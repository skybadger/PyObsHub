import flet as ft
import requests
import ast
import threading
import json
import os


# Annoyingly, when closing the program, there is no "niceway" to avoid the closing console error
def leveltomult(level, rootlevel="Site"):
    value = 0
    if level == "Site":
        value = 1
    elif level == "Station":
        value = 2
    elif level == "Mount":
        value = 3
    elif level == "OTA":
        value = 4
    elif level == "Port":
        value = 5

    rootvalue = 0
    if rootlevel == "Site":
        rootvalue = 1
    elif rootlevel == "Station":
        rootvalue = 2
    elif rootlevel == "Mount":
        rootvalue = 3
    elif rootlevel == "OTA":
        rootvalue = 4
    elif rootlevel == "Port":
        rootvalue = 5

    return value - rootvalue


def colourscale(hexcolour: str, multiplier: int = 100, channel: str = "all"):
    r = hexcolour[1:3]
    g = hexcolour[3:5]
    b = hexcolour[5:7]

    rd = int(r, 16)
    gd = int(g, 16)
    bd = int(b, 16)

    rawmult = multiplier / 100
    if rawmult > 0:
        if channel == "all":
            rd = min(round(rd * rawmult), 255)
            gd = min(round(gd * rawmult), 255)
            bd = min(round(bd * rawmult), 255)
        else:
            if "r" in channel:
                rd = min(round(rd * rawmult), 255)
            elif "g" in channel:
                gd = min(round(gd * rawmult), 255)
            elif "b" in channel:
                bd = min(round(bd * rawmult), 255)
            else:
                raise AttributeError(f"Channel must be a string of ['All', 'r', 'g', 'b'], not {channel}")
    elif rawmult < 0:
        if channel == "all":
            rd = max(round(255 + rd * rawmult), 0)
            gd = max(round(255 + gd * rawmult), 0)
            bd = max(round(255 + bd * rawmult), 0)
        else:
            if "r" in channel:
                rd = max(round(255 + rd * rawmult), 0)
            elif "g" in channel:
                gd = max(round(255 + gd * rawmult), 0)
            elif "b" in channel:
                bd = max(round(255 + bd * rawmult), 0)
            else:
                raise AttributeError(f"Channel must be a string of ['All', 'r', 'g', 'b'], not {channel}")
    else:
        raise AttributeError(f"Passed multiplier cannot be zero! ({multiplier})")

    valuer = str(hex(rd)[2:])
    valueg = str(hex(gd)[2:])
    valueb = str(hex(bd)[2:])

    if len(valuer) == 2:
        pass
    else:
        valuer = "0" + str(valuer)

    if len(valueg) == 2:
        pass
    else:
        valueg = "0" + str(valueg)

    if len(valueb) == 2:
        pass
    else:
        valueb = "0" + str(valueb)

    return "#" + valuer + valueg + valueb


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

    def getallforsys(self, path="/controller", debug=False):
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
            if debug:
                print(req.status_code)
            if req.ok:
                self.returntext = req.json()
                if debug:
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


class TabInheritance:
    nicenames = {"name": "Name",
                 "level": "Level",
                 "lastupdated": "Last updated at",
                 "associateddata": "Associated Data",
                 "avaliable": "Avaliable",
                 "stationtype": "Station type",
                 "hostname": "Network host name",
                 "interfacetype": "Interface type",
                 "altlimits": "Altitude Limits"}

    def __init__(self, sqn, bgcolour, page, sidewindowobj, sidebarsize=220, scale=100, offsetgrowth=10):
        self.sq = sqn
        self.bgcolour = bgcolour
        self.page = page
        self.sidewindowobj = sidewindowobj
        self.sidebarsize = sidebarsize
        self.scale = scale
        self.offsetgrowth = offsetgrowth

        self.lastevent = None
        self.laste = None

        global tabcolours
        self.tabcolours = tabcolours


