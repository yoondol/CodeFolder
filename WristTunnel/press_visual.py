import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
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

# 시뮬레이션 설정
duration = 15  # 데이터 수집 시간 (초)
interval = 100  # 데이터 수집 간격 (ms)
num_frames = int(duration * 1000 / interval)  # 총 프레임 수

# 데이터 초기화
x_data, y_data = [], []
start_time = time()

fig, ax = plt.subplots()
line, = ax.plot([], [], lw=2)

def update(frame):
    """실시간으로 그래프를 업데이트하는 함수"""
    current_time = time()
    elapsed_time = current_time - start_time

    if elapsed_time > duration:
        ani.event_source.stop()
        print("15 seconds of data collected.")
        return line,

    # 센서 데이터 읽기
    adc_value = read_adc(0)  # CH0에서 읽기
    x_data.append(elapsed_time)
    y_data.append(adc_value)

    # 최근 100개의 데이터만 표시
    if len(x_data) > 100:
        x_data.pop(0)
        y_data.pop(0)

    # 데이터 강도에 따라 색상 변경 (강도가 클수록 빨간색이 진해짐)
    color_intensity = adc_value / 1023  # 0.0 ~ 1.0 사이로 변환
    color = (1, 0, 0, color_intensity)  # (R, G, B, alpha) 튜플

    # 그래프 데이터 업데이트
    line.set_data(x_data, y_data)
    line.set_color(color)  # 그래프의 색상 설정

    ax.relim()
    ax.autoscale_view()
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("ADC Value")
    ax.set_title("Real-time Vibration Sensor Data")

    return line,

# 애니메이션 설정
ani = FuncAnimation(fig, update, frames=num_frames, blit=True, interval=interval)
plt.show()
