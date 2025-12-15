"""
IPTV Editor Pro v9.2 FINAL
- IPTV klasorune kayit
- Gercekci tarih kontrolu
- Performans optimizasyonu
- Her link ayri dosya
"""

import os, sys, re, gc, sqlite3, hashlib, traceback, threading, time
from datetime import datetime
from urllib.parse import urlparse, parse_qs
from functools import lru_cache
from collections import OrderedDict

def log_error(msg):
    try:
        p = os.path.join(os.path.expanduser('~'), 'iptv_error.log')
        with open(p, 'a') as f:
            f.write(f'\n{datetime.now()}\n{msg}\n')
    except: pass

sys.excepthook = lambda t,v,tb: log_error(''.join(traceback.format_exception(t,v,tb)))

from kivy.config import Config
Config.set('graphics', 'multisamples', '0')
Config.set('kivy', 'log_level', 'warning')

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.uix.slider import Slider
from kivy.uix.switch import Switch
from kivy.clock import Clock
from kivy.metrics import dp, sp
from kivy.core.window import Window
from kivy.core.clipboard import Clipboard
from kivy.properties import StringProperty, BooleanProperty, NumericProperty, ObjectProperty
from kivy.utils import get_color_from_hex
from kivy.animation import Animation
from kivy.graphics import Color, RoundedRectangle

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ==================== UNICODE SEMBOLLER ====================
class IC:
    HOME = '\u2302'      # ⌂
    BACK = '\u25C4'      # ◄
    NEXT = '\u25BA'      # ►
    UP = '\u25B2'        # ▲
    DOWN = '\u25BC'      # ▼
    CHECK = '\u2713'     # ✓
    CROSS = '\u2717'     # ✗
    PLUS = '\u002B'      # +
    STAR = '\u2605'      # ★
    STAR_O = '\u2606'    # ☆
    CIRCLE = '\u25CF'    # ●
    CIRCLE_O = '\u25CB'  # ○
    GEAR = '\u2699'      # ⚙
    EDIT = '\u270E'      # ✎
    SAVE = '\u2714'      # ✔
    DELETE = '\u2716'    # ✖
    LINK = '\u2197'      # ↗
    FILE = '\u25A1'      # □
    FOLDER = '\u25A3'    # ▣
    LIST = '\u2630'      # ☰
    REFRESH = '\u21BB'   # ↻
    WARN = '\u26A0'      # ⚠
    INFO = '\u2139'      # ℹ
    TV = '\u25A3'        # ▣
    PLAY = '\u25BA'      # ►
    PASTE = '\u2398'     # ⎘
    OK = '\u2714'        # ✔
    NO = '\u2718'        # ✘

I = IC()

APP_NAME = "IPTV Editor Pro"
APP_VERSION = "9.2"

# ==================== TEMALAR ====================
THEMES = {
    'dark': {
        'name': 'Koyu',
        'bg1': '#0d1b2a', 'bg2': '#1b263b',
        'card': '#22334a', 'card2': '#2d3f58', 'inp': '#1a2438',
        'acc': '#7b68ee', 'sec': '#ff6b9d',
        'ok': '#4ade80', 'warn': '#fbbf24', 'err': '#f87171', 'info': '#60a5fa',
        't1': '#ffffff', 't2': '#e2e8f0', 't3': '#94a3b8', 't4': '#64748b',
    },
    'light': {
        'name': 'Acik',
        'bg1': '#f8fafc', 'bg2': '#f1f5f9',
        'card': '#ffffff', 'card2': '#f8fafc', 'inp': '#f1f5f9',
        'acc': '#6366f1', 'sec': '#ec4899',
        'ok': '#22c55e', 'warn': '#f59e0b', 'err': '#ef4444', 'info': '#3b82f6',
        't1': '#1e293b', 't2': '#334155', 't3': '#64748b', 't4': '#94a3b8',
    },
    'amoled': {
        'name': 'AMOLED',
        'bg1': '#000000', 'bg2': '#0a0a0a',
        'card': '#141414', 'card2': '#1f1f1f', 'inp': '#0a0a0a',
        'acc': '#a78bfa', 'sec': '#f472b6',
        'ok': '#34d399', 'warn': '#fbbf24', 'err': '#fb7185', 'info': '#38bdf8',
        't1': '#ffffff', 't2': '#e5e5e5', 't3': '#a3a3a3', 't4': '#737373',
    },
}

current_theme = 'dark'
def T(key): return THEMES.get(current_theme, THEMES['dark']).get(key, '#ffffff')

# ==================== ULKELER ====================
COUNTRIES = {
    'turkey': {'name': 'TR Turkiye', 'c': ['tr', 'tur', 'turkey', 'turkiye', 'turk'], 'p': 1},
    'germany': {'name': 'DE Almanya', 'c': ['de', 'ger', 'germany', 'deutsch', 'almanya'], 'p': 2},
    'romania': {'name': 'RO Romanya', 'c': ['ro', 'rom', 'romania', 'romanya'], 'p': 3},
    'austria': {'name': 'AT Avusturya', 'c': ['at', 'aut', 'austria', 'avusturya', 'osterreich'], 'p': 4},
    'france': {'name': 'FR Fransa', 'c': ['fr', 'fra', 'france', 'fransa'], 'p': 5},
    'italy': {'name': 'IT Italya', 'c': ['it', 'ita', 'italy', 'italya'], 'p': 6},
    'spain': {'name': 'ES Ispanya', 'c': ['es', 'esp', 'spain', 'ispanya'], 'p': 7},
    'uk': {'name': 'UK Ingiltere', 'c': ['uk', 'gb', 'gbr', 'england', 'british'], 'p': 8},
    'usa': {'name': 'US Amerika', 'c': ['us', 'usa', 'america', 'amerika'], 'p': 9},
    'netherlands': {'name': 'NL Hollanda', 'c': ['nl', 'ned', 'netherlands', 'holland', 'dutch'], 'p': 10},
    'poland': {'name': 'PL Polonya', 'c': ['pl', 'pol', 'poland', 'polonya'], 'p': 11},
    'russia': {'name': 'RU Rusya', 'c': ['ru', 'rus', 'russia', 'rusya'], 'p': 12},
    'arabic': {'name': 'AR Arapca', 'c': ['ar', 'ara', 'arabic', 'arab', 'mbc'], 'p': 13},
    'india': {'name': 'IN Hindistan', 'c': ['in', 'ind', 'india', 'hindi'], 'p': 14},
    'portugal': {'name': 'PT Portekiz', 'c': ['pt', 'por', 'portugal'], 'p': 15},
    'greece': {'name': 'GR Yunanistan', 'c': ['gr', 'gre', 'greece', 'greek'], 'p': 16},
    'albania': {'name': 'AL Arnavutluk', 'c': ['al', 'alb', 'albania', 'shqip'], 'p': 17},
    'serbia': {'name': 'RS Sirbistan', 'c': ['rs', 'srb', 'serbia', 'serbian'], 'p': 18},
    'other': {'name': '-- Diger', 'c': ['other', 'misc', 'xxx'], 'p': 99},
}

PRIORITY_COUNTRIES = ['turkey', 'germany', 'romania', 'austria']
FORMATS = {'m3u': '.m3u', 'm3u8': '.m3u8', 'txt': '.txt'}

# ==================== CACHE ====================
class LRUCache:
    def __init__(self, capacity=200):
        self.cache = OrderedDict()
        self.cap = capacity
    
    def get(self, key):
        if key in self.cache:
            self.cache.move_to_end(key)
            return self.cache[key]
        return None
    
    def put(self, key, val):
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = val
        if len(self.cache) > self.cap:
            self.cache.popitem(last=False)
    
    def clear(self):
        self.cache.clear()

test_cache = LRUCache(300)

