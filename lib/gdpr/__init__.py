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
from .dpa.germany import Germany
from .dpa.greece import Greece
from .dpa.hungary import Hungary
from .dpa.ireland import Ireland
from .dpa.italy import Italy
from .dpa.latvia import Latvia
from .dpa.lithuania import Lithuania
from .dpa.luxembourg import Luxembourg
from .dpa.malta import Malta
from .dpa.netherlands import Netherlands
from .dpa.poland import Poland
from .dpa.portugal import Portugal
from .dpa.romania import Romania
from .dpa.slovakia import Slovakia
from .dpa.slovenia import Slovenia
from .dpa.spain import Spain
from .dpa.sweden import Sweden
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
    GERMANY        = 'DE'
    GREECE         = 'GR'
    HUNGARY        = 'HU'
    IRELAND        = 'IE'
    ITALY          = 'IT'
    LATVIA         = 'LV'
    LITHUANIA      = 'LT'
    LUXEMBOURG     = 'LU'
    MALTA          = 'MT'
    NETHERLANDS    = 'NL'
    POLAND         = 'PO'
    PORTUGAL       = 'PT'
    ROMANIA        = 'RO'
    SLOVAKIA       = 'SK'
    SLOVENIA       = 'SL'
    SPAIN          = 'ES'
    SWEDEN         = 'SE'
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
        elif iso_code == GDPR.EU_MEMBER.LATVIA:
            return Latvia()
        elif iso_code == GDPR.EU_MEMBER.LITHUANIA:
            return Lithuania()
        elif iso_code == GDPR.EU_MEMBER.LUXEMBOURG:
            return Luxembourg()
        elif iso_code == GDPR.EU_MEMBER.MALTA:
            return Malta()
        elif iso_code == GDPR.EU_MEMBER.NETHERLANDS:
            return Netherlands()
        elif iso_code == GDPR.EU_MEMBER.POLAND:
            return Poland()
        elif iso_code == GDPR.EU_MEMBER.PORTUGAL:
            return Portugal()
        elif iso_code == GDPR.EU_MEMBER.ROMANIA:
            return Romania()
        elif iso_code == GDPR.EU_MEMBER.SLOVAKIA:
            return Slovakia()
        elif iso_code == GDPR.EU_MEMBER.SLOVENIA:
            return Slovenia()
        elif iso_code == GDPR.EU_MEMBER.SPAIN:
            return Spain()
        elif iso_code == GDPR.EU_MEMBER.SWEDEN:
            return Sweden()
        elif iso_code == GDPR.EU_MEMBER.GERMANY:
            return Germany()
        elif iso_code == GDPR.EU_MEMBER.UNITED_KINGDOM:
            return UnitedKingdom()
