from ..specifications import eu_member_specification

def push_key_service(model, date, country_code):
    if hasattr(model, '__tablename__') is False:
        raise ValueError("model has invalid __tablename__")

    if eu_member_specification.is_satisfied_by(country_code) is False:
        raise ValueError("country code does not belong to a valid eu country member.")

    return "{model_prefix}{date}:{rand}+{country_code}".format(
        model_prefix=model.__tablename__[0:2].upper(),
        date=date.strftime("%m%d%y"),
        rand='DC98',
        country_code=country_code.upper()
    )
