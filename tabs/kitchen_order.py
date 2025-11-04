import tkinter as tk
from tkinter import ttk, messagebox
from db_connection import db
from datetime import datetime

class KitchenTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setup_ui()
        self.load_orders()

    def setup_ui(self):
        """Setup the kitchen interface"""
        # Main container
        main_container = tk.Frame(self)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)

        # Header
        header_frame = tk.Frame(main_container)
        header_frame.pack(fill="x", pady=(0, 10))

        tk.Label(header_frame, text="🍳 Kitchen Orders", font=("Arial", 18, "bold")).pack(side="left")
        
        # Refresh button
        refresh_btn = tk.Button(header_frame, text="🔄 Refresh Orders", command=self.load_orders,
                               font=("Arial", 10), bg="#2196F3", fg="white", padx=10, pady=5)
        refresh_btn.pack(side="right")

        # Status filter
        filter_frame = tk.Frame(main_container)
        filter_frame.pack(fill="x", pady=(0, 10))

        tk.Label(filter_frame, text="Filter by Status:", font=("Arial", 10, "bold")).pack(side="left")
        
        self.status_var = tk.StringVar(value="All")
        statuses = ["All", "Received", "Cooking", "Completed"]
        for status in statuses:
            tk.Radiobutton(filter_frame, text=status, variable=self.status_var, 
                          value=status, command=self.load_orders, font=("Arial", 9)).pack(side="left", padx=10)

        # Orders container
        orders_container = tk.Frame(main_container)
        orders_container.pack(fill="both", expand=True)

        # Pending orders frame
        self.pending_frame = tk.LabelFrame(orders_container, text="🕐 Pending Orders", font=("Arial", 12, "bold"), padx=10, pady=10)
        self.pending_frame.pack(fill="both", expand=True, side="left", padx=(0, 5))

        # Completed orders frame
        self.completed_frame = tk.LabelFrame(orders_container, text="✅ Completed Orders", font=("Arial", 12, "bold"), padx=10, pady=10)
        self.completed_frame.pack(fill="both", expand=True, side="right", padx=(5, 0))

        # Create scrollable frames for both sections
        self.setup_orders_display()

    def setup_orders_display(self):
        """Setup the orders display areas"""
        # Pending orders area
        pending_container = tk.Frame(self.pending_frame)
        pending_container.pack(fill="both", expand=True)

        # Scrollbar for pending orders
        pending_scrollbar = tk.Scrollbar(pending_container)
        pending_scrollbar.pack(side="right", fill="y")

        # Canvas for pending orders
        self.pending_canvas = tk.Canvas(pending_container, yscrollcommand=pending_scrollbar.set, bg="white")
        self.pending_canvas.pack(side="left", fill="both", expand=True)
        pending_scrollbar.config(command=self.pending_canvas.yview)

        # Frame inside canvas for pending orders
        self.pending_orders_frame = tk.Frame(self.pending_canvas, bg="white")
        self.pending_canvas_window = self.pending_canvas.create_window((0, 0), window=self.pending_orders_frame, anchor="nw")

        # Completed orders area
        completed_container = tk.Frame(self.completed_frame)
        completed_container.pack(fill="both", expand=True)

        # Scrollbar for completed orders
        completed_scrollbar = tk.Scrollbar(completed_container)
        completed_scrollbar.pack(side="right", fill="y")

        # Canvas for completed orders
        self.completed_canvas = tk.Canvas(completed_container, yscrollcommand=completed_scrollbar.set, bg="white")
        self.completed_canvas.pack(side="left", fill="both", expand=True)
        completed_scrollbar.config(command=self.completed_canvas.yview)

        # Frame inside canvas for completed orders
        self.completed_orders_frame = tk.Frame(self.completed_canvas, bg="white")
        self.completed_canvas_window = self.completed_canvas.create_window((0, 0), window=self.completed_orders_frame, anchor="nw")

        # Bind canvas configuration to update scroll region
        self.pending_orders_frame.bind("<Configure>", self.on_pending_frame_configure)
        self.completed_orders_frame.bind("<Configure>", self.on_completed_frame_configure)

    def on_pending_frame_configure(self, event):
        """Update scroll region when pending frame size changes"""
        self.pending_canvas.configure(scrollregion=self.pending_canvas.bbox("all"))

    def on_completed_frame_configure(self, event):
        """Update scroll region when completed frame size changes"""
        self.completed_canvas.configure(scrollregion=self.completed_canvas.bbox("all"))

    def load_orders(self):
        """Load orders from database"""
        try:
            # Clear existing orders
            for widget in self.pending_orders_frame.winfo_children():
                widget.destroy()
            for widget in self.completed_orders_frame.winfo_children():
                widget.destroy()

            # Build query based on filter
            status_filter = self.status_var.get()
            
            if status_filter == "All":
                query = """
                    SELECT o.order_id, o.order_date, c.customer_name, 
                           o.kitchen_status, o.total_price,
                           GROUP_CONCAT(CONCAT(m.name, ' (x', oi.qty, ')') SEPARATOR ', ') as items
                    FROM orders o
                    JOIN customer c ON o.customer_id = c.customer_id
                    JOIN order_items oi ON o.order_id = oi.order_id
                    JOIN menu m ON oi.menu_id = m.menu_id
                    WHERE o.kitchen_status != 'Completed' OR o.kitchen_status IS NULL
                    GROUP BY o.order_id
                    ORDER BY o.order_date ASC
                """
                orders = db.execute_query(query)
            else:
                query = """
                    SELECT o.order_id, o.order_date, c.customer_name, 
                           o.kitchen_status, o.total_price,
                           GROUP_CONCAT(CONCAT(m.name, ' (x', oi.qty, ')') SEPARATOR ', ') as items
                    FROM orders o
                    JOIN customer c ON o.customer_id = c.customer_id
                    JOIN order_items oi ON o.order_id = oi.order_id
                    JOIN menu m ON oi.menu_id = m.menu_id
                    WHERE o.kitchen_status = %s
                    GROUP BY o.order_id
                    ORDER BY o.order_date ASC
                """
                orders = db.execute_query(query, (status_filter,))

            # Load completed orders separately
            completed_query = """
                SELECT o.order_id, o.order_date, c.customer_name, 
                       o.kitchen_status, o.total_price,
                       GROUP_CONCAT(CONCAT(m.name, ' (x', oi.qty, ')') SEPARATOR ', ') as items
                FROM orders o
                JOIN customer c ON o.customer_id = c.customer_id
                JOIN order_items oi ON o.order_id = oi.order_id
                JOIN menu m ON oi.menu_id = m.menu_id
                WHERE o.kitchen_status = 'Completed'
                GROUP BY o.order_id
                ORDER BY o.order_date DESC
                LIMIT 20
            """
            completed_orders = db.execute_query(completed_query)

            if orders:
                self.display_orders(orders, self.pending_orders_frame, False)
            else:
                no_orders_label = tk.Label(self.pending_orders_frame, text="No pending orders", 
                                          font=("Arial", 12), fg="gray", pady=20, bg="white")
                no_orders_label.pack()

            if completed_orders:
                self.display_orders(completed_orders, self.completed_orders_frame, True)
            else:
                no_orders_label = tk.Label(self.completed_orders_frame, text="No completed orders", 
                                          font=("Arial", 12), fg="gray", pady=20, bg="white")
                no_orders_label.pack()

        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to load orders: {str(e)}")

    def display_orders(self, orders, parent_frame, is_completed):
        """Display orders in the given frame"""
        for order in orders:
            # Create order frame
            order_frame = tk.Frame(parent_frame, relief="solid", borderwidth=1, padx=10, pady=10, bg="white")
            order_frame.pack(fill="x", pady=5, padx=5)

            # Order header
            header_frame = tk.Frame(order_frame, bg="white")
            header_frame.pack(fill="x")

            tk.Label(header_frame, text=f"Order #{order['order_id']}", 
                    font=("Arial", 12, "bold"), bg="white").pack(side="left")
            
            tk.Label(header_frame, text=f"Customer: {order['customer_name']}", 
                    font=("Arial", 10), bg="white").pack(side="left", padx=(20, 0))

            # Order details
            details_frame = tk.Frame(order_frame, bg="white")
            details_frame.pack(fill="x", pady=5)

            # Format order date
            order_date = order['order_date']
            if isinstance(order_date, datetime):
                date_str = order_date.strftime("%Y-%m-%d %H:%M")
            else:
                date_str = str(order_date)

            tk.Label(details_frame, text=f"Time: {date_str}", font=("Arial", 9), bg="white").pack(anchor="w")
            tk.Label(details_frame, text=f"Items: {order['items']}", font=("Arial", 9), bg="white").pack(anchor="w")
            tk.Label(details_frame, text=f"Total: ${order['total_price']:.2f}", 
                    font=("Arial", 10, "bold"), bg="white").pack(anchor="w")

            # Status and actions
            status_frame = tk.Frame(order_frame, bg="white")
            status_frame.pack(fill="x", pady=(5, 0))

            current_status = order['kitchen_status'] or "Received"
           
            status_color = self.get_status_color(current_status)
            
            status_label = tk.Label(status_frame, text=f"Status: {current_status}", 
                                   font=("Arial", 10, "bold"), fg=status_color, bg="white")
            status_label.pack(side="left")

            if not is_completed:
                self.add_action_buttons(status_frame, order['order_id'], current_status)

    def get_status_color(self, status):
        """Get color for status label"""
        colors = {
            "Received": "red",
            "Cooking": "orange", 
            "Completed": "green"
        }
        return colors.get(status, "black")

    def add_action_buttons(self, parent, order_id, current_status):
        """Add action buttons based on current status"""
        button_frame = tk.Frame(parent, bg="white")
        button_frame.pack(side="right")

        if current_status == "Received":
            start_btn = tk.Button(button_frame, text="Start Cooking", 
                                 command=lambda: self.update_order_status(order_id, "Cooking"),
                                 bg="#4CAF50", fg="white", font=("Arial", 9), padx=10)
            start_btn.pack(side="left", padx=2)

        elif current_status == "Cooking":
            complete_btn = tk.Button(button_frame, text="Mark Complete", 
                                    command=lambda: self.update_order_status(order_id, "Completed"),
                                    bg="#2196F3", fg="white", font=("Arial", 9), padx=10)
            complete_btn.pack(side="left", padx=2)


    def update_order_status(self, order_id, new_status):
        """Update order status in database"""
        try:
            print(f"DEBUG: Updating order {order_id} to status {new_status}")
            
            # Ensure database connection
            if not db.connection or not db.connection.is_connected():
                print("DEBUG: Reconnecting to database...")
                if not db.connect():
                    messagebox.showerror("Error", "Cannot connect to database")
                    return
            
            query = "UPDATE orders SET kitchen_status = %s WHERE order_id = %s"
            print(f"DEBUG: Executing query: {query} with params: ({new_status}, {order_id})")
            
            result = db.execute_query(query, (new_status, order_id))
            print(f"DEBUG: Query result: {result}")
            
            if result is not None:
                messagebox.showinfo("Success", f"Order #{order_id} status updated to {new_status}")
                self.load_orders()  # Refresh the display
            else:
                # Try to get more detailed error
                test_query = "SELECT 1"
                test_result = db.execute_query(test_query)
                if test_result is None:
                    messagebox.showerror("Error", "Database connection lost. Please check your database server.")
                else:
                    messagebox.showerror("Error", "Failed to update order status. The order might not exist.")
                
        except Exception as e:
            error_msg = f"Failed to update order: {str(e)}"
            print(f"DEBUG: Exception: {error_msg}")
            messagebox.showerror("Database Error", error_msg)

    def refresh_orders(self):
        """Refresh orders display"""
        self.load_orders()