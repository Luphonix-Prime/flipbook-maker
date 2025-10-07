const { app, BrowserWindow, dialog, Menu } = require('electron');
const path = require('path');
const { exec, spawn } = require('child_process');
const fs = require('fs');

let flaskProcess;
let mainWindow;

function startFlask() {
  console.log('🚀 Starting Flask server...');
  
  // Create required directories
  ['uploads', 'static/flipbooks', 'temp_images', 'output_exe'].forEach(dir => {
    const dirPath = path.join(__dirname, '..', dir);
    if (!fs.existsSync(dirPath)) {
      fs.mkdirSync(dirPath, { recursive: true });
    }
  });

  const appPath = path.join(__dirname, '..', 'app.py');
  const pythonPath = 'python';

  const env = {
    ...process.env,
    FLASK_ENV: 'production',
    FLASK_DEBUG: 'false',
    PYTHONPATH: path.join(__dirname, '..')  // Add parent directory to Python path
  };

  flaskProcess = exec(`"${pythonPath}" "${appPath}"`, { env }, (error, stdout, stderr) => {
    if (error) {
      dialog.showErrorBox('Flask Error', `Failed to start Flask server: ${error.message}`);
      app.quit();
      return;
    }
  });

  // Handle Flask process output
  flaskProcess.stdout.on('data', (data) => console.log(`Flask: ${data}`));
  flaskProcess.stderr.on('data', (data) => console.error(`Flask Error: ${data}`));
}

// Add new function to handle export
function handleExport(flipbookId) {
  return new Promise((resolve, reject) => {
    // Get the absolute paths
    const appRoot = path.join(__dirname, '..');
    const exportScript = path.join(appRoot, 'export_flipbook.py');
    const flipbookDir = path.join(appRoot, 'static', 'flipbooks', flipbookId);
    const outputDir = path.join(appRoot, 'output_exe');
    
    // Ensure directories exist
    fs.mkdirSync(outputDir, { recursive: true });
    
    // Use absolute paths for Python and script
    const pythonPath = 'python';
    
    console.log('Starting export process...');
    console.log('Export script:', exportScript);
    console.log('Flipbook directory:', flipbookDir);
    
    const exportProcess = spawn(pythonPath, [exportScript, flipbookId], {
      cwd: appRoot,  // Set working directory to app root
      env: {
        ...process.env,
        PYTHONPATH: appRoot,
        FLIPBOOK_DIR: flipbookDir,
        OUTPUT_DIR: outputDir
      }
    });

    exportProcess.stdout.on('data', (data) => {
      console.log(`Export output: ${data}`);
      mainWindow.webContents.send('export-progress', { message: data.toString() });
    });

    exportProcess.stderr.on('data', (data) => {
      console.error(`Export error: ${data}`);
      mainWindow.webContents.send('export-error', { error: data.toString() });
    });

    exportProcess.on('close', (code) => {
      if (code === 0) {
        mainWindow.webContents.send('export-complete');
        resolve();
      } else {
        const error = `Export process exited with code ${code}`;
        mainWindow.webContents.send('export-error', { error });
        reject(new Error(error));
      }
    });
  });
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    },
    show: false
  });

  // Create the menu template
  const template = [
    {
      label: 'File',
      submenu: [
        {
          label: 'Export as .exe',
          click: async () => {
            try {
              // Get the current flipbook ID from the URL
              const url = mainWindow.webContents.getURL();
              const match = url.match(/\/flipbook\/([^/]+)/);
              if (match) {
                const flipbookId = match[1];
                mainWindow.webContents.send('export-started');
                
                // Show progress dialog
                dialog.showMessageBox(mainWindow, {
                  type: 'info',
                  title: 'Export Started',
                  message: 'Creating standalone executable...\nThis may take a few minutes.',
                  buttons: ['OK']
                });

                await handleExport(flipbookId);
                
                // Show success dialog
                dialog.showMessageBox(mainWindow, {
                  type: 'info',
                  title: 'Export Complete',
                  message: 'Flipbook has been exported successfully!',
                  buttons: ['OK']
                });
              } else {
                dialog.showErrorBox('Export Error', 'Please open a flipbook first');
              }
            } catch (error) {
              dialog.showErrorBox('Export Error', error.message);
            }
          }
        },
        { type: 'separator' },
        { role: 'quit' }
      ]
    }
  ];

  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);

  let retries = 0;
  const maxRetries = 30;

  const checkServer = () => {
    fetch('http://127.0.0.1:5000')
      .then(() => {
        mainWindow.loadURL('http://127.0.0.1:5000');
        mainWindow.show();
      })
      .catch(() => {
        retries++;
        if (retries > maxRetries) {
          dialog.showErrorBox('Server Error', 'Failed to connect to Flask server');
          app.quit();
          return;
        }
        setTimeout(checkServer, 1000);
      });
  };

  setTimeout(checkServer, 2000);

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

app.whenReady().then(() => {
  startFlask();
  createWindow();
});

app.on('window-all-closed', () => {
  if (flaskProcess) {
    flaskProcess.kill();
  }
  app.quit();
});

app.on('quit', () => {
  if (flaskProcess) {
    flaskProcess.kill();
  }
});

// Add IPC handlers
const { ipcMain } = require('electron');

ipcMain.handle('export-flipbook', async (event, flipbookId) => {
  try {
    await handleExport(flipbookId);
    return { success: true };
  } catch (error) {
    console.error('Export error:', error);
    return { success: false, error: error.message };
  }
});
