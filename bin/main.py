# Made by Alex Harrison (alex.harrison.xela@gmail.com)
# under creative commons 3.0 lisence

"""
import astropy as aspy
import astropy.units as u
import astropy.coordinates as ascod
"""
from PyObsHub.Gui import gui as fe
from PyObsHub.Server import serverInstance as si
import threading

"""
def testing():
    long, lat = (51.364076750227284, -0.9667076203406508)
    coord = ascod.SkyCoord.from_name("m38")
    EarthCentreCoord = ascod.SkyCoord.from_name("earth")
    CurrentCoord = ascod.EarthLocation.from_geodetic(51.364076750227284, -0.9667076203406508)
"""





if __name__ == "__main__":
    print("Running main...")
    # fe.start()   ##GUI start
    si.testing.test1("controllerconfig.json", remove=False)
    serverObj = si.serverinstance("localhost",
                      2000,
                      "controllerconfig.json")

    #testing()
