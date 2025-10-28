from ttkbootstrap import Window
from ui.tabs_frame import Tabsframe

class RmsApp(Window):  
    def __init__(self):
        super().__init__(themename="flatly")  
        self.title("Restaurant Management System")
        self.geometry("1500x800")
        self.resizable(False, False)

        tabs = Tabsframe(self)
        tabs.pack(fill="both", expand=True)


if __name__ == "__main__":
    app = RmsApp()
    app.mainloop()
