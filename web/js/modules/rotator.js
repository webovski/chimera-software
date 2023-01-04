let current_rotation = 0;
let rotating = false

function rotationAnimation(iconId) {
    if (rotating) {
        let icon = document.getElementById(iconId)
        let current_rotation = parseInt(icon.style.transform.replace('rotate(', ''). replace('deg)', ''));
        if (isNaN(current_rotation)) {
            current_rotation = 180
        } else {
           current_rotation += 180;
        }
        console.log(current_rotation, iconId)
        icon.style.transform = 'rotate(' + current_rotation + 'deg)';
        startRotating(750, false, iconId)
    }
}

eel.expose(startRotating)
function startRotating(timeout, stopRotating, iconId) {
    if (stopRotating === 'false') {
        rotating = false
    } else {
        rotating = true
        setTimeout(
            rotationAnimation,
            timeout,
            iconId
        );
    }
}
