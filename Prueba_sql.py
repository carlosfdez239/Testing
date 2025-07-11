'''
Autor: C. Fdez
Fecha: 19/05/2025
rev: 0
Descripción: Validador datos de producción


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
#from colorama import Fore, Style, Back

# Conexión a la base de datos MySQL
conn = mysql.connector.connect(
    host='wsmysqlserverpro.mysql.database.azure.com',
    user='admin_ws',
    password='ws9hnBt54T',
    database='entrega',
    port = '3306'
)

#Elausa BXLH[152621,152650,152645,152626,152649,152633,152643,152631,152637,152630,152634,152617,152639,152654,152653,152632,152619,152622,152646,152620]
#SN_list = [165835]

cursor = conn.cursor(dictionary=True)
SN = input("Introduce el SN del equipo --> ")
cursor.execute("SELECT Data FROM Units WHERE SN="+SN)
row = cursor.fetchone()

# Cargar el JSON desde la columna 'Data'
data_json = json.loads(row['Data'])

# Obtener la parte de interés
fixture_data = data_json.get("ELAUSA_FIXTURE_SOCKET", {})
eol_data = fixture_data.get("EOL", {})
set_fw_tests = eol_data.get("SET_FW", [])
start_fw = eol_data.get("START_FW")

Calibrator_data = data_json.get("CALIBRATOR_CHECK_LIMITS", {})
read = Calibrator_data.get("readed", {})
plano_1 = read.get("1",{})
plano_1_Y = plano_1.get("Y", {})
plano_1_Z = plano_1.get("Z", {})
plano_2 = read.get("2", {})
plano_2_Y= plano_2.get("Y", {})
plano_2_Z= plano_2.get("Z", {})

def to_float(value, default = 0.0):
    try:
        return float(str(value).strip())
    except (ValueError, TypeError):
        return default

# Recorremos cada test para set_fw_test
for test in set_fw_tests:
    test_name = test.get("CommandInfo", {}).get("TEST", "Sin nombre")
    
    if "ETAPA 1" in test_name:
        max = to_float(test.get("CommandInfo", {}).get("Data", {}).get("Data_Max", 0))
        min = to_float(test.get("CommandInfo", {}).get("Data", {}).get("Data_Min",0))
        value = to_float(test.get("CommandInfo", {}).get("Data", {}).get("Data_Value", 0))
        result = test.get("CommandInfo", {}).get("Data", {}).get("Result", "Sin resultado")
        if max > value > min:
                print(f"Test: {test_name}, Max: {max}, Valor: {value}, Min: {min}, Resultado_test: {result}, Resultado_control: ok")

    elif "ETAPA 2" in test_name:
        max = to_float(test.get("CommandInfo", {}).get("Data", {}).get("Data_Max", 0))
        min = to_float(test.get("CommandInfo", {}).get("Data", {}).get("Data_Min",0))
        value = to_float(test.get("CommandInfo", {}).get("Data", {}).get("Data_Value", 0))
        result = test.get("CommandInfo", {}).get("Data", {}).get("Result", "Sin resultado")
        if max > value > min:
                print(f"Test: {test_name}, Max: {max}, Valor: {value}, Min: {min}, Resultado_test: {result}, Resultado_control: ok")

    elif "ETAPA 3" in test_name:
        max = to_float(test.get("CommandInfo", {}).get("Data", {}).get("Data_Max", 0))
        min = to_float(test.get("CommandInfo", {}).get("Data", {}).get("Data_Min",0))
        value = to_float(test.get("CommandInfo", {}).get("Data", {}).get("Data_Value", 0))
        result = test.get("CommandInfo", {}).get("Data", {}).get("Result", "Sin resultado")
        if max > value > min:
                print(f"Test: {test_name}, Max: {max}, Valor: {value}, Min: {min}, Resultado_test: {result}, Resultado_control: ok")

    elif "ETAPA 4" in test_name:
        max = to_float(test.get("CommandInfo", {}).get("Data", {}).get("Data_Max", 0))
        min = to_float(test.get("CommandInfo", {}).get("Data", {}).get("Data_Min",0))
        value = to_float(test.get("CommandInfo", {}).get("Data", {}).get("Data_Value", 0))
        result = test.get("CommandInfo", {}).get("Data", {}).get("Result", "Sin resultado")
        if max > value > min:
                print(f"Test: {test_name}, Max: {max}, Valor: {value}, Min: {min}, Resultado_test: {result}, Resultado_control: ok")

     
                
    elif "ETAPA 5" in test_name:
        max = test.get("CommandInfo", {}).get("Data", {}).get("Data_Max", 0)
        min = test.get("CommandInfo", {}).get("Data", {}).get("Data_Min",0)
        result = test.get("CommandInfo", {}).get("Data", {}).get("Result", "Sin resultado")
        value = test.get("CommandInfo", {}).get("Data", {}).get("Data_Value", 0)
        if "OK" in value:
             print(f"Test: {test_name}, Expected: OK, Valor: {value}, Resultado_test: {result}, Resultado_control: ok")


    elif "ETAPA 6" in test_name:
        max = to_float(test.get("CommandInfo", {}).get("Data", {}).get("Data_Max", 0))
        min = to_float(test.get("CommandInfo", {}).get("Data", {}).get("Data_Min",0))
        value = to_float(test.get("CommandInfo", {}).get("Data", {}).get("Data_Value", 0))
        result = test.get("CommandInfo", {}).get("Data", {}).get("Result", "Sin resultado")
        if max > value > min:
                print(f"Test: {test_name}, Max: {max}, Valor: {value}, Min: {min}, Resultado_test: {result}, Resultado_control: ok")

    elif "ETAPA 7" in test_name:
        max = to_float(test.get("CommandInfo", {}).get("Data", {}).get("Data_Max", 0))
        min = to_float(test.get("CommandInfo", {}).get("Data", {}).get("Data_Min",0))
        value = to_float(test.get("CommandInfo", {}).get("Data", {}).get("Data_Value", 0))
        result = test.get("CommandInfo", {}).get("Data", {}).get("Result", "Sin resultado")
        if max > value > min:
                print(f"Test: {test_name}, Max: {max}, Valor: {value}, Min: {min}, Resultado_test: {result}, Resultado_control: ok")


    elif "ETAPA 8" in test_name:
    #    maximo_X= maximo[0]
    #    maximo_Y= maximo[1]
    #    maximo_Z= maximo[2]
    #    minimo = min.split(";")
    #    minimo_x = minimo[0]
    #    minimo_y = minimo[1]
    #    minimo_z = minimo[2]
        max_X = to_float(test.get("CommandInfo", {}).get("Data", {}).get("Data_Max_X",0))
        max_Y = to_float(test.get("CommandInfo", {}).get("Data", {}).get("Data_Max_Y",0))
        max_Z = to_float(test.get("CommandInfo", {}).get("Data", {}).get("Data_Max_Z",0))
        min_X = to_float(test.get("CommandInfo", {}).get("Data", {}).get("Data_Min_X",0))
        min_Y = to_float(test.get("CommandInfo", {}).get("Data", {}).get("Data_Min_Y",0))
        min_Z = to_float(test.get("CommandInfo", {}).get("Data", {}).get("Data_Min_Z",0))
        value_x = to_float(test.get("CommandInfo", {}).get("Data", {}).get("Data_Value X",0))
        value_y = to_float(test.get("CommandInfo", {}).get("Data", {}).get("Data_Value Y",0))
        value_z = to_float(test.get("CommandInfo", {}).get("Data", {}).get("Data_Value Z",0))
        result = test.get("CommandInfo", {}).get("Data", {}).get("Result", "Sin resultado")
        if max_X > value_x > min_X :
            print(f"Test: {test_name}, Max: {max_X}, Valor X: {value_x}, Min: {min_X}, Resultado: {result}, Resultado_control: ok")
        if max_Y > value_y > min_Y :
            print(f"Test: {test_name}, Max: {max_Y}, Valor Y: {value_y}, Min: {min_Y}, Resultado: {result}, Resultado_control: ok")
        if max_Z > value_z > min_Z :
           print(f"Test: {test_name}, Max: {max_Z}, Valor Z: {value_z}, Min: {min_Z}, Resultado: {result}, Resultado_control: ok")    

    elif "ETAPA 9" in test_name:
        
        max_X = to_float(test.get("CommandInfo", {}).get("Data", {}).get("Data_Max_X",0))
        max_Y = to_float(test.get("CommandInfo", {}).get("Data", {}).get("Data_Max_Y",0))
        max_Z = to_float(test.get("CommandInfo", {}).get("Data", {}).get("Data_Max_Z",0))
        min_X = to_float(test.get("CommandInfo", {}).get("Data", {}).get("Data_Min_X",0))
        min_Y = to_float(test.get("CommandInfo", {}).get("Data", {}).get("Data_Min_Y",0))
        min_Z = to_float(test.get("CommandInfo", {}).get("Data", {}).get("Data_Min_Z",0))
        value_x = to_float(test.get("CommandInfo", {}).get("Data", {}).get("Data_Value X",0))
        value_y = to_float(test.get("CommandInfo", {}).get("Data", {}).get("Data_Value Y",0))
        value_z = to_float(test.get("CommandInfo", {}).get("Data", {}).get("Data_Value Z",0))
        result = test.get("CommandInfo", {}).get("Data", {}).get("Result", "Sin resultado")
        if max_X > value_x > min_X :
            print(f"Test: {test_name}, Max: {max_X}, Valor X: {value_x}, Min: {min_X}, Resultado: {result}, Resultado_control: ok")
        if max_Y > value_y > min_Y :
            print(f"Test: {test_name}, Max: {max_Y}, Valor Y: {value_y}, Min: {min_Y}, Resultado: {result}, Resultado_control: ok")
        if max_Z > value_z > min_Z :
            print(f"Test: {test_name}, Max: {max_Z}, Valor Z: {value_z}, Min: {min_Z}, Resultado: {result}, Resultado_control: ok")    
    
    elif "ETAPA 10" in test_name:
        print(f'contenido de Etapa 10 --> {test}')
        max_X = to_float(test.get("CommandInfo", {}).get("Data", {}).get("Data_Max_X",0))
        print(f'max_X --> {max_X}')
        max_Y = to_float(test.get("CommandInfo", {}).get("Data", {}).get("Data_Max_Y",0))
        print(f'max_Y --> {max_Y}')
        max_Z = to_float(test.get("CommandInfo", {}).get("Data", {}).get("Data_Max_Z",0))
        print(f'max_Z --> {max_Z}')
        min_X = to_float(test.get("CommandInfo", {}).get("Data", {}).get("Data_Min_X",0))
        print(f'min_X --> {min_X}')
        min_Y = to_float(test.get("CommandInfo", {}).get("Data", {}).get("Data_Min_Y",0))
        print(f'min_Y --> {min_Y}')
        min_Z = to_float(test.get("CommandInfo", {}).get("Data", {}).get("Data_Min_Z",0))
        print(f'min_Z --> {min_Z}')
        value_x = to_float(test.get("CommandInfo", {}).get("Data", {}).get("Data_Value X",0))
        print(f'value_X --> {value_x}')
        value_y = to_float(test.get("CommandInfo", {}).get("Data", {}).get("Data_Value Y",0))
        print(f'value_Y --> {value_y}')
        value_z = to_float(test.get("CommandInfo", {}).get("Data", {}).get("Data_Value Z",0))
        print(f'value_z --> {value_z}')
        result = test.get("CommandInfo", {}).get("Data", {}).get("Result", "Sin resultado")
        if max_X > value_x > min_X :
            print(f"Test: {test_name}, Max: {max_X}, Valor X: {value_x}, Min: {min_X}, Resultado: {result}, Resultado_control: ok")
        if max_Y > value_y > min_Y :
            print(f"Test: {test_name}, Max: {max_Y}, Valor Y: {value_y}, Min: {min_Y}, Resultado: {result}, Resultado_control: ok")
        if max_Z > value_z > min_Z :
            print(f"Test: {test_name}, Max: {max_Z}, Valor Z: {value_z}, Min: {min_Z}, Resultado: {result}, Resultado_control: ok")
    
    elif "ETAPA 11" in test_name:
        max = to_float(test.get("CommandInfo", {}).get("Data", {}).get("Data_Max", 0))
        min = to_float(test.get("CommandInfo", {}).get("Data", {}).get("Data_Min",0))
        value = to_float(test.get("CommandInfo", {}).get("Data", {}).get("Data_Value", 0))
        result = test.get("CommandInfo", {}).get("Data", {}).get("Result", "Sin resultado")
        if max > value > min:
                print(f"Test: {test_name}, Max: {max}, Valor: {value}, Min: {min}, Resultado_test: {result}, Resultado_control: ok")
    elif "ETAPA 12" in test_name:
        max = to_float(test.get("CommandInfo", {}).get("Data", {}).get("Data_Max", 0))
        min = to_float(test.get("CommandInfo", {}).get("Data", {}).get("Data_Min",0))
        value = to_float(test.get("CommandInfo", {}).get("Data", {}).get("Data_Value", 0))
        result = test.get("CommandInfo", {}).get("Data", {}).get("Result", "Sin resultado")
        if max > value > min:
                print(f"Test: {test_name}, Max: {max}, Valor: {value}, Min: {min}, Resultado_test: {result}, Resultado_control: ok")
    elif "ETAPA 13" in test_name:
        result = test.get("CommandInfo", {}).get("Data", {}).get("Result", "Sin resultado")
        print(f"Test: {test_name}, Valor: {value}, Resultado: {result}")
    elif "ETAPA 14" in test_name:
        result = test.get("CommandInfo", {}).get("Data", {}).get("Result", "Sin resultado")
        print(f"Test: {test_name}, Valor: {value}, Resultado: {result}")
    elif "ETAPA 15" in test_name:
        result = test.get("CommandInfo", {}).get("Data", {}).get("Result", "Sin resultado")
        print(f"Test: {test_name}, Max: {max}, Valor: {value}, Min: {min}, Resultado: {result}")
print (f'Estado de test nº --> {test}')



# Recorremos cada test para start_FW
print(f'START_FW TEST')
print(f'\n')
for test in start_fw:
    test_name = test.get("CommandInfo", {}).get("TEST", "Sin nombre")
    result = test.get("CommandInfo", {}).get("Data", {}).get("Result", "Sin resultado")
    value = test.get("CommandInfo", {}).get("Data", {}).get("Data_Value", "Sin valor")
    max = test.get("CommandInfo", {}).get("Data", {}).get("Data_Max")
    min = test.get("CommandInfo", {}).get("Data", {}).get("Data_Min")
    value_x = test.get("CommandInfo", {}).get("Data", {}).get("Data_Value X")
    value_y = test.get("CommandInfo", {}).get("Data", {}).get("Data_Value Y")
    value_z = test.get("CommandInfo", {}).get("Data", {}).get("Data_Value Z")
    if "ETAPA 18" in test_name:
        print(f"Test: {test_name}, Valor: {value}, Resultado: {result}")
    elif "ETAPA 19" in test_name:
       print(f"Test: {test_name}, Valor: {value}, Resultado: {result}")
    elif "ETAPA 22" in test_name:
        print(f"Test: {test_name}, Valor: {value}, Resultado: {result}")
    

        
        if "OK" in value:
            print(f"Test: {test_name}, Max: {max}, Valor: {value}, Min: {min}, Resultado_test: {result}, Resultado_control: ok")

            
# Recorremos cada test para calibrator_check_limits
for test in start_fw:
    test_name = test.get("CommandInfo", {}).get("TEST", "Sin nombre")
    result = test.get("CommandInfo", {}).get("Data", {}).get("Result", "Sin resultado")
    value = test.get("CommandInfo", {}).get("Data", {}).get("Data_Value", "Sin valor")
    max = test.get("CommandInfo", {}).get("Data", {}).get("Data_Max")
    min = test.get("CommandInfo", {}).get("Data", {}).get("Data_Min")
    value_x = test.get("CommandInfo", {}).get("Data", {}).get("Data_Value X")
    value_y = test.get("CommandInfo", {}).get("Data", {}).get("Data_Value Y")
    value_z = test.get("CommandInfo", {}).get("Data", {}).get("Data_Value Z")
    if "ETAPA xx" in test_name:
        print(f"Test: {test_name}, Valor: {value}, Resultado: {result}")
    elif "ETAPA xx" in test_name:
       print(f"Test: {test_name}, Valor: {value}, Resultado: {result}")
    elif "ETAPA xx" in test_name:
        print(f"Test: {test_name}, Valor: {value}, Resultado: {result}")
    
    else:
        #maximo = max.replace(".",",")
        #valor = value.replace(".",",")
        #minimo = min.replace(".",",")
        if "-" in max:
            max = max.replace ("-","100000")
        if "-" in min:
            min = min.replace ("-","0")
        
        if "OK" in value:
            print(f"Test: {test_name}, Max: {max}, Valor: {value}, Min: {min}, Resultado_test: {result}, Resultado_control: ok")
        else:
            maximo = to_float(max)
            valor = to_float(value)
            minimo = to_float(min)
        #ok = f'{Fore.GREEN}{"ok"}{Style.RESET_ALL}'
            if maximo > valor > minimo :
                print(f"Test: {test_name}, Max: {maximo}, Valor: {valor}, Min: {minimo}, Resultado_test: {result}, Resultado_control: ok")


