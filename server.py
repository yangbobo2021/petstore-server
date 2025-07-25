from flask import Flask, request, jsonify, abort
from datetime import datetime

app = Flask(__name__)

# In-memory data stores
pets = {}
orders = {}
users = {}

# Helper: generate new IDs
def get_new_id(store):
    return max(store.keys(), default=0) + 1

# ---- Pet APIs ----
@app.route('/pet', methods=['POST'])
def add_pet():
    data = request.get_json()
    if not data or 'name' not in data or 'photoUrls' not in data:
        return jsonify({'message': 'Invalid input'}), 405
    pet_id = data.get('id') or get_new_id(pets)
    data['id'] = pet_id
    pets[pet_id] = data
    return jsonify(data)

@app.route('/pet', methods=['PUT'])
def update_pet():
    data = request.get_json()
    pet_id = data.get('id')
    if not pet_id or pet_id not in pets:
        return jsonify({'message': 'Pet not found'}), 404
    pets[pet_id] = data
    return jsonify(data)

@app.route('/pet/findByStatus', methods=['GET'])
def find_pets_by_status():
    status = request.args.getlist('status')
    result = [pet for pet in pets.values() if pet.get('status') in status]
    return jsonify(result)

@app.route('/pet/findByTags', methods=['GET'])
def find_pets_by_tags():
    tags = request.args.getlist('tags')
    result = []
    for pet in pets.values():
        pet_tags = [t['name'] for t in pet.get('tags', []) if 'name' in t]
        if any(tag in pet_tags for tag in tags):
            result.append(pet)
    return jsonify(result)

@app.route('/pet/<int:petId>', methods=['GET'])
def get_pet_by_id(petId):
    pet = pets.get(petId)
    if not pet:
        return jsonify({'message': 'Pet not found'}), 404
    return jsonify(pet)

@app.route('/pet/<int:petId>', methods=['POST'])
def update_pet_with_form(petId):
    pet = pets.get(petId)
    if not pet:
        return jsonify({'message': 'Pet not found'}), 404
    name = request.form.get('name')
    status = request.form.get('status')
    if name:
        pet['name'] = name
    if status:
        pet['status'] = status
    pets[petId] = pet
    return jsonify(pet)

@app.route('/pet/<int:petId>', methods=['DELETE'])
def delete_pet(petId):
    if petId not in pets:
        return jsonify({'message': 'Pet not found'}), 404
    del pets[petId]
    return '', 204

@app.route('/pet/<int:petId>/uploadImage', methods=['POST'])
def upload_pet_image(petId):
    if petId not in pets:
        return jsonify({'message': 'Pet not found'}), 404
    # 这里只做简单模拟，实际应处理文件上传
    additional_metadata = request.form.get('additionalMetadata')
    # file = request.files.get('file')
    return jsonify({
        'code': 200,
        'type': 'success',
        'message': f'Image uploaded for pet {petId}' + (f' with metadata: {additional_metadata}' if additional_metadata else '')
    })

# ---- Store APIs ----
@app.route('/store/order', methods=['POST'])
def place_order():
    data = request.get_json()
    if not data or 'petId' not in data:
        return jsonify({'message': 'Invalid Order'}), 400
    order_id = data.get('id') or get_new_id(orders)
    data['id'] = order_id
    data['shipDate'] = data.get('shipDate') or datetime.utcnow().isoformat() + 'Z'
    orders[order_id] = data
    return jsonify(data)

@app.route('/store/order/<int:orderId>', methods=['GET'])
def get_order_by_id(orderId):
    order = orders.get(orderId)
    if not order:
        return jsonify({'message': 'Order not found'}), 404
    return jsonify(order)

@app.route('/store/order/<int:orderId>', methods=['DELETE'])
def delete_order(orderId):
    if orderId not in orders:
        return jsonify({'message': 'Order not found'}), 404
    del orders[orderId]
    return '', 204

@app.route('/store/inventory', methods=['GET'])
def get_inventory():
    status_count = {}
    for pet in pets.values():
        status = pet.get('status', 'unknown')
        status_count[status] = status_count.get(status, 0) + 1
    return jsonify(status_count)

# ---- User APIs ----
@app.route('/user', methods=['POST'])
def create_user():
    data = request.get_json()
    if not data or 'username' not in data:
        return jsonify({'message': 'Invalid user'}), 400
    user_id = data.get('id') or get_new_id(users)
    data['id'] = user_id
    users[data['username']] = data
    return jsonify(data)

@app.route('/user/<string:username>', methods=['GET'])
def get_user_by_name(username):
    user = users.get(username)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    return jsonify(user)

@app.route('/user/<string:username>', methods=['PUT'])
def update_user(username):
    if username not in users:
        return jsonify({'message': 'User not found'}), 404
    data = request.get_json()
    data['id'] = users[username]['id']
    users[username] = data
    return jsonify(data)

@app.route('/user/<string:username>', methods=['DELETE'])
def delete_user(username):
    if username not in users:
        return jsonify({'message': 'User not found'}), 404
    del users[username]
    return '', 204

@app.route('/user/login', methods=['GET'])
def login_user():
    username = request.args.get('username')
    password = request.args.get('password')
    user = users.get(username)
    if not user or user.get('password') != password:
        return jsonify({'message': 'Invalid username/password supplied'}), 400
    return jsonify({'message': 'logged in', 'username': username})

@app.route('/user/logout', methods=['GET'])
def logout_user():
    return jsonify({'message': 'logged out'})

@app.route('/user/createWithList', methods=['POST'])
def create_users_with_list():
    data = request.get_json()
    if not isinstance(data, list):
        return jsonify({'message': 'Invalid input'}), 400
    for user in data:
        if 'username' in user:
            user_id = user.get('id') or get_new_id(users)
            user['id'] = user_id
            users[user['username']] = user
    return jsonify({'message': 'Users created'})

@app.route('/user/createWithArray', methods=['POST'])
def create_users_with_array():
    return create_users_with_list()

if __name__ == '__main__':
    app.run(debug=True)
