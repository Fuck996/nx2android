"""Translate desktop presentation only; keep the porter protocol unchanged."""

import os
import re

from gui.locale_zh_cn import ZH_CN

_LANGUAGE = 'en'


def configure_ui_language(system_locale, override=None):
    """Select at startup; UI locale is independent of the ported game's language."""
    global _LANGUAGE
    if override is None:
        override = os.environ.get('NX2A_UI_LANGUAGE', '')
    preference = override.strip().lower().replace('_', '-')
    locale = system_locale.lower().replace('_', '-')
    if preference in {'en', 'en-us', 'en-gb'}:
        _LANGUAGE = 'en'
    elif preference in {'zh', 'zh-cn', 'zh-hans'} or locale in {'zh', 'zh-cn', 'zh-sg', 'zh-hans', 'zh-hans-cn', 'zh-hans-sg'}:
        _LANGUAGE = 'zh-CN'
    else:
        _LANGUAGE = 'en'
    return _LANGUAGE


def tr(source, /, **values):
    text = ZH_CN.get(source, source) if _LANGUAGE == 'zh-CN' else source
    return text.format(**values) if values else text


# Porter stages, steps and doctor details coming from the subprocess. Localize
# known prose at display time, not structured fields, names, paths or raw logs.
_EVENT_PATTERNS = (
    (r'extract (.+)', '提取 {0}'),
    (r'linking (.+)', '链接 {0}'),
    (r'installing (.+)', '正在安装 {0}'),
    (r'pushing the RomFS into (.+)', '正在将 RomFS 推送至 {0}'),
    (r'comparing the content of (.+) with the pack\'s RomFS', '正在比较 {0} 的内容与数据包的 RomFS'),
    (r'comparing (.+) with the pack\'s RomFS', '正在比较 {0} 与数据包的 RomFS'),
    (r'removing ([\d,]+) files from (.+) that are not the pack\'s', '正在从 {1} 移除 {0} 个不属于数据包的文件'),
    (r'removing ([\d,]+) stale files', '正在移除 {0} 个旧文件'),
    (r'copying the (.+) on the device from (.+) \((.+)\)', '正在设备上从 {1} 复制 {0}（{2}）'),
    (r'translating ([\d,]+) shaders', '正在转换 {0} 个着色器'),
    (r'compressing ([\d,]+) shaders', '正在压缩 {0} 个着色器'),
    (r'([\d,]+) shaders decoded on the device', '已在设备上解码 {0} 个着色器'),
    (r'([\d,]+) shaders in (.+) s', '在 {1} 秒内处理了 {0} 个着色器'),
    (r'([\d,]+) files, (.+) GB', '{0} 个文件，共 {1} GB'),
    (r'(.+), reused \(inputs unchanged\)', '{0}，已复用（输入未变化）'),
    (r'(.+): the shader code archives \(round (\d+)\)', '{0}：着色器代码归档（第 {1} 轮）'),
    (r"(.+): ([\d,]+) Oodle streams with the game's decoder on the device \(round (\d+)\)", '{0}：使用设备端游戏解码器处理 {1} 个 Oodle 流（第 {2} 轮）'),
    (r"(.+): ([\d,]+) shaders with the game's decoder on the device", '{0}：使用设备端游戏解码器处理 {1} 个着色器'),
    (r"the game's Oodle decoder on the device: ([\d,]+) entries, (.+) GB", '设备端游戏 Oodle 解码：{0} 项，共 {1} GB'),
    (r'no game profile for ([0-9A-F]+): this game is not supported yet \(an experimental port surveys it and guesses a profile; it may not start\)', '没有 {0} 的游戏配置，暂不支持此游戏。实验模式可尝试自动推断配置，但游戏可能无法启动。'),
    (r'(.+) has a game profile \(iOS\) but is not ported to Android yet \(an experimental port tries it with that profile\)', '{0} 有 iOS 配置，但还未适配 Android。实验模式可用现有配置尝试移植。'),
    (r'(.+) is a work in progress: it plays, but parts of it are missing \(its page, (.+), says which\)', '{0} 尚在适配中，能玩但部分功能缺失，详见 {1}。'),
    (r"(.+) is not a version the profile was brought up on \((.+)\): it is packed from a derived profile, without that version's fixes", '{0} 未经过此游戏配置测试（已适配：{1}）。会用派生配置打包，不含该版本专用修复。'),
    (r'(.+) at (.+): the host is built with (.+); others are untested', '{1} 中的 {0}：运行环境以 {2} 构建，其他版本未经测试'),
    (r'a port takes about twice its game files on the game folder\'s drive \(NEO: 7 GB\); keep (\d+) GB free', '移植约需要游戏文件两倍的磁盘空间（例如 NEO：7 GB），请为游戏文件所在磁盘保留 {0} GB 可用空间'),
    (r'no SDK \((.+)\)', '{0} 中未找到 SDK'),
    (r'missing: (.+)', '缺少：{0}'),
    (r'no such file: (.+)', '文件不存在：{0}'),
    (r'(.+) GB free on (.+)', '{1} 可用空间 {0} GB'),
    (r'Download missing tools, or install NDK (.+) \(developer\.android\.com/ndk/downloads\) and set its folder', '请下载缺失工具，或从 developer.android.com/ndk/downloads 安装 NDK {0} 并指定文件夹'),
    (r'Download missing tools, or install the \.NET SDK (.+) \(dotnet.microsoft.com\)', '请下载缺失工具，或从 dotnet.microsoft.com 安装 .NET SDK {0}'),
    (r'install NDK (.+)', '安装 NDK {0}'),
)


def event_text(source):
    if _LANGUAGE != 'zh-CN':
        return source
    if source in ZH_CN:
        return ZH_CN[source]
    for pattern, translated in _EVENT_PATTERNS:
        if match := re.fullmatch(pattern, source):
            return translated.format(*match.groups())
    return source
