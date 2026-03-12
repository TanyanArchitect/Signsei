const { app, BrowserWindow, screen, ipcMain, globalShortcut } = require('electron')
const path = require('path')

let win;
let currentHotkey = 'F8'; 

function createWindow () {
  const { width, height } = screen.getPrimaryDisplay().bounds;

  win = new BrowserWindow({
    width: width, height: height,
    transparent: true, frame: false,
    alwaysOnTop: true, fullscreen: true, skipTaskbar: false, 
    icon: path.join(__dirname, 'icon.ico'),
    webPreferences: { 
      nodeIntegration: true, 
      contextIsolation: false, 
      sandbox: false,
      webSecurity: false
    }
  })

  win.loadFile('index.html')
}

function registerGlobalHotkey(key) {
  globalShortcut.unregisterAll();
  if (!key) return;
  try {
    globalShortcut.register(key, () => {
      if (win) win.webContents.send('trigger-hotkey'); 
    });
  } catch (err) { console.error("Lỗi đăng ký phím:", err); }
}

app.whenReady().then(() => { createWindow(); registerGlobalHotkey(currentHotkey); })
app.on('window-all-closed', () => { globalShortcut.unregisterAll(); if (process.platform !== 'darwin') app.quit() })
app.on('will-quit', () => { globalShortcut.unregisterAll(); });

ipcMain.on('minimize-window', () => { if(win) win.minimize(); });
ipcMain.on('restore-window', () => { if(win) { win.restore(); win.focus(); } });
ipcMain.on('close-window', () => { app.quit(); });
ipcMain.on('register-hotkey', (event, key) => { currentHotkey = key; registerGlobalHotkey(key); });
ipcMain.on('unregister-hotkey', () => { globalShortcut.unregisterAll(); });