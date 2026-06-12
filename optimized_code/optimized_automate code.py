# -*- coding: utf-8 -*-
"""
Created on Sat May 29 13:36:36 2021

@author: seune
"""
# Import necessary libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import glob
import os

# Function to read CSV file
def read_csv_file(file_path):
    try:
        df = pd.read_csv(file_path)
        print(df.head(5))
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except pd.errors.EmptyDataError:
        print(f"No data: {file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Function to get the latest file
def get_latest_file(directory, pattern='*'):
    try:
        list_of_files = glob.glob(os.path.join(directory, pattern))
        if not list_of_files:
            raise FileNotFoundError("No files found in the directory.")
        latest_file = max(list_of_files, key=os.path.getctime)
        return latest_file
    except Exception as e:
        print(f"An error occurred while fetching the latest file: {e}")
        return None

# Main execution
if __name__ == "__main__":
    # Read the CSV file
    csv_file_path = r"C:\\Users\\seune\\desktop\\Dataset\\Loan_Data\\test_Loan_data.csv"
    read_csv_file(csv_file_path)

    # Get the latest file
    directory = 'H:/periodic-reports/final-reports/'
    latest_file = get_latest_file(directory)
    if latest_file:
        print(f"Latest file: {latest_file}")

# Note: Package installations should be handled outside of the script.