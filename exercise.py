import sys


#########################
### A: AGENT BEHAVIOR ###
#########################

def average(task):
    if len(task) == 1: #only speculative utility
        return task[0][1]
    else:
        average = 0
        for utility in task:
            if utility[0] != 0:
                average += int(utility[1])
        print(average/(len(task)-1))
        return (average/(len(task)-1))



class Agent:
    def __init__(self, options):
    	if len(options) == 4: #autonomous agent
	        self.cycle = (options[0].split('='))[1]
	        self.decision = (options[1].split('='))[1]
	        self.restart = (options[2].split('='))[1]
	        self.memoryFactor = (options[3].split('='))[1]

	        global cycles_left
	        cycles_left = int(self.cycle)

	    #else: #len(options) = 6 because multi-agent system
	    #	self.cycle = (options[0].split('='))[1]
	    #	self.agents = (options[1].split('='))[1]
	    #    self.decision = (options[2].split('='))[1]
	    #    self.restart = (options[3].split('='))[1]
	    #    self.memoryFactor = (options[4].split('='))[1]
	    #    self.concurrencyPenalty = (options[5].split('='))[1]


    def perceive(self, input): # is it 'A' or 'Tx u=y'
        global restart_time, task_to_perform, gain, decide_task, cycles_left
        if input[0] == 'A':
            gain += int((input.strip().split('='))[1]) #strip() removes newline character at the end of the string
            state[task_to_perform[0]] += ((int(self.cycle)-cycles_left,(input.strip().split('='))[1]),)
            decide_task = 1 #after an update, he has to check which task to go for now (MIGHT BE PROBLEMATIC DONT FORGET THISSS)
        else: #input[0] = 'T'
            decide_task = 1
            state[(input.strip().split(' '))[0]] = ((0,(input.strip().split('='))[1]),)


    def decide_act(self): #which task shold the agent perform
    	global task_to_perform, restart_time, decide_task, cycles_left

    	if decide_task == 1:
    		previous_task = task_to_perform
    		if cycles_left >= (int(self.restart) + 1): #in this case, since I have enough steps/cycles left, I have to look into the tasks' utilities
    			for task in state.items():
    				if task[0] == 'T0':
    					task_to_perform = task
    				else:
    					if (float(average(task[1])) - float(average(task_to_perform[1]))) > 0: #compares utilities
    						task_to_perform = task

    		decide_task = 0
    	
    	cycles_left -= 1


    def recharge(self):
    	num = 0
    	denom = 0
    	output = "{"
    	for task in state.items():
    		if len(task[1]) > 1: #len = 1 means that that task was never executed (only has 1 tuple, which corresponds to the speculative utility)
    			for i in range(1, len(task[1])):
    				num += (float(task[1][i][1]) * (task[1][i][0]**float(self.memoryFactor)))
    				denom += task[1][i][0]**float(self.memoryFactor)
    			output += task[0] + '=' + str(num/denom)
    			num = 0
    			denom = 0
    		else:
    			output += task[0] + '=NA'

    		if list(state.keys())[-1] != task[0]:
    			output += ','

    	output += "} "

    	return ("state=" + output + "gain=" + str(gain) + '.00')


#####################
### B: MAIN UTILS ###
#####################
decide_task = 0 # 0 when no new task; 1 when new/need-update task and goes back to zero after knowing which task to perform
restart_time = 0 
cycles_left = 0 #number of cycles left for the algorith to end (useful to understand if it is worth pursuing a different task)
task_to_perform = () #for perceive(self, input)
gain = 0 #gain = gains for each task of each agent
state = {} #state = tasks and (expected) utilities of the agent

line = sys.stdin.readline()
agent = Agent(line.split(' ')) #line = list with every 'word'/character separated
for line in sys.stdin:
    if line.startswith("end"): break
    elif line.startswith("TIK"): agent.decide_act()
    else: agent.perceive(line)
sys.stdout.write(agent.recharge()+'\n');



