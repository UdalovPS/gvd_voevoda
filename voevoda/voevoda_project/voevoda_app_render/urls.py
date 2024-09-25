from django.urls import path
from .import views

urlpatterns = [
    path("", views.Main.as_view(), name='main'),
    path("players/", views.Players.as_view(), name='players'),
    path("player/", views.Player.as_view(), name='player'),
    path("clan/", views.Clan.as_view(), name='clan'),
    path("event/", views.Event.as_view(), name='event'),
    path("fight/", views.Fight.as_view(), name='fight'),
    path("person/", views.Person.as_view(), name='person'),
    path("presets/", views.Presets.as_view(), name='presents'),
    path("preset/", views.Preset.as_view(), name='present'),
]