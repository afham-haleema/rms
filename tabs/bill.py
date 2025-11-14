import tkinter as tk
from tkinter import ttk
from db_connection import create_connection
from datetime import datetime

class BillTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        tk.Label(self, text="Bills", font=("Arial", 18, 'bold')).pack(pady=10)

        columns = ("bill_id", "customer_name", "order_id", "bill_date", "payment_method",
                   "bill_amount", "name", "status")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=20)

        headings = ["Bill ID", "Customer", "Order ID", "Date/Time", "Payment Method",
                    "Amount (BHD)", "Employee", "Status"]
        for col, hd in zip(columns, headings):
            self.tree.heading(col, text=hd)
            self.tree.column(col, anchor="center", width=120, minwidth=80)

        # Scrollbars
        vsb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(self, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")


        style = ttk.Style()
        style.configure("BillTreeview.Treeview",
                        background="white",
                        foreground="black",
                        rowheight=50,
                        fieldbackground="white")
        style.map("BillTreeview.Treeview",
                background=[('selected', '#124035')])

        style.configure("BillTreeview.Treeview.Heading", font=("Arial", 10, "bold"))

        self.tree.configure(style="BillTreeview.Treeview")

        style.configure("Treeview.Heading", font=("Arial", 10, "bold"))
        style.layout("Treeview", [('Treeview.treearea', {'sticky': 'nswe'})])

        # Add striped rows and borders using tags
        self.tree.tag_configure('oddrow', background='white')
        self.tree.tag_configure('evenrow', background='#f2f2f2')

        self.load_bills()

    def load_bills(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        conn = create_connection()
        cursor = conn.cursor()

        query = """
            SELECT b.bill_id, c.customer_name, b.order_id, b.bill_date, b.payment_method,
                   b.bill_amount, e.name, b.status
            FROM bill b
            JOIN customer c ON b.customer_id = c.customer_id
            JOIN employees e ON b.employee_id = e.employee_id
            WHERE b.status = 'Paid'
            ORDER BY b.bill_date DESC
        """
        cursor.execute(query)
        bills = cursor.fetchall()
        conn.close()

        for i, bill in enumerate(bills):
            bill_id, cust_name, order_id, bill_date, payment_method, amount, emp_name, status = bill
            bill_date_str = bill_date.strftime("%Y-%m-%d %H:%M:%S") if isinstance(bill_date, datetime) else str(bill_date)
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            self.tree.insert("", "end", values=(bill_id, cust_name, order_id, bill_date_str,
                                                payment_method, f"{amount:.2f}", emp_name, status),
                             tags=(tag,))
