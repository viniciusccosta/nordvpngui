"""
Credits to:
    https://gist.github.com/erdem/8c7d26765831d0f9a8c62f02782ae00d
    <div>Icons made by <a href="https://www.flaticon.com/authors/freepik" title="Freepik">Freepik</a> from <a href="https://www.flaticon.com/" title="Flaticon">www.flaticon.com</a></div>
"""

# ======================================================================================================================
from os import path
import sys
import subprocess

from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import QSizePolicy, QHBoxLayout, QWidget, QListWidget, QApplication, QListWidgetItem
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtCore import QUrl, pyqtSlot

# ======================================================================================================================


class MyPage(QWebEnginePage):
    def javaScriptConsoleMessage(self, QWebEnginePage_JavaScriptConsoleMessageLevel, p_str, p_int, p_str_1):
        print(f"JAVA SCRIPT CONSOLE MESSAGE: |Linha: {p_int}|Arquivo: {p_str_1} |Output: {p_str}|")

    @pyqtSlot(name="quickConnectNordVPN", result=bool)
    def quickConnectNordVPN(self):
        print("Connecting (Quick Connect)...")
        try:
            output = subprocess.check_output(["nordvpn", "connect"])
            if output:
                print("\t", output.decode())
                return True
            else:
                return False
        except subprocess.SubprocessError as err:
            print("ERROR", err)
            return False

    @pyqtSlot(name="disconnectNordVPN", result=bool)
    def disconnectNordVPN(self):
        print("Disconnecting...")
        try:
            output = subprocess.check_output(["nordvpn", "disconnect"])
            if output:
                print("\t", output.decode())
                return True
            else:
                return False
        except subprocess.SubprocessError as err:
            print("ERROR", err)
            return False

    @pyqtSlot(str, name="connectNordVPN", result=bool)
    def connectNordVPN(self, server):
        print(f"Connecting to {server}...")
        try:
            output = subprocess.check_output(["nordvpn", "connect", server.replace(" ","_")])
            if output:
                print("\t", output.decode())
                return True
            else:
                return False
        except subprocess.SubprocessError as err:
            print("ERROR", err)
            return False


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

        # TODO: Add ToolBar with "Servers" and "Settings" options

        # --------------------------------------------------------------------------------------------------------------
        # Server's List:
        self.listWidget = QListWidget()
        sp1 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sp1.setHorizontalStretch(1)
        self.listWidget.setSizePolicy(sp1)

        self.listWidget.itemClicked.connect(self.serverClicked)
        self.listWidget.itemDoubleClicked.connect(self.serverDoubleClicked)
        vbox.addWidget(self.listWidget,)

        # TODO: Change to TreeView
        # TODO: add special servers (P2P, etc.)

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
        # TODO: Zoom to marker's position ?

    def serverDoubleClicked(self, widget):
        # TODO: "JS --> markerClicked(widget.text())". Let the JS do the "hard work"
        print(widget.text(), self.listWidget.currentItem())
        # try:
        #     result = subprocess.check_output(["nordvpn", "connect", widget.text()])
        #     print(result.decode())
        # except subprocess.SubprocessError as err:
        #     print("CONNECTION ERROR", err)

    def addServers(self):
        import json

        try:
            result              = subprocess.check_output(["nordvpn", "countries"]).decode("utf-8")
            server_countries    = [country.lower().replace("\r", "").replace("-", "").replace("_", " ").strip() for country in result.split(',')]

            with open("countries.json", 'r') as json_file:
                all_countries = json.load(json_file)

                for country in sorted(all_countries, key=lambda x: x['name']):
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
                        self.page.runJavaScript(
                            f'L.marker([{location[0]},{location[1]}])'
                            f'.addTo(map)'
                            f'.bindTooltip("{server}")'
                            f'.on("click", function(e) {{markerClicked(e,"{server}")}});'
                        )

        except subprocess.SubprocessError as e:
            print("ERROR", e)
            sys.exit("Subprocess Error on Adding Servers...")
        except Exception as e:
            print("ERROR", e)
            sys.exit("Adding Servers Fails")


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

https://wiki.python.org/moin/PyQt/QML%20callback%20function
https://myprogrammingnotes.com/communication-c-javascript-qt-webengine.html
"""