import os
from fcntl import ioctl
from ctypes import Structure, sizeof, c_char, c_uint16, c_uint32, memmove, create_string_buffer
from contextlib import contextmanager
from functools import cached_property

from .evdev import input_id, input_absinfo, input_event, BUS, EV, SYN, KEY, REL, ABS, MSC, SW, LED, SND, REP, FF, FF_STATUS, INPUT_PROP

class uinput_setup(Structure):
    _fields_ = [
        ("id", input_id),
        ("name", c_char * 80),
        ("ff_effects_max", c_uint32)
    ]

class uinput_abs_setup(Structure):
    _fields_ = [
        ("code", c_uint16),
        ("info", input_absinfo)
    ]

_ev_map = {
    SYN: EV.SYN,
    KEY: EV.KEY,
    REL: EV.REL,
    ABS: EV.ABS,
    MSC: EV.MSC,
    SW: EV.SW,
    LED: EV.LED,
    SND: EV.SND,
    REP: EV.REP,
    FF: EV.FF,
    FF_STATUS: EV.FF_STATUS,
}

_request_map = {
    EV:  0x40045564,
    KEY: 0x40045565,
    REL: 0x40045566,
    ABS: 0x40045567,
    MSC: 0x40045568,
    LED: 0x40045569,
    SND: 0x4004556A,
    FF:  0x4004556B,
    SW:  0x4004556D,
    INPUT_PROP: 0x4004556E,
}

class UInputDevice:

    def __init__(self, name, events, props=(), abs=()):
        setup = uinput_setup()
        setup.id.bustype = BUS.VIRTUAL
        setup.name = name
        setup.ff_effects_max = 0

        self.fd = os.open("/dev/uinput", os.O_RDWR)
        evs = {type(e) for e in events}
        if abs:
            evs.add(ABS)
        
        for ev in evs:
            e = _ev_map.get(ev, None)
            if e is not None:
                self._setbit(e)

        for code, info in abs:
            self._setbit(code)
            abs_setup = uinput_abs_setup()
            abs_setup.code = code
            abs_setup.info = info
            ioctl(self.fd, 0x401c5504, abs_setup) 

        for e in events:
            self._setbit(e)
        for p in props:
            self._setbit(p)

        ioctl(self.fd, 0x405c5503, setup)
        ioctl(self.fd, 0x5501)

    def _setbit(self, code):
        request = _request_map[type(code)]
        ioctl(self.fd, request, code)

    def fileno(self):
        return self.fd

    def close(self):
        if self.fd is not None:
            fd = self.fd
            self.fd = None
            ioctl(fd, 0x5502)
            os.close(fd)

    def __del__(self):
        self.close()

    def __enter__(self):
        return self

    def __exit__(self, type, exc, tb):
        self.close()

    @cached_property
    def sysname(self):
        arg = create_string_buffer(80)
        ioctl(self.fd, 0x8050552C, arg)
        return arg.value

    def emit(self, code, value):
        ev = _ev_map[type(code)]
        e = input_event()
        e.type = ev
        e.code = code
        e.value = value
        os.write(self.fd, e)

    @contextmanager
    def syn(self):
        yield
        self.emit(SYN.REPORT, 0)
