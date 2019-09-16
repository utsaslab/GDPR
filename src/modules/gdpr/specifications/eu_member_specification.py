import json

def is_satisfied_by(cand): # cand = country_code
    cand = cand.upper()
    with open('./modules/gdpr/assets/eu-members.json', 'r') as f:
        eu_members = json.load(f)
    eu_member_codes = eu_members.keys()
    return cand in eu_member_codes
