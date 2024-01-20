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

