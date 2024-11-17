import curses
import datetime
import math
import calendar

from datetime import timedelta, time, datetime as dt
from dateutil.relativedelta import relativedelta

from misc import display_borders
from modules import Habit

def get_records_from_habits(habits, index):
    """
    retrieves records from habits as a dict with the day as the key.
    """
    habitid = list(habits.keys())[index % len(habits)]
    raw_records = habits[habitid]['data']

    records = {datetime.date.today().strftime("%Y-%m-%d"): []}

    for record in raw_records:
        day_of_record = record[0][:10]
        try:
            records[day_of_record].append(record)
        except KeyError:
            records[day_of_record] = [record]

    return records

def duration_maps(window, selected, map_settings):
    """
    prints a duration map, with bars starting and ending based on time.
    """
    display_borders(window, selected)
    based_on = ["day", "habit"][map_settings['based_on'] % 2]
    index = map_settings['index']

    window.addstr(2, 5, "duration habits")
    window.addstr(4, 5, "based on: ")
    window.addstr(f"< {based_on} >", curses.color_pair(1 + (selected[0] == 2)))

    habits = Habit.load_habits()
    habits = {habit: habits[habit] for habit in habits if habits[habit]['type'] == "duration"}

    if habits:
        if based_on == "day":
            day = datetime.date.today() + timedelta(days=index)
            on = day.strftime("%Y-%m-%d")
            # all records that start or end on this day (fetch date from datetime)
            records = {habit: [
                record for record in habits[habit]['data'] if record[0][:10] == on
            ] for habit in habits}

            try:
                earliest_time = min(
                    min(
                        dt.strptime(record[0], "%Y-%m-%d-%H:%M") for record in records[habit]
                    ) for habit in records if records[habit]
                )
                latest_time = max(
                    max(
                        dt.strptime(record[1], "%Y-%m-%d-%H:%M") for record in records[habit]
                    ) for habit in records if records[habit]
                )
            except:
                earliest_time = dt.combine(day, time(hour=0, minute=0, second=0))
                latest_time = dt.combine(day, time(hour=12, minute=0, second=0))
                try:
                    # ensure earliest_time aligns to the nearest hour
                    # (if necessary adjustments are needed)
                    earliest_time = earliest_time.replace(minute=0, second=0)
                except:
                    # fallback in case of errors
                    earliest_time = dt.combine(day, time(hour=0, minute=0, second=0))
            latest_time_diff = math.ceil((latest_time - earliest_time) / timedelta(hours=1))
        else:
            habitid = list(habits.keys())[index % len(habits)]
            raw_records = habits[habitid]['data']
            on = habits[habitid]['name']

            # find periods and analyze the least recorded times
            # create a count for each hour in a 24-hour format
            hour_counts = [0] * 24
            for record in raw_records:
                start_dt = dt.strptime(record[0], "%Y-%m-%d-%H:%M")
                end_dt = dt.strptime(record[1], "%Y-%m-%d-%H:%M")
                for hour in range(start_dt.hour, end_dt.hour + 1):
                    hour_counts[hour % 24] += 1

            # find the hour with the least records
            earliest_record = min(
                raw_records, key=lambda r: dt.strptime(r[0], "%Y-%m-%d-%H:%M").hour
            )
            earliest_time = dt.strptime(earliest_record[0], "%Y-%m-%d-%H:%M")
            latest_time_diff = 24

            records = get_records_from_habits(habits, index)

        window.addstr(6, 5, f"< {on} >", curses.color_pair(1 + (selected[0] == 3)))

        max_length = max(
            len(habits[habit]['name']) for habit in records
        ) if based_on == "day" else 10
        max_width = window.getmaxyx()[1] - 13 - max_length

        try:
            hour_width = max_width // (latest_time_diff)
        except:
            hour_width = 0
        else:
            hour_widths = [4, 6, 12]
            hour_widths = [
                width for width in hour_widths
                if width * (latest_time_diff) <= max_width
            ]
            gaps = [abs(hour_width - width) for width in hour_widths]
            try:
                hour_width = hour_widths[gaps.index(min(gaps))]
            except:
                hour_width = 4

        for x in range(latest_time_diff + 1):
            window.addstr(
                8, 7 + max_length + round(hour_width * x),
                str((earliest_time.hour) + x % 24).rjust(2, "0")
            )

        records = dict(sorted(records.items()))

        for i, record in enumerate(records):
            if i + 9 <= window.getmaxyx()[0] - 6:
                if based_on == "day":
                    window.addstr(
                        9 + i, 5,
                        habits[record]["name"].rjust(max_length),
                        curses.color_pair(1 + (selected[0] == i + 4))
                    )
                else:
                    window.addstr(
                        9 + i, 5,
                        record.rjust(max_length),
                        curses.color_pair(1 + (selected[0] == i + 4))
                    )
                count = 0
                for entry in records[record]:
                    count += 1
                    entry = [dt.strptime(e, "%Y-%m-%d-%H:%M").hour for e in entry]
                    width = hour_width * ((entry[1] - entry[0]) % 24)
                    message = " " * width
                    if len(message) > width:
                        message = message[:width-3] + "..."
                    duration_hours = (
                        entry[0] - earliest_time.hour
                    )
                    window.addstr(
                        9 + i, 8 + max_length + hour_width * (duration_hours % 24),
                        message, curses.color_pair(2)
                    )
    else:
        window.addstr(
            8, 5,
            "< no duration habits >",
            curses.color_pair(1 + (selected[0] == 3))
        )

