# 11/15/25 - Data-driven code with proper units - Mohammad Hasan

import cvxpy as cp
import numpy as np
import pandas as pd
import os

# ---------------------------------------------------------------------
# 1. Load dataset from Datasets/ folder
# ---------------------------------------------------------------------
DATA_DIR = "Datasets"
FILENAME = "food_data_with_prices.csv" 
DATA_PATH = os.path.join(DATA_DIR, FILENAME)

#Checksum
if DATA_PATH.endswith(".csv"):
    try:
        df = pd.read_csv(DATA_PATH)
    except FileNotFoundError:
        DATA_PATH = os.path.join(DATA_DIR, "food_data_with_prices.xlsx")
        df = pd.read_excel(DATA_PATH)
else:
    df = pd.read_excel(DATA_PATH)

# Basic cleaning: drop rows without price or calories/protein
df = df.dropna(subset=["Market Price (USD per gram)", "Caloric Value", "Protein"])
df = df[df["Market Price (USD per gram)"] > 0].reset_index(drop=True)

food_names = df["food"].astype(str).tolist()
n = len(df)

# ---------------------------------------------------------------------
# 2. Build per-gram nutrient arrays
#    Dataset is per 100 g, so divide by 100 to get "per gram"
# ---------------------------------------------------------------------

# conversion factor constant
PER_100G_TO_PER_G = 100.0

# function to convert nutrient values with error handling
def get_nutrient_per_g(column_name, conversion_factor=PER_100G_TO_PER_G):
    """Extract nutrient data and convert to per-gram basis."""
    if column_name not in df.columns:
        print(f"Warning: Column '{column_name}' not found in dataset")
        return np.zeros(n)
    return df[column_name].fillna(0).to_numpy() / conversion_factor

# Cost per gram (already per gram per dataset description)
c = get_nutrient_per_g("Market Price (USD per gram)", conversion_factor=1.0)  # USD / g

# Macronutrients and other main nutrients (per 100 g → per g)
cal_per_g   = get_nutrient_per_g("Caloric Value")              # kcal/g
fat_per_g   = get_nutrient_per_g("Fat")                        # g/g
sat_per_g   = get_nutrient_per_g("Saturated Fats")             # g/g
mono_per_g  = get_nutrient_per_g("Monounsaturated Fats")       # g/g
poly_per_g  = get_nutrient_per_g("Polyunsaturated Fats")       # g/g
carb_per_g  = get_nutrient_per_g("Carbohydrates")              # g/g
sugar_per_g = get_nutrient_per_g("Sugars")                     # g/g
prot_per_g  = get_nutrient_per_g("Protein")                    # g/g
fib_per_g   = get_nutrient_per_g("Dietary Fiber")              # g/g

# Cholesterol: mg per 100 g → mg/g
chol_per_g  = get_nutrient_per_g("Cholesterol")                # mg/g

# Sodium: mg per 100 g → mg/g
Na_per_g    = get_nutrient_per_g("Sodium")                     # mg/g

# Water: g per 100 g → g/g
water_per_g = get_nutrient_per_g("Water")                      # g/g

# Minerals: mg per 100 g → mg/g (using dictionary for cleaner code)
mineral_names = ["Calcium", "Copper", "Iron", "Magnesium", "Manganese", 
                 "Phosphorus", "Potassium", "Selenium", "Zinc"]
minerals_per_g = {mineral: get_nutrient_per_g(mineral) for mineral in mineral_names}

# Create individual variables for backward compatibility
Calcium_per_g    = minerals_per_g["Calcium"]
Copper_per_g     = minerals_per_g["Copper"]
Iron_per_g       = minerals_per_g["Iron"]
Magnesium_per_g  = minerals_per_g["Magnesium"]
Manganese_per_g  = minerals_per_g["Manganese"]
Phosphorus_per_g = minerals_per_g["Phosphorus"]
Potassium_per_g  = minerals_per_g["Potassium"]
Selenium_per_g   = minerals_per_g["Selenium"]
Zinc_per_g       = minerals_per_g["Zinc"]

