

class Player:
    def __init__(self,name:str,disc_factor:int = 1,negative:bool=False) -> object:
        self.name = name
        self.strategies = []
        self.negative = negative
        self.disc_factor = disc_factor
        
    def set_strategy(self, num1:int = 0, num2:int = 0):
        if self.negative:
            if num1 < num2:
                num1 = -(abs(num1))
                num2 = -(abs(num2))
                self.strategies = [num1,num2]
            else:
                num1 = -(abs(num1))
                num2 = -(abs(num2))
                self.strategies = [num2,num1]
        else:
            if num1 > num2:
                self.strategies = [num1,num2]
            else:
                self.strategies = [num2,num1]
