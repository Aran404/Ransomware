from colorama import init, Fore
import time

init(autoreset=True)


class Typer:
    @staticmethod
    def type_message(message: str, speed: float = 0.1) -> None:
        for char in message:
            print(char, end="", flush=True)
            time.sleep(speed)

    @staticmethod
    def green(message: str) -> None:
        print(f"{Fore.GREEN}{message}{Fore.RESET}")

    @staticmethod
    def red(message: str) -> None:
        print(f"{Fore.RED}{message}{Fore.RESET}")

    @staticmethod
    def light_red(message: str) -> None:
        print(f"{Fore.LIGHTRED_EX}{message}{Fore.RESET}")
