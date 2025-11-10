import RPi.GPIO as GPIO
import time

# Pines de conexión
DIR = 20     # Dirección
STEP = 21    # Paso
EN = 16      # Enable
CW = 1       # Sentido horario
CCW = 0      # Sentido antihorario
SPR = 200    # Pasos por revolución (puede cambiar según microstepping)

# Configuración de GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(DIR, GPIO.OUT)
GPIO.setup(STEP, GPIO.OUT)
GPIO.setup(EN, GPIO.OUT)

# Activar el driver
GPIO.output(EN, GPIO.LOW)

def mover_motor(sentido, pasos, velocidad_ms):
    GPIO.output(DIR, sentido)
    for _ in range(pasos):
        GPIO.output(STEP, GPIO.HIGH)
        time.sleep(velocidad_ms / 1000.0)
        GPIO.output(STEP, GPIO.LOW)
        time.sleep(velocidad_ms / 1000.0)

try:
    print("Moviendo en sentido horario")
    mover_motor(CW, 100, 2)  # 100 pasos, 2ms entre pasos

    print("Pausa")
    time.sleep(2)

    print("Moviendo en sentido antihorario")
    mover_motor(CCW, 100, 2)

except KeyboardInterrupt:
    print("Interrumpido por el usuario")

finally:
    GPIO.output(EN, GPIO.HIGH)  # Desactiva el motor
    GPIO.cleanup()
