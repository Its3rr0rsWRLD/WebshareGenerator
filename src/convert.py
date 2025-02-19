import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
from typing import Optional, List
from enum import Enum

class ProxyFormat(Enum):
    USER_PASS_AT_IP_PORT = "user:pass@ip:port"
    USER_PASS_IP_PORT = "user:pass:ip:port"
    IP_PORT_USER_PASS = "ip:port:user:pass"

class ProxyConverter:
    """Handles proxy format conversion operations."""

    @staticmethod
    def parse_proxy(proxy: str, current_format: str, desired_format: str) -> Optional[str]:
        """
        Parse and convert a proxy string from one format to another.
        
        Args:
            proxy: The proxy string to convert
            current_format: The current format of the proxy string
            desired_format: The desired output format
            
        Returns:
            Converted proxy string or None if conversion fails
        """
        try:
            # Extract components based on current format
            if current_format == ProxyFormat.USER_PASS_AT_IP_PORT.value:
                user_pass, ip_port = proxy.split('@', 1)
                user, passwd = user_pass.split(':', 1)
                ip, port = ip_port.split(':')
            elif current_format == ProxyFormat.USER_PASS_IP_PORT.value:
                user, passwd, ip, port = proxy.split(':')
            elif current_format == ProxyFormat.IP_PORT_USER_PASS.value:
                ip, port, user, passwd = proxy.split(':')
            else:
                raise ValueError(f"Unsupported format: {current_format}")

            # Convert to desired format
            if desired_format == ProxyFormat.USER_PASS_AT_IP_PORT.value:
                return f"{user}:{passwd}@{ip}:{port}"
            elif desired_format == ProxyFormat.USER_PASS_IP_PORT.value:
                return f"{user}:{passwd}:{ip}:{port}"
            elif desired_format == ProxyFormat.IP_PORT_USER_PASS.value:
                return f"{ip}:{port}:{user}:{passwd}"
            else:
                raise ValueError(f"Unsupported format: {desired_format}")

        except ValueError as e:
            messagebox.showerror("Error", f"Invalid proxy format: {proxy}")
            return None

    @staticmethod
    def convert_file(file_path: str, current_format: str, desired_format: str) -> bool:
        """
        Convert all proxies in a file from one format to another.
        
        Args:
            file_path: Path to the proxy file
            current_format: Current format of the proxies
            desired_format: Desired output format
            
        Returns:
            bool: True if conversion was successful, False otherwise
        """
        try:
            with open(file_path, 'r') as file:
                proxies = [line.strip() for line in file if line.strip()]

            converted_proxies = []
            for proxy in proxies:
                converted = ProxyConverter.parse_proxy(proxy, current_format, desired_format)
                if converted:
                    converted_proxies.append(converted)
                else:
                    return False

            with open(file_path, 'w') as file:
                file.write('\n'.join(converted_proxies) + '\n')

            messagebox.showinfo("Success", "Proxies converted successfully.")
            return True

        except Exception as e:
            messagebox.showerror("Error", f"File operation failed: {str(e)}")
            return False

def main():
    """Main application entry point."""
    root = tk.Tk()
    root.withdraw()

    formats = [f.value for f in ProxyFormat]
    format_str = ", ".join(formats)

    current_format = simpledialog.askstring(
        "Input", 
        f"Enter the current proxy format ({format_str}):"
    )
    if not current_format or current_format not in formats:
        messagebox.showerror("Error", "Invalid format selected")
        return

    desired_format = simpledialog.askstring(
        "Input", 
        f"Enter the desired proxy format ({format_str}):"
    )
    if not desired_format or desired_format not in formats:
        messagebox.showerror("Error", "Invalid format selected")
        return

    file_path = filedialog.askopenfilename(
        title="Select the proxy file",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )
    if not file_path:
        return

    ProxyConverter.convert_file(file_path, current_format, desired_format)

if __name__ == "__main__":
    main()
