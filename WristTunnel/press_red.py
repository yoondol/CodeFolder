import tkinter as tk
import spidev
import numpy as np
from time import time

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

# Tkinter 설정
root = tk.Tk()
root.title("Vibration Intensity Display")

canvas = tk.Canvas(root, width=400, height=300)
canvas.pack()

# 시뮬레이션 설정
duration = 15  # 데이터 수집 시간 (초)
start_time = time()

def update_color():
    """센서 데이터에 따라 색상을 업데이트하는 함수"""
    current_time = time()
    elapsed_time = current_time - start_time

    if elapsed_time > duration:
        root.after_cancel(update_color)
        print("15 seconds of data collected.")
        return

    # 센서 데이터 읽기
    adc_value = read_adc(0)  # CH0에서 읽기

    # 데이터 강도에 따라 색상 변경 (강도가 클수록 빨간색이 진해짐)
    color_intensity = adc_value / 1023  # 0.0 ~ 1.0 사이로 변환
    red = int(255 * color_intensity)
    color = f'#{red:02x}0000'  # 빨간색 강도에 따른 색상

    # 배경 색상 업데이트
    canvas.config(bg=color)

    # 100ms 후에 색상 업데이트 함수 호출
    root.after(100, update_color)

update_color()  # 색상 업데이트 함수 호출
root.mainloop()  # Tkinter 이벤트 루프 시작
