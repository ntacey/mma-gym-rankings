class Promotion:
    
    def __init__(self, name, url):
        self.name = name
        self.url = url
        self.events = []
        
    def addEvent(self, event):
        self.events.append(event)


class Event:
    
    def __init__(self, name, date):
        self.name = name
        self.date = date
        self.bouts = []
        
    def addBout(self, bout):
        self.bouts.append(bout)
        

class Bout:
    
    def __init__(self, winningFighter, losingFighter, winningGym, wonVia):
        self.winningFighter = winningFighter
        self.losingFighter = losingFighter
        self.winningGym = winningGym
        self.wonVia = wonVia


class Fighter:
    
    def __init__(self, name, url, gym):
        self.name = name
        self.url = url
        self.gym = gym
        self.bouts = [] # these are added to the fighter

    def addBout(self, bout):
        self.bouts.append(bout)
