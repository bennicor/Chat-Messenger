let url = `ws://${window.location.host}/ws/chat/`;
const chatSocket = new WebSocket(url);

chatSocket.onmessage = function(e) {
    let data = JSON.parse(e.data);
    let messages = document.getElementById("messages");
    
    if (data.type === "chat") {
        messages.insertAdjacentHTML("beforeend", `<div><p>${data.user}: ${data.message}</p></div>`)
    } else if (data.type == "close") {
        messages.insertAdjacentHTML("beforeend", `<div><p>---${data.message}---</p></div>`)
    }
};

let form = document.getElementById("form");
form.addEventListener("submit", (e) => {
    e.preventDefault();
    let message = e.target.message.value;
    
    chatSocket.send(JSON.stringify({
        "message": message
    }));
    form.reset();
});