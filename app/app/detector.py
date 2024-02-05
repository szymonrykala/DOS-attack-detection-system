import json
import os
from statistics import mean
from threading import Thread
from time import sleep

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np

from .netflow_collector import NetFlowCollector
from .traffic_store import (
    DeleteAfter,
    GetStatsRows,
    GetStatsSince,
    InsertMany,
    TrafficStore,
)

CLEANING_TIME = 3 * 60
ANALYZER_MEMORY = 60
Z_SCORE_TH = 2
VIEW_COUNT = 60
TOL = 1
REFRESH_TIME_SEC = 2


class TraficAnalyzer:
    def __init__(self, store: TrafficStore) -> None:
        self.__last = False
        self.__store = store

        self.traffic_data = self.__store.run(GetStatsRows(ANALYZER_MEMORY))
        self.z_score = self.get_z_score(self.traffic_data)

        fig, [self.traffic_chart, self.z_score_chart] = plt.subplots(
            2, 1, layout="constrained", sharex="all"
        )

        self.ani = animation.FuncAnimation(
            fig, self.update_chart, interval=REFRESH_TIME_SEC * 1000
        )

        plt.show(block=False)

    def run_analysys(self):
        recent_stats = self.__store.run(GetStatsSince(2))
        if recent_stats:
            self.__store.run(DeleteAfter(CLEANING_TIME))
            self.traffic_data = (self.traffic_data + recent_stats)[-ANALYZER_MEMORY:]
            self.z_score = self.get_z_score(self.traffic_data)

            if self.traffic_data:
                few = mean(self.z_score[-4:])
                more = mean(self.z_score[-6:])

                if few > Z_SCORE_TH:
                    self.__last = True
                elif more < few:
                    self.__last = False

        return self.__last

    def update_chart(self, *_):
        self.traffic_chart.clear()
        self.z_score_chart.clear()

        self.traffic_chart.plot(self.traffic_data[-VIEW_COUNT:])
        self.traffic_chart.set_ylabel("Traffic Volume")

        self.z_score_chart.plot(self.z_score[-VIEW_COUNT:])
        self.z_score_chart.set_ylabel("z-score")
        self.z_score_chart.set_xlabel("probes")

    def get_z_score(self, traffic):
        return np.abs((traffic - np.mean(traffic)) / np.std(traffic))


class DOSDetector:
    def __init__(self):
        self.store = TrafficStore()
        self.__is_on = False
        self.__alert_clb = lambda: print("callback not set")
        self.__safe_clb = lambda: print("callback not set")

        self.netflow_collector = NetFlowCollector()
        self.netflow_collector.set_payload_callback(self.__save_packets)
        self.dos_analyzer = TraficAnalyzer(store=self.store)

        self.thread = None

    @property
    def is_on(self):
        return self.__is_on

    def __save_packets(self, batch: tuple):
        self.store.run(InsertMany(*batch))

    def __run_detection(self):
        print("Starting detection")
        while self.__is_on:
            result = self.dos_analyzer.run_analysys()
            if result:
                self.__alert_clb()
            else:
                self.__safe_clb()
            sleep(REFRESH_TIME_SEC)

    def __dump_traffic(self):
        if os.environ.get("DUMP_TRAFFIC") == "true":
            with open("./data/normal_traffic_dump.json", "w+") as file:
                file.write(json.dumps(self.netflow_collector.buffer))

    def on(self):
        self.__is_on = True
        self.netflow_collector.listen_async()
        self.thread = Thread(target=self.__run_detection)
        self.thread.start()

    def off(self):
        print("Shutting down detector ...")
        self.__is_on = False
        self.netflow_collector.stop()
        self.__dump_traffic()
        self.thread.join()
        print("Detection stopped")

    def set_alert_callback(self, callback: callable):
        self.__alert_clb = callback

    def set_safe_callback(self, callback: callable):
        self.__safe_clb = callback
