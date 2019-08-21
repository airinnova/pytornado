import tixi3.tixi3wrapper as tixiwrapper
from pytornado.fileio.cpacs import get_aero_map

tixi = tixiwrapper.Tixi3()
tixi.open('_cpacs/apm/pytornado/aircraft/B777_testAeroMap.xml')

get_aero_map(tixi)

