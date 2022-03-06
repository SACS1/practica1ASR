import rrdtool

def crearRRD(alias):
    ret = rrdtool.create(alias + ".rrd",
                         "--start",'N',
                         "--step",'60',
                         "DS:inPaqsUni:COUNTER:120:U:U",
                         "DS:inPaqsIPv4:COUNTER:120:U:U",
                         "DS:outMsjICMP:COUNTER:120:U:U",
                         "DS:inSeg:COUNTER:120:U:U",
                         "DS:outDatagram:COUNTER:120:U:U",
                         "RRA:AVERAGE:0.5:1:20",
                         "RRA:AVERAGE:0.5:1:20",
                         "RRA:AVERAGE:0.5:1:20",
                         "RRA:AVERAGE:0.5:1:20",
                         "RRA:AVERAGE:0.5:1:20")

    if ret:
        print (rrdtool.error())
