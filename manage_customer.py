from alert import Alert
from confirmation import Confirmation
from functools import partial
from pg8000.native import Connection
from tkinter import *
from tkinter import ttk

import tools

class ManageCustomer:
    def __init__(self, window_status, parent_child_roots_list, db_password, product_key=""):
        # Configs
        window_status['is_closed'] = False
        self.window_status = window_status
        self.db_password = db_password
        self.pad_val = 7
        window_size = {'width': '800', 'height': '450'}
        self.frame_width = int(window_size['width']) - (3 * self.pad_val)
        self.frame_height = int(window_size['height']) - (2 * self.pad_val)
        
        # Argument value from caller
        self.product_key = product_key
        
        # Main Window
        self.root = Toplevel()
        self.child_roots = []
        parent_child_roots_list.append(self.child_roots)
        parent_child_roots_list.append(self.root)

        # Main window's configs
        self.logo_img = PhotoImage(file='resources/images/Pika Center Indonesia Logo 2021 - resized.png')
        self.root.title("Pika Center Invoicing Program - Manage Customer")
        self.root.iconphoto(False, self.logo_img)
        self.root.geometry(tools.generate_tk_geometry(window_size))
        self.root.protocol('WM_DELETE_WINDOW', self.close_window)
        self.root.resizable(False, False)
        
        # Main Frame
        self.main_frame = ttk.Frame(self.root, width=self.frame_width)
        self.mf_title_label = ttk.Label(self.main_frame, text="MANAGE CUSTOMER", anchor='center', font=("Calibri", "28", "bold"))
        
        # Form Frame
        self.form_frame = ttk.Frame(self.main_frame, width=self.frame_width)
        # Row Frames and It's Widgets
        self.row_keys = tuple(['search_results', 'status', 'is_reseller', 'shop', 'pic', 'name', 'email', 'phone', 'shipping_address'])
        self.row_frames = {
            'search_results': ttk.Frame(self.form_frame),
            'status': ttk.Frame(self.form_frame),
            'is_reseller': ttk.Frame(self.form_frame),
            'shop': ttk.Frame(self.form_frame),
            'pic': ttk.Frame(self.form_frame),
            'name': ttk.Frame(self.form_frame),
            'email': ttk.Frame(self.form_frame),
            'phone': ttk.Frame(self.form_frame),
            'shipping_address': ttk.Frame(self.form_frame),
        }
        self.row_vars = {
            'search_results': StringVar(),
            'is_reseller': StringVar(),
            'shop': StringVar(),
            'pic': StringVar(),
            'name': StringVar(),
            'email': StringVar(),
            'phone': StringVar(),
            'shipping_address': StringVar(),
        }
        # Styles
        (ttk.Style()).configure('search_result.TCombobox', padding=[6,1,1,1])
        (ttk.Style()).configure('manage_customer_default.TEntry', padding=[6,1,16,1])
        self.row_widgets = {
            'search_results':[
                ttk.Label(self.row_frames['search_results'], width=15, text="Search Result", justify='left', font=("Calibri", "14", "bold")),
                ttk.Combobox(self.row_frames['search_results'], width=60, textvariable=self.row_vars['search_results'], font=("Calibri", "14", ""), foreground='#A9A9A9', style='search_result.TCombobox')
            ],
            'status': [
                ttk.Label(self.row_frames['status'], width=15, text="Status", justify='left', font=("Calibri", "14", "bold")),
                ttk.Label(self.row_frames['status'], justify='left', width=62, font=("Calibri", "14", "bold")),
            ],
            'is_reseller': [
                ttk.Label(self.row_frames['is_reseller'], width=15, text="Reseller?", justify='left', font=("Calibri", "14", "bold")),
                ttk.Checkbutton(self.row_frames['is_reseller'], variable=self.row_vars['is_reseller'], command=self.handle_cb_state_change),
            ],
            'shop': [
                ttk.Label(self.row_frames['shop'], width=15, text="Shop Name", justify='left', font=("Calibri", "14", "bold")),
                ttk.Entry(self.row_frames['shop'], textvariable=self.row_vars['shop'], width=60, font=("Calibri", "14", ""), style='manage_customer_default.TEntry')
            ],
            'pic': [
                ttk.Label(self.row_frames['pic'], width=15, text="PIC Name", justify='left', font=("Calibri", "14", "bold")),
                ttk.Entry(self.row_frames['pic'], textvariable=self.row_vars['pic'], width=60, font=("Calibri", "14", ""), style='manage_customer_default.TEntry')
            ],
            'name': [
                ttk.Label(self.row_frames['name'], width=15, text="Customer's Name", justify='left', font=("Calibri", "14", "bold")),
                ttk.Entry(self.row_frames['name'], textvariable=self.row_vars['name'], width=60, font=("Calibri", "14", ""), style='manage_customer_default.TEntry')
            ],
            'email': [
                ttk.Label(self.row_frames['email'], width=15, text="Email", justify='left', font=("Calibri", "14", "bold")),
                ttk.Entry(self.row_frames['email'], textvariable=self.row_vars['email'], width=60, font=("Calibri", "14", ""), style='manage_customer_default.TEntry')
            ],
            'phone': [
                ttk.Label(self.row_frames['phone'], width=15, text="Phone Number", justify='left', font=("Calibri", "14", "bold")),
                ttk.Entry(self.row_frames['phone'], textvariable=self.row_vars['phone'], width=60, font=("Calibri", "14", ""), style='manage_customer_default.TEntry')
            ],
            'shipping_address': [
                ttk.Label(self.row_frames['shipping_address'], width=15, text="Shipping Address", justify='left', font=("Calibri", "14", "bold")),
                ttk.Entry(self.row_frames['shipping_address'], textvariable=self.row_vars['shipping_address'], width=60, font=("Calibri", "14", ""), style='manage_customer_default.TEntry')
            ]
        }
        self.buttons_frame = ttk.Frame(self.form_frame, width=self.frame_width-(self.pad_val*2))
        (ttk.Style()).configure('delete.TButton', background='#FF0F0F', font=("Calibri","12","bold"))
        (ttk.Style()).configure('save.TButton', background='#4CFF4C', font=("Calibri","12","bold"))
        self.button_widgets ={
            'delete': ttk.Button(self.buttons_frame, text="DELETE", command=self.delete_data, width=10, style='delete.TButton'),
            'save': ttk.Button(self.buttons_frame, text="SAVE", command=self.save_data, width=10, style='save.TButton')
        }
        # Events Binding
        self.placeholder_val = "Search by Shop Name / Name / Email / Phone Number"
        self.row_widgets['search_results'][1].bind("<FocusIn>", partial(self.manage_placeholder, 'in', self.row_vars['search_results'], self.placeholder_val))
        self.row_widgets['search_results'][1].bind("<FocusOut>", partial(self.manage_placeholder, 'out', self.row_vars['search_results'], self.placeholder_val))
        self.row_widgets['search_results'][1].bind("<KeyRelease>", self.refresh_search_results)
        self.row_widgets['search_results'][1].bind("<<ComboboxSelected>>", self.fill_form_with_selected_result)
        # Assigning widget's default values
        self.search_results_list = []
        self.selected_result = -1
        self.row_vars['search_results'].set(self.placeholder_val)
        self.row_widgets['status'][1].configure(text=("Add" if self.product_key == "" else "Manage"))
        self.row_vars['is_reseller'].set("1")
        # Widgets gridding
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        
        self.main_frame.grid(column=0, row=0, sticky=(N,W,E,S))
        self.main_frame.grid_rowconfigure(0, weight=2)
        self.main_frame.grid_rowconfigure(1, weight=8)
        self.mf_title_label.grid(column=0, row=0, sticky=(W,E))
        
        self.form_frame.grid(column=0, row=1, sticky=(N,W,E), pady=(self.pad_val*2, 0))
        self.curr_form_row = 0
        for key in self.row_keys:
            self.row_frames[key].grid(column=0, row=self.curr_form_row, sticky=(W,E), padx=(11,11), pady=(self.pad_val*1.25, 0))
            self.row_widgets[key][0].grid(column=0, row=0, sticky=(W))
            self.row_widgets[key][1].grid(column=1, row=0, sticky=(W))
            self.curr_form_row += 1
        self.buttons_frame.grid(column=0, row=self.curr_form_row, sticky=(W,E), pady=(self.pad_val*2, 0))
        self.buttons_frame.grid_columnconfigure(0, weight=1)
        self.buttons_frame.grid_columnconfigure(1, weight=1)
        self.curr_form_row += 1
        self.button_widgets['delete'].grid(column=0, row=0, sticky=(W), padx=(11,0))
        self.button_widgets['save'].grid(column=1, row=0, sticky=(E), padx=(0,11))

        if len(self.product_key) > 0:
            self.load_existing_data()
        
        self.root.lift()

    def close_window(self):
        tools.change_window_status(self.window_status, 'is_closed', True)
        self.root.destroy()

        tools.destroy_roots_recursively(self.child_roots)

    def manage_placeholder(self, *args):
        event_type = args[0]
        string_var = args[1]
        default_val = args[2]
        
        if event_type == 'in' and string_var.get() == default_val:
            string_var.set('')

        elif event_type == 'out':
            if self.selected_result == -1:
                string_var.set(default_val)
    
    def handle_cb_state_change(self, *args):
        reseller_keys = self.row_keys[3:5]
        state = "normal"
        if self.row_vars['is_reseller'].get() == "0":
            state = "disabled"

        for key in reseller_keys:
            self.row_widgets[key][1].configure(state=state)
            self.row_vars[key].set("")
            
    def load_existing_data(self, *args):
        conn = Connection(user="postgres", password=self.db_password, database="pikacenter")
        db_fields = ('pkey', 'is_reseller', 'shop_name', 'pic_name', 'name', 'email', 'phone_number', 'shipping_address')
        
        sql = "SELECT "+','.join(db_fields)+" FROM public.customers WHERE pkey = :cust_pkey;"
        rl = conn.run(sql, cust_pkey=self.product_key)
        
        if len(rl) == 1:
            rl = rl[0]
            self.row_vars['is_reseller'].set(1 if rl[1] else 0)
            self.handle_cb_state_change()
            start_i = 2
            for key in self.row_keys[3:]:
                self.row_vars[key].set(str(rl[start_i]))
                start_i += 1

            

    def refresh_search_results(self, *args):
        conn = Connection(user="postgres", password=self.db_password, database="pikacenter")
        
        inputted_str = tools.create_db_input_string(self.row_vars['search_results'].get())
        if len(inputted_str) > 0:
            db_fields = ('pkey', 'shop_name', 'name', 'email', 'phone_number')
            sql = "SELECT "+','.join(db_fields)+" FROM public.customers WHERE (LOWER(shop_name) LIKE LOWER(\'%"+inputted_str+"%\') or LOWER(name) LIKE LOWER(\'%"+inputted_str+"%\') or LOWER(email) LIKE LOWER(\'%"+inputted_str+"%\') or LOWER(phone_number) LIKE LOWER(\'%"+inputted_str+"%\'));"
            
            rl = conn.run(sql, first=inputted_str, second=inputted_str, third=inputted_str, fourth=inputted_str)
            if len(rl) > 0:
                self.search_results_list = rl
                self.row_widgets['search_results'][1]['values'] = tuple([str(rl[i][1])+" - "+str(rl[i][2])+" - "+str(rl[i][3])+" - "+str(rl[i][4]) for i in range(len(rl))])
                return

            # Clear up combobox list of selections
            self.search_results_list = []
            self.selected_result = -1
            self.row_widgets['search_results'][1]['values'] = tuple()
            self.product_key = ""

            self.row_widgets['status'][1].configure(text="Add")
            # Return all entries to normal state, clear entry
            for key in self.row_keys:
                if key != 'search_results' and key != 'status':
                    self.row_vars[key].set("")
            self.row_vars['is_reseller'].set("1")
            self.handle_cb_state_change()

    def fill_form_with_selected_result(self, *args):
        self.selected_result = self.row_widgets['search_results'][1].current()
        self.search_results_list = [self.search_results_list[self.selected_result]]
        selected_rl = self.search_results_list[0]
        self.row_widgets['search_results'][1]['values'] = tuple([str(selected_rl[1])+" - "+str(selected_rl[2])+" - "+str(selected_rl[3])+" - "+str(selected_rl[4])])
        self.product_key = selected_rl[0]
        self.row_widgets['status'][1].configure(text="Manage")

        self.load_existing_data()
    
    def delete_data (self, *args):        
        conn = Connection(user="postgres", password=self.db_password, database="pikacenter")
        sql = "SELECT pkey FROM public.customers WHERE pkey = :cust_pkey;"
        rl = conn.run(sql, cust_pkey=self.product_key)
        if len(rl) == 0:
            Alert(self.child_roots, 'Form validation failed; Referred customer non-existent!')
        else:
            res_list = [None]
            Confirmation(self.root, "Delete Customer", "Delete this customer's data?", res_list=res_list)
            confirmed = res_list[0]
            
            if confirmed:
                conn.run("START TRANSACTION")
                conn.run("DELETE FROM public.customers WHERE pkey = :cust_pkey;", cust_pkey=self.product_key)
                conn.run("COMMIT")
                
                # CASCADE customer deletion to related invoices

                self.root.after(1)
                self.close_window()
    
    def validate_form(self):
        default_msg = " cannot be empty"
        error_msges = []
        if self.row_vars['is_reseller'].get() == "1":
            if len(self.row_vars['shop'].get()) == 0:
                error_msges.append("Shop name" + default_msg)
            if len(self.row_vars['pic'].get()) == 0:
                error_msges.append("PIC name" + default_msg)
            
        if len(self.row_vars['name'].get()) == 0:
            error_msges.append("Customer's name" + default_msg)

        
        return (True if len(error_msges) == 0 else False), ('\n'.join(error_msges) if len(error_msges) > 0 else '')

    def save_data(self, *args):
        form_is_valid, error_msges = self.validate_form()
        if not form_is_valid:
            Alert(self.child_roots, "Form validation failed\n" + error_msges)
            return

        res_list = [None]
        Confirmation(self.root, "Add Customer", "Save this new customer's data?", res_list=res_list)
        confirmed = res_list[0]
        
        if confirmed:
            conn = Connection(user="postgres", password=self.db_password, database="pikacenter")
            ins_val_dict ={
                'pkey': conn.run("SELECT uuid_generate_v1();")[0][0],
                'is_reseller': True if self.row_vars['is_reseller'].get() == "1" else False
            }
            for key in self.row_keys[3:]:
                ins_val_dict[key] = self.row_vars[key].get()
            conn.run("START TRANSACTION")
            sql = "INSERT INTO public.customers (pkey,is_reseller,shop_name,pic_name,name,email,phone_number,shipping_address) VALUES (:pkey,:is_reseller,:shop,:pic,:name,:email,:phone,:shipping_address);"
            conn.run(sql, **ins_val_dict)
            conn.run("COMMIT")

            self.root.after(1)
            self.close_window()
                
        

