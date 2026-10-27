# Ubuntu 8086 Emulator — Windows-developed, Ubuntu-run

This is a **starter 16-bit DOS .COM emulator / debugger GUI**, not a complete replacement for EMU8086.

## Develop on Windows
Edit `src/main.py` and `.asm` files using VS Code or another editor on Windows. **Do not copy a Windows virtual environment to Linux**: native Python wheels differ by OS.

## First run on Ubuntu (internet required)
1. Copy/extract the complete `Ubuntu8086` folder to Ubuntu.
2. Open Terminal inside the project folder.
3. Run `chmod +x install_ubuntu.sh run_ubuntu.sh`
4. Run `./install_ubuntu.sh` (installs Ubuntu native dependencies, asks sudo password).
5. Run `./run_ubuntu.sh`.

Requires a graphical Ubuntu session, Ubuntu's standard `apt` repositories and access to PyPI during initial installation. Later launches do not require internet. Ubuntu x86-64 recommended.

## Supported
- Assemble **NASM** syntax (`BITS 16`, `ORG 100h`), raw `.COM`-style 16-bit binary.
- Step and run 8086-compatible instructions in Unicorn x86 16-bit mode.
- Display registers, DOS-style output and basic memory hex dump.
- Implemented DOS INT 21h AH=02h (character), AH=09h (`$`-terminated string), AH=4Ch (terminate).

## Not yet implemented
- Full DOS, BIOS, `.EXE` loader, EMU8086-specific MASM macro syntax, source-level instruction highlighting, keyboard input, breakpoints, complete devices/peripherals.
- This emulator is for learning; it is not a cycle-accurate original 8086 hardware model.
- Run imposes a 100000-instruction safety limit per click and may still briefly block the GUI on large workloads.

## Offline Ubuntu installation
Installing Python dependencies on Windows does NOT embed Linux packages. For truly offline Ubuntu, obtain wheels for the **exact target Ubuntu architecture/Python version** plus apt `.deb` dependencies using a matching Ubuntu environment (e.g. Docker or WSL), then adapt the installer to use local wheels. The included script installs everything online on the Ubuntu computer to avoid incompatible binaries.
