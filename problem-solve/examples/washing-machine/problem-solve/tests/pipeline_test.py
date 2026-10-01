"""End to end test of phone_watch.py on SYNTHETIC data.

Writes 3 synthetic cycles (scenario B, hard rinse spins) in the pretty-printed
JSON shape termux-sensor prints, pipes them into phone_watch.py, and runs a
local HTTP server in place of ntfy.sh to catch the notification.
The ntfy.sh server itself could not be reached from this sandbox.
"""
import http.server, json, subprocess, sys, threading, os
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import vibration_test as v

got = []
class H(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        body = self.rfile.read(int(self.headers["Content-Length"])).decode()
        got.append((self.path, self.headers.get("Title"), body))
        self.send_response(200); self.end_headers()
    def log_message(self, *a): pass
srv = http.server.HTTPServer(("127.0.0.1", 0), H)
threading.Thread(target=srv.serve_forever, daemon=True).start()

rng = np.random.default_rng(3)
here = os.path.dirname(__file__)
for k in range(3):
    x, end = v.synth_cycle(rng, mid_spin_g=0.25)
    yz = rng.standard_normal((len(x), 2)) * 0.003 * 9.81
    lines = []
    for i in range(len(x)):
        lines.append(json.dumps({"FAKE Accelerometer": {"values": [float(x[i]), float(yz[i, 0]), 9.81 + float(yz[i, 1])]}}, indent=2))
    data = "\n".join(lines) + "\n"
    p = subprocess.run([sys.executable, os.path.join(here, "..", "phone_watch.py"), "--topic", "test-topic",
                        "--server", f"http://127.0.0.1:{srv.server_port}", "--fake-rate", str(v.FS)],
                       input=data, capture_output=True, text=True)
    print(f"cycle {k}: real end at {end:.0f}s ({end/60:.1f} min). script said: {p.stdout.strip() or p.stderr.strip()[-300:]}")
print("server received:", got)
