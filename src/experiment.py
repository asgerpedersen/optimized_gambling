from psychopy import core, visual, sound, event, gui, monitors
import threading, time, requests
import serial
from flask import Flask, Response, jsonify, request, send_from_directory
import queue, json
import os, csv
import trial_generator
import config

#----EEG--Setup-------------------------------------

# Define the port Remove comments when you run experiment
port = serial.Serial('/dev/tty.usbserial-DN2Q03LO', 115200) 

def trigger(code):
   port.write(code.to_bytes(1, 'big'))
   print('trigger sent {}'.format(code))

# dummy trigger:
# def trigger(code):
#     print("trigger: ", code)

#----Server-setup-----------------------------------
app = Flask(__name__)
clients = []
clients_lock = threading.Lock()

# Push_event converts python dict to json string in SSE format. 
# Puts data in connected client's cue
def push_event(data):
    payload = f"data: {json.dumps(data)}\n\n"
    with clients_lock:
        for q in clients:
            q.put(payload)

# Key press handling
key_event = threading.Event()
last_key = {"key": None}

@app.route("/keypress", methods=["POST"])
def keypress():
    data = request.get_json()
    last_key["key"] = data.get("key")
    print(f"Keypress received: {last_key['key']}")
    print(f"Setting key_event")
    key_event.set()
    print(f"key_event set, is_set: {key_event.is_set()}")
    return jsonify({"ok": True})

def waitForKey(timeout=None):
    key_event.clear()
    key_event.wait(timeout=timeout)
    key = last_key["key"]
    key_event.clear()
    return key

# Pleasure scale handling
rating_event = threading.Event()
last_rating = {"value": None}

@app.route("/rating", methods=["POST"])
def rating():
    data = request.get_json()
    last_rating["value"] = data.get("rating")
    print(f"Rating received: {last_rating['value']}")
    rating_event.set()
    return jsonify({"ok": True})

def waitForRating():
    rating_event.clear()
    rating_event.wait()
    rating = last_rating["value"]
    rating_event.clear()
    return rating

# The stream that the browser connects to. Techinal stuff...
@app.route("/stream")
def stream():
    q = queue.Queue()
    with clients_lock:
        clients.append(q)
    def generate():
        try:
            while True:
                yield q.get()
        except GeneratorExit:
            with clients_lock:
                clients.remove(q)
    return Response(generate(), 
                    mimetype="text/event-stream", 
                    headers={"Cache-Control": "no-cache"})

@app.route("/")
def index():
    return send_from_directory(".", "index.html")

@app.route("/<path:filename>")
def static_files(filename):
    return send_from_directory(".", filename)

# HTTP endpoint that recieves stimuli from experiment code
@app.route("/send", methods=["POST"])
def send_route():
    push_event(request.get_json())
    return jsonify({"ok": True})

# Routes to handle messages from JS about when the animation finishes.
animation_event = threading.Event()

@app.route("/animation-done", methods=["POST"])
def animation_done():
    animation_event.set()
    return jsonify({"ok": True})

def waitForAnimation():
    animation_event.clear()
    animation_event.wait()

partial_stop_event = threading.Event()

@app.route("/partial-stop", methods=["POST"])
def partial_stop():
    partial_stop_event.set()
    return jsonify({"ok": True})

def waitForPartialStop():
    partial_stop_event.clear()
    partial_stop_event.wait()

# Starting the server in a background thread.
threading.Thread(
    target=lambda: app.run(port=8000, threaded=True),
    daemon=True
).start()

#----Configure-----------------
try:
    from config import *
except ImportError:
    print("ERROR: Could not import config.py. Please ensure config.py exists in the same directory.")
    core.quit()

if not os.path.isdir(saveFolder): 
    os.makedirs(saveFolder)

#----Functions----------------
def send(data):
    requests.post("http://localhost:8000/send", json=data)

