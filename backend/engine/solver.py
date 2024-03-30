from amplpy import AMPL
import pandas as pd

def prepare_data(N):
    workers = [f"W{i:02d}" for i in range(1, N + 1)] # getWorkerss()
    days = [1, 2, 3, 4, 5, 6, 7] # getDays()
    shifts = [(i + 1) for i in range(21)]
    nights = [(i + 1) for i in range(6)]
    applications = [[1] * 21 for _ in range(15)] # getApplications()
    min_workers = [1] * 21
    return workers, days, applications, shifts, nights, min_workers

def model(N: int):

    model = AMPL()
    model.read("crew-optimizer/backend/engine/model/model.mod")

    workers, days, applications, shifts, nights, min_workers = prepare_data(N)

    model.set["WORKERS"] = workers
    model.set["DAYS"] = days
    model.set["SHIFTS"] = shifts
    model.set["NIGHTS"] = nights
    model.param["min_workers"] = min_workers
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

model(15)
