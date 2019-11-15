class DocumentRootSpecification():
    def __init__(self, dpa):
        self.dpa = dpa
    def is_satisfied_by(self, root):
        split = root.split('/')
        return (split.index(self.dpa.country.lower()) < len(split) - 1)
