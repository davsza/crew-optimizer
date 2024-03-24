set WORKERS;  # Set of workers
set DAYS ordered;     # Set of days

param min_workers{DAYS};	# Minimum required workers for each day
param application{WORKERS, DAYS};	# Application for the workers

var x{WORKERS, DAYS} binary;	# Binary variable indicating worker assignment

maximize Total_Match:
	sum {i in WORKERS, j in DAYS} x[i, j] * application[i, j];
	
# Constraint: each worker must work exactly 5 days
subject to Work_Constraint {i in WORKERS}:
    sum {j in DAYS} x[i,j] = 5;

# Constraint: minimum required workers constraint
subject to Min_Workers_Constraint {j in DAYS}:
    sum {i in WORKERS} x[i,j] >= min_workers[j];