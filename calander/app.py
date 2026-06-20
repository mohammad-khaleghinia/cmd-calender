"""Console calendar application.

Implements day view, navigation, search, editing, deletion, upcoming lists,
and immediate persistence after every modification.
"""

from datetime import datetime

from calendar_core import (
    PERSIAN_MONTH_NAMES,
    WEEKDAY_NAMES,
    format_gregorian,
    format_jalali,
    iso_to_jalali,
    jalali_month_length,
    jalali_to_gregorian,
    jalali_to_islamic,
    jalali_to_iso,
    jalali_weekday,
    system_today_jalali,
    valid_jalali_date,
)
from models import (
    EVENT_TYPE_EXACT,
    EVENT_TYPE_MONTHLY,
    EVENT_TYPE_WEEKLY,
    EVENT_TYPE_YEARLY,
    Event,
    Task,
)
from storage import Storage


ISLAMIC_MONTH_NAMES = [
    "moharam", "safar", "rabi alaval", "rabi alsani", "jamadi alaval", "jamadi alsani",
    "rajab", "shaaban", "ramezan", "shavval", "zighaadeh", "zihajeh"
]


class CalendarApp:
    def __init__(self):
        self.storage = Storage()
        data = self.storage.load()
        self.next_event_id = data["next_event_id"]
        self.next_task_id = data["next_task_id"]
        self.events = data["events"]
        self.tasks = data["tasks"]
        self.current_date = self._safe_today()

    def _safe_today(self):
        y, m, d = system_today_jalali()
        if valid_jalali_date(y, m, d):
            return [y, m, d]
        return [1111, 1, 1]

    def save(self):
        self.storage.save(self.next_event_id, self.next_task_id, self.events, self.tasks)

    def run(self):
        while True:
            self.show_day_page()
            cmd = input("\nWrite a command and press 'Enter': ").strip()
            if cmd == "1":
                self.goto_next_day()
            elif cmd == "2":
                self.goto_prev_day()
            elif cmd == "3":
                self.create_event_for_current_day()
            elif cmd == "4":
                self.create_event_for_specific_date()
            elif cmd == "5":
                self.create_task_for_current_day()
            elif cmd == "6":
                self.create_birthday()
            elif cmd == "7":
                self.show_upcoming_birthdays()
            elif cmd == "8":
                self.mark_task_done_from_current_day()
            elif cmd == "9":
                self.edit_event_from_current_day()
            elif cmd == "10":
                self.edit_task_from_current_day()
            elif cmd == "11":
                self.delete_event_from_current_day()
            elif cmd == "12":
                self.delete_task_from_current_day()
            elif cmd == "13":
                if not self.other_options_page():
                    break
            elif cmd == "0":
                print("exit the calander")
                break
            else:
                print("unknown command ")

    def current_tuple(self):
        return tuple(self.current_date)

    def current_iso(self):
        return jalali_to_iso(*self.current_tuple())

    def day_events(self, year, month, day):
        weekday = jalali_weekday(year, month, day)
        matched = []
        for event in self.events:
            if event.event_type == EVENT_TYPE_EXACT and event.exact_date == jalali_to_iso(year, month, day):
                matched.append(event)
            elif event.event_type == EVENT_TYPE_WEEKLY and event.weekday == weekday:
                matched.append(event)
            elif event.event_type == EVENT_TYPE_MONTHLY and event.day_of_month == day:
                matched.append(event)
            elif event.event_type == EVENT_TYPE_YEARLY and event.month_of_year == month and event.day_of_year == day:
                matched.append(event)
        return matched

    def day_tasks(self, year, month, day):
        target = jalali_to_iso(year, month, day)
        return [task for task in self.tasks if task.due_date == target]

    def show_day_page(self):
        year, month, day = self.current_tuple()
        weekday = jalali_weekday(year, month, day)
        now = datetime.now().strftime("%H:%M")
        gy, gm, gd = jalali_to_gregorian(year, month, day)
        iy, im, iday = jalali_to_islamic(year, month, day)
        events = self.day_events(year, month, day)
        tasks = self.day_tasks(year, month, day)
        
        print("\n" + "=" * 70)
        print("Day View")
        print("=" * 70)
        print(f"Jalali Date: {format_jalali(year, month, day)}")
        print(f"Gregorian Date: {format_gregorian(gy, gm, gd)}")
        print(f"Islamic Date: {iday} {ISLAMIC_MONTH_NAMES[im - 1]} {iy}")
        print(f"Weekday: {WEEKDAY_NAMES[weekday]}")
        print(f"Time that program : {now}")

        print("\nEvents:")
        if events:
            for i, event in enumerate(events, 1):
                print(f"  {i}. [{event.id}] {event.title} | {self.describe_event_time(event)}")
                if event.description:
                    print(f"     Description: {event.description}")
        else:
            print("  No items found.")

        print("\nTasks:")
        if tasks:
            for i, task in enumerate(tasks, 1):
                state = "Done" if task.done else "Not Done"
                print(f"  {i}. [{task.id}] {task.title} - {state}")
                if task.description:
                    print(f"     Description: {event.description}")
        else:
            print("  No items found.")

        print("\nHelp:")
        print("  1) Next day")
        print("  2) Previous day")
        print("  3) Create new event for today")
        print("  4) Create new event for specific date")
        print("  5) Create new task")
        print("  6) Add birthday")
        print("  7) Show upcoming birthdays")
        print("  8) Mark task as done")
        print("  9) Edit event")
        print("  10) Edit task")
        print("  11) Delete event")
        print("  12) Delete task")
        print("  13) More options")
        print("  0) Exit")

    def goto_next_day(self):
        y, m, d = self.current_tuple()
        d += 1
        if d > jalali_month_length(y, m):
            d = 1
            m += 1
            if m > 12:
                m = 1
                y += 1
        if valid_jalali_date(y, m, d):
            self.current_date = [y, m, d]
        else:
            print("You cannot go beyond the allowed date range.")

    def goto_prev_day(self):
        y, m, d = self.current_tuple()
        d -= 1
        if d < 1:
            m -= 1
            if m < 1:
                m = 12
                y -= 1
            d = jalali_month_length(y, m)
        if valid_jalali_date(y, m, d):
            self.current_date = [y, m, d]
        else:
            print("You cannot go below the allowed date range.")

    def prompt_nonempty(self, title):
        while True:
            value = input(title).strip()
            if value:
                return value
            print("This field must not be empty.")

    def prompt_optional(self, title):
        return input(title).strip()

    def create_event_for_current_day(self):
        title = self.prompt_nonempty("Event title: ")
        description = self.prompt_optional("Event description: ")
        print("Event type: 1) Specific date  2) Weekly  3) Monthly  4) Yearly")
        kind = input("Choice: ").strip()
        y, m, d = self.current_tuple()
        weekday = jalali_weekday(y, m, d)

        if kind == "1":
            event = Event(self.next_event_id, title, description, EVENT_TYPE_EXACT, exact_date=jalali_to_iso(y, m, d))
        elif kind == "2":
            event = Event(self.next_event_id, title, description, EVENT_TYPE_WEEKLY, weekday=weekday)
        elif kind == "3":
            event = Event(self.next_event_id, title, description, EVENT_TYPE_MONTHLY, day_of_month=d)
        elif kind == "4":
            event = Event(self.next_event_id, title, description, EVENT_TYPE_YEARLY, month_of_year=m, day_of_year=d)
        else:
            print("Invalid type.")
            return

        self.events.append(event)
        self.next_event_id += 1
        self.save()
        print("Event saved.")

    def create_task_for_current_day(self):
        title = self.prompt_nonempty("Task title: ")
        description = self.prompt_optional("Task description: ")
        use_current = input("Use current date? (y/n): ").strip().lower()
        if use_current == "y":
            due = self.current_iso()
        else:
            due = self.prompt_jalali_date()
        task = Task(self.next_task_id, title, description, due, False)
        self.tasks.append(task)
        self.next_task_id += 1
        self.save()
        print("Task saved.")

    def prompt_jalali_date(self):
        while True:
            raw = input("Enter Jalali date as YYYY-MM-DD: ").strip()
            try:
                y, m, d = iso_to_jalali(raw)
                if valid_jalali_date(y, m, d):
                    return raw
            except Exception:
                pass
            print("The date is invalid or outside the supported range.")

    def select_from_list(self, items, label):
        if not items:
            print("There is no item to select.")
            return None
        for i, item in enumerate(items, 1):
            if hasattr(item, "event_type"):
                print(f"  {i}. [{item.id}] {item.title} | {self.describe_event_time(item)}")
            else:
                state = "Done" if item.done else "Not Done"
                print(f"  {i}. [{item.id}] {item.title} | {item.due_date} | {state}")
        choice = input(f"Enter the number of {label}: ").strip()
        if not choice.isdigit():
            print("Invalid choice.")
            return None
        idx = int(choice) - 1
        if idx < 0 or idx >= len(items):
            print("Choice is out of range.")
            return None
        return items[idx]

    def mark_task_done_from_current_day(self):
        tasks = [t for t in self.day_tasks(*self.current_tuple()) if not t.done]
        item = self.select_from_list(tasks, "task")
        if item is None:
            return
        item.done = True
        self.save()
        print("Task marked as done.")

    def edit_event_from_current_day(self):
        event = self.select_from_list(self.day_events(*self.current_tuple()), "event")
        if event is None:
            return
        self.edit_event(event)

    def edit_task_from_current_day(self):
        task = self.select_from_list(self.day_tasks(*self.current_tuple()), "Task")
        if task is None:
            return
        self.edit_task(task)

    def delete_event_from_current_day(self):
        event = self.select_from_list(self.day_events(*self.current_tuple()), "event")
        if event is None:
            return
        self.events = [e for e in self.events if e.id != event.id]
        self.save()
        print("Event deleted.")

    def delete_task_from_current_day(self):
        task = self.select_from_list(self.day_tasks(*self.current_tuple()), "Task")
        if task is None:
            return
        self.tasks = [t for t in self.tasks if t.id != task.id]
        self.save()
        print("Task deleted.")

    def describe_event_time(self, event):
        if event.event_type == EVENT_TYPE_EXACT:
            return f"Specific date: {event.exact_date}"
        if event.event_type == EVENT_TYPE_WEEKLY:
            return f"Weekly: {WEEKDAY_NAMES[event.weekday]}"
        if event.event_type == EVENT_TYPE_MONTHLY:
            return f"Monthly: day {event.day_of_month}"
        return f"Yearly: {event.day_of_year} / {event.month_of_year}"

    def create_birthday(self):
        name = self.prompt_nonempty("Person name: ")
        description = self.prompt_optional("Description (optional): ")
        while True:
            raw = input("Birthday date (MM-DD in Jalali): ").strip()
            try:
                m, d = map(int, raw.split("-"))
            except:
                print("Invalid format. Use MM-DD")
                continue

            if not valid_jalali_date(1400, m, d):
                print("Invalid Jalali date.")
                continue

            break

        event = Event(
            id=self.next_event_id,
            title=f"{name}'s birthday",
            description=description,
            event_type=EVENT_TYPE_YEARLY,
            month_of_year=m,
            day_of_year=d,
        )
        self.events.append(event)
        self.next_event_id += 1
        self.save()
        print("Birthday added successfully.")

    def _next_yearly_occurrence(self, y, m, d, em, ed):
        if (m, d) <= (em, ed):
            return (y, em, ed)
        else:
            return (y + 1, em, ed)
        
    def _is_birthday_event(self, event):
        if event.event_type != EVENT_TYPE_YEARLY:
            return False
        return "birthday" in event.title.lower()

    def show_upcoming_birthdays(self):
        y, m, d = self.current_tuple()
        upcoming = []
        for event in self.events:
            if not self._is_birthday_event(event):
                continue

            ny, nm, nd = self._next_yearly_occurrence(
                y, m, d, event.month_of_year, event.day_of_year
            )
            upcoming.append(((ny, nm, nd), event))

        upcoming.sort(key=lambda x: x[0])
        print("\nUpcoming Birthdays:")
        if not upcoming:
            print("None.")
            return
        for i, ((yy, mm, dd), event) in enumerate(upcoming, 1):
            date_str = format_jalali(yy, mm, dd)
            print(f"{i}. {event.title} - {date_str}")
            if event.description:
                print(f"   {event.description}")

    def _days_until(self, y, m, d, ty, tm, td):
        from datetime import date
        today = date(y, m, d)
        target = date(ty, tm, td)
        print((target - today).days)
        return (target - today).days

    def show_nearby_birthdays(self, limit=7):
        y, m, d = self.current_tuple()
        upcoming = []
        for event in self.events:
            if not self._is_birthday_event(event):
                continue

            ny, nm, nd = self._next_yearly_occurrence(
                y, m, d,
                event.month_of_year,
                event.day_of_year
            )
            days = self._days_until(y, m, d, ny, nm, nd)
            if days <= limit:
                upcoming.append((days, event))

        upcoming.sort(key=lambda x: x[0])
        if not upcoming:
            return

        print("\nUpcoming birthdays:")
        for days, event in upcoming:
            if days == 0:
                print(f"- {event.title} (Today)")
            else:
                print(f"- {event.title} in {days} days")

    def create_event_for_specific_date(self):
        title = self.prompt_nonempty("Event title: ")
        description = self.prompt_optional("Description (optional): ")
        print("Event type: 1) Specific date  2) Weekly  3) Monthly  4) Yearly")
        kind = input("Choice: ").strip()
        raw = input("Date (YYYY-MM-DD Jalali): ").strip()
        try:
            y, m, d = map(int, raw.split("-"))
        except:
            print("Invalid format. Use YYYY-MM-DD")
        
        if not valid_jalali_date(y, m, d):
            print("Invalid Jalali date.")
            
        weekday = jalali_weekday(y, m, d)

        if kind == "1":
            event = Event(self.next_event_id, title, description, EVENT_TYPE_EXACT, exact_date=jalali_to_iso(y, m, d))
        elif kind == "2":
            event = Event(self.next_event_id, title, description, EVENT_TYPE_WEEKLY, weekday=weekday)
        elif kind == "3":
            event = Event(self.next_event_id, title, description, EVENT_TYPE_MONTHLY, day_of_month=d)
        elif kind == "4":
            event = Event(self.next_event_id, title, description, EVENT_TYPE_YEARLY, month_of_year=m, day_of_year=d)
        else:
            print("Invalid type.")
            return

        self.events.append(event)
        self.next_event_id += 1
        self.save()
        print("Event added successfully.")

    def other_options_page(self):
        while True:
            print("\n" + "-" * 50)
            print("More Options")
            print("-" * 50)
            print("  1) Go to a specific date")
            print("  2) Show upcoming tasks")
            print("  3) Show upcoming events")
            print("  4) Show overdue and unfinished tasks")
            print("  5) Search events by title/description")
            print("  6) Search tasks by title/description")
            print("  7) Return to day view")
            print("  0) Exit program")
            cmd = input("Choice: ").strip()
            if cmd == "1":
                self.goto_custom_date()
            elif cmd == "2":
                self.show_upcoming_tasks()
            elif cmd == "3":
                self.show_upcoming_events()
            elif cmd == "4":
                self.show_overdue_tasks()
            elif cmd == "5":
                self.search_events()
            elif cmd == "6":
                self.search_tasks()
            elif cmd == "7":
                return True
            elif cmd == "0":
                return False
            else:
                print("Invalid option.")

    def goto_custom_date(self):
        raw = self.prompt_jalali_date()
        self.current_date = list(iso_to_jalali(raw))

    def show_upcoming_tasks(self):
        today = self.current_iso()
        items = [t for t in self.tasks if t.due_date >= today]
        items.sort(key=lambda x: x.due_date)
        self.print_task_list(items, "Upcoming Tasks")

    def show_overdue_tasks(self):
        today = self.current_iso()
        items = [t for t in self.tasks if t.due_date < today and not t.done]
        items.sort(key=lambda x: x.due_date)
        self.print_task_list(items, "Overdue and Unfinished Tasks")

    def all_upcoming_event_occurrences(self):
        today = self.current_iso()
        result = []
        for event in self.events:
            occ = self.next_occurrence_for_event(event, today)
            if occ is not None:
                result.append((occ, event))
        result.sort(key=lambda x: x[0])
        return result

    def next_occurrence_for_event(self, event, today_iso):
        ty, tm, td = iso_to_jalali(today_iso)
        if event.event_type == EVENT_TYPE_EXACT:
            return event.exact_date if event.exact_date >= today_iso else None
        if event.event_type == EVENT_TYPE_MONTHLY:
            y, m = ty, tm
            for _ in range(24):
                if event.day_of_month <= jalali_month_length(y, m):
                    cand = jalali_to_iso(y, m, event.day_of_month)
                    if cand >= today_iso:
                        return cand
                m += 1
                if m > 12:
                    m = 1
                    y += 1
            return None
        if event.event_type == EVENT_TYPE_YEARLY:
            for y in range(ty, ty + 5):
                if event.day_of_year <= jalali_month_length(y, event.month_of_year):
                    cand = jalali_to_iso(y, event.month_of_year, event.day_of_year)
                    if cand >= today_iso:
                        return cand
            return None
        if event.event_type == EVENT_TYPE_WEEKLY:
            y, m, d = ty, tm, td
            for _ in range(14):
                if jalali_weekday(y, m, d) == event.weekday:
                    return jalali_to_iso(y, m, d)
                d += 1
                if d > jalali_month_length(y, m):
                    d = 1
                    m += 1
                    if m > 12:
                        m = 1
                        y += 1
            return None
        return None

    def show_upcoming_events(self):
        items = self.all_upcoming_event_occurrences()
        print("\nUpcoming Events:")
        if not items:
            print("  No items found.")
            return
        for i, (occ, event) in enumerate(items, 1):
            print(f"  {i}. [{event.id}] {event.title} | Next occurrence: {occ} | {self.describe_event_time(event)}")

    def print_task_list(self, items, title):
        print(f"\n{title}:")
        if not items:
            print("  No items found.")
            return
        for i, task in enumerate(items, 1):
            state = "Done" if task.done else "Not done"
            print(f"  {i}. [{task.id}] {task.title} | {task.due_date} | {state}")
            if task.description:
                print(f"     Description: {task.description}")

    def search_events(self):
        phrase = input("Search phrase: ").strip().lower()
        items = [e for e in self.events if phrase in e.title.lower() or phrase in e.description.lower()]
        items.sort(key=lambda x: x.title.lower())
        print("\nEvent Search Results:")
        if not items:
            print("  No results found.")
            return
        for i, event in enumerate(items, 1):
            print(f"  {i}. [{event.id}] {event.title} | {self.describe_event_time(event)}")
            if event.description:
                print(f"     Description: {event.description}")
        action = input("Enter e to edit, d to delete, or press Enter to return: ").strip().lower()
        if action == "e":
            event = self.select_from_list(items, "event")
            if event:
                self.edit_event(event)
        elif action == "d":
            event = self.select_from_list(items, "event")
            if event:
                self.events = [e for e in self.events if e.id != event.id]
                self.save()
                print("Event deleted.")

    def search_tasks(self):
        phrase = input("Search phrase: ").strip().lower()
        items = [t for t in self.tasks if phrase in t.title.lower() or phrase in t.description.lower()]
        items.sort(key=lambda x: x.title.lower())
        print("\nTask Search Results:")
        if not items:
            print("  No results found.")
            return
        for i, task in enumerate(items, 1):
            state = "Done" if task.done else "Not done"
            print(f"  {i}. [{task.id}] {task.title} | {task.due_date} | {state}")
            if task.description:
                print(f"     Description: {task.description}")
        action = input("Enter e to edit, d to delete, m to mark as done, or press Enter to return: ").strip().lower()
        if action == "e":
            task = self.select_from_list(items, "task")
            if task:
                self.edit_task(task)
        elif action == "d":
            task = self.select_from_list(items, "task")
            if task:
                self.tasks = [t for t in self.tasks if t.id != task.id]
                self.save()
                print("Task deleted.")
        elif action == "m":
            task = self.select_from_list(items, "Task")
            if task:
                task.done = True
                self.save()
                print("Task marked as done.")

    def edit_event(self, event):
        new_title = input(f"New title ({event.title}): ").strip()
        new_desc = input(f"New description ({event.description}): ").strip()
        print("New type: 1) Specific date  2) Weekly  3) Monthly  4) Yearly  Enter=No change")
        kind = input("Choice: ").strip()
        if new_title:
            event.title = new_title
        if new_desc:
            event.description = new_desc
        if kind:
            if kind == "1":
                event.event_type = EVENT_TYPE_EXACT
                event.exact_date = self.prompt_jalali_date()
                event.weekday = None
                event.day_of_month = None
                event.month_of_year = None
                event.day_of_year = None
            elif kind == "2":
                print("Weekday: 0 Monday, 1 Tuesday, 2 Wednesday, 3 Thursday, 4 Friday, 5 Saturday, 6 Sunday")
                wd = input("Weekday: ").strip()
                if not wd.isdigit() or int(wd) not in range(7):
                    print("Invalid weekday.")
                    return
                event.event_type = EVENT_TYPE_WEEKLY
                event.weekday = int(wd)
                event.exact_date = None
                event.day_of_month = None
                event.month_of_year = None
                event.day_of_year = None
            elif kind == "3":
                dom = input("Day of month: ").strip()
                if not dom.isdigit() or not (1 <= int(dom) <= 31):
                    print("Invalid day of month.")
                    return
                event.event_type = EVENT_TYPE_MONTHLY
                event.day_of_month = int(dom)
                event.exact_date = None
                event.weekday = None
                event.month_of_year = None
                event.day_of_year = None
            elif kind == "4":
                moy = input("Month of year: ").strip()
                doy = input("روز ماه: ").strip()
                if not moy.isdigit() or not doy.isdigit():
                    print("Invalid input.")
                    return
                moy = int(moy)
                doy = int(doy)
                if not (1 <= moy <= 12 and 1 <= doy <= 31):
                    print("Invalid yearly date.")
                    return
                event.event_type = EVENT_TYPE_YEARLY
                event.month_of_year = moy
                event.day_of_year = doy
                event.exact_date = None
                event.weekday = None
                event.day_of_month = None
            else:
                print("Invalid type.")
                return
        self.save()
        print("Event updated.")

    def edit_task(self, task):
        new_title = input(f"New title ({task.title}): ").strip()
        new_desc = input(f"New description ({task.description}): ").strip()
        new_date = input(f"New date ({task.due_date}) or press Enter: ").strip()
        new_state = input(f"New status done/undone ({'done' if task.done else 'undone'}) or press Enter: ").strip().lower()
        if new_title:
            task.title = new_title
        if new_desc:
            task.description = new_desc
        if new_date:
            try:
                y, m, d = iso_to_jalali(new_date)
                if not valid_jalali_date(y, m, d):
                    print("Invalid date.")
                    return
                task.due_date = new_date
            except Exception:
                print("Invalid date format.")
                return
        if new_state == "done":
            task.done = True
        elif new_state == "undone":
            task.done = False
        elif new_state:
            print("Invalid status.")
            return
        self.save()
        print("Task updated.")


if __name__ == "__main__":
    CalendarApp().run()
