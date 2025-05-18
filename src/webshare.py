import requests
import random
import threading
import string
from dataclasses import dataclass
from typing import Optional, List
from src.log import log
from capmonster_python import RecaptchaV2Task
import capsolver


download_proxies_lock = threading.Lock()

@dataclass
class ProxyConfig:
    address: str
    port: str
    username: Optional[str] = None
    password: Optional[str] = None

class Webshare:
    WEBSITE_KEY = "6LeHZ6UUAAAAAKat_YS--O2tj_by3gv3r_l03j9d"
    BASE_URL = "https://proxy.webshare.io/api/v2"
    USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"

    def __init__(self, proxyless: bool, captcha_apikey: str, captcha_service: str, proxies: List[str], proxy_format: str):
        self.proxyless = proxyless
        self.captcha_apikey = captcha_apikey
        self.service = captcha_service
        self.proxies = proxies
        self.proxy_format = proxy_format
        self.session = self._create_session()
        self.captcha_key = None
        self.used_captcha_key = False
        self.current_proxy = None

    def _create_session(self) -> requests.Session:
        session = requests.Session()
        session.headers["User-Agent"] = self.USER_AGENT
        if not self.proxyless:
            self.select_new_proxy(session)
        return session

    def select_new_proxy(self, session: Optional[requests.Session] = None):
        if session is None:
            session = self.session
        if not self.proxies:
            session.proxies = None
            return
        selected_proxy = random.choice(self.proxies)
        self.current_proxy = selected_proxy
        proxy_config = self._parse_proxy(selected_proxy)
        proxy_string = self._format_proxy_string(proxy_config)
        session.proxies = {
            'https': f'http://{proxy_string}',
            'http': f'http://{proxy_string}'
        }

    def _parse_proxy(self, proxy: str) -> ProxyConfig:
        if '@' in proxy:
            auth, address = proxy.split('@')
            username, password = auth.split(':')
            host, port = address.split(':')
            return ProxyConfig(address=host, port=port, username=username, password=password)
        parts = proxy.split(":")
        if len(parts) == 2:
            return ProxyConfig(address=parts[0], port=parts[1])
        elif len(parts) == 4:
            return ProxyConfig(address=parts[0], port=parts[1], username=parts[2], password=parts[3])
        raise ValueError("Invalid proxy format")

    def _format_proxy_string(self, config: ProxyConfig) -> str:
        if config.username and config.password:
            return f"{config.username}:{config.password}@{config.address}:{config.port}"
        return f"{config.address}:{config.port}"

    @staticmethod
    def solve_captcha(api_key: str, service_name: str, user_agent: str) -> str:
        if service_name == "capmonster":
            capmonster = RecaptchaV2Task(api_key)
            task_id = capmonster.create_task("https://webshare.io", Webshare.WEBSITE_KEY)
            result = capmonster.join_task_result(task_id)
            return result.get("gRecaptchaResponse")
        elif service_name == "capsolver":
            capsolver.api_key = api_key
            result = capsolver.solve({
                "type": "ReCaptchaV2TaskProxyLess",
                "websiteURL": "https://webshare.io",
                "userAgent": user_agent,
                "websiteKey": Webshare.WEBSITE_KEY
            })
            return result['gRecaptchaResponse']
        raise ValueError("Invalid captcha service")

    def _generate_email(self):
        domains = ['gmail.com', 'outlook.com', 'yahoo.com', 'icloud.com']
        roots = [
            'pixel', 'alpha', 'drift', 'neo', 'astro', 'zenith', 'echo', 'nova', 'crypt', 'orbit',
            'dash', 'cloud', 'vibe', 'frost', 'hex', 'pulse', 'quant', 'terra', 'lumen', 'flux'
        ]
        suffixes = ['tv', 'hub', 'io', 'xd', 'on', 'lab', 'it', 'max', 'sys', 'hq']

        base = random.choice(roots)
        suffix = random.choice(suffixes)
        number = str(random.randint(10, 999)) if random.random() < 0.4 else ''

        username = f"{base}{suffix}{number}"

        return f"{username}@{random.choice(domains)}"


    def _generate_password(self):
        pwd_chars = (
            random.choices(string.ascii_lowercase, k=random.randint(4, 6)) +
            random.choices(string.ascii_uppercase, k=random.randint(2, 4)) +
            random.choices(string.digits, k=random.randint(2, 4)) +
            random.choices('!@#$%^&*', k=random.randint(1, 2))
        )
        random.shuffle(pwd_chars)
        return ''.join(pwd_chars)

    def register(self) -> str:
        log.log("[+] Solving Captcha", "purple")
        if not self.captcha_key or self.used_captcha_key:
            self.captcha_key = self.solve_captcha(self.captcha_apikey, self.service, self.USER_AGENT)
        log.log("[+] Captcha Solved", "purple")

        email = self._generate_email()
        password = self._generate_password()

        payload = {
            "email": email,
            "password": password,
            "tos_accepted": True,
            "recaptcha": self.captcha_key
        }

        response = self.session.post(f"{self.BASE_URL}/register/", json=payload)
        result = response.json()
        self.used_captcha_key = True
        self.captcha_key = None

        if 'token' not in result:
            if "throttle" in result.get('detail', ''):
                if self.current_proxy in self.proxies:
                    self.proxies.remove(self.current_proxy)
                raise RuntimeError("Rate Limited - Proxy removed. Please try with a new proxy.")
            raise RuntimeError(f"Error: {result}")

        return result['token']

    def download_proxies(self) -> List[dict]:
        response = self.session.get(f"{self.BASE_URL}/proxy/list/?mode=direct&page=1&page_size=10")
        proxies = response.json().get('results', [])
        if not proxies:
            raise RuntimeError("No proxies found.")
        with download_proxies_lock:
            with open("output.txt", 'a+') as f:
                for proxy in proxies:
                    f.write(f"{self.format_proxy(proxy)}\n")
        return proxies

    def format_proxy(self, proxy: dict) -> str:
        formats = {
            "ip:port": lambda p: f"{p['proxy_address']}:{p['port']}",
            "ip:port:username:password:=": lambda p: f"{p['proxy_address']}:{p['port']}:{p['username']}:{p['password']}",
            "ip:port:user:pass": lambda p: f"{p['proxy_address']}:{p['port']}:{p['username']}:{p['password']}",
            "username:password@ip:port": lambda p: f"{p['username']}:{p['password']}@{p['proxy_address']}:{p['port']}",
            "user:pass@ip:port": lambda p: f"{p['username']}:{p['password']}@{p['proxy_address']}:{p['port']}"
        }
        formatter = formats.get(self.proxy_format)
        if not formatter:
            raise ValueError("Invalid proxy format")
        return formatter(proxy)

    def generate_proxies(self):
        try:
            auth_token = self.register()
            log.log("[*] Created Webshare Account", "cyan")
            self.session.headers['Authorization'] = f"Token {auth_token}"
            proxies = self.download_proxies()
            log.log(f"[*] {len(proxies)} Proxies Generated!", "green")
            self.select_new_proxy()
        except requests.RequestException as e:
            log.log(f"[!] Proxy Failed: {str(e)}", "red")
            if self.current_proxy in self.proxies:
                self.proxies.remove(self.current_proxy)
            self.select_new_proxy()
        except Exception as e:
            log.log(f"[!] {str(e)}", "red")
