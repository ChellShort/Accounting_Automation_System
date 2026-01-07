import tkinter as tk
from queue import Queue
import threading
import time
import tkinter as tk
from tkinter import filedialog

# Hacemos una cola de notificaciones
notification_queue = Queue() # Cola de notificaciones infinita

def send_notification(message):
    notification_queue.put(message) # Agregamos una notificacion a la cola

class App:
    def __init__(self, root):
        self.main_thread = False
        self.root = root
        self.root.title("Accounting Automation System")

        self.button_frame_1 = tk.Frame(root)
        self.button_frame_2 = tk.Frame(root)
        self.button_frame_3 = tk.Frame(root)

        self.btn_select_reports_directory = tk.Button(
            self.button_frame_1,
            text="Select Reports Directory",
            command=self.select_directory,
            width=20
        )
        self.report_directory = tk.Label(
            self.button_frame_1,
            text="No directory selected",
            wraplength=380
        )
    
        self.btn_select_template = tk.Button(
            self.button_frame_2,
            text = "Select Template",
            command= self.select_file,
            width= 20
        )
        self.template_directory = tk.Label(
            self.button_frame_2,
            text= "No template selected",
            wraplength = 380
        )

        self.btn_start = tk.Button(
            self.button_frame_3,
            text="Start",
            command= self.start_process,
            width = 20)
        
        self.btn_cancel = tk.Button(
            self.button_frame_3,
            text= "Cancel",
            command=self.cancel_process,
            width= 20)

        self.listbox = tk.Listbox(root)

        self.button_frame_1.pack(pady=20)
        self.button_frame_2.pack(pady=20)
        self.button_frame_3.pack()

        self.btn_select_reports_directory.pack(side=tk.LEFT, padx=20, expand=True)
        self.report_directory.pack(side=tk.LEFT, padx=20, expand= True)

        self.btn_select_template.pack(side=tk.LEFT, padx=20, expand=True)
        self.template_directory.pack(side=tk.LEFT, padx=20, expand=True)

        self.btn_start.pack(side=tk.LEFT, padx=20, expand=True)
        self.btn_cancel.pack(side=tk.LEFT, padx=20, expand=True)

        # self.btn_select.pack(pady=20)
        # self.label_path.pack(pady=20)
        self.listbox.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.poll_notifications()

    def poll_notifications(self):
        while not notification_queue.empty():  # Mientras la cola no este vacia, 
            msg = notification_queue.get() # Se seguiran sacando elementos de la cola
            self.listbox.insert(0, msg) # y se nsertaran dentro del listbox

        self.root.after(100, self.poll_notifications) # esto hace que la funcion se repita cada 100 ms
    
    def select_directory(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.report_directory.config(text=folder_selected)

    def select_file(self):
        file_selected = filedialog.askopenfile()
        if file_selected:
            self.template_directory.config(text=file_selected.name)

    def start_process(self):
        if not self.main_thread or not self.main_thread.is_alive():
            send_notification("Process started.")
            self._running = True
            self.main_thread = threading.Thread(target=self.background_task, daemon=True)
            self.main_thread.start()
        else:
            send_notification("Process is already running.")
        return None
    
    def cancel_process(self):
        if self.main_thread and self.main_thread.is_alive():
            self._running = False
            send_notification("Process canceled")
        else:
            send_notification("No process is running to cancel")
        return None

    def background_task(self):
        for i in range(5):
            if not self._running:
                send_notification("Background task stopped.")
                break
            send_notification(f"Background event {i + 1}")
        self.running = False
        send_notification("Background task completed.")

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
