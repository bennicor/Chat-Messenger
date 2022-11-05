let searchButton = document.getElementById("search");
let stopButton = document.getElementById("stop");
let form = document.getElementById("form");
const url = `ws://${window.location.host}/ws/chat/`;

startChat();
// if (localStorage.getItem("chatting") && localStorage.getItem("group_name")) {
//     startChat();
// }
// searchButton.addEventListener("click", startChat);

function handleMessage(e) {
    let data = JSON.parse(e.data);
    let messages = document.querySelector(".chat-window");
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
                    <img class="user-img" id="user-0" src="//gravatar.com/avatar/56234674574535734573000000000001?d=retro" />
                </div>
            </article>
            `
        } else {
            let user = "Анон";
            var message = `
                <article class="msg-container msg-remote">
                <div class="msg-box">
                    <img class="user-img" id="user-0" src="//gravatar.com/avatar/00034587632094500000000000000000?d=retro" />
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

        messages.insertAdjacentHTML("beforeend", message);
    } else if (data.type === "user_data") {
        localStorage.setItem("user_id", data.user_id);
        localStorage.setItem("group_name", data.group_name);
    } else if (data.type === "start") {
        // If backend is ready
        // Stop loading screen
    }
}

function toggleChatElements() {
    searchButton.style.display = (searchButton.style.display == "none") ? "block" : "none";
    stopButton.style.display = (stopButton.style.display == "none") ? "block" : "none";
    form.style.display = (form.style.display == "none") ? "block" : "none";
}

function startChat() {
    var chatSocket = new WebSocket(url);
    chatSocket.onmessage = function(e) {handleMessage(e)};
    
    const formSubmitListener = (e) => {
        e.preventDefault();
        let message = e.target.message.value;
        
        chatSocket.send(JSON.stringify({
            "message": message
        }));
        form.reset();
    }
    form.addEventListener("submit", formSubmitListener);
    localStorage.setItem("chatting", true);
    // toggleChatElements();

    // stopButton.addEventListener("click", (e) => {
    //     chatSocket.close(3000, "User closed chat");
    // });

    chatSocket.onclose = function(e) {
        toggleChatElements();
        localStorage.clear();
        // Update form event listener 
        // so new WebSocket object will be updated as well 
        form.removeEventListener("submit", formSubmitListener);
    }
}

const chatInput = document.querySelector(".chat-input input");
chatInput.addEventListener("keyup", (e) => {
    if (chatInput.value == "") {
        chatInput.removeAttribute("good");
    } else {
        chatInput.setAttribute("good", "");
    }
});
