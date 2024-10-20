"""Вся логика спрятана в данном модуле"""
import datetime
from typing import Union
import logging

from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError
from django.db.models import Q

from .models import *
from .parser import ClansParser,PlayerParser
from .redis_core import Redis
from . import schemas

logger = logging.getLogger(__name__)


class KeyLogic(Redis):
    """Логический класс с данными для генерации ключей доступа"""
    def generate_access_key(self, sub_key: str, data: dict) -> int:
        """Данный метод генерирует ключ доступа и прячет под ним данные
        в КЭШ по логике согласно sub_key
        """
        method_dict = {
            "voevoda": self.__generate_voevoda_reg_key,
            "person": self.__generate_person_reg_key,
            "render": self.__generate_auth_render_key
        }
        return method_dict[sub_key](**data)

    def __generate_auth_render_key(self, name: str):
        """Данный метод генерирует временный код доступа
        для входа в системы в браузере, чтобы пройти аутентификацию
        Args:
            name: имя пользователя, который проходит аутентификацию
        """
        data = None
        user = VoevodaModel.objects.filter(Q(name=name) | Q(telegram_username=name)).first()
        if user:
            data = schemas.VoevodaAuthSchem(
                voevoda_id=user.id,
                name=user.name,
                clan_id=user.clan_id.id
            )
        else:
            user = PersonsLogic().get_person_data_by_filter(filter={
                "telegram_username": name,
                "role": 2
            })
            if user:
                data = schemas.VoevodaAuthSchem(
                    voevoda_id=user[0]["voevoda_id"],
                    name=user[0]["stats"]["name"],
                    clan_id=user[0]["stats"]["clan"],
                    sub_person_id=user[0]["id"]
                )
        return self.create_connect_key(sub_key="render", data=data)

    def __generate_voevoda_reg_key(self, id: int) -> int:
        """Генерирует ключ доступа, когда регистрируется воевода
        Args:
            id: идентификатор воеводы из БД
        """
        data = schemas.VoevodaRegSchem(id=id)
        return self.create_connect_key(sub_key="voevoda", data=data)

    def __generate_person_reg_key(self, role: int, player_id: int, voevoda_id: int) -> int:
        """Генерирует ключ доступа, когда регистрируется игрок под воеводой
        Args:
            role: роль регистрируемого игрока (1 - воевода, 2 - помощник , 100 - игрок)
            player_id: идентификатор игрового персонажа
            voevoda_id: идентификатор воеводы, за которым закрепляется игрок
        """
        data = schemas.PersonRegisterSchem(
            player_id=player_id,
            voevoda_id=voevoda_id,
            role=role
        )
        return self.create_connect_key(sub_key="person", data=data)

    def validate_access_code(self, code: int):
        """Данный метод проверяет на валидность код доступа"""
        try:
            data = self.get_data_from_cache(key=f"render:{code}", data_class=schemas.VoevodaAuthSchem)
            if data:
                logger.info(f"Прошел валидацию по коду: {code} -> {data}")
                return data.model_dump()
        except Exception as _ex:
            logger.error(f"Ошибка при валидации кода: {code} -> {_ex}")

    def get_access_code(self, code: int):
        """Данный метод проверяет на валидность код доступа"""
        try:
            data = self.get_data_from_cache(key=f"render:{code}", data_class=schemas.VoevodaAuthSchem)
            if data:
                logger.info(f"Прошел валидацию по коду: {code} -> {data}")
                self.delete_data_from_cache(key=f"render:{code}")
                return data.model_dump()
        except Exception as _ex:
            logger.error(f"Ошибка при валидации кода: {code} -> {_ex}")



