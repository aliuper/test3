"""
IPTV Editor Pro v11.0 ULTIMATE
- Material Design Icons (TTF Font)
- Smart Link Detection (AI-like pattern matching)
- Landscape/Portrait support
- Modern Glass UI Design
- Custom app icon support
"""

import os, sys, re, gc, sqlite3, hashlib, traceback, threading, time
from datetime import datetime
from urllib.parse import urlparse, parse_qs, urlencode
from functools import lru_cache
from collections import OrderedDict

def log_err(msg):
    try:
        with open(os.path.join(os.path.expanduser('~'), 'iptv_error.log'), 'a') as f:
            f.write(f'\n{datetime.now()}\n{msg}\n')
    except: pass

sys.excepthook = lambda t,v,tb: log_err(''.join(traceback.format_exception(t,v,tb)))

from kivy.config import Config
Config.set('graphics', 'multisamples', '0')
Config.set('graphics', 'resizable', 'True')
Config.set('kivy', 'log_level', 'warning')

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.image import Image, AsyncImage
from kivy.uix.widget import Widget
from kivy.uix.slider import Slider
from kivy.uix.switch import Switch
from kivy.clock import Clock
from kivy.metrics import dp, sp
from kivy.core.window import Window
from kivy.core.clipboard import Clipboard
from kivy.core.text import LabelBase
from kivy.properties import StringProperty, BooleanProperty, NumericProperty, ObjectProperty, ListProperty
from kivy.utils import get_color_from_hex
from kivy.animation import Animation
from kivy.graphics import Color, Rectangle, RoundedRectangle, Line, Ellipse

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

APP_NAME = "IPTV Editor Pro"
APP_VER = "11.0"

# ==================== FONT REGISTRATION ====================
def register_fonts():
    """Register Material Design Icons font"""
    font_paths = [
        'materialdesignicons-webfont.ttf',
        os.path.join(os.path.dirname(__file__), 'materialdesignicons-webfont.ttf'),
        '/sdcard/Download/materialdesignicons-webfont.ttf',
    ]
    for fp in font_paths:
        if os.path.exists(fp):
            try:
                LabelBase.register(name='MDI', fn_regular=fp)
                return True
            except: pass
    return False

HAS_MDI = register_fonts()

# ==================== MATERIAL DESIGN ICONS ====================
# Unicode codepoints for Material Design Icons
class MDI:
    """Material Design Icons - Unicode codepoints"""
    # If font loaded, use MDI icons, otherwise fallback to text
    if HAS_MDI:
        HOME = '\U000F02DC'      # home
        BACK = '\U000F004D'      # arrow-left
        NEXT = '\U000F0054'      # arrow-right
        UP = '\U000F005D'        # arrow-up
        DOWN = '\U000F0045'      # arrow-down
        CHECK = '\U000F012C'     # check
        CLOSE = '\U000F0156'     # close
        PLUS = '\U000F0415'      # plus
        MINUS = '\U000F0374'     # minus
        STAR = '\U000F04CE'      # star
        STAR_O = '\U000F04D2'    # star-outline
        COG = '\U000F0493'       # cog
        EDIT = '\U000F03EB'      # pencil
        DELETE = '\U000F01B4'    # delete
        SAVE = '\U000F0193'      # content-save
        REFRESH = '\U000F0450'   # refresh
        DOWNLOAD = '\U000F01DA'  # download
        UPLOAD = '\U000F0552'    # upload
        FOLDER = '\U000F024B'    # folder
        FILE = '\U000F0214'      # file
        LINK = '\U000F0337'      # link
        PLAY = '\U000F040A'      # play
        STOP = '\U000F04DB'      # stop
        PAUSE = '\U000F03E4'     # pause
        TV = '\U000F0502'        # television
        WIFI = '\U000F05A9'      # wifi
        SEARCH = '\U000F0349'    # magnify
        FILTER = '\U000F0232'    # filter
        SORT = '\U000F04BA'      # sort
        CLIPBOARD = '\U000F0147' # clipboard
        COPY = '\U000F018F'      # content-copy
        PASTE = '\U000F0192'     # content-paste
        ALERT = '\U000F0026'     # alert
        INFO = '\U000F02FC'      # information
        HELP = '\U000F02D6'      # help-circle
        EARTH = '\U000F01E7'     # earth
        FLAG = '\U000F0238'      # flag
        CLOCK = '\U000F0954'     # clock-outline
        CALENDAR = '\U000F00ED'  # calendar
        ROCKET = '\U000F0463'    # rocket
        FIRE = '\U000F0238'      # fire
        BOLT = '\U000F0DB3'      # lightning-bolt
        MAGIC = '\U000F06E8'     # auto-fix
        AI = '\U000F07D3'        # brain
        MENU = '\U000F035C'      # menu
        DOTS = '\U000F01D9'      # dots-vertical
        THEME = '\U000F03F8'     # palette
        HEART = '\U000F02D1'     # heart
        SEND = '\U000F048A'      # send
        VIEW = '\U000F0208'      # eye
    else:
        # Fallback to simple text
        HOME = '[H]'
        BACK = '<'
        NEXT = '>'
        UP = '^'
        DOWN = 'v'
        CHECK = 'OK'
        CLOSE = 'X'
        PLUS = '+'
        MINUS = '-'
        STAR = '*'
        STAR_O = 'o'
        COG = '@'
        EDIT = '#'
        DELETE = 'X'
        SAVE = 'S'
        REFRESH = 'R'
        DOWNLOAD = 'D'
        UPLOAD = 'U'
        FOLDER = 'F'
        FILE = 'f'
        LINK = '~'
        PLAY = '>'
        STOP = '[]'
        PAUSE = '||'
        TV = 'TV'
        WIFI = 'W'
        SEARCH = '?'
        FILTER = '='
        SORT = 's'
        CLIPBOARD = 'C'
        COPY = 'c'
        PASTE = 'P'
        ALERT = '!'
        INFO = 'i'
        HELP = '?'
        EARTH = 'E'
        FLAG = 'F'
        CLOCK = 'T'
        CALENDAR = 'C'
        ROCKET = 'R'
        FIRE = 'F'
        BOLT = 'B'
        MAGIC = 'M'
        AI = 'AI'
        MENU = '='
        DOTS = ':'
        THEME = 'T'
        HEART = '<3'
        SEND = '>'
        VIEW = 'o'

ICON_FONT = 'MDI' if HAS_MDI else 'Roboto'

# ==================== THEMES ====================
THEMES = {
    'cyberpunk': {
        'name': 'Cyberpunk',
        'bg': '#0a0a0f', 'bg2': '#12121a', 'card': '#1a1a2e', 'card2': '#252542',
        'glass': 'rgba(26,26,46,0.85)', 'acc': '#ff2e63', 'acc2': '#08d9d6',
        'ok': '#08d9d6', 'warn': '#edf756', 'err': '#ff2e63', 'info': '#252a34',
        't1': '#ffffff', 't2': '#eaeaea', 't3': '#aaaaaa', 't4': '#666666',
        'gradient1': '#ff2e63', 'gradient2': '#08d9d6',
    },
    'midnight': {
        'name': 'Midnight',
        'bg': '#0d1b2a', 'bg2': '#1b263b', 'card': '#22334a', 'card2': '#2d3f58',
        'glass': 'rgba(34,51,74,0.85)', 'acc': '#7b68ee', 'acc2': '#ff6b9d',
        'ok': '#4ade80', 'warn': '#fbbf24', 'err': '#f87171', 'info': '#60a5fa',
        't1': '#ffffff', 't2': '#e2e8f0', 't3': '#94a3b8', 't4': '#64748b',
        'gradient1': '#7b68ee', 'gradient2': '#ff6b9d',
    },
    'forest': {
        'name': 'Forest',
        'bg': '#0b1a0b', 'bg2': '#132213', 'card': '#1a3a1a', 'card2': '#225522',
        'glass': 'rgba(26,58,26,0.85)', 'acc': '#4ade80', 'acc2': '#22d3ee',
        'ok': '#4ade80', 'warn': '#fde047', 'err': '#f87171', 'info': '#38bdf8',
        't1': '#ffffff', 't2': '#d1fae5', 't3': '#86efac', 't4': '#4ade80',
        'gradient1': '#4ade80', 'gradient2': '#22d3ee',
    },
    'light': {
        'name': 'Light',
        'bg': '#f8fafc', 'bg2': '#f1f5f9', 'card': '#ffffff', 'card2': '#f8fafc',
        'glass': 'rgba(255,255,255,0.9)', 'acc': '#6366f1', 'acc2': '#ec4899',
        'ok': '#22c55e', 'warn': '#f59e0b', 'err': '#ef4444', 'info': '#3b82f6',
        't1': '#1e293b', 't2': '#334155', 't3': '#64748b', 't4': '#94a3b8',
        'gradient1': '#6366f1', 'gradient2': '#ec4899',
    },
}

theme = 'cyberpunk'
def T(k): return THEMES.get(theme, THEMES['cyberpunk']).get(k, '#ffffff')
def TC(k): return get_color_from_hex(T(k))

# ==================== COUNTRIES ====================
COUNTRIES = {
    'turkey': {'n': 'Turkiye', 'f': '🇹🇷', 'c': ['tr', 'tur', 'turkey', 'turkiye', 'turk'], 'p': 1},
    'germany': {'n': 'Almanya', 'f': '🇩🇪', 'c': ['de', 'ger', 'germany', 'deutsch', 'almanya'], 'p': 2},
    'austria': {'n': 'Avusturya', 'f': '🇦🇹', 'c': ['at', 'aut', 'austria', 'avusturya', 'osterreich'], 'p': 3},
    'romania': {'n': 'Romanya', 'f': '🇷🇴', 'c': ['ro', 'rom', 'romania', 'romanya'], 'p': 4},
    'france': {'n': 'Fransa', 'f': '🇫🇷', 'c': ['fr', 'fra', 'france', 'fransa'], 'p': 5},
    'italy': {'n': 'Italya', 'f': '🇮🇹', 'c': ['it', 'ita', 'italy', 'italya'], 'p': 6},
    'spain': {'n': 'Ispanya', 'f': '🇪🇸', 'c': ['es', 'esp', 'spain', 'ispanya'], 'p': 7},
    'uk': {'n': 'Ingiltere', 'f': '🇬🇧', 'c': ['uk', 'gb', 'england', 'british'], 'p': 8},
    'usa': {'n': 'Amerika', 'f': '🇺🇸', 'c': ['us', 'usa', 'america', 'amerika'], 'p': 9},
    'netherlands': {'n': 'Hollanda', 'f': '🇳🇱', 'c': ['nl', 'netherlands', 'holland'], 'p': 10},
    'poland': {'n': 'Polonya', 'f': '🇵🇱', 'c': ['pl', 'poland', 'polonya'], 'p': 11},
    'russia': {'n': 'Rusya', 'f': '🇷🇺', 'c': ['ru', 'rus', 'russia', 'rusya'], 'p': 12},
    'arabic': {'n': 'Arapca', 'f': '🇸🇦', 'c': ['ar', 'ara', 'arabic', 'arab'], 'p': 13},
    'other': {'n': 'Diger', 'f': '🌐', 'c': ['other'], 'p': 99},
}
PRIO_C = ['turkey', 'germany', 'austria', 'romania']
FMTS = {'m3u': '.m3u', 'm3u8': '.m3u8', 'txt': '.txt'}

