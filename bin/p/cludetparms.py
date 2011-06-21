'''
Parameters used by:

 - bin/cludetform.py
 - bin/p/cludet.py
 - util/determinants1
 - util/determinants2

'''

# Interpolation parameter
Sep = 3

# Parameter for F-beta score
FastBeta = 1.4
SlowBeta = FastBeta

FastBeta2 = FastBeta * FastBeta
SlowBeta2 = SlowBeta * SlowBeta

# Parameter for limit in cumulative F-beta score, must be 1 or greater
# Additional patterns are only added if the new F score becomes at least Limit times the old F score
Limit = 1.02
