import os


def path_to_datafile(filename):
    return os.path.join(os.path.dirname(__file__), 'data', filename)
