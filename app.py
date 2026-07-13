# ============================================
# СЕКЦИЯ ПАРАМЕТРОВ (настройка запросов)
# ============================================

# Параметры API запросов
BATCH_SIZE = 50  # Размер батча для всех API
MAX_RETRIES = 3  # Количество попыток при ошибке
TIMEOUT = 30  # Таймаут на запрос в секундах
DELAY_BETWEEN_BATCHES = 0.5  # Задержка между батчами (сек)
MAX_CONCURRENT_REQUESTS = 10  # Максимум параллельных запросов
RETRY_DELAY = 2  # Задержка перед повторной попыткой (сек)
ORCID_REQUEST_DELAY = 0.2  # Задержка между запросами к ORCID API (сек)

# Параметры для анализа журналов
MAX_WORKERS = 8  # Количество параллельных потоков
BASE_DELAY = 0.35  # Базовая задержка между запросами
MAX_CITING_PER_PAPER = 300  # Максимум цитирующих работ на статью
MAX_PAGINATION_PAGES = 8  # Максимум страниц пагинации для цитирующих

# Параметры вывода
SHOW_DEBUG_LOGS = True  # Показывать детальные логи
GENERATE_HTML_REPORT = True  # Генерировать HTML отчет
LOGO_PATH = None  # Путь к логотипу журнала (устанавливается через виджет)

# ============================================
# ИМПОРТЫ
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
import seaborn as sns
from wordcloud import WordCloud
from io import BytesIO
import base64
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import requests
from bs4 import BeautifulSoup
import os
import hashlib
from matplotlib.ticker import MaxNLocator
import html
import html as html_module
import colorsys
from tenacity import retry, stop_after_attempt, wait_exponential, wait_random
from concurrent.futures import ThreadPoolExecutor, as_completed
import math
from itertools import combinations
import difflib
import random
from threading import Lock
from tqdm import tqdm

# ============================================
# СЛОВАРЬ ПЕРЕВОДОВ (РАСШИРЕННЫЙ)
# ============================================

