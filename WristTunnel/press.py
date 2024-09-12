import spidev
import numpy as np
import time

# SPI 인터페이스 설정
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1350000

def read_adc(channel):
    """MCP3008 ADC에서 값을 읽는 함수"""
    if channel < 0 or channel > 7:
        raise ValueError("Channel must be between 0 and 7")
    r = spi.xfer2([1, (8 + channel) << 4, 0])
    adc_value = ((r[1] & 3) << 8) + r[2]
    return adc_value

def collect_data(file_index, duration=60, interval=0.1, pressure_duration=30):
    """압력 상태를 시뮬레이션하여 데이터 수집"""
    start_time = time.time()
    pressure_data = []
    no_pressure_data = []
    
    print(f"Data collection {file_index} started...")

    while time.time() - start_time < duration:
        adc_value = read_adc(0)
        current_time = time.time() - start_time

        # 압력 상태와 비압력 상태를 시간으로 구분
        if current_time < pressure_duration:
            pressure_data.append(adc_value)
            status = "Pressure"
        else:
            no_pressure_data.append(adc_value)
            status = "No Pressure"
        
        # 실시간 데이터 출력
        print(f"Time: {current_time:.2f}s | ADC Value: {adc_value} | Status: {status}")

        time.sleep(interval)

    # 데이터 저장
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    np.save(f'data_pressure_{file_index}_{timestamp}.npy', np.array(pressure_data))
    np.save(f'data_no_pressure_{file_index}_{timestamp}.npy', np.array(no_pressure_data))

    print(f"Data collection {file_index} completed.")

# 데이터 수집
num_collections = 5  # 데이터 수집 횟수
for i in range(num_collections):
    collect_data(file_index=i, duration=60, interval=0.1, pressure_duration=30)
