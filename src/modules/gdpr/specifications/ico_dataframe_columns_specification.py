def is_satisfied_by(cand): # cand = dataframe
    required_columns = [
        'Data Controller',
        'Ref',
        'Sector ',
        'Nature',
        'Date of Final Notice',
        'DPA fine ',
        'PECR fine ',
        'Notes'
    ]
    return set(required_columns).issubset(cand.columns) is True
