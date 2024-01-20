import re
import PyPDF2
from io import BytesIO
from datetime import datetime
from loguru import logger
from .. import regex as config
from .base import CBFExtratBase


class CBFExtrat(CBFExtratBase):
    def get_person(self, text, local=False):
        """Coleta Generica -> x: y (x/x)"""
        query = config.REGEX_GET_NAME.search(text)
        if local:
            return {
                "nome": query.group(2).strip(),
                "categoria": query.group(3).strip(),
                "regiao": query.group(4).strip(),
            }
        return query.group(2).strip()

    def get_arbitros(self, arbitros, row):
        """PEGA OS ARBITROS"""
        if row.startswith(
            (
                "Arbitro:",
                "Arbitro Assistente 1:",
                "Arbitro Assistente 2:",
                "Quarto Arbitro:",
            )
        ):
            dados = self.get_person(row, local=True)
            if row.startswith("Arbitro:"):
                arbitros["arbitro_principal"] = dados

            elif row.startswith("Arbitro Assistente 1:"):
                arbitros["arbitro_segundo"] = dados

            elif row.startswith("Arbitro Assistente 2:"):
                arbitros["arbitro_terceiro"] = dados

            elif row.startswith("Quarto Arbitro:"):
                arbitros["arbitro_quarto"] = dados

    def get_localizacao(self, localizacao, row):
        """PEGA A LOCALIZAÇÃO DO JOGO"""
        loc = localizacao
        query = config.REGEX_ESTADIO.search(row)
        estadio = query.group(2).strip()
        cidade = query.group(3).strip()
        loc["data"] = self.colect_time(row, config.REGEX_DATA, "%d/%m/%Y")
        loc["hora"] = self.colect_time(
            row,
            config.REGEX_HORA,
            "%H:%M",
            time=True,
        )
        loc["estadio"] = estadio.strip()
        loc["cidade"] = cidade.strip()

    def get_tempos(self, anchor, row):
        """PEGA O TEMPO DE JOGO"""
        hora = config.REGEX_HORA
        atraso = config.REGEX_ATRASO.search(row)
        acrecimo = None
        if not atraso:
            acrecimo = config.REGEX_ACRESCIMO.search(row)

        if not hora and not atraso and not acrecimo:
            return

        hora = re.search(hora, row).group()
        if self.datetime:
            hora = self.colect_time(
                hora,
                config.REGEX_HORA,
                "%H:%M",
                time=True,
            )
        else:
            hora

        tempo = {"hora": hora}
        if acrecimo:
            acrecimo = int(acrecimo.group(2)) if acrecimo.group(2) else 0
            tempo["acrecimo"] = acrecimo
        else:
            atraso = int(atraso.group(2)) if atraso.group(2) else 0
            tempo["atraso"] = atraso
        anchor.append(tempo)

    def get_placar(self, anchor, row, casa, fora):
        """PEGA O PLACAR DO JOGO"""
        regex = config.REGEX_1X1  # 1 X 1
        tempos = re.findall(regex, row)
        t1, t2 = tempos
        t1 = {
            casa: int(t1[0]),
            fora: int(t1[3]),
        }
        t2 = {
            casa: int(t2[0]),
            fora: int(t2[3]),
        }
        anchor.append(t1)
        anchor.append(t2)

    def get_cartoes(self, anchor, row, times):
        """PEGA OS CARTÕES DO JOGO"""
        regex = config.REGEX_CARTOES
        query = re.findall(regex, row)
        if query:
            query = query[0]
            hora = (
                datetime.strptime(query[0], "%M:%S").time()
                if self.datetime
                else query[0]
            )
            tempo = int(query[1])
            num = int(query[2])
            nome = query[3]
            for time in times:
                _time = f"{time}/{times[time]['sigla']}"
                if _time in row:
                    nome = nome[: nome.find(time)].strip()
                    break
            anchor.append(
                {
                    "hora": hora,
                    "tempo": tempo,
                    "num": num,
                    "nome": nome,
                    "time": time,
                }
            )

    def get_times(self, anchor, row):
        """PEGA OS TIMES DO JOGO"""
        if not re.search(r"([\w\s]+)(\s+)?/", row):
            return
        query = config.REGEX_PEGAR_TIMES.search(row)
        casa_nome = query.group(1).strip()
        casa_sigla = query.group(4)
        fora_nome = query.group(7).strip()
        fora_sigla = query.group(10)
        logger.debug(f"TIMES: {casa_nome} X {fora_nome}")
        anchor[casa_nome] = {
            "nome": casa_nome,
            "sigla": casa_sigla,
            "casa": True,
        }
        anchor[fora_nome] = {
            "nome": fora_nome,
            "sigla": fora_sigla,
            "casa": False,
        }

    def get_substituicoes(self, anchor, row):
        """PEGA AS SUBSTITUIÇÕES DO JOGO"""
        is_int = False
        try:
            regex = config.REGEX_SUBSTITUICAO
            query = re.findall(regex, row)[0]
        except Exception:
            is_int = True

            try:
                print(row)
                regex = config.REGEX_SUBSTITUICAO_INT
                query = re.findall(regex, row)[0]
            except Exception:
                return

        hora = (
            datetime.strptime(query[0], "%M:%S").time() if self.datetime else query[0]
        )
        if is_int:
            tempo = query[2]
        else:
            tempo = int(query[2])
        time_nome = query[3].strip()
        num_1 = int(query[6])
        atleta_1 = query[9].strip()
        num_2 = int(query[12])
        atleta_2 = query[14].strip()
        anchor.append(
            {
                "hora": hora,
                "tempo": tempo,
                "time": time_nome,
                "entrada_numero": num_1,
                "entrada_nome": atleta_1,
                "saida_numero": num_2,
                "saida_nome": atleta_2,
            }
        )

    def get_gols(self, anchor, row):
        """PEGA OS GOLS DO JOGO"""

        regex = config.REGEX_GOLS
        query = re.findall(regex, row)
        if query:
            query = query[0]
            hora = (
                datetime.strptime(query[0], "%M:%S").time()
                if self.datetime
                else query[0]
            )
            tempo = int(query[2])
            num = int(query[3])
            tipo = query[4]
            nome = query[5].strip()
            time_nome = query[7].strip()
            anchor.append(
                {
                    "hora": hora,
                    "tempo": tempo,
                    "tipo": tipo,
                    "numero": num,
                    "nome": nome,
                    "time": time_nome,
                }
            )

    def get_posicao_jogador(self, text):
        if text == "(g)":
            return "Goleiro"
        return "Jogador"

    def get_tipo_jogador(self, text):
        if text == "T":
            return "Titular"
        elif text == "R":
            return "Reserva"

    def get_categoria_jogador(self, text):
        if text == "P":
            return "Profissional"
        elif text == "A":
            return "Amador"

    def get_jogador(self, row):
        jogador = config.REGEX_JOGADOR.search(row)
        if jogador:
            return {
                "tipo": self.get_tipo_jogador(jogador.group(1)),
                "posicao": self.get_posicao_jogador(jogador.group(2)),
                "categoria": self.get_categoria_jogador(jogador.group(3)),
                "cbf": jogador.group(4),
            }

    def get_time(self, times, casa=True):
        time = filter(lambda _obj: _obj["casa"] == casa, times.values())
        return tuple(time)[0]

    def pegar_jogarores_por_time(self, row, time, times):
        jogador = self.get_jogador(row)
        _time = tuple(filter(lambda _obj: _obj["casa"] == time, times.values()))[0]
        if jogador:
            jogadores = times[_time["nome"]].setdefault("jogadores", [])
            jogadores.append(jogador)

    def get_data(self, text):
        """PEGA TODOS OS DADOS DO JOGO"""
        times = {}
        localizacao = {}
        arbitros = {}
        delegado = ""
        analista = ""
        mandante_entrada = []
        visitante_entrada = []
        tempo_1 = []
        tempo_2 = []
        placar = []
        cartoes = False
        cartoes_amarelo = []
        cartoes_vermelho = []
        subs = False
        substituicoes = []
        gol = False
        gols = []
        time = -1
        for row in text.split("\n"):
            if "NºApelido Nome Completo T/RP/A CBF" in row:
                time += 1
            elif time in (0, 1) and config.REGEX_JOGADOR.search(row):
                self.pegar_jogarores_por_time(row, time, times)
            elif "Data:" in row and "Horário" in row:
                self.get_localizacao(localizacao, row)
            elif "Jogo: " in row:
                self.get_times(times, row)
            elif "Arbitro" in row:
                self.get_arbitros(arbitros, row)
            elif "Delegado" in row:
                delegado = self.get_person(row)
            elif "Analista" in row:
                analista = self.get_person(row)
            elif "Entrada do mandante:" in row:
                self.get_tempos(mandante_entrada, row)
            elif "Entrada do visitante:" in row:
                self.get_tempos(visitante_entrada, row)
            elif "Início 1º Tempo:" in row:
                self.get_tempos(tempo_1, row)
            elif "Término do 1º Tempo:" in row:
                self.get_tempos(tempo_1, row)
            elif "Início do 2º Tempo:" in row:
                self.get_tempos(tempo_2, row)
            elif "Término do 2º Tempo:" in row:
                self.get_tempos(tempo_2, row)
            elif "Resultado do 1º Tempo:" in row:
                casa = self.get_time(times, casa=True)
                fora = self.get_time(times, casa=False)
                self.get_placar(placar, row, casa["nome"], fora["nome"])
            elif "Gols" in row:
                gol = True
            elif "Cartões Amarelos" in row:
                gol = False
                cartoes = "Amarelos"
            elif "Cartões Vermelhos" in row:
                cartoes = "Vermelhos"
            elif "Substituições" in row:
                cartoes = False
                subs = True
            elif cartoes == "Amarelos":
                self.get_cartoes(cartoes_amarelo, row, times)
            elif cartoes == "Vermelhos":
                self.get_cartoes(cartoes_vermelho, row, times)
            elif subs:
                self.get_substituicoes(substituicoes, row)
            elif gol:
                self.get_gols(gols, row)
        return {
            "times": times,
            "localizacao": localizacao,
            "arbitros": arbitros,
            "delegado": delegado,
            "analista": analista,
            "mandante_entrada": mandante_entrada,
            "visitante_entrada": visitante_entrada,
            "tempo_1": tempo_1,
            "tempo_2": tempo_2,
            "placar": placar,
            "cartoes_amarelos": cartoes_amarelo,
            "cartoes_vemelhos": cartoes_vermelho,
            "substituicoes": substituicoes,
            "gols": gols,
        }
