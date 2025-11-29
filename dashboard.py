import customtkinter as ctk
import tkinter as tk
import re
from tkinter import messagebox
from tkcalendar import Calendar, DateEntry
from datetime import datetime
from tkinter import Toplevel
from PIL import Image, ImageTk, ImageDraw
import os
import threading
import time
from database import get_all_products, add_order_full, get_orders_by_user_full, update_order_status, find_user_by_email, \
    update_user_profile, update_user_profile_with_img

# GLOBAL VARIABLE FOR LOGGED IN USER
logged_user_email = None

# CART ITEMS
cart_items = []

# Add product to cart (if already exists, increase quantity)
def add_to_cart(product):
    global cart_items
    for item in cart_items:
        if item['name'] == product['name']:
            item['quantity'] += 1
            return
    product_copy = product.copy()
    product_copy['quantity'] = 1
    cart_items.append(product_copy)

# Remove product from cart (decrease quantity or remove entirely)
def remove_from_cart(product_name):
    for item in cart_items:
        if item['name'] == product_name:
            item['quantity'] -= 1
            if item['quantity'] <= 0:
                cart_items.remove(item)
            return


# Display cart in a given frame
def display_cart(cart_frame):
    # Clear previous widgets
    for widget in cart_frame.winfo_children():
        widget.destroy()


    if not cart_items:
        ctk.CTkLabel(cart_frame, text="Your cart is empty").grid(row=0, column=0)
        return


    # Create table headers
    ctk.CTkLabel(cart_frame, text="Product").grid(row=0, column=0, padx=5, pady=2)
    ctk.CTkLabel(cart_frame, text="Price").grid(row=0, column=1, padx=5, pady=2)
    ctk.CTkLabel(cart_frame, text="Quantity").grid(row=0, column=2, padx=5, pady=2)
    ctk.CTkLabel(cart_frame, text="Total").grid(row=0, column=3, padx=5, pady=2)


    total_price = 0
    for idx, item in enumerate(cart_items, start=1):
        item_total = item['price'] * item['quantity']
        total_price += item_total


        ctk.CTkLabel(cart_frame, text=item['name']).grid(row=idx, column=0, padx=5, pady=2)
        ctk.CTkLabel(cart_frame, text=f"₱{item['price']}").grid(row=idx, column=1, padx=5, pady=2)
        ctk.CTkLabel(cart_frame, text=item['quantity']).grid(row=idx, column=2, padx=5, pady=2)
        ctk.CTkLabel(cart_frame, text=f"₱{item_total}").grid(row=idx, column=3, padx=5, pady=2)


    # Show total at the bottom
    ctk.CTkLabel(cart_frame, text=f"Total: ₱{total_price}").grid(row=len(cart_items)+1, column=0, columnspan=4, pady=10)




# Categories
categories = ["Base", "Lip", "Eyes", "Others"]


