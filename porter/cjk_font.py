"""Fork-supplied fallback for game text, separate from the Android overlay font."""
from pathlib import Path
import sys

from porter.paths import REPO

BUNDLE_DIR = Path("resources/game-fonts")
SOURCE_DIR = Path("build/game-fonts")
FONT_NAME = "NX2A-CJK-SC-Regular.ttf"
LICENSE_NAME = "NotoSansSC-OFL.txt"
SIMPLIFIED = frozenset(("zh-hans", "zh-cn"))
FW_TITLE = "0100000000000814"
FW_NAMES = ("nintendo_udsg-r_org_zh-cn_003.bfttf", "nintendo_udsg-r_ext_zh-cn_003.bfttf")


def choose_shared_font(explicit, game_language, sysdata, bundle=None):
    """Return (font, license notice) if a shared-font override should be packed."""
    if explicit is not None:
        return explicit, None
    if not needs_chinese_fallback(game_language, sysdata):
        return None, None
    root = Path(bundle) if bundle is not None else REPO / (BUNDLE_DIR if getattr(sys, "frozen", False) else SOURCE_DIR)
    font, license_notice = root / FONT_NAME, root / LICENSE_NAME
    if font.is_file() and license_notice.is_file():
        return font, license_notice
    return None, None


def needs_chinese_fallback(game_language, sysdata):
    """Would the matching firmware font be unavailable without an override?"""
    # An override takes precedence over *all* firmware faces in the host.
    # If the player supplied a matching Chinese face, leave it to the host.
    return game_language.lower() in SIMPLIFIED and not (
        sysdata is not None and any((Path(sysdata) / FW_TITLE / name).is_file() for name in FW_NAMES)
    )