# ==================== SMART LINK EXTRACTOR ====================
class SmartLinkExtractor:
    """
    AI-like pattern matching to extract IPTV links from messy text
    Handles Telegram-style formatted text with emojis and special characters
    """
    
    # IPTV URL patterns
    URL_PATTERNS = [
        # Standard m3u links
        r'(https?://[^\s<>"\']+?/get\.php\?[^\s<>"\']+)',
        # Live/Movie/Series streams
        r'(https?://[^\s<>"\']+?/live/[^\s<>"\']+)',
        r'(https?://[^\s<>"\']+?/movie/[^\s<>"\']+)',
        r'(https?://[^\s<>"\']+?/series/[^\s<>"\']+)',
        # Panel links
        r'(https?://[^\s<>"\']+?/panel_api\.php\?[^\s<>"\']+)',
        # Player API
        r'(https?://[^\s<>"\']+?/player_api\.php\?[^\s<>"\']+)',
        # Direct m3u8/ts
        r'(https?://[^\s<>"\']+?\.m3u8?(?:\?[^\s<>"\']*)?)',
        r'(https?://[^\s<>"\']+?\.ts(?:\?[^\s<>"\']*)?)',
        # Generic IPTV ports (common: 8080, 8000, 80, 25461, 2095, 2082)
        r'(https?://[^\s<>"\']+?:(?:8080|8000|25461|2095|2082|80)/[^\s<>"\']+)',
    ]
    
    # Patterns to extract username/password from text
    CREDENTIAL_PATTERNS = [
        r'[Uu]ser(?:name)?[:\s=]+([A-Za-z0-9_.-]+)',
        r'👥\s*[^\s]+\s+([A-Za-z0-9_.-]+)',  # 👥 𝕌𝕤𝕖𝕣 username
        r'[Pp]ass(?:word)?[:\s=]+([A-Za-z0-9_.-]+)',
        r'🔑\s*[^\s]+\s+([A-Za-z0-9_.-]+)',  # 🔑 ℙ𝕒𝕤𝕤 password
    ]
    
    # Portal/Host patterns
    PORTAL_PATTERNS = [
        r'[Pp]ortal[:\s]+\s*(https?://[^\s]+)',
        r'👀\s*[^\s]+\s+(https?://[^\s]+)',  # 👀 ℙ𝕠𝕣𝕥𝕒𝕝 http://...
        r'[Hh]ost[:\s]+\s*(https?://[^\s]+)',
        r'[Ss]erver[:\s]+\s*(https?://[^\s]+)',
        r'🔰\s*[^\s]+\s+(https?://[^\s]+)',  # 🔰 ℝ𝕖𝕒𝕝 𝕌𝕣𝕝
    ]
    
    @classmethod
    def extract_links(cls, text):
        """Extract all IPTV links from text"""
        links = set()
        
        # Method 1: Direct URL extraction
        for pattern in cls.URL_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for m in matches:
                url = cls._clean_url(m)
                if cls._is_valid_iptv_url(url):
                    links.add(url)
        
        # Method 2: Build URLs from portal + credentials
        portals = []
        usernames = []
        passwords = []
        
        for pattern in cls.PORTAL_PATTERNS:
            portals.extend(re.findall(pattern, text, re.IGNORECASE))
        
        # Extract usernames
        user_matches = re.findall(r'[Uu]ser(?:name)?[:\s=]+\s*([A-Za-z0-9_.-]+)', text)
        usernames.extend(user_matches)
        user_matches2 = re.findall(r'👥[^A-Za-z0-9]*([A-Za-z0-9_.-]+)', text)
        usernames.extend(user_matches2)
        
        # Extract passwords
        pass_matches = re.findall(r'[Pp]ass(?:word)?[:\s=]+\s*([A-Za-z0-9_.-]+)', text)
        passwords.extend(pass_matches)
        pass_matches2 = re.findall(r'🔑[^A-Za-z0-9]*([A-Za-z0-9_.-]+)', text)
        passwords.extend(pass_matches2)
        
        # Build URLs from combinations
        for portal in portals:
            portal = cls._clean_url(portal)
            if portal:
                for i, user in enumerate(usernames):
                    pwd = passwords[i] if i < len(passwords) else ''
                    if user and pwd:
                        # Build get.php URL
                        base = portal.rstrip('/')
                        if ':' in base.split('/')[-1]:  # Has port
                            url = f"{base}/get.php?username={user}&password={pwd}&type=m3u_plus"
                        else:
                            url = f"{base}:8080/get.php?username={user}&password={pwd}&type=m3u_plus"
                        links.add(url)
        
        # Method 3: Look for M3U emoji patterns (🎬 𝕄𝟛𝕦)
        m3u_pattern = r'🎬[^h]*(https?://[^\s<>"\']+)'
        m3u_matches = re.findall(m3u_pattern, text)
        for m in m3u_matches:
            url = cls._clean_url(m)
            if cls._is_valid_iptv_url(url):
                links.add(url)
        
        return list(links)
    
    @classmethod
    def _clean_url(cls, url):
        """Clean and normalize URL"""
        if not url:
            return ''
        # Remove trailing punctuation
        url = url.rstrip('.,;:!?)]\'"')
        # Remove unicode fancy characters around URL
        url = re.sub(r'[^\x00-\x7F]+$', '', url)
        return url.strip()
    
    @classmethod
    def _is_valid_iptv_url(cls, url):
        """Check if URL looks like valid IPTV link"""
        if not url or not url.startswith('http'):
            return False
        # Must have either get.php, live/, or common IPTV patterns
        iptv_indicators = [
            'get.php', 'player_api.php', 'panel_api.php',
            '/live/', '/movie/', '/series/',
            '.m3u', '.m3u8', '.ts',
            'username=', 'password=',
        ]
        return any(ind in url.lower() for ind in iptv_indicators) or \
               re.search(r':\d{4,5}/', url)  # Has port number
    
    @classmethod
    def extract_expire_from_text(cls, text):
        """Extract expiry date from text"""
        patterns = [
            r'[Ee]xp(?:ire)?[:\s]+(\d{4}-\d{2}-\d{2})',
            r'📆\s*[^\d]*(\d{4}-\d{2}-\d{2})',
            r'[Ee]xp(?:ire)?[:\s]+(\d{2}[./]\d{2}[./]\d{4})',
        ]
        for p in patterns:
            m = re.search(p, text)
            if m:
                return m.group(1)
        return None

# ==================== CACHE & HTTP ====================
class Cache:
    def __init__(s, cap=500):
        s.d, s.cap = OrderedDict(), cap
    def get(s, k):
        if k in s.d: s.d.move_to_end(k); return s.d[k]
        return None
    def put(s, k, v):
        if k in s.d: s.d.move_to_end(k)
        s.d[k] = v
        if len(s.d) > s.cap: s.d.popitem(last=False)
    def clear(s): s.d.clear()

cache = Cache(500)

def mk_http():
    s = requests.Session()
    r = Retry(total=2, backoff_factor=0.3, status_forcelist=[500,502,503,504])
    a = HTTPAdapter(max_retries=r, pool_connections=20, pool_maxsize=30)
    s.mount('http://', a)
    s.mount('https://', a)
    s.headers.update({'User-Agent': 'VLC/3.0.20 LibVLC/3.0.20', 'Accept': '*/*', 'Connection': 'keep-alive'})
    return s

http = mk_http()

# ==================== PATH HELPERS ====================
def base_path():
    try:
        from android.storage import primary_external_storage_path
        return os.path.join(primary_external_storage_path(), 'Download')
    except: return os.path.expanduser('~')

def iptv_folder():
    p = os.path.join(base_path(), 'IPTV')
    try: os.makedirs(p, exist_ok=True)
    except: return base_path()
    return p

def app_path():
    try:
        from android.storage import app_storage_path
        return app_storage_path()
    except:
        p = os.path.join(os.path.expanduser('~'), '.iptv')
        os.makedirs(p, exist_ok=True)
        return p

def get_icon():
    """Get custom app icon from Download folder"""
    paths = [
        os.path.join(base_path(), 'icon.png'),
        os.path.join(base_path(), 'iptv_icon.png'),
        'icon.png',
    ]
    for p in paths:
        if os.path.exists(p):
            return p
    return None

def short_dom(url):
    try:
        d = urlparse(url).netloc
        if d.startswith('www.'): d = d[4:]
        p = d.split('.')
        return '.'.join(p[-2:])[:18] if len(p) > 2 else d[:18]
    except: return 'iptv'

def gc_(): gc.collect()

# ==================== EXPIRE DETECTION ====================
def get_expire(content, url):
    now = datetime.now()
    try:
        q = parse_qs(urlparse(url).query)
        for k in ['exp', 'expires', 'expire', 'e']:
            if k in q:
                ts = int(q[k][0])
                if ts > 1e12: ts //= 1000
                if 1704067200 < ts < 1893456000:
                    dt = datetime.fromtimestamp(ts)
                    if dt > now: return dt.strftime('%d.%m.%Y')
                    return f'{dt.strftime("%d.%m.%Y")} [EXPIRED]'
    except: pass
    for p in [r'[?&]exp[ire]*[s]?=(\d{10,13})', r'"exp[ire]*":\s*(\d{10,13})']:
        for m in re.findall(p, (content or '')[:5000], re.I):
            try:
                ts = int(m)
                if ts > 1e12: ts //= 1000
                if 1704067200 < ts < 1893456000:
                    dt = datetime.fromtimestamp(ts)
                    if dt > now: return dt.strftime('%d.%m.%Y')
                    return f'{dt.strftime("%d.%m.%Y")} [EXPIRED]'
            except: pass
    return ''

# ==================== COUNTRY DETECTION ====================
@lru_cache(3000)
def detect_c(grp):
    if not grp: return 'other'
    g = grp.lower()
    for cid, cd in COUNTRIES.items():
        for code in cd['c']:
            if g == code or g.startswith(code+' ') or g.startswith(code+'-') or g.endswith(' '+code):
                return cid
            if re.search(rf'\b{re.escape(code)}\b', g): return cid
    return 'other'

# ==================== M3U PARSER ====================
GRP_RE = re.compile(r'group-title="([^"]*)"')
LOGO_RE = re.compile(r'tvg-logo="([^"]*)"')
NAME_RE = re.compile(r',([^,]+)$')

def parse_m3u(content, url=''):
    chs, grps = [], {}
    exp = get_expire(content, url)
    cur = None
    for ln in content.split('\n'):
        ln = ln.strip()
        if ln.startswith('#EXTINF:'):
            cur = {'name': '', 'group': 'Diger', 'logo': '', 'url': ''}
            m = GRP_RE.search(ln)
            if m and m.group(1): cur['group'] = m.group(1).strip()
            m = LOGO_RE.search(ln)
            if m: cur['logo'] = m.group(1)
            m = NAME_RE.search(ln)
            if m: cur['name'] = m.group(1).strip()
        elif cur and ln.startswith(('http://', 'https://', 'rtmp://')):
            cur['url'] = ln
            chs.append(cur)
            g = cur['group']
            if g not in grps:
                grps[g] = {'chs': [], 'logo': cur.get('logo', ''), 'cty': detect_c(g)}
            grps[g]['chs'].append(cur)
            cur = None
    return chs, grps, exp

def gen_m3u(chs):
    lines = ['#EXTM3U']
    for c in chs:
        ext = '#EXTINF:-1'
        if c.get('logo'): ext += f' tvg-logo="{c["logo"]}"'
        if c.get('group'): ext += f' group-title="{c["group"]}"'
        ext += f',{c.get("name", "CH")}'
        lines.append(ext)
        lines.append(c.get('url', ''))
    return '\n'.join(lines)

# ==================== LINK TESTING ====================
def test_link(url, mode='deep', timeout=12):
    k = hashlib.md5(url.encode()).hexdigest()[:12]
    v = cache.get(k)
    if v: return v
    
    try:
        if mode == 'quick':
            r = http.head(url, timeout=timeout, allow_redirects=True)
            result = (r.status_code == 200, f"HTTP {r.status_code}")
        else:
            r = http.get(url, timeout=timeout, stream=True)
            if r.status_code != 200:
                return False, f"HTTP {r.status_code}"
            c, t = '', 0
            for ch in r.iter_content(8192, decode_unicode=True):
                if isinstance(ch, bytes): c += ch.decode('utf-8', errors='ignore')
                else: c += ch
                t += len(ch) if isinstance(ch, str) else len(ch)
                if t > 50000: break
            r.close()
            if len(c) < 50:
                result = (False, "Empty")
            elif '#EXTINF' in c:
                chs, _, _ = parse_m3u(c, url)
                result = (True, f"{len(chs)} ch") if chs else (False, "No ch")
            else:
                result = (True, "Stream") if t > 3000 else (False, "Invalid")
        cache.put(k, result)
        return result
    except requests.Timeout:
        return False, "Timeout"
    except Exception as e:
        return False, "Error"

def dedup(chs):
    seen, uni = {}, []
    for c in chs:
        u = c.get('url', '')
        if u and u not in seen: seen[u] = 1; uni.append(c)
    return uni, len(chs) - len(uni)

# ==================== DATABASE ====================
class DB:
    def __init__(s):
        s.path = os.path.join(app_path(), 'iptv.db')
        s.cn = None
        s._init()
    
    def _cn(s):
        if not s.cn:
            s.cn = sqlite3.connect(s.path, check_same_thread=False)
            s.cn.row_factory = sqlite3.Row
        return s.cn
    
    def _init(s):
        c = s._cn().cursor()
        c.execute('CREATE TABLE IF NOT EXISTS cfg (k TEXT PRIMARY KEY, v TEXT)')
        c.execute('CREATE TABLE IF NOT EXISTS fav (id INTEGER PRIMARY KEY, url TEXT UNIQUE, name TEXT, exp TEXT, cnt INTEGER DEFAULT 0)')
        c.execute('CREATE TABLE IF NOT EXISTS st (id INTEGER PRIMARY KEY, dt TEXT UNIQUE, te INTEGER DEFAULT 0, wo INTEGER DEFAULT 0, ch INTEGER DEFAULT 0, fi INTEGER DEFAULT 0)')
        s._cn().commit()
        for k, v in {'theme': 'cyberpunk', 'mode': 'deep', 'fmt': 'm3u8', 'dup': 'true', 'to': '12'}.items():
            c.execute('INSERT OR IGNORE INTO cfg VALUES (?,?)', (k, v))
        s._cn().commit()
    
    def get(s, k, d=None):
        c = s._cn().cursor()
        c.execute('SELECT v FROM cfg WHERE k=?', (k,))
        r = c.fetchone()
        return r['v'] if r else d
    
    def set(s, k, v):
        s._cn().cursor().execute('INSERT OR REPLACE INTO cfg VALUES (?,?)', (k, str(v)))
        s._cn().commit()
    
    def add_fav(s, u, n='', e='', c=0):
        try:
            s._cn().cursor().execute('INSERT OR REPLACE INTO fav (url,name,exp,cnt) VALUES (?,?,?,?)', (u, n or short_dom(u), e, c))
            s._cn().commit()
            return True
        except: return False
    
    def del_fav(s, u):
        s._cn().cursor().execute('DELETE FROM fav WHERE url=?', (u,))
        s._cn().commit()
    
    def favs(s):
        c = s._cn().cursor()
        c.execute('SELECT * FROM fav ORDER BY id DESC')
        return [dict(r) for r in c.fetchall()]
    
    def stat(s, te=0, wo=0, ch=0, fi=0):
        dt = datetime.now().strftime('%Y-%m-%d')
        c = s._cn().cursor()
        c.execute('SELECT * FROM st WHERE dt=?', (dt,))
        if c.fetchone(): c.execute('UPDATE st SET te=te+?,wo=wo+?,ch=ch+?,fi=fi+? WHERE dt=?', (te, wo, ch, fi, dt))
        else: c.execute('INSERT INTO st (dt,te,wo,ch,fi) VALUES (?,?,?,?,?)', (dt, te, wo, ch, fi))
        s._cn().commit()
    
    def stats(s):
        c = s._cn().cursor()
        c.execute('SELECT SUM(te) as t, SUM(wo) as w, SUM(ch) as c, SUM(fi) as f FROM st')
        r = c.fetchone()
        return {'te': r['t'] or 0, 'wo': r['w'] or 0, 'ch': r['c'] or 0, 'fi': r['f'] or 0}
    
    def close(s):
        if s.cn: s.cn.close()

db = DB()

