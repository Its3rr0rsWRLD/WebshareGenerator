import requests
import random
import threading
import string
import json
from capmonster_python import RecaptchaV2Task
import capsolver
import os

def log(msg: str, color: str):
    if not isinstance(msg, str):
        msg = str(msg)
    if color == "red":
        print(f"\033[91m{msg}\033[00m")
    elif color == "green":
        print(f"\033[92m{msg}\033[00m")
    elif color == "yellow":
        print(f"\033[93m{msg}\033[00m")
    elif color == "blue":
        print(f"\033[94m{msg}\033[00m")
    elif color == "purple":
        print(f"\033[95m{msg}\033[00m")
    elif color == "cyan":
        print(f"\033[96m{msg}\033[00m")
    else:
        print(msg)
    with open ("log.txt", "a+") as f:
        f.write(msg + "\n")

class Webshare:
    def __init__(self, proxyless=False, log_rotating=False, captcha_key="", captcha_service='capmonster'):
        self.proxyless = proxyless
        self.captcha_key = captcha_key
        self.log_rotating = log_rotating
        self.service = captcha_service
        self.session = requests.Session()
        self.proxies = [prox.strip() for prox in open("proxies.txt")] if not proxyless else []
        self.prox = random.choice(self.proxies) if self.proxies else None
        self.errored = 0
        self.should_stop = False
        
        self.session.headers = {
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
        }

        if not proxyless and self.prox:
            self.session.proxies = {
                'https': f'http://{self.prox}',
                'http': f'http://{self.prox}'
            }

    @staticmethod
    def solve_captcha(key: str, service: str):
        if service == "capmonster":
            capmonster = RecaptchaV2Task(key)
            task_id = capmonster.create_task("https://webshare.io", "6LeHZ6UUAAAAAKat_YS--O2tj_by3gv3r_l03j9d")
            result = capmonster.join_task_result(task_id)
            return result.get("gRecaptchaResponse")
        else:
            capsolver.api_key = key
            return capsolver.solve({
                "type": "ReCaptchaV2TaskProxyLess",
                "websiteURL": "https://webshare.io",
                "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
                "websiteKey": "6LeHZ6UUAAAAAKat_YS--O2tj_by3gv3r_l03j9d"
            })['gRecaptchaResponse']

    def register(self):
        if self.should_stop:
            return None
        log("[+] Solving Captcha", "purple")

        if not self.proxyless:
            try:
                response = self.session.get("https://webshare.io", timeout=10)
                if response.status_code != 200:
                    log("[!] Proxy Failed", "red")
                    return self.check()
            except:
                log("[!] Proxy Failed", "red")
                # remove the errored proxy
                with open("proxies.txt", "w") as f:
                    f.write("\n".join([prox for prox in self.proxies if prox != self.prox]))

                self.proxies = [prox.strip() for prox in open("proxies.txt")]
                self.prox = random.choice(self.proxies) if self.proxies else None
                self.session.proxies = {
                    'https': f'http://{self.prox}',
                    'http': f'http://{self.prox}'
                }
                return self.check()

        captcha_key = Webshare.solve_captcha(self.captcha_key, self.service)
        if captcha_key is None:
            return self.begin()
        log("[+] Captcha Solved", "purple")
        url = 'https://proxy.webshare.io/api/v2/register/'
        payload = {
            "email": f"{''.join(random.choice(string.ascii_letters) for _ in range(random.randint(10, 14)))}@gmail.com",
            "password": f"Joker{random.randint(2000, 5000)}!",
            "tos_accepted": True,
            "recaptcha": captcha_key
        }
        response = self.session.post(url, json=payload, proxies=self.session.proxies)
        self.session.cookies = response.cookies
        try:
            return response.json()['token']
        except:
            log(response.json(), "red")
            if response.json()['detail']:
                log(f"[!] {response.json()['detail']}", "red")
                # exit
                self.should_stop = True
                return None
            return self.check()

    def download_proxies(self):
        if self.should_stop:
            return
        url = 'https://proxy.webshare.io/api/v2/proxy/list/?mode=direct&page=1&page_size=10'
        for proxy in self.session.get(url).json()['results']:
            if self.log_rotating:
                with open("output.txt", 'a+') as f:
                    f.write(f"{proxy['username']}-rotate:{proxy['password']}@p.webshare.io:80\n")
                log("[+] Proxies Generated!", "green")
                break
            else:
                with open("output.txt", 'a+') as f:
                    f.write(f"{proxy['proxy_address']}:{proxy['port']}:{proxy['username']}:{proxy['password']}\n")
                # with open("proxies.txt", 'a+') as f:
                #    f.write(f"{proxy['username']}:{proxy['password']}@{proxy['proxy_address']}:{proxy['port']}\n")
        log(f"[*] Proxies Generated!", "green")

    def begin(self):
        if self.should_stop:
            return
        token = self.register()
        if token:
            log("[*] Created Webshare Account", "cyan")
            self.session.headers['Authorization'] = f"Token {token}"
            self.download_proxies()
            return self.begin()
        else:
            log("[!] Failed to create Webshare account.", "red")

    def check(self):
            self.errored += 1
            return self.begin()

def start_webshare():
    with open("config.json") as f:
        data = json.load(f)
        choice1 = "y" if data['proxyless'] else "n"
        captcha_key = data['captcha_apikey']
        captcha_service = data['captcha_service']
    choice2 = "1"
    ws = Webshare(proxyless=True if choice1.lower() == 'y' else False, log_rotating=True if choice2.lower() == '2' else False, captcha_key=captcha_key, captcha_service=captcha_service)
    ws.begin()

if __name__ == "__main__":
    os.system("title Webshare Generator")
    #os.system("mode con: cols=30 lines=5")
    num_threads = 1
    threads = []
    for _ in range(num_threads):
        t = threading.Thread(target=start_webshare)
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
