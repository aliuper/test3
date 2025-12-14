"""
IPTV Editor Pro v6.0
Full Featured - Optimized - Animated
"""

import os
import sys
import re
import gc
import traceback
import threading
import weakref
from datetime import datetime
from urllib.parse import urlparse, parse_qs
from functools import lru_cache

# ==================== HATA YAKALAMA ====================
def setup_error_handler():
    def handler(exc_type, exc_value, exc_tb):
        msg = ''.join(traceback.format_exception(exc_type, exc_value, exc_tb))
        try:
            from android.storage import primary_external_storage_path
            p = os.path.join(primary_external_storage_path(), 'Download', 'iptv_error.txt')
        except:
            p = '/sdcard/Download/iptv_error.txt'
        try:
            open(p, 'w').write(msg)
        except:
            pass
    sys.excepthook = handler

setup_error_handler()

# ==================== KIVY CONFIG ====================
from kivy.config import Config
Config.set('graphics', 'multisamples', '0')
Config.set('kivy', 'log_level', 'warning')

# ==================== KIVY IMPORTS ====================
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
from kivy.uix.progressbar import ProgressBar
from kivy.uix.spinner import Spinner
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.properties import StringProperty, BooleanProperty, NumericProperty, ListProperty, ObjectProperty
from kivy.utils import get_color_from_hex
from kivy.animation import Animation
from kivy.graphics import Color, Rectangle, RoundedRectangle, Line

import requests

# ==================== UNICODE ICONS ====================
# Android uyumlu unicode ikonlar
ICONS = {
    'home': '\u2302',           # ⌂
    'back': '\u25C0',           # ◀
    'forward': '\u25B6',        # ▶
    'up': '\u25B2',             # ▲
    'down': '\u25BC',           # ▼
    'check': '\u2713',          # ✓
    'cross': '\u2717',          # ✗
    'plus': '\u002B',           # +
    'minus': '\u2212',          # −
    'star': '\u2605',           # ★
    'star_empty': '\u2606',     # ☆
    'circle': '\u25CF',         # ●
    'circle_empty': '\u25CB',   # ○
    'square': '\u25A0',         # ■
    'square_empty': '\u25A1',   # □
    'triangle': '\u25B2',       # ▲
    'heart': '\u2665',          # ♥
    'diamond': '\u2666',        # ♦
    'club': '\u2663',           # ♣
    'spade': '\u2660',          # ♠
    'music': '\u266B',          # ♫
    'note': '\u266A',           # ♪
    'sun': '\u263C',            # ☼
    'cloud': '\u2601',          # ☁
    'umbrella': '\u2602',       # ☂
    'snow': '\u2744',           # ❄
    'lightning': '\u26A1',      # ⚡
    'fire': '\u2739',           # ✹
    'water': '\u2248',          # ≈
    'earth': '\u2295',          # ⊕
    'phone': '\u260E',          # ☎
    'mail': '\u2709',           # ✉
    'gear': '\u2699',           # ⚙
    'wrench': '\u2692',         # ⚒
    'hammer': '\u2692',         # ⚒
    'key': '\u26BF',            # ⚿
    'lock': '\u26BF',           # ⚿
    'unlock': '\u26BF',         # ⚿
    'flag': '\u2691',           # ⚑
    'pin': '\u2316',            # ⌖
    'target': '\u25CE',         # ◎
    'reload': '\u21BB',         # ↻
    'sync': '\u21C4',           # ⇄
    'download': '\u2193',       # ↓
    'upload': '\u2191',         # ↑
    'link': '\u26AD',           # ⚭
    'unlink': '\u26AF',         # ⚯
    'edit': '\u270E',           # ✎
    'delete': '\u2716',         # ✖
    'save': '\u2714',           # ✔
    'cancel': '\u2718',         # ✘
    'search': '\u2315',         # ⌕
    'filter': '\u29D6',         # ⧖
    'sort': '\u21C5',           # ⇅
    'list': '\u2630',           # ☰
    'grid': '\u2637',           # ☷
    'play': '\u25B6',           # ▶
    'pause': '\u23F8',          # ⏸
    'stop': '\u25A0',           # ■
    'record': '\u25CF',         # ●
    'prev': '\u23EE',           # ⏮
    'next': '\u23ED',           # ⏭
    'rewind': '\u23EA',         # ⏪
    'fastfwd': '\u23E9',        # ⏩
    'volume': '\u266B',         # ♫
    'mute': '\u266A',           # ♪
    'tv': '\u25A3',             # ▣
    'signal': '\u2637',         # ☷
    'wifi': '\u2630',           # ☰
    'bluetooth': '\u2630',      # ☰
    'battery': '\u25AE',        # ▮
    'power': '\u2B58',          # ⭘
    'time': '\u29D7',           # ⧗
    'calendar': '\u25A6',       # ▦
    'user': '\u2302',           # ⌂
    'users': '\u2302',          # ⌂
    'folder': '\u25A1',         # □
    'file': '\u25A0',           # ■
    'copy': '\u2750',           # ❐
    'paste': '\u2398',          # ⎘
    'cut': '\u2702',            # ✂
    'trash': '\u2716',          # ✖
    'warning': '\u26A0',        # ⚠
    'error': '\u2716',          # ✖
    'info': '\u2139',           # ℹ
    'help': '\u003F',           # ?
    'success': '\u2714',        # ✔
    'loading': '\u29D6',        # ⧖
    'refresh': '\u21BB',        # ↻
    'export': '\u2197',         # ↗
    'import': '\u2199',         # ↙
    'settings': '\u2699',       # ⚙
    'menu': '\u2630',           # ☰
    'more': '\u2026',           # …
    'dots_v': '\u22EE',         # ⋮
    'dots_h': '\u22EF',         # ⋯
    'arrow_r': '\u2192',        # →
    'arrow_l': '\u2190',        # ←
    'arrow_u': '\u2191',        # ↑
    'arrow_d': '\u2193',        # ↓
    'double_r': '\u00BB',       # »
    'double_l': '\u00AB',       # «
}

# Ülke bayrakları (ASCII)
COUNTRY_FLAGS = {
    'turkey': '[TR]',
    'germany': '[DE]',
    'romania': '[RO]',
    'austria': '[AT]',
    'france': '[FR]',
    'italy': '[IT]',
    'spain': '[ES]',
    'uk': '[UK]',
    'usa': '[US]',
    'netherlands': '[NL]',
    'poland': '[PL]',
    'russia': '[RU]',
    'arabic': '[AR]',
    'india': '[IN]',
    'portugal': '[PT]',
    'greece': '[GR]',
    'albania': '[AL]',
    'serbia': '[RS]',
    'croatia': '[HR]',
    'bulgaria': '[BG]',
    'other': '[??]',
}

# ==================== RENKLER ====================
COLORS = {
    'bg_dark': '#0d1b2a',
    'bg_medium': '#1b263b',
    'bg_card': '#22334a',
    'bg_card_light': '#2d3f58',
    'primary': '#7b68ee',
    'primary_dark': '#6354c9',
    'primary_light': '#9d8df7',
    'secondary': '#ff6b9d',
    'secondary_dark': '#e55a8a',
    'success': '#4ade80',
    'success_dark': '#22c55e',
    'warning': '#fbbf24',
    'warning_dark': '#f59e0b',
    'danger': '#f87171',
    'danger_dark': '#ef4444',
    'info': '#60a5fa',
    'text_white': '#ffffff',
    'text_light': '#e2e8f0',
    'text_gray': '#94a3b8',
    'text_dark': '#64748b',
    'border': '#334155',
    'shadow': '#000000',
    'overlay': '#00000088',
    'gradient_start': '#7b68ee',
    'gradient_end': '#ff6b9d',
}

# ==================== ÜLKE VERİLERİ ====================
COUNTRIES = {
    'turkey': {
        'name': 'Turkiye',
        'flag': '[TR]',
        'codes': ['tr', 'tur', 'turkey', 'turkiye', 'turk', 'turkish'],
        'priority': 1
    },
    'germany': {
        'name': 'Almanya',
        'flag': '[DE]',
        'codes': ['de', 'ger', 'deu', 'germany', 'deutsch', 'german', 'almanya'],
        'priority': 2
    },
    'romania': {
        'name': 'Romanya',
        'flag': '[RO]',
        'codes': ['ro', 'rom', 'rou', 'romania', 'romanian', 'romanya'],
        'priority': 3
    },
    'austria': {
        'name': 'Avusturya',
        'flag': '[AT]',
        'codes': ['at', 'aut', 'austria', 'austrian', 'avusturya'],
        'priority': 4
    },
    'france': {
        'name': 'Fransa',
        'flag': '[FR]',
        'codes': ['fr', 'fra', 'france', 'french', 'fransa'],
        'priority': 5
    },
    'italy': {
        'name': 'Italya',
        'flag': '[IT]',
        'codes': ['it', 'ita', 'italy', 'italian', 'italya'],
        'priority': 6
    },
    'spain': {
        'name': 'Ispanya',
        'flag': '[ES]',
        'codes': ['es', 'esp', 'spain', 'spanish', 'ispanya'],
        'priority': 7
    },
    'uk': {
        'name': 'Ingiltere',
        'flag': '[UK]',
        'codes': ['uk', 'gb', 'gbr', 'england', 'british', 'ingiltere'],
        'priority': 8
    },
    'usa': {
        'name': 'Amerika',
        'flag': '[US]',
        'codes': ['us', 'usa', 'america', 'american', 'amerika'],
        'priority': 9
    },
    'netherlands': {
        'name': 'Hollanda',
        'flag': '[NL]',
        'codes': ['nl', 'nld', 'netherlands', 'dutch', 'holland', 'hollanda'],
        'priority': 10
    },
    'poland': {
        'name': 'Polonya',
        'flag': '[PL]',
        'codes': ['pl', 'pol', 'poland', 'polish', 'polonya'],
        'priority': 11
    },
    'russia': {
        'name': 'Rusya',
        'flag': '[RU]',
        'codes': ['ru', 'rus', 'russia', 'russian', 'rusya'],
        'priority': 12
    },
    'arabic': {
        'name': 'Arapca',
        'flag': '[AR]',
        'codes': ['ar', 'ara', 'arabic', 'arab', 'arap'],
        'priority': 13
    },
    'india': {
        'name': 'Hindistan',
        'flag': '[IN]',
        'codes': ['in', 'ind', 'india', 'indian', 'hindi', 'hindistan'],
        'priority': 14
    },
    'portugal': {
        'name': 'Portekiz',
        'flag': '[PT]',
        'codes': ['pt', 'por', 'portugal', 'portuguese', 'brasil', 'portekiz'],
        'priority': 15
    },
    'greece': {
        'name': 'Yunanistan',
        'flag': '[GR]',
        'codes': ['gr', 'gre', 'greece', 'greek', 'yunanistan'],
        'priority': 16
    },
    'albania': {
        'name': 'Arnavutluk',
        'flag': '[AL]',
        'codes': ['al', 'alb', 'albania', 'albanian', 'arnavut'],
        'priority': 17
    },
    'serbia': {
        'name': 'Sirbistan',
        'flag': '[RS]',
        'codes': ['rs', 'srb', 'serbia', 'serbian', 'sirbistan'],
        'priority': 18
    },
    'croatia': {
        'name': 'Hirvatistan',
        'flag': '[HR]',
        'codes': ['hr', 'hrv', 'croatia', 'croatian', 'hirvatistan'],
        'priority': 19
    },
    'bulgaria': {
        'name': 'Bulgaristan',
        'flag': '[BG]',
        'codes': ['bg', 'bgr', 'bulgaria', 'bulgarian', 'bulgaristan'],
        'priority': 20
    },
    'other': {
        'name': 'Diger',
        'flag': '[??]',
        'codes': ['other', 'misc', 'mixed', 'international', 'world', 'diger'],
        'priority': 99
    }
}

PRIORITY_COUNTRIES = ['turkey', 'germany', 'romania', 'austria']

