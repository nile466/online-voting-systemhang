"""
Simple Online Voting System — Python Flask Backend
Run: pip install flask && python voting_app.py
Visit: http://127.0.0.1:5000
"""

from flask import Flask, request, jsonify, render_template_string
from datetime import datetime

app = Flask(__name__)

# ── In-memory data store ──────────────────────────────────────────────────────
poll = {
    "title": "Student Council Election 2025",
    "open": True,
    "created_at": datetime.now().isoformat(),
}

candidates = [
    {"id": 1, "name": "Aryan Sharma",  "party": "Development Alliance",   "votes": 0},
    {"id": 2, "name": "Priya Mehta",   "party": "Student Welfare Party",   "votes": 0},
    {"id": 3, "name": "Rahul Verma",   "party": "Progress Front",          "votes": 0},
]

voted_ips = set()          # simple IP-based duplicate prevention
next_id   = 4

# ── HTML template (single-file app) ──────────────────────────────────────────
HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Online Voting System</title>
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: system-ui, sans-serif; background: #f4f4f5; color: #18181b; min-height: 100vh; }
  .wrap { max-width: 660px; margin: 0 auto; padding: 2rem 1rem; }
  h1 { font-size: 1.5rem; font-weight: 600; margin-bottom: .25rem; }
  .meta { font-size: .85rem; color: #71717a; margin-bottom: 1.5rem; }
  .badge { display: inline-block; padding: 2px 10px; border-radius: 99px; font-size: .75rem; font-weight: 600; }
  .open   { background: #dcfce7; color: #166534; }
  .closed { background: #fef9c3; color: #854d0e; }
  .tabs { display: flex; gap: 4px; margin-bottom: 1.5rem; border-bottom: 1px solid #e4e4e7; }
  .tab { padding: 8px 16px; font-size: .9rem; cursor: pointer; border: none; background: none;
         border-bottom: 2px solid transparent; color: #71717a; }
  .tab.active { color: #18181b; border-bottom-color: #18181b; font-weight: 500; }
  .card { background: #fff; border: 1px solid #e4e4e7; border-radius: 12px;
          padding: 1rem 1.25rem; margin-bottom: .75rem; }
  .candidate { display: flex; align-items: center; gap: 12px; cursor: pointer; transition: border-color .15s; }
  .candidate:hover { border-color: #a1a1aa; }
  .candidate.selected { border-color: #3b82f6; border-width: 2px; }
  .avatar { width: 42px; height: 42px; border-radius: 50%; display: flex; align-items: center;
             justify-content: center; font-weight: 600; font-size: .85rem; flex-shrink: 0; }
  .info { flex: 1; }
  .cname { font-weight: 500; }
  .cparty { font-size: .8rem; color: #71717a; margin-top: 2px; }
  .radio { width: 18px; height: 18px; border-radius: 50%; border: 2px solid #d4d4d8;
           flex-shrink: 0; display: flex; align-items: center; justify-content: center; }
  .radio.on { border-color: #3b82f6; }
  .radio.on::after { content:''; width:8px; height:8px; border-radius:50%; background:#3b82f6; }
  .btn { width: 100%; padding: 10px; font-size: .95rem; font-weight: 500; border-radius: 8px;
         border: 1px solid #d4d4d8; background: transparent; cursor: pointer; transition: background .15s; margin-top: 4px; }
  .btn:hover:not(:disabled) { background: #f4f4f5; }
  .btn:disabled { opacity: .4; cursor: not-allowed; }
  .btn.danger { border-color: #fca5a5; color: #b91c1c; }
  .btn.danger:hover { background: #fef2f2; }
  .metrics { display: grid; grid-template-columns: repeat(3,1fr); gap: 10px; margin-bottom: 1.5rem; }
  .metric { background: #f4f4f5; border-radius: 8px; padding: 12px; text-align: center; }
  .mval { font-size: 1.4rem; font-weight: 600; }
  .mlbl { font-size: .75rem; color: #71717a; margin-top: 2px; }
  .bar-row { display: flex; align-items: center; gap: 10px; margin-bottom: 10px; }
  .bar-name { width: 130px; font-size: .85rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .bar-track { flex: 1; height: 8px; background: #e4e4e7; border-radius: 4px; overflow: hidden; }
  .bar-fill  { height: 100%; border-radius: 4px; transition: width .4s ease; }
  .bar-pct  { width: 36px; font-size: .8rem; text-align: right; color: #71717a; }
  .bar-cnt  { width: 36px; font-size: .8rem; text-align: right; color: #a1a1aa; }
  .input { width: 100%; padding: 7px 10px; font-size: .875rem; border: 1px solid #d4d4d8;
           border-radius: 6px; background: transparent; color: inherit; }
  .row { display: flex; gap: 8px; align-items: center; margin-bottom: 10px; }
  .sbtn { padding: 7px 14px; font-size: .8rem; border: 1px solid #d4d4d8; border-radius: 6px;
          background: transparent; cursor: pointer; white-space: nowrap; }
  .sbtn:hover { background: #f4f4f5; }
  .notice { font-size: .875rem; color: #71717a; padding: 12px; background: #f4f4f5;
            border-radius: 8px; text-align: center; }
  .success-notice { font-size: .875rem; color: #166534; padding: 12px;
                    background: #dcfce7; border-radius: 8px; text-align: center; margin-bottom: 12px; }
  .winner { padding: 12px 16px; border: 1px solid #86efac; border-radius: 8px;
            background: #f0fdf4; margin-bottom: 1rem; }
  .winner-lbl { font-size: .75rem; color: #166534; font-weight: 600; }
  .winner-name { font-size: 1rem; font-weight: 600; color: #166534; }
  .section-lbl { font-size: .75rem; font-weight: 600; color: #71717a;
                 letter-spacing: .05em; text-transform: uppercase; margin-bottom: 10px; }
  #toast { position: fixed; bottom: 1.5rem; left: 50%; transform: translateX(-50%);
           background: #18181b; color: #fff; padding: 8px 20px; border-radius: 8px;
           font-size: .875rem; display: none; z-index: 99; }
</style>
</head>
<body>
<div class="wrap" id="app"></div>
<div id="toast"></div>
<script>
const COLORS = ['#3b82f6','#10b981','#f97316','#ec4899','#84cc16','#f59e0b'];
const AV_BG  = ['#dbeafe','#d1fae5','#ffedd5','#fce7f3','#ecfccb','#fef3c7'];
const AV_FG  = ['#1e40af','#065f46','#9a3412','#9d174d','#365314','#78350f'];

let tab = 'vote', selected = null, voted = false;

function initials(n){ return n.split(' ').map(w=>w[0]).join('').slice(0,2).toUpperCase(); }
function esc(s){ return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;'); }
function toast(msg){ const t=document.getElementById('toast'); t.textContent=msg; t.style.display='block'; setTimeout(()=>t.style.display='none',2500); }

async function api(path, opts={}){
  const r = await fetch('/api'+path, opts);
  return r.json();
}

async function render(){
  const [pollData, cands] = await Promise.all([api('/poll'), api('/candidates')]);
  const total = cands.reduce((a,c)=>a+c.votes,0);
  const leader = total ? cands.reduce((a,b)=>b.votes>a.votes?b:a) : null;

  const header = `<h1>${esc(pollData.title)}</h1>
  <p class="meta">${cands.length} candidates &middot; ${total} votes &middot;
    <span class="badge ${pollData.open?'open':'closed'}">${pollData.open?'Open':'Closed'}</span></p>`;

  const tabs = `<div class="tabs">
    <button class="tab ${tab==='vote'?'active':''}" onclick="setTab('vote')">Ballot</button>
    <button class="tab ${tab==='results'?'active':''}" onclick="setTab('results')">Live results</button>
    <button class="tab ${tab==='admin'?'active':''}" onclick="setTab('admin')">Admin</button>
  </div>`;

  let body = '';
  if(tab==='vote'){
    if(!pollData.open){ body='<div class="notice">This poll is currently closed.</div>'; }
    else {
      if(voted) body+=`<div class="success-notice">Your vote has been recorded. Thank you!</div>`;
      cands.forEach((c,i)=>{
        const sel=selected===c.id;
        body+=`<div class="card candidate ${sel?'selected':''}" onclick="pick(${c.id})" ${voted?'style="cursor:default;pointer-events:none;opacity:.7"':''}>
          <div class="avatar" style="background:${AV_BG[i%6]};color:${AV_FG[i%6]}">${initials(c.name)}</div>
          <div class="info"><div class="cname">${esc(c.name)}</div><div class="cparty">${esc(c.party)}</div></div>
          <div class="radio ${sel?'on':''}"></div>
        </div>`;
      });
      body+=`<button class="btn" onclick="castVote()" ${(!selected||voted)?'disabled':''}>Cast vote</button>`;
    }
  } else if(tab==='results'){
    const sorted=[...cands].sort((a,b)=>b.votes-a.votes);
    if(leader&&!pollData.open) body+=`<div class="winner"><div class="winner-lbl">Winner</div><div class="winner-name">${esc(leader.name)}</div></div>`;
    body+=`<div class="metrics">
      <div class="metric"><div class="mval">${total}</div><div class="mlbl">Total votes</div></div>
      <div class="metric"><div class="mval">${cands.length}</div><div class="mlbl">Candidates</div></div>
      <div class="metric"><div class="mval">${leader?Math.round(leader.votes/total*100)+'%':'—'}</div><div class="mlbl">Leading share</div></div>
    </div><div class="section-lbl">Vote breakdown</div>`;
    sorted.forEach((c,i)=>{
      const pct=total?Math.round(c.votes/total*100):0;
      body+=`<div class="bar-row">
        <span class="bar-name">${esc(c.name)}</span>
        <div class="bar-track"><div class="bar-fill" style="width:${pct}%;background:${COLORS[i%6]}"></div></div>
        <span class="bar-pct">${pct}%</span>
        <span class="bar-cnt">${c.votes}v</span>
      </div>`;
    });
    if(!total) body+='<div class="notice">No votes cast yet.</div>';
  } else {
    body+=`<div class="section-lbl">Poll settings</div>
    <div class="card" style="margin-bottom:1rem">
      <div class="row">
        <input class="input" id="ptitle" value="${esc(pollData.title)}">
        <button class="sbtn" onclick="saveTitle()">Save</button>
      </div>
      <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap">
        <span style="font-size:.85rem;color:#71717a">Status:</span>
        <span class="badge ${pollData.open?'open':'closed'}">${pollData.open?'Open':'Closed'}</span>
        <button class="sbtn" onclick="togglePoll()">${pollData.open?'Close poll':'Open poll'}</button>
        <button class="sbtn danger" onclick="resetVotes()">Reset votes</button>
      </div>
    </div>
    <div class="section-lbl">Candidates</div>`;
    cands.forEach((c,i)=>{
      body+=`<div class="card" style="margin-bottom:8px">
        <div class="row">
          <div class="avatar" style="background:${AV_BG[i%6]};color:${AV_FG[i%6]};width:32px;height:32px;font-size:.75rem;flex-shrink:0">${initials(c.name)}</div>
          <input class="input" id="cn-${c.id}" value="${esc(c.name)}" onblur="updateCandidate(${c.id})">
          <input class="input" id="cp-${c.id}" value="${esc(c.party)}" onblur="updateCandidate(${c.id})" style="max-width:160px">
          <button class="sbtn danger" onclick="removeCandidate(${c.id})">Remove</button>
        </div>
      </div>`;
    });
    body+=`<div class="card">
      <div style="font-size:.85rem;color:#71717a;margin-bottom:10px">Add candidate</div>
      <div class="row">
        <input class="input" id="new-name" placeholder="Full name">
        <input class="input" id="new-party" placeholder="Party / affiliation">
        <button class="sbtn" onclick="addCandidate()">Add</button>
      </div>
    </div>`;
  }

  document.getElementById('app').innerHTML = header + tabs + body;
}

function setTab(t){ tab=t; render(); }
function pick(id){ if(!voted){ selected=id; render(); } }

async function castVote(){
  if(!selected||voted) return;
  const r = await api('/vote',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({candidate_id:selected})});
  if(r.success){ voted=true; toast('Vote cast!'); render(); } else { toast(r.error||'Could not cast vote'); }
}

async function saveTitle(){
  const t=document.getElementById('ptitle').value.trim();
  if(t){ await api('/poll',{method:'PATCH',headers:{'Content-Type':'application/json'},body:JSON.stringify({title:t})}); render(); }
}

async function togglePoll(){
  await api('/poll/toggle',{method:'POST'}); render();
}

async function resetVotes(){
  if(!confirm('Reset all votes?')) return;
  await api('/votes/reset',{method:'POST'}); voted=false; selected=null; toast('Votes reset'); render();
}

async function addCandidate(){
  const n=document.getElementById('new-name').value.trim();
  const p=document.getElementById('new-party').value.trim();
  if(!n) return;
  await api('/candidates',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:n,party:p||'Independent'})});
  render();
}

async function removeCandidate(id){
  const r=await api('/candidates/'+id,{method:'DELETE'});
  if(r.error) toast(r.error); else render();
}

async function updateCandidate(id){
  const n=document.getElementById('cn-'+id)?.value.trim();
  const p=document.getElementById('cp-'+id)?.value.trim();
  if(n) await api('/candidates/'+id,{method:'PATCH',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:n,party:p||'Independent'})});
}

render();
setInterval(()=>{ if(tab==='results') render(); }, 5000);
</script>
</body>
</html>"""


# ── REST API ──────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template_string(HTML)


@app.route("/api/poll")
def get_poll():
    return jsonify(poll)


@app.route("/api/poll", methods=["PATCH"])
def update_poll():
    data = request.get_json()
    if "title" in data:
        poll["title"] = data["title"]
    return jsonify(poll)


@app.route("/api/poll/toggle", methods=["POST"])
def toggle_poll():
    poll["open"] = not poll["open"]
    return jsonify(poll)


@app.route("/api/candidates")
def get_candidates():
    return jsonify(candidates)


@app.route("/api/candidates", methods=["POST"])
def add_candidate():
    global next_id
    data = request.get_json()
    if not data.get("name", "").strip():
        return jsonify({"error": "Name is required"}), 400
    c = {"id": next_id, "name": data["name"].strip(),
         "party": data.get("party", "Independent").strip(), "votes": 0}
    candidates.append(c)
    next_id += 1
    return jsonify(c), 201


@app.route("/api/candidates/<int:cid>", methods=["PATCH"])
def update_candidate(cid):
    c = next((x for x in candidates if x["id"] == cid), None)
    if not c:
        return jsonify({"error": "Not found"}), 404
    data = request.get_json()
    if "name" in data:
        c["name"] = data["name"].strip()
    if "party" in data:
        c["party"] = data["party"].strip()
    return jsonify(c)


@app.route("/api/candidates/<int:cid>", methods=["DELETE"])
def remove_candidate(cid):
    global candidates
    if len(candidates) <= 2:
        return jsonify({"error": "A poll needs at least 2 candidates"}), 400
    candidates = [c for c in candidates if c["id"] != cid]
    return jsonify({"success": True})


@app.route("/api/vote", methods=["POST"])
def cast_vote():
    if not poll["open"]:
        return jsonify({"error": "Poll is closed"}), 403

    # Basic IP-based duplicate prevention
    ip = request.remote_addr
    if ip in voted_ips:
        return jsonify({"error": "You have already voted"}), 403

    data = request.get_json()
    cid = data.get("candidate_id")
    c = next((x for x in candidates if x["id"] == cid), None)
    if not c:
        return jsonify({"error": "Invalid candidate"}), 400

    c["votes"] += 1
    voted_ips.add(ip)
    return jsonify({"success": True, "candidate": c})


@app.route("/api/votes/reset", methods=["POST"])
def reset_votes():
    for c in candidates:
        c["votes"] = 0
    voted_ips.clear()
    return jsonify({"success": True})


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Voting system running at http://127.0.0.1:5000")
    app.run(debug=True)
