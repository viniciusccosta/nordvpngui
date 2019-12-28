var map;

function initialize(){
    map = L.map('map').setView([0, 0], 3);
    map.setMaxBounds([[85, -174], [-59, 175]]);
    L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {maxZoom: 6, minZoom: 3, noWrap: true}).addTo(map);

    new QWebChannel(qt.webChannelTransport, function (channel) {
        window.MyPage = channel.objects.MyPage;
    });

}

function quickConnect(){
    console.log("QUICK CONNECT");
    console.log( document.getElementById("grand2") );
    // TODO: Call Python and try a "Quick Connect"
    // TODO: If sucess --> Change text and change BTN action.
}