class SystemTab(TabInheritance):
    def __init__(self, sqn, bgcolour, page, sidewindowobj, sidebarsize=220, scale=100, offsetgrowth=10):
        super().__init__(sqn, bgcolour, page, sidewindowobj, sidebarsize, scale, offsetgrowth)
        self.lastevent = None
        self.laste = None

        self.colour = self.tabcolours["System"]
        self.textsize = 14 * self.scale / 100
        self.buttonstyle = ft.ButtonStyle(color="#ffffff",
                                          bgcolor=colourscale(self.colour, 80),
                                          shape=ft.RoundedRectangleBorder(radius=5),
                                          padding=5)


        # Check to see if te
        syspagename = "cachedsyspage.json"
        cwd = os.getcwd()
        filename = os.path.dirname(cwd) + "/" + syspagename
        print(filename, cwd)
        try:
            open(filename, "r")
        except FileNotFoundError:
            print("No local cache found, downloading from server...")
        else:
            os.remove(filename)
            print("Old local system tab cache found, dowloading updated...")

        # Write dict to file
        self.sq.getallforsys()
        self.localheir = self.sq.returntext
        with open(filename, "w") as file:
            json.dump(self.localheir, file, indent=6)

        self.treecontrainer = ft.Container(content=ft.Column(spacing=0),
                                           bgcolor=self.bgcolour,
                                           expand=True,
                                           alignment=ft.Alignment(0.0, -1.0))
        self.treecontrainer.content.controls.append(self.displaytreeitem(self.localheir, offset=0))

        self.sidewindow = [ft.Text("Template tooltip...")]

    def displayavaliabletree(self):
        return self.treecontrainer

    def displayselecteditem(self):
        return self.sidewindow

    def redrawlastevent(self):
        if self.laste is None:
            self.sidewindow = [ft.Text("placeholder")]
        elif self.lastevent == "displayiteminfomationinmain":
            self.displayiteminfomationinmain(self.laste)
        elif self.lastevent == "diplaylistofheir":
            self.displayiteminfomationinmain(self.laste)
        else:
            raise NotImplementedError("No other events are listed! (Redraw last error)")

    def savebuttonpressed(self, e):
        ## Cannot be used to redraw as such, last e and last event are not set
        revnicenames = dict((v, k) for k, v in self.nicenames.items())


        content = self.sidewindowobj.struct
        displist = content.content.controls[1].controls
        listedname = displist[0].content.controls[1].content.value
        dictobj = self.findinheir(self.localheir, listedname)

        for item in displist:
            key, value = item.content.controls[0].value, item.content.controls[1].content.value
            actualkey = revnicenames[key]
            print(key, value)


    def displayiteminfomationinmain(self, e):
        """
        When a tree button is clicked, display the infomation in a editable format
        :param e: event to be triggered
        :return: None
        """
        self.laste = e
        self.lastevent = "displayiteminfomationinmain"

        branchname = e.control.text
        reducedheir = self.findinheir(self.localheir, branchname)[0]
        displist = []

        # Variable setup
        contpadding = 5
        nametextwidth = len(self.nicenames["hostname"]) * self.textsize / 1.8
        for key, value in reducedheir.items():
            if key in self.nicenames.keys():
                name = self.nicenames[key]
                nametext = ft.Text(name, size=self.textsize, width=nametextwidth)
                maxlength = round(self.page.window.width - (
                        nametextwidth + self.sidebarsize + contpadding * 4 + 30))

                item = ft.Container(content=ft.Row([nametext,
                                                    ft.Container(content=ft.TextField(value,
                                                                                      text_size=self.textsize,
                                                                                      content_padding=contpadding,
                                                                                      dense=True),
                                                                 width=maxlength)
                                                    ]),
                                    padding=contpadding)
                displist.append(item)

        content = ft.Column(controls=[ft.Container(content=ft.Row([ft.TextButton("Save",
                                                                                 icon=ft.icons.SAVE_ROUNDED,
                                                                                 style=self.buttonstyle,
                                                                                 icon_color="#ffffff",
                                                                                 on_click=self.savebuttonpressed),
                                                                   ft.Text("revert"),
                                                                   ft.Text("Close")],
                                                                  height=20 * self.scale / 100),
                                                   bgcolor=colourscale(self.colour, 80),
                                                   padding=contpadding,
                                                   border_radius=5),
                                      ft.Column(controls=displist)]
                            )


        self.sidewindow = content
        self.sidewindowobj.setstruct(self.sidewindow)

        self.page.update()

    def diplaylistofheir(self, e):
        self.laste = e
        self.lastevent = "diplaylistofheir"

        name = e.control.content.controls[1].value
        localheir = self.findinheir(self.localheir, name)[0]
        # Setup
        if "dropped" not in localheir.keys():
            localheir["dropped"] = False
            level = localheir["level"]
            rootlevel = self.localheir["level"]
            offset = leveltomult(level, rootlevel) * self.offsetgrowth
            localheir["offset"] = offset

        # When Expanded
        if not localheir["dropped"]:
            localheir["dropped"] = True
            e.control.content.controls[0].name = ft.icons.INDETERMINATE_CHECK_BOX_OUTLINED
            localtopop = list(self.treecontrainer.content.controls)
            insertidx = 0
            # Find the insert point for the items
            for i, cont in enumerate(localtopop):
                contname = cont.content.controls[0].controls[1].content.controls[1].value
                if contname == name:
                    insertidx = i + 1
                    break

            # Add the controlled objects to the page dropdow
            self.findallcontrolledanddroppeditems(localheir["controlled"],
                                                  localheir["offset"] + self.offsetgrowth,
                                                  insertidx)
        # When collapsed
        else:
            localheir["dropped"] = False
            e.control.content.controls[0].name = ft.icons.ADD_BOX_OUTLINED
            names = self.findnamesofalltoremove(localheir)
            popped = 0
            for name in names:
                localtopop = list(self.treecontrainer.content.controls)
                for i, cont in enumerate(localtopop):
                    contname = cont.content.controls[0].controls[1].content.controls[1].value
                    if name == contname:
                        self.treecontrainer.content.controls.remove(cont)
                        popped += 1
                        break

        self.page.update()

    def findallcontrolledanddroppeditems(self, controlled, offset, insertidx):
        for tempobj in controlled:
            if tempobj["level"] == "Port":
                item = self.displaytreeitem(tempobj, offset=offset + self.offsetgrowth, clickable=False)
            else:
                item = self.displaytreeitem(tempobj, offset=offset + self.offsetgrowth, clickable=True)

            self.treecontrainer.content.controls.insert(insertidx, item)
            insertidx += 1
            if "dropped" in tempobj.keys():
                if tempobj["dropped"] and not tempobj["controlled"]:
                    insertidx += self.findallcontrolledanddroppeditems(tempobj["controlled"],
                                                                       offset + self.offsetgrowth,
                                                                       insertidx)
        return insertidx

    def findinheir(self, obj: dict(), name: str):
        """
        Where OBJ is a dict and name is a string
        """

        if obj["name"] == name:
            return [obj]
        elif obj["name"] != name:
            returnlist = []
            for each in obj["controlled"]:
                returnlist += self.findinheir(each, name)
            return returnlist

    def findnamesofalltoremove(self, obj):
        names = []
        if obj["controlled"]:
            for item in obj["controlled"]:
                names.append(item["name"])
                if "dropped" in item.keys():
                    if item["dropped"]:
                        names += self.findnamesofalltoremove(item)
        return names

    def displaytreeitem(self, passdict, offset=0, clickable=True):
        root = passdict["name"]

        iconsize = 14 * self.scale / 100
        textsize = 14 * self.scale / 100
        textcolour = "#ffffff"

        if clickable:
            offsetspace = ft.Container(ft.Text("", width=offset))

            iconelement = ft.Icon(name=ft.icons.ADD_BOX_OUTLINED, color="#ffffff", size=iconsize)
            textelement = ft.Text(root, visible=False)
            iconbutton = ft.Container(ft.Row(controls=[iconelement, textelement]),
                                      padding=2,
                                      on_click=self.diplaylistofheir,
                                      on_hover=self.conthover,
                                      shape=ft.BoxShape.CIRCLE)

            butstyle = ft.ButtonStyle(shape=ft.RoundedRectangleBorder(),
                                      color=textcolour,
                                      padding=0)
            textbutton = ft.TextButton(root,
                                       on_click=self.displayiteminfomationinmain,
                                       style=butstyle)

            rowcontents = [offsetspace, iconbutton, textbutton]
        else:
            opt1 = ft.Icon(name=ft.icons.ARROW_RIGHT, color="#000000", size=iconsize)
            rowcontents = [ft.Container(ft.Text("", width=offset, color="#000000")),
                           ft.Container(ft.Row(controls=[opt1, ft.Text(root)]),
                                        padding=2)]

        baserow = ft.Row(controls=rowcontents,
                         alignment=ft.MainAxisAlignment.START,
                         vertical_alignment=ft.CrossAxisAlignment.CENTER,
                         spacing=0)

        onlinelist = [baserow]
        if "avaliable" in passdict.keys():
            if passdict["avaliable"]:
                avaliable = "#2dc21f"  # Green
            else:
                avaliable = "#bd0610"  # Red
            containerpadd = 2
            onlinelist.append(ft.Container(content=ft.Icon(name="CIRCLE_SHARP",
                                                           size=(iconsize - containerpadd) * 5 / 8,
                                                           color=avaliable),
                                           bgcolor="#150707", padding=containerpadd, margin=0,
                                           shape=ft.BoxShape.CIRCLE))

        baseitem = ft.Container(content=ft.Row(controls=onlinelist,
                                               width=self.sidebarsize,
                                               alignment=ft.MainAxisAlignment.START,
                                               vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                               spacing=5)
                                , bgcolor=self.bgcolour, alignment=ft.Alignment(0.0, -1.0))

        return baseitem

    def conthover(self, e):
        e.control.bgcolor = "#ff1010" if e.data == "true" else self.bgcolour
        e.control.update()
        self.page.update()