# Vitamins: treat all as "per 100 g → per g" regardless of mg / µg;
# we'll just report totals with a unit tag.
vitamin_cols = [col for col in df.columns if col.startswith("Vitamin ")]
vitamins_per_g = {col: get_nutrient_per_g(col) for col in vitamin_cols}

# nutrition density (unitless score per 100 g → per g)
if "Nutrition Density" in df.columns:
    nutrition_density_per_g = df["Nutrition Density"].to_numpy() / 100.0
else:
    nutrition_density_per_g = None

def show_range(name, value, lower=None, upper=None, unit=""):
    s = f"{name:20s}: {value:.2f} {unit}"
    if lower is not None:
        s += f" (min {lower} {unit})"
    if upper is not None:
        s += f", (max {upper} {unit})"
    print(s)

def solve_diet(
    name,
    C_min, C_max,
    P_min,
    Carb_min, Carb_max,
    Fat_min, Fat_max,
    Fib_min,
    Na_max,
    Sug_max,
    Chol_max,
    SatFat_max
):
    print("\n" + "="*60)
    print(f"Scenario: {name}")
    print("="*60)

    n = len(c)  # cost vector from before
    x = cp.Variable(n, nonneg=True)

    u = np.full(n, 1000.0)
    constraints = [x <= u]

    # Calories
    constraints += [cal_per_g @ x >= C_min,
                    cal_per_g @ x <= C_max]

    # Protein
    constraints += [prot_per_g @ x >= P_min]

    # Carbs
    constraints += [carb_per_g @ x >= Carb_min,
                    carb_per_g @ x <= Carb_max]

    # Fat
    constraints += [fat_per_g @ x >= Fat_min,
                    fat_per_g @ x <= Fat_max]

    # Fiber
    constraints += [fib_per_g @ x >= Fib_min]

    # Sodium
    constraints += [Na_per_g @ x <= Na_max]

    # Sugar
    constraints += [sugar_per_g @ x <= Sug_max]

    # Cholesterol
    constraints += [chol_per_g @ x <= Chol_max]

    # Sat fat
    constraints += [sat_per_g @ x <= SatFat_max]

    # (Optionally keep mineral constraints too, or drop if infeasible) - I did not add it - Maybe if we have character with mineral constrains we can certainly add them here
    constraints += [
        Calcium_per_g    @ x >= Ca_min,
        Iron_per_g       @ x >= Iron_min,
        Magnesium_per_g  @ x >= Mag_min,
        Phosphorus_per_g @ x >= Phos_min,
        Potassium_per_g  @ x >= K_min,
    ]

    objective = cp.Minimize(c @ x)
    prob = cp.Problem(objective, constraints)
    prob.solve()

    print("Status:", prob.status)
    if prob.status not in ["optimal", "optimal_inaccurate"]:
        print("Infeasible or failed for this profile.")
        return

    print(f"Optimal cost: ${prob.value:.2f} USD")

    print("\nSelected foods (non-zero):")
    for i in range(n):
        if x.value[i] is not None and x.value[i] > 1e-3:
            print(f"  {food_names[i]:30s} -> {x.value[i]:7.1f} g")

    # Compute totals
    total_cal   = float(cal_per_g   @ x.value)
    total_prot  = float(prot_per_g  @ x.value)
    total_carb  = float(carb_per_g  @ x.value)
    total_fat   = float(fat_per_g   @ x.value)
    total_fib   = float(fib_per_g   @ x.value)
    total_sugar = float(sugar_per_g @ x.value)
    total_Na    = float(Na_per_g    @ x.value)
    total_chol  = float(chol_per_g  @ x.value)
    total_sat   = float(sat_per_g   @ x.value)

    # Show constraint checks
    show_range("Calories", total_cal, C_min, C_max, "kcal")
    show_range("Protein", total_prot, P_min, None, "g")
    show_range("Carbs", total_carb, Carb_min, Carb_max, "g")
    show_range("Fat", total_fat, Fat_min, Fat_max, "g")
    show_range("Fiber", total_fib, Fib_min, None, "g")
    show_range("Sugar", total_sugar, None, Sug_max, "g")
    show_range("Sodium", total_Na, None, Na_max, "mg")
    show_range("Cholesterol", total_chol, None, Chol_max, "mg")
    show_range("Sat fat", total_sat, None, SatFat_max, "g")

    print()  # blank line


