import tkinter as tk
import interface_app
import custom_classes

if __name__ == "__main__":
    root = tk.Tk()
    app = interface_app.App(root, new_analysis=custom_classes.Analysis())
    root.mainloop()