from wsgiref.simple_server import make_server

import falcon
import json
import datetime
import os
import threading


class Hierarchy:
    hierarchy = ["Controller", "Site", "Station", "Mount", "OTA", "Port"]

    def __init__(self, name,
                 level,
                 lastupdated=datetime.datetime.now().isoformat(),
                 associateddata=None,
                 controlled=None,
                 avaliable=False):
        """

        :param name: name of the associated item such as a port or station
        :param level: level of the item in the Hierarchy (["Site", "Station", "Mount", "OTA", "Port"])
        :param lastupdated: Date when this item was last updated
        :param associateddata: Any required data like com port, author, admin email
        :param controlled: All controlled items one level below of type inhertied(Hierarchy)
        :param avaliable: If the avaliable item or resource is currently avaliable or off/needs maintenance
        """

        self.name = name
        self.level = level
        self.lastupdated = lastupdated
        self.associateddata = associateddata
        self.controlled = controlled
        if controlled is None and level != "Port":
            self.controlled = []

        self.avaliable = avaliable

    def add(self, item):
        """

        :param item: An object of class inherited(Hierarchy), must be only one level below
        """
        idx = self.hierarchy.index(self.level)
        itemidx = self.hierarchy.index(item.level)
        if (itemidx - idx) != 1:
            raise ValueError(f"Level of attached item must be one below original item! "
                             f"Orignal level: {self.level}, attached item level: {item.level}.")
        else:
            self.controlled.append(item)

    def addnonhierarchical(self, item):
        """

        :param item: Item of class inherited(Hierarchy) but without the required level association
        (level is not required to be one below)
        """
        self.controlled.append(item)

    def remove(self, index):
        """

        :param index: Index of item to remove from the controlled object list
        """
        if self.controlled is not None:
            if len(self.controlled) != 0:
                self.controlled.pop(index)
            else:
                raise IndexError("Attempted to remove item from list of size zero!")
        else:
            raise AttributeError("Controlled is of type None, probably because item is of level 'Port'!")

    def listcontrolled(self):
        """
        :return: List of controlled objects
        """
        return self.controlled

    def listallcontrolled(self):
        """

        :return: Entire hierarchy from the current object level upwards
        """
        return self.returncontrolledobjs(self)

    @staticmethod
    def returncontrolledobjs(obj):
        """
        Will break if there is a cyclical reference! Do not use, instead use listallcontrolled
        :param obj: Object of inherited class (hierarchy)
        :return: List of controlled item
        """
        if obj.level != obj.hierarchy[-1]:
            returnlist = []
            for objectItem in obj.controlled:
                returnlist.append(obj.returncontrolledobjs(objectItem))
            return [obj.name, returnlist]
        else:
            return obj.name

    def loadfromjson(self, filename="controller_config.json"):
        try:
            open(filename, "r")
        except FileNotFoundError:
            raise FileNotFoundError("No config file exists with that name!")

        with open(filename, "r") as openfile:
            savedict = json.load(openfile)
            sitelist = savedict["controlled"]
            sites = []
            for siteidx in range(len(sitelist)):
                sitedicttoload = sitelist[siteidx]
                tempsite = Site(**sitedicttoload)
                stationlist = sitelist[siteidx]["controlled"]
                stations = []

                for stationidx in range(len(stationlist)):
                    stationdicttoload = stationlist[stationidx]
                    tempstation = Station(**stationdicttoload)
                    mountlist = stationlist[stationidx]["controlled"]
                    mounts = []

                    for mountidx in range(len(mountlist)):
                        mountdicttoload = mountlist[mountidx]
                        tempmount = Mount(**mountdicttoload)
                        otalist = mountlist[mountidx]["controlled"]
                        otas = []

                        for otaidx in range(len(otalist)):
                            otadicttoload = otalist[otaidx]
                            tempota = Ota(**otadicttoload)
                            portlist = otalist[otaidx]["controlled"]
                            ports = []

                            for portidx in range(len(sitelist)):
                                portdictoload = portlist[portidx]
                                tempport = Port(**portdictoload)
                                ports.append(tempport)

                            tempota.controlled = ports
                            otas.append(tempota)

                        tempmount.controlled = otas
                        mounts.append(tempmount)

                    tempstation.controlled = mounts
                    stations.append(tempstation)

                tempsite.controlled = stations
                sites.append(tempsite)

            self.controlled = sites

    def savetojson(self, filename="controller_config.json"):
        savedict = dict()
        savedict["controlled"] = []
        for siteObj in self.controlled:
            sitedict = {key: value for key, value in siteObj.__dict__.items() if not key.startswith('__') and not callable(key)}
            sitedict["controlled"] = []

            for stationObj in siteObj.controlled:
                stationdict = {key: value for key, value in stationObj.__dict__.items() if not key.startswith('__') and not callable(key)}
                stationdict["controlled"] = []

                for mountObj in stationObj.controlled:
                    mountdict = {key: value for key, value in mountObj.__dict__.items() if not key.startswith('__') and not callable(key)}
                    mountdict["controlled"] = []

                    for OTAObj in mountObj.controlled:
                        otadict = {key: value for key, value in OTAObj.__dict__.items() if not key.startswith('__') and not callable(key)}
                        otadict["controlled"] = []

                        for portObj in OTAObj.controlled:
                            portdict = {key: value for key, value in portObj.__dict__.items() if not key.startswith('__') and not callable(key)}
                            portdict["controlled"] = None

                            otadict["controlled"].append(portdict)
                        mountdict["controlled"].append(otadict)
                    stationdict["controlled"].append(mountdict)
                sitedict["controlled"].append(stationdict)

            savedict["controlled"].append(sitedict)

        with open(filename, "w") as openfile:
            json.dump(savedict, openfile, indent=6)


