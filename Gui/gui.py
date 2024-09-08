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


class SystemTab:
    color = "#ff2354"

    def __init__(self, sqn, bgcolour, page, sidebarsize=220, scale=100, offsetgrowth = 10):
        self.sq = sqn
        self.bgcolour = bgcolour
        self.scale = scale
        self.page = page
        self.offsetgrowth = offsetgrowth
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

        self.treecontrainer = ft.Container(content=ft.Column(spacing=0),
                                           bgcolor=self.bgcolour,
                                           expand=True,
                                           alignment=ft.Alignment(0.0, -1.0))
        self.treecontrainer.content.controls.append(self.displaytreeitem(self.localheir, offset=0))


    def displayavaliabletree(self, navigating=[]):
        return self.treecontrainer

    """
    def displaylist(self, e):
        name = e.control.content.controls[1].value
        print(name)
        finditem = self.findintreeinfo(self.treeinfo, name)
        print(finditem)
        print(len(finditem) == 1, not self.treeinfo["dropped"], not self.treeinfo["controlled"])

        if len(finditem) == 1:
            if not self.treeinfo["dropped"]:
                self.treeinfo["dropped"] = True
                e.control.content.controls[0].name = ft.icons.INDETERMINATE_CHECK_BOX_OUTLINED
                if not self.treeinfo["controlled"]:
                    controlled = self.findcontrolledinheir(self.localheir, name)
                    for tempobj in controlled:
                        item = self.displaytreeitem(tempobj, offset=self.offsetgrowth)
                        self.treecontrainer.content.controls.append(item)
                        dictentry = {"name": tempobj["name"], "offset": self.offsetgrowth, "dropped": False, "controlled": []}
                        self.treeinfo["controlled"].append(dictentry)
                else:
                    print("Dropped", self.treeinfo["dropped"])
                    temp = self.finddroppedintree(self.treeinfo)
                    for obj in temp:
                        info = self.findintreeinfo(self.treeinfo, obj)
                        item = self.displaytreeitem(info, offset=info["offset"])
                        self.treecontrainer.content.controls.append(item)
                    print("Temp", temp)

            else:
                e.control.content.controls[0].name = ft.icons.ADD_BOX_OUTLINED
                self.treeinfo["dropped"] = False
                localtopop = list(self.treecontrainer.content.controls)
                popped = 0
                for i, cont in enumerate(localtopop):
                    contname = cont.content.controls[0].controls[1].content.controls[1].value
                    if contname != name:
                        self.treecontrainer.content.controls.pop(i - popped)
                        popped += 1


                pass
        elif len(finditem) == 2:
            print("Not base item")
            e.control.content.controls[0].name = ft.icons.INDETERMINATE_CHECK_BOX_OUTLINED
            controlled = self.findcontrolledinheir(self.localheir, name)
            rec = True
            idx = 1
            temp = ""
            newsearch = ""
            while rec:
                idx = finditem[0]
                temp = self.treeinfo["controlled"][idx]
                newsearch = self.findintreeinfo(temp, name)
                if len(newsearch) == 1:
                    rec = False

            if not temp["dropped"]:
                temp["dropped"] = True
                controlled = self.findcontrolledinheir(self.localheir, name)
                localtopop = list(self.treecontrainer.content.controls)
                insertpoint = 0
                for i, cont in enumerate(localtopop):
                    contname = cont.content.controls[0].controls[1].content.controls[1].value
                    if contname == name:
                        insertpoint = i
                        break

                insertidx = 1
                for tempobj in controlled:
                    item = self.displaytreeitem(tempobj, offset=self.offsetgrowth+temp["offset"])
                    self.treecontrainer.content.controls.insert(insertpoint + insertidx, item)
                    insertidx += 1
                    # self.treecontrainer.content.controls.append(item)
                    dictentry = {"name": tempobj["name"],
                                 "offset": self.offsetgrowth+temp["offset"],
                                 "dropped": False,
                                 "controlled": []}
                    temp["controlled"].append(dictentry)

                self.replacetreeinfoentry(temp, finditem)
            else:
                pass

        else:
            print("Error")
        
        """"""
        if not temptreeinfo["dropped"] and temptreeinfo["controlled"] == []:
            temptreeinfo["dropped"] = True
            e.control.content.controls[0].name = ft.icons.INDETERMINATE_CHECK_BOX_OUTLINED
            """"""
            localobjs = self.treeinfoscraper(self.localheir["controlled"])
            controlledobjs = localobjs[idx]
            for objects in controlledobjs:
                item = self.displaytreeitem(objects, offset=temptreeinfo["offset"]+self.offsetgrowth)
                self.treecontrainer.content.controls.append(item)
                temptreeinfo["controlled"].append({"name": objects["name"], "offset": temptreeinfo["offset"]+self.offsetgrowth, "dropped": False, "controlled": []})
              """"""
        elif self.treeinfo["dropped"]:
            self.treeinfo["dropped"] = False
            e.control.content.controls[0].name = ft.icons.ADD_BOX_OUTLINED
            """"""
            listofnames = self.treeinfoscraper(self.treeinfo, "name")
            listofnames.pop(0)
            numpopped = 0
            i=0
            localtopop = list(self.treecontrainer.content.controls)
            for cont in localtopop:
                contname = cont.content.controls[0].controls[1].content.controls[1].value
                if contname in listofnames:
                    self.treecontrainer.content.controls.pop(i-numpopped)
                    numpopped += 1 

                i+=1
            """"""
        else:
            self.treeinfo["dropped"] = True
            e.control.content.controls[0].name = ft.icons.INDETERMINATE_CHECK_BOX_OUTLINED

            
            
            idx = 0
            for item in listofdropped:
                dropped = True
                if listofoffset[idx] == listofoffset[idx+1] & dropped:
                    item = self.displaytreeitem(objects, offset=self.treeinfo["offset"]+self.offsetgrowth)
                    self.treecontrainer.content.controls.append(item)
            
        """"""
        self.page.update()
    """

    def displayiteminfomationinmain(self, e):
        # When a text box displayed is clicked, open the relevant information in the side window
        # for now this can just be config and nothing important until dad has more info

        # view current config
        pass

    def diplaylistofheir(self, e):
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
                    insertidx = i+1
                    break

            # Add the controlled objects to the page dropdow
            self.findallcontrolledanddroppeditems(localheir["controlled"],
                                                  localheir["offset"]+self.offsetgrowth,
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
                item = self.displaytreeitem(tempobj, offset=offset+self.offsetgrowth, clickable=False)
            else:
                item = self.displaytreeitem(tempobj, offset=offset+self.offsetgrowth, clickable=True)

            self.treecontrainer.content.controls.insert(insertidx, item)
            print(insertidx)
            insertidx += 1
            if "dropped" in tempobj.keys():
                if tempobj["dropped"] and not tempobj["controlled"]:
                    insertidx += self.findallcontrolledanddroppeditems(tempobj["controlled"],
                                                                       offset+self.offsetgrowth,
                                                                       insertidx)
        return insertidx

    def findinheir(self, obj, name):
        if obj["name"] == name:
            return [obj]
        elif obj["name"] != name:
            returnlist = []
            for each in obj["controlled"]:
                print(each)
                returnlist += self.findinheir(each, name)
            return returnlist

    def findnamesofalltoremove(self, obj):
        names = []
        if obj["controlled"]:
            for item in obj["controlled"]:
                names.append(item["name"])
                if "dropped" in item.keys():
                    if item["dropped"]:
                        print(item)
                        names += self.findnamesofalltoremove(item)
        return names
            
    def displaytreeitem(self, passdict, offset=0, clickable=True):
        print(passdict)
        root = passdict["name"]

        iconsize = 14 * self.scale / 100
        textsize = 14 * self.scale / 100
        textcolour = "#001122"

        if clickable:
            offsetspace = ft.Container(ft.Text("", width=offset))
            
            iconelement = ft.Icon(name=ft.icons.ADD_BOX_OUTLINED, color="#000000", size=iconsize)
            textelement = ft.Text(root, visible=False)
            iconbutton = ft.Container(ft.Row(controls=[iconelement, textelement]),
                                      padding=2,
                                      on_click=self.diplaylistofheir)
            
            butstyle = ft.ButtonStyle(alignment=ft.Alignment(-1, 0),
                                      shape=ft.RoundedRectangleBorder(),
                                      color=textcolour,
                                      padding=0, 
                                      visual_density=ft.VisualDensity.COMPACT)
            textbutton = ft.TextButton(root,
                                       on_click=self.displayiteminfomationinmain,
                                       style=butstyle)
            
            rowcontents = [offsetspace, iconbutton, textbutton]
            
        else:
            opt1 = ft.Icon(name=ft.icons.ARROW_RIGHT, color="#000000", size=iconsize)
            rowcontents = [ft.Container(ft.Text("", width=offset)),
                           ft.Container(ft.Row(controls=[opt1, ft.Text(root)]),
                                        padding=2)]


        baserow = ft.Row(controls=rowcontents,
                         alignment=ft.MainAxisAlignment.START,
                         vertical_alignment=ft.CrossAxisAlignment.CENTER,
                         spacing=0)

        onlinelist = [baserow]
        if "avaliable" in passdict.keys():
            print("Avaliable", passdict["avaliable"])
            if passdict["avaliable"]:
                avaliable = "#2dc21f" # Green
            else:
                avaliable = "#bd0610" # Red
            containerpadd = 1
            onlinelist.append(ft.Container(content=ft.Icon(name="CIRCLE_SHARP",
                                                           size=(iconsize - containerpadd)*5/8,
                                                           color=avaliable),
                                           bgcolor="#150707", padding=1, margin=0, shape=ft.BoxShape.CIRCLE))

        baseitem = ft.Container(content=ft.Row(controls=onlinelist,
                                               width=self.sidebarsize,
                                               alignment=ft.MainAxisAlignment.START,
                                               vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                               spacing=5)
                                , bgcolor=self.bgcolour, alignment=ft.Alignment(0.0, -1.0))

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
                ft.Container(content=systemtabobj.displayavaliabletree(), bgcolor=tabcolour, expand=True)
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
    systemtabobj = SystemTab(sq, tabcolours["System"], page, sidebarsize)

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
