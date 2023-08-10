# Screen Locker 🛡️

**Platform:** Windows Only.

**Description:** Automatically lock your PC using I/O activity and facial recognition to ensure security when you're not actively present.

## How I Came Up With This
In my role overseeing internal IT security at my company, I noticed several unlocked PCs. As a playful reminder of the importance of security, I would use their Microsoft Teams to announce they owed the office cake or other treats. However, rather than relying on manual locking, I developed this tool to automatically detect and lock the computer when no one is present.

## Building The Executable
To create a new executable, run:
\```bash
pyinstaller app.spec
\```

**Note:** The application displays messages in German.

## To-Do List:
- [ ] Run on startup
- [ ] Suppress command window
- [ ] Operate as a service
- [ ] Taskbar integration: right-click to display logs, enable/disable, restart, access settings.
