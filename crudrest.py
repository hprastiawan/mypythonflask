from flask import Flask, jsonify, request, render_template, redirect
import json
from flasgger import Swagger
from flasgger.utils import swag_from

app = Flask(__name__)
Swagger(app)
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Membuka dan menyimpan data ke file json
def load_data():
    try:
        with open("data.json", "r") as file:
            content = file.read()
            if not content:
                return []
            data = json.loads(content)
            # Pastikan setiap ID adalah integer
            for item in data:
                item['id'] = int(item['id'])
        return data
    except Exception as e:
        return {"error": str(e)}

def save_data(data):
    try:
        with open("data.json", "w") as file:
            json.dump(data, file, indent=4)
        return True
    except Exception as e:
        return False

#Agar data yang berhasil masuk, memiliki ID yang increment

def add_new_entry(entry):
    try:
        # Membuka dan membaca file data.json
        with open("data.json", "r") as file:
            content = file.read()
            # Jika file kosong, inisialisasi data sebagai list kosong
            if not content:
                data = []
            else:
                data = json.loads(content)
        
        # Mendapatkan ID terbesar dari data yang ada dan memastikan itu adalah integer
        max_id = max([int(item['id']) for item in data], default=0)
        # Menambahkan ID baru ke entry yang diberikan
        entry['id'] = max_id + 1
        # Menambahkan entry ke data
        data.append(entry)
        
        # Menulis kembali ke file data.json
        with open("data.json", "w") as file:
            json.dump(data, file, indent=4)
        print("Data berhasil ditambahkan ke data.json")
    except Exception as e:
        print(f"Error saat menambahkan data: {e}")


@app.route('/api/data', methods=['GET'])
@swag_from('swagger_docs/get_all.yaml')
def get_all_data():
    data = load_data()
    if "error" in data:
        return jsonify({"message": data["error"]}), 500
    return jsonify(data), 200

@app.route('/api/data/<int:data_id>', methods=['GET'])
@swag_from('swagger_docs/get_one.yaml')
def get_one_data(data_id):
    data = load_data()
    if "error" in data:
        return jsonify({"message": data["error"]}), 500
    data_item = next((item for item in data if item["id"] == data_id), None)
    if data_item:
        return jsonify(data_item), 200
    return jsonify({"message": "Data tidak ditemukan"}), 404

@app.route('/api/data', methods=['POST'])
@swag_from('swagger_docs/create_data.yaml')
def create_data():
    new_data = request.get_json()
    add_new_entry(new_data)
    return jsonify(new_data), 201

@app.route('/api/data/<int:data_id>', methods=['PUT'])
@swag_from('swagger_docs/update_data.yaml')
def update_data(data_id):
    print("Fungsi update_data dipanggil!")

    data = load_data()
    if "error" in data:
        return jsonify({"message": data["error"]}), 500

    data_item = next((item for item in data if item["id"] == data_id), None)
    print(f"Data item sebelum pembaruan: {data_item}")

    updated_data = request.form
    print(f"Data yang diterima dari form: {updated_data}")

    data_item.update(updated_data)
    print(f"Data item setelah pembaruan: {data_item}")

    success = save_data(data)
    print(f"Hasil penyimpanan: {success}")
    if not success:
        return jsonify({"message": "Kesalahan saat menyimpan data"}), 500

    return jsonify({"message": "Data berhasil diperbarui"}), 200

@app.route('/api/data/<int:data_id>', methods=['DELETE'])
@swag_from('swagger_docs/delete_data.yaml')
def delete_data(data_id):
    data = load_data()
    if "error" in data:
        return jsonify({"message": data["error"]}), 500
    data_item = next((item for item in data if item["id"] == data_id), None)
    if not data_item:
        return jsonify({"message": "Data tidak ditemukan"}), 404
    data.remove(data_item)
    success = save_data(data)
    if not success:
        return jsonify({"message": "Kesalahan saat menyimpan data"}), 500
    return jsonify({"message": "Data berhasil dihapus"}), 200

@app.route('/input', methods=['GET', 'POST'])
def input_data():
    if request.method == 'POST':
        new_data = {
            'nama': request.form['nama'],
            'alamat': request.form['alamat']
        }
        add_new_entry(new_data)
        return render_template('confirmation.html')
    return render_template('create_form.html')

@app.route('/display_all', methods=['GET'])
def display_all():
    data = load_data()
    if "error" in data:
        return "Kesalahan saat memuat data", 500
    return render_template('display_all.html', data=data)

@app.route('/search_update', methods=['GET', 'POST'])
def search_update():
    data_list = []
    try:
        if request.method == 'POST':
            search_name = request.form['nama'].lower()
            all_data = load_data()
            # Gunakan list comprehension untuk mendapatkan semua entri yang cocok
            data_list = [item for item in all_data if search_name in item["nama"].lower()]
    except Exception as e:
        print(f"Terjadi kesalahan: {e}")
    finally:
        return render_template('search_update.html', data_list=data_list)


@app.route('/delete', methods=['GET', 'POST'])
def delete_data_ui():
    data_list = []
    try:
        if request.method == 'POST':
            search_name = request.form['nama'].lower()
            all_data = load_data()
            # Gunakan list comprehension untuk mendapatkan semua entri yang cocok
            data_list = [item for item in all_data if search_name in item["nama"].lower()]
    except Exception as e:
        print(f"Terjadi kesalahan: {e}")
    finally:
        return render_template('delete_data.html', data_list=data_list)

@app.route('/delete_by_name', methods=['POST'])
def delete_by_name():
    try:
        name_to_delete = request.form['nama']
        all_data = load_data()
        # Hapus semua entri dengan nama yang cocok
        all_data = [item for item in all_data if item["nama"].lower() != name_to_delete.lower()]
        save_data(all_data)
    except Exception as e:
        print(f"Terjadi kesalahan: {e}")
    finally:
        return redirect('/delete')
    
@app.route('/update', methods=['POST'])
def update():
    data_id = request.form['id']
    updated_nama = request.form['nama']
    updated_alamat = request.form['alamat']

    # Cetak data yang dikirim ke fungsi update_data
    print(f"Data ID: {data_id}, Nama: {updated_nama}, Alamat: {updated_alamat}")

    # Panggil fungsi update_data dan cetak responsnya
    response = update_data(int(data_id))
    print(response)

    return redirect('/display_all')

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5020)