from dotenv import load_dotenv
import os

# Выгрузка секретных данных из .env. Данный файл должен лежать в данной директории.
load_dotenv()


TOKEN = os.getenv("TOKEN")
SERVER_URL = os.getenv("SERVER_URL")