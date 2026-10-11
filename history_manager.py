"""
History Manager: Persistence, Calculation Logging, Timestamps, and JSON Saving/Loading.
"""

import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional


class HistoryManager:
    """
    Manages calculation history with automatic persistence to a JSON file.
    """

    def __init__(self, filepath: str = "history.json", max_entries: int = 500):
        self.filepath = filepath
        self.max_entries = max_entries
        self.history: List[Dict[str, Any]] = []
        self.load()

    def load(self) -> None:
        """Loads calculation history from the JSON file."""
        if not os.path.exists(self.filepath):
            self.history = []
            return

        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    self.history = data
                else:
                    self.history = []
        except (json.JSONDecodeError, OSError):
            self.history = []

    def save(self) -> None:
        """Saves current calculation history to the JSON file."""
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(self.history, f, indent=2)
        except OSError:
            pass

    def add(self, expression: str, result: float) -> Dict[str, Any]:
        """Adds a new calculation entry to history and saves to JSON."""
        entry: Dict[str, Any] = {
            "id": len(self.history) + 1,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "expression": expression,
            "result": result,
        }
        self.history.append(entry)
        if len(self.history) > self.max_entries:
            self.history = self.history[-self.max_entries:]
            # Re-index
            for idx, item in enumerate(self.history, start=1):
                item["id"] = idx
        self.save()
        return entry

    def clear(self) -> None:
        """Clears calculation history and updates the JSON file."""
        self.history = []
        self.save()

    def get_last_result(self) -> float:
        """Returns the result of the most recent calculation, or 0.0."""
        if self.history:
            return float(self.history[-1].get("result", 0.0))
        return 0.0

    def get_recent(self, count: int = 15) -> List[Dict[str, Any]]:
        """Returns the most recent N calculation entries."""
        return self.history[-count:]
