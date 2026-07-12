# ============================================
# СЕКЦИЯ ПАРАМЕТРОВ (настройка запросов)
# ============================================

# Параметры API запросов
BATCH_SIZE = 50  # Размер батча для всех API
MAX_RETRIES = 4  # Количество попыток при ошибке
TIMEOUT = 30  # Таймаут на запрос в секундах
DELAY_BETWEEN_BATCHES = 0.5  # Задержка между батчами (сек)
MAX_CONCURRENT_REQUESTS = 10  # Максимум параллельных запросов
RETRY_DELAY = 2  # Задержка перед повторной попыткой (сек)
MAX_WORKERS = 8  # Количество параллельных потоков для цитирований
BASE_DELAY = 0.35  # Базовая задержка между запросами
MAX_CITING_PER_PAPER = None  # Без ограничения

# Параметры вывода
SHOW_DEBUG_LOGS = True  # Показывать детальные логи
GENERATE_HTML_REPORT = True  # Генерировать HTML отчет
USE_CACHE = False  # Кэширование результатов
LOGO_PATH = None  # Путь к логотипу журнала (устанавливается через виджет)

# Лимиты для анализа
MAX_PUBLICATIONS_TO_ANALYZE = 5000  # Максимум статей для анализа в год
MIN_YEAR_FOR_TREND = 5  # Сколько лет для тренда

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

# ============================================
# СЛОВАРЬ ПЕРЕВОДОВ (РАСШИРЕННЫЙ)
# ============================================

LANG = {
    'en': {
        # Existing translations...
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
        'analysis': '📊 Analysis',
        'reports': '📄 Reports',
        'issn_input': 'Journal ISSN',
        'issn_placeholder': '0028-0836',
        'period_input': 'Analysis Period',
        'period_placeholder': '2020-2023 or 2020,2021,2022 or 2020',
        'period_help': 'Enter period: 2020-2023 (range), 2020,2021,2022 (list), or 2020 (single year)',
        'max_workers': 'Parallel Threads',
        'max_workers_help': 'Number of parallel threads for citation fetching (4-12 recommended)',
        'analyze_button': '🔍 Analyze Journal',
        'no_issn': '⚠️ Enter ISSN',
        'no_period': '⚠️ Enter analysis period',
        'analysis_complete': '✅ Analysis complete! Found {count} publications in {time:.1f} sec.',
        'analyzing_journal': '🔍 Analyzing journal {issn} for period {period}...',
        'no_data': '👈 Load data in "Load Data" tab and click "Analyze Journal"',
        'no_data_reports': '👈 First run analysis in "Load Data" tab',
        'html_report': '📄 HTML Report Generation',
        'download_report': '💾 Download HTML Report',
        'report_preview': '📋 HTML Report Preview',
        'download_hint': 'Click "Download HTML Report" for full report',
        'generating_report': 'Generating HTML report...',
        'publications': 'Publications',
        'citations': 'Citations',
        'h_index': 'h-index',
        'g_index': 'g-index',
        'i10_index': 'i10-index',
        'i100_index': 'i100-index',
        'total_citations': 'Total Citations',
        'avg_citations': 'Avg Citations',
        'median_citations': 'Median Citations',
        'max_citations': 'Max Citations',
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
        'unknown_oa': 'Unknown',
        'open_access_breakdown': 'Open Access Breakdown',
        'overview': 'Overview',
        'analyzed_articles': 'Analyzed Articles',
        'author_analysis': 'Author Analysis',
        'rank': 'Rank',
        'authors': 'Authors',
        'orcid': 'ORCID',
        'affiliations': 'Affiliations',
        'countries': 'Countries',
        'publications_count': 'Publications',
        'top_affiliations': 'Top Affiliations',
        'geographic_analysis': 'Geographic Analysis',
        'unique_countries_per_publication': 'Unique Countries per Publication (Collaboration Level)',
        'authors_per_country': 'Authors per Country (Individual Distribution)',
        'collaboration_patterns': 'Collaboration Patterns',
        'single_country': 'Single Country',
        'international': 'International',
        'collaboration_couples': 'Collaboration Couples',
        'country_pair': 'Country Pair',
        'frequency': 'Frequency',
        'citation_analysis': 'Citation Analysis',
        'citation_dynamics_by_year': 'Citation Dynamics by Year',
        'publication_year': 'Publication Year',
        'citation_year': 'Citation Year',
        'citations_count': 'Citations Count',
        'cumulative_citations': 'Cumulative Citations',
        'citation_network_heatmap': 'Citation Network Heatmap',
        'most_cited_publications': 'Most Cited Publications',
        'title': 'Title',
        'year': 'Year',
        'citations_per_year': 'Citations/Year',
        'doi': 'DOI',
        'citing_works_analysis': 'Citing Works Analysis',
        'total_citing_works': 'Total Citing Works',
        'top_citing_authors': 'Top Citing Authors',
        'top_citing_affiliations': 'Top Citing Affiliations',
        'top_citing_countries': 'Top Citing Countries',
        'top_citing_journals': 'Top Citing Journals',
        'top_citing_publishers': 'Top Citing Publishers',
        'topics_analysis': 'Topics Analysis',
        'topics': 'Topics',
        'analyzed_count': 'Analyzed Count',
        'citing_count': 'Citing Count',
        'analyzed_norm_count': 'Analyzed Norm Count',
        'citing_norm_count': 'Citing Norm Count',
        'total_norm_count': 'Total Norm Count',
        'first_year': 'First Year',
        'peak_year': 'Peak Year',
        'recent_5_years_count': 'Recent 5 Years Count',
        'top_cited_topics': 'Top Cited Topics',
        'subtopics': 'Subtopics',
        'fields': 'Fields',
        'domains': 'Domains',
        'concepts': 'Concepts',
        'detailed_citations': 'Detailed Citations',
        'citing_journal': 'Citing Journal',
        'citing_year': 'Citing Year',
        'citing_date': 'Citing Date',
        'citation_lag': 'Citation Lag',
        'all_publications': 'All Publications',
        'filter_by_year': 'Filter by Year',
        'filter_by_author': 'Filter by Author',
        'filter_by_affiliations': 'Filter by Affiliations',
        'filter_by_citations': 'Filter by Citations (min)',
        'filter_by_title': 'Filter by Title Word(s)',
        'search_publications': 'Search Publications',
        'show_citations': 'Show Citations',
        'footer': '© Advanced Journal Analysis Tool / Created by daM / Chimica Techno Acta',
        'journal_url': 'https://chimicatechnoacta.ru',
        'no_profile_data': 'No data available',
        'analyze_journal': 'Analyze Journal by ISSN',
        'select_language': 'Select language',
        'theme_presets_label': 'Theme presets',
        'primary_color_label': 'Primary color',
        'secondary_color_label': 'Secondary color',
        'analysis_progress': 'Analysis progress',
        'loading_data': 'Loading data',
        'analyzing_data': 'Analyzing data',
        'generating_viz': 'Generating visualizations',
        'error_occurred': 'Error occurred',
        'analyzing_publications': 'Analyzing {count} publications...',
        'starting_analysis': 'Starting analysis...',
        'fetching_data': 'Fetching data',
        'analysis_complete_text': 'Analysis complete',
        'creating_charts': 'Creating charts',
        'fetching_citations': 'Fetching citations...',
        'citations_fetched': 'Citations fetched: {count}',
        'loading_publications': 'Loading publications from journal...',
        'publications_loaded': 'Publications loaded: {count}',
        'processing_publications': 'Processing publications...',
        'collecting_metadata': 'Collecting metadata...',
        'metadata_collected': 'Metadata collected for {count} publications',
        'collecting_citing_metadata': 'Collecting citing works metadata...',
        'citing_metadata_collected': 'Citing works metadata collected: {count}',
        'no_citations_found': 'No citations found for this journal',
        'total_publications_found': 'Total publications found: {count}',
        'analyzing_citations': 'Analyzing citations...',
        'citation_analysis_complete': 'Citation analysis complete',
        'generating_report': 'Generating report...',
        'report_generated': 'Report generated successfully',
        'main_metrics': 'Main Metrics',
        'collaboration_metrics': 'Collaboration Metrics',
        'advanced_metrics': 'Advanced Metrics',
        'publication_metrics': 'Publication Metrics',
        'citation_metrics': 'Citation Metrics',
        'author_metrics': 'Author Metrics',
        'geographic_metrics': 'Geographic Metrics',
        'topic_metrics': 'Topic Metrics',
    },
    'ru': {
        # Existing translations...
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
        'analysis': '📊 Анализ',
        'reports': '📄 Отчеты',
        'issn_input': 'ISSN журнала',
        'issn_placeholder': '0028-0836',
        'period_input': 'Период анализа',
        'period_placeholder': '2020-2023 или 2020,2021,2022 или 2020',
        'period_help': 'Введите период: 2020-2023 (диапазон), 2020,2021,2022 (список), или 2020 (один год)',
        'max_workers': 'Параллельных потоков',
        'max_workers_help': 'Количество параллельных потоков для сбора цитирований (рекомендуется 4-12)',
        'analyze_button': '🔍 Анализировать журнал',
        'no_issn': '⚠️ Введите ISSN',
        'no_period': '⚠️ Введите период анализа',
        'analysis_complete': '✅ Анализ завершен! Найдено {count} публикаций за {time:.1f} сек.',
        'analyzing_journal': '🔍 Анализ журнала {issn} за период {period}...',
        'no_data': '👈 Загрузите данные на вкладке "Загрузка данных" и нажмите "Анализировать журнал"',
        'no_data_reports': '👈 Сначала выполните анализ на вкладке "Загрузка данных"',
        'html_report': '📄 Генерация HTML отчета',
        'download_report': '💾 Скачать HTML отчет',
        'report_preview': '📋 Предпросмотр HTML отчета',
        'download_hint': 'Нажмите "Скачать HTML отчет" для полного отчета',
        'generating_report': 'Генерация HTML отчета...',
        'publications': 'Публикаций',
        'citations': 'Цитирований',
        'h_index': 'h-индекс',
        'g_index': 'g-индекс',
        'i10_index': 'i10-индекс',
        'i100_index': 'i100-индекс',
        'total_citations': 'Всего цитирований',
        'avg_citations': 'Среднее цитирований',
        'median_citations': 'Медиана цитирований',
        'max_citations': 'Максимум цитирований',
        'open_access': 'Открытый доступ',
        'active_years': 'Активных лет',
        'unique_authors': 'Уникальных авторов',
        'unique_affiliations': 'Уникальных аффилиаций',
        'unique_countries': 'Уникальных стран',
        'avg_authors_per_paper': 'Среднее авторов на статью',
        'avg_affiliations_per_paper': 'Среднее аффилиаций на статью',
        'avg_countries_per_paper': 'Среднее стран на статью',
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
        'unknown_oa': 'Неизвестно',
        'open_access_breakdown': 'Распределение открытого доступа',
        'overview': 'Обзор',
        'analyzed_articles': 'Анализируемые статьи',
        'author_analysis': 'Анализ авторов',
        'rank': 'Ранг',
        'authors': 'Авторы',
        'orcid': 'ORCID',
        'affiliations': 'Аффилиации',
        'countries': 'Страны',
        'publications_count': 'Публикации',
        'top_affiliations': 'Топ аффилиаций',
        'geographic_analysis': 'Географический анализ',
        'unique_countries_per_publication': 'Уникальные страны на публикацию (Уровень коллаборации)',
        'authors_per_country': 'Авторы по странам (Индивидуальное распределение)',
        'collaboration_patterns': 'Модели коллабораций',
        'single_country': 'Одна страна',
        'international': 'Международные',
        'collaboration_couples': 'Пары коллабораций',
        'country_pair': 'Пара стран',
        'frequency': 'Частота',
        'citation_analysis': 'Анализ цитирований',
        'citation_dynamics_by_year': 'Динамика цитирований по годам',
        'publication_year': 'Год публикации',
        'citation_year': 'Год цитирования',
        'citations_count': 'Количество цитирований',
        'cumulative_citations': 'Накопительные цитирования',
        'citation_network_heatmap': 'Тепловая карта сети цитирований',
        'most_cited_publications': 'Самые цитируемые публикации',
        'title': 'Название',
        'year': 'Год',
        'citations_per_year': 'Цитирований/год',
        'doi': 'DOI',
        'citing_works_analysis': 'Анализ цитирующих работ',
        'total_citing_works': 'Всего цитирующих работ',
        'top_citing_authors': 'Топ цитирующих авторов',
        'top_citing_affiliations': 'Топ цитирующих аффилиаций',
        'top_citing_countries': 'Топ цитирующих стран',
        'top_citing_journals': 'Топ цитирующих журналов',
        'top_citing_publishers': 'Топ цитирующих издателей',
        'topics_analysis': 'Тематический анализ',
        'topics': 'Темы',
        'analyzed_count': 'Количество в анализе',
        'citing_count': 'Количество цитирований',
        'analyzed_norm_count': 'Норм. количество в анализе',
        'citing_norm_count': 'Норм. количество цитирований',
        'total_norm_count': 'Общее норм. количество',
        'first_year': 'Первый год',
        'peak_year': 'Пиковый год',
        'recent_5_years_count': 'Количество за последние 5 лет',
        'top_cited_topics': 'Топ цитируемых тем',
        'subtopics': 'Подтемы',
        'fields': 'Поля',
        'domains': 'Домены',
        'concepts': 'Концепты',
        'detailed_citations': 'Детальные цитирования',
        'citing_journal': 'Цитирующий журнал',
        'citing_year': 'Год цитирования',
        'citing_date': 'Дата цитирования',
        'citation_lag': 'Задержка цитирования',
        'all_publications': 'Все публикации',
        'filter_by_year': 'Фильтр по году',
        'filter_by_author': 'Фильтр по автору',
        'filter_by_affiliations': 'Фильтр по аффилиациям',
        'filter_by_citations': 'Фильтр по цитированиям (мин)',
        'filter_by_title': 'Фильтр по слову в названии',
        'search_publications': 'Поиск публикаций',
        'show_citations': 'Показать цитирования',
        'footer': '© Advanced Journal Analysis Tool / Created by daM / Chimica Techno Acta',
        'journal_url': 'https://chimicatechnoacta.ru',
        'no_profile_data': 'Нет данных',
        'analyze_journal': 'Анализ журнала по ISSN',
        'select_language': 'Выберите язык',
        'theme_presets_label': 'Пресеты тем',
        'primary_color_label': 'Основной цвет',
        'secondary_color_label': 'Дополнительный цвет',
        'analysis_progress': 'Прогресс анализа',
        'loading_data': 'Загрузка данных',
        'analyzing_data': 'Анализ данных',
        'generating_viz': 'Генерация визуализаций',
        'error_occurred': 'Произошла ошибка',
        'analyzing_publications': 'Анализ {count} публикаций...',
        'starting_analysis': 'Начинаем анализ...',
        'fetching_data': 'Получение данных',
        'analysis_complete_text': 'Анализ завершен',
        'creating_charts': 'Создание графиков',
        'fetching_citations': 'Сбор цитирований...',
        'citations_fetched': 'Собрано цитирований: {count}',
        'loading_publications': 'Загрузка публикаций из журнала...',
        'publications_loaded': 'Загружено публикаций: {count}',
        'processing_publications': 'Обработка публикаций...',
        'collecting_metadata': 'Сбор метаданных...',
        'metadata_collected': 'Собраны метаданные для {count} публикаций',
        'collecting_citing_metadata': 'Сбор метаданных цитирующих работ...',
        'citing_metadata_collected': 'Собраны метаданные цитирующих работ: {count}',
        'no_citations_found': 'Цитирования для этого журнала не найдены',
        'total_publications_found': 'Всего найдено публикаций: {count}',
        'analyzing_citations': 'Анализ цитирований...',
        'citation_analysis_complete': 'Анализ цитирований завершен',
        'generating_report': 'Генерация отчета...',
        'report_generated': 'Отчет успешно сгенерирован',
        'main_metrics': 'Основные метрики',
        'collaboration_metrics': 'Метрики коллабораций',
        'advanced_metrics': 'Расширенные метрики',
        'publication_metrics': 'Метрики публикаций',
        'citation_metrics': 'Метрики цитирований',
        'author_metrics': 'Метрики авторов',
        'geographic_metrics': 'Географические метрики',
        'topic_metrics': 'Тематические метрики',
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
        
        .author-section {{
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #e0e0e0;
        }}
        
        .author-section:last-child {{
            border-bottom: none;
        }}
        
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
    
    # Если уже полное название (длиннее 2 символов), возвращаем как есть
    if len(country_code) > 3:
        return country_code
    
    return COUNTRY_CODE_TO_NAME.get(country_code.upper(), country_code)

def normalize_issn(issn_str: str) -> str:
    """Normalize ISSN string to standard format"""
    cleaned = re.sub(r'[^0-9Xx]', '', str(issn_str).strip())
    if len(cleaned) == 8:
        return f"{cleaned[:4]}-{cleaned[4:]}".upper()
    return cleaned.upper()

def parse_period(period_str: str) -> Any:
    """
    Parse period string to OpenAlex filter format.
    Returns: list of years, tuple (start, end), or single year
    """
    period_str = period_str.strip()
    
    # Check for range (e.g., 2020-2023)
    if '-' in period_str:
        parts = period_str.split('-')
        if len(parts) == 2:
            try:
                start = int(parts[0].strip())
                end = int(parts[1].strip())
                return (start, end)
            except:
                pass
    
    # Check for comma-separated list (e.g., 2020,2021,2022)
    if ',' in period_str:
        years = []
        for y in period_str.split(','):
            y = y.strip()
            if y.isdigit():
                years.append(int(y))
        if years:
            return years
    
    # Single year
    if period_str.isdigit():
        return int(period_str)
    
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

def get_cache_path(issn: str, period_str: str) -> str:
    """Возвращает путь к файлу кэша для ISSN и периода"""
    issn_clean = normalize_issn(issn)
    period_clean = period_str.replace('-', '_').replace(',', '_').replace(' ', '')
    if not os.path.exists('cache'):
        os.makedirs('cache')
    return f"cache/journal_{issn_clean}_{period_clean}.json"

def load_from_cache(cache_path: str) -> Optional[Dict]:
    """Загружает данные из кэша"""
    if not USE_CACHE:
        return None
    
    if os.path.exists(cache_path):
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"✅ Загружено из кэша: {cache_path}")
            return data
        except Exception as e:
            print(f"⚠️ Ошибка загрузки кэша: {e}")
            return None
    return None

def save_to_cache(cache_path: str, data: Dict):
    """Сохраняет данные в кэш"""
    if not USE_CACHE:
        return
    
    try:
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✅ Данные сохранены в кэш: {cache_path}")
    except Exception as e:
        print(f"⚠️ Ошибка сохранения кэша: {e}")

# ============================================
# КЛАССЫ ДЛЯ ДАННЫХ
# ============================================

class Author:
    """Класс для представления автора"""
    def __init__(self, display_name: str, orcid: str = None):
        self.display_name = display_name
        self.orcid = orcid
    
    def to_dict(self) -> Dict:
        return {
            'display_name': self.display_name,
            'orcid': self.orcid
        }

class Publication:
    """Класс для представления публикации"""
    def __init__(self, data: Dict):
        self.id = data.get('id', '')
        self.doi = data.get('doi', '').replace('https://doi.org/', '') if data.get('doi') else ''
        self.title = data.get('title', 'No title')
        self.publication_year = data.get('publication_year')
        self.cited_by_count = data.get('cited_by_count', 0)
        self.journal_name = data.get('journal_name', 'Unknown')
        self.publisher = data.get('publisher', 'Unknown')
        self.is_oa = data.get('is_oa', False)
        self.open_access_status = data.get('open_access_status', 'closed')
        self.authors = data.get('authors', [])
        self.author_orcids = data.get('author_orcids', [])
        self.authors_with_orcids = data.get('authors_with_orcids', [])
        self.affiliations = data.get('affiliations', [])
        self.affiliation_countries = data.get('affiliation_countries', [])
        self.countries = data.get('countries', [])
        self.concepts = data.get('concepts', [])
        self.topics = data.get('topics', [])
        self.fields = data.get('fields', [])
        self.domains = data.get('domains', [])
        self.citations_per_year = data.get('citations_per_year', 0)
        self.raw_data = data
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'doi': self.doi,
            'title': self.title,
            'publication_year': self.publication_year,
            'cited_by_count': self.cited_by_count,
            'journal_name': self.journal_name,
            'publisher': self.publisher,
            'is_oa': self.is_oa,
            'open_access_status': self.open_access_status,
            'authors': self.authors,
            'author_orcids': self.author_orcids,
            'authors_with_orcids': self.authors_with_orcids,
            'affiliations': self.affiliations,
            'affiliation_countries': self.affiliation_countries,
            'countries': self.countries,
            'concepts': self.concepts,
            'topics': self.topics,
            'fields': self.fields,
            'domains': self.domains,
            'citations_per_year': self.citations_per_year
        }

