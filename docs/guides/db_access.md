
## SQLiteDriver
import SQLiteDriver from amatak.database.drivers.sqlite

# Create and connect to database
db = SQLiteDriver()
db.connect(":memory:")

# Create table
db.execute("""
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL
)
""")

# Insert data
db.execute("INSERT INTO users (name, email) VALUES (?, ?)", ["John Doe", "john@example.com"])

# Query data
users = db.execute("SELECT * FROM users")
print(users)

# Disconnect
db.disconnect()









## PostgresDriver f

import PostgresDriver from amatak.database.drivers.postgres

# Create and connect to database
db = PostgresDriver()
connection_params = {
    'host': 'localhost',
    'port': 5432,
    'dbname': 'mydb',
    'user': 'myuser',
    'password': 'mypassword'
}
db.connect(connection_params)

# Create table
db.execute("""
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# Insert data with return
result = db.execute("""
    INSERT INTO users (name, email) 
    VALUES (%s, %s) 
    RETURNING id, created_at
""", ["Jane Smith", "jane@example.com"])
print("Inserted record:", result[0])

# Query with complex join
users = db.execute("""
    SELECT u.*, COUNT(p.id) as post_count
    FROM users u
    LEFT JOIN posts p ON p.user_id = u.id
    GROUP BY u.id
""")
print("Users with post counts:", users)

# Bulk insert
data = [
    ["Bob Johnson", "bob@example.com"],
    ["Alice Brown", "






# Initialize database connection
db = SQLiteDriver()
db.connect(":memory:")

# Connect models to database
Model.connect(db)

# Create tables
User.create_table()
Post.create_table()

# Create and save objects
user = User(username="johndoe", email="john@example.com")
user.save()

post = Post(title="Hello World", content="My first post", author=user.id)
post.save()

# Query objects
all_users = User.all()
active_users = User.filter(is_active=true)
john = User.get(user.id)

# Update objects
john.email = "john.doe@example.com"
john.save()

# Delete objects
post.delete()