class ClansLogic:
    """Логика связанная со взаимодействием с кланами"""

    def get_clan_data(self, clan_id: int):
        """Извлечение информации а клане по его ID"""
        try:
            data = ClansModel.objects.get(pk=clan_id)
            logger.info(f"Извлеченные данные о клане: №{data.id} {data.name}. Альянс с: {data.alliance}")
            return {"id": data.id, "name": data.name, "label": data.label, "alliance": self.get_clan_data_without_alliance(data.alliance)}
        except ObjectDoesNotExist:
            logger.error(f"Не найден клан с ID: {clan_id}")
            return None

    def get_clan_data_by_name(self, clan_name: str):
        """Извлечение данных клана по имени без учета регистра"""
        try:
            data = ClansModel.objects.filter(Q(name__icontains=clan_name))
            return [
                {"id": one_data.id, "name": one_data.name, "label": one_data.label, "alliance": self.get_clan_data_without_alliance(one_data.alliance)}
                for one_data in data
            ]
        except ObjectDoesNotExist:
            logger.error(f"Не найден клан с name: {clan_name}")
            return None

    @staticmethod
    def get_clan_data_without_alliance(alliance_data: Union[ClansModel, None]):
        if alliance_data is None:
            return None
        else:
            try:
                return {"id": alliance_data.id, "name": alliance_data.name, "label": alliance_data.label}
            except Exception as _ex:
                logger.error(f"Ошибка с возвращением данных альянса клана: {alliance_data}")
                return None

    def serialize_one_clan_data(self, data: ClansModel):
        return {
            "id": data.id,
            "name": data.name,
            "label": data.label,
            "alliance": self.get_clan_data_without_alliance(alliance_data=data.alliance)
        }

    @staticmethod
    def add_clan(clan_id: int, name: str, label: str):
        """Данный метод добавляет новый клан в БД"""
        try:
            data = ClansModel.objects.create(
                id=clan_id, name=name, label=label
            )
            data.save()
            logger.info(f"Добавил новый клан. id: {data.id}, name: {data.name}, label: {data.name}")
            return {"id": data.id, "name": data.name, "label": data.name}
        except Exception as _ex:
            logger.error(f"Ошибка при добавления клана. id: {clan_id} name: {name}, label: {label} -> {_ex}")
            return None

    @staticmethod
    def update_clan_data(clan_id: int, name: str, label: str, alliance: Union[int, None]):
        """Данный метод обновляет данные о клане"""
        if alliance:
            try:
                alliance_data = ClansModel.objects.get(pk=alliance)
                logger.info(f"Найдены данные об альянсовом клане: {alliance_data} для клана {name}")
            except ObjectDoesNotExist:
                alliance_data = None
        else:
            alliance_data = None

        try:
            ClansModel.objects.filter(id=clan_id).update(name=name, label=label, alliance=alliance_data)
            logger.info(f"Данные клана №{clan_id} name: {name} успешно обновлены")
            return True
        except Exception as _ex:
            logger.error(f"Ошибка при обновлении данных клана №{clan_id} name: {name} -> {_ex}")
            return False

    def reparse_clan_data(self):
        """Данный метод парсит данные обо всех кланах и обновляет их в БД"""
        parser = ClansParser()
        player_logic = PlayersLogic()

        clans_list_data = parser.pars_clans_data()
        for i, clan in enumerate(clans_list_data):
            logger.info(f"Обрабатываю {i + 1} клан из {len(clans_list_data)}")
            clan["clan_id"] = int(clan["clan_id"])

            self.add_clan(clan_id=clan["clan_id"], name=clan["name"], label=clan["label"])

            clan["alliance"] = parser.get_one_clan_allianse(clan_id=clan["clan_id"])

        for i, clan in enumerate(clans_list_data):
            logger.info("=" * 80)
            logger.info(f"Обработал {i} кланов из {len(clans_list_data)} по данным игроков")
            logger.info("=" * 80)
            player_logic.reparse_one_clan_players(clan_id=clan["clan_id"])

        return {"success": True, "data": "clan data was reparse"}


