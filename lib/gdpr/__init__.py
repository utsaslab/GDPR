from .dpa.gb import GB
from .dpa.at import AT
from .dpa.dk import DK
from .dpa.be import BE
from .dpa.bg import BG

class GDPR(object): # acts as a mediator pattern
    def get_dpa(self, iso_code):
        iso_code = iso_code.upper()
        if iso_code == 'GB':
            return GB()
        elif iso_code == 'AT':
            return AT()
        elif iso_code == 'DK':
            return DK()
        elif iso_code == 'BE':
            return BE()
        elif iso_code == 'BG':
            return BG()