# ---------------------------------------------------------------------
# 3. Daily requirements / limits (example values)
#    These are totals for the WHOLE DAY
# ---------------------------------------------------------------------
C_min, C_max        = 2200, 2600       # kcal/day
P_min               = 120              # g/day
Carb_min, Carb_max  = 200, 350         # g/day
Fat_min, Fat_max    = 50, 90           # g/day
Fib_min             = 25               # g/day
Na_max              = 2300             # mg/day
Sug_max             = 50               # g/day
Chol_max            = 300              # mg/day
SatFat_max          = 30               # g/day

# Example mineral targets (you can tune these)
Ca_min      = 800    # mg/day
Iron_min    = 8      # mg/day
Mag_min     = 200    # mg/day
Phos_min    = 700    # mg/day
K_min       = 2500   # mg/day

# ---------------------------------------------------------------------
# 4. CVX optimization problem
#    Decision variable x_i = grams of food i
# ---------------------------------------------------------------------
x = cp.Variable(n, nonneg=True)  # grams

# Upper bound: say max 1000 g per item (1 kg) for realism
u = np.full(n, 1000.0)  # grams
constraints = [x <= u]

# Energy
constraints += [
    cal_per_g @ x >= C_min,
    cal_per_g @ x <= C_max
]

# Protein
constraints += [prot_per_g @ x >= P_min]

# Carbs
constraints += [
    carb_per_g @ x >= Carb_min,
    carb_per_g @ x <= Carb_max
]

# Total fat
constraints += [
    fat_per_g @ x >= Fat_min,
    fat_per_g @ x <= Fat_max
]

# Fiber
constraints += [fib_per_g @ x >= Fib_min]

# Sodium (mg)
constraints += [Na_per_g @ x <= Na_max]

# Sugar (g)
constraints += [sugar_per_g @ x <= Sug_max]

# Cholesterol (mg)
constraints += [chol_per_g @ x <= Chol_max]

# Saturated fat (g)
constraints += [sat_per_g @ x <= SatFat_max]

# Minerals (mg)
constraints += [
    Calcium_per_g    @ x >= Ca_min,
    Iron_per_g       @ x >= Iron_min,
    Magnesium_per_g  @ x >= Mag_min,
    Phosphorus_per_g @ x >= Phos_min,
    Potassium_per_g  @ x >= K_min,
]

# Objective: minimize total cost (USD)
objective = cp.Minimize(c @ x)

problem = cp.Problem(objective, constraints)
problem.solve()

# ---------------------------------------------------------------------
# 5. Display results with units
# ---------------------------------------------------------------------
print("Status:", problem.status)
if problem.status not in ["optimal", "optimal_inaccurate"]:
    print("Problem is not optimal; maybe constraints are too strict.")
