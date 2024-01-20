# CBF Download
Como usar o serviço de download de arquivos do CBF.
o container não contem uma interface de usuario, para usar o serviço é necessario usar o rabbitmq para enviar uma mensagem para a fila cbf.download com os parametros serie, ano e partida.

### Dockercompose
```bash 
docker compose up
```
o serviço de download do arquivo vai esta disponivel da comunicação da tarefa cbf.download na porta 5672 passando os parametros serie, ano e partida apos isso sera retornado um dicionario contendo.
```json
{
    "serie": "A",
    "ano": 2022,
    "partida": 1,
    "file": "gzip decode latin-1"
}
```
como obter o binario da file
```python
data_response = task.result
file = data_response['file']
file_encode = file.encode('latin-1')
file_bytes = gzip.decompress(file_encode)
with open('file.pdf', 'wb') as f:
    f.write(file_bytes)
```

### Dockerfile
```bash
docker pull feiticeirotec/cbf-download

docker run\
-e RABBITMQ_USERNAME={RABBITMQ_USERNAME}\
-e RABBITMQ_HOST={RABBITMQ_HOST}\
-e RABBITMQ_PASSWORD={RABBITMQ_PASSWORD}\
-e RABBITMQ_PORT={RABBITMQ_PORT}\
feiticeirotec/cbf-download
```

### Exemplo de uso
```python
from celery import Celery
import gzip

BROKER = "pyamqp://guest:guest@localhost//"

app = Celery(broker=BROKER, backend="rpc://")


task = app.send_task(
    "cbf.download",
    kwargs={
        "serie": "A",
        "ano": 2019,
        "partida": 1,
    },
)

data_response = task.wait()
serie = data_response["serie"]
ano = data_response["ano"]
partida = data_response["partida"]
file = data_response["file"]
file_encode = file.encode("latin-1")
file_bytes = gzip.decompress(file_encode)
with open(f"{ano}-{serie}-{partida}.pdf", "wb") as f:
    f.write(file_bytes)

```

## Parse
Como usar o serviço de parse de arquivos do CBF.

```python

task = app.send_task(
    "cbf.parse",
    kwargs={
        "file": file,
    },
)

data_response = task.wait()
print(data_response)
```

retorno do parse do pdf

