from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
# from .helpers import charts_master
# import data
import json
from django.http import HttpResponse
from django.template import loader, Context, Template
import time
import datetime
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
#from .whatever import charts_master
import os
from .helpfunctions import main
from django.template.loader import render_to_string
from .helpfunctions import charts_master

# Create your views here.

def find_data_based_on_id(client_id):
    client_id = str(client_id)
    with open( 'report_generator/data/client_information.json', 'r') as f:
        clients = json.load(f)
    for client in clients:
        if clients[client]["client_id"] == client_id:
            data_sets = charts_master(clients, client)
    return data_sets

def display_traffic_chart(request,client_id):
    data_sets = find_data_based_on_id(client_id)
    traffic_data = data_sets[0]
    template = loader.get_template('traffic.html')
    context = {
        'data' : traffic_data
    }
    return HttpResponse(template.render(context,request))


def display_leads_chart(request, client_id):
    data_sets = find_data_based_on_id(client_id)
    leads_data = data_sets[1]
    template = loader.get_template('leads.html')
    context = {
        'data' : leads_data
    }
    return HttpResponse(template.render(context, request))

#def perform_whole_function(clients, client_id, client_lst):
    #display_traffic_chart(request, client_id)
   # display_leads_chart(request, client_id)
   # main(client_id)

def master(request,client_id):
    main(client_id)
    return HttpResponse()