from random import randint
from typing import Union, List
import logging
from pathlib import Path
import time

from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup, element
from fake_useragent import UserAgent

logger = logging.getLogger(__name__)



class PlayerSchem(BaseModel):
    id: int
    name: str
    level: int
    clan: int

    umka_knight: int
    umka_necro: int
    umka_mag: int
    umka_elf: int
    umka_barbar: int
    umka_black_elf: int
    umka_demon: int
    umka_dwarf: int
    umka_step_barb: int
    umka_pharaon: int

    gild_hunt: int
    gild_work: int
    gild_card: int
    gild_thief: int
    gild_ranger: int
    gild_mers: int
    gild_tactic: int
    gild_gard: int
    gild_seekers: int
    gild_leader: int
    gild_blacksmith: int
    gild_gunsmith: int


class BaseParser:
    headers = {
        "User-Agent": UserAgent().random,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8"
    }
    def get_data(self, url: str):
        """Данный метод данные посредством запроса"""
        print(f"Запрашиваю данные по URL: {url}")
        response = requests.get(url=url, headers=self.headers, allow_redirects=True)
        print(f"Данные по URL: {url} -> пришли")
        return response.text

    def save_page(self, data: Union[str, bytes], name: str = "index.html", type: int = 1):
        """Сервисный метод для сохранения html страницы"""
        if type == 1:
            with open(name, "w") as file:
                file.write(data)
        else:
            with open(name, "wb") as file:
                file.write(data)

    def open_page(self, file_path: str = "index.html"):
        with open(file_path) as file:
            src = file.read()
        return src


class ClansParser(BaseParser):

    def get_data(self, url: str, type: int = 1):
        """Данный метод данные посредством запроса"""
        print(f"Запрашиваю данные по URL: {url}")
        response = requests.get(url=url, headers=self.headers, allow_redirects=True)
        print(f"Данные по URL: {url} -> пришли")
        if type == 1:
            return response.text
        else:
            return response.content

        # self.save_page(data=response.text)

        # data = self.open_page()
        #
        # return data

    def pars_clans_data(self) -> list:
        """Данный метод парсит данные обо всех кланах и возвращает из в виде списка словарей"""
        # print(os.getcwd())
        # print(Path(__file__).resolve().parent.parent)
        data = self.get_data(url="https://daily.heroeswm.ru/bk")

        soup = BeautifulSoup(data, "lxml")

        clans = soup.find("table", class_="tab").find("tbody").find_all("tr")

        keys = ['clan_id', 'label', 'name']

        clans_data_list = []
        logger.info(f"Необходимой распарсить информацию о {len(clans)} кланах")
        for clan in clans:
            one_clan_data = clan.find_all("td")
            # print(one_clan_data)
            one_clan_list_data = []
            for value in one_clan_data:
                if value.find("img"):
                    one_clan_list_data.append(value.find("img")["src"])
                else:
                    one_clan_list_data.append(value.text)
            clans_data_list.append({key: value for key, value in zip(keys, one_clan_list_data)})
        return clans_data_list

    def get_one_clan_allianse(self, clan_id: int) -> Union[int, None]:
        """Данный метод парсит данные об одном клане с сайта ГВД"""

        # формируем ссылку по которой обращаемся к клану
        url = f"https://www.heroeswm.ru/clan_info.php?id={clan_id}"

        # непосредственно делаем запрос чтобы спасить данные о клане
        response = requests.get(url=url, headers=self.headers)

        # self.save_page(data=response.text, name=f"clan_{clan_id}.html")
        # data = self.open_page(file_path=f"clan_{clan_id}.html")

        soup = BeautifulSoup(response.text, "lxml")
        data = soup.find_all("a", class_="pi")
        for i in data:
            allians_clan_name = i.find("b")
            if allians_clan_name:
                logger.info(f"Клан №{clan_id} находится в альянсе №{allians_clan_name.text.split()[0][1:]}")
                return allians_clan_name.text.split()[0][1:]
        logger.info(f"Клан №{clan_id} находится без альянса")

    def save_give(self, url: str, path: str = Path(__file__).resolve().parent.parent):
        """
        Скачиваем гифку относящуюся к определенному клану и
        сохраняем ее в БД
        Сохраняет гифку закрепленную за определенным кланом
        НЕ НУЖНЫЙ МЕТОД
        """
        data = self.get_data(url=url, type=2)
        name = url.split("/")[-1].split("?")[0]
        self.save_page(data=data, name=f"{path}/static/voevoda_app/clans/{name}", type=2)


