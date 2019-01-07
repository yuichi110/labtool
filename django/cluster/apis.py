from rest_framework import generics
from .models import Cluster
from .serializers import ClusterSerializer

class ListCluster(generics.ListAPIView):
  queryset = Cluster.objects.all()
  serializer_class = ClusterSerializer

class DetailCluster(generics.RetrieveAPIView):
  queryset = Cluster.objects.all()
  serializer_class = ClusterSerializer