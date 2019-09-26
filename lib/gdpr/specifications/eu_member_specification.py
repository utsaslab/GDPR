import json

def is_satisfied_by(cand): # cand = iso_code
    with open('./gdpr/assets/eu-members.json', 'r') as f:
        eu_members = json.load(f)
    eu_member_codes = eu_members.keys()
    cand = cand.upper()
    return cand in eu_member_codes