```json
{
    "Times": [["Grêmio", "RS"],["Santos", "SP"]],
    "Jogaodres": {
        "Grêmio": [
            {"Ordem": "T", "Posicao": "(g)", "Categoria": "P", "cbf": "175411"},
            {"Ordem": "T", "Posicao": null, "Categoria": "P", "cbf": "165322"},
            {"Ordem": "T", "Posicao": null, "Categoria": "P", "cbf": "554626"},
            {"Ordem": "T", "Posicao": null, "Categoria": "P", "cbf": "303436"},
            {"Ordem": "T", "Posicao": null, "Categoria": "P", "cbf": "166603"},
            {"Ordem": "T", "Posicao": null, "Categoria": "P", "cbf": "379065"},
            {"Ordem": "T", "Posicao": null, "Categoria": "P", "cbf": "180546"},
            {"Ordem": "T", "Posicao": null, "Categoria": "P", "cbf": "407776"},
            {"Ordem": "T", "Posicao": null, "Categoria": "P", "cbf": "422351"},
            {"Ordem": "T", "Posicao": null, "Categoria": "P", "cbf": "317751"},
            {"Ordem": "T", "Posicao": null, "Categoria": "P", "cbf": "292942"},
            {"Ordem": "R", "Posicao": "(g)", "Categoria": "P", "cbf": "169978"},
            {"Ordem": "R", "Posicao": null, "Categoria": "P", "cbf": "137644"},
            {"Ordem": "R", "Posicao": null, "Categoria": "P", "cbf": "298485"},
            {"Ordem": "R", "Posicao": null, "Categoria": "P", "cbf": "409960"},
            {"Ordem": "R", "Posicao": null, "Categoria": "P", "cbf": "150201"},
            {"Ordem": "R", "Posicao": null, "Categoria": "P", "cbf": "399284"},
            {"Ordem": "R", "Posicao": null, "Categoria": "P", "cbf": "183094"},
            {"Ordem": "R", "Posicao": null, "Categoria": "P", "cbf": "391953"},
            {"Ordem": "R", "Posicao": null, "Categoria": "P", "cbf": "646612"},
            {"Ordem": "R", "Posicao": null, "Categoria": "P", "cbf": "428672"},
            {"Ordem": "R", "Posicao": null, "Categoria": "P", "cbf": "402681"},
            {"Ordem": "R", "Posicao": null, "Categoria": "P", "cbf": "184307"}],
        "Santos": [
            {"Ordem": "T", "Posicao": "(g)", "Categoria": "P", "cbf": "177770"},
            {"Ordem": "T", "Posicao": null, "Categoria": "P", "cbf": "170272"},
            {"Ordem": "T", "Posicao": null, "Categoria": "P", "cbf": "186450"},
            {"Ordem": "T", "Posicao": null, "Categoria": "P", "cbf": "646668"},
            {"Ordem": "T", "Posicao": null, "Categoria": "P", "cbf": "334559"},
            {"Ordem": "T", "Posicao": null, "Categoria": "P", "cbf": "646663"},
            {"Ordem": "T", "Posicao": null, "Categoria": "P", "cbf": "295792"},
            {"Ordem": "T", "Posicao": null, "Categoria": "P", "cbf": "377476"},
            {"Ordem": "T", "Posicao": null, "Categoria": "P", "cbf": "318143"},
            {"Ordem": "T", "Posicao": null, "Categoria": "P", "cbf": "373768"},
            {"Ordem": "T", "Posicao": null, "Categoria": "P", "cbf": "331842"},
            {"Ordem": "R", "Posicao": "(g)", "Categoria": "P", "cbf": "188398"},
            {"Ordem": "R", "Posicao": null, "Categoria": "P", "cbf": "354299"},
            {"Ordem": "R", "Posicao": null, "Categoria": "P", "cbf": "320593"},
            {"Ordem": "R", "Posicao": null, "Categoria": "P", "cbf": "308980"},
            {"Ordem": "R", "Posicao": null, "Categoria": "P", "cbf": "633531"},
            {"Ordem": "R", "Posicao": null, "Categoria": "P", "cbf": "553524"},
            {"Ordem": "R", "Posicao": null, "Categoria": "P", "cbf": "441648"},
            {"Ordem": "R", "Posicao": null, "Categoria": "P", "cbf": "324513"},
            {"Ordem": "R", "Posicao": null, "Categoria": "P", "cbf": "633582"},
            {"Ordem": "R", "Posicao": null, "Categoria": "P", "cbf": "307979"},
            {"Ordem": "R", "Posicao": null, "Categoria": "P", "cbf": "362877"},
            {"Ordem": "R", "Posicao": null, "Categoria": "P", "cbf": "529172"}
        ]
    },
    "Localizacao": {
        "data": "28/04/2019",
        "hora": "11: 00",
        "estadio": "Arena do Grêmio",
        "cidade": "Porto Alegre"
    },
    "Arbitros": {
        "Arbitro Principal": ["Bruno Arleu de Araujo",["AB", "RJ"]],
        "Arbitro Segundo": ["Rodrigo Figueiredo Henrique Correa",["FIFA", "RJ"]],
        "Arbitro Terceiro": ["Thiago Henrique Neto Correa Farinha",["AB", "RJ"]],
        "Arbitro Quarto": ["Alexandre Vargas Tavares de Jesus",["AB", "RJ"]]
    },
    "Delegado": "Marcos Roberto Caduri de Almeida",
    "Analista": "Jose Mocellin",
    "Mandante Entrada": [["10: 50",0],["12: 01",0]],
    "Visitante Entrada": [["10: 54",4],["12: 02",0]],
    "Tempo 1": [
        ["11: 02",2],
        ["11: 50",3]
    ],
    "Tempo 2": [
        ["12: 05",0],
        ["12: 54",4]
    ],
    "Placar": [
        [0,2],
        [1,2]
    ],
    "Cartoes Amarelos": [
        ["10: 00",2,5, "Alison Lopes Ferreira",["Santos", "SP"]],
        ["23: 00",2,21, "Diego Cristiano Evaristo",["Santos", "SP"]],
        ["39: 00",2,28, "Lucas Verissimo da Silva",["Santos", "SP"]],
        ["03: 00",2,17, "Derlis Alberto Gonzalez Galeano",["Santos", "SP"]],
        ["07: 00",2,14, "Matheus Henrique de Souza",["Grêmio", "RS"]],
        ["33: 00",1,8, "Maicon Thiago Pereira de Souza",["Grêmio", "RS"]],
        ["38: 00",1,4, "Walter Kannemann",["Grêmio", "RS"]]
    ],
    "Cartoes Vemelhos": [],
    "Substituicoes": [
        ["06: 00",2,["Grêmio", "RS"],9, "Diego Tardelli Martins 2",3, "Alisson Euler de Freitas Cas"],
        ["14: 00",2,["Grêmio", "RS"],7, "Luan Guilherme de Jesus Vieira 2",1, "Jean Pyerre Casagrande Silve"],
        ["21: 00",2,["Santos", "SP"],17, "Derlis Alberto Gonzalez Gale",27, "Eduardo Colcenti Antunes"],
        ["28: 00",2,["Grêmio", "RS"],10, "Felipe dos Reis Pereira Vize",12, "Bruno Cortes Barbosa"],
        ["36: 00",2,["Santos", "SP"],7, "Carlos Andres Sanchez Arcosa 3",0, "Jean Lucas de Souza Oliveira"]
    ],
    "Gols": [
        ["05: 00",1, "NR",27, "Eduardo Colcenti Antunes",["Santos", "SP"]],
        ["35: 00",1, "NR",36, "Felipe Jonatan Rocha Andrade",["Santos", "SP"]]
    ]
}
```

