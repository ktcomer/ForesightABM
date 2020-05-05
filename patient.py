import random as RD
from itertools import count
import matplotlib.pyplot as plt
import numpy
import math
import csv

# Input and Output File Paths
InputFile = "C:/Users/ktcomer/Documents/MSIM/HealthSimInputSheet.csv"
OutputFile = "C:/Users/ktcomer/Documents/MSIM/HealthSimOutputSheet.csv"

# Random seed generator
RD.seed()

# Number of Patients in the run
NumPatients = 100000
USPopulation = 330000000

# Chances of having diabetes, based on age and ethnicity (CDC Report, 2017)
BaseRate = 0.000066
WhiteOddsRate = 0.9351
BlackOddsRate = 1.3621
HispOddsRate = 1.0272
OtherOddsRate = 0.95
LessHSOddsRate = 1.6765
HSOddsRate = 1.166
MoreHSOddsRate = 0.7785

# Parameters for the Mortality Function (Lenart 2012)
gompertz_alpha = 0.0000015
gompertz_beta = 0.12

# Policy Parameters (will be input to the simulation)
# MedicareAge = 65
medicarePercentage = 0.25
# MedicaidIncomeElig = 1.38
FedPovLevel = 12060

# Administration Cost for Private Insurers
AdminCost = 0.15

# Inertial Force of patients switching to a new private insurance company
InertialPriceForce = 1.5

# Difference in cost factor for individuals with diabetes (ADA Publication, 2017)
DiabetesCostFactor = 4.0
diabetes_risk = 0.109
DiabetesQualityFactor = 0.5

# Cost of care for individuals, without diabetes (CDC, 2014)
YoungestCostMean = 2877
YoungCostMean = 3727
MiddleCostMean = 7837
OldCostMean = 13029
OldestCostMean = 25251

# Pareto parameter for determining cost of care
Pareto_alpha = 2.806

# Increased chance of death from diabetes (ADA Publication, 2017)
DiabetesMortalityRisk = 1.6

# Cost of care for individuals, with and without diabetes (ADA Publication, 2017)
CareCostMean = 4185
DiabetesCostMean = 9600
diabetes_risk = 0.109

# Maximum percent of income spent on healthcare premium
MaxPercentIns = 0.35#0.1

# Cumulative Prospect Theory parameters, for the purposes of estimating costs
alpha = 0.88
lmda = 2.25
gamma = 0.61
delta = 0.69

# Rates of diagnosis, based on age
AgeDiagnosed = 1.084

# Chance of getting diagnosed with insurance, dependent on race
WhiteInsDiagnosed = 1.462
BlackInsDiagnosed = 1.168
AsianInsDiagnosed = 1.32
HispInsDiagnosed = 0.98
MexInsDiagnosed = 0.777

# Chance of getting control, dependent on attributes
InsControl = 3.96
BlackControl = 1.3
HispControl = 0.43
FemaleControl = 0.53
YoungControl = 0.34
OldControl = 0.85

riskAversion = 1.15 #hedge risk of unexpected healthcare costs in future

class Agent(object):
    id_generator = count()
    """
    
    """
    def __init__(self):
        self.ident = Agent.id_generator.next()

    def __hash__(self):
        return self.ident
        
