import cvxpy as cp
import pandas as pd
import numpy as np

df = pd.read_excel("food_data_with_prices_with_category.xlsx")
df = df.loc[:, ~df.columns.str.contains("Unnamed")]

for col in ["Caloric Value","Fat","Carbohydrates","Sugars","Protein","Dietary Fiber","Sodium"]:
    df[col] = df[col].fillna(0.0)

# Convert per 100g → per gram
price   = df["Market Price (USD per gram)"].values
cal     = df["Caloric Value"].values / 100.0
protein = df["Protein"].values / 100.0
carb    = df["Carbohydrates"].values / 100.0
fat     = df["Fat"].values / 100.0
fiber   = df["Dietary Fiber"].values / 100.0
sodium  = df["Sodium"].values / 100.0
sugar   = df["Sugars"].values / 100.0

n = len(df)
x = cp.Variable(n, nonneg=True)

# CONSTRAINTS
constraints = [
    cal @ x >= 500,
    cal @ x <= 800,

    carb @ x >= 50,
    carb @ x <= 110,

    fat @ x >= 10,
    fat @ x <= 35,

    fiber @ x >= 8,
    sugar @ x <= 40,
    sodium @ x <= 2,

    cp.sum(x) >= 350,
    cp.sum(x) <= 600,
]

# OBJECTIVE: MAXIMIZE PROTEIN
problem = cp.Problem(cp.Minimize(-protein @ x), constraints)
problem.solve(solver=cp.ECOS)

x_val = x.value

# PRINT RESULTS
def summarize_solution(x, df):
    idx = np.where(x > 1e-3)[0]  # nonzero foods

    total_cost = float((price * x).sum())
    total_weight = float(x.sum())
    total_cal = float((cal * x).sum())
    total_prot = float((protein * x).sum())
    total_carb = float((carb * x).sum())
    total_fat = float((fat * x).sum())
    total_fiber = float((fiber * x).sum())
    total_sodium = float((sodium * x).sum())
    total_sugar = float((sugar * x).sum())

    print("\n HIGH-PROTEIN OPTIMAL MEAL ")
    print("Ingredients :\n")
    for i in idx:
        print(f"{df['food'][i]} → {x[i]:.1f} g")

    print("\n TOTALS:")
    print(f"Total Weight : {total_weight:.2f} g")
    print(f"Calories     : {total_cal:.2f} kcal")
    print(f"Protein      : {total_prot:.2f} g")
    print(f"Carbs        : {total_carb:.2f} g")
    print(f"Fat          : {total_fat:.2f} g")
    print(f"Fiber        : {total_fiber:.2f} g")
    print(f"Sodium       : {total_sodium:.2f} g")
    print(f"Sugar        : {total_sugar:.2f} g")
    print(f"Total Cost   : ${total_cost:.2f}")

summarize_solution(x_val, df)
