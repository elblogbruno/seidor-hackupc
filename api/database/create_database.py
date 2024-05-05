import sqlite3
import random
import psycopg2

def create_database():
    import sqlite3
    import random
    from faker import Faker

    # Initialize Faker for generating random data
    fake = Faker()

    # Connect to SQLite database (or create it if it doesn't exist)
    # conn = sqlite3.connect('warehouse.db')


    # cursor = conn.cursor()

    # Connect to PostgreSQL database
    conn = psycopg2.connect(
        dbname='warehouse',
        user='warehouse_user',
        password='test',
        host='localhost',
        port='5432'
    )

    cursor = conn.cursor()


    # Create Items table
    cursor.execute('''CREATE TABLE IF NOT EXISTS Items (
                        ItemID SERIAL PRIMARY KEY,
                        Name TEXT,
                        Category TEXT,
                        Price REAL
                    )
                    ''')

    # Create Users table
    cursor.execute('''CREATE TABLE IF NOT EXISTS Users (
                        UserID SERIAL PRIMARY KEY,
                        Name TEXT,
                        Email TEXT
                    )''')

    # Create Orders table
    cursor.execute('''CREATE TABLE IF NOT EXISTS Orders (
                        OrderID SERIAL PRIMARY KEY,
                        UserID INTEGER,
                        OrderDate DATE,
                        TotalAmount REAL,
                        FOREIGN KEY (UserID) REFERENCES Users(UserID)
                    )''')

    # Create Locations table
    cursor.execute('''CREATE TABLE IF NOT EXISTS Locations (
                        LocationID SERIAL PRIMARY KEY,
                        Aisle INTEGER,
                        Shelf INTEGER,
                        Bin INTEGER
                    )''')

    # Create ItemLocations table
    cursor.execute('''CREATE TABLE IF NOT EXISTS ItemLocations (
                        ItemLocationID SERIAL PRIMARY KEY,
                        ItemID INTEGER,
                        LocationID INTEGER,
                        FOREIGN KEY (ItemID) REFERENCES Items(ItemID),
                        FOREIGN KEY (LocationID) REFERENCES Locations(LocationID)
                    )''')

    # Populate Items table with random data
    for _ in range(10):  # Generate 10 items
        item_name = fake.word()
        category = random.choice(['Fruit', 'Dairy', 'Bakery'])
        price = round(random.uniform(0.5, 10.0), 2)
        cursor.execute("INSERT INTO Items (Name, Category, Price) VALUES (%s, %s, %s)", (item_name, category, price))


    # Populate Users table with random data
    for user_id in range(1, 6):  # Generate 5 users
        name = fake.name()
        email = fake.email()
        cursor.execute("INSERT INTO Users (UserID, Name, Email) VALUES (%s, %s, %s)", (user_id, name, email))


    # Populate Orders table with random data
    for _ in range(3):  # Generate 3 orders
        user_id = random.randint(1, 5)  # Assuming there are at least 5 users in the database
        order_date = fake.date_this_year()
        total_amount = round(random.uniform(5.0, 50.0), 2)
        cursor.execute("INSERT INTO Orders (UserID, OrderDate, TotalAmount) VALUES (%s, %s, %s)", (user_id, order_date, total_amount))

    # Populate Locations table with random data
    for i in range(1, 21):  # Generate 20 locations
        aisle = random.randint(1, 10)
        shelf = random.randint(1, 5)
        bin_ = random.randint(1, 10)
        cursor.execute("INSERT INTO Locations (LocationID, Aisle, Shelf, Bin) VALUES (%s, %s, %s, %s)", (i, aisle, shelf, bin_))

    # Populate ItemLocations table with random data
    for item_id in range(1, 11):  # Assuming there are 10 items in the Items table
        location_id = random.randint(1, 20)  # Assuming there are 20 locations in the Locations table
        cursor.execute("INSERT INTO ItemLocations (ItemID, LocationID) VALUES (%s, %s)", (item_id, location_id))

    # Commit changes and close connection
    conn.commit()
    conn.close()

    print("Database created and populated successfully.")


if __name__ == '__main__':
    create_database()