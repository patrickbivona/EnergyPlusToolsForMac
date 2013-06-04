import pyparsing as pp


class IdfParser(object):

    def __init__(self, class_definitions):
        self.defs = class_definitions
        self.comma = pp.Suppress(pp.Literal(','))
        self.semicolon = pp.Suppress(pp.Literal(';'))
        self.classname = pp.Word(pp.alphanums).setName('classname')
        self.field_comment = pp.Suppress(pp.Literal('!-') + pp.restOfLine.setName('fieldcomment') + pp.LineEnd())
        self.field = pp.Word(pp.alphanums + '. ').setName('field')
        self.obj = self.classname + self.comma + \
            pp.ZeroOrMore(self.field + self.comma + pp.Optional(self.field_comment)) + \
            self.field + self.semicolon + pp.Optional(self.field_comment)
        self.obj.setDebug()
        self.objs = pp.ZeroOrMore(pp.Group(self.obj))

        self.errors = []

    def parse(self, idf):
        """Returns a list of parsed objects"""
        result = []
        self.errors = []
        try:
            objects = self.objs.parseString(idf).asList()
            for o in objects:
                if self.defs.supports_object(o):
                    result.append(o)
                else:
                    self.errors.append('Found unsupported object: ' + ','.join(o) + ';')
            return result
        except pp.ParseException as e:
            print(e)
            return []

    def errors(self):
        self.errors

    def parse_file(self, filename):
        """Returns a list of objects parsed from the given file"""
        with open(filename, 'r') as f:
            return self.parse(f.read())

    def write_file(self, objects, filename):
        with open(filename, 'w') as f:
            for obj in objects:
                f.write(','.join(obj) + ';\n')


class ClassDefinitions(object):

    def __init__(self, defs={}):
        self.class_defs = defs

    def add_class_def(self, class_def):
        self.class_defs[class_def.name] = class_def

    def class_names(self):
        return self.class_defs.keys()

    def class_def(self, class_name):
        return self.class_defs[class_name]

    def supports_object(self, object):
        if object is None or len(object) < 1:
            return False
        else:
            return object[0] in self.class_defs


class ClassDefinition(object):

    def __init__(self, name, fields=[]):
        self.name = name
        self.fields = fields

    def __repr__(self):
        repr = self.name + ", "
        for field in self.fields:
            repr += field.__repr__()
        return repr

    def add_field(self, field):
        self.fields.append(field)

    def validate_object(self, eplus_obj):
        """Returns None if object is valid, error message otherwise"""
        if eplus_obj[0] != self.name:
            return "Class name does not match definition:", self.name
        if len(eplus_obj) - 1 != len(self.fields):
            return "Incorrect number of fields for class: %i, expected %i" % (len(eplus_obj) - 1, len(self.fields))
        for (field_value, field_definition) in zip(eplus_obj[1:], self.fields):
            if not field_definition.accepts(field_value):
                return "Invalid value %s for field %s" % (field_value, field_definition.id)
        return None

    def field_names(self):
        return [field.attributes['field'] for field in self.fields]

    def field_count(self):
        return len(self.fields)


class FieldDefinition(object):
    def __init__(self, id, attributes):
        self.id = id
        self.attributes = attributes

    def __repr__(self):
        repr = " field %s { " % self.id
        for (attr_key, attr_value) in self.attributes.items():
            repr += "%s:%s " % (attr_key, attr_value)
        repr += "}"
        return repr

    def accepts(self, field_value):
        field_type = self.attributes.get('type')
        if field_type is None:
            return False
        elif field_type == 'integer':
            try:
                int(field_value)
                return True
            except ValueError:
                return False
        elif field_type == 'alpha':
            return True
        else:
            return False


comma = pp.Suppress(pp.Literal(','))
semicolon = pp.Suppress(pp.Literal(';'))
backslash = pp.Suppress('\\')

class_name = pp.Word(pp.alphanums)
field_id = pp.Combine(pp.oneOf('A N') + pp.Word(pp.nums))
field_name = backslash + pp.Literal('field') + pp.Word(pp.alphanums)
field_type = backslash + pp.Literal('type') + pp.Word(pp.alphanums)
field_attribute = pp.Group(field_name | field_type)

field_definition = pp.Group(field_id.setResultsName("id") +
                            (comma | semicolon) +
                            pp.Group(pp.Dict((pp.ZeroOrMore(field_attribute)))))
classs = class_name.setResultsName("class_name") + comma + pp.OneOrMore(field_definition).setResultsName("fields")
classes = pp.ZeroOrMore(pp.Group(classs))


class DataDictionaryParser(object):
    def __init__(self):
        pass

    def parse(self, idd_string):
        raw_defs = classes.parseString(idd_string)
        class_defs = {}
        for raw_def in raw_defs:
            class_def = self._make_definition(raw_def)
            if class_def:
                class_defs[class_def.name] = class_def
        return class_defs

    def parse_file(self, idd_file_path):
        with open(idd_file_path, 'r') as idd:
            return self.parse(idd.read())

    def _make_definition(self, raw_def):
        class_def = ClassDefinition(raw_def.class_name, [])
        for raw_field in raw_def.fields:
            class_def.add_field(FieldDefinition(raw_field.id, raw_field[1]))
        return class_def
