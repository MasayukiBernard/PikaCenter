from tkinter import *
from tkinter import ttk
import tools

class Alert:
    def __init__(self, parent_child_roots_list, message):
        window_size = {'width': "450", 'height': "50"}

        self.root = Toplevel()
        # self.child_roots = []
        # parent_child_roots_list.append(self.child_roots)
        parent_child_roots_list.append(self.root)
        
        self.root.title("Pika Center Invoicing Program - Alert")
        self.root.geometry(tools.generate_tk_geometry(window_size))
        self.root.resizable(False, False)

        main_frame = ttk.Frame(self.root)

        label = ttk.Label(main_frame, text=message, foreground='red', anchor='center')
        label.grid(column=0, row=0)
        
        main_frame.grid(column=0, row=0, rowspan=2, sticky=(N, W, E, S))
        label.grid(column=0, row=0)

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)

        self.root.lift()