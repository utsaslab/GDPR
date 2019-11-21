class ExistsFileLanguageSpec():
    def __init__(self, file_languages):
        self.file_languages = file_languages
    def is_satisfied_by(self, file_language):
        return (file_language not in file_languages)
