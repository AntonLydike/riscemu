from .IOModule import IOModule
from ..priv.Exceptions import InstructionAccessFault
from ..helpers import int_from_bytes
from threading import Thread
import time


def _window_loop(textIO: 'TextIO'):
    #textIO.set_sg_window(None)
    #return
    try:
        import PySimpleGUI as sg

        logs = sg.Text(font="monospace")
        col = sg.Column([[logs]], size=(640, 400), scrollable=True)
        window = sg.Window("TextIO:{:x}".format(textIO.addr), [[col]])
        lines = list()

        window.finalize()
        textIO.set_sg_window(window)
        while True:
            e, v = window.read()
            if e == sg.WINDOW_CLOSED:
                window.close()
                textIO.set_sg_window(None)
                break
            if e == 'putlog':
                lines.insert(0, v[0])
                logs.update(value='\n'.join(lines) + '\n')
                col.contents_changed()

    except ImportError:
        print("[TextIO] module works best with PySimpleGui!")
        textIO.set_sg_window(None)


class TextIO(IOModule):
    def __init__(self, addr: int, buflen: int = 128):
        super(TextIO, self).__init__(addr, buflen + 4)
        self.buff = bytearray(buflen)
        self.current_line = ""
        self.sg_window = None
        self.start_buffer = list()

        self.thread = Thread(target=_window_loop, args=(self,))
        self.thread.start()
        time.sleep(0.1)

    def set_sg_window(self, window):
        if self.sg_window is not None and window is not None:
            raise Exception("cannot set window twice!")
        self.sg_window = window

        buff = self.start_buffer
        self.start_buffer = None if window is None else list()

        for line in buff:
            self._present(line)

    def read(self, addr: int, size: int) -> bytearray:
        raise InstructionAccessFault(addr)

    def write(self, addr: int, data: bytearray, size: int):
        if addr == self.addr:
            if size > 4:
                raise InstructionAccessFault(addr)
            if int_from_bytes(data[0:4]) > 0:
                self._print()
                return
        buff_start = addr - self.addr - 4
        self.buff[buff_start:buff_start + size] = data[0:size]

    def _print(self):
        buff = self.buff
        self.buff = bytearray(self.size)
        if b'\x00' in buff:
            buff = buff.split(b'\x00')[0]
        text = buff.decode('ascii')
        if '\n' in text:
            lines = text.split("\n")
            lines[0] = self.current_line + lines[0]
            for line in lines[:-1]:
                self._present(line)
            self.current_line = lines[-1]
        else:
            self.current_line += text

    def _present(self, text: str):
        if self.sg_window is not None:
            self.sg_window.write_event_value('putlog', text)
        elif self.start_buffer is not None:
            self.start_buffer.append(text)
        else:
            print("[TextIO:{:x}] {}".format(self.addr, text))

