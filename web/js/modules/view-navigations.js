eel.expose(updateAccountsBadges)
function updateAccountsBadges(accounts_all, accounts_valid, accounts_not_checked, accounts_spam_block) {
    let accountsAllBadge = document.getElementById('all-accounts-badge')
    let accountsValidBadge = document.getElementById('valid-accounts-badge')
    let accountsNotCheckedBadge = document.getElementById('not-checked-accounts-badge')
    let accountSpamBlockBadge = document.getElementById('spam-block-accounts-badge')

    accountsAllBadge.innerText = accounts_all
    accountsValidBadge.innerText = accounts_valid
    accountsNotCheckedBadge.innerText = accounts_not_checked
    accountSpamBlockBadge.innerText = accounts_spam_block
}

function uploadNewAccounts() {
    console.log("fuck");
    //get invisible object for load directory
    let directoryPicker = document.getElementById('fileselector');
    let directoryPath = directoryPicker.files[0].path.match(/(.*)[\/\\]/)[1]||'';
    //copy accounts from direct
    console.log(directoryPath);
    eel.copy_accounts(directoryPath)
    //render accounts list on view
    eel.render_accounts_list()
}

function getSelectedAccounts(){
    // get selected accounts by checkboxes
    let tableBody = document.getElementsByTagName("tbody")[0];
    let selectAccountsCheckBoxes = tableBody.querySelectorAll('input[type=checkbox]:checked');
    let sessionsArray = [];
    selectAccountsCheckBoxes.forEach(account => sessionsArray.push(account.value));
    console.log(sessionsArray);
    return sessionsArray
}

function updateProxies(){
    //update proxies for selected accounts
    let accountsList = getSelectedAccounts();
    if(accountsList.length > 0){
        eel.set_proxies(accountsList)
    } else {
        displayToast('Вы не выбрали аккаунты!', 'error')
        //send warning message about need choose accounts before
    }
}

function changeAllCheckboxes(event){
    // set all checkbox checked
  let tableRows = document.getElementsByTagName("tbody")[0].rows;
  if (event.currentTarget.checked) {
    for(let i=0;i<tableRows.length;i++){
      let checkbox = tableRows[i].querySelectorAll('input[type=checkbox]');
      checkbox[0].checked = true;
    }
    } else {
    for(let i=0;i<tableRows.length;i++){
      let checkbox = tableRows[i].querySelectorAll('input[type=checkbox]');
      checkbox[0].checked = false;
    }
  }
}
const checkbox = document.getElementById('flexCheckDefault')
//set listener for change main checkbox
checkbox.addEventListener('change', (event) => {
  changeAllCheckboxes(event)
});

function checkAccounts() {
    let accountsList = getSelectedAccounts();
    if(accountsList.length > 0){
        startRotating(750, false)
        blockButton('checking-accounts-btn', 'checking-accounts-btn-text', 'Проверяем аккаунты')
        eel.check_accounts(accountsList)
    } else {
        displayToast('Вы не выбрали аккаунты!', 'error')
    }
}

eel.expose(blockButton)
function blockButton(buttonId, buttonTextId, textOnButton) {
    let selectedButton = document.getElementById(buttonId)
    let buttonText = document.getElementById(buttonTextId)
    buttonText.innerText = textOnButton
    selectedButton.style.pointerEvents = 'none';
    selectedButton.style.opacity = '0.5';
}

eel.expose(unblockButton)
function unblockButton(buttonId, buttonTextId, textOnButton) {
    let selectedButton = document.getElementById(buttonId)
    let buttonText = document.getElementById(buttonTextId)
    buttonText.innerText = textOnButton
    selectedButton.style.pointerEvents = 'all';
    selectedButton.style.opacity = '1';
}