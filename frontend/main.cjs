const { app, BrowserWindow, Tray, Menu, nativeImage, ipcMain } = require('electron');
const path = require('path');
const isDev = require('electron-is-dev');
const http = require('http');

let mainWindow;
let tray;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1000,
    height: 800,
    show: false,
    frame: false, 
    transparent: true,
    vibrancy: 'sidebar',
    visualEffectState: 'active',
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
    },
  });

  const url = isDev 
    ? 'http://localhost:5173' 
    : `file://${path.join(__dirname, 'dist/index.html')}`;

  mainWindow.loadURL(url);

  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

function updateTrayMenu() {
  // Fetch tasks from backend to show in tray
  http.get('http://127.0.0.1:8000/get_view_data', (res) => {
    let data = '';
    res.on('data', (chunk) => data += chunk);
    res.on('end', () => {
      try {
        const json = JSON.parse(data);
        const tasks = json.calendar || [];
        
        const taskItems = tasks.slice(0, 5).map(t => ({
          label: `[${t.time}] ${t.title} (${(t.load * 100).toFixed(0)}%)`,
          click: () => {
            mainWindow.show();
            mainWindow.webContents.send('navigate', 'Schedule');
          }
        }));

        const contextMenu = Menu.buildFromTemplate([
          { label: 'Notion Soul Agent', enabled: false },
          { type: 'separator' },
          ...taskItems,
          { type: 'separator' },
          { label: 'Show Dashboard', click: () => mainWindow.show() },
          { label: 'Quit', click: () => app.quit() }
        ]);
        
        tray.setContextMenu(contextMenu);
      } catch (e) {
        setDefaultTray();
      }
    });
  }).on('error', () => {
    setDefaultTray();
  });
}

function setDefaultTray() {
  const contextMenu = Menu.buildFromTemplate([
    { label: 'Notion Soul Agent', enabled: false },
    { type: 'separator' },
    { label: 'Backend Offline', enabled: false },
    { type: 'separator' },
    { label: 'Show Dashboard', click: () => mainWindow.show() },
    { label: 'Quit', click: () => app.quit() }
  ]);
  tray.setContextMenu(contextMenu);
}

function createTray() {
  const icon = nativeImage.createEmpty(); 
  tray = new Tray(icon);
  tray.setToolTip('Notion Soul Agent');
  setDefaultTray();
  
  // Refresh tray every 1 minute
  setInterval(updateTrayMenu, 60000);
  updateTrayMenu();
}

app.whenReady().then(() => {
  createWindow();
  createTray();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});
