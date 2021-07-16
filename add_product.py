from tkinter import *
from tkinter import ttk

from pg8000.native import Connection
import tools

class AddProduct:
    def __init__(self, window_status, db_password):
        self.db_password = db_password
        window_size = {'width': '800', 'height': '450'}
        self.monitor_actual_area = tools.get_monitor_actual_area()
        self.pad_val = 7
        self.frame_width = int(window_size['width']) - (3 * self.pad_val)
        self.frame_height = int(window_size['height']) - (2 * self.pad_val)
        self.window_status = window_status

        self.root = Tk()
        self.root.title("Pika Center Invoicing Program - Add Product")
        self.root.geometry(tools.generate_tk_geometry(window_size))
        self.root.protocol('WM_DELETE_WINDOW', tools.change_window_status(self.window_status, 'is_closed', True))
        self.root.resizable(False, False)

        self.canvas_frame = ttk.Frame(self.root)
        self.canvas = Canvas(self.canvas_frame, width=self.frame_width, height=self.frame_height)
        self.canvas_sb = ttk.Scrollbar(self.canvas_frame, orient=VERTICAL, command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.canvas_sb.set)
        self.canvas.bind('<Configure>', lambda event: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.main_frame = ttk.Frame(self.canvas, borderwidth=2, relief='groove')
        self.title_label = ttk.Label(self.main_frame, text="Formulir Penambahan Produk", font=("Calibri", "16"), borderwidth=2, relief='groove')
        
        self.window_height = self.frame_height + 2000
        self.window_id = self.canvas.create_window((0,0), window=self.main_frame, anchor="nw", width=self.frame_width, height=self.window_height)

        self.form_vars = {
            'product':{
                'name': StringVar(),
                'description': StringVar()
            },
        }

        self.form_frame = ttk.Frame(self.main_frame, width=self.frame_width, borderwidth=2, relief='groove')
        self.form_row_frame = {
            'name': ttk.Frame(self.form_frame, borderwidth=2, relief='groove', width=self.frame_width),
            'description': ttk.Frame(self.form_frame, borderwidth=2, relief='groove', width=self.frame_width),
        }
        self.form_row_col_frame = {
            'label':{
                'name': ttk.Frame(self.form_row_frame['name'], borderwidth=2, relief='groove', width=int(self.frame_width*.34)),
                'description': ttk.Frame(self.form_row_frame['description'], borderwidth=2, relief='groove', width=int(self.frame_width*.34))
            },
            'entry':{
                'name': ttk.Frame(self.form_row_frame['name'], borderwidth=2, relief='groove', width=int(self.frame_width*.66)),
                'description': ttk.Frame(self.form_row_frame['description'], borderwidth=2, relief='groove', width=int(self.frame_width*.66))
            },
        }

        self.form_widgets = {
            'product':{
                'label': {
                    'name': ttk.Label(self.form_row_frame['name'], text="Nama Barang", justify='right', borderwidth=2, relief='groove'),
                    'description': ttk.Label(self.form_row_frame['description'], text="Deskripsi", justify='right', borderwidth=2, relief='groove')
                },
                'entry': {
                    'name': ttk.Entry(self.form_row_frame['name'], textvariable=self.form_vars['product']['name'], width=50),
                    'description': ttk.Entry(self.form_row_frame['description'], textvariable=self.form_vars['product']['description'], width=50),
                }
            },
        }
        
        self.form_detail_vars = {
            'sku': [StringVar()],
            'temp_invoice_id': [StringVar()],
            'buyprice': [StringVar()],
            'sellprice': [StringVar()],
        }
        self.form_detail_widgets = {}
        self.form_detail_widgets['frame'] = {
            'title': ttk.Frame(self.form_frame, borderwidth=2, relief='groove', width=self.frame_width),
            'heading': {'base': ttk.Frame(self.form_frame, borderwidth=2, relief='groove')},
            'entry': [ttk.Frame(self.form_frame, borderwidth=2, relief='groove')],
            'add_row': ttk.Frame(self.form_frame, borderwidth=2, relief='groove')
        }
        self.form_detail_widgets['frame']['heading']['column'] ={
            'sku': ttk.Frame(self.form_detail_widgets['frame']['heading']['base'], borderwidth=2, relief='groove'),
            'temp_invoice_id': ttk.Frame(self.form_detail_widgets['frame']['heading']['base'], borderwidth=2, relief='groove'),
            'buyprice': ttk.Frame(self.form_detail_widgets['frame']['heading']['base'], borderwidth=2, relief='groove'),
            'sellprice': ttk.Frame(self.form_detail_widgets['frame']['heading']['base'], borderwidth=2, relief='groove'),
            'del_btn': ttk.Frame(self.form_detail_widgets['frame']['heading']['base'], borderwidth=2, relief='groove')
        }
        self.form_detail_widgets['label'] = {
            'title': ttk.Label(self.form_detail_widgets['frame']['title'], text="Detil Produk", borderwidth=2, relief='groove'),
            'heading': {
                'sku': ttk.Label(self.form_detail_widgets['frame']['heading']['column']['sku'], text="SKU", borderwidth=2, relief='groove'),
                'temp_invoice_id': ttk.Label(self.form_detail_widgets['frame']['heading']['column']['temp_invoice_id'], text="No. Invoice", borderwidth=2, relief='groove'),
                'buyprice': ttk.Label(self.form_detail_widgets['frame']['heading']['column']['buyprice'], text="Harga Beli", borderwidth=2, relief='groove'),
                'sellprice': ttk.Label(self.form_detail_widgets['frame']['heading']['column']['sellprice'], text="Harga Jual", borderwidth=2, relief='groove'),
                'del_btn': ttk.Label(self.form_detail_widgets['frame']['heading']['column']['del_btn'], text="HAPUS", borderwidth=2, relief='groove')
            }
        }
        self.form_detail_widgets['entry'] = {
            'sku': [ttk.Entry(self.form_detail_widgets['frame']['entry'][0], justify='center', textvariable=self.form_detail_vars['sku'][0])],
            'temp_invoice_id': [ttk.Entry(self.form_detail_widgets['frame']['entry'][0], justify='center', textvariable=self.form_detail_vars['temp_invoice_id'][0])],
            'buyprice': [ttk.Entry(self.form_detail_widgets['frame']['entry'][0], justify='center', textvariable=self.form_detail_vars['buyprice'][0])],
            'sellprice': [ttk.Entry(self.form_detail_widgets['frame']['entry'][0], justify='center', textvariable=self.form_detail_vars['sellprice'][0])],
        }
        self.form_detail_widgets['del_btn'] = [ttk.Button(self.form_detail_widgets['frame']['entry'][0], text='X',width=3)]
        self.form_detail_widgets['add_row_btn'] = ttk.Button(self.form_detail_widgets['frame']['add_row'], text='Tambah', command=self.add_new_row, width=10)

        self.canvas_frame.grid(column=0, row=0, sticky=(N, E, S, W))
        self.canvas.grid(column=0, row=0, sticky=(N, E, S, W))
        self.canvas_sb.grid(column=1, row=0, sticky=(N,S,E))
        # self.main_frame.grid(column=0, row=0, sticky=(N, E, S, W))
        self.title_label.grid(column=0, row=0, pady=self.pad_val*2)

        self.form_frame.grid(column=0, row=1, sticky=(N, W, E, S), pady=(self.pad_val*2, 0))

        self.form_row_frame['name'].grid(column=0, row=0)
        self.form_row_frame['description'].grid(column=0, row=1)

        self.form_row_col_frame['label']['name'].grid(column=0, row=0)
        self.form_widgets['product']['label']['name'].grid(column=0, row=0, padx=self.pad_val, sticky=(E))
        self.form_row_col_frame['entry']['name'].grid(column=1, row=0)
        self.form_widgets['product']['entry']['name'].grid(column=1, row=0, padx=self.pad_val, sticky=(W))
        self.form_row_col_frame['label']['description'].grid(column=0, row=0)
        self.form_widgets['product']['label']['description'].grid(column=0, row=0, padx=self.pad_val, sticky=(E))
        self.form_row_col_frame['entry']['description'].grid(column=1, row=0)
        self.form_widgets['product']['entry']['description'].grid(column=1, row=0, padx=self.pad_val, sticky=(W))

        self.form_detail_widgets['frame']['title'].grid(column=0, row=2)
        self.form_detail_widgets['frame']['heading']['base'].grid(column=0, row=3, sticky=(W, E))
        self.form_detail_widgets['frame']['heading']['column']['sku'].grid(column=0, row=0, sticky=(W, E))
        self.form_detail_widgets['frame']['heading']['column']['temp_invoice_id'].grid(column=1, row=0, sticky=(W, E))
        self.form_detail_widgets['frame']['heading']['column']['buyprice'].grid(column=2, row=0, sticky=(W, E))
        self.form_detail_widgets['frame']['heading']['column']['sellprice'].grid(column=3, row=0, sticky=(W, E))
        self.form_detail_widgets['frame']['heading']['column']['del_btn'].grid(column=4, row=0, sticky=(W, E))
        self.form_detail_widgets['frame']['entry'][0].grid(column=0, row=4, sticky=(W, E))
        self.form_detail_widgets['frame']['add_row'].grid(column=0, row=5, sticky=(W, E))
        self.current_row = 5

        self.form_detail_widgets['label']['title'].grid(column=0, row=0)
        self.form_detail_widgets['label']['heading']['sku'].grid(column=0, row=0)
        self.form_detail_widgets['label']['heading']['temp_invoice_id'].grid(column=0, row=0)
        self.form_detail_widgets['label']['heading']['buyprice'].grid(column=0, row=0)
        self.form_detail_widgets['label']['heading']['sellprice'].grid(column=0, row=0)
        self.form_detail_widgets['label']['heading']['del_btn'].grid(column=0, row=0)

        self.form_detail_widgets['entry']['sku'][0].grid(column=0, row=0, sticky=(W), padx=(self.pad_val+3,0))
        self.form_detail_widgets['entry']['temp_invoice_id'][0].grid(column=1, row=0, sticky=(W), padx=(self.pad_val*3, 0), ipadx=self.pad_val*2)
        self.form_detail_widgets['entry']['buyprice'][0].grid(column=2, row=0, sticky=(W), padx=(self.pad_val,0), ipadx=self.pad_val*2)
        self.form_detail_widgets['entry']['sellprice'][0].grid(column=3, row=0, sticky=(W), ipadx=self.pad_val*2)
        self.form_detail_widgets['del_btn'][0].grid(column=4, row=0, sticky=(W), padx=(0, self.pad_val*2))

        self.form_detail_widgets['add_row_btn'].grid(column=0, row=0, sticky=(W), padx=(self.pad_val+2, 0))

        for child in self.form_frame.winfo_children():
            child.grid_configure(pady=(self.pad_val*2, 0))
        
        self.root.grid_columnconfigure(0, weight=1)

        self.canvas_frame.grid_columnconfigure(0, weight=10)
        self.canvas_frame.grid_columnconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.form_frame.grid_columnconfigure(0, weight=1)

        for key, row_frame in self.form_row_frame.items():
            row_frame.grid_columnconfigure(0, weight=1)
            row_frame.grid_columnconfigure(1, weight=1)             
        
        for key, label in self.form_widgets['product']['label'].items():
            label.grid_columnconfigure(0, weight=1)
        for key, entry in self.form_widgets['product']['entry'].items():
            entry.grid_columnconfigure(0, weight=1)

        self.form_detail_widgets['frame']['title'].grid_columnconfigure(0, weight=1)
        self.form_detail_widgets['frame']['heading']['base'].grid_columnconfigure(0, weight=8)
        self.form_detail_widgets['frame']['heading']['base'].grid_columnconfigure(1, weight=10)
        self.form_detail_widgets['frame']['heading']['base'].grid_columnconfigure(2, weight=9)
        self.form_detail_widgets['frame']['heading']['base'].grid_columnconfigure(3, weight=8)
        self.form_detail_widgets['frame']['heading']['base'].grid_columnconfigure(4, weight=1)
        self.form_detail_widgets['frame']['heading']['column']['sku'].grid_columnconfigure(0, weight=1)
        self.form_detail_widgets['frame']['heading']['column']['temp_invoice_id'].grid_columnconfigure(0, weight=1)
        self.form_detail_widgets['frame']['heading']['column']['buyprice'].grid_columnconfigure(0, weight=1)
        self.form_detail_widgets['frame']['heading']['column']['sellprice'].grid_columnconfigure(0, weight=1)
        self.form_detail_widgets['frame']['heading']['column']['del_btn'].grid_columnconfigure(0, weight=1)
        self.form_detail_widgets['frame']['entry'][0].grid_columnconfigure(0, weight=6)
        self.form_detail_widgets['frame']['entry'][0].grid_columnconfigure(1, weight=10)
        self.form_detail_widgets['frame']['entry'][0].grid_columnconfigure(2, weight=9)
        self.form_detail_widgets['frame']['entry'][0].grid_columnconfigure(3, weight=8)
        self.form_detail_widgets['frame']['entry'][0].grid_columnconfigure(4, weight=1)
        self.form_detail_widgets['frame']['add_row'].grid_columnconfigure(0, weight=1)
        
        self.root.mainloop()
    
    def add_new_row(self, *args):
        current_len = self.current_row - 4
        self.form_detail_widgets['frame']['entry'].append(ttk.Frame(self.form_frame, borderwidth=2, relief='groove'))
        self.form_detail_vars['sku'].append(StringVar())
        self.form_detail_widgets['entry']['sku'].append(ttk.Entry(self.form_detail_widgets['frame']['entry'][current_len], justify='center', textvariable=self.form_detail_vars['sku'][current_len]))
        self.form_detail_vars['temp_invoice_id'].append(StringVar())
        self.form_detail_widgets['entry']['temp_invoice_id'].append(ttk.Entry(self.form_detail_widgets['frame']['entry'][current_len], justify='center', textvariable=self.form_detail_vars['temp_invoice_id'][current_len]))
        self.form_detail_vars['buyprice'].append(StringVar())
        self.form_detail_widgets['entry']['buyprice'].append(ttk.Entry(self.form_detail_widgets['frame']['entry'][current_len], justify='center', textvariable=self.form_detail_vars['buyprice'][current_len]))
        self.form_detail_vars['sellprice'].append(StringVar())
        self.form_detail_widgets['entry']['sellprice'].append(ttk.Entry(self.form_detail_widgets['frame']['entry'][current_len], justify='center'   , textvariable=self.form_detail_vars['sellprice'][current_len]))
        self.form_detail_widgets['del_btn'].append(ttk.Button(self.form_detail_widgets['frame']['entry'][current_len], text='X',width=3))

        self.form_detail_widgets['frame']['entry'][current_len].grid(column=0, row=self.current_row, sticky=(W, E))
        self.form_detail_widgets['entry']['sku'][current_len].grid(column=0, row=0, sticky=(W), padx=(self.pad_val+3,0))
        self.form_detail_widgets['entry']['temp_invoice_id'][current_len].grid(column=1, row=0, sticky=(W), padx=(self.pad_val*3, 0), ipadx=self.pad_val*2)
        self.form_detail_widgets['entry']['buyprice'][current_len].grid(column=2, row=0, sticky=(W), padx=(self.pad_val,0), ipadx=self.pad_val*2)
        self.form_detail_widgets['entry']['sellprice'][current_len].grid(column=3, row=0, sticky=(W), ipadx=self.pad_val*2)
        self.form_detail_widgets['del_btn'][current_len].grid(column=4, row=0, sticky=(W), padx=(0, self.pad_val*2))

        self.current_row += 1

        self.form_detail_widgets['frame']['add_row'].grid(column=0, row=self.current_row, sticky=(W, E))
        self.form_detail_widgets['add_row_btn'].grid(column=0, row=0, sticky=(W), padx=(self.pad_val+2, 0))

        self.form_detail_widgets['frame']['entry'][current_len].grid_columnconfigure(0, weight=6)
        self.form_detail_widgets['frame']['entry'][current_len].grid_columnconfigure(1, weight=10)
        self.form_detail_widgets['frame']['entry'][current_len].grid_columnconfigure(2, weight=9)
        self.form_detail_widgets['frame']['entry'][current_len].grid_columnconfigure(3, weight=8)
        self.form_detail_widgets['frame']['entry'][current_len].grid_columnconfigure(4, weight=1)
        self.form_detail_widgets['frame']['add_row'].grid_columnconfigure(0, weight=1)