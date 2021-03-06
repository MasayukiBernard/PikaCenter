from tkinter import *
from tkinter import ttk
import tools

class LoadingScreen:
    def __init__(self):
        window_size = {'width': "800", 'height': "450"}

        self.root = Tk()

        self.logo_img = PhotoImage(file='resources/images/Pika Center Indonesia Logo 2021 - resized.png')
        self.root.title("Pika Center Invoicing Program - Loading...")
        self.root.iconphoto(False, self.logo_img)
        self.root.geometry(tools.generate_tk_geometry(window_size))
        self.root.resizable(False, False)
        
        # Prevents closing
        self.root.protocol('WM_DELETE_WINDOW', lambda: None)
        label = ttk.Label(self.root, text='Pika Center Invoicing Program', font=("Calibri", "36", "bold"))
        label.grid(column=0, row=0)

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.root.after(1500, lambda: self.root.destroy())

        self.root.mainloop()
        
        
