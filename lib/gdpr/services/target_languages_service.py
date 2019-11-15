class TargetLanguagesService():
    def __init__(self, dpa):
        self.dpa = dpa
    def filter_target_languages(self, target_languages):
        target_languages = [lang.lower() for lang in target_languages]
        # target_languages = [lang for lang in target_languages if lang != self.language_code]
        return target_languages
