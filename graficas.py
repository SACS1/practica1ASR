import sys
import rrdtool
import time

tiempo_actual = int(time.time())
#Grafica desde el tiempo actual menos diez minutos
tiempo_inicial = tiempo_actual - 300


def graficaInPaqsUni(alias):

    ret = rrdtool.graph( "inPaqsUni_" + alias + ".png",
                         "--start",str(tiempo_inicial),
                         "--end","N",
                         "--vertical-label=Paquetes",
                         "--title=Paquetes Unicast que ha recibido una interfaz \n Usando SNMP y RRDtools",
                         "DEF:PaquetesEntrada=" + alias + ".rrd:inPaqsUni:AVERAGE",
                         "LINE3:PaquetesEntrada#00FF00:Tráfico de entrada")

def graficaInPaqsIPv4(alias):

    ret = rrdtool.graph( "inPaqsIPv4_" + alias + ".png",
                         "--start",str(tiempo_inicial),
                         "--end","N",
                         "--vertical-label=Paquetes",
                         "--title=Paquetes recibidos a protocolos IPv4\n Usando SNMP y RRDtools",
                         "DEF:PaquetesEntrada=" + alias + ".rrd:inPaqsIPv4:AVERAGE",
                         "LINE3:PaquetesEntrada#00FF00:Tráfico de entrada")

def graficaOutMsjICMP(alias):

    ret = rrdtool.graph( "outMsjICMP_" + alias + ".png",
                         "--start",str(tiempo_inicial),
                         "--end","N",
                         "--vertical-label=Mensajes",
                         "--title=Mensajes ICMP Echo enviados\n Usando SNMP y RRDtools",
                         "DEF:MensajesSalida=" + alias + ".rrd:outMsjICMP:AVERAGE",
                         "LINE3:MensajesSalida#00FF00:Mensajes enviados")

def graficaInSeg(alias):

    ret = rrdtool.graph( "inSeg_" + alias + ".png",
                         "--start",str(tiempo_inicial),
                         "--end","N",
                         "--vertical-label=Bytes/s",
                         "--title=Segmentos que ha recibido una interfaz \n Usando SNMP y RRDtools",
                         "DEF:SegmentosEntrada=" + alias + ".rrd:inSeg:AVERAGE",
                         "CDEF:escala=SegmentosEntrada,8,*",
                         "LINE3:escala#00FF00:Tráfico de entrada")

def graficaOutDatagram(alias):

    ret = rrdtool.graph( "outDatagram_" + alias + ".png",
                         "--start",str(tiempo_inicial),
                         "--end","N",
                         "--vertical-label=Datagramas",
                         "--title=Datagramas entregados a usuarios UDP \n Usando SNMP y RRDtools",
                         "DEF:PaquetesEntrada=" + alias + ".rrd:outDatagram:AVERAGE",
                         "LINE3:PaquetesEntrada#00FF00:Tráfico de entrada")
