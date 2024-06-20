# Webshare Proxy Generator

# Warning

This script doesn't handle much errors. You will need to be a dev to fix them and understand how this works.

This project automates the process of creating accounts on Webshare, solving captchas, and downloading proxies. It supports multi-threading to run multiple instances concurrently.

## Features

- Proxyless operation support
- Captcha solving using CapMonster or CapSolver
- Multi-threaded execution
- Configurable via a JSON file
- Thread-safe logging

## Prerequisites

- Python 3.x
- `requests` library
- `colorama` library
- `capmonster_python` library
- `capsolver` library

## Installation

1. Clone the repository:

   ```sh
   git clone https://github.com/Its3rr0rsWRLD/WebshareGenerator.git
   cd WebshareGenerator
   ```

2. Install the required dependencies:
   ```sh
   pip install requests colorama capmonster_python capsolver
   ```

## Configuration

The script will prompt you to configure the necessary settings on the first run. Configuration options include:

- Proxyless operation
- Captcha API Key
- Captcha Service (`capmonster` or `capsolver`)
- Headless mode
- Number of threads

The configuration is saved in `config.json`.

## Usage

1. Run the main script:

   ```sh
   python generator.py
   ```

   Or click on the `generator.bat` file to run the script.

2. The script will read the configuration from `config.json` and start the specified number of threads.

## Customization

### `Webshare` Class

The `Webshare` class handles the main logic, including solving captchas, registering accounts, and downloading proxies.

## Notes:

- The proxies are from webshare, so the quality is going to be bad.

## Disclaimer

> This project is for educational purposes only. The author will not be responsible for misuse of the information provided.
