from data_processing.apriori_data_processor import AprioriDataProcessor
from gui.gui_module import GUIModule

def main():
    print("Starting Apriori Association Rules Explorer")
    gm = GUIModule()
    gm.run()

if __name__ == "__main__":
    main()