# ==================== KIVY LANG ====================
KV = '''
#:import dp kivy.metrics.dp
#:import sp kivy.metrics.sp
#:import Window kivy.core.window.Window

<IconLabel@Label>:
    font_name: 'MDI' if app.has_mdi else 'Roboto'
    font_size: sp(24)
    color: 1, 1, 1, 1
    size_hint: None, None
    size: dp(48), dp(48)
    halign: 'center'
    valign: 'middle'
    text_size: self.size

<GlassCard@BoxLayout>:
    canvas.before:
        Color:
            rgba: app.tc('card')
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(16)]
        Color:
            rgba: app.tc('gradient1')[0], app.tc('gradient1')[1], app.tc('gradient1')[2], 0.1
        Line:
            rounded_rectangle: self.x, self.y, self.width, self.height, dp(16)
            width: dp(1.5)

<AccentBtn@Button>:
    background_normal: ''
    background_color: 0, 0, 0, 0
    font_size: sp(14)
    bold: True
    size_hint_y: None
    height: dp(52)
    canvas.before:
        Color:
            rgba: app.tc('acc')
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(14)]

<GhostBtn@Button>:
    background_normal: ''
    background_color: 0, 0, 0, 0
    font_size: sp(13)
    size_hint_y: None
    height: dp(46)
    canvas.before:
        Color:
            rgba: app.tc('card')
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(12)]

<BaseScreen>:
    canvas.before:
        Color:
            rgba: app.tc('bg')
        Rectangle:
            pos: self.pos
            size: self.size

<AnimProg>:
    canvas:
        Color:
            rgba: app.tc('card2')
        RoundedRectangle:
            pos: self.x, self.center_y - dp(12)
            size: self.width, dp(24)
            radius: [dp(12)]
        Color:
            rgba: app.tc('acc')
        RoundedRectangle:
            pos: self.x + dp(4), self.center_y - dp(8)
            size: max(0, (self.width - dp(8)) * self.v / 100.0), dp(16)
            radius: [dp(8)]

<RV>:
    viewclass: 'GrpRow'
    RecycleBoxLayout:
        default_size: None, dp(72)
        default_size_hint: 1, None
        size_hint_y: None
        height: self.minimum_height
        orientation: 'vertical'
        spacing: dp(10)
        padding: dp(6)

<GrpRow>:
    orientation: 'horizontal'
    size_hint_y: None
    height: dp(72)
    padding: [dp(16), dp(12)]
    spacing: dp(14)
    canvas.before:
        Color:
            rgba: app.tc('ok') if self.sel else app.tc('card')
            a: 0.2 if self.sel else 1
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(14)]
    Label:
        text: root.flag
        font_size: sp(24)
        size_hint_x: None
        width: dp(40)
    BoxLayout:
        orientation: 'vertical'
        spacing: dp(4)
        Label:
            text: root.dname
            font_size: sp(14)
            color: app.tc('t1')
            text_size: self.size
            halign: 'left'
            valign: 'middle'
            shorten: True
        Label:
            text: str(root.cnt) + ' kanal'
            font_size: sp(11)
            color: app.tc('t3')
            text_size: self.size
            halign: 'left'
    Button:
        size_hint: None, None
        size: dp(50), dp(50)
        text: 'OK' if root.sel else '+'
        font_size: sp(16)
        bold: True
        background_normal: ''
        background_color: app.tc('ok') if root.sel else app.tc('acc')
        on_press: root.toggle()
'''

Builder.load_string(KV)

# ==================== WIDGETS ====================
class BaseScreen(Screen):
    def on_pre_enter(self):
        # Handle orientation
        pass

class AnimProg(Widget):
    v = NumericProperty(0)
    def sv(s, val, anim=True):
        val = min(100, max(0, val))
        if anim: Animation(v=val, d=0.25, t='out_quad').start(s)
        else: s.v = val

class GrpRow(RecycleDataViewBehavior, BoxLayout):
    idx = None
    sel = BooleanProperty(False)
    gn = StringProperty('')
    cnt = NumericProperty(0)
    cty = StringProperty('other')
    flag = StringProperty('')
    dname = StringProperty('')
    cb = ObjectProperty(None)
    
    def refresh_view_attrs(s, rv, idx, data):
        s.idx = idx
        s.gn = data.get('gn', '')
        s.cnt = data.get('cnt', 0)
        s.sel = data.get('sel', False)
        s.cty = data.get('cty', 'other')
        s.cb = data.get('cb', None)
        s.dname = s.gn[:32] + ('...' if len(s.gn) > 32 else '')
        cd = COUNTRIES.get(s.cty, COUNTRIES['other'])
        s.flag = cd['f']
        return super().refresh_view_attrs(rv, idx, data)
    
    def toggle(s):
        s.sel = not s.sel
        if s.cb: s.cb(s.gn, s.sel, s.idx)

class RV(RecycleView): pass

# ==================== ICON BUTTON ====================
def icon_btn(icon, color, on_press, size=48):
    """Create icon button"""
    btn = Button(
        text=icon,
        font_name=ICON_FONT,
        font_size=sp(22),
        size_hint=(None, None),
        size=(dp(size), dp(size)),
        background_normal='',
        background_color=[0,0,0,0],
        color=color
    )
    btn.bind(on_press=on_press)
    
    # Add background
    with btn.canvas.before:
        Color(*get_color_from_hex(T('card')))
        btn._bg = RoundedRectangle(pos=btn.pos, size=btn.size, radius=[dp(12)])
    btn.bind(pos=lambda w,v: setattr(w._bg, 'pos', w.pos))
    btn.bind(size=lambda w,v: setattr(w._bg, 'size', w.size))
    
    return btn

# ==================== SCREENS ====================
class WelcomeScreen(BaseScreen):
    def on_enter(s):
        s.clear_widgets()
        Clock.schedule_once(lambda dt: s.build(), 0.05)
    
    def build(s):
        app = App.get_running_app()
        
        # Responsive layout
        is_landscape = Window.width > Window.height
        padding = dp(24) if is_landscape else dp(20)
        
        root = BoxLayout(orientation='vertical', padding=padding, spacing=dp(16))
        
        # ===== HEADER =====
        hdr = BoxLayout(size_hint_y=None, height=dp(120) if not is_landscape else dp(80), spacing=dp(12))
        
        # Logo
        logo_box = BoxLayout(size_hint_x=None, width=dp(80))
        icon_path = get_icon()
        if icon_path and os.path.exists(icon_path):
            logo = Image(source=icon_path, size_hint=(None, None), size=(dp(64), dp(64)))
        else:
            # Fallback logo
            logo = Label(text=MDI.TV, font_name=ICON_FONT, font_size=sp(48), color=app.tc('acc'))
        logo_box.add_widget(logo)
        hdr.add_widget(logo_box)
        
        # Title
        title_box = BoxLayout(orientation='vertical', spacing=dp(4))
        title_box.add_widget(Label(text=APP_NAME, font_size=sp(24), bold=True, color=app.tc('t1'), halign='left', valign='bottom', size_hint_y=0.6))
        title_box.add_widget(Label(text=f'v{APP_VER} | {"MDI Icons" if HAS_MDI else "Text Mode"}', font_size=sp(11), color=app.tc('t3'), halign='left', valign='top', size_hint_y=0.4))
        hdr.add_widget(title_box)
        
        # Settings button
        settings_btn = icon_btn(MDI.COG, app.tc('t1'), lambda x: s.go('st'))
        hdr.add_widget(settings_btn)
        root.add_widget(hdr)
        
        # ===== STATS =====
        st = db.stats()
        stats_box = BoxLayout(size_hint_y=None, height=dp(80), spacing=dp(10))
        
        for val, lbl, clr, icon in [
            (st['te'], 'Test', 'info', MDI.REFRESH),
            (st['wo'], 'OK', 'ok', MDI.CHECK),
            (st['ch'], 'Kanal', 'acc', MDI.TV),
            (st['fi'], 'Dosya', 'warn', MDI.FILE)
        ]:
            card = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(2))
            with card.canvas.before:
                Color(*app.tc('card'))
                card._bg = RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(12)])
            card.bind(pos=s._upd, size=s._upd)
            
            row = BoxLayout(size_hint_y=0.6)
            row.add_widget(Label(text=icon, font_name=ICON_FONT, font_size=sp(16), color=app.tc(clr), size_hint_x=0.3))
            row.add_widget(Label(text=str(val), font_size=sp(20), bold=True, color=app.tc(clr)))
            card.add_widget(row)
            card.add_widget(Label(text=lbl, font_size=sp(10), color=app.tc('t3'), size_hint_y=0.4))
            stats_box.add_widget(card)
        root.add_widget(stats_box)
        
        # ===== INFO =====
        info_box = BoxLayout(size_hint_y=None, height=dp(30), spacing=dp(8))
        info_box.add_widget(Label(text=MDI.FOLDER, font_name=ICON_FONT, font_size=sp(16), color=app.tc('info'), size_hint_x=None, width=dp(30)))
        info_box.add_widget(Label(text='Kayit: Download/IPTV/', font_size=sp(11), color=app.tc('t3'), halign='left'))
        root.add_widget(info_box)
        
        # ===== MENU =====
        menu = ScrollView()
        
        if is_landscape:
            ml = GridLayout(cols=2, spacing=dp(12), size_hint_y=None, padding=[0, dp(8)])
        else:
            ml = BoxLayout(orientation='vertical', spacing=dp(14), size_hint_y=None, padding=[0, dp(8)])
        ml.bind(minimum_height=ml.setter('height'))
        
        items = [
            ('Manuel Duzenleme', 'URL gir, kanallari duzenle', MDI.EDIT, 'acc', 'mi'),
            ('Otomatik Islem', 'Akilli link tespit, toplu test', MDI.MAGIC, 'ok', 'ai'),
            (f'Favoriler ({len(db.favs())})', 'Kayitli IPTV linkleri', MDI.STAR, 'warn', 'fv'),
            ('Ayarlar', 'Tema, test ayarlari', MDI.COG, 'info', 'st'),
        ]
        
        for title, desc, icon, clr, scr in items:
            card = BoxLayout(orientation='horizontal', padding=dp(16), spacing=dp(14), size_hint_y=None, height=dp(90))
            with card.canvas.before:
                Color(*app.tc('card'))
                card._bg = RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(16)])
            card.bind(pos=s._upd, size=s._upd)
            
            # Icon
            icon_box = BoxLayout(size_hint_x=None, width=dp(50))
            icon_lbl = Label(text=icon, font_name=ICON_FONT, font_size=sp(28), color=app.tc(clr))
            icon_box.add_widget(icon_lbl)
            card.add_widget(icon_box)
            
            # Info
            info = BoxLayout(orientation='vertical', spacing=dp(4))
            info.add_widget(Label(text=title, font_size=sp(15), bold=True, color=app.tc('t1'), halign='left', valign='bottom', text_size=(dp(180), None)))
            info.add_widget(Label(text=desc, font_size=sp(11), color=app.tc('t3'), halign='left', valign='top', text_size=(dp(180), None)))
            card.add_widget(info)
            
            # Button
            btn = Button(text=MDI.NEXT, font_name=ICON_FONT, font_size=sp(20), size_hint=(None, None), size=(dp(50), dp(50)), background_normal='', background_color=app.tc(clr))
            btn.bind(on_press=lambda x, sc=scr: s.go(sc))
            card.add_widget(btn)
            
            ml.add_widget(card)
        
        menu.add_widget(ml)
        root.add_widget(menu)
        s.add_widget(root)
    
    def _upd(s, w, v):
        if hasattr(w, '_bg'): w._bg.pos, w._bg.size = w.pos, w.size
    
    def go(s, scr):
        s.manager.transition = SlideTransition(direction='left')
        s.manager.current = scr


