function changeAllCheckboxes(event){
    // set all checkbox checked
  let tableRows =document.getElementsByTagName("tbody")[0].rows;
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
function updateAccountsInfoBadges(){

}
//get main checkbox
const checkbox = document.getElementById('flexCheckDefault')
//set listener for change main checkbox
checkbox.addEventListener('change', (event) => {
  changeAllCheckboxes(event)
});