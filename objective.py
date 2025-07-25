import json
import random
from itertools import product
import matplotlib.pyplot as plt

class Strategy:
    def __init__(self, testcaseData, parameters, scaleRequst=10):
        self.totalTimestamps = len(testcaseData)
        self.testcaseData = testcaseData
        self.noOfBlocks = parameters['noOfBlocks']
        self.gridSize = parameters['gridSize']
        self.neighbors = parameters['neighbors']
        self.paramsRequest = parameters['request']
        self.scaleRequest = scaleRequst

    def getAvailableAgents(self, evdistribution):
        availableAgents = []
        for block, agentList in evdistribution.items():
            for agent in agentList:
                availableAgents.append(agent)
        return availableAgents

    def getActions(self, agent):
        currentBlock = agent['block']
        actionSet = [currentBlock] + self.neighbors.get(currentBlock, [])
        return actionSet
    
    def getFeasibleActions(self, agent, actionSet, congestion, threshold=2):
        feasibleActions = []
        currentBlock = agent['block']
        for action in actionSet:
            if action == currentBlock or congestion.get(currentBlock, {}).get(action, 0) < threshold:
                feasibleActions.append(action)
        return feasibleActions
    
    def objectiveFunction(self, profile, requests):
        newEvCount = {}
        for i in range(1, self.noOfBlocks + 1):
            blockName = f"Block {i}"
            newEvCount[blockName] = 0
        for agent, action in profile.items():
            newEvCount[action] += 1
        
        for block in newEvCount:
            if block not in requests:
                requests[block] = 0
            newEvCount[block] = max(requests[block] - newEvCount[block], 0)

        return max(newEvCount.values())
    
    def getTransitionProbability(self, evsInBlock, totalEvs):
        if evsInBlock > 0.5 * totalEvs:
            return random.uniform(0.5, 1.0)
        else:
            return random.uniform(0.0, 0.5)
    
    def estimateEVs(self, blockName, agents):
        presentEVs = sum(1 for agent in agents if agent['block'] == blockName)
        totalEVs = len(agents)
        adjBlocks = self.neighbors.get(blockName, [])
        incomingEVs = 0
        for adjBlock in adjBlocks:
            evsInAdj = sum(1 for agent in agents if agent['block'] == adjBlock)
            prob = self.getTransitionProbability(evsInAdj, totalEVs)
            incomingEVs += int(evsInAdj * prob)
        return presentEVs + incomingEVs

    def payoff(self, agent, action, agents, congestion):
        soc = agent['soc']
        requestMean = self.paramsRequest[action]['mean']
        requestStd = self.paramsRequest[action]['std']
        forecastedRequests = max(0, int(random.gauss(requestMean, requestStd)* self.scaleRequest))
        estimatedEVs = self.estimateEVs(action, agents)
        currentBlock = agent['block']
        tau = congestion.get(currentBlock, {}).get(action, 0)
        payoffValue = soc * max(forecastedRequests - estimatedEVs, 0) / (tau + 1)
        return payoffValue
   
    def payoffStrategy(self, agents, feasibleActionSet, congestion):
        profile = {}
        for agent in agents:
            actions = feasibleActionSet[agent['id']]
            bestAction = max(actions, key=lambda a: self.payoff(agent, a, agents, congestion))
            profile[agent['id']] = bestAction
        return profile


    def getAllStrategies(self, timestampIndex):
        print("Timestamp Index:", timestampIndex)
        data = self.testcaseData[timestampIndex]
        evDistribution = data['evDistribution']
        agents = self.getAvailableAgents(evDistribution)
        
        ActionSet = {}
        print("Action Set:")
        for agent in agents:
            actions = self.getActions(agent)
            print(f" - {agent['id']}: {actions}")
            ActionSet[agent['id']] = actions

        feasibleActionSet = {}
        print("Feasible Actions:")
        for agent in agents:
            feasibleActions = self.getFeasibleActions(agent, ActionSet[agent['id']], data['congestion'])
            print(f" - {agent['id']}: {feasibleActions}")
            feasibleActionSet[agent['id']] = feasibleActions

        allStrategies = []
        objectiveValues = []
        requests = data['requests']
        print("All Strategy Profiles:")
        for i, strategy in enumerate(product(*feasibleActionSet.values())):
            profile = {agent_id: action for agent_id, action in zip(feasibleActionSet.keys(), strategy)}
            allStrategies.append(profile)
            print(f" - Profile {i}:")
            for agent_id, action in profile.items():
                print(f"   - {agent_id} -> {action}")
            objectiveValue = self.objectiveFunction(profile, requests)
            objectiveValues.append(objectiveValue)
            print(f"   - Objective Value: {objectiveValue}")

        print("Strategy Profile based on payoff:")
        bestProfile = self.payoffStrategy(agents, feasibleActionSet, data['congestion'])
        for agent_id, action in bestProfile.items():
            print(f" - {agent_id} -> {action}")
        payoffObjectiveValue = self.objectiveFunction(bestProfile, requests)
        print(f" - Objective Value: {payoffObjectiveValue}")

        print("Best Strategy Profile According to Objective Function:")
        bestIndex = objectiveValues.index(min(objectiveValues))
        bestProfile = allStrategies[bestIndex]
        print(f" - Profile {bestIndex}: {bestProfile}")
        print(f" - Objective Value: {objectiveValues[bestIndex]}")

        return payoffObjectiveValue, objectiveValues[bestIndex]


if __name__ == "__main__":
    with open("input/testcase.json", "r") as f:
        testcase_data = json.load(f)

    with open("env/parameters.json", "r") as f:
        parameters = json.load(f)

    strategy = Strategy(testcase_data, parameters)
    payoffStrategy = []
    bestStrategy = []
    for i in range(strategy.totalTimestamps):
        payoffValue, objectiveValue = strategy.getAllStrategies(i)
        payoffStrategy.append(payoffValue)
        bestStrategy.append(objectiveValue)
        print("-----------------------------------------------")
    
    
    plt.figure(figsize=(10, 5))
    x = range(strategy.totalTimestamps)
    plt.bar(x, payoffStrategy, width=0.4, label='Payoff Strategy', color='blue', align='center')
    plt.bar([p + 0.4 for p in x], bestStrategy, width=0.4, label='Best Strategy', color='green', align='center')
    plt.xlabel('Timestamp Index')
    plt.ylabel('Objective Value')
    plt.title('Comparison of Payoff Strategy and Best Strategy')
    plt.xticks([p + 0.2 for p in x], [f'Timestamp {i}' for i in x])
    plt.legend()
    plt.tight_layout()
    plt.savefig("strategy_comparison.png")

    


    