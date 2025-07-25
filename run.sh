#clear all files in env and input directory
rm -rf env/*
rm -rf input/*

#delete strategy_comparison.png if it exists which is in current directory
if [ -f strategy_comparison.png ]; then
    rm strategy_comparison.png
fi
#delete strategy.txt if it exists which is in current directory
if [ -f strategy.txt ]; then
    rm strategy.txt
fi

# run env.py
python3 env.py

# run input.py
python3 input.py

# run objective.py and save output to strategy.txt
python3 objective.py > strategy.txt