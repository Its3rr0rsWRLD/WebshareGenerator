import requests
import random
import threading
import string
import json
import os
from src.log import log
from capmonster_python import RecaptchaV2Task
import capsolver

class Webshare:
    def __init__(self, proxyless=False, captcha_key="", captcha_service='capmonster', proxies=None):
        self.proxyless = proxyless
        self.captcha_key = captcha_key
        self.service = captcha_service
        self.session = requests.Session()
        self.proxies = proxies
        self.prox = random.choice(self.proxies) if self.proxies else None
        self.errored = 0
        self.should_stop = False

        self.session.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
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

        log.log("[+] Solving Captcha", "purple")

        if not self.proxyless:
            try:
                response = self.session.get("https://webshare.io", timeout=10)
                if response.status_code != 200:
                    log.log("[!] Proxy Failed", "red")
                    return self.check()
            except requests.RequestException:
                log.log("[!] Proxy Failed", "red")
                self.update_proxies()
                return self.check()

        captcha_key = Webshare.solve_captcha(self.captcha_key, self.service)
        if captcha_key is None:
            return self.begin()
        log.log("[+] Captcha Solved", "purple")
        
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
        except KeyError:
            if response.json().get('detail'):
                log.log(f"[!] {response.json()['detail']}", "red")
                if "throttle" in response.json()['detail']:
                    log.log("[!] Rate Limited - Please change your VPN/IP location and run the script again.", "red")
                self.should_stop = True
                return None
            return self.check()

    def download_proxies(self):
        if self.should_stop:
            return
        
        url = 'https://proxy.webshare.io/api/v2/proxy/list/?mode=direct&page=1&page_size=10'
        response = self.session.get(url)
        proxies = response.json().get('results', [])

        if not proxies:
            log.log("[!] No proxies found.", "red")
            return

        with open("output.txt", 'a+') as f:
            for proxy in proxies:
                proxy_string = self.format_proxy(proxy)
                f.write(proxy_string + "\n")

        log.log(f"[*] {len(proxies)} Proxies Generated!", "green")

    def format_proxy(self, proxy):
        return f"{proxy['proxy_address']}:{proxy['port']}:{proxy['username']}:{proxy['password']}"

    def begin(self):
        if self.should_stop:
            return
        token = self.register()
        if token:
            log.log("[*] Created Webshare Account", "cyan")
            self.session.headers['Authorization'] = f"Token {token}"
            self.download_proxies()
            return self.begin()
        else:
            if self.should_stop:
                return
            log.log("[!] Failed to create Webshare account.", "red")

    def check(self):
        self.errored += 1
        return self.begin()