#!/usr/bin/env python3
import subprocess
import json
from pathlib import Path
from tabulate import tabulate
from wcwidth import wcswidth
import glob
import sys

# ---------------- utilidades ----------------
def run_cmd(cmd, sudo=False):
    """Ejecuta un comando en shell y devuelve el resultado."""
    if sudo:
        cmd = ["sudo"] + cmd
    res = subprocess.run(cmd, capture_output=True, text=True)
    return res

def get_brother_drivers():
    """Obtiene los drivers Brother instalados desde dpkg."""
    result = run_cmd(["dpkg", "-l"])
    lines = [line for line in result.stdout.splitlines() if "Brother" in line]
    drivers = {}

    for line in lines:
        parts = line.split()
        if len(parts) >= 5:
            status = parts[0]
            package = parts[1]
            version = parts[2]
            arch = parts[3]
            description = " ".join(parts[4:])
            drivers[package] = {
                "status": status,
                "version": version,
                "arch": arch,
                "description": description
            }
    return drivers

def save_to_json(data, filename="brother_drivers.json"):
    """Guarda el diccionario en un archivo JSON legible."""
    path = Path(filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"\n ✅ Archivo guardado en: {path.resolve()}")

# ---------------- comparación ----------------
def compare_with_pattern(drivers, pattern):
    """Compara los drivers instalados con un patrón esperado."""
    comparison = []

    for pkg, expected_version in pattern.items():
        if pkg in drivers:
            installed_version = drivers[pkg]["version"]
            if expected_version is None:
                result = f"Instalado (versión: {installed_version})"
                match = "OK"
            elif installed_version == expected_version:
                result = f"Correcta ({installed_version})"
                match = "OK"
            else:
                result = f"Diferente (instalada: {installed_version}, esperada: {expected_version})"
                match = "WARNING"
        else:
            result = "No instalado"
            installed_version = "-"
            match = "FAIL"
        comparison.append([pkg, expected_version or "-", installed_version, result, match])

    return comparison

# ---------------- alineado visual ----------------
def visual_width(s):
    return wcswidth(str(s))

def pad_row_cells(rows, headers):
    """Corrige la alineación visual de emojis y texto."""
    all_rows = [headers] + rows
    n_cols = len(headers)
    max_widths = [0] * n_cols

    for r in all_rows:
        for i in range(n_cols):
            cell = r[i] if i < len(r) else ""
            w = visual_width(cell)
            if w < 0:
                w = len(str(cell))
            if w > max_widths[i]:
                max_widths[i] = w

    padded_rows = []
    for r in rows:
        new_row = []
        for i in range(n_cols):
            cell = r[i] if i < len(r) else ""
            cell_str = str(cell)
            w = visual_width(cell_str)
            if w < 0:
                w = len(cell_str)
            pad = max_widths[i] - w
            new_cell = cell_str + (" " * pad)
            new_row.append(new_cell)
        padded_rows.append(new_row)

    padded_headers = []
    for i, h in enumerate(headers):
        h_str = str(h)
        w = visual_width(h_str)
        pad = max_widths[i] - w
        padded_headers.append(h_str + (" " * pad))

    return padded_rows, padded_headers

# ---------------- instalación ----------------
def find_deb_for_package(package_name):
    """Busca archivos .deb que coincidan con el nombre del paquete."""
    patterns = [
        f"./{package_name}*.deb",
        f"./{package_name.replace(':', '_')}*.deb",
        f"/var/cache/apt/archives/{package_name}*.deb",
        f"/tmp/{package_name}*.deb",
        f"/var/cache/apt/archives/*{package_name}*.deb",
        f"./*{package_name}*.deb"
    ]
    for pat in patterns:
        for path in glob.glob(pat):
            if Path(path).is_file():
                return Path(path).resolve()

    # búsqueda alternativa
    fallback_patterns = [
        "./brother*.deb",
        "./ql*.deb",
        "/var/cache/apt/archives/brother*.deb",
        "/var/cache/apt/archives/ql*.deb"
    ]
    for pat in fallback_patterns:
        matches = glob.glob(pat)
        if matches:
            return Path(matches[0]).resolve()
    return None

def install_deb(deb_path):
    """Instala un archivo .deb con confirmación del usuario."""
    if not Path(deb_path).is_file():
        return False, f"No existe el archivo: {deb_path}"

    print(f"\n🔧 Se encontró el paquete: {deb_path}")
    confirm = input("¿Deseas instalarlo con 'sudo dpkg -i --force-all'? [y/N]: ").strip().lower()
    if confirm != "y":
        return False, "Instalación cancelada por el usuario."

    print(f"➡️ Instalando {deb_path}...")
    res = run_cmd(["dpkg", "-i", "--force-all", str(deb_path)], sudo=True)
    success = (res.returncode == 0)
    output = res.stdout + ("\n" + res.stderr if res.stderr else "")
    return success, output

def install_driver_if_missing(package_name):
    """Intenta instalar el paquete si no está instalado, con confirmación."""
    drivers = get_brother_drivers()
    if package_name in drivers:
        return True, f"{package_name} ya está instalado (versión: {drivers[package_name]['version']})"

    found = find_deb_for_package(package_name)
    if not found:
        return False, f"No se encontró un archivo .deb para {package_name}."

    ok, msg = install_deb(found)
    if ok:
        new_drivers = get_brother_drivers()
        if package_name in new_drivers:
            return True, f"{package_name} instalado correctamente."
    return False, msg

# ---------------- main ----------------
if __name__ == "__main__":
    brother_drivers = get_brother_drivers()
    save_to_json(brother_drivers)

    expected_pattern = {
        #"printer-driver-brlaser": "6-3",
        #"printer-driver-ptouch": "1.6-2build1",
        "ql820nwbpdrv:i386": "3.1.5",
        "ql800pdrv:i386": None
    }

    comparison_results = compare_with_pattern(brother_drivers, expected_pattern)

    headers = ["Paquete", "Versión esperada", "Versión instalada", "Resultado", "Estado"]
    padded_rows, padded_headers = pad_row_cells(comparison_results, headers)

    print("\n🧩 Resultado de comparación:\n")
    print(tabulate(padded_rows, headers=padded_headers, tablefmt="fancy_grid", stralign="left", disable_numparse=True))

    to_install = [row[0] for row in comparison_results if row[4] == "FAIL"]
    if to_install:
        print("\n🔎 Paquetes no instalados:")
        for pkg in to_install:
            print(f" - {pkg}")
        for pkg in to_install:
            installed, msg = install_driver_if_missing(pkg)
            print(f"\n{msg}")
    else:
        print("\n✅ Todos los paquetes del patrón están instalados.\n\n")

    missing = [row for row in comparison_results if row[4] == "FAIL"]
    sys.exit(0 if not missing else 1)
