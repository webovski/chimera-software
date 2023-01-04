eel.render_accounts_list()
updateAccountsBadges()
document.querySelectorAll('.form-outline').forEach((formOutline) => {
    try {
        new mdb.Input(formOutline).init();
    } catch (e) {
    }
});
document.querySelectorAll('.form-select').forEach((fromSelect) => {
    try {
        new mdb.Input(fromSelect).init();
    } catch (e) {
    }
});
$("#menu-toggle").click(function (e) {
    e.preventDefault();
    $("#wrapper").toggleClass("toggled");
});
$('[rel="tooltip"]').on('click', function () {
    $(this).tooltip('hide')
})
$('#pro-li').click(function () {
    let proMenu = document.getElementById('pro-menu-list')
    let proAnimation = document.getElementById('menu-item-span')
    let settingsLi = document.getElementById('settings-li')
    if (proMenu.style.maxHeight) {
        proMenu.style.maxHeight = null;
        proAnimation.classList.remove('opened')
        settingsLi.style.borderTop = '0px solid #f4f4f4'
    } else {
        proMenu.style.maxHeight = proMenu.scrollHeight + "px";
        proAnimation.classList.add('opened')
        settingsLi.style.borderTop = '2px solid #f4f4f4'
    }
});


eel.expose(blockButton)

function blockButton(buttonId, buttonTextId = null, textOnButton = "") {
    let selectedButton = document.getElementById(buttonId)
    if (buttonTextId !== null) {
        let buttonText = document.getElementById(buttonTextId)
        buttonText.innerText = textOnButton
    }
    selectedButton.style.pointerEvents = 'none';
    selectedButton.style.opacity = '0.5';
}

eel.expose(unblockButton)
function unblockButton(buttonId, buttonTextId = null, textOnButton = "") {
    let selectedButton = document.getElementById(buttonId)
    if (buttonTextId !== null) {
        let buttonText = document.getElementById(buttonTextId)
        buttonText.innerText = textOnButton
    }
    selectedButton.style.pointerEvents = 'all';
    selectedButton.style.opacity = '1';
}

eel.expose(switchIcons)
function switchIcons(currentIconId, newIconId) {
    let iconSearchParsing = document.getElementById(currentIconId)
    iconSearchParsing.style.display = 'none'
    let iconSyncParsing = document.getElementById(newIconId)
    iconSyncParsing.style.display = 'contents'
}


function copyTextToClipboard(elementId) {
    //for copy text from objects by id
    let element = document.getElementById(elementId);
    if (element !== null) {
        element.setSelectionRange(0, 99999999);
        navigator.clipboard.writeText(element.value);
    }
}

eel.expose(writeLog)

function writeLog(textAreaId, text) {
    let textArea = document.getElementById(textAreaId);
    if (textArea !== null) {
        let time = getCurrentTime();
        textArea.value += `\n[${time}]: ${text}`;
    }
}

function getCurrentTime() {
    let today = new Date();
    return today.getHours() + ":" + ('0'+today.getMinutes()).slice(-2)+':'+ ('0'+today.getSeconds()).slice(-2);
}

eel.expose(autoScroll)
function autoScroll(testAreaId) {
    let textarea = document.getElementById(testAreaId);
    textarea.scrollTop = textarea.scrollHeight;
}