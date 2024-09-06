import flet as ft
import requests
import ast
import threading
import json
import os


# Annoyingly, when closing the program, there is no "niceway" to avoid the closing console error


def mapstuff(page: ft.page):
    items = {"Earth": [1, -2],
             "moon": [-5, -5],
             "sun": [9, 7]}

    mapdims = (800, 300)

    points = []
    for idxItem, idxValue in items.items():
        rightval = mapdims[0] / 2 * (1 + idxValue[0] / 10)
        heightval = mapdims[1] / 2 * (1 + idxValue[1] / 10)
        print(rightval, idxValue[0])
        circle = ft.IconButton(icon=ft.icons.CIRCLE, right=rightval, height=heightval)
        points.append(circle)

    st = ft.Stack(points, width=mapdims[0], height=mapdims[1])
    page.add(st)


class ServerQuery:
    def __init__(self, host="localhost", port=8000, url=""):
        self.returntext = ""
        if url == "":
            self.address = "http://" + host + ":" + str(port)
        else:
            self.address = url

    # All get methods first
    def getfullheirarchy(self, path="/controller"):
        try:
            req = requests.get(self.address + path,
                               {"method": "getfullheirarchy", "avaliable": "True"},
                               allow_redirects=False,
                               timeout=5)
        except:
            raise ConnectionError("This error occurs when the server cannot be connected to\n"
                                  "this could be because the server is down or that you do not have \n"
                                  "a steady internet connection.")
        else:
            print(req.status_code)
            self.returntext = None
            if req.ok:
                print(req.text)
                returntext = req.text
                self.returntext = returntext

    def getallforsys(self, path="/controller"):
        try:
            req = requests.get(self.address + path,
                               {"method": "getfullheirarchy",
                                "returntype": "everything",
                                "highestname": "templateStation"},
                               allow_redirects=False,
                               timeout=5)
        except requests.exceptions.ConnectionError:
            raise ConnectionError("This error occurs when the server cannot be connected to,\n"
                                  "the server is down or if do not have a steady internet connection.")
        else:
            print(req.status_code)
            if req.ok:
                self.returntext = req.json()
                print(req.json())

    # Then post, for sending data to the server
    """
    def checkheirisuptodate(self, curheir: str, path="/controller"):
        req = requests.post(self.address + path,
                            params={"method": "checkheirisuptodate",
                                    "highestname": "templateStation"},
                            json=json.dumps(curheir),
                            allow_redirects=False,
                            timeout=5)

        print(req.status_code)

        if req.ok:
            self.returntext = ast.literal_eval(req.json())
        else:
            raise RuntimeError("Request returned anomolous...")
    """


class SystemTab:
    color = "#ff2354"

    def __init__(self, sqn, bgcolour, sidebarsize=220, scale=100):
        self.sq = sqn
        self.bgcolour = bgcolour
        self.scale = scale
        self.sidebarsize = sidebarsize
        self.sidebarcontents = ft.Container(ft.Text(""))

        syspagename = "cachedsyspage.json"
        try:
            open(syspagename, "r")
        except FileNotFoundError:
            print("No local cache found, downloading from server...")
        else:
            os.remove(syspagename)
            print("Old local system tab cache found, dowloading updated...")
        self.sq.getallforsys()
        self.localheir = self.sq.returntext
        with open(syspagename, "w") as file:
            json.dump(self.localheir, file, indent=6)

        self.treecontrainer = ft.Container(content=ft.Column(),
                                           bgcolor=self.bgcolour,
                                           expand=True,
                                           alignment=ft.Alignment(0.0, -1.0))
        self.treecontrainer.content.controls.append(self.displaytreeitem(self.localheir, offset=0))
        self.dropdowned = {"name": self.localheir["name"], "dropped": False}

    def displayavaliabletree(self, navigating=[]):
        return self.treecontrainer

    def displaylist(self, e):
        print(e.control.content.controls[1])
        pass

    def displaytreeitem(self, dict, offset=0):

        root = dict["name"]

        iconsize = 20 * self.scale / 100
        textsize = 14 * self.scale / 100

        opt1 = ft.Icon(name=ft.icons.ADD_BOX_OUTLINED, color="#000000", size=iconsize)
        """ft.Container(opt1, data="Help me"),
                       ft.Container(ft.TextButton(text=root,
                                                  style=ft.ButtonStyle(),
                                                  tooltip="Drop down for controlled items",
                                                  on_click=self.displaylist))"""

        rowcontents = [ft.Container(ft.Text("", size=offset)),
                       ft.Container(ft.Row(controls=[opt1, ft.Text("Clickme")]), on_click=self.displaylist)]


        baserow = ft.Row(controls=rowcontents,
                         alignment=ft.MainAxisAlignment.START,
                         vertical_alignment=ft.CrossAxisAlignment.CENTER,
                         spacing=0)

        onlinelist = [baserow]
        try:
            online = self.localheir["avaliable"]
        except KeyError:
            pass
        else:
            if online:
                avaliable = "#2dc21f"
            else:
                avaliable = "#7d0610"
            containerpadd = 1
            onlinelist.append(ft.Container(content=ft.Icon(name="CIRCLE_SHARP",
                                                           size=iconsize - containerpadd,
                                                           color=avaliable),
                                           bgcolor="#050c2b", padding=1, margin=0, shape=ft.BoxShape.CIRCLE))

        baseitem = ft.Container(content=ft.Row(controls=onlinelist,
                                               width=self.sidebarsize,
                                               alignment=ft.MainAxisAlignment.START,
                                               vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                               spacing=5)
                                , bgcolor=self.bgcolour, expand=True, alignment=ft.Alignment(0.0, -1.0))

        return baseitem