class AutoInputScreen(BaseScreen):
    """Smart link detection from messy text"""
    def on_enter(s):
        s.clear_widgets()
        s.tm = db.get('mode', 'deep')
        Clock.schedule_once(lambda dt: s.build(), 0.05)
    
    def build(s):
        app = App.get_running_app()
        is_landscape = Window.width > Window.height
        
        root = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(12))
        
        # Top bar
        top = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(12))
        back_btn = icon_btn(MDI.BACK, app.tc('t1'), lambda x: s.back())
        top.add_widget(back_btn)
        top.add_widget(Label(text='Akilli Link Tespit', font_size=sp(18), bold=True, color=app.tc('t1')))
        
        # AI badge
        ai_box = BoxLayout(size_hint_x=None, width=dp(60), padding=dp(4))
        with ai_box.canvas.before:
            Color(*app.tc('acc')[:3], 0.2)
            ai_box._bg = RoundedRectangle(pos=ai_box.pos, size=ai_box.size, radius=[dp(8)])
        ai_box.bind(pos=s._upd, size=s._upd)
        ai_box.add_widget(Label(text=f'{MDI.AI} AI', font_name=ICON_FONT, font_size=sp(12), color=app.tc('acc')))
        top.add_widget(ai_box)
        root.add_widget(top)
        
        # Info
        info_card = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(6), size_hint_y=None, height=dp(70))
        with info_card.canvas.before:
            Color(*app.tc('ok')[:3], 0.15)
            info_card._bg = RoundedRectangle(pos=info_card.pos, size=info_card.size, radius=[dp(12)])
        info_card.bind(pos=s._upd, size=s._upd)
        
        info_card.add_widget(Label(text=f'{MDI.MAGIC} Karisik metin yapistirin - linkler otomatik bulunur!', font_name=ICON_FONT, font_size=sp(12), color=app.tc('ok'), halign='left'))
        info_card.add_widget(Label(text='Telegram mesajlari, emoji iceren metinler desteklenir', font_size=sp(10), color=app.tc('t3'), halign='left'))
        root.add_widget(info_card)
        
        # Text input
        inp_card = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(8))
        with inp_card.canvas.before:
            Color(*app.tc('card'))
            inp_card._bg = RoundedRectangle(pos=inp_card.pos, size=inp_card.size, radius=[dp(14)])
        inp_card.bind(pos=s._upd, size=s._upd)
        
        s.txt_inp = TextInput(
            hint_text='Buraya karisik metin, Telegram mesaji veya IPTV linkleri yapistirin...\n\nOrnek:\n🎬 𝕄𝟛𝕦 http://server.com:8080/get.php?username=xxx&password=yyy\n\nveya normal linkler:\nhttp://example.com/get.php?...',
            multiline=True, font_size=sp(12), background_color=app.tc('bg2'), foreground_color=app.tc('t1'), padding=[dp(12), dp(12)]
        )
        inp_card.add_widget(s.txt_inp)
        
        btn_row = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(8))
        paste_btn = Button(text=f'{MDI.PASTE} Yapistir', font_name=ICON_FONT, font_size=sp(12), background_normal='', background_color=app.tc('acc'))
        paste_btn.bind(on_press=lambda x: setattr(s.txt_inp, 'text', Clipboard.paste() or ''))
        btn_row.add_widget(paste_btn)
        
        clear_btn = Button(text=f'{MDI.DELETE} Temizle', font_name=ICON_FONT, font_size=sp(12), background_normal='', background_color=app.tc('card2'))
        clear_btn.bind(on_press=lambda x: setattr(s.txt_inp, 'text', ''))
        btn_row.add_widget(clear_btn)
        inp_card.add_widget(btn_row)
        root.add_widget(inp_card)
        
        # Test mode
        mode_card = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(8), size_hint_y=None, height=dp(90))
        with mode_card.canvas.before:
            Color(*app.tc('card'))
            mode_card._bg = RoundedRectangle(pos=mode_card.pos, size=mode_card.size, radius=[dp(14)])
        mode_card.bind(pos=s._upd, size=s._upd)
        
        mode_card.add_widget(Label(text='Test Modu', font_size=sp(12), color=app.tc('t3'), halign='left', size_hint_y=None, height=dp(20)))
        
        mode_row = BoxLayout(spacing=dp(10), size_hint_y=None, height=dp(44))
        s.qb = ToggleButton(text=f'{MDI.BOLT} Hizli', font_name=ICON_FONT, group='m', state='down' if s.tm == 'quick' else 'normal', font_size=sp(12), background_normal='', background_color=app.tc('acc') if s.tm == 'quick' else app.tc('card2'))
        s.qb.bind(on_press=lambda x: s.sm('quick'))
        mode_row.add_widget(s.qb)
        
        s.db = ToggleButton(text=f'{MDI.SEARCH} Derin', font_name=ICON_FONT, group='m', state='down' if s.tm == 'deep' else 'normal', font_size=sp(12), background_normal='', background_color=app.tc('acc') if s.tm == 'deep' else app.tc('card2'))
        s.db.bind(on_press=lambda x: s.sm('deep'))
        mode_row.add_widget(s.db)
        mode_card.add_widget(mode_row)
        root.add_widget(mode_card)
        
        # Start button
        start_btn = Button(text=f'{MDI.ROCKET} Linkleri Bul ve Test Et', font_name=ICON_FONT, font_size=sp(15), bold=True, size_hint_y=None, height=dp(56), background_normal='', background_color=app.tc('ok'))
        start_btn.bind(on_press=s.start)
        root.add_widget(start_btn)
        
        s.add_widget(root)
    
    def _upd(s, w, v):
        if hasattr(w, '_bg'): w._bg.pos, w._bg.size = w.pos, w.size
    
    def sm(s, m):
        app = App.get_running_app()
        s.tm = m
        db.set('mode', m)
        s.qb.background_color = app.tc('acc') if m == 'quick' else app.tc('card2')
        s.db.background_color = app.tc('acc') if m == 'deep' else app.tc('card2')
    
    def start(s, *a):
        txt = s.txt_inp.text.strip()
        if not txt:
            return s.popup(MDI.ALERT, 'Metin girin!')
        
        # Smart link extraction
        links = SmartLinkExtractor.extract_links(txt)
        
        if not links:
            return s.popup(MDI.CLOSE, 'Link bulunamadi!\n\nMetinde IPTV linki tespit edilemedi.')
        
        # Show found links
        s.show_found(links)
    
    def show_found(s, links):
        """Show found links and start test"""
        app = App.get_running_app()
        
        c = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(12))
        
        # Header
        hdr = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        hdr.add_widget(Label(text=MDI.CHECK, font_name=ICON_FONT, font_size=sp(32), color=app.tc('ok'), size_hint_x=None, width=dp(50)))
        hdr.add_widget(Label(text=f'{len(links)} Link Bulundu!', font_size=sp(18), bold=True, color=app.tc('t1')))
        c.add_widget(hdr)
        
        # Links list
        scroll = ScrollView(size_hint_y=None, height=dp(150))
        lst = BoxLayout(orientation='vertical', spacing=dp(4), size_hint_y=None)
        lst.bind(minimum_height=lst.setter('height'))
        
        for i, lk in enumerate(links[:10]):
            lst.add_widget(Label(text=f'{i+1}. {short_dom(lk)}', font_size=sp(11), color=app.tc('t2'), size_hint_y=None, height=dp(20), halign='left'))
        
        if len(links) > 10:
            lst.add_widget(Label(text=f'... ve {len(links) - 10} link daha', font_size=sp(10), color=app.tc('t4'), size_hint_y=None, height=dp(18)))
        
        scroll.add_widget(lst)
        c.add_widget(scroll)
        
        # Buttons
        btn_row = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(10))
        
        cancel_btn = Button(text='Iptal', font_size=sp(13), background_normal='', background_color=app.tc('card'))
        
        test_btn = Button(text=f'{MDI.PLAY} Test Baslat', font_name=ICON_FONT, font_size=sp(13), bold=True, background_normal='', background_color=app.tc('ok'))
        
        p = Popup(title='', content=c, size_hint=(0.9, 0.6), separator_height=0)
        
        cancel_btn.bind(on_press=p.dismiss)
        
        def start_test(x):
            p.dismiss()
            app = App.get_running_app()
            app.tlks, app.tm = links, s.tm
            s.manager.current = 'ts'
        
        test_btn.bind(on_press=start_test)
        
        btn_row.add_widget(cancel_btn)
        btn_row.add_widget(test_btn)
        c.add_widget(btn_row)
        
        p.open()
    
    def popup(s, icon, msg):
        app = App.get_running_app()
        c = BoxLayout(orientation='vertical', padding=dp(24), spacing=dp(16))
        c.add_widget(Label(text=icon, font_name=ICON_FONT, font_size=sp(40), color=app.tc('warn')))
        c.add_widget(Label(text=msg, font_size=sp(13), color=app.tc('t1'), halign='center'))
        btn = Button(text='Tamam', size_hint=(0.5, None), height=dp(44), pos_hint={'center_x': 0.5}, background_normal='', background_color=app.tc('warn'))
        p = Popup(title='', content=c, size_hint=(0.85, 0.45), separator_height=0)
        btn.bind(on_press=p.dismiss)
        c.add_widget(btn)
        p.open()
    
    def back(s):
        s.manager.transition = SlideTransition(direction='right')
        s.manager.current = 'ws'


class ManualInputScreen(BaseScreen):
    def on_enter(s):
        s.clear_widgets()
        s.fmt = db.get('fmt', 'm3u8')
        s.dup = db.get('dup', 'true') == 'true'
        Clock.schedule_once(lambda dt: s.build(), 0.05)
    
    def build(s):
        app = App.get_running_app()
        root = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(14))
        
        # Top bar
        top = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(12))
        back_btn = icon_btn(MDI.BACK, app.tc('t1'), lambda x: s.back())
        top.add_widget(back_btn)
        top.add_widget(Label(text='Manuel Duzenleme', font_size=sp(18), bold=True, color=app.tc('t1')))
        root.add_widget(top)
        
        # URL input card
        url_card = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(10), size_hint_y=None, height=dp(140))
        with url_card.canvas.before:
            Color(*app.tc('card'))
            url_card._bg = RoundedRectangle(pos=url_card.pos, size=url_card.size, radius=[dp(16)])
        url_card.bind(pos=s._upd, size=s._upd)
        
        url_card.add_widget(Label(text=f'{MDI.LINK} Playlist URL', font_name=ICON_FONT, font_size=sp(12), color=app.tc('t3'), halign='left', size_hint_y=None, height=dp(20)))
        
        url_row = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        s.url_inp = TextInput(hint_text='https://example.com/get.php?username=...', multiline=False, font_size=sp(12), background_color=app.tc('bg2'), foreground_color=app.tc('t1'), padding=[dp(14), dp(14)])
        url_row.add_widget(s.url_inp)
        
        paste_btn = Button(text=MDI.PASTE, font_name=ICON_FONT, font_size=sp(20), size_hint=(None, None), size=(dp(50), dp(50)), background_normal='', background_color=app.tc('acc'))
        paste_btn.bind(on_press=lambda x: setattr(s.url_inp, 'text', Clipboard.paste() or ''))
        url_row.add_widget(paste_btn)
        url_card.add_widget(url_row)
        
        # Quick fav
        favs = db.favs()
        if favs:
            fav_btn = Button(text=f'{MDI.STAR} {favs[0]["name"][:22]}', font_name=ICON_FONT, font_size=sp(10), size_hint_y=None, height=dp(30), background_normal='', background_color=app.tc('warn')[:3]+[0.3])
            fav_btn.bind(on_press=lambda x: setattr(s.url_inp, 'text', favs[0]['url']))
            url_card.add_widget(fav_btn)
        root.add_widget(url_card)
        
        # Format card
        fmt_card = BoxLayout(orientation='vertical', padding=dp(14), spacing=dp(8), size_hint_y=None, height=dp(90))
        with fmt_card.canvas.before:
            Color(*app.tc('card'))
            fmt_card._bg = RoundedRectangle(pos=fmt_card.pos, size=fmt_card.size, radius=[dp(16)])
        fmt_card.bind(pos=s._upd, size=s._upd)
        
        fmt_card.add_widget(Label(text='Cikti Formati', font_size=sp(11), color=app.tc('t3'), halign='left', size_hint_y=None, height=dp(18)))
        
        fmt_row = BoxLayout(spacing=dp(10), size_hint_y=None, height=dp(44))
        s.fmt_btns = {}
        for fid in ['m3u', 'm3u8', 'txt']:
            is_sel = fid == s.fmt
            btn = ToggleButton(text=fid.upper(), group='fmt', state='down' if is_sel else 'normal', font_size=sp(12), background_normal='', background_color=app.tc('acc') if is_sel else app.tc('card2'))
            btn.fid = fid
            btn.bind(on_press=s.on_fmt)
            s.fmt_btns[fid] = btn
            fmt_row.add_widget(btn)
        fmt_card.add_widget(fmt_row)
        root.add_widget(fmt_card)
        
        # Options
        opt_row = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(10))
        dup_btn = ToggleButton(text=f'{MDI.FILTER} Duplicate Temizle', font_name=ICON_FONT, state='down' if s.dup else 'normal', font_size=sp(12), background_normal='', background_color=app.tc('ok') if s.dup else app.tc('card'))
        dup_btn.bind(on_press=lambda x: setattr(s, 'dup', x.state == 'down'))
        opt_row.add_widget(dup_btn)
        root.add_widget(opt_row)
        
        root.add_widget(Widget())
        
        # Load button
        load_btn = Button(text=f'{MDI.DOWNLOAD} Kanallari Yukle', font_name=ICON_FONT, font_size=sp(15), bold=True, size_hint_y=None, height=dp(56), background_normal='', background_color=app.tc('ok'))
        load_btn.bind(on_press=s.load)
        root.add_widget(load_btn)
        
        s.add_widget(root)
    
    def _upd(s, w, v):
        if hasattr(w, '_bg'): w._bg.pos, w._bg.size = w.pos, w.size
    
    def on_fmt(s, btn):
        app = App.get_running_app()
        s.fmt = btn.fid
        for f, b in s.fmt_btns.items():
            b.background_color = app.tc('acc') if f == s.fmt else app.tc('card2')
    
    def load(s, *a):
        url = s.url_inp.text.strip()
        if not url:
            return s.popup(MDI.ALERT, 'URL girin!')
        if not url.startswith('http'):
            return s.popup(MDI.CLOSE, 'Gecersiz URL!')
        s.show_load()
        threading.Thread(target=s._load, args=(url,), daemon=True).start()
    
    def _load(s, url):
        try:
            Clock.schedule_once(lambda dt: s.upd_load(10, 'Baglaniyor...'))
            r = http.get(url, timeout=30)
            Clock.schedule_once(lambda dt: s.upd_load(50, 'Ayristiriliyor...'))
            chs, grps, exp = parse_m3u(r.text, url)
            if not chs:
                return Clock.schedule_once(lambda dt: s._err('Kanal bulunamadi!'))
            Clock.schedule_once(lambda dt: s.upd_load(80, 'Isleniyor...'))
            if s.dup:
                chs, _ = dedup(chs)
                grps = {}
                for c in chs:
                    g = c['group']
                    if g not in grps: grps[g] = {'chs': [], 'logo': c.get('logo', ''), 'cty': detect_c(g)}
                    grps[g]['chs'].append(c)
            Clock.schedule_once(lambda dt: s.upd_load(100, 'Tamamlandi!'))
            Clock.schedule_once(lambda dt: s._ok(chs, grps, exp, url), 0.2)
        except Exception as e:
            Clock.schedule_once(lambda dt: s._err(str(e)[:30]))
    
    def _ok(s, chs, grps, exp, url):
        s.hide_load()
        app = App.get_running_app()
        app.chs, app.grps, app.exp, app.surl, app.fmt = chs, grps, exp, url, s.fmt
        gc_()
        s.manager.current = 'cl'
    
    def _err(s, msg):
        s.hide_load()
        s.popup(MDI.CLOSE, msg)
    
    def show_load(s):
        app = App.get_running_app()
        c = BoxLayout(orientation='vertical', padding=dp(24), spacing=dp(14))
        c.add_widget(Label(text=MDI.REFRESH, font_name=ICON_FONT, font_size=sp(40), color=app.tc('acc')))
        s.l_msg = Label(text='Baslatiliyor...', font_size=sp(13), color=app.tc('t1'))
        c.add_widget(s.l_msg)
        s.l_prog = AnimProg(size_hint_y=None, height=dp(24))
        c.add_widget(s.l_prog)
        s.l_pct = Label(text='%0', font_size=sp(22), bold=True, color=app.tc('acc'))
        c.add_widget(s.l_pct)
        s._pop = Popup(title='', content=c, size_hint=(0.85, 0.45), auto_dismiss=False, separator_height=0)
        s._pop.open()
    
    def upd_load(s, pct, msg):
        if hasattr(s, 'l_prog'):
            s.l_prog.sv(pct)
            s.l_pct.text = f'%{int(pct)}'
            s.l_msg.text = msg
    
    def hide_load(s):
        if hasattr(s, '_pop'): s._pop.dismiss()
    
    def popup(s, icon, msg):
        app = App.get_running_app()
        c = BoxLayout(orientation='vertical', padding=dp(24), spacing=dp(16))
        c.add_widget(Label(text=icon, font_name=ICON_FONT, font_size=sp(40), color=app.tc('warn')))
        c.add_widget(Label(text=msg, font_size=sp(13), color=app.tc('t1'), halign='center'))
        btn = Button(text='Tamam', size_hint=(0.5, None), height=dp(44), pos_hint={'center_x': 0.5}, background_normal='', background_color=app.tc('warn'))
        p = Popup(title='', content=c, size_hint=(0.8, 0.4), separator_height=0)
        btn.bind(on_press=p.dismiss)
        c.add_widget(btn)
        p.open()
    
    def back(s):
        s.manager.transition = SlideTransition(direction='right')
        s.manager.current = 'ws'


