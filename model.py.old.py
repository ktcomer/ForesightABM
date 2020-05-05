import random as RD

import matplotlib.pyplot as plt
import numpy
import math
import csv

from agents.patient import Patient
from agents.payer import Payer

# Random seed generator
RD.seed()
RunLength = 20

NumPatients = 100000
NumPayers = 10
InertiaFactor = 1.25
AdminCostFactor = 1.15
SalaryBuffer = 1
PremiumBuffer = 0.2

alpha = 0.88
lmda = 2.25
gamma = 0.61
delta = 0.69

IndividualMandate = False
CoverageMandate = False
IndividualSubsidies = False
RiskAdjustment = False
Reinsurance = False
RiskCorridors = False

IMAmount = 472.01
IMPercent = 2.5
FPL = 8050
AttachmentPoint = 61123.22
ReinsurancePerCapita = 18.34
ReinsuranceFund = 0.0
RiskCorridorFund = 0.0
SystemLoss = 0.0

Pareto_xmin = 33800
Pareto_alpha = 0.291

Income_xmin = 109045
Income_alpha = 1.7
Income_lambda = 36400

ARMA_phi = 0.949
ARMA_theta = 0.104
ARMA_error_sigma = 0.039


    
ListOfPatients = []
ListOfPayers = []

All_premiums = []

Run = 1
BudgetBuffer = 5

ReinsuranceFund = 0.0
RiskCorridorFund = 0.0
SystemLoss = 0.0
          
