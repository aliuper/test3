"""
IPTV Editor Pro v8.0
Emoji Icons + Custom Logo + Loading Percentage
"""

import os
import sys
import re
import gc
import traceback
import threading
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
from kivy.uix.image import Image, AsyncImage
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.properties import StringProperty, BooleanProperty, NumericProperty, ObjectProperty
from kivy.utils import get_color_from_hex
from kivy.animation import Animation
from kivy.graphics import Color, RoundedRectangle

import requests

# ==================== EMOJİ İKONLAR ====================
E = {
    # Genel
    'app': '📡',
    'tv': '📺',
    'channel': '📻',
    'signal': '📶',
    
    # Navigasyon
    'back': '◀️',
    'next': '▶️',
    'up': '🔼',
    'down': '🔽',
    'home': '🏠',
    'menu': '☰',
    
    # Aksiyonlar
    'check': '✅',
    'cross': '❌',
    'plus': '➕',
    'minus': '➖',
    'edit': '✏️',
    'save': '💾',
    'delete': '🗑️',
    'search': '🔍',
    'filter': '🔽',
    'refresh': '🔄',
    'download': '⬇️',
    'upload': '⬆️',
    'export': '📤',
    'import': '📥',
    
    # Medya
    'play': '▶️',
    'pause': '⏸️',
    'stop': '⏹️',
    'record': '⏺️',
    
    # Dosya
    'folder': '📁',
    'file': '📄',
    'link': '🔗',
    'list': '📋',
    
    # Durum
    'success': '✅',
    'error': '❌',
    'warning': '⚠️',
    'info': 'ℹ️',
    'loading': '⏳',
    'wait': '⌛',
    'clock': '🕐',
    'calendar': '📅',
    
    # Ayarlar
    'settings': '⚙️',
    'gear': '⚙️',
    'tool': '🔧',
    'key': '🔑',
    
    # Diğer
    'star': '⭐',
    'heart': '❤️',
    'fire': '🔥',
    'bolt': '⚡',
    'globe': '🌍',
    'flag': '🚩',
    'target': '🎯',
    'rocket': '🚀',
    'magic': '✨',
    'party': '🎉',
    'thumb_up': '👍',
    'thumb_down': '👎',
    'eye': '👁️',
    'lock': '🔒',
    'unlock': '🔓',
    
    # Ülke Bayrakları
    'tr': '🇹🇷',
    'de': '🇩🇪',
    'ro': '🇷🇴',
    'at': '🇦🇹',
    'fr': '🇫🇷',
    'it': '🇮🇹',
    'es': '🇪🇸',
    'uk': '🇬🇧',
    'us': '🇺🇸',
    'nl': '🇳🇱',
    'pl': '🇵🇱',
    'ru': '🇷🇺',
    'sa': '🇸🇦',
    'in': '🇮🇳',
    'pt': '🇵🇹',
    'gr': '🇬🇷',
    'al': '🇦🇱',
    'rs': '🇷🇸',
    'hr': '🇭🇷',
    'bg': '🇧🇬',
    'world': '🌍',
}

# ==================== RENKLER ====================
C = {
    'bg_dark': '#0d1b2a',
    'bg_medium': '#1b263b',
    'bg_card': '#22334a',
    'bg_light': '#2d3f58',
    'primary': '#7b68ee',
    'primary_dark': '#6354c9',
    'secondary': '#ff6b9d',
    'success': '#4ade80',
    'warning': '#fbbf24',
    'danger': '#f87171',
    'info': '#60a5fa',
    'white': '#ffffff',
    'light': '#e2e8f0',
    'gray': '#94a3b8',
    'dark': '#64748b',
}

# ==================== ÜLKELER ====================
COUNTRIES = {
    'turkey': {'name': 'Türkiye', 'flag': '🇹🇷', 'codes': ['tr', 'tur', 'turkey', 'turkiye', 'turk'], 'p': 1},
    'germany': {'name': 'Almanya', 'flag': '🇩🇪', 'codes': ['de', 'ger', 'germany', 'deutsch', 'almanya'], 'p': 2},
    'romania': {'name': 'Romanya', 'flag': '🇷🇴', 'codes': ['ro', 'rom', 'romania', 'romanya'], 'p': 3},
    'austria': {'name': 'Avusturya', 'flag': '🇦🇹', 'codes': ['at', 'aut', 'austria', 'avusturya'], 'p': 4},
    'france': {'name': 'Fransa', 'flag': '🇫🇷', 'codes': ['fr', 'fra', 'france', 'fransa'], 'p': 5},
    'italy': {'name': 'İtalya', 'flag': '🇮🇹', 'codes': ['it', 'ita', 'italy', 'italya'], 'p': 6},
    'spain': {'name': 'İspanya', 'flag': '🇪🇸', 'codes': ['es', 'esp', 'spain', 'ispanya'], 'p': 7},
    'uk': {'name': 'İngiltere', 'flag': '🇬🇧', 'codes': ['uk', 'gb', 'england', 'ingiltere'], 'p': 8},
    'usa': {'name': 'Amerika', 'flag': '🇺🇸', 'codes': ['us', 'usa', 'america', 'amerika'], 'p': 9},
    'netherlands': {'name': 'Hollanda', 'flag': '🇳🇱', 'codes': ['nl', 'netherlands', 'holland', 'hollanda'], 'p': 10},
    'poland': {'name': 'Polonya', 'flag': '🇵🇱', 'codes': ['pl', 'poland', 'polonya'], 'p': 11},
    'russia': {'name': 'Rusya', 'flag': '🇷🇺', 'codes': ['ru', 'rus', 'russia', 'rusya'], 'p': 12},
    'arabic': {'name': 'Arapça', 'flag': '🇸🇦', 'codes': ['ar', 'ara', 'arabic', 'arab'], 'p': 13},
    'india': {'name': 'Hindistan', 'flag': '🇮🇳', 'codes': ['in', 'ind', 'india', 'hindi'], 'p': 14},
    'portugal': {'name': 'Portekiz', 'flag': '🇵🇹', 'codes': ['pt', 'portugal', 'portekiz'], 'p': 15},
    'greece': {'name': 'Yunanistan', 'flag': '🇬🇷', 'codes': ['gr', 'greece', 'yunanistan'], 'p': 16},
    'albania': {'name': 'Arnavutluk', 'flag': '🇦🇱', 'codes': ['al', 'albania', 'arnavut'], 'p': 17},
    'serbia': {'name': 'Sırbistan', 'flag': '🇷🇸', 'codes': ['rs', 'serbia', 'sirbistan'], 'p': 18},
    'croatia': {'name': 'Hırvatistan', 'flag': '🇭🇷', 'codes': ['hr', 'croatia', 'hirvatistan'], 'p': 19},
    'bulgaria': {'name': 'Bulgaristan', 'flag': '🇧🇬', 'codes': ['bg', 'bulgaria', 'bulgaristan'], 'p': 20},
    'other': {'name': 'Diğer', 'flag': '🌍', 'codes': ['other', 'misc', 'xxx'], 'p': 99},
}

PRIORITY_COUNTRIES = ['turkey', 'germany', 'romania', 'austria']

FORMATS = {
    'm3u': {'name': 'M3U', 'ext': '.m3u'},
    'm3u8': {'name': 'M3U8 ⭐', 'ext': '.m3u8'},
    'txt': {'name': 'TXT', 'ext': '.txt'},
}

# ==================== KV ====================
KV = '''
#:import dp kivy.metrics.dp
#:import get_color_from_hex kivy.utils.get_color_from_hex

<BaseScreen>:
    canvas.before:
        Color:
            rgba: get_color_from_hex('#0d1b2a')
        Rectangle:
            pos: self.pos
            size: self.size

<AnimProgress>:
    canvas:
        Color:
            rgba: 0.12, 0.16, 0.23, 1
        RoundedRectangle:
            pos: self.x, self.center_y - dp(8)
            size: self.width, dp(16)
            radius: [dp(8)]
        Color:
            rgba: get_color_from_hex('#7b68ee')
        RoundedRectangle:
            pos: self.x + dp(2), self.center_y - dp(6)
            size: max(0, (self.width - dp(4)) * self.value / 100.0), dp(12)
            radius: [dp(6)]

<RV>:
    viewclass: 'GroupRow'
    RecycleBoxLayout:
        default_size: None, dp(68)
        default_size_hint: 1, None
        size_hint_y: None
        height: self.minimum_height
        orientation: 'vertical'
        spacing: dp(6)

<GroupRow>:
    orientation: 'horizontal'
    size_hint_y: None
    height: dp(68)
    padding: [dp(10), dp(6)]
    spacing: dp(10)
    
    canvas.before:
        Color:
            rgba: get_color_from_hex('#4ade80') if self.is_selected else get_color_from_hex('#22334a')
            a: 0.25 if self.is_selected else 1
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(10)]
    
    Label:
        text: '📺'
        font_size: dp(22)
        size_hint_x: None
        width: dp(38)
    
    BoxLayout:
        orientation: 'vertical'
        spacing: dp(2)
        Label:
            text: root.grp_name[:28] + ('...' if len(root.grp_name) > 28 else '')
            font_size: dp(13)
            color: get_color_from_hex('#ffffff')
            text_size: self.size
            halign: 'left'
            valign: 'middle'
        Label:
            text: str(root.ch_count) + ' kanal'
            font_size: dp(10)
            color: get_color_from_hex('#94a3b8')
            text_size: self.size
            halign: 'left'
            valign: 'middle'
    
    Button:
        size_hint: None, None
        size: dp(44), dp(44)
        text: '✅' if root.is_selected else '➕'
        font_size: dp(18)
        background_normal: ''
        background_color: get_color_from_hex('#4ade80') if root.is_selected else get_color_from_hex('#7b68ee')
        on_press: root.do_toggle()
'''

