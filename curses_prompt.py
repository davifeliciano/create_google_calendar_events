import curses
from enum import IntEnum
from dataclasses import dataclass


@dataclass
class PromptField:
    label: str
    value: str
    y: int
    x: int
    maxlen: int
    is_error: bool = False


class ColorPair(IntEnum):
    ERROR = 1
    GREEN = 2
    BLUE = 3


class CursesPrompt:
    PROMPT_HEIGHT = 7
    PROMPT_WIDTH = 60
    PROMPT_START_Y = 1
    PROMPT_START_X = 1

    def __init__(self, event_name: str, calendar_name: str):
        self.current_field = 0
        self.fields = [
            PromptField(
                label="Event Name:",
                value=event_name,
                y=2,
                x=2,
                maxlen=40,
                is_error=False,
            ),
            PromptField(
                label="Calendar Name:",
                value=calendar_name,
                y=4,
                x=2,
                maxlen=37,
                is_error=False,
            ),
        ]

        self.window = curses.newwin(
            self.PROMPT_HEIGHT,
            self.PROMPT_WIDTH,
            self.PROMPT_START_Y,
            self.PROMPT_START_X,
        )

        curses.curs_set(1)
        self.init_colors()
        self.window.keypad(True)

    @staticmethod
    def init_colors():
        curses.init_pair(ColorPair.ERROR, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(ColorPair.GREEN, curses.COLOR_GREEN, curses.COLOR_BLACK)

        curses.init_pair(
            ColorPair.BLUE,
            curses.COLOR_CYAN,
            curses.COLOR_BLACK,
        )

    def draw(self):
        self.window.clear()
        self.window.border(0)

        for field in self.fields:
            color_pair = (
                curses.color_pair(ColorPair.ERROR)
                if field.is_error
                else curses.color_pair(ColorPair.GREEN)
            )

            self.window.addstr(field.y, field.x, field.label, color_pair)

            self.window.addstr(
                field.y,
                field.x + len(field.label) + 1,
                field.value + " " * (field.maxlen - len(field.value)),
                curses.color_pair(ColorPair.BLUE),
            )

        if any(field.is_error for field in self.fields):
            self.window.addstr(
                0, 2, " Please fill in all fields! ", curses.color_pair(ColorPair.ERROR)
            )

        self.window.addstr(6, 2, " Tab: Next | Enter: Confirm | F3: Cancel ")
        self.window.refresh()

    def handle_tab(self):
        self.current_field = (self.current_field + 1) % len(self.fields)

    def handle_enter(self) -> tuple[str, str] | None:
        if all(field.value.strip() for field in self.fields):
            return (
                self.fields[0].value.strip(),
                self.fields[1].value.strip(),
            )

        for field in self.fields:
            field.is_error = not field.value.strip()

    def handle_backspace(self):
        field = self.fields[self.current_field]

        if len(field.value) > 0:
            field.value = field.value[:-1]

    def handle_input(self, key: int):
        field = self.fields[self.current_field]

        if len(field.value) < field.maxlen:
            field.value += chr(key)

    def curses_main(self) -> tuple[str, str]:
        while True:
            self.draw()

            field = self.fields[self.current_field]
            label_len = len(field.label)
            self.window.move(field.y, field.x + label_len + 1 + len(field.value))
            key = self.window.getch()

            if key == curses.KEY_F3:
                return "", ""

            elif key in (9, curses.KEY_BTAB):
                self.handle_tab()

            elif key in (curses.KEY_ENTER, 10, 13):
                result = self.handle_enter()

                if result is not None:
                    return result

            elif key in (curses.KEY_BACKSPACE, 127, 8):
                self.handle_backspace()

            elif 32 <= key <= 126:
                self.handle_input(key)


def curses_main(
    stdscr: curses.window,
    event_name: str = "",
    calendar_name: str = "",
) -> tuple[str, str]:
    curses_prompt = CursesPrompt(event_name, calendar_name)
    return curses_prompt.curses_main()
