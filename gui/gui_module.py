import os
import tkinter as tk
from tkinter import filedialog
import json

from data_processing.apriori_data_processor import AprioriDataProcessor

class GUIModule:
    def __init__(self):
        self.__filepath = ""
        self.__adp = AprioriDataProcessor()

        self.__root = tk.Tk()
        self.__root.title("Apriori Association Rule Explorer")
        self.__root.geometry("1200x900")
        self.__root.configure(bg = "#d4d0c7")

        self.__file_name_entry = None
        self.__file_button = None

        self.__fixed_length_var = tk.BooleanVar(value = False)
        self.__fixed_length_checkbox = None

        self.__omit_first_column_var = tk.BooleanVar(value = False)
        self.__omit_column_checkbox = None

        self.__total_records_label = None
        self.__strong_rules_label = None

        self.__min_sup_entry = None
        self.__min_conf_entry = None

        self.__run_button = None
        self.__exit_button = None
        self.__show_plots_button = None
        self.__save_to_json_button = None

        self.__rule_display = None

        self.__min_sup_text = tk.StringVar(value = "50")
        self.__min_conf_text = tk.StringVar(value = "0.5")

        self.__supported_datafiles = {"csv", "arff"}

        self.__rule_data = []

    def run(self):
        self.__init_widgets()
        self.__root.mainloop()

    def __init_widgets(self):
        # File name widgets
        self.__file_name_entry = tk.Entry(self.__root, disabledforeground = "black", state = tk.DISABLED)
        self.__file_name_entry.grid(row = 0, column = 0, padx = 10, pady = 10, sticky = "ew")

        self.__file_button = tk.Button(self.__root, bg = "#bfbab0", width = 20, text = "Choose File", command = self.__choose_file)
        self.__file_button.grid(row = 1, column = 0, padx = 10, pady = 5, sticky = "ew")

        # Checkbox widgets
        self.__fixed_length_var = tk.BooleanVar()
        self.__fixed_length_checkbox = tk.Checkbutton(
            self.__root,
            text = "Fixed length transactions",
            variable = self.__fixed_length_var,
            state = tk.DISABLED,
            bg = "#d4d0c7"
        )
        self.__fixed_length_checkbox.grid(row = 0, column = 1, padx = 10, pady = 10, sticky = "w")

        self.omit_column_var = tk.BooleanVar()
        self.__omit_column_checkbox = tk.Checkbutton(
            self.__root,
            text = "Omit first column",
            variable = self.__omit_first_column_var,
            state = tk.DISABLED,
            bg = "#d4d0c7"
        )
        self.__omit_column_checkbox.grid(row = 1, column = 1, padx = 10, pady = 5, sticky = "w")

        # Data info labels
        self.__total_records_label = tk.Label(self.__root, text = "", bg = "#d4d0c7")
        self.__total_records_label.grid(row = 2, column = 0, padx = 10, pady = 5, sticky = "w")
        self.__strong_rules_label = tk.Label(self.__root, text = "", bg = "#d4d0c7")
        self.__strong_rules_label.grid(row = 3, column = 0, padx = 10, pady = 5, sticky = "w")

        # Algorithm parameters widgets
        min_sup_label = tk.Label(self.__root, text = "Minimal support:", bg = "#d4d0c7")
        min_sup_label.grid(row = 0, column = 2, padx = 10, pady = 5, sticky = "w")
        self.__min_sup_entry = tk.Entry(self.__root, textvariable = self.__min_sup_text)
        self.__min_sup_entry.grid(row = 1, column = 2, padx = 10, pady = 10, sticky = "ew")

        min_conf_label = tk.Label(self.__root, text = "Minimal confidence:", bg = "#d4d0c7")
        min_conf_label.grid(row = 2, column = 2, padx = 10, pady = 5, sticky = "w")
        self.__min_conf_entry = tk.Entry(self.__root, textvariable = self.__min_conf_text)
        self.__min_conf_entry.grid(row = 3, column = 2, padx = 10, pady = 5, sticky = "ew")

        # Buttons
        self.__run_button = tk.Button(self.__root, text = "Run", bg = "#d6d6d4", width = 10, command = self.__run_button_click, state = tk.DISABLED)
        self.__run_button.grid(row = 0, column = 3, rowspan = 2, padx = 10, pady = 10, sticky = "ns")

        self.__exit_button = tk.Button(self.__root, text = "Exit", bg = "#d41c2b", width = 10, command = self.__exit)
        self.__exit_button.grid(row = 2, column = 3, rowspan = 2, padx = 10, pady = 5, sticky = "ns")

        self.__save_to_json_button = tk.Button(self.__root, text = "Save to json", bg = "#bfbab0", width = 10, command = self.__save_to_json_button_click, state = tk.DISABLED)
        self.__save_to_json_button.grid(row = 2, column = 1, rowspan = 1, padx = 10, pady = 5, sticky = "ns")

        self.__show_plots_button = tk.Button(self.__root, text = "Show plots", bg = "#bfbab0", width = 10, command = self.__show_plots_button_click, state = tk.DISABLED)
        self.__show_plots_button.grid(row = 3, column = 1, rowspan = 1, padx = 10, pady = 5, sticky = "ns")

        self.__rule_display = tk.Listbox(self.__root)
        self.__rule_display.grid(row = 4, column = 0, columnspan = 4, padx = 10, pady = 10, sticky = "nsew")

        self.__root.grid_rowconfigure(4, weight = 1)
        self.__root.grid_columnconfigure(0, weight = 1)

    def __run_button_click(self):
        self.__rule_display.delete(0, tk.END)
        self.__total_records_label.config(text = "")
        self.__strong_rules_label.config(text = "")
        try:
            min_sup = float(self.__min_sup_text.get())
            min_conf = float(self.__min_conf_text.get())
            fixed_length = self.__fixed_length_var.get()
            omit_first_column = self.__omit_first_column_var.get()
            self.__adp.set_parameters({"min_sup": min_sup, "min_conf": min_conf})
            self.__rule_data, total_records = self.__adp.process_data(self.__filepath, fixed_length = fixed_length, ommit_first_column = omit_first_column)

            for rule in self.__rule_data:
                formatted_rule = self.__format_rule(rule)
                self.__rule_display.insert(tk.END, formatted_rule)
                rule["rule"] = f"{rule['rule'][0]} --> {rule['rule'][1]}"

            self.__save_to_json_button.config(state = tk.NORMAL, bg = "#bfbab0")
            self.__show_plots_button.config(state = tk.NORMAL, bg = "#bfbab0")
            label = f"{total_records} total records."
            self.__total_records_label.config(text = label)
            label = f"{len(self.__rule_data)} strong association rules found."
            self.__strong_rules_label.config(text = label)

        except ValueError:
            print(f"[ERROR] Parameters are incorrect! Please provide floating point values.")
            return
        
    def __show_plots_button_click(self):
        self.__adp.show_plots()

    def __save_to_json_button_click(self):
        file_name = filedialog.asksaveasfilename(
            defaultextension = ".json",
            filetypes = [("JSON files", "*.json"), ("All files", "*.*")]
        )

        if file_name:
            with open(file_name, "w") as file:
                json.dump(self.__rule_data, file, indent = 4)
            print(f"Strong association rules saved to file {file_name}")

    def __choose_file(self):
        self.__filepath = filedialog.askopenfilename()
        if self.__filepath == None or self.__filepath == "":
            return
        short_file_name = os.path.basename(self.__filepath)
        ext = short_file_name.split(".")[-1]
        if ext not in self.__supported_datafiles:
            self.__filepath = None
            self.__run_button.config(state = tk.DISABLED, bg = "#d6d6d4")
            self.__save_to_json_button.config(state = tk.DISABLED, bg = "#d6d6d4")
            self.__show_plots_button_click.config(state = tk.DISABLED, bg = "#d6d6d4")
            self.__fixed_length_checkbox.config(state = tk.DISABLED)
            self.__omit_column_checkbox.config(state = tk.DISABLED)
            self.__set_chosen_filename("")
            self.__total_records_label.config(text = "")
            self.__strong_rules_label.config(text = "")
            print(f"'{ext}' file format not supported!")        
            return
        
        if ext == "csv":
            self.__fixed_length_checkbox.config(state = tk.NORMAL)
            self.__omit_column_checkbox.config(state = tk.NORMAL)
        else:
            self.__fixed_length_checkbox.config(state = tk.DISABLED)
            self.__omit_column_checkbox.config(state = tk.DISABLED)

        self.__run_button.config(state = tk.NORMAL, bg = "#54a820")
        self.__set_chosen_filename(short_file_name)

        print(f"Selected file: {short_file_name}")        

    def __set_chosen_filename(self, filename):
        self.__file_name_entry.config(state = tk.NORMAL)
        self.__file_name_entry.delete(0, tk.END)
        self.__file_name_entry.insert(0, filename)
        self.__file_name_entry.config(state = tk.DISABLED)

    def __exit(self):
        self.__root.destroy()

    def __format_rule(self, rule_data):
        return f"Rule: {rule_data['rule']}, " + \
               f"Support: {rule_data['sup']:.4g}, " + \
               f"rSUP: {rule_data['rsup']:.4g}, " + \
               f"Confidence: {rule_data['conf']:.4g}, " + \
               f"Lift: {rule_data['lift']:.4g}, " + \
               f"Cosine: {rule_data['cosine']:.4g}, " + \
               f"Jaccard: {rule_data['jaccard']:.4g}, " + \
               f"Certainty Factor: {rule_data['cf']:.4g}"
    