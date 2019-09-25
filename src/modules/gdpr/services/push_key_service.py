import random
from ..specifications import eu_member_specification

def push_key_service(model, date, iso_code):
    if hasattr(model, '__tablename__') is False: # turn into specification
        raise ValueError("model has invalid __tablename__")

    if eu_member_specification.is_satisfied_by(iso_code) is False:
        raise ValueError("country code does not belong to a valid eu country member.")

    return "{model}{date}:{rand}+{iso_code}".format(
        model=model.__tablename__[0:2].upper(),
        date=date.strftime("%y%m%d"),
        rand=str(random.randint(0, 99)).zfill(2), # prop. of collision?
        iso_code=iso_code.upper()
    )
