# -*- coding: utf-8 -*-
"""
Created on Sat May 29 13:36:36 2021

@author: seune
"""
#Install the needed libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_csv(r"C:\\Users\\seune\\desktop\\Dataset\\Loan_Data\\test_Loan_data.csv")
df.head(5)

#To get the latest file 
import glob
import os

list_of_files = glob.glob('H:/periodic-reports/final-reports/*')
latest_file = max(list_of_files, key = os.path.getctime)
latest_file = latest_file.split('2018', 1)
latest_file = '2018' + latest_file[1]

# install pycaret
pip install -U pycaret