class ChannelListScreen(BaseScreen):
    def on_enter(s):
        s.clear_widgets()
        s.sel = set()
        Clock.schedule_once(lambda dt: s.build(), 0.05)
    
    def build(s):
        app = App.get_running_app()
        grps = getattr(app, 'grps', {})
        chs = getattr(app, 'chs', [])
        exp = getattr(app, 'exp', '')
        
        root = BoxLayout(orientation='vertical', padding=dp(14), spacing=dp(10))
        
        # Top bar
        top = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(10))
        back_btn = icon_btn(MDI.BACK, app.tc('t1'), lambda x: s.back())
        top.add_widget(back_btn)
        top.add_widget(Label(text='Kanal Gruplari', font_size=sp(17), bold=True, color=app.tc('t1')))
        fav_btn = icon_btn(MDI.STAR, app.tc('warn'), lambda x: s.add_fav())
        top.add_widget(fav_btn)
        root.add_widget(top)
        
        # Info bar
        info = BoxLayout(size_hint_y=None, height=dp(60), orientation='vertical', spacing=dp(2))
        info.add_widget(Label(text=f'{len(grps)} grup | {len(chs)} kanal', font_size=sp(12), color=app.tc('t3')))
        exp_clr = app.tc('err') if 'EXPIRED' in exp else app.tc('warn')
        info.add_widget(Label(text=f'{MDI.CALENDAR} Bitis: {exp or "Bilinmiyor"}', font_name=ICON_FONT, font_size=sp(11), color=exp_clr))
        s.sel_lbl = Label(text='Secilen: 0 grup', font_size=sp(11), color=app.tc('ok'))
        info.add_widget(s.sel_lbl)
        root.add_widget(info)
        
        # Search
        search_row = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
        s.search_inp = TextInput(hint_text=f'{MDI.SEARCH} Ara...', multiline=False, font_size=sp(12), background_color=app.tc('card'), foreground_color=app.tc('t1'), padding=[dp(14), dp(12)], size_hint_x=0.85)
        s.search_inp.bind(text=s.on_search)
        search_row.add_widget(s.search_inp)
        clr_btn = icon_btn(MDI.CLOSE, app.tc('t3'), lambda x: setattr(s.search_inp, 'text', ''), size=44)
        search_row.add_widget(clr_btn)
        root.add_widget(search_row)
        
        # RecycleView
        s.rv = RV()
        s.all_data = [{'gn': gn, 'cnt': len(gd['chs']), 'cty': gd.get('cty', 'other'), 'sel': False, 'cb': s.on_sel} for gn, gd in sorted(grps.items())]
        s.rv_data = s.all_data.copy()
        s.rv.data = s.rv_data
        root.add_widget(s.rv)
        
        # Bottom buttons
        btm = BoxLayout(size_hint_y=None, height=dp(54), spacing=dp(12))
        sel_all = Button(text='Tumunu Sec', font_size=sp(13), bold=True, background_normal='', background_color=app.tc('acc'))
        sel_all.bind(on_press=s.sel_all)
        btm.add_widget(sel_all)
        exp_btn = Button(text=f'{MDI.UPLOAD} Disa Aktar', font_name=ICON_FONT, font_size=sp(13), bold=True, background_normal='', background_color=app.tc('ok'))
        exp_btn.bind(on_press=s.export)
        btm.add_widget(exp_btn)
        root.add_widget(btm)
        
        s.add_widget(root)
    
    def on_search(s, inp, txt):
        s.rv_data = [d for d in s.all_data if txt.lower() in d['gn'].lower()] if txt else s.all_data.copy()
        s.rv.data = s.rv_data
    
    def on_sel(s, gn, sel, idx):
        for d in s.all_data:
            if d['gn'] == gn: d['sel'] = sel
        for d in s.rv_data:
            if d['gn'] == gn: d['sel'] = sel
        if sel: s.sel.add(gn)
        else: s.sel.discard(gn)
        grps = getattr(App.get_running_app(), 'grps', {})
        tot = sum(len(grps[g]['chs']) for g in s.sel if g in grps)
        s.sel_lbl.text = f'Secilen: {len(s.sel)} grup ({tot} kanal)'
    
    def sel_all(s, *a):
        grps = getattr(App.get_running_app(), 'grps', {})
        for d in s.all_data:
            d['sel'] = True
            s.sel.add(d['gn'])
        s.rv_data = s.all_data.copy()
        s.rv.data = s.rv_data
        s.rv.refresh_from_data()
        tot = sum(len(grps[g]['chs']) for g in s.sel if g in grps)
        s.sel_lbl.text = f'Secilen: {len(s.sel)} grup ({tot} kanal)'
    
    def add_fav(s):
        app = App.get_running_app()
        url, chs, exp = getattr(app, 'surl', ''), getattr(app, 'chs', []), getattr(app, 'exp', '')
        if url:
            db.add_fav(url, short_dom(url), exp, len(chs))
            s.popup_ok('Favorilere eklendi!')
    
    def export(s, *a):
        if not s.sel:
            return s.popup_err('Grup secin!')
        app = App.get_running_app()
        grps, fmt, exp, url = getattr(app, 'grps', {}), getattr(app, 'fmt', 'm3u8'), getattr(app, 'exp', ''), getattr(app, 'surl', '')
        chs = [c for gn in s.sel if gn in grps for c in grps[gn]['chs']]
        content = gen_m3u(chs)
        path = iptv_folder()
        
        if exp and 'EXPIRED' not in exp:
            exp_str = exp.replace('.', '')
        else:
            exp_str = datetime.now().strftime('%d%m%Y')
        
        fname = f'bitis{exp_str}_{short_dom(url)}{FMTS.get(fmt, ".m3u8")}'
        
        try:
            with open(os.path.join(path, fname), 'w', encoding='utf-8') as f:
                f.write(content)
            db.stat(ch=len(chs), fi=1)
            s.popup_ok(f'{len(chs)} kanal kaydedildi!\n\nIPTV/{fname}')
        except Exception as e:
            s.popup_err(str(e)[:30])
        gc_()
    
    def popup_ok(s, msg):
        app = App.get_running_app()
        c = BoxLayout(orientation='vertical', padding=dp(24), spacing=dp(14))
        c.add_widget(Label(text=MDI.CHECK, font_name=ICON_FONT, font_size=sp(48), color=app.tc('ok')))
        c.add_widget(Label(text=msg, font_size=sp(13), color=app.tc('t1'), halign='center'))
        btn = Button(text='Tamam', size_hint=(0.5, None), height=dp(46), pos_hint={'center_x': 0.5}, background_normal='', background_color=app.tc('acc'))
        p = Popup(title='', content=c, size_hint=(0.85, 0.45), separator_height=0)
        btn.bind(on_press=p.dismiss)
        c.add_widget(btn)
        p.open()
    
    def popup_err(s, msg):
        app = App.get_running_app()
        c = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(12))
        c.add_widget(Label(text=MDI.ALERT, font_name=ICON_FONT, font_size=sp(40), color=app.tc('err')))
        c.add_widget(Label(text=msg, font_size=sp(13), color=app.tc('t1')))
        btn = Button(text='Tamam', size_hint=(0.5, None), height=dp(42), pos_hint={'center_x': 0.5}, background_normal='', background_color=app.tc('warn'))
        p = Popup(title='', content=c, size_hint=(0.78, 0.38), separator_height=0)
        btn.bind(on_press=p.dismiss)
        c.add_widget(btn)
        p.open()
    
    def back(s):
        gc_()
        s.manager.transition = SlideTransition(direction='right')
        s.manager.current = 'mi'


class TestingScreen(BaseScreen):
    def on_enter(s):
        s.clear_widgets()
        s.testing, s.wk, s.fl = True, [], []
        Clock.schedule_once(lambda dt: s.build(), 0.05)
        Clock.schedule_once(lambda dt: s.run(), 0.2)
    
    def build(s):
        app = App.get_running_app()
        root = BoxLayout(orientation='vertical', padding=dp(18), spacing=dp(14))
        
        # Header
        hdr = BoxLayout(size_hint_y=None, height=dp(60), spacing=dp(14))
        hdr.add_widget(Label(text=MDI.REFRESH, font_name=ICON_FONT, font_size=sp(36), color=app.tc('acc'), size_hint_x=None, width=dp(50)))
        hdr.add_widget(Label(text='Test Ediliyor', font_size=sp(22), bold=True, color=app.tc('t1')))
        root.add_widget(hdr)
        
        # Progress card
        prog_card = BoxLayout(orientation='vertical', padding=dp(18), spacing=dp(10), size_hint_y=None, height=dp(150))
        with prog_card.canvas.before:
            Color(*app.tc('card'))
            prog_card._bg = RoundedRectangle(pos=prog_card.pos, size=prog_card.size, radius=[dp(16)])
        prog_card.bind(pos=s._upd, size=s._upd)
        
        s.prog_lbl = Label(text='Hazirlaniyor...', font_size=sp(13), color=app.tc('t2'), size_hint_y=None, height=dp(22))
        prog_card.add_widget(s.prog_lbl)
        
        s.prog = AnimProg(size_hint_y=None, height=dp(26))
        prog_card.add_widget(s.prog)
        
        s.pct = Label(text='%0', font_size=sp(32), bold=True, color=app.tc('acc'), size_hint_y=None, height=dp(40))
        prog_card.add_widget(s.pct)
        
        s.stat_lbl = Label(text=f'{MDI.CHECK} 0  |  {MDI.CLOSE} 0', font_name=ICON_FONT, font_size=sp(12), color=app.tc('t3'), size_hint_y=None, height=dp(20))
        prog_card.add_widget(s.stat_lbl)
        root.add_widget(prog_card)
        
        # Log
        log_card = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(6))
        with log_card.canvas.before:
            Color(*app.tc('card'))
            log_card._bg = RoundedRectangle(pos=log_card.pos, size=log_card.size, radius=[dp(16)])
        log_card.bind(pos=s._upd, size=s._upd)
        
        log_card.add_widget(Label(text='Log', font_size=sp(11), color=app.tc('t3'), halign='left', size_hint_y=None, height=dp(18)))
        
        scrl = ScrollView()
        s.log_box = BoxLayout(orientation='vertical', spacing=dp(4), size_hint_y=None)
        s.log_box.bind(minimum_height=s.log_box.setter('height'))
        scrl.add_widget(s.log_box)
        log_card.add_widget(scrl)
        root.add_widget(log_card)
        
        # Action button
        s.act_btn = Button(text=f'{MDI.CLOSE} Iptal', font_name=ICON_FONT, font_size=sp(14), bold=True, size_hint_y=None, height=dp(56), background_normal='', background_color=app.tc('err'))
        s.act_btn.bind(on_press=s.on_act)
        root.add_widget(s.act_btn)
        
        s.add_widget(root)
    
    def _upd(s, w, v):
        if hasattr(w, '_bg'): w._bg.pos, w._bg.size = w.pos, w.size
    
    def run(s):
        threading.Thread(target=s._test, daemon=True).start()
    
    def _test(s):
        app = App.get_running_app()
        lks, m = getattr(app, 'tlks', []), getattr(app, 'tm', 'deep')
        tot = len(lks)
        for i, lk in enumerate(lks):
            if not s.testing: break
            dm = short_dom(lk)
            Clock.schedule_once(lambda dt, d=dm: s.log(f'{MDI.LINK} {d}', 't'))
            ok, msg = test_link(lk, m)
            if ok:
                s.wk.append(lk)
                Clock.schedule_once(lambda dt, d=dm, m=msg: s.log(f'{MDI.CHECK} {d}: {m}', 'ok'))
            else:
                s.fl.append({'lk': lk, 'r': msg})
                Clock.schedule_once(lambda dt, d=dm, m=msg: s.log(f'{MDI.CLOSE} {d}: {m}', 'er'))
            p = ((i + 1) / tot) * 100
            Clock.schedule_once(lambda dt, pp=p, c=i+1, t=tot: s.up(pp, c, t))
        db.stat(te=len(lks), wo=len(s.wk))
        Clock.schedule_once(lambda dt: s.done())
    
    def log(s, txt, tp):
        app = App.get_running_app()
        clrs = {'t': app.tc('t3'), 'ok': app.tc('ok'), 'er': app.tc('err')}
        lbl = Label(text=txt, font_name=ICON_FONT, font_size=sp(11), color=clrs.get(tp, app.tc('t3')), size_hint_y=None, height=dp(18), halign='left')
        lbl.bind(size=lambda w, sz: setattr(w, 'text_size', sz))
        s.log_box.add_widget(lbl)
        if len(s.log_box.children) > 30:
            s.log_box.remove_widget(s.log_box.children[-1])
    
    def up(s, p, c, t):
        s.prog.sv(p)
        s.prog_lbl.text = f'Test: {c}/{t}'
        s.pct.text = f'%{int(p)}'
        s.stat_lbl.text = f'{MDI.CHECK} {len(s.wk)}  |  {MDI.CLOSE} {len(s.fl)}'
    
    def done(s):
        app = App.get_running_app()
        s.testing = False
        s.prog_lbl.text = 'Tamamlandi!'
        s.pct.text = '%100'
        s.act_btn.text = f'{MDI.NEXT} Devam'
        s.act_btn.background_color = app.tc('ok')
        app.wlks, app.flks = s.wk, s.fl
    
    def on_act(s, *a):
        if 'Iptal' in s.act_btn.text:
            s.testing = False
            s.manager.transition = SlideTransition(direction='right')
            s.manager.current = 'ai'
        elif not s.wk:
            s.popup('Calisan link yok!')
        else:
            gc_()
            s.manager.current = 'ar'
    
    def popup(s, msg):
        app = App.get_running_app()
        c = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(12))
        c.add_widget(Label(text=MDI.ALERT, font_name=ICON_FONT, font_size=sp(40), color=app.tc('warn')))
        c.add_widget(Label(text=msg, font_size=sp(13), color=app.tc('t1')))
        btn = Button(text='Geri', size_hint=(0.5, None), height=dp(42), pos_hint={'center_x': 0.5}, background_normal='', background_color=app.tc('acc'))
        p = Popup(title='', content=c, size_hint=(0.75, 0.35), separator_height=0)
        def go(x):
            p.dismiss()
            s.manager.transition = SlideTransition(direction='right')
            s.manager.current = 'ai'
        btn.bind(on_press=go)
        c.add_widget(btn)
        p.open()


