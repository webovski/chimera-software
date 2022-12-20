const {app, BrowserWindow} = require('electron')
const path = require('path')
const devMode = false

if (devMode) {
    require('electron-reload')(__dirname, {
       electron: require(`${__dirname}/node_modules/electron`)
    });
}

function createWindow() {
    const win = new BrowserWindow({
        width: 1200, height: 800, resizable: true, show: false, webPreferences: {
            preload: path.join(__dirname, 'preloader.js')
        },
        icon: path.join(__dirname, 'app.ico')
    })

    const splash = new BrowserWindow({
        width: 800, height: 630, transparent: true, frame: false, alwaysOnTop: true, icon: path.join(__dirname, 'app.ico')
    });
    splash.setMenuBarVisibility(false)
    win.setMenuBarVisibility(false)
    splash.loadFile('splash.html');
    splash.center();
    win.maximize();
    if (devMode) {
        win.loadFile('web/app.html')
    } else {
        win.loadURL('http://localhost:7255/app.html')
    }

    win.webContents.once('dom-ready', () => {
        splash.close();
        win.center();
        win.show();
        win.maximize();
        win.webContents.openDevTools()
    });
}

app.whenReady().then(() => {
    createWindow()

    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) {
            createWindow()
        }
    })
})

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit()
    }
})