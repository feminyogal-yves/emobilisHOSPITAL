from django.contrib import admin

# Register your models here.
from Patients.models import Patient

admin.site.register(Patient)