for z in range(10):
    Run = z + 1
    FileName = "./Run_"
    FileName += str(int(Run)) + ".csv"
    print(FileName)
    with open(FileName, 'w') as csvfile:
        writer = csv.writer(csvfile)
        print("Starting Run", Run)
        TimeStep = 1
        ListOfPatients = []
        ListOfPayers = []
        All_premiums = []
        for a in range(NumPatients):
            if RD.random() < 0.05:
                income = Income_xmin/pow(RD.random(), Income_alpha)
            else: income = numpy.random.exponential(Income_lambda)
            newPatient = Patient(income)
            newPatient.history.append(RD.lognormvariate(6.69, 2.11))
            newPatient.get_sick()
            newPatient.get_care(0)
            newPatient.estimate_expenses()
            newPatient.estimate_penalty()
            ListOfPatients.append(newPatient)
        for b in range(NumPayers):
            newPayer = Payer(RD.normalvariate(1000, 200)) 
            ListOfPayers.append(newPayer)
            newPayer.premiums_list.append(newPayer.premium)
            All_premiums.append(newPayer.premium)
        
        # add Medicare
        newPayer = Payer(RD.normalvariate(1000, 200)) 
        newPayer.isMedicare = True
        ListOfPayers.append(newPayer)
        newPayer.premiums_list.append(newPayer.premium)
        All_premiums.append(newPayer.premium)
        
        # Have patients choose plans
        for c in range(len(ListOfPatients)):
            CurrentPatient = ListOfPatients[c]
            CurrentPatient.estimate_expenses()
            CurrentPayer = ListOfPayers[RD.randint(0, NumPayers-1)]
            if CurrentPatient.plan == None:
                if CurrentPayer.underwrite(CurrentPatient):
                    CurrentPatient.add_plan(CurrentPayer)
                else: CurrentPatient.rejected = True
        for d in range(NumPayers):
            ListOfPayers[d].subscribers_list.append(len(ListOfPayers[d].subscribers))
            
        t=0
        NumRejected = 0
        NumCheap = 0
        NumDumped = 0
        NumUninsured = 0
        NumVolunteered = 0
        for t in range(RunLength):
            SumOfRisk = 0.0
            MeanRisk = 0.0
            #Add a new line on the ledger of each Payer, for the new time step
            for f in range(len(ListOfPayers)):
                ListOfPayers[f].ledger.append([])
                #print ListOfPayers[h].ledger[t]
                if RiskCorridors:
                    ListOfPayers[f].calculate_target()
                if RiskAdjustment:
                    ListOfPayers[f].estimate_risk()
                    SumOfRisk += ListOfPayers[f].risk_estimate
            if RiskAdjustment:
                MeanRisk = SumOfRisk/len(ListOfPayers)
                for x in range(len(ListOfPayers)):
                    ListOfPayers[x].ledger[-1].append(MeanRisk - ListOfPayers[x].risk_estimate)
            for g in range(len(ListOfPatients)):
                CurrentPatient = ListOfPatients[g]
                # Add salary to each Patient's wealth
                CurrentPatient.wealth = CurrentPatient.income + CurrentPatient.wealth
                # Each patient assess expenses that they would normally incur if they didn't have insurance
                CurrentPatient.estimate_expenses()
                # Each patient also accesses how much they paid last year, through medical care and insurance premiums
                if CurrentPatient.plan != None: 
                    PreviousExpense = CurrentPatient.expenses[-1]
                else: PreviousExpense = CurrentPatient.history[-1]
                # If the patient has no plan, they will assess the market of plans, via expected expenses
                for h in range(len(ListOfPayers)):
                    newPlan = ListOfPayers[h]
                    CurrentPatient.estimate_insurance(newPlan)
                    if (InertiaFactor * PreviousExpense >= CurrentPatient.insured_estimate):
                        if newPlan.underwrite(CurrentPatient):
                            CurrentPatient.drop_plan()
                            CurrentPatient.add_plan(newPlan)
                        else: CurrentPatient.rejected = True
                # If the patient has a plan, all rationales for being uninsured are set to False
                if CurrentPatient.plan != None:
                    CurrentPatient.rejected = False
                    CurrentPatient.cheap = False
                    CurrentPatient.dumped = False
                    CurrentPatient.volunteer = False
                    # If the currently owned plan's premium is higher than expected expenses, then the Patient wil drop their plan
                    CurrentPatient.estimate_insurance(CurrentPatient.plan)
                    if CurrentPatient.insured_estimate > InertiaFactor * (CurrentPatient.expected_expenses + CurrentPatient.penalty):
                        CurrentPatient.drop_plan()
                        CurrentPatient.volunteer = True
                        SystemLoss -= CurrentPatient.penalty
                    # If the currently owned plan's premium is higher than a certain percentage of their income, then the Patient wil drop their plan
                    if CurrentPatient.insured_estimate >= SalaryBuffer * CurrentPatient.income:
                        CurrentPatient.drop_plan()
                        CurrentPatient.cheap = True
                        SystemLoss -= CurrentPatient.penalty
                # Patients have a chance of getting sick, and needing their insurance
                CurrentPatient.get_sick()
                # If a patient's care cost is more than 10% of the plan's operating budget, the patient will be dropped; else, the patient will have their care covered
                if CurrentPatient.plan != None:
                    if CoverageMandate:
                        CurrentPatient.get_care(t)
                    else:
                        if CurrentPatient.care_cost <= (CurrentPatient.plan.lifetime_max):
                            CurrentPatient.get_care(t)
                        else:
                            CurrentPatient.drop_plan()
                            CurrentPatient.dumped = True
                else: CurrentPatient.get_care(t)
            
            # Payers reassess their costs and re-evaluate their premium prices
            for i in range(len(ListOfPayers)):
                CurrentPayer = ListOfPayers[i]
                if CurrentPayer.inMarket:
                    
                    yrCosts = CurrentPayer.assess_costs()
                    yrRevenue = CurrentPayer.assess_revenue()
                    (costForecast, revForecast) = CurrentPayer.forecast(BudgetBuffer, t)
                    
                    YearExpense = yrRevenue - yrCosts #Includes admin costs; doesn't include reinsurance
                    CurrentPayer.budget -= YearExpense
                    if RiskCorridors:
                        CurrentPayer.risk_corridor_payment(YearExpense)
                    if Reinsurance:
                        CurrentPayer.budget -= CurrentPayer.subscribers_list[-1] * ReinsurancePerCapita
                        ReinsuranceFund += CurrentPayer.subscribers_list[-1] * ReinsurancePerCapita

                    print("Plan", i+1, "has a premium of", CurrentPayer.premium, "with a coinsurance rate of", CurrentPayer.coinsurance, "and a stop-loss of", CurrentPayer.OOP_Max)
                    print("Plan", i+1, "has a subscriber base of", len(CurrentPayer.subscribers),"and a budget of",CurrentPayer.budget)
                    
                    CurrentPayer.update_premium(BudgetBuffer, costForecast, revForecast, min(All_premiums))
                    
                    CurrentPayer.premiums_list.append(CurrentPayer.premium)
                    CurrentPayer.subscribers_list.append(len(CurrentPayer.subscribers))
                    All_premiums.append(CurrentPayer.premium)
                    
                    # If a Payer is bankrupt, all patients are dropped, and payer now exits the market
                    if CurrentPayer.budget <= 0:
                        CurrentPayer.bankrupt()
                        
                writer.writerow([t, i, CurrentPayer.premium, CurrentPayer.coinsurance, CurrentPayer.subscribers_list[-1], sum(CurrentPayer.ledger[-1]), (CurrentPayer.subscribers_list[-1] * CurrentPayer.premiums_list[-1]), CurrentPayer.budget])
            
            # Count Patients
            for k in range(len(ListOfPatients)):
                CurrentPatient = ListOfPatients[k]
                if CurrentPatient.plan == None:
                    NumUninsured += 1
                if CurrentPatient.rejected == True:
                    NumRejected += 1
                elif CurrentPatient.cheap == True:
                    NumCheap += 1
                elif CurrentPatient.dumped == True:
                    NumDumped += 1
                elif CurrentPatient.volunteer == True:
                    NumVolunteered += 1
            print("Number Uninsured:", NumUninsured)
            print("Number Rejected:", NumRejected)
            print("Number Cheap:", NumCheap)
            print("Number Volunteers:", NumVolunteered)
            print("Number Dumped:", NumDumped)
            print("System Loss", SystemLoss)
            print("Reinsurance Fund", ReinsuranceFund)
            print("Risk Corridor Fund", RiskCorridorFund)
            writer.writerow([t, NumUninsured, NumRejected, NumCheap, NumVolunteered, NumDumped, SystemLoss, ReinsuranceFund, RiskCorridorFund])
            NumUninsured = 0
            NumRejected = 0
            NumCheap = 0
            NumDumped = 0
            NumVolunteered = 0
            TimeStep += 1   
    
subscribed_expenses = []
unsubscribed_expenses = []
for x in range(len(ListOfPatients)):
    CurrentPatient = ListOfPatients[x]
    #print "History:", CurrentPatient.history
    #print "Expenses:", CurrentPatient.expenses
    if CurrentPatient.plan == None:
        unsubscribed_expenses.append(CurrentPatient.care_cost)
    else: subscribed_expenses.append(CurrentPatient.care_cost)
      