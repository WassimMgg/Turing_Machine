# turing_simulator.py
from typing import Dict, Tuple, Set, Optional

Direction = str  # 'L' or 'R' or 'N' (no-move)

class TuringMachine:
# states → All machine states (Q)

# input_symbols → Symbols allowed in the input alphabet (Σ)

# tape_symbols → Symbols allowed on the tape (Γ)

# transitions → Transition function δ

# initial_state → Starting state

# blank_symbol → Empty cell symbol (_)

# final_states → Accepting states

# tape_input → Input string on the tape
    def __init__(
        self,
        states: Set[str],
        input_symbols: Set[str],
        tape_symbols: Set[str],
        transitions: Dict[Tuple[str, str], Tuple[str, str, Direction]],
        initial_state: str,
        blank_symbol: str,
        final_states: Set[str],
        tape_input: str = ""
    ):
        """
        transitions: dict with keys (state, symbol) -> (new_state, write_symbol, direction)
        blank_symbol: e.g. '_'
        tape_input: initial content (string of input_symbols)
        """
        self.states = states
        self.input_symbols = input_symbols
        self.tape_symbols = tape_symbols
        self.transitions = transitions
        self.state = initial_state
        self.blank = blank_symbol
        self.final_states = final_states

        # Use a dictionary for an infinite tape: index -> symbol
        self.tape = {}
        for i, ch in enumerate(tape_input):
            self.tape[i] = ch
        # head starts at position 0
        self.head = 0
        self.step_count = 0

    def read(self, position: int) -> str:
        return self.tape.get(position, self.blank)

    def write(self, position: int, symbol: str):
        if symbol == self.blank:
            # optional: erase blanks to keep tape small
            if position in self.tape:
                del self.tape[position]
        else:
            self.tape[position] = symbol

    def current_symbol(self) -> str:
        return self.read(self.head)

    def step(self) -> bool:
        """Performs one transition. Returns True if a transition was applied; False if machine halts (no transition)."""
        cur_sym = self.current_symbol()
        key = (self.state, cur_sym)
        if key not in self.transitions:
            return False  # no applicable rule -> halt
        new_state, write_sym, direction = self.transitions[key]
        # apply rule
        self.write(self.head, write_sym)
        self.state = new_state
        if direction == 'R':
            self.head += 1
        elif direction == 'L':
            self.head -= 1
        elif direction == 'N':
            pass
        else:
            raise ValueError(f"Invalid direction: {direction}")
        self.step_count += 1
        return True

    def tape_str_window(self, padding: int = 10) -> Tuple[str, int]:
        """
        Return a string representation of tape around non-blank cells (with padding),
        plus the index of the head within that string.
        """
        if self.tape:
            min_idx = min(min(self.tape.keys()), self.head)
            max_idx = max(max(self.tape.keys()), self.head)
        else:
            min_idx = min(0, self.head)
            max_idx = max(0, self.head)
        # extend window by padding
        left = min_idx - padding
        right = max_idx + padding
        cells = []
        head_pos_in_str = None
        for i in range(left, right + 1):
            ch = self.read(i)
            cells.append(ch)
            if i == self.head:
                head_pos_in_str = len(''.join(cells)) - 1  # position in final string
        tape_str = ''.join(cells)
        return tape_str, (self.head - left)

    def pretty_print(self):
        tape_str, head_pos = self.tape_str_window(padding=8)
        # show tape with head marker
        head_marker = ' ' * head_pos + '^'
        print(f"Step {self.step_count:3d} | state={self.state} | head={self.head}")
        print("Tape: ", tape_str)
        print("      ", head_marker)
        print()

    def run(self, max_steps: int = 10000, verbose: bool = True) -> Tuple[bool, Optional[str]]:
        """
        Run until accept / reject / halt or max_steps.
        Returns (accepted_bool, final_state_or_None)
        """
        if verbose:
            print("Initial configuration:")
            self.pretty_print()

        for _ in range(max_steps):
            if self.state in self.final_states:
                if verbose:
                    print(f"Machine halted in final state '{self.state}' after {self.step_count} steps: ACCEPT")
                    self.pretty_print()
                return True, self.state
            applied = self.step()
            if not applied:
                # no transition available -> halting non-final state => reject
                if verbose:
                    print(f"No transition for (state={self.state}, symbol={self.current_symbol()}). HALT (reject).")
                    self.pretty_print()
                return False, self.state
            if verbose:
                self.pretty_print()

        # exceeded max steps
        if verbose:
            print(f"Exceeded max steps ({max_steps}). Halting as REJECT/UNKNOWN.")
        return False, None

# -------------------------
# Example machine: parity of 1's (accept if even number of '1' in the input)
# Alphabet: {'0','1'} ; blank symbol '_'
#
# Idea:
# - State 'q_even' = we've seen an even number of 1's so far
# - State 'q_odd'  = we've seen an odd number of 1's so far
# - When we read '1' we toggle between q_even and q_odd and move right.
# - When we read '0' we just move right (state unchanged).
# - When we read blank '_' we halt: if in q_even -> accept, else reject.
# -------------------------
if __name__ == "__main__":
    states = {'q_even', 'q_odd', 'q_accept', 'q_reject'}
    input_symbols = {'0', '1'}
    tape_symbols = {'0', '1', '_'}
    blank = '_'
    initial_state = 'q_even'
    final_states = {'q_accept'}

    # transitions: (state, symbol) -> (new_state, write_symbol, direction)
    transitions = {
        ('q_even', '1'): ('q_odd',  '1', 'R'),
        ('q_even', '0'): ('q_even', '0', 'R'),
        ('q_even', '_'): ('q_accept', '_', 'N'),  # accept when blank and even

        ('q_odd',  '1'): ('q_even', '1', 'R'),
        ('q_odd',  '0'): ('q_odd',  '0', 'R'),
        ('q_odd',  '_'): ('q_reject', '_', 'N'),  # reject when blank and odd
    }

    # try some inputs
    examples = ["", "1", "11", "1011", "1100", "1101"]
    for inp in examples:
        print("===")
        print(f"Input: '{inp}'")
        tm = TuringMachine(
            states=states,
            input_symbols=input_symbols,
            tape_symbols=tape_symbols,
            transitions=transitions,
            initial_state=initial_state,
            blank_symbol=blank,
            final_states=final_states,
            tape_input=inp
        )
        accepted, final = tm.run(max_steps=500, verbose=True)
        print(f"Result for input '{inp}': {'ACCEPTED' if accepted else 'REJECTED'} (final state = {final})\n\n")
