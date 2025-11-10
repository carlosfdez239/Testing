#!/usr/bin/env python3
"""
printer_status.py

Lee brother_oids.json y consulta cada OID vía snmpget.
Muestra una tabla resumen con OID, nombre y valor.

Requisitos:
 - snmpget (net-snmp) instalado y accesible en PATH
 - python3
 - pip install tabulate (opcional, el script funciona sin tabulate pero la salida será mejor)
"""

import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime

# Opcionales
try:
    from tabulate import tabulate
    _HAS_TABULATE = True
except Exception:
    _HAS_TABULATE = False

JSON_FILE = "brother_oids.json"

# Parámetros SNMP: modifica si tu comunidad o versión son otras
SNMP_VERSION = "2c"
SNMP_COMMUNITY = "public"
SNMP_TIMEOUT = 2  # segundos por intento

def load_oids(json_path):
    p = Path(json_path)
    if not p.is_file():
        print(f"Error: no existe {json_path}")
        sys.exit(2)
    data = json.loads(p.read_text(encoding="utf-8"))
    return data

def run_snmpget(host, oid, community=SNMP_COMMUNITY, version=SNMP_VERSION, timeout=SNMP_TIMEOUT):
    """
    Ejecuta snmpget para un único OID. Devuelve (ok_boolean, salida_texto).
    Si falla (timeout, noSuchName, etc.) devuelve ok=False y mensaje de error.
    """
    cmd = [
        "snmpget",
        "-v", version,
        "-c", community,
        "-t", str(timeout),
        host,
        oid
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True)
    except FileNotFoundError:
        return False, "snmpget no encontrado. Instala net-snmp-utils / snmp."
    # si returncode != 0 puede ser timeout u otro error
    out = res.stdout.strip()
    err = res.stderr.strip()
    if res.returncode != 0:
        # intentar devolver stderr si existe
        msg = err if err else out if out else f"snmpget retornó código {res.returncode}"
        return False, msg
    if not out:
        return False, "sin salida"
    # Normalizar la línea: suele tener formato "OID = TYPE: VALUE"
    return True, out

def parse_snmp_output(raw):
    """
    Trata de extraer el valor de la salida de snmpget.
    Ejemplo de raw:
      SNMPv2-SMI::mib(1) = STRING: "texto"
      iso.3.6.1.2.1.1.1.0 = STRING: "desc..."
    Devuelve una cadena legible con tipo y valor o el raw si no puede parsear.
    """
    # Intento simple: buscar '=' y tomar lo que hay a la derecha
    if "=" in raw:
        parts = raw.split("=", 1)[1].strip()
        return parts
    # fallback
    return raw

def gather_status(host, oids):
    rows = []
    summary = {"ok": 0, "not_impl": 0, "error": 0}
    for entry in oids:
        oid = entry.get("oid")
        name = entry.get("name", oid)
        desc = entry.get("description", "")
        ok, out = run_snmpget(host, oid)
        if not ok:
            # Si hay error, intentar snmpwalk corto (algunas OIDs requieren walk)
            walk_try = False
            if "No Such" in out or "Timeout" in out or "noSuchObject" in out or "noSuchInstance" in out:
                walk_try = True
            if walk_try:
                # intentamos snmpwalk del OID
                cmd = ["snmpwalk", "-v", SNMP_VERSION, "-c", SNMP_COMMUNITY, host, oid]
                try:
                    r = subprocess.run(cmd, capture_output=True, text=True, timeout=SNMP_TIMEOUT+1)
                    wout = r.stdout.strip()
                    if r.returncode == 0 and wout:
                        ok2 = True
                        out2 = wout
                    else:
                        ok2 = False
                        out2 = r.stderr.strip() if r.stderr.strip() else (wout if wout else f"snmpwalk error {r.returncode}")
                except Exception as e:
                    ok2 = False
                    out2 = f"snmpwalk fallo: {e}"
                if ok2:
                    val = parse_snmp_output(out2)
                    rows.append([name, oid, desc, val])
                    summary["ok"] += 1
                    continue
                else:
                    rows.append([name, oid, desc, f"ERROR: {out2}"])
                    summary["error"] += 1
                    continue
            # no se pudo obtener OID
            rows.append([name, oid, desc, f"ERROR: {out}"])
            summary["error"] += 1
        else:
            val = parse_snmp_output(out)
            # detectar valores típicos de "no disponible"
            lowval = val.lower()
            if "no such" in lowval or "noSuch" in val or "noSuchInstance" in val or "noSuchObject" in val:
                rows.append([name, oid, desc, "NO IMPLEMENTADO"])
                summary["not_impl"] += 1
            else:
                rows.append([name, oid, desc, val])
                summary["ok"] += 1
    return rows, summary

def print_table(rows):
    headers = ["Nombre", "OID", "Descripción", "Valor"]
    if _HAS_TABULATE:
        print(tabulate(rows, headers=headers, tablefmt="fancy_grid", stralign="left", disable_numparse=True))
    else:
        # impresión simple alineada
        widths = [max(len(str(r[i])) for r in ([headers] + rows)) for i in range(4)]
        fmt = "  ".join("{:<" + str(w) + "}" for w in widths)
        print(fmt.format(*headers))
        print("-" * (sum(widths) + 6))
        for r in rows:
            print(fmt.format(*[str(x) for x in r]))

def main():
    if len(sys.argv) < 2:
        print("Uso: python3 printer_status.py <host> [community]")
        print("Ejemplo: python3 printer_status.py 192.168.1.199 public")
        sys.exit(1)
    host = sys.argv[1]
    global SNMP_COMMUNITY
    if len(sys.argv) >= 3:
        SNMP_COMMUNITY = sys.argv[2]

    # cargar OIDs
    data = load_oids(JSON_FILE)
    oids = data.get("oids", [])

    start = datetime.now()
    print(f"Consultando {len(oids)} OIDs en {host} (comunidad='{SNMP_COMMUNITY}', v{SNMP_VERSION})...")
    rows, summary = gather_status(host, oids)
    end = datetime.now()
    elapsed = (end - start).total_seconds()

    print("\nResultados:\n")
    print_table(rows)

    print("\nResumen:")
    print(f"  OK: {summary['ok']}")
    print(f"  No implementado / sin instancia: {summary['not_impl']}")
    print(f"  Errores: {summary['error']}")
    print(f"Tiempo total: {elapsed:.2f} s")

if __name__ == "__main__":
    main()
