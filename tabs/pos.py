from datetime import datetime
import os
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from db_connection import create_connection

FALLBACK_IMAGE = "images/image.png"

# Use the exact same color scheme as Menu tab
CARD_BG = "#124035"  # Dark green for CARDS
TEXT_COLOR = "#ebcd95"  # Golden
BACKGROUND_COLOR = "#23170e"  # Dark brown for BACKGROUND
BORDER_COLOR = "#444444"  # Grey border color

class PosTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BACKGROUND_COLOR)
        self.menu_items = []
        self.image_cache = {}
        self.cart = {}  # {menu_id: {'name':..., 'price':..., 'qty':..., 'menu_id':...}}

        # Configure ttk styles
        self.configure_styles()

        # ===== Top Cart Button + Search =====
        top_frame = tk.Frame(self, bg=BACKGROUND_COLOR)
        top_frame.pack(fill="x", pady=12, padx=15)

        tk.Label(top_frame, text="Search:", font=("Arial", 12), 
                bg=BACKGROUND_COLOR, fg=TEXT_COLOR).pack(side="left")
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(top_frame, textvariable=self.search_var, width=25, style="Custom.TEntry")
        search_entry.pack(side="left", padx=8)
        self.search_var.trace_add("write", lambda *_: self.populate_menu())

        # Cart button with count
        self.cart_btn = ttk.Button(top_frame, text="🛒 Cart (0)", command=self.show_cart, style="Custom.TButton")
        self.cart_btn.pack(side="right")

        # ===== Scrollable Menu Area =====
        canvas = tk.Canvas(self, bg=BACKGROUND_COLOR, highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview, style="Custom.Vertical.TScrollbar")
        scrollbar.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=scrollbar.set)

        self.menu_frame = tk.Frame(canvas, bg=BACKGROUND_COLOR)
        canvas.create_window((0, 0), window=self.menu_frame, anchor="nw")
        self.menu_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # Load menu from database
        self.load_menu_from_db()
        self.populate_menu()

    def center_window(self, window):
        """
        Center any window on the screen
        """
        window.update_idletasks()
        
        # Get the screen dimensions
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        
        # Get the window dimensions
        window_width = window.winfo_width()
        window_height = window.winfo_height()
        
        # Calculate the position
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        # Set the position
        window.geometry(f"+{x}+{y}")

    def configure_styles(self):
        """Configure ttk styles to match our dark theme - EXACT SAME AS MENU TAB"""
        style = ttk.Style()
        
        # Configure Entry style
        style.configure("Custom.TEntry",
                       fieldbackground="#2d2015",
                       foreground=TEXT_COLOR,
                       borderwidth=2,
                       relief="solid")
        
        # Configure Button style
        style.configure("Custom.TButton",
                       background=CARD_BG,
                       foreground=TEXT_COLOR,
                       borderwidth=2,
                       relief="raised",
                       focuscolor="none")
        
        style.map("Custom.TButton",
                 background=[('active', '#1a8a5c')],
                 foreground=[('active', TEXT_COLOR)])
        
        # Configure Scrollbar style
        style.configure("Custom.Vertical.TScrollbar",
                       background=CARD_BG,
                       troughcolor=BACKGROUND_COLOR,
                       borderwidth=0,
                       relief="flat")

    def _nuclear_force_green_cards(self):
        """
        EXACT SAME NUCLEAR ROUTINE AS MENU TAB
        """
        if not hasattr(self, 'menu_frame'):
            return

        def widget_inside_card(widget):
            """Return True if widget is inside a card (an ancestor with is_card == True)."""
            parent = widget.master
            while parent:
                if getattr(parent, "is_card", False):
                    return True
                parent = parent.master
            return False

        def enforce_theme(widget):
            try:
                # Skip anything that is inside a card
                if widget_inside_card(widget):
                    return

                # Apply background and foreground to common widget types
                if isinstance(widget, tk.Frame) or isinstance(widget, tk.Canvas):
                    # set bg to global background
                    try:
                        widget.configure(bg=BACKGROUND_COLOR)
                    except:
                        pass
                elif isinstance(widget, tk.Label):
                    # Labels outside cards: dark background + golden text
                    try:
                        widget.configure(bg=BACKGROUND_COLOR, fg=TEXT_COLOR)
                    except:
                        pass
                elif isinstance(widget, tk.Button):
                    # regular tk.Button: adapt background and fg
                    try:
                        widget.configure(bg=CARD_BG, fg=TEXT_COLOR)
                    except:
                        pass
            except:
                pass

            # Recurse
            for child in widget.winfo_children():
                enforce_theme(child)

        enforce_theme(self.menu_frame)

    def load_menu_from_db(self):
        """Load menu items from database"""
        try:
            conn = create_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT menu_id, name, image, price, category, status FROM menu ORDER BY category, name")
            self.menu_items = cursor.fetchall()
            conn.close()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to load menu: {str(e)}")
            self.menu_items = []

    def update_cart_btn(self):
        """Update cart button count"""
        count = sum(item['qty'] for item in self.cart.values())
        self.cart_btn.config(text=f"🛒 Cart ({count})")

    def populate_menu(self):
        """Populate menu area with items - EXACT SAME STRUCTURE AS MENU TAB"""
        for widget in self.menu_frame.winfo_children():
            widget.destroy()

        search_text = self.search_var.get().lower()
        filtered_items = [i for i in self.menu_items if search_text in i[1].lower()]

        current_category = None
        row_frame = None
        item_count = 0
        
        for menu_id, name, image_path, price, category, status in filtered_items:
            if category != current_category:
                current_category = category
                item_count = 0
                # Category header - EXACT SAME AS MENU TAB
                category_label = tk.Label(self.menu_frame, text=category, font=("Arial", 18, "bold"), 
                        bg=BACKGROUND_COLOR, fg=TEXT_COLOR)
                category_label.pack(pady=(20, 15), fill="x")
                
                row_frame = tk.Frame(self.menu_frame, bg=BACKGROUND_COLOR)
                row_frame.pack(fill="x", padx=75, pady=60)

            if item_count % 3 == 0:
                row_frame = tk.Frame(self.menu_frame, bg=BACKGROUND_COLOR)
                row_frame.pack(fill="x", padx=55, pady=50)

            # Card with EXACT SAME STRUCTURE as Menu tab
            card = tk.Frame(row_frame, relief="solid", bg=CARD_BG, bd=2, 
                          highlightbackground=BORDER_COLOR, highlightthickness=1)
            card.pack(side="left", fill="both", expand=True, padx=55, pady=48)
            card.configure(width=380, height=420)
            # MARK AS CARD - EXACT SAME AS MENU TAB
            setattr(card, "is_card", True)

            # Inner frame - EVERYTHING INSIDE CARD STAYS GREEN
            inner_frame = tk.Frame(card, bg=CARD_BG, padx=20, pady=20)
            inner_frame.pack(fill="both", expand=True)

            # Load image
            if image_path not in self.image_cache:
                img_path = image_path if os.path.exists(image_path) else FALLBACK_IMAGE
                try:
                    img = Image.open(img_path)
                    img.thumbnail((200, 200))
                    self.image_cache[image_path] = ImageTk.PhotoImage(img)
                except:
                    self.image_cache[image_path] = None

            content_frame = tk.Frame(inner_frame, bg=CARD_BG)
            content_frame.pack(fill="both", expand=True)

            if self.image_cache.get(image_path):
                img_label = tk.Label(content_frame, image=self.image_cache[image_path], bg=CARD_BG)
                img_label.pack(pady=15)

            info_frame = tk.Frame(content_frame, bg=CARD_BG)
            info_frame.pack(fill="x", pady=25)

            # Name and price - GOLDEN TEXT (INSIDE CARD - STAYS GREEN)
            tk.Label(info_frame, text=name, font=("Arial", 16, "bold"),
                    bg=CARD_BG, fg=TEXT_COLOR, wraplength=300).pack(pady=(10, 6))
            
            tk.Label(info_frame, text=f"BHD {price:.2f}", font=("Arial", 14, "bold"),
                    bg=CARD_BG, fg=TEXT_COLOR).pack(pady=(6, 12))

            bottom_frame = tk.Frame(info_frame, bg=CARD_BG)
            bottom_frame.pack(fill="x", pady=(10, 0))

            # Status badge - INSIDE CARD - STAYS GREEN
            status_color = "#27ae60" if status.lower() == "available" else "#e74c3c"
            status_text = "AVAILABLE" if status.lower() == "available" else "UNAVAILABLE"
            
            status_label = tk.Label(
                bottom_frame,
                text=status_text,
                bg=status_color,
                fg="white",
                font=("Arial", 11, "bold"),
                padx=22,
                pady=7,
                relief="raised",
                bd=2
            )
            status_label.pack(side="left", padx=(0, 15))

            # Add to Cart button (only if available) - INSIDE CARD - STAYS GREEN
            if status.lower() == "available":
                ttk.Button(bottom_frame, text="Add to Cart", 
                          command=lambda mid=menu_id: self.add_to_cart(mid),
                          style="Custom.TButton").pack(side="right")

            item_count += 1

        # Fill remaining spaces in the last row - EXACT SAME AS MENU TAB
        remaining_items = item_count % 3
        if remaining_items > 0 and row_frame:
            for _ in range(3 - remaining_items):
                filler = tk.Frame(row_frame, bg=BACKGROUND_COLOR)
                filler.pack(side="left", fill="both", expand=True, padx=40, pady=40)

        # CALL NUCLEAR ROUTINE - EXACT SAME AS MENU TAB
        self.after(200, self._nuclear_force_green_cards)

    def add_to_cart(self, menu_id):
        """Add item to cart"""
        item = next((i for i in self.menu_items if i[0]==menu_id), None)
        if not item:
            return
        _, name, _, price, _, _ = item
        if menu_id in self.cart:
            self.cart[menu_id]['qty'] += 1
        else:
            self.cart[menu_id] = {'name': name, 'price': price, 'qty': 1, 'menu_id': menu_id}

        self.update_cart_btn()

    def show_cart(self):
        """Show cart window"""
        if not self.cart:
            messagebox.showinfo("Cart", "Cart is empty!")
            return

        win = tk.Toplevel(self)
        win.title("Order Cart")
        win.geometry("500x600")
        win.configure(bg=BACKGROUND_COLOR)
        self.center_window(win)  # CENTER THE CART WINDOW

        # Title - GOLDEN TEXT
        tk.Label(win, text="🛒 Shopping Cart", font=("Arial", 18, "bold"), 
                bg=BACKGROUND_COLOR, fg=TEXT_COLOR).pack(pady=10)

        # Items frame
        items_frame = tk.Frame(win, bg=BACKGROUND_COLOR)
        items_frame.pack(fill="both", expand=True, padx=20, pady=10)

        total_var = tk.DoubleVar(value=0.0)

        def update_total():
            total = sum(v['price']*v['qty'] for v in self.cart.values())
            total_var.set(total)
            self.update_cart_btn()

        # Display cart items
        for menu_id, info in list(self.cart.items()):
            frame = tk.Frame(items_frame, bg=CARD_BG, relief="solid", bd=1, padx=10, pady=8)
            frame.pack(fill="x", pady=5)

            # Item info - GOLDEN TEXT
            tk.Label(frame, text=info['name'], bg=CARD_BG, fg=TEXT_COLOR, 
                    font=("Arial", 11, 'bold')).pack(side="left")
            
            qty_label = tk.Label(frame, text=str(info['qty']), bg=CARD_BG, fg=TEXT_COLOR,
                               width=3, font=("Arial", 11, 'bold'))
            qty_label.pack(side="left", padx=10)
            
            tk.Label(frame, text=f"BHD {info['price']*info['qty']:.2f}", 
                    bg=CARD_BG, fg=TEXT_COLOR, font=("Arial", 11)).pack(side="left", padx=5)

            # Quantity controls
            btn_frame = tk.Frame(frame, bg=CARD_BG)
            btn_frame.pack(side="right")

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

            ttk.Button(btn_frame, text="+", command=plus, width=3, style="Custom.TButton").pack(side="left", padx=2)
            ttk.Button(btn_frame, text="-", command=minus, width=3, style="Custom.TButton").pack(side="left", padx=2)

        # Total price - GOLDEN TEXT
        total_frame = tk.Frame(win, bg=BACKGROUND_COLOR)
        total_frame.pack(fill="x", pady=10, padx=20)
        
        tk.Label(total_frame, text="Total:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR,
                font=("Arial", 14, 'bold')).pack(side="left")
        tk.Label(total_frame, textvariable=total_var, bg=BACKGROUND_COLOR, fg=TEXT_COLOR,
                font=("Arial", 14, 'bold')).pack(side="left", padx=10)
        update_total()

        # Customer Info Fields - GOLDEN TEXT
        cust_frame = tk.Frame(win, bg=BACKGROUND_COLOR)
        cust_frame.pack(fill="x", pady=15, padx=20)

        tk.Label(cust_frame, text="Customer Name:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR).grid(row=0, column=0, sticky="w", pady=5)
        customer_name_var = tk.StringVar()
        ttk.Entry(cust_frame, textvariable=customer_name_var, style="Custom.TEntry").grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        tk.Label(cust_frame, text="Customer Phone:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR).grid(row=1, column=0, sticky="w", pady=5)
        customer_phone_var = tk.StringVar()
        ttk.Entry(cust_frame, textvariable=customer_phone_var, style="Custom.TEntry").grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        cust_frame.columnconfigure(1, weight=1)

        # Payment buttons
        btn_frame = tk.Frame(win, bg=BACKGROUND_COLOR)
        btn_frame.pack(pady=15)
        
        ttk.Button(
            btn_frame,
            text="💳 Pay by Card",
            command=lambda: self.pay_by_card(win, customer_name_var.get(), customer_phone_var.get(), list(self.cart.values())),
            style="Custom.TButton"
        ).pack(side="left", padx=8)
        
        ttk.Button(
            btn_frame,
            text="💵 Pay by Cash",
            command=lambda: self.pay_by_cash(win, customer_name_var.get(), customer_phone_var.get(), list(self.cart.values())),
            style="Custom.TButton"
        ).pack(side="left", padx=8)

    def pay_by_card(self, cart_window, cust_name, cust_phone, cart_items):
        """Process card payment - FULL VERSION WITH DATABASE"""
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

        try:
            # Create customer
            cursor.execute("INSERT INTO customer (customer_name, phone) VALUES (%s, %s)", (cust_name, cust_phone))
            customer_id = cursor.lastrowid

            # Create order with kitchen_status
            cursor.execute("INSERT INTO orders (customer_id, total_price, order_date, kitchen_status) VALUES (%s, %s, %s, %s)",
                        (customer_id, total_price, datetime.now(), "Received"))
            order_id = cursor.lastrowid

            # Insert order items
            for item in cart_items:
                cursor.execute("INSERT INTO order_items (order_id, menu_id, qty, price) VALUES (%s, %s, %s, %s)",
                            (order_id, item['menu_id'], item['qty'], item['price']))

            conn.commit()
            
            # Clear cart
            self.cart.clear()
            self.update_cart_btn()

            # Card Payment Window
            win = tk.Toplevel()
            win.title("Card Payment")
            win.geometry("500x650")
            win.configure(bg=BACKGROUND_COLOR)
            self.center_window(win)  # CENTER THE PAYMENT WINDOW

            # Title - GOLDEN TEXT
            tk.Label(win, text="💳 Card Payment", font=("Arial", 20, "bold"), 
                    bg=BACKGROUND_COLOR, fg=TEXT_COLOR).pack(pady=15)

            # Payment form
            form_frame = tk.Frame(win, bg=BACKGROUND_COLOR)
            form_frame.pack(fill="both", expand=True, padx=20, pady=10)

            # Card Number
            tk.Label(form_frame, text="Card Number:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR, 
                    font=("Arial", 11)).grid(row=0, column=0, sticky="w", pady=8)
            card_number_var = tk.StringVar()
            ttk.Entry(form_frame, textvariable=card_number_var, style="Custom.TEntry", 
                     font=("Arial", 11)).grid(row=0, column=1, sticky="ew", padx=10, pady=8)

            # Cardholder Name
            tk.Label(form_frame, text="Cardholder Name:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR,
                    font=("Arial", 11)).grid(row=1, column=0, sticky="w", pady=8)
            card_name_var = tk.StringVar()
            ttk.Entry(form_frame, textvariable=card_name_var, style="Custom.TEntry",
                     font=("Arial", 11)).grid(row=1, column=1, sticky="ew", padx=10, pady=8)

            # Security Code
            tk.Label(form_frame, text="Security Code:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR,
                    font=("Arial", 11)).grid(row=2, column=0, sticky="w", pady=8)
            cvv_var = tk.StringVar()
            ttk.Entry(form_frame, textvariable=cvv_var, style="Custom.TEntry",
                     font=("Arial", 11)).grid(row=2, column=1, sticky="ew", padx=10, pady=8)

            # Expiry Date
            tk.Label(form_frame, text="Expiry Date (MM/YY):", bg=BACKGROUND_COLOR, fg=TEXT_COLOR,
                    font=("Arial", 11)).grid(row=3, column=0, sticky="w", pady=8)
            expiry_var = tk.StringVar()
            ttk.Entry(form_frame, textvariable=expiry_var, style="Custom.TEntry",
                     font=("Arial", 11)).grid(row=3, column=1, sticky="ew", padx=10, pady=8)

            # Employee ID
            tk.Label(form_frame, text="Employee ID:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR,
                    font=("Arial", 11)).grid(row=4, column=0, sticky="w", pady=8)
            emp_id_var = tk.IntVar()
            ttk.Entry(form_frame, textvariable=emp_id_var, style="Custom.TEntry",
                     font=("Arial", 11)).grid(row=4, column=1, sticky="ew", padx=10, pady=8)

            form_frame.columnconfigure(1, weight=1)

            # Amount to pay
            amount_frame = tk.Frame(win, bg=BACKGROUND_COLOR)
            amount_frame.pack(pady=15)
            tk.Label(amount_frame, text=f"Amount to Pay: BHD {total_price:.2f}", 
                    font=("Arial", 16, "bold"), bg=BACKGROUND_COLOR, fg=TEXT_COLOR).pack()

            def process_payment():
                if not all([card_number_var.get(), card_name_var.get(), cvv_var.get(), expiry_var.get(), emp_id_var.get()]):
                    messagebox.showerror("Error", "Please fill all fields!")
                    return

                # Fetch employee name from employee ID
                cursor.execute("SELECT name FROM employees WHERE employee_id = %s", (emp_id_var.get(),))
                result = cursor.fetchone()
                if not result:
                    messagebox.showerror("Error", "Employee ID not found!")
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

                # Display Receipt
                for widget in win.winfo_children():
                    widget.destroy()

                win.configure(bg=BACKGROUND_COLOR)
                self.center_window(win)  # CENTER THE RECEIPT WINDOW
                
                # Receipt content
                tk.Label(win, text="🎉 PAYMENT SUCCESSFUL!", font=("Arial", 18, "bold"), 
                        bg=BACKGROUND_COLOR, fg="#27ae60").pack(pady=10)
                tk.Label(win, text="*** BILL RECEIPT ***", font=("Arial", 14, "bold"), 
                        bg=BACKGROUND_COLOR, fg=TEXT_COLOR).pack(pady=5)
                
                receipt_frame = tk.Frame(win, bg=BACKGROUND_COLOR)
                receipt_frame.pack(fill="both", expand=True, padx=20, pady=10)
                
                tk.Label(receipt_frame, text=f"Bill ID: {bill_id}", 
                        bg=BACKGROUND_COLOR, fg=TEXT_COLOR, font=("Arial", 11)).pack(anchor="w")
                tk.Label(receipt_frame, text=f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
                        bg=BACKGROUND_COLOR, fg=TEXT_COLOR, font=("Arial", 11)).pack(anchor="w")
                tk.Label(receipt_frame, text=f"Customer: {cust_name}", 
                        bg=BACKGROUND_COLOR, fg=TEXT_COLOR, font=("Arial", 11)).pack(anchor="w")
                tk.Label(receipt_frame, text=f"Employee: {emp_name} (ID: {emp_id_var.get()})", 
                        bg=BACKGROUND_COLOR, fg=TEXT_COLOR, font=("Arial", 11)).pack(anchor="w")
                tk.Label(receipt_frame, text="─" * 40, 
                        bg=BACKGROUND_COLOR, fg=TEXT_COLOR).pack(pady=5)

                for item in cart_items:
                    item_total = item['qty'] * item['price']
                    tk.Label(receipt_frame, 
                            text=f"{item['name']} x {item['qty']} @ BHD {item['price']:.2f} = BHD {item_total:.2f}",
                            bg=BACKGROUND_COLOR, fg=TEXT_COLOR, font=("Arial", 10)).pack(anchor="w")

                tk.Label(receipt_frame, text="─" * 40, 
                        bg=BACKGROUND_COLOR, fg=TEXT_COLOR).pack(pady=5)
                tk.Label(receipt_frame, text=f"Total Amount: BHD {total_price:.2f}", 
                        font=("Arial", 12, "bold"), bg=BACKGROUND_COLOR, fg=TEXT_COLOR).pack(anchor="w")
                tk.Label(receipt_frame, text=f"Payment Method: Card", 
                        bg=BACKGROUND_COLOR, fg=TEXT_COLOR, font=("Arial", 11)).pack(anchor="w")
                tk.Label(receipt_frame, text=f"Order #{order_id} sent to kitchen! ✅", 
                        font=("Arial", 11, "bold"), bg=BACKGROUND_COLOR, fg="#27ae60").pack(anchor="w", pady=10)

                ttk.Button(win, text="Close", command=win.destroy, style="Custom.TButton").pack(pady=15)

            ttk.Button(win, text="Pay Now", command=process_payment, style="Custom.TButton", 
                      width=15).pack(pady=20)

        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to create order: {str(e)}")
            conn.rollback()
            conn.close()

    def pay_by_cash(self, cart_window, cust_name, cust_phone, cart_items):
        """Process cash payment - FULL VERSION WITH DATABASE"""
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

        try:
            # Create customer
            cursor.execute("INSERT INTO customer (customer_name, phone) VALUES (%s, %s)", (cust_name, cust_phone))
            customer_id = cursor.lastrowid

            # Create order with kitchen_status
            cursor.execute("INSERT INTO orders (customer_id, total_price, order_date, kitchen_status) VALUES (%s, %s, %s, %s)",
                        (customer_id, total_price, datetime.now(), "Received"))
            order_id = cursor.lastrowid

            # Insert order items
            for item in cart_items:
                cursor.execute("INSERT INTO order_items (order_id, menu_id, qty, price) VALUES (%s, %s, %s, %s)",
                            (order_id, item['menu_id'], item['qty'], item['price']))

            conn.commit()
            
            # Clear cart
            self.cart.clear()
            self.update_cart_btn()

            # Cash Payment Window
            win = tk.Toplevel()
            win.title("Cash Payment")
            win.geometry("400x400")
            win.configure(bg=BACKGROUND_COLOR)
            self.center_window(win)  # CENTER THE PAYMENT WINDOW

            # Title - GOLDEN TEXT
            tk.Label(win, text="💵 Cash Payment", font=("Arial", 18, "bold"), 
                    bg=BACKGROUND_COLOR, fg=TEXT_COLOR).pack(pady=15)

            content_frame = tk.Frame(win, bg=BACKGROUND_COLOR)
            content_frame.pack(fill="both", expand=True, padx=20, pady=10)

            tk.Label(content_frame, text="Employee ID:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR,
                    font=("Arial", 11)).pack(anchor="w", pady=8)
            emp_id_var = tk.IntVar()
            ttk.Entry(content_frame, textvariable=emp_id_var, style="Custom.TEntry",
                     font=("Arial", 11)).pack(fill="x", pady=8)

            tk.Label(content_frame, text=f"Amount to Pay: BHD {total_price:.2f}", 
                    font=("Arial", 14, "bold"), bg=BACKGROUND_COLOR, fg=TEXT_COLOR).pack(pady=15)

            def payment_received():
                if not emp_id_var.get():
                    messagebox.showerror("Error", "Please enter employee ID!")
                    return

                # Fetch employee name from employee ID
                cursor.execute("SELECT name FROM employees WHERE employee_id = %s", (emp_id_var.get(),))
                result = cursor.fetchone()
                if not result:
                    messagebox.showerror("Error", "Employee ID not found!")
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

                # Display Receipt
                for widget in win.winfo_children():
                    widget.destroy()

                win.configure(bg=BACKGROUND_COLOR)
                self.center_window(win)  # CENTER THE RECEIPT WINDOW
                
                tk.Label(win, text="💰 CASH PAYMENT RECEIVED", font=("Arial", 16, "bold"), 
                        bg=BACKGROUND_COLOR, fg=TEXT_COLOR).pack(pady=10)
                tk.Label(win, text="*** BILL RECEIPT ***", font=("Arial", 12, "bold"), 
                        bg=BACKGROUND_COLOR, fg=TEXT_COLOR).pack(pady=5)
                
                receipt_frame = tk.Frame(win, bg=BACKGROUND_COLOR)
                receipt_frame.pack(fill="both", expand=True, padx=20, pady=10)
                
                tk.Label(receipt_frame, text=f"Bill ID: {bill_id}", 
                        bg=BACKGROUND_COLOR, fg=TEXT_COLOR).pack(anchor="w")
                tk.Label(receipt_frame, text=f"Customer: {cust_name}", 
                        bg=BACKGROUND_COLOR, fg=TEXT_COLOR).pack(anchor="w")
                tk.Label(receipt_frame, text=f"Employee: {emp_name}", 
                        bg=BACKGROUND_COLOR, fg=TEXT_COLOR).pack(anchor="w")
                tk.Label(receipt_frame, text=f"Total: BHD {total_price:.2f}", 
                        font=("Arial", 11, "bold"), bg=BACKGROUND_COLOR, fg=TEXT_COLOR).pack(anchor="w")
                tk.Label(receipt_frame, text="Payment Method: Cash", 
                        bg=BACKGROUND_COLOR, fg=TEXT_COLOR).pack(anchor="w")
                tk.Label(receipt_frame, text=f"Order #{order_id} sent to kitchen! ✅", 
                        font=("Arial", 10, "bold"), bg=BACKGROUND_COLOR, fg="#27ae60").pack(anchor="w", pady=10)

                ttk.Button(win, text="Close", command=win.destroy, style="Custom.TButton").pack(pady=15)

            ttk.Button(win, text="Payment Received", command=payment_received, 
                      style="Custom.TButton").pack(pady=20)

        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to create order: {str(e)}")
            conn.rollback()
            conn.close()


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1200x800")
    app = PosTab(root)
    app.pack(fill="both", expand=True)
    root.mainloop()