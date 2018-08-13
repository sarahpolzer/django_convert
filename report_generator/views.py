from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
# from .helpers import charts_master
# import data
import json
from django.http import HttpResponse
from django.template import loader
import time
import datetime
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from report_generator.whatever import charts_master
import os
from .helpfunctions import main

# Create your views here.
def find_client_id(client):
    client_lst = []
    with open( 'report_generator/data/client_information.json', 'r') as f:
        clients = json.load(f)
    for client in clients.keys():
        client_lst.append(client)
    for i in range(len(client_lst)):
        if client == client_lst[i]:
            client_id = i
    data = [client_id, client_lst]
    return data

def find_data_based_on_id(clients, client_id, client_lst):
    client = client_lst[client_id]
    data_sets = charts_master(clients, client)  
    traffic_data = data_sets[0]
    leads_data= data_sets[1]
    chart_data = [traffic_data, leads_data]
    return chart_data



def display_traffic_chart(request, client_id, traffic_data):
    traffic = traffic_data
    template = loader.get_template('traffic.html')
    context = {
        'data' : traffic
    }
    return HttpResponse(template.render(context,request))

def display_leads_chart(request, client_id, leads_data):
    leads = leads_data
    template = loader.get_template('leads.html')
    context = {
        'data' : leads
    }
    return HttpResponse(template.render(context, request))

def perform_whole_function(clients, client_id):
    find_data_based_on_id(clients, client_id)
    display_traffic_chart(request, client_id)
    display_leads_chart(request, client_id)
    main(clients, client)

def master(clients, client):
    request = "GET"
    data = find_client_id(client)
    client_id = data[0]
    client_lst = data[1]
    chart_data = find_data_based_on_id(clients,client_id, client_lst)
    traffic_data = chart_data[0]
    leads_data = chart_data[1]
    display_traffic_chart(request, client_id, traffic_data)
    display_leads_chart(request, client_id, leads_data)
    main(clients, client)