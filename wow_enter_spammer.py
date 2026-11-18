"""
╔══════════════════════════════════════════════════════════════╗
║  WoW Character Creation Enter Spammer                        ║
║   — Faction Lock Buster                                      ║
║                                                              ║
║  Spamuje Enter do WoW okna, i kdyz neni v popredi.           ║
║  Hotkeys: F6 = Start/Stop | F7 = Exit                        ║
╚══════════════════════════════════════════════════════════════╝
"""

import ctypes
import ctypes.wintypes
import time
import threading
import sys
import keyboard

# ═══════════════════════════════════════════════════════════
# Win32 konstanty
# ═══════════════════════════════════════════════════════════
WM_KEYDOWN = 0x0100
WM_KEYUP   = 0x0101
VK_RETURN  = 0x0D  # Enter key

# Win32 API
user32 = ctypes.windll.user32
EnumWindows = user32.EnumWindows
GetWindowTextW = user32.GetWindowTextW
GetWindowTextLengthW = user32.GetWindowTextLengthW
IsWindowVisible = user32.IsWindowVisible
PostMessageW = user32.PostMessageW
GetForegroundWindow = user32.GetForegroundWindow
SetForegroundWindow = user32.SetForegroundWindow

WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.wintypes.HWND, ctypes.wintypes.LPARAM)

# ═══════════════════════════════════════════════════════════
# Konfigurace
# ═══════════════════════════════════════════════════════════
DELAY_MS = 500        # Delay mezi Enter stisky v ms (0.5s default)
HOTKEY_TOGGLE = "f6"  # Toggle start/stop
HOTKEY_EXIT = "f7"    # Ukonci program

# WoW window titulky — upravit pokud mas jiny nazev
WOW_TITLES = [
    "World of Warcraft",
    "Wow",
    "WoW",
]