Builder.load_string(KV)

# ==================== HELPERS ====================

def get_download_path():
    try:
        from android.storage import primary_external_storage_path
        return os.path.join(primary_external_storage_path(), 'Download')
    except:
        return os.path.expanduser('~')


def get_icon_path():
    """icon.png yolunu bul"""
    paths = [
        '/sdcard/Download/icon.png',
        'icon.png',
        './icon.png',
        os.path.join(os.path.dirname(__file__), 'icon.png'),
    ]
    for p in paths:
        if os.path.exists(p):
            return p
    return None


def extract_expire(content, url):
    """Expire tarihini çıkar"""
    # URL'den
    try:
        params = parse_qs(urlparse(url).query)
        for k in ['exp', 'expires', 'expire', 'e']:
            if k in params:
                ts = int(params[k][0])
                if ts > 1e12:
                    ts //= 1000
                if ts > 1e9:
                    return datetime.fromtimestamp(ts).strftime('%d.%m.%Y')
    except:
        pass
    
    # URL'de timestamp
    m = re.search(r'/(\d{10})/', url)
    if m:
        try:
            ts = int(m.group(1))
            dt = datetime.fromtimestamp(ts)
            if 2024 <= dt.year <= 2030:
                return dt.strftime('%d.%m.%Y')
        except:
            pass
    
    # Content'ten
    patterns = [
        r'[Ee]xp(?:ire)?[:\s=]+(\d{10,13})',
        r'[Ee]xp(?:ire)?[:\s=]+["\']?(\d{1,2}[./-]\d{1,2}[./-]\d{2,4})',
        r'[Bb]itis[:\s=]+["\']?(\d{1,2}[./-]\d{1,2}[./-]\d{2,4})',
    ]
    for p in patterns:
        m = re.search(p, content[:3000], re.I)
        if m:
            v = m.group(1)
            if v.isdigit() and len(v) >= 10:
                try:
                    ts = int(v)
                    if ts > 1e12:
                        ts //= 1000
                    dt = datetime.fromtimestamp(ts)
                    if 2024 <= dt.year <= 2030:
                        return dt.strftime('%d.%m.%Y')
                except:
                    pass
            else:
                v = v.replace('-', '.').replace('/', '.')
                parts = v.split('.')
                if len(parts) == 3:
                    try:
                        if len(parts[2]) == 2:
                            parts[2] = '20' + parts[2]
                        if len(parts[0]) == 4:
                            dt = datetime(int(parts[0]), int(parts[1]), int(parts[2]))
                        else:
                            dt = datetime(int(parts[2]), int(parts[1]), int(parts[0]))
                        if 2024 <= dt.year <= 2030:
                            return dt.strftime('%d.%m.%Y')
                    except:
                        pass
    
    return 'Bilinmiyor'


def parse_m3u(content, url=''):
    """M3U parse et"""
    channels = []
    groups = {}
    expire = extract_expire(content, url)
    
    lines = content.split('\n')
    current = None
    
    grp_re = re.compile(r'group-title="([^"]*)"')
    logo_re = re.compile(r'tvg-logo="([^"]*)"')
    name_re = re.compile(r',([^,]+)$')
    
    for line in lines:
        line = line.strip()
        if line.startswith('#EXTINF:'):
            current = {'name': '', 'group': 'Diğer', 'logo': '', 'url': ''}
            m = grp_re.search(line)
            if m and m.group(1):
                current['group'] = m.group(1).strip()
            m = logo_re.search(line)
            if m:
                current['logo'] = m.group(1)
            m = name_re.search(line)
            if m:
                current['name'] = m.group(1).strip()
        elif current and line.startswith(('http', 'rtmp', 'rtsp')):
            current['url'] = line
            channels.append(current)
            grp = current['group']
            if grp not in groups:
                groups[grp] = {'channels': [], 'logo': current['logo'], 'country': detect_country(grp)}
            groups[grp]['channels'].append(current)
            current = None
    
    return channels, groups, expire


@lru_cache(maxsize=512)
def detect_country(grp):
    if not grp:
        return 'other'
    g = grp.lower()
    for cid, cd in COUNTRIES.items():
        for code in cd['codes']:
            if g.startswith(code + ' ') or g.startswith(code + '-') or g.startswith(code + '_'):
                return cid
            if g.endswith(' ' + code) or g.endswith('-' + code):
                return cid
            if g == code:
                return cid
            if re.search(rf'[\s\-_]({re.escape(code)})[\s\-_]', ' ' + g + ' '):
                return cid
    return 'other'


def gen_m3u(channels, fmt='m3u'):
    out = '#EXTM3U\n'
    for ch in channels:
        out += '#EXTINF:-1'
        if ch.get('logo'):
            out += f' tvg-logo="{ch["logo"]}"'
        if ch.get('group'):
            out += f' group-title="{ch["group"]}"'
        out += f',{ch.get("name", "Channel")}\n{ch.get("url", "")}\n'
    return out


def test_quick(url, timeout=8):
    try:
        r = requests.head(url, timeout=timeout, headers={'User-Agent': 'VLC/3.0'}, allow_redirects=True)
        return r.status_code == 200, f"HTTP {r.status_code}"
    except requests.exceptions.Timeout:
        return False, "Timeout"
    except:
        return False, "Hata"


def test_deep(url, timeout=15):
    """Gerçek derin test - M3U indir ve kanalları test et"""
    try:
        r = requests.get(url, timeout=timeout, headers={'User-Agent': 'VLC/3.0'})
        if r.status_code != 200:
            return False, f"HTTP {r.status_code}"
        
        content = r.text
        if len(content) < 100:
            return False, "Boş içerik"
        
        if '#EXTINF' not in content:
            return test_stream(url)
        
        chs, grps, exp = parse_m3u(content, url)
        if not chs:
            return False, "Kanal yok"
        
        # 3 kanal test et
        import random
        test_chs = random.sample(chs, min(3, len(chs)))
        working = sum(1 for ch in test_chs if test_stream(ch.get('url', ''))[0])
        
        if working > 0:
            return True, f"{len(chs)} kanal, {working}/3 aktif"
        elif len(chs) >= 5:
            return True, f"{len(chs)} kanal bulundu"
        return False, "Kanallar ölü"
    except requests.exceptions.Timeout:
        return False, "Timeout"
    except:
        return False, "Hata"


def test_stream(url, timeout=8):
    try:
        r = requests.get(url, timeout=timeout, headers={'User-Agent': 'VLC/3.0'}, stream=True)
        if r.status_code != 200:
            return False, f"HTTP {r.status_code}"
        total = 0
        for chunk in r.iter_content(4096):
            total += len(chunk)
            if total > 16384:
                break
        r.close()
        return total > 1024, "Aktif" if total > 1024 else "Veri yok"
    except:
        return False, "Hata"


def short_domain(url):
    try:
        d = urlparse(url).netloc
        if d.startswith('www.'):
            d = d[4:]
        parts = d.split('.')
        if len(parts) > 2:
            d = '.'.join(parts[-2:])
        return d[:18]
    except:
        return 'iptv'


def cleanup():
    gc.collect()


# ==================== WIDGETS ====================

class BaseScreen(Screen):
    pass


class AnimProgress(Widget):
    value = NumericProperty(0)
    
    def set_value(self, v, anim=True):
        if anim:
            Animation(value=v, duration=0.3).start(self)
        else:
            self.value = v


