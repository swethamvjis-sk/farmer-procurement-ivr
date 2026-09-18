# =========================================================
# FARMER PROCUREMENT SYSTEM - FLASK BACKEND
# This is the "brain" - the HTML page in templates/index.html
# talks to this server to look up farmers, check prices, and
# create bookings. Data is saved to bookings.json so it
# survives restarts.
# =========================================================
from flask import Flask, request, jsonify, render_template_string
import json
import os

app = Flask(__name__)

# ---------------------------------------------------------
# The entire frontend (HTML + CSS + JS) lives here as one
# big string, so this single file is everything you need -
# no separate templates folder required.
# ---------------------------------------------------------
INDEX_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>AgriStack Procurement Line</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,400;8..60,600;8..60,700&family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@500;600&display=swap" rel="stylesheet">
<style>
  :root{
    --green-deep:#2D5233; --green-soft:#3E6B47; --gold:#C08A28; --gold-soft:#E4C77E;
    --parchment:#F6F2E7; --parchment-dim:#EDE6D4; --ink:#1E1E1E; --ink-soft:#5B5648;
    --clay:#B23A32; --line:#D8CFB6;
  }
  *{box-sizing:border-box;}
  body{
    margin:0; min-height:100vh;
    background: radial-gradient(circle at 15% 10%, rgba(45,82,51,0.08), transparent 45%),
                radial-gradient(circle at 90% 85%, rgba(192,138,40,0.10), transparent 45%),
                var(--parchment);
    font-family:'IBM Plex Sans', sans-serif; color:var(--ink);
    display:flex; align-items:flex-start; justify-content:center; padding:48px 20px;
  }
  .stage{ display:flex; gap:40px; align-items:flex-start; flex-wrap:wrap; max-width:920px; }
  .label-block{ width:100%; text-align:center; margin-bottom:8px; }
  .label-block h1{ font-family:'Source Serif 4', serif; font-size:28px; font-weight:600; color:var(--green-deep); margin:0 0 6px 0; }
  .label-block p{ margin:0; color:var(--ink-soft); font-size:14.5px; }

  .phone{ width:300px; height:600px; background:linear-gradient(180deg,#25482c,var(--green-deep));
    border-radius:36px; padding:14px; box-shadow:0 20px 40px rgba(45,82,51,0.25), inset 0 0 0 1px rgba(255,255,255,0.06); position:relative; }
  .phone-notch{ position:absolute; top:14px; left:50%; transform:translateX(-50%); width:90px; height:16px; background:#173420; border-radius:10px; }
  .screen{ background:var(--parchment); height:100%; border-radius:24px; display:flex; flex-direction:column; overflow:hidden; padding-top:30px; }

  .call-card{ flex:1; display:flex; flex-direction:column; align-items:center; justify-content:center; padding:20px; text-align:center; gap:6px; }
  .call-eyebrow{ font-size:12px; letter-spacing:0.02em; color:var(--ink-soft); }
  .call-number{ font-family:'IBM Plex Mono', monospace; font-size:26px; font-weight:600; color:var(--green-deep); margin:6px 0 2px 0; }
  .call-sub{ font-size:13px; color:var(--ink-soft); max-width:220px; line-height:1.4; }
  .call-status{ font-size:13px; color:var(--gold); font-weight:600; min-height:18px; margin-top:10px; }

  .call-btn{ margin-top:22px; width:64px; height:64px; border-radius:50%; background:var(--green-deep); border:none; color:#fff;
    font-size:24px; cursor:pointer; box-shadow:0 8px 18px rgba(45,82,51,0.35); transition:transform 0.15s ease, background 0.15s ease; }
  .call-btn:hover{ transform:scale(1.06); background:var(--green-soft); }
  .call-btn:active{ transform:scale(0.96); }
  .call-btn[disabled]{ opacity:0.5; cursor:default; transform:none; }

  .transcript-wrap{ flex:1; display:none; flex-direction:column; min-height:0; }
  .call-topbar{ display:flex; align-items:center; justify-content:space-between; padding:10px 16px; border-bottom:1px solid var(--line); background:var(--parchment-dim); }
  .call-topbar .who{ font-size:13px; font-weight:600; color:var(--green-deep); }
  .call-topbar .timer{ font-family:'IBM Plex Mono', monospace; font-size:12px; color:var(--ink-soft); }
  .end-btn{ border:none; background:var(--clay); color:#fff; font-size:11px; font-weight:600; padding:5px 10px; border-radius:14px; cursor:pointer; }

  .transcript{ flex:1; overflow-y:auto; padding:14px; display:flex; flex-direction:column; gap:10px; }
  .bubble{ max-width:88%; padding:9px 12px; border-radius:12px; font-size:13px; line-height:1.42; }
  .bubble.ivr{ align-self:flex-start; background:#fff; border:1px solid var(--line); border-bottom-left-radius:3px; }
  .bubble.you{ align-self:flex-end; background:var(--green-deep); color:#fff; border-bottom-right-radius:3px; }
  .bubble.sms{ align-self:center; background:var(--gold-soft); border:1px solid var(--gold); font-size:12.5px; text-align:left; white-space:pre-line; }

  .input-row{ display:flex; gap:6px; padding:10px 12px 14px 12px; border-top:1px solid var(--line); background:var(--parchment-dim); }
  .input-row input{ flex:1; border:1px solid var(--line); border-radius:10px; padding:8px 10px; font-size:13px; font-family:'IBM Plex Sans', sans-serif; background:#fff; }
  .input-row button{ border:none; background:var(--green-deep); color:#fff; border-radius:10px; padding:0 14px; font-weight:600; font-size:13px; cursor:pointer; }
  .keypad-row{ display:flex; flex-wrap:wrap; gap:6px; padding:0 12px 12px 12px; background:var(--parchment-dim); }
  .key{ flex:1; min-width:70px; border:1px solid var(--line); background:#fff; border-radius:10px; padding:8px 6px; font-size:12px; font-weight:600; color:var(--green-deep); cursor:pointer; text-align:center; }
  .key:hover{ background:var(--parchment); }

  .side{ flex:1; min-width:320px; }
  .dash-card{ background:#fff; border:1px solid var(--line); border-radius:16px; padding:18px 20px; box-shadow:0 12px 30px rgba(30,30,30,0.06); }
  .dash-card h2{ font-family:'Source Serif 4', serif; font-size:18px; margin:0 0 4px 0; color:var(--green-deep); }
  .dash-card p.hint{ margin:0 0 14px 0; font-size:13px; color:var(--ink-soft); }
  table{ width:100%; border-collapse:collapse; font-size:12.5px; }
  th,td{ text-align:left; padding:7px 6px; border-bottom:1px solid var(--line); }
  th{ color:var(--ink-soft); font-weight:600; font-size:11.5px; text-transform:uppercase; letter-spacing:0.03em; }
  .status-pill{ display:inline-block; padding:2px 8px; border-radius:10px; font-size:11px; font-weight:600; }
  .status-pill.Confirmed{ background:#E3EFE4; color:var(--green-deep); }
  .status-pill.Waitlisted{ background:#F6E4C9; color:var(--gold); }
  .empty-row{ color:var(--ink-soft); font-size:13px; padding:14px 4px; }
  .server-tag{ font-size:11.5px; color:var(--ink-soft); text-align:center; margin-top:10px; }
  .server-tag b{ color:var(--green-deep); }
</style>
</head>
<body>

<div class="stage">
  <div class="label-block">
    <h1>Farmer Procurement Line</h1>
    <p>Connected live to the Python (Flask) backend — real requests, real responses</p>
  </div>

  <div class="phone">
    <div class="phone-notch"></div>
    <div class="screen">
      <div class="call-card" id="idleCard">
        <div class="call-eyebrow">Toll-free · works on any phone</div>
        <div class="call-number">1800-419-2026</div>
        <div class="call-sub">Dial to check crop prices, book a pickup slot, or track your procurement status.</div>
        <div class="call-status" id="callStatus">&nbsp;</div>
        <button class="call-btn" id="callBtn" title="Call">📞</button>
      </div>

      <div class="transcript-wrap" id="callView">
        <div class="call-topbar">
          <span class="who">AgriStack Procurement Line</span>
          <span class="timer" id="callTimer">00:00</span>
          <button class="end-btn" id="endBtn">End Call</button>
        </div>
        <div class="transcript" id="transcript"></div>
        <div class="input-row" id="inputRow" style="display:none;">
          <input type="text" id="textInput" placeholder="Type here...">
          <button id="sendBtn">Send</button>
        </div>
        <div class="keypad-row" id="keypadRow" style="display:none;"></div>
      </div>
    </div>
  </div>

  <div class="side">
    <div class="dash-card">
      <h2>Procurement Dashboard</h2>
      <p class="hint">Live bookings from the Flask server — this is what the centre officer sees.</p>
      <table>
        <thead><tr><th>Token</th><th>Farmer</th><th>Crop</th><th>Qty (t)</th><th>Window</th><th>Status</th></tr></thead>
        <tbody id="bookingsBody">
          <tr><td colspan="6" class="empty-row">No bookings yet — make a call to create one.</td></tr>
        </tbody>
      </table>
      <div class="server-tag">Data served from <b>bookings.json</b> on your local Flask server</div>
    </div>
  </div>
</div>

<script>
let callSeconds = 0;
let timerInterval = null;

const idleCard = document.getElementById('idleCard');
const callView = document.getElementById('callView');
const callBtn = document.getElementById('callBtn');
const callStatus = document.getElementById('callStatus');
const transcript = document.getElementById('transcript');
const inputRow = document.getElementById('inputRow');
const textInput = document.getElementById('textInput');
const sendBtn = document.getElementById('sendBtn');
const keypadRow = document.getElementById('keypadRow');
const endBtn = document.getElementById('endBtn');
const callTimer = document.getElementById('callTimer');

function addBubble(text, type){
  const b = document.createElement('div');
  b.className = 'bubble ' + type;
  b.textContent = text;
  transcript.appendChild(b);
  transcript.scrollTop = transcript.scrollHeight;
  return b;
}

function clearInputArea(){
  inputRow.style.display = 'none';
  keypadRow.style.display = 'none';
  keypadRow.innerHTML = '';
  textInput.value = '';
}

function showTextInput(placeholder, onSubmit){
  clearInputArea();
  inputRow.style.display = 'flex';
  textInput.placeholder = placeholder;
  textInput.focus();
  const handler = () => {
    const val = textInput.value.trim();
    if(!val) return;
    addBubble(val, 'you');
    clearInputArea();
    sendBtn.removeEventListener('click', handler);
    onSubmit(val);
  };
  sendBtn.addEventListener('click', handler);
  textInput.onkeydown = (e) => { if(e.key === 'Enter') handler(); };
}

function showKeypad(options, onSubmit){
  clearInputArea();
  keypadRow.style.display = 'flex';
  options.forEach(opt => {
    const btn = document.createElement('button');
    btn.className = 'key';
    btn.textContent = opt.key + '. ' + opt.label;
    btn.onclick = () => {
      addBubble('Pressed ' + opt.key, 'you');
      clearInputArea();
      onSubmit(opt.key);
    };
    keypadRow.appendChild(btn);
  });
}

function startTimer(){
  callSeconds = 0;
  timerInterval = setInterval(() => {
    callSeconds++;
    const m = String(Math.floor(callSeconds/60)).padStart(2,'0');
    const s = String(callSeconds%60).padStart(2,'0');
    callTimer.textContent = m + ':' + s;
  }, 1000);
}
function stopTimer(){ clearInterval(timerInterval); }

// ---------- talk to the Flask backend ----------
async function fetchFarmer(enrolmentNo){
  const res = await fetch('/api/farmer/' + encodeURIComponent(enrolmentNo));
  if(!res.ok) return null;
  return await res.json();
}
async function fetchPrice(crop){
  const res = await fetch('/api/price/' + encodeURIComponent(crop));
  return await res.json();
}
async function postBooking(enrolmentNo, qty, windowKey){
  const res = await fetch('/api/book', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({enrolment_no: enrolmentNo, qty: qty, window: windowKey})
  });
  return await res.json();
}
async function refreshDashboard(){
  const res = await fetch('/api/bookings');
  const bookings = await res.json();
  const body = document.getElementById('bookingsBody');
  if(bookings.length === 0){
    body.innerHTML = '<tr><td colspan="6" class="empty-row">No bookings yet — make a call to create one.</td></tr>';
    return;
  }
  body.innerHTML = bookings.map(b => `
    <tr>
      <td>${b.token}</td><td>${b.name}</td><td>${b.crop}</td>
      <td>${b.qty}</td><td>${b.window}</td>
      <td><span class="status-pill ${b.status}">${b.status}</span></td>
    </tr>`).join('');
}

// ---------- call flow ----------
callBtn.addEventListener('click', () => {
  callBtn.disabled = true;
  callStatus.textContent = 'Dialling...';
  setTimeout(() => { callStatus.textContent = 'Connecting...'; }, 700);
  setTimeout(() => {
    idleCard.style.display = 'none';
    callView.style.display = 'flex';
    transcript.innerHTML = '';
    startTimer();
    addBubble("Welcome to the AgriStack Procurement Line. Please enter your enrolment number.", 'ivr');
    showTextInput('Enter enrolment number...', handleEnrolment);
  }, 1500);
});

function endCall(){
  stopTimer();
  callBtn.disabled = false;
  callStatus.textContent = '';
  callView.style.display = 'none';
  idleCard.style.display = 'flex';
  clearInputArea();
}
endBtn.addEventListener('click', endCall);

async function handleEnrolment(value){
  const profile = await fetchFarmer(value);
  if(!profile || !profile.found){
    addBubble("We could not find that enrolment number. Please contact your local agent.", 'ivr');
    setTimeout(endCall, 2200);
    return;
  }
  addBubble(`Hello ${profile.name} from ${profile.village}.`, 'ivr');
  setTimeout(() => {
    addBubble(`Your registered crop: ${profile.crop}, estimated ${profile.tonnes} tonnes.`, 'ivr');
    setTimeout(() => {
      addBubble("Please choose an option:", 'ivr');
      showKeypad([
        {key:'1', label:'Book Pickup'},
        {key:'2', label:'Check Price'},
        {key:'3', label:'Speak to Agent'},
      ], (choice) => handleMenu(choice, value, profile));
    }, 500);
  }, 500);
}

function handleMenu(choice, enrolmentNo, profile){
  if(choice === '1'){
    addBubble("Confirm actual quantity in tonnes:", 'ivr');
    showTextInput('e.g. 5', (qty) => {
      addBubble("Choose pickup window:", 'ivr');
      showKeypad([
        {key:'1', label:'Morning'},
        {key:'2', label:'Midday'},
        {key:'3', label:'Afternoon'},
      ], (winChoice) => finishBooking(enrolmentNo, profile, qty, winChoice));
    });
  } else if(choice === '2'){
    fetchPrice(profile.crop).then(data => {
      addBubble(`Current price for ${data.crop} is ₹${data.price} per quintal at your nearest mandi.`, 'ivr');
      setTimeout(endCall, 3000);
    });
  } else {
    addBubble("Connecting you to an agent...", 'ivr');
    setTimeout(endCall, 2200);
  }
}

async function finishBooking(enrolmentNo, profile, qty, winChoice){
  const windows = {'1':'Morning','2':'Midday','3':'Afternoon'};
  const win = windows[winChoice] || 'Morning';

  const booking = await postBooking(enrolmentNo, qty, win);
  await refreshDashboard();

  addBubble(
    booking.status === 'Confirmed'
      ? `Booking confirmed. Your token is ${booking.token} for the ${win} window.`
      : `The ${win} window is full — you've been added to the waitlist.`,
    'ivr'
  );

  setTimeout(() => {
    addBubble(
      `Dear ${profile.name},\nBooking Ref: ${booking.ref}   Token: ${booking.token}\nWindow: ${win}   Status: ${booking.status}\nCrop: ${profile.crop}   Qty: ${qty}t`,
      'sms'
    );
    setTimeout(endCall, 3200);
  }, 700);
}

// Load dashboard on page open
refreshDashboard();
</script>
</body>
</html>
"""


BOOKINGS_FILE = "bookings.json"
SLOT_CAPACITY = 5  # max farmers per time window

# ---------------------------------------------------------
# Fake AgriStack database (in real life this already exists
# in the government system - we just look it up)
# ---------------------------------------------------------
AGRISTACK = {
    "1001": {"name": "Ramesh Kumar", "village": "Kheda", "crop": "Paddy", "tonnes": 5},
    "1002": {"name": "Sita Devi", "village": "Rampur", "crop": "Wheat", "tonnes": 3},
    "1003": {"name": "Mohan Lal", "village": "Bhiarpur", "crop": "Maize", "tonnes": 7},
}

PRICES = {"Paddy": 2310, "Wheat": 2125, "Maize": 1962}


# ---------------------------------------------------------
# Helpers to load/save bookings from a simple JSON file
# (same idea as the pickle file in your earlier project,
# just in a human-readable format)
# ---------------------------------------------------------
def load_bookings():
    if not os.path.exists(BOOKINGS_FILE):
        return []
    with open(BOOKINGS_FILE, "r") as f:
        return json.load(f)


def save_bookings(bookings):
    with open(BOOKINGS_FILE, "w") as f:
        json.dump(bookings, f, indent=2)


def count_in_window(bookings, window):
    return sum(1 for b in bookings if b["window"] == window)


# ---------------------------------------------------------
# Route: serve the frontend page
# ---------------------------------------------------------
@app.route("/")
def home():
    return render_template_string(INDEX_HTML)


# ---------------------------------------------------------
# API: look up a farmer by enrolment number
# ---------------------------------------------------------
@app.route("/api/farmer/<enrolment_no>")
def get_farmer(enrolment_no):
    profile = AGRISTACK.get(enrolment_no)
    if not profile:
        return jsonify({"found": False}), 404
    return jsonify({"found": True, **profile})


# ---------------------------------------------------------
# API: check market price for a crop
# ---------------------------------------------------------
@app.route("/api/price/<crop>")
def get_price(crop):
    price = PRICES.get(crop, 2000)
    return jsonify({"crop": crop, "price": price})


# ---------------------------------------------------------
# API: create a booking
# ---------------------------------------------------------
@app.route("/api/book", methods=["POST"])
def book_pickup():
    data = request.get_json()
    enrolment_no = data.get("enrolment_no")
    qty = data.get("qty")
    window = data.get("window")

    profile = AGRISTACK.get(enrolment_no)
    if not profile:
        return jsonify({"error": "Farmer not found"}), 404

    bookings = load_bookings()
    count = count_in_window(bookings, window)
    status = "Waitlisted" if count >= SLOT_CAPACITY else "Confirmed"
    token = count + 1
    booking_ref = f"BK{len(bookings) + 1:04d}"

    new_booking = {
        "token": token,
        "name": profile["name"],
        "crop": profile["crop"],
        "qty": qty,
        "window": window,
        "status": status,
        "ref": booking_ref,
    }
    bookings.append(new_booking)
    save_bookings(bookings)

    return jsonify(new_booking)


# ---------------------------------------------------------
# API: get all bookings (for the dashboard)
# ---------------------------------------------------------
@app.route("/api/bookings")
def get_bookings():
    return jsonify(load_bookings())


if __name__ == "__main__":
    app.run(debug=True, port=5000, use_reloader=False)
