# WoW Faction Bypass / Background Auto-Clicker

A background enter-spammer to bypass the World of Warcraft "Faction Currently Unavailable" (population imbalance) lock during character creation.

Instead of hijacking your mouse or keyboard like a basic macro, this script uses the Win32 API (`PostMessageW`) to send keystrokes directly to the WoW window. You can alt-tab, watch YouTube, or write code while the script fights the faction lock in the background.

## Setup

Requires Python 3. 
Install the required keyboard hook dependency:
```bash
pip install keyboard
```

## Usage

You must run this script as **Administrator** because the `keyboard` module requires global hook privileges in Windows to register the background hotkeys.

```bash
python wow_enter_spammer.py
```

**Hotkeys:**
* **F6** - Start / Pause spamming
* **F7** - Exit script completely

**Custom Delay:**
By default, it sends an input every 500ms. You can adjust this via arguments:
```bash
python wow_enter_spammer.py --delay 300
```

## Disclaimer
Automating inputs violates Blizzard's ToS. Use at your own risk.
