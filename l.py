import tkinter as tk
from tkinter import messagebox, ttk
import json
from datetime import datetime
from PIL import Image, ImageTk
import os
#tes
#halo dafis aron

class LoginWindow:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("🐾 Pawsome Pet Shop Login 🐾")
        self.window.geometry("1920x1080")
        self.window.configure(bg="#f0f0f0")
        
        
        if not os.path.exists("users.json"):
            default_users = {
                "admin": {"password": "admin123", "balance": 5000000},
                "kasir": {"password": "kasir123", "balance": 5000000}
            }
            with open("users.json", "w") as f:
                json.dump(default_users, f)
        
        self.create_widgets()
        
    def create_widgets(self):

        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        

        title_label = tk.Label(
            main_frame,
            text="🐾 Kantin UNESA 🐾",
            font=("Helvetica", 30, "bold"),
            bg="#f0f0f0"
        )
        title_label.pack(pady=10)
        
       
        login_frame = ttk.Frame(main_frame)
        login_frame.pack(fill=tk.BOTH, expand=True, pady=50)
        
        
        ttk.Label(login_frame, text="Email:", font=("Helvetica", 10, "bold")).pack(pady=5)
        self.username_entry = ttk.Entry(login_frame)
        self.username_entry.configure(width=100)
        self.username_entry.pack(pady=15)
        self.username_entry.pack(ipady=10)
        
        
        ttk.Label(login_frame, text="Password:").pack(pady=5)
        self.password_entry = ttk.Entry(login_frame, show="*")
        self.password_entry.pack(pady=5, ipady=10)
        self.password_entry.configure(width=100)
        
        
        login_button = ttk.Button(
            login_frame,
            text="Login",
            command=self.login
        )
        login_button.pack(pady=20)
        
    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Database User tidak ditemukan")
            return
        
        try:
            with open("users.json", "r") as f:
                users = json.load(f)
        except FileNotFoundError:
            messagebox.showerror("Error", "Database User tidak ditemukan")
            return
        
        if username in users and users[username]["password"] == password:
            messagebox.showinfo("Success", "Login successful!")
            self.window.destroy()
            root = tk.Tk()
            app = PetShopApp(root, username, users[username]["balance"])
            root.mainloop()
        else:
            messagebox.showerror("Error", "Invalid username or password!")

