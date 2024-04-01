from amplpy import AMPL
import pandas as pd
import json
from model_config import model_constants, model_parameters as mp


def build_model(model_path: str, config_path: str):
    with open(config_path, 'r') as config_file:
        config = config_file.read()
    data = json.loads(config)

    with open(model_path, 'w') as model_file:
        for _, items in data.items():
            for item, enabled in items.items():
                if enabled:
                    model_file.write(getattr(model_constants, item) + "\n")


def prepare_data(number_of_shifts: int, number_of_workers: int):
    workers = mp.get_workers(number_of_workers=number_of_workers)
    days = mp.get_days()
    shifts = mp.get_shifts(number_of_shifts=number_of_shifts)
    nights = mp.get_nights()
    applications = mp.get_applications(number_of_shifts=number_of_shifts, number_of_workers=number_of_workers)
    min_workers = mp.get_min_workers(number_of_shifts=number_of_shifts)
    days_to_work_per_week = mp.get_days_to_work_per_week()
    return workers, days, applications, shifts, nights, min_workers, days_to_work_per_week


def model(number_of_shifts: int, number_of_workers: int, model_path: str):
    model = AMPL()
    model.read(model_path)

    workers, days, applications, shifts, nights, min_workers, days_to_work_per_week = prepare_data(
        number_of_shifts=number_of_shifts, number_of_workers=number_of_workers)

    model.set["WORKERS"] = workers
    model.set["DAYS"] = days
    model.set["SHIFTS"] = shifts
    model.set["NIGHTS"] = nights
    model.param["min_workers"] = min_workers
    model.param["days_to_work_per_week"] = days_to_work_per_week
    model.param["application"] = pd.DataFrame(applications, index=workers, columns=shifts)
    model.setOption('solver', ".\SCIPOptSuite\\bin\\scip.exe")
    model.solve()

    shift_matrix = model.getVariable("x")
    data_dict = shift_matrix.getValues().toDict()
    result = []
    worker_ids = set(key[0] for key in data_dict)
    for worker_id in sorted(worker_ids):
        data = [data_dict.get((worker_id, i), 0) for i in range(1, 22)]
        result.append(data)
    print(result)


def main():
    model_path = "crew-optimizer/backend/engine/model/model.mod"
    config_path = "crew-optimizer/backend/engine/model_config/model_config.json"
    number_of_shifts = 21
    number_of_workers = 15
    build_model(model_path=model_path, config_path=config_path)
    model(number_of_shifts=number_of_shifts, number_of_workers=number_of_workers, model_path=model_path)


if __name__ == "__main__":
    main()
