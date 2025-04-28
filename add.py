import json
from flask import Flask, render_template, request, redirect, url_for, jsonify

app = Flask(__name__)

NOTES_FILE = 'notes.json'

# Загрузка заметок из файла
try:
    with open(NOTES_FILE, 'r', encoding='utf-8') as f:
        notes = json.load(f)
        notes = {int(k): v for k, v in notes.items()}
        note_id_counter = max(notes.keys()) + 1 if notes else 1
except FileNotFoundError:
    notes = {}
    note_id_counter = 1

# Сохранение заметок
def save_notes():
    with open(NOTES_FILE, 'w', encoding='utf-8') as f:
        json.dump(notes, f, ensure_ascii=False, indent=2)

@app.route('/')
def index():
    return render_template('index.html', notes=notes)

@app.route('/note/<int:note_id>', methods=['GET', 'POST'])
def note_detail(note_id):
    note = notes.get(note_id)
    if note is None:
        return "Заметка не найдена", 404

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        note['title'] = title
        note['content'] = content
        save_notes()
        return '', 204

    return render_template('note.html', note=note)

@app.route('/create')
def create_note():
    global note_id_counter
    notes[note_id_counter] = {
        'id': note_id_counter,
        'title': '',
        'content': ''
    }
    note_id = note_id_counter
    note_id_counter += 1
    save_notes()
    return redirect(url_for('note_detail', note_id=note_id))

@app.route('/delete/<int:note_id>', methods=['POST'])
def delete_note(note_id):
    notes.pop(note_id, None)
    save_notes()
    return redirect(url_for('index'))

@app.route('/api/note/<int:note_id>', methods=['GET', 'POST'])
def api_note_detail(note_id):
    note = notes.get(note_id)
    if note is None:
        return jsonify({'error': 'Заметка не найдена'}), 404

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        note['title'] = title
        note['content'] = content
        save_notes()
        return '', 204

    return jsonify(note)

@app.route('/create', methods=['POST'])
def api_create_note():
    global note_id_counter
    title = ''
    content = ''
    notes[note_id_counter] = {'id': note_id_counter, 'title': title, 'content': content}
    note_id_counter += 1
    save_notes()
    return jsonify(notes[note_id_counter - 1])

if __name__ == '__main__':
    app.run(debug=True)
