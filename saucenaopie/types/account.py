from enum import Enum

from pydantic import BaseModel


class AccountType(str, Enum):
    UNREGISTERED = "unregistered"  # No longer relevant
    FREE = "free"
    ENHANCED = "enhanced"


class AccountInfo(BaseModel):
    """
    SauceNao account info ripped out of the header,
    such as user_id and current limits.
    """

    user_id: int
    account_type: AccountType
    short_limit: int
    long_limit: int
    long_remaining: int
    short_remaining: int
