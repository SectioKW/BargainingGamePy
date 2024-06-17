from typing import List
from src.PlayerClass import Player
import pandas as pd
from tabulate import tabulate
import numpy as np

class Game:
    def __init__(self,players:List[Player] = [],type:str = "bargaining",
                 latex:bool = False):
        if len(players) !=2:
            raise ValueError("Game must have two players")
        self.players = players
        self.player1 = players[0]
        self.player2 = players[1]
        self.latex = latex
        self.disagreement = 0
        
    
    def get_payoff(self):
        
        payoff = []
        
        for i in range(0,len(self.players)):
            for j in range(0,len(self.players)):
                payoff.append([self.player1.strategies[i],
                                     self.player2.strategies[j]])
                
        rows = [f'{self.player1.name}: A', f'{self.player1.name}: B']
        cols = [f'{self.player2.name}: A', f'{self.player2.name}: B']

        # Create a list of lists for tabulate
        table = []
        table.append([''] + cols)  # Header row
        for i in range(len(rows)):
            row = [rows[i]]
            for j in range(len(cols)):
                row.append(payoff[(i*2)+j])
            table.append(row)

        # Display the payoff matrix with grid using tabulate
        print("Payoff Matrix:")
        print(tabulate(table, headers='firstrow', 
                       tablefmt=("latex" if self.latex else "fancy_grid")))
    
    def get_game_payoff(self):
        payoff = []
        
        for i in range(0,len(self.players)):
            for j in range(0,len(self.players)):
                payoff.append([self.player1.strategies[i]+
                                     self.player2.strategies[j]])
                
        rows = [f'{self.player1.name}: A', f'{self.player1.name}: B']
        cols = [f'{self.player2.name}: A', f'{self.player2.name}: B']

        # Create a list of lists for tabulate
        table = []
        table.append([''] + cols)  # Header row
        for i in range(len(rows)):
            row = [rows[i]]
            for j in range(len(cols)):
                row.append(payoff[(i*2)+j][0])
            table.append(row)

        # Display the payoff matrix with grid using tabulate
        print("Game Value Matrix:")
        print(tabulate(table, headers='firstrow', 
                       tablefmt=("latex" if self.latex else "fancy_grid")))
        print(f"Disagreement Value: {self.player1.name} = {self.disagreement[0]} || {self.player2.name} = {self.disagreement[1]}",)
    
    def game_nash_solve(self):
        self.get_game_payoff()
        payoff = []
        
        for i in range(0,len(self.players)):
            for j in range(0,len(self.players)):
                payoff.append([self.player1.strategies[i]+
                                     self.player2.strategies[j]])
        
        #Round 1 :
        s = max(payoff)
        
        #Round 2:
        payoff.remove(s)
        offer = max(payoff)
        if self.latex:
            print("Bargaining Solution:")
            #write to latex
            print(f'Pada awal penawaran, {self.player1.name} dan {self.player2.name} menggunakan strategi dengan nilai tertinggi')
            print(r'\begin{equation}')
            print(f's = {s[0]}')
            print(r'\end{equation}')
            print()
            print(r'\begin{equation}')
            print(f'y = {offer[0]}')
            print(f'x = {s[0]}-{offer[0]}')
            print(f'x = {s[0]-offer[0]}')
            print(r'\end{equation}')
            print()
            print("Nash Bargaining Solution:")
            print(r'\begin{equation}')
            print(f'(x/s), (y/s) = {((s[0]-offer[0])/s[0]):.3f} , {offer[0]/s[0]:.3f}')
            print(r'\end{equation}')
        else:
            print("Bargaining Solution:")
            print("-== Round 1 ==-")
            print(f's = {s[0]}')
            
            print("-== Round 2 ==-")
            print(f'y = {offer[0]}')
            print(f'x = {s[0]}-{offer[0]}')
            print(f'x = {s[0]-offer[0]}')
            
            print()
            print("Nash Bargaining Solution:")
            
            print(f'(x/s), (y/s) = {((s[0]-offer[0])/s[0]):.3f} , {offer[0]/s[0]:.3f}')
        
    def game_rubinstein_solve(self,max_iteration:int = 100):
        a = RubinsteinBargainingModel(
            self.player1.strategies[1],
            self.player1.strategies[0],
            self.player2.strategies[1],
            self.player2.strategies[0],
            self.player1.disc_factor,
            self.player2.disc_factor
        )
        result = a.simulate_bargaining(max_iteration)
        table = []
        table.append(['Round','Buyer Offer','Seller Offer'])
        for i in range(len(result[2])):
            table.append([i+1,result[3][i],result[2][i]])
        print(tabulate(table, headers='firstrow', 
                       tablefmt=("latex" if self.latex else "fancy_grid")))
        print(f"Final Offer: {self.player1.name} : {result[1]} || {self.player2.name} : {result[0]}")
        
    def set_disagreement_value(self,disagreement: List[int] ):
        self.disagreement = disagreement

