import didppy as dp

# Number of locations
n = 4
# Travel time
w = [
    [0, 3, 4, 5],
    [3, 0, 5, 4],
    [4, 5, 0, 3],
    [5, 4, 3, 0],
]

model = dp.Model(maximize=False, float_cost=False)

customer = model.add_object_type(number=n)

# U
unvisited = model.add_set_var(object_type=customer, target=list(range(1, n)))
# i
location = model.add_element_var(object_type=customer, target=0)
# t (resource variable)
time = model.add_int_resource_var(target=0, less_is_better=True)

delete_table = model.add_set_table([[[], [], [], [2]], 
     [[], [], [0], []],
     [[], [0], [], [1,3]],
     [[2], [], [1,3], []]], object_type=customer)
travel_time = model.add_int_table(w)

for j in range(1, n):
    visit = dp.Transition(
        name="visit {}".format(j),
        cost=travel_time[location, j] + dp.IntExpr.state_cost(),
        preconditions=[unvisited.contains(j), delete_table[location,j].issuperset(unvisited)],
        effects=[
            (unvisited, unvisited.remove(j)),
            (location, j),
            (time, time + travel_time[location, j]),
        ],
    )
    model.add_transition(visit)

return_to_depot = dp.Transition(
    name="return",
    cost=travel_time[location, 0] + dp.IntExpr.state_cost(),
    effects=[
        (location, 0),
        (time, time + travel_time[location, 0]),
    ],
    preconditions=[unvisited.is_empty(), location != 0],
)
model.add_transition(return_to_depot)

model.add_base_case([unvisited.is_empty(), location == 0])

for j in range(1, n):
    model.add_state_constr(
        ~unvisited.contains(j)
    )

min_to = model.add_int_table(
    [min(w[k][j] for k in range(n) if k != j) for j in range(n)]
)

model.add_dual_bound(min_to[unvisited] + (location != 0).if_then_else(min_to[0], 0))

min_from = model.add_int_table(
    [min(w[j][k] for k in range(n) if k != j) for j in range(n)]
)

model.add_dual_bound(
    min_from[unvisited] + (location != 0).if_then_else(min_from[location], 0)
)

solver = dp.CABS(model)
solution = solver.search()

print("Transitions to apply:")

for t in solution.transitions:
    print(t.name)

print("Cost: {}".format(solution.cost))