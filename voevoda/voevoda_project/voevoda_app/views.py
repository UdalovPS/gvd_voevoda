import json

from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from .servises import ClansLogic, PlayersLogic, VoevodaLogic, KeyLogic, PresetsLogic, FightsLogic, logger
from .servises import PersonPresetLogic, PersonsLogic, FightEventLogic, InviteLogic


@method_decorator(csrf_exempt, name='dispatch')
class ClansView(View):
    """Представление для работы с данными кланов"""

    @staticmethod
    def get(request, *args, **kwargs):
        clan_id = request.GET.get('clan_id')

        obj = ClansLogic()
        data = obj.get_clan_data(clan_id=clan_id)
        if data:
            return JsonResponse(data={"success": True, "data": data}, status=200)
        else:
            return JsonResponse(data={"success": False, "data": "clan not found"}, status=400)

    @staticmethod
    def post(request, *args, **kwargs):
        """Данный метод добавляет новый клан"""
        json_data = json.loads(request.body)
        obj = ClansLogic()
        data = obj.add_clan(clan_id=json_data["id"], name=json_data["name"], label=json_data["label"])
        if data:
            return JsonResponse(data={"success": True, "data": data}, status=200)
        else:
            return JsonResponse(data={"success": False, "data": "clan not add"}, status=400)

    @staticmethod
    def patch(request,  *args, **kwargs):
        """Обновление информации о клане"""
        json_data = json.loads(request.body)
        obj = ClansLogic()
        data = obj.update_clan_data(clan_id=json_data["id"], name=json_data["name"], label=json_data["label"], alliance=json_data["alliance"])
        if data:
            return JsonResponse(data={"success": True}, status=200)
        else:
            return JsonResponse(data={"success": False}, status=400)

    @staticmethod
    def put(request, *args, **kwargs):
        obj = ClansLogic()
        data = obj.reparse_clan_data()
        return JsonResponse(data=data)


