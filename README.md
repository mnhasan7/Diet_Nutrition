# Diet_Nutrition
Diet Nutrition Optimization - Convex Project Fall 2025


## Example Output Rev_02:
```
Status: optimal
Optimal cost: $2.55 USD

Selected foods (non-zero):
  burrito with beans beef        ->   295.9 g
  succotash                      ->   189.1 g
  chili beef soup                ->    36.0 g
  whopper burger king            ->    41.1 g

=== Nutrient totals ===
Total calories:       2200.0 kcal
Total protein:        120.0 g
Total carbs:          267.2 g
Total fat:            78.4 g
  Saturated fat:      30.0 g
  Monounsaturated:    31.2 g
  Polyunsaturated:    10.5 g
Total fiber:          25.0 g
Total sugar:          25.9 g
Total cholesterol:    241.8 mg
Total sodium:         6.4 mg
Total water:          814.7 g

=== Mineral totals (approx) ===
Calcium:              810.1 mg
Copper:               32.80 mg
Iron:                 21.98 mg
Magnesium:            395.9 mg
Manganese:            22.87 mg
Phosphorus:           1734.8 mg
Potassium:            3733.8 mg
Selenium:             379.12 mg
Zinc:                 18.57 mg

=== Vitamin totals (approx, from dataset units) ===
Vitamin A           : 0.3561 (per-day total in dataset units)
Vitamin B1          : 2.0390 (per-day total in dataset units)
Vitamin B11         : 0.8104 (per-day total in dataset units)
Vitamin B12         : 0.2618 (per-day total in dataset units)
Vitamin B2          : 1.5370 (per-day total in dataset units)
Vitamin B3          : 23.8159 (per-day total in dataset units)
Vitamin B5          : 5.4507 (per-day total in dataset units)
Vitamin B6          : 2.1562 (per-day total in dataset units)
Vitamin C           : 43.6557 (per-day total in dataset units)
Vitamin D           : 3.1284 (per-day total in dataset units)
Vitamin E           : 3.3785 (per-day total in dataset units)
Vitamin K           : 1.0770 (per-day total in dataset units)

Nutrition density (weighted sum over grams): 1366.65

============================================================
Scenario: Person A - 21yo male, moderately active
============================================================
Status: optimal
Optimal cost: $3.01 USD

Selected foods (non-zero):
  burrito with beans beef        ->   256.1 g
  succotash                      ->   386.3 g
  chili beef soup                ->    77.2 g
  whopper burger king            ->    45.7 g
Calories            : 2600.00 kcal (min 2600 kcal), (max 2900 kcal)
Protein             : 135.21 g (min 130 g)
Carbs               : 363.62 g (min 260 g), (max 380 g)
Fat                 : 79.19 g (min 70 g), (max 100 g)
Fiber               : 25.00 g (min 25 g)
Sugar               : 29.86 g, (max 50 g)
Sodium              : 7.78 mg, (max 2300 mg)
Cholesterol         : 232.91 mg, (max 300 mg)
Sat fat             : 30.00 g, (max 30 g)


============================================================
Scenario: Person B - 35yo female, light activity
============================================================
Status: optimal
Optimal cost: $2.22 USD

Selected foods (non-zero):
  burrito with beans beef        ->   270.6 g
  succotash                      ->   176.2 g
  pupusas con queso              ->    29.7 g
  bean ham soup                  ->    46.0 g
Calories            : 1800.00 kcal (min 1800 kcal), (max 2100 kcal)
Protein             : 101.11 g (min 80 g)
Carbs               : 232.80 g (min 180 g), (max 260 g)
Fat                 : 57.10 g (min 50 g), (max 80 g)
Fiber               : 25.00 g (min 25 g)
Sugar               : 18.35 g, (max 35 g)
Sodium              : 5.05 mg, (max 2000 mg)
Cholesterol         : 183.00 mg, (max 250 mg)
Sat fat             : 22.00 g, (max 22 g)


============================================================
Scenario: Person C - 60yo, hypertension focus
============================================================
Status: optimal
Optimal cost: $2.16 USD

Selected foods (non-zero):
  burrito with beans beef        ->   213.3 g
  succotash                      ->   188.5 g
  pupusas con queso              ->    53.0 g
  bean ham soup                  ->    80.0 g
Calories            : 1700.00 kcal (min 1700 kcal), (max 2000 kcal)
Protein             : 93.08 g (min 90 g)
Carbs               : 229.16 g (min 160 g), (max 240 g)
Fat                 : 51.43 g (min 50 g), (max 75 g)
Fiber               : 25.00 g (min 25 g)
Sugar               : 18.29 g, (max 35 g)
Sodium              : 4.59 mg, (max 1500 mg)
Cholesterol         : 157.45 mg, (max 200 mg)
Sat fat             : 20.00 g, (max 20 g)
```


## Example Output Rev_01:
```
Status: optimal
Optimal cost: 6.224641510115688

Oatmeal servings: 10.000
Chicken servings: 1.911
Rice servings: 2.323
Broccoli servings: 0.000
Almonds servings: 0.788
Yogurt servings: 0.000

Total calories: 2200.0000017834873
Total protein: 120.00000001174789
Total carbs: 328.15202172731045
Total fat: 50.00000006099113
Total fiber: 46.93874564686679
Total sodium: 133.75244983573992
Total sugar: 10.787912680558412
```

![Pic1](pic1.jpg)