class GroupRow(RecycleDataViewBehavior, BoxLayout):
    index = None
    is_selected = BooleanProperty(False)
    grp_name = StringProperty('')
    ch_count = NumericProperty(0)
    callback = ObjectProperty(None)
    
    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        self.grp_name = data.get('grp_name', '')
        self.ch_count = data.get('ch_count', 0)
        self.is_selected = data.get('is_selected', False)
        self.callback = data.get('callback', None)
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
        root = BoxLayout(orientation='vertical', padding=dp(25), spacing=dp(15))
        
        # Header with Logo
        header = BoxLayout(orientation='vertical', size_hint_y=0.32, spacing=dp(8))
        
        # Logo from icon.png or emoji
        logo_box = BoxLayout(size_hint_y=None, height=dp(80))
        icon_path = get_icon_path()
        if icon_path:
            logo = Image(source=icon_path, size_hint=(None, None), size=(dp(70), dp(70)), pos_hint={'center_x': 0.5})
        else:
            logo = Label(text='📡', font_size=dp(55))
        logo_box.add_widget(logo)
        header.add_widget(logo_box)
        
        header.add_widget(Label(text='IPTV Editor Pro', font_size=dp(26), bold=True, color=get_color_from_hex(C['white'])))
        header.add_widget(Label(text='v8.0 • Gelişmiş IPTV Düzenleyici', font_size=dp(12), color=get_color_from_hex(C['gray'])))
        root.add_widget(header)
        
        # Cards
        cards = BoxLayout(orientation='vertical', spacing=dp(12), size_hint_y=0.55)
        
        # Manual
        m_card = self._card(
            f'{E["edit"]} Manuel Düzenleme',
            'URL girin, kanalları seçin, kaydedin',
            f'{E["next"]} Başla',
            C['primary'],
            lambda: self.go('manual_input')
        )
        cards.add_widget(m_card)
        
        # Auto
        a_card = self._card(
            f'{E["gear"]} Otomatik Düzenleme',
            'Toplu test, ülke filtresi, ayrı dosyalar',
            f'{E["next"]} Başla',
            C['secondary'],
            lambda: self.go('auto_input')
        )
        cards.add_widget(a_card)
        
        root.add_widget(cards)
        
        # Footer
        root.add_widget(Label(text=f'{E["star"]} Gelişmiş Test + Doğru Expire', font_size=dp(10), color=get_color_from_hex(C['dark']), size_hint_y=0.08))
        
        self.add_widget(root)
    
    def _card(self, title, desc, btn_text, btn_color, callback):
        card = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(8))
        with card.canvas.before:
            Color(*get_color_from_hex(C['bg_card']))
            card._bg = RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(12)])
        card.bind(pos=self._upd, size=self._upd)
        
        card.add_widget(Label(text=title, font_size=dp(16), bold=True, color=get_color_from_hex(C['white']), size_hint_y=None, height=dp(28)))
        card.add_widget(Label(text=desc, font_size=dp(11), color=get_color_from_hex(C['gray']), size_hint_y=None, height=dp(22)))
        
        btn = Button(text=btn_text, font_size=dp(14), bold=True, size_hint=(0.5, None), height=dp(38), pos_hint={'center_x': 0.5}, background_normal='', background_color=get_color_from_hex(btn_color))
        btn.bind(on_press=lambda x: callback())
        card.add_widget(btn)
        return card
    
    def _upd(self, w, v):
        if hasattr(w, '_bg'):
            w._bg.pos = w.pos
            w._bg.size = w.size
    
    def go(self, s):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = s


