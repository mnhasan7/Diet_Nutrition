import cvxpy as cp
import pandas as pd
import numpy as np

# Load cleaned dataset
df = pd.read_excel("food_data_with_prices (1).xlsx")

# Remove unnamed columns
df = df.loc[:, ~df.columns.str.contains('Unnamed')]

# Extract key arrays (convert per 100 g → per gram)
price = df["Market Price (USD per gram)"].values
cal = df["Caloric Value"].values / 100
protein = df["Protein"].values / 100
carb = df["Carbohydrates"].values / 100
fat = df["Fat"].values / 100
fiber = df["Dietary Fiber"].values / 100
sodium = df["Sodium"].values / 100
sugar = df["Sugars"].values / 100
n = len(df)

# Decision variable
x = cp.Variable(n, nonneg=True)

# Constraints
constraints = []

# Calorie constraints
constraints += [
    cal @ x >= 1200,
    cal @ x <= 1400
]

# Macro constraints
constraints += [
    protein @ x >= 25,
    carb @ x >= 50,
    carb @ x <= 110,
    fat @ x >= 10,
    fat @ x <= 35,
    fiber @ x >= 8,
]


# Sugar + sodium limits
constraints += [
    sugar @ x <= 20,
    sodium @ x <= 2
]

# Total meal size
constraints += [
    cp.sum(x) >= 350,
    cp.sum(x) <= 600
]

# Objective: minimize cost
objective = cp.Minimize(price @ x)
problem = cp.Problem(objective, constraints)

problem.solve(solver=cp.ECOS)

print("Optimal cost:", price @ x.value)
print("Weights (g):")
for food, grams in zip(df["food"], x.value):
    if grams > 1e-3:
        print(food, round(grams, 2))

