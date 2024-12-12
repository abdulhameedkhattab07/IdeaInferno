const emojiModal = document.getElementById('emojiModal');
const messageInput = document.getElementById('message-input');
const post = document.getElementById('post');
const posted = document.getElementById('posted');
const main = document.getElementById('main');
const main2 = document.getElementById('main2');
const posted2 = document.getElementById('posted2');

const openEmojiModal = () => {
    emojiModal.style.display = "block";
}

function closeEmojiModal() {
    emojiModal.style.display = "none";
}

document.querySelectorAll('.emoji').forEach(emoji => {
    emoji.addEventListener('click', (event) => {

        const emojiSymbol = event.target.getAttribute('data-emoji');
        messageInput.value += emojiSymbol;
    });
});

post.addEventListener('click', () =>{
    main.classList.toggle('home');
    posted.style.display =  posted.style.display === 'grid' ? 'none' : 'grid';
});

function togglePost(){
    main2.classList.toggle('home');
    posted2.style.display =  posted2.style.display === 'grid' ? 'none' : 'grid';
}

function toggleFileOptions() {
    const fileOptions = document.getElementById("file-options");
    fileOptions.style.display = fileOptions.style.display === "none" ? "block" : "none";
}

function openImageModal(imageSrc){
    const imageModal = document.querySelector('#imageModal');
    const modalImg = document.getElementById('modalImage');
    imageModal.style.display = 'block';
    modalImg.style.backgroundImage = `url(${imageSrc})`;
}

function closeImageModal(){
    const imageModal = document.querySelector('#imageModal');
    imageModal.style.display = 'none';
}