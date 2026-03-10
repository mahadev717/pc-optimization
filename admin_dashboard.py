# ADMIN DASHBOARD - Standalone Supabase Login Viewer
# Opens with login page (username: mahadev, password: mahadev)
# After login, shows all user login records from cloud database
# Build: pyinstaller --onefile --noconsole --name admin admin_dashboard.py

import http.server
import threading
import webbrowser
import json
import datetime
import socket
import io
import base64

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

LOCAL_IP = get_local_ip()

# ============================================================
# SUPABASE CONFIG
# ============================================================
SUPABASE_URL = "https://mvsvbcmwovyufyrgquwy.supabase.co"
SUPABASE_KEY = "sb_publishable_QWAKXmaByRRWl8kSqXPqRw_tJBdjB7h"

# Admin credentials
ADMIN_USER = "mahadev"
ADMIN_PASS = "1"

try:
    from supabase import create_client
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception:
    supabase = None

PORT = 5066
_authenticated = set()


def make_qr_base64(url):
    try:
        import qrcode
        qr = qrcode.QRCode(version=1, box_size=5, border=2)
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode("ascii")
    except Exception:
        return ""


def get_all_data():
    if not supabase:
        return {"users": [], "all_logins": [], "error": "Supabase not connected"}
    try:
        users_res = supabase.table("users").select("id, username, created_at").order("id").execute()
        logins_res = supabase.table("logins").select("*").order("id", desc=True).execute()
        users = users_res.data or []
        all_logins = logins_res.data or []
        enriched = []
        for u in users:
            uname = u["username"]
            u_logins = [l for l in all_logins if l.get("username") == uname]
            last = u_logins[0]["logged_at"] if u_logins else ""
            enriched.append({
                "id": str(u["id"]), "username": str(u["username"]),
                "created_at": str(u["created_at"]),
                "login_count": str(len(u_logins)), "last_login": str(last),
                "login_history": u_logins,
            })
        return {"users": enriched, "all_logins": all_logins}
    except Exception as e:
        return {"users": [], "all_logins": [], "error": str(e)}


def clear_logs():
    if supabase:
        supabase.table("logins").delete().neq("id", 0).execute()


