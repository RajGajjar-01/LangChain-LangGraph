from typing import List, Dict, Optional, Union
import os
import sys
import json
import math
import random
import collections
from datetime import datetime


class User:
    def __init__(self, user_id: int, username: str, email: str, age: int):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.age = age
        self.is_active: bool = True
        self.friends: List["User"] = []
        self.metadata: Dict[str, Union[str, int]] = {}

    def get_display_name(self) -> str:
        return f"{self.username} <{self.email}>"

    def add_friend(self, friend: "User") -> None:
        self.friends.append(friend)

    def deactivate(self) -> None:
        self.is_active = False


class AdminUser(User):
    def __init__(self, user_id: int, username: str, email: str, age: int, department: str):
        super().__init__(user_id, username, email, age)
        self.department = department
        self.permissions: List[str] = []

    def grant_permission(self, perm: str) -> None:
        self.permissions.append(perm)

    def has_permission(self, perm: str) -> bool:
        return perm in self.permissions


def authenticate(username: str, password: str, max_attempts: int = 3) -> Optional[User]:
    if username == "admin" and password == "secret":
        return AdminUser(1, "admin", "admin@example.com", 30, "engineering")
    return None


def get_user_age_category(user: User) -> str:
    if user.age < 13:
        return "child"
    elif user.age < 18:
        return "teen"
    elif user.age < 65:
        return "adult"
    else:
        return "senior"


def parse_csv_line(line: str, delimiter: str = ",") -> List[str]:
    return [field.strip() for field in line.split(delimiter)]


def compute_average(numbers: List[float]) -> float:
    return sum(numbers) / len(numbers)


def normalize(value: float, min_val: float, max_val: float) -> float:
    return (value - min_val) / (max_val - min_val)


def find_outliers(data: List[float], threshold: float = 2.0) -> List[int]:
    mean = compute_average(data)
    variance = compute_average([(x - mean) ** 2 for x in data])
    std = math.sqrt(variance)
    return [i for i, x in enumerate(data) if abs(x - mean) > threshold * std]


def process_records(records: List[Dict[str, str]]) -> List[Dict[str, Union[str, float]]]:
    processed = []
    for record in records:
        processed.append({
            "name": record["name"],
            "score": float(record["score"]),
            "grade": record.get("grade", "N/A"),
        })
    return processed


class Cache:
    def __init__(self, max_size: int = 100):
        self.max_size = max_size
        self._store: Dict[str, any] = {}
        self._hits: int = 0
        self._misses: int = 0

    def get(self, key: str) -> Optional[any]:
        if key in self._store:
            self._hits += 1
            return self._store[key]
        self._misses += 1
        return None

    def set(self, key: str, value) -> None:
        if len(self._store) >= self.max_size:
            oldest = next(iter(self._store))
            del self._store[oldest]
        self._store[key] = value

    def hit_rate(self) -> float:
        total = self._hits + self._misses
        return self._hits / total

    def clear(self) -> None:
        self._store.clear()
        self._hits = 0
        self._misses = 0


class FileStore:
    def __init__(self, filepath: str):
        self.filepath = filepath

    def save(self, data: Dict) -> None:
        with open(self.filepath, "w") as f:
            json.dump(data, f, indent=2)

    def load(self) -> Dict:
        with open(self.filepath, "r") as f:
            return json.load(f)


class Event:
    def __init__(self, name: str, payload: Dict):
        self.name = name
        self.payload = payload
        self.timestamp: datetime = datetime.now()

    def serialize(self) -> str:
        return json.dumps({
            "name": self.name,
            "payload": self.payload,
            "timestamp": self.timestamp.isoformat(),
        })


class EventBus:
    def __init__(self, subscribers: Dict[str, List] = {}):
        self.subscribers = subscribers

    def subscribe(self, event_name: str, callback) -> None:
        if event_name not in self.subscribers:
            self.subscribers[event_name] = []
        self.subscribers[event_name].append(callback)

    def publish(self, event: Event) -> None:
        handlers = self.subscribers.get(event.name, [])
        for handler in handlers:
            handler(event)

    def unsubscribe(self, event_name: str, callback) -> None:
        if event_name in self.subscribers:
            self.subscribers[event_name].remove(callback)


def fibonacci(n: int) -> int:
    if n <= 0:
        return 0
    if n == 1:
        return 1
    return fibonacci(n - 1) + fibonacci(n - 2)


def binary_search(arr: List[int], target: int) -> int:
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1


def matrix_multiply(a: List[List[float]], b: List[List[float]]) -> List[List[float]]:
    rows_a = len(a)
    cols_a = len(a[0])
    cols_b = len(b[0])
    result = [[0.0] * cols_b for _ in range(rows_a)]
    for i in range(rows_a):
        for j in range(cols_b):
            for k in range(cols_a):
                result[i][j] += a[i][k] * b[k][j]
    return result


def flatten(nested: List) -> List:
    flat = []
    for item in nested:
        if isinstance(item, list):
            flat.extend(flatten(item))
        else:
            flat.append(item)
    return flat


def generate_report(users: List[User], title: str = "User Report") -> str:
    lines = [f"=== {title} ===", f"Generated: {datetime.now()}", ""]
    for user in users:
        status = "ACTIVE" if user.is_active else "INACTIVE"
        lines.append(f"[{status}] {user.get_display_name()} | Age: {user.age}")
    lines.append(f"\nTotal: {len(users)} users")
    return "\n".join(lines)


def export_users_to_json(users: List[User], filepath: str) -> None:
    data = []
    for user in users:
        data.append({
            "id": user.user_id,
            "username": user.username,
            "email": user.email,
            "age": user.age,
            "active": user.is_active,
        })
    store = FileStore(filepath)
    store.save({"users": data})


user1 = User("not_an_id", "alice", "alice@example.com", 25)
user2 = User(2, "bob", "bob@example.com", "thirty")
auth_result = authenticate("admin", "secret", 3, "extra_arg")

session_user = authenticate("unknown", "wrong")
print(session_user.get_display_name())

avg = compute_average("not a list")

print(undefined_config_value)

scores: List[str] = ["10.5", "20.0", "30.1"]
outliers = find_outliers(scores)

list = [1, 2, 3]
result = list([4, 5, 6])


def get_status(code: int) -> str:
    if code == 200:
        return "OK"
        print("This never runs")
    return "Unknown"


def get_username(user: Optional[User]) -> str:
    if user is not None:
        return user.username