# ==================== HTTP ====================
def create_http():
    s = requests.Session()
    retry = Retry(total=2, backoff_factor=0.3, status_forcelist=[500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry, pool_connections=15, pool_maxsize=25)
    s.mount('http://', adapter)
    s.mount('https://', adapter)
    s.headers.update({
        'User-Agent': 'VLC/3.0.18 LibVLC/3.0.18',
        'Accept': '*/*',
        'Connection': 'keep-alive'
    })
    return s

http = create_http()

# ==================== PATH HELPERS ====================
def get_base_path():
    """Download klasorunu dondur"""
    try:
        from android.storage import primary_external_storage_path
        return os.path.join(primary_external_storage_path(), 'Download')
    except:
        return os.path.expanduser('~')

def get_iptv_folder():
    """IPTV klasorunu olustur ve dondur"""
    base = get_base_path()
    iptv_path = os.path.join(base, 'IPTV')
    try:
        os.makedirs(iptv_path, exist_ok=True)
    except:
        return base
    return iptv_path

def get_app_path():
    """Uygulama veri klasoru"""
    try:
        from android.storage import app_storage_path
        return app_storage_path()
    except:
        p = os.path.join(os.path.expanduser('~'), '.iptv_editor')
        os.makedirs(p, exist_ok=True)
        return p

def get_icon():
    for p in [os.path.join(get_base_path(), 'icon.png'), 'icon.png']:
        if os.path.exists(p):
            return p
    return None

def short_domain(url):
    """URL'den kisa domain adi cikar"""
    try:
        d = urlparse(url).netloc
        if d.startswith('www.'):
            d = d[4:]
        parts = d.split('.')
        if len(parts) > 2:
            return '.'.join(parts[-2:])[:18]
        return d[:18]
    except:
        return 'iptv'

def cleanup():
    gc.collect()

# ==================== EXPIRE DETECTION ====================
def extract_expire(content, url):
    """
    Gercekci tarih kontrolu:
    1. URL parametrelerinden
    2. Icerik icindeki patternlerden
    """
    now = datetime.now()
    
    # 1. URL parametrelerinden kontrol
    try:
        params = parse_qs(urlparse(url).query)
        for key in ['exp', 'expires', 'expire', 'e', 'expiry']:
            if key in params:
                ts = int(params[key][0])
                # Milisaniye ise saniyeye cevir
                if ts > 1e12:
                    ts //= 1000
                # Gecerli aralik kontrolu (2024-2030)
                if 1704067200 < ts < 1893456000:  # 2024-01-01 to 2030-01-01
                    dt = datetime.fromtimestamp(ts)
                    # Gecmis tarih mi kontrol et
                    if dt > now:
                        return dt.strftime('%d.%m.%Y')
                    else:
                        return f'{dt.strftime("%d.%m.%Y")} (SURESI DOLMUS)'
    except:
        pass
    
    # 2. Icerikten tarih cikarma
    patterns = [
        # exp=1234567890
        r'[?&]exp[ire]*[s]?=(\d{10,13})',
        # "exp": 1234567890
        r'"exp[ire]*[s]?":\s*(\d{10,13})',
        # expire: 1234567890  
        r'expire[s]?[:\s=]+(\d{10,13})',
        # #EXTINF icinde exp
        r'exp[=:](\d{10,13})',
    ]
    
    content_sample = content[:5000] if content else ''
    
    for pattern in patterns:
        matches = re.findall(pattern, content_sample, re.IGNORECASE)
        for match in matches:
            try:
                ts = int(match)
                if ts > 1e12:
                    ts //= 1000
                if 1704067200 < ts < 1893456000:
                    dt = datetime.fromtimestamp(ts)
                    if dt > now:
                        return dt.strftime('%d.%m.%Y')
                    else:
                        return f'{dt.strftime("%d.%m.%Y")} (SURESI DOLMUS)'
            except:
                continue
    
    # 3. Okunabilir tarih formati ara (dd.mm.yyyy veya dd/mm/yyyy)
    date_patterns = [
        r'(\d{2})[./](\d{2})[./](202[4-9]|203[0-5])',
        r'(202[4-9]|203[0-5])[./](\d{2})[./](\d{2})',
    ]
    
    for pattern in date_patterns:
        m = re.search(pattern, content_sample)
        if m:
            try:
                groups = m.groups()
                if len(groups[0]) == 4:  # YYYY.MM.DD
                    dt = datetime(int(groups[0]), int(groups[1]), int(groups[2]))
                else:  # DD.MM.YYYY
                    dt = datetime(int(groups[2]), int(groups[1]), int(groups[0]))
                if dt > now:
                    return dt.strftime('%d.%m.%Y')
            except:
                pass
    
    return 'Bilinmiyor'

# ==================== COUNTRY DETECTION ====================
@lru_cache(maxsize=2000)
def detect_country(grp):
    """Grup adından ülke tespit et"""
    if not grp:
        return 'other'
    g = grp.lower().strip()
    
    # Direkt eslesme kontrolleri
    for cid, cd in COUNTRIES.items():
        for code in cd['c']:
            # Tam eslesme
            if g == code:
                return cid
            # Basinda veya sonunda
            if g.startswith(code + ' ') or g.startswith(code + '-') or g.startswith(code + ':'):
                return cid
            if g.endswith(' ' + code) or g.endswith('-' + code) or g.endswith(':' + code):
                return cid
            # | ile ayrilmis
            if f'|{code}|' in f'|{g}|':
                return cid
    
    # Kelime bazli arama
    for cid, cd in COUNTRIES.items():
        for code in cd['c']:
            if re.search(rf'\b{re.escape(code)}\b', g):
                return cid
    
    return 'other'

# ==================== M3U PARSER ====================
# Precompiled regex for performance
GRP_RE = re.compile(r'group-title="([^"]*)"')
LOGO_RE = re.compile(r'tvg-logo="([^"]*)"')
NAME_RE = re.compile(r',([^,]+)$')

def parse_m3u(content, url=''):
    """M3U dosyasini parse et"""
    channels = []
    groups = {}
    expire = extract_expire(content, url)
    
    current = None
    lines = content.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        if line.startswith('#EXTINF:'):
            current = {'name': '', 'group': 'Diger', 'logo': '', 'url': ''}
            
            m = GRP_RE.search(line)
            if m and m.group(1):
                current['group'] = m.group(1).strip()
            
            m = LOGO_RE.search(line)
            if m:
                current['logo'] = m.group(1)
            
            m = NAME_RE.search(line)
            if m:
                current['name'] = m.group(1).strip()
                
        elif current and line.startswith(('http://', 'https://', 'rtmp://', 'rtsp://')):
            current['url'] = line
            channels.append(current)
            
            grp = current['group']
            if grp not in groups:
                groups[grp] = {
                    'channels': [],
                    'logo': current.get('logo', ''),
                    'country': detect_country(grp)
                }
            groups[grp]['channels'].append(current)
            current = None
    
    return channels, groups, expire

def gen_m3u(channels):
    """M3U dosyasi olustur"""
    lines = ['#EXTM3U']
    for ch in channels:
        extinf = '#EXTINF:-1'
        if ch.get('logo'):
            extinf += f' tvg-logo="{ch["logo"]}"'
        if ch.get('group'):
            extinf += f' group-title="{ch["group"]}"'
        extinf += f',{ch.get("name", "Channel")}'
        lines.append(extinf)
        lines.append(ch.get('url', ''))
    return '\n'.join(lines)

# ==================== LINK TESTING ====================
def test_quick(url, timeout=8):
    """Hizli HEAD testi"""
    try:
        r = http.head(url, timeout=timeout, allow_redirects=True)
        return r.status_code == 200, f"HTTP {r.status_code}"
    except requests.Timeout:
        return False, "Timeout"
    except:
        return False, "Hata"

def test_deep(url, timeout=12):
    """Derin icerik testi"""
    key = hashlib.md5(url.encode()).hexdigest()[:12]
    cached = test_cache.get(key)
    if cached:
        return cached
    
    try:
        r = http.get(url, timeout=timeout, stream=True)
        if r.status_code != 200:
            return False, f"HTTP {r.status_code}"
        
        content = ''
        total = 0
        for chunk in r.iter_content(8192, decode_unicode=True):
            if isinstance(chunk, bytes):
                content += chunk.decode('utf-8', errors='ignore')
            else:
                content += chunk
            total += len(chunk) if isinstance(chunk, str) else len(chunk)
            if total > 40000:
                break
        r.close()
        
        if len(content) < 50:
            return False, "Bos"
        
        if '#EXTINF' in content:
            chs, _, exp = parse_m3u(content, url)
            if chs:
                result = (True, f"{len(chs)} kanal")
            else:
                result = (False, "Kanal yok")
        else:
            result = (True, "Stream") if total > 3000 else (False, "Gecersiz")
        
        test_cache.put(key, result)
        return result
    except requests.Timeout:
        return False, "Timeout"
    except:
        return False, "Hata"

def find_duplicates(channels):
    """Duplicate linkleri bul ve temizle"""
    seen = {}
    unique = []
    for ch in channels:
        url = ch.get('url', '')
        if url and url not in seen:
            seen[url] = True
            unique.append(ch)
    return unique, len(channels) - len(unique)

# ==================== DATABASE ====================
class Database:
    def __init__(self):
        self.path = os.path.join(get_app_path(), 'iptv.db')
        self.conn = None
        self._init()
    
    def _get_conn(self):
        if not self.conn:
            self.conn = sqlite3.connect(self.path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
        return self.conn
    
    def _init(self):
        c = self._get_conn().cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS settings 
            (key TEXT PRIMARY KEY, value TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS favorites 
            (id INTEGER PRIMARY KEY, url TEXT UNIQUE, name TEXT, expire TEXT, 
             count INTEGER DEFAULT 0, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        c.execute('''CREATE TABLE IF NOT EXISTS stats 
            (id INTEGER PRIMARY KEY, date TEXT UNIQUE, 
             tested INTEGER DEFAULT 0, working INTEGER DEFAULT 0, 
             channels INTEGER DEFAULT 0, files INTEGER DEFAULT 0)''')
        self._get_conn().commit()
        
        defaults = {
            'theme': 'dark',
            'test_mode': 'deep',
            'format': 'm3u8',
            'auto_dup': 'true',
            'timeout': '12'
        }
        for k, v in defaults.items():
            c.execute('INSERT OR IGNORE INTO settings VALUES (?, ?)', (k, v))
        self._get_conn().commit()
    
    def get(self, key, default=None):
        c = self._get_conn().cursor()
        c.execute('SELECT value FROM settings WHERE key=?', (key,))
        r = c.fetchone()
        return r['value'] if r else default
    
    def set(self, key, value):
        self._get_conn().cursor().execute(
            'INSERT OR REPLACE INTO settings VALUES (?, ?)', (key, str(value)))
        self._get_conn().commit()
    
    def add_fav(self, url, name='', expire='', count=0):
        try:
            self._get_conn().cursor().execute(
                'INSERT OR REPLACE INTO favorites (url, name, expire, count) VALUES (?, ?, ?, ?)',
                (url, name or short_domain(url), expire, count))
            self._get_conn().commit()
            return True
        except:
            return False
    
    def del_fav(self, url):
        self._get_conn().cursor().execute('DELETE FROM favorites WHERE url=?', (url,))
        self._get_conn().commit()
    
    def get_favs(self):
        c = self._get_conn().cursor()
        c.execute('SELECT * FROM favorites ORDER BY created_at DESC')
        return [dict(r) for r in c.fetchall()]
    
    def update_stats(self, tested=0, working=0, channels=0, files=0):
        today = datetime.now().strftime('%Y-%m-%d')
        c = self._get_conn().cursor()
        c.execute('SELECT * FROM stats WHERE date=?', (today,))
        if c.fetchone():
            c.execute('''UPDATE stats SET tested=tested+?, working=working+?, 
                channels=channels+?, files=files+? WHERE date=?''',
                (tested, working, channels, files, today))
        else:
            c.execute('INSERT INTO stats (date, tested, working, channels, files) VALUES (?, ?, ?, ?, ?)',
                (today, tested, working, channels, files))
        self._get_conn().commit()
    
    def get_total_stats(self):
        c = self._get_conn().cursor()
        c.execute('SELECT SUM(tested) as t, SUM(working) as w, SUM(channels) as c, SUM(files) as f FROM stats')
        r = c.fetchone()
        return {
            'tested': r['t'] or 0,
            'working': r['w'] or 0,
            'channels': r['c'] or 0,
            'files': r['f'] or 0
        }
    
    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None

db = Database()

# ==================== KIVY KV ====================
KV = '''
#:import dp kivy.metrics.dp
#:import sp kivy.metrics.sp

<BaseScreen>:
    canvas.before:
        Color:
            rgba: app.tc('bg1')
        Rectangle:
            pos: self.pos
            size: self.size

<AnimProgress>:
    canvas:
        Color:
            rgba: app.tc('card')
        RoundedRectangle:
            pos: self.x, self.center_y - dp(8)
            size: self.width, dp(16)
            radius: [dp(8)]
        Color:
            rgba: app.tc('acc')
        RoundedRectangle:
            pos: self.x + dp(2), self.center_y - dp(6)
            size: max(0, (self.width - dp(4)) * self.value / 100.0), dp(12)
            radius: [dp(6)]

<RV>:
    viewclass: 'GroupRow'
    RecycleBoxLayout:
        default_size: None, dp(62)
        default_size_hint: 1, None
        size_hint_y: None
        height: self.minimum_height
        orientation: 'vertical'
        spacing: dp(5)
        padding: [dp(4), dp(4)]

<GroupRow>:
    orientation: 'horizontal'
    size_hint_y: None
    height: dp(62)
    padding: [dp(10), dp(6)]
    spacing: dp(10)
    canvas.before:
        Color:
            rgba: app.tc('ok') if self.is_selected else app.tc('card')
            a: 0.25 if self.is_selected else 1
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(10)]
    Label:
        text: root.flag
        font_size: sp(11)
        size_hint_x: None
        width: dp(32)
        color: app.tc('t3')
    BoxLayout:
        orientation: 'vertical'
        spacing: dp(2)
        Label:
            text: root.display_name
            font_size: sp(11)
            color: app.tc('t1')
            text_size: self.size
            halign: 'left'
            valign: 'middle'
            shorten: True
        Label:
            text: str(root.ch_count) + ' kanal'
            font_size: sp(9)
            color: app.tc('t3')
            text_size: self.size
            halign: 'left'
    Button:
        size_hint: None, None
        size: dp(42), dp(42)
        text: '\\u2714' if root.is_selected else '+'
        font_size: sp(14)
        background_normal: ''
        background_color: app.tc('ok') if root.is_selected else app.tc('acc')
        on_press: root.do_toggle()
'''

Builder.load_string(KV)

# ==================== WIDGETS ====================
class BaseScreen(Screen):
    pass

class AnimProgress(Widget):
    value = NumericProperty(0)
    
    def set_value(self, v, animate=True):
        v = min(100, max(0, v))
        if animate:
            Animation(value=v, duration=0.25, t='out_quad').start(self)
        else:
            self.value = v

class GroupRow(RecycleDataViewBehavior, BoxLayout):
    index = None
    is_selected = BooleanProperty(False)
    grp_name = StringProperty('')
    ch_count = NumericProperty(0)
    country = StringProperty('other')
    flag = StringProperty('')
    display_name = StringProperty('')
    callback = ObjectProperty(None)
    
    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        self.grp_name = data.get('grp_name', '')
        self.ch_count = data.get('ch_count', 0)
        self.is_selected = data.get('is_selected', False)
        self.country = data.get('country', 'other')
        self.callback = data.get('callback', None)
        
        name = self.grp_name
        self.display_name = name[:28] + ('...' if len(name) > 28 else '')
        
        cd = COUNTRIES.get(self.country, COUNTRIES['other'])
        self.flag = cd['name'][:2]
        
        return super().refresh_view_attrs(rv, index, data)
    
    def do_toggle(self):
        self.is_selected = not self.is_selected
        if self.callback:
            self.callback(self.grp_name, self.is_selected, self.index)

class RV(RecycleView):
    pass

# ==================== SCREENS ====================
class WelcomeScreen(BaseScreen):
    def on_enter(self):
        self.clear_widgets()
        Clock.schedule_once(lambda dt: self.build(), 0.05)
    
    def build(self):
        app = App.get_running_app()
        root = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(12))
        
        # Header
        header = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(95), spacing=dp(4))
        logo_box = BoxLayout(size_hint_y=None, height=dp(50))
        icon_path = get_icon()
        if icon_path:
            logo = Image(source=icon_path, size_hint=(None, None), size=(dp(45), dp(45)))
        else:
            logo = Label(text=I.TV, font_size=sp(32), bold=True)
        logo_box.add_widget(Widget())
        logo_box.add_widget(logo)
        logo_box.add_widget(Widget())
        header.add_widget(logo_box)
        header.add_widget(Label(text=APP_NAME, font_size=sp(18), bold=True, 
            color=app.tc('t1'), size_hint_y=None, height=dp(24)))
        header.add_widget(Label(text=f'v{APP_VERSION}', font_size=sp(9), 
            color=app.tc('t3'), size_hint_y=None, height=dp(14)))
        root.add_widget(header)
        
        # Stats
        stats = db.get_total_stats()
        stats_card = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(4))
        for val, lbl in [(stats['tested'], 'Test'), (stats['working'], 'OK'), 
                         (stats['channels'], 'Kanal'), (stats['files'], 'Dosya')]:
            box = BoxLayout(orientation='vertical')
            self._card_bg(box)
            box.add_widget(Label(text=str(val), font_size=sp(13), bold=True, color=app.tc('acc')))
            box.add_widget(Label(text=lbl, font_size=sp(8), color=app.tc('t3')))
            stats_card.add_widget(box)
        root.add_widget(stats_card)
        
        # IPTV folder info
        iptv_path = get_iptv_folder()
        root.add_widget(Label(text=f'{I.FOLDER} Kayit: IPTV/', font_size=sp(8), 
            color=app.tc('info'), size_hint_y=None, height=dp(16)))
        
        # Actions
        actions = ScrollView(size_hint_y=1)
        al = BoxLayout(orientation='vertical', spacing=dp(8), size_hint_y=None, padding=[0, dp(4)])
        al.bind(minimum_height=al.setter('height'))
        
        menu_items = [
            ('Manuel Duzenleme', 'URL gir, kanallari sec', f'{I.NEXT} Basla', 'acc', 'manual_input'),
            ('Otomatik Duzenleme', 'Toplu test, ulke filtresi', f'{I.NEXT} Basla', 'sec', 'auto_input'),
            (f'Favoriler ({len(db.get_favs())})', 'Kayitli linkler', f'{I.NEXT} Ac', 'warn', 'favorites'),
            ('Ayarlar', 'Tema, performans', f'{I.GEAR} Ac', 'info', 'settings'),
        ]
        
        for title, desc, btn_txt, color, screen in menu_items:
            card = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(4), 
                size_hint_y=None, height=dp(82))
            self._card_bg(card)
            card.add_widget(Label(text=title, font_size=sp(12), bold=True, 
                color=app.tc('t1'), halign='left', size_hint_y=None, height=dp(20)))
            card.add_widget(Label(text=desc, font_size=sp(9), color=app.tc('t3'), 
                size_hint_y=None, height=dp(14)))
            btn = Button(text=btn_txt, font_size=sp(10), bold=True, 
                size_hint=(0.45, None), height=dp(32), pos_hint={'center_x': 0.5},
                background_normal='', background_color=app.tc(color))
            btn.bind(on_press=lambda x, s=screen: self.goto(s))
            card.add_widget(btn)
            al.add_widget(card)
        
        actions.add_widget(al)
        root.add_widget(actions)
        self.add_widget(root)
    
    def _card_bg(self, w):
        with w.canvas.before:
            Color(*App.get_running_app().tc('card'))
            w._bg = RoundedRectangle(pos=w.pos, size=w.size, radius=[dp(8)])
        w.bind(pos=self._upd, size=self._upd)
    
    def _upd(self, w, v):
        if hasattr(w, '_bg'):
            w._bg.pos, w._bg.size = w.pos, w.size
    
    def goto(self, s):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = s