class Site(Hierarchy):
    def __init__(self, name,
                 level,
                 location,
                 elevation,
                 tzoffset,
                 lastupdated=datetime.datetime.now().isoformat(),
                 associateddata=None,
                 controlled=None,
                 avaliable=False):
        """

        :param name: name of the associated item such as a port or station
        :param level: level of the item in the Hierarchy (["Site", "Station", "Mount", "OTA", "Port"])
        :param lastupdated: Date when this item was last updated
        :param associateddata: Any required data like com port, author, admin email
        :param controlled: All controlled items one level below of type inhertied(Hierarchy)
        :param avaliable: If the avaliable item or resource is currently avaliable or off/needs maintenance
        """

        super().__init__(name, level, lastupdated, associateddata, controlled, avaliable)
        self.location = location
        self.elevation = elevation
        self.tzoffset = tzoffset

    def loadfromjson(self, filename="controller_config.json"):
        pass

    def savetojson(self, filename="controller_config.json"):
        pass


class Station(Hierarchy):
    stationtypes = ["None", "Fenced", "Dome", "Roll-off"]

    def __init__(self, name: str,
                 level: str,
                 stationtype: str,
                 hostname: str,
                 interfacetype: str,
                 altlimits: tuple = (0, 90),
                 flatfielder=None,
                 lastupdated=datetime.datetime.now().isoformat(),
                 associateddata: str = "",
                 controlled: None or [] = None,
                 avaliable: bool = False):

        super().__init__(name, level, lastupdated, associateddata, controlled, avaliable)
        try:
            self.stationtypes.index(stationtype)
        except ValueError:
            raise ValueError(f"Station type is not listed in avaliable types! ({self.stationtypes})")
        else:
            self.stationtype = stationtype

        self.hostname = hostname
        self.interfacetype = interfacetype
        self.altlimits = altlimits
        self.flatfielder = flatfielder

    def loadfromjson(self, filename="controller_config.json"):
        pass

    def savetojson(self, filename="controller_config.json"):
        pass


class Mount(Hierarchy):

    def __init__(self, name,
                 level,
                 horizonmap: tuple = (0, 0, 0),
                 telescope: dict = None,
                 lastupdated=datetime.datetime.now().isoformat(),
                 associateddata="",
                 controlled=None,
                 avaliable=False):
        super().__init__(name, level, lastupdated, associateddata, controlled, avaliable)
        self.horizonmap = horizonmap
        if telescope is None:
            self.telescope = {"name": None,
                              "hostname": "FQDN",
                              "protocol": "string",
                              "port": "0000"}
        else:
            self.telescope = telescope

    def loadfromjson(self, filename="controller_config.json"):
        pass

    def savetojson(self, filename="controller_config.json"):
        pass


class Ota(Hierarchy):
    otatypes = []

    def __init__(self, name,
                 level,
                 otatype: str,
                 aperture: float,
                 obstruction: str,
                 fratio: float,
                 spectralrange: tuple,
                 dewheater: dict = None,
                 lastupdated=datetime.datetime.now().isoformat(),
                 associateddata="",
                 controlled=None,
                 avaliable=False):

        super().__init__(name, level, lastupdated, associateddata, controlled, avaliable)
        self.otatype = otatype
        self.aperture = aperture
        self.obstruction = obstruction
        self.fratio = fratio
        self.spectralrange = spectralrange
        if dewheater is None:
            self.dewheater = {"name": None,
                              "hostname": "FQDN",
                              "protocol": "string",
                              "port": "0000",
                              "powerlevel": "50",
                              "poweron": False,
                              "useconditions": True}
        else:
            self.dewheater = dewheater

    def setcovercalibrator(self, name: str, hostname: str = "FQDN", protocol: str = "", port: int = 1242):
        ad = {"hostname": hostname, "protocol": protocol, "port": port}
        covercalibrator = Port(name, "Port", associateddata=ad, avaliable=True)
        self.addnonhierarchical(covercalibrator)

    def loadfromjson(self, filename="controller_config.json"):
        pass

    def savetojson(self, filename="controller_config.json"):
        pass


