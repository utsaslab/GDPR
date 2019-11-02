import platform

def path_for_platform():
    system = platform.system()
    supported = ['Darwin', 'Linux', 'Windows']
    if system not in supported:
        raise ValueError('No chromedriver is supported for this platform system %s' % system)
    return "./gdpr/assets/chromedriver/%s" % system.lower()