FILE_FORMATS = {
    'm3u': {'name': 'M3U', 'desc': 'Standart', 'ext': '.m3u'},
    'm3u8': {'name': 'M3U8', 'desc': 'En Iyi', 'ext': '.m3u8'},
    'txt': {'name': 'TXT', 'desc': 'Basit', 'ext': '.txt'},
}

# ==================== KV TASARIM ====================
KV_DESIGN = '''
#:import dp kivy.metrics.dp
#:import Animation kivy.animation.Animation
#:import get_color_from_hex kivy.utils.get_color_from_hex

# ===== RENKLER =====
#:set BG_DARK '#0d1b2a'
#:set BG_MEDIUM '#1b263b'
#:set BG_CARD '#22334a'
#:set PRIMARY '#7b68ee'
#:set SECONDARY '#ff6b9d'
#:set SUCCESS '#4ade80'
#:set WARNING '#fbbf24'
#:set DANGER '#f87171'
#:set TEXT_WHITE '#ffffff'
#:set TEXT_GRAY '#94a3b8'

# ===== TEMEL EKRAN =====
<BaseScreen>:
    canvas.before:
        Color:
            rgba: get_color_from_hex(BG_DARK)
        Rectangle:
            pos: self.pos
            size: self.size

# ===== ANİMASYONLU PROGRESS BAR =====
<AnimatedProgressBar>:
    canvas:
        Color:
            rgba: get_color_from_hex('#1e293b')
        RoundedRectangle:
            pos: self.x, self.center_y - dp(6)
            size: self.width, dp(12)
            radius: [dp(6)]
        Color:
            rgba: get_color_from_hex(PRIMARY)
        RoundedRectangle:
            pos: self.x + dp(2), self.center_y - dp(4)
            size: (self.width - dp(4)) * self.value / self.max, dp(8)
            radius: [dp(4)]

# ===== RECYCLEVIEW =====
<RV>:
    viewclass: 'GroupItem'
    RecycleBoxLayout:
        default_size: None, dp(72)
        default_size_hint: 1, None
        size_hint_y: None
        height: self.minimum_height
        orientation: 'vertical'
        spacing: dp(8)

<GroupItem>:
    orientation: 'horizontal'
    size_hint_y: None
    height: dp(72)
    padding: [dp(12), dp(8)]
    spacing: dp(12)
    selected: False
    group_name: ''
    channel_count: 0
    
    canvas.before:
        Color:
            rgba: get_color_from_hex(SUCCESS) if self.selected else get_color_from_hex(BG_CARD)
            a: 0.3 if self.selected else 1
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(10)]
    
    Label:
        text: root.icon_text
        font_size: dp(24)
        size_hint_x: None
        width: dp(45)
        color: get_color_from_hex(PRIMARY)
    
    BoxLayout:
        orientation: 'vertical'
        spacing: dp(2)
        Label:
            text: root.display_name
            font_size: dp(14)
            color: get_color_from_hex(TEXT_WHITE)
            text_size: self.size
            halign: 'left'
            valign: 'middle'
            shorten: True
            shorten_from: 'right'
        Label:
            text: str(root.channel_count) + ' kanal'
            font_size: dp(11)
            color: get_color_from_hex(TEXT_GRAY)
            text_size: self.size
            halign: 'left'
            valign: 'middle'
    
    Button:
        size_hint: None, None
        size: dp(44), dp(44)
        text: root.btn_text
        font_size: dp(18)
        background_normal: ''
        background_color: get_color_from_hex(SUCCESS) if root.selected else get_color_from_hex(PRIMARY)
        on_press: root.toggle_selection()
'''

Builder.load_string(KV_DESIGN)

# ==================== YARDIMCI FONKSİYONLAR ====================

def get_download_path():
    """Android Download klasoru"""
    try:
        from android.storage import primary_external_storage_path
        return os.path.join(primary_external_storage_path(), 'Download')
    except:
        return os.path.expanduser('~')


def extract_expire_date(content, url=''):
    """IPTV iceriginden veya URL'den bitis tarihini cikar"""
    expire_date = None
    expire_str = 'Bilinmiyor'
    
    # URL'den exp parametresi
    try:
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        if 'exp' in params:
            exp_ts = int(params['exp'][0])
            expire_date = datetime.fromtimestamp(exp_ts)
            expire_str = expire_date.strftime('%d.%m.%Y')
            return expire_str
    except:
        pass
    
    # İçerikten expire bilgisi
    patterns = [
        r'[Ee]xp(?:ire[sd]?)?[:\s=]+(\d{1,2}[./]\d{1,2}[./]\d{2,4})',
        r'[Bb]itis[:\s=]+(\d{1,2}[./]\d{1,2}[./]\d{2,4})',
        r'[Vv]alid[:\s=]+(\d{1,2}[./]\d{1,2}[./]\d{2,4})',
        r'(\d{1,2}[./]\d{1,2}[./]\d{4})\s*[Ee]xp',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, content[:2000])
        if match:
            date_str = match.group(1)
            try:
                for fmt in ['%d.%m.%Y', '%d/%m/%Y', '%m/%d/%Y', '%d.%m.%y', '%d/%m/%y']:
                    try:
                        expire_date = datetime.strptime(date_str, fmt)
                        if expire_date.year < 100:
                            expire_date = expire_date.replace(year=expire_date.year + 2000)
                        expire_str = expire_date.strftime('%d.%m.%Y')
                        return expire_str
                    except:
                        continue
            except:
                pass
    
    # Timestamp kontrolü
    ts_match = re.search(r'[Ee]xp(?:ire)?[:\s=]+(\d{10,13})', content[:2000])
    if ts_match:
        try:
            ts = int(ts_match.group(1))
            if ts > 1e12:
                ts = ts / 1000
            expire_date = datetime.fromtimestamp(ts)
            expire_str = expire_date.strftime('%d.%m.%Y')
            return expire_str
        except:
            pass
    
    return expire_str


def parse_m3u_optimized(content, url=''):
    """Optimize edilmis M3U parser"""
    channels = []
    groups = {}
    expire_date = extract_expire_date(content, url)
    
    lines = content.split('\n')
    current_channel = None
    
    # Regex pattern'leri onceden derle
    group_pattern = re.compile(r'group-title="([^"]*)"')
    logo_pattern = re.compile(r'tvg-logo="([^"]*)"')
    tvg_id_pattern = re.compile(r'tvg-id="([^"]*)"')
    name_pattern = re.compile(r',(.+)$')
    
    for line in lines:
        line = line.strip()
        
        if line.startswith('#EXTINF:'):
            current_channel = {
                'name': '',
                'group': 'Diger',
                'logo': '',
                'tvg_id': '',
                'url': ''
            }
            
            # Group title
            match = group_pattern.search(line)
            if match and match.group(1):
                current_channel['group'] = match.group(1).strip()
            
            # Logo
            match = logo_pattern.search(line)
            if match:
                current_channel['logo'] = match.group(1)
            
            # TVG-ID
            match = tvg_id_pattern.search(line)
            if match:
                current_channel['tvg_id'] = match.group(1)
            
            # Channel name
            match = name_pattern.search(line)
            if match:
                current_channel['name'] = match.group(1).strip()
                
        elif current_channel and (line.startswith('http') or line.startswith('rtmp') or line.startswith('rtsp')):
            current_channel['url'] = line
            channels.append(current_channel)
            
            group_name = current_channel['group']
            if group_name not in groups:
                groups[group_name] = {
                    'channels': [],
                    'logo': current_channel['logo'],
                    'country': None
                }
            groups[group_name]['channels'].append(current_channel)
            current_channel = None
    
    # Grup ulkelerini tespit et
    for group_name in groups:
        groups[group_name]['country'] = detect_country_from_group(group_name)
    
    return channels, groups, expire_date


@lru_cache(maxsize=256)
def detect_country_from_group(group_name):
    """Grup adindan ulke tespit et (cache'li)"""
    if not group_name:
        return 'other'
    
    group_lower = group_name.lower()
    
    # Grup adının başındaki ülke kodunu kontrol et
    for country_id, country_data in COUNTRIES.items():
        for code in country_data['codes']:
            # Başında kontrol
            if group_lower.startswith(code + ' ') or group_lower.startswith(code + '-') or group_lower.startswith(code + '_') or group_lower.startswith(code + ':') or group_lower.startswith(code + '|'):
                return country_id
            # Sonda kontrol
            if group_lower.endswith(' ' + code) or group_lower.endswith('-' + code) or group_lower.endswith('_' + code):
                return country_id
            # Tam eşleşme
            if group_lower == code:
                return country_id
            # İçinde geçiyor mu (word boundary ile)
            if re.search(rf'\b{re.escape(code)}\b', group_lower):
                return country_id
    
    return 'other'


def generate_m3u(channels, format_type='m3u'):
    """M3U icerik olustur"""
    content = '#EXTM3U\n'
    
    for ch in channels:
        extinf = '#EXTINF:-1'
        
        if ch.get('tvg_id'):
            extinf += f' tvg-id="{ch["tvg_id"]}"'
        if ch.get('logo'):
            extinf += f' tvg-logo="{ch["logo"]}"'
        if ch.get('group'):
            extinf += f' group-title="{ch["group"]}"'
        
        extinf += f',{ch.get("name", "Unknown")}\n'
        content += extinf
        content += f'{ch.get("url", "")}\n'
    
    return content


def test_link_fast(url, timeout=6):
    """Hizli link testi"""
    try:
        headers = {'User-Agent': 'VLC/3.0.11 LibVLC/3.0.11'}
        response = requests.head(url, timeout=timeout, headers=headers, allow_redirects=True)
        return response.status_code == 200, "Basarili"
    except requests.exceptions.Timeout:
        return False, "Zaman asimi"
    except requests.exceptions.ConnectionError:
        return False, "Baglanti hatasi"
    except Exception as e:
        return False, str(e)[:20]


def test_link_deep(url, timeout=12):
    """Derin link testi - video akisi kontrol"""
    try:
        headers = {'User-Agent': 'VLC/3.0.11 LibVLC/3.0.11'}
        response = requests.get(url, timeout=timeout, headers=headers, stream=True)
        
        if response.status_code != 200:
            return False, f"HTTP {response.status_code}"
        
        total_bytes = 0
        for chunk in response.iter_content(chunk_size=8192):
            total_bytes += len(chunk)
            if total_bytes > 32768:
                break
        
        if total_bytes > 2048:
            return True, f"Aktif ({total_bytes//1024}KB)"
        else:
            return False, "Veri yok"
            
    except requests.exceptions.Timeout:
        return False, "Zaman asimi"
    except requests.exceptions.ConnectionError:
        return False, "Baglanti hatasi"
    except Exception as e:
        return False, str(e)[:20]


def get_short_domain(url):
    """URL'den kisa domain al"""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc
        if domain.startswith('www.'):
            domain = domain[4:]
        parts = domain.split('.')
        if len(parts) > 2:
            domain = '.'.join(parts[-2:])
        return domain[:20]
    except:
        return url[:20]


def cleanup_memory():
    """Bellek temizligi"""
    gc.collect()


# ==================== CUSTOM WIDGETS ====================

class BaseScreen(Screen):
    """Temel ekran sinifi"""
    pass


class AnimatedProgressBar(Widget):
    """Animasyonlu ilerleme cubugu"""
    value = NumericProperty(0)
    max = NumericProperty(100)
    
    def set_progress(self, value, animate=True):
        if animate:
            anim = Animation(value=value, duration=0.3, t='out_quad')
            anim.start(self)
        else:
            self.value = value


class GroupItem(RecycleDataViewBehavior, BoxLayout):
    """RecycleView icin grup itemi"""
    index = None
    selected = BooleanProperty(False)
    group_name = StringProperty('')
    channel_count = NumericProperty(0)
    icon_text = StringProperty(ICONS['tv'])
    display_name = StringProperty('')
    btn_text = StringProperty('+')
    callback = ObjectProperty(None)
    
    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        self.group_name = data.get('group_name', '')
        self.channel_count = data.get('channel_count', 0)
        self.selected = data.get('selected', False)
        self.callback = data.get('callback', None)
        
        # Display name
        name = self.group_name
        if len(name) > 28:
            name = name[:25] + '...'
        self.display_name = name
        
        # Button text
        self.btn_text = ICONS['check'] if self.selected else '+'
        
        return super().refresh_view_attrs(rv, index, data)
    
    def toggle_selection(self):
        self.selected = not self.selected
        self.btn_text = ICONS['check'] if self.selected else '+'
        
        if self.callback:
            self.callback(self.group_name, self.selected, self.index)


