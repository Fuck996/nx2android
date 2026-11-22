"""Validate the native overlay's translations independently of an Android device."""
from pathlib import Path
import json
import re
import shutil
import struct
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
DM = ROOT / 'nxnative/dm'
CATALOG = DM / 'android/overlay_i18n.h'
PACK = DM / 'third_party/fusion-pixel-font/fusion-pixel-12px-proportional-zh_tw.nxpf'


class AndroidOverlayI18n(unittest.TestCase):
    def test_catalog_keeps_format_arguments_and_has_every_glyph(self):
        source = CATALOG.read_text(encoding='utf-8')
        pairs = [(json.loads(en), json.loads(zh)) for en, zh in re.findall(r'\{("(?:[^"\\]|\\.)*"), ("(?:[^"\\]|\\.)*")\},', source)]
        self.assertGreater(len(pairs), 75)
        self.assertEqual([a for a, b in pairs], sorted(set(a for a, b in pairs)))
        pack = PACK.read_bytes()
        self.assertEqual(pack[:4], b'NXPF')
        count, = struct.unpack_from('<I', pack, 4)
        codepoints = {struct.unpack_from('<I', pack, 8 + i * 12)[0] >> 8 for i in range(count)}
        for en, zh in pairs:
            with self.subTest(english=en):
                spec = r'%(?:ll|l)?(?:\.\d+)?[dfs]'
                self.assertEqual(re.findall(spec, en), re.findall(spec, zh))
                self.assertFalse(set(map(ord, zh)) - codepoints)

    def test_locale_and_lookup_in_c(self):
        cc = shutil.which('cc') or shutil.which('clang')
        if not cc:
            self.skipTest('a C compiler is needed')
        with tempfile.TemporaryDirectory() as t:
            source, exe = Path(t) / 'test.c', Path(t) / 'test'
            source.write_text(r"""
#include <assert.h>
#include <stdio.h>
#include "overlay_i18n.h"
int dm_overlay_zh(void) { return 1; }
int main(void) {
    assert(ov_locale_zh("zh-Hans", "en-US", "en"));
    assert(!ov_locale_zh("en", "zh-Hans", "zh"));
    assert(ov_locale_zh("", "en-US", "zh"));
    assert(ov_locale_zh(NULL, "zh-Hans", "en"));
    assert(!ov_locale_zh(NULL, "ja", "en"));
    assert(!strcmp(ov_translate("Show gamepad", 0), "Show gamepad"));
    assert(!strcmp(ov_tr("Show gamepad"), "\xe6\x98\xbe\xe7\xa4\xba\xe8\x99\x9a\xe6\x8b\x9f\xe6\x89\x8b\xe6\x9f\x84"));
    assert(!strcmp(ov_tr("Unknown upstream text"), "Unknown upstream text"));
    assert(!ov_tr(NULL));
    return 0;
}
""", encoding='utf-8')
            subprocess.run([cc, '-std=c11', '-Wall', '-Werror', f'-I{DM / "android"}', str(source), '-o', str(exe)], check=True)
            subprocess.run([str(exe)], check=True)


if __name__ == '__main__':
    unittest.main()
