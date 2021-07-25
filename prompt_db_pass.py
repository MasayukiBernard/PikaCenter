from tkinter import *
from tkinter import ttk

from alert import Alert

from pg8000.native import Connection
import tools

class PromptDatabasePassword:
    def __init__(self, window_status, password, is_success):
        window_size = {'width': "600", 'height': "100"}

        self.root = Tk()
        self.root.title("Pika Center Invoicing Program - Database Authentication")
        self.root.geometry(tools.generate_tk_geometry(window_size))
        self.root.resizable(False, False)
        self.child_roots = []
        self.root.protocol('WM_DELETE_WINDOW', self.close_window)

        window_status['is_closed'] = False
        self.window_status = window_status
        self.is_success = is_success

        main_frame = ttk.Frame(self.root)

        label = ttk.Label(main_frame, text="INPUT DATABASE PASSWORD", font=("Calibri", "20"))

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

        self.root.lift()
        self.root.mainloop()

    def get_password(self, *args):
        try:
            conn = Connection(user="postgres", password=self.password['inputted'].get(), database="pikacenter")
            conn.run("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";")
            
            self.password['inputted'] = self.password['inputted'].get()
            self.is_success[0] = True
            
            self.root.destroy()
            tools.destroy_roots_recursively(self.child_roots)
        except Exception as e:
            Alert(self.child_roots,'Database is not yet running / Inputted password is not recognized!')

    def close_window(self):
        tools.change_window_status(self.window_status, 'is_closed', True)
        self.root.destroy()

        tools.destroy_roots_recursively(self.child_roots)