class RV(RecycleView):
    """Optimize edilmis RecycleView"""
    pass


# ==================== EKRANLAR ====================

class WelcomeScreen(BaseScreen):
    """Ana ekran"""
    
    def on_enter(self):
        self.clear_widgets()
        Clock.schedule_once(lambda dt: self.build_ui(), 0.05)
    
    def build_ui(self):
        root = BoxLayout(orientation='vertical', padding=dp(25), spacing=dp(20))
        
        # Header
        header = BoxLayout(orientation='vertical', size_hint_y=0.32, spacing=dp(8))
        
        # Logo/Icon
        logo_box = BoxLayout(size_hint_y=None, height=dp(80))
        logo = Label(
            text=f'{ICONS["tv"]} {ICONS["signal"]}',
            font_size=dp(50),
            color=get_color_from_hex(COLORS['primary'])
        )
        logo_box.add_widget(logo)
        header.add_widget(logo_box)
        
        # Title
        title = Label(
            text='IPTV Editor Pro',
            font_size=dp(28),
            bold=True,
            color=get_color_from_hex(COLORS['text_white']),
            size_hint_y=None,
            height=dp(40)
        )
        header.add_widget(title)
        
        # Subtitle
        subtitle = Label(
            text='Gelismis IPTV Duzenleyici',
            font_size=dp(14),
            color=get_color_from_hex(COLORS['text_gray']),
            size_hint_y=None,
            height=dp(25)
        )
        header.add_widget(subtitle)
        
        root.add_widget(header)
        
        # Cards
        cards = BoxLayout(orientation='vertical', spacing=dp(15), size_hint_y=0.55)
        
        # Manual Card
        manual_card = self.create_card(
            icon=ICONS['edit'],
            title='Manuel Duzenleme',
            desc='IPTV URL girin, kanallari gorun\nistediginiz kanallari secin',
            btn_text=f'{ICONS["arrow_r"]} Basla',
            btn_color=COLORS['primary'],
            callback=lambda: self.go_to('manual_input')
        )
        cards.add_widget(manual_card)
        
        # Auto Card
        auto_card = self.create_card(
            icon=ICONS['gear'],
            title='Otomatik Duzenleme',
            desc='Toplu linkleri test edin\nulkelere gore filtreleyin',
            btn_text=f'{ICONS["arrow_r"]} Basla',
            btn_color=COLORS['secondary'],
            callback=lambda: self.go_to('auto_input')
        )
        cards.add_widget(auto_card)
        
        root.add_widget(cards)
        
        # Footer
        footer = Label(
            text=f'v6.0 {ICONS["star"]} Optimize Edilmis',
            font_size=dp(11),
            color=get_color_from_hex(COLORS['text_dark']),
            size_hint_y=0.08
        )
        root.add_widget(footer)
        
        self.add_widget(root)
        
        # Entrance animation
        root.opacity = 0
        anim = Animation(opacity=1, duration=0.4)
        anim.start(root)
    
    def create_card(self, icon, title, desc, btn_text, btn_color, callback):
        card = BoxLayout(orientation='vertical', padding=dp(18), spacing=dp(10))
        
        # Background
        with card.canvas.before:
            Color(*get_color_from_hex(COLORS['bg_card']))
            card._bg = RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(15)])
        card.bind(pos=self._update_card_bg, size=self._update_card_bg)
        
        # Header row
        header_row = BoxLayout(size_hint_y=None, height=dp(38), spacing=dp(10))
        
        icon_lbl = Label(
            text=icon,
            font_size=dp(28),
            color=get_color_from_hex(COLORS['primary']),
            size_hint_x=None,
            width=dp(40)
        )
        header_row.add_widget(icon_lbl)
        
        title_lbl = Label(
            text=title,
            font_size=dp(17),
            bold=True,
            color=get_color_from_hex(COLORS['text_white']),
            halign='left'
        )
        title_lbl.bind(size=lambda w, s: setattr(w, 'text_size', s))
        header_row.add_widget(title_lbl)
        
        card.add_widget(header_row)
        
        # Description
        desc_lbl = Label(
            text=desc,
            font_size=dp(12),
            color=get_color_from_hex(COLORS['text_gray']),
            size_hint_y=None,
            height=dp(35),
            halign='center'
        )
        desc_lbl.bind(size=lambda w, s: setattr(w, 'text_size', s))
        card.add_widget(desc_lbl)
        
        # Button
        btn = Button(
            text=btn_text,
            font_size=dp(14),
            bold=True,
            size_hint=(0.55, None),
            height=dp(40),
            pos_hint={'center_x': 0.5},
            background_normal='',
            background_color=get_color_from_hex(btn_color)
        )
        btn.bind(on_press=lambda x: callback())
        card.add_widget(btn)
        
        return card
    
    def _update_card_bg(self, widget, value):
        if hasattr(widget, '_bg'):
            widget._bg.pos = widget.pos
            widget._bg.size = widget.size
    
    def go_to(self, screen_name):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = screen_name


class ManualInputScreen(BaseScreen):
    """Manuel URL giris ekrani"""
    
    def on_enter(self):
        self.clear_widgets()
        self.selected_format = 'm3u8'
        Clock.schedule_once(lambda dt: self.build_ui(), 0.05)
    
    def build_ui(self):
        root = BoxLayout(orientation='vertical', padding=dp(18), spacing=dp(15))
        
        # Top bar
        top_bar = self.create_top_bar('Manuel Duzenleme', 'welcome')
        root.add_widget(top_bar)
        
        # URL Card
        url_card = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10), size_hint_y=None, height=dp(130))
        self._setup_card_bg(url_card)
        
        url_label = Label(
            text=f'{ICONS["link"]} Playlist URL',
            font_size=dp(13),
            color=get_color_from_hex(COLORS['text_gray']),
            size_hint_y=None,
            height=dp(22),
            halign='left'
        )
        url_label.bind(size=lambda w, s: setattr(w, 'text_size', s))
        url_card.add_widget(url_label)
        
        self.url_input = TextInput(
            hint_text='https://example.com/playlist.m3u',
            multiline=False,
            font_size=dp(14),
            background_color=get_color_from_hex(COLORS['bg_medium']),
            foreground_color=get_color_from_hex(COLORS['text_white']),
            cursor_color=get_color_from_hex(COLORS['primary']),
            padding=[dp(12), dp(10)],
            size_hint_y=None,
            height=dp(48)
        )
        url_card.add_widget(self.url_input)
        
        root.add_widget(url_card)
        
        # Format Card
        format_card = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10), size_hint_y=None, height=dp(115))
        self._setup_card_bg(format_card)
        
        format_label = Label(
            text=f'{ICONS["file"]} Cikti Formati',
            font_size=dp(13),
            color=get_color_from_hex(COLORS['text_gray']),
            size_hint_y=None,
            height=dp(22),
            halign='left'
        )
        format_label.bind(size=lambda w, s: setattr(w, 'text_size', s))
        format_card.add_widget(format_label)
        
        format_btns = BoxLayout(spacing=dp(8), size_hint_y=None, height=dp(42))
        self.format_buttons = {}
        
        for fmt_id, fmt_data in FILE_FORMATS.items():
            is_selected = fmt_id == 'm3u8'
            btn = ToggleButton(
                text=f"{fmt_data['name']} {'*' if fmt_id == 'm3u8' else ''}",
                group='format',
                state='down' if is_selected else 'normal',
                font_size=dp(13),
                background_normal='',
                background_color=get_color_from_hex(COLORS['primary']) if is_selected else get_color_from_hex(COLORS['bg_card_light'])
            )
            btn.format_id = fmt_id
            btn.bind(on_press=self.on_format_select)
            self.format_buttons[fmt_id] = btn
            format_btns.add_widget(btn)
        
        format_card.add_widget(format_btns)
        root.add_widget(format_card)
        
        # Spacer
        root.add_widget(Label())
        
        # Load Button
        load_btn = Button(
            text=f'{ICONS["download"]} Kanallari Yukle',
            font_size=dp(16),
            bold=True,
            size_hint_y=None,
            height=dp(52),
            background_normal='',
            background_color=get_color_from_hex(COLORS['success'])
        )
        load_btn.bind(on_press=self.load_channels)
        root.add_widget(load_btn)
        
        self.add_widget(root)
    
    def create_top_bar(self, title, back_screen):
        top_bar = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(10))
        
        back_btn = Button(
            text=ICONS['back'],
            size_hint=(None, None),
            size=(dp(48), dp(42)),
            font_size=dp(20),
            background_normal='',
            background_color=get_color_from_hex(COLORS['bg_card'])
        )
        back_btn.bind(on_press=lambda x: self.go_back(back_screen))
        top_bar.add_widget(back_btn)
        
        title_lbl = Label(
            text=f'{ICONS["edit"]} {title}',
            font_size=dp(17),
            bold=True,
            color=get_color_from_hex(COLORS['text_white'])
        )
        top_bar.add_widget(title_lbl)
        
        return top_bar
    
    def _setup_card_bg(self, card):
        with card.canvas.before:
            Color(*get_color_from_hex(COLORS['bg_card']))
            card._bg = RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(12)])
        card.bind(pos=self._update_bg, size=self._update_bg)
    
    def _update_bg(self, widget, value):
        if hasattr(widget, '_bg'):
            widget._bg.pos = widget.pos
            widget._bg.size = widget.size
    
    def on_format_select(self, btn):
        self.selected_format = btn.format_id
        for fmt_id, button in self.format_buttons.items():
            if fmt_id == self.selected_format:
                button.background_color = get_color_from_hex(COLORS['primary'])
            else:
                button.background_color = get_color_from_hex(COLORS['bg_card_light'])
    
    def load_channels(self, instance):
        url = self.url_input.text.strip()
        if not url:
            self.show_popup(ICONS['warning'], 'Hata', 'Lutfen bir URL girin!', 'warning')
            return
        
        if not url.startswith('http'):
            self.show_popup(ICONS['error'], 'Hata', 'Gecersiz URL formati!', 'danger')
            return
        
        self.show_loading()
        threading.Thread(target=self._load_playlist, args=(url,), daemon=True).start()
    
    def _load_playlist(self, url):
        try:
            response = requests.get(url, timeout=30, headers={'User-Agent': 'Mozilla/5.0'})
            response.raise_for_status()
            
            channels, groups, expire_date = parse_m3u_optimized(response.text, url)
            
            if not channels:
                Clock.schedule_once(lambda dt: self._on_error('Kanal bulunamadi!'))
                return
            
            Clock.schedule_once(lambda dt: self._on_success(channels, groups, expire_date, url))
            
        except requests.exceptions.Timeout:
            Clock.schedule_once(lambda dt: self._on_error('Baglanti zaman asimina ugradi!'))
        except Exception as e:
            Clock.schedule_once(lambda dt: self._on_error(f'Hata: {str(e)[:40]}'))
    
    def _on_success(self, channels, groups, expire_date, url):
        self.hide_loading()
        
        app = App.get_running_app()
        app.channels = channels
        app.groups = groups
        app.expire_date = expire_date
        app.source_url = url
        app.selected_format = self.selected_format
        app.source_mode = 'manual'
        
        cleanup_memory()
        self.manager.current = 'channel_list'
    
    def _on_error(self, msg):
        self.hide_loading()
        self.show_popup(ICONS['error'], 'Yukleme Hatasi', msg, 'danger')
    
    def show_loading(self):
        content = BoxLayout(orientation='vertical', padding=dp(25), spacing=dp(15))
        
        loading_icon = Label(
            text=ICONS['loading'],
            font_size=dp(45),
            color=get_color_from_hex(COLORS['primary'])
        )
        content.add_widget(loading_icon)
        
        # Animasyonlu dönen efekt
        anim = Animation(opacity=0.3, duration=0.5) + Animation(opacity=1, duration=0.5)
        anim.repeat = True
        anim.start(loading_icon)
        
        msg = Label(
            text='Yukleniyor...',
            font_size=dp(14),
            color=get_color_from_hex(COLORS['text_white'])
        )
        content.add_widget(msg)
        
        progress = AnimatedProgressBar(size_hint_y=None, height=dp(20))
        progress.set_progress(50)
        content.add_widget(progress)
        
        self._loading_popup = Popup(
            title='',
            content=content,
            size_hint=(0.75, 0.35),
            auto_dismiss=False,
            separator_height=0,
            background_color=[0.05, 0.1, 0.16, 0.95]
        )
        self._loading_popup.open()
    
    def hide_loading(self):
        if hasattr(self, '_loading_popup'):
            self._loading_popup.dismiss()
    
    def show_popup(self, icon, title, message, popup_type='info'):
        colors = {
            'info': COLORS['info'],
            'success': COLORS['success'],
            'warning': COLORS['warning'],
            'danger': COLORS['danger']
        }
        
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        
        icon_lbl = Label(
            text=icon,
            font_size=dp(45),
            color=get_color_from_hex(colors.get(popup_type, COLORS['info']))
        )
        content.add_widget(icon_lbl)
        
        msg = Label(
            text=message,
            font_size=dp(14),
            color=get_color_from_hex(COLORS['text_white']),
            halign='center'
        )
        msg.bind(size=lambda w, s: setattr(w, 'text_size', s))
        content.add_widget(msg)
        
        btn = Button(
            text='Tamam',
            size_hint=(0.5, None),
            height=dp(42),
            pos_hint={'center_x': 0.5},
            background_normal='',
            background_color=get_color_from_hex(colors.get(popup_type, COLORS['info']))
        )
        
        popup = Popup(
            title='',
            content=content,
            size_hint=(0.8, 0.4),
            separator_height=0
        )
        
        btn.bind(on_press=popup.dismiss)
        content.add_widget(btn)
        popup.open()
    
    def go_back(self, screen):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = screen


