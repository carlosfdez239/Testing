import json
import pandas as pd
import mysql.connector
import os

# Conexión a la base de datos MySQL
conn = mysql.connector.connect(
    host='wsmysqlserverpro.mysql.database.azure.com',
    user='admin_ws',
    password='ws9hnBt54T',
    database='entrega',
    port = '3306'
)

cursor = conn.cursor(dictionary=True)

SN_list = [165111,165119,165134,
165125,165121,165112,165429,165428,165438,165439,165447,165110,165106,165131,165042,165114,165090,165104,
165123,165118,165126,165107,165093,165116,165103,165132,165096,165083,165098,165113,165117,165105,165108,
165453,165087,165115,165120,165099,165094,165124,165435,165431,165430,165420,165437,165446,165432,165415,
164988,165474,165472,
165480,165465,165475,165458,165460,165450,165427,165418,165477,165421,
165483,165417,165481,165476,165479,165413,165462,165464,165467,165473,165362,
165419,165424,165426,165422,165436,165441,165416,165485,165487,165478,165486,165484
]  # Lista con los números de serie que quieres procesar
excel_rows = []

for SN in SN_list:
    cursor.execute("SELECT Data FROM Units WHERE SN=%s", (SN,))
    row = cursor.fetchone()

    if row is None:
        print(f"No se encontraron datos para el SN: {SN}")
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

    # Agregar datos de calibración (como en tu código original)
    Calib_test = data_json.get("CALIBRATOR_CHECK_LIMITS", {}).get("readed", {})
    Canal_1_Y_limit = Calib_test.get("1", {}).get("Y", {}).get("limit")
    Canal_1_Y_result = Calib_test.get("1", {}).get("Y", {}).get("result")
    Canal_1_Z_limit = Calib_test.get("1", {}).get("Z", {}).get("limit")
    Canal_1_Z_result = Calib_test.get("1", {}).get("Z", {}).get("result")
    Canal_2_Y_limit = Calib_test.get("2", {}).get("Y", {}).get("limit")
    Canal_2_Y_result = Calib_test.get("2", {}).get("Y", {}).get("result")
    Canal_2_Z_limit = Calib_test.get("2", {}).get("Z", {}).get("limit")
    Canal_2_Z_result = Calib_test.get("2", {}).get("Z", {}).get("result")

    In_range_Canal_1_Y = "true" if Canal_1_Y_result < Canal_1_Y_limit else "false"
    In_range_Canal_1_Z = "true" if Canal_1_Z_result < Canal_1_Z_limit else "false"
    In_range_Canal_2_Y = "true" if Canal_2_Y_result < Canal_2_Y_limit else "false"
    In_range_Canal_2_Z = "true" if Canal_2_Z_result < Canal_2_Z_limit else "false"

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

cursor.close()
conn.close()

# Crear DataFrame y guardar Excel
excel_file = 'informe_Elausa_BXLH.xlsx'
if os.path.exists(excel_file):
    df_existente = pd.read_excel(excel_file)
    df_nuevo = pd.DataFrame(excel_rows)
    df_final = pd.concat([df_existente, df_nuevo], ignore_index=True)
else:
    df_final = pd.DataFrame(excel_rows)

df_final.to_excel(excel_file, index=False)
print(f'Informe Excel generado: {excel_file}')