class PlayersLogic:
    parser = PlayerParser()

    """Логика связанная со взаимодействием с игроками"""
    def reparse_one_clan_players(self, clan_id: int):
        """Данный метод парсит данные всех игроков из одного клана и заносит их в БД/Обновляет существующих"""
        total_list = []
        clan = ClansModel.objects.get(pk=clan_id)
        players_data = self.parser.parse_one_clan_data(clan_id=clan_id, total_list=total_list)
        for player in players_data:
            add = self.add_new_player(in_data=player.model_dump())
            if not add:
                self.update_player_data(in_data=player.model_dump())
        players_id_list = [player.id for player in players_data]
        players_not_in_list = PlayersModel.objects.filter(clan=clan).exclude(id__in=players_id_list).update(clan=None)


    def get_players_data(self, player_filter: dict) -> Union[list, dict, None]:
        """Данный метод извлекает данные об игроках или об одном игроке
        в зависимости от переданных параметров
        """
        voevoda_id = player_filter.get("voevoda_id")
        player_id = player_filter.get("player_id")
        if player_id:
            return self.get_player_data_by_id(player_id=player_id)
        return self.get_player_data_by_filter(player_filter=player_filter, voevoda_id=voevoda_id)

    def get_player_data_by_filter(self, player_filter: dict, voevoda_id: Union[int, None] = None) -> Union[list, None]:
        """Данный метод возвращает данные об игроках по фильтру
        Например id клана и т.п.
        """
        clan_id = player_filter.get("clan_id")
        try:
            data = PlayersModel.objects.filter(clan_id=clan_id)
            return [self.serialize_one_player_data(data=one_data, voevoda_id=voevoda_id) for one_data in data]
        except ObjectDoesNotExist:
            logger.error(f"Не игрока по фильтру: {player_filter}")
            return None

    def get_player_data_by_id(self, player_id: int) -> Union[dict, None]:
        """Извлечение информации об игроке по его ID"""
        try:
            data = PlayersModel.objects.get(pk=player_id)
            logger.info(f"Извлеченные данные об игроке: №{data.id} {data.name}")
            # data.clan = data.clan.id
            return self.serialize_one_player_data(data=data)
        except ObjectDoesNotExist:
            logger.error(f"Не игрок с ID: {player_id}")
            return None

    @staticmethod
    def serialize_one_player_data(data: PlayersModel, voevoda_id: Union[int, None] = None) -> dict:
        if data.clan:
            clan_id = data.clan.id
        else:
            clan_id = None
        person_id = None
        logger.info(f"voevoda_id: {voevoda_id}")
        if voevoda_id:
            try:
                logger.info(f"try. player_id: {data.id} voevoda_id: {voevoda_id}")
                person_data = PersonsModel.objects.get(player_id=data.id, voevoda_id=voevoda_id)
                logger.info(f"Person_data: {person_data}")
                if person_data:
                    person_id = person_data.id
            except ObjectDoesNotExist:
                person_id = None
        return {
            "id": data.id,
            "name": data.name,
            "level": data.level,
            "clan": clan_id,
            "umka_knight": data.umka_knight,
            "umka_necro": data.umka_necro,
            "umka_mag": data.umka_mag,
            "umka_elf": data.umka_elf,
            "umka_barbar": data.umka_barbar,
            "umka_black_elf": data.umka_black_elf,
            "umka_demon": data.umka_demon,
            "umka_dwarf": data.umka_dwarf,
            "umka_step_barb": data.umka_step_barb,
            "umka_pharaon": data.umka_pharaon,
            "gild_hunt": data.gild_hunt,
            "gild_work": data.gild_work,
            "gild_card": data.gild_card,
            "gild_thief": data.gild_thief,
            "gild_ranger": data.gild_ranger,
            "gild_mers": data.gild_mers,
            "gild_tactic": data.gild_tactic,
            "gild_gard": data.gild_gard,
            "gild_seekers": data.gild_seekers,
            "gild_leader": data.gild_leader,
            "gild_blacksmith": data.gild_blacksmith,
            "gild_gunsmith": data.gild_gunsmith,
            "person_id": person_id
        }

    def add_new_player(self, in_data: dict) -> Union[dict, None]:
        """Данный метод заносит нового игрока в БД"""
        try:
            in_data["clan"] = ClansModel.objects.get(pk=in_data["clan"])
            data = PlayersModel.objects.create(**in_data)
            data.save()
            logger.info(f"Добавил нового игрока ID: {in_data['id']} name: {in_data['name']}")
            in_data["clan"] = in_data["clan"].id
            return in_data
        except IntegrityError:
            logger.info(f"Игрок: ID {in_data['id']} name: {in_data['name']} уже есть в БД")
        except Exception as _ex:
            logger.error(f"Ошибка при добавления игрока: ID {in_data['id']} name: {in_data['name']} -> {_ex}")

    def update_player_data(self, in_data: dict) -> bool:
        """Данный метод обновляет данные игрока по его ID"""
        try:
            player_id = in_data.pop("id")
            if in_data["clan"]:
                in_data["clan"] = ClansModel.objects.get(pk=in_data["clan"])

            PlayersModel.objects.filter(id=player_id).update(**in_data)
            logger.info(f"Обновил данные по игроку: {player_id} {in_data['name']}")
            return True
        except Exception as _ex:
            logger.info(f"Ошибка при обновлении данных игрока: {in_data} -> {_ex}")
            return False