class RubinsteinBargainingModel:
    
    def __init__(self, seller_min_price, seller_max_price, buyer_max_price, buyer_price,seller_discount_rate, buyer_discount_rate):
        self.seller_min_price = abs(seller_min_price)
        self.seller_max_price = abs(seller_max_price)
        self.buyer_max_price = abs(buyer_max_price)
        self.buyer_price = abs(buyer_price)
        self.seller_discount_rate = seller_discount_rate
        self.buyer_discount_rate = buyer_discount_rate
        self.available_surplus = self.buyer_max_price - self.seller_min_price
    
    # def calculate_discounted_offer(self, offer, discount_rate, num_rounds):
    #     print(offer,(1-discount_rate) ** num_rounds+1)
    #     return offer + (self.available_surplus - offer) * (1-discount_rate) ** num_rounds
    
    def seller_offer(self,offer,discount_rate,num_rounds):
        return offer - (self.available_surplus*(1-discount_rate)) //1
    
    def buyer_offer(self,offer,discount_rate,num_rounds):
        return offer + (self.available_surplus * (1-discount_rate)) //1
    
    def simulate_bargaining(self,max_iter:int):
        print("Rubinstein Bargaining Model")
        sellers = []
        buyers = []
        seller_status = "Reject"
        buyer_status = "Reject"
        # When T = 0
        # Seller then Buyer
        seller_offer = self.available_surplus
        buyer_offer = 0
        num_rounds = 0
        seller_status = self.seller_response(seller_offer, buyer_offer)
        buyer_status = self.buyer_response(buyer_offer, seller_offer)
        while num_rounds < max_iter and not self.isTransactionDone(seller_status,buyer_status) :
            num_rounds += 1
            buyer_offer = self.buyer_offer(buyer_offer, discount_rate=self.buyer_discount_rate, num_rounds=num_rounds)
            buyer_status = self.buyer_response(buyer_offer, seller_offer)
            if buyer_offer > self.available_surplus:
                buyer_offer = self.available_surplus
            buyers.append(buyer_offer)
            seller_offer = self.seller_offer(seller_offer, discount_rate=self.seller_discount_rate, num_rounds=num_rounds)
            seller_status = self.seller_response(seller_offer, buyer_offer)
            if seller_offer < 0:
                seller_offer = 0
            sellers.append(seller_offer)

        return [min(buyer_offer,self.available_surplus),max(seller_offer,0),sellers,buyers]
        
    def buyer_response(self,my_offer,offer):
        if offer < my_offer:
            return "Accept"
        elif offer == my_offer:
            return "break"
        else:
            return "Reject"
        
    def seller_response(self,my_offer,offer):
        if offer > my_offer:
            return "Accept"
        elif offer == my_offer:
            return "break"
        else:
            return "Reject"
        
    def isTransactionDone(self,seller_offer,buyer_offer):
        if seller_offer == "Accept" and buyer_offer == "Accept":
            return True
        elif seller_offer == "break" or buyer_offer == "break":
            return True 
        return False
    
    
    # def make_offer(self):
    #     return self.current_offer

    # def respond_to_offer(self, offer):
    #     if offer > self.current_offer:
    #         self.current_offer = offer
    #         return "Accept"
    #     else:
    #         return "Reject"


    # def buyer_offer(self,num_rounds:int):
    #     return 
    
    # def simulate_bargaining(self,max_iter):
    #     seller_response = ""
    #     num_rounds = 0
    #     while seller_response != "Accept" and num_rounds < max_iter:
    #         buyer_offer = self.calculate_discounted_offer(random.uniform(0, self.available_surplus), self.buyer_discount_rate, num_rounds)
    #         seller_response = self.respond_to_offer(buyer_offer)
    #         print(buyer_offer,seller_response)
    #         if seller_response == "Accept":
    #             break
    #         seller_offer = self.calculate_discounted_offer(random.uniform(self.current_offer, self.seller_min_price), self.seller_discount_rate, num_rounds)
    #         buyer_response = self.respond_to_offer(seller_offer)
    #         if buyer_response == "Accept":
    #             self.current_offer = seller_offer
    #             break
    #         num_rounds += 1
    #         print(f"Round {num_rounds}: Buyer Offer: {buyer_offer}, Seller Offer: {seller_offer}")
    #     return self.current_offer
    
    
    