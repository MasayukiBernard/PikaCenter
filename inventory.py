from alert import Alert
from confirmation import Confirmation
from functools import partial
from tkinter import *
from tkinter import ttk

from datetime import date
from decimal import Decimal
from pg8000.native import Connection
import re
import tools

from manage_product import ManageProduct

class Inventory:
    def __init__(self, window_status, parent_child_roots_list, db_password):
        self.db_password = db_password
        window_size = {'width': '1280', 'height': '700'}
        self.monitor_actual_area = tools.get_monitor_actual_area()
        self.pad_val = 7
        self.frame_width = int(window_size['width']) - (2 * self.pad_val)
        window_status['is_closed'] = False
        self.window_status = window_status
        self.child_windows_status = {
            'manage_product': {'is_closed': False}
        }

        self.root = Toplevel()
        self.child_roots = []
        parent_child_roots_list.append(self.child_roots)
        parent_child_roots_list.append(self.root)

        self.root.title("Pika Center Invoicing Program - Inventory")
        self.root.iconphoto(False, PhotoImage(file='resources/images/Pika Center Indonesia Logo 2021.png'))
        self.root.geometry(tools.generate_tk_geometry(window_size))
        self.root.protocol('WM_DELETE_WINDOW', self.close_window)
        self.root.resizable(False, False)

        self.main_frame = ttk.Frame(self.root, width=self.frame_width)
        self.window_title = ttk.Label(self.main_frame, text="INVENTORY", anchor='center', font=("Calibri", "28", "bold"))
        self.product_search_var = StringVar()
        self.placeholder_val = ". . . Search by Name or Description"
        self.product_search_var.set(self.placeholder_val)
        search_bar_style = ttk.Style()
        search_bar_style.configure('ipadded.TEntry', padding=[self.pad_val, 0, self.pad_val, 0])
        self.product_search_bar = ttk.Entry(self.main_frame, textvariable=self.product_search_var, width=48, foreground='#A9A9A9', justify='right', style='ipadded.TEntry')
        self.product_search_bar.bind('<FocusIn>', partial(self.manage_placeholder, 'in', self.product_search_var, self.placeholder_val))
        self.product_search_bar.bind('<FocusOut>', partial(self.manage_placeholder, 'out', self.product_search_var, self.placeholder_val))
        self.product_search_bar.bind('<KeyRelease>', partial(self.refresh_product_tree_data, True))
        
        self.tree = {
            'product': ttk.Treeview(self.main_frame, selectmode=BROWSE, show="tree headings", columns=('idx', 'sku', 'latest_release_date', 'name', 'description', 'available_stock', 'availability_rate'), height=9),
            'arrived': ttk.Treeview(self.main_frame, selectmode=BROWSE, show="tree headings", columns=('idx', 'entry_date', 'eta', 'qty', 'buyprice'), height=4),
            'sold': ttk.Treeview(self.main_frame, selectmode=BROWSE, show="tree headings", columns=('idx', 'sold_date', 'Invoice ID', 'qty', 'sellprice', 'sales_type'), height=4),
        }
        self.tree_style = ttk.Style()
        self.tree_style.map("Treeview", foreground=self.fixed_map("foreground"), background=self.fixed_map("background"))
        
        self.y_scrollbar = {
            'product': ttk.Scrollbar(self.main_frame, orient=VERTICAL, command=self.tree['product'].yview),
            'arrived': ttk.Scrollbar(self.main_frame, orient=VERTICAL, command=self.tree['arrived'].yview),
            'sold': ttk.Scrollbar(self.main_frame, orient=VERTICAL, command=self.tree['sold'].yview)
        }

        tree_config = {
            'product': {
                'column_index': ['#0', 'idx', 'sku', 'latest_release_date', 'name', 'description', 'available_stock', 'availability_rate'],
                'heading_text': ['', '', 'SKU', 'Latest Release Date', 'Name', 'Description', 'Available Stock(s)', 'Availability Rate'],
                'width': [0, int(self.frame_width * .025), int(self.frame_width * .1), int(self.frame_width * .1), int(self.frame_width * .4), int(self.frame_width * .175), int(self.frame_width * .0875), int(self.frame_width * .0875)],
                'anchor': ['center', 'center', 'center', 'center', 'w', 'w', 'center', 'e'] 
            },
            'arrived': {
                'column_index': ['#0', 'idx', 'entry_date', 'eta', 'qty', 'buyprice'],
                'heading_text': ['', '', 'Entry Date', 'ETA', 'Qty', 'Buy Price'],
                'width': [0, int(self.frame_width * .025), int(self.frame_width * .1), int(self.frame_width * .1), int(self.frame_width * .075), int(self.frame_width * .675)],
                'anchor': ['center', 'center', 'center', 'center', 'center', 'e'] 
            },
            'sold': {
                'column_index': ['#0', 'idx', 'sold_date', 'Invoice ID', 'qty', 'sellprice', 'sales_type'],
                'heading_text': ['', '', 'Sold Date', 'Invoice ID', 'Qty', 'Sell Price', 'Sales Type'],
                'width': [0, int(self.frame_width * .025), int(self.frame_width * .1), int(self.frame_width * .15), int(self.frame_width * .075), int(self.frame_width * .475), int(self.frame_width * .15)],
                'anchor': ['center', 'center', 'center', 'center', 'center', 'e', 'center'] 
            }
        }
        for key, value in tree_config.items():
            self.tree[key].configure(yscrollcommand=self.y_scrollbar[key].set)
            for i in range(len(value['column_index'])):
                self.tree[key].column(value['column_index'][i], width=value['width'][i], stretch=False, anchor=value['anchor'][i])
                self.tree[key].heading(value['column_index'][i], text=value['heading_text'][i])

        self.subtitle_label = {
            'product': ttk.Label(self.main_frame, text="Product(s) List", anchor='center', font=("", "15", "bold")),
            'arrived': ttk.Label(self.main_frame, text="Arrived \"\" Product Logs", anchor='center', font=("", "15", "bold")),
            'sold': ttk.Label(self.main_frame, text="Sold \"\" Product Logs", anchor='center', font=("", "15", "bold")),
        }

        self.product_btn_frame = ttk.Frame(self.main_frame, width=self.frame_width)
        self.product_tree_btn = {
            'refresh': ttk.Button(self.product_btn_frame, text="Refresh", command=partial(self.refresh_product_tree_data, False)),
            'manage_product_with_entries': ttk.Button(self.product_btn_frame, text="MANAGE PRODUCT & ARRIVED LOGS", command=partial(self.show_manage_product, 'arrived')),
            'manage_sold': ttk.Button(self.product_btn_frame, text="MANAGE SOLD", command=partial(self.show_manage_product, 'sold')),
            'delete': ttk.Button(self.product_btn_frame, text="DELETE", command=partial(self.delete_product, 'delete'))
        }
        self.tree['product'].bind('<<TreeviewSelect>>', self.refresh_detail_trees_data)

        self.arrived_averaged_buyprice_label = ttk.Label(self.main_frame, text="Average Buy Price: -", font=("", "11", "bold"))

        for child in self.main_frame.winfo_children():
            child.grid_configure(padx=self.pad_val, pady=(0, self.pad_val))
            
        self.main_frame.grid(column=0, row=0, sticky=(N, W, E, S))
        self.window_title.grid(column=0, columnspan=2, row=0,sticky=(W, E))

        self.subtitle_label['product'].grid(column=0, columnspan=2, row=1, sticky=(W, E))
        self.product_search_bar.grid(column=0, row=2, sticky=(E), ipadx=self.pad_val*2)
        self.tree['product'].grid(column=0, row=3, sticky=(W, E))
        self.y_scrollbar['product'].grid(column=1, row=3, sticky=(N, S, E))
        self.product_btn_frame.grid(column=0, row=4, sticky=(W, E))
        self.product_tree_btn['refresh'].grid(column=0, row=0, ipadx=self.pad_val)
        self.product_tree_btn['manage_product_with_entries'].grid(column=1, row=0, ipadx=self.pad_val, padx=(self.pad_val*3,self.pad_val))
        self.product_tree_btn['manage_sold'].grid(column=2, row=0, ipadx=self.pad_val, padx=(0,self.pad_val))
        self.product_tree_btn['delete'].grid(column=3, row=0, padx=(700,0), ipadx=self.pad_val, sticky=(W))

        self.subtitle_label['arrived'].grid(column=0, columnspan=2, row=5, sticky=(W, E))
        self.tree['arrived'].grid(column=0, row=6, pady=(self.pad_val, 0))
        self.y_scrollbar['arrived'].grid(column=1, row=6, sticky=(N, S, E))
        self.arrived_averaged_buyprice_label.grid(column=0, row=7, sticky=(E))
        
        self.subtitle_label['sold'].grid(column=0, columnspan=2, row=8, sticky=(W, E))
        self.tree['sold'].grid(column=0, row=9)
        self.y_scrollbar['sold'].grid(column=1, row=9, sticky=(N, S, E))

        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        self.refresh_product_tree_data(False)
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
        # Returns the style map for 'option' with any styles starting with
        # ("!disabled", "!selected", ...) filtered out

        # style.map() returns an empty list for missing options, so this should
        # be future-safe
        return [elm for elm in self.tree_style.map("Treeview", query_opt=option)
                if elm[:2] != ("!disabled", "!selected")]

    def refresh_product_tree_data(self, *args):
        is_search = args[0]

        conn = Connection(user="postgres", password=self.db_password, database="pikacenter")

        added_condition_sql =  ""
        added_condition = ""
        if is_search:
            added_condition = tools.create_pretty_alphanumerical(self.product_search_var.get())
            added_condition = re.escape(added_condition)
            added_condition_sql  += 'WHERE (LOWER(p.name) LIKE LOWER(\'%' + added_condition + '%\') or LOWER(p.description) LIKE LOWER(\'%' + added_condition + '%\'))'
        else:
            self.product_search_var.set(self.placeholder_val)
        
        sql = "SELECT p.*, apl_0.entry_date AS last_entry_date FROM public.products as p LEFT OUTER JOIN public.arrived_products_log AS apl_0 ON (apl_0.pkey = (SELECT DISTINCT ON (entry_date) pkey FROM public.arrived_products_log WHERE refproductkey = p.pkey AND entry_date IS NOT NULL ORDER BY entry_date DESC LIMIT 1)) " + added_condition_sql + " GROUP BY p.pkey, apl_0.entry_date ORDER BY p.sku, p.name ASC;"
        rl = conn.run(sql, added_condition=added_condition)

        self.tree['product'].delete(*self.tree['product'].get_children())
        self.clear_detail_trees()

        for i in range(len(rl)):
            arrived_stock = int(conn.run("SELECT COALESCE(SUM(qty), 0) FROM public.arrived_products_log WHERE refproductkey = :product_key and entry_date IS NOT NULL;", product_key=rl[i][0])[0][0])
            used_stock = int(conn.run("SELECT COALESCE(SUM(qty), 0) FROM public.sold_products_log WHERE refproductkey = :product_key;", product_key=rl[i][0])[0][0])
            product = {
                'key':str(rl[i][0]),
                'latest_release_date': rl[i][4].strftime("%Y - %b - %d") if rl[i][4] is not None else "N / A",
                'name': str(rl[i][1]),
                'description': str(rl[i][2]),
                'sku': str(rl[i][3]),
                'available_stock': str(tools.create_pretty_numerical(arrived_stock - used_stock)) + " / " + str(tools.create_pretty_numerical(arrived_stock)),
                'availibility_rate': "{:.1f}%".format((arrived_stock - used_stock) * 100 / arrived_stock) if (arrived_stock - used_stock) > 0 else '0.0%'
            }
            
            created_tag = ''
            if (arrived_stock - used_stock) < 0:
                created_tag = 'caution'
                
            
            self.tree['product'].insert('', 'end', iid=product['key'], values=(i+1, product['sku'], product['latest_release_date'], product['name'], product['description'], product['available_stock'], product['availibility_rate']), tags=(created_tag,))
        
        self.tree['product'].tag_configure('caution', foreground='red', background='yellow')

            
    def refresh_detail_trees_data(self, event):
        selected_product_key = self.tree['product'].selection()[0]
        
        tree_key = ['arrived', 'sold']
        label_text = ["Arrived \"", "Sold \""]

        sql = ["SELECT ", " FROM ", " WHERE refproductkey = :product_key ", " ORDER BY "]
        column = ["*", "spl.pkey, spl.sold_date, spl.qty, spl.sellprice, spl.temp_invoice_id, st.name as sales_type"]
        table = ["public.arrived_products_log", "public.sold_products_log as spl,public.sales_types as st"]
        additional_condition = ["", "AND spl.refsalestypekey = st.pkey"]
        order_by = ["entry_date DESC, eta DESC", "sold_date ASC, temp_invoice_id ASC"]

        args = [[2,3,4,5], [1,4,2,3,5]]
        conn = Connection(user="postgres", password=self.db_password, database="pikacenter")

        for i in range(len(tree_key)):
            self.tree[tree_key[i]].delete(*self.tree[tree_key[i]].get_children())
            self.subtitle_label[tree_key[i]].configure(text= label_text[i] + self.tree['product'].item(selected_product_key)['values'][3] + "\" Product Logs")
            rl_detail = conn.run(sql[0] + column[i] + sql[1] + table[i] + sql[2] + additional_condition[i] + sql[3] + order_by[i], product_key=selected_product_key)
            
            total_buy_price = 0
            for j in range(len(rl_detail)):
                if tree_key[i] == 'arrived':
                    total_buy_price += int(rl_detail[j][5])
                val_args = ["N / A" if rl_detail[j][args[i][k]] is None else tools.create_pretty_numerical(rl_detail[j][args[i][k]]) if isinstance(rl_detail[j][args[i][k]], Decimal) or isinstance(rl_detail[j][args[i][k]], int) else rl_detail[j][args[i][k]].strftime("%Y - %b - %d") if isinstance(rl_detail[j][args[i][k]], date) else rl_detail[j][args[i][k]] for k in range(len(args[i]))]
                self.tree[tree_key[i]].insert('', 'end', iid=rl_detail[j][0], values=(j+1, *val_args))

            if tree_key[i] == 'arrived':
                self.arrived_averaged_buyprice_label.configure(text="Average Buy Price: " + (tools.create_pretty_numerical(total_buy_price / len(rl_detail)) if len(rl_detail) > 0 else "-"))
    
    def clear_detail_trees(self):
        self.tree['arrived'].delete(*self.tree['arrived'].get_children())
        self.subtitle_label['arrived'].configure(text="Arrived \"\" Product Logs")
        self.arrived_averaged_buyprice_label.configure(text="Average Buy Price: -")

        self.tree['sold'].delete(*self.tree['sold'].get_children())
        self.subtitle_label['sold'].configure(text="Sold \"\" Product Logs")

    def show_manage_product(self, *args):

        action_type = args[0]

        if action_type == 'arrived' or action_type == 'sold':
            selected_product_keys = self.tree['product'].selection()
            if len(selected_product_keys) == 1:
                selected_product_keys = selected_product_keys[0]
            else:
                selected_product_keys = ""

        ManageProduct(self.child_windows_status, self.child_roots, self.db_password, action_type, selected_product_keys)

    def delete_product(self, *args):
        selected_product_key = self.tree['product'].selection()[0]

        if len(selected_product_key) == 0:
            Alert(self.child_roots, "Please select a listed product before deleting it!")
            return
        
        res_list = [None]
        Confirmation(self.root, "Delete", "Konfirmasi Penghapusan Produk Terpilih?", res_list)
        confirmed = res_list[0]
        
        if confirmed:
            conn = Connection(user="postgres", password=self.db_password, database="pikacenter")
            conn.run("START TRANSACTION")
            conn.run("DELETE FROM public.arrived_products_log WHERE refproductkey = :product_key", product_key=selected_product_key)
            conn.run("DELETE FROM public.sold_products_log WHERE refproductkey = :product_key", product_key=selected_product_key)
            conn.run("DELETE FROM public.products WHERE pkey = :product_key", product_key=selected_product_key)
            conn.run("COMMIT")
            self.refresh_product_tree_data(False)

