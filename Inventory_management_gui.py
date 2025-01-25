import tkinter as tk
from tkinter import messagebox, ttk
from inventory_management_backend import InventoryManagementSystem
from datetime import datetime

# Color scheme and fonts
BG_COLOR = "#E8F0F8"  # Light blue background
SECONDARY_BG = "#D1E2F2"  # Slightly darker blue for contrast
BUTTON_COLOR = "#C4D7ED"  # Medium light blue for buttons
TEXT_COLOR = "#000000"  # Solid black for text
TITLE_FONT = ('Roboto', 24, 'bold')
LABEL_FONT = ('Open Sans', 12)
ENTRY_FONT = ('Open Sans', 12)
BUTTON_FONT = ('Roboto', 12, 'bold')

class LoginWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Inventory Management System - Login")
        self.root.geometry("400x500")
        self.root.config(bg=BG_COLOR)
        
        self.ims = InventoryManagementSystem()
        
        # Configure styles
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('Custom.TButton',
                           font=BUTTON_FONT,
                           background=BUTTON_COLOR,
                           foreground=TEXT_COLOR,
                           padding=10)
        
        # Title
        title_label = tk.Label(self.root, text="Login", 
                             font=TITLE_FONT, bg=BG_COLOR, fg=TEXT_COLOR)
        title_label.pack(pady=30)
        
        # Role selection
        role_frame = tk.Frame(self.root, bg=BG_COLOR)
        role_frame.pack(pady=20)
        
        self.role_var = tk.StringVar(value="admin")
        tk.Radiobutton(role_frame, text="Admin", variable=self.role_var, 
                      value="admin", bg=BG_COLOR).pack(side=tk.LEFT, padx=10)
        tk.Radiobutton(role_frame, text="Cashier", variable=self.role_var, 
                      value="cashier", bg=BG_COLOR).pack(side=tk.LEFT, padx=10)
        
        # Username
        tk.Label(self.root, text="Username:", 
                font=LABEL_FONT, bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=5)
        self.username_entry = ttk.Entry(self.root, font=ENTRY_FONT)
        self.username_entry.pack(pady=5)
        
        # Password
        tk.Label(self.root, text="Password:", 
                font=LABEL_FONT, bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=5)
        self.password_entry = ttk.Entry(self.root, font=ENTRY_FONT, show="*")
        self.password_entry.pack(pady=5)
        
        # Login button
        ttk.Button(self.root, text="Login", 
                  command=self.login, style='Custom.TButton').pack(pady=20)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        role = self.role_var.get()
        
        user_role = self.ims.authenticate_user(username, password)
        
        if user_role == role:
            self.root.withdraw()  # Hide login window
            if role == "admin":
                AdminInterface(self.ims, username, self)
            else:
                CashierInterface(self.ims, username, self)
        else:
            messagebox.showerror("Error", "Invalid credentials or role!")

    def show(self):
        self.root.deiconify()  # Show login window

    def run(self):
        self.root.mainloop()

