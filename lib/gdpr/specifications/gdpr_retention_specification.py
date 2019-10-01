import datetime
from ..policies import gdpr_policy

def is_satisfied_by(cand): #cand = date : Datetime
    today = datetime.date.today()
    margin = today - gdpr_policy.implementation_date() # timedelta
    return today - margin <= cand <= today + margin
