import os
import time
import subprocess
import json

os.system("cls")
os.system("title Webshare Generation Manager")

threads = input("\n[?] How many threads would you like to run? > ")
threads = int(threads)

with open("output.txt", "r") as f:
    lines = len(f.readlines())

old_lines = lines

firstTime = True
secondTime = False

with open("log.txt", "w") as f:
    f.write("")

print("\n! This is only if you are getting rate limited very fast !\n")

reset = 0

looped = 0

def run():
    global reset, lines, threads, firstTime, secondTime, looped

    if reset >= 10:
        print("Rate limited too many times, stopping generator")
        time.sleep(3)
        return
    
    for _ in range(threads):
        with open("config.json") as f:
            data = json.load(f)
            if data['headless']:
                os.system("start /min cmd /c python main.py")
            else:
                os.system("start cmd /c python main.py")

    while True:

        if looped == 15:
            # get tasks
            tasks = subprocess.getoutput("tasklist").split("\n")
            # check if any "webshare generator" tasks are running
            running = [task for task in tasks if "Webshare Generator" in task.lower()]
            if len(running) == 0:
                # red
                #print("\033[91m" + "Uh oh! All threads have closed! Please contact the developer if this is a mistake." + "\033[0m")
                print("For some reason, windows is saying all threads have closed. This is a mistake, please ignore this message. If it is not a mistake, restart the generator.")

            looped = 0

            with open("log.txt", "w") as f:
                f.write("")


        with open("log.txt", "r") as f:
            log = f.read()
            os.system("cls")
            log = log.split("\n")
            for line in log:
                if line.startswith("[*]"):
                    if line.startswith("[*] Created"):
                        # cyan
                        print("\033[96m" + line + "\033[0m")
                    else:
                        # green
                        print("\033[92m" + line + "\033[0m")
                elif line.startswith("[!]"):
                    # red
                    print("\033[91m" + line + "\033[0m")
                else:
                    # purple
                    print("\033[95m" + line + "\033[0m")
        
        with open("output.txt", "r") as f:
            lines = len(f.readlines())

            print("\033[92m\n\n[ Total Proxies: " + str(lines) + " ; New Proxies: " + str(lines - old_lines) + " ]\033[0m")
        
        time.sleep(2)

        looped += 1

    reset = reset + 1

    print("Windows closed, restarting generator. Reset Number " + str(reset))

    time.sleep(3)

    with open("log.txt", "w") as f:
        f.write("")

    run()

run()