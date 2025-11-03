const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs');
const isDev = require('electron-is-dev');

// Initialize store as null, will be set after app is ready
let store = null;

// Function to initialize store
async function initializeStore() {
  if (!store) {
    const Store = (await import('electron-store')).default;
    store = new Store();
  }
  return store;
}

let mainWindow;
let backendProcess;

// Backend server configuration
const BACKEND_PORT = 8001;
const BACKEND_HOST = 'localhost';

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      enableRemoteModule: false,
      preload: path.join(__dirname, 'preload.js')
    },
    icon: path.join(__dirname, 'icon.png'),
    title: 'Garena Account Creator'
  });

  // Load the app
  if (isDev) {
    mainWindow.loadURL('http://localhost:3000');
    mainWindow.webContents.openDevTools();
  } else {
    mainWindow.loadFile(path.join(__dirname, '../build/index.html'));
  }

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

function startBackendServer() {
  return new Promise(async (resolve, reject) => {
    try {
      let backendPath;
      let command;
      let args;

      // Initialize store if not already done
      await initializeStore();

      // Get settings from store
      const mongoUrl = store.get('mongoUrl', 'mongodb://localhost:27017');
      const apiKey = store.get('apiKey', '');
      const dbName = store.get('dbName', 'garena_creator_db');

      if (isDev) {
        // Development mode - use Python directly
        backendPath = path.join(__dirname, '../../backend');
        command = 'python';
        args = ['-m', 'uvicorn', 'server:app', '--host', '0.0.0.0', '--port', BACKEND_PORT.toString()];
      } else {
        // Production mode - use packaged executable
        if (process.platform === 'win32') {
          backendPath = path.join(process.resourcesPath, 'backend', 'server.exe');
          command = backendPath;
          args = [];
        } else if (process.platform === 'darwin') {
          backendPath = path.join(process.resourcesPath, 'backend', 'server');
          command = backendPath;
          args = [];
        } else {
          backendPath = path.join(process.resourcesPath, 'backend', 'server');
          command = backendPath;
          args = [];
        }
      }

      console.log('Starting backend:', command, args);
      console.log('Backend path:', backendPath);

      // Set environment variables from settings
      const env = {
        ...process.env,
        MONGO_URL: mongoUrl,
        DB_NAME: dbName,
        CORS_ORIGINS: '*'
      };
      
      if (apiKey) {
        env.TEMP_MAIL_API_KEY = apiKey;
      }

      const options = isDev 
        ? { cwd: backendPath, shell: true, env } 
        : { shell: false, env };
      
      backendProcess = spawn(command, args, options);

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

      backendProcess.on('close', (code) => {
        console.log(`Backend process exited with code ${code}`);
      });

      // Wait for backend to be ready
      setTimeout(() => {
        console.log('Backend server should be ready');
        resolve();
      }, 3000);
    } catch (error) {
      console.error('Error starting backend:', error);
      reject(error);
    }
  });
}

function stopBackendServer() {
  if (backendProcess) {
    console.log('Stopping backend server...');
    backendProcess.kill();
    backendProcess = null;
  }
}

// IPC Handlers for settings
ipcMain.handle('get-settings', async () => {
  await initializeStore();
  return {
    mongoUrl: store.get('mongoUrl', ''),
    apiKey: store.get('apiKey', ''),
    dbName: store.get('dbName', 'garena_creator_db'),
    backendUrl: `http://${BACKEND_HOST}:${BACKEND_PORT}`
  };
});

ipcMain.handle('save-settings', async (event, settings) => {
  try {
    await initializeStore();
    if (settings.mongoUrl) store.set('mongoUrl', settings.mongoUrl);
    if (settings.apiKey) store.set('apiKey', settings.apiKey);
    if (settings.dbName) store.set('dbName', settings.dbName);
    return { success: true };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('get-backend-url', async () => {
  return `http://${BACKEND_HOST}:${BACKEND_PORT}`;
});

ipcMain.handle('select-directory', async () => {
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openDirectory']
  });
  return result.filePaths[0];
});

// App lifecycle
app.whenReady().then(async () => {
  try {
    console.log('Starting application...');
    await startBackendServer();
    createWindow();
  } catch (error) {
    console.error('Failed to start application:', error);
    dialog.showErrorBox('Startup Error', `Failed to start backend server: ${error.message}`);
    app.quit();
  }
});

app.on('window-all-closed', () => {
  stopBackendServer();
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (mainWindow === null) {
    createWindow();
  }
});

app.on('before-quit', () => {
  stopBackendServer();
});

app.on('will-quit', () => {
  stopBackendServer();
});