class AutoResultScreen(BaseScreen):
    def on_enter(s):
        s.clear_widgets()
        Clock.schedule_once(lambda dt: s.build(), 0.05)
    
    def build(s):
        app = App.get_running_app()
        w, f = len(getattr(app, 'wlks', [])), len(getattr(app, 'flks', []))
        
        root = BoxLayout(orientation='vertical', padding=dp(22), spacing=dp(18))
        
        # Header
        hdr = BoxLayout(size_hint_y=None, height=dp(70), spacing=dp(14))
        hdr.add_widget(Label(text=MDI.CHECK, font_name=ICON_FONT, font_size=sp(48), color=app.tc('ok'), size_hint_x=None, width=dp(60)))
        hdr.add_widget(Label(text='Test Tamamlandi!', font_size=sp(20), bold=True, color=app.tc('t1')))
        root.add_widget(hdr)
        
        # Results
        res_card = BoxLayout(orientation='horizontal', padding=dp(20), spacing=dp(20), size_hint_y=None, height=dp(100))
        with res_card.canvas.before:
            Color(*app.tc('card'))
            res_card._bg = RoundedRectangle(pos=res_card.pos, size=res_card.size, radius=[dp(16)])
        res_card.bind(pos=s._upd, size=s._upd)
        
        for val, lbl, clr, icon in [(w, 'Calisiyor', 'ok', MDI.CHECK), (f, 'Basarisiz', 'err', MDI.CLOSE)]:
            box = BoxLayout(orientation='vertical')
            box.add_widget(Label(text=icon, font_name=ICON_FONT, font_size=sp(24), color=app.tc(clr)))
            box.add_widget(Label(text=str(val), font_size=sp(28), bold=True, color=app.tc(clr)))
            box.add_widget(Label(text=lbl, font_size=sp(11), color=app.tc('t3')))
            res_card.add_widget(box)
        root.add_widget(res_card)
        
        root.add_widget(Label(text=f'{w} link = {w} ayri dosya olusturulacak', font_size=sp(12), color=app.tc('info'), size_hint_y=None, height=dp(24)))
        
        # Options
        for title, desc, clr, scr, icon in [
            ('Otomatik', f'Ulke sec, {w} ayri dosya', 'acc', 'cs', MDI.MAGIC),
            ('Manuel', 'Her linki tek tek duzenle', 'ok', 'mll', MDI.EDIT)
        ]:
            card = BoxLayout(orientation='horizontal', padding=dp(16), spacing=dp(14), size_hint_y=None, height=dp(80))
            with card.canvas.before:
                Color(*app.tc('card'))
                card._bg = RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(14)])
            card.bind(pos=s._upd, size=s._upd)
            
            card.add_widget(Label(text=icon, font_name=ICON_FONT, font_size=sp(28), color=app.tc(clr), size_hint_x=None, width=dp(50)))
            
            info = BoxLayout(orientation='vertical', spacing=dp(2))
            info.add_widget(Label(text=title, font_size=sp(14), bold=True, color=app.tc('t1'), halign='left'))
            info.add_widget(Label(text=desc, font_size=sp(10), color=app.tc('t3'), halign='left'))
            card.add_widget(info)
            
            btn = Button(text=MDI.NEXT, font_name=ICON_FONT, font_size=sp(18), size_hint=(None, None), size=(dp(46), dp(46)), background_normal='', background_color=app.tc(clr))
            btn.bind(on_press=lambda x, sc=scr: setattr(s.manager, 'current', sc))
            card.add_widget(btn)
            root.add_widget(card)
        
        # Back
        back = Button(text=f'{MDI.BACK} Geri', font_name=ICON_FONT, size_hint_y=None, height=dp(48), background_normal='', background_color=app.tc('card'))
        back.bind(on_press=lambda x: s.back())
        root.add_widget(back)
        
        s.add_widget(root)
    
    def _upd(s, w, v):
        if hasattr(w, '_bg'): w._bg.pos, w._bg.size = w.pos, w.size
    
    def back(s):
        s.manager.transition = SlideTransition(direction='right')
        s.manager.current = 'ai'


class CountrySelectScreen(BaseScreen):
    def on_enter(s):
        s.clear_widgets()
        s.sel, s.fmt = set(), db.get('fmt', 'm3u8')
        Clock.schedule_once(lambda dt: s.build(), 0.05)
    
    def build(s):
        app = App.get_running_app()
        num = len(getattr(app, 'wlks', []))
        
        root = BoxLayout(orientation='vertical', padding=dp(14), spacing=dp(10))
        
        # Top bar
        top = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(10))
        back_btn = icon_btn(MDI.BACK, app.tc('t1'), lambda x: s.back())
        top.add_widget(back_btn)
        top.add_widget(Label(text=f'{MDI.EARTH} Ulke Secimi', font_name=ICON_FONT, font_size=sp(17), bold=True, color=app.tc('t1')))
        root.add_widget(top)
        
        root.add_widget(Label(text=f'{num} link = {num} ayri dosya', font_size=sp(11), color=app.tc('info'), size_hint_y=None, height=dp(18)))
        
        s.sel_lbl = Label(text='Secilen: 0 ulke', font_size=sp(11), color=app.tc('ok'), size_hint_y=None, height=dp(18))
        root.add_widget(s.sel_lbl)
        
        # Country grid
        scrl = ScrollView()
        grid = GridLayout(cols=2, spacing=dp(10), size_hint_y=None, padding=dp(4))
        grid.bind(minimum_height=grid.setter('height'))
        
        s.btns = {}
        for cid in PRIO_C:
            cd = COUNTRIES[cid]
            btn = ToggleButton(text=f"{cd['f']} {cd['n']}", size_hint_y=None, height=dp(52), font_size=sp(13), background_normal='', background_color=app.tc('warn'))
            btn.cid, btn.pri = cid, True
            btn.bind(on_press=s.on_tog)
            s.btns[cid] = btn
            grid.add_widget(btn)
        
        for cid, cd in sorted(COUNTRIES.items(), key=lambda x: x[1]['p']):
            if cid not in PRIO_C:
                btn = ToggleButton(text=f"{cd['f']} {cd['n']}", size_hint_y=None, height=dp(52), font_size=sp(13), background_normal='', background_color=app.tc('card'))
                btn.cid, btn.pri = cid, False
                btn.bind(on_press=s.on_tog)
                s.btns[cid] = btn
                grid.add_widget(btn)
        
        scrl.add_widget(grid)
        root.add_widget(scrl)
        
        # Format
        fmt_row = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))
        fmt_row.add_widget(Label(text='Format:', size_hint_x=None, width=dp(60), font_size=sp(11), color=app.tc('t3')))
        
        s.fmt_btns = {}
        for fid in ['m3u', 'm3u8', 'txt']:
            is_sel = fid == s.fmt
            btn = ToggleButton(text=fid.upper(), group='f2', state='down' if is_sel else 'normal', font_size=sp(12), background_normal='', background_color=app.tc('acc') if is_sel else app.tc('card2'))
            btn.fid = fid
            btn.bind(on_press=s.on_fmt)
            s.fmt_btns[fid] = btn
            fmt_row.add_widget(btn)
        root.add_widget(fmt_row)
        
        # Process button
        proc_btn = Button(text=f'{MDI.ROCKET} Olustur', font_name=ICON_FONT, font_size=sp(14), bold=True, size_hint_y=None, height=dp(54), background_normal='', background_color=app.tc('ok'))
        proc_btn.bind(on_press=s.proc)
        root.add_widget(proc_btn)
        
        s.add_widget(root)
    
    def on_tog(s, btn):
        app = App.get_running_app()
        if btn.state == 'down':
            s.sel.add(btn.cid)
            btn.background_color = app.tc('ok')
        else:
            s.sel.discard(btn.cid)
            btn.background_color = app.tc('warn') if btn.pri else app.tc('card')
        s.sel_lbl.text = f'Secilen: {len(s.sel)} ulke'
    
    def on_fmt(s, btn):
        app = App.get_running_app()
        s.fmt = btn.fid
        for f, b in s.fmt_btns.items():
            b.background_color = app.tc('acc') if f == s.fmt else app.tc('card2')
    
    def proc(s, *a):
        if not s.sel:
            return s.popup('Ulke secin!')
        app = App.get_running_app()
        app.sctrs, app.ofmt = s.sel, s.fmt
        s.manager.current = 'pr'
    
    def popup(s, msg):
        app = App.get_running_app()
        c = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(12))
        c.add_widget(Label(text=MDI.ALERT, font_name=ICON_FONT, font_size=sp(40), color=app.tc('warn')))
        c.add_widget(Label(text=msg, font_size=sp(13), color=app.tc('t1')))
        btn = Button(text='Tamam', size_hint=(0.5, None), height=dp(42), pos_hint={'center_x': 0.5}, background_normal='', background_color=app.tc('warn'))
        p = Popup(title='', content=c, size_hint=(0.72, 0.32), separator_height=0)
        btn.bind(on_press=p.dismiss)
        c.add_widget(btn)
        p.open()
    
    def back(s):
        s.manager.transition = SlideTransition(direction='right')
        s.manager.current = 'ar'


class ProcessingScreen(BaseScreen):
    def on_enter(s):
        s.clear_widgets()
        s.fls = []
        Clock.schedule_once(lambda dt: s.build(), 0.05)
        Clock.schedule_once(lambda dt: s.run(), 0.2)
    
    def build(s):
        app = App.get_running_app()
        root = BoxLayout(orientation='vertical', padding=dp(22), spacing=dp(16))
        
        # Header
        hdr = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(12))
        hdr.add_widget(Label(text=MDI.COG, font_name=ICON_FONT, font_size=sp(36), color=app.tc('acc'), size_hint_x=None, width=dp(50)))
        hdr.add_widget(Label(text='Isleniyor...', font_size=sp(20), bold=True, color=app.tc('t1')))
        root.add_widget(hdr)
        
        s.status = Label(text='Baslatiliyor...', font_size=sp(12), color=app.tc('t3'), size_hint_y=None, height=dp(22))
        root.add_widget(s.status)
        
        s.prog = AnimProg(size_hint_y=None, height=dp(26))
        root.add_widget(s.prog)
        
        s.pct = Label(text='%0', font_size=sp(36), bold=True, color=app.tc('acc'), size_hint_y=None, height=dp(48))
        root.add_widget(s.pct)
        
        # Stats
        stats_card = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(8), size_hint_y=None, height=dp(120))
        with stats_card.canvas.before:
            Color(*app.tc('card'))
            stats_card._bg = RoundedRectangle(pos=stats_card.pos, size=stats_card.size, radius=[dp(16)])
        stats_card.bind(pos=s._upd, size=s._upd)
        
        s.cur_lbl = Label(text=f'{MDI.LINK} -', font_name=ICON_FONT, font_size=sp(11), color=app.tc('t3'))
        stats_card.add_widget(s.cur_lbl)
        s.tot_lbl = Label(text=f'{MDI.TV} Toplam: 0 kanal', font_name=ICON_FONT, font_size=sp(12), color=app.tc('t2'))
        stats_card.add_widget(s.tot_lbl)
        s.flt_lbl = Label(text=f'{MDI.CHECK} Filtrelenen: 0 kanal', font_name=ICON_FONT, font_size=sp(12), color=app.tc('ok'))
        stats_card.add_widget(s.flt_lbl)
        s.fil_lbl = Label(text=f'{MDI.FILE} Dosyalar: 0', font_name=ICON_FONT, font_size=sp(11), color=app.tc('info'))
        stats_card.add_widget(s.fil_lbl)
        
        root.add_widget(stats_card)
        root.add_widget(Widget())
        s.add_widget(root)
    
    def _upd(s, w, v):
        if hasattr(w, '_bg'): w._bg.pos, w._bg.size = w.pos, w.size
    
    def run(s):
        threading.Thread(target=s._proc, daemon=True).start()
    
    def _proc(s):
        app = App.get_running_app()
        lks, ctrs, fmt = getattr(app, 'wlks', []), getattr(app, 'sctrs', set()), getattr(app, 'ofmt', 'm3u8')
        tl, tch, tflt = len(lks), 0, 0
        path, ext = iptv_folder(), FMTS.get(fmt, '.m3u8')
        
        for i, lk in enumerate(lks):
            dm = short_dom(lk)
            Clock.schedule_once(lambda dt, d=dm: setattr(s.cur_lbl, 'text', f'{MDI.LINK} {d}'))
            Clock.schedule_once(lambda dt, p=((i + 0.3) / tl) * 100: s._up(p))
            
            try:
                r = http.get(lk, timeout=30)
                chs, grps, exp = parse_m3u(r.text, lk)
                tch += len(chs)
                
                fchs = [c for gn, gd in grps.items() if gd.get('cty', 'other') in ctrs for c in gd['chs']]
                tflt += len(fchs)
                Clock.schedule_once(lambda dt, t=tch, f=tflt: s._us(t, f))
                
                if fchs:
                    content = gen_m3u(fchs)
                    if exp and 'EXPIRED' not in exp:
                        exp_str = exp.replace('.', '')
                    else:
                        exp_str = datetime.now().strftime('%d%m%Y')
                    
                    fname = f'bitis{exp_str}_{dm}{ext}'
                    with open(os.path.join(path, fname), 'w', encoding='utf-8') as f:
                        f.write(content)
                    s.fls.append({'n': fname, 'c': len(fchs), 'e': exp})
                    Clock.schedule_once(lambda dt, c=len(s.fls): setattr(s.fil_lbl, 'text', f'{MDI.FILE} Dosyalar: {c}'))
            except: pass
            
            Clock.schedule_once(lambda dt, p=((i + 1) / tl) * 100: s._up(p))
            if i % 3 == 0: gc_()
        
        db.stat(ch=tflt, fi=len(s.fls))
        app.sfls, app.tflt, app.tch = s.fls, tflt, tch
        Clock.schedule_once(lambda dt: s._up(100))
        Clock.schedule_once(lambda dt: s._done())
    
    def _up(s, p):
        s.prog.sv(p)
        s.pct.text = f'%{int(p)}'
    
    def _us(s, t, f):
        s.tot_lbl.text = f'{MDI.TV} Toplam: {t} kanal'
        s.flt_lbl.text = f'{MDI.CHECK} Filtrelenen: {f} kanal'
    
    def _done(s):
        gc_()
        s.manager.current = 'cp'


