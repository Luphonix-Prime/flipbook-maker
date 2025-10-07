const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  uploadPDF: async (formData) => {
    return await fetch('http://127.0.0.1:5000/upload', {
      method: 'POST',
      body: formData
    }).then(res => res.json());
  },
  exportFlipbook: async (flipbookId) => {
    try {
      // First try the direct export through Electron
      const result = await ipcRenderer.invoke('export-flipbook', flipbookId);
      if (result.success) {
        return { success: true };
      }
      
      // Fallback to Flask endpoint if direct export fails
      const response = await fetch(`http://127.0.0.1:5000/export/${flipbookId}`, {
        method: 'POST'
      });
      
      if (!response.ok) {
        throw new Error('Export failed');
      }
      return response.json();
    } catch (error) {
      console.error('Export error:', error);
      throw error;
    }
  },
  checkExport: async (flipbookId) => {
    const response = await fetch(`http://127.0.0.1:5000/check-export/${flipbookId}`);
    if (!response.ok) {
      throw new Error('Failed to check export status');
    }
    return response.json();
  },
  downloadExe: async (flipbookId) => {
    const response = await fetch(`http://127.0.0.1:5000/download/${flipbookId}`);
    if (!response.ok) {
      throw new Error('Failed to download executable');
    }
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${flipbookId}.exe`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  },
  onExportStarted: (callback) => {
    ipcRenderer.on('export-started', () => callback());
  },
  
  onExportProgress: (callback) => {
    ipcRenderer.on('export-progress', (_, data) => callback(data));
  },
  
  onExportError: (callback) => {
    ipcRenderer.on('export-error', (_, data) => callback(data));
  },
  
  onExportComplete: (callback) => {
    ipcRenderer.on('export-complete', () => callback());
  }
});