def progress_maps(window, selected, map_settings):
    """
    prints a progress map, with progress bars.
    """
    display_borders(window, selected)
    based_on = ["day", "habit"][map_settings['based_on'] % 2]
    index = map_settings['index']

    window.addstr(2, 5, "progress habits")

    window.addstr(4, 5, "based on: ")
    window.addstr(f"< {based_on} >", curses.color_pair(1 + (selected[0] == 2)))

    habits = Habit.load_habits()

    # filter habits based on type
    # include both 'progress' and 'frequency' types for habit-based view
    if based_on == "habit":
        habits = {
            habit: habits[habit] for habit in habits
            if habits[habit]['type'] in ["progress", "frequency"]
        }
    else:
        habits = {
            habit: habits[habit] for habit in habits
            if habits[habit]['type'] == "progress"
        }
    habits = dict(sorted(habits.items(), key=lambda x: x[1]['name']))

    if habits:
        if based_on == "day":
            day = datetime.date.today() + timedelta(days=index)
            on = day.strftime("%Y-%m-%d")
            try:
                records = {habit: habits[habit]['data'][on] for habit in habits}
            except:
                for habit in habits:
                    if on not in habits[habit]['data']:
                        habits[habit]['data'][on] = 0
                records = {habit: habits[habit]['data'][on] for habit in habits}
        else:
            habitid = list(habits.keys())[index % len(habits)]
            records = habits[habitid]['data']
            on = habits[habitid]['name']

        window.addstr(6, 5, f"< {on} >", curses.color_pair(1 + (selected[0] == 3)))

        max_length = max(
            len(habits[habit]['name']) for habit in records
        ) if based_on == "day" else 10
        max_width = window.getmaxyx()[1] - 23 - max_length

        interval = max_width // 10

        records = dict(sorted(records.items()))

        for i, (key, value) in enumerate(records.items()):
            if i + 9 <= window.getmaxyx()[0] - 6:
                if based_on == "day":
                    habitid = key
                    key = habits[key]['name']
                    target = habits[habitid]['target_value']
                else:
                    habitid = list(habits.keys())[index % len(habits)]
                    if habits[habitid]['type'] == "progress":
                        target = habits[habitid]['target_value']
                    else:  # for frequency tasks, use the maximum value in the displayed data
                        target = max(*records.values(), 1)

                for x in range(interval + 1):
                    if based_on == "day" or habits[habitid]['type'] == "progress":
                        window.addstr(
                            8, 7 + max_length + round(max_width * (x / interval)),
                            str(round(x / interval * 100)).rjust(2)
                        )
                    else:
                        window.addstr(
                            8, 7 + max_length + round(max_width * (x / interval)),
                            f'{float(f"{x / interval * target:.2g}"):g}'.rjust(2)
                        )

                window.addstr(
                    9 + i, 5,
                    key.rjust(max_length), curses.color_pair(1 + (selected[0] == i + 4))
                )
                window.addstr(
                    9 + i, 8 + max_length,
                    " " * min(round(max_width * value / target), max_width), curses.color_pair(2)
                )
                if habits[habitid]['type'] == "progress":
                    window.addstr(
                        9 + i, window.getmaxyx()[1] - 15,
                        f"{round(value / target * 100, 2):.2f}%".rjust(10)
                    )
                else:
                    max_length_values = max(len(str(value)) for value in records.values())
                    window.addstr(
                        9 + i, window.getmaxyx()[1] - 6 - max_length_values,
                        str(value).rjust(max_length_values)
                    )
    else:
        window.addstr(8, 5, "no progress habits!")

