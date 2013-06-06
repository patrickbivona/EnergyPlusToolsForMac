import os.path
import eplus


class_defs = eplus.ClassDefinitions({
    'Version': eplus.ClassDefinition('Version', [
        eplus.FieldDefinition('A1', {'field': 'Version Identifier', 'type': 'alpha'})]),
    'ScheduleTypeLimits': eplus.ClassDefinition('ScheduleTypeLimits', [
        eplus.FieldDefinition('A1', {'field': 'Name', 'type': 'alpha'}),
        eplus.FieldDefinition('N1', {'field': 'Lower Limit Value', 'type': 'integer'}),
        eplus.FieldDefinition('N2', {'field': 'Upper Limit Value', 'type': 'integer'}),
        eplus.FieldDefinition('A2', {'field': 'Numeric Type', 'type': 'alpha'}),
        eplus.FieldDefinition('A3', {'field': 'Unit Type', 'type': 'alpha'})]),
    'Timestep': eplus.ClassDefinition('Timestep', [
        eplus.FieldDefinition('N1', {'field': 'Number of Timesteps per Hour', 'type': 'integer'})])
})


class PyIdfDocument:

    def __init__(self):
        self.objs = []

    def readFromFile_(self, path: str):
        if not os.path.exists(path):
            return []
        parser = eplus.IdfParser(class_defs)
        self.objs = parser.parse_file(path)

    def writeToFile_(self, path: str):
        parser = eplus.IdfParser(class_defs)
        parser.write_file(self.objs, path)

    def objects(self) -> list:
        return self.objs

    def allClassesWithObjectCount(self) -> dict:
        result = {}
        for clazz in class_defs.class_names():
            result[clazz] = 0
        for (clazz, count) in self.onlyClassesWithObjectsWithObjectCount().items():
            result[clazz] = count
        return result

    def onlyClassesWithObjectsWithObjectCount(self) -> dict:
        result = {}
        for obj in self.objs:
            class_name = obj[0]
            tmp_count = result.get(class_name, 0)
            tmp_count += 1
            result[class_name] = tmp_count
        return result

    def objectsOfClass_(self, className:str) -> list:
        return [obj for obj in self.objs if obj[0] == className]

    def fieldsOfClass_(self, className:str) -> list:
        class_def = class_defs.class_def(className)
        return class_def.field_names()

    def addEmptyObject_(self, className:str):
        class_def = class_defs.class_def(className)
        new_obj = [className] + [''] * class_def.field_count()
        self.objs.append(new_obj)

    def objectOfClass_atIndex_(self, className:str, index:int) -> list:
        objs = self.objectsOfClass_(className)
        if index < len(objs):
            return objs[index]
        else:
            return []

    def replaceObjectAtIndex_withObject_(self, index:int, obj:list):
        old_obj = self.objectOfClass_atIndex_(obj[0], index)
        i = self.objs.index(old_obj)
        self.objs[i] = obj

    def deleteObjectOfClass_atIndex_(self, className:str, index:int):
        class_objs = self.objectsOfClass_(className)
        if index >= len(class_objs):
            return
        class_obj = class_objs[index]
        all_objs_index = self.objs.index(class_obj)
        self.objs.pop(all_objs_index)
