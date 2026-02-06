class ComponentList:
    def __init__(self, identifier: str, display: str, languages: list = None):
        self.identifier = identifier
        self.display = display
        self.languages = languages


class LanguagePackMetadata:
    def __init__(
        self,
        locale: str,
        locale_display: str,
        locale_english: str,
        last_update: int = None,
        author: str = None,
    ):
        self.locale = locale
        self.locale_display = locale_display
        self.locale_english = locale_english
        self.last_update = last_update
        self.author = author