class ChannelListScreen(BaseScreen):
    """Kanal gruplari listesi - Optimize edilmis"""
    
    def on_enter(self):
        self.clear_widgets()
        self.selected_groups = set()
        Clock.schedule_once(lambda dt: self.build_ui(), 0.05)
    
    def build_ui(self):
        app = App.get_running_app()
        groups = getattr(app, 'groups', {})
        channels = getattr(app, 'channels', [])
        expire_date = getattr(app, 'expire_date', 'Bilinmiyor')
        
        root = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        
        # Top bar
        top_bar = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(10))
        
        back_btn = Button(
            text=ICONS['back'],
            size_hint=(None, None),
            size=(dp(48), dp(42)),
            font_size=dp(20),
            background_normal='',
            background_color=get_color_from_hex(COLORS['bg_card'])
        )
        back_btn.bind(on_press=lambda x: self.go_back())
        top_bar.add_widget(back_btn)
        
        title = Label(
            text=f'{ICONS["tv"]} Kanal Gruplari',
            font_size=dp(16),
            bold=True,
            color=get_color_from_hex(COLORS['text_white'])
        )
        top_bar.add_widget(title)
        
        root.add_widget(top_bar)
        
        # Info bar
        info_bar = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(8))
        
        # Stats
        stats_box = BoxLayout(orientation='vertical')
        stats1 = Label(
            text=f'{ICONS["list"]} {len(groups)} grup - {len(channels)} kanal',
            font_size=dp(12),
            color=get_color_from_hex(COLORS['text_gray']),
            halign='left'
        )
        stats1.bind(size=lambda w, s: setattr(w, 'text_size', s))
        stats_box.add_widget(stats1)
        
        stats2 = Label(
            text=f'{ICONS["time"]} Bitis: {expire_date}',
            font_size=dp(11),
            color=get_color_from_hex(COLORS['warning']),
            halign='left'
        )
        stats2.bind(size=lambda w, s: setattr(w, 'text_size', s))
        stats_box.add_widget(stats2)
        
        info_bar.add_widget(stats_box)
        
        root.add_widget(info_bar)
        
        # Selection label
        self.selection_label = Label(
            text=f'{ICONS["check"]} Secilen: 0 grup (0 kanal)',
            font_size=dp(12),
            color=get_color_from_hex(COLORS['success']),
            size_hint_y=None,
            height=dp(22)
        )
        root.add_widget(self.selection_label)
        
        # RecycleView ile optimize edilmis liste
        self.rv = RV()
        self.rv_data = []
        
        for group_name, group_data in sorted(groups.items()):
            self.rv_data.append({
                'group_name': group_name,
                'channel_count': len(group_data['channels']),
                'selected': False,
                'callback': self.on_group_select
            })
        
        self.rv.data = self.rv_data
        root.add_widget(self.rv)
        
        # Bottom buttons
        bottom = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        
        select_all_btn = Button(
            text=f'{ICONS["check"]} Tumunu Sec',
            font_size=dp(13),
            bold=True,
            background_normal='',
            background_color=get_color_from_hex(COLORS['primary'])
        )
        select_all_btn.bind(on_press=self.select_all)
        bottom.add_widget(select_all_btn)
        
        export_btn = Button(
            text=f'{ICONS["export"]} Disa Aktar',
            font_size=dp(13),
            bold=True,
            background_normal='',
            background_color=get_color_from_hex(COLORS['success'])
        )
        export_btn.bind(on_press=self.export_selected)
        bottom.add_widget(export_btn)
        
        root.add_widget(bottom)
        self.add_widget(root)
    
    def on_group_select(self, group_name, selected, index):
        app = App.get_running_app()
        groups = getattr(app, 'groups', {})
        
        # Update data
        self.rv_data[index]['selected'] = selected
        
        if selected:
            self.selected_groups.add(group_name)
        else:
            self.selected_groups.discard(group_name)
        
        # Update label
        total_channels = sum(len(groups[g]['channels']) for g in self.selected_groups if g in groups)
        self.selection_label.text = f'{ICONS["check"]} Secilen: {len(self.selected_groups)} grup ({total_channels} kanal)'
    
    def select_all(self, instance):
        app = App.get_running_app()
        groups = getattr(app, 'groups', {})
        
        for i, item in enumerate(self.rv_data):
            item['selected'] = True
            self.selected_groups.add(item['group_name'])
        
        self.rv.data = self.rv_data
        self.rv.refresh_from_data()
        
        total_channels = sum(len(groups[g]['channels']) for g in self.selected_groups if g in groups)
        self.selection_label.text = f'{ICONS["check"]} Secilen: {len(self.selected_groups)} grup ({total_channels} kanal)'
    
    def export_selected(self, instance):
        if not self.selected_groups:
            self.show_popup(ICONS['warning'], 'Uyari', 'Lutfen en az bir grup secin!', 'warning')
            return
        
        app = App.get_running_app()
        groups = getattr(app, 'groups', {})
        selected_format = getattr(app, 'selected_format', 'm3u8')
        expire_date = getattr(app, 'expire_date', '')
        source_url = getattr(app, 'source_url', '')
        
        # Collect channels
        selected_channels = []
        for group_name in self.selected_groups:
            if group_name in groups:
                selected_channels.extend(groups[group_name]['channels'])
        
        # Generate content
        content = generate_m3u(selected_channels, selected_format)
        
        # Filename with expire date and domain
        download_path = get_download_path()
        domain = get_short_domain(source_url) if source_url else 'iptv'
        expire_str = expire_date.replace('.', '') if expire_date != 'Bilinmiyor' else datetime.now().strftime('%d%m%Y')
        ext = FILE_FORMATS.get(selected_format, {}).get('ext', '.m3u')
        filename = f'bitis{expire_str}_{domain}{ext}'
        filepath = os.path.join(download_path, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.show_popup(
                ICONS['success'],
                'Basarili!',
                f'{len(selected_channels)} kanal kaydedildi!\n\n{ICONS["file"]} {filename}\n{ICONS["folder"]} Download',
                'success'
            )
        except Exception as e:
            self.show_popup(ICONS['error'], 'Hata', f'Kaydetme hatasi: {str(e)[:40]}', 'danger')
        
        cleanup_memory()
    
    def show_popup(self, icon, title, message, popup_type='info'):
        colors = {
            'info': COLORS['info'],
            'success': COLORS['success'],
            'warning': COLORS['warning'],
            'danger': COLORS['danger']
        }
        
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        
        icon_lbl = Label(
            text=icon,
            font_size=dp(45),
            color=get_color_from_hex(colors.get(popup_type, COLORS['info']))
        )
        content.add_widget(icon_lbl)
        
        msg = Label(
            text=message,
            font_size=dp(13),
            color=get_color_from_hex(COLORS['text_white']),
            halign='center'
        )
        msg.bind(size=lambda w, s: setattr(w, 'text_size', s))
        content.add_widget(msg)
        
        btn = Button(
            text='Tamam',
            size_hint=(0.5, None),
            height=dp(42),
            pos_hint={'center_x': 0.5},
            background_normal='',
            background_color=get_color_from_hex(colors.get(popup_type, COLORS['info']))
        )
        
        popup = Popup(title='', content=content, size_hint=(0.85, 0.45), separator_height=0)
        btn.bind(on_press=popup.dismiss)
        content.add_widget(btn)
        popup.open()
    
    def go_back(self):
        cleanup_memory()
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'manual_input'


class AutoInputScreen(BaseScreen):
    """Otomatik mod - Toplu link giris"""
    
    def on_enter(self):
        self.clear_widgets()
        self.test_mode = 'deep'
        Clock.schedule_once(lambda dt: self.build_ui(), 0.05)
    
    def build_ui(self):
        root = BoxLayout(orientation='vertical', padding=dp(18), spacing=dp(12))
        
        # Top bar
        top_bar = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(10))
        
        back_btn = Button(
            text=ICONS['back'],
            size_hint=(None, None),
            size=(dp(48), dp(42)),
            font_size=dp(20),
            background_normal='',
            background_color=get_color_from_hex(COLORS['bg_card'])
        )
        back_btn.bind(on_press=lambda x: self.go_back())
        top_bar.add_widget(back_btn)
        
        title = Label(
            text=f'{ICONS["gear"]} Otomatik Duzenleme',
            font_size=dp(17),
            bold=True,
            color=get_color_from_hex(COLORS['text_white'])
        )
        top_bar.add_widget(title)
        
        root.add_widget(top_bar)
        
        # Description
        desc = Label(
            text='IPTV linklerini her satira bir tane girin',
            font_size=dp(12),
            color=get_color_from_hex(COLORS['text_gray']),
            size_hint_y=None,
            height=dp(22)
        )
        root.add_widget(desc)
        
        # Links input card
        input_card = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(8))
        self._setup_card_bg(input_card)
        
        self.links_input = TextInput(
            hint_text='https://example1.com/playlist.m3u\nhttps://example2.com/playlist.m3u',
            multiline=True,
            font_size=dp(12),
            background_color=get_color_from_hex(COLORS['bg_medium']),
            foreground_color=get_color_from_hex(COLORS['text_white']),
            cursor_color=get_color_from_hex(COLORS['primary']),
            padding=[dp(12), dp(10)]
        )
        input_card.add_widget(self.links_input)
        
        root.add_widget(input_card)
        
        # Test mode card
        mode_card = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(8), size_hint_y=None, height=dp(100))
        self._setup_card_bg(mode_card)
        
        mode_label = Label(
            text=f'{ICONS["settings"]} Test Yontemi',
            font_size=dp(12),
            color=get_color_from_hex(COLORS['text_gray']),
            size_hint_y=None,
            height=dp(20),
            halign='left'
        )
        mode_label.bind(size=lambda w, s: setattr(w, 'text_size', s))
        mode_card.add_widget(mode_label)
        
        mode_btns = BoxLayout(spacing=dp(10), size_hint_y=None, height=dp(45))
        
        self.quick_btn = ToggleButton(
            text=f'{ICONS["lightning"]} Hizli',
            group='test_mode',
            state='normal',
            font_size=dp(12),
            background_normal='',
            background_color=get_color_from_hex(COLORS['bg_card_light'])
        )
        self.quick_btn.bind(on_press=lambda x: self.set_mode('quick'))
        mode_btns.add_widget(self.quick_btn)
        
        self.deep_btn = ToggleButton(
            text=f'{ICONS["search"]} Derin *',
            group='test_mode',
            state='down',
            font_size=dp(12),
            background_normal='',
            background_color=get_color_from_hex(COLORS['primary'])
        )
        self.deep_btn.bind(on_press=lambda x: self.set_mode('deep'))
        mode_btns.add_widget(self.deep_btn)
        
        mode_card.add_widget(mode_btns)
        root.add_widget(mode_card)
        
        # Start button
        start_btn = Button(
            text=f'{ICONS["play"]} Test Baslat',
            font_size=dp(16),
            bold=True,
            size_hint_y=None,
            height=dp(52),
            background_normal='',
            background_color=get_color_from_hex(COLORS['success'])
        )
        start_btn.bind(on_press=self.start_testing)
        root.add_widget(start_btn)
        
        self.add_widget(root)
    
    def _setup_card_bg(self, card):
        with card.canvas.before:
            Color(*get_color_from_hex(COLORS['bg_card']))
            card._bg = RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(12)])
        card.bind(pos=self._update_bg, size=self._update_bg)
    
    def _update_bg(self, widget, value):
        if hasattr(widget, '_bg'):
            widget._bg.pos = widget.pos
            widget._bg.size = widget.size
    
    def set_mode(self, mode):
        self.test_mode = mode
        if mode == 'quick':
            self.quick_btn.background_color = get_color_from_hex(COLORS['primary'])
            self.deep_btn.background_color = get_color_from_hex(COLORS['bg_card_light'])
        else:
            self.quick_btn.background_color = get_color_from_hex(COLORS['bg_card_light'])
            self.deep_btn.background_color = get_color_from_hex(COLORS['primary'])
    
    def start_testing(self, instance):
        text = self.links_input.text.strip()
        
        if not text:
            self.show_popup(ICONS['warning'], 'Hata', 'Lutfen en az bir link girin!', 'warning')
            return
        
        links = []
        for line in text.split('\n'):
            line = line.strip()
            if line.startswith('http'):
                links.append(line)
        
        if not links:
            self.show_popup(ICONS['error'], 'Hata', 'Gecerli link bulunamadi!', 'danger')
            return
        
        app = App.get_running_app()
        app.links_to_test = links
        app.test_mode = self.test_mode
        
        self.manager.current = 'testing'
    
    def show_popup(self, icon, title, message, popup_type='info'):
        colors = {'warning': COLORS['warning'], 'danger': COLORS['danger']}
        
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        
        icon_lbl = Label(text=icon, font_size=dp(45), color=get_color_from_hex(colors.get(popup_type, COLORS['info'])))
        content.add_widget(icon_lbl)
        
        msg = Label(text=message, font_size=dp(14), color=get_color_from_hex(COLORS['text_white']), halign='center')
        msg.bind(size=lambda w, s: setattr(w, 'text_size', s))
        content.add_widget(msg)
        
        btn = Button(
            text='Tamam',
            size_hint=(0.5, None),
            height=dp(42),
            pos_hint={'center_x': 0.5},
            background_normal='',
            background_color=get_color_from_hex(colors.get(popup_type, COLORS['info']))
        )
        
        popup = Popup(title='', content=content, size_hint=(0.8, 0.4), separator_height=0)
        btn.bind(on_press=popup.dismiss)
        content.add_widget(btn)
        popup.open()
    
    def go_back(self):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'welcome'


