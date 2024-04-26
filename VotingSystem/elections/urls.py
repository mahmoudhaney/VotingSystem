from django.urls import path, include
from .views import VoteCreateView, ElectionListCreateView, ElectionCandidatesView, ElectionDetailWithWinnerView

app_name = 'elections'

elections_urls = [
    path('', ElectionListCreateView.as_view(), name='elections-list-create'),
    path('<uuid:election_uuid>/candidates/', ElectionCandidatesView.as_view(), name='election-candidates'),
    path('<uuid:election_uuid>/result/', ElectionDetailWithWinnerView.as_view(), name='election-result'),
]

urlpatterns = [
    path('', include(elections_urls)),
    path('vote/', VoteCreateView.as_view(), name='vote'),
]