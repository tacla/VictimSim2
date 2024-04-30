from collections import deque
from vs.constants import VS
from map import Map

class BFS:
    def __init__ (self, map, cost_line=1.0, cost_diag=1.5):
        self.map = map             # an instance of the class Map
        self.frontier = None       # the frontier of the search algorithm
        self.cost_line = cost_line # the cost to move one step in the horizontal or vertical
        self.cost_diag = cost_diag # the cost to move one step in any diagonal
        self.tlim = float('inf')    # when the walk time reach this threshold, the plan is aborted
        
        
        self.incr = {              # the increments for each walk action
            0: (0, -1),             #  u: Up
            1: (1, -1),             # ur: Upper right diagonal
            2: (1, 0),              #  r: Right
            3: (1, 1),              # dr: Down right diagonal
            4: (0, 1),              #  d: Down
            5: (-1, 1),             # dl: Down left left diagonal
            6: (-1, 0),             #  l: Left
            7: (-1, -1)             # ul: Up left diagonal
        }

    # Find possible actions of a given position (state)
    def get_possible_actions(self, pos):
        x, y = pos
        actions = []


        if self.map.in_map(pos):
            incr = 0
            for key in self.incr:
                possible_pos = self.map.get_actions_results(pos)
                if possible_pos[incr] == VS.CLEAR:
                    actions.append((self.incr[key][0], self.incr[key][1]))

                incr += 1
            
        return actions

    # Verifies if pos (state) is already in the frontier
    def in_the_frontier(self, pos):
        for node in self.frontier:
            frontier_pos, _, _ = node
            if pos == frontier_pos:
                return True
            
        return False

    
    def search(self, start, goal, tlim=float('inf')):
        """ this method performs a breadth-first search.
            @param start the initial position
            @param goal  the goal position
            @returns     a plan (a list of actions defined as increments in x and y; and the time to execute the plan
                         for instance: [(-1, 0), (-1, 1), (1, 1), (1, 0)] walk -1 in the x position, walk -1 in x and +1 in the y;  so on
                         In case of fail, it returns:
                         [], -1: no plan because the time limit was reached
                         [],  0: no path found between start and goal position
                         plan, time: a plan with the time required to execute (only walk actions)"""
        self.tlim = tlim
        selected = set()
        self.frontier = deque([(start, [], 0)]) # double ended queue (position, plan in delta x and delta y, accumulated time)
        if start == goal:
           return [], 0
        
        while self.frontier:   # queue is not empty
            current_pos, plan, acc_cost = self.frontier.popleft()   # pop head of the queue
            selected.add(current_pos)
            possible_actions = self.get_possible_actions(current_pos)
     
            for action in possible_actions:
                child = (current_pos[0] + action[0], current_pos[1] + action[1])
                
                if self.map.in_map(child) and child not in selected and not self.in_the_frontier(child):
                    difficulty = self.map.get_difficulty(child)
                    if action[0] == 0 or action[1] == 0: # hor or vertical move
                        new_acc_cost = acc_cost + self.cost_line * difficulty
                    else:
                        new_acc_cost = acc_cost + self.cost_diag * difficulty

                    
                    new_plan = plan + [action]
                    
                    if child == goal:
                        if new_acc_cost > self.tlim:
                            return [], -1    # time exceeded
                        
                        return new_plan, new_acc_cost

                    self.frontier.append((child, new_plan, new_acc_cost))  #append child
                

                    
        return None, 0  # No path found

# Example usage: it is a script not used when importe by other module
if __name__ == '__main__':
    map = Map()
    map.data = {
        (0, 0): (1, VS.NO_VICTIM, [VS.END, VS.END, VS.CLEAR, VS.CLEAR, VS.CLEAR, VS.CLEAR, VS.END,   VS.END]),
        (1, 0): (1, VS.NO_VICTIM, [VS.END, VS.END, VS.CLEAR, VS.CLEAR, VS.CLEAR, VS.CLEAR, VS.CLEAR, VS.END]),
        (2, 0): (1, VS.NO_VICTIM, [VS.END, VS.END, VS.CLEAR, VS.WALL,  VS.WALL,  VS.CLEAR, VS.CLEAR, VS.END]),
        (3, 0): (1, VS.NO_VICTIM, [VS.END, VS.END, VS.END,   VS.END,   VS.WALL,  VS.WALL,  VS.CLEAR, VS.END]),   
        (0, 1): (1, 1,            [VS.CLEAR, VS.CLEAR, VS.CLEAR, VS.CLEAR, VS.CLEAR, VS.END,   VS.END,   VS.END]),
        (1, 1): (1, 2,            [VS.CLEAR, VS.CLEAR, VS.WALL,  VS.CLEAR, VS.CLEAR, VS.CLEAR, VS.CLEAR, VS.CLEAR]),
        (0, 2): (1, VS.NO_VICTIM, [VS.CLEAR, VS.CLEAR, VS.CLEAR, VS.END, VS.END, VS.END, VS.END,   VS.END]),
        (1, 2): (1, VS.NO_VICTIM, [VS.CLEAR, VS.WALL,  VS.CLEAR, VS.END, VS.END, VS.END, VS.CLEAR, VS.CLEAR]),
        (2, 2): (1, VS.NO_VICTIM, [VS.WALL,  VS.WALL,  VS.CLEAR, VS.END, VS.END, VS.END, VS.CLEAR, VS.CLEAR]),
        (3, 2): (1, 3,            [VS.WALL,  VS.END,   VS.END,   VS.END, VS.END, VS.END, VS.CLEAR, VS.WALL]),
    }
    map.draw()

    start = (3, 0)
    goal = (3, 2)
    bfs = BFS(map)
    plan, total_cost = bfs.search(start, goal)
    print(f"Start: {start}, goal: {goal} cost: {total_cost}")
    print(f"Plan: {plan}")

