# generator/meta.py

from config import LINES

################################
# ENV 센서 (39)
################################
def build_env_sources(tenant_id):
    sources = []

    # 창고 환경 (3)
    for i in range(1, 4):
        sources.append({
            "tenant_id": tenant_id,
            "line_id": "WH",
            "process": "ENV",
            "device_type": "ENV_SENSOR",
            "device_name": f"WAREHOUSE_ENV_{i}",
            "metrics": ["TEMP", "HUMIDITY"]
        })

    # 라인별 환경 센서 (9 × 4)
    for line in LINES:
        for i in range(1, 10):
            sources.append({
                "tenant_id": tenant_id,
                "line_id": line,
                "process": "ENV",
                "device_type": "ENV_SENSOR",
                "device_name": f"{line}_ENV_{i}",
                "metrics": ["TEMP", "HUMIDITY"]
            })

    return sources

################################
# SCALE 장비 (12)
################################
def build_scale_sources(tenant_id):
    sources = []

    scale_defs = [
        ("DOUGH_SCALE", "WEIGHT"),
        ("UNIT_SCALE", "WEIGHT"),
        ("PACK_SCALE", "WEIGHT"),
    ]

    for line in LINES:
        for device_type, metric in scale_defs:
            sources.append({
                "tenant_id": tenant_id,
                "line_id": line,
                "process": "QC",
                "device_type": device_type,
                "device_name": f"{line}_{device_type}",
                "metric": metric
            })

    return sources

################################
# MACHINE 장비
################################
MACHINE_DEFS = [
    ("FRY",  "FRYER_OIL",      "OIL_TEMP"),
    ("FRY",  "FRYER_STATE",    "OVERHEAT"),
    ("FRY",  "FRYER_OIL",      "ACID_VALUE"),
    ("COAT", "COATER",         "TEMP"),
    ("COAT", "COATER_BRIX",    "BRIX"),
    ("COOL", "COOLER",         "TEMP"),
    ("COOL", "COOLER_CLOCK",   "COOL_TIME"),
    ("COOL", "COOLER_FAN",     "FAN_SPEED"),
    ("DRY",  "DRYER",          "HUMIDITY"),
    ("ALL",  "CONVEYOR",       "CONVEYOR_SPEED"),
    ("ALL",  "CONVEYOR_JAM",   "JAM_STATE"),
    ("QC",   "METAL_DETECTOR", "METAL_DETECTED"),
]

def build_machine_sources(tenant_id):
    sources = []

    for line in LINES:
        for process, device_type, metric in MACHINE_DEFS:
            sources.append({
                "tenant_id": tenant_id,
                "line_id": line,
                "process": process,
                "device_type": device_type,
                "device_name": f"{line}_{device_type}",
                "metric": metric
            })

    return sources

################################
# POWER 장비 (1)
################################
def build_power_source(tenant_id):
    return [{
        "tenant_id": tenant_id,
        "line_id": "ALL",
        "process": "PWR",
        "device_type": "POWER_METER",
        "device_name": "FACTORY_POWER",
        "metric": "ENERGY_TOTAL"
    }]

################################
# ALL Sources (100)
################################
def build_all_sources(tenant_id):
    sources = []
    sources += build_env_sources(tenant_id)
    sources += build_scale_sources(tenant_id)
    sources += build_machine_sources(tenant_id)
    sources += build_power_source(tenant_id)
    return sources


if __name__ == "__main__":
    all_sources = build_all_sources("F01")
    print(f"Total sources: {len(all_sources)}")
    assert len(all_sources) == 100
