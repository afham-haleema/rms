from datetime import datetime
import os
import shutil
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
from db_connection import create_connection
from ui.theme import COLORS

FALLBACK_IMAGE = "images/image.png"  # default fallback image

# Theme
CARD_BG = "#124035"          # Dark green for cards (unchanged)
TEXT_COLOR = "#ebcd95"       # Golden text
BACKGROUND_COLOR = "#23170e" # Dark brown background (requested)
BORDER_COLOR = "#444444"     # Grey border color

class MenuTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BACKGROUND_COLOR)

        self.menu_items = []
        self.image_cache = {}

        # Configure ttk styles to match our theme
        self.configure_styles()

        # ===== Top Search + Add Button Bar =====
        top_frame = tk.Frame(self, bg=BACKGROUND_COLOR)
        top_frame.pack(fill="x", pady=12, padx=15)

        tk.Label(top_frame, text="Search:", font=("Arial", 12), bg=BACKGROUND_COLOR, fg=TEXT_COLOR).pack(side="left")
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(top_frame, textvariable=self.search_var, width=25, style="Custom.TEntry")
        search_entry.pack(side="left", padx=8)
        self.search_var.trace_add("write", lambda *_: self.populate_menu())

        add_btn = ttk.Button(top_frame, text="➕ Add Item", command=self.add_item, style="Custom.TButton")
        add_btn.pack(side="right")

        canvas = tk.Canvas(self, bg=BACKGROUND_COLOR, highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview, style="Custom.Vertical.TScrollbar")
        scrollbar.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=scrollbar.set)

        self.menu_frame = tk.Frame(canvas, bg=BACKGROUND_COLOR)
        canvas.create_window((0, 0), window=self.menu_frame, anchor="nw")
        self.menu_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

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
        """Configure ttk styles to match our dark theme"""
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

        # Combobox style (optional)
        style.configure("Custom.TCombobox",
                        fieldbackground="#2d2015",
                        foreground=TEXT_COLOR)

    def _nuclear_force_green_cards(self):
        """
        NUCLEAR routine (preserved because you need it).
        New behavior: enforce the global theme (BACKGROUND_COLOR/ TEXT_COLOR)
        on all widgets EXCEPT those that are inside a card (card frames are marked with .is_card = True).
        This avoids recoloring card contents while keeping the rest of UI consistent.
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
                        widget.configure(bg=CARD_BG, fg=TEXT_COLOR)  # keep interactive buttons visually distinct
                    except:
                        pass
                # For ttk widgets, attempt a style enforcement where appropriate
                # (We avoid forcing styles that may break ttk's native look.)
            except:
                pass

            # Recurse
            for child in widget.winfo_children():
                enforce_theme(child)

        enforce_theme(self.menu_frame)

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
        win.geometry("500x550")
        win.configure(bg=CARD_BG)  # dialogs use card green for contrast
        self.center_window(win)  # CENTER THE WINDOW

        # Fields
        tk.Label(win, text="Name:", bg=CARD_BG, fg=TEXT_COLOR).pack(anchor="w", padx=10, pady=(10, 0))
        name_var = tk.StringVar()
        ttk.Entry(win, textvariable=name_var, style="Custom.TEntry").pack(fill="x", padx=10, pady=5)

        tk.Label(win, text="Price:", bg=CARD_BG, fg=TEXT_COLOR).pack(anchor="w", padx=10, pady=(10, 0))
        price_var = tk.DoubleVar()
        ttk.Entry(win, textvariable=price_var, style="Custom.TEntry").pack(fill="x", padx=10, pady=5)

        tk.Label(win, text="Image:", bg=CARD_BG, fg=TEXT_COLOR).pack(anchor="w", padx=10, pady=(10, 0))
        img_var = tk.StringVar()
        ttk.Entry(win, textvariable=img_var, style="Custom.TEntry").pack(fill="x", padx=10, pady=5)

        # Upload button - FIXED to prevent minimizing
        def browse_file():
            # Bring the parent window to front before opening file dialog
            win.lift()
            win.focus_force()
            
            file_path = filedialog.askopenfilename(
                parent=win,  # Set parent to keep dialog on top
                title="Select Image File",
                filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif")]
            )
            if file_path:
                img_var.set(file_path)
                # Bring window back to front after file selection
                win.lift()
                win.focus_force()

        ttk.Button(win, text="Browse", command=browse_file, style="Custom.TButton").pack(pady=5)

        tk.Label(win, text="Category:", bg=CARD_BG, fg=TEXT_COLOR).pack(anchor="w", padx=10, pady=(10, 0))
        cat_var = tk.StringVar()
        ttk.Combobox(win, textvariable=cat_var, values=self.categories, state="readonly", style="Custom.TCombobox").pack(fill="x", padx=10, pady=5)

        tk.Label(win, text="Status:", bg=CARD_BG, fg=TEXT_COLOR).pack(anchor="w", padx=10, pady=(10, 0))
        status_var = tk.StringVar(value="Available")
        ttk.Combobox(win, textvariable=status_var, values=["Available", "Unavailable"], state="readonly", style="Custom.TCombobox").pack(fill="x", padx=10, pady=5)

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

        ttk.Button(win, text="✅ Add", command=save_new, style="Custom.TButton").pack(pady=15)
        ttk.Button(win, text="❌ Cancel", command=win.destroy, style="Custom.TButton").pack()

    def edit_item(self, menu_id):
        item = next((i for i in self.menu_items if i[0] == menu_id), None)
        if not item:
            messagebox.showerror("Error", "Menu item not found!")
            return

        menu_id, name, image_path, price, category, status = item

        win = tk.Toplevel(self)
        win.title("Edit Menu Item")
        win.geometry("500x550")
        win.configure(bg=CARD_BG)
        self.center_window(win)  # CENTER THE WINDOW

        # Fields
        tk.Label(win, text="Name:", bg=CARD_BG, fg=TEXT_COLOR).pack(anchor="w", padx=10, pady=(10, 0))
        name_var = tk.StringVar(value=name)
        ttk.Entry(win, textvariable=name_var, style="Custom.TEntry").pack(fill="x", padx=10, pady=5)

        tk.Label(win, text="Price:", bg=CARD_BG, fg=TEXT_COLOR).pack(anchor="w", padx=10, pady=(10, 0))
        price_var = tk.DoubleVar(value=price)
        ttk.Entry(win, textvariable=price_var, style="Custom.TEntry").pack(fill="x", padx=10, pady=5)

        tk.Label(win, text="Image:", bg=CARD_BG, fg=TEXT_COLOR).pack(anchor="w", padx=10, pady=(10, 0))
        img_var = tk.StringVar(value=image_path)
        ttk.Entry(win, textvariable=img_var, style="Custom.TEntry").pack(fill="x", padx=10, pady=5)

        # Upload button - FIXED to prevent minimizing
        def browse_file():
            # Bring the parent window to front before opening file dialog
            win.lift()
            win.focus_force()
            
            file_path = filedialog.askopenfilename(
                parent=win,  # Set parent to keep dialog on top
                title="Select Image File", 
                filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif")]
            )
            if file_path:
                img_var.set(file_path)
                # Bring window back to front after file selection
                win.lift()
                win.focus_force()

        ttk.Button(win, text="Browse", command=browse_file, style="Custom.TButton").pack(pady=5)

        tk.Label(win, text="Category:", bg=CARD_BG, fg=TEXT_COLOR).pack(anchor="w", padx=10, pady=(10, 0))
        cat_var = tk.StringVar(value=category)
        ttk.Combobox(win, textvariable=cat_var, values=self.categories, state="readonly", style="Custom.TCombobox").pack(fill="x", padx=10, pady=5)

        tk.Label(win, text="Status:", bg=CARD_BG, fg=TEXT_COLOR).pack(anchor="w", padx=10, pady=(10, 0))
        status_var = tk.StringVar(value=status)
        ttk.Combobox(win, textvariable=status_var, values=["Available", "Unavailable"], state="readonly", style="Custom.TCombobox").pack(fill="x", padx=10, pady=5)

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

        ttk.Button(win, text="✅ Save", command=save_changes, style="Custom.TButton").pack(pady=15)
        ttk.Button(win, text="❌ Cancel", command=win.destroy, style="Custom.TButton").pack()

    def delete_item(self, menu_id):
        if messagebox.askyesno("Delete", "Are you sure you want to delete this item?"):
            conn = create_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM menu WHERE menu_id=%s", (menu_id,))
            conn.commit()
            conn.close()
            self.load_menu_from_db()
            self.populate_menu()

    def populate_menu(self):
        for widget in self.menu_frame.winfo_children():
            widget.destroy()

        search_text = self.search_var.get().lower()
        filtered_items = [item for item in self.menu_items if search_text in item[1].lower()]

        current_category = None
        row_frame = None
        item_count = 0

        for menu_id, name, image_path, price, category, status in filtered_items:
            # Create category header - dark brown background
            if category != current_category:
                current_category = category
                item_count = 0
                category_label = tk.Label(self.menu_frame, text=category, font=("Arial", 18, "bold"),
                         background=BACKGROUND_COLOR, foreground=TEXT_COLOR)
                category_label.pack(pady=(20, 15), fill="x")

                row_frame = tk.Frame(self.menu_frame, bg=BACKGROUND_COLOR)
                row_frame.pack(fill="x", padx=70, pady=60)

            if item_count % 3 == 0:
                row_frame = tk.Frame(self.menu_frame, bg=BACKGROUND_COLOR)
                row_frame.pack(fill="x", padx=25, pady=20)

            card = tk.Frame(row_frame, relief="solid", bg=CARD_BG, bd=2,
                          highlightbackground=BORDER_COLOR, highlightthickness=1)
            card.pack(side="left", fill="both", expand=True, padx=55, pady=48)
            card.configure(width=320, height=380)
            # Mark this frame as a card so the nuclear routine can detect and skip it
            setattr(card, "is_card", True)

            # EVERYTHING inside the card should remain GREEN
            inner_frame = tk.Frame(card, bg=CARD_BG, padx=15, pady=15)
            inner_frame.pack(fill="both", expand=True)

            # Image
            if image_path not in self.image_cache:
                img_path = image_path if os.path.exists(image_path) else FALLBACK_IMAGE
                try:
                    img = Image.open(img_path)
                    img.thumbnail((180, 180))
                    self.image_cache[image_path] = ImageTk.PhotoImage(img)
                except:
                    self.image_cache[image_path] = None

            content_frame = tk.Frame(inner_frame, bg=CARD_BG)
            content_frame.pack(fill="both", expand=True)

            if self.image_cache[image_path]:
                img_label = tk.Label(content_frame, image=self.image_cache[image_path], bg=CARD_BG)
                img_label.pack(pady=12)

            info_frame = tk.Frame(content_frame, bg=CARD_BG)
            info_frame.pack(fill="x", pady=12)

            # Name label - GREEN background, GOLDEN text
            name_label = tk.Label(info_frame, text=name, font=("Arial", 14, "bold"),
                                bg=CARD_BG, fg=TEXT_COLOR, wraplength=260)
            name_label.pack(pady=(8, 5))

            # Price label - GREEN background, GOLDEN text
            price_label = tk.Label(info_frame, text=f"BHD {price:.2f}", font=("Arial", 13, "bold"),
                                 bg=CARD_BG, fg=TEXT_COLOR)
            price_label.pack(pady=(5, 10))

            bottom_frame = tk.Frame(info_frame, bg=CARD_BG)
            bottom_frame.pack(fill="x", pady=(8, 0))

            # Status Badge - keep clear green/red
            status_color = "#27ae60" if status.lower() == "available" else "#e74c3c"
            status_text = "AVAILABLE" if status.lower() == "available" else "UNAVAILABLE"

            status_label = tk.Label(
                bottom_frame,
                text=status_text,
                bg=status_color,
                fg="white",
                font=("Arial", 10, "bold"),
                padx=20,
                pady=6,
                relief="raised",
                bd=2
            )
            status_label.pack(side="left", padx=(0, 15))

            btn_frame = tk.Frame(bottom_frame, bg=CARD_BG)
            btn_frame.pack(side="right")

            edit_btn = ttk.Button(btn_frame, text="📝", width=5,
                                command=lambda mid=menu_id: self.edit_item(mid), style="Custom.TButton")
            edit_btn.pack(side="left", padx=4)

            delete_btn = ttk.Button(btn_frame, text="❌", width=5,
                                  command=lambda mid=menu_id: self.delete_item(mid), style="Custom.TButton")
            delete_btn.pack(side="left", padx=4)

            item_count += 1

        remaining_items = item_count % 3
        if remaining_items > 0:
            for _ in range(3 - remaining_items):
                filler = tk.Frame(row_frame, bg=BACKGROUND_COLOR)
                filler.pack(side="left", fill="both", expand=True, padx=12, pady=12)

        # Keep the nuclear routine (but it no longer recolors card contents)
        self.after(200, self._nuclear_force_green_cards)