@method_decorator(csrf_exempt, name='dispatch')
class PlayerView(View):
    """Представление для работы с данными игроков"""

    @staticmethod
    def get(request, *args, **kwargs):

        player_filter = {
            "player_id": request.GET.get('player_id'),
            "clan_id": request.GET.get('clan_id'),
            "voevoda_id": request.GET.get('voevoda_id'),
        }

        obj = PlayersLogic()
        data = obj.get_players_data(player_filter=player_filter)

        if data:
            return JsonResponse(data={"success": True, "data": data}, status=200)
        else:
            return JsonResponse(data={"success": False, "data": "Player not found"}, status=400)

    @staticmethod
    def post(request, *args, **kwargs):
        """Данный метод добавляет нового игрока"""
        json_data = json.loads(request.body)
        obj = PlayersLogic()
        data = obj.add_new_player(in_data=json_data)
        if data:
            return JsonResponse(data={"success": True, "data": data}, status=200)
        else:
            return JsonResponse(data={"success": False, "data": "Player not add"}, status=400)

    @staticmethod
    def patch(request, *args, **kwargs):
        """Данный метод добавляет нового игрока"""
        json_data = json.loads(request.body)
        obj = PlayersLogic()
        data = obj.update_player_data(in_data=json_data)
        if data:
            return JsonResponse(data={"success": True}, status=200)
        else:
            return JsonResponse(data={"success": False}, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class VoevodaView(View):
    """Представление для работы с данными воеводы"""

    @staticmethod
    def patch(request, *args, **kwargs):
        """Данный метод обновляет данные воеводы"""
        json_data = json.loads(request.body)
        obj = VoevodaLogic()
        data = obj.connect_voevoda_telegram(**json_data)
        if data:
            return JsonResponse(data={"success": True, "data": data}, status=200)
        else:
            return JsonResponse(data={"success": False, "data": "Player not add"}, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class KeyView(View):
    """Метод для создания временная ключу"""

    @staticmethod
    def get(request, *args, **kwargs):
        """Данный метод обновляет данные воеводы"""
        sub_key = request.GET.get('sub_key')
        data = {}
        if request.GET.get('id'):
            data["id"] = request.GET.get('id')
        if request.GET.get('player_id'):
            data["player_id"] = request.GET.get('player_id')
        if request.GET.get('voevoda_id'):
            data["voevoda_id"] = request.GET.get('voevoda_id')
        if request.GET.get('role'):
            data["role"] = request.GET.get('role')
        if request.GET.get('name'):
            data["name"] = request.GET.get('name')
        data = KeyLogic().generate_access_key(sub_key=sub_key, data=data)
        if data:
            return JsonResponse(data={"success": True, "data": data}, status=200)
        else:
            return JsonResponse(data={"success": False, "data": "Error to generate key"}, status=400)

    @staticmethod
    def post(request, *args, **kwargs):
        """ Данный метод проверяет код на валидность"""
        json_data = json.loads(request.body)
        logger.info(f"Validate access code: {json_data}")
        data = KeyLogic().validate_access_code(**json_data)
        if data:
            return JsonResponse(data={"success": True}, status=200)
        else:
            return JsonResponse(data={"success": False}, status=400)

    @staticmethod
    def put(request, *args, **kwargs):
        json_data = json.loads(request.body)
        logger.info(f"Get access code to render: {json_data}")
        data = KeyLogic().get_access_code(**json_data)
        if data:
            return JsonResponse(data={"success": True, "data": data}, status=200)
        else:
            return JsonResponse(data={"success": False}, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class PresetsView(View):
    """Для работы с данными пресетов"""

    @staticmethod
    def get(request, *args, **kwargs):
        preset_filter = {
            "preset_id": request.GET.get('preset_id'),
            "voevoda_id": request.GET.get('voevoda_id')
        }
        obj = PresetsLogic()
        data = obj.get_presets_data(data_filter=preset_filter)

        if data:
            return JsonResponse(data={"success": True, "data": data}, status=200)
        else:
            return JsonResponse(data={"success": False, "data": "Player not found"}, status=400)

    @staticmethod
    def post(request, *args, **kwargs):
        """Данный метод добавляет нового пресета"""
        json_data = json.loads(request.body)
        obj = PresetsLogic()
        data = obj.add_new_preset(in_data=json_data)
        if data:
            return JsonResponse(data={"success": True, "data": data}, status=200)
        else:
            return JsonResponse(data={"success": False}, status=400)

    @staticmethod
    def patch(request, *args, **kwargs):
        """Данный метод добавляет нового игрока"""
        json_data = json.loads(request.body)
        obj = PresetsLogic()
        data = obj.update_preset_data(in_data=json_data)
        if data:
            return JsonResponse(data={"success": True}, status=200)
        else:
            return JsonResponse(data={"success": False}, status=400)

    @staticmethod
    def delete(request, *args, **kwargs):
        preset_id = request.GET.get('preset_id')
        obj = PresetsLogic()
        data = obj.delete_preset_data(preset_id=preset_id)
        if data:
            return JsonResponse(data={"success": True}, status=200)
        else:
            return JsonResponse(data={"success": False}, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class PersonsView(View):
    """Для работы с данными живых игроков"""

    @staticmethod
    def get(request, *args, **kwargs):
        filter = {
            "person_id": request.GET.get('person_id'),
            "voevoda_id": request.GET.get('voevoda_id')
        }
        obj = PersonsLogic()
        data = obj.get_person_data(filter=filter)

        if data:
            return JsonResponse(data={"success": True, "data": data}, status=200)
        else:
            return JsonResponse(data={"success": False, "data": "Persons not found"}, status=400)

    @staticmethod
    def post(request, *args, **kwargs):
        """Данный метод добавляет нового игрока"""
        json_data = json.loads(request.body)
        obj = PersonsLogic()
        data = obj.connect_person_telegram(**json_data)
        if data:
            return JsonResponse(data={"success": True, "data": data}, status=200)
        else:
            return JsonResponse(data={"success": False}, status=400)

    @staticmethod
    def patch(request, *args, **kwargs):
        """Данный метод добавляет нового игрока"""
        json_data = json.loads(request.body)
        obj = PersonsLogic()
        data = obj.update_person_data(in_data=json_data)
        if data:
            return JsonResponse(data={"success": True}, status=200)
        else:
            return JsonResponse(data={"success": False}, status=400)

    @staticmethod
    def delete(request, *args, **kwargs):
        person_id = request.GET.get('person_id')
        obj = PersonsLogic()
        data = obj.delete_person_data(person_id=person_id)
        if data:
            return JsonResponse(data={"success": True}, status=200)
        else:
            return JsonResponse(data={"success": False}, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class PersonsPresetsView(View):
    """Для работы с данными живых игроков и относящихся к ним пресетах"""

    @staticmethod
    def get(request, *args, **kwargs):
        """Получаем данные пресетов живых игроков"""
        person_id = request.GET.get('person_id')
        obj = PersonPresetLogic()
        data = obj.get_person_presets(person_id=person_id)
        if data:
            return JsonResponse(data={"success": True, "data": data}, status=200)
        else:
            return JsonResponse(data={"success": False}, status=400)

    @staticmethod
    def patch(request, *args, **kwargs):
        """Данный метод обновляет данные персональных пресетов"""
        json_data = json.loads(request.body)
        obj = PersonPresetLogic()
        data = obj.update_person_preset_data(in_data=json_data)
        if data:
            return JsonResponse(data={"success": True}, status=200)
        else:
            return JsonResponse(data={"success": False}, status=400)

    @staticmethod
    def delete(request, *args, **kwargs):
        json_data = json.loads(request.body)
        obj = PersonPresetLogic()
        data = obj.delete_person_presets_data(in_data=json_data)
        if data:
            return JsonResponse(data={"success": True}, status=200)
        else:
            return JsonResponse(data={"success": False}, status=400)

    @staticmethod
    def post(request, *args, **kwargs):
        """Добавление нового персонального пресета"""
        json_data = json.loads(request.body)
        obj = PersonPresetLogic()
        data = obj.add_new_person_preset(in_data=json_data)
        if data:
            return JsonResponse(data={"success": True, "data": data}, status=200)
        else:
            return JsonResponse(data={"success": False}, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class FightsView(View):
    """Представление для работы боев"""

    @staticmethod
    def post(request, *args, **kwargs):
        """Добавление нового персонального пресета"""
        json_data = json.loads(request.body)
        obj = FightsLogic()
        data = obj.add_fight(in_data=json_data)
        if data:
            return JsonResponse(data={"success": True, "data": data}, status=200)
        else:
            return JsonResponse(data={"success": False}, status=400)

    @staticmethod
    def get(request, *args, **kwargs):
        filter = {
            "fight_id": request.GET.get('fight_id'),
            "voevoda_id": request.GET.get('voevoda_id')
        }
        data = FightsLogic().get_fights(in_data=filter)
        if data:
            return JsonResponse(data={"success": True, "data": data}, status=200)
        else:
            return JsonResponse(data={"success": False}, status=400)

    @staticmethod
    def patch(request, *args, **kwargs):
        json_data = json.loads(request.body)
        data = FightsLogic().update_fight(in_data=json_data)
        if data:
            return JsonResponse(data={"success": True}, status=200)
        else:
            return JsonResponse(data={"success": False}, status=400)

    @staticmethod
    def delete(request, *args, **kwargs):
        json_data = json.loads(request.body)
        data = FightsLogic().delete_fight(fight_id=json_data["fight_id"])
        if data:
            return JsonResponse(data={"success": True}, status=200)
        else:
            return JsonResponse(data={"success": False}, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class FightsEventsView(View):
    """Представление для работы боевых ивентов"""

    @staticmethod
    def post(request, *args, **kwargs):
        """Добавление нового персонального пресета"""
        json_data = json.loads(request.body)
        data = FightEventLogic().add_event(in_data=json_data)
        if data:
            return JsonResponse(data={"success": True, "data": data}, status=200)
        else:
            return JsonResponse(data={"success": False}, status=400)

    @staticmethod
    def get(request, *args, **kwargs):
        filter = {"event_id": request.GET.get('event_id')}
        if request.GET.get('voevoda_id'):
            filter["voevoda_id"] = request.GET.get('voevoda_id')
        if request.GET.get('state__in'):
            filter["state__in"] = request.GET.getlist('state__in')

        data = FightEventLogic().get_events(in_data=filter)
        if data:
            return JsonResponse(data={"success": True, "data": data}, status=200)
        else:
            return JsonResponse(data={"success": False}, status=400)

    @staticmethod
    def patch(request, *args, **kwargs):
        json_data = json.loads(request.body)
        data = FightEventLogic().update_event(in_data=json_data)
        if data:
            return JsonResponse(data={"success": True}, status=200)
        else:
            return JsonResponse(data={"success": False}, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class InviteView(View):
    """Представление для работы с приглашениями на ивенты"""

    @staticmethod
    def get(request, *args, **kwargs):
        filter = {"invite_id": request.GET.get('invite_id')}
        if request.GET.get('state__in'):
            filter["state__in"] = request.GET.getlist('state__in')
        if request.GET.get('event_id'):
            filter["event_id"] = request.GET.get('event_id')

        data = InviteLogic().get_invites(in_data=filter)
        if data:
            return JsonResponse(data={"success": True, "data": data}, status=200)
        else:
            return JsonResponse(data={"success": False}, status=400)

    @staticmethod
    def post(request, *args, **kwargs):
        """Добавление нового приглашения"""
        json_data = json.loads(request.body)
        data = InviteLogic().add_invite(in_data=json_data)
        if data:
            return JsonResponse(data={"success": True, "data": data}, status=200)
        else:
            return JsonResponse(data={"success": False}, status=400)

    @staticmethod
    def patch(request, *args, **kwargs):
        json_data = json.loads(request.body)
        data = InviteLogic().update_invite(in_data=json_data)
        if data:
            return JsonResponse(data={"success": True}, status=200)
        else:
            return JsonResponse(data={"success": False}, status=400)