class ManualInputScreen(BaseScreen):
    def on_enter(self):
        self.clear_widgets()
        self.fmt = 'm3u8'
        Clock.schedule_once(lambda dt: self.build(), 0.05)
    
    def build(self):
        root = BoxLayout(orientation='vertical', padding=dp(18), spacing=dp(12))
        
        # Top
        top = BoxLayout(size_hint_y=None, height=dp(45), spacing=dp(10))
        back = Button(text=E['back'], size_hint=(None, None), size=(dp(45), dp(40)), font_size=dp(18), background_normal='', background_color=get_color_from_hex(C['bg_card']))
        back.bind(on_press=lambda x: self.go_back())
        top.add_widget(back)
        top.add_widget(Label(text=f'{E["edit"]} Manuel Düzenleme', font_size=dp(16), bold=True, color=get_color_from_hex(C['white'])))
        root.add_widget(top)
        
        # URL Card
        url_card = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(8), size_hint_y=None, height=dp(115))
        self._bg(url_card)
        url_card.add_widget(Label(text=f'{E["link"]} Playlist URL', font_size=dp(12), color=get_color_from_hex(C['gray']), size_hint_y=None, height=dp(20), halign='left'))
        self.url_inp = TextInput(hint_text='https://example.com/playlist.m3u', multiline=False, font_size=dp(13), background_color=get_color_from_hex(C['bg_medium']), foreground_color=get_color_from_hex(C['white']), size_hint_y=None, height=dp(45))
        url_card.add_widget(self.url_inp)
        root.add_widget(url_card)
        
        # Format
        fmt_card = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(8), size_hint_y=None, height=dp(95))
        self._bg(fmt_card)
        fmt_card.add_widget(Label(text=f'{E["file"]} Çıktı Formatı', font_size=dp(12), color=get_color_from_hex(C['gray']), size_hint_y=None, height=dp(20)))
        
        fmt_box = BoxLayout(spacing=dp(8), size_hint_y=None, height=dp(40))
        self.fmt_btns = {}
        for fid, fd in FORMATS.items():
            btn = ToggleButton(text=fd['name'], group='fmt', state='down' if fid == 'm3u8' else 'normal', font_size=dp(12), background_normal='', background_color=get_color_from_hex(C['primary']) if fid == 'm3u8' else get_color_from_hex(C['bg_light']))
            btn.fid = fid
            btn.bind(on_press=self.on_fmt)
            self.fmt_btns[fid] = btn
            fmt_box.add_widget(btn)
        fmt_card.add_widget(fmt_box)
        root.add_widget(fmt_card)
        
        root.add_widget(Label())
        
        # Load btn
        load = Button(text=f'{E["download"]} Kanalları Yükle', font_size=dp(15), bold=True, size_hint_y=None, height=dp(50), background_normal='', background_color=get_color_from_hex(C['success']))
        load.bind(on_press=self.load)
        root.add_widget(load)
        
        self.add_widget(root)
    
    def _bg(self, w):
        with w.canvas.before:
            Color(*get_color_from_hex(C['bg_card']))
            w._bg = RoundedRectangle(pos=w.pos, size=w.size, radius=[dp(10)])
        w.bind(pos=self._upd, size=self._upd)
    
    def _upd(self, w, v):
        if hasattr(w, '_bg'):
            w._bg.pos = w.pos
            w._bg.size = w.size
    
    def on_fmt(self, btn):
        self.fmt = btn.fid
        for fid, b in self.fmt_btns.items():
            b.background_color = get_color_from_hex(C['primary']) if fid == self.fmt else get_color_from_hex(C['bg_light'])
    
    def load(self, *args):
        url = self.url_inp.text.strip()
        if not url:
            self.popup(E['warning'], 'URL girin!', 'warning')
            return
        if not url.startswith('http'):
            self.popup(E['error'], 'Geçersiz URL!', 'danger')
            return
        
        self.show_loading()
        threading.Thread(target=self._load, args=(url,), daemon=True).start()
    
    def _load(self, url):
        try:
            # İlerleme göster
            Clock.schedule_once(lambda dt: self.update_loading(10, 'Bağlanılıyor...'))
            
            r = requests.get(url, timeout=30, headers={'User-Agent': 'Mozilla/5.0'}, stream=True)
            
            Clock.schedule_once(lambda dt: self.update_loading(30, 'İndiriliyor...'))
            
            content = r.text
            
            Clock.schedule_once(lambda dt: self.update_loading(60, 'Ayrıştırılıyor...'))
            
            chs, grps, exp = parse_m3u(content, url)
            
            Clock.schedule_once(lambda dt: self.update_loading(90, 'Gruplar oluşturuluyor...'))
            
            if not chs:
                Clock.schedule_once(lambda dt: self._err('Kanal bulunamadı!'))
                return
            
            Clock.schedule_once(lambda dt: self.update_loading(100, 'Tamamlandı!'))
            Clock.schedule_once(lambda dt: self._ok(chs, grps, exp, url), 0.3)
        except Exception as e:
            Clock.schedule_once(lambda dt: self._err(str(e)[:40]))
    
    def _ok(self, chs, grps, exp, url):
        self.hide_loading()
        app = App.get_running_app()
        app.channels = chs
        app.groups = grps
        app.expire = exp
        app.src_url = url
        app.fmt = self.fmt
        app.mode = 'manual'
        cleanup()
        self.manager.current = 'channel_list'
    
    def _err(self, msg):
        self.hide_loading()
        self.popup(E['error'], msg, 'danger')
    
    def show_loading(self):
        c = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(12))
        
        self.load_icon = Label(text=E['loading'], font_size=dp(40))
        c.add_widget(self.load_icon)
        
        self.load_msg = Label(text='Başlatılıyor...', font_size=dp(13), color=get_color_from_hex(C['white']))
        c.add_widget(self.load_msg)
        
        self.load_prog = AnimProgress(size_hint_y=None, height=dp(20))
        c.add_widget(self.load_prog)
        
        self.load_pct = Label(text='%0', font_size=dp(20), bold=True, color=get_color_from_hex(C['primary']))
        c.add_widget(self.load_pct)
        
        self._pop = Popup(title='', content=c, size_hint=(0.75, 0.38), auto_dismiss=False, separator_height=0)
        self._pop.open()
    
    def update_loading(self, pct, msg):
        if hasattr(self, 'load_prog'):
            self.load_prog.set_value(pct)
            self.load_pct.text = f'%{int(pct)}'
            self.load_msg.text = msg
    
    def hide_loading(self):
        if hasattr(self, '_pop'):
            self._pop.dismiss()
    
    def popup(self, icon, msg, typ='info'):
        colors = {'info': C['info'], 'success': C['success'], 'warning': C['warning'], 'danger': C['danger']}
        c = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        c.add_widget(Label(text=icon, font_size=dp(40)))
        c.add_widget(Label(text=msg, font_size=dp(13), color=get_color_from_hex(C['white']), halign='center'))
        btn = Button(text='Tamam', size_hint=(0.5, None), height=dp(40), pos_hint={'center_x': 0.5}, background_normal='', background_color=get_color_from_hex(colors.get(typ, C['info'])))
        p = Popup(title='', content=c, size_hint=(0.8, 0.38), separator_height=0)
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
        grps = getattr(app, 'groups', {})
        chs = getattr(app, 'channels', [])
        exp = getattr(app, 'expire', 'Bilinmiyor')
        
        root = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(8))
        
        # Top
        top = BoxLayout(size_hint_y=None, height=dp(45), spacing=dp(8))
        back = Button(text=E['back'], size_hint=(None, None), size=(dp(45), dp(40)), font_size=dp(18), background_normal='', background_color=get_color_from_hex(C['bg_card']))
        back.bind(on_press=lambda x: self.go_back())
        top.add_widget(back)
        top.add_widget(Label(text=f'{E["tv"]} Kanal Grupları', font_size=dp(15), bold=True, color=get_color_from_hex(C['white'])))
        root.add_widget(top)
        
        # Info
        info = BoxLayout(size_hint_y=None, height=dp(42), orientation='vertical')
        info.add_widget(Label(text=f'{E["list"]} {len(grps)} grup • {len(chs)} kanal', font_size=dp(11), color=get_color_from_hex(C['gray'])))
        info.add_widget(Label(text=f'{E["calendar"]} Bitiş: {exp}', font_size=dp(11), color=get_color_from_hex(C['warning'])))
        root.add_widget(info)
        
        # Selection
        self.sel_lbl = Label(text=f'{E["check"]} Seçilen: 0 grup (0 kanal)', font_size=dp(11), color=get_color_from_hex(C['success']), size_hint_y=None, height=dp(20))
        root.add_widget(self.sel_lbl)
        
        # RV
        self.rv = RV()
        self.rv_data = []
        for gn, gd in sorted(grps.items()):
            self.rv_data.append({'grp_name': gn, 'ch_count': len(gd['channels']), 'is_selected': False, 'callback': self.on_sel})
        self.rv.data = self.rv_data
        root.add_widget(self.rv)
        
        # Bottom
        btm = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
        sel_all = Button(text=f'{E["check"]} Tümünü Seç', font_size=dp(13), bold=True, background_normal='', background_color=get_color_from_hex(C['primary']))
        sel_all.bind(on_press=self.sel_all)
        btm.add_widget(sel_all)
        exp_btn = Button(text=f'{E["export"]} Dışa Aktar', font_size=dp(13), bold=True, background_normal='', background_color=get_color_from_hex(C['success']))
        exp_btn.bind(on_press=self.export)
        btm.add_widget(exp_btn)
        root.add_widget(btm)
        
        self.add_widget(root)
    
    def on_sel(self, gn, sel, idx):
        self.rv_data[idx]['is_selected'] = sel
        if sel:
            self.selected.add(gn)
        else:
            self.selected.discard(gn)
        
        app = App.get_running_app()
        grps = getattr(app, 'groups', {})
        total = sum(len(grps[g]['channels']) for g in self.selected if g in grps)
        self.sel_lbl.text = f'{E["check"]} Seçilen: {len(self.selected)} grup ({total} kanal)'
    
    def sel_all(self, *args):
        app = App.get_running_app()
        grps = getattr(app, 'groups', {})
        for i, d in enumerate(self.rv_data):
            d['is_selected'] = True
            self.selected.add(d['grp_name'])
        self.rv.data = self.rv_data
        self.rv.refresh_from_data()
        total = sum(len(grps[g]['channels']) for g in self.selected if g in grps)
        self.sel_lbl.text = f'{E["check"]} Seçilen: {len(self.selected)} grup ({total} kanal)'
    
    def export(self, *args):
        if not self.selected:
            self.popup(E['warning'], 'Grup seçin!', 'warning')
            return
        
        app = App.get_running_app()
        grps = getattr(app, 'groups', {})
        fmt = getattr(app, 'fmt', 'm3u8')
        exp = getattr(app, 'expire', '')
        url = getattr(app, 'src_url', '')
        
        chs = []
        for gn in self.selected:
            if gn in grps:
                chs.extend(grps[gn]['channels'])
        
        content = gen_m3u(chs, fmt)
        
        path = get_download_path()
        domain = short_domain(url)
        exp_str = exp.replace('.', '') if exp != 'Bilinmiyor' else datetime.now().strftime('%d%m%Y')
        ext = FORMATS.get(fmt, {}).get('ext', '.m3u')
        fname = f'bitis{exp_str}_{domain}{ext}'
        fpath = os.path.join(path, fname)
        
        try:
            with open(fpath, 'w', encoding='utf-8') as f:
                f.write(content)
            self.popup(E['success'], f'{len(chs)} kanal kaydedildi!\n\n{E["file"]} {fname}', 'success')
        except Exception as e:
            self.popup(E['error'], str(e)[:40], 'danger')
        cleanup()
    
    def popup(self, icon, msg, typ='info'):
        colors = {'info': C['info'], 'success': C['success'], 'warning': C['warning'], 'danger': C['danger']}
        c = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(12))
        c.add_widget(Label(text=icon, font_size=dp(40)))
        c.add_widget(Label(text=msg, font_size=dp(12), color=get_color_from_hex(C['white']), halign='center'))
        btn = Button(text='Tamam', size_hint=(0.5, None), height=dp(40), pos_hint={'center_x': 0.5}, background_normal='', background_color=get_color_from_hex(colors.get(typ, C['info'])))
        p = Popup(title='', content=c, size_hint=(0.85, 0.4), separator_height=0)
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
        self.mode = 'deep'
        Clock.schedule_once(lambda dt: self.build(), 0.05)
    
    def build(self):
        root = BoxLayout(orientation='vertical', padding=dp(18), spacing=dp(12))
        
        # Top
        top = BoxLayout(size_hint_y=None, height=dp(45), spacing=dp(10))
        back = Button(text=E['back'], size_hint=(None, None), size=(dp(45), dp(40)), font_size=dp(18), background_normal='', background_color=get_color_from_hex(C['bg_card']))
        back.bind(on_press=lambda x: self.go_back())
        top.add_widget(back)
        top.add_widget(Label(text=f'{E["gear"]} Otomatik Düzenleme', font_size=dp(16), bold=True, color=get_color_from_hex(C['white'])))
        root.add_widget(top)
        
        root.add_widget(Label(text='Her satıra bir IPTV linki girin', font_size=dp(11), color=get_color_from_hex(C['gray']), size_hint_y=None, height=dp(20)))
        
        # Input
        inp_card = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(5))
        self._bg(inp_card)
        self.links_inp = TextInput(hint_text='https://example1.com/get.php?...\nhttps://example2.com/get.php?...', multiline=True, font_size=dp(11), background_color=get_color_from_hex(C['bg_medium']), foreground_color=get_color_from_hex(C['white']))
        inp_card.add_widget(self.links_inp)
        root.add_widget(inp_card)
        
        # Mode
        mode_card = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(6), size_hint_y=None, height=dp(90))
        self._bg(mode_card)
        mode_card.add_widget(Label(text=f'{E["settings"]} Test Yöntemi', font_size=dp(11), color=get_color_from_hex(C['gray']), size_hint_y=None, height=dp(18)))
        
        mode_box = BoxLayout(spacing=dp(8), size_hint_y=None, height=dp(42))
        self.quick_btn = ToggleButton(text=f'{E["bolt"]} Hızlı', group='mode', state='normal', font_size=dp(12), background_normal='', background_color=get_color_from_hex(C['bg_light']))
        self.quick_btn.bind(on_press=lambda x: self.set_mode('quick'))
        mode_box.add_widget(self.quick_btn)
        self.deep_btn = ToggleButton(text=f'{E["search"]} Derin ⭐', group='mode', state='down', font_size=dp(12), background_normal='', background_color=get_color_from_hex(C['primary']))
        self.deep_btn.bind(on_press=lambda x: self.set_mode('deep'))
        mode_box.add_widget(self.deep_btn)
        mode_card.add_widget(mode_box)
        root.add_widget(mode_card)
        
        # Start
        start = Button(text=f'{E["play"]} Test Başlat', font_size=dp(15), bold=True, size_hint_y=None, height=dp(50), background_normal='', background_color=get_color_from_hex(C['success']))
        start.bind(on_press=self.start)
        root.add_widget(start)
        
        self.add_widget(root)
    
    def _bg(self, w):
        with w.canvas.before:
            Color(*get_color_from_hex(C['bg_card']))
            w._bg = RoundedRectangle(pos=w.pos, size=w.size, radius=[dp(10)])
        w.bind(pos=self._upd, size=self._upd)
    
    def _upd(self, w, v):
        if hasattr(w, '_bg'):
            w._bg.pos = w.pos
            w._bg.size = w.size
    
    def set_mode(self, m):
        self.mode = m
        self.quick_btn.background_color = get_color_from_hex(C['primary']) if m == 'quick' else get_color_from_hex(C['bg_light'])
        self.deep_btn.background_color = get_color_from_hex(C['primary']) if m == 'deep' else get_color_from_hex(C['bg_light'])
    
    def start(self, *args):
        txt = self.links_inp.text.strip()
        if not txt:
            self.popup(E['warning'], 'Link girin!', 'warning')
            return
        
        links = [l.strip() for l in txt.split('\n') if l.strip().startswith('http')]
        if not links:
            self.popup(E['error'], 'Geçerli link yok!', 'danger')
            return
        
        app = App.get_running_app()
        app.test_links = links
        app.test_mode = self.mode
        self.manager.current = 'testing'
    
    def popup(self, icon, msg, typ='info'):
        colors = {'warning': C['warning'], 'danger': C['danger']}
        c = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        c.add_widget(Label(text=icon, font_size=dp(40)))
        c.add_widget(Label(text=msg, font_size=dp(13), color=get_color_from_hex(C['white'])))
        btn = Button(text='Tamam', size_hint=(0.5, None), height=dp(40), pos_hint={'center_x': 0.5}, background_normal='', background_color=get_color_from_hex(colors.get(typ, C['info'])))
        p = Popup(title='', content=c, size_hint=(0.8, 0.38), separator_height=0)
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
        root = BoxLayout(orientation='vertical', padding=dp(18), spacing=dp(12))
        
        root.add_widget(Label(text=f'{E["search"]} Test Ediliyor...', font_size=dp(20), bold=True, color=get_color_from_hex(C['white']), size_hint_y=None, height=dp(40)))
        
        # Progress
        prog_card = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(8), size_hint_y=None, height=dp(130))
        self._bg(prog_card)
        
        self.prog_lbl = Label(text='Hazırlanıyor...', font_size=dp(14), color=get_color_from_hex(C['white']), size_hint_y=None, height=dp(22))
        prog_card.add_widget(self.prog_lbl)
        
        self.prog_bar = AnimProgress(size_hint_y=None, height=dp(22))
        prog_card.add_widget(self.prog_bar)
        
        self.pct_lbl = Label(text='%0', font_size=dp(24), bold=True, color=get_color_from_hex(C['primary']), size_hint_y=None, height=dp(32))
        prog_card.add_widget(self.pct_lbl)
        
        self.stats_lbl = Label(text=f'{E["success"]} 0 Çalışıyor  {E["cross"]} 0 Başarısız', font_size=dp(11), color=get_color_from_hex(C['gray']), size_hint_y=None, height=dp(20))
        prog_card.add_widget(self.stats_lbl)
        
        root.add_widget(prog_card)
        
        # Log
        log_card = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(4))
        self._bg(log_card)
        
        log_card.add_widget(Label(text=f'{E["list"]} Test Günlüğü', font_size=dp(11), color=get_color_from_hex(C['gray']), size_hint_y=None, height=dp(18), halign='left'))
        
        scroll = ScrollView()
        self.log_box = BoxLayout(orientation='vertical', spacing=dp(2), size_hint_y=None)
        self.log_box.bind(minimum_height=self.log_box.setter('height'))
        scroll.add_widget(self.log_box)
        log_card.add_widget(scroll)
        
        root.add_widget(log_card)
        
        # Action
        self.act_btn = Button(text=f'{E["cross"]} İptal', font_size=dp(14), bold=True, size_hint_y=None, height=dp(48), background_normal='', background_color=get_color_from_hex(C['danger']))
        self.act_btn.bind(on_press=self.on_action)
        root.add_widget(self.act_btn)
        
        self.add_widget(root)
    
    def _bg(self, w):
        with w.canvas.before:
            Color(*get_color_from_hex(C['bg_card']))
            w._bg = RoundedRectangle(pos=w.pos, size=w.size, radius=[dp(10)])
        w.bind(pos=self._upd, size=self._upd)
    
    def _upd(self, w, v):
        if hasattr(w, '_bg'):
            w._bg.pos = w.pos
            w._bg.size = w.size
    
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
            Clock.schedule_once(lambda dt, d=domain: self.log(f'{E["loading"]} Test: {d}', 'testing'))
            
            if mode == 'quick':
                ok, msg = test_quick(link)
            else:
                ok, msg = test_deep(link)
            
            if ok:
                self.working.append(link)
                Clock.schedule_once(lambda dt, d=domain, m=msg: self.log(f'{E["success"]} {d}: {m}', 'success'))
            else:
                self.failed.append({'link': link, 'reason': msg})
                Clock.schedule_once(lambda dt, d=domain, m=msg: self.log(f'{E["cross"]} {d}: {m}', 'error'))
            
            pct = ((i + 1) / total) * 100
            Clock.schedule_once(lambda dt, p=pct, c=i+1, t=total: self.upd_prog(p, c, t))
        
        Clock.schedule_once(lambda dt: self.done())
    
    def log(self, txt, typ):
        colors = {'testing': C['gray'], 'success': C['success'], 'error': C['danger']}
        lbl = Label(text=txt, font_size=dp(10), color=get_color_from_hex(colors.get(typ, C['gray'])), size_hint_y=None, height=dp(18), halign='left')
        lbl.bind(size=lambda w, s: setattr(w, 'text_size', s))
        self.log_box.add_widget(lbl)
        if len(self.log_box.children) > 40:
            self.log_box.remove_widget(self.log_box.children[-1])
    
    def upd_prog(self, pct, curr, total):
        self.prog_bar.set_value(pct)
        self.prog_lbl.text = f'Test: {curr}/{total}'
        self.pct_lbl.text = f'%{int(pct)}'
        self.stats_lbl.text = f'{E["success"]} {len(self.working)} Çalışıyor  {E["cross"]} {len(self.failed)} Başarısız'
    
    def done(self):
        self.testing = False
        self.prog_lbl.text = f'{E["success"]} Test Tamamlandı!'
        self.pct_lbl.text = '%100'
        self.act_btn.text = f'{E["next"]} Devam'
        self.act_btn.background_color = get_color_from_hex(C['success'])
        
        app = App.get_running_app()
        app.working_links = self.working
        app.failed_links = self.failed
    
    def on_action(self, *args):
        if 'İptal' in self.act_btn.text:
            self.testing = False
            self.manager.transition = SlideTransition(direction='right')
            self.manager.current = 'auto_input'
        else:
            if not self.working:
                c = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
                c.add_widget(Label(text=E['warning'], font_size=dp(40)))
                c.add_widget(Label(text='Çalışan link yok!', font_size=dp(14), color=get_color_from_hex(C['white'])))
                btn = Button(text='Geri', size_hint=(0.5, None), height=dp(40), pos_hint={'center_x': 0.5}, background_normal='', background_color=get_color_from_hex(C['primary']))
                p = Popup(title='', content=c, size_hint=(0.75, 0.35), separator_height=0)
                def go(x):
                    p.dismiss()
                    self.manager.transition = SlideTransition(direction='right')
                    self.manager.current = 'auto_input'
                btn.bind(on_press=go)
                c.add_widget(btn)
                p.open()
            else:
                cleanup()
                self.manager.current = 'auto_result'


