import argparse

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(help='sub-command help', dest='COMMAND')

parser_list = subparsers.add_parser('list', help='list devices')
parser_list.add_argument('-v', '--verbose', action='store_true')

parser_show = subparsers.add_parser('show', help='show device info')
parser_show.add_argument('-v', '--verbose', action='store_true')
parser_show.add_argument('device')

parser_monitor = subparsers.add_parser('monitor', help='monitor device event')
parser_monitor.add_argument('device')

parser_virtual = subparsers.add_parser('virtual', help='run a virtual device')
parser_virtual.add_argument('config')
parser_virtual.add_argument('device')

args = parser.parse_args()
if args.COMMAND == 'list':
    from .evdev import list_devices

    for device in list_devices():
        print(device.dev, device.phys, device.name, end="")
        print(' '.join(repr(p) for p in device.properties))
        if args.verbose:
            for key, caps in device.capabilities.items():
                print(f"  {key.__name__}: ", end="")
                print(' '.join(repr(cap) for cap in caps))

elif args.COMMAND == 'show':
    from .evdev import EventDevice, EV, ABS
    import ctypes

    def to_python(value):
        if isinstance(value, ctypes.Structure):
            return {n: getattr(value, n) for n, _ in value._fields_}
        elif isinstance(value, ctypes.Array):
            return [value[i] for i in range(value._length_)]
        elif isinstance(value, ctypes._SimpleCData):
            return value.value
        else:
            return value

    with EventDevice(args.device) as device:
        print(device.dev, device.phys, device.name, end="")
        print(' '.join(repr(p) for p in device.properties))
        if args.verbose:
            for key, caps in device.capabilities.items():
                print(f"  {key.__name__}: ", end="")
                print(' '.join(repr(cap) for cap in caps))
        print("version:", to_python(device.get_version()))
        print("id:", to_python(device.get_id()))
        print("name:", to_python(device.get_name()))
        print("phys:", to_python(device.get_phys()))
        print("prop:", to_python(device.get_prop()))
        print("abs:")
        for e in device.capabilities.get(ABS, ()):
            print(f"  {e!r}: ", to_python(device.get_abs(e)))


elif args.COMMAND == 'monitor':
    from .evdev import EventDevice, EV
    with EventDevice(args.device) as device:
        prev = None
        for event in device:
            if event.time != prev:
                if prev:
                    print(f"{(event.time - prev).total_seconds()},", end="")
                print(f"# TIME: {event.time.isoformat()}")
                prev = event.time
            if event.type == EV.KEY:
                print(f"({event.code.name}, {event.value}),")
            else:
                print(f"({event.code.__class__.__name__}.{event.code.name}, {event.value}),")

elif args.COMMAND == 'virtual':
    from .virtual import main
    main(args.config, args.device)

else:
    parser.print_help()
