from .authorities.gb import GB

class GDPR(object): # acts as a mediator pattern
    def get_authority(self, country_code):
        country_code = country_code.upper()
        if country_code == 'GB':
            return GB()
