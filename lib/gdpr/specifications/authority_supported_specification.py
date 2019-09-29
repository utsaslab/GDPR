import json

def is_satisfied_by(cand):
    with open('./gdpr/assets/dba-info.json', 'r') as f:
        authorities = json.load(f)

    authority_codes = authorities.keys()
    cand = cand.upper()

    return cand in authority_codes
