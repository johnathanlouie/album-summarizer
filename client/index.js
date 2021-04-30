const { app, BrowserWindow, ipcMain } = require('electron');
const process = require('process');

// Holds all subprocess IDs.
const pids = [];

function createWindow() {
    // Create the browser window.
    const win = new BrowserWindow({
        width: 1600,
        height: 900,
        webPreferences: {
            nodeIntegration: true
        }
    });
    win.maximize();

    // Removes the menu bar on linux, windows, but not macOS.
    win.removeMenu();

    // and load the index.html of the app.
    win.loadFile('index.html');

    // Open the DevTools.
    // win.webContents.openDevTools();
}

// This method will be called when Electron has finished
// initialization and is ready to create browser windows.
// Some APIs can only be used after this event occurs.
app.whenReady().then(createWindow);

// Quit when all windows are closed, except on macOS. There, it's common
// for applications and their menu bar to stay active until the user quits
// explicitly with Cmd + Q.
app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('activate', () => {
    // On macOS it's common to re-create a window in the app when the
    // dock icon is clicked and there are no other windows open.
    if (BrowserWindow.getAllWindows().length === 0) {
        createWindow();
    }
});

// When a subprocess is created by the renderer, keep track of the PID.
ipcMain.on('add-pid', function (event, arg) {
    pids.push(arg);
    console.log(`Added PID ${arg}`);
});

// When a subprocess ends, remove it from the array.
ipcMain.on('remove-pid', function (event, arg) {
    var i = pids.indexOf(arg);
    if (i >= 0) {
        pids.splice(i, 1);
        console.log(`Removed PID ${arg}`);
    } else {
        console.log(`PID ${arg} not found`);
    }
});

app.on('before-quit', () => {
    pids.forEach(pid => {
        process.kill(pid);
        console.log(`Killed PID ${pid}`);
    });
});

// In this file you can include the rest of your app's specific main process
// code. You can also put them in separate files and require them here.