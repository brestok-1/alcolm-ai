const sendButton = document.getElementById('sendButton')
const textInput = document.getElementById('textInput')

function createNewMessage(text, type) {
    const message = document.createElement('div')
    message.className = 'message'
    let content = document.createElement('div')
    if (type === 'bot') {
        content.className = 'bot_message mt-4 py-3 px-4 rounded-4 w-75 ms-3'
    } else {
        content.className = 'user_message mt-4 py-3 px-4 rounded-4 w-75 me-3'
    }
    content.innerText = text
    message.appendChild(content)
    chatBody.appendChild(message)
}

function sendMessageToServer() {
    const userQuery = textInput.value;
    if (userQuery.length === 0) {
        return
    }
    createNewMessage(userQuery, 'user')
    socket.send(JSON.stringify({'query': userQuery}));
    textInput.value = ''
    isFirstWord = false
    chatBody.scrollTop = chatBody.scrollHeight;
}

function generateUUID() {
    const arr = new Uint8Array(16);
    window.crypto.getRandomValues(arr);

    arr[6] = (arr[6] & 0x0f) | 0x40;
    arr[8] = (arr[8] & 0x3f) | 0x80;

    return ([...arr].map((b, i) =>
        (i === 4 || i === 6 || i === 8 || i === 10 ? "-" : "") + b.toString(16).padStart(2, "0")
    ).join(""));
}

textInput.addEventListener("keydown", function (event) {
    if (event.key === "Enter") {
        sendMessageToServer();
    }
});

sendButton.addEventListener("click", sendMessageToServer);