import curses
import calendar
from enum import IntEnum

CALENDAR_SPACING = 2
DAY_DIGITS = 2
DAYS_IN_WEEK = 7
CALENDAR_HEIGHT = 11
CALENDAR_WIDTH = 6 * CALENDAR_SPACING + DAYS_IN_WEEK * DAY_DIGITS
WEEK_DAYS = ["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"]


class ColorPair(IntEnum):
    ERROR = 1
    WEEK_DAY = 2
    DAY_NOT_SELECTED_HAS_NO_CURSOR = 3
    DAY_SELECTED_HAS_NO_CURSOR = 4
    DAY_NOT_SELECTED_HAS_CURSOR = 5
    DAY_SELECTED_HAS_CURSOR = 6


def init_colors():
    curses.init_pair(ColorPair.ERROR, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(ColorPair.WEEK_DAY, curses.COLOR_GREEN, curses.COLOR_BLACK)

    curses.init_pair(
        ColorPair.DAY_NOT_SELECTED_HAS_NO_CURSOR,
        curses.COLOR_CYAN,
        curses.COLOR_BLACK,
    )

    curses.init_pair(
        ColorPair.DAY_SELECTED_HAS_NO_CURSOR,
        curses.COLOR_BLACK,
        curses.COLOR_CYAN,
    )

    curses.init_pair(
        ColorPair.DAY_NOT_SELECTED_HAS_CURSOR,
        curses.COLOR_YELLOW,
        curses.COLOR_BLACK,
    )

    curses.init_pair(
        ColorPair.DAY_SELECTED_HAS_CURSOR, curses.COLOR_BLACK, curses.COLOR_YELLOW
    )


def get_color_pair_for_calendar_day(
    day: tuple[int, int],
    selected_days_positions: set[tuple[int, int]],
    cursor_position: tuple[int, int],
) -> int:
    day_is_selected = day in selected_days_positions
    day_has_cursor = day == cursor_position
    color_pair_int = 0

    if not day_is_selected and not day_has_cursor:
        color_pair_int = ColorPair.DAY_NOT_SELECTED_HAS_NO_CURSOR
    elif day_is_selected and not day_has_cursor:
        color_pair_int = ColorPair.DAY_SELECTED_HAS_NO_CURSOR
    elif not day_is_selected and day_has_cursor:
        color_pair_int = ColorPair.DAY_NOT_SELECTED_HAS_CURSOR
    elif day_is_selected and day_has_cursor:
        color_pair_int = ColorPair.DAY_SELECTED_HAS_CURSOR

    return curses.color_pair(color_pair_int)


def draw_calendar(window: curses.window, year: int, month: int):
    month_name = calendar.month_name[month]
    month_and_year = f"{month_name} {year}"
    start_y, start_x = 1, 1

    window.addstr(
        start_y, start_x, f"{month_and_year:^{CALENDAR_WIDTH}}", curses.A_BOLD
    )

    for idx, day in enumerate(WEEK_DAYS):
        window.addstr(
            start_y + 1,
            start_x + idx * 4,
            day,
            curses.color_pair(ColorPair.WEEK_DAY) | curses.A_BOLD,
        )


def draw_calendar_days(
    window: curses.window,
    calendar_matrix: list[list[int]],
    selected_days_positions: set[tuple[int, int]],
    cursor_position: tuple[int, int],
):
    start_y, start_x = 1, 1

    for week_idx, week in enumerate(calendar_matrix):
        for day_idx, day in enumerate(week):
            if day == 0:
                continue

            color_pair = get_color_pair_for_calendar_day(
                (week_idx, day_idx), selected_days_positions, cursor_position
            )

            window.addstr(
                start_y + 2 + week_idx,
                start_x + day_idx * (CALENDAR_SPACING + DAY_DIGITS),
                f"{day:2}",
                color_pair,
            )


def draw_help_text(window):
    window.addstr(1, 0, "Arrows: Navigate across days")
    window.addstr(2, 0, "F7/Page Up: Previous month")
    window.addstr(3, 0, "F8/Page Down: Next Month")
    window.addstr(4, 0, "F3/q: Exit")
    window.addstr(5, 0, "Enter: Confirm")

    window.addstr(
        7, 0, "You can only select days in", curses.color_pair(ColorPair.ERROR)
    )
    window.addstr(
        8, 0, "a single month per execution", curses.color_pair(ColorPair.ERROR)
    )


def move_cursor_left_until_day(
    calendar_matrix: list[list[int]], cursor_position: tuple[int, int]
):
    week_idx, day_idx = cursor_position
    day_idx = (day_idx + DAYS_IN_WEEK - 1) % DAYS_IN_WEEK

    while calendar_matrix[week_idx][day_idx] == 0:
        day_idx = (day_idx + DAYS_IN_WEEK - 1) % DAYS_IN_WEEK

    return week_idx, day_idx


def move_cursor_right_until_day(
    calendar_matrix: list[list[int]], cursor_position: tuple[int, int]
):
    week_idx, day_idx = cursor_position
    day_idx = (day_idx + 1) % DAYS_IN_WEEK

    while calendar_matrix[week_idx][day_idx] == 0:
        day_idx = (day_idx + 1) % DAYS_IN_WEEK

    return week_idx, day_idx


def move_cursor_up_until_day(
    calendar_matrix: list[list[int]], cursor_position: tuple[int, int]
):
    week_idx, day_idx = cursor_position
    weeks_in_month = len(calendar_matrix)
    week_idx = (week_idx + weeks_in_month - 1) % weeks_in_month

    while calendar_matrix[week_idx][day_idx] == 0:
        week_idx = (week_idx + weeks_in_month - 1) % weeks_in_month

    return week_idx, day_idx


def move_cursor_down_until_day(
    calendar_matrix: list[list[int]], cursor_position: tuple[int, int]
):
    week_idx, day_idx = cursor_position
    weeks_in_month = len(calendar_matrix)
    week_idx = (week_idx + 1) % weeks_in_month

    while calendar_matrix[week_idx][day_idx] == 0:
        week_idx = (week_idx + 1) % weeks_in_month

    return week_idx, day_idx


def toggle_day_selection(
    selected_days_positions: set[tuple[int, int]], cursor_position: tuple[int, int]
):
    if cursor_position in selected_days_positions:
        selected_days_positions.discard(cursor_position)
    else:
        selected_days_positions.add(cursor_position)


def get_previous_month(year: int, month: int) -> tuple[int, int]:
    if month == 1:
        return year - 1, 12
    else:
        return year, month - 1


def get_next_month(year: int, month: int) -> tuple[int, int]:
    if month == 12:
        return year + 1, 1
    else:
        return year, month + 1


def curses_main(
    stdscr: curses.window,
    init_year: int,
    init_month: int,
) -> tuple[int, int, list[int]]:
    curses.curs_set(0)
    init_colors()
    stdscr.clear()

    year, month = init_year, init_month

    calendar.setfirstweekday(calendar.SUNDAY)
    calendar_matrix = calendar.monthcalendar(year, month)
    selected_days_positions = set()

    calendar_window = curses.newwin(CALENDAR_HEIGHT, CALENDAR_WIDTH + 2, 0, 0)
    calendar_window.keypad(True)

    cursor_position = move_cursor_right_until_day(calendar_matrix, (0, 0))

    draw_calendar(calendar_window, year, month)
    draw_calendar_days(
        calendar_window, calendar_matrix, selected_days_positions, cursor_position
    )

    text_window = curses.newwin(CALENDAR_HEIGHT, 30, 0, CALENDAR_WIDTH + 4)

    draw_help_text(text_window)

    calendar_window.refresh()
    text_window.refresh()
    curses.doupdate()

    while True:
        key = calendar_window.getch()

        if key in (ord("q"), ord("Q"), curses.KEY_F3):
            selected_days_positions.clear()
            break

        if key in (curses.KEY_ENTER, 10, 13):
            break

        if key == curses.KEY_RIGHT:
            cursor_position = move_cursor_right_until_day(
                calendar_matrix, cursor_position
            )

        if key == curses.KEY_LEFT:
            cursor_position = move_cursor_left_until_day(
                calendar_matrix, cursor_position
            )

        if key == curses.KEY_UP:
            cursor_position = move_cursor_up_until_day(calendar_matrix, cursor_position)

        if key == curses.KEY_DOWN:
            cursor_position = move_cursor_down_until_day(
                calendar_matrix, cursor_position
            )

        if key in (curses.KEY_F7, curses.KEY_PPAGE):
            year, month = get_previous_month(year, month)
            calendar_matrix = calendar.monthcalendar(year, month)
            cursor_position = move_cursor_right_until_day(calendar_matrix, (0, 0))
            selected_days_positions.clear()
            calendar_window.clear()
            draw_calendar(calendar_window, year, month)

        if key in (curses.KEY_F8, curses.KEY_NPAGE):
            year, month = get_next_month(year, month)
            calendar_matrix = calendar.monthcalendar(year, month)
            cursor_position = move_cursor_right_until_day(calendar_matrix, (0, 0))
            selected_days_positions.clear()
            calendar_window.clear()
            draw_calendar(calendar_window, year, month)

        if key == ord(" "):
            toggle_day_selection(selected_days_positions, cursor_position)

        draw_calendar_days(
            calendar_window, calendar_matrix, selected_days_positions, cursor_position
        )

        calendar_window.noutrefresh()
        curses.doupdate()

    return (
        year,
        month,
        sorted(
            calendar_matrix[week_idx][day_idx]
            for week_idx, day_idx in selected_days_positions
        ),
    )
