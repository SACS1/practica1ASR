from consultas import conectividad
from consultas import consultaSNMP
from consultas import descInterfaces
from crearBD import crearRRD
from graficas import graficaInPaqsUni
from graficas import graficaInPaqsIPv4
from graficas import graficaOutMsjICMP
from graficas import graficaInSeg
from graficas import graficaOutDatagram
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from os import remove
import time
import rrdtool
import threading

def pedirNumeroEntero():

    correcto = False
    num = 0
    while(not correcto):
        try:
            num = int(input("Introduzca un numero entero: "))
            correcto = True
        except ValueError:
            print("Error, introduzca un numero entero")

    return num

def leerArchivo():
    f = open('agentes.txt', 'r')
    contenido = f.read()
    f.close()
    return contenido

def alta():
    global stop_t
    stop_t = True
    global start_m
    start_m = True
    alias = input("Ingrese un alias para el dispositivo: ")
    ipHstName = input("Ingrese la dirección IP o el Hostname del dispositivo: ")
    versionSNMP = input("Ingrese la versión de SNMP: ")
    comunidad = input("Ingrese el nombre de la comunidad: ")
    f = open('agentes.txt', 'a')
    f.write(alias + ': ' + ipHstName + ' ' + versionSNMP + ' ' + comunidad + '\n')
    f.close()
    crearRRD(alias)

def listarAgentes(agentes):
    for x in range(len(agentes) - 1):
        print(x+1,") " + agentes[x])

def baja(agentes):
    global stop_t
    stop_t = True
    global start_m
    start_m = True
    listarAgentes(agentes)
    print("Seleccione la opción que desea eliminar")
    num = pedirNumeroEntero()
    alias = agentes[num-1].split()[0][:-1]
    agentes.pop(num-1)
    contenidoNuevo = ""
    for e in agentes:
        if(e != ''):
            contenidoNuevo += e + '\n'
    f = open('agentes.txt', 'w')
    f.write(contenidoNuevo)
    f.close()
    remove(alias + ".rrd")
    try:
        remove("inPaqsUni_" + alias + ".png")
        remove("inPaqsIPv4_" + alias + ".png")
        remove("outMsjICMP_" + alias + ".png")
        remove("inSeg_" + alias + ".png")
        remove("outDatagram_" + alias + ".png")
    except ValueError:
        print("No hay reportes por eliminar")

def listarInterfaces(numInterfaces, comunidad, ipHstName):
    for k in range(1, numInterfaces+1):
        descripcion = descInterfaces(comunidad, ipHstName, k)
        if("0x" in descripcion):
            try:
                descripcion = bytes.fromhex(descripcion.split("0x")[1])
                descripcion = descripcion.decode("ascii")
                print("\t" + str(k) + ") Descripcion: " + descripcion);
            except ValueError:
                print("\t" + str(k) + ") Descripcion: " + descripcion)
        else:
            print("\t" + str(k) + ") Descripcion: " + descripcion)
        estadoAdm = "Estado administrativo: "
        estado = int(consultaSNMP(comunidad, ipHstName, "1.3.6.1.2.1.2.2.1.7." + str(k)))
        if(estado == 1):
            estadoAdm += "Up"
        elif(estado == 2):
            estadoAdm += "Down"
        else:
            estadoAdm += "Testing"
        print("\tEstado de la interfaz: " + estadoAdm)

def obtenerNumInterfaces(comunidad, ipHstName):
    return int(consultaSNMP(comunidad, ipHstName, "1.3.6.1.2.1.2.1.0"))

def resumenAgente(agente, numAgente):
    info = agente.split()
    alias = info[0][:-1]
    comunidad = info[3]
    ipHstName = info[1]
    #version = info[2]
    print('\n', numAgente+1,") " + alias)
    print("Estado: " + conectividad(comunidad, ipHstName))
    numInterfaces = obtenerNumInterfaces(comunidad, ipHstName)
    print("Numero de interfaces: ", numInterfaces)
    listarInterfaces(numInterfaces, comunidad, ipHstName)


