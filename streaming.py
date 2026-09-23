#!/usr/bin/env python3
"""
StreamIMDB Downloader
Looks up a movie or TV show, resolves an HLS stream, and saves it as an MP4.

Core flow (unchanged): lookup title -> pick stream quality -> confirm -> download.

Extra features:
  * Search results picker (no more silent "first result")
  * Movies AND TV shows (pick a season + episode, or an entire season)
  * Batch downloads: many IDs/URLs/titles, or a text file of queries
  * Quality wizard with a configurable default (best / 720 / 1080)
  * Parallel segment downloads
  * AES-128 encrypted HLS streams decoded on the fly (via OpenSSL)
  * config.conf settings: rpi, ffmpeg_path, openssl_path, output_dir,
    default_quality, parallel_workers, skip_confirm
  * --kodi-test environment check for Raspberry Pi / LibreELEC / Kodi / PC

Usage:
    python streamimdb-download.py
    python streamimdb-download.py <query> [<query> ...]
    python streamimdb-download.py -f movies.txt
    python streamimdb-download.py <query> -y
    python streamimdb-download.py --kodi-test
    python streamimdb-download.py --help

Examples:
    python3 streamimdb-download.py 1480574
    python3 streamimdb-download.py https://streamimdb.ru/movie/995vo-just-play-dead
    python3 streamimdb-download.py interstella 5555
    python3 streamimdb-download.py "breaking bad" -f batch.txt -y
"""

import os
import re
import sys
import json
import time
import shutil
import argparse
import subprocess
import threading
import urllib.request
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed

# ── Configuration ──────────────────────────────────────────────────────
API_KEY = "2c0bef41c58b6316e7ca2049b9ce16f9"
STREAM_API = "https://streamdata.vaplayer.ru/api.php"
PLAYER_ORIGIN = "https://nextgencloudfabric.com"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"

HEADERS = {
    "User-Agent": UA,
    "Referer": PLAYER_ORIGIN + "/",
    "Origin": PLAYER_ORIGIN,
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "config.conf")

DEFAULT_CONFIG = {
    "rpi": "false",
    "ffmpeg_path": "ffmpeg",
    "openssl_path": "openssl",
    "output_dir": ".",
    "default_quality": "720",
    "parallel_workers": "4",
    "skip_confirm": "false",
}

FFMPEG_CANDIDATES = [
    "ffmpeg",
    "/usr/bin/ffmpeg",
    "/usr/local/bin/ffmpeg",
    "/storage/.kodi/tools/ffmpeg",
    "/storage/.kodi/addons/tools.ffmpeg/ffmpeg",
]

OPENSSL_CANDIDATES = [
    "openssl",
    "/usr/bin/openssl",
    "/usr/local/bin/openssl",
    "/storage/.kodi/tools/openssl",
]

def load_config():
    """Load config.conf (key=value lines) over the defaults, if it exists."""
    config = dict(DEFAULT_CONFIG)
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    key, value = line.split("=", 1)
                    config[key.strip()] = value.strip()
        except Exception as e:
            print(f"[!] Could not read {CONFIG_FILE}: {e}")
    return config

def get_cfg_bool(key, default=False):
    return str(CONFIG.get(key, str(default))).strip().lower() in ("1", "true", "yes", "on")

def get_cfg_int(key, default):
    try:
        return int(CONFIG.get(key, default))
    except (TypeError, ValueError):
        return default

CONFIG = load_config()
FFMPEG_PATH = CONFIG.get("ffmpeg_path") or "ffmpeg"
OPENSSL_PATH = CONFIG.get("openssl_path") or "openssl"
OUTPUT_DIR = CONFIG.get("output_dir") or "."
DEFAULT_QUALITY = (CONFIG.get("default_quality") or "720").strip()
PARALLEL_WORKERS = get_cfg_int("parallel_workers", 4)
SKIP_CONFIRM = get_cfg_bool("skip_confirm", False)

# ── Environment / Kodi Detection ───────────────────────────────────────
def read_file(path):
    """Return the contents of a file, or an empty string if unreadable."""
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception:
        return ""

