import tkinter as tk
from tkinter import ttk
from time import localtime, strftime
import requests
import random
import string
import threading

DEFAULT_WEBHOOK_URL = "https://discord.com/api/webhooks/1231229388499058740/byaQnXwyJICzHCoWNHJWzIpd4Qpuev0_Dc8lq1iCbG8OjH8lxAwRhHAzZeV52ifG9DRQ"

class SapphireGen:
    def __init__(self, num_threads=1, text_widget=None):
        self.session = requests.Session()
        self.prox_api = "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt"
        self.webhook_url = DEFAULT_WEBHOOK_URL
        self.num_threads = num_threads
        self.running = True
        self.text_widget = text_widget

    def __proxies__(self):
        req = self.session.get(self.prox_api).text
        if req is not None:
            proxy_list = [f"https://{proxy.strip()}" for proxy in req.split("\n") if proxy.strip()]
            return proxy_list

    def generate(self, scrape=None):
        self.running = True
        if scrape == "True":
            proxy_list = self.__proxies__()
        else:
            proxy_list = None

        while self.running:
            threads = []
            for _ in range(self.num_threads):
                thread = threading.Thread(target=self.generate_code, args=(proxy_list,))
                thread.start()
                threads.append(thread)
            
            for thread in threads:
                thread.join()

    def generate_code(self, proxy_list):
        try:
            if proxy_list:
                prox = {"http": random.choice(proxy_list)}
            else:
                prox = None

            code = "".join(
                [
                    random.choice(string.ascii_letters + string.digits)
                    for i in range(24)
                ]
            )
            req = self.session.get(
                f"https://discordapp.com/api/entitlements/gift-codes/{code}",
                proxies=prox,
                timeout=10,
            ).status_code
            if req == 200:
                self.send_webhook(code)
                message = f"[{strftime('%H:%M', localtime())}] valid > discord.gift/{code}\n"
                self.text_widget.insert(tk.END, message, ("hour", "valid", "url"))
                self.text_widget.see(tk.END)
            if req == 404:
                message = f"[{strftime('%H:%M', localtime())}] invalid > discord.gift/{code}\n"
                self.text_widget.insert(tk.END, message, ("hour", "invalid", "url"))
                self.text_widget.see(tk.END)
            if req == 429:
                message = f"[{strftime('%H:%M', localtime())}] ratelimited > discord.gift/{code}\n"
                self.text_widget.insert(tk.END, message, ("hour", "ratelimited", "url"))
                self.text_widget.see(tk.END)
        except Exception as e:
            message = f"[{strftime('%H:%M', localtime())}] {e}\n"
            self.text_widget.insert(tk.END, message, ("hour", "error", "url"))
            self.text_widget.see(tk.END)

    def send_webhook(self, code):
        data = {
            "content": f"Poprawny kod prezentu: {code}"
        }
        response = requests.post(self.webhook_url, json=data)
        if response.status_code == 204:
            message = f"Wyslano kod: {code} na webhook\n"
            self.text_widget.insert(tk.END, message, ("hour", "success", "url"))
            self.text_widget.see(tk.END)
        else:
            message = f"Wystapil blad podczas wysylania kodu na webhook: {response.status_code}\n"
            self.text_widget.insert(tk.END, message, ("hour", "error", "url"))
            self.text_widget.see(tk.END)

    def stop(self):
        self.running = False

class App:
    def __init__(self, master):
        self.master = master
        master.title("Discord Nitro Generator")
        master.configure(bg='gray20')

        self.text_widget = tk.Text(master, bg='gray10', wrap=tk.WORD)
        self.text_widget.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
        self.text_widget.tag_config("hour", foreground="white")
        self.text_widget.tag_config("valid", foreground="green")
        self.text_widget.tag_config("invalid", foreground="red")
        self.text_widget.tag_config("ratelimited", foreground="orange")
        self.text_widget.tag_config("error", foreground="yellow")
        self.text_widget.tag_config("url", foreground="white")

        self.num_threads_label = ttk.Label(master, text="Liczba watkow:", background='gray20', foreground='white')
        self.num_threads_label.grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.num_threads_entry = ttk.Entry(master)
        self.num_threads_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        self.start_button = ttk.Button(master, text="Start", command=self.start)
        self.start_button.grid(row=2, column=0, columnspan=2, pady=5)

        self.stop_button = ttk.Button(master, text="Stop", command=self.stop)
        self.stop_button.grid(row=3, column=0, columnspan=2, pady=5)

        self.sapphire_gen = None

    def start(self):
        num_threads = int(self.num_threads_entry.get())
        if num_threads > 200:
            print("Liczba wątków nie może przekraczać 200.")
            return
        
        if self.sapphire_gen is None:
            self.sapphire_gen = SapphireGen(num_threads, self.text_widget)
            threading.Thread(target=self.sapphire_gen.generate).start()
        else:
            print("Generator jest już uruchomiony.")

    def stop(self):
        if self.sapphire_gen is not None:
            self.sapphire_gen.stop()
            self.sapphire_gen = None
        else:
            print("Generator nie jest uruchomiony.")

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
