# 11/08/25 - Initial example code - Mohammad Hasan

import cvxpy as cp
import numpy as np

# Problem data (example, We will add more food items)
# Number of foods
n = 6

# Cost per serving (c_i)
c = np.array([0.25, 1.50, 0.20, 0.35, 0.50, 0.90])

# Nutrient content per serving
cal  = np.array([150, 165, 110,  35, 164, 100])   # calories
P    = np.array([  5,  31, 2.6, 2.4,   6,  17])   # protein (g)
Carb = np.array([ 27,   0,  23,   7,   6,   6])   # carbs (g)
Fat  = np.array([  3, 3.6, 0.9, 0.4,  14,   0])   # fat (g)
Fib  = np.array([  4,   0, 1.8,   3, 3.5,   0])   # fiber (g)
Na   = np.array([  0,  70,   0,  30,   0,  60])   # sodium (mg)
Sug  = np.array([  1,   0,   0,   1,   1,   6])   # sugar (g)

# Daily requirements / limits (these are example values - I have an API fro Spoonacular but with their free version we can request ever 1 sec)
# Possible dataset (no price data): https://www.kaggle.com/datasets/utsavdey1410/food-nutrition-dataset 
C_min, C_max        = 2200, 2600       # calories range 
P_min               = 120              # min protein
Carb_min, Carb_max  = 200, 350         # carbs range
Fat_min, Fat_max    = 50, 90           # fat range
Fib_min             = 25               # min fiber
Na_max              = 2300             # max sodium
Sug_max             = 50               # max sugar

# Upper bounds for each food (for variety / realism)
u = np.array([10, 10, 10, 10, 10, 10])

# 2. Decision variable
# x_i = servings of food i
x = cp.Variable(n, nonneg=True)   # nonneg enforces x >= 0

# 3. Constraints
constraints = []

# Upper bounds 0 <= x_i <= u_i
constraints += [x <= u]

# Calories: C_min <= cal^T x <= C_max
constraints += [cal @ x >= C_min,
                cal @ x <= C_max]

# Protein: P^T x >= P_min
constraints += [P @ x >= P_min]

# Carbs: Carb_min <= Carb^T x <= Carb_max
constraints += [Carb @ x >= Carb_min,
                Carb @ x <= Carb_max]

# Fat: Fat_min <= Fat^T x <= Fat_max
constraints += [Fat @ x >= Fat_min,
                Fat @ x <= Fat_max]

# Fiber: Fib^T x >= Fib_min
constraints += [Fib @ x >= Fib_min]

# Sodium: Na^T x <= Na_max
constraints += [Na @ x <= Na_max]

# Sugar: Sug^T x <= Sug_max
constraints += [Sug @ x <= Sug_max]


# 4. Objective: minimize total cost
objective = cp.Minimize(c @ x)

# 5. Solve the problem
problem = cp.Problem(objective, constraints)
problem.solve()   # or leave empty and let cvxpy choose  (solver=cp.ECOS does not work)

# 6. Display results
print("Status:", problem.status)
print("Optimal cost:", problem.value)

food_names = ["Oatmeal", "Chicken", "Rice", "Broccoli", "Almonds", "Yogurt"]
for i in range(n):
    print(f"{food_names[i]} servings: {x.value[i]:.3f}")

# (Optional) check nutrients of the optimal solution
print("\nTotal calories:",  cal @ x.value)
print("Total protein:",    P @ x.value)
print("Total carbs:",      Carb @ x.value)
print("Total fat:",        Fat @ x.value)
print("Total fiber:",      Fib @ x.value)
print("Total sodium:",     Na @ x.value)
print("Total sugar:",      Sug @ x.value)