LANG = {
    'en': {
        'app_title': 'Advanced Journal Analysis Tool',
        'app_icon': '📊',
        'settings': '⚙️ Settings',
        'language': '🌐 Language',
        'language_en': 'English',
        'language_ru': 'Russian',
        'color_theme': '🎨 Color Theme',
        'preset_themes': '🎨 Theme Presets',
        'use_preset': 'Use preset',
        'select_color': '🎨 Select primary color',
        'primary': 'Primary',
        'secondary': 'Secondary',
        'upload_logo': 'Upload journal logo (optional)',
        'logo_help': 'Logo will be displayed in reports',
        'journal_analysis': '📊 Journal Analysis',
        'issn_input': 'ISSN Number',
        'issn_placeholder': '0028-0836 or 00280836',
        'issn_help': 'Enter ISSN of the journal to analyze',
        'period_input': 'Analysis Period',
        'period_placeholder': '2020-2023 or 2020,2021,2022',
        'period_help': 'Format: YYYY-YYYY (range) or YYYY,YYYY (list) or YYYY (single year)',
        'workers_count': 'Parallel Workers',
        'workers_help': 'Number of parallel threads for fetching citations (4-12)',
        'analyze_button': '🚀 Analyze Journal',
        'analyzing_articles': '📚 Loading journal articles...',
        'fetching_citations': '⚡ Fetching citing works...',
        'no_issn': '⚠️ Please enter ISSN',
        'no_period': '⚠️ Please enter analysis period',
        'analysis_complete': '✅ Analysis complete!',
        'download_report': '💾 Download HTML Report',
        'generating_report': 'Generating HTML report...',
        'no_data': '👈 Load data and click "Analyze Journal"',
        'footer': '© Advanced Journal Analysis Tool / Created by daM / Chimica Techno Acta',
        'journal_url': 'https://chimicatechnoacta.ru',
        'total_publications': 'Total Publications',
        'total_citations': 'Total Citations',
        'h_index': 'h-index',
        'g_index': 'g-index',
        'i10_index': 'i10-index',
        'i100_index': 'i100-index',
        'avg_citations': 'Avg Citations',
        'open_access': 'Open Access',
        'active_years': 'Active Years',
        'unique_authors': 'Unique Authors',
        'unique_affiliations': 'Unique Affiliations',
        'unique_countries': 'Unique Countries',
        'avg_authors_per_paper': 'Avg Authors/Paper',
        'avg_affiliations_per_paper': 'Avg Affiliations/Paper',
        'avg_countries_per_paper': 'Avg Countries/Paper',
        'international_collaboration_rate': 'International Collaboration Rate',
        'unique_citing_authors': 'Unique Citing Authors',
        'unique_citing_affiliations': 'Unique Citing Affiliations',
        'unique_citing_countries': 'Unique Citing Countries',
        'unique_citing_journals': 'Unique Citing Journals',
        'unique_citing_publishers': 'Unique Citing Publishers',
        'open_access_breakdown': 'Open Access Breakdown',
        'gold': 'Gold',
        'hybrid': 'Hybrid',
        'green': 'Green',
        'bronze': 'Bronze',
        'closed': 'Closed',
        'unknown': 'Unknown',
        'author_analysis': 'Author Analysis',
        'top_affiliations': 'Top Affiliations',
        'geographic_analysis': 'Geographic Analysis',
        'countries_per_publication': 'Countries per Publication (Collaboration Level)',
        'authors_per_country': 'Authors per Country (Individual Distribution)',
        'collaboration_patterns': 'Collaboration Patterns',
        'single_country': 'Single-Country',
        'international': 'International',
        'collaboration_couples': 'Collaboration Couples',
        'collaboration_couple': 'Collaboration Couple',
        'frequency': 'Frequency',
        'citation_analysis': 'Citation Analysis',
        'citation_dynamics': 'Citation Dynamics by Year',
        'cumulative_citations': 'Cumulative Citations',
        'citation_heatmap': 'Citation Network Heatmap',
        'most_cited_publications': 'Most Cited Publications',
        'citing_works_analysis': 'Citing Works Analysis',
        'total_citing_works': 'Total Citing Works',
        'top_citing_authors': 'Top Citing Authors',
        'top_citing_affiliations': 'Top Citing Affiliations',
        'top_citing_countries': 'Top Citing Countries',
        'top_citing_journals': 'Top Citing Journals',
        'top_citing_publishers': 'Top Citing Publishers',
        'topics_analysis': 'Topics Analysis',
        'topics_overview': 'Topics Overview',
        'top_topics_by_citations': 'Top Topics by Citations',
        'detailed_citations': 'Detailed Citations',
        'all_publications': 'All Publications',
        'filter_by_title': 'Filter by Title Word(s)',
        'filter_by_year': 'Filter by Year',
        'filter_by_author': 'Filter by Author',
        'filter_by_affiliation': 'Filter by Affiliation',
        'filter_by_citations_min': 'Filter by Citations (min)',
        'show_citations': 'Show Citations',
        'rank': 'Rank',
        'authors': 'Authors',
        'orcid': 'ORCID',
        'affiliations': 'Affiliations',
        'countries': 'Countries',
        'publications': 'Publications',
        'citations': 'Citations',
        'citation_year': 'Citation Year',
        'citations_count': 'Citations Count',
        'citation_lag': 'Citation Lag',
        'first_citation_stats': 'First Citation Statistics',
        'min': 'Min',
        'max': 'Max',
        'average': 'Average',
        'median': 'Median',
        'citing_journal': 'Citing Journal',
        'citing_publisher': 'Citing Publisher',
        'topics_count': 'Topics',
        'subtopics_count': 'Subtopics',
        'fields_count': 'Fields',
        'domains_count': 'Domains',
        'concepts_count': 'Concepts',
        'analyzed_count': 'Analyzed Count',
        'citing_count': 'Citing Count',
        'analyzed_norm_count': 'Analyzed Norm Count',
        'citing_norm_count': 'Citing Norm Count',
        'total_norm_count': 'Total Norm Count',
        'first_year': 'First Year',
        'peak_year': 'Peak Year',
        'publication_year': 'Publication Year',
        'title': 'Title',
        'year': 'Year',
        'doi': 'DOI',
        'citations_per_year': 'Citations/Year',
        'journal': 'Journal',
        'overview': 'Overview',
        'analyzed_articles': 'Analyzed Articles',
        'citing_works': 'Citing Works',
        'topics_analysis_title': 'Topics Analysis',
        'article': 'Article',
        'articles_count': 'Articles',
        'download_hint': 'Click "Download HTML Report" for full report',
        'report_preview': 'HTML Report Preview',
        'no_publications_found': 'No publications found for this ISSN and period',
        'error_occurred': 'Error occurred',
        'select_language': 'Select language',
        'theme_presets_label': 'Theme presets',
        'primary_color_label': 'Primary color',
        'secondary_color_label': 'Secondary color',
        'analysis_progress': 'Analysis Progress',
        'loading_data': 'Loading data',
        'analyzing_data': 'Analyzing data',
        'generating_viz': 'Generating visualizations',
        'publication': 'Publication',
        'publication_date': 'Publication Date',
        'citing_date': 'Citing Date',
        'author_count': 'Author Count',
        'affiliation_count': 'Affiliation Count',
        'country_count': 'Country Count',
        'journal_name': 'Journal Name',
        'publisher_name': 'Publisher',
        'topic': 'Topic',
        'subtopic': 'Subtopic',
        'field': 'Field',
        'domain': 'Domain',
        'concept': 'Concept',
        'source_data': 'Source: OpenAlex',
        'generated_on': 'Generated',
    },
    'ru': {
        'app_title': 'Расширенный инструмент анализа журналов',
        'app_icon': '📊',
        'settings': '⚙️ Настройки',
        'language': '🌐 Язык',
        'language_en': 'Английский',
        'language_ru': 'Русский',
        'color_theme': '🎨 Цветовая тема',
        'preset_themes': '🎨 Пресеты тем',
        'use_preset': 'Использовать пресет',
        'select_color': '🎨 Выберите основной цвет',
        'primary': 'Основной',
        'secondary': 'Дополнительный',
        'upload_logo': 'Загрузить логотип журнала (опционально)',
        'logo_help': 'Логотип будет отображаться в отчетах',
        'journal_analysis': '📊 Анализ журнала',
        'issn_input': 'ISSN номер',
        'issn_placeholder': '0028-0836 или 00280836',
        'issn_help': 'Введите ISSN анализируемого журнала',
        'period_input': 'Период анализа',
        'period_placeholder': '2020-2023 или 2020,2021,2022',
        'period_help': 'Формат: ГГГГ-ГГГГ (диапазон) или ГГГГ,ГГГГ (список) или ГГГГ (один год)',
        'workers_count': 'Параллельных потоков',
        'workers_help': 'Количество параллельных потоков для сбора цитирований (4-12)',
        'analyze_button': '🚀 Анализировать журнал',
        'analyzing_articles': '📚 Загрузка статей журнала...',
        'fetching_citations': '⚡ Сбор цитирующих работ...',
        'no_issn': '⚠️ Введите ISSN',
        'no_period': '⚠️ Введите период анализа',
        'analysis_complete': '✅ Анализ завершен!',
        'download_report': '💾 Скачать HTML отчет',
        'generating_report': 'Генерация HTML отчета...',
        'no_data': '👈 Загрузите данные и нажмите "Анализировать журнал"',
        'footer': '© Advanced Journal Analysis Tool / Created by daM / Chimica Techno Acta',
        'journal_url': 'https://chimicatechnoacta.ru',
        'total_publications': 'Всего публикаций',
        'total_citations': 'Всего цитирований',
        'h_index': 'h-индекс',
        'g_index': 'g-индекс',
        'i10_index': 'i10-индекс',
        'i100_index': 'i100-индекс',
        'avg_citations': 'Среднее цитирований',
        'open_access': 'Открытый доступ',
        'active_years': 'Активных лет',
        'unique_authors': 'Уникальных авторов',
        'unique_affiliations': 'Уникальных аффилиаций',
        'unique_countries': 'Уникальных стран',
        'avg_authors_per_paper': 'Среднее авторов/статья',
        'avg_affiliations_per_paper': 'Среднее аффилиаций/статья',
        'avg_countries_per_paper': 'Среднее стран/статья',
        'international_collaboration_rate': 'Доля международных коллабораций',
        'unique_citing_authors': 'Уникальных цитирующих авторов',
        'unique_citing_affiliations': 'Уникальных цитирующих аффилиаций',
        'unique_citing_countries': 'Уникальных цитирующих стран',
        'unique_citing_journals': 'Уникальных цитирующих журналов',
        'unique_citing_publishers': 'Уникальных цитирующих издательств',
        'open_access_breakdown': 'Разбивка по открытому доступу',
        'gold': 'Золотой',
        'hybrid': 'Гибридный',
        'green': 'Зеленый',
        'bronze': 'Бронзовый',
        'closed': 'Закрытый',
        'unknown': 'Неизвестный',
        'author_analysis': 'Анализ авторов',
        'top_affiliations': 'Топ аффилиаций',
        'geographic_analysis': 'Географический анализ',
        'countries_per_publication': 'Стран на публикацию (уровень коллабораций)',
        'authors_per_country': 'Авторов по странам (индивидуальное распределение)',
        'collaboration_patterns': 'Модели коллабораций',
        'single_country': 'Внутристрановые',
        'international': 'Международные',
        'collaboration_couples': 'Пары коллабораций',
        'collaboration_couple': 'Пара стран',
        'frequency': 'Частота',
        'citation_analysis': 'Анализ цитирований',
        'citation_dynamics': 'Динамика цитирований по годам',
        'cumulative_citations': 'Накопленные цитирования',
        'citation_heatmap': 'Тепловая карта цитирований',
        'most_cited_publications': 'Самые цитируемые публикации',
        'citing_works_analysis': 'Анализ цитирующих работ',
        'total_citing_works': 'Всего цитирующих работ',
        'top_citing_authors': 'Топ цитирующих авторов',
        'top_citing_affiliations': 'Топ цитирующих аффилиаций',
        'top_citing_countries': 'Топ цитирующих стран',
        'top_citing_journals': 'Топ цитирующих журналов',
        'top_citing_publishers': 'Топ цитирующих издательств',
        'topics_analysis': 'Тематический анализ',
        'topics_overview': 'Обзор тем',
        'top_topics_by_citations': 'Топ тем по цитированиям',
        'detailed_citations': 'Детальные цитирования',
        'all_publications': 'Все публикации',
        'filter_by_title': 'Фильтр по словам в названии',
        'filter_by_year': 'Фильтр по году',
        'filter_by_author': 'Фильтр по автору',
        'filter_by_affiliation': 'Фильтр по аффилиации',
        'filter_by_citations_min': 'Фильтр по цитированиям (мин)',
        'show_citations': 'Показать цитирования',
        'rank': 'Ранг',
        'authors': 'Авторы',
        'orcid': 'ORCID',
        'affiliations': 'Аффилиации',
        'countries': 'Страны',
        'publications': 'Публикаций',
        'citations': 'Цитирований',
        'citation_year': 'Год цитирования',
        'citations_count': 'Количество цитирований',
        'citation_lag': 'Задержка цитирования',
        'first_citation_stats': 'Статистика первого цитирования',
        'min': 'Мин',
        'max': 'Макс',
        'average': 'Среднее',
        'median': 'Медиана',
        'citing_journal': 'Цитирующий журнал',
        'citing_publisher': 'Цитирующее издательство',
        'topics_count': 'Темы',
        'subtopics_count': 'Подтемы',
        'fields_count': 'Области',
        'domains_count': 'Домены',
        'concepts_count': 'Концепты',
        'analyzed_count': 'Количество в анализируемых',
        'citing_count': 'Количество в цитирующих',
        'analyzed_norm_count': 'Норм. количество в анализируемых',
        'citing_norm_count': 'Норм. количество в цитирующих',
        'total_norm_count': 'Общее норм. количество',
        'first_year': 'Первый год',
        'peak_year': 'Пиковый год',
        'publication_year': 'Год публикации',
        'title': 'Название',
        'year': 'Год',
        'doi': 'DOI',
        'citations_per_year': 'Цитирований/год',
        'journal': 'Журнал',
        'overview': 'Обзор',
        'analyzed_articles': 'Анализируемые статьи',
        'citing_works': 'Цитирующие работы',
        'topics_analysis_title': 'Тематический анализ',
        'article': 'Статья',
        'articles_count': 'Статей',
        'download_hint': 'Нажмите "Скачать HTML отчет" для полного отчета',
        'report_preview': 'Предпросмотр HTML отчета',
        'no_publications_found': 'Публикации не найдены для этого ISSN и периода',
        'error_occurred': 'Произошла ошибка',
        'select_language': 'Выберите язык',
        'theme_presets_label': 'Пресеты тем',
        'primary_color_label': 'Основной цвет',
        'secondary_color_label': 'Дополнительный цвет',
        'analysis_progress': 'Прогресс анализа',
        'loading_data': 'Загрузка данных',
        'analyzing_data': 'Анализ данных',
        'generating_viz': 'Генерация визуализаций',
        'publication': 'Публикация',
        'publication_date': 'Дата публикации',
        'citing_date': 'Дата цитирования',
        'author_count': 'Количество авторов',
        'affiliation_count': 'Количество аффилиаций',
        'country_count': 'Количество стран',
        'journal_name': 'Название журнала',
        'publisher_name': 'Издательство',
        'topic': 'Тема',
        'subtopic': 'Подтема',
        'field': 'Область',
        'domain': 'Домен',
        'concept': 'Концепт',
        'source_data': 'Источник: OpenAlex',
        'generated_on': 'Сгенерировано',
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
# COLOR UTILITIES FOR DYNAMIC THEMES
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

def get_analogous_colors(hex_color: str, count: int = 2) -> List[str]:
    """Generate analogous colors"""
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

def get_contrast_color(hex_color: str) -> str:
    """Get contrasting color (black or white) for text on a colored background"""
    rgb = hex_to_rgb(hex_color)
    luminance = (0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]) / 255
    return '#FFFFFF' if luminance < 0.5 else '#000000'

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
        
        .color-preview {{
            display: inline-block;
            width: 30px;
            height: 30px;
            border-radius: 50%;
            margin-left: 10px;
            vertical-align: middle;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }}
        
        .color-preview:hover {{
            transform: scale(1.1);
        }}
        
        .complementary-preview {{
            display: inline-block;
            width: 30px;
            height: 30px;
            border-radius: 50%;
            margin-left: 10px;
            vertical-align: middle;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .theme-info {{
            background: var(--hover-light);
            border-radius: 10px;
            padding: 12px;
            margin-top: 15px;
            font-size: 12px;
            text-align: center;
        }}
    </style>
    """
    st.markdown(theme_css, unsafe_allow_html=True)

# ============================================
# НАСТРОЙКА НАУЧНОГО СТИЛЯ ДЛЯ ГРАФИКОВ
# ============================================

def apply_scientific_style():
    """Улучшенный научный стиль для matplotlib"""
    try:
        plt.style.use('seaborn-v0_8-whitegrid')
    except:
        try:
            plt.style.use('seaborn-whitegrid')
        except:
            pass
    
    plt.rcParams.update({
        'font.size': 11,
        'font.family': 'serif',
        'font.serif': ['Times New Roman', 'DejaVu Serif', 'Computer Modern Roman'],
        'mathtext.fontset': 'stix',
        'axes.labelsize': 12,
        'axes.labelweight': 'bold',
        'axes.titlesize': 13,
        'axes.titleweight': 'bold',
        'axes.facecolor': '#FFFFFF',
        'axes.edgecolor': '#000000',
        'axes.linewidth': 1.5,
        'axes.spines.top': False,
        'axes.spines.right': False,
        'axes.grid': True,
        'grid.alpha': 0.3,
        'grid.linestyle': '--',
        'xtick.color': '#000000',
        'ytick.color': '#000000',
        'xtick.labelsize': 11,
        'ytick.labelsize': 11,
        'xtick.direction': 'in',
        'ytick.direction': 'in',
        'xtick.major.size': 7,
        'xtick.major.width': 1.5,
        'ytick.major.size': 7,
        'ytick.major.width': 1.5,
        'xtick.minor.size': 3,
        'xtick.minor.width': 1.0,
        'ytick.minor.size': 3,
        'ytick.minor.width': 1.0,
        'legend.fontsize': 10,
        'legend.frameon': True,
        'legend.framealpha': 0.9,
        'legend.edgecolor': '#000000',
        'legend.fancybox': False,
        'legend.borderaxespad': 0.5,
        'legend.handlelength': 1.5,
        'legend.handletextpad': 0.8,
        'figure.dpi': 300,
        'savefig.dpi': 300,
        'savefig.bbox': 'tight',
        'savefig.pad_inches': 0.05,
        'figure.facecolor': 'white',
        'figure.constrained_layout.use': True,
        'figure.figsize': (8, 6),
        'lines.linewidth': 2,
        'lines.markersize': 7,
        'lines.markeredgewidth': 1.0,
        'errorbar.capsize': 3,
        'pdf.fonttype': 42,
        'ps.fonttype': 42,
    })

apply_scientific_style()

# ============================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================

def normalize_issn(issn_str: str) -> str:
    """Нормализует ISSN (удаляет нецифровые символы, добавляет дефис)"""
    cleaned = re.sub(r'[^0-9Xx]', '', str(issn_str).strip())
    if len(cleaned) == 8:
        return f"{cleaned[:4]}-{cleaned[4:]}".upper()
    return cleaned.upper()

def parse_period(period_str: str):
    """Парсит период из строки. Возвращает список годов или диапазон"""
    period_str = period_str.strip()
    
    if ',' in period_str:
        years = [int(y.strip()) for y in period_str.split(',') if y.strip().isdigit()]
        return years
    elif '-' in period_str:
        parts = period_str.split('-')
        if len(parts) == 2:
            start = int(parts[0].strip())
            end = int(parts[1].strip())
            return (start, end)
    else:
        try:
            year = int(period_str)
            return year
        except:
            pass
    
    return None

def format_year_filter(period):
    """Форматирует период для фильтра OpenAlex"""
    if isinstance(period, list):
        return '|'.join(f"publication_year:{y}" for y in period)
    elif isinstance(period, tuple) and len(period) == 2:
        return f"publication_year:{period[0]}-{period[1]}"
    else:
        return f"publication_year:{period}"

def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def safe_get(data, *keys, default=None):
    """Безопасное получение значения из вложенного словаря"""
    for key in keys:
        if isinstance(data, dict):
            data = data.get(key, default)
        else:
            return default
    return data

# ============================================
# МОДУЛЬ СБОРА ДАННЫХ (НА ОСНОВЕ УСКОРЕННОГО КОДА)
# ============================================

class JournalAnalyzer:
    """Класс для анализа журнала по ISSN"""
    
    def __init__(self, issn: str, period, max_workers: int = 8):
        self.issn = normalize_issn(issn)
        self.period = period
        self.max_workers = max_workers
        self.articles = []
        self.citations = {}  # article_id -> list of citing works
        self.all_citing_works = []  # все цитирующие работы
        self.analysis_complete = False
        self.lock = Lock()
        
    def smart_get(self, url: str, params: dict, retries: int = MAX_RETRIES) -> dict:
        """Выполняет GET запрос с защитой от 429 и повторными попытками"""
        for attempt in range(retries):
            try:
                with self.lock:
                    time.sleep(random.uniform(0.1, BASE_DELAY))
                
                resp = requests.get(url, params=params, timeout=25)
                
                if resp.status_code == 429:
                    wait = int(resp.headers.get("Retry-After", 2 ** attempt + 1))
                    time.sleep(wait + random.uniform(0.5, 1.5))
                    continue
                    
                if resp.status_code == 200:
                    return resp.json()
                
                time.sleep(1 * (2 ** attempt))
                
            except:
                time.sleep(1.5 * (2 ** attempt))
        return None
    
    def fetch_articles(self, progress_callback=None) -> List[Dict]:
        """Загружает статьи журнала за указанный период"""
        articles = []
        cursor = "*"
        base_url = "https://api.openalex.org/works"
        year_filter = format_year_filter(self.period)
        
        page = 0
        while True:
            page += 1
            params = {
                "filter": f"primary_location.source.issn:{self.issn},{year_filter}",
                "per_page": 200,
                "select": "id,doi,title,publication_year,publication_date,cited_by_count,open_access,authorships,primary_location,topics,concepts",
                "cursor": cursor
            }
            
            if progress_callback:
                progress_callback(page, "loading")
            
            data = self.smart_get(base_url, params)
            if not data or not data.get("results"):
                break
                
            for w in data["results"]:
                # Парсим статью
                article = self._parse_article(w)
                if article:
                    articles.append(article)
            
            cursor = data.get("meta", {}).get("next_cursor")
            if not cursor:
                break
        
        self.articles = articles
        return articles
    
    def _parse_article(self, work: Dict) -> Dict:
        """Парсит статью из OpenAlex"""
        try:
            # Основная информация
            article = {
                'id': work.get('id', '').replace('https://openalex.org/', ''),
                'doi': work.get('doi', '').replace('https://doi.org/', ''),
                'title': work.get('title', 'No title'),
                'publication_year': work.get('publication_year'),
                'publication_date': work.get('publication_date', ''),
                'cited_by_count': work.get('cited_by_count', 0),
                'is_oa': False,
                'oa_status': 'unknown'
            }
            
            # Open Access
            oa = work.get('open_access', {})
            if oa:
                article['is_oa'] = oa.get('is_oa', False)
                article['oa_status'] = oa.get('oa_status', 'unknown')
            
            # Authors, Affiliations, Countries
            authors = []
            affiliations = []
            countries = []
            author_with_orcid = []
            
            for auth in work.get('authorships', []):
                author_data = auth.get('author', {})
                author_name = author_data.get('display_name', '')
                author_orcid = author_data.get('orcid', '').replace('https://orcid.org/', '')
                
                if author_name:
                    authors.append(author_name)
                    if author_orcid:
                        author_with_orcid.append({
                            'name': author_name,
                            'orcid': author_orcid
                        })
                
                # Аффилиации
                for inst in auth.get('institutions', []):
                    inst_name = inst.get('display_name', '')
                    inst_country = inst.get('country_code', '')
                    if inst_name:
                        affiliations.append(inst_name)
                        if inst_country and inst_country not in countries:
                            countries.append(inst_country)
            
            article['authors'] = authors
            article['author_count'] = len(authors)
            article['authors_with_orcid'] = author_with_orcid
            article['affiliations'] = list(set(affiliations))
            article['affiliation_count'] = len(set(affiliations))
            article['countries'] = countries
            article['country_count'] = len(set(countries))
            
            # Journal
            primary_location = work.get('primary_location', {})
            source = primary_location.get('source', {})
            article['journal_name'] = source.get('display_name', 'Unknown')
            article['publisher'] = source.get('host_organization_name', 'Unknown')
            
            # Topics
            topics = []
            subtopics = []
            fields = []
            domains = []
            concepts = []
            
            # Primary topic
            primary_topic = work.get('primary_topic', {})
            if primary_topic:
                if primary_topic.get('display_name'):
                    topics.append(primary_topic['display_name'])
                if primary_topic.get('subfield', {}).get('display_name'):
                    subtopics.append(primary_topic['subfield']['display_name'])
                if primary_topic.get('field', {}).get('display_name'):
                    fields.append(primary_topic['field']['display_name'])
                if primary_topic.get('domain', {}).get('display_name'):
                    domains.append(primary_topic['domain']['display_name'])
            
            # All topics
            for topic in work.get('topics', []):
                if topic.get('display_name'):
                    topics.append(topic['display_name'])
                if topic.get('subfield', {}).get('display_name'):
                    subtopics.append(topic['subfield']['display_name'])
                if topic.get('field', {}).get('display_name'):
                    fields.append(topic['field']['display_name'])
                if topic.get('domain', {}).get('display_name'):
                    domains.append(topic['domain']['display_name'])
            
            # Concepts
            for concept in work.get('concepts', []):
                if concept.get('display_name'):
                    concepts.append(concept['display_name'])
            
            article['topics'] = list(set(topics))
            article['subtopics'] = list(set(subtopics))
            article['fields'] = list(set(fields))
            article['domains'] = list(set(domains))
            article['concepts'] = list(set(concepts))
            
            return article
            
        except Exception as e:
            if SHOW_DEBUG_LOGS:
                print(f"⚠️ Ошибка парсинга статьи: {e}")
            return None
    
    def get_citing_dois(self, oa_id: str) -> List[str]:
        """Получает список DOI цитирующих работ для одной статьи"""
        citing = []
        cursor = "*"
        base_url = "https://api.openalex.org/works"
        
        for _ in range(MAX_PAGINATION_PAGES):
            data = self.smart_get(base_url, {
                "filter": f"cites:{oa_id}",
                "per_page": 200,
                "select": "id,doi,title,publication_year,publication_date,authorships,primary_location,topics,concepts",
                "cursor": cursor
            })
            
            if not data:
                break
            results = data.get("results", [])
            if not results:
                break
                
            for item in results:
                doi = item.get("doi")
                if doi:
                    citing.append(doi.replace("https://doi.org/", ""))
            
            cursor = data.get("meta", {}).get("next_cursor")
            if not cursor:
                break
        
        return citing[:MAX_CITING_PER_PAPER]
    
    def _parse_citing_work(self, work: Dict) -> Dict:
        """Парсит цитирующую работу из OpenAlex"""
        try:
            citing_work = {
                'id': work.get('id', '').replace('https://openalex.org/', ''),
                'doi': work.get('doi', '').replace('https://doi.org/', ''),
                'title': work.get('title', 'No title'),
                'publication_year': work.get('publication_year'),
                'publication_date': work.get('publication_date', ''),
            }
            
            # Authors
            authors = []
            for auth in work.get('authorships', []):
                author_data = auth.get('author', {})
                author_name = author_data.get('display_name', '')
                if author_name:
                    authors.append(author_name)
            citing_work['authors'] = authors
            
            # Affiliations
            affiliations = []
            for auth in work.get('authorships', []):
                for inst in auth.get('institutions', []):
                    inst_name = inst.get('display_name', '')
                    if inst_name:
                        affiliations.append(inst_name)
            citing_work['affiliations'] = list(set(affiliations))
            
            # Countries
            countries = []
            for auth in work.get('authorships', []):
                for inst in auth.get('institutions', []):
                    country = inst.get('country_code', '')
                    if country and country not in countries:
                        countries.append(country)
            citing_work['countries'] = countries
            
            # Journal
            primary_location = work.get('primary_location', {})
            source = primary_location.get('source', {})
            citing_work['journal_name'] = source.get('display_name', 'Unknown')
            citing_work['publisher'] = source.get('host_organization_name', 'Unknown')
            
            # Topics
            topics = []
            subtopics = []
            fields = []
            domains = []
            concepts = []
            
            primary_topic = work.get('primary_topic', {})
            if primary_topic:
                if primary_topic.get('display_name'):
                    topics.append(primary_topic['display_name'])
                if primary_topic.get('subfield', {}).get('display_name'):
                    subtopics.append(primary_topic['subfield']['display_name'])
                if primary_topic.get('field', {}).get('display_name'):
                    fields.append(primary_topic['field']['display_name'])
                if primary_topic.get('domain', {}).get('display_name'):
                    domains.append(primary_topic['domain']['display_name'])
            
            for topic in work.get('topics', []):
                if topic.get('display_name'):
                    topics.append(topic['display_name'])
                if topic.get('subfield', {}).get('display_name'):
                    subtopics.append(topic['subfield']['display_name'])
                if topic.get('field', {}).get('display_name'):
                    fields.append(topic['field']['display_name'])
                if topic.get('domain', {}).get('display_name'):
                    domains.append(topic['domain']['display_name'])
            
            for concept in work.get('concepts', []):
                if concept.get('display_name'):
                    concepts.append(concept['display_name'])
            
            citing_work['topics'] = list(set(topics))
            citing_work['subtopics'] = list(set(subtopics))
            citing_work['fields'] = list(set(fields))
            citing_work['domains'] = list(set(domains))
            citing_work['concepts'] = list(set(concepts))
            
            return citing_work
            
        except Exception as e:
            if SHOW_DEBUG_LOGS:
                print(f"⚠️ Ошибка парсинга цитирующей работы: {e}")
            return None
    
    def fetch_citing_works_parallel(self, progress_callback=None) -> Dict:
        """Параллельный сбор цитирующих работ"""
        if not self.articles:
            return {}
        
        citations = {}
        all_citing_works = []
        futures = {}
        
        # Собираем задачи для параллельного выполнения
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            for article in self.articles:
                if article['cited_by_count'] > 0 and article['doi']:
                    future = executor.submit(self.get_citing_dois, article['id'])
                    futures[future] = article['id']
            
            total = len(futures)
            completed = 0
            
            for future in as_completed(futures):
                article_id = futures[future]
                completed += 1
                
                if progress_callback:
                    progress_callback(completed, total)
                
                try:
                    citing_dois = future.result()
                    citations[article_id] = citing_dois
                    
                    # Парсим детальную информацию о цитирующих работах
                    for doi in citing_dois:
                        # Здесь нужно получить полную информацию о цитирующей работе
                        # Для экономии запросов можно сделать батч-запрос
                        pass
                        
                except Exception as e:
                    if SHOW_DEBUG_LOGS:
                        print(f"⚠️ Ошибка получения цитирований для {article_id}: {e}")
                    citations[article_id] = []
        
        self.citations = citations
        
        # Теперь собираем детальную информацию о всех цитирующих работах
        # Делаем это батчами для экономии запросов
        all_doi_to_fetch = []
        for citing_dois in citations.values():
            all_doi_to_fetch.extend(citing_dois)
        
        # Уникальные DOI
        unique_dois = list(set(all_doi_to_fetch))
        
        if SHOW_DEBUG_LOGS:
            print(f"📊 Уникальных цитирующих DOI для детального парсинга: {len(unique_dois)}")
        
        # Загружаем детальную информацию батчами
        citing_works_map = {}
        for batch in chunks(unique_dois, 50):
            doi_query = '|'.join(batch[:50])
            params = {
                "filter": f"doi:{doi_query}",
                "per_page": len(batch)
            }
            url = "https://api.openalex.org/works"
            data = self.smart_get(url, params)
            
            if data and data.get('results'):
                for work in data['results']:
                    parsed = self._parse_citing_work(work)
                    if parsed and parsed.get('doi'):
                        citing_works_map[parsed['doi']] = parsed
                        all_citing_works.append(parsed)
            
            time.sleep(BASE_DELAY)
        
        self.all_citing_works = all_citing_works
        
        # Обновляем citations с полной информацией
        detailed_citations = {}
        for article_id, citing_dois in citations.items():
            detailed_citations[article_id] = []
            for doi in citing_dois:
                if doi in citing_works_map:
                    detailed_citations[article_id].append(citing_works_map[doi])
        
        self.citations = detailed_citations
        
        return self.citations
    
    def analyze(self, progress_callback=None) -> Dict:
        """Полный анализ журнала"""
        if not self.articles:
            return None
        
        if progress_callback:
            progress_callback(0, "start")
        
        # Сбор цитирований
        if progress_callback:
            progress_callback(0, "citing")
        
        self.fetch_citing_works_parallel(progress_callback)
        
        self.analysis_complete = True
        
        return self.get_report_data()
    
    def get_report_data(self) -> Dict:
        """Возвращает данные для отчета"""
        return {
            'articles': self.articles,
            'citations': self.citations,
            'all_citing_works': self.all_citing_works,
            'issn': self.issn,
            'period': self.period,
            'total_articles': len(self.articles),
            'total_citing_works': len(self.all_citing_works)
        }

# ============================================
# МОДУЛЬ РАСЧЕТА МЕТРИК
# ============================================

class MetricsCalculator:
    """Класс для расчета метрик на основе данных анализа"""
    
    def __init__(self, articles: List[Dict], citations: Dict, all_citing_works: List[Dict]):
        self.articles = articles
        self.citations = citations
        self.all_citing_works = all_citing_works
        
    def calculate_basic_metrics(self) -> Dict:
        """Расчет основных метрик"""
        metrics = {}
        
        # Total publications
        metrics['total_publications'] = len(self.articles)
        
        # Total citations
        total_citations = sum(a.get('cited_by_count', 0) for a in self.articles)
        metrics['total_citations'] = total_citations
        
        # Citations list
        citations_list = [a.get('cited_by_count', 0) for a in self.articles]
        citations_sorted = sorted([c for c in citations_list if c > 0], reverse=True)
        
        # h-index
        h_index = 0
        for i, c in enumerate(citations_sorted, 1):
            if c >= i:
                h_index = i
            else:
                break
        metrics['h_index'] = h_index
        
        # g-index
        total_citations_sorted = 0
        g_index = 0
        for i, c in enumerate(citations_sorted, 1):
            total_citations_sorted += c
            if total_citations_sorted >= i**2:
                g_index = i
        metrics['g_index'] = g_index
        
        # i10-index
        metrics['i10_index'] = sum(1 for c in citations_list if c >= 10)
        
        # i100-index
        metrics['i100_index'] = sum(1 for c in citations_list if c >= 100)
        
        # Avg citations
        metrics['avg_citations'] = sum(citations_list) / len(citations_list) if citations_list else 0
        
        # Open Access breakdown
        oa_statuses = {}
        for a in self.articles:
            status = a.get('oa_status', 'unknown')
            oa_statuses[status] = oa_statuses.get(status, 0) + 1
        metrics['open_access_breakdown'] = oa_statuses
        
        # Active years
        years = [a.get('publication_year') for a in self.articles if a.get('publication_year')]
        metrics['active_years'] = len(set(years)) if years else 0
        metrics['min_year'] = min(years) if years else None
        metrics['max_year'] = max(years) if years else None
        
        # Unique authors
        all_authors = []
        for a in self.articles:
            all_authors.extend(a.get('authors', []))
        metrics['unique_authors'] = len(set(all_authors))
        
        # Unique affiliations
        all_affiliations = []
        for a in self.articles:
            all_affiliations.extend(a.get('affiliations', []))
        metrics['unique_affiliations'] = len(set(all_affiliations))
        
        # Unique countries
        all_countries = []
        for a in self.articles:
            all_countries.extend(a.get('countries', []))
        metrics['unique_countries'] = len(set(all_countries))
        
        # Avg authors per paper
        metrics['avg_authors_per_paper'] = sum(a.get('author_count', 0) for a in self.articles) / len(self.articles) if self.articles else 0
        
        # Avg affiliations per paper
        metrics['avg_affiliations_per_paper'] = sum(a.get('affiliation_count', 0) for a in self.articles) / len(self.articles) if self.articles else 0
        
        # Avg countries per paper
        metrics['avg_countries_per_paper'] = sum(a.get('country_count', 0) for a in self.articles) / len(self.articles) if self.articles else 0
        
        # International collaboration rate
        international_papers = 0
        for a in self.articles:
            if a.get('country_count', 0) > 1:
                international_papers += 1
        metrics['international_collaboration_rate'] = international_papers / len(self.articles) if self.articles else 0
        
        # Citing metrics
        citing_authors = []
        citing_affiliations = []
        citing_countries = []
        citing_journals = []
        citing_publishers = []
        
        for citing in self.all_citing_works:
            citing_authors.extend(citing.get('authors', []))
            citing_affiliations.extend(citing.get('affiliations', []))
            citing_countries.extend(citing.get('countries', []))
            citing_journals.append(citing.get('journal_name', ''))
            citing_publishers.append(citing.get('publisher', ''))
        
        metrics['unique_citing_authors'] = len(set(citing_authors))
        metrics['unique_citing_affiliations'] = len(set(citing_affiliations))
        metrics['unique_citing_countries'] = len(set(citing_countries))
        metrics['unique_citing_journals'] = len(set(citing_journals))
        metrics['unique_citing_publishers'] = len(set(citing_publishers))
        metrics['total_citing_works'] = len(self.all_citing_works)
        
        return metrics
    
    def calculate_author_stats(self) -> List[Dict]:
        """Расчет статистики по авторам"""
        author_stats = {}
        
        for a in self.articles:
            for idx, author_name in enumerate(a.get('authors', [])):
                if author_name not in author_stats:
                    author_stats[author_name] = {
                        'name': author_name,
                        'orcid': '',
                        'affiliations': [],
                        'countries': [],
                        'publications': 0,
                        'citations': 0
                    }
                
                author_stats[author_name]['publications'] += 1
                author_stats[author_name]['citations'] += a.get('cited_by_count', 0)
                
                if a.get('authors_with_orcid') and idx < len(a.get('authors_with_orcid', [])):
                    if a['authors_with_orcid'][idx].get('orcid'):
                        author_stats[author_name]['orcid'] = a['authors_with_orcid'][idx]['orcid']
                
                if a.get('affiliations') and idx < len(a.get('affiliations', [])):
                    author_stats[author_name]['affiliations'].extend(a['affiliations'])
                
                if a.get('countries') and idx < len(a.get('countries', [])):
                    author_stats[author_name]['countries'].extend(a['countries'])
        
        # Уникальные аффилиации и страны
        for name, stats in author_stats.items():
            stats['affiliations'] = list(set(stats['affiliations']))[:3]
            stats['countries'] = list(set(stats['countries']))
        
        # Сортировка по цитированиям
        return sorted(author_stats.values(), key=lambda x: x['citations'], reverse=True)
    
    def calculate_top_affiliations(self, top_n: int = 10) -> Dict:
        """Расчет топ аффилиаций"""
        aff_count = defaultdict(int)
        
        for a in self.articles:
            for aff in a.get('affiliations', []):
                aff_count[aff] += 1
        
        return dict(sorted(aff_count.items(), key=lambda x: x[1], reverse=True)[:top_n])
    
    def calculate_geographic_stats(self) -> Dict:
        """Расчет географической статистики"""
        # Countries per publication (collaboration level)
        countries_per_pub = []
        for a in self.articles:
            countries = set(a.get('countries', []))
            countries_per_pub.append({
                'article_id': a.get('id'),
                'countries': list(countries),
                'count': len(countries)
            })
        
        # Authors per country (individual distribution)
        authors_per_country = defaultdict(int)
        for a in self.articles:
            for idx, author in enumerate(a.get('authors', [])):
                if idx < len(a.get('countries', [])):
                    country = a['countries'][idx]
                    if country:
                        authors_per_country[country] += 1
        
        # Collaboration patterns
        single_country = 0
        international = 0
        for a in self.articles:
            if a.get('country_count', 0) <= 1:
                single_country += 1
            else:
                international += 1
        
        # Collaboration couples
        couple_freq = defaultdict(int)
        for a in self.articles:
            countries = sorted(set(a.get('countries', [])))
            for i in range(len(countries)):
                for j in range(i + 1, len(countries)):
                    couple = f"{countries[i]}-{countries[j]}"
                    couple_freq[couple] += 1
        
        return {
            'countries_per_pub': countries_per_pub,
            'authors_per_country': dict(authors_per_country),
            'single_country': single_country,
            'international': international,
            'collaboration_couples': dict(sorted(couple_freq.items(), key=lambda x: x[1], reverse=True)[:20])
        }
    
    def calculate_citation_dynamics(self) -> Dict:
        """Расчет динамики цитирований"""
        dynamics = defaultdict(lambda: defaultdict(int))
        citation_lags = []
        
        for article in self.articles:
            pub_year = article.get('publication_year')
            if not pub_year:
                continue
            
            article_dois = self.citations.get(article['id'], [])
            for citing in article_dois:
                cite_year = citing.get('publication_year')
                if cite_year:
                    lag = cite_year - pub_year
                    if lag >= 0:
                        dynamics[pub_year][cite_year] += 1
                        citation_lags.append(lag)
        
        # Статистика по лагу первого цитирования
        first_lag_stats = {}
        if citation_lags:
            first_lag_stats = {
                'min': min(citation_lags),
                'max': max(citation_lags),
                'avg': sum(citation_lags) / len(citation_lags),
                'median': sorted(citation_lags)[len(citation_lags) // 2]
            }
        
        return {
            'dynamics': dynamics,
            'citation_lags': citation_lags,
            'first_lag_stats': first_lag_stats
        }
    
    def calculate_cumulative_citations(self) -> Dict:
        """Расчет накопленных цитирований"""
        cumulative = defaultdict(int)
        
        for article in self.articles:
            pub_year = article.get('publication_year')
            if not pub_year:
                continue
            
            article_dois = self.citations.get(article['id'], [])
            for citing in article_dois:
                cite_year = citing.get('publication_year')
                if cite_year and cite_year >= pub_year:
                    cumulative[cite_year] += 1
        
        # Сортируем по годам
        sorted_cumulative = dict(sorted(cumulative.items()))
        
        # Накопление
        running_total = 0
        cumulative_with_running = {}
        for year, count in sorted_cumulative.items():
            running_total += count
            cumulative_with_running[year] = running_total
        
        return cumulative_with_running
    
    def calculate_heatmap_data(self) -> Dict:
        """Расчет данных для тепловой карты"""
        dynamics = self.calculate_citation_dynamics()['dynamics']
        
        pub_years = sorted(dynamics.keys())
        cite_years = sorted(set().union(*[set(d.keys()) for d in dynamics.values()]))
        
        heatmap_data = []
        for pub_year in pub_years:
            row = []
            for cite_year in cite_years:
                row.append(dynamics.get(pub_year, {}).get(cite_year, 0))
            heatmap_data.append(row)
        
        return {
            'pub_years': pub_years,
            'cite_years': cite_years,
            'data': heatmap_data
        }
    
    def calculate_most_cited(self, top_n: int = 20) -> List[Dict]:
        """Расчет самых цитируемых публикаций"""
        sorted_articles = sorted(self.articles, key=lambda x: x.get('cited_by_count', 0), reverse=True)
        most_cited = []
        
        for article in sorted_articles[:top_n]:
            authors_str = ', '.join(article.get('authors', [])[:3])
            if len(article.get('authors', [])) > 3:
                authors_str += f" +{len(article.get('authors', [])) - 3} more"
            
            most_cited.append({
                'title': article.get('title', 'No title'),
                'year': article.get('publication_year'),
                'citations': article.get('cited_by_count', 0),
                'citations_per_year': article.get('cited_by_count', 0) / max(1, 2024 - article.get('publication_year', 2024) + 1) if article.get('publication_year') else 0,
                'authors': authors_str,
                'doi': article.get('doi', '')
            })
        
        return most_cited
    
    def calculate_topics_stats(self) -> Dict:
        """Расчет статистики по темам"""
        topics_stats = defaultdict(lambda: {
            'analyzed_count': 0,
            'citing_count': 0,
            'first_year': None,
            'peak_year': None,
            'year_counts': defaultdict(int)
        })
        
        # Анализируемые статьи
        for article in self.articles:
            pub_year = article.get('publication_year')
            if not pub_year:
                continue
            
            for topic in article.get('topics', []):
                topics_stats[topic]['analyzed_count'] += 1
                topics_stats[topic]['year_counts'][pub_year] += 1
                if not topics_stats[topic]['first_year'] or pub_year < topics_stats[topic]['first_year']:
                    topics_stats[topic]['first_year'] = pub_year
        
        # Цитирующие работы
        for citing in self.all_citing_works:
            cite_year = citing.get('publication_year')
            if not cite_year:
                continue
            
            for topic in citing.get('topics', []):
                topics_stats[topic]['citing_count'] += 1
        
        # Расчет пикового года и нормализованных значений
        total_analyzed = len(self.articles)
        total_citing = len(self.all_citing_works)
        total_combined = total_analyzed + total_citing
        
        for topic, stats in topics_stats.items():
            if stats['year_counts']:
                stats['peak_year'] = max(stats['year_counts'].items(), key=lambda x: x[1])[0]
            
            stats['analyzed_norm'] = stats['analyzed_count'] / total_analyzed if total_analyzed > 0 else 0
            stats['citing_norm'] = stats['citing_count'] / total_citing if total_citing > 0 else 0
            stats['total_norm'] = (stats['analyzed_count'] + stats['citing_count']) / total_combined if total_combined > 0 else 0
        
        # Сортировка по total_norm
        return dict(sorted(topics_stats.items(), key=lambda x: x[1]['total_norm'], reverse=True))
    
    def calculate_top_citing(self, category: str = 'authors', top_n: int = 10) -> Dict:
        """Расчет топ цитирующих элементов"""
        counter = defaultdict(int)
        
        for citing in self.all_citing_works:
            if category == 'authors':
                for item in citing.get('authors', []):
                    counter[item] += 1
            elif category == 'affiliations':
                for item in citing.get('affiliations', []):
                    counter[item] += 1
            elif category == 'countries':
                for item in citing.get('countries', []):
                    counter[item] += 1
            elif category == 'journals':
                item = citing.get('journal_name', '')
                if item:
                    counter[item] += 1
            elif category == 'publishers':
                item = citing.get('publisher', '')
                if item:
                    counter[item] += 1
        
        return dict(sorted(counter.items(), key=lambda x: x[1], reverse=True)[:top_n])
    
    def calculate_top_topics_by_citations(self, category: str = 'topics', top_n: int = 10) -> Dict:
        """Расчет топ тем по цитированиям"""
        topic_citations = defaultdict(int)
        
        for article in self.articles:
            citations_count = article.get('cited_by_count', 0)
            
            if category == 'topics':
                items = article.get('topics', [])
            elif category == 'subtopics':
                items = article.get('subtopics', [])
            elif category == 'fields':
                items = article.get('fields', [])
            elif category == 'domains':
                items = article.get('domains', [])
            elif category == 'concepts':
                items = article.get('concepts', [])
            else:
                items = []
            
            for item in items:
                topic_citations[item] += citations_count
        
        return dict(sorted(topic_citations.items(), key=lambda x: x[1], reverse=True)[:top_n])
    
    def get_detailed_citations(self) -> Dict:
        """Получение детальных цитирований для каждой статьи"""
        detailed = {}
        
        for article in self.articles:
            article_id = article.get('id')
            citing_works = self.citations.get(article_id, [])
            
            if citing_works:
                citations_list = []
                for citing in citing_works:
                    # Проверяем, является ли citing словарем или строкой
                    if isinstance(citing, dict):
                        citations_list.append({
                            'citing_title': citing.get('title', 'No title'),
                            'citing_year': citing.get('publication_year'),
                            'citing_date': citing.get('publication_date', ''),
                            'citing_journal': citing.get('journal_name', 'Unknown'),
                            'citing_publisher': citing.get('publisher', 'Unknown'),
                            'citing_doi': citing.get('doi', ''),
                            'citation_lag': citing.get('publication_year', 0) - article.get('publication_year', 0) if citing.get('publication_year') and article.get('publication_year') else None,
                            'citing_authors': citing.get('authors', []),
                            'citing_countries': citing.get('countries', []),
                            'citing_topics': citing.get('topics', [])[:5]
                        })
                
                detailed[article_id] = {
                    'title': article.get('title', 'No title'),
                    'year': article.get('publication_year'),
                    'doi': article.get('doi', ''),
                    'total_citations': len(citations_list),
                    'citations': citations_list
                }
        
        return detailed
    
    def get_all_publications_data(self) -> List[Dict]:
        """Получение данных для всех публикаций (для таблицы)"""
        publications = []
        
        for article in self.articles:
            publications.append({
                'id': article.get('id'),
                'title': article.get('title', 'No title'),
                'year': article.get('publication_year'),
                'authors': ', '.join(article.get('authors', [])[:5]) + (f" +{len(article.get('authors', [])) - 5} more" if len(article.get('authors', [])) > 5 else ''),
                'affiliations': ', '.join(article.get('affiliations', [])[:3]) + (f" +{len(article.get('affiliations', [])) - 3} more" if len(article.get('affiliations', [])) > 3 else ''),
                'citations': article.get('cited_by_count', 0),
                'citations_per_year': article.get('cited_by_count', 0) / max(1, 2024 - article.get('publication_year', 2024) + 1) if article.get('publication_year') else 0,
                'doi': article.get('doi', ''),
                'journal': article.get('journal_name', 'Unknown'),
                'authors_list': article.get('authors', []),
                'affiliations_list': article.get('affiliations', []),
                'year_raw': article.get('publication_year')
            })
        
        return sorted(publications, key=lambda x: x['year'] if x['year'] else 0, reverse=True)

# ============================================
# МОДУЛЬ ГЕНЕРАЦИИ HTML ОТЧЕТА
# ============================================

def generate_journal_html_report(
    issn: str,
    period,
    articles: List[Dict],
    citations: Dict,
    all_citing_works: List[Dict],
    metrics: Dict,
    author_stats: List[Dict],
    top_affiliations: Dict,
    geographic_stats: Dict,
    citation_dynamics: Dict,
    cumulative_citations: Dict,
    heatmap_data: Dict,
    most_cited: List[Dict],
    top_citing_authors: Dict,
    top_citing_affiliations: Dict,
    top_citing_countries: Dict,
    top_citing_journals: Dict,
    top_citing_publishers: Dict,
    topics_stats: Dict,
    top_topics_by_citations: Dict,
    top_subtopics_by_citations: Dict,
    top_fields_by_citations: Dict,
    top_domains_by_citations: Dict,
    top_concepts_by_citations: Dict,
    detailed_citations: Dict,
    all_publications: List[Dict],
    logo_base64: Optional[str] = None,
    app_logo_base64: Optional[str] = None,
    theme_colors: Optional[Dict] = None,
    lang: str = 'en'
) -> str:
    """Генерирует HTML отчет для журнала"""
    
    if theme_colors is None:
        theme_colors = {
            'primary': '#667eea',
            'secondary': '#f39c12'
        }
    
    primary = theme_colors.get('primary', '#667eea')
    secondary = theme_colors.get('secondary', '#f39c12')
    
    def t(key: str, **kwargs) -> str:
        return translate(key, lang, **kwargs)
    
    # Форматирование периода для отображения
    period_str = str(period)
    if isinstance(period, tuple):
        period_str = f"{period[0]}-{period[1]}"
    elif isinstance(period, list):
        period_str = ', '.join(str(y) for y in period)
    
    # OA breakdown
    oa_breakdown = metrics.get('open_access_breakdown', {})
    oa_labels = {
        'gold': t('gold'),
        'hybrid': t('hybrid'),
        'green': t('green'),
        'bronze': t('bronze'),
        'closed': t('closed'),
        'unknown': t('unknown')
    }
    
    # Генерация строки для OA breakdown
    oa_html = ""
    for status, count in oa_breakdown.items():
        label = oa_labels.get(status, status)
        oa_html += f"""
        <div style="display: flex; justify-content: space-between; padding: 4px 0; border-bottom: 1px solid #eee;">
            <span>{label}</span>
            <span><strong>{count}</strong></span>
        </div>
        """
    
    # Author analysis table
    author_html = ""
    for idx, author in enumerate(author_stats[:20], 1):
        author_html += f"""
        <tr>
            <td>{idx}</td>
            <td><strong>{html.escape(author['name'])}</strong></td>
            <td>{author.get('orcid', '')}</td>
            <td>{', '.join(html.escape(a) for a in author.get('affiliations', [])[:3])}</td>
            <td>{', '.join(author.get('countries', []))}</td>
            <td>{author.get('publications', 0)}</td>
            <td>{author.get('citations', 0)}</td>
        </tr>
        """
    
    # Top affiliations
    top_aff_html = ""
    for aff, count in list(top_affiliations.items())[:10]:
        top_aff_html += f"""
        <tr>
            <td><strong>{html.escape(aff)}</strong></td>
            <td>{count}</td>
        </tr>
        """
    
    # Countries per publication
    countries_per_pub_html = ""
    for item in geographic_stats.get('countries_per_pub', [])[:20]:
        countries_str = ', '.join(item.get('countries', []))
        countries_per_pub_html += f"""
        <tr>
            <td>{item.get('article_id', '')[:20]}...</td>
            <td>{item.get('count', 0)}</td>
            <td>{countries_str}</td>
        </tr>
        """
    
    # Authors per country
    authors_per_country_html = ""
    for country, count in sorted(geographic_stats.get('authors_per_country', {}).items(), key=lambda x: x[1], reverse=True)[:20]:
        authors_per_country_html += f"""
        <tr>
            <td><strong>{country}</strong></td>
            <td>{count}</td>
        </tr>
        """
    
    # Collaboration patterns
    single_country = geographic_stats.get('single_country', 0)
    international = geographic_stats.get('international', 0)
    total_pubs = single_country + international
    single_pct = (single_country / total_pubs * 100) if total_pubs > 0 else 0
    intl_pct = (international / total_pubs * 100) if total_pubs > 0 else 0
    
    # Collaboration couples
    couples_html = ""
    for couple, freq in list(geographic_stats.get('collaboration_couples', {}).items())[:15]:
        couples_html += f"""
        <tr>
            <td><strong>{couple}</strong></td>
            <td>{freq}</td>
        </tr>
        """
    
    # Citation dynamics
    dynamics = citation_dynamics.get('dynamics', {})
    dynamics_html = ""
    for pub_year, cite_years in sorted(dynamics.items()):
        for cite_year, count in sorted(cite_years.items()):
            dynamics_html += f"""
            <tr>
                <td>{pub_year}</td>
                <td>{cite_year}</td>
                <td>{count}</td>
            </tr>
            """
    
    # First citation stats
    first_lag_stats = citation_dynamics.get('first_lag_stats', {})
    first_stats_html = ""
    if first_lag_stats:
        first_stats_html = f"""
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin: 10px 0;">
            <div class="metric-card"><div class="metric-value">{first_lag_stats.get('min', 0)}</div><div class="metric-label">{t('min')}</div></div>
            <div class="metric-card"><div class="metric-value">{first_lag_stats.get('max', 0)}</div><div class="metric-label">{t('max')}</div></div>
            <div class="metric-card"><div class="metric-value">{first_lag_stats.get('avg', 0):.1f}</div><div class="metric-label">{t('average')}</div></div>
            <div class="metric-card"><div class="metric-value">{first_lag_stats.get('median', 0)}</div><div class="metric-label">{t('median')}</div></div>
        </div>
        """
    
    # Cumulative citations
    cumul_html = ""
    for year, count in sorted(cumulative_citations.items()):
        cumul_html += f"""
        <tr>
            <td>{year}</td>
            <td>{count}</td>
        </tr>
        """
    
    # Heatmap
    heatmap_pub_years = heatmap_data.get('pub_years', [])
    heatmap_cite_years = heatmap_data.get('cite_years', [])
    heatmap_data_matrix = heatmap_data.get('data', [])
    
    # Находим максимальное значение для масштабирования цветов
    max_val = 0
    for row in heatmap_data_matrix:
        for val in row:
            if val > max_val:
                max_val = val
    
    heatmap_html = ""
    if heatmap_pub_years and heatmap_cite_years:
        heatmap_html = """
        <div style="overflow-x: auto; margin: 15px 0;">
            <table style="border-collapse: collapse; font-size: 13px;">
                <thead>
                    <tr>
                        <th style="padding: 8px; background: #f8f9fa; border: 1px solid #ddd;">\\</th>
        """
        
        for cite_year in heatmap_cite_years:
            heatmap_html += f'<th style="padding: 8px; background: #f8f9fa; border: 1px solid #ddd; text-align: center;">{cite_year}</th>'
        
        heatmap_html += """
                    </tr>
                </thead>
                <tbody>
        """
        
        for i, pub_year in enumerate(heatmap_pub_years):
            heatmap_html += f'<tr><td style="padding: 8px; border: 1px solid #ddd; font-weight: bold; background: #f8f9fa;">{pub_year}</td>'
            
            for j, cite_year in enumerate(heatmap_cite_years):
                val = heatmap_data_matrix[i][j] if i < len(heatmap_data_matrix) and j < len(heatmap_data_matrix[i]) else 0
                
                # Вычисляем интенсивность цвета
                intensity = val / max_val if max_val > 0 else 0
                r = int(hex_to_rgb(primary)[0] * intensity + 255 * (1 - intensity))
                g = int(hex_to_rgb(primary)[1] * intensity + 255 * (1 - intensity))
                b = int(hex_to_rgb(primary)[2] * intensity + 255 * (1 - intensity))
                color = f'rgb({r},{g},{b})'
                
                heatmap_html += f'<td style="padding: 8px; border: 1px solid #ddd; text-align: center; background-color: {color};">{val if val > 0 else "-"}</td>'
            
            heatmap_html += '</tr>'
        
        heatmap_html += """
                </tbody>
            </table>
        </div>
        """
    
    # Most cited
    most_cited_html = ""
    for idx, pub in enumerate(most_cited[:20], 1):
        most_cited_html += f"""
        <tr>
            <td>{idx}</td>
            <td class="word-wrap">{html.escape(pub['title'])}</td>
            <td>{pub['year']}</td>
            <td><span class="citation-count">{pub['citations']}</span></td>
            <td>{pub['citations_per_year']:.1f}</td>
            <td>{html.escape(pub['authors'])}</td>
            <td><a href="https://doi.org/{pub['doi']}" target="_blank" class="doi-link">{pub['doi']}</a></td>
        </tr>
        """
    
    # Citing works
    total_citing_works = metrics.get('total_citing_works', 0)
    unique_citing_authors = metrics.get('unique_citing_authors', 0)
    unique_citing_affiliations = metrics.get('unique_citing_affiliations', 0)
    unique_citing_countries = metrics.get('unique_citing_countries', 0)
    unique_citing_journals = metrics.get('unique_citing_journals', 0)
    unique_citing_publishers = metrics.get('unique_citing_publishers', 0)
    
    # Top citing authors
    top_citing_authors_html = ""
    for author, count in list(top_citing_authors.items())[:15]:
        top_citing_authors_html += f"""
        <tr>
            <td><strong>{html.escape(author)}</strong></td>
            <td>{count}</td>
        </tr>
        """
    
    # Top citing affiliations
    top_citing_affiliations_html = ""
    for aff, count in list(top_citing_affiliations.items())[:15]:
        top_citing_affiliations_html += f"""
        <tr>
            <td><strong>{html.escape(aff)}</strong></td>
            <td>{count}</td>
        </tr>
        """
    
    # Top citing countries
    top_citing_countries_html = ""
    for country, count in list(top_citing_countries.items())[:15]:
        top_citing_countries_html += f"""
        <tr>
            <td><strong>{country}</strong></td>
            <td>{count}</td>
        </tr>
        """
    
    # Top citing journals
    top_citing_journals_html = ""
    for journal, count in list(top_citing_journals.items())[:15]:
        top_citing_journals_html += f"""
        <tr>
            <td><strong>{html.escape(journal)}</strong></td>
            <td>{count}</td>
        </tr>
        """
    
    # Top citing publishers
    top_citing_publishers_html = ""
    for publisher, count in list(top_citing_publishers.items())[:15]:
        top_citing_publishers_html += f"""
        <tr>
            <td><strong>{html.escape(publisher)}</strong></td>
            <td>{count}</td>
        </tr>
        """
    
    # Topics overview
    topics_html = ""
    for topic, stats in list(topics_stats.items())[:20]:
        topics_html += f"""
        <tr>
            <td><strong>{html.escape(topic)}</strong></td>
            <td>{stats.get('analyzed_count', 0)}</td>
            <td>{stats.get('citing_count', 0)}</td>
            <td>{stats.get('analyzed_norm', 0):.3f}</td>
            <td>{stats.get('citing_norm', 0):.3f}</td>
            <td>{stats.get('total_norm', 0):.3f}</td>
            <td>{stats.get('first_year', '')}</td>
            <td>{stats.get('peak_year', '')}</td>
        </tr>
        """
    
    # Top topics by citations
    top_topics_citations_html = ""
    for topic, count in list(top_topics_by_citations.items())[:10]:
        top_topics_citations_html += f"""
        <tr>
            <td><strong>{html.escape(topic)}</strong></td>
            <td>{count}</td>
        </tr>
        """
    
    # Top subtopics by citations
    top_subtopics_citations_html = ""
    for subtopic, count in list(top_subtopics_by_citations.items())[:10]:
        top_subtopics_citations_html += f"""
        <tr>
            <td><strong>{html.escape(subtopic)}</strong></td>
            <td>{count}</td>
        </tr>
        """
    
    # Top fields by citations
    top_fields_citations_html = ""
    for field, count in list(top_fields_by_citations.items())[:10]:
        top_fields_citations_html += f"""
        <tr>
            <td><strong>{html.escape(field)}</strong></td>
            <td>{count}</td>
        </tr>
        """
    
    # Top domains by citations
    top_domains_citations_html = ""
    for domain, count in list(top_domains_by_citations.items())[:10]:
        top_domains_citations_html += f"""
        <tr>
            <td><strong>{html.escape(domain)}</strong></td>
            <td>{count}</td>
        </tr>
        """
    
    # Top concepts by citations
    top_concepts_citations_html = ""
    for concept, count in list(top_concepts_by_citations.items())[:10]:
        top_concepts_citations_html += f"""
        <tr>
            <td><strong>{html.escape(concept)}</strong></td>
            <td>{count}</td>
        </tr>
        """
    
    # Detailed citations
    detailed_citations_html = ""
    for article_id, data in detailed_citations.items():
        if data.get('citations'):
            # Генерируем уникальный ID для коллапсера
            collapse_id = f"cite_{article_id.replace('/', '_')}"
            
            detailed_citations_html += f"""
            <div class="collapser" onclick="toggleCitations('{collapse_id}')">
                <strong>{html.escape(data.get('title', 'No title'))}</strong>
                <span class="badge badge-info">{data.get('year', '')}</span>
                <span class="citation-count">{data.get('total_citations', 0)} citations</span>
                <span style="font-size: 12px; color: #666; margin-left: 10px;">DOI: {data.get('doi', '')}</span>
                <span style="float: right; font-size: 12px; color: #666;">Click to toggle citations</span>
            </div>
            <div id="{collapse_id}" style="display: none; padding: 10px; background: #f8f9fa; border-radius: 8px; margin: 5px 0 15px 0;">
            """
            
            for cite in data.get('citations', []):
                detailed_citations_html += f"""
                <div class="citation-detail" style="background: white; padding: 12px; margin: 8px 0; border-radius: 6px; border-left: 3px solid {primary}; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                    <div><strong>{html.escape(cite.get('citing_title') or 'No title')}</strong></div>
                    <div class="cite-meta" style="font-size: 12px; color: #555; margin-top: 4px;">
                        <strong>{t('citing_journal')}:</strong> {html.escape(cite.get('citing_journal', 'Unknown'))} | 
                        <strong>{t('citing_year')}:</strong> {cite.get('citing_year', '')} | 
                        <strong>{t('citation_lag')}:</strong> {cite.get('citation_lag', '')} years
                    </div>
                    <div class="cite-meta" style="font-size: 12px; color: #555;">
                        <strong>{t('authors')}:</strong> {', '.join(cite.get('citing_authors', [])[:5])}{' +' + str(len(cite.get('citing_authors', [])) - 5) + ' more' if len(cite.get('citing_authors', [])) > 5 else ''} |
                        <strong>{t('countries')}:</strong> {', '.join(cite.get('citing_countries', []))} |
                        <strong>{t('topics')}:</strong> {', '.join(cite.get('citing_topics', [])[:5])}
                    </div>
                    <div class="cite-meta" style="font-size: 12px;">
                        <a href="https://doi.org/{cite.get('citing_doi', '')}" target="_blank" class="doi-link">DOI: {cite.get('citing_doi', '')}</a>
                    </div>
                </div>
                """
            
            detailed_citations_html += """
            </div>
            """
    
    # All publications table
    all_pubs_html = ""
    for idx, pub in enumerate(all_publications, 1):
        all_pubs_html += f"""
        <tr data-year="{pub.get('year', '')}" data-authors="{','.join(pub.get('authors_list', []))}" data-affiliations="{','.join(pub.get('affiliations_list', []))}" data-citations="{pub.get('citations', 0)}" data-title="{pub.get('title', '').lower()}">
            <td>{idx}</td>
            <td class="word-wrap">{html.escape(pub.get('title', 'No title'))}</td>
            <td>{pub.get('year', '')}</td>
            <td>{html.escape(pub.get('authors', ''))}</td>
            <td>{html.escape(pub.get('affiliations', ''))}</td>
            <td><span class="citation-count">{pub.get('citations', 0)}</span></td>
            <td>{pub.get('citations_per_year', 0):.1f}</td>
            <td><a href="https://doi.org/{pub.get('doi', '')}" target="_blank" class="doi-link">{pub.get('doi', '')}</a></td>
        </tr>
        """
    
    # Собираем уникальные годы для фильтра
    years_for_filter = sorted(set(p.get('year') for p in all_publications if p.get('year')), reverse=True)
    year_filter_options = ""
    for year in years_for_filter:
        year_filter_options += f'<option value="{year}">{year}</option>'
    
    # Собираем уникальных авторов для фильтра
    authors_for_filter = sorted(set(a for p in all_publications for a in p.get('authors_list', [])))
    author_filter_datalist = '<datalist id="authorList">'
    for author in authors_for_filter[:100]:
        author_filter_datalist += f'<option value="{html.escape(author)}">'
    author_filter_datalist += '</datalist>'
    
    # Собираем уникальные аффилиации для фильтра
    affs_for_filter = sorted(set(a for p in all_publications for a in p.get('affiliations_list', [])))
    aff_filter_datalist = '<datalist id="affiliationList">'
    for aff in affs_for_filter[:100]:
        aff_filter_datalist += f'<option value="{html.escape(aff)}">'
    aff_filter_datalist += '</datalist>'
    
    # HTML отчет
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>{t('app_title')} - {issn}</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{
                font-family: 'Times New Roman', 'DejaVu Serif', serif;
                margin: 0;
                padding: 20px;
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                color: #333;
            }}
            .report-wrapper {{
                max-width: 1400px;
                margin: 0 auto;
                background: white;
                box-shadow: 0 10px 40px rgba(0,0,0,0.1);
                border-radius: 10px;
                overflow: hidden;
            }}
            .sidebar {{
                position: fixed;
                left: 0;
                top: 0;
                width: 280px;
                height: 100vh;
                background: linear-gradient(135deg, {primary} 0%, {secondary} 100%);
                color: white;
                padding: 30px 20px;
                overflow-y: auto;
                z-index: 1000;
            }}
            .sidebar h3 {{
                margin-bottom: 20px;
                font-size: 18px;
                font-weight: 600;
                color: white;
            }}
            .sidebar a {{
                color: white;
                text-decoration: none;
                display: block;
                padding: 10px 15px;
                margin: 3px 0;
                border-radius: 8px;
                transition: all 0.3s;
                font-size: 14px;
            }}
            .sidebar a:hover {{
                background: rgba(255,255,255,0.2);
                transform: translateX(5px);
            }}
            .sidebar .sub-item {{
                padding-left: 30px;
                font-size: 13px;
                opacity: 0.9;
            }}
            .sidebar .sub-item:hover {{
                opacity: 1;
            }}
            .main-content {{
                margin-left: 280px;
                padding: 30px 40px;
            }}
            .header {{
                background: linear-gradient(135deg, {primary} 0%, {secondary} 100%);
                color: white;
                padding: 40px;
                border-radius: 15px;
                margin-bottom: 30px;
                text-align: center;
            }}
            .header h1 {{
                color: white;
                border-bottom: none;
                margin: 0;
                font-size: 32px;
            }}
            .header .subtitle {{
                opacity: 0.9;
                margin-top: 10px;
                font-size: 16px;
            }}
            .header .date {{
                opacity: 0.9;
                margin-top: 10px;
            }}
            .header-logo {{
                max-height: 150px;
                max-width: 300px;
                margin-bottom: 15px;
            }}
            .header-logo-app {{
                max-height: 120px;
                max-width: 360px;
                margin-bottom: 10px;
            }}
            .section {{
                background: white;
                border-radius: 15px;
                padding: 25px;
                margin-bottom: 30px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }}
            .section-title {{
                font-size: 24px;
                font-weight: 600;
                margin-bottom: 20px;
                padding-bottom: 10px;
                border-bottom: 3px solid {primary};
                display: flex;
                align-items: center;
                gap: 12px;
            }}
            .section-title .icon {{
                font-size: 28px;
            }}
            .subsection-title {{
                font-size: 18px;
                font-weight: 600;
                margin: 20px 0 15px 0;
                color: {primary};
                display: flex;
                align-items: center;
                gap: 10px;
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
                font-family: 'Times New Roman', serif;
            }}
            .metric-label {{
                font-size: 12px;
                color: #7F8C8D;
                margin-top: 5px;
                font-family: 'Times New Roman', serif;
            }}
            .metrics-grid-2 {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 15px;
                margin: 15px 0;
            }}
            .grid-2-col {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
            }}
            .grid-3-col {{
                display: grid;
                grid-template-columns: 1fr 1fr 1fr;
                gap: 20px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
                font-family: 'Times New Roman', serif;
                font-size: 13px;
            }}
            th {{
                background: linear-gradient(135deg, {primary} 0%, {secondary} 100%);
                color: white;
                padding: 12px;
                text-align: left;
                position: sticky;
                top: 0;
                z-index: 10;
            }}
            td {{
                padding: 10px;
                border-bottom: 1px solid #BDC3C7;
            }}
            tr:hover {{
                background-color: #f5f5f5;
            }}
            .table-container {{
                max-height: 600px;
                overflow-y: auto;
                border: 1px solid #ddd;
                border-radius: 8px;
            }}
            .table-container table {{
                margin: 0;
            }}
            .table-container thead th {{
                position: sticky;
                top: 0;
                z-index: 10;
            }}
            .word-wrap {{
                word-wrap: break-word;
                max-width: 250px;
            }}
            .doi-link {{
                color: #2980B9;
                text-decoration: none;
                font-size: 12px;
                word-break: break-all;
            }}
            .doi-link:hover {{
                text-decoration: underline;
            }}
            .citation-count {{
                font-weight: bold;
                color: {primary};
            }}
            .badge {{
                display: inline-block;
                padding: 4px 12px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: 600;
                margin: 2px;
            }}
            .badge-info {{
                background: #d1ecf1;
                color: #0c5460;
            }}
            .badge-success {{
                background: #d4edda;
                color: #155724;
            }}
            .badge-warning {{
                background: #fff3cd;
                color: #856404;
            }}
            .badge-danger {{
                background: #f8d7da;
                color: #721c24;
            }}
            .progress-bar-container {{
                width: 100%;
                background-color: #f0f0f0;
                border-radius: 10px;
                overflow: hidden;
                height: 20px;
                margin: 5px 0;
            }}
            .progress-bar-fill {{
                height: 100%;
                background: linear-gradient(90deg, {primary}, {secondary});
                border-radius: 10px;
                transition: width 0.5s;
                text-align: center;
                color: white;
                font-size: 11px;
                line-height: 20px;
            }}
            .collapser {{
                background: #f8f9fa;
                padding: 12px 15px;
                border-radius: 8px;
                margin: 8px 0;
                cursor: pointer;
                border-left: 4px solid {primary};
                transition: all 0.3s;
            }}
            .collapser:hover {{
                background: #e9ecef;
                transform: translateX(5px);
            }}
            .collapser .badge {{
                margin-left: 10px;
            }}
            .citation-detail {{
                background: white;
                padding: 12px;
                margin: 8px 0;
                border-radius: 6px;
                border-left: 3px solid {primary};
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            }}
            .citation-detail:hover {{
                box-shadow: 0 2px 8px rgba(0,0,0,0.15);
            }}
            .cite-meta {{
                font-size: 12px;
                color: #555;
                margin-top: 4px;
            }}
            .filter-section {{
                background: #f8f9fa;
                padding: 15px;
                border-radius: 8px;
                margin: 15px 0;
                border: 1px solid #ddd;
            }}
            .filter-row {{
                display: flex;
                flex-wrap: wrap;
                gap: 15px;
                align-items: center;
            }}
            .filter-row > div {{
                display: flex;
                flex-direction: column;
                gap: 4px;
            }}
            .filter-row label {{
                font-size: 12px;
                font-weight: 600;
                color: #555;
            }}
            .filter-row select, .filter-row input {{
                padding: 6px 10px;
                border: 1px solid #ddd;
                border-radius: 6px;
                font-size: 13px;
                font-family: 'Times New Roman', serif;
            }}
            .filter-row select:focus, .filter-row input:focus {{
                outline: none;
                border-color: {primary};
                box-shadow: 0 0 0 2px {primary}40;
            }}
            .filter-row input[type="number"] {{
                width: 80px;
            }}
            .filter-row input[type="text"] {{
                width: 150px;
            }}
            .filter-row select {{
                min-width: 100px;
            }}
            #visibleCount {{
                font-weight: 500;
                color: {primary};
                padding: 6px 12px;
                background: white;
                border-radius: 6px;
                border: 1px solid #ddd;
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
                color: #2980B9;
                text-decoration: none;
            }}
            .footer a:hover {{
                text-decoration: underline;
            }}
            .oa-card {{
                background: #f8f9fa;
                padding: 15px;
                border-radius: 8px;
                border: 1px solid #ddd;
            }}
            .oa-row {{
                display: flex;
                justify-content: space-between;
                padding: 4px 0;
                border-bottom: 1px solid #eee;
            }}
            .oa-row:last-child {{
                border-bottom: none;
            }}
            .oa-label {{
                font-weight: 500;
            }}
            .oa-value {{
                font-weight: bold;
            }}
            .collab-pattern {{
                display: flex;
                gap: 20px;
                align-items: center;
            }}
            .collab-item {{
                text-align: center;
                padding: 10px 20px;
                background: #f8f9fa;
                border-radius: 8px;
                flex: 1;
            }}
            .collab-item .number {{
                font-size: 24px;
                font-weight: bold;
                color: {primary};
            }}
            .collab-item .label {{
                font-size: 12px;
                color: #666;
            }}
            
            @media print {{
                .sidebar {{ display: none; }}
                .main-content {{ margin-left: 0; }}
            }}
            @media (max-width: 768px) {{
                .sidebar {{ display: none; }}
                .main-content {{ margin-left: 0; padding: 20px; }}
                .grid-2-col, .grid-3-col {{ grid-template-columns: 1fr; }}
                .filter-row {{ flex-direction: column; align-items: stretch; }}
                .filter-row input[type="text"], .filter-row input[type="number"], .filter-row select {{
                    width: 100%;
                }}
                .metrics-grid {{ grid-template-columns: repeat(2, 1fr); }}
                .collab-pattern {{ flex-direction: column; }}
            }}
            
            .sticky-header {{
                position: sticky;
                top: 0;
                z-index: 100;
            }}
            .scrollable-table {{
                max-height: 600px;
                overflow-y: auto;
            }}
            .scrollable-table table {{
                width: 100%;
                border-collapse: collapse;
            }}
            .scrollable-table thead th {{
                position: sticky;
                top: 0;
                z-index: 10;
            }}
            .highlight-row:hover {{
                background-color: {primary}20;
            }}
        </style>
        <script>
            function toggleCitations(id) {{
                var el = document.getElementById(id);
                if (el) {{
                    if (el.style.display === 'none' || el.style.display === '') {{
                        el.style.display = 'block';
                    }} else {{
                        el.style.display = 'none';
                    }}
                }}
            }}
            
            function filterPublications() {{
                var yearFilter = document.getElementById('yearFilter');
                var authorFilter = document.getElementById('authorFilter');
                var affFilter = document.getElementById('affFilter');
                var citationFilter = document.getElementById('citationFilter');
                var searchFilter = document.getElementById('searchFilter');
                
                var year = yearFilter ? yearFilter.value.toLowerCase() : '';
                var author = authorFilter ? authorFilter.value.toLowerCase() : '';
                var aff = affFilter ? affFilter.value.toLowerCase() : '';
                var citations = citationFilter ? parseInt(citationFilter.value) || 0 : 0;
                var search = searchFilter ? searchFilter.value.toLowerCase() : '';
                
                var rows = document.querySelectorAll('#publicationsTable tbody tr');
                var visibleCount = 0;
                
                rows.forEach(function(row) {{
                    var rowYear = row.getAttribute('data-year') || '';
                    var rowAuthors = row.getAttribute('data-authors') || '';
                    var rowAffs = row.getAttribute('data-affiliations') || '';
                    var rowCitations = parseInt(row.getAttribute('data-citations')) || 0;
                    var rowTitle = row.getAttribute('data-title') || '';
                    
                    var show = true;
                    
                    if (year && rowYear !== year) show = false;
                    if (author && !rowAuthors.toLowerCase().includes(author)) show = false;
                    if (aff && !rowAffs.toLowerCase().includes(aff)) show = false;
                    if (citations > 0 && rowCitations < citations) show = false;
                    if (search && !rowTitle.includes(search)) show = false;
                    
                    if (show) {{
                        row.style.display = '';
                        visibleCount++;
                    }} else {{
                        row.style.display = 'none';
                    }}
                }});
                
                var countEl = document.getElementById('visibleCount');
                if (countEl) {{
                    var total = rows.length;
                    countEl.textContent = 'Showing ' + visibleCount + ' of ' + total + ' publications';
                }}
            }}
            
            function sortTable(n) {{
                var table = document.getElementById('publicationsTable');
                var tbody = table.querySelector('tbody');
                var rows = Array.from(tbody.querySelectorAll('tr'));
                var ascending = table.getAttribute('data-sort-dir') === 'asc';
                
                rows.sort(function(a, b) {{
                    var x = a.cells[n].textContent.trim();
                    var y = b.cells[n].textContent.trim();
                    
                    var xNum = parseFloat(x);
                    var yNum = parseFloat(y);
                    if (!isNaN(xNum) && !isNaN(yNum)) {{
                        return ascending ? xNum - yNum : yNum - xNum;
                    }}
                    
                    return ascending ? x.localeCompare(y) : y.localeCompare(x);
                }});
                
                rows.forEach(function(row) {{
                    tbody.appendChild(row);
                }});
                
                table.setAttribute('data-sort-dir', ascending ? 'desc' : 'asc');
            }}
            
            document.addEventListener('DOMContentLoaded', function() {{
                var yearFilter = document.getElementById('yearFilter');
                var authorFilter = document.getElementById('authorFilter');
                var affFilter = document.getElementById('affFilter');
                var citationFilter = document.getElementById('citationFilter');
                var searchFilter = document.getElementById('searchFilter');
                
                if (yearFilter) yearFilter.addEventListener('change', filterPublications);
                if (authorFilter) authorFilter.addEventListener('keyup', filterPublications);
                if (affFilter) affFilter.addEventListener('keyup', filterPublications);
                if (citationFilter) citationFilter.addEventListener('change', filterPublications);
                if (searchFilter) searchFilter.addEventListener('keyup', filterPublications);
                
                filterPublications();
            }});
        </script>
    </head>
    <body>
        <div class="sidebar">
            <h3>📑 {t('app_title')}</h3>
            <a href="#overview">📊 {t('overview')}</a>
            <a href="#analyzed_articles" style="padding-left: 30px; font-size: 13px;">📝 {t('analyzed_articles')}</a>
            <a href="#citation_analysis" style="padding-left: 30px; font-size: 13px;">📈 {t('citation_analysis')}</a>
            <a href="#citing_works" style="padding-left: 30px; font-size: 13px;">📚 {t('citing_works')}</a>
            <a href="#topics_analysis" style="padding-left: 30px; font-size: 13px;">🏷️ {t('topics_analysis')}</a>
            <a href="#detailed_citations" style="padding-left: 30px; font-size: 13px;">📋 {t('detailed_citations')}</a>
            <a href="#all_publications" style="padding-left: 30px; font-size: 13px;">📚 {t('all_publications')}</a>
        </div>
        
        <div class="main-content">
            <div class="header">
                {f'<img src="data:image/png;base64,{app_logo_base64}" class="header-logo-app" alt="App Logo">' if app_logo_base64 else ''}
                {f'<img src="data:image/png;base64,{logo_base64}" class="header-logo" alt="Journal Logo">' if logo_base64 else ''}
                <h1>📊 {t('app_title')}</h1>
                <div class="subtitle">{t('journal_analysis')}: {issn} ({period_str})</div>
                <div class="date">{t('generated_on')}: {datetime.now().strftime('%d.%m.%Y %H:%M')}</div>
                <div style="margin-top: 10px; font-size: 13px; opacity: 0.8;">{t('source_data')}</div>
            </div>
            
            <!-- SECTION: Overview -->
            <div id="overview" class="section">
                <div class="section-title"><span class="icon">📊</span> {t('overview')}</div>
                
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-value">{metrics.get('total_publications', 0)}</div>
                        <div class="metric-label">{t('total_publications')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{metrics.get('total_citations', 0):,}</div>
                        <div class="metric-label">{t('total_citations')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{metrics.get('h_index', 0)}</div>
                        <div class="metric-label">{t('h_index')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{metrics.get('g_index', 0)}</div>
                        <div class="metric-label">{t('g_index')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{metrics.get('i10_index', 0)}</div>
                        <div class="metric-label">{t('i10_index')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{metrics.get('i100_index', 0)}</div>
                        <div class="metric-label">{t('i100_index')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{metrics.get('avg_citations', 0):.1f}</div>
                        <div class="metric-label">{t('avg_citations')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{metrics.get('active_years', 0)}</div>
                        <div class="metric-label">{t('active_years')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{metrics.get('unique_authors', 0):,}</div>
                        <div class="metric-label">{t('unique_authors')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{metrics.get('unique_affiliations', 0):,}</div>
                        <div class="metric-label">{t('unique_affiliations')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{metrics.get('unique_countries', 0)}</div>
                        <div class="metric-label">{t('unique_countries')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{metrics.get('avg_authors_per_paper', 0):.1f}</div>
                        <div class="metric-label">{t('avg_authors_per_paper')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{metrics.get('avg_affiliations_per_paper', 0):.1f}</div>
                        <div class="metric-label">{t('avg_affiliations_per_paper')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{metrics.get('avg_countries_per_paper', 0):.1f}</div>
                        <div class="metric-label">{t('avg_countries_per_paper')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{(metrics.get('international_collaboration_rate', 0) * 100):.1f}%</div>
                        <div class="metric-label">{t('international_collaboration_rate')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{metrics.get('unique_citing_authors', 0):,}</div>
                        <div class="metric-label">{t('unique_citing_authors')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{metrics.get('unique_citing_affiliations', 0):,}</div>
                        <div class="metric-label">{t('unique_citing_affiliations')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{metrics.get('unique_citing_countries', 0)}</div>
                        <div class="metric-label">{t('unique_citing_countries')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{metrics.get('unique_citing_journals', 0):,}</div>
                        <div class="metric-label">{t('unique_citing_journals')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{metrics.get('unique_citing_publishers', 0):,}</div>
                        <div class="metric-label">{t('unique_citing_publishers')}</div>
                    </div>
                </div>
                
                <div class="subsection-title">{t('open_access_breakdown')}</div>
                <div style="max-width: 300px;">
                    {oa_html}
                </div>
            </div>
            
            <!-- SECTION: Analyzed Articles -->
            <div id="analyzed_articles" class="section">
                <div class="section-title"><span class="icon">📝</span> {t('analyzed_articles')}</div>
                
                <div class="subsection-title">{t('author_analysis')}</div>
                <div class="scrollable-table">
                    <table>
                        <thead>
                            <tr>
                                <th>{t('rank')}</th>
                                <th>{t('authors')}</th>
                                <th>{t('orcid')}</th>
                                <th>{t('affiliations')}</th>
                                <th>{t('countries')}</th>
                                <th>{t('publications')}</th>
                                <th>{t('citations')}</th>
                            </tr>
                        </thead>
                        <tbody>
                            {author_html}
                        </tbody>
                    </table>
                </div>
                
                <div class="subsection-title">{t('top_affiliations')}</div>
                <div style="max-width: 400px;">
                    <table>
                        <thead>
                            <tr>
                                <th>{t('affiliations')}</th>
                                <th>{t('publications')}</th>
                            </tr>
                        </thead>
                        <tbody>
                            {top_aff_html}
                        </tbody>
                    </table>
                </div>
                
                <div class="subsection-title">{t('geographic_analysis')}</div>
                
                <div class="grid-2-col">
                    <div>
                        <h4 style="font-size: 15px; color: {primary};">{t('countries_per_publication')}</h4>
                        <div class="scrollable-table" style="max-height: 300px;">
                            <table>
                                <thead>
                                    <tr>
                                        <th>Article</th>
                                        <th>{t('countries')}</th>
                                        <th>{t('country_count')}</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {countries_per_pub_html}
                                </tbody>
                            </table>
                        </div>
                    </div>
                    <div>
                        <h4 style="font-size: 15px; color: {primary};">{t('authors_per_country')}</h4>
                        <div class="scrollable-table" style="max-height: 300px;">
                            <table>
                                <thead>
                                    <tr>
                                        <th>{t('countries')}</th>
                                        <th>{t('authors')}</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {authors_per_country_html}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
                
                <div style="margin-top: 20px;">
                    <h4 style="font-size: 15px; color: {primary};">{t('collaboration_patterns')}</h4>
                    <div class="collab-pattern">
                        <div class="collab-item">
                            <div class="number">{single_country}</div>
                            <div class="label">{t('single_country')} ({single_pct:.1f}%)</div>
                        </div>
                        <div class="collab-item">
                            <div class="number">{international}</div>
                            <div class="label">{t('international')} ({intl_pct:.1f}%)</div>
                        </div>
                    </div>
                </div>
                
                <div style="margin-top: 20px;">
                    <h4 style="font-size: 15px; color: {primary};">{t('collaboration_couples')}</h4>
                    <div style="max-width: 400px;">
                        <table>
                            <thead>
                                <tr>
                                    <th>{t('collaboration_couple')}</th>
                                    <th>{t('frequency')}</th>
                                </tr>
                            </thead>
                            <tbody>
                                {couples_html}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
            
            <!-- SECTION: Citation Analysis -->
            <div id="citation_analysis" class="section">
                <div class="section-title"><span class="icon">📈</span> {t('citation_analysis')}</div>
                
                <div class="subsection-title">{t('citation_dynamics')}</div>
                <div class="scrollable-table" style="max-height: 400px;">
                    <table>
                        <thead>
                            <tr>
                                <th>{t('publication_year')}</th>
                                <th>{t('citation_year')}</th>
                                <th>{t('citations_count')}</th>
                            </tr>
                        </thead>
                        <tbody>
                            {dynamics_html}
                        </tbody>
                    </table>
                </div>
                
                <div class="subsection-title">{t('first_citation_stats')}</div>
                {first_stats_html}
                
                <div class="subsection-title">{t('cumulative_citations')}</div>
                <div style="max-width: 400px;">
                    <table>
                        <thead>
                            <tr>
                                <th>{t('year')}</th>
                                <th>{t('cumulative_citations')}</th>
                            </tr>
                        </thead>
                        <tbody>
                            {cumul_html}
                        </tbody>
                    </table>
                </div>
                
                <div class="subsection-title">{t('citation_heatmap')}</div>
                {heatmap_html}
                
                <div class="subsection-title">{t('most_cited_publications')}</div>
                <div class="scrollable-table" style="max-height: 500px;">
                    <table>
                        <thead>
                            <tr>
                                <th>{t('rank')}</th>
                                <th>{t('title')}</th>
                                <th>{t('year')}</th>
                                <th>{t('citations')}</th>
                                <th>{t('citations_per_year')}</th>
                                <th>{t('authors')}</th>
                                <th>{t('doi')}</th>
                            </tr>
                        </thead>
                        <tbody>
                            {most_cited_html}
                        </tbody>
                    </table>
                </div>
            </div>
            
            <!-- SECTION: Citing Works -->
            <div id="citing_works" class="section">
                <div class="section-title"><span class="icon">📚</span> {t('citing_works_analysis')}</div>
                
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-value">{total_citing_works}</div>
                        <div class="metric-label">{t('total_citing_works')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{unique_citing_authors:,}</div>
                        <div class="metric-label">{t('unique_citing_authors')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{unique_citing_affiliations:,}</div>
                        <div class="metric-label">{t('unique_citing_affiliations')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{unique_citing_countries}</div>
                        <div class="metric-label">{t('unique_citing_countries')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{unique_citing_journals:,}</div>
                        <div class="metric-label">{t('unique_citing_journals')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{unique_citing_publishers:,}</div>
                        <div class="metric-label">{t('unique_citing_publishers')}</div>
                    </div>
                </div>
                
                <div class="grid-2-col">
                    <div>
                        <h4 style="font-size: 15px; color: {primary};">{t('top_citing_authors')}</h4>
                        <div class="scrollable-table" style="max-height: 400px;">
                            <table>
                                <thead>
                                    <tr>
                                        <th>{t('authors')}</th>
                                        <th>{t('citations')}</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {top_citing_authors_html}
                                </tbody>
                            </table>
                        </div>
                    </div>
                    <div>
                        <h4 style="font-size: 15px; color: {primary};">{t('top_citing_affiliations')}</h4>
                        <div class="scrollable-table" style="max-height: 400px;">
                            <table>
                                <thead>
                                    <tr>
                                        <th>{t('affiliations')}</th>
                                        <th>{t('citations')}</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {top_citing_affiliations_html}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
                
                <div class="grid-2-col" style="margin-top: 20px;">
                    <div>
                        <h4 style="font-size: 15px; color: {primary};">{t('top_citing_countries')}</h4>
                        <div class="scrollable-table" style="max-height: 400px;">
                            <table>
                                <thead>
                                    <tr>
                                        <th>{t('countries')}</th>
                                        <th>{t('citations')}</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {top_citing_countries_html}
                                </tbody>
                            </table>
                        </div>
                    </div>
                    <div>
                        <h4 style="font-size: 15px; color: {primary};">{t('top_citing_journals')}</h4>
                        <div class="scrollable-table" style="max-height: 400px;">
                            <table>
                                <thead>
                                    <tr>
                                        <th>{t('journals')}</th>
                                        <th>{t('citations')}</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {top_citing_journals_html}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
                
                <div style="margin-top: 20px;">
                    <h4 style="font-size: 15px; color: {primary};">{t('top_citing_publishers')}</h4>
                    <div style="max-width: 400px;">
                        <table>
                            <thead>
                                <tr>
                                    <th>{t('publishers')}</th>
                                    <th>{t('citations')}</th>
                                </tr>
                            </thead>
                            <tbody>
                                {top_citing_publishers_html}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
            
            <!-- SECTION: Topics Analysis -->
            <div id="topics_analysis" class="section">
                <div class="section-title"><span class="icon">🏷️</span> {t('topics_analysis')}</div>
                
                <div class="subsection-title">{t('topics_overview')}</div>
                <div class="scrollable-table" style="max-height: 500px;">
                    <table>
                        <thead>
                            <tr>
                                <th>{t('topics')}</th>
                                <th>{t('analyzed_count')}</th>
                                <th>{t('citing_count')}</th>
                                <th>{t('analyzed_norm_count')}</th>
                                <th>{t('citing_norm_count')}</th>
                                <th>{t('total_norm_count')}</th>
                                <th>{t('first_year')}</th>
                                <th>{t('peak_year')}</th>
                            </tr>
                        </thead>
                        <tbody>
                            {topics_html}
                        </tbody>
                    </table>
                </div>
                
                <div class="subsection-title">{t('top_topics_by_citations')}</div>
                <div class="grid-2-col">
                    <div>
                        <h4 style="font-size: 14px; color: {primary};">{t('topics')}</h4>
                        <table>
                            <thead>
                                <tr>
                                    <th>{t('topics')}</th>
                                    <th>{t('citations')}</th>
                                </tr>
                            </thead>
                            <tbody>
                                {top_topics_citations_html}
                            </tbody>
                        </table>
                    </div>
                    <div>
                        <h4 style="font-size: 14px; color: {primary};">{t('subtopics')}</h4>
                        <table>
                            <thead>
                                <tr>
                                    <th>{t('subtopics')}</th>
                                    <th>{t('citations')}</th>
                                </tr>
                            </thead>
                            <tbody>
                                {top_subtopics_citations_html}
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <div class="grid-2-col" style="margin-top: 15px;">
                    <div>
                        <h4 style="font-size: 14px; color: {primary};">{t('fields')}</h4>
                        <table>
                            <thead>
                                <tr>
                                    <th>{t('fields')}</th>
                                    <th>{t('citations')}</th>
                                </tr>
                            </thead>
                            <tbody>
                                {top_fields_citations_html}
                            </tbody>
                        </table>
                    </div>
                    <div>
                        <h4 style="font-size: 14px; color: {primary};">{t('domains')}</h4>
                        <table>
                            <thead>
                                <tr>
                                    <th>{t('domains')}</th>
                                    <th>{t('citations')}</th>
                                </tr>
                            </thead>
                            <tbody>
                                {top_domains_citations_html}
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <div style="margin-top: 15px;">
                    <h4 style="font-size: 14px; color: {primary};">{t('concepts')}</h4>
                    <div style="max-width: 400px;">
                        <table>
                            <thead>
                                <tr>
                                    <th>{t('concepts')}</th>
                                    <th>{t('citations')}</th>
                                </tr>
                            </thead>
                            <tbody>
                                {top_concepts_citations_html}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
            
            <!-- SECTION: Detailed Citations -->
            <div id="detailed_citations" class="section">
                <div class="section-title"><span class="icon">📋</span> {t('detailed_citations')}</div>
                {detailed_citations_html if detailed_citations_html else f'<p>{t("no_publications_found")}</p>'}
            </div>
            
            <!-- SECTION: All Publications -->
            <div id="all_publications" class="section">
                <div class="section-title"><span class="icon">📚</span> {t('all_publications')}</div>
                
                <div class="filter-section">
                    <div class="filter-row">
                        <div>
                            <label for="searchFilter">{t('filter_by_title')}</label>
                            <input type="text" id="searchFilter" placeholder="Search..." onkeyup="filterPublications()">
                        </div>
                        <div>
                            <label for="yearFilter">{t('filter_by_year')}</label>
                            <select id="yearFilter" onchange="filterPublications()">
                                <option value="">All Years</option>
                                {year_filter_options}
                            </select>
                        </div>
                        <div>
                            <label for="authorFilter">{t('filter_by_author')}</label>
                            <input type="text" id="authorFilter" placeholder="Author name..." onkeyup="filterPublications()" list="authorList">
                            {author_filter_datalist}
                        </div>
                        <div>
                            <label for="affFilter">{t('filter_by_affiliation')}</label>
                            <input type="text" id="affFilter" placeholder="Affiliation..." onkeyup="filterPublications()" list="affiliationList">
                            {aff_filter_datalist}
                        </div>
                        <div>
                            <label for="citationFilter">{t('filter_by_citations_min')}</label>
                            <input type="number" id="citationFilter" placeholder="Min..." min="0" onchange="filterPublications()">
                        </div>
                        <div>
                            <span id="visibleCount">All publications</span>
                        </div>
                    </div>
                </div>
                
                <div class="scrollable-table" id="publicationsTableContainer" style="max-height: 600px; overflow-y: auto;">
                    <table id="publicationsTable" data-sort-dir="asc">
                        <thead>
                            <tr>
                                <th onclick="sortTable(0)" style="cursor: pointer;">#</th>
                                <th onclick="sortTable(1)" style="cursor: pointer;">{t('title')}</th>
                                <th onclick="sortTable(2)" style="cursor: pointer;">{t('year')}</th>
                                <th onclick="sortTable(3)" style="cursor: pointer;">{t('authors')}</th>
                                <th onclick="sortTable(4)" style="cursor: pointer;">{t('affiliations')}</th>
                                <th onclick="sortTable(5)" style="cursor: pointer;">{t('citations')}</th>
                                <th onclick="sortTable(6)" style="cursor: pointer;">{t('citations_per_year')}</th>
                                <th>{t('doi')}</th>
                            </tr>
                        </thead>
                        <tbody>
                            {all_pubs_html}
                        </tbody>
                    </table>
                </div>
            </div>
            
            <!-- Footer -->
            <div class="footer">
                <p>{t('footer')}</p>
                <p><a href="{t('journal_url')}" target="_blank">{t('journal_url')}</a></p>
                <p style="font-size: 11px; margin-top: 5px;">{t('source_data')} | {t('generated_on')}: {datetime.now().strftime('%d.%m.%Y %H:%M')}</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html_content

# ============================================
# ОСНОВНАЯ ФУНКЦИЯ ЗАПУСКА ДЛЯ STREAMLIT
# ============================================

def run_journal_analysis(issn: str, period, max_workers: int = 8, journal_logo: Optional[Dict] = None):
    """Запускает анализ журнала"""
    
    current_lang = st.session_state.get('language', 'en')
    def t(key: str, **kwargs) -> str:
        return translate(key, current_lang, **kwargs)
    
    # Проверка наличия данных в сессии
    session_key = f"journal_analysis_{issn}_{str(period)}_{max_workers}"
    
    if session_key in st.session_state:
        # Данные уже есть в кэше сессии
        st.success(f"✅ {t('analysis_complete')} (from cache)")
        html_report = st.session_state[session_key]
        st.components.v1.html(html_report, height=800, scrolling=True)
        
        # Кнопка скачивания
        st.download_button(
            label=t('download_report'),
            data=html_report.encode('utf-8'),
            file_name=f"journal_analysis_{issn}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
            mime="text/html",
            width='stretch'
        )
        return
    
    # Новый анализ
    progress_container = st.empty()
    status_container = st.empty()
    analysis_progress = st.progress(0, text=t('analyzing_articles'))
    
    try:
        # Загружаем логотип приложения
        app_logo_base64 = None
        if os.path.exists("icon.png"):
            try:
                with open("icon.png", "rb") as f:
                    app_logo_base64 = base64.b64encode(f.read()).decode()
            except Exception as e:
                print(f"⚠️ Ошибка загрузки логотипа приложения: {e}")
        
        journal_logo_base64 = None
        if journal_logo:
            try:
                for filename, file_info in journal_logo.items():
                    content = file_info['content'] if hasattr(file_info, 'get') else file_info
                    if hasattr(content, 'read'):
                        content = content.read()
                    journal_logo_base64 = base64.b64encode(content).decode()
                    break
            except Exception as e:
                st.warning(f"⚠️ Ошибка загрузки логотипа журнала: {e}")
        
        # Создаем анализатор
        analyzer = JournalAnalyzer(issn, period, max_workers)
        
        # Функция обновления прогресса
        def progress_callback(current, total, stage="loading"):
            if stage == "loading":
                progress = (current / 20) * 0.5  # 50% на загрузку статей
                analysis_progress.progress(progress, text=f"📚 {t('analyzing_articles')}... (page {current})")
                status_container.info(f"📚 {t('analyzing_articles')} (page {current})")
            elif stage == "citing":
                progress = 0.5 + (current / total) * 0.5  # 50% на сбор цитирований
                analysis_progress.progress(progress, text=f"⚡ {t('fetching_citations')}... ({current}/{total})")
                status_container.info(f"⚡ {t('fetching_citations')} ({current}/{total})")
        
        # Загрузка статей
        analyzer.fetch_articles(lambda p, s: progress_callback(p, 0, s))
        
        if not analyzer.articles:
            st.warning(t('no_publications_found'))
            return
        
        # Сбор цитирований
        analyzer.fetch_citing_works_parallel(lambda c, t: progress_callback(c, t, "citing"))
        
        # Расчет метрик
        metrics_calc = MetricsCalculator(analyzer.articles, analyzer.citations, analyzer.all_citing_works)
        
        # Сбор всех данных для отчета
        metrics = metrics_calc.calculate_basic_metrics()
        author_stats = metrics_calc.calculate_author_stats()
        top_affiliations = metrics_calc.calculate_top_affiliations()
        geographic_stats = metrics_calc.calculate_geographic_stats()
        citation_dynamics = metrics_calc.calculate_citation_dynamics()
        cumulative_citations = metrics_calc.calculate_cumulative_citations()
        heatmap_data = metrics_calc.calculate_heatmap_data()
        most_cited = metrics_calc.calculate_most_cited()
        top_citing_authors = metrics_calc.calculate_top_citing('authors')
        top_citing_affiliations = metrics_calc.calculate_top_citing('affiliations')
        top_citing_countries = metrics_calc.calculate_top_citing('countries')
        top_citing_journals = metrics_calc.calculate_top_citing('journals')
        top_citing_publishers = metrics_calc.calculate_top_citing('publishers')
        topics_stats = metrics_calc.calculate_topics_stats()
        top_topics_by_citations = metrics_calc.calculate_top_topics_by_citations('topics')
        top_subtopics_by_citations = metrics_calc.calculate_top_topics_by_citations('subtopics')
        top_fields_by_citations = metrics_calc.calculate_top_topics_by_citations('fields')
        top_domains_by_citations = metrics_calc.calculate_top_topics_by_citations('domains')
        top_concepts_by_citations = metrics_calc.calculate_top_topics_by_citations('concepts')
        detailed_citations = metrics_calc.get_detailed_citations()
        all_publications = metrics_calc.get_all_publications_data()
        
        # Генерация отчета
        analysis_progress.progress(0.95, text=f"📄 {t('generating_report')}...")
        status_container.info(f"📄 {t('generating_report')}...")
        
        theme_colors = {
            'primary': st.session_state.get('primary_color', '#667eea'),
            'secondary': st.session_state.get('secondary_color', '#f39c12')
        }
        
        html_report = generate_journal_html_report(
            issn=issn,
            period=period,
            articles=analyzer.articles,
            citations=analyzer.citations,
            all_citing_works=analyzer.all_citing_works,
            metrics=metrics,
            author_stats=author_stats,
            top_affiliations=top_affiliations,
            geographic_stats=geographic_stats,
            citation_dynamics=citation_dynamics,
            cumulative_citations=cumulative_citations,
            heatmap_data=heatmap_data,
            most_cited=most_cited,
            top_citing_authors=top_citing_authors,
            top_citing_affiliations=top_citing_affiliations,
            top_citing_countries=top_citing_countries,
            top_citing_journals=top_citing_journals,
            top_citing_publishers=top_citing_publishers,
            topics_stats=topics_stats,
            top_topics_by_citations=top_topics_by_citations,
            top_subtopics_by_citations=top_subtopics_by_citations,
            top_fields_by_citations=top_fields_by_citations,
            top_domains_by_citations=top_domains_by_citations,
            top_concepts_by_citations=top_concepts_by_citations,
            detailed_citations=detailed_citations,
            all_publications=all_publications,
            logo_base64=journal_logo_base64,
            app_logo_base64=app_logo_base64,
            theme_colors=theme_colors,
            lang=current_lang
        )
        
        # Сохраняем в сессию
        st.session_state[session_key] = html_report
        
        analysis_progress.progress(1.0, text=f"✅ {t('analysis_complete')}!")
        status_container.success(f"✅ {t('analysis_complete')} {len(analyzer.articles)} articles, {len(analyzer.all_citing_works)} citing works")
        
        # Отображение отчета
        st.components.v1.html(html_report, height=800, scrolling=True)
        
        # Кнопка скачивания
        st.download_button(
            label=t('download_report'),
            data=html_report.encode('utf-8'),
            file_name=f"journal_analysis_{issn}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
            mime="text/html",
            width='stretch'
        )
        
        st.balloons()
        
    except Exception as e:
        st.error(f"❌ {t('error_occurred')}: {str(e)}")
        import traceback
        st.code(traceback.format_exc())
    finally:
        analysis_progress.empty()

# ============================================
# ОСНОВНАЯ ФУНКЦИЯ STREAMLIT
# ============================================

def main():
    # Page configuration
    st.set_page_config(
        page_title="Advanced Journal Analysis Tool",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    if 'primary_color' not in st.session_state:
        st.session_state.primary_color = '#667eea'
    if 'secondary_color' not in st.session_state:
        st.session_state.secondary_color = '#f39c12'
    if 'language' not in st.session_state:
        st.session_state.language = 'en'
    
    # Apply theme
    primary = st.session_state.primary_color
    secondary = st.session_state.secondary_color
    apply_theme_css(primary, secondary)
    
    # Get current language
    current_lang = st.session_state.language
    
    # Helper function for translations
    def t(key: str, **kwargs) -> str:
        return translate(key, current_lang, **kwargs)
    
    # Sidebar
    with st.sidebar:
        st.markdown(f"## {t('settings')}")
        
        # Language selector
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
        
        # Color theme
        st.markdown(f"## {t('color_theme')}")
        
        preset_themes = {
            "Default (Blue-Purple)": {"primary": "#667eea", "secondary": "#a9019b"},
            "Emerald (Green-Teal)": {"primary": "#2ecc71", "secondary": "#27ae60"},
            "Sunset (Orange-Coral)": {"primary": "#e74c3c", "secondary": "#c0392b"},
            "Ocean (Deep Blue)": {"primary": "#3498db", "secondary": "#2980b9"},
            "Royal (Purple-Pink)": {"primary": "#9b59b6", "secondary": "#e84393"},
            "Forest (Dark Green)": {"primary": "#27ae60", "secondary": "#2ecc71"},
            "Cherry (Red-Pink)": {"primary": "#e84393", "secondary": "#9b59b6"},
            "Amber (Yellow-Orange)": {"primary": "#f39c12", "secondary": "#e67e22"},
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
                t('select_color'),
                value=st.session_state.primary_color
            )
            st.session_state.primary_color = selected_color
            st.session_state.secondary_color = get_complementary_color(selected_color)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(
                f'<div style="text-align: center;">'
                f'<div class="color-preview" style="background: {st.session_state.primary_color};"></div>'
                f'<div style="font-size: 11px; margin-top: 5px;">{t("primary")}</div>'
                f'</div>',
                unsafe_allow_html=True
            )
        with col2:
            st.markdown(
                f'<div style="text-align: center;">'
                f'<div class="color-preview" style="background: {st.session_state.secondary_color};"></div>'
                f'<div style="font-size: 11px; margin-top: 5px;">{t("secondary")}</div>'
                f'</div>',
                unsafe_allow_html=True
            )
        
        st.markdown(
            f'<div class="complementary-preview" style="height: 8px; width: 100%; margin: 10px 0;"></div>',
            unsafe_allow_html=True
        )
        
        st.markdown("---")
        
        st.markdown(f"## {t('upload_logo')}")
        journal_logo_upload = st.file_uploader(
            t('upload_logo'),
            type=['png', 'jpg', 'jpeg', 'svg'],
            help=t('logo_help')
        )
        
        st.markdown("---")
        
        st.markdown(f"""
        <div style="font-size: 11px; color: #666; text-align: center;">
            © daM / Chimica Techno Acta \ https://chimicatechnoacta.ru
        </div>
        """, unsafe_allow_html=True)
    
    # Main content
    st.markdown("---")
    if os.path.exists("icon.png"):
        col_logo, col_text = st.columns([1, 3])
        with col_logo:
            st.image("icon.png", width=400)
    else:
        st.markdown(f"### {t('journal_analysis')}")
    st.markdown("---")
    
    # Input section
    st.header(t('journal_analysis'))
    
    col1, col2, col3 = st.columns([2, 2, 1])
    
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
    
    with col3:
        workers_slider = st.slider(
            t('workers_count'),
            min_value=4,
            max_value=12,
            value=8,
            step=1,
            help=t('workers_help')
        )
    
    journal_logo_data = None
    if journal_logo_upload:
        journal_logo_data = {
            journal_logo_upload.name: {
                'content': journal_logo_upload.read()
            }
        }
    
    if st.button(t('analyze_button'), type="primary", width='stretch'):
        issn = issn_input.strip()
        period_str = period_input.strip()
        
        if not issn:
            st.error(t('no_issn'))
        elif not period_str:
            st.error(t('no_period'))
        else:
            period = parse_period(period_str)
            if period is None:
                st.error(t('no_period'))
            else:
                run_journal_analysis(issn, period, workers_slider, journal_logo_data)

if __name__ == "__main__":
    main()