class ScheduleTab(TabInheritance):
    def __init__(self, sqn, bgcolour, page, sidewindowobj, sidebarsize=220, scale=100, offsetgrowth=10):
        super().__init__(sqn, bgcolour, page, sidewindowobj, sidebarsize, scale, offsetgrowth)

        self.lastevent = None
        self.laste = None

        self.colour = self.tabcolours["Schedule"]

        self.sidebarcontents = ft.Container(ft.Text("Schedule sidebar"),
                                            expand=True,
                                            bgcolor=self.colour,
                                            width=self.sidebarsize)
        self.sidewindow = ft.Container(content=ft.Text("Schedule window..."), expand=True)

    def redrawlastevent(self):
        self.sidewindowobj.setstruct(self.sidewindow)


class ObservedTab(TabInheritance):
    def __init__(self, sqn, bgcolour, page, sidewindowobj, sidebarsize=220, scale=100, offsetgrowth=10):
        super().__init__(sqn, bgcolour, page, sidewindowobj, sidebarsize, scale, offsetgrowth)

        self.lastevent = None
        self.laste = None

        self.colour = self.tabcolours["Schedule"]

        self.sidebarcontents = ft.Container(ft.Text("Observed sidebar"),
                                            expand=True,
                                            bgcolor=self.colour,
                                            width=self.sidebarsize)
        self.sidewindow = ft.Container(content=ft.Text("Observed window..."), expand=True)

    def redrawlastevent(self):
        self.sidewindowobj.setstruct(self.sidewindow)


