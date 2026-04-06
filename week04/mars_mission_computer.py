import time


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

    def read(self):
        self.env_values['mars_base_internal_temperature'] += 0.1
        self.env_values['mars_base_external_temperature'] += 0.2
        self.env_values['mars_base_internal_humidity'] += 0.05
        self.env_values['mars_base_external_illuminance'] += 1.0
        self.env_values['mars_base_internal_co2'] += 0.01
        self.env_values['mars_base_internal_oxygen'] += 0.02

        return self.env_values.copy()


class JsonFormatter:
    @staticmethod
    def format(data):
        lines = ['{']
        for key, value in data.items():
            lines.append(f"  '{key}': {value},")
        lines[-1] = lines[-1].rstrip(',')
        lines.append('}')
        return '\n'.join(lines)


class OutputHandler:
    @staticmethod
    def print(data):
        formatted = JsonFormatter.format(data)
        print(formatted)


class MissionComputer:
    def __init__(self, sensor):
        self.sensor = sensor
        self.env_values = self._init_env_values()

    def _init_env_values(self):
        return {
            'mars_base_internal_temperature': 0.0,
            'mars_base_external_temperature': 0.0,
            'mars_base_internal_humidity': 0.0,
            'mars_base_external_illuminance': 0.0,
            'mars_base_internal_co2': 0.0,
            'mars_base_internal_oxygen': 0.0
        }

    def update_env(self):
        sensor_data = self.sensor.read()
        for key in self.env_values:
            self.env_values[key] = sensor_data[key]

    def run(self):
        while True:
            self.update_env()
            OutputHandler.print(self.env_values)
            time.sleep(5)


if __name__ == '__main__':
    ds = DummySensor()
    RunComputer = MissionComputer(ds)
    RunComputer.run()