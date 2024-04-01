SET_WORKERS = "set WORKERS ordered;	# Set of workers"
SET_SHIFTS = "set SHIFTS ordered;	# Set of shifts"
SET_DAYS = "set DAYS ordered;	# Set of days"
SET_NIGHTS = "set NIGHTS ordered;	# Set of nights"

PARAM_MIN_WORKERS = "param min_workers{SHIFTS}; #   Minimum required workers for each day"
PARAM_DAYS_TO_WORK = "param days_to_work_per_week; #    Minimum days to work for each worker"
PARAM_APPLICATIONS = "param application{WORKERS, SHIFTS}; # Application for the workers"

VARIABLE_X = "var x{WORKERS, SHIFTS} binary; #   Binary variable indicating worker assignment"

OBJECTIVE_TOTAL_MATCH = "maximize Total_Match: sum {i in WORKERS, j in SHIFTS} x[i, j] * application[i, j];"
CONSTRAINT_DAYS_TO_WORK = "subject to Work_Constraint {i in WORKERS}: sum {j in SHIFTS} x[i,j] = days_to_work_per_week; #   Constraint: each worker must work exactly 5 days"
CONSTRAINT_MAX_ONE_SHIFT_PER_DAY = "subject to Max_One_Shift_Per_Day {i in WORKERS, j in DAYS}: sum {k in 1..3} x[i, (j - 1) * 3 + k] <= 1; #   Constraint: each day a worker can work exactly 0 or 1 shift each day"
CONSTRAINT_NIGHT_SHIFTS = "subject to Night_Shifts {i in WORKERS, j in NIGHTS}: sum {k in 0..2} x[i, 3 + (j - 1) * 3 + k] <= 1; #   Constraint: after the night shifts, the workers can't have any morning or afternoon shift"
CONSTRAINT_MIN_WORKERS_PER_SHIFT = "subject to Min_Workers_Constraint {j in SHIFTS}: sum {i in WORKERS} x[i,j] >= min_workers[j]; # Constraint: minimum required workers constraint"