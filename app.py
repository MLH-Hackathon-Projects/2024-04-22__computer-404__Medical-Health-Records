from flask import Flask, jsonify, request, render_template_string
from flask_httpauth import HTTPBasicAuth
import datetime
import hashlib
import json

app = Flask(__name__)
auth = HTTPBasicAuth()

# This will be our simple user store
users = {
    "doctor": hashlib.sha256("password1".encode()).hexdigest(),  # Existing user
    "nurse": hashlib.sha256("password2".encode()).hexdigest()   # Existing user
}

def verify_hash(password, hash):
    return hashlib.sha256(password.encode()).hexdigest() == hash

@auth.verify_password
def verify_password(username, password):
    if username in users and verify_hash(password, users[username]):
        return username

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'message': 'Username and password are required'}), 400
    if username in users:
        return jsonify({'message': 'User already exists'}), 400
    users[username] = hashlib.sha256(password.encode()).hexdigest()
    return jsonify({'message': f'User {username} registered successfully'}), 201

class Blockchain:
    def __init__(self):
        self.chain = []
        self.create_block(proof=1, previous_hash='0', patient_data={})

    def create_block(self, proof, previous_hash, patient_data):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': str(datetime.datetime.now()),
            'proof': proof,
            'previous_hash': previous_hash,
            'patient_data': patient_data
        }
        self.chain.append(block)
        return block

    def get_previous_block(self):
        return self.chain[-1]

    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False
        while check_proof is False:
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                new_proof += 1
        return new_proof

    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def is_chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block['previous_hash'] != self.hash(previous_block):
                return False
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False
            previous_block = block
            block_index += 1
        return True

blockchain = Blockchain()

@app.route('/')
def home():
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Medical Health Records Blockchain</title>
        <style>
            body { font-family: Arial, sans-serif; background-color: #f4f4f9; margin: 40px; }
            h1 { color: #333; }
            form { margin-top: 20px; }
            input, select, textarea { padding: 10px; margin: 10px; border-radius: 5px; border: 1px solid #ccc; }
            input[type="submit"], button { background-color: #4CAF50; color: white; border: none; cursor: pointer; }
            input[type="submit"]:hover, button:hover { background-color: #45a049; }
            .container { background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px 0 rgba(0,0,0,0.1); }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Welcome to the Medical Health Records Blockchain!</h1>
            <p>Click the buttons below to perform actions:</p>

            <form action="/register" method="POST">
                <h2>Register as a Doctor</h2>
                <label for="username">Username:</label>
                <input type="text" id="username" name="username" required><br>
                <label for="password">Password:</label>
                <input type="password" id="password" name="password" required><br>
                <input type="submit" value="Register">
            </form>
            <form action="/add_patient" method="POST">
                <label for="name">Patient Name:</label>
                <input type="text" id="name" name="name" required><br>
                <label for="age">Patient Age:</label>
                <input type="number" id="age" name="age" required><br>
                <label for="gender">Patient Gender:</label>
                <select id="gender" name="gender" required>
                    <option value="Male">Male</option>
                    <option value="Female">Female</option>
                    <option value="Other">Other</option>
                </select><br>
                <label for="comments">Comments:</label>
                <textarea id="comments" name="comments" rows="4" cols="50" required></textarea><br>
                <input type="submit" value="Add Patient">
            </form>
            <form action="/get_chain" method="GET">
                <input type="submit" value="View Blockchain">
            </form>
            <form action="/is_valid" method="GET">
                <input type="submit" value="Check Blockchain Validity">
            </form>
        </div>
        <script>
        document.getElementById("registration-form").addEventListener("submit", function(event) {
            event.preventDefault();  // Prevent normal form submission

            const username = document.getElementById("username").value;
            const password = document.getElementById("password").value;

            fetch("/register", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    username: username,
                    password: password
                })
            })
            .then(response => response.json())
            .then(data => alert(data.message))  // Show a message with the response
            .catch(error => console.error('Error:', error));
        });
        </script>
    </body>
    </html>
    ''')

@app.route('/add_patient', methods=['POST'])
@auth.login_required
def add_patient():
    name = request.form['name']
    age = request.form['age']
    gender = request.form['gender']
    patient_data = {
        'name': name,
        'age': age,
        'gender': gender
    }
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    block = blockchain.create_block(proof, previous_hash, patient_data)
    response = {
        'message': f'Patient {name} added to Block {block["index"]}',
        'index': block['index'],
        'timestamp': block['timestamp'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
        'patient_data': block['patient_data']
    }
    return jsonify(response), 201

@app.route('/get_chain', methods=['GET'])
def get_chain():
    chain_data = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Blockchain Overview</title>
        <style>
            body { font-family: Arial, sans-serif; background-color: #f4f4f9; margin: 40px; }
            h1 { color: #333; }
            table { width: 100%; border-collapse: collapse; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #4CAF50; color: white; }
            button {
                padding: 10px 20px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                text-align: center;
                text-decoration: none;
                display: inline-block;
                font-size: 16px;
            }
            button:hover { background-color: #45a049; }
        </style>
    </head>
    <body>
        <h1>Blockchain Details</h1>
        <table>
            <tr>
                <th>Index</th>
                <th>Timestamp</th>
                <th>Data</th>
                <th>Previous Hash</th>
            </tr>
            {% for block in chain %}
            <tr>
                <td>{{ block['index'] }}</td>
                <td>{{ block['timestamp'] }}</td>
                <td>{{ block['patient_data'] }}</td>
                <td>{{ block['previous_hash'] }}</td>
            </tr>
            {% endfor %}
        </table>
        <p>Blockchain Length: {{ length }}</p>
        <button onclick="window.history.back();">Go Back</button>
    </body>
    </html>
    ''', chain=chain_data['chain'], length=chain_data['length'])

@app.route('/is_valid', methods=['GET'])
def is_valid():
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    if is_valid:
        response = {'message': 'The Blockchain is valid.'}
    else:
        response = {'message': 'The Blockchain is not valid.'}
    return jsonify(response), 200

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
