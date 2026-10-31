<div align="center">

# 🖥️ Ubuntu 8086 Emulator

### A modern 16-bit 8086 assembly emulator & debugger for Linux

Write NASM assembly · Assemble to a DOS `.COM` binary · Run or single-step it · Watch registers, memory and output live.

![Platform](https://img.shields.io/badge/platform-Ubuntu%20%7C%20Debian-E95420?logo=ubuntu&logoColor=white)
![Python](https://img.shields.io/badge/python-3.9%2B-3776AB?logo=python&logoColor=white)
![GUI](https://img.shields.io/badge/GUI-PySide6%20(Qt)-41CD52?logo=qt&logoColor=white)
![Engine](https://img.shields.io/badge/CPU-Unicorn%20Engine-8A2BE2)
![Assembler](https://img.shields.io/badge/assembler-NASM-0A7BBB)
![Architecture](https://img.shields.io/badge/arch-Intel%208086%20(16--bit)-informational)
![Status](https://img.shields.io/badge/status-student%20edition-success)

**Developed by [Pratik Wakchaure](#-author) [& Rugved Kulkarni](#-author)**

[Features](#-features) · [Quick Start](#-quick-start) · [Usage](#-usage) · [How It Works](#-how-it-works) · [Roadmap](#-roadmap) · [Troubleshooting](#-troubleshooting)

</div>

---

## 📖 Overview

**Ubuntu 8086 Emulator** is a desktop application that lets students learn Intel 8086 assembly natively on Linux. It combines an in-app code editor, the NASM assembler, and the Unicorn CPU engine in a clean Qt interface, so you can go from source code to a running, inspectable program in one click.

> **Note:** this is a learning tool, not a full EMU8086 replacement and not a cycle-accurate hardware model. See [Limitations](#-limitations).

## ✨ Features

| | Feature | Details |
|---|---|---|
| ✍️ | **Built-in editor** | NASM-syntax source with New / Open / Save for `.asm` files and a ready-made example |
| ⚙️ | **One-click assemble** | Calls NASM (`-f bin`) and loads the `.COM` binary at `0000:0100` |
| ▶️ | **Run & Step** | Run up to 100,000 instructions per click, or step one instruction at a time |
| 🧮 | **Live registers** | AX, BX, CX, DX, SI, DI, BP, SP, CS, DS, ES, SS, IP, FLAGS |
| 📟 | **DOS output console** | Text printed through INT 21h appears in its own tab |
| 🧠 | **Memory viewer** | 128-byte hex dump starting at `DS:0100` |
| 🛡️ | **Safety limits** | Instruction cap against infinite loops, `$`-terminator guard, clear error dialogs |

### Supported DOS services (INT 21h)

| AH | Function |
|----|----------|
| `02h` | Print a character (`DL`) |
| `09h` | Print a `$`-terminated string (`DS:DX`) |
| `4Ch` | Terminate the program |

Any other interrupt or DOS function stops execution with a clear "Unsupported" message.

## 🎬 Demo

A screen recording of the emulator in action is included in this repository: `Emulator_8086_Video.mp4`.
Youtube link : https://youtu.be/UMxzN-Kq5rg

## 🚀 Quick Start

### Requirements

- Ubuntu / Debian-based Linux with a graphical session (x86-64 recommended)
- `sudo` access and an internet connection for the first install (apt + PyPI)

### Install

```bash
# 1. Get the project (replace with your repository URL)
git clone https://github.com/<your-username>/Ubuntu8086.git
cd Ubuntu8086

# 2. Make the scripts executable
chmod +x install_ubuntu.sh run_ubuntu.sh

# 3. One-time setup (asks for your sudo password)
./install_ubuntu.sh
```

### Run

```bash
./run_ubuntu.sh
```

The installer sets up everything for you:

1. System packages: `python3`, `python3-venv`, `python3-pip`, `nasm`, plus the Qt libraries (`libegl1`, `libopengl0`, `libxkbcommon-x11-0`, `libxcb-cursor0`)
2. A virtual environment in `.venv/`
3. Python dependencies from `requirements.txt` (`PySide6`, `unicorn`)

After the first install, launching works fully offline.

## 🕹️ Usage

1. Write or open a program in the editor (or use the built-in example).
2. Click **Assemble** to build it with NASM.
3. Click **Run** to execute, or **Step** to go one instruction at a time.
4. Inspect the **registers**, **DOS output** and **memory** panels.
5. Click **Reset** to start over, then **Assemble** again before the next run.

| Button | Action |
|--------|--------|
| **New** | Load the example program and reset |
| **Open** | Open an `.asm` / `.s` file |
| **Save** | Save the editor contents as `.asm` |
| **Assemble** | Assemble the editor contents with NASM |
| **Run** | Execute up to 100,000 instructions |
| **Step** | Execute exactly one instruction |
| **Reset** | Clear CPU state, output and memory view (re-assemble before running) |

### Example program

```nasm
BITS 16
ORG 100h

mov ah, 09h          ; DOS: print string
mov dx, message
int 21h

mov ax, 0005h
mov bx, 0003h
add ax, bx           ; AX = 0008h

mov ax, 4C00h        ; DOS: exit
int 21h

message db 'Hello from Ubuntu 8086 Emulator!$'
```

Start every program with `BITS 16` and `ORG 100h`, and finish with `mov ax, 4C00h` / `int 21h`.

## 🧩 How It Works

```
 ┌────────────┐   NASM -f bin   ┌────────────┐   mem_write @0x100   ┌──────────────────┐
 │ Source     │ ──────────────▶ │ .COM       │ ───────────────────▶ │ Unicorn x86      │
 │ (editor)   │                 │ binary     │                      │ 16-bit CPU       │
 └────────────┘                 └────────────┘                      └────────┬─────────┘
                                                                             │ INT 21h hook
                                         Registers · Memory · DOS output ◀───┘
```

- **PySide6** provides the GUI (editor, register table, output and memory tabs).
- **NASM** assembles the source into a flat binary.
- **Unicorn** emulates the 16-bit x86 CPU; a hook on interrupts implements the supported DOS services.

### Project structure

```
Ubuntu8086/
├── src/
│   └── main.py            # GUI, assembler integration, emulator core
├── requirements.txt       # PySide6, unicorn
├── install_ubuntu.sh      # One-time Ubuntu setup (apt + venv + pip)
├── run_ubuntu.sh          # Launches the app from the virtual environment
└── README.md
```

## 🛠️ Developing on Windows

Edit `src/main.py` and your `.asm` files in VS Code or any editor on Windows, then copy the project to Ubuntu to run it.

> ⚠️ **Never copy a Windows virtual environment to Linux.** Native Python wheels differ per operating system. Always create `.venv` on Ubuntu with `./install_ubuntu.sh`.

## ⚠️ Limitations

- Only INT 21h functions `02h`, `09h` and `4Ch` are implemented (no full DOS/BIOS).
- No `.EXE` loader, no EMU8086/MASM macro syntax (NASM syntax only).
- No keyboard input, breakpoints, source-line highlighting or peripheral devices.
- Run stops at 100,000 instructions per click; very heavy workloads may briefly freeze the window.
- Programs are limited to `.COM` size (just under 64 KB).
- Not a cycle-accurate model of original 8086 hardware.

## 🗺️ Roadmap

- [ ] Breakpoints and source-line highlighting while stepping
- [ ] Keyboard input (INT 21h AH=01h / 0Ah)
- [ ] More DOS and BIOS services
- [ ] Flag-bit display (CF, ZF, SF, OF…) and stack viewer
- [ ] `.EXE` loader
- [ ] Non-blocking Run (background thread)

## 🩺 Troubleshooting

| Problem | Fix |
|---|---|
| `Run ./install_ubuntu.sh first` | The virtual environment doesn't exist yet. Run the installer. |
| "NASM missing" dialog | `sudo apt install nasm` |
| `Permission denied` on scripts | `chmod +x install_ubuntu.sh run_ubuntu.sh` |
| Qt error: "could not load the Qt platform plugin xcb" | Re-run `./install_ubuntu.sh` and make sure you are in a graphical session (not plain SSH). |
| "This installer supports Ubuntu/Debian apt-based Linux only" | Install Python 3, NASM and the Qt libraries manually, then create the venv and run `pip install -r requirements.txt`. |
| `Unsupported interrupt` / `Unsupported DOS function` | The program uses a service that isn't implemented yet. |

### Offline installation

Python packages installed on Windows are **not** Linux-compatible. For a fully offline Ubuntu machine, download the wheels and `.deb` packages from a matching Ubuntu environment (same release, architecture and Python version, e.g. Docker or WSL) and adapt `install_ubuntu.sh` to install from local files.

## 👨‍💻 Author

**Pratik Wakchaure**
Student & independent software developer, Sanjivani University

Designed and developed by Pratik Wakchaure.

If this project helped you learn assembly, consider giving it a ⭐ on GitHub.

---

<div align="center">

Made with ❤️ by **Pratik Wakchaure**

</div>
