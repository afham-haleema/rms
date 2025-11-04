import tkinter as tk
from ttkbootstrap import ttk
from tabs.dashboard_tab import DashboardTab
from tabs.bill import BillTab
from tabs.kitchen_order import KitchenTab
from tabs.pos import PosTab
from tabs.menu import MenuTab
from tabs.manager import ManagerTab
from ui.theme import apply_theme, COLORS
from tabs.Reservation import ReservationTab 

class Tabsframe(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        apply_theme(self.parent)
        self.configure(bg=COLORS["bg"])
        
        # Initialize current tab tracking
        self.current_tab = None
        self.active_tab = None
        
        self._setup_navbar()
        self._setup_content_area()
        self.show_tab("Dashboard")  # Show default tab

    def _setup_navbar(self):
        """Setup the navigation bar with logo, tabs, and user info"""
        self.navbar = tk.Frame(self, bg="white", height=120)
        self.navbar.pack(side="top", fill="x", padx=0, pady=(0, 5))
        
        self._setup_navbar_left()
        self._setup_navbar_center()
        self._setup_navbar_right()

    def _setup_navbar_left(self):
        """Setup left side of navbar (logo and title)"""
        left_frame = tk.Frame(self.navbar, bg="white")
        left_frame.pack(side="left", padx=20)
        
        # Logo
        tk.Label(
            left_frame, 
            text="🍴", 
            font=("Segoe UI Emoji", 18), 
            bg="white"
        ).pack(side="left")
        
        # Title
        tk.Label(
            left_frame, 
            text="RestaurantOS", 
            font=("Segoe UI", 14, "bold"), 
            bg="white", 
            fg=COLORS["accent"]
        ).pack(side="left", padx=(8, 0))

    def _setup_navbar_center(self):
        """Setup center of navbar (tab buttons)"""
        center_frame = tk.Frame(self.navbar, bg="white")
        center_frame.pack(side="left", padx=60)

        # Define tabs in order of appearance
        self.tabs = {
            "Dashboard": DashboardTab,
            "Menu": MenuTab,
            "POS": PosTab,  # Consistent capitalization
            "Kitchen": KitchenTab,
            "Reservation": ReservationTab,
            "Bill": BillTab,
            "Manager": ManagerTab
        }

        self.buttons = {}
        for name, tab_class in self.tabs.items():
            btn = ttk.Button(
                center_frame,
                text=name,
                style="TabButton.TButton",
                command=lambda n=name: self.show_tab(n)
            )
            btn.pack(side="left", padx=5)
            self.buttons[name] = btn

    def _setup_navbar_right(self):
        """Setup right side of navbar (user info)"""
        right_frame = tk.Frame(self.navbar, bg="white")
        right_frame.pack(side="right", padx=20)
        
        tk.Label(
            right_frame, 
            text="Welcome", 
            bg="white", 
            fg=COLORS["accent"], 
            font=("Segoe UI", 10, "bold")
        ).pack(side="left")

    def _setup_content_area(self):
        """Setup the main content area where tabs are displayed"""
        self.container = tk.Frame(self, bg=COLORS["bg"])
        self.container.pack(fill="both", expand=True, padx=20, pady=20)

    def show_tab(self, tab_name):
        """Switch to the specified tab"""
        # Validate tab exists
        if tab_name not in self.tabs:
            raise ValueError(f"Tab '{tab_name}' does not exist")
        
        # Destroy current tab
        if self.current_tab:
            self.current_tab.destroy()
        
        # Create and display new tab
        tab_class = self.tabs[tab_name]
        self.current_tab = tab_class(self.container)
        self.current_tab.pack(fill="both", expand=True)
        
        # Update button styles
        self._update_button_styles(tab_name)
        
        # Update active tab reference
        self.active_tab = tab_name
        
        # Optional: Call tab activation method if it exists
        if hasattr(self.current_tab, 'on_tab_activated'):
            self.current_tab.on_tab_activated()

    def _update_button_styles(self, active_tab_name):
        """Update the visual style of tab buttons to show active state"""
        for name, button in self.buttons.items():
            if name == active_tab_name:
                button.configure(style="ActiveTab.TButton")
            else:
                button.configure(style="TabButton.TButton")

    def get_current_tab(self):
        """Get the currently active tab instance"""
        return self.current_tab

    def get_active_tab_name(self):
        """Get the name of the currently active tab"""
        return self.active_tab