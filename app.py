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

# Параметры вывода
SHOW_DEBUG_LOGS = True  # Показывать детальные логи
GENERATE_HTML_REPORT = True  # Генерировать HTML отчет
USE_CACHE = False  # Кэширование результатов
LOGO_PATH = None  # Путь к логотипу журнала (устанавливается через виджет)

# Лимиты для анализа
MAX_PUBLICATIONS_TO_ANALYZE = 1000  # Максимум статей для анализа
MIN_YEAR_FOR_TREND = 5  # Сколько лет для тренда

# Режим анализа источников данных
ANALYSIS_MODE = "orcid_openalex"  # "orcid_only" | "orcid_openalex"
# orcid_only: только публикации из ORCID профиля
# orcid_openalex: ORCID + OpenAlex (максимальная полнота)

# Параметры для обнаружения временных разрывов
MIN_GAP_YEARS_FOR_WARNING = 10  # Минимальный разрыв в годах для предупреждения

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
        'analysis_params': '📊 Analysis Parameters',
        'use_cache': '💾 Use cache',
        'clear_cache': '🗑️ Clear cache',
        'cache_cleared': '✅ Cache cleared!',
        'load_data': '📥 Load Data',
        'journal_analysis': '📄 Journal Analysis',
        'reports': '📄 Reports',
        'issn_input': 'Journal ISSN',
        'issn_placeholder': '0028-0836 or 0028-0836',
        'issn_help': 'Enter the ISSN of the journal to analyze',
        'period_input': 'Analysis Period',
        'period_placeholder': '2020-2023 or 2020,2021,2022',
        'period_help': 'Enter year range (2020-2023) or comma-separated years (2020,2021,2022)',
        'workers_slider': 'Parallel Workers',
        'workers_help': 'Number of parallel threads for data collection (4-12)',
        'upload_logo': 'Upload journal logo (optional)',
        'logo_help': 'Logo will be displayed in reports',
        'analyze_button': '🔍 Analyze Journal',
        'no_issn': '⚠️ Enter ISSN',
        'no_period': '⚠️ Enter analysis period',
        'analysis_complete': '✅ Analysis complete! Found {count} publications in {time:.1f} sec.',
        'analysis_progress': 'Analysis Progress',
        'loading_articles': 'Loading journal articles',
        'loading_citations': 'Loading citing works',
        'processing_data': 'Processing data',
        'generating_report': 'Generating HTML report',
        'no_data': '👈 Load data in "Load Data" tab and click "Analyze Journal"',
        'no_data_reports': '👈 First run analysis in "Load Data" tab',
        'html_report': '📄 HTML Report Generation',
        'download_report': '💾 Download HTML Report',
        'report_preview': '📋 HTML Report Preview',
        'download_hint': 'Click "Download HTML Report" for full report',
        'generating_report_text': 'Generating HTML report...',
        
        # Overview Section
        'overview': '📊 Overview',
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
        'diamond': 'Diamond',
        
        # Analyzed Articles Section
        'analyzed_articles': '📄 Analyzed Articles',
        'author_analysis': 'Author Analysis',
        'rank': 'Rank',
        'authors': 'Authors',
        'orcid': 'ORCID',
        'affiliations': 'Affiliations',
        'countries': 'Countries',
        'publications': 'Publications',
        'citations': 'Citations',
        'top_affiliations': 'Top Affiliations',
        'geographic_analysis': 'Geographic Analysis',
        'unique_countries_per_publication': 'Unique Countries per Publication',
        'authors_per_country': 'Authors per Country',
        'collaboration_patterns': 'Collaboration Patterns',
        'collaboration_couples': 'Collaboration Couples',
        'single_country': 'Single Country',
        'international': 'International',
        'country_pair': 'Country Pair',
        'collaborations': 'Collaborations',
        
        # Citation Analysis Section
        'citation_analysis': '📈 Citation Analysis',
        'citation_dynamics': 'Citation Dynamics by Year',
        'publication_year': 'Publication Year',
        'citation_year': 'Citation Year',
        'citations_count': 'Citations Count',
        'cumulative_citations': 'Cumulative Citations',
        'citation_network_heatmap': 'Citation Network Heatmap',
        'most_cited_publications': 'Most Cited Publications',
        'citations_per_year': 'Citations/Year',
        'title': 'Title',
        'year': 'Year',
        'journal': 'Journal',
        'doi': 'DOI',
        
        # Citing Works Section
        'citing_works': '📚 Citing Works',
        'citing_works_analysis': 'Citing Works Analysis',
        'total_citing_works': 'Total Citing Works',
        'top_citing_authors': 'Top Citing Authors',
        'top_citing_affiliations': 'Top Citing Affiliations',
        'top_citing_countries': 'Top Citing Countries',
        'top_citing_journals': 'Top Citing Journals',
        'top_citing_publishers': 'Top Citing Publishers',
        
        # Topics Analysis Section
        'topics_analysis': '🏷️ Topics Analysis',
        'topics': 'Topics',
        'analyzed_count': 'Analyzed Count',
        'citing_count': 'Citing Count',
        'analyzed_norm_count': 'Analyzed Norm Count',
        'citing_norm_count': 'Citing Norm Count',
        'total_norm_count': 'Total Norm Count',
        'first_year': 'First Year',
        'peak_year': 'Peak Year',
        'top_cited_topics': 'Top Cited Topics',
        'top_cited_subtopics': 'Top Cited Subtopics',
        'top_cited_fields': 'Top Cited Fields',
        'top_cited_domains': 'Top Cited Domains',
        'top_cited_concepts': 'Top Cited Concepts',
        'subtopics': 'Subtopics',
        'fields': 'Fields',
        'domains': 'Domains',
        'concepts': 'Concepts',
        
        # Detailed Citations Section
        'detailed_citations': '📋 Detailed Citations',
        'show_citations': 'Show Citations',
        'citing_journal': 'Citing Journal',
        'citing_year': 'Citing Year',
        'citing_date': 'Citing Date',
        'citation_lag': 'Citation Lag',
        'click_to_toggle': 'Click to toggle citations',
        
        # All Publications Section
        'all_publications': '📚 All Publications',
        'filter_by_year': 'Filter by Year',
        'filter_by_author': 'Filter by Author',
        'filter_by_affiliations': 'Filter by Affiliations',
        'filter_by_citations': 'Filter by Citations (min)',
        'filter_by_title': 'Filter by Title Word(s)',
        'search_publications': 'Search Publications',
        'all_years': 'All Years',
        'visible_count': 'Visible publications',
        
        # Footer
        'footer': '© Advanced Journal Analysis Tool / Created by daM / Chimica Techno Acta',
        'journal_url': 'https://chimicatechnoacta.ru',
        'data_source': 'Data source: OpenAlex',
        'generated': 'Generated',
        
        # Progress
        'starting_analysis': 'Starting analysis...',
        'fetching_articles': 'Fetching articles',
        'fetching_citations': 'Fetching citations',
        'analyzing_data': 'Analyzing data',
        'creating_report': 'Creating report',
        'analysis_complete_text': 'Analysis complete!',
        'error_occurred': 'Error occurred',
        'data_not_found': 'Data not found. Check ISSN correctness.',
        'no_publications_found': 'No publications found for this journal and period.',
        
        # Status messages
        'fetching_journal_articles': '📡 Fetching journal articles...',
        'journal_articles_fetched': '✅ Fetched {count} articles',
        'fetching_citing_works': '📚 Fetching citing works...',
        'citing_works_fetched': '✅ Fetched {count} citing works',
        'processing_publications': '📊 Processing publications...',
        'generating_report_progress': '📄 Generating report...',
        'download_report_button': '📥 Download HTML Report',
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
        'analysis_params': '📊 Параметры анализа',
        'use_cache': '💾 Использовать кэш',
        'clear_cache': '🗑️ Очистить кэш',
        'cache_cleared': '✅ Кэш очищен!',
        'load_data': '📥 Загрузка данных',
        'journal_analysis': '📄 Анализ журнала',
        'reports': '📄 Отчеты',
        'issn_input': 'ISSN журнала',
        'issn_placeholder': '0028-0836 или 0028-0836',
        'issn_help': 'Введите ISSN журнала для анализа',
        'period_input': 'Период анализа',
        'period_placeholder': '2020-2023 или 2020,2021,2022',
        'period_help': 'Введите диапазон лет (2020-2023) или годы через запятую (2020,2021,2022)',
        'workers_slider': 'Параллельных потоков',
        'workers_help': 'Количество параллельных потоков для сбора данных (4-12)',
        'upload_logo': 'Загрузить логотип журнала (опционально)',
        'logo_help': 'Логотип будет отображаться в отчетах',
        'analyze_button': '🔍 Анализировать журнал',
        'no_issn': '⚠️ Введите ISSN',
        'no_period': '⚠️ Введите период анализа',
        'analysis_complete': '✅ Анализ завершен! Найдено {count} публикаций за {time:.1f} сек.',
        'analysis_progress': 'Прогресс анализа',
        'loading_articles': 'Загрузка статей журнала',
        'loading_citations': 'Загрузка цитирующих работ',
        'processing_data': 'Обработка данных',
        'generating_report': 'Генерация HTML отчета',
        'no_data': '👈 Загрузите данные на вкладке "Загрузка данных" и нажмите "Анализировать журнал"',
        'no_data_reports': '👈 Сначала выполните анализ на вкладке "Загрузка данных"',
        'html_report': '📄 Генерация HTML отчета',
        'download_report': '💾 Скачать HTML отчет',
        'report_preview': '📋 Предпросмотр HTML отчета',
        'download_hint': 'Нажмите "Скачать HTML отчет" для полного отчета',
        'generating_report_text': 'Генерация HTML отчета...',
        
        # Overview Section
        'overview': '📊 Обзор',
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
        'international_collaboration_rate': 'Доля международных коллабораций',
        'unique_citing_authors': 'Уникальных цитирующих авторов',
        'unique_citing_affiliations': 'Уникальных цитирующих аффилиаций',
        'unique_citing_countries': 'Уникальных цитирующих стран',
        'unique_citing_journals': 'Уникальных цитирующих журналов',
        'unique_citing_publishers': 'Уникальных цитирующих издательств',
        'open_access_breakdown': 'Распределение открытого доступа',
        'gold': 'Золотой',
        'hybrid': 'Гибридный',
        'green': 'Зеленый',
        'bronze': 'Бронзовый',
        'closed': 'Закрытый',
        'unknown': 'Неизвестный',
        'diamond': 'Алмазный',
        
        # Analyzed Articles Section
        'analyzed_articles': '📄 Анализируемые статьи',
        'author_analysis': 'Анализ авторов',
        'rank': 'Ранг',
        'authors': 'Авторы',
        'orcid': 'ORCID',
        'affiliations': 'Аффилиации',
        'countries': 'Страны',
        'publications': 'Публикаций',
        'citations': 'Цитирований',
        'top_affiliations': 'Топ аффилиаций',
        'geographic_analysis': 'Географический анализ',
        'unique_countries_per_publication': 'Уникальных стран на публикацию',
        'authors_per_country': 'Авторов по странам',
        'collaboration_patterns': 'Модели коллабораций',
        'collaboration_couples': 'Пары коллабораций',
        'single_country': 'Одна страна',
        'international': 'Международные',
        'country_pair': 'Пара стран',
        'collaborations': 'Коллабораций',
        
        # Citation Analysis Section
        'citation_analysis': '📈 Анализ цитирований',
        'citation_dynamics': 'Динамика цитирований по годам',
        'publication_year': 'Год публикации',
        'citation_year': 'Год цитирования',
        'citations_count': 'Количество цитирований',
        'cumulative_citations': 'Накопленные цитирования',
        'citation_network_heatmap': 'Тепловая карта сети цитирований',
        'most_cited_publications': 'Самые цитируемые публикации',
        'citations_per_year': 'Цитирований/год',
        'title': 'Название',
        'year': 'Год',
        'journal': 'Журнал',
        'doi': 'DOI',
        
        # Citing Works Section
        'citing_works': '📚 Цитирующие работы',
        'citing_works_analysis': 'Анализ цитирующих работ',
        'total_citing_works': 'Всего цитирующих работ',
        'top_citing_authors': 'Топ цитирующих авторов',
        'top_citing_affiliations': 'Топ цитирующих аффилиаций',
        'top_citing_countries': 'Топ цитирующих стран',
        'top_citing_journals': 'Топ цитирующих журналов',
        'top_citing_publishers': 'Топ цитирующих издательств',
        
        # Topics Analysis Section
        'topics_analysis': '🏷️ Анализ тем',
        'topics': 'Темы',
        'analyzed_count': 'Анализируемых',
        'citing_count': 'Цитирующих',
        'analyzed_norm_count': 'Норм. анализируемых',
        'citing_norm_count': 'Норм. цитирующих',
        'total_norm_count': 'Всего норм.',
        'first_year': 'Первый год',
        'peak_year': 'Пиковый год',
        'top_cited_topics': 'Топ цитируемых тем',
        'top_cited_subtopics': 'Топ цитируемых подтем',
        'top_cited_fields': 'Топ цитируемых областей',
        'top_cited_domains': 'Топ цитируемых доменов',
        'top_cited_concepts': 'Топ цитируемых концептов',
        'subtopics': 'Подтемы',
        'fields': 'Области',
        'domains': 'Домены',
        'concepts': 'Концепты',
        
        # Detailed Citations Section
        'detailed_citations': '📋 Детальные цитирования',
        'show_citations': 'Показать цитирования',
        'citing_journal': 'Цитирующий журнал',
        'citing_year': 'Год цитирования',
        'citing_date': 'Дата цитирования',
        'citation_lag': 'Задержка цитирования',
        'click_to_toggle': 'Нажмите для показа цитирований',
        
        # All Publications Section
        'all_publications': '📚 Все публикации',
        'filter_by_year': 'Фильтр по году',
        'filter_by_author': 'Фильтр по автору',
        'filter_by_affiliations': 'Фильтр по аффилиации',
        'filter_by_citations': 'Фильтр по цитированиям (мин)',
        'filter_by_title': 'Фильтр по словам в названии',
        'search_publications': 'Поиск публикаций',
        'all_years': 'Все годы',
        'visible_count': 'Видимых публикаций',
        
        # Footer
        'footer': '© Advanced Journal Analysis Tool / Created by daM / Chimica Techno Acta',
        'journal_url': 'https://chimicatechnoacta.ru',
        'data_source': 'Источник данных: OpenAlex',
        'generated': 'Сгенерировано',
        
        # Progress
        'starting_analysis': 'Начинаем анализ...',
        'fetching_articles': 'Получение статей',
        'fetching_citations': 'Получение цитирований',
        'analyzing_data': 'Анализ данных',
        'creating_report': 'Создание отчета',
        'analysis_complete_text': 'Анализ завершен!',
        'error_occurred': 'Произошла ошибка',
        'data_not_found': 'Данные не найдены. Проверьте правильность ISSN.',
        'no_publications_found': 'Публикаций не найдено для этого журнала и периода.',
        
        # Status messages
        'fetching_journal_articles': '📡 Получение статей журнала...',
        'journal_articles_fetched': '✅ Получено {count} статей',
        'fetching_citing_works': '📚 Получение цитирующих работ...',
        'citing_works_fetched': '✅ Получено {count} цитирующих работ',
        'processing_publications': '📊 Обработка публикаций...',
        'generating_report_progress': '📄 Генерация отчета...',
        'download_report_button': '📥 Скачать HTML отчет',
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
        
        .rank-item {{
            border-left: 3px solid var(--primary);
        }}
        
        .rank-number {{
            color: var(--primary);
        }}
        
        .progress-fill {{
            background: linear-gradient(90deg, var(--primary), var(--secondary));
        }}
        
        .custom-tab-button.active {{
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
        }}
        
        .custom-tab-button:hover {{
            background: linear-gradient(135deg, var(--primary-light) 0%, var(--secondary-light) 100%);
        }}
        
        .colored-progress-bar {{
            background: linear-gradient(90deg, 
                var(--primary) 0%, 
                var(--secondary) 50%,
                var(--primary) 100%);
        }}
        
        .section-title {{
            border-bottom: 3px solid var(--primary);
        }}
        
        .concept-card {{
            background: linear-gradient(135deg, var(--hover-light) 0%, var(--secondary-light) 100%);
            border: 1px solid var(--primary-light);
        }}
        
        .concept-name {{
            color: var(--primary);
        }}
        
        .clickable-link {{
            color: var(--primary);
        }}
        
        .clickable-link:hover {{
            color: var(--secondary);
        }}
        
        .badge-success {{
            background: var(--primary-light);
            color: var(--primary-contrast);
        }}
        
        .custom-tab-button .custom-tab-title {{
            color: inherit;
        }}
        
        .metric-card:hover {{
            box-shadow: 0 6px 12px rgba({int(hex_to_rgb(css_vars['--primary-color'])[0])}, {int(hex_to_rgb(css_vars['--primary-color'])[1])}, {int(hex_to_rgb(css_vars['--primary-color'])[2])}, 0.15);
        }}
        
        * {{
            transition: background-color 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease;
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

def update_colored_progress(progress_percent: float, status_text: str = "", color: str = None, badge_text: str = None):
    """Update progress bar with theme colors"""
    if color is None:
        primary_color = st.session_state.get('primary_color', '#667eea')
        secondary_color = st.session_state.get('secondary_color', get_complementary_color(primary_color))
        color = primary_color
    
    if badge_text is None:
        if progress_percent >= 80:
            badge_text = "✅ Отлично"
        elif progress_percent >= 60:
            badge_text = "📊 Хорошо"
        elif progress_percent >= 40:
            badge_text = "⚠️ Средне"
        elif progress_percent >= 20:
            badge_text = "⚠️ Низко"
        else:
            badge_text = "❌ Критично"
    
    progress_html = f"""
    <style>
    @keyframes shimmer{{
        0% {{ background-position: -1000px 0; }}
        100% {{ background-position: 1000px 0; }}
    }}
    
    .colored-progress-container {{
        width: 100%;
        background-color: #f0f0f0;
        border-radius: 20px;
        overflow: hidden;
        box-shadow: inset 0 1px 3px rgba(0,0,0,0.2);
        margin: 10px 0;
    }}
    
    .colored-progress-bar {{
        width: {progress_percent:.1f}%;
        height: 32px;
        background: linear-gradient(90deg, 
            {color} 0%, 
            {color}DD 25%,
            {color} 50%,
            {color}DD 75%,
            {color} 100%);
        background-size: 200% 100%;
        animation: shimmer 2s infinite linear;
        border-radius: 20px;
        transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        font-size: 13px;
        text-shadow: 0 0 2px rgba(0,0,0,0.5);
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }}
    
    .colored-progress-bar::after {{
        content: "{progress_percent:.1f}%";
        position: absolute;
        left: 50%;
        transform: translateX(-50%);
        white-space: nowrap;
    }}
    
    .progress-stats {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 10px;
        margin-top: 8px;
        font-size: 12px;
    }}
    
    .progress-badge {{
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        background: {color}20;
        color: {color};
        border: 1px solid {color}40;
    }}
    
    .progress-status {{
        font-size: 14px;
        font-weight: 500;
        color: #333;
    }}
    </style>
    
    <div class="colored-progress-container">
        <div class="colored-progress-bar"></div>
    </div>
    <div class="progress-stats">
        <span class="progress-status">{status_text}</span>
        <span class="progress-badge">{badge_text}</span>
    </div>
    """
    
    return progress_html

# ============================================
# НАСТРОЙКА НАУЧНОГО СТИЛЯ ДЛЯ ГРАФИКОВ
# ============================================

def apply_scientific_style():
    """Улучшенный научный стиль для matplotlib для материаловедческих публикаций"""
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
# ДОПОЛНИТЕЛЬНЫЕ СЛОВАРИ И УТИЛИТЫ
# ============================================

# Словарь для преобразования кодов стран в полные названия
COUNTRY_CODE_TO_NAME = {
    'GR': 'Greece',
    'CN': 'China',
    'PT': 'Portugal',
    'BY': 'Belarus',
    'PL': 'Poland',
    'SK': 'Slovakia',
    'SA': 'Saudi Arabia',
    'US': 'United States',
    'AU': 'Australia',
    'PK': 'Pakistan',
    'GB': 'United Kingdom',
    'HK': 'Hong Kong',
    'DE': 'Germany',
    'NO': 'Norway',
    'FR': 'France',
    'IN': 'India',
    'KR': 'South Korea',
    'RU': 'Russia',
    'UA': 'Ukraine',
    'IT': 'Italy',
    'ES': 'Spain',
    'NL': 'Netherlands',
    'CH': 'Switzerland',
    'SE': 'Sweden',
    'BE': 'Belgium',
    'AT': 'Austria',
    'DK': 'Denmark',
    'FI': 'Finland',
    'IE': 'Ireland',
    'NZ': 'New Zealand',
    'ZA': 'South Africa',
    'AR': 'Argentina',
    'MX': 'Mexico',
    'CL': 'Chile',
    'CO': 'Colombia',
    'BR': 'Brazil',
    'JP': 'Japan',
    'SG': 'Singapore',
    'TW': 'Taiwan',
    'IL': 'Israel',
    'TR': 'Turkey',
    'EG': 'Egypt',
    'NG': 'Nigeria',
    'KE': 'Kenya',
}

def get_full_country_name(country_code: str) -> str:
    """Преобразует код страны в полное название"""
    if not country_code:
        return 'Unknown'
    
    if len(country_code) > 3:
        return country_code
    
    return COUNTRY_CODE_TO_NAME.get(country_code.upper(), country_code)

def normalize_issn(issn_str: str) -> str:
    """Normalize ISSN string to standard format"""
    cleaned = re.sub(r'[^0-9Xx]', '', str(issn_str).strip())
    if len(cleaned) == 8:
        return f"{cleaned[:4]}-{cleaned[4:]}".upper()
    return cleaned.upper()


def smart_get(url: str, params: Dict = None, retries: int = 4, base_delay: float = 0.35) -> Optional[Dict]:
    """Smart GET request with retry logic and rate limiting protection"""
    lock = Lock()
    
    for attempt in range(retries):
        try:
            with lock:
                time.sleep(random.uniform(0.1, base_delay))
            
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

def get_cache_path(issn: str) -> str:
    """Возвращает путь к файлу кэша для ISSN"""
    issn_clean = normalize_issn(issn)
    if not os.path.exists('cache'):
        os.makedirs('cache')
    return f"cache/journal_{issn_clean}.json"

def load_from_cache(issn: str) -> Optional[Dict]:
    """Загружает данные из кэша"""
    if not USE_CACHE:
        return None
    
    cache_path = get_cache_path(issn)
    if os.path.exists(cache_path):
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if SHOW_DEBUG_LOGS:
                print(f"✅ Загружено из кэша: {cache_path}")
            return data
        except Exception as e:
            if SHOW_DEBUG_LOGS:
                print(f"⚠️ Ошибка загрузки кэша: {e}")
            return None
    return None

def save_to_cache(issn: str, data: Dict):
    """Сохраняет данные в кэш"""
    if not USE_CACHE:
        return
    
    cache_path = get_cache_path(issn)
    try:
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        if SHOW_DEBUG_LOGS:
            print(f"✅ Данные сохранены в кэш: {cache_path}")
    except Exception as e:
        if SHOW_DEBUG_LOGS:
            print(f"⚠️ Ошибка сохранения кэша: {e}")

# ============================================
# КЛАССЫ ДЛЯ ДАННЫХ
# ============================================

class Author:
    def __init__(self, display_name: str = '', orcid: str = '', affiliations: List[str] = None, countries: List[str] = None):
        self.display_name = display_name
        self.orcid = orcid
        self.affiliations = affiliations or []
        self.countries = countries or []
        self.publications_count = 0
        self.total_citations = 0

class Publication:
    def __init__(self, data: Dict):
        self.id = data.get('id', '')
        self.doi = data.get('doi', '').replace('https://doi.org/', '')
        self.title = data.get('title', 'No title')
        self.publication_year = data.get('publication_year')
        self.cited_by_count = data.get('cited_by_count', 0)
        self.open_access = data.get('open_access', {})
        self.authors = []
        self.affiliations = []
        self.countries = []
        self.institutions = []
        self.journal_name = 'Unknown'
        self.publisher = 'Unknown'
        self.topics = []
        self.concepts = []
        self.citations = []
        self.citations_per_year = 0
        
        # Parse authorships
        for auth in data.get('authorships', []):
            if auth.get('author'):
                author_name = auth['author'].get('display_name', '')
                author_orcid = auth['author'].get('orcid', '').replace('https://orcid.org/', '')
                if author_name:
                    author = Author(
                        display_name=author_name,
                        orcid=author_orcid
                    )
                    
                    # Parse affiliations for this author
                    affils = []
                    countries_list = []
                    for inst in auth.get('institutions', []):
                        affil_name = inst.get('display_name', '')
                        if affil_name:
                            affils.append(affil_name)
                            country = inst.get('country_code', '')
                            if country:
                                countries_list.append(country)
                    
                    author.affiliations = affils
                    author.countries = countries_list
                    self.authors.append(author)
                    
                    # Collect all affiliations and countries
                    self.affiliations.extend(affils)
                    self.countries.extend(countries_list)
                    
                    # Collect institutions
                    for inst in auth.get('institutions', []):
                        self.institutions.append({
                            'id': inst.get('id', ''),
                            'display_name': inst.get('display_name', ''),
                            'country_code': inst.get('country_code', ''),
                            'ror': inst.get('ror', '')
                        })
        
        # Parse primary location
        if data.get('primary_location'):
            source = data['primary_location'].get('source', {})
            self.journal_name = source.get('display_name', 'Unknown')
            self.publisher = source.get('host_organization_name') or source.get('publisher', 'Unknown')
        
        # Parse topics
        for topic in data.get('topics', []):
            self.topics.append({
                'display_name': topic.get('display_name', ''),
                'subfield': topic.get('subfield', {}).get('display_name', ''),
                'field': topic.get('field', {}).get('display_name', ''),
                'domain': topic.get('domain', {}).get('display_name', ''),
                'score': topic.get('score', 0)
            })
        
        # Parse concepts
        for concept in data.get('concepts', []):
            self.concepts.append({
                'display_name': concept.get('display_name', ''),
                'level': concept.get('level', 0),
                'score': concept.get('score', 0)
            })
        
        # Calculate citations per year
        if self.publication_year:
            current_year = datetime.now().year
            years_since = current_year - self.publication_year + 1
            self.citations_per_year = self.cited_by_count / max(years_since, 1)

class CitingWork:
    def __init__(self, data: Dict):
        self.id = data.get('id', '')
        self.doi = data.get('doi', '').replace('https://doi.org/', '')
        self.title = data.get('title', 'No title')
        self.publication_year = data.get('publication_year')
        self.cited_by_count = data.get('cited_by_count', 0)
        self.open_access = data.get('open_access', {})
        self.authors = []
        self.affiliations = []
        self.countries = []
        self.journal_name = 'Unknown'
        self.publisher = 'Unknown'
        self.topics = []
        self.concepts = []
        self.citation_lag = 0
        self.citing_date = None
        
        # Parse authorships
        for auth in data.get('authorships', []):
            if auth.get('author'):
                author_name = auth['author'].get('display_name', '')
                if author_name:
                    self.authors.append(author_name)
                    
                    # Parse affiliations
                    for inst in auth.get('institutions', []):
                        affil_name = inst.get('display_name', '')
                        if affil_name:
                            self.affiliations.append(affil_name)
                        country = inst.get('country_code', '')
                        if country:
                            self.countries.append(country)
        
        # Parse primary location
        if data.get('primary_location'):
            source = data['primary_location'].get('source', {})
            self.journal_name = source.get('display_name', 'Unknown')
            self.publisher = source.get('host_organization_name') or source.get('publisher', 'Unknown')
        
        # Parse topics
        for topic in data.get('topics', []):
            self.topics.append({
                'display_name': topic.get('display_name', ''),
                'subfield': topic.get('subfield', {}).get('display_name', ''),
                'field': topic.get('field', {}).get('display_name', ''),
                'domain': topic.get('domain', {}).get('display_name', ''),
                'score': topic.get('score', 0)
            })
        
        # Parse concepts
        for concept in data.get('concepts', []):
            self.concepts.append({
                'display_name': concept.get('display_name', ''),
                'level': concept.get('level', 0),
                'score': concept.get('score', 0)
            })

# ============================================
# ОСНОВНОЙ КЛАСС АНАЛИЗА ЖУРНАЛА
# ============================================

class JournalAnalyzer:
    def __init__(self, issn: str, years: Any, max_workers: int = 8):
        self.issn = normalize_issn(issn)
        self.years = years
        self.max_workers = max_workers
        self.publications = []
        self.citations_map = {}
        self.citing_works = []
        self.analysis_results = {}
        self.journal_name = ''
        self.publisher = ''
        self.progress_callback = None
        
    def set_progress_callback(self, callback):
        """Set callback for progress updates"""
        self.progress_callback = callback
    
    def _update_progress(self, percent: float, message: str = ""):
        """Update progress if callback is set"""
        if self.progress_callback:
            self.progress_callback(percent, message)
    
    def _get_citing_dois(self, oa_id: str, max_citing: int = 300) -> List[str]:
        """Get citing DOIs for a single work"""
        citing = []
        cursor = "*"
        base_url = "https://api.openalex.org/works"
        
        for _ in range(8):  # pagination limit
            data = smart_get(base_url, {
                "filter": f"cites:{oa_id}",
                "per_page": 200,
                "select": "doi",
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
        
        return citing[:max_citing]
    
    def _fetch_journal_articles(self) -> List[Dict]:
        """
        Fetch all articles from the journal for the specified period.
        Использует логику из вспомогательного мини-кода для корректной работы.
        """
        base_url = "https://api.openalex.org/works"
        
        # Формируем фильтр по годам как во вспомогательном коде
        if isinstance(self.years, list):
            year_filter = "|".join(f"publication_year:{y}" for y in self.years)
        elif isinstance(self.years, tuple):
            year_filter = f"publication_year:{self.years[0]}-{self.years[1]}"
        else:
            year_filter = f"publication_year:{self.years}"
        
        articles = []
        cursor = "*"
        
        self._update_progress(5, translate('fetching_articles', st.session_state.get('language', 'en')))
        
        # Используем tqdm для прогресса как во вспомогательном коде
        with tqdm(desc=translate('loading_articles', st.session_state.get('language', 'en')), unit="стр") as pbar:
            while True:
                # Формируем параметры запроса как во вспомогательном коде
                params = {
                    "filter": f"primary_location.source.issn:{self.issn},{year_filter}",
                    "per_page": 200,
                    "select": "id,doi,title,publication_year,cited_by_count,open_access,authorships,primary_location,topics,concepts",
                    "cursor": cursor
                }
                
                data = smart_get(base_url, params)
                
                if not data or not data.get("results"):
                    break
                
                for w in data["results"]:
                    # Extract journal name and publisher from first result
                    if not self.journal_name and w.get('primary_location'):
                        source = w['primary_location'].get('source', {})
                        self.journal_name = source.get('display_name', '')
                        self.publisher = source.get('host_organization_name') or source.get('publisher', '')
                    
                    articles.append(w)
                
                pbar.update(len(data["results"]))
                cursor = data.get("meta", {}).get("next_cursor")
                if not cursor:
                    break
        
        self._update_progress(20, translate('journal_articles_fetched', st.session_state.get('language', 'en'), count=len(articles)))
        return articles
    
    def _fetch_citing_works_parallel(self, publications: List[Dict]) -> Dict[str, List[str]]:
        """
        Fetch citing DOIs in parallel using ThreadPoolExecutor.
        Использует логику из вспомогательного мини-кода.
        """
        citing_map = {}
        futures = {}
        
        self._update_progress(25, translate('fetching_citations', st.session_state.get('language', 'en')))
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            for pub in publications:
                pub_id = pub.get('id', '').replace('https://openalex.org/', '')
                cited_by_count = pub.get('cited_by_count', 0)
                if cited_by_count > 0 and pub_id:
                    future = executor.submit(self._get_citing_dois, pub_id)
                    futures[future] = pub.get('doi', '').replace('https://doi.org/', '')
            
            # Используем tqdm для прогресса как во вспомогательном коде
            with tqdm(desc=translate('loading_citations', st.session_state.get('language', 'en')), total=len(futures)) as pbar:
                for future in as_completed(futures):
                    doi = futures[future]
                    try:
                        citing_map[doi] = future.result()
                    except:
                        citing_map[doi] = []
                    pbar.update(1)
                    
                    # Update progress
                    progress = 25 + (pbar.n / len(futures)) * 35
                    self._update_progress(progress, 
                        translate('fetching_citations', st.session_state.get('language', 'en')) + 
                        f" ({pbar.n}/{len(futures)})")
        
        self._update_progress(60, translate('citing_works_fetched', st.session_state.get('language', 'en'), count=sum(len(v) for v in citing_map.values())))
        return citing_map
    
    def _fetch_citing_metadata(self, citing_dois: List[str]) -> List[Dict]:
        """Fetch full metadata for citing works"""
        if not citing_dois:
            return []
        
        metadata = []
        
        # Batch DOIs for efficient fetching
        for batch in chunks(citing_dois, 50):
            doi_query = '|'.join(batch)
            base_url = "https://api.openalex.org/works"
            data = smart_get(base_url, {
                "filter": f"doi:{doi_query}",
                "per_page": len(batch),
                "select": "id,doi,title,publication_year,cited_by_count,open_access,authorships,primary_location,topics,concepts"
            })
            
            if data and data.get('results'):
                metadata.extend(data['results'])
            
            # Small delay between batches
            time.sleep(0.1)
        
        return metadata
    
    def analyze(self) -> Dict:
        """Perform complete journal analysis"""
        # Step 1: Fetch journal articles
        articles_data = self._fetch_journal_articles()
        
        if not articles_data:
            self._update_progress(100, translate('no_publications_found', st.session_state.get('language', 'en')))
            return {'error': 'no_publications'}
        
        # Step 2: Parse publications
        self.publications = []
        for data in articles_data:
            pub = Publication(data)
            self.publications.append(pub)
        
        self._update_progress(30, translate('processing_data', st.session_state.get('language', 'en')))
        
        # Step 3: Fetch citing DOIs in parallel
        citing_dois_map = self._fetch_citing_works_parallel(articles_data)
        self.citations_map = citing_dois_map
        
        # Step 4: Collect all citing DOIs
        all_citing_dois = []
        for doi_list in citing_dois_map.values():
            all_citing_dois.extend(doi_list)
        
        # Step 5: Fetch citing metadata
        self._update_progress(65, translate('processing_data', st.session_state.get('language', 'en')))
        citing_metadata = self._fetch_citing_metadata(all_citing_dois)
        
        # Step 6: Parse citing works
        self.citing_works = []
        for data in citing_metadata:
            citing_work = CitingWork(data)
            self.citing_works.append(citing_work)
        
        # Step 7: Link citations to publications
        for pub in self.publications:
            if pub.doi in citing_dois_map:
                pub.citations = citing_dois_map[pub.doi]
        
        self._update_progress(80, translate('processing_data', st.session_state.get('language', 'en')))
        
        # Step 8: Calculate all metrics
        self._calculate_metrics()
        
        self._update_progress(95, translate('processing_data', st.session_state.get('language', 'en')))
        
        return self.analysis_results
    
    def _calculate_metrics(self):
        """Calculate all analysis metrics"""
        results = {
            'journal_name': self.journal_name,
            'publisher': self.publisher,
            'issn': self.issn,
            'publications': self.publications,
            'citing_works': self.citing_works,
            'citations_map': self.citations_map
        }
        
        # Basic metrics
        total_pubs = len(self.publications)
        total_citations = sum(p.cited_by_count for p in self.publications)
        
        # Calculate h-index, g-index, i10-index, i100-index
        citations_list = sorted([p.cited_by_count for p in self.publications], reverse=True)
        
        h_index = 0
        for i, c in enumerate(citations_list, 1):
            if c >= i:
                h_index = i
            else:
                break
        
        g_index = 0
        total_citations_sorted = 0
        for i, c in enumerate(citations_list, 1):
            total_citations_sorted += c
            if total_citations_sorted >= i**2:
                g_index = i
        
        i10_index = sum(1 for c in citations_list if c >= 10)
        i100_index = sum(1 for c in citations_list if c >= 100)
        
        avg_citations = total_citations / total_pubs if total_pubs > 0 else 0
        
        # Open access breakdown
        oa_breakdown = {
            'gold': 0, 'hybrid': 0, 'green': 0, 'bronze': 0, 'closed': 0, 'unknown': 0, 'diamond': 0
        }
        for pub in self.publications:
            status = pub.open_access.get('oa_status', 'unknown')
            if status in oa_breakdown:
                oa_breakdown[status] += 1
            else:
                oa_breakdown['unknown'] += 1
        
        # Unique authors, affiliations, countries
        unique_authors = set()
        unique_affiliations = set()
        unique_countries = set()
        author_publications = defaultdict(int)
        author_citations = defaultdict(int)
        author_affiliations = defaultdict(set)
        author_countries = defaultdict(set)
        
        for pub in self.publications:
            for author in pub.authors:
                unique_authors.add(author.display_name)
                author_publications[author.display_name] += 1
                author_citations[author.display_name] += pub.cited_by_count
                for affil in author.affiliations:
                    author_affiliations[author.display_name].add(affil)
                    unique_affiliations.add(affil)
                for country in author.countries:
                    author_countries[author.display_name].add(country)
                    unique_countries.add(country)
        
        # Average authors, affiliations, countries per paper
        total_authors = sum(len(p.authors) for p in self.publications)
        total_affiliations = sum(len(p.affiliations) for p in self.publications)
        total_countries = sum(len(set(p.countries)) for p in self.publications)
        
        avg_authors_per_paper = total_authors / total_pubs if total_pubs > 0 else 0
        avg_affiliations_per_paper = total_affiliations / total_pubs if total_pubs > 0 else 0
        avg_countries_per_paper = total_countries / total_pubs if total_pubs > 0 else 0
        
        # International collaboration rate
        single_country = 0
        international = 0
        for pub in self.publications:
            unique_countries_pub = set(pub.countries)
            if len(unique_countries_pub) <= 1:
                single_country += 1
            else:
                international += 1
        
        international_collab_rate = international / total_pubs if total_pubs > 0 else 0
        
        # Active years
        years = set()
        for pub in self.publications:
            if pub.publication_year:
                years.add(pub.publication_year)
        active_years = len(years)
        
        # Unique citing metrics
        unique_citing_authors = set()
        unique_citing_affiliations = set()
        unique_citing_countries = set()
        unique_citing_journals = set()
        unique_citing_publishers = set()
        
        for work in self.citing_works:
            unique_citing_authors.update(work.authors)
            unique_citing_affiliations.update(work.affiliations)
            unique_citing_countries.update(work.countries)
            if work.journal_name and work.journal_name != 'Unknown':
                unique_citing_journals.add(work.journal_name)
            if work.publisher and work.publisher != 'Unknown':
                unique_citing_publishers.add(work.publisher)
        
        # Top citing authors
        citing_author_counts = defaultdict(int)
        for work in self.citing_works:
            for author in work.authors:
                citing_author_counts[author] += 1
        
        top_citing_authors = dict(sorted(citing_author_counts.items(), key=lambda x: x[1], reverse=True)[:20])
        
        # Top citing affiliations
        citing_affiliation_counts = defaultdict(int)
        for work in self.citing_works:
            for affil in work.affiliations:
                citing_affiliation_counts[affil] += 1
        
        top_citing_affiliations = dict(sorted(citing_affiliation_counts.items(), key=lambda x: x[1], reverse=True)[:20])
        
        # Top citing countries
        citing_country_counts = defaultdict(int)
        for work in self.citing_works:
            for country in work.countries:
                citing_country_counts[get_full_country_name(country)] += 1
        
        top_citing_countries = dict(sorted(citing_country_counts.items(), key=lambda x: x[1], reverse=True)[:20])
        
        # Top citing journals
        citing_journal_counts = defaultdict(int)
        for work in self.citing_works:
            if work.journal_name and work.journal_name != 'Unknown':
                citing_journal_counts[work.journal_name] += 1
        
        top_citing_journals = dict(sorted(citing_journal_counts.items(), key=lambda x: x[1], reverse=True)[:20])
        
        # Top citing publishers
        citing_publisher_counts = defaultdict(int)
        for work in self.citing_works:
            if work.publisher and work.publisher != 'Unknown':
                citing_publisher_counts[work.publisher] += 1
        
        top_citing_publishers = dict(sorted(citing_publisher_counts.items(), key=lambda x: x[1], reverse=True)[:20])
        
        # Top affiliations
        affiliation_counts = defaultdict(int)
        for pub in self.publications:
            for affil in pub.affiliations:
                affiliation_counts[affil] += 1
        
        top_affiliations = dict(sorted(affiliation_counts.items(), key=lambda x: x[1], reverse=True)[:20])
        
        # Author analysis
        author_stats = []
        for author in unique_authors:
            author_stats.append({
                'name': author,
                'publications': author_publications[author],
                'citations': author_citations[author],
                'affiliations': list(author_affiliations[author]),
                'countries': list(author_countries[author])
            })
        author_stats.sort(key=lambda x: x['citations'], reverse=True)
        
        # Citation dynamics by year
        citation_dynamics = defaultdict(lambda: defaultdict(int))
        for pub in self.publications:
            if pub.doi in self.citations_map:
                for citing_doi in self.citations_map[pub.doi]:
                    # Find citing work year
                    for work in self.citing_works:
                        if work.doi == citing_doi and work.publication_year:
                            citation_dynamics[pub.publication_year][work.publication_year] += 1
                            break
        
        # Cumulative citations
        cumulative_citations = defaultdict(int)
        all_years = sorted(citation_dynamics.keys())
        for pub_year in all_years:
            total = 0
            for cite_year, count in citation_dynamics[pub_year].items():
                total += count
            cumulative_citations[pub_year] = cumulative_citations.get(pub_year, 0) + total
        
        # Citation network heatmap
        citation_heatmap = defaultdict(lambda: defaultdict(int))
        for pub_year, citing_years in citation_dynamics.items():
            for cite_year, count in citing_years.items():
                citation_heatmap[pub_year][cite_year] = count
        
        # Most cited publications
        most_cited = sorted(self.publications, key=lambda x: x.cited_by_count, reverse=True)[:20]
        most_cited_data = []
        for pub in most_cited:
            authors_list = [a.display_name for a in pub.authors]
            authors_str = ', '.join(authors_list[:3])
            if len(authors_list) > 3:
                authors_str += f' +{len(authors_list) - 3} more'
            most_cited_data.append({
                'title': pub.title,
                'year': pub.publication_year,
                'citations': pub.cited_by_count,
                'citations_per_year': pub.citations_per_year,
                'authors': authors_str,
                'doi': pub.doi
            })
        
        # Geographic analysis
        # Unique countries per publication
        unique_countries_per_pub = []
        for pub in self.publications:
            unique_countries_pub = set()
            for country in pub.countries:
                if country:
                    unique_countries_pub.add(get_full_country_name(country))
            unique_countries_per_pub.append({
                'publication': pub.title[:50] + '...' if len(pub.title) > 50 else pub.title,
                'year': pub.publication_year,
                'countries': ', '.join(sorted(unique_countries_pub)) if unique_countries_pub else 'Unknown'
            })
        
        # Authors per country
        authors_per_country = defaultdict(int)
        for pub in self.publications:
            for author in pub.authors:
                for country in author.countries:
                    if country:
                        authors_per_country[get_full_country_name(country)] += 1
        
        # Collaboration patterns
        collaboration_patterns = {
            'single_country': single_country,
            'international': international,
            'total': total_pubs
        }
        
        # Collaboration couples
        country_pairs = defaultdict(int)
        for pub in self.publications:
            countries_pub = set()
            for country in pub.countries:
                if country:
                    countries_pub.add(get_full_country_name(country))
            
            countries_list = list(countries_pub)
            if len(countries_list) >= 2:
                for i in range(len(countries_list)):
                    for j in range(i+1, len(countries_list)):
                        pair = tuple(sorted([countries_list[i], countries_list[j]]))
                        country_pairs[pair] += 1
        
        collaboration_couples = dict(sorted(country_pairs.items(), key=lambda x: x[1], reverse=True)[:20])
        
        # Topics analysis
        topics_data = defaultdict(lambda: {
            'analyzed_count': 0,
            'citing_count': 0,
            'first_year': None,
            'peak_year': None,
            'years': []
        })
        
        for pub in self.publications:
            for topic in pub.topics:
                topic_name = topic.get('display_name', '')
                if topic_name:
                    topics_data[topic_name]['analyzed_count'] += 1
                    if topics_data[topic_name]['first_year'] is None or pub.publication_year < topics_data[topic_name]['first_year']:
                        topics_data[topic_name]['first_year'] = pub.publication_year
                    topics_data[topic_name]['years'].append(pub.publication_year)
        
        for work in self.citing_works:
            for topic in work.topics:
                topic_name = topic.get('display_name', '')
                if topic_name:
                    topics_data[topic_name]['citing_count'] += 1
        
        # Calculate peak year and norm counts
        for topic_name, data in topics_data.items():
            if data['years']:
                year_counts = Counter(data['years'])
                data['peak_year'] = max(year_counts.items(), key=lambda x: x[1])[0]
            
            total_count = data['analyzed_count'] + data['citing_count']
            data['analyzed_norm_count'] = data['analyzed_count'] / total_pubs if total_pubs > 0 else 0
            data['citing_norm_count'] = data['citing_count'] / len(self.citing_works) if self.citing_works else 0
            data['total_norm_count'] = data['analyzed_norm_count'] + data['citing_norm_count']
        
        top_topics = dict(sorted(topics_data.items(), key=lambda x: x[1]['total_norm_count'], reverse=True)[:20])
        
        # Top cited topics, subtopics, fields, domains, concepts
        def get_top_cited(category, key):
            counts = defaultdict(int)
            for pub in self.publications:
                for item in getattr(pub, category, []):
                    if isinstance(item, dict):
                        name = item.get(key, '')
                    else:
                        name = item
                    if name:
                        counts[name] += pub.cited_by_count
            return dict(sorted(counts.items(), key=lambda x: x[1], reverse=True)[:10])
        
        top_cited_topics = get_top_cited('topics', 'display_name')
        
        # For subtopics, fields, domains from topics
        subtopic_counts = defaultdict(int)
        field_counts = defaultdict(int)
        domain_counts = defaultdict(int)
        
        for pub in self.publications:
            for topic in pub.topics:
                if topic.get('subfield'):
                    subtopic_counts[topic['subfield']] += pub.cited_by_count
                if topic.get('field'):
                    field_counts[topic['field']] += pub.cited_by_count
                if topic.get('domain'):
                    domain_counts[topic['domain']] += pub.cited_by_count
        
        top_cited_subtopics = dict(sorted(subtopic_counts.items(), key=lambda x: x[1], reverse=True)[:10])
        top_cited_fields = dict(sorted(field_counts.items(), key=lambda x: x[1], reverse=True)[:10])
        top_cited_domains = dict(sorted(domain_counts.items(), key=lambda x: x[1], reverse=True)[:10])
        
        # Top cited concepts
        concept_counts = defaultdict(int)
        for pub in self.publications:
            for concept in pub.concepts:
                if concept.get('display_name'):
                    concept_counts[concept['display_name']] += pub.cited_by_count
        
        top_cited_concepts = dict(sorted(concept_counts.items(), key=lambda x: x[1], reverse=True)[:10])
        
        # Detailed citations for each publication
        detailed_citations = {}
        for pub in self.publications:
            if pub.doi in self.citations_map and self.citations_map[pub.doi]:
                citations_list = []
                for citing_doi in self.citations_map[pub.doi]:
                    citing_work = None
                    for work in self.citing_works:
                        if work.doi == citing_doi:
                            citing_work = work
                            break
                    
                    if citing_work:
                        # Calculate citation lag
                        lag = None
                        if pub.publication_year and citing_work.publication_year:
                            lag = citing_work.publication_year - pub.publication_year
                        
                        citations_list.append({
                            'citing_title': citing_work.title,
                            'citing_year': citing_work.publication_year,
                            'citing_date': citing_work.publication_year,
                            'citing_journal': citing_work.journal_name,
                            'citing_publisher': citing_work.publisher,
                            'citing_doi': citing_work.doi,
                            'citation_lag': lag,
                            'citing_authors': citing_work.authors,
                            'citing_countries': citing_work.countries,
                            'citing_topics': [t.get('display_name', '') for t in citing_work.topics[:5]]
                        })
                
                detailed_citations[pub.id] = {
                    'title': pub.title,
                    'year': pub.publication_year,
                    'doi': pub.doi,
                    'total_citations': len(citations_list),
                    'citations': citations_list
                }
        
        # All publications for filtering
        all_publications_data = []
        for i, pub in enumerate(self.publications, 1):
            all_publications_data.append({
                'index': i,
                'title': pub.title,
                'year': pub.publication_year,
                'authors': ', '.join([a.display_name for a in pub.authors]),
                'affiliations': ', '.join(set(pub.affiliations[:3])),
                'citations': pub.cited_by_count,
                'citations_per_year': pub.citations_per_year,
                'doi': pub.doi,
                'journal': pub.journal_name,
                'id': pub.id
            })
        
        # Compile all results
        self.analysis_results = {
            'journal_name': self.journal_name,
            'publisher': self.publisher,
            'issn': self.issn,
            'total_publications': total_pubs,
            'total_citations': total_citations,
            'h_index': h_index,
            'g_index': g_index,
            'i10_index': i10_index,
            'i100_index': i100_index,
            'avg_citations': avg_citations,
            'active_years': active_years,
            'unique_authors': len(unique_authors),
            'unique_affiliations': len(unique_affiliations),
            'unique_countries': len(unique_countries),
            'avg_authors_per_paper': avg_authors_per_paper,
            'avg_affiliations_per_paper': avg_affiliations_per_paper,
            'avg_countries_per_paper': avg_countries_per_paper,
            'international_collaboration_rate': international_collab_rate,
            'unique_citing_authors': len(unique_citing_authors),
            'unique_citing_affiliations': len(unique_citing_affiliations),
            'unique_citing_countries': len(unique_citing_countries),
            'unique_citing_journals': len(unique_citing_journals),
            'unique_citing_publishers': len(unique_citing_publishers),
            'open_access_breakdown': oa_breakdown,
            'top_affiliations': top_affiliations,
            'author_stats': author_stats,
            'citation_dynamics': dict(citation_dynamics),
            'cumulative_citations': dict(cumulative_citations),
            'citation_heatmap': dict(citation_heatmap),
            'most_cited': most_cited_data,
            'top_citing_authors': top_citing_authors,
            'top_citing_affiliations': top_citing_affiliations,
            'top_citing_countries': top_citing_countries,
            'top_citing_journals': top_citing_journals,
            'top_citing_publishers': top_citing_publishers,
            'top_topics': top_topics,
            'top_cited_topics': top_cited_topics,
            'top_cited_subtopics': top_cited_subtopics,
            'top_cited_fields': top_cited_fields,
            'top_cited_domains': top_cited_domains,
            'top_cited_concepts': top_cited_concepts,
            'unique_countries_per_pub': unique_countries_per_pub,
            'authors_per_country': dict(authors_per_country),
            'collaboration_patterns': collaboration_patterns,
            'collaboration_couples': collaboration_couples,
            'detailed_citations': detailed_citations,
            'all_publications': all_publications_data,
            'publications': self.publications,
            'citing_works': self.citing_works,
            'citations_map': self.citations_map
        }
        
        return self.analysis_results

# ============================================
# ФУНКЦИИ ГЕНЕРАЦИИ HTML ОТЧЕТА
# ============================================

def generate_journal_html_report(results: Dict, logo_base64: Optional[str] = None, 
                                 app_logo_base64: Optional[str] = None,
                                 theme_colors: Optional[Dict] = None,
                                 lang: str = 'en') -> str:
    """Generate HTML report for journal analysis"""
    
    if theme_colors is None:
        theme_colors = {
            'primary': '#667eea',
            'secondary': '#f39c12'
        }
    
    primary = theme_colors.get('primary', '#667eea')
    secondary = theme_colors.get('secondary', '#f39c12')
    
    def t(key: str, **kwargs) -> str:
        return translate(key, lang, **kwargs)
    
    # Extract data
    journal_name = results.get('journal_name', 'Unknown Journal')
    publisher = results.get('publisher', 'Unknown')
    issn = results.get('issn', '')
    
    total_pubs = results.get('total_publications', 0)
    total_citations = results.get('total_citations', 0)
    h_index = results.get('h_index', 0)
    g_index = results.get('g_index', 0)
    i10_index = results.get('i10_index', 0)
    i100_index = results.get('i100_index', 0)
    avg_citations = results.get('avg_citations', 0)
    active_years = results.get('active_years', 0)
    unique_authors = results.get('unique_authors', 0)
    unique_affiliations = results.get('unique_affiliations', 0)
    unique_countries = results.get('unique_countries', 0)
    avg_authors_per_paper = results.get('avg_authors_per_paper', 0)
    avg_affiliations_per_paper = results.get('avg_affiliations_per_paper', 0)
    avg_countries_per_paper = results.get('avg_countries_per_paper', 0)
    international_collab_rate = results.get('international_collaboration_rate', 0)
    unique_citing_authors = results.get('unique_citing_authors', 0)
    unique_citing_affiliations = results.get('unique_citing_affiliations', 0)
    unique_citing_countries = results.get('unique_citing_countries', 0)
    unique_citing_journals = results.get('unique_citing_journals', 0)
    unique_citing_publishers = results.get('unique_citing_publishers', 0)
    
    oa_breakdown = results.get('open_access_breakdown', {})
    top_affiliations = results.get('top_affiliations', {})
    author_stats = results.get('author_stats', [])
    citation_dynamics = results.get('citation_dynamics', {})
    cumulative_citations = results.get('cumulative_citations', {})
    citation_heatmap = results.get('citation_heatmap', {})
    most_cited = results.get('most_cited', [])
    top_citing_authors = results.get('top_citing_authors', {})
    top_citing_affiliations = results.get('top_citing_affiliations', {})
    top_citing_countries = results.get('top_citing_countries', {})
    top_citing_journals = results.get('top_citing_journals', {})
    top_citing_publishers = results.get('top_citing_publishers', {})
    top_topics = results.get('top_topics', {})
    top_cited_topics = results.get('top_cited_topics', {})
    top_cited_subtopics = results.get('top_cited_subtopics', {})
    top_cited_fields = results.get('top_cited_fields', {})
    top_cited_domains = results.get('top_cited_domains', {})
    top_cited_concepts = results.get('top_cited_concepts', {})
    unique_countries_per_pub = results.get('unique_countries_per_pub', [])
    authors_per_country = results.get('authors_per_country', {})
    collaboration_patterns = results.get('collaboration_patterns', {})
    collaboration_couples = results.get('collaboration_couples', {})
    detailed_citations = results.get('detailed_citations', {})
    all_publications = results.get('all_publications', [])
    
    total_citing_works = len(results.get('citing_works', []))
    
    # Build HTML
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>{t('app_title')} - {html.escape(journal_name)}</title>
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
                transition: transform 0.3s;
            }}
            .sidebar::-webkit-scrollbar {{
                width: 5px;
            }}
            .sidebar::-webkit-scrollbar-thumb {{
                background: rgba(255,255,255,0.3);
                border-radius: 10px;
            }}
            .sidebar-brand {{
                font-size: 20px;
                font-weight: 700;
                padding: 10px 0 20px 0;
                border-bottom: 2px solid rgba(255,255,255,0.2);
                margin-bottom: 15px;
                text-align: center;
            }}
            .sidebar-brand small {{
                font-size: 12px;
                font-weight: 400;
                opacity: 0.8;
                display: block;
                margin-top: 5px;
            }}
            .sidebar-section {{
                margin-bottom: 8px;
            }}
            .sidebar-section-title {{
                font-size: 11px;
                text-transform: uppercase;
                letter-spacing: 1px;
                opacity: 0.7;
                padding: 8px 12px 4px 12px;
                font-weight: 600;
            }}
            .sidebar a {{
                color: white;
                text-decoration: none;
                display: flex;
                align-items: center;
                gap: 10px;
                padding: 8px 12px;
                margin: 2px 0;
                border-radius: 8px;
                transition: all 0.3s;
                font-size: 14px;
                cursor: pointer;
            }}
            .sidebar a:hover {{
                background: rgba(255,255,255,0.2);
                transform: translateX(5px);
            }}
            .sidebar a .icon {{
                font-size: 18px;
                width: 24px;
                text-align: center;
            }}
            .sidebar a .arrow {{
                margin-left: auto;
                font-size: 12px;
                opacity: 0.6;
            }}
            .sidebar-sub {{
                padding-left: 30px;
            }}
            .sidebar-sub a {{
                font-size: 13px;
                padding: 6px 12px;
                opacity: 0.9;
            }}
            .sidebar-sub a:hover {{
                opacity: 1;
            }}
            
            /* Main Content */
            .main-content {{
                margin-left: 280px;
                padding: 30px 40px;
                min-height: 100vh;
            }}
            
            /* Header */
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
                margin-top: 8px;
                font-size: 16px;
            }}
            .header .date {{
                opacity: 0.8;
                margin-top: 10px;
                font-size: 13px;
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
            
            /* Sections */
            .section {{
                background: white;
                border-radius: 15px;
                padding: 25px;
                margin-bottom: 30px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                border: 1px solid #e8ecf1;
                scroll-margin-top: 20px;
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
            }}
            .section-title .icon {{
                font-size: 28px;
            }}
            
            /* Sub-section */
            .sub-section {{
                margin-top: 25px;
                padding-top: 20px;
                border-top: 1px solid #e8ecf1;
            }}
            .sub-section-title {{
                font-size: 18px;
                font-weight: 600;
                margin-bottom: 15px;
                color: #2C3E50;
            }}
            .sub-section-title .icon {{
                font-size: 20px;
                margin-right: 8px;
            }}
            
            /* Metrics Grid */
            .metrics-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
                gap: 12px;
                margin: 15px 0;
            }}
            .metric-card {{
                background: #f8f9fa;
                padding: 12px 15px;
                border-radius: 8px;
                border-left: 3px solid {primary};
                text-align: center;
                transition: transform 0.3s;
            }}
            .metric-card:hover {{
                transform: translateY(-3px);
                box-shadow: 0 4px 8px rgba(0,0,0,0.08);
            }}
            .metric-value {{
                font-size: 24px;
                font-weight: bold;
                color: #2C3E50;
                font-family: 'Times New Roman', serif;
            }}
            .metric-label {{
                font-size: 11px;
                color: #7F8C8D;
                margin-top: 3px;
                font-family: 'Times New Roman', serif;
            }}
            
            /* Tables */
            .table-container {{
                overflow-x: auto;
                max-height: 600px;
                overflow-y: auto;
                margin: 15px 0;
                border-radius: 8px;
                border: 1px solid #e8ecf1;
            }}
            .table-container table {{
                width: 100%;
                border-collapse: collapse;
                font-family: 'Times New Roman', serif;
                font-size: 13px;
            }}
            .table-container th {{
                background: linear-gradient(135deg, {primary} 0%, {secondary} 100%);
                color: white;
                padding: 10px 12px;
                text-align: left;
                position: sticky;
                top: 0;
                z-index: 10;
                font-weight: 600;
            }}
            .table-container td {{
                padding: 8px 12px;
                border-bottom: 1px solid #e8ecf1;
                vertical-align: top;
            }}
            .table-container tr:hover {{
                background-color: #f5f7fa;
            }}
            .table-container tr:nth-child(even) {{
                background-color: #fafbfc;
            }}
            .table-container tr:nth-child(even):hover {{
                background-color: #f5f7fa;
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
            
            .word-wrap {{
                word-wrap: break-word;
                max-width: 300px;
            }}
            
            .citation-count {{
                font-weight: 600;
                color: {primary};
            }}
            
            /* Progress Bar */
            .progress-bar-container {{
                background: #e8ecf1;
                border-radius: 10px;
                overflow: hidden;
                height: 20px;
                margin: 5px 0;
                position: relative;
            }}
            .progress-bar-fill {{
                height: 100%;
                background: linear-gradient(90deg, {primary}, {secondary});
                border-radius: 10px;
                transition: width 0.5s ease;
                display: flex;
                align-items: center;
                justify-content: flex-end;
                padding-right: 8px;
                font-size: 11px;
                color: white;
                font-weight: 600;
            }}
            
            /* Collapsible */
            .collapser {{
                padding: 12px 15px;
                background: #f8f9fa;
                border: 1px solid #e8ecf1;
                border-radius: 8px;
                margin-bottom: 5px;
                cursor: pointer;
                transition: all 0.3s;
                display: flex;
                align-items: center;
                flex-wrap: wrap;
                gap: 8px;
            }}
            .collapser:hover {{
                background: #e8ecf1;
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
            .badge-primary {{
                background: {primary}30;
                color: {primary};
            }}
            
            .citation-detail {{
                padding: 10px 15px;
                margin: 5px 0 5px 20px;
                background: #fafbfc;
                border-left: 3px solid {primary};
                border-radius: 4px;
                font-size: 13px;
            }}
            .citation-detail .cite-meta {{
                font-size: 12px;
                color: #666;
                margin-top: 3px;
            }}
            
            /* Filter section */
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
                align-items: flex-end;
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
                border: 1px solid #ddd;
                border-radius: 6px;
                font-size: 13px;
                font-family: 'Times New Roman', serif;
                background: white;
            }}
            .filter-row select:focus, .filter-row input:focus {{
                outline: none;
                border-color: {primary};
                box-shadow: 0 0 0 3px {primary}25;
            }}
            
            /* Footer */
            .footer {{
                margin-top: 40px;
                padding-top: 20px;
                border-top: 1px solid #e8ecf1;
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
            
            /* Progress in tables */
            .progress-cell {{
                min-width: 80px;
            }}
            
            /* Responsive */
            @media (max-width: 768px) {{
                .sidebar {{
                    transform: translateX(-100%);
                    width: 280px;
                }}
                .sidebar.open {{
                    transform: translateX(0);
                }}
                .main-content {{
                    margin-left: 0;
                    padding: 15px;
                }}
                .metrics-grid {{
                    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
                }}
                .filter-row > div {{
                    min-width: 120px;
                }}
            }}
            
            /* Hide toggle button for citations */
            .citation-content {{
                display: none;
            }}
            .citation-content.show {{
                display: block;
            }}
            
            /* Heatmap */
            .heatmap-grid {{
                display: grid;
                gap: 2px;
                margin: 10px 0;
            }}
            .heatmap-cell {{
                padding: 6px 8px;
                text-align: center;
                font-size: 12px;
                border-radius: 3px;
                font-weight: 500;
            }}
            .heatmap-header {{
                font-weight: 600;
                background: #f0f0f0;
                padding: 6px 8px;
                text-align: center;
                font-size: 12px;
                border-radius: 3px;
            }}
        </style>
    </head>
    <body>
        <!-- Sidebar Navigation -->
        <nav class="sidebar" id="sidebar">
            <div class="sidebar-brand">
                📊 {t('app_title')}
                <small>{html.escape(journal_name)}</small>
            </div>
            
            <div class="sidebar-section">
                <div class="sidebar-section-title">{t('overview')}</div>
                <a href="#overview"><span class="icon">📊</span> {t('overview')}</a>
            </div>
            
            <div class="sidebar-section">
                <div class="sidebar-section-title">{t('analyzed_articles')}</div>
                <a href="#author_analysis"><span class="icon">👤</span> {t('author_analysis')}</a>
                <a href="#top_affiliations"><span class="icon">🏛️</span> {t('top_affiliations')}</a>
                <a href="#geographic_analysis"><span class="icon">🌍</span> {t('geographic_analysis')}</a>
            </div>
            
            <div class="sidebar-section">
                <div class="sidebar-section-title">{t('citation_analysis')}</div>
                <a href="#citation_dynamics"><span class="icon">📈</span> {t('citation_dynamics')}</a>
                <a href="#cumulative_citations"><span class="icon">📊</span> {t('cumulative_citations')}</a>
                <a href="#citation_heatmap"><span class="icon">🔥</span> {t('citation_network_heatmap')}</a>
                <a href="#most_cited"><span class="icon">⭐</span> {t('most_cited_publications')}</a>
            </div>
            
            <div class="sidebar-section">
                <div class="sidebar-section-title">{t('citing_works')}</div>
                <a href="#citing_works"><span class="icon">📚</span> {t('citing_works_analysis')}</a>
            </div>
            
            <div class="sidebar-section">
                <div class="sidebar-section-title">{t('topics_analysis')}</div>
                <a href="#topics_analysis"><span class="icon">🏷️</span> {t('topics_analysis')}</a>
            </div>
            
            <div class="sidebar-section">
                <div class="sidebar-section-title">{t('detailed_citations')}</div>
                <a href="#detailed_citations"><span class="icon">📋</span> {t('detailed_citations')}</a>
            </div>
            
            <div class="sidebar-section">
                <div class="sidebar-section-title">{t('all_publications')}</div>
                <a href="#all_publications"><span class="icon">📚</span> {t('all_publications')}</a>
            </div>
        </nav>
        
        <!-- Main Content -->
        <div class="main-content">
            <!-- Header -->
            <div class="header">
                {f'<img src="data:image/png;base64,{app_logo_base64}" class="header-logo-app" alt="App Logo">' if app_logo_base64 else ''}
                {f'<img src="data:image/png;base64,{logo_base64}" class="header-logo" alt="Journal Logo">' if logo_base64 else ''}
                <h1>{t('app_title')}</h1>
                <div class="subtitle">{html.escape(journal_name)}</div>
                <div class="subtitle" style="font-size: 14px; opacity: 0.8;">ISSN: {issn} | {t('publisher') if lang=='en' else 'Издатель'}: {html.escape(publisher)}</div>
                <div class="date">{t('generated')}: {datetime.now().strftime('%d.%m.%Y %H:%M')}</div>
            </div>
            
            <!-- ============================================ -->
            <!-- SECTION 1: OVERVIEW -->
            <!-- ============================================ -->
            <div id="overview" class="section">
                <div class="section-title"><span class="icon">📊</span> {t('overview')}</div>
                
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-value">{total_pubs}</div>
                        <div class="metric-label">{t('total_publications')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{total_citations:,}</div>
                        <div class="metric-label">{t('total_citations')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{h_index}</div>
                        <div class="metric-label">{t('h_index')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{g_index}</div>
                        <div class="metric-label">{t('g_index')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{i10_index}</div>
                        <div class="metric-label">{t('i10_index')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{i100_index}</div>
                        <div class="metric-label">{t('i100_index')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{avg_citations:.1f}</div>
                        <div class="metric-label">{t('avg_citations')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{active_years}</div>
                        <div class="metric-label">{t('active_years')}</div>
                    </div>
                </div>
                
                <div style="margin-top: 15px;">
                    <div class="metrics-grid">
                        <div class="metric-card">
                            <div class="metric-value">{unique_authors}</div>
                            <div class="metric-label">{t('unique_authors')}</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{unique_affiliations}</div>
                            <div class="metric-label">{t('unique_affiliations')}</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{unique_countries}</div>
                            <div class="metric-label">{t('unique_countries')}</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{avg_authors_per_paper:.2f}</div>
                            <div class="metric-label">{t('avg_authors_per_paper')}</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{avg_affiliations_per_paper:.2f}</div>
                            <div class="metric-label">{t('avg_affiliations_per_paper')}</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{avg_countries_per_paper:.2f}</div>
                            <div class="metric-label">{t('avg_countries_per_paper')}</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{international_collab_rate*100:.1f}%</div>
                            <div class="metric-label">{t('international_collaboration_rate')}</div>
                        </div>
                    </div>
                </div>
                
                <div style="margin-top: 15px;">
                    <div class="metrics-grid">
                        <div class="metric-card">
                            <div class="metric-value">{unique_citing_authors}</div>
                            <div class="metric-label">{t('unique_citing_authors')}</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{unique_citing_affiliations}</div>
                            <div class="metric-label">{t('unique_citing_affiliations')}</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{unique_citing_countries}</div>
                            <div class="metric-label">{t('unique_citing_countries')}</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{unique_citing_journals}</div>
                            <div class="metric-label">{t('unique_citing_journals')}</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{unique_citing_publishers}</div>
                            <div class="metric-label">{t('unique_citing_publishers')}</div>
                        </div>
                    </div>
                </div>
                
                <!-- Open Access Breakdown -->
                <div class="sub-section">
                    <div class="sub-section-title"><span class="icon">🔓</span> {t('open_access_breakdown')}</div>
                    <div class="metrics-grid">
                        {f'<div class="metric-card"><div class="metric-value">{oa_breakdown.get("gold", 0)}</div><div class="metric-label">{t("gold")}</div></div>' if oa_breakdown.get("gold", 0) > 0 else ''}
                        {f'<div class="metric-card"><div class="metric-value">{oa_breakdown.get("hybrid", 0)}</div><div class="metric-label">{t("hybrid")}</div></div>' if oa_breakdown.get("hybrid", 0) > 0 else ''}
                        {f'<div class="metric-card"><div class="metric-value">{oa_breakdown.get("green", 0)}</div><div class="metric-label">{t("green")}</div></div>' if oa_breakdown.get("green", 0) > 0 else ''}
                        {f'<div class="metric-card"><div class="metric-value">{oa_breakdown.get("bronze", 0)}</div><div class="metric-label">{t("bronze")}</div></div>' if oa_breakdown.get("bronze", 0) > 0 else ''}
                        {f'<div class="metric-card"><div class="metric-value">{oa_breakdown.get("diamond", 0)}</div><div class="metric-label">{t("diamond")}</div></div>' if oa_breakdown.get("diamond", 0) > 0 else ''}
                        {f'<div class="metric-card"><div class="metric-value">{oa_breakdown.get("closed", 0)}</div><div class="metric-label">{t("closed")}</div></div>' if oa_breakdown.get("closed", 0) > 0 else ''}
                        {f'<div class="metric-card"><div class="metric-value">{oa_breakdown.get("unknown", 0)}</div><div class="metric-label">{t("unknown")}</div></div>' if oa_breakdown.get("unknown", 0) > 0 else ''}
                    </div>
                </div>
            </div>
            
            <!-- ============================================ -->
            <!-- SECTION 2: ANALYZED ARTICLES -->
            <!-- ============================================ -->
            <div id="analyzed_articles" class="section">
                <div class="section-title"><span class="icon">📄</span> {t('analyzed_articles')}</div>
                
                <!-- 5.1 Author Analysis -->
                <div id="author_analysis" class="sub-section">
                    <div class="sub-section-title"><span class="icon">👤</span> {t('author_analysis')}</div>
                    <div class="table-container">
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
                                {''.join([
                                    f'''
                                    <tr>
                                        <td>{i+1}</td>
                                        <td>{html.escape(author['name'])}</td>
                                        <td>N/A</td>
                                        <td>{', '.join([html.escape(a) for a in author['affiliations'][:3]]) + ('...' if len(author['affiliations']) > 3 else '')}</td>
                                        <td>{', '.join([html.escape(c) for c in author['countries'][:3]]) + ('...' if len(author['countries']) > 3 else '')}</td>
                                        <td>{author['publications']}</td>
                                        <td><span class="citation-count">{author['citations']}</span></td>
                                    </tr>
                                    '''
                                    for i, author in enumerate(author_stats[:50])
                                ])}
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <!-- 5.2 Top Affiliations -->
                <div id="top_affiliations" class="sub-section">
                    <div class="sub-section-title"><span class="icon">🏛️</span> {t('top_affiliations')}</div>
                    <div class="table-container">
                        <table>
                            <thead>
                                <tr>
                                    <th>{t('rank')}</th>
                                    <th>{t('affiliations')}</th>
                                    <th>{t('publications')}</th>
                                </tr>
                            </thead>
                            <tbody>
                                {''.join([
                                    f'''
                                    <tr>
                                        <td>{i+1}</td>
                                        <td>{html.escape(affil)}</td>
                                        <td>{count}</td>
                                    </tr>
                                    '''
                                    for i, (affil, count) in enumerate(list(top_affiliations.items())[:20])
                                ])}
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <!-- 5.3 Geographic Analysis -->
                <div id="geographic_analysis" class="sub-section">
                    <div class="sub-section-title"><span class="icon">🌍</span> {t('geographic_analysis')}</div>
                    
                    <!-- 5.3.1 Unique Countries per Publication -->
                    <div style="margin-bottom: 20px;">
                        <h4 style="color: {primary}; margin-bottom: 10px;">{t('unique_countries_per_publication')}</h4>
                        <div class="table-container">
                            <table>
                                <thead>
                                    <tr>
                                        <th>#</th>
                                        <th>{t('title')}</th>
                                        <th>{t('year')}</th>
                                        <th>{t('countries')}</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {''.join([
                                        f'''
                                        <tr>
                                            <td>{i+1}</td>
                                            <td class="word-wrap">{html.escape(item['publication'])}</td>
                                            <td>{item['year']}</td>
                                            <td>{item['countries']}</td>
                                        </tr>
                                        '''
                                        for i, item in enumerate(unique_countries_per_pub[:30])
                                    ])}
                                </tbody>
                            </table>
                        </div>
                    </div>
                    
                    <!-- 5.3.2 Authors per Country -->
                    <div style="margin-bottom: 20px;">
                        <h4 style="color: {primary}; margin-bottom: 10px;">{t('authors_per_country')}</h4>
                        <div class="table-container">
                            <table>
                                <thead>
                                    <tr>
                                        <th>{t('rank')}</th>
                                        <th>{t('countries')}</th>
                                        <th>{t('authors')}</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {''.join([
                                        f'''
                                        <tr>
                                            <td>{i+1}</td>
                                            <td>{html.escape(country)}</td>
                                            <td>{count}</td>
                                        </tr>
                                        '''
                                        for i, (country, count) in enumerate(list(authors_per_country.items())[:20])
                                    ])}
                                </tbody>
                            </table>
                        </div>
                    </div>
                    
                    <!-- 5.3.3 Collaboration Patterns -->
                    <div style="margin-bottom: 20px;">
                        <h4 style="color: {primary}; margin-bottom: 10px;">{t('collaboration_patterns')}</h4>
                        <div class="metrics-grid">
                            <div class="metric-card">
                                <div class="metric-value">{collaboration_patterns.get('single_country', 0)}</div>
                                <div class="metric-label">{t('single_country')}</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-value">{collaboration_patterns.get('international', 0)}</div>
                                <div class="metric-label">{t('international')}</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-value">{collaboration_patterns.get('total', 0)}</div>
                                <div class="metric-label">{t('total_publications')}</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-value">{ (collaboration_patterns.get('international', 0) / collaboration_patterns.get('total', 1) * 100):.1f}%</div>
                                <div class="metric-label">{t('international_collaboration_rate')}</div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- 5.3.4 Collaboration Couples -->
                    <div>
                        <h4 style="color: {primary}; margin-bottom: 10px;">{t('collaboration_couples')}</h4>
                        <div class="table-container">
                            <table>
                                <thead>
                                    <tr>
                                        <th>{t('rank')}</th>
                                        <th>{t('country_pair')}</th>
                                        <th>{t('collaborations')}</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {''.join([
                                        f'''
                                        <tr>
                                            <td>{i+1}</td>
                                            <td>{html.escape(pair[0])} — {html.escape(pair[1])}</td>
                                            <td>{count}</td>
                                        </tr>
                                        '''
                                        for i, (pair, count) in enumerate(list(collaboration_couples.items())[:20])
                                    ])}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- ============================================ -->
            <!-- SECTION 3: CITATION ANALYSIS -->
            <!-- ============================================ -->
            <div id="citation_analysis" class="section">
                <div class="section-title"><span class="icon">📈</span> {t('citation_analysis')}</div>
                
                <!-- 6.1 Citation Dynamics by Year -->
                <div id="citation_dynamics" class="sub-section">
                    <div class="sub-section-title"><span class="icon">📊</span> {t('citation_dynamics')}</div>
                    <div class="table-container">
                        <table>
                            <thead>
                                <tr>
                                    <th>{t('publication_year')}</th>
                                    <th>{t('citation_year')}</th>
                                    <th>{t('citations_count')}</th>
                                </tr>
                            </thead>
                            <tbody>
                                {''.join([
                                    f'''
                                    <tr>
                                        <td>{pub_year}</td>
                                        <td>{cite_year}</td>
                                        <td>{count}</td>
                                    </tr>
                                    '''
                                    for pub_year in sorted(citation_dynamics.keys())
                                    for cite_year in sorted(citation_dynamics[pub_year].keys())
                                    if citation_dynamics[pub_year][cite_year] > 0
                                ])}
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <!-- 6.2 Cumulative Citations -->
                <div id="cumulative_citations" class="sub-section">
                    <div class="sub-section-title"><span class="icon">📈</span> {t('cumulative_citations')}</div>
                    <div class="table-container">
                        <table>
                            <thead>
                                <tr>
                                    <th>{t('year')}</th>
                                    <th>{t('cumulative_citations')}</th>
                                </tr>
                            </thead>
                            <tbody>
                                {''.join([
                                    f'''
                                    <tr>
                                        <td>{year}</td>
                                        <td>{count} {t('citations') if count > 1 else t('citation') if lang=='en' else 'цитирований'}</td>
                                    </tr>
                                    '''
                                    for year, count in sorted(cumulative_citations.items())
                                ])}
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <!-- 6.3 Citation Network Heatmap -->
                <div id="citation_heatmap" class="sub-section">
                    <div class="sub-section-title"><span class="icon">🔥</span> {t('citation_network_heatmap')}</div>
                    <div class="table-container">
                        <table>
                            <thead>
                                <tr>
                                    <th>{t('publication_year')} \\ {t('citation_year')}</th>
                                    {''.join([
                                        f'<th>{year}</th>'
                                        for year in sorted(set().union(*[set(citation_heatmap.get(pub_year, {}).keys()) for pub_year in citation_heatmap.keys()]))
                                    ])}
                                </tr>
                            </thead>
                            <tbody>
                                {''.join([
                                    f'''
                                    <tr>
                                        <td><strong>{pub_year}</strong></td>
                                        {''.join([
                                            f'''
                                            <td style="background: {_get_heatmap_color(count, max_val)}; color: {get_contrast_color(_get_heatmap_color(count, max_val))}">
                                                {count if count > 0 else '-'}
                                            </td>
                                            '''
                                            for cite_year in sorted(set().union(*[set(citation_heatmap.get(p, {}).keys()) for p in citation_heatmap.keys()]))
                                            for count in [citation_heatmap.get(pub_year, {}).get(cite_year, 0)]
                                        ])}
                                    </tr>
                                    '''
                                    for pub_year in sorted(citation_heatmap.keys())
                                ])}
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <!-- 6.4 Most Cited Publications -->
                <div id="most_cited" class="sub-section">
                    <div class="sub-section-title"><span class="icon">⭐</span> {t('most_cited_publications')}</div>
                    <div class="table-container">
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
                                {''.join([
                                    f'''
                                    <tr>
                                        <td>{i+1}</td>
                                        <td class="word-wrap">{html.escape(pub['title'])}</td>
                                        <td>{pub['year']}</td>
                                        <td><span class="citation-count">{pub['citations']}</span></td>
                                        <td>{pub['citations_per_year']:.1f}</td>
                                        <td>{html.escape(pub['authors'])}</td>
                                        <td><a href="https://doi.org/{pub['doi']}" target="_blank" class="doi-link">{pub['doi']}</a></td>
                                    </tr>
                                    '''
                                    for i, pub in enumerate(most_cited[:20])
                                ])}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
            
            <!-- ============================================ -->
            <!-- SECTION 4: CITING WORKS -->
            <!-- ============================================ -->
            <div id="citing_works" class="section">
                <div class="section-title"><span class="icon">📚</span> {t('citing_works_analysis')}</div>
                
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-value">{total_citing_works}</div>
                        <div class="metric-label">{t('total_citing_works')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{unique_citing_authors}</div>
                        <div class="metric-label">{t('unique_citing_authors')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{unique_citing_affiliations}</div>
                        <div class="metric-label">{t('unique_citing_affiliations')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{unique_citing_countries}</div>
                        <div class="metric-label">{t('unique_citing_countries')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{unique_citing_journals}</div>
                        <div class="metric-label">{t('unique_citing_journals')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{unique_citing_publishers}</div>
                        <div class="metric-label">{t('unique_citing_publishers')}</div>
                    </div>
                </div>
                
                <!-- 7.1 Top Citing Authors -->
                <div class="sub-section">
                    <div class="sub-section-title"><span class="icon">👤</span> {t('top_citing_authors')}</div>
                    <div class="table-container">
                        <table>
                            <thead>
                                <tr>
                                    <th>{t('rank')}</th>
                                    <th>{t('authors')}</th>
                                    <th>{t('citations')}</th>
                                </tr>
                            </thead>
                            <tbody>
                                {''.join([
                                    f'''
                                    <tr>
                                        <td>{i+1}</td>
                                        <td>{html.escape(author)}</td>
                                        <td>{count}</td>
                                    </tr>
                                    '''
                                    for i, (author, count) in enumerate(list(top_citing_authors.items())[:20])
                                ])}
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <!-- 7.2 Top Citing Affiliations -->
                <div class="sub-section">
                    <div class="sub-section-title"><span class="icon">🏛️</span> {t('top_citing_affiliations')}</div>
                    <div class="table-container">
                        <table>
                            <thead>
                                <tr>
                                    <th>{t('rank')}</th>
                                    <th>{t('affiliations')}</th>
                                    <th>{t('citations')}</th>
                                </tr>
                            </thead>
                            <tbody>
                                {''.join([
                                    f'''
                                    <tr>
                                        <td>{i+1}</td>
                                        <td>{html.escape(affil)}</td>
                                        <td>{count}</td>
                                    </tr>
                                    '''
                                    for i, (affil, count) in enumerate(list(top_citing_affiliations.items())[:20])
                                ])}
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <!-- 7.3 Top Citing Countries -->
                <div class="sub-section">
                    <div class="sub-section-title"><span class="icon">🌍</span> {t('top_citing_countries')}</div>
                    <div class="table-container">
                        <table>
                            <thead>
                                <tr>
                                    <th>{t('rank')}</th>
                                    <th>{t('countries')}</th>
                                    <th>{t('citations')}</th>
                                </tr>
                            </thead>
                            <tbody>
                                {''.join([
                                    f'''
                                    <tr>
                                        <td>{i+1}</td>
                                        <td>{html.escape(country)}</td>
                                        <td>{count}</td>
                                    </tr>
                                    '''
                                    for i, (country, count) in enumerate(list(top_citing_countries.items())[:20])
                                ])}
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <!-- 7.4 Top Citing Journals -->
                <div class="sub-section">
                    <div class="sub-section-title"><span class="icon">📰</span> {t('top_citing_journals')}</div>
                    <div class="table-container">
                        <table>
                            <thead>
                                <tr>
                                    <th>{t('rank')}</th>
                                    <th>{t('journal')}</th>
                                    <th>{t('citations')}</th>
                                </tr>
                            </thead>
                            <tbody>
                                {''.join([
                                    f'''
                                    <tr>
                                        <td>{i+1}</td>
                                        <td>{html.escape(journal)}</td>
                                        <td>{count}</td>
                                    </tr>
                                    '''
                                    for i, (journal, count) in enumerate(list(top_citing_journals.items())[:20])
                                ])}
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <!-- 7.5 Top Citing Publishers -->
                <div class="sub-section">
                    <div class="sub-section-title"><span class="icon">📚</span> {t('top_citing_publishers')}</div>
                    <div class="table-container">
                        <table>
                            <thead>
                                <tr>
                                    <th>{t('rank')}</th>
                                    <th>{t('publisher') if lang=='en' else 'Издательство'}</th>
                                    <th>{t('citations')}</th>
                                </tr>
                            </thead>
                            <tbody>
                                {''.join([
                                    f'''
                                    <tr>
                                        <td>{i+1}</td>
                                        <td>{html.escape(publisher_name)}</td>
                                        <td>{count}</td>
                                    </tr>
                                    '''
                                    for i, (publisher_name, count) in enumerate(list(top_citing_publishers.items())[:20])
                                ])}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
            
            <!-- ============================================ -->
            <!-- SECTION 5: TOPICS ANALYSIS -->
            <!-- ============================================ -->
            <div id="topics_analysis" class="section">
                <div class="section-title"><span class="icon">🏷️</span> {t('topics_analysis')}</div>
                
                <!-- 8.1 Topics Table -->
                <div class="table-container">
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
                            {''.join([
                                f'''
                                <tr>
                                    <td class="word-wrap">{html.escape(topic)}</td>
                                    <td>{data['analyzed_count']}</td>
                                    <td>{data['citing_count']}</td>
                                    <td>{data['analyzed_norm_count']:.3f}</td>
                                    <td>{data['citing_norm_count']:.3f}</td>
                                    <td><strong>{data['total_norm_count']:.3f}</strong></td>
                                    <td>{data['first_year'] or 'N/A'}</td>
                                    <td>{data['peak_year'] or 'N/A'}</td>
                                </tr>
                                '''
                                for topic, data in list(top_topics.items())[:20]
                            ])}
                        </tbody>
                    </table>
                </div>
                
                <!-- 8.2 Top Cited Topics, Subtopics, Fields, Domains, Concepts -->
                <div class="sub-section">
                    <div class="sub-section-title"><span class="icon">🏆</span> {t('top_cited_topics')}</div>
                    <div class="table-container">
                        <table>
                            <thead>
                                <tr>
                                    <th>{t('rank')}</th>
                                    <th>{t('topics')}</th>
                                    <th>{t('citations')}</th>
                                </tr>
                            </thead>
                            <tbody>
                                {''.join([
                                    f'''
                                    <tr>
                                        <td>{i+1}</td>
                                        <td>{html.escape(topic)}</td>
                                        <td><span class="citation-count">{count}</span></td>
                                    </tr>
                                    '''
                                    for i, (topic, count) in enumerate(list(top_cited_topics.items())[:10])
                                ])}
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <div class="sub-section">
                    <div class="sub-section-title"><span class="icon">📂</span> {t('top_cited_subtopics')}</div>
                    <div class="table-container">
                        <table>
                            <thead>
                                <tr>
                                    <th>{t('rank')}</th>
                                    <th>{t('subtopics')}</th>
                                    <th>{t('citations')}</th>
                                </tr>
                            </thead>
                            <tbody>
                                {''.join([
                                    f'''
                                    <tr>
                                        <td>{i+1}</td>
                                        <td>{html.escape(subtopic)}</td>
                                        <td><span class="citation-count">{count}</span></td>
                                    </tr>
                                    '''
                                    for i, (subtopic, count) in enumerate(list(top_cited_subtopics.items())[:10])
                                ])}
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <div class="sub-section">
                    <div class="sub-section-title"><span class="icon">🔬</span> {t('top_cited_fields')}</div>
                    <div class="table-container">
                        <table>
                            <thead>
                                <tr>
                                    <th>{t('rank')}</th>
                                    <th>{t('fields')}</th>
                                    <th>{t('citations')}</th>
                                </tr>
                            </thead>
                            <tbody>
                                {''.join([
                                    f'''
                                    <tr>
                                        <td>{i+1}</td>
                                        <td>{html.escape(field)}</td>
                                        <td><span class="citation-count">{count}</span></td>
                                    </tr>
                                    '''
                                    for i, (field, count) in enumerate(list(top_cited_fields.items())[:10])
                                ])}
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <div class="sub-section">
                    <div class="sub-section-title"><span class="icon">🌐</span> {t('top_cited_domains')}</div>
                    <div class="table-container">
                        <table>
                            <thead>
                                <tr>
                                    <th>{t('rank')}</th>
                                    <th>{t('domains')}</th>
                                    <th>{t('citations')}</th>
                                </tr>
                            </thead>
                            <tbody>
                                {''.join([
                                    f'''
                                    <tr>
                                        <td>{i+1}</td>
                                        <td>{html.escape(domain)}</td>
                                        <td><span class="citation-count">{count}</span></td>
                                    </tr>
                                    '''
                                    for i, (domain, count) in enumerate(list(top_cited_domains.items())[:10])
                                ])}
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <div class="sub-section">
                    <div class="sub-section-title"><span class="icon">💡</span> {t('top_cited_concepts')}</div>
                    <div class="table-container">
                        <table>
                            <thead>
                                <tr>
                                    <th>{t('rank')}</th>
                                    <th>{t('concepts')}</th>
                                    <th>{t('citations')}</th>
                                </tr>
                            </thead>
                            <tbody>
                                {''.join([
                                    f'''
                                    <tr>
                                        <td>{i+1}</td>
                                        <td>{html.escape(concept)}</td>
                                        <td><span class="citation-count">{count}</span></td>
                                    </tr>
                                    '''
                                    for i, (concept, count) in enumerate(list(top_cited_concepts.items())[:10])
                                ])}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
            
            <!-- ============================================ -->
            <!-- SECTION 6: DETAILED CITATIONS -->
            <!-- ============================================ -->
            <div id="detailed_citations" class="section">
                <div class="section-title"><span class="icon">📋</span> {t('detailed_citations')}</div>
                
                {''.join([
                    f'''
                    <div class="collapser" onclick="toggleCitations('{pub_id.replace('https://openalex.org/', '')}')">
                        <strong>{html.escape(data['title'])[:100]}{'...' if len(html.escape(data['title'])) > 100 else ''}</strong>
                        <span class="badge badge-info">{data['year']}</span>
                        <span class="citation-count">{data['total_citations']} {t('citations') if data['total_citations'] > 1 else t('citation') if lang=='en' else 'цитирований'}</span>
                        <span style="font-size: 12px; color: #666; margin-left: 10px;">DOI: {data['doi']}</span>
                        <span style="float: right; font-size: 12px; color: {primary};">{t('click_to_toggle')}</span>
                    </div>
                    <div id="citations_{pub_id.replace('https://openalex.org/', '')}" class="citation-content">
                        {''.join([
                            f'''
                            <div class="citation-detail">
                                <div><strong>{html.escape(cite['citing_title'])[:150]}{'...' if len(html.escape(cite['citing_title'])) > 150 else ''}</strong></div>
                                <div class="cite-meta">
                                    <strong>{t('citing_journal')}:</strong> {html.escape(cite['citing_journal'])} | 
                                    <strong>{t('citing_year')}:</strong> {cite['citing_year']} | 
                                    <strong>{t('citing_date')}:</strong> {cite['citing_date']} |
                                    <strong>{t('citation_lag')}:</strong> {cite['citation_lag']} {t('years') if lang=='en' else 'лет' if cite['citation_lag'] and cite['citation_lag'] > 1 else 'год' if cite['citation_lag'] else ''}
                                </div>
                                <div class="cite-meta">
                                    <strong>{t('authors')}:</strong> {', '.join([html.escape(a) for a in cite['citing_authors'][:5]])}{' +' + str(len(cite['citing_authors']) - 5) + ' more' if len(cite['citing_authors']) > 5 else ''} |
                                    <strong>{t('countries')}:</strong> {', '.join([html.escape(c) for c in cite['citing_countries'][:3]]) + ('...' if len(cite['citing_countries']) > 3 else '')}
                                </div>
                                <div class="cite-meta">
                                    <a href="https://doi.org/{cite['citing_doi']}" target="_blank" class="doi-link">DOI: {cite['citing_doi']}</a>
                                </div>
                            </div>
                            ''' for cite in data['citations'][:20]
                        ])}
                        {f'<div style="padding: 8px 15px; color: #666; font-style: italic;">... and {len(data["citations"]) - 20} more citations</div>' if len(data['citations']) > 20 else ''}
                    </div>
                    ''' for pub_id, data in detailed_citations.items()
                ])}
                
                <script>
                function toggleCitations(id) {{
                    var el = document.getElementById('citations_' + id);
                    if (el) {{
                        el.classList.toggle('show');
                        var parent = el.previousElementSibling;
                        if (parent && parent.classList.contains('collapser')) {{
                            if (el.classList.contains('show')) {{
                                parent.style.borderLeft = '3px solid {primary}';
                            }} else {{
                                parent.style.borderLeft = 'none';
                            }}
                        }}
                    }}
                }}
                </script>
            </div>
            
            <!-- ============================================ -->
            <!-- SECTION 7: ALL PUBLICATIONS -->
            <!-- ============================================ -->
            <div id="all_publications" class="section">
                <div class="section-title"><span class="icon">📚</span> {t('all_publications')}</div>
                
                <!-- Filter Section -->
                <div class="filter-section">
                    <div class="filter-row">
                        <div>
                            <label for="yearFilter">{t('filter_by_year')}:</label>
                            <select id="yearFilter" onchange="filterPublications()">
                                <option value="">{t('all_years')}</option>
                                {''.join([
                                    f'<option value="{year}">{year}</option>'
                                    for year in sorted(set(p['year'] for p in all_publications if p['year']), reverse=True)
                                ])}
                            </select>
                        </div>
                        <div>
                            <label for="titleFilter">{t('filter_by_title')}:</label>
                            <input type="text" id="titleFilter" placeholder="{t('filter_by_title')}..." onkeyup="filterPublications()">
                        </div>
                        <div>
                            <label for="authorFilter">{t('filter_by_author')}:</label>
                            <input type="text" id="authorFilter" placeholder="Author name..." onkeyup="filterPublications()">
                        </div>
                        <div>
                            <label for="affilFilter">{t('filter_by_affiliations')}:</label>
                            <input type="text" id="affilFilter" placeholder="Affiliation..." onkeyup="filterPublications()">
                        </div>
                        <div>
                            <label for="citationFilter">{t('filter_by_citations')}:</label>
                            <input type="number" id="citationFilter" placeholder="Min citations..." min="0" onchange="filterPublications()">
                        </div>
                        <div>
                            <span id="visibleCount" style="font-weight: 500; display: block; margin-top: 20px;">{t('visible_count')}: {len(all_publications)}</span>
                        </div>
                    </div>
                </div>
                
                <!-- Publications Table -->
                <div class="table-container">
                    <table id="publicationsTable">
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
                            {''.join([
                                f'''
                                <tr data-year="{p['year']}" data-title="{p['title'].lower()}" data-authors="{p['authors'].lower()}" data-affils="{p['affiliations'].lower()}" data-citations="{p['citations']}">
                                    <td>{p['index']}</td>
                                    <td class="word-wrap">{html.escape(p['title'])}</td>
                                    <td>{p['year']}</td>
                                    <td>{html.escape(p['authors'])}</td>
                                    <td>{html.escape(p['affiliations'])}</td>
                                    <td><span class="citation-count">{p['citations']}</span></td>
                                    <td>{p['citations_per_year']:.1f}</td>
                                    <td><a href="https://doi.org/{p['doi']}" target="_blank" class="doi-link">{p['doi']}</a></td>
                                </tr>
                                '''
                                for p in all_publications
                            ])}
                        </tbody>
                    </table>
                </div>
            </div>
            
            <!-- Footer -->
            <div class="footer">
                <p>{t('footer')}</p>
                <p><a href="{t('journal_url')}" target="_blank">{t('journal_url')}</a></p>
                <p style="font-size: 11px; margin-top: 5px;">{t('data_source')} | {t('generated')}: {datetime.now().strftime('%d.%m.%Y %H:%M')}</p>
            </div>
        </div>
        
        <script>
        // Filter function
        function filterPublications() {{
            var yearFilter = document.getElementById('yearFilter').value;
            var titleFilter = document.getElementById('titleFilter').value.toLowerCase();
            var authorFilter = document.getElementById('authorFilter').value.toLowerCase();
            var affilFilter = document.getElementById('affilFilter').value.toLowerCase();
            var citationFilter = parseInt(document.getElementById('citationFilter').value) || 0;
            
            var rows = document.querySelectorAll('#publicationsTable tbody tr');
            var visible = 0;
            
            rows.forEach(function(row) {{
                var year = row.getAttribute('data-year');
                var title = row.getAttribute('data-title');
                var authors = row.getAttribute('data-authors');
                var affils = row.getAttribute('data-affils');
                var citations = parseInt(row.getAttribute('data-citations')) || 0;
                
                var show = true;
                
                if (yearFilter && year !== yearFilter) show = false;
                if (titleFilter && !title.includes(titleFilter)) show = false;
                if (authorFilter && !authors.includes(authorFilter)) show = false;
                if (affilFilter && !affils.includes(affilFilter)) show = false;
                if (citations < citationFilter) show = false;
                
                row.style.display = show ? '' : 'none';
                if (show) visible++;
            }});
            
            document.getElementById('visibleCount').textContent = '{t('visible_count')}: ' + visible;
        }}
        
        // Sort function
        var sortOrder = {{}};
        function sortTable(column) {{
            var table = document.getElementById('publicationsTable');
            var tbody = table.querySelector('tbody');
            var rows = Array.from(tbody.querySelectorAll('tr'));
            var ascending = sortOrder[column] !== 'asc';
            sortOrder[column] = ascending ? 'asc' : 'desc';
            
            rows.sort(function(a, b) {{
                var aVal = a.cells[column].textContent.trim();
                var bVal = b.cells[column].textContent.trim();
                
                // Check if numeric
                if (!isNaN(aVal) && !isNaN(bVal)) {{
                    return ascending ? parseFloat(aVal) - parseFloat(bVal) : parseFloat(bVal) - parseFloat(aVal);
                }}
                return ascending ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
            }});
            
            rows.forEach(function(row) {{
                tbody.appendChild(row);
            }});
        }}
        </script>
    </body>
    </html>
    """
    
    return html_content

def _get_heatmap_color(count: int, max_val: int) -> str:
    """Get color for heatmap cell based on count value"""
    if count == 0:
        return '#f0f0f0'
    
    # Use primary color gradient
    primary = st.session_state.get('primary_color', '#667eea')
    rgb = hex_to_rgb(primary)
    
    intensity = count / max_val if max_val > 0 else 0
    intensity = min(intensity, 1.0)
    
    # Blend from light to full color
    r = int(rgb[0] * intensity + 240 * (1 - intensity))
    g = int(rgb[1] * intensity + 240 * (1 - intensity))
    b = int(rgb[2] * intensity + 240 * (1 - intensity))
    
    return f'rgb({r}, {g}, {b})'

# ============================================
# ОСНОВНАЯ ФУНКЦИЯ ЗАПУСКА ДЛЯ STREAMLIT
# ============================================

def run_journal_analysis(issn: str, period: Any, max_workers: int = 8, journal_logo: Optional[Dict] = None):
    """Run complete journal analysis with progress tracking"""
    
    current_lang = st.session_state.get('language', 'en')
    def t(key: str, **kwargs) -> str:
        return translate(key, current_lang, **kwargs)
    
    if not issn:
        st.error(t('no_issn'))
        return
    
    if not period:
        st.error(t('no_period'))
        return
    
    # Clear cache if needed
    st.cache_data.clear()
    
    # Progress tracking
    progress_container = st.empty()
    status_container = st.empty()
    analysis_progress = st.progress(0, text=t('starting_analysis'))
    
    try:
        # Load app logo
        app_logo_base64 = None
        if os.path.exists("icon.png"):
            try:
                with open("icon.png", "rb") as f:
                    app_logo_base64 = base64.b64encode(f.read()).decode()
            except Exception as e:
                if SHOW_DEBUG_LOGS:
                    print(f"⚠️ Error loading app logo: {e}")
        
        # Load journal logo
        journal_logo_base64 = None
        if journal_logo:
            try:
                for filename, file_info in journal_logo.items():
                    content = file_info['content'] if hasattr(file_info, 'get') else file_info
                    if hasattr(content, 'read'):
                        content = content.read()
                    journal_logo_base64 = base64.b64encode(content).decode()
                    if SHOW_DEBUG_LOGS:
                        print(f"✅ Journal logo loaded: {filename}")
                    break
            except Exception as e:
                if SHOW_DEBUG_LOGS:
                    print(f"⚠️ Error loading journal logo: {e}")
        
        # Parse period
        if isinstance(period, str):
            if ',' in period:
                years = [int(y.strip()) for y in period.split(',') if y.strip().isdigit()]
            elif '-' in period:
                parts = period.split('-')
                if len(parts) == 2:
                    years = tuple(map(int, [x.strip() for x in parts]))
                else:
                    years = int(period.strip())
            else:
                years = int(period.strip())
        else:
            years = period
        
        # Create analyzer
        analyzer = JournalAnalyzer(issn, years, max_workers)
        
        # Setup progress callback
        def progress_callback(percent: float, message: str = ""):
            analysis_progress.progress(percent / 100, text=message)
            status_container.info(message)
        
        analyzer.set_progress_callback(progress_callback)
        
        # Run analysis
        start_time = time.time()
        results = analyzer.analyze()
        
        if results.get('error') == 'no_publications':
            st.warning(t('no_publications_found'))
            analysis_progress.empty()
            return
        
        elapsed = time.time() - start_time
        
        # Store results in session state
        st.session_state['journal_results'] = results
        st.session_state['journal_logo_base64'] = journal_logo_base64
        st.session_state['app_logo_base64'] = app_logo_base64
        st.session_state['analysis_complete'] = True
        st.session_state['journal_name'] = results.get('journal_name', 'Unknown Journal')
        
        analysis_progress.progress(1.0, text=t('analysis_complete_text'))
        
        st.success(t('analysis_complete', count=results.get('total_publications', 0), time=elapsed))
        
        # Generate HTML report immediately
        with st.spinner(t('generating_report_text')):
            theme_colors = {
                'primary': st.session_state.get('primary_color', '#667eea'),
                'secondary': st.session_state.get('secondary_color', '#f39c12')
            }
            
            html_report = generate_journal_html_report(
                results,
                journal_logo_base64,
                app_logo_base64,
                theme_colors,
                current_lang
            )
            
            st.session_state['html_report'] = html_report
            
            # Show report preview
            st.markdown(f"## {t('html_report')}")
            st.info(t('download_hint'))
            
            # Download button
            filename = f"journal_analysis_{normalize_issn(issn)}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            st.download_button(
                label=t('download_report_button'),
                data=html_report.encode('utf-8'),
                file_name=filename,
                mime="text/html",
                type="primary",
                use_container_width=True
            )
            
            # Show preview with iframe
            st.markdown("---")
            st.markdown(f"### {t('report_preview')}")
            
            # Use HTML display with sandbox
            st.components.v1.html(
                html_report,
                height=800,
                scrolling=True,
                sandbox="allow-scripts allow-modals allow-same-origin"
            )
        
        st.balloons()
        
    except Exception as e:
        st.error(f"❌ {t('error_occurred')}: {str(e)}")
        import traceback
        st.code(traceback.format_exc())
    finally:
        analysis_progress.empty()
        status_container.empty()

# ============================================
# СОЗДАНИЕ WIDGET-ИНТЕРФЕЙСА STREAMLIT
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
    if 'all_authors' not in st.session_state:
        st.session_state.all_authors = []
    if 'analysis_complete' not in st.session_state:
        st.session_state.analysis_complete = False
    if 'journal_logo_base64' not in st.session_state:
        st.session_state.journal_logo_base64 = None
    if 'app_logo_base64' not in st.session_state:
        st.session_state.app_logo_base64 = None
    if 'language' not in st.session_state:
        st.session_state.language = 'en'
    if 'journal_results' not in st.session_state:
        st.session_state.journal_results = {}
    if 'html_report' not in st.session_state:
        st.session_state.html_report = None
    if 'journal_name' not in st.session_state:
        st.session_state.journal_name = ''
    
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
        
        st.markdown(f"## {t('analysis_params')}")
        
        global USE_CACHE
        use_cache = st.checkbox(t('use_cache'), value=USE_CACHE)
        USE_CACHE = use_cache
        
        if st.button(t('clear_cache')):
            import shutil
            if os.path.exists('cache'):
                shutil.rmtree('cache')
                st.cache_data.clear()
                st.success(t('cache_cleared'))
        
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
    
    # Tabs
    tab1, tab2 = st.tabs([
        t('load_data'),
        t('reports')
    ])
    
    with tab1:
        st.markdown('<div class="custom-tab fade-in">', unsafe_allow_html=True)
        st.header(t('load_data'))
        
        # ISSN input
        issn = st.text_input(
            t('issn_input'),
            placeholder=t('issn_placeholder'),
            help=t('issn_help')
        )
        
        # Period input
        period = st.text_input(
            t('period_input'),
            placeholder=t('period_placeholder'),
            help=t('period_help')
        )
        
        # Workers slider
        max_workers = st.slider(
            t('workers_slider'),
            min_value=4,
            max_value=12,
            value=8,
            step=1,
            help=t('workers_help')
        )
        
        # Logo upload
        journal_logo_upload = st.file_uploader(
            t('upload_logo'),
            type=['png', 'jpg', 'jpeg', 'svg'],
            help=t('logo_help')
        )
        
        if st.button(t('analyze_button'), type="primary", use_container_width=True):
            if not issn.strip():
                st.error(t('no_issn'))
            elif not period.strip():
                st.error(t('no_period'))
            else:
                journal_logo_data = None
                if journal_logo_upload:
                    journal_logo_data = {
                        journal_logo_upload.name: {
                            'content': journal_logo_upload.read()
                        }
                    }
                
                run_journal_analysis(issn.strip(), period.strip(), max_workers, journal_logo_data)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        if st.session_state.analysis_complete and st.session_state.html_report:
            st.markdown(f"## {t('html_report')}")
            
            # Display journal info
            journal_name = st.session_state.get('journal_name', 'Unknown Journal')
            st.info(f"📄 **{journal_name}**")
            
            # Download button
            st.download_button(
                label=t('download_report_button'),
                data=st.session_state.html_report.encode('utf-8'),
                file_name=f"journal_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                mime="text/html",
                type="primary",
                use_container_width=True
            )
            
            st.markdown("---")
            st.markdown(f"### {t('report_preview')}")
            
            # Show report preview
            st.components.v1.html(
                st.session_state.html_report,
                height=800,
                scrolling=True,
                sandbox="allow-scripts allow-modals allow-same-origin"
            )
            
            st.info(t('download_hint'))
        else:
            st.info(t('no_data_reports'))

if __name__ == "__main__":
    main()
