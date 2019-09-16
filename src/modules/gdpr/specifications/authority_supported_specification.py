import json

def is_satisfied_by(cand):
    with open('./modules/gdpr/assets/supported_authorities.json', 'r') as f:
        authorities = json.load(f)

    authority_codes = authorities.keys()
    cand = cand.upper()

    return cand in authority_codes
