import curses


def draw(window: curses.window, fields: list[dict], current_field: int):
    window.clear()
    window.border(0)

    for idx, field in enumerate(fields):
        label = field["label"]
        value = field["value"]
        window.addstr(field["y"], field["x"], label)

        if idx == current_field:
            window.attron(curses.A_REVERSE)

        window.addstr(
            field["y"],
            field["x"] + len(label) + 1,
            value + " " * (field["maxlen"] - len(value)),
        )

        if idx == current_field:
            window.attroff(curses.A_REVERSE)

    window.addstr(6, 2, " Tab: Next | Enter: Confirm | F3: Cancel ")
    window.refresh()


def curses_main(
    stdscr: curses.window,
    event_name: str = "",
    calendar_name: str = "",
) -> tuple[str, str]:
    curses.curs_set(1)
    stdscr.clear()
    stdscr.refresh()

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
        },
        {
            "label": "Calendar Name:",
            "value": calendar_name,
            "y": 4,
            "x": 2,
            "maxlen": 37,
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
            if all(f["value"].strip() for f in fields):
                return fields[0]["value"].strip(), fields[1]["value"].strip()

        elif key in (curses.KEY_BACKSPACE, 127, 8):
            if len(field["value"]) > 0:
                field["value"] = field["value"][:-1]

        elif 32 <= key <= 126:
            if len(field["value"]) < field["maxlen"]:
                field["value"] += chr(key)
