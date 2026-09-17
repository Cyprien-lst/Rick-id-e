#!/usr/bin/env python3
"""
Test brut du bouton (SW) d'un module joystick.
Affiche la valeur lue en continu (pas seulement au changement),
pour voir si le signal bouge du tout quand on appuie.
"""

import RPi.GPIO as GPIO
import time

BROCHE_SW = 27  # BCM, correspond a la pin physique 13

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(BROCHE_SW, GPIO.IN, pull_up_down=GPIO.PUD_UP)

print("=== Test brut du bouton joystick (GPIO27 / pin13) ===")
print("Valeur au repos attendue : 1 (HIGH). En appuyant, ca devrait passer a 0 (LOW).")
print("Ctrl+C pour arreter.\n")

try:
    while True:
        valeur = GPIO.input(BROCHE_SW)
        print(f"Valeur lue : {valeur}")
        time.sleep(0.5)
except KeyboardInterrupt:
    print("\nArret.")
finally:
    GPIO.cleanup()
