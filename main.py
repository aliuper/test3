"""
IPTV Editor Pro - Gelişmiş IPTV Düzenleyici
Python + Kivy ile Android APK
"""

import os
import re
import json
import traceback
import threading
import requests
from datetime import datetime
from urllib.parse import urlparse
from functools import partial

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.checkbox import CheckBox
from kivy.uix.progressbar import ProgressBar
from kivy.uix.spinner import Spinner
from kivy.uix.image import AsyncImage
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from kivy.properties import StringProperty, ListProperty, BooleanProperty, NumericProperty

# Hata yakalama - Android'de log dosyasına yazar
def handle_exception(exc_type, exc_value, exc_traceback):
    error_msg = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    try:
        from android.storage import primary_external_storage_path
        log_path = os.path.join(primary_external_storage_path(), 'Download', 'iptv_error.txt')
    except:
        log_path = '/sdcard/Download/iptv_error.txt'
    
    with open(log_path, 'w') as f:
        f.write(error_msg)

import sys
sys.excepthook = handle_exception

# Renk Paleti - Pastel ve Profesyonel
COLORS = {
    'primary': '#6C63FF',        # Ana mor
    'primary_light': '#8B85FF',  # Açık mor
    'secondary': '#FF6B9D',      # Pembe
    'success': '#4ECDC4',        # Turkuaz
    'warning': '#FFE66D',        # Sarı
    'danger': '#FF6B6B',         # Kırmızı
    'bg_dark': '#1A1A2E',        # Koyu arka plan
    'bg_medium': '#16213E',      # Orta arka plan
    'bg_light': '#0F3460',       # Açık arka plan
    'card_bg': '#252A40',        # Kart arka planı
    'text_primary': '#FFFFFF',   # Ana metin
    'text_secondary': '#B8B8D1', # İkincil metin
    'border': '#3D3D5C',         # Kenarlık
}

# Ülke Kodları ve Eşleşmeleri
COUNTRY_CODES = {
    'turkey': ['tr', 'tur', 'turkey', 'türkiye', 'turkiye', 'turkish', 'turk'],
    'germany': ['de', 'ger', 'germany', 'deutschland', 'german', 'deutsch', 'deu'],
    'romania': ['ro', 'rom', 'romania', 'romanian', 'rou'],
    'austria': ['at', 'aut', 'austria', 'österreich', 'austrian'],
    'france': ['fr', 'fra', 'france', 'french', 'francais'],
    'italy': ['it', 'ita', 'italy', 'italian', 'italiano'],
    'spain': ['es', 'esp', 'spain', 'spanish', 'espanol', 'españa'],
    'uk': ['uk', 'gb', 'gbr', 'england', 'british', 'english'],
    'usa': ['us', 'usa', 'america', 'american', 'united states'],
    'netherlands': ['nl', 'nld', 'netherlands', 'dutch', 'holland'],
    'poland': ['pl', 'pol', 'poland', 'polish', 'polska'],
    'russia': ['ru', 'rus', 'russia', 'russian'],
    'arabic': ['ar', 'ara', 'arabic', 'arab', 'عربي'],
    'india': ['in', 'ind', 'india', 'indian', 'hindi'],
    'portugal': ['pt', 'por', 'portugal', 'portuguese', 'brasil', 'brazil'],
    'greece': ['gr', 'gre', 'greece', 'greek', 'ελληνικά'],
    'albania': ['al', 'alb', 'albania', 'albanian', 'shqip'],
    'serbia': ['rs', 'srb', 'serbia', 'serbian', 'srpski'],
    'croatia': ['hr', 'hrv', 'croatia', 'croatian', 'hrvatski'],
    'bulgaria': ['bg', 'bgr', 'bulgaria', 'bulgarian'],
    'other': ['other', 'misc', 'mixed', 'international', 'world']
}

COUNTRY_FLAGS = {
    'turkey': '🇹🇷',
    'germany': '🇩🇪',
    'romania': '🇷🇴',
    'austria': '🇦🇹',
    'france': '🇫🇷',
    'italy': '🇮🇹',
    'spain': '🇪🇸',
    'uk': '🇬🇧',
    'usa': '🇺🇸',
    'netherlands': '🇳🇱',
    'poland': '🇵🇱',
    'russia': '🇷🇺',
    'arabic': '🇸🇦',
    'india': '🇮🇳',
    'portugal': '🇵🇹',
    'greece': '🇬🇷',
    'albania': '🇦🇱',
    'serbia': '🇷🇸',
    'croatia': '🇭🇷',
    'bulgaria': '🇧🇬',
    'other': '🌍'
}


class RoundedButton(Button):
    """Yuvarlatılmış köşeli özel buton"""
    
    def __init__(self, bg_color=COLORS['primary'], **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)
        self.background_normal = ''
        self.bg_color = bg_color
        self.bind(pos=self.update_canvas, size=self.update_canvas)
        
    def update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*get_color_from_hex(self.bg_color))
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(12)])


class StyledCard(BoxLayout):
    """Stilize edilmiş kart bileşeni"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = dp(15)
        self.spacing = dp(10)
        self.bind(pos=self.update_canvas, size=self.update_canvas)
        
    def update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*get_color_from_hex(COLORS['card_bg']))
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(15)])


class ChannelGroupItem(BoxLayout):
    """Kanal grubu liste öğesi"""
    
    selected = BooleanProperty(False)
    
    def __init__(self, group_name, channel_count, logo_url=None, on_select=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(70)
        self.padding = dp(10)
        self.spacing = dp(10)
        self.group_name = group_name
        self.on_select_callback = on_select
        
        self.bind(pos=self.update_canvas, size=self.update_canvas)
        
        # Logo
        if logo_url:
            logo = AsyncImage(source=logo_url, size_hint=(None, None), size=(dp(50), dp(50)))
        else:
            logo = Label(text='📺', font_size=dp(30), size_hint=(None, None), size=(dp(50), dp(50)))
        self.add_widget(logo)
        
        # Grup bilgisi
        info_layout = BoxLayout(orientation='vertical', spacing=dp(2))
        name_label = Label(
            text=group_name,
            font_size=dp(16),
            color=get_color_from_hex(COLORS['text_primary']),
            halign='left',
            valign='middle'
        )
        name_label.bind(size=name_label.setter('text_size'))
        
        count_label = Label(
            text=f'{channel_count} kanal',
            font_size=dp(12),
            color=get_color_from_hex(COLORS['text_secondary']),
            halign='left',
            valign='middle'
        )
        count_label.bind(size=count_label.setter('text_size'))
        
        info_layout.add_widget(name_label)
        info_layout.add_widget(count_label)
        self.add_widget(info_layout)
        
        # Seçim butonu
        self.select_btn = RoundedButton(
            text='＋',
            size_hint=(None, None),
            size=(dp(50), dp(50)),
            font_size=dp(24),
            bg_color=COLORS['primary']
        )
        self.select_btn.bind(on_press=self.toggle_selection)
        self.add_widget(self.select_btn)
        
    def update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            if self.selected:
                Color(*get_color_from_hex(COLORS['success']), 0.3)
            else:
                Color(*get_color_from_hex(COLORS['card_bg']))
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(12)])
            
    def toggle_selection(self, instance):
        self.selected = not self.selected
        if self.selected:
            self.select_btn.text = '✓'
            self.select_btn.bg_color = COLORS['success']
        else:
            self.select_btn.text = '＋'
            self.select_btn.bg_color = COLORS['primary']
        self.select_btn.update_canvas()
        self.update_canvas()
        
        if self.on_select_callback:
            self.on_select_callback(self.group_name, self.selected)


class IPTVParser:
    """M3U/M3U8 dosya ayrıştırıcı"""
    
    @staticmethod
    def parse_m3u(content):
        """M3U içeriğini ayrıştır"""
        channels = []
        groups = {}
        
        lines = content.split('\n')
        current_channel = {}
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('#EXTINF:'):
                # Kanal bilgilerini çıkar
                current_channel = IPTVParser._parse_extinf(line)
                
            elif line.startswith('http') or line.startswith('rtmp'):
                if current_channel:
                    current_channel['url'] = line
                    channels.append(current_channel)
                    
                    # Gruplara ekle
                    group = current_channel.get('group', 'Diğer')
                    if group not in groups:
                        groups[group] = {
                            'channels': [],
                            'logo': current_channel.get('logo', '')
                        }
                    groups[group]['channels'].append(current_channel)
                    
                current_channel = {}
                
        return channels, groups
    
    @staticmethod
    def _parse_extinf(line):
        """EXTINF satırını ayrıştır"""
        channel = {
            'name': '',
            'group': 'Diğer',
            'logo': '',
            'duration': -1
        }
        
        # Grup adını çıkar
        group_match = re.search(r'group-title="([^"]*)"', line)
        if group_match:
            channel['group'] = group_match.group(1) or 'Diğer'
            
        # Logo URL'sini çıkar
        logo_match = re.search(r'tvg-logo="([^"]*)"', line)
        if logo_match:
            channel['logo'] = logo_match.group(1)
            
        # TVG-ID'yi çıkar
        tvg_id_match = re.search(r'tvg-id="([^"]*)"', line)
        if tvg_id_match:
            channel['tvg_id'] = tvg_id_match.group(1)
            
        # TVG-Name'i çıkar
        tvg_name_match = re.search(r'tvg-name="([^"]*)"', line)
        if tvg_name_match:
            channel['tvg_name'] = tvg_name_match.group(1)
            
        # Kanal adını çıkar (satırın sonundaki kısım)
        name_match = re.search(r',(.+)$', line)
        if name_match:
            channel['name'] = name_match.group(1).strip()
            
        return channel
    
    @staticmethod
    def detect_country(group_name, channel_name=''):
        """Ülkeyi tespit et"""
        text = f"{group_name} {channel_name}".lower()
        
        for country, codes in COUNTRY_CODES.items():
            for code in codes:
                # Tam kelime eşleşmesi veya başlangıç/bitiş kontrolü
                patterns = [
                    rf'\b{code}\b',           # Tam kelime
                    rf'^{code}[:\s_-]',       # Başlangıçta
                    rf'[:\s_-]{code}$',       # Sonda
                    rf'\|{code}\|',           # Ayraçlar arasında
                    rf'\[{code}\]',           # Köşeli parantez içinde
                    rf'\({code}\)',           # Parantez içinde
                ]
                for pattern in patterns:
                    if re.search(pattern, text):
                        return country
                        
        return 'other'
    
    @staticmethod
    def generate_m3u(channels, format_type='m3u'):
        """Kanal listesinden M3U içeriği oluştur"""
        content = '#EXTM3U\n'
        
        for ch in channels:
            extinf = f'#EXTINF:-1'
            
            if ch.get('tvg_id'):
                extinf += f' tvg-id="{ch["tvg_id"]}"'
            if ch.get('tvg_name'):
                extinf += f' tvg-name="{ch["tvg_name"]}"'
            if ch.get('logo'):
                extinf += f' tvg-logo="{ch["logo"]}"'
            if ch.get('group'):
                extinf += f' group-title="{ch["group"]}"'
                
            extinf += f',{ch.get("name", "Unknown")}\n'
            content += extinf
            content += f'{ch.get("url", "")}\n'
            
        return content


class IPTVTester:
    """IPTV link test edici"""
    
    @staticmethod
    def test_link(url, timeout=10):
        """Tek bir linki test et"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            # İlk olarak HEAD isteği dene
            response = requests.head(url, timeout=timeout, headers=headers, allow_redirects=True)
            
            if response.status_code == 200:
                return True, "Başarılı"
                
            # HEAD başarısız olursa GET dene
            response = requests.get(url, timeout=timeout, headers=headers, stream=True)
            
            # İlk birkaç byte'ı oku
            content = next(response.iter_content(1024), None)
            
            if content:
                return True, "Başarılı"
            else:
                return False, "İçerik yok"
                
        except requests.exceptions.Timeout:
            return False, "Zaman aşımı"
        except requests.exceptions.ConnectionError:
            return False, "Bağlantı hatası"
        except Exception as e:
            return False, str(e)[:50]
    
    @staticmethod
    def test_stream(url, timeout=15):
        """Video akışını test et (daha kapsamlı)"""
        try:
            headers = {
                'User-Agent': 'VLC/3.0.11 LibVLC/3.0.11'
            }
            
            response = requests.get(url, timeout=timeout, headers=headers, stream=True)
            
            if response.status_code != 200:
                return False, f"HTTP {response.status_code}"
            
            content_type = response.headers.get('Content-Type', '')
            
            # Video içerik türlerini kontrol et
            valid_types = ['video', 'application/octet-stream', 'application/vnd.apple.mpegurl', 
                          'audio/mpegurl', 'application/x-mpegurl']
            
            is_valid_type = any(vt in content_type.lower() for vt in valid_types)
            
            # İlk chunk'ı oku
            total_bytes = 0
            for chunk in response.iter_content(chunk_size=8192):
                total_bytes += len(chunk)
                if total_bytes > 32768:  # 32KB yeterli
                    break
                    
            if total_bytes > 1024:
                return True, f"Aktif ({total_bytes} bytes)"
            else:
                return False, "Yetersiz veri"
                
        except requests.exceptions.Timeout:
            return False, "Zaman aşımı"
        except requests.exceptions.ConnectionError:
            return False, "Bağlantı hatası"
        except Exception as e:
            return False, str(e)[:50]


