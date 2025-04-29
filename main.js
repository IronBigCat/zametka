const { app, BrowserWindow } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const http = require('http');

let pyProc = null;

function waitForFlask(url, callback) {
  const tryConnect = () => {
    http.get(url, (res) => {
      if (res.statusCode === 200) {
        console.log('✅ Flask is ready!');
        callback();
      } else {
        setTimeout(tryConnect, 500);
      }
    }).on('error', () => {
      setTimeout(tryConnect, 500);
    });
  };

  tryConnect();
}

function createWindow() {
  const win = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      contextIsolation: false,
      nodeIntegration: true,
      webSecurity: false
    }
  });

  win.loadURL('http://127.0.0.1:5000');
  win.webContents.openDevTools();
}

function startPython() {
  const script = path.join(__dirname, 'add.py');
  pyProc = spawn('python3', [script]);

  pyProc.stdout.on('data', (data) => console.log(`PYTHON: ${data}`));
  pyProc.stderr.on('data', (data) => console.error(`PYTHON ERR: ${data}`));
}

app.whenReady().then(() => {
  startPython();
  waitForFlask('http://127.0.0.1:5000', createWindow);
});

app.on('window-all-closed', () => {
  if (pyProc) pyProc.kill();
  if (process.platform !== 'darwin') app.quit();
});