class ManualInputScreen(BaseScreen):
    def on_enter(self):
        self.clear_widgets()
        self.fmt = db.get('format', 'm3u8')
        self.remove_dups = db.get('auto_dup', 'true') == 'true'
        Clock.schedule_once(lambda dt: self.build(), 0.05)
    
    def build(self):
        app = App.get_running_app()
        root = BoxLayout(orientation='vertical', padding=dp(14), spacing=dp(8))
        
        # Top bar
        top = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(8))
        back = Button(text=I.BACK, size_hint=(None, None), size=(dp(42), dp(38)),
            font_size=sp(16), background_normal='', background_color=app.tc('card'))
        back.bind(on_press=lambda x: self.go_back())
        top.add_widget(back)
        top.add_widget(Label(text='Manuel Duzenleme', font_size=sp(14), bold=True, color=app.tc('t1')))
        root.add_widget(top)
        
        # URL input
        url_card = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(6), 
            size_hint_y=None, height=dp(95))
        self._card_bg(url_card)
        url_card.add_widget(Label(text='Playlist URL', font_size=sp(10), 
            color=app.tc('t3'), size_hint_y=None, height=dp(14), halign='left'))
        
        url_row = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(6))
        self.url_inp = TextInput(hint_text='https://example.com/playlist.m3u',
            multiline=False, font_size=sp(11), background_color=app.tc('inp'),
            foreground_color=app.tc('t1'), padding=[dp(8), dp(8)])
        url_row.add_widget(self.url_inp)
        paste_btn = Button(text=I.PASTE, size_hint=(None, None), size=(dp(40), dp(40)),
            font_size=sp(14), background_normal='', background_color=app.tc('card2'))
        paste_btn.bind(on_press=lambda x: setattr(self.url_inp, 'text', Clipboard.paste() or ''))
        url_row.add_widget(paste_btn)
        url_card.add_widget(url_row)
        
        # Quick favorite
        favs = db.get_favs()
        if favs:
            fav_btn = Button(text=f'{I.STAR} {favs[0]["name"][:18]}', font_size=sp(8),
                size_hint_y=None, height=dp(22), background_normal='',
                background_color=app.tc('warn')[:3] + [0.3])
            fav_btn.bind(on_press=lambda x: setattr(self.url_inp, 'text', favs[0]['url']))
            url_card.add_widget(fav_btn)
        root.add_widget(url_card)
        
        # Format selection
        fmt_card = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(4),
            size_hint_y=None, height=dp(72))
        self._card_bg(fmt_card)
        fmt_card.add_widget(Label(text='Cikti Formati', font_size=sp(10),
            color=app.tc('t3'), size_hint_y=None, height=dp(14)))
        
        fmt_row = BoxLayout(spacing=dp(6), size_hint_y=None, height=dp(36))
        self.fmt_btns = {}
        for fid in ['m3u', 'm3u8', 'txt']:
            is_sel = fid == self.fmt
            btn = ToggleButton(text=fid.upper(), group='fmt', 
                state='down' if is_sel else 'normal', font_size=sp(10),
                background_normal='', 
                background_color=app.tc('acc') if is_sel else app.tc('card2'))
            btn.fid = fid
            btn.bind(on_press=self.on_fmt)
            self.fmt_btns[fid] = btn
            fmt_row.add_widget(btn)
        fmt_card.add_widget(fmt_row)
        root.add_widget(fmt_card)
        
        # Options
        opt_row = BoxLayout(size_hint_y=None, height=dp(38), spacing=dp(6))
        dup_btn = ToggleButton(text=f'{I.CHECK} Duplicate Temizle',
            state='down' if self.remove_dups else 'normal', font_size=sp(9),
            background_normal='',
            background_color=app.tc('ok') if self.remove_dups else app.tc('card2'))
        dup_btn.bind(on_press=lambda x: setattr(self, 'remove_dups', x.state == 'down'))
        opt_row.add_widget(dup_btn)
        root.add_widget(opt_row)
        
        root.add_widget(Widget())
        
        # Load button
        load_btn = Button(text=f'{I.DOWN} Kanallari Yukle', font_size=sp(13), bold=True,
            size_hint_y=None, height=dp(48), background_normal='', background_color=app.tc('ok'))
        load_btn.bind(on_press=self.load)
        root.add_widget(load_btn)
        
        self.add_widget(root)
    
    def _card_bg(self, w):
        with w.canvas.before:
            Color(*App.get_running_app().tc('card'))
            w._bg = RoundedRectangle(pos=w.pos, size=w.size, radius=[dp(8)])
        w.bind(pos=self._upd, size=self._upd)
    
    def _upd(self, w, v):
        if hasattr(w, '_bg'):
            w._bg.pos, w._bg.size = w.pos, w.size
    
    def on_fmt(self, btn):
        app = App.get_running_app()
        self.fmt = btn.fid
        for fid, b in self.fmt_btns.items():
            b.background_color = app.tc('acc') if fid == self.fmt else app.tc('card2')
    
    def load(self, *args):
        url = self.url_inp.text.strip()
        if not url:
            return self.popup(I.WARN, 'URL girin!')
        if not url.startswith('http'):
            return self.popup(I.CROSS, 'Gecersiz URL!')
        
        self.show_loading()
        threading.Thread(target=self._load, args=(url,), daemon=True).start()
    
    def _load(self, url):
        try:
            Clock.schedule_once(lambda dt: self.upd_load(10, 'Baglaniyor...'))
            r = http.get(url, timeout=30)
            Clock.schedule_once(lambda dt: self.upd_load(40, 'Indiriliyor...'))
            content = r.text
            Clock.schedule_once(lambda dt: self.upd_load(60, 'Ayristiriliyor...'))
            channels, groups, expire = parse_m3u(content, url)
            
            if not channels:
                return Clock.schedule_once(lambda dt: self._err('Kanal bulunamadi!'))
            
            Clock.schedule_once(lambda dt: self.upd_load(80, 'Isleniyor...'))
            
            if self.remove_dups:
                channels, removed = find_duplicates(channels)
                groups = {}
                for ch in channels:
                    grp = ch['group']
                    if grp not in groups:
                        groups[grp] = {'channels': [], 'logo': ch.get('logo', ''), 
                                       'country': detect_country(grp)}
                    groups[grp]['channels'].append(ch)
            
            Clock.schedule_once(lambda dt: self.upd_load(100, 'Tamamlandi!'))
            Clock.schedule_once(lambda dt: self._ok(channels, groups, expire, url), 0.3)
        except Exception as e:
            Clock.schedule_once(lambda dt: self._err(str(e)[:30]))
    
    def _ok(self, channels, groups, expire, url):
        self.hide_loading()
        app = App.get_running_app()
        app.channels = channels
        app.groups = groups
        app.expire = expire
        app.src_url = url
        app.fmt = self.fmt
        cleanup()
        self.manager.current = 'channel_list'
    
    def _err(self, msg):
        self.hide_loading()
        self.popup(I.CROSS, msg)
    
    def show_loading(self):
        app = App.get_running_app()
        c = BoxLayout(orientation='vertical', padding=dp(18), spacing=dp(8))
        self.l_icon = Label(text=I.REFRESH, font_size=sp(28))
        c.add_widget(self.l_icon)
        self.l_msg = Label(text='Baslatiliyor...', font_size=sp(11), color=app.tc('t1'))
        c.add_widget(self.l_msg)
        self.l_prog = AnimProgress(size_hint_y=None, height=dp(16))
        c.add_widget(self.l_prog)
        self.l_pct = Label(text='%0', font_size=sp(16), bold=True, color=app.tc('acc'))
        c.add_widget(self.l_pct)
        self._pop = Popup(title='', content=c, size_hint=(0.72, 0.35), 
            auto_dismiss=False, separator_height=0)
        self._pop.open()
    
    def upd_load(self, pct, msg):
        if hasattr(self, 'l_prog'):
            self.l_prog.set_value(pct)
            self.l_pct.text = f'%{int(pct)}'
            self.l_msg.text = msg
    
    def hide_loading(self):
        if hasattr(self, '_pop'):
            self._pop.dismiss()
    
    def popup(self, icon, msg):
        app = App.get_running_app()
        c = BoxLayout(orientation='vertical', padding=dp(18), spacing=dp(10))
        c.add_widget(Label(text=icon, font_size=sp(28)))
        c.add_widget(Label(text=msg, font_size=sp(11), color=app.tc('t1'), halign='center'))
        btn = Button(text='Tamam', size_hint=(0.5, None), height=dp(36),
            pos_hint={'center_x': 0.5}, background_normal='', background_color=app.tc('warn'))
        p = Popup(title='', content=c, size_hint=(0.72, 0.32), separator_height=0)
        btn.bind(on_press=p.dismiss)
        c.add_widget(btn)
        p.open()
    
    def go_back(self):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'welcome'


