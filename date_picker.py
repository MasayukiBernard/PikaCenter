from tkinter import *
from tkinter import ttk
from tkcalendar import Calendar
from datetime import date
import tools

class DatePicker:
    def __init__(self, parent_child_roots_list, selected_str_var, counter_str_var):
        window_size = {'width': "300", 'height': "250"}

        self.root = Toplevel()
        # self.child_roots = []
        # parent_child_roots_list.append(self.child_roots)
        parent_child_roots_list.append(self.root)
        
        self.root.protocol('WM_DELETE_WINDOW', self.clear_string_var)
        self.root.title("Pika Center Invoicing Program - Date Pickerr")
        self.root.geometry(tools.generate_tk_geometry(window_size))
        self.root.resizable(False, False)

        main_frame = ttk.Frame(self.root)

        self.selected_str_var = selected_str_var
        self.counter_str_var = counter_str_var
        self.selected_str_var.set('')
        self.root.after(100)
        self.calendar = Calendar(main_frame, textvariable=self.selected_str_var, showweeknumbers=False, showothermonthdays=False, date_pattern='y-mm-dd')
        self.calendar.bind("<<CalendarSelected>>", self.destroy_window)
        self.calendar.grid(column=0, row=0)
        
        main_frame.grid(column=0, row=0, sticky=(N, W, E, S))
        self.calendar.grid(column=0, row=0)

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)

        self.root.lift()
    
    def clear_string_var(self, *args):
        self.destroy_window(None)
        
    def destroy_window(self, event):
        self.calendar.configure(textvariable=StringVar())
        self.root.destroy()

        curr_string_var_val = self.selected_str_var.get()
        if len(curr_string_var_val) > 0:
            self.selected_str_var.set(date.fromisoformat(curr_string_var_val).strftime('%Y - %b - %d'))
            self.counter_str_var.set('')
            if event is None:
                self.selected_str_var.set('')