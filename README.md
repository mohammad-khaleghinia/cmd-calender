# cmd-calender

# Persian Terminal Calendar

A simple and lightweight terminal-based calendar application written in Python.

This project provides a Persian/Jalali calendar with support for events, tasks, birthdays, Gregorian and Hijri date display, and local JSON-based data storage.

---

## Features

- Display Persian/Jalali calendar date
- Display Gregorian date
- Display Hijri/Islamic date
- Show current weekday and time
- Add and manage daily events
- Add events for specific Jalali dates
- Add and manage tasks
- Add birthdays as yearly recurring events
- Show upcoming birthdays
- Show nearby birthdays
- Search events
- Store data locally using JSON
- Fully English terminal interface

---

## Project Structure

```text
.
├── app.py
├── calendar_core.py
├── models.py
├── storage.py
├── calendar_data.json
└── README.md
```

### `app.py`

Main entry point of the program.  
It contains the terminal user interface, menus, and user interaction logic.

### `calendar_core.py`

Contains calendar-related calculations, including:

- Jalali date handling
- Gregorian date conversion
- Hijri date conversion
- Weekday calculation
- Jalali leap year detection

### `models.py`

Contains the main data models used in the application, such as:

- Events
- Tasks
- Event types

### `storage.py`

Handles loading and saving application data.

### `calendar_data.json`

Local JSON file used to store events, tasks, birthdays, and other calendar data.

---

## Requirements

- Python 3.9 or newer

This project does not require any external Python packages.

---

## Installation

Clone the repository:

```bash
git clone https://github.com/your-username/persian-terminal-calendar.git
```

Go to the project directory:

```bash
cd persian-terminal-calendar
```

Run the application:

```bash
python app.py
```

Or, depending on your system:

```bash
python3 app.py
```

---

## Usage

After running the program, the main menu will be displayed in the terminal.

Example menu:

```text
1) Show today
2) Show specific day
3) Add event
4) Add task
5) Search
6) Manage tasks
7) Other options
8) Add birthday
9) Show upcoming birthdays
10) Add event for specific date
0) Exit
```

You can choose an option by entering its number.

---

## Date Format

For entering Jalali dates, use the following format:

```text
YYYY-MM-DD
```

Example:

```text
1404-07-10
```

---

## Events

The application supports different types of events.

You can add:

- Daily events
- Events for a specific Jalali date
- Yearly recurring events such as birthdays

Example:

```text
Title: Meeting with team
Date: 1404-07-10
Description: Project discussion
```

---

## Birthdays

Birthdays are stored as yearly recurring events.

The application can:

- Add birthdays
- Show upcoming birthdays
- Show birthdays near the selected day
- Display birthday reminders

Example:

```text
Ali's birthday - 1404-08-15
```

---

## Tasks

You can add and manage tasks from the terminal.

Tasks can be used for simple personal reminders and daily planning.

---

## Data Storage

All application data is saved locally in:

```text
calendar_data.json
```

This file contains events, tasks, birthdays, and other saved information.

Because the data is stored locally, no internet connection or database is required.

---

## Example Output

```text
Saturday
Time: 14:35

Jalali: 1404-07-10
Gregorian: 2025-10-02
Hijri: 27 Ramadan 1447

Events:
- Team meeting

Tasks:
- Finish report

Upcoming Birthdays:
- Sara's birthday in 3 days
```

---

## Calendar Notes

The project works with three calendar systems:

- Jalali / Persian calendar
- Gregorian calendar
- Hijri / Islamic calendar

Hijri calendar dates may sometimes differ by one day depending on moon sighting methods and local calendar authorities.

---

## Future Improvements

Possible future features:

- Monthly calendar view
- Weekly calendar view
- Colorized terminal output
- Event editing and deletion
- Task deadlines
- Notification system
- Export to `.ics` calendar format
- Better Hijri calendar adjustment
- Backup and restore support

---

## Contributing

Contributions are welcome.

If you want to improve the project:

1. Fork the repository
2. Create a new branch
3. Make your changes
4. Submit a pull request

---

## License

This project is available for educational and personal use.

You can modify and use it freely.
```
