from lib.busca_tty import USBDeviceScanner  

FIXTURE_SERIAL = "90355de66362ed1192c19f1e8680196e"

def main():
    usb_connected = ""
    scanner = USBDeviceScanner()
    devices = scanner.scan()

    for d in devices:
        print(d["ttyUSB"], d["idVendor"], d["serial"])
        if d["serial"] == FIXTURE_SERIAL:
            usb_connected = d["ttyUSB"]
            print(f'El dispositivo detectado se ha conectado usando el puerto --> {usb_connected}\n')
        else:
            print(f"No se ha encontrado el dispositivo que se busca")
if __name__ == "__main__":
    main()