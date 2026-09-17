#!/usr/bin/env python3
"""
Script de diagnostic pour identifier le cablage reel du clavier matriciel.
Teste chaque broche GPIO une par une pour reperer quelle ligne/colonne reagit.

Ne fait AUCUNE hypothese sur l'ordre des fils : teste toutes les combinaisons
possibles de 8 broches GPIO consecutives et affiche ce qui se passe quand
vous appuyez sur une touche.
"""

import RPi.GPIO as GPIO
import time

# Les 8 broches sur lesquelles le clavier est branche (dans l'ordre physique
# ou vous les avez cablees). Modifiez cette liste si besoin selon votre cablage reel.
BROCHES = [5, 6, 13, 19, 12, 16, 20, 21]

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

print("=== Test du clavier matriciel ===")
print(f"Broches testees (BCM) : {BROCHES}")
print("Appuyez sur n'importe quelle touche du clavier plusieurs fois.")
print("Ctrl+C pour arreter.\n")

try:
    while True:
        # On met toutes les broches en entree avec pull-up, sauf une a la fois
        # qu'on met en sortie a LOW, pour voir laquelle des autres broches
        # detecte un signal LOW quand une touche est appuyee.
        for i, broche_sortie in enumerate(BROCHES):
            GPIO.setup(BROCHES, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.setup(broche_sortie, GPIO.OUT)
            GPIO.output(broche_sortie, GPIO.LOW)
            time.sleep(0.005)

            for j, broche_entree in enumerate(BROCHES):
                if broche_entree == broche_sortie:
                    continue
                if GPIO.input(broche_entree) == GPIO.LOW:
                    print(f"Touche detectee : sortie=GPIO{broche_sortie} (position {i}) "
                          f"<-> entree=GPIO{broche_entree} (position {j})")

except KeyboardInterrupt:
    print("\nArret.")
finally:
    GPIO.cleanup()
