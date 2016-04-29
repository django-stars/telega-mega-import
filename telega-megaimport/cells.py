class CellBase(object):
    def __init__(self, title, required=True):
        self.title = title
        self.required = required


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


class CellString(CellBase):
    def __init__(self, *args, **kwargs):
        self.strip = True if 'strip' in kwargs and kwargs['strip'] else False
        super(CellString, self).__init__(*args, **kwargs)

    def normalize(self, value):
        return value.strip() if self.strip and value else value

    def validate(self, value):
        error = super(CellString, self).validate(value) or []
        if self.required is False and value is None:
            return None
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
        value = value.lower() if value else value
        if value in self.true_values:
            return True
        elif value in self.false_values:
            return False
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
        if self.required is False and value is None:
            return None
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
        if self.required is False and value is None:
            return None
        try:
            float(value)
        except TypeError:
            error += ['Not convertable to float']
        if error:
            return error
        else:
            return None
