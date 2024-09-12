# from gpiozero import Button
# from time import sleep

# sensor = Button(2)  
# while True:
#     if sensor.is_pressed:
#         print("Pressure! !")
#     else:
#         print("None.")
#     sleep(0.1) 


# from gpiozero import MCP3008
# import time

# pot = MCP3008(0)
# while True:
#     time.sleep(0.1)
#     print(pot.value)

import spidev
from time import sleep

# SPI 인터페이스 설정
spi = spidev.SpiDev()
spi.open(0, 0)  # SPI 버스 0, 장치 0
spi.max_speed_hz = 1350000

def read_adc(channel):
    """MCP3008 ADC에서 값을 읽는 함수"""
    if channel < 0 or channel > 7:
        raise ValueError("Channel must be between 0 and 7")
    r = spi.xfer2([1, (8 + channel) << 4, 0])
    adc_value = ((r[1] & 3) << 8) + r[2]
    return adc_value

while True:
    adc_value = read_adc(0)  # CH0에서 읽기
    print(f"ADC Value: {adc_value}")
    sleep(0.1)
