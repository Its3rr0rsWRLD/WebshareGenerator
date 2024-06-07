import os

os.system("pip install -r requirements.txt")

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
    current_version = "1.1.2"
    try:
        version = requests.get("https://raw.githubusercontent.com/Its3rr0rsWRLD/WebshareGenerator/main/version.txt").text.strip()
        if version != current_version:
            print(f"Update available! {current_version} -> {version}")
            print("Do you want to update? (y/n): ", end="")
            update = input().strip().lower()
            if update == 'y':
                os.system("git pull")
                print("Updated successfully. Restart the program.")
                exit()
        else:
            print("No updates available.")
    except Exception as e:
        print(f"An error occurred while checking for updates: {e}")

def config():
    print("Proxyless? [Recommended] (y/n): ", end="")
    proxyless = input().strip().lower()
    print("Captcha API Key: ", end="")
    captcha_key = input().strip()
    print("Captcha Service (capmonster/capsolver): ", end="")
    captcha_service = input().strip().lower()
    print("Headless? (y/n): ", end="")
    headless = input().strip().lower()
    print("Thread count: ", end="")
    threads = int(input().strip())

    data = {
        "proxyless": proxyless == 'y',
        "captcha_apikey": captcha_key,
        "captcha_service": captcha_service,
        "headless": headless == 'y',
        "threads": threads
    }

    with open("config.json", "w") as f:
        json.dump(data, f, indent=4)

    print("Config saved. To edit the config, open config.json")

def worker(proxyless, captcha_key, captcha_service):
    webshare = Webshare(proxyless=proxyless, captcha_key=captcha_key, captcha_service=captcha_service)
    webshare.begin()

def main():
    if not os.path.exists("config.json"):
        config()

    with open("config.json") as f:
        data = json.load(f)
        proxyless = data.get("proxyless")
        captcha_key = data.get("captcha_apikey")
        captcha_service = data.get("captcha_service")
        threads = data.get("threads")

    thread_list = []
    for _ in range(threads):
        thread = threading.Thread(target=worker, args=(proxyless, captcha_key, captcha_service))
        thread_list.append(thread)
        thread.start()

    for thread in thread_list:
        thread.join()

if __name__ == "__main__":
    update()
    main()