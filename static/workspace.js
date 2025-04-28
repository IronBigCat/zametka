async function loadNote(noteId) {
    const response = await fetch(`/api/note/${noteId}`);
    const data = await response.json();

    document.getElementById('title').value = data.title;
    document.getElementById('saved-content').innerHTML = data.content;

    window.currentNoteId = noteId;

    initBlocks(data.content);
}

async function createNewNote() {
    const response = await fetch('/create', { method: 'POST' });
    const data = await response.json();

    const noteList = document.getElementById('note-list');
    const li = document.createElement('li');
    li.textContent = data.title || 'Без названия';
    li.onclick = () => loadNote(data.id);
    noteList.appendChild(li);

    loadNote(data.id);
}

// Переопределяем сохранение — чтобы знать id заметки
function autoSave() {
    if (!window.currentNoteId) return;

    const title = document.getElementById('title').value;
    const blocks = document.querySelectorAll('.block');
    let content = '';

    blocks.forEach(block => {
        const type = block.getAttribute('data-type');
        const text = block.querySelector('.block-content').innerText;
        content += `<div data-type="${type}">${text}</div>`;
    });

    fetch(`/api/note/${window.currentNoteId}`, {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
        },
        body: `title=${encodeURIComponent(title)}&content=${encodeURIComponent(content)}`
    });
}
async function loadNote(noteId) {
    const response = await fetch(`/api/note/${noteId}`);
    const data = await response.json();

    document.getElementById('title').value = data.title;
    document.getElementById('saved-content').innerHTML = data.content;

    window.currentNoteId = noteId;
    initBlocks(data.content);

    document.querySelectorAll('#note-list li').forEach(li => li.classList.remove('active'));
    const activeNote = document.getElementById(`note-${noteId}`);
    if (activeNote) activeNote.classList.add('active');
}

async function createNewNote() {
    const response = await fetch('/create', { method: 'POST' });
    const data = await response.json();

    const noteList = document.getElementById('note-list');
    const li = document.createElement('li');
    li.textContent = data.title || 'Без названия';
    li.id = `note-${data.id}`;
    li.onclick = () => loadNote(data.id);
    noteList.appendChild(li);

    loadNote(data.id);
}