def dashboard_page(app, username, logout_callback):
    for widget in app.winfo_children():
        widget.destroy()


    sidebar = ctk.CTkFrame(app, fg_color="#ff99cc", width=300, corner_radius=0)
    sidebar.pack(side="left", fill="y")


    main = ctk.CTkFrame(app, fg_color="white")
    main.pack(side="right", expand=True, fill="both")


    ctk.CTkLabel(
        sidebar,
        text="POWERPUFF",
        text_color="white",
        font=("Arial", 26, "bold")
    ).pack(pady=(20, 50))


    # ================= PROFILE PAGE =================
    def show_profile():
        for widget in main.winfo_children():
            widget.destroy()


        user = find_user_by_email(username)
        if not user:
            messagebox.showerror("Error", "User not found.")
            return


        # ================= HEADER =================
        ctk.CTkLabel(main, text="My Profile", font=("Arial Black", 36, "bold"),
                     text_color="#cc0066", anchor="w").pack(anchor="w", padx=60, pady=(40, 20))


        content = ctk.CTkFrame(main, fg_color="white")
        content.pack(fill="both", expand=True, padx=60, pady=10)
        content.grid_columnconfigure(0, weight=0)
        content.grid_columnconfigure(1, weight=1)


        # ================= LEFT PANEL =================
        left = ctk.CTkFrame(content, fg_color="white", border_color="#ff66aa",
                            border_width=3, corner_radius=10, width=250, height=500)
        left.grid(row=0, column=0, sticky="n", padx=(0, 40), pady=10)
        left.grid_propagate(False)
        left.pack_propagate(False)


        # Function to load circular profile image
        def load_circle_image(path, size=180):
            try:
                img = Image.open(path).resize((size, size)).convert("RGBA")
                mask = Image.new("L", (size, size), 0)
                draw = ImageDraw.Draw(mask)
                draw.ellipse((0, 0, size, size), fill=255)
                img.putalpha(mask)
                return ImageTk.PhotoImage(img)
            except:
                return None


        default_img = os.path.join("pics", "unknown.jpg")
        image_path = user.get("profile_img") or default_img
        if not os.path.exists(image_path):
            image_path = default_img


        # Profile Image Frame
        img_frame = ctk.CTkFrame(left, fg_color="white")
        img_frame.pack(pady=15)
        photo = load_circle_image(image_path)
        img_label = ctk.CTkLabel(img_frame, image=photo, text="")
        img_label.image = photo
        img_label.pack()


        # Full Name
        full_name = f"{user['first_name']} {user['last_name']}".strip()
        ctk.CTkLabel(left, text=full_name, font=("Arial Black", 17, "bold"),
                     text_color="black").pack(pady=(5, 15))


        # Upload Picture Button
        def upload_picture():
            from tkinter.filedialog import askopenfilename
            path = askopenfilename(filetypes=[("Images", "*.png *.jpg *.jpeg")])
            if not path:
                return


            update_user_profile_with_img(user["email"], path)
            new_img = load_circle_image(path)
            if new_img:
                img_label.configure(image=new_img)
                img_label.image = new_img


        ctk.CTkButton(left, text="Upload Picture", fg_color="#ff66aa", hover_color="#ff3385",
                      text_color="white", width=200, height=40, corner_radius=10,
                      command=upload_picture).pack(pady=(0, 20))


        # Contact Information
        ctk.CTkLabel(left, text="CONTACT INFORMATION", font=("Arial", 14, "bold"),
                     text_color="#cc0066").pack(anchor="w", padx=25)
        email_label = ctk.CTkLabel(left, text=f"📧 {user['email']}", font=("Arial", 14), text_color="black")
        email_label.pack(anchor="w", padx=25, pady=(5, 0))
        phone_label = ctk.CTkLabel(left, text=f"📞 {user.get('phone', '')}", font=("Arial", 14), text_color="black")
        phone_label.pack(anchor="w", padx=25, pady=(0, 20))


        # ================= RIGHT PANEL =================
        right = ctk.CTkFrame(content, fg_color="white", border_color="#ff66aa",
                             border_width=3, corner_radius=10, width=850, height=700)
        right.grid(row=0, column=1, sticky="nsew", pady=10)
        right.grid_propagate(True)


        form = ctk.CTkFrame(right, fg_color="white")
        form.pack(padx=30, pady=20, fill="both", expand=True)
        form.grid_columnconfigure(0, weight=1)
        form.grid_columnconfigure(1, weight=1)


        # ================= HELPER TO ADD FIELDS =================
        def add_field(parent, label, value="", is_combo=False, combo_values=None, combo_var=None):
            wrapper = ctk.CTkFrame(parent, fg_color="white")
            wrapper.pack(fill="x", pady=8)


            # Label sa ibabaw
            ctk.CTkLabel(wrapper, text=label, font=("Arial", 14, "bold"),
                         text_color="#cc0066").pack(anchor="w")


            # If combo box
            if is_combo:
                combo = ctk.CTkComboBox(
                    wrapper,
                    values=combo_values or [],
                    variable=combo_var,
                    width=400, height=38,
                    fg_color="#ffe6f2",
                    border_color="#ff66aa",  # pink border
                    border_width=2,
                    dropdown_fg_color="white",
                    dropdown_text_color="black"  # black text
                )
                combo.pack(fill="x")
                return combo


            # If birthday, use DateEntry calendar
            if label.lower() == "birthday":
                try:
                    # Try to parse existing value
                    date_val = datetime.strptime(value, "%Y-%m-%d") if value else datetime.today()
                except:
                    # If parsing fails, default to today
                    date_val = datetime.today()


                date_entry = DateEntry(
                    wrapper,
                    width=17,
                    background="#ff66aa",
                    foreground="white",
                    borderwidth=2,
                    year=date_val.year,
                    month=date_val.month,
                    day=date_val.day,
                    date_pattern="yyyy-mm-dd"  # format for DB
                )
                date_entry.pack(fill="x")
                return date_entry


            # Normal entry
            entry = ctk.CTkEntry(
                wrapper, width=400, height=38,
                fg_color="#ffe6f2",
                border_color="#ff66aa",  # pink border
                border_width=2,
                text_color="black",  # black text
                placeholder_text_color="gray"
            )
            entry.insert(0, value or "")
            entry.pack(fill="x")
            return entry


        # Columns
        col1 = ctk.CTkFrame(form, fg_color="white")
        col1.grid(row=0, column=0, padx=10, pady=5, sticky="n")
        col2 = ctk.CTkFrame(form, fg_color="white")
        col2.grid(row=0, column=1, padx=10, pady=5, sticky="n")


        # Left Column Fields
        fname_entry = add_field(col1, "Full Name", full_name)
        age_entry = add_field(col1, "Age", str(user.get("age", "")))
        phone_entry = add_field(col1, "Phone Number", user.get("phone", ""))
        email_entry = add_field(col1, "Email Account", user.get("email", ""))
        birthday_entry = add_field(col1, "Birthday", user.get("birthday", ""))


        # Right Column Fields with Province → City → Barangay
        # ---------------- FULL PH PROVINCES, CITIES, BARANGAYS ----------------
        # NOTE: For simplicity, I'm only including major cities per province;
        # you can expand barangays per city if needed. Full list is huge.


        provinces_cities = {
            "Abra": ["Bangued", "Boliney", "Bucay"],
            "Agusan del Norte": ["Butuan", "Cabadbaran"],
            "Agusan del Sur": ["Bayugan", "Sibagat", "San Francisco"],
            "Aklan": ["Kalibo", "Malay", "Nabas"],
            "Albay": ["Legazpi", "Tabaco", "Ligao"],
            "Antique": ["San Jose", "Sibalom", "Patnongon"],
            "Apayao": ["Kabugao", "Conner"],
            "Aurora": ["Baler", "Casiguran"],
            "Basilan": ["Isabela", "Lamitan", "Tipo-Tipo"],
            "Bataan": ["Balanga", "Dinalupihan", "Orani"],
            "Batanes": ["Basco", "Itbayat"],
            "Batangas": ["Batangas City", "Lipa", "Tanauan"],
            "Benguet": ["Baguio", "La Trinidad", "Tuba"],
            "Biliran": ["Naval", "Biliran"],
            "Bohol": ["Tagbilaran", "Carmen", "Tubigon"],
            "Bukidnon": ["Malaybalay", "Valencia", "Manolo Fortich"],
            "Bulacan": ["Malolos", "Meycauayan", "San Jose del Monte"],
            "Cagayan": ["Tuguegarao", "Aparri", "Cauayan"],
            "Camarines Norte": ["Daet", "Labo", "Capalonga"],
            "Camarines Sur": ["Naga", "Iriga", "Pasacao"],
            "Camiguin": ["Mambajao", "Mahinog"],
            "Capiz": ["Roxas", "Panay", "Dao"],
            "Catanduanes": ["Virac", "Baras"],
            "Cavite": ["Imus", "Bacoor", "Tagaytay"],
            "Cebu": ["Cebu City", "Lapu-Lapu", "Mandaue", "Danao"],
            "Cotabato": ["Kidapawan", "Midsayap", "Cotabato City"],
            "Davao de Oro": ["Nabunturan", "Monkayo"],
            "Davao del Norte": ["Tagum", "Panabo", "Samal"],
            "Davao del Sur": ["Davao City", "Digos", "Santa Cruz"],
            "Davao Occidental": ["Malita", "Santa Maria"],
            "Davao Oriental": ["Mati", "Baganga", "Boston"],
            "Dinagat Islands": ["San Jose", "Libjo"],
            "Eastern Samar": ["Borongan", "Balangkayan", "Salcedo"],
            "Guimaras": ["Jordan", "Nueva Valencia"],
            "Ifugao": ["Lagawe", "Kiangan"],
            "Ilocos Norte": ["Laoag", "Batac", "Paoay"],
            "Ilocos Sur": ["Vigan", "Candon", "Santa"],
            "Iloilo": ["Iloilo City", "Passi", "Dumangas"],
            "Isabela": ["Ilagan", "Cauayan", "Santiago"],
            "Kalinga": ["Tabuk", "Lubuagan"],
            "La Union": ["San Fernando", "Agoo", "Bauang"],
            "Laguna": ["Santa Rosa", "Calamba", "San Pablo", "Alaminos"],
            "Lanao del Norte": ["Iligan", "Tubod", "Kapatagan"],
            "Lanao del Sur": ["Marawi", "Bacolod-Kalawi"],
            "Leyte": ["Tacloban", "Ormoc", "Baybay"],
            "Maguindanao": ["Buluan", "Cotabato City", "Sultan Kudarat"],
            "Marinduque": ["Boac", "Mogpog"],
            "Masbate": ["Masbate City", "Cataingan"],
            "Metro Manila": ["Manila", "Quezon City", "Makati", "Pasig", "Taguig"],
            "Misamis Occidental": ["Ozamiz", "Tangub"],
            "Misamis Oriental": ["Cagayan de Oro", "El Salvador"],
            "Mountain Province": ["Bontoc", "Sagada"],
            "Negros Occidental": ["Bacolod", "Silay", "Victorias"],
            "Negros Oriental": ["Dumaguete", "Bais", "Tanjay"],
            "Northern Samar": ["Catarman", "Laoang"],
            "Nueva Ecija": ["Cabanatuan", "Gapan", "Palayan"],
            "Nueva Vizcaya": ["Bayombong", "Solano"],
            "Occidental Mindoro": ["Mamburao", "San Jose"],
            "Oriental Mindoro": ["Calapan", "Pinamalayan"],
            "Palawan": ["Puerto Princesa", "El Nido", "Roxas"],
            "Pampanga": ["San Fernando", "Angeles", "Mabalacat"],
            "Pangasinan": ["Lingayen", "Dagupan", "Urdaneta"],
            "Quezon": ["Lucena", "Tayabas", "Sariaya"],
            "Quirino": ["Cabugao", "Diffun"],
            "Rizal": ["Antipolo", "Cainta", "Tanay"],
            "Romblon": ["Romblon", "Odiongan", "San Agustin"],
            "Samar": ["Catbalogan", "Calbayog"],
            "Sarangani": ["Alabel", "Glan"],
            "Siquijor": ["Siquijor", "Larena", "Lazi"],
            "Sorsogon": ["Sorsogon City", "Bulusan", "Irosin"],
            "South Cotabato": ["Koronadal", "Santo Niño"],
            "Southern Leyte": ["Maasin", "Sogod"],
            "Sultan Kudarat": ["Tacurong", "Isulan"],
            "Sulu": ["Jolo", "Indanan", "Patikul"],
            "Surigao del Norte": ["Surigao", "Placer"],
            "Surigao del Sur": ["Tandag", "Bislig"],
            "Tarlac": ["Tarlac City", "Concepcion", "Paniqui"],
            "Tawi-Tawi": ["Bongao", "Sapa-Sapa"],
            "Zambales": ["Iba", "Olongapo", "Castillejos"],
            "Zamboanga del Norte": ["Dipolog", "Dapitan"],
            "Zamboanga del Sur": ["Pagadian", "Dumingag"],
            "Zamboanga Sibugay": ["Ipil", "Titay"]
        }


        # Sample barangays (for demonstration, not full PH list)
        city_barangays = {
            "San Pablo": [
                "Bagong Bayan II-A", "Bagong Pook VI-C",
                "Barangay I-A", "Barangay I-B",
                "Barangay II-A", "Barangay II-B", "Barangay II-C",
                "Barangay II-D", "Barangay II-E", "Barangay II-F",
                "Barangay III-A", "Barangay III-B", "Barangay III-C",
                "Barangay III-D", "Barangay III-E", "Barangay III-F",
                "Barangay IV-A", "Barangay IV-B", "Barangay IV-C",
                "Barangay V-A", "Barangay V-B", "Barangay V-C", "Barangay V-D",
                "Barangay VI-A", "Barangay VI-B", "Barangay VI-D", "Barangay VI-E",
                "Barangay VII-A", "Barangay VII-B", "Barangay VII-C", "Barangay VII-D", "Barangay VII-E",
                "Bautista", "Concepcion", "Del Remedio", "Dolores",
                "San Antonio 1", "San Antonio 2", "San Bartolome",
                "San Buenaventura", "San Crispin", "San Cristobal",
                "San Diego", "San Francisco", "San Gabriel", "San Gregorio",
                "San Ignacio", "San Isidro", "San Joaquin", "San Jose",
                "San Juan", "San Lorenzo", "San Lucas 1", "San Lucas 2",
                "San Marcos", "San Mateo", "San Miguel", "San Nicolas",
                "San Pedro", "San Rafael", "San Roque", "San Vicente",
                "Santa Ana", "Santa Catalina", "Santa Cruz", "Santa Elena",
                "Santa Felomina", "Santa Isabel", "Santa Maria", "Santa Maria Magdalena",
                "Santa Monica", "Santa Veronica", "Santiago I", "Santiago II",
                "Santisimo Rosario", "Santo Angel", "Santo Cristo", "Santo Niño",
                "Soledad", "Atisan"
            ],
            "Alaminos": [
                "Barangay I (Poblacion)", "Barangay II (Poblacion)", "Barangay III (Poblacion)",
                "Barangay IV (Poblacion)",
                "Del Carmen", "Palma", "San Agustin", "San Andres", "San Benito",
                "San Gregorio", "San Ildefonso", "San Juan", "San Miguel", "San Roque", "Santa Rosa"
            ]
        }


        province_var = ctk.StringVar(value=user.get("province", ""))
        city_var = ctk.StringVar(value=user.get("city", ""))
        barangay_var = ctk.StringVar(value=user.get("barangay", ""))


        province_entry = add_field(col2, "Province", is_combo=True,
                                   combo_values=list(provinces_cities.keys()),
                                   combo_var=province_var)


        city_entry = add_field(col2, "City", is_combo=True,
                               combo_values=provinces_cities.get(province_var.get(), []),
                               combo_var=city_var)


        barangay_entry = add_field(col2, "Barangay", is_combo=True,
                                   combo_values=city_barangays.get(city_var.get(), []),
                                   combo_var=barangay_var)


        postal_entry = add_field(col2, "Postal Code", user.get("postal_code", ""))
        street_entry = add_field(col2, "Street Address", user.get("address", ""))


        # Update cities when province changes
        def update_cities(*args):
            selected = province_var.get()
            city_entry.configure(values=provinces_cities.get(selected, []))
            city_var.set("")
            barangay_entry.configure(values=[])  # clear barangays
            barangay_var.set("")


        province_var.trace("w", update_cities)


        # Update barangays when city changes
        def update_barangays(*args):
            selected_city = city_var.get()
            barangay_entry.configure(values=city_barangays.get(selected_city, []))
            barangay_var.set("")


        city_var.trace("w", update_barangays)


        # ================= SAVE CHANGES =================
        def save_changes():
            # Get values
            full_name_val = fname_entry.get().strip()
            phone_val = phone_entry.get().strip()
            email_val = email_entry.get().strip()
            province_val = province_var.get().strip()
            city_val = city_var.get().strip()
            barangay_val = barangay_var.get().strip()
            postal_val = postal_entry.get().strip()


            # Check required fields
            if not full_name_val:
                messagebox.showerror("Error", "Full Name is required.")
                return
            if not phone_val:
                messagebox.showerror("Error", "Phone Number is required.")
                return
            if not email_val:
                messagebox.showerror("Error", "Email is required.")
                return
            if not province_val:
                messagebox.showerror("Error", "Province is required.")
                return
            if not city_val:
                messagebox.showerror("Error", "City is required.")
                return
            if not barangay_val:
                messagebox.showerror("Error", "Barangay is required.")
                return
            if not postal_val:
                messagebox.showerror("Error", "Postal Code is required.")
                return


            # ---------------- PHONE NUMBER AUTO +63 ----------------
            if not phone_val.startswith("+63"):
                # Remove leading zero if user typed 09xxxxxxxxx
                if phone_val.startswith("0") and len(phone_val) == 11:
                    phone_val = "+63" + phone_val[1:]
                else:
                    phone_val = "+63" + phone_val


            # ---------------- PHONE NUMBER VALIDATION ----------------
            phone_pattern = r'^\+63\d{10}$'  # +63 followed by 10 digits
            if not re.match(phone_pattern, phone_val):
                messagebox.showerror("Error", "Must enter a valid phone number.")
                return


            # Split full name
            parts = full_name_val.split(" ", 1)
            first_name_val = parts[0]
            last_name_val = parts[1] if len(parts) > 1 else ""


            # Update database
            update_user_profile(
                email_val,
                first_name=first_name_val,
                last_name=last_name_val,
                age=age_entry.get(),
                birthday=birthday_entry.get(),
                phone=phone_val,
                barangay=barangay_val,
                city=city_val,
                province=province_val,
                postal_code=postal_val,
                address=street_entry.get()
            )


            # Update labels
            email_label.configure(text=f"📧 {email_val}")
            phone_label.configure(text=f"📞 {phone_val}")
            img_label.configure(image=img_label.image)
            messagebox.showinfo("Success", "Profile updated successfully!")


        ctk.CTkButton(right, text="Save Changes", fg_color="#ff66aa", hover_color="#ff3385",
                      text_color="white", width=220, height=44, corner_radius=12,
                      font=("Arial", 16, "bold"), command=save_changes).pack(side="bottom", pady=(10, 20))


    # ================= PRODUCTS =================
    def show_products():
        for w in main.winfo_children():
            w.destroy()


        ctk.CTkLabel(main, text="Available Products", font=("Arial Black", 36, "bold"),
                     text_color="#cc0066", anchor="w").pack(anchor="w", padx=60, pady=(40, 10))


        top_frame = ctk.CTkFrame(main, fg_color="white")
        top_frame.pack(fill="x", padx=60, pady=(0, 10))


        cat_var = ctk.StringVar(value="All")
        search_var = ctk.StringVar()


        category_dropdown = ctk.CTkComboBox(top_frame, values=["All"] + categories, variable=cat_var,
                                            width=200, height=40, fg_color="#ffccdd",
                                            button_color="#ff66aa", button_hover_color="#ff3385",
                                            dropdown_fg_color="white", dropdown_text_color="black")
        category_dropdown.pack(side="left", padx=(0, 15))


        search_entry = ctk.CTkEntry(top_frame, textvariable=search_var, placeholder_text="Search product...",
                                    width=250, height=40, corner_radius=10, fg_color="#ffe6f2",
                                    text_color="black", font=("Arial", 16), border_width=0,
                                    placeholder_text_color="gray")
        search_entry.pack(side="left", padx=(0, 10))


        ctk.CTkButton(top_frame, text="Search", fg_color="#ff66aa", hover_color="#ff3385",
                      text_color="white", width=100, height=40, corner_radius=10,
                      font=("Arial", 16, "bold"), command=lambda: display_products()).pack(side="left")


        canvas = ctk.CTkCanvas(main, bg="white", highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True, padx=60, pady=(0, 20))
        scrollbar = ctk.CTkScrollbar(main, orientation="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=scrollbar.set)


        product_frame = ctk.CTkFrame(canvas, fg_color="white")
        canvas.create_window((0, 0), window=product_frame, anchor="nw")


        def on_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))


        product_frame.bind("<Configure>", on_configure)


        # ================= DISPLAY PRODUCTS FUNCTION =================
        def view_product_popup(product):
            # Open a new window
            popup = Toplevel()
            popup.title(product['name'])
            popup.geometry("400x550")
            popup.resizable(False, False)


            # Background frame
            frame = ctk.CTkFrame(popup, fg_color="white")
            frame.pack(fill="both", expand=True, padx=20, pady=20)


            # Product Image
            try:
                img_path = os.path.join("pics", product.get("img", "pr1.jpg"))
                img = Image.open(img_path).resize((350, 220))
                photo = ImageTk.PhotoImage(img)
                img_label = ctk.CTkLabel(frame, image=photo, text="")
                img_label.image = photo
                img_label.pack(pady=(0, 10))
            except:
                ctk.CTkLabel(frame, text="No Image", font=("Arial", 16), text_color="gray").pack(pady=(0, 10))


            # Product Name
            ctk.CTkLabel(frame, text=product['name'], font=("Arial Black", 18, "bold"),
                         text_color="#cc0066").pack(pady=(5, 5))


            # Product Price
            ctk.CTkLabel(frame, text=f"₱{product['price']}", font=("Arial", 16, "bold"),
                         text_color="black").pack(pady=(0, 10))


            # Product Description
            desc = product.get("description", "No description available.")
            desc_label = ctk.CTkLabel(frame, text=desc, font=("Arial", 14), text_color="gray",
                                      wraplength=350, justify="left")
            desc_label.pack(pady=(0, 10))


            # ================= QUANTITY SELECTION =================
            qty_frame = ctk.CTkFrame(frame, fg_color="white")
            qty_frame.pack(pady=(10, 0))
            ctk.CTkLabel(qty_frame, text="Quantity:", font=("Arial", 14, "bold"), text_color="black").pack(side="left",
                                                                                                           padx=(0, 5))
            qty_var = ctk.IntVar(value=1)
            qty_entry = ctk.CTkEntry(qty_frame, width=50, height=30, textvariable=qty_var, justify="center")
            qty_entry.pack(side="left")


            # Subtotal Label
            subtotal_var = ctk.StringVar(value=f"Subtotal: ₱{product['price']}")


            def update_subtotal(*args):
                try:
                    qty = int(qty_var.get())
                    subtotal_var.set(f"Subtotal: ₱{product['price'] * qty}")
                except:
                    subtotal_var.set(f"Subtotal: ₱{product['price']}")


            qty_var.trace("w", update_subtotal)
            ctk.CTkLabel(frame, textvariable=subtotal_var, font=("Arial", 16, "bold"), text_color="#ff3399").pack(
                pady=(10, 0))


            # Buttons
            btn_frame = ctk.CTkFrame(frame, fg_color="white")
            btn_frame.pack(pady=(15, 0))


            def add_to_cart_multiple(product, qty):
                for _ in range(qty):
                    add_to_cart(product)

            def add_order_multiple(username, product, qty):
                # Prepare the order items
                cart_items = [{
                    "name": product['name'],
                    "price": product['price'],
                    "quantity": qty
                }]

                # Add the order in one call
                order_id = add_order_full(username, cart_items)

                # Optionally, start a thread to process the product asynchronously
                threading.Thread(target=process_single_order, args=(username, product['name'])).start()

                messagebox.showinfo("Purchase", f"Order placed: {product['name']} x{qty}")

            ctk.CTkButton(btn_frame, text="Add to Cart", fg_color="#ff66aa", text_color="white",
                          hover_color="#ff3385", width=120, height=40,
                          command=lambda p=product, q=qty_var: add_to_cart_multiple(p, q.get())).pack(side="left",
                                                                                                      padx=(0, 5))


            ctk.CTkButton(btn_frame, text="Buy Now", fg_color="#cc0066", text_color="white",
                          hover_color="#99004d", width=120, height=40,
                          command=lambda p=product, q=qty_var: add_order_multiple(username, p, q.get())).pack(
                side="left", padx=(0, 5))


            # Automatically log browsing history
            from database import add_browsing_history
            add_browsing_history(username, product['name'], product['price'], product.get('img', 'pr1.jpg'))


        def display_products(*args):
            for widget in product_frame.winfo_children():
                widget.destroy()


            all_products = get_all_products()
            category_filter = cat_var.get()
            search_filter = search_var.get().lower().strip()


            filtered = all_products
            if category_filter != "All":
                filtered = [p for p in filtered if p.get("category") == category_filter]
            if search_filter:
                filtered = [p for p in filtered if search_filter in p["name"].lower()]


            if not filtered:
                ctk.CTkLabel(product_frame, text="No products found.", font=("Arial", 18),
                             text_color="gray").pack(pady=30)
                return


            columns = 3
            for i, product in enumerate(filtered):
                row, col = divmod(i, columns)
                box = ctk.CTkFrame(product_frame, fg_color="#ffe0f0", width=400, height=420)
                box.grid(row=row, column=col, padx=30, pady=15, sticky="n")


                try:
                    img_path = os.path.join("pics", product.get("img", "pr1.jpg"))
                    img = Image.open(img_path).resize((350, 220))
                    photo = ImageTk.PhotoImage(img)
                    label = ctk.CTkLabel(box, image=photo, text="")
                    label.image = photo
                    label.pack(pady=(0, 1))
                except:
                    ctk.CTkLabel(box, text="No Image", font=("Arial", 18), text_color="gray").pack(pady=(10, 8))


                ctk.CTkLabel(box, text=product['name'], font=("Arial", 17, "bold"), text_color="gray").pack()
                ctk.CTkLabel(box, text=f"₱{product['price']}", font=("Arial", 17, "bold"), text_color="black").pack()


                btn_frame = ctk.CTkFrame(box, fg_color="#ffe0f0")
                btn_frame.pack(pady=(10, 20))


                ctk.CTkButton(btn_frame, text="Add to Cart", fg_color="#ff66aa", text_color="white",
                              hover_color="#ff3385", width=120, height=40,
                              command=lambda p=product: add_to_cart(p)).pack(side="left", padx=(0, 5))


                ctk.CTkButton(btn_frame, text="View Product", fg_color="#ff99cc", text_color="white",
                              hover_color="#ff66aa", width=120, height=40,
                              command=lambda p=product: view_product_popup(p)).pack(side="left", padx=(0, 5))


                ctk.CTkButton(btn_frame, text="Buy Now", fg_color="#cc0066", text_color="white",
                              hover_color="#99004d", width=120, height=40,
                              command=lambda p=product: buy_now(p)).pack(side="left", padx=(0, 5))




        # ================= AUTO REFRESH =================
        def auto_refresh_products():
            display_products()
            main.after(5000, auto_refresh_products)  # refresh every 5 seconds


        display_products()  # initial display
        auto_refresh_products()  # start auto-refresh


    # ================= CART / ORDERS =================
    def add_to_cart(product):
        # Check if product already exists in cart
        for item in cart_items:
            if item['name'] == product['name']:  # or 'id' if you use unique IDs
                item['quantity'] += 1  # just increase the quantity
                # Do NOT show cart page here
                return

        # If product not in cart, add it with quantity 1
        product_copy = product.copy()
        product_copy['quantity'] = 1
        cart_items.append(product_copy)
        # Do NOT show cart page here either

    def buy_now(product):
        add_order_full(username, product['name'], product['price'], status="Pending")
        threading.Thread(target=process_single_order, args=(username, product['name'])).start()
        messagebox.showinfo("Purchase", f"Order placed: {product['name']}")

    def show_cart():
        global cart_items

        for w in main.winfo_children():
            w.destroy()

        # --- Colors ---
        dark_pink = "#C71585"
        light_pink = "#FF69B4"
        light_bg = "#ffe6f2"

        # --- Header ---
        ctk.CTkLabel(
            main, text="Your Cart",
            font=("Arial Black", 36, "bold"),
            text_color=dark_pink,
            anchor="w"
        ).pack(anchor="w", padx=60, pady=(40, 10))

        cart_frame = ctk.CTkFrame(main, fg_color="white")
        cart_frame.pack(fill="both", expand=True, padx=60, pady=10)

        # --- Variables ---
        total_price_var = ctk.StringVar(value="Total: ₱0")
        select_all_var = ctk.BooleanVar(value=True)

        # Initialize per-item variables
        for item in cart_items:
            item.setdefault("selected_var", ctk.BooleanVar(value=True))
            item.setdefault(
                "subtotal_var",
                ctk.StringVar(value=f"₱{item['price'] * item.get('quantity', 1)}")
            )

        # --- Compute Totals ---
        def update_total(*args):
            total = 0
            for item in cart_items:
                subtotal = item["price"] * item.get("quantity", 1)
                item["subtotal_var"].set(f"₱{subtotal}")

                if item["selected_var"].get():
                    total += subtotal

            total_price_var.set(f"Total: ₱{total}")

        # --- Select All ---
        def toggle_select_all():
            for item in cart_items:
                item["selected_var"].set(select_all_var.get())
            update_total()

        select_all_frame = ctk.CTkFrame(cart_frame, fg_color="white")
        select_all_frame.pack(fill="x", padx=20, pady=(0, 10))

        ctk.CTkCheckBox(
            select_all_frame,
            variable=select_all_var,
            text="Select All",
            text_color=dark_pink,
            checkmark_color=light_pink,
            fg_color="white",
            command=toggle_select_all
        ).pack(anchor="w")

        # --- Cart Items List ---
        for item in cart_items:
            item_frame = ctk.CTkFrame(cart_frame, fg_color=light_bg, corner_radius=12)
            item_frame.pack(fill="x", pady=10, padx=20)
            item_frame.grid_columnconfigure(1, weight=1)

            # Checkbox
            ctk.CTkCheckBox(
                item_frame,
                variable=item["selected_var"],
                text="",
                checkmark_color=light_pink,
                fg_color="white",
                command=update_total
            ).grid(row=0, column=0, padx=10, pady=10, sticky="w")

            # Info
            info_frame = ctk.CTkFrame(item_frame, fg_color=light_bg)
            info_frame.grid(row=0, column=1, sticky="w", padx=10, pady=10)

            ctk.CTkLabel(
                info_frame,
                text=item["name"],
                font=("Arial", 18, "bold"),
                text_color=dark_pink
            ).pack(anchor="w")

            # Price + Quantity
            price_qty_frame = ctk.CTkFrame(info_frame, fg_color=light_bg)
            price_qty_frame.pack(anchor="w", pady=(5, 0))

            ctk.CTkLabel(
                price_qty_frame,
                text=f"₱{item['price']}",
                font=("Arial", 16),
                text_color=dark_pink
            ).pack(side="left", padx=(0, 15))

            qty_var = ctk.IntVar(value=item.get("quantity", 1))

            def update_qty(v, i):
                i["quantity"] = v.get()
                update_total()

            # (-) button
            ctk.CTkButton(
                price_qty_frame, text="-", width=35, height=35,
                fg_color=light_pink, hover_color="#FF1493",
                text_color=dark_pink,
                command=lambda v=qty_var, i=item: (v.set(max(v.get() - 1, 1)), update_qty(v, i))
            ).pack(side="left")

            # qty number
            ctk.CTkLabel(
                price_qty_frame, textvariable=qty_var, width=40,
                font=("Arial", 16), text_color=dark_pink
            ).pack(side="left", padx=5)

            # (+) button
            ctk.CTkButton(
                price_qty_frame, text="+", width=35, height=35,
                fg_color=light_pink, hover_color="#FF1493",
                text_color=dark_pink,
                command=lambda v=qty_var, i=item: (v.set(v.get() + 1), update_qty(v, i))
            ).pack(side="left")

            # Subtotal
            ctk.CTkLabel(
                info_frame,
                textvariable=item["subtotal_var"],
                font=("Arial", 16, "bold"),
                text_color=dark_pink
            ).pack(anchor="w", pady=(5, 0))

            # Remove X button
            ctk.CTkButton(
                item_frame,
                text="X", width=40, height=40,
                fg_color=light_pink, hover_color="#FF1493",
                text_color="white",
                command=lambda i=item: (cart_items.remove(i), show_cart())
            ).grid(row=0, column=2, padx=10, pady=10)

        # ----------------------------
        # SINGLE VALID CHECKOUT LOGIC
        # ----------------------------
        def checkout():
            global cart_items

            selected_items = [i for i in cart_items if i["selected_var"].get()]

            if not selected_items:
                messagebox.showinfo("Info", "No items selected!")
                return

            # Add orders to DB
            for item in selected_items:
                add_order_full(
                    username=username,
                    product_id=item["product_id"],
                    quantity=item["quantity"],
                    price=item["price"],
                    status="To Ship"
                )

            # Remove selected items SAFELY
            cart_items = [i for i in cart_items if not i["selected_var"].get()]

            messagebox.showinfo("Success", "Checkout successful!")
            show_cart()

        # ----------------------------
        # FINAL SINGLE TOTAL + CHECKOUT BAR
        # ----------------------------
        bottom_frame = ctk.CTkFrame(main, fg_color="white")
        bottom_frame.pack(fill="x", padx=60, pady=(10, 20))

        ctk.CTkLabel(
            bottom_frame,
            textvariable=total_price_var,
            font=("Arial Black", 24, "bold"),
            text_color=dark_pink
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            bottom_frame,
            text="Checkout",
            fg_color=light_pink, hover_color="#FF1493",
            text_color="white",
            width=150, height=45,
            command=checkout
        ).pack(side="right", padx=10)

        update_total()

    def show_orders():
        # Clear screen
        for w in main.winfo_children():
            w.destroy()

        # Title
        ctk.CTkLabel(
            main,
            text="My Orders",
            font=("Arial Black", 36, "bold"),
            text_color="#cc0066"
        ).pack(anchor="w", padx=60, pady=(40, 20))

        # ----------------------------------------
        #           TAB BAR
        # ----------------------------------------
        tab_frame = ctk.CTkFrame(main, fg_color="transparent")
        tab_frame.pack()

        status_options = ["To Ship", "To Receive", "Completed", "Cancelled"]
        active_status = tk.StringVar(value="To Receive")

        def switch_tab(status):
            active_status.set(status)
            refresh_tabs()
            display_orders()

        def refresh_tabs():
            for w in tab_frame.winfo_children():
                w.destroy()

            for s in status_options:
                active = (s == active_status.get())

                ctk.CTkButton(
                    tab_frame,
                    text=s,
                    fg_color="#ff66aa" if active else "white",
                    text_color="white" if active else "#cc0066",
                    hover_color="#ff3385",
                    corner_radius=20,
                    width=130,
                    height=35,
                    border_width=2,
                    border_color="#ff66aa",
                    command=lambda x=s: switch_tab(x)
                ).pack(side="left", padx=8)

        refresh_tabs()

        # ----------------------------------------
        #       SCROLLING AREA
        # ----------------------------------------
        canvas = ctk.CTkCanvas(main, bg="white", highlightthickness=0)
        canvas.pack(fill="both", expand=True, padx=60, pady=20)

        scrollbar = ctk.CTkScrollbar(main, orientation="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")

        canvas.configure(yscrollcommand=scrollbar.set)

        order_frame = ctk.CTkFrame(canvas, fg_color="white")
        canvas.create_window((0, 0), window=order_frame, anchor="nw")

        def update_scroll(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        order_frame.bind("<Configure>", update_scroll)

        # ----------------------------------------
        #         DISPLAY ORDERS
        # ----------------------------------------
        def display_orders():
            for w in order_frame.winfo_children():
                w.destroy()

            orders = get_orders_by_user_full(username)
            orders = [o for o in orders if o["status"] == active_status.get()]

            if not orders:
                ctk.CTkLabel(order_frame, text="No orders under this category.",
                             text_color="gray", font=("Arial", 16)).pack(pady=20)
                return

            for order in orders:
                # Card
                card = ctk.CTkFrame(order_frame, fg_color="#FFF0F6", corner_radius=12)
                card.pack(fill="x", pady=10)

                # Header
                header = ctk.CTkFrame(card, fg_color="#FFF0F6")
                header.pack(fill="x", pady=(10, 5))

                ctk.CTkLabel(
                    header,
                    text=f"Order #{order['id']}",
                    font=("Arial Black", 18),
                    text_color="#C2185B"
                ).pack(side="left", padx=15)

                status_color = {
                    "To Ship": "#FF9800",
                    "To Receive": "#03A9F4",
                    "Completed": "#4CAF50",
                    "Cancelled": "#E53935"
                }.get(order["status"], "#777")

                ctk.CTkLabel(
                    header,
                    text=order["status"],
                    font=("Arial Black", 14),
                    text_color="white",
                    fg_color=status_color,
                    corner_radius=8,
                    width=110,
                    height=32
                ).pack(side="right", padx=15)

                # Product box
                product_box = ctk.CTkFrame(card, fg_color="white", corner_radius=10)
                product_box.pack(fill="x", padx=15, pady=10)

                # Image
                left = ctk.CTkFrame(product_box, fg_color="white")
                left.pack(side="left", padx=10, pady=10)

                try:
                    img = Image.open(order["image"])
                    img = img.resize((90, 90))
                    imgTk = ImageTk.PhotoImage(img)
                    label = tk.Label(left, image=imgTk, bg="white")
                    label.image = imgTk
                    label.pack()
                except:
                    tk.Label(left, text="📦", font=("Arial", 40), bg="white").pack()

                # Info
                info = ctk.CTkFrame(product_box, fg_color="white")
                info.pack(side="left", fill="both", expand=True, padx=10)

                ctk.CTkLabel(info, text=order["product_name"],
                             font=("Arial Black", 17), text_color="#C2185B").pack(anchor="w")

                ctk.CTkLabel(info, text=f"₱{order['price']}",
                             font=("Arial", 15)).pack(anchor="w")

                ctk.CTkLabel(info, text=f"Ordered: {order['date_ordered']}",
                             font=("Arial", 13), text_color="#777").pack(anchor="w")

                # Action
                if order["status"] == "To Receive":
                    ctk.CTkButton(
                        card,
                        text="Order Received",
                        fg_color="#4CAF50",
                        hover_color="#43A047",
                        text_color="white",
                        height=40,
                        corner_radius=10,
                        command=lambda oid=order["id"]: mark_as_received(oid)
                    ).pack(anchor="e", padx=20, pady=(0, 12))

        # ----------------------------------------
        #         STATUS CHANGE HANDLER
        # ----------------------------------------
        def mark_as_received(oid):
            update_order_status(oid, "Completed")
            display_orders()
            messagebox.showinfo("Success", "Order marked as received!")

        # Load orders initially
        display_orders()

    # ================= BROWSING HISTORY =================
    def show_browsing_history():
        for w in main.winfo_children():
            w.destroy()


        ctk.CTkLabel(main, text="Browsing History", font=("Arial Black", 36, "bold"),
                     text_color="#cc0066", anchor="w").pack(anchor="w", padx=60, pady=(40, 10))


        # Scrollable container
        canvas = ctk.CTkCanvas(main, bg="white", highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True, padx=60, pady=(0, 20))
        scrollbar = ctk.CTkScrollbar(main, orientation="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=scrollbar.set)


        history_frame = ctk.CTkFrame(canvas, fg_color="white")
        canvas.create_window((0, 0), window=history_frame, anchor="nw")


        def on_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))


        history_frame.bind("<Configure>", on_configure)


        # Fetch browsing history from database
        from database import get_browsing_history_by_user, add_browsing_history
        browsing_history = get_browsing_history_by_user(username)


        if not browsing_history:
            ctk.CTkLabel(history_frame, text="No browsing history yet.", font=("Arial", 20),
                         text_color="gray").pack(pady=50)
            return


        for item in browsing_history:
            frame = ctk.CTkFrame(history_frame, fg_color="#ffe6f2", corner_radius=10)
            frame.pack(pady=10, padx=20, fill="x")


            # Thumbnail
            try:
                img_path = os.path.join("pics", item.get("img", "pr1.jpg"))
                img = Image.open(img_path).resize((80, 80))
                photo = ImageTk.PhotoImage(img)
                label_img = ctk.CTkLabel(frame, image=photo, text="")
                label_img.image = photo
                label_img.pack(side="left", padx=10, pady=10)
            except:
                ctk.CTkLabel(frame, text="No Image", font=("Arial", 14), text_color="gray").pack(side="left", padx=10)


            # Details
            details = ctk.CTkFrame(frame, fg_color="white")
            details.pack(side="left", fill="x", expand=True, padx=10, pady=10)


            ctk.CTkLabel(details, text=item['name'], font=("Arial", 18, "bold"), text_color="#ff3399").pack(anchor="w")
            ctk.CTkLabel(details, text=f"₱{item['price']}", font=("Arial", 16), text_color="black").pack(anchor="w")
            ctk.CTkLabel(details, text=f"Viewed on: {item['date']}", font=("Arial", 14), text_color="gray").pack(
                anchor="w")


            # View Again button
            ctk.CTkButton(frame, text="View Again", fg_color="#ff66aa", hover_color="#ff3385",
                          text_color="white", width=120, height=35,
                          command=lambda p=item: view_product_again(p)).pack(side="right", padx=10)

    # ================= FUNCTION TO SHOW PRODUCT AGAIN AND LOG =================
    def view_product_again(product):
        # Open a new window
        popup = Toplevel()
        popup.title(product['name'])
        popup.geometry("400x550")
        popup.resizable(False, False)


        # Background frame
        frame = ctk.CTkFrame(popup, fg_color="white")
        frame.pack(fill="both", expand=True, padx=20, pady=20)


        # Product Image
        try:
            img_path = os.path.join("pics", product.get("img", "pr1.jpg"))
            img = Image.open(img_path).resize((350, 220))
            photo = ImageTk.PhotoImage(img)
            img_label = ctk.CTkLabel(frame, image=photo, text="")
            img_label.image = photo
            img_label.pack(pady=(0, 10))
        except:
            ctk.CTkLabel(frame, text="No Image", font=("Arial", 16), text_color="gray").pack(pady=(0, 10))


        # Product Name
        ctk.CTkLabel(frame, text=product['name'], font=("Arial Black", 18, "bold"),
                     text_color="#cc0066").pack(pady=(5, 5))


        # Product Price
        ctk.CTkLabel(frame, text=f"₱{product['price']}", font=("Arial", 16, "bold"),
                     text_color="black").pack(pady=(0, 10))


        # Product Description
        desc = product.get("description", "No description available.")
        desc_label = ctk.CTkLabel(frame, text=desc, font=("Arial", 14), text_color="gray",
                                  wraplength=350, justify="left")
        desc_label.pack(pady=(0, 10))


        # Quantity Selector
        qty_frame = ctk.CTkFrame(frame, fg_color="white")
        qty_frame.pack(pady=(10, 0))
        ctk.CTkLabel(qty_frame, text="Quantity:", font=("Arial", 14, "bold"), text_color="black").pack(side="left",
                                                                                                       padx=(0, 5))
        qty_var = ctk.IntVar(value=1)
        qty_entry = ctk.CTkEntry(qty_frame, width=50, height=30, textvariable=qty_var, justify="center")
        qty_entry.pack(side="left")


        # Subtotal Label
        subtotal_var = ctk.StringVar(value=f"Subtotal: ₱{product['price']}")


        def update_subtotal(*args):
            try:
                qty = int(qty_var.get())
                subtotal_var.set(f"Subtotal: ₱{product['price'] * qty}")
            except:
                subtotal_var.set(f"Subtotal: ₱{product['price']}")


        qty_var.trace("w", update_subtotal)
        ctk.CTkLabel(frame, textvariable=subtotal_var, font=("Arial", 16, "bold"), text_color="#ff3399").pack(
            pady=(10, 0))


        # Add to Cart / Buy Now buttons
        btn_frame = ctk.CTkFrame(frame, fg_color="white")
        btn_frame.pack(pady=(15, 0))


        def add_to_cart_multiple(product, qty):
            for _ in range(qty):
                add_to_cart(product)

        def add_order_multiple(username, product, qty):
            # Create a list of items in the cart format
            cart_items = [{
                "name": product['name'],
                "price": product['price'],
                "quantity": qty
            }]

            # Add the order using the new database function
            order_id = add_order_full(username, cart_items)

            # Optionally, start a thread to process each product individually (if needed)
            threading.Thread(target=process_single_order, args=(username, product['name'])).start()

            messagebox.showinfo("Purchase", f"Order placed: {product['name']} x{qty}")

        ctk.CTkButton(btn_frame, text="Add to Cart", fg_color="#ff66aa", text_color="white",
                      hover_color="#ff3385", width=120, height=40,
                      command=lambda p=product, q=qty_var: add_to_cart_multiple(p, q.get())).pack(side="left",
                                                                                                  padx=(0, 5))


        ctk.CTkButton(btn_frame, text="Buy Now", fg_color="#cc0066", text_color="white",
                      hover_color="#99004d", width=120, height=40,
                      command=lambda p=product, q=qty_var: add_order_multiple(username, p, q.get())).pack(side="left",
                                                                                                          padx=(0, 5))


        # Automatically log this view in database
        from database import add_browsing_history
        add_browsing_history(username, product['name'], product['price'], product.get('img', 'pr1.jpg'))


    # ================= LOGOUT =================
    def logout():
        if messagebox.askyesno("Confirm Logout", "Are you sure you want to logout?"):
            logout_callback()


    # ================= PROCESS ORDERS =================
    def process_single_order(user_email, product_name):
        time.sleep(1)
        orders = get_orders_by_user_full(logged_user_email)
        target = None

        # Search through orders and their items for the product
        for order in reversed(orders):
            for item in order['items']:
                if item['name'] == product_name and order['status'] == "Pending":
                    target = order['id']
                    break
            if target is not None:
                break

        if target is None:
            return

        # Update order status sequentially
        update_order_status(target, "Processing")
        time.sleep(3)
        update_order_status(target, "Shipped")
        time.sleep(3)
        update_order_status(target, "Delivered")

    # ================= SIDEBAR BUTTONS =================
    buttons = [
        ("👤   Profile", show_profile),
        ("📦   Products", show_products),
        ("🛒   Cart", show_cart),
        ("📝   Orders", show_orders),
        ("🕒   Browsing History", show_browsing_history)
    ]


    for text, func in buttons:
        ctk.CTkButton(sidebar, text="     " + text, command=func,
                      fg_color="#ff99cc", hover_color="#ff66aa",
                      text_color="white", width=300, height=60,
                      corner_radius=0, font=("Arial", 25, "bold"), anchor="w").pack(pady=7)


    ctk.CTkButton(sidebar, text="     🔓   Logout", command=logout,
                  fg_color="#ff99cc", hover_color="#ff66aa",
                  text_color="white", width=300, height=60,
                  corner_radius=0, font=("Arial", 25, "bold"), anchor="w").pack(side="bottom", pady=0)


    show_profile()  # default page

# ================= RUN APPLICATION =================
if __name__ == "__main__":
    root = ctk.CTk()
    app = dashboard_page(root)
    root.mainloop()
