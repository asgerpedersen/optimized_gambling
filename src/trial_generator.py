from itertools import product
import random
import config
from math import floor

def trialType(reel_stop):
        if reel_stop[0] == reel_stop[1] == reel_stop[2]:
            return "win"
        elif reel_stop[0] == reel_stop[1] != reel_stop[2]:
            return "near_miss"
        else:
            return "miss"

total_combinations = [list(c) for c in product(range(1,10), repeat=3)]

win_combinations = [c for c in total_combinations if trialType(c)=='win']
near_miss_combinations = [c for c in total_combinations if trialType(c)=='near_miss']
miss_combinations = [c for c in total_combinations if trialType(c)=='miss']


def generateTrials(distribution_key):                   #Size must be divisable by four 
    miss_ratio = distribution_key[0]
    near_miss_ratio = distribution_key[1]
    win_ratio = distribution_key[2]
    
    trials = []
    # Add 1/4 size number of win combinations
    trials.extend(
        random.choices(win_combinations, k=int(config.block_size * win_ratio))
            )
    trials.extend(
        random.choices(near_miss_combinations, k=int(config.block_size * near_miss_ratio))
            )
    trials.extend(
        random.choices(miss_combinations, k=int(config.block_size * miss_ratio))
            )
    
    # mix 'em up!
    random.shuffle(trials)

    return trials


def generateEndSequence(end_seq_type):
    end_sequence = []
    if end_seq_type == "miss":                                                                 # Only miss trials
        end_sequence.extend(random.sample(miss_combinations, config.end_seq_length))
    
    elif end_seq_type == "near_miss":                                                                # Three near miss trials
        end_sequence.extend(random.sample(miss_combinations, config.end_seq_length-3))
        end_sequence.extend(random.sample(near_miss_combinations, 3))
    
    elif end_seq_type == "win":
        end_sequence.extend(random.sample(miss_combinations, config.end_seq_length-3))
        end_sequence.extend(random.sample(win_combinations, 3))

    random.shuffle(end_sequence)
    return end_sequence


def generateExtraSpins():
    extra_spins = []
    extra_spins.extend(random.sample(total_combinations, 5))

    return extra_spins