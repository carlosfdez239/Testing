'''
Script to generate a product receipt in PDF format using ReportLab.

author: Carlos Fdez
date: 08/07/2025
revision: 1.0

Todo:
    [X] Implement the function to generate the txt file.

revision history:
    1.0 - Initial version with basic structure for PDF generation.
    1.1 - Added Color_Text module for colored text output. 06/08/2025
    
'''
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os   
from datetime import datetime
from reportlab.lib.units import mm
import json
import pandas as pd
import mysql.connector
import Color_Text as color

# Conexión a la base de datos MySQL
conn = mysql.connector.connect(
    host='wsmysqlserverpro.mysql.database.azure.com',
    user='admin_ws',
    password='ws9hnBt54T',
    database='entrega',
    port = '3306'
)

import json

cursor = conn.cursor(dictionary=True)
producto = input("Introduce el ERP code del producto: ")

query = """
SELECT 
    products.Id AS product_id,
    products.ErpCode,
    
    processes.Id AS process_id,
    processes.Description AS process_description,
    
    process_routes.Id AS process_routes_id,
    process_routes.Description AS process_routes_description,
    process_routes.Phase AS process_routes_phase,

    operation_routes.Id AS operation_route_id,
    operation_routes.Description AS operation_description,
    operation_routes.Index AS operation_index,
    operation_routes.OperationRouteType,
    
    operation_type_enum.Id AS operation_type_id,
    operation_type_enum.Name AS operation_type_name

FROM products
JOIN processes ON processes.IdProduct = products.Id
LEFT JOIN process_routes ON process_routes.IdProcess = processes.Id
LEFT JOIN operation_routes ON operation_routes.IdProcessRoute = process_routes.Id
LEFT JOIN operation_type_enum ON operation_routes.OperationRouteType = operation_type_enum.Id
WHERE products.ErpCode = %s
ORDER BY processes.Id, process_routes.Id, operation_routes.Index
"""

cursor.execute(query, (producto,))
rows = cursor.fetchall()

if not rows:
    print(color.color_text(f"\nNo se encontraron datos para el producto: {producto}\n\n", color.ROJO))
    exit()

# Agrupar por proceso y luego por fase
agrupado = {}

for row in rows:
    proceso_id = row["process_id"]
    fase_nombre = row["process_routes_phase"] or "Fase desconocida"

    if proceso_id not in agrupado:
        agrupado[proceso_id] = {
            "descripcion": row["process_description"],
            "fases": {}
        }

    if fase_nombre not in agrupado[proceso_id]["fases"]:
        agrupado[proceso_id]["fases"][fase_nombre] = {
            "descripcion": row["process_routes_description"],
            "operaciones": []
        }

    if row["operation_route_id"] is not None:
        agrupado[proceso_id]["fases"][fase_nombre]["operaciones"].append({
            "id": row["operation_route_id"],
            "descripcion": row["operation_description"],
            "index": row["operation_index"],
            "tipo": row["operation_type_name"]
        })

# Escribir archivo de salida
file_name = f'receta_producto_{producto}.txt'
with open(file_name, 'w', encoding='utf-8') as f:
    f.write(f"Informe de producto ERP: {producto}\n")
    f.write("=" * 60 + "\n\n")
    
    for proceso_id, proceso_data in agrupado.items():
        f.write(f"Proceso {proceso_id}: {proceso_data['descripcion']}\n")
        f.write("-" * 60 + "\n")

        for fase_nombre, fase_data in sorted(proceso_data["fases"].items()):
            f.write(f"  Fase: {fase_nombre} - {fase_data['descripcion']}\n")
            
            operaciones_ordenadas = sorted(fase_data["operaciones"], key=lambda x: x["index"] or 0)
            for op in operaciones_ordenadas:
                f.write(f"    [{op['index']}] {op['descripcion']} (Tipo: {op['tipo']})\n")
            f.write("\n")
        f.write("\n")

print(color.color_text(f"\n✅ Archivo generado correctamente: {file_name} \n\n", color.VERDE))