class SideWindowController:
    def __init__(self, page, scale=100):
        self.page = page
        self.struct = ft.Container(content=ft.Column(controls=[ft.Row([ft.Text("Save"),
                                                                       ft.Text("revert"),
                                                                       ft.Text("Close")],
                                                                      height=20 * scale / 100),
                                                               ft.Column(controls=[ft.Text("Temp class")])]),
                                   padding=5)
        # self.struct = ft.Column(controls=[ft.Text("Temp class")])
        self.page.update()

    def setstruct(self, newstruct):
        if isinstance(newstruct, list):
            self.struct.content.controls = newstruct
        else:
            self.struct.content = newstruct

        self.page.update()


def window(page: ft.page):
    def event(e):
        if e.data != "focus" or e.data != "blur":
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
        nonlocal tabcolour, currenttab
        tabcolour = tabcolours[e.control.text]

        if e.control.text == "System":
            currenttab = "System"
            replacement = systemtabobj.displayavaliabletree()
            sidewindowobj.setstruct(systemtabobj.sidewindow)
        elif e.control.text == "Schedule":
            currenttab = "Schedule"
            replacement = scheduleobj.sidebarcontents
            sidewindowobj.setstruct(scheduleobj.sidewindow)
        else:
            currenttab = "Observed"
            replacement = observedobj.sidebarcontents
            sidewindowobj.setstruct(observedobj.sidewindow)

        page.controls[1].controls[0].content.controls[1] = replacement
        page.update()

    def drawhome():
        secondheight = page.window.height - bannerheight
        nonlocal spacing, tabcolour, sidebarsize
        page.clean()
        banner = ft.Container(content=ft.Text("", width=page.window.width, height=bannerheight),
                              bgcolor="#ffffff")

        sidebarbuttons = ft.Row([ft.Container(ft.TextButton("System",
                                                            on_click=tab_clicked,
                                                            style=buttonstyleours),
                                              bgcolor=tabcolours["System"],
                                              border_radius=ft.border_radius.vertical(top=5), expand=True),
                                 ft.Container(ft.TextButton("Schedule",
                                                            on_click=tab_clicked,
                                                            style=buttonstyleours),
                                              bgcolor=tabcolours["Schedule"],
                                              border_radius=ft.border_radius.vertical(top=5), expand=True),
                                 ft.Container(ft.TextButton("Observed",
                                                            on_click=tab_clicked,
                                                            style=buttonstyleours),
                                              bgcolor=tabcolours["Observed"],
                                              border_radius=ft.border_radius.vertical(top=5), expand=True)],
                                spacing=spacing,
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                width=sidebarsize)

        if currenttab == "System":
            sidebarcontent = systemtabobj.treecontrainer
            systemtabobj.redrawlastevent()
        elif currenttab == "Schedule":
            sidebarcontent = scheduleobj.sidebarcontents
            scheduleobj.redrawlastevent()
        else:
            sidebarcontent = observedobj.sidebarcontents
            observedobj.redrawlastevent()

        sidebar = ft.Container(
            ft.Column([
                sidebarbuttons,
                ft.Container(content=sidebarcontent, bgcolor=tabcolour, expand=True, width=sidebarsize)
            ],
                expand=1,
                height=secondheight,
                alignment=ft.MainAxisAlignment.START,
                spacing=0
            ))

        mainwindow = ft.Container(content=sidewindowobj.struct,
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
        if currentpage == "Home":
            drawhome()

    # Themes
    global tabcolours
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
    currentpage = "Home"
    currenttab = "System"
    tabcolour = tabcolours["System"]

    sidewindowobj = SideWindowController(page)

    global sq
    systemtabobj = SystemTab(sq, tabcolours["System"], page, sidewindowobj, sidebarsize)
    systemtabobj.sidewindow = [ft.Text("Placeholder text for system...")]
    scheduleobj = ScheduleTab(sq, tabcolours["Schedule"], page, sidewindowobj, sidebarsize)
    scheduleobj.sidewindow = [ft.Text("Placeholder text for schedule...")]
    observedobj = ObservedTab(sq, tabcolours["Observed"], page, sidewindowobj, sidebarsize)
    observedobj.sidewindow = [ft.Text("Placeholder text for observed...")]

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
tabcolours = {}
start()


## Add context menu and save functionality+