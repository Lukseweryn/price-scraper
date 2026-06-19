import os
import csv
import json
import sys
import threading
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from collections import defaultdict

import matplotlib
matplotlib.use('TkAgg')
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SHOP_INFO_FILE = os.path.join(BASE_DIR, 'shop_information.json')
SHOP_CLASS_FILE = os.path.join(BASE_DIR, 'shop_class.json')
RESULTS_FILE = os.path.join(BASE_DIR, 'results.csv')


# ── file helpers ──────────────────────────────────────────────────────────────

def load_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, encoding='utf-8') as f:
        return json.load(f)

def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_results():
    if not os.path.exists(RESULTS_FILE):
        return []
    with open(RESULTS_FILE, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


# ── dialogs ───────────────────────────────────────────────────────────────────

class ProductDialog(tk.Toplevel):
    def __init__(self, parent, title, product=None):
        super().__init__(parent)
        self.title(title)
        self.resizable(False, False)
        self.grab_set()
        self.result = None

        fields = [
            ("Product name:", 'product_name'),
            ("Shop name:",    'shop_name'),
            ("URL:",          'url'),
        ]
        self.vars = {}
        for row, (label, key) in enumerate(fields):
            ttk.Label(self, text=label).grid(row=row, column=0, sticky='w', padx=12, pady=5)
            var = tk.StringVar(value=product.get(key, '') if product else '')
            ttk.Entry(self, textvariable=var, width=50).grid(row=row, column=1, padx=12, pady=5)
            self.vars[key] = var

        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=len(fields), column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text="Save",   command=self._save).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side='left', padx=5)

        self.wait_window()

    def _save(self):
        result = {k: v.get().strip() for k, v in self.vars.items()}
        if not all(result.values()):
            messagebox.showwarning("Validation", "All fields are required.", parent=self)
            return
        self.result = result
        self.destroy()


class ShopDialog(tk.Toplevel):
    def __init__(self, parent, title, shop_key=None, classes=None):
        super().__init__(parent)
        self.title(title)
        self.resizable(False, False)
        self.grab_set()
        self.result = None

        ttk.Label(self, text="Shop key:").grid(row=0, column=0, sticky='w', padx=12, pady=5)
        self.key_var = tk.StringVar(value=shop_key or '')
        key_entry = ttk.Entry(self, textvariable=self.key_var, width=40)
        key_entry.grid(row=0, column=1, padx=12, pady=5)
        if shop_key:
            key_entry.configure(state='disabled')

        ttk.Label(self, text="CSS classes\n(one per line):").grid(row=1, column=0, sticky='nw', padx=12, pady=5)
        self.classes_text = tk.Text(self, width=40, height=6)
        self.classes_text.grid(row=1, column=1, padx=12, pady=5)
        if classes:
            self.classes_text.insert('1.0', '\n'.join(classes))

        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text="Save",   command=self._save).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side='left', padx=5)

        self.wait_window()

    def _save(self):
        key = self.key_var.get().strip()
        classes = [c.strip() for c in self.classes_text.get('1.0', 'end').splitlines() if c.strip()]
        if not key or not classes:
            messagebox.showwarning("Validation",
                                   "Shop key and at least one CSS class are required.", parent=self)
            return
        self.result = (key, classes)
        self.destroy()


# ── main application ──────────────────────────────────────────────────────────

class PriceScraperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Price Scraper")
        self.root.geometry("1050x680")
        self.root.minsize(800, 520)

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        self._build_products_tab()
        self._build_shops_tab()
        self._build_results_tab()

    # ── Products ──────────────────────────────────────────────────────────────

    def _build_products_tab(self):
        frame = ttk.Frame(self.notebook, padding=5)
        self.notebook.add(frame, text="  Products  ")

        cols = ('product_name', 'shop_name', 'url')
        self.products_tree = ttk.Treeview(frame, columns=cols, show='headings', selectmode='browse')
        self.products_tree.heading('product_name', text='Product Name')
        self.products_tree.heading('shop_name',    text='Shop')
        self.products_tree.heading('url',          text='URL')
        self.products_tree.column('product_name', width=220)
        self.products_tree.column('shop_name',    width=120)
        self.products_tree.column('url',          width=560)

        vsb = ttk.Scrollbar(frame, orient='vertical',   command=self.products_tree.yview)
        hsb = ttk.Scrollbar(frame, orient='horizontal', command=self.products_tree.xview)
        self.products_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.products_tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=2, column=0, columnspan=2, sticky='ew', pady=(6, 0))
        ttk.Button(btn_frame, text="Add",     command=self._add_product).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="Edit",    command=self._edit_product).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="Delete",  command=self._delete_product).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="Refresh", command=self._load_products).pack(side='right', padx=2)

        self._load_products()

    def _load_products(self):
        self.products_tree.delete(*self.products_tree.get_children())
        for p in load_json(SHOP_INFO_FILE, []):
            self.products_tree.insert('', 'end',
                                      values=(p['product_name'], p['shop_name'], p['url']))

    def _add_product(self):
        dlg = ProductDialog(self.root, "Add Product")
        if dlg.result:
            products = load_json(SHOP_INFO_FILE, [])
            products.append(dlg.result)
            save_json(SHOP_INFO_FILE, products)
            self._load_products()

    def _edit_product(self):
        sel = self.products_tree.selection()
        if not sel:
            messagebox.showinfo("Edit", "Select a product first.")
            return
        vals = self.products_tree.item(sel[0], 'values')
        current = {'product_name': vals[0], 'shop_name': vals[1], 'url': vals[2]}
        dlg = ProductDialog(self.root, "Edit Product", current)
        if dlg.result:
            products = load_json(SHOP_INFO_FILE, [])
            for i, p in enumerate(products):
                if p['url'] == current['url']:
                    products[i] = dlg.result
                    break
            save_json(SHOP_INFO_FILE, products)
            self._load_products()

    def _delete_product(self):
        sel = self.products_tree.selection()
        if not sel:
            messagebox.showinfo("Delete", "Select a product first.")
            return
        vals = self.products_tree.item(sel[0], 'values')
        if not messagebox.askyesno("Confirm", f"Delete '{vals[0]}'?"):
            return
        products = [p for p in load_json(SHOP_INFO_FILE, []) if p['url'] != vals[2]]
        save_json(SHOP_INFO_FILE, products)
        self._load_products()

    # ── Shops ─────────────────────────────────────────────────────────────────

    def _build_shops_tab(self):
        frame = ttk.Frame(self.notebook, padding=5)
        self.notebook.add(frame, text="  Shops  ")

        cols = ('shop_key', 'css_classes')
        self.shops_tree = ttk.Treeview(frame, columns=cols, show='headings', selectmode='browse')
        self.shops_tree.heading('shop_key',   text='Shop Key')
        self.shops_tree.heading('css_classes', text='CSS Classes')
        self.shops_tree.column('shop_key',    width=160)
        self.shops_tree.column('css_classes', width=720)

        vsb = ttk.Scrollbar(frame, orient='vertical', command=self.shops_tree.yview)
        self.shops_tree.configure(yscrollcommand=vsb.set)

        self.shops_tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=1, column=0, columnspan=2, sticky='ew', pady=(6, 0))
        ttk.Button(btn_frame, text="Add",     command=self._add_shop).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="Edit",    command=self._edit_shop).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="Delete",  command=self._delete_shop).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="Refresh", command=self._load_shops).pack(side='right', padx=2)

        self._load_shops()

    def _load_shops(self):
        self.shops_tree.delete(*self.shops_tree.get_children())
        for key, classes in load_json(SHOP_CLASS_FILE, {}).items():
            self.shops_tree.insert('', 'end', values=(key, ', '.join(classes)))

    def _add_shop(self):
        dlg = ShopDialog(self.root, "Add Shop")
        if dlg.result:
            shops = load_json(SHOP_CLASS_FILE, {})
            key, classes = dlg.result
            if key in shops:
                messagebox.showwarning("Add Shop", f"Shop key '{key}' already exists.")
                return
            shops[key] = classes
            save_json(SHOP_CLASS_FILE, shops)
            self._load_shops()

    def _edit_shop(self):
        sel = self.shops_tree.selection()
        if not sel:
            messagebox.showinfo("Edit", "Select a shop first.")
            return
        key = self.shops_tree.item(sel[0], 'values')[0]
        shops = load_json(SHOP_CLASS_FILE, {})
        dlg = ShopDialog(self.root, "Edit Shop", shop_key=key, classes=shops.get(key, []))
        if dlg.result:
            _, classes = dlg.result
            shops[key] = classes
            save_json(SHOP_CLASS_FILE, shops)
            self._load_shops()

    def _delete_shop(self):
        sel = self.shops_tree.selection()
        if not sel:
            messagebox.showinfo("Delete", "Select a shop first.")
            return
        key = self.shops_tree.item(sel[0], 'values')[0]
        if not messagebox.askyesno("Confirm", f"Delete shop '{key}'?"):
            return
        shops = load_json(SHOP_CLASS_FILE, {})
        shops.pop(key, None)
        save_json(SHOP_CLASS_FILE, shops)
        self._load_shops()

    # ── Results ───────────────────────────────────────────────────────────────

    def _build_results_tab(self):
        frame = ttk.Frame(self.notebook, padding=5)
        self.notebook.add(frame, text="  Results  ")

        # Top bar
        top = ttk.Frame(frame)
        top.pack(fill='x', pady=(0, 6))

        ttk.Label(top, text="Chart:").pack(side='left', padx=(0, 4))
        self.chart_product_var = tk.StringVar()
        self.product_combo = ttk.Combobox(top, textvariable=self.chart_product_var,
                                          state='readonly', width=30)
        self.product_combo.pack(side='left', padx=(0, 10))
        self.product_combo.bind('<<ComboboxSelected>>', lambda _: self._update_chart())

        self.run_btn = ttk.Button(top, text="Run Scraper", command=self._run_scraper)
        self.run_btn.pack(side='right', padx=2)
        ttk.Button(top, text="Refresh", command=self._load_results).pack(side='right', padx=2)

        # Paned: table top, chart bottom
        paned = ttk.PanedWindow(frame, orient='vertical')
        paned.pack(fill='both', expand=True)

        # Table
        table_frame = ttk.Frame(paned)
        paned.add(table_frame, weight=1)

        cols = ('SKLEP', 'PRODUKT', 'CENA', 'DATA')
        self.results_tree = ttk.Treeview(table_frame, columns=cols, show='headings')
        for col in cols:
            self.results_tree.heading(col, text=col)
            self.results_tree.column(col, width=180)
        vsb = ttk.Scrollbar(table_frame, orient='vertical', command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=vsb.set)
        self.results_tree.pack(side='left', fill='both', expand=True)
        vsb.pack(side='right', fill='y')

        # Chart
        chart_frame = ttk.Frame(paned)
        paned.add(chart_frame, weight=1)

        fig = Figure(figsize=(9, 3), dpi=96, tight_layout=True)
        self.ax = fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)

        # Scraper log output
        self.log_text = tk.Text(frame, height=5, state='disabled',
                                font=('Consolas', 8), wrap='word')
        self.log_text.pack(fill='x', pady=(6, 0))

        self._load_results()

    def _load_results(self):
        self.results_tree.delete(*self.results_tree.get_children())
        rows = load_results()
        products = sorted({r['PRODUKT'] for r in rows})
        self.product_combo['values'] = products
        if products and not self.chart_product_var.get():
            self.chart_product_var.set(products[0])
        for row in rows:
            self.results_tree.insert('', 'end',
                                     values=(row['SKLEP'], row['PRODUKT'], row['CENA'], row['DATA']))
        self._update_chart()

    def _update_chart(self):
        product = self.chart_product_var.get()
        self.ax.clear()
        dates, prices = [], []
        for r in load_results():
            if r['PRODUKT'] != product:
                continue
            try:
                dates.append(datetime.strptime(r['DATA'], '%Y-%m-%d'))
                prices.append(float(r['CENA']))
            except (ValueError, TypeError):
                continue
        if dates:
            self.ax.plot(dates, prices, marker='o', linewidth=2, color='steelblue')
            self.ax.set_title(product, fontsize=10)
            self.ax.set_ylabel("Price")
            self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            self.ax.figure.autofmt_xdate(rotation=25)
            self.ax.grid(True, alpha=0.3)
        else:
            self.ax.set_title("No data" if not product else f"No data for: {product}", fontsize=10)
        self.canvas.draw()

    def _run_scraper(self):
        self.run_btn.configure(state='disabled', text="Running…")
        self._append_log("--- Starting scraper ---")

        def run():
            try:
                proc = subprocess.run(
                    [sys.executable, os.path.join(BASE_DIR, 'main_script.py')],
                    capture_output=True, text=True
                )
                output = (proc.stdout + proc.stderr).strip()
                self.root.after(0, lambda: self._append_log(output or "Done."))
            except Exception as e:
                self.root.after(0, lambda: self._append_log(f"Launch error: {e}"))
            finally:
                self.root.after(0, self._scraper_finished)

        threading.Thread(target=run, daemon=True).start()

    def _scraper_finished(self):
        self.run_btn.configure(state='normal', text="Run Scraper")
        self._append_log("--- Finished ---")
        self._load_results()

    def _append_log(self, text):
        self.log_text.configure(state='normal')
        self.log_text.insert('end', text.rstrip() + '\n')
        self.log_text.see('end')
        self.log_text.configure(state='disabled')


# ── entry point ───────────────────────────────────────────────────────────────

if __name__ == '__main__':
    root = tk.Tk()
    PriceScraperApp(root)
    root.mainloop()
