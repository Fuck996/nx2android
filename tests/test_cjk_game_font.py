import importlib.util
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from porter import cjk_font

SCRIPT = Path(__file__).resolve().parent.parent / 'packaging' / 'build_cjk_font.py'
SPEC = importlib.util.spec_from_file_location('build_cjk_font', SCRIPT)
generator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(generator)


class ChineseGameFont(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.font = self.root / cjk_font.FONT_NAME
        self.notice = self.root / cjk_font.LICENSE_NAME

    def choose(self, explicit=None, language='zh-Hans', sysdata=None):
        return cjk_font.choose_shared_font(explicit, language, sysdata, self.root)

    def test_complete_bundle_is_auto_for_simplified_chinese_only(self):
        self.font.touch()
        self.assertEqual(self.choose(), (None, None))  # font without its notice is not distributable
        self.notice.touch()
        self.assertEqual(self.choose(), (self.font, self.notice))
        self.assertEqual(self.choose(language='zh-CN'), (self.font, self.notice))
        for language in ('en-US', 'ja', 'zh-Hant', 'zh-TW', 'ko'):
            self.assertEqual(self.choose(language=language), (None, None))

    def test_explicit_font_wins_and_effective_firmware_stays_preferred(self):
        self.font.touch()
        self.notice.touch()
        sysdata = self.root / 'sysdata'
        matching = sysdata / cjk_font.FW_TITLE / cjk_font.FW_NAMES[1]
        matching.parent.mkdir(parents=True)
        self.assertEqual(self.choose(sysdata=sysdata), (self.font, self.notice))
        matching.touch()
        self.assertEqual(self.choose(sysdata=sysdata), (None, None))
        custom = self.root / 'custom.ttf'
        self.assertEqual(self.choose(explicit=custom, sysdata=sysdata), (custom, None))

    def test_wrong_upstream_hash_is_rejected(self):
        with patch.object(generator, 'urlopen', return_value=io.BytesIO(b'bad')):
            with self.assertRaisesRegex(ValueError, 'Incorrect SHA-256'):
                generator.verified_download(generator.FONT)


if __name__ == '__main__':
    unittest.main()