class PetShopApp:
    def __init__(self, root, username, initial_balance):
        self.root = root
        self.root.title("🐾 Pawsome Pet Shop 🐾")
        self.root.geometry("1920x1080")
        self.root.configure(bg="#f0f0f0")
        
        self.username = username
        self.current_balance = initial_balance
        
        # Menyiapkan cache untuk gambar
        self.image_cache = {}
        
        # Data produk dengan path gambar
        self.products = {
            "Mie": {
                "price": 2500000,
                "stock": 5,
                "category": "Hewan",
                "image": "Mie.jpg"
            },
            "Kucing Anggora": {
                "price": 2000000,
                "stock": 3,
                "category": "Hewan",
                "image": "images/angora.jpg"
            },
            "Royal Canin": {
                "price": 150000,
                "stock": 20,
                "category": "Makanan",
                "image": "images/royal_canin.jpg"
            },
            "Whiskas": {
                "price": 85000,
                "stock": 30,
                "category": "Makanan",
                "image": "images/whiskas.jpg"
            },
            "Kandang Premium": {
                "price": 750000,
                "stock": 10,
                "category": "Aksesoris",
                "image": "images/cage.jpg"
            },
            "Mainan Kucing": {
                "price": 45000,
                "stock": 25,
                "category": "Aksesoris",
                "image": "images/toy.jpg"
            },
        }
        
        self.cart = {}
        self.create_widgets()
        self.load_transaction_history()
        
    def create_widgets(self):
        # Frame utama dengan proporsi 70-30
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header Frame
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(header_frame, 
                text="🐾 Pawsome Pet Shop 🐾", 
                font=("Helvetica", 24, "bold")).pack(side=tk.LEFT, padx=10)
        
        self.balance_label = tk.Label(header_frame,
                                    text=f"Saldo: Rp {self.current_balance:,}",
                                    font=("Helvetica", 12))
        self.balance_label.pack(side=tk.RIGHT, padx=10)
        
        # Container untuk produk dan keranjang
        content_frame = ttk.Frame(self.main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Frame produk (kiri, 70%)
        product_frame = ttk.Frame(content_frame)
        product_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Filter Frame
        filter_frame = ttk.Frame(product_frame)
        filter_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(filter_frame, text="Filter:").pack(side=tk.LEFT, padx=5)
        categories = ["Semua", "Hewan", "Makanan", "Aksesoris"]
        self.category_var = tk.StringVar(value="Semua")
        for category in categories:
            ttk.Radiobutton(filter_frame, text=category, value=category,
                          variable=self.category_var,
                          command=self.filter_products).pack(side=tk.LEFT, padx=5)
        
        # Scrollable Product Frame
        product_scroll = ttk.Frame(product_frame)
        product_scroll.pack(fill=tk.BOTH, expand=True)
        
        self.product_canvas = tk.Canvas(product_scroll)
        scrollbar = ttk.Scrollbar(product_scroll, orient="vertical", 
                                command=self.product_canvas.yview)
        
        self.product_grid = ttk.Frame(self.product_canvas)
        
        self.product_canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.product_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.canvas_frame = self.product_canvas.create_window(
            (0, 0),
            window=self.product_grid,
            anchor="w",
            width=self.product_canvas.winfo_reqwidth()
        )
        
        # Frame keranjang (kanan, 30%)
        cart_frame = ttk.Frame(content_frame)
        cart_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=(5, 0))
        
        tk.Label(cart_frame, text="🛒 Keranjang Belanja",
                font=("Helvetica", 14, "bold")).pack(pady=10)
        
        self.cart_text = tk.Text(cart_frame, height=15, width=35)
        self.cart_text.pack(padx=10, pady=5)
        
        self.total_label = tk.Label(cart_frame, text="Total: Rp 0",
                                  font=("Helvetica", 12, "bold"))
        self.total_label.pack(pady=5)
        
        ttk.Button(cart_frame, text="Checkout",
                  command=self.checkout).pack(pady=5)
        
        ttk.Button(cart_frame, text="Riwayat Transaksi",
                  command=self.show_history).pack(pady=5)
        
        # Bind events
        self.product_grid.bind("<Configure>", self.on_frame_configure)
        self.product_canvas.bind("<Configure>", self.on_canvas_configure)
        
        # Tampilkan produk
        self.display_products()

    def load_and_resize_image(self, image_path, size=(150, 150)):
        """Load gambar dan resize sesuai ukuran yang diinginkan"""
        try:
            if image_path not in self.image_cache:
                image = Image.open(image_path)
                image = image.resize(size, Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                self.image_cache[image_path] = photo
            return self.image_cache[image_path]
        except Exception as e:
            print(f"Error loading image {image_path}: {e}")
            return self.get_placeholder_image(size)

    def get_placeholder_image(self, size=(150, 150)):
        """Membuat placeholder image jika gambar tidak ditemukan"""
        if 'placeholder' not in self.image_cache:
            img = Image.new('RGB', size, color='lightgray')
            photo = ImageTk.PhotoImage(img)
            self.image_cache['placeholder'] = photo
        return self.image_cache['placeholder']

    def display_products(self):
        # Hapus produk yang ada
        for widget in self.product_grid.winfo_children():
            widget.destroy()
        
        # Filter produk berdasarkan kategori
        filtered_products = {}
        selected_category = self.category_var.get()
        
        for name, details in self.products.items():
            if selected_category == "Semua" or details["category"] == selected_category:
                filtered_products[name] = details
        
        # Tampilkan produk dalam grid
        row = 0
        col = 0
        for name, details in filtered_products.items():
            product_frame = ttk.Frame(self.product_grid)
            product_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            
            # Load dan tampilkan gambar
            image_path = details["image"]
            photo = self.load_and_resize_image(image_path)
            image_label = tk.Label(product_frame, image=photo)
            image_label.image = photo
            image_label.pack(pady=5)
            
            tk.Label(product_frame, text=name,
                    font=("Helvetica", 10, "bold")).pack()
            
            tk.Label(product_frame, 
                    text=f"Rp {details['price']:,}").pack()
            
            tk.Label(product_frame,
                    text=f"Stok: {details['stock']}").pack()
            
            buy_button = ttk.Button(product_frame, text="+ Keranjang")
            buy_button.configure(command=self.create_buy_command(name))
            buy_button.pack(pady=5)
            
            col += 1
            if col > 2:
                col = 0
                row += 1
        
        # Konfigurasi grid
        for i in range(3):
            self.product_grid.grid_columnconfigure(i, weight=1)

    def create_buy_command(self, product_name):
        def buy_click():
            self.add_to_cart(product_name)
        return buy_click

    def update_cart_display(self):
        self.cart_text.delete(1.0, tk.END)
        total = 0
        
        for product, quantity in self.cart.items():
            price = self.products[product]["price"]
            subtotal = price * quantity
            total = total + subtotal
            
            self.cart_text.insert(tk.END,
                                f"{product} x{quantity}\n"
                                f"Rp {price:,} x {quantity} = Rp {subtotal:,}\n\n")
        
        self.total_label.config(text=f"Total: Rp {total:,}")

    def checkout(self):
        if len(self.cart) == 0:
            messagebox.showwarning("Keranjang Kosong", 
                                 "Silakan tambahkan produk ke keranjang terlebih dahulu!")
            return
        
        total = 0
        for product, quantity in self.cart.items():
            price = self.products[product]["price"]
            total = total + (price * quantity)
        
        if total > self.current_balance:
            messagebox.showerror("Saldo Tidak Cukup",
                               "Maaf, saldo Anda tidak mencukupi untuk melakukan pembelian ini!")
            return
        
        self.current_balance = self.current_balance - total
        self.balance_label.config(text=f"Saldo: Rp {self.current_balance:,}")
        
        transaction = {
            "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "items": dict(self.cart),
            "total": total
        }
        self.save_transaction(transaction)
        
        self.cart.clear()
        self.update_cart_display()
        
        messagebox.showinfo("Sukses", "Terima kasih atas pembelian Anda!")

    def add_to_cart(self, product_name):
        if self.products[product_name]["stock"] > 0:
            if product_name in self.cart:
                self.cart[product_name] = self.cart[product_name] + 1
            else:
                self.cart[product_name] = 1
                
            self.products[product_name]["stock"] = self.products[product_name]["stock"] - 1
            self.update_cart_display()
            self.display_products()
        else:
            messagebox.showwarning("Stok Habis", f"Maaf, {product_name} sedang kosong!")

    def save_transaction(self, transaction):
        try:
            with open("transactions.json", "r") as f:
                transactions = json.load(f)
        except FileNotFoundError:
            transactions = []
        
        transactions.append(transaction)
        
        with open("transactions.json", "w") as f:
            json.dump(transactions, f)

    def load_transaction_history(self):
        try:
            with open("transactions.json", "r") as f:
                self.transactions = json.load(f)
        except FileNotFoundError:
            self.transactions = []

    def show_history(self):
        history_window = tk.Toplevel(self.root)
        history_window.title("Riwayat Transaksi")
        history_window.geometry("500x400")
        
        columns = ("Tanggal", "Total")
        tree = ttk.Treeview(history_window, columns=columns, show="headings")
        
        tree.heading("Tanggal", text="Tanggal")
        tree.heading("Total", text="Total")
        
        scrollbar = ttk.Scrollbar(history_window, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
        
        for transaction in self.transactions:
            tree.insert("", tk.END, values=(
                transaction["datetime"],
                f"Rp {transaction['total']:,}"
            ))
            
        def show_details(event):
            selected_item = tree.selection()
            if len(selected_item) > 0:
                item = selected_item[0]
                transaction = self.transactions[tree.index(item)]
                
                details = "Detail Pembelian:\n\n"
                for product, quantity in transaction["items"].items():
                    price = self.products[product]["price"]
                    subtotal = price * quantity
                    details = details + f"{product} x{quantity}\n"
                    details = details + f"Rp {price:,} x {quantity} = Rp {subtotal:,}\n\n"
                
                messagebox.showinfo("Detail Transaksi", details)
        
        tree.bind("<Double-1>", show_details)
            
    def on_frame_configure(self, event=None):
        self.product_canvas.configure(scrollregion=self.product_canvas.bbox("all"))
    
    def on_canvas_configure(self, event):
        self.product_canvas.itemconfig(self.canvas_frame, width=event.width)

    def filter_products(self):
        self.display_products()


app = LoginWindow()
app.window.mainloop()