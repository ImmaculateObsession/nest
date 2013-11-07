from django.db import models


class Setting(models.Model):

    key = models.CharField(max_length=50, unique=True)
    value = models.TextField()
    export_to_template = models.BooleanField(default=False)
    export_to_context = models.BooleanField(default=False)
    show_in_admin = models.BooleanField(default=True)

    def __str__(self):
        return self.key

    def __unicode__(self):
        return self.key
