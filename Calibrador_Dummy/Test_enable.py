import RPi.GPIO as GPIO
import time
import math

# Pines (ajusta según tu conexión)
PUL = 21    # PUL+ (STEP)
DIR = 20    # DIR+
ENA = 16    # ENA+ (si lo usas)
# Si tu TB6600 usa las entradas invertidas (PUL-, DIR-, ENA-) y tienes que usar +5V,
# conecta PUL- a GND y PUL+ al GPIO (o usa transistores/opto). Revisa tu placa.

GPIO.setmode(GPIO.BCM)
GPIO.setup(PUL, GPIO.OUT)
GPIO.setup(DIR, GPIO.OUT)
GPIO.setup(ENA, GPIO.OUT)

# Parámetros físicos
STEPS_PER_REV = 3200  # 200 full steps * 16 microsteps

# Habilitar driver (comprobar si ENA es activo LOW o HIGH en tu módulo)
GPIO.output(ENA, GPIO.HIGH)  # normalmente LOW = ENABLE (varía por placa)

def rpm_to_delay(rpm):
    # devuelve delay por semi-fase en segundos (d), tal que se obtiene rpm
    steps_per_sec = rpm * STEPS_PER_REV / 60.0
    if steps_per_sec == 0:
        return None
    period = 1.0 / steps_per_sec    # periodo por paso (HIGH+LOW)
    d = period / 2.0
    return d

def pasos_para_angulo(angle_deg):
    return int(round(angle_deg / 360.0 * STEPS_PER_REV))

def mover_pasos(pasos, sentido=True, delay_sec=0.001, accel_steps=200):
    """
    Mueve 'pasos' pasos. sentido=True -> HIGH (ejemplo: CW), False -> CCW.
    delay_sec: retardo base por semi-fase.
    accel_steps: número de pasos para aceleración y desaceleración (simple)
    """
    GPIO.output(DIR, GPIO.HIGH if sentido else GPIO.LOW)

    def pulse(d):
        GPIO.output(PUL, GPIO.HIGH)
        time.sleep(d)
        GPIO.output(PUL, GPIO.LOW)
        time.sleep(d)

    # Simple rampa lineal
    for i in range(abs(pasos)):
        # factor rampa en [0,1]
        if accel_steps > 0:
            if i < accel_steps:
                factor = (i+1) / accel_steps  # rampa inicio
            elif i > (abs(pasos) - accel_steps):
                factor = (abs(pasos) - i) / accel_steps  # rampa final
            else:
                factor = 1.0
            # limitar factor
            if factor < 0.1: factor = 0.1
            d = delay_sec / factor
        else:
            d = delay_sec
        pulse(d)

def mover_angulo(angle_deg, rpm=6.0):
    pasos = pasos_para_angulo(abs(angle_deg))
    d = rpm_to_delay(rpm)
    if d is None:
        return
    sentido = angle_deg >= 0  # positivo = sentido True
    mover_pasos(pasos, sentido=sentido, delay_sec=d, accel_steps= min(200, pasos//4))

try:
    # Ejemplos:
    print("Habilitando driver")
    GPIO.output(ENA, GPIO.HIGH)
    print("tensión en Enable durante 10s")
    time.sleep(10)

    # Mover 90 grados a 6 RPM
    #mover_angulo(90, rpm=6.0)
    #time.sleep(1)

    # Girar 4 paradas intermedias: 360/4 = 90 grados cada parada
    #for i in range(4):
    #    mover_angulo(90, rpm=6.0)
    #    print("Parada intermedia", i+1)
    #    time.sleep(2)

except KeyboardInterrupt:
    print("Interrumpido")

finally:
    # Desactivar motor (ajusta según comportamiento de tu placa)
    GPIO.output(ENA, GPIO.LOW)
    GPIO.cleanup()