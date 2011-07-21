'''
Parameters used by:

 - bin/cludetform.py
 - bin/p/cludet.py
 - util/determinants1
 - util/determinants1af
 - util/determinants2
 - util/determinants2af

'''

# Interpolation parameter
Sep = 3

# Parameter for F-beta score
FastBeta = 1.5
SlowBeta = FastBeta

FastBeta2 = FastBeta * FastBeta
SlowBeta2 = SlowBeta * SlowBeta

# Parameter for limit in cumulative score
# Additional patterns are only added if the new score becomes at least Limit times the old Importance
Limit = 1.01
