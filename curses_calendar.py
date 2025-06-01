import curses
import calendar
from enum import IntEnum


class Calendar:
    def __init__(self, year: int, month: int):
        calendar.setfirstweekday(calendar.SUNDAY)
        self.year = year
        self.month = month
        self.days_matrix = calendar.monthcalendar(self.year, self.month)

    def _previous_month_year(self) -> tuple[int, int]:
        if self.month == 1:
            return self.year - 1, 12
        else:
            return self.year, self.month - 1

    def _next_month_year(self) -> tuple[int, int]:
        if self.month == 12:
            return self.year + 1, 1
        else:
            return self.year, self.month + 1

    def previous_month(self):
        self.year, self.month = self._previous_month_year()
        self.days_matrix = calendar.monthcalendar(self.year, self.month)

    def next_month(self):
        self.year, self.month = self._next_month_year()
        self.days_matrix = calendar.monthcalendar(self.year, self.month)

    def get_month_name(self) -> str:
        return calendar.month_name[self.month]


class ColorPair(IntEnum):
    ERROR = 1
    WEEK_DAY = 2
    DAY_NOT_SELECTED_HAS_NO_CURSOR = 3
    DAY_SELECTED_HAS_NO_CURSOR = 4
    DAY_NOT_SELECTED_HAS_CURSOR = 5
    DAY_SELECTED_HAS_CURSOR = 6