class TestingScreen(BaseScreen):
    """Link test ekrani - Animasyonlu progress"""
    
    def on_enter(self):
        self.clear_widgets()
        self.testing = True
        self.working_links = []
        self.failed_links = []
        self.link_results = {}  # URL -> {expire, domain, channels}
        Clock.schedule_once(lambda dt: self.build_ui(), 0.05)
        Clock.schedule_once(lambda dt: self.start_tests(), 0.2)
    
    def build_ui(self):
        root = BoxLayout(orientation='vertical', padding=dp(18), spacing=dp(12))
        
        # Title
        title = Label(
            text=f'{ICONS["search"]} Linkler Test Ediliyor',
            font_size=dp(20),
            bold=True,
            color=get_color_from_hex(COLORS['text_white']),
            size_hint_y=None,
            height=dp(40)
        )
        root.add_widget(title)
        
        # Progress card
        progress_card = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10), size_hint_y=None, height=dp(130))
        self._setup_card_bg(progress_card)
        
        self.progress_label = Label(
            text='Hazirlaniyor...',
            font_size=dp(15),
            color=get_color_from_hex(COLORS['text_white']),
            size_hint_y=None,
            height=dp(25)
        )
        progress_card.add_widget(self.progress_label)
        
        # Animated progress bar
        self.progress_bar = AnimatedProgressBar(size_hint_y=None, height=dp(20))
        progress_card.add_widget(self.progress_bar)
        
        # Percentage label
        self.percent_label = Label(
            text='%0',
            font_size=dp(22),
            bold=True,
            color=get_color_from_hex(COLORS['primary']),
            size_hint_y=None,
            height=dp(30)
        )
        progress_card.add_widget(self.percent_label)
        
        self.stats_label = Label(
            text=f'{ICONS["success"]} 0 Calisiyor  {ICONS["cross"]} 0 Basarisiz',
            font_size=dp(12),
            color=get_color_from_hex(COLORS['text_gray']),
            size_hint_y=None,
            height=dp(22)
        )
        progress_card.add_widget(self.stats_label)
        
        root.add_widget(progress_card)
        
        # Log area
        log_card = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(5))
        self._setup_card_bg(log_card)
        
        log_title = Label(
            text=f'{ICONS["list"]} Test Gunlugu',
            font_size=dp(12),
            color=get_color_from_hex(COLORS['text_gray']),
            size_hint_y=None,
            height=dp(20),
            halign='left'
        )
        log_title.bind(size=lambda w, s: setattr(w, 'text_size', s))
        log_card.add_widget(log_title)
        
        scroll = ScrollView()
        self.log_layout = BoxLayout(orientation='vertical', spacing=dp(3), size_hint_y=None)
        self.log_layout.bind(minimum_height=self.log_layout.setter('height'))
        scroll.add_widget(self.log_layout)
        log_card.add_widget(scroll)
        
        root.add_widget(log_card)
        
        # Action button
        self.action_btn = Button(
            text=f'{ICONS["cross"]} Iptal Et',
            font_size=dp(15),
            bold=True,
            size_hint_y=None,
            height=dp(48),
            background_normal='',
            background_color=get_color_from_hex(COLORS['danger'])
        )
        self.action_btn.bind(on_press=self.on_action)
        root.add_widget(self.action_btn)
        
        self.add_widget(root)
    
    def _setup_card_bg(self, card):
        with card.canvas.before:
            Color(*get_color_from_hex(COLORS['bg_card']))
            card._bg = RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(12)])
        card.bind(pos=self._update_bg, size=self._update_bg)
    
    def _update_bg(self, widget, value):
        if hasattr(widget, '_bg'):
            widget._bg.pos = widget.pos
            widget._bg.size = widget.size
    
    def start_tests(self):
        threading.Thread(target=self._run_tests, daemon=True).start()
    
    def _run_tests(self):
        app = App.get_running_app()
        links = getattr(app, 'links_to_test', [])
        test_mode = getattr(app, 'test_mode', 'deep')
        
        total = len(links)
        
        for i, link in enumerate(links):
            if not self.testing:
                break
            
            domain = get_short_domain(link)
            Clock.schedule_once(lambda dt, d=domain: self.add_log(f'{ICONS["loading"]} Test: {d}', 'testing'))
            
            if test_mode == 'quick':
                success, message = test_link_fast(link)
            else:
                success, message = test_link_deep(link)
            
            if success:
                self.working_links.append(link)
                self.link_results[link] = {'domain': domain, 'status': 'ok'}
                Clock.schedule_once(lambda dt, d=domain: self.add_log(f'{ICONS["success"]} Calisiyor: {d}', 'success'))
            else:
                self.failed_links.append({'link': link, 'reason': message})
                Clock.schedule_once(lambda dt, d=domain, m=message: self.add_log(f'{ICONS["cross"]} Basarisiz: {d} ({m})', 'error'))
            
            progress = ((i + 1) / total) * 100
            Clock.schedule_once(lambda dt, p=progress, c=i+1, t=total: self.update_progress(p, c, t))
        
        Clock.schedule_once(lambda dt: self.tests_complete())
    
    def add_log(self, text, log_type):
        colors = {
            'testing': COLORS['text_gray'],
            'success': COLORS['success'],
            'error': COLORS['danger']
        }
        
        log_item = Label(
            text=text,
            font_size=dp(11),
            color=get_color_from_hex(colors.get(log_type, COLORS['text_gray'])),
            size_hint_y=None,
            height=dp(20),
            halign='left'
        )
        log_item.bind(size=lambda w, s: setattr(w, 'text_size', s))
        self.log_layout.add_widget(log_item)
        
        # Limit log entries for memory
        if len(self.log_layout.children) > 50:
            self.log_layout.remove_widget(self.log_layout.children[-1])
    
    def update_progress(self, progress, current, total):
        self.progress_bar.set_progress(progress, animate=True)
        self.progress_label.text = f'Test ediliyor: {current}/{total}'
        self.percent_label.text = f'%{int(progress)}'
        self.stats_label.text = f'{ICONS["success"]} {len(self.working_links)} Calisiyor  {ICONS["cross"]} {len(self.failed_links)} Basarisiz'
    
    def tests_complete(self):
        self.testing = False
        self.progress_label.text = f'{ICONS["success"]} Test tamamlandi!'
        self.percent_label.text = '%100'
        self.action_btn.text = f'{ICONS["arrow_r"]} Devam Et'
        self.action_btn.background_color = get_color_from_hex(COLORS['success'])
        
        app = App.get_running_app()
        app.working_links = self.working_links
        app.failed_links = self.failed_links
        app.link_results = self.link_results
    
    def on_action(self, instance):
        if self.action_btn.text.startswith(ICONS['cross']):
            self.testing = False
            self.manager.transition = SlideTransition(direction='right')
            self.manager.current = 'auto_input'
        else:
            if not self.working_links:
                self.show_no_links_popup()
            else:
                cleanup_memory()
                self.manager.current = 'auto_result'
    
    def show_no_links_popup(self):
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        
        icon = Label(text=ICONS['warning'], font_size=dp(50), color=get_color_from_hex(COLORS['warning']))
        content.add_widget(icon)
        
        msg = Label(
            text='Calisan link bulunamadi!\nLutfen farkli linkler deneyin.',
            font_size=dp(14),
            color=get_color_from_hex(COLORS['text_white']),
            halign='center'
        )
        msg.bind(size=lambda w, s: setattr(w, 'text_size', s))
        content.add_widget(msg)
        
        btn = Button(
            text='Geri Don',
            size_hint=(0.5, None),
            height=dp(42),
            pos_hint={'center_x': 0.5},
            background_normal='',
            background_color=get_color_from_hex(COLORS['primary'])
        )
        
        popup = Popup(title='', content=content, size_hint=(0.8, 0.4), separator_height=0)
        
        def go_back(x):
            popup.dismiss()
            self.manager.transition = SlideTransition(direction='right')
            self.manager.current = 'auto_input'
        
        btn.bind(on_press=go_back)
        content.add_widget(btn)
        popup.open()