class AutoResultScreen(BaseScreen):
    def on_enter(self):
        self.clear_widgets()
        Clock.schedule_once(lambda dt: self.build(), 0.05)
    
    def build(self):
        app = App.get_running_app()
        w = len(getattr(app, 'working_links', []))
        f = len(getattr(app, 'failed_links', []))
        
        root = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        
        root.add_widget(Label(text=f'{E["success"]} Test Tamamlandı!', font_size=dp(20), bold=True, color=get_color_from_hex(C['white']), size_hint_y=None, height=dp(35)))
        
        # Results
        res_card = BoxLayout(orientation='horizontal', padding=dp(20), spacing=dp(20), size_hint_y=None, height=dp(95))
        self._bg(res_card)
        
        w_box = BoxLayout(orientation='vertical')
        w_box.add_widget(Label(text=E['success'], font_size=dp(28)))
        w_box.add_widget(Label(text=str(w), font_size=dp(24), bold=True, color=get_color_from_hex(C['success'])))
        w_box.add_widget(Label(text='Çalışıyor', font_size=dp(10), color=get_color_from_hex(C['gray'])))
        res_card.add_widget(w_box)
        
        f_box = BoxLayout(orientation='vertical')
        f_box.add_widget(Label(text=E['cross'], font_size=dp(28)))
        f_box.add_widget(Label(text=str(f), font_size=dp(24), bold=True, color=get_color_from_hex(C['danger'])))
        f_box.add_widget(Label(text='Başarısız', font_size=dp(10), color=get_color_from_hex(C['gray'])))
        res_card.add_widget(f_box)
        
        root.add_widget(res_card)
        
        root.add_widget(Label(text='Nasıl düzenlemek istersiniz?', font_size=dp(13), color=get_color_from_hex(C['light']), size_hint_y=None, height=dp(25)))
        
        # Options
        opts = BoxLayout(orientation='vertical', spacing=dp(10))
        
        # Auto
        auto_card = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(6), size_hint_y=None, height=dp(105))
        self._bg(auto_card)
        auto_card.add_widget(Label(text=f'{E["gear"]} Otomatik Düzenleme', font_size=dp(14), bold=True, color=get_color_from_hex(C['white']), size_hint_y=None, height=dp(25)))
        auto_card.add_widget(Label(text='Ülke seç, AYRI dosyalar oluştur', font_size=dp(10), color=get_color_from_hex(C['gray']), size_hint_y=None, height=dp(18)))
        auto_btn = Button(text=f'{E["next"]} Otomatik', size_hint=(0.55, None), height=dp(36), pos_hint={'center_x': 0.5}, background_normal='', background_color=get_color_from_hex(C['primary']))
        auto_btn.bind(on_press=lambda x: self.go('country_select'))
        auto_card.add_widget(auto_btn)
        opts.add_widget(auto_card)
        
        # Manual
        man_card = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(6), size_hint_y=None, height=dp(105))
        self._bg(man_card)
        man_card.add_widget(Label(text=f'{E["edit"]} Manuel Düzenleme', font_size=dp(14), bold=True, color=get_color_from_hex(C['white']), size_hint_y=None, height=dp(25)))
        man_card.add_widget(Label(text='Her linki tek tek düzenle', font_size=dp(10), color=get_color_from_hex(C['gray']), size_hint_y=None, height=dp(18)))
        man_btn = Button(text=f'{E["next"]} Manuel', size_hint=(0.55, None), height=dp(36), pos_hint={'center_x': 0.5}, background_normal='', background_color=get_color_from_hex(C['secondary']))
        man_btn.bind(on_press=lambda x: self.go('manual_link_list'))
        man_card.add_widget(man_btn)
        opts.add_widget(man_card)
        
        root.add_widget(opts)
        
        back = Button(text=f'{E["back"]} Geri', size_hint_y=None, height=dp(40), background_normal='', background_color=get_color_from_hex(C['bg_card']))
        back.bind(on_press=lambda x: self.go_back())
        root.add_widget(back)
        
        self.add_widget(root)
    
    def _bg(self, w):
        with w.canvas.before:
            Color(*get_color_from_hex(C['bg_card']))
            w._bg = RoundedRectangle(pos=w.pos, size=w.size, radius=[dp(10)])
        w.bind(pos=self._upd, size=self._upd)
    
    def _upd(self, w, v):
        if hasattr(w, '_bg'):
            w._bg.pos = w.pos
            w._bg.size = w.size
    
    def go(self, s):
        self.manager.current = s
    
    def go_back(self):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'auto_input'


