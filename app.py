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
USE_CACHE = True  # Кэширование результатов
LOGO_PATH = None  # Путь к логотипу журнала (устанавливается через виджет)

# Лимиты для анализа
MAX_PUBLICATIONS_TO_ANALYZE = 1000  # Максимум статей для анализа
MIN_YEAR_FOR_TREND = 5  # Сколько лет для тренда

# Режим анализа источников данных
ANALYSIS_MODE = "journal_analysis"  # Режим анализа журнала

# Параметры для обнаружения временных разрывов
MIN_GAP_YEARS_FOR_WARNING = 10  # Минимальный разрыв в годах для предупреждения

# Параметры для параллельного сбора цитирований
MAX_WORKERS = 8  # Количество параллельных потоков
BASE_DELAY = 0.35  # Базовая задержка между запросами
MAX_RETRIES_PARALLEL = 4  # Количество попыток при ошибке для параллельных запросов
MAX_CITING_PER_PAPER = 300  # Максимум цитирующих DOI на статью

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
import random
from tqdm import tqdm

# ============================================
# СЛОВАРЬ ПЕРЕВОДОВ
# ============================================

LANG = {
    'en': {
        'app_title': 'Advanced Journal Analysis',
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
        'reports': '📄 Reports',
        'issn_label': 'ISSN',
        'period_label': 'Period',
        'period_hint': 'e.g., 2020-2023, 2020,2021,2022, or 2020',
        'threads_label': 'Parallel threads',
        'start_analysis': '🚀 START ANALYSIS',
        'upload_logo': 'Upload journal logo (optional)',
        'logo_help': 'Logo will be displayed in the report',
        'analysis_progress': 'Analysis progress',
        'no_data': 'No data available. Run analysis first.',
        'analysis_complete': '✅ Analysis complete!',
        'analysis_in_progress': 'Analysis in progress...',
        'stage_fetching_articles': 'Fetching journal articles...',
        'stage_collecting_citations': 'Collecting citing DOIs...',
        'stage_enriching_articles': 'Enriching journal articles...',
        'stage_enriching_citations': 'Enriching citing works...',
        'stage_generating_report': 'Generating report...',
        'fetching_articles': 'Fetching articles',
        'collecting_citations': 'Collecting citing DOIs',
        'enriching_articles': 'Enriching journal articles',
        'enriching_citations': 'Enriching citing works',
        'generating_report': 'Generating report',
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
        'international_collab_rate': 'International Collaboration Rate',
        'unique_citing_authors': 'Unique Citing Authors',
        'unique_citing_affiliations': 'Unique Citing Affiliations',
        'unique_citing_countries': 'Unique Citing Countries',
        'unique_citing_journals': 'Unique Citing Journals',
        'unique_citing_publishers': 'Unique Citing Publishers',
        'gold': 'Gold',
        'hybrid': 'Hybrid',
        'green': 'Green',
        'bronze': 'Bronze',
        'closed': 'Closed',
        'unknown': 'Unknown',
        'rank': 'Rank',
        'authors': 'Authors',
        'orcid': 'ORCID',
        'affiliations': 'Affiliations',
        'countries': 'Countries',
        'publications': 'Publications',
        'citations': 'Citations',
        'author_analysis': 'Author Analysis',
        'top_affiliations': 'Top Affiliations',
        'geographic_analysis': 'Geographic Analysis',
        'unique_countries_per_pub': 'Unique Countries per Publication',
        'authors_per_country': 'Authors per Country',
        'collaboration_patterns': 'Collaboration Patterns',
        'collaboration_couples': 'Collaboration Couples',
        'citation_dynamics': 'Citation Dynamics by Year',
        'cumulative_citations': 'Cumulative Citations',
        'citation_heatmap': 'Citation Network Heatmap',
        'most_cited_publications': 'Most Cited Publications',
        'citing_works_analysis': 'Citing Works Analysis',
        'top_citing_authors': 'Top Citing Authors',
        'top_citing_affiliations': 'Top Citing Affiliations',
        'top_citing_countries': 'Top Citing Countries',
        'top_citing_journals': 'Top Citing Journals',
        'top_citing_publishers': 'Top Citing Publishers',
        'topics_analysis': 'Topics Analysis',
        'topic_overview': 'Topic Overview',
        'top_topics': 'Top Topics',
        'top_subtopics': 'Top Subtopics',
        'top_fields': 'Top Fields',
        'top_domains': 'Top Domains',
        'top_concepts': 'Top Concepts',
        'detailed_citations': 'Detailed Citations',
        'all_publications': 'All Publications',
        'filter_by_year': 'Filter by Year',
        'filter_by_author': 'Filter by Author',
        'filter_by_affiliation': 'Filter by Affiliation',
        'filter_by_citations': 'Filter by Citations (min)',
        'filter_by_title': 'Filter by Title Word(s)',
        'search_publications': 'Search Publications',
        'show_citations': 'Show Citations',
        'citing_journal': 'Citing Journal',
        'citing_year': 'Citing Year',
        'citing_date': 'Citing Date',
        'citation_lag': 'Citation Lag',
        'single_country': 'Single-country',
        'international': 'International',
        'citations_per_year': 'Citations/Year',
        'title': 'Title',
        'year': 'Year',
        'doi': 'DOI',
        'journal': 'Journal',
        'publisher': 'Publisher',
        'analyzed_count': 'Analyzed Count',
        'citing_count': 'Citing Count',
        'analyzed_norm': 'Analyzed Norm',
        'citing_norm': 'Citing Norm',
        'total_norm': 'Total Norm',
        'first_year': 'First Year',
        'peak_year': 'Peak Year',
        'footer': '© Advanced Journal Analysis / Powered by OpenAlex',
        'journal_url': 'https://openalex.org',
        'download_report': 'Download HTML Report',
        'report_preview': 'Report Preview',
        'no_data_reports': 'No data available. Run analysis first.',
        'error_occurred': 'Error occurred',
        'data_not_found': 'Data not found. Check ISSN correctness.',
        'journal_analysis': 'Journal Analysis',
        'analysis_source': '📊 Data source: OpenAlex',
        'overview': 'Overview',
        'analyzed_articles': 'Analyzed Articles',
        'citation_analysis': 'Citation Analysis',
        'citing_works': 'Citing Works Analysis',
        'topics_analysis_section': 'Topics Analysis',
        'detailed_citations_section': 'Detailed Citations',
        'all_publications_section': 'All Publications',
        'publication_metrics': 'Publication Metrics',
        'oa_breakdown': 'Open Access Breakdown',
        'collaboration_stats': 'Collaboration Stats',
        'author_analysis_section': 'Author Analysis',
        'top_affiliations_section': 'Top Affiliations',
        'geographic_analysis_section': 'Geographic Analysis',
        'citation_dynamics_section': 'Citation Dynamics by Year',
        'cumulative_citations_section': 'Cumulative Citations',
        'citation_heatmap_section': 'Citation Network Heatmap',
        'most_cited_publications_section': 'Most Cited Publications',
        'top_citing_authors_section': 'Top Citing Authors',
        'top_citing_affiliations_section': 'Top Citing Affiliations',
        'top_citing_countries_section': 'Top Citing Countries',
        'top_citing_journals_section': 'Top Citing Journals',
        'top_citing_publishers_section': 'Top Citing Publishers',
        'topic_overview_section': 'Topic Overview',
        'top_topics_section': 'Top Topics',
        'top_subtopics_section': 'Top Subtopics',
        'top_fields_section': 'Top Fields',
        'top_domains_section': 'Top Domains',
        'top_concepts_section': 'Top Concepts',
        'all_publications_table': 'All Publications Table',
        'first_citation_analysis': 'First Citation Analysis',
        'min': 'Min',
        'max': 'Max',
        'avg': 'Avg',
        'median': 'Median',
        'years': 'years',
        'citation_year': 'Citation Year',
        'publication_year': 'Publication Year',
        'count': 'Count',
        'citing_doi': 'Citing DOI',
        'citing_title': 'Citing Title',
        'citing_authors': 'Citing Authors',
        'citing_affiliations': 'Citing Affiliations',
        'citing_countries': 'Citing Countries',
        'citing_topics': 'Citing Topics',
        'analyzed_work': 'Analyzed Work',
        'total_citing_works': 'Total Citing Works',
    },
    'ru': {
        'app_title': 'Расширенный анализ журналов',
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
        'reports': '📄 Отчеты',
        'issn_label': 'ISSN',
        'period_label': 'Период',
        'period_hint': 'например, 2020-2023, 2020,2021,2022, или 2020',
        'threads_label': 'Параллельных потоков',
        'start_analysis': '🚀 НАЧАТЬ АНАЛИЗ',
        'upload_logo': 'Загрузить логотип журнала (опционально)',
        'logo_help': 'Логотип будет отображаться в отчете',
        'analysis_progress': 'Прогресс анализа',
        'no_data': 'Нет данных. Сначала выполните анализ.',
        'analysis_complete': '✅ Анализ завершен!',
        'analysis_in_progress': 'Анализ выполняется...',
        'stage_fetching_articles': 'Загрузка статей журнала...',
        'stage_collecting_citations': 'Сбор цитирующих DOI...',
        'stage_enriching_articles': 'Обогащение статей журнала...',
        'stage_enriching_citations': 'Обогащение цитирующих работ...',
        'stage_generating_report': 'Генерация отчета...',
        'fetching_articles': 'Загрузка статей',
        'collecting_citations': 'Сбор цитирующих DOI',
        'enriching_articles': 'Обогащение статей журнала',
        'enriching_citations': 'Обогащение цитирующих работ',
        'generating_report': 'Генерация отчета',
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
        'international_collab_rate': 'Доля международных коллабораций',
        'unique_citing_authors': 'Уникальных цитирующих авторов',
        'unique_citing_affiliations': 'Уникальных цитирующих аффилиаций',
        'unique_citing_countries': 'Уникальных цитирующих стран',
        'unique_citing_journals': 'Уникальных цитирующих журналов',
        'unique_citing_publishers': 'Уникальных цитирующих издателей',
        'gold': 'Золотой',
        'hybrid': 'Гибридный',
        'green': 'Зеленый',
        'bronze': 'Бронзовый',
        'closed': 'Закрытый',
        'unknown': 'Неизвестный',
        'rank': 'Место',
        'authors': 'Авторы',
        'orcid': 'ORCID',
        'affiliations': 'Аффилиации',
        'countries': 'Страны',
        'publications': 'Публикаций',
        'citations': 'Цитирований',
        'author_analysis': 'Анализ авторов',
        'top_affiliations': 'Топ аффилиаций',
        'geographic_analysis': 'Географический анализ',
        'unique_countries_per_pub': 'Уникальные страны на публикацию',
        'authors_per_country': 'Авторы по странам',
        'collaboration_patterns': 'Шаблоны коллабораций',
        'collaboration_couples': 'Пары стран-коллабораций',
        'citation_dynamics': 'Динамика цитирований по годам',
        'cumulative_citations': 'Накопленные цитирования',
        'citation_heatmap': 'Тепловая карта цитирований',
        'most_cited_publications': 'Самые цитируемые публикации',
        'citing_works_analysis': 'Анализ цитирующих работ',
        'top_citing_authors': 'Топ цитирующих авторов',
        'top_citing_affiliations': 'Топ цитирующих аффилиаций',
        'top_citing_countries': 'Топ цитирующих стран',
        'top_citing_journals': 'Топ цитирующих журналов',
        'top_citing_publishers': 'Топ цитирующих издателей',
        'topics_analysis': 'Анализ тем',
        'topic_overview': 'Обзор тем',
        'top_topics': 'Топ тем',
        'top_subtopics': 'Топ подтем',
        'top_fields': 'Топ полей',
        'top_domains': 'Топ доменов',
        'top_concepts': 'Топ концептов',
        'detailed_citations': 'Детальные цитирования',
        'all_publications': 'Все публикации',
        'filter_by_year': 'Фильтр по году',
        'filter_by_author': 'Фильтр по автору',
        'filter_by_affiliation': 'Фильтр по аффилиации',
        'filter_by_citations': 'Фильтр по цитированиям (мин)',
        'filter_by_title': 'Фильтр по словам в названии',
        'search_publications': 'Поиск публикаций',
        'show_citations': 'Показать цитирования',
        'citing_journal': 'Цитирующий журнал',
        'citing_year': 'Год цитирования',
        'citing_date': 'Дата цитирования',
        'citation_lag': 'Задержка цитирования',
        'single_country': 'Однострановые',
        'international': 'Международные',
        'citations_per_year': 'Цитирований/год',
        'title': 'Название',
        'year': 'Год',
        'doi': 'DOI',
        'journal': 'Журнал',
        'publisher': 'Издатель',
        'analyzed_count': 'Анализируемых',
        'citing_count': 'Цитирующих',
        'analyzed_norm': 'Норма анализируемых',
        'citing_norm': 'Норма цитирующих',
        'total_norm': 'Общая норма',
        'first_year': 'Первый год',
        'peak_year': 'Пиковый год',
        'footer': '© Расширенный анализ журналов / На основе OpenAlex',
        'journal_url': 'https://openalex.org',
        'download_report': 'Скачать HTML отчет',
        'report_preview': 'Предпросмотр отчета',
        'no_data_reports': 'Нет данных. Сначала выполните анализ.',
        'error_occurred': 'Произошла ошибка',
        'data_not_found': 'Данные не найдены. Проверьте правильность ISSN.',
        'journal_analysis': 'Анализ журнала',
        'analysis_source': '📊 Источник данных: OpenAlex',
        'overview': 'Обзор',
        'analyzed_articles': 'Анализируемые статьи',
        'citation_analysis': 'Анализ цитирований',
        'citing_works': 'Анализ цитирующих работ',
        'topics_analysis_section': 'Анализ тем',
        'detailed_citations_section': 'Детальные цитирования',
        'all_publications_section': 'Все публикации',
        'publication_metrics': 'Метрики публикаций',
        'oa_breakdown': 'Разбивка по открытому доступу',
        'collaboration_stats': 'Статистика коллабораций',
        'author_analysis_section': 'Анализ авторов',
        'top_affiliations_section': 'Топ аффилиаций',
        'geographic_analysis_section': 'Географический анализ',
        'citation_dynamics_section': 'Динамика цитирований по годам',
        'cumulative_citations_section': 'Накопленные цитирования',
        'citation_heatmap_section': 'Тепловая карта цитирований',
        'most_cited_publications_section': 'Самые цитируемые публикации',
        'top_citing_authors_section': 'Топ цитирующих авторов',
        'top_citing_affiliations_section': 'Топ цитирующих аффилиаций',
        'top_citing_countries_section': 'Топ цитирующих стран',
        'top_citing_journals_section': 'Топ цитирующих журналов',
        'top_citing_publishers_section': 'Топ цитирующих издателей',
        'topic_overview_section': 'Обзор тем',
        'top_topics_section': 'Топ тем',
        'top_subtopics_section': 'Топ подтем',
        'top_fields_section': 'Топ полей',
        'top_domains_section': 'Топ доменов',
        'top_concepts_section': 'Топ концептов',
        'all_publications_table': 'Таблица всех публикаций',
        'first_citation_analysis': 'Анализ первого цитирования',
        'min': 'Мин',
        'max': 'Макс',
        'avg': 'Среднее',
        'median': 'Медиана',
        'years': 'лет',
        'citation_year': 'Год цитирования',
        'publication_year': 'Год публикации',
        'count': 'Количество',
        'citing_doi': 'Цитирующий DOI',
        'citing_title': 'Название цитирующей работы',
        'citing_authors': 'Авторы цитирующей работы',
        'citing_affiliations': 'Аффилиации цитирующей работы',
        'citing_countries': 'Страны цитирующей работы',
        'citing_topics': 'Темы цитирующей работы',
        'analyzed_work': 'Анализируемая работа',
        'total_citing_works': 'Всего цитирующих работ',
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
# COLOR UTILITIES FOR DYNAMIC THEMES (из второго кода)
# ============================================

def hex_to_rgb(hex_color: str) -> tuple:
    """Convert hex color to RGB tuple"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb: tuple) -> str:
    """Convert RGB tuple to hex color"""
    return '#{:02x}{:02x}{:02x}'.format(int(rgb[0]), int(rgb[1]), int(rgb[2]))

def get_complementary_color(hex_color: str) -> str:
    """
    Generate complementary color by rotating hue by 180 degrees
    Returns a color that pairs well with the base color
    """
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

        .theme-info {{
            background: var(--hover-light);
            border-radius: 10px;
            padding: 12px;
            margin-top: 15px;
            font-size: 12px;
            text-align: center;
        }}
        
        .reviewer-card {{
            background: white;
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 16px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transition: transform 0.2s, box-shadow 0.2s;
            border-left: 4px solid var(--primary);
        }}
        
        .reviewer-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }}
        
        .reviewer-name {{
            font-size: 18px;
            font-weight: 600;
            color: var(--primary);
            margin-bottom: 8px;
        }}
        
        .reviewer-orcid {{
            font-family: monospace;
            font-size: 12px;
            margin-bottom: 8px;
        }}
        
        .reviewer-section {{
            margin-top: 12px;
            padding-top: 8px;
            border-top: 1px solid #e0e0e0;
        }}
        
        .reviewer-section-title {{
            font-weight: 600;
            font-size: 13px;
            margin-bottom: 8px;
            color: #555;
        }}
        
        .external-id-link {{
            display: inline-block;
            background: #f0f0f0;
            padding: 4px 10px;
            border-radius: 15px;
            font-size: 11px;
            margin: 3px;
            text-decoration: none;
            color: #333;
            transition: background 0.2s;
        }}
        
        .external-id-link:hover {{
            background: var(--primary);
            color: white;
        }}
        
        .reviewer-website {{
            display: inline-block;
            margin: 3px 6px 3px 0;
            font-size: 12px;
        }}
        
        .confidential-banner {{
            background: linear-gradient(135deg, #fff3cd 0%, #ffe69e 100%);
            border-left: 4px solid #dc3545;
            padding: 12px 20px;
            margin-bottom: 20px;
            border-radius: 8px;
            font-weight: 500;
            text-align: center;
        }}
        
        /* Author card styles for multiple authors */
        .author-card {{
            background: white;
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 25px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            border-left: 5px solid var(--primary);
            transition: transform 0.2s;
        }}
        
        .author-card:hover {{
            transform: translateX(5px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        }}
        
        .author-card.best {{
            border-left-color: #FFD700;
            background: linear-gradient(135deg, #fff9e6 0%, #ffffff 100%);
        }}
        
        .author-rank {{
            font-size: 20px;
            font-weight: bold;
            color: var(--primary);
            display: inline-block;
            margin-right: 10px;
        }}
        
        .author-name-main {{
            font-size: 22px;
            font-weight: 600;
            color: var(--primary);
            display: inline-block;
        }}
        
        .author-hindex {{
            font-size: 18px;
            color: #666;
            margin-left: 10px;
        }}
        
        .best-badge {{
            background: #FFD700;
            color: #333;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: bold;
            display: inline-block;
            margin-left: 15px;
        }}
        
        /* Color coding for author cards in reports */
        .author-section {{
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #e0e0e0;
        }}
        
        .author-section:last-child {{
            border-bottom: none;
        }}
        
        /* Source types table styles */
        .source-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            font-family: 'Times New Roman', serif;
        }}
        .source-table th {{
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
            color: white;
            padding: 12px;
            text-align: left;
        }}
        .source-table td {{
            padding: 10px;
            border-bottom: 1px solid #BDC3C7;
            vertical-align: top;
        }}
        .source-table tr:hover {{
            background-color: #f5f5f5;
        }}
        .source-example-item {{
            margin: 3px 0;
            font-size: 13px;
        }}
        .source-example-link {{
            color: #2980B9;
            text-decoration: none;
            font-size: 12px;
        }}
        .source-example-link:hover {{
            text-decoration: underline;
        }}
        .source-badge {{
            display: inline-block;
            padding: 2px 10px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 600;
            margin-left: 5px;
        }}
        .source-badge-doi {{
            background: #d4edda;
            color: #155724;
        }}
        .source-badge-nodoi {{
            background: #f8d7da;
            color: #721c24;
        }}
        
        /* Co-author card styles */
        .coauthor-card {{
            background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
            border-radius: 12px;
            padding: 16px 20px;
            margin-bottom: 12px;
            border: 1px solid #e0e0e0;
            border-left: 4px solid var(--primary);
            transition: transform 0.2s, box-shadow 0.2s;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }}
        
        .coauthor-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(0,0,0,0.1);
            border-color: var(--primary);
        }}
        
        .coauthor-name {{
            font-size: 16px;
            font-weight: 600;
            color: var(--primary);
            margin-bottom: 6px;
        }}
        
        .coauthor-joint {{
            font-size: 13px;
            color: #666;
            margin-bottom: 8px;
        }}
        
        .coauthor-profiles {{
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            margin-top: 8px;
        }}
        
        .coauthor-profile-link {{
            display: inline-flex;
            align-items: center;
            gap: 4px;
            padding: 3px 10px;
            border-radius: 15px;
            font-size: 11px;
            font-weight: 500;
            text-decoration: none;
            transition: all 0.2s;
            background: #f0f0f0;
            color: #333;
        }}
        
        .coauthor-profile-link:hover {{
            transform: translateY(-1px);
            box-shadow: 0 2px 8px rgba(0,0,0,0.15);
        }}
        
        .coauthor-profile-link.orcid {{
            background: #a6ce39;
            color: #1a1a1a;
        }}
        
        .coauthor-profile-link.orcid:hover {{
            background: #8cb82e;
        }}
        
        .coauthor-profile-link.scopus {{
            background: #e97132;
            color: white;
        }}
        
        .coauthor-profile-link.scopus:hover {{
            background: #d45f24;
        }}
        
        .coauthor-profile-link.researcherid {{
            background: #005a9c;
            color: white;
        }}
        
        .coauthor-profile-link.researcherid:hover {{
            background: #004a82;
        }}
        
        .coauthor-profile-link.website {{
            background: #6c757d;
            color: white;
        }}
        
        .coauthor-profile-link.website:hover {{
            background: #5a6268;
        }}
        
        .coauthor-profile-link.other {{
            background: #17a2b8;
            color: white;
        }}
        
        .coauthor-profile-link.other:hover {{
            background: #138496;
        }}
        
        .coauthor-no-orcid {{
            font-size: 12px;
            color: #999;
            font-style: italic;
        }}
        
        /* Journal analysis specific styles */
        .journal-metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
            gap: 12px;
            margin: 15px 0;
        }}
        .journal-metric-card {{
            background: #f8f9fa;
            padding: 14px;
            border-radius: 10px;
            border-left: 4px solid var(--primary);
            text-align: center;
            transition: transform 0.3s;
        }}
        .journal-metric-card:hover {{
            transform: translateY(-3px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }}
        .journal-metric-value {{
            font-size: 26px;
            font-weight: bold;
            color: #2C3E50;
            font-family: 'Times New Roman', serif;
        }}
        .journal-metric-label {{
            font-size: 11px;
            color: #7F8C8D;
            margin-top: 4px;
            font-family: 'Times New Roman', serif;
        }}
        .oa-progress-container {{
            margin: 15px 0;
        }}
        .oa-progress-item {{
            display: flex;
            align-items: center;
            gap: 12px;
            margin: 6px 0;
        }}
        .oa-progress-label {{
            min-width: 80px;
            font-size: 13px;
            font-weight: 500;
        }}
        .oa-progress-track {{
            flex: 1;
            height: 22px;
            background: #f0f0f0;
            border-radius: 12px;
            overflow: hidden;
            position: relative;
        }}
        .oa-progress-fill {{
            height: 100%;
            border-radius: 12px;
            transition: width 0.8s ease;
            display: flex;
            align-items: center;
            justify-content: flex-end;
            padding-right: 8px;
            font-size: 11px;
            font-weight: 600;
            color: white;
            text-shadow: 0 1px 2px rgba(0,0,0,0.3);
        }}
        .oa-progress-percent {{
            min-width: 50px;
            font-size: 13px;
            font-weight: 500;
            color: #555;
        }}
        .heatmap-grid {{
            display: grid;
            gap: 2px;
            margin: 15px 0;
            overflow-x: auto;
        }}
        .heatmap-row {{
            display: grid;
            gap: 2px;
            align-items: center;
        }}
        .heatmap-header {{
            font-weight: 600;
            padding: 8px 12px;
            background: #f0f0f0;
            text-align: center;
            font-size: 13px;
        }}
        .heatmap-row-label {{
            font-weight: 500;
            padding: 8px 12px;
            background: #f8f9fa;
            text-align: center;
            font-size: 13px;
        }}
        .heatmap-cell {{
            padding: 8px 12px;
            text-align: center;
            border-radius: 4px;
            font-size: 13px;
            font-weight: 500;
            transition: transform 0.2s;
        }}
        .heatmap-cell:hover {{
            transform: scale(1.05);
            z-index: 10;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        }}
        .heatmap-cell-empty {{
            background: #f5f5f5;
            color: #ccc;
        }}
        .collapser {{
            cursor: pointer;
            padding: 12px 16px;
            margin: 8px 0;
            background: #f8f9fa;
            border-radius: 8px;
            border-left: 4px solid var(--primary);
            transition: background 0.3s, transform 0.2s;
            user-select: none;
        }}
        .collapser:hover {{
            background: #e9ecef;
            transform: translateX(4px);
        }}
        .collapser .citation-count {{
            background: var(--primary);
            color: white;
            padding: 2px 12px;
            border-radius: 12px;
            font-size: 12px;
            margin-left: 10px;
        }}
        .citation-detail {{
            padding: 12px 20px;
            margin: 4px 0 4px 20px;
            background: white;
            border-radius: 6px;
            border: 1px solid #e0e0e0;
            border-left: 3px solid var(--secondary);
        }}
        .citation-detail:hover {{
            background: #fafafa;
        }}
        .cite-meta {{
            font-size: 13px;
            color: #555;
            margin-top: 4px;
        }}
        .cite-meta strong {{
            color: #333;
        }}
        .filter-section {{
            background: #f8f9fa;
            padding: 16px 20px;
            border-radius: 10px;
            margin: 15px 0;
            border: 1px solid #e0e0e0;
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
            margin-bottom: 4px;
        }}
        .filter-row select, .filter-row input {{
            width: 100%;
            padding: 6px 10px;
            border: 1px solid #ccc;
            border-radius: 6px;
            font-size: 13px;
            background: white;
        }}
        .filter-row select:focus, .filter-row input:focus {{
            border-color: var(--primary);
            outline: none;
            box-shadow: 0 0 0 3px var(--hover-light);
        }}
        #visibleCount {{
            font-weight: 600;
            color: var(--primary);
            font-size: 14px;
        }}
        .word-wrap {{
            word-wrap: break-word;
            max-width: 300px;
        }}
        .collab-couples-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 8px;
            margin: 10px 0;
        }}
        .collab-couple-item {{
            background: #f8f9fa;
            padding: 8px 14px;
            border-radius: 8px;
            border: 1px solid #e0e0e0;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 14px;
        }}
        .collab-couple-item .badge {{
            background: var(--primary);
            color: white;
            padding: 2px 12px;
            border-radius: 12px;
            font-size: 12px;
        }}
        .country-flag {{
            font-size: 18px;
            margin-right: 4px;
        }}
        .scrollable-table {{
            max-height: 600px;
            overflow-y: auto;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
        }}
        .scrollable-table table {{
            margin: 0;
        }}
        .scrollable-table thead {{
            position: sticky;
            top: 0;
            z-index: 10;
        }}
        .topic-card {{
            background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
            border-radius: 10px;
            padding: 14px 18px;
            margin: 6px 0;
            border-left: 4px solid var(--primary);
            transition: transform 0.2s;
        }}
        .topic-card:hover {{
            transform: translateX(4px);
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }}
        .topic-name {{
            font-weight: 600;
            font-size: 14px;
            color: var(--primary);
        }}
        .topic-stats {{
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            margin-top: 4px;
            font-size: 12px;
            color: #666;
        }}
        .topic-stats span {{
            background: #f0f0f0;
            padding: 2px 10px;
            border-radius: 12px;
        }}
        .topic-stats .highlight {{
            background: var(--primary);
            color: white;
        }}
        .sticky-header {{
            position: sticky;
            top: 0;
            z-index: 100;
            background: white;
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
    """Нормализует ISSN"""
    cleaned = re.sub(r'[^0-9Xx]', '', str(issn_str).strip())
    if len(cleaned) == 8:
        return f"{cleaned[:4]}-{cleaned[4:]}".upper()
    return cleaned.upper()

def smart_get(url: str, params: dict, retries: int = MAX_RETRIES_PARALLEL) -> Optional[dict]:
    """Выполняет GET запрос с повторными попытками при ошибке"""
    lock = Lock()
    
    for attempt in range(retries):
        try:
            with lock:
                time.sleep(random.uniform(0.1, BASE_DELAY))
            
            resp = requests.get(url, params=params, timeout=25)
            
            if resp.status_code == 429:
                wait = int(resp.headers.get("Retry-After", 2 ** attempt + 1))
                time.sleep(wait + random.uniform(0.5, 1.5))
                continue
                
            if resp.status_code == 200:
                return resp.json()
            
            time.sleep(1 * (2 ** attempt))
            
        except Exception as e:
            if SHOW_DEBUG_LOGS:
                print(f"⚠️ Попытка {attempt+1}/{retries} ошибка: {str(e)[:100]}")
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

def get_cache_path(issn: str, data_type: str) -> str:
    """Возвращает путь к файлу кэша"""
    issn_clean = normalize_issn(issn)
    if not os.path.exists('cache'):
        os.makedirs('cache')
    return f"cache/{issn_clean}_{data_type}.json"

def load_from_cache(issn: str, data_type: str) -> Optional[Dict]:
    """Загружает данные из кэша"""
    if not USE_CACHE:
        return None
    
    cache_path = get_cache_path(issn, data_type)
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

def save_to_cache(issn: str, data_type: str, data: Dict):
    """Сохраняет данные в кэш"""
    if not USE_CACHE:
        return
    
    cache_path = get_cache_path(issn, data_type)
    try:
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        if SHOW_DEBUG_LOGS:
            print(f"✅ Данные сохранены в кэш: {cache_path}")
    except Exception as e:
        if SHOW_DEBUG_LOGS:
            print(f"⚠️ Ошибка сохранения кэша: {e}")

# ============================================
# ФУНКЦИИ ДЛЯ РАБОТЫ С OPENALEX API
# ============================================

def get_articles_by_journal(issn: str, period, progress_callback=None) -> List[Dict]:
    """
    Получает все статьи журнала за указанный период через OpenAlex API.
    
    Args:
        issn: ISSN журнала
        period: период (int, list, или tuple)
        progress_callback: функция для обновления прогресса
    
    Returns:
        List[Dict]: список статей
    """
    normalized = normalize_issn(issn)
    if SHOW_DEBUG_LOGS:
        print(f"🔍 Запрос статей для журнала {normalized}")
    
    # Проверяем кэш
    cache_data = load_from_cache(normalized, "articles")
    if cache_data:
        return cache_data.get('articles', [])
    
    base_url = "https://api.openalex.org/works"
    
    # Формируем фильтр по году
    if isinstance(period, list):
        year_filter = "|".join(f"publication_year:{y}" for y in period)
    elif isinstance(period, tuple):
        year_filter = f"publication_year:{period[0]}-{period[1]}"
    else:
        year_filter = f"publication_year:{period}"
    
    articles = []
    cursor = "*"
    page_count = 0
    
    while True:
        page_count += 1
        
        data = smart_get(base_url, {
            "filter": f"primary_location.source.issn:{normalized},{year_filter}",
            "per_page": 200,
            "select": "id,doi,publication_year,publication_date,cited_by_count,open_access",
            "cursor": cursor
        })
        
        if not data or not data.get("results"):
            break
        
        for w in data["results"]:
            doi = w.get("doi", "")
            if doi:
                doi = doi.replace("https://doi.org/", "")
            
            oa = w.get("open_access", {})
            
            articles.append({
                "id": w.get("id", ""),
                "doi": doi or "N/A",
                "publication_year": w.get("publication_year"),
                "publication_date": w.get("publication_date"),
                "cited_by_count": w.get("cited_by_count", 0),
                "is_oa": oa.get("is_oa", False),
                "oa_status": oa.get("oa_status", "unknown"),
                "openalex_id": w.get("id", "").replace("https://openalex.org/", "")
            })
        
        if progress_callback:
            progress_callback(len(articles), len(articles))
        
        cursor = data.get("meta", {}).get("next_cursor")
        if not cursor:
            break
    
    if SHOW_DEBUG_LOGS:
        print(f"✅ Найдено статей: {len(articles)}")
    
    # Сохраняем в кэш
    save_to_cache(normalized, "articles", {"articles": articles})
    
    return articles

def get_citing_dois(oa_id: str) -> List[str]:
    """
    Получает список цитирующих DOI для статьи.
    
    Args:
        oa_id: OpenAlex ID статьи
    
    Returns:
        List[str]: список DOI
    """
    if not oa_id:
        return []
    
    citing = []
    cursor = "*"
    base_url = "https://api.openalex.org/works"
    
    for _ in range(8):  # ограничение пагинации
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
    
    return citing[:MAX_CITING_PER_PAPER]

def fetch_openalex_metadata(doi_list: List[str], batch_size: int = 50, progress_callback=None) -> List[Dict]:
    """
    Получает полные метаданные из OpenAlex для списка DOI.
    
    Args:
        doi_list: список DOI
        batch_size: размер батча
        progress_callback: функция для обновления прогресса
    
    Returns:
        List[Dict]: список метаданных
    """
    if not doi_list:
        return []
    
    all_metadata = []
    total = len(doi_list)
    
    for i in range(0, total, batch_size):
        batch = doi_list[i:i+batch_size]
        doi_query = '|'.join(batch[:50])
        
        params = {
            'filter': f'doi:{doi_query}',
            'per-page': len(batch)
        }
        
        url = "https://api.openalex.org/works"
        data = smart_get(url, params)
        
        if data and data.get('results'):
            for item in data['results']:
                parsed = parse_openalex_publication(item)
                if parsed:
                    all_metadata.append(parsed)
        
        if progress_callback:
            progress_callback(len(all_metadata), total)
        
        time.sleep(DELAY_BETWEEN_BATCHES)
    
    return all_metadata

def parse_openalex_publication(item: Dict) -> Dict:
    """Парсит публикацию из OpenAlex с расширенной информацией"""
    try:
        pub = {}
        
        pub['id'] = item.get('id', '')
        pub['doi'] = item.get('doi', '').replace('https://doi.org/', '')
        pub['title'] = item.get('title', 'No title')
        pub['publication_year'] = item.get('publication_year')
        pub['publication_date'] = item.get('publication_date')
        
        pub['type'] = item.get('type', 'unknown')
        pub['raw_type'] = item.get('raw_type', '')
        
        if item.get('primary_location'):
            source = item['primary_location'].get('source', {})
            pub['journal_name'] = source.get('display_name', 'Unknown')
            pub['publisher'] = source.get('host_organization_name') or source.get('publisher', 'Unknown')
            pub['issn'] = source.get('issn', [])
            pub['source_type'] = source.get('type', 'unknown')
        else:
            pub['journal_name'] = 'Unknown'
            pub['publisher'] = 'Unknown'
            pub['issn'] = []
            pub['source_type'] = 'unknown'
        
        oa = item.get('open_access', {})
        pub['is_oa'] = oa.get('is_oa', False)
        pub['open_access_status'] = oa.get('oa_status', 'closed')
        pub['oa_url'] = oa.get('oa_url', None)
        pub['any_repository_has_fulltext'] = oa.get('any_repository_has_fulltext', False)
        
        affiliations = []
        affiliation_countries = []
        institutions = []
        authors = []
        authors_with_orcids = []
        
        for auth in item.get('authorships', []):
            if auth.get('author'):
                author_name = auth['author'].get('display_name', '')
                author_orcid = auth['author'].get('orcid', '')
                if author_name:
                    authors.append(author_name)
                    if author_orcid:
                        authors_with_orcids.append({
                            'name': author_name,
                            'orcid': author_orcid.replace('https://orcid.org/', '') if author_orcid else None
                        })
            
            if auth.get('institutions'):
                for inst in auth['institutions']:
                    affil = inst.get('display_name', '')
                    if affil:
                        affiliations.append(affil)
                        country = extract_country_from_affiliation(affil)
                        if country:
                            affiliation_countries.append(country)
                        
                        institutions.append({
                            'id': inst.get('id', ''),
                            'display_name': inst.get('display_name', ''),
                            'country_code': inst.get('country_code', ''),
                            'ror': inst.get('ror', ''),
                            'type': inst.get('type', ''),
                            'lineage': inst.get('lineage', [])
                        })
        
        pub['authors'] = authors
        pub['authors_with_orcids'] = authors_with_orcids
        pub['author_count'] = len(authors)
        pub['affiliations'] = affiliations
        pub['affiliation_countries'] = affiliation_countries
        pub['institutions'] = institutions
        
        if affiliations:
            pub['country'] = extract_country_from_affiliation(affiliations[0])
        else:
            pub['country'] = 'Unknown'
        
        primary_topic = item.get('primary_topic', {})
        if primary_topic:
            pub['primary_topic'] = {
                'display_name': primary_topic.get('display_name', ''),
                'subfield': primary_topic.get('subfield', {}).get('display_name', ''),
                'field': primary_topic.get('field', {}).get('display_name', ''),
                'domain': primary_topic.get('domain', {}).get('display_name', ''),
                'score': primary_topic.get('score', 0)
            }
        else:
            pub['primary_topic'] = None
        
        topics_list = item.get('topics', [])
        pub['topics'] = [
            {
                'display_name': t.get('display_name', ''),
                'subfield': t.get('subfield', {}).get('display_name', ''),
                'field': t.get('field', {}).get('display_name', ''),
                'domain': t.get('domain', {}).get('display_name', ''),
                'score': t.get('score', 0)
            }
            for t in topics_list
        ]
        
        keywords = item.get('keywords', [])
        pub['keywords'] = [k.get('display_name', '') for k in keywords if k.get('display_name')]
        
        concepts = []
        concept_levels = {}
        fields = []
        domains = []
        topics_old = []
        subtopics = []
        
        for concept in item.get('concepts', []):
            concept_name = concept.get('display_name', '')
            concept_level = concept.get('level', 0)
            concept_score = concept.get('score', 0)
            
            if concept_name:
                concepts.append(concept_name)
                concept_levels[concept_name] = {
                    'level': concept_level,
                    'score': concept_score
                }
            
            if concept_level >= 3:
                domains.append(concept_name)
            elif concept_level == 2:
                fields.append(concept_name)
            elif concept_level == 1:
                topics_old.append(concept_name)
            elif concept_level == 0:
                subtopics.append(concept_name)
        
        pub['concepts'] = concepts[:15]
        pub['concept_levels'] = concept_levels
        pub['fields'] = fields[:10]
        pub['domains'] = domains[:5]
        pub['topics_old'] = topics_old[:15]
        pub['subtopics'] = subtopics[:20]
        
        pub['cited_by_count'] = item.get('cited_by_count', 0)
        pub['cited_by_percentile'] = item.get('cited_by_percentile', {})
        
        pub['is_retracted'] = item.get('is_retracted', False)
        pub['is_correction'] = item.get('is_correction', False)
        pub['is_paratext'] = item.get('is_paratext', False)
        
        if pub['is_retracted']:
            pub['retraction_info'] = item.get('retraction_info', {})
        
        pub['created_date'] = item.get('created_date')
        pub['updated_date'] = item.get('updated_date')
        
        return pub
        
    except Exception as e:
        if SHOW_DEBUG_LOGS:
            print(f"⚠️ Ошибка парсинга публикации: {e}")
        return None

def extract_country_from_affiliation(affiliation: str) -> str:
    """Извлекает страну из названия аффилиации"""
    countries = [
        'USA', 'UK', 'China', 'Germany', 'France', 'Japan', 'Russia', 'Italy', 
        'Canada', 'Australia', 'Spain', 'Brazil', 'India', 'Netherlands', 'Switzerland',
        'South Korea', 'Sweden', 'Belgium', 'Poland', 'Austria', 'Norway', 'Denmark',
        'Finland', 'Ireland', 'Portugal', 'Greece', 'Czech Republic', 'Hungary',
        'New Zealand', 'South Africa', 'Argentina', 'Mexico', 'Chile', 'Colombia',
        'United States', 'United Kingdom', 'England', 'Scotland', 'Wales'
    ]
    
    for country in countries:
        if country.lower() in affiliation.lower():
            return country
    return "Unknown"

# ============================================
# КЛАСС ДЛЯ АНАЛИЗА ЖУРНАЛА
# ============================================

class JournalAnalyzer:
    def __init__(self, issn: str, period, max_workers: int = MAX_WORKERS):
        self.issn = normalize_issn(issn)
        self.period = period
        self.max_workers = max_workers
        self.journal_articles = []
        self.citing_dois_map = {}
        self.enriched_articles = []
        self.enriched_citations = []
        self.report_data = {}
        self.cache_data = {}
        
        # Коллекции для агрегации
        self.all_authors = set()
        self.all_affiliations = set()
        self.all_countries = set()
        self.all_journals = set()
        self.all_publishers = set()
        self.all_topics = defaultdict(lambda: {'analyzed': 0, 'citing': 0})
        self.all_subtopics = defaultdict(lambda: {'analyzed': 0, 'citing': 0})
        self.all_fields = defaultdict(lambda: {'analyzed': 0, 'citing': 0})
        self.all_domains = defaultdict(lambda: {'analyzed': 0, 'citing': 0})
        self.all_concepts = defaultdict(lambda: {'analyzed': 0, 'citing': 0})
        
        # Детальные цитирования
        self.detailed_citations = {}
        
    def run_analysis(self, progress_callback=None) -> Dict:
        """Запускает полный анализ журнала"""
        if SHOW_DEBUG_LOGS:
            print(f"🚀 Запуск анализа для журнала {self.issn}")
        
        # Этап 1: Сбор статей журнала
        if progress_callback:
            progress_callback(0, 1, "stage_fetching_articles", 0, 0)
        
        self.journal_articles = get_articles_by_journal(
            self.issn, 
            self.period,
            lambda current, total: progress_callback(current, total, "stage_fetching_articles", current, total) if progress_callback else None
        )
        
        if not self.journal_articles:
            if SHOW_DEBUG_LOGS:
                print("❌ Статьи не найдены")
            return {}
        
        if SHOW_DEBUG_LOGS:
            print(f"✅ Найдено статей: {len(self.journal_articles)}")
        
        # Этап 2: Сбор цитирующих DOI (параллельно)
        if progress_callback:
            progress_callback(0, 1, "stage_collecting_citations", 0, 0)
        
        self._collect_citing_dois(progress_callback)
        
        # Этап 3: Обогащение статей журнала
        if progress_callback:
            progress_callback(0, 1, "stage_enriching_articles", 0, 0)
        
        self._enrich_articles(progress_callback)
        
        # Этап 4: Обогащение цитирующих работ
        if progress_callback:
            progress_callback(0, 1, "stage_enriching_citations", 0, 0)
        
        self._enrich_citations(progress_callback)
        
        # Этап 5: Анализ и подготовка данных для отчета
        if progress_callback:
            progress_callback(0, 1, "stage_generating_report", 0, 0)
        
        self._prepare_report_data()
        
        # Сохраняем результат в кэш
        save_to_cache(self.issn, "analysis", self.report_data)
        
        if SHOW_DEBUG_LOGS:
            print("✅ Анализ завершен!")
        
        return self.report_data
    
    def _collect_citing_dois(self, progress_callback=None):
        """Параллельный сбор цитирующих DOI"""
        if SHOW_DEBUG_LOGS:
            print(f"⚡ Параллельный сбор цитирующих DOI ({self.max_workers} потоков)...")
        
        self.citing_dois_map = {}
        futures = {}
        
        # Собираем статьи с цитированиями
        citing_tasks = []
        for article in self.journal_articles:
            if article.get('cited_by_count', 0) > 0 and article.get('doi') != "N/A":
                citing_tasks.append(article)
        
        if SHOW_DEBUG_LOGS:
            print(f"📊 Статей с цитированиями: {len(citing_tasks)}")
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            for article in citing_tasks:
                oa_id = article.get('openalex_id', '')
                if oa_id:
                    future = executor.submit(get_citing_dois, oa_id)
                    futures[future] = article.get('doi', '')
            
            total = len(futures)
            completed = 0
            
            for future in as_completed(futures):
                doi = futures[future]
                try:
                    self.citing_dois_map[doi] = future.result()
                except Exception as e:
                    if SHOW_DEBUG_LOGS:
                        print(f"⚠️ Ошибка сбора цитирований для {doi}: {e}")
                    self.citing_dois_map[doi] = []
                
                completed += 1
                if progress_callback:
                    progress_callback(completed, total, "stage_collecting_citations", completed, total)
        
        total_citing = sum(len(v) for v in self.citing_dois_map.values())
        if SHOW_DEBUG_LOGS:
            print(f"✅ Собрано цитирующих DOI: {total_citing}")
    
    def _enrich_articles(self, progress_callback=None):
        """Обогащение статей журнала метаданными"""
        if SHOW_DEBUG_LOGS:
            print("📊 Обогащение статей журнала...")
        
        dois_to_fetch = [a['doi'] for a in self.journal_articles if a['doi'] != "N/A"]
        
        if not dois_to_fetch:
            self.enriched_articles = self.journal_articles
            return
        
        # Проверяем кэш
        cache_data = load_from_cache(self.issn, "enriched_articles")
        if cache_data:
            self.enriched_articles = cache_data.get('articles', [])
            if SHOW_DEBUG_LOGS:
                print(f"✅ Загружено из кэша: {len(self.enriched_articles)} статей")
            return
        
        # Получаем метаданные
        all_metadata = fetch_openalex_metadata(
            dois_to_fetch,
            batch_size=BATCH_SIZE,
            progress_callback=lambda current, total: progress_callback(current, total, "stage_enriching_articles", current, total) if progress_callback else None
        )
        
        # Обогащаем статьи
        enriched_map = {item['doi']: item for item in all_metadata if item.get('doi')}
        
        self.enriched_articles = []
        for article in self.journal_articles:
            doi = article.get('doi')
            if doi != "N/A" and doi in enriched_map:
                enriched = enriched_map[doi].copy()
                # Добавляем поля из исходной статьи
                enriched['cited_by_count'] = article.get('cited_by_count', 0)
                enriched['is_oa'] = article.get('is_oa', False)
                enriched['oa_status'] = article.get('oa_status', 'unknown')
                self.enriched_articles.append(enriched)
            else:
                self.enriched_articles.append(article)
        
        # Сохраняем в кэш
        save_to_cache(self.issn, "enriched_articles", {"articles": self.enriched_articles})
        
        if SHOW_DEBUG_LOGS:
            print(f"✅ Обогащено статей: {len(self.enriched_articles)}")
    
    def _enrich_citations(self, progress_callback=None):
        """Обогащение цитирующих работ метаданными"""
        if SHOW_DEBUG_LOGS:
            print("📊 Обогащение цитирующих работ...")
        
        # Собираем все уникальные цитирующие DOI
        all_citing_dois = set()
        for doi, citing_list in self.citing_dois_map.items():
            all_citing_dois.update(citing_list)
        
        if not all_citing_dois:
            self.enriched_citations = []
            return
        
        if SHOW_DEBUG_LOGS:
            print(f"📊 Уникальных цитирующих DOI: {len(all_citing_dois)}")
        
        # Проверяем кэш
        cache_data = load_from_cache(self.issn, "enriched_citations")
        if cache_data:
            self.enriched_citations = cache_data.get('citations', [])
            if SHOW_DEBUG_LOGS:
                print(f"✅ Загружено из кэша: {len(self.enriched_citations)} цитирований")
            return
        
        # Получаем метаданные для цитирующих работ
        citing_dois_list = list(all_citing_dois)
        all_metadata = fetch_openalex_metadata(
            citing_dois_list,
            batch_size=BATCH_SIZE,
            progress_callback=lambda current, total: progress_callback(current, total, "stage_enriching_citations", current, total) if progress_callback else None
        )
        
        self.enriched_citations = all_metadata
        
        # Сохраняем в кэш
        save_to_cache(self.issn, "enriched_citations", {"citations": self.enriched_citations})
        
        if SHOW_DEBUG_LOGS:
            print(f"✅ Обогащено цитирований: {len(self.enriched_citations)}")
    
    def _prepare_report_data(self):
        """Подготовка данных для HTML отчета"""
        if SHOW_DEBUG_LOGS:
            print("📊 Подготовка данных для отчета...")
        
        # Базовая статистика
        articles = self.enriched_articles
        citations = self.enriched_citations
        
        # Словарь для быстрого доступа к цитирующим по DOI
        citing_map = {}
        for cite in citations:
            citing_map[cite.get('doi', '')] = cite
        
        # 1. Основные метрики
        total_publications = len(articles)
        total_citations = sum(a.get('cited_by_count', 0) for a in articles)
        
        # h-index, g-index, i10-index, i100-index
        citation_counts = [a.get('cited_by_count', 0) for a in articles]
        h_index = self._calculate_h_index(citation_counts)
        g_index = self._calculate_g_index(citation_counts)
        i10_index = sum(1 for c in citation_counts if c >= 10)
        i100_index = sum(1 for c in citation_counts if c >= 100)
        avg_citations = sum(citation_counts) / len(citation_counts) if citation_counts else 0
        
        # Open Access Breakdown
        oa_breakdown = {'gold': 0, 'hybrid': 0, 'green': 0, 'bronze': 0, 'closed': 0, 'unknown': 0}
        for a in articles:
            status = a.get('oa_status', 'unknown')
            if status in oa_breakdown:
                oa_breakdown[status] += 1
            else:
                oa_breakdown['unknown'] += 1
        
        # Активные годы
        years = [a.get('publication_year') for a in articles if a.get('publication_year')]
        active_years = len(set(years))
        
        # Уникальные авторы, аффилиации, страны
        all_authors = set()
        all_affiliations = set()
        all_countries = set()
        total_authors = 0
        total_affiliations = 0
        total_countries = 0
        international_collab_count = 0
        
        for a in articles:
            authors = a.get('authors', [])
            affiliations = a.get('affiliations', [])
            countries = a.get('affiliation_countries', [])
            
            all_authors.update(authors)
            all_affiliations.update(affiliations)
            
            # Извлекаем страны из аффилиаций
            country_codes = set()
            for aff in affiliations:
                country = extract_country_from_affiliation(aff)
                if country != 'Unknown':
                    country_codes.add(country)
            all_countries.update(country_codes)
            
            total_authors += len(authors)
            total_affiliations += len(affiliations)
            total_countries += len(country_codes)
            
            # Международные коллаборации
            if len(country_codes) >= 2:
                international_collab_count += 1
        
        avg_authors_per_paper = total_authors / len(articles) if articles else 0
        avg_affiliations_per_paper = total_affiliations / len(articles) if articles else 0
        avg_countries_per_paper = total_countries / len(articles) if articles else 0
        international_collab_rate = international_collab_count / len(articles) if articles else 0
        
        # 2. Анализ авторов (top 30)
        author_stats = defaultdict(lambda: {'publications': 0, 'citations': 0, 'orcid': '', 'affiliations': set(), 'countries': set()})
        for a in articles:
            authors = a.get('authors', [])
            authors_with_orcids = a.get('authors_with_orcids', [])
            citations_count = a.get('cited_by_count', 0)
            
            # Создаем словарь для быстрого поиска ORCID по имени
            orcid_map = {item['name']: item.get('orcid', '') for item in authors_with_orcids}
            
            for author in authors:
                author_stats[author]['publications'] += 1
                author_stats[author]['citations'] += citations_count
                if author in orcid_map and not author_stats[author]['orcid']:
                    author_stats[author]['orcid'] = orcid_map[author]
                
                # Добавляем аффилиации и страны
                affs = a.get('affiliations', [])
                for aff in affs:
                    author_stats[author]['affiliations'].add(aff)
                    country = extract_country_from_affiliation(aff)
                    if country != 'Unknown':
                        author_stats[author]['countries'].add(country)
        
        # Сортируем по количеству публикаций
        sorted_authors = sorted(
            author_stats.items(),
            key=lambda x: (x[1]['publications'], x[1]['citations']),
            reverse=True
        )[:30]
        
        author_analysis = []
        for rank, (name, stats) in enumerate(sorted_authors, 1):
            author_analysis.append({
                'rank': rank,
                'name': name,
                'orcid': stats['orcid'],
                'affiliations': ', '.join(list(stats['affiliations'])[:3]),
                'countries': ', '.join(list(stats['countries'])[:3]),
                'publications': stats['publications'],
                'citations': stats['citations']
            })
        
        # 3. Top Affiliations (top 30)
        aff_stats = defaultdict(int)
        for a in articles:
            for aff in a.get('affiliations', []):
                aff_stats[aff] += 1
        
        top_affiliations = sorted(aff_stats.items(), key=lambda x: x[1], reverse=True)[:30]
        top_affiliations = [{'affiliation': aff, 'count': count} for aff, count in top_affiliations]
        
        # 4. Geographic Analysis
        # 4.1 Unique Countries per Publication
        unique_countries_per_pub = defaultdict(int)
        for a in articles:
            countries = set()
            for aff in a.get('affiliations', []):
                country = extract_country_from_affiliation(aff)
                if country != 'Unknown':
                    countries.add(country)
            for country in countries:
                unique_countries_per_pub[country] += 1
        
        # 4.2 Authors per Country
        authors_per_country = defaultdict(int)
        for a in articles:
            for aff in a.get('affiliations', []):
                country = extract_country_from_affiliation(aff)
                if country != 'Unknown':
                    authors_per_country[country] += 1
        
        # 4.3 Collaboration Patterns
        single_country_papers = 0
        international_papers = 0
        for a in articles:
            countries = set()
            for aff in a.get('affiliations', []):
                country = extract_country_from_affiliation(aff)
                if country != 'Unknown':
                    countries.add(country)
            if len(countries) >= 2:
                international_papers += 1
            elif len(countries) == 1:
                single_country_papers += 1
        
        # 4.4 Collaboration Couples
        collaboration_couples = defaultdict(int)
        for a in articles:
            countries = set()
            for aff in a.get('affiliations', []):
                country = extract_country_from_affiliation(aff)
                if country != 'Unknown':
                    countries.add(country)
            if len(countries) >= 2:
                country_list = sorted(list(countries))
                for i in range(len(country_list)):
                    for j in range(i+1, len(country_list)):
                        pair = tuple(sorted([country_list[i], country_list[j]]))
                        collaboration_couples[pair] += 1
        
        # 5. Citation Analysis
        # 5.1 Citation Dynamics by Year
        citation_dynamics = defaultdict(lambda: defaultdict(int))
        first_citation_lags = []
        
        # Строим карту цитирований
        for article in articles:
            pub_year = article.get('publication_year')
            pub_date = article.get('publication_date')
            doi = article.get('doi', '')
            
            if not pub_year:
                continue
            
            citing_dois = self.citing_dois_map.get(doi, [])
            for citing_doi in citing_dois:
                citing_work = citing_map.get(citing_doi)
                if citing_work:
                    cite_year = citing_work.get('publication_year')
                    cite_date = citing_work.get('publication_date')
                    
                    if cite_year:
                        citation_dynamics[pub_year][cite_year] += 1
                        
                        # Первое цитирование
                        if cite_year and pub_year:
                            lag = cite_year - pub_year
                            if lag >= 0:
                                first_citation_lags.append(lag)
        
        # Преобразуем в список для отчета
        citation_dynamics_list = []
        for pub_year in sorted(citation_dynamics.keys()):
            for cite_year in sorted(citation_dynamics[pub_year].keys()):
                citation_dynamics_list.append({
                    'publication_year': pub_year,
                    'citation_year': cite_year,
                    'count': citation_dynamics[pub_year][cite_year]
                })
        
        # First citation analysis
        first_citation_stats = {}
        if first_citation_lags:
            first_citation_stats = {
                'min': min(first_citation_lags),
                'max': max(first_citation_lags),
                'avg': sum(first_citation_lags) / len(first_citation_lags),
                'median': sorted(first_citation_lags)[len(first_citation_lags)//2]
            }
        
        # 5.2 Cumulative Citations
        cumulative_citations = defaultdict(int)
        all_citation_years = set()
        for article in articles:
            pub_year = article.get('publication_year')
            if not pub_year:
                continue
            doi = article.get('doi', '')
            citing_dois = self.citing_dois_map.get(doi, [])
            for citing_doi in citing_dois:
                citing_work = citing_map.get(citing_doi)
                if citing_work:
                    cite_year = citing_work.get('publication_year')
                    if cite_year:
                        all_citation_years.add(cite_year)
        
        # Сортируем годы
        sorted_years = sorted(all_citation_years)
        cum_sum = 0
        cumulative_list = []
        for year in sorted_years:
            # Суммируем все цитирования за этот год
            year_total = 0
            for pub_year in citation_dynamics.keys():
                year_total += citation_dynamics[pub_year].get(year, 0)
            cum_sum += year_total
            cumulative_list.append({
                'year': year,
                'cumulative_count': cum_sum
            })
        
        # 5.3 Citation Network Heatmap
        heatmap_data = {}
        for pub_year in sorted(citation_dynamics.keys()):
            for cite_year in sorted(citation_dynamics[pub_year].keys()):
                heatmap_data[(pub_year, cite_year)] = citation_dynamics[pub_year][cite_year]
        
        # 5.4 Most Cited Publications
        sorted_by_citations = sorted(articles, key=lambda x: x.get('cited_by_count', 0), reverse=True)[:20]
        most_cited_publications = []
        for rank, pub in enumerate(sorted_by_citations, 1):
            authors_list = pub.get('authors', [])
            authors_str = ', '.join(authors_list[:3])
            if len(authors_list) > 3:
                authors_str += f' +{len(authors_list)-3} more'
            
            most_cited_publications.append({
                'rank': rank,
                'title': pub.get('title', 'No title'),
                'year': pub.get('publication_year', 'N/A'),
                'citations': pub.get('cited_by_count', 0),
                'citations_per_year': pub.get('cited_by_count', 0) / max(1, (2026 - (pub.get('publication_year') or 2026))),
                'authors': authors_str,
                'doi': pub.get('doi', '')
            })
        
        # 6. Citing Works Analysis
        citing_authors = set()
        citing_affiliations = set()
        citing_countries = set()
        citing_journals = set()
        citing_publishers = set()
        
        for cite in citations:
            citing_authors.update(cite.get('authors', []))
            citing_affiliations.update(cite.get('affiliations', []))
            
            for aff in cite.get('affiliations', []):
                country = extract_country_from_affiliation(aff)
                if country != 'Unknown':
                    citing_countries.add(country)
            
            journal = cite.get('journal_name')
            if journal and journal != 'Unknown':
                citing_journals.add(journal)
            
            publisher = cite.get('publisher')
            if publisher and publisher != 'Unknown':
                citing_publishers.add(publisher)
        
        # 6.1 Top Citing Authors
        citing_author_stats = defaultdict(int)
        for cite in citations:
            for author in cite.get('authors', []):
                citing_author_stats[author] += 1
        
        top_citing_authors = sorted(citing_author_stats.items(), key=lambda x: x[1], reverse=True)[:20]
        top_citing_authors = [{'name': name, 'count': count} for name, count in top_citing_authors]
        
        # 6.2 Top Citing Affiliations
        citing_aff_stats = defaultdict(int)
        for cite in citations:
            for aff in cite.get('affiliations', []):
                citing_aff_stats[aff] += 1
        
        top_citing_affiliations = sorted(citing_aff_stats.items(), key=lambda x: x[1], reverse=True)[:20]
        top_citing_affiliations = [{'affiliation': aff, 'count': count} for aff, count in top_citing_affiliations]
        
        # 6.3 Top Citing Countries
        citing_country_stats = defaultdict(int)
        for cite in citations:
            for aff in cite.get('affiliations', []):
                country = extract_country_from_affiliation(aff)
                if country != 'Unknown':
                    citing_country_stats[country] += 1
        
        top_citing_countries = sorted(citing_country_stats.items(), key=lambda x: x[1], reverse=True)[:20]
        top_citing_countries = [{'country': country, 'count': count} for country, count in top_citing_countries]
        
        # 6.4 Top Citing Journals
        citing_journal_stats = defaultdict(int)
        for cite in citations:
            journal = cite.get('journal_name')
            if journal and journal != 'Unknown':
                citing_journal_stats[journal] += 1
        
        top_citing_journals = sorted(citing_journal_stats.items(), key=lambda x: x[1], reverse=True)[:20]
        top_citing_journals = [{'journal': journal, 'count': count} for journal, count in top_citing_journals]
        
        # 6.5 Top Citing Publishers
        citing_publisher_stats = defaultdict(int)
        for cite in citations:
            publisher = cite.get('publisher')
            if publisher and publisher != 'Unknown':
                citing_publisher_stats[publisher] += 1
        
        top_citing_publishers = sorted(citing_publisher_stats.items(), key=lambda x: x[1], reverse=True)[:20]
        top_citing_publishers = [{'publisher': publisher, 'count': count} for publisher, count in top_citing_publishers]
        
        # 7. Topics Analysis
        # 7.1 Topic Overview
        topic_stats = defaultdict(lambda: {'analyzed': 0, 'citing': 0, 'first_year': 9999, 'last_year': 0})
        
        for article in articles:
            pub_year = article.get('publication_year', 0)
            for topic in article.get('topics', []):
                topic_name = topic.get('display_name', '')
                if topic_name:
                    topic_stats[topic_name]['analyzed'] += 1
                    if pub_year < topic_stats[topic_name]['first_year']:
                        topic_stats[topic_name]['first_year'] = pub_year
                    if pub_year > topic_stats[topic_name]['last_year']:
                        topic_stats[topic_name]['last_year'] = pub_year
        
        for cite in citations:
            for topic in cite.get('topics', []):
                topic_name = topic.get('display_name', '')
                if topic_name:
                    topic_stats[topic_name]['citing'] += 1
        
        # Нормализация
        total_analyzed = len(articles)
        total_citing = len(citations)
        
        topic_analysis_list = []
        for topic, stats in topic_stats.items():
            analyzed_norm = stats['analyzed'] / total_analyzed if total_analyzed > 0 else 0
            citing_norm = stats['citing'] / total_citing if total_citing > 0 else 0
            total_norm = (stats['analyzed'] + stats['citing']) / (total_analyzed + total_citing) if (total_analyzed + total_citing) > 0 else 0
            
            # Определяем пиковый год
            peak_year = stats['last_year'] if stats['last_year'] > 0 else 0
            
            topic_analysis_list.append({
                'topic': topic,
                'analyzed_count': stats['analyzed'],
                'citing_count': stats['citing'],
                'analyzed_norm': analyzed_norm,
                'citing_norm': citing_norm,
                'total_norm': total_norm,
                'first_year': stats['first_year'] if stats['first_year'] != 9999 else 0,
                'peak_year': peak_year
            })
        
        # Сортируем по total_norm
        topic_analysis_list = sorted(topic_analysis_list, key=lambda x: x['total_norm'], reverse=True)[:30]
        
        # 7.2 Top Topics, Subtopics, Fields, Domains, Concepts
        topic_count = defaultdict(int)
        subtopic_count = defaultdict(int)
        field_count = defaultdict(int)
        domain_count = defaultdict(int)
        concept_count = defaultdict(int)
        
        for article in articles:
            for topic in article.get('topics', []):
                topic_name = topic.get('display_name', '')
                if topic_name:
                    topic_count[topic_name] += 1
                
                subtopic = topic.get('subfield', '')
                if subtopic:
                    subtopic_count[subtopic] += 1
                
                field = topic.get('field', '')
                if field:
                    field_count[field] += 1
                
                domain = topic.get('domain', '')
                if domain:
                    domain_count[domain] += 1
            
            for concept in article.get('concepts', []):
                concept_count[concept] += 1
        
        for cite in citations:
            for topic in cite.get('topics', []):
                topic_name = topic.get('display_name', '')
                if topic_name:
                    topic_count[topic_name] += 1
                
                subtopic = topic.get('subfield', '')
                if subtopic:
                    subtopic_count[subtopic] += 1
                
                field = topic.get('field', '')
                if field:
                    field_count[field] += 1
                
                domain = topic.get('domain', '')
                if domain:
                    domain_count[domain] += 1
            
            for concept in cite.get('concepts', []):
                concept_count[concept] += 1
        
        top_topics = sorted(topic_count.items(), key=lambda x: x[1], reverse=True)[:20]
        top_subtopics = sorted(subtopic_count.items(), key=lambda x: x[1], reverse=True)[:20]
        top_fields = sorted(field_count.items(), key=lambda x: x[1], reverse=True)[:20]
        top_domains = sorted(domain_count.items(), key=lambda x: x[1], reverse=True)[:20]
        top_concepts = sorted(concept_count.items(), key=lambda x: x[1], reverse=True)[:20]
        
        # 8. Detailed Citations
        self.detailed_citations = {}
        for article in articles:
            pub_id = article.get('id', '')
            doi = article.get('doi', '')
            if not pub_id:
                continue
            
            citing_dois = self.citing_dois_map.get(doi, [])
            citing_list = []
            
            for citing_doi in citing_dois:
                citing_work = citing_map.get(citing_doi)
                if citing_work:
                    # Вычисляем задержку цитирования
                    pub_year = article.get('publication_year', 0)
                    cite_year = citing_work.get('publication_year', 0)
                    lag = cite_year - pub_year if pub_year and cite_year else None
                    
                    citing_list.append({
                        'citing_title': citing_work.get('title', 'No title'),
                        'citing_year': cite_year,
                        'citing_date': citing_work.get('publication_date', ''),
                        'citing_journal': citing_work.get('journal_name', 'Unknown'),
                        'citing_publisher': citing_work.get('publisher', 'Unknown'),
                        'citing_doi': citing_doi,
                        'citation_lag': lag if lag is not None else 0,
                        'citing_authors': citing_work.get('authors', []),
                        'citing_countries': [extract_country_from_affiliation(aff) for aff in citing_work.get('affiliations', []) if extract_country_from_affiliation(aff) != 'Unknown'],
                        'citing_topics': [t.get('display_name', '') for t in citing_work.get('topics', [])[:5]]
                    })
            
            if citing_list:
                self.detailed_citations[pub_id] = {
                    'title': article.get('title', 'No title'),
                    'year': article.get('publication_year', 'N/A'),
                    'doi': doi,
                    'total_citations': len(citing_list),
                    'citations': citing_list
                }
        
        # 9. All Publications
        all_publications = []
        for idx, article in enumerate(articles, 1):
            all_publications.append({
                'id': idx,
                'title': article.get('title', 'No title'),
                'year': article.get('publication_year', 'N/A'),
                'authors': ', '.join(article.get('authors', [])[:5]) + (' +' + str(len(article.get('authors', [])) - 5) if len(article.get('authors', [])) > 5 else ''),
                'affiliations': ', '.join(article.get('affiliations', [])[:3]) + (' +' + str(len(article.get('affiliations', [])) - 3) if len(article.get('affiliations', [])) > 3 else ''),
                'citations': article.get('cited_by_count', 0),
                'citations_per_year': article.get('cited_by_count', 0) / max(1, (2026 - (article.get('publication_year') or 2026))),
                'doi': article.get('doi', ''),
                'raw_authors': article.get('authors', []),
                'raw_affiliations': article.get('affiliations', [])
            })
        
        # Собираем все данные в report_data
        self.report_data = {
            'issn': self.issn,
            'period': self.period,
            'total_publications': total_publications,
            'total_citations': total_citations,
            'h_index': h_index,
            'g_index': g_index,
            'i10_index': i10_index,
            'i100_index': i100_index,
            'avg_citations': avg_citations,
            'oa_breakdown': oa_breakdown,
            'active_years': active_years,
            'unique_authors': len(all_authors),
            'unique_affiliations': len(all_affiliations),
            'unique_countries': len(all_countries),
            'avg_authors_per_paper': avg_authors_per_paper,
            'avg_affiliations_per_paper': avg_affiliations_per_paper,
            'avg_countries_per_paper': avg_countries_per_paper,
            'international_collab_rate': international_collab_rate,
            'author_analysis': author_analysis,
            'top_affiliations': top_affiliations,
            'unique_countries_per_pub': dict(sorted(unique_countries_per_pub.items(), key=lambda x: x[1], reverse=True)),
            'authors_per_country': dict(sorted(authors_per_country.items(), key=lambda x: x[1], reverse=True)),
            'single_country_papers': single_country_papers,
            'international_papers': international_papers,
            'collaboration_couples': dict(sorted(collaboration_couples.items(), key=lambda x: x[1], reverse=True)[:30]),
            'citation_dynamics': citation_dynamics_list,
            'first_citation_stats': first_citation_stats,
            'cumulative_citations': cumulative_list,
            'heatmap_data': heatmap_data,
            'most_cited_publications': most_cited_publications,
            'total_citing_works': len(citations),
            'unique_citing_authors': len(citing_authors),
            'unique_citing_affiliations': len(citing_affiliations),
            'unique_citing_countries': len(citing_countries),
            'unique_citing_journals': len(citing_journals),
            'unique_citing_publishers': len(citing_publishers),
            'top_citing_authors': top_citing_authors,
            'top_citing_affiliations': top_citing_affiliations,
            'top_citing_countries': top_citing_countries,
            'top_citing_journals': top_citing_journals,
            'top_citing_publishers': top_citing_publishers,
            'topic_analysis': topic_analysis_list,
            'top_topics': top_topics,
            'top_subtopics': top_subtopics,
            'top_fields': top_fields,
            'top_domains': top_domains,
            'top_concepts': top_concepts,
            'detailed_citations': self.detailed_citations,
            'all_publications': all_publications,
            'articles': articles,
            'citations': citations,
            'citing_dois_map': self.citing_dois_map
        }
        
        if SHOW_DEBUG_LOGS:
            print("✅ Данные для отчета подготовлены")
    
    def _calculate_h_index(self, citations: List[int]) -> int:
        """Расчет h-index"""
        citations_sorted = sorted([c for c in citations if c > 0], reverse=True)
        h = 0
        for i, c in enumerate(citations_sorted, 1):
            if c >= i:
                h = i
            else:
                break
        return h
    
    def _calculate_g_index(self, citations: List[int]) -> int:
        """Расчет g-index"""
        citations_sorted = sorted(citations, reverse=True)
        total = 0
        g = 0
        for i, c in enumerate(citations_sorted, 1):
            total += c
            if total >= i * i:
                g = i
        return g

# ============================================
# ФУНКЦИИ ДЛЯ ГЕНЕРАЦИИ HTML ОТЧЕТА
# ============================================

def generate_html_report(report_data: Dict, logo_base64: Optional[str] = None, app_logo_base64: Optional[str] = None, theme_colors: Optional[Dict] = None, lang: str = 'en') -> str:
    """Генерирует HTML отчет для анализа журнала"""
    
    if theme_colors is None:
        theme_colors = {
            'primary': '#667eea',
            'secondary': '#f39c12'
        }
    
    primary = theme_colors.get('primary', '#667eea')
    secondary = theme_colors.get('secondary', '#f39c12')
    
    def t(key: str, **kwargs) -> str:
        return translate(key, lang, **kwargs)
    
    # Получаем данные из отчета
    total_pubs = report_data.get('total_publications', 0)
    total_citations = report_data.get('total_citations', 0)
    h_index = report_data.get('h_index', 0)
    g_index = report_data.get('g_index', 0)
    i10_index = report_data.get('i10_index', 0)
    i100_index = report_data.get('i100_index', 0)
    avg_citations = report_data.get('avg_citations', 0)
    oa_breakdown = report_data.get('oa_breakdown', {})
    active_years = report_data.get('active_years', 0)
    unique_authors = report_data.get('unique_authors', 0)
    unique_affiliations = report_data.get('unique_affiliations', 0)
    unique_countries = report_data.get('unique_countries', 0)
    avg_authors_per_paper = report_data.get('avg_authors_per_paper', 0)
    avg_affiliations_per_paper = report_data.get('avg_affiliations_per_paper', 0)
    avg_countries_per_paper = report_data.get('avg_countries_per_paper', 0)
    international_collab_rate = report_data.get('international_collab_rate', 0)
    
    total_citing_works = report_data.get('total_citing_works', 0)
    unique_citing_authors = report_data.get('unique_citing_authors', 0)
    unique_citing_affiliations = report_data.get('unique_citing_affiliations', 0)
    unique_citing_countries = report_data.get('unique_citing_countries', 0)
    unique_citing_journals = report_data.get('unique_citing_journals', 0)
    unique_citing_publishers = report_data.get('unique_citing_publishers', 0)
    
    author_analysis = report_data.get('author_analysis', [])
    top_affiliations = report_data.get('top_affiliations', [])
    unique_countries_per_pub = report_data.get('unique_countries_per_pub', {})
    authors_per_country = report_data.get('authors_per_country', {})
    single_country_papers = report_data.get('single_country_papers', 0)
    international_papers = report_data.get('international_papers', 0)
    collaboration_couples = report_data.get('collaboration_couples', {})
    citation_dynamics = report_data.get('citation_dynamics', [])
    first_citation_stats = report_data.get('first_citation_stats', {})
    cumulative_citations = report_data.get('cumulative_citations', [])
    heatmap_data = report_data.get('heatmap_data', {})
    most_cited_publications = report_data.get('most_cited_publications', [])
    top_citing_authors = report_data.get('top_citing_authors', [])
    top_citing_affiliations = report_data.get('top_citing_affiliations', [])
    top_citing_countries = report_data.get('top_citing_countries', [])
    top_citing_journals = report_data.get('top_citing_journals', [])
    top_citing_publishers = report_data.get('top_citing_publishers', [])
    topic_analysis = report_data.get('topic_analysis', [])
    top_topics = report_data.get('top_topics', [])
    top_subtopics = report_data.get('top_subtopics', [])
    top_fields = report_data.get('top_fields', [])
    top_domains = report_data.get('top_domains', [])
    top_concepts = report_data.get('top_concepts', [])
    detailed_citations = report_data.get('detailed_citations', {})
    all_publications = report_data.get('all_publications', [])
    
    # Цвета для OA
    oa_colors = {
        'gold': '#2ECC71',
        'hybrid': '#F1C40F',
        'green': '#3498DB',
        'bronze': '#E67E22',
        'closed': '#95A5A6',
        'unknown': '#BDC3C7'
    }
    
    oa_labels = {
        'gold': t('gold'),
        'hybrid': t('hybrid'),
        'green': t('green'),
        'bronze': t('bronze'),
        'closed': t('closed'),
        'unknown': t('unknown')
    }
    
    total_oa = sum(oa_breakdown.values()) if oa_breakdown else 1
    
    # Генерируем OA прогресс-бары
    oa_bars_html = ""
    for status in ['gold', 'hybrid', 'green', 'bronze', 'closed', 'unknown']:
        count = oa_breakdown.get(status, 0)
        if count > 0:
            percent = (count / total_oa) * 100
            color = oa_colors.get(status, '#BDC3C7')
            label = oa_labels.get(status, status)
            oa_bars_html += f"""
            <div class="oa-progress-item">
                <span class="oa-progress-label">{label}</span>
                <div class="oa-progress-track">
                    <div class="oa-progress-fill" style="width: {percent}%; background: {color};">{count}</div>
                </div>
                <span class="oa-progress-percent">{percent:.1f}%</span>
            </div>
            """
    
    # Генерируем таблицу Author Analysis
    author_table_html = ""
    if author_analysis:
        author_table_html = """
        <div class="scrollable-table">
            <table>
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Author</th>
                        <th>ORCID</th>
                        <th>Affiliations</th>
                        <th>Countries</th>
                        <th>Publications</th>
                        <th>Citations</th>
                    </tr>
                </thead>
                <tbody>
        """
        for author in author_analysis:
            author_table_html += f"""
            <tr>
                <td>{author['rank']}</td>
                <td>{html.escape(author['name'])}</td>
                <td>{f'<a href="https://orcid.org/{author["orcid"]}" target="_blank">{author["orcid"]}</a>' if author['orcid'] else '—'}</td>
                <td>{html.escape(author['affiliations'])}</td>
                <td>{html.escape(author['countries'])}</td>
                <td>{author['publications']}</td>
                <td>{author['citations']}</td>
            </tr>
            """
        author_table_html += """
                </tbody>
            </table>
        </div>
        """
    
    # Генерируем таблицу Top Affiliations
    aff_table_html = ""
    if top_affiliations:
        aff_table_html = """
        <div class="scrollable-table">
            <table>
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Affiliation</th>
                        <th>Publications</th>
                    </tr>
                </thead>
                <tbody>
        """
        for idx, aff in enumerate(top_affiliations[:30], 1):
            aff_table_html += f"""
            <tr>
                <td>{idx}</td>
                <td>{html.escape(aff['affiliation'])}</td>
                <td>{aff['count']}</td>
            </tr>
            """
        aff_table_html += """
                </tbody>
            </table>
        </div>
        """
    
    # Генерируем Unique Countries per Publication
    countries_pub_html = ""
    if unique_countries_per_pub:
        countries_pub_html = """
        <div class="scrollable-table">
            <table>
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Country</th>
                        <th>Publications</th>
                    </tr>
                </thead>
                <tbody>
        """
        for idx, (country, count) in enumerate(sorted(unique_countries_per_pub.items(), key=lambda x: x[1], reverse=True)[:30], 1):
            countries_pub_html += f"""
            <tr>
                <td>{idx}</td>
                <td>{html.escape(country)}</td>
                <td>{count}</td>
            </tr>
            """
        countries_pub_html += """
                </tbody>
            </table>
        </div>
        """
    
    # Генерируем Authors per Country
    authors_country_html = ""
    if authors_per_country:
        authors_country_html = """
        <div class="scrollable-table">
            <table>
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Country</th>
                        <th>Authors</th>
                    </tr>
                </thead>
                <tbody>
        """
        for idx, (country, count) in enumerate(sorted(authors_per_country.items(), key=lambda x: x[1], reverse=True)[:30], 1):
            authors_country_html += f"""
            <tr>
                <td>{idx}</td>
                <td>{html.escape(country)}</td>
                <td>{count}</td>
            </tr>
            """
        authors_country_html += """
                </tbody>
            </table>
        </div>
        """
    
    # Генерируем Collaboration Couples
    collab_couples_html = ""
    if collaboration_couples:
        collab_couples_html = '<div class="collab-couples-grid">'
        for (country1, country2), count in list(collaboration_couples.items())[:30]:
            collab_couples_html += f"""
            <div class="collab-couple-item">
                <span>{html.escape(country1)} — {html.escape(country2)}</span>
                <span class="badge">{count}</span>
            </div>
            """
        collab_couples_html += '</div>'
    
    # Генерируем Citation Dynamics таблицу
    citation_dynamics_html = ""
    if citation_dynamics:
        citation_dynamics_html = """
        <div class="scrollable-table">
            <table>
                <thead>
                    <tr>
                        <th>Publication Year</th>
                        <th>Citation Year</th>
                        <th>Citations Count</th>
                    </tr>
                </thead>
                <tbody>
        """
        # Группируем по году публикации
        dynamics_by_pub = defaultdict(list)
        for item in citation_dynamics:
            dynamics_by_pub[item['publication_year']].append(item)
        
        for pub_year in sorted(dynamics_by_pub.keys()):
            for item in sorted(dynamics_by_pub[pub_year], key=lambda x: x['citation_year']):
                citation_dynamics_html += f"""
                <tr>
                    <td>{item['publication_year']}</td>
                    <td>{item['citation_year']}</td>
                    <td>{item['count']}</td>
                </tr>
                """
        citation_dynamics_html += """
                </tbody>
            </table>
        </div>
        """
    
    # Генерируем Cumulative Citations таблицу
    cumulative_html = ""
    if cumulative_citations:
        cumulative_html = """
        <div class="scrollable-table">
            <table>
                <thead>
                    <tr>
                        <th>Year</th>
                        <th>Cumulative Citations</th>
                    </tr>
                </thead>
                <tbody>
        """
        for item in cumulative_citations:
            cumulative_html += f"""
            <tr>
                <td>{item['year']}</td>
                <td>{item['cumulative_count']}</td>
            </tr>
            """
        cumulative_html += """
                </tbody>
            </table>
        </div>
        """
    
    # Генерируем Heatmap
    heatmap_html = ""
    if heatmap_data:
        # Определяем все годы
        pub_years = sorted(set(k[0] for k in heatmap_data.keys()))
        cite_years = sorted(set(k[1] for k in heatmap_data.keys()))
        
        if pub_years and cite_years:
            max_val = max(heatmap_data.values()) if heatmap_data else 1
            
            # Строим сетку тепловой карты
            heatmap_html = '<div class="heatmap-grid" style="grid-template-columns: 100px ' + ' '.join(['80px'] * len(cite_years)) + ';">'
            
            # Заголовки
            heatmap_html += '<div class="heatmap-header"></div>'
            for cy in cite_years:
                heatmap_html += f'<div class="heatmap-header">{cy}</div>'
            
            # Строки
            for py in pub_years:
                heatmap_html += f'<div class="heatmap-row" style="grid-template-columns: 100px ' + ' '.join(['80px'] * len(cite_years)) + ';">'
                heatmap_html += f'<div class="heatmap-row-label">{py}</div>'
                for cy in cite_years:
                    val = heatmap_data.get((py, cy), 0)
                    if val > 0:
                        opacity = min(0.9, 0.1 + (val / max_val) * 0.8)
                        heatmap_html += f'<div class="heatmap-cell" style="background: {primary}; opacity: {opacity};">{val}</div>'
                    else:
                        if cy < py:
                            heatmap_html += '<div class="heatmap-cell heatmap-cell-empty">—</div>'
                        else:
                            heatmap_html += '<div class="heatmap-cell" style="background: #f5f5f5; color: #ccc;">0</div>'
                heatmap_html += '</div>'
            
            heatmap_html += '</div>'
    
    # Генерируем Most Cited Publications
    most_cited_html = ""
    if most_cited_publications:
        most_cited_html = """
        <div class="scrollable-table">
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
        """
        for pub in most_cited_publications[:20]:
            most_cited_html += f"""
            <tr>
                <td>{pub['rank']}</td>
                <td class="word-wrap">{html.escape(pub['title'][:100])}</td>
                <td>{pub['year']}</td>
                <td>{pub['citations']}</td>
                <td>{pub['citations_per_year']:.1f}</td>
                <td>{html.escape(pub['authors'])}</td>
                <td><a href="https://doi.org/{pub['doi']}" target="_blank" class="doi-link">{pub['doi'][:30]}...</a></td>
            </tr>
            """
        most_cited_html += """
                </tbody>
            </table>
        </div>
        """
    
    # Генерируем Top Citing Authors
    citing_authors_html = ""
    if top_citing_authors:
        citing_authors_html = """
        <div class="scrollable-table">
            <table>
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Author</th>
                        <th>Citations</th>
                    </tr>
                </thead>
                <tbody>
        """
        for idx, author in enumerate(top_citing_authors[:20], 1):
            citing_authors_html += f"""
            <tr>
                <td>{idx}</td>
                <td>{html.escape(author['name'])}</td>
                <td>{author['count']}</td>
            </tr>
            """
        citing_authors_html += """
                </tbody>
            </table>
        </div>
        """
    
    # Генерируем Top Citing Affiliations
    citing_aff_html = ""
    if top_citing_affiliations:
        citing_aff_html = """
        <div class="scrollable-table">
            <table>
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Affiliation</th>
                        <th>Citations</th>
                    </tr>
                </thead>
                <tbody>
        """
        for idx, aff in enumerate(top_citing_affiliations[:20], 1):
            citing_aff_html += f"""
            <tr>
                <td>{idx}</td>
                <td>{html.escape(aff['affiliation'])}</td>
                <td>{aff['count']}</td>
            </tr>
            """
        citing_aff_html += """
                </tbody>
            </table>
        </div>
        """
    
    # Генерируем Top Citing Countries
    citing_countries_html = ""
    if top_citing_countries:
        citing_countries_html = """
        <div class="scrollable-table">
            <table>
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Country</th>
                        <th>Citations</th>
                    </tr>
                </thead>
                <tbody>
        """
        for idx, country in enumerate(top_citing_countries[:20], 1):
            citing_countries_html += f"""
            <tr>
                <td>{idx}</td>
                <td>{html.escape(country['country'])}</td>
                <td>{country['count']}</td>
            </tr>
            """
        citing_countries_html += """
                </tbody>
            </table>
        </div>
        """
    
    # Генерируем Top Citing Journals
    citing_journals_html = ""
    if top_citing_journals:
        citing_journals_html = """
        <div class="scrollable-table">
            <table>
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Journal</th>
                        <th>Citations</th>
                    </tr>
                </thead>
                <tbody>
        """
        for idx, journal in enumerate(top_citing_journals[:20], 1):
            citing_journals_html += f"""
            <tr>
                <td>{idx}</td>
                <td>{html.escape(journal['journal'])}</td>
                <td>{journal['count']}</td>
            </tr>
            """
        citing_journals_html += """
                </tbody>
            </table>
        </div>
        """
    
    # Генерируем Top Citing Publishers
    citing_publishers_html = ""
    if top_citing_publishers:
        citing_publishers_html = """
        <div class="scrollable-table">
            <table>
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Publisher</th>
                        <th>Citations</th>
                    </tr>
                </thead>
                <tbody>
        """
        for idx, publisher in enumerate(top_citing_publishers[:20], 1):
            citing_publishers_html += f"""
            <tr>
                <td>{idx}</td>
                <td>{html.escape(publisher['publisher'])}</td>
                <td>{publisher['count']}</td>
            </tr>
            """
        citing_publishers_html += """
                </tbody>
            </table>
        </div>
        """
    
    # Генерируем Topic Analysis
    topic_analysis_html = ""
    if topic_analysis:
        topic_analysis_html = """
        <div class="scrollable-table">
            <table>
                <thead>
                    <tr>
                        <th>Topic</th>
                        <th>Analyzed Count</th>
                        <th>Citing Count</th>
                        <th>Analyzed Norm</th>
                        <th>Citing Norm</th>
                        <th>Total Norm</th>
                        <th>First Year</th>
                        <th>Peak Year</th>
                    </tr>
                </thead>
                <tbody>
        """
        for topic in topic_analysis[:30]:
            topic_analysis_html += f"""
            <tr>
                <td>{html.escape(topic['topic'])}</td>
                <td>{topic['analyzed_count']}</td>
                <td>{topic['citing_count']}</td>
                <td>{topic['analyzed_norm']:.3f}</td>
                <td>{topic['citing_norm']:.3f}</td>
                <td>{topic['total_norm']:.3f}</td>
                <td>{topic['first_year']}</td>
                <td>{topic['peak_year']}</td>
            </tr>
            """
        topic_analysis_html += """
                </tbody>
            </table>
        </div>
        """
    
    # Генерируем Top Topics, Subtopics, Fields, Domains, Concepts
    def generate_rank_list(items, title, max_items=20):
        if not items:
            return ""
        html_out = f"<h4>{title}</h4><div class='scrollable-table'><table><thead><tr><th>#</th><th>Name</th><th>Count</th></tr></thead><tbody>"
        for idx, (name, count) in enumerate(items[:max_items], 1):
            html_out += f"<tr><td>{idx}</td><td>{html.escape(name)}</td><td>{count}</td></tr>"
        html_out += "</tbody></table></div>"
        return html_out
    
    top_topics_html = generate_rank_list(top_topics, t('top_topics'))
    top_subtopics_html = generate_rank_list(top_subtopics, t('top_subtopics'))
    top_fields_html = generate_rank_list(top_fields, t('top_fields'))
    top_domains_html = generate_rank_list(top_domains, t('top_domains'))
    top_concepts_html = generate_rank_list(top_concepts, t('top_concepts'))
    
    # Генерируем Detailed Citations
    detailed_citations_html = ""
    if detailed_citations:
        for pub_id, data in detailed_citations.items():
            # Создаем безопасный ID для JavaScript
            safe_id = re.sub(r'[^a-zA-Z0-9]', '_', pub_id)
            
            detailed_citations_html += f"""
            <div class="collapser" onclick="toggleCitations('{safe_id}')">
                <strong>{html.escape(data['title'][:100])}</strong>
                <span class="badge badge-info">{data['year']}</span>
                <span class="citation-count">{data['total_citations']} {t('citations')}</span>
                <span style="font-size: 12px; color: #666; margin-left: 10px;">DOI: {data['doi'][:30]}...</span>
                <span style="float: right; font-size: 12px; color: #666;">{t('show_citations')}</span>
            </div>
            <div id="citations_{safe_id}" style="display: none;">
            """
            
            for cite in data['citations']:
                detailed_citations_html += f"""
                <div class="citation-detail">
                    <div><strong>{html.escape(cite['citing_title'][:150])}</strong></div>
                    <div class="cite-meta">
                        <strong>{t('citing_journal')}:</strong> {html.escape(cite['citing_journal'])} | 
                        <strong>{t('citing_year')}:</strong> {cite['citing_year']} | 
                        <strong>{t('citing_date')}:</strong> {cite['citing_date']} |
                        <strong>{t('citation_lag')}:</strong> {cite['citation_lag']} {t('years')}
                    </div>
                    <div class="cite-meta">
                        <strong>{t('authors')}:</strong> {', '.join(cite['citing_authors'][:5])}{' +' + str(len(cite['citing_authors']) - 5) if len(cite['citing_authors']) > 5 else ''} |
                        <strong>{t('countries')}:</strong> {', '.join(cite['citing_countries'][:3])} |
                        <strong>{t('topics')}:</strong> {', '.join(cite['citing_topics'][:3])}
                    </div>
                    <div class="cite-meta">
                        <a href="https://doi.org/{cite['citing_doi']}" target="_blank" class="doi-link">DOI: {cite['citing_doi']}</a>
                    </div>
                </div>
                """
            
            detailed_citations_html += """
            </div>
            """
    
    # Генерируем All Publications таблицу с фильтрацией
    all_publications_html = ""
    if all_publications:
        # Собираем уникальные годы для фильтра
        years_set = sorted(set(p['year'] for p in all_publications if p['year'] != 'N/A'), reverse=True)
        
        all_publications_html = f"""
        <div class="filter-section">
            <div class="filter-row">
                <div>
                    <label for="titleFilter">{t('filter_by_title')}:</label>
                    <input type="text" id="titleFilter" placeholder="Search in titles..." onkeyup="filterPublications()">
                </div>
                <div>
                    <label for="yearFilter">{t('filter_by_year')}:</label>
                    <select id="yearFilter" onchange="filterPublications()">
                        <option value="">All Years</option>
                        {''.join([f'<option value="{year}">{year}</option>' for year in years_set])}
                    </select>
                </div>
                <div>
                    <label for="authorFilter">{t('filter_by_author')}:</label>
                    <input type="text" id="authorFilter" placeholder="Author name..." onkeyup="filterPublications()">
                </div>
                <div>
                    <label for="affiliationFilter">{t('filter_by_affiliation')}:</label>
                    <input type="text" id="affiliationFilter" placeholder="Affiliation..." onkeyup="filterPublications()">
                </div>
                <div>
                    <label for="citationFilter">{t('filter_by_citations')}:</label>
                    <input type="number" id="citationFilter" placeholder="Min citations..." min="0" onchange="filterPublications()">
                </div>
                <div>
                    <span id="visibleCount" style="font-weight: 500;">All publications: {len(all_publications)}</span>
                </div>
            </div>
        </div>
        
        <div class="scrollable-table" style="max-height: 800px;">
            <table id="publicationsTable">
                <thead>
                    <tr>
                        <th onclick="sortTable(0)" style="cursor: pointer;">#</th>
                        <th onclick="sortTable(1)" style="cursor: pointer;">Title</th>
                        <th onclick="sortTable(2)" style="cursor: pointer;">Year</th>
                        <th onclick="sortTable(3)" style="cursor: pointer;">Authors</th>
                        <th onclick="sortTable(4)" style="cursor: pointer;">Affiliations</th>
                        <th onclick="sortTable(5)" style="cursor: pointer;">Citations</th>
                        <th onclick="sortTable(6)" style="cursor: pointer;">Citations/Year</th>
                        <th>DOI</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for pub in all_publications:
            # Подготавливаем данные для фильтрации (в data-атрибутах)
            authors_lower = ' '.join(pub.get('raw_authors', [])).lower()
            affiliations_lower = ' '.join(pub.get('raw_affiliations', [])).lower()
            title_lower = pub['title'].lower()
            
            all_publications_html += f"""
            <tr data-year="{pub['year']}" 
                data-authors="{html.escape(' '.join(pub.get('raw_authors', [])))}" 
                data-affiliations="{html.escape(' '.join(pub.get('raw_affiliations', [])))}" 
                data-citations="{pub['citations']}" 
                data-title="{html.escape(pub['title'].lower())}">
                <td>{pub['id']}</td>
                <td class="word-wrap">{html.escape(pub['title'])}</td>
                <td>{pub['year']}</td>
                <td>{html.escape(pub['authors'])}</td>
                <td>{html.escape(pub['affiliations'])}</td>
                <td><span class="citation-count">{pub['citations']}</span></td>
                <td>{pub['citations_per_year']:.1f}</td>
                <td><a href="https://doi.org/{pub['doi']}" target="_blank" class="doi-link">{pub['doi'][:30]}...</a></td>
            </tr>
            """
        
        all_publications_html += """
                </tbody>
            </table>
        </div>
        """
    
    # JavaScript для фильтрации и сортировки
    js_script = """
    <script>
        function toggleCitations(id) {
            var div = document.getElementById('citations_' + id);
            if (div) {
                if (div.style.display === 'none') {
                    div.style.display = 'block';
                } else {
                    div.style.display = 'none';
                }
            }
        }
        
        function filterPublications() {
            var titleFilter = document.getElementById('titleFilter')?.value?.toLowerCase() || '';
            var yearFilter = document.getElementById('yearFilter')?.value || '';
            var authorFilter = document.getElementById('authorFilter')?.value?.toLowerCase() || '';
            var affiliationFilter = document.getElementById('affiliationFilter')?.value?.toLowerCase() || '';
            var citationFilter = parseInt(document.getElementById('citationFilter')?.value) || 0;
            
            var table = document.getElementById('publicationsTable');
            if (!table) return;
            
            var rows = table.getElementsByTagName('tbody')[0].getElementsByTagName('tr');
            var visibleCount = 0;
            
            for (var i = 0; i < rows.length; i++) {
                var row = rows[i];
                var year = row.getAttribute('data-year') || '';
                var authors = row.getAttribute('data-authors')?.toLowerCase() || '';
                var affiliations = row.getAttribute('data-affiliations')?.toLowerCase() || '';
                var citations = parseInt(row.getAttribute('data-citations')) || 0;
                var title = row.getAttribute('data-title') || '';
                
                var show = true;
                
                if (yearFilter && year !== yearFilter) show = false;
                if (authorFilter && !authors.includes(authorFilter)) show = false;
                if (affiliationFilter && !affiliations.includes(affiliationFilter)) show = false;
                if (citationFilter > 0 && citations < citationFilter) show = false;
                if (titleFilter && !title.includes(titleFilter)) show = false;
                
                if (show) {
                    row.style.display = '';
                    visibleCount++;
                } else {
                    row.style.display = 'none';
                }
            }
            
            var countSpan = document.getElementById('visibleCount');
            if (countSpan) {
                countSpan.textContent = 'Showing ' + visibleCount + ' of ' + rows.length + ' publications';
            }
        }
        
        function sortTable(n) {
            var table = document.getElementById('publicationsTable');
            if (!table) return;
            
            var rows = table.getElementsByTagName('tbody')[0].getElementsByTagName('tr');
            var switching = true;
            var dir = 'asc';
            var switchcount = 0;
            
            while (switching) {
                switching = false;
                for (var i = 0; i < (rows.length - 1); i++) {
                    var x = rows[i].getElementsByTagName('td')[n];
                    var y = rows[i + 1].getElementsByTagName('td')[n];
                    
                    var xVal = x.textContent.trim();
                    var yVal = y.textContent.trim();
                    
                    if (n === 0 || n === 2 || n === 5 || n === 6) {
                        xVal = parseFloat(xVal) || 0;
                        yVal = parseFloat(yVal) || 0;
                    } else {
                        xVal = xVal.toLowerCase();
                        yVal = yVal.toLowerCase();
                    }
                    
                    if (dir === 'asc') {
                        if (xVal > yVal) {
                            rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
                            switching = true;
                            switchcount++;
                            break;
                        }
                    } else {
                        if (xVal < yVal) {
                            rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
                            switching = true;
                            switchcount++;
                            break;
                        }
                    }
                }
                if (switchcount === 0 && dir === 'asc') {
                    dir = 'desc';
                    switching = true;
                }
            }
        }
        
        // Автоматическая фильтрация при изменении полей
        document.addEventListener('DOMContentLoaded', function() {
            var inputs = document.querySelectorAll('#titleFilter, #yearFilter, #authorFilter, #affiliationFilter, #citationFilter');
            for (var i = 0; i < inputs.length; i++) {
                inputs[i].addEventListener('input', filterPublications);
                inputs[i].addEventListener('change', filterPublications);
            }
        });
    </script>
    """
    
    # Базовый HTML отчет
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>{t('app_title')} - {report_data.get('issn', '')}</title>
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
                padding: 25px 18px;
                overflow-y: auto;
                z-index: 1000;
            }}
            .sidebar h3 {{
                margin-bottom: 15px;
                font-size: 17px;
                font-weight: 600;
                color: white;
                border-bottom: 2px solid rgba(255,255,255,0.3);
                padding-bottom: 10px;
            }}
            .sidebar a {{
                color: rgba(255,255,255,0.85);
                text-decoration: none;
                display: flex;
                align-items: center;
                gap: 10px;
                padding: 7px 12px;
                margin: 3px 0;
                border-radius: 6px;
                transition: all 0.3s;
                font-size: 13px;
            }}
            .sidebar a:hover {{
                background: rgba(255,255,255,0.2);
                transform: translateX(4px);
                color: white;
            }}
            .sidebar .sub-link {{
                padding-left: 30px;
                font-size: 12px;
                opacity: 0.8;
            }}
            .sidebar .sub-link:hover {{
                opacity: 1;
            }}
            .main-content {{
                margin-left: 280px;
                padding: 30px 40px;
            }}
            .header {{
                background: linear-gradient(135deg, {primary} 0%, {secondary} 100%);
                color: white;
                padding: 30px 35px;
                border-radius: 15px;
                margin-bottom: 25px;
                display: flex;
                align-items: center;
                justify-content: space-between;
                flex-wrap: wrap;
                gap: 15px;
            }}
            .header-left {{
                display: flex;
                align-items: center;
                gap: 20px;
            }}
            .header-logo-app {{
                max-height: 70px;
                max-width: 200px;
            }}
            .header-logo {{
                max-height: 60px;
                max-width: 160px;
            }}
            .header h1 {{
                color: white;
                border-bottom: none;
                margin: 0;
                font-size: 26px;
                font-weight: 600;
            }}
            .header .subtitle {{
                opacity: 0.9;
                font-size: 14px;
                margin-top: 4px;
            }}
            .header .issn-info {{
                background: rgba(255,255,255,0.2);
                padding: 6px 16px;
                border-radius: 20px;
                font-size: 14px;
                font-weight: 500;
            }}
            .section {{
                background: white;
                border-radius: 12px;
                padding: 22px 25px;
                margin-bottom: 25px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                border: 1px solid #f0f0f0;
            }}
            .section-title {{
                font-size: 22px;
                font-weight: 600;
                margin-bottom: 18px;
                padding-bottom: 10px;
                border-bottom: 3px solid {primary};
                display: flex;
                align-items: center;
                gap: 12px;
            }}
            .section-title .icon {{
                font-size: 24px;
            }}
            .journal-metrics-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
                gap: 12px;
                margin: 15px 0;
            }}
            .journal-metric-card {{
                background: #f8f9fa;
                padding: 14px;
                border-radius: 10px;
                border-left: 4px solid {primary};
                text-align: center;
                transition: transform 0.3s;
            }}
            .journal-metric-card:hover {{
                transform: translateY(-3px);
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            }}
            .journal-metric-value {{
                font-size: 26px;
                font-weight: bold;
                color: #2C3E50;
                font-family: 'Times New Roman', serif;
            }}
            .journal-metric-label {{
                font-size: 11px;
                color: #7F8C8D;
                margin-top: 4px;
                font-family: 'Times New Roman', serif;
            }}
            .oa-progress-container {{
                margin: 15px 0;
                max-width: 600px;
            }}
            .oa-progress-item {{
                display: flex;
                align-items: center;
                gap: 12px;
                margin: 6px 0;
            }}
            .oa-progress-label {{
                min-width: 80px;
                font-size: 13px;
                font-weight: 500;
            }}
            .oa-progress-track {{
                flex: 1;
                height: 24px;
                background: #f0f0f0;
                border-radius: 12px;
                overflow: hidden;
                position: relative;
            }}
            .oa-progress-fill {{
                height: 100%;
                border-radius: 12px;
                transition: width 0.8s ease;
                display: flex;
                align-items: center;
                justify-content: flex-end;
                padding-right: 8px;
                font-size: 12px;
                font-weight: 600;
                color: white;
                text-shadow: 0 1px 2px rgba(0,0,0,0.3);
            }}
            .oa-progress-percent {{
                min-width: 50px;
                font-size: 13px;
                font-weight: 500;
                color: #555;
            }}
            .heatmap-grid {{
                display: grid;
                gap: 2px;
                margin: 15px 0;
                overflow-x: auto;
            }}
            .heatmap-row {{
                display: grid;
                gap: 2px;
                align-items: center;
            }}
            .heatmap-header {{
                font-weight: 600;
                padding: 8px 10px;
                background: #f0f0f0;
                text-align: center;
                font-size: 12px;
            }}
            .heatmap-row-label {{
                font-weight: 500;
                padding: 8px 10px;
                background: #f8f9fa;
                text-align: center;
                font-size: 12px;
            }}
            .heatmap-cell {{
                padding: 8px 10px;
                text-align: center;
                border-radius: 4px;
                font-size: 12px;
                font-weight: 500;
                transition: transform 0.2s;
            }}
            .heatmap-cell:hover {{
                transform: scale(1.05);
                z-index: 10;
                box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            }}
            .heatmap-cell-empty {{
                background: #f5f5f5;
                color: #ccc;
            }}
            .collapser {{
                cursor: pointer;
                padding: 12px 16px;
                margin: 8px 0;
                background: #f8f9fa;
                border-radius: 8px;
                border-left: 4px solid {primary};
                transition: background 0.3s, transform 0.2s;
                user-select: none;
            }}
            .collapser:hover {{
                background: #e9ecef;
                transform: translateX(4px);
            }}
            .collapser .citation-count {{
                background: {primary};
                color: white;
                padding: 2px 12px;
                border-radius: 12px;
                font-size: 12px;
                margin-left: 10px;
            }}
            .citation-detail {{
                padding: 12px 20px;
                margin: 4px 0 4px 20px;
                background: white;
                border-radius: 6px;
                border: 1px solid #e0e0e0;
                border-left: 3px solid {secondary};
            }}
            .citation-detail:hover {{
                background: #fafafa;
            }}
            .cite-meta {{
                font-size: 13px;
                color: #555;
                margin-top: 4px;
            }}
            .cite-meta strong {{
                color: #333;
            }}
            .filter-section {{
                background: #f8f9fa;
                padding: 16px 20px;
                border-radius: 10px;
                margin: 15px 0;
                border: 1px solid #e0e0e0;
            }}
            .filter-row {{
                display: flex;
                flex-wrap: wrap;
                gap: 12px;
                align-items: flex-end;
            }}
            .filter-row > div {{
                flex: 1;
                min-width: 140px;
            }}
            .filter-row label {{
                display: block;
                font-size: 12px;
                font-weight: 600;
                color: #555;
                margin-bottom: 4px;
            }}
            .filter-row select, .filter-row input {{
                width: 100%;
                padding: 6px 10px;
                border: 1px solid #ccc;
                border-radius: 6px;
                font-size: 13px;
                background: white;
            }}
            .filter-row select:focus, .filter-row input:focus {{
                border-color: {primary};
                outline: none;
                box-shadow: 0 0 0 3px rgba({int(hex_to_rgb(primary)[0])}, {int(hex_to_rgb(primary)[1])}, {int(hex_to_rgb(primary)[2])}, 0.2);
            }}
            #visibleCount {{
                font-weight: 600;
                color: {primary};
                font-size: 14px;
            }}
            .word-wrap {{
                word-wrap: break-word;
                max-width: 300px;
            }}
            .collab-couples-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
                gap: 8px;
                margin: 10px 0;
            }}
            .collab-couple-item {{
                background: #f8f9fa;
                padding: 8px 14px;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
                display: flex;
                justify-content: space-between;
                align-items: center;
                font-size: 13px;
            }}
            .collab-couple-item .badge {{
                background: {primary};
                color: white;
                padding: 2px 12px;
                border-radius: 12px;
                font-size: 12px;
            }}
            .scrollable-table {{
                max-height: 600px;
                overflow-y: auto;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
            }}
            .scrollable-table table {{
                margin: 0;
                width: 100%;
                border-collapse: collapse;
                font-size: 13px;
            }}
            .scrollable-table thead {{
                position: sticky;
                top: 0;
                z-index: 10;
            }}
            .scrollable-table th {{
                background: linear-gradient(135deg, {primary} 0%, {secondary} 100%);
                color: white;
                padding: 10px 12px;
                text-align: left;
                font-weight: 600;
                font-size: 12px;
                white-space: nowrap;
            }}
            .scrollable-table td {{
                padding: 8px 12px;
                border-bottom: 1px solid #e0e0e0;
                vertical-align: middle;
            }}
            .scrollable-table tr:hover {{
                background-color: #f5f5f5;
            }}
            .scrollable-table tr:nth-child(even) {{
                background-color: #fafafa;
            }}
            .scrollable-table tr:nth-child(even):hover {{
                background-color: #f0f0f0;
            }}
            .badge {{
                display: inline-block;
                padding: 2px 10px;
                border-radius: 12px;
                font-size: 11px;
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
            .citation-count {{
                background: {primary};
                color: white;
                padding: 2px 10px;
                border-radius: 12px;
                font-size: 12px;
                font-weight: 600;
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
            .footer {{
                margin-top: 30px;
                padding-top: 18px;
                border-top: 2px solid #e0e0e0;
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
            .stat-row {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 10px;
                margin: 10px 0;
            }}
            .stat-item {{
                background: #f8f9fa;
                padding: 8px 14px;
                border-radius: 6px;
                border-left: 3px solid {primary};
                font-size: 13px;
            }}
            .stat-item strong {{
                color: #333;
            }}
            .sub-section-title {{
                font-size: 18px;
                font-weight: 600;
                margin: 15px 0 10px 0;
                color: {primary};
                padding-bottom: 6px;
                border-bottom: 2px solid #e0e0e0;
            }}
            .collab-stats {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 15px;
                margin: 10px 0;
            }}
            .collab-stat-box {{
                background: #f8f9fa;
                padding: 12px 16px;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
                text-align: center;
            }}
            .collab-stat-box .value {{
                font-size: 24px;
                font-weight: bold;
                color: {primary};
            }}
            .collab-stat-box .label {{
                font-size: 13px;
                color: #666;
                margin-top: 4px;
            }}
            @media print {{
                .sidebar {{ display: none; }}
                .main-content {{ margin-left: 0; }}
            }}
            @media (max-width: 768px) {{
                .sidebar {{ display: none; }}
                .main-content {{ margin-left: 0; padding: 15px; }}
                .filter-row > div {{ min-width: 100%; }}
                .collab-stats {{ grid-template-columns: 1fr; }}
            }}
        </style>
    </head>
    <body>
        <div class="sidebar">
            <h3>📊 {t('app_title')}</h3>
            <a href="#overview"><span>📋</span> {t('overview')}</a>
            <a href="#analyzed_articles" class="sub-link"><span>📄</span> {t('analyzed_articles')}</a>
            <a href="#author_analysis" class="sub-link"><span>👤</span> {t('author_analysis')}</a>
            <a href="#top_affiliations" class="sub-link"><span>🏛️</span> {t('top_affiliations')}</a>
            <a href="#geographic_analysis" class="sub-link"><span>🌍</span> {t('geographic_analysis')}</a>
            <a href="#citation_analysis"><span>📈</span> {t('citation_analysis')}</a>
            <a href="#citation_dynamics" class="sub-link"><span>📊</span> {t('citation_dynamics')}</a>
            <a href="#cumulative_citations" class="sub-link"><span>📈</span> {t('cumulative_citations')}</a>
            <a href="#citation_heatmap" class="sub-link"><span>🔥</span> {t('citation_heatmap')}</a>
            <a href="#most_cited" class="sub-link"><span>⭐</span> {t('most_cited_publications')}</a>
            <a href="#citing_works"><span>🔄</span> {t('citing_works')}</a>
            <a href="#top_citing_authors" class="sub-link"><span>👤</span> {t('top_citing_authors')}</a>
            <a href="#top_citing_affiliations" class="sub-link"><span>🏛️</span> {t('top_citing_affiliations')}</a>
            <a href="#top_citing_countries" class="sub-link"><span>🌍</span> {t('top_citing_countries')}</a>
            <a href="#top_citing_journals" class="sub-link"><span>📰</span> {t('top_citing_journals')}</a>
            <a href="#top_citing_publishers" class="sub-link"><span>📚</span> {t('top_citing_publishers')}</a>
            <a href="#topics_analysis"><span>🏷️</span> {t('topics_analysis')}</a>
            <a href="#topic_overview" class="sub-link"><span>📊</span> {t('topic_overview')}</a>
            <a href="#top_topics_section" class="sub-link"><span>🏷️</span> {t('top_topics')}</a>
            <a href="#detailed_citations"><span>📋</span> {t('detailed_citations')}</a>
            <a href="#all_publications"><span>📚</span> {t('all_publications')}</a>
        </div>
        
        <div class="main-content">
            <div class="header">
                <div class="header-left">
                    {f'<img src="data:image/png;base64,{app_logo_base64}" class="header-logo-app" alt="{t("app_title")}">' if app_logo_base64 else ''}
                    <div>
                        <h1>{t('app_title')}</h1>
                        <div class="subtitle">{t('journal_analysis')}</div>
                    </div>
                </div>
                <div style="display: flex; align-items: center; gap: 15px; flex-wrap: wrap;">
                    {f'<img src="data:image/png;base64,{logo_base64}" class="header-logo" alt="Journal Logo">' if logo_base64 else ''}
                    <span class="issn-info">ISSN: {report_data.get('issn', '')}</span>
                    <span class="issn-info">Period: {report_data.get('period', '')}</span>
                </div>
            </div>
            
            <!-- OVERVIEW -->
            <div id="overview" class="section">
                <div class="section-title"><span class="icon">📋</span> {t('overview')}</div>
                
                <div class="journal-metrics-grid">
                    <div class="journal-metric-card">
                        <div class="journal-metric-value">{total_pubs}</div>
                        <div class="journal-metric-label">{t('total_publications')}</div>
                    </div>
                    <div class="journal-metric-card">
                        <div class="journal-metric-value">{total_citations:,}</div>
                        <div class="journal-metric-label">{t('total_citations')}</div>
                    </div>
                    <div class="journal-metric-card">
                        <div class="journal-metric-value">{h_index}</div>
                        <div class="journal-metric-label">{t('h_index')}</div>
                    </div>
                    <div class="journal-metric-card">
                        <div class="journal-metric-value">{g_index}</div>
                        <div class="journal-metric-label">{t('g_index')}</div>
                    </div>
                    <div class="journal-metric-card">
                        <div class="journal-metric-value">{i10_index}</div>
                        <div class="journal-metric-label">{t('i10_index')}</div>
                    </div>
                    <div class="journal-metric-card">
                        <div class="journal-metric-value">{i100_index}</div>
                        <div class="journal-metric-label">{t('i100_index')}</div>
                    </div>
                    <div class="journal-metric-card">
                        <div class="journal-metric-value">{avg_citations:.1f}</div>
                        <div class="journal-metric-label">{t('avg_citations')}</div>
                    </div>
                    <div class="journal-metric-card">
                        <div class="journal-metric-value">{active_years}</div>
                        <div class="journal-metric-label">{t('active_years')}</div>
                    </div>
                    <div class="journal-metric-card">
                        <div class="journal-metric-value">{unique_authors}</div>
                        <div class="journal-metric-label">{t('unique_authors')}</div>
                    </div>
                    <div class="journal-metric-card">
                        <div class="journal-metric-value">{unique_affiliations}</div>
                        <div class="journal-metric-label">{t('unique_affiliations')}</div>
                    </div>
                    <div class="journal-metric-card">
                        <div class="journal-metric-value">{unique_countries}</div>
                        <div class="journal-metric-label">{t('unique_countries')}</div>
                    </div>
                    <div class="journal-metric-card">
                        <div class="journal-metric-value">{avg_authors_per_paper:.1f}</div>
                        <div class="journal-metric-label">{t('avg_authors_per_paper')}</div>
                    </div>
                    <div class="journal-metric-card">
                        <div class="journal-metric-value">{avg_affiliations_per_paper:.1f}</div>
                        <div class="journal-metric-label">{t('avg_affiliations_per_paper')}</div>
                    </div>
                    <div class="journal-metric-card">
                        <div class="journal-metric-value">{avg_countries_per_paper:.1f}</div>
                        <div class="journal-metric-label">{t('avg_countries_per_paper')}</div>
                    </div>
                    <div class="journal-metric-card">
                        <div class="journal-metric-value">{international_collab_rate*100:.1f}%</div>
                        <div class="journal-metric-label">{t('international_collab_rate')}</div>
                    </div>
                    <div class="journal-metric-card">
                        <div class="journal-metric-value">{total_citing_works}</div>
                        <div class="journal-metric-label">{t('total_citing_works')}</div>
                    </div>
                    <div class="journal-metric-card">
                        <div class="journal-metric-value">{unique_citing_authors}</div>
                        <div class="journal-metric-label">{t('unique_citing_authors')}</div>
                    </div>
                    <div class="journal-metric-card">
                        <div class="journal-metric-value">{unique_citing_affiliations}</div>
                        <div class="journal-metric-label">{t('unique_citing_affiliations')}</div>
                    </div>
                    <div class="journal-metric-card">
                        <div class="journal-metric-value">{unique_citing_countries}</div>
                        <div class="journal-metric-label">{t('unique_citing_countries')}</div>
                    </div>
                    <div class="journal-metric-card">
                        <div class="journal-metric-value">{unique_citing_journals}</div>
                        <div class="journal-metric-label">{t('unique_citing_journals')}</div>
                    </div>
                    <div class="journal-metric-card">
                        <div class="journal-metric-value">{unique_citing_publishers}</div>
                        <div class="journal-metric-label">{t('unique_citing_publishers')}</div>
                    </div>
                </div>
                
                <h3 style="color: {primary}; margin-top: 20px;">{t('oa_breakdown')}</h3>
                <div class="oa-progress-container">
                    {oa_bars_html}
                </div>
            </div>
            
            <!-- ANALYZED ARTICLES -->
            <div id="analyzed_articles" class="section">
                <div class="section-title"><span class="icon">📄</span> {t('analyzed_articles')}</div>
                
                <!-- Author Analysis -->
                <div id="author_analysis">
                    <h3 class="sub-section-title">{t('author_analysis')}</h3>
                    {author_table_html if author_table_html else '<p>No data available</p>'}
                </div>
                
                <!-- Top Affiliations -->
                <div id="top_affiliations">
                    <h3 class="sub-section-title">{t('top_affiliations')}</h3>
                    {aff_table_html if aff_table_html else '<p>No data available</p>'}
                </div>
                
                <!-- Geographic Analysis -->
                <div id="geographic_analysis">
                    <h3 class="sub-section-title">{t('geographic_analysis')}</h3>
                    
                    <h4 style="margin: 12px 0 6px 0;">{t('unique_countries_per_pub')}</h4>
                    {countries_pub_html if countries_pub_html else '<p>No data available</p>'}
                    
                    <h4 style="margin: 12px 0 6px 0;">{t('authors_per_country')}</h4>
                    {authors_country_html if authors_country_html else '<p>No data available</p>'}
                    
                    <h4 style="margin: 12px 0 6px 0;">{t('collaboration_patterns')}</h4>
                    <div class="collab-stats">
                        <div class="collab-stat-box">
                            <div class="value">{single_country_papers}</div>
                            <div class="label">{t('single_country')}</div>
                        </div>
                        <div class="collab-stat-box">
                            <div class="value">{international_papers}</div>
                            <div class="label">{t('international')}</div>
                        </div>
                    </div>
                    
                    <h4 style="margin: 12px 0 6px 0;">{t('collaboration_couples')}</h4>
                    {collab_couples_html if collab_couples_html else '<p>No data available</p>'}
                </div>
            </div>
            
            <!-- CITATION ANALYSIS -->
            <div id="citation_analysis" class="section">
                <div class="section-title"><span class="icon">📈</span> {t('citation_analysis')}</div>
                
                <!-- Citation Dynamics -->
                <div id="citation_dynamics">
                    <h3 class="sub-section-title">{t('citation_dynamics')}</h3>
                    {citation_dynamics_html if citation_dynamics_html else '<p>No data available</p>'}
                </div>
                
                <!-- First Citation Analysis -->
                <div id="first_citation_analysis">
                    <h3 class="sub-section-title">{t('first_citation_analysis')}</h3>
                    <div class="stat-row">
                        <div class="stat-item"><strong>{t('min')}:</strong> {first_citation_stats.get('min', '—')} {t('years')}</div>
                        <div class="stat-item"><strong>{t('max')}:</strong> {first_citation_stats.get('max', '—')} {t('years')}</div>
                        <div class="stat-item"><strong>{t('avg')}:</strong> {first_citation_stats.get('avg', '—'):.1f} {t('years')}</div>
                        <div class="stat-item"><strong>{t('median')}:</strong> {first_citation_stats.get('median', '—')} {t('years')}</div>
                    </div>
                </div>
                
                <!-- Cumulative Citations -->
                <div id="cumulative_citations">
                    <h3 class="sub-section-title">{t('cumulative_citations')}</h3>
                    {cumulative_html if cumulative_html else '<p>No data available</p>'}
                </div>
                
                <!-- Citation Heatmap -->
                <div id="citation_heatmap">
                    <h3 class="sub-section-title">{t('citation_heatmap')}</h3>
                    {heatmap_html if heatmap_html else '<p>No data available</p>'}
                </div>
                
                <!-- Most Cited Publications -->
                <div id="most_cited">
                    <h3 class="sub-section-title">{t('most_cited_publications')}</h3>
                    {most_cited_html if most_cited_html else '<p>No data available</p>'}
                </div>
            </div>
            
            <!-- CITING WORKS ANALYSIS -->
            <div id="citing_works" class="section">
                <div class="section-title"><span class="icon">🔄</span> {t('citing_works_analysis')}</div>
                
                <div class="stat-row">
                    <div class="stat-item"><strong>{t('total_citing_works')}:</strong> {total_citing_works}</div>
                    <div class="stat-item"><strong>{t('unique_citing_authors')}:</strong> {unique_citing_authors}</div>
                    <div class="stat-item"><strong>{t('unique_citing_affiliations')}:</strong> {unique_citing_affiliations}</div>
                    <div class="stat-item"><strong>{t('unique_citing_countries')}:</strong> {unique_citing_countries}</div>
                    <div class="stat-item"><strong>{t('unique_citing_journals')}:</strong> {unique_citing_journals}</div>
                    <div class="stat-item"><strong>{t('unique_citing_publishers')}:</strong> {unique_citing_publishers}</div>
                </div>
                
                <div id="top_citing_authors">
                    <h3 class="sub-section-title">{t('top_citing_authors')}</h3>
                    {citing_authors_html if citing_authors_html else '<p>No data available</p>'}
                </div>
                
                <div id="top_citing_affiliations">
                    <h3 class="sub-section-title">{t('top_citing_affiliations')}</h3>
                    {citing_aff_html if citing_aff_html else '<p>No data available</p>'}
                </div>
                
                <div id="top_citing_countries">
                    <h3 class="sub-section-title">{t('top_citing_countries')}</h3>
                    {citing_countries_html if citing_countries_html else '<p>No data available</p>'}
                </div>
                
                <div id="top_citing_journals">
                    <h3 class="sub-section-title">{t('top_citing_journals')}</h3>
                    {citing_journals_html if citing_journals_html else '<p>No data available</p>'}
                </div>
                
                <div id="top_citing_publishers">
                    <h3 class="sub-section-title">{t('top_citing_publishers')}</h3>
                    {citing_publishers_html if citing_publishers_html else '<p>No data available</p>'}
                </div>
            </div>
            
            <!-- TOPICS ANALYSIS -->
            <div id="topics_analysis" class="section">
                <div class="section-title"><span class="icon">🏷️</span> {t('topics_analysis')}</div>
                
                <div id="topic_overview">
                    <h3 class="sub-section-title">{t('topic_overview')}</h3>
                    {topic_analysis_html if topic_analysis_html else '<p>No data available</p>'}
                </div>
                
                <div id="top_topics_section">
                    <h3 class="sub-section-title">{t('top_topics')}</h3>
                    {top_topics_html if top_topics_html else '<p>No data available</p>'}
                </div>
                
                <div id="top_subtopics_section">
                    <h3 class="sub-section-title">{t('top_subtopics')}</h3>
                    {top_subtopics_html if top_subtopics_html else '<p>No data available</p>'}
                </div>
                
                <div id="top_fields_section">
                    <h3 class="sub-section-title">{t('top_fields')}</h3>
                    {top_fields_html if top_fields_html else '<p>No data available</p>'}
                </div>
                
                <div id="top_domains_section">
                    <h3 class="sub-section-title">{t('top_domains')}</h3>
                    {top_domains_html if top_domains_html else '<p>No data available</p>'}
                </div>
                
                <div id="top_concepts_section">
                    <h3 class="sub-section-title">{t('top_concepts')}</h3>
                    {top_concepts_html if top_concepts_html else '<p>No data available</p>'}
                </div>
            </div>
            
            <!-- DETAILED CITATIONS -->
            <div id="detailed_citations" class="section">
                <div class="section-title"><span class="icon">📋</span> {t('detailed_citations')}</div>
                {detailed_citations_html if detailed_citations_html else '<p>No data available</p>'}
            </div>
            
            <!-- ALL PUBLICATIONS -->
            <div id="all_publications" class="section">
                <div class="section-title"><span class="icon">📚</span> {t('all_publications')}</div>
                {all_publications_html if all_publications_html else '<p>No data available</p>'}
            </div>
            
            <!-- FOOTER -->
            <div class="footer">
                <p>{t('footer')}</p>
                <p><a href="{t('journal_url')}" target="_blank">{t('journal_url')}</a></p>
                <p style="font-size: 11px; margin-top: 5px;">Data source: OpenAlex | Generated: {datetime.now().strftime('%d.%m.%Y')}</p>
            </div>
        </div>
    </body>
    {js_script}
    </html>
    """
    
    return html_content

def generate_html_report_from_analysis(analyzer: JournalAnalyzer, logo_base64: Optional[str] = None, app_logo_base64: Optional[str] = None, theme_colors: Optional[Dict] = None, lang: str = 'en') -> str:
    """Генерирует HTML отчет из объекта анализатора"""
    report_data = analyzer.report_data
    return generate_html_report(report_data, logo_base64, app_logo_base64, theme_colors, lang)

# ============================================
# ОСНОВНАЯ ФУНКЦИЯ ЗАПУСКА ДЛЯ STREAMLIT
# ============================================

def run_journal_analysis(issn: str, period, max_workers: int = MAX_WORKERS, journal_logo: Optional[Dict] = None, lang: str = 'en'):
    """Запускает анализ журнала и отображает результаты"""
    
    def t(key: str, **kwargs) -> str:
        return translate(key, lang, **kwargs)
    
    if not issn or not period:
        st.error("⚠️ " + t('no_data'))
        return
    
    # Нормализуем ISSN
    issn_normalized = normalize_issn(issn)
    if len(issn_normalized) != 9 or issn_normalized[4] != '-':
        st.error("⚠️ " + t('data_not_found'))
        return
    
    # Парсим период
    period_str = str(period)
    if ',' in period_str:
        years = [int(y.strip()) for y in period_str.split(',') if y.strip().isdigit()]
        if years:
            period_parsed = years
        else:
            st.error("⚠️ " + t('data_not_found'))
            return
    elif '-' in period_str:
        parts = period_str.split('-')
        if len(parts) == 2 and parts[0].strip().isdigit() and parts[1].strip().isdigit():
            period_parsed = (int(parts[0].strip()), int(parts[1].strip()))
        else:
            st.error("⚠️ " + t('data_not_found'))
            return
    else:
        if period_str.strip().isdigit():
            period_parsed = int(period_str.strip())
        else:
            st.error("⚠️ " + t('data_not_found'))
            return
    
    # Загружаем логотип приложения
    app_logo_base64 = None
    if os.path.exists("logo.png"):
        try:
            with open("logo.png", "rb") as f:
                app_logo_base64 = base64.b64encode(f.read()).decode()
        except Exception as e:
            if SHOW_DEBUG_LOGS:
                print(f"⚠️ Ошибка загрузки логотипа приложения: {e}")
    
    journal_logo_base64 = None
    if journal_logo:
        try:
            for filename, file_info in journal_logo.items():
                content = file_info['content'] if hasattr(file_info, 'get') else file_info
                if hasattr(content, 'read'):
                    content = content.read()
                journal_logo_base64 = base64.b64encode(content).decode()
                if SHOW_DEBUG_LOGS:
                    print(f"✅ Логотип журнала загружен: {filename}")
                break
        except Exception as e:
            st.warning(f"⚠️ " + t('error_occurred') + f": {e}")
    
    # Создаем прогресс-бары
    progress_container = st.empty()
    status_container = st.empty()
    analysis_progress = st.progress(0, text=t('analysis_in_progress'))
    
    # Функция обновления прогресса
    def progress_callback(current: int, total: int, stage: str, stage_current: int = 0, stage_total: int = 0):
        """Обновляет прогресс в интерфейсе"""
        stages = {
            'stage_fetching_articles': 0,
            'stage_collecting_citations': 25,
            'stage_enriching_articles': 50,
            'stage_enriching_citations': 75,
            'stage_generating_report': 90
        }
        
        stage_base = stages.get(stage, 0)
        
        if stage_total > 0:
            stage_progress = (stage_current / stage_total) * 25
        else:
            stage_progress = 0
        
        total_progress = (stage_base + stage_progress) / 100
        
        # Ограничиваем 99% до завершения
        total_progress = min(total_progress, 0.99)
        
        # Обновляем прогресс-бар
        analysis_progress.progress(total_progress, text=t(stage))
        
        # Обновляем статус с деталями
        if stage_total > 0:
            status_container.info(f"{t(stage)} ({stage_current}/{stage_total})")
        else:
            status_container.info(t(stage))
    
    try:
        # Создаем анализатор
        analyzer = JournalAnalyzer(issn_normalized, period_parsed, max_workers)
        
        # Запускаем анализ
        report_data = analyzer.run_analysis(progress_callback)
        
        if not report_data:
            st.error("❌ " + t('data_not_found'))
            analysis_progress.empty()
            return
        
        # Завершаем прогресс
        analysis_progress.progress(1.0, text=f"✅ {t('analysis_complete')}")
        status_container.success(f"✅ {t('analysis_complete')}")
        
        # Сохраняем данные в session_state
        st.session_state['report_data'] = report_data
        st.session_state['analyzer'] = analyzer
        st.session_state['analysis_complete'] = True
        st.session_state['journal_logo_base64'] = journal_logo_base64
        st.session_state['app_logo_base64'] = app_logo_base64
        
        # Отображаем метрики
        st.markdown("---")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric(t('total_publications'), report_data.get('total_publications', 0))
        with col2:
            st.metric(t('total_citations'), f"{report_data.get('total_citations', 0):,}")
        with col3:
            st.metric(t('h_index'), report_data.get('h_index', 0))
        with col4:
            st.metric(t('g_index'), report_data.get('g_index', 0))
        with col5:
            st.metric(t('avg_citations'), f"{report_data.get('avg_citations', 0):.1f}")
        
        # Кнопка скачивания отчета
        st.markdown("---")
        st.markdown(f"### {t('download_report')}")
        
        theme_colors = {
            'primary': st.session_state.get('primary_color', '#667eea'),
            'secondary': st.session_state.get('secondary_color', '#f39c12')
        }
        
        if st.button(t('download_report'), type="primary", width='stretch'):
            with st.spinner(t('generating_report')):
                html_report = generate_html_report_from_analysis(
                    analyzer,
                    journal_logo_base64,
                    app_logo_base64,
                    theme_colors,
                    lang
                )
                
                filename = f"journal_{issn_normalized}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
                
                st.download_button(
                    label="📥 " + t('download_report'),
                    data=html_report.encode('utf-8'),
                    file_name=filename,
                    mime="text/html",
                    width='stretch'
                )
        
        # Предпросмотр отчета
        st.markdown("---")
        st.markdown(f"### {t('report_preview')}")
        
        with st.spinner(t('generating_report')):
            html_report_preview = generate_html_report_from_analysis(
                analyzer,
                journal_logo_base64,
                app_logo_base64,
                theme_colors,
                lang
            )
            
            # Отображаем HTML в iframe
            st.components.v1.html(html_report_preview, height=800, scrolling=True)
        
        st.balloons()
        
    except Exception as e:
        st.error(f"❌ {t('error_occurred')}: {str(e)}")
        import traceback
        st.code(traceback.format_exc())
    finally:
        analysis_progress.empty()

# ============================================
# СОЗДАНИЕ WIDGET-ИНТЕРФЕЙСА STREAMLIT
# ============================================

def main():
    # Page configuration
    st.set_page_config(
        page_title="Advanced Journal Analysis",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    if 'primary_color' not in st.session_state:
        st.session_state.primary_color = '#667eea'
    if 'secondary_color' not in st.session_state:
        st.session_state.secondary_color = '#f39c12'
    if 'analysis_complete' not in st.session_state:
        st.session_state.analysis_complete = False
    if 'journal_logo_base64' not in st.session_state:
        st.session_state.journal_logo_base64 = None
    if 'app_logo_base64' not in st.session_state:
        st.session_state.app_logo_base64 = None
    if 'language' not in st.session_state:
        st.session_state.language = 'en'  # По умолчанию английский
    if 'report_data' not in st.session_state:
        st.session_state.report_data = {}
    if 'analyzer' not in st.session_state:
        st.session_state.analyzer = None
    
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
            © daM / Advanced Journal Analysis
        </div>
        """, unsafe_allow_html=True)
    
    # Main content
    st.markdown("---")
    
    # Display logo if exists
    if os.path.exists("logo.png"):
        col_logo, col_text = st.columns([1, 3])
        with col_logo:
            st.image("logo.png", width=200)
    else:
        st.markdown(f"### {t('app_title')}")
    
    st.markdown("---")
    
    # Main interface
    st.markdown(f"## {t('journal_analysis')}")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        issn_input = st.text_input(
            t('issn_label'),
            placeholder="0028-0836",
            help="Enter the ISSN of the journal (e.g., 0028-0836)"
        )
        
        period_input = st.text_input(
            t('period_label'),
            placeholder="2020-2023",
            help=t('period_hint')
        )
    
    with col2:
        max_workers = st.slider(
            t('threads_label'),
            min_value=4,
            max_value=12,
            value=8,
            step=1,
            help="Number of parallel threads for citation collection"
        )
        
        journal_logo_upload = st.file_uploader(
            t('upload_logo'),
            type=['png', 'jpg', 'jpeg', 'svg'],
            help=t('logo_help')
        )
    
    # Start analysis button
    if st.button(t('start_analysis'), type="primary", width='stretch'):
        journal_logo_data = None
        if journal_logo_upload:
            journal_logo_data = {
                journal_logo_upload.name: {
                    'content': journal_logo_upload.read()
                }
            }
        
        run_journal_analysis(
            issn_input,
            period_input,
            max_workers,
            journal_logo_data,
            current_lang
        )
    
    # Display report if available
    if st.session_state.analysis_complete and st.session_state.report_data:
        st.markdown("---")
        
        # Кнопка скачивания отчета
        st.markdown(f"### {t('download_report')}")
        
        theme_colors = {
            'primary': st.session_state.primary_color,
            'secondary': st.session_state.secondary_color
        }
        
        if st.button(t('download_report'), type="primary", width='stretch', key="download_report_btn"):
            with st.spinner(t('generating_report')):
                html_report = generate_html_report_from_analysis(
                    st.session_state.analyzer,
                    st.session_state.journal_logo_base64,
                    st.session_state.app_logo_base64,
                    theme_colors,
                    current_lang
                )
                
                issn_normalized = normalize_issn(st.session_state.report_data.get('issn', ''))
                filename = f"journal_{issn_normalized}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
                
                st.download_button(
                    label="📥 " + t('download_report'),
                    data=html_report.encode('utf-8'),
                    file_name=filename,
                    mime="text/html",
                    width='stretch'
                )
        
        # Предпросмотр отчета
        st.markdown("---")
        st.markdown(f"### {t('report_preview')}")
        
        with st.spinner(t('generating_report')):
            html_report_preview = generate_html_report_from_analysis(
                st.session_state.analyzer,
                st.session_state.journal_logo_base64,
                st.session_state.app_logo_base64,
                theme_colors,
                current_lang
            )
            
            # Отображаем HTML в iframe
            st.components.v1.html(html_report_preview, height=800, scrolling=True)

if __name__ == "__main__":
    main()
