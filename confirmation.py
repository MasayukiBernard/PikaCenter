from tkinter import messagebox
import tools

class Confirmation:
    def __init__(self, title, message, res_list):
        res_list[0] = messagebox.askyesno(title=title+" Confirmation", message=message)