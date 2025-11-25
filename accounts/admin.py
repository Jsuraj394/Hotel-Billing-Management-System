from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(Menu)
admin.site.register(Invoice)
admin.site.register(Expense)
admin.site.register(Staff)
admin.site.register(StaffAttendance)