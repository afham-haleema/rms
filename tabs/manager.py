import tkinter as tk
from tkinter import ttk, messagebox
from db_connection import create_connection
from datetime import datetime

class ManagerTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.configure(bg="#23170e")  # Dark brown background

        # Password Frame - Centered and styled
        self.password_frame = tk.Frame(self, bg="#ebcd95")  # Dark brown background
        self.password_frame.place(relx=0.5, rely=0.5, anchor="center")  # Center the frame

        # Title
        tk.Label(self.password_frame, text="Manager Access", font=("Arial", 18, "bold"), 
                bg="#23170e", fg="#ebcd95").grid(row=0, column=0, pady=(0, 30))

        # Lock icon
        tk.Label(self.password_frame, text="🔒", font=("Arial", 60), 
                bg="#23170e", fg="#ebcd95").grid(row=1, column=0, pady=(0, 20))

        # Password label
        tk.Label(self.password_frame, text="Enter Password:", font=("Arial", 12), 
                bg="#23170e", fg="#ebcd95").grid(row=2, column=0, pady=(0, 10))

        # Password entry with custom styling
        self.password_var = tk.StringVar()
        
        # Configure entry style
        style = ttk.Style()
        style.configure("Manager.TEntry",
                       fieldbackground="#2d2015",
                       foreground="#ebcd95",
                       borderwidth=2,
                       relief="solid",
                       font=("Arial", 12),
                       padding=10)
        
        self.password_entry = ttk.Entry(self.password_frame, 
                                      textvariable=self.password_var, 
                                      show="*", 
                                      width=25, 
                                      font=("Arial", 12),
                                      style="Manager.TEntry")
        self.password_entry.grid(row=3, column=0, pady=(0, 10), ipady=8)
        self.password_entry.focus()  # Focus on entry when tab opens
        
        # Bind Enter key to submit
        self.password_entry.bind('<Return>', lambda e: self.check_password())
        
        # Style the button to match the theme
        style.configure("Manager.TButton",
                       background="#124035",
                       foreground="#ebcd95",
                       borderwidth=2,
                       relief="raised",
                       font=("Arial", 12, "bold"),
                       padding=10)
        
        style.map("Manager.TButton",
                 background=[('active', '#1a8a5c')],
                 foreground=[('active', '#ebcd95')])
        
        self.submit_btn = ttk.Button(self.password_frame, 
                                   text="Enter Manager Portal", 
                                   command=self.check_password, 
                                   style="Manager.TButton",
                                   width=20)
        self.submit_btn.grid(row=4, column=0, pady=(0, 15))
        
        # Error label
        self.error_label = tk.Label(self.password_frame, text="", 
                                   fg="#e74c3c",  # Red color for errors
                                   font=("Arial", 10, "bold"), 
                                   bg="#23170e")
        self.error_label.grid(row=5, column=0, pady=(0, 10))
        
        # Instructions
        tk.Label(self.password_frame, text="Enter password to access pending bills", 
                font=("Arial", 9), 
                bg="#23170e", fg="#ebcd95", 
                foreground="#888888").grid(row=6, column=0, pady=(10, 0))
        
        self.tree_frame = tk.Frame(self, bg="#23170e")  # Dark brown background

    def check_password(self):
        if self.password_var.get() == "1234":
            self.password_frame.place_forget()  # Use place_forget instead of pack_forget
            self.show_pending_bills()
        else:
            self.error_label.config(text="❌ Wrong password! Try again.")
            self.password_var.set("")  # Clear the entry
            self.password_entry.focus()  # Refocus on entry

    def show_pending_bills(self):
        self.tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("bill_id", "customer_name", "order_id", "bill_date", "payment_method",
                   "bill_amount", "employee", "action")
        self.tree = ttk.Treeview(self.tree_frame, columns=columns, show="headings", height=20)

        # Configure treeview style to match BillTab
        style = ttk.Style()
        style.configure("Manager.Treeview",
                        background="#2d2015",  # Dark background for rows
                        foreground="#ebcd95",  # Golden text
                        rowheight=50,
                        fieldbackground="#2d2015")  # Dark background
        
        style.configure("Manager.Treeview.Heading", 
                       background="#124035",  # Dark green headers
                       foreground="#ebcd95",  # Golden text
                       font=("Arial", 10, "bold"))
        
        style.map("Manager.Treeview",
                 background=[('selected', '#1a8a5c')])  # Darker green when selected

        self.tree.configure(style="Manager.Treeview")

        headings = ["Bill ID", "Customer", "Order ID", "Date/Time", "Payment Method",
                    "Amount (BHD)", "Employee", "Action"]
        for col, hd in zip(columns, headings):
            self.tree.heading(col, text=hd)
            self.tree.column(col, anchor="center", width=120, minwidth=80)

        # Scrollbars with themed colors
        vsb = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(self.tree_frame, orient="horizontal", command=self.tree.xview)
        
        # Style scrollbars
        style.configure("Manager.Vertical.TScrollbar",
                       background="#124035",
                       troughcolor="#23170e",
                       borderwidth=0)
        style.configure("Manager.Horizontal.TScrollbar",
                       background="#124035",
                       troughcolor="#23170e",
                       borderwidth=0)
        
        vsb.configure(style="Manager.Vertical.TScrollbar")
        hsb.configure(style="Manager.Horizontal.TScrollbar")
        
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.pack(fill="both", expand=True, side="left")
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")

        # Style for striped rows
        self.tree.tag_configure('oddrow', background='#2d2015', foreground='#ebcd95')  # Dark brown
        self.tree.tag_configure('evenrow', background='#23170e', foreground='#ebcd95')  # Lighter brown

        # Bind click on Action column
        self.tree.bind("<Button-1>", self.on_tree_click)

        # Load pending bills
        self.load_pending_bills()

    def load_pending_bills(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT b.bill_id, c.customer_name, b.order_id, b.bill_date, b.payment_method,
                   b.bill_amount, e.name, b.status
            FROM bill b
            JOIN customer c ON b.customer_id = c.customer_id
            JOIN employees e ON b.employee_id = e.employee_id
            WHERE b.status = 'Pending'
            ORDER BY b.bill_date ASC
        """)
        self.pending_bills = cursor.fetchall()
        conn.close()

        for i, bill in enumerate(self.pending_bills):
            bill_id, cust_name, order_id, bill_date, payment_method, amount, emp_name, status = bill
            bill_date_str = bill_date.strftime("%Y-%m-%d %H:%M:%S") if isinstance(bill_date, datetime) else str(bill_date)
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'

            # Insert row, set Action column text as "✔"
            self.tree.insert("", "end", iid=str(bill_id),
                             values=(bill_id, cust_name, order_id, bill_date_str,
                                     payment_method, f"{amount:.2f}", emp_name, "✔"),
                             tags=(tag,))

    def on_tree_click(self, event):
        region = self.tree.identify("region", event.x, event.y)
        if region != "cell":
            return

        column = self.tree.identify_column(event.x)
        row_id = self.tree.identify_row(event.y)
        if not row_id:
            return

        col_index = int(column.replace("#", "")) - 1
        if col_index == 7:  # Action column
            self.mark_as_paid(row_id)

    def mark_as_paid(self, bill_id):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE bill SET status='Paid' WHERE bill_id=%s", (bill_id,))
        conn.commit()
        conn.close()

        self.tree.delete(bill_id)
        messagebox.showinfo("Success", f"Bill {bill_id} marked as Paid!")