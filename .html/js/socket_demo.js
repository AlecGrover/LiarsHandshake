const socket = new WebSocket('ws://localhost:80');
let seperator = "::";
let uuid;

function get_cookie(cname) {

    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${cname}`);
    if (parts.length === 2) return parts.pop().split(';').shift().substring(1,);

    // let name = cname + '=';
    // let d_cookie = decodeURIComponent(document.cname);
    // let ca = d_cookie.split(';');
    // for (let ci = 0; ci < ca.length; ci++) {
    //     let c = ca[ci];
    //     while (c.charAt(0) == ' ') {
    //         c = c.substring(1);
    //     }
    //     if (c.indexOf(name) == 0) {
    //         return c.substring(name.length, c.length);
    //     }
    // }
    // return null;
}

socket.addEventListener('open', function(event) {
    socket.send("Connection Established");
    uuid = get_cookie('uuid');
    console.log(uuid);
    if (uuid == null) {
        sendMessage("Get New UUID")
    }
    document.getElementById("UserIDHeader").innerHTML = uuid;
});

socket.addEventListener('close', function(event) {
    socket.send("Connection Closed" + seperator + uuid);
})

socket.addEventListener('message', function(event) {
    if (event.data.match(/Seperator=./)) {
        let message = event.data.split('=');
        if (message.length < 2) return;
        seperator = message[1];
        socket.send("uuid" + seperator + uuid)
        return;
    }

    console.log(event.data);
    let message = event.data.split(seperator);
    switch (message[0]) {
        case ("UUID"):
            document.getElementById("UserIDHeader").innerHTML = message[1];
            uuid = message[1];
            let d = new Date();
            // Sets expiry to one week
            d.setTime(d.getTime() + 604800000);
            document.cookie = "uuid=" + uuid + ";expires=" + d.toUTCString();
            break;
        case ("Player Data"):
            console.log(message[1]);
            break;
    }
});

const contactServer = () => {
    socket.send("Initialize");
}

const sendMessage = (message) => {
    socket.send(message);
}

const searchUsername = () => {
    let username = document.getElementById("UsernameSearchField").value;
    socket.send("Player Search" + seperator + username);
}

const setUsername = () => {
    let username = document.getElementById("UsernameSearchField").value;
    socket.send("Set Username" + seperator + username + seperator + uuid)
}