class ManualLinkListScreen(BaseScreen):
    def on_enter(s):
        s.clear_widgets()
        Clock.schedule_once(lambda dt: s.build(), 0.05)
    
    def build(s):
        app = App.get_running_app()
        lks = getattr(app, 'wlks', [])
        
        root = BoxLayout(orientation='vertical', padding=dp(14), spacing=dp(10))
        
        # Top bar
        top = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(10))
        back_btn = icon_btn(MDI.BACK, app.tc('t1'), lambda x: s.back())
        top.add_widget(back_btn)
        top.add_widget(Label(text=f'{MDI.EDIT} Manuel ({len(lks)})', font_name=ICON_FONT, font_size=sp(16), bold=True, color=app.tc('t1')))
        root.add_widget(top)
        
        # Links
        scrl = ScrollView()
        lst = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None)
        lst.bind(minimum_height=lst.setter('height'))
        
        for i, lk in enumerate(lks):
            item = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(68), padding=dp(14), spacing=dp(12))
            with item.canvas.before:
                Color(*app.tc('card'))
                item._bg = RoundedRectangle(pos=item.pos, size=item.size, radius=[dp(14)])
            item.bind(pos=s._upd, size=s._upd)
            
            item.add_widget(Label(text=str(i+1), font_size=sp(18), bold=True, color=app.tc('acc'), size_hint_x=None, width=dp(32)))
            
            info = BoxLayout(orientation='vertical', spacing=dp(2))
            info.add_widget(Label(text=short_dom(lk), font_size=sp(13), color=app.tc('t1'), halign='left'))
            info.add_widget(Label(text=lk[:34]+'...', font_size=sp(9), color=app.tc('t4'), halign='left'))
            item.add_widget(info)
            
            edit_btn = Button(text=MDI.EDIT, font_name=ICON_FONT, font_size=sp(18), size_hint=(None, None), size=(dp(46), dp(46)), background_normal='', background_color=app.tc('acc'))
            edit_btn.lk, edit_btn.idx = lk, i+1
            edit_btn.bind(on_press=s.edit)
            item.add_widget(edit_btn)
            
            lst.add_widget(item)
        
        scrl.add_widget(lst)
        root.add_widget(scrl)
        s.add_widget(root)
    
    def _upd(s, w, v):
        if hasattr(w, '_bg'): w._bg.pos, w._bg.size = w.pos, w.size
    
    def edit(s, btn):
        app = App.get_running_app()
        app.elk, app.eidx = btn.lk, btn.idx
        s.manager.current = 'le'
    
    def back(s):
        s.manager.transition = SlideTransition(direction='right')
        s.manager.current = 'ar'


class LinkEditorScreen(BaseScreen):
    def on_enter(s):
        s.clear_widgets()
        s.sel, s.grps, s.chs, s.exp = set(), {}, [], ''
        Clock.schedule_once(lambda dt: s.build(), 0.05)
        Clock.schedule_once(lambda dt: s.load(), 0.1)
    
    def build(s):
        app = App.get_running_app()
        idx = getattr(app, 'eidx', 1)
        tot = len(getattr(app, 'wlks', []))
        
        root = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(8))
        
        # Top bar
        top = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(10))
        back_btn = icon_btn(MDI.BACK, app.tc('t1'), lambda x: s.back(), size=44)
        top.add_widget(back_btn)
        top.add_widget(Label(text=f'Link {idx}/{tot}', font_size=sp(14), bold=True, color=app.tc('t1')))
        root.add_widget(top)
        
        # Loading
        s.load_box = BoxLayout(orientation='vertical', spacing=dp(10))
        s.load_box.add_widget(Label(text=MDI.REFRESH, font_name=ICON_FONT, font_size=sp(40), color=app.tc('acc')))
        s.l_msg = Label(text='Yukleniyor...', font_size=sp(12), color=app.tc('t3'))
        s.load_box.add_widget(s.l_msg)
        s.l_prog = AnimProg(size_hint_y=None, height=dp(20))
        s.load_box.add_widget(s.l_prog)
        s.l_pct = Label(text='%0', font_size=sp(20), bold=True, color=app.tc('acc'))
        s.load_box.add_widget(s.l_pct)
        root.add_widget(s.load_box)
        
        # Content
        s.content = BoxLayout(orientation='vertical', spacing=dp(6), opacity=0)
        s.exp_lbl = Label(text='', font_size=sp(10), color=app.tc('warn'), size_hint_y=None, height=dp(16))
        s.content.add_widget(s.exp_lbl)
        s.stats_lbl = Label(text='', font_size=sp(11), color=app.tc('t3'), size_hint_y=None, height=dp(18))
        s.content.add_widget(s.stats_lbl)
        s.sel_lbl = Label(text='Secilen: 0', font_size=sp(10), color=app.tc('ok'), size_hint_y=None, height=dp(16))
        s.content.add_widget(s.sel_lbl)
        s.rv = RV()
        s.rv_data = []
        s.content.add_widget(s.rv)
        root.add_widget(s.content)
        
        # Bottom
        s.btm = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10), opacity=0)
        save_btn = Button(text=f'{MDI.SAVE} Kaydet', font_name=ICON_FONT, font_size=sp(13), bold=True, background_normal='', background_color=app.tc('ok'))
        save_btn.bind(on_press=s.save)
        s.btm.add_widget(save_btn)
        root.add_widget(s.btm)
        
        s.add_widget(root)
    
    def load(s):
        threading.Thread(target=s._load, daemon=True).start()
    
    def _load(s):
        app = App.get_running_app()
        lk = getattr(app, 'elk', '')
        try:
            Clock.schedule_once(lambda dt: s._ul(10, 'Baglaniyor...'))
            r = http.get(lk, timeout=30)
            Clock.schedule_once(lambda dt: s._ul(50, 'Ayristiriliyor...'))
            s.chs, s.grps, s.exp = parse_m3u(r.text, lk)
            Clock.schedule_once(lambda dt: s._ul(100, 'Tamam!'))
            Clock.schedule_once(lambda dt: s._show(), 0.2)
        except Exception as e:
            Clock.schedule_once(lambda dt: s._err(str(e)[:20]))
    
    def _ul(s, p, m):
        s.l_prog.sv(p)
        s.l_pct.text = f'%{int(p)}'
        s.l_msg.text = m
    
    def _show(s):
        app = App.get_running_app()
        s.load_box.opacity, s.load_box.size_hint_y = 0, 0.001
        s.content.opacity, s.btm.opacity = 1, 1
        
        exp_clr = app.tc('err') if 'EXPIRED' in s.exp else app.tc('warn')
        s.exp_lbl.text = f'{MDI.CALENDAR} Bitis: {s.exp or "Bilinmiyor"}'
        s.exp_lbl.color = exp_clr
        
        s.stats_lbl.text = f'{len(s.grps)} grup | {len(s.chs)} kanal'
        
        s.rv_data = [{'gn': gn, 'cnt': len(gd['chs']), 'cty': gd.get('cty', 'other'), 'sel': False, 'cb': s.on_sel} for gn, gd in sorted(s.grps.items())]
        s.rv.data = s.rv_data
    
    def _err(s, m):
        s.l_msg.text = f'{MDI.CLOSE} Hata: {m}'
    
    def on_sel(s, gn, sel, idx):
        s.rv_data[idx]['sel'] = sel
        if sel: s.sel.add(gn)
        else: s.sel.discard(gn)
        tot = sum(len(s.grps[g]['chs']) for g in s.sel if g in s.grps)
        s.sel_lbl.text = f'Secilen: {len(s.sel)} grup ({tot} kanal)'
    
    def save(s, *a):
        app = App.get_running_app()
        if not s.sel:
            return s.popup('Grup secin!')
        
        chs = [c for gn in s.sel if gn in s.grps for c in s.grps[gn]['chs']]
        content = gen_m3u(chs)
        lk = getattr(app, 'elk', '')
        path, dm = iptv_folder(), short_dom(lk)
        
        if s.exp and 'EXPIRED' not in s.exp:
            exp_str = s.exp.replace('.', '')
        else:
            exp_str = datetime.now().strftime('%d%m%Y')
        
        fname = f'bitis{exp_str}_{dm}.m3u8'
        
        try:
            with open(os.path.join(path, fname), 'w', encoding='utf-8') as f:
                f.write(content)
            db.stat(ch=len(chs), fi=1)
            s.popup_ok(fname, len(chs))
        except Exception as e:
            s.popup(str(e)[:25])
        gc_()
    
    def popup(s, msg):
        app = App.get_running_app()
        c = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(12))
        c.add_widget(Label(text=MDI.ALERT, font_name=ICON_FONT, font_size=sp(36), color=app.tc('warn')))
        c.add_widget(Label(text=msg, font_size=sp(12), color=app.tc('t1')))
        btn = Button(text='Tamam', size_hint=(0.5, None), height=dp(40), pos_hint={'center_x': 0.5}, background_normal='', background_color=app.tc('warn'))
        p = Popup(title='', content=c, size_hint=(0.72, 0.32), separator_height=0)
        btn.bind(on_press=p.dismiss)
        c.add_widget(btn)
        p.open()
    
    def popup_ok(s, fname, cnt):
        app = App.get_running_app()
        c = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(12))
        c.add_widget(Label(text=MDI.CHECK, font_name=ICON_FONT, font_size=sp(48), color=app.tc('ok')))
        c.add_widget(Label(text='Kaydedildi!', font_size=sp(14), bold=True, color=app.tc('t1')))
        c.add_widget(Label(text=f'{cnt} kanal\nIPTV/{fname}', font_size=sp(11), color=app.tc('t3'), halign='center'))
        btn = Button(text='Listeye Don', size_hint=(0.55, None), height=dp(42), pos_hint={'center_x': 0.5}, background_normal='', background_color=app.tc('acc'))
        p = Popup(title='', content=c, size_hint=(0.82, 0.42), separator_height=0)
        def go(x):
            p.dismiss()
            s.manager.transition = SlideTransition(direction='right')
            s.manager.current = 'mll'
        btn.bind(on_press=go)
        c.add_widget(btn)
        p.open()
    
    def back(s):
        gc_()
        s.manager.transition = SlideTransition(direction='right')
        s.manager.current = 'mll'


class CompleteScreen(BaseScreen):
    def on_enter(s):
        s.clear_widgets()
        Clock.schedule_once(lambda dt: s.build(), 0.05)
    
    def build(s):
        app = App.get_running_app()
        fls = getattr(app, 'sfls', [])
        flt = getattr(app, 'tflt', 0)
        tot = getattr(app, 'tch', 0)
        
        root = BoxLayout(orientation='vertical', padding=dp(24), spacing=dp(18))
        
        # Success icon
        root.add_widget(Label(text=MDI.CHECK, font_name=ICON_FONT, font_size=sp(72), color=app.tc('ok'), size_hint_y=None, height=dp(90)))
        root.add_widget(Label(text='Tamamlandi!', font_size=sp(26), bold=True, color=app.tc('t1'), size_hint_y=None, height=dp(36)))
        
        # Results
        res_card = BoxLayout(orientation='vertical', padding=dp(18), spacing=dp(8), size_hint_y=None, height=dp(120))
        with res_card.canvas.before:
            Color(*app.tc('card'))
            res_card._bg = RoundedRectangle(pos=res_card.pos, size=res_card.size, radius=[dp(16)])
        res_card.bind(pos=s._upd, size=s._upd)
        
        res_card.add_widget(Label(text=f'{flt} kanal filtrelendi', font_size=sp(14), color=app.tc('ok')))
        res_card.add_widget(Label(text=f'Toplam {tot} kanaldan', font_size=sp(11), color=app.tc('t3')))
        res_card.add_widget(Label(text=f'{len(fls)} dosya olusturuldu', font_size=sp(12), color=app.tc('info')))
        res_card.add_widget(Label(text=f'{MDI.FOLDER} Download/IPTV/', font_name=ICON_FONT, font_size=sp(10), color=app.tc('t4')))
        root.add_widget(res_card)
        
        # Files
        if fls:
            root.add_widget(Label(text='Dosyalar:', font_size=sp(11), color=app.tc('t3'), size_hint_y=None, height=dp(20)))
            
            scrl = ScrollView(size_hint_y=None, height=dp(80))
            fb = BoxLayout(orientation='vertical', spacing=dp(4), size_hint_y=None)
            fb.bind(minimum_height=fb.setter('height'))
            
            for f in fls[:5]:
                exp_info = f" ({f['e']})" if f.get('e') and 'EXPIRED' not in f['e'] else ''
                fb.add_widget(Label(text=f"{MDI.FILE} {f['n']} - {f['c']} ch{exp_info}", font_name=ICON_FONT, font_size=sp(9), color=app.tc('t2'), size_hint_y=None, height=dp(16), halign='left'))
            
            if len(fls) > 5:
                fb.add_widget(Label(text=f'... ve {len(fls) - 5} dosya daha', font_size=sp(9), color=app.tc('t4'), size_hint_y=None, height=dp(14)))
            
            scrl.add_widget(fb)
            root.add_widget(scrl)
        
        # Buttons
        btns = BoxLayout(orientation='vertical', spacing=dp(12), size_hint_y=None, height=dp(110))
        
        new_btn = Button(text=f'{MDI.REFRESH} Yeni Islem', font_name=ICON_FONT, font_size=sp(14), bold=True, size_hint_y=None, height=dp(48), background_normal='', background_color=app.tc('acc'))
        new_btn.bind(on_press=lambda x: s.go('ai'))
        btns.add_widget(new_btn)
        
        home_btn = Button(text=f'{MDI.HOME} Ana Sayfa', font_name=ICON_FONT, font_size=sp(14), bold=True, size_hint_y=None, height=dp(48), background_normal='', background_color=app.tc('card'))
        home_btn.bind(on_press=lambda x: s.go('ws'))
        btns.add_widget(home_btn)
        root.add_widget(btns)
        
        s.add_widget(root)
    
    def _upd(s, w, v):
        if hasattr(w, '_bg'): w._bg.pos, w._bg.size = w.pos, w.size
    
    def go(s, scr):
        gc_()
        s.manager.transition = SlideTransition(direction='right')
        s.manager.current = scr


