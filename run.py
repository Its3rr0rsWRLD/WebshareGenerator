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
secondTime = False

print("\n! This is only if you are getting rate limited very fast !\n")

reset = 0

def run():
    global reset, lines, threads, firstTime, secondTime

    if reset >= 10:
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

        checkOutput = subprocess.check_output('tasklist /v', shell=True)

        checkOutput = checkOutput.decode('utf-8', 'ignore')
        checkOutput = checkOutput.encode('utf-8', 'ignore')
        checkOutput = str(checkOutput)

        for line in checkOutput.split("\\r\\n"):
            if "Webshare Generator" in line:
                active_windows += 1

        os.system("cls")

        print("\n[+] New proxies generated: " + str(int(divided)))
        print("[+] Total proxies generated: " + str(int(new_lines)))
        if active_windows == 0:
            print("[+] Active threads: " + str(threads))
        else:
            print("[+] Active threads: " + str(active_windows))

        try:
            tasks = subprocess.check_output('tasklist /v', shell=True, encoding='utf-8')
        except:
            continue

        if "Webshare Generator" not in tasks:
            break

        if firstTime:
            time.sleep(0)
            firstTime = False
            secondTime = True
        elif secondTime:
            time.sleep(10)
            secondTime = False
        else:
            continue

    reset = reset + 1

    print("Windows closed, restarting generator. Reset Number " + str(reset))

    run()

run()