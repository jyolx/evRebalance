import json

def load_data(filename):
    with open(filename, 'r') as f:
        return json.load(f)

def get_agents(data):
    # Flatten agents from evDistribution
    agents = {}
    for block, agent_list in data['evDistribution'].items():
        for agent in agent_list:
            agents[agent['id']] = {
                'block': agent['block'],
                'soc': agent['soc'],
                'isIdle': agent['isIdle']
            }
    return agents

def get_action_set(agents, neighbors):
    action_set = {}
    for agent, info in agents.items():
        current_block = info['block']
        action_set[agent] = [current_block] + neighbors.get(current_block, [])
    return action_set

def feasible_actions(agent, agents, action_set, congestion, threshold=2):
    '''Determine feasible actions for an agent based on congestion.'''
    current_block = agents[agent]['block']
    actions = action_set[agent]
    feasible = []
    for action in actions:
        if action == current_block:
            feasible.append(action)
        else:
            if congestion.get(current_block, {}).get(action, 0) < threshold:
                feasible.append(action)
    return feasible

def payoff(agent, action, agents, requests):
    '''Calculate the payoff for an agent given an action.'''
    soc = agents[agent]['soc']
    req = requests.get(action, 0)
    return soc - req

def strategy_profile(agents, action_set, congestion, requests):
    '''Generate a strategy profile for the agents based on their best actions.'''
    profile = {}
    for agent in agents:
        actions = feasible_actions(agent, agents, action_set, congestion)
        best_action = max(actions, key=lambda a: payoff(agent, a, agents, requests))
        profile[agent] = best_action
    return profile

def generate_all_strategy(agents, action_set, congestion):
    '''Generate all possible strategy profiles for the agents.'''
    from itertools import product
    agent_list = list(agents.keys())
    action_lists = [feasible_actions(agent, agents, action_set, congestion) for agent in agent_list]
    all_profiles = []
    for actions in product(*action_lists):
        profile = {agent: action for agent, action in zip(agent_list, actions)}
        all_profiles.append(profile)
    return all_profiles
    

if __name__ == "__main__":
    data_filename = "input/data_0.json"
    param_filename = "env/parameters.json"
    data = load_data(data_filename)
    params = load_data(param_filename)
    agents = get_agents(data)
    neighbors = params['neighbors']
    action_set = get_action_set(agents, neighbors)
    print("Action Set:", action_set)
    feasible_actions_= {agent: feasible_actions(agent, agents, action_set, data['congestion']) for agent in agents}
    print("Feasible Actions:", feasible_actions_)
    profile = strategy_profile(agents, action_set, data['congestion'], data['requests'])
    print("Strategy Profile based on payoff:", profile)
    all_profiles = generate_all_strategy(agents, action_set, data['congestion'])
    for i, p in enumerate(all_profiles):
        print(f"Profile {i+1}: {p}")