from django.db import models

class Results(models.Model):
    ET0 = models.DecimalField(max_digits=10, decimal_places=2)
    ETc = models.DecimalField(max_digits=10, decimal_places=2)
    IRn = models.DecimalField(max_digits=10, decimal_places=2)
    IR = models.DecimalField(max_digits=10, decimal_places=2)
    Dw = models.DecimalField(max_digits=10, decimal_places=2)
    IDG = models.DecimalField(max_digits=10, decimal_places=2)
    Wf = models.PositiveIntegerField()
    city = models.CharField(max_length=1000)
    Date = models.DateTimeField(auto_now_add=True)

class SensorData(models.Model):
    SoilMoistureValue = models.PositiveIntegerField()
    Date = models.DateTimeField(auto_now_add=True)