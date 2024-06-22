import requests
import random
import threading
import string
from src.log import log
from capmonster_python import RecaptchaV2Task
import capsolver

download_proxies_lock = threading.Lock()

class Webshare:
    WEBSITE_KEY = "6LeHZ6UUAAAAAKat_YS--O2tj_by3gv3r_l03j9d"

    def __init__(self, proxyless, captcha_apikey, captcha_service, proxies):
        self.proxyless = proxyless
        self.captcha_apikey = captcha_apikey
        self.service = captcha_service
        self.proxies = proxies
        self.session = requests.Session()
        self.user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
        self.captcha_key = None
        self.used_captcha_key = False

        self.session.headers = {
            "User-Agent": self.user_agent
        }

        if not proxyless:
            self.select_new_proxy()

    def select_new_proxy(self):
        selected_proxy = random.choice(self.proxies) if self.proxies else None

        if selected_proxy:
            proxy_address = selected_proxy.split(":")[0]
            port = selected_proxy.split(":")[1]
            username = selected_proxy.split(":")[2]
            password = selected_proxy.split(":")[3]

            if username and password:
                proxy_string = f"{username}:{password}@{proxy_address}:{port}"
            else:
                proxy_string = f"{proxy_address}:{port}"

            self.session.proxies = {
                'https': f'http://{proxy_string}',
                'http': f'http://{proxy_string}'
            }
        else:
            self.session.proxies = None

    @staticmethod
    def solve_captcha(api_key: str, service_name: str, user_agent: str):
        if service_name == "capmonster":
            capmonster = RecaptchaV2Task(api_key)
            task_id = capmonster.create_task("https://webshare.io", Webshare.WEBSITE_KEY)
            result = capmonster.join_task_result(task_id)
            return result.get("gRecaptchaResponse")
        elif service_name == "capsolver":
            capsolver.api_key = api_key
            return capsolver.solve({
                "type": "ReCaptchaV2TaskProxyLess",
                "websiteURL": "https://webshare.io",
                "userAgent": user_agent,
                "websiteKey": Webshare.WEBSITE_KEY
            })['gRecaptchaResponse']
        else:
            raise Exception("Invalid captcha service")

    def register(self):
        log.log("[+] Solving Captcha", "purple")

        if not self.captcha_key or self.used_captcha_key:
            self.captcha_key = Webshare.solve_captcha(self.captcha_apikey, self.service, self.user_agent)

        log.log("[+] Captcha Solved", "purple")

        url = 'https://proxy.webshare.io/api/v2/register/'
        payload = {
            "email": f"{''.join(random.choice(string.ascii_letters) for _ in range(random.randint(10, 14)))}@gmail.com",
            "password": f"Joker{random.randint(2000, 5000)}!",
            "tos_accepted": True,
            "recaptcha": self.captcha_key
        }

        response = self.session.post(url, json=payload)
        self.used_captcha_key = False
        self.captcha_key = None

        self.session.cookies = response.cookies

        result = response.json()

        try:
            token = result['token']
        except KeyError:
            if "throttle" in result.get('detail'):
                raise Exception("[!] Rate Limited - Please change your VPN/IP location and run the script again.")

            raise Exception(f"[!] Error: {result}")

        return token

    def download_proxies(self):
        url = 'https://proxy.webshare.io/api/v2/proxy/list/?mode=direct&page=1&page_size=10'
        response = self.session.get(url)
        proxies = response.json().get('results', [])

        if not proxies:
            raise Exception("No proxies found.")

        with download_proxies_lock:
            with open("output.txt", 'a+') as f:
                for proxy in proxies:
                    proxy_string = self.format_proxy(proxy)
                    f.write(proxy_string + "\n")

        return proxies

    def format_proxy(self, proxy):
        return f"{proxy['proxy_address']}:{proxy['port']}:{proxy['username']}:{proxy['password']}"

    def generate_proxies(self):
        try:
            auth_token = self.register()
            log.log("[*] Created Webshare Account", "cyan")
            self.session.headers['Authorization'] = f"Token {auth_token}"

            proxies = self.download_proxies()
            log.log(f"[*] {len(proxies)} Proxies Generated!", "green")
            self.select_new_proxy()

        except requests.RequestException as e:
            log.log("[!] Proxy Failed " + str(e), "red")

        except Exception as e:
            log.log(f"[!] {str(e)}", "red")
