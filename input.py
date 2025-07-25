import json
import random

def generate_data(timeStamp, nblocks, gridSize, neighbors, distributionEV, distributionRequest, distributionCongestion, noOfAgents, agents, scaleEv, scaleRequest, scaleCongestion):

    requests = {}
    for block in range(nblocks):
        block_name = f"Block {block + 1}"
        mean = distributionRequest[block_name]["mean"] 
        std = distributionRequest[block_name]["std"] 
        requests[block_name] = max(0, int(random.gauss(mean, std) * scaleRequest))

    congestion = {}
    for block in range(nblocks):
        block_name = f"Block {block + 1}"
        congestion[block_name] = {}
        for neighbor in neighbors[block_name]:
            mean = distributionCongestion[block_name][neighbor]["mean"] 
            std = distributionCongestion[block_name][neighbor]["std"] 
            congestion[block_name][neighbor] = max(0, int(random.gauss(mean, std) * scaleCongestion))

    ev_count = {}
    total_generated = 0

    initial_counts = {}
    for block in range(nblocks):
        block_name = f"Block {block + 1}"
        mean = distributionEV[block_name]["mean"] 
        std = distributionEV[block_name]["std"] 
        count = max(0, int(random.gauss(mean, std) * scaleEv))
        initial_counts[block_name] = count
        total_generated += count

    if total_generated > noOfAgents:
        scale_factor = noOfAgents / total_generated
        remaining_agents = noOfAgents
        
        for block in range(nblocks):
            block_name = f"Block {block + 1}"
            if block == nblocks - 1:  
                ev_count[block_name] = remaining_agents
            else:
                scaled_count = int(initial_counts[block_name] * scale_factor)
                ev_count[block_name] = scaled_count
                remaining_agents -= scaled_count
    else:
        ev_count = initial_counts.copy()
    
    # Create a list of available agents and shuffle for random assignment
    available_agents = list(agents.keys())
    random.shuffle(available_agents)

    ev_distribution = {}
    assigned_agents = set()

    # Assign agents to blocks based on ev_count
    agent_index = 0
    for block in range(nblocks):
        block_name = f"Block {block + 1}"
        ev_distribution[block_name] = []
        
        # Assign the required number of agents to this block
        for _ in range(ev_count[block_name]):
            if agent_index < len(available_agents):
                agent_name = available_agents[agent_index]
                agent_info = agents[agent_name]
                
                current_block = agent_info.get("block", None)
                
                # Update agent's block assignment and set as idle
                agent_info["block"] = block_name
                agent_info["isIdle"] = True
                
                # Reduce SOC if agent was not idle OR if they're moving to a different block
                should_reduce_soc = (not agents[agent_name].get("isIdle", True)) or (current_block != block_name)

                if should_reduce_soc:
                    soc_reduction_percent = random.uniform(0.05, 0.15)  # 5% to 15%
                    current_soc = agent_info["soc"]
                    new_soc = current_soc * (1 - soc_reduction_percent)
                    agent_info["soc"] = max(0.0, new_soc)
                
                # Add the full agent info to ev_distribution
                # print(f"Assigning {agent_name} to {block_name} with SOC {agent_info['soc']}")
                # print(agent_info)
                ev_distribution[block_name].append(agent_info.copy())
                
                # Update the original agents dictionary
                agents[agent_name] = agent_info
                assigned_agents.add(agent_name)
                
                agent_index += 1

    # For unassigned agents, set isidle to False
    # print("Assigned Agents:", assigned_agents)
    # print("Unassigned Agents:", set(agents.keys()) - assigned_agents)
    for agent_name in agents:
        if agent_name not in assigned_agents:
            agents[agent_name]["isIdle"] = False

    data = {
        "timeStamp": timeStamp,
        "evCount": ev_count,
        "evDistribution": ev_distribution,
        "requests": requests,
        "congestion": congestion
    }

    return data, agents
    
        

if __name__ == "__main__":

    agentInfo = json.load(open("env/agents.json"))
    noOfAgents = agentInfo['noOfAgents']
    agents = agentInfo['agents']

    parameters = json.load(open("env/parameters.json"))
    nblocks = parameters['noOfBlocks']
    gridSize = parameters['gridSize']
    neighbors = parameters['neighbors']
    distributionEV = parameters['ev']
    distributionRequest = parameters['request']
    distributionCongestion = parameters['congestion']

    scaleEv= 7
    scaleRequest = 10
    scaleCongestion = 10

    timestamps = []

    for x in range(4):
        # print(f"Generating data for timestamp {x + 1}...")
        data, agents = generate_data(x, nblocks, gridSize, neighbors, distributionEV, distributionRequest, distributionCongestion, noOfAgents, agents, scaleEv, scaleRequest, scaleCongestion)
        timestamps.append(data)      

    with open("input/testcase.json", "w") as f:
        json.dump(timestamps, f, indent=4)

    print("Data generated successfully.")
