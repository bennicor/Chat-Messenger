let url = `ws://${window.location.host}/ws/chat/`;
const chatSocket = new WebSocket(url);

chatSocket.onmessage = function(e) {
    let data = JSON.parse(e.data);
    let messages = document.getElementById("messages");
    console.log(data.message)
    
    if (data.type === "chat") {
        messages.insertAdjacentHTML("beforeend", `<div><p>abob ${data.message}</p></div>`)
    } else if (data.type === "user_id") {
        console.log("USER ID GOTTEn " + data.message);
        sessionStorage.setItem("user_id", data.message);
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