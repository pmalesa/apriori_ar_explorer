import pandas as pd
import numpy as numpy
import csv
from scipy.io import arff

from data_processing.apriori_algorithm import Apriori

class AprioriDataProcessor:
    def __init__(self):
        self.__raw_rows = [] # list of sets
        self.__df: pd.DataFrame = None
        self.__dimension = 0
        self.__unique_items = None

        self.__supported_datafiles = {"csv", "arff"}
        self.__parameters = {}

    def set_parameters(self, parameters: dict = {}):
        if parameters == {}:
            print(f"[ERROR] Passed parameters are empty!")
            return
        self.__parameters = parameters

    def run(self, filepath: str, fixed_length = True, ommit_first_column = True):
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
        results = ap.run(self.__raw_rows, self.__unique_items)

        # Process results
        # ...

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

### TODO ###
        
# 2) Zaimplementuj Apriori (najpierw wyszukaj częste zbiory a potem silne reguły na podstawie minSup i minConf)
# 3) Ogarnij liczenie tych metryk dla odkrytych silnych i częstych reguł asocjacyjnych:
#       - cosine,
#       - Jaccard,
#       - odds_ratio,
# 4) Zwróć wyniki do okna gui z wynikiami
# 5) Zrób gui do wpisywania parametrów wejściowych
