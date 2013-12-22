import pyparsing as pp
import copy


class ClassDefinitions(object):

    def __init__(self, defs={}):
        self.class_defs = copy.deepcopy(defs)

    def add_class_def(self, class_def):
        self.class_defs[class_def.name] = class_def

    def class_names(self):
        return self.class_defs.keys()

    def class_def(self, class_name):
        try:
            return self.class_defs[class_name]
        except KeyError:
            return None

    def __getitem__(self, key):
        return self.class_def(key)

    def __len__(self):
        return len(self.class_defs)

    def supports_object(self, object):
        if object is None or len(object) < 1:
            return False
        else:
            return object[0] in self.class_defs


class NoddingClassDefinitions(object):

    def supports_object(self, object):
        return True


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


class DataDictionaryParser(object):

    def __init__(self):
        self.comma = pp.Suppress(pp.Literal(','))
        self.semicolon = pp.Suppress(pp.Literal(';'))
        self.backslash = pp.Suppress('\\')

        self.field_id = pp.Combine(pp.oneOf('A N') + pp.Word(pp.nums))

        self.field_attribute_key = pp.Word(pp.alphas, pp.alphas + '-')
        self.field_attribute = pp.Group(pp.Suppress(self.backslash) + self.field_attribute_key + \
                                    pp.Word(pp.printables))
        self.field_definition = pp.Group(self.field_id.setResultsName("id") +
                                    (self.comma | self.semicolon) +
                                    pp.Group(pp.Dict((pp.ZeroOrMore(self.field_attribute)))))
        self.field_level_attributes = pp.Group(pp.Dict((pp.ZeroOrMore(self.field_attribute))))

        self.class_attribute_memo = self.backslash + pp.Literal('memo') + pp.OneOrMore(pp.Word(pp.printables))
        self.class_attributes = self.class_attribute_memo + ~pp.FollowedBy(self.field_definition)

        self.class_name = pp.Word(pp.alphanums).setResultsName("class_name")
        self.classs = self.class_name + self.comma + \
                        pp.ZeroOrMore(self.class_attributes) + \
                        pp.OneOrMore(self.field_definition).setResultsName("fields")
        self.classes = pp.ZeroOrMore(pp.Group(self.classs))
        self.classs.setDebug()

    def parse(self, idd_string):
        try:
            raw_defs = self.classes.parseString(idd_string)
            class_defs = ClassDefinitions()
            for raw_def in raw_defs:
                class_def = self._make_definition(raw_def)
                if class_def:
                    class_defs.add_class_def(class_def)
            return class_defs
        except pp.ParseException as e:
            print(e)
            return ClassDefinition

    def parse_file(self, idd_file_path):
        with open(idd_file_path, 'r') as idd:
            return self.parse(idd.read())

    def _make_definition(self, raw_def):
        class_def = ClassDefinition(raw_def.class_name, [])
        for raw_field in raw_def.fields:
            class_def.add_field(FieldDefinition(raw_field.id, raw_field[1]))
        return class_def


class InlineIdfFormatter(object):

    def format(self, idf_obj):
        return ','.join(idf_obj) + ';\n'


class PrettyIdfFormatter(object):

    def __init__(self, print_comments=True, indentation=4):
        self.indent = ' ' * indentation

    def format(self, idf_obj):
        result = ''
        for index, field in enumerate(idf_obj):
            if index == 0:
                result += field + ',\n'
            elif index == len(idf_obj)-1:
                result += self.indent + field + ';\n\n'
            else:
                result += self.indent + field + ',\n'
        return result


class IdfParser(object):

    def __init__(self, class_definitions=NoddingClassDefinitions()):
        self.defs = class_definitions
        self.comma = pp.Suppress(pp.Literal(','))
        self.semicolon = pp.Suppress(pp.Literal(';'))
        self.classname = pp.Word(pp.alphas, pp.alphas + ':')
        self.field_comment = pp.Suppress(pp.Literal('!-') + pp.restOfLine.setName('fieldcomment') + pp.LineEnd())
        self.field = (pp.Word(pp.printables + ' ', excludeChars=',;') | pp.Empty().setParseAction(pp.replaceWith(''))).setName('field')
        self.obj = self.classname + self.comma + \
            pp.ZeroOrMore(self.field + self.comma + pp.Optional(self.field_comment)) + \
            self.field + self.semicolon + pp.Optional(self.field_comment)
        # self.obj.setDebug()
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

    def parse_file(self, filename):
        """Returns a list of objects parsed from the given file"""
        with open(filename, 'r') as f:
            return self.parse(f.read())

    def write_file(self, objects, filename, formatter=PrettyIdfFormatter()):
        with open(filename, 'w') as f:
            for obj in objects:
                f.write(formatter.format(obj))
