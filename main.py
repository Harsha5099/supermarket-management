import mysql.connector
from datetime import datetime, timedelta

def create_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Bond@5099",
        database="supermarket"
    )

def create_tables():
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Suppliers (
            SupplierID INT AUTO_INCREMENT PRIMARY KEY,
            SupplierName VARCHAR(100) NOT NULL,
            ContactNumber VARCHAR(20),
            Email VARCHAR(100),
            Address VARCHAR(255)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Products (
            ProductID INT AUTO_INCREMENT PRIMARY KEY,
            ProductName VARCHAR(100) NOT NULL,
            Category VARCHAR(50),
            Price DECIMAL(10,2) NOT NULL,
            StockLevel INT NOT NULL,
            SupplierID INT,
            ExpiryDate DATE,
            FOREIGN KEY (SupplierID) REFERENCES Suppliers(SupplierID) ON DELETE CASCADE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Customers (
            CustomerID INT AUTO_INCREMENT PRIMARY KEY,
            CustomerName VARCHAR(100) NOT NULL,
            ContactNumber VARCHAR(20),
            Email VARCHAR(100),
            Address VARCHAR(255)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Sales (
            SaleID INT AUTO_INCREMENT PRIMARY KEY,
            ProductID INT,
            CustomerID INT,
            Quantity INT NOT NULL,
            TotalAmount DECIMAL(10,2) NOT NULL,
            SaleDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (ProductID) REFERENCES Products(ProductID) ON DELETE CASCADE,
            FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID) ON DELETE CASCADE
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()
    print("Tables created!")

def add_supplier():
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO Suppliers (SupplierName, ContactNumber, Email, Address) VALUES (%s, %s, %s, %s)",
        (input("Supplier Name: "),
         input("Contact: "),
         input("Email: "),
         input("Address: "))
    )

    conn.commit()
    cursor.close()
    conn.close()
    print("Supplier added!")

def add_product():
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT SupplierID, SupplierName FROM Suppliers")
    suppliers = cursor.fetchall()

    if not suppliers:
        print("No suppliers! Add one first.")
        cursor.close()
        conn.close()
        return

    for s in suppliers:
        print(f"{s[0]}: {s[1]}")

    cursor.execute(
        "INSERT INTO Products (ProductName, Category, Price, StockLevel, SupplierID, ExpiryDate) VALUES (%s, %s, %s, %s, %s, %s)",
        (
            input("Product Name: "),
            input("Category: "),
            float(input("Price: ")),
            int(input("Stock: ")),
            int(input("Supplier ID: ")),
            input("Expiry Date (YYYY-MM-DD): ")
        )
    )

    conn.commit()
    cursor.close()
    conn.close()
    print("Product added!")

def purchase_product():
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT ProductID, ProductName, StockLevel, Price FROM Products")
    products = cursor.fetchall()

    if not products:
        print("No products available!")
        cursor.close()
        conn.close()
        return

    for p in products:
        print(f"{p[0]}: {p[1]} (Stock: {p[2]}, Price: ${p[3]:.2f})")

    product_id = int(input("Product ID: "))
    quantity = int(input("Quantity: "))
    customer = input("Customer Name: ")

    cursor.execute("SELECT Price, StockLevel FROM Products WHERE ProductID = %s", (product_id,))
    product = cursor.fetchone()

    if not product or product[1] < quantity:
        print("Invalid product or insufficient stock!")
        cursor.close()
        conn.close()
        return

    cursor.execute("INSERT INTO Customers (CustomerName) VALUES (%s)", (customer,))
    customer_id = cursor.lastrowid

    cursor.execute(
        "INSERT INTO Sales (ProductID, CustomerID, Quantity, TotalAmount) VALUES (%s, %s, %s, %s)",
        (product_id, customer_id, quantity, product[0] * quantity)
    )

    cursor.execute(
        "UPDATE Products SET StockLevel = StockLevel - %s WHERE ProductID = %s",
        (quantity, product_id)
    )

    conn.commit()
    cursor.close()
    conn.close()
    print("Purchase successful!")

def show_products():
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Products")
    products = cursor.fetchall()

    if not products:
        print("No products available!")
    else:
        print("\n**Products List**")
        for p in products:
            print(f"{p[0]}: {p[1]} (Category: {p[2]}, Price: ${p[3]:.2f}, Stock: {p[4]})")

    cursor.close()
    conn.close()

def show_expiring_products():
    conn = create_connection()
    cursor = conn.cursor()

    today = datetime.today().date()
    future_date = today + timedelta(days=30)

    cursor.execute(
        "SELECT ProductID, ProductName, ExpiryDate, StockLevel FROM Products WHERE ExpiryDate BETWEEN %s AND %s",
        (today, future_date)
    )

    products = cursor.fetchall()

    if not products:
        print("No products expiring soon.")
    else:
        print("\n**Expiring Products**")
        for p in products:
            print(f"{p[0]}: {p[1]} (Expiry: {p[2]}, Stock: {p[3]})")

    cursor.close()
    conn.close()

def main():
    create_tables()
    while True:
        print("\n🛒 **Supermarket Management**")
        print("1️⃣ Add Supplier  2️⃣ Add Product  3️⃣ Purchase Product  4️⃣ Show Products  5️⃣ Show Expiring Products  6️⃣ Exit")
        choice = input("Enter choice: ")
        if choice == "1":
            add_supplier()
        elif choice == "2":
            add_product()
        elif choice == "3":
            purchase_product()
        elif choice == "4":
            show_products()
        elif choice == "5":
            show_expiring_products()
        elif choice == "6":
            print("Exiting...")
            break
        else:
            print("Invalid choice!")

if __name__ == "__main__":
    main()
