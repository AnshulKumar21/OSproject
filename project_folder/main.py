import tkinter as tk
from tkinter import messagebox
from backEnd import DeadlockDetector
import threading
import time

def worker(detector, thread_id, resource_id, output_text):
    if detector.request_resource(thread_id, resource_id):
        output_text.insert(tk.END, f"Thread {thread_id} acquired Resource {resource_id}\n")
        time.sleep(0.5)
        detector.release_resource(thread_id, resource_id)
        output_text.insert(tk.END, f"Thread {thread_id} released Resource {resource_id}\n")
    else:
        output_text.insert(tk.END, f"[ALERT] Deadlock detected for Thread {thread_id} requesting Resource {resource_id}!\n")

def start_simulation():
    def run_simulation():
        try:
            num_tasks = int(entry_tasks.get())
            output_text.delete(1.0, tk.END)
            detector = DeadlockDetector()
            threads = []
            
            for i in range(num_tasks):
                t = threading.Thread(target=worker, args=(detector, f"T{i}", f"R{i}", output_text))
                threads.append(t)
                t.start()
            
            for t in threads:
                t.join()
            
            messagebox.showinfo("Execution", "Execution Completed")
        except ValueError:
            messagebox.showerror("Input Error", "Please enter a valid number")

    threading.Thread(target=run_simulation, daemon=True).start()

root = tk.Tk()
root.title("Deadlock Detection GUI")

tk.Label(root, text="Enter number of tasks:").pack()
entry_tasks = tk.Entry(root)
entry_tasks.pack()

tk.Button(root, text="Start Simulation", command=start_simulation).pack()

output_text = tk.Text(root, height=10, width=50)
output_text.pack()

root.mainloop()
