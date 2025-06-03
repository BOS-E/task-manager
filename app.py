from flask import Flask, render_template, request, jsonify
import psycopg2
import os
from datetime import datetime

app = Flask(__name__)

# Database connection
DATABASE_URL = os.environ.get("DATABASE_URL")  # Set this in Railway and in local .env file

def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn

# Initialize DB (one-time call on startup)
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            completed BOOLEAN DEFAULT FALSE,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    conn.commit()
    cur.close()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT id, title, description, completed, created_date FROM tasks ORDER BY created_date DESC')
    rows = cur.fetchall()
    cur.close()
    conn.close()
    tasks = []
    for row in rows:
        tasks.append({
            'id': row[0],
            'title': row[1],
            'description': row[2],
            'completed': row[3],
            'created_date': row[4].isoformat()
        })
    return jsonify(tasks)

@app.route('/api/tasks', methods=['POST'])
def add_task():
    data = request.get_json()
    title = data.get('title')
    description = data.get('description', '')

    if not title:
        return jsonify({'error': 'Title is required'}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('INSERT INTO tasks (title, description, created_date) VALUES (%s, %s, %s)',
                (title, description, datetime.now()))
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({'message': 'Task added successfully'}), 201

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.get_json()
    completed = data.get('completed', False)

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('UPDATE tasks SET completed = %s WHERE id = %s', (completed, task_id))
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({'message': 'Task updated successfully'})

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM tasks WHERE id = %s', (task_id,))
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({'message': 'Task deleted successfully'})

if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv()
    init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
else:
    init_db()
