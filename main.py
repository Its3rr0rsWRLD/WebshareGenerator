import os, json, random, string, threading, time, concurrent.futures
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Dict

import requests, colorama
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from capmonster_python import RecaptchaV2Task
import capsolver


class log:
    def log(msg: str, color: str = "reset"):
        msg = str(msg)
        codes = {
            "reset": "\033[0m",
            "red": "\033[91m",
            "green": "\033[92m",
            "yellow": "\033[93m",
            "blue": "\033[94m",
            "purple": "\033[95m",
            "cyan": "\033[96m",
        }
        print(f"{codes.get(color, codes['reset'])}{msg}{codes['reset']}")


class ProxyFormat(Enum):
    USER_PASS_AT_IP_PORT = "user:pass@ip:port"
    USER_PASS_IP_PORT = "user:pass:ip:port"
    IP_PORT_USER_PASS = "ip:port:user:pass"


class ProxyConverter:
    @staticmethod
    def parse(proxy: str, cur: str, out: str) -> Optional[str]:
        try:
            if cur == ProxyFormat.USER_PASS_AT_IP_PORT.value:
                up, ip_port = proxy.split("@")
                user, pwd = up.split(":")
                ip, port = ip_port.split(":")
            elif cur == ProxyFormat.USER_PASS_IP_PORT.value:
                user, pwd, ip, port = proxy.split(":")
            elif cur == ProxyFormat.IP_PORT_USER_PASS.value:
                ip, port, user, pwd = proxy.split(":")
            else:
                return None
            if out == ProxyFormat.USER_PASS_AT_IP_PORT.value:
                return f"{user}:{pwd}@{ip}:{port}"
            if out == ProxyFormat.USER_PASS_IP_PORT.value:
                return f"{user}:{pwd}:{ip}:{port}"
            if out == ProxyFormat.IP_PORT_USER_PASS.value:
                return f"{ip}:{port}:{user}:{pwd}"
        except ValueError:
            return None
        return None

    @staticmethod
    def convert_file(path: str, cur: str, out: str) -> bool:
        try:
            with open(path, "r", encoding="utf-8") as f:
                lines = [l.strip() for l in f if l.strip()]
            conv = [ProxyConverter.parse(p, cur, out) for p in lines]
            if None in conv:
                return False
            with open(path, "w", encoding="utf-8") as f:
                f.write("\n".join(conv) + "\n")
            return True
        except Exception as e:
            log.log(e, "red")
            return False


@dataclass
class ProxyConf:
    address: str
    port: str
    user: Optional[str] = None
    pwd: Optional[str] = None


