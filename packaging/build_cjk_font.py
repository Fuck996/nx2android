"""Create the static Simplified Chinese game-text fallback for the Windows ZIP."""
import argparse
import hashlib
import io
from pathlib import Path
import sys
import tempfile
from urllib.request import urlopen

from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

# A directly executed packaging script starts with packaging/ on sys.path.
if not __package__:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from porter.cjk_font import FONT_NAME, LICENSE_NAME

UPSTREAM = "https://raw.githubusercontent.com/notofonts/noto-cjk/Sans2.004/"
FONT = ("Sans/Variable/TTF/Subset/NotoSansSC-VF.ttf",
        "d68bafcb48a2707749396aa12bbbd833cb70401f3a9a689fd2902c7e0d295964")
OFL = ("LICENSE", "6a73f9541c2de74158c0e7cf6b0a58ef774f5a780bf191f2d7ec9cc53efe2bf2")


def verified_download(entry):
    source, expected = entry
    with urlopen(UPSTREAM + source, timeout=60) as response:
        data = response.read(24 * 1024 * 1024 + 1)
    if len(data) > 24 * 1024 * 1024 or hashlib.sha256(data).hexdigest() != expected:
        raise ValueError(f"Incorrect SHA-256 for Noto font source: {source}")
    return data


def static_ttf(original, target):
    # The source declares Adobe's reserved name 'Source'; name the derived
    # font separately and preserve the original copyright and OFL records.
    names = {
        1: "NX2A CJK SC", 2: "Regular", 3: "NX2ACJKSC-Regular-2.004",
        4: "NX2A CJK SC Regular", 6: "NX2ACJKSC-Regular",
        16: "NX2A CJK SC", 17: "Regular", 18: "NX2A CJK SC Regular",
        20: "NX2ACJKSC-Regular", 21: "NX2A CJK SC", 22: "Regular",
        25: "NX2ACJKSC",
    }
    with TTFont(io.BytesIO(original), recalcTimestamp=False) as font:
        instantiateVariableFont(font, {"wght": 400}, inplace=True, updateFontNames=True)
        for name in font["name"].names:
            if name.nameID in names:
                name.string = names[name.nameID]
        cmap = font.getBestCmap()
        if "fvar" in font or "glyf" not in font or not all(ord(c) in cmap for c in "简体中文三国志AZaz0123，。！？"):
            raise ValueError("Expected static TrueType with Latin, Chinese, and punctuation coverage")
        font.save(target)
        return font["name"].getDebugName(0)


def build_cjk_font(destination):
    font_data = verified_download(FONT)
    ofl = verified_download(OFL)
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    # Work beside the destination to let replace keep every staged file atomic.
    with tempfile.TemporaryDirectory(prefix=".cjk-", dir=destination) as stage:
        tmp = Path(stage)
        copyright_notice = static_ttf(font_data, tmp / FONT_NAME)
        if not copyright_notice:
            raise ValueError("The source font did not declare its copyright notice")
        (tmp / LICENSE_NAME).write_bytes(copyright_notice.encode("utf-8") + b"\n\n" + ofl)
        (tmp / LICENSE_NAME).replace(destination / LICENSE_NAME)
        (tmp / FONT_NAME).replace(destination / FONT_NAME)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    build_cjk_font(parser.parse_args().destination)
