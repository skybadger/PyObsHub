import flet as ft



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
        print(tabcolour)
        tabcolour = tabcolours[e.control.text]
        page.controls[1].controls[0].content.controls[1] = ft.Container(content=ft.Text(e.control.text, width=sidebarsize), bgcolor=tabcolour, expand=True)
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

    page.window_min_width, page.window.max_width = 400, 1920
    page.window.min_height, page.window.max_height = 300, 1080

    page.window.on_event = event
    page.on_resize = redrawToFit
    page.update()


def start():
    ft.app(target=window)
