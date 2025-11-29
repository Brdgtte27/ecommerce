import customtkinter as ctk
from tkinter import messagebox


def dashboard_page(app, username, users, login_callback):
    for widget in app.winfo_children():
        widget.destroy()

    sidebar = ctk.CTkFrame(app, fg_color="#ff99cc", width=250)
    sidebar.pack(side="left", fill="y")

    main = ctk.CTkFrame(app, fg_color="white")
    main.pack(side="right", expand=True, fill="both")

    ctk.CTkLabel(sidebar, text="CUSTOMER DASHBOARD", text_color="white",
                 font=("Arial", 22, "bold")).pack(pady=30)

    def show_profile():
        for w in main.winfo_children():
            w.destroy()
        ctk.CTkLabel(main, text=f"Welcome, {username}!", font=("Arial",28,"bold"),
                     text_color="#ff66aa").pack(pady=40)
        for user in users:
            if user["name"] == username:
                ctk.CTkLabel(main, text=f"📧 Email: {user['email']}", font=("Arial",20),
                             text_color="#ff3399").pack(pady=10)
                break

    def products():
        messagebox.showinfo("Products", "Browse products here soon!")

    def logout():
        messagebox.showinfo("Logout", "You have been logged out successfully.")
        login_callback()

    # Sidebar buttons
    ctk.CTkButton(sidebar, text="👤 Profile", fg_color="#ff66aa", text_color="white",
                  hover_color="#ff3385", command=show_profile,
                  width=180, height=40, corner_radius=15).pack(pady=10)

    ctk.CTkButton(sidebar, text="🛍️ Products", fg_color="#ff66aa", text_color="white",
                  hover_color="#ff3385", command=products,
                  width=180, height=40, corner_radius=15).pack(pady=10)

    ctk.CTkButton(sidebar, text="🚪 Logout", fg_color="#ff3385", text_color="white",
                  hover_color="#ff007f", command=logout,
                  width=180, height=40, corner_radius=15).pack(pady=40)

    show_profile()
