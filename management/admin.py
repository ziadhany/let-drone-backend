from django.contrib import admin

from management.models import Pharmacist, Patient, Geolocation, Drone, GCS, Comment, Prescription, Delivery

# Register your models here.
admin.site.register(Pharmacist)
admin.site.register(Patient)
admin.site.register(Geolocation)
admin.site.register(Drone)
admin.site.register(GCS)
admin.site.register(Comment)
admin.site.register(Prescription)
admin.site.register(Delivery)
