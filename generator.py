import os
import time
import json
import logging
from typing import List, Dict, Optional
from pathlib import Path
import requests
import colorama
import threading
from dotenv import load_dotenv
from src.webshare import Webshare

# Constants
CONFIG_FILE = "config.json"
VERSION_FILE = "version.txt"
VERSION_URL = "https://raw.githubusercontent.com/Its3rr0rsWRLD/WebshareGenerator/main/version.txt"

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ConfigManager:
    @staticmethod
    def create_config() -> Dict:
        config = {
            "proxyless": input("Proxyless? [Recommended] (y/n): ").strip().lower() == 'y',
            "captcha_apikey": input("Captcha API Key: ").strip(),
            "captcha_service": input("Captcha Service (capmonster/capsolver): ").strip().lower(),
            "proxy_file": input("Proxy File? [Leave Blank If Proxyless] (filename): ").strip().lower(),
            "threads": int(input("Thread count: ").strip()),
            "proxy_format": input("Proxy Format (ip:port:username:password, user:pass:ip:port, user:pass@ip:port): ").strip()
        }

        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=4)

        logger.info("Config saved successfully")
        return config

    @staticmethod
    def load_config() -> Dict:
        try:
            with open(CONFIG_FILE) as f:
                return json.load(f)
        except FileNotFoundError:
            return ConfigManager.create_config()
        except json.JSONDecodeError:
            logger.error("Invalid config file format")
            return ConfigManager.create_config()

def check_for_updates() -> None:
    try:
        with open(VERSION_FILE) as f:
            current_version = f.read().strip()

        response = requests.get(VERSION_URL, timeout=5)
        version = response.text.strip()

        if [int(i) for i in version.split(".")] > [int(i) for i in current_version.split(".")]:
            if input(f"Update available! {current_version} -> {version}\nDo you want to update? (y/n): ").lower() == 'y':
                os.system("git pull")
                if os.path.exists(CONFIG_FILE):
                    os.remove(CONFIG_FILE)
                input("Updated successfully. Config reset required. Press enter to exit.")
                exit(0)
    except Exception as e:
        logger.error(f"Update check failed: {e}")

def load_proxies(config: Dict) -> List[str]:
    if config["proxyless"] or not config["proxy_file"]:
        return []

    try:
        with open(config["proxy_file"]) as f:
            return f.read().splitlines()
    except FileNotFoundError:
        logger.warning(f"Proxy file {config['proxy_file']} not found, continuing without proxies")
        return []

class ProxyGenerator:
    def __init__(self, config: Dict, proxies: List[str]):
        self.config = config
        self.proxies = proxies
        self.stop_event = threading.Event()
        self.threads: List[threading.Thread] = []

    def worker(self) -> None:
        webshare = Webshare(
            self.config["proxyless"],
            self.config["captcha_apikey"],
            self.config["captcha_service"],
            self.proxies,
            self.config["proxy_format"]
        )
        while not self.stop_event.is_set():
            try:
                webshare.generate_proxies()
            except Exception as e:
                logger.error(f"Error in worker thread: {e}")

    def start(self) -> None:
        logger.info("Starting proxy generation. Press CTRL+C to stop.")
        for _ in range(self.config["threads"]):
            thread = threading.Thread(target=self.worker, daemon=True)
            self.threads.append(thread)
            thread.start()

    def stop(self) -> None:
        self.stop_event.set()
        for thread in self.threads:
            thread._stop()  # Force stop the thread
            thread.join(timeout=1.0)  # Wait max 1 second for each thread

def main() -> None:
    # Initialize colorama
    colorama.init()

    # Clear screen
    os.system("cls" if os.name == "nt" else "clear")

    # Check for updates
    check_for_updates()

    # Load configuration
    config = ConfigManager.load_config()

    # Load proxies
    proxies = load_proxies(config)

    # Initialize and start proxy generator
    generator = ProxyGenerator(config, proxies)
    try:
        generator.start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Stopping proxy generation...")
        generator.stop()

if __name__ == "__main__":
    main()