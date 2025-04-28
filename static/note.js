// ======== Автосохранение всей страницы ========
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

// ======== Создание нового блока ========
function createBlock(afterBlock = null, type = 'text') {
    const block = document.createElement('div');
    block.className = 'block';
    block.setAttribute('data-type', type);
    block.draggable = true; // для drag&drop

    const plus = document.createElement('button');
    plus.className = 'add-block-button';
    plus.type = 'button';
    plus.innerText = '+';
    plus.onclick = function () { showBlockMenu(this); };

    const content = document.createElement('div');
    content.className = 'block-content';
    content.contentEditable = true;
    content.oninput = autoSave;
    content.addEventListener('keydown', handleBlockKeydown);

    if (type === 'h1') {
        content.dataset.placeholder = 'Заголовок 1';
    } else if (type === 'h2') {
        content.dataset.placeholder = 'Заголовок 2';
    } else {
        content.dataset.placeholder = 'Текст';
    }

    block.appendChild(plus);
    block.appendChild(content);

    block.addEventListener('dragstart', handleDragStart);
    block.addEventListener('dragover', handleDragOver);
    block.addEventListener('drop', handleDrop);

    const contentDiv = document.getElementById('content');
    if (afterBlock) {
        contentDiv.insertBefore(block, afterBlock.nextSibling);
    } else {
        contentDiv.appendChild(block);
    }

    setTimeout(() => content.focus(), 0);
}

// ======== Работа с клавишами внутри блоков ========
function handleBlockKeydown(event) {
    const currentBlock = event.target.closest('.block');

    if (event.key === 'Enter') {
        event.preventDefault();
        createBlock(currentBlock);
    }

    if (event.key === 'Backspace') {
        const content = currentBlock.querySelector('.block-content');
        if (content.innerText.trim() === '') {
            event.preventDefault();
            const previousBlock = currentBlock.previousElementSibling;

            if (previousBlock && previousBlock.classList.contains('block')) {
                const previousContent = previousBlock.querySelector('.block-content');
                previousContent.focus();

                const range = document.createRange();
                range.selectNodeContents(previousContent);
                range.collapse(false);
                const selection = window.getSelection();
                selection.removeAllRanges();
                selection.addRange(range);
            }

            const contentDiv = document.getElementById('content');
            if (contentDiv.children.length === 1) {
                content.innerText = '';
            } else {
                currentBlock.remove();
            }

            autoSave();
        }
    }
}

// ======== Инициализация старых блоков ========
function initBlocks(savedContent) {
    const contentDiv = document.getElementById('content');
    contentDiv.innerHTML = '';

    if (savedContent.trim() === '') {
        createBlock();
        return;
    }

    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = savedContent;

    tempDiv.querySelectorAll('div[data-type]').forEach(savedBlock => {
        const type = savedBlock.getAttribute('data-type');
        const text = savedBlock.innerText;

        const block = document.createElement('div');
        block.className = 'block';
        block.setAttribute('data-type', type);
        block.draggable = true;

        const plus = document.createElement('button');
        plus.className = 'add-block-button';
        plus.type = 'button';
        plus.innerText = '+';
        plus.onclick = function () { showBlockMenu(this); };

        const content = document.createElement('div');
        content.className = 'block-content';
        content.contentEditable = true;
        content.innerText = text;
        content.oninput = autoSave;
        content.addEventListener('keydown', handleBlockKeydown);

        if (type === 'h1') {
            content.dataset.placeholder = 'Заголовок 1';
        } else if (type === 'h2') {
            content.dataset.placeholder = 'Заголовок 2';
        } else {
            content.dataset.placeholder = 'Текст';
        }

        block.appendChild(plus);
        block.appendChild(content);

        block.addEventListener('dragstart', handleDragStart);
        block.addEventListener('dragover', handleDragOver);
        block.addEventListener('drop', handleDrop);

        contentDiv.appendChild(block);
    });
}

// ======== Всплывающее меню для добавления нового блока ========
function showBlockMenu(button) {
    closeAllMenus();

    const menu = document.createElement('div');
    menu.className = 'block-menu';
    menu.innerHTML = `
        <div onclick="insertNewBlock(this, 'text')">Текст</div>
        <div onclick="insertNewBlock(this, 'h1')">Заголовок 1</div>
        <div onclick="insertNewBlock(this, 'h2')">Заголовок 2</div>
    `;

    button.parentElement.appendChild(menu);
}

function insertNewBlock(element, type) {
    const currentBlock = element.closest('.block');
    createBlock(currentBlock, type);
    closeAllMenus();
    autoSave();
}

function closeAllMenus() {
    document.querySelectorAll('.block-menu').forEach(menu => menu.remove());
}

// ======== Drag and Drop с линией подсказки ========
let draggedBlock = null;
let dropIndicator = null;

function handleDragStart(e) {
    draggedBlock = this;
    e.dataTransfer.effectAllowed = 'move';

    if (!dropIndicator) {
        dropIndicator = document.createElement('div');
        dropIndicator.className = 'drop-indicator';
    }
}

function handleDragOver(e) {
    e.preventDefault();

    const contentDiv = document.getElementById('content');
    const blocks = Array.from(contentDiv.children);

    if (dropIndicator.parentElement) {
        dropIndicator.parentElement.removeChild(dropIndicator);
    }

    let closestBlock = null;
    let closestOffset = Number.POSITIVE_INFINITY;

    blocks.forEach(block => {
        const rect = block.getBoundingClientRect();
        const offset = Math.abs(e.clientY - rect.top - rect.height / 2);

        if (offset < closestOffset) {
            closestOffset = offset;
            closestBlock = block;
        }
    });

    if (closestBlock) {
        const rect = closestBlock.getBoundingClientRect();
        if (e.clientY < rect.top + rect.height / 2) {
            closestBlock.parentElement.insertBefore(dropIndicator, closestBlock);
        } else {
            closestBlock.parentElement.insertBefore(dropIndicator, closestBlock.nextSibling);
        }
    }
}

function handleDrop(e) {
    e.preventDefault();

    if (dropIndicator && dropIndicator.parentElement) {
        dropIndicator.parentElement.insertBefore(draggedBlock, dropIndicator);
        dropIndicator.remove();
        autoSave();
    }
}

// ======== Старт приложения ========
document.addEventListener('DOMContentLoaded', function () {
    const titleField = document.getElementById('title');
    const savedContent = document.getElementById('saved-content')?.innerHTML || '';

    initBlocks(savedContent);

    titleField.focus();

    titleField.addEventListener('keydown', function (event) {
        if (event.key === 'Enter') {
            event.preventDefault();
            const firstBlockContent = document.querySelector('.block-content');
            if (firstBlockContent) {
                firstBlockContent.focus();
            }
        }
    });

    // Наведение мыши для отображения "+"
    document.addEventListener('mousemove', function (e) {
        const blocks = document.querySelectorAll('.block');
        blocks.forEach(block => {
            const plusButton = block.querySelector('.add-block-button');
            if (!plusButton) return;

            const rect = block.getBoundingClientRect();
            if (e.clientY >= rect.top && e.clientY <= rect.bottom) {
                plusButton.style.visibility = 'visible';
            } else {
                plusButton.style.visibility = 'hidden';
            }
        });
    });
});
