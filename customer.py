from functools import partial
from pg8000.native import Connection
from re import A, M, escape
from tkinter import *
from tkinter import ttk

import tools

from manage_customer import ManageCustomer

class Customer:
    def __init__(self, window_status, parent_child_roots_list, db_password):
        # --- Configs
        self.db_password = db_password

        window_size = {'width': '1280', 'height': '700'}
        self.monitor_actual_area = tools.get_monitor_actual_area()

        self.pad_val = 7
        self.frame_width = int(window_size['width']) - (2 * self.pad_val)

        window_status['is_closed'] = False
        self.window_status = window_status

        self.child_windows_status = {
            'manage_customer': {'is_closed': False}
        }
        # --- End of Configs

        # Window and Frames
        self.root = Toplevel()
        self.child_roots = []
        parent_child_roots_list.append(self.child_roots)
        parent_child_roots_list.append(self.root)

        # Window Configs
        self.logo_img = PhotoImage(file='resources/images/Pika Center Indonesia Logo 2021 - resized.png')
        self.root.title("Pika Center Invoicing Program - Customers' Data")
        self.root.iconphoto(False, self.logo_img)
        self.root.geometry(tools.generate_tk_geometry(window_size))
        self.root.protocol('WM_DELETE_WINDOW', self.close_window)
        self.root.resizable(False, False)

        # Main Frame (Main Container)
        self.main_frame = ttk.Frame(self.root, width=self.frame_width)
        self.mf_title_label = ttk.Label(self.main_frame, text="CUSTOMERS' DATA", anchor='center', font=("Calibri", "28", "bold"))

        # Main Tree Search Bar
        self.search_bar_var = StringVar()
        self.placeholder_val = ". . . Search by Name / Email / Phone Number"
        self.search_bar_var.set(self.placeholder_val)
        search_bar_style = ttk.Style()
        search_bar_style.configure('ipadded.TEntry', padding=[self.pad_val, 0, self.pad_val, 0])
        self.search_bar = ttk.Entry(self.main_frame, textvariable=self.search_bar_var, width=48, foreground='#A9A9A9', justify='right', style='ipadded.TEntry')
        # Events Binding
        self.search_bar.bind('<FocusIn>', partial(self.manage_placeholder, 'in', self.search_bar_var, self.placeholder_val))
        self.search_bar.bind('<FocusOut>', partial(self.manage_placeholder, 'out', self.search_bar_var, self.placeholder_val))
        self.search_bar.bind('<KeyRelease>', partial(self.refresh_tree_data, True))

        # Main Tree
        self.tree = ttk.Treeview(self.main_frame, selectmode=BROWSE, show="tree headings", columns=('idx', 'reseller', 'shop', 'pic', 'name', 'phone_number', 'email', 'shipping_address'), height=23)
        self.tree_y_sb = ttk.Scrollbar(self.main_frame, orient=VERTICAL, command=self.tree.yview)
        # Sets scrollbar to tree
        self.tree.configure(yscrollcommand=self.tree_y_sb.set)
        tree_column_config = {
            'index': ('#0', 'idx', 'reseller', 'shop', 'pic', 'name', 'phone_number', 'email', 'shipping_address'),
            'heading_text': ("", "", "Reseller?", "Shop Name", "PIC Name", "Name", "Phone Number", "Email", "Shipping Address"),
            'width': (0, int(self.frame_width * .025), int(self.frame_width * .05), int(self.frame_width * .13), int(self.frame_width * .13), int(self.frame_width * .13), int(self.frame_width * .13), int(self.frame_width * .13), int(self.frame_width*.25)),
            'anchor': ("w", "center", "center", "w", "w", "w", "w", "w", "w"),
        }
        # To set up tree's columns
        # Iterate through index key val assuming all key val in tree_column_config has conforming len
        for i in range(len(tree_column_config['index'])):
            self.tree.column(tree_column_config['index'][i], width=tree_column_config['width'][i], stretch=False, anchor=tree_column_config['anchor'][i])
            self.tree.heading(tree_column_config['index'][i], text=tree_column_config['heading_text'][i])
        # Tree's interaction buttons
        self.tree_btn_frame = ttk.Frame(self.main_frame, width=self.frame_width)
        self.product_tree_btn = {
            'refresh': ttk.Button(self.tree_btn_frame, text="Refresh", command=partial(self.refresh_tree_data, False)),
            'manage_customer': ttk.Button(self.tree_btn_frame, text="MANAGE CUSTOMER", command=partial(self.show_manage_form), width=20)
        }

        # CRUCIAL Code for Treeview Stylizing [Python 3.7]
        self.tree_style = ttk.Style()
        self.tree_style.map("Treeview", foreground=self.fixed_map("foreground"), background=self.fixed_map("background"))

        # Paddings addition to all main frame's children widgets
        for child in self.main_frame.winfo_children():
            child.grid_configure(padx=self.pad_val, pady=(int(self.pad_val*1.5),0))

        # Widgets gridding
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        self.main_frame.grid(column=0, row=0, sticky=(N, W, E, S))
        self.mf_title_label.grid(column=0, columnspan=2, row=0, sticky=(W, E))
        self.search_bar.grid(column=0, row=1, sticky=(E), ipadx=self.pad_val*2)
        self.tree.grid(column=0, row=2, sticky=(W, E))
        self.tree_y_sb.grid(column=1, row=2, sticky=(N, S, E))
        self.tree_btn_frame.grid(column=0, columnspan=2, row=3, sticky=(W,E))
        self.product_tree_btn['refresh'].grid(column=0, row=0, sticky=(W))
        self.product_tree_btn['manage_customer'].grid(column=1, row=0, padx=self.pad_val, sticky=(W))
        
        self.refresh_tree_data(False)
        self.root.lift()
        

    def close_window(self):
        tools.change_window_status(self.window_status, 'is_closed', True)
        self.root.destroy()

        tools.destroy_roots_recursively(self.child_roots)

    def manage_placeholder(self, *args):
        event_type = args[0]
        string_var = args[1]
        default_val = args[2]
        
        if event_type == 'in':
            if string_var.get() == default_val:
                string_var.set('')

        elif event_type == 'out':
            if len(tools.create_pretty_alphanumerical(string_var.get())) == 0:
                string_var.set(default_val)
    
    def fixed_map(self, option):
        return [elm for elm in self.tree_style.map("Treeview", query_opt=option) if elm[:2] != ("!disabled", "!selected")]

    def show_manage_form(self, *args):
        selected_product_keys = self.tree.selection()
        if len(selected_product_keys) == 1:
            selected_product_keys = selected_product_keys[0]
        else:
            selected_product_keys = ""
        
        ManageCustomer(self.child_windows_status, self.child_roots, self.db_password, selected_product_keys)

    def refresh_tree_data(self, *args):
        is_search = args[0]

        # Querying Data
        conn = Connection(user="postgres", password=self.db_password, database="pikacenter")
        added_condition_sql =  ""
        if is_search:
            added_condition = tools.create_pretty_alphanumerical(self.search_bar_var.get())
            added_condition = escape(added_condition)
            added_condition_sql  += 'WHERE (LOWER(name) LIKE LOWER(\'%' + added_condition + '%\') or LOWER(phone_number) LIKE LOWER(\'%' + added_condition + '%\') or LOWER(email) LIKE LOWER(\'%' + added_condition + '%\'))'
        else:
            self.search_bar_var.set(self.placeholder_val)
        fields = ('pkey', 'name', 'phone_number', 'email', 'shipping_address', 'is_reseller', 'shop_name', 'pic_name')
        sql = "SELECT " + ','.join(fields) + " FROM public.customers " +  added_condition_sql + " ORDER BY is_reseller DESC, name ASC;"
        rl = conn.run(sql)

        # Clearing tree's data
        self.tree.delete(*self.tree.get_children())

        # Inserting queried data to tree
        for i in range(len(rl)):
            params_val = {
                'parent': '',
                'index': 'end',
                'iid': str(rl[i][0]),
                'values': tuple([i+1, "Yes" if rl[i][5] else "No", str(rl[i][6]), str(rl[i][7]), str(rl[i][1]), str(rl[i][2]), str(rl[i][3]), str(rl[i][4])])
            }
            self.tree.insert(**params_val)