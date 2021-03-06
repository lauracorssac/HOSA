from enum import Enum

class MenuOption(Enum):
    ACTIVATE_BUZZER = 1
    DEACTIVATE_BUZZER = 2

    @classmethod
    def get_option(cls, value):
        if value in cls._value2member_map_:
            return MenuOption(value)
        else:
            return None
