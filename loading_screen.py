from tkinter import *
from tkinter import ttk
import tools

class LoadingScreen:
    def __init__(self):
        window_size = {'width': "800", 'height': "450"}

        self.root = Tk()
        self.root.title("Pika Center Invoicing Program - Loading...")
        self.root.geometry(tools.generate_tk_geometry(window_size))
        self.root.resizable(False, False)
        
        # Prevents closing
        self.root.protocol('WM_DELETE_WINDOW', lambda: None)
        # self.root.attributes('-fullscreen', True)
        label = ttk.Label(self.root, text='Pika Center Invoicing Program', font=("Calibri", "36", "bold  "))
        label.grid(column=0, row=0)
    
        self.progress_label = StringVar()
        progress_label = ttk.Label(self.root, textvariable=self.progress_label)
        progress_label.grid(column=0, row=1, sticky=(W))

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=5)
        self.root.rowconfigure(1, weight=1)
        self.root.after(2000, lambda: self.root.destroy())

        self.root.mainloop()
        
        
