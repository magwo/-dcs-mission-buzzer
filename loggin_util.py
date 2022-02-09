from colorama import init, Fore, Back, Style

init()
from sys import stdout  # Needed for weird colorama hack on windows


def print_warning(msg: str):
    print(f"{Style.BRIGHT}{Fore.YELLOW}{msg}{Style.RESET_ALL}")


def print_error(msg: str):
    print(f"{Style.BRIGHT}{Fore.RED}{msg}{Style.RESET_ALL}")


def print_success(msg: str):
    print(f"{Fore.GREEN}{Style.BRIGHT}{msg}{Style.RESET_ALL}")


def print_bold(msg: str):
    print(f"{Style.BRIGHT}{msg}{Style.RESET_ALL}")
