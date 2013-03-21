import os.path


class PyIdfFileIO:

    def readEplusObjectsFromFile_(self, path: str) -> list:
        if not os.path.exists(path):
            return []

        with open(path, 'r') as f:
            idf = f.read()
        return [idf.split(',')]
