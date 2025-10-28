
from datetime import datetime
import os
import shutil
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
from db_connection import create_connection
from ttkbootstrap import Style
from ui.theme import COLORS

FALLBACK_IMAGE = "images/image.png"  # default fallback image

class MenuTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.configure(style="Card.TFrame")
        self.menu_items = []
        self.image_cache = {}

        # ===== Top Search + Add Button Bar =====
        top_frame = ttk.Frame(self)
        top_frame.pack(fill="x", pady=10, padx=10)

        tk.Label(top_frame, text="Search:", font=("Arial", 12), bg=COLORS["bg"]).pack(side="left")
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(top_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side="left", padx=5)
        self.search_var.trace_add("write", lambda *_: self.populate_menu())

        # Add Item Button
        add_btn = ttk.Button(top_frame, text="➕ Add Item", command=self.add_item)
        add_btn.pack(side="right")

        # ===== Scrollable Menu Area =====
        canvas = tk.Canvas(self, bg=COLORS["bg"], highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=scrollbar.set)

        self.menu_frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=self.menu_frame, anchor="nw")
        self.menu_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        self.load_menu_from_db()
        self.populate_menu()

    # --- Load menu items ---
    def load_menu_from_db(self):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT menu_id, name, image, price, category, status FROM menu ORDER BY category, name")
        self.menu_items = cursor.fetchall()
        cursor.execute("SELECT DISTINCT category FROM menu")
        self.categories = [row[0] for row in cursor.fetchall()]
        conn.close()

    # --- Add Item ---
    def add_item(self):
        win = tk.Toplevel(self)
        win.title("Add Menu Item")
        win.geometry("550x600")
        win.configure(bg=COLORS["card"])

        # Fields
        tk.Label(win, text="Name:", bg=COLORS["card"]).pack(anchor="w", padx=10, pady=(10, 0))
        name_var = tk.StringVar()
        ttk.Entry(win, textvariable=name_var).pack(fill="x", padx=10, pady=5)

        tk.Label(win, text="Price:", bg=COLORS["card"]).pack(anchor="w", padx=10, pady=(10, 0))
        price_var = tk.DoubleVar()
        ttk.Entry(win, textvariable=price_var).pack(fill="x", padx=10, pady=5)

        tk.Label(win, text="Image:", bg=COLORS["card"]).pack(anchor="w", padx=10, pady=(10, 0))
        img_var = tk.StringVar()
        ttk.Entry(win, textvariable=img_var).pack(fill="x", padx=10, pady=5)

        # Upload button
        def browse_file():
            file_path = filedialog.askopenfilename(
                filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif")])
            if file_path:
                img_var.set(file_path)
        ttk.Button(win, text="Browse", command=browse_file).pack(pady=5)

        tk.Label(win, text="Category:", bg=COLORS["card"]).pack(anchor="w", padx=10, pady=(10, 0))
        cat_var = tk.StringVar()
        ttk.Combobox(win, textvariable=cat_var, values=self.categories, state="readonly").pack(fill="x", padx=10, pady=5)

        tk.Label(win, text="Status:", bg=COLORS["card"]).pack(anchor="w", padx=10, pady=(10, 0))
        status_var = tk.StringVar(value="Available")
        ttk.Combobox(win, textvariable=status_var, values=["Available", "Unavailable"], state="readonly").pack(fill="x", padx=10, pady=5)

        # --- Save new item ---
        def save_new():
            if not name_var.get() or not cat_var.get():
                messagebox.showerror("Error", "Please fill all required fields!")
                return

            # Save image to images/<menu_name>/image.ext
            saved_img_path = FALLBACK_IMAGE
            if img_var.get():
                folder = os.path.join("images", name_var.get().replace(" ", "_"))
                os.makedirs(folder, exist_ok=True)
                ext = os.path.splitext(img_var.get())[1]
                saved_img_path = os.path.join(folder, f"image{ext}")
                shutil.copy(img_var.get(), saved_img_path)

            conn = create_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO menu (name, price, image, category, status) VALUES (%s, %s, %s, %s, %s)",
                (name_var.get(), price_var.get(), saved_img_path, cat_var.get(), status_var.get())
            )
            conn.commit()
            conn.close()

            self.load_menu_from_db()
            self.populate_menu()
            win.destroy()
            messagebox.showinfo("Success", "New item added successfully!")

        ttk.Button(win, text="✅ Add", command=save_new).pack(pady=15)
        ttk.Button(win, text="❌ Cancel", command=win.destroy).pack()

    # --- Edit Item ---
    def edit_item(self, menu_id):
        item = next((i for i in self.menu_items if i[0] == menu_id), None)
        if not item:
            messagebox.showerror("Error", "Menu item not found!")
            return

        menu_id, name, image_path, price, category, status = item

        win = tk.Toplevel(self)
        win.title("Edit Menu Item")
        win.geometry("550x600")
        win.configure(bg=COLORS["card"])

        # Fields
        tk.Label(win, text="Name:", bg=COLORS["card"]).pack(anchor="w", padx=10, pady=(10, 0))
        name_var = tk.StringVar(value=name)
        ttk.Entry(win, textvariable=name_var).pack(fill="x", padx=10, pady=5)

        tk.Label(win, text="Price:", bg=COLORS["card"]).pack(anchor="w", padx=10, pady=(10, 0))
        price_var = tk.DoubleVar(value=price)
        ttk.Entry(win, textvariable=price_var).pack(fill="x", padx=10, pady=5)

        tk.Label(win, text="Image:", bg=COLORS["card"]).pack(anchor="w", padx=10, pady=(10, 0))
        img_var = tk.StringVar(value=image_path)
        ttk.Entry(win, textvariable=img_var).pack(fill="x", padx=10, pady=5)

        def browse_file():
            file_path = filedialog.askopenfilename(
                filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif")])
            if file_path:
                img_var.set(file_path)
        ttk.Button(win, text="Browse", command=browse_file).pack(pady=5)

        tk.Label(win, text="Category:", bg=COLORS["card"]).pack(anchor="w", padx=10, pady=(10, 0))
        cat_var = tk.StringVar(value=category)
        ttk.Combobox(win, textvariable=cat_var, values=self.categories, state="readonly").pack(fill="x", padx=10, pady=5)

        tk.Label(win, text="Status:", bg=COLORS["card"]).pack(anchor="w", padx=10, pady=(10, 0))
        status_var = tk.StringVar(value=status)
        ttk.Combobox(win, textvariable=status_var, values=["Available", "Unavailable"], state="readonly").pack(fill="x", padx=10, pady=5)

        # Save changes
        def save_changes():
            saved_img_path = image_path
            if img_var.get() != image_path and img_var.get():
                folder = os.path.join("images", name_var.get().replace(" ", "_"))
                os.makedirs(folder, exist_ok=True)
                ext = os.path.splitext(img_var.get())[1]
                saved_img_path = os.path.join(folder, f"image{ext}")
                shutil.copy(img_var.get(), saved_img_path)

            conn = create_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE menu SET name=%s, price=%s, image=%s, category=%s, status=%s WHERE menu_id=%s",
                (name_var.get(), price_var.get(), saved_img_path, cat_var.get(), status_var.get(), menu_id)
            )
            conn.commit()
            conn.close()

            self.load_menu_from_db()
            self.populate_menu()
            win.destroy()
            messagebox.showinfo("Success", "Item updated successfully!")

        ttk.Button(win, text="✅ Save", command=save_changes).pack(pady=15)
        ttk.Button(win, text="❌ Cancel", command=win.destroy).pack()

    def delete_item(self, menu_id):
        if messagebox.askyesno("Delete", "Are you sure you want to delete this item?"):
            conn = create_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM menu WHERE menu_id=%s", (menu_id,))
            conn.commit()
            conn.close()
            self.load_menu_from_db()
            self.populate_menu()

    # --- Populate Menu ---
    def populate_menu(self):
        for widget in self.menu_frame.winfo_children():
            widget.destroy()

        search_text = self.search_var.get().lower()
        filtered_items = [item for item in self.menu_items if search_text in item[1].lower()]

        current_category = None
        for menu_id, name, image_path, price, category, status in filtered_items:
            if category != current_category:
                current_category = category
                ttk.Label(self.menu_frame, text=category, font=("Arial", 14, "bold"),
                          background=COLORS["bg"]).pack(anchor="w", pady=(10, 5), padx=10)

            # --- Card ---
            card = ttk.Frame(self.menu_frame, style="Card.TFrame", relief="raised", padding=10)
            card.pack(fill="x", pady=5, padx=20)

            # Image
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
            info_frame = ttk.Frame(card, style="Card.TFrame")
            info_frame.pack(side="left", padx=10, fill="x", expand=True)
            tk.Label(info_frame, text=name, font=("Arial", 12, "bold"), bg=COLORS["card"]).pack(anchor="w")
            tk.Label(info_frame, text=f"BHD {price:.2f}", font=("Arial", 10), bg=COLORS["card"]).pack(anchor="w")

            # Status Badge
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

            # Buttons
            btn_frame = ttk.Frame(card, style="Card.TFrame")
            btn_frame.pack(side="right")
            ttk.Button(btn_frame, text="📝", command=lambda mid=menu_id: self.edit_item(mid)).pack(side="left", padx=5)
            ttk.Button(btn_frame, text="❌", command=lambda mid=menu_id: self.delete_item(mid)).pack(side="left", padx=5)
    