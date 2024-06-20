import os

if os.name == 'nt':
    os.system("cls")
else:
    os.system("clear")

import json
import requests
import colorama
import threading
from src.webshare import Webshare

colorama.init()

threads = 1

def update():
    with open("version.txt") as f:
        current_version = f.read().strip()
    try:
        version = requests.get("https://raw.githubusercontent.com/Its3rr0rsWRLD/WebshareGenerator/main/version.txt").text.strip()
        vnum = [int(i) for i in version.split(".")]
        cvnum = [int(i) for i in current_version.split(".")]
        if vnum > cvnum:
            print(f"Update available! {current_version} -> {version}")
            print("Do you want to update? (y/n): ", end="")
            update = input().strip().lower()
            if update == 'y':
                os.system("git pull")
                print("Updated successfully. Restart the program.")
                exit()
        else:
            pass
    except Exception as e:
        print(f"An error occurred while checking for updates: {e}")

def create_config():
    print("Proxyless? [Recommended] (y/n): ", end="")
    proxyless = input().strip().lower()
    print("Captcha API Key: ", end="")
    captcha_apikey = input().strip()
    print("Captcha Service (capmonster/capsolver): ", end="")
    captcha_service = input().strip().lower()
    print("Proxy File? [Leave Blank If Proxyless] (filename): ", end="")
    proxy_file = input().strip().lower()
    print("Thread count: ", end="")
    threads = int(input().strip())

    data = {
        "proxyless": proxyless == 'y',
        "captcha_apikey": captcha_apikey,
        "captcha_service": captcha_service,
        "proxy_file": proxy_file,
        "threads": threads
    }

    with open("config.json", "w") as f:
        json.dump(data, f, indent=4)

    print("Config saved. To edit the config, open config.json")

def worker(proxyless, captcha_apikey, captcha_service, proxies):
    webshare = Webshare(proxyless, captcha_apikey, captcha_service, proxies)
    while True:
        webshare.generate_proxies()

def main():
    if not os.path.exists("config.json"):
        create_config()

    with open("config.json") as f:
        data = json.load(f)
        proxyless = data.get("proxyless")
        captcha_apikey = data.get("captcha_apikey")
        captcha_service = data.get("captcha_service")
        proxy_file = data.get("proxy_file")
        threads = data.get("threads")

    if not proxyless and proxy_file:
        with open(proxy_file) as proxy_file:
            proxies = proxy_file.read().splitlines()
    else:
        proxies = []

    print("You can stop generation by pressing CTRL + C\n")

    thread_list = []
    for _ in range(threads):
        thread = threading.Thread(target=worker, args=(proxyless, captcha_apikey, captcha_service, proxies), daemon=True)
        thread_list.append(thread)
        thread.start()

    try:
        while True:
            pass
    except KeyboardInterrupt:
        for thread in thread_list:
            thread.join()

if __name__ == "__main__":
    update()
    main()