from tkinter import *
from tkinter import ttk

from pg8000.native import Connection
import uuid
import tools

class Inventory:
    def __init__(self, window_status,  db_password):
        self.db_password = db_password
        window_size = {'width': '1200', 'height': '675'}
        self.monitor_actual_area = tools.get_monitor_actual_area()
        self.pad_val = 7
        self.frame_width = int(window_size['width']) - (2 * self.pad_val)
        self.window_status = window_status

        self.root = Tk()
        self.root.title("Pika Center Invoicing Program - Inventory")
        self.root.geometry(tools.generate_tk_geometry(window_size))
        self.root.protocol('WM_DELETE_WINDOW', tools.change_window_status(self.window_status, 'is_closed', True))
        self.root.resizable(False, False)

        self.main_frame = ttk.Frame(self.root, width=self.frame_width)

        self.tree = {
            'product': ttk.Treeview(self.main_frame, selectmode=BROWSE, show="tree headings", columns=('idx', 'name', 'description'), height=13),
            'detail': ttk.Treeview(self.main_frame, selectmode=BROWSE, show="tree headings", columns=('idx', 'sku', 'buyprice', 'sellprice'), height=13)
        }
        self.y_scrollbar = {
            'product': ttk.Scrollbar(self.main_frame, orient=VERTICAL, command=self.tree['product'].yview),
            'detail': ttk.Scrollbar(self.main_frame, orient=VERTICAL, command=self.tree['detail'].yview)
        }

        self.detail_label = ttk.Label(self.main_frame, text="Detil Barang")
        
        self.tree['product'].configure(yscrollcommand=self.y_scrollbar['product'].set)
        self.tree['product'].column('#0', width=0, stretch=False)
        self.tree['product'].column('idx', width=int(self.frame_width * 0.025), stretch=False, anchor='center')
        self.tree['product'].column('name', width=int(self.frame_width * 0.675), stretch=False)
        self.tree['product'].column('description',  width=int(self.frame_width * 0.275), stretch=False)
        self.tree['product'].heading('name', text="Nama")
        self.tree['product'].heading('description', text="Deskripsi")
        
        self.tree['detail'].configure(yscrollcommand=self.y_scrollbar['detail'].set)
        self.tree['detail'].column('#0', width=0, stretch=False)
        self.tree['detail'].column('idx', width=int(self.frame_width * 0.025), stretch=False, anchor='center')
        self.tree['detail'].column('sku', width=int(self.frame_width * 0.55), stretch=False)
        self.tree['detail'].column('buyprice',  width=int(self.frame_width * 0.2), stretch=False, anchor='e')
        self.tree['detail'].column('sellprice',  width=int(self.frame_width * 0.2), stretch=False, anchor='e')
        self.tree['detail'].heading('sku', text="SKU")
        self.tree['detail'].heading('buyprice', text="Harga Beli")
        self.tree['detail'].heading('sellprice', text="Harga Jual Default")
        self.refresh_product_tree_data()


        self.tree['product'].bind('<<TreeviewSelect>>', self.refresh_detail_tree_data)


        self.main_frame.grid(column=0, row=0, sticky=(N, W, E, S))

        self.tree['product'].grid(column=0, row=0)
        self.y_scrollbar['product'].grid(column=1, row=0, sticky=(N, S))
        
        self.tree['detail'].grid(column=0, row=2)
        self.y_scrollbar['detail'].grid(column=1, row=2, sticky=(N, S))

        for child in self.main_frame.winfo_children():
            child.grid_configure(padx=self.pad_val, pady=self.pad_val)
        
        self.detail_label.grid(column=0, columnspan=2, row=1, padx=self.pad_val, pady=(int(self.pad_val * 2), 0))
        
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        self.root.mainloop()
    
    def refresh_product_tree_data(self):
        conn = Connection(user="postgres", password=self.db_password, database="pikacenter")
        rl = conn.run("SELECT * FROM public.products ORDER BY name ASC")

        dummy = [[uuid.uuid4(), 'Test Name', 'Test Desc'], [uuid.uuid4(), 'Test Name', 'Test Desc'], [uuid.uuid4(), 'Test Name', 'Test Desc'], [uuid.uuid4(), 'Test Name', 'Test Desc'], [uuid.uuid4(), 'Test Name', 'Test Desc'], [uuid.uuid4(), 'Test Name', 'Test Desc'], [uuid.uuid4(), 'Test Name', 'Test Desc'], [uuid.uuid4(), 'Test Name', 'Test Desc'], [uuid.uuid4(), 'Test Name', 'Test Desc'], [uuid.uuid4(), 'Test Name', 'Test Desc'], [uuid.uuid4(), 'Test Name', 'Test Desc'], [uuid.uuid4(), 'Test Name', 'Test Desc'], [uuid.uuid4(), 'Test Name', 'Test Desc'], [uuid.uuid4(), 'Test Name', 'Test Desc'], [uuid.uuid4(), 'Test Name', 'Test Desc'], [uuid.uuid4(), 'Test Name', 'Test Desc'], [uuid.uuid4(), 'Test Name', 'Test Desc'], [uuid.uuid4(), 'Test Name', 'Test Desc'], [uuid.uuid4(), 'Test Name', 'Test Desc'], [uuid.uuid4(), 'Test Name', 'Test Desc'], [uuid.uuid4(), 'Test Name', 'Test Desc'], [uuid.uuid4(), 'Test Name', 'Test Desc'], [uuid.uuid4(), 'Test Name', 'Test Desc'], [uuid.uuid4(), 'Test Name', 'Test Desc'], [uuid.uuid4(), 'Test Name', 'Test Desc'], [uuid.uuid4(), 'Test Name', 'Test Desc'], [uuid.uuid4(), 'Test Name', 'Test Desc']]
        # rl += dummy
    
        for i in range(len(rl)):
            product = {
                'key':str(rl[i][0]),
                'name': str(rl[i][1]),
                'description': str(rl[i][2])
            }

            self.tree['product'].insert('', 'end', iid=product['key'], values=(i+1, product['name'], product['description']))            

            
    def refresh_detail_tree_data(self, event):
        self.tree['detail'].delete(*self.tree['detail'].get_children())
        selected_product_key = self.tree['product'].selection()[0]
        self.detail_label.configure(text="Detail Barang \"" + self.tree['product'].item(selected_product_key)['values'][1] + "\"")

        conn = Connection(user="postgres", password=self.db_password, database="pikacenter")

        sql = "SELECT * FROM public.products_details WHERE refproductkey = '" + selected_product_key + "'" + "ORDER BY sku ASC"
        rl_detail = conn.run(sql)

        for i in range(len(rl_detail)):
            detail = {
                'key': str(rl_detail[i][0]),
                'refproductkey': str(rl_detail[i][1]),
                'sku': str(rl_detail[i][2]),
                'buyprice': tools.add_string_commas(('%.24f' % rl_detail[i][3]).rstrip('0').rstrip('.')),
                'sellprice': tools.add_string_commas(('%.24f' % rl_detail[i][4]).rstrip('0').rstrip('.'))
            }

            self.tree['detail'].insert('', 'end', iid=detail['key'], values=(i+1, detail['sku'], detail['buyprice'], detail['sellprice']))
