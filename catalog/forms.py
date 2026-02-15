from django import forms
from .models import Cheese, BatchItem


class CheeseForm(forms.ModelForm):
    class Meta:
        model = Cheese
        fields = [
            "name",
            "price",
            "price_small_opt",
            "min_qty_small_opt",
            "price_big_opt",
            "min_qty_big_opt",
            "weight",
            "cheese_type",
            "in_stock",
            "production_date",
        ]
        labels = {
            "name": "Название",
            "price": "Цена (₽)",
            "price_small_opt": "Цена мелкий опт (₽)",
            "min_qty_small_opt": "Минимальное количество мелкий опт",
            "price_big_opt": "Цена крупный опт (₽)",
            "min_qty_big_opt": "Минимальное количество крупный опт",
            "weight": "Вес (г)",
            "cheese_type": "Тип сыра",
            "in_stock": "В наличии",
            "production_date": "Дата производства",
        }
        widgets = {
            "name":
                forms.TextInput(attrs={"placeholder": "Например, Пармезан"}),
            "price":
                forms.NumberInput(attrs={"min": "0", "step": "0.01"}),
            "price_small_opt":
                forms.NumberInput(attrs={"min": "0", "step": "0.01"}),
            "min_qty_small_opt":
                forms.NumberInput(attrs={"min": "0", "step": "1"}),
            "price_big_opt":
                forms.NumberInput(attrs={"min": "0", "step": "0.01"}),
            "min_qty_big_opt":
                forms.NumberInput(attrs={"min": "0", "step": "1"}),
            "weight":
                forms.NumberInput(attrs={"min": "0", "step": "0.1"}),
            "production_date":
                forms.DateInput(attrs={"type": "date"}),
        }


class BatchItemForm(forms.ModelForm):
    class Meta:
        model = BatchItem
        fields = ["cheese", "quantity"]
        widgets = {
            "quantity": forms.NumberInput(attrs={"min": 1}),
        }
