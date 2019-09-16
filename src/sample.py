from modules.gdpr import Authority

def main():
    authority = Authority('GB')
    penalties = authority.get_penalties()
    print(penalties)

if __name__ == '__main__':
    main()
