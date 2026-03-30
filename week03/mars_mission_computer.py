import random
import time
import os


class DummySensor:
    def __init__(self):
        self.env_values = {
            'mars_base_internal_temperature': 0.0,
            'mars_base_external_temperature': 0.0,
            'mars_base_internal_humidity': 0.0,
            'mars_base_external_illuminance': 0.0,
            'mars_base_internal_co2': 0.0,
            'mars_base_internal_oxygen': 0.0
        }

    def set_env(self):
        self.env_values['mars_base_internal_temperature'] = round(random.uniform(18, 30), 2)
        self.env_values['mars_base_external_temperature'] = round(random.uniform(0, 21), 2)
        self.env_values['mars_base_internal_humidity'] = round(random.uniform(50, 60), 2)
        self.env_values['mars_base_external_illuminance'] = round(random.uniform(500, 715), 2)
        self.env_values['mars_base_internal_co2'] = round(random.uniform(0.02, 0.1), 4)
        self.env_values['mars_base_internal_oxygen'] = round(random.uniform(4, 7), 2)

    def get_env(self):
        current_time = time.strftime('%Y-%m-%d %H:%M:%S')

        log_line = (
            current_time +
            ' | 화성 기지 내부 온도: ' + str(self.env_values['mars_base_internal_temperature']) +
            ' | 화성 기지 외부 온도: ' + str(self.env_values['mars_base_external_temperature']) +
            ' | 화성 기지 내부 습도: ' + str(self.env_values['mars_base_internal_humidity']) +
            ' | 화성 기지 외부 광량: ' + str(self.env_values['mars_base_external_illuminance']) +
            ' | 화성 기지 내부 이산화탄소 농도: ' + str(self.env_values['mars_base_internal_co2']) +
            ' | 화성 기지 내부 산소 농도: ' + str(self.env_values['mars_base_internal_oxygen'])
        )

        file_path = os.path.join(os.path.dirname(__file__), 'mars_log.txt')

        with open(file_path, 'a', encoding='utf-8') as f:
            f.write(log_line + '\n')

        return self.env_values


ds = DummySensor()

ds.set_env()
env = ds.get_env()

print(env)