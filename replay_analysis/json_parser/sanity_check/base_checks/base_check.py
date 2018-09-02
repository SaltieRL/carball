from typing import TypeVar, Generic, List, Optional, ClassVar

from ..errors.errors import CheckError, CheckErrorLevel

T = TypeVar('T')


class BaseCheck(Generic[T]):
    error_class = CheckError
    class_message: ClassVar[str]

    def __init__(self, obj: T):
        self.obj = obj

    def run_check(self) -> List[CheckError]:
        check_functions_to_error_levels = {
            self.critical_checks: CheckErrorLevel.CRITICAL,
            self.major_checks: CheckErrorLevel.MAJOR,
            self.minor_checks: CheckErrorLevel.MINOR
        }
        errors = []
        for check_function, error_level in check_functions_to_error_levels.items():
            errors += [
                self.error_class(error_level, f"{self.class_message}: {e}")
                for e in check_function() if e is not None
            ]

        return errors

    def critical_checks(self) -> List[Optional[AssertionError]]:
        return []

    def major_checks(self) -> List[Optional[AssertionError]]:
        return []

    def minor_checks(self) -> List[Optional[AssertionError]]:
        return []

    @staticmethod
    def check(condition: bool, message: str) -> Optional[AssertionError]:
        if not condition:
            return AssertionError(message)
