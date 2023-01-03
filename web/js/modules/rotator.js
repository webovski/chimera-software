let current_rotation = 0;
let rotating = false

function rotationAnimation(iconId, initDeg) {
    if (rotating) {
        let icon = document.getElementById(iconId)
        let current_rotation = initDeg;
        current_rotation += 180;
        icon.style.transform = 'rotate(' + current_rotation + 'deg)';
        startRotating(750, false, iconId, current_rotation)
    }
}

eel.expose(startRotating)
function startRotating(timeout, stopRotating, iconId, initDeg) {
    if (stopRotating === 'false') {
        rotating = false
    } else {
        rotating = true
        setTimeout(
            rotationAnimation,
            timeout,
            iconId,
            initDeg
        );
    }
}