# ========================= EKRANLAR =========================

class WelcomeScreen(Screen):
    """Karşılama ekranı"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
        
    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=dp(30), spacing=dp(20))
        layout.bind(pos=self.update_bg, size=self.update_bg)
        
        # Başlık
        title_layout = BoxLayout(orientation='vertical', size_hint_y=0.4)
        
        app_icon = Label(text='📡', font_size=dp(80))
        title_layout.add_widget(app_icon)
        
        title = Label(
            text='IPTV Editor Pro',
            font_size=dp(32),
            bold=True,
            color=get_color_from_hex(COLORS['text_primary'])
        )
        title_layout.add_widget(title)
        
        subtitle = Label(
            text='Gelişmiş IPTV Düzenleyici',
            font_size=dp(16),
            color=get_color_from_hex(COLORS['text_secondary'])
        )
        title_layout.add_widget(subtitle)
        
        layout.add_widget(title_layout)
        
        # Mod seçimi kartları
        cards_layout = BoxLayout(orientation='vertical', spacing=dp(20), size_hint_y=0.5)
        
        # Manuel mod kartı
        manual_card = StyledCard()
        manual_inner = BoxLayout(orientation='vertical', spacing=dp(10))
        
        manual_icon = Label(text='✏️', font_size=dp(40))
        manual_title = Label(
            text='Manuel Düzenleme',
            font_size=dp(20),
            bold=True,
            color=get_color_from_hex(COLORS['text_primary'])
        )
        manual_desc = Label(
            text='IPTV linkini girin, kanal gruplarını görüntüleyin\nve istediğiniz kanalları seçin',
            font_size=dp(13),
            color=get_color_from_hex(COLORS['text_secondary']),
            halign='center'
        )
        manual_desc.bind(size=manual_desc.setter('text_size'))
        
        manual_btn = RoundedButton(
            text='Başla →',
            size_hint=(0.6, None),
            height=dp(45),
            pos_hint={'center_x': 0.5},
            bg_color=COLORS['primary']
        )
        manual_btn.bind(on_press=self.go_manual)
        
        manual_inner.add_widget(manual_icon)
        manual_inner.add_widget(manual_title)
        manual_inner.add_widget(manual_desc)
        manual_inner.add_widget(manual_btn)
        manual_card.add_widget(manual_inner)
        cards_layout.add_widget(manual_card)
        
        # Otomatik mod kartı
        auto_card = StyledCard()
        auto_inner = BoxLayout(orientation='vertical', spacing=dp(10))
        
        auto_icon = Label(text='🤖', font_size=dp(40))
        auto_title = Label(
            text='Otomatik Düzenleme',
            font_size=dp(20),
            bold=True,
            color=get_color_from_hex(COLORS['text_primary'])
        )
        auto_desc = Label(
            text='Toplu linkleri test edin, çalışanları filtreleyin\nve ülkelere göre otomatik düzenleyin',
            font_size=dp(13),
            color=get_color_from_hex(COLORS['text_secondary']),
            halign='center'
        )
        auto_desc.bind(size=auto_desc.setter('text_size'))
        
        auto_btn = RoundedButton(
            text='Başla →',
            size_hint=(0.6, None),
            height=dp(45),
            pos_hint={'center_x': 0.5},
            bg_color=COLORS['secondary']
        )
        auto_btn.bind(on_press=self.go_auto)
        
        auto_inner.add_widget(auto_icon)
        auto_inner.add_widget(auto_title)
        auto_inner.add_widget(auto_desc)
        auto_inner.add_widget(auto_btn)
        auto_card.add_widget(auto_inner)
        cards_layout.add_widget(auto_card)
        
        layout.add_widget(cards_layout)
        
        # Alt bilgi
        footer = Label(
            text='v1.0.0 • Made with ❤️',
            font_size=dp(12),
            color=get_color_from_hex(COLORS['text_secondary']),
            size_hint_y=0.1
        )
        layout.add_widget(footer)
        
        self.add_widget(layout)
        
    def update_bg(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*get_color_from_hex(COLORS['bg_dark']))
            Rectangle(pos=self.pos, size=self.size)
            
    def go_manual(self, instance):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'manual_input'
        
    def go_auto(self, instance):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'auto_input'


class ManualInputScreen(Screen):
    """Manuel mod - URL giriş ekranı"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
        
    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        layout.bind(pos=self.update_bg, size=self.update_bg)
        
        # Üst bar
        top_bar = BoxLayout(size_hint_y=None, height=dp(50))
        
        back_btn = RoundedButton(
            text='← Geri',
            size_hint=(None, None),
            size=(dp(100), dp(40)),
            bg_color=COLORS['bg_light']
        )
        back_btn.bind(on_press=self.go_back)
        top_bar.add_widget(back_btn)
        
        top_bar.add_widget(Label())  # Spacer
        
        layout.add_widget(top_bar)
        
        # Başlık
        title = Label(
            text='✏️ Manuel Düzenleme',
            font_size=dp(24),
            bold=True,
            color=get_color_from_hex(COLORS['text_primary']),
            size_hint_y=None,
            height=dp(40)
        )
        layout.add_widget(title)
        
        # Açıklama
        desc = Label(
            text='IPTV playlist URL\'sini girin',
            font_size=dp(14),
            color=get_color_from_hex(COLORS['text_secondary']),
            size_hint_y=None,
            height=dp(30)
        )
        layout.add_widget(desc)
        
        # URL giriş alanı
        url_card = StyledCard(size_hint_y=None, height=dp(150))
        url_inner = BoxLayout(orientation='vertical', spacing=dp(10))
        
        url_label = Label(
            text='Playlist URL',
            font_size=dp(14),
            color=get_color_from_hex(COLORS['text_secondary']),
            halign='left',
            size_hint_y=None,
            height=dp(25)
        )
        url_label.bind(size=url_label.setter('text_size'))
        
        self.url_input = TextInput(
            hint_text='https://example.com/playlist.m3u',
            multiline=False,
            font_size=dp(14),
            background_color=get_color_from_hex(COLORS['bg_medium']),
            foreground_color=get_color_from_hex(COLORS['text_primary']),
            cursor_color=get_color_from_hex(COLORS['primary']),
            padding=[dp(15), dp(12)],
            size_hint_y=None,
            height=dp(50)
        )
        
        url_inner.add_widget(url_label)
        url_inner.add_widget(self.url_input)
        url_card.add_widget(url_inner)
        layout.add_widget(url_card)
        
        # Format seçimi
        format_card = StyledCard(size_hint_y=None, height=dp(120))
        format_inner = BoxLayout(orientation='vertical', spacing=dp(10))
        
        format_label = Label(
            text='Çıktı Formatı',
            font_size=dp(14),
            color=get_color_from_hex(COLORS['text_secondary']),
            halign='left',
            size_hint_y=None,
            height=dp(25)
        )
        format_label.bind(size=format_label.setter('text_size'))
        
        format_buttons = BoxLayout(spacing=dp(10))
        
        self.format_buttons = {}
        formats = [
            ('m3u', 'M3U', '⭐ En İyi'),
            ('m3u8', 'M3U8', '📱 Mobil'),
            ('txt', 'TXT', '📝 Basit')
        ]
        
        for fmt, name, tag in formats:
            btn_layout = BoxLayout(orientation='vertical', spacing=dp(5))
            
            btn = RoundedButton(
                text=name,
                bg_color=COLORS['primary'] if fmt == 'm3u' else COLORS['bg_light']
            )
            btn.format_type = fmt
            btn.bind(on_press=self.select_format)
            self.format_buttons[fmt] = btn
            
            tag_label = Label(
                text=tag,
                font_size=dp(10),
                color=get_color_from_hex(COLORS['success']),
                size_hint_y=None,
                height=dp(15)
            )
            
            btn_layout.add_widget(btn)
            btn_layout.add_widget(tag_label)
            format_buttons.add_widget(btn_layout)
            
        format_inner.add_widget(format_label)
        format_inner.add_widget(format_buttons)
        format_card.add_widget(format_inner)
        layout.add_widget(format_card)
        
        # Spacer
        layout.add_widget(Label())
        
        # İleri butonu
        next_btn = RoundedButton(
            text='Kanalları Yükle →',
            size_hint=(1, None),
            height=dp(55),
            font_size=dp(18),
            bg_color=COLORS['success']
        )
        next_btn.bind(on_press=self.load_channels)
        layout.add_widget(next_btn)
        
        self.add_widget(layout)
        
        self.selected_format = 'm3u'
        
    def update_bg(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*get_color_from_hex(COLORS['bg_dark']))
            Rectangle(pos=self.pos, size=self.size)
            
    def go_back(self, instance):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'welcome'
        
    def select_format(self, instance):
        self.selected_format = instance.format_type
        for fmt, btn in self.format_buttons.items():
            if fmt == self.selected_format:
                btn.bg_color = COLORS['primary']
            else:
                btn.bg_color = COLORS['bg_light']
            btn.update_canvas()
            
    def load_channels(self, instance):
        url = self.url_input.text.strip()
        
        if not url:
            self.show_error('Lütfen bir URL girin!')
            return
            
        # Loading popup
        self.show_loading()
        
        # Arka planda yükle
        threading.Thread(target=self._load_playlist, args=(url,), daemon=True).start()
        
    def _load_playlist(self, url):
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            content = response.text
            
            channels, groups = IPTVParser.parse_m3u(content)
            
            Clock.schedule_once(lambda dt: self._on_playlist_loaded(channels, groups))
            
        except Exception as e:
            Clock.schedule_once(lambda dt: self._on_load_error(str(e)))
            
    def _on_playlist_loaded(self, channels, groups):
        self.dismiss_loading()
        
        # Verileri app'e kaydet
        app = App.get_running_app()
        app.channels = channels
        app.groups = groups
        app.selected_format = self.selected_format
        
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'channel_list'
        
    def _on_load_error(self, error):
        self.dismiss_loading()
        self.show_error(f'Yükleme hatası: {error}')
        
    def show_loading(self):
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(20))
        
        spinner_label = Label(text='⏳', font_size=dp(50))
        content.add_widget(spinner_label)
        
        loading_label = Label(
            text='Playlist yükleniyor...',
            font_size=dp(16),
            color=get_color_from_hex(COLORS['text_primary'])
        )
        content.add_widget(loading_label)
        
        progress = ProgressBar(max=100, value=50)
        content.add_widget(progress)
        
        self.loading_popup = Popup(
            title='',
            content=content,
            size_hint=(0.8, 0.4),
            auto_dismiss=False,
            separator_height=0,
            background_color=get_color_from_hex(COLORS['card_bg'])
        )
        self.loading_popup.open()
        
    def dismiss_loading(self):
        if hasattr(self, 'loading_popup'):
            self.loading_popup.dismiss()
            
    def show_error(self, message):
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(20))
        
        error_icon = Label(text='❌', font_size=dp(50))
        content.add_widget(error_icon)
        
        error_label = Label(
            text=message,
            font_size=dp(14),
            color=get_color_from_hex(COLORS['text_primary']),
            halign='center'
        )
        error_label.bind(size=error_label.setter('text_size'))
        content.add_widget(error_label)
        
        close_btn = RoundedButton(
            text='Tamam',
            size_hint=(0.5, None),
            height=dp(45),
            pos_hint={'center_x': 0.5},
            bg_color=COLORS['danger']
        )
        
        popup = Popup(
            title='',
            content=content,
            size_hint=(0.85, 0.4),
            separator_height=0,
            background_color=get_color_from_hex(COLORS['card_bg'])
        )
        
        close_btn.bind(on_press=popup.dismiss)
        content.add_widget(close_btn)
        
        popup.open()


