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


class PyIdfDocument:

    def __init__(self):
        self.objs = []

    def readFromFile_(self, path:str):
        if not os.path.exists(path):
            return []

        parser = eplus.IdfParser()
        (self.objs, errors) = parser.parse_file(path, accepted_classes)
        if len(errors) > 0:
            print(errors)

    def writeToFile_(self, path:str):
        parser = eplus.IdfParser()
        parser.write_file(self.objs, path)

    def objects(self) -> list:
        return self.objs

    def classesWithObjectCount(self) -> dict:
        result = {}
        for obj in self.objs:
            class_name = obj[0]
            tmp_count = result.get(class_name, 0)
            tmp_count += 1
            result[class_name] = tmp_count
        return result

    def objectsOfClass_(self, className:str) -> list:
        return [obj for obj in self.objs if obj[0] == className]
