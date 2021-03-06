from models import *
from django.shortcuts import render_to_response, redirect
from django.http import HttpResponse
from django.template import RequestContext

from datetime import datetime
from availability_display import availability_display
from roomlist import roomlist
from reserve_url import get_reserve_url

import urllib
import urllib2
import json
import os

BITLY_URL = "http://api.bitly.com/v3/shorten?"

def bitly(long_url):
  url = BITLY_URL
  args = {}
  args['login'] = os.getenv('BITLY_LOGIN')
  args['apiKey'] = os.getenv('BITLY_API_KEY')
  if args['login'] is None or args['apiKey'] is None:
      raise OSError("Please set the BITLY_LOGIN and BITLY_API_KEY environment variables")
  args['longUrl'] = str(long_url)
  args['format'] = 'json'
  formatted = url + urllib.urlencode(args)
  #return formatted
  page = urllib2.build_opener().open(formatted)
  json_str = page.read()
  json_dict = json.loads(json_str)
  data = json_dict['data']
  return data['url']


def shareevent(request):
  args = {}
  args['date'] = request.GET.get('date')
  args['shr'] = request.GET.get('shr')
  args['smin'] = request.GET.get('smin')
  args['ehr'] = request.GET.get('ehr')
  args['emin'] = request.GET.get('emin')
  roomid = request.GET.get('roomid')
  rooms = Room.objects.filter(id=roomid).all()
  args['room'] = rooms[0]
  url = request.build_absolute_uri()
  args['shorturl'] = bitly(url)
  return render_to_response('shareevent.html', args)


def show_all_available(request):
  """Initial, simple test view so we can examine data
    passing to template: dict(building->dict(room_kind->list(name)))"""

  all_rooms = {}

  for rk in RoomKind.objects.all():
    all_rooms_of_rk = [r.name for r in rk.room_set.all()]
    get_or_else(all_rooms, rk.building.name, {})[rk.name] = all_rooms_of_rk
  return render_to_response('simple.html', {'all_rooms': all_rooms})


def deeplink(request):
  """Given some URL (params: time_from/time_to xxxx, date yyyy-mm-dd, room_id])
     (TODO: room_kind id)
     redirects the user to the deep link for that particular room kind"""
  date = datetime.strptime(request.GET['date'], "%Y-%m-%d")
  time_from = int(request.GET['time_from'])
  time_to = int(request.GET['time_to'])
  room = Room.objects.get(id=int(request.GET['room']))

  return redirect(get_reserve_url(room, date, time_from, time_to))


def index(request):
  return render_to_response('index.html',
                            {}, context_instance=RequestContext(request))


def log_test(response):
  import logging
  logging.getLogger(__name__).error("test error")
  return HttpResponse("testing that logging works")
