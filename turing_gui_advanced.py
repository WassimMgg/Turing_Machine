import tkinter as tk
import copy

# ==================================================
# TURING MACHINE CORE (WITH UNDO)
# ==================================================

class TuringMachine:
    def __init__(self, transitions, initial_state, final_states, blank):
        self.transitions = transitions
        self.initial_state = initial_state
        self.final_states = final_states
        self.blank = blank
        self.history = []
        self.reset("")

    def snapshot(self):
        return copy.deepcopy((
            self.state, self.tape, self.head,
            self.steps, self.halted, self.accepted
        ))

    def restore(self, snap):
        (self.state, self.tape, self.head,
         self.steps, self.halted, self.accepted) = snap

    def reset(self, tape_input):
        self.state = self.initial_state
        self.tape = {i: c for i, c in enumerate(tape_input)}
        self.head = 0
        self.steps = 0
        self.halted = False
        self.accepted = False
        self.history.clear()

    def read(self):
        return self.tape.get(self.head, self.blank)

    def write(self, sym):
        if sym == self.blank:
            self.tape.pop(self.head, None)
        else:
            self.tape[self.head] = sym

    def step(self):
        if self.halted:
            return False

        self.history.append(self.snapshot())

        key = (self.state, self.read())
        if key not in self.transitions:
            self.halted = True
            self.accepted = self.state in self.final_states
            return False

        ns, w, mv = self.transitions[key]
        self.write(w)
        self.state = ns

        if mv == 'R': self.head += 1
        elif mv == 'L': self.head -= 1

        self.steps += 1

        if self.state in self.final_states:
            self.halted = True
            self.accepted = True

        return True

    def undo(self):
        if self.history:
            self.restore(self.history.pop())

# ==================================================
# TURING MACHINES (INCLUDING a^n b^n)
# ==================================================

MACHINES = {
    "Even number of 1s": {
        "initial": "q_even",
        "final": {"q_accept"},
        "alphabet": {"0","1"},
        "tape": {"0","1","_"},
        "transitions": {
            ('q_even','1'):('q_odd','1','R'),
            ('q_even','0'):('q_even','0','R'),
            ('q_even','_'):('q_accept','_','N'),
            ('q_odd','1'):('q_even','1','R'),
            ('q_odd','0'):('q_odd','0','R'),
            ('q_odd','_'):('q_reject','_','N'),
        }
    },

    "a^n b^n": {
        "initial": "q0",
        "final": {"q_accept"},
        "alphabet": {"a","b"},
        "tape": {"a","b","X","Y","_"},
        "transitions": {
            ('q0','a'):('q1','X','R'),
            ('q0','Y'):('q0','Y','R'),
            ('q0','_'):('q_accept','_','N'),

            ('q1','a'):('q1','a','R'),
            ('q1','Y'):('q1','Y','R'),
            ('q1','b'):('q2','Y','L'),

            ('q2','a'):('q2','a','L'),
            ('q2','Y'):('q2','Y','L'),
            ('q2','X'):('q0','X','R'),
        }
    }
}

# ==================================================
# GUI
# ==================================================

class GUI:
    def __init__(self, root):
        self.root = root
        root.title("Turing Machine Simulator (Final)")
        root.geometry("1200x850")  # a bit taller for slider

        self.machine_name = tk.StringVar(value="Even number of 1s")

        top = tk.Frame(root)
        top.pack()

        tk.OptionMenu(top, self.machine_name, *MACHINES).pack(side=tk.LEFT)
        self.machine_name.trace_add("write", self.change_machine)

        self.input = tk.Entry(top, width=20)
        self.input.insert(0,"11011")  # default input
        self.input.pack(side=tk.LEFT,padx=5)

        tk.Button(top,text="Reset",command=self.reset).pack(side=tk.LEFT)
        tk.Button(top,text="Step",command=self.step).pack(side=tk.LEFT)
        tk.Button(top,text="Undo",command=self.undo).pack(side=tk.LEFT)
        tk.Button(top,text="Run",command=self.run).pack(side=tk.LEFT)

        # ---------- Speed control ----------
        speed_frame = tk.Frame(root)
        speed_frame.pack(pady=5)
        tk.Label(speed_frame,text="Speed:").pack(side=tk.LEFT)
        self.speed_var = tk.DoubleVar(value=0.6)  # default 600 ms
        self.speed_slider = tk.Scale(speed_frame, from_=0.1, to=2.0, resolution=0.1,
                                     orient=tk.HORIZONTAL, variable=self.speed_var,
                                     length=200)
        self.speed_slider.pack(side=tk.LEFT)

        self.info = tk.Label(root,font=("Arial",14))
        self.info.pack()

        self.tape = tk.Canvas(root,height=140,bg="white")
        self.tape.pack(fill=tk.X)

        self.formal = tk.Text(root,height=10,font=("Courier",11))
        self.formal.pack(fill=tk.X)

        self.load_machine()

    # ---------- Machine ----------
    def load_machine(self):
        m = MACHINES[self.machine_name.get()]
        self.tm = TuringMachine(
            m["transitions"], m["initial"], m["final"], "_"
        )

        self.formal.delete(1.0,tk.END)
        self.formal.insert(tk.END,
            f"Q = {set([s for s,_ in m['transitions'].keys()])}\n"
            f"Σ = {m['alphabet']}\n"
            f"Γ = {m['tape']}\n"
            f"q0 = {m['initial']}\n"
            f"F = {m['final']}\n"
            f"δ defined for {len(m['transitions'])} transitions\n"
        )

    def change_machine(self,*_):
        self.load_machine()
        self.reset()

    # ---------- Controls ----------
    def reset(self):
        self.tm.reset(self.input.get())
        self.draw()

    def step(self):
        self.tm.step()
        self.draw()

    def undo(self):
        self.tm.undo()
        self.draw()

    def run(self):
        if not self.tm.halted:
            self.tm.step()
            self.draw()
            # use slider value for delay
            delay = int(self.speed_var.get() * 1000)
            self.root.after(delay, self.run)

    # ---------- Drawing ----------
    def draw(self):
        self.tape.delete("all")
        start = self.tm.head - 6

        for i in range(start,start+13):
            x = (i-start)*60+100
            s = self.tm.tape.get(i,'_')
            c = "lightblue" if i==self.tm.head else "white"
            self.tape.create_rectangle(x,40,x+50,90,fill=c)
            self.tape.create_text(x+25,65,text=s,font=("Arial",16))

        if self.tm.halted:
            self.info.config(
                text="ACCEPTED" if self.tm.accepted else "REJECTED",
                fg="green" if self.tm.accepted else "red"
            )
        else:
            self.info.config(text=f"State: {self.tm.state} | Steps: {self.tm.steps}")

# ==================================================
# START
# ==================================================

root=tk.Tk()
GUI(root)
root.mainloop()
