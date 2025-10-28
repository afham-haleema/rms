import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import Frame

class DashboardTab(Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#f9f5f0")
        self.pack(fill="both", expand=True, padx=30, pady=30)

        title = ttk.Label(self, text="Dashboard", font=("Arial", 24, "bold"), bootstyle="dark")
        subtitle = ttk.Label(self, text="Welcome back! Here's your restaurant overview.",
                             font=("Arial", 12), foreground="#666")
        title.pack(anchor="w")
        subtitle.pack(anchor="w", pady=(0, 20))

   