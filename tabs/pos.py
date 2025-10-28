from datetime import datetime
import os
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from db_connection import create_connection
from ui.theme import COLORS

FALLBACK_IMAGE = "images/image.png"  # Use a default image if menu image is missing

class PosTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.menu_items = []
        self.image_cache = {}
        self.cart = {}  # {menu_id: {'name':..., 'price':..., 'qty':...}}

        # ===== Top Cart Button + Search =====
        top_frame = tk.Frame(self, bg=COLORS["bg"])
        top_frame.pack(fill="x", pady=10, padx=10)

        tk.Label(top_frame, text="Search:", font=("Arial", 12, 'bold'), bg=COLORS["bg"]).pack(side="left")
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(top_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side="left", padx=5)
        self.search_var.trace_add("write", lambda *_: self.populate_menu())

        # Cart button with count
        self.cart_btn = ttk.Button(top_frame, text="🛒 Cart (0)", command=self.show_cart)
        self.cart_btn.pack(side="right")

        # ===== Scrollable Menu Area =====
        canvas = tk.Canvas(self, bg=COLORS["bg"], highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=scrollbar.set)

        self.menu_frame = tk.Frame(canvas, bg=COLORS["bg"])
        canvas.create_window((0, 0), window=self.menu_frame, anchor="nw")
        self.menu_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # Load menu from database
        self.load_menu_from_db()
        self.populate_menu()

    # --- Load menu items from DB ---
    def load_menu_from_db(self):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT menu_id, name, image, price, category, status FROM menu ORDER BY category, name")
        self.menu_items = cursor.fetchall()
        conn.close()

    # --- Update cart button count ---
    def update_cart_btn(self):
        count = sum(item['qty'] for item in self.cart.values())
        self.cart_btn.config(text=f"🛒 Cart ({count})")

    # --- Populate menu area ---
    def populate_menu(self):
        for widget in self.menu_frame.winfo_children():
            widget.destroy()

        search_text = self.search_var.get().lower()
        filtered_items = [i for i in self.menu_items if search_text in i[1].lower()]

        current_category = None
        for menu_id, name, image_path, price, category, status in filtered_items:
            if category != current_category:
                current_category = category
                tk.Label(self.menu_frame, text=category, font=("Arial", 14, "bold"), bg=COLORS["bg"]).pack(anchor="w", pady=(10,5), padx=10)

            card = tk.Frame(self.menu_frame, bg=COLORS["card"], bd=1, relief="raised", padx=10, pady=10)
            card.pack(fill="x", pady=5, padx=20)

            # Load image from local path
            if image_path not in self.image_cache:
                img_path = image_path if os.path.exists(image_path) else FALLBACK_IMAGE
                try:
                    img = Image.open(img_path)
                    img.thumbnail((100, 200))
                    self.image_cache[image_path] = ImageTk.PhotoImage(img)
                except:
                    self.image_cache[image_path] = None

            if self.image_cache[image_path]:
                tk.Label(card, image=self.image_cache[image_path], bg=COLORS["card"]).pack(side="left", padx=5)

            # Info
            info_frame = tk.Frame(card, bg=COLORS["card"])
            info_frame.pack(side="left", padx=10, fill="x", expand=True)
            tk.Label(info_frame, text=name, font=("Arial",12,'bold'), bg=COLORS["card"]).pack(anchor="w")
            tk.Label(info_frame, text=f"BHD {price:.2f}", font=("Arial",10), bg=COLORS["card"]).pack(anchor="w")

            # Status badge
            status_color = "#f39c12" if status.lower() == "available" else "#e74c3c"
            tk.Label(
                info_frame,
                text=status.upper(),
                bg=status_color,
                fg="white",
                font=("Arial", 9, "bold"),
                padx=10,
                pady=3,
                relief="ridge",
                bd=2
            ).pack(anchor="w", pady=4)

            # Add to Cart button
            if status.lower() == "available":
                ttk.Button(card, text="Add to Cart", command=lambda mid=menu_id: self.add_to_cart(mid)).pack(side="right", padx=5)

    # --- Add item to cart ---
    def add_to_cart(self, menu_id):
        item = next((i for i in self.menu_items if i[0]==menu_id), None)
        if not item:
            return
        _, name, _, price, _, _ = item
        if menu_id in self.cart:
            self.cart[menu_id]['qty'] += 1
        else:
            self.cart[menu_id] = {'name': name, 'price': price, 'qty': 1}

        self.update_cart_btn()


    def show_cart(self):
        if not self.cart:
            messagebox.showinfo("Cart", "Cart is empty!")
            return

        win = tk.Toplevel(self)
        win.title("Cart")
        win.geometry("450x600")
        win.configure(bg=COLORS["card"])

        items_frame = tk.Frame(win, bg=COLORS["card"])
        items_frame.pack(fill="both", expand=True, padx=10, pady=10)

        total_var = tk.DoubleVar(value=0.0)

        def update_total():
            total = sum(v['price']*v['qty'] for v in self.cart.values())
            total_var.set(total)
            self.update_cart_btn()  # update main cart button count

        # Display cart items (same as before)
        for menu_id, info in list(self.cart.items()):
            frame = tk.Frame(items_frame, bg=COLORS["card"])
            frame.pack(fill="x", pady=5)

            tk.Label(frame, text=info['name'], bg=COLORS["card"], font=("Arial",10,'bold')).pack(side="left")
            qty_label = tk.Label(frame, text=str(info['qty']), bg=COLORS["card"], width=3)
            qty_label.pack(side="left", padx=5)
            tk.Label(frame, text=f"BHD {info['price']*info['qty']:.2f}", bg=COLORS["card"]).pack(side="left", padx=5)

            def plus(mid=menu_id, ql=qty_label):
                self.cart[mid]['qty'] += 1
                ql.config(text=str(self.cart[mid]['qty']))
                update_total()

            def minus(mid=menu_id, ql=qty_label):
                if self.cart[mid]['qty'] > 1:
                    self.cart[mid]['qty'] -= 1
                    ql.config(text=str(self.cart[mid]['qty']))
                else:
                    del self.cart[mid]
                    frame.destroy()
                update_total()

            ttk.Button(frame, text="+", command=plus, width=2).pack(side="right", padx=2)
            ttk.Button(frame, text="-", command=minus, width=2).pack(side="right", padx=2)

        # Total price
        tk.Label(win, text="Total:", bg=COLORS["card"], font=("Arial",12,'bold')).pack(anchor="w", padx=10)
        tk.Label(win, textvariable=total_var, bg=COLORS["card"], font=("Arial",12,'bold')).pack(anchor="w", padx=10)
        update_total()

        # ===== Customer Info Fields =====
        cust_frame = tk.Frame(win, bg=COLORS["card"])
        cust_frame.pack(fill="x", pady=10, padx=10)

        tk.Label(cust_frame, text="Customer Name:", bg=COLORS["card"]).grid(row=0, column=0, sticky="w")
        customer_name_var = tk.StringVar()
        ttk.Entry(cust_frame, textvariable=customer_name_var).grid(row=0, column=1, sticky="ew", padx=5)

        tk.Label(cust_frame, text="Customer Phone:", bg=COLORS["card"]).grid(row=1, column=0, sticky="w")
        customer_phone_var = tk.StringVar()
        ttk.Entry(cust_frame, textvariable=customer_phone_var).grid(row=1, column=1, sticky="ew", padx=5)

        cust_frame.columnconfigure(1, weight=1)

        # Payment buttons
        btn_frame = tk.Frame(win, bg=COLORS["card"])
        btn_frame.pack(pady=10)
        ttk.Button(
            btn_frame,
            text="Pay by Card",
            command=lambda: self.pay_by_card(win, customer_name_var.get(), customer_phone_var.get(), list(self.cart.values()))
        ).pack(side="left", padx=5)
        ttk.Button(
            btn_frame,
            text="Pay by Cash",
            command=lambda: self.pay_by_cash(win, customer_name_var.get(), customer_phone_var.get(), list(self.cart.values()))
        ).pack(side="left", padx=5)

    # --- Card Payment ---
    def pay_by_card(self, cart_window, cust_name, cust_phone, cart_items):
        if not cart_items:
            messagebox.showerror("Error", "Cart is empty!")
            return
        if not cust_name or not cust_phone:
            messagebox.showerror("Error", "Please enter customer name and phone!")
            return

        cart_window.destroy()
        total_price = sum(item['price'] * item['qty'] for item in cart_items)

        conn = create_connection()
        cursor = conn.cursor()

        # Create customer
        cursor.execute("INSERT INTO customer (customer_name, phone) VALUES (%s, %s)", (cust_name, cust_phone))
        customer_id = cursor.lastrowid

        # Create order
        cursor.execute("INSERT INTO orders (customer_id, total_price, order_date) VALUES (%s, %s, %s)",
                    (customer_id, total_price, datetime.now()))
        order_id = cursor.lastrowid
        conn.commit()
        conn.close()

        # Clear cart
        self.cart.clear()
        self.update_cart_btn()

        # Card Payment Window
        win = tk.Toplevel()
        win.title("Card Payment")
        win.geometry("400x550")
        win.configure(bg="#f0f0f0")

        tk.Label(win, text="Card Number:").pack(pady=5, anchor="w", padx=10)
        card_number_var = tk.StringVar()
        ttk.Entry(win, textvariable=card_number_var).pack(fill="x", padx=10)

        tk.Label(win, text="Cardholder Name:").pack(pady=5, anchor="w", padx=10)
        card_name_var = tk.StringVar()
        ttk.Entry(win, textvariable=card_name_var).pack(fill="x", padx=10)

        tk.Label(win, text="Security Code:").pack(pady=5, anchor="w", padx=10)
        cvv_var = tk.StringVar()
        ttk.Entry(win, textvariable=cvv_var).pack(fill="x", padx=10)

        tk.Label(win, text="Expiry Date (MM/YY):").pack(pady=5, anchor="w", padx=10)
        expiry_var = tk.StringVar()
        ttk.Entry(win, textvariable=expiry_var).pack(fill="x", padx=10)

        tk.Label(win, text="Employee ID:").pack(pady=5, anchor="w", padx=10)
        emp_id_var = tk.IntVar()
        ttk.Entry(win, textvariable=emp_id_var).pack(fill="x", padx=10)

        tk.Label(win, text=f"Amount to Pay: BHD {total_price:.2f}", font=("Arial", 12, "bold")).pack(pady=10)

        def process_payment():
            if not all([card_number_var.get(), card_name_var.get(), cvv_var.get(), expiry_var.get(), emp_id_var.get()]):
                messagebox.showerror("Error", "Please fill all fields!")
                return

            # Fetch employee name from employee ID
            conn = create_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM employees WHERE employee_id = %s", (emp_id_var.get(),))
            result = cursor.fetchone()
            if not result:
                messagebox.showerror("Error", "Employee ID not found!")
                conn.close()
                return
            emp_name = result[0]

            # Insert into bill
            cursor.execute("""
                INSERT INTO bill (customer_id, order_id, bill_date, payment_method, bill_amount, employee_id, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (customer_id, order_id, datetime.now(), "Card", total_price, emp_id_var.get(), "Paid"))
            bill_id = cursor.lastrowid
            conn.commit()
            conn.close()

            # Display Bill
            for widget in win.winfo_children():
                widget.destroy()

            tk.Label(win, text="*** BILL RECEIPT ***", font=("Arial", 14, "bold")).pack(pady=5)
            tk.Label(win, text=f"Bill ID: {bill_id}").pack(anchor="w", padx=10)
            tk.Label(win, text=f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}").pack(anchor="w", padx=10)
            tk.Label(win, text=f"Customer: {cust_name}").pack(anchor="w", padx=10)
            tk.Label(win, text=f"Employee: {emp_name} (ID: {emp_id_var.get()})").pack(anchor="w", padx=10)
            tk.Label(win, text="-----------------------------------").pack(pady=5)

            for item in cart_items:
                item_total = item['qty'] * item['price']
                tk.Label(win, text=f"{item['name']} x {item['qty']} @ BHD {item['price']:.2f} = BHD {item_total:.2f}").pack(anchor="w", padx=10)

            tk.Label(win, text="-----------------------------------").pack(pady=5)
            tk.Label(win, text=f"Total Amount: BHD {total_price:.2f}", font=("Arial", 12, "bold")).pack(anchor="w", padx=10)
            tk.Label(win, text=f"Payment Method: Card").pack(anchor="w", padx=10)

            tk.Button(win, text="Close", command=win.destroy).pack(pady=10)

        ttk.Button(win, text="Pay", command=process_payment, bootstyle="primary").pack(pady=15)


# --- Cash Payment ---
    def pay_by_cash(self, cart_window, cust_name, cust_phone, cart_items):
        if not cart_items:
            messagebox.showerror("Error", "Cart is empty!")
            return
        if not cust_name or not cust_phone:
            messagebox.showerror("Error", "Please enter customer name and phone!")
            return

        cart_window.destroy()
        total_price = sum(item['price'] * item['qty'] for item in cart_items)

        conn = create_connection()
        cursor = conn.cursor()

        # Create customer
        cursor.execute("INSERT INTO customer (customer_name, phone) VALUES (%s, %s)", (cust_name, cust_phone))
        customer_id = cursor.lastrowid

        # Create order
        cursor.execute("INSERT INTO orders (customer_id, total_price, order_date) VALUES (%s, %s, %s)",
                    (customer_id, total_price, datetime.now()))
        order_id = cursor.lastrowid
        conn.commit()
        conn.close()

        # Clear cart
        self.cart.clear()
        self.update_cart_btn()

        # Cash Payment Window
        win = tk.Toplevel()
        win.title("Cash Payment")
        win.geometry("350x350")
        win.configure(bg="#f0f0f0")

        tk.Label(win, text="Employee ID:").pack(pady=5, anchor="w", padx=10)
        emp_id_var = tk.IntVar()
        ttk.Entry(win, textvariable=emp_id_var).pack(fill="x", padx=10)

        tk.Label(win, text=f"Amount to Pay: BHD {total_price:.2f}", font=("Arial", 12, "bold")).pack(pady=10)

        def payment_received():
            if not emp_id_var.get():
                messagebox.showerror("Error", "Please enter employee ID!")
                return

            # Fetch employee name from employee ID
            conn = create_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM employees WHERE employee_id = %s", (emp_id_var.get(),))
            result = cursor.fetchone()
            if not result:
                messagebox.showerror("Error", "Employee ID not found!")
                conn.close()
                return
            emp_name = result[0]

            # Insert bill
            cursor.execute("""
                INSERT INTO bill (customer_id, order_id, bill_date, payment_method, bill_amount, employee_id, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (customer_id, order_id, datetime.now(), "Cash", total_price, emp_id_var.get(), "Pending"))
            bill_id = cursor.lastrowid
            conn.commit()
            conn.close()

            # Display Bill
            for widget in win.winfo_children():
                widget.destroy()

            tk.Label(win, text="*** BILL RECEIPT ***", font=("Arial", 14, "bold")).pack(pady=5)
            tk.Label(win, text=f"Bill ID: {bill_id}").pack(anchor="w", padx=10)
            tk.Label(win, text=f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}").pack(anchor="w", padx=10)
            tk.Label(win, text=f"Customer: {cust_name}").pack(anchor="w", padx=10)
            tk.Label(win, text=f"Employee: {emp_name} (ID: {emp_id_var.get()})").pack(anchor="w", padx=10)
            tk.Label(win, text="-----------------------------------").pack(pady=5)

            for item in cart_items:
                item_total = item['qty'] * item['price']
                tk.Label(win, text=f"{item['name']} x {item['qty']} @ BHD {item['price']:.2f} = BHD {item_total:.2f}").pack(anchor="w", padx=10)

            tk.Label(win, text="-----------------------------------").pack(pady=5)
            tk.Label(win, text=f"Total Amount: BHD {total_price:.2f}", font=("Arial", 12, "bold")).pack(anchor="w", padx=10)
            tk.Label(win, text=f"Payment Method: Cash").pack(anchor="w", padx=10)

            tk.Button(win, text="Close", command=win.destroy).pack(pady=10)

        ttk.Button(win, text="Payment Received", command=payment_received).pack(pady=15)
