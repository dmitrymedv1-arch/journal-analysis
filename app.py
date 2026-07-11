"""
Journal Analytics System - Full Featured Version
Complete analysis of academic journals using OpenAlex API
All features: detailed citations, topic relationships, citing works analysis, and more
"""

# ============================================
# CONFIGURATION
# ============================================

BATCH_SIZE = 50
MAX_RETRIES = 3
TIMEOUT = 30
DELAY_BETWEEN_BATCHES = 0.5
MAX_CONCURRENT_REQUESTS = 10
RETRY_DELAY = 2
SHOW_DEBUG_LOGS = True
USE_CACHE = True
MAX_PUBLICATIONS_TO_ANALYZE = 5000
MAX_CITATIONS_PER_PUBLICATION = 500

# ============================================
# IMPORTS
# ============================================

import asyncio
import aiohttp
import pandas as pd
import streamlit as st
from streamlit import session_state as ss
import re
import time
from datetime import datetime
import json
from typing import List, Set, Dict, Tuple, Optional, Any
from collections import Counter, defaultdict
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
from io import BytesIO
import base64
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import requests
import os
import hashlib
from matplotlib.ticker import MaxNLocator
import html
import colorsys
from tenacity import retry, stop_after_attempt, wait_exponential
from concurrent.futures import ThreadPoolExecutor
import math
from itertools import combinations
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any
from enum import Enum
import seaborn as sns

# ============================================
# COLOR UTILITIES (FROM OLD CODE)
# ============================================

