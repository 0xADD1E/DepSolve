# In[]
# Imports and Stuff
import z3
import csv
import sys
import pprint
import numpy as np
from collections import defaultdict
from collections import namedtuple
pp = pprint.PrettyPrinter(indent=4)
Dependency = namedtuple('Dependency', 'me dependsOn')
systemFile = 'RunFile.smt2'
resultsFile = 'Results'

# In[]
# Create our deps list
deps = []
y = {}
with open(sys.argv[1]) as myFile:
    myFile.readline()
    r = csv.reader(myFile)
    for line in r:
        a = line[0]
        for b in line[1].split(','):
            me = b
            dep = a
            deps.append(Dependency(me,dep))
            if me not in y: y[me] = z3.Int(me)
            if dep not in y: y[dep] = z3.Int(dep)
deps

# In[]
# Construct Transitive Closure... This... Could get hairy

#setup
symbols_list = list(y)
n_symbols = len(symbols_list)
symbols_indexes = {s:i for i,s in enumerate(symbols_list)}
transitive = np.full((n_symbols,n_symbols), False)
#fill
for me,dep in deps:
    i,j = symbols_indexes[me],symbols_indexes[dep]
    transitive[i][j] = True
#transitive
for i in range(n_symbols):
    for j in range(n_symbols):
        for k in range(n_symbols):
            transitive[i][j] |= transitive[i][k] and transitive[k][j]
pp.pprint(symbols_indexes)
pp.pprint(transitive)

# In[]
# Create the system
s = z3.Solver()
for me,dep in deps:    
    if transitive[symbols_indexes[dep]][symbols_indexes[me]]:
        s.add(y[dep]<=y[me])
    else:
        s.add(y[dep]<y[me])

for k in y:
    s.add(y[k]>0)

with open(systemFile, 'w') as myFile:
    myFile.write(s.to_smt2())
    pp.pprint('SMT System saved as {}'.format(systemFile))

# In[]
# Run the solver
if str(s.check()) == 'sat':
    m = s.model()
    result = {}
    for a in y:
        stage = str(m.eval(y[a]))
        if stage not in result: result[stage] = []
        result[stage].append(a)
else:
    result = 'unsat'

with open(resultsFile, 'w') as myFile:
        myFile.write(str(result))
        pp.pprint('Results saved as {}'.format(resultsFile))
pp.pprint(result)

