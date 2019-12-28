# ======================================================================================================================
from os import path
import sys
import subprocess

from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import QSizePolicy, QHBoxLayout, QWidget, QListWidget, QApplication, QListWidgetItem
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtCore import QUrl

# ======================================================================================================================


class MyPage(QWebEnginePage):
    def javaScriptConsoleMessage(self, QWebEnginePage_JavaScriptConsoleMessageLevel, p_str, p_int, p_str_1):
        print(f"JAVA SCRIPT CONSOLE MESSAGE: |Linha: {p_int}|Arquivo: {p_str_1}|Output: {p_str}|")


class MyWindow(QWidget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setWindowTitle("NordVPN GUI for CLI")
        self.setWindowIcon(QIcon("./icons/nordvpn.png"))

        self.listWidget = None
        self.webview = None
        self.page = MyPage()
        self.channel = None
        self.AbsTrans = None

        self.setupUi()

    def setupUi(self):
        # --------------------------------------------------------------------------------------------------------------
        vbox = QHBoxLayout()
        self.setLayout(vbox)

        # --------------------------------------------------------------------------------------------------------------
        # Server's List:
        self.listWidget = QListWidget()
        sp1 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sp1.setHorizontalStretch(1)
        self.listWidget.setSizePolicy(sp1)

        self.listWidget.itemClicked.connect(self.serverClicked)
        self.listWidget.itemDoubleClicked.connect(self.serverDoubleClicked)
        vbox.addWidget(self.listWidget,)

        # --------------------------------------------------------------------------------------------------------------
        # WebView:
        self.webview = QWebEngineView()
        sp2 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sp2.setHorizontalStretch(4)
        self.webview.setSizePolicy(sp2)

        self.webview.loadFinished.connect(self.onLoadFinished)
        self.webview.setPage(self.page)

        self.channel = QWebChannel()
        self.channel.registerObject("MyPage", self.page)
        self.page.setWebChannel(self.channel)

        file = path.join(path.dirname(path.realpath(__file__)), "main.html",)
        self.webview.setUrl(QUrl.fromLocalFile(file))

        vbox.addWidget(self.webview,)

        # --------------------------------------------------------------------------------------------------------------

    def onLoadFinished(self, ok):
        if ok:
            self.addServers()

    def serverClicked(self, widget):
        print(widget.text(), self.listWidget.currentItem())
        # TODO: Zoom to position

    def serverDoubleClicked(self, widget):
        print(widget.text(), self.listWidget.currentItem())
        try:
            result = subprocess.check_output(["nordvpn", "connect", widget.text()])
            print(result.decode())
            # TODO: If sucess --> call JS and change: HTML button to "Disconnect" and text...
        except subprocess.SubprocessError as err:
            print("CONNECTION ERROR", err)

    def addServers(self):
        import json

        try:
            result              = subprocess.check_output(["nordvpn","countries"]).decode("utf-8")
            server_countries    = [country.lower().replace("\r", "").replace("-", "").replace("_", " ").strip() for country in result.split(',')]

            with open("countries.json", 'r') as json_file:
                all_countries = json.load(json_file)

                for country in all_countries:
                    country_name = country['name'].lower().replace("_", " ").strip()

                    if country_name in server_countries:
                        location = country["latlng"]

                        server = country_name.title()

                        item = QListWidgetItem()
                        item.setText(server)
                        item.setIcon(QIcon(f'./icons/{country_name.replace(" ","-")}.png'))

                        font = QFont()
                        font.setPointSize(14)
                        item.setFont(font)

                        self.listWidget.addItem(item)
                        self.page.runJavaScript(f'L.marker([{location[0]},{location[1]}])'
                                                f'.addTo(map)'
                                                f'.bindPopup("{server}")')

                # TODO: Should we "L.geoJSON(geojsonFeature).addTo(map);" ? (inside the main.js)
                # TODO: There is no "North Macedonia" on countries list, but we have a server there...

        except subprocess.SubprocessError as e:
            print("ERROR", e)
            sys.exit("Adding Servers...")


# ======================================================================================================================


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MyWindow()
    w.showMaximized()
    sys.exit(app.exec_())


# ======================================================================================================================
"""
https://stackoverflow.com/questions/56351399/creating-a-open-street-maps-view
https://gist.github.com/nilsnolde/4dd879a93ae18837aa95f17e1fc4836a

https://gist.github.com/erdem/8c7d26765831d0f9a8c62f02782ae00d                  <-- LIST
<div>Icons made by <a href="https://www.flaticon.com/authors/freepik" title="Freepik">Freepik</a> from <a href="https://www.flaticon.com/" title="Flaticon">www.flaticon.com</a></div>
"""


"""
# @QtCore.pyqtSlot(float, float,)
# def onMapMove(self, lat, lng):
#     print(lat, lng)

# --------------------------------------------------------------------------------------------------------------
# Button:

# button = QtWidgets.QPushButton("Go to Paris")
# panToParis = functools.partial(self.addMarker, 2.3272, 48.8620)
# button.clicked.connect(panToParis)
# vbox.addWidget(button)
"""