class Port(Hierarchy):

    def __init__(self, name,
                 level,
                 focuser: dict = None,
                 camera: dict = None,
                 filterwheel: dict = None,
                 lastupdated=datetime.datetime.now().isoformat(),
                 associateddata=None,
                 controlled=None,
                 avaliable=False):
        """

        :param name: name of the associated item such as a port or station
        :param level: level of the item in the Hierarchy (["Site", "Station", "Mount", "OTA", "Port"])
        :param lastupdated: Date when this item was last updated
        :param associateddata: Any required data like com port, author, admin email
        :param controlled: All controlled items one level below of type inhertied(Hierarchy)
        :param avaliable: If the avaliable item or resource is currently avaliable or off/needs maintenance
        """

        super().__init__(name, level, lastupdated, associateddata, controlled, avaliable)
        if focuser is None:
            self.focuser = {"name": None, "hostname": None, "protocol": None, "port": 1234}
        else:
            self.focuser = focuser

        if camera is None:
            self.camera = {"name": None, "hostname": None, "protocol": None}
        else:
            self.camera = camera

        if focuser is None:
            self.filterwheel = {"name": None, "hostname": None, "protocol": None, "port": 1234}
        else:
            self.filterwheel = filterwheel

    def loadfromjson(self, filename="controller_config.json"):
        pass

    def savetojson(self, filename="controller_config.json"):
        pass


class Testing:
    def __init__(self):
        self.test1()

    @staticmethod
    def test1(filename="TestConfig", remove=True):
        port = Port(name="templatePort", level="Port", associateddata="15232", avaliable=False)
        port2 = Port(name="templatePort2", level="Port", associateddata="17231", avaliable=True)
        ota = Ota(name="templateOTA",
                  level="OTA",
                  otatype="template",
                  aperture=1.3,
                  obstruction="wall",
                  fratio=4.3,
                  spectralrange=(300 * 10 ** -9, 1000 * 10 ** -9),
                  associateddata="port controller",
                  avaliable=False,
                  controlled=[port])
        ota2 = Ota(name="templateOTA2",
                   level="OTA",
                   otatype="template2",
                   aperture=1.3,
                   obstruction="wall",
                   fratio=4.3,
                   spectralrange=(300 * 10 ** -9, 1000 * 10 ** -9),
                   associateddata="port controller",
                   avaliable=False,
                   controlled=[port2])
        mount = Mount(name="templateMount", level="Mount", associateddata="OTA controller", avaliable=False,
                      controlled=[ota])
        mount2 = Mount(name="templateMount2", level="Mount", associateddata="OTA controller", avaliable=False,
                       controlled=[ota2])
        station = Station(name="templateStation",
                          level="Station",
                          stationtype="Dome",
                          hostname="localhost",
                          interfacetype="fast",
                          associateddata="Mount controller",
                          avaliable=False,
                          controlled=[mount, mount2])
        site = Site(name="templateSite",
                    level="Site",
                    location=(51.234, 52.324),
                    elevation=74,
                    tzoffset=0.94,
                    associateddata="Station controller",
                    avaliable=False,
                    controlled=[station])
        controller = Hierarchy(name="templateController", level="Controller", avaliable=True, controlled=[site])
        controller.savetojson(filename)

        if remove:
            controller2 = Hierarchy(name="templateController", level="Controller", avaliable=True, controlled=[])
            controller2.loadfromjson(filename)
            os.remove(filename)
            assert controller.listallcontrolled() == controller2.listallcontrolled()

    @staticmethod
    def loadtest(filename="controllerconfig.json"):
        controller2 = Hierarchy(name="templateController", level="Controller", avaliable=True, controlled=[])
        controller2.loadfromjson(filename)
        return controller2.listallcontrolled()

class ReqHandlerRorController:

    @staticmethod
    def on_get(req, resp):
        """Handles GET requests"""
        send = req.context
        print(send)
        resp.status = falcon.HTTP_200
        resp.content_type = falcon.MEDIA_JSON
        responsedict = {"app": 300, "coins": 200}
        print(json.dumps(responsedict))
        resp.text = json.dumps(responsedict)


# falcon.App instances are callable WSGI apps
# in larger applications the app is created in a separate file


class ServerInstance:
    def __init__(self, host: str = "localhost", port: int = 2000, controllerconfig: str = "contconfig.json"):
        """

        :param host: String of hosted ip for the server
        :param port: Int port number upto 2^8
        :param controllerconfig: Config file name
        """
        self.host = host
        self.port = port
        self.controllerconfig = controllerconfig

        self.app = falcon.App()
        reqobj = ReqHandlerRorController()
        self.app.add_route('/controller', reqobj)

        print("Server starting...")
        self.serverthread = threading.Thread(target=self.startserver, daemon=True)
        self.serverthread.start()
        print("Server started!")

        print("Loading controller config...")
        self.controller = Hierarchy(name="ServerController", level="Controller", avaliable=True)
        self.controllerthread = threading.Thread(target=self.controller.loadfromjson, args=(self.controllerconfig,))
        self.controllerthread.start()
        self.controllerthread.join()
        print("Controller config loaded!")

        tempthread = threading.Timer(5, self.turnserveroff)
        tempthread.start()

        self.serveronline = True
        while self.serveronline:
            pass
        print("Ending server!")

    def startserver(self):
        with make_server(self.host, self.port, self.app) as httpd:
            print(f"Serving on port {self.port} at address {self.host}")
            httpd.serve_forever()

    def turnserveroff(self):
        self.serveronline = False
