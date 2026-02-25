from flask import Flask, request, jsonify, render_template
import sqlite3

app = Flask(__name__)
db_name =  'path/to/your/.db'

def init_db():
    with sqlite3.connect(db_name) as conn:
        conn.execute('CREATE TABLE IF NOT EXISTS passwords (id INTEGER PRIMARY KEY, service TEXT, data TEXT)')

@app.route('/')
def index():
    return render_template('yourindex.html')

    
@app.route('/api/save', methods=['POST'])
def save():
    content = request.json
    with sqlite3.connect(db_name) as conn:
        conn.execute('INSERT INTO passwords (service, data) VALUES (?, ?)', 
                     (content['service'], content['data']))
    return jsonify({"status": "success"})

@app.route('/api/load', methods=['GET'])
def load():
    with sqlite3.connect(db_name) as conn:
        #iterative id,websit e password
        cursor = conn.execute('SELECT id, service, data FROM passwords')
        items = [{"id": row[0], "service": row[1], "data": row[2]} for row in cursor.fetchall()]
        #cursor = conn.execute('SELECT service, data FROM passwords')
       # items = [{"service": row[0], "data": row[1]} for row in cursor.fetchall()]
    return jsonify(items)

@app.route('/api/delete/<int:id>', methods=['DELETE'])
def delete_pw(id):
    with sqlite3.connect(db_name) as conn:
        conn.execute('DELETE FROM passwords WHERE id = ?', (id,))
    return jsonify({"status": "success"})

@app.route('/api/update/<int:id>', methods=['PUT'])
def update_pw(id):
    content = request.json
    with sqlite3.connect(db_name) as conn:
        conn.execute('UPDATE passwords SET data = ? WHERE id = ?', (content['data'], id))
    return jsonify({"status": "success"})

if __name__ == '__main__':
    init_db()
    
    cert_file = 'path/to/your/.crt'
    key_file =  'path/to/your/.key'
    app.run(host='0.0.0.0', port=5000, ssl_context=(cert_file, key_file))

    #app.run(host='127.0.0.1', port=5000)