class VoevodaLogic(Redis):
    """Логика взаимодействия воеводы с интерфейсом"""

    def update_voevoda_data(self, voevoda_id: int, data: dict) -> bool:
        """Данный метод обновляет данные воеводы по его ID"""
        try:
            VoevodaModel.objects.filter(id=voevoda_id).update(**data)
            logger.info(f"Данные воеводы: {voevoda_id} успешно обновлены")
            return True
        except Exception as _ex:
            logger.error(f"Ошибка при обновлении данных воеводы: {voevoda_id} -> {_ex}")
            return False

    def connect_voevoda_telegram(self, key: int, telegram_id: int, telegram_username: str) -> bool:
        """Данный метод подключает телеграм аккаунт воеводы к системе
        Args:
            key: ключ подключения, данный воеводе
            telegram_id: идентификатор аккаунта из телеграм
            telegram_username: username аккаунта телеграм
        """
        check_data_by_key = self.get_data_from_cache(key=f"voevoda:{key}", data_class=schemas.VoevodaRegSchem)
        if not check_data_by_key:
            logger.error(f"По ключу: voevoda:{key} ничего в КЭШе не найдено")
            return False

        update = self.update_voevoda_data(
            voevoda_id=check_data_by_key.id,
            data={"telegram_id": telegram_id, "telegram_username": telegram_username}
        )
        if not update:
            logger.error(f"Ошибка при обновлении данных воеводы: {check_data_by_key.id}")
            return False
        else:
            self.delete_data_from_cache(key=f"voevoda:{key}")
            return True

    def get_player_register_key(self, player_id: int, voevoda_id: int, role: int = 100) -> int:
        """Данный метод метод создает в КЭШе значение с ключем
        для добавления добавления нового игрока к воеводе
        """
        data = schemas.PersonRegisterSchem(
            player_id=player_id,
            voevoda_id=voevoda_id,
            role=role
        )
        return self.create_connect_key(sub_key="person", data=data)


class PresetsLogic(Redis):
    """Логический класс для работы с данными пресетов"""

    def get_presets_data(self, data_filter: dict) -> Union[list, dict, None]:
        """Данный метод извлекает данные об пресетах по фильтру
        """
        preset_id = data_filter.get("preset_id")
        if preset_id:
            return self.get_preset_data_by_id(preset_id=preset_id)
        return self.get_preset_data_by_filter(preset_filter=data_filter)

    def get_preset_data_by_filter(self, preset_filter: dict) -> Union[list, None]:
        """Данный метод возвращает данные о пресете по фильтру
        """
        try:
            data = PresetsModel.objects.filter(voevoda_id=preset_filter["voevoda_id"])
            return [self.serialize_one_preset_data(data=one_data) for one_data in data]
        except ObjectDoesNotExist:
            logger.error(f"Нет пресетов по фильтру: {preset_filter}")
            return None

    def get_preset_data_by_id(self, preset_id: int) -> Union[dict, None]:
        """Извлечение информации о пресете по его ID"""
        try:
            data = PresetsModel.objects.get(pk=preset_id)
            logger.info(f"Извлеченные данные об пресете: №{data.id} {data.name}")
            return self.serialize_one_preset_data(data=data)
        except ObjectDoesNotExist:
            logger.error(f"Нет пресета с id: {preset_id}")
            return None

    @staticmethod
    def serialize_one_preset_data(data: PresetsModel):
        """Сериализуем данные модели в нужный вид"""
        return {
            "id": data.id,
            "voevoda_id": data.voevoda_id.id,
            "fraction": data.fraction,
            "name": data.name,
            "description": data.description
        }

    @staticmethod
    def add_new_preset(in_data: dict) -> Union[dict, None]:
        """Данный метод заносит нового игрока в БД"""
        try:
            # добавляем новый пресет
            in_data["voevoda_id"] = VoevodaModel.objects.get(pk=in_data["voevoda_id"])
            data = PresetsModel.objects.create(**in_data)
            data.save()
            logger.info(f"Добавил новый пресет: {in_data}")
            in_data["voevoda_id"] = in_data["voevoda_id"].id

            # извлекаем всех игроков относящихся к воеводе и добавляем им данный пресет
            persons_list = PersonsLogic().get_person_data(filter={"voevoda_id": in_data["voevoda_id"], "person_id": None})
            logger.info(f"Список игроков воеводы {data.voevoda_id.id}: {persons_list}")
            for person in persons_list:
                PersonPresetLogic().add_new_person_preset(in_data={
                    "person_id": person["id"],
                    "preset_id": data.id
                })
            return in_data
        except IntegrityError:
            logger.info(f"Пресет уже существует")
        except Exception as _ex:
            logger.error(f"Ошибка при добавления пресета {in_data} -> {_ex}")

    @staticmethod
    def update_preset_data(in_data: dict) -> bool:
        """Данный метод обновляет данные пресета"""
        try:
            preset_id = in_data.pop("preset_id")
            PresetsModel.objects.filter(id=preset_id).update(**in_data)
            logger.info(f"Обновил данные пресета: {in_data}")
            return True
        except Exception as _ex:
            logger.info(f"Ошибка при обновлении данных пресета: {in_data} -> {_ex}")
            return False

    @staticmethod
    def delete_preset_data(preset_id: int) -> bool:
        """Данный метод удаляет данные пресета"""
        try:
            obj = PresetsModel.objects.get(id=preset_id)
            obj.delete()
            logger.info(f"Обновил данные пресета: {preset_id}")
            return True
        except Exception as _ex:
            logger.info(f"Ошибка при удалении пресета: {preset_id} -> {_ex}")
            return False