class PlayerParser(BaseParser):
    """Класс для парсинга данных об игроках"""

    base_url = "https://daily.heroeswm.ru/players/l/5n/bc/"

    def parse_one_clan_data(self, clan_id: int, page: int = 1, total_list = []) -> List[PlayerSchem]:
        """Данный метод парсит всех игроков из боевого клана под номером clan_id"""
        one_page_data = self.parse_one_page(clan_id=clan_id, page=page)
        time.sleep(randint(1, 3))
        if one_page_data is not None:
            total_list.extend(one_page_data)
            return self.parse_one_clan_data(clan_id=clan_id, page=page + 1, total_list=total_list)
        else:
            return total_list


    def parse_one_page(self, clan_id: int, page: int = 1) -> Union[List[PlayerSchem], None]:
        """Данный метод парсит данные об игроках из боевого клана с одной страницы
        Args:
            clan_id: идентификатор боевого клана
            page: страница (не более 50 игроков на одной странице)
        """
        url = self.base_url + str(clan_id) + "/p/" + str(page)
        html_data = self.get_data(url=url)
        # html_data = self.open_page(file_path=f"k{clan_id}_p{page}.html")
        # self.save_page(data=one_page_data, name=f"k{clan_id}_p{page}.html")

        soup = BeautifulSoup(html_data, "lxml")

        # получаем html страницу с данные о героях
        all_person_data = soup.find_all("tbody")

        # проверяем есть ли на странице данные о героях
        page_len = len(all_person_data)
        # print(f"page_len: {page_len}")
        # print(all_person_data[1].text)
        if not all_person_data[1].text:
            return
        else:
            # выбираем ту часть, которая относится к героям
            persons_data = all_person_data[1]

            #  преобразуем данные относящиеся к героям в список
            persons_list_data = persons_data.find_all("tr")

            return [self.parse_one_person_data(in_data=person_data, clan_id=clan_id) for person_data in persons_list_data]

    def parse_one_person_data(self, in_data: element.Tag, clan_id: int) -> PlayerSchem:
        """Данный метод парсит данные из html страницы относящиеся к персонажу
        и преобразует их в словарь
        """
        total_dict = {}
        elements_list = in_data.find_all("td")
        for index, element in enumerate(elements_list):
            total_dict["clan"] = clan_id
            if index == 1:
                total_dict["id"] = int(element.text)
            if index == 2:
                split_name_lvl = element.text.split("[")
                total_dict["level"] = int(split_name_lvl[1].split("]")[0])
                total_dict["name"] = split_name_lvl[0].strip()
            if index == 7:
                total_dict["umka_knight"] = int(element.text)
            if index == 8:
                total_dict["umka_necro"] = int(element.text)
            if index == 9:
                total_dict["umka_mag"] = int(element.text)
            if index == 10:
                total_dict["umka_elf"] = int(element.text)
            if index == 11:
                total_dict["umka_barbar"] = int(element.text)
            if index == 12:
                total_dict["umka_black_elf"] = int(element.text)
            if index == 13:
                total_dict["umka_demon"] = int(element.text)
            if index == 14:
                total_dict["umka_dwarf"] = int(element.text)
            if index == 15:
                total_dict["umka_step_barb"] = int(element.text)
            if index == 16:
                total_dict["umka_pharaon"] = int(element.text)

            if index == 18:
                total_dict["gild_hunt"] = int(element.text)
            if index == 19:
                total_dict["gild_work"] = int(element.text)
            if index == 20:
                total_dict["gild_card"] = int(element.text)
            if index == 21:
                total_dict["gild_thief"] = int(element.text)
            if index == 22:
                total_dict["gild_ranger"] = int(element.text)
            if index == 23:
                total_dict["gild_mers"] = int(element.text)
            if index == 24:
                total_dict["gild_tactic"] = int(element.text)
            if index == 25:
                total_dict["gild_gard"] = int(element.text)
            if index == 26:
                total_dict["gild_seekers"] = int(element.text)
            if index == 27:
                total_dict["gild_leader"] = int(element.text)
            if index == 28:
                total_dict["gild_blacksmith"] = int(element.text)
            if index == 29:
                total_dict["gild_gunsmith"] = int(element.text)

        return PlayerSchem(**total_dict)

if __name__ == '__main__':
    obj = PersonParser()
    # page_day_data = obj.parse_one_page(clan_id=13, page=2)
    # print(page_day_data)
    data = obj.parse_one_clan_data(clan_id=13)
    print(data, len(data))