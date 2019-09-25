from .dpa.gb import GB
from .dpa.at import AT

class GDPR(object): # acts as a mediator pattern
    def get_dpa(self, country_code):
        country_code = country_code.upper()
        if country_code == 'GB':
            return GB()
        elif country_code == 'AT':
            return AT()