class PersonsLogic(Redis):
    """Класс с бизнес логикой взаимодействия с данными
    живых игроков
    """

    def connect_person_telegram(self, key: int, telegram_id: int, telegram_username: str) -> Union[dict, None]:
        """Данный метод подключает телеграм аккаунт игрока к системе за определенным воеводой
        Args:
            key: ключ подключения, данный воеводой
            telegram_id: идентификатор аккаунта из телеграм
            telegram_username: username аккаунта телеграм
        """
        check_data_by_key = self.get_data_from_cache(key=f"person:{key}", data_class=schemas.PersonRegisterSchem)
        if not check_data_by_key:
            logger.error(f"По ключу: person:{key} ничего в КЭШе не найдено")
            return None

        # добавляем нового персонажа
        new_person = self.add_new_person(in_data={
            "role": check_data_by_key.role,
            "telegram_id": telegram_id,
            "telegram_username": telegram_username,
            "player_id": check_data_by_key.player_id,
            "voevoda_id": check_data_by_key.voevoda_id,
        })
        self.delete_data_from_cache(key=f"person:{key}")

        # извлекаем все пресеты, относящиеся к воеводе
        presets_list = PresetsLogic().get_presets_data(data_filter={"voevoda_id": check_data_by_key.voevoda_id})

        for preset in presets_list:
            PersonPresetLogic().add_new_person_preset(in_data={
                "person_id": new_person["id"],
                "preset_id": preset["id"]
            })

        return new_person

    def get_person_data(self, filter: dict):
        """Получить данные игрока"""
        person_id = filter.pop("person_id")
        if person_id:
            return self.get_person_data_by_id(person_id=person_id)
        return self.get_person_data_by_filter(filter=filter)

    def get_person_data_by_id(self, person_id: int):
        try:
            data = PersonsModel.objects.get(pk=person_id)
            players_presets_list = PersonPresetLogic().get_person_presets(person_id=data.id)
            logger.info(f"Извлеченные данные об игроке: {data.player_id} {data.voevoda_id}")
            return self.serialize_one_person_data(data=data, presets_list=players_presets_list)
        except ObjectDoesNotExist:
            logger.error(f"Игрок с ID: {person_id} не обнаружен")
            return None

    def get_person_data_by_filter(self, filter: dict) -> Union[list, None]:
        """Данный метод возвращает данные об игроке по фильтру
        """
        try:
            data = PersonsModel.objects.filter(**filter)
            return [self.serialize_one_person_data(
                data=one_data,
                presets_list=PersonPresetLogic().get_person_presets(person_id=one_data.id)
            ) for one_data in data]
        except ObjectDoesNotExist:
            logger.error(f"Нет игроков по фильтру: {filter}")
            return None

    def serialize_one_person_data(self, data: PersonsModel, presets_list: Union[list, None] = None):
        return {
            "id": data.id,
            "role": data.role,
            "telegram_id": data.telegram_id,
            "telegram_username": data.telegram_username,
            "voevoda_id": data.voevoda_id.id,
            "activity": data.activity,
            "comment": data.comment,
            "stats": PlayersLogic().serialize_one_player_data(data=data.player_id),
            "presets": presets_list
        }

    @staticmethod
    def add_new_person(in_data: dict) -> Union[dict, None]:
        """Данный метод заносит нового игрока в БД"""
        try:
            in_data["voevoda_id"] = VoevodaModel.objects.get(pk=in_data["voevoda_id"])
            in_data["player_id"] = PlayersModel.objects.get(pk=in_data["player_id"])
            data = PersonsModel.objects.create(**in_data)
            data.save()
            logger.info(f"Добавил нового игрока: {in_data}")
            in_data["voevoda_id"] = in_data["voevoda_id"].id
            in_data["player_id"] = in_data["player_id"].id
            in_data["id"] = data.id
            return in_data
        except IntegrityError:
            logger.info(f"Игрок уже существует")
        except Exception as _ex:
            logger.error(f"Ошибка при добавления Игрока {in_data} -> {_ex}")

    @staticmethod
    def update_person_data(in_data: dict) -> bool:
        """Данный метод обновляет данные пресета"""
        try:
            preset_id = in_data.pop("person_id")
            PersonsModel.objects.filter(id=preset_id).update(**in_data)
            logger.info(f"Обновил данные игрока: {in_data}")
            return True
        except Exception as _ex:
            logger.info(f"Ошибка при обновлении данных игрока: {in_data} -> {_ex}")
            return False

    @staticmethod
    def delete_person_data(person_id: int) -> bool:
        """Данный метод удаляет данные пресета"""
        try:
            obj = PersonsModel.objects.get(id=person_id)
            obj.delete()
            logger.info(f"Удалил игрока: {person_id}")
            return True
        except Exception as _ex:
            logger.info(f"Ошибка при удалении игрока: {person_id} -> {_ex}")
            return False