class AutoResultScreen(BaseScreen):
    """Test sonuclari - Duzenleme modu secimi"""
    
    def on_enter(self):
        self.clear_widgets()
        Clock.schedule_once(lambda dt: self.build_ui(), 0.05)
    
    def build_ui(self):
        app = App.get_running_app()
        working = len(getattr(app, 'working_links', []))
        failed = len(getattr(app, 'failed_links', []))
        
        root = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        
        # Title
        title = Label(
            text=f'{ICONS["success"]} Test Tamamlandi!',
            font_size=dp(22),
            bold=True,
            color=get_color_from_hex(COLORS['text_white']),
            size_hint_y=None,
            height=dp(40)
        )
        root.add_widget(title)
        
        # Results card
        result_card = BoxLayout(orientation='horizontal', padding=dp(20), spacing=dp(20), size_hint_y=None, height=dp(100))
        self._setup_card_bg(result_card)
        
        # Working
        working_box = BoxLayout(orientation='vertical')
        working_box.add_widget(Label(text=ICONS['success'], font_size=dp(30), color=get_color_from_hex(COLORS['success'])))
        working_box.add_widget(Label(text=str(working), font_size=dp(26), bold=True, color=get_color_from_hex(COLORS['success'])))
        working_box.add_widget(Label(text='Calisiyor', font_size=dp(11), color=get_color_from_hex(COLORS['text_gray'])))
        result_card.add_widget(working_box)
        
        # Failed
        failed_box = BoxLayout(orientation='vertical')
        failed_box.add_widget(Label(text=ICONS['cross'], font_size=dp(30), color=get_color_from_hex(COLORS['danger'])))
        failed_box.add_widget(Label(text=str(failed), font_size=dp(26), bold=True, color=get_color_from_hex(COLORS['danger'])))
        failed_box.add_widget(Label(text='Basarisiz', font_size=dp(11), color=get_color_from_hex(COLORS['text_gray'])))
        result_card.add_widget(failed_box)
        
        root.add_widget(result_card)
        
        # Question
        question = Label(
            text='Calisan linkleri nasil duzenlemek istersiniz?',
            font_size=dp(14),
            color=get_color_from_hex(COLORS['text_light']),
            size_hint_y=None,
            height=dp(30)
        )
        root.add_widget(question)
        
        # Options
        options = BoxLayout(orientation='vertical', spacing=dp(12))
        
        # Auto option
        auto_card = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(8), size_hint_y=None, height=dp(115))
        self._setup_card_bg(auto_card)
        
        auto_header = BoxLayout(size_hint_y=None, height=dp(30))
        auto_header.add_widget(Label(text=ICONS['gear'], font_size=dp(24), size_hint_x=None, width=dp(35), color=get_color_from_hex(COLORS['primary'])))
        auto_header.add_widget(Label(text='Otomatik Duzenleme', font_size=dp(15), bold=True, color=get_color_from_hex(COLORS['text_white']), halign='left'))
        auto_card.add_widget(auto_header)
        
        auto_desc = Label(
            text='Ulke secin, kanallar filtrelensin - AYRI DOSYALAR',
            font_size=dp(11),
            color=get_color_from_hex(COLORS['text_gray']),
            size_hint_y=None,
            height=dp(20)
        )
        auto_card.add_widget(auto_desc)
        
        auto_btn = Button(
            text=f'{ICONS["arrow_r"]} Otomatik',
            size_hint=(0.6, None),
            height=dp(38),
            pos_hint={'center_x': 0.5},
            background_normal='',
            background_color=get_color_from_hex(COLORS['primary'])
        )
        auto_btn.bind(on_press=lambda x: self.go_auto())
        auto_card.add_widget(auto_btn)
        options.add_widget(auto_card)
        
        # Manual option
        manual_card = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(8), size_hint_y=None, height=dp(115))
        self._setup_card_bg(manual_card)
        
        manual_header = BoxLayout(size_hint_y=None, height=dp(30))
        manual_header.add_widget(Label(text=ICONS['edit'], font_size=dp(24), size_hint_x=None, width=dp(35), color=get_color_from_hex(COLORS['secondary'])))
        manual_header.add_widget(Label(text='Manuel Duzenleme', font_size=dp(15), bold=True, color=get_color_from_hex(COLORS['text_white']), halign='left'))
        manual_card.add_widget(manual_header)
        
        manual_desc = Label(
            text='Her linki tek tek duzenleyin',
            font_size=dp(11),
            color=get_color_from_hex(COLORS['text_gray']),
            size_hint_y=None,
            height=dp(20)
        )
        manual_card.add_widget(manual_desc)
        
        manual_btn = Button(
            text=f'{ICONS["arrow_r"]} Manuel',
            size_hint=(0.6, None),
            height=dp(38),
            pos_hint={'center_x': 0.5},
            background_normal='',
            background_color=get_color_from_hex(COLORS['secondary'])
        )
        manual_btn.bind(on_press=lambda x: self.go_manual())
        manual_card.add_widget(manual_btn)
        options.add_widget(manual_card)
        
        root.add_widget(options)
        
        # Back button
        back_btn = Button(
            text=f'{ICONS["back"]} Geri',
            size_hint_y=None,
            height=dp(42),
            background_normal='',
            background_color=get_color_from_hex(COLORS['bg_card'])
        )
        back_btn.bind(on_press=lambda x: self.go_back())
        root.add_widget(back_btn)
        
        self.add_widget(root)
    
    def _setup_card_bg(self, card):
        with card.canvas.before:
            Color(*get_color_from_hex(COLORS['bg_card']))
            card._bg = RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(12)])
        card.bind(pos=self._update_bg, size=self._update_bg)
    
    def _update_bg(self, widget, value):
        if hasattr(widget, '_bg'):
            widget._bg.pos = widget.pos
            widget._bg.size = widget.size
    
    def go_auto(self):
        self.manager.current = 'country_select'
    
    def go_manual(self):
        self.manager.current = 'manual_link_list'
    
    def go_back(self):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'auto_input'


class CountrySelectScreen(BaseScreen):
    """Ulke secim ekrani"""
    
    def on_enter(self):
        self.clear_widgets()
        self.selected_countries = set()
        self.selected_format = 'm3u8'
        Clock.schedule_once(lambda dt: self.build_ui(), 0.05)
    
    def build_ui(self):
        root = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        
        # Top bar
        top_bar = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(10))
        
        back_btn = Button(
            text=ICONS['back'],
            size_hint=(None, None),
            size=(dp(48), dp(42)),
            font_size=dp(20),
            background_normal='',
            background_color=get_color_from_hex(COLORS['bg_card'])
        )
        back_btn.bind(on_press=lambda x: self.go_back())
        top_bar.add_widget(back_btn)
        
        title = Label(
            text=f'{ICONS["flag"]} Ulke Secimi',
            font_size=dp(17),
            bold=True,
            color=get_color_from_hex(COLORS['text_white'])
        )
        top_bar.add_widget(title)
        
        root.add_widget(top_bar)
        
        # Info
        info = Label(
            text='Grup bazli filtreleme yapilacak\nGrup adindaki ulke koduna gore tum grup dahil edilir',
            font_size=dp(11),
            color=get_color_from_hex(COLORS['text_gray']),
            size_hint_y=None,
            height=dp(35),
            halign='center'
        )
        info.bind(size=lambda w, s: setattr(w, 'text_size', s))
        root.add_widget(info)
        
        # Selection label
        self.selection_label = Label(
            text=f'{ICONS["check"]} Secilen: 0 ulke',
            font_size=dp(12),
            color=get_color_from_hex(COLORS['success']),
            size_hint_y=None,
            height=dp(22)
        )
        root.add_widget(self.selection_label)
        
        # Country grid
        scroll = ScrollView()
        grid = GridLayout(cols=2, spacing=dp(8), size_hint_y=None, padding=dp(3))
        grid.bind(minimum_height=grid.setter('height'))
        
        self.country_buttons = {}
        
        # Priority countries first
        for country_id in PRIORITY_COUNTRIES:
            country_data = COUNTRIES[country_id]
            btn = self._create_country_btn(country_id, country_data, priority=True)
            grid.add_widget(btn)
        
        # Other countries
        for country_id, country_data in sorted(COUNTRIES.items(), key=lambda x: x[1]['priority']):
            if country_id not in PRIORITY_COUNTRIES:
                btn = self._create_country_btn(country_id, country_data)
                grid.add_widget(btn)
        
        scroll.add_widget(grid)
        root.add_widget(scroll)
        
        # Format selection
        format_box = BoxLayout(size_hint_y=None, height=dp(45), spacing=dp(8))
        
        format_label = Label(
            text='Format:',
            size_hint_x=None,
            width=dp(55),
            font_size=dp(12),
            color=get_color_from_hex(COLORS['text_gray'])
        )
        format_box.add_widget(format_label)
        
        self.format_buttons = {}
        for fmt_id in ['m3u', 'm3u8', 'txt']:
            fmt_data = FILE_FORMATS[fmt_id]
            btn = ToggleButton(
                text=fmt_data['name'],
                group='format_select',
                state='down' if fmt_id == 'm3u8' else 'normal',
                font_size=dp(12),
                background_normal='',
                background_color=get_color_from_hex(COLORS['primary']) if fmt_id == 'm3u8' else get_color_from_hex(COLORS['bg_card_light'])
            )
            btn.format_id = fmt_id
            btn.bind(on_press=self.on_format_select)
            self.format_buttons[fmt_id] = btn
            format_box.add_widget(btn)
        
        root.add_widget(format_box)
        
        # Process button
        process_btn = Button(
            text=f'{ICONS["play"]} Olustur (Ayri Dosyalar)',
            font_size=dp(15),
            bold=True,
            size_hint_y=None,
            height=dp(50),
            background_normal='',
            background_color=get_color_from_hex(COLORS['success'])
        )
        process_btn.bind(on_press=self.start_process)
        root.add_widget(process_btn)
        
        self.add_widget(root)
    
    def _create_country_btn(self, country_id, country_data, priority=False):
        btn = ToggleButton(
            text=f"{country_data['flag']} {country_data['name']}",
            size_hint_y=None,
            height=dp(50),
            font_size=dp(12),
            background_normal='',
            background_color=get_color_from_hex(COLORS['warning']) if priority else get_color_from_hex(COLORS['bg_card'])
        )
        btn.country_id = country_id
        btn.is_priority = priority
        btn.bind(on_press=self.on_country_toggle)
        self.country_buttons[country_id] = btn
        return btn
    
    def on_country_toggle(self, btn):
        if btn.state == 'down':
            self.selected_countries.add(btn.country_id)
            btn.background_color = get_color_from_hex(COLORS['success'])
        else:
            self.selected_countries.discard(btn.country_id)
            if btn.is_priority:
                btn.background_color = get_color_from_hex(COLORS['warning'])
            else:
                btn.background_color = get_color_from_hex(COLORS['bg_card'])
        
        self.selection_label.text = f'{ICONS["check"]} Secilen: {len(self.selected_countries)} ulke'
    
    def on_format_select(self, btn):
        self.selected_format = btn.format_id
        for fmt_id, button in self.format_buttons.items():
            if fmt_id == self.selected_format:
                button.background_color = get_color_from_hex(COLORS['primary'])
            else:
                button.background_color = get_color_from_hex(COLORS['bg_card_light'])
    
    def start_process(self, instance):
        if not self.selected_countries:
            self.show_popup(ICONS['warning'], 'Uyari', 'Lutfen en az bir ulke secin!', 'warning')
            return
        
        app = App.get_running_app()
        app.selected_countries = self.selected_countries
        app.output_format = self.selected_format
        
        self.manager.current = 'processing'
    
    def show_popup(self, icon, title, message, popup_type='info'):
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        icon_lbl = Label(text=icon, font_size=dp(45), color=get_color_from_hex(COLORS['warning']))
        content.add_widget(icon_lbl)
        msg = Label(text=message, font_size=dp(14), color=get_color_from_hex(COLORS['text_white']), halign='center')
        content.add_widget(msg)
        btn = Button(text='Tamam', size_hint=(0.5, None), height=dp(42), pos_hint={'center_x': 0.5},
                    background_normal='', background_color=get_color_from_hex(COLORS['warning']))
        popup = Popup(title='', content=content, size_hint=(0.75, 0.35), separator_height=0)
        btn.bind(on_press=popup.dismiss)
        content.add_widget(btn)
        popup.open()
    
    def go_back(self):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'auto_result'


