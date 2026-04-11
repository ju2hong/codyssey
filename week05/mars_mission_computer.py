import platform
import os
import json


class MissionComputer:

    def __init__(self):
        self.psutil = self._load_psutil()
        self.settings = self._load_settings()

    def _load_psutil(self):
        try:
            import psutil
            return psutil
        except Exception:
            return None

    def _load_settings(self):
        try:
            base_path = os.path.dirname(__file__)
            file_path = os.path.join(base_path, 'setting.txt')

            with open(file_path, 'r') as f:
                return [line.strip() for line in f if line.strip()]
        except Exception:
            return []

    def _safe_execute(self, func, default_value='cannot get info'):
        try:
            return func()
        except Exception:
            return default_value

    def _filter_data(self, data):
        if not self.settings:
            return data
        return {k: v for k, v in data.items() if k in self.settings}

    # =========================
    # 시스템 정보
    # =========================
    def get_mission_computer_info(self):
        info = {
            'os': self._safe_execute(platform.system),
            'os_version': self._safe_execute(platform.version),
            'cpu_type': self._safe_execute(platform.processor),
            'cpu_cores': self._safe_execute(os.cpu_count),
            'memory_total': self._get_memory_total()
        }

        info = self._filter_data(info)
        self._print_json(info)
        return info

    def _get_memory_total(self):
        if self.psutil:
            return self._safe_execute(
                lambda: self.psutil.virtual_memory().total
            )
        return 'psutil not available'

    # =========================
    # 시스템 부하
    # =========================
    def get_mission_computer_load(self):
        load = {
            'cpu_usage': self._get_cpu_usage(),
            'memory_usage': self._get_memory_usage()
        }

        load = self._filter_data(load)
        self._print_json(load)
        return load

    def _get_cpu_usage(self):
        if self.psutil:
            return self._safe_execute(
                lambda: self.psutil.cpu_percent(interval=1)
            )
        return 'psutil not available'

    def _get_memory_usage(self):
        if self.psutil:
            return self._safe_execute(
                lambda: self.psutil.virtual_memory().percent
            )
        return 'psutil not available'

    def _print_json(self, data):
        print(json.dumps(data, indent=4))


if __name__ == '__main__':
    runComputer = MissionComputer()

    print('=== Mission Computer Info ===')
    runComputer.get_mission_computer_info()

    print('\n=== Mission Computer Load ===')
    runComputer.get_mission_computer_load()