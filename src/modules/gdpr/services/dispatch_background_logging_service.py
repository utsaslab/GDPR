import logging

def dispatch_background_logging_service(logpath='/tmp/gdpr.log'):
    logging.basicConfig(
        format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p %z',
        filename=logpath,
        filemode='w',
        level=logging.DEBUG
    )
