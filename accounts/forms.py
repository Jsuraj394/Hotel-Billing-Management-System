from django import forms
from .models import Menu


class MenuForm(forms.ModelForm):
    class Meta:
        model = Menu
        fields = ['DishName', 'price', 'image']
        widgets = {
            'DishName': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


 
from django import forms
from .models import Expense
import datetime

class ExpenseForm(forms.ModelForm):
    date = forms.DateField(
        initial=datetime.date.today,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    owner = forms.ChoiceField(
        choices=Expense.OWNER_CHOICES,
        initial='Swad',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    payment_mode = forms.ChoiceField(
        choices=Expense.PAYMENT_CHOICES,
        initial='online',
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Payment Mode'
    )

    class Meta:
        model = Expense
        fields = [
            'date',
            'description',
            'amount',
            'owner',
            'payment_mode',
        ]
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
        }