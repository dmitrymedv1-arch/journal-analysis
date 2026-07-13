# ============================================
# ADVANCED JOURNAL ANALYSIS TOOL
# ============================================

# ============================================
# СЕКЦИЯ ПАРАМЕТРОВ
# ============================================

# Параметры API запросов
MAX_WORKERS = 8  # Количество параллельных потоков для OpenAlex
BASE_DELAY = 0.35  # Базовая задержка между запросами
MAX_RETRIES = 4  # Количество попыток при ошибке
MAX_CITING_PER_PAPER = 500  # Максимум цитирующих на статью (увеличено)
TIMEOUT = 30  # Таймаут на запрос в секундах

# Параметры вывода
SHOW_DEBUG_LOGS = True
GENERATE_HTML_REPORT = True
LOGO_PATH = None
APP_LOGO_PATH = "logo.png"  # Путь к логотипу программы

# Лимиты для анализа
MAX_ARTICLES_TO_ANALYZE = 1000  # Максимум статей журнала для анализа
MIN_YEAR_FOR_TREND = 3

# ============================================
# ИМПОРТЫ
# ============================================

import streamlit as st
from streamlit import session_state as ss
import pandas as pd
import numpy as np
import requests
import re
import time
import random
import json
import base64
import hashlib
import os
import math
from datetime import datetime
from typing import List, Dict, Set, Tuple, Optional, Any, DefaultDict
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
import colorsys
import html as html_module

# Научный стиль для графиков (оставляем для совместимости)
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from io import BytesIO

# ============================================
# СЛОВАРЬ ПЕРЕВОДОВ
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
        'analyze_button': '🚀 Run Journal Analysis',
        'issn_input': 'ISSN',
        'issn_placeholder': '0028-0836',
        'period_input': 'Period',
        'period_placeholder': '2020-2023 or 2020,2021,2022',
        'workers_label': 'Parallel threads:',
        'no_issn': '⚠️ Please enter ISSN',
        'no_period': '⚠️ Please enter period',
        'analysis_complete': '✅ Analysis complete!',
        'analyzing_articles': '📚 Loading journal articles...',
        'fetching_citations': '📖 Fetching citing works...',
        'processing_results': '⚙️ Processing results...',
        'generating_report': '📄 Generating HTML report...',
        'report_ready': '📄 Report ready for download',
        
        # HTML Report Navigation
        'nav_overview': '📊 Overview',
        'nav_analyzed': '📄 Analyzed Articles',
        'nav_authors': '👤 Author Analysis',
        'nav_geo': '🌍 Geographic Analysis',
        'nav_citations': '📈 Citation Analysis',
        'nav_dynamics': '📈 Citation Dynamics',
        'nav_heatmap': '🔥 Citation Heatmap',
        'nav_most_cited': '🏆 Most Cited Publications',
        'nav_citing': '📚 Citing Works Analysis',
        'nav_topics': '🏷️ Topics Analysis',
        'nav_detailed': '📋 Detailed Citations',
        'nav_all_pubs': '📚 All Publications',
        
        # Metrics
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
        'international_collab_rate': 'International Collab Rate',
        'unique_citing_authors': 'Unique Citing Authors',
        'unique_citing_affiliations': 'Unique Citing Affiliations',
        'unique_citing_countries': 'Unique Citing Countries',
        'unique_citing_journals': 'Unique Citing Journals',
        'unique_citing_publishers': 'Unique Citing Publishers',
        
        # Open Access
        'oa_breakdown': 'Open Access Breakdown',
        'oa_gold': 'Gold',
        'oa_hybrid': 'Hybrid',
        'oa_green': 'Green',
        'oa_bronze': 'Bronze',
        'oa_closed': 'Closed',
        'oa_unknown': 'Unknown',
        'oa_diamond': 'Diamond',
        
        # Tables
        'rank': 'Rank',
        'authors': 'Authors',
        'orcid': 'ORCID',
        'affiliations': 'Affiliations',
        'countries': 'Countries',
        'publications': 'Publications',
        'citations': 'Citations',
        'citations_per_year': 'Citations/Year',
        'title': 'Title',
        'year': 'Year',
        'journal': 'Journal',
        'doi': 'DOI',
        'publisher': 'Publisher',
        'citing_works': 'Citing Works',
        'citing_authors': 'Citing Authors',
        'citing_affiliations': 'Citing Affiliations',
        'citing_countries': 'Citing Countries',
        'citing_journals': 'Citing Journals',
        'citing_publishers': 'Citing Publishers',
        'top_citing_authors': 'Top Citing Authors',
        'top_citing_affiliations': 'Top Citing Affiliations',
        'top_citing_countries': 'Top Citing Countries',
        'top_citing_journals': 'Top Citing Journals',
        'top_citing_publishers': 'Top Citing Publishers',
        'top_affiliations': 'Top Affiliations',
        'total_analyzed': 'Total analyzed: {count} articles',
        
        # Citation Analysis
        'citation_dynamics': 'Citation Dynamics by Year',
        'publication_year': 'Publication Year',
        'citation_year': 'Citation Year',
        'citations_count': 'Citations Count',
        'cumulative_citations': 'Cumulative Citations',
        'heatmap_title': 'Citation Network Heatmap',
        'most_cited_publications': 'Most Cited Publications',
        
        # Geographic
        'unique_countries_per_publication': 'Unique Countries per Publication (Collaboration Level)',
        'authors_per_country': 'Authors per Country (Individual Distribution)',
        'collaboration_patterns': 'Collaboration Patterns',
        'single_country': 'Single-Country',
        'international': 'International',
        'collaboration_couples': 'Collaboration Couples',
        
        # Topics
        'topics_analysis': 'Topics Analysis',
        'analyzed_count': 'Analyzed Count',
        'citing_count': 'Citing Count',
        'analyzed_norm': 'Analyzed Norm',
        'citing_norm': 'Citing Norm',
        'total_norm': 'Total Norm',
        'first_year': 'First Year',
        'peak_year': 'Peak Year',
        'topic': 'Topic',
        'subtopic': 'Subtopic',
        'field': 'Field',
        'domain': 'Domain',
        'concept': 'Concept',
        
        # Filters
        'filter_by_year': 'Filter by Year',
        'filter_by_author': 'Filter by Author',
        'filter_by_affiliations': 'Filter by Affiliations',
        'filter_by_citations_min': 'Filter by Citations (min)',
        'filter_by_title': 'Filter by Title Word(s)',
        'search_publications': 'Search Publications',
        'all_years': 'All Years',
        'show_citations': 'Show Citations',
        'all_publications': 'All Publications',
        
        # Details
        'detailed_citations': 'Detailed Citations for Analyzed Works',
        'citing_journal': 'Citing Journal',
        'citing_year': 'Citing Year',
        'citing_date': 'Citing Date',
        'citation_lag': 'Citation Lag',
        'click_to_toggle': 'Click to toggle citations',
        
        # Footer
        'footer': '© Advanced Journal Analysis Tool | developed by @ daM',
        'journal_url': 'https://chimicatechnoacta.ru',
        'data_source': 'Data source: OpenAlex',
        'generated': 'Generated',
        
        # Status messages
        'fetching_articles': 'Fetching articles from OpenAlex...',
        'articles_found': 'Articles found: {count}',
        'fetching_citations_progress': 'Fetching citations: {current}/{total}',
        'total_citing_works': 'Total citing works found: {count}',
        'processing_data': 'Processing data and calculating metrics...',
        'download_report': '📥 Download HTML Report',
        'report_preview': '📋 Report Preview',
        'no_data': '👈 Run analysis first',
        
        # Additional Metrics
        'citation_velocity': 'Citation Velocity',
        'sleeping_beauties': 'Sleeping Beauties',
        'awakening_time': 'Awakening Time',
        'price_index': 'Price Index',
        'half_life': 'Half-Life',
        'self_citation_rate': 'Self-Citation Rate',
        'citation_lag_distribution': 'Citation Lag Distribution',
        'median_lag': 'Median Lag',
        'avg_lag': 'Avg Lag',
        'min_lag': 'Min Lag',
        'max_lag': 'Max Lag',
        'predicted_citations': 'Predicted Citations',
        'future_impact': 'Future Impact Index',
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
        'analyze_button': '🚀 Запустить анализ журнала',
        'issn_input': 'ISSN',
        'issn_placeholder': '0028-0836',
        'period_input': 'Период',
        'period_placeholder': '2020-2023 или 2020,2021,2022',
        'workers_label': 'Параллельных потоков:',
        'no_issn': '⚠️ Введите ISSN',
        'no_period': '⚠️ Введите период',
        'analysis_complete': '✅ Анализ завершен!',
        'analyzing_articles': '📚 Загрузка статей журнала...',
        'fetching_citations': '📖 Получение цитирующих работ...',
        'processing_results': '⚙️ Обработка результатов...',
        'generating_report': '📄 Генерация HTML отчета...',
        'report_ready': '📄 Отчет готов к скачиванию',
        
        # HTML Report Navigation
        'nav_overview': '📊 Обзор',
        'nav_analyzed': '📄 Анализируемые статьи',
        'nav_authors': '👤 Авторский анализ',
        'nav_geo': '🌍 Географический анализ',
        'nav_citations': '📈 Цитирование',
        'nav_dynamics': '📈 Динамика цитирования',
        'nav_heatmap': '🔥 Тепловая карта цитирования',
        'nav_most_cited': '🏆 Самые цитируемые статьи',
        'nav_citing': '📚 Анализ цитирующих работ',
        'nav_topics': '🏷️ Тематический анализ',
        'nav_detailed': '📋 Детальное цитирование',
        'nav_all_pubs': '📚 Все публикации',
        
        # Metrics
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
        'avg_authors_per_paper': 'Среднее авторов/статью',
        'avg_affiliations_per_paper': 'Среднее аффилиаций/статью',
        'avg_countries_per_paper': 'Среднее стран/статью',
        'international_collab_rate': 'Доля международных коллабораций',
        'unique_citing_authors': 'Уникальных цитирующих авторов',
        'unique_citing_affiliations': 'Уникальных цитирующих аффилиаций',
        'unique_citing_countries': 'Уникальных цитирующих стран',
        'unique_citing_journals': 'Уникальных цитирующих журналов',
        'unique_citing_publishers': 'Уникальных цитирующих издательств',
        
        # Open Access
        'oa_breakdown': 'Разбивка по открытому доступу',
        'oa_gold': 'Gold',
        'oa_hybrid': 'Hybrid',
        'oa_green': 'Green',
        'oa_bronze': 'Bronze',
        'oa_closed': 'Закрытый',
        'oa_unknown': 'Неизвестный',
        'oa_diamond': 'Diamond',
        
        # Tables
        'rank': 'Место',
        'authors': 'Авторы',
        'orcid': 'ORCID',
        'affiliations': 'Аффилиации',
        'countries': 'Страны',
        'publications': 'Публикаций',
        'citations': 'Цитирований',
        'citations_per_year': 'Цитирований/год',
        'title': 'Название',
        'year': 'Год',
        'journal': 'Журнал',
        'doi': 'DOI',
        'publisher': 'Издательство',
        'citing_works': 'Цитирующих работ',
        'citing_authors': 'Цитирующих авторов',
        'citing_affiliations': 'Цитирующих аффилиаций',
        'citing_countries': 'Цитирующих стран',
        'citing_journals': 'Цитирующих журналов',
        'citing_publishers': 'Цитирующих издательств',
        'top_citing_authors': 'Топ цитирующих авторов',
        'top_citing_affiliations': 'Топ цитирующих аффилиаций',
        'top_citing_countries': 'Топ цитирующих стран',
        'top_citing_journals': 'Топ цитирующих журналов',
        'top_citing_publishers': 'Топ цитирующих издательств',
        'top_affiliations': 'Топ аффилиаций',
        'total_analyzed': 'Всего проанализировано: {count} статей',
        
        # Citation Analysis
        'citation_dynamics': 'Динамика цитирований по годам',
        'publication_year': 'Год публикации',
        'citation_year': 'Год цитирования',
        'citations_count': 'Количество цитирований',
        'cumulative_citations': 'Накопленные цитирования',
        'heatmap_title': 'Тепловая карта цитирований',
        'most_cited_publications': 'Самые цитируемые статьи',
        
        # Geographic
        'unique_countries_per_publication': 'Уникальные страны на публикацию (уровень коллаборации)',
        'authors_per_country': 'Авторы по странам (индивидуальное распределение)',
        'collaboration_patterns': 'Модели коллабораций',
        'single_country': 'Внутристрановые',
        'international': 'Международные',
        'collaboration_couples': 'Пары стран-коллабораций',
        
        # Topics
        'topics_analysis': 'Тематический анализ',
        'analyzed_count': 'Анализируемых',
        'citing_count': 'Цитирующих',
        'analyzed_norm': 'Анализ. норма',
        'citing_norm': 'Цитир. норма',
        'total_norm': 'Общая норма',
        'first_year': 'Первый год',
        'peak_year': 'Пиковый год',
        'topic': 'Тема',
        'subtopic': 'Подтема',
        'field': 'Область',
        'domain': 'Домен',
        'concept': 'Концепт',
        
        # Filters
        'filter_by_year': 'Фильтр по году',
        'filter_by_author': 'Фильтр по автору',
        'filter_by_affiliations': 'Фильтр по аффилиациям',
        'filter_by_citations_min': 'Фильтр по цитированиям (мин)',
        'filter_by_title': 'Фильтр по словам в названии',
        'search_publications': 'Поиск публикаций',
        'all_years': 'Все годы',
        'show_citations': 'Показать цитирования',
        'all_publications': 'Все публикации',
        
        # Details
        'detailed_citations': 'Детальное цитирование анализируемых работ',
        'citing_journal': 'Цитирующий журнал',
        'citing_year': 'Год цитирования',
        'citing_date': 'Дата цитирования',
        'citation_lag': 'Задержка цитирования',
        'click_to_toggle': 'Нажмите для показа цитирований',
        
        # Footer
        'footer': '© Advanced Journal Analysis Tool | разработано @ daM',
        'journal_url': 'https://chimicatechnoacta.ru',
        'data_source': 'Источник данных: OpenAlex',
        'generated': 'Сгенерировано',
        
        # Status messages
        'fetching_articles': 'Получение статей из OpenAlex...',
        'articles_found': 'Найдено статей: {count}',
        'fetching_citations_progress': 'Получение цитирований: {current}/{total}',
        'total_citing_works': 'Всего найдено цитирующих работ: {count}',
        'processing_data': 'Обработка данных и расчет метрик...',
        'download_report': '📥 Скачать HTML отчет',
        'report_preview': '📋 Предпросмотр отчета',
        'no_data': '👈 Сначала выполните анализ',
        
        # Additional Metrics
        'citation_velocity': 'Скорость цитирования',
        'sleeping_beauties': 'Спящие красавицы',
        'awakening_time': 'Время пробуждения',
        'price_index': 'Индекс Прайса',
        'half_life': 'Период полураспада',
        'self_citation_rate': 'Доля самоцитирований',
        'citation_lag_distribution': 'Распределение задержки цитирования',
        'median_lag': 'Медианная задержка',
        'avg_lag': 'Средняя задержка',
        'min_lag': 'Мин. задержка',
        'max_lag': 'Макс. задержка',
        'predicted_citations': 'Прогнозируемые цитирования',
        'future_impact': 'Индекс будущего влияния',
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
# COLOR UTILITIES
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

