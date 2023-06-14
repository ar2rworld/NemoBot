from src.menus.menu import Menu


class MissingMenuError(Exception):
    def __init__(self, menu_name: str, *args: object) -> None:
        super().__init__(*args)
        self.menu_name: str = menu_name
    def __str__(self) -> str:
        return super().__str__() + f"Missing menu: {self.menu_name} in the `bot_data` context"

class NoScreensMenuError(Exception):
    def __init__(self, menu: Menu, *args: object) -> None:
        super().__init__(*args)
        self.menu: Menu = menu
    def __str__(self) -> str:
        return super().__str__() + f"No screens in menu: {self.menu.name}\n{self.menu}"

class ScreenMenuError(Exception):
    def __init__(self, message: str, menu: Menu, *args: object) -> None:
        super().__init__(*args)
        self.message: str = message
        self.menu: Menu = menu
    def __str__(self) -> str:
        return super().__str__() + f"{self.message}\n{self.menu}"

class MenuError(Exception):
    def __init__(self, message: str, menu: Menu | None, *args: object) -> None:
        super().__init__(*args)
        self.message: str = message
        self.menu: Menu | None = menu
    def __str__(self) -> str:
        return super().__str__() + f"{self.message}\n{self.menu}"
