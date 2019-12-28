var map;
var loading = false;

function initialize(){
    map = L.map('map').setView([0, 0], 3);
    map.setMaxBounds([[85, -174], [-59, 175]]);
    L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {maxZoom: 6, minZoom: 3, noWrap: true}).addTo(map);

    new QWebChannel(qt.webChannelTransport,
        function (channel) {
            // --------------------------------------------------------------
            // Global:
            window.MyPage = channel.objects.MyPage;

            // --------------------------------------------------------------
            // Do it:
            MyPage.getCurrentStatus(
                function(result){
                    console.log("Current Status (connected): " + result);
                    if(result !== null){ updateHTML(result); }                  // TODO: Get server's info and update HTML
                }
            );

            // --------------------------------------------------------------
            // Listeners:
            MyPage.signalConnectServer.connect(
                function(server){
                    if (server !== null && loading === false){ askPythonConnect(false, server); }
                    else{ console.log("!!! WAIT !!! "); }
                }
            );

            MyPage.signalConnectionChanged.connect(
                function(connected){
                    if (connected !== null){ updateHTML(connected); }
                }
            );

            // --------------------------------------------------------------
        }
    );

}

function markerClicked(event, server){
    if (loading === false){ askPythonConnect(false, server); }
    else { console.log("!!! WAIT !!! "); }
}

function btnPressed(){
    var btn = document.getElementById("btnId");

    if (loading === false){
        btn.disable = true;

        if (btn.value === "qc"){ askPythonConnect(true); }
        else if(btn.value === "d"){ askPythonDisconnect(); }
    }
    else { console.log("!!! WAIT !!! "); }
}

function askPythonConnect(quickly, server = null){
    console.log("ASK PYTHON TO CONNECT " + server);
    loading = true;

    if (quickly === true){
        MyPage.quickConnectNordVPN(
            function(result){
                loading = false;
                if (result === true){ updateHTML(true); }
            }
        );
    }else{
        MyPage.connectNordVPN(server,
            function(result){
                loading = false;
                if (result === true){ updateHTML(true); }
            }
        );
    }
}

function askPythonDisconnect(){
    console.log("ASK PYTHON TO DISCONNECT");
    loading = true;

    MyPage.disconnectNordVPN(
        function(result){
            loading = false;
            if (result === true){
                updateHTML(false);
            }
        }
    );
}

function updateHTML(connected){
    var btn = document.getElementById("btnId");
    var txt = document.getElementById("divTxtId");

    if (connected === true){
        btn.disable = false;
        btn.value = "d";
        btn.textContent = "Disconnect";
        btn.style.backgroundColor = "red";

        // TODO: Change text appropriately
        txt.innerHTML = "<b> <font color=\"#00ff00\" face=\"arial\">&bull; Connected</font> <br> </b>"
    }else{
        btn.disable = false;
        btn.value = "qc";
        btn.textContent = "Quick Connect";
        btn.style.backgroundColor = "#3075bb";

        // TODO: Change text appropriately
        txt.innerHTML = "<b> <font color=\"#ff0000\" face=\"arial\">&bull; You are not connected</font> <br> </b> <font color=\"#000000\" face=\"arial\">Pick a country or use quick connect</font>"
    }
}

/*
    TODO: PERFOMANCE ISSUE
        User has 3 options:
            1) Quick Connect / Disconnect button
            2) Click on Marker
            3) Select country on ListView
            ---------------------------------------------
            When javascript is waiting for the result of python all the webview get stucked,
            which is a good thing, because, user won't be able to request a lot of connections,
            but python still runs, which means that user can click multiple times on ListView,
            and all of that signals them will be emitted and javascript will execute them one by one, after each other.
            ---------------------------------------------
            Possible Solution:
                1) add "loading" variable on python and only emit a signal if is false
                2) show "loader" on HTML to a visual feedback to user
            ---------------------------------------------
            Obs:
                Javascript's "loading" variable is not so useful as I expected, see why:
                ----------
                1) loading is false
                2) set loading to true
                3) request python to do something
                4) wait for the result
                5) set loading to true
                ----------
                Since javascript will be stucked on step 4 this variable is not helping at all.
            ---------------------------------------------
            Obs:
                Python's "loading" variable not working either, for exactly same reason of Javascript's variable.
            ---------------------------------------------_
*/