class ChannelListScreen(BaseScreen):
    def on_enter(self):
        self.clear_widgets()
        self.selected = set()
        Clock.schedule_once(lambda dt: self.build(), 0.05)
    
    def build(self):
        app = App.get_running_app()
        groups = getattr(app, 'groups', {})
        channels = getattr(app, 'channels', [])
        expire = getattr(app, 'expire', 'Bilinmiyor')
        
        root = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(6))
        
        # Top bar
        top = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(6))
        back = Button(text=I.BACK, size_hint=(None, None), size=(dp(42), dp(38)),
            font_size=sp(16), background_normal='', background_color=app.tc('card'))
        back.bind(on_press=lambda x: self.go_back())
        top.add_widget(back)
        top.add_widget(Label(text='Kanal Gruplari', font_size=sp(13), bold=True, color=app.tc('t1')))
        fav_btn = Button(text=I.STAR, size_hint=(None, None), size=(dp(42), dp(38)),
            font_size=sp(18), background_normal='', background_color=app.tc('warn'))
        fav_btn.bind(on_press=self.add_fav)
        top.add_widget(fav_btn)
        root.add_widget(top)
        
        # Info
        info = BoxLayout(size_hint_y=None, height=dp(48), orientation='vertical')
        info.add_widget(Label(text=f'{len(groups)} grup | {len(channels)} kanal', 
            font_size=sp(10), color=app.tc('t3')))
        
        # Expire color based on status
        exp_color = app.tc('err') if 'DOLMUS' in expire else app.tc('warn')
        info.add_widget(Label(text=f'Bitis: {expire}', font_size=sp(9), color=exp_color))
        
        self.sel_lbl = Label(text='Secilen: 0 grup (0 kanal)', font_size=sp(9), color=app.tc('ok'))
        info.add_widget(self.sel_lbl)
        root.add_widget(info)
        
        # Search
        search_row = BoxLayout(size_hint_y=None, height=dp(38), spacing=dp(4))
        self.search_inp = TextInput(hint_text='Ara...', multiline=False, font_size=sp(10),
            background_color=app.tc('card'), foreground_color=app.tc('t1'), size_hint_x=0.78)
        self.search_inp.bind(text=self.on_search)
        search_row.add_widget(self.search_inp)
        clear_btn = Button(text=I.CROSS, size_hint=(None, None), size=(dp(38), dp(34)),
            font_size=sp(12), background_normal='', background_color=app.tc('card'))
        clear_btn.bind(on_press=lambda x: setattr(self.search_inp, 'text', ''))
        search_row.add_widget(clear_btn)
        root.add_widget(search_row)
        
        # RecycleView
        self.rv = RV()
        self.all_data = []
        for gn, gd in sorted(groups.items()):
            self.all_data.append({
                'grp_name': gn,
                'ch_count': len(gd['channels']),
                'country': gd.get('country', 'other'),
                'is_selected': False,
                'callback': self.on_sel
            })
        self.rv_data = self.all_data.copy()
        self.rv.data = self.rv_data
        root.add_widget(self.rv)
        
        # Bottom buttons
        btm = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(6))
        sel_all = Button(text='Tumunu Sec', font_size=sp(11), bold=True,
            background_normal='', background_color=app.tc('acc'))
        sel_all.bind(on_press=self.sel_all)
        btm.add_widget(sel_all)
        exp_btn = Button(text=f'{I.UP} Disa Aktar', font_size=sp(11), bold=True,
            background_normal='', background_color=app.tc('ok'))
        exp_btn.bind(on_press=self.export)
        btm.add_widget(exp_btn)
        root.add_widget(btm)
        
        self.add_widget(root)
    
    def on_search(self, inp, txt):
        if txt:
            self.rv_data = [d for d in self.all_data if txt.lower() in d['grp_name'].lower()]
        else:
            self.rv_data = self.all_data.copy()
        self.rv.data = self.rv_data
    
    def on_sel(self, gn, sel, idx):
        for d in self.all_data:
            if d['grp_name'] == gn:
                d['is_selected'] = sel
        for d in self.rv_data:
            if d['grp_name'] == gn:
                d['is_selected'] = sel
        
        if sel:
            self.selected.add(gn)
        else:
            self.selected.discard(gn)
        
        groups = getattr(App.get_running_app(), 'groups', {})
        total = sum(len(groups[g]['channels']) for g in self.selected if g in groups)
        self.sel_lbl.text = f'Secilen: {len(self.selected)} grup ({total} kanal)'
    
    def sel_all(self, *args):
        groups = getattr(App.get_running_app(), 'groups', {})
        for d in self.all_data:
            d['is_selected'] = True
            self.selected.add(d['grp_name'])
        self.rv_data = self.all_data.copy()
        self.rv.data = self.rv_data
        self.rv.refresh_from_data()
        total = sum(len(groups[g]['channels']) for g in self.selected if g in groups)
        self.sel_lbl.text = f'Secilen: {len(self.selected)} grup ({total} kanal)'
    
    def add_fav(self, *args):
        app = App.get_running_app()
        url = getattr(app, 'src_url', '')
        channels = getattr(app, 'channels', [])
        expire = getattr(app, 'expire', '')
        if url:
            db.add_fav(url, short_domain(url), expire, len(channels))
            self.popup(I.STAR, 'Favorilere eklendi!')
    
    def export(self, *args):
        if not self.selected:
            return self.popup(I.WARN, 'Grup secin!')
        
        app = App.get_running_app()
        groups = getattr(app, 'groups', {})
        fmt = getattr(app, 'fmt', 'm3u8')
        expire = getattr(app, 'expire', '')
        url = getattr(app, 'src_url', '')
        
        channels = []
        for gn in self.selected:
            if gn in groups:
                channels.extend(groups[gn]['channels'])
        
        content = gen_m3u(channels)
        path = get_iptv_folder()
        
        # Dosya adi olustur
        if expire and expire != 'Bilinmiyor' and 'DOLMUS' not in expire:
            exp_str = expire.replace('.', '')
        else:
            exp_str = datetime.now().strftime('%d%m%Y')
        
        fname = f'bitis{exp_str}_{short_domain(url)}{FORMATS.get(fmt, ".m3u8")}'
        
        try:
            with open(os.path.join(path, fname), 'w', encoding='utf-8') as f:
                f.write(content)
            db.update_stats(channels=len(channels), files=1)
            self.popup(I.CHECK, f'{len(channels)} kanal kaydedildi!\n\nIPTV/{fname}')
        except Exception as e:
            self.popup(I.CROSS, str(e)[:30])
        
        cleanup()
    
    def popup(self, icon, msg):
        app = App.get_running_app()
        c = BoxLayout(orientation='vertical', padding=dp(18), spacing=dp(10))
        c.add_widget(Label(text=icon, font_size=sp(28)))
        c.add_widget(Label(text=msg, font_size=sp(10), color=app.tc('t1'), halign='center'))
        btn = Button(text='Tamam', size_hint=(0.5, None), height=dp(36),
            pos_hint={'center_x': 0.5}, background_normal='', background_color=app.tc('acc'))
        p = Popup(title='', content=c, size_hint=(0.78, 0.36), separator_height=0)
        btn.bind(on_press=p.dismiss)
        c.add_widget(btn)
        p.open()
    
    def go_back(self):
        cleanup()
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'manual_input'


class AutoInputScreen(BaseScreen):
    def on_enter(self):
        self.clear_widgets()
        self.test_mode = db.get('test_mode', 'deep')
        Clock.schedule_once(lambda dt: self.build(), 0.05)
    
    def build(self):
        app = App.get_running_app()
        root = BoxLayout(orientation='vertical', padding=dp(14), spacing=dp(8))
        
        # Top bar
        top = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(8))
        back = Button(text=I.BACK, size_hint=(None, None), size=(dp(42), dp(38)),
            font_size=sp(16), background_normal='', background_color=app.tc('card'))
        back.bind(on_press=lambda x: self.go_back())
        top.add_widget(back)
        top.add_widget(Label(text='Otomatik Duzenleme', font_size=sp(14), bold=True, color=app.tc('t1')))
        root.add_widget(top)
        
        root.add_widget(Label(text='Her satira bir IPTV linki girin', font_size=sp(9),
            color=app.tc('t3'), size_hint_y=None, height=dp(16)))
        
        # Links input
        inp_card = BoxLayout(orientation='vertical', padding=dp(8), spacing=dp(4))
        self._card_bg(inp_card)
        self.links_inp = TextInput(
            hint_text='https://example1.com/get.php?...\nhttps://example2.com/get.php?...',
            multiline=True, font_size=sp(9), background_color=app.tc('inp'),
            foreground_color=app.tc('t1'))
        inp_card.add_widget(self.links_inp)
        
        btn_row = BoxLayout(size_hint_y=None, height=dp(32), spacing=dp(4))
        paste_btn = Button(text=f'{I.PASTE} Yapistir', font_size=sp(9),
            background_normal='', background_color=app.tc('card2'))
        paste_btn.bind(on_press=lambda x: setattr(self.links_inp, 'text', Clipboard.paste() or ''))
        btn_row.add_widget(paste_btn)
        clear_btn = Button(text=f'{I.DELETE} Temizle', font_size=sp(9),
            background_normal='', background_color=app.tc('card2'))
        clear_btn.bind(on_press=lambda x: setattr(self.links_inp, 'text', ''))
        btn_row.add_widget(clear_btn)
        inp_card.add_widget(btn_row)
        root.add_widget(inp_card)
        
        # Test mode
        mode_card = BoxLayout(orientation='vertical', padding=dp(8), spacing=dp(4),
            size_hint_y=None, height=dp(75))
        self._card_bg(mode_card)
        mode_card.add_widget(Label(text='Test Yontemi', font_size=sp(9),
            color=app.tc('t3'), size_hint_y=None, height=dp(14)))
        
        mode_row = BoxLayout(spacing=dp(6), size_hint_y=None, height=dp(36))
        self.quick_btn = ToggleButton(text='Hizli (HEAD)', group='mode',
            state='down' if self.test_mode == 'quick' else 'normal', font_size=sp(10),
            background_normal='',
            background_color=app.tc('acc') if self.test_mode == 'quick' else app.tc('card2'))
        self.quick_btn.bind(on_press=lambda x: self.set_mode('quick'))
        mode_row.add_widget(self.quick_btn)
        
        self.deep_btn = ToggleButton(text=f'Derin {I.STAR}', group='mode',
            state='down' if self.test_mode == 'deep' else 'normal', font_size=sp(10),
            background_normal='',
            background_color=app.tc('acc') if self.test_mode == 'deep' else app.tc('card2'))
        self.deep_btn.bind(on_press=lambda x: self.set_mode('deep'))
        mode_row.add_widget(self.deep_btn)
        mode_card.add_widget(mode_row)
        root.add_widget(mode_card)
        
        # Start button
        start_btn = Button(text=f'{I.PLAY} Test Baslat', font_size=sp(13), bold=True,
            size_hint_y=None, height=dp(46), background_normal='', background_color=app.tc('ok'))
        start_btn.bind(on_press=self.start)
        root.add_widget(start_btn)
        
        self.add_widget(root)
    
    def _card_bg(self, w):
        with w.canvas.before:
            Color(*App.get_running_app().tc('card'))
            w._bg = RoundedRectangle(pos=w.pos, size=w.size, radius=[dp(8)])
        w.bind(pos=self._upd, size=self._upd)
    
    def _upd(self, w, v):
        if hasattr(w, '_bg'):
            w._bg.pos, w._bg.size = w.pos, w.size
    
    def set_mode(self, m):
        app = App.get_running_app()
        self.test_mode = m
        db.set('test_mode', m)
        self.quick_btn.background_color = app.tc('acc') if m == 'quick' else app.tc('card2')
        self.deep_btn.background_color = app.tc('acc') if m == 'deep' else app.tc('card2')
    
    def start(self, *args):
        txt = self.links_inp.text.strip()
        if not txt:
            return self.popup(I.WARN, 'Link girin!')
        
        links = [l.strip() for l in txt.split('\n') if l.strip().startswith('http')]
        if not links:
            return self.popup(I.CROSS, 'Gecerli link yok!')
        
        app = App.get_running_app()
        app.test_links = links
        app.test_mode = self.test_mode
        self.manager.current = 'testing'
    
    def popup(self, icon, msg):
        app = App.get_running_app()
        c = BoxLayout(orientation='vertical', padding=dp(18), spacing=dp(10))
        c.add_widget(Label(text=icon, font_size=sp(28)))
        c.add_widget(Label(text=msg, font_size=sp(11), color=app.tc('t1')))
        btn = Button(text='Tamam', size_hint=(0.5, None), height=dp(36),
            pos_hint={'center_x': 0.5}, background_normal='', background_color=app.tc('warn'))
        p = Popup(title='', content=c, size_hint=(0.72, 0.32), separator_height=0)
        btn.bind(on_press=p.dismiss)
        c.add_widget(btn)
        p.open()
    
    def go_back(self):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'welcome'


