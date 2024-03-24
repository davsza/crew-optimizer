from amplpy import AMPL
import pandas as pd
import numpy as np
import os

def prepare_data(N):
    workers = [f"W{i:02d}" for i in range(1, N + 1)]
    days = ["MON", "THU", "WED", "THR", "FRI", "SAT", "SUN"]
    applications = [
        [0, 0, 1, 1, 1, 1, 1],
        [0, 0, 1, 1, 1, 1, 1],
        [0, 0, 1, 1, 1, 1, 1],
        [0, 0, 1, 1, 1, 1, 1],
        [0, 0, 1, 1, 1, 1, 1]
    ]
    return workers, days, applications

def shift_schedule(N: int):

    model = AMPL()
    model.read("crew-optimizer/backend/engine/model/model.mod")

    workers, days, applications = prepare_data(5)
    # print(workers_dict)
    # print(days_dict)
    # print(applications)

    model.set["WORKERS"] = workers
    model.set["DAYS"] = days
    model.param["min_workers"] = [4, 4, 4, 4, 4, 2, 2]
    model.param["application"] = pd.DataFrame(applications, index=workers, columns=days)
    model.option["solver"] = "gurobi"
    model.solve()

shift_schedule(5)