def get_sunday(this_date):
    """
    returns the sunday of the week.
    """
    this_date = dt.strptime(this_date, "%Y-%m-%d")
    return (this_date - timedelta(days=this_date.weekday() + 1)).strftime("%Y-%m-%d")

def get_bounds(based_on, index, index2):
    """
    gets the start and end of the heatmap dates.
    """
    if based_on in ["day", "week"]:
        start_day = (datetime.date.today() + timedelta(days=index)).strftime("%Y-%m-%d")
        end_day = (datetime.date.today() + timedelta(days=index2)).strftime("%Y-%m-%d")
    elif based_on == "month":
        start_day = (
            datetime.date.today().replace(day=1) + relativedelta(months=index)
        ).strftime("%Y-%m-%d")
        end_day = (
            datetime.date.today().replace(day=1) + relativedelta(
                months=index2 + 1, days=-1
            )
        ).strftime("%Y-%m-%d")
    elif based_on == "year":
        start_day = datetime.date.today().replace(
            year=datetime.date.today().year + index, month=1, day=1
        ).strftime("%Y-%m-%d")
        end_day = datetime.date.today().replace(
            year=datetime.date.today().year + index2, month=12, day=31
        ).strftime("%Y-%m-%d")
    return start_day, end_day

def get_dates(start_day, end_day, based_on):
    """
    gets dates based on start and end day.
    """
    if based_on == "day":
        length = math.ceil((end_day - start_day) / timedelta(days=1)) + 1
        length = max(1, length)
        dates = [start_day + timedelta(days=i) for i in range(length)]
    elif based_on == "week":
        length = math.ceil((end_day - start_day) / timedelta(days=1) / 7)
        length = max(1, length)
        dates = [start_day + timedelta(days=7 * i) for i in range(length)]
    elif based_on == "month":
        length = math.ceil((end_day - start_day) / timedelta(days=1) / 30)
        length = max(1, length)
        dates = [start_day + relativedelta(months=i) for i in range(length)]
    elif based_on == "year":
        length = math.ceil((end_day - start_day) / timedelta(days=1) / 365)
        length = max(1, length)
        dates = [start_day.replace(year=start_day.year + i) for i in range(length)]
    return dates

