'''
Autor: C. Fdez
Fecha: 02/07/2025
rev: 0
Descripción: Validador datos de producción para equipos Montronic


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
import datetime
#from colorama import Fore, Style, Back

# Lista de los numeros de serie a analizar
# 161577,161645,175741, no hay datos

SN_list = [182321,
#182343,182324,182327,182336,182404,182334,182393,
#182391,182386,182396,182387,182381,182314,182319,182344
]


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

TIL = input(color.color_text(f"\nlos serials son TIL? ", color.AMARILLO))
if "S" in TIL or "s" in TIL:
    TIL = True
else:
    TIL = False

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
            Eol_test = data_json.get("EOL", {})
            Type_Eol = Eol_test.get("Type")
            Cmd_Eol = Eol_test.get("Cmd")
            Status_Eol = Eol_test.get("Status")
            serial_Eol = Eol_test.get("Serial")
            Info_Eol = Eol_test.get("Info", {})
            Fixture_Id = Info_Eol.get("FixtureId")
            Fixture_cassette = Info_Eol.get("Cassette")
            
            if Status_Eol =="COMPLETE":
                Status_Eol = "PASS"
            Eol_step = Eol_test.get("Step")
            print(f"\nAnálisis del SN: {SN}")
            print(f"Tipo de prueba EOL: {Type_Eol}")
            print(f"Comando EOL: {Cmd_Eol}")
            print(f"Estado de la prueba EOL: {Status_Eol}")
            print(f"Serial leído en EOL: {serial_Eol}")
            print(f"Fixture ID: {Fixture_Id}")
            print(f"Cassette del fixture: {Fixture_cassette}\n")
            print (f"===================== Detalles de las pruebas EOL ====================\n")
            
            nombre = f'Informe_EOL_SN_{SN}.txt'
            Eol_data_Test = Eol_test.get("Tests", [])
            with open(nombre, 'a') as f:
                f.write(f"Análisis del SN: {SN}\n")
                f.write(f"Tipo de prueba EOL: {Type_Eol}\n")
                f.write(f"Comando EOL: {Cmd_Eol}\n")
                f.write(f"Estado de la prueba EOL: {Status_Eol}\n")
                f.write(f"Serial leído en EOL: {serial_Eol}\n")
                f.write(f"Fixture ID: {Fixture_Id}\n")
                f.write(f"Cassette del fixture: {Fixture_cassette}\n\n")
                f.write (f"===================== Detalles de las pruebas EOL ====================\n\n")
                for element in Eol_data_Test:
                    Test_Name = element.get("Description")
                    Data_value = element.get("DataValue")
                    Data_Max = element.get("DataMax")
                    Data_Min = element.get("DataMin")
                    Test_Result = element.get("Result")
                    Units = element.get("Units")
                    print(f"{SN} - {Test_Name}: {Data_value} {Units} (Min: {Data_Min}, Max: {Data_Max} - Result: {Test_Result}")
                    f.write(f"\t{Test_Name}:\t Min: {Data_Min}\t Value: {Data_value}\t Max: {Data_Max} {Units}\t- Result: {Test_Result}\n")

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
        except TypeError:
            print(f"Error en la adquisición de los datos para el serial {SN}\n")

        print(f"#######################################################################################################\n")

# Cerrar la conexión a la base de datos
cursor.close()
conn.close()
'''
               
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
            print(f"Error en la adquisición de los datos para el serial {SN}\n")
            
fecha = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')                           
excel_file = f'informe_Nuevo_Json + {fecha}+.xlsx'
if os.path.exists(excel_file):
    df_existente = pd.read_excel(excel_file)
    df_nuevo = pd.DataFrame(excel_rows)
    df_final = pd.concat([df_existente, df_nuevo], ignore_index=True)
else:
    df_final = pd.DataFrame(excel_rows)
# Guardar el DataFrame en un archivo Excel
df_final.to_excel(excel_file, index=False)
print(f'Informe Excel generado: {excel_file} en ')
'''