class WoWEnterSpammer:
    """Hlavni trida spammeru — posila Enter do WoW okna pres PostMessage."""

    def __init__(self, delay_ms: int = DELAY_MS):
        self.delay_ms = delay_ms
        self.running = False
        self.alive = True
        self.wow_hwnd = None
        self.spam_thread = None
        self.total_sent = 0
        self.lock = threading.Lock()

    def find_wow_window(self) -> int | None:
        """Najde WoW okno prohledanim vsech viditelnych oken."""
        found_hwnd = None

        def enum_callback(hwnd, _lparam):
            nonlocal found_hwnd
            if not IsWindowVisible(hwnd):
                return True

            length = GetWindowTextLengthW(hwnd)
            if length == 0:
                return True

            buff = ctypes.create_unicode_buffer(length + 1)
            GetWindowTextW(hwnd, buff, length + 1)
            title = buff.value

            for wow_title in WOW_TITLES:
                if wow_title.lower() in title.lower():
                    found_hwnd = hwnd
                    return False  # Stop enumerating
            return True

        EnumWindows(WNDENUMPROC(enum_callback), 0)
        return found_hwnd

    def send_enter(self, hwnd: int) -> bool:
        """Posle Enter keystroke do okna pres PostMessage (funguje i na pozadi)."""
        try:
            # LPARAM pro Enter key: scan code 0x1C, extended = 0
            lparam_down = 0x001C0001  # repeat=1, scancode=0x1C
            lparam_up   = 0xC01C0001  # repeat=1, scancode=0x1C, release flags

            PostMessageW(hwnd, WM_KEYDOWN, VK_RETURN, lparam_down)
            time.sleep(0.02)  # Kratka pauza mezi down a up
            PostMessageW(hwnd, WM_KEYUP, VK_RETURN, lparam_up)
            return True
        except Exception:
            return False

    def spam_loop(self):
        """Hlavni smycka spammeru — bezi v separatnim threadu."""
        while self.alive:
            if not self.running:
                time.sleep(0.05)
                continue

            # Zkontroluj/najdi WoW okno
            if self.wow_hwnd is None:
                self.wow_hwnd = self.find_wow_window()
                if self.wow_hwnd is None:
                    self.print_status("⚠  WoW okno NENALEZENO — hledam znovu...")
                    time.sleep(1.0)
                    continue
                else:
                    self.print_status(f"✅ WoW okno nalezeno! HWND: {self.wow_hwnd}")

            # Posli Enter
            if self.send_enter(self.wow_hwnd):
                with self.lock:
                    self.total_sent += 1
                count = self.total_sent
                # Kazdejch 10 stiku update status
                if count % 10 == 0:
                    self.print_status(f"🔨 Odesláno {count} Enter kláves | Delay: {self.delay_ms}ms")
            else:
                # Okno mohlo zmizet, reset
                self.wow_hwnd = None
                self.print_status("⚠  Chyba při odesílání — hledám okno znovu...")

            time.sleep(self.delay_ms / 1000.0)

    def toggle(self):
        """Toggle spammer on/off."""
        self.running = not self.running
        if self.running:
            self.wow_hwnd = self.find_wow_window()
            if self.wow_hwnd:
                self.print_status(f"▶  SPAMMER ZAPNUT | WoW HWND: {self.wow_hwnd} | Delay: {self.delay_ms}ms")
            else:
                self.print_status("▶  SPAMMER ZAPNUT | ⚠ WoW okno zatím nenalezeno, hledám...")
        else:
            self.print_status(f"⏸  SPAMMER POZASTAVEN | Celkem odesláno: {self.total_sent}")

    def stop(self):
        """Ukonci spammer."""
        self.running = False
        self.alive = False
        self.print_status(f"⏹  SPAMMER UKONČEN | Celkem odesláno: {self.total_sent}")

    def print_status(self, msg: str):
        """Vypise status s timestampem."""
        ts = time.strftime("%H:%M:%S")
        print(f"  [{ts}] {msg}")

    def start(self):
        """Spusti spammer — hlavni entry point."""
        self.print_banner()

        # Spust spam thread
        self.spam_thread = threading.Thread(target=self.spam_loop, daemon=True)
        self.spam_thread.start()

        # Registruj hotkeys
        keyboard.on_press_key(HOTKEY_TOGGLE, lambda _: self.toggle(), suppress=False)
        keyboard.on_press_key(HOTKEY_EXIT, lambda _: self.stop(), suppress=False)

        self.print_status("Čekám na příkaz... Stiskni F6 pro start spammeru.")

        # Hlavni loop — ceka na ukonceni
        try:
            while self.alive:
                time.sleep(0.1)
        except KeyboardInterrupt:
            self.stop()

        print("\n  Nashle, frajeře.\n")

    def print_banner(self):
        """Vypise banner pri startu."""
        print()
        print("  ╔══════════════════════════════════════════════════════════╗")
        print("  ║     WoW Enter Spammer — Faction Lock Buster             ║")
        print("  ║                                                          ║")
        print("  ╠══════════════════════════════════════════════════════════╣")
        print(f" ║  Delay:        {self.delay_ms}ms mezi Entery            ║")
        print(f" ║  Toggle:       {HOTKEY_TOGGLE.upper()} (Start/Stop)     ║")
        print(f" ║  Exit:         {HOTKEY_EXIT.upper()} (Ukončit)          ║")
        print("  ║  Režim:        PostMessage (funguje i na pozadí)         ║")
        print("  ╠══════════════════════════════════════════════════════════╣")
        print("  ║  TIP: Launch WoW, go to a character creation screen,     ║")
        print("  ║       select a character, name and press F6.             ║")
        print("  ╚══════════════════════════════════════════════════════════╝")
        print()


def main():
    """Entry point — parsuje argumenty a spusti spammer."""
    delay = DELAY_MS

    # Jednoduchej arg parsing pro delay
    for i, arg in enumerate(sys.argv[1:], 1):
        if arg in ("--delay", "-d") and i < len(sys.argv) - 1:
            try:
                delay = int(sys.argv[i + 1])
            except ValueError:
                print(f"  ⚠ Neplatný delay: {sys.argv[i + 1]}, použiji default {DELAY_MS}ms")
                delay = DELAY_MS
        elif arg in ("--help", "-h"):
            print("  Použití: python wow_enter_spammer.py [--delay MS]")
            print(f"  Default delay: {DELAY_MS}ms")
            print(f"  Hotkeys: {HOTKEY_TOGGLE.upper()} = Toggle | {HOTKEY_EXIT.upper()} = Exit")
            sys.exit(0)

    spammer = WoWEnterSpammer(delay_ms=delay)
    spammer.start()


if __name__ == "__main__":
    main()
