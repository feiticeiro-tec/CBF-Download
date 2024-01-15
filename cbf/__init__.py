from loguru import logger
import re
from requests import Session


class CBF(Session):
    URL_BASE = "https://www.cbf.com.br"
    URL_CAMP_BRASILEIRO_SERIE_FORMAT = (
        URL_BASE + "/futebol-brasileiro/competicoes/"
        "campeonato-brasileiro-serie-"
        "{serie}/{ano}/{partida}"
    )
    URL_EXTERNAL_SUMULA_FORMAT = URL_BASE + "/external/sumula/{ano}/"

    def request_get_serie(self, serie, ano, partida):
        msg = f"REQUEST GET SERIE! SERIE:{serie} ANO:{ano} PARTIDA:{partida}"
        logger.debug(msg)
        return self.get(
            self.URL_CAMP_BRASILEIRO_SERIE_FORMAT.format(
                serie=serie.lower(), ano=ano, partida=partida
            )
        )

    def get_url_external(self, html, ano):
        url = self.URL_EXTERNAL_SUMULA_FORMAT.format(ano=ano)
        for row in html.split("\n"):
            if url in row:
                # https://www.cbf.com.br/external/sumula/2023/[0-9]+
                query = f"{url}[0-9]+"
                return re.search(query, row).group()

    def get_url_sumula_external(self, serie, ano, partida):
        """PEGA O LINK DO PDF DE RELATORIO DA PARTIDA!"""
        logger.debug(
            "PEGA O LINK DO PDF DE RELATORIO DA PARTIDA!"
            f"SERIE: {serie} ANO: {ano} PARTIDA: {partida}"
        )
        response = self.request_get_serie(serie, ano, partida)

        return self.get_url_external(response.text, ano)

    def request_download_file(self, url):
        logger.debug(f"FAZ O DOWNLOAD DE UM ARQUIVO! URL: {url}")
        return self.get(url).content


if __name__ == "__main__":
    cbf = CBF()
    url = cbf.get_url_sumula_external("A", 2021, 1)
    file = cbf.request_download_file(url)
    print(type(file))
