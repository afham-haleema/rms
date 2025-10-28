import tkinter as tk
from ttkbootstrap import ttk
from tabs.dashboard_tab import DashboardTab
from tabs.bill import BillTab
from tabs.kitchen_order import KitchenTab
from tabs.pos import PosTab
from tabs.menu import MenuTab
from tabs.manager import ManagerTab
from ui.theme import apply_theme, COLORS

class Tabsframe(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        apply_theme(self.parent)
        self.configure(bg=COLORS["bg"])

        # ===== Top Navbar =====
        self.navbar = tk.Frame(self, bg="white", height=120)
        self.navbar.pack(side="top", fill="x", padx=0, pady=(0, 5))

        # --- Left: Logo + Title ---
        left_frame = tk.Frame(self.navbar, bg="white")
        left_frame.pack(side="left", padx=20)
        tk.Label(left_frame, text="🍴", font=("Segoe UI Emoji", 18), bg="white").pack(side="left")
        tk.Label(left_frame, text="RestaurantOS", font=("Segoe UI", 14, "bold"), bg="white", fg=COLORS["accent"]).pack(side="left", padx=(8, 0))

        # --- Center: Tabs ---
        center_frame = tk.Frame(self.navbar, bg="white")
        center_frame.pack(side="left", padx=60)

        self.tabs = {
            "Dashboard": DashboardTab,
            "Menu": MenuTab,
            "Pos": PosTab,
            "Kitchen": KitchenTab,
            "Bill": BillTab,
            "Manager": ManagerTab
        }

        self.buttons = {}
        for name in self.tabs.keys():
            btn = ttk.Button(
                center_frame,
                text=name,
                style="TabButton.TButton",
                command=lambda n=name: self.show_tab(n)
            )
            btn.pack(side="left", padx=5)
            self.buttons[name] = btn

        # --- Right: Welcome text ---
        right_frame = tk.Frame(self.navbar, bg="white")
        right_frame.pack(side="right", padx=20)
        tk.Label(right_frame, text="Welcome", bg="white", fg=COLORS["accent"], font=("Segoe UI", 10, "bold")).pack(side="left")

        # ===== Content Area =====
        self.container = tk.Frame(self, bg=COLORS["bg"])
        self.container.pack(fill="both", expand=True, padx=20, pady=20)

        self.current_tab = None
        self.active_tab = None
        self.show_tab("Dashboard")

    def show_tab(self, name):
        if self.current_tab:
            self.current_tab.destroy()
        tab_class = self.tabs[name]
        self.current_tab = tab_class(self.container)
        self.current_tab.pack(fill="both", expand=True)

        if self.active_tab:
            self.buttons[self.active_tab].configure(style="TabButton.TButton")
        self.buttons[name].configure(style="ActiveTab.TButton")
        self.active_tab = name
