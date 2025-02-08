from flask import Flask, request, redirect, jsonify, render_template
import base64
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

"""
# Database connection parameters
DB_CONFIG = {
    "user": "siva",
    "password": "siva12345",
    "database": "supersimple",
    "host": "34.47.192.92",
    "port": 3306
}
"""

"""
#Table users is already created in supersimple database, directly in cloud
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    age INT NOT NULL,
    gender VARCHAR(10)
);
"""

# Function to establish a connection
def create_connection():
    try:
        #connection = mysql.connector.connect(**DB_CONFIG)
        connection = mysql.connector.connect(
                    user="siva",
                    password="siva12345",
                    database="supersimple",
                    host="34.47.192.92",
                    port=3306
                   )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error: '{e}'")
        return None


# Function to close the connection
def close_connection(connection):
    if connection.is_connected():
        connection.close()


# Endpoint to fetch all users
@app.route('/users/get', methods=['GET'])
def get_users():
    connection = create_connection()
    if not connection:
        return jsonify({"error": "Database connection failed"}), 500

    query = "SELECT * FROM users;"
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        results = cursor.fetchall()
        close_connection(connection)
        users = [
            {"id": row[0], "name": row[1], "age": row[2], "gender": row[3]} for row in results
        ]
        return jsonify(users)
    except Error as e:
        close_connection(connection)
        return jsonify({"error": str(e)}), 500


# Endpoint to add a new user
@app.route('/users/add', methods=['POST'])
def add_user():
    data = request.json
    name = data.get('name')
    age = data.get('age')
    gender = data.get('gender')

    if not (name and age and gender):
        return jsonify({"error": "Missing required fields"}), 400

    connection = create_connection()
    if not connection:
        return jsonify({"error": "Database connection failed"}), 500

    query = "INSERT INTO users (name, age, gender) VALUES (%s, %s, %s)"
    values = (name, age, gender)
    cursor = connection.cursor()
    try:
        cursor.execute(query, values)
        connection.commit()
        close_connection(connection)
        return jsonify({"message": "User added successfully"}), 201
    except Error as e:
        close_connection(connection)
        return jsonify({"error": str(e)}), 500


# Endpoint to delete a user by ID
@app.route('/users/del/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    connection = create_connection()
    if not connection:
        return jsonify({"error": "Database connection failed"}), 500

    query = "DELETE FROM users WHERE id = %s"
    cursor = connection.cursor()
    try:
        cursor.execute(query, (user_id,))
        connection.commit()
        close_connection(connection)
        if cursor.rowcount > 0:
            return jsonify({"message": "User deleted successfully"}), 200
        else:
            return jsonify({"error": "User not found"}), 404
    except Error as e:
        close_connection(connection)
        return jsonify({"error": str(e)}), 500


# Start the Flask app
if __name__ == '__main__':
    app.run(debug=True)
