# -*- coding: utf-8 -*-

from django.http import HttpResponse
import json
import urllib, urllib2
import re


def json_response(d):
    return HttpResponse(json.dumps(d), mimetype='application/json; charset=UTF-8')

def check_pop(name):
    params = {"format":"xml",
              "action":"query",
              "prop":"revisions",
              "rvprop":"timestamp|user|comment|content"}
    params["titles"] = "API|%s" % urllib.quote(name.encode("utf8"))
    qs = "&".join("%s=%s" % (k, v)  for k, v in params.items())
    url = "http://ru.wikipedia.org/w/api.php?%s" % qs
    #print url
    opener = urllib2.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')] #
    city_wp_html = opener.open(url).read()
    try:
        pop_string = re.search(r"\| ?население.*", city_wp_html).group()
        pop = int(''.join([d for d in pop_string.split("&lt;")[0] if d.isdigit()]))
    except AttributeError:
        return None
    return pop