import json
import gzip


def dict_compress(data):
    return gzip.compress(json.dumps(data).encode("latin-1"))


def compress_to_dict(data):
    return json.loads(gzip.decompress(data).decode("latin-1"))


def dict_to_string(data):
    return json.dumps(data)


def string_to_dict(data):
    return json.loads(data)
