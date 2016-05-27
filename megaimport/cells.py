from django.core.exceptions import ObjectDoesNotExist


class CellBase(object):
    # Counter is added for ordering of field-declaration
    creation_counter = 0

    def __init__(self, required=True, default=None):
        # Hack, is used for sorting in parser-creator
        if default and required:
            raise ValueError('Default value and required value can\'t be combined!')
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


class EmptyCell(CellBase):
    def normalize(self, value):
        return None

    def validate(self, value):
        return None


class CellString(CellBase):
    def __init__(self, *args, **kwargs):
        self.strip = True if 'strip' in kwargs and kwargs['strip'] else False
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
    def normalize(self, value):
        try:
            return int(value)
        except TypeError:
            return value

    def validate(self, value):
        error = super(CellInteger, self).validate(value) or []
        try:
            int(value)
        except TypeError:
            error += ['Not convertable to integer']
        if error:
            return error
        else:
            return None


class CellFloat(CellBase):
    def normalize(self, value):
        try:
            return float(value)
        except TypeError:
            return value

    def validate(self, value):
        error = super(CellFloat, self).validate(value) or []
        try:
            float(value)
        except TypeError:
            error += ['Not convertable to float']
        if error:
            return error
        else:
            return None


class CellModel(CellBase):
    def __init__(self, queryset=None, lookup_arg='pk', *args, **kwargs):
        self.queryset = queryset
        self.lookup_arg = lookup_arg
        super(CellModel, self).__init__(*args, **kwargs)

    def normalizer(self, value):
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