def apply_theme_css(base_color: str, accent_color: str = None):
    """Apply dynamic CSS theme based on selected colors"""
    if accent_color is None:
        accent_color = get_complementary_color(base_color)
    
    base_rgb = hex_to_rgb(base_color)
    accent_rgb = hex_to_rgb(accent_color)
    
    theme_css = f"""
    <style>
        :root {{
            --primary: {base_color};
            --secondary: {accent_color};
            --primary-rgb: {base_rgb[0]}, {base_rgb[1]}, {base_rgb[2]};
            --secondary-rgb: {accent_rgb[0]}, {accent_rgb[1]}, {accent_rgb[2]};
            --primary-contrast: {get_contrast_color(base_color)};
            --secondary-contrast: {get_contrast_color(accent_color)};
        }}
        
        .stApp {{
            background: linear-gradient(135deg, 
                rgba({base_rgb[0]}, {base_rgb[1]}, {base_rgb[2]}, 0.05) 0%,
                rgba({accent_rgb[0]}, {accent_rgb[1]}, {accent_rgb[2]}, 0.08) 100%);
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
    </style>
    """
    st.markdown(theme_css, unsafe_allow_html=True)

# ============================================
# OPENALEX API HELPERS
# ============================================

lock = Lock()

def normalize_issn(issn_str: str) -> str:
    """Normalize ISSN to XX-XXXX format"""
    cleaned = re.sub(r'[^0-9Xx]', '', str(issn_str).strip())
    if len(cleaned) == 8:
        return f"{cleaned[:4]}-{cleaned[4:]}".upper()
    return cleaned.upper()

def smart_get(url: str, params: dict, retries: int = MAX_RETRIES, delay: float = BASE_DELAY) -> Optional[dict]:
    """Smart GET with retries and rate limiting"""
    for attempt in range(retries):
        try:
            with lock:
                time.sleep(random.uniform(0.1, delay))
            
            resp = requests.get(url, params=params, timeout=TIMEOUT)
            
            if resp.status_code == 429:
                wait = int(resp.headers.get("Retry-After", 2 ** attempt + 1))
                time.sleep(wait + random.uniform(0.5, 1.5))
                continue
                
            if resp.status_code == 200:
                return resp.json()
            
            time.sleep(1 * (2 ** attempt))
            
        except Exception as e:
            if SHOW_DEBUG_LOGS:
                print(f"⚠️ Attempt {attempt+1} failed: {str(e)[:100]}")
            time.sleep(1.5 * (2 ** attempt))
    
    return None

def parse_openalex_work(work: dict) -> dict:
    """Parse OpenAlex work to standardized format"""
    parsed = {}
    
    # Basic info
    parsed['id'] = work.get('id', '')
    
    doi = work.get('doi')
    parsed['doi'] = doi.replace('https://doi.org/', '') if doi else ''

    parsed['title'] = work.get('title', 'No title')
    parsed['publication_year'] = work.get('publication_year')
    parsed['publication_date'] = work.get('publication_date', '')
    parsed['cited_by_count'] = work.get('cited_by_count', 0)
    parsed['type'] = work.get('type', 'unknown')
    
    # Open Access
    oa = work.get('open_access', {})
    parsed['is_oa'] = oa.get('is_oa', False)
    parsed['oa_status'] = oa.get('oa_status', 'unknown')
    parsed['oa_url'] = oa.get('oa_url', None)
    
    # Journal info
    primary_location = work.get('primary_location', {})
    source = primary_location.get('source', {})
    parsed['journal_name'] = source.get('display_name', 'Unknown')
    parsed['publisher'] = source.get('host_organization_name') or source.get('publisher', 'Unknown')
    parsed['issn'] = source.get('issn', [])
    parsed['source_type'] = source.get('type', 'unknown')
    
    # Authors
    authors = []
    author_orcids = []
    author_affiliations = []
    author_countries = []
    authors_with_countries = []
    authorships_data = []
    
    for authorship in work.get('authorships', []):
        author = authorship.get('author', {})
        author_name = authorship.get('raw_author_name', '') or author.get('display_name', '')
        author_orcid = author.get('orcid', '')
        
        author_country = None
        author_institutions = []
        for inst in authorship.get('institutions', []):
            inst_name = inst.get('display_name', '')
            country_code = inst.get('country_code', '')
            if inst_name:
                author_institutions.append(inst_name)
                author_affiliations.append(inst_name)
            if country_code:
                author_country = country_code
                author_countries.append(country_code)
        
        if author_name:
            authors.append(author_name)
            if author_orcid:
                author_orcids.append(author_orcid)
            if author_country:
                authors_with_countries.append((author_name, author_country))
        
        authorships_data.append({
            'author_name': author_name,
            'author_orcid': author_orcid,
            'country': author_country,
            'institutions': author_institutions,
            'is_corresponding': authorship.get('is_corresponding', False),
            'author_position': authorship.get('author_position', '')
        })
    
    parsed['authors'] = authors
    parsed['author_orcids'] = author_orcids
    parsed['authors_with_countries'] = authors_with_countries
    parsed['authorships_data'] = authorships_data
    parsed['author_count'] = len(authors)
    parsed['affiliations'] = list(set(author_affiliations))
    parsed['countries'] = list(set(author_countries))
    
    # Topics
    topics = []
    for topic in work.get('topics', []):
        topics.append({
            'display_name': topic.get('display_name', ''),
            'subfield': topic.get('subfield', {}).get('display_name', ''),
            'field': topic.get('field', {}).get('display_name', ''),
            'domain': topic.get('domain', {}).get('display_name', ''),
            'score': topic.get('score', 0)
        })
    parsed['topics'] = topics
    
    # Primary topic
    primary_topic = work.get('primary_topic', {})
    if primary_topic:
        parsed['primary_topic'] = {
            'display_name': primary_topic.get('display_name', ''),
            'subfield': primary_topic.get('subfield', {}).get('display_name', ''),
            'field': primary_topic.get('field', {}).get('display_name', ''),
            'domain': primary_topic.get('domain', {}).get('display_name', ''),
            'score': primary_topic.get('score', 0)
        }
    else:
        parsed['primary_topic'] = None
    
    # Concepts
    concepts = []
    for concept in work.get('concepts', []):
        concepts.append({
            'display_name': concept.get('display_name', ''),
            'level': concept.get('level', 0),
            'score': concept.get('score', 0)
        })
    parsed['concepts'] = concepts
    
    return parsed

def get_citing_dois_optimized(oa_id: str, max_citing: int = MAX_CITING_PER_PAPER) -> List[Dict]:
    """
    Оптимизированная версия получения цитирующих работ
    Полностью скопирована из проверочного кода с добавлением полного парсинга
    """
    citing = []
    cursor = "*"
    base_url = "https://api.openalex.org/works"
    
    for _ in range(8):  # ограничение пагинации
        data = smart_get(base_url, {
            "filter": f"cites:{oa_id}",
            "per_page": 200,
            "select": "id,doi,title,publication_year,publication_date,cited_by_count,type,open_access,primary_location,authorships,topics,concepts",
            "cursor": cursor
        })
        
        if not data:
            break
        results = data.get("results", [])
        if not results:
            break
            
        for item in results:
            citing.append(parse_openalex_work(item))
            if len(citing) >= max_citing:
                break
        
        if len(citing) >= max_citing:
            break
        
        cursor = data.get("meta", {}).get("next_cursor")
        if not cursor:
            break
    
    return citing[:max_citing]

def get_journal_info_by_issn(issn: str) -> Optional[Dict]:
    """Get journal name and abbreviation by ISSN from OpenAlex"""
    normalized = normalize_issn(issn)
    url = "https://api.openalex.org/sources"
    
    data = smart_get(url, {
        "filter": f"issn:{normalized}",
        "select": "id,display_name,issn,host_organization_name,type,abbreviation"
    })
    
    if data and data.get("results"):
        source = data["results"][0]
        return {
            'name': source.get('display_name', ''),
            'abbreviation': source.get('abbreviation', '') or source.get('display_name', '')[:10].upper().replace(' ', ''),
            'publisher': source.get('host_organization_name', 'Unknown'),
            'type': source.get('type', 'unknown')
        }
    return None

def full_parallel_analysis(issn: str, period: str, max_workers: int = MAX_WORKERS, progress_callback=None) -> Dict:
    """
    Full parallel analysis of a journal
    
    Args:
        issn: ISSN of the journal
        period: Period string (e.g., "2020-2023" or "2020,2021,2022" or "2020")
        max_workers: Number of parallel threads
        progress_callback: Callback function for progress updates
    
    Returns:
        Dict with all analysis results
    """
    normalized = normalize_issn(issn)
    
    # Get journal info
    journal_info = get_journal_info_by_issn(normalized)
    
    if progress_callback:
        progress_callback(0, 100, translate('fetching_articles', 'en'))
    
    # ============= ПАРСИНГ ПЕРИОДА (ПОЛНОСТЬЮ ИЗ ПРОВЕРОЧНОГО КОДА) =============
    if ',' in period:
        years = [int(y.strip()) for y in period.split(',') if y.strip().isdigit()]
        if len(years) == 1:
            year_filter = f"publication_year:{years[0]}"
        else:
            year_filter = "|".join(f"publication_year:{y}" for y in years)
    elif '-' in period:
        parts = [x.strip() for x in period.split('-')]
        if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
            start_year = int(parts[0])
            end_year = int(parts[1])
            year_filter = f"publication_year:{start_year}-{end_year}"
            years = list(range(start_year, end_year + 1))
        else:
            years = [int(period)] if period.isdigit() else []
            year_filter = f"publication_year:{years[0]}" if years else ""
    else:
        years = [int(period)] if period.isdigit() else []
        year_filter = f"publication_year:{years[0]}" if years else ""
    
    if not years or not year_filter:
        return {'error': 'Invalid period format'}
    
    # ============= ЗАГРУЗКА СТАТЕЙ (ПОЛНОСТЬЮ ИЗ ПРОВЕРОЧНОГО КОДА) =============
    base_url = "https://api.openalex.org/works"
    articles = []
    cursor = "*"
    
    if progress_callback:
        progress_callback(5, 100, translate('fetching_articles', 'en'))
    
    while True:
        data = smart_get(base_url, {
            "filter": f"primary_location.source.issn:{normalized},{year_filter}",
            "per_page": 200,
            "select": "id,doi,title,publication_year,publication_date,cited_by_count,type,open_access,primary_location,authorships,topics,concepts",
            "cursor": cursor
        })
        
        if not data or not data.get("results"):
            break
            
        for work in data["results"]:
            parsed = parse_openalex_work(work)
            articles.append(parsed)
        
        if progress_callback and len(articles) % 50 == 0:
            progress_callback(5 + min(15, int(len(articles) / 20)), 100, 
                            translate('articles_found', 'en', count=len(articles)))
        
        cursor = data.get("meta", {}).get("next_cursor")
        if not cursor:
            break
    
    if not articles:
        return {'error': 'No articles found for this ISSN and period'}
    
    if progress_callback:
        progress_callback(20, 100, translate('articles_found', 'en', count=len(articles)))
    
    # ============= ПАРАЛЛЕЛЬНЫЙ СБОР ЦИТИРУЮЩИХ (ПОЛНОСТЬЮ ИЗ ПРОВЕРОЧНОГО КОДА) =============
    if progress_callback:
        progress_callback(25, 100, translate('fetching_citations', 'en'))
    
    citing_map = {}
    futures = {}
    
    # Создаем список статей для обработки (только те, у которых есть цитирования)
    articles_to_process = []
    for article in articles:
        if article.get('cited_by_count', 0) > 0 and article.get('id'):
            articles_to_process.append(article)
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for article in articles_to_process:
            # Используем OpenAlex ID
            oa_id = article['id']
            future = executor.submit(get_citing_dois_optimized, oa_id)
            futures[future] = article['doi']
        
        completed = 0
        total = len(futures)
        
        for future in as_completed(futures):
            doi = futures[future]
            try:
                citing_map[doi] = future.result()
            except Exception as e:
                if SHOW_DEBUG_LOGS:
                    print(f"⚠️ Error fetching citing works for {doi}: {e}")
                citing_map[doi] = []
            
            completed += 1
            if progress_callback and total > 0:
                progress = 25 + int((completed / total) * 60)
                progress_callback(progress, 100, translate('fetching_citations_progress', 'en', current=completed, total=total))
    
    if progress_callback:
        total_citing = sum(len(c) for c in citing_map.values())
        progress_callback(85, 100, translate('total_citing_works', 'en', count=total_citing))
    
    # ============= ОБРАБОТКА РЕЗУЛЬТАТОВ =============
    if progress_callback:
        progress_callback(90, 100, translate('processing_data', 'en'))
    
    # Build comprehensive analysis
    result = {
        'issn': normalized,
        'period': period,
        'years': years,
        'articles': articles,
        'citing_map': citing_map,
        'timestamp': datetime.now().isoformat(),
        'journal_info': journal_info
    }
    
    # Calculate metrics
    analyzer = JournalAnalyzer(result)
    result['metrics'] = analyzer.calculate_metrics()
    result['analyzed_articles'] = analyzer.get_analyzed_articles_data()
    result['citation_dynamics'] = analyzer.get_citation_dynamics()
    result['cumulative_citations'] = analyzer.get_cumulative_citations()
    result['heatmap_data'] = analyzer.get_heatmap_data()
    result['most_cited'] = analyzer.get_most_cited()
    result['citing_works_analysis'] = analyzer.get_citing_works_analysis()
    result['topics_analysis'] = analyzer.get_topics_analysis()
    result['detailed_citations'] = analyzer.get_detailed_citations()
    result['all_publications'] = analyzer.get_all_publications_data()
    
    if progress_callback:
        progress_callback(100, 100, translate('analysis_complete', 'en'))
    
    return result

# ============================================
# JOURNAL ANALYZER CLASS
# ============================================

