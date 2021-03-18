# Import libraries

import os
import math
import time
import itertools
import matplotlib.pyplot as plt
from gurobipy import *


# Set working directory to where the script file is

os.chdir(os.path.dirname(os.path.abspath(__file__)))


# Input type of instance according to line sapcing ("unif" or "rand")

line_spacing = "unif"


# Input model to be used ("tsp1" or "tsp2")

mip_model = "tsp1"


# Input v, h and r

v = 1 # number of vertical lines (1 through 30)
h = 1 # number of horizontal lines (1 through 20)
r = 1 # replication (1 through 5)


# Compute number of nodes

n = 1 + 2 * (h + v)


# Open file with instance information

filename = "instances/" + line_spacing + "/tpo_" + line_spacing + "_" + str(v) + "_" + str(h) + "_" + str(r) + ".txt"
f = open(filename, 'r')
l, a = f.readline().split()
coord_x = f.readline().split()
coord_y = f.readline().split()
f.close()
l = int(l)
a = int(a)
coord_x = [int(i) for i in coord_x] 
coord_y = [int(i) for i in coord_y] 


#Create list "points" with all nodes of the graph (each node is a tuple)

points = [(0,0)]          

for x in coord_x:
    points.append((x, 0))
    points.append((x, a))

for y in coord_y:
    points.append((0, y))
    points.append((l, y))            


# Create dictionay with distances between each pair of nodes

dist = {(i,j) :
    round(math.sqrt(sum((points[i][k]-points[j][k])**2 for k in range(2))), 4)
    for j in range(n) for i in range(j)}

    
# START OF GUROBI CODE

time_start = time.time()  #start timer

# Callback functions (use lazy constraints to eliminate subtours)

# Subtour elimination for TSP1
    
def subtour_elim_tsp1(model, where):
    if where == GRB.Callback.MIPSOL:
        # Make a list of edges selected in the solution
        vals = model.cbGetSolution(model._vars)
        selected = tuplelist((i,j) for i,j in model._vars.keys() if vals[i,j] > 0.5)
        # Find the shortest cycle in the selected edge list
        tour = subtour(selected)
        if len(tour) < n:
            # Add subtour elimination constraint for every pair of cities in tour
            model.cbLazy(quicksum(model._vars[i,j] for i,j in itertools.combinations(tour, 2)) <= len(tour)-1)


# Subtour elimination for TSP2

def diff(first, second):
    second = set(second)
    return [item for item in first if item not in second]
            
def subtour_elim_tsp2(model, where):
    if where == GRB.Callback.MIPSOL:
        # make a list of edges selected in the solution
        vals = model.cbGetSolution(model._vars)
        selected = tuplelist((i,j) for i,j in model._vars.keys() if vals[i,j] > 0.5)
        # find the shortest cycle in the selected edge list
        tour = subtour(selected)
        tourcomplement = diff(list(range(n)),tour)
        if len(tour) < n:
            # add isolated component elimination constraint for every pair of 
            # edges between the component and the rest of the graph
            model.cbLazy(quicksum(model._vars[i,j] for i in tour for j in tourcomplement) >= 2)


# Given a tuplelist of edges, find the shortest subtour

def subtour(edges):
    uvisited = list(range(n))
    cycle = range(n+1) # initial length has 1 more city
    while uvisited: # true if list is non-empty
        thiscycle = []
        neighbors = uvisited
        while neighbors:
            current = neighbors[0]
            thiscycle.append(current)
            uvisited.remove(current)
            neighbors = [j for i,j in edges.select(current,'*') if j in uvisited]
        if len(cycle) > len(thiscycle):
            cycle = thiscycle
    return cycle


# Create model

m = Model()


# Create variables

vars = m.addVars(dist.keys(), obj=dist, vtype=GRB.BINARY, name='e')


# Inform Gurobi that e[j,i] is equivalent to e[i,j]

for i,j in vars.keys():
    vars[j,i] = vars[i,j]


# Add degree-2 constraint

for i in range(n):
    m.addConstr(sum(vars[i,j] for j in range(n) if j != i) == 2)


# Add required edges constraints

for i in range(1,n):
    if i % 2 == 1:
        m.addConstr(vars[i,i+1] == 1)


# Set time limit to 600 seconds

timelimit = 600
m.setParam('TimeLimit', timelimit)


# Set absolute MIP gap to zero

m.setParam('MIPGapAbs', 0)


# Optimize model

m._vars = vars
m.Params.lazyConstraints = 1

if mip_model == "tsp1":
    subtour_elim = subtour_elim_tsp1
else:
    subtour_elim = subtour_elim_tsp2

m.optimize(subtour_elim)

vals = m.getAttr('x', vars)
selected = tuplelist((i,j) for i,j in vals.keys() if vals[i,j] > 0.5)
tour = subtour(selected)
assert len(tour) == n


# Collect solution information

dist_tsp = m.objVal
gap_tsp = m.MIPGap
time_tsp = round(min(time.time() - time_start, timelimit), 2)

# END OF GUROBI CODE


# Output best tour found to a txt file

tourname = "tpo_" + line_spacing + "_" + mip_model + "_" + str(v) + "_" + str(h) + "_" + str(r) + ".txt"
file1 = open(tourname, "w")
file1.write(str(tour) + "\n")
file1.write(str(dist_tsp/1000) + " m")
file1.write("\n")
file1.close()


# Display figure and output it to a png file

x = []
y = []          

for i in tour:
    x.append(points[i][0])
    y.append(points[i][1])

x.append(points[0][0])
y.append(points[0][1])

border_x = [0, l, l, 0, 0]
border_y = [0, 0, a, a, 0]

plt.clf()

plt.plot(border_x, border_y, c='gray', linestyle='-', marker='')
plt.plot(x, y, c='red', linestyle='-', linewidth=3, marker='.')
plt.xlim(-0.1*l,1.1*l)
plt.ylim(-0.1*a,1.1*a)
plt.xticks([])
plt.yticks([])
plt.title('v = ' + str(v) + ',  h = ' + str(h) + ',  r = ' + str(r))
plt.box(on=None)
plt.xlabel('Dist = %.2f m,   ' % (dist_tsp / 1000) + 'Gap = %.4f %%,   ' % (gap_tsp * 100) + 'Time = %.2f s' % time_tsp)

for i, txt in enumerate(list(range(n))):
    if i == 0:
        plt.annotate(txt, (points[i][0], points[i][1]), textcoords="offset points", xytext=(-10,-10), ha='center')
    elif i % 2 == 1 and i <= 2 * v:
        plt.annotate(txt, (points[i][0], points[i][1]), textcoords="offset points", xytext=(0,-10), ha='center')
    elif i % 2 == 0 and i <= 2 * v:
        plt.annotate(txt, (points[i][0], points[i][1]), textcoords="offset points", xytext=(0,5), ha='center')
    elif i % 2 == 1:
        plt.annotate(txt, (points[i][0], points[i][1]), textcoords="offset points", xytext=(-10,0), ha='center')
    else:
        plt.annotate(txt, (points[i][0], points[i][1]), textcoords="offset points", xytext=(10,0), ha='center')
        
figname = "tpo_" + line_spacing + "_" + mip_model + "_" + str(v) + "_" + str(h) + "_" + str(r) + ".png"
fig = plt.gcf()
fig.set_size_inches(1.2*l/1000, 1.23*a/1000, forward=True)
fig.savefig(figname, dpi=200)

plt.show() # comment this line to not display figure on screen
            
# End of code