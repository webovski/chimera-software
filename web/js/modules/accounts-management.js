let accountsTable = document.getElementById('account-table-body')
eel.expose(renderAccountsList)

function renderAccountsList(accountsTableItemsHtml) {
    accountsTable.innerHTML = ''
    accountsTable.innerHTML += accountsTableItemsHtml
}

eel.expose(updateAccountsBadges)

function updateAccountsBadges(accounts_all, accounts_valid, accounts_not_checked, accounts_spam_block, accounts_deleted) {
    let accountsAllBadge = document.getElementById('all-accounts-badge')
    let accountsValidBadge = document.getElementById('valid-accounts-badge')
    let accountsNotCheckedBadge = document.getElementById('not-checked-accounts-badge')
    let accountSpamBlockBadge = document.getElementById('spam-block-accounts-badge')
    let accountDeletedBadge = document.getElementById('deleted-accounts-badge')

    accountsAllBadge.innerText = accounts_all
    accountsValidBadge.innerText = accounts_valid
    accountsNotCheckedBadge.innerText = accounts_not_checked
    accountSpamBlockBadge.innerText = accounts_spam_block
    accountDeletedBadge.innerText = accounts_deleted
}

function uploadNewAccounts() {
    //get invisible object for load directory
    let directoryPicker = document.getElementById('fileselector');
    let directoryPath = directoryPicker.files[0].path.match(/(.*)[\/\\]/)[1] || '';
    //copy accounts from direct
    console.log(directoryPath);
    eel.copy_accounts(directoryPath)
    //render accounts list on view
    eel.render_accounts_list()
}

function getAllSelectedAccounts() {
    // get selected accounts by checkboxes
    let tableBody = document.getElementById("account-table-body");
    //get selected checkboxes and convert nodelist to standart array
    //for use filter and etc methods
    let selectAccountsCheckBoxes = Array.prototype.slice.call(tableBody.querySelectorAll('input[type=checkbox]:checked'));
    let sessionsArray = [];
    selectAccountsCheckBoxes.forEach(function (account) {
        sessionsArray.push(account.value);
    })

    return sessionsArray
}

function getOnlyLiveSelectedAccounts() {
    // get selected accounts by checkboxes
    let tableBody = document.getElementById("account-table-body");
    //get selected checkboxes and convert nodelist to standart array
    //for use filter and etc methods
    let selectAccountsCheckBoxes = Array.prototype.slice.call(tableBody.querySelectorAll('input[type=checkbox]:checked'));
    let sessionsArray = [];
    selectAccountsCheckBoxes.forEach(function (account) {
        if (account.dataset.accountStatus !== "Удалён") {
            sessionsArray.push(account.value);
        }
    })

    return sessionsArray
}

function updateProxies() {
    //update proxies for selected accounts
    let accountsList = getOnlyLiveSelectedAccounts();
    if (accountsList.length > 0) {
        eel.set_proxies(accountsList)
    } else {
        displayToast('Вы не выбрали аккаунты!', 'error')
        //send warning message about need choose accounts before
    }
}

