#!/usr/bin/env python3
"""
Clase para consultar el estado de una impresora Brother QL
y mostrar qué cinta/etiqueta está instalada.
Compatible con brother-ql-inventree.

requisitos : pip3 install brother-ql-inventree

"""

from brother_ql.backends.pyusb import BrotherQLBackendPyUSB as Qlpyusb
from brother_ql.backends.network import BrotherQLBackendNetwork as QLnetwork
from brother_ql.brother_ql_debug import interpret_response
from brother_ql.reader import BrotherQLReader as Qlreader
import brother_ql.brother_ql_info as QLinfo

class BrotherQLStatus:
    # Tabla de equivalencias de soportes (basada en documentación Brother)
    MEDIA_CODES = {
        # Continuas
        12:  ("12 mm", "cinta continua"),
        24:  ("24 mm", "cinta continua"),
        29:  ("29 mm", "cinta continua"),
        38:  ("38 mm", "cinta continua"),
        50:  ("50 mm", "cinta continua"),
        54:  ("54 mm", "cinta continua"),
        62:  ("62 mm", "cinta continua"),
        102: ("102 mm", "cinta continua"),

        # Precortadas
        (29, 90):   ("29 x 90 mm", "precortada"),
        (38, 90):   ("38 x 90 mm", "precortada"),
        (62, 29):   ("62 x 29 mm", "precortada"),
        (62, 100):  ("62 x 100 mm", "precortada"),
        (62, 150):  ("62 x 150 mm", "precortada"),
        (102, 51):  ("102 x 51 mm", "precortada"),
        (102, 152): ("102 x 152 mm", "precortada"),
    }

    def __init__(self, backend_type="pyusb", device_specifier = "QL820-NWBc",printer_identifier="usb://0x04f9:0x209b"):
        """
        Inicializa la conexión con la impresora Brother QL.
        - backend_type: 'pyusb', 'network', 'linux_kernel'
        - printer_identifier: ej. 'usb://0x04f9:0x209b' o 'tcp://192.168.1.50'
        """
        if backend_type == "pyusb":
            self.backend_pyUSB = Qlpyusb()
        elif backend_type == "network":
            self.backend_network = QLnetwork(printer_identifier)
        else:
            raise ValueError (f"Backend desconocido --> {backend_type}\n")
        
        self.printer_identifier = printer_identifier

    def _lookup_media(self, width, length):
        """Devuelve descripción legible a partir de ancho/largo."""
        if length == 0:  # continuo
            return self.MEDIA_CODES.get(width, (f"{width} mm", "desconocido"))
        return self.MEDIA_CODES.get((width, length), (f"{width} x {length} mm", "desconocido"))

    def get_status(self):
        """Obtiene e interpreta el estado de la impresora."""

        impresoras_encotradas = self.backend_network.read()
        #backend = get_backend(self.backend)
        #self.backend.open(self.printer_identifier)
        #self.backend.open(self.printer_identifier)
        status_bytes = self.backend_network.read()
        status = interpret_response(status_bytes)
        self.backend.close()

        result = {
            "raw_bytes": status_bytes.hex(),
            "state": status.get("state", "desconocido"),
            "errors": status.get("errors", []),
            "tape_color": status.get("tape_color", "desconocido"),
            "media": None
        }

        # Procesar información de soporte
        media = status.get("media", {})
        if media:
            width = media.get("width_mm", 0)
            length = media.get("length_mm", 0)
            nombre, tipo = self._lookup_media(width, length)
            result["media"] = {
                "width": width,
                "length": length,
                "nombre": nombre,
                "tipo": tipo
            }

        return result

    def print_status(self):
        """Imprime por consola el estado en formato legible."""
        status = self.get_status()
        print("=== ESTADO DE LA IMPRESORA BROTHER QL ===")
        print("Estado bruto:", status["raw_bytes"])
        print(f"🖨️ Estado: {status['state']}")

        if status["media"]:
            print(f"📦 Soporte detectado: {status['media']['nombre']} ({status['media']['tipo']})\n")
        else:
            print(f"⚠️ No se detecta cinta instalada.\n")

        print(f"🎨 Color de cinta: {status['tape_color']}\n")

        if status["errors"]:
            print("❌ Errores detectados:", status["errors"])
        else:
            print(f"✅ Sin errores\n")

# =====================
# Ejemplo de uso
# =====================
if __name__ == "__main__":
    # Cambia el backend y la impresora según tu caso:
    #   USB:    backend="pyusb", printer="usb://0x04f9:0x209b"
    #   Red:    backend="network", printer="tcp://192.168.1.50"
    #ql = BrotherQLStatus(backend_type="pyusb", printer_identifier="usb://0x04f9:0x209b")
    ql = BrotherQLStatus(backend_type="network",printer_identifier="tcp://192.168.1.199")
    ql.print_status()