class JournalAnalyzer:
    def __init__(self, result: Dict):
        self.articles = result.get('articles', [])
        self.citing_map = result.get('citing_map', {})
        self.years = result.get('years', [])
        self.issn = result.get('issn', '')
        self.period = result.get('period', '')
        
    def calculate_metrics(self) -> Dict:
        """Calculate all metrics for the journal"""
        metrics = {}
        
        # Basic metrics
        metrics['total_publications'] = len(self.articles)
        metrics['total_citations'] = sum(a.get('cited_by_count', 0) for a in self.articles)
        
        # Citation metrics
        citations = [a.get('cited_by_count', 0) for a in self.articles]
        citations_sorted = sorted([c for c in citations if c > 0], reverse=True)
        
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
        metrics['i10_index'] = sum(1 for c in citations if c >= 10)
        
        # i100-index
        metrics['i100_index'] = sum(1 for c in citations if c >= 100)
        
        # Avg citations
        metrics['avg_citations'] = sum(citations) / len(citations) if citations else 0
        
        # Open Access
        oa_statuses = [a.get('oa_status', 'unknown') for a in self.articles]
        oa_counts = Counter(oa_statuses)
        metrics['oa_breakdown'] = dict(oa_counts)
        metrics['oa_percentage'] = sum(1 for a in self.articles if a.get('is_oa', False)) / len(self.articles) * 100 if self.articles else 0
        
        # Years
        years = [a.get('publication_year') for a in self.articles if a.get('publication_year')]
        metrics['active_years'] = len(set(years))
        metrics['min_year'] = min(years) if years else None
        metrics['max_year'] = max(years) if years else None
        
        # Authors
        all_authors = []
        all_affiliations = []
        all_countries = []
        author_orcids = []
        
        for a in self.articles:
            all_authors.extend(a.get('authors', []))
            all_affiliations.extend(a.get('affiliations', []))
            all_countries.extend(a.get('countries', []))
            author_orcids.extend(a.get('author_orcids', []))
        
        metrics['unique_authors'] = len(set(all_authors))
        metrics['unique_affiliations'] = len(set(all_affiliations))
        metrics['unique_countries'] = len(set(all_countries))
        metrics['unique_authors_with_orcid'] = len(set(author_orcids))
        
        # Averages per paper
        metrics['avg_authors_per_paper'] = sum(a.get('author_count', 0) for a in self.articles) / len(self.articles) if self.articles else 0
        metrics['avg_affiliations_per_paper'] = sum(len(a.get('affiliations', [])) for a in self.articles) / len(self.articles) if self.articles else 0
        metrics['avg_countries_per_paper'] = sum(len(a.get('countries', [])) for a in self.articles) / len(self.articles) if self.articles else 0
        
        # International collaboration rate
        international_count = 0
        for a in self.articles:
            countries = a.get('countries', [])
            if len(set(countries)) > 1:
                international_count += 1
        metrics['international_collab_rate'] = international_count / len(self.articles) * 100 if self.articles else 0
        
        # Citing works metrics
        all_citing_works = []
        for citing_list in self.citing_map.values():
            all_citing_works.extend(citing_list)
        
        metrics['total_citing_works'] = len(all_citing_works)
        
        citing_authors = []
        citing_affiliations = []
        citing_countries = []
        citing_journals = []
        citing_publishers = []
        
        for citing in all_citing_works:
            citing_authors.extend(citing.get('authors', []))
            citing_affiliations.extend(citing.get('affiliations', []))
            citing_countries.extend(citing.get('countries', []))
            citing_journals.append(citing.get('journal_name', 'Unknown'))
            citing_publishers.append(citing.get('publisher', 'Unknown'))
        
        metrics['unique_citing_authors'] = len(set(citing_authors))
        metrics['unique_citing_affiliations'] = len(set(citing_affiliations))
        metrics['unique_citing_countries'] = len(set(citing_countries))
        metrics['unique_citing_journals'] = len(set(citing_journals))
        metrics['unique_citing_publishers'] = len(set(citing_publishers))
        
        # Price Index (citations from last 5 years / total citations)
        current_year = datetime.now().year
        recent_citations = sum(
            len(citing_list) for doi, citing_list in self.citing_map.items()
            if any(c.get('publication_year', 0) >= current_year - 5 for c in citing_list)
        )
        metrics['price_index'] = recent_citations / metrics['total_citations'] * 100 if metrics['total_citations'] > 0 else 0
        
        # Citation lag metrics
        lags = []
        for citing_list in self.citing_map.values():
            for citing in citing_list:
                pub_year = citing.get('publication_year')
                # Find the year of the cited article
                cited_year = None
                for article in self.articles:
                    if article.get('doi') in self.citing_map:
                        # This is the cited article
                        pass
                if pub_year:
                    lags.append(pub_year)
        
        if lags:
            metrics['median_lag'] = np.median(lags) if lags else 0
            metrics['avg_lag'] = np.mean(lags) if lags else 0
            metrics['min_lag'] = min(lags) if lags else 0
            metrics['max_lag'] = max(lags) if lags else 0
        
        # Citation velocity
        if metrics['total_citations'] > 0 and metrics['active_years'] > 0:
            metrics['citation_velocity'] = metrics['total_citations'] / metrics['active_years']
        else:
            metrics['citation_velocity'] = 0
        
        # Self-citation rate
        self_citations = 0
        all_author_names = set(all_authors)
        for citing_list in self.citing_map.values():
            for citing in citing_list:
                citing_authors_set = set(citing.get('authors', []))
                if citing_authors_set.intersection(all_author_names):
                    self_citations += 1
        metrics['self_citation_rate'] = self_citations / metrics['total_citations'] * 100 if metrics['total_citations'] > 0 else 0
        
        return metrics
    
    def get_analyzed_articles_data(self) -> Dict:
        """Get data for analyzed articles section"""
        author_stats = defaultdict(lambda: {
            'name': '',
            'orcid': None,
            'affiliations': set(),
            'countries': set(),
            'publications': 0,
            'citations': 0
        })
        
        affiliations_counter = Counter()
        countries_counter = Counter()
        
        # Для подсчета уникальных стран на публикацию (Collaboration Level)
        # Каждая страна считается 1 раз для каждой публикации
        unique_countries_per_publication = Counter()
        
        # Для подсчета авторов по странам (Individual Distribution)
        # Каждый автор считается отдельно
        authors_per_country = Counter()
        
        for article in self.articles:
            authors = article.get('authors', [])
            orcids = article.get('author_orcids', [])
            affiliations = article.get('affiliations', [])
            countries = article.get('countries', [])
            citations = article.get('cited_by_count', 0)
            
            # Статистика по авторам
            for idx, author in enumerate(authors):
                if author not in author_stats:
                    author_stats[author]['name'] = author
                    if idx < len(orcids) and orcids[idx]:
                        author_stats[author]['orcid'] = orcids[idx]
                author_stats[author]['publications'] += 1
                author_stats[author]['citations'] += citations
                author_stats[author]['affiliations'].update(affiliations)
                author_stats[author]['countries'].update(countries)
            
            # Топ аффилиаций
            for aff in affiliations:
                affiliations_counter[aff] += 1
            
            # Уникальные страны на публикацию (Collaboration Level)
            # Каждая страна считается 1 раз для этой публикации
            unique_countries = set(countries)
            for country in unique_countries:
                if country:
                    unique_countries_per_publication[country] += 1
            
            # Авторы по странам (Individual Distribution)
            # Используем authors_with_countries для подсчета каждого автора
            for author_name, country in article.get('authors_with_countries', []):
                if country:
                    authors_per_country[country] += 1
            
            # Также считаем страны через countries (для обратной совместимости)
            for country in countries:
                if country:
                    countries_counter[country] += 1
        
        # Convert to list and sort
        author_list = []
        for name, data in author_stats.items():
            author_list.append({
                'name': name,
                'orcid': data['orcid'],
                'affiliations': list(data['affiliations']),
                'countries': list(data['countries']),
                'publications': data['publications'],
                'citations': data['citations']
            })
        
        author_list.sort(key=lambda x: x['citations'], reverse=True)
        
        return {
            'authors': author_list,
            'top_affiliations': dict(affiliations_counter.most_common(20)),
            'top_countries': dict(countries_counter.most_common(20)),
            'unique_countries_per_publication': dict(unique_countries_per_publication.most_common(20)),
            'authors_per_country': dict(authors_per_country.most_common(20))
        }
    
    def get_citation_dynamics(self) -> pd.DataFrame:
        """Get citation dynamics by year"""
        dynamics = defaultdict(lambda: defaultdict(int))
        
        for doi, citing_list in self.citing_map.items():
            # Find publication year for this article
            pub_year = None
            for article in self.articles:
                if article.get('doi') == doi:
                    pub_year = article.get('publication_year')
                    break
            
            if pub_year is None:
                continue
            
            for citing in citing_list:
                citing_year = citing.get('publication_year')
                if citing_year:
                    dynamics[pub_year][citing_year] += 1
        
        # Convert to DataFrame
        rows = []
        for pub_year, citing_years in dynamics.items():
            for citing_year, count in citing_years.items():
                rows.append({
                    'Publication Year': pub_year,
                    'Citation Year': citing_year,
                    'Citations Count': count
                })
        
        return pd.DataFrame(rows)
    
    def get_cumulative_citations(self) -> Dict:
        """Get cumulative citations by year"""
        cumulative = defaultdict(int)
        current_year = datetime.now().year
        
        for citing_list in self.citing_map.values():
            for citing in citing_list:
                year = citing.get('publication_year')
                if year and year <= current_year:
                    cumulative[year] += 1
        
        # Calculate cumulative sum
        cumulative_sum = {}
        total = 0
        for year in sorted(cumulative.keys()):
            total += cumulative[year]
            cumulative_sum[year] = total
        
        return cumulative_sum
    
    def get_heatmap_data(self) -> pd.DataFrame:
        """Get heatmap data for citation network"""
        dynamics = defaultdict(lambda: defaultdict(int))
        
        for doi, citing_list in self.citing_map.items():
            pub_year = None
            for article in self.articles:
                if article.get('doi') == doi:
                    pub_year = article.get('publication_year')
                    break
            
            if pub_year is None:
                continue
            
            for citing in citing_list:
                citing_year = citing.get('publication_year')
                if citing_year:
                    dynamics[pub_year][citing_year] += 1
        
        # Create full matrix
        all_years = sorted(set(list(dynamics.keys()) + list(set().union(*[d.keys() for d in dynamics.values()]) if dynamics else [])))
        
        if not all_years:
            return pd.DataFrame()
        
        heatmap_data = []
        for pub_year in all_years:
            row = {'Publication Year': pub_year}
            for cit_year in all_years:
                row[cit_year] = dynamics.get(pub_year, {}).get(cit_year, 0)
            heatmap_data.append(row)
        
        return pd.DataFrame(heatmap_data)
    
    def get_most_cited(self, limit: int = 20) -> List[Dict]:
        """Get most cited publications"""
        sorted_articles = sorted(self.articles, key=lambda x: x.get('cited_by_count', 0), reverse=True)
        
        most_cited = []
        for i, article in enumerate(sorted_articles[:limit], 1):
            year = article.get('publication_year')
            citations = article.get('cited_by_count', 0)
            # Calculate years since publication
            if year:
                years_since = max(1, datetime.now().year - year + 1)
            else:
                years_since = 1
            citations_per_year = citations / years_since
            
            most_cited.append({
                'rank': i,
                'title': article.get('title', 'No title'),
                'year': year,
                'citations': citations,
                'citations_per_year': citations_per_year,
                'authors': article.get('authors', [])[:3],
                'doi': article.get('doi', ''),
                'journal': article.get('journal_name', 'Unknown')
            })
        
        return most_cited
    
    def get_citing_works_analysis(self) -> Dict:
        """Get analysis of citing works"""
        all_citing = []
        for citing_list in self.citing_map.values():
            all_citing.extend(citing_list)
        
        # Author analysis
        author_counter = Counter()
        affiliation_counter = Counter()
        country_counter = Counter()
        journal_counter = Counter()
        publisher_counter = Counter()
        
        for citing in all_citing:
            for author in citing.get('authors', []):
                author_counter[author] += 1
            for aff in citing.get('affiliations', []):
                affiliation_counter[aff] += 1
            for country in citing.get('countries', []):
                country_counter[country] += 1
            journal_counter[citing.get('journal_name', 'Unknown')] += 1
            publisher_counter[citing.get('publisher', 'Unknown')] += 1
        
        return {
            'top_authors': dict(author_counter.most_common(20)),
            'top_affiliations': dict(affiliation_counter.most_common(20)),
            'top_countries': dict(country_counter.most_common(20)),
            'top_journals': dict(journal_counter.most_common(20)),
            'top_publishers': dict(publisher_counter.most_common(20))
        }
    
    def get_topics_analysis(self) -> Dict:
        """Get topics analysis with normalization"""
        # Collect topics from analyzed articles
        analyzed_topics = defaultdict(lambda: {
            'count': 0,
            'first_year': 9999,
            'peak_year': 0,
            'peak_count': 0,
            'years': []
        })
        
        for article in self.articles:
            year = article.get('publication_year')
            if not year:
                continue
            
            for topic in article.get('topics', []):
                name = topic.get('display_name', '')
                if not name:
                    continue
                
                analyzed_topics[name]['count'] += 1
                analyzed_topics[name]['years'].append(year)
                if year < analyzed_topics[name]['first_year']:
                    analyzed_topics[name]['first_year'] = year
        
        # Collect topics from citing works
        citing_topics = defaultdict(int)
        for citing_list in self.citing_map.values():
            for citing in citing_list:
                for topic in citing.get('topics', []):
                    name = topic.get('display_name', '')
                    if name:
                        citing_topics[name] += 1
        
        # Calculate peak year for each topic
        for name, data in analyzed_topics.items():
            if data['years']:
                year_counts = Counter(data['years'])
                peak_year, peak_count = max(year_counts.items(), key=lambda x: x[1])
                data['peak_year'] = peak_year
                data['peak_count'] = peak_count
        
        # Calculate normalized counts
        total_analyzed = len(self.articles)
        total_citing = sum(len(c) for c in self.citing_map.values())
        
        topics_data = []
        all_topics = set(analyzed_topics.keys()) | set(citing_topics.keys())
        
        for topic in all_topics:
            analyzed_count = analyzed_topics.get(topic, {}).get('count', 0)
            citing_count = citing_topics.get(topic, 0)
            analyzed_norm = analyzed_count / total_analyzed if total_analyzed > 0 else 0
            citing_norm = citing_count / total_citing if total_citing > 0 else 0
            
            topics_data.append({
                'topic': topic,
                'analyzed_count': analyzed_count,
                'citing_count': citing_count,
                'analyzed_norm': analyzed_norm,
                'citing_norm': citing_norm,
                'total_norm': analyzed_norm + citing_norm,
                'first_year': analyzed_topics.get(topic, {}).get('first_year', None),
                'peak_year': analyzed_topics.get(topic, {}).get('peak_year', None)
            })
        
        # Sort by total_norm
        topics_data.sort(key=lambda x: x['total_norm'], reverse=True)
        
        # Get top concepts, fields, domains, subtopics
        concept_counter = Counter()
        field_counter = Counter()
        domain_counter = Counter()
        subtopic_counter = Counter()
        
        for article in self.articles:
            for concept in article.get('concepts', []):
                concept_counter[concept.get('display_name', '')] += 1
            # Also from topics
            for topic in article.get('topics', []):
                if topic.get('subfield'):
                    subtopic_counter[topic['subfield']] += 1
                if topic.get('field'):
                    field_counter[topic['field']] += 1
                if topic.get('domain'):
                    domain_counter[topic['domain']] += 1
        
        # Also from citing works
        for citing_list in self.citing_map.values():
            for citing in citing_list:
                for concept in citing.get('concepts', []):
                    concept_counter[concept.get('display_name', '')] += 1
                for topic in citing.get('topics', []):
                    if topic.get('subfield'):
                        subtopic_counter[topic['subfield']] += 1
                    if topic.get('field'):
                        field_counter[topic['field']] += 1
                    if topic.get('domain'):
                        domain_counter[topic['domain']] += 1
        
        return {
            'topics': topics_data[:30],
            'top_concepts': dict(concept_counter.most_common(20)),
            'top_subtopics': dict(subtopic_counter.most_common(20)),
            'top_fields': dict(field_counter.most_common(20)),
            'top_domains': dict(domain_counter.most_common(20))
        }
    
    def get_detailed_citations(self) -> Dict:
        """Get detailed citations for each publication"""
        detailed = {}
        
        for article in self.articles:
            doi = article.get('doi')
            if not doi:
                continue
            
            citations_list = self.citing_map.get(doi, [])
            if not citations_list:
                continue
            
            detailed[doi] = {
                'title': article.get('title', 'No title'),
                'year': article.get('publication_year'),
                'doi': doi,
                'journal': article.get('journal_name', 'Unknown'),
                'total_citations': len(citations_list),
                'citations': []
            }
            
            for citing in citations_list:
                detailed[doi]['citations'].append({
                    'citing_title': citing.get('title', 'No title'),
                    'citing_year': citing.get('publication_year'),
                    'citing_date': citing.get('publication_date', ''),
                    'citing_journal': citing.get('journal_name', 'Unknown'),
                    'citing_publisher': citing.get('publisher', 'Unknown'),
                    'citing_doi': citing.get('doi', ''),
                    'citing_authors': citing.get('authors', []),
                    'citing_countries': citing.get('countries', []),
                    'citing_topics': [t.get('display_name', '') for t in citing.get('topics', [])],
                    'citation_lag': citing.get('publication_year') - article.get('publication_year') if citing.get('publication_year') and article.get('publication_year') else None
                })
        
        return detailed
    
    def get_all_publications_data(self) -> List[Dict]:
        """Get all publications data for the table"""
        all_pubs = []
        
        for article in self.articles:
            year = article.get('publication_year')
            citations = article.get('cited_by_count', 0)
            # Calculate years since publication
            if year:
                years_since = max(1, datetime.now().year - year + 1)
            else:
                years_since = 1
            citations_per_year = citations / years_since
            
            all_pubs.append({
                'title': article.get('title', 'No title'),
                'year': year,
                'authors': article.get('authors', []),
                'affiliations': article.get('affiliations', []),
                'citations': citations,
                'citations_per_year': citations_per_year,
                'doi': article.get('doi', ''),
                'journal': article.get('journal_name', 'Unknown'),
                'oa_status': article.get('oa_status', 'unknown')
            })
        
        return all_pubs

