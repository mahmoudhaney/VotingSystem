from django.urls import path
from .views import VoteCreateView, ElectionListCreateView

app_name = 'elections'

urlpatterns = [
    path('', ElectionListCreateView.as_view(), name='elections'),
    path('vote/', VoteCreateView.as_view(), name='vote'),
]