"""The Windows Oodle workaround streams real subprocess stdout, without adb or a device."""
from pathlib import Path
import shlex
import sys
import tempfile
import unittest
from unittest import mock

from porter import adb


PAYLOAD = b'DMOR\x00\r\n\x1a\x80\xff'
REMOTE = "/data/local/tmp/who's there/job.bin.out"
# Fake adb runner. Deliberately uses binary stdout including the DOS EOF byte.
BODY = '''
import sys, time
mode, verb, arg = sys.argv[1:4]
if verb == "shell":
    print(0 if mode == "empty" else 10)
elif verb == "exec-out":
    data = bytes.fromhex("444d4f52000d0a1a80ff")
    if mode == "timeout": time.sleep(20)
    sys.stdout.buffer.write(data[:4] if mode == "truncated" else data)
    if mode == "failure":
        print("transport lost", file=sys.stderr)
        sys.exit(7)
'''


class FakeAdb(adb.Adb):
    def __init__(self, mode):
        super().__init__(sys.executable, serial='fixture')
        self.mode, self.calls = mode, []

    def cmd(self, verb, *args):
        self.calls.append((verb, *args))
        return [self.exe, '-c', BODY, self.mode, str(verb), *(str(a) for a in args)]


class WindowsOodlePull(unittest.TestCase):
    def setUp(self):
        t = tempfile.TemporaryDirectory()
        self.addCleanup(t.cleanup)
        self.parent = Path(t.name) / '中文 + ポケモン'
        self.parent.mkdir()
        self.dest = self.parent / 'job.out'

    def pull(self, mode, timeout=4):
        fake = FakeAdb(mode)
        with mock.patch.object(adb.sys, 'platform', 'win32'):
            fake.pull_oodle_result(REMOTE, self.dest, timeout)
        self.assertEqual(fake.calls, [
            ('shell', f'stat -c %s -- {shlex.quote(REMOTE)}'),
            ('exec-out', f'cat -- {shlex.quote(REMOTE)}'),
        ])
        # The Windows pathname is never passed to adb.
        self.assertFalse(any(str(self.dest) in str(call) for call in fake.calls))
        self.assertEqual(list(self.parent.glob('*.part')), [])

    def test_binary_output_matches(self):
        self.dest.write_bytes(b'old')
        self.pull('success')
        self.assertEqual(self.dest.read_bytes(), PAYLOAD)

    def test_failures_preserve_existing_and_remove_temp(self):
        for mode, error in [('truncated', 'expected 10 bytes, received 4'),
                            ('failure', 'transport lost'), ('empty', 'invalid remote file size'),
                            ('timeout', 'timed out')]:
            with self.subTest(mode=mode):
                self.dest.write_bytes(b'keep')
                with self.assertRaisesRegex(adb.AdbError, error):
                    self.pull(mode, timeout=1)
                self.assertEqual(self.dest.read_bytes(), b'keep')
                self.assertEqual(list(self.parent.glob('*.part')), [])

    def test_ordinary_paths_use_pull(self):
        fake = FakeAdb('unused')
        with mock.patch.object(adb.sys, 'platform', 'win32'), mock.patch.object(fake, 'run') as run:
            fake.pull_oodle_result(REMOTE, Path('plain') / 'job.out')
            run.assert_called_once_with('pull', REMOTE, str(Path('plain') / 'job.out'), timeout=1800)
        # On non-Windows, even Unicode uses the original command.
        with mock.patch.object(adb.sys, 'platform', 'linux'), mock.patch.object(fake, 'run') as run:
            fake.pull_oodle_result(REMOTE, self.dest)
            run.assert_called_once_with('pull', REMOTE, str(self.dest), timeout=1800)

    def test_finalize_denied_keeps_existing_and_removes_temp(self):
        self.dest.write_bytes(b'preserved')
        with mock.patch.object(adb.os, 'replace', side_effect=PermissionError(13, 'locked')):
            with self.assertRaisesRegex(adb.AdbError, 'cannot write'):
                self.pull('success')
        self.assertEqual(self.dest.read_bytes(), b'preserved')
        self.assertEqual(list(self.parent.glob('*.part')), [])

    def test_temporary_file_stays_next_to_destination(self):
        fake = FakeAdb('success')
        temp = adb.tempfile.NamedTemporaryFile
        with mock.patch.object(adb.sys, 'platform', 'win32'), \
             mock.patch.object(adb.tempfile, 'NamedTemporaryFile', wraps=temp) as stage:
            fake.pull_oodle_result(REMOTE, self.dest)
        self.assertEqual(Path(stage.call_args.kwargs['dir']), self.parent.resolve())


if __name__ == '__main__':
    unittest.main()
