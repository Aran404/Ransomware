from typing import Any
from typing_extensions import Self
from dataclasses import dataclass

__all__ = ["RansomTransaction"]


@dataclass
class RansomTransaction:
    success: bool
    uuid: str
    time_before_deactivation: int
    address: str
    amount: float
    payment_id: str

    @classmethod
    def from_dict(cls, obj: Any) -> Self:
        _success = bool(obj.get("success"))
        _uuid = str(obj.get("uuid"))
        _time_before_deactivation = int(obj.get("time_before_deactivation"))
        _address = str(obj.get("address"))
        _amount = float(obj.get("amount"))
        _payment_id = str(obj.get("payment_id"))
        return cls(
            success=_success,
            uuid=_uuid,
            time_before_deactivation=_time_before_deactivation,
            address=_address,
            amount=_amount,
            payment_id=_payment_id,
        )