class Citation:
    """Класс для представления цитирования"""
    def __init__(self, data: Dict):
        self.citing_doi = data.get('citing_doi', '')
        self.citing_title = data.get('citing_title', 'No title')
        self.citing_year = data.get('citing_year')
        self.citing_date = data.get('citing_date')
        self.citing_journal = data.get('citing_journal', 'Unknown')
        self.citing_publisher = data.get('citing_publisher', 'Unknown')
        self.citation_lag = data.get('citation_lag', 0)
        self.citing_authors = data.get('citing_authors', [])
        self.citing_countries = data.get('citing_countries', [])
        self.citing_affiliations = data.get('citing_affiliations', [])
        self.citing_topics = data.get('citing_topics', [])
        self.citing_fields = data.get('citing_fields', [])
        self.citing_domains = data.get('citing_domains', [])
        self.citing_concepts = data.get('citing_concepts', [])
    
    def to_dict(self) -> Dict:
        return {
            'citing_doi': self.citing_doi,
            'citing_title': self.citing_title,
            'citing_year': self.citing_year,
            'citing_date': self.citing_date,
            'citing_journal': self.citing_journal,
            'citing_publisher': self.citing_publisher,
            'citation_lag': self.citation_lag,
            'citing_authors': self.citing_authors,
            'citing_countries': self.citing_countries,
            'citing_affiliations': self.citing_affiliations,
            'citing_topics': self.citing_topics,
            'citing_fields': self.citing_fields,
            'citing_domains': self.citing_domains,
            'citing_concepts': self.citing_concepts
        }

# ============================================
# ОСНОВНОЙ КЛАСС ДЛЯ АНАЛИЗА ЖУРНАЛА
# ============================================

