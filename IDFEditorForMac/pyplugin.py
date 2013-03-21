import os.path


class PyIdfFileIO:

    def readEplusObjectsFromFile_(self, path: str) -> list:
        if not os.path.exists(path):
            return []

        with open(path, 'r') as f:
            idf = f.read()
        return [idf.split(',')]

    def writeEplusObjects_toFile_(self, objs:list, path:str):
        with open(path, 'w') as f:
            if len(objs) == 0:
                f.write('')
            else:
                f.write(','.join(objs[0]))
