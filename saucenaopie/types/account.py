from pydantic import BaseModel


class AccountInfo(BaseModel):
    """
    SauceNao account info ripped out of the header,
    such as user_id and current limits.
    """

    user_id: int
    account_type: str  # unregistered / free / enhanced
    short_limit: int
    long_limit: int
    long_remaining: int
    short_remaining: int
