import sys


#########################
### A: AGENT BEHAVIOR ###
#########################

def average(task, memoryFactor):
	if len(task) == 1: #only speculative utility
		return task[0][1]
	else:
		num = 0.0
		denom = 0.0
		for i in range(1, len(task)):
			num += (float(task[i][1]) * (task[i][0]**memoryFactor))
			denom += task[i][0]**memoryFactor
		return round(num/denom,4)


class Agent:
	def __init__(self, options):
		self.restart = 0
		if len(options) == 4: #autonomous agent
			self.cycle = int((options[0].split('='))[1])
			self.decision = (options[1].split('='))[1]
			self.restart = int((options[2].split('='))[1])
			self.memoryFactor = float((options[3].split('='))[1])

		else: #len(options) = 6 because multi-agent system
			self.cycle = int((options[0].split('='))[1])
			self.agents = (((options[1].split('='))[1])[1:-1]).split(',')
			self.decision = (options[2].split('='))[1]
			self.restart = int((options[3].split('='))[1])
			self.memoryFactor = float((options[4].split('='))[1])
			self.concurrencyPenalty = int((options[5].split('='))[1])

		self.cycles_left = self.cycle
		self.decide_task = 0 # 0 when no new task; 1 when new/need-update task and goes back to zero after knowing which task to perform
		self.restart_time = self.restart
		self.task_to_perform = () #for perceive(self, input) ----- {'T0': ((A1),(A2),(A3)), 'T1': ((A1),(A2),(A3)), ...}
		self.gain = 0 #gain = gains for each task of each agent
		self.state = {} #state = tasks and utilities of the agent


	def perceive(self, input): # is it 'A' or 'Tx u=y'
		if input[0] == 'A':
			self.gain += float((input.strip().split('='))[1]) #strip() removes newline character at the end of the string
			self.state[self.task_to_perform[0]] += ((self.cycle-self.cycles_left,(input.strip().split('='))[1]),)
		else: #input[0] = 'T'
			self.state[(input.strip().split(' '))[0]] = ((0,(input.strip().split('='))[1]),)


	def decide_act(self): #which task shold the agent perform
		if len(self.task_to_perform) > 0:
			previous_task = (self.task_to_perform[0],self.state[self.task_to_perform[0]])
		else:
			previous_task = ()

		if self.cycles_left >= self.restart: #in this case, since I have enough steps/cycles left, I have to look into the tasks' utilities
			self.task_to_perform = ('T0',self.state['T0'])
			for task in self.state.items(): # para ver a melhor task
				if task[0] != 'T0':
					if (float(average(task[1], self.memoryFactor)) > float(average(self.task_to_perform[1], self.memoryFactor))):
						self.task_to_perform = task

		if self.restart == 0:
			self.cycles_left -= 1
			return

		expected_to_perform = float(average(self.task_to_perform[1], self.memoryFactor))*(self.cycles_left-self.restart)
		if len(previous_task) > 0:
			expected_previous = float(average(previous_task[1], self.memoryFactor))*(self.cycles_left-self.restart_time)
		else:
			expected_previous = float('-inf')

		if (expected_previous > expected_to_perform) or (expected_previous == expected_to_perform and int(previous_task[0][1:]) <= int(self.task_to_perform[0][1:])):
			self.task_to_perform = previous_task
			if self.restart_time != 0:
				self.restart_time -=1
		else:
			self.restart_time = self.restart - 1
		
		self.cycles_left -= 1


	def recharge(self):
		global agentPos, heteroGain
		if self.decision == 'rationale':
			output = "{"
			for task in self.state.items():
				if len(task[1]) > 1: #len = 1 means that that task was never executed (only has 1 tuple, which corresponds to the speculative utility)
					output += task[0] + '=' + ("{:.2f}".format(float(average(task[1], self.memoryFactor))))
				else:
					output += task[0] + '=NA'

				if list(self.state.keys())[-1] != task[0]:
					output += ','
			
			output += "} "

			return ("state=" + output + "gain=" + str(("{:.2f}".format(self.gain))))

		elif self.decision == 'homogeneous-society':
			output = "{"
			for i in range(len(self.agents)):
				output += 'A' + str(i+1) + '={'
				for task in self.state.items():
					if len(task[1]) > 1: #len = 1 means that that task was never executed (only has 1 tuple, which corresponds to the speculative utility)
						output += task[0] + '=' + ("{:.2f}".format(float(average(task[1], self.memoryFactor))))
					else:
						output += task[0] + '=NA'

					if list(self.state.keys())[-1] != task[0]:
						output += ','

				output += '}'
				if i != len(self.agents)-1:
					output += ','

			output += "} "

			return ("state=" + output + "gain=" + str(("{:.2f}".format(self.gain))))

		elif self.decision == 'heterogeneous-society':
			if agentPos == 0:
				output = 'state={'
				output += self.agents[agentPos] + '={'
			else:
				output = self.agents[agentPos] + '={' 
				
			for task in self.state.items():
				if len(task[1]) > 1: #len = 1 means that that task was never executed (only has 1 tuple, which corresponds to the speculative utility)
					output += task[0] + '=' + ("{:.2f}".format(float(average(task[1], self.memoryFactor))))
				else:
					output += task[0] + '=NA'

				if list(self.state.keys())[-1] != task[0]:
					output += ','

			output += '}'

			heteroGain += self.gain
			
			if agentPos != len(self.agents)-1:
					output += ','
					agentPos += 1
					return (output)

			else:
				output += "} "
				return (output + "gain=" + str(("{:.2f}".format(heteroGain))))


		


#####################
### B: MAIN UTILS ###
#####################

agentPos = 0 #agent position for heterogeneous society recharge
heteroGain = 0 

line = sys.stdin.readline()
if (len(line.split(' ')) == 4) or ((len(line.split(' ')) == 6) and (line.split(' ')[2].split('=')[1] == 'homogeneous-society')):
	agent = Agent(line.split(' '))
	for line in sys.stdin:
		if line.startswith("end"): break
		elif line.startswith("TIK"): agent.decide_act()
		else: agent.perceive(line)
	sys.stdout.write(agent.recharge()+'\n');

else:
	agents = list()
	for i in range(len(line.split(' ')[1].split('=')[1][1:-1].split(','))): #number of agents
		agents.append(Agent(line.split(' '))) #line = list with every 'word'/character separated

	for line in sys.stdin:
		if line.startswith("end"): break
		elif line.startswith("TIK"): 
			for agent in agents:
				agent.decide_act()
		else: 
			if line.startswith("T"):
				for agent in agents:
					agent.perceive(line)
			else:
				agents[int(line.split(' ')[0][1:])-1].perceive(line)

	for agent in agents:
		if agent != agents[-1]:
			sys.stdout.write(agent.recharge());
		else:
			sys.stdout.write(agent.recharge()+'\n');



