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
        keys = list(data.keys())

        for i, key in enumerate(keys):
            line = f'  "{key}": {data[key]}'
            if i < len(keys) - 1:
                line += ','
            lines.append(line)

        lines.append('}')
        return '\n'.join(lines)


class OutputHandler:
    @staticmethod
    def display(data):
        formatted = JsonFormatter.format(data)
        print(formatted)


class MissionComputer:
    def __init__(self, sensor):
        self.sensor = sensor
        self.env_values = self._init_env_values()

        self.history = []
        self.max_history = 60  # 5초 * 60 = 5분

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
        self.env_values.update(sensor_data)

    def calculate_average(self):
        avg = {}

        for key in self.env_values:
            total = 0
            for data in self.history:
                total += data[key]
            avg[key] = round(total / len(self.history), 3)

        return avg

    def run(self):
        while True:
            self.update_env()

            # 현재 상태 출력
            OutputHandler.display(self.env_values)

            # 데이터 저장
            self.history.append(self.env_values.copy())

            # 5분 평균 출력
            if len(self.history) == self.max_history:
                print("\n[5분 평균 값]")
                avg = self.calculate_average()
                OutputHandler.display(avg)
                self.history.clear()

            # 사용자 입력 (종료 여부 확인)
            user_input = input("종료하려면 q 입력, 계속하려면 Enter: ")

            if user_input.lower() == 'q':
                print("System stopped...")
                breakq
                

            time.sleep(5)


if __name__ == '__main__':
    ds = DummySensor()
    mission_computer = MissionComputer(ds)
    mission_computer.run()