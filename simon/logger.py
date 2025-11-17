import numpy as np
from typing import Literal


class LogEntry:
    def __init__(self, content, label: str = ""):
        self.content = content
        self.label = label

    def to_str(self, num_format: Literal["h", "b"] = "h") -> str:
        """Convert content to string."""
        if self.label == "":
            label_str = ""
        else:
            label_str = self.label + ": "

        if num_format == "b":
            if isinstance(self.content, np.ndarray):
                return label_str + " ".join(
                    ["{:032b}".format(b) for b in self.content.flatten()]
                )
            elif isinstance(self.content, np.integer):
                return label_str + "{:032b}".format(self.content)
            else:
                return label_str + str(self.content)
        else:
            if isinstance(self.content, np.ndarray):
                return label_str + " ".join(
                    ["{:08X}".format(b) for b in self.content.flatten()]
                )
            elif isinstance(self.content, np.integer):
                return label_str + "{:08X}".format(self.content)
            else:
                return label_str + str(self.content)

    def xor(self, other: "LogEntry") -> "LogEntry":
        """XOR two log entries together."""
        if isinstance(self.content, np.ndarray) and isinstance(
            other.content, np.ndarray
        ):
            new_content = self.content ^ other.content
        elif isinstance(self.content, np.integer) and isinstance(
            other.content, np.integer
        ):
            new_content = self.content ^ other.content
        else:
            new_content = self.content  # Cannot XOR. Just use original content.
        return LogEntry(new_content, self.label)


class Log:
    """Logging utility for cipher implementation."""

    def __init__(self):
        self.entries: list[LogEntry] = []

    def add(self, content, label: str = ""):
        """Append content to the log."""
        new_entry = LogEntry(content, label)
        self.entries.append(new_entry)

    def to_str(self, num_format: Literal["h", "b"] = "h") -> str:
        log_str = "=== SIMON LOG ===\n"
        log_str = "=== SIMON LOG ===\n"
        log_str += "\n".join([e.to_str(num_format) for e in self.entries])
        log_str += "\n=== END OF LOG ==="
        return log_str

    def xor(self, other: "Log") -> "Log":
        """XOR two logs together."""
        result = Log()
        for a, b in zip(self.entries, other.entries):
            result.entries.append(a.xor(b))
        return result
