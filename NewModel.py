import copy
import random as RD
import math
import csv

from agents.patient import Patient
from agents.payer import Payer

def runModel(policySettings, NumPatients=100000):

    # Input and Output File Paths
    InputFile = "./HealthSimInputSheet.csv"

    # Random seed generator
    RD.seed()

    USPopulation = 330000000
    NumPrivPayers = 10

    # Parameters for the Mortality Function (Lenart 2012)
    gompertz_alpha = 0.0000015
    gompertz_beta = 0.12

    # Policy Parameters (will be input to the simulation)
    #MedicareAge = 65
    medicarePercentage = 0.25
    #MedicaidIncomeElig = 1.38
    FedPovLevel = 12060

    # Administration Cost for Private Insurers
    AdminCost = 0.15

    # Pareto parameter for determining cost of care
    Pareto_alpha = 2.806

    ListOfPatients = []
    ListOfDeceasedPatients = []
    ListOfPayers = []
    InputData = []

    #privatePremium = 0
    medicarePremium = 0
    
    minPremium = 1000
    
    # Education Override Input
    #EducationOverride = False
    #EducationOverrideQual = 0.5

    Run = 1
    runLength = 10
    
    maxRaise = 0.2
    deductibleChange = 200
    
    Bankrupt_list = []
    

    def create_new_patient(policySettings):
        randomParameters = RD.random()
        for r in range(len(InputData)):
            if randomParameters <= InputData[r][0]:
                newPatient = Patient(InputData[r][1], policySettings)
                newPatient.age = 0
                diabetes_status_c = InputData[r][2]
                if diabetes_status_c != "Undiagnosed, (-) Diabetes":
                    newPatient.diabetes = True
                newPatient.QALY = newPatient.age
                newPatient.gender = InputData[r][4]
                Educ_c = InputData[r][5]
                if Educ_c == "Educ: High School Grad/GED or Equivalent" or "Educ: High school graduate or GED or equivalent":
                    newPatient.education = "High School Diploma or Equivalent"
                elif Educ_c == "Educ: Some College or AA degree":
                    newPatient.education = "Some College or AA degree"
                else: newPatient.education = "Less than High School Diploma"
                IPR_c = InputData[r][6]
                if IPR_c == "INDFMPIR<0.25":
                    newPatient.IPR = RD.uniform(0, 0.25)
                elif IPR_c == "0.25<=INDFMPIR<0.5":
                    newPatient.IPR = RD.uniform(0.25, 0.5)
                elif IPR_c == "0.5<=INDFMPIR<0.75":
                    newPatient.IPR = RD.uniform(0.5, 0.75)
                elif IPR_c == "0.75<=INDFMPIR<1":
                    newPatient.IPR = RD.uniform(0.75, 1)
                elif IPR_c == "1<=INDFMPIR<1.5":
                    newPatient.IPR = RD.uniform(1, 1.5)
                elif IPR_c == "1.5<=INDFMPIR<2":
                    newPatient.IPR = RD.uniform(1.5, 2)
                elif IPR_c == "2<=INDFMPIR<3":
                    newPatient.IPR = RD.uniform(2, 3)
                elif IPR_c == "3<=INDFMPIR<2":
                    newPatient.IPR = RD.uniform(3, 4)
                elif IPR_c == "4<=INDFMPIR":
                    newPatient.IPR = RD.uniform(4, 5)
                if policySettings.EducationOverride:
                    if policySettings.EducationOverrideQual >= newPatient.IPR:
                        newPatient.education = "Some College or AA degree"
                HHincome3_c = InputData[r][7]
                newPatient.income = RD.randint(0, 54999)
                if HHincome3_c == "($55,000 to $64,999)<=HHincome<=($75,000 to $99,999)":
                    newPatient.income = RD.randint(55000, 99999)
                elif HHincome3_c == "($100,000 and Over)<=HHincome":
                    newPatient.income = RD.randint(100000, 250000)
                if InputData[r][9] == "Covered by pvt ins":
                    newPatient.PrivateInsured = True
                    newPatient.insured = True
                    RandomPlan = RD.randint(0, len(ListOfPayers)-1) #Don't select Medicaid or Medicare
                    newPatient.add_plan(ListOfPayers[RandomPlan])
                elif InputData[r][10] == "Covered by Medicare":
                    newPatient.Medicare = True
                    newPatient.insured = True
                    newPatient.add_plan(Medicare)
                elif InputData[r][11] == "Covered by Medicaid":
                    newPatient.Medicaid = True
                    newPatient.insured = True
                    newPatient.add_plan(Medicaid)
                break
        return newPatient   

    def create_patient(policySettings):
        randomParameters = RD.random()
        for r in range(len(InputData)):
            if randomParameters <= InputData[r][0]:
                newPatient = Patient(InputData[r][1], policySettings)
                diabetes_status_c = InputData[r][2]
                if diabetes_status_c != "Undiagnosed, (-) Diabetes":
                    newPatient.diabetes = True
                    if diabetes_status_c != "Undiagnosed,(+)Diabetes":
                        newPatient.diagnosed = True
                        if diabetes_status_c != "Diagnosed, Uncontrolled Diabetes":
                            newPatient.controlled = True
                age65_c = InputData[r][3]
                if age65_c == "0<=age<20yo":
                    newPatient.age = RD.randint(0, 19)
                elif age65_c == "20<age<65yo":
                    newPatient.age = RD.randint(20, 64)
                elif age65_c == "65<=age":
                    newPatient.age = RD.randint(65, 80)
                newPatient.QALY = newPatient.age
                newPatient.gender = InputData[r][4]
                Educ_c = InputData[r][5]
                if Educ_c == "Educ: High School Grad/GED or Equivalent" or "Educ: High school graduate or GED or equivalent":
                    newPatient.education = "High School Diploma or Equivalent"
                elif Educ_c == "Educ: Some College or AA degree":
                    newPatient.education = "Some College or AA degree"
                else: newPatient.education = "Less than High School Diploma"
                IPR_c = InputData[r][6]
                if IPR_c == "INDFMPIR<0.25":
                    newPatient.IPR = RD.uniform(0, 0.25)
                elif IPR_c == "0.25<=INDFMPIR<0.5":
                    newPatient.IPR = RD.uniform(0.25, 0.5)
                elif IPR_c == "0.5<=INDFMPIR<0.75":
                    newPatient.IPR = RD.uniform(0.5, 0.75)
                elif IPR_c == "0.75<=INDFMPIR<1":
                    newPatient.IPR = RD.uniform(0.75, 1)
                elif IPR_c == "1<=INDFMPIR<1.5":
                    newPatient.IPR = RD.uniform(1, 1.5)
                elif IPR_c == "1.5<=INDFMPIR<2":
                    newPatient.IPR = RD.uniform(1.5, 2)
                elif IPR_c == "2<=INDFMPIR<3":
                    newPatient.IPR = RD.uniform(2, 3)
                elif IPR_c == "3<=INDFMPIR<2":
                    newPatient.IPR = RD.uniform(3, 4)
                elif IPR_c == "4<=INDFMPIR":
                    newPatient.IPR = RD.uniform(4, 5)
                if policySettings.EducationOverride:
                    if policySettings.EducationOverrideQual >= newPatient.IPR:
                        newPatient.education = "Some College or AA degree"
                HHincome3_c = InputData[r][7]
                newPatient.income = RD.randint(0, 54999)
                if HHincome3_c == "($55,000 to $64,999)<=HHincome<=($75,000 to $99,999)":
                    newPatient.income = RD.randint(55000, 99999)
                elif HHincome3_c == "($100,000 and Over)<=HHincome":
                    newPatient.income = RD.randint(100000, 250000)
                if InputData[r][9] == "Covered by pvt ins":
                    newPatient.PrivateInsured = True
                    newPatient.insured = True
                    RandomPlan = RD.randint(0, NumPrivPayers-1)
                    newPatient.add_plan(ListOfPayers[RandomPlan])
                elif InputData[r][10] == "Covered by Medicare":
                    newPatient.Medicare = True
                    newPatient.insured = True
                    newPatient.add_plan(Medicare)
                elif InputData[r][11] == "Covered by Medicaid":
                    newPatient.Medicaid = True
                    newPatient.insured = True
                    newPatient.add_plan(Medicaid)
                break              	
        return newPatient

    def findBestPlan(List):
        PremiumPrice = math.inf
        BestPlan = None
        for p in range(len(List)):
            if List[p].premium < PremiumPrice:
                BestPlan = List[p]
                PremiumPrice = BestPlan.premium
        return BestPlan
        

    with open(InputFile, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        counter = 0.0
        for row in reader:
            counter += float(row['propOfTotalPop'])
            ethnicity = row['ethnicity_c']
            diabetes_status = row['diabetes_status_c']
            age_c = row['age65_c']
            gender = row['gender_c']
            education = row['Educ_c']
            IPR_c = row['IPR_c']
            HHIncome3 = row['HHincome3_c']
            healthIns = row['healthInsStatus_c']
            PrivateIns = row['typeOfIns1_c']
            Medicare = row['typeOfIns2_c']
            Medicaid = row['typeOfIns4_c']
            InputData.append([counter, ethnicity, diabetes_status, age_c, gender, education, IPR_c, HHIncome3, healthIns, PrivateIns, Medicare, Medicaid])

    # Initialize Payers
    starting_premium = 3000
    for b in range(NumPrivPayers):
        starting_capital = starting_premium * NumPatients
        newPayer = Payer(starting_premium, starting_capital) #initial premium of $3000
        newPayer.isPrivate = True
        ListOfPayers.append(newPayer)
    Medicare = Payer(starting_premium, starting_capital)
    Medicare.isMedicare = True
    ListOfPayers.append(Medicare)
    Medicaid = Payer(starting_premium, starting_capital)
    Medicaid.isMedicaid = True
    ListOfPayers.append(Medicaid)

    # Initialize Patients
    for a in range(NumPatients):
        newPatient = create_patient(policySettings)
        newPatient.add_expense()
        newPatient.estimate_expenses()
        ListOfPatients.append(newPatient)
        Progress = 100 * a / NumPatients
        if Progress % 10 == 0:
            print("Patient Initialization", Progress, "% Complete") 
            
    # Finish initializing payers
    BestPlan = findBestPlan(ListOfPayers[:-2])
    for g in range(len(ListOfPayers)):
    	ListOfPayers[g].subscribers_list.append(len(ListOfPayers[g].subscribers))
    	ListOfPayers[g].update_capital()
    	ListOfPayers[g].update_premium_deductible(BestPlan, medicarePercentage, AdminCost, maxRaise, deductibleChange)
        
    # Simulation start t = 1,2,3...runLength
    for t in (range(1,runLength+1)):
        BestPlan = findBestPlan(ListOfPayers[:-2])
        
        for f in range(len(ListOfPayers)):
            ListOfPayers[f].newYear()
        
        for d in range(len(ListOfPatients)):
            if ListOfPatients[d].deceased == True:
                if ListOfPatients[d].plan != None:
                    ListOfPatients[d].plan.subscribers.remove(ListOfPatients[d])
                ListOfDeceasedPatients.append(copy.copy(ListOfPatients[d]))
                ListOfPatients[d] = create_new_patient(policySettings)
                CurrentPatient = ListOfPatients[d]
        
        for c in range(len(ListOfPatients)):
            CurrentPatient = ListOfPatients[c]
            
            CurrentPatient.choose_plan(BestPlan, Medicare, Medicaid)
            if CurrentPatient.diabetes == False:
                CurrentPatient.contract_diabetes()

            CurrentPatient.grow_older()
            CurrentPatient.add_expense()
            CurrentPatient.estimate_expenses()
            
        
        for f in range(len(ListOfPayers)):
            ListOfPayers[f].subscribers_list.append(len(ListOfPayers[f].subscribers))
            ListOfPayers[f].update_capital()
            #change minPremium to undercut best plan
            ListOfPayers[f].update_premium_deductible(BestPlan, medicarePercentage, AdminCost, maxRaise, deductibleChange) 
        
        privateCosts = 0
        privateN = 0
        for f in range(len(ListOfPayers)):
            if ListOfPayers[f].isPrivate:
                privateCosts += ListOfPayers[f].assess_costs()
                privateN += len(ListOfPayers[f].subscribers)
        
        privateCount = privateN
        medicareCount = len(Medicare.subscribers)
        medicaidCount = len(Medicaid.subscribers)
        uninsuredCount = NumPatients - (privateCount+medicareCount+medicaidCount)
        if privateCount > 0:
            privatePremium = privateCosts * (AdminCost + 1.0) / privateCount
        else:
            privatePremium = "None"
        medicareFunds = Medicare.assess_govtCosts(medicarePercentage)
        medicaidFunds = Medicaid.assess_govtCosts(medicarePercentage)
        medicarePremium = Medicare.premium
        medicaidPremium = Medicaid.premium
        
        NewListOfPayers = ListOfPayers.copy()
        for f in range(len(ListOfPayers)):
            if ListOfPayers[f].check_bankruptcy():
                bpayer = ListOfPayers[f]
                Bankrupt_list.append(bpayer)
                NewListOfPayers.remove(bpayer)
            print(ListOfPayers[f].capital)
        ListOfPayers = NewListOfPayers.copy()
        
        if len(ListOfPayers) <= 2:
            print("All Private Payers have gone bankrupt!")
            break
                

    return {
        'runSummary': {
            "Number on Private Insurance:": [privateCount, privateCount * USPopulation / NumPatients],
            "Number on Medicare:": [medicareCount, medicareCount * USPopulation / NumPatients],
            "Number on Medicaid:": [medicaidCount, medicaidCount * USPopulation / NumPatients],
            "Number of Uninsured:": [uninsuredCount, uninsuredCount * USPopulation / NumPatients],
            "Private Premium:": [privatePremium],
            "Medicare Premium:": [medicarePremium],
            "Medicare Funds:": [medicareFunds, medicareFunds * USPopulation / NumPatients],
            "Medicaid Funds:": [medicaidFunds, medicaidFunds * USPopulation / NumPatients]
        },
        'patients': ListOfDeceasedPatients + ListOfPatients
    }