class WebshareClient:
    WEBSITE_KEY = "6LeHZ6UUAAAAAKat_YS--O2tj_by3gv3r_l03j9d"
    BASE = "https://proxy.webshare.io/api/v2"
    UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
    TIMEOUT = (5, 20)

    def __init__(self, proxyless: bool, cap_key: str, cap_service: str, pool: List[str], fmt: str, max_pool: int = 64):
        self.proxyless = proxyless
        self.cap_key = cap_key
        self.cap_service = cap_service
        self.proxies = pool
        self.fmt = fmt
        self.session = self._sess(max_pool)
        self.ckey: Optional[str] = None
        self.used = False
        self.cur_proxy: Optional[str] = None
        self.domains = ["gmail.com", "outlook.com", "yahoo.com", "icloud.com"]
        self.roots = ["pixel", "alpha", "drift", "neo", "astro", "zenith", "echo", "nova", "crypt", "orbit", "dash", "cloud", "vibe", "frost", "hex", "pulse", "quant", "terra", "lumen", "flux"]
        self.suffixes = ["tv", "hub", "io", "xd", "on", "lab", "it", "max", "sys", "hq"]
        self.lock = threading.Lock()

    def _sess(self, max_pool):
        s = requests.Session()
        s.headers["User-Agent"] = self.UA
        ad = HTTPAdapter(pool_connections=max_pool, pool_maxsize=max_pool, max_retries=Retry(total=2, backoff_factor=0.2))
        s.mount("https://", ad)
        s.mount("http://", ad)
        if not self.proxyless:
            self._pick_proxy(s)
        return s

    def _pick_proxy(self, s=None):
        s = s or self.session
        if not self.proxies:
            s.proxies = {}
            return
        self.cur_proxy = random.choice(self.proxies)
        cfg = self._parse(self.cur_proxy)
        pstr = self._fmt(cfg)
        s.proxies = {"https": f"http://{pstr}", "http": f"http://{pstr}"}

    @staticmethod
    def _parse(p: str) -> ProxyConf:
        if "@" in p:
            auth, addr = p.split("@")
            user, pwd = auth.split(":")
            ip, prt = addr.split(":")
            return ProxyConf(ip, prt, user, pwd)
        pts = p.split(":")
        if len(pts) == 2:
            return ProxyConf(pts[0], pts[1])
        if len(pts) == 4:
            return ProxyConf(pts[0], pts[1], pts[2], pts[3])
        raise ValueError("bad proxy")

    @staticmethod
    def _fmt(c: ProxyConf):
        return f"{c.user}:{c.pwd}@{c.address}:{c.port}" if c.user and c.pwd else f"{c.address}:{c.port}"

    def _solve(self):
        if self.cap_service == "capmonster":
            task = RecaptchaV2Task(self.cap_key)
            tid = task.create_task("https://webshare.io", self.WEBSITE_KEY)
            return task.join_task_result(tid)["gRecaptchaResponse"]
        capsolver.api_key = self.cap_key
        res = capsolver.solve({"type": "ReCaptchaV2TaskProxyLess", "websiteURL": "https://webshare.io", "userAgent": self.UA, "websiteKey": self.WEBSITE_KEY})
        return res["gRecaptchaResponse"]

    def _rand_email(self):
        base = random.choice(self.roots)
        suf = random.choice(self.suffixes)
        num = str(random.randint(10, 999)) if random.random() < 0.4 else ""
        return f"{base}{suf}{num}@{random.choice(self.domains)}"

    def _rand_pwd(self):
        chars = random.choices(string.ascii_lowercase, k=random.randint(4, 6)) + random.choices(string.ascii_uppercase, k=random.randint(2, 4)) + random.choices(string.digits, k=random.randint(2, 4)) + random.choices("!@#$%^&*", k=random.randint(1, 2))
        random.shuffle(chars)
        return "".join(chars)

    def _register(self):
        if not self.ckey or self.used:
            self.ckey = self._solve()
            self.used = False
        js = {"email": self._rand_email(), "password": self._rand_pwd(), "tos_accepted": True, "recaptcha": self.ckey}
        r = self.session.post(f"{self.BASE}/register/", json=js, timeout=self.TIMEOUT)
        res = r.json()
        self.used = True
        self.ckey = None
        tok = res.get("token")
        if not tok:
            if "throttle" in res.get("detail", "") and self.cur_proxy in self.proxies:
                self.proxies.remove(self.cur_proxy)
            raise RuntimeError(res)
        return tok

    def _download(self, tok, page_size=50):
        self.session.headers["Authorization"] = f"Token {tok}"
        r = self.session.get(f"{self.BASE}/proxy/list/?mode=direct&page=1&page_size={page_size}", timeout=self.TIMEOUT)
        data = r.json().get("results", [])
        if not data:
            raise RuntimeError("empty list")
        with self.lock:
            with open("output.txt", "a", encoding="utf-8") as f:
                for p in data:
                    f.write(self._out(p) + "\n")
        return len(data)

    def _out(self, p: dict):
        if self.fmt == "ip:port":
            return f"{p['proxy_address']}:{p['port']}"
        if self.fmt in ("ip:port:username:password", "ip:port:user:pass"):
            return f"{p['proxy_address']}:{p['port']}:{p['username']}:{p['password']}"
        if self.fmt in ("user:pass@ip:port", "username:password@ip:port"):
            return f"{p['username']}:{p['password']}@{p['proxy_address']}:{p['port']}"
        raise ValueError("bad fmt")

    def generate_once(self):
        try:
            tok = self._register()
            log.log("[*] account", "cyan")
            cnt = self._download(tok)
            log.log(f"[*] {cnt} proxies", "green")
        except requests.RequestException as e:
            log.log(f"[!] {e}", "red")
            if self.cur_proxy in self.proxies:
                self.proxies.remove(self.cur_proxy)
        except Exception as e:
            log.log(f"[!] {e}", "red")
        finally:
            self._pick_proxy()


class ConfigManager:
    CFG = "config.json"

    @staticmethod
    def create() -> Dict:
        cfg = {
            "proxyless": input("proxyless? y/n: ").strip().lower() == "y",
            "captcha_apikey": input("captcha key: ").strip(),
            "captcha_service": input("captcha svc (capmonster/capsolver): ").strip().lower(),
            "proxy_file": input("proxy file [blank if proxyless]: ").strip(),
            "threads": int(input("threads: ").strip()),
            "proxy_format": input("proxy fmt (ip:port | ip:port:username:password | user:pass@ip:port): ").strip(),
        }
        with open(ConfigManager.CFG, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)
        return cfg

    @staticmethod
    def load() -> Dict:
        try:
            with open(ConfigManager.CFG, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return ConfigManager.create()


def load_proxies(cfg: Dict) -> List[str]:
    if cfg["proxyless"] or not cfg["proxy_file"]:
        return []
    try:
        with open(cfg["proxy_file"], "r", encoding="utf-8") as f:
            return [l.strip() for l in f if l.strip()]
    except FileNotFoundError:
        log.log("proxy file missing, proxyless mode", "yellow")
        return []


class ProxyGenerator:
    def __init__(self, cfg: Dict, proxies: List[str]):
        self.cfg = cfg
        self.proxies = proxies
        self.stop = threading.Event()

    def worker(self):
        client = WebshareClient(self.cfg["proxyless"], self.cfg["captcha_apikey"], self.cfg["captcha_service"], self.proxies, self.cfg["proxy_format"])
        while not self.stop.is_set():
            client.generate_once()

    def start(self):
        pool = []
        for _ in range(self.cfg["threads"]):
            t = threading.Thread(target=self.worker, daemon=True)
            pool.append(t)
            t.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            log.log("shutting down...", "yellow")
            self.stop.set()
            for t in pool:
                t.join()


def main():
    colorama.init()
    os.system("cls" if os.name == "nt" else "clear")
    cfg = ConfigManager.load()
    proxies = load_proxies(cfg)
    ProxyGenerator(cfg, proxies).start()


if __name__ == "__main__":
    main()
