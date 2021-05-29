from django.db import models

# Create your models here.
class ChartData(models.Model):
    files = models.FileField(upload_to='files')
    name = models.CharField(max_length=200,default='files')

    def __str__(self):
        return self.name

    