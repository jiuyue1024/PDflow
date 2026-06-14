"""
TranslationManager — 印流PDflow i18n 管理器

职责：
1. 管理当前语言设置（zh_CN / zh_TW / en_US）
2. 维护已注册页面的列表，在语言切换时调用 retranslateUi()
3. 提供 translate() 快捷函数供页面使用
"""

from translations.translations import translate as _tr

LOCALE_NAMES = {
    "zh_CN": "简体中文",
    "zh_TW": "繁體中文",
    "en_US": "English",
}

_current_locale = "zh_CN"


def set_locale(locale: str):
    """设置当前语言"""
    global _current_locale
    _current_locale = locale


def get_locale() -> str:
    """获取当前语言"""
    return _current_locale


def _(text: str) -> str:
    """快捷翻译函数，在页面代码中使用：_("文本")"""
    return _tr(_current_locale, text)


class TranslationManager:
    """管理语言切换和页面重译"""

    def __init__(self):
        self._registered_pages = []

    def register_page(self, page_instance, has_ui=True):
        """注册一个页面，以便在语言切换时重译

        Args:
            page_instance: 页面实例
            has_ui: 是否为 Ui_XXXPage 模式（有 .ui 属性）
                    True  → 调用 page_instance.ui.retranslateUi(page_instance)
                    False → 调用 page_instance.retranslateUi()
        """
        self._registered_pages.append((page_instance, has_ui))

    def switch_language(self, locale_code: str) -> bool:
        """切换语言

        Args:
            locale_code: 语言代码 (zh_CN / zh_TW / en_US)

        Returns:
            bool: 是否成功切换
        """
        set_locale(locale_code)
        self._retranslate_all()
        print(f"[i18n] 已切换至: {locale_code}")
        return True

    def _retranslate_all(self):
        """对所有已注册的页面调用 retranslateUi"""
        for page_instance, has_ui in self._registered_pages:
            try:
                if has_ui and hasattr(page_instance, "ui"):
                    page_instance.ui.retranslateUi(page_instance)
                elif hasattr(page_instance, "retranslateUi"):
                    page_instance.retranslateUi()
            except Exception as e:
                print(f"[i18n] retranslateUi 失败 ({type(page_instance).__name__}): {e}")
