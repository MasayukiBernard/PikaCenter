from tkinter import *
from tkinter import ttk

from functools import partial
from pg8000.native import Connection
import re
import tools

from alert import Alert
from confirmation import Confirmation
from date_picker import DatePicker

class ManageProduct:
    def __init__(self, window_status, parent_child_roots_list, db_password, action_type, product_key=""):
        self.db_password = db_password
        window_size = {'width': '800', 'height': '450'}
        self.monitor_actual_area = tools.get_monitor_actual_area()
        self.pad_val = 7
        self.frame_width = int(window_size['width']) - (3 * self.pad_val)
        self.frame_height = int(window_size['height']) - (2 * self.pad_val)

        window_status['is_closed'] = False
        self.window_status = window_status
        self.action_type = action_type
        self.action_type_str = action_type[0].upper() + action_type[1:]
        self.product_key = product_key

        self.root = Toplevel()
        self.child_roots = []
        parent_child_roots_list.append(self.child_roots)
        parent_child_roots_list.append(self.root)

        self.root.title("Pika Center Invoicing Program - Manage " + self.action_type_str + " Products")
        self.root.geometry(tools.generate_tk_geometry(window_size))
        self.root.protocol('WM_DELETE_WINDOW', self.close_window)
        self.root.resizable(False, False)

        self.canvas_frame = ttk.Frame(self.root)
        self.canvas = Canvas(self.canvas_frame, width=self.frame_width, height=self.frame_height, bd=0, highlightthickness=0, relief='ridge')
        self.canvas_sb = ttk.Scrollbar(self.canvas_frame, orient=VERTICAL, command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.canvas_sb.set)
        self.canvas.bind('<Configure>', lambda event: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.main_frame = ttk.Frame(self.canvas)
        
        self.title_label = ttk.Label(self.main_frame, text= self.action_type_str + " Product Form", font=("Calibri", "28", "bold"))
        
        self.window_height = self.frame_height + 4000
        self.window_id = self.canvas.create_window((0,0), window=self.main_frame, anchor="nw", width=self.frame_width, height=self.window_height)

        self.form_vars = {
            'result': StringVar(),
            'result_list': [],
            'selected_result': -1,
            'sku': StringVar(),
            'name': StringVar(),
            'description': StringVar()
        }
        self.form_frame = ttk.Frame(self.main_frame, width=self.frame_width)
        self.form_row_frame = {
            'result': ttk.Frame(self.form_frame, width=self.frame_width),
            'status': ttk.Frame(self.form_frame, width=self.frame_width),
            'sku': ttk.Frame(self.form_frame, width=self.frame_width),
            'name': ttk.Frame(self.form_frame, width=self.frame_width),
            'description': ttk.Frame(self.form_frame, width=self.frame_width),
        }
        self.form_row_col_frame = {
            'label':{
                'result': ttk.Frame(self.form_row_frame['result']),
                'status': ttk.Frame(self.form_row_frame['status']),
                'sku': ttk.Frame(self.form_row_frame['sku']),
                'name': ttk.Frame(self.form_row_frame['name']),
                'description': ttk.Frame(self.form_row_frame['description'])
            },
            'entry':{
                'result': ttk.Frame(self.form_row_frame['result']),
                'status': ttk.Frame(self.form_row_frame['status']),
                'sku': ttk.Frame(self.form_row_frame['sku']),
                'name': ttk.Frame(self.form_row_frame['name']),
                'description': ttk.Frame(self.form_row_frame['description'])
            },
        }

        (ttk.Style()).configure('result.TCombobox', padding=[6,1,1,1])
        (ttk.Style()).configure('manage_product.TEntry', padding=[6,1,16,1])
        self.form_widgets = {
            'label': {
                'result': ttk.Label(self.form_row_col_frame['label']['result'], text="Search Result", justify='left', font=("Calibri", "14", "bold")),
                'status': ttk.Label(self.form_row_col_frame['label']['status'], text="Status", justify='left', font=("Calibri", "14", "bold")),
                'sku': ttk.Label(self.form_row_col_frame['label']['sku'], text="SKU", justify='left', font=("Calibri", "14", "bold")),
                'name': ttk.Label(self.form_row_col_frame['label']['name'], text="Name", justify='left', font=("Calibri", "14", "bold")),
                'description': ttk.Label(self.form_row_col_frame['label']['description'], text="Description", justify='left', font=("Calibri", "14", "bold"))
            },
            'entry': {
                'result': ttk.Combobox(self.form_row_col_frame['entry']['result'], width=60, textvariable=self.form_vars['result'], font=("Calibri", "14", ""), foreground='#A9A9A9', style='result.TCombobox'),
                'status': ttk.Label(self.form_row_col_frame['entry']['status'], justify='left', width=62, font=("Calibri", "14", "bold")),
                'sku': ttk.Entry(self.form_row_col_frame['entry']['sku'], textvariable=self.form_vars['sku'], width=60, font=("Calibri", "14", ""), style='manage_product.TEntry'),
                'name': ttk.Entry(self.form_row_col_frame['entry']['name'], textvariable=self.form_vars['name'], width=60, font=("Calibri", "14", ""), style='manage_product.TEntry'),
                'description': ttk.Entry(self.form_row_col_frame['entry']['description'], textvariable=self.form_vars['description'], width=60, font=("Calibri", "14", ""), style='manage_product.TEntry'),
            }
        }
        self.placeholder_val = "Search by Name / Description. . ."
        self.form_vars['result'].set(self.placeholder_val)
        self.form_widgets['entry']['result'].bind("<FocusIn>", partial(self.manage_placeholder, 'in', self.form_vars['result'], self.placeholder_val))
        self.form_widgets['entry']['result'].bind("<FocusOut>", partial(self.manage_placeholder, 'out', self.form_vars['result'], self.placeholder_val))
        self.form_widgets['entry']['result'].bind("<KeyRelease>", self.refresh_result_list)
        self.form_widgets['entry']['result'].bind("<<ComboboxSelected>>", self.apply_result_selection)
        
        status_str = "Manage"
        if self.action_type == 'arrived' and len(self.product_key) == 0:
            status_str = "Add"
        self.form_widgets['entry']['status'].configure(text=status_str)

        if status_str == "Manage":
            self.form_widgets['entry']['sku'].configure(state='disabled') 
            self.form_widgets['entry']['name'].configure(state='disabled')
            self.form_widgets['entry']['description'].configure(state='disabled')

        self.form_widgets['entry']['sku'].bind("<FocusOut>", partial(self.correct_alphanumerical_entry, 'main', 'sku'))
        self.form_widgets['entry']['name'].bind("<FocusOut>", partial(self.correct_alphanumerical_entry, 'main', 'name'))
        self.form_widgets['entry']['description'].bind("<FocusOut>", partial(self.correct_alphanumerical_entry, 'main', 'description'))

        
        self.detail_widgets_keys = ['entry_date', 'eta', 'qty', 'buyprice']
        self.heading_texts = ["Entry Date", "ETA", "Qty", "Buy Price"]
        self.form_detail_vars = {}
        if self.action_type == 'sold':
            self.detail_widgets_keys = ['temp_invoice_id', 'sold_date', 'qty', 'sellprice', 'sales_type']
            self.heading_texts = ["Invoice ID", "Sold Date", "Qty", "Sell Price", "Sales Type"]
            conn = Connection(user="postgres", password=self.db_password, database="pikacenter")
            stc_rl = conn.run("SELECT * FROM public.sales_types ORDER BY pkey ASC;")
            self.form_detail_vars['sales_type_choices'] = tuple([stc_rl[j][1] for j in range(len(stc_rl))])
        for key in self.detail_widgets_keys:
            self.form_detail_vars[key] = []

        self.form_detail_widgets = {}
        self.form_detail_widgets['frame'] = {
            'title': ttk.Frame(self.form_frame, width=self.frame_width),
            'heading': {'base': ttk.Frame(self.form_frame)},
            'entry': [],
            'btns_row': ttk.Frame(self.form_frame)
        }

        self.detail_widgets_keys.append('del_btn')
        self.heading_texts.append('DELETE')
        self.form_detail_widgets['frame']['heading']['column'] = {}
        self.form_detail_widgets['label'] = {
            'title': ttk.Label(self.form_detail_widgets['frame']['title'], text=("Arrived" if self.action_type == 'arrived' else "Sold") + " Log", font=("Calibri", "12", "bold"))
        }
        self.form_detail_widgets['label']['heading'] = {}
        self.form_detail_widgets['entry'] = {}
        for i in range(len(self.detail_widgets_keys)):
            self.form_detail_widgets['frame']['heading']['column'][self.detail_widgets_keys[i]] = ttk.Frame(self.form_detail_widgets['frame']['heading']['base'])
            self.form_detail_widgets['label']['heading'][self.detail_widgets_keys[i]] = ttk.Label(self.form_detail_widgets['frame']['heading']['column'][self.detail_widgets_keys[i]], text=self.heading_texts[i])
            self.form_detail_widgets['entry'][self.detail_widgets_keys[i]] = []
        # self.form_detail_widgets['frame']['heading']['column'] = {
        #     'entry_date': ttk.Frame(self.form_detail_widgets['frame']['heading']['base']),
        #     'eta': ttk.Frame(self.form_detail_widgets['frame']['heading']['base']),
        #     'qty': ttk.Frame(self.form_detail_widgets['frame']['heading']['base']),
        #     'buyprice': ttk.Frame(self.form_detail_widgets['frame']['heading']['base']),
        # }
        # if self.action_type == 'sold':
        #     self.form_detail_widgets['frame']['heading']['column'] = {
        #         'sold_date': ttk.Frame(self.form_detail_widgets['frame']['heading']['base']),
        #         'qty': ttk.Frame(self.form_detail_widgets['frame']['heading']['base']),
        #         'sellprice': ttk.Frame(self.form_detail_widgets['frame']['heading']['base']),
        #         'sales_type': ttk.Frame(self.form_detail_widgets['frame']['heading']['base']),
        #         'temp_invoice_id': ttk.Frame(self.form_detail_widgets['frame']['heading']['base']),
        #     }
        # self.form_detail_widgets['label']['heading'] = {
        #     'entry_date': ttk.Label(self.form_detail_widgets['frame']['heading']['column']['sku'], text="Entry Date"),
        #     'eta': ttk.Label(self.form_detail_widgets['frame']['heading']['column']['temp_invoice_id'], text="ETA"),
        #     'qty': ttk.Label(self.form_detail_widgets['frame']['heading']['column']['buyprice'], text="Qty"),
        #     'buyprice': ttk.Label(self.form_detail_widgets['frame']['heading']['column']['sellprice'], text="Buy Price")
        # }
        # if self.action_type == 'sold':
        #     self.form_detail_widgets['label']['heading'] = {
        #         'sold_date': ttk.Label(self.form_detail_widgets['frame']['heading']['column']['sku'], text="Sold Date"),
        #         'qty': ttk.Label(self.form_detail_widgets['frame']['heading']['column']['buyprice'], text="Qty"),
        #         'sellprice': ttk.Label(self.form_detail_widgets['frame']['heading']['column']['temp_invoice_id'], text="Sell Price"),
        #         'sales_type': ttk.Label(self.form_detail_widgets['frame']['heading']['column']['sellprice'], text="Sales Type"),
        #         'temp_invoice_id': ttk.Label(self.form_detail_widgets['frame']['heading']['column']['sellprice'], text="Invoice ID")
        #     }

        # self.form_detail_widgets['entry'] = {
        #     'sku': [],
        #     'temp_invoice_id': [],
        #     'buyprice': [],
        #     'sellprice': []
        # }

        self.form_detail_widgets['del_btn'] = []
        self.form_detail_widgets['add_row_btn'] = ttk.Button(self.form_detail_widgets['frame']['btns_row'], text='Tambah', command=self.add_new_row, width=10)
        self.form_detail_widgets['save_btn'] = ttk.Button(self.form_detail_widgets['frame']['btns_row'], text='SIMPAN', command=self.save_product, width=10)
        

        self.canvas_frame.grid(column=0, row=0, sticky=(N, E, S, W))
        self.canvas.grid(column=0, row=0, sticky=(N, E, S, W))
        self.canvas_sb.grid(column=1, row=0, sticky=(N,S,E))
        
        self.title_label.grid(column=0, row=0, pady=self.pad_val*2)

        self.form_frame.grid(column=0, row=1, sticky=(N, W, E, S))

        self.current_row_idx = 0
        for key, val in self.form_row_frame.items():
            self.form_row_frame[key].grid(column=0, row=self.current_row_idx, sticky=(W,E))
            self.form_row_col_frame['label'][key].grid(column=0, row=0, sticky=(W))
            self.form_widgets['label'][key].grid(column=0, row=0, padx=(self.pad_val*2, 0))
            self.form_row_col_frame['entry'][key].grid(column=1, row=0, sticky=(E))
            self.form_widgets['entry'][key].grid(column=1, row=0, padx=(0, self.pad_val*2))

            self.current_row_idx +=1
        
        if self.action_type == 'sold':
            self.form_widgets['label']['status'].grid_remove()
            self.form_widgets['entry']['status'].grid_remove()
            self.form_row_col_frame['label']['status'].grid_remove()
            self.form_row_col_frame['entry']['status'].grid_remove()
            self.form_row_frame['status'].grid_remove()

        self.form_detail_widgets['frame']['title'].grid(column=0, row=self.current_row_idx)
        self.form_detail_widgets['label']['title'].grid(column=0, row=0)
        
        self.form_detail_widgets['frame']['heading']['base'].grid(column=0, row=self.current_row_idx+1, sticky=(W, E))
        self.current_row_idx += 2
        detail_col_idx = 0
        for key in self.detail_widgets_keys:
            self.form_detail_widgets['frame']['heading']['column'][key].grid(column=detail_col_idx, row=self.current_row_idx, sticky=(W, E))
            self.form_detail_widgets['label']['heading'][key].grid(column=0, row=0)
            detail_col_idx +=1

        self.form_detail_widgets['frame']['btns_row'].grid(column=0, row=self.current_row_idx, sticky=(W))
        self.form_detail_widgets['add_row_btn'].grid(column=0, row=0, sticky=(W), padx=(self.pad_val+2, 0))
        self.form_detail_widgets['save_btn'].grid(column=1, row=0, sticky=(W), padx=(self.pad_val, 0))
        self.current_row_idx += 1

        # self.form_detail_widgets['frame']['heading']['column']['sku'].grid(column=0, row=0, sticky=(W, E))
        # self.form_detail_widgets['frame']['heading']['column']['temp_invoice_id'].grid(column=1, row=0, sticky=(W, E))
        # self.form_detail_widgets['frame']['heading']['column']['buyprice'].grid(column=2, row=0, sticky=(W, E))
        # self.form_detail_widgets['frame']['heading']['column']['sellprice'].grid(column=3, row=0, sticky=(W, E))
        # self.form_detail_widgets['frame']['heading']['column']['del_btn'].grid(column=4, row=0, sticky=(W, E))

        # self.form_detail_widgets['label']['title'].grid(column=0, row=0)
        # self.form_detail_widgets['label']['heading']['sku'].grid(column=0, row=0)
        # self.form_detail_widgets['label']['heading']['temp_invoice_id'].grid(column=0, row=0)
        # self.form_detail_widgets['label']['heading']['buyprice'].grid(column=0, row=0)
        # self.form_detail_widgets['label']['heading']['sellprice'].grid(column=0, row=0)
        # self.form_detail_widgets['label']['heading']['del_btn'].grid(column=0, row=0)

        for child in self.form_frame.winfo_children():
            child.grid_configure(pady=(0, self.pad_val))
        
        self.root.grid_columnconfigure(0, weight=1)

        self.canvas_frame.grid_columnconfigure(0, weight=10)
        self.canvas_frame.grid_columnconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.form_frame.grid_columnconfigure(0, weight=1)

        for key, row_frame in self.form_row_frame.items():
            row_frame.grid_columnconfigure(0, weight=2)
            row_frame.grid_columnconfigure(1, weight=8)
        
        for key, label in self.form_widgets['label'].items():
            label.grid_columnconfigure(0, weight=1)
        for key, entry in self.form_widgets['entry'].items():
            entry.grid_columnconfigure(0, weight=1)

        self.form_detail_widgets['frame']['title'].grid_columnconfigure(0, weight=1)

        self.base_weights = [3,3,4,7,1]
        if self.action_type == 'sold':
            self.base_weights = [3,2,2,3,4,1]
        
        for i in range(len(self.detail_widgets_keys)):
            self.form_detail_widgets['frame']['heading']['base'].grid_columnconfigure(i, weight=self.base_weights[i])
            self.form_detail_widgets['frame']['heading']['column'][self.detail_widgets_keys[i]].grid_columnconfigure(0, weight=1)

        # self.form_detail_widgets['frame']['heading']['base'].grid_columnconfigure(0, weight=8)
        # self.form_detail_widgets['frame']['heading']['base'].grid_columnconfigure(1, weight=10) 
        # self.form_detail_widgets['frame']['heading']['base'].grid_columnconfigure(2, weight=9)
        # self.form_detail_widgets['frame']['heading']['base'].grid_columnconfigure(3, weight=8)
        # self.form_detail_widgets['frame']['heading']['base'].grid_columnconfigure(4, weight=1)
        # self.form_detail_widgets['frame']['heading']['column']['sku'].grid_columnconfigure(0, weight=1)
        # self.form_detail_widgets['frame']['heading']['column']['temp_invoice_id'].grid_columnconfigure(0, weight=1)
        # self.form_detail_widgets['frame']['heading']['column']['buyprice'].grid_columnconfigure(0, weight=1)
        # self.form_detail_widgets['frame']['heading']['column']['sellprice'].grid_columnconfigure(0, weight=1)
        # self.form_detail_widgets['frame']['heading']['column']['del_btn'].grid_columnconfigure(0, weight=1)
        self.form_detail_widgets['frame']['btns_row'].grid_columnconfigure(0, weight=1)
        self.form_detail_widgets['frame']['btns_row'].grid_columnconfigure(1, weight=1)
        
        if len(self.product_key) > 0:
            self.load_existing_data()
        
        self.root.lift()
    
    def close_window(self, *args):
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
            if self.form_vars['selected_result'] == -1:
                    string_var.set(default_val)

    def refresh_result_list(self, *args):       
        conn = Connection(user="postgres", password=self.db_password, database="pikacenter")
        
        typed_value = re.escape(tools.create_pretty_alphanumerical(self.form_vars['result'].get()))
        if len(typed_value) > 0:
            sql = 'SELECT * FROM public.products WHERE (LOWER(name) LIKE LOWER(\'%' + typed_value + '%\') or LOWER(description) LIKE LOWER(\'%' + typed_value + '%\')) ORDER BY sku, name ASC;' 
            rl = conn.run(sql)
            self.form_vars['result_list'] = rl
            if len(self.form_vars['result_list']) > 0:
                self.form_widgets['entry']['result']['values'] = tuple([("["+str(row_val[3])+"] - "+str(row_val[1])) for row_val in self.form_vars['result_list']])
                return
        
        self.form_vars['result_list'] = []
        self.form_vars['selected_result'] = -1
        self.form_widgets['entry']['result']['values'] = tuple()
        self.form_widgets['entry']['status'].configure(text='Add')
        self.form_widgets['entry']['sku'].configure(state='normal') 
        self.form_widgets['entry']['name'].configure(state='normal')
        self.form_widgets['entry']['description'].configure(state='normal')
        # Clear Form

        form_vars_keys = ['sku', 'name', 'description']
        for i in range(len(form_vars_keys)):
            self.form_vars[form_vars_keys[i]].set('')
            

    def apply_result_selection(self, *args):
        self.form_vars['selected_result'] = self.form_widgets['entry']['result'].current()
        self.form_vars['result_list'] = [self.form_vars['result_list'][self.form_vars['selected_result']]]
        row_val = self.form_vars['result_list'][0]
        self.form_widgets['entry']['result']['values'] = tuple(["["+str(row_val[3])+"] - "+str(row_val[1])])
        self.form_widgets['entry']['status'].configure(text='Manage')

        self.form_widgets['entry']['sku'].configure(state='disabled') 
        self.form_widgets['entry']['name'].configure(state='disabled')
        self.form_widgets['entry']['description'].configure(state='disabled')
        
        # Updates Existing Form Data
        self.product_key = str(row_val[0])
        self.load_existing_data()

    def correct_alphanumerical_entry(self, *args):
        type = args[0]
        key = args[1]
        if type == 'detail':
            selected_entry_idx = args[2]

        if type == 'detail':
            entered_str = self.form_detail_vars[key][selected_entry_idx].get()
            if len(entered_str) > 0:
                res_str = ''
                res_str = tools.create_pretty_alphanumerical(entered_str)
                if len(res_str) > 0:
                    self.form_detail_vars[key][selected_entry_idx].set(res_str)
                else:
                    self.form_detail_vars[key][selected_entry_idx].set('')
        elif type == 'main':
            entered_str = self.form_vars[key].get()
            if len(entered_str) > 0:
                res_str = ''
                res_str = tools.create_pretty_alphanumerical(entered_str)
                if len(res_str) > 0:
                    self.form_vars[key].set(res_str)
                else:
                    self.form_vars[key].set('')
                

    def correct_numeric_entry(self, *args):
        key = args[0]
        selected_entry_idx = args[1]
        entered_str = self.form_detail_vars[key][selected_entry_idx].get()
        if len(entered_str) > 0:
            res_str = ''
            res_str = tools.remove_non_integer(entered_str)
            if len(res_str) > 0:
                res_str = tools.create_pretty_numerical(int(res_str))
                self.form_detail_vars[key][selected_entry_idx].set(res_str)
            else:
                self.form_detail_vars[key][selected_entry_idx].set('')
    
    def fill_empty_entry(self, *args):
        key = args[0]
        selected_entry_idx = args[1]
        entered_str = self.form_detail_vars[key][selected_entry_idx].get()

        if len(entered_str) == 0:
            self.form_detail_vars[key][selected_entry_idx].set('0')
            
    def load_existing_data(self):
        conn = Connection(user="postgres", password=self.db_password, database="pikacenter")

        query_sql = "SELECT * FROM public.products WHERE pkey = :product_key;"
        rl = conn.run(query_sql, product_key=self.product_key)

        additional_columns = "entry_date,eta,qty,buyprice"
        tables = "public.arrived_products_log"
        order_bys = "entry_date DESC, eta DESC"

        if self.action_type == 'sold':
            additional_columns = "sold_date,qty,sellprice,refsalestypekey,temp_invoice_id"
            tables = "public.sold_products_log"
            order_bys = "sold_date DESC"
            
        detail_query_sql = "SELECT pkey," + additional_columns+ " FROM " + tables + " WHERE refproductkey = :product_key ORDER BY " + order_bys + ";"
        detail_rl = conn.run(detail_query_sql, product_key=self.product_key)
        
        if len(rl) == 1:
            form_vars_keys = ['sku', 'name', 'description']
            form_vars_values = [str(rl[0][3]), str(rl[0][1]), str(rl[0][2])]
            for i in range(len(form_vars_keys)):
                self.form_vars[form_vars_keys[i]].set(form_vars_values[i])

            self.form_vars['selected_result'] = self.form_widgets['entry']['result'].current()
            self.form_vars['result_list'] = rl
            self.form_widgets['entry']['result']['values'] = tuple(["["+str(form_vars_values[0])+"] - "+str(form_vars_values[1])])
            self.form_widgets['entry']['result'].current(0)

            if len(detail_rl) > 0:
                for i in range(len(detail_rl)):
                    detail_data = {}
                    if self.action_type == 'arrived':
                        detail_data['entry_date'] = detail_rl[i][1]
                        detail_data['eta'] = detail_rl[i][2]
                        detail_data['qty'] = detail_rl[i][3]
                        detail_data['buyprice'] = detail_rl[i][4]
                    elif self.action_type == 'sold':
                        detail_data['sold_date'] = detail_rl[i][1]
                        detail_data['qty'] = detail_rl[i][2]
                        detail_data['sellprice'] = detail_rl[i][3]
                        detail_data['refsalestypekey'] = detail_rl[i][4]
                        detail_data['temp_invoice_id'] = detail_rl[i][5]
                    # self.add_new_row(detail_data)

    def show_date_picker(self, *args):
        DatePicker(self.child_roots, args[0])

    def add_new_row(self, *args):
        current_len = len(self.form_detail_widgets['del_btn'])
        data = {'entry_date': "", 'eta': "", 'qty': "0", 'buyprice': "0"}
        if self.action_type == 'sold':
            data = {'sold_date': "", 'qty': "0", 'sellprice': "0", 'sales_type': "", 'temp_invoice_id': ""}
        
        if len(args) > 0:
            data = args[0]

        self.form_detail_widgets['frame']['entry'].append(ttk.Frame(self.form_frame))

        for i in range(len(self.detail_widgets_keys)):
            if self.detail_widgets_keys[i] != 'del_btn':
                self.form_detail_vars[self.detail_widgets_keys[i]].append(StringVar())

            widget = None
            if self.detail_widgets_keys[i] == 'entry_date' or  self.detail_widgets_keys[i] == 'sold_date' or  self.detail_widgets_keys[i] == 'eta':
                # Pop-up a new window for pickingdate
                # Append window to child windows list
                widget = ttk.Entry(self.form_detail_widgets['frame']['entry'][current_len], state='disabled', justify='center', textvariable=self.form_detail_vars[self.detail_widgets_keys[i]][current_len], width=21)
                widget.bind("<ButtonPress-1>", partial(self.show_date_picker, self.form_detail_vars[self.detail_widgets_keys[i]][current_len]))
            elif self.detail_widgets_keys[i] == 'sales_type':
                widget = ttk.Combobox(self.form_detail_widgets['frame']['entry'][current_len], justify='center')
                widget['values'] = self.form_detail_vars['sales_type_choices']
            elif self.detail_widgets_keys[i] == 'del_btn':
                widget = ttk.Button(self.form_detail_widgets['frame']['entry'][current_len], text='X',width=3, command=partial(self.delete_row, current_len))
            else:
                widget = ttk.Entry(self.form_detail_widgets['frame']['entry'][current_len], justify='center', textvariable=self.form_detail_vars[self.detail_widgets_keys[i]][current_len], width=24)

                if self.detail_widgets_keys[i] == 'buyprice':
                    widget.configure(width=42)
                if self.detail_widgets_keys[i] == 'qty':
                    widget.configure(width=9)

                if self.detail_widgets_keys[i] == 'buyprice' or self.detail_widgets_keys[i] == 'sellprice' or self.detail_widgets_keys[i] == 'qty':
                    temp_price_val = data[self.detail_widgets_keys[i]]
                    if temp_price_val != "0" and type(temp_price_val) is not str:
                        data[self.detail_widgets_keys[i]] = tools.create_pretty_numerical(temp_price_val)
                    widget.bind("<KeyRelease>", partial(self.correct_numeric_entry, self.detail_widgets_keys[i], current_len))
                    widget.bind("<FocusOut>", partial(self.fill_empty_entry, self.detail_widgets_keys[i], current_len))
                else:
                    # Widget only contains string
                    widget.configure(width=18)
                    widget.bind("<FocusOut>", partial(self.correct_alphanumerical_entry, 'detail', self.detail_widgets_keys[i], current_len))
            
            if self.detail_widgets_keys[i] != 'del_btn':
                self.form_detail_widgets['entry'][self.detail_widgets_keys[i]].append(widget)
                self.form_detail_vars[self.detail_widgets_keys[i]][current_len].set(data[self.detail_widgets_keys[i]])
            else:
                self.form_detail_widgets['del_btn'].append(widget)


        self.form_detail_widgets['frame']['entry'][current_len].grid(column=0, row=self.current_row_idx, sticky=(W, E))
        self.current_row_idx += 1

        padxs = [[self.pad_val*2-3,0],[0,0],[0,0],[0,0],[0,self.pad_val*5]]
        if self.action_type == 'sold':
            padxs = [[self.pad_val*2-3,0],[0,0],[0,0],[0,0],[self.pad_val*2-3,0]]

        column_idx = 0
        for key in self.detail_widgets_keys:
            if key != 'del_btn':
                self.form_detail_widgets['entry'][self.detail_widgets_keys[column_idx]][current_len].grid(column=column_idx, row=0, sticky=(W), padx=(padxs[column_idx][0], padxs[column_idx][1]))
            column_idx +=1
        self.form_detail_widgets['del_btn'][current_len].grid(column=column_idx, row=0, sticky=(W), padx=(0, self.pad_val*2-3))

        self.form_detail_widgets['frame']['btns_row'].grid(column=0, row=self.current_row_idx, sticky=(W))
        self.form_detail_widgets['add_row_btn'].grid(column=0, row=0, sticky=(W), padx=(self.pad_val+2, 0))
        self.form_detail_widgets['save_btn'].grid(column=1, row=0, sticky=(W), padx=(self.pad_val, 0))
        self.current_row_idx += 1

        for i in range(column_idx):
            self.form_detail_widgets['frame']['entry'][current_len].grid_columnconfigure(i, weight=self.base_weights[i])
        
        self.form_detail_widgets['frame']['btns_row'].grid_columnconfigure(0, weight=1)
        self.form_detail_widgets['frame']['btns_row'].grid_columnconfigure(1, weight=1)
    
    def delete_row(self, *args):
        current_len = len(self.form_detail_widgets['del_btn'])
        if current_len > 0:
            row_idx = args[0]

            for key, val in self.form_detail_widgets['entry'].items():
                val[row_idx].destroy()
                del val[row_idx]

            for key, val in self.form_detail_vars.items():
                del val[row_idx]
            
            self.form_detail_widgets['frame']['entry'][row_idx].destroy()
            del self.form_detail_widgets['frame']['entry'][row_idx]

            self.form_detail_widgets['del_btn'][row_idx].destroy()
            del self.form_detail_widgets['del_btn'][row_idx]

            new_current_len = len(self.form_detail_widgets['del_btn'])

            for i in range(new_current_len):
                self.form_detail_widgets['del_btn'][i].configure(command=partial(self.delete_row, i))
        
    def validate_inputs(self):
        is_passed = True
        keys = ['sku', 'temp_invoice_id', 'buyprice', 'sellprice']

        if len(self.form_vars['name'].get()) == 0:
            is_passed = False
        
        res_len = len(self.form_detail_vars['sku'])
        row_idx_to_del = []
        for i in range(res_len):
            is_not_empty = False
            for key in keys:
                if len(self.form_detail_vars[key][i].get()) > 0:
                    if key == 'buyprice' or key == 'sellprice':
                        if self.form_detail_vars[key][i].get() != "0":
                            is_not_empty = True
                    else:
                        is_not_empty = True
            
            if not is_not_empty:
                row_idx_to_del.append(i)

        num_of_del = 0
        for idx in row_idx_to_del:
            self.delete_row((idx-num_of_del))
            num_of_del+=1
        
        return is_passed

    def save_product(self, *args):
        input_valid = self.validate_inputs()
        if not input_valid:
            Alert(self.child_roots, 'Nama harus diisi!')
            return

        res_list = [None]
        Confirmation(self.root, "Product", "Konfirmasi Penyimpanan Produk", res_list=res_list)
        confirmed = res_list[0]

        if confirmed:
            # for key, val in self.form_detail_vars.items():
            #     print(key)
            #     print('len:', len(val))
            #     for item in val:
            #         print(item.get())
            # print("\n")
            
            product_dict = {}
            product_sql = ""
            conn = Connection(user="postgres", password=self.db_password, database="pikacenter")
            conn.run("START TRANSACTION")
            
            if self.action_type_str[0] == 'Add':
                product_sql += "INSERT INTO public.products (pkey, name, description) VALUES (:generated_uuid, :name, :description);"
                product_dict['generated_uuid'] = conn.run("SELECT uuid_generate_v1();")[0][0]
            elif self.action_type_str[0] == 'Manage':
                product_sql += "UPDATE public.products SET name = :name, description = :description WHERE pkey = :product_key"
                product_dict['product_key'] = self.product_key
            product_dict['name'] = self.form_vars['name'].get().replace("\n", "")
            product_dict['description'] = self.form_vars['description'].get().replace("\n", "")
            conn.run(product_sql, **product_dict)

            if self.action_type_str[0] == 'Manage':
                conn.run("DELETE FROM public.products_details WHERE refproductkey = :product_key", product_key=self.product_key)
            
            res_len = len(self.form_detail_vars['sku'])
            for i in range(res_len):
                detail_dict = {}
                detail_sql = ""

                detail_sql += "INSERT INTO public.products_details(pkey, refproductkey, sku, temp_invoice_id, buyprice, sellprice) VALUES(uuid_generate_v1(), :generated_uuid, :sku_"+str(i)+", :temp_invoice_id_"+str(i)+", :buyprice_"+str(i)+", :sellprice_"+str(i)+");"
                
                if self.action_type_str[0] == 'Add':
                    detail_dict['generated_uuid'] = product_dict['generated_uuid']
                elif self.action_type_str[0] == 'Manage':
                    detail_dict['generated_uuid'] = self.product_key

                detail_dict['sku_'+str(i)] = self.form_detail_vars['sku'][i].get()
                detail_dict['temp_invoice_id_'+str(i)] = self.form_detail_vars['temp_invoice_id'][i].get()
                bp_str = str(self.form_detail_vars['buyprice'][i].get())
                bp_str = bp_str.replace(',', '')
                detail_dict['buyprice_'+str(i)] = bp_str
                sp_str = str(self.form_detail_vars['sellprice'][i].get())
                sp_str = sp_str.replace(',', '')
                detail_dict['sellprice_'+str(i)] = sp_str
                
                conn.run(detail_sql, **detail_dict)
            
            conn.run("COMMIT")

            self.close_window()