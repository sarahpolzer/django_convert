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
import json

with open( 'report_generator/data/client_information.json', 'r') as f:
    clients = json.load(f)

app_name="report_generator"
urlpatterns = [
    path('traffic/<int:client_id>', views.display_traffic_chart, name='Traffic'),
    path('leads/<int:client_id>', views.display_leads_chart, name='Leads'),
    path('make-report/<int:client_id>', views.master, name = 'generate-report')

]


