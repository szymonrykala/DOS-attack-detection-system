import tkinter as ttk

from .detector import DOSDetector


class App(ttk.Frame):
    def __init__(self, master):
        master.geometry("150x120")
        master.title("Dos Detect")
        super().__init__(master)
        self.pack(fill="both", expand=True, side="top")

        self.detector = DOSDetector()
        self.detector.set_alert_callback(self.__set_alert)
        self.detector.set_safe_callback(self.__remove_alert)

        self.message = ttk.StringVar(value="Not started")
        self.btn_mess = ttk.StringVar(value="Run detector")

        self.label = ttk.Label(
            self, textvariable=self.message, bg="gray", font=("Arial", 21)
        )
        self.label.pack(fill="both", expand=True, side="top")
        # self.label.bind("<Button-1>", self.__on_click)  # testing purposes

        ttk.Button(self, textvariable=self.btn_mess, command=self.__detector_btn_click).pack(
            side="bottom", fill="both"
        )
        self.__set_idle()

    def __set_idle(self):
        self.message.set("Not\nstarted")
        self.btn_mess.set("Run detector")
        self.label.configure(background="gray")

    def __set_alert(self):
        self.message.set("Attack\ndetected!")
        self.label.configure(background="red")

    def __remove_alert(self):
        self.message.set("Machine\nsafe")
        self.label.configure(background="green")

    def __detector_btn_click(self):
        if self.detector.is_on:
            self.__set_idle()
            self.btn_mess.set("Run detector")
            self.detector.off()
        else:
            self.__remove_alert()
            self.btn_mess.set("Stop detector")
            self.detector.on()

    def __on_click(self, *_):
        if self.label.cget("background") == "green":
            self.__set_alert()
        else:
            self.__remove_alert()

