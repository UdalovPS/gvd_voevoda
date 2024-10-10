# voevoda_app MODELS

from django.db import models
from django.utils import timezone


class ClansModel(models.Model):
    """Модель с кланами из Героев Войны и Денег"""
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50, verbose_name="Название")
    label = models.CharField(verbose_name="Значек", max_length=50)
    alliance = models.ForeignKey("ClansModel", null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Альянс")

    def __str__(self):
        return f"№{self.id} - {self.name}"

    class Meta:
        verbose_name_plural = "Кланы"


class PlayersModel(models.Model):
    """Таблица с чемпионами из Героев Войны и Денег"""
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50, verbose_name="Ник")
    level = models.IntegerField(default=1, verbose_name="Уровень")
    clan = models.ForeignKey("ClansModel", null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Клан")

    umka_knight = models.IntegerField(default=1, verbose_name="Рыцарь")
    umka_necro = models.IntegerField(default=1, verbose_name="Некромант")
    umka_mag = models.IntegerField(default=1, verbose_name="Маг")
    umka_elf = models.IntegerField(default=1, verbose_name="Эльф")
    umka_barbar = models.IntegerField(default=1, verbose_name="Варвар")
    umka_black_elf = models.IntegerField(default=1, verbose_name="Темный эльф")
    umka_demon = models.IntegerField(default=1, verbose_name="Демон")
    umka_dwarf = models.IntegerField(default=1, verbose_name="Гном")
    umka_step_barb = models.IntegerField(default=1, verbose_name="Степной варвар")
    umka_pharaon = models.IntegerField(default=1, verbose_name="Фараон")

    gild_hunt = models.IntegerField(default=1, verbose_name="Гильдия Охотников")
    gild_work = models.IntegerField(default=1, verbose_name="Гильдия Рабочих")
    gild_card = models.IntegerField(default=1, verbose_name="Гильдия Картежников")
    gild_thief = models.IntegerField(default=1, verbose_name="Гильдия Воров")
    gild_ranger = models.IntegerField(default=1, verbose_name="Гильдия Рейнджеров")
    gild_mers = models.IntegerField(default=1, verbose_name="Гильдия Наемников")
    gild_tactic = models.IntegerField(default=1, verbose_name="Гильдия Тактиков")
    gild_gard = models.IntegerField(default=1, verbose_name="Гильдия Стражей")
    gild_seekers = models.IntegerField(default=1, verbose_name="Гильдия Искателей")
    gild_leader = models.IntegerField(default=1, verbose_name="Гильдия Лидеров")
    gild_blacksmith = models.IntegerField(default=1, verbose_name="Гильдия Кузнецов")
    gild_gunsmith = models.IntegerField(default=1, verbose_name="Гильдия Оружейников")

    def __str__(self):
        return f"№{self.id} - {self.name}"

    class Meta:
        verbose_name_plural = "Персонажи"


class VoevodaModel(models.Model):
    """Класс отвечающий за данные самого воеводы, который является админом для своего клана"""
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, verbose_name="Имя", unique=True)
    telegram_id = models.BigIntegerField(null=True, blank=True)
    telegram_username = models.CharField(max_length=100, null=True, blank=True, unique=True)
    phone = models.CharField(max_length=20)
    clan_id = models.ForeignKey("ClansModel", null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Клан")
    access_date = models.DateTimeField(auto_now_add=True)
    tmp_code = models.IntegerField(null=True, blank=True, default=None)

    def __str__(self):
        return f"№{self.id} - {self.name}"

    class Meta:
        verbose_name_plural = "Воеводы"


class PersonsModel(models.Model):
    """Класс отвечающий за данные живых игроков подключенных к системе"""
    ROTE_CHOICES = [
        (1, "Воевода"),
        (2, "Помощник воеводы"),
        (100, "Игрок")
    ]

    id = models.AutoField(primary_key=True)
    role = models.IntegerField(default=100, choices=ROTE_CHOICES, verbose_name="Роль")
    telegram_id = models.BigIntegerField()
    telegram_username = models.CharField(max_length=100, unique=True)
    player_id = models.ForeignKey("PlayersModel", null=True, blank=True, on_delete=models.CASCADE, verbose_name="Игровой персонаж")
    voevoda_id = models.ForeignKey("VoevodaModel", null=True, blank=True, on_delete=models.CASCADE, verbose_name="Закреплен за воеводой")
    activity = models.BooleanField(default=False, verbose_name="Активность")
    comment = models.TextField(null=True, blank=True, verbose_name="Комментарий к игроку")

    def __str__(self):
        return f"{self.role} - {self.player_id} - {self.voevoda_id}"

    class Meta:
        verbose_name_plural = "Игроки"


class PresetsModel(models.Model):
    FRACTION_CHOICES = [
        (0, "Рыцарь"),
        (1, "Некромант"),
        (2, "Маг"),
        (3, "Эльф"),
        (4, "Варвар"),
        (5, "Темный эльф"),
        (6, "Демон"),
        (7, "Гном"),
        (8, "Степной варвар"),
        (9, "Фараон"),
    ]

    """Класс с пресетами персональными для каждого воеводы"""
    id = models.AutoField(primary_key=True)
    voevoda_id = models.ForeignKey("VoevodaModel", null=True, blank=True, on_delete=models.CASCADE,
                                   verbose_name="Закреплен за воеводой")
    fraction = models.IntegerField(choices=FRACTION_CHOICES)
    name = models.CharField(max_length=50, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")

    def __str__(self):
        return f"{self.name} - {self.voevoda_id}"

    class Meta:
        verbose_name_plural = "Пресеты"


class PersonPresetModel(models.Model):
    """Данные о том, играет ли живой за пресет или нет"""
    id = models.AutoField(primary_key=True)
    person_id = models.ForeignKey("PersonsModel", null=True, blank=True, on_delete=models.CASCADE,
                                  verbose_name="Игрок")
    preset_id = models.ForeignKey("PresetsModel", null=True, blank=True, on_delete=models.CASCADE,
                                  verbose_name="Пресет")
    play_preset = models.BooleanField(default=False, verbose_name="Играет за пресет?")

    class Meta:
        verbose_name_plural = "Пресеты игроков"


class FightsModel(models.Model):
    """Модель описывающая бои"""
    FIGHT_TYPE_CHOICES = [
        (1, "Атака"),
        (2, "Защита"),
    ]
    RESULT_CHOICER = [
        (1, "Победа стороны атаки"),
        (2, "Победа стороны защиты"),
    ]
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, verbose_name="Название")
    type = models.IntegerField(choices=FIGHT_TYPE_CHOICES, default=1, verbose_name="Тип боя")
    date = models.DateTimeField(default=timezone.now, verbose_name="Дата")
    voevoda_id = models.ForeignKey("VoevodaModel", null=True, blank=True, on_delete=models.SET_NULL,
                                   verbose_name="Воевода")
    attack_1_pers = models.ForeignKey("PlayersModel", null=True, blank=True, on_delete=models.SET_NULL,
                                        verbose_name="1-й игрок атаки", related_name="attack_1_fights")
    attack_2_pers = models.ForeignKey("PlayersModel", null=True, blank=True, on_delete=models.SET_NULL,
                                        verbose_name="2-й игрок атаки", related_name="attack_2_fights")
    defence_1_pers = models.ForeignKey("PlayersModel", null=True, blank=True, on_delete=models.SET_NULL,
                                        verbose_name="1-й игрок защиты", related_name="defence_1_fights")
    defence_2_pers = models.ForeignKey("PlayersModel", null=True, blank=True, on_delete=models.SET_NULL,
                                        verbose_name="2-й игрок защиты", related_name="defence_2_fights")
    attack_1_pers_preset = models.ForeignKey("PresetsModel", null=True, blank=True, on_delete=models.SET_NULL,
                                        verbose_name="пресет 1-го игрока атаки", related_name="attack_1_presets")
    attack_2_pers_preset = models.ForeignKey("PresetsModel", null=True, blank=True, on_delete=models.SET_NULL,
                                        verbose_name="пресет 2-го игрока атаки", related_name="attack_2_presets")
    defence_1_pers_preset = models.ForeignKey("PresetsModel", null=True, blank=True, on_delete=models.SET_NULL,
                                        verbose_name="пресет 1-го игрока защиты", related_name="defence_1_presets")
    defence_2_pers_preset = models.ForeignKey("PresetsModel", null=True, blank=True, on_delete=models.SET_NULL,
                                        verbose_name="пресет 2-го игрока защиты", related_name="defence_2_presets")
    result = models.IntegerField(choices=RESULT_CHOICER, verbose_name="Результат")
    description = models.TextField(verbose_name="Комментарий")

    def __str__(self):
        return f"{self.name} - {self.voevoda_id}"

    class Meta:
        verbose_name_plural = "Битвы"


class FightEventModel(models.Model):
    """Модель с ивентами. (одним из ивентов является собрание на бой)"""
    STATE_CHOICER = [
        (1, "Первоначальный сбор"),
        (2, "Выбор бойцов"),
        (3, "Идет бой"),
        (4, "Завершен"),
    ]
    FIGHT_TYPE_CHOICES = [
        (1, "Атака"),
        (2, "Защита"),
    ]

    id = models.AutoField(primary_key=True)
    date = models.DateTimeField(default=timezone.now, verbose_name="Дата")
    name = models.CharField(max_length=50, verbose_name="Название")
    type = models.IntegerField(choices=FIGHT_TYPE_CHOICES, default=1, verbose_name="Тип боя")
    voevoda_id = models.ForeignKey("VoevodaModel", null=True, blank=True, on_delete=models.CASCADE,
                                   verbose_name="Воевода")
    enemy = models.ForeignKey("ClansModel", null=True, blank=True, on_delete=models.SET_NULL,
                                   verbose_name="Противник")
    state = models.IntegerField(choices=STATE_CHOICER, default=1)

    def __str__(self):
        return f"{self.name} - {self.voevoda_id}"

    class Meta:
        verbose_name_plural = "Боевые Ивенты"


class InviteModel(models.Model):
    """Приглашения на ивент"""
    STATE_CHOICES = [
        (1, "Отправлено"),
        (2, "Принято"),
        (3, "Отказ"),
        (4, "Выбран на бой"),
    ]

    id = models.AutoField(primary_key=True)
    date = models.DateTimeField(default=timezone.now, verbose_name="Дата")
    event_id = models.ForeignKey("FightEventModel", null=True, blank=True,
                                 on_delete=models.CASCADE, verbose_name="Ивент")
    person_id = models.ForeignKey("PersonsModel", null=True, blank=True,
                                 on_delete=models.CASCADE, verbose_name="Игрок")
    state = models.IntegerField(choices=STATE_CHOICES, default=1)

    def __str__(self):
        return f"{self.event_id} - {self.person_id}"

    class Meta:
        verbose_name_plural = "Приглашение на ивент"