class PersonPresetLogic(Redis):
    """Логика работы с пресетами персональными за игроками"""

    def get_person_presets(self, person_id: int):
        """Извлекаем список пресетов однового игрока"""
        try:
            data = PersonPresetModel.objects.filter(person_id=person_id)
            return [self.serialize_one_person_preset_data(data=one_data) for one_data in data]
        except ObjectDoesNotExist:
            logger.error(f"Не пресетов для игрока по person_id: {person_id}")
            return None

    def serialize_one_person_preset_data(self, data: PersonPresetModel):
        return {
            "id": data.id,
            "person_id": data.person_id.id,
            "preset": PresetsLogic().serialize_one_preset_data(data=data.preset_id),
            "play_preset": data.play_preset
        }

    @staticmethod
    def add_new_person_preset(in_data: dict):
        try:
            in_data["person_id"] = PersonsModel.objects.get(pk=in_data["person_id"])
            in_data["preset_id"] = PresetsModel.objects.get(pk=in_data["preset_id"])
            data = PersonPresetModel.objects.create(**in_data)
            data.save()
            logger.info(f"Добавил новый пресет для игрока: {in_data}")
            in_data["person_id"] = in_data["person_id"].id
            in_data["preset_id"] = in_data["preset_id"].id
            return in_data
        except Exception as _ex:
            logger.error(f"Ошибка при добавления пресета игроку {in_data} -> {_ex}")

    @staticmethod
    def update_person_preset_data(in_data: dict) -> bool:
        try:
            person_preset_id = in_data.pop("person_preset_id")
            PersonPresetModel.objects.filter(id=person_preset_id).update(**in_data)
            logger.info(f"Обновил данные: {in_data}")
            return True
        except Exception as _ex:
            logger.info(f"Ошибка при обновлении данных: {in_data} -> {_ex}")
            return False

    @staticmethod
    def delete_person_presets_data(in_data: dict) -> bool:
        try:
            PersonPresetModel.objects.filter(**in_data).delete()
            logger.info(f"Удалил данные: {in_data}")
            return True
        except Exception as _ex:
            logger.info(f"Ошибка при удалении данных: {in_data} -> {_ex}")
            return False


