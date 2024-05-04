import psycopg2

# Function to import data into PostgreSQL
def import_data():
    # Connect to PostgreSQL database
    conn = psycopg2.connect(
        dbname='warehouse',
        user='warehouse_user',
        password='test',
        host='localhost',
        port='5432'
    )


    # Open a cursor to perform database operations
    cursor = conn.cursor()

    # Create a new table if it doesn't exist
    cursor.execute('''CREATE TABLE IF NOT EXISTS Products (
                        id VARCHAR(10),
                        name VARCHAR(255),
                        ean VARCHAR(20)
                    )''')

    # Read data from the file and insert into the table
    with open('products.csv', 'r') as file:
        next(file)  # Skip header line
        for line in file:
            data = line.strip().split(';')
            cursor.execute("INSERT INTO Products (id, name, ean) VALUES (%s, %s, %s)", (data[0], data[1], data[2]))

    # Commit changes and close connection
    conn.commit()
    conn.close()

    print("Data imported successfully.")

if __name__ == '__main__':
    import_data()
