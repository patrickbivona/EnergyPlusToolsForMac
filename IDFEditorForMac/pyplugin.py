import os.path
import eplus


class PyIdfFileIO:

    def readEplusObjectsFromFile_(self, path: str) -> list:
        if not os.path.exists(path):
            return []

        parser = eplus.IdfParser()
        accepted_classes = {
            'Class1': eplus.ClassDefinition('Class1', [
                eplus.FieldDefinition('A1', {'type': 'alpha'}),
                eplus.FieldDefinition('A2', {'type': 'alpha'})])
        }
        (objs, errors) = parser.parse_file(path, accepted_classes)
        return objs

    def writeEplusObjects_toFile_(self, objs:list, path:str):
        parser = IdfParser()
        parser.write_file(objs, path)
