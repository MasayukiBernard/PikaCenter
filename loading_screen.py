from tkinter import *
from tkinter import ttk
import time
import tools

class LoadingScreen:
    def __init__(self):
        root = Tk()
        root.title('Pika Center Invoicing Program')
        
        window_size = {'width': '800', 'height': '450'}
        root.geometry(window_size['width'] + "x" + window_size['height'] + tools.calculate_unused_screen_area(window_size))
        root.resizable(False, False)
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        # Prevents closing
        root.protocol('WM_DELETE_WINDOW', lambda: None)
        # root.attributes('-fullscreen', True)
        label = ttk.Label(root, text='Pika Center Invoicing Program', font=("Calibri", "36", "bold  "))
        label.grid(column=0, row=0)
    
        root.after(2250, lambda: root.destroy())
        root.mainloop()

LoadingScreen()
