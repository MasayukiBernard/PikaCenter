from tkinter import messagebox
import tools

class Confirmation:
    def __init__(self, parent_root, title, message, res_list):
        res_list[0] = messagebox.askyesno(parent = parent_root, title=title+" Confirmation", message=message)