def is_raspberry_pi():
    """Detect Raspberry Pi hardware via /proc/cpuinfo or device-tree model."""
    cpuinfo = read_file("/proc/cpuinfo")
    if "Raspberry Pi" in cpuinfo or "BCM" in cpuinfo:
        return True
    return "Raspberry Pi" in read_file("/proc/device-tree/model")

def is_libreelec():
    """Detect LibreELEC / Kodi environments."""
    os_release = read_file("/etc/os-release")
    if "LibreELEC" in os_release or "libreelec" in os_release:
        return True
    return os.path.isdir("/storage/.kodi")

def detect_tool(candidates):
    """Return the first candidate that exists and runs, or None."""
    for candidate in candidates:
        path = candidate if os.path.isabs(candidate) else shutil.which(candidate)
        if not path or not os.path.exists(path):
            continue
        try:
            result = subprocess.run([path, "-version"], stdout=subprocess.DEVNULL,
                                    stderr=subprocess.DEVNULL, timeout=10)
            if result.returncode == 0:
                return path
        except Exception:
            continue
    return None

def detect_ffmpeg():
    return detect_tool(FFMPEG_CANDIDATES)

def detect_openssl():
    return detect_tool(OPENSSL_CANDIDATES)

def write_config(rpi, ffmpeg_path, openssl_path):
    """Write config.conf with the detected environment settings."""
    lines = [
        "# Auto-generated by streamimdb-download.py --kodi-test",
        "# You may edit these values; re-run --kodi-test to regenerate.",
        f"rpi={'true' if rpi else 'false'}",
        f"ffmpeg_path={ffmpeg_path}",
        f"openssl_path={openssl_path or 'openssl'}",
        "output_dir=.",
        "default_quality=720",
        "parallel_workers=4",
        "skip_confirm=false",
    ]
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

def run_kodi_test():
    """Check that this machine has everything needed, then write config.conf."""
    print("=" * 60)
    print("  StreamIMDB Downloader - environment check (--kodi-test)")
    print("=" * 60)

    rpi = is_raspberry_pi()
    libreelec = is_libreelec()
    kodi_env = rpi or libreelec

    print(f"  Platform      : {sys.platform}")
    print(f"  Python        : {sys.version.split()[0]}")
    print(f"  Raspberry Pi  : {'yes' if rpi else 'no'}")
    print(f"  Kodi/LibreELEC: {'yes' if libreelec else 'no'}")

    problems = []

    if sys.version_info < (3, 6):
        problems.append("Python 3.6+ is required.")
        print("  Python check  : FAIL (too old)")
    else:
        print("  Python check  : OK")

    ffmpeg_path = detect_ffmpeg()
    if ffmpeg_path:
        print(f"  FFmpeg        : OK ({ffmpeg_path})")
    else:
        problems.append("FFmpeg was not found. Install it (e.g. 'sudo apt install ffmpeg').")
        print("  FFmpeg        : MISSING")

    openssl_path = detect_openssl()
    if openssl_path:
        print(f"  OpenSSL       : OK ({openssl_path})")
    else:
        print("  OpenSSL       : missing (only needed for encrypted HLS streams)")

    try:
        testfile = os.path.join(BASE_DIR, ".write_test")
        with open(testfile, "w") as f:
            f.write("ok")
        os.remove(testfile)
        print(f"  Write access  : OK ({BASE_DIR})")
    except Exception as e:
        problems.append(f"Cannot write to {BASE_DIR}: {e}")
        print(f"  Write access  : FAIL ({e})")

    print("-" * 60)

    if problems:
        print("[!] Missing requirements:")
        for p in problems:
            print(f"    - {p}")
        print("\n[!] config.conf was NOT written. Fix the above and re-run --kodi-test.")
        sys.exit(1)

    env_name = "Raspberry Pi / Kodi" if kodi_env else "PC / normal"
    write_config(kodi_env, ffmpeg_path, openssl_path)
    print(f"[+] Environment: {env_name}")
    print(f"[+] config.conf written to: {CONFIG_FILE}")
    if kodi_env:
        print("    rpi=true -> using Kodi/LibreELEC friendly settings.")
    else:
        print("    rpi=false -> keeping normal PC defaults (ffmpeg from PATH).")
    print("[+] Everything needed to run is installed. You're good to go.")
    sys.exit(0)

