// Simplified Chinese strings for the Android overlay. Only translate at display sites;
// protocol keys, raw logs, and game-provided strings remain unchanged.
#ifndef NX2A_OVERLAY_I18N_H
#define NX2A_OVERLAY_I18N_H
#include <stddef.h>
#include <string.h>

int dm_overlay_zh(void);

static inline int ov_lang_is_zh(const char *s) {
    return s && (!strcmp(s, "zh") || !strcmp(s, "zh-Hans") || !strcmp(s, "zh-CN") || !strcmp(s, "zh-SG"));
}

// The explicit UI override wins; otherwise honor Android's Chinese locale or a Simplified Chinese game.
static inline int ov_locale_zh(const char *override, const char *game, const char *system) {
    return override && *override ? ov_lang_is_zh(override) : ov_lang_is_zh(game) || ov_lang_is_zh(system);
}

static inline const char *ov_translate(const char *text, int chinese) {
    if (!text || !chinese) return text;
    static const struct { const char *en, *zh; } translations[] = {
        {"%ld file%s, %.1f MB", "%ld 个文件%s，%.1f MB"},
        {"%ld file%s, %lld KB", "%ld 个文件%s，%lld KB"},
        {"%s: drag, pinch, - +", "%s：拖动移动，双指或 - / + 缩放"},
        {"%s: hidden, Show", "%s：已隐藏，可显示"},
        {"(a console's, as its save tools copy it) in", "（可用主机存档工具导出的文件夹）放入"},
        {"A key  B delete  Y shift  + OK  - cancel", "A 输入  B 删除  Y 切换大小写  + 确定  - 取消"},
        {"Audio output", "音频输出"},
        {"BAT row", "电池温度"},
        {"Back", "返回"},
        {"Bottom left", "左下角"},
        {"Bottom right", "右下角"},
        {"Box", "背景框"},
        {"Cancel", "取消"},
        {"Colour", "颜色"},
        {"Counter", "计数器"},
        {"Cyan", "青色"},
        {"D-pad", "方向键"},
        {"Del", "删除"},
        {"Discard", "放弃"},
        {"Discard your changes?", "放弃本次修改？"},
        {"Docked", "底座"},
        {"Drag to move, pinch to resize", "拖动移动，双指缩放"},
        {"Driver row", "显卡驱动"},
        {"Edit", "编辑"},
        {"Edit layout", "编辑布局"},
        {"Enter text", "输入文字"},
        {"Export", "导出"},
        {"Export save", "导出存档"},
        {"Exporting...", "正在导出…"},
        {"Extra large", "特大"},
        {"FPS row", "帧率"},
        {"Face buttons", "正面按键"},
        {"Failed", "失败"},
        {"Game", "游戏"},
        {"Gamepad", "手柄"},
        {"Graph row", "帧率曲线"},
        {"Green", "绿色"},
        {"Handheld", "掌机"},
        {"Hide", "隐藏"},
        {"Import", "导入"},
        {"Import a save", "选择要导入的存档"},
        {"Import and close", "导入并关闭"},
        {"Import save", "导入存档"},
        {"Import this save?", "导入这个存档？"},
        {"Importing the save", "正在导入存档"},
        {"Keep editing", "继续编辑"},
        {"Label", "字母"},
        {"Large", "大"},
        {"Left stick", "左摇杆"},
        {"Magenta", "品红色"},
        {"Medium", "中"},
        {"Menu button", "菜单键"},
        {"Minus", "减号"},
        {"Mode", "运行模式"},
        {"No save yet", "暂无存档"},
        {"No saves yet. Export one, or put a save folder", "暂无存档。请先导出，或将存档文件夹"},
        {"None", "无"},
        {"Normal", "标准"},
        {"OFF", "关"},
        {"OK", "确定"},
        {"ON", "开"},
        {"Opacity", "不透明度"},
        {"Outline", "描边"},
        {"Plus", "加号"},
        {"Position", "位置"},
        {"Reset", "重置"},
        {"Resume", "继续游戏"},
        {"Right stick", "右摇杆"},
        {"Rumble", "振动"},
        {"SOC row", "芯片温度"},
        {"Save", "保存"},
        {"Select", "选择"},
        {"Shift", "切换"},
        {"Show", "显示"},
        {"Show FPS", "显示帧率"},
        {"Show gamepad", "显示虚拟手柄"},
        {"Size", "大小"},
        {"Small", "小"},
        {"Snap to grid: Off", "网格吸附：关"},
        {"Snap to grid: On", "网格吸附：开"},
        {"Space", "空格"},
        {"Style", "样式"},
        {"The game closes now. Open it again:", "游戏即将关闭。重新打开后，"},
        {"Thick", "粗"},
        {"Thin", "细"},
        {"Top left", "左上角"},
        {"Top right", "右上角"},
        {"White", "白色"},
        {"Yellow", "黄色"},
        {"Your current save is exported first,", "当前存档会先导出备份，"},
        {"page %d of %d", "第 %d / %d 页"},
        {"the save is imported as it starts.", "存档会在启动时导入。"},
        {"then the game closes: open it again.", "然后关闭游戏，请重新打开。"},
    };
    size_t lo = 0, hi = sizeof translations / sizeof translations[0];
    while (lo < hi) {
        size_t mid = lo + (hi - lo) / 2;
        int cmp = strcmp(text, translations[mid].en);
        if (!cmp) return translations[mid].zh;
        if (cmp < 0) hi = mid; else lo = mid + 1;
    }
    return text;
}
static inline const char *ov_tr(const char *text) { return ov_translate(text, dm_overlay_zh()); }
#endif
