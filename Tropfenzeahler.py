# Tropfenzähler Python-Code Vorlage

# Bibliothek einfügen (noch die Bibliothek von den Sensoren und LCD-Display einfügen).
import RPi.GPIO as gpio
import time
from datetime import datetime


#-------------------------------------------------------------------------------------
# Grundkonfiguration
#-------------------------------------------------------------------------------------
gpio.setmode(gpio.BCM)

# Pins (Platzhalter, bitte anpassen)
# Auf möglich, anstatt BUTTON => BTN

PIN_Sensor = 1000
PIN_LED_GRUEN = 20000
PIN_LED_GELB = 30000
PIN_LED_ROT = 40000
BUTTON_UP = 50000
BUTTON_DOWN = 60000
BUTTON_START = 70000
BUTTON_STOPP = 8000

# Achtung LCD Display (Neu erstellen, nur Pseudocode!!!)
def lcd_ausgabe(zeile1 = "", zeile2 = ""):
    print(f"LCD: {zeile1} | {zeile2}")
    

# Pinseinstellungen
gpio.setup(PIN_Sensor, gpio.IN, pull_up_down=gpio.PUD_UP)
gpio.setmode(PIN_LED_GRUEN, gpio.OUT)
gpio.setmode(PIN_LED_GELB, gpio.OUT)
gpio.setmode(PIN_LED_ROT, gpio.OUT)

for pin in [BUTTON_UP, BUTTON_DOWN, BUTTON_START, BUTTON_START]:
    gpio.setup(pin, gpio.IN, pull_up_down=gpio.PUD_UP)
    
# Globale Variable
gezählt = 0
gewuenschte_zahl = None
laeuft = False
logfile = "Tropfen_log.txt"


# Hilfsfunktion
def event_log(message):
    # Schreibt Ergebnis ins Logfile mit Datum & Uhrzeit
    with open(logfile, "a") as f:
        f.write(f"{datetime.now().strftime('%y -%m -%d &H:%M:%S')} - {message}\n")
        
def reset_leds():
    gpio.output(PIN_LED_GRUEN, False)
    gpio.output(PIN_LED_GELB, False)
    gpio.output(PIN_LED_ROT, False)
    
    
# Tropfenerkennung
def sensor_callback(channel):
    global gezählt, gewuenschte_zahl, laeuft
    
    if laeuft:
        count += 1
        event_log(f"Tropfen erkannt, Gesamt: {gezählt}")
        lcd_ausgabe(f"Anzahl: {gezählt}", "")
        
        if gewuenschte_zahl:
            if gezählt < gewuenschte_zahl - 3:
                gpio.output(PIN_LED_GELB, True)
            elif gezählt == gewuenschte_zahl - 3:
                lcd_ausgabe(f"Anzahl: {gezählt}", "Achtung, Tropfenanzahl fast erreicht!")
                gpio.output(PIN_LED_GELB, True)
            elif gezählt == gewuenschte_zahl:
                reset_leds()
                gpio.output(PIN_LED_GRUEN, True)
                lcd_ausgabe(f"Anzahl: {gezählt}", "Fertig!")
            elif count > gewuenschte_zahl:
                reset_leds()
                gpio.output(PIN_LED_ROT, True)
                print(f"Überschreitung: {gezählt}, es wurden {gezählt-gewuenschte_zahl} überschritten.")
                
# Interrupt für Sensor
gpio.add_event_detect(PIN_Sensor, gpio.FALLING, callback=sensor_callback, bouncetime=200)

# Konfiguration der Knöpfe
def warten_auf_button():
    global gezählt, gewuenschte_zahl, laeuft
    
    while True:
            # Start Button
        if gpio.input(BUTTON_START) == gpio.LOW and not laeuft:
            laeuft = True
            gezählt = 0
            lcd_ausgabe("Zählung gestartet", "Anzahl: 0")
            event_log("Zählung gestartet")
            time.sleep(0.5)
                            
            # Stop Button
        if gpio.input(BUTTON_START) == gpio.LOW and laeuft:
            laeuft = False
            lcd_ausgabe("Zählung beendet", f"Endstand: {gezählt}")
            event_log(f"Zählung beendet bei {gezählt}")
            time.sleep(0.5)

        # Reset Button (erneut drücken)
        if gpio.input(BUTTON_STOPP) == gpio.LOW and not laeuft:
            gezählt = 0
            gewuenschte_zahl = None
            reset_leds()
            lcd_ausgabe("Reset", "")
            event_log("System Reset")
            time.sleep(0.5)

        # Zielwert erhöhen/verringern (nur wenn Zählung nicht läuft)
        if not laeuft:
            if gpio.input(BUTTON_UP) == gpio.LOW:
                if gewuenschte_zahl is None:
                    gewuenschte_zahl = 0
                gewuenschte_zahl += 1
                lcd_ausgabe("Ziel gesetzt", f"{gewuenschte_zahl} Tropfen")
                time.sleep(0.3)

            if gpio.input(BUTTON_DOWN) == gpio.LOW:
                if gewuenschte_zahl is None:
                    gewuenschte_zahl = 0
                gewuenschte_zahl = max(0, gewuenschte_zahl - 1)
                lcd_ausgabe("Ziel gesetzt", f"{gewuenschte_zahl} Tropfen")
                time.sleep(0.3)

        time.sleep(0.05)

# ---------------------------------------------------------
# Main Loop
# ---------------------------------------------------------
try:
    lcd_ausgabe("Bereit", "Drücke Start")
    warten_auf_button()

except KeyboardInterrupt:
    print("Programm beendet")

finally:
    gpio.cleanup()