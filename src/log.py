class log:
    def log(msg: str, color: str):
        if not isinstance(msg, str):
            msg = str(msg)
        if color == "red":
            print(f"\033[91m{msg}\033[00m")
        elif color == "green":
            print(f"\033[92m{msg}\033[00m")
        elif color == "yellow":
            print(f"\033[93m{msg}\033[00m")
        elif color == "blue":
            print(f"\033[94m{msg}\033[00m")
        elif color == "purple":
            print(f"\033[95m{msg}\033[00m")
        elif color == "cyan":
            print(f"\033[96m{msg}\033[00m")
        else:
            print(msg)