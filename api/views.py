from django.contrib.auth.models import User
from .models import Organization
from rest_framework import viewsets
from .serializers import UserSerializer, OrganizationSerializer
# Create your views here.

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer

class OrganizationViewSet(viewsets.ModelViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer


def send(request):
    with open( 'django_report_gen/report_generator/data/client_information.json', 'r') as f:
        clients = json.load(f)
    for client in clients:
        client_id = clients[client]['client_id']
        url = '127.0.0.8000/' + client_id
        o = Organization(organization=client, report_url=url)
        o.save()
    return HttpResponse('')