def updateRRD(comunidad, ipHstName, interfaz, alias):
    while 1:
        total_inPaqsUni = int(
            consultaSNMP(comunidad, ipHstName,
                         '1.3.6.1.2.1.2.2.1.11.' + str(interfaz)))
        total_inPaqsIPv4 = int(
            consultaSNMP(comunidad, ipHstName,
                         '1.3.6.1.2.1.4.3.0'))
        total_outMsjICMP = int(
            consultaSNMP(comunidad, ipHstName,
                         '1.3.6.1.2.1.5.21.0'))
        total_inSeg = int(
            consultaSNMP(comunidad, ipHstName,
                         '1.3.6.1.2.1.2.2.1.10.' + str(interfaz)))
        total_outDatagram = int(
            consultaSNMP(comunidad, ipHstName,
                         '1.3.6.1.2.1.7.1.0'))

        valor = "N:" + str(total_inPaqsUni) + ':' + str(total_inPaqsIPv4) + ':' + str(total_outMsjICMP) + ':' + str(total_inSeg) + ':' + str(total_outDatagram)
        rrdtool.update(alias + '.rrd', valor)
        time.sleep(1)
        global stop_t
        if(stop_t):
            global start_m
            start_m = True
            break

def iniciarMonitoreo(agente):
    global stop_t
    stop_t = False
    info = agente.split()
    alias = info[0][:-1]
    comunidad = info[3]
    ipHstName = info[1]
    print("Seleccione la interfaz que desea monitorear del agente " + alias)
    num = pedirNumeroEntero()
    t = threading.Thread(target = updateRRD, args = [comunidad, ipHstName, num, alias])
    t.start()

def crearGraficas(agentes):
    listarAgentes(agentes)
    print("Seleccione la opción que desea reportar")
    num = pedirNumeroEntero()
    alias = agentes[num-1].split()[0][:-1]
    """graficaInPaqsUni(alias)
    graficaInPaqsIPv4(alias)
    graficaOutMsjICMP(alias)
    graficaInSeg(alias)
    graficaOutDatagram(alias)"""
    c = canvas.Canvas("reporte_" + alias + ".pdf")
    #595.2 de ancho y 841.8 de alto
    #showPage() para terminar con una hoja
    #x,y (0,0) empieza en esquina inferior izquierda
    text = c.beginText(200, 800)
    text.setFont("Helvetica-Bold", 16)
    text.textLine("Reporte del agente " + alias)
    c.drawText(text)
    imgInPaqsUni = ImageReader("inPaqsUni_" + alias + ".png")
    imgInPaqsUni_w, imgInPaqsUni_h = imgInPaqsUni.getSize()
    altura = 790 - imgInPaqsUni_h
    c.drawImage(imgInPaqsUni, 50, altura)

    imgInPaqsIPv4 = ImageReader("inPaqsIPv4_" + alias + ".png")
    imgInPaqsIPv4_w, imgInPaqsIPv4_h = imgInPaqsIPv4.getSize()
    altura -= 10
    altura -= imgInPaqsIPv4_h
    c.drawImage(imgInPaqsIPv4, 50, altura)

    imgOutMsjICMP = ImageReader("outMsjICMP_" + alias + ".png")
    imgOutMsjICMP_w, imgOutMsjICMP_h = imgOutMsjICMP.getSize()
    altura -= 10
    altura -= imgOutMsjICMP_h
    c.drawImage(imgOutMsjICMP, 50, altura)

    c.showPage()

    imgInSeg = ImageReader("inSeg_" + alias + ".png")
    imgInSeg_w, imgInSeg_h = imgInSeg.getSize()
    altura = 790 - imgInSeg_h
    c.drawImage(imgInSeg, 50, altura)

    imgOutDatagram = ImageReader("outDatagram_" + alias + ".png")
    imgOutDatagram_w, imgOutDatagram_h = imgOutDatagram.getSize()
    altura -= 10
    altura -= imgOutDatagram_h
    c.drawImage(imgOutDatagram, 50, altura)

    c.save()

salir = False
opcion = 0
start_m = True
stop_t = False
while not salir:

    #fecha = (7821%3)+1
    #print(fecha)

    contenido = leerArchivo()
    numAgentes = contenido.count('\n')
    agentes = contenido.split('\n')
    print('\nNúmero de dispositivos registrados', numAgentes,'\n')
    for x in range(len(agentes) - 1):
        resumenAgente(agentes[x], x)
        if(start_m):
            iniciarMonitoreo(agentes[x])
    start_m = False

    print ("Elige una opcion\n")

    print ("1. Alta")
    print ("2. Baja")
    print ("3. Reporte")
    print ("4. Salir\n")

    opcion = pedirNumeroEntero()

    if opcion == 1:
        alta()
    elif opcion == 2:
        baja(agentes)
    elif opcion == 3:
        crearGraficas(agentes)
        #stop = True
    elif opcion == 4:
        stop_t = True
        salir = True
    else:
        print ("Introduce un numero entre 1 y 4")

print ("Fin")
