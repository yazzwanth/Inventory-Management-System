import mysql.connector
from mysql.connector import Error
import logging
import hashlib
from datetime import datetime

# Set up logging
logging.basicConfig(
    filename='inventory_management.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class InventoryManagementSystem:
    def __init__(self):
        """Initialize connection to the MySQL database."""
        try:
            self.connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="inventory_management"
            )
            if self.connection.is_connected():
                logging.info("Connected to MySQL database: inventory_management")
                self._initialize_default_users()
        except Error as e:
            logging.error(f"Database connection failed: {e}")
            self.connection = None
            raise SystemExit("Cannot proceed without database connection")

    def _initialize_default_users(self):
        """Initialize default admin and cashier users if they don't exist."""
        try:
            cursor = self.connection.cursor()
            
            # Check if default users exist
            cursor.execute("SELECT * FROM users WHERE username IN ('ADMIN', 'CASHIER')")
            existing_users = cursor.fetchall()
            
            # Hash the default password (123456)
            default_password = hashlib.sha256("123456".encode()).hexdigest()
            
            if not any(user[1] == 'ADMIN' for user in existing_users):
                cursor.execute("""
                    INSERT INTO users (username, password_hash, role) 
                    VALUES ('ADMIN', %s, 'admin')
                """, (default_password,))
            
            if not any(user[1] == 'CASHIER' for user in existing_users):
                cursor.execute("""
                    INSERT INTO users (username, password_hash, role) 
                    VALUES ('CASHIER', %s, 'cashier')
                """, (default_password,))
            
            self.connection.commit()
            logging.info("Default users initialized")
        except Error as e:
            logging.error(f"Error initializing default users: {e}")

    def _check_connection(self):
        """Helper method to check if the database connection exists."""
        if not self.connection:
            logging.warning("No database connection available")
            return False
        return True

    def authenticate_user(self, username, password):
        """Authenticate user and return role if successful."""
        if not self._check_connection():
            return None
        
        try:
            cursor = self.connection.cursor()
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            
            query = "SELECT role FROM users WHERE username = %s AND password_hash = %s"
            cursor.execute(query, (username, password_hash))
            result = cursor.fetchone()
            
            if result:
                logging.info(f"User {username} authenticated successfully")
                return result[0]
            else:
                logging.warning(f"Failed login attempt for user {username}")
                return None
        except Error as e:
            logging.error(f"Authentication error: {e}")
            return None

    def add_product(self, name, category, price, quantity):
        """Add a new product to the inventory."""
        if not self._check_connection():
            return False
        try:
            if not name or not category or price <= 0 or quantity < 0:
                logging.warning("Invalid product details provided")
                return False

            cursor = self.connection.cursor()
            query = "INSERT INTO products (name, category, price, quantity) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (name, category, price, quantity))
            self.connection.commit()
            logging.info(f"Product added: {name}, {category}, ${price}, {quantity} units")
            return True
        except Error as e:
            logging.error(f"Error adding product: {e}")
            return False

    def get_product(self, product_id):
        """Get product details by ID."""
        if not self._check_connection():
            return None
        try:
            cursor = self.connection.cursor()
            query = "SELECT * FROM products WHERE id = %s"
            cursor.execute(query, (product_id,))
            result = cursor.fetchone()
            return result
        except Error as e:
            logging.error(f"Error retrieving product {product_id}: {e}")
            return None

    def view_inventory(self):
        """Retrieve all products in the inventory."""
        if not self._check_connection():
            return []
        try:
            cursor = self.connection.cursor()
            query = "SELECT * FROM products"
            cursor.execute(query)
            results = cursor.fetchall()
            logging.info("Inventory retrieved successfully")
            return results
        except Error as e:
            logging.error(f"Error retrieving inventory: {e}")
            return []

    def update_product(self, product_id, name=None, category=None, price=None, quantity=None):
        """Update product details."""
        if not self._check_connection():
            return False
        try:
            cursor = self.connection.cursor()
            updates = []
            values = []
            
            if name:
                updates.append("name = %s")
                values.append(name)
            if category:
                updates.append("category = %s")
                values.append(category)
            if price is not None:
                if price <= 0:
                    logging.warning("Invalid price provided")
                    return False
                updates.append("price = %s")
                values.append(price)
            if quantity is not None:
                if quantity < 0:
                    logging.warning("Invalid quantity provided")
                    return False
                updates.append("quantity = %s")
                values.append(quantity)

            if not updates:
                logging.warning("No updates provided")
                return False

            values.append(product_id)
            query = f"UPDATE products SET {', '.join(updates)} WHERE id = %s"
            cursor.execute(query, values)
            self.connection.commit()
            
            if cursor.rowcount > 0:
                logging.info(f"Product {product_id} updated successfully")
                return True
            logging.warning(f"Product {product_id} not found")
            return False
        except Error as e:
            logging.error(f"Error updating product {product_id}: {e}")
            return False

    def delete_product(self, product_id):
        """Delete a product from inventory."""
        if not self._check_connection():
            return False
        try:
            cursor = self.connection.cursor()
            query = "DELETE FROM products WHERE id = %s"
            cursor.execute(query, (product_id,))
            self.connection.commit()
            
            if cursor.rowcount > 0:
                logging.info(f"Product {product_id} deleted successfully")
                return True
            logging.warning(f"Product {product_id} not found")
            return False
        except Error as e:
            logging.error(f"Error deleting product {product_id}: {e}")
            return False

    def record_sale(self, invoice_number, product_id, quantity, total_price, cashier_username):
        """Record a sale with cashier information."""
        if not self._check_connection():
            return False
        try:
            cursor = self.connection.cursor()

            # Check product availability
            cursor.execute("SELECT quantity FROM products WHERE id = %s", (product_id,))
            result = cursor.fetchone()
            if not result:
                logging.warning(f"Product {product_id} not found")
                return False
            if result[0] < quantity:
                logging.warning(f"Insufficient quantity for product {product_id}")
                return False

            # Record sale
            cursor.execute("""
                INSERT INTO sales (invoice_number, product_id, quantity, total_price, cashier_username)
                VALUES (%s, %s, %s, %s, %s)
            """, (invoice_number, product_id, quantity, total_price, cashier_username))

            # Update inventory
            cursor.execute("""
                UPDATE products 
                SET quantity = quantity - %s 
                WHERE id = %s
            """, (quantity, product_id))

            self.connection.commit()
            logging.info(f"Sale recorded: Invoice {invoice_number} by {cashier_username}")
            return True
        except Error as e:
            self.connection.rollback()
            logging.error(f"Error recording sale: {e}")
            return False

    def view_sales(self):
        """Retrieve all sales records."""
        if not self._check_connection():
            return []
        try:
            cursor = self.connection.cursor()
            query = """
                SELECT s.id, s.invoice_number, p.name, s.quantity, 
                       s.total_price, s.sale_date, s.cashier_username
                FROM sales s
                JOIN products p ON s.product_id = p.id
                ORDER BY s.sale_date DESC
            """
            cursor.execute(query)
            results = cursor.fetchall()
            logging.info("Sales records retrieved successfully")
            return results
        except Error as e:
            logging.error(f"Error retrieving sales: {e}")
            return []

    def add_cashier(self, username, password):
        """Add a new cashier account."""
        if not self._check_connection():
            return False
        try:
            cursor = self.connection.cursor()
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            
            cursor.execute("""
                INSERT INTO users (username, password_hash, role)
                VALUES (%s, %s, 'cashier')
            """, (username, password_hash))
            
            self.connection.commit()
            logging.info(f"New cashier account created: {username}")
            return True
        except Error as e:
            logging.error(f"Error creating cashier account: {e}")
            return False

    def remove_cashier(self, username):
        """Remove a cashier account."""
        if not self._check_connection():
            return False
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                DELETE FROM users 
                WHERE username = %s AND role = 'cashier'
            """, (username,))
            
            self.connection.commit()
            if cursor.rowcount > 0:
                logging.info(f"Cashier account removed: {username}")
                return True
            return False
        except Error as e:
            logging.error(f"Error removing cashier account: {e}")
            return False

    def list_cashiers(self):
        """List all cashier accounts."""
        if not self._check_connection():
            return []
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT username FROM users WHERE role = 'cashier'")
            return [row[0] for row in cursor.fetchall()]
        except Error as e:
            logging.error(f"Error listing cashiers: {e}")
            return []

    def close_connection(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            logging.info("Database connection closed")
