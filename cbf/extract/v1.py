import re
from datetime import datetime
from loguru import logger
from .. import regex as config
from .base import CBFExtratBase


class CBFExtrat(CBFExtratBase):
    def get_person(self, text, local=False):
        """Coleta Generica -> x: y (x/x)"""
        query = config.REGEX_GET_NAME.search(text)
        if local:
            return (
                query.group(2).strip(),
                (query.group(3).strip(), query.group(4).strip()),
            )
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
                arbitros["Arbitro Principal"] = dados

            elif row.startswith("Arbitro Assistente 1:"):
                arbitros["Arbitro Segundo"] = dados

            elif row.startswith("Arbitro Assistente 2:"):
                arbitros["Arbitro Terceiro"] = dados

            elif row.startswith("Quarto Arbitro:"):
                arbitros["Arbitro Quarto"] = dados

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
        diferenca = config.REGEX_ATRASO.search(row)
        if not diferenca:
            diferenca = config.REGEX_ACRESCIMO.search(row)

        if not hora and not diferenca:
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
        diferenca = int(diferenca.group(2)) if diferenca.group(2) else 0
        anchor.append((hora, diferenca))

    def get_placar(self, anchor, row):
        """PEGA O PLACAR DO JOGO"""
        regex = config.REGEX_1X1  # 1 X 1
        tempos = re.findall(regex, row)
        t1, t2 = tempos
        t1 = (int(t1[0]), int(t1[3]))
        t2 = (int(t2[0]), int(t2[3]))
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
                _time = "/".join(time)
                if _time in row:
                    nome = nome[: nome.find(time[0])].strip()
                    break
            anchor.append((hora, tempo, num, nome, time))

    def get_times(self, anchor, row):
        """PEGA OS TIMES DO JOGO"""
        if not re.search(r"([\w\s]+)(\s+)?/", row):
            return
        query = config.REGEX_PEGAR_TIMES.search(row)
        casa = (query.group(1).strip(), query.group(4))
        fora = (query.group(7).strip(), query.group(10))
        logger.debug(f"TIMES: {casa} X {fora}")
        anchor.append(casa)
        anchor.append(fora)

    def get_substuicoes(self, anchor, row):
        """PEGA AS SUBSTITUIÇÕES DO JOGO"""
        try:
            regex = config.REGEX_SUBSTITUICAO
            query = re.findall(regex, row)[0]
        except Exception:
            return

        if self.datetime:
            hora = datetime.strptime(query[0], "%M:%S").time()
        else:
            hora = query[0]
        tempo = int(query[2])
        time = (query[3].strip(), query[4])
        num_1 = int(query[6])
        atleta_1 = query[9].strip()
        num_2 = int(query[12])
        atleta_2 = query[14].strip()
        anchor.append((hora, tempo, time, num_1, atleta_1, num_2, atleta_2))

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
            time = (query[7].strip(), query[8])
            anchor.append((hora, tempo, tipo, num, nome, time))

    def get_jogador(self, row):
        jogador = config.REGEX_JOGADOR.search(row)
        if jogador:
            return {
                "Ordem": jogador.group(1),
                "Posicao": jogador.group(2),
                "Categoria": jogador.group(3),
                "cbf": jogador.group(4),
            }

    def get_data(self, text):
        """PEGA TODOS OS DADOS DO JOGO"""
        times = []
        jogadores = {}
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
                jogador = self.get_jogador(row)
                if jogador:
                    jogadores.setdefault(times[time][0], []).append(jogador)
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
                self.get_placar(placar, row)
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
                self.get_substuicoes(substituicoes, row)
            elif gol:
                self.get_gols(gols, row)
        return {
            "Times": times,
            "Jogaodres": jogadores,
            "Localizacao": localizacao,
            "Arbitros": arbitros,
            "Delegado": delegado,
            "Analista": analista,
            "Mandante Entrada": mandante_entrada,
            "Visitante Entrada": visitante_entrada,
            "Tempo 1": tempo_1,
            "Tempo 2": tempo_2,
            "Placar": placar,
            "Cartoes Amarelos": cartoes_amarelo,
            "Cartoes Vemelhos": cartoes_vermelho,
            "Substituicoes": substituicoes,
            "Gols": gols,
        }