# ============================================================
# LOGIN PAGE HTML
# ============================================================
LOGIN_HTML = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>ADMIN LOGIN</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');
  :root{--cyan:#00f3ff;--green:#39ff14;--red:#ff3c3c;--orange:#ff8800;--bg:#060a0e;--mono:'Share Tech Mono',monospace}
  *{box-sizing:border-box;margin:0;padding:0}
  body{background:var(--bg);color:var(--cyan);font-family:var(--mono);min-height:100vh;display:flex;align-items:center;justify-content:center}
  .login-box{border:1px solid rgba(0,243,255,.2);background:rgba(0,243,255,.03);backdrop-filter:blur(12px);padding:52px 44px;width:420px;text-align:center;box-shadow:0 0 60px rgba(0,243,255,.07)}
  .login-box h2{letter-spacing:7px;font-size:1rem;margin-bottom:5px;color:var(--cyan)}
  .login-box .sub{font-size:.55rem;letter-spacing:3px;color:var(--orange);margin-bottom:30px}
  .login-box input{width:100%;background:rgba(0,243,255,.05);border:1px solid rgba(0,243,255,.18);color:var(--cyan);font-family:var(--mono);font-size:.8rem;padding:12px 16px;margin-bottom:12px;outline:none;letter-spacing:2px}
  .login-box input:focus{border-color:var(--cyan);box-shadow:0 0 10px rgba(0,243,255,.15)}
  .login-box input::placeholder{color:rgba(0,243,255,.3)}
  .login-btn{width:100%;background:transparent;border:1px solid var(--green);color:var(--green);font-family:var(--mono);font-size:.75rem;letter-spacing:4px;padding:13px;cursor:pointer;transition:.2s;margin-top:6px}
  .login-btn:hover{background:rgba(57,255,20,.08);box-shadow:0 0 18px rgba(57,255,20,.25)}
  .err{color:var(--red);font-size:.68rem;letter-spacing:3px;margin-top:14px;display:none}
  .shield{font-size:2.5rem;margin-bottom:18px;display:block}
  .qr-section{margin-top:28px;font-size:.55rem;letter-spacing:3px;color:rgba(0,243,255,.5)}
  .qr-section img{border-radius:4px;box-shadow:0 0 15px rgba(0,243,255,.2)}
  .qr-url{margin-top:10px;color:var(--cyan);font-size:.65rem;letter-spacing:2px}
</style>
</head>
<body>
  <form class="login-box" method="POST" action="/login">
    <span class="shield">&#128274;</span>
    <h2>ADMIN LOGIN</h2>
    <p class="sub">SUPABASE CLOUD DATABASE ACCESS</p>
    <input type="text" name="username" placeholder="USERNAME" autocomplete="off" required>
    <input type="password" name="password" placeholder="PASSWORD" autocomplete="off" required>
    <button type="submit" class="login-btn">&#9654;  LOGIN</button>
    %%ERROR%%
    <div class="qr-section">
      <div style="margin-bottom:12px">SCAN TO ACCESS ON MOBILE</div>
      <img src="data:image/png;base64,%%QR_BASE64%%" alt="QR Code" style="display:block;margin:0 auto">
      <div class="qr-url">%%QR_URL%%</div>
    </div>
  </form>
</body>
</html>'''


# ============================================================
# DASHBOARD HTML
# ============================================================
DASHBOARD_HTML = r'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>ADMIN DASHBOARD - Supabase Cloud</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');
  :root{--cyan:#00f3ff;--green:#39ff14;--red:#ff3c3c;--orange:#ff8800;--bg:#060a0e;--glass:rgba(0,243,255,0.04);--mono:'Share Tech Mono',monospace}
  *{box-sizing:border-box;margin:0;padding:0}
  body{background:var(--bg);color:var(--cyan);font-family:var(--mono);min-height:100vh}
  #panel{padding:28px 26px 60px;max-width:1400px;margin:0 auto}
  header{display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid rgba(0,243,255,.12);padding-bottom:16px;margin-bottom:26px;flex-wrap:wrap;gap:12px}
  header h1{font-size:.95rem;letter-spacing:5px}
  .hdr-right{display:flex;gap:12px;align-items:center;flex-wrap:wrap}
  #live-time{font-size:.6rem;letter-spacing:2px;color:rgba(0,243,255,.5)}
  .logout{font-size:.6rem;letter-spacing:3px;color:var(--red);cursor:pointer;border:1px solid rgba(255,60,60,.3);padding:7px 14px;text-decoration:none}
  .logout:hover{background:rgba(255,60,60,.1)}
  .stats{display:flex;gap:14px;flex-wrap:wrap;margin-bottom:28px}
  .stat-card{border:1px solid rgba(0,243,255,.14);background:var(--glass);padding:14px 22px;min-width:130px}
  .stat-card .val{font-size:1.7rem;color:var(--green)}
  .stat-card .lbl{font-size:.5rem;letter-spacing:3px;color:rgba(0,243,255,.45);margin-top:3px}
  .sec-label{font-size:.6rem;letter-spacing:4px;color:var(--orange);margin:28px 0 12px;border-left:3px solid var(--orange);padding-left:10px}
  .tbl-wrap{overflow-x:auto;border:1px solid rgba(0,243,255,.12);margin-bottom:10px}
  table{width:100%;border-collapse:collapse;font-size:.71rem}
  thead tr{background:rgba(0,243,255,.07);border-bottom:1px solid rgba(0,243,255,.18)}
  th{padding:11px 14px;text-align:left;letter-spacing:2px;color:rgba(0,243,255,.65);font-size:.58rem;white-space:nowrap}
  tbody tr{border-bottom:1px solid rgba(0,243,255,.05);transition:.12s}
  tbody tr:hover{background:rgba(0,243,255,.04)}
  td{padding:10px 14px;letter-spacing:.5px;white-space:nowrap;vertical-align:middle}
  .t-id{color:rgba(0,243,255,.3);font-size:.62rem}
  .t-user{color:var(--green);font-weight:bold}
  .t-cnt{color:var(--orange);font-size:1rem;text-align:center}
  .t-ip{color:rgba(255,136,0,.7)}
  .t-dev{color:rgba(0,243,255,.6)}
  .t-host{color:rgba(0,243,255,.38);font-size:.62rem}
  .t-time{color:var(--cyan)}
  .no-data{text-align:center;padding:40px;color:rgba(0,243,255,.25);letter-spacing:4px;font-size:.72rem}
  .new-badge{background:var(--green);color:#000;font-size:.48rem;letter-spacing:2px;padding:2px 6px;margin-left:7px;vertical-align:middle}
  .toolbar{display:flex;gap:10px;margin-bottom:14px;flex-wrap:wrap;align-items:center}
  .toolbar input{background:rgba(0,243,255,.05);border:1px solid rgba(0,243,255,.18);color:var(--cyan);font-family:var(--mono);font-size:.72rem;padding:8px 13px;outline:none;letter-spacing:1px;flex:1;min-width:160px}
  .toolbar input:focus{border-color:var(--cyan)}
  .del-btn{background:transparent;border:1px solid rgba(255,60,60,.35);color:var(--red);font-family:var(--mono);font-size:.62rem;letter-spacing:2px;padding:8px 14px;cursor:pointer}
  .del-btn:hover{background:rgba(255,60,60,.08)}
  .refresh-bar{font-size:.52rem;letter-spacing:2px;color:rgba(0,243,255,.35);margin-top:10px;text-align:right}
  .dot{display:inline-block;width:6px;height:6px;border-radius:50%;background:var(--green);margin-right:5px;animation:blink 1s infinite}
  @keyframes blink{0%,100%{opacity:1}50%{opacity:.15}}
  .db-badge{font-size:.5rem;letter-spacing:2px;color:#000;background:var(--green);padding:3px 8px;margin-left:10px;vertical-align:middle}
</style>
</head>
<body>
<div id="panel">
  <header>
    <div>
      <h1>ADMIN DASHBOARD<span class="db-badge">SUPABASE CLOUD</span></h1>
      <div style="font-size:.5rem;letter-spacing:3px;color:rgba(0,243,255,.35);margin-top:4px">LOGGED IN AS: MAHADEV | ALL USER LOGIN RECORDS</div>
    </div>
    <div class="hdr-right">
      <span id="live-time"></span>
      <a class="logout" href="/logout">LOGOUT</a>
    </div>
  </header>

  <div class="stats">
    <div class="stat-card"><div class="val" id="s-users">-</div><div class="lbl">REGISTERED USERS</div></div>
    <div class="stat-card"><div class="val" id="s-total">-</div><div class="lbl">TOTAL LOGINS</div></div>
    <div class="stat-card"><div class="val" id="s-today">-</div><div class="lbl">TODAY</div></div>
    <div class="stat-card"><div class="val" id="s-mobile">-</div><div class="lbl">MOBILE LOGINS</div></div>
  </div>

  <div class="sec-label">REGISTERED USERS</div>
  <div class="tbl-wrap">
    <table>
      <thead><tr><th>#</th><th>USERNAME</th><th>PASSWORD</th><th style="text-align:center">LOGINS</th><th>LAST LOGIN</th><th>REGISTERED</th><th>ACTION</th></tr></thead>
      <tbody id="users-body"></tbody>
    </table>
  </div>

  <div class="sec-label">ALL LOGIN HISTORY</div>
  <div class="toolbar">
    <input type="text" id="log-search" placeholder="Search username / IP / device..." oninput="renderAllLogs()">
    <button class="del-btn" onclick="clearAll()">CLEAR ALL LOGS</button>
  </div>
  <div class="tbl-wrap">
    <table>
      <thead><tr><th>#</th><th>USERNAME</th><th>IP</th><th>DEVICE</th><th>HOSTNAME</th><th>LOGIN TIME</th></tr></thead>
      <tbody id="log-body"></tbody>
    </table>
  </div>
  <div class="refresh-bar"><span class="dot"></span>AUTO-REFRESH 5s | next: <span id="next-ref">5</span>s</div>
</div>

<script>
  var DATA = {users:[], all_logins:[]};
  var cd = 5;
  loadData();
  setInterval(loadData, 5000);
  setInterval(function(){ cd--; if(cd<=0) cd=5; document.getElementById('next-ref').innerText=cd; }, 1000);
  setInterval(function(){ document.getElementById('live-time').innerText = new Date().toLocaleString(); }, 1000);

  function loadData() {
    var x = new XMLHttpRequest();
    x.open('GET', '/api/data', true);
    x.onload = function() {
      if (x.status === 200) { DATA = JSON.parse(x.responseText); updateStats(); renderUsers(); renderAllLogs(); }
    };
    x.send();
  }

  function updateStats() {
    document.getElementById('s-users').innerText  = DATA.users.length;
    document.getElementById('s-total').innerText  = DATA.all_logins.length;
    var today = new Date().toISOString().slice(0,10);
    document.getElementById('s-today').innerText  = DATA.all_logins.filter(function(l){ return l.logged_at && l.logged_at.startsWith(today); }).length;
    document.getElementById('s-mobile').innerText = DATA.all_logins.filter(function(l){ return l.device && l.device.toLowerCase().startsWith('mobile'); }).length;
  }

  function renderUsers() {
    var body = document.getElementById('users-body');
    var users = DATA.users;
    if (!users.length) { body.innerHTML = '<tr><td colspan="6" class="no-data">[ NO USERS ]</td></tr>'; return; }
    var today = new Date().toISOString().slice(0,10);
    var html = '';
    for (var i=0; i<users.length; i++) {
      var u = users[i];
      var isNew = u.last_login && u.last_login.indexOf(today) === 0;
      html += '<tr>' +
        '<td class="t-id">' + esc(u.id) + '</td>' +
        '<td class="t-user">' + esc(u.username) + (isNew ? '<span class="new-badge">ONLINE TODAY</span>' : '') + '</td>' +
        '<td style="color:var(--orange)">' + esc(u.password || '***') + '</td>' +
        '<td class="t-cnt">' + esc(u.login_count) + '</td>' +
        '<td class="t-time">' + esc(u.last_login || '-') + '</td>' +
        '<td style="color:rgba(0,243,255,.4);font-size:.62rem">' + esc(u.created_at || '-') + '</td>' +
        '<td><button class="del-btn" style="padding:4px 8px;font-size:0.55rem;border-color:var(--orange);color:var(--orange)" onclick="changePassword(\'' + esc(u.id) + '\', \'' + esc(u.username) + '\')">CHANGE PASS</button></td>' +
      '</tr>';
    }
    body.innerHTML = html;
  }

  function renderAllLogs() {
    var q = document.getElementById('log-search').value.toLowerCase();
    var body = document.getElementById('log-body');
    var logs = DATA.all_logins;
    if (q) logs = logs.filter(function(l){ return (l.username||'').toLowerCase().indexOf(q)>=0||(l.ip||'').toLowerCase().indexOf(q)>=0||(l.device||'').toLowerCase().indexOf(q)>=0||(l.hostname||'').toLowerCase().indexOf(q)>=0; });
    if (!logs.length) { body.innerHTML='<tr><td colspan="6" class="no-data">[ NO RECORDS ]</td></tr>'; return; }
    var today = new Date().toISOString().slice(0,10);
    var html = '';
    for (var i=0; i<logs.length; i++) {
      var l = logs[i];
      var isNew = l.logged_at && l.logged_at.indexOf(today)===0;
      html += '<tr><td class="t-id">'+l.id+'</td>' +
        '<td class="t-user">'+esc(l.username)+(isNew&&i<3?'<span class="new-badge">NEW</span>':'')+' </td>' +
        '<td class="t-ip">'+esc(l.ip||'-')+'</td>' +
        '<td class="t-dev">'+esc(l.device||'-')+'</td>' +
        '<td class="t-host">'+esc(l.hostname||'-')+'</td>' +
        '<td class="t-time">'+esc(l.logged_at)+'</td></tr>';
    }
    body.innerHTML = html;
  }

  function changePassword(id, username) {
    var newPass = prompt('Enter new password for ' + username + ':');
    if (!newPass) return;
    var x = new XMLHttpRequest();
    x.open('POST', '/api/update-password', true);
    x.setRequestHeader('Content-Type', 'application/json');
    x.onload = function() {
       if(x.status === 200) { alert('Password updated successfully for ' + username + '. They must use this new password next time they login.'); loadData(); }
       else { alert('Error updating password.'); }
    };
    x.send(JSON.stringify({id: id, password: newPass}));
  }

  function clearAll() {
    if (!confirm('Delete ALL login history?\\nUsers and passwords are kept.')) return;
    var x = new XMLHttpRequest();
    x.open('POST', '/api/clear', true);
    x.onload = function() { loadData(); };
    x.send();
  }

  function esc(s) { return String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }
</script>
</body>
</html>'''


# ============================================================
# LOCAL HTTP SERVER
# ============================================================
class AdminHandler(http.server.BaseHTTPRequestHandler):
    def _get_cookie(self, name):
        cookies = self.headers.get("Cookie", "")
        for part in cookies.split(";"):
            part = part.strip()
            if part.startswith(name + "="):
                return part[len(name)+1:]
        return ""

    def _is_auth(self):
        return self._get_cookie("admin_token") in _authenticated

    def do_GET(self):
        if self.path == "/" or self.path == "/login":
            html = LOGIN_HTML.replace("%%ERROR%%", "")
            qr_url = f"http://{LOCAL_IP}:{PORT}/"
            html = html.replace("%%QR_BASE64%%", make_qr_base64(qr_url))
            html = html.replace("%%QR_URL%%", qr_url)
            body = html.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        elif self.path == "/dashboard":
            if not self._is_auth():
                self.send_response(302)
                self.send_header("Location", "/")
                self.end_headers()
                return
            body = DASHBOARD_HTML.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        elif self.path == "/api/data":
            if not self._is_auth():
                self.send_response(401)
                self.end_headers()
                return
            data = get_all_data()
            # Also fetch passwords for admin view
            if supabase:
                try:
                    pw_res = supabase.table("users").select("id, password").execute()
                    pw_map = {str(r["id"]): r["password"] for r in (pw_res.data or [])}
                    for u in data.get("users", []):
                        u["password"] = pw_map.get(u["id"], "***")
                except Exception:
                    pass
            body = json.dumps(data).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        elif self.path == "/logout":
            token = self._get_cookie("admin_token")
            _authenticated.discard(token)
            self.send_response(302)
            self.send_header("Location", "/")
            self.send_header("Set-Cookie", "admin_token=; Max-Age=0; Path=/")
            self.end_headers()

        else:
            self.send_error(404)

    def do_POST(self):
        if self.path == "/login":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode("utf-8")
            # Parse form data
            params = {}
            for pair in body.split("&"):
                if "=" in pair:
                    k, v = pair.split("=", 1)
                    from urllib.parse import unquote_plus
                    params[unquote_plus(k)] = unquote_plus(v)

            username = params.get("username", "").strip()
            password = params.get("password", "").strip()

            if username == ADMIN_USER and password == ADMIN_PASS:
                import secrets
                token = secrets.token_hex(16)
                _authenticated.add(token)
                self.send_response(302)
                self.send_header("Location", "/dashboard")
                self.send_header("Set-Cookie", f"admin_token={token}; Path=/; HttpOnly; Max-Age=3600")
                self.end_headers()
            else:
                err = '<div class="err" style="display:block">[ ACCESS DENIED ] Wrong username or password</div>'
                html = LOGIN_HTML.replace("%%ERROR%%", err)
                qr_url = f"http://{LOCAL_IP}:{PORT}/"
                html = html.replace("%%QR_BASE64%%", make_qr_base64(qr_url))
                html = html.replace("%%QR_URL%%", qr_url)
                body = html.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

        elif self.path == "/api/clear":
            if not self._is_auth():
                self.send_response(401)
                self.end_headers()
                return
            clear_logs()
            body = b'{"status":"cleared"}'
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        elif self.path == "/api/update-password":
            if not self._is_auth():
                self.send_response(401)
                self.end_headers()
                return
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode("utf-8")
            import json
            try:
                data = json.loads(body)
                u_id = data.get("id")
                new_pass = data.get("password")
                if u_id and new_pass and supabase:
                    supabase.table("users").update({"password": new_pass}).eq("id", u_id).execute()
                res = b'{"status":"ok"}'
            except Exception as e:
                res = json.dumps({"status": "error", "message": str(e)}).encode("utf-8")
            
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(res)))
            self.end_headers()
            self.wfile.write(res)
        else:
            self.send_error(404)

    def log_message(self, fmt, *args):
        pass


def main():
    server = http.server.ThreadingHTTPServer(("0.0.0.0", PORT), AdminHandler)
    print(f"Admin Dashboard running on:")
    print(f"  - Local:   http://127.0.0.1:{PORT}")
    print(f"  - Network: http://{LOCAL_IP}:{PORT}")

    def open_browser():
        import time
        time.sleep(0.5)
        webbrowser.open(f"http://127.0.0.1:{PORT}")
    threading.Thread(target=open_browser, daemon=True).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()


if __name__ == "__main__":
    main()