class JournalAnalyzer:
    """Класс для анализа журнала по ISSN"""
    
    def __init__(self, issn: str, period: Any, max_workers: int = MAX_WORKERS):
        self.issn = normalize_issn(issn)
        self.period = period
        self.max_workers = max_workers
        self.publications: List[Publication] = []
        self.citations: Dict[str, List[Citation]] = {}  # doi -> list of citations
        self.metrics = {}
        self.lock = Lock()
        
    def normalize_issn(self, issn_str: str) -> str:
        return normalize_issn(issn_str)
    
    def _smart_get(self, url: str, params: Dict = None, retries: int = MAX_RETRIES) -> Optional[Dict]:
        """Smart GET request with retry logic and rate limiting"""
        for attempt in range(retries):
            try:
                with self.lock:
                    time.sleep(random.uniform(0.1, BASE_DELAY))
                
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
                    print(f"⚠️ Попытка {attempt+1}/{retries} ошибка: {str(e)[:100]}")
                time.sleep(1.5 * (2 ** attempt))
        
        return None
    
    def _get_citing_dois(self, oa_id: str) -> List[str]:
        """Get citing DOIs for a publication"""
        citing = []
        cursor = "*"
        base_url = "https://api.openalex.org/works"
        
        for _ in range(10):  # Максимум 10 страниц (2000 цитирований)
            data = self._smart_get(base_url, {
                "filter": f"cites:{oa_id}",
                "per_page": 200,
                "select": "doi,id,title,publication_year,publication_date,primary_location,type,cited_by_count",
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
        
        return citing
    
    def _get_publication_metadata(self, doi: str) -> Optional[Dict]:
        """Get full metadata for a publication by DOI"""
        url = "https://api.openalex.org/works"
        params = {
            "filter": f"doi:{doi}",
            "per_page": 1
        }
        
        data = self._smart_get(url, params)
        if data and data.get("results"):
            return data["results"][0]
        return None
    
    def _parse_publication(self, data: Dict) -> Publication:
        """Parse OpenAlex work data to Publication object"""
        # Extract authors
        authors = []
        author_orcids = []
        authors_with_orcids = []
        
        for auth in data.get('authorships', []):
            if auth.get('author'):
                author_name = auth['author'].get('display_name', '')
                author_orcid = auth['author'].get('orcid', '')
                if author_name:
                    authors.append(author_name)
                    if author_orcid:
                        author_orcids.append(author_orcid)
                    authors_with_orcids.append({
                        'name': author_name,
                        'orcid': author_orcid.replace('https://orcid.org/', '') if author_orcid else None
                    })
        
        # Extract affiliations and countries
        affiliations = []
        affiliation_countries = []
        countries = []
        
        for auth in data.get('authorships', []):
            if auth.get('institutions'):
                for inst in auth['institutions']:
                    affil = inst.get('display_name', '')
                    if affil:
                        affiliations.append(affil)
                        country = extract_country_from_affiliation(affil)
                        if country and country != 'Unknown':
                            affiliation_countries.append(country)
                            countries.append(country)
        
        # Extract topics and concepts
        concepts = []
        topics = []
        fields = []
        domains = []
        
        for concept in data.get('concepts', []):
            concept_name = concept.get('display_name', '')
            concept_level = concept.get('level', 0)
            if concept_name:
                concepts.append(concept_name)
                if concept_level >= 3:
                    domains.append(concept_name)
                elif concept_level == 2:
                    fields.append(concept_name)
                elif concept_level == 1:
                    topics.append(concept_name)
        
        # Get primary topic
        primary_topic = data.get('primary_topic', {})
        if primary_topic:
            if primary_topic.get('display_name'):
                topics.append(primary_topic['display_name'])
            if primary_topic.get('field', {}).get('display_name'):
                fields.append(primary_topic['field']['display_name'])
            if primary_topic.get('domain', {}).get('display_name'):
                domains.append(primary_topic['domain']['display_name'])
        
        # Get OA status
        oa = data.get('open_access', {})
        is_oa = oa.get('is_oa', False)
        oa_status = oa.get('oa_status', 'closed')
        
        # Get journal info
        journal_name = 'Unknown'
        publisher = 'Unknown'
        if data.get('primary_location'):
            source = data['primary_location'].get('source', {})
            journal_name = source.get('display_name', 'Unknown')
            publisher = source.get('host_organization_name') or source.get('publisher', 'Unknown')
        
        # Calculate citations per year
        current_year = datetime.now().year
        pub_year = data.get('publication_year')
        citations_per_year = 0
        if pub_year:
            years_since = current_year - pub_year + 1
            citations_count = data.get('cited_by_count', 0)
            citations_per_year = citations_count / max(years_since, 1)
        
        pub_data = {
            'id': data.get('id', ''),
            'doi': data.get('doi', ''),
            'title': data.get('title', 'No title'),
            'publication_year': pub_year,
            'cited_by_count': data.get('cited_by_count', 0),
            'journal_name': journal_name,
            'publisher': publisher,
            'is_oa': is_oa,
            'open_access_status': oa_status,
            'authors': authors,
            'author_orcids': author_orcids,
            'authors_with_orcids': authors_with_orcids,
            'affiliations': affiliations,
            'affiliation_countries': affiliation_countries,
            'countries': countries,
            'concepts': concepts,
            'topics': topics,
            'fields': fields,
            'domains': domains,
            'citations_per_year': citations_per_year
        }
        
        return Publication(pub_data)
    
    def _parse_citation(self, citing_data: Dict, pub_year: int) -> Citation:
        """Parse citation data from OpenAlex work"""
        # Extract authors
        citing_authors = []
        for auth in citing_data.get('authorships', []):
            if auth.get('author'):
                author_name = auth['author'].get('display_name', '')
                if author_name:
                    citing_authors.append(author_name)
        
        # Extract countries
        citing_countries = []
        citing_affiliations = []
        for auth in citing_data.get('authorships', []):
            if auth.get('institutions'):
                for inst in auth['institutions']:
                    affil = inst.get('display_name', '')
                    if affil:
                        citing_affiliations.append(affil)
                        country = extract_country_from_affiliation(affil)
                        if country and country != 'Unknown':
                            citing_countries.append(country)
        
        # Extract topics and concepts
        citing_topics = []
        citing_fields = []
        citing_domains = []
        citing_concepts = []
        
        for concept in citing_data.get('concepts', []):
            concept_name = concept.get('display_name', '')
            concept_level = concept.get('level', 0)
            if concept_name:
                citing_concepts.append(concept_name)
                if concept_level >= 3:
                    citing_domains.append(concept_name)
                elif concept_level == 2:
                    citing_fields.append(concept_name)
                elif concept_level == 1:
                    citing_topics.append(concept_name)
        
        primary_topic = citing_data.get('primary_topic', {})
        if primary_topic:
            if primary_topic.get('display_name'):
                citing_topics.append(primary_topic['display_name'])
            if primary_topic.get('field', {}).get('display_name'):
                citing_fields.append(primary_topic['field']['display_name'])
            if primary_topic.get('domain', {}).get('display_name'):
                citing_domains.append(primary_topic['domain']['display_name'])
        
        # Get journal info
        citing_journal = 'Unknown'
        citing_publisher = 'Unknown'
        if citing_data.get('primary_location'):
            source = citing_data['primary_location'].get('source', {})
            citing_journal = source.get('display_name', 'Unknown')
            citing_publisher = source.get('host_organization_name') or source.get('publisher', 'Unknown')
        
        citing_year = citing_data.get('publication_year')
        citation_lag = citing_year - pub_year if citing_year and pub_year else 0
        
        citation_data = {
            'citing_doi': citing_data.get('doi', '').replace('https://doi.org/', ''),
            'citing_title': citing_data.get('title', 'No title'),
            'citing_year': citing_year,
            'citing_date': citing_data.get('publication_date', ''),
            'citing_journal': citing_journal,
            'citing_publisher': citing_publisher,
            'citation_lag': citation_lag,
            'citing_authors': citing_authors,
            'citing_countries': citing_countries,
            'citing_affiliations': citing_affiliations,
            'citing_topics': citing_topics,
            'citing_fields': citing_fields,
            'citing_domains': citing_domains,
            'citing_concepts': citing_concepts
        }
        
        return Citation(citation_data)
    
    def _load_publications(self, progress_callback=None) -> int:
        """Load all publications for the journal and period"""
        if SHOW_DEBUG_LOGS:
            print(f"📚 Loading publications for ISSN: {self.issn}, period: {self.period}")
        
        # Build period filter
        if isinstance(self.period, list):
            year_filter = "|".join(f"publication_year:{y}" for y in self.period)
        elif isinstance(self.period, tuple):
            year_filter = f"publication_year:{self.period[0]}-{self.period[1]}"
        else:
            year_filter = f"publication_year:{self.period}"
        
        base_url = "https://api.openalex.org/works"
        cursor = "*"
        total_loaded = 0
        
        while True:
            data = self._smart_get(base_url, {
                "filter": f"primary_location.source.issn:{self.issn},{year_filter}",
                "per_page": 200,
                "cursor": cursor
            })
            
            if not data or not data.get("results"):
                break
            
            for item in data["results"]:
                pub = self._parse_publication(item)
                self.publications.append(pub)
                total_loaded += 1
            
            if progress_callback:
                progress_callback(len(self.publications))
            
            cursor = data.get("meta", {}).get("next_cursor")
            if not cursor:
                break
            
            # Check limit
            if len(self.publications) >= MAX_PUBLICATIONS_TO_ANALYZE:
                if SHOW_DEBUG_LOGS:
                    print(f"⚠️ Reached limit of {MAX_PUBLICATIONS_TO_ANALYZE} publications")
                break
        
        if SHOW_DEBUG_LOGS:
            print(f"✅ Loaded {len(self.publications)} publications")
        
        return len(self.publications)
    
    def _fetch_citations_parallel(self, progress_callback=None) -> int:
        """Fetch citations for all publications in parallel"""
        if SHOW_DEBUG_LOGS:
            print(f"⚡ Fetching citations with {self.max_workers} workers...")
        
        # Collect all publications that have citations
        pubs_to_fetch = []
        for pub in self.publications:
            if pub.cited_by_count > 0 and pub.doi:
                pubs_to_fetch.append((pub.doi, pub.id))
        
        if not pubs_to_fetch:
            if SHOW_DEBUG_LOGS:
                print("ℹ️ No publications with citations found")
            return 0
        
        citing_map = {}
        futures = {}
        total_citations = 0
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            for doi, oa_id in pubs_to_fetch:
                future = executor.submit(self._get_citing_dois, oa_id)
                futures[future] = doi
            
            completed = 0
            for future in as_completed(futures):
                doi = futures[future]
                try:
                    citing_dois = future.result()
                    citing_map[doi] = citing_dois
                    total_citations += len(citing_dois)
                    completed += 1
                    
                    if progress_callback:
                        progress_callback(completed, len(pubs_to_fetch))
                    
                    if SHOW_DEBUG_LOGS and completed % 10 == 0:
                        print(f"  Processed {completed}/{len(pubs_to_fetch)} publications, found {total_citations} citations")
                except Exception as e:
                    if SHOW_DEBUG_LOGS:
                        print(f"⚠️ Error fetching citations for {doi}: {e}")
                    citing_map[doi] = []
        
        # Now fetch metadata for citing publications
        if SHOW_DEBUG_LOGS:
            print(f"📖 Fetching metadata for {total_citations} citing publications...")
        
        # Collect all citing DOIs
        all_citing_dois = []
        for doi, citing_dois in citing_map.items():
            all_citing_dois.extend(citing_dois)
        
        # Remove duplicates
        unique_citing_dois = list(set(all_citing_dois))
        if SHOW_DEBUG_LOGS:
            print(f"  Unique citing DOIs: {len(unique_citing_dois)}")
        
        # Fetch metadata for each citing DOI
        citing_metadata_map = {}
        citing_batches = list(chunks(unique_citing_dois, BATCH_SIZE))
        
        for batch_idx, batch in enumerate(citing_batches):
            if SHOW_DEBUG_LOGS and batch_idx % 10 == 0:
                print(f"  Batch {batch_idx+1}/{len(citing_batches)}")
            
            for doi in batch:
                metadata = self._get_publication_metadata(doi)
                if metadata:
                    citing_metadata_map[doi] = metadata
                time.sleep(DELAY_BETWEEN_BATCHES)
        
        if SHOW_DEBUG_LOGS:
            print(f"✅ Retrieved metadata for {len(citing_metadata_map)} citing publications")
        
        # Build citation objects
        self.citations = {}
        for pub in self.publications:
            if pub.doi in citing_map:
                citation_list = []
                for citing_doi in citing_map[pub.doi]:
                    if citing_doi in citing_metadata_map:
                        citing_data = citing_metadata_map[citing_doi]
                        citation = self._parse_citation(citing_data, pub.publication_year)
                        citation_list.append(citation)
                if citation_list:
                    self.citations[pub.doi] = citation_list
        
        total_citations_found = sum(len(c) for c in self.citations.values())
        if SHOW_DEBUG_LOGS:
            print(f"✅ Total citations found: {total_citations_found}")
        
        return total_citations_found
    
    def analyze(self, progress_callback=None) -> Dict:
        """Run complete analysis of the journal"""
        if SHOW_DEBUG_LOGS:
            print(f"🚀 Starting analysis for {self.issn}")
        
        # Step 1: Load publications
        if progress_callback:
            progress_callback(0, "loading_publications")
        pub_count = self._load_publications()
        
        if pub_count == 0:
            return {'error': 'No publications found'}
        
        # Step 2: Fetch citations
        if progress_callback:
            progress_callback(30, "fetching_citations")
        
        def citation_progress(current, total):
            if progress_callback:
                progress = 30 + (current / total) * 40
                progress_callback(progress, "fetching_citations")
        
        citation_count = self._fetch_citations_parallel(citation_progress)
        
        # Step 3: Calculate metrics
        if progress_callback:
            progress_callback(70, "calculating_metrics")
        
        self._calculate_metrics()
        
        if progress_callback:
            progress_callback(100, "complete")
        
        return self.metrics
    
    def _calculate_metrics(self):
        """Calculate all metrics for the journal"""
        if SHOW_DEBUG_LOGS:
            print("📊 Calculating metrics...")
        
        pubs = self.publications
        total_pubs = len(pubs)
        
        if total_pubs == 0:
            self.metrics = {'total_publications': 0}
            return
        
        # Basic metrics
        total_citations = sum(p.cited_by_count for p in pubs)
        citations_list = [p.cited_by_count for p in pubs]
        avg_citations = total_citations / total_pubs if total_pubs > 0 else 0
        
        # h-index
        citations_sorted = sorted([c for c in citations_list if c > 0], reverse=True)
        h_index = 0
        for i, c in enumerate(citations_sorted, 1):
            if c >= i:
                h_index = i
            else:
                break
        
        # g-index
        total_citations_sorted = 0
        g_index = 0
        for i, c in enumerate(citations_sorted, 1):
            total_citations_sorted += c
            if total_citations_sorted >= i**2:
                g_index = i
        
        # i10-index, i100-index
        i10_index = sum(1 for c in citations_list if c >= 10)
        i100_index = sum(1 for c in citations_list if c >= 100)
        
        # Open Access breakdown
        oa_statuses = {
            'gold': 0,
            'hybrid': 0,
            'green': 0,
            'bronze': 0,
            'closed': 0,
            'unknown': 0
        }
        for p in pubs:
            status = p.open_access_status.lower()
            if status in oa_statuses:
                oa_statuses[status] += 1
            else:
                oa_statuses['unknown'] += 1
        
        # Authors
        all_authors = []
        author_counter = Counter()
        author_orcid_counter = Counter()
        
        for p in pubs:
            for author in p.authors:
                all_authors.append(author)
                author_counter[author] += 1
            for orcid in p.author_orcids:
                if orcid:
                    author_orcid_counter[orcid] += 1
        
        unique_authors = len(author_counter)
        
        # Affiliations
        all_affiliations = []
        affiliation_counter = Counter()
        for p in pubs:
            for aff in p.affiliations:
                all_affiliations.append(aff)
                affiliation_counter[aff] += 1
        unique_affiliations = len(affiliation_counter)
        
        # Countries
        all_countries = []
        country_counter = Counter()
        for p in pubs:
            for country in p.countries:
                if country and country != 'Unknown':
                    all_countries.append(country)
                    country_counter[country] += 1
        unique_countries = len(country_counter)
        
        # Average metrics
        avg_authors = sum(len(p.authors) for p in pubs) / total_pubs if total_pubs > 0 else 0
        avg_affiliations = sum(len(p.affiliations) for p in pubs) / total_pubs if total_pubs > 0 else 0
        avg_countries = sum(len(set(p.countries)) for p in pubs) / total_pubs if total_pubs > 0 else 0
        
        # International collaboration rate
        international_count = 0
        for p in pubs:
            if len(set(p.countries)) > 1:
                international_count += 1
        international_rate = international_count / total_pubs if total_pubs > 0 else 0
        
        # Active years
        years = [p.publication_year for p in pubs if p.publication_year]
        active_years = len(set(years)) if years else 0
        
        # Years distribution
        year_counts = Counter(years)
        
        # Citation dynamics by year
        citation_dynamics = defaultdict(lambda: defaultdict(int))
        for pub in pubs:
            if pub.doi in self.citations:
                for citation in self.citations[pub.doi]:
                    if pub.publication_year and citation.citing_year:
                        citation_dynamics[pub.publication_year][citation.citing_year] += 1
        
        # Cumulative citations
        cumulative_citations = defaultdict(int)
        for pub in pubs:
            if pub.doi in self.citations:
                for citation in self.citations[pub.doi]:
                    if citation.citing_year:
                        cumulative_citations[citation.citing_year] += 1
        
        # Sort cumulative citations by year
        cumulative_sorted = sorted(cumulative_citations.items())
        cumulative_values = []
        running_total = 0
        for year, count in cumulative_sorted:
            running_total += count
            cumulative_values.append((year, running_total))
        
        # Most cited publications
        most_cited = sorted(pubs, key=lambda x: x.cited_by_count, reverse=True)[:15]
        most_cited_data = []
        for p in most_cited:
            most_cited_data.append({
                'title': p.title,
                'year': p.publication_year,
                'citations': p.cited_by_count,
                'citations_per_year': p.citations_per_year,
                'authors': ', '.join(p.authors[:3]) + (' + more' if len(p.authors) > 3 else ''),
                'doi': p.doi
            })
        
        # Citing works analysis
        all_citing_authors = []
        all_citing_affiliations = []
        all_citing_countries = []
        all_citing_journals = []
        all_citing_publishers = []
        all_citing_topics = []
        all_citing_fields = []
        all_citing_domains = []
        all_citing_concepts = []
        
        citing_author_counter = Counter()
        citing_affiliation_counter = Counter()
        citing_country_counter = Counter()
        citing_journal_counter = Counter()
        citing_publisher_counter = Counter()
        
        total_citing_works = 0
        
        for pub in pubs:
            if pub.doi in self.citations:
                for citation in self.citations[pub.doi]:
                    total_citing_works += 1
                    
                    for author in citation.citing_authors:
                        all_citing_authors.append(author)
                        citing_author_counter[author] += 1
                    
                    for aff in citation.citing_affiliations:
                        all_citing_affiliations.append(aff)
                        citing_affiliation_counter[aff] += 1
                    
                    for country in citation.citing_countries:
                        if country and country != 'Unknown':
                            all_citing_countries.append(country)
                            citing_country_counter[country] += 1
                    
                    if citation.citing_journal and citation.citing_journal != 'Unknown':
                        all_citing_journals.append(citation.citing_journal)
                        citing_journal_counter[citation.citing_journal] += 1
                    
                    if citation.citing_publisher and citation.citing_publisher != 'Unknown':
                        all_citing_publishers.append(citation.citing_publisher)
                        citing_publisher_counter[citation.citing_publisher] += 1
                    
                    all_citing_topics.extend(citation.citing_topics)
                    all_citing_fields.extend(citation.citing_fields)
                    all_citing_domains.extend(citation.citing_domains)
                    all_citing_concepts.extend(citation.citing_concepts)
        
        # Topics analysis
        topic_counter = Counter()
        for pub in pubs:
            for topic in pub.topics:
                if topic:
                    topic_counter[topic] += 1
        
        citing_topic_counter = Counter()
        for pub in pubs:
            if pub.doi in self.citations:
                for citation in self.citations[pub.doi]:
                    for topic in citation.citing_topics:
                        if topic:
                            citing_topic_counter[topic] += 1
        
        # Topic metrics
        topic_metrics = {}
        all_topics = set(topic_counter.keys()) | set(citing_topic_counter.keys())
        
        for topic in all_topics:
            analyzed_count = topic_counter.get(topic, 0)
            citing_count = citing_topic_counter.get(topic, 0)
            
            # Normalized counts (per 1000 publications)
            analyzed_norm = (analyzed_count / total_pubs) * 1000 if total_pubs > 0 else 0
            citing_norm = (citing_count / total_citing_works) * 1000 if total_citing_works > 0 else 0
            
            # First year and peak year
            first_year = None
            peak_year = None
            recent_5_count = 0
            
            # Find years for this topic
            topic_years = []
            for pub in pubs:
                if topic in pub.topics and pub.publication_year:
                    topic_years.append(pub.publication_year)
            
            if topic_years:
                first_year = min(topic_years)
                peak_year = max(set(topic_years), key=topic_years.count)
                current_year = datetime.now().year
                recent_5_count = sum(1 for y in topic_years if y >= current_year - 5)
            
            topic_metrics[topic] = {
                'analyzed_count': analyzed_count,
                'citing_count': citing_count,
                'analyzed_norm_count': analyzed_norm,
                'citing_norm_count': citing_norm,
                'total_norm_count': analyzed_norm + citing_norm,
                'first_year': first_year,
                'peak_year': peak_year,
                'recent_5_years_count': recent_5_count
            }
        
        # Top topics by total norm count
        top_topics = sorted(topic_metrics.items(), 
                           key=lambda x: x[1]['total_norm_count'], 
                           reverse=True)[:10]
        
        # Top cited topics, subtopics, fields, domains, concepts
        topic_citations = defaultdict(int)
        subtopic_citations = defaultdict(int)
        field_citations = defaultdict(int)
        domain_citations = defaultdict(int)
        concept_citations = defaultdict(int)
        
        for pub in pubs:
            if pub.doi in self.citations:
                for citation in self.citations[pub.doi]:
                    for topic in citation.citing_topics:
                        topic_citations[topic] += 1
                    for field in citation.citing_fields:
                        field_citations[field] += 1
                    for domain in citation.citing_domains:
                        domain_citations[domain] += 1
                    for concept in citation.citing_concepts:
                        concept_citations[concept] += 1
        
        top_cited_topics = sorted(topic_citations.items(), key=lambda x: x[1], reverse=True)[:10]
        top_cited_fields = sorted(field_citations.items(), key=lambda x: x[1], reverse=True)[:10]
        top_cited_domains = sorted(domain_citations.items(), key=lambda x: x[1], reverse=True)[:10]
        top_cited_concepts = sorted(concept_citations.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Detailed citations
        detailed_citations = {}
        for pub in pubs:
            if pub.doi in self.citations and self.citations[pub.doi]:
                citation_list = []
                for citation in self.citations[pub.doi]:
                    citation_list.append({
                        'citing_title': citation.citing_title,
                        'citing_year': citation.citing_year,
                        'citing_date': citation.citing_date,
                        'citing_journal': citation.citing_journal,
                        'citing_publisher': citation.citing_publisher,
                        'citing_doi': citation.citing_doi,
                        'citation_lag': citation.citation_lag,
                        'citing_authors': citation.citing_authors,
                        'citing_countries': citation.citing_countries,
                        'citing_topics': citation.citing_topics
                    })
                
                detailed_citations[pub.doi] = {
                    'title': pub.title,
                    'year': pub.publication_year,
                    'doi': pub.doi,
                    'total_citations': len(citation_list),
                    'citations': citation_list
                }
        
        # Author analysis with ORCID
        author_analysis = []
        for author, count in author_counter.most_common(100):
            orcids = []
            for p in pubs:
                if author in p.authors:
                    for author_data in p.authors_with_orcids:
                        if author_data.get('name') == author and author_data.get('orcid'):
                            orcids.append(author_data['orcid'])
            
            # Get affiliations for this author
            author_affiliations = []
            author_countries_list = []
            for p in pubs:
                if author in p.authors:
                    author_affiliations.extend(p.affiliations)
                    author_countries_list.extend(p.countries)
            
            # Get citations for this author's publications
            author_citations = 0
            for p in pubs:
                if author in p.authors:
                    author_citations += p.cited_by_count
            
            author_analysis.append({
                'name': author,
                'orcid': orcids[0] if orcids else None,
                'publications': count,
                'citations': author_citations,
                'affiliations': list(set(author_affiliations))[:3],
                'countries': list(set(author_countries_list))[:3]
            })
        
        # Sort by publications count
        author_analysis = sorted(author_analysis, key=lambda x: x['publications'], reverse=True)
        
        # Top affiliations
        top_affiliations = affiliation_counter.most_common(20)
        
        # Collaboration couples (country pairs)
        country_pairs = Counter()
        for p in pubs:
            countries = set(p.countries)
            if len(countries) >= 2:
                for c1, c2 in combinations(sorted(countries), 2):
                    if c1 and c2 and c1 != 'Unknown' and c2 != 'Unknown':
                        country_pairs[f"{c1} - {c2}"] += 1
        
        # Build final metrics
        self.metrics = {
            'total_publications': total_pubs,
            'total_citations': total_citations,
            'h_index': h_index,
            'g_index': g_index,
            'i10_index': i10_index,
            'i100_index': i100_index,
            'avg_citations': avg_citations,
            'open_access_breakdown': oa_statuses,
            'active_years': active_years,
            'unique_authors': unique_authors,
            'unique_affiliations': unique_affiliations,
            'unique_countries': unique_countries,
            'avg_authors_per_paper': avg_authors,
            'avg_affiliations_per_paper': avg_affiliations,
            'avg_countries_per_paper': avg_countries,
            'international_collaboration_rate': international_rate,
            'year_counts': dict(year_counts),
            'citation_dynamics': dict(citation_dynamics),
            'cumulative_citations': cumulative_values,
            'most_cited': most_cited_data,
            'total_citing_works': total_citing_works,
            'unique_citing_authors': len(citing_author_counter),
            'unique_citing_affiliations': len(citing_affiliation_counter),
            'unique_citing_countries': len(citing_country_counter),
            'unique_citing_journals': len(citing_journal_counter),
            'unique_citing_publishers': len(citing_publisher_counter),
            'top_citing_authors': citing_author_counter.most_common(20),
            'top_citing_affiliations': citing_affiliation_counter.most_common(20),
            'top_citing_countries': citing_country_counter.most_common(20),
            'top_citing_journals': citing_journal_counter.most_common(20),
            'top_citing_publishers': citing_publisher_counter.most_common(20),
            'topic_metrics': topic_metrics,
            'top_topics': top_topics,
            'top_cited_topics': top_cited_topics,
            'top_cited_fields': top_cited_fields,
            'top_cited_domains': top_cited_domains,
            'top_cited_concepts': top_cited_concepts,
            'author_analysis': author_analysis,
            'top_affiliations': top_affiliations,
            'country_pairs': dict(country_pairs.most_common(50)),
            'detailed_citations': detailed_citations,
            'all_publications': pubs
        }
        
        if SHOW_DEBUG_LOGS:
            print("✅ Metrics calculation complete")
        
        return self.metrics

# ============================================
# ФУНКЦИИ ДЛЯ ГЕНЕРАЦИИ HTML ОТЧЕТА
# ============================================

def generate_journal_html_report(metrics: Dict, issn: str, period: str, 
                                 primary_color: str = '#667eea', 
                                 secondary_color: str = '#f39c12',
                                 lang: str = 'en') -> str:
    """Generate HTML report for journal analysis"""
    
    def t(key: str, **kwargs) -> str:
        return translate(key, lang, **kwargs)
    
    primary = primary_color
    secondary = secondary_color
    
    # Extract metrics
    total_pubs = metrics.get('total_publications', 0)
    total_citations = metrics.get('total_citations', 0)
    h_index = metrics.get('h_index', 0)
    g_index = metrics.get('g_index', 0)
    i10_index = metrics.get('i10_index', 0)
    i100_index = metrics.get('i100_index', 0)
    avg_citations = metrics.get('avg_citations', 0)
    active_years = metrics.get('active_years', 0)
    unique_authors = metrics.get('unique_authors', 0)
    unique_affiliations = metrics.get('unique_affiliations', 0)
    unique_countries = metrics.get('unique_countries', 0)
    avg_authors = metrics.get('avg_authors_per_paper', 0)
    avg_affiliations = metrics.get('avg_affiliations_per_paper', 0)
    avg_countries = metrics.get('avg_countries_per_paper', 0)
    international_rate = metrics.get('international_collaboration_rate', 0)
    total_citing_works = metrics.get('total_citing_works', 0)
    unique_citing_authors = metrics.get('unique_citing_authors', 0)
    unique_citing_affiliations = metrics.get('unique_citing_affiliations', 0)
    unique_citing_countries = metrics.get('unique_citing_countries', 0)
    unique_citing_journals = metrics.get('unique_citing_journals', 0)
    unique_citing_publishers = metrics.get('unique_citing_publishers', 0)
    
    # Open Access breakdown
    oa_breakdown = metrics.get('open_access_breakdown', {})
    oa_labels = {
        'gold': t('gold'),
        'hybrid': t('hybrid'),
        'green': t('green'),
        'bronze': t('bronze'),
        'closed': t('closed'),
        'unknown': t('unknown_oa')
    }
    
    # Build OA breakdown HTML
    oa_html = ""
    for status, count in oa_breakdown.items():
        if status in oa_labels:
            oa_html += f"""
            <div class="metric-card" style="min-width: 100px;">
                <div class="metric-value">{count}</div>
                <div class="metric-label">{oa_labels[status]}</div>
            </div>
            """
    
    # Author analysis table
    author_analysis = metrics.get('author_analysis', [])
    author_table_rows = ""
    for i, author in enumerate(author_analysis[:20], 1):
        orcid_link = f'<a href="https://orcid.org/{author["orcid"]}" target="_blank">{author["orcid"]}</a>' if author.get('orcid') else '-'
        author_table_rows += f"""
        <tr>
            <td>{i}</td>
            <td>{html.escape(author['name'])}</td>
            <td>{orcid_link}</td>
            <td>{', '.join([html.escape(a) for a in author.get('affiliations', [])[:3]])}</td>
            <td>{', '.join(author.get('countries', []))}</td>
            <td>{author['publications']}</td>
            <td>{author['citations']}</td>
        </tr>
        """
    
    # Top affiliations
    top_affiliations = metrics.get('top_affiliations', [])
    affil_rows = ""
    for affil, count in top_affiliations[:20]:
        affil_rows += f"""
        <tr>
            <td>{html.escape(affil)}</td>
            <td>{count}</td>
        </tr>
        """
    
    # Geographic analysis - unique countries per publication
    countries_per_pub = []
    all_pubs = metrics.get('all_publications', [])
    for pub in all_pubs:
        countries = list(set(pub.countries))
        if countries:
            countries_per_pub.append({
                'title': pub.title[:50] + '...' if len(pub.title) > 50 else pub.title,
                'year': pub.publication_year,
                'countries': ', '.join(countries),
                'count': len(countries)
            })
    
    # Sort by number of countries
    countries_per_pub = sorted(countries_per_pub, key=lambda x: x['count'], reverse=True)[:20]
    
    countries_per_pub_rows = ""
    for item in countries_per_pub:
        countries_per_pub_rows += f"""
        <tr>
            <td>{html.escape(item['title'])}</td>
            <td>{item['year']}</td>
            <td>{html.escape(item['countries'])}</td>
            <td>{item['count']}</td>
        </tr>
        """
    
    # Authors per country
    author_country_counter = Counter()
    for pub in all_pubs:
        for author in pub.authors:
            if author and pub.countries:
                # Assign the first country of the publication to the author
                author_country_counter[pub.countries[0]] += 1
    
    authors_per_country_rows = ""
    for country, count in author_country_counter.most_common(30):
        authors_per_country_rows += f"""
        <tr>
            <td>{country if country and country != 'Unknown' else 'Unknown'}</td>
            <td>{count}</td>
        </tr>
        """
    
    # Collaboration patterns
    single_country = 0
    international_pubs = 0
    for pub in all_pubs:
        if len(set(pub.countries)) <= 1:
            single_country += 1
        else:
            international_pubs += 1
    
    # Collaboration couples
    country_pairs = metrics.get('country_pairs', {})
    country_pairs_rows = ""
    for pair, count in list(country_pairs.items())[:30]:
        country_pairs_rows += f"""
        <tr>
            <td>{html.escape(pair)}</td>
            <td>{count}</td>
        </tr>
        """
    
    # Citation dynamics by year
    citation_dynamics = metrics.get('citation_dynamics', {})
    dynamics_rows = ""
    for pub_year, citing_years in sorted(citation_dynamics.items()):
        for citing_year, count in sorted(citing_years.items()):
            dynamics_rows += f"""
            <tr>
                <td>{pub_year}</td>
                <td>{citing_year}</td>
                <td>{count}</td>
            </tr>
            """
    
    # Cumulative citations
    cumulative = metrics.get('cumulative_citations', [])
    cumulative_rows = ""
    for year, total in cumulative:
        cumulative_rows += f"""
        <tr>
            <td>{year}</td>
            <td>{total}</td>
        </tr>
        """
    
    # Citation network heatmap
    heatmap_rows = ""
    all_years = sorted(set(citation_dynamics.keys()) | set().union(*[set(citing_years.keys()) for citing_years in citation_dynamics.values()]))
    
    for pub_year in sorted(citation_dynamics.keys()):
        row = f"<tr><td>{pub_year}</td>"
        for citing_year in all_years:
            if citing_year >= pub_year:
                count = citation_dynamics.get(pub_year, {}).get(citing_year, 0)
                # Calculate color intensity based on count
                max_count = max([citation_dynamics.get(py, {}).get(cy, 0) for py in citation_dynamics for cy in citation_dynamics[py]]) if citation_dynamics else 1
                intensity = min(count / max_count, 1) if max_count > 0 else 0
                
                # Create gradient color
                r1, g1, b1 = hex_to_rgb(primary)
                r2, g2, b2 = hex_to_rgb(secondary)
                
                r = int(r1 + (r2 - r1) * intensity)
                g = int(g1 + (g2 - g1) * intensity)
                b = int(b1 + (b2 - b1) * intensity)
                
                bg_color = f"rgb({r},{g},{b})"
                text_color = get_contrast_color(rgb_to_hex((r, g, b)))
                
                row += f'<td style="background-color: {bg_color}; color: {text_color}; padding: 4px; text-align: center;">{count if count > 0 else "-"}</td>'
            else:
                row += '<td style="background-color: #f5f5f5; color: #ccc; padding: 4px; text-align: center;">-</td>'
        row += "</tr>"
        heatmap_rows += row
    
    # Most cited publications
    most_cited = metrics.get('most_cited', [])
    most_cited_rows = ""
    for i, pub in enumerate(most_cited[:15], 1):
        most_cited_rows += f"""
        <tr>
            <td>{i}</td>
            <td>{html.escape(pub['title'])}</td>
            <td>{pub['year']}</td>
            <td>{pub['citations']}</td>
            <td>{pub['citations_per_year']:.1f}</td>
            <td>{html.escape(pub['authors'])}</td>
            <td><a href="https://doi.org/{pub['doi']}" target="_blank">{pub['doi']}</a></td>
        </tr>
        """
    
    # Citing works analysis - top citing authors
    top_citing_authors = metrics.get('top_citing_authors', [])
    citing_authors_rows = ""
    for i, (author, count) in enumerate(top_citing_authors[:20], 1):
        citing_authors_rows += f"""
        <tr>
            <td>{i}</td>
            <td>{html.escape(author)}</td>
            <td>{count}</td>
        </tr>
        """
    
    # Top citing affiliations
    top_citing_affiliations = metrics.get('top_citing_affiliations', [])
    citing_affil_rows = ""
    for i, (affil, count) in enumerate(top_citing_affiliations[:20], 1):
        citing_affil_rows += f"""
        <tr>
            <td>{i}</td>
            <td>{html.escape(affil)}</td>
            <td>{count}</td>
        </tr>
        """
    
    # Top citing countries
    top_citing_countries = metrics.get('top_citing_countries', [])
    citing_country_rows = ""
    for i, (country, count) in enumerate(top_citing_countries[:20], 1):
        citing_country_rows += f"""
        <tr>
            <td>{i}</td>
            <td>{country if country and country != 'Unknown' else 'Unknown'}</td>
            <td>{count}</td>
        </tr>
        """
    
    # Top citing journals
    top_citing_journals = metrics.get('top_citing_journals', [])
    citing_journal_rows = ""
    for i, (journal, count) in enumerate(top_citing_journals[:20], 1):
        citing_journal_rows += f"""
        <tr>
            <td>{i}</td>
            <td>{html.escape(journal)}</td>
            <td>{count}</td>
        </tr>
        """
    
    # Top citing publishers
    top_citing_publishers = metrics.get('top_citing_publishers', [])
    citing_publisher_rows = ""
    for i, (publisher, count) in enumerate(top_citing_publishers[:20], 1):
        citing_publisher_rows += f"""
        <tr>
            <td>{i}</td>
            <td>{html.escape(publisher)}</td>
            <td>{count}</td>
        </tr>
        """
    
    # Topics analysis
    topic_metrics = metrics.get('topic_metrics', {})
    top_topics = metrics.get('top_topics', [])
    topics_rows = ""
    for topic, data in top_topics:
        topics_rows += f"""
        <tr>
            <td>{html.escape(topic)}</td>
            <td>{data['analyzed_count']}</td>
            <td>{data['citing_count']}</td>
            <td>{data['analyzed_norm_count']:.3f}</td>
            <td>{data['citing_norm_count']:.3f}</td>
            <td>{data['total_norm_count']:.3f}</td>
            <td>{data['first_year'] or '-'}</td>
            <td>{data['peak_year'] or '-'}</td>
            <td>{data['recent_5_years_count']}</td>
        </tr>
        """
    
    # Top cited topics, fields, domains, concepts
    top_cited_topics = metrics.get('top_cited_topics', [])
    top_cited_fields = metrics.get('top_cited_fields', [])
    top_cited_domains = metrics.get('top_cited_domains', [])
    top_cited_concepts = metrics.get('top_cited_concepts', [])
    
    top_cited_rows = ""
    for i, (name, count) in enumerate(top_cited_topics[:10], 1):
        top_cited_rows += f"""
        <tr>
            <td>{i}</td>
            <td>{html.escape(name)}</td>
            <td>{count}</td>
        </tr>
        """
    
    top_cited_fields_rows = ""
    for i, (name, count) in enumerate(top_cited_fields[:10], 1):
        top_cited_fields_rows += f"""
        <tr>
            <td>{i}</td>
            <td>{html.escape(name)}</td>
            <td>{count}</td>
        </tr>
        """
    
    top_cited_domains_rows = ""
    for i, (name, count) in enumerate(top_cited_domains[:10], 1):
        top_cited_domains_rows += f"""
        <tr>
            <td>{i}</td>
            <td>{html.escape(name)}</td>
            <td>{count}</td>
        </tr>
        """
    
    top_cited_concepts_rows = ""
    for i, (name, count) in enumerate(top_cited_concepts[:10], 1):
        top_cited_concepts_rows += f"""
        <tr>
            <td>{i}</td>
            <td>{html.escape(name)}</td>
            <td>{count}</td>
        </tr>
        """
    
    # Detailed citations
    detailed_citations = metrics.get('detailed_citations', {})
    detailed_citations_html = ""
    for pub_id, data in detailed_citations.items():
        pub_id_clean = pub_id.replace('https://doi.org/', '').replace('/', '_')
        citations_html = ""
        for cite in data['citations']:
            citations_html += f"""
            <div class="citation-detail">
                <div><strong>{html.escape(cite['citing_title'])}</strong></div>
                <div class="cite-meta">
                    <strong>{t('citing_journal')}:</strong> {html.escape(cite['citing_journal'])} | 
                    <strong>{t('citing_year')}:</strong> {cite['citing_year']} | 
                    <strong>{t('citing_date')}:</strong> {cite['citing_date']} |
                    <strong>{t('citation_lag')}:</strong> {cite['citation_lag']} years
                </div>
                <div class="cite-meta">
                    <strong>{t('authors')}:</strong> {', '.join([html.escape(a) for a in cite['citing_authors'][:5]])}{' + more' if len(cite['citing_authors']) > 5 else ''} |
                    <strong>{t('countries')}:</strong> {', '.join(cite['citing_countries'][:5])}{' + more' if len(cite['citing_countries']) > 5 else ''} |
                    <strong>{t('topics')}:</strong> {', '.join([html.escape(t) for t in cite['citing_topics'][:5]])}{' + more' if len(cite['citing_topics']) > 5 else ''}
                </div>
                <div class="cite-meta">
                    <a href="https://doi.org/{cite['citing_doi']}" target="_blank" class="doi-link">DOI: {cite['citing_doi']}</a>
                </div>
            </div>
            """
        
        detailed_citations_html += f"""
        <div class="collapser" onclick="toggleCitations('{pub_id_clean}')">
            <strong>{html.escape(data['title'])}</strong>
            <span class="badge badge-info">{data['year']}</span>
            <span class="citation-count">{data['total_citations']} citations</span>
            <span style="font-size: 12px; color: #666; margin-left: 10px;">DOI: {data['doi']}</span>
            <span style="float: right; font-size: 12px; color: #666;">Click to toggle citations</span>
        </div>
        <div id="citations_{pub_id_clean}" style="display: none;">
            {citations_html}
        </div>
        """
    
    # All publications table
    all_pubs = metrics.get('all_publications', [])
    years_list = sorted(set([p.publication_year for p in all_pubs if p.publication_year]), reverse=True)
    
    publications_rows = ""
    for i, pub in enumerate(all_pubs, 1):
        publications_rows += f"""
        <tr data-year="{pub.publication_year}" 
            data-authors="{','.join([a.lower() for a in pub.authors])}" 
            data-affiliations="{','.join([a.lower() for a in pub.affiliations])}"
            data-citations="{pub.cited_by_count}" 
            data-title="{pub.title.lower()}" 
            data-doi="{pub.doi.lower()}">
            <td>{i}</td>
            <td class="word-wrap">{html.escape(pub.title)}</td>
            <td>{pub.publication_year}</td>
            <td>{', '.join([html.escape(a) for a in pub.authors[:5]])}{' + more' if len(pub.authors) > 5 else ''}</td>
            <td>{', '.join([html.escape(a) for a in pub.affiliations[:3]])}{' + more' if len(pub.affiliations) > 3 else ''}</td>
            <td><span class="citation-count">{pub.cited_by_count}</span></td>
            <td>{pub.citations_per_year:.1f}</td>
            <td><a href="https://doi.org/{pub.doi}" target="_blank" class="doi-link">{pub.doi}</a></td>
        </tr>
        """
    
    # Year options for filter
    year_options = ""
    for year in years_list:
        year_options += f'<option value="{year}">{year}</option>'
    
    # Build complete HTML
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
                padding: 25px 15px;
                overflow-y: auto;
                z-index: 1000;
                scrollbar-width: thin;
                scrollbar-color: rgba(255,255,255,0.3) transparent;
            }}
            .sidebar::-webkit-scrollbar {{
                width: 5px;
            }}
            .sidebar::-webkit-scrollbar-thumb {{
                background: rgba(255,255,255,0.3);
                border-radius: 10px;
            }}
            .sidebar h2 {{
                margin-bottom: 20px;
                font-size: 20px;
                font-weight: 600;
                color: white;
                text-align: center;
                border-bottom: 2px solid rgba(255,255,255,0.2);
                padding-bottom: 12px;
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
            }}
            .sidebar a:hover {{
                background: rgba(255,255,255,0.2);
                transform: translateX(5px);
            }}
            .sidebar .nav-level1 {{
                font-weight: 600;
                padding-left: 8px;
                margin-top: 8px;
                border-left: 3px solid rgba(255,255,255,0.3);
            }}
            .sidebar .nav-level2 {{
                padding-left: 30px;
                font-size: 13px;
                font-weight: 400;
                opacity: 0.9;
            }}
            .sidebar .nav-level2:hover {{
                opacity: 1;
            }}
            .main-content {{
                margin-left: 280px;
                padding: 30px 40px;
            }}
            .header {{
                background: linear-gradient(135deg, {primary} 0%, {secondary} 100%);
                color: white;
                padding: 30px;
                border-radius: 15px;
                margin-bottom: 30px;
                text-align: center;
            }}
            .header h1 {{
                color: white;
                border-bottom: none;
                margin: 0;
                font-size: 30px;
            }}
            .header .subtitle {{
                opacity: 0.9;
                margin-top: 8px;
                font-size: 16px;
            }}
            .header .date {{
                opacity: 0.8;
                margin-top: 10px;
                font-size: 14px;
            }}
            .section {{
                background: white;
                border-radius: 15px;
                padding: 25px;
                margin-bottom: 30px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                border: 1px solid #e8e8e8;
            }}
            .section-title {{
                font-size: 22px;
                font-weight: 600;
                margin-bottom: 20px;
                padding-bottom: 12px;
                border-bottom: 3px solid {primary};
                display: flex;
                align-items: center;
                gap: 12px;
            }}
            .section-title .icon {{
                font-size: 24px;
            }}
            .sub-section-title {{
                font-size: 18px;
                font-weight: 600;
                margin: 15px 0 12px 0;
                padding-bottom: 8px;
                border-bottom: 2px solid {secondary}40;
                color: {primary};
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
                transform: translateY(-3px);
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }}
            .metric-value {{
                font-size: 26px;
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
            .metric-card.primary {{
                border-left-color: {primary};
            }}
            .metric-card.secondary {{
                border-left-color: {secondary};
            }}
            .badge {{
                display: inline-block;
                padding: 3px 10px;
                border-radius: 15px;
                font-size: 11px;
                font-weight: 600;
                margin: 2px;
            }}
            .badge-success {{ background: #d4edda; color: #155724; }}
            .badge-warning {{ background: #fff3cd; color: #856404; }}
            .badge-danger {{ background: #f8d7da; color: #721c24; }}
            .badge-info {{ background: #d1ecf1; color: #0c5460; }}
            .badge-primary {{ background: {primary}20; color: {primary}; }}
            .citation-count {{
                font-weight: bold;
                color: {primary};
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 15px 0;
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
                border-bottom: 1px solid #e8e8e8;
                vertical-align: top;
            }}
            tr:hover {{
                background-color: #f8f9fa;
            }}
            tr:nth-child(even) {{
                background-color: #fafafa;
            }}
            tr:nth-child(even):hover {{
                background-color: #f0f0f0;
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
            .collapser {{
                background: #f8f9fa;
                padding: 12px 15px;
                margin: 8px 0;
                border-radius: 8px;
                cursor: pointer;
                border-left: 3px solid {primary};
                transition: background 0.3s;
                display: flex;
                flex-wrap: wrap;
                align-items: center;
                gap: 8px;
            }}
            .collapser:hover {{
                background: #e9ecef;
            }}
            .citation-detail {{
                background: #f8f9fa;
                padding: 12px 15px;
                margin: 8px 0 8px 20px;
                border-radius: 6px;
                border-left: 3px solid {secondary};
            }}
            .citation-detail .cite-meta {{
                font-size: 13px;
                color: #555;
                margin-top: 5px;
                word-wrap: break-word;
            }}
            .filter-section {{
                background: #f8f9fa;
                padding: 15px 20px;
                border-radius: 8px;
                margin-bottom: 20px;
                border: 1px solid #e8e8e8;
            }}
            .filter-row {{
                display: flex;
                flex-wrap: wrap;
                gap: 15px;
                align-items: center;
            }}
            .filter-row > div {{
                display: flex;
                align-items: center;
                gap: 8px;
                flex-wrap: wrap;
            }}
            .filter-row label {{
                font-size: 13px;
                font-weight: 500;
                color: #555;
                white-space: nowrap;
            }}
            .filter-row select, .filter-row input {{
                padding: 5px 10px;
                border: 1px solid #ddd;
                border-radius: 5px;
                font-size: 13px;
                font-family: inherit;
                background: white;
            }}
            .filter-row select:focus, .filter-row input:focus {{
                outline: none;
                border-color: {primary};
                box-shadow: 0 0 0 2px {primary}30;
            }}
            .filter-row input[type="text"] {{
                min-width: 150px;
            }}
            .filter-row input[type="number"] {{
                width: 80px;
            }}
            #visibleCount {{
                font-weight: 600;
                color: {primary};
                font-size: 14px;
                padding: 5px 10px;
                background: white;
                border-radius: 5px;
                border: 1px solid #e8e8e8;
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
            .table-container {{
                overflow-x: auto;
                max-height: 600px;
                overflow-y: auto;
                border: 1px solid #e8e8e8;
                border-radius: 8px;
            }}
            .table-container table {{
                margin: 0;
            }}
            .table-container thead {{
                position: sticky;
                top: 0;
                z-index: 10;
            }}
            @media print {{
                .sidebar {{ display: none; }}
                .main-content {{ margin-left: 0; }}
            }}
            @media (max-width: 768px) {{
                .sidebar {{ display: none; }}
                .main-content {{ margin-left: 0; padding: 20px; }}
                .metrics-grid {{
                    grid-template-columns: repeat(2, 1fr);
                }}
                .filter-row {{
                    flex-direction: column;
                    align-items: stretch;
                }}
                .filter-row > div {{
                    flex-wrap: wrap;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="sidebar">
            <h2>📊 {t('app_title')}</h2>
            <a href="#overview" class="nav-level1"><span>📋 {t('overview')}</span></a>
            <a href="#analyzed_articles" class="nav-level1"><span>📄 {t('analyzed_articles')}</span></a>
            <a href="#author_analysis" class="nav-level2"><span>👤 {t('author_analysis')}</span></a>
            <a href="#top_affiliations" class="nav-level2"><span>🏛️ {t('top_affiliations')}</span></a>
            <a href="#geographic_analysis" class="nav-level2"><span>🌍 {t('geographic_analysis')}</span></a>
            <a href="#geographic_countries_per_pub" class="nav-level2" style="padding-left: 45px;">└ {t('unique_countries_per_publication')}</a>
            <a href="#geographic_authors_per_country" class="nav-level2" style="padding-left: 45px;">└ {t('authors_per_country')}</a>
            <a href="#geographic_collaboration_patterns" class="nav-level2" style="padding-left: 45px;">└ {t('collaboration_patterns')}</a>
            <a href="#geographic_collaboration_couples" class="nav-level2" style="padding-left: 45px;">└ {t('collaboration_couples')}</a>
            <a href="#citation_analysis" class="nav-level1"><span>📈 {t('citation_analysis')}</span></a>
            <a href="#citation_dynamics" class="nav-level2"><span>📊 {t('citation_dynamics_by_year')}</span></a>
            <a href="#cumulative_citations" class="nav-level2"><span>📈 {t('cumulative_citations')}</span></a>
            <a href="#heatmap" class="nav-level2"><span>🔥 {t('citation_network_heatmap')}</span></a>
            <a href="#most_cited" class="nav-level2"><span>🏆 {t('most_cited_publications')}</span></a>
            <a href="#citing_works" class="nav-level1"><span>📚 {t('citing_works_analysis')}</span></a>
            <a href="#citing_authors" class="nav-level2"><span>👤 {t('top_citing_authors')}</span></a>
            <a href="#citing_affiliations" class="nav-level2"><span>🏛️ {t('top_citing_affiliations')}</span></a>
            <a href="#citing_countries" class="nav-level2"><span>🌍 {t('top_citing_countries')}</span></a>
            <a href="#citing_journals" class="nav-level2"><span>📰 {t('top_citing_journals')}</span></a>
            <a href="#citing_publishers" class="nav-level2"><span>🏢 {t('top_citing_publishers')}</span></a>
            <a href="#topics_analysis" class="nav-level1"><span>🏷️ {t('topics_analysis')}</span></a>
            <a href="#topics_overview" class="nav-level2"><span>📊 {t('topics')}</span></a>
            <a href="#top_cited" class="nav-level2"><span>🏆 {t('top_cited_topics')}</span></a>
            <a href="#detailed_citations" class="nav-level1"><span>📋 {t('detailed_citations')}</span></a>
            <a href="#all_publications" class="nav-level1"><span>📚 {t('all_publications')}</span></a>
        </div>
        
        <div class="main-content">
            <div class="header">
                <h1>📊 {t('app_title')}</h1>
                <div class="subtitle">ISSN: {issn} | Period: {period}</div>
                <div class="date">{t('report_preview')}: {datetime.now().strftime('%d.%m.%Y %H:%M')}</div>
                <div style="margin-top: 15px;">
                    <span class="badge badge-info">{t('total_publications_found', count=total_pubs)}</span>
                    <span class="badge badge-success">h-index: {h_index}</span>
                    <span class="badge badge-primary">{t('total_citations')}: {total_citations:,}</span>
                </div>
            </div>
            
            <!-- Overview Section -->
            <div id="overview" class="section">
                <div class="section-title"><span class="icon">📋</span> {t('overview')}</div>
                
                <div class="sub-section-title">{t('main_metrics')}</div>
                <div class="metrics-grid">
                    <div class="metric-card primary">
                        <div class="metric-value">{total_pubs}</div>
                        <div class="metric-label">{t('publications')}</div>
                    </div>
                    <div class="metric-card primary">
                        <div class="metric-value">{total_citations:,}</div>
                        <div class="metric-label">{t('total_citations')}</div>
                    </div>
                    <div class="metric-card primary">
                        <div class="metric-value">{h_index}</div>
                        <div class="metric-label">{t('h_index')}</div>
                    </div>
                    <div class="metric-card primary">
                        <div class="metric-value">{g_index}</div>
                        <div class="metric-label">{t('g_index')}</div>
                    </div>
                    <div class="metric-card primary">
                        <div class="metric-value">{i10_index}</div>
                        <div class="metric-label">{t('i10_index')}</div>
                    </div>
                    <div class="metric-card primary">
                        <div class="metric-value">{i100_index}</div>
                        <div class="metric-label">{t('i100_index')}</div>
                    </div>
                    <div class="metric-card secondary">
                        <div class="metric-value">{avg_citations:.1f}</div>
                        <div class="metric-label">{t('avg_citations')}</div>
                    </div>
                    <div class="metric-card secondary">
                        <div class="metric-value">{active_years}</div>
                        <div class="metric-label">{t('active_years')}</div>
                    </div>
                </div>
                
                <div class="sub-section-title">{t('open_access_breakdown')}</div>
                <div class="metrics-grid">
                    {oa_html}
                </div>
                
                <div class="sub-section-title">{t('collaboration_metrics')}</div>
                <div class="metrics-grid">
                    <div class="metric-card secondary">
                        <div class="metric-value">{unique_authors}</div>
                        <div class="metric-label">{t('unique_authors')}</div>
                    </div>
                    <div class="metric-card secondary">
                        <div class="metric-value">{unique_affiliations}</div>
                        <div class="metric-label">{t('unique_affiliations')}</div>
                    </div>
                    <div class="metric-card secondary">
                        <div class="metric-value">{unique_countries}</div>
                        <div class="metric-label">{t('unique_countries')}</div>
                    </div>
                    <div class="metric-card secondary">
                        <div class="metric-value">{avg_authors:.1f}</div>
                        <div class="metric-label">{t('avg_authors_per_paper')}</div>
                    </div>
                    <div class="metric-card secondary">
                        <div class="metric-value">{avg_affiliations:.1f}</div>
                        <div class="metric-label">{t('avg_affiliations_per_paper')}</div>
                    </div>
                    <div class="metric-card secondary">
                        <div class="metric-value">{avg_countries:.1f}</div>
                        <div class="metric-label">{t('avg_countries_per_paper')}</div>
                    </div>
                    <div class="metric-card primary">
                        <div class="metric-value">{international_rate*100:.1f}%</div>
                        <div class="metric-label">{t('international_collab_rate')}</div>
                    </div>
                </div>
                
                <div class="sub-section-title">{t('citing_works_analysis')}</div>
                <div class="metrics-grid">
                    <div class="metric-card secondary">
                        <div class="metric-value">{total_citing_works}</div>
                        <div class="metric-label">{t('total_citing_works')}</div>
                    </div>
                    <div class="metric-card secondary">
                        <div class="metric-value">{unique_citing_authors}</div>
                        <div class="metric-label">{t('unique_citing_authors')}</div>
                    </div>
                    <div class="metric-card secondary">
                        <div class="metric-value">{unique_citing_affiliations}</div>
                        <div class="metric-label">{t('unique_citing_affiliations')}</div>
                    </div>
                    <div class="metric-card secondary">
                        <div class="metric-value">{unique_citing_countries}</div>
                        <div class="metric-label">{t('unique_citing_countries')}</div>
                    </div>
                    <div class="metric-card secondary">
                        <div class="metric-value">{unique_citing_journals}</div>
                        <div class="metric-label">{t('unique_citing_journals')}</div>
                    </div>
                    <div class="metric-card secondary">
                        <div class="metric-value">{unique_citing_publishers}</div>
                        <div class="metric-label">{t('unique_citing_publishers')}</div>
                    </div>
                </div>
            </div>
            
            <!-- Analyzed Articles Section -->
            <div id="analyzed_articles" class="section">
                <div class="section-title"><span class="icon">📄</span> {t('analyzed_articles')}</div>
                
                <!-- Author Analysis -->
                <div id="author_analysis">
                    <div class="sub-section-title">{t('author_analysis')}</div>
                    <div class="table-container">
                        <table>
                            <thead>
                                <tr>
                                    <th>{t('rank')}</th>
                                    <th>{t('authors')}</th>
                                    <th>{t('orcid')}</th>
                                    <th>{t('affiliations')}</th>
                                    <th>{t('countries')}</th>
                                    <th>{t('publications_count')}</th>
                                    <th>{t('citations')}</th>
                                </tr>
                            </thead>
                            <tbody>
                                {author_table_rows}
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <!-- Top Affiliations -->
                <div id="top_affiliations">
                    <div class="sub-section-title">{t('top_affiliations')}</div>
                    <div class="table-container">
                        <table>
                            <thead>
                                <tr>
                                    <th>{t('affiliations')}</th>
                                    <th>{t('publications_count')}</th>
                                </tr>
                            </thead>
                            <tbody>
                                {affil_rows}
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <!-- Geographic Analysis -->
                <div id="geographic_analysis">
                    <div class="sub-section-title">{t('geographic_analysis')}</div>
                    
                    <!-- Unique Countries per Publication -->
                    <div id="geographic_countries_per_pub">
                        <h4 style="color: {primary}; margin: 15px 0 10px 0;">{t('unique_countries_per_publication')}</h4>
                        <div class="table-container">
                            <table>
                                <thead>
                                    <tr>
                                        <th>{t('title')}</th>
                                        <th>{t('year')}</th>
                                        <th>{t('countries')}</th>
                                        <th>{t('publications_count')}</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {countries_per_pub_rows}
                                </tbody>
                            </table>
                        </div>
                    </div>
                    
                    <!-- Authors per Country -->
                    <div id="geographic_authors_per_country">
                        <h4 style="color: {primary}; margin: 15px 0 10px 0;">{t('authors_per_country')}</h4>
                        <div class="table-container">
                            <table>
                                <thead>
                                    <tr>
                                        <th>{t('countries')}</th>
                                        <th>{t('authors')}</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {authors_per_country_rows}
                                </tbody>
                            </table>
                        </div>
                    </div>
                    
                    <!-- Collaboration Patterns -->
                    <div id="geographic_collaboration_patterns">
                        <h4 style="color: {primary}; margin: 15px 0 10px 0;">{t('collaboration_patterns')}</h4>
                        <div class="metrics-grid" style="grid-template-columns: repeat(2, 1fr); max-width: 400px;">
                            <div class="metric-card secondary">
                                <div class="metric-value">{single_country}</div>
                                <div class="metric-label">{t('single_country')}</div>
                            </div>
                            <div class="metric-card primary">
                                <div class="metric-value">{international_pubs}</div>
                                <div class="metric-label">{t('international')}</div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Collaboration Couples -->
                    <div id="geographic_collaboration_couples">
                        <h4 style="color: {primary}; margin: 15px 0 10px 0;">{t('collaboration_couples')}</h4>
                        <div class="table-container">
                            <table>
                                <thead>
                                    <tr>
                                        <th>{t('country_pair')}</th>
                                        <th>{t('frequency')}</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {country_pairs_rows}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Citation Analysis Section -->
            <div id="citation_analysis" class="section">
                <div class="section-title"><span class="icon">📈</span> {t('citation_analysis')}</div>
                
                <!-- Citation Dynamics by Year -->
                <div id="citation_dynamics">
                    <div class="sub-section-title">{t('citation_dynamics_by_year')}</div>
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
                                {dynamics_rows}
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <!-- Cumulative Citations -->
                <div id="cumulative_citations">
                    <div class="sub-section-title">{t('cumulative_citations')}</div>
                    <div class="table-container">
                        <table>
                            <thead>
                                <tr>
                                    <th>{t('year')}</th>
                                    <th>{t('citations')}</th>
                                </tr>
                            </thead>
                            <tbody>
                                {cumulative_rows}
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <!-- Citation Network Heatmap -->
                <div id="heatmap">
                    <div class="sub-section-title">{t('citation_network_heatmap')}</div>
                    <div class="table-container" style="max-height: 800px;">
                        <table>
                            <thead>
                                <tr>
                                    <th style="position: sticky; left: 0; z-index: 20;">{t('publication_year')}</th>
                                    {''.join([f'<th style="position: sticky; top: 0; z-index: 10;">{year}</th>' for year in all_years])}
                                </tr>
                            </thead>
                            <tbody>
                                {heatmap_rows}
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <!-- Most Cited Publications -->
                <div id="most_cited">
                    <div class="sub-section-title">{t('most_cited_publications')}</div>
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
                                {most_cited_rows}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
            
            <!-- Citing Works Analysis Section -->
            <div id="citing_works" class="section">
                <div class="section-title"><span class="icon">📚</span> {t('citing_works_analysis')}</div>
                
                <!-- Top Citing Authors -->
                <div id="citing_authors">
                    <div class="sub-section-title">{t('top_citing_authors')}</div>
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
                                {citing_authors_rows}
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <!-- Top Citing Affiliations -->
                <div id="citing_affiliations">
                    <div class="sub-section-title">{t('top_citing_affiliations')}</div>
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
                                {citing_affil_rows}
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <!-- Top Citing Countries -->
                <div id="citing_countries">
                    <div class="sub-section-title">{t('top_citing_countries')}</div>
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
                                {citing_country_rows}
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <!-- Top Citing Journals -->
                <div id="citing_journals">
                    <div class="sub-section-title">{t('top_citing_journals')}</div>
                    <div class="table-container">
                        <table>
                            <thead>
                                <tr>
                                    <th>{t('rank')}</th>
                                    <th>{t('journals')}</th>
                                    <th>{t('citations')}</th>
                                </tr>
                            </thead>
                            <tbody>
                                {citing_journal_rows}
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <!-- Top Citing Publishers -->
                <div id="citing_publishers">
                    <div class="sub-section-title">{t('top_citing_publishers')}</div>
                    <div class="table-container">
                        <table>
                            <thead>
                                <tr>
                                    <th>{t('rank')}</th>
                                    <th>{t('publishers')}</th>
                                    <th>{t('citations')}</th>
                                </tr>
                            </thead>
                            <tbody>
                                {citing_publisher_rows}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
            
            <!-- Topics Analysis Section -->
            <div id="topics_analysis" class="section">
                <div class="section-title"><span class="icon">🏷️</span> {t('topics_analysis')}</div>
                
                <!-- Topics Overview -->
                <div id="topics_overview">
                    <div class="sub-section-title">{t('topics')}</div>
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
                                    <th>{t('recent_5_years_count')}</th>
                                </tr>
                            </thead>
                            <tbody>
                                {topics_rows}
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <!-- Top Cited Topics, Fields, Domains, Concepts -->
                <div id="top_cited">
                    <div class="sub-section-title">{t('top_cited_topics')}</div>
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
                                {top_cited_rows}
                            </tbody>
                        </table>
                    </div>
                    
                    <div class="sub-section-title" style="margin-top: 20px;">{t('fields')}</div>
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
                                {top_cited_fields_rows}
                            </tbody>
                        </table>
                    </div>
                    
                    <div class="sub-section-title" style="margin-top: 20px;">{t('domains')}</div>
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
                                {top_cited_domains_rows}
                            </tbody>
                        </table>
                    </div>
                    
                    <div class="sub-section-title" style="margin-top: 20px;">{t('concepts')}</div>
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
                                {top_cited_concepts_rows}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
            
            <!-- Detailed Citations Section -->
            <div id="detailed_citations" class="section">
                <div class="section-title"><span class="icon">📋</span> {t('detailed_citations')}</div>
                {detailed_citations_html if detailed_citations_html else '<p>No detailed citations available</p>'}
            </div>
            
            <!-- All Publications Section -->
            <div id="all_publications" class="section">
                <div class="section-title"><span class="icon">📚</span> {t('all_publications')}</div>
                
                <div class="filter-section">
                    <div class="filter-row">
                        <div>
                            <label for="yearFilter">{t('filter_by_year')}:</label>
                            <select id="yearFilter" onchange="filterPublications()">
                                <option value="">All Years</option>
                                {year_options}
                            </select>
                        </div>
                        <div>
                            <label for="authorFilter">{t('filter_by_author')}:</label>
                            <input type="text" id="authorFilter" placeholder="Author name..." onkeyup="filterPublications()">
                        </div>
                        <div>
                            <label for="affiliationFilter">{t('filter_by_affiliations')}:</label>
                            <input type="text" id="affiliationFilter" placeholder="Affiliation..." onkeyup="filterPublications()">
                        </div>
                        <div>
                            <label for="citationFilter">{t('filter_by_citations')}:</label>
                            <input type="number" id="citationFilter" placeholder="Min citations..." min="0" onchange="filterPublications()">
                        </div>
                        <div>
                            <label for="titleFilter">{t('filter_by_title')}:</label>
                            <input type="text" id="titleFilter" placeholder="Search in titles..." onkeyup="filterPublications()">
                        </div>
                        <div>
                            <span id="visibleCount" style="font-weight: 500;">All publications</span>
                        </div>
                    </div>
                </div>
                
                <div class="table-container" style="max-height: 800px;">
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
                            {publications_rows}
                        </tbody>
                    </table>
                </div>
            </div>
            
            <!-- Footer -->
            <div class="footer">
                <p>{t('footer')}</p>
                <p><a href="{t('journal_url')}" target="_blank">{t('journal_url')}</a></p>
                <p style="font-size: 11px; margin-top: 5px;">Data source: OpenAlex | Generated: {datetime.now().strftime('%d.%m.%Y %H:%M')}</p>
            </div>
        </div>
        
        <script>
            function toggleCitations(id) {{
                var element = document.getElementById('citations_' + id);
                if (element) {{
                    if (element.style.display === 'none') {{
                        element.style.display = 'block';
                    }} else {{
                        element.style.display = 'none';
                    }}
                }}
            }}
            
            function filterPublications() {{
                var yearFilter = document.getElementById('yearFilter').value;
                var authorFilter = document.getElementById('authorFilter').value.toLowerCase();
                var affiliationFilter = document.getElementById('affiliationFilter').value.toLowerCase();
                var citationFilter = parseInt(document.getElementById('citationFilter').value) || 0;
                var titleFilter = document.getElementById('titleFilter').value.toLowerCase();
                
                var table = document.getElementById('publicationsTable');
                var rows = table.getElementsByTagName('tbody')[0].getElementsByTagName('tr');
                var visibleCount = 0;
                
                for (var i = 0; i < rows.length; i++) {{
                    var row = rows[i];
                    var year = row.getAttribute('data-year');
                    var authors = row.getAttribute('data-authors') || '';
                    var affiliations = row.getAttribute('data-affiliations') || '';
                    var citations = parseInt(row.getAttribute('data-citations')) || 0;
                    var title = row.getAttribute('data-title') || '';
                    
                    var show = true;
                    
                    if (yearFilter && year !== yearFilter) show = false;
                    if (authorFilter && !authors.includes(authorFilter)) show = false;
                    if (affiliationFilter && !affiliations.includes(affiliationFilter)) show = false;
                    if (citations < citationFilter) show = false;
                    if (titleFilter && !title.includes(titleFilter)) show = false;
                    
                    row.style.display = show ? '' : 'none';
                    if (show) visibleCount++;
                }}
                
                var countElement = document.getElementById('visibleCount');
                var total = rows.length;
                countElement.textContent = visibleCount + ' of ' + total + ' publications';
            }}
            
            function sortTable(columnIndex) {{
                var table = document.getElementById('publicationsTable');
                var tbody = table.getElementsByTagName('tbody')[0];
                var rows = tbody.getElementsByTagName('tr');
                var sortedRows = Array.from(rows);
                
                var isAscending = table.getAttribute('data-sort-dir') !== 'asc';
                table.setAttribute('data-sort-dir', isAscending ? 'asc' : 'desc');
                
                sortedRows.sort(function(a, b) {{
                    var aVal = a.cells[columnIndex].textContent.trim();
                    var bVal = b.cells[columnIndex].textContent.trim();
                    
                    var aNum = parseFloat(aVal);
                    var bNum = parseFloat(bVal);
                    
                    if (!isNaN(aNum) && !isNaN(bNum)) {{
                        return isAscending ? aNum - bNum : bNum - aNum;
                    }}
                    
                    return isAscending ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
                }});
                
                for (var i = 0; i < sortedRows.length; i++) {{
                    tbody.appendChild(sortedRows[i]);
                }}
            }}
            
            // Initialize visible count
            window.onload = function() {{
                filterPublications();
            }};
        </script>
    </body>
    </html>
    """
    
    return html_content

# ============================================
# ФУНКЦИИ ДЛЯ АНАЛИЗА ЖУРНАЛА (ОСНОВНАЯ ЛОГИКА)
# ============================================

def analyze_journal(issn: str, period_str: str, max_workers: int = MAX_WORKERS, progress_callback=None) -> Dict:
    """Main function to analyze a journal"""
    
    if SHOW_DEBUG_LOGS:
        print(f"🚀 Starting journal analysis for ISSN: {issn}, period: {period_str}")
    
    # Normalize ISSN
    issn_normalized = normalize_issn(issn)
    if not issn_normalized:
        return {'error': 'Invalid ISSN'}
    
    # Parse period
    period = parse_period(period_str)
    if period is None:
        return {'error': 'Invalid period format'}
    
    # Check cache
    cache_path = get_cache_path(issn_normalized, period_str)
    cached_data = load_from_cache(cache_path)
    
    if cached_data:
        if SHOW_DEBUG_LOGS:
            print("📦 Using cached data")
        return cached_data
    
    # Create analyzer
    analyzer = JournalAnalyzer(issn_normalized, period, max_workers)
    
    # Run analysis
    def internal_progress(progress, stage):
        if progress_callback:
            progress_callback(progress, stage)
    
    metrics = analyzer.analyze(internal_progress)
    
    if 'error' in metrics:
        return metrics
    
    # Save to cache
    save_to_cache(cache_path, metrics)
    
    if SHOW_DEBUG_LOGS:
        print("✅ Analysis complete")
    
    return metrics

# ============================================
# ОСНОВНАЯ ФУНКЦИЯ ЗАПУСКА ДЛЯ STREAMLIT
# ============================================

def run_journal_analysis(issn: str, period_str: str, max_workers: int):
    """Run journal analysis and display results in Streamlit"""
    
    # Get current language for translations
    current_lang = st.session_state.get('language', 'en')
    def t(key: str, **kwargs) -> str:
        return translate(key, current_lang, **kwargs)
    
    if not issn:
        st.error("⚠️ " + t('no_issn'))
        return
    
    if not period_str:
        st.error("⚠️ " + t('no_period'))
        return
    
    st.cache_data.clear()
    
    st.info(t('analyzing_journal', issn=issn, period=period_str))
    
    progress_container = st.empty()
    status_container = st.empty()
    analysis_progress = st.progress(0, text=t('starting_analysis'))
    
    try:
        start_time = time.time()
        
        def progress_callback(progress, stage):
            """Update progress bar"""
            progress_value = progress / 100
            stage_text = t(stage) if stage in LANG[current_lang] else stage
            status_container.info(f"{stage_text}...")
            analysis_progress.progress(progress_value, text=f"{stage_text} ({progress:.0f}%)")
        
        # Run analysis
        metrics = analyze_journal(issn, period_str, max_workers, progress_callback)
        
        elapsed = time.time() - start_time
        
        if 'error' in metrics:
            st.error(f"❌ {t('error_occurred')}: {metrics['error']}")
            analysis_progress.empty()
            return
        
        total_pubs = metrics.get('total_publications', 0)
        h_index = metrics.get('h_index', 0)
        total_citations = metrics.get('total_citations', 0)
        
        st.success(t('analysis_complete', count=total_pubs, time=elapsed))
        
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(t('publications'), total_pubs)
        with col2:
            st.metric(t('h_index'), h_index)
        with col3:
            st.metric(t('total_citations'), f"{total_citations:,}")
        with col4:
            st.metric(t('active_years'), metrics.get('active_years', 0))
        
        # Generate HTML report
        primary_color = st.session_state.get('primary_color', '#667eea')
        secondary_color = st.session_state.get('secondary_color', '#f39c12')
        
        with st.spinner(t('generating_report')):
            html_report = generate_journal_html_report(
                metrics, 
                issn, 
                period_str,
                primary_color,
                secondary_color,
                current_lang
            )
        
        st.session_state['journal_metrics'] = metrics
        st.session_state['html_report'] = html_report
        st.session_state['analysis_complete'] = True
        
        analysis_progress.progress(1.0, text=f"✅ {t('analysis_complete_text')}!")
        
        # Show report preview
        st.markdown("---")
        st.markdown(f"## {t('report_preview')}")
        
        # Download button
        filename = f"journal_{issn}_{period_str.replace('-', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        st.download_button(
            label="📥 " + t('download_report'),
            data=html_report.encode('utf-8'),
            file_name=filename,
            mime="text/html",
            type="primary"
        )
        
        st.info(t('download_hint'))
        
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
    if 'analysis_complete' not in st.session_state:
        st.session_state.analysis_complete = False
    if 'journal_metrics' not in st.session_state:
        st.session_state.journal_metrics = {}
    if 'html_report' not in st.session_state:
        st.session_state.html_report = None
    
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
    st.markdown(f"### {t('app_title')}")
    st.markdown(f"#### {t('analyze_journal')}")
    st.markdown("---")
    
    # Tabs
    tab1, tab2 = st.tabs([
        t('load_data'),
        t('reports')
    ])
    
    with tab1:
        st.markdown('<div class="custom-tab fade-in">', unsafe_allow_html=True)
        st.header(t('load_data'))
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            issn_input = st.text_input(
                t('issn_input'),
                placeholder=t('issn_placeholder'),
                help="Enter the ISSN of the journal to analyze"
            )
            
            period_input = st.text_input(
                t('period_input'),
                placeholder=t('period_placeholder'),
                help=t('period_help')
            )
        
        with col2:
            max_workers = st.slider(
                t('max_workers'),
                min_value=2,
                max_value=12,
                value=MAX_WORKERS,
                step=1,
                help=t('max_workers_help')
            )
            
            st.markdown("---")
            st.markdown("**Examples:**")
            st.markdown("• Range: `2020-2023`")
            st.markdown("• List: `2020,2021,2022`")
            st.markdown("• Single year: `2020`")
        
        if st.button(t('analyze_button'), type="primary", width='stretch'):
            if not issn_input:
                st.error(t('no_issn'))
            elif not period_input:
                st.error(t('no_period'))
            else:
                run_journal_analysis(issn_input, period_input, max_workers)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        if st.session_state.analysis_complete and st.session_state.html_report:
            st.markdown(f"## {t('html_report')}")
            
            # Display metrics summary
            metrics = st.session_state.journal_metrics
            if metrics:
                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    st.metric(t('publications'), metrics.get('total_publications', 0))
                with col2:
                    st.metric(t('h_index'), metrics.get('h_index', 0))
                with col3:
                    st.metric(t('g_index'), metrics.get('g_index', 0))
                with col4:
                    st.metric(t('total_citations'), f"{metrics.get('total_citations', 0):,}")
                with col5:
                    st.metric(t('avg_citations'), f"{metrics.get('avg_citations', 0):.1f}")
            
            st.markdown("---")
            
            # Download button
            filename = f"journal_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            st.download_button(
                label="📥 " + t('download_report'),
                data=st.session_state.html_report.encode('utf-8'),
                file_name=filename,
                mime="text/html",
                type="primary"
            )
            
            st.info(t('download_hint'))
            
            # Show preview of the report in an iframe
            st.markdown("---")
            st.markdown(f"### {t('report_preview')}")
            
            # Display HTML in iframe
            html_report = st.session_state.html_report
            st.components.v1.html(html_report, height=800, scrolling=True)
            
        else:
            st.info(t('no_data_reports'))

if __name__ == "__main__":
    main()
