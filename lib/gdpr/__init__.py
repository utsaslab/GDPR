from enum import Enum
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

class EUMember(enum):
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
    def get_dpa(self, country_code):
        country_code = country_code.upper()
        if country_code == EUMember.AUSTRIA.value:
            return Austria()
        elif country_code == EUMember.BELGIUM.value:
                return Belgium()
        elif country_code == EUMember.BULGARIA.value:
                return Bulgaria()
        elif country_code == EUMember.CROATIA.value:
                return Croatia()
        elif country_code == EUMember.CYPRUS.value:
                return Cyprus()
        elif country_code == EUMember.CZECH_REPUBLIC.value:
                return CzechRepublic()
        elif country_code == EUMember.DENMARK.value:
                return Denmark()
        elif country_code == EUMember.ESTONIA.value:
                return Estonia()
        elif country_code == EUMember.FINLAND.value:
                return Finland()
        elif country_code == EUMember.FRANCE.value:
                return France()
        elif country_code == EUMember.GREECE.value:
                return Greece()
        elif country_code == EUMember.HUNGARY.value:
                return Hungary()
        elif country_code == EUMember.IRELAND.value:
                return Ireland()
        elif country_code == EUMember.ITALY.value:
                return Italy()
        elif country_code == EUMember.LATVIA.value:
                return Latvia()
        elif country_code == EUMember.LITHUANIA.value:
                return Lithuania()
        elif country_code == EUMember.LUXEMBOURG.value:
                return Luxembourg()
        elif country_code == EUMember.MALTA.value:
                return Malta()
        elif country_code == EUMember.NETHERLANDS.value:
                return Netherlands()
        elif country_code == EUMember.POLAND.value:
                return Poland()
        elif country_code == EUMember.PORTUGAL.value:
                return Portugal()
        elif country_code == EUMember.ROMANIA.value:
                return Romania()
        elif country_code == EUMember.SLOVAKIA.value:
                return Slovakia()
        elif country_code == EUMember.SLOVENIA.value:
                return Slovenia()
        elif country_code == EUMember.SPAIN.value:
                return Spain()
        elif country_code == EUMember.SWEDEN.value:
                return Sweden()
        elif country_code == EUMember.GERMANY.value:
                return Germany()
        elif country_code == EUMember.UNITED_KINGDOM.value:
            return UnitedKingdom()
