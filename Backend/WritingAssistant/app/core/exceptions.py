from typing import Any, Dict, Optional


class DomainError(Exception):

    def __init__(self, detail: Any = None, headers: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(detail)
        self.detail = detail
        self.headers = headers


class DuplicatedError(DomainError):
    pass


class AuthError(DomainError):
    pass


class NotFoundError(DomainError):
    pass


class ValidationError(DomainError):
    pass


class ConflictError(DomainError):
    pass
