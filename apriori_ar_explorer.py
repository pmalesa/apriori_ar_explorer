from data_processing.apriori_data_processor import AprioriDataProcessor
from gui.gui_module import GUIModule

# For development
import argparse

def main(filepath: str):
    print("Starting Apriori Association Rules Explorer")

    # TODO
    # gm = GUIModule()
    # gm.run()

    adp = AprioriDataProcessor()
    adp.set_parameters({"min_sup": 60, "min_conf": 0.65})
    adp.run(filepath, fixed_length = False, ommit_first_column = False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = "Run the script by choosing the specific model to test.")
    parser.add_argument("filepath", help = "Path to a data file to analyze.")
    args = parser.parse_args()
    main(args.filepath)