const { app, BrowserWindow, ipcMain, Tray, Menu } = require('electron');
const path = require('path');
const isDev = require('electron-is-dev');
const { spawn } = require('child_process');
const fs = require('fs');

let mainWindow;
let tray;
let backendProcess;
let mongoProcess;
const Store = require('electron-store');
const store = new Store();

// Paths
const RESOURCES_PATH = isDev 
  ? path.join(__dirname, '../../')
  : process.resourcesPath;

const BACKEND_PATH = path.join(RESOURCES_PATH, 'backend', 'server.exe');
const MONGO_PATH = path.join(RESOURCES_PATH, 'mongodb', 'bin', 'mongod.exe');
const MONGO_DATA_PATH = path.join(app.getPath('userData'), 'mongodb-data');

// Create MongoDB data directory
if (!fs.existsSync(MONGO_DATA_PATH)) {
  fs.mkdirSync(MONGO_DATA_PATH, { recursive: true });
}

function startMongoDB() {
  return new Promise((resolve, reject) => {
    console.log('Starting MongoDB...');
    
    if (isDev) {
      // In dev mode, assume MongoDB is already running
      console.log('Dev mode: Skipping MongoDB start');
      resolve();
      return;
    }

    try {
      mongoProcess = spawn(MONGO_PATH, [
        '--dbpath', MONGO_DATA_PATH,
        '--port', '27017',
        '--bind_ip', '127.0.0.1'
      ]);

      mongoProcess.stdout.on('data', (data) => {
        console.log(`MongoDB: ${data}`);
        if (data.includes('waiting for connections')) {
          console.log('MongoDB started successfully');
          resolve();
        }
      });

      mongoProcess.stderr.on('data', (data) => {
        console.error(`MongoDB Error: ${data}`);
      });

      mongoProcess.on('error', (error) => {
        console.error('Failed to start MongoDB:', error);
        reject(error);
      });

      // Timeout fallback
      setTimeout(() => resolve(), 5000);
    } catch (error) {
      console.error('Error starting MongoDB:', error);
      reject(error);
    }
  });
}

function startBackend() {
  return new Promise((resolve, reject) => {
    console.log('Starting Backend...');
    
    if (isDev) {
      // In dev mode, assume backend is running
      console.log('Dev mode: Using existing backend');
      resolve();
      return;
    }

    try {
      const env = Object.assign({}, process.env, {
        MONGO_URL: 'mongodb://127.0.0.1:27017',
        DB_NAME: 'garena_accounts',
        PORT: '8001'
      });

      backendProcess = spawn(BACKEND_PATH, [], { env });

      backendProcess.stdout.on('data', (data) => {
        console.log(`Backend: ${data}`);
      });

      backendProcess.stderr.on('data', (data) => {
        console.error(`Backend Error: ${data}`);
      });

      backendProcess.on('error', (error) => {
        console.error('Failed to start backend:', error);
        reject(error);
      });

      // Wait for backend to start
      setTimeout(() => {
        console.log('Backend started');
        resolve();
      }, 3000);
    } catch (error) {
      console.error('Error starting backend:', error);
      reject(error);
    }
  });
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 800,
    minHeight: 600,
    icon: path.join(__dirname, 'icon.ico'),
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    },
    frame: true,
    titleBarStyle: 'default',
    title: 'Tool Tạo Acc Garena'
  });

  const startURL = isDev
    ? 'http://localhost:3000'
    : `file://${path.join(__dirname, '../build/index.html')}`;

  mainWindow.loadURL(startURL);

  if (isDev) {
    mainWindow.webContents.openDevTools();
  }

  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  // Minimize to tray
  mainWindow.on('minimize', (event) => {
    event.preventDefault();
    mainWindow.hide();
  });

  mainWindow.on('close', (event) => {
    if (!app.isQuiting) {
      event.preventDefault();
      mainWindow.hide();
    }
    return false;
  });
}

function createTray() {
  tray = new Tray(path.join(__dirname, 'icon.ico'));
  
  const contextMenu = Menu.buildFromTemplate([
    {
      label: 'Mở Tool Tạo Acc Garena',
      click: () => {
        mainWindow.show();
      }
    },
    {
      label: 'Thoát',
      click: () => {
        app.isQuiting = true;
        app.quit();
      }
    }
  ]);

  tray.setToolTip('Tool Tạo Acc Garena');
  tray.setContextMenu(contextMenu);
  
  tray.on('double-click', () => {
    mainWindow.show();
  });
}

// Auto-start management
ipcMain.handle('get-auto-start', () => {
  return app.getLoginItemSettings().openAtLogin;
});

ipcMain.handle('set-auto-start', (event, enabled) => {
  app.setLoginItemSettings({
    openAtLogin: enabled,
    openAsHidden: false
  });
  return true;
});

// Settings management
ipcMain.handle('get-settings', () => {
  return store.store;
});

ipcMain.handle('set-setting', (event, key, value) => {
  store.set(key, value);
  return true;
});

app.on('ready', async () => {
  try {
    // Start MongoDB first
    await startMongoDB();
    
    // Then start backend
    await startBackend();
    
    // Create window and tray
    createWindow();
    createTray();
    
    console.log('App started successfully');
  } catch (error) {
    console.error('Failed to start app:', error);
  }
});

app.on('window-all-closed', () => {
  // Don't quit on window close, keep in tray
});

app.on('activate', () => {
  if (mainWindow === null) {
    createWindow();
  }
});

app.on('before-quit', () => {
  app.isQuiting = true;
  
  // Kill processes
  if (backendProcess) {
    backendProcess.kill();
  }
  if (mongoProcess) {
    mongoProcess.kill();
  }
});