class CountrySelectScreen(BaseScreen):
    def on_enter(self):
        self.clear_widgets()
        self.selected = set()
        self.fmt = 'm3u8'
        Clock.schedule_once(lambda dt: self.build(), 0.05)
    
    def build(self):
        root = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(8))
        
        # Top
        top = BoxLayout(size_hint_y=None, height=dp(45), spacing=dp(8))
        back = Button(text=E['back'], size_hint=(None, None), size=(dp(45), dp(40)), font_size=dp(18), background_normal='', background_color=get_color_from_hex(C['bg_card']))
        back.bind(on_press=lambda x: self.go_back())
        top.add_widget(back)
        top.add_widget(Label(text=f'{E["globe"]} Ülke Seçimi', font_size=dp(16), bold=True, color=get_color_from_hex(C['white'])))
        root.add_widget(top)
        
        root.add_widget(Label(text='Grup bazlı filtreleme • Her link AYRI dosya', font_size=dp(10), color=get_color_from_hex(C['gray']), size_hint_y=None, height=dp(18)))
        
        self.sel_lbl = Label(text=f'{E["check"]} Seçilen: 0 ülke', font_size=dp(11), color=get_color_from_hex(C['success']), size_hint_y=None, height=dp(20))
        root.add_widget(self.sel_lbl)
        
        # Grid
        scroll = ScrollView()
        grid = GridLayout(cols=2, spacing=dp(6), size_hint_y=None, padding=dp(3))
        grid.bind(minimum_height=grid.setter('height'))
        
        self.btns = {}
        for cid in PRIORITY_COUNTRIES:
            cd = COUNTRIES[cid]
            btn = self._cbtn(cid, cd, True)
            grid.add_widget(btn)
        
        for cid, cd in sorted(COUNTRIES.items(), key=lambda x: x[1]['p']):
            if cid not in PRIORITY_COUNTRIES:
                btn = self._cbtn(cid, cd, False)
                grid.add_widget(btn)
        
        scroll.add_widget(grid)
        root.add_widget(scroll)
        
        # Format
        fmt_box = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(6))
        fmt_box.add_widget(Label(text='Format:', size_hint_x=None, width=dp(50), font_size=dp(11), color=get_color_from_hex(C['gray'])))
        
        self.fmt_btns = {}
        for fid, fd in FORMATS.items():
            btn = ToggleButton(text=fd['name'], group='fmt2', state='down' if fid == 'm3u8' else 'normal', font_size=dp(11), background_normal='', background_color=get_color_from_hex(C['primary']) if fid == 'm3u8' else get_color_from_hex(C['bg_light']))
            btn.fid = fid
            btn.bind(on_press=self.on_fmt)
            self.fmt_btns[fid] = btn
            fmt_box.add_widget(btn)
        root.add_widget(fmt_box)
        
        proc = Button(text=f'{E["rocket"]} Oluştur (Ayrı Dosyalar)', font_size=dp(14), bold=True, size_hint_y=None, height=dp(48), background_normal='', background_color=get_color_from_hex(C['success']))
        proc.bind(on_press=self.process)
        root.add_widget(proc)
        
        self.add_widget(root)
    
    def _cbtn(self, cid, cd, pri):
        btn = ToggleButton(text=f"{cd['flag']} {cd['name']}", size_hint_y=None, height=dp(48), font_size=dp(11), background_normal='', background_color=get_color_from_hex(C['warning']) if pri else get_color_from_hex(C['bg_card']))
        btn.cid = cid
        btn.pri = pri
        btn.bind(on_press=self.on_toggle)
        self.btns[cid] = btn
        return btn
    
    def on_toggle(self, btn):
        if btn.state == 'down':
            self.selected.add(btn.cid)
            btn.background_color = get_color_from_hex(C['success'])
        else:
            self.selected.discard(btn.cid)
            btn.background_color = get_color_from_hex(C['warning']) if btn.pri else get_color_from_hex(C['bg_card'])
        self.sel_lbl.text = f'{E["check"]} Seçilen: {len(self.selected)} ülke'
    
    def on_fmt(self, btn):
        self.fmt = btn.fid
        for fid, b in self.fmt_btns.items():
            b.background_color = get_color_from_hex(C['primary']) if fid == self.fmt else get_color_from_hex(C['bg_light'])
    
    def process(self, *args):
        if not self.selected:
            c = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
            c.add_widget(Label(text=E['warning'], font_size=dp(40)))
            c.add_widget(Label(text='Ülke seçin!', font_size=dp(14), color=get_color_from_hex(C['white'])))
            btn = Button(text='Tamam', size_hint=(0.5, None), height=dp(40), pos_hint={'center_x': 0.5}, background_normal='', background_color=get_color_from_hex(C['warning']))
            p = Popup(title='', content=c, size_hint=(0.7, 0.32), separator_height=0)
            btn.bind(on_press=p.dismiss)
            c.add_widget(btn)
            p.open()
            return
        
        app = App.get_running_app()
        app.sel_countries = self.selected
        app.out_fmt = self.fmt
        self.manager.current = 'processing'
    
    def go_back(self):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'auto_result'


