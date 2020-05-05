from .agent import Agent
import random as RD
import matplotlib.pyplot as plt
import numpy as np
import math
import csv

adminCost = 0.15

class Payer(Agent):
    
    def __init__(self, premium_price, starting_capital, seed=None):
        # Payer is the agent that pays Providers for medical procedures, and is paid premiums by Patients
        # Usually represents insurance companies, but might represent government agencies
        self.inMarket = True # Payers can choose whether to serve a specific market
        self.premium = premium_price 
        self.ledger = [[]] # list of cost lists for each turn
        self.subscribers = [] # list of subscribers in a given turn
        self.premiums_list = [] # list of premiums over time
        self.subscribers_list = [] # number of subscribers over time
        self.premium_minimum = 10 # lowest premium a payer will accept typically the expected cost of claims (actuarially fair price)
        self.isMedicare = False
        self.isMedicaid = False
        self.isPrivate = False
        self.govtCost = []
        self.deductible = 2000 # starting deductible for each patient
        self.capital = starting_capital  # initial cash funds of payor
    
    def add_cost(self, expense_cost):
        self.ledger[-1].append(expense_cost)
        
    def assess_costs(self): # Not including admin cost
        return sum(self.ledger[-1])
    
    def assess_revenue(self):
        return self.subscribers_list[-1] * self.premiums_list[-1]
    
    #Assess cost to government of Medicare (75% of total cost)
    def assess_govtCosts(self, medicarePct):
        if self.isMedicare:
            cost = (1-medicarePct) * self.assess_costs()
        elif self.isMedicaid:
            cost = self.assess_costs()
        else:
            cost = 0.0
        self.govtCost.append(cost)
        return cost
    
    def newYear(self):
        self.ledger.append([])
        
    def update_capital(self): # Call prior to update_premium_deductible()
        if self.isPrivate:
            current_costs = self.assess_costs()*(1+adminCost)
            current_income = self.premium*len(self.subscribers)
            self.capital = self.capital + current_income - current_costs
        
       
    def update_premium_deductible(self, BestPlan, medicarePct, adminCost, maxRaise, deductibleChange):
        # If a Payer has subscribers, then they will reset their premium price
        if len(self.subscribers) != 0:  
            #If Medicare, 25% of per capita cost of care              
            if self.isMedicaid:
                self.deductible = 0
                self.premium = 0
            elif self.isMedicare:
                self.deductible = 0
                self.premium = self.assess_costs()*medicarePct/len(self.subscribers)
                self.premiums_list.append(self.premium)
            else:
                # This year's level of cost per subscriber
                newPremVal = self.assess_costs()*(1+adminCost)/len(self.subscribers)
                # Percent of old premium
                premPct = newPremVal/self.premium
                if premPct > 1:
                    if premPct > (1+maxRaise):
                        self.premium = self.premium*(1+maxRaise)
                        self.deductible += deductibleChange
                    else:
                        self.premium = self.premium*(premPct)
                #Only reduce premium and deductible if costs decrease by more than 10% and not in the red
                elif premPct < (1-maxRaise+.1) and self.capital > 0: 
                    if premPct < (1-maxRaise):
                        self.premium = self.premium*(1-maxRaise+.1)
                        if self.deductible >= deductibleChange:
                            self.deductible -= deductibleChange 
                    else:
                        self.premium = self.premium*(premPct+0.1)
                    
                self.premiums_list.append(self.premium)
                
                          
        # If a Payer no longer has subscribers, then they will lower their coinsurance rate and premium price to regain competitive edge
        else:
            print("Plan has zero subscribers.")
            self.premium = BestPlan.premium*0.95
            self.deductible = BestPlan.deductible
    
    def check_bankruptcy(self):
        if self.capital <= 0 and self.isPrivate :
            self.inMarket = False
            for j in range(len(self.subscribers)):
                self.subscribers[j].plan = None
            del self.subscribers[:]
            return True
        else: 
            return False
            
