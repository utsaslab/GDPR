# Source: https://stackoverflow.com/questions/34503540/why-does-python-give-oserror-errno-36-file-name-too-long-for-filename-short
MAX_FILENAME_LENGTH = 255

def is_allowed(filename):
    return len(filename) <= MAX_FILENAME_LENGTH
