from ..models import Penalty
from ..services.push_key_service import push_key_service

def create(iso_code, data_controller, sector, nature, date, fine, currency, notes):
    id = push_key_service(Penalty, date, iso_code)
    penalty = Penalty(
        id=id,
        data_controller=data_controller,
        sector=sector,
        nature=nature,
        date=date,
        fine=fine,
        currency=currency,
        notes=notes
    )
    return penalty