class ProcessingScreen(BaseScreen):
    """Isleme ekrani - Her link icin ayri dosya"""
    
    def on_enter(self):
        self.clear_widgets()
        self.saved_files = []
        Clock.schedule_once(lambda dt: self.build_ui(), 0.05)
        Clock.schedule_once(lambda dt: self.start_processing(), 0.2)
    
    def build_ui(self):
        root = BoxLayout(orientation='vertical', padding=dp(25), spacing=dp(15))
        
        # Title
        title = Label(
            text=f'{ICONS["gear"]} Isleniyor...',
            font_size=dp(22),
            bold=True,
            color=get_color_from_hex(COLORS['text_white']),
            size_hint_y=None,
            height=dp(40)
        )
        root.add_widget(title)
        
        # Status
        self.status_label = Label(
            text='Baslatiliyor...',
            font_size=dp(14),
            color=get_color_from_hex(COLORS['text_gray']),
            size_hint_y=None,
            height=dp(25)
        )
        root.add_widget(self.status_label)
        
        # Progress bar
        self.progress_bar = AnimatedProgressBar(size_hint_y=None, height=dp(20))
        root.add_widget(self.progress_bar)
        
        # Percent
        self.percent_label = Label(
            text='%0',
            font_size=dp(24),
            bold=True,
            color=get_color_from_hex(COLORS['primary']),
            size_hint_y=None,
            height=dp(35)
        )
        root.add_widget(self.percent_label)
        
        # Stats card
        stats_card = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(8), size_hint_y=None, height=dp(130))
        self._setup_card_bg(stats_card)
        
        self.current_label = Label(
            text=f'{ICONS["link"]} Islenen: -',
            font_size=dp(12),
            color=get_color_from_hex(COLORS['text_gray'])
        )
        stats_card.add_widget(self.current_label)
        
        self.total_label = Label(
            text=f'{ICONS["tv"]} Toplam Kanal: 0',
            font_size=dp(14),
            color=get_color_from_hex(COLORS['text_white'])
        )
        stats_card.add_widget(self.total_label)
        
        self.filtered_label = Label(
            text=f'{ICONS["success"]} Filtrelenen: 0',
            font_size=dp(14),
            color=get_color_from_hex(COLORS['success'])
        )
        stats_card.add_widget(self.filtered_label)
        
        self.files_label = Label(
            text=f'{ICONS["file"]} Olusturulan: 0 dosya',
            font_size=dp(12),
            color=get_color_from_hex(COLORS['info'])
        )
        stats_card.add_widget(self.files_label)
        
        root.add_widget(stats_card)
        
        root.add_widget(Label())
        
        self.add_widget(root)
    
    def _setup_card_bg(self, card):
        with card.canvas.before:
            Color(*get_color_from_hex(COLORS['bg_card']))
            card._bg = RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(12)])
        card.bind(pos=self._update_bg, size=self._update_bg)
    
    def _update_bg(self, widget, value):
        if hasattr(widget, '_bg'):
            widget._bg.pos = widget.pos
            widget._bg.size = widget.size
    
    def start_processing(self):
        threading.Thread(target=self._process, daemon=True).start()
    
    def _process(self):
        app = App.get_running_app()
        working_links = getattr(app, 'working_links', [])
        selected_countries = getattr(app, 'selected_countries', set())
        output_format = getattr(app, 'output_format', 'm3u8')
        
        total_links = len(working_links)
        total_channels = 0
        total_filtered = 0
        download_path = get_download_path()
        ext = FILE_FORMATS.get(output_format, {}).get('ext', '.m3u')
        
        for i, link in enumerate(working_links):
            domain = get_short_domain(link)
            Clock.schedule_once(lambda dt, d=domain: setattr(self.current_label, 'text', f'{ICONS["link"]} Islenen: {d}'))
            
            progress = ((i + 0.5) / total_links) * 100
            Clock.schedule_once(lambda dt, p=progress: self.update_progress(p))
            
            try:
                response = requests.get(link, timeout=30, headers={'User-Agent': 'Mozilla/5.0'})
                channels, groups, expire_date = parse_m3u_optimized(response.text, link)
                
                total_channels += len(channels)
                
                # GRUP BAZLI FILTRELEME
                filtered_channels = []
                for group_name, group_data in groups.items():
                    group_country = group_data.get('country', 'other')
                    
                    # Eger grubun ulkesi secilen ulkeler arasindaysa TUM GRUBU ekle
                    if group_country in selected_countries:
                        filtered_channels.extend(group_data['channels'])
                
                total_filtered += len(filtered_channels)
                
                Clock.schedule_once(lambda dt, t=total_channels, f=total_filtered: self.update_stats(t, f))
                
                # Eger filtrelenen kanal varsa dosya olustur
                if filtered_channels:
                    content = generate_m3u(filtered_channels, output_format)
                    
                    # Dosya adi: bitis{tarih}_{domain}.m3u8
                    expire_str = expire_date.replace('.', '') if expire_date != 'Bilinmiyor' else datetime.now().strftime('%d%m%Y')
                    filename = f'bitis{expire_str}_{domain}{ext}'
                    filepath = os.path.join(download_path, filename)
                    
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    self.saved_files.append({
                        'filename': filename,
                        'channels': len(filtered_channels),
                        'expire': expire_date,
                        'domain': domain
                    })
                    
                    Clock.schedule_once(lambda dt, c=len(self.saved_files): setattr(self.files_label, 'text', f'{ICONS["file"]} Olusturulan: {c} dosya'))
                
            except Exception as e:
                continue
            
            progress = ((i + 1) / total_links) * 100
            Clock.schedule_once(lambda dt, p=progress: self.update_progress(p))
            
            # Memory cleanup periodically
            if i % 3 == 0:
                cleanup_memory()
        
        app.saved_files = self.saved_files
        app.total_filtered = total_filtered
        app.total_channels = total_channels
        
        Clock.schedule_once(lambda dt: self.update_progress(100))
        Clock.schedule_once(lambda dt: self._complete())
    
    def update_progress(self, p):
        self.progress_bar.set_progress(p)
        self.percent_label.text = f'%{int(p)}'
    
    def update_stats(self, total, filtered):
        self.total_label.text = f'{ICONS["tv"]} Toplam Kanal: {total}'
        self.filtered_label.text = f'{ICONS["success"]} Filtrelenen: {filtered}'
    
    def _complete(self):
        cleanup_memory()
        self.manager.current = 'complete'


class ManualLinkListScreen(BaseScreen):
    """Manuel duzenleme - Link listesi"""
    
    def on_enter(self):
        self.clear_widgets()
        Clock.schedule_once(lambda dt: self.build_ui(), 0.05)
    
    def build_ui(self):
        app = App.get_running_app()
        working_links = getattr(app, 'working_links', [])
        
        root = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        
        # Top bar
        top_bar = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(10))
        
        back_btn = Button(
            text=ICONS['back'],
            size_hint=(None, None),
            size=(dp(48), dp(42)),
            font_size=dp(20),
            background_normal='',
            background_color=get_color_from_hex(COLORS['bg_card'])
        )
        back_btn.bind(on_press=lambda x: self.go_back())
        top_bar.add_widget(back_btn)
        
        title = Label(
            text=f'{ICONS["edit"]} Manuel Duzenleme',
            font_size=dp(16),
            bold=True,
            color=get_color_from_hex(COLORS['text_white'])
        )
        top_bar.add_widget(title)
        
        root.add_widget(top_bar)
        
        # Description
        desc = Label(
            text=f'{len(working_links)} calisan link - Duzenlemek icin tiklayin',
            font_size=dp(12),
            color=get_color_from_hex(COLORS['text_gray']),
            size_hint_y=None,
            height=dp(25)
        )
        root.add_widget(desc)
        
        # Link list
        scroll = ScrollView()
        list_layout = BoxLayout(orientation='vertical', spacing=dp(8), size_hint_y=None)
        list_layout.bind(minimum_height=list_layout.setter('height'))
        
        for i, link in enumerate(working_links):
            item = self._create_link_item(i + 1, link)
            list_layout.add_widget(item)
        
        scroll.add_widget(list_layout)
        root.add_widget(scroll)
        
        self.add_widget(root)
    
    def _create_link_item(self, index, link):
        item = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(65), padding=dp(10), spacing=dp(10))
        
        with item.canvas.before:
            Color(*get_color_from_hex(COLORS['bg_card']))
            item._bg = RoundedRectangle(pos=item.pos, size=item.size, radius=[dp(10)])
        item.bind(pos=self._update_item_bg, size=self._update_item_bg)
        
        # Index
        index_lbl = Label(
            text=str(index),
            font_size=dp(18),
            bold=True,
            color=get_color_from_hex(COLORS['primary']),
            size_hint_x=None,
            width=dp(35)
        )
        item.add_widget(index_lbl)
        
        # Info
        info = BoxLayout(orientation='vertical', spacing=dp(2))
        
        domain = get_short_domain(link)
        domain_lbl = Label(
            text=domain,
            font_size=dp(13),
            color=get_color_from_hex(COLORS['text_white']),
            halign='left'
        )
        domain_lbl.bind(size=lambda w, s: setattr(w, 'text_size', s))
        info.add_widget(domain_lbl)
        
        link_short = link[:40] + '...' if len(link) > 40 else link
        link_lbl = Label(
            text=link_short,
            font_size=dp(10),
            color=get_color_from_hex(COLORS['text_dark']),
            halign='left'
        )
        link_lbl.bind(size=lambda w, s: setattr(w, 'text_size', s))
        info.add_widget(link_lbl)
        
        item.add_widget(info)
        
        # Edit button
        edit_btn = Button(
            text=ICONS['edit'],
            size_hint=(None, None),
            size=(dp(45), dp(45)),
            font_size=dp(20),
            background_normal='',
            background_color=get_color_from_hex(COLORS['primary'])
        )
        edit_btn.link_url = link
        edit_btn.link_index = index
        edit_btn.bind(on_press=self.edit_link)
        item.add_widget(edit_btn)
        
        return item
    
    def _update_item_bg(self, widget, value):
        if hasattr(widget, '_bg'):
            widget._bg.pos = widget.pos
            widget._bg.size = widget.size
    
    def edit_link(self, btn):
        app = App.get_running_app()
        app.current_edit_link = btn.link_url
        app.current_edit_index = btn.link_index
        
        self.manager.current = 'link_editor'
    
    def go_back(self):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'auto_result'