def hex_to_rgb(hex_color: str) -> tuple:
    """Convert hex color to RGB tuple"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb: tuple) -> str:
    """Convert RGB tuple to hex color"""
    return '#{:02x}{:02x}{:02x}'.format(int(rgb[0]), int(rgb[1]), int(rgb[2]))

def get_complementary_color(hex_color: str) -> str:
    """Generate complementary color by rotating hue by 180 degrees"""
    rgb = hex_to_rgb(hex_color)
    h, s, v = colorsys.rgb_to_hsv(rgb[0]/255.0, rgb[1]/255.0, rgb[2]/255.0)
    complementary_hue = (h + 0.5) % 1.0
    complementary_rgb = colorsys.hsv_to_rgb(complementary_hue, s, v)
    return rgb_to_hex(tuple(int(c * 255) for c in complementary_rgb))

def get_contrast_color(hex_color: str) -> str:
    """Get contrasting color (black or white) for text on a colored background"""
    rgb = hex_to_rgb(hex_color)
    luminance = (0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]) / 255
    return '#FFFFFF' if luminance < 0.5 else '#000000'

def get_analogous_colors(hex_color: str, count: int = 2) -> List[str]:
    """Generate analogous colors (colors adjacent on color wheel)"""
    rgb = hex_to_rgb(hex_color)
    h, s, v = colorsys.rgb_to_hsv(rgb[0]/255.0, rgb[1]/255.0, rgb[2]/255.0)
    colors_list = []
    step = 30 / 360.0
    for i in range(count):
        offset = (i + 1) * step
        new_hue = (h + offset) % 1.0
        new_rgb = colorsys.hsv_to_rgb(new_hue, s, v)
        colors_list.append(rgb_to_hex(tuple(int(c * 255) for c in new_rgb)))
    return colors_list

def get_gradient_colors(hex_color: str, steps: int = 5) -> List[str]:
    """Generate gradient colors from base color to lighter shades"""
    rgb = hex_to_rgb(hex_color)
    colors_list = []
    for i in range(steps):
        factor = 0.3 + (i * 0.14)
        new_rgb = tuple(min(255, int(c * (1 + factor * 0.5))) for c in rgb)
        colors_list.append(rgb_to_hex(new_rgb))
    return colors_list

def generate_css_variables(base_color: str, accent_color: str = None) -> Dict[str, str]:
    """Generate complete CSS variable set for the theme"""
    if accent_color is None:
        accent_color = get_complementary_color(base_color)
    
    gradient_start = base_color
    gradient_end = accent_color
    lighter_base = get_gradient_colors(base_color, 1)[0]
    lighter_accent = get_gradient_colors(accent_color, 1)[0]
    base_contrast = get_contrast_color(base_color)
    accent_contrast = get_contrast_color(accent_color)
    analogous = get_analogous_colors(base_color, 2)
    
    return {
        '--primary-color': base_color,
        '--secondary-color': accent_color,
        '--primary-light': lighter_base,
        '--secondary-light': lighter_accent,
        '--primary-contrast': base_contrast,
        '--secondary-contrast': accent_contrast,
        '--gradient-start': gradient_start,
        '--gradient-end': gradient_end,
        '--accent-1': analogous[0] if len(analogous) > 0 else accent_color,
        '--accent-2': analogous[1] if len(analogous) > 1 else accent_color,
        '--hover-light': f"{base_color}20",
    }

def apply_theme_css(base_color: str, accent_color: str = None):
    """Apply dynamic CSS theme based on selected colors"""
    if accent_color is None:
        accent_color = get_complementary_color(base_color)
    
    css_vars = generate_css_variables(base_color, accent_color)
    
    theme_css = f"""
    <style>
        :root {{
            --primary: {css_vars['--primary-color']};
            --secondary: {css_vars['--secondary-color']};
            --primary-light: {css_vars['--primary-light']};
            --secondary-light: {css_vars['--secondary-light']};
            --primary-contrast: {css_vars['--primary-contrast']};
            --secondary-contrast: {css_vars['--secondary-contrast']};
            --gradient-start: {css_vars['--gradient-start']};
            --gradient-end: {css_vars['--gradient-end']};
            --accent-1: {css_vars['--accent-1']};
            --accent-2: {css_vars['--accent-2']};
            --hover-light: {css_vars['--hover-light']};
        }}
        
        .stApp {{
            background: linear-gradient(135deg, 
                rgba({int(hex_to_rgb(css_vars['--gradient-start'])[0])}, {int(hex_to_rgb(css_vars['--gradient-start'])[1])}, {int(hex_to_rgb(css_vars['--gradient-start'])[2])}, 0.05) 0%,
                rgba({int(hex_to_rgb(css_vars['--gradient-end'])[0])}, {int(hex_to_rgb(css_vars['--gradient-end'])[1])}, {int(hex_to_rgb(css_vars['--gradient-end'])[2])}, 0.08) 100%);
        }}
        
        .metric-number {{
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        .section-header {{
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
        }}
        
        .rank-item {{
            border-left: 3px solid var(--primary);
        }}
        
        .rank-number {{
            color: var(--primary);
        }}
        
        .progress-fill {{
            background: linear-gradient(90deg, var(--primary), var(--secondary));
        }}
        
        .section-title {{
            border-bottom: 3px solid var(--primary);
        }}
        
        .metric-card:hover {{
            box-shadow: 0 6px 12px rgba({int(hex_to_rgb(css_vars['--primary-color'])[0])}, {int(hex_to_rgb(css_vars['--primary-color'])[1])}, {int(hex_to_rgb(css_vars['--primary-color'])[2])}, 0.15);
        }}
        
        * {{
            transition: background-color 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease;
        }}
    </style>
    """
    st.markdown(theme_css, unsafe_allow_html=True)

# ============================================
# LOCALIZATION
# ============================================

LANG = {
    'en': {
        'app_title': '📊 Journal Analytics System',
        'app_subtitle': 'Complete journal analysis with citation network and topic relationships',
        'settings': '⚙️ Settings',
        'language': '🌐 Language',
        'language_en': 'English',
        'language_ru': 'Russian',
        'issn_input': '📝 Journal ISSN',
        'issn_placeholder': '1234-5678 or 12345678 or 1234 5678',
        'issn_help': 'Enter ISSN in any format (with or without hyphens, with or without spaces)',
        'period_input': '📅 Analysis Period',
        'period_placeholder': '2023 or 2023-2025 or 2019-2021,2023-2026',
        'period_help': 'Single year, range, or multiple ranges separated by commas',
        'analyze_button': '🔍 Analyze Journal',
        'no_issn': '⚠️ Please enter a valid ISSN',
        'invalid_issn': '⚠️ Invalid ISSN format. Please enter 8 digits (e.g., 1234-5678)',
        'invalid_period': '⚠️ Invalid period format. Use: 2023 or 2023-2025 or 2019-2021,2023-2026',
        'analysis_started': '🔄 Starting journal analysis...',
        'fetching_journal': '📚 Fetching journal information...',
        'journal_not_found': '❌ Journal not found. Please check ISSN.',
        'fetching_publications': '📄 Fetching publications...',
        'fetching_citations': '📊 Fetching citations...',
        'analyzing_data': '🔬 Analyzing data...',
        'generating_report': '📄 Generating HTML report...',
        'analysis_complete': '✅ Analysis complete! Found {count} publications in {time:.1f} sec.',
        'download_report': '💾 Download HTML Report',
        'report_preview': '📋 Report Preview',
        'no_data': '👈 Run analysis first',
        
        # Metrics
        'total_publications': 'Total Publications',
        'total_citations': 'Total Citations',
        'avg_citations': 'Avg Citations',
        'h_index': 'h-index',
        'g_index': 'g-index',
        'i10_index': 'i10-index',
        'i100_index': 'i100-index',
        'open_access': 'Open Access',
        'active_years': 'Active Years',
        'unique_authors': 'Unique Authors',
        'unique_countries': 'Unique Countries',
        'unique_affiliations': 'Unique Affiliations',
        'papers_per_year': 'Papers/Year',
        'citations_per_year': 'Citations/Year',
        'median_citations': 'Median Citations',
        'max_citations': 'Max Citations',
        'citing_works_total': 'Total Citing Works',
        'unique_citing_journals': 'Unique Citing Journals',
        'unique_citing_publishers': 'Unique Citing Publishers',
        'unique_citing_authors': 'Unique Citing Authors',
        'unique_citing_countries': 'Unique Citing Countries',
        'avg_citation_lag': 'Avg Citation Lag (years)',
        'hot_topics': 'Hot Topics (Citation Impact)',
        'topic_overlap': 'Topic Overlap',
        
        # Report sections
        'executive_summary': '📊 Executive Summary',
        'publication_dynamics': '📈 Publication Dynamics',
        'most_cited_publications': '🏆 Most Cited Publications',
        'author_analysis': '👨‍🎓 Author Analysis',
        'top_affiliations': '🏛️ Top Affiliations',
        'top_countries': '🌍 Top Countries',
        'unique_countries_per_reference': 'Unique Countries per Reference',
        'authors_per_country': 'Authors per Country',
        'collaboration_patterns': 'Collaboration Patterns',
        'affiliation_analysis': '🏛️ Affiliation & Country Analysis',
        'citation_analysis': '📊 Citation Analysis',
        'citation_distribution': 'Citation Distribution',
        'citation_matrix': 'Citation Matrix (Publication Year → Citation Year)',
        'citing_works_analysis': '📚 Citing Works Analysis',
        'citing_works_distribution': '📊 Citing Works Distribution',
        'topic_analysis': '🏷️ Topics Analysis',
        'topic_relationship': '🔄 Topic Relationship',
        'detailed_citations': '📋 Detailed Citations',
        'citation_timeline': '📈 Citation Timeline',
        'all_publications': '📚 All Publications',
        'publication_year': 'Publication Year',
        'number': 'Number',
        'citations': 'Citations',
        'citations_per_year': 'Citations/Year',
        'journal': 'Journal',
        'authors': 'Authors',
        'affiliations': 'Affiliations',
        'countries': 'Countries',
        'title': 'Title',
        'year': 'Year',
        'doi': 'DOI',
        'citing_work': 'Citing Work',
        'citing_journal': 'Citing Journal',
        'citing_year': 'Citing Year',
        'citing_date': 'Citing Date',
        'citation_lag': 'Citation Lag (years)',
        
        # Citing works distribution
        'top_citing_journals': 'Top Citing Journals',
        'top_citing_publishers': 'Top Citing Publishers',
        'top_citing_authors': 'Top Citing Authors',
        'top_citing_countries': 'Top Citing Countries',
        'top_citing_affiliations': 'Top Citing Affiliations',
        
        # Topics
        'topics': 'Topics',
        'fields': 'Fields',
        'domains': 'Domains',
        'concepts': 'Concepts',
        'subtopics': 'Subtopics',
        'publication_topics': 'Publication Topics',
        'citing_topics': 'Citing Topics',
        'topic_overlap_percentage': 'Topic Overlap Percentage',
        'hot_topic_index': 'Hot Topic Index',
        'ratio': 'Ratio',
        
        # Filters
        'filter_by_year': 'Filter by Year',
        'filter_by_author': 'Filter by Author',
        'filter_by_citations': 'Filter by Citations (min)',
        'search_publications': 'Search publications',
        'show_citations': 'Show Citations',
        'hide_citations': 'Hide Citations',
        
        # Color Theme
        'color_theme': '🎨 Color Theme',
        'preset_themes': 'Preset themes',
        'use_preset': 'Use preset theme',
        'pick_color': 'Pick your primary color',
        'primary_color': 'Primary',
        'complementary_color': 'Complementary',
        'default_theme': 'Default (Blue-Purple)',
        'emerald_theme': 'Emerald (Green-Teal)',
        'sunset_theme': 'Sunset (Orange-Coral)',
        'ocean_theme': 'Ocean (Deep Blue)',
        'royal_theme': 'Royal (Purple-Pink)',
        'forest_theme': 'Forest (Dark Green)',
        'cherry_theme': 'Cherry (Red-Pink)',
        'amber_theme': 'Amber (Yellow-Orange)',
        
        # Footer
        'footer': '© Journal Analytics System / Created by daM / Chimica Techno Acta',
        'journal_url': 'https://chimicatechnoacta.ru',
    },
    'ru': {
        'app_title': '📊 Система анализа журналов',
        'app_subtitle': 'Полный анализ журнала с сетью цитирований и взаимосвязью тем',
        'settings': '⚙️ Настройки',
        'language': '🌐 Язык',
        'language_en': 'Английский',
        'language_ru': 'Русский',
        'issn_input': '📝 ISSN журнала',
        'issn_placeholder': '1234-5678 или 12345678 или 1234 5678',
        'issn_help': 'Введите ISSN в любом формате (с дефисами или без, с пробелами или без)',
        'period_input': '📅 Период анализа',
        'period_placeholder': '2023 или 2023-2025 или 2019-2021,2023-2026',
        'period_help': 'Один год, диапазон или несколько диапазонов через запятую',
        'analyze_button': '🔍 Анализировать журнал',
        'no_issn': '⚠️ Введите корректный ISSN',
        'invalid_issn': '⚠️ Неверный формат ISSN. Введите 8 цифр (например, 1234-5678)',
        'invalid_period': '⚠️ Неверный формат периода. Используйте: 2023 или 2023-2025 или 2019-2021,2023-2026',
        'analysis_started': '🔄 Запуск анализа журнала...',
        'fetching_journal': '📚 Получение информации о журнале...',
        'journal_not_found': '❌ Журнал не найден. Проверьте ISSN.',
        'fetching_publications': '📄 Получение публикаций...',
        'fetching_citations': '📊 Получение цитирований...',
        'analyzing_data': '🔬 Анализ данных...',
        'generating_report': '📄 Генерация HTML отчета...',
        'analysis_complete': '✅ Анализ завершен! Найдено {count} публикаций за {time:.1f} сек.',
        'download_report': '💾 Скачать HTML отчет',
        'report_preview': '📋 Предпросмотр отчета',
        'no_data': '👈 Сначала выполните анализ',
        
        # Metrics
        'total_publications': 'Всего публикаций',
        'total_citations': 'Всего цитирований',
        'avg_citations': 'Среднее цитирований',
        'h_index': 'h-index',
        'g_index': 'g-index',
        'i10_index': 'i10-index',
        'i100_index': 'i100-index',
        'open_access': 'Открытый доступ',
        'active_years': 'Активных лет',
        'unique_authors': 'Уникальных авторов',
        'unique_countries': 'Уникальных стран',
        'unique_affiliations': 'Уникальных аффилиаций',
        'papers_per_year': 'Статей/год',
        'citations_per_year': 'Цитирований/год',
        'median_citations': 'Медиана цитирований',
        'max_citations': 'Максимум цитирований',
        'citing_works_total': 'Всего цитирующих работ',
        'unique_citing_journals': 'Уникальных цитирующих журналов',
        'unique_citing_publishers': 'Уникальных цитирующих издательств',
        'unique_citing_authors': 'Уникальных цитирующих авторов',
        'unique_citing_countries': 'Уникальных цитирующих стран',
        'avg_citation_lag': 'Средняя задержка цитирования (лет)',
        'hot_topics': 'Горячие темы',
        'topic_overlap': 'Пересечение тем',
        
        # Report sections
        'executive_summary': '📊 Сводка',
        'publication_dynamics': '📈 Динамика публикаций',
        'most_cited_publications': '🏆 Самые цитируемые публикации',
        'author_analysis': '👨‍🎓 Анализ авторов',
        'top_affiliations': '🏛️ Топ аффилиаций',
        'top_countries': '🌍 Топ стран',
        'unique_countries_per_reference': 'Уникальные страны по ссылке',
        'authors_per_country': 'Авторы по странам',
        'collaboration_patterns': 'Паттерны коллабораций',
        'affiliation_analysis': '🏛️ Анализ аффилиаций и стран',
        'citation_analysis': '📊 Анализ цитирований',
        'citation_distribution': 'Распределение цитирований',
        'citation_matrix': 'Матрица цитирований (год публикации → год цитирования)',
        'citing_works_analysis': '📚 Анализ цитирующих работ',
        'citing_works_distribution': '📊 Распределение цитирующих работ',
        'topic_analysis': '🏷️ Тематический анализ',
        'topic_relationship': '🔄 Взаимосвязь тем',
        'detailed_citations': '📋 Детальные цитирования',
        'citation_timeline': '📈 Временная шкала цитирований',
        'all_publications': '📚 Все публикации',
        'publication_year': 'Год публикации',
        'number': 'Число',
        'citations': 'Цитирований',
        'citations_per_year': 'Цитирований/год',
        'journal': 'Журнал',
        'authors': 'Авторы',
        'affiliations': 'Аффилиации',
        'countries': 'Страны',
        'title': 'Название',
        'year': 'Год',
        'doi': 'DOI',
        'citing_work': 'Цитирующая работа',
        'citing_journal': 'Цитирующий журнал',
        'citing_year': 'Год цитирования',
        'citing_date': 'Дата цитирования',
        'citation_lag': 'Задержка цитирования (лет)',
        
        # Citing works distribution
        'top_citing_journals': 'Топ цитирующих журналов',
        'top_citing_publishers': 'Топ цитирующих издательств',
        'top_citing_authors': 'Топ цитирующих авторов',
        'top_citing_countries': 'Топ цитирующих стран',
        'top_citing_affiliations': 'Топ цитирующих аффилиаций',
        
        # Topics
        'topics': 'Темы',
        'fields': 'Поля',
        'domains': 'Домены',
        'concepts': 'Концепты',
        'subtopics': 'Сабтопики',
        'publication_topics': 'Темы публикаций',
        'citing_topics': 'Темы цитирующих работ',
        'topic_overlap_percentage': 'Процент пересечения тем',
        'hot_topic_index': 'Индекс горячих тем',
        'ratio': 'Соотношение',
        
        # Filters
        'filter_by_year': 'Фильтр по году',
        'filter_by_author': 'Фильтр по автору',
        'filter_by_citations': 'Фильтр по цитированиям (мин)',
        'search_publications': 'Поиск публикаций',
        'show_citations': 'Показать цитирования',
        'hide_citations': 'Скрыть цитирования',
        
        # Color Theme
        'color_theme': '🎨 Цветовая тема',
        'preset_themes': 'Готовые темы',
        'use_preset': 'Использовать готовую тему',
        'pick_color': 'Выберите основной цвет',
        'primary_color': 'Основной',
        'complementary_color': 'Дополнительный',
        'default_theme': 'По умолчанию (Сине-Фиолетовый)',
        'emerald_theme': 'Изумруд (Зелено-Бирюзовый)',
        'sunset_theme': 'Закат (Оранжево-Коралловый)',
        'ocean_theme': 'Океан (Глубокий Синий)',
        'royal_theme': 'Королевский (Фиолетово-Розовый)',
        'forest_theme': 'Лес (Темно-Зеленый)',
        'cherry_theme': 'Вишня (Красно-Розовый)',
        'amber_theme': 'Янтарь (Желто-Оранжевый)',
        
        # Footer
        'footer': '© Journal Analytics System / Created by daM / Chimica Techno Acta',
        'journal_url': 'https://chimicatechnoacta.ru',
    }
}

def translate(key: str, lang: str = 'en', **kwargs) -> str:
    """Get translated string by key and language"""
    if lang not in LANG:
        lang = 'en'
    text = LANG[lang].get(key, key)
    if kwargs:
        try:
            text = text.format(**kwargs)
        except:
            pass
    return text

# ============================================
# DATA MODELS
# ============================================

@dataclass
class Author:
    display_name: str
    compare_name: str = ""
    orcid: str = ""
    affiliations: List[Dict] = field(default_factory=list)
    countries: List[str] = field(default_factory=list)
    works_count: int = 0
    cited_by_count: int = 0
    
    def __post_init__(self):
        if not self.compare_name and self.display_name:
            self.compare_name = self.display_name.lower()

@dataclass
class Affiliation:
    display_name: str
    country_code: str = ""
    country_name: str = ""
    ror: str = ""
    works_count: int = 0
    citations_count: int = 0

@dataclass
class Topic:
    display_name: str
    subfield: str = ""
    field: str = ""
    domain: str = ""
    score: float = 0.0
    publications_count: int = 0
    citations_count: int = 0
    hot_topic_index: float = 0.0

@dataclass
class Publication:
    id: str
    doi: str = ""
    title: str = ""
    publication_year: int = 0
    publication_date: str = ""
    authors: List[Author] = field(default_factory=list)
    affiliations: List[Affiliation] = field(default_factory=list)
    countries: List[str] = field(default_factory=list)
    journal_name: str = ""
    publisher: str = ""
    cited_by_count: int = 0
    is_oa: bool = False
    open_access_status: str = ""
    topics: List[Topic] = field(default_factory=list)
    concepts: List[str] = field(default_factory=list)
    fields: List[str] = field(default_factory=list)
    domains: List[str] = field(default_factory=list)
    citations: List['Citation'] = field(default_factory=list)
    citations_per_year: float = 0.0
    is_retracted: bool = False
    is_correction: bool = False
    citation_years: Dict[int, int] = field(default_factory=dict)

@dataclass
class Citation:
    citing_work_id: str
    citing_doi: str = ""
    citing_title: str = ""
    citing_year: int = 0
    citing_date: str = ""
    citing_journal: str = ""
    citing_publisher: str = ""
    citing_authors: List[Author] = field(default_factory=list)
    citing_affiliations: List[Affiliation] = field(default_factory=list)
    citing_countries: List[str] = field(default_factory=list)
    citing_topics: List[Topic] = field(default_factory=list)
    citing_concepts: List[str] = field(default_factory=list)
    citing_fields: List[str] = field(default_factory=list)
    citing_domains: List[str] = field(default_factory=list)
    citation_lag: int = 0

@dataclass
class Journal:
    id: str
    issn: str
    title: str
    publisher: str = ""
    works_count: int = 0
    cited_by_count: int = 0
    is_oa: bool = False
    created_date: str = ""
    updated_date: str = ""

# ============================================
# UTILITY FUNCTIONS
# ============================================

def clean_orcid(orcid_input: str) -> str:
    """Clean ORCID to standard format"""
    if not orcid_input:
        return ""
    orcid = orcid_input.strip().upper()
    if 'orcid.org/' in orcid:
        orcid = orcid.split('orcid.org/')[-1]
    orcid = re.sub(r'[^0-9X-]', '', orcid)
    if re.match(r'^\d{4}-\d{4}-\d{4}-\d{3}[\dX]$', orcid):
        return orcid
    if len(orcid) == 16 and orcid.isdigit():
        return f"{orcid[:4]}-{orcid[4:8]}-{orcid[8:12]}-{orcid[12:]}"
    return orcid

def normalize_author_name(name: str) -> Tuple[str, str]:
    """Normalize author name to format {Lastname} {FirstInitial}"""
    if not name or not isinstance(name, str):
        return "", ""
    
    name = name.strip()
    
    if ',' in name:
        last, first = name.split(',', 1)
        last = last.strip()
        first = first.strip()
        first_initial = ''
        if first:
            first_parts = first.split()
            for part in first_parts:
                if part and part[0].isalpha():
                    first_initial = part[0].upper()
                    break
        display_name = f"{last} {first_initial}." if first_initial else last
        compare_name = f"{last.lower()} {first_initial.lower()}."
        return compare_name, display_name
    
    parts = name.split()
    if len(parts) >= 2:
        last = parts[-1]
        first_initial = ''
        for part in parts[:-1]:
            if part and part[0].isalpha():
                first_initial = part[0].upper()
                break
        display_name = f"{last} {first_initial}." if first_initial else last
        compare_name = f"{last.lower()} {first_initial.lower()}."
        return compare_name, display_name
    
    if len(parts) == 1:
        display_name = parts[0]
        compare_name = parts[0].lower()
        return compare_name, display_name
    
    return name.lower(), name

def parse_issn(issn_input: str) -> Optional[str]:
    """Parse ISSN from various formats to XXXX-XXXX"""
    if not issn_input:
        return None
    
    issn_clean = re.sub(r'[^0-9Xx]', '', issn_input.strip())
    
    if len(issn_clean) == 8:
        if re.match(r'^[0-9]{7}[0-9Xx]$', issn_clean):
            return f"{issn_clean[:4]}-{issn_clean[4:]}"
    
    if re.match(r'^\d{4}-\d{3}[\dX]$', issn_input.strip(), re.IGNORECASE):
        return issn_input.strip().upper()
    
    return None

def parse_periods(period_input: str) -> List[Tuple[int, int]]:
    """Parse period string into list of (start_year, end_year) tuples"""
    if not period_input or not period_input.strip():
        current_year = datetime.now().year
        return [(current_year - 10, current_year)]
    
    periods = []
    parts = period_input.split(',')
    
    for part in parts:
        part = part.strip()
        if not part:
            continue
        
        if '-' in part:
            start_str, end_str = part.split('-', 1)
            try:
                start = int(start_str.strip())
                end = int(end_str.strip())
                if start <= end:
                    periods.append((start, end))
                else:
                    periods.append((end, start))
            except ValueError:
                continue
        else:
            try:
                year = int(part.strip())
                periods.append((year, year))
            except ValueError:
                continue
    
    if not periods:
        current_year = datetime.now().year
        return [(current_year - 10, current_year)]
    
    return periods

def safe_get(data: Dict, *keys, default=None):
    """Safe get from nested dict"""
    for key in keys:
        if isinstance(data, dict):
            data = data.get(key, default)
        else:
            return default
    return data

def chunks(lst, n):
    """Split list into chunks of size n"""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def get_cache_path(issn: str, periods_hash: str) -> str:
    """Get cache file path"""
    if not os.path.exists('cache'):
        os.makedirs('cache')
    return f"cache/journal_{issn}_{periods_hash}.json"

def load_from_cache(issn: str, periods_hash: str) -> Optional[Dict]:
    """Load data from cache"""
    if not USE_CACHE:
        return None
    
    cache_path = get_cache_path(issn, periods_hash)
    if os.path.exists(cache_path):
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if SHOW_DEBUG_LOGS:
                print(f"✅ Loaded from cache: {cache_path}")
            return data
        except Exception as e:
            if SHOW_DEBUG_LOGS:
                print(f"⚠️ Cache load error: {e}")
            return None
    return None

def save_to_cache(issn: str, periods_hash: str, data: Dict):
    """Save data to cache"""
    if not USE_CACHE:
        return
    
    cache_path = get_cache_path(issn, periods_hash)
    try:
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        if SHOW_DEBUG_LOGS:
            print(f"✅ Saved to cache: {cache_path}")
    except Exception as e:
        if SHOW_DEBUG_LOGS:
            print(f"⚠️ Cache save error: {e}")

# ============================================
# API CLIENT
# ============================================

async def fetch_with_retry(session, url, params=None, headers=None, method='GET', timeout_override=None):
    """Execute request with retries on error with proper timeout handling"""
    timeout_value = timeout_override if timeout_override else TIMEOUT
    
    for attempt in range(MAX_RETRIES):
        try:
            async with session.request(
                method, url, params=params, headers=headers, 
                timeout=aiohttp.ClientTimeout(total=timeout_value)
            ) as response:
                if response.status == 429:
                    retry_after = int(response.headers.get('Retry-After', RETRY_DELAY * (attempt + 1)))
                    if SHOW_DEBUG_LOGS:
                        print(f"⚠️ Rate limit, waiting {retry_after} sec...")
                    await asyncio.sleep(min(retry_after, 30))  # Не ждать больше 30 секунд
                    continue
                
                if response.status == 200:
                    return await response.json()
                elif response.status == 404:
                    # Not found - don't retry
                    return None
                else:
                    if SHOW_DEBUG_LOGS:
                        print(f"⚠️ Error {response.status} for {url}")
                    if response.status >= 500:
                        # Server error - retry
                        if attempt < MAX_RETRIES - 1:
                            await asyncio.sleep(RETRY_DELAY * (attempt + 1))
                            continue
                    return None
        except asyncio.TimeoutError:
            if SHOW_DEBUG_LOGS:
                print(f"⚠️ Timeout attempt {attempt+1}/{MAX_RETRIES} for {url}")
            if attempt < MAX_RETRIES - 1:
                await asyncio.sleep(RETRY_DELAY * (attempt + 1))
            else:
                return None
        except aiohttp.ClientError as e:
            if SHOW_DEBUG_LOGS:
                print(f"⚠️ Client error attempt {attempt+1}/{MAX_RETRIES} for {url}: {str(e)[:100]}")
            if attempt < MAX_RETRIES - 1:
                await asyncio.sleep(RETRY_DELAY * (attempt + 1))
            else:
                return None
        except Exception as e:
            if SHOW_DEBUG_LOGS:
                print(f"⚠️ Attempt {attempt+1}/{MAX_RETRIES} error: {str(e)[:100]}")
            if attempt < MAX_RETRIES - 1:
                await asyncio.sleep(RETRY_DELAY * (attempt + 1))
            else:
                return None
    return None

async def get_journal_by_issn(issn: str, session) -> Optional[Dict]:
    """Get journal information from OpenAlex by ISSN with timeout"""
    issn_clean = parse_issn(issn)
    if not issn_clean:
        return None
    
    url = "https://api.openalex.org/sources"
    params = {
        'filter': f'issn:{issn_clean}',
        'per-page': 1
    }
    
    try:
        data = await asyncio.wait_for(
            fetch_with_retry(session, url, params=params),
            timeout=30.0
        )
    except asyncio.TimeoutError:
        if SHOW_DEBUG_LOGS:
            print(f"⚠️ Timeout getting journal by ISSN: {issn_clean}")
        return None
    
    if not data:
        return None
    
    results = data.get('results', [])
    if not results:
        return None
    
    return results[0]

async def get_journal_publications(journal_id: str, session, periods: List[Tuple[int, int]], progress_callback=None, issn: str = None) -> List[Dict]:
    """Get all publications for a journal within specified periods with cursor support for large datasets"""
    if not journal_id:
        return []
    
    year_filters = []
    for start, end in periods:
        if start == end:
            year_filters.append(str(start))
        else:
            year_filters.append(f"{start}-{end}")
    
    year_filter = ','.join(year_filters)
    
    all_works = []
    url = "https://api.openalex.org/works"
    
    params = {
        'filter': f'primary_location.source.issn:{issn},publication_year:{year_filter}',
        'per-page': 200,
        'sort': 'publication_date:desc',
        'cursor': '*'
    }
    
    max_pages = 25  # Ограничение на количество страниц (25 * 200 = 5000 работ)
    page_count = 0
    
    while True:
        page_count += 1
        if page_count > max_pages:
            if SHOW_DEBUG_LOGS:
                print(f"⚠️ Reached max pages limit ({max_pages})")
            break
        
        try:
            data = await asyncio.wait_for(
                fetch_with_retry(session, url, params=params),
                timeout=45.0
            )
        except asyncio.TimeoutError:
            if SHOW_DEBUG_LOGS:
                print(f"⚠️ Timeout getting publications, page {page_count}")
            break
        
        if not data:
            break
        
        results = data.get('results', [])
        if not results:
            break
        
        all_works.extend(results)
        
        meta = data.get('meta', {})
        total_count = meta.get('count', 0)
        
        if progress_callback:
            progress_callback(len(all_works), total_count)
        
        next_cursor = meta.get('next_cursor')
        if not next_cursor:
            break
        
        params['cursor'] = next_cursor
        
        await asyncio.sleep(DELAY_BETWEEN_BATCHES)
    
    return all_works
    
async def get_work_citations(work_id: str, session, progress_callback=None) -> List[Dict]:
    """Get all citing works for a publication with timeout"""
    if not work_id:
        return []
    
    all_citations = []
    url = "https://api.openalex.org/works"
    params = {
        'filter': f'cites:{work_id}',
        'per-page': 200
    }
    
    page_count = 0
    max_citation_pages = 3  # 3 * 200 = 600 цитирований на работу
    
    while True:
        page_count += 1
        if page_count > max_citation_pages:
            if SHOW_DEBUG_LOGS:
                print(f"⚠️ Reached max citation pages limit ({max_citation_pages}) for {work_id}")
            break
        
        try:
            data = await asyncio.wait_for(
                fetch_with_retry(session, url, params=params),
                timeout=30.0
            )
        except asyncio.TimeoutError:
            if SHOW_DEBUG_LOGS:
                print(f"⚠️ Timeout getting citations for {work_id}")
            break
        
        if not data:
            break
        
        results = data.get('results', [])
        if not results:
            break
        
        all_citations.extend(results)
        
        if progress_callback:
            progress_callback(len(all_citations))
        
        meta = data.get('meta', {})
        next_url = meta.get('next_page_url')
        if not next_url:
            break
        
        url = next_url
        params = None
        
        await asyncio.sleep(DELAY_BETWEEN_BATCHES)
        
        if len(all_citations) >= MAX_CITATIONS_PER_PUBLICATION:
            break
    
    return all_citations

# ============================================
# DATA PARSING
# ============================================

def parse_author_from_openalex(auth_data: Dict) -> Author:
    """Parse author from OpenAlex data"""
    author_info = auth_data.get('author', {})
    display_name = author_info.get('display_name', '')
    orcid = author_info.get('orcid', '')
    
    affiliations = []
    countries = []
    
    for inst in auth_data.get('institutions', []):
        aff_name = inst.get('display_name', '')
        if aff_name:
            country_code = inst.get('country_code', '')
            country_names = {
                'US': 'USA', 'GB': 'UK', 'CN': 'China', 'DE': 'Germany',
                'FR': 'France', 'JP': 'Japan', 'CA': 'Canada', 'AU': 'Australia',
                'RU': 'Russia', 'IN': 'India', 'BR': 'Brazil', 'IT': 'Italy',
                'ES': 'Spain', 'KR': 'South Korea', 'NL': 'Netherlands',
                'CH': 'Switzerland', 'SE': 'Sweden', 'BE': 'Belgium',
                'NO': 'Norway', 'DK': 'Denmark', 'FI': 'Finland', 'PL': 'Poland',
                'PT': 'Portugal', 'GR': 'Greece', 'TR': 'Turkey', 'IL': 'Israel'
            }
            country_name = country_names.get(country_code, country_code)
            
            affiliations.append({
                'name': aff_name,
                'country': country_name
            })
            if country_name:
                countries.append(country_name)
    
    compare_name, display_name_norm = normalize_author_name(display_name)
    
    return Author(
        display_name=display_name_norm or display_name,
        compare_name=compare_name,
        orcid=clean_orcid(orcid),
        affiliations=affiliations,
        countries=list(set(countries))
    )

def parse_publication_from_openalex(item: Dict) -> Optional[Publication]:
    """Parse publication from OpenAlex data"""
    try:
        pub_id = item.get('id', '')
        doi = item.get('doi', '').replace('https://doi.org/', '')
        title = item.get('title', 'No title')
        publication_year = item.get('publication_year', 0)
        publication_date = item.get('publication_date', '')
        
        journal_name = ''
        publisher = ''
        primary_location = item.get('primary_location', {})
        if primary_location:
            source = primary_location.get('source', {})
            journal_name = source.get('display_name', '')
            publisher = source.get('publisher', '')
            if not publisher:
                publisher = source.get('host_organization_name', '')
            if not publisher and source.get('host_organization_lineage_names'):
                publisher = source['host_organization_lineage_names'][0] if source['host_organization_lineage_names'] else ''
        
        oa = item.get('open_access', {})
        is_oa = oa.get('is_oa', False)
        open_access_status = oa.get('oa_status', 'closed')
        
        authors = []
        affiliations = []
        countries = []
        
        for auth in item.get('authorships', []):
            author = parse_author_from_openalex(auth)
            authors.append(author)
            
            for aff in author.affiliations:
                if aff not in affiliations:
                    affiliations.append(aff)
                if aff.get('country') and aff['country'] not in countries:
                    countries.append(aff['country'])
        
        topics = []
        concepts = []
        fields = []
        domains = []
        
        for concept in item.get('concepts', []):
            concept_name = concept.get('display_name', '')
            concept_level = concept.get('level', 0)
            if concept_name:
                concepts.append(concept_name)
                if concept_level >= 3:
                    domains.append(concept_name)
                elif concept_level == 2:
                    fields.append(concept_name)
                elif concept_level == 1:
                    topics.append(Topic(
                        display_name=concept_name,
                        subfield='',
                        field='',
                        domain='',
                        score=concept.get('score', 0)
                    ))
        
        primary_topic = item.get('primary_topic', {})
        if primary_topic:
            topics.append(Topic(
                display_name=primary_topic.get('display_name', ''),
                subfield=primary_topic.get('subfield', {}).get('display_name', ''),
                field=primary_topic.get('field', {}).get('display_name', ''),
                domain=primary_topic.get('domain', {}).get('display_name', ''),
                score=primary_topic.get('score', 0)
            ))
        
        cited_by_count = item.get('cited_by_count', 0)
        
        is_retracted = item.get('is_retracted', False)
        is_correction = item.get('is_correction', False)
        
        current_year = datetime.now().year
        citations_per_year = 0
        if publication_year > 0:
            years_since = current_year - publication_year + 1
            citations_per_year = cited_by_count / max(years_since, 1)
        
        return Publication(
            id=pub_id,
            doi=doi,
            title=title,
            publication_year=publication_year,
            publication_date=publication_date,
            authors=authors,
            affiliations=affiliations,
            countries=list(set(countries)),
            journal_name=journal_name,
            publisher=publisher,
            cited_by_count=cited_by_count,
            is_oa=is_oa,
            open_access_status=open_access_status,
            topics=topics,
            concepts=list(set(concepts)),
            fields=list(set(fields)),
            domains=list(set(domains)),
            citations=[],
            citations_per_year=citations_per_year,
            is_retracted=is_retracted,
            is_correction=is_correction,
            citation_years={}
        )
    
    except Exception as e:
        if SHOW_DEBUG_LOGS:
            print(f"⚠️ Error parsing publication: {e}")
        return None

def parse_citation_from_openalex(item: Dict, publication_year: int = 0) -> Optional[Citation]:
    """Parse citation from OpenAlex data with citation lag calculation"""
    try:
        citing_id = item.get('id', '')
        citing_doi = item.get('doi', '').replace('https://doi.org/', '')
        citing_title = item.get('title', 'No title')
        citing_year = item.get('publication_year', 0)
        citing_date = item.get('publication_date', '')
        
        citation_lag = 0
        if publication_year > 0 and citing_year > 0:
            citation_lag = citing_year - publication_year
        
        citing_journal = ''
        citing_publisher = ''
        primary_location = item.get('primary_location', {})
        if primary_location:
            source = primary_location.get('source', {})
            citing_journal = source.get('display_name', '')
            citing_publisher = source.get('publisher', '')
            if not citing_publisher:
                citing_publisher = source.get('host_organization_name', '')
            if not citing_publisher and source.get('host_organization_lineage_names'):
                citing_publisher = source['host_organization_lineage_names'][0] if source['host_organization_lineage_names'] else ''
        
        citing_authors = []
        citing_affiliations = []
        citing_countries = []
        
        for auth in item.get('authorships', []):
            author = parse_author_from_openalex(auth)
            citing_authors.append(author)
            
            for aff in author.affiliations:
                if aff not in citing_affiliations:
                    citing_affiliations.append(aff)
                if aff.get('country') and aff['country'] not in citing_countries:
                    citing_countries.append(aff['country'])
        
        citing_topics = []
        citing_concepts = []
        citing_fields = []
        citing_domains = []
        
        for concept in item.get('concepts', []):
            concept_name = concept.get('display_name', '')
            concept_level = concept.get('level', 0)
            if concept_name:
                citing_concepts.append(concept_name)
                if concept_level >= 3:
                    citing_domains.append(concept_name)
                elif concept_level == 2:
                    citing_fields.append(concept_name)
                elif concept_level == 1:
                    citing_topics.append(Topic(
                        display_name=concept_name,
                        score=concept.get('score', 0)
                    ))
        
        primary_topic = item.get('primary_topic', {})
        if primary_topic:
            citing_topics.append(Topic(
                display_name=primary_topic.get('display_name', ''),
                subfield=primary_topic.get('subfield', {}).get('display_name', ''),
                field=primary_topic.get('field', {}).get('display_name', ''),
                domain=primary_topic.get('domain', {}).get('display_name', ''),
                score=primary_topic.get('score', 0)
            ))
        
        return Citation(
            citing_work_id=citing_id,
            citing_doi=citing_doi,
            citing_title=citing_title,
            citing_year=citing_year,
            citing_date=citing_date,
            citing_journal=citing_journal,
            citing_publisher=citing_publisher,
            citing_authors=citing_authors,
            citing_affiliations=citing_affiliations,
            citing_countries=list(set(citing_countries)),
            citing_topics=citing_topics,
            citing_concepts=list(set(citing_concepts)),
            citing_fields=list(set(citing_fields)),
            citing_domains=list(set(citing_domains)),
            citation_lag=citation_lag
        )
    
    except Exception as e:
        if SHOW_DEBUG_LOGS:
            print(f"⚠️ Error parsing citation: {e}")
        return None

# ============================================
# ENHANCED ANALYTICS ENGINE
# ============================================

class JournalAnalytics:
    def __init__(self, journal: Journal, publications: List[Publication], citations: Dict[str, List[Citation]]):
        self.journal = journal
        self.publications = publications
        self.citations = citations
        self.analytics = {}
        self._run_analysis()
    
    def _run_analysis(self):
        """Run all analytics"""
        self.analytics = {
            'publication_stats': self._get_publication_stats(),
            'citation_stats': self._get_citation_stats(),
            'author_stats': self._get_author_stats(),
            'affiliation_stats': self._get_affiliation_stats(),
            'country_stats': self._get_country_stats(),
            'topic_stats': self._get_topic_stats(),
            'citing_works_stats': self._get_citing_works_stats(),
            'temporal_stats': self._get_temporal_stats(),
            'most_cited': self._get_most_cited(),
            'citation_distribution': self._get_citation_distribution(),
            'citation_timeline': self._get_citation_timeline(),
            'citation_matrix': self._get_citation_matrix(),
            'topic_relationship': self._get_topic_relationship(),
            'detailed_citations': self._get_detailed_citations(),
        }
    
    def _get_publication_stats(self) -> Dict:
        """Get publication statistics"""
        pubs = self.publications
        total = len(pubs)
        
        if total == 0:
            return {'total': 0}
        
        years = [p.publication_year for p in pubs if p.publication_year > 0]
        year_counts = Counter(years)
        
        authors_per_paper = [len(p.authors) for p in pubs]
        oa_count = sum(1 for p in pubs if p.is_oa)
        retracted = sum(1 for p in pubs if p.is_retracted)
        
        affs_per_paper = [len(p.affiliations) for p in pubs]
        
        return {
            'total': total,
            'years': sorted(year_counts.keys()),
            'year_counts': dict(year_counts),
            'active_years': len(year_counts),
            'avg_authors_per_paper': np.mean(authors_per_paper) if authors_per_paper else 0,
            'median_authors_per_paper': np.median(authors_per_paper) if authors_per_paper else 0,
            'oa_count': oa_count,
            'oa_percentage': (oa_count / total * 100) if total > 0 else 0,
            'retracted': retracted,
            'retracted_percentage': (retracted / total * 100) if total > 0 else 0,
            'avg_affiliations_per_paper': np.mean(affs_per_paper) if affs_per_paper else 0,
        }
    
    def _get_citation_stats(self) -> Dict:
        """Get citation statistics"""
        pubs = self.publications
        
        if not pubs:
            return {'total': 0}
        
        citations = [p.cited_by_count for p in pubs]
        total_citations = sum(citations)
        
        sorted_citations = sorted([c for c in citations if c > 0], reverse=True)
        h_index = 0
        for i, c in enumerate(sorted_citations, 1):
            if c >= i:
                h_index = i
            else:
                break
        
        total_citations_sorted = 0
        g_index = 0
        for i, c in enumerate(sorted_citations, 1):
            total_citations_sorted += c
            if total_citations_sorted >= i**2:
                g_index = i
        
        i10_index = sum(1 for c in citations if c >= 10)
        i100_index = sum(1 for c in citations if c >= 100)
        
        current_year = datetime.now().year
        citations_per_year = []
        for p in pubs:
            if p.publication_year > 0:
                years_since = current_year - p.publication_year + 1
                citations_per_year.append(p.cited_by_count / max(years_since, 1))
        
        return {
            'total': total_citations,
            'avg': np.mean(citations) if citations else 0,
            'median': np.median(citations) if citations else 0,
            'max': max(citations) if citations else 0,
            'min': min(citations) if citations else 0,
            'h_index': h_index,
            'g_index': g_index,
            'i10_index': i10_index,
            'i100_index': i100_index,
            'avg_citations_per_year': np.mean(citations_per_year) if citations_per_year else 0,
            'total_citations_per_year': total_citations / max(len(citations), 1),
        }
    
    def _get_author_stats(self) -> Dict:
        """Get author statistics with collaboration patterns and countries"""
        author_data = {}
        
        for pub in self.publications:
            for author in pub.authors:
                key = author.compare_name
                if key not in author_data:
                    author_data[key] = {
                        'display_name': author.display_name,
                        'compare_name': author.compare_name,
                        'orcid': author.orcid,
                        'publications': 0,
                        'citations': 0,
                        'affiliations': [],
                        'countries': [],
                        'works': []
                    }
                
                author_data[key]['publications'] += 1
                author_data[key]['citations'] += pub.cited_by_count
                author_data[key]['works'].append(pub.doi)
                
                for aff in author.affiliations:
                    if aff not in author_data[key]['affiliations']:
                        author_data[key]['affiliations'].append(aff)
                
                for country in author.countries:
                    if country not in author_data[key]['countries']:
                        author_data[key]['countries'].append(country)
        
        author_list = []
        for key, data in author_data.items():
            citations_per_work = []
            for pub in self.publications:
                for author in pub.authors:
                    if author.compare_name == key:
                        citations_per_work.append(pub.cited_by_count)
                        break
            
            sorted_cites = sorted([c for c in citations_per_work if c > 0], reverse=True)
            h = 0
            for i, c in enumerate(sorted_cites, 1):
                if c >= i:
                    h = i
                else:
                    break
            
            data['h_index'] = h
            author_list.append(data)
        
        author_list.sort(key=lambda x: x['publications'], reverse=True)
        
        # Get collaboration patterns
        collaboration_patterns = self._get_collaboration_patterns()
        unique_countries_per_ref = self._get_unique_countries_per_reference()
        authors_per_country = self._get_authors_per_country()
        
        return {
            'total_authors': len(author_list),
            'top_authors': author_list[:20],
            'all_authors': author_list,
            'collaboration_patterns': collaboration_patterns,
            'unique_countries_per_reference': unique_countries_per_ref,
            'authors_per_country': authors_per_country,
        }
    
    def _get_collaboration_patterns(self) -> Dict:
        """Get collaboration patterns (country combinations)"""
        pattern_counter = Counter()
        
        for pub in self.publications:
            countries = sorted(set(pub.countries))
            if countries:
                key = '+'.join(countries)
                pattern_counter[key] += 1
        
        # Sort by count descending
        sorted_patterns = dict(pattern_counter.most_common())
        
        # Separate single-country and multi-country
        single_country = {}
        multi_country = {}
        
        for pattern, count in sorted_patterns.items():
            if '+' not in pattern:
                single_country[pattern] = count
            else:
                multi_country[pattern] = count
        
        return {
            'all_patterns': sorted_patterns,
            'single_country': single_country,
            'multi_country': multi_country,
            'total_collaborations': len(pattern_counter)
        }
    
    def _get_unique_countries_per_reference(self) -> Dict:
        """Get unique countries per reference (collaboration level)"""
        country_counter = Counter()
        
        for pub in self.publications:
            for country in set(pub.countries):
                if country:
                    country_counter[country] += 1
        
        return dict(country_counter.most_common())
    
    def _get_authors_per_country(self) -> Dict:
        """Get authors per country (individual distribution)"""
        country_counter = Counter()
        
        for pub in self.publications:
            for author in pub.authors:
                for country in author.countries:
                    if country:
                        country_counter[country] += 1
        
        return dict(country_counter.most_common())
    
    def _get_affiliation_stats(self) -> Dict:
        """Get affiliation statistics"""
        aff_data = {}
        
        for pub in self.publications:
            for aff in pub.affiliations:
                key = aff.get('name', '')
                if not key:
                    continue
                
                if key not in aff_data:
                    aff_data[key] = {
                        'name': key,
                        'country': aff.get('country', ''),
                        'publications': 0,
                        'citations': 0,
                        'authors': set()
                    }
                
                aff_data[key]['publications'] += 1
                aff_data[key]['citations'] += pub.cited_by_count
                
                for author in pub.authors:
                    for author_aff in author.affiliations:
                        if author_aff.get('name') == key:
                            aff_data[key]['authors'].add(author.compare_name)
        
        aff_list = []
        for key, data in aff_data.items():
            data['authors_count'] = len(data['authors'])
            aff_list.append(data)
        
        aff_list.sort(key=lambda x: x['publications'], reverse=True)
        
        return {
            'total_affiliations': len(aff_list),
            'top_affiliations': aff_list[:20],
            'all_affiliations': aff_list,
        }
    
    def _get_country_stats(self) -> Dict:
        """Get country statistics"""
        country_data = {}
        
        for pub in self.publications:
            for country in pub.countries:
                if not country:
                    continue
                
                if country not in country_data:
                    country_data[country] = {
                        'country': country,
                        'publications': 0,
                        'citations': 0,
                        'affiliations': set(),
                        'authors': set()
                    }
                
                country_data[country]['publications'] += 1
                country_data[country]['citations'] += pub.cited_by_count
                
                for aff in pub.affiliations:
                    if aff.get('country') == country:
                        country_data[country]['affiliations'].add(aff.get('name', ''))
                
                for author in pub.authors:
                    if country in author.countries:
                        country_data[country]['authors'].add(author.compare_name)
        
        country_list = []
        for key, data in country_data.items():
            data['affiliations_count'] = len(data['affiliations'])
            data['authors_count'] = len(data['authors'])
            country_list.append(data)
        
        country_list.sort(key=lambda x: x['publications'], reverse=True)
        
        return {
            'total_countries': len(country_list),
            'top_countries': country_list[:20],
            'all_countries': country_list,
        }
    
    def _get_topic_stats(self) -> Dict:
        """Get topic statistics"""
        topic_data = {}
        field_data = {}
        domain_data = {}
        concept_data = {}
        
        for pub in self.publications:
            for topic in pub.topics:
                key = topic.display_name
                if key:
                    if key not in topic_data:
                        topic_data[key] = {
                            'name': key,
                            'publications': 0,
                            'citations': 0,
                            'subfield': topic.subfield,
                            'field': topic.field,
                            'domain': topic.domain
                        }
                    topic_data[key]['publications'] += 1
                    topic_data[key]['citations'] += pub.cited_by_count
            
            for field in pub.fields:
                if field:
                    if field not in field_data:
                        field_data[field] = {'name': field, 'publications': 0, 'citations': 0}
                    field_data[field]['publications'] += 1
                    field_data[field]['citations'] += pub.cited_by_count
            
            for domain in pub.domains:
                if domain:
                    if domain not in domain_data:
                        domain_data[domain] = {'name': domain, 'publications': 0, 'citations': 0}
                    domain_data[domain]['publications'] += 1
                    domain_data[domain]['citations'] += pub.cited_by_count
            
            for concept in pub.concepts:
                if concept:
                    if concept not in concept_data:
                        concept_data[concept] = {'name': concept, 'publications': 0, 'citations': 0}
                    concept_data[concept]['publications'] += 1
                    concept_data[concept]['citations'] += pub.cited_by_count
        
        topic_list = list(topic_data.values())
        topic_list.sort(key=lambda x: x['publications'], reverse=True)
        
        field_list = list(field_data.values())
        field_list.sort(key=lambda x: x['publications'], reverse=True)
        
        domain_list = list(domain_data.values())
        domain_list.sort(key=lambda x: x['publications'], reverse=True)
        
        concept_list = list(concept_data.values())
        concept_list.sort(key=lambda x: x['publications'], reverse=True)
        
        return {
            'topics': topic_list[:20],
            'fields': field_list[:20],
            'domains': domain_list[:10],
            'concepts': concept_list[:30],
            'all_topics': topic_list,
            'all_fields': field_list,
            'all_domains': domain_list,
            'all_concepts': concept_list,
            'total_topics': len(topic_list),
            'total_fields': len(field_list),
            'total_domains': len(domain_list),
            'total_concepts': len(concept_list),
        }
    
    def _get_citing_works_stats(self) -> Dict:
        """Get detailed statistics about citing works with collaboration patterns"""
        all_citations = []
        for cites in self.citations.values():
            all_citations.extend(cites)
        
        if not all_citations:
            return {
                'total': 0,
                'top_journals': [],
                'top_publishers': [],
                'top_authors': [],
                'top_countries': [],
                'top_affiliations': [],
                'citation_lag': {},
                'citation_years': {},
                'unique_journals': 0,
                'unique_publishers': 0,
                'unique_authors': 0,
                'unique_countries': 0,
                'unique_affiliations': 0,
                'collaboration_patterns': {},
                'unique_countries_per_reference': {},
                'authors_per_country': {}
            }
        
        journal_counts = Counter()
        journal_citations = defaultdict(int)
        for c in all_citations:
            if c.citing_journal:
                journal_counts[c.citing_journal] += 1
                journal_citations[c.citing_journal] += 1
        
        publisher_counts = Counter()
        for c in all_citations:
            if c.citing_publisher:
                publisher_counts[c.citing_publisher] += 1
        
        author_counts = Counter()
        for c in all_citations:
            for author in c.citing_authors:
                if author.display_name:
                    author_counts[author.display_name] += 1
        
        country_counts = Counter()
        for c in all_citations:
            for country in c.citing_countries:
                if country:
                    country_counts[country] += 1
        
        aff_counts = Counter()
        for c in all_citations:
            for aff in c.citing_affiliations:
                if aff.get('name'):
                    aff_counts[aff['name']] += 1
        
        citation_lag = []
        citation_lag_by_year = defaultdict(list)
        
        for pub in self.publications:
            for cite in self.citations.get(pub.id, []):
                if pub.publication_year > 0 and cite.citing_year > 0:
                    lag = cite.citing_year - pub.publication_year
                    citation_lag.append(lag)
                    citation_lag_by_year[cite.citing_year].append(lag)
        
        citation_years = Counter()
        for c in all_citations:
            if c.citing_year > 0:
                citation_years[c.citing_year] += 1
        
        avg_lag_by_year = {}
        for year, lags in citation_lag_by_year.items():
            avg_lag_by_year[year] = np.mean(lags) if lags else 0
        
        # Collaboration patterns for citing works
        citing_collaboration_patterns = self._get_citing_collaboration_patterns(all_citations)
        citing_unique_countries_per_ref = self._get_citing_unique_countries_per_reference(all_citations)
        citing_authors_per_country = self._get_citing_authors_per_country(all_citations)
        
        return {
            'total': len(all_citations),
            'unique_journals': len(journal_counts),
            'unique_publishers': len(publisher_counts),
            'unique_authors': len(author_counts),
            'unique_countries': len(country_counts),
            'unique_affiliations': len(aff_counts),
            'top_journals': [{'name': k, 'count': v} for k, v in journal_counts.most_common(20)],
            'top_publishers': [{'name': k, 'count': v} for k, v in publisher_counts.most_common(20)],
            'top_authors': [{'name': k, 'count': v} for k, v in author_counts.most_common(20)],
            'top_countries': [{'name': k, 'count': v} for k, v in country_counts.most_common(20)],
            'top_affiliations': [{'name': k, 'count': v} for k, v in aff_counts.most_common(20)],
            'citation_lag': {
                'avg': np.mean(citation_lag) if citation_lag else 0,
                'median': np.median(citation_lag) if citation_lag else 0,
                'max': max(citation_lag) if citation_lag else 0,
                'min': min(citation_lag) if citation_lag else 0,
                'distribution': dict(Counter(citation_lag)),
                'by_year': avg_lag_by_year
            },
            'citation_years': dict(citation_years),
            'all_citations': all_citations,
            'collaboration_patterns': citing_collaboration_patterns,
            'unique_countries_per_reference': citing_unique_countries_per_ref,
            'authors_per_country': citing_authors_per_country
        }
    
    def _get_citing_collaboration_patterns(self, citations: List[Citation]) -> Dict:
        """Get collaboration patterns for citing works"""
        pattern_counter = Counter()
        
        for cite in citations:
            countries = sorted(set(cite.citing_countries))
            if countries:
                key = '+'.join(countries)
                pattern_counter[key] += 1
        
        sorted_patterns = dict(pattern_counter.most_common())
        
        single_country = {}
        multi_country = {}
        
        for pattern, count in sorted_patterns.items():
            if '+' not in pattern:
                single_country[pattern] = count
            else:
                multi_country[pattern] = count
        
        return {
            'all_patterns': sorted_patterns,
            'single_country': single_country,
            'multi_country': multi_country,
            'total_collaborations': len(pattern_counter)
        }
    
    def _get_citing_unique_countries_per_reference(self, citations: List[Citation]) -> Dict:
        """Get unique countries per citing reference"""
        country_counter = Counter()
        
        for cite in citations:
            for country in set(cite.citing_countries):
                if country:
                    country_counter[country] += 1
        
        return dict(country_counter.most_common())
    
    def _get_citing_authors_per_country(self, citations: List[Citation]) -> Dict:
        """Get authors per country for citing works"""
        country_counter = Counter()
        
        for cite in citations:
            for author in cite.citing_authors:
                for country in author.countries:
                    if country:
                        country_counter[country] += 1
        
        return dict(country_counter.most_common())
    
    def _get_temporal_stats(self) -> Dict:
        """Get temporal statistics"""
        pubs = self.publications
        
        if not pubs:
            return {}
        
        years = [p.publication_year for p in pubs if p.publication_year > 0]
        year_counts = Counter(years)
        
        citation_by_year = defaultdict(int)
        for p in pubs:
            if p.publication_year > 0:
                citation_by_year[p.publication_year] += p.cited_by_count
        
        return {
            'year_counts': dict(year_counts),
            'citations_by_year': dict(citation_by_year),
            'min_year': min(years) if years else 0,
            'max_year': max(years) if years else 0,
            'active_years': len(years),
            'total_years': max(years) - min(years) + 1 if years else 0,
        }
    
    def _get_most_cited(self) -> List[Dict]:
        """Get most cited publications with detailed info"""
        sorted_pubs = sorted(self.publications, key=lambda x: x.cited_by_count, reverse=True)
        return [
            {
                'title': p.title,
                'citations': p.cited_by_count,
                'year': p.publication_year,
                'journal': p.journal_name,
                'doi': p.doi,
                'authors': [a.display_name for a in p.authors],
                'citations_per_year': p.citations_per_year,
                'citation_years': p.citation_years
            }
            for p in sorted_pubs[:20]
        ]
    
    def _get_citation_distribution(self) -> Dict:
        """Get citation distribution"""
        citations = [p.cited_by_count for p in self.publications]
        
        if not citations:
            return {}
        
        bins = [0, 1, 5, 10, 20, 50, 100, 500, 1000]
        distribution = {}
        for i in range(len(bins) - 1):
            lower = bins[i]
            upper = bins[i + 1]
            key = f"{lower}-{upper}"
            distribution[key] = sum(1 for c in citations if lower <= c < upper)
        distribution[f">{bins[-1]}"] = sum(1 for c in citations if c >= bins[-1])
        
        return distribution
    
    def _get_citation_timeline(self) -> Dict:
        """Get citation timeline for each publication"""
        timeline = {}
        
        for pub in self.publications:
            if pub.id in self.citations:
                year_counts = Counter()
                for cite in self.citations[pub.id]:
                    if cite.citing_year > 0:
                        year_counts[cite.citing_year] += 1
                
                timeline[pub.id] = {
                    'title': pub.title,
                    'year': pub.publication_year,
                    'total_citations': pub.cited_by_count,
                    'citations_by_year': dict(year_counts),
                    'doi': pub.doi
                }
        
        return timeline
    
    def _get_citation_matrix(self) -> Dict:
        """Get citation matrix (publication_year → citation_year → count)"""
        matrix = defaultdict(lambda: defaultdict(int))
        
        for pub in self.publications:
            if pub.publication_year > 0 and pub.id in self.citations:
                for cite in self.citations[pub.id]:
                    if cite.citing_year > 0:
                        matrix[pub.publication_year][cite.citing_year] += 1
        
        # Convert to sorted dict
        sorted_matrix = {}
        for pub_year in sorted(matrix.keys()):
            sorted_matrix[pub_year] = dict(sorted(matrix[pub_year].items()))
        
        return sorted_matrix
    
    def _get_topic_relationship(self) -> Dict:
        """Analyze relationship between publication topics and citing topics"""
        pub_topics = Counter()
        for pub in self.publications:
            for topic in pub.topics:
                if topic.display_name:
                    pub_topics[topic.display_name] += 1
        
        citing_topics = Counter()
        for cites in self.citations.values():
            for cite in cites:
                for topic in cite.citing_topics:
                    if topic.display_name:
                        citing_topics[topic.display_name] += 1
        
        pub_topic_set = set(pub_topics.keys())
        citing_topic_set = set(citing_topics.keys())
        overlap = pub_topic_set & citing_topic_set
        
        hot_topics = {}
        for topic in pub_topic_set:
            pub_count = pub_topics[topic]
            cite_count = citing_topics.get(topic, 0)
            if pub_count > 0:
                ratio = cite_count / pub_count
                if ratio > 1.0:
                    hot_topics[topic] = {
                        'publications': pub_count,
                        'citations': cite_count,
                        'ratio': ratio,
                        'hot_index': ratio * cite_count
                    }
        
        # Sort by ratio descending
        hot_topics_sorted = dict(sorted(hot_topics.items(), key=lambda x: x[1]['ratio'], reverse=True))
        
        return {
            'publication_topics': dict(pub_topics.most_common(30)),
            'citing_topics': dict(citing_topics.most_common(30)),
            'overlap_topics': list(overlap),
            'overlap_percentage': (len(overlap) / max(len(pub_topic_set), 1) * 100) if pub_topic_set else 0,
            'hot_topics': hot_topics_sorted,
            'total_pub_topics': len(pub_topic_set),
            'total_citing_topics': len(citing_topic_set),
        }
    
    def _get_detailed_citations(self) -> Dict:
        """Get detailed citations for each publication"""
        detailed = {}
        
        for pub in self.publications:
            if pub.id in self.citations and self.citations[pub.id]:
                citations_list = []
                for cite in self.citations[pub.id]:
                    citations_list.append({
                        'citing_title': cite.citing_title,
                        'citing_year': cite.citing_year,
                        'citing_date': cite.citing_date,
                        'citing_journal': cite.citing_journal,
                        'citing_publisher': cite.citing_publisher,
                        'citing_doi': cite.citing_doi,
                        'citation_lag': cite.citation_lag,
                        'citing_authors': [a.display_name for a in cite.citing_authors],
                        'citing_countries': cite.citing_countries,
                        'citing_topics': [t.display_name for t in cite.citing_topics]
                    })
                
                detailed[pub.id] = {
                    'title': pub.title,
                    'year': pub.publication_year,
                    'doi': pub.doi,
                    'total_citations': len(citations_list),
                    'citations': citations_list
                }
        
        return detailed
    
    def get_analytics(self) -> Dict:
        """Get all analytics"""
        return self.analytics

# ============================================
# ADVANCED VISUALIZATION FUNCTIONS
# ============================================

def create_advanced_visualizations(analytics: Dict, lang: str = 'en') -> Dict[str, str]:
    """Create advanced visualizations for the report"""
    images = {}
    
    def t(key: str, **kwargs) -> str:
        return translate(key, lang, **kwargs)
    
    # Publication dynamics
    publication_stats = analytics.get('publication_stats', {})
    if publication_stats and publication_stats.get('year_counts'):
        fig, ax = plt.subplots(figsize=(10, 5))
        years = sorted(publication_stats['year_counts'].keys())
        counts = [publication_stats['year_counts'][y] for y in years]
        
        bars = ax.bar(years, counts, color='#2E86AB', alpha=0.7, edgecolor='black', linewidth=1.0)
        
        for bar, count in zip(bars, counts):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.3,
                   f'{count}', ha='center', va='bottom', fontsize=9)
        
        ax.set_xlabel(t('publication_year'), fontsize=11, fontweight='bold')
        ax.set_ylabel(t('number'), fontsize=11, fontweight='bold')
        ax.set_title(t('publication_dynamics'), fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        
        if len(years) >= 3:
            x = np.arange(len(years))
            z = np.polyfit(x, counts, 1)
            p = np.poly1d(z)
            ax.plot(years, p(x), 'r-', linewidth=2, alpha=0.8, label='Trend')
            ax.legend(loc='upper left')
        
        plt.tight_layout()
        
        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        buf.seek(0)
        images['publication_dynamics'] = base64.b64encode(buf.getvalue()).decode()
        plt.close()
    
    # Citation distribution
    citation_dist = analytics.get('citation_distribution', {})
    if citation_dist:
        fig, ax = plt.subplots(figsize=(10, 5))
        
        ranges = list(citation_dist.keys())
        counts = list(citation_dist.values())
        
        bars = ax.bar(range(len(ranges)), counts, color='#A23B72', alpha=0.8, edgecolor='black', linewidth=1.0)
        
        for bar, count in zip(bars, counts):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.3,
                   f'{count}', ha='center', va='bottom', fontsize=9)
        
        ax.set_xticks(range(len(ranges)))
        ax.set_xticklabels(ranges, rotation=45, ha='right', fontsize=9)
        ax.set_xlabel(t('citations'), fontsize=11, fontweight='bold')
        ax.set_ylabel(t('number'), fontsize=11, fontweight='bold')
        ax.set_title('Citation Distribution', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        
        plt.tight_layout()
        
        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        buf.seek(0)
        images['citation_distribution'] = base64.b64encode(buf.getvalue()).decode()
        plt.close()
    
    # Top authors
    author_stats = analytics.get('author_stats', {})
    top_authors = author_stats.get('top_authors', [])
    if top_authors:
        fig, ax = plt.subplots(figsize=(10, 5))
        
        names = [a['display_name'][:30] for a in top_authors[:10]]
        pubs = [a['publications'] for a in top_authors[:10]]
        
        bars = ax.barh(range(len(names)), pubs, color='#F18F01', alpha=0.8, edgecolor='black', linewidth=1.0)
        
        for bar, count in zip(bars, pubs):
            ax.text(count + 0.3, bar.get_y() + bar.get_height()/2,
                   f'{count}', va='center', fontsize=9)
        
        ax.set_yticks(range(len(names)))
        ax.set_yticklabels(names, fontsize=9)
        ax.invert_yaxis()
        ax.set_xlabel(t('publications'), fontsize=11, fontweight='bold')
        ax.set_title('Top Authors', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3, linestyle='--', axis='x')
        
        plt.tight_layout()
        
        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        buf.seek(0)
        images['top_authors'] = base64.b64encode(buf.getvalue()).decode()
        plt.close()
    
    # Top countries
    country_stats = analytics.get('country_stats', {})
    top_countries = country_stats.get('top_countries', [])
    if top_countries:
        fig, ax = plt.subplots(figsize=(10, 5))
        
        names = [c['country'][:20] for c in top_countries[:10]]
        pubs = [c['publications'] for c in top_countries[:10]]
        
        bars = ax.barh(range(len(names)), pubs, color='#3498DB', alpha=0.8, edgecolor='black', linewidth=1.0)
        
        for bar, count in zip(bars, pubs):
            ax.text(count + 0.3, bar.get_y() + bar.get_height()/2,
                   f'{count}', va='center', fontsize=9)
        
        ax.set_yticks(range(len(names)))
        ax.set_yticklabels(names, fontsize=9)
        ax.invert_yaxis()
        ax.set_xlabel(t('publications'), fontsize=11, fontweight='bold')
        ax.set_title('Top Countries', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3, linestyle='--', axis='x')
        
        plt.tight_layout()
        
        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        buf.seek(0)
        images['top_countries'] = base64.b64encode(buf.getvalue()).decode()
        plt.close()
    
    # Citation timeline (citations per year)
    citation_timeline = analytics.get('citation_timeline', {})
    if citation_timeline:
        all_years = Counter()
        for data in citation_timeline.values():
            for year, count in data.get('citations_by_year', {}).items():
                all_years[year] += count
        
        if all_years:
            fig, ax = plt.subplots(figsize=(10, 5))
            years = sorted(all_years.keys())
            counts = [all_years[y] for y in years]
            
            ax.plot(years, counts, 'o-', color='#2E86AB', linewidth=2, markersize=8)
            ax.fill_between(years, counts, alpha=0.3, color='#2E86AB')
            
            ax.set_xlabel('Year', fontsize=11, fontweight='bold')
            ax.set_ylabel('Citations Received', fontsize=11, fontweight='bold')
            ax.set_title('Aggregated Citation Timeline', fontsize=12, fontweight='bold')
            ax.grid(True, alpha=0.3, linestyle='--')
            
            plt.tight_layout()
            
            buf = BytesIO()
            plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
            buf.seek(0)
            images['citation_timeline'] = base64.b64encode(buf.getvalue()).decode()
            plt.close()
    
    # Citation Matrix Heatmap
    citation_matrix = analytics.get('citation_matrix', {})
    if citation_matrix:
        pub_years = sorted(citation_matrix.keys())
        all_cite_years = set()
        for years in citation_matrix.values():
            all_cite_years.update(years.keys())
        cite_years = sorted(all_cite_years)
        
        if pub_years and cite_years:
            matrix_data = []
            for pub_year in pub_years:
                row = []
                for cite_year in cite_years:
                    row.append(citation_matrix[pub_year].get(cite_year, 0))
                matrix_data.append(row)
            
            fig, ax = plt.subplots(figsize=(12, 8))
            im = ax.imshow(matrix_data, cmap='YlOrRd', aspect='auto')
            
            ax.set_xticks(range(len(cite_years)))
            ax.set_yticks(range(len(pub_years)))
            ax.set_xticklabels(cite_years, rotation=45, ha='right', fontsize=9)
            ax.set_yticklabels(pub_years, fontsize=9)
            ax.set_xlabel('Citation Year', fontsize=11, fontweight='bold')
            ax.set_ylabel('Publication Year', fontsize=11, fontweight='bold')
            ax.set_title(t('citation_matrix'), fontsize=12, fontweight='bold')
            
            plt.colorbar(im, ax=ax, label='Citations Count')
            
            plt.tight_layout()
            
            buf = BytesIO()
            plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
            buf.seek(0)
            images['citation_matrix'] = base64.b64encode(buf.getvalue()).decode()
            plt.close()
    
    # Hot topics bubble chart
    hot_topics = analytics.get('topic_relationship', {}).get('hot_topics', {})
    if hot_topics:
        fig, ax = plt.subplots(figsize=(10, 6))
        
        names = []
        sizes = []
        colors = []
        ratios = []
        
        for topic, data in list(hot_topics.items())[:10]:
            names.append(topic[:30])
            sizes.append(data['hot_index'])
            ratios.append(data['ratio'])
            colors.append(data['ratio'] / max(d['ratio'] for d in hot_topics.values()) if hot_topics else 1)
        
        if names:
            scatter = ax.scatter(range(len(names)), sizes, s=[s * 20 for s in sizes], 
                               c=colors, cmap='RdYlGn', alpha=0.6, edgecolors='black', linewidth=1)
            
            ax.set_xticks(range(len(names)))
            ax.set_xticklabels(names, rotation=45, ha='right', fontsize=9)
            ax.set_ylabel('Hot Topic Index', fontsize=11, fontweight='bold')
            ax.set_title('Hot Topics (Citation Impact)', fontsize=12, fontweight='bold')
            ax.grid(True, alpha=0.3, linestyle='--')
            
            plt.tight_layout()
            
            buf = BytesIO()
            plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
            buf.seek(0)
            images['hot_topics'] = base64.b64encode(buf.getvalue()).decode()
            plt.close()
    
    # Top citing journals
    citing_stats = analytics.get('citing_works_stats', {})
    top_journals = citing_stats.get('top_journals', [])
    if top_journals:
        fig, ax = plt.subplots(figsize=(10, 5))
        
        names = [j['name'][:25] for j in top_journals[:10]]
        counts = [j['count'] for j in top_journals[:10]]
        
        bars = ax.barh(range(len(names)), counts, color='#8E44AD', alpha=0.8, edgecolor='black', linewidth=1.0)
        
        for bar, count in zip(bars, counts):
            ax.text(count + 0.3, bar.get_y() + bar.get_height()/2,
                   f'{count}', va='center', fontsize=9)
        
        ax.set_yticks(range(len(names)))
        ax.set_yticklabels(names, fontsize=9)
        ax.invert_yaxis()
        ax.set_xlabel('Citations', fontsize=11, fontweight='bold')
        ax.set_title('Top Citing Journals', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3, linestyle='--', axis='x')
        
        plt.tight_layout()
        
        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        buf.seek(0)
        images['top_citing_journals'] = base64.b64encode(buf.getvalue()).decode()
        plt.close()
    
    # Top citing countries
    top_countries = citing_stats.get('top_countries', [])
    if top_countries:
        fig, ax = plt.subplots(figsize=(10, 5))
        
        names = [c['name'][:20] for c in top_countries[:10]]
        counts = [c['count'] for c in top_countries[:10]]
        
        bars = ax.barh(range(len(names)), counts, color='#1ABC9C', alpha=0.8, edgecolor='black', linewidth=1.0)
        
        for bar, count in zip(bars, counts):
            ax.text(count + 0.3, bar.get_y() + bar.get_height()/2,
                   f'{count}', va='center', fontsize=9)
        
        ax.set_yticks(range(len(names)))
        ax.set_yticklabels(names, fontsize=9)
        ax.invert_yaxis()
        ax.set_xlabel('Citations', fontsize=11, fontweight='bold')
        ax.set_title('Top Citing Countries', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3, linestyle='--', axis='x')
        
        plt.tight_layout()
        
        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        buf.seek(0)
        images['top_citing_countries'] = base64.b64encode(buf.getvalue()).decode()
        plt.close()
    
    # Top citing publishers
    top_publishers = citing_stats.get('top_publishers', [])
    if top_publishers:
        fig, ax = plt.subplots(figsize=(10, 5))
        
        names = [p['name'][:25] for p in top_publishers[:10]]
        counts = [p['count'] for p in top_publishers[:10]]
        
        bars = ax.barh(range(len(names)), counts, color='#E74C3C', alpha=0.8, edgecolor='black', linewidth=1.0)
        
        for bar, count in zip(bars, counts):
            ax.text(count + 0.3, bar.get_y() + bar.get_height()/2,
                   f'{count}', va='center', fontsize=9)
        
        ax.set_yticks(range(len(names)))
        ax.set_yticklabels(names, fontsize=9)
        ax.invert_yaxis()
        ax.set_xlabel('Citations', fontsize=11, fontweight='bold')
        ax.set_title('Top Citing Publishers', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3, linestyle='--', axis='x')
        
        plt.tight_layout()
        
        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        buf.seek(0)
        images['top_citing_publishers'] = base64.b64encode(buf.getvalue()).decode()
        plt.close()
    
    return images

# ============================================
# ENHANCED HTML REPORT GENERATOR
# ============================================

def generate_enhanced_html_report(journal: Journal, analytics: Dict, periods: List[Tuple[int, int]], 
                                   images: Dict[str, str], theme_colors: Dict, lang: str = 'en',
                                   all_publications: List[Publication] = None) -> str:
    """Generate enhanced HTML report with all features"""
    
    def t(key: str, **kwargs) -> str:
        return translate(key, lang, **kwargs)
    
    primary = theme_colors.get('primary', '#667eea')
    secondary = theme_colors.get('secondary', '#f39c12')
    
    period_strs = []
    for start, end in periods:
        if start == end:
            period_strs.append(str(start))
        else:
            period_strs.append(f"{start}-{end}")
    period_display = ', '.join(period_strs)
    
    pub_stats = analytics.get('publication_stats', {})
    cit_stats = analytics.get('citation_stats', {})
    author_stats = analytics.get('author_stats', {})
    country_stats = analytics.get('country_stats', {})
    topic_stats = analytics.get('topic_stats', {})
    citing_stats = analytics.get('citing_works_stats', {})
    most_cited = analytics.get('most_cited', [])
    topic_rel = analytics.get('topic_relationship', {})
    detailed_citations = analytics.get('detailed_citations', {})
    citation_timeline = analytics.get('citation_timeline', {})
    citation_matrix = analytics.get('citation_matrix', {})
    affiliation_stats = analytics.get('affiliation_stats', {})
    
    # Build sidebar navigation
    sidebar_items = [
        ('executive_summary', t('executive_summary')),
        ('publication_dynamics', t('publication_dynamics')),
        ('citation_timeline', t('citation_timeline')),
        ('most_cited', t('most_cited_publications')),
        ('author_analysis', t('author_analysis')),
        ('affiliation_analysis', t('affiliation_analysis')),
        ('citation_analysis', t('citation_analysis')),
        ('citing_works_analysis', t('citing_works_analysis')),
        ('topic_analysis', t('topic_analysis')),
        ('topic_relationship', t('topic_relationship')),
        ('detailed_citations', t('detailed_citations')),
        ('all_publications', t('all_publications')),
    ]
    
    sidebar_html = '<div class="sidebar">\n'
    sidebar_html += f'<h3>{t("navigation")}</h3>\n'
    for item_id, title_text in sidebar_items:
        sidebar_html += f'<a href="#{item_id}"><span>{title_text}</span></a>\n'
    sidebar_html += '</div>\n'
    
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Journal Analytics - {journal.title}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Times New Roman', 'DejaVu Serif', serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            color: #333;
        }}
        .sidebar {{
            position: fixed;
            left: 0;
            top: 0;
            width: 240px;
            height: 100vh;
            background: linear-gradient(180deg, {primary} 0%, {secondary} 100%);
            padding: 20px 10px;
            overflow-y: auto;
            z-index: 1000;
        }}
        .sidebar h3 {{
            color: white;
            text-align: center;
            font-size: 16px;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid rgba(255,255,255,0.3);
        }}
        .sidebar a {{
            display: block;
            color: white;
            text-decoration: none;
            padding: 8px 12px;
            border-radius: 8px;
            margin: 3px 0;
            font-size: 13px;
            transition: background 0.3s;
            opacity: 0.85;
        }}
        .sidebar a:hover {{
            background: rgba(255,255,255,0.2);
            opacity: 1;
        }}
        .sidebar a span {{
            display: inline-block;
        }}
        .report-wrapper {{
            max-width: 1400px;
            margin: 0 auto;
            margin-left: 260px;
            background: white;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            border-radius: 10px;
            overflow: hidden;
        }}
        .main-content {{
            padding: 30px 40px;
        }}
        .header {{
            background: linear-gradient(135deg, {primary} 0%, {secondary} 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        .header h1 {{
            color: white;
            font-size: 32px;
            margin: 0;
        }}
        .header .subtitle {{
            opacity: 0.9;
            margin-top: 10px;
            font-size: 16px;
        }}
        .header .date {{
            opacity: 0.8;
            margin-top: 8px;
            font-size: 14px;
        }}
        .section {{
            background: white;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 25px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .section-title {{
            font-size: 24px;
            font-weight: 600;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid {primary};
        }}
        .section-title .icon {{
            font-size: 28px;
            margin-right: 10px;
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        .metric-card {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid {primary};
            text-align: center;
            transition: transform 0.3s;
        }}
        .metric-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }}
        .metric-value {{
            font-size: 28px;
            font-weight: bold;
            color: #2C3E50;
        }}
        .metric-label {{
            font-size: 12px;
            color: #7F8C8D;
            margin-top: 5px;
        }}
        .chart-container {{
            margin: 20px 0;
            text-align: center;
        }}
        .chart-container img {{
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .two-column {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }}
        .three-column {{
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 15px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
            font-size: 14px;
        }}
        th {{
            background: linear-gradient(135deg, {primary} 0%, {secondary} 100%);
            color: white;
            padding: 12px;
            text-align: left;
        }}
        td {{
            padding: 10px;
            border-bottom: 1px solid #BDC3C7;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        .doi-link {{
            color: #2980B9;
            text-decoration: none;
            font-size: 12px;
        }}
        .doi-link:hover {{
            text-decoration: underline;
        }}
        .rank-item {{
            border-radius: 10px;
            padding: 12px;
            margin-bottom: 8px;
            transition: all 0.3s;
            background: #f8f9fa;
            border-left: 3px solid {primary};
        }}
        .rank-item:hover {{
            transform: translateX(5px);
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .rank-number {{
            font-weight: bold;
            color: {primary};
            font-size: 18px;
            display: inline-block;
            width: 40px;
        }}
        .rank-name {{
            display: inline-block;
            font-weight: 500;
        }}
        .rank-count {{
            float: right;
            color: #666;
        }}
        .progress-bar {{
            background: #e0e0e0;
            border-radius: 10px;
            height: 6px;
            margin-top: 6px;
            overflow: hidden;
        }}
        .progress-fill {{
            background: linear-gradient(90deg, {primary}, {secondary});
            height: 100%;
            border-radius: 10px;
            transition: width 0.5s;
        }}
        .badge {{
            display: inline-block;
            padding: 3px 10px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            margin: 2px;
        }}
        .badge-success {{ background: #d4edda; color: #155724; }}
        .badge-warning {{ background: #fff3cd; color: #856404; }}
        .badge-info {{ background: #d1ecf1; color: #0c5460; }}
        .badge-danger {{ background: #f8d7da; color: #721c24; }}
        .badge-hot {{ background: #ff6b6b; color: white; }}
        .badge-cold {{ background: #74b9ff; color: white; }}
        
        .collapser {{
            cursor: pointer;
            padding: 10px 15px;
            background: #f8f9fa;
            border: 1px solid #ddd;
            border-radius: 8px;
            margin: 5px 0;
            transition: background 0.3s;
        }}
        .collapser:hover {{
            background: #e9ecef;
        }}
        .collapser-content {{
            padding: 10px 15px;
            border: 1px solid #ddd;
            border-top: none;
            border-radius: 0 0 8px 8px;
            margin-bottom: 10px;
        }}
        .collapser .badge {{
            margin-left: 10px;
        }}
        
        .filter-section {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            border: 1px solid #ddd;
        }}
        .filter-row {{
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
            align-items: center;
        }}
        .filter-row input, .filter-row select {{
            padding: 8px 12px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 13px;
        }}
        .filter-row label {{
            font-weight: 500;
            font-size: 13px;
        }}
        
        .citation-detail {{
            background: #f8f9fa;
            padding: 10px 15px;
            margin: 5px 0;
            border-radius: 5px;
            border-left: 3px solid {primary};
        }}
        .citation-detail .cite-meta {{
            font-size: 12px;
            color: #666;
            margin-top: 3px;
        }}
        
        .hot-topic {{
            background: linear-gradient(135deg, #fff5f5 0%, #ffe8e8 100%);
            border-left: 3px solid #ff6b6b;
        }}
        
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #BDC3C7;
            text-align: center;
            color: #7F8C8D;
            font-size: 12px;
        }}
        .footer a {{
            color: {primary};
            text-decoration: none;
        }}
        .footer a:hover {{
            text-decoration: underline;
        }}
        
        @media (max-width: 768px) {{
            .sidebar {{
                display: none;
            }}
            .report-wrapper {{
                margin-left: 0;
            }}
            .two-column, .three-column {{ grid-template-columns: 1fr; }}
            .metrics-grid {{ grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); }}
            .main-content {{ padding: 20px; }}
            .header {{ padding: 25px; }}
            .filter-row {{ flex-direction: column; align-items: stretch; }}
        }}
        
        .highlight {{
            background-color: #ffeb3b;
            padding: 0 2px;
        }}
        
        .citation-count {{
            display: inline-block;
            padding: 2px 10px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            background: {primary}20;
            color: {primary};
        }}
        
        .word-wrap {{
            word-wrap: break-word;
            word-break: break-word;
        }}
    </style>
    <script>
        function filterPublications() {{
            const yearFilter = document.getElementById('yearFilter').value;
            const authorFilter = document.getElementById('authorFilter').value.toLowerCase();
            const citationFilter = parseInt(document.getElementById('citationFilter').value) || 0;
            const searchTerm = document.getElementById('searchInput').value.toLowerCase();
            
            const rows = document.querySelectorAll('#publicationsTable tbody tr');
            let visibleCount = 0;
            
            rows.forEach(row => {{
                const year = parseInt(row.dataset.year) || 0;
                const authors = row.dataset.authors.toLowerCase();
                const citations = parseInt(row.dataset.citations) || 0;
                const title = row.dataset.title.toLowerCase();
                const doi = row.dataset.doi.toLowerCase();
                
                let visible = true;
                
                if (yearFilter && year != yearFilter) visible = false;
                if (authorFilter && !authors.includes(authorFilter)) visible = false;
                if (citations < citationFilter) visible = false;
                if (searchTerm && !title.includes(searchTerm) && !doi.includes(searchTerm) && !authors.includes(searchTerm)) visible = false;
                
                row.style.display = visible ? '' : 'none';
                if (visible) visibleCount++;
            }});
            
            document.getElementById('visibleCount').textContent = visibleCount + ' publications visible';
        }}
        
        function toggleCitations(id) {{
            const element = document.getElementById('citations_' + id);
            if (element) {{
                if (element.style.display === 'none' || element.style.display === '') {{
                    element.style.display = 'block';
                }} else {{
                    element.style.display = 'none';
                }}
            }}
        }}
        
        function sortTable(n) {{
            const table = document.getElementById('publicationsTable');
            let rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;
            switching = true;
            dir = "asc";
            
            while (switching) {{
                switching = false;
                rows = table.rows;
                
                for (i = 1; i < (rows.length - 1); i++) {{
                    shouldSwitch = false;
                    x = rows[i].getElementsByTagName("TD")[n];
                    y = rows[i + 1].getElementsByTagName("TD")[n];
                    
                    if (dir == "asc") {{
                        if (x.innerHTML.toLowerCase() > y.innerHTML.toLowerCase()) {{
                            shouldSwitch = true;
                            break;
                        }}
                    }} else if (dir == "desc") {{
                        if (x.innerHTML.toLowerCase() < y.innerHTML.toLowerCase()) {{
                            shouldSwitch = true;
                            break;
                        }}
                    }}
                }}
                
                if (shouldSwitch) {{
                    rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
                    switching = true;
                    switchcount++;
                }} else {{
                    if (switchcount == 0 && dir == "asc") {{
                        dir = "desc";
                        switching = true;
                    }}
                }}
            }}
        }}
    </script>
</head>
<body>
    {sidebar_html}
    
    <div class="report-wrapper">
        <div class="header">
            <h1>📊 Journal Analytics Report</h1>
            <div class="subtitle">{journal.title}</div>
            <div class="date">ISSN: {journal.issn} | Publisher: {journal.publisher} | Period: {period_display}</div>
            <div class="date">Generated: {datetime.now().strftime('%d.%m.%Y')}</div>
        </div>
        
        <div class="main-content">
            <!-- Executive Summary -->
            <div id="executive_summary" class="section">
                <div class="section-title"><span class="icon">📊</span> {t('executive_summary')}</div>
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-value">{pub_stats.get('total', 0)}</div>
                        <div class="metric-label">{t('total_publications')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{cit_stats.get('total', 0):,}</div>
                        <div class="metric-label">{t('total_citations')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{cit_stats.get('h_index', 0)}</div>
                        <div class="metric-label">{t('h_index')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{cit_stats.get('g_index', 0)}</div>
                        <div class="metric-label">{t('g_index')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{cit_stats.get('i10_index', 0)}</div>
                        <div class="metric-label">{t('i10_index')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{cit_stats.get('i100_index', 0)}</div>
                        <div class="metric-label">{t('i100_index')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{cit_stats.get('avg', 0):.1f}</div>
                        <div class="metric-label">{t('avg_citations')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{pub_stats.get('oa_percentage', 0):.1f}%</div>
                        <div class="metric-label">{t('open_access')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{pub_stats.get('active_years', 0)}</div>
                        <div class="metric-label">{t('active_years')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{author_stats.get('total_authors', 0)}</div>
                        <div class="metric-label">{t('unique_authors')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{country_stats.get('total_countries', 0)}</div>
                        <div class="metric-label">{t('unique_countries')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{citing_stats.get('total', 0):,}</div>
                        <div class="metric-label">{t('citing_works_total')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{citing_stats.get('unique_journals', 0)}</div>
                        <div class="metric-label">{t('unique_citing_journals')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{citing_stats.get('citation_lag', {}).get('avg', 0):.1f}</div>
                        <div class="metric-label">{t('avg_citation_lag')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{topic_rel.get('overlap_percentage', 0):.1f}%</div>
                        <div class="metric-label">{t('topic_overlap')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{len(topic_rel.get('hot_topics', {}))}</div>
                        <div class="metric-label">{t('hot_topics')}</div>
                    </div>
                </div>
            </div>
            
            <!-- Publication Dynamics -->
            {f'''
            <div id="publication_dynamics" class="section">
                <div class="section-title"><span class="icon">📈</span> {t('publication_dynamics')}</div>
                <div class="chart-container">
                    <img src="data:image/png;base64,{images.get('publication_dynamics', '')}" alt="{t('publication_dynamics')}">
                </div>
            </div>
            ''' if images.get('publication_dynamics') else ''}
            
            <!-- Citation Timeline -->
            {f'''
            <div id="citation_timeline" class="section">
                <div class="section-title"><span class="icon">📈</span> {t('citation_timeline')}</div>
                <div class="chart-container">
                    <img src="data:image/png;base64,{images.get('citation_timeline', '')}" alt="{t('citation_timeline')}">
                </div>
            </div>
            ''' if images.get('citation_timeline') else ''}
            
            <!-- Most Cited Publications -->
            {f'''
            <div id="most_cited" class="section">
                <div class="section-title"><span class="icon">🏆</span> {t('most_cited_publications')}</div>
                <table>
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Title</th>
                            <th>Year</th>
                            <th>Citations</th>
                            <th>Citations/Year</th>
                            <th>Authors</th>
                            <th>DOI</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join([
                            f'<tr>'
                            f'<td>{i+1}</td>'
                            f'<td class="word-wrap">{html.escape(pub["title"])}</td>'
                            f'<td>{pub["year"]}</td>'
                            f'<td><span class="citation-count">{pub["citations"]}</span></td>'
                            f'<td>{pub.get("citations_per_year", 0):.1f}</td>'
                            f'<td class="word-wrap">{", ".join(pub["authors"])}</td>'
                            f'<td><a href="https://doi.org/{pub["doi"]}" target="_blank" class="doi-link">{pub["doi"]}</a></td>'
                            f'</tr>'
                            for i, pub in enumerate(most_cited)
                        ])}
                    </tbody>
                </table>
            </div>
            ''' if most_cited else ''}
            
            <!-- Author Analysis -->
            {f'''
            <div id="author_analysis" class="section">
                <div class="section-title"><span class="icon">👨‍🎓</span> {t('author_analysis')}</div>
                
                <h4>Top Authors by Publications</h4>
                {''.join([
                    f'<div class="rank-item">'
                    f'<span class="rank-number">{i+1}</span>'
                    f'<span class="rank-name">{html.escape(a["display_name"])}</span>'
                    f'<span class="rank-count">{a["publications"]} pubs</span>'
                    f'<div class="progress-bar"><div class="progress-fill" style="width: {a["publications"]/max([a["publications"] for a in author_stats.get("top_authors", [])])*100 if author_stats.get("top_authors") else 0}%;"></div></div>'
                    f'<div style="font-size: 11px; color: #666;">h-index: {a["h_index"]} | Citations: {a["citations"]}</div>'
                    f'</div>'
                    for i, a in enumerate(author_stats.get("top_authors", [])[:20])
                ])}
                
                <h4 style="margin-top: 25px;">{t('top_countries')}</h4>
                {''.join([
                    f'<div class="rank-item">'
                    f'<span class="rank-number">{i+1}</span>'
                    f'<span class="rank-name">{html.escape(c["country"])}</span>'
                    f'<span class="rank-count">{c["publications"]} pubs</span>'
                    f'<div class="progress-bar"><div class="progress-fill" style="width: {c["publications"]/max([c["publications"] for c in country_stats.get("top_countries", [])])*100 if country_stats.get("top_countries") else 0}%;"></div></div>'
                    f'</div>'
                    for i, c in enumerate(country_stats.get("top_countries", [])[:20])
                ])}
                
                <h4 style="margin-top: 25px;">{t('unique_countries_per_reference')}</h4>
                {''.join([
                    f'<div class="rank-item">'
                    f'<span class="rank-number">{i+1}</span>'
                    f'<span class="rank-name">{html.escape(country)}</span>'
                    f'<span class="rank-count">{count} refs</span>'
                    f'<div class="progress-bar"><div class="progress-fill" style="width: {count/max(author_stats.get("unique_countries_per_reference", {}).values())*100 if author_stats.get("unique_countries_per_reference") else 0}%;"></div></div>'
                    f'</div>'
                    for i, (country, count) in enumerate(list(author_stats.get("unique_countries_per_reference", {}).items())[:20])
                ])}
                
                <h4 style="margin-top: 25px;">{t('authors_per_country')}</h4>
                {''.join([
                    f'<div class="rank-item">'
                    f'<span class="rank-number">{i+1}</span>'
                    f'<span class="rank-name">{html.escape(country)}</span>'
                    f'<span class="rank-count">{count} authors</span>'
                    f'<div class="progress-bar"><div class="progress-fill" style="width: {count/max(author_stats.get("authors_per_country", {}).values())*100 if author_stats.get("authors_per_country") else 0}%;"></div></div>'
                    f'</div>'
                    for i, (country, count) in enumerate(list(author_stats.get("authors_per_country", {}).items())[:20])
                ])}
                
                <h4 style="margin-top: 25px;">{t('collaboration_patterns')}</h4>
                {''.join([
                    f'<div class="rank-item">'
                    f'<span class="rank-number">{i+1}</span>'
                    f'<span class="rank-name">{html.escape(pattern)}</span>'
                    f'<span class="rank-count">{count} pubs</span>'
                    f'<div class="progress-bar"><div class="progress-fill" style="width: {count/max(author_stats.get("collaboration_patterns", {}).get("all_patterns", {}).values())*100 if author_stats.get("collaboration_patterns", {}).get("all_patterns") else 0}%;"></div></div>'
                    f'</div>'
                    for i, (pattern, count) in enumerate(list(author_stats.get("collaboration_patterns", {}).get("all_patterns", {}).items())[:30])
                ])}
            </div>
            ''' if author_stats.get('top_authors') else ''}
            
            <!-- Affiliation & Country Analysis -->
            {f'''
            <div id="affiliation_analysis" class="section">
                <div class="section-title"><span class="icon">🏛️</span> {t('affiliation_analysis')}</div>
                
                <h4>{t('top_affiliations')}</h4>
                {''.join([
                    f'<div class="rank-item">'
                    f'<span class="rank-number">{i+1}</span>'
                    f'<span class="rank-name">{html.escape(a["name"][:60])}</span>'
                    f'<span class="rank-count">{a["publications"]} pubs</span>'
                    f'<div class="progress-bar"><div class="progress-fill" style="width: {a["publications"]/max([a["publications"] for a in affiliation_stats.get("top_affiliations", [])])*100 if affiliation_stats.get("top_affiliations") else 0}%;"></div></div>'
                    f'<div style="font-size: 11px; color: #666;">Country: {a.get("country", "N/A")} | Authors: {a.get("authors_count", 0)}</div>'
                    f'</div>'
                    for i, a in enumerate(affiliation_stats.get("top_affiliations", [])[:20])
                ])}
            </div>
            ''' if affiliation_stats.get('top_affiliations') else ''}
            
            <!-- Citation Analysis -->
            <div id="citation_analysis" class="section">
                <div class="section-title"><span class="icon">📊</span> {t('citation_analysis')}</div>
                
                {f'''
                <div class="chart-container">
                    <img src="data:image/png;base64,{images.get('citation_distribution', '')}" alt="{t('citation_distribution')}">
                </div>
                ''' if images.get('citation_distribution') else ''}
                
                <!-- Citation Matrix -->
                {f'''
                <h4 style="margin-top: 25px;">{t('citation_matrix')}</h4>
                <div class="chart-container">
                    <img src="data:image/png;base64,{images.get('citation_matrix', '')}" alt="{t('citation_matrix')}">
                </div>
                
                <div style="overflow-x: auto; margin-top: 15px;">
                    <table>
                        <thead>
                            <tr>
                                <th>{t('publication_year')}</th>
                                {''.join([f'<th>{year}</th>' for year in sorted(citation_matrix.keys()) if citation_matrix.get(year)])}
                            </tr>
                        </thead>
                        <tbody>
                            {''.join([
                                f'<tr>'
                                f'<td><strong>{pub_year}</strong></td>'
                                f'{''.join([f'<td>{citation_matrix.get(pub_year, {}).get(cite_year, 0)}</td>' for cite_year in sorted(citation_matrix.keys())])}'
                                f'</tr>'
                                for pub_year in sorted(citation_matrix.keys())
                            ])}
                        </tbody>
                    </table>
                </div>
                ''' if citation_matrix else ''}
            </div>
            
            <!-- Citing Works Analysis -->
            {f'''
            <div id="citing_works_analysis" class="section">
                <div class="section-title"><span class="icon">📚</span> {t('citing_works_analysis')}</div>
                
                <div class="metrics-grid" style="grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));">
                    <div class="metric-card">
                        <div class="metric-value">{citing_stats.get("total", 0):,}</div>
                        <div class="metric-label">{t('citing_works_total')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{citing_stats.get("unique_journals", 0)}</div>
                        <div class="metric-label">{t('unique_citing_journals')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{citing_stats.get("unique_publishers", 0)}</div>
                        <div class="metric-label">{t('unique_citing_publishers')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{citing_stats.get("unique_countries", 0)}</div>
                        <div class="metric-label">{t('unique_citing_countries')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{citing_stats.get("citation_lag", {}).get("avg", 0):.1f}</div>
                        <div class="metric-label">{t('avg_citation_lag')}</div>
                    </div>
                </div>
                
                <div class="two-column">
                    <div>
                        <h4>{t('top_citing_journals')}</h4>
                        {''.join([
                            f'<div class="rank-item">'
                            f'<span class="rank-number">{i+1}</span>'
                            f'<span class="rank-name">{html.escape(j["name"][:40])}</span>'
                            f'<span class="rank-count">{j["count"]}</span>'
                            f'<div class="progress-bar"><div class="progress-fill" style="width: {j["count"]/max([j["count"] for j in citing_stats.get("top_journals", [])])*100 if citing_stats.get("top_journals") else 0}%;"></div></div>'
                            f'</div>'
                            for i, j in enumerate(citing_stats.get("top_journals", [])[:20])
                        ])}
                    </div>
                    <div>
                        <h4>{t('top_citing_publishers')}</h4>
                        {''.join([
                            f'<div class="rank-item">'
                            f'<span class="rank-number">{i+1}</span>'
                            f'<span class="rank-name">{html.escape(p["name"][:40])}</span>'
                            f'<span class="rank-count">{p["count"]}</span>'
                            f'<div class="progress-bar"><div class="progress-fill" style="width: {p["count"]/max([p["count"] for p in citing_stats.get("top_publishers", [])])*100 if citing_stats.get("top_publishers") else 0}%;"></div></div>'
                            f'</div>'
                            for i, p in enumerate(citing_stats.get("top_publishers", [])[:20])
                        ])}
                    </div>
                </div>
                
                <div class="two-column" style="margin-top: 20px;">
                    <div>
                        <h4>{t('top_citing_countries')}</h4>
                        {''.join([
                            f'<div class="rank-item">'
                            f'<span class="rank-number">{i+1}</span>'
                            f'<span class="rank-name">{html.escape(c["name"][:30])}</span>'
                            f'<span class="rank-count">{c["count"]}</span>'
                            f'<div class="progress-bar"><div class="progress-fill" style="width: {c["count"]/max([c["count"] for c in citing_stats.get("top_countries", [])])*100 if citing_stats.get("top_countries") else 0}%;"></div></div>'
                            f'</div>'
                            for i, c in enumerate(citing_stats.get("top_countries", [])[:20])
                        ])}
                    </div>
                    <div>
                        <h4>{t('top_citing_authors')}</h4>
                        {''.join([
                            f'<div class="rank-item">'
                            f'<span class="rank-number">{i+1}</span>'
                            f'<span class="rank-name">{html.escape(a["name"][:30])}</span>'
                            f'<span class="rank-count">{a["count"]}</span>'
                            f'<div class="progress-bar"><div class="progress-fill" style="width: {a["count"]/max([a["count"] for a in citing_stats.get("top_authors", [])])*100 if citing_stats.get("top_authors") else 0}%;"></div></div>'
                            f'</div>'
                            for i, a in enumerate(citing_stats.get("top_authors", [])[:20])
                        ])}
                    </div>
                </div>
                
                <div style="margin-top: 25px;">
                    <h4>{t('top_citing_affiliations')}</h4>
                    {''.join([
                        f'<div class="rank-item">'
                        f'<span class="rank-number">{i+1}</span>'
                        f'<span class="rank-name">{html.escape(a["name"][:50])}</span>'
                        f'<span class="rank-count">{a["count"]}</span>'
                        f'<div class="progress-bar"><div class="progress-fill" style="width: {a["count"]/max([a["count"] for a in citing_stats.get("top_affiliations", [])])*100 if citing_stats.get("top_affiliations") else 0}%;"></div></div>'
                        f'</div>'
                        for i, a in enumerate(citing_stats.get("top_affiliations", [])[:20])
                    ])}
                </div>
                
                <h4 style="margin-top: 25px;">{t('unique_countries_per_reference')} (Citing)</h4>
                {''.join([
                    f'<div class="rank-item">'
                    f'<span class="rank-number">{i+1}</span>'
                    f'<span class="rank-name">{html.escape(country)}</span>'
                    f'<span class="rank-count">{count} refs</span>'
                    f'<div class="progress-bar"><div class="progress-fill" style="width: {count/max(citing_stats.get("unique_countries_per_reference", {}).values())*100 if citing_stats.get("unique_countries_per_reference") else 0}%;"></div></div>'
                    f'</div>'
                    for i, (country, count) in enumerate(list(citing_stats.get("unique_countries_per_reference", {}).items())[:20])
                ])}
                
                <h4 style="margin-top: 25px;">{t('authors_per_country')} (Citing)</h4>
                {''.join([
                    f'<div class="rank-item">'
                    f'<span class="rank-number">{i+1}</span>'
                    f'<span class="rank-name">{html.escape(country)}</span>'
                    f'<span class="rank-count">{count} authors</span>'
                    f'<div class="progress-bar"><div class="progress-fill" style="width: {count/max(citing_stats.get("authors_per_country", {}).values())*100 if citing_stats.get("authors_per_country") else 0}%;"></div></div>'
                    f'</div>'
                    for i, (country, count) in enumerate(list(citing_stats.get("authors_per_country", {}).items())[:20])
                ])}
                
                <h4 style="margin-top: 25px;">{t('collaboration_patterns')} (Citing)</h4>
                {''.join([
                    f'<div class="rank-item">'
                    f'<span class="rank-number">{i+1}</span>'
                    f'<span class="rank-name">{html.escape(pattern)}</span>'
                    f'<span class="rank-count">{count} pubs</span>'
                    f'<div class="progress-bar"><div class="progress-fill" style="width: {count/max(citing_stats.get("collaboration_patterns", {}).get("all_patterns", {}).values())*100 if citing_stats.get("collaboration_patterns", {}).get("all_patterns") else 0}%;"></div></div>'
                    f'</div>'
                    for i, (pattern, count) in enumerate(list(citing_stats.get("collaboration_patterns", {}).get("all_patterns", {}).items())[:30])
                ])}
                
                <div class="two-column" style="margin-top: 25px;">
                    <div class="chart-container">
                        <img src="data:image/png;base64,{images.get('top_citing_journals', '')}" alt="{t('top_citing_journals')}">
                    </div>
                    <div class="chart-container">
                        <img src="data:image/png;base64,{images.get('top_citing_publishers', '')}" alt="{t('top_citing_publishers')}">
                    </div>
                </div>
                <div class="two-column">
                    <div class="chart-container">
                        <img src="data:image/png;base64,{images.get('top_citing_countries', '')}" alt="{t('top_citing_countries')}">
                    </div>
                </div>
            </div>
            ''' if citing_stats.get('total', 0) > 0 else ''}
            
            <!-- Topics Analysis -->
            {f'''
            <div id="topic_analysis" class="section">
                <div class="section-title"><span class="icon">🏷️</span> {t('topic_analysis')}</div>
                
                <h4>{t('topics')}</h4>
                {''.join([
                    f'<div class="rank-item">'
                    f'<span class="rank-number">{i+1}</span>'
                    f'<span class="rank-name">{html.escape(t["name"][:50])}</span>'
                    f'<span class="rank-count">{t["publications"]} pubs</span>'
                    f'<div class="progress-bar"><div class="progress-fill" style="width: {t["publications"]/max([t["publications"] for t in topic_stats.get("topics", [])])*100 if topic_stats.get("topics") else 0}%;"></div></div>'
                    f'</div>'
                    for i, t in enumerate(topic_stats.get("topics", [])[:20])
                ])}
                
                <h4 style="margin-top: 25px;">{t('fields')}</h4>
                {''.join([
                    f'<div class="rank-item">'
                    f'<span class="rank-number">{i+1}</span>'
                    f'<span class="rank-name">{html.escape(f["name"][:50])}</span>'
                    f'<span class="rank-count">{f["publications"]} pubs</span>'
                    f'<div class="progress-bar"><div class="progress-fill" style="width: {f["publications"]/max([f["publications"] for f in topic_stats.get("fields", [])])*100 if topic_stats.get("fields") else 0}%;"></div></div>'
                    f'</div>'
                    for i, f in enumerate(topic_stats.get("fields", [])[:20])
                ])}
                
                <h4 style="margin-top: 25px;">{t('domains')}</h4>
                {''.join([
                    f'<div class="rank-item">'
                    f'<span class="rank-number">{i+1}</span>'
                    f'<span class="rank-name">{html.escape(d["name"][:50])}</span>'
                    f'<span class="rank-count">{d["publications"]} pubs</span>'
                    f'<div class="progress-bar"><div class="progress-fill" style="width: {d["publications"]/max([d["publications"] for d in topic_stats.get("domains", [])])*100 if topic_stats.get("domains") else 0}%;"></div></div>'
                    f'</div>'
                    for i, d in enumerate(topic_stats.get("domains", [])[:20])
                ])}
                
                <h4 style="margin-top: 25px;">{t('concepts')}</h4>
                {''.join([
                    f'<div class="rank-item">'
                    f'<span class="rank-number">{i+1}</span>'
                    f'<span class="rank-name">{html.escape(c["name"][:50])}</span>'
                    f'<span class="rank-count">{c["publications"]} pubs</span>'
                    f'<div class="progress-bar"><div class="progress-fill" style="width: {c["publications"]/max([c["publications"] for c in topic_stats.get("concepts", [])])*100 if topic_stats.get("concepts") else 0}%;"></div></div>'
                    f'</div>'
                    for i, c in enumerate(topic_stats.get("concepts", [])[:30])
                ])}
            </div>
            ''' if topic_stats.get('topics') else ''}
            
            <!-- Topic Relationship -->
            {f'''
            <div id="topic_relationship" class="section">
                <div class="section-title"><span class="icon">🔄</span> {t('topic_relationship')}</div>
                
                <div class="metrics-grid" style="grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));">
                    <div class="metric-card">
                        <div class="metric-value">{topic_rel.get('total_pub_topics', 0)}</div>
                        <div class="metric-label">{t('publication_topics')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{topic_rel.get('total_citing_topics', 0)}</div>
                        <div class="metric-label">{t('citing_topics')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{topic_rel.get('overlap_percentage', 0):.1f}%</div>
                        <div class="metric-label">{t('topic_overlap_percentage')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{len(topic_rel.get('hot_topics', {}))}</div>
                        <div class="metric-label">{t('hot_topics')}</div>
                    </div>
                </div>
                
                <div class="two-column">
                    <div>
                        <h4>{t('publication_topics')}</h4>
                        {''.join([
                            f'<div class="rank-item">'
                            f'<span class="rank-name">{html.escape(topic[:50])}</span>'
                            f'<span class="rank-count">{count}</span>'
                            f'<div class="progress-bar"><div class="progress-fill" style="width: {count/max(topic_rel.get("publication_topics", {}).values())*100 if topic_rel.get("publication_topics") else 0}%;"></div></div>'
                            f'</div>'
                            for topic, count in list(topic_rel.get("publication_topics", {}).items())[:20]
                        ])}
                    </div>
                    <div>
                        <h4>{t('citing_topics')}</h4>
                        {''.join([
                            f'<div class="rank-item">'
                            f'<span class="rank-name">{html.escape(topic[:50])}</span>'
                            f'<span class="rank-count">{count}</span>'
                            f'<div class="progress-bar"><div class="progress-fill" style="width: {count/max(topic_rel.get("citing_topics", {}).values())*100 if topic_rel.get("citing_topics") else 0}%;"></div></div>'
                            f'</div>'
                            for topic, count in list(topic_rel.get("citing_topics", {}).items())[:20]
                        ])}
                    </div>
                </div>
                
                <div style="margin-top: 20px;">
                    <h4>{t('hot_topics')} ({t('ratio')} ↓)</h4>
                    {''.join([
                        f'<div class="rank-item hot-topic">'
                        f'<span class="rank-name">{html.escape(topic[:50])}</span>'
                        f'<span class="rank-count">Citations: {data["citations"]} | Ratio: {data["ratio"]:.2f}</span>'
                        f'<div class="progress-bar"><div class="progress-fill" style="width: {min(100, data["ratio"] / max([d["ratio"] for d in topic_rel.get("hot_topics", {}).values()]) * 100 if topic_rel.get("hot_topics") else 0)}%;"></div></div>'
                        f'<div style="font-size: 11px; color: #666;">Publications: {data["publications"]} | Hot Index: {data["hot_index"]:.1f}</div>'
                        f'</div>'
                        for topic, data in list(topic_rel.get("hot_topics", {}).items())[:20]
                    ])}
                </div>
                
                <div style="margin-top: 25px;">
                    <div class="chart-container">
                        <img src="data:image/png;base64,{images.get('hot_topics', '')}" alt="Hot Topics">
                    </div>
                </div>
            </div>
            ''' if topic_rel.get('publication_topics') else ''}
            
            <!-- Detailed Citations -->
            {f'''
            <div id="detailed_citations" class="section">
                <div class="section-title"><span class="icon">📋</span> {t('detailed_citations')}</div>
                
                {''.join([
                    f'''
                    <div class="collapser" onclick="toggleCitations('{pub_id.replace('https://openalex.org/', '')}')">
                        <strong>{html.escape(data['title'])}</strong>
                        <span class="badge badge-info">{data['year']}</span>
                        <span class="citation-count">{data['total_citations']} citations</span>
                        <span style="font-size: 12px; color: #666; margin-left: 10px;">DOI: {data['doi']}</span>
                        <span style="float: right; font-size: 12px; color: #666;">Click to toggle citations</span>
                    </div>
                    <div id="citations_{pub_id.replace('https://openalex.org/', '')}" style="display: none;">
                        {''.join([
                            f'''
                            <div class="citation-detail">
                                <div><strong>{html.escape(cite['citing_title'])}</strong></div>
                                <div class="cite-meta">
                                    <strong>{t('citing_journal')}:</strong> {html.escape(cite['citing_journal'])} | 
                                    <strong>{t('citing_year')}:</strong> {cite['citing_year']} | 
                                    <strong>{t('citing_date')}:</strong> {cite['citing_date']} |
                                    <strong>{t('citation_lag')}:</strong> {cite['citation_lag']} years
                                </div>
                                <div class="cite-meta">
                                    <strong>{t('authors')}:</strong> {', '.join(cite['citing_authors'])} |
                                    <strong>{t('countries')}:</strong> {', '.join(cite['citing_countries'])} |
                                    <strong>{t('topics')}:</strong> {', '.join(cite['citing_topics'][:5])}
                                </div>
                                <div class="cite-meta">
                                    <a href="https://doi.org/{cite['citing_doi']}" target="_blank" class="doi-link">DOI: {cite['citing_doi']}</a>
                                </div>
                            </div>
                            ''' for cite in data['citations']
                        ])}
                    </div>
                    ''' for pub_id, data in detailed_citations.items()
                ])}
            </div>
            ''' if detailed_citations else ''}
            
            <!-- All Publications -->
            <div id="all_publications" class="section">
                <div class="section-title"><span class="icon">📚</span> {t('all_publications')}</div>
                
                <div class="filter-section">
                    <div class="filter-row">
                        <div>
                            <label for="yearFilter">{t('filter_by_year')}:</label>
                            <select id="yearFilter" onchange="filterPublications()">
                                <option value="">All Years</option>
                                {''.join([
                                    f'<option value="{year}">{year}</option>'
                                    for year in sorted(pub_stats.get('year_counts', {}).keys(), reverse=True)
                                ])}
                            </select>
                        </div>
                        <div>
                            <label for="authorFilter">{t('filter_by_author')}:</label>
                            <input type="text" id="authorFilter" placeholder="Author name..." onkeyup="filterPublications()">
                        </div>
                        <div>
                            <label for="citationFilter">{t('filter_by_citations')}:</label>
                            <input type="number" id="citationFilter" placeholder="Min citations..." min="0" onchange="filterPublications()">
                        </div>
                        <div>
                            <label for="searchInput">{t('search_publications')}:</label>
                            <input type="text" id="searchInput" placeholder="Search..." onkeyup="filterPublications()">
                        </div>
                        <div>
                            <span id="visibleCount" style="font-weight: 500;">All publications</span>
                        </div>
                    </div>
                </div>
                
                <div style="overflow-x: auto; max-height: 800px; overflow-y: auto;">
                    <table id="publicationsTable">
                        <thead>
                            <tr>
                                <th onclick="sortTable(0)" style="cursor: pointer;">#</th>
                                <th onclick="sortTable(1)" style="cursor: pointer;">Title</th>
                                <th onclick="sortTable(2)" style="cursor: pointer;">Year</th>
                                <th onclick="sortTable(3)" style="cursor: pointer;">Citations</th>
                                <th onclick="sortTable(4)" style="cursor: pointer;">Citations/Year</th>
                                <th onclick="sortTable(5)" style="cursor: pointer;">Journal</th>
                                <th>DOI</th>
                                <th>{t('show_citations')}</th>
                            </tr>
                        </thead>
                        <tbody>
                            {''.join([
                                f'<tr data-year="{p.publication_year}" data-authors="{",".join([a.display_name for a in p.authors])}" data-citations="{p.cited_by_count}" data-title="{p.title.lower()}" data-doi="{p.doi.lower()}">'
                                f'<td>{i+1}</td>'
                                f'<td class="word-wrap">{html.escape(p.title)}</td>'
                                f'<td>{p.publication_year}</td>'
                                f'<td><span class="citation-count">{p.cited_by_count}</span></td>'
                                f'<td>{p.citations_per_year:.1f}</td>'
                                f'<td>{html.escape(p.journal_name)}</td>'
                                f'<td><a href="https://doi.org/{p.doi}" target="_blank" class="doi-link">{p.doi}</a></td>'
                                f'<td>'
                                f'<button onclick="toggleCitations(\'{p.id.replace("https://openalex.org/", "")}\')" style="padding: 3px 8px; border: none; border-radius: 4px; background: {primary}; color: white; cursor: pointer; font-size: 11px;">{t("show_citations")}</button>'
                                f'</td>'
                                f'</tr>'
                                for i, p in enumerate(all_publications)
                            ])}
                        </tbody>
                    </table>
                </div>
            </div>
            
            <!-- Footer -->
            <div class="footer">
                <p>{t('footer')}</p>
                <p><a href="{t('journal_url')}" target="_blank">{t('journal_url')}</a></p>
                <p style="font-size: 11px; margin-top: 5px;">Data source: OpenAlex | Generated: {datetime.now().strftime('%d.%m.%Y')}</p>
            </div>
        </div>
    </div>
</body>
</html>"""
    
    return html_content

# ============================================
# MAIN ANALYSIS FUNCTION
# ============================================

async def analyze_journal(issn: str, periods: List[Tuple[int, int]], progress_callback=None) -> Tuple[Journal, List[Publication], Dict[str, List[Citation]], Dict]:
    """Main journal analysis function with timeout handling"""
    
    issn_clean = parse_issn(issn)
    if not issn_clean:
        return None, [], {}, {}
    
    periods_hash = hashlib.md5(str(periods).encode()).hexdigest()[:8]
    cache_data = load_from_cache(issn_clean, periods_hash)
    if cache_data:
        journal = Journal(**cache_data['journal'])
        publications = [Publication(**p) for p in cache_data['publications']]
        citations = {k: [Citation(**c) for c in v] for k, v in cache_data['citations'].items()}
        return journal, publications, citations, cache_data.get('analytics', {})
    
    # Создаем сессию с таймаутами
    timeout = aiohttp.ClientTimeout(total=120, connect=30, sock_read=60)
    
    async with aiohttp.ClientSession(timeout=timeout) as session:
        if progress_callback:
            progress_callback('journal', 0, 100)
        
        # Получение информации о журнале с таймаутом
        try:
            journal_data = await asyncio.wait_for(
                get_journal_by_issn(issn_clean, session),
                timeout=45.0
            )
        except asyncio.TimeoutError:
            if SHOW_DEBUG_LOGS:
                print(f"⚠️ Timeout getting journal data for {issn_clean}")
            return None, [], {}, {}
        
        if not journal_data:
            return None, [], {}, {}
        
        journal = Journal(
            id=journal_data.get('id', ''),
            issn=issn_clean,
            title=journal_data.get('display_name', 'Unknown'),
            publisher=journal_data.get('publisher', ''),
            works_count=journal_data.get('works_count', 0),
            cited_by_count=journal_data.get('cited_by_count', 0),
            is_oa=journal_data.get('is_oa', False),
            created_date=journal_data.get('created_date', ''),
            updated_date=journal_data.get('updated_date', '')
        )
        
        if progress_callback:
            progress_callback('publications', 0, 100)
        
        def pub_progress(current, total):
            if progress_callback:
                progress_callback('publications', current, total)
        
        # Получение публикаций с таймаутом
        try:
            works = await asyncio.wait_for(
                get_journal_publications(journal.id, session, periods, pub_progress, issn_clean),
                timeout=180.0
            )
        except asyncio.TimeoutError:
            if SHOW_DEBUG_LOGS:
                print(f"⚠️ Timeout getting publications for {journal.title}")
            return journal, [], {}, {}
        
        if not works:
            return journal, [], {}, {}
        
        publications = []
        for work in works:
            pub = parse_publication_from_openalex(work)
            if pub:
                publications.append(pub)
        
        if len(publications) > MAX_PUBLICATIONS_TO_ANALYZE:
            publications = publications[:MAX_PUBLICATIONS_TO_ANALYZE]
        
        if progress_callback:
            progress_callback('citations', 0, len(publications))
        
        citations = {}
        total_citations = 0
        
        # Получение цитирований с таймаутом для каждой работы
        for idx, pub in enumerate(publications):
            if progress_callback:
                progress_callback('citations', idx + 1, len(publications))
            
            if pub.cited_by_count > 0:
                try:
                    citing_works = await asyncio.wait_for(
                        get_work_citations(pub.id, session),
                        timeout=60.0
                    )
                except asyncio.TimeoutError:
                    if SHOW_DEBUG_LOGS:
                        print(f"⚠️ Timeout getting citations for {pub.id}")
                    continue
                
                parsed_citations = []
                for cw in citing_works:
                    citation = parse_citation_from_openalex(cw, pub.publication_year)
                    if citation:
                        parsed_citations.append(citation)
                        if citation.citing_year > 0:
                            pub.citation_years[citation.citing_year] = pub.citation_years.get(citation.citing_year, 0) + 1
                citations[pub.id] = parsed_citations
                total_citations += len(parsed_citations)
        
        current_year = datetime.now().year
        for pub in publications:
            if pub.publication_year > 0:
                years_since = current_year - pub.publication_year + 1
                pub.citations_per_year = pub.cited_by_count / max(years_since, 1)
        
        if progress_callback:
            progress_callback('analytics', 0, 100)
        
        analytics_engine = JournalAnalytics(journal, publications, citations)
        analytics = analytics_engine.get_analytics()
        
        cache_data = {
            'journal': asdict(journal),
            'publications': [asdict(p) for p in publications],
            'citations': {k: [asdict(c) for c in v] for k, v in citations.items()},
            'analytics': analytics
        }
        save_to_cache(issn_clean, periods_hash, cache_data)
        
        return journal, publications, citations, analytics

# ============================================
# STREAMLIT INTERFACE
# ============================================

def main():
    st.set_page_config(
        page_title="Journal Analytics System",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    if 'primary_color' not in st.session_state:
        st.session_state.primary_color = '#667eea'
    if 'secondary_color' not in st.session_state:
        st.session_state.secondary_color = '#f39c12'
    if 'language' not in st.session_state:
        st.session_state.language = 'en'
    if 'analysis_done' not in st.session_state:
        st.session_state.analysis_done = False
    if 'journal' not in st.session_state:
        st.session_state.journal = None
    if 'publications' not in st.session_state:
        st.session_state.publications = []
    if 'citations' not in st.session_state:
        st.session_state.citations = {}
    if 'analytics' not in st.session_state:
        st.session_state.analytics = {}
    if 'periods' not in st.session_state:
        st.session_state.periods = []
    if 'images' not in st.session_state:
        st.session_state.images = {}
    
    apply_theme_css(st.session_state.primary_color, st.session_state.secondary_color)
    
    current_lang = st.session_state.language
    def t(key: str, **kwargs) -> str:
        return translate(key, current_lang, **kwargs)
    
    with st.sidebar:
        st.markdown(f"## {t('settings')}")
        
        lang_option = st.selectbox(
            t('language'),
            options=['en', 'ru'],
            format_func=lambda x: t('language_en') if x == 'en' else t('language_ru'),
            index=0 if current_lang == 'en' else 1
        )
        if lang_option != current_lang:
            st.session_state.language = lang_option
            st.rerun()
        
        st.markdown("---")
        
        # Color Theme
        st.markdown(f"## {t('color_theme')}")
        
        preset_themes = {
            t('default_theme'): {"primary": "#667eea", "secondary": "#9b59b6"},
            t('emerald_theme'): {"primary": "#2ecc71", "secondary": "#27ae60"},
            t('sunset_theme'): {"primary": "#e74c3c", "secondary": "#c0392b"},
            t('ocean_theme'): {"primary": "#3498db", "secondary": "#2980b9"},
            t('royal_theme'): {"primary": "#9b59b6", "secondary": "#e84393"},
            t('forest_theme'): {"primary": "#27ae60", "secondary": "#2ecc71"},
            t('cherry_theme'): {"primary": "#e84393", "secondary": "#9b59b6"},
            t('amber_theme'): {"primary": "#f39c12", "secondary": "#e67e22"},
        }
        
        theme_option = st.selectbox(
            t('preset_themes'),
            options=list(preset_themes.keys()),
            index=0
        )
        
        use_preset = st.checkbox(t('use_preset'), value=True)
        
        if use_preset:
            selected_theme = preset_themes[theme_option]
            st.session_state.primary_color = selected_theme["primary"]
            st.session_state.secondary_color = selected_theme["secondary"]
        else:
            selected_color = st.color_picker(
                t('pick_color'),
                value=st.session_state.primary_color
            )
            st.session_state.primary_color = selected_color
            st.session_state.secondary_color = get_complementary_color(selected_color)
        
        complementary = st.session_state.secondary_color
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(
                f'<div style="text-align: center;">'
                f'<div style="background: {st.session_state.primary_color}; height: 40px; border-radius: 8px;"></div>'
                f'<div style="font-size: 11px; margin-top: 5px;">{t("primary_color")}</div>'
                f'</div>',
                unsafe_allow_html=True
            )
        with col2:
            st.markdown(
                f'<div style="text-align: center;">'
                f'<div style="background: {complementary}; height: 40px; border-radius: 8px;"></div>'
                f'<div style="font-size: 11px; margin-top: 5px;">{t("complementary_color")}</div>'
                f'</div>',
                unsafe_allow_html=True
            )
        
        st.markdown(
            f'<div style="background: linear-gradient(135deg, {st.session_state.primary_color}, {complementary}); height: 6px; border-radius: 3px; margin: 10px 0;"></div>',
            unsafe_allow_html=True
        )
        
        apply_theme_css(st.session_state.primary_color, complementary)
        
        st.markdown("---")
        
        if st.button("🗑️ Clear Cache"):
            import shutil
            if os.path.exists('cache'):
                shutil.rmtree('cache')
                st.session_state.analysis_done = False
                st.cache_data.clear()
                st.success("Cache cleared!")
        
        st.markdown("---")
        st.markdown("📚 **Journal Analytics System**")
        st.markdown("v2.0 | Full Featured")
        st.markdown("Data: OpenAlex")
        st.markdown("© daM / Chimica Techno Acta")
    
    st.markdown(f"# {t('app_title')}")
    st.markdown(f"### {t('app_subtitle')}")
    st.markdown("---")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        issn_input = st.text_input(
            t('issn_input'),
            placeholder=t('issn_placeholder'),
            help=t('issn_help')
        )
    
    with col2:
        period_input = st.text_input(
            t('period_input'),
            placeholder=t('period_placeholder'),
            help=t('period_help')
        )
    
    if st.button(t('analyze_button'), type="primary", use_container_width=True):
        issn_clean = parse_issn(issn_input)
        if not issn_clean:
            st.error(t('invalid_issn'))
            return
        
        periods = parse_periods(period_input)
        if not periods:
            st.error(t('invalid_period'))
            return
        
        st.info(t('analysis_started'))
        
        progress_placeholder = st.empty()
        status_placeholder = st.empty()
        
        def progress_callback(stage, current, total):
            if stage == 'journal':
                status_placeholder.text(t('fetching_journal'))
                progress_placeholder.progress(0.1)
            elif stage == 'publications':
                status_placeholder.text(f"{t('fetching_publications')} ({current}/{total})")
                progress_placeholder.progress(0.1 + 0.5 * (current / total))
            elif stage == 'citations':
                status_placeholder.text(f"{t('fetching_citations')} ({current}/{total})")
                progress_placeholder.progress(0.6 + 0.3 * (current / total))
            elif stage == 'analytics':
                status_placeholder.text(t('analyzing_data'))
                progress_placeholder.progress(0.9)
        
        try:
            start_time = time.time()
            
            # Создаем новый событийный цикл для изоляции
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                journal, publications, citations, analytics = loop.run_until_complete(
                    analyze_journal(issn_clean, periods, progress_callback)
                )
            finally:
                loop.close()
            
            if not journal:
                st.error(t('journal_not_found'))
                progress_placeholder.empty()
                status_placeholder.empty()
                return
            
            # ... остальной код
        except asyncio.TimeoutError:
            st.error("❌ Analysis timed out. Please try again or check your internet connection.")
            progress_placeholder.empty()
            status_placeholder.empty()
            return
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            import traceback
            st.code(traceback.format_exc())
            progress_placeholder.empty()
            status_placeholder.empty()
            return
    
    if st.session_state.analysis_done and st.session_state.journal:
        journal = st.session_state.journal
        publications = st.session_state.publications
        citations = st.session_state.citations
        analytics = st.session_state.analytics
        periods = st.session_state.periods
        
        st.markdown("---")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"**📚 {journal.title}**")
            st.caption(f"ISSN: {journal.issn}")
        with col2:
            st.caption(f"Publisher: {journal.publisher}")
            st.caption(f"Works: {journal.works_count}")
        with col3:
            st.caption(f"Citations: {journal.cited_by_count:,}")
            st.caption(f"Period: {', '.join([f'{s}-{e}' if s != e else str(s) for s, e in periods])}")
        
        st.markdown("---")
        
        pub_stats = analytics.get('publication_stats', {})
        cit_stats = analytics.get('citation_stats', {})
        author_stats = analytics.get('author_stats', {})
        country_stats = analytics.get('country_stats', {})
        citing_stats = analytics.get('citing_works_stats', {})
        topic_rel = analytics.get('topic_relationship', {})
        
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric(t('total_publications'), pub_stats.get('total', 0))
        with col2:
            st.metric(t('total_citations'), f"{cit_stats.get('total', 0):,}")
        with col3:
            st.metric(t('h_index'), cit_stats.get('h_index', 0))
        with col4:
            st.metric(t('avg_citations'), f"{cit_stats.get('avg', 0):.1f}")
        with col5:
            st.metric(t('open_access'), f"{pub_stats.get('oa_percentage', 0):.1f}%")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric(t('unique_authors'), author_stats.get('total_authors', 0))
        with col2:
            st.metric(t('unique_countries'), country_stats.get('total_countries', 0))
        with col3:
            st.metric(t('active_years'), pub_stats.get('active_years', 0))
        with col4:
            st.metric(t('citing_works_total'), citing_stats.get('total', 0))
        with col5:
            st.metric(t('avg_citation_lag'), f"{citing_stats.get('citation_lag', {}).get('avg', 0):.1f}")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(t('hot_topics'), len(topic_rel.get('hot_topics', {})))
        with col2:
            st.metric(t('topic_overlap_percentage'), f"{topic_rel.get('overlap_percentage', 0):.1f}%")
        
        st.markdown("---")
        
        with st.spinner("Generating visualizations..."):
            images = create_advanced_visualizations(analytics, current_lang)
            st.session_state.images = images
        
        viz_tabs = st.tabs([
            "📈 Dynamics",
            "📊 Citations",
            "👨‍🎓 Authors",
            "🌍 Countries",
            "🏷️ Topics",
            "📚 Citing Works"
        ])
        
        with viz_tabs[0]:
            if images.get('publication_dynamics'):
                st.image(f"data:image/png;base64,{images['publication_dynamics']}", use_container_width=True)
            if images.get('citation_timeline'):
                st.image(f"data:image/png;base64,{images['citation_timeline']}", use_container_width=True)
        
        with viz_tabs[1]:
            if images.get('citation_distribution'):
                st.image(f"data:image/png;base64,{images['citation_distribution']}", use_container_width=True)
            if images.get('citation_matrix'):
                st.image(f"data:image/png;base64,{images['citation_matrix']}", use_container_width=True)
        
        with viz_tabs[2]:
            if images.get('top_authors'):
                st.image(f"data:image/png;base64,{images['top_authors']}", use_container_width=True)
        
        with viz_tabs[3]:
            if images.get('top_countries'):
                st.image(f"data:image/png;base64,{images['top_countries']}", use_container_width=True)
        
        with viz_tabs[4]:
            if images.get('hot_topics'):
                st.image(f"data:image/png;base64,{images['hot_topics']}", use_container_width=True)
        
        with viz_tabs[5]:
            if images.get('top_citing_journals'):
                st.image(f"data:image/png;base64,{images['top_citing_journals']}", use_container_width=True)
            if images.get('top_citing_publishers'):
                st.image(f"data:image/png;base64,{images['top_citing_publishers']}", use_container_width=True)
            if images.get('top_citing_countries'):
                st.image(f"data:image/png;base64,{images['top_citing_countries']}", use_container_width=True)
        
        st.markdown("---")
        
        st.markdown(f"### {t('report_preview')}")
        
        with st.spinner(t('generating_report')):
            theme_colors = {
                'primary': st.session_state.primary_color,
                'secondary': st.session_state.secondary_color
            }
            html_report = generate_enhanced_html_report(
                journal, analytics, periods, images, theme_colors, current_lang, publications
            )

        filename = f"journal_{journal.issn}_{datetime.now().strftime('%Y%m%d')}.html"
        st.download_button(
            label=t('download_report'),
            data=html_report.encode('utf-8'),
            file_name=filename,
            mime="text/html",
            type="primary",
            use_container_width=True
        )
        
        with st.expander("📋 Report Preview"):
            st.components.v1.html(html_report, height=600, scrolling=True)
    
    else:
        st.info(t('no_data'))

if __name__ == "__main__":
    main()
