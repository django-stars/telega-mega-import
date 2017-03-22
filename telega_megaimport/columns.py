from dateutil import parser

from django.core.exceptions import ObjectDoesNotExist
from django.apps import apps


class BaseColumn(object):
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
        self.creation_order = BaseColumn.creation_counter
        BaseColumn.creation_counter += 1
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
        return value if value else None

    def validate(self, value):
        # Return None if all is OK,
        # Return list of strings with error description in other case.
        if self.required and value is None:
            return ['Empty value']
        return None


class EmptyColumn(BaseColumn):
    """
    EmptyColumn: use it for declaration of empty columns in yor file
    """
    def normalize(self, value):
        return None

    def validate(self, value):
        return None


class StringColumn(BaseColumn):
    """
    Use for parsing string values; converts parse results to
    string.
    """
    def __init__(self, strip=False, *args, **kwargs):
        self.strip = strip
        super(StringColumn, self).__init__(*args, **kwargs)

    def normalize(self, value):
        if self.strip and value:
            return value.strip()
        elif value:
            return value
        return None

    def validate(self, value):
        error = super(StringColumn, self).validate(value) or []
        if not isinstance(value, basestring):
            error += ['Not convertable to string value']
        if error:
            return error
        else:
            return None


class BooleanColumn(BaseColumn):
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
        error = super(BooleanColumn, self).validate(value) or []
        value = value.lower() if not isinstance(value, bool) else value
        if value not in self.true_values + self.false_values:
            error += ['Value cannot be parsed as boolean']
        if error:
            return error
        else:
            return None


class IntegerColumn(BaseColumn):
    """
    Use for parsing integer values;
    Retunrns integer
    """

    def normalize(self, value):
        try:
            return int(value)
        except ValueError:
            return None

    def validate(self, value):
        error = super(IntegerColumn, self).validate(value) or []
        try:
            int(value)
        except ValueError:
            error += ['Not convertable to integer']
        if error:
            return error
        else:
            return None


class FloatColumn(BaseColumn):
    """
    Use for parsing float values;
    Returns float
    """

    def normalize(self, value):
        try:
            return float(value)
        except ValueError:
            return None

    def validate(self, value):
        error = super(FloatColumn, self).validate(value) or []
        try:
            float(value)
        except ValueError:
            error += ['Not convertable to float']
        if error:
            return error
        else:
            return None


class ModelColumn(BaseColumn):
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
        super(ModelColumn, self).__init__(*args, **kwargs)

    def normalize(self, value):
        try:
            return self.queryset.get(**{self.lookup_arg: value})
        except ObjectDoesNotExist:
            return None

    def validate(self, value):
        error = super(ModelColumn, self).validate(value) or []
        try:
            self.queryset.get(**{self.lookup_arg: value})
        except ObjectDoesNotExist:
            error += ['Object not found']
        except ValueError:
            error += ['Invalid lookup']
        if error:
            return error
        else:
            return None


class DateTimeColumn(BaseColumn):
    """
        Used for parsing date time values;
    """

    def __init__(self, *args, **kwargs):
        self.parserinfo = kwargs.pop('parserinfo', None)
        self.ignoretz = kwargs.pop('ignoretz', False)
        self.tzinfos = kwargs.pop('tzinfos', None)
        self.dayfirst = kwargs.pop('dayfirst', None)
        self.yearfirst = kwargs.pop('yearfirst', None)
        self.fuzzy = kwargs.pop('fuzzy', None)
        super(DateTimeColumn, self).__init__(*args, **kwargs)

    def normalize(self, value):
        dt = parser.parse(
            value, parserinfo=self.parserinfo, ignoretz=self.ignoretz, tzinfos=self.tzinfos, dayfirst=self.dayfirst,
            yearfirst=self.yearfirst, fuzzy=self.fuzzy
        )
        return dt

    def validate(self, value):
        errors = super(DateTimeColumn, self).validate(value) or []
        try:
            self.normalize(value)
        except (OverflowError, ValueError) as e:
            errors.append(e.message) if errors is not None else [e.message]
        return errors if errors else None


class ModelTypeColumn(BaseColumn):
    """
        Use for parsing direct model association. Always set queryset;
        default lookup argument - primary key.
        Returns model instance.
    """
    def __init__(self, applabel=None, *args, **kwargs):
        self.applabel = applabel
        self._unique_models = None
        self._ambiguous_models = None
        super(ModelTypeColumn, self).__init__(*args, **kwargs)

    def normalize(self, value):
        if self.applabel:
            try:
                return apps.get_model(self.applabel, value)
            except LookupError:
                return None
        else:
            try:
                return self._get_model(value)
            except LookupError:
                return None
            except ValueError:
                return None

    def validate(self, value):
        error = super(ModelTypeColumn, self).validate(value) or []
        if self.applabel:
            try:
                apps.get_model(self.applabel, value)
            except LookupError:
                error += ['Model not found']
        else:
            try:
                return self._get_model(value)
            except LookupError:
                error += ['Model not found']
            except ValueError:
                error += ['Ambigious model, specify applabel']
        if error:
            return error
        else:
            return None

    def _get_model(self, value):
        value = value.lower()

        if self._unique_models is None:
            self._populate()

        if value in self._ambiguous_models:
            raise ValueError('%s is a model in more than one app. ')

        model = self._unique_models.get(value)
        if model is None:
            raise LookupError
        return model

    def _populate(self):
        """
            Cache models for faster self._get_model.
        """
        unique_models = {}
        ambiguous_models = []

        all_models = apps.all_models

        for app_model in all_models.values():
            for name, model in app_model.items():
                if name not in unique_models:
                    unique_models[name] = model
                else:
                    ambiguous_models.append(name)

        for name in ambiguous_models:
            unique_models.pop(name, None)

        self._ambiguous_models = ambiguous_models
        self._unique_models = unique_models
