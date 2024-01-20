import re
from loguru import logger
from .. import regex as config
from .base import CBFExtratBase


class CBFExtrat(CBFExtratBase):
    @classmethod
    def get_person(cls, text, local=False):
        """Coleta Generica -> x: y (x/x)"""
        query = config.REGEX_GET_NAME.search(text)
        if local:
            return {
                "nome": query.group(2).strip(),
                "categoria": query.group(3).strip(),
                "regiao": query.group(4).strip(),
            }
        return query.group(2).strip()

    @classmethod
    def get_arbitros(cls, row):
        if row.startswith(
            (
                "Arbitro:",
                "Arbitro Assistente 1:",
                "Arbitro Assistente 2:",
                "Quarto Arbitro:",
            )
        ):
            return cls.get_person(row, local=True)

    @classmethod
    def set_in_arbistros_row(cls, arbitros, row):
        """PEGA OS ARBITROS"""
        dados = cls.get_arbitros(row)
        if not dados:
            return

        if row.startswith("Arbitro:"):
            arbitros["arbitro_principal"] = dados

        elif row.startswith("Arbitro Assistente 1:"):
            arbitros["arbitro_segundo"] = dados

        elif row.startswith("Arbitro Assistente 2:"):
            arbitros["arbitro_terceiro"] = dados

        elif row.startswith("Quarto Arbitro:"):
            arbitros["arbitro_quarto"] = dados

    def get_data(self, text):
        return self.colect_time(
            text,
            config.REGEX_DATA,
            "%d/%m/%Y",
        )

    def get_hora_time(self, text):
        return self.colect_time(
            text,
            config.REGEX_HORA,
            "%H:%M",
            time=True,
        )

    def get_localizacao(self, row):
        """PEGA A LOCALIZAÇÃO DO JOGO"""
        query = config.REGEX_ESTADIO.search(row)
        return {
            "data": self.get_data(row),
            "hora": self.get_hora_time(row),
            "estadio": query.group(2).strip(),
            "cidade": query.group(3).strip(),
        }

    def set_in_localizacao_row(self, localizacao, row):
        """PEGA A LOCALIZAÇÃO DO JOGO"""
        loc = self.get_localizacao(row)
        localizacao["hora"] = loc["hora"]
        localizacao["data"] = loc["data"]
        localizacao["estadio"] = loc["estadio"]
        localizacao["cidade"] = loc["cidade"]

    @classmethod
    def get_hora_acrecimo_atraso(cls, row):
        hora = re.search(config.REGEX_HORA, row).group()
        atraso = config.REGEX_ATRASO.search(row)
        acrecimo = None
        if not atraso:
            acrecimo = config.REGEX_ACRESCIMO.search(row)

        if not hora and not atraso and not acrecimo:
            return
        return (hora, acrecimo, atraso)

    def get_tempos(self, row):
        """PEGA O TEMPO DE JOGO"""
        hora, acrecimo, atraso = self.get_hora_acrecimo_atraso(row)
        if self.datetime:
            hora = self.get_hora_time(hora)

        tempo = {"hora": hora}
        if acrecimo:
            key = "acrecimo"
            value = acrecimo.group(2)
        else:
            key = "atraso"
            value = atraso.group(2)

        tempo[key] = int(value) if value else 0
        return tempo

    def set_in_tempos_row(self, anchor, row):
        """PEGA O TEMPO DE JOGO"""
        tempo = self.get_tempos(row)
        if tempo:
            anchor.append(tempo)

    @classmethod
    def get_placar(cls, row, casa, fora):
        """PEGA O PLACAR DO JOGO"""
        regex = config.REGEX_1X1  # 1 X 1
        tempos = re.findall(regex, row)
        tempo_1, tempo_2 = tempos
        tempo_1 = {
            casa: int(tempo_1[0]),
            fora: int(tempo_1[3]),
        }
        tempo_2 = {
            casa: int(tempo_2[0]),
            fora: int(tempo_2[3]),
        }
        return (tempo_1, tempo_2)

    @classmethod
    def set_placar_in_row(cls, anchor, row, casa, fora):
        """PEGA O PLACAR DO JOGO"""
        tempo_1, tempo_2 = cls.get_placar(row, casa, fora)
        anchor.append(tempo_1)
        anchor.append(tempo_2)

    def get_cartoes(self, row, times):
        """PEGA OS CARTÕES DO JOGO"""
        regex = config.REGEX_CARTOES
        query = re.findall(regex, row)
        if query:
            query = query[0]
            if self.datetime:
                hora = self.get_hora_time(query[0])
            else:
                hora = query[0]
            tempo = int(query[1])
            num = int(query[2])
            nome = query[3]
            for time in times:
                _time = f"{time}/{times[time]['sigla']}"
                if _time in row:
                    nome = nome[: nome.find(time)].strip()
                    break
            return {
                "hora": hora,
                "tempo": tempo,
                "num": num,
                "nome": nome,
                "time": time,
            }

    def set_cartoes_in_row(self, anchor, row, times):
        """PEGA OS CARTÕES DO JOGO"""

        cartao = self.get_cartoes(row, times)
        if cartao:
            anchor.append(cartao)

    @classmethod
    def get_times(cls, row):
        """PEGA OS TIMES DO JOGO"""
        if not re.search(r"([\w\s]+)(\s+)?/", row):
            return
        query = config.REGEX_PEGAR_TIMES.search(row)
        casa_nome = query.group(1).strip()
        casa_sigla = query.group(4)
        fora_nome = query.group(7).strip()
        fora_sigla = query.group(10)
        logger.debug(f"TIMES: {casa_nome} X {fora_nome}")
        return {
            casa_nome: {
                "nome": casa_nome,
                "sigla": casa_sigla,
                "casa": True,
            },
            fora_nome: {
                "nome": fora_nome,
                "sigla": fora_sigla,
                "casa": False,
            },
        }

    def set_times_in_row(self, anchor, row):
        """PEGA OS TIMES DO JOGO"""

        times = self.get_times(row)
        if times:
            for time in times:
                anchor[time] = times[time]

    def get_query_substituicao(self, row):
        """is_int, query"""
        is_int = False
        try:
            regex = config.REGEX_SUBSTITUICAO
            query = re.findall(regex, row)[0]
        except Exception:
            is_int = True

            try:
                regex = config.REGEX_SUBSTITUICAO_INT
                query = re.findall(regex, row)[0]
            except Exception:
                return
        return is_int, query

    def get_substituicoes(self, row):
        """PEGA AS SUBSTITUIÇÕES DO JOGO"""
        query = self.get_query_substituicao(row)
        if not query:
            return
        is_int, query = query
        hora = self.get_hora_time(query[0])

        if is_int:
            tempo = query[2]
        else:
            tempo = int(query[2])

        time_nome = query[3].strip()
        num_1 = int(query[6])
        atleta_1 = query[9].strip()
        num_2 = int(query[12])
        atleta_2 = query[14].strip()
        return {
            "hora": hora,
            "tempo": tempo,
            "time": time_nome,
            "entrada_numero": num_1,
            "entrada_nome": atleta_1,
            "saida_numero": num_2,
            "saida_nome": atleta_2,
        }

    def set_substituicoes_in_row(self, anchor, row):
        """PEGA AS SUBSTITUIÇÕES DO JOGO"""
        substituicao = self.get_substituicoes(row)
        if not substituicao:
            return
        anchor.append(substituicao)

    def get_gol(self, row):
        """PEGA OS GOLS DO JOGO"""

        regex = config.REGEX_GOLS
        query = re.findall(regex, row)
        if query:
            query = query[0]
            hora = self.get_hora_time(query[0])
            tempo = int(query[2])
            num = int(query[3])
            tipo = query[4]
            nome = query[5].strip()
            time_nome = query[7].strip()
            return {
                "hora": hora,
                "tempo": tempo,
                "tipo": tipo,
                "numero": num,
                "nome": nome,
                "time": time_nome,
            }

    def set_gols_in_row(self, anchor, row):
        """PEGA OS GOLS DO JOGO"""
        gol = self.get_gol(row)
        if gol:
            anchor.append(gol)

    @classmethod
    def get_posicao_jogador(self, text):
        if text == "(g)":
            return "Goleiro"
        return "Jogador"

    @classmethod
    def get_tipo_jogador(self, text):
        if text == "T":
            return "Titular"
        elif text == "R":
            return "Reserva"

    @classmethod
    def get_categoria_jogador(self, text):
        if text == "P":
            return "Profissional"
        elif text == "A":
            return "Amador"

    @classmethod
    def get_jogador(cls, row):
        jogador = config.REGEX_JOGADOR.search(row)
        if jogador:
            return {
                "tipo": cls.get_tipo_jogador(jogador.group(1)),
                "posicao": cls.get_posicao_jogador(jogador.group(2)),
                "categoria": cls.get_categoria_jogador(jogador.group(3)),
                "cbf": jogador.group(4),
            }

    @classmethod
    def get_time(cls, times, casa=True):
        time = filter(lambda _obj: _obj["casa"] == casa, times.values())
        return tuple(time)[0]

    def set_jogador_in_time(self, row, time, times):
        jogador = self.get_jogador(row)
        _time = self.get_time(times, casa=time == 0)
        if jogador:
            jogadores = times[_time["nome"]].setdefault("jogadores", [])
            jogadores.append(jogador)

    def get_coleta(self, text):
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
                self.set_jogador_in_time(row, time, times)
            elif "Data:" in row and "Horário" in row:
                self.set_in_localizacao_row(localizacao, row)
            elif "Jogo: " in row:
                self.set_times_in_row(times, row)
            elif "Arbitro" in row:
                self.set_in_arbistros_row(arbitros, row)
            elif "Delegado" in row:
                delegado = self.get_person(row)
            elif "Analista" in row:
                analista = self.get_person(row)
            elif "Entrada do mandante:" in row:
                self.set_in_tempos_row(mandante_entrada, row)
            elif "Entrada do visitante:" in row:
                self.set_in_tempos_row(visitante_entrada, row)
            elif "Início 1º Tempo:" in row:
                self.set_in_tempos_row(tempo_1, row)
            elif "Término do 1º Tempo:" in row:
                self.set_in_tempos_row(tempo_1, row)
            elif "Início do 2º Tempo:" in row:
                self.set_in_tempos_row(tempo_2, row)
            elif "Término do 2º Tempo:" in row:
                self.set_in_tempos_row(tempo_2, row)
            elif "Resultado do 1º Tempo:" in row:
                casa = self.get_time(times, casa=True)
                fora = self.get_time(times, casa=False)
                self.set_placar_in_row(placar, row, casa["nome"], fora["nome"])
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
                self.set_cartoes_in_row(cartoes_amarelo, row, times)
            elif cartoes == "Vermelhos":
                self.set_cartoes_in_row(cartoes_vermelho, row, times)
            elif subs:
                self.set_substituicoes_in_row(substituicoes, row)
            elif gol:
                self.set_gols_in_row(gols, row)
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