def heatmaps(window, selected, map_settings):
    """
    prints heatmap.
    """
    display_borders(window, selected)
    based_list = ["day", "week", "month", "year", "calendar"]
    based_on = based_list[map_settings['based_on'] % len(based_list)]
    index = map_settings['index']
    index2 = map_settings['index2']

    window.addstr(2, 5, "heatmaps")

    window.addstr(4, 5, "based on: ")
    window.addstr(f"< {based_on} >", curses.color_pair(1 + (selected[0] == 2)))

    habits = Habit.load_habits()
    habits = dict(sorted(habits.items(), key=lambda x: x[1]['name']))

    if habits:
        # print the bounds
        if based_on != "calendar":
            start_day, end_day = get_bounds(based_on, index, index2)

            window.addstr(6, 5, "start: ")
            window.addstr(f"< {start_day} >", curses.color_pair(1 + (selected[0] == 3)))
            window.addstr(8, 5, "end: ")
            window.addstr(f"< {end_day} >", curses.color_pair(1 + (selected[0] == 4)))
        else:
            year = datetime.date.today().year + index
            start_day = f"{year}-01-01"
            end_day = f"{year}-12-31"

            habit = list(habits.keys())[index2 % len(habits)]

            window.addstr(6, 5, "year: ")
            window.addstr(f"< {year} >", curses.color_pair(1 + (selected[0] == 3)))

            window.addstr(8, 5, "habit: ")
            window.addstr(f"< {habits[habit]['name']} >", curses.color_pair(1 + (selected[0] == 4)))

        # reformat the information based on the bounds
        heat = {}
        for habit in habits:
            heat[habit] = {}
            if habits[habit]['type'] == "duration":
                for record in habits[habit]['data']:
                    record = [dt.strptime(r, "%Y-%m-%d-%H:%M") for r in record]
                    duration = (record[1] - record[0]) / timedelta(hours=1)
                    target_value = habits[habit]['target_value']
                    try:
                        heat[habit][record[0].date()] += duration / target_value
                    except:
                        heat[habit][record[0].date()] = duration / target_value
            elif habits[habit]['type'] == "progress":
                for d in habits[habit]['data']:
                    heat[habit][
                        dt.strptime(d, "%Y-%m-%d").date()
                    ] = habits[habit]['data'][d] / habits[habit]['target_value']
            elif habits[habit]['type'] == "frequency":
                max_frequency = max(*habits[habit]['data'].values(), 1)
                for d in habits[habit]['data']:
                    heat[habit][
                        dt.strptime(d, "%Y-%m-%d").date()
                    ] = habits[habit]['data'][d] / max_frequency

        start_day = dt.strptime(start_day, "%Y-%m-%d").date()
        end_day = dt.strptime(end_day, "%Y-%m-%d").date()

        # condense the information into time blocks
        if based_on in ["day", "calendar"]:
            condensed = {
                habit: {
                    day: heat[habit][day] for day in heat[habit] if start_day <= day <= end_day
                } for habit in heat
            }
        elif based_on in ["week", "month", "year"]:
            condensed = {}
            for habit in heat:
                condensed[habit] = {}
                for og_date in heat[habit]:
                    if og_date < start_day or og_date > end_day:
                        continue
                    if based_on == "week":
                        rounded_date = get_sunday(dt.strftime(og_date, "%Y-%m-%d"))
                    elif based_on == "month":
                        rounded_date = dt.strftime(og_date, "%Y-%m-%d")[:7] + "-01"
                    else:
                        rounded_date = dt.strftime(og_date, "%Y-%m-%d")[:4] + "-01-01"
                    try:
                        condensed[habit][rounded_date] += heat[habit][og_date]
                    except:
                        condensed[habit][rounded_date] = heat[habit][og_date]
                if based_on == "day":
                    length_of_period = 1
                elif based_on == "week":
                    length_of_period = 7
                elif based_on == "month":
                    length_of_period = calendar.monthrange(
                        int(rounded_date[:4]), int(rounded_date[5:7])
                    )[1]
                else:
                    length_of_period = 365
                for rounded_date in condensed[habit]:
                    condensed[habit][rounded_date] /= length_of_period
        condensed = dict(sorted(condensed.items(), key=lambda x: x[0]))

        # print the heatmaps
        if based_on != "calendar":
            # print side
            max_length = max(len(habits[habit]['name']) for habit in condensed)
            date_headers = ["yy", "mm", "dd"]
            if based_on == "year":
                date_headers = ["yy"]
            elif based_on == "month":
                date_headers = ["yy", "mm"]
            side_headers = date_headers + [habits[habit]['name'] for habit in condensed.keys()]
            for i, habit in enumerate(side_headers):
                window.addstr(
                    10 + i, 5,
                    habit.rjust(max_length),
                    curses.color_pair(1 + (selected[0] == i + 2 if i >= 3 else 0))
                )

            # define shades:
            shades = [" ", "░", "▒", "▓", "█"]

            # print squares
            dates = get_dates(start_day, end_day, based_on)
            dates = [this_date.strftime("%Y-%m-%d") for this_date in dates]

            selected_col = selected[1] % (len(dates))
            for n, day in enumerate(dates):
                day_list = day[2:].split("-")[:len(date_headers)]
                for d, date_header in enumerate(day_list):
                    # only print if different from last round
                    if date_header != dates[n-1][2:].split("-")[:len(date_headers)][d] or n == 0:
                        window.addstr(
                            10 + d, 6 + max_length + n * 2,
                            date_header.rjust(2, "0"),
                            curses.color_pair(2 if selected_col == n and selected[0] >= 5 else 1)
                        )
                for i, habit in enumerate(condensed):
                    try:
                        value = condensed[habit][dt.strptime(day, "%Y-%m-%d").date()]
                    except:
                        value = 0
                    this_cell_selected = selected[0] == i + 5 and selected_col == n
                    window.addstr(
                        10 + len(date_headers) + i, 6 + max_length + n * 2,
                        shades[min(round(value * 4), 4)] * 2,
                        curses.color_pair(8 if this_cell_selected else 1)
                    )
        else:
            side_headers = ["mm", "dd", "sun", "mon", "tue", "wed", "thu", "fri", "sat"]
            for i, day in enumerate(side_headers):
                window.addstr(
                    10 + i, 5, day.rjust(3),
                    curses.color_pair(1 + (selected[0] == i + 3 if i >= 2 else 0))
                )

            habit = list(habits.keys())[index2 % len(habits)]
            shades = [" ", "░", "▒", "▓", "█"]

            year_length = datetime.date(year, 12, 31).timetuple().tm_yday
            year_length_in_weeks = (
                dt.strptime(
                    get_sunday(f"{year}-12-31"), "%Y-%m-%d"
                ) - dt.strptime(
                    get_sunday(f"{year}-01-01"), "%Y-%m-%d"
                )
            ) // timedelta(weeks=1) + 1
            selected_col = selected[1] % (year_length_in_weeks)

            window.addstr(
                10, 9,
                get_sunday(dt.strftime(start_day, "%Y-%m-%d"))[5:7],
                curses.color_pair(2 if selected_col == 0 and selected[0] >= 5 else 1)
            )
            window.addstr(
                11, 9,
                get_sunday(dt.strftime(start_day, "%Y-%m-%d"))[8:10],
                curses.color_pair(2 if selected_col == 0 and selected[0] >= 5 else 1)
            )

            for day in range(0, year_length):
                this_date = datetime.date(year, 1, 1) + timedelta(days=day)
                weekday = (this_date.weekday() + 1) % 7
                weeks = math.ceil((day - datetime.date(year, 1, 1).weekday() - 5) / 7)
                if weekday == 0:
                    if this_date.month != (this_date - timedelta(days=7)).month:
                        window.addstr(
                            10, 9 + weeks * 2,
                            str(this_date.month).rjust(2, "0"),
                            curses.color_pair(
                                2 if selected_col == weeks and selected[0] >= 5 else 1
                            )
                        )
                    window.addstr(
                        11, 9 + weeks * 2,
                        str(this_date.day).rjust(2, "0"),
                        curses.color_pair(2 if selected_col == weeks and selected[0] >= 5 else 1)
                    )
                try:
                    value = heat[habit][this_date]
                except:
                    value = 0
                this_cell_selected = selected[0] == weekday + 5 and selected_col == weeks
                window.addstr(
                    12 + weekday, 9 + weeks * 2,
                    shades[min(round(value * 4), 4)] * 2,
                    curses.color_pair(8 if this_cell_selected else 1)
                )
    else:
        window.addstr(8, 5, "no habits!")

