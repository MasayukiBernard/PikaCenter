# Windows
from alert import Alert
from inventory import Inventory

# Dependencies
from functools import partial
from tkinter import *
from tkinter import ttk

import tools

class MainNavigation:
    def __init__(self, window_status, db_password):
        self.db_password = db_password
        window_size = {'width': '800', 'height': '450'}
        self.monitor_actual_area = tools.get_monitor_actual_area()

        window_status['main_nav']['is_closed'] = False
        self.windows_status = window_status

        self.root = Tk()
        self.child_roots = []

        self.logo_img = PhotoImage(file='resources/images/Pika Center Indonesia Logo 2021 - resized.png')
        self.root.title("Pika Center Invoicing Program - Main Navigation")
        self.root.iconphoto(False, self.logo_img)
        self.root.geometry(tools.generate_tk_geometry(window_size))
        self.root.protocol('WM_DELETE_WINDOW', self.close_window)
        self.root.resizable(False, False)

        self.main_frame_style = ttk.Style()
        self.main_frame_style.configure('Frames.TFrame', background='#ffee8f')
        self.main_frame = ttk.Frame(self.root, style='Frames.TFrame')
        self.title_label = ttk.Label(self.main_frame, text="PIKA CENTER", font=("Calibri", "26", "bold"), anchor='center', background='#ffee8f')
        
        self.logo_img_container = ttk.Label(self.main_frame, image=self.logo_img, background='#ffee8f')

        self.nav_btns_frame = ttk.Frame(self.main_frame, style='Frames.TFrame')
        self.nav_btns_style = ttk.Style()
        self.nav_btns_style.configure('Navigation.TButton', font='Calibri 20')
        self.nav_btns = {
            'INVENTORY': ttk.Button(self.nav_btns_frame, text="Inventory", style='Navigation.TButton', width=15, command=partial(self.navigate_to, 'inventory')),
            'CUSTOMER': ttk.Button(self.nav_btns_frame, text="Customer", style='Navigation.TButton', width=15, command=partial(self.navigate_to, 'customer')),
            'INVOICING': ttk.Button(self.nav_btns_frame, text="Invoicing", style='Navigation.TButton', width=15, command=partial(self.navigate_to, 'invoice'))
        }

        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        self.main_frame.grid(column=0, row=0, sticky=(N, E, S, W))
        self.title_label.grid(column=0, row=0, sticky= (W, E))
        self.logo_img_container.grid(column=0, row=1)
        self.nav_btns_frame.grid(column=0, row=2, sticky=(N, E, S, W))

        self.nav_btns['INVENTORY'].grid(column=0, row=0, ipady=7)
        self.nav_btns['CUSTOMER'].grid(column=1, row=0, ipady=7)
        self.nav_btns['INVOICING'].grid(column=2, row=0, ipady=7)
        
        self.main_frame.grid_rowconfigure(0, weight=2)
        self.main_frame.grid_rowconfigure(1, weight=3)
        self.main_frame.grid_rowconfigure(2, weight=4)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.nav_btns_frame.grid_rowconfigure(0, weight=1)
        self.nav_btns_frame.grid_columnconfigure(0, weight=1)
        self.nav_btns_frame.grid_columnconfigure(1, weight=1)
        self.nav_btns_frame.grid_columnconfigure(2, weight=1)

        self.root.lift()
        self.root.mainloop()
    
    def close_window(self, *args):
        tools.change_window_status(self.windows_status['main_nav'], 'is_closed', True)
        self.root.destroy()

        # Destroy children roots recursively
        tools.destroy_roots_recursively(self.child_roots)
            
    
    def navigate_to(self, *args):
        entered_key = args[0]
        
        if entered_key == 'inventory':
            Inventory(self.windows_status['inventory'], self.child_roots, db_password=self.db_password)
        else:
            Alert(self.child_roots, "Selected module is currently in development, please select another module!")