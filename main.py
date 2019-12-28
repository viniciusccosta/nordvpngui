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
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtCore import QUrl, pyqtSlot, pyqtSignal


# ======================================================================================================================


class MyPage(QWebEnginePage):
    signalConnectServer = pyqtSignal(str)
    signalConnectionChanged = pyqtSignal(bool)

    # ------------------------------------------------------------------------------------------------------------------
    def __init__(self):
        super().__init__()
        self.m_loading = False

    def javaScriptConsoleMessage(self, QWebEnginePage_JavaScriptConsoleMessageLevel, p_str, p_int, p_str_1):
        print(f"JAVA SCRIPT CONSOLE MESSAGE: |Linha: {p_int}|Arquivo: {p_str_1} |Output: {p_str}|")

    # ------------------------------------------------------------------------------------------------------------------
    # Auxiliary:
    def getConnectionInfo(self):
        try:
            output = subprocess.check_output(["nordvpn", "status"], timeout=60)
            print("\t", output.decode("utf-8"))
            return output.decode("utf-8")
        except subprocess.SubprocessError as err:
            print("ERROR", err)
            return "ERROR"

    # ------------------------------------------------------------------------------------------------------------------
    # Signal Emitters:
    def askJStoConnect(self, server):
        if not self.m_loading:
            print("EMIT SIGNAL TO JS", server.replace(" ", "_"))
            self.signalConnectServer.emit(server.replace(" ", "_"))
        else:
            print("!!! WAIT !!!")

    # ------------------------------------------------------------------------------------------------------------------
    # Slots:
    @pyqtSlot(name="quickConnectNordVPN", result=bool)
    def quickConnectNordVPN(self):
        print("Connecting (Quick Connect)...")
        self.m_loading = True

        try:
            output = subprocess.check_output(["nordvpn", "connect"], timeout=60)

            if output:
                print("\t", output.decode())
                updateSystemTray(self.getConnectionInfo())
                self.m_loading = False
                return True
            else:
                return False

        except subprocess.SubprocessError as err:
            print("ERROR", err)
            self.m_loading = False
            return False

    @pyqtSlot(name="disconnectNordVPN", result=bool)
    def disconnectNordVPN(self):
        print("Disconnecting...")
        self.m_loading = True

        try:
            output = subprocess.check_output(["nordvpn", "disconnect"], timeout=60)
            self.m_loading = False

            if output:
                print("\t", output.decode())
                updateSystemTray()
                return True
            else:
                return False

        except subprocess.SubprocessError as err:
            print("ERROR", err)
            self.m_loading = False
            return False

    @pyqtSlot(str, name="connectNordVPN", result=bool)
    def connectNordVPN(self, server):
        print(f"Connecting to {server}...")
        self.m_loading = True

        try:
            output = subprocess.check_output(["nordvpn", "connect", server.replace(" ", "_")], timeout=60)

            if output:
                print("\t", output.decode())
                updateSystemTray(self.getConnectionInfo())
                self.m_loading = False
                return True
            else:
                return False

        except subprocess.SubprocessError as err:
            print("ERROR", err)
            self.m_loading = False
            return False

    @pyqtSlot(name="getCurrentStatus", result=bool)
    def getCurrentStatus(self):
        print("Getting status...")
        self.m_loading = True

        try:
            output = self.getConnectionInfo()
            self.m_loading = False
            if "status: connected" in output.lower():
                updateSystemTray(output)
                return True
            else:
                updateSystemTray()
                return False

        except subprocess.SubprocessError as err:
            print("ERROR", err)
            self.m_loading = False
            return False

    # ------------------------------------------------------------------------------------------------------------------


class MyWindow(QWidget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setWindowTitle("NordVPN GUI for CLI")
        self.setWindowIcon(QIcon("./icons/nordvpn.png"))

        self.listWidget = None
        self.webview = None
        self.mypage = MyPage()
        self.channel = None
        self.AbsTrans = None
        self.overlay = None

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
        self.webview.setPage(self.mypage)

        self.channel = QWebChannel()
        self.channel.registerObject("MyPage", self.mypage)
        self.mypage.setWebChannel(self.channel)

        file = path.join(path.dirname(path.realpath(__file__)), "main.html",)
        self.webview.setUrl(QUrl.fromLocalFile(file))

        vbox.addWidget(self.webview,)

        # --------------------------------------------------------------------------------------------------------------

        # TODO: URGENT !!! Add LOADING OVERLAY !!! or at least a MessageBox...

        # --------------------------------------------------------------------------------------------------------------

    def onLoadFinished(self, ok):
        if ok:
            self.addServers()

    def serverDoubleClicked(self, widget):
        if not self.mypage.m_loading:
            self.mypage.askJStoConnect(widget.text())
        else:
            print("!!! WAIT !!!")

    def addServers(self):
        import json

        try:
            result              = subprocess.check_output(["nordvpn", "countries"], timeout=60).decode("utf-8")
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
                        self.mypage.runJavaScript(
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


def openPressed():
    my_window.showMaximized()


def exitPressed():
    sys.exit(0)


def createSystemTray():
    global app
    global trayIcon
    global actions

    # ------------------------------------------------------
    # Application:
    app.setQuitOnLastWindowClosed(False)

    # ------------------------------------------------------
    # Icon:
    trayIcon = QSystemTrayIcon()
    trayIcon.setIcon(QIcon("./icons/nordvpn-gray.png"))
    trayIcon.show()

    # ------------------------------------------------------
    # Menu:
    menu = QMenu()

    # ------------------------------------------------------
    # Mennu Items:
    for dic in actions.values():
        action = dic["action"]
        action.triggered.connect(dic["target"])
        action.setEnabled(True)
        menu.addAction(action)

    # ------------------------------------------------------
    # Add Menu:
    trayIcon.setContextMenu(menu)


def updateSystemTray(tooltip_txt=None):
    if tooltip_txt:
        trayIcon.setIcon(QIcon("./icons/nordvpn.png"))
        trayIcon.setToolTip(tooltip_txt)
    else:
        trayIcon.setIcon(QIcon("./icons/nordvpn-gray.png"))
        trayIcon.setToolTip("Disconnected")


# ======================================================================================================================


trayIcon = None
app = None
my_window = None
actions = {
    "Quick Connect": {
        "action": QAction("Open"),
        "target": openPressed,
    },
    "Disconnect": {
        "action": QAction("Exit"),
        "target": exitPressed,
    },
}


# ======================================================================================================================


if __name__ == "__main__":
    app = QApplication(sys.argv)

    my_window = MyWindow()
    my_window.showMaximized()

    createSystemTray()              # TODO: It should be inside some class...

    sys.exit(app.exec_())


# ======================================================================================================================
"""
https://stackoverflow.com/questions/56351399/creating-a-open-street-maps-view
https://gist.github.com/nilsnolde/4dd879a93ae18837aa95f17e1fc4836a

https://wiki.python.org/moin/PyQt/QML%20callback%20function
https://myprogrammingnotes.com/communication-c-javascript-qt-webengine.html
"""