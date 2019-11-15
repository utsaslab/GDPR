# possibly make use of future document_file_structure_policy.
class DocumentLanguagesService():
    def __init__(self, files):
        self.files = files
    def get(self):
        return set([name.split('.')[0] for name in self.files])
