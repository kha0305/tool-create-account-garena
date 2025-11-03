const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electron', {
  getSettings: () => ipcRenderer.invoke('get-settings'),
  saveSettings: (settings) => ipcRenderer.invoke('save-settings', settings),
  getBackendUrl: () => ipcRenderer.invoke('get-backend-url'),
  selectDirectory: () => ipcRenderer.invoke('select-directory'),
  platform: process.platform
});