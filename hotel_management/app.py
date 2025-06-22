from flask import Flask, render_template, request, redirect, url_for, jsonify
import mysql.connector

app = Flask(__name__)

# MySQL Database Configuration
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "root",
    "database": "hotel_management"
}

# Initialize Database (Run Once)
def init_db():
    conn = mysql.connector.connect(**db_config)
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS rooms (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    type VARCHAR(50),
                    price FLOAT,
                    status VARCHAR(20) DEFAULT 'Available')''')

    c.execute('''CREATE TABLE IF NOT EXISTS customers (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100),
                    contact VARCHAR(50),
                    room_id INT,
                    checkin_date DATE,
                    checkout_date DATE,
                    FOREIGN KEY(room_id) REFERENCES rooms(id) ON DELETE SET NULL)''')

    conn.commit()
    conn.close()

@app.route('/')
def index():
    conn = mysql.connector.connect(**db_config)
    c = conn.cursor()
    c.execute("SELECT * FROM rooms")
    rooms = c.fetchall()
    conn.close()
    return render_template('index.html', rooms=rooms)

@app.route('/book', methods=['POST'])
def book():
    name = request.form['name']
    contact = request.form['contact']
    room_id = request.form['room_id']
    checkin_date = request.form['checkin_date']
    checkout_date = request.form['checkout_date']

    conn = mysql.connector.connect(**db_config)
    c = conn.cursor()
    c.execute("INSERT INTO customers (name, contact, room_id, checkin_date, checkout_date) VALUES (%s, %s, %s, %s, %s)",
              (name, contact, room_id, checkin_date, checkout_date))
    c.execute("UPDATE rooms SET status = 'Booked' WHERE id = %s", (room_id,))
    conn.commit()
    conn.close()

    return redirect(url_for('index'))

@app.route('/checkout/<int:room_id>')
def checkout(room_id):
    conn = mysql.connector.connect(**db_config)
    c = conn.cursor()
    c.execute("DELETE FROM customers WHERE room_id = %s", (room_id,))
    c.execute("UPDATE rooms SET status = 'Available' WHERE id = %s", (room_id,))
    conn.commit()
    conn.close()

    return redirect(url_for('index'))

@app.route('/manage_rooms')
def manage_rooms():
    conn = mysql.connector.connect(**db_config)
    c = conn.cursor()
    c.execute("SELECT * FROM rooms")
    rooms = c.fetchall()
    conn.close()
    return render_template('manage_rooms.html', rooms=rooms)

@app.route('/add_room', methods=['POST'])
def add_room():
    room_type = request.form['type']
    price = request.form['price']

    conn = mysql.connector.connect(**db_config)
    c = conn.cursor()
    c.execute("INSERT INTO rooms (type, price, status) VALUES (%s, %s, 'Available')", (room_type, price))
    conn.commit()
    conn.close()

    return redirect(url_for('manage_rooms'))

@app.route('/add_customer', methods=['POST'])
def add_customer():
    name = request.form['name']
    contact = request.form['contact']

    conn = mysql.connector.connect(**db_config)
    c = conn.cursor()
    c.execute("INSERT INTO customers (name, contact, room_id, checkin_date, checkout_date) VALUES (%s, %s, NULL, NULL, NULL)", 
              (name, contact))
    conn.commit()
    conn.close()

    return redirect(url_for('index'))

@app.route('/check_availability')
def check_availability():
    conn = mysql.connector.connect(**db_config)
    c = conn.cursor()
    c.execute("SELECT * FROM rooms WHERE status='Available'")
    available_rooms = c.fetchall()
    conn.close()
    return render_template('check.html', available_rooms=available_rooms)

@app.route('/api/rooms', methods=['GET'])
def get_rooms():
    conn = mysql.connector.connect(**db_config)
    c = conn.cursor()
    c.execute("SELECT * FROM rooms")
    rooms = c.fetchall()
    conn.close()
    rooms_list = [{"id": room[0], "type": room[1], "price": room[2], "status": room[3]} for room in rooms]
    return jsonify(rooms_list)

if __name__ == '__main__':
    init_db()  # Run this only once to create tables
    app.run(debug=True)
