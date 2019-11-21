class DocumentRootSpec():
    def __init__(self, doc):
        self.doc = doc
    def is_satisfied_by(self, root):
        split = root.split('/')
        doc_index = split.index(doc) if doc in split else -1
        last_index = len(split) - 1
        return (doc_index == last_index)
