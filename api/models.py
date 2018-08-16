from django.db import models

# Create your models here.
class Organization(models.Model):
    organization = models.CharField(max_length=250)
    report_url = models.CharField(max_length=250)

    def __str__(self):
        return '%s %s' % (self.organization, self.report_url)