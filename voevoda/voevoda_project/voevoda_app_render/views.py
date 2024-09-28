from django.shortcuts import render
from django.views import View
from django.shortcuts import redirect
from django.http import Http404
import os
import requests


# Create your views here.

class Main(View):
    def get(self, request):
        code = request.GET.get('code')
        if code:
            code_data = requests.put(
                url="http://127.0.0.1:8000/api/keys/",
                json={"code": code}
            ).json()

            if code_data["success"]:
                request.session['voevoda_id'] = code_data["data"]["voevoda_id"]
                request.session['name'] = code_data["data"]["name"]
                request.session['clan_id'] = code_data["data"]["clan_id"]
                request.session['sub_person_id'] = code_data["data"]["sub_person_id"]
        return render(
            request=request,
            template_name="voevoda_app_render/main.html",
        )


class Presets(View):
    def get(self, request):
        return render(
            request=request,
            template_name="voevoda_app_render/presets.html",
        )


class Preset(View):
    def get(self, request):
        preset_id = request.GET.get('preset_id')
        voevoda_id = request.session.get("voevoda_id")
        if preset_id and voevoda_id:
            preset_data = requests.get(
                url="http://127.0.0.1:8000/api/presets/",
                params={"preset_id": preset_id}
            ).json()
            if preset_data["success"]:
                if preset_data["data"]["voevoda_id"] == int(voevoda_id):
                    return render(
                        request=request,
                        template_name="voevoda_app_render/preset.html",
                        context={"preset_data": preset_data["data"]}
                    )
        return render(
            request=request,
            template_name="voevoda_app_render/preset.html",
        )


class Player(View):
    def get(self, request):
        player_id = request.GET.get('player_id')
        voevoda_id = request.session.get("voevoda_id")
        if player_id and voevoda_id:
            player_data = requests.get(
                url="http://127.0.0.1:8000/api/persons/",
                params={"person_id": player_id}
            ).json()
            if player_data["success"]:
                if player_data["data"]["voevoda_id"] == int(voevoda_id):
                    return render(
                        request=request,
                        template_name="voevoda_app_render/player.html",
                        context={"player_data": player_data["data"]}
                    )
        raise Http404("Not found")



class Players(View):
    def get(self, request):
        return render(
            request=request,
            template_name="voevoda_app_render/players.html",
        )



class Clan(View):
    def get(self, request):
        clan_id = request.GET.get('clan_id')
        my = True if request.GET.get('my') else False
        if not clan_id:
            clan_id = request.session.get("clan_id")
        if not clan_id:
            return redirect('/')
        return render(
            request=request,
            template_name="voevoda_app_render/clan.html",
            context={"clan_id": clan_id, "my": my}
        )


class Event(View):
    def get(self, request):
        return render(
            request=request,
            template_name="voevoda_app_render/event.html",
        )


class Fights(View):
    def get(self, request):
        return render(
            request=request,
            template_name="voevoda_app_render/fights.html",
        )


class Fight(View):
    def get(self, request):

        fight_id = request.GET.get('fight_id')
        voevoda_id = request.session.get("voevoda_id")

        presets_data = requests.get(
            url="http://127.0.0.1:8000/api/presets/",
            params={voevoda_id: "voevoda_id"}
        ).json()

        if fight_id and voevoda_id:
            fight_data = requests.get(
                url="http://127.0.0.1:8000/api/fights/",
                params={"fight_id": fight_id, voevoda_id: "voevoda_id"}
            ).json()
            if fight_data["success"]:
                if fight_data["data"]["voevoda_id"] == int(voevoda_id):
                    return render(
                        request=request,
                        template_name="voevoda_app_render/fight.html",
                        context={"fight_data": fight_data["data"], "presets_data": presets_data["data"]}
                    )
        return render(
            request=request,
            template_name="voevoda_app_render/fight.html",
            context={"presets_data": presets_data["data"]}
        )


class Person(View):
    def get(self, request):
        return render(
            request=request,
            template_name="voevoda_app_render/person.html",
        )