class Patient(Agent):
    
    def __init__(self, ethnicity, policySettings, seed=None):
        self.income = 0
        self.ethnicity = ethnicity
        self.age = 0
        self.MortalityHazardRatio = 1.0
        self.deceased = False
        self.diabetes = False
        self.diagnosed = False
        self.controlled = False
        self.insured = False
        self.Medicare = False
        self.Medicaid = False
        self.PrivateInsured = False
        self.QALY = 0
        self.plan = None  
        self.education = ""
        self.IPR = 0.0
        self.care_cost = 0
        self.history = []
        self.expected_expenses = 0
        self.policySettings = policySettings
        
    def grow_older(self):
        # Incorporated increased hazard ratios for diabetes based on Wang & Liu (2016)
        if self.diabetes == True and self.controlled == False:
            self.QALY = self.QALY - DiabetesQualityFactor
            if self.age < 20:
                self.MortalityHazardRatio = 3.03
            elif self.age < 30:
                self.MortalityHazardRatio = 2.98
            elif self.age < 40:
                self.MortalityHazardRatio = 2.81
            elif self.age < 50:
                self.MortalityHazardRatio = 2.26
            elif self.age < 60:
                self.MortalityHazardRatio = 1.82
            elif self.age < 70:
                self.MortalityHazardRatio = 1.64
            elif self.age < 80:
                self.MortalityHazardRatio = 1.53
            else: self.MortalityHazardRatio = 1.04
        chance_of_death = gompertz_alpha * math.exp(gompertz_beta * self.age) * self.MortalityHazardRatio
        if RD.random() <= chance_of_death:
            self.deceased = True
            if self.diabetes == True:
                if self.age < 83: self.YLL = 83 - self.age
        else: 
            self.age = self.age + 1
            self.QALY += 1.0
        
    def contract_diabetes(self):
        diabetes_chance = BaseRate * self.age
        if self.ethnicity == "Non-Hispanic White":
            diabetes_chance = diabetes_chance * WhiteOddsRate
        elif self.ethnicity == "Non-Hispanic Black":
            diabetes_chance = diabetes_chance * BlackOddsRate
        elif self.ethnicity == "Non-Hispanic Asian":
            diabetes_chance = diabetes_chance * OtherOddsRate
        elif self.ethnicity == "Other Hispanic" or self.ethnicity == "Mexican American":
            diabetes_chance= diabetes_chance * HispOddsRate
        if self.education == "Less Than High School Diploma":
            diabetes_chance = diabetes_chance * LessHSOddsRate
        elif self.education == "Some College or AA degree":
            diabetes_chance = diabetes_chance * MoreHSOddsRate   
        else: diabetes_chance = diabetes_chance * HSOddsRate
        if RD.random() <= diabetes_chance:
            self.diabetes = True
            self.diagnose_diabetes()
            if self.diagnosed == True:
                self.control_diabetes()
    
    def diagnose_diabetes(self):
        # Given that an individual has diabetes, the probability it can be diagnosed
        diagnosis_chance = math.pow(1.084, self.age) / 100.0
        if self.insured:
            if self.ethnicity == "Non-Hispanic White":
                diagnosis_chance = diagnosis_chance * WhiteInsDiagnosed
            elif self.ethnicity == "Non-Hispanic Black":
                diagnosis_chance = diagnosis_chance * BlackInsDiagnosed
            elif self.ethnicity == "Non-Hispanic Asian":
                diagnosis_chance = diagnosis_chance * AsianInsDiagnosed
            if self.ethnicity == "Other Hispanic":
                diagnosis_chance = diagnosis_chance * HispInsDiagnosed
            if self.ethnicity == "Mexican American":
                diagnosis_chance = diagnosis_chance * MexInsDiagnosed
        if RD.random() <= diagnosis_chance:
            self.diagnosed = True
            
    def control_diabetes(self):
        # Given that an individual has diabetes, the probability they can control it with medication
        control_chance = 0.252873
        if self.insured:
            control_chance = control_chance * InsControl
        if self.ethnicity == "Non-Hispanic Black":
            control_chance = control_chance * BlackControl
        if self.ethnicity == "Mexican American" or self.ethnicity == "Other Hispanic":
            control_chance = control_chance * HispControl
        if self.gender == "Female":
            control_chance = control_chance * FemaleControl
        if self.age <= 44:
            control_chance = control_chance * YoungControl
        if self.age >= 65:
            control_chance = control_chance * OldControl
        if RD.random() <= control_chance:
            self.controlled = True
    
    def add_plan(self, NewPlan):
        # The patient adds the plan provided by Payer
        # This will only occur if patient currently has no plan
        if self.plan is None:
            self.plan = NewPlan
            NewPlan.subscribers.append(self)
    
    def drop_plan(self):
        # The patient wil drop the plan offered by Payer
        # This will only occur if patient currently has a plan
        if self.plan is not None:
            self.plan.subscribers.remove(self)
            self.plan = None
    
    def estimate_expenses(self):
        # W is the perceived probability of a catastrophic accident occurring
        # V1 is the perceived loss for regular years
        # V2 is a catastrophic loss that the patient may incur
        care_estimate = max(self.history)
        if self.diagnosed == False:
            diabetes_estimate = care_estimate * DiabetesCostFactor
        else: diabetes_estimate = self.history[-1]
        V1 = lmda * pow(care_estimate, alpha)
        V2 = lmda * pow(diabetes_estimate, alpha)
        W = pow(diabetes_risk, delta)/pow(pow(diabetes_risk, delta) + pow(1.0 - diabetes_risk, delta), (1.0/delta))
        self.expected_expenses = (1.0 - W) * V1 + W * V2
    
    def choose_plan(self, newPlan, Medicare, Medicaid):
        privateCost = newPlan.premium + newPlan.deductible
        # If they are eligible for Medicaid, they will enroll into Medicaid.
        if self.income <= (self.policySettings.MedicaidIncomeElig * FedPovLevel):
            self.Medicare = False
            self.PrivateInsured = False
            self.Medicaid = True
            self.drop_plan()
            self.add_plan(Medicaid)
        # If they are eligible for Medicare, they will enroll into Medicare.
        elif self.age >= self.policySettings.MedicareAge:
            self.Medicare = True
            self.PrivateInsured = False
            self.Medicaid = False
            self.drop_plan()
            self.add_plan(Medicare)
        # If a patient's expected expenses are greater than the current best premium on the market, they will buy insurance. Otherwise, they will not.
        elif self.expected_expenses*riskAversion >= privateCost and (privateCost/self.income) <= MaxPercentIns: ###review this logic
            self.PrivateInsured = True
            self.Medicaid = False
            self.Medicare = False
            if self.plan == None:
                self.add_plan(newPlan)
            elif self.plan == Medicare or self.plan == Medicaid:
                self.drop_plan()
                self.add_plan(newPlan)
            elif privateCost < (self.plan.premium / InertialPriceForce):
                self.drop_plan()
                self.add_plan(newPlan)
            #else keep your existing private plan
        else: 
            self.PrivateInsured = False
            self.drop_plan()
        
        #Check if they are insured
        if self.PrivateInsured or self.Medicare or self.Medicaid:
            self.insured = True
        else: 
            self.Medicare = False
            self.PrivateInsured = False
            self.Medicaid = False
            self.insured = False
            self.drop_plan()
            
        
    def add_expense(self):
        # The patient has incurred a medical expense and must subtract it from their wealth
        if self.age <= 18:
            CareCostMean = YoungestCostMean
        elif self.age <= 44:
            CareCostMean = YoungCostMean
        elif self.age <= 64:
            CareCostMean = MiddleCostMean
        elif self.age <= 84:
            CareCostMean = OldCostMean
        else:
            CareCostMean = OldestCostMean
        if self.diabetes == True:
            CareCostMean = CareCostMean * DiabetesCostFactor
        self.care_cost = numpy.random.pareto(Pareto_alpha) * CareCostMean
        self.history.append(self.care_cost)
        if self.plan != None:
            plan_cost = max([0,self.care_cost - self.plan.deductible])
            cash_cost = min([self.plan.deductible, self.care_cost])
            self.plan.add_cost(plan_cost)
        else:
            cash_cost = self.care_cost
