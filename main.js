var map;

function initialize(){
    map = L.map('map').setView([0, 0], 3);
    map.setMaxBounds([[85, -174], [-59, 175]]);
    L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {maxZoom: 6, minZoom: 3, noWrap: true}).addTo(map);

    new QWebChannel(qt.webChannelTransport, function (channel) {
        window.MyPage = channel.objects.MyPage;
    });

    // # TODO: Read current status on Python and change text and buttons if necessary

}

function markerClicked(event, server){
    var btn = document.getElementById("grand2");                    // TODO: CHANGE THIS ID
    var txt = document.getElementById("grand1");                    // TODO: CHANGE THIS ID

    MyPage.connectNordVPN(server, function(result){
        if (result === true){
            console.log("CONNECTED");

            btn.value = "d";
            btn.textContent = "Disconnect";
            btn.style.backgroundColor = "red";

            // TODO: Change text appropriately
            txt.innerHTML = "<b> <font color=\"#00ff00\" face=\"arial\">&bull; Connected</font> <br> </b>"
        }
    });
}

function btnPressed(){
    var btn = document.getElementById("grand2");                    // TODO: CHANGE THIS ID
    var txt = document.getElementById("grand1");                    // TODO: CHANGE THIS ID

    if (btn.value === "qc"){
        console.log("QUICK CONNECT");

        MyPage.quickConnectNordVPN(function(result){
            if (result === true){
                console.log("CONNECTED");

                btn.value = "d";
                btn.textContent = "Disconnect";
                btn.style.backgroundColor = "red";

                // TODO: Change text appropriately
                txt.innerHTML = "<b> <font color=\"#00ff00\" face=\"arial\">&bull; Connected</font> <br> </b>"
            }
        });
    }
    else if(btn.value === "d"){
        console.log("DISCONNECT");

        MyPage.disconnectNordVPN(function(result){
            if (result === true){
                console.log("DISCONNECTED");

                btn.value = "qc";
                btn.textContent = "Quick Connect";
                btn.style.backgroundColor = "#3075bb";

                // TODO: Change text appropriately
                txt.innerHTML = "<b> <font color=\"#ff0000\" face=\"arial\">&bull; You are not connected</font> <br> </b> <font color=\"#000000\" face=\"arial\">Pick a country or use quick connect</font>"
            }
        });
    }
}
