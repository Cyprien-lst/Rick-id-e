#!/usr/bin/env python3
"""
Pipeline RickLab - IA locale defaillante
Bouton joystick (GPIO17) -> enregistrement -> Vosk -> Gemini (persona) -> Piper -> haut-parleur
"""

import subprocess
import sounddevice as sd
import soundfile as sf
import json
import os
import time
import random
import traceback
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
import RPi.GPIO as GPIO
from vosk import Model, KaldiRecognizer
from generateur_gemini import generer_reponse
from generateur_reponses import generer_reponse as generer_reponse_scripte

VOSK_MODEL_PATH = os.path.expanduser("~/model-fr")
PIPER_BIN = os.path.expanduser("~/ricklab-env/bin/piper")
PIPER_MODEL_PATH = os.path.expanduser("~/ricklab/fr_FR-tom-medium.onnx")
AUDIO_OUTPUT_DEVICE = "plughw:0,0"

RECORD_SECONDS = 5
SAMPLE_RATE = 16000

# Note : on cree un NOUVEAU ThreadPoolExecutor a chaque appel plutot que
# d'en reutiliser un seul en permanence. Sinon, si un appel Gemini reste
# bloque indefiniment (ex: reseau instable juste apres un redemarrage),
# le meme "thread" reste occupe pour toujours et TOUS les appels suivants
# restent coinces derriere lui, sans jamais vraiment demarrer.


def generer_reponse_avec_timeout(texte, timeout=10):
    executor = ThreadPoolExecutor(max_workers=1)
    future = executor.submit(generer_reponse, texte)
    try:
        return future.result(timeout=timeout)
    except FuturesTimeoutError:
        print(f"[Gemini trop long (> {timeout}s), bascule sur le mode scripte]")
        return generer_reponse_scripte(texte)
    finally:
        # On ne bloque pas en attendant que le thread bloque se termine :
        # on l'abandonne (il finira orphelin si vraiment bloque, mais ca
        # ne genera plus les appels suivants).
        executor.shutdown(wait=False)

BROCHE_BOUTON = 17  # BCM, correspond a la pin physique 11

# Le modele Vosk est charge UNE SEULE FOIS au demarrage du script,
# car le chargement est lent (peut prendre jusqu'a 1 minute au premier
# lancement / juste apres un redemarrage). Le recharger a chaque
# interaction rendait le pipeline tres lent.
print("[Chargement du modele Vosk...]")
MODELE_VOSK = Model(VOSK_MODEL_PATH)
print("[Modele Vosk pret]")


def enregistrer_audio(chemin_wav="entree.wav"):
    print(f"[Enregistrement de {RECORD_SECONDS}s... parlez maintenant]")
    audio = sd.rec(int(RECORD_SECONDS * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype="int16")
    sd.wait()
    sf.write(chemin_wav, audio, SAMPLE_RATE)
    return chemin_wav


def transcrire_audio(chemin_wav):
    rec = KaldiRecognizer(MODELE_VOSK, SAMPLE_RATE)
    with open(chemin_wav, "rb") as f:
        f.read(44)
        while True:
            data = f.read(4000)
            if len(data) == 0:
                break
            rec.AcceptWaveform(data)
    resultat = json.loads(rec.FinalResult())
    return resultat.get("text", "")


def parler(texte, chemin_wav="reponse.wav"):
    if os.path.exists(chemin_wav):
        os.remove(chemin_wav)

    resultat_piper = subprocess.run(
        [PIPER_BIN, "--model", PIPER_MODEL_PATH, "--output_file", chemin_wav],
        input=texte, text=True,
        capture_output=True
    )

    if resultat_piper.returncode != 0:
        print(f"[ERREUR Piper] {resultat_piper.stderr}")
        return

    if not os.path.exists(chemin_wav) or os.path.getsize(chemin_wav) == 0:
        print("[ERREUR] Piper n'a pas genere de fichier audio valide.")
        return

    # Traitement sox pour le grain de voix "Rick" : pitch grave + legere
    # distorsion, avec un peu de variation aleatoire a chaque reponse
    # pour un effet plus instable / vivant qu'un reglage toujours identique.
    chemin_wav_traite = "reponse_traitee.wav"
    pitch = random.randint(-110, -70)
    tempo = round(random.uniform(1.0, 1.1), 2)
    overdrive = random.randint(4, 9)

    resultat_sox = subprocess.run(
        ["sox", chemin_wav, chemin_wav_traite,
         "pitch", str(pitch), "tempo", str(tempo), "overdrive", str(overdrive)],
        capture_output=True, text=True
    )

    chemin_final = chemin_wav_traite if resultat_sox.returncode == 0 else chemin_wav
    if resultat_sox.returncode != 0:
        print(f"[ERREUR sox, on joue la voix sans effet] {resultat_sox.stderr}")

    resultat_aplay = subprocess.run(
        ["aplay", "-D", AUDIO_OUTPUT_DEVICE, chemin_final],
        capture_output=True, text=True
    )
    if resultat_aplay.returncode != 0:
        print(f"[ERREUR aplay] {resultat_aplay.stderr}")


def traiter_une_interaction():
    try:
        wav_entree = enregistrer_audio()
        texte = transcrire_audio(wav_entree)
        print(f"[Vous avez dit] {texte}")

        if not texte.strip():
            print("[Rien entendu]")
            return

        reponse = generer_reponse_avec_timeout(texte)
        print(f"[Reponse generee] {reponse}")

        parler(reponse)

    except Exception as e:
        print(f"[ERREUR inattendue] {e}")
        traceback.print_exc()


def boucle_principale():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(BROCHE_BOUTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    print("=== RickLab IA - pret. Appuyez sur le bouton joystick pour parler. ===")

    bouton_precedent = GPIO.HIGH

    try:
        while True:
            etat_bouton = GPIO.input(BROCHE_BOUTON)

            # Detection du front descendant (HIGH -> LOW = bouton presse)
            if bouton_precedent == GPIO.HIGH and etat_bouton == GPIO.LOW:
                time.sleep(0.05)  # anti-rebond simple
                if GPIO.input(BROCHE_BOUTON) == GPIO.LOW:
                    traiter_une_interaction()
                    # On attend le relachement avant de continuer, pour eviter
                    # de relancer plusieurs fois pour un seul appui.
                    while GPIO.input(BROCHE_BOUTON) == GPIO.LOW:
                        time.sleep(0.05)

            bouton_precedent = etat_bouton
            time.sleep(0.02)

    except KeyboardInterrupt:
        print("\nArret du pipeline.")
    finally:
        GPIO.cleanup()


if __name__ == "__main__":
    boucle_principale()
