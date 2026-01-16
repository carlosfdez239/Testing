'''
Autor: C. Fdez
Fecha: 02/07/2025
rev: 0
Descripción: Validador datos de producción para equipos Montronic


To Do

    [] Implementar la opción de generar un informe pdf

    [] Implementar entorno gráfico tkinter


Revisiones:
v0 - Creación del script base para análisis de datos JSON de producción
v1 - Se cambia la búsqueda de los datos a la tabla Operation_results. De la tabla Units se recoge el idunit y 
se usa para buscar en Operation_results el dato de su último Compelted_At. Luego se extrae el JSON de la columna Data.

Dependencias

sudo apt install python3-mysql.connector

'''

import mysql.connector
import json
import os
import pandas as pd
import Color_Text as color
import datetime

# Lista de los numeros de serie a analizar
SN_list = [188378,188352,188358,188354,188288,188275,188197,188284,188377,188253,188226,188178,188177,188356,188198]

# Conexión a la base de datos MySQL
conn = mysql.connector.connect(
    host='wsmysqlserverpro.mysql.database.azure.com',
    user='admin_ws',
    password='ws9hnBt54T',
    database='world_sensing_2025',
    port='3306'
)
cursor = conn.cursor(dictionary=True)

respuesta_til = input(color.color_text(f"\n¿Los serials son TIL? (S/N): ", color.AMARILLO))
TIL = True if "S" in respuesta_til.upper() else False

for SN in SN_list:
    try:
        # Obtener ID de la unidad
        cursor.execute("SELECT Id FROM Units WHERE SN=%s", (SN,))
        row_unit = cursor.fetchone()
        #print(f'el contenido de row_unit: {row_unit}\n')

        if row_unit is None:
            print(f"ROW_UNIT is None. No se encontraron datos para el SN: {SN}")
            continue

        # Obtener última operación
        cursor.execute("SELECT * FROM Operation_results WHERE IdUnit=%s AND OperationType = %s ORDER BY CompletedAt DESC LIMIT 1", (row_unit['Id'], 20))
        row_op = cursor.fetchone()
        #print(f'el contenido de row_op: {row_op}\n')
        
        if row_op is None:
            print(f"ROW_OP is None. No se encontraron datos de operación para el SN: {SN}")
            continue
        
        # Cargar el JSON
        data_json = json.loads(row_op['Data'])

        # Extraer metadatos generales
        Type_Eol = data_json.get("Type", "N/A")
        Cmd_Eol = data_json.get("Cmd", "N/A")
        Status_Eol = data_json.get("Status", "N/A")
        serial_Eol = data_json.get("Serial", "N/A")
        Info_Eol = data_json.get("Info", {})
        Fixture_Id = Info_Eol.get("FixtureId", "N/A")
        Fixture_cassette = Info_Eol.get("Cassette", "N/A")
        Completed_At = row_op.get("CompletedAt", "N/A")
        
        # Extraer la lista de Tests
        Eol_data_Test = data_json.get("Tests", [])
        
        if Status_Eol == "COMPLETE":
            Status_Eol = "PASS"

        print(f"\nAnálisis del SN: {SN}")
        print(f"Estado: {Status_Eol}")
        print(f"Completado en: {Completed_At}")
        print(f"Fixture: {Fixture_Id} | Cassette: {Fixture_cassette}\n")
        print(f"===================== Detalles de las pruebas EOL ====================\n")
        
        nombre_archivo = f'Informe_EOL_SN_{SN}.txt'
        
        with open(nombre_archivo, 'w', encoding='utf-8') as f:
            f.write(f"INFORME DE PRUEBAS EOL - SN: {SN}\n")
            f.write(f"Fecha: {datetime.datetime.now()}\n")
            f.write("-" * 150 + "\n")
            f.write(f"Tipo: {Type_Eol}\n")
            f.write(f"Estado Final: {Status_Eol}\n")
            f.write(f"Fixture ID: {Fixture_Id} | Cassette: {Fixture_cassette}\n")
            f.write("-" * 150 + "\n")
            f.write(f"{'DESCRIPCION':<20} | {'UNITS':<7} | {'MIN':<10} | {'VALOR':<75} | {'MAX':<10} | {'RESULT'}\n")
            f.write("-" * 150 + "\n")

            for element in Eol_data_Test:
                Test_Name = element.get("Description", "N/A")
                Data_value = element.get("DataValue", "N/A")
                Data_Max = element.get("DataMax", "N/A")
                Data_Min = element.get("DataMin", "N/A")
                Test_Result = "PASS" if element.get("Result") is True else "FAIL"
                Units = element.get("Units", "")

                # Manejo especial si DataValue es un diccionario (como en 'HEALTH')
                if isinstance(Data_value, dict):
                    display_value = "DICT_DATA"
                else:
                    display_value = f"{Data_value}"

                # Imprimir en consola y escribir en archivo con formato de columnas
                print(f"{Test_Name:<20} {Units:<7} -> {display_value:<75} [{Test_Result}]")
                
                f.write(f"{Test_Name:<20} | {str(Units):<7} | {str(Data_Min):<10} | {str(display_value):<75} | {str(Data_Max):<10} | {Test_Result}\n")

            # --- SECCIÓN DE CALIBRACIÓN (TIL) ---
            if TIL:
                f.write("\n" + "="*20 + " CALIBRATION CHECK " + "="*20 + "\n")
                
                cursor.execute("SELECT * FROM Operation_results WHERE IdUnit=%s AND OperationType = %s ORDER BY CompletedAt DESC LIMIT 1", (row_unit['Id'], 17))
                row_calib = cursor.fetchone()
                #print(f'el contenido de row_op: {row_op}\n')

                if row_calib is None:
                    print(f"ROW_CALIB is None. No se encontraron datos de calibración para el SN: {SN}")
                    continue
                
                # Cargar el JSON
                data_json = json.loads(row_calib['Data'])
                Completed_At = row_calib.get("CompletedAt", "N/A")
                
                Calib_test = data_json.get("readed", {})
                
                # Función auxiliar para validar rangos de calibración
                def check_calib(channel, axis):
                    node = Calib_test.get(str(channel), {}).get(axis, {})
                    val = node.get("result", 999)
                    lim = node.get("limit", 0)
                    return val <= lim, val, lim

                c1y_pass, v1y, l1y = check_calib(1, "Y")
                c1z_pass, v1z, l1z = check_calib(1, "Z")
                c2y_pass, v2y, l2y = check_calib(2, "Y")
                c2z_pass, v2z, l2z = check_calib(2, "Z")

                calib_final = "PASS" if all([c1y_pass, c1z_pass, c2y_pass, c2z_pass]) else "FAIL"

                res_text = f"\nResultado Calibración: {calib_final}\n"
                res_text += f"Completado en: {Completed_At}\n"
                res_text += f"\n{'Canal':<10} | {'Valor':<10} | {'Limite':<10}\n"
                res_text += "-"*35 + "\n"
                res_text += f"{'1Y':<10} | {v1y:<10} | {l1y:<10}\n"
                res_text += f"{'1Z':<10} | {v1z:<10} | {l1z:<10}\n"
                res_text += f"{'2Y':<10} | {v2y:<10} | {l2y:<10}\n"
                res_text += f"{'2Z':<10} | {v2z:<10} | {l2z:<10}\n"

                print(f"\n{res_text}")
                f.write(res_text)

    except Exception as e:
        print(f"Error procesando el SN {SN}: {e}")

    print(f"\n{'#'*80}\n")

# Cerrar la conexión
cursor.close()
conn.close()
print("Proceso finalizado.")


