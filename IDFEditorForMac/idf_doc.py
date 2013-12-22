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


class IdfDocument:

    def __init__(self):
        self.objs = []

    def readFromFile(self, path):
        if not os.path.exists(path):
            return []
        parser = eplus.IdfParser(class_defs)
        self.objs = parser.parse_file(path)

    def writeToFile(self, path):
        parser = eplus.IdfParser(class_defs)
        parser.write_file(self.objs, path, eplus.InlineIdfFormatter())

    def objects(self):
        return self.objs

    def allClassesWithObjectCount(self):
        result = {}
        for clazz in class_defs.class_names():
            result[clazz] = 0
        for (clazz, count) in self.onlyClassesWithObjectsWithObjectCount().items():
            result[clazz] = count
        return result

    def onlyClassesWithObjectsWithObjectCount(self):
        result = {}
        for obj in self.objs:
            class_name = obj[0]
            tmp_count = result.get(class_name, 0)
            tmp_count += 1
            result[class_name] = tmp_count
        return result

    def objectsOfClass(self, className):
        return [obj for obj in self.objs if obj[0] == className]

    def fieldsOfClass(self, className):
        class_def = class_defs.class_def(className)
        if class_def is None:
            return []
        else:
            return class_def.field_names()

    def addEmptyObject(self, className):
        class_def = class_defs.class_def(className)
        new_obj = [className] + [''] * class_def.field_count()
        self.objs.append(new_obj)

    def objectOfClassAtIndex(self, className, index):
        objs = self.objectsOfClass(className)
        if index < len(objs):
            return objs[index]
        else:
            return []

    def replaceObjectAtIndexWithObject(self, index, obj):
        old_obj = self.objectOfClassAtIndex(obj[0], index)
        i = self.objs.index(old_obj)
        self.objs[i] = obj

    def deleteObjectOfClassAtIndex(self, className, index):
        class_objs = self.objectsOfClass(className)
        if index >= len(class_objs):
            return
        class_obj = class_objs[index]
        all_objs_index = self.objs.index(class_obj)
        self.objs.pop(all_objs_index)