class ChannelListScreen(Screen):
    """Kanal grupları listesi ekranı"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_groups = set()
        
    def on_enter(self):
        self.clear_widgets()
        self.build_ui()
        
    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        layout.bind(pos=self.update_bg, size=self.update_bg)
        
        # Üst bar
        top_bar = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        
        back_btn = RoundedButton(
            text='←',
            size_hint=(None, None),
            size=(dp(50), dp(40)),
            bg_color=COLORS['bg_light']
        )
        back_btn.bind(on_press=self.go_back)
        top_bar.add_widget(back_btn)
        
        title = Label(
            text='📺 Kanal Grupları',
            font_size=dp(18),
            bold=True,
            color=get_color_from_hex(COLORS['text_primary'])
        )
        top_bar.add_widget(title)
        
        layout.add_widget(top_bar)
        
        # İstatistikler
        app = App.get_running_app()
        groups = getattr(app, 'groups', {})
        channels = getattr(app, 'channels', [])
        
        stats_label = Label(
            text=f'📊 {len(groups)} grup • {len(channels)} kanal',
            font_size=dp(14),
            color=get_color_from_hex(COLORS['text_secondary']),
            size_hint_y=None,
            height=dp(30)
        )
        layout.add_widget(stats_label)
        
        # Seçim bilgisi
        self.selection_label = Label(
            text='Seçilen: 0 grup',
            font_size=dp(12),
            color=get_color_from_hex(COLORS['success']),
            size_hint_y=None,
            height=dp(25)
        )
        layout.add_widget(self.selection_label)
        
        # Kanal listesi
        scroll = ScrollView()
        self.list_layout = BoxLayout(orientation='vertical', spacing=dp(8), size_hint_y=None)
        self.list_layout.bind(minimum_height=self.list_layout.setter('height'))
        
        for group_name, group_data in sorted(groups.items()):
            item = ChannelGroupItem(
                group_name=group_name,
                channel_count=len(group_data['channels']),
                logo_url=group_data.get('logo'),
                on_select=self.on_group_select
            )
            self.list_layout.add_widget(item)
            
        scroll.add_widget(self.list_layout)
        layout.add_widget(scroll)
        
        # Alt butonlar
        bottom_bar = BoxLayout(size_hint_y=None, height=dp(55), spacing=dp(10))
        
        select_all_btn = RoundedButton(
            text='Tümünü Seç',
            bg_color=COLORS['primary']
        )
        select_all_btn.bind(on_press=self.select_all)
        bottom_bar.add_widget(select_all_btn)
        
        export_btn = RoundedButton(
            text='Dışa Aktar →',
            bg_color=COLORS['success']
        )
        export_btn.bind(on_press=self.export_selected)
        bottom_bar.add_widget(export_btn)
        
        layout.add_widget(bottom_bar)
        
        self.add_widget(layout)
        
    def update_bg(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*get_color_from_hex(COLORS['bg_dark']))
            Rectangle(pos=self.pos, size=self.size)
            
    def go_back(self, instance):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'manual_input'
        
    def on_group_select(self, group_name, selected):
        if selected:
            self.selected_groups.add(group_name)
        else:
            self.selected_groups.discard(group_name)
            
        self.selection_label.text = f'Seçilen: {len(self.selected_groups)} grup'
        
    def select_all(self, instance):
        app = App.get_running_app()
        groups = getattr(app, 'groups', {})
        
        for child in self.list_layout.children:
            if isinstance(child, ChannelGroupItem) and not child.selected:
                child.toggle_selection(None)
                
    def export_selected(self, instance):
        if not self.selected_groups:
            self.show_message('Uyarı', 'Lütfen en az bir grup seçin!')
            return
            
        app = App.get_running_app()
        groups = getattr(app, 'groups', {})
        selected_format = getattr(app, 'selected_format', 'm3u')
        
        # Seçili kanalları topla
        selected_channels = []
        for group_name in self.selected_groups:
            if group_name in groups:
                selected_channels.extend(groups[group_name]['channels'])
                
        # M3U oluştur
        content = IPTVParser.generate_m3u(selected_channels, selected_format)
        
        # Dosyayı kaydet
        self.save_file(content, selected_format)
        
    def save_file(self, content, format_type):
        try:
            # Android'de Downloads klasörüne kaydet
            from android.storage import primary_external_storage_path
            download_path = os.path.join(primary_external_storage_path(), 'Download')
        except:
            # Desktop'ta mevcut dizine kaydet
            download_path = os.path.expanduser('~')
            
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'iptv_export_{timestamp}.{format_type}'
        filepath = os.path.join(download_path, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
                
            self.show_message('Başarılı! ✅', f'Dosya kaydedildi:\n{filepath}')
        except Exception as e:
            self.show_message('Hata', f'Kaydetme hatası: {str(e)}')
            
    def show_message(self, title, message):
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(20))
        
        icon = Label(text='✅' if 'Başarılı' in title else '⚠️', font_size=dp(50))
        content.add_widget(icon)
        
        msg_label = Label(
            text=message,
            font_size=dp(14),
            color=get_color_from_hex(COLORS['text_primary']),
            halign='center'
        )
        msg_label.bind(size=msg_label.setter('text_size'))
        content.add_widget(msg_label)
        
        close_btn = RoundedButton(
            text='Tamam',
            size_hint=(0.5, None),
            height=dp(45),
            pos_hint={'center_x': 0.5},
            bg_color=COLORS['success'] if 'Başarılı' in title else COLORS['warning']
        )
        
        popup = Popup(
            title='',
            content=content,
            size_hint=(0.85, 0.45),
            separator_height=0
        )
        
        close_btn.bind(on_press=popup.dismiss)
        content.add_widget(close_btn)
        
        popup.open()


class AutoInputScreen(Screen):
    """Otomatik mod - Toplu link giriş ekranı"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
        
    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        layout.bind(pos=self.update_bg, size=self.update_bg)
        
        # Üst bar
        top_bar = BoxLayout(size_hint_y=None, height=dp(50))
        
        back_btn = RoundedButton(
            text='← Geri',
            size_hint=(None, None),
            size=(dp(100), dp(40)),
            bg_color=COLORS['bg_light']
        )
        back_btn.bind(on_press=self.go_back)
        top_bar.add_widget(back_btn)
        top_bar.add_widget(Label())
        
        layout.add_widget(top_bar)
        
        # Başlık
        title = Label(
            text='🤖 Otomatik Düzenleme',
            font_size=dp(24),
            bold=True,
            color=get_color_from_hex(COLORS['text_primary']),
            size_hint_y=None,
            height=dp(40)
        )
        layout.add_widget(title)
        
        # Açıklama
        desc = Label(
            text='IPTV linklerini her satıra bir tane olacak şekilde girin.\nProgram çalışan linkleri otomatik tespit edecek.',
            font_size=dp(13),
            color=get_color_from_hex(COLORS['text_secondary']),
            size_hint_y=None,
            height=dp(50),
            halign='center'
        )
        desc.bind(size=desc.setter('text_size'))
        layout.add_widget(desc)
        
        # Link giriş alanı
        input_card = StyledCard()
        input_inner = BoxLayout(orientation='vertical', spacing=dp(10))
        
        input_label = Label(
            text='IPTV Linkleri (her satıra bir link)',
            font_size=dp(14),
            color=get_color_from_hex(COLORS['text_secondary']),
            halign='left',
            size_hint_y=None,
            height=dp(25)
        )
        input_label.bind(size=input_label.setter('text_size'))
        
        self.links_input = TextInput(
            hint_text='https://example1.com/playlist.m3u\nhttps://example2.com/playlist.m3u\n...',
            multiline=True,
            font_size=dp(13),
            background_color=get_color_from_hex(COLORS['bg_medium']),
            foreground_color=get_color_from_hex(COLORS['text_primary']),
            cursor_color=get_color_from_hex(COLORS['primary']),
            padding=[dp(15), dp(12)]
        )
        
        input_inner.add_widget(input_label)
        input_inner.add_widget(self.links_input)
        input_card.add_widget(input_inner)
        layout.add_widget(input_card)
        
        # Test seçenekleri
        options_card = StyledCard(size_hint_y=None, height=dp(100))
        options_inner = BoxLayout(orientation='vertical', spacing=dp(10))
        
        options_label = Label(
            text='Test Yöntemi',
            font_size=dp(14),
            color=get_color_from_hex(COLORS['text_secondary']),
            halign='left',
            size_hint_y=None,
            height=dp(25)
        )
        options_label.bind(size=options_label.setter('text_size'))
        
        test_buttons = BoxLayout(spacing=dp(10))
        
        self.quick_test_btn = RoundedButton(
            text='⚡ Hızlı Test',
            bg_color=COLORS['primary']
        )
        self.quick_test_btn.bind(on_press=lambda x: self.select_test_mode('quick'))
        
        self.deep_test_btn = RoundedButton(
            text='🔍 Derin Test',
            bg_color=COLORS['bg_light']
        )
        self.deep_test_btn.bind(on_press=lambda x: self.select_test_mode('deep'))
        
        test_buttons.add_widget(self.quick_test_btn)
        test_buttons.add_widget(self.deep_test_btn)
        
        options_inner.add_widget(options_label)
        options_inner.add_widget(test_buttons)
        options_card.add_widget(options_inner)
        layout.add_widget(options_card)
        
        # Test başlat butonu
        start_btn = RoundedButton(
            text='🚀 Test Başlat',
            size_hint=(1, None),
            height=dp(55),
            font_size=dp(18),
            bg_color=COLORS['success']
        )
        start_btn.bind(on_press=self.start_testing)
        layout.add_widget(start_btn)
        
        self.add_widget(layout)
        
        self.test_mode = 'quick'
        
    def update_bg(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*get_color_from_hex(COLORS['bg_dark']))
            Rectangle(pos=self.pos, size=self.size)
            
    def go_back(self, instance):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'welcome'
        
    def select_test_mode(self, mode):
        self.test_mode = mode
        if mode == 'quick':
            self.quick_test_btn.bg_color = COLORS['primary']
            self.deep_test_btn.bg_color = COLORS['bg_light']
        else:
            self.quick_test_btn.bg_color = COLORS['bg_light']
            self.deep_test_btn.bg_color = COLORS['primary']
        self.quick_test_btn.update_canvas()
        self.deep_test_btn.update_canvas()
        
    def start_testing(self, instance):
        links_text = self.links_input.text.strip()
        
        if not links_text:
            self.show_error('Lütfen en az bir link girin!')
            return
            
        # Linkleri ayır
        links = [l.strip() for l in links_text.split('\n') if l.strip().startswith('http')]
        
        if not links:
            self.show_error('Geçerli link bulunamadı!')
            return
            
        # App'e kaydet
        app = App.get_running_app()
        app.links_to_test = links
        app.test_mode = self.test_mode
        
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'testing'
        
    def show_error(self, message):
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(20))
        
        error_icon = Label(text='❌', font_size=dp(50))
        content.add_widget(error_icon)
        
        error_label = Label(
            text=message,
            font_size=dp(14),
            color=get_color_from_hex(COLORS['text_primary']),
            halign='center'
        )
        error_label.bind(size=error_label.setter('text_size'))
        content.add_widget(error_label)
        
        close_btn = RoundedButton(
            text='Tamam',
            size_hint=(0.5, None),
            height=dp(45),
            pos_hint={'center_x': 0.5},
            bg_color=COLORS['danger']
        )
        
        popup = Popup(
            title='',
            content=content,
            size_hint=(0.85, 0.4),
            separator_height=0
        )
        
        close_btn.bind(on_press=popup.dismiss)
        content.add_widget(close_btn)
        
        popup.open()


