"""django_report_gen URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views
from .views import find_client_id
import json

with open( 'report_generator/data/client_information.json', 'r') as f:
        clients = json.load(f)
client = "321 Web Marketing"

client_id = find_client_id(client)
request = "GET"

app_name="report_generator"
urlpatterns = [
    #path('traffic/', views.display_traffic_chart(request,client_id), name='Traffic'),
    # ex: /polls/5/results/
    #path('leads/', views.display_leads_chart(request,client_id), name='Leads'),
    path('make-report/<int:org_id>', views.master(clients, client), name="generate-report")
]