class TestingScreen(BaseScreen):
    def on_enter(self):
        self.clear_widgets()
        self.testing = True
        self.working = []
        self.failed = []
        Clock.schedule_once(lambda dt: self.build(), 0.05)
        Clock.schedule_once(lambda dt: self.run(), 0.2)
    
    def build(self):
        app = App.get_running_app()
        root = BoxLayout(orientation='vertical', padding=dp(14), spacing=dp(8))
        
        root.add_widget(Label(text=f'{I.REFRESH} Test Ediliyor...', font_size=sp(16), bold=True,
            color=app.tc('t1'), size_hint_y=None, height=dp(32)))
        
        # Progress card
        prog_card = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(6),
            size_hint_y=None, height=dp(105))
        self._card_bg(prog_card)
        
        self.prog_lbl = Label(text='Hazirlaniyor...', font_size=sp(10),
            color=app.tc('t2'), size_hint_y=None, height=dp(18))
        prog_card.add_widget(self.prog_lbl)
        
        self.prog_bar = AnimProgress(size_hint_y=None, height=dp(18))
        prog_card.add_widget(self.prog_bar)
        
        self.pct_lbl = Label(text='%0', font_size=sp(18), bold=True,
            color=app.tc('acc'), size_hint_y=None, height=dp(26))
        prog_card.add_widget(self.pct_lbl)
        
        self.stats_lbl = Label(text=f'{I.CHECK} 0  |  {I.CROSS} 0', font_size=sp(9),
            color=app.tc('t3'), size_hint_y=None, height=dp(16))
        prog_card.add_widget(self.stats_lbl)
        root.add_widget(prog_card)
        
        # Log
        log_card = BoxLayout(orientation='vertical', padding=dp(8), spacing=dp(4))
        self._card_bg(log_card)
        log_card.add_widget(Label(text='Log', font_size=sp(9), color=app.tc('t3'),
            size_hint_y=None, height=dp(14), halign='left'))
        
        scroll = ScrollView()
        self.log_box = BoxLayout(orientation='vertical', spacing=dp(2), size_hint_y=None)
        self.log_box.bind(minimum_height=self.log_box.setter('height'))
        scroll.add_widget(self.log_box)
        log_card.add_widget(scroll)
        root.add_widget(log_card)
        
        # Action button
        self.act_btn = Button(text=f'{I.CROSS} Iptal', font_size=sp(12), bold=True,
            size_hint_y=None, height=dp(44), background_normal='', background_color=app.tc('err'))
        self.act_btn.bind(on_press=self.on_action)
        root.add_widget(self.act_btn)
        
        self.add_widget(root)
    
    def _card_bg(self, w):
        with w.canvas.before:
            Color(*App.get_running_app().tc('card'))
            w._bg = RoundedRectangle(pos=w.pos, size=w.size, radius=[dp(8)])
        w.bind(pos=self._upd, size=self._upd)
    
    def _upd(self, w, v):
        if hasattr(w, '_bg'):
            w._bg.pos, w._bg.size = w.pos, w.size
    
    def run(self):
        threading.Thread(target=self._test, daemon=True).start()
    
    def _test(self):
        app = App.get_running_app()
        links = getattr(app, 'test_links', [])
        mode = getattr(app, 'test_mode', 'deep')
        total = len(links)
        
        for i, link in enumerate(links):
            if not self.testing:
                break
            
            domain = short_domain(link)
            Clock.schedule_once(lambda dt, d=domain: self.log(f'{I.LINK} {d}', 'testing'))
            
            if mode == 'quick':
                ok, msg = test_quick(link)
            else:
                ok, msg = test_deep(link)
            
            if ok:
                self.working.append(link)
                Clock.schedule_once(lambda dt, d=domain, m=msg: self.log(f'{I.CHECK} {d}: {m}', 'success'))
            else:
                self.failed.append({'link': link, 'reason': msg})
                Clock.schedule_once(lambda dt, d=domain, m=msg: self.log(f'{I.CROSS} {d}: {m}', 'error'))
            
            pct = ((i + 1) / total) * 100
            Clock.schedule_once(lambda dt, p=pct, c=i+1, t=total: self.upd_prog(p, c, t))
        
        db.update_stats(tested=len(links), working=len(self.working))
        Clock.schedule_once(lambda dt: self.done())
    
    def log(self, txt, typ):
        app = App.get_running_app()
        colors = {
            'testing': app.tc('t3'),
            'success': app.tc('ok'),
            'error': app.tc('err')
        }
        lbl = Label(text=txt, font_size=sp(8), color=colors.get(typ, app.tc('t3')),
            size_hint_y=None, height=dp(14), halign='left')
        lbl.bind(size=lambda w, s: setattr(w, 'text_size', s))
        self.log_box.add_widget(lbl)
        if len(self.log_box.children) > 30:
            self.log_box.remove_widget(self.log_box.children[-1])
    
    def upd_prog(self, pct, curr, total):
        self.prog_bar.set_value(pct)
        self.prog_lbl.text = f'Test: {curr}/{total}'
        self.pct_lbl.text = f'%{int(pct)}'
        self.stats_lbl.text = f'{I.CHECK} {len(self.working)}  |  {I.CROSS} {len(self.failed)}'
    
    def done(self):
        app = App.get_running_app()
        self.testing = False
        self.prog_lbl.text = 'Tamamlandi!'
        self.pct_lbl.text = '%100'
        self.act_btn.text = f'{I.NEXT} Devam'
        self.act_btn.background_color = app.tc('ok')
        app.working_links = self.working
        app.failed_links = self.failed
    
    def on_action(self, *args):
        if 'Iptal' in self.act_btn.text:
            self.testing = False
            self.manager.transition = SlideTransition(direction='right')
            self.manager.current = 'auto_input'
        elif not self.working:
            self.popup(I.WARN, 'Calisan link yok!')
        else:
            cleanup()
            self.manager.current = 'auto_result'
    
    def popup(self, icon, msg):
        app = App.get_running_app()
        c = BoxLayout(orientation='vertical', padding=dp(18), spacing=dp(10))
        c.add_widget(Label(text=icon, font_size=sp(28)))
        c.add_widget(Label(text=msg, font_size=sp(11), color=app.tc('t1')))
        btn = Button(text='Geri', size_hint=(0.5, None), height=dp(36),
            pos_hint={'center_x': 0.5}, background_normal='', background_color=app.tc('acc'))
        p = Popup(title='', content=c, size_hint=(0.68, 0.30), separator_height=0)
        def go(x):
            p.dismiss()
            self.manager.transition = SlideTransition(direction='right')
            self.manager.current = 'auto_input'
        btn.bind(on_press=go)
        c.add_widget(btn)
        p.open()


class AutoResultScreen(BaseScreen):
    def on_enter(self):
        self.clear_widgets()
        Clock.schedule_once(lambda dt: self.build(), 0.05)
    
    def build(self):
        app = App.get_running_app()
        w = len(getattr(app, 'working_links', []))
        f = len(getattr(app, 'failed_links', []))
        
        root = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(10))
        
        root.add_widget(Label(text=f'{I.CHECK} Test Tamamlandi!', font_size=sp(16), bold=True,
            color=app.tc('t1'), size_hint_y=None, height=dp(32)))
        
        # Results card
        res_card = BoxLayout(orientation='horizontal', padding=dp(16), spacing=dp(16),
            size_hint_y=None, height=dp(80))
        self._card_bg(res_card)
        
        for val, lbl, clr in [(w, 'Calisiyor', 'ok'), (f, 'Basarisiz', 'err')]:
            box = BoxLayout(orientation='vertical')
            box.add_widget(Label(text=str(val), font_size=sp(22), bold=True, color=app.tc(clr)))
            box.add_widget(Label(text=lbl, font_size=sp(9), color=app.tc('t3')))
            res_card.add_widget(box)
        root.add_widget(res_card)
        
        root.add_widget(Label(text='Nasil duzenlemek istersiniz?', font_size=sp(11),
            color=app.tc('t2'), size_hint_y=None, height=dp(22)))
        
        # Info about separate files
        root.add_widget(Label(text=f'{I.INFO} Her link ayri dosya olarak kaydedilir',
            font_size=sp(9), color=app.tc('info'), size_hint_y=None, height=dp(18)))
        
        # Options
        opts = BoxLayout(orientation='vertical', spacing=dp(8))
        
        options = [
            ('Otomatik', f'Ulke sec, {w} ayri dosya', f'{I.NEXT} Otomatik', 'acc', 'country_select'),
            ('Manuel', 'Her linki tek tek duzenle', f'{I.NEXT} Manuel', 'sec', 'manual_link_list'),
        ]
        
        for title, desc, btn_txt, color, screen in options:
            card = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(4),
                size_hint_y=None, height=dp(78))
            self._card_bg(card)
            card.add_widget(Label(text=title, font_size=sp(12), bold=True,
                color=app.tc('t1'), halign='left', size_hint_y=None, height=dp(20)))
            card.add_widget(Label(text=desc, font_size=sp(8), color=app.tc('t3'),
                size_hint_y=None, height=dp(14)))
            btn = Button(text=btn_txt, size_hint=(0.5, None), height=dp(32),
                pos_hint={'center_x': 0.5}, background_normal='', background_color=app.tc(color))
            btn.bind(on_press=lambda x, s=screen: setattr(self.manager, 'current', s))
            card.add_widget(btn)
            opts.add_widget(card)
        root.add_widget(opts)
        
        # Back button
        back = Button(text=f'{I.BACK} Geri', size_hint_y=None, height=dp(38),
            background_normal='', background_color=app.tc('card'))
        back.bind(on_press=lambda x: self.go_back())
        root.add_widget(back)
        
        self.add_widget(root)
    
    def _card_bg(self, w):
        with w.canvas.before:
            Color(*App.get_running_app().tc('card'))
            w._bg = RoundedRectangle(pos=w.pos, size=w.size, radius=[dp(8)])
        w.bind(pos=self._upd, size=self._upd)
    
    def _upd(self, w, v):
        if hasattr(w, '_bg'):
            w._bg.pos, w._bg.size = w.pos, w.size
    
    def go_back(self):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'auto_input'


