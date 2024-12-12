

// Modal open/close logic
const loginModal = document.getElementById("loginModal");
const openLoginModal = document.getElementById("open-login");

const registerModal = document.getElementById("registerModal");
const openRegisterModal = document.getElementById("open-signup");

const notificationModal = document.getElementById("notificationModal");

const postModal = document.getElementById("postModal");
const openPostModal = document.getElementById("open-add-post");

const closeLoginModal = document.getElementById("closeLoginModal");
const closeRegisterModal = document.getElementById("closeRegisterModal");
const closePostModal = document.getElementById("closePostModal");

openLoginModal.onclick = () => loginModal.style.display = "block";
closeLoginModal.onclick = () => loginModal.style.display = "none";

openRegisterModal.onclick = () => registerModal.style.display = "block";
closeRegisterModal.onclick = () => registerModal.style.display = "none";





// openPostModal.onclick = () => postModal.style.display = "block";
function openModal() {
    postModal.style.display = "block";
}

function openNotificationModal() {
    notificationModal.style.display = "block";

    // Hide the badge
    const badge = document.querySelector(".notification-icon .badge");
    if (badge) {
        badge.style.display = "none";
    }

    // Optionally, mark notifications as read on the server
    fetch('/mark-notifications-read', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log("Notifications marked as read.");
            }
        })
        .catch(error => console.error("Error:", error));
}

function openInbox() {
    // Hide the badge
    const badge = document.querySelector(".notification-icon .badge2");
    if (badge) {
        badge.style.display = "none";
    }
}

function markRead(element) {

    const userId = element.getAttribute('data-user-id')
    // Optionally, mark notifications as read on the server
    fetch(`/mark-message-read/${userId}/read`, { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const badge = document.querySelector(`#messageBadge-${userId}`);
                if (badge) {
                    badge.style.display = "none";
                }
            }
        })
        .catch(error => console.error("Error:", error));
}

function closeNotificationModal() {
    notificationModal.style.display = "none";
}

function closeModal() {
    postModal.style.display = "none";
}
