# sample_code.py
# This is the file our LSP agent will analyze.
# It has intentional bugs for the agent to find!

import math  # imported but never used — pylsp will flag this


def add(a: int, b: int) -> int:
    """Adds two integers."""
    return a + b


def divide(a: float, b: float) -> float:
    """Divides a by b."""
    return a / b  # risky — no zero check


def greet(name: str) -> str:
    return "Hello, " + name


class Calculator:
    def __init__(self):
        self.history = []

    def compute(self, op: str, x: float, y: float) -> float:
        if op == "add":
            result = add(x, y)
        elif op == "divide":
            result = divide(x, y)
        else:
            raise ValueError(f"Unknown op: {op}")
        self.history.append((op, x, y, result))
        return result


# TYPE ERROR: passing string instead of int — pylsp catches this
result = add("hello", 5)

# NAME ERROR: undefined variable
print(undefined_variable)