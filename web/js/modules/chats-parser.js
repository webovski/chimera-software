function validateChatType() {
    let sendingChatTypeDropdown = document.getElementById("sending-chat-type-dropdown");
    let sendingUserTypeDropdown = document.getElementById("target-user-type-dropdown");
    let recipientsUploadButton = document.getElementById("recipients-upload-button");
    if (sendingChatTypeDropdown.value === "Диалог") {
        sendingUserTypeDropdown.disabled = true
        recipientsUploadButton.style.pointerEvents = 'none'
        recipientsUploadButton.style.opacity = '0.5'
    } else {
        sendingUserTypeDropdown.disabled = false
        recipientsUploadButton.style.pointerEvents = 'all'
        recipientsUploadButton.style.opacity = '1'
    }
}

function validateMessageType() {
    let messageTypeDropdown = document.getElementById("message-type")
    let forwardFromLinkInput = document.getElementById("forward-from-link")
    let messageTextArea = document.getElementById('message-text-area')

    let linkForwardContainer = document.getElementById('link-forward-input')
    let addFileButton = document.getElementById('add-file-button')

    if (messageTypeDropdown.value === "Репост") {
        forwardFromLinkInput.disabled = false
        messageTextArea.disabled = true
        linkForwardContainer.style.display = 'block'
        addFileButton.style.display = 'none'
    } else if (messageTypeDropdown.value === "Медиа файл") {
        addFileButton.style.display = 'block'
        linkForwardContainer.style.display = 'none'
        messageTextArea.disabled = false
    } else {
        forwardFromLinkInput.value = ''
        forwardFromLinkInput.classList.remove('active')
        forwardFromLinkInput.disabled = true
        messageTextArea.disabled = false
    }
}

function parseDialogs() {
    let parseDialogsCheckboxIsChecked = document.getElementById('parse-dialogs').checked
    if (parseDialogsCheckboxIsChecked) {
        document.getElementById('chat-link-label').innerText = 'Название чата';
    } else {
        document.getElementById('chat-link-label').innerText = 'Ссылка на чат';
    }
}

function runChatsScraping() {

    let onlyPhotos = document.getElementById("parse-only-photo");
    let chatLink = document.getElementById('chat-link');
    let dialogsParsing = document.getElementById('parse-dialogs');
    let fastParsing = document.getElementById('parse-fast');
    let parsePremium = document.getElementById('parse-premium');
    let parsePhones = document.getElementById('parse-phones');
    let parseOnlyAdmins = document.getElementById('parse-only-admins');
    let parseOnlyBots = document.getElementById('parse-only-bots');

    if (chatLink.value === "") {
        displayToast('Вы не указали чат!', 'error')
    } else {
        let sessions = getOnlyLiveSelectedAccounts()
        if (sessions.length < 1) {
            displayToast('Вы не выбрали аккаунты для парсинга!', 'error')
        } else {
            //check if select more one account before scraping by dialogs
            if (sessions.length > 1 && dialogsParsing.checked === true) {
                displayToast('Выберите один аккаунт в котором находится диалог!', 'error')
            } else {
                console.log(chatLink.value, dialogsParsing.checked, fastParsing.checked, parsePremium.checked, parsePhones.checked, parseOnlyAdmins.checked, parseOnlyBots.checked,)

                let parsingParameters = {
                    "chat": chatLink.value,
                    "dialogsParsing": dialogsParsing.checked,
                    "fastParsing": fastParsing.checked,
                    "premium": parsePremium.checked,
                    "parsePhones": parsePhones.checked,
                    "parseOnlyAdmins": parseOnlyAdmins.checked,
                    "parseOnlyBots": parseOnlyBots.checked,
                    "onlyPhotos": onlyPhotos.checked,
                }
                eel.run_parsing(sessions, parsingParameters);
                blockButton("clear-parsing-database");
                blockButton("download-parsing-results");
                let iconSearchParsing = document.getElementById('icon-search-parsing')
                iconSearchParsing.style.display = 'none'
                let iconSyncParsing = document.getElementById('icon-sync-parsing')
                iconSyncParsing.style.display = 'inherit'

                startRotating(750, false, 'icon-sync-parsing')
                blockButton('start-parsing-btn', 'start-parsing-btn-text', 'Парсинг запущен')
            }
        }
    }
}


function removeScrapingDB() {
    eel.remove_scraping_db()
}

function convertDBtoExcel() {
    writeLog("result-users-text-area", "Создание отчета начато!")
    blockButton('start-parsing-btn')
    eel.convert_db_to_excel()
     blockButton("download-parsing-results");
    blockButton("clear-parsing-database");
}