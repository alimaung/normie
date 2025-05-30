from flask import Flask, render_template, request, jsonify
import subprocess

app = Flask(__name__)

# Paths to scripts
SCRIPT_1 = "cpu_monitor.py"
SCRIPT_2 = "random_number.py"

# Store subprocesses
processes = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/toggle', methods=['POST'])
def toggle_script():
    data = request.json
    script = data.get("script")
    
    if script in processes:
        # Stop the script
        processes[script].terminate()
        processes[script].wait()
        del processes[script]
        return jsonify({"status": "stopped"})
    else:
        # Start the script
        processes[script] = subprocess.Popen(["python", script])
        return jsonify({"status": "running"})

@app.route('/status')
def status():
    # Return the status of all scripts
    status = {}
    for script, proc in processes.items():
        status[script] = "running"
    return jsonify(status)

if __name__ == '__main__':
    app.run(debug=True)
