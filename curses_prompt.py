import curses
from enum import IntEnum


class ColorPair(IntEnum):
    ERROR = 1
    GREEN = 2
    BLUE = 3


def init_colors():
    curses.init_pair(ColorPair.ERROR, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(ColorPair.GREEN, curses.COLOR_GREEN, curses.COLOR_BLACK)

    curses.init_pair(
        ColorPair.BLUE,
        curses.COLOR_CYAN,
        curses.COLOR_BLACK,
    )


def draw(window: curses.window, fields: list[dict], current_field: int):
    window.clear()
    window.border(0)

    for field in fields:
        x, y = field["x"], field["y"]
        label = field["label"]
        value = field["value"]
        maxlen = field["maxlen"]

        if field["is_error"]:
            window.addstr(y, x, label, curses.color_pair(ColorPair.ERROR))
        else:
            window.addstr(y, x, label, curses.color_pair(ColorPair.GREEN))

        window.addstr(
            y,
            x + len(label) + 1,
            value + " " * (maxlen - len(value)),
            curses.color_pair(ColorPair.BLUE),
        )

    if any(field["is_error"] for field in fields):
        window.addstr(
            0, 2, " Please fill in all fields! ", curses.color_pair(ColorPair.ERROR)
        )

    window.addstr(6, 2, " Tab: Next | Enter: Confirm | F3: Cancel ")
    window.refresh()


def curses_main(
    stdscr: curses.window,
    event_name: str = "",
    calendar_name: str = "",
) -> tuple[str, str]:
    curses.curs_set(1)
    init_colors()
    stdscr.clear()

    height, width = 7, 60
    start_y, start_x = 1, 1
    prompt_window = curses.newwin(height, width, start_y, start_x)
    prompt_window.keypad(True)

    fields = [
        {
            "label": "Event Name:",
            "value": event_name,
            "y": 2,
            "x": 2,
            "maxlen": 40,
            "is_error": False,
        },
        {
            "label": "Calendar Name:",
            "value": calendar_name,
            "y": 4,
            "x": 2,
            "maxlen": 37,
            "is_error": False,
        },
    ]

    current_field = 0

    while True:
        draw(prompt_window, fields, current_field)

        field = fields[current_field]
        label_len = len(field["label"])
        prompt_window.move(field["y"], field["x"] + label_len + 1 + len(field["value"]))
        key = prompt_window.getch()

        if key == curses.KEY_F3:
            return "", ""

        elif key in (9, curses.KEY_BTAB):
            current_field = (current_field + 1) % len(fields)

        elif key in (curses.KEY_ENTER, 10, 13):
            if all(field["value"].strip() for field in fields):
                return fields[0]["value"].strip(), fields[1]["value"].strip()

            for field in fields:
                field["is_error"] = not field["value"].strip()

        elif key in (curses.KEY_BACKSPACE, 127, 8):
            if len(field["value"]) > 0:
                field["value"] = field["value"][:-1]

        elif 32 <= key <= 126:
            if len(field["value"]) < field["maxlen"]:
                field["value"] += chr(key)
