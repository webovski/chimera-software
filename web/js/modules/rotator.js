let current_rotation = 0;
let rotating = false

function rotationAnimation() {
    if (rotating) {
        let sync_icon = document.getElementById('sync-icon')
        current_rotation += 180;
        sync_icon.style.transform = 'rotate(' + current_rotation + 'deg)';
        startRotating(750, false)
    }
}

eel.expose(startRotating)
function startRotating(timeout, stopRotating) {
    if (stopRotating === 'false') {
        rotating = false
    } else {
        rotating = true
        setTimeout(
            rotationAnimation,
            timeout
        );
    }
}
