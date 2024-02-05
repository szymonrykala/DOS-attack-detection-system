import os
import socket
from threading import Thread

from netflow import parse_packet

IP = os.environ.get("COLLECTOR_IP", "localhost")
PORT = int(os.environ.get("COLLECTOR_PORT", 5005))


class NetFlowCollector:
    def __init__(self, ip: str = IP, port: int = PORT):
        self.buffer = []
        self.__ip = ip
        self.__port = port
        self.thread: Thread = None
        self.__should_run = True
        self.__process_payload: callable = None

    def __setup_socket(self):
        print("setting up UDP socket")
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.bind((self.__ip, self.__port))

    def listen(self):
        self.__setup_socket()

        self.__should_run = True
        templates = {"netflow": {}, "ipfix": {}}

        print("NetFlowCollector listening...")
        while self.__should_run:
            try:
                data, client = self.udp_socket.recvfrom(4096)
                payload = parse_packet(data, templates)

                for flow in payload.flows:
                    self.__process_payload(tuple(flow.data for flow in payload.flows))

            except Exception as err:
                print(err)

    def listen_async(self) -> Thread:
        self.thread = Thread(name="NetFlowDetector", target=self.listen)
        self.thread.start()

    def stop(self):
        print("Shutting down NetFlowCollector")
        self.__should_run = False
        self.udp_socket.close()
        self.thread and self.thread.join()

    def set_payload_callback(self, func:callable):
        self.__process_payload = func


if __name__ == "__main__":
    collector = NetFlowCollector(IP, PORT)

    try:
        collector.listen()
    except KeyboardInterrupt:
        collector.stop()
        print("shuting down collector")
