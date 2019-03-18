# In[1]
# Imports and Stuff
import z3
import csv
import sys
import pprint
from collections import defaultdict
from collections import namedtuple
pp = pprint.PrettyPrinter(indent=4)
dep = namedtuple('Dependency', 'me dependsOn')
systemFile = 'RunFile.smt2'
resultsFile = 'Results'

# In[2]
# Create our deps list
deps = []
with open(sys.argv[1]) as myFile:
    myFile.readline()
    r = csv.reader(myFile)
    for line in r:
        a = line[0]
        for thingThatDependsOnA in line[1].split(','):
            deps.append(dep(me=thingThatDependsOnA,dependsOn=a))
deps

# In[3]
# Create the system
y = {}
s = z3.Solver()
for me,dep in deps:
    if me not in y: y[me] = z3.Int(me)
    if dep not in y: y[dep] = z3.Int(dep)
    me = y[me]
    dep = y[dep]
    
    s.add(dep<me)

for k in y:
    s.add(y[k]>0)

with open(systemFile, 'w') as myFile:
    myFile.write(s.to_smt2())
    pp.pprint('SMT System saved as {}'.format(systemFile))

# In[4]
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

