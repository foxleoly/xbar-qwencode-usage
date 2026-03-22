#!/opt/homebrew/bin/python3
# <xbar.title>Qwen Code & OpenCode Token Usage</xbar.title>
# <xbar.version>2.10.0</xbar.version>
# <xbar.desc>Shows daily token usage from Qwen Code and OpenCode</xbar.desc>
# <xbar.dependencies>python3</xbar.dependencies>

import json
import os
import sqlite3
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

VERSION = "2.10.0"
REPO = "foxleoly/xbar-qwencode-usage"
PLUGIN_PATH = os.path.abspath(__file__)

def format_count(n):
    if n >= 1_000_000: return f"{n/1_000_000:.1f}M"
    if n >= 1_000: return f"{n/1_000:.1f}K"
    return str(n)

def get_latest_version():
    """Get latest version from GitHub"""
    try:
        import urllib.request
        url = f"https://raw.githubusercontent.com/{REPO}/master/opencode-usage.1m.py"
        with urllib.request.urlopen(url, timeout=5) as response:
            content = response.read().decode('utf-8')
            for line in content.split('\n'):
                if line.startswith('# <xbar.version>'):
                    return line.split('>')[1].split('<')[0]
    except:
        pass
    return None

def update_plugin():
    """Download and install latest version"""
    try:
        import urllib.request
        url = f"https://raw.githubusercontent.com/{REPO}/master/opencode-usage.1m.py"
        with urllib.request.urlopen(url, timeout=10) as response:
            content = response.read().decode('utf-8')
        with open(PLUGIN_PATH, 'w') as f:
            f.write(content)
        os.chmod(PLUGIN_PATH, 0o755)
        return True
    except Exception as e:
        return False

def get_model_info():
    """Get current model name from settings.json"""
    settings_path = Path.home() / ".qwen" / "settings.json"
    if not settings_path.exists():
        return None
    try:
        with open(settings_path) as f:
            settings = json.load(f)
        model_id = settings.get("model", {}).get("name")
        if not model_id:
            return None
        providers = settings.get("modelProviders", {})
        for provider, models in providers.items():
            for m in models:
                if m.get("id") == model_id:
                    return m.get("name", model_id)
        return model_id
    except:
        return None

def get_oc_stats():
    db = Path.home() / ".local/share/opencode/opencode.db"
    if not db.exists(): return 0, 0, 0, 0, 0, 0, 0, 0, 0
    try:
        conn = sqlite3.connect(str(db))
        c = conn.cursor()
        c.execute("""SELECT 
            SUM(CASE WHEN date(time_created/1000,'unixepoch','localtime')=date('now','localtime') 
                THEN json_extract(data,'$.tokens.total') ELSE 0 END),
            SUM(CASE WHEN date(time_created/1000,'unixepoch','localtime')=date('now','localtime') 
                THEN json_extract(data,'$.tokens.input') ELSE 0 END),
            SUM(CASE WHEN date(time_created/1000,'unixepoch','localtime')=date('now','localtime') 
                THEN json_extract(data,'$.tokens.output') ELSE 0 END),
            SUM(CASE WHEN date(time_created/1000,'unixepoch','localtime')=date('now','localtime') 
                THEN json_extract(data,'$.tokens.cache.read') ELSE 0 END),
            SUM(CASE WHEN date(time_created/1000,'unixepoch','localtime')=date('now','localtime') 
                THEN json_extract(data,'$.tokens.reasoning') ELSE 0 END)
            FROM message WHERE json_extract(data,'$.role')='assistant'""")
        row = c.fetchone()
        today_t = int(row[0] or 0)
        today_i = int(row[1] or 0)
        today_o = int(row[2] or 0)
        today_c = int(row[3] or 0)
        today_r = int(row[4] or 0)
        c.execute("SELECT SUM(json_extract(data,'$.tokens.total')) FROM message WHERE json_extract(data,'$.role')='assistant' AND date(time_created/1000,'unixepoch','localtime')>=date('now','localtime','-6 days')")
        d7 = int(c.fetchone()[0] or 0)
        c.execute("SELECT SUM(json_extract(data,'$.tokens.total')) FROM message WHERE json_extract(data,'$.role')='assistant' AND date(time_created/1000,'unixepoch','localtime')>=date('now','localtime','-29 days')")
        d30 = int(c.fetchone()[0] or 0)
        c.execute("SELECT SUM(json_extract(data,'$.tokens.reasoning')) FROM message WHERE json_extract(data,'$.role')='assistant' AND date(time_created/1000,'unixepoch','localtime')>=date('now','localtime','-6 days')")
        d7_r = int(c.fetchone()[0] or 0)
        c.execute("SELECT SUM(json_extract(data,'$.tokens.reasoning')) FROM message WHERE json_extract(data,'$.role')='assistant' AND date(time_created/1000,'unixepoch','localtime')>=date('now','localtime','-29 days')")
        d30_r = int(c.fetchone()[0] or 0)
        conn.close()
        return today_t, today_i, today_o, today_c, today_r, d7, d30, d7_r, d30_r
    except: return 0, 0, 0, 0, 0, 0, 0, 0, 0

