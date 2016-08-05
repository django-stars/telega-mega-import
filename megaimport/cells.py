from django.core.exceptions import ObjectDoesNotExist


class CellBase(object):
    """
    Base class for inheritance for Cell creation

    Don't forget to override kls.normalize(value) and
    kls.validate(value) if required
    """
    # Counter is added for ordering of field-declaration
    creation_counter = 0

    def __init__(self, required=True, default=None):
        if default and required:
            raise ValueError('Default value and required value can\'t be combined!')
        # Hack, is used for sorting in parser-creator
        self.creation_order = CellBase.creation_counter
        CellBase.creation_counter += 1
        self.title = None
        self.required = required
        self.default = default

    def __repr__(self):
        return "<{}: {}{}>".format(
            self.__class__.__name__,
            self.title,
            [" ","*"][int(self.required)],
        )

    def normalize(self, value):
        return value

    def validate(self, value):
        # Return None if all is OK,
        # Return list of strings with error description in other case.
        if self.required and value is None:
            return ['Empty value']
        return None


class CellEmpty(CellBase):
    """
    CellEmpty: use it for declaration of empty columns in yor file
    """
    def normalize(self, value):
        return None

    def validate(self, value):
        return None


class CellString(CellBase):
    """
    Use for parsing string values; converts parse results to
    string.
    """
    def __init__(self, strip=False, *args, **kwargs):
        self.strip = strip
        super(CellString, self).__init__(*args, **kwargs)

    def normalize(self, value):
        return value.strip() if self.strip and value else value

    def validate(self, value):
        error = super(CellString, self).validate(value) or []
        if not isinstance(value, basestring):
            error += ['Not convertable to string value']
        if error:
            return error
        else:
            return None


class CellBoolean(CellBase):
    """
    Use for parsing boolean values;
    True = 'yes', 'y', '+', '1', 'true'
    False = 'no', 'n', '-', '0', 'false'
    Returns boolean value.
    """
    true_values = ['yes', 'y', '+', '1', 'true']
    false_values = ['no', 'n', '-', '0', 'false']

    def normalize(self, value):
        value = value.lower() if not isinstance(value, bool) else value
        if value in self.true_values:
            return True
        elif value in self.false_values:
            return False

    def validate(self, value):
        error = super(CellBoolean, self).validate(value) or []
        value = value.lower() if not isinstance(value, bool) else value
        if value not in self.true_values + self.false_values:
            error += ['Value cannot be parsed as boolean']
        if error:
            return error
        else:
            return None


class CellInteger(CellBase):
    """
    Use for parsing integer values;
    Retunrns integer
    """

    def normalize(self, value):
        try:
            return int(value)
        except ValueError:
            return value

    def validate(self, value):
        error = super(CellInteger, self).validate(value) or []
        try:
            int(value)
        except ValueError:
            error += ['Not convertable to integer']
        if error:
            return error
        else:
            return None


class CellFloat(CellBase):
    """
    Use for parsing float values;
    Retunrns float
    """

    def normalize(self, value):
        try:
            return float(value)
        except ValueError:
            return value

    def validate(self, value):
        error = super(CellFloat, self).validate(value) or []
        try:
            float(value)
        except ValueError:
            error += ['Not convertable to float']
        if error:
            return error
        else:
            return None


class CellModel(CellBase):
    """
    Use for parsing direct model association. Always set queryset;
    default lookup argument - primary key.
    Returns model instance.
    """
    def __init__(self, queryset=None, lookup_arg='pk', *args, **kwargs):
        self.queryset = queryset
        if queryset is None:
            raise ValueError('Queryset is required!')
        self.lookup_arg = lookup_arg
        super(CellModel, self).__init__(*args, **kwargs)

    def normalize(self, value):
        try:
            return self.queryset.get(**{self.lookup_arg: value})
        except ObjectDoesNotExist:
            return value

    def validate(self, value):
        error = super(CellModel, self).validate(value) or []
        try:
            return self.queryset.get(**{self.lookup_arg: value})
        except ObjectDoesNotExist:
            error += ['Object not found']
        if error:
            return error
        else:
            return None
