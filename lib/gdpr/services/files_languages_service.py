# possibly make use of future document_file_structure_policy.
class FilesLanguagesService():
    def __init__(self, files):
        self.files = files
    def get_languages(self):
        return set([language.split('.')[0] for language in self.files])
