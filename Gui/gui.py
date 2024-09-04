import flet as ft
import requests
import ast
import threading
# Annoyingly, when closing the program, there is no "niceway" to avoid the closing console error


def mapstuff(page: ft.page):
    items = {"Earth": [1, -2],
             "moon": [-5, -5],
             "sun": [9, 7]}

    position = [0,0]
    mapDims = (800, 300)

    points = []
    for idxItem, idxValue in items.items():
        RightVal = mapDims[0]/2*(1+idxValue[0]/10)
        HeightVal = mapDims[1]/2*(1+idxValue[1]/10)
        print(RightVal, idxValue[0])
        circle = ft.IconButton(icon=ft.icons.CIRCLE, right=RightVal, height=HeightVal)
        points.append(circle)

    st = ft.Stack(points, width=mapDims[0], height=mapDims[1])
    page.add(st)

class serverquery:
    def __init__(self, host="localhost", port=8000, url=""):
        if url == "":
            self.address = "http://"+host+":"+str(port)
        else:
            self.address = url



    def getfullheirarchy(self, returntext=None, path="/controller"):
        req = requests.get(self.address+path,
                           {"method": "getfullheirarchy", "avaliable": "True"},
                           allow_redirects=False,
                           timeout=5)
        print(req.status_code)
        self.returntext = None
        if req.ok:
            print(req.text)
            returntext = req.text
            self.returntext = returntext


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

    def tab_clicked(e):
        nonlocal tabcolour
        tabcolour = tabcolours[e.control.text]
        returncontent = None

        global sq
        threadret = threading.Thread(target=sq.getfullheirarchy, args=[])
        threadret.start()
        replacement = ft.Container(content=ft.Text("Waiting on server reply...",
                                                   width=sidebarsize),
                                   bgcolor=tabcolour,
                                   expand=True)
        page.controls[1].controls[0].content.controls[1] = replacement
        page.update()
        threadret.join()
        respobj = ast.literal_eval(sq.returntext)
        column = ft.Column()
        replacement = ft.Container(content=ft.Text(respobj[0],
                                                   width=sidebarsize),
                                   bgcolor=tabcolour,
                                   expand=True)

        page.controls[1].controls[0].content.controls[1] = replacement
        page.update()

    def drawHome():
        secondheight = page.window.height-bannerheight
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

        second = ft.Row([sidebar, mainwindow],
                        width=page.window.width,
                        vertical_alignment=ft.CrossAxisAlignment.START,
                        expand=True, spacing=spacing)
        page.add(banner, second)

    def redrawToFit(e):
        #print("Redraw graphics to fit screen")
        #print("New page size:", page.window.width, page.window.height)
        if currentpage == "home":
            drawHome()

    # Themes
    tabcolours = {"System": "#991020",
                  "Schedule": "#102099",
                  "Observed": "#109920"}

    buttonstyleours = ft.ButtonStyle(color="#000000",
                                     padding=5,
                                     shape=ft.RoundedRectangleBorder())

    # Layout
    bordersize = 46
    sidebarsize = 220
    bannerheight = 75
    spacing = 2

    # variable setup
    currentpage = "home"
    hometab = "sys"
    tabcolour = tabcolours["System"]

    # page setup
    page.window.width = 600
    page.window.height = 400
    page.padding = spacing
    page.spacing = spacing

    page.window.min_width, page.window.max_width = 400, 1920
    page.window.min_height, page.window.max_height = 300, 1080

    page.window.on_event = event
    page.on_resized = redrawToFit
    page.update()



def start():
    global sq
    sq = serverquery(host="localhost", port=2000)
    ft.app(target=window)


sq = None
start()
