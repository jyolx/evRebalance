import json
import numpy as np

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

def get_transition_probability(evs_in_block, total_evs):
    '''
    Returns a sampled probability for EVs moving from a block to another.
    If evs_in_block > 0.5 * total_evs, sample from [0.5, 1.0], else from [0.0, 0.5).
    '''
    if evs_in_block > 0.5 * total_evs:
        return np.random.uniform(0.5, 1.0)
    else:
        return np.random.uniform(0.0, 0.5)

def estimate_evs(action_block, agents, neighbors):
    '''Estimates the number of EVs expected to be present at action_block.'''
    # Number of EVs already present in action_block
    present_evs = sum(1 for agent in agents.values() if agent['block'] == action_block)
    # Total EVs
    total_evs = len(agents)
    # Sum over adjacent blocks
    adj_blocks = [block for block in neighbors if action_block in neighbors[block]]
    incoming_evs = 0
    for adj_block in adj_blocks:
        evs_in_adj = sum(1 for agent in agents.values() if agent['block'] == adj_block)
        prob = get_transition_probability(evs_in_adj, total_evs)
        incoming_evs += evs_in_adj * prob
    return present_evs + incoming_evs

def payoff(agent, action, agents,params,congestion):
    '''Calculate the payoff for an agent given an action.'''
    soc = agents[agent]['soc']
    mean = params['request'][action]['mean']
    std = params['request'][action]['std']
    forecasted_requests = np.random.normal(mean, std)
    estimated_evs = estimate_evs(action, agents, params['neighbors'])
    current_block = agents[agent]['block']
    tau= congestion[current_block][action] if action in congestion[current_block] else 0
    payoff_value = soc * max(forecasted_requests-estimated_evs,0)/ (tau + 1)
    return payoff_value

def strategy_profile(agents, action_set, congestion, params):
    '''Generate a strategy profile for the agents based on their best actions.'''
    profile = {}
    for agent in agents:
        actions = feasible_actions(agent, agents, action_set, congestion)
        best_action = max(actions, key=lambda a: payoff(agent, a, agents, params,congestion))
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
    print("Action Set:")
    for agent, actions in action_set.items():
        print(f"{agent}: {actions}")
    print("----------------------------------------------")
    feasible_actions_= {agent: feasible_actions(agent, agents, action_set, data['congestion']) for agent in agents}
    print("Feasible Actions:")
    for agent, actions in feasible_actions_.items():
        print(f"{agent}: {actions}")
    print("----------------------------------------------")
    profile = strategy_profile(agents, action_set, data['congestion'], params)
    print("Strategy Profile based on payoff:")
    for agent, action in profile.items():
        print(f"{agent} -> {action}")
    print("----------------------------------------------")
    all_profiles = generate_all_strategy(agents, action_set, data['congestion'])
    print("All Strategy Profiles:")
    for i, p in enumerate(all_profiles):
        print(f"Profile {i+1}: {p}")