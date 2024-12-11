# import matplotlib.pyplot as plt
# from matplotlib.animation import FuncAnimation
# import spidev
# import numpy as np
# from time import time

# # SPI 인터페이스 설정
# spi = spidev.SpiDev()
# spi.open(0, 0)  # SPI 버스 0, 장치 0
# spi.max_speed_hz = 1350000

# def read_adc(channel):
#     """MCP3008 ADC에서 값을 읽는 함수"""
#     if channel < 0 or channel > 7:
#         raise ValueError("Channel must be between 0 and 7")
#     r = spi.xfer2([1, (8 + channel) << 4, 0])
#     adc_value = ((r[1] & 3) << 8) + r[2]
#     return adc_value

# # 데이터 초기화
# x_data, y_data = [], []
# start_time = time()

# fig, ax = plt.subplots()
# line, = ax.plot([], [], lw=2)

# def update(frame):
#     """실시간으로 그래프를 업데이트하는 함수"""
#     current_time = time()
#     elapsed_time = current_time - start_time

#     # 센서 데이터 읽기
#     adc_value = read_adc(0)  # CH0에서 읽기

#     x_data.append(elapsed_time)
#     y_data.append(adc_value)

#     # 최근 100개의 데이터만 표시
#     if len(x_data) > 100:
#         x_data.pop(0)
#         y_data.pop(0)

#     # 그래프 데이터 업데이트
#     line.set_data(x_data, y_data)
#     ax.relim()
#     ax.autoscale_view()
#     ax.set_xlabel("Time (s)")
#     ax.set_ylabel("ADC Value")
#     ax.set_title("Real-time Vibration Sensor Data")

#     return line,

# # 애니메이션 설정
# ani = FuncAnimation(fig, update, blit=True, interval=100)
# plt.show()




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

# 데이터 초기화
x_data, y_data = [], []
start_time = time()

# 오프셋을 초기화합니다. (예: 초기 100개의 데이터 평균을 오프셋으로 사용)
initial_readings = [read_adc(0) for _ in range(100)]
offset = np.mean(initial_readings)

fig, ax = plt.subplots()
line, = ax.plot([], [], lw=2)

def update(frame):
    """실시간으로 그래프를 업데이트하는 함수"""
    current_time = time()
    elapsed_time = current_time - start_time

    # 센서 데이터 읽기
    adc_value = read_adc(0)  # CH0에서 읽기
    corrected_value = adc_value - offset  # 오프셋을 제거한 값

    x_data.append(elapsed_time)
    y_data.append(corrected_value)

    # 최근 100개의 데이터만 표시
    if len(x_data) > 100:
        x_data.pop(0)
        y_data.pop(0)

    # 그래프 데이터 업데이트
    line.set_data(x_data, y_data)
    ax.relim()
    ax.autoscale_view()
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("ADC Value")
    ax.set_title("Real-time Vibration Sensor Data (Offset Corrected)")

    return line,

# 애니메이션 설정
ani = FuncAnimation(fig, update, blit=True, interval=100)
plt.show()