Extração da versão 2:
```json

{
    "times": {
        "Gr\u00eamio": {
            "nome": "Gr\u00eamio",
            "sigla": "RS",
            "casa": true,
            "jogadores": [
                {
                    "tipo": "Titular",
                    "posicao": "Goleiro",
                    "categoria": "Profissional",
                    "cbf": "175411"
                },
                {
                    "tipo": "Titular",
                    "posicao": "Jogador",
                    "categoria": "Profissional",
                    "cbf": "165322"
                },
                {
                    "tipo": "Titular",
                    "posicao": "Jogador",
                    "categoria": "Profissional",
                    "cbf": "554626"
                },
                {
                    "tipo": "Titular",
                    "posicao": "Jogador",
                    "categoria": "Profissional",
                    "cbf": "303436"
                },
                {
                    "tipo": "Titular",
                    "posicao": "Jogador",
                    "categoria": "Profissional",
                    "cbf": "166603"
                },
                {
                    "tipo": "Titular",
                    "posicao": "Jogador",
                    "categoria": "Profissional",
                    "cbf": "379065"
                },
                {
                    "tipo": "Titular",
                    "posicao": "Jogador",
                    "categoria": "Profissional",
                    "cbf": "180546"
                },
                {
                    "tipo": "Titular",
                    "posicao": "Jogador",
                    "categoria": "Profissional",
                    "cbf": "407776"
                },
                {
                    "tipo": "Titular",
                    "posicao": "Jogador",
                    "categoria": "Profissional",
                    "cbf": "422351"
                },
                {
                    "tipo": "Titular",
                    "posicao": "Jogador",
                    "categoria": "Profissional",
                    "cbf": "317751"
                },
                {
                    "tipo": "Titular",
                    "posicao": "Jogador",
                    "categoria": "Profissional",
                    "cbf": "292942"
                },
                {
                    "tipo": "Reserva",
                    "posicao": "Goleiro",
                    "categoria": "Profissional",
                    "cbf": "169978"
                },
                {
                    "tipo": "Reserva",
                    "posicao": "Jogador",
                    "categoria": "Profissional",
                    "cbf": "137644"
                },
                {
                    "tipo": "Reserva",
                    "posicao": "Jogador",
                    "categoria": "Profissional",
                    "cbf": "298485"
                },
                {
                    "tipo": "Reserva",
                    "posicao": "Jogador",
                    "categoria": "Profissional",
                    "cbf": "409960"
                },
                {
                    "tipo": "Reserva",
                    "posicao": "Jogador",
                    "categoria": "Profissional",
                    "cbf": "150201"
                },
                {
                    "tipo": "Reserva",
                    "posicao": "Jogador",
                    "categoria": "Profissional",
                    "cbf": "399284"
                },
                {
                    "tipo": "Reserva",
                    "posicao": "Jogador",
                    "categoria": "Profissional",
                    "cbf": "183094"
                },
                {
                    "tipo": "Reserva",
                    "posicao": "Jogador",
                    "categoria": "Profissional",
                    "cbf": "391953"
                },
                {
                    "tipo": "Reserva",
                    "posicao": "Jogador",
                    "categoria": "Profissional",
                    "cbf": "646612"
                },
                {
                    "tipo": "Reserva",
                    "posicao": "Jogador",
                    "categoria": "Profissional",
                    "cbf": "428672"
                },
                {
                    "tipo": "Reserva",
                    "posicao": "Jogador",
                    "categoria": "Profissional",
                    "cbf": "402681"
                },
                {
                    "tipo": "Reserva",
                    "posicao": "Jogador",
                    "categoria": "Profissional",
                    "cbf": "184307"
                }
            ]
        },
        "Santos": {
            "nome": "Santos",
            "sigla": "SP",
            "casa": false,
            "jogadores": [
                {
                    "tipo": "Titular",
                    "posicao": "Goleiro",
                    "categoria": "Profissional",
                    "cbf": "177770"
                },
                {
                    "tipo": "Titular",
                    "posicao": "Jogador",
                    "categoria": "Profissional",
                    "cbf": "170272"
                },
                {
                    "tipo": "Titular",
                    "posicao": "Jogador",
                    "categoria": "Profissional",
                    "cbf": "186450"
                },
                {
                    "tipo": "Titular",
                    "posicao": "Jogador",
                    "categoria": "Profissional",
                    "cbf": "646668"
                },
                {
                    "tipo": "Titular",
                    "posicao": "Jogador",
                    "categoria": "Profissional",
                    "cbf": "334559"
                },
                {
                    "tipo": "Titular",
                    "posicao": "Jogador",
                    "categoria": "Profissional",
                    "cbf": "646663"
                },
                {
                    "tipo": "Titular",
                    "posicao": "Jogador",
                    "categoria": "Profissional",
                    "cbf": "295792"
                },
                {
                    "tipo": "Titular",
                    "posicao": "Jogador",
                    "categoria": "Profissional",
                    "cbf": "377476"
                },
                {
                    "tipo": "Titular",
                    "posicao": "Jogador",
                    "categoria": "Profissional",
                    "cbf": "318143"
                },
                {
                    "tipo": "Titular",
                    "posicao": "Jogador",
                    "categoria": "Profissional",
                    "cbf": "373768"
                },
                {
                    "tipo": "Titular",
                    "posicao": "Jogador",
                    "categoria": "Profissional",
                    "cbf": "331842"
                },
                {
                    "tipo": "Reserva",
                    "posicao": "Goleiro",
                    "categoria": "Profissional",
                    "cbf": "188398"
                },
                {
                    "tipo": "Reserva",
                    "posicao": "Jogador",
                    "categoria": "Profissional",
                    "cbf": "354299"
                },
                {
                    "tipo": "Reserva",
                    "posicao": "Jogador",
                    "categoria": "Profissional",
                    "cbf": "320593"
                },
                {
                    "tipo": "Reserva",
                    "posicao": "Jogador",
                    "categoria": "Profissional",
                    "cbf": "308980"
                },
                {
                    "tipo": "Reserva",
                    "posicao": "Jogador",
                    "categoria": "Profissional",
                    "cbf": "633531"
                },
                {
                    "tipo": "Reserva",
                    "posicao": "Jogador",
                    "categoria": "Profissional",
                    "cbf": "553524"
                },
                {
                    "tipo": "Reserva",
                    "posicao": "Jogador",
                    "categoria": "Profissional",
                    "cbf": "441648"
                },
                {
                    "tipo": "Reserva",
                    "posicao": "Jogador",
                    "categoria": "Profissional",
                    "cbf": "324513"
                },
                {
                    "tipo": "Reserva",
                    "posicao": "Jogador",
                    "categoria": "Profissional",
                    "cbf": "633582"
                },
                {
                    "tipo": "Reserva",
                    "posicao": "Jogador",
                    "categoria": "Profissional",
                    "cbf": "307979"
                },
                {
                    "tipo": "Reserva",
                    "posicao": "Jogador",
                    "categoria": "Profissional",
                    "cbf": "362877"
                },
                {
                    "tipo": "Reserva",
                    "posicao": "Jogador",
                    "categoria": "Profissional",
                    "cbf": "529172"
                }
            ]
        }
    },
    "localizacao": {
        "hora": "11:00",
        "data": "28/04/2019",
        "estadio": "Arena do Gr\u00eamio",
        "cidade": "Porto Alegre"
    },
    "arbitros": {
        "arbitro_principal": {
            "nome": "Bruno Arleu de Araujo",
            "categoria": "AB",
            "regiao": "RJ"
        },
        "arbitro_segundo": {
            "nome": "Rodrigo Figueiredo Henrique Correa",
            "categoria": "FIFA",
            "regiao": "RJ"
        },
        "arbitro_terceiro": {
            "nome": "Thiago Henrique Neto Correa Farinha",
            "categoria": "AB",
            "regiao": "RJ"
        },
        "arbitro_quarto": {
            "nome": "Alexandre Vargas Tavares de Jesus",
            "categoria": "AB",
            "regiao": "RJ"
        }
    },
    "delegado": "Marcos Roberto Caduri de Almeida",
    "analista": "Jose Mocellin",
    "mandante_entrada": [
        {
            "hora": "10:50",
            "atraso": 0
        },
        {
            "hora": "12:01",
            "atraso": 0
        }
    ],
    "visitante_entrada": [
        {
            "hora": "10:54",
            "atraso": 4
        },
        {
            "hora": "12:02",
            "atraso": 0
        }
    ],
    "tempo_1": [
        {
            "hora": "11:02",
            "atraso": 2
        },
        {
            "hora": "11:50",
            "acrecimo": 3
        }
    ],
    "tempo_2": [
        {
            "hora": "12:05",
            "atraso": 0
        },
        {
            "hora": "12:54",
            "acrecimo": 4
        }
    ],
    "placar": [
        {
            "Gr\u00eamio": 0,
            "Santos": 2
        },
        {
            "Gr\u00eamio": 1,
            "Santos": 2
        }
    ],
    "cartoes_amarelos": [
        {
            "hora": "10:00",
            "tempo": 2,
            "num": 5,
            "nome": "Alison Lopes Ferreira",
            "time": "Santos"
        },
        {
            "hora": "23:00",
            "tempo": 2,
            "num": 21,
            "nome": "Diego Cristiano Evaristo",
            "time": "Santos"
        },
        {
            "hora": "39:00",
            "tempo": 2,
            "num": 28,
            "nome": "Lucas Verissimo da Silva",
            "time": "Santos"
        },
        {
            "hora": "03:00",
            "tempo": 2,
            "num": 17,
            "nome": "Derlis Alberto Gonzalez Galeano",
            "time": "Santos"
        },
        {
            "hora": "07:00",
            "tempo": 2,
            "num": 14,
            "nome": "Matheus Henrique de Souza",
            "time": "Gr\u00eamio"
        },
        {
            "hora": "33:00",
            "tempo": 1,
            "num": 8,
            "nome": "Maicon Thiago Pereira de Souza",
            "time": "Gr\u00eamio"
        },
        {
            "hora": "38:00",
            "tempo": 1,
            "num": 4,
            "nome": "Walter Kannemann",
            "time": "Gr\u00eamio"
        }
    ],
    "cartoes_vemelhos": [],
    "substituicoes": [
        {
            "hora": "45:00",
            "tempo": "INT",
            "time": "Santos",
            "entrada_numero": 5,
            "entrada_nome": "Alison Lopes Ferreira 4",
            "saida_numero": 1,
            "saida_nome": "Jean Mota Oliveira de Sousa"
        },
        {
            "hora": "06:00",
            "tempo": 2,
            "time": "Gr\u00eamio",
            "entrada_numero": 9,
            "entrada_nome": "Diego Tardelli Martins 2",
            "saida_numero": 3,
            "saida_nome": "Alisson Euler de Freitas Cas"
        },
        {
            "hora": "14:00",
            "tempo": 2,
            "time": "Gr\u00eamio",
            "entrada_numero": 7,
            "entrada_nome": "Luan Guilherme de Jesus Vieira 2",
            "saida_numero": 1,
            "saida_nome": "Jean Pyerre Casagrande Silve"
        },
        {
            "hora": "21:00",
            "tempo": 2,
            "time": "Santos",
            "entrada_numero": 17,
            "entrada_nome": "Derlis Alberto Gonzalez Gale",
            "saida_numero": 27,
            "saida_nome": "Eduardo Colcenti Antunes"
        },
        {
            "hora": "28:00",
            "tempo": 2,
            "time": "Gr\u00eamio",
            "entrada_numero": 10,
            "entrada_nome": "Felipe dos Reis Pereira Vize",
            "saida_numero": 12,
            "saida_nome": "Bruno Cortes Barbosa"
        },
        {
            "hora": "36:00",
            "tempo": 2,
            "time": "Santos",
            "entrada_numero": 7,
            "entrada_nome": "Carlos Andres Sanchez Arcosa 3",
            "saida_numero": 0,
            "saida_nome": "Jean Lucas de Souza Oliveira"
        }
    ],
    "gols": [
        {
            "hora": "05:00",
            "tempo": 1,
            "tipo": "NR",
            "numero": 27,
            "nome": "Eduardo Colcenti Antunes",
            "time": "Santos"
        },
        {
            "hora": "35:00",
            "tempo": 1,
            "tipo": "NR",
            "numero": 36,
            "nome": "Felipe Jonatan Rocha Andrade",
            "time": "Santos"
        }
    ]
}
```