class CursesCalendar:
    CALENDAR_SPACING = 2
    DAY_DIGITS = 2
    DAYS_IN_WEEK = 7
    CALENDAR_HEIGHT = 11
    CALENDAR_WIDTH = 6 * CALENDAR_SPACING + DAYS_IN_WEEK * DAY_DIGITS
    WEEK_DAYS = ["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"]

    def __init__(self, year: int, month: int):
        self.year = year
        self.month = month
        self.calendar = Calendar(year, month)
        self.selected_days_positions: set[tuple[int, int]] = set()
        self.cursor_position = (0, 0)
        self.move_cursor_right_until_day()
        self.window = curses.newwin(self.CALENDAR_HEIGHT, self.CALENDAR_WIDTH + 2, 0, 0)
        self.help_text_window = curses.newwin(
            self.CALENDAR_HEIGHT, 30, 0, self.CALENDAR_WIDTH + 4
        )

        self._key_handlers = {
            curses.KEY_RIGHT: self.move_cursor_right_until_day,
            curses.KEY_LEFT: self.move_cursor_left_until_day,
            curses.KEY_UP: self.move_cursor_up_until_day,
            curses.KEY_DOWN: self.move_cursor_down_until_day,
            ord(" "): self.toggle_day_selection,
            curses.KEY_F7: self.previous_month,
            curses.KEY_PPAGE: self.previous_month,
            curses.KEY_F8: self.next_month,
            curses.KEY_NPAGE: self.next_month,
        }

        curses.curs_set(0)
        self.window.keypad(True)
        self.window.clear()
        self.init_colors()
        self.draw_calendar()
        self.draw_calendar_days()
        self.draw_help_text()

    @staticmethod
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

    def draw_calendar(self):
        month_name = self.calendar.get_month_name()
        month_and_year = f"{month_name} {self.calendar.year}"
        start_y, start_x = 1, 1

        self.window.addstr(
            start_y, start_x, f"{month_and_year:^{self.CALENDAR_WIDTH}}", curses.A_BOLD
        )

        for idx, day in enumerate(self.WEEK_DAYS):
            self.window.addstr(
                start_y + 1,
                start_x + idx * 4,
                day,
                curses.color_pair(ColorPair.WEEK_DAY) | curses.A_BOLD,
            )

    def get_color_pair_for_calendar_day(
        self,
        day_position: tuple[int, int],
    ) -> int:
        day_is_selected = day_position in self.selected_days_positions
        day_has_cursor = day_position == self.cursor_position
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

    def draw_calendar_days(self):
        start_y, start_x = 1, 1

        for week_idx, week in enumerate(self.calendar.days_matrix):
            for day_idx, day in enumerate(week):
                if day == 0:
                    continue

                color_pair = self.get_color_pair_for_calendar_day((week_idx, day_idx))

                self.window.addstr(
                    start_y + 2 + week_idx,
                    start_x + day_idx * (self.CALENDAR_SPACING + self.DAY_DIGITS),
                    f"{day:2}",
                    color_pair,
                )

    def draw_help_text(self):
        self.help_text_window.addstr(1, 0, "Arrows: Navigate across days")
        self.help_text_window.addstr(2, 0, "F7/Page Up: Previous month")
        self.help_text_window.addstr(3, 0, "F8/Page Down: Next Month")
        self.help_text_window.addstr(4, 0, "F3/q: Exit")
        self.help_text_window.addstr(5, 0, "Enter: Confirm")

        self.help_text_window.addstr(
            7, 0, "You can only select days in", curses.color_pair(ColorPair.ERROR)
        )
        self.help_text_window.addstr(
            8, 0, "a single month per execution", curses.color_pair(ColorPair.ERROR)
        )

    def move_cursor_left_until_day(self):
        week_idx, day_idx = self.cursor_position
        day_idx = (day_idx + self.DAYS_IN_WEEK - 1) % self.DAYS_IN_WEEK

        while self.calendar.days_matrix[week_idx][day_idx] == 0:
            day_idx = (day_idx + self.DAYS_IN_WEEK - 1) % self.DAYS_IN_WEEK

        self.cursor_position = week_idx, day_idx

    def move_cursor_right_until_day(self):
        week_idx, day_idx = self.cursor_position
        day_idx = (day_idx + 1) % self.DAYS_IN_WEEK

        while self.calendar.days_matrix[week_idx][day_idx] == 0:
            day_idx = (day_idx + 1) % self.DAYS_IN_WEEK

        self.cursor_position = week_idx, day_idx

    def move_cursor_up_until_day(self):
        week_idx, day_idx = self.cursor_position
        weeks_in_month = len(self.calendar.days_matrix)
        week_idx = (week_idx + weeks_in_month - 1) % weeks_in_month

        while self.calendar.days_matrix[week_idx][day_idx] == 0:
            week_idx = (week_idx + weeks_in_month - 1) % weeks_in_month

        self.cursor_position = week_idx, day_idx

    def move_cursor_down_until_day(self):
        week_idx, day_idx = self.cursor_position
        weeks_in_month = len(self.calendar.days_matrix)
        week_idx = (week_idx + 1) % weeks_in_month

        while self.calendar.days_matrix[week_idx][day_idx] == 0:
            week_idx = (week_idx + 1) % weeks_in_month

        self.cursor_position = week_idx, day_idx

    def toggle_day_selection(self):
        if self.cursor_position in self.selected_days_positions:
            self.selected_days_positions.discard(self.cursor_position)
        else:
            self.selected_days_positions.add(self.cursor_position)

    def previous_month(self):
        self.calendar.previous_month()
        self.selected_days_positions.clear()
        self.cursor_position = (0, 0)
        self.move_cursor_right_until_day()
        self.window.clear()
        self.draw_calendar()
        self.draw_calendar_days()

    def next_month(self):
        self.calendar.next_month()
        self.selected_days_positions.clear()
        self.cursor_position = (0, 0)
        self.move_cursor_right_until_day()
        self.window.clear()
        self.draw_calendar()
        self.draw_calendar_days()

    def handle_key(self, key: int):
        handler = self._key_handlers.get(key)

        if handler:
            handler()

    def get_selected_dates(self) -> list[str]:
        return sorted(
            f"{self.calendar.year}-{self.calendar.month:02d}-{day:02d}"
            for week_idx, day_idx in self.selected_days_positions
            if (day := self.calendar.days_matrix[week_idx][day_idx]) != 0
        )

    def curses_main(self) -> list[str]:
        self.window.refresh()
        self.help_text_window.refresh()
        curses.doupdate()

        while True:
            key = self.window.getch()

            if key in (ord("q"), ord("Q"), curses.KEY_F3):
                self.selected_days_positions.clear()
                break

            if key in (curses.KEY_ENTER, 10, 13):
                break

            self.handle_key(key)

            self.draw_calendar_days()
            self.window.noutrefresh()
            curses.doupdate()

        return self.get_selected_dates()


def curses_main(
    stdscr: curses.window,
    init_year: int,
    init_month: int,
) -> list[str]:
    stdscr.clear()
    curses_calendar = CursesCalendar(init_year, init_month)
    return curses_calendar.curses_main()
