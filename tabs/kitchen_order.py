import tkinter as tk
from db_connection import create_connection

class KitchenTab(tk.Frame):
    def __init__(self,parent):
        super().__init__(parent)
        tk.Label(self, text="Kitchen", font=("Arial", 18, 'bold')).pack(pady=20)
