from tkinter import *
from tkinter import ttk

from win32api import AbortSystemShutdown
import tools

class PromptDatabasePassword:
    def __init__(self, password):
        window_size = {'width': "600", 'height': "100"}

        self.root = Tk()
        self.root.title("Pika Center Invoicing Program - Database Authentication")
        self.root.geometry(tools.generate_tk_geometry(window_size))
        self.root.resizable(False, False)
        self.root.protocol('WM_DELETE_WINDOW', lambda: None)

        main_frame = ttk.Frame(self.root)

        label = ttk.Label(main_frame, text="MASUKKAN KATA SANDI DATABASE", font=("Calibri", "20"), borderwidth=5, relief='groove')

        self.password = password
        self.password['inputted'] = StringVar()
        password_entry = ttk.Entry(main_frame, textvariable=self.password['inputted'], font=("Calibri", "12"), show='*', justify='center')

        main_frame.grid(column=0, row=0, rowspan=2, sticky=(N, W, E, S))
        label.grid(column=0, row=0)
        password_entry.grid(column=0, row=1)

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)

        for child in main_frame.winfo_children(): 
            child.grid_configure(padx=5, pady=5)

        password_entry.focus()

        password_entry.bind("<Return>", self.get_password)

        self.root.mainloop()

    def get_password(self, *args):
        self.password['inputted'] = self.password['inputted'].get()
        self.root.destroy()