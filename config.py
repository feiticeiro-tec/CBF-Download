import os
import re

RABBITMQ_USERNAME = os.environ["RABBITMQ_USERNAME"]
RABBITMQ_HOST = os.environ["RABBITMQ_HOST"]
RABBITMQ_PASSWORD = os.environ["RABBITMQ_PASSWORD"]
RABBITMQ_PORT = os.environ["RABBITMQ_PORT"]
RABBITMQ_BROKER = f"pyamqp://{RABBITMQ_USERNAME}:{RABBITMQ_PASSWORD}@{RABBITMQ_HOST}:{RABBITMQ_PORT}//"
RESULT_EXPIRES = int(os.environ.get("RESULT_EXPIRES", 3600))  # 1 hour

URL_BASE = "https://www.cbf.com.br"
URL_CAMP_BRASILEIRO_SERIE_FORMAT = (
    URL_BASE + "/futebol-brasileiro/competicoes/"
    "campeonato-brasileiro-serie-"
    "{serie}/{ano}/{partida}"
)
URL_EXTERNAL_SUMULA_FORMAT = URL_BASE + "/external/sumula/{ano}/"
DATETIME = True

REGEX_PEGAR_TIMES = re.compile(
    r"([\w|\s]+)(\s+)?/(\s+)?(\w{2})(\s+)?X" r"(\s+)?([\w|\s]+)(\s+)?/(\s+)?(\w{2})"
)
REGEX_GET_NAME = re.compile(r"[\w|\s|\d]+:(\s+)?([\w|\s.]+)\(([\w|\s]+)/([\w|\s]+)\)")
REGEX_ESTADIO = re.compile(r"Estádio:(\s+)?([\w\s]+)/([\w\s]+)")
REGEX_JOGADOR = re.compile(r"([TR])(\(g\))?([PA])([0-9]+)")
REGEX_ATRASO = re.compile(r"Atraso:(\s+)?([0-9]+)?")
REGEX_ACRESCIMO = re.compile(r"Acréscimo:(\s+)?([0-9]+)?")
REGEX_1X1 = r"([0-9]+)(\s+)?X(\s+)?([0-9]+)"
REGEX_CARTOES = r"([0-9]+:[0-9]+) ([0-9])T(\d+)([\w\s]+)/(\w{2})"
REGEX_SUBSTITUICAO = (
    r"([0-9]+:[0-9]+)(\s+)?([0-9]+)T"
    r"([\w\s]+)/(\w{2})(\s+)?([0-9]+)(\s+)?[-]"
    r"(\s+)?([\w\s]+)(\.+)?(\s+)?([0-9]+)(\s+)?[-]([\w\s]+)"
)

REGEX_GOLS = (
    r"([0-9]+:[0-9]+)(\s+)?([0-9]+)T([0-9]+)([A-Z]{2})"
    r"([\w\s]+)(\s+)([\w\s]+)/(\w{2})"
)

REGEX_DATA = r"[0-9]+[/][0-9]+[/][0-9]+"
REGEX_HORA = r"[0-9]+[:][0-9]+"
