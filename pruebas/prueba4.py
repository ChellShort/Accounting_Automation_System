import tkinter as tk
from tkinter import filedialog

def select_directory():
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        label_path.config(text=folder_selected)

# Create main window
root = tk.Tk()
root.title("Select Directory")
root.geometry("400x150")

# Button to open directory dialog
btn_select = tk.Button(
    root,
    text="Select Directory",
    command=select_directory,
    width=20
)
btn_select.pack(pady=20)

# Label to display selected path
label_path = tk.Label(
    root,
    text="No directory selected",
    wraplength=380
)
label_path.pack(pady=10)

# Start the GUI loop
root.mainloop()
