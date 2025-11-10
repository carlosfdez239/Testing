'''
Autor: C. Fdez
Fecha: 02/07/2025
rev: 0
Descripción: Validador datos de producción para equipos Montronic


To Do:
    [X] Implementar la función para generar el archivo Excel.
    [X] Validar los datos de calibración y tests.
    [X] Añadir resultados de calibración al Excel.
    [X] Manejar errores de conexión a la base de datos.
    [X] Añadir colores a los mensajes de estado.
    [ ] Añadir extracción del modelo de producto para adjuntar calibración al Excel.
    [ ] Añadir entrada de números de serie desde un archivo o consola.
'''

import json
import pandas as pd
import mysql.connector
import os
import Color_Text as color

# Conexión a la base de datos MySQL
conn = mysql.connector.connect(
    host='wsmysqlserverpro.mysql.database.azure.com',
    user='admin_ws',
    password='ws9hnBt54T',
    database='entrega',
    port = '3306'
)

cursor = conn.cursor(dictionary=True)
TIL = input(color.color_text(f"\nlos serials son TIL? ", color.AMARILLO))
if "Si" in TIL or "si" in TIL:
    TIL = True
else:
    TIL = False

 # Lista con los números de serie que quieres procesar

SN_list = [175435,175453,175436,175464,175444,
175475,175486,175465,175455,175467,175493,175450,175481,175470,175460,
175431,175417,175479,175490,175428,175382,175468,175483,175456,175396,
175449,175363,175419,175344,175489,175492,175430,175473,175480,175368,
175377,175358,175366,175305,175262,175440,175365,175362,175364,175332,175427,175403,175378] 
input_SN = input(color.color_text("Introduce los números de serie separados por comas: ", color.BLANCO))
#if input_SN:
#    SN_list = [sn.strip() for sn in input_SN.split(',') if sn.strip()]  
#else:
#    print(color.color_text("No se introdujeron números de serie. Saliendo del programa.", color.ROJO))
#    exit()
excel_rows = []

for SN in SN_list:
    cursor.execute("SELECT Data FROM Units WHERE SN=%s", (SN,))
    row = cursor.fetchone()

    if row is None:
        print(color.color_text(f"No se encontraron datos para el SN: {SN}", color.ROJO))
        continue

    data_json = json.loads(row['Data'])
    

    # Extraer tests tanto SET_FW como START_FW
    fixture = data_json.get("ELAUSA_FIXTURE_SOCKET", {}).get("EOL", {})
    set_fw_tests = fixture.get("SET_FW", [])
    start_fw_tests = fixture.get("START_FW", [])

    all_tests = set_fw_tests + start_fw_tests

    test_results = {}

    serial_number = None
    for test in all_tests:
        cmd_info = test.get("CommandInfo", {})
        serial_number = cmd_info.get("SerialNumber", SN)  # fallback a SN si no hay SerialNumber

        test_name = cmd_info.get("TEST", "UnknownTest")
        data_dict = cmd_info.get("Data", {})

        # Aplanamos cada clave/valor de Data en columnas con nombre <test_name>_<key>
        for key, value in data_dict.items():
            # Reemplazar puntos por coma si es string para formato numérico decimal europeo
            if isinstance(value, str):
                value = value.replace('.', ',')
            column_name = f"{test_name}_{key}"
            test_results[column_name] = value

    # Agregar datos de calibración
    if TIL:
        Calib_test = data_json.get("CALIBRATOR_CHECK_LIMITS", {}).get("readed", {})
        Canal_1_Y_limit = Calib_test.get("1", {}).get("Y", {}).get("limit")
        Canal_1_Y_result = Calib_test.get("1", {}).get("Y", {}).get("result")
        Canal_1_Z_limit = Calib_test.get("1", {}).get("Z", {}).get("limit")
        Canal_1_Z_result = Calib_test.get("1", {}).get("Z", {}).get("result")
        Canal_2_Y_limit = Calib_test.get("2", {}).get("Y", {}).get("limit")
        Canal_2_Y_result = Calib_test.get("2", {}).get("Y", {}).get("result")
        Canal_2_Z_limit = Calib_test.get("2", {}).get("Z", {}).get("limit")
        Canal_2_Z_result = Calib_test.get("2", {}).get("Z", {}).get("result")

        In_range_Canal_1_Y = "true" if Canal_1_Y_result <= Canal_1_Y_limit else "false"
        In_range_Canal_1_Z = "true" if Canal_1_Z_result <= Canal_1_Z_limit else "false"
        In_range_Canal_2_Y = "true" if Canal_2_Y_result <= Canal_2_Y_limit else "false"
        In_range_Canal_2_Z = "true" if Canal_2_Z_result <= Canal_2_Z_limit else "false"

        Calibracion_Check = "PASS" if (In_range_Canal_1_Y == "true" and In_range_Canal_1_Z == "true" and
                                    In_range_Canal_2_Y == "true" and In_range_Canal_2_Z == "true") else "FAIL"

        # Construir fila de datos
        data_row = {
            "SN": SN,
            "SerialNumber": serial_number,
            "Calibracion_Check": Calibracion_Check,
            "Calib_Canal_1_Y_Result": Canal_1_Y_result,
            "Calib_Canal_1_Y_Limit": Canal_1_Y_limit,
            "Calib_Canal_1_Y_In_Range": In_range_Canal_1_Y,
            "Calib_Canal_1_Z_Result": Canal_1_Z_result,
            "Calib_Canal_1_Z_Limit": Canal_1_Z_limit,
            "Calib_Canal_1_Z_In_Range": In_range_Canal_1_Z,
            "Calib_Canal_2_Y_Result": Canal_2_Y_result,
            "Calib_Canal_2_Y_Limit": Canal_2_Y_limit,
            "Calib_Canal_2_Y_In_Range": In_range_Canal_2_Y,
            "Calib_Canal_2_Z_Result": Canal_2_Z_result,
            "Calib_Canal_2_Z_Limit": Canal_2_Z_limit,
            "Calib_Canal_2_Z_In_Range": In_range_Canal_2_Z,
        }

        # Añadir resultados de tests
        data_row.update(test_results)
        excel_rows.append(data_row)
    else:
        # Si no es TIL, solo guardamos los resultados de los tests
        data_row = {
            "SN": SN,
            "SerialNumber": serial_number,
        }
        data_row.update(test_results)
        excel_rows.append(data_row)
    


cursor.close()
conn.close()

# Crear DataFrame y guardar Excel
excel_file = '~/Documentos/Testing/informe_Elausa_BXLH.xlsx'
if os.path.exists(excel_file):
    df_existente = pd.read_excel(excel_file)
    df_nuevo = pd.DataFrame(excel_rows)
    df_final = pd.concat([df_existente, df_nuevo], ignore_index=True)
else:
    df_final = pd.DataFrame(excel_rows)

df_final.to_excel(excel_file, index=False)
print(color.color_text(f"Informe Excel generado: {excel_file}", color.VERDE))
