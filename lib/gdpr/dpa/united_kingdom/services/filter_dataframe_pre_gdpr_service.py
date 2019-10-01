def filter_dataframe_pre_gdpr_service(df, gdpr_implementation_date):
    gdpr_implementation_str = gdpr_implementation_date.strftime("%m/%d/%Y")
    _df = df[(df['Date of Final Notice'] >= gdpr_implementation_str)]
    return _df
