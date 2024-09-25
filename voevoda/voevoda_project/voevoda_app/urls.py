from django.urls import path
from .views import ClansView, PlayerView, VoevodaView, KeyView, PersonsView, FightsEventsView
from .views import PresetsView, FightsView, PersonsPresetsView, InviteView

urlpatterns = [
    path("clans/", ClansView.as_view(), name="clans"),
    path("players/", PlayerView.as_view(), name="player"),
    path("voevoda/", VoevodaView.as_view(), name="voevoda"),
    path("keys/", KeyView.as_view(), name="keys"),
    path("presets/", PresetsView.as_view(), name="presets"),
    path("persons/", PersonsView.as_view(), name="persons"),
    path("persons_presets/", PersonsPresetsView.as_view(), name="persons_presets"),
    path("fights/", FightsView.as_view(), name="fights"),
    path("events/", FightsEventsView.as_view(), name="fights_event"),
    path("invites/", InviteView.as_view(), name="invites"),
]