class ProcessingScreen(BaseScreen):
    def on_enter(self):
        self.clear_widgets()
        self.files = []
        Clock.schedule_once(lambda dt: self.build(), 0.05)
        Clock.schedule_once(lambda dt: self.run(), 0.2)
    
    def build(self):
        root = BoxLayout(orientation='vertical', padding=dp(25), spacing=dp(12))
        
        root.add_widget(Label(text=f'{E["gear"]} İşleniyor...', font_size=dp(20), bold=True, color=get_color_from_hex(C['white']), size_hint_y=None, height=dp(35)))
        
        self.status = Label(text='Başlatılıyor...', font_size=dp(12), color=get_color_from_hex(C['gray']), size_hint_y=None, height=dp(22))
        root.add_widget(self.status)
        
        self.prog = AnimProgress(size_hint_y=None, height=dp(22))
        root.add_widget(self.prog)
        
        self.pct = Label(text='%0', font_size=dp(22), bold=True, color=get_color_from_hex(C['primary']), size_hint_y=None, height=dp(30))
        root.add_widget(self.pct)
        
        stats_card = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(6), size_hint_y=None, height=dp(110))
        self._bg(stats_card)
        
        self.curr_lbl = Label(text=f'{E["link"]} İşlenen: -', font_size=dp(11), color=get_color_from_hex(C['gray']))
        stats_card.add_widget(self.curr_lbl)
        
        self.total_lbl = Label(text=f'{E["tv"]} Toplam: 0 kanal', font_size=dp(13), color=get_color_from_hex(C['white']))
        stats_card.add_widget(self.total_lbl)
        
        self.filt_lbl = Label(text=f'{E["success"]} Filtrelenen: 0 kanal', font_size=dp(13), color=get_color_from_hex(C['success']))
        stats_card.add_widget(self.filt_lbl)
        
        self.file_lbl = Label(text=f'{E["file"]} Dosyalar: 0', font_size=dp(11), color=get_color_from_hex(C['info']))
        stats_card.add_widget(self.file_lbl)
        
        root.add_widget(stats_card)
        root.add_widget(Label())
        
        self.add_widget(root)
    
    def _bg(self, w):
        with w.canvas.before:
            Color(*get_color_from_hex(C['bg_card']))
            w._bg = RoundedRectangle(pos=w.pos, size=w.size, radius=[dp(10)])
        w.bind(pos=self._upd, size=self._upd)
    
    def _upd(self, w, v):
        if hasattr(w, '_bg'):
            w._bg.pos = w.pos
            w._bg.size = w.size
    
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
        path = get_download_path()
        ext = FORMATS.get(fmt, {}).get('ext', '.m3u')
        
        for i, link in enumerate(links):
            domain = short_domain(link)
            Clock.schedule_once(lambda dt, d=domain: setattr(self.curr_lbl, 'text', f'{E["link"]} İşlenen: {d}'))
            
            pct = ((i + 0.5) / total_links) * 100
            Clock.schedule_once(lambda dt, p=pct: self._upd_prog(p))
            
            try:
                r = requests.get(link, timeout=30, headers={'User-Agent': 'Mozilla/5.0'})
                chs, grps, exp = parse_m3u(r.text, link)
                
                total_ch += len(chs)
                
                filt_chs = []
                for gn, gd in grps.items():
                    if gd.get('country', 'other') in countries:
                        filt_chs.extend(gd['channels'])
                
                total_filt += len(filt_chs)
                
                Clock.schedule_once(lambda dt, t=total_ch, f=total_filt: self._upd_stats(t, f))
                
                if filt_chs:
                    content = gen_m3u(filt_chs, fmt)
                    exp_str = exp.replace('.', '') if exp != 'Bilinmiyor' else datetime.now().strftime('%d%m%Y')
                    fname = f'bitis{exp_str}_{domain}{ext}'
                    fpath = os.path.join(path, fname)
                    
                    with open(fpath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    self.files.append({'name': fname, 'count': len(filt_chs), 'expire': exp})
                    Clock.schedule_once(lambda dt, c=len(self.files): setattr(self.file_lbl, 'text', f'{E["file"]} Dosyalar: {c}'))
            except:
                pass
            
            pct = ((i + 1) / total_links) * 100
            Clock.schedule_once(lambda dt, p=pct: self._upd_prog(p))
            
            if i % 2 == 0:
                cleanup()
        
        app.saved_files = self.files
        app.total_filt = total_filt
        app.total_ch = total_ch
        
        Clock.schedule_once(lambda dt: self._upd_prog(100))
        Clock.schedule_once(lambda dt: self._done())
    
    def _upd_prog(self, p):
        self.prog.set_value(p)
        self.pct.text = f'%{int(p)}'
    
    def _upd_stats(self, t, f):
        self.total_lbl.text = f'{E["tv"]} Toplam: {t} kanal'
        self.filt_lbl.text = f'{E["success"]} Filtrelenen: {f} kanal'
    
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
        
        root = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(8))
        
        top = BoxLayout(size_hint_y=None, height=dp(45), spacing=dp(8))
        back = Button(text=E['back'], size_hint=(None, None), size=(dp(45), dp(40)), font_size=dp(18), background_normal='', background_color=get_color_from_hex(C['bg_card']))
        back.bind(on_press=lambda x: self.go_back())
        top.add_widget(back)
        top.add_widget(Label(text=f'{E["edit"]} Manuel Düzenleme', font_size=dp(15), bold=True, color=get_color_from_hex(C['white'])))
        root.add_widget(top)
        
        root.add_widget(Label(text=f'{len(links)} link • Düzenlemek için tıkla', font_size=dp(11), color=get_color_from_hex(C['gray']), size_hint_y=None, height=dp(20)))
        
        scroll = ScrollView()
        lst = BoxLayout(orientation='vertical', spacing=dp(6), size_hint_y=None)
        lst.bind(minimum_height=lst.setter('height'))
        
        for i, link in enumerate(links):
            item = self._item(i + 1, link)
            lst.add_widget(item)
        
        scroll.add_widget(lst)
        root.add_widget(scroll)
        
        self.add_widget(root)
    
    def _item(self, idx, link):
        item = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(60), padding=dp(10), spacing=dp(8))
        
        with item.canvas.before:
            Color(*get_color_from_hex(C['bg_card']))
            item._bg = RoundedRectangle(pos=item.pos, size=item.size, radius=[dp(8)])
        item.bind(pos=self._upd, size=self._upd)
        
        item.add_widget(Label(text=str(idx), font_size=dp(16), bold=True, color=get_color_from_hex(C['primary']), size_hint_x=None, width=dp(30)))
        
        info = BoxLayout(orientation='vertical', spacing=dp(2))
        domain = short_domain(link)
        info.add_widget(Label(text=domain, font_size=dp(12), color=get_color_from_hex(C['white']), halign='left'))
        info.add_widget(Label(text=link[:35] + '...', font_size=dp(9), color=get_color_from_hex(C['dark']), halign='left'))
        item.add_widget(info)
        
        btn = Button(text=E['edit'], size_hint=(None, None), size=(dp(42), dp(42)), font_size=dp(18), background_normal='', background_color=get_color_from_hex(C['primary']))
        btn.link = link
        btn.idx = idx
        btn.bind(on_press=self.edit)
        item.add_widget(btn)
        
        return item
    
    def _upd(self, w, v):
        if hasattr(w, '_bg'):
            w._bg.pos = w.pos
            w._bg.size = w.size
    
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
        
        root = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(6))
        
        top = BoxLayout(size_hint_y=None, height=dp(45), spacing=dp(8))
        back = Button(text=E['back'], size_hint=(None, None), size=(dp(45), dp(40)), font_size=dp(18), background_normal='', background_color=get_color_from_hex(C['bg_card']))
        back.bind(on_press=lambda x: self.go_back())
        top.add_widget(back)
        top.add_widget(Label(text=f'Link {idx}/{total}', font_size=dp(14), bold=True, color=get_color_from_hex(C['white'])))
        root.add_widget(top)
        
        # Loading with percentage
        self.load_box = BoxLayout(orientation='vertical', spacing=dp(8))
        self.load_icon = Label(text=E['loading'], font_size=dp(35))
        self.load_box.add_widget(self.load_icon)
        self.load_msg = Label(text='Yükleniyor...', font_size=dp(13), color=get_color_from_hex(C['gray']))
        self.load_box.add_widget(self.load_msg)
        self.load_prog = AnimProgress(size_hint_y=None, height=dp(18))
        self.load_box.add_widget(self.load_prog)
        self.load_pct = Label(text='%0', font_size=dp(18), bold=True, color=get_color_from_hex(C['primary']))
        self.load_box.add_widget(self.load_pct)
        root.add_widget(self.load_box)
        
        # Content
        self.content = BoxLayout(orientation='vertical', spacing=dp(6), opacity=0)
        
        self.exp_lbl = Label(text='', font_size=dp(10), color=get_color_from_hex(C['warning']), size_hint_y=None, height=dp(18))
        self.content.add_widget(self.exp_lbl)
        
        self.stats_lbl = Label(text='', font_size=dp(11), color=get_color_from_hex(C['gray']), size_hint_y=None, height=dp(20))
        self.content.add_widget(self.stats_lbl)
        
        self.sel_lbl = Label(text=f'{E["check"]} Seçilen: 0', font_size=dp(10), color=get_color_from_hex(C['success']), size_hint_y=None, height=dp(18))
        self.content.add_widget(self.sel_lbl)
        
        self.rv = RV()
        self.rv_data = []
        self.content.add_widget(self.rv)
        
        root.add_widget(self.content)
        
        self.btm = BoxLayout(size_hint_y=None, height=dp(45), spacing=dp(8), opacity=0)
        save = Button(text=f'{E["save"]} Kaydet', font_size=dp(13), bold=True, background_normal='', background_color=get_color_from_hex(C['success']))
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
            Clock.schedule_once(lambda dt: self._upd_load(10, 'Bağlanılıyor...'))
            
            r = requests.get(link, timeout=30, headers={'User-Agent': 'Mozilla/5.0'})
            
            Clock.schedule_once(lambda dt: self._upd_load(40, 'İndiriliyor...'))
            
            content = r.text
            
            Clock.schedule_once(lambda dt: self._upd_load(70, 'Ayrıştırılıyor...'))
            
            self.channels, self.groups, self.expire = parse_m3u(content, link)
            
            Clock.schedule_once(lambda dt: self._upd_load(100, 'Tamamlandı!'))
            Clock.schedule_once(lambda dt: self._show(), 0.2)
        except Exception as e:
            Clock.schedule_once(lambda dt, m=str(e)[:30]: self._err(m))
    
    def _upd_load(self, pct, msg):
        self.load_prog.set_value(pct)
        self.load_pct.text = f'%{int(pct)}'
        self.load_msg.text = msg
    
    def _show(self):
        self.load_box.opacity = 0
        self.load_box.size_hint_y = 0.001
        self.content.opacity = 1
        self.btm.opacity = 1
        
        self.exp_lbl.text = f'{E["calendar"]} Bitiş: {self.expire}'
        self.stats_lbl.text = f'{E["list"]} {len(self.groups)} grup • {len(self.channels)} kanal'
        
        self.rv_data = []
        for gn, gd in sorted(self.groups.items()):
            self.rv_data.append({'grp_name': gn, 'ch_count': len(gd['channels']), 'is_selected': False, 'callback': self.on_sel})
        self.rv.data = self.rv_data
    
    def _err(self, msg):
        self.load_msg.text = f'{E["error"]} Hata: {msg}'
        self.load_icon.text = E['error']
    
    def on_sel(self, gn, sel, idx):
        self.rv_data[idx]['is_selected'] = sel
        if sel:
            self.selected.add(gn)
        else:
            self.selected.discard(gn)
        
        total = sum(len(self.groups[g]['channels']) for g in self.selected if g in self.groups)
        self.sel_lbl.text = f'{E["check"]} Seçilen: {len(self.selected)} grup ({total} kanal)'
    
    def save(self, *args):
        if not self.selected:
            c = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
            c.add_widget(Label(text=E['warning'], font_size=dp(40)))
            c.add_widget(Label(text='Grup seçin!', font_size=dp(14), color=get_color_from_hex(C['white'])))
            btn = Button(text='Tamam', size_hint=(0.5, None), height=dp(40), pos_hint={'center_x': 0.5}, background_normal='', background_color=get_color_from_hex(C['warning']))
            p = Popup(title='', content=c, size_hint=(0.7, 0.32), separator_height=0)
            btn.bind(on_press=p.dismiss)
            c.add_widget(btn)
            p.open()
            return
        
        chs = []
        for gn in self.selected:
            if gn in self.groups:
                chs.extend(self.groups[gn]['channels'])
        
        content = gen_m3u(chs)
        
        app = App.get_running_app()
        link = getattr(app, 'edit_link', '')
        
        path = get_download_path()
        domain = short_domain(link)
        exp_str = self.expire.replace('.', '') if self.expire != 'Bilinmiyor' else datetime.now().strftime('%d%m%Y')
        fname = f'bitis{exp_str}_{domain}.m3u8'
        fpath = os.path.join(path, fname)
        
        try:
            with open(fpath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            c = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
            c.add_widget(Label(text=E['success'], font_size=dp(45)))
            c.add_widget(Label(text='Kaydedildi!', font_size=dp(16), bold=True, color=get_color_from_hex(C['white'])))
            c.add_widget(Label(text=f'{len(chs)} kanal\n{E["file"]} {fname}', font_size=dp(11), color=get_color_from_hex(C['gray']), halign='center'))
            btn = Button(text='Listeye Dön', size_hint=(0.55, None), height=dp(38), pos_hint={'center_x': 0.5}, background_normal='', background_color=get_color_from_hex(C['primary']))
            p = Popup(title='', content=c, size_hint=(0.8, 0.42), separator_height=0)
            def go(x):
                p.dismiss()
                self.manager.transition = SlideTransition(direction='right')
                self.manager.current = 'manual_link_list'
            btn.bind(on_press=go)
            c.add_widget(btn)
            p.open()
        except Exception as e:
            c = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
            c.add_widget(Label(text=E['error'], font_size=dp(40)))
            c.add_widget(Label(text=str(e)[:30], font_size=dp(13), color=get_color_from_hex(C['white'])))
            btn = Button(text='Tamam', size_hint=(0.5, None), height=dp(40), pos_hint={'center_x': 0.5}, background_normal='', background_color=get_color_from_hex(C['danger']))
            p = Popup(title='', content=c, size_hint=(0.75, 0.35), separator_height=0)
            btn.bind(on_press=p.dismiss)
            c.add_widget(btn)
            p.open()
        cleanup()
    
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
        
        root = BoxLayout(orientation='vertical', padding=dp(25), spacing=dp(15))
        
        root.add_widget(Label(text=E['party'], font_size=dp(55), size_hint_y=0.18))
        root.add_widget(Label(text='Tamamlandı!', font_size=dp(24), bold=True, color=get_color_from_hex(C['white']), size_hint_y=None, height=dp(35)))
        
        res_card = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(8), size_hint_y=None, height=dp(120))
        self._bg(res_card)
        
        res_card.add_widget(Label(text=f'{E["tv"]} {filt} kanal filtrelendi', font_size=dp(14), color=get_color_from_hex(C['success'])))
        res_card.add_widget(Label(text=f'Toplam {total} kanaldan', font_size=dp(11), color=get_color_from_hex(C['gray'])))
        res_card.add_widget(Label(text=f'{E["file"]} {len(files)} dosya oluşturuldu', font_size=dp(13), color=get_color_from_hex(C['info'])))
        res_card.add_widget(Label(text=f'{E["folder"]} Download klasörüne kaydedildi', font_size=dp(10), color=get_color_from_hex(C['dark'])))
        
        root.add_widget(res_card)
        
        if files:
            root.add_widget(Label(text='Dosyalar:', font_size=dp(12), color=get_color_from_hex(C['gray']), size_hint_y=None, height=dp(22)))
            
            scroll = ScrollView(size_hint_y=None, height=dp(70))
            fb = BoxLayout(orientation='vertical', spacing=dp(2), size_hint_y=None)
            fb.bind(minimum_height=fb.setter('height'))
            
            for f in files[:4]:
                fb.add_widget(Label(text=f"{E['file']} {f['name']} ({f['count']})", font_size=dp(9), color=get_color_from_hex(C['light']), size_hint_y=None, height=dp(16), halign='left'))
            
            if len(files) > 4:
                fb.add_widget(Label(text=f'... ve {len(files) - 4} dosya daha', font_size=dp(9), color=get_color_from_hex(C['dark']), size_hint_y=None, height=dp(16)))
            
            scroll.add_widget(fb)
            root.add_widget(scroll)
        
        btns = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None, height=dp(95))
        
        new_btn = Button(text=f'{E["refresh"]} Yeni İşlem', font_size=dp(14), bold=True, size_hint_y=None, height=dp(42), background_normal='', background_color=get_color_from_hex(C['primary']))
        new_btn.bind(on_press=lambda x: self.go('auto_input'))
        btns.add_widget(new_btn)
        
        home_btn = Button(text=f'{E["home"]} Ana Sayfa', font_size=dp(14), bold=True, size_hint_y=None, height=dp(42), background_normal='', background_color=get_color_from_hex(C['bg_card']))
        home_btn.bind(on_press=lambda x: self.go('welcome'))
        btns.add_widget(home_btn)
        
        root.add_widget(btns)
        
        self.add_widget(root)
    
    def _bg(self, w):
        with w.canvas.before:
            Color(*get_color_from_hex(C['bg_card']))
            w._bg = RoundedRectangle(pos=w.pos, size=w.size, radius=[dp(12)])
        w.bind(pos=self._upd, size=self._upd)
    
    def _upd(self, w, v):
        if hasattr(w, '_bg'):
            w._bg.pos = w.pos
            w._bg.size = w.size
    
    def go(self, s):
        cleanup()
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = s


# ==================== APP ====================

class IPTVApp(App):
    def build(self):
        Window.clearcolor = get_color_from_hex(C['bg_dark'])
        
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
        cleanup()


if __name__ == '__main__':
    IPTVApp().run()
