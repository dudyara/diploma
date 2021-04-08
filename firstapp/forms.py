from django import forms


class UserForm(forms.Form):
    id = forms.CharField(label="ID Сотрудника")
    month = forms.IntegerField(label="Месяц")
    year = forms.IntegerField(label="Год")