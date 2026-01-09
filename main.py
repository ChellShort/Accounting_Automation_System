import tkinter as tk
import interface_app
import custom_classes

if __name__ == "__main__":
    root = tk.Tk()
    app = interface_app.App(root, new_analysis=custom_classes.Analysis())
    root.geometry("1000x800")
    root.resizable(False, False) # Disables both width and height resizing
    root.mainloop()