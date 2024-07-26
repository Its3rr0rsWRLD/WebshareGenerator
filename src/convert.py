import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox

def parse_proxy(proxy, current_format, desired_format):
    if current_format == "user:pass@ip:port":
        user, rest = proxy.split(':', 1)
        passwd, ip_port = rest.split('@', 1)
        ip, port = ip_port.split(':')
    elif current_format == "user:pass:ip:port":
        user, passwd, ip, port = proxy.split(':')
    elif current_format == "ip:port:user:pass":
        ip, port, user, passwd = proxy.split(':')
    else:
        return None

    if desired_format == "user:pass@ip:port":
        return f"{user}:{passwd}@{ip}:{port}"
    elif desired_format == "user:pass:ip:port":
        return f"{user}:{passwd}:{ip}:{port}"
    elif desired_format == "ip:port:user:pass":
        return f"{ip}:{port}:{user}:{passwd}"
    else:
        return None

def convert_file(file_path, current_format, desired_format):
    try:
        with open(file_path, 'r') as file:
            proxies = file.readlines()
        
        converted_proxies = [
            parse_proxy(proxy.strip(), current_format, desired_format) for proxy in proxies
        ]

        with open(file_path, 'w') as file:
            for proxy in converted_proxies:
                file.write(proxy + "\n")
        
        messagebox.showinfo("Success", "Proxies converted successfully.")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def main():
    root = tk.Tk()
    root.withdraw()

    current_format = simpledialog.askstring("Input", "Enter the current proxy format (user:pass@ip:port, user:pass:ip:port, ip:port:user:pass):")
    if not current_format:
        return
    
    desired_format = simpledialog.askstring("Input", "Enter the desired proxy format (user:pass@ip:port, user:pass:ip:port, ip:port:user:pass):")
    if not desired_format:
        return

    file_path = filedialog.askopenfilename(title="Select the proxy file")
    if not file_path:
        return

    convert_file(file_path, current_format, desired_format)

if __name__ == "__main__":
    main()
