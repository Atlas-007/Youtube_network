import tkinter as tk
from tkinter import ttk

def launch_gui():
    root = tk.Tk()
    root.title("YouTube Network Graph")
    root.geometry("700x600")
    root.configure(bg="#f5f5f5")  # light background

    # ---------- Styles ----------
    style = ttk.Style()
    style.configure("TEntry",
                    padding=5,
                    foreground="black",
                    font=("Helvetica", 12))

    style.configure("TButton",
                    font=("Helvetica", 12),
                    padding=5)

    # ---------- Helper for placeholder ----------
    def add_placeholder(entry, placeholder):
        entry.insert(0, placeholder)
        entry.config(foreground='grey')

        def on_focus_in(event):
            if entry.get() == placeholder:
                entry.delete(0, 'end')
                entry.config(foreground='black')

        def on_focus_out(event):
            if entry.get() == '':
                entry.insert(0, placeholder)
                entry.config(foreground='grey')

        entry.bind("<FocusIn>", on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)

    # ---------- Labels and Entry Widgets ----------
    labels = [
        "Enter channel name:",
        "Enter the number of channels in the graph:",
        "Enter the number of commenters (more = more accurate):",
        "Enter the number of subscriptions per commenter (more = more accurate):"
        
    ]

    placeholders = [
        "e.g. MrBeast",
        "e.g. 25",
        "e.g. 100",
        "e.g. 50"
    ]

    entries = []

    for i, (text, placeholder) in enumerate(zip(labels, placeholders)):
        lbl = tk.Label(root, text=text, font=("Helvetica", 12), bg="#f5f5f5")
        lbl.pack(pady=(20 if i==0 else 10, 5))
        
        entry = ttk.Entry(root, width=30)
        entry.pack(pady=5)
        add_placeholder(entry, placeholder)
        entries.append(entry)

    # ---------- Submit Function ----------
    user_input = {}

    def show_input():
        user_input["main_channel"] = entries[0].get()
        user_input["channels"] = int(entries[1].get())
        user_input["commenters"] = int(entries[2].get())
        user_input["subs_per_com"] = int(entries[3].get())
        print("User input:", user_input)  # for testing

        root.destroy()
    submit_button = ttk.Button(root, text="Submit", command=show_input)
    submit_button.pack(pady=20)

  
    root.mainloop()
    return user_input  



