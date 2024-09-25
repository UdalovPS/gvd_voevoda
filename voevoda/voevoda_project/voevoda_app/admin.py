from django.contrib import admin
from .models import ClansModel, PlayersModel, VoevodaModel, PersonsModel
from .models import PresetsModel, PersonPresetModel, FightsModel, FightEventModel
from .models import InviteModel
from .servises import KeyLogic


@admin.register(ClansModel)
class ClansModelAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'label', 'name', 'alliance'
    ]
    search_fields = ['name']


@admin.register(PlayersModel)
class PlayersModelAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "name",
        "level",
        "clan",
        "umka_knight",
        "umka_necro",
        "umka_mag",
        "umka_elf",
        "umka_barbar",
        "umka_black_elf",
        "umka_demon",
        "umka_dwarf",
        "umka_step_barb",
        "umka_pharaon",
        "gild_hunt",
        "gild_work",
        "gild_card",
        "gild_thief",
        "gild_ranger",
        "gild_mers",
        "gild_tactic",
        "gild_gard",
        "gild_seekers",
        "gild_leader",
        "gild_blacksmith",
        "gild_gunsmith"
    ]
    list_filter = ['clan', "level"]
    search_fields = ['id', 'name']


@admin.register(VoevodaModel)
class VoevodaModelAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'name', 'telegram_id', 'telegram_username', 'phone', "clan_id", "access_date", "tmp_code"
    ]
    search_fields = ['name']
    actions = ['generate_code']

    def generate_code(self, requests, queryset):
        for obj in queryset:
            key = KeyLogic().generate_access_key(sub_key="voevoda", data={"id": obj.id})
            queryset.update(tmp_code=key)

    generate_code.short_description = 'Сгенериновать код'


@admin.register(PersonsModel)
class PersonsModelAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'role', 'telegram_id', 'telegram_username', 'player_id', "voevoda_id", "activity"
    ]
    search_fields = ['name']
    list_filter = ['voevoda_id']


@admin.register(PresetsModel)
class PresetsModelAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'voevoda_id', 'fraction', 'name', 'description'
    ]
    search_fields = ['name']
    list_filter = ['voevoda_id', "fraction"]


@admin.register(PersonPresetModel)
class PersonPresetModelAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'person_id', 'preset_id', 'play_preset'
    ]
    list_filter = ['preset_id', "person_id", "play_preset"]


@admin.register(FightsModel)
class FightsModelAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "date",
        "name",
        "type",
        "voevoda_id",
        "attack_1_pers",
        "attack_2_pers",
        "defence_1_pers",
        "defence_2_pers",
        "attack_1_pers_preset",
        "attack_2_pers_preset",
        "defence_1_pers_preset",
        "defence_2_pers_preset",
        "result",
        "description",
    ]

    list_filter = ['voevoda_id', "type"]

    search_fields = ['name']


@admin.register(FightEventModel)
class FightEventModelAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "date",
        "name",
        "type",
        "voevoda_id",
        "enemy",
        "state"
    ]

    list_filter = ['voevoda_id', "type"]

    search_fields = ['name', "date"]


@admin.register(InviteModel)
class InviteModelAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "date",
        "event_id",
        "person_id",
        "state",
    ]

    list_filter = ["state"]

    search_fields = ["date", "event_id", "person_id"]