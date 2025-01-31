from colorama import init, Fore
from typing import Callable, TypeVar, ParamSpec
import functools
import random
import string
import time

init()
T = TypeVar("T")
P = ParamSpec("P")


def unix_to_hhmmss(ms: int) -> str:
    seconds = ms / 1000
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(hours):02}h:{int(minutes):02}m:{int(seconds):02}s"


def get_random_string(length: int) -> str:
    return "".join(random.choices(string.ascii_letters, k=length))


def get_random_numbers(length: int) -> str:
    return "".join(random.choices(string.digits, k=length))


class Typer:
    @staticmethod
    def type_message(message: str, /, speed: float = 0.1) -> None:
        for char in message:
            print(char, end="", flush=True)
            time.sleep(speed)

    @staticmethod
    def green(message: str, /, speed: float = 0.1) -> None:
        print(Fore.GREEN)
        Typer.type_message(message, speed=speed)
        print(Fore.RESET)

    @staticmethod
    def red(message: str, /, speed: float = 0.1) -> None:
        print(Fore.RED)
        Typer.type_message(message, speed=speed)
        print(Fore.RESET)

    @staticmethod
    def light_red(message: str, /, speed: float = 0.1) -> None:
        print(Fore.LIGHTRED_EX)
        Typer.type_message(message, speed=speed)
        print(Fore.RESET)


def except_pass(func: Callable[P, T]) -> Callable[P, T | None]:
    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T | None:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if e is KeyboardInterrupt:
                raise e
            return

    return wrapper
