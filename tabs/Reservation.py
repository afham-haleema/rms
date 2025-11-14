import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date
from db_connection import db

class ReservationTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setup_ui()
        self.load_reservations()

    def setup_ui(self):
        """Setup the reservation interface with input form and display"""
        self.configure(bg="#000000")
        
        # Main container
        main_container = tk.Frame(self, bg="#000000")
        main_container.pack(fill="both", expand=True, padx=10, pady=10)

        # ===== LEFT SIDE: Input Form =====
        form_frame = tk.LabelFrame(main_container, text="Add New Reservation", 
                                 font=("Arial", 12, "bold"), padx=15, pady=15,
                                 bg="#1a1a1a", fg="#ebcd95", relief="ridge", bd=2)
        form_frame.pack(side="left", fill="y", padx=(0, 10))

        # Customer Name
        tk.Label(form_frame, text="Customer Name:*", font=("Arial", 10, "bold"), 
                bg="#1a1a1a", fg="#ebcd95").grid(row=0, column=0, sticky="w", pady=8)
        self.name_entry = tk.Entry(form_frame, width=25, font=("Arial", 10), 
                                 bg="#2d2015", fg="#ebcd95", insertbackground="#ebcd95")
        self.name_entry.grid(row=0, column=1, pady=8, padx=(10, 0))
        self.name_entry.focus()

        # Phone Number
        tk.Label(form_frame, text="Phone Number:*", font=("Arial", 10, "bold"), 
                bg="#1a1a1a", fg="#ebcd95").grid(row=1, column=0, sticky="w", pady=8)
        self.phone_entry = tk.Entry(form_frame, width=25, font=("Arial", 10),
                                  bg="#2d2015", fg="#ebcd95", insertbackground="#ebcd95")
        self.phone_entry.grid(row=1, column=1, pady=8, padx=(10, 0))

        # Date
        tk.Label(form_frame, text="Date (YYYY-MM-DD):*", font=("Arial", 10, "bold"), 
                bg="#1a1a1a", fg="#ebcd95").grid(row=2, column=0, sticky="w", pady=8)
        self.date_entry = tk.Entry(form_frame, width=25, font=("Arial", 10),
                                 bg="#2d2015", fg="#ebcd95", insertbackground="#ebcd95")
        self.date_entry.grid(row=2, column=1, pady=8, padx=(10, 0))
        today = date.today().strftime("%Y-%m-%d")
        self.date_entry.insert(0, today)

        # Time
        tk.Label(form_frame, text="Time (HH:MM):*", font=("Arial", 10, "bold"), 
                bg="#1a1a1a", fg="#ebcd95").grid(row=3, column=0, sticky="w", pady=8)
        self.time_entry = tk.Entry(form_frame, width=25, font=("Arial", 10),
                                 bg="#2d2015", fg="#ebcd95", insertbackground="#ebcd95")
        self.time_entry.grid(row=3, column=1, pady=8, padx=(10, 0))
        next_hour = (datetime.now().hour + 1) % 24
        self.time_entry.insert(0, f"{next_hour:02d}:00")

        # Number of Guests
        tk.Label(form_frame, text="Number of Guests:*", font=("Arial", 10, "bold"), 
                bg="#1a1a1a", fg="#ebcd95").grid(row=4, column=0, sticky="w", pady=8)
        self.guests_var = tk.StringVar(value="2")
        guests_spinbox = tk.Spinbox(form_frame, from_=1, to=20, width=22, 
                                  textvariable=self.guests_var, font=("Arial", 10),
                                  bg="#2d2015", fg="#ebcd95", buttonbackground="#124035")
        guests_spinbox.grid(row=4, column=1, pady=8, padx=(10, 0))

        # Buttons
        button_frame = tk.Frame(form_frame, bg="#1a1a1a")
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)

        add_btn = tk.Button(button_frame, text="➕ Add Reservation", command=self.add_reservation, 
                           bg="#124035", fg="#ebcd95", font=("Arial", 11, "bold"), 
                           padx=15, pady=8, width=15, relief="raised", bd=2)
        add_btn.pack(side="left", padx=5)

        clear_btn = tk.Button(button_frame, text="🗑️ Clear Form", command=self.clear_form,
                             bg="#124035", fg="#ebcd95", font=("Arial", 11), 
                             padx=15, pady=8, width=12, relief="raised", bd=2)
        clear_btn.pack(side="left", padx=5)

        # ===== RIGHT SIDE: Reservations Table =====
        table_frame = tk.LabelFrame(main_container, text="Existing Reservations", 
                                  font=("Arial", 12, "bold"), padx=15, pady=15,
                                  bg="#1a1a1a", fg="#ebcd95", relief="ridge", bd=2)
        table_frame.pack(side="right", fill="both", expand=True)

        # Header with buttons
        header_frame = tk.Frame(table_frame, bg="#1a1a1a")
        header_frame.pack(fill="x", pady=(0, 10))

        tk.Label(header_frame, text="All Reservations", font=("Arial", 11, "bold"), 
                bg="#1a1a1a", fg="#ebcd95").pack(side="left")
        
        action_frame = tk.Frame(header_frame, bg="#1a1a1a")
        action_frame.pack(side="right")
        
        
        edit_btn = tk.Button(action_frame, text="✏️ Edit", command=self.edit_reservation,
                           font=("Arial", 10), bg="#124035", fg="#ebcd95", 
                           padx=10, pady=4, relief="raised", bd=2)
        edit_btn.pack(side="left", padx=5)
        
        delete_btn = tk.Button(action_frame, text="🗑️ Delete", command=self.delete_reservation,
                              font=("Arial", 10), bg="#124035", fg="#ebcd95",
                              padx=10, pady=4, relief="raised", bd=2)
        delete_btn.pack(side="left", padx=5)

        # Status label
        self.status_label = tk.Label(header_frame, text="Ready", font=("Arial", 9), 
                                   bg="#1a1a1a", fg="#124035")
        self.status_label.pack(side="right", padx=10)

        # Treeview for reservations
        style = ttk.Style()
        style.configure("Treeview", background="#2d2015", fieldbackground="#2d2015", foreground="#ebcd95")
        style.configure("Treeview.Heading", background="#124035", foreground="#ebcd95", font=('Arial', 10, 'bold'))
        
        columns = ("res_id", "customer_name", "phone", "time", "date", "guests")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)

        headings = ["ID", "Customer Name", "Phone", "Time", "Date", "Guests"]
        widths = [60, 150, 120, 80, 100, 60]
        
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
        
        # Bind double-click to edit
        self.tree.bind("<Double-1>", self.on_double_click)

    def on_double_click(self, event):
        """Handle double-click on reservation to edit"""
        item = self.tree.selection()
        if item:
            self.edit_reservation()

    def edit_reservation(self):
        """Edit selected reservation"""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a reservation to edit")
            return
        
        # Get reservation details
        item = selected_item[0]
        values = self.tree.item(item, 'values')
        
        if not values or values[0] == "No data" or values[0] == "Error":
            messagebox.showwarning("Warning", "Please select a valid reservation to edit")
            return
            
        res_id = values[0]
        customer_name = values[1]
        phone = values[2]
        reservation_time = values[3]
        reservation_date = values[4]
        guests = values[5]
        
        # Create edit window
        edit_win = tk.Toplevel(self)
        edit_win.title(f"Edit Reservation #{res_id}")
        edit_win.geometry("450x400")
        edit_win.configure(bg="#000000")
        edit_win.resizable(False, False)
        
        # Center the window
        edit_win.transient(self)
        edit_win.grab_set()
        
        # Center on screen
        edit_win.update_idletasks()
        x = (edit_win.winfo_screenwidth() // 2) - (450 // 2)
        y = (edit_win.winfo_screenheight() // 2) - (400 // 2)
        edit_win.geometry(f"+{x}+{y}")
        
        # Main container for the edit form - USE FRAME WITH grid
        main_frame = tk.Frame(edit_win, padx=20, pady=20, bg="#000000")
        main_frame.pack(fill="both", expand=True)
        
        # Title - use pack for the title
        title_label = tk.Label(main_frame, text=f"Edit Reservation #{res_id}", 
                              font=("Arial", 14, "bold"), bg="#000000", fg="#ebcd95")
        title_label.pack(pady=(0, 20))
        
        # Form container - use a separate frame for the form with grid
        form_frame = tk.Frame(main_frame, bg="#000000")
        form_frame.pack(fill="both", expand=True, pady=10)
        
        # Customer Name
        tk.Label(form_frame, text="Customer Name:*", font=("Arial", 10, "bold"), 
                bg="#000000", fg="#ebcd95").grid(row=0, column=0, sticky="w", pady=8, padx=(0, 10))
        edit_name_entry = tk.Entry(form_frame, width=25, font=("Arial", 10), 
                                 bg="#2d2015", fg="#ebcd95", insertbackground="#ebcd95")
        edit_name_entry.grid(row=0, column=1, pady=8, sticky="w")
        edit_name_entry.insert(0, customer_name)
        edit_name_entry.focus()

        # Phone Number
        tk.Label(form_frame, text="Phone Number:*", font=("Arial", 10, "bold"), 
                bg="#000000", fg="#ebcd95").grid(row=1, column=0, sticky="w", pady=8, padx=(0, 10))
        edit_phone_entry = tk.Entry(form_frame, width=25, font=("Arial", 10), 
                                  bg="#2d2015", fg="#ebcd95", insertbackground="#ebcd95")
        edit_phone_entry.grid(row=1, column=1, pady=8, sticky="w")
        edit_phone_entry.insert(0, phone)

        # Date
        tk.Label(form_frame, text="Date (YYYY-MM-DD):*", font=("Arial", 10, "bold"), 
                bg="#000000", fg="#ebcd95").grid(row=2, column=0, sticky="w", pady=8, padx=(0, 10))
        edit_date_entry = tk.Entry(form_frame, width=25, font=("Arial", 10), 
                                 bg="#2d2015", fg="#ebcd95", insertbackground="#ebcd95")
        edit_date_entry.grid(row=2, column=1, pady=8, sticky="w")
        edit_date_entry.insert(0, reservation_date)

        # Time
        tk.Label(form_frame, text="Time (HH:MM):*", font=("Arial", 10, "bold"), 
                bg="#000000", fg="#ebcd95").grid(row=3, column=0, sticky="w", pady=8, padx=(0, 10))
        edit_time_entry = tk.Entry(form_frame, width=25, font=("Arial", 10), 
                                 bg="#2d2015", fg="#ebcd95", insertbackground="#ebcd95")
        edit_time_entry.grid(row=3, column=1, pady=8, sticky="w")
        edit_time_entry.insert(0, reservation_time)

        # Number of Guests
        tk.Label(form_frame, text="Number of Guests:*", font=("Arial", 10, "bold"), 
                bg="#000000", fg="#ebcd95").grid(row=4, column=0, sticky="w", pady=8, padx=(0, 10))
        edit_guests_var = tk.StringVar(value=guests)
        edit_guests_spinbox = tk.Spinbox(form_frame, from_=1, to=20, width=22, 
                                       textvariable=edit_guests_var, font=("Arial", 10),
                                       bg="#2d2015", fg="#ebcd95", buttonbackground="#124035")
        edit_guests_spinbox.grid(row=4, column=1, pady=8, sticky="w")

        # Buttons frame - use pack for buttons
        button_frame = tk.Frame(main_frame, bg="#000000")
        button_frame.pack(pady=20)
        
        save_btn = tk.Button(button_frame, text="💾 Save Changes", 
                           command=lambda: self.save_edited_reservation(
                               res_id, edit_name_entry.get(), edit_phone_entry.get(), 
                               edit_date_entry.get(), edit_time_entry.get(), edit_guests_var.get(), edit_win),
                           bg="#124035", fg="#ebcd95", font=("Arial", 11, "bold"), 
                           padx=15, pady=8, relief="raised", bd=2)
        save_btn.pack(side="left", padx=10)

        cancel_btn = tk.Button(button_frame, text="❌ Cancel", 
                             command=edit_win.destroy,
                             bg="#124035", fg="#ebcd95", font=("Arial", 11), 
                             padx=15, pady=8, relief="raised", bd=2)
        cancel_btn.pack(side="left", padx=10)

    def save_edited_reservation(self, res_id, customer_name, phone, reservation_date, reservation_time, guests, edit_win):
        """Save the edited reservation to database"""
        # Validation
        if not customer_name:
            messagebox.showerror("Error", "Please enter customer name")
            return
        
        if not phone:
            messagebox.showerror("Error", "Please enter phone number")
            return

        if not reservation_date:
            messagebox.showerror("Error", "Please enter reservation date")
            return

        if not reservation_time:
            messagebox.showerror("Error", "Please enter reservation time")
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
            return

        # Validate time format
        try:
            datetime.strptime(reservation_time, '%H:%M')
        except ValueError:
            messagebox.showerror("Error", "Invalid time format. Please use HH:MM")
            return

        try:
            # Update reservation in database
            query = """
                UPDATE reservation 
                SET customer_name = %s, phone = %s, date = %s, time = %s, guests = %s
                WHERE res_id = %s
            """
            
            result = db.execute_query(query, (customer_name, phone, reservation_date, reservation_time, guests_int, res_id))
            
            if result is not None:
                messagebox.showinfo("Success", f"Reservation #{res_id} updated successfully!")
                edit_win.destroy()
                self.load_reservations()  # Refresh the table
            else:
                messagebox.showerror("Error", "Failed to update reservation. Check database connection.")
                
        except Exception as e:
            error_msg = f"Error updating reservation: {str(e)}"
            print(error_msg)
            messagebox.showerror("Database Error", error_msg)

    def delete_reservation(self):
        """Delete selected reservation from database"""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a reservation to delete")
            return
        
        # Get reservation details
        item = selected_item[0]
        values = self.tree.item(item, 'values')
        
        if not values or values[0] == "No data" or values[0] == "Error":
            messagebox.showwarning("Warning", "Please select a valid reservation to delete")
            return
            
        res_id = values[0]
        customer_name = values[1]
        reservation_date = values[4]
        reservation_time = values[3]
        
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
            # Delete from database
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
            # Insert into database
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
        self.status_label.config(text="Loading...", fg="#124035")
        
        for row in self.tree.get_children():
            self.tree.delete(row)

        try:
            # Get data from database
            query = """
                SELECT 
                    res_id, 
                    customer_name, 
                    phone, 
                    time,
                    date,
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
                self.status_label.config(text=f"Loaded {len(reservations)} reservations", fg="#124035")
                
                for reservation in reservations:
                    res_id = reservation.get('res_id', '')
                    customer_name = reservation.get('customer_name', '')
                    phone = reservation.get('phone', '')
                    reservation_time = reservation.get('time', '')
                    reservation_date = reservation.get('date', '')
                    guests = reservation.get('guests', 1)
                    
                    # Format time to remove seconds if present
                    if reservation_time and ':' in str(reservation_time):
                        time_parts = str(reservation_time).split(':')
                        if len(time_parts) >= 2:
                            reservation_time = f"{time_parts[0]}:{time_parts[1]}"
                    
                    # Format date if needed
                    if isinstance(reservation_date, date):
                        reservation_date = reservation_date.strftime("%Y-%m-%d")
                    else:
                        reservation_date = str(reservation_date)
                    
                    self.tree.insert("", "end", values=(
                        res_id, customer_name, phone, reservation_time, reservation_date, guests
                    ))
            else:
                self.status_label.config(text="No reservations found", fg="#124035")
                self.tree.insert("", "end", values=(
                    "No data", "No reservations found", "Add some using the form", "", "", ""
                ))
                
        except Exception as e:
            error_msg = f"Failed to load reservations: {str(e)}"
            self.status_label.config(text="Error loading data", fg="red")
            print(f"DEBUG: {error_msg}")
            self.tree.insert("", "end", values=("Error", "Check console for details", "", "", "", ""))