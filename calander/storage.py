"""Manual JSON-like storage without using the json library."""

from pathlib import Path
from models import Event, Task, VALID_EVENT_TYPES


class Storage:
    """Handles persistence for events and tasks."""

    def __init__(self, filename="calendar_data.json"):
        self.filename = Path(filename)
        if not self.filename.exists():
            self._write_text('{\n  "next_event_id": 1,\n  "next_task_id": 1,\n  "events": [],\n  "tasks": []\n}')

    def load(self):
        text = self._read_text()
        data = parse_json_like(text)
        events = [Event(**item) for item in data.get("events", [])]
        tasks = [Task(**item) for item in data.get("tasks", [])]
        next_event_id = int(data.get("next_event_id", 1))
        next_task_id = int(data.get("next_task_id", 1))
        return {
            "next_event_id": next_event_id,
            "next_task_id": next_task_id,
            "events": events,
            "tasks": tasks,
        }

    def save(self, next_event_id, next_task_id, events, tasks):
        data = {
            "next_event_id": next_event_id,
            "next_task_id": next_task_id,
            "events": [event_to_dict(e) for e in events],
            "tasks": [task_to_dict(t) for t in tasks],
        }
        self._write_text(dump_json_like(data))

    def _read_text(self):
        return self.filename.read_text(encoding="utf-8")

    def _write_text(self, text):
        self.filename.write_text(text, encoding="utf-8")


def event_to_dict(e):
    if e.event_type not in VALID_EVENT_TYPES:
        raise ValueError("Invalid event type")
    return {
        "id": e.id,
        "title": e.title,
        "description": e.description,
        "event_type": e.event_type,
        "exact_date": e.exact_date,
        "weekday": e.weekday,
        "day_of_month": e.day_of_month,
        "month_of_year": e.month_of_year,
        "day_of_year": e.day_of_year,
    }


def task_to_dict(t):
    return {
        "id": t.id,
        "title": t.title,
        "description": t.description,
        "due_date": t.due_date,
        "done": t.done,
    }


def dump_json_like(value, indent=0):
    sp = "  " * indent
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, str):
        return '"' + escape_string(value) + '"'
    if isinstance(value, list):
        if not value:
            return "[]"
        items = ["  " * (indent + 1) + dump_json_like(v, indent + 1) for v in value]
        return "[\n" + ",\n".join(items) + "\n" + sp + "]"
    if isinstance(value, dict):
        if not value:
            return "{}"
        items = []
        for k, v in value.items():
            items.append("  " * (indent + 1) + dump_json_like(str(k)) + ": " + dump_json_like(v, indent + 1))
        return "{\n" + ",\n".join(items) + "\n" + sp + "}"
    raise TypeError(f"Unsupported type: {type(value)}")


def escape_string(s):
    return s.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\t', '\\t')


class Parser:
    def __init__(self, text):
        self.text = text
        self.i = 0

    def parse(self):
        value = self.parse_value()
        self.skip_ws()
        if self.i != len(self.text):
            raise ValueError("Unexpected extra data")
        return value

    def skip_ws(self):
        while self.i < len(self.text) and self.text[self.i] in " \n\r\t":
            self.i += 1

    def parse_value(self):
        self.skip_ws()
        if self.i >= len(self.text):
            raise ValueError("Unexpected end")
        ch = self.text[self.i]
        if ch == '{':
            return self.parse_object()
        if ch == '[':
            return self.parse_array()
        if ch == '"':
            return self.parse_string()
        if ch in '-0123456789':
            return self.parse_number()
        if self.text.startswith("true", self.i):
            self.i += 4
            return True
        if self.text.startswith("false", self.i):
            self.i += 5
            return False
        if self.text.startswith("null", self.i):
            self.i += 4
            return None
        raise ValueError("Invalid value")

    def parse_object(self):
        obj = {}
        self.i += 1
        self.skip_ws()
        if self.text[self.i] == '}':
            self.i += 1
            return obj
        while True:
            self.skip_ws()
            key = self.parse_string()
            self.skip_ws()
            if self.text[self.i] != ':':
                raise ValueError("Expected colon")
            self.i += 1
            value = self.parse_value()
            obj[key] = value
            self.skip_ws()
            if self.text[self.i] == '}':
                self.i += 1
                return obj
            if self.text[self.i] != ',':
                raise ValueError("Expected comma")
            self.i += 1

    def parse_array(self):
        arr = []
        self.i += 1
        self.skip_ws()
        if self.text[self.i] == ']':
            self.i += 1
            return arr
        while True:
            arr.append(self.parse_value())
            self.skip_ws()
            if self.text[self.i] == ']':
                self.i += 1
                return arr
            if self.text[self.i] != ',':
                raise ValueError("Expected comma")
            self.i += 1

    def parse_string(self):
        if self.text[self.i] != '"':
            raise ValueError("Expected string")
        self.i += 1
        out = []
        while self.i < len(self.text):
            ch = self.text[self.i]
            if ch == '"':
                self.i += 1
                return ''.join(out)
            if ch == '\\':
                self.i += 1
                esc = self.text[self.i]
                mapping = {'"': '"', '\\': '\\', 'n': '\n', 't': '\t'}
                if esc not in mapping:
                    raise ValueError("Unsupported escape")
                out.append(mapping[esc])
                self.i += 1
            else:
                out.append(ch)
                self.i += 1
        raise ValueError("Unterminated string")

    def parse_number(self):
        start = self.i
        if self.text[self.i] == '-':
            self.i += 1
        while self.i < len(self.text) and self.text[self.i].isdigit():
            self.i += 1
        if self.i < len(self.text) and self.text[self.i] == '.':
            self.i += 1
            while self.i < len(self.text) and self.text[self.i].isdigit():
                self.i += 1
            return float(self.text[start:self.i])
        return int(self.text[start:self.i])


def parse_json_like(text):
    return Parser(text).parse()