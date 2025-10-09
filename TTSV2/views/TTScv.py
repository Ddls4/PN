# frame_one.py
import tkinter as tk

def create_frame_one(container):
    frame = tk.Frame(container, bg="lightblue")
    frame.place(relwidth=1, relheight=1)
    label = tk.Label(frame, text="Este es el Frame 1", bg="lightblue", font=("Arial", 16))
    label.pack(pady=20)
    return frame