# Steps to recreate environment -:

1. Run env.py to generate parameters.json and agents.json
2. Run input.py to generate data_x.json which is the input file for timesamp x. Value of x can be changed accordingly.
3. Run generate_strategy.py to get action set and strategy profile.
</br>
Note - The agents.json file represents the state of agents after x timestamps and not the state before timestamp 0.

# Input Generation

## The input is separated as follows :-
- Parameter.json - This file contains all environment info which is common for all timestamps => no. of blocks, grid size, neighbors, mean and standard deviation for generating requests, ev distribution and congestion matrix.
- Agents.json - This file contains agent information => agent id, soc, is idle parameter, current block.
- Input file for each time stamp - This file contains the information at each timestamp => no of evs in each block, list of evs in each block, no of requests in each block, congestion matrix.

## Changes made while creating input file :-
- No of evs idle at a block is with respect to the mean and standard deviation.
- The total number of idle evs do not exceed the total number of evs available.
- The soc value is decreased in 2 conditions - 
	- A non idle ev becomes idle at some timestamp (The case where it was serving a request before so thatswhy its soc reduced)
	- An idle ev which was idle at a different block at the previous timestamp (The case where an idle ev had to come to another block because it got rebalanced. So due to the movement it's soc reduced.)
- SOC is reduced by a percentage drawn from a uniform distribution between 0.05 and 0.15.

# Strategy Generation

## Action Set:
For each agent, the action set includes its current block and all neighboring blocks.

## Feasible Action Set:
The feasible action set contains only those blocks from the action set where congestion is below a threshold.

## Payoff Function:
The payoff is calculated as the agent’s battery minus the number of requests in the target block. ( Temporary simple placeholder function)

## Strategy Profile:
Each agent selects the feasible action with the highest payoff, forming a mapping of agent to chosen action.

## All Strategy Profiles:
All possible combinations of feasible actions for all agents are generated as joint strategy profiles.