def window(page: ft.page):
    def event(e):
        print("event", e.data)

        if e.data == "close":
            pass
            """
            page.dialog = confirm_dialog
            confirm_dialog.open = True
            page.update()
            """

    # noinspection PyUnresolvedReferences
    def tab_clicked(e):
        nonlocal tabcolour
        tabcolour = tabcolours[e.control.text]

        replacement = ft.Container(content=ft.Text("Waiting on server reply...",
                                                   width=sidebarsize),
                                   bgcolor=tabcolour,
                                   expand=True)
        page.controls[1].controls[0].content.controls[1] = replacement
        page.update()

        if e.control.text == "System":
            replacement = systemtabobj.displayavaliabletree()
        else:
            replacement = ft.Container(content=ft.Text("System", width=sidebarsize),
                                       bgcolor=tabcolour,
                                       expand=True)

        page.controls[1].controls[0].content.controls[1] = replacement
        page.update()

    def drawhome():
        secondheight = page.window.height - bannerheight
        nonlocal spacing
        page.clean()
        banner = ft.Container(content=ft.Text("", width=page.window.width, height=bannerheight),
                              bgcolor="#ffffff")

        sidebarbuttons = ft.Row([ft.Container(ft.TextButton("System", on_click=tab_clicked, style=buttonstyleours),
                                              bgcolor=tabcolours["System"],
                                              border_radius=ft.border_radius.vertical(top=5), expand=True),
                                 ft.Container(ft.TextButton("Schedule", on_click=tab_clicked, style=buttonstyleours),
                                              bgcolor=tabcolours["Schedule"],
                                              border_radius=ft.border_radius.vertical(top=5), expand=True),
                                 ft.Container(ft.TextButton("Observed", on_click=tab_clicked, style=buttonstyleours),
                                              bgcolor=tabcolours["Observed"],
                                              border_radius=ft.border_radius.vertical(top=5), expand=True)],
                                spacing=spacing,
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                width=sidebarsize
                                )

        sidebar = ft.Container(
            ft.Column([
                sidebarbuttons,
                ft.Container(content=ft.Text("System", width=sidebarsize), bgcolor=tabcolour, expand=True)
            ],
                expand=1,
                height=secondheight,
                alignment=ft.MainAxisAlignment.START,
                spacing=0
            ))

        mainwindow = ft.Container(content=ft.Text(""),
                                  bgcolor="#3300ff",
                                  height=secondheight,
                                  expand=True)

        rowbellowbanner = ft.Row([sidebar, mainwindow],
                                 width=page.window.width,
                                 vertical_alignment=ft.CrossAxisAlignment.START,
                                 expand=True, spacing=spacing)
        page.add(banner, rowbellowbanner)

    def redrawtofit(e):
        # print("Redraw graphics to fit screen")
        # print("New page size:", page.window.width, page.window.height)
        if currentpage == "home":
            drawhome()

    # Themes
    tabcolours = {"System": "#991020",
                  "Schedule": "#102099",
                  "Observed": "#109920"}

    buttonstyleours = ft.ButtonStyle(color="#000000",
                                     padding=5,
                                     shape=ft.RoundedRectangleBorder())

    page.add(ft.Container(content=ft.Text("Loading..."), expand=True))

    # Layout
    sidebarsize = 220
    bannerheight = 75
    spacing = 2

    # variable setup
    currentpage = "home"
    tabcolour = tabcolours["System"]
    """ there should be a number of pages associated with each tab, each of which is populated
     to present the content the tab is currently pointing to. 
    e.g the system tab might be asking the user for user details to create a new user. HEnce the main body page 
    should have an object which can be activiated in the main window
    which collects this information in teh context of a User object and the tab knows how to save it back to the server. 
    """
    """
    tabs = tabs[3]
    pages = pages[1]
    """

    global sq
    systemtabobj = SystemTab(sq, tabcolours["System"], sidebarsize)

    # page setup
    page.window.width = 600
    page.window.height = 400
    page.padding = spacing
    page.spacing = spacing

    page.window.min_width, page.window.max_width = 400, 1920
    page.window.min_height, page.window.max_height = 300, 1080

    page.window.on_event = event
    page.on_resized = redrawtofit
    page.update()


def start():
    global sq
    sq = ServerQuery(host="localhost", port=2000)
    ft.app(target=window)


sq = None
start()
