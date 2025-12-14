"""
IPTV Editor Pro v5.0
Tam Özellikli - Profesyonel Tasarım
Tüm özellikler: Manuel/Otomatik düzenleme, Link testi, Ülke filtreleme
"""

import os
import sys
import re
import traceback
import threading
from datetime import datetime
from urllib.parse import urlparse

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

# ==================== KIVY IMPORTS ====================
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition, NoTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar
from kivy.uix.spinner import Spinner
from kivy.uix.image import AsyncImage
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.properties import StringProperty, BooleanProperty, NumericProperty, ListProperty
from kivy.utils import get_color_from_hex

import requests

# ==================== KV TASARIM ====================
# KV dili ile tasarım - Android'de daha stabil çalışır
KV_DESIGN = '''
#:import dp kivy.metrics.dp
#:import get_color_from_hex kivy.utils.get_color_from_hex

# ===== RENKLER =====
#:set BG_DARK '#1a1a2e'
#:set BG_MEDIUM '#16213e'
#:set BG_CARD '#252542'
#:set PRIMARY '#7c6aef'
#:set PRIMARY_LIGHT '#9d8df7'
#:set SECONDARY '#f7717d'
#:set SUCCESS '#56d4bc'
#:set WARNING '#ffd369'
#:set DANGER '#ff6b6b'
#:set TEXT_WHITE '#ffffff'
#:set TEXT_GRAY '#a0a0b8'
#:set BORDER '#3d3d5c'

# ===== TEMEL WIDGETLAR =====
<StyledButton@Button>:
    background_normal: ''
    background_color: get_color_from_hex(PRIMARY)
    color: get_color_from_hex(TEXT_WHITE)
    font_size: dp(15)
    size_hint_y: None
    height: dp(48)
    bold: True

<SecondaryButton@Button>:
    background_normal: ''
    background_color: get_color_from_hex(SECONDARY)
    color: get_color_from_hex(TEXT_WHITE)
    font_size: dp(15)
    size_hint_y: None
    height: dp(48)
    bold: True

<SuccessButton@Button>:
    background_normal: ''
    background_color: get_color_from_hex(SUCCESS)
    color: get_color_from_hex(BG_DARK)
    font_size: dp(15)
    size_hint_y: None
    height: dp(48)
    bold: True

<DarkButton@Button>:
    background_normal: ''
    background_color: get_color_from_hex(BG_CARD)
    color: get_color_from_hex(TEXT_WHITE)
    font_size: dp(14)
    size_hint_y: None
    height: dp(44)

<CardBox@BoxLayout>:
    orientation: 'vertical'
    padding: dp(15)
    spacing: dp(10)
    canvas.before:
        Color:
            rgba: get_color_from_hex(BG_CARD)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(12)]

<TitleLabel@Label>:
    color: get_color_from_hex(TEXT_WHITE)
    font_size: dp(24)
    bold: True
    size_hint_y: None
    height: dp(40)

<SubtitleLabel@Label>:
    color: get_color_from_hex(TEXT_GRAY)
    font_size: dp(14)
    size_hint_y: None
    height: dp(25)

<SmallLabel@Label>:
    color: get_color_from_hex(TEXT_GRAY)
    font_size: dp(12)
    size_hint_y: None
    height: dp(20)

<StyledInput@TextInput>:
    background_color: get_color_from_hex(BG_MEDIUM)
    foreground_color: get_color_from_hex(TEXT_WHITE)
    cursor_color: get_color_from_hex(PRIMARY)
    font_size: dp(14)
    padding: [dp(12), dp(10)]
    size_hint_y: None
    height: dp(48)
    multiline: False

<MultiLineInput@TextInput>:
    background_color: get_color_from_hex(BG_MEDIUM)
    foreground_color: get_color_from_hex(TEXT_WHITE)
    cursor_color: get_color_from_hex(PRIMARY)
    font_size: dp(13)
    padding: [dp(12), dp(10)]

# ===== EKRANLAR =====
<BaseScreen@Screen>:
    canvas.before:
        Color:
            rgba: get_color_from_hex(BG_DARK)
        Rectangle:
            pos: self.pos
            size: self.size

<ChannelGroupCard@BoxLayout>:
    orientation: 'horizontal'
    size_hint_y: None
    height: dp(75)
    padding: dp(10)
    spacing: dp(12)
    selected: False
    group_name: ''
    channel_count: 0
    logo_url: ''
    
    canvas.before:
        Color:
            rgba: get_color_from_hex(SUCCESS) if self.selected else get_color_from_hex(BG_CARD)
            a: 0.25 if self.selected else 1
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(10)]
    
    BoxLayout:
        size_hint_x: None
        width: dp(50)
        Label:
            text: '[TV]'
            font_size: dp(22)
            color: get_color_from_hex(PRIMARY)
    
    BoxLayout:
        orientation: 'vertical'
        spacing: dp(2)
        Label:
            text: root.group_name[:30] + ('...' if len(root.group_name) > 30 else '')
            font_size: dp(14)
            color: get_color_from_hex(TEXT_WHITE)
            text_size: self.size
            halign: 'left'
            valign: 'middle'
        Label:
            text: str(root.channel_count) + ' kanal'
            font_size: dp(11)
            color: get_color_from_hex(TEXT_GRAY)
            text_size: self.size
            halign: 'left'
            valign: 'middle'
    
    Button:
        size_hint: None, None
        size: dp(48), dp(48)
        text: 'OK' if root.selected else '+'
        font_size: dp(20)
        background_normal: ''
        background_color: get_color_from_hex(SUCCESS) if root.selected else get_color_from_hex(PRIMARY)
        on_press: root.toggle_select()

<CountryCard@ToggleButton>:
    size_hint_y: None
    height: dp(55)
    background_normal: ''
    background_color: get_color_from_hex(SUCCESS) if self.state == 'down' else get_color_from_hex(BG_CARD)
    color: get_color_from_hex(TEXT_WHITE)
    font_size: dp(13)
    bold: True

<FormatButton@ToggleButton>:
    size_hint_y: None
    height: dp(42)
    background_normal: ''
    background_color: get_color_from_hex(PRIMARY) if self.state == 'down' else get_color_from_hex(BG_CARD)
    color: get_color_from_hex(TEXT_WHITE)
    font_size: dp(14)
    group: 'format'

<LinkTestItem@BoxLayout>:
    orientation: 'horizontal'
    size_hint_y: None
    height: dp(50)
    padding: [dp(10), dp(5)]
    spacing: dp(10)
    
    Label:
        text: root.status_icon
        font_size: dp(20)
        size_hint_x: None
        width: dp(35)
    
    Label:
        text: root.link_text
        font_size: dp(11)
        color: get_color_from_hex(root.text_color)
        text_size: self.size
        halign: 'left'
        valign: 'middle'
        shorten: True
        shorten_from: 'right'
'''

Builder.load_string(KV_DESIGN)

# ==================== RENKLER ====================
COLORS = {
    'bg_dark': '#1a1a2e',
    'bg_medium': '#16213e', 
    'bg_card': '#252542',
    'primary': '#7c6aef',
    'primary_light': '#9d8df7',
    'secondary': '#f7717d',
    'success': '#56d4bc',
    'warning': '#ffd369',
    'danger': '#ff6b6b',
    'text_white': '#ffffff',
    'text_gray': '#a0a0b8',
}

# ==================== ÜLKE VERİLERİ ====================
COUNTRIES = {
    'turkey': {
        'name': 'Türkiye',
        'flag': '🇹🇷',
        'codes': ['tr', 'tur', 'turkey', 'türkiye', 'turkiye', 'turkish', 'turk', 'türk'],
        'priority': 1
    },
    'germany': {
        'name': 'Almanya', 
        'flag': '🇩🇪',
        'codes': ['de', 'ger', 'germany', 'deutschland', 'german', 'deutsch', 'deu', 'almanya'],
        'priority': 2
    },
    'romania': {
        'name': 'Romanya',
        'flag': '🇷🇴', 
        'codes': ['ro', 'rom', 'romania', 'romanian', 'rou', 'romanya'],
        'priority': 3
    },
    'austria': {
        'name': 'Avusturya',
        'flag': '🇦🇹',
        'codes': ['at', 'aut', 'austria', 'österreich', 'austrian', 'avusturya'],
        'priority': 4
    },
    'france': {
        'name': 'Fransa',
        'flag': '🇫🇷',
        'codes': ['fr', 'fra', 'france', 'french', 'francais', 'fransa'],
        'priority': 5
    },
    'italy': {
        'name': 'İtalya',
        'flag': '🇮🇹',
        'codes': ['it', 'ita', 'italy', 'italian', 'italiano', 'italya'],
        'priority': 6
    },
    'spain': {
        'name': 'İspanya',
        'flag': '🇪🇸',
        'codes': ['es', 'esp', 'spain', 'spanish', 'espanol', 'españa', 'ispanya'],
        'priority': 7
    },
    'uk': {
        'name': 'İngiltere',
        'flag': '🇬🇧',
        'codes': ['uk', 'gb', 'gbr', 'england', 'british', 'english', 'ingiltere'],
        'priority': 8
    },
    'usa': {
        'name': 'Amerika',
        'flag': '🇺🇸',
        'codes': ['us', 'usa', 'america', 'american', 'united states', 'amerika'],
        'priority': 9
    },
    'netherlands': {
        'name': 'Hollanda',
        'flag': '🇳🇱',
        'codes': ['nl', 'nld', 'netherlands', 'dutch', 'holland', 'hollanda'],
        'priority': 10
    },
    'poland': {
        'name': 'Polonya',
        'flag': '🇵🇱',
        'codes': ['pl', 'pol', 'poland', 'polish', 'polska', 'polonya'],
        'priority': 11
    },
    'russia': {
        'name': 'Rusya',
        'flag': '🇷🇺',
        'codes': ['ru', 'rus', 'russia', 'russian', 'rusya'],
        'priority': 12
    },
    'arabic': {
        'name': 'Arapça',
        'flag': '🇸🇦',
        'codes': ['ar', 'ara', 'arabic', 'arab', 'arap'],
        'priority': 13
    },
    'india': {
        'name': 'Hindistan',
        'flag': '🇮🇳',
        'codes': ['in', 'ind', 'india', 'indian', 'hindi', 'hindistan'],
        'priority': 14
    },
    'portugal': {
        'name': 'Portekiz',
        'flag': '🇵🇹',
        'codes': ['pt', 'por', 'portugal', 'portuguese', 'brasil', 'brazil', 'portekiz'],
        'priority': 15
    },
    'greece': {
        'name': 'Yunanistan',
        'flag': '🇬🇷',
        'codes': ['gr', 'gre', 'greece', 'greek', 'yunanistan', 'yunan'],
        'priority': 16
    },
    'albania': {
        'name': 'Arnavutluk',
        'flag': '🇦🇱',
        'codes': ['al', 'alb', 'albania', 'albanian', 'shqip', 'arnavut'],
        'priority': 17
    },
    'serbia': {
        'name': 'Sırbistan',
        'flag': '🇷🇸',
        'codes': ['rs', 'srb', 'serbia', 'serbian', 'srpski', 'sirbistan'],
        'priority': 18
    },
    'croatia': {
        'name': 'Hırvatistan',
        'flag': '🇭🇷',
        'codes': ['hr', 'hrv', 'croatia', 'croatian', 'hrvatski', 'hirvatistan'],
        'priority': 19
    },
    'bulgaria': {
        'name': 'Bulgaristan',
        'flag': '🇧🇬',
        'codes': ['bg', 'bgr', 'bulgaria', 'bulgarian', 'bulgaristan'],
        'priority': 20
    },
    'other': {
        'name': 'Diğer Ülkeler',
        'flag': '🌍',
        'codes': ['other', 'misc', 'mixed', 'international', 'world', 'diger'],
        'priority': 99
    }
}