def manage_habits(window, selected, removing):
    """
    prints a habit management menu.
    """
    display_borders(window, selected)
    habits = Habit.load_habits()
    habits = dict(sorted(habits.items(), key=lambda x: x[0]))

    headers = ["name", "type", "unit", "target value"]
    column_widths = []
    for key in headers:
        try:
            column_widths.append(max(len(str(habits[habit][key])) for habit in habits))
        except:
            column_widths.append(0)
    column_widths = [max(column_widths[i], len(headers[i])) + 3 for i in range(len(headers))]

    window.addstr(2, 5, "manage habits")

    for i, header in enumerate(headers):
        # draw the top row of the table
        window.addstr(
            4, 5 + sum(column_widths[:i]) + i,
            ('╔' if i == 0 else "╦") + '═' * column_widths[i]
        )
        # draw the header row
        window.addstr(
            5, 5 + sum(column_widths[:i]) + i,
            "║ " + header.ljust(column_widths[i])
        )
        # draw the separator row below the header
        window.addstr(
            6, 5 + sum(column_widths[:i]) + i,
            ('╠' if i == 0 else "╬") + '═' * column_widths[i]
        )
        # draw the bottom border of the table
        window.addstr(
            min(7 + len(habits), window.getmaxyx()[0] - 6),
            5 + sum(column_widths[:i]) + i,
            ('╚' if i == 0 else "╩") + '═' * column_widths[i]
        )

    # draw the right border of the table
    for row in range(3):
        window.addstr(
            4 + row, 5 + sum(column_widths) + len(column_widths),
            '║' if row % 2 else ('╗' if row == 0 else '╣')
        )
    window.addstr(
        min(7 + len(habits), window.getmaxyx()[0] - 6),
        5 + sum(column_widths) + len(column_widths),
        '╝'
    )

    for h, habit in enumerate(habits):
        if h + 7 <= window.getmaxyx()[0] - 7:
            for i, header in enumerate(headers):
                item = str(habits[habit][header])
                if i == 3 and habits[habit]["type"] == "frequency":
                    item = ""
                # draw cell contents
                window.addstr(
                    7 + h, 5 + sum(column_widths[:i]) + i,
                    "║" + " " * column_widths[i]
                )
                if removing == habit:
                    window.addstr(
                        7 + h, 7 + sum(column_widths[:i]) + i,
                        item.ljust(column_widths[i] - 2), curses.color_pair(7)
                    )
                else:
                    window.addstr(
                        7 + h, 7 + sum(column_widths[:i]) + i,
                        item.ljust(column_widths[i] - 2),
                        curses.color_pair(1 + (selected[0] == h + 2 and selected[1] % 4 == i))
                    )
            # draw the right cell border
            window.addstr(7 + h, 5 + sum(column_widths) + len(column_widths), "║")

def add_new_habit(window, selected, new_habit):
    """
    prints the add new habit menu.
    """
    display_borders(window, selected)

    window.addstr(2, 5, "new habit")

    # input for habit name
    window.addstr(4, 5, "name: ")
    # display current input for habit name
    window.addstr(new_habit['name'], curses.color_pair(1 + (selected[0] == 2)))

    window.addstr(6, 5, "type: ")
    # display current input for habit type
    window.addstr(f"< {new_habit['type']} >", curses.color_pair(1 + (selected[0] == 3)))

    # input for measurement unit
    window.addstr(8, 5, "unit (e.g. hours): ")
    # display current input for unit
    window.addstr(
        new_habit['unit'] if new_habit['unit'] else "(none)",
        curses.color_pair(1 + (selected[0] == 4))
    )

    # input for target value
    window.addstr(10, 5, "target value: ")
    # display current input for target value
    window.addstr(
        str(new_habit['target_value']) if new_habit['type'] != "frequency" else "(none)",
        curses.color_pair(1 + (selected[0] == 5))
    )

    # additional information if needed
    window.addstr(12, 5, "submit", curses.color_pair(1 + (selected[0] == 6)))

    # refresh window to display updates
    window.refresh()