class CountrySelectScreen(BaseScreen):
    def on_enter(self):
        self.clear_widgets()
        self.selected = set()
        self.fmt = db.get('format', 'm3u8')
        Clock.schedule_once(lambda dt: self.build(), 0.05)
    
    def build(self):
        app = App.get_running_app()
        num_links = len(getattr(app, 'working_links', []))
        
        root = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(6))
        
        # Top bar
        top = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(6))
        back = Button(text=I.BACK, size_hint=(None, None), size=(dp(42), dp(38)),
            font_size=sp(16), background_normal='', background_color=app.tc('card'))
        back.bind(on_press=lambda x: self.go_back())
        top.add_widget(back)
        top.add_widget(Label(text='Ulke Secimi', font_size=sp(13), bold=True, color=app.tc('t1')))
        root.add_widget(top)
        
        # Info
        root.add_widget(Label(text=f'{I.INFO} {num_links} link = {num_links} ayri dosya (IPTV klasorune)',
            font_size=sp(8), color=app.tc('info'), size_hint_y=None, height=dp(16)))
        
        self.sel_lbl = Label(text='Secilen: 0 ulke', font_size=sp(9),
            color=app.tc('ok'), size_hint_y=None, height=dp(16))
        root.add_widget(self.sel_lbl)
        
        # Country grid
        scroll = ScrollView()
        grid = GridLayout(cols=2, spacing=dp(4), size_hint_y=None, padding=dp(2))
        grid.bind(minimum_height=grid.setter('height'))
        
        self.btns = {}
        
        # Priority countries first
        for cid in PRIORITY_COUNTRIES:
            cd = COUNTRIES[cid]
            btn = ToggleButton(text=cd['name'], size_hint_y=None, height=dp(42),
                font_size=sp(10), background_normal='', background_color=app.tc('warn'))
            btn.cid = cid
            btn.pri = True
            btn.bind(on_press=self.on_toggle)
            self.btns[cid] = btn
            grid.add_widget(btn)
        
        # Other countries
        for cid, cd in sorted(COUNTRIES.items(), key=lambda x: x[1]['p']):
            if cid not in PRIORITY_COUNTRIES:
                btn = ToggleButton(text=cd['name'], size_hint_y=None, height=dp(42),
                    font_size=sp(10), background_normal='', background_color=app.tc('card'))
                btn.cid = cid
                btn.pri = False
                btn.bind(on_press=self.on_toggle)
                self.btns[cid] = btn
                grid.add_widget(btn)
        
        scroll.add_widget(grid)
        root.add_widget(scroll)
        
        # Format selection
        fmt_row = BoxLayout(size_hint_y=None, height=dp(38), spacing=dp(4))
        fmt_row.add_widget(Label(text='Format:', size_hint_x=None, width=dp(45),
            font_size=sp(9), color=app.tc('t3')))
        
        self.fmt_btns = {}
        for fid in ['m3u', 'm3u8', 'txt']:
            is_sel = fid == self.fmt
            btn = ToggleButton(text=fid.upper(), group='fmt2',
                state='down' if is_sel else 'normal', font_size=sp(9),
                background_normal='',
                background_color=app.tc('acc') if is_sel else app.tc('card2'))
            btn.fid = fid
            btn.bind(on_press=self.on_fmt)
            self.fmt_btns[fid] = btn
            fmt_row.add_widget(btn)
        root.add_widget(fmt_row)
        
        # Process button
        proc_btn = Button(text=f'{I.PLAY} Olustur', font_size=sp(12), bold=True,
            size_hint_y=None, height=dp(44), background_normal='', background_color=app.tc('ok'))
        proc_btn.bind(on_press=self.process)
        root.add_widget(proc_btn)
        
        self.add_widget(root)
    
    def on_toggle(self, btn):
        app = App.get_running_app()
        if btn.state == 'down':
            self.selected.add(btn.cid)
            btn.background_color = app.tc('ok')
        else:
            self.selected.discard(btn.cid)
            btn.background_color = app.tc('warn') if btn.pri else app.tc('card')
        self.sel_lbl.text = f'Secilen: {len(self.selected)} ulke'
    
    def on_fmt(self, btn):
        app = App.get_running_app()
        self.fmt = btn.fid
        for fid, b in self.fmt_btns.items():
            b.background_color = app.tc('acc') if fid == self.fmt else app.tc('card2')
    
    def process(self, *args):
        if not self.selected:
            return self.popup(I.WARN, 'Ulke secin!')
        
        app = App.get_running_app()
        app.sel_countries = self.selected
        app.out_fmt = self.fmt
        self.manager.current = 'processing'
    
    def popup(self, icon, msg):
        app = App.get_running_app()
        c = BoxLayout(orientation='vertical', padding=dp(18), spacing=dp(10))
        c.add_widget(Label(text=icon, font_size=sp(28)))
        c.add_widget(Label(text=msg, font_size=sp(11), color=app.tc('t1')))
        btn = Button(text='Tamam', size_hint=(0.5, None), height=dp(36),
            pos_hint={'center_x': 0.5}, background_normal='', background_color=app.tc('warn'))
        p = Popup(title='', content=c, size_hint=(0.68, 0.30), separator_height=0)
        btn.bind(on_press=p.dismiss)
        c.add_widget(btn)
        p.open()
    
    def go_back(self):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'auto_result'


class ProcessingScreen(BaseScreen):
    """
    Her link icin AYRI dosya olusturur
    Dosyalar IPTV klasorune kaydedilir
    """
    def on_enter(self):
        self.clear_widgets()
        self.files = []
        Clock.schedule_once(lambda dt: self.build(), 0.05)
        Clock.schedule_once(lambda dt: self.run(), 0.2)
    
    def build(self):
        app = App.get_running_app()
        root = BoxLayout(orientation='vertical', padding=dp(18), spacing=dp(10))
        
        root.add_widget(Label(text=f'{I.GEAR} Isleniyor...', font_size=sp(16), bold=True,
            color=app.tc('t1'), size_hint_y=None, height=dp(28)))
        
        self.status = Label(text='Baslatiliyor...', font_size=sp(10),
            color=app.tc('t3'), size_hint_y=None, height=dp(18))
        root.add_widget(self.status)
        
        self.prog = AnimProgress(size_hint_y=None, height=dp(18))
        root.add_widget(self.prog)
        
        self.pct = Label(text='%0', font_size=sp(18), bold=True,
            color=app.tc('acc'), size_hint_y=None, height=dp(26))
        root.add_widget(self.pct)
        
        # Stats card
        stats_card = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(4),
            size_hint_y=None, height=dp(95))
        self._card_bg(stats_card)
        
        self.curr_lbl = Label(text=f'{I.LINK} -', font_size=sp(9), color=app.tc('t3'))
        stats_card.add_widget(self.curr_lbl)
        
        self.total_lbl = Label(text=f'{I.TV} Toplam: 0 kanal', font_size=sp(10), color=app.tc('t2'))
        stats_card.add_widget(self.total_lbl)
        
        self.filt_lbl = Label(text=f'{I.CHECK} Filtrelenen: 0 kanal', font_size=sp(10), color=app.tc('ok'))
        stats_card.add_widget(self.filt_lbl)
        
        self.file_lbl = Label(text=f'{I.FILE} Dosyalar: 0', font_size=sp(9), color=app.tc('info'))
        stats_card.add_widget(self.file_lbl)
        
        root.add_widget(stats_card)
        root.add_widget(Widget())
        self.add_widget(root)
    
    def _card_bg(self, w):
        with w.canvas.before:
            Color(*App.get_running_app().tc('card'))
            w._bg = RoundedRectangle(pos=w.pos, size=w.size, radius=[dp(10)])
        w.bind(pos=self._upd, size=self._upd)
    
    def _upd(self, w, v):
        if hasattr(w, '_bg'):
            w._bg.pos, w._bg.size = w.pos, w.size
    
    def run(self):
        threading.Thread(target=self._proc, daemon=True).start()
    
    def _proc(self):
        app = App.get_running_app()
        links = getattr(app, 'working_links', [])
        countries = getattr(app, 'sel_countries', set())
        fmt = getattr(app, 'out_fmt', 'm3u8')
        
        total_links = len(links)
        total_ch = 0
        total_filt = 0
        
        # IPTV klasorune kaydet
        path = get_iptv_folder()
        ext = FORMATS.get(fmt, '.m3u8')
        
        for i, link in enumerate(links):
            domain = short_domain(link)
            Clock.schedule_once(lambda dt, d=domain: setattr(self.curr_lbl, 'text', f'{I.LINK} {d}'))
            Clock.schedule_once(lambda dt, p=((i + 0.3) / total_links) * 100: self._upd_prog(p))
            
            try:
                r = http.get(link, timeout=30)
                chs, grps, exp = parse_m3u(r.text, link)
                total_ch += len(chs)
                
                # Ulke filtreleme
                filt_chs = []
                for gn, gd in grps.items():
                    if gd.get('country', 'other') in countries:
                        filt_chs.extend(gd['channels'])
                
                total_filt += len(filt_chs)
                Clock.schedule_once(lambda dt, t=total_ch, f=total_filt: self._upd_stats(t, f))
                
                # HER LINK ICIN AYRI DOSYA
                if filt_chs:
                    content = gen_m3u(filt_chs)
                    
                    # Tarih belirleme
                    if exp and exp != 'Bilinmiyor' and 'DOLMUS' not in exp:
                        exp_str = exp.replace('.', '')
                    else:
                        exp_str = datetime.now().strftime('%d%m%Y')
                    
                    # Dosya adi: bitis{tarih}_{domain}.m3u8
                    fname = f'bitis{exp_str}_{domain}{ext}'
                    
                    with open(os.path.join(path, fname), 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    self.files.append({
                        'name': fname,
                        'count': len(filt_chs),
                        'expire': exp,
                        'domain': domain
                    })
                    Clock.schedule_once(lambda dt, c=len(self.files): 
                        setattr(self.file_lbl, 'text', f'{I.FILE} Dosyalar: {c}'))
            except Exception as e:
                log_error(f"Process error for {link}: {e}")
            
            Clock.schedule_once(lambda dt, p=((i + 1) / total_links) * 100: self._upd_prog(p))
            
            # Bellek temizligi
            if i % 3 == 0:
                cleanup()
        
        db.update_stats(channels=total_filt, files=len(self.files))
        app.saved_files = self.files
        app.total_filt = total_filt
        app.total_ch = total_ch
        Clock.schedule_once(lambda dt: self._upd_prog(100))
        Clock.schedule_once(lambda dt: self._done())
    
    def _upd_prog(self, p):
        self.prog.set_value(p)
        self.pct.text = f'%{int(p)}'
    
    def _upd_stats(self, t, f):
        self.total_lbl.text = f'{I.TV} Toplam: {t} kanal'
        self.filt_lbl.text = f'{I.CHECK} Filtrelenen: {f} kanal'
    
    def _done(self):
        cleanup()
        self.manager.current = 'complete'


class ManualLinkListScreen(BaseScreen):
    def on_enter(self):
        self.clear_widgets()
        Clock.schedule_once(lambda dt: self.build(), 0.05)
    
    def build(self):
        app = App.get_running_app()
        links = getattr(app, 'working_links', [])
        
        root = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(6))
        
        # Top bar
        top = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(6))
        back = Button(text=I.BACK, size_hint=(None, None), size=(dp(42), dp(38)),
            font_size=sp(16), background_normal='', background_color=app.tc('card'))
        back.bind(on_press=lambda x: self.go_back())
        top.add_widget(back)
        top.add_widget(Label(text=f'{I.EDIT} Manuel ({len(links)})', font_size=sp(13),
            bold=True, color=app.tc('t1')))
        root.add_widget(top)
        
        root.add_widget(Label(text='Tikla = duzenle, her link ayri dosya', font_size=sp(8),
            color=app.tc('t3'), size_hint_y=None, height=dp(14)))
        
        # Links list
        scroll = ScrollView()
        lst = BoxLayout(orientation='vertical', spacing=dp(6), size_hint_y=None)
        lst.bind(minimum_height=lst.setter('height'))
        
        for i, link in enumerate(links):
            item = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(55),
                padding=dp(8), spacing=dp(6))
            with item.canvas.before:
                Color(*app.tc('card'))
                item._bg = RoundedRectangle(pos=item.pos, size=item.size, radius=[dp(10)])
            item.bind(pos=self._upd_bg, size=self._upd_bg)
            
            item.add_widget(Label(text=str(i+1), font_size=sp(14), bold=True,
                color=app.tc('acc'), size_hint_x=None, width=dp(26)))
            
            info = BoxLayout(orientation='vertical', spacing=dp(1))
            info.add_widget(Label(text=short_domain(link), font_size=sp(11),
                color=app.tc('t1'), halign='left'))
            info.add_widget(Label(text=link[:28]+'...', font_size=sp(7),
                color=app.tc('t4'), halign='left'))
            item.add_widget(info)
            
            btn = Button(text=I.EDIT, size_hint=(None, None), size=(dp(40), dp(40)),
                font_size=sp(16), background_normal='', background_color=app.tc('acc'))
            btn.link = link
            btn.idx = i + 1
            btn.bind(on_press=self.edit)
            item.add_widget(btn)
            lst.add_widget(item)
        
        scroll.add_widget(lst)
        root.add_widget(scroll)
        self.add_widget(root)
    
    def _upd_bg(self, w, v):
        if hasattr(w, '_bg'):
            w._bg.pos, w._bg.size = w.pos, w.size
    
    def edit(self, btn):
        app = App.get_running_app()
        app.edit_link = btn.link
        app.edit_idx = btn.idx
        self.manager.current = 'link_editor'
    
    def go_back(self):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'auto_result'


