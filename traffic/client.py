from logging import INFO, FileHandler, getLogger
from random import random
from time import sleep, time

from cmn import get_arg
from requests import get

host = get_arg("--host")
port = get_arg("--port")
stats_file = get_arg("--stats")

logger = getLogger("stats")
logger.handlers.clear()
logger.addHandler(FileHandler(stats_file))
logger.setLevel(INFO)

i = 1

def send_request(host:str, port:int):
    return get(f"http://{host}:{port}", timeout=5)

print("running client traffic simulation ...")
while True:
    now = time()
    state = None
    try:
        send_request(host, port)
        state = "SUCCESS"
    except Exception as e:
        state = "FAILED"
        print(e)


    logger.info(f"{i},{(time() - now) * 1000},{state}")
    i += 1
    sleep(random())
