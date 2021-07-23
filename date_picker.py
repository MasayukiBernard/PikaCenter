from tkinter import *
from tkinter import ttk
from tkcalendar import Calendar
import tools

class DatePicker:
    def __init__(self, parent_child_roots_list, string_var_ref):
        window_size = {'width': "300", 'height': "250"}

        self.root = Toplevel()
        # self.child_roots = []
        # parent_child_roots_list.append(self.child_roots)
        parent_child_roots_list.append(self.root)
        
        self.root.title("Pika Center Invoicing Program - Date Pickerr")
        self.root.geometry(tools.generate_tk_geometry(window_size))
        self.root.resizable(False, False)

        main_frame = ttk.Frame(self.root)

        string_var_ref.set('')
        calendar = Calendar(main_frame, textvariable=string_var_ref, showweeknumbers=False, showothermonthdays=False, date_pattern='y-mm-dd')
        calendar.bind("<<CalendarSelected>>", self.destroy_window)
        calendar.grid(column=0, row=0)
        
        main_frame.grid(column=0, row=0, sticky=(N, W, E, S))
        calendar.grid(column=0, row=0)

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)

        self.root.lift()
    
    def destroy_window(self, event):
        self.root.destroy()