class LinkEditorScreen(BaseScreen):
    def on_enter(self):
        self.clear_widgets()
        self.selected = set()
        self.groups = {}
        self.channels = []
        self.expire = 'Bilinmiyor'
        Clock.schedule_once(lambda dt: self.build(), 0.05)
        Clock.schedule_once(lambda dt: self.load(), 0.1)
    
    def build(self):
        app = App.get_running_app()
        idx = getattr(app, 'edit_idx', 1)
        total = len(getattr(app, 'working_links', []))
        
        root = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(5))
        
        # Top bar
        top = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(6))
        back = Button(text=I.BACK, size_hint=(None, None), size=(dp(42), dp(38)),
            font_size=sp(16), background_normal='', background_color=app.tc('card'))
        back.bind(on_press=lambda x: self.go_back())
        top.add_widget(back)
        top.add_widget(Label(text=f'Link {idx}/{total}', font_size=sp(12),
            bold=True, color=app.tc('t1')))
        root.add_widget(top)
        
        # Loading
        self.load_box = BoxLayout(orientation='vertical', spacing=dp(6))
        self.l_icon = Label(text=I.REFRESH, font_size=sp(28))
        self.load_box.add_widget(self.l_icon)
        self.l_msg = Label(text='Yukleniyor...', font_size=sp(10), color=app.tc('t3'))
        self.load_box.add_widget(self.l_msg)
        self.l_prog = AnimProgress(size_hint_y=None, height=dp(14))
        self.load_box.add_widget(self.l_prog)
        self.l_pct = Label(text='%0', font_size=sp(14), bold=True, color=app.tc('acc'))
        self.load_box.add_widget(self.l_pct)
        root.add_widget(self.load_box)
        
        # Content (hidden initially)
        self.content = BoxLayout(orientation='vertical', spacing=dp(5), opacity=0)
        self.exp_lbl = Label(text='', font_size=sp(8), color=app.tc('warn'),
            size_hint_y=None, height=dp(14))
        self.content.add_widget(self.exp_lbl)
        self.stats_lbl = Label(text='', font_size=sp(9), color=app.tc('t3'),
            size_hint_y=None, height=dp(16))
        self.content.add_widget(self.stats_lbl)
        self.sel_lbl = Label(text='Secilen: 0', font_size=sp(8), color=app.tc('ok'),
            size_hint_y=None, height=dp(14))
        self.content.add_widget(self.sel_lbl)
        
        self.rv = RV()
        self.rv_data = []
        self.content.add_widget(self.rv)
        root.add_widget(self.content)
        
        # Bottom buttons
        self.btm = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(6), opacity=0)
        save = Button(text=f'{I.SAVE} Kaydet', font_size=sp(11), bold=True,
            background_normal='', background_color=app.tc('ok'))
        save.bind(on_press=self.save)
        self.btm.add_widget(save)
        root.add_widget(self.btm)
        
        self.add_widget(root)
    
    def load(self):
        threading.Thread(target=self._load, daemon=True).start()
    
    def _load(self):
        app = App.get_running_app()
        link = getattr(app, 'edit_link', '')
        
        try:
            Clock.schedule_once(lambda dt: self._upd_load(10, 'Baglaniyor...'))
            r = http.get(link, timeout=30)
            Clock.schedule_once(lambda dt: self._upd_load(50, 'Ayristiriliyor...'))
            self.channels, self.groups, self.expire = parse_m3u(r.text, link)
            Clock.schedule_once(lambda dt: self._upd_load(100, 'Tamamlandi!'))
            Clock.schedule_once(lambda dt: self._show(), 0.2)
        except Exception as e:
            Clock.schedule_once(lambda dt: self._err(str(e)[:20]))
    
    def _upd_load(self, pct, msg):
        self.l_prog.set_value(pct)
        self.l_pct.text = f'%{int(pct)}'
        self.l_msg.text = msg
    
    def _show(self):
        self.load_box.opacity = 0
        self.load_box.size_hint_y = 0.001
        self.content.opacity = 1
        self.btm.opacity = 1
        
        # Expire color
        app = App.get_running_app()
        exp_color = app.tc('err') if 'DOLMUS' in self.expire else app.tc('warn')
        self.exp_lbl.text = f'Bitis: {self.expire}'
        self.exp_lbl.color = exp_color
        
        self.stats_lbl.text = f'{len(self.groups)} grup | {len(self.channels)} kanal'
        
        self.rv_data = []
        for gn, gd in sorted(self.groups.items()):
            self.rv_data.append({
                'grp_name': gn,
                'ch_count': len(gd['channels']),
                'country': gd.get('country', 'other'),
                'is_selected': False,
                'callback': self.on_sel
            })
        self.rv.data = self.rv_data
    
    def _err(self, msg):
        self.l_msg.text = f'{I.CROSS} Hata: {msg}'
        self.l_icon.text = I.CROSS
    
    def on_sel(self, gn, sel, idx):
        self.rv_data[idx]['is_selected'] = sel
        if sel:
            self.selected.add(gn)
        else:
            self.selected.discard(gn)
        total = sum(len(self.groups[g]['channels']) for g in self.selected if g in self.groups)
        self.sel_lbl.text = f'Secilen: {len(self.selected)} grup ({total} kanal)'
    
    def save(self, *args):
        app = App.get_running_app()
        if not self.selected:
            return self.popup(I.WARN, 'Grup secin!')
        
        channels = []
        for gn in self.selected:
            if gn in self.groups:
                channels.extend(self.groups[gn]['channels'])
        
        content = gen_m3u(channels)
        link = getattr(app, 'edit_link', '')
        path = get_iptv_folder()
        domain = short_domain(link)
        
        # Tarih
        if self.expire and self.expire != 'Bilinmiyor' and 'DOLMUS' not in self.expire:
            exp_str = self.expire.replace('.', '')
        else:
            exp_str = datetime.now().strftime('%d%m%Y')
        
        fname = f'bitis{exp_str}_{domain}.m3u8'
        
        try:
            with open(os.path.join(path, fname), 'w', encoding='utf-8') as f:
                f.write(content)
            db.update_stats(channels=len(channels), files=1)
            self.popup_success(fname, len(channels))
        except Exception as e:
            self.popup(I.CROSS, str(e)[:25])
        
        cleanup()
    
    def popup(self, icon, msg):
        app = App.get_running_app()
        c = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(8))
        c.add_widget(Label(text=icon, font_size=sp(28)))
        c.add_widget(Label(text=msg, font_size=sp(10), color=app.tc('t1')))
        btn = Button(text='Tamam', size_hint=(0.5, None), height=dp(34),
            pos_hint={'center_x': 0.5}, background_normal='', background_color=app.tc('warn'))
        p = Popup(title='', content=c, size_hint=(0.68, 0.28), separator_height=0)
        btn.bind(on_press=p.dismiss)
        c.add_widget(btn)
        p.open()
    
    def popup_success(self, fname, count):
        app = App.get_running_app()
        c = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(6))
        c.add_widget(Label(text=I.CHECK, font_size=sp(32)))
        c.add_widget(Label(text='Kaydedildi!', font_size=sp(12), bold=True, color=app.tc('t1')))
        c.add_widget(Label(text=f'{count} kanal\nIPTV/{fname}', font_size=sp(9),
            color=app.tc('t3'), halign='center'))
        btn = Button(text='Listeye Don', size_hint=(0.55, None), height=dp(34),
            pos_hint={'center_x': 0.5}, background_normal='', background_color=app.tc('acc'))
        p = Popup(title='', content=c, size_hint=(0.75, 0.36), separator_height=0)
        def go(x):
            p.dismiss()
            self.manager.transition = SlideTransition(direction='right')
            self.manager.current = 'manual_link_list'
        btn.bind(on_press=go)
        c.add_widget(btn)
        p.open()
    
    def go_back(self):
        cleanup()
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'manual_link_list'


class CompleteScreen(BaseScreen):
    def on_enter(self):
        self.clear_widgets()
        Clock.schedule_once(lambda dt: self.build(), 0.05)
    
    def build(self):
        app = App.get_running_app()
        files = getattr(app, 'saved_files', [])
        filt = getattr(app, 'total_filt', 0)
        total = getattr(app, 'total_ch', 0)
        
        root = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        
        # Icon
        icon = Label(text=I.CHECK, font_size=sp(48), size_hint_y=0.15)
        root.add_widget(icon)
        
        root.add_widget(Label(text='Tamamlandi!', font_size=sp(20), bold=True,
            color=app.tc('t1'), size_hint_y=None, height=dp(32)))
        
        # Results card
        res_card = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(6),
            size_hint_y=None, height=dp(100))
        self._card_bg(res_card)
        res_card.add_widget(Label(text=f'{filt} kanal filtrelendi', font_size=sp(12), color=app.tc('ok')))
        res_card.add_widget(Label(text=f'Toplam {total} kanaldan', font_size=sp(9), color=app.tc('t3')))
        res_card.add_widget(Label(text=f'{len(files)} dosya olusturuldu', font_size=sp(10), color=app.tc('info')))
        res_card.add_widget(Label(text=f'{I.FOLDER} IPTV klasorune kaydedildi', font_size=sp(8), color=app.tc('t4')))
        root.add_widget(res_card)
        
        # Files list
        if files:
            root.add_widget(Label(text='Dosyalar:', font_size=sp(10),
                color=app.tc('t3'), size_hint_y=None, height=dp(18)))
            
            scroll = ScrollView(size_hint_y=None, height=dp(70))
            fb = BoxLayout(orientation='vertical', spacing=dp(2), size_hint_y=None)
            fb.bind(minimum_height=fb.setter('height'))
            
            for f in files[:5]:
                exp_info = f" (Bitis: {f['expire']})" if f.get('expire') and f['expire'] != 'Bilinmiyor' else ''
                fb.add_widget(Label(text=f"{I.FILE} {f['name']} ({f['count']}){exp_info}",
                    font_size=sp(7), color=app.tc('t2'), size_hint_y=None, height=dp(13), halign='left'))
            
            if len(files) > 5:
                fb.add_widget(Label(text=f'... ve {len(files) - 5} dosya daha',
                    font_size=sp(7), color=app.tc('t4'), size_hint_y=None, height=dp(12)))
            
            scroll.add_widget(fb)
            root.add_widget(scroll)
        
        # Buttons
        btns = BoxLayout(orientation='vertical', spacing=dp(8), size_hint_y=None, height=dp(85))
        new_btn = Button(text=f'{I.REFRESH} Yeni Islem', font_size=sp(12), bold=True,
            size_hint_y=None, height=dp(38), background_normal='', background_color=app.tc('acc'))
        new_btn.bind(on_press=lambda x: self.goto('auto_input'))
        btns.add_widget(new_btn)
        
        home_btn = Button(text=f'{I.HOME} Ana Sayfa', font_size=sp(12), bold=True,
            size_hint_y=None, height=dp(38), background_normal='', background_color=app.tc('card'))
        home_btn.bind(on_press=lambda x: self.goto('welcome'))
        btns.add_widget(home_btn)
        root.add_widget(btns)
        
        self.add_widget(root)
    
    def _card_bg(self, w):
        with w.canvas.before:
            Color(*App.get_running_app().tc('card'))
            w._bg = RoundedRectangle(pos=w.pos, size=w.size, radius=[dp(8)])
        w.bind(pos=self._upd, size=self._upd)
    
    def _upd(self, w, v):
        if hasattr(w, '_bg'):
            w._bg.pos, w._bg.size = w.pos, w.size
    
    def goto(self, s):
        cleanup()
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = s


