import os.path
import eplus


accepted_classes = {
    'Version': eplus.ClassDefinition('Version', [
        eplus.FieldDefinition('A1', {'type': 'alpha'})]),
    'ScheduleTypeLimits': eplus.ClassDefinition('ScheduleTypeLimits', [
        eplus.FieldDefinition('A1', {'type': 'alpha'}),
        eplus.FieldDefinition('N1', {'type': 'integer'}),
        eplus.FieldDefinition('N2', {'type': 'integer'}),
        eplus.FieldDefinition('A2', {'type': 'alpha'}),
        eplus.FieldDefinition('A3', {'type': 'alpha'})])
}


class PyIdfFileIO:

    def readEplusObjectsFromFile_(self, path: str) -> list:
        if not os.path.exists(path):
            return []

        parser = eplus.IdfParser()
        (objs, errors) = parser.parse_file(path, accepted_classes)
        if len(errors) > 0:
            print(errors)
        return objs

    def writeEplusObjects_toFile_(self, objs:list, path:str):
        parser = eplus.IdfParser()
        parser.write_file(objs, path)
