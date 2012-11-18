# -*- coding: utf-8 -*-


from django import forms


class CityForm(forms.Form):
    city_name = forms.CharField(max_length=200, label=u"Введите город")
    estimated_population = forms.IntegerField(min_value=0, label=u"Предположите население")