def get_qwen_stats():
    qwen_path = Path.home() / ".qwen/projects"
    if not qwen_path.exists(): return {}
    stats = {'today': {'t':0,'i':0,'o':0,'c':0,'th':0}, 'd7': {'t':0,'i':0,'o':0,'c':0,'th':0}, 'd30': {'t':0,'i':0,'o':0,'c':0,'th':0}}
    now = datetime.now().date()
    cutoff7 = now - timedelta(days=6)
    cutoff30 = now - timedelta(days=29)
    for f in qwen_path.glob("*/chats/*.jsonl"):
        try:
            for line in open(f):
                if '"ui_telemetry"' not in line: continue
                d = json.loads(line)
                if d.get("subtype") != "ui_telemetry": continue
                ui = d.get("systemPayload",{}).get("uiEvent",{})
                ts = d.get("timestamp","")
                if not ts: continue
                rd = datetime.fromisoformat(ts.replace("Z","+00:00")).date()
                t = ui.get("total_token_count",0)
                i = ui.get("input_token_count",0)
                o = ui.get("output_token_count",0)
                c = ui.get("cached_content_token_count",0)
                th = ui.get("thoughts_token_count",0)
                if rd == now:
                    stats['today']['t'] += t
                    stats['today']['i'] += i
                    stats['today']['o'] += o
                    stats['today']['c'] += c
                    stats['today']['th'] += th
                if rd >= cutoff7:
                    stats['d7']['t'] += t
                    stats['d7']['i'] += i
                    stats['d7']['o'] += o
                    stats['d7']['c'] += c
                    stats['d7']['th'] += th
                if rd >= cutoff30:
                    stats['d30']['t'] += t
                    stats['d30']['i'] += i
                    stats['d30']['o'] += o
                    stats['d30']['c'] += c
                    stats['d30']['th'] += th
        except: pass
    return stats

def main():
    oc_t, oc_i, oc_o, oc_c, oc_r, oc_7, oc_30, oc_7_r, oc_30_r = get_oc_stats()
    qw = get_qwen_stats()
    qw_t = qw.get('today',{}).get('t',0)
    model_name = get_model_info()
    
    # Check for updates
    latest_version = get_latest_version()
    has_update = latest_version and latest_version != VERSION
    
    # Title - Qwen Code first
    if qw_t > 0 and oc_t > 0:
        print(f"QC {format_count(qw_t)} / OC {format_count(oc_t)}")
    elif qw_t > 0:
        print(f"QC {format_count(qw_t)}")
    elif oc_t > 0:
        print(f"OC {format_count(oc_t)}")
    else:
        print("No data")
    
    # Update notification
    if has_update:
        print(f"⬆️ v{VERSION} → v{latest_version} | color=orange")
    print("---")
    
    # Update menu item
    if has_update:
        print(f"🔄 Update to v{latest_version} | bash={sys.executable} param1={PLUGIN_PATH} param2=update terminal=false refresh=true")
        print("---")
    
    # Qwen Code section (first)
    if qw_t > 0:
        print("Qwen Code | color=#7986cb font=Menlo size=13")
        print(f"--Total: {format_count(qw['today']['t'])} | color=#00bcd4")
        print(f"--Input: {format_count(qw['today']['i'])} | color=#81d4fa")
        print(f"--Output: {format_count(qw['today']['o'])} | color=#a5d6a7")
        print(f"--Cache: {format_count(qw['today']['c'])} | color=#ffcc80")
        print(f"--Thoughts: {format_count(qw['today']['th'])} | color=#f48fb1")
        print(f"--7-Day: {format_count(qw['d7']['t'])} | color=#ce93d8")
        print(f"--30-Day: {format_count(qw['d30']['t'])} | color=#90a4ae")
        print(f"--Model: {model_name or 'N/A'} | color=#b0bec5 size=11")
    
    # OpenCode section (second)
    if oc_t > 0:
        if qw_t > 0:
            print("---")
        print("OpenCode | color=#4fc3f7 font=Menlo size=13")
        print(f"--Total: {format_count(oc_t)} | color=#00bcd4")
        print(f"--Input: {format_count(oc_i)} | color=#81d4fa")
        print(f"--Output: {format_count(oc_o)} | color=#a5d6a7")
        print(f"--Cache: {format_count(oc_c)} | color=#ffcc80")
        print(f"--Reasoning: {format_count(oc_r)} | color=#f48fb1")
        print(f"--7-Day: {format_count(oc_7)} | color=#ce93d8")
        print(f"--30-Day: {format_count(oc_30)} | color=#90a4ae")
        print(f"--Model: {model_name or 'N/A'} | color=#b0bec5 size=11")
    
    print("---")
    print(f"Current: v{VERSION} | color=#78909c size=10")
    print(f"Updated: {datetime.now().strftime('%H:%M:%S')} | color=#78909c size=10")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "update":
        if update_plugin():
            print("✅ Update successful!")
        else:
            print("❌ Update failed!")
        sys.exit(0)
    main()