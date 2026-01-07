import tkinter as tk
from tkinter import ttk

root = tk.Tk()
root.title("Listbox con Scrollbar")

# 1. Crear un contenedor (Frame) para agrupar el Listbox y el Scrollbar
frame = tk.Frame(root)
frame.pack(padx=10, pady=10)

# 2. Crear el Scrollbar
scrollbar = tk.Scrollbar(frame, orient="vertical")
scrollbar.pack(side="right", fill="y")

# 3. Crear el Listbox y conectarlo al Scrollbar mediante yscrollcommand
listbox = tk.Listbox(frame, yscrollcommand=scrollbar.set)
listbox.pack(side="left", fill="both")

# 4. Configurar el Scrollbar para que mueva la vista del Listbox
scrollbar.config(command=listbox.yview)

# Insertar datos de prueba
for i in range(100):
    listbox.insert("end", f"Elemento número {i}")

root.mainloop()
