from ttkbootstrap import Style

COLORS = {
    "bg": "#ECE2D8",
    "card": "#ffffff",
    "accent": "#f4a100",
    "text_dark": "#bf4c4c",
    "text_light": "#704141",
    "success": "#16a34a",
    "danger": "#dc2626",
    "border": "#e5e7eb",
}

def apply_theme(root):
    style = Style(theme="flatly")
    root.configure(bg=COLORS["bg"])

    # Customize button styles
    
    style.configure(
        "TabButton.TButton",
        font=("Segoe UI", 10, "bold"),
        background="#ffffff",
        foreground="#444",
        padding=(16, 8),
        borderwidth=0
    )

    # Hover effect for inactive
    style.map(
        "TabButton.TButton",
        background=[("active", "#fef3e2")],   
        foreground=[("active", "#000")]
    )

    # Active (selected) tab
    style.configure(
        "ActiveTab.TButton",
        font=("Segoe UI", 10, "bold"),
        background="#f4a100",
        foreground="white",
        padding=(16, 8),
        borderwidth=0
    )

    style.map(
        "ActiveTab.TButton",
        background=[("active", "#f1a733")],  
        foreground=[("active", "white")]
    )