else:
    print(f"Optimal cost: ${problem.value:.2f} USD")

    print("\nSelected foods (non-zero):")
    for i in range(n):
        if x.value[i] is not None and x.value[i] > 1e-3:
            print(f"  {food_names[i]:30s} -> {x.value[i]:7.1f} g")

    # Totals
    total_cal   = float(cal_per_g   @ x.value)  # kcal
    total_prot  = float(prot_per_g  @ x.value)  # g
    total_carb  = float(carb_per_g  @ x.value)  # g
    total_fat   = float(fat_per_g   @ x.value)  # g
    total_sat   = float(sat_per_g   @ x.value)  # g
    total_mono  = float(mono_per_g  @ x.value)  # g
    total_poly  = float(poly_per_g  @ x.value)  # g
    total_fib   = float(fib_per_g   @ x.value)  # g
    total_sugar = float(sugar_per_g @ x.value)  # g
    total_chol  = float(chol_per_g  @ x.value)  # mg
    total_Na    = float(Na_per_g    @ x.value)  # mg
    total_water = float(water_per_g @ x.value)  # g

    print("\n=== Nutrient totals ===")
    print(f"Total calories:       {total_cal:.1f} kcal")
    print(f"Total protein:        {total_prot:.1f} g")
    print(f"Total carbs:          {total_carb:.1f} g")
    print(f"Total fat:            {total_fat:.1f} g")
    print(f"  Saturated fat:      {total_sat:.1f} g")
    print(f"  Monounsaturated:    {total_mono:.1f} g")
    print(f"  Polyunsaturated:    {total_poly:.1f} g")
    print(f"Total fiber:          {total_fib:.1f} g")
    print(f"Total sugar:          {total_sugar:.1f} g")
    print(f"Total cholesterol:    {total_chol:.1f} mg")
    print(f"Total sodium:         {total_Na:.1f} mg")
    print(f"Total water:          {total_water:.1f} g")

    print("\n=== Mineral totals (approx) ===")
    print(f"Calcium:              {float(Calcium_per_g    @ x.value):.1f} mg")
    print(f"Copper:               {float(Copper_per_g     @ x.value):.2f} mg")
    print(f"Iron:                 {float(Iron_per_g       @ x.value):.2f} mg")
    print(f"Magnesium:            {float(Magnesium_per_g  @ x.value):.1f} mg")
    print(f"Manganese:            {float(Manganese_per_g  @ x.value):.2f} mg")
    print(f"Phosphorus:           {float(Phosphorus_per_g @ x.value):.1f} mg")
    print(f"Potassium:            {float(Potassium_per_g  @ x.value):.1f} mg")
    print(f"Selenium:             {float(Selenium_per_g   @ x.value):.2f} mg")
    print(f"Zinc:                 {float(Zinc_per_g       @ x.value):.2f} mg")

    print("\n=== Vitamin totals (approx, from dataset units) ===")
    for vit_name, vit_arr_per_g in vitamins_per_g.items():
        total_vit = float(vit_arr_per_g @ x.value)
        print(f"{vit_name:20s}: {total_vit:.4f} (per-day total in dataset units)")

    if nutrition_density_per_g is not None:
        total_nd = float(nutrition_density_per_g @ x.value)
        print(f"\nNutrition density (weighted sum over grams): {total_nd:.2f}")


# Example scenarios - User with different constraints
solve_diet(
    name="Person A - 21yo male, moderately active",
    C_min=2600, C_max=2900,
    P_min=130,
    Carb_min=260, Carb_max=380,
    Fat_min=70, Fat_max=100,
    Fib_min=25,
    Na_max=2300,
    Sug_max=50,
    Chol_max=300,
    SatFat_max=30
)

solve_diet(
    name="Person B - 35yo female, light activity",
    C_min=1800, C_max=2100,
    P_min=80,
    Carb_min=180, Carb_max=260,
    Fat_min=50, Fat_max=80,
    Fib_min=25,
    Na_max=2000,
    Sug_max=35,
    Chol_max=250,
    SatFat_max=22
)

solve_diet(
    name="Person C - 60yo, hypertension focus",
    C_min=1700, C_max=2000,
    P_min=90,
    Carb_min=160, Carb_max=240,
    Fat_min=50, Fat_max=75,
    Fib_min=25,
    Na_max=1500,
    Sug_max=35,
    Chol_max=200,
    SatFat_max=20
)
