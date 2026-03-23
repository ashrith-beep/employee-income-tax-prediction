import pandas as pd
import numpy as np

np.random.seed(42)
n = 5000

def compute_tax(taxable_income):
    """Indian Old Regime Tax Slabs (simplified)."""
    tax = 0
    if taxable_income <= 250000:
        tax = 0
    elif taxable_income <= 500000:
        tax = (taxable_income - 250000) * 0.05
    elif taxable_income <= 1000000:
        tax = 12500 + (taxable_income - 500000) * 0.20
    else:
        tax = 112500 + (taxable_income - 1000000) * 0.30

    # Add 4% health and education cess
    tax = tax + tax * 0.04
    return max(0, round(tax, 2))

annual_salary    = np.random.randint(200000, 5000000, n)
other_income     = np.random.randint(0, 500000, n)
investments      = np.random.randint(0, 150000, n)   # 80C limit
deductions       = np.random.randint(0, 100000, n)   # 80D, HRA etc.
age              = np.random.randint(21, 65, n)

# Standard deduction of 50000 for salaried
standard_deduction = 50000

gross_income     = annual_salary + other_income
taxable_income   = np.maximum(0, gross_income - investments - deductions - standard_deduction)

tax_paid = np.array([compute_tax(ti) for ti in taxable_income])

df = pd.DataFrame({
    'annual_salary': annual_salary,
    'other_income': other_income,
    'investments': investments,
    'deductions': deductions,
    'age': age,
    'tax_paid': tax_paid
})

df.to_csv('tax_dataset.csv', index=False)
print(f"Dataset generated: {len(df)} rows saved to tax_dataset.csv")
print(df.describe())
