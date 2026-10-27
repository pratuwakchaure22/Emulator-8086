import os, sys, subprocess, tempfile
from pathlib import Path
from PySide6.QtWidgets import (QApplication,QMainWindow,QWidget,QVBoxLayout,QHBoxLayout,QPlainTextEdit,QPushButton,QTableWidget,QTableWidgetItem,QSplitter,QFileDialog,QMessageBox,QLabel,QTabWidget,QHeaderView)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from unicorn import Uc, UcError, UC_ARCH_X86, UC_MODE_16, UC_HOOK_INTR
from unicorn.x86_const import *

REGISTERS = {'AX':UC_X86_REG_AX,'BX':UC_X86_REG_BX,'CX':UC_X86_REG_CX,'DX':UC_X86_REG_DX,'SI':UC_X86_REG_SI,'DI':UC_X86_REG_DI,'BP':UC_X86_REG_BP,'SP':UC_X86_REG_SP,'CS':UC_X86_REG_CS,'DS':UC_X86_REG_DS,'ES':UC_X86_REG_ES,'SS':UC_X86_REG_SS,'IP':UC_X86_REG_IP,'FLAGS':UC_X86_REG_EFLAGS}
EXAMPLE = '''; 16-bit DOS .COM program (NASM syntax)\nBITS 16\nORG 100h\n\nmov ah, 09h\nmov dx, message\nint 21h\n\nmov ax, 0005h\nmov bx, 0003h\nadd ax, bx\n\nmov ax, 4C00h\nint 21h\n\nmessage db 'Hello from Ubuntu 8086 Emulator!$'\n'''
class Emulator(QMainWindow):
    def __init__(self):
        super().__init__(); self.setWindowTitle('Ubuntu 8086 Emulator — Student Edition'); self.resize(1180,750)
        self.filename=None; self.uc=None; self.terminated=False; self.code=b''; self.instructions=0
        root=QWidget(); self.setCentralWidget(root); outer=QVBoxLayout(root)
        actions=QHBoxLayout(); outer.addLayout(actions)
        for title,callback in [('New',self.new),('Open',self.open_file),('Save',self.save),('Assemble',self.assemble),('Run',self.run_program),('Step',self.step),('Reset',self.reset)]:
            btn=QPushButton(title); btn.clicked.connect(callback); actions.addWidget(btn)
        splitter=QSplitter(Qt.Horizontal); outer.addWidget(splitter)
        left=QWidget(); leftv=QVBoxLayout(left); leftv.addWidget(QLabel('8086 Assembly Source (NASM syntax)'))
        self.editor=QPlainTextEdit(EXAMPLE); self.editor.setFont(QFont('Monospace',12)); leftv.addWidget(self.editor); splitter.addWidget(left)
        right=QWidget(); rv=QVBoxLayout(right); rv.addWidget(QLabel('CPU Registers (hex)'))
        self.regs=QTableWidget(len(REGISTERS),2); self.regs.setHorizontalHeaderLabels(['Register','Value']); self.regs.verticalHeader().hide(); self.regs.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        for i,name in enumerate(REGISTERS): self.regs.setItem(i,0,QTableWidgetItem(name)); self.regs.setItem(i,1,QTableWidgetItem('0000'))
        rv.addWidget(self.regs)
        tabs=QTabWidget(); self.console=QPlainTextEdit(); self.console.setReadOnly(True); tabs.addTab(self.console,'DOS output')
        self.memory=QPlainTextEdit(); self.memory.setReadOnly(True); self.memory.setFont(QFont('Monospace',10)); tabs.addTab(self.memory,'Memory (segment 0000)')
        rv.addWidget(tabs); splitter.addWidget(right); splitter.setSizes([680,480]); self.statusBar().showMessage('Ready — press Assemble, then Run or Step')
    def new(self): self.filename=None; self.editor.setPlainText(EXAMPLE); self.reset()
    def open_file(self):
        name,_=QFileDialog.getOpenFileName(self,'Open assembly source','','Assembly (*.asm *.s);;All files (*)')
        if name:
            try: self.editor.setPlainText(Path(name).read_text(encoding='utf-8')); self.filename=name; self.reset()
            except OSError as e: QMessageBox.critical(self,'Open error',str(e))
    def save(self):
        name=self.filename
        if not name: name,_=QFileDialog.getSaveFileName(self,'Save assembly source','main.asm','Assembly (*.asm)')
        if name:
            try: Path(name).write_text(self.editor.toPlainText(),encoding='utf-8'); self.filename=name
            except OSError as e: QMessageBox.critical(self,'Save error',str(e))
    def assemble(self):
        try:
            with tempfile.TemporaryDirectory() as d:
                src=Path(d)/'program.asm'; dst=Path(d)/'program.com'; src.write_text(self.editor.toPlainText(),encoding='utf-8')
                proc=subprocess.run(['nasm','-f','bin',str(src),'-o',str(dst)],capture_output=True,text=True,timeout=15)
                if proc.returncode: raise ValueError(proc.stderr or 'NASM failed')
                self.code=dst.read_bytes()
            if len(self.code)>0xFF00: raise ValueError('Program exceeds supported .COM size')
            if not self.code: raise ValueError('Empty binary')
            self.uc=None; self.terminated=False; self.instructions=0
            self.statusBar().showMessage(f'Assembled: {len(self.code)} bytes (16-bit .COM)')
            return True
        except FileNotFoundError: QMessageBox.critical(self,'NASM missing','Install NASM: sudo apt install nasm')
        except Exception as e: QMessageBox.critical(self,'Assembly error',str(e))
        return False
    def initialize(self):
        if not self.code and not self.assemble(): return False
        self.uc=Uc(UC_ARCH_X86,UC_MODE_16); self.uc.mem_map(0,0x100000)
        self.uc.mem_write(0x100,self.code)
        for name in ('CS','DS','ES','SS'): self.uc.reg_write(REGISTERS[name],0)
        self.uc.reg_write(UC_X86_REG_IP,0x100); self.uc.reg_write(UC_X86_REG_SP,0xFFFE)
        self.uc.reg_write(UC_X86_REG_EFLAGS,0x202)
        self.uc.hook_add(UC_HOOK_INTR,self.interrupt)
        self.console.clear(); self.terminated=False; self.instructions=0; self.update_views(); return True
    def interrupt(self,uc,intno,user_data):
        if intno != 0x21: raise RuntimeError(f'Unsupported interrupt INT {intno:02X}h')
        ax=uc.reg_read(UC_X86_REG_AX); ah=(ax>>8)&255; dx=uc.reg_read(UC_X86_REG_DX); ds=uc.reg_read(UC_X86_REG_DS)
        if ah==0x09:
            start=(ds<<4)+dx; output=[]
            for i in range(4096):
                ch=uc.mem_read(start+i,1)[0]
                if ch==ord('$'): break
                output.append(chr(ch))
            else: raise RuntimeError('INT 21h/AH=09h: missing $ terminator (limit 4096 bytes)')
            self.console.insertPlainText(''.join(output))
        elif ah==0x02: self.console.insertPlainText(chr(dx&255))
        elif ah==0x4C: self.terminated=True; uc.emu_stop()
        else: raise RuntimeError(f'Unsupported DOS function INT 21h/AH={ah:02X}h')
    def execute(self,count):
        if self.uc is None and not self.initialize(): return
        if self.terminated: self.statusBar().showMessage('Program terminated; Reset to restart'); return
        try:
            ip=self.uc.reg_read(UC_X86_REG_IP); cs=self.uc.reg_read(UC_X86_REG_CS); start=(cs<<4)+ip
            self.uc.emu_start(start,0,count=count)
            self.instructions+=count
            if not self.terminated and self.uc.reg_read(UC_X86_REG_IP)==ip and count==1:
                self.statusBar().showMessage('Warning: IP unchanged')
            else: self.statusBar().showMessage('Terminated' if self.terminated else f'Executed (up to {count}) instruction(s)')
        except (UcError,RuntimeError) as e:
            self.terminated=True; QMessageBox.warning(self,'Execution stopped',str(e))
        self.update_views()
    def run_program(self):
        # Hard limit prevents accidental infinite loops from freezing the UI indefinitely.
        self.execute(100000)
        if self.uc and not self.terminated: self.statusBar().showMessage('Stopped at safety limit (100000 instructions); Step or Run to continue')
    def step(self): self.execute(1)
    def reset(self): self.uc=None; self.terminated=False; self.code=b''; self.console.clear(); self.memory.clear(); self.statusBar().showMessage('Reset — assemble before running')
    def update_views(self):
        if not self.uc:return
        for i,(name,reg) in enumerate(REGISTERS.items()):
            value=self.uc.reg_read(reg); self.regs.item(i,1).setText(f'{value:08X}' if name=='FLAGS' else f'{value & 0xFFFF:04X}')
        addr=(self.uc.reg_read(UC_X86_REG_DS)<<4)+0x100
        try:
            data=bytes(self.uc.mem_read(addr,128)); lines=[]
            for off in range(0,128,16): lines.append(f'{addr+off:05X}: '+' '.join(f'{b:02X}' for b in data[off:off+16]))
            self.memory.setPlainText('\n'.join(lines))
        except UcError: self.memory.setPlainText('Memory not accessible')
if __name__=='__main__':
    app=QApplication(sys.argv); window=Emulator(); window.show(); sys.exit(app.exec())
