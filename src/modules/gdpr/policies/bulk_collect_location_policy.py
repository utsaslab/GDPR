import os

PROJECT_NAME = 'GDPR'
VALID_LOCATION = PROJECT_NAME + '/src/data'
DELIMITER = os.sep

def is_allowed(location):
    root_path = os.path.dirname(os.path.abspath(location))
    paths = root_path.split(DELIMITER)

    project_index = paths.index(PROJECT_NAME)
    project_path = DELIMITER.join(paths[project_index:])

    return project_path == VALID_LOCATION
