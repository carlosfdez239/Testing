'''
Autor: C. Fdez
Fecha: 02/07/2025
rev: 0
Descripción: Listado de los serials de un producto que han sido testeados en EOL
             y extracción de los datos de los tests realizados


To Do

    [] Implementar misma estructura para START_FW
    [] Implementar misma estructura para CALIBRATOR_CHECK_LIMITS
    [] Implementar misma estructura para CALIBRATOR_RESET_DEVICE
    [] Implementar misma estructura para CALIBRATOR_SET_DEVICE_PARAMS
    [] Cambiar las sentencias if elif por match case
        # Example: API response status code handling
        
        status_code = 200

        match status_code:
            case 200:
                print("Request succeeded.")
            case 404:
                print("Resource not found.")
            case 500:
                print("Server error. Please try again later.")
            case _:
                print("Unknown status code.")

    [] Pasar las implementaciones a funciones def
    [] Implementar la opción de generar un informe pdf

    [] Implementar entorno gráfico tkinter


Dependencias

sudo apt install python3-mysql.connector

'''


import mysql.connector
import json
import subprocess
import os
import pandas as pd
import Color_Text as color
#from colorama import Fore, Style, Back

# Lista de los numeros de serie a analizar
# 161577,161645,175741, no hay datos

SN_list = []


excel_rows = []


# Conexión a la base de datos MySQL
conn = mysql.connector.connect(
    host='wsmysqlserverpro.mysql.database.azure.com',
    user='admin_ws',
    password='ws9hnBt54T',
    database='entrega',
    port = '3306'
)
cursor = conn.cursor(dictionary=True)

#TIL = input(color.color_text(f"\nlos serials son TIL? ", color.AMARILLO))
#if "S" in TIL or "s" in TIL:
TIL = True
#else:
#    TIL = False

try:
    # Ejecutar la consulta
    cursor.execute("""
        SELECT u.SN, u.StartAt AS Data, u.DATA, p.PartNo, b.Id AS BatchId,
               b.BatchNumber, pr.Name AS ProcessName, pr.Version AS ProcessVersion,
               u.CompletedAt, u.UnitResult
        FROM products p
        JOIN processes pr ON pr.IdProduct = p.Id
        JOIN batches b ON b.IdProcess = pr.Id
        JOIN units u ON u.IdBatch = b.Id
        WHERE p.Id = '55243a04-90ef-4ff0-98e0-45ed9de2b95e'
          AND pr.Id = '4b1cb05a-5a1b-455a-b396-1e5819c89888'
        ORDER BY b.BatchNumber, u.SN
    """)

    # Guardar todos los resultados en SN_list
    SN_list = cursor.fetchall()  

    #print(f"Contenido de SN_list ({len(SN_list)} registros):\n", SN_list)

except mysql.connector.Error as e:
    print(f"Error en la adquisición de los datos: {e}")

