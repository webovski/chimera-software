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