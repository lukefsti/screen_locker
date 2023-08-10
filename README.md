# Screen Locker 🛡️

**Platform:** Windows Only.

**Description:** Automatically lock your PC using I/O activity and facial recognition to ensure security when you're not actively present.

## How I Came Up With This
In my role overseeing internal IT security at my company, I noticed several unlocked PCs. As a playful reminder of the importance of security, I would use their Microsoft Teams to announce they owed the office cake or other treats. However, rather than relying on manual locking, I developed this tool to automatically detect and lock the computer when no one is present.

## How It Works

The Screen Locker application primarily uses two methods to decide whether to lock your computer:

1. **Inactivity Detection:** It monitors user input (keyboard and mouse) to determine inactivity. If there's no user input for a specified duration, it considers the workstation to be inactive and triggers the locking process.

2. **Facial Recognition:** The application scans for available cameras and uses them to detect any face(s). If no face is detected for a certain duration, it locks the workstation.

The application attempts multiple methods to lock the workstation, including `os.system`, `ctypes`, `subprocess`, and `pyautogui`.

**Settings Configuration:** You can configure settings like the `NoFaceDuration`, `InactivityDuration`, and the locking method (`Face`, `Inactivity`, or `Both`) using the `settings.ini` file. By default, if there's an issue with the settings, the application reverts to a predefined default configuration.

The application provides feedback via console logs, primarily in German.

## Building The Executable
To create a new executable, run:
```bash
pyinstaller app.spec

## To-Do List:
- [ ] Run on startup
- [ ] Suppress command window
- [ ] Operate as a service
- [ ] Taskbar integration: right-click to display logs, enable/disable, restart, access settings.
