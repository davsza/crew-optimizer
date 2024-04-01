DAYS_TO_WORK_PER_WEEK = 5

def get_workers(number_of_workers: int):
    # dummy data, will be changed to db access
    return [f"W{i:02d}" for i in range(1, number_of_workers + 1)]

def get_days():
    return [(i + 1) for i in range(7)]


def get_shifts(number_of_shifts: int):
    return [(i + 1) for i in range(number_of_shifts)]


def get_nights():
    return [(i + 1) for i in range(6)]


def get_applications(number_of_shifts: int, number_of_workers: int):
    # dummy data, will be changed to db access
    return [[1] * number_of_shifts for _ in range(number_of_workers)]


def get_min_workers(number_of_shifts: int):
    return [1] * number_of_shifts


def get_days_to_work_per_week():
    return DAYS_TO_WORK_PER_WEEK