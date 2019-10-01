from .dpa.austria import Austria
from .dpa.belgium import Belgium
from .dpa.bulgaria import Bulgaria
from .dpa.croatia import Crotia
from .dpa.cyprus import Cyprus
from .dpa.czech_republic import CzechRepublic

from .dpa.denmark import Denmark
from .dpa.united_kingdom import UnitedKingdom

class EUMember(object):
    AUSTRIA        = 'AT'
    BELGIUM        = 'BE'
    BULGARIA       = 'BG'
    CROATIA        = 'HR'
    CYPRUS         = 'CY'
    CZECH_REPUBLIC = 'CZ'
    DENMARK        = 'DK'
    UNITED_KINGDOM = 'GB'

class GDPR(object): # acts as a mediator/facade pattern :: find su:ku slides.
    EU_MEMBER = EUMember()

    def get_dpa(self, iso_code):
        iso_code = iso_code.upper()
        if iso_code == GDPR.EU_MEMBER.AUSTRIA:
            return Austria()
        elif iso_code == GDPR.EU_MEMBER.BELGIUM:
            return Belgium()
        elif iso_code == GDPR.EU_MEMBER.BULGARIA:
            return Bulgaria()
        elif iso_code == GDPR.EU_MEMBER.CROATIA:
            return Croatia()
        elif iso_code == GDPR.EU_MEMBER.CYPRUS:
            return Cyprus()
        elif iso_code == GDPR.EU_MEMBER.CZECH_REPUBLIC:
            return CzechRepublic()
        elif iso_code == GDPR.EU_MEMBER.DENMARK:
            return Denmark()
        elif iso_code == GDPR.EU_MEMBER.UNITED_KINGDOM:
            return UnitedKingdom()
