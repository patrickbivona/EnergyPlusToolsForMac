import pyparsing as pp


class IdfParser(object):

    def parse(self, idf, allowed_classes):
        """Returns a 2-tuple with the list of parsed objects and the list of parsing errors"""

        text_objects = idf.split(';')
        objects = []
        errors = []
        for text_object in text_objects:
            if text_object.strip():
                (obj, err) = self._parse_object(text_object, allowed_classes)
                if obj is not None:
                    objects.append(obj)
                if err is not None:
                    errors.append(err)
        return (objects, errors)

    def _parse_object(self, obj, known_classes):
        """Returns a 2-tuple with the parsed object (or None) and a parsing error (or None)"""

        items = obj.strip(' ;').split(',')

        class_name = items[0].strip(' \n')
        if not class_name:
            return (None, None)

        known_class = known_classes.get(class_name)
        if known_class is None:
            return (None, "Missing definition for object of class " + class_name)

        obj = [k.strip(' \n') for k in items]
        valid = known_class.validate_object(obj)
        if valid is None:
            return (obj, None)
        else:
            return (None, valid)

    def parse_file(self, filename, allowed_classes):
        """Returns a 2-tuple with the list of parsed objects and the list of parsing errors"""

        f = open(filename, 'r')
        content = f.read()
        f.close()
        return self.parse(content, allowed_classes)

    def write_file(self, objects, filename):
        with open(filename, 'w') as f:
            for obj in objects:
                f.write(', '.join(obj) + '\n')


class ClassDefinition(object):

    def __init__(self, name=None, fields=[]):
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


class FieldDefinition(object):
    def __init__(self, id, attributes):
        self.id = id
        self.attributes = attributes

    def __repr__(self):
        repr = "field %s{ " % self.id
        for (attr_key, attr_value) in self.attributes.iteritems():
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

class_name = pp.Word(pp.alphas)
field_id = pp.Combine(pp.Literal('A') + pp.Word(pp.nums))
field_name = backslash + pp.Literal('field') + pp.Word(pp.alphanums)
field_type = backslash + pp.Literal('type') + pp.Word(pp.alphanums)
field_attribute = pp.Group(field_name | field_type)

field_definition = pp.Group(field_id.setResultsName("id") + \
                            (comma | semicolon) + \
                            pp.Group(pp.Dict((pp.ZeroOrMore(field_attribute)))))
classs = class_name.setResultsName("class_name") + comma + pp.OneOrMore(field_definition).setResultsName("fields")


class DataDictionaryParser(object):
    def __init__(self):
        pass

    def parse(self, idd_file_path):

        class_defs = {}

        with open(idd_file_path, 'r') as idd:
            idd_object_buffer = ""
            try:
                for line in idd:
                    idd_object_buffer += line
                    if ';' in line:
                        class_defs.update(self._parse_definition(idd_object_buffer))
            except StopIteration:
                class_defs.update(self._parse_definition(idd_object_buffer))
        return class_defs

    def _parse_definition(self, raw_def):
        parsed_class = classs.parseString(raw_def)
        class_def = ClassDefinition(parsed_class.class_name, [])
        for raw_field in parsed_class.fields:
            class_def.add_field(FieldDefinition(raw_field.id, raw_field[1]))
        print class_def
        return {class_def.name: class_def}
