from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup


class Screen:
    def __init__(self, obj: dict) -> None:
        self.obj = obj
        self.name = obj["name"]
        self.rows = []
        self.callbackButtonFunctions = {}
        self.requiredKeys_ = ["text", "name"]
        self.markup = None
        # check if all required keys are present
        for key in self.requiredKeys_:
            if key not in self.obj:
                raise Exception("Missing key: " + key)
        if "rows" in obj:
            for row in obj["rows"]:
                for button in row:
                    if "text" not in button or "callbackData" not in button:
                        msg = f"Missing key: text or callback in {button}"
                        raise Exception(msg)
                    if "_" in button["callbackData"]:
                        msg = f'Button callback cannot contain "_", name: "{button}"'
                        raise Exception(msg)
        self.menuName = obj["menuName"]
        self.text = obj["text"]
        self.create_markup()

    def __str__(self) -> str:
        return f"Screen: {self.text}, callback: {self.name}, nRows: {len(self.rows)}"

    def create_markup(self) -> list[list[InlineKeyboardButton]]:
        if "rows" in self.obj:
            for row in self.obj["rows"]:
                t_row = []
                for button in row:
                    self.callbackButtonFunctions[button["callbackData"]] = button["callbackFunction"]
                    t_row.append(
                        InlineKeyboardButton(
                            button["text"],
                            callback_data=f'{button["callbackData"]}_{self.menuName}',
                        )
                    )
                self.rows.append(t_row)
        return self.rows

    def build(self) -> None:
        self.markup = InlineKeyboardMarkup(self.rows)
