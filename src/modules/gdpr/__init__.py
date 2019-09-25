from .dpa.gb import GB
from .dpa.at import AT

class GDPR(object): # acts as a mediator pattern
    def get_dpa(self, iso_code):
        iso_code = iso_code.upper()
        if iso_code == 'GB':
            return GB()
        elif iso_code == 'AT':
            return AT()
