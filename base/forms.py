from django.forms import ModelForm, CheckboxSelectMultiple, Form, FileField, FileInput, ModelMultipleChoiceField, CharField, TextInput
from .models import Product, Category, Hub

class ProductFilterForm(Form):
    query = CharField(
        label='Buscar por nombre',
        required=False,
        widget= TextInput(attrs={'placeholder': 'Ej: Harina', 'class': 'form-control'})
    )
    categories =  ModelMultipleChoiceField(
        label= 'Categorías',
        queryset= Category.objects.all(),
        widget= CheckboxSelectMultiple,
        required= False
    )
    
    hubs =  ModelMultipleChoiceField(
        label='Hubs',
        queryset=Hub.objects.all(),
        widget=CheckboxSelectMultiple,
        required=False
    )

class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = '__all__'
        widgets = {
            'categories': CheckboxSelectMultiple,
            'hubs': CheckboxSelectMultiple,
        }
        

class ImportProductCSVForm(Form):
    csv_file = FileField(
        label= 'Selecciona un archivo CSV para importar productos',
        widget= FileInput(attrs={'accept': '.csv'})
    )