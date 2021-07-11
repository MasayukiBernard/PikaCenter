from tkinter import *
from tkinter import ttk
import tools

class Alert:
    def __init__(self, message):
        window_size = {'width': "450", 'height': "50"}

        root = Tk()
        root.title("Pika Center Invoicing Program - Alert")
        root.geometry(tools.generate_tk_geometry(window_size))
        root.resizable(False, False)

        main_frame = ttk.Frame(root)

        label = ttk.Label(main_frame, text=message, foreground='red')
        label.grid(column=0, row=0)
        
        main_frame.grid(column=0, row=0, rowspan=2, sticky=(N, W, E, S))
        label.grid(column=0, row=0)

        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)

        root.mainloop()