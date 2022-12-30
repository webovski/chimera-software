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