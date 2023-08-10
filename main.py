import cv2
import time
import os
import win32api
import configparser
import ctypes
import subprocess
import pyautogui

def load_settings():
    print("Einstellungen werden geladen...")
    config = configparser.ConfigParser()
    config.read('settings.ini')
    defaults = {
        'NoFaceDuration': 5,
        'InactivityDuration': 60,
        'LockMethod': 'Both'
    }
    try:
        # Validate and load configurations
        NoFaceDuration = int(config.get('SETTINGS', 'NoFaceDuration', fallback=defaults['NoFaceDuration']))
        InactivityDuration = int(config.get('SETTINGS', 'InactivityDuration', fallback=defaults['InactivityDuration']))
        LockMethod = config.get('SETTINGS', 'LockMethod', fallback=defaults['LockMethod'])

        assert LockMethod in ['Face', 'Both', 'Inactivity'], "Ungültige LockMethod in den Einstellungen. Nur 'Face', 'Incativity' oder 'Both' sind valide!"
        
        settings = {
            'NoFaceDuration': NoFaceDuration,
            'InactivityDuration': InactivityDuration,
            'LockMethod': LockMethod
        }
        print("Einstellungen erfolgreich geladen.")
        return settings
    except AssertionError as ae:
        print(f"Konfigurationsfehler: {ae}")
        print("Default Fallback Einstellungen werden geladen.")
        return defaults
    except Exception as e:
        print(f"Fehler beim Laden der Einstellungen: {e}")
        print("Default Fallback Einstellungen werden geladen.")
        return defaults

settings = load_settings()

# Global variable to keep track of the last time the screen was locked
last_locked_time = None


def is_workstation_locked():
    '''Return True if the workstation is locked, else False.'''
    try:
        user32 = ctypes.windll.User32
        if not hasattr(user32, "GetForegroundWindow"):
            print("GetForegroundWindow method not available.")
            return False  # Conservatively assume not locked if we can't detect
        return user32.GetForegroundWindow() == 0
    except Exception as e:
        print(f"Error checking if workstation is locked: {e}")
        return False  # Conservatively assume not locked if we encounter an error


def lock_screen():
    global last_locked_time
    current_time = time.time()

    if not is_workstation_locked():
        if last_locked_time is None or (current_time - last_locked_time) > 10:
            
            # Method 1: os.system
            try:
                print("Versuche mit os.system zu sperren...")
                result = os.system('rundll32.exe user32.dll,LockWorkStation')
                if result == 0:
                    print("Versuch, mit os.system zu sperren abgeschlossen.")
                    time.sleep(1)
            except Exception as e:
                print(f"Unexpected error while using os.system: {e}")

            # Method 2: ctypes
            if not is_workstation_locked():
                try:
                    print("Versuche mit ctypes.windll.user32.LockWorkStation zu sperren...")
                    ctypes.windll.user32.LockWorkStation()
                    print("Versuch, mit ctypes.windll.user32.LockWorkStation zu sperren ist abgeschlossen.")
                    time.sleep(1)
                except Exception as e:
                    print(f"Unexpected error while using ctypes: {e}")

            # Method 3: subprocess
            if not is_workstation_locked():
                try:
                    print("Versuche mit subprocess zu sperren...")
                    subprocess.run(['rundll32.exe', 'user32.dll,LockWorkStation'], check=True)
                    print("Versuch, mit subprocess zu sperren abgeschlossen.")
                    time.sleep(1)
                except Exception as e:
                    print(f"Unexpected error while using subprocess: {e}")

            # Method 4: pyautogui
            if not is_workstation_locked():
                try:
                    print("Versuche mit pyautogui zu sperren...")
                    # Using the Windows+L shortcut to lock the workstation
                    pyautogui.hotkey('win', 'l')
                    print("Versuch, mit pyautogui zu sperren abgeschlossen.")
                    time.sleep(1)
                except Exception as e:
                    print(f"Unexpected error while using pyautogui: {e}")

            if is_workstation_locked():
                last_locked_time = current_time

def get_last_input():
    try:
        '''Returns the elapsed time in seconds since the last input event.'''
        millis_since_start = win32api.GetTickCount()  # current tick count
        millis_since_last_input = millis_since_start - win32api.GetLastInputInfo() 
        return millis_since_last_input / 1000  # convert to seconds
    except Exception as e:
        print(f"Fehler beim Abrufen der letzten Eingabe: {e}")
        return float('inf')  # Return a very large value, so it won't affect the logic

