# Project/main.py

from scripts.run_linear_regression import linear_regression
from scripts.run_polynomial_regression import polynomial_regression
from scripts.run_multivariate_regression import multivariate_regression

def main():
    #------
    print("Running linear regression...")
    linear_regression()

    # #------
    # print("Running polynomial regression...")
    # polynomial_regression()

    # #------
    # print("Running multivariate regression...")
    # multivariate_regression()

if __name__ == "__main__":
    main()
