"""Desktop localization keeps port commands, paths and diagnostics unchanged."""
import ast
import os
import string
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from gui.i18n import configure_ui_language, event_text, tr
from gui.locale_zh_cn import ZH_CN

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
try:
    from gui import app
except ImportError as err:
    if err.name != 'PySide6':
        raise
    app = None


class Catalog(unittest.TestCase):
    def tearDown(self):
        configure_ui_language('en', override='en')

    def test_language_choice_default_and_override(self):
        for locale, override, want in (
            ('zh_CN', '', 'zh-CN'), ('zh_Hans_CN', '', 'zh-CN'),
            ('zh_TW', '', 'en'), ('en_US', '', 'en'),
            ('zh_CN', 'en', 'en'), ('en_US', 'zh-Hans', 'zh-CN'),
        ):
            with self.subTest(locale=locale, override=override):
                self.assertEqual(configure_ui_language(locale, override), want)

    def test_formats_are_covered_and_preserve_dynamic_parts(self):
        fields = lambda text: {field for _, field, _, _ in string.Formatter().parse(text) if field}
        for filename in ('app.py', 'runner.py'):
            tree = ast.parse((ROOT / 'gui' / filename).read_text(encoding='utf-8'))
            for node in ast.walk(tree):
                if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                        and node.func.id == 'tr' and isinstance(node.args[0], ast.Constant)):
                    continue
                source = node.args[0].value
                with self.subTest(source=source):
                    self.assertIn(source, ZH_CN)
                    self.assertEqual(fields(source), fields(ZH_CN[source]))
                    self.assertEqual(fields(source), {kw.arg for kw in node.keywords})
        configure_ui_language('zh_CN', override='')
        self.assertEqual(tr('Imported {name}', name='save{1}.zip'), '已导入 save{1}.zip')

    def test_stage_translation_is_not_a_protocol_change(self):
        configure_ui_language('zh_CN', override='')
        self.assertEqual(event_text('build nx_extract'), '构建 nx_extract')
        self.assertEqual(event_text('installing game.apk'), '正在安装 game.apk')
        self.assertIn('2,000', event_text('translating 2,000 shaders'))
        self.assertEqual(event_text('D:\\a\\file.nsp'), 'D:\\a\\file.nsp')
        self.assertEqual(event_text('New upstream status'), 'New upstream status')
        configure_ui_language('zh_CN', override='en')
        self.assertEqual(event_text('build nx_extract'), 'build nx_extract')


@unittest.skipIf(app is None, 'PySide6 is needed for the GUI tests')
class DesktopWindow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt = app.QApplication.instance() or app.QApplication([])

    def test_pages_labels_and_progress(self):
        self.addCleanup(configure_ui_language, 'en', override='en')
        for locale, tabs, label in (
            ('zh_CN', ['移植', '配置', '支持列表', '存档'], '简体中文'),
            ('en_US', ['Port', 'Setup', 'Games', 'Saves'], 'Chinese (Simplified)'),
        ):
            configure_ui_language(locale, override='')
            with patch.object(app, 'call_json'), patch.object(app.config, 'load', return_value={}):
                window = app.Window()
            self.addCleanup(window.deleteLater)
            self.assertEqual([window.tabs.tabText(i) for i in range(window.tabs.count())], tabs)
            self.assertEqual(window.port.language.itemText(10), label)
            self.assertEqual(window.port.language.itemData(10), 'zh-Hans')
            window.port.on_event({'ev': 'stage', 'k': 1, 'n': 2, 'name': 'Vulkan shaders', 'step': 'checking the inputs'})
            self.assertIn('Vulkan 着色器' if locale == 'zh_CN' else 'Vulkan shaders', window.port.step.text())
            window.port.on_event({'ev': 'say', 'msg': 'Raw diagnostic: build nx_extract'})
            self.assertIn('Raw diagnostic: build nx_extract', window.port.log.toPlainText())
