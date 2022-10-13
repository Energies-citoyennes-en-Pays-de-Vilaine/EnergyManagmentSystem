from typing import Any

class UpdateChecked():
    def __init__(self) -> None:
        self.has_been_updated   = False
    def __setattr__(self, __name: str, __value: Any) -> None:
        if (__name != "has_been_updated" and __value != self.__getattribute__(__name)):
            self.has_been_updated = True
        super().__setattr__(__name, __value)
        