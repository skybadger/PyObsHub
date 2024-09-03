from wsgiref.simple_server import make_server

import falcon
import json
import datetime

class Hierarchy:
    hierarchy = ["Controller", "Site", "Station", "Mount", "OTA", "Port"]

    def __init__(self, name,
                 level,
                 lastupdated=datetime.datetime.now().isoformat(),
                 associateddata="",
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

        :param item: Item of class inherited(Hierarchy) but without the required level association (level is not required to be one below)
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
        ## Will break if there is a cyclical reference!
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
        with open(filename, "r") as openfile:
            savedict = json.load(openfile)
            sitelist = savedict["controlled"]
            sites = []
            for siteidx in range(len(sitelist)):
                tempsite = Site(sitelist[siteidx]["name"],
                                level="Site",
                                lastupdated=sitelist[siteidx]["lastupdated"],
                                associateddata=sitelist[siteidx]["associateddata"],
                                avaliable=sitelist[siteidx]["avaliable"])

                stationlist = sitelist[siteidx]["controlled"]
                stations = []
                for stationidx in range(len(stationlist)):
                    tempstation = Site(stationlist[stationidx]["name"],
                                    level="Station",
                                    lastupdated=stationlist[stationidx]["lastupdated"],
                                    associateddata=stationlist[stationidx]["associateddata"],
                                    avaliable=stationlist[stationidx]["avaliable"])

                    mountlist = stationlist[stationidx]["controlled"]
                    mounts = []
                    for mountidx in range(len(mountlist)):
                        tempmount = Site(mountlist[mountidx]["name"],
                                        level="Mount",
                                        lastupdated=mountlist[mountidx]["lastupdated"],
                                        associateddata=mountlist[mountidx]["associateddata"],
                                        avaliable=mountlist[mountidx]["avaliable"])

                        otalist = mountlist[mountidx]["controlled"]
                        otas = []
                        for otaidx in range(len(otalist)):
                            tempota = Site(otalist[otaidx]["name"],
                                            level="OTA",
                                            lastupdated=otalist[otaidx]["lastupdated"],
                                            associateddata=otalist[otaidx]["associateddata"],
                                            avaliable=otalist[otaidx]["avaliable"])

                            portlist = otalist[otaidx]["controlled"]
                            ports = []
                            for portidx in range(len(sitelist)):
                                tempport = Site(portlist[portidx]["name"],
                                                level="Port",
                                                lastupdated=portlist[portidx]["lastupdated"],
                                                associateddata=portlist[portidx]["associateddata"],
                                                controlled=None,
                                                avaliable=portlist[portidx]["avaliable"])

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
            sitedict = dict()
            sitedict["name"] = siteObj.name
            sitedict["level"] = "Site"
            sitedict["lastupdated"] = siteObj.lastupdated
            sitedict["associateddata"] = siteObj.associateddata
            sitedict["controlled"] = []
            sitedict["avaliable"] = siteObj.avaliable

            for stationObj in siteObj.controlled:
                stationdict = dict()
                stationdict["name"] = stationObj.name
                stationdict["level"] = "Station"
                stationdict["lastupdated"] = stationObj.lastupdated
                stationdict["associateddata"] = stationObj.associateddata
                stationdict["controlled"] = []
                stationdict["avaliable"] = stationObj.avaliable

                for mountObj in stationObj.controlled:
                    mountdict = dict()
                    mountdict["name"] = mountObj.name
                    mountdict["level"] = "Mount"
                    mountdict["lastupdated"] = mountObj.lastupdated
                    mountdict["associateddata"] = mountObj.associateddata
                    mountdict["controlled"] = []
                    mountdict["avaliable"] = mountObj.avaliable

                    for OTAObj in mountObj.controlled:
                        OTAdict = dict()
                        OTAdict["name"] = OTAObj.name
                        OTAdict["level"] = "OTA"
                        OTAdict["lastupdated"] = OTAObj.lastupdated
                        OTAdict["associateddata"] = OTAObj.associateddata
                        OTAdict["controlled"] = []
                        OTAdict["avaliable"] = OTAObj.avaliable

                        for portObj in OTAObj.controlled:
                            portdict = dict()
                            portdict["name"] = portObj.name
                            portdict["level"] = "Port"
                            portdict["lastupdated"] = portObj.lastupdated
                            portdict["associateddata"] = portObj.associateddata
                            portdict["controlled"] = None
                            portdict["avaliable"] = portObj.avaliable

                            OTAdict["controlled"].append(portdict)
                        mountdict["controlled"].append(OTAdict)
                    stationdict["controlled"].append(mountdict)
                sitedict["controlled"].append(stationdict)
            savedict["controlled"].append(sitedict)

        with open(filename, "w") as openfile:
            json.dump(savedict, openfile, indent=6)


class Site(Hierarchy):
    def loadfrompkl(self):
        pass

    def savetopkl(self):
        pass


class Station(Hierarchy):
    def loadfrompkl(self):
        pass

    def savetopkl(self):
        pass


class Mount(Hierarchy):
    def loadfrompkl(self):
        pass

    def savetopkl(self):
        pass


class Ota(Hierarchy):
    def loadfrompkl(self):
        pass

    def savetopkl(self):
        pass


class Port(Hierarchy):
    def loadfrompkl(self):
        pass

    def savetopkl(self):
        pass


port = Port(name="templatePort", level="Port", associateddata="15232", avaliable=False)
port2 = Port(name="templatePort2", level="Port", associateddata="17231", avaliable=True)
OTA = Ota(name="templateOTA", level="OTA", associateddata="port controller", avaliable=False, controlled=[port])
OTA2 = Ota(name="templateOTA2", level="OTA", associateddata="port controller", avaliable=False, controlled=[port2])
mount = Mount(name="templateMount", level="Mount", associateddata="OTA controller", avaliable=False, controlled=[OTA])
mount2 = Mount(name="templateMount2", level="Mount", associateddata="OTA controller", avaliable=False, controlled=[OTA2])
station = Station(name="templateStation", level="Station", associateddata="Mount controller", avaliable=False, controlled=[mount, mount2])
site = Site(name="templateSite", level="Site", associateddata="Station controller", avaliable=False, controlled=[station])
controller = Hierarchy(name="templateController", level="Controller", avaliable=True, controlled=[site])
controller.savetojson()
print(controller.listallcontrolled())

controller2 = Hierarchy(name="templateController", level="Controller", avaliable=True, controlled=[])
controller2.loadfromjson()
print(controller2.listallcontrolled())
assert controller.listallcontrolled() == controller2.listallcontrolled()


class ReqHandler:

    @staticmethod
    def on_get(req, resp):
        """Handles GET requests"""
        resp.status = falcon.HTTP_200
        resp.content_type = falcon.MEDIA_JSON
        responsedict = {"app": 300, "coins": 200}
        print(json.dumps(responsedict))
        resp.body = json.dumps(responsedict)

# falcon.App instances are callable WSGI apps
# in larger applications the app is created in a separate file


app = falcon.App()
reqobj = ReqHandler()
app.add_route('/site', reqobj)
"""
if __name__ == '__main__':
    with make_server('', 8000, app) as httpd:
        print('Serving on port 8000...')

        # Serve until process is killed

        httpd.serve_forever()
"""