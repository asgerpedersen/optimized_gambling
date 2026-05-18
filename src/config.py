'''
Configuration file for slot machine experiment
Kristoffersen, Due & Pedersen
'''

# ==================== INPUT SETTINGS ====================
# Key mappings
ansKeys = ['space']                 #Mappes til en fysisk knap
quitKeys = ['esc','escape']

# ==================== GAME SETTINGS ====================
start_balance = 0
cost = 7
win_price = 3
extra_spins_cost = 4
extra_spins_amount = 5      # number of extra spins

block_size = 40             # number of trials pr block
end_seq_length = 5          # number of trials in end sequence

# Time settings
between_trial_wait = 2      # in seconds (i think)
instruction_wait = 5

# Settings for trial combinations
main_trials_distribution_keys = [
    # miss, near_miss, win
    [0.5,0.3,0.2],
    [0.5,0.2,0.3],
    [0.5,0.1,0.4],
    [0.5,0.4,0.1]
]

trial_auto = [False, True, False, True, False, True, False, True]
end_sequence_type = ["miss", "near_miss", "win", "near_miss", "win", "miss", "win", "near_miss"]
distribution_key_indecies = [0,1,2,3,0,1,2,3]


def expectedBlockWinnings(start_balance, size, win_price, cost, distribution_key_index):
    number_of_wins = size * main_trials_distribution_keys[distribution_key_index][2]

    return start_balance + number_of_wins * win_price - size*cost


# ==================== DATA SETTINGS ====================
# Data containers for each trial
subjectID = 000
dataCategories = ['Block_number', 'Block_type','Trial_number', 'Trial_type', 'RT', 'Block_pleasure', 'Balance']

# File paths
saveFolder = 'data'

print((expectedBlockWinnings(start_balance, block_size, win_price, cost, distribution_key_index=0)
      + expectedBlockWinnings(start_balance, block_size, win_price, cost, distribution_key_index=1)
      + expectedBlockWinnings(start_balance, block_size, win_price, cost, distribution_key_index=2)
      + expectedBlockWinnings(start_balance, block_size, win_price, cost, distribution_key_index=3))*2)