# Öncelikli ülkeler (ilk 4)
PRIORITY_COUNTRIES = ['turkey', 'germany', 'romania', 'austria']

# ==================== DOSYA FORMATLARI ====================
FILE_FORMATS = {
    'm3u': {'name': 'M3U', 'desc': 'Standart', 'ext': '.m3u'},
    'm3u8': {'name': 'M3U8', 'desc': 'En İyi ⭐', 'ext': '.m3u8'},
    'm3u_plus': {'name': 'M3U Plus', 'desc': 'Gelişmiş', 'ext': '.m3u'},
    'txt': {'name': 'TXT', 'desc': 'Basit', 'ext': '.txt'},
}

# ==================== YARDIMCI FONKSİYONLAR ====================

def get_download_path():
    """Android Download klasörünü döndür"""
    try:
        from android.storage import primary_external_storage_path
        return os.path.join(primary_external_storage_path(), 'Download')
    except:
        return os.path.expanduser('~')


def parse_m3u(content):
    """M3U içeriğini parse et"""
    channels = []
    groups = {}
    
    lines = content.split('\n')
    current_channel = {}
    
    for line in lines:
        line = line.strip()
        
        if line.startswith('#EXTINF:'):
            current_channel = {
                'name': '',
                'group': 'Diğer',
                'logo': '',
                'tvg_id': '',
                'tvg_name': '',
                'url': ''
            }
            
            # Group title
            match = re.search(r'group-title="([^"]*)"', line)
            if match and match.group(1):
                current_channel['group'] = match.group(1)
            
            # Logo
            match = re.search(r'tvg-logo="([^"]*)"', line)
            if match:
                current_channel['logo'] = match.group(1)
            
            # TVG-ID
            match = re.search(r'tvg-id="([^"]*)"', line)
            if match:
                current_channel['tvg_id'] = match.group(1)
            
            # TVG-Name
            match = re.search(r'tvg-name="([^"]*)"', line)
            if match:
                current_channel['tvg_name'] = match.group(1)
            
            # Channel name
            match = re.search(r',(.+)$', line)
            if match:
                current_channel['name'] = match.group(1).strip()
                
        elif line.startswith('http') or line.startswith('rtmp') or line.startswith('rtsp'):
            if current_channel:
                current_channel['url'] = line
                channels.append(current_channel.copy())
                
                group_name = current_channel['group']
                if group_name not in groups:
                    groups[group_name] = {
                        'channels': [],
                        'logo': current_channel['logo']
                    }
                groups[group_name]['channels'].append(current_channel.copy())
                
            current_channel = {}
    
    return channels, groups


def generate_m3u(channels, format_type='m3u'):
    """Kanal listesinden M3U içeriği oluştur"""
    content = '#EXTM3U\n'
    
    if format_type == 'm3u_plus':
        content = '#EXTM3U url-tvg="http://epg.example.com"\n'
    
    for ch in channels:
        extinf = '#EXTINF:-1'
        
        if ch.get('tvg_id'):
            extinf += f' tvg-id="{ch["tvg_id"]}"'
        if ch.get('tvg_name'):
            extinf += f' tvg-name="{ch["tvg_name"]}"'
        if ch.get('logo'):
            extinf += f' tvg-logo="{ch["logo"]}"'
        if ch.get('group'):
            extinf += f' group-title="{ch["group"]}"'
            
        extinf += f',{ch.get("name", "Unknown Channel")}\n'
        content += extinf
        content += f'{ch.get("url", "")}\n'
    
    return content


def generate_txt(channels):
    """Sadece URL'leri içeren basit TXT formatı"""
    return '\n'.join([ch.get('url', '') for ch in channels if ch.get('url')])


def detect_country(text):
    """Metinden ülke tespit et"""
    text = text.lower()
    
    for country_id, country_data in COUNTRIES.items():
        for code in country_data['codes']:
            # Tam kelime eşleşmesi için word boundary kullan
            if re.search(rf'\b{re.escape(code)}\b', text):
                return country_id
            # Başında veya sonunda tire/alt çizgi ile
            if re.search(rf'[-_]{re.escape(code)}[-_]', text):
                return country_id
            if text.startswith(code + ' ') or text.startswith(code + '-') or text.startswith(code + '_'):
                return country_id
    
    return 'other'


