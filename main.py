# Made by Alex Harrison (alex.harrison.xela@gmail.com)
# under creative commons 3.0 license

"""
import astropy as aspy
import astropy.units as u
import astropy.coordinates as ascod

# for gui
from PyObsHub.Gui import gui as fe
"""
import Server.serverInstance as Si

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
    Si.Testing.test1("controllerconfig.json", False)
    Si.Testing.test1("test.json", True)


    serverObj = Si.ServerInstance("localhost",
                                  2000,
                                  "controllerconfig.json")

    print("Ending main!")
