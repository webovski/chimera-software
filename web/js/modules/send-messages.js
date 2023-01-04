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