# ── TMDB / Stream Lookup ───────────────────────────────────────────────
def fetch_json(url, headers=None):
    """Fetch a URL and return parsed JSON (None on failure)."""
    req = urllib.request.Request(url, headers=headers or {"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        print(f"  [!] Request error for {url}: {e}")
        return None

def media_label(result):
    return "Movie" if result["media_type"] == "movie" else "TV"

def menu_line(result):
    y = f" ({result['year']})" if result.get("year") else ""
    return f"[{media_label(result)}] {result['title']}{y}"

def search_tmdb_multi(query):
    """Search TMDB and return normalized movie/tv result dicts."""
    url = (f"https://api.themoviedb.org/3/search/multi"
           f"?api_key={API_KEY}&query={urllib.parse.quote(query)}")
    data = fetch_json(url)
    results = []
    if not data or not data.get("results"):
        return results
    for r in data["results"]:
        mt = r.get("media_type")
        if mt not in ("movie", "tv"):
            continue
        if mt == "movie":
            title = r.get("title") or r.get("name") or "Unknown"
            year = (r.get("release_date") or "")[:4]
        else:
            title = r.get("name") or r.get("title") or "Unknown"
            year = (r.get("first_air_date") or "")[:4]
        results.append({
            "id": r["id"],
            "title": title,
            "year": year,
            "media_type": mt,
        })
    return results

def pick_tmdb_result(query):
    """Search TMDB and let the user choose; single matches auto-pick."""
    results = search_tmdb_multi(query)
    if not results:
        return None
    if len(results) == 1:
        print(f"[+] Matched: {menu_line(results[0])}")
        return results[0]
    print(f"\n[+] Search results for '{query}':")
    limit = min(len(results), 8)
    for i, r in enumerate(results[:limit], start=1):
        print(f"  {i}. {menu_line(r)}")
    print("  q. Quit")
    while True:
        c = input(f"Select a result [1-{limit}] or q to quit: ").strip()
        if c.isdigit() and 1 <= int(c) <= limit:
            r = results[int(c) - 1]
            print(f"[+] Selected: {menu_line(r)}")
            return r
        if c.lower() in ("q", "quit", "cancel"):
            raise RuntimeError("Cancelled by user.")
        print("  [!] Invalid selection.")

def resolve_tmdb_id(tmdb_id):
    """Fetch title info for a raw TMDB ID (movie or TV)."""
    for mt, name_key in (("movie", "title"), ("tv", "name")):
        data = fetch_json(f"https://api.themoviedb.org/3/{mt}/{tmdb_id}?api_key={API_KEY}")
        if data:
            name = data.get(name_key)
            if name:
                year = (data.get("release_date") or data.get("first_air_date") or "")[:4]
                return {"id": tmdb_id, "title": name, "year": year, "media_type": mt}
    return None

def get_tv_seasons(tv_id):
    """Return the list of numbered seasons for a TV show."""
    data = fetch_json(f"https://api.themoviedb.org/3/tv/{tv_id}?api_key={API_KEY}")
    out = []
    if data:
        for s in data.get("seasons", []):
            num = s.get("season_number", 0)
            cnt = s.get("episode_count", 0)
            if num >= 1 and cnt:
                out.append({"number": num, "name": s.get("name") or f"Season {num}", "episodes": cnt})
    return out

def get_tv_episodes(tv_id, season):
    """Return the list of episodes for a given season."""
    data = fetch_json(f"https://api.themoviedb.org/3/tv/{tv_id}/season/{season}?api_key={API_KEY}")
    out = []
    if data:
        for e in data.get("episodes", []):
            num = e.get("episode_number", 0)
            if num:
                out.append({"number": num, "name": e.get("name") or ""})
    return out

def build_tv_jobs(result):
    """Interactively pick a season and episode(s) for a TV show."""
    show = result["title"]
    print(f"\n[*] '{show}' is a TV show. Loading seasons...")
    seasons = get_tv_seasons(result["id"])
    if not seasons:
        raise RuntimeError("No seasons found for this show.")
    print("[+] Seasons:")
    for i, s in enumerate(seasons, start=1):
        print(f"  {i}. Season {s['number']}: {s['name']} ({s['episodes']} ep)")
    while True:
        c = input(f"Select a season [1-{len(seasons)}] or press Enter for season 1: ").strip()
        if not c:
            c = "1"
        if c.isdigit() and 1 <= int(c) <= len(seasons):
            season = seasons[int(c) - 1]
            break
        print("  [!] Invalid selection.")

    episodes = get_tv_episodes(result["id"], season["number"])
    if not episodes:
        raise RuntimeError(f"No episode data for season {season['number']}.")
    print(f"\n[+] Season {season['number']} of '{show}':")
    for e in episodes:
        name = f" - {e['name']}" if e["name"] else ""
        print(f"  {e['number']}. E{e['number']:02d}{name}")
    print("  0. Entire season (download all episodes)")

    picked = []
    while True:
        c = input(f"Select an episode [1-{len(episodes)}] or 0 for the whole season: ").strip()
        if c in ("0", "all"):
            picked = list(episodes)
            break
        if c.isdigit() and 1 <= int(c) <= len(episodes):
            picked = [episodes[int(c) - 1]]
            break
        print("  [!] Invalid selection.")

    jobs = []
    for e in picked:
        label = f"{show} - S{season['number']:02d}E{e['number']:02d}"
        if e["name"]:
            label += f" - {e['name']}"
        jobs.append({
            "title": show,
            "tmdb_id": result["id"],
            "mtype": "tv",
            "season": season["number"],
            "episode": e["number"],
            "label": label,
        })
    return jobs

def build_jobs_from_result(result):
    """Turn a TMDB result into one or more download jobs."""
    if result["media_type"] == "movie":
        return [{
            "title": result["title"],
            "tmdb_id": result["id"],
            "mtype": "movie",
            "season": None,
            "episode": None,
            "label": result["title"],
        }]
    return build_tv_jobs(result)

def build_jobs_from_url(url):
    """Resolve a StreamIMDB URL slug into TMDB results."""
    match = re.search(r"/(movie|tv)/([^/]+)", url)
    if not match:
        raise RuntimeError("Invalid URL. Expected https://streamimdb.ru/movie/<slug> or .../tv/<slug>")
    slug = match.group(2)
    parts = slug.split("-")
    queries = [slug.replace("-", " ")]
    if len(parts) > 1 and len(parts[0]) <= 6 and parts[0].isalnum():
        queries.insert(0, " ".join(parts[1:]))
    for q in queries:
        print(f"[*] Searching TMDB for: '{q}'...")
        result = pick_tmdb_result(q)
        if result:
            return build_jobs_from_result(result)
    raise RuntimeError("Could not find a matching movie/TV show on TMDB.")

def build_jobs(arg):
    """Parse a single query (URL, TMDB ID, or title) into download job(s)."""
    arg = arg.strip()
    if arg.startswith("http"):
        return build_jobs_from_url(arg)
    if re.fullmatch(r"\d+", arg):
        result = resolve_tmdb_id(int(arg))
        if not result:
            raise RuntimeError("No movie or TV show found for that TMDB ID.")
        print(f"[+] Found: {menu_line(result)}")
        return build_jobs_from_result(result)
    print(f"[*] Searching TMDB for: '{arg}'...")
    result = pick_tmdb_result(arg)
    if not result:
        raise RuntimeError(f"No results on TMDB for '{arg}'.")
    return build_jobs_from_result(result)

def read_query_file(path):
    """Read one query per line from a text file ('#' comments are ignored)."""
    out = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            for ln in f:
                ln = ln.strip()
                if ln and not ln.startswith("#"):
                    out.append(ln)
    except Exception as e:
        print(f"[!] Could not read {path}: {e}")
    return out

def dedupe(items):
    """Remove duplicates while preserving order."""
    seen = set()
    out = []
    for item in items:
        key = item.strip().lower()
        if key and key not in seen:
            seen.add(key)
            out.append(item)
    return out

# ── Stream / Quality Selection ─────────────────────────────────────────
def get_streams(tmdb_id, mtype="movie", season=None, episode=None):
    """Fetch stream URLs from the StreamData API (movie or TV)."""
    attempts = [mtype]
    if mtype == "tv":
        attempts.append("series")
    else:
        attempts.append("tv")

    for t in attempts:
        params = {"tmdb": tmdb_id, "type": t}
        if season is not None:
            params["season"] = season
            params["episode"] = episode if episode is not None else 1
        url = STREAM_API + "?" + urllib.parse.urlencode(params)
        headers = {
            "User-Agent": UA,
            "Referer": f"{PLAYER_ORIGIN}/embed/{t}/{tmdb_id}",
            "Origin": PLAYER_ORIGIN,
        }
        data = fetch_json(url, headers)
        if data and str(data.get("status_code")) == "200":
            streams = data.get("data", {}).get("stream_urls", [])
            if streams:
                return streams
    return []

def get_variants(master_url):
    """Fetch a master playlist and return a list of (height, uri) variant tuples."""
    req = urllib.request.Request(master_url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            text = resp.read().decode('utf-8')
        variants = []
        lines = text.splitlines()
        for i, line in enumerate(lines):
            if line.upper().startswith("#EXT-X-STREAM-INF"):
                uri = None
                for j in range(i + 1, len(lines)):
                    if not lines[j].startswith("#"):
                        uri = lines[j].strip()
                        break
                if uri:
                    height = None
                    match = re.search(r"RESOLUTION=\d+x(\d+)", line, re.IGNORECASE)
                    if match:
                        height = int(match.group(1))
                    variants.append((height, urllib.parse.urljoin(master_url, uri)))
        return variants
    except Exception as e:
        print(f"  [!] Variant resolution warning: {e}")
        return []

def compute_default_index(options):
    """Pick the default menu index from config default_quality."""
    q = DEFAULT_QUALITY.lower()
    if q in ("best", "highest", "max", "auto", "high"):
        return 1
    m = re.search(r"\d+", q)
    if m:
        target = int(m.group(0))
        for i, (_, _, h) in enumerate(options, start=1):
            if h == target:
                return i
        known = [(i, h) for i, (_, _, h) in enumerate(options, start=1) if h]
        if known:
            return min(known, key=lambda t: abs(t[1] - target))[0]
    for target in (720, 1080):
        for i, (_, _, h) in enumerate(options, start=1):
            if h == target:
                return i
    return 1

        print("\n[!] Nothing to download.")
        sys.exit(1)

    confirmed = False
    if len(jobs) > 1 and not SKIP_CONFIRM:
        answer = input(f"\nFound {len(jobs)} item(s) to download. Download all now? [y/N]: ").strip().lower()
        if answer in ("y", "yes"):
            confirmed = True
        else:
            print("[!] Batch download cancelled.")
            sys.exit(0)

    print(f"\n[*] {len(jobs)} download job(s) queued.")
    completed = 0
    failed = 0
    skipped = 0
    for n, job in enumerate(jobs, start=1):
        print("\n" + "=" * 60)
        print(f"[Job {n}/{len(jobs)}] {job['label']}")
        print("=" * 60)
        try:
            if run_job(job, confirmed=confirmed):
                completed += 1
            else:
                skipped += 1
        except SystemExit:
            raise
        except Exception as e:
            failed += 1
            print(f"[!] Job failed: {e}")

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"  Completed : {completed}")
    print(f"  Failed    : {failed}")
    print(f"  Skipped   : {skipped}")
    if failed:
        sys.exit(1)

if __name__ == "__main__":
    main()