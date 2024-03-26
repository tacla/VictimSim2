class State:
    instance_count = 0  #Class variable to keep track of the count of instances
    def __init__(self, actions, action_order):
        State.instance_count += 1
        self.id = State.instance_count  #Unique id for the state
        self.result = []                #Array to keep track of result of actions
        self.actions = actions          #Array with the sequence of actions of the explorer
        self.untried = actions          #Array to keep track of the untried actions
        self.unbacktracked = []         #Array (stack) to keep track of previous states
        self.action_order = action_order

    def getActions(self):
        return self.actions
    
    def setResult(self, state_id, action):
        self.result[self.action_order[action]] = state_id  #update the corresponding position in result
                                                           #with the state_id of the resulting state

    def getResult(self):
        return self.result
    
    def updateUntried(self):
        self.untried.pop(0)    #remove first element of the list, representing the action that was done

    def updateUnbacktracked(self, state_id):
        self.unbacktracked.push(state_id)
        





        