class TestingScreen(Screen):
    """Link test ekranı"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.testing = False
        self.working_links = []
        self.failed_links = []
        
    def on_enter(self):
        self.clear_widgets()
        self.build_ui()
        self.start_tests()
        
    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        layout.bind(pos=self.update_bg, size=self.update_bg)
        
        # Başlık
        title = Label(
            text='🔍 Test Ediliyor...',
            font_size=dp(24),
            bold=True,
            color=get_color_from_hex(COLORS['text_primary']),
            size_hint_y=None,
            height=dp(50)
        )
        layout.add_widget(title)
        
        # İlerleme
        progress_card = StyledCard(size_hint_y=None, height=dp(150))
        progress_inner = BoxLayout(orientation='vertical', spacing=dp(15), padding=dp(10))
        
        self.progress_label = Label(
            text='Hazırlanıyor...',
            font_size=dp(16),
            color=get_color_from_hex(COLORS['text_primary'])
        )
        progress_inner.add_widget(self.progress_label)
        
        self.progress_bar = ProgressBar(max=100, value=0)
        progress_inner.add_widget(self.progress_bar)
        
        self.stats_label = Label(
            text='✅ 0 Çalışan  •  ❌ 0 Başarısız',
            font_size=dp(14),
            color=get_color_from_hex(COLORS['text_secondary'])
        )
        progress_inner.add_widget(self.stats_label)
        
        progress_card.add_widget(progress_inner)
        layout.add_widget(progress_card)
        
        # Canlı log
        log_card = StyledCard()
        log_inner = BoxLayout(orientation='vertical', spacing=dp(10))
        
        log_title = Label(
            text='📋 Test Günlüğü',
            font_size=dp(14),
            color=get_color_from_hex(COLORS['text_secondary']),
            halign='left',
            size_hint_y=None,
            height=dp(25)
        )
        log_title.bind(size=log_title.setter('text_size'))
        log_inner.add_widget(log_title)
        
        scroll = ScrollView()
        self.log_layout = BoxLayout(orientation='vertical', spacing=dp(5), size_hint_y=None)
        self.log_layout.bind(minimum_height=self.log_layout.setter('height'))
        scroll.add_widget(self.log_layout)
        log_inner.add_widget(scroll)
        
        log_card.add_widget(log_inner)
        layout.add_widget(log_card)
        
        # İptal butonu
        self.cancel_btn = RoundedButton(
            text='❌ İptal Et',
            size_hint=(1, None),
            height=dp(50),
            bg_color=COLORS['danger']
        )
        self.cancel_btn.bind(on_press=self.cancel_tests)
        layout.add_widget(self.cancel_btn)
        
        self.add_widget(layout)
        
    def update_bg(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*get_color_from_hex(COLORS['bg_dark']))
            Rectangle(pos=self.pos, size=self.size)
            
    def start_tests(self):
        self.testing = True
        self.working_links = []
        self.failed_links = []
        
        app = App.get_running_app()
        self.links = getattr(app, 'links_to_test', [])
        self.test_mode = getattr(app, 'test_mode', 'quick')
        self.total = len(self.links)
        self.current = 0
        
        threading.Thread(target=self._run_tests, daemon=True).start()
        
    def _run_tests(self):
        for i, link in enumerate(self.links):
            if not self.testing:
                break
                
            self.current = i + 1
            
            Clock.schedule_once(lambda dt, l=link: self.add_log(f'Test ediliyor: {l[:50]}...', 'info'))
            
            # Test et
            if self.test_mode == 'quick':
                success, message = IPTVTester.test_link(link)
            else:
                success, message = IPTVTester.test_stream(link)
                
            if success:
                self.working_links.append(link)
                Clock.schedule_once(lambda dt, l=link: self.add_log(f'✅ Çalışıyor: {l[:40]}...', 'success'))
            else:
                self.failed_links.append({'link': link, 'reason': message})
                Clock.schedule_once(lambda dt, l=link, m=message: self.add_log(f'❌ Başarısız: {l[:30]}... ({m})', 'error'))
                
            # UI güncelle
            Clock.schedule_once(self.update_progress)
            
        Clock.schedule_once(self.tests_completed)
        
    def update_progress(self, dt):
        if self.total > 0:
            progress = (self.current / self.total) * 100
            self.progress_bar.value = progress
            self.progress_label.text = f'Test ediliyor: {self.current}/{self.total}'
            self.stats_label.text = f'✅ {len(self.working_links)} Çalışan  •  ❌ {len(self.failed_links)} Başarısız'
            
    def add_log(self, message, log_type='info'):
        colors = {
            'info': COLORS['text_secondary'],
            'success': COLORS['success'],
            'error': COLORS['danger']
        }
        
        log_item = Label(
            text=message,
            font_size=dp(12),
            color=get_color_from_hex(colors.get(log_type, COLORS['text_secondary'])),
            size_hint_y=None,
            height=dp(25),
            halign='left'
        )
        log_item.bind(size=log_item.setter('text_size'))
        self.log_layout.add_widget(log_item)
        
    def tests_completed(self, dt):
        self.testing = False
        self.progress_label.text = 'Test tamamlandı!'
        self.cancel_btn.text = 'Devam Et →'
        self.cancel_btn.bg_color = COLORS['success']
        self.cancel_btn.update_canvas()
        self.cancel_btn.unbind(on_press=self.cancel_tests)
        self.cancel_btn.bind(on_press=self.go_next)
        
        # Sonuçları kaydet
        app = App.get_running_app()
        app.working_links = self.working_links
        app.failed_links = self.failed_links
        
    def cancel_tests(self, instance):
        self.testing = False
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'auto_input'
        
    def go_next(self, instance):
        if not self.working_links:
            self.show_no_working_links()
            return
            
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'auto_result'
        
    def show_no_working_links(self):
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(20))
        
        icon = Label(text='😞', font_size=dp(50))
        content.add_widget(icon)
        
        msg = Label(
            text='Çalışan link bulunamadı!\nLütfen farklı linkler deneyin.',
            font_size=dp(14),
            color=get_color_from_hex(COLORS['text_primary']),
            halign='center'
        )
        msg.bind(size=msg.setter('text_size'))
        content.add_widget(msg)
        
        close_btn = RoundedButton(
            text='Geri Dön',
            size_hint=(0.5, None),
            height=dp(45),
            pos_hint={'center_x': 0.5},
            bg_color=COLORS['primary']
        )
        
        popup = Popup(
            title='',
            content=content,
            size_hint=(0.85, 0.4),
            separator_height=0
        )
        
        def go_back(x):
            popup.dismiss()
            self.manager.transition = SlideTransition(direction='right')
            self.manager.current = 'auto_input'
            
        close_btn.bind(on_press=go_back)
        content.add_widget(close_btn)
        
        popup.open()


class AutoResultScreen(Screen):
    """Otomatik test sonuç ve düzenleme seçim ekranı"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
    def on_enter(self):
        self.clear_widgets()
        self.build_ui()
        
    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        layout.bind(pos=self.update_bg, size=self.update_bg)
        
        app = App.get_running_app()
        working = len(getattr(app, 'working_links', []))
        failed = len(getattr(app, 'failed_links', []))
        
        # Başlık
        title = Label(
            text='🎉 Test Tamamlandı!',
            font_size=dp(24),
            bold=True,
            color=get_color_from_hex(COLORS['text_primary']),
            size_hint_y=None,
            height=dp(50)
        )
        layout.add_widget(title)
        
        # Sonuç kartı
        result_card = StyledCard(size_hint_y=None, height=dp(120))
        result_inner = BoxLayout(orientation='horizontal', spacing=dp(20))
        
        # Çalışan
        working_box = BoxLayout(orientation='vertical')
        working_icon = Label(text='✅', font_size=dp(40))
        working_count = Label(
            text=str(working),
            font_size=dp(32),
            bold=True,
            color=get_color_from_hex(COLORS['success'])
        )
        working_label = Label(
            text='Çalışan',
            font_size=dp(12),
            color=get_color_from_hex(COLORS['text_secondary'])
        )
        working_box.add_widget(working_icon)
        working_box.add_widget(working_count)
        working_box.add_widget(working_label)
        result_inner.add_widget(working_box)
        
        # Başarısız
        failed_box = BoxLayout(orientation='vertical')
        failed_icon = Label(text='❌', font_size=dp(40))
        failed_count = Label(
            text=str(failed),
            font_size=dp(32),
            bold=True,
            color=get_color_from_hex(COLORS['danger'])
        )
        failed_label = Label(
            text='Başarısız',
            font_size=dp(12),
            color=get_color_from_hex(COLORS['text_secondary'])
        )
        failed_box.add_widget(failed_icon)
        failed_box.add_widget(failed_count)
        failed_box.add_widget(failed_label)
        result_inner.add_widget(failed_box)
        
        result_card.add_widget(result_inner)
        layout.add_widget(result_card)
        
        # Soru
        question = Label(
            text='Çalışan linkleri nasıl düzenlemek istersiniz?',
            font_size=dp(16),
            color=get_color_from_hex(COLORS['text_primary']),
            size_hint_y=None,
            height=dp(40)
        )
        layout.add_widget(question)
        
        # Seçenekler
        # Otomatik düzenleme kartı
        auto_card = StyledCard(size_hint_y=None, height=dp(140))
        auto_inner = BoxLayout(orientation='vertical', spacing=dp(10))
        
        auto_header = BoxLayout(size_hint_y=None, height=dp(40))
        auto_icon = Label(text='🤖', font_size=dp(30), size_hint_x=None, width=dp(50))
        auto_title = Label(
            text='Otomatik Düzenleme',
            font_size=dp(18),
            bold=True,
            color=get_color_from_hex(COLORS['text_primary']),
            halign='left'
        )
        auto_title.bind(size=auto_title.setter('text_size'))
        auto_header.add_widget(auto_icon)
        auto_header.add_widget(auto_title)
        
        auto_desc = Label(
            text='Ülke seçin, kanallar otomatik filtrelensin',
            font_size=dp(13),
            color=get_color_from_hex(COLORS['text_secondary']),
            halign='center'
        )
        auto_desc.bind(size=auto_desc.setter('text_size'))
        
        auto_btn = RoundedButton(
            text='Otomatik →',
            size_hint=(0.6, None),
            height=dp(40),
            pos_hint={'center_x': 0.5},
            bg_color=COLORS['primary']
        )
        auto_btn.bind(on_press=self.go_auto_edit)
        
        auto_inner.add_widget(auto_header)
        auto_inner.add_widget(auto_desc)
        auto_inner.add_widget(auto_btn)
        auto_card.add_widget(auto_inner)
        layout.add_widget(auto_card)
        
        # Manuel düzenleme kartı
        manual_card = StyledCard(size_hint_y=None, height=dp(140))
        manual_inner = BoxLayout(orientation='vertical', spacing=dp(10))
        
        manual_header = BoxLayout(size_hint_y=None, height=dp(40))
        manual_icon = Label(text='✏️', font_size=dp(30), size_hint_x=None, width=dp(50))
        manual_title = Label(
            text='Manuel Düzenleme',
            font_size=dp(18),
            bold=True,
            color=get_color_from_hex(COLORS['text_primary']),
            halign='left'
        )
        manual_title.bind(size=manual_title.setter('text_size'))
        manual_header.add_widget(manual_icon)
        manual_header.add_widget(manual_title)
        
        manual_desc = Label(
            text='Her linki tek tek düzenleyin',
            font_size=dp(13),
            color=get_color_from_hex(COLORS['text_secondary']),
            halign='center'
        )
        manual_desc.bind(size=manual_desc.setter('text_size'))
        
        manual_btn = RoundedButton(
            text='Manuel →',
            size_hint=(0.6, None),
            height=dp(40),
            pos_hint={'center_x': 0.5},
            bg_color=COLORS['secondary']
        )
        manual_btn.bind(on_press=self.go_manual_edit)
        
        manual_inner.add_widget(manual_header)
        manual_inner.add_widget(manual_desc)
        manual_inner.add_widget(manual_btn)
        manual_card.add_widget(manual_inner)
        layout.add_widget(manual_card)
        
        # Spacer
        layout.add_widget(Label())
        
        # Geri butonu
        back_btn = RoundedButton(
            text='← Geri',
            size_hint=(1, None),
            height=dp(45),
            bg_color=COLORS['bg_light']
        )
        back_btn.bind(on_press=self.go_back)
        layout.add_widget(back_btn)
        
        self.add_widget(layout)
        
    def update_bg(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*get_color_from_hex(COLORS['bg_dark']))
            Rectangle(pos=self.pos, size=self.size)
            
    def go_back(self, instance):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'auto_input'
        
    def go_auto_edit(self, instance):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'country_select'
        
    def go_manual_edit(self, instance):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'manual_edit_list'