def get_available_cameras(max_cameras=10):
    """Returns a list of available camera indices."""
    available_cameras = []
    for i in range(max_cameras):
        cap = cv2.VideoCapture(i)
        if cap is None or not cap.isOpened():
            cap.release()
        else:
            available_cameras.append(i)
            cap.release()
    if len(available_cameras) == 0:
        print("Keine Kameras verfügbar.")
    return available_cameras

def main():
    try:
        if settings['LockMethod'] in ['Face', 'Both']:
            print("Lade Gesichts-erkennungs Model.")
            face_cascade = cv2.CascadeClassifier('models/haarcascade_frontalface_default.xml')
            print("Model geladen.")
        else:
            face_cascade = None

        print("Kameras werden erkannt...")
        available_cameras = get_available_cameras()
        num_cameras = len(available_cameras)
        if num_cameras == 0:
            print("Keine Kameras erkannt.")
            return

        print(f"{num_cameras} Kamera(s) gefunden. Verwende Kamera-Indices: {', '.join(map(str, available_cameras))}")

        # Open all available cameras
        caps = [cv2.VideoCapture(i) for i in available_cameras]

        no_face_detected_time = None
        elapsed_without_face = 0
        elapsed_inactivity = 0
        while True:
            try:
                if is_workstation_locked():
                    print("PC ist gesperrt")
                    elapsed_without_face = 0
                    elapsed_inactivity = 0
                    time.sleep(1)
                    continue
                current_time = time.time()
                
                all_faces = []  # This will store faces detected across all cameras
                for idx, cap in enumerate(caps):
                    if cap:
                        ret, frame = cap.read()
                        if ret:
                            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
                            all_faces.extend(faces)
                            print(f"Kamera {idx}: {len(faces)} Gesicht(er) erkannt.")
                        else:
                            print(f"Fehler bei der Kamera {idx}: Bild konnte nicht abgerufen werden.")
                            cap.release()
                            del caps[idx]


                elapsed_inactivity = get_last_input()
                if (elapsed_inactivity > 2.00):
                    print(f"Inaktivität: {elapsed_inactivity:.2f} Sekunden.")
                
                if len(all_faces) == 0 and (settings['LockMethod'] == 'Face' or settings['LockMethod'] == 'Both'):
                    if no_face_detected_time is None:
                        no_face_detected_time = current_time
                    elapsed_without_face = current_time - no_face_detected_time
                    if (elapsed_without_face > 2.00):
                        print(f"Kein Gesicht erkannt für: {elapsed_without_face:.2f} Sekunden.")
                else:
                    no_face_detected_time = None

                # Lock Method: Inactivity
                if settings['LockMethod'] == 'Inactivity' and elapsed_inactivity > settings['InactivityDuration']:
                    print("Inaktivität erkannt. Versuche, den Bildschirm zu sperren...")
                    lock_screen()

                # Lock Method: Face
                elif settings['LockMethod'] == 'Face' and len(all_faces) == 0:
                    if no_face_detected_time is None:
                        no_face_detected_time = current_time
                    elif elapsed_without_face >= settings['NoFaceDuration']:
                        print("Keine Gesichtserkennung für die festgelegte Dauer. Versuche, den Bildschirm zu sperren...")
                        lock_screen()
                        no_face_detected_time = None

                # Lock Method: Both
                elif settings['LockMethod'] == 'Both' and len(all_faces) == 0 and elapsed_inactivity > settings['InactivityDuration']:
                    if no_face_detected_time is None:
                        no_face_detected_time = current_time
                    elif elapsed_without_face >= settings['NoFaceDuration']:
                        print("Inaktivität und kein Gesicht erkannt. Versuche, den Bildschirm zu sperren...")
                        lock_screen()
                        no_face_detected_time = None

                # If faces are detected, reset the no_face_detected_time counter
                if len(all_faces) > 0:
                    no_face_detected_time = None

                # Check if the user pressed the 'q' key
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print("Beendigungsbefehl (Q-Taste) empfangen.")
                    break

                time.sleep(0.5)
            except cv2.error as e:
                print(f"OpenCV-Fehler: {e}")
            except Exception as e:
                print(f"Unbekannter Fehler: {e}")
        for cap in caps:
            cap.release()
        print("Alle Kameras freigegeben.")
        if face_cascade:
            cv2.destroyAllWindows()
            print("Alle OpenCV-Fenster geschlossen.")
    except Exception as e:
        print(f"Unbekannter Fehler: {e}")
if __name__ == "__main__":
    try:
        print("Starte das Gesichtserkennungs- und Sperrprogramm.")
        main()
    except KeyboardInterrupt:
        print("Benutzer hat das Programm beendet.")
    except Exception as e:
        print(f"Ein kritischer Fehler ist aufgetreten: {e}")
    finally:
        print("Beende das Gesichtserkennungs- und Sperrprogramm.")