class LinkEditorScreen(BaseScreen):
    """Tek link duzenleme - RecycleView ile optimize"""
    
    def on_enter(self):
        self.clear_widgets()
        self.selected_groups = set()
        self.groups = {}
        self.channels = []
        self.expire_date = 'Bilinmiyor'
        Clock.schedule_once(lambda dt: self.build_ui(), 0.05)
        Clock.schedule_once(lambda dt: self.load_link(), 0.1)
    
    def build_ui(self):
        app = App.get_running_app()
        link_index = getattr(app, 'current_edit_index', 1)
        working_links = getattr(app, 'working_links', [])
        
        root = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(8))
        
        # Top bar
        top_bar = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(10))
        
        back_btn = Button(
            text=ICONS['back'],
            size_hint=(None, None),
            size=(dp(48), dp(42)),
            font_size=dp(20),
            background_normal='',
            background_color=get_color_from_hex(COLORS['bg_card'])
        )
        back_btn.bind(on_press=lambda x: self.go_back())
        top_bar.add_widget(back_btn)
        
        title = Label(
            text=f'Link {link_index}/{len(working_links)}',
            font_size=dp(15),
            bold=True,
            color=get_color_from_hex(COLORS['text_white'])
        )
        top_bar.add_widget(title)
        
        root.add_widget(top_bar)
        
        # Loading / Content
        self.loading_label = Label(
            text=f'{ICONS["loading"]} Kanallar yukleniyor...',
            font_size=dp(14),
            color=get_color_from_hex(COLORS['text_gray'])
        )
        root.add_widget(self.loading_label)
        
        # Content layout
        self.content_layout = BoxLayout(orientation='vertical', spacing=dp(8), opacity=0)
        
        self.expire_label = Label(
            text='',
            font_size=dp(11),
            color=get_color_from_hex(COLORS['warning']),
            size_hint_y=None,
            height=dp(20)
        )
        self.content_layout.add_widget(self.expire_label)
        
        self.stats_label = Label(
            text='',
            font_size=dp(12),
            color=get_color_from_hex(COLORS['text_gray']),
            size_hint_y=None,
            height=dp(22)
        )
        self.content_layout.add_widget(self.stats_label)
        
        self.selection_label = Label(
            text=f'{ICONS["check"]} Secilen: 0 grup',
            font_size=dp(11),
            color=get_color_from_hex(COLORS['success']),
            size_hint_y=None,
            height=dp(20)
        )
        self.content_layout.add_widget(self.selection_label)
        
        # RecycleView
        self.rv = RV()
        self.rv_data = []
        self.content_layout.add_widget(self.rv)
        
        root.add_widget(self.content_layout)
        
        # Bottom
        self.bottom_bar = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(10), opacity=0)
        
        save_btn = Button(
            text=f'{ICONS["save"]} Kaydet',
            font_size=dp(14),
            bold=True,
            background_normal='',
            background_color=get_color_from_hex(COLORS['success'])
        )
        save_btn.bind(on_press=self.save_selection)
        self.bottom_bar.add_widget(save_btn)
        
        root.add_widget(self.bottom_bar)
        
        self.add_widget(root)
    
    def load_link(self):
        threading.Thread(target=self._load_content, daemon=True).start()
    
    def _load_content(self):
        app = App.get_running_app()
        link = getattr(app, 'current_edit_link', '')
        
        try:
            response = requests.get(link, timeout=30, headers={'User-Agent': 'Mozilla/5.0'})
            self.channels, self.groups, self.expire_date = parse_m3u_optimized(response.text, link)
            Clock.schedule_once(lambda dt: self._display_content())
        except Exception as e:
            Clock.schedule_once(lambda dt, m=str(e)[:40]: self._show_error(m))
    
    def _display_content(self):
        self.loading_label.opacity = 0
        self.content_layout.opacity = 1
        self.bottom_bar.opacity = 1
        
        self.expire_label.text = f'{ICONS["time"]} Bitis: {self.expire_date}'
        self.stats_label.text = f'{ICONS["list"]} {len(self.groups)} grup - {len(self.channels)} kanal'
        
        # RecycleView data
        self.rv_data = []
        for group_name, group_data in sorted(self.groups.items()):
            self.rv_data.append({
                'group_name': group_name,
                'channel_count': len(group_data['channels']),
                'selected': False,
                'callback': self.on_group_select
            })
        
        self.rv.data = self.rv_data
    
    def _show_error(self, msg):
        self.loading_label.text = f'{ICONS["error"]} Hata: {msg}'
    
    def on_group_select(self, group_name, selected, index):
        self.rv_data[index]['selected'] = selected
        
        if selected:
            self.selected_groups.add(group_name)
        else:
            self.selected_groups.discard(group_name)
        
        total_ch = sum(len(self.groups[g]['channels']) for g in self.selected_groups if g in self.groups)
        self.selection_label.text = f'{ICONS["check"]} Secilen: {len(self.selected_groups)} grup ({total_ch} kanal)'
    
    def save_selection(self, instance):
        if not self.selected_groups:
            self.show_popup(ICONS['warning'], 'Uyari', 'Lutfen en az bir grup secin!', 'warning')
            return
        
        selected_channels = []
        for group_name in self.selected_groups:
            if group_name in self.groups:
                selected_channels.extend(self.groups[group_name]['channels'])
        
        content = generate_m3u(selected_channels)
        
        app = App.get_running_app()
        link = getattr(app, 'current_edit_link', '')
        
        download_path = get_download_path()
        domain = get_short_domain(link)
        expire_str = self.expire_date.replace('.', '') if self.expire_date != 'Bilinmiyor' else datetime.now().strftime('%d%m%Y')
        filename = f'bitis{expire_str}_{domain}.m3u8'
        filepath = os.path.join(download_path, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.show_save_success(filename, len(selected_channels))
        except Exception as e:
            self.show_popup(ICONS['error'], 'Hata', f'Kaydetme hatasi: {str(e)[:40]}', 'danger')
        
        cleanup_memory()
    
    def show_popup(self, icon, title, message, popup_type='info'):
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        icon_lbl = Label(text=icon, font_size=dp(45), color=get_color_from_hex(COLORS['warning']))
        content.add_widget(icon_lbl)
        msg = Label(text=message, font_size=dp(14), color=get_color_from_hex(COLORS['text_white']), halign='center')
        content.add_widget(msg)
        btn = Button(text='Tamam', size_hint=(0.5, None), height=dp(42), pos_hint={'center_x': 0.5},
                    background_normal='', background_color=get_color_from_hex(COLORS['warning']))
        popup = Popup(title='', content=content, size_hint=(0.75, 0.35), separator_height=0)
        btn.bind(on_press=popup.dismiss)
        content.add_widget(btn)
        popup.open()
    
    def show_save_success(self, filename, channel_count):
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(12))
        
        icon = Label(text=ICONS['success'], font_size=dp(50), color=get_color_from_hex(COLORS['success']))
        content.add_widget(icon)
        
        title = Label(text='Basariyla Kaydedildi!', font_size=dp(16), bold=True, color=get_color_from_hex(COLORS['text_white']))
        content.add_widget(title)
        
        info = Label(text=f'{channel_count} kanal\n{ICONS["file"]} {filename}', font_size=dp(12),
                    color=get_color_from_hex(COLORS['text_gray']), halign='center')
        content.add_widget(info)
        
        btn = Button(text='Listeye Don', size_hint=(0.6, None), height=dp(40), pos_hint={'center_x': 0.5},
                    background_normal='', background_color=get_color_from_hex(COLORS['primary']))
        
        popup = Popup(title='', content=content, size_hint=(0.8, 0.45), separator_height=0)
        
        def go_list(x):
            popup.dismiss()
            self.manager.transition = SlideTransition(direction='right')
            self.manager.current = 'manual_link_list'
        
        btn.bind(on_press=go_list)
        content.add_widget(btn)
        popup.open()
    
    def go_back(self):
        cleanup_memory()
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'manual_link_list'


class CompleteScreen(BaseScreen):
    """Islem tamamlandi ekrani"""
    
    def on_enter(self):
        self.clear_widgets()
        Clock.schedule_once(lambda dt: self.build_ui(), 0.05)
    
    def build_ui(self):
        app = App.get_running_app()
        saved_files = getattr(app, 'saved_files', [])
        total_filtered = getattr(app, 'total_filtered', 0)
        total_channels = getattr(app, 'total_channels', 0)
        
        root = BoxLayout(orientation='vertical', padding=dp(25), spacing=dp(15))
        
        # Success icon with animation
        icon_box = BoxLayout(size_hint_y=0.2)
        icon = Label(
            text=ICONS['success'],
            font_size=dp(65),
            color=get_color_from_hex(COLORS['success'])
        )
        icon_box.add_widget(icon)
        root.add_widget(icon_box)
        
        # Animate icon
        anim = Animation(font_size=dp(75), duration=0.3) + Animation(font_size=dp(65), duration=0.3)
        anim.repeat = True
        Clock.schedule_once(lambda dt: anim.start(icon), 0.2)
        Clock.schedule_once(lambda dt: anim.cancel(icon), 3)
        
        # Title
        title = Label(
            text='Islem Tamamlandi!',
            font_size=dp(24),
            bold=True,
            color=get_color_from_hex(COLORS['text_white']),
            size_hint_y=None,
            height=dp(40)
        )
        root.add_widget(title)
        
        # Results card
        result_card = BoxLayout(orientation='vertical', padding=dp(18), spacing=dp(10), size_hint_y=None, height=dp(140))
        self._setup_card_bg(result_card)
        
        result_card.add_widget(Label(
            text=f'{ICONS["tv"]} {total_filtered} kanal filtrelendi',
            font_size=dp(16),
            color=get_color_from_hex(COLORS['success'])
        ))
        
        result_card.add_widget(Label(
            text=f'{ICONS["list"]} Toplam {total_channels} kanaldan',
            font_size=dp(12),
            color=get_color_from_hex(COLORS['text_gray'])
        ))
        
        result_card.add_widget(Label(
            text=f'{ICONS["file"]} {len(saved_files)} dosya olusturuldu',
            font_size=dp(14),
            color=get_color_from_hex(COLORS['info'])
        ))
        
        result_card.add_widget(Label(
            text=f'{ICONS["folder"]} Download klasorune kaydedildi',
            font_size=dp(11),
            color=get_color_from_hex(COLORS['text_dark'])
        ))
        
        root.add_widget(result_card)
        
        # Files list (if any)
        if saved_files:
            files_label = Label(
                text='Olusturulan Dosyalar:',
                font_size=dp(13),
                color=get_color_from_hex(COLORS['text_gray']),
                size_hint_y=None,
                height=dp(25)
            )
            root.add_widget(files_label)
            
            scroll = ScrollView(size_hint_y=None, height=dp(80))
            files_box = BoxLayout(orientation='vertical', spacing=dp(3), size_hint_y=None)
            files_box.bind(minimum_height=files_box.setter('height'))
            
            for f in saved_files[:5]:  # Max 5 dosya goster
                file_lbl = Label(
                    text=f'{ICONS["file"]} {f["filename"]} ({f["channels"]} kanal)',
                    font_size=dp(10),
                    color=get_color_from_hex(COLORS['text_light']),
                    size_hint_y=None,
                    height=dp(18),
                    halign='left'
                )
                file_lbl.bind(size=lambda w, s: setattr(w, 'text_size', s))
                files_box.add_widget(file_lbl)
            
            if len(saved_files) > 5:
                more_lbl = Label(
                    text=f'... ve {len(saved_files) - 5} dosya daha',
                    font_size=dp(10),
                    color=get_color_from_hex(COLORS['text_dark']),
                    size_hint_y=None,
                    height=dp(18)
                )
                files_box.add_widget(more_lbl)
            
            scroll.add_widget(files_box)
            root.add_widget(scroll)
        
        # Buttons
        btns = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None, height=dp(100))
        
        new_btn = Button(
            text=f'{ICONS["reload"]} Yeni Islem',
            font_size=dp(14),
            bold=True,
            size_hint_y=None,
            height=dp(45),
            background_normal='',
            background_color=get_color_from_hex(COLORS['primary'])
        )
        new_btn.bind(on_press=lambda x: self.go_to('auto_input'))
        btns.add_widget(new_btn)
        
        home_btn = Button(
            text=f'{ICONS["home"]} Ana Sayfa',
            font_size=dp(14),
            bold=True,
            size_hint_y=None,
            height=dp(45),
            background_normal='',
            background_color=get_color_from_hex(COLORS['bg_card'])
        )
        home_btn.bind(on_press=lambda x: self.go_to('welcome'))
        btns.add_widget(home_btn)
        
        root.add_widget(btns)
        
        self.add_widget(root)
    
    def _setup_card_bg(self, card):
        with card.canvas.before:
            Color(*get_color_from_hex(COLORS['bg_card']))
            card._bg = RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(15)])
        card.bind(pos=self._update_bg, size=self._update_bg)
    
    def _update_bg(self, widget, value):
        if hasattr(widget, '_bg'):
            widget._bg.pos = widget.pos
            widget._bg.size = widget.size
    
    def go_to(self, screen):
        cleanup_memory()
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = screen


# ==================== ANA UYGULAMA ====================

class IPTVEditorApp(App):
    """Ana uygulama"""
    
    def build(self):
        Window.clearcolor = get_color_from_hex(COLORS['bg_dark'])
        
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
        
        return sm
    
    def on_stop(self):
        cleanup_memory()


if __name__ == '__main__':
    IPTVEditorApp().run()