class FavoritesScreen(BaseScreen):
    def on_enter(s):
        s.clear_widgets()
        Clock.schedule_once(lambda dt: s.build(), 0.05)
    
    def build(s):
        app = App.get_running_app()
        favs = db.favs()
        
        root = BoxLayout(orientation='vertical', padding=dp(14), spacing=dp(12))
        
        # Top bar
        top = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(12))
        back_btn = icon_btn(MDI.BACK, app.tc('t1'), lambda x: s.back())
        top.add_widget(back_btn)
        top.add_widget(Label(text=f'{MDI.STAR} Favoriler', font_name=ICON_FONT, font_size=sp(18), bold=True, color=app.tc('t1')))
        root.add_widget(top)
        
        if not favs:
            empty = BoxLayout(orientation='vertical', spacing=dp(16))
            empty.add_widget(Widget())
            empty.add_widget(Label(text=MDI.STAR_O, font_name=ICON_FONT, font_size=sp(64), color=app.tc('t4')))
            empty.add_widget(Label(text='Henuz favori yok', font_size=sp(14), color=app.tc('t3')))
            empty.add_widget(Label(text='Manuel duzenlemede yildiz ile ekleyin', font_size=sp(11), color=app.tc('t4')))
            empty.add_widget(Widget())
            root.add_widget(empty)
        else:
            root.add_widget(Label(text=f'{len(favs)} kayitli link', font_size=sp(11), color=app.tc('t3'), size_hint_y=None, height=dp(20)))
            
            scrl = ScrollView()
            lst = BoxLayout(orientation='vertical', spacing=dp(12), size_hint_y=None)
            lst.bind(minimum_height=lst.setter('height'))
            
            for fav in favs:
                item = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(72), padding=dp(14), spacing=dp(12))
                with item.canvas.before:
                    Color(*app.tc('card'))
                    item._bg = RoundedRectangle(pos=item.pos, size=item.size, radius=[dp(14)])
                item.bind(pos=s._upd, size=s._upd)
                
                item.add_widget(Label(text=MDI.STAR, font_name=ICON_FONT, font_size=sp(24), color=app.tc('warn'), size_hint_x=None, width=dp(36)))
                
                info = BoxLayout(orientation='vertical', spacing=dp(2))
                info.add_widget(Label(text=fav['name'][:24], font_size=sp(13), color=app.tc('t1'), halign='left'))
                det = f"{fav.get('cnt', 0)} ch"
                if fav.get('exp') and 'EXPIRED' not in fav['exp']:
                    det += f" | {fav['exp']}"
                info.add_widget(Label(text=det, font_size=sp(10), color=app.tc('t3'), halign='left'))
                item.add_widget(info)
                
                btn_box = BoxLayout(orientation='vertical', size_hint_x=None, width=dp(48), spacing=dp(4))
                
                use_btn = Button(text=MDI.PLAY, font_name=ICON_FONT, font_size=sp(14), size_hint=(None, None), size=(dp(42), dp(28)), background_normal='', background_color=app.tc('ok'))
                use_btn.url = fav['url']
                use_btn.bind(on_press=s.use_fav)
                btn_box.add_widget(use_btn)
                
                del_btn = Button(text=MDI.DELETE, font_name=ICON_FONT, font_size=sp(14), size_hint=(None, None), size=(dp(42), dp(28)), background_normal='', background_color=app.tc('err'))
                del_btn.url = fav['url']
                del_btn.bind(on_press=s.del_fav)
                btn_box.add_widget(del_btn)
                
                item.add_widget(btn_box)
                lst.add_widget(item)
            
            scrl.add_widget(lst)
            root.add_widget(scrl)
        
        s.add_widget(root)
    
    def _upd(s, w, v):
        if hasattr(w, '_bg'): w._bg.pos, w._bg.size = w.pos, w.size
    
    def use_fav(s, btn):
        s.manager.current = 'mi'
        Clock.schedule_once(lambda dt: s._fill(btn.url), 0.2)
    
    def _fill(s, url):
        scr = s.manager.get_screen('mi')
        if hasattr(scr, 'url_inp'):
            scr.url_inp.text = url
    
    def del_fav(s, btn):
        db.del_fav(btn.url)
        s.on_enter()
    
    def back(s):
        s.manager.transition = SlideTransition(direction='right')
        s.manager.current = 'ws'


class SettingsScreen(BaseScreen):
    def on_enter(s):
        s.clear_widgets()
        Clock.schedule_once(lambda dt: s.build(), 0.05)
    
    def build(s):
        app = App.get_running_app()
        root = BoxLayout(orientation='vertical', padding=dp(14), spacing=dp(12))
        
        # Top bar
        top = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(12))
        back_btn = icon_btn(MDI.BACK, app.tc('t1'), lambda x: s.back())
        top.add_widget(back_btn)
        top.add_widget(Label(text=f'{MDI.COG} Ayarlar', font_name=ICON_FONT, font_size=sp(18), bold=True, color=app.tc('t1')))
        root.add_widget(top)
        
        scrl = ScrollView()
        sl = BoxLayout(orientation='vertical', spacing=dp(14), size_hint_y=None)
        sl.bind(minimum_height=sl.setter('height'))
        
        # Theme
        theme_card = s._sec(f'{MDI.THEME} Tema')
        theme_grid = GridLayout(cols=2, spacing=dp(10), size_hint_y=None, height=dp(100))
        cur = db.get('theme', 'cyberpunk')
        s.theme_btns = {}
        for tid, td in THEMES.items():
            is_sel = tid == cur
            btn = ToggleButton(text=td['name'], group='theme', state='down' if is_sel else 'normal', font_size=sp(12), size_hint_y=None, height=dp(44), background_normal='', background_color=app.tc('acc') if is_sel else app.tc('card2'))
            btn.tid = tid
            btn.bind(on_press=s.ch_theme)
            s.theme_btns[tid] = btn
            theme_grid.add_widget(btn)
        theme_card.add_widget(theme_grid)
        sl.add_widget(theme_card)
        
        # Test
        test_card = s._sec(f'{MDI.BOLT} Test')
        mode_row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(10))
        mode_row.add_widget(Label(text='Mod:', font_size=sp(11), color=app.tc('t3'), size_hint_x=0.2))
        tm = db.get('mode', 'deep')
        s.mode_btns = {}
        for mid, mn in [('quick', 'Hizli'), ('deep', 'Derin')]:
            is_sel = mid == tm
            btn = ToggleButton(text=mn, group='tm', state='down' if is_sel else 'normal', font_size=sp(12), background_normal='', background_color=app.tc('acc') if is_sel else app.tc('card2'))
            btn.mid = mid
            btn.bind(on_press=s.ch_mode)
            s.mode_btns[mid] = btn
            mode_row.add_widget(btn)
        test_card.add_widget(mode_row)
        
        to_row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(10))
        to_row.add_widget(Label(text='Timeout:', font_size=sp(11), color=app.tc('t3'), size_hint_x=0.2))
        s.to_lbl = Label(text=db.get('to', '12') + 's', font_size=sp(13), bold=True, color=app.tc('acc'), size_hint_x=0.15)
        to_row.add_widget(s.to_lbl)
        to_sl = Slider(min=5, max=30, value=int(db.get('to', '12')), step=1)
        to_sl.bind(value=s.ch_to)
        to_row.add_widget(to_sl)
        test_card.add_widget(to_row)
        sl.add_widget(test_card)
        
        # File
        file_card = s._sec(f'{MDI.FILE} Dosya')
        fmt_row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(10))
        fmt_row.add_widget(Label(text='Format:', font_size=sp(11), color=app.tc('t3'), size_hint_x=0.2))
        df = db.get('fmt', 'm3u8')
        s.fmt_btns = {}
        for fid in ['m3u', 'm3u8', 'txt']:
            is_sel = fid == df
            btn = ToggleButton(text=fid.upper(), group='df', state='down' if is_sel else 'normal', font_size=sp(12), background_normal='', background_color=app.tc('acc') if is_sel else app.tc('card2'))
            btn.fid = fid
            btn.bind(on_press=s.ch_fmt)
            s.fmt_btns[fid] = btn
            fmt_row.add_widget(btn)
        file_card.add_widget(fmt_row)
        
        dup_row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(10))
        dup_row.add_widget(Label(text='Duplicate Temizle:', font_size=sp(11), color=app.tc('t3')))
        dup_sw = Switch(active=db.get('dup', 'true') == 'true')
        dup_sw.bind(active=lambda sw, a: db.set('dup', 'true' if a else 'false'))
        dup_row.add_widget(dup_sw)
        file_card.add_widget(dup_row)
        
        file_card.add_widget(Label(text=f'{MDI.FOLDER} Kayit: Download/IPTV/', font_name=ICON_FONT, font_size=sp(10), color=app.tc('info'), size_hint_y=None, height=dp(20)))
        sl.add_widget(file_card)
        
        # Data
        data_card = s._sec(f'{MDI.DELETE} Veri')
        cache_btn = Button(text='Onbellek Temizle', font_size=sp(12), size_hint_y=None, height=dp(44), background_normal='', background_color=app.tc('info'))
        cache_btn.bind(on_press=s.clr_cache)
        data_card.add_widget(cache_btn)
        sl.add_widget(data_card)
        
        # About
        about_card = s._sec(f'{MDI.INFO} Hakkinda')
        about_card.add_widget(Label(text=f'{APP_NAME} v{APP_VER}', font_size=sp(13), bold=True, color=app.tc('t1'), size_hint_y=None, height=dp(24)))
        about_card.add_widget(Label(text=f'MDI Font: {"Yuklu" if HAS_MDI else "Yok"}', font_size=sp(10), color=app.tc('ok') if HAS_MDI else app.tc('err'), size_hint_y=None, height=dp(18)))
        st = db.stats()
        about_card.add_widget(Label(text=f"Toplam: {st['te']} test, {st['fi']} dosya", font_size=sp(10), color=app.tc('t3'), size_hint_y=None, height=dp(18)))
        sl.add_widget(about_card)
        
        sl.add_widget(Widget(size_hint_y=None, height=dp(20)))
        scrl.add_widget(sl)
        root.add_widget(scrl)
        s.add_widget(root)
    
    def _sec(s, title):
        app = App.get_running_app()
        card = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(10), size_hint_y=None)
        card.bind(minimum_height=card.setter('height'))
        with card.canvas.before:
            Color(*app.tc('card'))
            card._bg = RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(14)])
        card.bind(pos=s._upd, size=s._upd)
        card.add_widget(Label(text=title, font_name=ICON_FONT, font_size=sp(13), bold=True, color=app.tc('t1'), halign='left', size_hint_y=None, height=dp(22)))
        return card
    
    def _upd(s, w, v):
        if hasattr(w, '_bg'): w._bg.pos, w._bg.size = w.pos, w.size
    
    def ch_theme(s, btn):
        global theme
        app = App.get_running_app()
        theme = btn.tid
        db.set('theme', btn.tid)
        for tid, b in s.theme_btns.items():
            b.background_color = app.tc('acc') if tid == btn.tid else app.tc('card2')
        s.popup('Tema degistirildi!\n\nYeniden baslatin')
    
    def ch_mode(s, btn):
        app = App.get_running_app()
        db.set('mode', btn.mid)
        for mid, b in s.mode_btns.items():
            b.background_color = app.tc('acc') if mid == btn.mid else app.tc('card2')
    
    def ch_to(s, sl, val):
        s.to_lbl.text = f'{int(val)}s'
        db.set('to', str(int(val)))
    
    def ch_fmt(s, btn):
        app = App.get_running_app()
        db.set('fmt', btn.fid)
        for fid, b in s.fmt_btns.items():
            b.background_color = app.tc('acc') if fid == btn.fid else app.tc('card2')
    
    def clr_cache(s, *a):
        cache.clear()
        detect_c.cache_clear()
        gc_()
        s.popup('Onbellek temizlendi!')
    
    def popup(s, msg):
        app = App.get_running_app()
        c = BoxLayout(orientation='vertical', padding=dp(24), spacing=dp(14))
        c.add_widget(Label(text=MDI.CHECK, font_name=ICON_FONT, font_size=sp(40), color=app.tc('ok')))
        c.add_widget(Label(text=msg, font_size=sp(12), color=app.tc('t1'), halign='center'))
        btn = Button(text='Tamam', size_hint=(0.5, None), height=dp(42), pos_hint={'center_x': 0.5}, background_normal='', background_color=app.tc('acc'))
        p = Popup(title='', content=c, size_hint=(0.78, 0.4), separator_height=0)
        btn.bind(on_press=p.dismiss)
        c.add_widget(btn)
        p.open()
    
    def back(s):
        s.manager.transition = SlideTransition(direction='right')
        s.manager.current = 'ws'


# ==================== MAIN APP ====================
class IPTVApp(App):
    has_mdi = BooleanProperty(HAS_MDI)
    
    def build(s):
        global theme
        theme = db.get('theme', 'cyberpunk')
        Window.clearcolor = s.tc('bg')
        
        # Allow rotation
        try:
            from android.runnable import run_on_ui_thread
            @run_on_ui_thread
            def set_orientation():
                from jnius import autoclass
                activity = autoclass('org.kivy.android.PythonActivity').mActivity
                activity.setRequestedOrientation(autoclass('android.content.pm.ActivityInfo').SCREEN_ORIENTATION_SENSOR)
            set_orientation()
        except: pass
        
        sm = ScreenManager(transition=SlideTransition())
        sm.add_widget(WelcomeScreen(name='ws'))
        sm.add_widget(ManualInputScreen(name='mi'))
        sm.add_widget(ChannelListScreen(name='cl'))
        sm.add_widget(AutoInputScreen(name='ai'))
        sm.add_widget(TestingScreen(name='ts'))
        sm.add_widget(AutoResultScreen(name='ar'))
        sm.add_widget(CountrySelectScreen(name='cs'))
        sm.add_widget(ProcessingScreen(name='pr'))
        sm.add_widget(ManualLinkListScreen(name='mll'))
        sm.add_widget(LinkEditorScreen(name='le'))
        sm.add_widget(CompleteScreen(name='cp'))
        sm.add_widget(FavoritesScreen(name='fv'))
        sm.add_widget(SettingsScreen(name='st'))
        return sm
    
    def tc(s, k):
        try:
            return get_color_from_hex(T(k))
        except:
            return [1, 1, 1, 1]
    
    def on_stop(s):
        db.close()
        gc_()


if __name__ == '__main__':
    IPTVApp().run()
