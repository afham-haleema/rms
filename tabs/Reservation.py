import tkinter as tk
from tkinter import ttk, messagebox
from db_connection import db
from datetime import datetime, date

class ReservationTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setup_ui()
        self.load_reservations()

    def setup_ui(self):
        """Setup the reservation interface with input form and display"""
        # Main container
        main_container = tk.Frame(self)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)

        # ===== LEFT SIDE: Input Form =====
        form_frame = tk.LabelFrame(main_container, text="Add New Reservation", font=("Arial", 12, "bold"), padx=15, pady=15)
        form_frame.pack(side="left", fill="y", padx=(0, 10))

        # Customer Name
        tk.Label(form_frame, text="Customer Name:*", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w", pady=8)
        self.name_entry = tk.Entry(form_frame, width=25, font=("Arial", 10))
        self.name_entry.grid(row=0, column=1, pady=8, padx=(10, 0))
        self.name_entry.focus()

        # Phone Number
        tk.Label(form_frame, text="Phone Number:*", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky="w", pady=8)
        self.phone_entry = tk.Entry(form_frame, width=25, font=("Arial", 10))
        self.phone_entry.grid(row=1, column=1, pady=8, padx=(10, 0))

        # Date
        tk.Label(form_frame, text="Date (YYYY-MM-DD):*", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky="w", pady=8)
        self.date_entry = tk.Entry(form_frame, width=25, font=("Arial", 10))
        self.date_entry.grid(row=2, column=1, pady=8, padx=(10, 0))
        # Set today's date as default
        today = date.today().strftime("%Y-%m-%d")
        self.date_entry.insert(0, today)

        # Time
        tk.Label(form_frame, text="Time (HH:MM):*", font=("Arial", 10, "bold")).grid(row=3, column=0, sticky="w", pady=8)
        self.time_entry = tk.Entry(form_frame, width=25, font=("Arial", 10))
        self.time_entry.grid(row=3, column=1, pady=8, padx=(10, 0))
        # Set default time to next hour
        next_hour = (datetime.now().hour + 1) % 24
        self.time_entry.insert(0, f"{next_hour:02d}:00")

        # Number of Guests
        tk.Label(form_frame, text="Number of Guests:*", font=("Arial", 10, "bold")).grid(row=4, column=0, sticky="w", pady=8)
        self.guests_var = tk.StringVar(value="2")
        guests_spinbox = tk.Spinbox(form_frame, from_=1, to=20, width=22, textvariable=self.guests_var, font=("Arial", 10))
        guests_spinbox.grid(row=4, column=1, pady=8, padx=(10, 0))

        # Buttons
        button_frame = tk.Frame(form_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)

        add_btn = tk.Button(button_frame, text="➕ Add Reservation", command=self.add_reservation, 
                           bg="#4CAF50", fg="white", font=("Arial", 11, "bold"), padx=15, pady=8, width=15)
        add_btn.pack(side="left", padx=5)

        clear_btn = tk.Button(button_frame, text="🗑️ Clear Form", command=self.clear_form,
                             bg="#f44336", fg="white", font=("Arial", 11), padx=15, pady=8, width=12)
        clear_btn.pack(side="left", padx=5)

        # Form instructions
        instructions = tk.Label(form_frame, text="* Required fields", font=("Arial", 9), fg="gray")
        instructions.grid(row=6, column=0, columnspan=2, pady=(10, 0))

        # ===== RIGHT SIDE: Reservations Table =====
        table_frame = tk.LabelFrame(main_container, text="Existing Reservations", font=("Arial", 12, "bold"), padx=15, pady=15)
        table_frame.pack(side="right", fill="both", expand=True)

        # Header with refresh button
        header_frame = tk.Frame(table_frame)
        header_frame.pack(fill="x", pady=(0, 10))

        tk.Label(header_frame, text="All Reservations", font=("Arial", 11, "bold")).pack(side="left")
        
        # Action buttons frame
        action_frame = tk.Frame(header_frame)
        action_frame.pack(side="right")
        
        delete_btn = tk.Button(action_frame, text="🗑️ Delete Selected", command=self.delete_reservation,
                              font=("Arial", 10), bg="#dc3545", fg="white", padx=10, pady=4)
        delete_btn.pack(side="left", padx=5)
        
        refresh_btn = tk.Button(action_frame, text="🔄 Refresh", command=self.load_reservations,
                               font=("Arial", 10), bg="#2196F3", fg="white", padx=10, pady=4)
        refresh_btn.pack(side="left", padx=5)

        # Status label
        self.status_label = tk.Label(header_frame, text="Ready", font=("Arial", 9), fg="green")
        self.status_label.pack(side="right", padx=10)

        # Treeview for reservations
        columns = ("res_id", "customer_name", "phone", "date", "time", "guests")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)

        headings = ["ID", "Customer Name", "Phone", "Date", "Time", "Guests"]
        widths = [60, 150, 120, 100, 80, 60]
        
        for col, hd, width in zip(columns, headings, widths):
            self.tree.heading(col, text=hd)
            self.tree.column(col, width=width, anchor="center")

        # Scrollbars
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.tree.pack(fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        
        # Bind double-click to delete
        self.tree.bind("<Double-1>", self.on_double_click)

        # Row styling
        self.tree.tag_configure('today', background='#e8f5e8')
        self.tree.tag_configure('past', background='#ffebee')
        self.tree.tag_configure('future', background='#e3f2fd')

    def on_double_click(self, event):
        """Handle double-click on reservation to delete"""
        item = self.tree.selection()
        if item:
            self.delete_reservation()

    def delete_reservation(self):
        """Delete selected reservation"""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a reservation to delete")
            return
        
        # Get reservation details
        item = selected_item[0]
        values = self.tree.item(item, 'values')
        res_id = values[0]
        customer_name = values[1]
        reservation_date = values[3]
        reservation_time = values[4]
        
        # Confirm deletion
        confirm = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to delete this reservation?\n\n"
            f"Reservation ID: {res_id}\n"
            f"Customer: {customer_name}\n"
            f"Date: {reservation_date}\n"
            f"Time: {reservation_time}"
        )
        
        if not confirm:
            return
        
        try:
            # Delete reservation from database
            query = "DELETE FROM reservation WHERE res_id = %s"
            result = db.execute_query(query, (res_id,))
            
            if result is not None:
                messagebox.showinfo("Success", f"Reservation #{res_id} deleted successfully!")
                self.load_reservations()  # Refresh the table
            else:
                messagebox.showerror("Error", "Failed to delete reservation. Check database connection.")
                
        except Exception as e:
            error_msg = f"Error deleting reservation: {str(e)}"
            print(error_msg)
            messagebox.showerror("Database Error", error_msg)

    def add_reservation(self):
        """Add a new reservation to the database"""
        # Get values from form
        customer_name = self.name_entry.get().strip()
        phone = self.phone_entry.get().strip()
        reservation_date = self.date_entry.get().strip()
        reservation_time = self.time_entry.get().strip()
        guests = self.guests_var.get().strip()

        # Validation
        if not customer_name:
            messagebox.showerror("Error", "Please enter customer name")
            self.name_entry.focus()
            return
        
        if not phone:
            messagebox.showerror("Error", "Please enter phone number")
            self.phone_entry.focus()
            return

        if not reservation_date:
            messagebox.showerror("Error", "Please enter reservation date")
            self.date_entry.focus()
            return

        if not reservation_time:
            messagebox.showerror("Error", "Please enter reservation time")
            self.time_entry.focus()
            return

        # Validate guests
        try:
            guests_int = int(guests)
            if guests_int < 1 or guests_int > 20:
                messagebox.showerror("Error", "Number of guests must be between 1 and 20")
                return
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number for guests")
            return

        # Validate date format
        try:
            datetime.strptime(reservation_date, '%Y-%m-%d')
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Please use YYYY-MM-DD")
            self.date_entry.focus()
            return

        # Validate time format
        try:
            datetime.strptime(reservation_time, '%H:%M')
        except ValueError:
            messagebox.showerror("Error", "Invalid time format. Please use HH:MM")
            self.time_entry.focus()
            return

        try:
            # Insert into database - INCLUDING GUESTS
            query = """
                INSERT INTO reservation (customer_name, phone, date, time, guests)
                VALUES (%s, %s, %s, %s, %s)
            """
            
            result = db.execute_query(query, (customer_name, phone, reservation_date, reservation_time, guests_int))
            
            if result is not None:
                messagebox.showinfo("Success", "Reservation added successfully!")
                self.clear_form()
                self.load_reservations()  # Refresh the table
            else:
                messagebox.showerror("Error", "Failed to add reservation. Check database connection.")
                
        except Exception as e:
            error_msg = f"Error adding reservation: {str(e)}"
            print(error_msg)
            messagebox.showerror("Database Error", error_msg)

    def clear_form(self):
        """Clear the input form"""
        self.name_entry.delete(0, tk.END)
        self.phone_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        today = date.today().strftime("%Y-%m-%d")
        self.date_entry.insert(0, today)
        self.time_entry.delete(0, tk.END)
        next_hour = (datetime.now().hour + 1) % 24
        self.time_entry.insert(0, f"{next_hour:02d}:00")
        self.guests_var.set("2")
        self.name_entry.focus()

    def load_reservations(self):
        """Load reservations from database"""
        self.status_label.config(text="Loading...", fg="blue")
        
        for row in self.tree.get_children():
            self.tree.delete(row)

        try:
            # Use the correct table name and column names - INCLUDING GUESTS
            query = """
                SELECT 
                    res_id, 
                    customer_name, 
                    phone, 
                    date, 
                    time,
                    guests
                FROM reservation 
                ORDER BY date ASC, time ASC
            """
            
            reservations = db.execute_query(query)
            
            if reservations is None:
                self.status_label.config(text="Database error", fg="red")
                self.tree.insert("", "end", values=("Error", "Cannot connect to database", "", "", "", ""))
                return
                
            if reservations:
                self.status_label.config(text=f"Loaded {len(reservations)} reservations", fg="green")
                today = date.today()
                
                for i, reservation in enumerate(reservations):
                    res_id = reservation.get('res_id', '')
                    customer_name = reservation.get('customer_name', '')
                    phone = reservation.get('phone', '')
                    reservation_date = reservation.get('date', '')
                    reservation_time = reservation.get('time', '')
                    guests = reservation.get('guests', 1)  # Get guests count
                    
                    # Format date
                    if isinstance(reservation_date, date):
                        date_str = reservation_date.strftime("%Y-%m-%d")
                        is_today = (reservation_date == today)
                        is_past = (reservation_date < today)
                    else:
                        date_str = str(reservation_date)
                        is_today = False
                        is_past = False
                    
                    # Format time
                    if isinstance(reservation_time, datetime):
                        time_str = reservation_time.strftime("%H:%M")
                    elif reservation_time:
                        time_str = str(reservation_time)
                    else:
                        time_str = ""
                    
                    # Choose tag based on date
                    if is_today:
                        tag = 'today'
                    elif is_past:
                        tag = 'past'
                    else:
                        tag = 'future'
                    
                    self.tree.insert("", "end", values=(
                        res_id, customer_name, phone, date_str, time_str, guests
                    ), tags=(tag,))
            else:
                self.status_label.config(text="No reservations found", fg="orange")
                self.tree.insert("", "end", values=(
                    "No data", "No reservations found", "Add some using the form", "", "", ""
                ))
                
        except Exception as e:
            error_msg = f"Failed to load reservations: {str(e)}"
            self.status_label.config(text="Error loading data", fg="red")
            print(f"DEBUG: {error_msg}")
            self.tree.insert("", "end", values=("Error", "Check console for details", "", "", "", ""))

    def refresh_reservations(self):
        """Refresh the reservations display"""
        self.load_reservations()