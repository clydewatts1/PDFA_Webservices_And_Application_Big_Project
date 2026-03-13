from __future__ import annotations

from datetime import datetime

HIGH_DATE_LITERAL = datetime(9999, 1, 1, 0, 0, 0)


class ValidationError(ValueError):
    def __init__(self, message: str, *, code: str = "validation_error") -> None:
        super().__init__(message)
        self.code = code


def validate_temporal_window(eff_from: datetime, eff_to: datetime) -> None:
    if eff_to < eff_from:
        raise ValidationError("EffToDateTime must be greater than or equal to EffFromDateTime", code="invalid_temporal_window")


def validate_delete_ind(delete_ind: int) -> None:
    if delete_ind not in (0, 1):
        raise ValidationError("DeleteInd must be 0 (active) or 1 (deleted)", code="invalid_delete_indicator")


def validate_instance_state(instance_state: str) -> None:
    if instance_state not in ("A", "I", "P"):
        raise ValidationError("InstanceState must be one of A, I, P", code="invalid_instance_state")


def is_active_row(delete_ind: int, eff_to: datetime) -> bool:
    return delete_ind == 0 and eff_to == HIGH_DATE_LITERAL
