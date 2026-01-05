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

        # Place states in a circle
        self.state_coords = {}
        for i, s in enumerate(states):
            angle = 2 * math.pi * i / n
            x = center_x + spacing * math.cos(angle)
            y = center_y + spacing * math.sin(angle)
            self.state_coords[s] = (x, y)

            # Final state double circle
            if s in machine["final"]:
                self.diagram.create_oval(x-radius-5, y-radius-5, x+radius+5, y+radius+5,
                                        outline="black", width=2)
            # Main circle
            self.diagram.create_oval(x-radius, y-radius, x+radius, y+radius, fill="white",
                                    outline="black", width=2, tags=("state", s))
            self.diagram.create_text(x, y, text=s, font=("Arial",12,"bold"))

        # Draw transitions
        for (src, sym), (dst, _, _) in machine["transitions"].items():
            x1, y1 = self.state_coords[src]
            x2, y2 = self.state_coords[dst]

            dx = x2 - x1
            dy = y2 - y1
            dist = (dx**2 + dy**2)**0.5

            if dist == 0:
                # Self-loop properly around the circle without crossing it
                r = radius
                loop_radius = r * 1.5  # slightly bigger than circle
                angle1 = math.radians(45)
                angle2 = math.radians(135)

                # Start and end points on circle edge
                x_start = x1 + r * math.cos(angle1)
                y_start = y1 - r * math.sin(angle1)
                x_end = x1 + r * math.cos(angle2)
                y_end = y1 - r * math.sin(angle2)

                # Arc coordinates
                x0 = x1 - loop_radius
                y0 = y1 - loop_radius
                x1_ = x1 + loop_radius
                y1_ = y1 - loop_radius * 0.2  # flatten the loop

                self.diagram.create_arc(x0, y0, x1_, y1_, start=200, extent=140,
                                        style=tk.ARC, width=2, outline="blue")
                self.diagram.create_text(x1, y0 - 10, text=sym, font=("Arial",10,"bold"), fill="blue")
                continue

            # Normal transition line
            # Compute points on the edge of the circles
            x_start = x1 + dx*radius/dist
            y_start = y1 + dy*radius/dist
            x_end = x2 - dx*radius/dist
            y_end = y2 - dy*radius/dist

            # Draw arrow line
            self.diagram.create_line(x_start, y_start, x_end, y_end, arrow=tk.LAST,
                                    width=2, fill="blue")

            # Place symbol near the middle of the line, slightly offset
            mx, my = (x_start + x_end)/2 - dy*0.15, (y_start + y_end)/2 + dx*0.15
            self.diagram.create_text(mx, my, text=sym, font=("Arial",10,"bold"), fill="blue")
