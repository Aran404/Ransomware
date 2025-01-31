import json
from dataclasses import asdict
from typing import Any, Dict

__all__ = ["Serializable"]


class Serializable:
    def to_json(self, omit_empty: bool = True) -> str:
        """Convert the dataclass to a JSON string."""
        d = self.to_dict(omit_empty)
        return json.dumps(d)

    def to_dict(self, omit_empty: bool = True) -> Dict[str, Any]:
        """Convert the dataclass to a dictionary."""
        if not hasattr(self, "__dataclass_fields__"):
            raise TypeError("to_dict can only be used with dataclasses.")

        kv = asdict(self)  # type: ignore
        return {k: v for k, v in kv.items() if v} if omit_empty else kv
