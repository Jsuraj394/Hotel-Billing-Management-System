from django.urls import path
from . import views
from .views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # path('login/', views.user_login, name='login'),
    path('generateBill/', views.generateBill),
    path('generate_bill_summary/', views.generate_bill_summary),
    path('print-invoice/', views.print_invoice, name='print_invoice'),
    path(r'billHistory/', views.invoice_history,name='invoice_history'),
    path('adminPanel/', admin_dashboard, name='admin_dashboard'),
    path('edit_menu/', edit_menu, name='edit_menu'),
    path('daily_summary/', daily_summary, name='daily_summary'),
    path('add_expense/', views.add_expense, name='add_expense'),


    path('adminPanel/staff/', views.staff_management, name='staff_management'),
    path('adminPanel/staff/add/', views.add_staff, name='add_staff'),
    path('adminPanel/staff/edit/<int:staff_id>/', views.edit_staff, name='edit_staff'),
    path('adminPanel/staff/delete/<int:staff_id>/', views.delete_staff, name='delete_staff'),
    path('adminPanel/staff/attendance/', views.mark_attendance, name='mark_attendance'),


]
