# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.template import RequestContext
from django.template.loader import render_to_string
from django.forms.util import ErrorList
from django.core.exceptions import ObjectDoesNotExist

from game.utils import json_response, check_pop
from game.forms import CityForm
from game.models import City


def home(request):
    records = request.session.get('records', {})
    rendered_records = [row.render() for row in records.itervalues()]
    city_form = CityForm()
    return render_to_response('index.html',
        {'records': rendered_records,
        'cityform': city_form,
        'average_precision': average_precision(records)},
        context_instance=RequestContext(request))


class Row(object):
    def __init__(self, city_name, est_pop, real_pop):
        self.city_name = city_name
        self.est_pop = est_pop
        self.real_pop = real_pop

    @property
    def precision(self):
        pair_pop = (self.est_pop, self.real_pop)
        return float(min(pair_pop)) / max(pair_pop)

    def render(self):
        return u"<tr><td>{0}</td><td>{1}</td>" \
               u"<td>{2}</td><td>{3:.0f}%</td></tr>".format(
            self.city_name, self.est_pop, self.real_pop, self.precision * 100)


def render_form(request, form):
    return render_to_string('form.html', {'cityform': form.as_table()},
        context_instance=RequestContext(request))


def make_estimate(request):
    if request.POST.get('clear'):
        if request.session.get('records'):
            del request.session['records']
        return json_response({'action': 'clean'})

    form = CityForm(request.POST)
    if not form.is_valid():
        return json_response({'form': render_form(request, form)})

    city_name = form.cleaned_data.get('city_name')
    est_pop = form.cleaned_data.get('estimated_population')
    records = request.session.get('records', {})

    try:
        city_in_db = City.objects.get(name=city_name)
    except ObjectDoesNotExist:
        city_in_db = None

    if city_name in records:
        msg = u'Оценка населения этого города уже выполнялась'
        form._errors["city_name"] = ErrorList([msg])
        return json_response({'form': render_form(request, form)})

    if city_in_db:
        real_pop = city_in_db.population
    else:
        real_pop = check_pop(city_name)
        if real_pop:
            City(name=city_name, population=real_pop).save()
        else:
            msg = u"Нет информации о населении этого города"
            form._errors["city_name"] = ErrorList([msg])
            return json_response({'form': render_form(request, form)})

    new_row = {city_name: Row(city_name, est_pop, real_pop)}
    records.update(new_row)
    request.session['records'] = records
    city_form = CityForm()
    rendered = render_to_string('form.html',
        {'cityform': city_form.as_table()},
        context_instance=RequestContext(request))
    x = {'new_row': new_row[city_name].render(),
        'form': rendered,
        'average_precision': average_precision(records)}
    return json_response(x)


def average_precision(records):
    if not records:
        return False
    sum_of_precisions = sum(row.precision for row in records.itervalues())
    return "%.0f%%" % (sum_of_precisions * 100 / len(records))
