import tkinter as tk
import copy
import math

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
# TURING MACHINES
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
        root.title("Turing Machine Simulator")
        root.geometry("1400x800")

        self.machine_name = tk.StringVar(value="Even number of 1s")

        # Main horizontal layout
        main_frame = tk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Left side: controls, tape, info, formal
        left_frame = tk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        # Top controls
        top_controls = tk.Frame(left_frame)
        top_controls.pack()
        tk.OptionMenu(top_controls, self.machine_name, *MACHINES).pack(side=tk.LEFT)
        self.machine_name.trace_add("write", self.change_machine)
        self.input = tk.Entry(top_controls, width=20)
        self.input.insert(0,"aabb")
        self.input.pack(side=tk.LEFT,padx=5)
        tk.Button(top_controls,text="Reset",command=self.reset).pack(side=tk.LEFT)
        tk.Button(top_controls,text="Step",command=self.step).pack(side=tk.LEFT)
        tk.Button(top_controls,text="Undo",command=self.undo).pack(side=tk.LEFT)
        tk.Button(top_controls,text="Run",command=self.run).pack(side=tk.LEFT)

        # Speed control
        speed_frame = tk.Frame(left_frame)
        speed_frame.pack(pady=5)
        tk.Label(speed_frame,text="Speed:").pack(side=tk.LEFT)
        self.speed_var = tk.DoubleVar(value=0.6)
        self.speed_slider = tk.Scale(speed_frame, from_=0.1, to=2.0, resolution=0.1,
                                     orient=tk.HORIZONTAL, variable=self.speed_var, length=200)
        self.speed_slider.pack(side=tk.LEFT)

        # Info label
        self.info = tk.Label(left_frame,font=("Arial",14))
        self.info.pack(pady=10)

        # Tape canvas
        self.tape = tk.Canvas(left_frame,height=140,bg="white")
        self.tape.pack(fill=tk.X, pady=5)

        # Formal description
        self.formal = tk.Text(left_frame,height=10,font=("Courier",11))
        self.formal.pack(fill=tk.X, pady=5)

        # Right side: diagram
        right_frame = tk.Frame(main_frame)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.diagram = tk.Canvas(right_frame,bg="white")
        self.diagram.pack(fill=tk.BOTH, expand=True)

        # Load machine
        self.load_machine()

    # ---------- Machine ----------
    def load_machine(self):
        m = MACHINES[self.machine_name.get()]
        self.tm = TuringMachine(
            m["transitions"], m["initial"], m["final"], "_"
        )

        # Formal description
        all_states = set([s for s,_ in m["transitions"].keys()])
        all_states.update([dst for _,dst,_ in m["transitions"].values()])
        all_states.update(m["final"])
        self.formal.delete(1.0,tk.END)
        self.formal.insert(tk.END,
            f"Q = {all_states}\n"
            f"Σ = {m['alphabet']}\n"
            f"Γ = {m['tape']}\n"
            f"q0 = {m['initial']}\n"
            f"F = {m['final']}\n"
            f"δ defined for {len(m['transitions'])} transitions\n"
        )

        # Prepare diagram layout
        self.state_coords = {}
        self.prepare_diagram(m)

    # ---------- Diagram ----------
    def prepare_diagram(self, machine):
        self.diagram.delete("all")

        # Include all states
        all_states = set()
        for (src, _), (dst, _, _) in machine["transitions"].items():
            all_states.add(src)
            all_states.add(dst)
        all_states.update(machine["final"])
        states = list(all_states)

        n = len(states)
        radius = 40

        # Force update canvas to get actual size
        self.diagram.update()
        width = self.diagram.winfo_width()
        height = self.diagram.winfo_height()

        # Center in canvas
        center_x = width / 2
        center_y = height / 2

        # Dynamically calculate spacing based on number of states and canvas size
        spacing = min(width, height) / 2 - 2*radius - 20  # leave margin

        self.state_coords = {}
        for i, s in enumerate(states):
            angle = 2*math.pi*i/n
            x = center_x + spacing*math.cos(angle)
            y = center_y + spacing*math.sin(angle)
            self.state_coords[s] = (x, y)

            # Final state double circle
            if s in machine["final"]:
                self.diagram.create_oval(x-radius-5, y-radius-5, x+radius+5, y+radius+5,
                                        outline="black", width=2)
            # Main circle
            self.diagram.create_oval(x-radius, y-radius, x+radius, y+radius, fill="white",
                                    outline="black", width=2, tags=("state", s))
            self.diagram.create_text(x, y, text=s, font=("Arial",12,"bold"))

        # Draw transitions connecting circle edges
        for (src, sym), (dst, _, _) in machine["transitions"].items():
            x1, y1 = self.state_coords[src]
            x2, y2 = self.state_coords[dst]

            dx = x2 - x1
            dy = y2 - y1
            dist = (dx**2 + dy**2)**0.5
            if dist == 0:
                # self-loop
                self.diagram.create_arc(x1-30, y1-50, x1+30, y1-10, start=0, extent=300,
                                        style=tk.ARC, width=2, outline="blue")
                self.diagram.create_text(x1, y1-55, text=sym, font=("Arial",10,"italic"))
                continue

            # Points on circle edge
            x_start = x1 + dx*radius/dist
            y_start = y1 + dy*radius/dist
            x_end = x2 - dx*radius/dist
            y_end = y2 - dy*radius/dist

            # Draw line
            self.diagram.create_line(x_start, y_start, x_end, y_end, arrow=tk.LAST,
                                    width=2, fill="blue")
            # Label mid-point
            mx, my = (x_start + x_end)/2 - dy*0.1, (y_start + y_end)/2 + dx*0.1
            self.diagram.create_text(mx, my, text=sym, font=("Arial",10,"italic"))

    # ---------- Controls ----------
    def change_machine(self,*_):
        self.load_machine()
        self.reset()

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
            delay = int(self.speed_var.get() * 1000)
            self.root.after(delay, self.run)

    # ---------- Drawing ----------
    def draw(self):
        # Tape
        self.tape.delete("all")
        start = self.tm.head - 6
        for i in range(start,start+13):
            x = (i-start)*60+100
            s = self.tm.tape.get(i,'_')
            c = "lightblue" if i==self.tm.head else "white"
            self.tape.create_rectangle(x,40,x+50,90,fill=c)
            self.tape.create_text(x+25,65,text=s,font=("Arial",16))

        # Info
        if self.tm.halted:
            self.info.config(
                text="ACCEPTED" if self.tm.accepted else "REJECTED",
                fg="green" if self.tm.accepted else "red"
            )
        else:
            self.info.config(text=f"State: {self.tm.state} | Steps: {self.tm.steps}")

        # Diagram animation
        for s in self.state_coords:
            fill = "yellow" if s==self.tm.state else "lightgreen" if s in self.tm.final_states else "white"
            width = 4 if s==self.tm.state else 2
            self.diagram.itemconfig(self.diagram.find_withtag(s), fill=fill, width=width)

# ==================================================
# START
# ==================================================
if __name__ == "__main__":
    root = tk.Tk()
    GUI(root)
    root.mainloop()
