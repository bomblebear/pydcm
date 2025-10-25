from pydcm import dcminfo

dcm = dcminfo()
dcm.read("../data/DEMO.DCM")
# find functions:0, calibrations:5, axises:0

DEMO_CURVE = dcm.calibrations["DEMO_CURVE"]
print(DEMO_CURVE)
# name=DEMO_CURVE, description=This is a standard curve: one input and one output.
# line_start=35, line_end=43
# type=CURVE, unit=
# value=
# [0.30078125, 0.3984375, 0.5, 0.59765625, 0.69921875, 0.80078125, 0.8984375]
# axis x
# name=, description=
# line_start=0, line_end=0
# type=, unit=revs
# value=
# [120.0, 200.0, 320.0, 400.0, 520.0, 600.0, 720.0]

DEMO_MAP_2 = dcm.getcalobject("DEMO_MAP_2")
#DEMO_MAP_2.show()



baseDCMPath = "../data/DEMO.DCM"
tgtDCMPath = "../data/autoGen.DCM"

deflist = []
dcm = dcminfo(baseDCMPath)

calobj = dcm.getcalobject('DEMO_CURVE')
calobj.value = [1,2,3,4,5,6,7]
deflist.append(dcm.getDCMDefStr(calobj))

calobj = dcm.addcalibration('AddedCalibration')
calobj.keyword = 'FESTWERT'
calobj.type = dcm.keywords[calobj.keyword]
calobj.value = [400]
deflist.append(dcm.getDCMDefStr(calobj))

dcm.genDcmFile(tgtDCMPath, deflist)