import time
from typing import Dict, Tuple, Set

class TuringMachine:
    def __init__(
        self,
        states: Set[str],
        input_symbols: Set[str],
        tape_symbols: Set[str],
        transitions: Dict[Tuple[str, str], Tuple[str, str, str]],
        initial_state: str,
        blank_symbol: str,
        final_states: Set[str],
        tape_input: str = ""
    ):
        self.states = states
        self.input_symbols = input_symbols
        self.tape_symbols = tape_symbols
        self.transitions = transitions
        self.state = initial_state
        self.blank = blank_symbol
        self.final_states = final_states

        # Infinite tape using dictionary
        self.tape = {}
        for i, ch in enumerate(tape_input):
            self.tape[i] = ch

        self.head = 0
        self.step_count = 0

    # ---------------- Tape operations ----------------

    def read(self, position: int) -> str:
        return self.tape.get(position, self.blank)

    def write(self, position: int, symbol: str):
        if symbol == self.blank:
            self.tape.pop(position, None)
        else:
            self.tape[position] = symbol

    # ---------------- Visualization ----------------

    def visualize(self, window: int = 6):
        min_index = min(self.tape.keys(), default=0)
        max_index = max(self.tape.keys(), default=0)

        left = min(min_index, self.head) - window
        right = max(max_index, self.head) + window

        tape_line = ""
        head_line = ""

        for i in range(left, right + 1):
            tape_line += f"{self.read(i)} "
            if i == self.head:
                head_line += "↑ "
            else:
                head_line += "  "

        print(f"Step: {self.step_count}")
        print(f"State: {self.state}")
        print("Tape :", tape_line)
        print("       ", head_line)
        print("-" * 50)

    # ---------------- One step ----------------

    def step(self) -> bool:
        current_symbol = self.read(self.head)
        key = (self.state, current_symbol)

        if key not in self.transitions:
            return False  # halt

        new_state, write_symbol, direction = self.transitions[key]

        self.write(self.head, write_symbol)
        self.state = new_state

        if direction == 'R':
            self.head += 1
        elif direction == 'L':
            self.head -= 1

        self.step_count += 1
        return True

    # ---------------- Run machine ----------------

    def run(self, delay: float = 0.7):
        print("\nInitial configuration")
        self.visualize()
        time.sleep(delay)

        while True:
            if self.state in self.final_states:
                print("✅ ACCEPTED")
                break

            if not self.step():
                print("❌ REJECTED")
                break

            self.visualize()
            time.sleep(delay)

# ==================================================
# Turing Machine: Even number of 1s
# ==================================================

states = {'q_even', 'q_odd', 'q_accept', 'q_reject'}
input_symbols = {'0', '1'}
tape_symbols = {'0', '1', '_'}
blank = '_'
initial_state = 'q_even'
final_states = {'q_accept'}

transitions = {
    ('q_even', '1'): ('q_odd', '1', 'R'),
    ('q_even', '0'): ('q_even', '0', 'R'),
    ('q_even', '_'): ('q_accept', '_', 'N'),

    ('q_odd', '1'): ('q_even', '1', 'R'),
    ('q_odd', '0'): ('q_odd', '0', 'R'),
    ('q_odd', '_'): ('q_reject', '_', 'N'),
}

# ---------------- TEST INPUT ----------------

input_string = "11011"   # try changing this!

tm = TuringMachine(
    states,
    input_symbols,
    tape_symbols,
    transitions,
    initial_state,
    blank,
    final_states,
    input_string
)

tm.run(delay=0.8)
