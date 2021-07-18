from confirmation import Confirmation
from alert import Alert
from functools import partial
from tkinter import *
from tkinter import ttk

from pg8000.native import Connection
import uuid
import tools

from manage_product import ManageProduct

class Inventory:
    def __init__(self, window_status,  db_password):
        self.db_password = db_password
        window_size = {'width': '1200', 'height': '675'}
        self.monitor_actual_area = tools.get_monitor_actual_area()
        self.pad_val = 7
        self.frame_width = int(window_size['width']) - (2 * self.pad_val)
        window_status['is_closed'] = False
        self.window_status = window_status
        self.child_windows_status = {
            'manage_product': {'is_closed': False}
        }

        self.root = Tk()
        self.root.title("Pika Center Invoicing Program - Inventory")
        self.root.geometry(tools.generate_tk_geometry(window_size))
        self.root.protocol('WM_DELETE_WINDOW', self.close_window)
        self.root.resizable(False, False)

        self.main_frame = ttk.Frame(self.root, width=self.frame_width)
        self.tree = {
            'product': ttk.Treeview(self.main_frame, selectmode=BROWSE, show="tree headings", columns=('idx', 'name', 'description', 'stock_rate'), height=13),
            'detail': ttk.Treeview(self.main_frame, selectmode=BROWSE, show="tree headings", columns=('idx', 'sku', 'temp_invoice_id', 'buyprice', 'sellprice'), height=9)
        }
        self.y_scrollbar = {
            'product': ttk.Scrollbar(self.main_frame, orient=VERTICAL, command=self.tree['product'].yview),
            'detail': ttk.Scrollbar(self.main_frame, orient=VERTICAL, command=self.tree['detail'].yview)
        }
        self.detail_label = ttk.Label(self.main_frame, text="Detil Produk \"\"")
        
        self.btn_frame = ttk.Frame(self.main_frame, width=self.frame_width)
        self.refresh_btn = ttk.Button(self.btn_frame, text="Refresh", command=self.refresh_product_tree_data)
        self.add_btn = ttk.Button(self.btn_frame, text="TAMBAH PRODUK", command=partial(self.show_manage_product, 'add'))
        self.manage_btn = ttk.Button(self.btn_frame, text="ATUR PRODUK", command=partial(self.show_manage_product, 'manage'))
        self.delete_btn = ttk.Button(self.btn_frame, text="HAPUS PRODUK", command=self.delete_product)
        
        self.tree['product'].configure(yscrollcommand=self.y_scrollbar['product'].set)
        self.tree['product'].column('#0', width=0, stretch=False)
        self.tree['product'].column('idx', width=int(self.frame_width * 0.025), stretch=False, anchor='center')
        self.tree['product'].column('name', width=int(self.frame_width * 0.475), stretch=False)
        self.tree['product'].column('description',  width=int(self.frame_width * 0.35), stretch=False)
        self.tree['product'].column('stock_rate',  width=int(self.frame_width * .125), stretch=False, anchor='center')
        self.tree['product'].heading('name', text="Nama")
        self.tree['product'].heading('description', text="Deskripsi")
        self.tree['product'].heading('stock_rate', text="Persentasi Stok Tersedia")
        self.tree['detail'].configure(yscrollcommand=self.y_scrollbar['detail'].set)
        self.tree['detail'].column('#0', width=0, stretch=False)
        self.tree['detail'].column('idx', width=int(self.frame_width * .025), stretch=False, anchor='center')
        self.tree['detail'].column('sku', width=int(self.frame_width * .2), stretch=False)
        self.tree['detail'].column('temp_invoice_id', width=int(self.frame_width * .2), stretch=False)
        self.tree['detail'].column('buyprice',  width=int(self.frame_width * 0.275), stretch=False, anchor='e')
        self.tree['detail'].column('sellprice',  width=int(self.frame_width * 0.275), stretch=False, anchor='e')
        self.tree['detail'].heading('sku', text="SKU")
        self.tree['detail'].heading('temp_invoice_id', text="Invoice ID")
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

        self.btn_frame.grid(column=0, row=3, sticky=(N, W, E, S))
        self.refresh_btn.grid(column=0, row=0, ipadx=self.pad_val)
        self.add_btn.grid(column=1, row=0, ipadx=self.pad_val, padx=(0,self.pad_val))
        self.manage_btn.grid(column=2, row=0, ipadx=self.pad_val, padx=(0,self.pad_val))
        self.delete_btn.grid(column=3, row=0, ipadx=self.pad_val, padx=(0,self.pad_val))

        self.root.lift()
        self.root.mainloop()
    
    def refresh_product_tree_data(self):
        self.tree['product'].delete(*self.tree['product'].get_children())
        self.clear_detail()

        conn = Connection(user="postgres", password=self.db_password, database="pikacenter")
        rl = conn.run("SELECT public.products.*, COUNT(public.products_details.pkey) FROM public.products, public.products_details WHERE public.products.pkey = public.products_details.refproductkey AND public.products_details.temp_invoice_id LIKE '' GROUP BY public.products.pkey ORDER BY public.products.name ASC")
        

        dummy = [[uuid.uuid4(), 'Test Name', 'Test Desc'], [uuid.uuid4(), 'Test Name', 'Test Desc'], [uuid.uuid4(), 'Test Name', 'Test Desc'], [uuid.uuid4(), 'Test Name', 'Test Desc'], [uuid.uuid4(), 'Test Name', 'Test Desc'], [uuid.uuid4(), 'Test Name', 'Test Desc'], [uuid.uuid4(), 'Test Name', 'Test Desc'], [uuid.uuid4(), 'Test Name', 'Test Desc'], [uuid.uuid4(), 'Test Name', 'Test Desc'], [uuid.uuid4(), 'Test Name', 'Test Desc'], [uuid.uuid4(), 'Test Name', 'Test Desc'], [uuid.uuid4(), 'Test Name', 'Test Desc'], [uuid.uuid4(), 'Test Name', 'Test Desc'], [uuid.uuid4(), 'Test Name', 'Test Desc'], [uuid.uuid4(), 'Test Name', 'Test Desc'], [uuid.uuid4(), 'Test Name', 'Test Desc'], [uuid.uuid4(), 'Test Name', 'Test Desc'], [uuid.uuid4(), 'Test Name', 'Test Desc'], [uuid.uuid4(), 'Test Name', 'Test Desc'], [uuid.uuid4(), 'Test Name', 'Test Desc'], [uuid.uuid4(), 'Test Name', 'Test Desc'], [uuid.uuid4(), 'Test Name', 'Test Desc'], [uuid.uuid4(), 'Test Name', 'Test Desc'], [uuid.uuid4(), 'Test Name', 'Test Desc'], [uuid.uuid4(), 'Test Name', 'Test Desc'], [uuid.uuid4(), 'Test Name', 'Test Desc'], [uuid.uuid4(), 'Test Name', 'Test Desc']]
        # rl += dummy
    
        for i in range(len(rl)):
            available_stock = int(conn.run("SELECT COUNT(pkey) FROM public.products_details WHERE refproductkey = :product_key ", product_key=rl[i][0])[0][0])
            product = {
                'key':str(rl[i][0]),
                'name': str(rl[i][1]),
                'description': str(rl[i][2]),
                'stock_rate': "{:.1f}%".format(int(rl[i][3]) * 100 / available_stock)
            }
            

            self.tree['product'].insert('', 'end', iid=product['key'], values=(i+1, product['name'], product['description'], product['stock_rate']))            

            
    def refresh_detail_tree_data(self, event):
        self.tree['detail'].delete(*self.tree['detail'].get_children())
        selected_product_key = self.tree['product'].selection()[0]
        self.detail_label.configure(text="Detail Produk \"" + self.tree['product'].item(selected_product_key)['values'][1] + "\"")

        conn = Connection(user="postgres", password=self.db_password, database="pikacenter")

        sql = "SELECT * FROM public.products_details WHERE refproductkey = '" + selected_product_key + "'" + "ORDER BY sku ASC"
        rl_detail = conn.run(sql)

        for i in range(len(rl_detail)):
            detail = {
                'key': str(rl_detail[i][0]),
                'refproductkey': str(rl_detail[i][1]),
                'sku': str(rl_detail[i][2]),
                'temp_invoice_id': str(rl_detail[i][5]),
                'buyprice': tools.create_pretty_numerical(rl_detail[i][3]),
                'sellprice': tools.create_pretty_numerical(rl_detail[i][4])
            }

            self.tree['detail'].insert('', 'end', iid=detail['key'], values=(i+1, detail['sku'], detail['temp_invoice_id'], detail['buyprice'], detail['sellprice']))
    
    def clear_detail(self):
        self.tree['detail'].delete(*self.tree['detail'].get_children())
        self.detail_label.configure(text="Detail Produk \"\"")

    def show_manage_product(self, *args):

        action_type = args[0]
        selected_product_keys = ""

        if action_type == 'manage':
            selected_product_keys = self.tree['product'].selection()
            if len(selected_product_keys) == 0:
                Alert("Produk harus dipilih terlebih dahulu sebelum bisa diatur!")
                return
            else:
                selected_product_keys = selected_product_keys[0]

        self.root.destroy()
        ManageProduct(self.child_windows_status, self.db_password, self, action_type, selected_product_keys)

    def delete_product(self, *args):
        selected_product_key = self.tree['product'].selection()[0]

        if len(selected_product_key) == 0:
            Alert("Produk harus dipilih terlebih dahulu sebelum bisa dihapus!")
            return
        
        res_list = [None]
        Confirmation("Delete", "Konfirmasi Penghapusan Produk Terpilih?", res_list)
        confirmed = res_list[0]
        
        if confirmed:
            conn = Connection(user="postgres", password=self.db_password, database="pikacenter")
            conn.run("START TRANSACTION")
            conn.run("DELETE FROM public.products_details WHERE refproductkey = :product_key", product_key=selected_product_key)
            conn.run("DELETE FROM public.products WHERE pkey = :product_key", product_key=selected_product_key)
            conn.run("COMMIT")
            self.refresh_product_tree_data()

    def close_window(self):
        tools.change_window_status(self.window_status, 'is_closed', True)
        self.root.destroy()

