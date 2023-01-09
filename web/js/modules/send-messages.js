function validateChatType() {
    let sendingChatTypeDropdown = document.getElementById("sending-chat-type-dropdown");
    let sendingUserTypeDropdown = document.getElementById("target-sending-user-type-dropdown");
    let recipientsUploadButton = document.getElementById("sending-recipients-upload-button");
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
    let messageTypeDropdown = document.getElementById("sending-message-type")
    let forwardFromLinkInput = document.getElementById("sending-link-forward-input")
    let messageTextArea = document.getElementById('message-text-area')

    let linkForwardContainer = document.getElementById('sending-link-forward-input')
    let addFileButton = document.getElementById('sending-add-file-button')

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

function uploadRecipients(){
    //get invisible object for load recipients
    let filePicker = document.getElementById('recipientsFileSelector');
    let recipientFilePath = filePicker.files[0].path;
    //copy accounts from direct
    console.log(recipientFilePath);
}
function startSendingMessages(){
        let messageText = document.getElementById('message-text-area');
        //тип получателя
        let recipientType = document.getElementById('target-user-type-dropdown');
        let chatType = document.getElementById('sending-chat-type-dropdown');
        let messageType = document.getElementById('message-type');
        let linkOnPost = document.getElementById('forward-from-link');
        let accountLimit = document.getElementById('account-limit');
        let delayFrom = document.getElementById('delay-between-sms-from');
        let delayTo = document.getElementById('delay-between-sms-to');
}