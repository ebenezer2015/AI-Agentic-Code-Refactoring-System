import numpy as np
import pandas as pd

class LoanCalculationError(Exception):
    pass

def optmised_schedule(provider: str, amount: float, initial_rate: float, paymentsperyear: int, years: int, product_fees: float, initial_fixed_period=0, follow_on_rate=0.0):
    if paymentsperyear <= 0:
        raise LoanCalculationError("Payments per year must be greater than zero.")
    if years <= 0:
        raise LoanCalculationError("Years must be greater than zero.")
    if amount <= 0:
        raise LoanCalculationError("Loan amount must be greater than zero.")
    if initial_rate < 0 or follow_on_rate < 0:
        raise LoanCalculationError("Interest rates cannot be negative.")
    if product_fees < 0:
        raise LoanCalculationError("Product fees cannot be negative.")

    def PMT(int_rate, no_instalment, loan_amount):
        if no_instalment <= 0:
            raise LoanCalculationError("Number of instalments must be greater than zero.")
        if int_rate != 0:
            pmt = (int_rate * loan_amount * (1 + int_rate) ** no_instalment) / (1 - (1 + int_rate) ** -no_instalment)
        else:
            pmt = loan_amount / no_instalment
        return round(pmt, 2)

    def IPMT(int_rate, per, no_instalment, loan_amount):
        ipmt = -(((1 + int_rate) ** (per - 1)) * (loan_amount * int_rate + PMT(int_rate, no_instalment, loan_amount)) - PMT(int_rate, no_instalment, loan_amount))
        return round(ipmt, 2)

    def PPMT(int_rate, per, no_instalment, loan_amount):
        ppmt = PMT(int_rate, no_instalment, loan_amount) - IPMT(int_rate, per, no_instalment, loan_amount)
        return round(ppmt, 2)

    annual_interest_rate = initial_rate / 100
    total_payments = paymentsperyear * years

    df = pd.DataFrame({
        'Principal': [PPMT(annual_interest_rate / paymentsperyear, i + 1, total_payments, amount) for i in range(total_payments)],
        'Interest': [IPMT(annual_interest_rate / paymentsperyear, i + 1, total_payments, amount) for i in range(total_payments)]
    })

    df['Instalment'] = df.Principal + df.Interest
    df['Balance'] = amount - np.cumsum(df.Principal)
    df['Total_Interest_Paid'] = np.cumsum(df.Interest)
    df['Total_Principal_Paid'] = np.cumsum(df.Principal)
    df['Total_Instalment_Paid'] = np.cumsum(df.Instalment)
    df['Product_Fees'] = product_fees
    df['Loan'] = amount
    df['Interest_Rate'] = initial_rate
    df['Fixed_Period'] = initial_fixed_period

    if initial_fixed_period == 0 and follow_on_rate == 0:
        return df.iloc[:, 2:].head(2 * paymentsperyear).tail(1).reset_index(drop=True)
    elif (initial_fixed_period == 0 and follow_on_rate != 0) or (initial_fixed_period != 0 and follow_on_rate == 0):
        return "One of these is missing, either the follow on rate or the initial fixed period?"
    elif initial_fixed_period != 0 and follow_on_rate != 0:
        follow_on_year = years - initial_fixed_period
        follow_rate = follow_on_rate / 100
        df1 = df.head(initial_fixed_period * paymentsperyear)
        bal = df1.tail(1)['Balance'].to_numpy()[0]
        df2 = pd.DataFrame({
            'Principal': [PPMT(follow_rate / paymentsperyear, i + 1, paymentsperyear * follow_on_year, bal) for i in range(paymentsperyear * follow_on_year)],
            'Interest': [IPMT(follow_rate / paymentsperyear, i + 1, paymentsperyear * follow_on_year, bal) for i in range(paymentsperyear * follow_on_year)]
        })

        df2['Instalment'] = df2.Principal + df2.Interest
        df2['Balance'] = bal - np.cumsum(df2.Principal)
        df3 = pd.concat([df1, df2]).reset_index(drop=True)
        df3['Total_Interest_Paid'] = np.cumsum(df3.Interest)
        df3['Total_Principal_Paid'] = np.cumsum(df3.Principal)
        df3['Total_Instalment_Paid'] = np.cumsum(df3.Instalment)
        df3['Product_Fees'] = product_fees
        df3['Loan'] = amount
        df3['Interest_Rate'] = initial_rate
        df3['Fixed_Period'] = initial_fixed_period
        df3['Provider'] = provider

        return df3.iloc[:, 2:].head(initial_fixed_period * paymentsperyear).tail(1).reset_index(drop=True)