from django.db import models
from django.utils.translation import ugettext_lazy as _


class TestModel(models.Model):
    """
    Base for test models that sets app_label, so they play nicely.
    """

    class Meta:
        app_label = 'tests'
        abstract = True


class BasicModel(TestModel):
	text = models.CharField(max_length=100)
