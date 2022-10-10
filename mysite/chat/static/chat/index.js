let url = `ws://${window.location.host}/ws/chat/`;
const chatSocket = new WebSocket(url);

chatSocket.onmessage = function(e) {
    let data = JSON.parse(e.data);
    let messages = document.getElementById("messages");
    let userId = sessionStorage.getItem("user_id");
    
    if (data.type === "chat") {
        if (data.user_id == userId) {
            user = "me"
        } else {
            user = "nekto"
        }

        messages.insertAdjacentHTML("beforeend", `<div><p>${user}: ${data.message} <small>${data.time}</small></p></div>`)
    } else if (data.type === "user_id") {
        sessionStorage.setItem("user_id", data.message);
    } else if (data.type === "start") {
        messages.insertAdjacentHTML("beforeend", `<div><p>--- Собеседник найден ---</p></div>`)
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
