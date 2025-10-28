import tkinter as tk
from tkinter import ttk, messagebox
from db_connection import create_connection
from datetime import datetime

class ManagerTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        tk.Label(self, text="Manager", font=("Arial", 18, 'bold')).pack(pady=20)

        # Password Frame
        self.password_frame = tk.Frame(self)
        self.password_frame.pack(pady=50)

        self.password_var = tk.StringVar()

        tk.Label(self.password_frame, text="🔒", font=("Arial", 80)).grid(row=0, column=0, pady=5)
        self.password_entry = ttk.Entry(self.password_frame, textvariable=self.password_var, show="*")
        self.password_entry.grid(row=1, column=0, pady=5)
        self.submit_btn = ttk.Button(self.password_frame, text="Enter", command=self.check_password)
        self.submit_btn.grid(row=2, column=0, pady=10)
        self.error_label = tk.Label(self.password_frame, text="", fg="red", font=("Arial", 10))
        self.error_label.grid(row=3, column=0, pady=5)
        self.tree_frame = tk.Frame(self)

    def check_password(self):
        if self.password_var.get() == "1234":
            self.password_frame.pack_forget()
            self.show_pending_bills()
        else:
            self.error_label.config(text="Wrong password!")

    def show_pending_bills(self):
        self.tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("bill_id", "customer_name", "order_id", "bill_date", "payment_method",
                   "bill_amount", "employee", "action")
        self.tree = ttk.Treeview(self.tree_frame, columns=columns, show="headings", height=20)

        headings = ["Bill ID", "Customer", "Order ID", "Date/Time", "Payment Method",
                    "Amount (BHD)", "Employee", "Action"]
        for col, hd in zip(columns, headings):
            self.tree.heading(col, text=hd)
            self.tree.column(col, anchor="center", width=120, minwidth=80)

        # Scrollbars
        vsb = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(self.tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.pack(fill="both", expand=True, side="left")
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")

        # Style
        self.tree.tag_configure('oddrow', background='white')
        self.tree.tag_configure('evenrow', background='#f2f2f2')
        style = ttk.Style()
        style.configure("BillTreeview.Treeview.Heading", font=("Arial", 10, "bold"))
        style.configure("Treeview", rowheight=50)

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
