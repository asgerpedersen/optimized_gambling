from psychopy import core, visual, sound, event, gui, monitors
import threading, time, requests
import serial
from flask import Flask, Response, jsonify, request, send_from_directory
import queue, json
import os, csv

#----EEG--Setup-------------------------------------

# Define the port Remove comments when you run experiment
# port = serial.Serial('/dev/tty.usbserial-DN2Q03LO', 115200) 

# def trigger(code):
#    port.write(code.to_bytes(1, 'big'))
#    print('trigger sent {}'.format(code))

# dummy trigger:
def trigger(code):
    pass

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
        self.current_balance = 0
        self.block_number = 0
        self.trial_number = 0

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

    def runTrial(self, trial, reel_stop, auto):
        self.trial_number += 1

        if auto:                                                                            # If auto trial, send trial to frontend
            send({"type": "roll", "targets": reel_stop})
            trial['RT'] = None
        else:                                                                                # If trial is not auto, wait for key response
            t_start = time.time()
            key = waitForKey()
            response_time = time.time() - t_start

            if key in ansKeys:
                send({"type": "roll", "targets": reel_stop})
                trial['RT'] = response_time

            if key in quitKeys:
                core.quit()
            
            trial['RT'] = response_time
        if self.trialType(reel_stop) == "win":                                              # Update current balance
            self.current_balance += win_price
        
                                                                                             # Add trial values to trial dict
        trial['Block_number'] = self.block_number
        trial['Trial_number'] = self.trial_number
        trial['Trial_type'] = self.trialType(reel_stop)
        trial['Balance'] = self.current_balance
        trial['Block_pleasure'] = None

        self.results.append(trial)                                                           # Push results to Results list
            

    def runBlock(self):
        pass

    def runExperiment(self):
        pass

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



# show intro first
send({"type": "scene", "name": "scene-intro"})

# switch to slots and roll
send({"type": "scene", "name": "slots"})
time.sleep(2)
exp.runTrial({},[3,3,3], False)
time.sleep(7)
exp.runTrial({},[3,2,1], True)
send({"type": "result", "result": exp.results})

while True:
    time.sleep(1)