const loadingScreen = document.getElementById("loading-screen");
const searchButton = document.getElementById("search");
const stopButton = document.getElementById("stop");
const form = document.getElementById("form");
const chatWindow = document.getElementById("chat");
const chatMessages = document.getElementById("messages");
const chatInput = document.querySelector(".chat-input input");
const statusMessage = document.getElementById("status");
const url = `ws://${window.location.host}/ws/chat/`;
var unreadMessageCounter = 0;

if (localStorage.getItem("chatting") && localStorage.getItem("group_name")) {
    startChat();
}
searchButton.addEventListener("click", startChat);

function handleMessage(e) {
    let data = JSON.parse(e.data);
    let userId = localStorage.getItem("user_id");
    
    if (data.type === "chat") {
        // Define username, based on the user id given
        if (data.user_id == userId) {
            let user = "Я";
            var message = `
                <article class="msg-container msg-self">
                <div class="msg-box">
                    <div class="flr">
                        <div class="messages">
                            <p class="msg">
                                ${data.message}
                            </p>
                        </div>
                        <span class="timestamp"><span class="username">${user}</span>&bull;<span class="posttime">${data.time}</span></span>
                    </div>
                </div>
            </article>
            `
        } else {
            let user = "Анон";
            var message = `
                <article class="msg-container msg-remote">
                <div class="msg-box">
                    <div class="flr">
                        <div class="messages">
                            <p class="msg">
                                ${data.message}
                            </p>
                        </div>
                        <span class="timestamp"><span class="username">${user}</span>&bull;<span class="posttime">${data.time}</span></span>
                    </div>
                </div>
            </article>
            `
        }

        chatMessages.insertAdjacentHTML("beforeend", message);
        // Notify user if he has unread messages with tab title
        if (document.visibilityState === "hidden") {
            unreadMessageCounter += 1;
            let unreadMessages = unreadMessageCounter;            
            if (unreadMessageCounter > 9) {
                unreadMessages = "9+";
            }
            document.title = `${unreadMessages} новых сообщений`
        } else {
            focusOnLastMessage();
        }
    } else if (data.type === "user_data") {
        localStorage.setItem("user_id", data.user_id);
        localStorage.setItem("group_name", data.group_name);
    } else if (data.type === "start") {
        // If backend is ready
        toggleLoadingScreen();
        toggleChatElements();
        focusOnLastMessage();
    } else if (data.type === "typing") {
        let status = data.message;
        if (status) {
            statusMessage.innerText = "Печатает...";
            setVisibility(statusMessage, "block");
        } else {
            statusMessage.innerText = "";
            setVisibility(statusMessage, "none");
        }
    }
}

function setVisibility(selector, visibility) {
    selector.style.display = visibility
}

function toggleChatElements() {
    stopButton.style.display = (stopButton.style.display == "none") ? "block" : "none";
    chatWindow.style.display = (chatWindow.style.display == "none") ? "block" : "none";
}

function toggleLoadingScreen() {
    loadingScreen.style.display = (loadingScreen.style.display == "none") ? "block" : "none";
}

function focusOnLastMessage() {
    let messageElement = chatMessages.lastElementChild;
    const y = messageElement.offsetTop;
    chatMessages.scrollTo({
        top: y,
        behavior: 'smooth'
    });
}

var timeout;

function startChat() {
    setVisibility(searchButton, "none");
    toggleLoadingScreen();
    var chatSocket = new WebSocket(url);
    chatSocket.onmessage = function(e) {handleMessage(e)};
    
    // Handle chat elements
    const formSubmitListener = (e) => {
        e.preventDefault();
        let message = e.target.message.value;
        
        if (message != "") {
            chatSocket.send(JSON.stringify({
                "type": "message",
                "message": message
            }));
            form.reset();
            timeoutFunction();
        }
    }

    form.addEventListener("submit", formSubmitListener);
    localStorage.setItem("chatting", true);

    stopButton.addEventListener("click", (e) => {
        chatSocket.close(3000, "User closed chat");
    });

    // Handle typing status
    function timeoutFunction() {
        chatSocket.send(JSON.stringify({
            "type": "typing",
            "message": false
        }));
    }
    
    const alphaRegex = new RegExp("^[A-Za-z0-9 ]");
    chatInput.addEventListener('keyup', function(e) {
        keyPressed = String.fromCharCode(e.which);

        // React only on typing keys
        if (alphaRegex.test(keyPressed)) {
            chatSocket.send(JSON.stringify({
                "type": "typing",
                "message": true
            }));
           clearTimeout(timeout);
           timeout = setTimeout(timeoutFunction, 2000);
        }
    })
      
    // Handle socket closing
    chatSocket.onclose = function(e) {
        setVisibility(searchButton, "block");
        setVisibility(stopButton, "none");
        setVisibility(chatWindow, "none");
        setVisibility(loadingScreen, "none");
        setVisibility(statusMessage, "none");
        localStorage.clear();
        // Update form event listener 
        // so new WebSocket object will be updated as well 
        form.removeEventListener("submit", formSubmitListener);
        // Clear chat from previous session
        chatMessages.textContent = "";
    }
}

// Make submit button glow when typing
chatInput.addEventListener("keyup", (e) => {
    if (chatInput.value == "") {
        chatInput.removeAttribute("good");
    } else {
        chatInput.setAttribute("good", "");
    }
});

form.addEventListener("submit", (e) => {
    if (chatInput.value == "") {
        chatInput.removeAttribute("good");
    }
});

// Display unread message counter in tab title
document.addEventListener("visibilitychange", () => {
    if (document.visibilityState === "visible") {
        unreadMessageCounter = 0;
        document.title = "Текстовый чат"
    }
})
  