"""Installer regressions, including the Windows unpack rename failure without Windows."""
import hashlib
import io
from pathlib import Path
import tempfile
import unittest
from unittest import mock
import zipfile

from porter import fetch, toolchain


class ToolInstall(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.arc = self.root / 'tool.zip'
        for key, value in [('player_tools', lambda: self.root), ('WINDOWS', True)]:
            patcher = mock.patch.object(fetch, key, value)
            patcher.start()
            self.addCleanup(patcher.stop)
        self.it = fetch.Item('Android NDK', '27.2.12479018', 'https://dl.google.com/tool.zip',
                             0, '', 'sha512', 'ndk', '')

    def archive(self, *paths):
        with zipfile.ZipFile(self.arc, 'w') as z:
            for path in paths:
                z.writestr(path, 'Verified archive contents')

    def test_normal_promotion(self):
        self.archive('android-ndk-r27c/source.properties')
        dst = fetch._install(self.it, self.arc)
        self.assertEqual(dst, self.root / 'ndk')
        self.assertTrue((dst / 'source.properties').is_file())
        self.assertEqual(list(self.root.glob('.ndk-*')), [])

    def test_rename_denied_keeps_completed_tree(self):
        self.archive('android-ndk-r27c/source.properties')
        with mock.patch.object(Path, 'rename', side_effect=PermissionError(13, 'access denied')):
            dst = fetch._install(self.it, self.arc)
        self.assertNotEqual(dst, self.root / 'ndk')
        self.assertTrue((dst / 'source.properties').is_file())
        self.assertFalse((self.root / 'ndk').exists())

    def test_dotnet_flat_zip_survives_rename_denied(self):
        self.it.folder = 'dotnet'
        self.archive('dotnet.exe', 'sdk/10.0.404/dotnet.dll')
        with mock.patch.object(Path, 'rename', side_effect=PermissionError(13, 'access denied')):
            dst = fetch._install(self.it, self.arc)
        self.assertTrue((dst / 'dotnet.exe').is_file())
        self.assertTrue((dst / 'sdk/10.0.404/dotnet.dll').is_file())

    def test_preserves_existing_destination(self):
        existing = self.root / 'ndk'
        existing.mkdir()
        (existing / 'keep').write_text('previous install')
        self.archive('android-ndk-r27c/source.properties')
        with mock.patch.object(Path, 'rename') as rename:
            dst = fetch._install(self.it, self.arc)
        rename.assert_not_called()
        self.assertEqual((existing / 'keep').read_text(), 'previous install')
        self.assertTrue((dst / 'source.properties').is_file())

    def test_bad_archive_not_adopted(self):
        self.arc.write_bytes(b'invalid zip')
        with self.assertRaises(zipfile.BadZipFile):
            fetch._install(self.it, self.arc)
        self.assertEqual(list(self.root.glob('.ndk-*')), [])
        self.assertFalse((self.root / 'ndk').exists())

    def test_download_hash_mismatch_never_publishes(self):
        response = io.BytesIO(b'not matching')
        response.headers = {}
        self.it.hash = hashlib.sha512(b'official payload').hexdigest()
        with mock.patch.object(fetch.urllib.request, 'urlopen', return_value=response):
            with self.assertRaisesRegex(fetch.BuildError, 'sha512'):
                fetch._download(self.it, self.arc)
        self.assertFalse(self.arc.exists())
        self.assertFalse(self.arc.with_suffix('.zip.part').exists())

    def test_resolver_accepts_portable_ndk_dotnet_adb(self):
        ndk = self.root / 'android-ndk-r27c'
        ndk.mkdir()
        (ndk / 'source.properties').write_text(f'Pkg.Revision = {toolchain.NDK_REVISION}')
        dn = self.root / 'dotnet' / f'dotnet{toolchain.EXE}'
        adb = self.root / 'platform-tools' / f'adb{toolchain.EXE}'
        for path in dn, adb:
            path.parent.mkdir()
            path.touch()
        with mock.patch.object(toolchain, 'PORTABLE_TOOLS', self.root), \
             mock.patch.object(toolchain, 'player_tools', return_value=self.root / 'user'), \
             mock.patch.object(toolchain, '_sdk_roots', return_value=[]), \
             mock.patch.object(toolchain.shutil, 'which', return_value=None), \
             mock.patch.object(toolchain, 'dotnet_sdks', side_effect=lambda x: {'10.0.404': ''} if x == dn else {}), \
             mock.patch.dict(toolchain.os.environ, {}, clear=True):
            self.assertEqual(toolchain.find_ndk({}), (ndk, toolchain.NDK_REVISION))
            self.assertEqual(toolchain.find_dotnet({}), dn)
            self.assertEqual(toolchain.find_adb({}), adb)


if __name__ == '__main__':
    unittest.main()
