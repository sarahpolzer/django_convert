from django.db import models

# Create your models here.
class Organization(models.Model):
    domain_name = models.CharField(max_length=250)
    org_logo = models.CharField(max_length=250)
    what_converts = models.CharField(max_length=250)
    presentation_id = models.CharField(max_length=250)
    google_analytics = models.CharField(max_length=250)