function changeAllCheckboxes(event) {
    // set all checkbox checked
    let tableRows = document.getElementsByTagName("tbody")[0].rows;
    if (event.currentTarget.checked) {
        for (let i = 0; i < tableRows.length; i++) {
            let checkbox = tableRows[i].querySelectorAll('input[type=checkbox]');
            checkbox[0].checked = true;
        }
    } else {
        for (let i = 0; i < tableRows.length; i++) {
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
    let accountsList = getAllSelectedAccounts();
    if (accountsList.length > 0) {
        startRotating(750, false, 'sync-icon')
        blockButton('checking-accounts-btn', 'checking-accounts-btn-text', 'Проверяем аккаунты')
        eel.check_accounts(accountsList)
    } else {
        displayToast('Вы не выбрали аккаунты!', 'error')
    }
}


eel.expose(blockTableRow)

function blockTableRow(sessionName) {
    let format = `tr_${sessionName}`;
    let selectTRofTable = document.getElementById(format);
    selectTRofTable.style.pointerEvents = "none";
    selectTRofTable.style.opacity = '0.5';
}

eel.expose(unblockTableRow)

function unblockTableRow(sessionName) {
    let format = `tr_${sessionName}`;
    let selectTRofTable = document.getElementById(format);
    selectTRofTable.style.pointerEvents = "all";
    selectTRofTable.style.opacity = '1';
}

function getSmsCode(sessionName) {
    blockTableRow(sessionName);
    eel.get_sms_code(sessionName);
}

function addNewAccount() {
    let accountPhone = document.getElementById('phone-number-input')
    let smsCode = document.getElementById('sms-code-input')
    let cloudPassword = document.getElementById('cloud-password-input')
    let phoneCodeHash = document.getElementById('phone-code-hash-input')
    let userInfoContainer = document.getElementById('adding-account-process-container')
    userInfoContainer.classList.remove('active')

    let accountPlaneIcon = document.getElementById('add-account-button-i')
    let accountSpinnerAnimation = document.getElementById('add-account-button-spinner')
    accountPlaneIcon.style.display = 'none'
    accountSpinnerAnimation.style.display = 'inline-block'
    blockButton('add-account-button', 'send-code-button-text', 'Обработка')

    console.log(accountPhone, cloudPassword, cloudPassword, phoneCodeHash)

    eel.add_new_account(accountPhone.value, smsCode.value, cloudPassword.value, phoneCodeHash.value);
}

eel.expose(setPhoneCodeHash)

function setPhoneCodeHash(phoneCodeHashFromTelegram) {
    let phoneCodeHash = document.getElementById('phone-code-hash-input')
    phoneCodeHash.value = phoneCodeHashFromTelegram
    unblockButton('add-account-button', 'send-code-button-text', 'Добавить аккаунт')
    let accountPlaneIcon = document.getElementById('add-account-button-i')
    let accountSpinnerAnimation = document.getElementById('add-account-button-spinner')
    accountPlaneIcon.style.display = 'contents'
    accountSpinnerAnimation.style.display = 'none'
}

eel.expose(informUserAboutPhoneAdding)

function informUserAboutPhoneAdding(message, alertType) {
    let userInfoContainer = document.getElementById('adding-account-process-container')
    let informTextContainer = document.getElementById('inform-text-container')
    informTextContainer.innerText = message
    informTextContainer.className = `alert alert-${alertType}`
    userInfoContainer.classList.add('active')
    unblockButton('add-account-button', 'send-code-button-text', 'Добавить аккаунт')
    let accountPlaneIcon = document.getElementById('add-account-button-i')
    let accountSpinnerAnimation = document.getElementById('add-account-button-spinner')
    accountPlaneIcon.style.display = 'contents'
    accountSpinnerAnimation.style.display = 'none'
}

function clearAddingAccountForm() {
    let accountPhone = document.getElementById('phone-number-input')
    let smsCode = document.getElementById('sms-code-input')
    let cloudPassword = document.getElementById('cloud-password-input')
    let phoneCodeHash = document.getElementById('phone-code-hash-input')

    accountPhone.classList.remove('active')
    smsCode.classList.remove('active')
    cloudPassword.classList.remove('active')
    phoneCodeHash.classList.remove('active')

    accountPhone.value = ''
    smsCode.value = ''
    cloudPassword.value = ''
    phoneCodeHash.value = ''

    let userInfoContainer = document.getElementById('adding-account-process-container')
    userInfoContainer.value = ''
    userInfoContainer.classList.remove('active')
}

function removeAccounts() {
    let accountsList = getAllSelectedAccounts();
    if (accountsList.length > 0) {
        //blockButton('remove-accounts-btn');
        eel.delete_accounts(accountsList)
    } else {
        displayToast('Вы не выбрали аккаунты!', 'error')
    }
}


function createAccountsArchive() {
    let accountsList = getAllSelectedAccounts();
    if (accountsList.length > 0) {
        eel.create_zip(accountsList)
    } else {
        displayToast('Вы не выбрали аккаунты!', 'error')
    }
}

function getAccountsByFilter(filterName) {
    switch (filterName) {
        case 'all':
            eel.render_accounts_by_filter();
            break;
        case 'not-checked':
            eel.render_accounts_by_filter('Не проверен');
            break;
        case 'valid':
            eel.render_accounts_by_filter('Проверен');
            break;
        case 'spam-block':
            eel.render_accounts_by_filter('Спам-Блок');
            break;
        case 'spam-block':
            eel.render_accounts_by_filter('Спам-Блок');
            break;
        case 'deleted':
            eel.render_accounts_by_filter('Удалён');
            break;
    }
}
