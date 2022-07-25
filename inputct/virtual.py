from ctypes.util import find_library
from functools import reduce
from ctypes import CDLL, Structure, POINTER, c_long
from traceback import print_exc
from datetime import datetime
from threading import Thread
from queue import Queue, Empty

from .evdev import EventDevice, grab, EV, SYN, KEY, REL, ABS, MSC, SW, LED, SND, REP, FF, FF_STATUS, INPUT_PROP
from .uinput import UInputDevice


libc = CDLL(find_library('c'))
class timespec(Structure):
    _fields_ = [('sec', c_long),
                ('nsec', c_long)]

libc.nanosleep.argtypes = [POINTER(timespec), POINTER(timespec)]

_req = timespec()
_rem = timespec()

def nanosleep(ns):
    _req.sec = ns // 1000000000
    _req.nsec = ns % 1000000000
    libc.nanosleep(_req, _rem)

def reload(config):
    try:
        with open(config) as f:
            source = f.read()
        code = compile(source, config, 'exec')
    except Exception:
        print_exc()
        return

    try:
        g = KEY.__members__.copy()
        g['SYN'] = SYN
        g['KEY'] = KEY
        g['REL'] = REL
        g['ABS'] = ABS
        g['MSC'] = MSC
        g['SW'] = SW
        g['LED'] = LED
        g['SND'] = SND
        g['REP'] = REP
        g['FF'] = FF
        g['FF_STATUS'] = FF_STATUS
        g['INPUT_PROP'] = INPUT_PROP
        exec(code, g)
        name = g.get('NAME', config)
        events = g.get('EVENTS', ())
        props = g.get('PROPS', ())
        modifiers = {k: (1<<i) for i, k in enumerate(g.get('MODIFIERS', ()))}
        mask = reduce(lambda a,b: (a|b), modifiers.values(), 0)
        keymap = g['KEYMAP']
        combo = g.get('COMBO', {})
        combo = {reduce(lambda acc, m: (acc|modifiers[m]), k, 0): v
                 for k, v in combo.items()}
        return name, events, props, keymap, modifiers, mask, combo
    except Exception:
        print_exc()
        return

def emitter(queue, output):
    while True:
        items = queue.get()
        while True:
            try:
                items = queue.get_nowait()
            except Empty:
                break

        for c in items:
            if isinstance(c, int):
                nanosleep(c)
            else:
                output.emit(*c)

def main(config, device):
    NAME, EVENTS, PROPS, KEYMAP, MODIFIERS, MASK, COMBO = reload(config)

    queue = Queue()

    with EventDevice(device) as dev:
        with grab(dev):
            abs = []

            for src, dst in KEYMAP.items():
                if not isinstance(dst, ABS):
                    continue
                assert isinstance(src, ABS)
                abs.append((dst, dev.get_abs(src)))

            with UInputDevice(NAME.encode(), EVENTS, PROPS, abs) as output:
                Thread(target=emitter, args=(queue, output), daemon=True).start()

                mod = 0
                pending_key = []

                for event in dev:
                    if event.type == EV.SYN:
                        if event.code != SYN.REPORT or event.value != 0:
                            continue
                        if not pending_key:
                            continue

                        pending_key.append((event.code, event.value))
                        queue.put(pending_key)
                        pending_key = []
                        continue

                    code = event.code
                    value = event.value
                    
                    key = KEYMAP.get(code, None)
                    if key is not None:
                        pending_key.append((key, value))
                        continue
                    m = MODIFIERS.get(code, None)
                    if m:
                        if value:
                            mod |= m
                        else:
                            mod &= (MASK ^ m)
                        print(mod)
                        continue
                    if value != 1:
                        continue
                    if code == KEY.KEY_ESC:
                        break
                    elif code == KEY.KEY_BACKSPACE:
                        result = reload(config)
                        if result:
                            NAME, EVENTS, PROPS, KEYMAP, MODIFIERS, MASK, COMBO = result
                            print(datetime.now(), "reload success")
                        continue

                    combo = COMBO.get(mod, {}).get(code, None)
                    if combo:
                        queue.put(combo)