def test_link_quick(url, timeout=8):
    """Hızlı link testi - sadece HEAD request"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.head(url, timeout=timeout, headers=headers, allow_redirects=True)
        return response.status_code == 200, "Başarılı"
    except requests.exceptions.Timeout:
        return False, "Zaman aşımı"
    except requests.exceptions.ConnectionError:
        return False, "Bağlantı hatası"
    except Exception as e:
        return False, str(e)[:30]


def test_link_deep(url, timeout=15):
    """Derin link testi - video akışını kontrol et"""
    try:
        headers = {'User-Agent': 'VLC/3.0.11 LibVLC/3.0.11'}
        response = requests.get(url, timeout=timeout, headers=headers, stream=True)
        
        if response.status_code != 200:
            return False, f"HTTP {response.status_code}"
        
        # Video verisi almaya çalış
        total_bytes = 0
        for chunk in response.iter_content(chunk_size=8192):
            total_bytes += len(chunk)
            if total_bytes > 32768:  # 32KB yeterli
                break
        
        if total_bytes > 1024:
            return True, f"Aktif ({total_bytes//1024}KB)"
        else:
            return False, "Veri yok"
            
    except requests.exceptions.Timeout:
        return False, "Zaman aşımı"
    except requests.exceptions.ConnectionError:
        return False, "Bağlantı hatası"
    except Exception as e:
        return False, str(e)[:30]


# ==================== CUSTOM WIDGETS ====================

class ChannelGroupCard(BoxLayout):
    """Kanal grubu kartı"""
    selected = BooleanProperty(False)
    group_name = StringProperty('')
    channel_count = NumericProperty(0)
    logo_url = StringProperty('')
    
    def __init__(self, on_select_callback=None, **kwargs):
        super().__init__(**kwargs)
        self.on_select_callback = on_select_callback
    
    def toggle_select(self):
        self.selected = not self.selected
        if self.on_select_callback:
            self.on_select_callback(self.group_name, self.selected)


class LinkTestItem(BoxLayout):
    """Link test sonucu satırı"""
    status_icon = StringProperty('⏳')
    link_text = StringProperty('')
    text_color = StringProperty('#a0a0b8')


# ==================== EKRANLAR ====================

class WelcomeScreen(Screen):
    """Ana ekran - Mod seçimi"""
    
    def on_enter(self):
        self.clear_widgets()
        Clock.schedule_once(lambda dt: self.build_ui(), 0.05)
    
    def build_ui(self):
        root = BoxLayout(orientation='vertical', padding=dp(25), spacing=dp(20))
        
        # === HEADER ===
        header = BoxLayout(orientation='vertical', size_hint_y=0.3, spacing=dp(5))
        
        # App icon
        icon_label = Label(
            text='📡',
            font_size=dp(60),
            size_hint_y=None,
            height=dp(80)
        )
        header.add_widget(icon_label)
        
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
            text='Gelişmiş IPTV Düzenleyici',
            font_size=dp(14),
            color=get_color_from_hex(COLORS['text_gray']),
            size_hint_y=None,
            height=dp(25)
        )
        header.add_widget(subtitle)
        
        root.add_widget(header)
        
        # === MODE CARDS ===
        cards = BoxLayout(orientation='vertical', spacing=dp(15), size_hint_y=0.55)
        
        # Manual Mode Card
        manual_card = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(12))
        manual_card.bind(size=self._update_card_bg, pos=self._update_card_bg)
        self._cards = [manual_card]
        
        manual_icon = Label(text='✏️', font_size=dp(35), size_hint_y=None, height=dp(45))
        manual_title = Label(
            text='Manuel Düzenleme',
            font_size=dp(18),
            bold=True,
            color=get_color_from_hex(COLORS['text_white']),
            size_hint_y=None,
            height=dp(28)
        )
        manual_desc = Label(
            text='IPTV URL\'sini girin, kanal gruplarını görün\nve istediğiniz kanalları seçerek dışa aktarın',
            font_size=dp(12),
            color=get_color_from_hex(COLORS['text_gray']),
            size_hint_y=None,
            height=dp(40),
            halign='center'
        )
        manual_desc.bind(size=lambda w, s: setattr(w, 'text_size', s))
        
        manual_btn = Button(
            text='Başla',
            font_size=dp(15),
            bold=True,
            size_hint=(0.5, None),
            height=dp(42),
            pos_hint={'center_x': 0.5},
            background_normal='',
            background_color=get_color_from_hex(COLORS['primary'])
        )
        manual_btn.bind(on_press=lambda x: self.go_to('manual_input'))
        
        manual_card.add_widget(manual_icon)
        manual_card.add_widget(manual_title)
        manual_card.add_widget(manual_desc)
        manual_card.add_widget(manual_btn)
        cards.add_widget(manual_card)
        
        # Auto Mode Card
        auto_card = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(12))
        auto_card.bind(size=self._update_card_bg, pos=self._update_card_bg)
        self._cards.append(auto_card)
        
        auto_icon = Label(text='🤖', font_size=dp(35), size_hint_y=None, height=dp(45))
        auto_title = Label(
            text='Otomatik Düzenleme',
            font_size=dp(18),
            bold=True,
            color=get_color_from_hex(COLORS['text_white']),
            size_hint_y=None,
            height=dp(28)
        )
        auto_desc = Label(
            text='Toplu linkleri test edin, çalışanları filtreleyin\nve ülkelere göre otomatik düzenleyin',
            font_size=dp(12),
            color=get_color_from_hex(COLORS['text_gray']),
            size_hint_y=None,
            height=dp(40),
            halign='center'
        )
        auto_desc.bind(size=lambda w, s: setattr(w, 'text_size', s))
        
        auto_btn = Button(
            text='Başla',
            font_size=dp(15),
            bold=True,
            size_hint=(0.5, None),
            height=dp(42),
            pos_hint={'center_x': 0.5},
            background_normal='',
            background_color=get_color_from_hex(COLORS['secondary'])
        )
        auto_btn.bind(on_press=lambda x: self.go_to('auto_input'))
        
        auto_card.add_widget(auto_icon)
        auto_card.add_widget(auto_title)
        auto_card.add_widget(auto_desc)
        auto_card.add_widget(auto_btn)
        cards.add_widget(auto_card)
        
        root.add_widget(cards)
        
        # === FOOTER ===
        footer = Label(
            text='v5.0 • Made with ❤️',
            font_size=dp(11),
            color=get_color_from_hex(COLORS['text_gray']),
            size_hint_y=0.1
        )
        root.add_widget(footer)
        
        self.add_widget(root)
        
        # Draw card backgrounds
        Clock.schedule_once(lambda dt: self._draw_all_cards(), 0.1)
    
    def _update_card_bg(self, widget, value):
        Clock.schedule_once(lambda dt: self._draw_card(widget), 0)
    
    def _draw_all_cards(self):
        for card in getattr(self, '_cards', []):
            self._draw_card(card)
    
    def _draw_card(self, card):
        from kivy.graphics import Color, RoundedRectangle
        card.canvas.before.clear()
        with card.canvas.before:
            Color(*get_color_from_hex(COLORS['bg_card']))
            RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(15)])
    
    def go_to(self, screen_name):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = screen_name


class ManualInputScreen(Screen):
    """Manuel mod - URL giriş ekranı"""
    
    def on_enter(self):
        self.clear_widgets()
        self.selected_format = 'm3u8'
        Clock.schedule_once(lambda dt: self.build_ui(), 0.05)
    
    def build_ui(self):
        root = BoxLayout(orientation='vertical', padding=dp(18), spacing=dp(15))
        
        # Top bar
        top_bar = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(10))
        
        back_btn = Button(
            text='◀',
            size_hint=(None, None),
            size=(dp(48), dp(42)),
            font_size=dp(18),
            background_normal='',
            background_color=get_color_from_hex(COLORS['bg_card'])
        )
        back_btn.bind(on_press=lambda x: self.go_back())
        top_bar.add_widget(back_btn)
        
        title = Label(
            text='✏️ Manuel Düzenleme',
            font_size=dp(18),
            bold=True,
            color=get_color_from_hex(COLORS['text_white'])
        )
        top_bar.add_widget(title)
        
        root.add_widget(top_bar)
        
        # URL Input Card
        url_card = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10), size_hint_y=None, height=dp(140))
        url_card.bind(size=self._update_card, pos=self._update_card)
        self._url_card = url_card
        
        url_label = Label(
            text='Playlist URL',
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
        
        # Format Selection Card
        format_card = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(12), size_hint_y=None, height=dp(130))
        format_card.bind(size=self._update_card, pos=self._update_card)
        self._format_card = format_card
        
        format_label = Label(
            text='Çıktı Formatı',
            font_size=dp(13),
            color=get_color_from_hex(COLORS['text_gray']),
            size_hint_y=None,
            height=dp(22),
            halign='left'
        )
        format_label.bind(size=lambda w, s: setattr(w, 'text_size', s))
        format_card.add_widget(format_label)
        
        format_btns = BoxLayout(spacing=dp(8), size_hint_y=None, height=dp(45))
        self.format_buttons = {}
        
        for fmt_id, fmt_data in FILE_FORMATS.items():
            btn = ToggleButton(
                text=f"{fmt_data['name']}\n{fmt_data['desc']}",
                group='format',
                state='down' if fmt_id == 'm3u8' else 'normal',
                font_size=dp(11),
                background_normal='',
                background_color=get_color_from_hex(COLORS['primary']) if fmt_id == 'm3u8' else get_color_from_hex(COLORS['bg_card']),
                size_hint_y=None,
                height=dp(45)
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
            text='📥 Kanalları Yükle',
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
        Clock.schedule_once(lambda dt: self._draw_cards(), 0.1)
    
    def _update_card(self, widget, value):
        Clock.schedule_once(lambda dt: self._draw_single_card(widget), 0)
    
    def _draw_cards(self):
        self._draw_single_card(self._url_card)
        self._draw_single_card(self._format_card)
    
    def _draw_single_card(self, card):
        from kivy.graphics import Color, RoundedRectangle
        card.canvas.before.clear()
        with card.canvas.before:
            Color(*get_color_from_hex(COLORS['bg_card']))
            RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(12)])
    
    def on_format_select(self, btn):
        self.selected_format = btn.format_id
        for fmt_id, button in self.format_buttons.items():
            if fmt_id == self.selected_format:
                button.background_color = get_color_from_hex(COLORS['primary'])
            else:
                button.background_color = get_color_from_hex(COLORS['bg_card'])
    
    def load_channels(self, instance):
        url = self.url_input.text.strip()
        if not url:
            self.show_popup('Hata', 'Lütfen bir URL girin!', 'error')
            return
        
        if not url.startswith('http'):
            self.show_popup('Hata', 'Geçersiz URL formatı!', 'error')
            return
        
        self.show_loading('Playlist yükleniyor...')
        threading.Thread(target=self._load_playlist, args=(url,), daemon=True).start()
    
    def _load_playlist(self, url):
        try:
            response = requests.get(url, timeout=30, headers={'User-Agent': 'Mozilla/5.0'})
            response.raise_for_status()
            
            channels, groups = parse_m3u(response.text)
            
            if not channels:
                Clock.schedule_once(lambda dt: self._on_load_error('Kanal bulunamadı!'))
                return
            
            Clock.schedule_once(lambda dt: self._on_load_success(channels, groups))
            
        except requests.exceptions.Timeout:
            Clock.schedule_once(lambda dt: self._on_load_error('Bağlantı zaman aşımına uğradı!'))
        except requests.exceptions.RequestException as e:
            Clock.schedule_once(lambda dt: self._on_load_error(f'Bağlantı hatası: {str(e)[:50]}'))
        except Exception as e:
            Clock.schedule_once(lambda dt: self._on_load_error(f'Hata: {str(e)[:50]}'))
    
    def _on_load_success(self, channels, groups):
        self.hide_loading()
        
        app = App.get_running_app()
        app.channels = channels
        app.groups = groups
        app.selected_format = self.selected_format
        app.source_mode = 'manual'
        
        self.manager.current = 'channel_list'
    
    def _on_load_error(self, error_msg):
        self.hide_loading()
        self.show_popup('Yükleme Hatası', error_msg, 'error')
    
    def show_loading(self, message):
        content = BoxLayout(orientation='vertical', padding=dp(25), spacing=dp(20))
        
        spinner_label = Label(text='⏳', font_size=dp(45))
        content.add_widget(spinner_label)
        
        msg_label = Label(
            text=message,
            font_size=dp(14),
            color=get_color_from_hex(COLORS['text_white'])
        )
        content.add_widget(msg_label)
        
        progress = ProgressBar(max=100, value=50, size_hint_y=None, height=dp(8))
        content.add_widget(progress)
        
        self._loading_popup = Popup(
            title='',
            content=content,
            size_hint=(0.75, 0.35),
            auto_dismiss=False,
            separator_height=0,
            background_color=[0.1, 0.1, 0.18, 0.95]
        )
        self._loading_popup.open()
    
    def hide_loading(self):
        if hasattr(self, '_loading_popup'):
            self._loading_popup.dismiss()
    
    def show_popup(self, title, message, popup_type='info'):
        icons = {'info': 'ℹ️', 'success': '✅', 'error': '❌', 'warning': '⚠️'}
        colors = {'info': COLORS['primary'], 'success': COLORS['success'], 
                  'error': COLORS['danger'], 'warning': COLORS['warning']}
        
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        
        icon = Label(text=icons.get(popup_type, 'ℹ️'), font_size=dp(45))
        content.add_widget(icon)
        
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
            background_color=get_color_from_hex(colors.get(popup_type, COLORS['primary']))
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
    
    def go_back(self):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'welcome'


class ChannelListScreen(Screen):
    """Kanal grupları listesi"""
    
    def on_enter(self):
        self.clear_widgets()
        self.selected_groups = set()
        Clock.schedule_once(lambda dt: self.build_ui(), 0.05)
    
    def build_ui(self):
        app = App.get_running_app()
        groups = getattr(app, 'groups', {})
        channels = getattr(app, 'channels', [])
        
        root = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(12))
        
        # Top bar
        top_bar = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(10))
        
        back_btn = Button(
            text='◀',
            size_hint=(None, None),
            size=(dp(48), dp(42)),
            font_size=dp(18),
            background_normal='',
            background_color=get_color_from_hex(COLORS['bg_card'])
        )
        back_btn.bind(on_press=lambda x: self.go_back())
        top_bar.add_widget(back_btn)
        
        title = Label(
            text='📺 Kanal Grupları',
            font_size=dp(17),
            bold=True,
            color=get_color_from_hex(COLORS['text_white'])
        )
        top_bar.add_widget(title)
        
        root.add_widget(top_bar)
        
        # Stats
        stats_label = Label(
            text=f'📊 {len(groups)} grup • {len(channels)} kanal',
            font_size=dp(13),
            color=get_color_from_hex(COLORS['text_gray']),
            size_hint_y=None,
            height=dp(25)
        )
        root.add_widget(stats_label)
        
        # Selection info
        self.selection_label = Label(
            text='✓ Seçilen: 0 grup (0 kanal)',
            font_size=dp(12),
            color=get_color_from_hex(COLORS['success']),
            size_hint_y=None,
            height=dp(22)
        )
        root.add_widget(self.selection_label)
        
        # Channel list
        scroll = ScrollView()
        self.list_layout = BoxLayout(orientation='vertical', spacing=dp(8), size_hint_y=None)
        self.list_layout.bind(minimum_height=self.list_layout.setter('height'))
        
        self.group_cards = {}
        for group_name, group_data in sorted(groups.items()):
            card = ChannelGroupCard(on_select_callback=self.on_group_select)
            card.group_name = group_name
            card.channel_count = len(group_data['channels'])
            card.logo_url = group_data.get('logo', '')
            self.group_cards[group_name] = card
            self.list_layout.add_widget(card)
        
        scroll.add_widget(self.list_layout)
        root.add_widget(scroll)
        
        # Bottom buttons
        bottom_bar = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        
        select_all_btn = Button(
            text='Tümünü Seç',
            font_size=dp(14),
            bold=True,
            background_normal='',
            background_color=get_color_from_hex(COLORS['primary'])
        )
        select_all_btn.bind(on_press=self.select_all)
        bottom_bar.add_widget(select_all_btn)
        
        export_btn = Button(
            text='📤 Dışa Aktar',
            font_size=dp(14),
            bold=True,
            background_normal='',
            background_color=get_color_from_hex(COLORS['success'])
        )
        export_btn.bind(on_press=self.export_selected)
        bottom_bar.add_widget(export_btn)
        
        root.add_widget(bottom_bar)
        self.add_widget(root)
    
    def on_group_select(self, group_name, selected):
        app = App.get_running_app()
        groups = getattr(app, 'groups', {})
        
        if selected:
            self.selected_groups.add(group_name)
        else:
            self.selected_groups.discard(group_name)
        
        # Count selected channels
        total_channels = sum(len(groups[g]['channels']) for g in self.selected_groups if g in groups)
        self.selection_label.text = f'✓ Seçilen: {len(self.selected_groups)} grup ({total_channels} kanal)'
    
    def select_all(self, instance):
        app = App.get_running_app()
        groups = getattr(app, 'groups', {})
        
        for group_name, card in self.group_cards.items():
            if not card.selected:
                card.selected = True
                self.selected_groups.add(group_name)
        
        total_channels = sum(len(groups[g]['channels']) for g in self.selected_groups if g in groups)
        self.selection_label.text = f'✓ Seçilen: {len(self.selected_groups)} grup ({total_channels} kanal)'
    
    def export_selected(self, instance):
        if not self.selected_groups:
            self.show_popup('Uyarı', 'Lütfen en az bir grup seçin!', 'warning')
            return
        
        app = App.get_running_app()
        groups = getattr(app, 'groups', {})
        selected_format = getattr(app, 'selected_format', 'm3u8')
        
        # Collect selected channels
        selected_channels = []
        for group_name in self.selected_groups:
            if group_name in groups:
                selected_channels.extend(groups[group_name]['channels'])
        
        # Generate content
        if selected_format == 'txt':
            content = generate_txt(selected_channels)
            ext = '.txt'
        else:
            content = generate_m3u(selected_channels, selected_format)
            ext = FILE_FORMATS.get(selected_format, {}).get('ext', '.m3u')
        
        # Save file
        download_path = get_download_path()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'iptv_export_{timestamp}{ext}'
        filepath = os.path.join(download_path, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.show_popup(
                'Başarılı! ✅',
                f'{len(selected_channels)} kanal kaydedildi!\n\n📁 {filename}\n📂 Download klasörü',
                'success'
            )
        except Exception as e:
            self.show_popup('Hata', f'Kaydetme hatası: {str(e)[:50]}', 'error')
    
    def show_popup(self, title, message, popup_type='info'):
        icons = {'success': '✅', 'error': '❌', 'warning': '⚠️'}
        colors = {'success': COLORS['success'], 'error': COLORS['danger'], 'warning': COLORS['warning']}
        
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        
        icon = Label(text=icons.get(popup_type, '✅'), font_size=dp(45))
        content.add_widget(icon)
        
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
            background_color=get_color_from_hex(colors.get(popup_type, COLORS['success']))
        )
        
        popup = Popup(title='', content=content, size_hint=(0.85, 0.45), separator_height=0)
        btn.bind(on_press=popup.dismiss)
        content.add_widget(btn)
        popup.open()
    
    def go_back(self):
        app = App.get_running_app()
        source = getattr(app, 'source_mode', 'manual')
        
        self.manager.transition = SlideTransition(direction='right')
        if source == 'manual':
            self.manager.current = 'manual_input'
        else:
            self.manager.current = 'auto_result'


class AutoInputScreen(Screen):
    """Otomatik mod - Toplu link giriş"""
    
    def on_enter(self):
        self.clear_widgets()
        self.test_mode = 'deep'
        Clock.schedule_once(lambda dt: self.build_ui(), 0.05)
    
    def build_ui(self):
        root = BoxLayout(orientation='vertical', padding=dp(18), spacing=dp(15))
        
        # Top bar
        top_bar = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(10))
        
        back_btn = Button(
            text='◀',
            size_hint=(None, None),
            size=(dp(48), dp(42)),
            font_size=dp(18),
            background_normal='',
            background_color=get_color_from_hex(COLORS['bg_card'])
        )
        back_btn.bind(on_press=lambda x: self.go_back())
        top_bar.add_widget(back_btn)
        
        title = Label(
            text='🤖 Otomatik Düzenleme',
            font_size=dp(18),
            bold=True,
            color=get_color_from_hex(COLORS['text_white'])
        )
        top_bar.add_widget(title)
        
        root.add_widget(top_bar)
        
        # Description
        desc = Label(
            text='IPTV linklerini her satıra bir tane olacak şekilde girin.\nTüm linkler sırayla test edilecek.',
            font_size=dp(12),
            color=get_color_from_hex(COLORS['text_gray']),
            size_hint_y=None,
            height=dp(38),
            halign='center'
        )
        desc.bind(size=lambda w, s: setattr(w, 'text_size', s))
        root.add_widget(desc)
        
        # Links input
        input_card = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(8))
        input_card.bind(size=self._update_card, pos=self._update_card)
        self._input_card = input_card
        
        input_label = Label(
            text='IPTV Linkleri (her satıra bir link)',
            font_size=dp(12),
            color=get_color_from_hex(COLORS['text_gray']),
            size_hint_y=None,
            height=dp(20),
            halign='left'
        )
        input_label.bind(size=lambda w, s: setattr(w, 'text_size', s))
        input_card.add_widget(input_label)
        
        self.links_input = TextInput(
            hint_text='https://example1.com/playlist.m3u\nhttps://example2.com/playlist.m3u\nhttps://example3.com/playlist.m3u',
            multiline=True,
            font_size=dp(12),
            background_color=get_color_from_hex(COLORS['bg_medium']),
            foreground_color=get_color_from_hex(COLORS['text_white']),
            cursor_color=get_color_from_hex(COLORS['primary']),
            padding=[dp(12), dp(10)]
        )
        input_card.add_widget(self.links_input)
        
        root.add_widget(input_card)
        
        # Test mode selection
        mode_card = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(10), size_hint_y=None, height=dp(105))
        mode_card.bind(size=self._update_card, pos=self._update_card)
        self._mode_card = mode_card
        
        mode_label = Label(
            text='Test Yöntemi',
            font_size=dp(12),
            color=get_color_from_hex(COLORS['text_gray']),
            size_hint_y=None,
            height=dp(20),
            halign='left'
        )
        mode_label.bind(size=lambda w, s: setattr(w, 'text_size', s))
        mode_card.add_widget(mode_label)
        
        mode_btns = BoxLayout(spacing=dp(10), size_hint_y=None, height=dp(48))
        
        self.quick_btn = ToggleButton(
            text='⚡ Hızlı Test\nSadece bağlantı',
            group='test_mode',
            state='normal',
            font_size=dp(11),
            background_normal='',
            background_color=get_color_from_hex(COLORS['bg_card'])
        )
        self.quick_btn.bind(on_press=lambda x: self.set_test_mode('quick'))
        mode_btns.add_widget(self.quick_btn)
        
        self.deep_btn = ToggleButton(
            text='🔍 Derin Test ⭐\nVideo akışı kontrolü',
            group='test_mode',
            state='down',
            font_size=dp(11),
            background_normal='',
            background_color=get_color_from_hex(COLORS['primary'])
        )
        self.deep_btn.bind(on_press=lambda x: self.set_test_mode('deep'))
        mode_btns.add_widget(self.deep_btn)
        
        mode_card.add_widget(mode_btns)
        root.add_widget(mode_card)
        
        # Start button
        start_btn = Button(
            text='🚀 Test Başlat',
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
        Clock.schedule_once(lambda dt: self._draw_cards(), 0.1)
    
    def _update_card(self, widget, value):
        Clock.schedule_once(lambda dt: self._draw_single_card(widget), 0)
    
    def _draw_cards(self):
        self._draw_single_card(self._input_card)
        self._draw_single_card(self._mode_card)
    
    def _draw_single_card(self, card):
        from kivy.graphics import Color, RoundedRectangle
        card.canvas.before.clear()
        with card.canvas.before:
            Color(*get_color_from_hex(COLORS['bg_card']))
            RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(12)])
    
    def set_test_mode(self, mode):
        self.test_mode = mode
        if mode == 'quick':
            self.quick_btn.background_color = get_color_from_hex(COLORS['primary'])
            self.deep_btn.background_color = get_color_from_hex(COLORS['bg_card'])
        else:
            self.quick_btn.background_color = get_color_from_hex(COLORS['bg_card'])
            self.deep_btn.background_color = get_color_from_hex(COLORS['primary'])
    
    def start_testing(self, instance):
        links_text = self.links_input.text.strip()
        
        if not links_text:
            self.show_popup('Hata', 'Lütfen en az bir link girin!', 'error')
            return
        
        # Parse links
        links = []
        for line in links_text.split('\n'):
            line = line.strip()
            if line.startswith('http'):
                links.append(line)
        
        if not links:
            self.show_popup('Hata', 'Geçerli link bulunamadı!\nLinkler http veya https ile başlamalı.', 'error')
            return
        
        app = App.get_running_app()
        app.links_to_test = links
        app.test_mode = self.test_mode
        
        self.manager.current = 'testing'
    
    def show_popup(self, title, message, popup_type='info'):
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        
        icon = Label(text='❌' if popup_type == 'error' else 'ℹ️', font_size=dp(45))
        content.add_widget(icon)
        
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
            background_color=get_color_from_hex(COLORS['danger'])
        )
        
        popup = Popup(title='', content=content, size_hint=(0.8, 0.4), separator_height=0)
        btn.bind(on_press=popup.dismiss)
        content.add_widget(btn)
        popup.open()
    
    def go_back(self):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'welcome'


class TestingScreen(Screen):
    """Link test ekranı"""
    
    def on_enter(self):
        self.clear_widgets()
        self.testing = True
        self.working_links = []
        self.failed_links = []
        Clock.schedule_once(lambda dt: self.build_ui(), 0.05)
        Clock.schedule_once(lambda dt: self.start_tests(), 0.2)
    
    def build_ui(self):
        root = BoxLayout(orientation='vertical', padding=dp(18), spacing=dp(15))
        
        # Title
        title = Label(
            text='🔍 Linkler Test Ediliyor...',
            font_size=dp(20),
            bold=True,
            color=get_color_from_hex(COLORS['text_white']),
            size_hint_y=None,
            height=dp(45)
        )
        root.add_widget(title)
        
        # Progress card
        progress_card = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(12), size_hint_y=None, height=dp(130))
        progress_card.bind(size=self._update_card, pos=self._update_card)
        self._progress_card = progress_card
        
        self.progress_label = Label(
            text='Hazırlanıyor...',
            font_size=dp(15),
            color=get_color_from_hex(COLORS['text_white']),
            size_hint_y=None,
            height=dp(25)
        )
        progress_card.add_widget(self.progress_label)
        
        self.progress_bar = ProgressBar(max=100, value=0, size_hint_y=None, height=dp(12))
        progress_card.add_widget(self.progress_bar)
        
        self.stats_label = Label(
            text='✅ 0 Çalışan  •  ❌ 0 Başarısız',
            font_size=dp(13),
            color=get_color_from_hex(COLORS['text_gray']),
            size_hint_y=None,
            height=dp(25)
        )
        progress_card.add_widget(self.stats_label)
        
        root.add_widget(progress_card)
        
        # Log area
        log_card = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(8))
        log_card.bind(size=self._update_card, pos=self._update_card)
        self._log_card = log_card
        
        log_title = Label(
            text='📋 Test Günlüğü',
            font_size=dp(13),
            color=get_color_from_hex(COLORS['text_gray']),
            size_hint_y=None,
            height=dp(22),
            halign='left'
        )
        log_title.bind(size=lambda w, s: setattr(w, 'text_size', s))
        log_card.add_widget(log_title)
        
        scroll = ScrollView()
        self.log_layout = BoxLayout(orientation='vertical', spacing=dp(4), size_hint_y=None)
        self.log_layout.bind(minimum_height=self.log_layout.setter('height'))
        scroll.add_widget(self.log_layout)
        log_card.add_widget(scroll)
        
        root.add_widget(log_card)
        
        # Cancel button
        self.action_btn = Button(
            text='❌ İptal Et',
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
        Clock.schedule_once(lambda dt: self._draw_cards(), 0.1)
    
    def _update_card(self, widget, value):
        Clock.schedule_once(lambda dt: self._draw_single_card(widget), 0)
    
    def _draw_cards(self):
        self._draw_single_card(self._progress_card)
        self._draw_single_card(self._log_card)
    
    def _draw_single_card(self, card):
        from kivy.graphics import Color, RoundedRectangle
        card.canvas.before.clear()
        with card.canvas.before:
            Color(*get_color_from_hex(COLORS['bg_card']))
            RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(12)])
    
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
            
            # Log testing
            domain = urlparse(link).netloc or link[:30]
            Clock.schedule_once(lambda dt, d=domain: self.add_log(f'⏳ Test ediliyor: {d}', 'testing'))
            
            # Test link
            if test_mode == 'quick':
                success, message = test_link_quick(link)
            else:
                success, message = test_link_deep(link)
            
            if success:
                self.working_links.append(link)
                Clock.schedule_once(lambda dt, d=domain: self.add_log(f'✅ Çalışıyor: {d}', 'success'))
            else:
                self.failed_links.append({'link': link, 'reason': message})
                Clock.schedule_once(lambda dt, d=domain, m=message: self.add_log(f'❌ Başarısız: {d} ({m})', 'error'))
            
            # Update progress
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
            height=dp(22),
            halign='left'
        )
        log_item.bind(size=lambda w, s: setattr(w, 'text_size', s))
        self.log_layout.add_widget(log_item)
    
    def update_progress(self, progress, current, total):
        self.progress_bar.value = progress
        self.progress_label.text = f'Test ediliyor: {current}/{total}'
        self.stats_label.text = f'✅ {len(self.working_links)} Çalışan  •  ❌ {len(self.failed_links)} Başarısız'
    
    def tests_complete(self):
        self.testing = False
        self.progress_label.text = '✅ Test tamamlandı!'
        self.action_btn.text = '➡️ Devam Et'
        self.action_btn.background_color = get_color_from_hex(COLORS['success'])
        
        app = App.get_running_app()
        app.working_links = self.working_links
        app.failed_links = self.failed_links
    
    def on_action(self, instance):
        if self.action_btn.text == '❌ İptal Et':
            self.testing = False
            self.manager.transition = SlideTransition(direction='right')
            self.manager.current = 'auto_input'
        else:
            if not self.working_links:
                self.show_no_links_popup()
            else:
                self.manager.current = 'auto_result'
    
    def show_no_links_popup(self):
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        
        icon = Label(text='😞', font_size=dp(50))
        content.add_widget(icon)
        
        msg = Label(
            text='Çalışan link bulunamadı!\n\nLütfen farklı linkler deneyin.',
            font_size=dp(14),
            color=get_color_from_hex(COLORS['text_white']),
            halign='center'
        )
        msg.bind(size=lambda w, s: setattr(w, 'text_size', s))
        content.add_widget(msg)
        
        btn = Button(
            text='Geri Dön',
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


class AutoResultScreen(Screen):
    """Test sonuçları - Düzenleme modu seçimi"""
    
    def on_enter(self):
        self.clear_widgets()
        Clock.schedule_once(lambda dt: self.build_ui(), 0.05)
    
    def build_ui(self):
        app = App.get_running_app()
        working = len(getattr(app, 'working_links', []))
        failed = len(getattr(app, 'failed_links', []))
        
        root = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(18))
        
        # Title
        title = Label(
            text='🎉 Test Tamamlandı!',
            font_size=dp(22),
            bold=True,
            color=get_color_from_hex(COLORS['text_white']),
            size_hint_y=None,
            height=dp(45)
        )
        root.add_widget(title)
        
        # Results card
        result_card = BoxLayout(orientation='horizontal', padding=dp(20), spacing=dp(20), size_hint_y=None, height=dp(110))
        result_card.bind(size=self._update_card, pos=self._update_card)
        self._result_card = result_card
        
        # Working count
        working_box = BoxLayout(orientation='vertical')
        working_box.add_widget(Label(text='✅', font_size=dp(35)))
        working_box.add_widget(Label(text=str(working), font_size=dp(28), bold=True, 
                                     color=get_color_from_hex(COLORS['success'])))
        working_box.add_widget(Label(text='Çalışan', font_size=dp(12), 
                                     color=get_color_from_hex(COLORS['text_gray'])))
        result_card.add_widget(working_box)
        
        # Failed count
        failed_box = BoxLayout(orientation='vertical')
        failed_box.add_widget(Label(text='❌', font_size=dp(35)))
        failed_box.add_widget(Label(text=str(failed), font_size=dp(28), bold=True,
                                    color=get_color_from_hex(COLORS['danger'])))
        failed_box.add_widget(Label(text='Başarısız', font_size=dp(12),
                                    color=get_color_from_hex(COLORS['text_gray'])))
        result_card.add_widget(failed_box)
        
        root.add_widget(result_card)
        
        # Question
        question = Label(
            text='Çalışan linkleri nasıl düzenlemek istersiniz?',
            font_size=dp(15),
            color=get_color_from_hex(COLORS['text_white']),
            size_hint_y=None,
            height=dp(35)
        )
        root.add_widget(question)
        
        # Option cards
        options = BoxLayout(orientation='vertical', spacing=dp(12))
        
        # Auto option
        auto_card = BoxLayout(orientation='vertical', padding=dp(18), spacing=dp(10), size_hint_y=None, height=dp(130))
        auto_card.bind(size=self._update_card, pos=self._update_card)
        self._auto_card = auto_card
        
        auto_header = BoxLayout(size_hint_y=None, height=dp(35))
        auto_header.add_widget(Label(text='🤖', font_size=dp(28), size_hint_x=None, width=dp(45)))
        auto_header.add_widget(Label(text='Otomatik Düzenleme', font_size=dp(16), bold=True,
                                     color=get_color_from_hex(COLORS['text_white']), halign='left'))
        auto_card.add_widget(auto_header)
        
        auto_desc = Label(
            text='Ülke seçin, kanallar otomatik filtrelensin ve birleştirilsin',
            font_size=dp(12),
            color=get_color_from_hex(COLORS['text_gray']),
            size_hint_y=None,
            height=dp(22)
        )
        auto_card.add_widget(auto_desc)
        
        auto_btn = Button(
            text='Otomatik Düzenle',
            size_hint=(0.7, None),
            height=dp(40),
            pos_hint={'center_x': 0.5},
            background_normal='',
            background_color=get_color_from_hex(COLORS['primary'])
        )
        auto_btn.bind(on_press=lambda x: self.go_auto())
        auto_card.add_widget(auto_btn)
        options.add_widget(auto_card)
        
        # Manual option
        manual_card = BoxLayout(orientation='vertical', padding=dp(18), spacing=dp(10), size_hint_y=None, height=dp(130))
        manual_card.bind(size=self._update_card, pos=self._update_card)
        self._manual_card = manual_card
        
        manual_header = BoxLayout(size_hint_y=None, height=dp(35))
        manual_header.add_widget(Label(text='✏️', font_size=dp(28), size_hint_x=None, width=dp(45)))
        manual_header.add_widget(Label(text='Manuel Düzenleme', font_size=dp(16), bold=True,
                                       color=get_color_from_hex(COLORS['text_white']), halign='left'))
        manual_card.add_widget(manual_header)
        
        manual_desc = Label(
            text='Her linki tek tek düzenleyin, istediğiniz kanalları seçin',
            font_size=dp(12),
            color=get_color_from_hex(COLORS['text_gray']),
            size_hint_y=None,
            height=dp(22)
        )
        manual_card.add_widget(manual_desc)
        
        manual_btn = Button(
            text='Manuel Düzenle',
            size_hint=(0.7, None),
            height=dp(40),
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
            text='◀ Geri',
            size_hint_y=None,
            height=dp(42),
            background_normal='',
            background_color=get_color_from_hex(COLORS['bg_card'])
        )
        back_btn.bind(on_press=lambda x: self.go_back())
        root.add_widget(back_btn)
        
        self.add_widget(root)
        Clock.schedule_once(lambda dt: self._draw_cards(), 0.1)
    
    def _update_card(self, widget, value):
        Clock.schedule_once(lambda dt: self._draw_single_card(widget), 0)
    
    def _draw_cards(self):
        self._draw_single_card(self._result_card)
        self._draw_single_card(self._auto_card)
        self._draw_single_card(self._manual_card)
    
    def _draw_single_card(self, card):
        from kivy.graphics import Color, RoundedRectangle
        card.canvas.before.clear()
        with card.canvas.before:
            Color(*get_color_from_hex(COLORS['bg_card']))
            RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(12)])
    
    def go_auto(self):
        self.manager.current = 'country_select'
    
    def go_manual(self):
        self.manager.current = 'manual_link_list'
    
    def go_back(self):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'auto_input'


class CountrySelectScreen(Screen):
    """Ülke seçim ekranı"""
    
    def on_enter(self):
        self.clear_widgets()
        self.selected_countries = set()
        self.selected_format = 'm3u8'
        Clock.schedule_once(lambda dt: self.build_ui(), 0.05)
    
    def build_ui(self):
        root = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(12))
        
        # Top bar
        top_bar = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(10))
        
        back_btn = Button(
            text='◀',
            size_hint=(None, None),
            size=(dp(48), dp(42)),
            font_size=dp(18),
            background_normal='',
            background_color=get_color_from_hex(COLORS['bg_card'])
        )
        back_btn.bind(on_press=lambda x: self.go_back())
        top_bar.add_widget(back_btn)
        
        title = Label(
            text='🌍 Ülke Seçimi',
            font_size=dp(18),
            bold=True,
            color=get_color_from_hex(COLORS['text_white'])
        )
        top_bar.add_widget(title)
        
        root.add_widget(top_bar)
        
        # Description
        desc = Label(
            text='Hangi ülkelerin kanallarını istiyorsunuz?',
            font_size=dp(13),
            color=get_color_from_hex(COLORS['text_gray']),
            size_hint_y=None,
            height=dp(25)
        )
        root.add_widget(desc)
        
        # Selection info
        self.selection_label = Label(
            text='✓ Seçilen: 0 ülke',
            font_size=dp(12),
            color=get_color_from_hex(COLORS['success']),
            size_hint_y=None,
            height=dp(22)
        )
        root.add_widget(self.selection_label)
        
        # Country grid
        scroll = ScrollView()
        self.country_grid = GridLayout(cols=2, spacing=dp(10), size_hint_y=None, padding=dp(5))
        self.country_grid.bind(minimum_height=self.country_grid.setter('height'))
        
        self.country_buttons = {}
        
        # Priority countries first
        for country_id in PRIORITY_COUNTRIES:
            country_data = COUNTRIES[country_id]
            btn = self._create_country_button(country_id, country_data, priority=True)
            self.country_grid.add_widget(btn)
        
        # Other countries
        for country_id, country_data in sorted(COUNTRIES.items(), key=lambda x: x[1]['priority']):
            if country_id not in PRIORITY_COUNTRIES:
                btn = self._create_country_button(country_id, country_data)
                self.country_grid.add_widget(btn)
        
        scroll.add_widget(self.country_grid)
        root.add_widget(scroll)
        
        # Format selection
        format_box = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
        
        format_label = Label(
            text='Format:',
            size_hint_x=None,
            width=dp(55),
            font_size=dp(13),
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
                background_color=get_color_from_hex(COLORS['primary']) if fmt_id == 'm3u8' else get_color_from_hex(COLORS['bg_card'])
            )
            btn.format_id = fmt_id
            btn.bind(on_press=self.on_format_select)
            self.format_buttons[fmt_id] = btn
            format_box.add_widget(btn)
        
        root.add_widget(format_box)
        
        # Process button
        process_btn = Button(
            text='🚀 Oluştur',
            font_size=dp(16),
            bold=True,
            size_hint_y=None,
            height=dp(52),
            background_normal='',
            background_color=get_color_from_hex(COLORS['success'])
        )
        process_btn.bind(on_press=self.start_process)
        root.add_widget(process_btn)
        
        self.add_widget(root)
    
    def _create_country_button(self, country_id, country_data, priority=False):
        btn = ToggleButton(
            text=f"{country_data['flag']} {country_data['name']}",
            size_hint_y=None,
            height=dp(55),
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
        
        self.selection_label.text = f'✓ Seçilen: {len(self.selected_countries)} ülke'
    
    def on_format_select(self, btn):
        self.selected_format = btn.format_id
        for fmt_id, button in self.format_buttons.items():
            if fmt_id == self.selected_format:
                button.background_color = get_color_from_hex(COLORS['primary'])
            else:
                button.background_color = get_color_from_hex(COLORS['bg_card'])
    
    def start_process(self, instance):
        if not self.selected_countries:
            self.show_popup('Uyarı', 'Lütfen en az bir ülke seçin!', 'warning')
            return
        
        app = App.get_running_app()
        app.selected_countries = self.selected_countries
        app.output_format = self.selected_format
        
        self.manager.current = 'processing'
    
    def show_popup(self, title, message, popup_type='info'):
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        
        icon = Label(text='⚠️', font_size=dp(45))
        content.add_widget(icon)
        
        msg = Label(
            text=message,
            font_size=dp(14),
            color=get_color_from_hex(COLORS['text_white']),
            halign='center'
        )
        content.add_widget(msg)
        
        btn = Button(
            text='Tamam',
            size_hint=(0.5, None),
            height=dp(42),
            pos_hint={'center_x': 0.5},
            background_normal='',
            background_color=get_color_from_hex(COLORS['warning'])
        )
        
        popup = Popup(title='', content=content, size_hint=(0.75, 0.35), separator_height=0)
        btn.bind(on_press=popup.dismiss)
        content.add_widget(btn)
        popup.open()
    
    def go_back(self):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'auto_result'


class ProcessingScreen(Screen):
    """İşleme ekranı"""
    
    def on_enter(self):
        self.clear_widgets()
        Clock.schedule_once(lambda dt: self.build_ui(), 0.05)
        Clock.schedule_once(lambda dt: self.start_processing(), 0.2)
    
    def build_ui(self):
        root = BoxLayout(orientation='vertical', padding=dp(25), spacing=dp(18))
        
        # Title
        title = Label(
            text='⚙️ İşleniyor...',
            font_size=dp(22),
            bold=True,
            color=get_color_from_hex(COLORS['text_white']),
            size_hint_y=None,
            height=dp(45)
        )
        root.add_widget(title)
        
        # Status
        self.status_label = Label(
            text='Linkler indiriliyor...',
            font_size=dp(14),
            color=get_color_from_hex(COLORS['text_gray']),
            size_hint_y=None,
            height=dp(28)
        )
        root.add_widget(self.status_label)
        
        # Progress bar
        self.progress_bar = ProgressBar(max=100, value=0, size_hint_y=None, height=dp(15))
        root.add_widget(self.progress_bar)
        
        # Stats card
        stats_card = BoxLayout(orientation='vertical', padding=dp(18), spacing=dp(12), size_hint_y=None, height=dp(140))
        stats_card.bind(size=self._update_card, pos=self._update_card)
        self._stats_card = stats_card
        
        self.total_label = Label(
            text='📺 Toplam Kanal: 0',
            font_size=dp(15),
            color=get_color_from_hex(COLORS['text_white'])
        )
        stats_card.add_widget(self.total_label)
        
        self.filtered_label = Label(
            text='✅ Filtrelenen: 0',
            font_size=dp(15),
            color=get_color_from_hex(COLORS['success'])
        )
        stats_card.add_widget(self.filtered_label)
        
        self.current_label = Label(
            text='🔗 İşlenen: -',
            font_size=dp(12),
            color=get_color_from_hex(COLORS['text_gray'])
        )
        stats_card.add_widget(self.current_label)
        
        root.add_widget(stats_card)
        
        # Spacer
        root.add_widget(Label())
        
        self.add_widget(root)
        Clock.schedule_once(lambda dt: self._draw_card(), 0.1)
    
    def _update_card(self, widget, value):
        Clock.schedule_once(lambda dt: self._draw_card(), 0)
    
    def _draw_card(self):
        from kivy.graphics import Color, RoundedRectangle
        self._stats_card.canvas.before.clear()
        with self._stats_card.canvas.before:
            Color(*get_color_from_hex(COLORS['bg_card']))
            RoundedRectangle(pos=self._stats_card.pos, size=self._stats_card.size, radius=[dp(12)])
    
    def start_processing(self):
        threading.Thread(target=self._process, daemon=True).start()
    
    def _process(self):
        app = App.get_running_app()
        working_links = getattr(app, 'working_links', [])
        selected_countries = getattr(app, 'selected_countries', set())
        output_format = getattr(app, 'output_format', 'm3u8')
        
        all_channels = []
        filtered_channels = []
        total_links = len(working_links)
        
        for i, link in enumerate(working_links):
            domain = urlparse(link).netloc or link[:25]
            Clock.schedule_once(lambda dt, d=domain: setattr(self.current_label, 'text', f'🔗 İşlenen: {d}'))
            Clock.schedule_once(lambda dt, p=((i+1)/total_links)*70: setattr(self.progress_bar, 'value', p))
            
            try:
                response = requests.get(link, timeout=30, headers={'User-Agent': 'Mozilla/5.0'})
                channels, groups = parse_m3u(response.text)
                
                for ch in channels:
                    all_channels.append(ch)
                    
                    # Detect country from group name and channel name
                    text_to_check = f"{ch.get('group', '')} {ch.get('name', '')}"
                    detected_country = detect_country(text_to_check)
                    
                    if detected_country in selected_countries:
                        ch['detected_country'] = detected_country
                        filtered_channels.append(ch)
                
                Clock.schedule_once(lambda dt, t=len(all_channels), f=len(filtered_channels): self._update_stats(t, f))
                
            except Exception as e:
                continue
        
        Clock.schedule_once(lambda dt: setattr(self.status_label, 'text', 'Dosya oluşturuluyor...'))
        Clock.schedule_once(lambda dt: setattr(self.progress_bar, 'value', 85))
        
        # Generate output
        if output_format == 'txt':
            content = generate_txt(filtered_channels)
            ext = '.txt'
        else:
            content = generate_m3u(filtered_channels, output_format)
            ext = FILE_FORMATS.get(output_format, {}).get('ext', '.m3u')
        
        # Save file
        download_path = get_download_path()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        countries_str = '_'.join(sorted(selected_countries)[:3])
        filename = f'iptv_{countries_str}_{timestamp}{ext}'
        filepath = os.path.join(download_path, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            pass
        
        app.output_filepath = filepath
        app.output_filename = filename
        app.filtered_channels = filtered_channels
        app.total_channels = all_channels
        
        Clock.schedule_once(lambda dt: setattr(self.progress_bar, 'value', 100))
        Clock.schedule_once(lambda dt: self._complete())
    
    def _update_stats(self, total, filtered):
        self.total_label.text = f'📺 Toplam Kanal: {total}'
        self.filtered_label.text = f'✅ Filtrelenen: {filtered}'
    
    def _complete(self):
        self.manager.current = 'complete'


class ManualLinkListScreen(Screen):
    """Manuel düzenleme - Link listesi"""
    
    def on_enter(self):
        self.clear_widgets()
        Clock.schedule_once(lambda dt: self.build_ui(), 0.05)
    
    def build_ui(self):
        app = App.get_running_app()
        working_links = getattr(app, 'working_links', [])
        
        root = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(12))
        
        # Top bar
        top_bar = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(10))
        
        back_btn = Button(
            text='◀',
            size_hint=(None, None),
            size=(dp(48), dp(42)),
            font_size=dp(18),
            background_normal='',
            background_color=get_color_from_hex(COLORS['bg_card'])
        )
        back_btn.bind(on_press=lambda x: self.go_back())
        top_bar.add_widget(back_btn)
        
        title = Label(
            text='✏️ Manuel Düzenleme',
            font_size=dp(17),
            bold=True,
            color=get_color_from_hex(COLORS['text_white'])
        )
        top_bar.add_widget(title)
        
        root.add_widget(top_bar)
        
        # Description
        desc = Label(
            text=f'{len(working_links)} çalışan link bulundu.\nDüzenlemek istediğiniz linke tıklayın.',
            font_size=dp(12),
            color=get_color_from_hex(COLORS['text_gray']),
            size_hint_y=None,
            height=dp(40),
            halign='center'
        )
        desc.bind(size=lambda w, s: setattr(w, 'text_size', s))
        root.add_widget(desc)
        
        # Link list
        scroll = ScrollView()
        list_layout = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None)
        list_layout.bind(minimum_height=list_layout.setter('height'))
        
        for i, link in enumerate(working_links):
            item = self._create_link_item(i + 1, link)
            list_layout.add_widget(item)
        
        scroll.add_widget(list_layout)
        root.add_widget(scroll)
        
        self.add_widget(root)
    
    def _create_link_item(self, index, link):
        item = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(70), 
                        padding=dp(12), spacing=dp(10))
        item.bind(size=self._update_item, pos=self._update_item)
        item._is_card = True
        
        # Index
        index_label = Label(
            text=str(index),
            font_size=dp(18),
            bold=True,
            color=get_color_from_hex(COLORS['primary']),
            size_hint_x=None,
            width=dp(35)
        )
        item.add_widget(index_label)
        
        # Link info
        info = BoxLayout(orientation='vertical', spacing=dp(2))
        
        domain = urlparse(link).netloc or link[:25]
        domain_label = Label(
            text=domain,
            font_size=dp(13),
            color=get_color_from_hex(COLORS['text_white']),
            halign='left'
        )
        domain_label.bind(size=lambda w, s: setattr(w, 'text_size', s))
        
        link_short = link[:45] + '...' if len(link) > 45 else link
        link_label = Label(
            text=link_short,
            font_size=dp(10),
            color=get_color_from_hex(COLORS['text_gray']),
            halign='left'
        )
        link_label.bind(size=lambda w, s: setattr(w, 'text_size', s))
        
        info.add_widget(domain_label)
        info.add_widget(link_label)
        item.add_widget(info)
        
        # Edit button
        edit_btn = Button(
            text='📝',
            size_hint=(None, None),
            size=(dp(48), dp(48)),
            font_size=dp(20),
            background_normal='',
            background_color=get_color_from_hex(COLORS['primary'])
        )
        edit_btn.link_url = link
        edit_btn.link_index = index
        edit_btn.bind(on_press=self.edit_link)
        item.add_widget(edit_btn)
        
        return item
    
    def _update_item(self, widget, value):
        if getattr(widget, '_is_card', False):
            Clock.schedule_once(lambda dt: self._draw_item(widget), 0)
    
    def _draw_item(self, item):
        from kivy.graphics import Color, RoundedRectangle
        item.canvas.before.clear()
        with item.canvas.before:
            Color(*get_color_from_hex(COLORS['bg_card']))
            RoundedRectangle(pos=item.pos, size=item.size, radius=[dp(10)])
    
    def edit_link(self, btn):
        app = App.get_running_app()
        app.current_edit_link = btn.link_url
        app.current_edit_index = btn.link_index
        app.source_mode = 'auto_manual'
        
        self.manager.current = 'link_editor'
    
    def go_back(self):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'auto_result'


class LinkEditorScreen(Screen):
    """Tek link düzenleme ekranı"""
    
    def on_enter(self):
        self.clear_widgets()
        self.selected_groups = set()
        self.channels = []
        self.groups = {}
        Clock.schedule_once(lambda dt: self.build_ui(), 0.05)
        Clock.schedule_once(lambda dt: self.load_link(), 0.1)
    
    def build_ui(self):
        app = App.get_running_app()
        link_index = getattr(app, 'current_edit_index', 1)
        working_links = getattr(app, 'working_links', [])
        
        root = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        
        # Top bar
        top_bar = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(10))
        
        back_btn = Button(
            text='◀',
            size_hint=(None, None),
            size=(dp(48), dp(42)),
            font_size=dp(18),
            background_normal='',
            background_color=get_color_from_hex(COLORS['bg_card'])
        )
        back_btn.bind(on_press=lambda x: self.go_back())
        top_bar.add_widget(back_btn)
        
        title = Label(
            text=f'Link {link_index}/{len(working_links)}',
            font_size=dp(16),
            bold=True,
            color=get_color_from_hex(COLORS['text_white'])
        )
        top_bar.add_widget(title)
        
        root.add_widget(top_bar)
        
        # Loading indicator
        self.loading_label = Label(
            text='⏳ Kanallar yükleniyor...',
            font_size=dp(15),
            color=get_color_from_hex(COLORS['text_gray'])
        )
        root.add_widget(self.loading_label)
        
        # Content (hidden initially)
        self.content_layout = BoxLayout(orientation='vertical', spacing=dp(10), opacity=0)
        
        self.stats_label = Label(
            text='',
            font_size=dp(13),
            color=get_color_from_hex(COLORS['text_gray']),
            size_hint_y=None,
            height=dp(25)
        )
        self.content_layout.add_widget(self.stats_label)
        
        self.selection_label = Label(
            text='✓ Seçilen: 0 grup',
            font_size=dp(12),
            color=get_color_from_hex(COLORS['success']),
            size_hint_y=None,
            height=dp(22)
        )
        self.content_layout.add_widget(self.selection_label)
        
        scroll = ScrollView()
        self.list_layout = BoxLayout(orientation='vertical', spacing=dp(8), size_hint_y=None)
        self.list_layout.bind(minimum_height=self.list_layout.setter('height'))
        scroll.add_widget(self.list_layout)
        self.content_layout.add_widget(scroll)
        
        root.add_widget(self.content_layout)
        
        # Bottom buttons
        self.bottom_bar = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10), opacity=0)
        
        save_btn = Button(
            text='💾 Kaydet',
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
            self.channels, self.groups = parse_m3u(response.text)
            Clock.schedule_once(lambda dt: self._display_content())
        except Exception as e:
            Clock.schedule_once(lambda dt: self._show_error(str(e)[:50]))
    
    def _display_content(self):
        self.loading_label.opacity = 0
        self.content_layout.opacity = 1
        self.bottom_bar.opacity = 1
        
        self.stats_label.text = f'📊 {len(self.groups)} grup • {len(self.channels)} kanal'
        
        self.group_cards = {}
        for group_name, group_data in sorted(self.groups.items()):
            card = ChannelGroupCard(on_select_callback=self.on_group_select)
            card.group_name = group_name
            card.channel_count = len(group_data['channels'])
            self.group_cards[group_name] = card
            self.list_layout.add_widget(card)
    
    def _show_error(self, error):
        self.loading_label.text = f'❌ Hata: {error}'
    
    def on_group_select(self, group_name, selected):
        if selected:
            self.selected_groups.add(group_name)
        else:
            self.selected_groups.discard(group_name)
        
        total_channels = sum(len(self.groups[g]['channels']) for g in self.selected_groups if g in self.groups)
        self.selection_label.text = f'✓ Seçilen: {len(self.selected_groups)} grup ({total_channels} kanal)'
    
    def save_selection(self, instance):
        if not self.selected_groups:
            self.show_popup('Uyarı', 'Lütfen en az bir grup seçin!', 'warning')
            return
        
        selected_channels = []
        for group_name in self.selected_groups:
            if group_name in self.groups:
                selected_channels.extend(self.groups[group_name]['channels'])
        
        content = generate_m3u(selected_channels)
        
        app = App.get_running_app()
        link_index = getattr(app, 'current_edit_index', 1)
        
        download_path = get_download_path()
        timestamp = datetime.now().strftime('%H%M%S')
        filename = f'iptv_link{link_index}_{timestamp}.m3u'
        filepath = os.path.join(download_path, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.show_save_success(filename, len(selected_channels))
        except Exception as e:
            self.show_popup('Hata', f'Kaydetme hatası: {str(e)[:50]}', 'error')
    
    def show_popup(self, title, message, popup_type='info'):
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        
        icon = Label(text='⚠️', font_size=dp(45))
        content.add_widget(icon)
        
        msg = Label(
            text=message,
            font_size=dp(14),
            color=get_color_from_hex(COLORS['text_white']),
            halign='center'
        )
        content.add_widget(msg)
        
        btn = Button(
            text='Tamam',
            size_hint=(0.5, None),
            height=dp(42),
            pos_hint={'center_x': 0.5},
            background_normal='',
            background_color=get_color_from_hex(COLORS['warning'])
        )
        
        popup = Popup(title='', content=content, size_hint=(0.75, 0.35), separator_height=0)
        btn.bind(on_press=popup.dismiss)
        content.add_widget(btn)
        popup.open()
    
    def show_save_success(self, filename, channel_count):
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        
        icon = Label(text='✅', font_size=dp(50))
        content.add_widget(icon)
        
        title_lbl = Label(
            text='Başarıyla Kaydedildi!',
            font_size=dp(17),
            bold=True,
            color=get_color_from_hex(COLORS['text_white'])
        )
        content.add_widget(title_lbl)
        
        info_lbl = Label(
            text=f'{channel_count} kanal\n📁 {filename}',
            font_size=dp(12),
            color=get_color_from_hex(COLORS['text_gray']),
            halign='center'
        )
        content.add_widget(info_lbl)
        
        btn = Button(
            text='Listeye Dön',
            size_hint=(0.6, None),
            height=dp(42),
            pos_hint={'center_x': 0.5},
            background_normal='',
            background_color=get_color_from_hex(COLORS['primary'])
        )
        
        popup = Popup(title='', content=content, size_hint=(0.8, 0.45), separator_height=0)
        
        def go_list(x):
            popup.dismiss()
            self.manager.transition = SlideTransition(direction='right')
            self.manager.current = 'manual_link_list'
        
        btn.bind(on_press=go_list)
        content.add_widget(btn)
        popup.open()
    
    def go_back(self):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'manual_link_list'


class CompleteScreen(Screen):
    """İşlem tamamlandı ekranı"""
    
    def on_enter(self):
        self.clear_widgets()
        Clock.schedule_once(lambda dt: self.build_ui(), 0.05)
    
    def build_ui(self):
        app = App.get_running_app()
        filepath = getattr(app, 'output_filepath', '')
        filename = getattr(app, 'output_filename', '')
        filtered = getattr(app, 'filtered_channels', [])
        total = getattr(app, 'total_channels', [])
        
        root = BoxLayout(orientation='vertical', padding=dp(30), spacing=dp(20))
        
        # Success icon
        icon = Label(
            text='🎉',
            font_size=dp(70),
            size_hint_y=0.25
        )
        root.add_widget(icon)
        
        # Title
        title = Label(
            text='İşlem Tamamlandı!',
            font_size=dp(26),
            bold=True,
            color=get_color_from_hex(COLORS['text_white']),
            size_hint_y=None,
            height=dp(45)
        )
        root.add_widget(title)
        
        # Results card
        result_card = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(12), size_hint_y=None, height=dp(140))
        result_card.bind(size=self._update_card, pos=self._update_card)
        self._result_card = result_card
        
        result_card.add_widget(Label(
            text=f'📺 {len(filtered)} kanal filtrelendi',
            font_size=dp(17),
            color=get_color_from_hex(COLORS['success'])
        ))
        
        result_card.add_widget(Label(
            text=f'📊 Toplam {len(total)} kanaldan seçildi',
            font_size=dp(13),
            color=get_color_from_hex(COLORS['text_gray'])
        ))
        
        result_card.add_widget(Label(
            text=f'📁 {filename}',
            font_size=dp(12),
            color=get_color_from_hex(COLORS['primary'])
        ))
        
        root.add_widget(result_card)
        
        # Spacer
        root.add_widget(Label())
        
        # Buttons
        btns = BoxLayout(orientation='vertical', spacing=dp(12), size_hint_y=None, height=dp(110))
        
        new_btn = Button(
            text='🔄 Yeni İşlem',
            font_size=dp(15),
            bold=True,
            size_hint_y=None,
            height=dp(48),
            background_normal='',
            background_color=get_color_from_hex(COLORS['primary'])
        )
        new_btn.bind(on_press=lambda x: self.go_to('auto_input'))
        btns.add_widget(new_btn)
        
        home_btn = Button(
            text='🏠 Ana Sayfa',
            font_size=dp(15),
            bold=True,
            size_hint_y=None,
            height=dp(48),
            background_normal='',
            background_color=get_color_from_hex(COLORS['bg_card'])
        )
        home_btn.bind(on_press=lambda x: self.go_to('welcome'))
        btns.add_widget(home_btn)
        
        root.add_widget(btns)
        
        self.add_widget(root)
        Clock.schedule_once(lambda dt: self._draw_card(), 0.1)
    
    def _update_card(self, widget, value):
        Clock.schedule_once(lambda dt: self._draw_card(), 0)
    
    def _draw_card(self):
        from kivy.graphics import Color, RoundedRectangle
        self._result_card.canvas.before.clear()
        with self._result_card.canvas.before:
            Color(*get_color_from_hex(COLORS['bg_card']))
            RoundedRectangle(pos=self._result_card.pos, size=self._result_card.size, radius=[dp(15)])
    
    def go_to(self, screen):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = screen


# ==================== ANA UYGULAMA ====================

class IPTVEditorApp(App):
    """Ana uygulama sınıfı"""
    
    def build(self):
        # Pencere ayarları
        Window.clearcolor = get_color_from_hex(COLORS['bg_dark'])
        
        # Screen Manager
        sm = ScreenManager(transition=SlideTransition())
        
        # Ekranları ekle
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


# Uygulamayı başlat
if __name__ == '__main__':
    IPTVEditorApp().run()
