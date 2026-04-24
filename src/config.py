'''
Configuration file for slot machine experiment
Kristoffersen, Due & Pedersen
'''

# ==================== INPUT SETTINGS ====================
# Key mappings
ansKeys = ['space']                 #Mappes til en fysisk knap
quitKeys = ['esc','escape']

# ==================== MONEY SETTINGS ====================
cost = 10
win_price = 50

# ==================== DATA SETTINGS ====================
# Data containers for each trial
subjectID = 000
dataCategories = ['Block_number', 'Block_type','Trial_number', 'Trial_type', 'RT', 'Block_pleasure', 'Balance']

# File paths
saveFolder = 'data'