'''
for SN in SN_list:
        try:
            # SN = input("Introduce el SN del equipo --> ")
            cursor.execute("SELECT Data FROM Units WHERE SN="+str(SN))
            row = cursor.fetchone()
            if row is None:
                print(f"No se encontraron datos para el SN: {SN}")
                continue

            # Cargar el JSON desde la columna 'Data'
            data_json = json.loads(row['Data'])

            # Obtener la parte de interés
            Eol_test = data_json.get("EOL_TEST", {})
            decode_data = Eol_test.get("DECODE", {})
            node_model_decode = decode_data.get("NODE_MODEL")
            node_id_decode = decode_data.get("NODE_ID")
            serial_decode = decode_data.get("SERIAL_NUMBER")
            fw_decode = decode_data.get("FIRMWARE_VERSION")
            FW_bin = Eol_test.get("FW_BIN")
            status = Eol_test.get("STATUS")
            if status =="success":
                status = "PASS"

            # Obtener los datos de Test_1
            test1 = Eol_test.get("TEST_1", {}).get("CURR_POWER_UP", {}).get("In_Range")

            # Obtener los datos de Test_2
            test2 = Eol_test.get("TEST_2", {}).get("BATT", {}).get("In_Range")

            # Obtener los datos de Test_10
            test10 = Eol_test.get("TEST_10", {}).get("TEST_VERSION")

            # Obtener los datos de Test_11
            test11 = Eol_test.get("TEST_11", {}).get("TEST_TEMP_HUM")

            # Obtener los datos de Test_12
            test12 = Eol_test.get("TEST_12", {}).get("TEST_FLASH")

            # Obtener los datos de Test_13
            test13 = Eol_test.get("TEST_13", {}).get("V_BATT", {}).get("In_Range")

            # Obtener los datos de Test_14
            test14 = Eol_test.get("TEST_14", {}).get("LOW_POW_CURR", {}).get("In_Range")

            # Obtener los datos de Test_15
            test15 = Eol_test.get("TEST_15", {}).get("FULL_POW_CURR", {}).get("In_Range")

            # Obtener los datos de Test_17
            test17 = Eol_test.get("TEST_17", {}).get("TEST_LORA_TX", {}).get("RSSI").get("In_Range") if Eol_test.get("TEST_17", {}).get("TEST_LORA_TX", {}).get("RSSI") else None   

            # Obtener los datos de Test_18
            test18 = Eol_test.get("TEST_18", {}).get("TEST_LORA_RX", {}).get("RSSI").get("In_Range") if Eol_test.get("TEST_18", {}).get("TEST_LORA_RX", {}).get("RSSI") else None

            # Obtener los datos de Test_21
            test21_X = Eol_test.get("TEST_21", {}).get("TEST_LP_ACC", {}).get("X").get("In_Range") if Eol_test.get("TEST_21", {}).get("TEST_LP_ACC", {}).get("X") else None
            test21_Y = Eol_test.get("TEST_21", {}).get("TEST_LP_ACC", {}).get("Y").get("In_Range") if Eol_test.get("TEST_21", {}).get("TEST_LP_ACC", {}).get("Y") else None
            test21_Z = Eol_test.get("TEST_21", {}).get("TEST_LP_ACC", {}).get("Z").get("In_Range") if Eol_test.get("TEST_21", {}).get("TEST_LP_ACC", {}).get("Z") else None

            # Obtener los datos de Test_22
            test22_X = Eol_test.get("TEST_22", {}).get("TEST_HP_ACC", {}).get("X").get("In_Range") if Eol_test.get("TEST_22", {}).get("TEST_HP_ACC", {}).get("X") else None
            test22_Y = Eol_test.get("TEST_22", {}).get("TEST_HP_ACC", {}).get("Y").get("In_Range") if Eol_test.get("TEST_22", {}).get("TEST_HP_ACC", {}).get("Y") else None
            test22_Z = Eol_test.get("TEST_22", {}).get("TEST_HP_ACC", {}).get("Z").get("In_Range") if Eol_test.get("TEST_22", {}).get("TEST_HP_ACC", {}).get("Z") else None

            # Obtener los datos de Test_23
            test23_X = Eol_test.get("TEST_23", {}).get("TEST_MAG_MMC_Results", {}).get("X").get("In_Range") if Eol_test.get("TEST_23", {}).get("TEST_MAG_MMC_Results", {}).get("X") else None
            test23_Y = Eol_test.get("TEST_23", {}).get("TEST_MAG_MMC_Results", {}).get("Y").get("In_Range") if Eol_test.get("TEST_23", {}).get("TEST_MAG_MMC_Results", {}).get("Y") else None
            test23_Z = Eol_test.get("TEST_23", {}).get("TEST_MAG_MMC_Results", {}).get("Z").get("In_Range") if Eol_test.get("TEST_23", {}).get("TEST_MAG_MMC_Results", {}).get("Z") else None

            # Obtener los datos de Test_24
            test24 = Eol_test.get("TEST_24", {}).get("TEST_LORA_ID")

            # Obtener los datos de Test_26
            test26 = Eol_test.get("TEST_26", {}).get("TEST_STM32_ID")

            # Obtener los datos de Test_35
            test35 = Eol_test.get("TEST_35", {}).get("TEST_BLE_ENABLE")

            # Obtener los datos de Test_36
            test36_FW = Eol_test.get("TEST_36", {}).get("TEST_BLE_FW")
            test36_Check = Eol_test.get("TEST_36", {}).get("BLE_FW_CHECK").get("In_Range") if Eol_test.get("TEST_36", {}).get("BLE_FW_CHECK") else None

            # Obtener los datos de Test_37
            test37 = Eol_test.get("TEST_37", {}).get("TEST_BT_ID")

            # Obtener los datos de Test_38
            test38 = Eol_test.get("TEST_38", {}).get("TEST_BLE_RSSI").get("RSSI").get("In_Range") if Eol_test.get("TEST_38", {}).get("TEST_BLE_RSSI") else None

            # Obtener los datos de Test_55
            test55 = Eol_test.get("TEST_55", {}).get("TEST_LORA_TX 868000 14 7")

            # Obteneer datos de los checks finales
            final_check_MAC_read =  Eol_test.get("COMPARATION", {}).get("MAC", {}).get("Read")
            final_check_MAC_check =  Eol_test.get("COMPARATION", {}).get("MAC", {}).get("In_Range")
                                                    
            final_check_PRCODE_read =  Eol_test.get("COMPARATION", {}).get("PRCODE", {}).get("Read")
            final_check_PRCODE_check =  Eol_test.get("COMPARATION", {}).get("PRCODE", {}).get("In_Range")

            final_check_SERIAL_read =  Eol_test.get("COMPARATION", {}).get("SERIAL", {}).get("Read")
            final_check_SERIAL_check =  Eol_test.get("COMPARATION", {}).get("SERIAL", {}).get("In_Range")

            final_check_FW_VERSION_read =  Eol_test.get("COMPARATION", {}).get("FW_VERSION", {}).get("Read")
            final_check_FW_VERSION_check =  Eol_test.get("COMPARATION", {}).get("FW_VERSION", {}).get("In_Range")

            final_check_HW_VERSION_read =  Eol_test.get("COMPARATION", {}).get("HW_VERSION", {}).get("Read")
            final_check_HW_VERSION_check =  Eol_test.get("COMPARATION", {}).get("HW_VERSION", {}).get("In_Range")


            # Obtener resultados de la calibración
            if TIL:
                Calib_test = data_json.get("CALIBRATOR_CHECK_LIMITS", {}).get("readed", {})
                Canal_1_Y_limit = Calib_test.get("1", {}).get("Y", {}).get("limit")
                Canal_1_Y_result = Calib_test.get("1", {}).get("Y", {}).get("result")
                Canal_1_Z_limit = Calib_test.get("1", {}).get("Z", {}).get("limit")
                Canal_1_Z_result = Calib_test.get("1", {}).get("Z", {}).get("result")
                Canal_2_Y_limit = Calib_test.get("2", {}). get("Y", {}).get("limit")
                Canal_2_Y_result = Calib_test.get("2", {}).get("Y", {}).get("result")
                Canal_2_Z_limit = Calib_test.get("2", {}).get("Z", {}).get("limit")
                Canal_2_Z_result = Calib_test.get("2", {}).get("Z", {}).get("result")

                # Comparar resultados de la calibración
                if Canal_1_Y_result <= Canal_1_Y_limit:
                    In_range_Canal_1_Y = "true"
                else:
                    In_range_Canal_1_Y = "false"

                if Canal_1_Z_result <= Canal_1_Z_limit:
                    In_range_Canal_1_Z = "true"
                else:
                    In_range_Canal_1_Z = "false"    

                if Canal_2_Y_result <= Canal_2_Y_limit:
                    In_range_Canal_2_Y = "true"
                else:
                    In_range_Canal_2_Y = "false"    

                if Canal_2_Z_result <= Canal_2_Z_limit:
                    In_range_Canal_2_Z = "true"
                else:
                    In_range_Canal_2_Z = "false"

                if (In_range_Canal_1_Y == "true" and
                    In_range_Canal_1_Z == "true" and
                    In_range_Canal_2_Y == "true" and
                    In_range_Canal_2_Z == "true"):
                    Calibracion_Check = "PASS"
                else:
                    Calibracion_Check = "FAIL"
                data = {
                    "SN": SN,
                    "node_model": node_model_decode,
                    "node_id": node_id_decode,
                    "serial": serial_decode,
                    "fw": fw_decode,
                    "FW_bin": FW_bin,
                    "EOL_Test": status,
                    "Calibracion_Check": Calibracion_Check,
                    "TEST_1": test1,
                    "TEST_2": test2,
                    "TEST_10": test10,
                    "TEST_11": test11,
                    "TEST_12": test12,
                    "TEST_13": test13,
                    "TEST_14": test14,
                    "TEST_15": test15,
                    "TEST_17": test17,
                    "TEST_18": test18,
                    "TEST_21_X": test21_X,
                    "TEST_21_Y": test21_Y,
                    "TEST_21_Z": test21_Z,
                    "TEST_22_X": test22_X,
                    "TEST_22_Y": test22_Y,
                    "TEST_22_Z": test22_Z,
                    "TEST_23_X": test23_X,
                    "TEST_23_Y": test23_Y,
                    "TEST_23_Z": test23_Z,
                    "TEST_24": test24,
                    "TEST_26": test26,
                    "TEST_35": test35,
                    "TEST_36_FW": test36_FW,
                    "TEST_36_Check": test36_Check,
                    "TEST_37": test37,
                    "TEST_38": test38,
                    "TEST_55": test55,
                    "Final_Check_MAC_Read": final_check_MAC_read,
                    "Final_Check_MAC_In_Range": final_check_MAC_check,
                    "Final_Check_PRCODE_Read": final_check_PRCODE_read,
                    "Final_Check_PRCODE_In_Range": final_check_PRCODE_check,
                    "Final_Check_SERIAL_Read": final_check_SERIAL_read,
                    "Final_Check_SERIAL_In_Range": final_check_SERIAL_check,
                    "Final_Check_FW_VERSION_Read": final_check_FW_VERSION_read,
                    "Final_Check_FW_VERSION_In_Range": final_check_FW_VERSION_check,
                    "Final_Check_HW_VERSION_Read": final_check_HW_VERSION_read,
                    "Final_Check_HW_VERSION_In_Range": final_check_HW_VERSION_check,
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
                    "Calib_Canal_2_Z_In_Range": In_range_Canal_2_Z
                }
                excel_rows.append(data)
                data_resumen = {
                    "SN": SN,
                    "node_model": node_model_decode,
                    "node_id": node_id_decode,
                    "serial": serial_decode,
                    "fw": fw_decode,
                    "FW_bin": FW_bin,
                    "EOL_Test": status,
                    "Calibracion_Check": Calibracion_Check,
                }
            else:

                # Generar datos Json para el informe
                data = {
                    "SN": SN,
                    "node_model": node_model_decode,
                    "node_id": node_id_decode,
                    "serial": serial_decode,
                    "fw": fw_decode,
                    "FW_bin": FW_bin,
                    "EOL_Test": status,
                    "Calibracion_Check": "N/A",  # No aplica si no es TIL
                    "TEST_1": test1,
                    "TEST_2": test2,
                    "TEST_10": test10,
                    "TEST_11": test11,
                    "TEST_12": test12,
                    "TEST_13": test13,
                    "TEST_14": test14,
                    "TEST_15": test15,
                    "TEST_17": test17,
                    "TEST_18": test18,
                    "TEST_21_X": test21_X,
                    "TEST_21_Y": test21_Y,
                    "TEST_21_Z": test21_Z,
                    "TEST_22_X": test22_X,
                    "TEST_22_Y": test22_Y,
                    "TEST_22_Z": test22_Z,
                    "TEST_23_X": test23_X,
                    "TEST_23_Y": test23_Y,
                    "TEST_23_Z": test23_Z,
                    "TEST_24": test24,
                    "TEST_26": test26,
                    "TEST_35": test35,
                    "TEST_36_FW": test36_FW,
                    "TEST_36_Check": test36_Check,
                    "TEST_37": test37,
                    "TEST_38": test38,
                    "TEST_55": test55,
                    "Final_Check_MAC_Read": final_check_MAC_read,
                    "Final_Check_MAC_In_Range": final_check_MAC_check,
                    "Final_Check_PRCODE_Read": final_check_PRCODE_read,
                    "Final_Check_PRCODE_In_Range": final_check_PRCODE_check,
                    "Final_Check_SERIAL_Read": final_check_SERIAL_read,
                    "Final_Check_SERIAL_In_Range": final_check_SERIAL_check,
                    "Final_Check_FW_VERSION_Read": final_check_FW_VERSION_read,
                    "Final_Check_FW_VERSION_In_Range": final_check_FW_VERSION_check,
                    "Final_Check_HW_VERSION_Read": final_check_HW_VERSION_read,
                    "Final_Check_HW_VERSION_In_Range": final_check_HW_VERSION_check,

                }

                excel_rows.append(data)
                data_resumen = {
                    "SN": SN,
                    "node_model": node_model_decode,
                    "node_id": node_id_decode,
                    "serial": serial_decode,
                    "fw": fw_decode,
                    "FW_bin": FW_bin,
                    "EOL_Test": status,
                    "Calibracion_Check": data.get("Calibracion_Check", "N/A") # No aplica si no es TIL,
                
                }
            #nombre_informe = f'informe_pruebas_equipo_{SN}.pdf'
            #json_string = json.dumps(data_resumen, indent=4)
            #nombre_informe = f'informe_extendido_equipo_{SN}.pdf'
            json_string = json.dumps(data, indent=4)
            #subprocess.run(["python3", "Generar_informe_pdf.py",nombre_informe, json_string], check=True)   
        except TypeError:
            print(f"Error en la adquisición de los datos para el serial {SN}\n")'''

for Sn in SN_list:
    print(f"Procesado SN: {Sn['SN']} - Resultado: {Sn['UnitResult']} - Fecha: {Sn['CompletedAt']} - Lote: {Sn['BatchNumber']}")
    data = {
        "SN": Sn['SN'],
        "Resultado": Sn['UnitResult'],
        "Fecha": Sn['CompletedAt'],
        "Lote": Sn['BatchNumber'],
        "Data": Sn['DATA'],
        "PartNo": Sn['PartNo'],
        "BatchId": Sn['BatchId'],
        "ProcessName": Sn['ProcessName'],
    }  
    excel_rows.append(data)
excel_file = 'listado total Serials BXLH-W-2 producidos.xlsx'
if os.path.exists(excel_file):
    df_existente = pd.read_excel(excel_file)
    df_nuevo = pd.DataFrame(excel_rows)
    df_final = pd.concat([df_existente, df_nuevo], ignore_index=True)
else:
    df_final = pd.DataFrame(excel_rows)
# Guardar el DataFrame en un archivo Excel
df_final.to_excel(excel_file, index=False)
print(f'Informe Excel generado: {excel_file} en ')
# Cerrar la conexión a la base de datos
    

cursor.close()
conn.close()


