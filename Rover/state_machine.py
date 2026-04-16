from enum import Enum, auto

class RobotState(Enum):
    BOOT = auto()
    IDLE = auto()
    MANUAL_CONTROL = auto()
    SAFETY_OVERRIDE = auto()
    COMM_LOST = auto()
    RECOVERY = auto()
    SHUTDOWN = auto()

import threading

class StateMachine:
    def __init__(self):
        self._lock = threading.Lock()
        self.state = RobotState.BOOT

    def set_state(self, new_state):
        with self._lock:
            print(f"[STATE] {self.state.name} → {new_state.name}")
            self.state = new_state

    def get_state(self):
        with self._lock:
            return self.state