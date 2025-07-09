import random
import json

def generate_agents(noAgents,nblocks):
    agentInfo = {}
    agentInfo['noOfAgents'] = noAgents
    agents = {}
    for i in range(noAgents):
        agent = {
            "id": f"Agent_{i+1}",
            "soc": round(random.uniform(0.5, 1.0), 2),
            "isIdle": True,
            "block": f"Block_{random.randint(1, nblocks)}"
        }
        agents[agent['id']] = agent
    agentInfo['agents'] = agents
    return agentInfo

def generate_parameters(n_blocks, grid_size):
    parameters = {}
    parameters['noOfBlocks'] = n_blocks
    parameters['gridSize'] = grid_size

    neighbors = {}
    for i in range(1, n_blocks + 1):
        block_name = f"Block {i}"
        neighbors[block_name] = []
        # top neighbor
        if i > grid_size:
            neighbors[block_name].append(f"Block {i - grid_size}")
        # right neighbor
        if i % grid_size != 0:
            neighbors[block_name].append(f"Block {i + 1}")
        # bottom neighbor
        if i <= n_blocks - grid_size:
            neighbors[block_name].append(f"Block {i + grid_size}")
        # left neighbor
        if i % grid_size != 1:
            neighbors[block_name].append(f"Block {i - 1}")
    parameters["neighbors"] = neighbors

    parameters["ev"] = {}
    parameters["request"] = {}
    parameters["congestion"] = {}
    for i in range(1, n_blocks + 1):
        block_name = f"Block {i}"
        parameters["request"][block_name] = {
            "mean": random.uniform(0.1, 0.5),
            "std": random.uniform(0.01, 0.1)
        }
        parameters["ev"][block_name] = {
            "mean": random.uniform(0.1, 0.5),
            "std": random.uniform(0.01, 0.1)
        }
        parameters["congestion"][block_name] = {}
        for neighbor in neighbors[block_name]:
            parameters["congestion"][block_name][neighbor] = {
                "mean": random.uniform(0.1, 0.5),
                "std": random.uniform(0.01, 0.1)
            }

    return parameters

if __name__ == "__main__":
    noBlocks = 4
    gridSize = 2
    parameters = generate_parameters(noBlocks, gridSize)
    file = "env/parameters.json"
    with open(file, "w") as f:
        json.dump(parameters, f, indent=4)
    print(f"Parameters data written to {file}")
    noAgents = 10
    agents = generate_agents(noAgents, noBlocks)
    file = "env/agents.json"
    with open(file, "w") as f:
        json.dump(agents, f, indent=4)
    print(f"Agents data written to {file}")
