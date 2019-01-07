from rest_framework import generics
from .models import Cluster
from .serializers import ClusterSerializer

class ClusterAPIView(generics.ListAPIView):
  queryset = Cluster.objects.all()
  serializer_class = ClusterSerializer
