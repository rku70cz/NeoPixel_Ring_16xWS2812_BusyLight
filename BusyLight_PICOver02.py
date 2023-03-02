# ---------------------------------------------------------------------
# BusyLight_PICOver02.py
# ======================
#
# Druha,jednoducha ukazka reseni "BusyLight" za pouziti desky Raspberry
# Pi Pico. Jako svetelny majak pouzit prouzek 8-mi RGB LED WS2812B.Ovla
# dani pomoci dvou tlacitek. Jako sirena pouzit aktivni bzucak.
#
# tlacitko 1.      GP16   prepinani BUSY OFF/ON (zelena/cervena)
# tlacitko 2.      GP17   privolavaci PANIC MODE (stridave cervena+mod-
#                         ra+zvukove znameni na modre)
# aktivni bzucak   GP18   spinani bzucaku resp. "piskatka"
#
# *Sestaveno za pouziti ukazek a trid dostupnych v repozitarich GitHub
# https://github.com/benevpi/pico_python_ws2812b
# https://github.com/blaz-r/pi_pico_neopixel
#
# *Ceske komentare zdrojoveho kodu  (Czech comments of the source code)
# 
# vytvoreno:       28.02.2023 (RKu70cz)
# verze:           1.00
# posledni uprava: 28.02.2023 (RKu70cz)
#
# (c) 2022, RKu70cz
# ---------------------------------------------------------------------

from machine import Pin
import time
import ws2812b

#
# metoda "RingOFF"
#         =======
#
# Zhasne vsechny diody LED pasku resp. nastavi na nich cernou barvu
#
def RingOFF():
    ring.fill( BLACK[0],BLACK[1],BLACK[2] )
    ring.show()
    time.sleep(0.5)

#
# metoda "busyON"
#         =======
#
# Vsechny diody LED pasku postupne rozsviti cervene
#
def busyON():
    RingOFF()    
    for i in range(numLEDs):
        ring.set_pixel(i, RED[0], RED[1], RED[2])
        time.sleep(0.01)
        ring.show()

#
# metoda "busyOFF"
#         ========
#
# Vsechny diody LED pasku postupne rozsviti zelene
#    
def busyOFF():
    RingOFF()
    for i in range(numLEDs):
        ring.set_pixel(i, GREEN[0], GREEN[1], GREEN[2])
        time.sleep(0.01)
        ring.show()

#
# metoda "PanicMODE"
#         =========
#
# Jednorazove provede zmenu barvy LEDek na pasku na modrou a pak cerve-
# nou. Zaroven na dobu zobrazeni modre spusti bzucak.
#
# *protoze me neslo obslouzit pres timer (problem pri jeho deaktivaci)
# tak reseno jednoduse pres odpocitavani v hlavni smycce, ktera ma mo-
# mentalne cyklus 0,5s
#
def PanicMODE():
    ring.fill( BLUE[0],BLUE[1],BLUE[2] )
    ring.show()
    buzz.toggle()
    time.sleep(0.5)

    ring.fill( RED[0],RED[1],RED[2] )
    ring.show()
    buzz.toggle()
    time.sleep(0.5)
    
numLEDs = 8               # pocet LEDek pasku
ws2812bDATApin = 22       # PIN, na ktery je napojen DATA INPUT prouzku resp. kruhu

RED = (255, 0, 0)         # definice barev v RGB pro dalsi snadne pouziti
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)   # bila, zatim nepouzita ...
BLACK = (0, 0, 0)         # cerna, vlastne zhasnuto 

COLORS = (RED, GREEN, BLUE, WHITE, BLACK)

# pocatecni inicializace GPIO
bttn1 = Pin(16, Pin.IN)   # PIN, na ktere je pripojeno tlacitko 1. - prepinani BUSY OFF/ON (zelena/cervena)
bttn2 = Pin(17, Pin.IN)   # PIN, na ktere je pripojeno tlacitko 2. - aktivace PANIC MODu

buzz = Pin(18, Pin.OUT)   # PIN, na kterem je zapojeno ovladani aktivniho bzucaku

# objekt LED pasku resp. ringu
ring = ws2812b.ws2812b(numLEDs, 0, ws2812bDATApin)
RingOFF()

# test prouzku resp. ringu (nastavi postupne vsechny vyse nadefinovane barvy)
for color in COLORS:
    for i in range(numLEDs):
        ring.set_pixel(i, color[0], color[1], color[2])
        time.sleep(0.01)
        ring.show()
    time.sleep(0.1)

busy = False             # priznak rezimu BUSY ON ( busy = True = CERVENA; jinak ZELENA )
panic = False            # priznak aktivace rezimu "PANIC MODE"; True = aktivni ( v tomto rezimu je take zaroven busy = True ) 

time.sleep(1)
busyOFF()

panicMCount = 0          # interne zaznamenavany pocet prubehu smycky - odpocitavani pro tzv. "PANIC MODE"
panicMFirst = True       # priznak prvniho prubehu smycky po aktivaci "PANIC MODE" 
panicMDelay = 20         # hodnota po jejimz dosazeni bude zvukovy a svetelny signal v "PANIC MODE"
                         # *smycka jede momentalne s periodou 0,5s
                         # *takto nastaveno je to vlastne 20 x 0,5s = kazdych 10s

# -------------------------
# HLAVNI (nekonecna) SMYCKA
# -------------------------
while True:

    b1 = bttn1.value()   # nacte stavy tlacitek do promennych ( uklada se 0 nebo 1 s tim, ze 1 je "stisknuto" )
    b2 = bttn2.value()   # *jedine misto kde se cte; zbytek kodu se ridi jiz jednom hodnotami v promennych b1, b2
                         # a pripadne ostatnimi pomocnymi priznaky ( busy, panic, panicMFirst, panicMDelay ... )
                         # *v kodu je zarizeno tak, ze tlacitko 1. ma vzdy prednost
    if b1:
        if panic:
            #print( "panic OFF" )
            panic = False
            busy = True
        else:
            if busy:
                busy = False
            else:
                busy = True
    elif b2:
        #print( "panic ON" )
        busy = True
        panic = True

    #print( panic )
    #print( busy )
    #print( "" )
    
    if b1:
        if busy:
            busyON()
        else:
            busyOFF()
    elif b2:
        if panic:
            panicMFirst = True
            panicMCount = 0

    if panic:
        if panicMFirst:
            panicMFirst = False
            PanicMODE()
        else:
            panicMCount = panicMCount + 1
            #print( panicMCount )
            if panicMCount >= panicMDelay:
                panicMCount = 0
                PanicMODE()
        time.sleep(0.5)
    else:
        time.sleep(0.5)