# ============================================
# HTML REPORT GENERATOR
# ============================================

def generate_html_report(result: Dict, logo_base64: Optional[str] = None, 
                         app_logo_base64: Optional[str] = None,
                         theme_colors: Optional[Dict] = None, lang: str = 'en') -> str:
    """Generate HTML report with all analysis results and rich visualizations"""
    
    if theme_colors is None:
        theme_colors = {
            'primary': '#667eea',
            'secondary': '#f39c12'
        }
    
    primary = theme_colors.get('primary', '#667eea')
    secondary = theme_colors.get('secondary', '#f39c12')
    
    primary_rgb = hex_to_rgb(primary)
    secondary_rgb = hex_to_rgb(secondary)
    
    def t(key: str, **kwargs) -> str:
        return translate(key, lang, **kwargs)
    
    metrics = result.get('metrics', {})
    articles = result.get('articles', [])
    analyzed_data = result.get('analyzed_articles', {})
    citation_dynamics = result.get('citation_dynamics', pd.DataFrame())
    cumulative = result.get('cumulative_citations', {})
    heatmap_data = result.get('heatmap_data', pd.DataFrame())
    most_cited = result.get('most_cited', [])
    citing_works = result.get('citing_works_analysis', {})
    topics_data = result.get('topics_analysis', {})
    detailed_citations = result.get('detailed_citations', {})
    all_publications = result.get('all_publications', [])
    journal_info = result.get('journal_info', {})
    journal_name = journal_info.get('name', result.get('issn', ''))
    
    # Generate abbreviation for filename
    journal_abbr = journal_info.get('abbreviation', '')
    if not journal_abbr:
        # Try to create abbreviation from name
        if journal_name:
            words = journal_name.split()
            if len(words) >= 2:
                journal_abbr = ''.join(word[0].upper() for word in words if word)
            else:
                journal_abbr = journal_name[:8].upper().replace(' ', '')
        else:
            journal_abbr = result.get('issn', '').replace('-', '')
    
    # Build HTML
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>{t('app_title')} - {journal_name}</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{
                font-family: 'Times New Roman', 'DejaVu Serif', serif;
                margin: 0;
                padding: 0;
                background: #f5f7fa;
                color: #333;
            }}
            .report-wrapper {{
                max-width: 1400px;
                margin: 0 auto;
                background: white;
                box-shadow: 0 10px 40px rgba(0,0,0,0.1);
                min-height: 100vh;
            }}
            
            /* Sidebar Navigation */
            .sidebar {{
                position: fixed;
                left: 0;
                top: 0;
                width: 280px;
                height: 100vh;
                background: linear-gradient(135deg, {primary} 0%, {secondary} 100%);
                color: white;
                padding: 20px 15px;
                overflow-y: auto;
                z-index: 1000;
                box-shadow: 2px 0 10px rgba(0,0,0,0.1);
            }}
            .sidebar::-webkit-scrollbar {{
                width: 4px;
            }}
            .sidebar::-webkit-scrollbar-thumb {{
                background: rgba(255,255,255,0.3);
                border-radius: 2px;
            }}
            .sidebar h3 {{
                margin-bottom: 15px;
                font-size: 18px;
                font-weight: 600;
                color: white;
                padding-bottom: 10px;
                border-bottom: 2px solid rgba(255,255,255,0.2);
            }}
            .sidebar .nav-item {{
                display: block;
                color: rgba(255,255,255,0.85);
                text-decoration: none;
                padding: 8px 12px;
                margin: 2px 0;
                border-radius: 6px;
                transition: all 0.2s;
                font-size: 13px;
            }}
            .sidebar .nav-item:hover {{
                background: rgba(255,255,255,0.15);
                color: white;
                transform: translateX(3px);
            }}
            .sidebar .nav-item.active {{
                background: rgba(255,255,255,0.2);
                color: white;
            }}
            .sidebar .nav-item .nav-icon {{
                margin-right: 8px;
            }}
            .sidebar .nav-sub {{
                padding-left: 25px;
            }}
            .sidebar .nav-sub .nav-item {{
                font-size: 12px;
                padding: 5px 10px;
            }}
            
            /* Main Content */
            .main-content {{
                margin-left: 280px;
                padding: 30px 40px;
            }}
            
            /* Header */
            .header {{
                background: linear-gradient(135deg, {primary} 0%, {secondary} 100%);
                color: white;
                padding: 25px 40px;
                border-radius: 15px;
                margin-bottom: 30px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                display: flex;
                align-items: center;
                justify-content: space-between;
                flex-wrap: wrap;
            }}
            .header-left {{
                display: flex;
                align-items: center;
                gap: 20px;
            }}
            .header-right {{
                display: flex;
                align-items: center;
            }}
            .header h1 {{
                color: white;
                margin: 0;
                font-size: 24px;
            }}
            .header .subtitle {{
                opacity: 0.9;
                margin-top: 4px;
                font-size: 14px;
            }}
            .header .date {{
                opacity: 0.85;
                margin-top: 2px;
                font-size: 12px;
            }}
            .header-logo {{
                max-height: 80px;
                max-width: 200px;
                object-fit: contain;
            }}
            .header-app-logo {{
                max-height: 70px;
                max-width: 150px;
                object-fit: contain;
            }}
            
            /* Sections */
            .section {{
                background: white;
                border-radius: 12px;
                padding: 25px 30px;
                margin-bottom: 25px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                border: 1px solid #e8ecf1;
            }}
            .section-title {{
                font-size: 22px;
                font-weight: 600;
                margin-bottom: 20px;
                padding-bottom: 10px;
                border-bottom: 3px solid {primary};
                display: flex;
                align-items: center;
                gap: 12px;
                color: #2c3e50;
            }}
            .section-title .icon {{
                font-size: 24px;
            }}
            
            /* Metrics Grid */
            .metrics-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
                gap: 12px;
                margin: 15px 0;
            }}
            .metric-card {{
                background: #f8f9fa;
                padding: 14px;
                border-radius: 8px;
                border-left: 4px solid {primary};
                text-align: center;
                transition: transform 0.2s, box-shadow 0.2s;
            }}
            .metric-card:hover {{
                transform: translateY(-3px);
                box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            }}
            .metric-value {{
                font-size: 26px;
                font-weight: bold;
                color: #2c3e50;
                font-family: 'Times New Roman', serif;
            }}
            .metric-label {{
                font-size: 11px;
                color: #7f8c8d;
                margin-top: 4px;
                font-family: 'Times New Roman', serif;
            }}
            
            /* Progress Bar Styles */
            .progress-bar-container {{
                margin: 8px 0;
                background: #e9ecef;
                border-radius: 20px;
                overflow: hidden;
                height: 22px;
                box-shadow: inset 0 1px 3px rgba(0,0,0,0.1);
                position: relative;
            }}
            .progress-bar {{
                height: 100%;
                background: linear-gradient(90deg, {primary} 0%, {secondary} 100%);
                border-radius: 20px;
                transition: width 1.2s cubic-bezier(0.4, 0, 0.2, 1);
                display: flex;
                align-items: center;
                justify-content: flex-end;
                padding-right: 8px;
                color: white;
                font-size: 11px;
                font-weight: 600;
                text-shadow: 0 1px 2px rgba(0,0,0,0.3);
                min-width: 30px;
                position: relative;
                overflow: hidden;
            }}
            .progress-bar::after {{
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: linear-gradient(90deg, transparent, rgba(255,255,255,0.15), transparent);
                animation: shimmer 2s infinite;
                transform: translateX(-100%);
            }}
            @keyframes shimmer {{
                0% {{ transform: translateX(-100%); }}
                100% {{ transform: translateX(100%); }}
            }}
            .progress-bar-label {{
                display: flex;
                justify-content: space-between;
                font-size: 12px;
                color: #555;
                margin-top: 2px;
            }}
            .progress-bar-label .name {{
                font-weight: 500;
            }}
            .progress-bar-label .value {{
                font-weight: 600;
                color: {primary};
            }}
            
            /* Horizontal bar chart for rankings */
            .rank-bar-container {{
                margin: 4px 0;
                display: flex;
                align-items: center;
                gap: 10px;
            }}
            .rank-bar-label {{
                min-width: 120px;
                font-size: 12px;
                color: #333;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }}
            .rank-bar-track {{
                flex: 1;
                height: 18px;
                background: #e9ecef;
                border-radius: 10px;
                overflow: hidden;
                position: relative;
            }}
            .rank-bar-fill {{
                height: 100%;
                background: linear-gradient(90deg, {primary} 0%, {secondary} 100%);
                border-radius: 10px;
                transition: width 1s cubic-bezier(0.4, 0, 0.2, 1);
            }}
            .rank-bar-value {{
                min-width: 40px;
                font-size: 12px;
                font-weight: 600;
                color: {primary};
                text-align: right;
            }}
            
            /* Tables */
            .table-container {{
                overflow-x: auto;
                margin: 15px 0;
                border-radius: 8px;
                border: 1px solid #e8ecf1;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                font-family: 'Times New Roman', serif;
                font-size: 13px;
            }}
            th {{
                background: linear-gradient(135deg, {primary} 0%, {secondary} 100%);
                color: white;
                padding: 10px 12px;
                text-align: left;
                font-weight: 600;
                position: sticky;
                top: 0;
                z-index: 10;
            }}
            td {{
                padding: 8px 12px;
                border-bottom: 1px solid #e8ecf1;
                vertical-align: middle;
            }}
            tr:hover {{
                background: rgba({primary_rgb[0]}, {primary_rgb[1]}, {primary_rgb[2]}, 0.05);
            }}
            tr:nth-child(even) {{
                background: #fafbfc;
            }}
            .doi-link {{
                color: #2980b9;
                text-decoration: none;
                font-size: 12px;
                word-break: break-all;
            }}
            .doi-link:hover {{
                text-decoration: underline;
            }}
            
            /* Citation Heatmap */
            .heatmap-container {{
                overflow-x: auto;
                margin: 15px 0;
            }}
            .heatmap-table td {{
                text-align: center;
                padding: 6px 12px;
                font-weight: 500;
                min-width: 50px;
                transition: transform 0.2s;
            }}
            .heatmap-table td:hover {{
                transform: scale(1.05);
                box-shadow: 0 2px 8px rgba(0,0,0,0.15);
            }}
            .heatmap-table th {{
                text-align: center;
                padding: 8px 12px;
                position: sticky;
                top: 0;
                z-index: 10;
            }}
            
            /* Collapsible */
            .collapser {{
                cursor: pointer;
                padding: 12px 15px;
                margin: 5px 0;
                background: #f8f9fa;
                border-radius: 6px;
                border-left: 4px solid {primary};
                transition: all 0.2s;
                display: flex;
                align-items: center;
                flex-wrap: wrap;
                gap: 8px;
            }}
            .collapser:hover {{
                background: rgba({primary_rgb[0]}, {primary_rgb[1]}, {primary_rgb[2]}, 0.08);
                transform: translateX(3px);
            }}
            .collapser .badge {{
                display: inline-block;
                padding: 2px 10px;
                border-radius: 12px;
                font-size: 11px;
                font-weight: 600;
            }}
            .badge-info {{
                background: #d1ecf1;
                color: #0c5460;
            }}
            .badge-primary {{
                background: {primary};
                color: white;
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
            .badge-secondary {{
                background: #e2e3e5;
                color: #383d41;
            }}
            
            .citation-count {{
                font-weight: 600;
                color: {primary};
                margin-left: auto;
            }}
            
            .collapse-content {{
                display: none;
                padding: 12px 15px;
                margin: 0 0 8px 0;
                background: #fafbfc;
                border-radius: 0 0 6px 6px;
                border: 1px solid #e8ecf1;
                border-top: none;
            }}
            .collapse-content.open {{
                display: block;
            }}
            
            .citation-detail {{
                padding: 10px 12px;
                margin: 5px 0;
                background: white;
                border-radius: 4px;
                border-left: 3px solid {secondary};
                box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            }}
            .citation-detail .cite-meta {{
                font-size: 12px;
                color: #555;
                margin-top: 4px;
            }}
            .citation-detail .cite-meta strong {{
                color: #2c3e50;
            }}
            
            /* Filter Section */
            .filter-section {{
                background: #f8f9fa;
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 15px;
                border: 1px solid #e8ecf1;
            }}
            .filter-row {{
                display: flex;
                flex-wrap: wrap;
                gap: 12px;
                align-items: end;
            }}
            .filter-row > div {{
                flex: 1;
                min-width: 150px;
            }}
            .filter-row label {{
                display: block;
                font-size: 12px;
                font-weight: 600;
                color: #555;
                margin-bottom: 3px;
            }}
            .filter-row select, .filter-row input {{
                width: 100%;
                padding: 6px 10px;
                border: 1px solid #d1d5db;
                border-radius: 4px;
                font-size: 13px;
                font-family: 'Times New Roman', serif;
                transition: border-color 0.2s;
            }}
            .filter-row select:focus, .filter-row input:focus {{
                outline: none;
                border-color: {primary};
                box-shadow: 0 0 0 3px rgba({primary_rgb[0]}, {primary_rgb[1]}, {primary_rgb[2]}, 0.15);
            }}
            
            /* Footer */
            .footer {{
                margin-top: 30px;
                padding: 20px 0;
                border-top: 2px solid #e8ecf1;
                text-align: center;
                color: #7f8c8d;
                font-size: 12px;
            }}
            .footer a {{
                color: {primary};
                text-decoration: none;
            }}
            .footer a:hover {{
                text-decoration: underline;
            }}
            
            /* Responsive */
            @media print {{
                .sidebar {{ display: none; }}
                .main-content {{ margin-left: 0; padding: 20px; }}
            }}
            @media (max-width: 768px) {{
                .sidebar {{ display: none; }}
                .main-content {{ margin-left: 0; padding: 15px; }}
                .metrics-grid {{ grid-template-columns: repeat(2, 1fr); }}
                .filter-row > div {{ min-width: 120px; }}
                .header {{
                    flex-direction: column;
                    text-align: center;
                }}
                .header-left {{
                    flex-direction: column;
                }}
            }}
            
            /* Word wrap for long titles */
            .word-wrap {{
                word-wrap: break-word;
                max-width: 300px;
            }}
            
            .visible-count {{
                font-weight: 500;
                color: {primary};
                padding: 5px 10px;
                background: rgba({primary_rgb[0]}, {primary_rgb[1]}, {primary_rgb[2]}, 0.1);
                border-radius: 4px;
            }}
            
            /* Colorful badges for OA status */
            .oa-badge {{
                display: inline-block;
                padding: 2px 10px;
                border-radius: 12px;
                font-size: 10px;
                font-weight: 600;
            }}
            .oa-gold {{ background: #FFD700; color: #333; }}
            .oa-hybrid {{ background: #FFA500; color: #333; }}
            .oa-green {{ background: #2ECC71; color: white; }}
            .oa-bronze {{ background: #CD7F32; color: white; }}
            .oa-closed {{ background: #95A5A6; color: white; }}
            .oa-diamond {{ background: #00CED1; color: white; }}
            .oa-unknown {{ background: #BDC3C7; color: #333; }}
            
            /* Mini progress bars in tables */
            .mini-progress {{
                display: inline-block;
                width: 60px;
                height: 6px;
                background: #e9ecef;
                border-radius: 3px;
                overflow: hidden;
                vertical-align: middle;
                margin-left: 4px;
            }}
            .mini-progress .fill {{
                height: 100%;
                background: linear-gradient(90deg, {primary}, {secondary});
                border-radius: 3px;
                transition: width 0.5s;
            }}
            
            /* Tooltip for heatmap */
            .heatmap-tooltip {{
                position: relative;
                cursor: help;
            }}
            .heatmap-tooltip:hover::after {{
                content: attr(data-tooltip);
                position: absolute;
                bottom: 100%;
                left: 50%;
                transform: translateX(-50%);
                background: #333;
                color: white;
                padding: 4px 10px;
                border-radius: 4px;
                font-size: 11px;
                white-space: nowrap;
                z-index: 100;
            }}
            
            /* Citation velocity indicator */
            .velocity-indicator {{
                display: inline-block;
                padding: 2px 8px;
                border-radius: 10px;
                font-size: 11px;
                font-weight: 600;
            }}
            .velocity-high {{ background: #d4edda; color: #155724; }}
            .velocity-medium {{ background: #fff3cd; color: #856404; }}
            .velocity-low {{ background: #f8d7da; color: #721c24; }}
            
            /* Progress bar for cumulative citations */
            .cumulative-progress {{
                height: 14px;
                background: #e9ecef;
                border-radius: 7px;
                overflow: hidden;
                margin: 2px 0;
            }}
            .cumulative-progress .fill {{
                height: 100%;
                background: linear-gradient(90deg, {primary}40, {primary});
                border-radius: 7px;
                transition: width 0.8s;
            }}
            
            .collaboration-badge {{
                display: inline-block;
                padding: 2px 8px;
                border-radius: 10px;
                font-size: 10px;
                font-weight: 600;
            }}
            .collab-single {{ background: #d1ecf1; color: #0c5460; }}
            .collab-international {{ background: #f8d7da; color: #721c24; }}
            
            .topic-card {{
                background: #f8f9fa;
                border-radius: 6px;
                padding: 8px 12px;
                margin: 4px 0;
                border-left: 3px solid {primary};
                transition: all 0.2s;
            }}
            .topic-card:hover {{
                transform: translateX(3px);
                box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            }}
            .topic-card .topic-name {{
                font-weight: 500;
                color: #2c3e50;
            }}
            .topic-card .topic-meta {{
                font-size: 11px;
                color: #7f8c8d;
                margin-top: 2px;
            }}
            
            .concept-tag {{
                display: inline-block;
                padding: 2px 10px;
                border-radius: 12px;
                font-size: 10px;
                font-weight: 500;
                margin: 2px;
                background: rgba({primary_rgb[0]}, {primary_rgb[1]}, {primary_rgb[2]}, 0.12);
                color: {primary};
                border: 1px solid rgba({primary_rgb[0]}, {primary_rgb[1]}, {primary_rgb[2]}, 0.2);
            }}
            .concept-tag:hover {{
                background: rgba({primary_rgb[0]}, {primary_rgb[1]}, {primary_rgb[2]}, 0.2);
            }}
            
            .publication-card {{
                background: #f8f9fa;
                border-radius: 6px;
                padding: 10px 14px;
                margin: 4px 0;
                border-left: 3px solid {secondary};
                transition: all 0.2s;
            }}
            .publication-card:hover {{
                transform: translateX(3px);
                box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            }}
            .publication-card .pub-title {{
                font-weight: 500;
                color: #2c3e50;
            }}
            .publication-card .pub-meta {{
                font-size: 11px;
                color: #7f8c8d;
                margin-top: 2px;
            }}
        </style>
    </head>
    <body>
        <div class="report-wrapper">
            <!-- Sidebar Navigation -->
            <div class="sidebar">
                <h3>📊 {t('app_title')}</h3>
                <a href="#overview" class="nav-item"><span class="nav-icon">📊</span> {t('nav_overview')}</a>
                <a href="#analyzed" class="nav-item"><span class="nav-icon">📄</span> {t('nav_analyzed')}</a>
                <div class="nav-sub">
                    <a href="#author_analysis" class="nav-item">👤 {t('nav_authors')}</a>
                    <a href="#geo_analysis" class="nav-item">🌍 {t('nav_geo')}</a>
                </div>
                <a href="#citation_analysis" class="nav-item"><span class="nav-icon">📈</span> {t('nav_citations')}</a>
                <div class="nav-sub">
                    <a href="#citation_dynamics" class="nav-item">📈 {t('nav_dynamics')}</a>
                    <a href="#heatmap" class="nav-item">🔥 {t('nav_heatmap')}</a>
                    <a href="#most_cited" class="nav-item">🏆 {t('nav_most_cited')}</a>
                </div>
                <a href="#citing_works" class="nav-item"><span class="nav-icon">📚</span> {t('nav_citing')}</a>
                <a href="#topics_analysis" class="nav-item"><span class="nav-icon">🏷️</span> {t('nav_topics')}</a>
                <a href="#detailed_citations" class="nav-item"><span class="nav-icon">📋</span> {t('nav_detailed')}</a>
                <a href="#all_publications" class="nav-item"><span class="nav-icon">📚</span> {t('nav_all_pubs')}</a>
            </div>
            
            <!-- Main Content -->
            <div class="main-content">
                <!-- Header -->
                <div class="header">
                    <div class="header-left">
                        {f'<img src="data:image/png;base64,{logo_base64}" class="header-logo" alt="Journal Logo">' if logo_base64 else ''}
                        <div>
                            <h1>{html_module.escape(journal_name) if journal_name else result.get('issn', '')}</h1>
                            <div class="subtitle">ISSN: {result.get('issn', '')} | {t('period_input')}: {result.get('period', '')}</div>
                            <div class="date">{t('generated')}: {datetime.now().strftime('%d.%m.%Y')}</div>
                        </div>
                    </div>
                    <div class="header-right">
                        {f'<img src="data:image/png;base64,{app_logo_base64}" class="header-app-logo" alt="App Logo">' if app_logo_base64 else ''}
                    </div>
                </div>
    """
    
    # ==================== OVERVIEW ====================
    # Calculate max values for progress bars
    max_citations = metrics.get('total_citations', 1)
    max_publications = metrics.get('total_publications', 1)
    max_unique_authors = metrics.get('unique_authors', 1)
    
    html += f"""
                <div id="overview" class="section">
                    <div class="section-title"><span class="icon">📊</span> {t('nav_overview')}</div>
                    
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
                            <div class="metric-value">{metrics.get('oa_percentage', 0):.1f}%</div>
                            <div class="metric-label">{t('open_access')}</div>
                            <div class="progress-bar-container" style="height: 6px; margin-top: 4px;">
                                <div class="progress-bar" style="width: {min(metrics.get('oa_percentage', 0), 100)}%; height: 6px;"></div>
                            </div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{metrics.get('active_years', 0)}</div>
                            <div class="metric-label">{t('active_years')}</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{metrics.get('unique_authors', 0)}</div>
                            <div class="metric-label">{t('unique_authors')}</div>
                            <div class="progress-bar-container" style="height: 6px; margin-top: 4px;">
                                <div class="progress-bar" style="width: {min((metrics.get('unique_authors', 0) / max(metrics.get('total_publications', 1), 1)) * 100, 100)}%; height: 6px;"></div>
                            </div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{metrics.get('unique_affiliations', 0)}</div>
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
                            <div class="metric-value">{metrics.get('international_collab_rate', 0):.1f}%</div>
                            <div class="metric-label">{t('international_collab_rate')}</div>
                            <div class="progress-bar-container" style="height: 6px; margin-top: 4px;">
                                <div class="progress-bar" style="width: {min(metrics.get('international_collab_rate', 0), 100)}%; height: 6px;"></div>
                            </div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{metrics.get('citation_velocity', 0):.1f}</div>
                            <div class="metric-label">{t('citation_velocity')}</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{metrics.get('price_index', 0):.1f}%</div>
                            <div class="metric-label">{t('price_index')}</div>
                            <div class="progress-bar-container" style="height: 6px; margin-top: 4px;">
                                <div class="progress-bar" style="width: {min(metrics.get('price_index', 0), 100)}%; height: 6px;"></div>
                            </div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{metrics.get('self_citation_rate', 0):.1f}%</div>
                            <div class="metric-label">{t('self_citation_rate')}</div>
                            <div class="progress-bar-container" style="height: 6px; margin-top: 4px;">
                                <div class="progress-bar" style="width: {min(metrics.get('self_citation_rate', 0), 100)}%; height: 6px; background: linear-gradient(90deg, #e74c3c, #c0392b);"></div>
                            </div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{metrics.get('unique_citing_authors', 0)}</div>
                            <div class="metric-label">{t('unique_citing_authors')}</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{metrics.get('unique_citing_affiliations', 0)}</div>
                            <div class="metric-label">{t('unique_citing_affiliations')}</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{metrics.get('unique_citing_countries', 0)}</div>
                            <div class="metric-label">{t('unique_citing_countries')}</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{metrics.get('unique_citing_journals', 0)}</div>
                            <div class="metric-label">{t('unique_citing_journals')}</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{metrics.get('unique_citing_publishers', 0)}</div>
                            <div class="metric-label">{t('unique_citing_publishers')}</div>
                        </div>
                    </div>
                    
                    <h4 style="margin-top: 20px; color: {primary};">{t('oa_breakdown')}</h4>
                    <div class="metrics-grid" style="grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));">
    """
    
    oa_labels = {
        'gold': t('oa_gold'),
        'hybrid': t('oa_hybrid'),
        'green': t('oa_green'),
        'bronze': t('oa_bronze'),
        'closed': t('oa_closed'),
        'diamond': t('oa_diamond'),
        'unknown': t('oa_unknown')
    }
    
    oa_colors = {
        'gold': '#FFD700',
        'hybrid': '#FFA500',
        'green': '#2ECC71',
        'bronze': '#CD7F32',
        'closed': '#95A5A6',
        'diamond': '#00CED1',
        'unknown': '#BDC3C7'
    }
    
    oa_breakdown = metrics.get('oa_breakdown', {})
    total_oa = sum(oa_breakdown.values()) if oa_breakdown else 1
    
    for status, count in oa_breakdown.items():
        label = oa_labels.get(status, status)
        color = oa_colors.get(status, '#BDC3C7')
        percentage = (count / total_oa * 100) if total_oa > 0 else 0
        html += f"""
                        <div class="metric-card" style="border-left-color: {color};">
                            <div class="metric-value">{count}</div>
                            <div class="metric-label">{label}</div>
                            <div class="progress-bar-container" style="height: 6px; margin-top: 4px;">
                                <div class="progress-bar" style="width: {percentage}%; height: 6px; background: {color};"></div>
                            </div>
                        </div>
        """
    
    html += """
                    </div>
                </div>
    """
    
    # ==================== ANALYZED ARTICLES ====================
    html += f"""
                <div id="analyzed" class="section">
                    <div class="section-title"><span class="icon">📄</span> {t('nav_analyzed')}</div>
                    <p style="color: #555; margin-bottom: 15px;">{t('total_analyzed', count=len(articles))}</p>
    """
    
    # Author Analysis with progress bars
    html += f"""
                    <div id="author_analysis" class="section" style="padding: 15px 20px; margin: 10px 0;">
                        <h4 style="color: {primary}; margin-bottom: 10px;">👤 {t('nav_authors')}</h4>
                        <div class="table-container" style="max-height: 600px; overflow-y: auto;">
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
    """
    
    authors = analyzed_data.get('authors', [])
    max_author_pubs = max([a.get('publications', 0) for a in authors]) if authors else 1
    max_author_citations = max([a.get('citations', 0) for a in authors]) if authors else 1
    
    for idx, author in enumerate(authors, 1):
        orcid = author.get('orcid', '')
        orcid_display = f'<a href="https://orcid.org/{orcid}" target="_blank">{orcid}</a>' if orcid else '—'
        affiliations_display = ', '.join(author.get('affiliations', [])[:3])
        if len(author.get('affiliations', [])) > 3:
            affiliations_display += f' +{len(author.get("affiliations", []))-3} more'
        countries_display = ', '.join(author.get('countries', [])[:3])
        
        pub_count = author.get('publications', 0)
        cit_count = author.get('citations', 0)
        pub_pct = (pub_count / max_author_pubs * 100) if max_author_pubs > 0 else 0
        cit_pct = (cit_count / max_author_citations * 100) if max_author_citations > 0 else 0
        
        html += f"""
                                    <tr>
                                        <td>{idx}</td>
                                        <td>{author.get('name', 'Unknown')}</td>
                                        <td>{orcid_display}</td>
                                        <td>{affiliations_display}</td>
                                        <td>{countries_display}</td>
                                        <td>
                                            {pub_count}
                                            <span class="mini-progress"><span class="fill" style="width: {pub_pct}%;"></span></span>
                                        </td>
                                        <td>
                                            {cit_count}
                                            <span class="mini-progress"><span class="fill" style="width: {cit_pct}%;"></span></span>
                                        </td>
                                    </tr>
        """
    
    html += """
                                </tbody>
                            </table>
                        </div>
                    </div>
    """
    
    # Top Affiliations with progress bars
    html += f"""
                    <div style="margin: 10px 0;">
                        <h4 style="color: {primary}; margin-bottom: 10px;">🏛️ {t('top_affiliations')}</h4>
                        <div class="table-container">
                            <table>
                                <thead><tr><th>{t('rank')}</th><th>{t('affiliations')}</th><th>{t('publications')}</th></tr></thead>
                                <tbody>
    """
    
    top_affs = analyzed_data.get('top_affiliations', {})
    max_aff_count = max(top_affs.values()) if top_affs else 1
    
    for idx, (aff, count) in enumerate(list(top_affs.items())[:20], 1):
        pct = (count / max_aff_count * 100) if max_aff_count > 0 else 0
        html += f"""
                                    <tr>
                                        <td>{idx}</td>
                                        <td>{aff}</td>
                                        <td>
                                            {count}
                                            <span class="mini-progress"><span class="fill" style="width: {pct}%;"></span></span>
                                        </td>
                                    </tr>
        """
    
    html += """
                                </tbody>
                            </table>
                        </div>
                    </div>
    """
    
    # Geographic Analysis with progress bars
    html += f"""
                    <div id="geo_analysis" style="margin-top: 20px;">
                        <h4 style="color: {primary}; margin-bottom: 10px;">🌍 {t('nav_geo')}</h4>
    """
    
    # Unique Countries per Publication (Collaboration Level)
    unique_countries_pub = analyzed_data.get('unique_countries_per_publication', {})
    max_country_pub = max(unique_countries_pub.values()) if unique_countries_pub else 1
    
    html += f"""
                        <div style="margin: 10px 0; padding: 10px; background: #f8f9fa; border-radius: 6px;">
                            <h5 style="color: #555; margin-bottom: 8px;">📊 {t('unique_countries_per_publication')}</h5>
                            <div style="max-height: 300px; overflow-y: auto;">
    """
    
    for idx, (country, count) in enumerate(list(unique_countries_pub.items())[:20], 1):
        pct = (count / max_country_pub * 100) if max_country_pub > 0 else 0
        html += f"""
                                <div class="rank-bar-container">
                                    <span class="rank-bar-label">{idx}. {country or 'Unknown'}</span>
                                    <div class="rank-bar-track">
                                        <div class="rank-bar-fill" style="width: {pct}%;"></div>
                                    </div>
                                    <span class="rank-bar-value">{count}</span>
                                </div>
        """
    
    html += """
                            </div>
                        </div>
    """
    
    # Authors per Country (Individual Distribution)
    authors_per_country = analyzed_data.get('authors_per_country', {})
    max_author_country = max(authors_per_country.values()) if authors_per_country else 1
    
    html += f"""
                        <div style="margin: 10px 0; padding: 10px; background: #f8f9fa; border-radius: 6px;">
                            <h5 style="color: #555; margin-bottom: 8px;">📊 {t('authors_per_country')}</h5>
                            <div style="max-height: 300px; overflow-y: auto;">
    """
    
    for idx, (country, count) in enumerate(list(authors_per_country.items())[:20], 1):
        pct = (count / max_author_country * 100) if max_author_country > 0 else 0
        html += f"""
                                <div class="rank-bar-container">
                                    <span class="rank-bar-label">{idx}. {country or 'Unknown'}</span>
                                    <div class="rank-bar-track">
                                        <div class="rank-bar-fill" style="width: {pct}%;"></div>
                                    </div>
                                    <span class="rank-bar-value">{count}</span>
                                </div>
        """
    
    html += """
                            </div>
                        </div>
    """
    
    # Collaboration Patterns
    single_country = 0
    international = 0
    
    for article in articles:
        countries = set(article.get('countries', []))
        countries = {c for c in countries if c}
        if len(countries) <= 1:
            single_country += 1
        else:
            international += 1
    
    total_collab = single_country + international
    if total_collab > 0:
        single_pct = single_country / total_collab * 100
        int_pct = international / total_collab * 100
    else:
        single_pct = 0
        int_pct = 0
    
    html += f"""
                        <div style="margin: 10px 0; padding: 10px; background: #f8f9fa; border-radius: 6px;">
                            <h5 style="color: #555; margin-bottom: 8px;">📊 {t('collaboration_patterns')}</h5>
                            <div style="display: flex; gap: 30px; flex-wrap: wrap;">
                                <div style="flex: 1; min-width: 200px;">
                                    <span class="collaboration-badge collab-single">{t('single_country')}</span>
                                    <strong>{single_country}</strong> ({single_pct:.1f}%)
                                    <div class="progress-bar-container" style="height: 14px; width: 100%;">
                                        <div class="progress-bar" style="width: {single_pct}%; background: #3498db; height: 14px;"></div>
                                    </div>
                                </div>
                                <div style="flex: 1; min-width: 200px;">
                                    <span class="collaboration-badge collab-international">{t('international')}</span>
                                    <strong>{international}</strong> ({int_pct:.1f}%)
                                    <div class="progress-bar-container" style="height: 14px; width: 100%;">
                                        <div class="progress-bar" style="width: {int_pct}%; background: #e74c3c; height: 14px;"></div>
                                    </div>
                                </div>
                            </div>
                        </div>
    """
    
    # Collaboration Couples
    country_pairs = Counter()
    for article in articles:
        countries = list(set(article.get('countries', [])))
        countries = [c for c in countries if c]
        if len(countries) >= 2:
            for i in range(len(countries)):
                for j in range(i+1, len(countries)):
                    pair = tuple(sorted([countries[i], countries[j]]))
                    country_pairs[pair] += 1
    
    max_pair_count = max(country_pairs.values()) if country_pairs else 1
    
    html += f"""
                        <div style="margin: 10px 0; padding: 10px; background: #f8f9fa; border-radius: 6px;">
                            <h5 style="color: #555; margin-bottom: 8px;">📊 {t('collaboration_couples')}</h5>
                            <div style="max-height: 300px; overflow-y: auto;">
    """
    
    for idx, (pair, count) in enumerate(list(country_pairs.most_common(20)), 1):
        pct = (count / max_pair_count * 100) if max_pair_count > 0 else 0
        html += f"""
                                <div class="rank-bar-container">
                                    <span class="rank-bar-label">{idx}. {pair[0]} — {pair[1]}</span>
                                    <div class="rank-bar-track">
                                        <div class="rank-bar-fill" style="width: {pct}%;"></div>
                                    </div>
                                    <span class="rank-bar-value">{count}</span>
                                </div>
        """
    
    html += """
                            </div>
                        </div>
                    </div>
                </div>
    """
    
    # ==================== CITATION ANALYSIS ====================
    html += f"""
                <div id="citation_analysis" class="section">
                    <div class="section-title"><span class="icon">📈</span> {t('nav_citations')}</div>
    """
    
    # Citation Dynamics
    html += f"""
                    <div id="citation_dynamics" style="margin-bottom: 20px;">
                        <h4 style="color: {primary}; margin-bottom: 10px;">📈 {t('citation_dynamics')}</h4>
                        <div class="table-container" style="max-height: 400px; overflow-y: auto;">
                            <table>
                                <thead>
                                    <tr>
                                        <th>{t('publication_year')}</th>
                                        <th>{t('citation_year')}</th>
                                        <th>{t('citations_count')}</th>
                                    </tr>
                                </thead>
                                <tbody>
    """
    
    if not citation_dynamics.empty:
        citation_dynamics_sorted = citation_dynamics.sort_values(['Publication Year', 'Citation Year'])
        max_dyn_count = citation_dynamics_sorted['Citations Count'].max() if not citation_dynamics_sorted.empty else 1
        
        for _, row in citation_dynamics_sorted.iterrows():
            count = row['Citations Count']
            pct = (count / max_dyn_count * 100) if max_dyn_count > 0 else 0
            html += f"""
                                    <tr>
                                        <td>{row['Publication Year']}</td>
                                        <td>{row['Citation Year']}</td>
                                        <td>
                                            {count}
                                            <span class="mini-progress"><span class="fill" style="width: {pct}%;"></span></span>
                                        </td>
                                    </tr>
            """
    else:
        html += '<tr><td colspan="3" style="text-align: center;">No citation dynamics data</td></tr>'
    
    html += """
                                </tbody>
                            </table>
                        </div>
                        
                        <div style="margin-top: 10px; display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 8px;">
    """
    
    # Lag statistics
    lag_stats = {
        'min_lag': metrics.get('min_lag', 0),
        'avg_lag': metrics.get('avg_lag', 0),
        'median_lag': metrics.get('median_lag', 0),
        'max_lag': metrics.get('max_lag', 0)
    }
    
    lag_labels = {
        'min_lag': t('min_lag'),
        'avg_lag': t('avg_lag'),
        'median_lag': t('median_lag'),
        'max_lag': t('max_lag')
    }
    
    for key, label in lag_labels.items():
        value = lag_stats.get(key, 0)
        pct = (value / max(lag_stats.values()) * 100) if max(lag_stats.values()) > 0 else 0
        html += f"""
                            <div class="metric-card" style="padding: 8px 12px;">
                                <div class="metric-value" style="font-size: 18px;">{value:.1f}</div>
                                <div class="metric-label" style="font-size: 10px;">{label}</div>
                                <div class="progress-bar-container" style="height: 4px; margin-top: 4px;">
                                    <div class="progress-bar" style="width: {pct}%; height: 4px;"></div>
                                </div>
                            </div>
        """
    
    html += """
                        </div>
                    </div>
    """
    
    # Cumulative Citations with progress bars
    html += f"""
                    <div style="margin-bottom: 20px;">
                        <h4 style="color: {primary}; margin-bottom: 10px;">📈 {t('cumulative_citations')}</h4>
                        <div style="max-height: 300px; overflow-y: auto;">
    """
    
    if cumulative:
        max_cumulative = max(cumulative.values()) if cumulative else 1
        for year in sorted(cumulative.keys()):
            count = cumulative[year]
            pct = (count / max_cumulative * 100) if max_cumulative > 0 else 0
            html += f"""
                            <div class="rank-bar-container">
                                <span class="rank-bar-label" style="min-width: 60px;">{year}</span>
                                <div class="rank-bar-track">
                                    <div class="rank-bar-fill" style="width: {pct}%;"></div>
                                </div>
                                <span class="rank-bar-value">{count:,}</span>
                            </div>
            """
    else:
        html += '<p style="color: #555;">No cumulative citation data available</p>'
    
    html += """
                        </div>
                    </div>
    """
    
    # Heatmap
    html += f"""
                    <div id="heatmap" style="margin-bottom: 20px;">
                        <h4 style="color: {primary}; margin-bottom: 10px;">🔥 {t('heatmap_title')}</h4>
                        <div class="heatmap-container">
                            <table class="heatmap-table">
    """
    
    if not heatmap_data.empty:
        year_cols = [col for col in heatmap_data.columns if col != 'Publication Year']
        max_val = heatmap_data[year_cols].max().max() if year_cols else 1
        
        html += '<thead><tr><th>Publication Year \\ Citation Year</th>'
        for col in year_cols:
            html += f'<th>{col}</th>'
        html += '</tr></thead><tbody>'
        
        for _, row in heatmap_data.iterrows():
            pub_year = row['Publication Year']
            html += f'<tr><td><strong>{pub_year}</strong></td>'
            for col in year_cols:
                value = row.get(col, 0)
                if value > 0:
                    intensity = min(0.9, value / max_val) if max_val > 0 else 0
                    color = f'rgba({primary_rgb[0]}, {primary_rgb[1]}, {primary_rgb[2]}, {0.2 + intensity * 0.7})'
                    html += f'<td style="background: {color}; font-weight: bold;" class="heatmap-tooltip" data-tooltip="{pub_year} → {col}: {value} citations">{value}</td>'
                else:
                    html += '<td style="color: #ccc;">-</td>'
            html += '</tr>'
        
        html += '</tbody>'
    else:
        html += '<tr><td colspan="2" style="text-align: center;">No heatmap data available</td></tr>'
    
    html += """
                            </table>
                        </div>
                    </div>
    """
    
    # Most Cited Publications with progress bars
    # Calculate max citations per year for color scaling
    max_cpy = max([item.get('citations_per_year', 0) for item in most_cited]) if most_cited else 1
    min_cpy = min([item.get('citations_per_year', 0) for item in most_cited]) if most_cited else 0
    cpy_range = max_cpy - min_cpy if max_cpy != min_cpy else 1
    
    html += f"""
                    <div id="most_cited">
                        <h4 style="color: {primary}; margin-bottom: 10px;">🏆 {t('most_cited_publications')}</h4>
                        <div class="table-container" style="max-height: 500px; overflow-y: auto;">
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
    """
    
    max_cited_count = max([item.get('citations', 0) for item in most_cited]) if most_cited else 1
    
    for item in most_cited:
        authors_display = ', '.join(item.get('authors', [])[:3])
        if len(item.get('authors', [])) > 3:
            authors_display += f' +{len(item.get("authors", []))-3} more'
        
        cit_count = item.get('citations', 0)
        pct = (cit_count / max_cited_count * 100) if max_cited_count > 0 else 0
        cpy = item.get('citations_per_year', 0)
        
        # Calculate color for citations per year - green (max) to red (min)
        if cpy_range > 0:
            normalized = (cpy - min_cpy) / cpy_range
            # Green (0,255,0) to Red (255,0,0)
            red = int(255 * (1 - normalized))
            green = int(255 * normalized)
            cpy_color = f'#{red:02x}{green:02x}00'
        else:
            cpy_color = '#28a745'  # Green if all values are equal
        
        html += f"""
                                    <tr>
                                        <td>{item.get('rank', '')}</td>
                                        <td class="word-wrap">{item.get('title', 'No title')[:100]}</td>
                                        <td>{item.get('year', '')}</td>
                                        <td>
                                            {cit_count}
                                            <span class="mini-progress"><span class="fill" style="width: {pct}%;"></span></span>
                                        </td>
                                        <td><span style="display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 11px; font-weight: 600; background: {cpy_color}; color: white;">{cpy:.1f}</span></td>
                                        <td>{authors_display}</td>
                                        <td><a href="https://doi.org/{item.get('doi', '')}" target="_blank" class="doi-link">{item.get('doi', '')[:20]}...</a></td>
                                    </tr>
        """
    
    html += """
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
    """
    
    # ==================== CITING WORKS ====================
    html += f"""
                <div id="citing_works" class="section">
                    <div class="section-title"><span class="icon">📚</span> {t('nav_citing')}</div>
                    
                    <div class="metrics-grid" style="grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));">
                        <div class="metric-card">
                            <div class="metric-value">{metrics.get('total_citing_works', 0)}</div>
                            <div class="metric-label">{t('citing_works')}</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{metrics.get('unique_citing_authors', 0)}</div>
                            <div class="metric-label">{t('unique_citing_authors')}</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{metrics.get('unique_citing_affiliations', 0)}</div>
                            <div class="metric-label">{t('unique_citing_affiliations')}</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{metrics.get('unique_citing_countries', 0)}</div>
                            <div class="metric-label">{t('unique_citing_countries')}</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{metrics.get('unique_citing_journals', 0)}</div>
                            <div class="metric-label">{t('unique_citing_journals')}</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{metrics.get('unique_citing_publishers', 0)}</div>
                            <div class="metric-label">{t('unique_citing_publishers')}</div>
                        </div>
                    </div>
    """
    
    # Top Citing Authors with progress bars
    top_authors = citing_works.get('top_authors', {})
    if top_authors:
        max_author_citing = max(top_authors.values()) if top_authors else 1
        html += f"""
                    <div style="margin: 15px 0;">
                        <h4 style="color: {primary}; margin-bottom: 8px;">👤 {t('top_citing_authors')}</h4>
                        <div style="max-height: 300px; overflow-y: auto;">
        """
        # Find max label length to align progress bars
        max_label_len = max([len(str(author)) for author in top_authors.keys()]) if top_authors else 0
        label_width = min(250, max(120, max_label_len * 7))
        
        for idx, (author, count) in enumerate(list(top_authors.items())[:20], 1):
            pct = (count / max_author_citing * 100) if max_author_citing > 0 else 0
            # Truncate long names
            display_author = author if len(author) <= 40 else author[:37] + '...'
            html += f"""
                            <div class="rank-bar-container">
                                <span class="rank-bar-label" style="min-width: {label_width}px;">{idx}. {display_author}</span>
                                <div class="rank-bar-track">
                                    <div class="rank-bar-fill" style="width: {pct}%;"></div>
                                </div>
                                <span class="rank-bar-value">{count}</span>
                            </div>
            """
        html += """
                        </div>
                    </div>
        """
    
    # Top Citing Affiliations with progress bars
    top_affs_citing = citing_works.get('top_affiliations', {})
    if top_affs_citing:
        max_aff_citing = max(top_affs_citing.values()) if top_affs_citing else 1
        html += f"""
                    <div style="margin: 15px 0;">
                        <h4 style="color: {primary}; margin-bottom: 8px;">🏛️ {t('top_citing_affiliations')}</h4>
                        <div style="max-height: 300px; overflow-y: auto;">
        """
        max_label_len = max([len(str(aff)) for aff in top_affs_citing.keys()]) if top_affs_citing else 0
        label_width = min(250, max(120, max_label_len * 7))
        
        for idx, (aff, count) in enumerate(list(top_affs_citing.items())[:20], 1):
            pct = (count / max_aff_citing * 100) if max_aff_citing > 0 else 0
            display_aff = aff if len(aff) <= 40 else aff[:37] + '...'
            html += f"""
                            <div class="rank-bar-container">
                                <span class="rank-bar-label" style="min-width: {label_width}px;">{idx}. {display_aff}</span>
                                <div class="rank-bar-track">
                                    <div class="rank-bar-fill" style="width: {pct}%;"></div>
                                </div>
                                <span class="rank-bar-value">{count}</span>
                            </div>
            """
        html += """
                        </div>
                    </div>
        """
    
    # Top Citing Countries with progress bars
    top_countries_citing = citing_works.get('top_countries', {})
    if top_countries_citing:
        max_country_citing = max(top_countries_citing.values()) if top_countries_citing else 1
        html += f"""
                    <div style="margin: 15px 0;">
                        <h4 style="color: {primary}; margin-bottom: 8px;">🌍 {t('top_citing_countries')}</h4>
                        <div style="max-height: 300px; overflow-y: auto;">
        """
        max_label_len = max([len(str(country)) for country in top_countries_citing.keys()]) if top_countries_citing else 0
        label_width = min(250, max(120, max_label_len * 7))
        
        for idx, (country, count) in enumerate(list(top_countries_citing.items())[:20], 1):
            pct = (count / max_country_citing * 100) if max_country_citing > 0 else 0
            display_country = country if len(country) <= 40 else country[:37] + '...'
            html += f"""
                            <div class="rank-bar-container">
                                <span class="rank-bar-label" style="min-width: {label_width}px;">{idx}. {display_country}</span>
                                <div class="rank-bar-track">
                                    <div class="rank-bar-fill" style="width: {pct}%;"></div>
                                </div>
                                <span class="rank-bar-value">{count}</span>
                            </div>
            """
        html += """
                        </div>
                    </div>
        """
    
    # Top Citing Journals with progress bars
    top_journals_citing = citing_works.get('top_journals', {})
    if top_journals_citing:
        max_journal_citing = max(top_journals_citing.values()) if top_journals_citing else 1
        html += f"""
                    <div style="margin: 15px 0;">
                        <h4 style="color: {primary}; margin-bottom: 8px;">📖 {t('top_citing_journals')}</h4>
                        <div style="max-height: 300px; overflow-y: auto;">
        """
        max_label_len = max([len(str(journal)) for journal in top_journals_citing.keys()]) if top_journals_citing else 0
        label_width = min(250, max(120, max_label_len * 7))
        
        for idx, (journal, count) in enumerate(list(top_journals_citing.items())[:20], 1):
            pct = (count / max_journal_citing * 100) if max_journal_citing > 0 else 0
            display_journal = journal if len(journal) <= 40 else journal[:37] + '...'
            html += f"""
                            <div class="rank-bar-container">
                                <span class="rank-bar-label" style="min-width: {label_width}px;">{idx}. {display_journal}</span>
                                <div class="rank-bar-track">
                                    <div class="rank-bar-fill" style="width: {pct}%;"></div>
                                </div>
                                <span class="rank-bar-value">{count}</span>
                            </div>
            """
        html += """
                        </div>
                    </div>
        """
    
    # Top Citing Publishers with progress bars
    top_publishers_citing = citing_works.get('top_publishers', {})
    if top_publishers_citing:
        max_publisher_citing = max(top_publishers_citing.values()) if top_publishers_citing else 1
        html += f"""
                    <div style="margin: 15px 0;">
                        <h4 style="color: {primary}; margin-bottom: 8px;">🏢 {t('top_citing_publishers')}</h4>
                        <div style="max-height: 300px; overflow-y: auto;">
        """
        max_label_len = max([len(str(publisher)) for publisher in top_publishers_citing.keys()]) if top_publishers_citing else 0
        label_width = min(250, max(120, max_label_len * 7))
        
        for idx, (publisher, count) in enumerate(list(top_publishers_citing.items())[:20], 1):
            pct = (count / max_publisher_citing * 100) if max_publisher_citing > 0 else 0
            display_publisher = publisher if len(publisher) <= 40 else publisher[:37] + '...'
            html += f"""
                            <div class="rank-bar-container">
                                <span class="rank-bar-label" style="min-width: {label_width}px;">{idx}. {display_publisher}</span>
                                <div class="rank-bar-track">
                                    <div class="rank-bar-fill" style="width: {pct}%;"></div>
                                </div>
                                <span class="rank-bar-value">{count}</span>
                            </div>
            """
        html += """
                        </div>
                    </div>
        """
    
    html += """
                </div>
    """
    
    # ==================== TOPICS ANALYSIS ====================
    html += f"""
                <div id="topics_analysis" class="section">
                    <div class="section-title"><span class="icon">🏷️</span> {t('nav_topics')}</div>
    """
    
    topics_list = topics_data.get('topics', [])
    if topics_list:
        max_total_norm = max([item.get('total_norm', 0) for item in topics_list]) if topics_list else 1
        
        html += f"""
                    <h4 style="color: {primary}; margin-bottom: 10px;">{t('topics_analysis')}</h4>
                    <div class="table-container" style="max-height: 500px; overflow-y: auto;">
                        <table>
                            <thead>
                                <tr>
                                    <th>{t('topic')}</th>
                                    <th>{t('analyzed_count')}</th>
                                    <th>{t('citing_count')}</th>
                                    <th>{t('analyzed_norm')}</th>
                                    <th>{t('citing_norm')}</th>
                                    <th>{t('total_norm')}</th>
                                    <th>{t('first_year')}</th>
                                    <th>{t('peak_year')}</th>
                                </tr>
                            </thead>
                            <tbody>
        """
        
        for item in topics_list[:30]:
            total_norm = item.get('total_norm', 0)
            pct = (total_norm / max_total_norm * 100) if max_total_norm > 0 else 0
            
            html += f"""
                                <tr>
                                    <td>{item.get('topic', '')}</td>
                                    <td>{item.get('analyzed_count', 0)}</td>
                                    <td>{item.get('citing_count', 0)}</td>
                                    <td>{item.get('analyzed_norm', 0):.3f}</td>
                                    <td>{item.get('citing_norm', 0):.3f}</td>
                                    <td>
                                        <strong>{total_norm:.3f}</strong>
                                        <span class="mini-progress"><span class="fill" style="width: {pct}%;"></span></span>
                                    </td>
                                    <td>{item.get('first_year', '')}</td>
                                    <td>{item.get('peak_year', '')}</td>
                                </tr>
            """
        
        html += """
                            </tbody>
                        </table>
                    </div>
        """
    
    # Top Concepts, Subtopics, Fields, Domains with progress bars
    concept_sections = [
        ('top_concepts', 'Concept'),
        ('top_subtopics', 'Subtopic'),
        ('top_fields', 'Field'),
        ('top_domains', 'Domain')
    ]
    
    for section_key, label in concept_sections:
        data = topics_data.get(section_key, {})
        if data:
            max_data = max(data.values()) if data else 1
            html += f"""
                    <div style="margin: 15px 0;">
                        <h4 style="color: {primary}; margin-bottom: 8px;">📊 Top {label}s</h4>
                        <div style="max-height: 300px; overflow-y: auto;">
            """
            max_label_len = max([len(str(name)) for name in data.keys()]) if data else 0
            label_width = min(250, max(120, max_label_len * 7))
            
            for idx, (name, count) in enumerate(list(data.items())[:20], 1):
                pct = (count / max_data * 100) if max_data > 0 else 0
                display_name = name if len(name) <= 40 else name[:37] + '...'
                html += f"""
                            <div class="rank-bar-container">
                                <span class="rank-bar-label" style="min-width: {label_width}px;">{idx}. {display_name}</span>
                                <div class="rank-bar-track">
                                    <div class="rank-bar-fill" style="width: {pct}%;"></div>
                                </div>
                                <span class="rank-bar-value">{count}</span>
                            </div>
                """
            html += """
                        </div>
                    </div>
            """
    
    html += """
                </div>
    """
    
    # ==================== DETAILED CITATIONS ====================
    html += f"""
                <div id="detailed_citations" class="section">
                    <div class="section-title"><span class="icon">📋</span> {t('nav_detailed')}</div>
    """
    
    if detailed_citations:
        html += """
                        <div style="margin: 10px 0;">
            """
        
        sorted_detailed = sorted(
            detailed_citations.items(),
            key=lambda x: x[1].get('total_citations', 0),
            reverse=True
        )
        
        max_cit_detailed = max([d.get('total_citations', 0) for _, d in sorted_detailed]) if sorted_detailed else 1
        
        for doi, data in sorted_detailed:
            pub_id = doi.replace('/', '_').replace('.', '_')
            total_cit = data.get('total_citations', 0)
            
            # Progress bar for citation count relative to max
            pct = (total_cit / max_cit_detailed * 100) if max_cit_detailed > 0 else 0
            
            html += f"""
                        <div class="collapser" onclick="toggleCitations('{pub_id}')">
                            <strong>{html_module.escape(data.get('title', 'No title')[:80])}</strong>
                            <span class="badge badge-info">{data.get('year', '')}</span>
                            <span class="citation-count">{total_cit} citations</span>
                            <span class="mini-progress" style="width: 80px;"><span class="fill" style="width: {pct}%;"></span></span>
                            <span style="font-size: 11px; color: #666; margin-left: 5px;">DOI: {doi[:30]}...</span>
                            <span style="font-size: 11px; color: #666; margin-left: auto;">▼ {t('click_to_toggle')}</span>
                        </div>
                        <div id="citations_{pub_id}" class="collapse-content">
            """
            
            for citing in data.get('citations', []):
                citing_title = html_module.escape((citing.get('citing_title') or 'No title')[:100] if citing.get('citing_title') else 'No title')
                citing_journal = html_module.escape(citing.get('citing_journal', 'Unknown'))
                citing_year = citing.get('citing_year', '')
                citing_date = citing.get('citing_date', '')[:10] if citing.get('citing_date') else ''
                citation_lag = citing.get('citation_lag', 'N/A')
                citing_doi = citing.get('citing_doi', '')
                citing_authors = ', '.join(citing.get('citing_authors', [])[:5])
                if len(citing.get('citing_authors', [])) > 5:
                    citing_authors += ' + more'
                citing_countries = ', '.join(citing.get('citing_countries', [])[:3])
                citing_topics = ', '.join(citing.get('citing_topics', [])[:3])
                
                html += f"""
                            <div class="citation-detail">
                                <div><strong>{citing_title}</strong></div>
                                <div class="cite-meta">
                                    <strong>{t('citing_journal')}:</strong> {citing_journal} | 
                                    <strong>{t('citing_year')}:</strong> {citing_year} | 
                                    <strong>{t('citing_date')}:</strong> {citing_date} |
                                    <strong>{t('citation_lag')}:</strong> {citation_lag} years
                                </div>
                                <div class="cite-meta">
                                    <strong>{t('authors')}:</strong> {citing_authors} |
                                    <strong>{t('countries')}:</strong> {citing_countries} |
                                    <strong>{t('topics')}:</strong> {citing_topics}
                                </div>
                                <div class="cite-meta">
                                    <a href="https://doi.org/{citing_doi}" target="_blank" class="doi-link">DOI: {citing_doi}</a>
                                </div>
                            </div>
                """
            
            html += """
                        </div>
            """
        
        html += """
                    </div>
    """
    else:
        html += '<p style="color: #555;">No detailed citation data available</p>'
    
    html += """
                </div>
    """
    
    # ==================== ALL PUBLICATIONS ====================
    # Calculate max citations per year for color scaling in all publications
    all_cpy_values = [p.get('citations_per_year', 0) for p in all_publications]
    max_all_cpy = max(all_cpy_values) if all_cpy_values else 1
    min_all_cpy = min(all_cpy_values) if all_cpy_values else 0
    all_cpy_range = max_all_cpy - min_all_cpy if max_all_cpy != min_all_cpy else 1
    
    html += f"""
                <div id="all_publications" class="section">
                    <div class="section-title"><span class="icon">📚</span> {t('nav_all_pubs')}</div>
                    
                    <div class="filter-section">
                        <div class="filter-row">
                            <div>
                                <label for="titleFilter">{t('filter_by_title')}</label>
                                <input type="text" id="titleFilter" placeholder="Search title..." onkeyup="filterAllPublications()">
                            </div>
                            <div>
                                <label for="yearFilterAll">{t('filter_by_year')}</label>
                                <select id="yearFilterAll" onchange="filterAllPublications()">
                                    <option value="">{t('all_years')}</option>
    """
    
    years_set = sorted(set(p.get('year') for p in all_publications if p.get('year')), reverse=True)
    for year in years_set:
        html += f'                                    <option value="{year}">{year}</option>\n'
    
    html += """
                                </select>
                            </div>
                            <div>
                                <label for="authorFilterAll">{t('filter_by_author')}</label>
                                <input type="text" id="authorFilterAll" placeholder="Author name..." onkeyup="filterAllPublications()">
                            </div>
                            <div>
                                <label for="affiliationFilterAll">{t('filter_by_affiliations')}</label>
                                <input type="text" id="affiliationFilterAll" placeholder="Affiliation..." onkeyup="filterAllPublications()">
                            </div>
                            <div>
                                <label for="citationFilterAll">{t('filter_by_citations_min')}</label>
                                <input type="number" id="citationFilterAll" placeholder="Min citations..." min="0" onchange="filterAllPublications()">
                            </div>
                            <div>
                                <span class="visible-count" id="visibleCountAll">{t('all_publications')}: {len(all_publications)}</span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="table-container" style="max-height: 600px; overflow-y: auto;">
                        <table id="allPublicationsTable">
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
    """
    
    max_citations_all = max([p.get('citations', 0) for p in all_publications]) if all_publications else 1
    
    for idx, pub in enumerate(all_publications, 1):
        authors_display = ', '.join(pub.get('authors', [])[:3])
        if len(pub.get('authors', [])) > 3:
            authors_display += f' +{len(pub.get("authors", []))-3} more'
        affs_display = ', '.join(pub.get('affiliations', [])[:2])
        if len(pub.get('affiliations', [])) > 2:
            affs_display += f' +{len(pub.get("affiliations", []))-2} more'
        
        doi_value = (pub.get('doi') or '').lower()
        title_value = (pub.get('title') or '').lower()
        year_value = pub.get('year', '')
        authors_value = ', '.join(pub.get('authors', []))
        affiliations_value = ', '.join(pub.get('affiliations', []))
        citations_value = pub.get('citations', 0)
        
        pct = (citations_value / max_citations_all * 100) if max_citations_all > 0 else 0
        cpy = pub.get('citations_per_year', 0)
        
        # Calculate color for citations per year - green (max) to red (min)
        if all_cpy_range > 0:
            normalized = (cpy - min_all_cpy) / all_cpy_range
            red = int(255 * (1 - normalized))
            green = int(255 * normalized)
            cpy_color = f'#{red:02x}{green:02x}00'
        else:
            cpy_color = '#28a745'
        
        html += f"""
                                    <tr data-year="{year_value}" data-authors="{authors_value}" data-affiliations="{affiliations_value}" data-title="{title_value}" data-citations="{citations_value}" data-doi="{doi_value}">
                                        <td>{idx}</td>
                                        <td class="word-wrap">{html_module.escape((pub.get('title') or 'No title')[:120])}</td>
                                        <td>{pub.get('year', '')}</td>
                                        <td>{authors_display}</td>
                                        <td>{affs_display}</td>
                                        <td>
                                            {citations_value}
                                            <span class="mini-progress"><span class="fill" style="width: {pct}%;"></span></span>
                                        </td>
                                        <td><span style="display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 11px; font-weight: 600; background: {cpy_color}; color: white;">{cpy:.1f}</span></td>
                                        <td><a href="https://doi.org/{pub.get('doi', '')}" target="_blank" class="doi-link">{pub.get('doi', '')[:30]}...</a></td>
                                    </tr>
        """
    
    html += """
                            </tbody>
                        </table>
                    </div>
                </div>
    """
    
    # ==================== FOOTER ====================
    html += f"""
                <div class="footer">
                    <p>{t('footer')}</p>
                    <p><a href="{t('journal_url')}" target="_blank">{t('journal_url')}</a> | {t('generated')}: {datetime.now().strftime('%d.%m.%Y')}</p>
                    <p style="font-size: 11px; margin-top: 5px;">{t('data_source')}</p>
                </div>
            </div>
        </div>
        
        <script>
            // Toggle citations
            function toggleCitations(id) {{
                var elem = document.getElementById('citations_' + id);
                if (elem) {{
                    elem.classList.toggle('open');
                }}
            }}
            
            // Filter All Publications
            function filterAllPublications() {{
                var titleFilter = document.getElementById('titleFilter').value.toLowerCase();
                var yearFilter = document.getElementById('yearFilterAll').value;
                var authorFilter = document.getElementById('authorFilterAll').value.toLowerCase();
                var affiliationFilter = document.getElementById('affiliationFilterAll').value.toLowerCase();
                var citationFilter = parseInt(document.getElementById('citationFilterAll').value) || 0;
                
                var rows = document.querySelectorAll('#allPublicationsTable tbody tr');
                var visible = 0;
                
                rows.forEach(function(row) {{
                    var title = row.getAttribute('data-title') || '';
                    var year = row.getAttribute('data-year') || '';
                    var authors = row.getAttribute('data-authors') || '';
                    var affiliations = row.getAttribute('data-affiliations') || '';
                    var citations = parseInt(row.getAttribute('data-citations')) || 0;
                    
                    var match = true;
                    
                    if (titleFilter && !title.includes(titleFilter)) match = false;
                    if (yearFilter && year !== yearFilter) match = false;
                    if (authorFilter && !authors.toLowerCase().includes(authorFilter)) match = false;
                    if (affiliationFilter && !affiliations.toLowerCase().includes(affiliationFilter)) match = false;
                    if (citationFilter > 0 && citations < citationFilter) match = false;
                    
                    if (match) {{
                        row.style.display = '';
                        visible++;
                    }} else {{
                        row.style.display = 'none';
                    }}
                }});
                
                document.getElementById('visibleCountAll').textContent = '{t('all_publications')}: ' + visible;
            }}
            
            // Sort table
            var sortDirection = {{}};
            function sortTable(col) {{
                var table = document.getElementById('allPublicationsTable');
                var rows = Array.from(table.querySelectorAll('tbody tr'));
                var isAsc = sortDirection[col] || false;
                
                rows.sort(function(a, b) {{
                    var aVal = a.cells[col].textContent.trim();
                    var bVal = b.cells[col].textContent.trim();
                    
                    // Try numeric comparison
                    var aNum = parseFloat(aVal);
                    var bNum = parseFloat(bVal);
                    if (!isNaN(aNum) && !isNaN(bNum)) {{
                        return isAsc ? aNum - bNum : bNum - aNum;
                    }}
                    
                    return isAsc ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
                }});
                
                sortDirection[col] = !isAsc;
                
                var tbody = table.querySelector('tbody');
                rows.forEach(function(row) {{
                    tbody.appendChild(row);
                }});
            }}
            
            // Auto-filter on load
            document.addEventListener('DOMContentLoaded', function() {{
                filterAllPublications();
                
                // Animate progress bars on load
                document.querySelectorAll('.progress-bar, .rank-bar-fill, .mini-progress .fill').forEach(function(el) {{
                    var width = el.style.width;
                    el.style.width = '0%';
                    setTimeout(function() {{
                        el.style.width = width;
                    }}, 100);
                }});
            }});
        </script>
    </body>
    </html>
    """
    
    return html

# ============================================
# STREAMLIT APPLICATION
# ============================================

def main():
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
    if 'analysis_result' not in st.session_state:
        st.session_state.analysis_result = None
    if 'language' not in st.session_state:
        st.session_state.language = 'en'
    if 'journal_logo_base64' not in st.session_state:
        st.session_state.journal_logo_base64 = None
    if 'analysis_complete' not in st.session_state:
        st.session_state.analysis_complete = False
    
    # Apply theme
    primary = st.session_state.primary_color
    secondary = st.session_state.secondary_color
    apply_theme_css(primary, secondary)
    
    # Get current language
    current_lang = st.session_state.language
    
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
        
        # Upload logo
        journal_logo_upload = st.file_uploader(
            t('upload_logo'),
            type=['png', 'jpg', 'jpeg', 'svg'],
            help=t('logo_help')
        )
        
        if journal_logo_upload:
            try:
                content = journal_logo_upload.read()
                st.session_state.journal_logo_base64 = base64.b64encode(content).decode()
                st.success("✅ Logo loaded")
            except Exception as e:
                st.error(f"Error loading logo: {e}")
        
        st.markdown("---")
        
        st.markdown(f"""
        <div style="font-size: 11px; color: #666; text-align: center;">
            © Advanced Journal Analysis Tool<br>
            Powered by OpenAlex
        </div>
        """, unsafe_allow_html=True)
    
    # Main content
    # Загружаем логотип приложения из файла
    app_logo_base64 = None
    if os.path.exists(APP_LOGO_PATH):
        try:
            with open(APP_LOGO_PATH, 'rb') as f:
                app_logo_content = f.read()
                app_logo_base64 = base64.b64encode(app_logo_content).decode()
        except Exception as e:
            pass
    
    # Отображаем логотип вместо заголовка
    if app_logo_base64:
        st.markdown(
            f'<div style="text-align: center; margin: 10px 0 20px 0;">'
            f'<img src="data:image/png;base64,{app_logo_base64}" style="max-height: 80px; width: auto;">'
            f'</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(f"## {t('app_title')}")
    
    st.markdown("---")
    
    # Input section
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        issn_input = st.text_input(
            t('issn_input'),
            placeholder=t('issn_placeholder'),
            value=st.session_state.get('last_issn', '')
        )
    
    with col2:
        period_input = st.text_input(
            t('period_input'),
            placeholder=t('period_placeholder'),
            value=st.session_state.get('last_period', '')
        )
    
    with col3:
        workers = st.slider(
            t('workers_label'),
            min_value=4,
            max_value=12,
            value=8,
            step=1
        )
    
    # Analyze button
    if st.button(t('analyze_button'), type="primary", width='stretch'):
        if not issn_input.strip():
            st.error(t('no_issn'))
        elif not period_input.strip():
            st.error(t('no_period'))
        else:
            # Check if we have cached result
            cache_key = f"{issn_input.strip()}_{period_input.strip()}"
            if st.session_state.analysis_result and st.session_state.get('cache_key') == cache_key:
                st.info("📦 Using cached results from previous analysis")
                st.session_state.analysis_complete = True
            else:
                # Run analysis
                status_container = st.status(t('analyzing_articles'), expanded=True)
                progress_bar = st.progress(0)
                
                def progress_callback(current, total, message):
                    progress_bar.progress(current / total)
                    status_container.update(label=message)
                
                with st.spinner("Running analysis..."):
                    result = full_parallel_analysis(
                        issn_input.strip(),
                        period_input.strip(),
                        max_workers=workers,
                        progress_callback=progress_callback
                    )
                
                if result and 'error' not in result:
                    st.session_state.analysis_result = result
                    st.session_state.cache_key = cache_key
                    st.session_state.last_issn = issn_input.strip()
                    st.session_state.last_period = period_input.strip()
                    st.session_state.analysis_complete = True
                    status_container.update(label=t('analysis_complete'), state="complete")
                    progress_bar.empty()
                    st.balloons()
                else:
                    error_msg = result.get('error', 'Unknown error')
                    st.error(f"❌ Analysis failed: {error_msg}")
                    status_container.update(label="❌ Analysis failed", state="error")
                    st.session_state.analysis_complete = False
    
    st.markdown("---")
    
    # Display results
    if st.session_state.analysis_complete and st.session_state.analysis_result:
        result = st.session_state.analysis_result
        
        st.success(f"✅ {t('analysis_complete')} | ISSN: {result.get('issn', '')} | Period: {result.get('period', '')}")
        
        # Show metrics summary
        metrics = result.get('metrics', {})
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric(t('total_publications'), metrics.get('total_publications', 0))
        with col2:
            st.metric(t('total_citations'), f"{metrics.get('total_citations', 0):,}")
        with col3:
            st.metric(t('h_index'), metrics.get('h_index', 0))
        with col4:
            st.metric(t('avg_citations'), f"{metrics.get('avg_citations', 0):.1f}")
        with col5:
            st.metric(t('open_access'), f"{metrics.get('oa_percentage', 0):.1f}%")
        
        # Generate and display HTML report
        with st.spinner(t('generating_report')):
            theme_colors = {
                'primary': st.session_state.primary_color,
                'secondary': st.session_state.secondary_color
            }
            
            # Get journal abbreviation for filename
            journal_info = result.get('journal_info', {})
            journal_abbr = journal_info.get('abbreviation', '')
            if not journal_abbr:
                journal_name = journal_info.get('name', '')
                if journal_name:
                    words = journal_name.split()
                    if len(words) >= 2:
                        journal_abbr = ''.join(word[0].upper() for word in words if word)
                    else:
                        journal_abbr = journal_name[:8].upper().replace(' ', '')
                else:
                    journal_abbr = result.get('issn', '').replace('-', '')
            
            html_report = generate_html_report(
                result,
                logo_base64=st.session_state.journal_logo_base64,
                app_logo_base64=app_logo_base64,
                theme_colors=theme_colors,
                lang=current_lang
            )
            
            # Download button with abbreviated filename
            download_filename = f"journal_analysis_{journal_abbr}_{result.get('period', '')}.html"
            st.download_button(
                label=t('download_report'),
                data=html_report.encode('utf-8'),
                file_name=download_filename,
                mime="text/html",
                width='stretch'
            )
            
            # Preview
            st.markdown("---")
            st.markdown(f"### {t('report_preview')}")
            st.components.v1.html(html_report, height=800, scrolling=True)
    
    else:
        st.info(t('no_data'))

if __name__ == "__main__":
    main()
