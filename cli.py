import json
import glob
import argparse
from model.NewModel import runModel
from collections import namedtuple
import csv

OutputFile = "./HealthSimOutputSheet.csv"

parser = argparse.ArgumentParser(description='Select policy file')
parser.add_argument('-p', type=str, default='default', help='name of a a policy file')
parser.add_argument('-n', type=int, default=100000, help='number of patients')

args = parser.parse_args()

NumPatients = args.n

policyName = args.p
matchingPolicies = glob.glob(f"./policies/{policyName}*")

if len(matchingPolicies) == 0:
    raise SystemExit(f"No matching policy named {policyName}")
elif len(matchingPolicies) > 1:
    raise SystemExit(f"Multiple matching policies for {policyName}: {matchingPolicies}")

policyFile = matchingPolicies[0]

with open(policyFile, 'r') as stream:
    # magic to turn json into an object instead of a dict
    # https://stackoverflow.com/a/15882054
    policySettings = json.load(stream, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))


results = runModel(policySettings, NumPatients)

with open(OutputFile, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    keys = ["Number on Private Insurance:", "Number on Medicare:",
            "Number on Medicaid:", "Number of Uninsured:",
            "Private Premium:", "Medicare Premium:",
            "Medicare Funds:", "Medicaid Funds:"]

    for key in keys:
        row = [key] + results['runSummary'][key]
        writer.writerow(row)

    patients = results['patients']
    writer.writerow(["Patient ID", "Age", "Ethnicity", "Gender", "Education", "Income", "Income Bracket", "QALY", "Diabetes", "Diagnosed", "Controlled", "Deceased"])
    for m in range(len(patients)):
        writer.writerow([m, patients[m].age, patients[m].ethnicity, patients[m].gender, patients[m].education, patients[m].income, patients[m].IPR, patients[m].QALY, patients[m].diabetes, patients[m].diagnosed, patients[m].controlled, patients[m].deceased])