class slotMachineTask:
    def __init__(self, subject_id):
        self.subject_id = subject_id
        self.results = []
        # Values that are reset per block
        self.current_balance = config.start_balance
        self.block_number = 0
        self.trial_number = 0

        # Values that stay the same across blocks
        self.global_balance = 0

        self.xpos = 0
        self.ypos = 0

    def trialType(self, reel_stop):
        if reel_stop[0] == reel_stop[1] == reel_stop[2]:
            return "win"
        elif reel_stop[0] == reel_stop[1] != reel_stop[2]:
            return "near_miss"
        else:
            return "miss"

    def showInstructions(self):
        pass

    def runTrial(self, trial_data, reel_stop, auto):                                             
        self.trial_number += 1
        
                                                                                            # Decide partial stop trigger code for trial
        if auto and self.trialType(reel_stop) == "win":                                     # auto partial_stop_win
             partial_stop_trigger_code = 121
        elif not auto and self.trialType(reel_stop) == "win":                               # manual partial_stop_win
             partial_stop_trigger_code = 221
        elif auto and self.trialType(reel_stop) == "near_miss":                              # auto partial_stop_near_miss
             partial_stop_trigger_code = 122
        elif not auto and self.trialType(reel_stop) == "near_miss":                          # manual partial_stop_near_miss
             partial_stop_trigger_code = 222
        elif auto and self.trialType(reel_stop) == "miss":                                     # auto partial_stop_miss
             partial_stop_trigger_code = 123
        elif not auto and self.trialType(reel_stop) == "miss":                               # manual partial_stop_miss
             partial_stop_trigger_code = 223


                                                                                            # Decide full stop trigger code for trial
        if auto and self.trialType(reel_stop) == "win":                                     # auto full_stop_win
             full_stop_trigger_code = 131
        elif not auto and self.trialType(reel_stop) == "win":                               # manual full_stop_win
             full_stop_trigger_code = 231
        elif auto and self.trialType(reel_stop) == "near_miss":                              # auto full_stop_near_miss
             full_stop_trigger_code = 132
        elif not auto and self.trialType(reel_stop) == "near_miss":                          # manual full_stop_near_miss
             full_stop_trigger_code = 232
        elif auto and self.trialType(reel_stop) == "miss":                                     # auto full_stop_miss
             full_stop_trigger_code = 133
        elif not auto and self.trialType(reel_stop) == "miss":                               # manual full_stop_miss
             full_stop_trigger_code = 233

        if auto:                                                                            # If auto trial, send trial to frontend
            time.sleep(between_trial_wait)
            self.spins_left -= 1
            send({"type": "spins-left", "spins_left": self.spins_left})
            send({"type": "roll", "targets": reel_stop})
            trigger(11)
            trial_data['RT'] = None
        else:                                                                                # If trial is not auto, wait for key response
            t_start = time.time()
            key = waitForKey()
            response_time = time.time() - t_start

            if key in ansKeys:
                self.spins_left -= 1
                send({"type": "spins-left", "spins_left": self.spins_left})
                send({"type": "roll", "targets": reel_stop})
                trigger(21)
                trial_data['RT'] = response_time

            if key in quitKeys:
                core.quit()
            
            trial_data['RT'] = response_time
        if self.trialType(reel_stop) == "win":                                              # Update current balance
            self.current_balance += win_price
        
                                                                                             # Add trial values to trial dict
        trial_data['Block_number'] = self.block_number
        trial_data['Block_type'] = str(auto)
        trial_data['Trial_number'] = self.trial_number
        trial_data['Trial_type'] = self.trialType(reel_stop)
        trial_data['Balance'] = self.current_balance
        trial_data['Block_pleasure'] = None
        
        self.results.append(trial_data) 
        waitForPartialStop()                  
        trigger(partial_stop_trigger_code)    
        waitForAnimation()                                                                  # Waits till js animation is done
        trigger(full_stop_trigger_code)
        send({"type": "balance", "balance": self.current_balance})
        
                                                                  # Push results to Results list

    def runBlock(self, auto, distribution_key_index, end_sequence_type):                                                 
        if auto:
            accept_extra_spins_trigger_code = 101
            pleasure_rating_1_trigger_code = 191
        elif not auto:
            accept_extra_spins_trigger_code = 201
            pleasure_rating_1_trigger_code = 291

        distribution_key = config.main_trials_distribution_keys[distribution_key_index]
        
        self.trial_number = 0                                                                   # Reset trial number
        self.block_number += 1                                                                  # Increase block number
        send({"type": "block-start", "block_number": self.block_number})                        # Update blocknumber
        self.current_balance = config.start_balance                                             # Reset current balance
        self.spins_left = config.block_size + config.end_seq_length
        

        send({"type": "balance", "balance": self.current_balance})
        send({"type": "spins-left", "spins_left": self.spins_left})

        trials = trial_generator.generateTrials(distribution_key)
        end_sequence = trial_generator.generateEndSequence(end_sequence_type)
        
        if auto:
            send({"type": "scene", "name": "instruction-auto"}) 

        elif not auto:  
            send({"type": "scene", "name": "instruction-manual"}) 
        
        time.sleep(instruction_wait)

        send({"type": "scene", "name": "slots"})                                                # Switch to slot scene

        for trial in trials:
            if auto:                                                                            # On manual trials there is no inbetween wait
                self.runTrial({}, trial, auto)
            else:
                self.runTrial({}, trial, auto)
        
        for trial in end_sequence:                                                             # Run end-sequence
            self.runTrial({},trial, auto)   

        time.sleep(1)
        send({"type": "scene", "name": "extra-spins?"})                                         # Set scene to "extra spins?"

        extra_spins = trial_generator.generateExtraSpins()
        while True:
            key = waitForKey()
            print(f"Extra spins key received: '{key}'")
            if key in ('y', 'n'):
                break
        
        if key == 'y':
            trigger(accept_extra_spins_trigger_code)
            self.current_balance -= config.extra_spins_cost
            self.current_balance += config.extra_spins_amount
            self.spins_left = 5
            send({"type": "spins-left", "spins_left": self.spins_left})
            send({"type": "balance", "balance": self.current_balance})
            send({"type": "scene", "name": "slots"})
            time.sleep(1)
            for trial in extra_spins:
                self.runTrial({}, trial, auto)
        else:
            trigger(accept_extra_spins_trigger_code+1)
        
        time.sleep(0.5)
        self.global_balance += self.current_balance

        # Show current global balance scene
        send({"type": "block-start", "block_number": self.block_number}) 
        send({"type": "global_balance", "global_balance": self.global_balance})
        send({"type": "scene", "name": "global-balance"})
        time.sleep(5)

        
        send({"type": "scene", "name": "pleasure-rating"})
        block_pleasure = waitForRating()
        trigger(pleasure_rating_1_trigger_code + block_pleasure - 1)
        print(f"Block pleasure rating: {block_pleasure}")

        # # add rating to all trials in this block
        for trial_data in self.results:
            if trial_data['Block_number'] == self.block_number:
                trial_data['Block_pleasure'] = block_pleasure
        
        time.sleep(1)
    

    def runExperiment(self):
        # Wait while showing introduction
        block_types = []
        for x,y,z in zip(config.trial_auto, config.distribution_key_indecies, config.end_sequence_type):
            block_types.append((x,y,z))

        waitForKey()

        for block_type in block_types:
            x,y,z = block_type
            self.runBlock(x,y,z)
        
        send({"type": "global_balance", "global_balance": self.global_balance})
        send({"type": "scene", "name": "exit-scene"})
        time.sleep(1)
        self.saveResults()



    def saveResults(self):
        #Set up save .csv function
        saveFile = saveFolder+'/subject_' +str(subjectID)+'.csv'              # Filename for save-data
        csvWriter = csv.writer(open(saveFile, 'w', newline=''), delimiter=';').writerow     # The writer function to csv
        csvWriter(dataCategories) 

        for trial in self.results:
            csvWriter([trial[category] for category in dataCategories])


#----Run--experiment--------
exp = slotMachineTask(subjectID)
time.sleep(3)
exp.runExperiment()
# exp.runBlock(True, 3, "win")


# switch to slots and roll
# exp.runBlock(True, config.main_trials_distribution_keys[0], "win")
# send({"type": "result", "result": exp.results})
# exp.results = [{'Block_number': 1, 'Block_type': "True" ,'Trial_number': 2, 'Trial_type': "miss", 'RT': 2, 'Block_pleasure': 4, 'Balance': 32}]
# exp.saveResults()
#exp.runBlock(True, config.main_trials_distribution_keys[0], "win")
# send({"type": "result", "result": exp.results})



while True:
    time.sleep(1)