class FightsLogic(Redis):
    def get_fights(self, in_data: dict):
        """Извлечения данных по боям"""
        fight_id = in_data.pop("fight_id")
        if fight_id:
            return self.get_fight_by_id(fight_id=fight_id)
        return self.get_fight_by_filter(filter=in_data)

    def get_fight_by_id(self, fight_id: int):
        """Извлечение данных по одному бою"""
        try:
            data = FightsModel.objects.get(pk=fight_id)
            return self.serialize_one_fight_data(data=data)
        except ObjectDoesNotExist:
            logger.error(f"Бой с ID: {fight_id} не обнаружен")
            return None

    def get_fight_by_filter(self, filter: dict):
        """Извлечение данных о группе поев по фильтру"""
        try:
            data = FightsModel.objects.filter(**filter)
            return [self.serialize_one_fight_data(data=one_data) for one_data in data]
        except ObjectDoesNotExist:
            logger.error(f"Нет данных о боях по фильтру: {filter}")
            return None

    @staticmethod
    def serialize_one_fight_data(data: FightsModel):
        """Сериализация данных об одном бое"""
        return {
            "id": data.id,
            "name": data.name,
            "type": data.type,
            "date": data.date.timestamp(),
            "voevoda_id": data.voevoda_id.id,
            "attack_1_pers": PlayersLogic().serialize_one_player_data(data=data.attack_1_pers),
            "attack_2_pers": PlayersLogic().serialize_one_player_data(data=data.attack_2_pers),
            "defence_1_pers": PlayersLogic().serialize_one_player_data(data=data.defence_1_pers),
            "defence_2_pers": PlayersLogic().serialize_one_player_data(data=data.defence_2_pers),
            "attack_1_pers_preset": PresetsLogic().serialize_one_preset_data(data=data.attack_1_pers_preset),
            "attack_2_pers_preset": PresetsLogic().serialize_one_preset_data(data=data.attack_2_pers_preset),
            "defence_1_pers_preset": PresetsLogic().serialize_one_preset_data(data=data.defence_1_pers_preset),
            "defence_2_pers_preset": PresetsLogic().serialize_one_preset_data(data=data.defence_2_pers_preset),
            "result": data.result,
            "description": data.description
        }

    def add_fight(self, in_data: dict):
        """Добавление нового боя"""
        try:
            # данные воеводы
            in_data["voevoda_id"] = VoevodaModel.objects.get(pk=in_data["voevoda_id"])
            in_data["date"] = datetime.datetime.fromtimestamp(in_data["date"])

            # данные стороны атаки
            in_data["attack_1_pers"] = PlayersModel.objects.get(pk=in_data["attack_1_pers"])
            in_data["attack_2_pers"] = PlayersModel.objects.get(pk=in_data["attack_2_pers"])
            in_data["attack_1_pers_preset"] = PresetsModel.objects.get(pk=in_data["attack_1_pers_preset"])
            in_data["attack_2_pers_preset"] = PresetsModel.objects.get(pk=in_data["attack_2_pers_preset"])

            # данные стороны защиты
            in_data["defence_1_pers"] = PlayersModel.objects.get(pk=in_data["defence_1_pers"])
            in_data["defence_2_pers"] = PlayersModel.objects.get(pk=in_data["defence_2_pers"])
            in_data["defence_1_pers_preset"] = PresetsModel.objects.get(pk=in_data["defence_1_pers_preset"])
            in_data["defence_2_pers_preset"] = PresetsModel.objects.get(pk=in_data["defence_2_pers_preset"])

            data = FightsModel.objects.create(**in_data)
            data.save()
            logger.info(f"Добавил новый бой: {in_data}")
            return self.serialize_one_fight_data(data=data)
        except Exception as _ex:
            logger.error(f"Ошибка при добавления нового боя {in_data} -> {_ex}")

    @staticmethod
    def update_fight(in_data: dict):
        """Обновление данных о бое"""
        try:
            fight_id = in_data.pop("fight_id")
            FightsModel.objects.filter(id=fight_id).update(**in_data)
            logger.info(f"Обновил данные: {in_data}")
            return True
        except Exception as _ex:
            logger.info(f"Ошибка при обновлении данных: {in_data} -> {_ex}")
            return False

    @staticmethod
    def delete_fight(fight_id: int):
        """Удаление данных о бое"""
        try:
            FightsModel.objects.filter(id=fight_id).delete()
            logger.info(f"Удалил данные о бое: {fight_id}")
            return True
        except Exception as _ex:
            logger.info(f"Ошибка при удалении данных о бое: {fight_id} -> {_ex}")
            return False


