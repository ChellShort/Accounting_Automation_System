import tkinter as tk
import interface_app
import custom_classes
import multiprocessing

if __name__ == "__main__":
    multiprocessing.freeze_support()
    root = tk.Tk()
    app = interface_app.App(root, new_analysis=custom_classes.Analysis())
    root.geometry("1000x800")
    root.resizable(False, False) # Disables both width and height resizing
    root.mainloop()