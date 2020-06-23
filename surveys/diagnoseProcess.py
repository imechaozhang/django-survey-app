import pandas as pd
from .models import Question


class DiagnoseProcess():
    filename = 'surveys/static/files/wm.csv'
    weight_matrix = pd.read_csv(filename, index_col=0)

    def __init__(self):
        self.wm = self.weight_matrix.copy(deep=True)
        self.asked = []
        self.positive = []
        self.age = 'Adult'
        self.gender = 'Male'

    def reduce(self):
        self.wm = self.weight_matrix.copy(deep=True)
        for symptom in self.asked:
            if symptom in self.positive:
                self.wm = self.wm[self.wm[symptom] > 0]
            else:
                self.wm = self.wm[self.wm[symptom] <= 0]
        for symptom in self.asked:
            if symptom in self.wm.columns:
                self.wm.drop(columns=symptom, inplace=True)
        for symptom in self.weight_matrix.columns[28:]:
            if symptom in self.wm.columns:
                self.wm.drop(columns=symptom, inplace=True)

    def time_to_conclude(self):
        return len(self.wm) <= 1

    def next_symptom(self):
        next_symp = self.wm.columns[0]
        max_priority = len(self.weight_matrix)
        for symp in self.wm.columns:
            value_counts = {'0': 0, '1': 0}
            for dis in self.wm[symp].values:
                if dis > 0:
                    value_counts['1'] += 1
                else:
                    value_counts['0'] += 1
            priority = abs(value_counts['1'] - value_counts['0'])
            if priority < max_priority:
                max_priority = priority
                next_symp = symp
        return next_symp

    def check(self):
        symptom_list = pd.Series(index=self.weight_matrix.columns, data=[0] * len(self.weight_matrix.columns))
        for symp in self.positive:
            symptom_list[symp] = 1

        diagnosis_result = self.weight_matrix.dot(symptom_list)
        diagnosis_result.sort_values(ascending=False, inplace=True)
        return diagnosis_result
