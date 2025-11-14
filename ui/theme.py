from ttkbootstrap import Style

# Define the colors with dark brown background
COLORS = {
    "bg": "#23170e",        # Dark brown background
    "card": "#124035",      # Dark green for cards
    "accent": "#124035",    # Dark green (buttons)
    "text_dark": "#ebcd95", # Gold text
    "text_light": "#ebcd95",# Gold text
    "success": "#1a4d42",   # Lighter green (hover/active)
    "danger": "#dc2626",    # Red (delete)
    "border": "#23170e",    # Border color
}

def apply_theme(root):
    # Create dark base theme
    style = Style(theme="darkly")
    
    # Root window background
    root.configure(bg=COLORS["bg"])

    # 🟩 Primary Button (default tab buttons)
    style.configure(
        "primary.TButton",
        background=COLORS["accent"],
        foreground=COLORS["text_light"],
        bordercolor=COLORS["accent"],
        focuscolor=COLORS["accent"],
        relief="flat",
        borderwidth=0,
        font=("Segoe UI", 10, "bold"),
        padding=(14, 6),
        anchor="center"
    )
    style.map(
        "primary.TButton",
        background=[("active", "#0a2c23"), ("pressed", "#0a2c23")]
    )

    # 🟢 Success Button (active/selected state)
    style.configure(
        "success.TButton",
        background=COLORS["success"],
        foreground=COLORS["text_light"],
        bordercolor=COLORS["success"],
        focuscolor=COLORS["success"],
        relief="flat",
        borderwidth=0,
        font=("Segoe UI", 10, "bold"),
        padding=(14, 6),
        anchor="center"
    )
    style.map(
        "success.TButton",
        background=[("active", COLORS["accent"]), ("pressed", COLORS["accent"])]
    )

    # 🟨 Custom Button (for forms like Reservation)
    style.configure(
        "Custom.TButton",
        background=COLORS["accent"],
        foreground=COLORS["text_light"],
        bordercolor=COLORS["accent"],
        focuscolor=COLORS["accent"],
        relief="flat",
        borderwidth=0,
        font=("Arial", 10, "bold"),
        padding=(14, 6),
        anchor="center"
    )
    style.map(
        "Custom.TButton",
        background=[("active", COLORS["success"]), ("pressed", COLORS["success"])],
        foreground=[("active", COLORS["text_light"]), ("pressed", COLORS["text_light"])]
    )

    # 🧱 Frames - DISABLE ttkbootstrap frame styling to allow custom colors
    style.configure("TFrame", background="")
    style.configure("TLabelframe", background="", foreground=COLORS["text_light"], bordercolor=COLORS["border"])
    style.configure("TLabelframe.Label", background="", foreground=COLORS["text_light"])

    # 🏷 Labels - DISABLE ttkbootstrap label styling to allow custom colors
    style.configure("TLabel", background="", foreground="")

    # Entry fields
    style.configure("TEntry", 
                   fieldbackground=COLORS["card"],
                   foreground=COLORS["text_light"],
                   bordercolor=COLORS["border"])
    
    # Combobox
    style.configure("TCombobox",
                   fieldbackground=COLORS["card"],
                   background=COLORS["card"],
                   foreground=COLORS["text_light"],
                   bordercolor=COLORS["border"])
    
    