class CountrySelectScreen(Screen):
    """Ülke seçim ekranı"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_countries = set()
        
    def on_enter(self):
        self.clear_widgets()
        self.selected_countries = set()
        self.build_ui()
        
    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        layout.bind(pos=self.update_bg, size=self.update_bg)
        
        # Üst bar
        top_bar = BoxLayout(size_hint_y=None, height=dp(50))
        
        back_btn = RoundedButton(
            text='←',
            size_hint=(None, None),
            size=(dp(50), dp(40)),
            bg_color=COLORS['bg_light']
        )
        back_btn.bind(on_press=self.go_back)
        top_bar.add_widget(back_btn)
        
        title = Label(
            text='🌍 Ülke Seçimi',
            font_size=dp(20),
            bold=True,
            color=get_color_from_hex(COLORS['text_primary'])
        )
        top_bar.add_widget(title)
        
        layout.add_widget(top_bar)
        
        # Açıklama
        desc = Label(
            text='Hangi ülkelerin kanallarını istiyorsunuz?',
            font_size=dp(14),
            color=get_color_from_hex(COLORS['text_secondary']),
            size_hint_y=None,
            height=dp(30)
        )
        layout.add_widget(desc)
        
        # Seçim bilgisi
        self.selection_label = Label(
            text='Seçilen: 0 ülke',
            font_size=dp(12),
            color=get_color_from_hex(COLORS['success']),
            size_hint_y=None,
            height=dp(25)
        )
        layout.add_widget(self.selection_label)
        
        # Ülke listesi
        scroll = ScrollView()
        self.country_layout = GridLayout(cols=2, spacing=dp(10), size_hint_y=None, padding=dp(5))
        self.country_layout.bind(minimum_height=self.country_layout.setter('height'))
        
        # Öne çıkan ülkeler (en üstte)
        featured = ['turkey', 'germany', 'romania', 'austria']
        
        self.country_buttons = {}
        
        # Öne çıkan ülkeleri ekle
        for country in featured:
            btn = self._create_country_button(country, featured=True)
            self.country_layout.add_widget(btn)
            
        # Diğer ülkeleri ekle
        for country in sorted(COUNTRY_FLAGS.keys()):
            if country not in featured:
                btn = self._create_country_button(country)
                self.country_layout.add_widget(btn)
                
        scroll.add_widget(self.country_layout)
        layout.add_widget(scroll)
        
        # Format seçimi
        format_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        
        format_label = Label(
            text='Format:',
            size_hint_x=None,
            width=dp(60),
            color=get_color_from_hex(COLORS['text_secondary'])
        )
        format_layout.add_widget(format_label)
        
        self.format_spinner = Spinner(
            text='M3U',
            values=('M3U', 'M3U8', 'TXT'),
            size_hint_x=None,
            width=dp(120)
        )
        format_layout.add_widget(self.format_spinner)
        format_layout.add_widget(Label())  # Spacer
        
        layout.add_widget(format_layout)
        
        # İşle butonu
        process_btn = RoundedButton(
            text='🚀 Oluştur',
            size_hint=(1, None),
            height=dp(55),
            font_size=dp(18),
            bg_color=COLORS['success']
        )
        process_btn.bind(on_press=self.process_links)
        layout.add_widget(process_btn)
        
        self.add_widget(layout)
        
    def _create_country_button(self, country, featured=False):
        btn = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(80))
        
        flag = COUNTRY_FLAGS.get(country, '🏳️')
        name = country.replace('_', ' ').title()
        
        inner_btn = RoundedButton(
            text=f'{flag}\n{name}',
            bg_color=COLORS['warning'] if featured else COLORS['card_bg'],
            halign='center'
        )
        inner_btn.country = country
        inner_btn.bind(on_press=self.toggle_country)
        
        self.country_buttons[country] = inner_btn
        btn.add_widget(inner_btn)
        
        if featured:
            star = Label(
                text='⭐ Önerilen',
                font_size=dp(10),
                color=get_color_from_hex(COLORS['warning']),
                size_hint_y=None,
                height=dp(15)
            )
            btn.add_widget(star)
            
        return btn
        
    def toggle_country(self, instance):
        country = instance.country
        
        if country in self.selected_countries:
            self.selected_countries.remove(country)
            instance.bg_color = COLORS['card_bg']
        else:
            self.selected_countries.add(country)
            instance.bg_color = COLORS['success']
            
        instance.update_canvas()
        self.selection_label.text = f'Seçilen: {len(self.selected_countries)} ülke'
        
    def update_bg(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*get_color_from_hex(COLORS['bg_dark']))
            Rectangle(pos=self.pos, size=self.size)
            
    def go_back(self, instance):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'auto_result'
        
    def process_links(self, instance):
        if not self.selected_countries:
            self.show_error('Lütfen en az bir ülke seçin!')
            return
            
        # İşlemeye başla
        app = App.get_running_app()
        app.selected_countries = self.selected_countries
        app.output_format = self.format_spinner.text.lower()
        
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'processing'
        
    def show_error(self, message):
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(20))
        
        icon = Label(text='⚠️', font_size=dp(50))
        content.add_widget(icon)
        
        label = Label(
            text=message,
            font_size=dp(14),
            color=get_color_from_hex(COLORS['text_primary']),
            halign='center'
        )
        label.bind(size=label.setter('text_size'))
        content.add_widget(label)
        
        btn = RoundedButton(
            text='Tamam',
            size_hint=(0.5, None),
            height=dp(45),
            pos_hint={'center_x': 0.5},
            bg_color=COLORS['warning']
        )
        
        popup = Popup(
            title='',
            content=content,
            size_hint=(0.8, 0.35),
            separator_height=0
        )
        
        btn.bind(on_press=popup.dismiss)
        content.add_widget(btn)
        popup.open()


class ProcessingScreen(Screen):
    """İşleme ekranı"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
    def on_enter(self):
        self.clear_widgets()
        self.build_ui()
        self.start_processing()
        
    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        layout.bind(pos=self.update_bg, size=self.update_bg)
        
        # Başlık
        title = Label(
            text='⚙️ İşleniyor...',
            font_size=dp(24),
            bold=True,
            color=get_color_from_hex(COLORS['text_primary']),
            size_hint_y=None,
            height=dp(50)
        )
        layout.add_widget(title)
        
        # İlerleme
        self.progress_label = Label(
            text='Linkleri indiriliyor...',
            font_size=dp(16),
            color=get_color_from_hex(COLORS['text_secondary']),
            size_hint_y=None,
            height=dp(30)
        )
        layout.add_widget(self.progress_label)
        
        self.progress_bar = ProgressBar(max=100, value=0, size_hint_y=None, height=dp(30))
        layout.add_widget(self.progress_bar)
        
        # İstatistikler
        stats_card = StyledCard(size_hint_y=None, height=dp(150))
        self.stats_layout = BoxLayout(orientation='vertical', spacing=dp(10))
        
        self.total_channels_label = Label(
            text='📺 Toplam Kanal: 0',
            font_size=dp(14),
            color=get_color_from_hex(COLORS['text_primary'])
        )
        self.filtered_channels_label = Label(
            text='✅ Filtrelenen: 0',
            font_size=dp(14),
            color=get_color_from_hex(COLORS['success'])
        )
        self.current_link_label = Label(
            text='🔗 İşlenen: -',
            font_size=dp(12),
            color=get_color_from_hex(COLORS['text_secondary'])
        )
        
        self.stats_layout.add_widget(self.total_channels_label)
        self.stats_layout.add_widget(self.filtered_channels_label)
        self.stats_layout.add_widget(self.current_link_label)
        
        stats_card.add_widget(self.stats_layout)
        layout.add_widget(stats_card)
        
        # Spacer
        layout.add_widget(Label())
        
        self.add_widget(layout)
        
    def update_bg(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*get_color_from_hex(COLORS['bg_dark']))
            Rectangle(pos=self.pos, size=self.size)
            
    def start_processing(self):
        threading.Thread(target=self._process_links, daemon=True).start()
        
    def _process_links(self):
        app = App.get_running_app()
        working_links = getattr(app, 'working_links', [])
        selected_countries = getattr(app, 'selected_countries', set())
        output_format = getattr(app, 'output_format', 'm3u')
        
        all_channels = []
        filtered_channels = []
        total = len(working_links)
        
        for i, link in enumerate(working_links):
            Clock.schedule_once(lambda dt, l=link: self._update_current(l))
            Clock.schedule_once(lambda dt, p=(i+1)/total*50: self._update_progress(p))
            
            try:
                response = requests.get(link, timeout=30)
                content = response.text
                channels, groups = IPTVParser.parse_m3u(content)
                
                all_channels.extend(channels)
                
                # Ülkeye göre filtrele
                for ch in channels:
                    group_name = ch.get('group', '')
                    channel_name = ch.get('name', '')
                    detected_country = IPTVParser.detect_country(group_name, channel_name)
                    
                    if detected_country in selected_countries:
                        ch['detected_country'] = detected_country
                        filtered_channels.append(ch)
                        
                Clock.schedule_once(lambda dt, t=len(all_channels), f=len(filtered_channels): 
                    self._update_stats(t, f))
                    
            except Exception as e:
                print(f"Error processing {link}: {e}")
                continue
                
        Clock.schedule_once(lambda dt: self._update_progress(75))
        Clock.schedule_once(lambda dt: self._update_label('Dosya oluşturuluyor...'))
        
        # Dosya oluştur
        content = IPTVParser.generate_m3u(filtered_channels, output_format)
        
        # Kaydet
        try:
            from android.storage import primary_external_storage_path
            download_path = os.path.join(primary_external_storage_path(), 'Download')
        except:
            download_path = os.path.expanduser('~')
            
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        countries_str = '_'.join(sorted(selected_countries)[:3])
        filename = f'iptv_{countries_str}_{timestamp}.{output_format}'
        filepath = os.path.join(download_path, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
            
        app.output_filepath = filepath
        app.filtered_channels = filtered_channels
        
        Clock.schedule_once(lambda dt: self._update_progress(100))
        Clock.schedule_once(self._processing_complete)
        
    def _update_progress(self, value):
        self.progress_bar.value = value
        
    def _update_label(self, text):
        self.progress_label.text = text
        
    def _update_current(self, link):
        self.current_link_label.text = f'🔗 İşlenen: {link[:40]}...'
        
    def _update_stats(self, total, filtered):
        self.total_channels_label.text = f'📺 Toplam Kanal: {total}'
        self.filtered_channels_label.text = f'✅ Filtrelenen: {filtered}'
        
    def _processing_complete(self, dt):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'complete'


class ManualEditListScreen(Screen):
    """Manuel düzenleme - link listesi"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
    def on_enter(self):
        self.clear_widgets()
        self.build_ui()
        
    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        layout.bind(pos=self.update_bg, size=self.update_bg)
        
        app = App.get_running_app()
        working_links = getattr(app, 'working_links', [])
        
        # Üst bar
        top_bar = BoxLayout(size_hint_y=None, height=dp(50))
        
        back_btn = RoundedButton(
            text='←',
            size_hint=(None, None),
            size=(dp(50), dp(40)),
            bg_color=COLORS['bg_light']
        )
        back_btn.bind(on_press=self.go_back)
        top_bar.add_widget(back_btn)
        
        title = Label(
            text='✏️ Manuel Düzenleme',
            font_size=dp(20),
            bold=True,
            color=get_color_from_hex(COLORS['text_primary'])
        )
        top_bar.add_widget(title)
        
        layout.add_widget(top_bar)
        
        # Açıklama
        desc = Label(
            text=f'{len(working_links)} çalışan link bulundu.\nDüzenlemek istediğiniz linke tıklayın.',
            font_size=dp(14),
            color=get_color_from_hex(COLORS['text_secondary']),
            size_hint_y=None,
            height=dp(50),
            halign='center'
        )
        desc.bind(size=desc.setter('text_size'))
        layout.add_widget(desc)
        
        # Link listesi
        scroll = ScrollView()
        list_layout = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None)
        list_layout.bind(minimum_height=list_layout.setter('height'))
        
        for i, link in enumerate(working_links):
            item = self._create_link_item(i + 1, link)
            list_layout.add_widget(item)
            
        scroll.add_widget(list_layout)
        layout.add_widget(scroll)
        
        self.add_widget(layout)
        
    def _create_link_item(self, index, link):
        item = StyledCard(size_hint_y=None, height=dp(80))
        inner = BoxLayout(orientation='horizontal', spacing=dp(10))
        
        # İndeks
        index_label = Label(
            text=str(index),
            font_size=dp(20),
            bold=True,
            color=get_color_from_hex(COLORS['primary']),
            size_hint_x=None,
            width=dp(40)
        )
        inner.add_widget(index_label)
        
        # Link bilgisi
        info_layout = BoxLayout(orientation='vertical')
        
        # URL'den domain çıkar
        domain = urlparse(link).netloc or link[:30]
        
        domain_label = Label(
            text=domain,
            font_size=dp(14),
            color=get_color_from_hex(COLORS['text_primary']),
            halign='left'
        )
        domain_label.bind(size=domain_label.setter('text_size'))
        
        link_label = Label(
            text=link[:50] + '...' if len(link) > 50 else link,
            font_size=dp(11),
            color=get_color_from_hex(COLORS['text_secondary']),
            halign='left'
        )
        link_label.bind(size=link_label.setter('text_size'))
        
        info_layout.add_widget(domain_label)
        info_layout.add_widget(link_label)
        inner.add_widget(info_layout)
        
        # Düzenle butonu
        edit_btn = RoundedButton(
            text='📝',
            size_hint=(None, None),
            size=(dp(50), dp(50)),
            bg_color=COLORS['primary']
        )
        edit_btn.link_url = link
        edit_btn.link_index = index
        edit_btn.bind(on_press=self.edit_link)
        inner.add_widget(edit_btn)
        
        item.add_widget(inner)
        return item
        
    def update_bg(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*get_color_from_hex(COLORS['bg_dark']))
            Rectangle(pos=self.pos, size=self.size)
            
    def go_back(self, instance):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'auto_result'
        
    def edit_link(self, instance):
        app = App.get_running_app()
        app.current_edit_link = instance.link_url
        app.current_edit_index = instance.link_index
        
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'link_editor'


class LinkEditorScreen(Screen):
    """Tek link düzenleme ekranı"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_groups = set()
        
    def on_enter(self):
        self.clear_widgets()
        self.selected_groups = set()
        self.build_ui()
        self.load_link_content()
        
    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        layout.bind(pos=self.update_bg, size=self.update_bg)
        
        app = App.get_running_app()
        link_index = getattr(app, 'current_edit_index', 1)
        working_links = getattr(app, 'working_links', [])
        
        # Üst bar
        top_bar = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        
        back_btn = RoundedButton(
            text='←',
            size_hint=(None, None),
            size=(dp(50), dp(40)),
            bg_color=COLORS['bg_light']
        )
        back_btn.bind(on_press=self.go_back)
        top_bar.add_widget(back_btn)
        
        title = Label(
            text=f'Link {link_index}/{len(working_links)}',
            font_size=dp(18),
            bold=True,
            color=get_color_from_hex(COLORS['text_primary'])
        )
        top_bar.add_widget(title)
        
        layout.add_widget(top_bar)
        
        # Yükleniyor göstergesi
        self.loading_label = Label(
            text='⏳ Kanallar yükleniyor...',
            font_size=dp(16),
            color=get_color_from_hex(COLORS['text_secondary'])
        )
        layout.add_widget(self.loading_label)
        
        # Kanal listesi (başta gizli)
        self.content_layout = BoxLayout(orientation='vertical', spacing=dp(10))
        self.content_layout.opacity = 0
        
        # İstatistikler
        self.stats_label = Label(
            text='',
            font_size=dp(14),
            color=get_color_from_hex(COLORS['text_secondary']),
            size_hint_y=None,
            height=dp(30)
        )
        self.content_layout.add_widget(self.stats_label)
        
        # Seçim bilgisi
        self.selection_label = Label(
            text='Seçilen: 0 grup',
            font_size=dp(12),
            color=get_color_from_hex(COLORS['success']),
            size_hint_y=None,
            height=dp(25)
        )
        self.content_layout.add_widget(self.selection_label)
        
        # Kanal listesi scroll
        scroll = ScrollView()
        self.list_layout = BoxLayout(orientation='vertical', spacing=dp(8), size_hint_y=None)
        self.list_layout.bind(minimum_height=self.list_layout.setter('height'))
        scroll.add_widget(self.list_layout)
        self.content_layout.add_widget(scroll)
        
        layout.add_widget(self.content_layout)
        
        # Alt butonlar
        self.bottom_bar = BoxLayout(size_hint_y=None, height=dp(55), spacing=dp(10), opacity=0)
        
        save_btn = RoundedButton(
            text='💾 Kaydet',
            bg_color=COLORS['success']
        )
        save_btn.bind(on_press=self.save_selection)
        self.bottom_bar.add_widget(save_btn)
        
        layout.add_widget(self.bottom_bar)
        
        self.add_widget(layout)
        
    def load_link_content(self):
        threading.Thread(target=self._load_content, daemon=True).start()
        
    def _load_content(self):
        app = App.get_running_app()
        link = getattr(app, 'current_edit_link', '')
        
        try:
            response = requests.get(link, timeout=30)
            channels, groups = IPTVParser.parse_m3u(response.text)
            
            self.channels = channels
            self.groups = groups
            
            Clock.schedule_once(self._display_content)
            
        except Exception as e:
            Clock.schedule_once(lambda dt: self._show_error(str(e)))
            
    def _display_content(self, dt):
        self.loading_label.opacity = 0
        self.content_layout.opacity = 1
        self.bottom_bar.opacity = 1
        
        self.stats_label.text = f'📊 {len(self.groups)} grup • {len(self.channels)} kanal'
        
        for group_name, group_data in sorted(self.groups.items()):
            item = ChannelGroupItem(
                group_name=group_name,
                channel_count=len(group_data['channels']),
                logo_url=group_data.get('logo'),
                on_select=self.on_group_select
            )
            self.list_layout.add_widget(item)
            
    def _show_error(self, error):
        self.loading_label.text = f'❌ Hata: {error}'
        
    def on_group_select(self, group_name, selected):
        if selected:
            self.selected_groups.add(group_name)
        else:
            self.selected_groups.discard(group_name)
            
        self.selection_label.text = f'Seçilen: {len(self.selected_groups)} grup'
        
    def update_bg(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*get_color_from_hex(COLORS['bg_dark']))
            Rectangle(pos=self.pos, size=self.size)
            
    def go_back(self, instance):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'manual_edit_list'
        
    def save_selection(self, instance):
        if not self.selected_groups:
            self.show_message('Uyarı', 'Lütfen en az bir grup seçin!')
            return
            
        # Seçili kanalları topla
        selected_channels = []
        for group_name in self.selected_groups:
            if group_name in self.groups:
                selected_channels.extend(self.groups[group_name]['channels'])
                
        # M3U oluştur
        content = IPTVParser.generate_m3u(selected_channels)
        
        # Kaydet
        try:
            from android.storage import primary_external_storage_path
            download_path = os.path.join(primary_external_storage_path(), 'Download')
        except:
            download_path = os.path.expanduser('~')
            
        app = App.get_running_app()
        link_index = getattr(app, 'current_edit_index', 1)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'iptv_link{link_index}_{timestamp}.m3u'
        filepath = os.path.join(download_path, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
            
        self.show_save_success(filepath)
        
    def show_message(self, title, message):
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(20))
        
        icon = Label(text='⚠️', font_size=dp(50))
        content.add_widget(icon)
        
        label = Label(
            text=message,
            font_size=dp(14),
            color=get_color_from_hex(COLORS['text_primary']),
            halign='center'
        )
        label.bind(size=label.setter('text_size'))
        content.add_widget(label)
        
        btn = RoundedButton(
            text='Tamam',
            size_hint=(0.5, None),
            height=dp(45),
            pos_hint={'center_x': 0.5},
            bg_color=COLORS['warning']
        )
        
        popup = Popup(
            title='',
            content=content,
            size_hint=(0.8, 0.35),
            separator_height=0
        )
        
        btn.bind(on_press=popup.dismiss)
        content.add_widget(btn)
        popup.open()
        
    def show_save_success(self, filepath):
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        
        icon = Label(text='✅', font_size=dp(50))
        content.add_widget(icon)
        
        title_label = Label(
            text='Başarıyla Kaydedildi!',
            font_size=dp(18),
            bold=True,
            color=get_color_from_hex(COLORS['text_primary'])
        )
        content.add_widget(title_label)
        
        path_label = Label(
            text=filepath,
            font_size=dp(11),
            color=get_color_from_hex(COLORS['text_secondary']),
            halign='center'
        )
        path_label.bind(size=path_label.setter('text_size'))
        content.add_widget(path_label)
        
        btn_layout = BoxLayout(spacing=dp(10), size_hint_y=None, height=dp(45))
        
        back_btn = RoundedButton(
            text='Listeye Dön',
            bg_color=COLORS['primary']
        )
        
        popup = Popup(
            title='',
            content=content,
            size_hint=(0.9, 0.45),
            separator_height=0
        )
        
        def go_list(x):
            popup.dismiss()
            self.manager.transition = SlideTransition(direction='right')
            self.manager.current = 'manual_edit_list'
            
        back_btn.bind(on_press=go_list)
        btn_layout.add_widget(back_btn)
        
        content.add_widget(btn_layout)
        popup.open()


class CompleteScreen(Screen):
    """İşlem tamamlandı ekranı"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
    def on_enter(self):
        self.clear_widgets()
        self.build_ui()
        
    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=dp(30), spacing=dp(20))
        layout.bind(pos=self.update_bg, size=self.update_bg)
        
        app = App.get_running_app()
        filepath = getattr(app, 'output_filepath', '')
        filtered = len(getattr(app, 'filtered_channels', []))
        
        # Başarı ikonu
        icon = Label(text='🎉', font_size=dp(80), size_hint_y=0.3)
        layout.add_widget(icon)
        
        # Başlık
        title = Label(
            text='İşlem Tamamlandı!',
            font_size=dp(28),
            bold=True,
            color=get_color_from_hex(COLORS['text_primary']),
            size_hint_y=None,
            height=dp(50)
        )
        layout.add_widget(title)
        
        # Sonuç kartı
        result_card = StyledCard(size_hint_y=None, height=dp(150))
        result_inner = BoxLayout(orientation='vertical', spacing=dp(15))
        
        channel_label = Label(
            text=f'📺 {filtered} kanal filtrelendi',
            font_size=dp(18),
            color=get_color_from_hex(COLORS['success'])
        )
        result_inner.add_widget(channel_label)
        
        file_label = Label(
            text='📁 Dosya kaydedildi:',
            font_size=dp(14),
            color=get_color_from_hex(COLORS['text_secondary'])
        )
        result_inner.add_widget(file_label)
        
        path_label = Label(
            text=os.path.basename(filepath),
            font_size=dp(12),
            color=get_color_from_hex(COLORS['primary'])
        )
        result_inner.add_widget(path_label)
        
        result_card.add_widget(result_inner)
        layout.add_widget(result_card)
        
        # Spacer
        layout.add_widget(Label())
        
        # Butonlar
        btn_layout = BoxLayout(orientation='vertical', spacing=dp(15), size_hint_y=None, height=dp(120))
        
        new_btn = RoundedButton(
            text='🔄 Yeni İşlem',
            size_hint=(1, None),
            height=dp(50),
            bg_color=COLORS['primary']
        )
        new_btn.bind(on_press=self.new_process)
        btn_layout.add_widget(new_btn)
        
        home_btn = RoundedButton(
            text='🏠 Ana Sayfa',
            size_hint=(1, None),
            height=dp(50),
            bg_color=COLORS['bg_light']
        )
        home_btn.bind(on_press=self.go_home)
        btn_layout.add_widget(home_btn)
        
        layout.add_widget(btn_layout)
        
        self.add_widget(layout)
        
    def update_bg(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*get_color_from_hex(COLORS['bg_dark']))
            Rectangle(pos=self.pos, size=self.size)
            
    def new_process(self, instance):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'auto_input'
        
    def go_home(self, instance):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'welcome'


# ========================= ANA UYGULAMA =========================

class IPTVEditorApp(App):
    """Ana uygulama sınıfı"""
    
    def build(self):
        # Pencere ayarları
        Window.clearcolor = get_color_from_hex(COLORS['bg_dark'])
        
        # Ekran yöneticisi
        sm = ScreenManager()
        
        # Ekranları ekle
        sm.add_widget(WelcomeScreen(name='welcome'))
        sm.add_widget(ManualInputScreen(name='manual_input'))
        sm.add_widget(ChannelListScreen(name='channel_list'))
        sm.add_widget(AutoInputScreen(name='auto_input'))
        sm.add_widget(TestingScreen(name='testing'))
        sm.add_widget(AutoResultScreen(name='auto_result'))
        sm.add_widget(CountrySelectScreen(name='country_select'))
        sm.add_widget(ProcessingScreen(name='processing'))
        sm.add_widget(ManualEditListScreen(name='manual_edit_list'))
        sm.add_widget(LinkEditorScreen(name='link_editor'))
        sm.add_widget(CompleteScreen(name='complete'))
        
        return sm


if __name__ == '__main__':
    IPTVEditorApp().run()