class FavoritesScreen(BaseScreen):
    def on_enter(self):
        self.clear_widgets()
        Clock.schedule_once(lambda dt: self.build(), 0.05)
    
    def build(self):
        app = App.get_running_app()
        favs = db.get_favs()
        
        root = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(6))
        
        # Top bar
        top = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(6))
        back = Button(text=I.BACK, size_hint=(None, None), size=(dp(42), dp(38)),
            font_size=sp(16), background_normal='', background_color=app.tc('card'))
        back.bind(on_press=lambda x: self.go_back())
        top.add_widget(back)
        top.add_widget(Label(text=f'{I.STAR} Favoriler', font_size=sp(14),
            bold=True, color=app.tc('t1')))
        root.add_widget(top)
        
        if not favs:
            # Empty state
            empty = BoxLayout(orientation='vertical', spacing=dp(10))
            empty.add_widget(Widget())
            empty.add_widget(Label(text=I.STAR_O, font_size=sp(40)))
            empty.add_widget(Label(text='Henuz favori yok', font_size=sp(12), color=app.tc('t3')))
            empty.add_widget(Label(text='Manuel duzenleme sirasinda\nyildiz butonu ile ekleyin',
                font_size=sp(9), color=app.tc('t4'), halign='center'))
            empty.add_widget(Widget())
            root.add_widget(empty)
        else:
            root.add_widget(Label(text=f'{len(favs)} kayitli link', font_size=sp(9),
                color=app.tc('t3'), size_hint_y=None, height=dp(16)))
            
            scroll = ScrollView()
            lst = BoxLayout(orientation='vertical', spacing=dp(6), size_hint_y=None)
            lst.bind(minimum_height=lst.setter('height'))
            
            for fav in favs:
                item = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(58),
                    padding=dp(8), spacing=dp(6))
                with item.canvas.before:
                    Color(*app.tc('card'))
                    item._bg = RoundedRectangle(pos=item.pos, size=item.size, radius=[dp(8)])
                item.bind(pos=self._upd_bg, size=self._upd_bg)
                
                item.add_widget(Label(text=I.STAR, font_size=sp(18),
                    size_hint_x=None, width=dp(28)))
                
                info = BoxLayout(orientation='vertical', spacing=dp(1))
                info.add_widget(Label(text=fav['name'][:20], font_size=sp(10),
                    color=app.tc('t1'), halign='left'))
                
                details = f"{fav.get('count', 0)} kanal"
                if fav.get('expire') and fav['expire'] != 'Bilinmiyor':
                    details += f" | Bitis: {fav['expire']}"
                info.add_widget(Label(text=details, font_size=sp(8),
                    color=app.tc('t3'), halign='left'))
                item.add_widget(info)
                
                btn_box = BoxLayout(orientation='vertical', size_hint_x=None, width=dp(42), spacing=dp(3))
                use_btn = Button(text=I.PLAY, size_hint=(None, None), size=(dp(36), dp(24)),
                    font_size=sp(12), background_normal='', background_color=app.tc('ok'))
                use_btn.url = fav['url']
                use_btn.bind(on_press=self.use_fav)
                btn_box.add_widget(use_btn)
                
                del_btn = Button(text=I.DELETE, size_hint=(None, None), size=(dp(36), dp(24)),
                    font_size=sp(12), background_normal='', background_color=app.tc('err'))
                del_btn.url = fav['url']
                del_btn.bind(on_press=self.del_fav)
                btn_box.add_widget(del_btn)
                item.add_widget(btn_box)
                lst.add_widget(item)
            
            scroll.add_widget(lst)
            root.add_widget(scroll)
        
        self.add_widget(root)
    
    def _upd_bg(self, w, v):
        if hasattr(w, '_bg'):
            w._bg.pos, w._bg.size = w.pos, w.size
    
    def use_fav(self, btn):
        self.manager.current = 'manual_input'
        Clock.schedule_once(lambda dt: self._fill(btn.url), 0.2)
    
    def _fill(self, url):
        s = self.manager.get_screen('manual_input')
        if hasattr(s, 'url_inp'):
            s.url_inp.text = url
    
    def del_fav(self, btn):
        db.del_fav(btn.url)
        self.on_enter()
    
    def go_back(self):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'welcome'


class SettingsScreen(BaseScreen):
    def on_enter(self):
        self.clear_widgets()
        Clock.schedule_once(lambda dt: self.build(), 0.05)
    
    def build(self):
        app = App.get_running_app()
        root = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(6))
        
        # Top bar
        top = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(6))
        back = Button(text=I.BACK, size_hint=(None, None), size=(dp(42), dp(38)),
            font_size=sp(16), background_normal='', background_color=app.tc('card'))
        back.bind(on_press=lambda x: self.go_back())
        top.add_widget(back)
        top.add_widget(Label(text=f'{I.GEAR} Ayarlar', font_size=sp(14),
            bold=True, color=app.tc('t1')))
        root.add_widget(top)
        
        scroll = ScrollView()
        sl = BoxLayout(orientation='vertical', spacing=dp(8), size_hint_y=None)
        sl.bind(minimum_height=sl.setter('height'))
        
        # Theme section
        theme_card = self._section('Tema')
        theme_grid = GridLayout(cols=3, spacing=dp(4), size_hint_y=None, height=dp(38))
        cur = db.get('theme', 'dark')
        self.theme_btns = {}
        for tid, td in THEMES.items():
            is_sel = tid == cur
            btn = ToggleButton(text=td['name'], group='theme',
                state='down' if is_sel else 'normal', font_size=sp(9),
                size_hint_y=None, height=dp(34), background_normal='',
                background_color=app.tc('acc') if is_sel else app.tc('card2'))
            btn.tid = tid
            btn.bind(on_press=self.change_theme)
            self.theme_btns[tid] = btn
            theme_grid.add_widget(btn)
        theme_card.add_widget(theme_grid)
        sl.add_widget(theme_card)
        
        # Test settings
        test_card = self._section('Test Ayarlari')
        mode_row = BoxLayout(size_hint_y=None, height=dp(36), spacing=dp(4))
        mode_row.add_widget(Label(text='Mod:', font_size=sp(9), color=app.tc('t3'), size_hint_x=0.25))
        tm = db.get('test_mode', 'deep')
        self.mode_btns = {}
        for mid, mname in [('quick', 'Hizli'), ('deep', 'Derin')]:
            is_sel = mid == tm
            btn = ToggleButton(text=mname, group='tm',
                state='down' if is_sel else 'normal', font_size=sp(9),
                background_normal='',
                background_color=app.tc('acc') if is_sel else app.tc('card2'))
            btn.mid = mid
            btn.bind(on_press=self.change_mode)
            self.mode_btns[mid] = btn
            mode_row.add_widget(btn)
        test_card.add_widget(mode_row)
        
        timeout_row = BoxLayout(size_hint_y=None, height=dp(36), spacing=dp(4))
        timeout_row.add_widget(Label(text='Timeout:', font_size=sp(9), color=app.tc('t3'), size_hint_x=0.25))
        self.to_lbl = Label(text=db.get('timeout', '12'), font_size=sp(10), bold=True,
            color=app.tc('acc'), size_hint_x=0.12)
        timeout_row.add_widget(self.to_lbl)
        to_slider = Slider(min=5, max=30, value=int(db.get('timeout', '12')), step=1)
        to_slider.bind(value=self.change_timeout)
        timeout_row.add_widget(to_slider)
        test_card.add_widget(timeout_row)
        sl.add_widget(test_card)
        
        # File settings
        file_card = self._section('Dosya')
        fmt_row = BoxLayout(size_hint_y=None, height=dp(36), spacing=dp(4))
        fmt_row.add_widget(Label(text='Format:', font_size=sp(9), color=app.tc('t3'), size_hint_x=0.25))
        df = db.get('format', 'm3u8')
        self.fmt_btns = {}
        for fid in ['m3u', 'm3u8', 'txt']:
            is_sel = fid == df
            btn = ToggleButton(text=fid.upper(), group='df',
                state='down' if is_sel else 'normal', font_size=sp(9),
                background_normal='',
                background_color=app.tc('acc') if is_sel else app.tc('card2'))
            btn.fid = fid
            btn.bind(on_press=self.change_fmt)
            self.fmt_btns[fid] = btn
            fmt_row.add_widget(btn)
        file_card.add_widget(fmt_row)
        
        dup_row = BoxLayout(size_hint_y=None, height=dp(36), spacing=dp(4))
        dup_row.add_widget(Label(text='Duplicate Temizle:', font_size=sp(9), color=app.tc('t3')))
        dup_sw = Switch(active=db.get('auto_dup', 'true') == 'true')
        dup_sw.bind(active=lambda sw, a: db.set('auto_dup', 'true' if a else 'false'))
        dup_row.add_widget(dup_sw)
        file_card.add_widget(dup_row)
        
        # Save path info
        file_card.add_widget(Label(text=f'{I.FOLDER} Kayit: Download/IPTV/', font_size=sp(8),
            color=app.tc('info'), size_hint_y=None, height=dp(16)))
        sl.add_widget(file_card)
        
        # Data section
        data_card = self._section('Veri')
        cache_btn = Button(text=f'{I.DELETE} Onbellek Temizle', font_size=sp(10),
            size_hint_y=None, height=dp(34), background_normal='', background_color=app.tc('info'))
        cache_btn.bind(on_press=self.clear_cache)
        data_card.add_widget(cache_btn)
        sl.add_widget(data_card)
        
        # About section
        about_card = self._section('Hakkinda')
        about_card.add_widget(Label(text=f'{APP_NAME} v{APP_VERSION}', font_size=sp(10), bold=True,
            color=app.tc('t1'), size_hint_y=None, height=dp(20)))
        stats = db.get_total_stats()
        about_card.add_widget(Label(text=f"Toplam: {stats['tested']} test, {stats['files']} dosya",
            font_size=sp(8), color=app.tc('t3'), size_hint_y=None, height=dp(14)))
        sl.add_widget(about_card)
        
        sl.add_widget(Widget(size_hint_y=None, height=dp(12)))
        scroll.add_widget(sl)
        root.add_widget(scroll)
        self.add_widget(root)
    
    def _section(self, title):
        app = App.get_running_app()
        card = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(6), size_hint_y=None)
        card.bind(minimum_height=card.setter('height'))
        with card.canvas.before:
            Color(*app.tc('card'))
            card._bg = RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(8)])
        card.bind(pos=self._upd, size=self._upd)
        card.add_widget(Label(text=title, font_size=sp(10), bold=True,
            color=app.tc('t1'), size_hint_y=None, height=dp(18), halign='left'))
        return card
    
    def _upd(self, w, v):
        if hasattr(w, '_bg'):
            w._bg.pos, w._bg.size = w.pos, w.size
    
    def change_theme(self, btn):
        global current_theme
        app = App.get_running_app()
        current_theme = btn.tid
        db.set('theme', btn.tid)
        for tid, b in self.theme_btns.items():
            b.background_color = app.tc('acc') if tid == btn.tid else app.tc('card2')
        self.popup(I.INFO, f'Tema: {THEMES[btn.tid]["name"]}\n\nUygulama yeniden baslatildiginda aktif olacak')
    
    def change_mode(self, btn):
        app = App.get_running_app()
        db.set('test_mode', btn.mid)
        for mid, b in self.mode_btns.items():
            b.background_color = app.tc('acc') if mid == btn.mid else app.tc('card2')
    
    def change_timeout(self, slider, val):
        self.to_lbl.text = str(int(val))
        db.set('timeout', str(int(val)))
    
    def change_fmt(self, btn):
        app = App.get_running_app()
        db.set('format', btn.fid)
        for fid, b in self.fmt_btns.items():
            b.background_color = app.tc('acc') if fid == btn.fid else app.tc('card2')
    
    def clear_cache(self, *args):
        test_cache.clear()
        detect_country.cache_clear()
        cleanup()
        self.popup(I.CHECK, 'Onbellek temizlendi!')
    
    def popup(self, icon, msg):
        app = App.get_running_app()
        c = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(8))
        c.add_widget(Label(text=icon, font_size=sp(28)))
        c.add_widget(Label(text=msg, font_size=sp(10), color=app.tc('t1'), halign='center'))
        btn = Button(text='Tamam', size_hint=(0.5, None), height=dp(34),
            pos_hint={'center_x': 0.5}, background_normal='', background_color=app.tc('acc'))
        p = Popup(title='', content=c, size_hint=(0.72, 0.34), separator_height=0)
        btn.bind(on_press=p.dismiss)
        c.add_widget(btn)
        p.open()
    
    def go_back(self):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'welcome'


# ==================== MAIN APP ====================
class IPTVApp(App):
    def build(self):
        global current_theme
        current_theme = db.get('theme', 'dark')
        Window.clearcolor = self.tc('bg1')
        
        sm = ScreenManager(transition=SlideTransition())
        sm.add_widget(WelcomeScreen(name='welcome'))
        sm.add_widget(ManualInputScreen(name='manual_input'))
        sm.add_widget(ChannelListScreen(name='channel_list'))
        sm.add_widget(AutoInputScreen(name='auto_input'))
        sm.add_widget(TestingScreen(name='testing'))
        sm.add_widget(AutoResultScreen(name='auto_result'))
        sm.add_widget(CountrySelectScreen(name='country_select'))
        sm.add_widget(ProcessingScreen(name='processing'))
        sm.add_widget(ManualLinkListScreen(name='manual_link_list'))
        sm.add_widget(LinkEditorScreen(name='link_editor'))
        sm.add_widget(CompleteScreen(name='complete'))
        sm.add_widget(FavoritesScreen(name='favorites'))
        sm.add_widget(SettingsScreen(name='settings'))
        return sm
    
    def tc(self, key):
        try:
            return get_color_from_hex(T(key))
        except:
            return [1, 1, 1, 1]
    
    def on_stop(self):
        db.close()
        cleanup()


if __name__ == '__main__':
    IPTVApp().run()
