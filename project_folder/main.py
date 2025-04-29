import tkinter as tk
import networkx as nx
import matplotlib
matplotlib.use("TkAgg")  # Use the TkAgg backend
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class DeadlockDetector:
    def __init__(self, root):
        self.root = root
        self.root.title("Deadlock Detection Tool")
        self.entries_alloc = []
        self.entries_req = []
        self.entries_total = []
        self.num_proc = 0
        self.num_res = 0
        self.graph_window = None # To hold the graph window

        # Process/Resource Count Input
        tk.Label(root, text="Enter number of processes:").pack()
        self.entry_proc = tk.Entry(root)
        self.entry_proc.pack()

        tk.Label(root, text="Enter number of resources:").pack()
        self.entry_res = tk.Entry(root)
        self.entry_res.pack()

        tk.Button(root, text="Generate Input Tables", command=self.generate_tables).pack(pady=5)
        self.table_frame = tk.Frame(root)
        self.table_frame.pack()

        self.btn_detect = tk.Button(root, text="Detect Deadlock & Show Graph", command=self.detect_deadlock_and_draw)
        self.btn_detect.pack(pady=10)

    def generate_tables(self):
        for widget in self.table_frame.winfo_children():
            widget.destroy()
        self.entries_alloc, self.entries_req, self.entries_total = [], [], []

        try:
            self.num_proc = int(self.entry_proc.get())
            self.num_res = int(self.entry_res.get())
        except ValueError:
            self.show_popup("Please enter valid integers for process and resource counts.")
            return

        # Allocation Matrix
        tk.Label(self.table_frame, text="Allocation Matrix").grid(row=0, column=0, columnspan=self.num_res + 1, pady=(0, 5))
        tk.Label(self.table_frame, text="").grid(row=1, column=0) # Empty cell for spacing
        for j in range(self.num_res):
            tk.Label(self.table_frame, text=f"R{j}").grid(row=1, column=j + 1)
        for i in range(self.num_proc):
            row_entries = []
            tk.Label(self.table_frame, text=f"P{i}").grid(row=i + 2, column=0)
            for j in range(self.num_res):
                e = tk.Entry(self.table_frame, width=5)
                e.grid(row=i + 2, column=j + 1)
                row_entries.append(e)
            self.entries_alloc.append(row_entries)

        offset = self.num_proc + 4
        # Request Matrix
        tk.Label(self.table_frame, text="Request Matrix").grid(row=offset, column=0, columnspan=self.num_res + 1, pady=(10, 5))
        tk.Label(self.table_frame, text="").grid(row=offset + 1, column=0) # Empty cell for spacing
        for j in range(self.num_res):
            tk.Label(self.table_frame, text=f"R{j}").grid(row=offset + 1, column=j + 1)
        for i in range(self.num_proc):
            row_entries = []
            tk.Label(self.table_frame, text=f"P{i}").grid(row=offset + i + 2, column=0)
            for j in range(self.num_res):
                e = tk.Entry(self.table_frame, width=5)
                e.grid(row=offset + i + 2, column=j + 1)
                row_entries.append(e)
            self.entries_req.append(row_entries)

        offset = offset + self.num_proc + 4
        # Total Resources (Optional)
        tk.Label(self.table_frame, text="(Optional) Total Resources").grid(row=offset, column=0, columnspan=self.num_res, pady=(10, 5))
        for j in range(self.num_res):
            tk.Label(self.table_frame, text=f"R{j}").grid(row=offset + 1, column=j)
            e = tk.Entry(self.table_frame, width=5)
            e.grid(row=offset + 2, column=j)
            self.entries_total.append(e)

    def detect_deadlock(self):
        try:
            alloc = [[int(e.get()) for e in row] for row in self.entries_alloc]
            req = [[int(e.get()) for e in row] for row in self.entries_req]
            total_resources_str = [e.get() for e in self.entries_total]
            total_resources = [int(val) if val else 0 for val in total_resources_str]
        except ValueError:
            self.show_popup("All entries in the tables must be integers.")
            return None, None, None, None

        if not self.num_proc or not self.num_res or len(alloc) != self.num_proc or len(req) != self.num_proc or any(len(row) != self.num_res for row in alloc) or any(len(row) != self.num_res for row in req) or len(total_resources) != self.num_res:
            self.show_popup("Please ensure all input tables are correctly filled.")
            return None, None, None, None

        # Auto-calculate total resources if not fully provided
        for j in range(self.num_res):
            if total_resources[j] == 0:
                total_resources[j] = sum(alloc[i][j] for i in range(self.num_proc))

        available = [total_resources[j] - sum(alloc[i][j] for i in range(self.num_proc)) for j in range(self.num_res)]

        p, r = self.num_proc, self.num_res
        finish = [False] * p
        work = list(available)
        deadlocked = []

        while True:
            found = False
            for i in range(p):
                if not finish[i] and all(req[i][j] <= work[j] for j in range(r)):
                    for j in range(r):
                        work[j] += alloc[i][j]
                    finish[i] = True
                    found = True
            if not found:
                break

        for i in range(p):
            if not finish[i]:
                deadlocked.append(i)

        return alloc, req, deadlocked, total_resources, available

    def detect_deadlock_and_draw(self):
        result = self.detect_deadlock()
        if result:
            alloc, req, deadlocked, total_resources, available = result
            msg = f"""
Total Resources: {total_resources}
Available Resources: {available}

Deadlocked Processes: {', '.join(f'P{i}' for i in deadlocked) or 'None'}

Result: {'🛑 Deadlock Detected' if deadlocked else '✅ No Deadlock'}
            """
            self.show_popup(msg.strip())
            self.draw_graph(alloc, req, deadlocked)
        else:
            # Error occurred during deadlock detection
            pass

    def draw_graph(self, alloc, req, deadlocked):
        G = nx.DiGraph()
        p, r = len(alloc), len(alloc[0])

        for i in range(p):
            G.add_node(f"P{i}", color='red' if i in deadlocked else 'lightgreen')
        for j in range(r):
            G.add_node(f"R{j}", color='skyblue')

        for i in range(p):
            for j in range(r):
                if req[i][j] > 0:
                    G.add_edge(f"P{i}", f"R{j}", label="Request")
                if alloc[i][j] > 0:
                    G.add_edge(f"R{j}", f"P{i}", label="Alloc")

        colors = [G.nodes[n]['color'] for n in G.nodes]
        pos = nx.spring_layout(G, seed=42)
        edge_labels = nx.get_edge_attributes(G, 'label')

        try:
            fig, ax = plt.subplots(figsize=(8, 6))
            nx.draw(G, pos, with_labels=True, node_color=colors, arrows=True,
                    node_size=1600, font_size=12, edge_color='gray',
                    arrowstyle='->', arrowsize=20, ax=ax)
            nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=10, ax=ax)
            ax.set_title("Resource Allocation Graph (RAG)")
            fig.tight_layout()

            # Embed the Matplotlib figure in a Tkinter Toplevel window
            if self.graph_window is None or not tk.Toplevel.winfo_exists(self.graph_window):
                self.graph_window = tk.Toplevel(self.root)
                self.graph_window.title("Resource Allocation Graph")

            canvas = FigureCanvasTkAgg(fig, master=self.graph_window)
            canvas_widget = canvas.get_tk_widget()
            canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
            canvas.draw()

        except Exception as e:
            print(f"Error drawing graph: {e}")
            self.show_popup(f"Error drawing graph: {e}")

    def show_popup(self, message):
        popup = tk.Toplevel()
        popup.title("Result")
        tk.Label(popup, text=message, padx=20, pady=20, justify="left").pack()
        tk.Button(popup, text="OK", command=popup.destroy).pack(pady=(0, 10))


if __name__ == "__main__":
    root = tk.Tk()
    app = DeadlockDetector(root)
    root.mainloop()