class FightEventLogic(Redis):
    def get_events(self, in_data: dict):
        """Извлечения данных по боям
        """
        event_id = in_data.pop("event_id")
        if event_id:
            return self.get_event_by_id(event_id=event_id)
        return self.get_event_by_filter(filter=in_data)

    def get_event_by_id(self, event_id: int):
        """Извлечение данных по одному бою
        """
        try:
            data = FightEventModel.objects.get(pk=event_id)
            return self.serialize_one_event_data(data=data)
        except ObjectDoesNotExist:
            logger.error(f"Ивент с ID: {event_id} не обнаружен")
            return None

    def get_event_by_filter(self, filter: dict):
        """Извлечение данных о ивентах по фильтру
        """
        try:
            data = FightEventModel.objects.filter(**filter)
            return [self.serialize_one_event_data(data=one_data) for one_data in data]
        except ObjectDoesNotExist:
            logger.error(f"Нет данных об ивентах по фильтру: {filter}")
            return None

    @staticmethod
    def serialize_one_event_data(data: FightEventModel):
        """Сериализация данных об одном бое"""
        return {
            "id": data.id,
            "name": data.name,
            "type": data.type,
            "date": data.date.timestamp(),
            "voevoda_id": data.voevoda_id.id,
            "enemy": ClansLogic().serialize_one_clan_data(data.enemy),
            "state": data.state
        }

    def add_event(self, in_data: dict):
        """Добавление нового ивента"""
        try:
            # данные воеводы
            in_data["voevoda_id"] = VoevodaModel.objects.get(pk=in_data["voevoda_id"])
            in_data["date"] = datetime.datetime.fromtimestamp(in_data["date"] / 1000)
            in_data["enemy"] = ClansModel.objects.get(pk=in_data["enemy"])

            data = FightEventModel.objects.create(**in_data)
            data.save()
            logger.info(f"Добавил новый ивент: {in_data}")
            return self.serialize_one_event_data(data=data)
        except Exception as _ex:
            logger.error(f"Ошибка при добавления нового Ивента {in_data} -> {_ex}")

    @staticmethod
    def update_event(in_data: dict):
        """Обновление данных о бое
        -
        """
        try:
            event_id = in_data.pop("event_id")
            FightEventModel.objects.filter(id=event_id).update(**in_data)
            logger.info(f"Обновил данные: {in_data}")
            return True
        except Exception as _ex:
            logger.info(f"Ошибка при обновлении данных: {in_data} -> {_ex}")
            return False


class InviteLogic(Redis):
    def get_invites(self, in_data: dict):
        """Извлечения данных по боям
        """
        invite_id = in_data.pop("invite_id")
        if invite_id:
            return self.get_invite_by_id(invite_id=invite_id)
        return self.get_invite_by_filter(filter=in_data)

    def get_invite_by_id(self, invite_id: int):
        """Извлечение данных по одному бою
        """
        try:
            data = InviteModel.objects.get(pk=invite_id)
            return self.serialize_one_invite_data(data=data)
        except ObjectDoesNotExist:
            logger.error(f"Приглашение с ID: {invite_id} не обнаружен")
            return None

    def get_invite_by_filter(self, filter: dict):
        """Извлечение данных о ивентах по фильтру
        """
        try:
            filter["event_id"] = FightEventModel.objects.get(pk=filter["event_id"])
            data = InviteModel.objects.filter(**filter)
            return [self.serialize_one_invite_data(data=one_data) for one_data in data]
        except ObjectDoesNotExist:
            logger.error(f"Нет данных об ивентах по фильтру: {filter}")
            return None

    @staticmethod
    def serialize_one_invite_data(data: InviteModel):
        """Сериализация данных об одном бое"""
        return {
            "id": data.id,
            "date": data.date.timestamp(),
            "event_id": FightEventLogic().serialize_one_event_data(data=data.event_id),
            "person_id": PersonsLogic().serialize_one_person_data(data=data.person_id),
            "state": data.state
        }

    def add_invite(self, in_data: dict):
        """Добавление нового ивента"""
        try:
            # данные воеводы
            in_data["event_id"] = FightEventModel.objects.get(pk=in_data["event_id"])
            in_data["person_id"] = PersonsModel.objects.get(pk=in_data["person_id"])

            data = InviteModel.objects.create(**in_data)
            data.save()
            logger.info(f"Добавил новое приглашение на ивент: {in_data}")
            return self.serialize_one_invite_data(data=data)
        except Exception as _ex:
            logger.error(f"Ошибка при добавления нового приглашения на ивент {in_data} -> {_ex}")

    @staticmethod
    def update_invite(in_data: dict):
        """Обновление данных об приглашении на виент"""
        try:
            invite_id = in_data.pop("invite_id")
            InviteModel.objects.filter(id=invite_id).update(**in_data)
            logger.info(f"Обновил данные: {in_data}")
            return True
        except Exception as _ex:
            logger.info(f"Ошибка при обновлении данных: {in_data} -> {_ex}")
            return False
