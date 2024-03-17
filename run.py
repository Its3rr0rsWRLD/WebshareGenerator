import os
import time
import subprocess

os.system("cls")
os.system("title Webshare Generation Manager")

threads = input("\n[?] How many threads would you like to run? > ")
threads = int(threads)

with open("output.txt", "r") as f:
    lines = len(f.readlines())

old_lines = lines

firstTime = True

print("\n! This is only if you are getting rate limited very fast !\n")

reset = 0

def run():
    global reset, lines, threads, firstTime

    if reset >= 5:
        print("Rate limited too many times, stopping generator")
        time.sleep(3)
        return
    
    for _ in range(threads):
        os.system("start cmd /c python main.py")

    while True:

        with open("output.txt", "r") as f:
            new_lines = len(f.readlines())
            
        divided = (int(new_lines - lines))

        active_windows = 0
        for line in subprocess.check_output('tasklist /v', shell=True, encoding='utf-8').split("\n"):
            if "Webshare Generator" in line:
                active_windows += 1

        os.system("cls")

        print("\n[+] New proxies generated: " + str(int(divided)))
        print("[+] Total proxies generated: " + str(int(new_lines)))
        print("[+] Active threads: " + str(active_windows))

        try:
            tasks = subprocess.check_output('tasklist /v', shell=True, encoding='utf-8')
        except UnicodeDecodeError as e:
            print("[*] Uh oh! It seems like Discord is open. Discord can cause issues with the generator due to the way it handles window titles. Please close Discord and try again.")
            time.sleep(3)
            os.system("taskkill /f /im cmd.exe")
            os._exit(1)

        if "Webshare Generator" not in tasks:
            break

        if firstTime:
            time.sleep(6)
            firstTime = False
        else:
            time.sleep(2)

    reset = reset + 1

    print("Windows closed, restarting generator. Reset Number " + str(reset))

    run()

run()