from django.db import models
from django.utils import timezone

# Create your models here.

class Menu(models.Model):
    CATEGORY_CHOICES = [
        ('Breakfast', 'Breakfast'),
        ('Rice', 'Rice'),
        ('Thali', 'Thali'),
        ('Main Course', 'Main Course'),
        ('Beverage', 'Beverage'),
    ]

    sno = models.AutoField(primary_key=True)
    DishName = models.CharField(max_length=200)
    # price = models.CharField(max_length=30)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    image = models.ImageField(upload_to='menu_images/')
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='Main Course'
    )

    def __str__(self):
        return f"{self.DishName} ({self.category})"

class Invoice(models.Model):
    invoice_number = models.AutoField(primary_key=True)
    invoice_date   = models.DateTimeField()
    items          = models.TextField()            # ← allow longer JSON
    total          = models.CharField(max_length=10)



class Expense(models.Model):
    OWNER_CHOICES = [
        ('Sura',   'Sura'),
        ('Vijay',  'Vijay'),
        ('Swad',   'Swad'),
        ('Aditya', 'Aditya'),
    ]
    PAYMENT_CHOICES = [
        ('cash',   'Cash'),
        ('online', 'Online'),
    ]

    date = models.DateField(default=timezone.localdate)
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    owner = models.CharField(
        max_length=10,
        choices=OWNER_CHOICES,
        default='Swad'
    )
    payment_mode = models.CharField(
        max_length=10,
        choices=PAYMENT_CHOICES,
        default='cash'
    )

    def __str__(self):
        return f"{self.date} | {self.owner} | {self.payment_mode.title()} | ₹{self.amount}"


class Staff(models.Model):
    name = models.CharField(max_length=100)
    age = models.PositiveIntegerField()
    aadhar_number = models.CharField(max_length=12, unique=True)
    address = models.TextField()
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    joining_date = models.DateField()

    def __str__(self):
        return self.name


class StaffAttendance(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    date = models.DateField()
    present = models.BooleanField(default=False)

    class Meta:
        unique_together = ('staff', 'date')