class AdminInterface:
    def __init__(self, ims, username, login_window):
        self.root = tk.Toplevel()
        self.root.title(f"Admin Interface - {username}")
        self.root.geometry("800x600")
        self.root.config(bg=BG_COLOR)
        self.ims = ims
        self.username = username
        self.login_window = login_window
        
        # Configure styles
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('Custom.TButton',
                           font=BUTTON_FONT,
                           background=BUTTON_COLOR,
                           foreground=TEXT_COLOR,
                           padding=10)
        
        # Title
        title_label = tk.Label(self.root, text="Admin Dashboard", 
                             font=TITLE_FONT, bg=BG_COLOR, fg=TEXT_COLOR)
        title_label.pack(pady=30)
        
        # Buttons frame
        button_frame = tk.Frame(self.root, bg=BG_COLOR)
        button_frame.pack(pady=20)
        
        buttons = [
            ("Add Product", self.show_add_product_form),
            ("View Inventory", self.view_inventory),
            ("Update Product", self.update_product),
            ("Delete Product", self.delete_product),
            ("View Sales", self.view_sales),
            ("Manage Cashiers", self.manage_cashiers),
            ("Logout", self.logout)
        ]
        
        for text, command in buttons:
            ttk.Button(button_frame, text=text, command=command, 
                      style='Custom.TButton', width=20).pack(pady=10)

        self.root.protocol("WM_DELETE_WINDOW", self.logout)

    def show_add_product_form(self):
        form_window = tk.Toplevel(self.root)
        form_window.title("Add Product")
        form_window.geometry("400x500")
        form_window.config(bg=BG_COLOR)

        # Title
        title_label = tk.Label(form_window, text="Add New Product", 
                             font=('Roboto', 16, 'bold'), bg=BG_COLOR, fg=TEXT_COLOR)
        title_label.pack(pady=20)

        # Create form fields
        labels = ["Product Name:", "Category:", "Price:", "Quantity:"]
        entries = []

        for label in labels:
            tk.Label(form_window, text=label, font=LABEL_FONT, 
                    bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=5)
            entry = ttk.Entry(form_window, font=ENTRY_FONT)
            entry.pack(pady=5)
            entries.append(entry)

        def submit_product():
            try:
                name = entries[0].get()
                category = entries[1].get()
                price = float(entries[2].get())
                quantity = int(entries[3].get())

                if self.ims.add_product(name, category, price, quantity):
                    messagebox.showinfo("Success", "Product added successfully!")
                    form_window.destroy()
                else:
                    messagebox.showerror("Error", "Failed to add product!")
            except ValueError:
                messagebox.showerror("Error", "Invalid price or quantity!")

        ttk.Button(form_window, text="Add Product", 
                  command=submit_product, style='Custom.TButton').pack(pady=20)

    def view_inventory(self):
        inventory_window = tk.Toplevel(self.root)
        inventory_window.title("Current Inventory")
        inventory_window.geometry("800x600")
        inventory_window.config(bg=BG_COLOR)

        # Create Treeview
        columns = ('ID', 'Name', 'Category', 'Price', 'Quantity')
        tree = ttk.Treeview(inventory_window, columns=columns, show='headings')

        # Define headings
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(inventory_window, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        tree.pack(pady=20, padx=20, fill='both', expand=True)

        # Fetch and display inventory
        inventory = self.ims.view_inventory()
        for item in inventory:
            tree.insert('', 'end', values=item)

    def update_product(self):
        update_window = tk.Toplevel(self.root)
        update_window.title("Update Product")
        update_window.geometry("400x600")
        update_window.config(bg=BG_COLOR)

        # Title
        title_label = tk.Label(update_window, text="Update Product", 
                             font=('Roboto', 16, 'bold'), bg=BG_COLOR, fg=TEXT_COLOR)
        title_label.pack(pady=20)

        # Product ID
        tk.Label(update_window, text="Product ID:", font=LABEL_FONT, 
                bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=5)
        id_entry = ttk.Entry(update_window, font=ENTRY_FONT)
        id_entry.pack(pady=5)

        # Other fields
        labels = ["New Name (optional):", "New Category (optional):", 
                 "New Price (optional):", "New Quantity (optional):"]
        entries = []

        for label in labels:
            tk.Label(update_window, text=label, font=LABEL_FONT, 
                    bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=5)
            entry = ttk.Entry(update_window, font=ENTRY_FONT)
            entry.pack(pady=5)
            entries.append(entry)

        def submit_update():
            try:
                product_id = int(id_entry.get())
                name = entries[0].get() or None
                category = entries[1].get() or None
                price = float(entries[2].get()) if entries[2].get() else None
                quantity = int(entries[3].get()) if entries[3].get() else None

                if self.ims.update_product(product_id, name, category, price, quantity):
                    messagebox.showinfo("Success", "Product updated successfully!")
                    update_window.destroy()
                else:
                    messagebox.showerror("Error", "Failed to update product!")
            except ValueError:
                messagebox.showerror("Error", "Invalid input!")

        ttk.Button(update_window, text="Update Product", 
                  command=submit_update, style='Custom.TButton').pack(pady=20)

    def delete_product(self):
        delete_window = tk.Toplevel(self.root)
        delete_window.title("Delete Product")
        delete_window.geometry("300x200")
        delete_window.config(bg=BG_COLOR)

        tk.Label(delete_window, text="Enter Product ID:", font=LABEL_FONT, 
                bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=20)
        id_entry = ttk.Entry(delete_window, font=ENTRY_FONT)
        id_entry.pack(pady=10)

        def confirm_delete():
            try:
                product_id = int(id_entry.get())
                if messagebox.askyesno("Confirm", "Are you sure you want to delete this product?"):
                    if self.ims.delete_product(product_id):
                        messagebox.showinfo("Success", "Product deleted successfully!")
                        delete_window.destroy()
                    else:
                        messagebox.showerror("Error", "Failed to delete product!")
            except ValueError:
                messagebox.showerror("Error", "Invalid product ID!")

        ttk.Button(delete_window, text="Delete Product", 
                  command=confirm_delete, style='Custom.TButton').pack(pady=20)

    def view_sales(self):
        sales_window = tk.Toplevel(self.root)
        sales_window.title("Sales Records")
        sales_window.geometry("1000x600")
        sales_window.config(bg=BG_COLOR)

        # Create Treeview
        columns = ('ID', 'Invoice', 'Product', 'Quantity', 'Total Price', 'Date', 'Cashier')
        tree = ttk.Treeview(sales_window, columns=columns, show='headings')

        # Define headings
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=140)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(sales_window, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        tree.pack(pady=20, padx=20, fill='both', expand=True)

        # Fetch and display sales
        sales = self.ims.view_sales()
        for sale in sales:
            tree.insert('', 'end', values=sale)

    def manage_cashiers(self):
        cashier_window = tk.Toplevel(self.root)
        cashier_window.title("Manage Cashiers")
        cashier_window.geometry("400x500")
        cashier_window.config(bg=BG_COLOR)

        # Add Cashier Frame
        add_frame = tk.LabelFrame(cashier_window, text="Add New Cashier", 
                                bg=BG_COLOR, fg=TEXT_COLOR)
        add_frame.pack(pady=10, padx=10, fill="x")

        tk.Label(add_frame, text="Username:", 
                bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=5)
        username_entry = ttk.Entry(add_frame)
        username_entry.pack(pady=5)

        tk.Label(add_frame, text="Password:", 
                bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=5)
        password_entry = ttk.Entry(add_frame, show="*")
        password_entry.pack(pady=5)

        def add_cashier():
            username = username_entry.get()
            password = password_entry.get()
            if self.ims.add_cashier(username, password):
                messagebox.showinfo("Success", "Cashier added successfully!")
                list_cashiers()
            else:
                messagebox.showerror("Error", "Failed to add cashier!")

        ttk.Button(add_frame, text="Add Cashier", 
                  command=add_cashier, style='Custom.TButton').pack(pady=10)

        # List Cashiers Frame
        list_frame = tk.LabelFrame(cashier_window, text="Current Cashiers", 
                                 bg=BG_COLOR, fg=TEXT_COLOR)
        list_frame.pack(pady=10, padx=10, fill="both", expand=True)

        cashier_listbox = tk.Listbox(list_frame, font=LABEL_FONT)
        cashier_listbox.pack(pady=10, fill="both", expand=True)

        def list_cashiers():
            cashier_listbox.delete(0, tk.END)
            cashiers = self.ims.list_cashiers()
            for cashier in cashiers:
                cashier_listbox.insert(tk.END, cashier)

        def remove_cashier():
            selection = cashier_listbox.curselection()
            if selection:
                username = cashier_listbox.get(selection[0])
                if messagebox.askyesno("Confirm", f"Remove cashier {username}?"):
                    if self.ims.remove_cashier(username):
                        messagebox.showinfo("Success", "Cashier removed successfully!")
                        list_cashiers()
                    else:
                        messagebox.showerror("Error", "Failed to remove cashier!")

        ttk.Button(list_frame, text="Remove Selected Cashier", 
                  command=remove_cashier, style='Custom.TButton').pack(pady=10)

        list_cashiers()

    def logout(self):
        self.root.destroy()
        self.login_window.show()

# ... [CashierInterface class remains the same] ...

if __name__ == "__main__":
    login = LoginWindow()
    login.run()
