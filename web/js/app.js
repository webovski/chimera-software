eel.expose(displayToast)

function displayToast(text, event_type) {
    switch (event_type) {
        case 'success':
            new SnackBar({message: text, status: "success", timeout: 100000});
            break;
        case 'error':
            new SnackBar({message: text, status: "error", timeout: 100000});
            break;
        case 'info':
            new SnackBar({message: text, status: "info", timeout: 100000});
            break;
        default:
            new SnackBar({message: text, status: "error", timeout: 100000});
    }
}


eel.expose(backToLogin)

function backToLogin() {
    document.getElementById('loading').style.display = 'none';
    document.getElementById('auth').style.display = 'block';
}

eel.expose(openApp)

function openApp() {
    document.getElementById('loading').style.display = 'none';
    document.getElementById('app').style.display = 'block';
}

