import pandas as pd
import numpy as np
import csv
from scipy.io import arff
import matplotlib.pyplot as plt

from data_processing.apriori_algorithm import Apriori

class AprioriDataProcessor:
    def __init__(self):
        self.__raw_rows = []
        self.__df: pd.DataFrame = None
        self.__dimension = 0
        self.__unique_items = None

        self.__supported_datafiles = {"csv", "arff"}
        self.__parameters = {}

        self.__rules = []

    def set_parameters(self, parameters: dict = {}):
        if parameters == {}:
            print(f"[ERROR] Passed parameters are empty!")
            return
        self.__parameters = parameters

    def process_data(self, filepath: str, fixed_length = True, ommit_first_column = True):
        self.__load_data_file(filepath, fixed_length, ommit_first_column)

        if self.__raw_rows == None or self.__raw_rows == []:
            print(f"[ERROR] Could not run the processing. Data was not loaded!")
            return
        if self.__raw_rows == None or len(self.__raw_rows) == 0:
            print(f"[ERROR] Row data supplied for Apriori algorithm is empty.")
            return
        if self.__parameters["min_sup"] == None or self.__parameters["min_sup"] < 0:
            print(f"[ERROR] min_sup has to be greater or equal to 0.")
            return
        if self.__parameters["min_conf"] == None or self.__parameters["min_conf"] < 0 or self.__parameters["min_conf"] > 1:
            print(f"[ERROR] min_conf has to be a value between 0 and 1.")
            return
        if self.__unique_items == None or len(self.__unique_items) == 0:
            print(f"[ERROR] Unique item set is empty.")
            return

        # Run Apriori algorithm
        ap = Apriori(
            min_sup = self.__parameters["min_sup"],
            min_conf = self.__parameters["min_conf"]
        )
        self.__rules = ap.run(self.__raw_rows, self.__unique_items)
        sorted_rules = sorted(self.__rules, key = lambda x: (-x["sup"], -x["conf"]))

        return sorted_rules, len(self.__raw_rows)
    
    def show_plots(self):
        if self.__rules == []:
            return

        supports = []
        confidences = []
        lifts = []
        cosines = []
        jaccards = []
        certainty_factors = []

        for rule_data in self.__rules:
            supports.append(rule_data["sup"])
            confidences.append(rule_data["conf"])
            lifts.append(rule_data["lift"])
            cosines.append(rule_data["cosine"])
            jaccards.append(rule_data["jaccard"])
            certainty_factors.append(rule_data["cf"])

        supports_array = np.sort(np.array(supports))
        confidences_array = np.sort(np.array(confidences))
        lifts_array = np.sort(np.array(lifts))
        cosines_array = np.sort(np.array(cosines))
        jaccards_array = np.sort(np.array(jaccards))
        certainty_factors_array = np.sort(np.array(certainty_factors))

        # Create subplots
        fig, axs = plt.subplots(2, 2, figsize = (12, 10))

        # Support vs. Confidence
        axs[0, 0].scatter(supports_array, confidences_array, color = "blue", s = 10)
        axs[0, 0].set_title("Support vs. Confidence")
        axs[0, 0].set_xlabel("Support")
        axs[0, 0].set_ylabel("Confidence")

        # Lift vs. Cosine
        axs[0, 1].scatter(lifts_array, cosines_array, color = "green", s = 10)
        axs[0, 1].set_title("Lift vs. Cosine")
        axs[0, 1].set_xlabel("Lift")
        axs[0, 1].set_ylabel("Cosine")

        # Lift vs. Jaccard
        axs[1, 0].scatter(lifts_array, jaccards_array, color = "red", s = 10)
        axs[1, 0].set_title("Lift vs. Jaccard")
        axs[1, 0].set_xlabel("Lift")
        axs[1, 0].set_ylabel("Jaccard")

        # Lift vs. Certainty Factor
        axs[1, 1].scatter(lifts_array, certainty_factors_array, color = "purple", s = 10)
        axs[1, 1].set_title("Lift vs. Certainty Factor")
        axs[1, 1].set_xlabel("Lift")
        axs[1, 1].set_ylabel("Certainty Factor")

        plt.tight_layout()
        plt.show()

    def __load_data_file(self, filepath: str, fixed_length = True, ommit_first_column = False):
        ext = filepath.split(".")[-1]
        if ext not in self.__supported_datafiles:
            print(f"[ERROR] Could not load data. Data format '{ext}' is not supported!")
            return None

        # Load appropriate data file format
        if ext == "csv":
            if fixed_length == True:
                self.__load_csv_fixed(filepath, ommit_first_column)
            else:
                self.__load_csv_non_fixed(filepath)
        elif ext == "arff":
            self.__load_arff(filepath)   
        self.__count_unique_elements()     

    def __count_unique_elements(self):
        print(f"[INFO] Counting number of unique items...")
        self.__unique_items = set()
        for row in self.__raw_rows:
            self.__unique_items.update(row)
        self.__dimension = len(self.__unique_items)
        print(f"    |---- Done. Number of unique elements: {self.__dimension}")

    def __load_csv_non_fixed(self, filepath):
        self.__raw_rows = []
        with open(filepath, "r") as file:
            for line in file:
                row = {item.strip() for item in line.split(",")}
                self.__raw_rows.append(row)

    def __load_csv_fixed(self, filepath, ommit_first_column = False):
        self.__raw_rows = []
        if ommit_first_column == True:
            columns = pd.read_csv(filepath, nrows = 0).columns
            self.__df = pd.read_csv(filepath, usecols = columns[1:])
        else:
            self.__df = pd.read_csv(filepath)

        for index, row in self.__df.iterrows():
            row_set = {f"{col}={row[col]}" for col in self.__df.columns if pd.notna(row[col])}
            self.__raw_rows.append(row_set)
        
    def __load_arff(self, filepath):
        self.__raw_rows = []
        data, meta = arff.loadarff(filepath)
        self.__df = pd.DataFrame(data)

        # Convert 0/1 float values to integers and byte strings to regular strings
        for col in meta.names():
            if meta[col][0] == "nominal":
                self.__df[col] = self.__df[col].str.decode("utf-8")
            else:
                self.__df[col] = self.__df[col].astype(int)
            
        for index, row in self.__df.iterrows():
            row_set = {f"{meta.names()[i]}={row.iloc[i]}" for i in range(len(meta.names()))}
            self.__raw_rows.append(row_set)
