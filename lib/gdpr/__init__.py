from .dpa.austria import Austria
from .dpa.belgium import Belgium
from .dpa.bulgaria import Bulgaria
from .dpa.croatia import Crotia
from .dpa.cyprus import Cyprus
from .dpa.czech_republic import CzechRepublic
from .dpa.denmark import Denmark
from .dpa.estonia import Estonia
from .dpa.finland import Finland
from .dpa.france import France
from .dpa.greece import Greece
from .dpa.hungary import Hungary
from .dpa.ireland import Ireland
from .dpa.italy import Italy
from .dpa.united_kingdom import UnitedKingdom

class EUMember(object):
    AUSTRIA        = 'AT'
    BELGIUM        = 'BE'
    BULGARIA       = 'BG'
    CROATIA        = 'HR'
    CYPRUS         = 'CY'
    CZECH_REPUBLIC = 'CZ'
    DENMARK        = 'DK'
    ESTONIA        = 'EE'
    FINLAND        = 'FI'
    FRANCE         = 'FR'
    GREECE         = 'GR'
    HUNGARY        = 'HU'
    IRELAND        = 'IE'
    ITALY          = 'IT'
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
        elif iso_code == GDPR.EU_MEMBER.ESTONIA:
            return Estonia()
        elif iso_code == GDPR.EU_MEMBER.FINLAND:
            return Finland()
        elif iso_code == GDPR.EU_MEMBER.FRANCE:
            return France()
        elif iso_code == GDPR.EU_MEMBER.GREECE:
            return Greece()
        elif iso_code == GDPR.EU_MEMBER.HUNGARY:
            return Hungary()
        elif iso_code == GDPR.EU_MEMBER.IRELAND:
            return Ireland()
        elif iso_code == GDPR.EU_MEMBER.ITALY:
            return Italy()
        elif iso_code == GDPR.EU_MEMBER.UNITED_KINGDOM:
            return UnitedKingdom()
