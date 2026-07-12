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
MAX_WORKERS = 8  # Количество параллельных потоков для сбора цитирований
BASE_DELAY = 0.35  # Базовая задержка между запросами
MAX_CITING_PER_PAPER = 300  # Максимум цитирующих статей на одну работу

# Параметры вывода
SHOW_DEBUG_LOGS = True  # Показывать детальные логи
GENERATE_HTML_REPORT = True  # Генерировать HTML отчет
USE_CACHE = False  # Кэширование результатов
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
        'analysis_params': '📊 Analysis Parameters',
        'use_cache': '💾 Use cache',
        'clear_cache': '🗑️ Clear cache',
        'cache_cleared': '✅ Cache cleared!',
        'load_data': '📥 Load Data',
        'analyze_journal': '📊 Analyze Journal',
        'reports': '📄 Reports',
        'issn_input': 'Journal ISSN',
        'issn_placeholder': '0028-0836 or 0028-0836',
        'issn_help': 'Enter ISSN of the journal to analyze',
        'period_input': 'Analysis Period',
        'period_placeholder': '2020-2023 or 2020,2021,2022 or 2020',
        'period_help': 'Format: YYYY-YYYY (range), YYYY,YYYY (list), or YYYY (single year)',
        'workers_label': 'Parallel Workers',
        'workers_help': 'Number of parallel threads for citation collection (4-12)',
        'upload_logo': 'Upload journal logo (optional)',
        'logo_help': 'Logo will be displayed in reports',
        'analyze_button': '🚀 Start Analysis',
        'no_issn': '⚠️ Enter ISSN',
        'no_period': '⚠️ Enter analysis period',
        'invalid_period': '⚠️ Invalid period format',
        'analysis_complete': '✅ Analysis complete!',
        'error_occurred': '❌ Error occurred',
        'no_data': '👈 Run analysis in "Analyze Journal" tab',
        'html_report': '📄 HTML Report',
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
        'international_collaboration_rate': 'International Collaboration Rate',
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
        'author_analysis': 'Author Analysis',
        'rank': 'Rank',
        'authors': 'Authors',
        'orcid': 'ORCID',
        'affiliations': 'Affiliations',
        'countries': 'Countries',
        'publications_count': 'Publications',
        'citations_count': 'Citations',
        'top_affiliations': 'Top Affiliations',
        'geographic_analysis': 'Geographic Analysis',
        'unique_countries_per_publication': 'Unique Countries per Publication (Collaboration Level)',
        'authors_per_country': 'Authors per Country (Individual Distribution)',
        'collaboration_patterns': 'Collaboration Patterns',
        'single_country': 'Single-Country',
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
        'year': 'Year',
        'cumulative': 'Cumulative',
        'citation_network_heatmap': 'Citation Network Heatmap',
        'most_cited_publications': 'Most Cited Publications',
        'title': 'Title',
        'citations_per_year': 'Citations/Year',
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
        'analyzed_norm': 'Analyzed Norm',
        'citing_norm': 'Citing Norm',
        'total_norm': 'Total Norm',
        'first_year': 'First Year',
        'peak_year': 'Peak Year',
        'top_topics': 'Top Topics',
        'subtopics': 'Subtopics',
        'fields': 'Fields',
        'domains': 'Domains',
        'concepts': 'Concepts',
        'detailed_citations': 'Detailed Citations',
        'all_publications': 'All Publications',
        'filter_by_year': 'Filter by Year',
        'filter_by_title': 'Filter by Title Word(s)',
        'filter_by_author': 'Filter by Author',
        'filter_by_affiliation': 'Filter by Affiliations',
        'filter_by_citations': 'Filter by Citations (min)',
        'show_citations': 'Show Citations',
        'all_years': 'All Years',
        'citing_journal': 'Citing Journal',
        'citing_year': 'Citing Year',
        'citing_date': 'Citing Date',
        'citation_lag': 'Citation Lag',
        'search_publications': 'Search Publications',
        'footer': '© Advanced Journal Analysis Tool / Created by daM / Chimica Techno Acta',
        'journal_url': 'https://chimicatechnoacta.ru',
        'no_profile_data': 'No data available',
        'enter_issn': 'Enter ISSN to analyze',
        'select_language': 'Select language',
        'theme_presets_label': 'Theme presets',
        'primary_color_label': 'Primary color',
        'secondary_color_label': 'Secondary color',
        'analysis_progress': 'Analysis Progress',
        'loading_articles': 'Loading journal articles',
        'fetching_citations': 'Fetching citation DOIs',
        'fetching_citation_metadata': 'Fetching citation metadata',
        'analyzing_data': 'Analyzing data',
        'generating_report_text': 'Generating HTML report',
        'articles_loaded': 'Articles loaded',
        'citation_dois_collected': 'Citation DOIs collected',
        'citation_metadata_fetched': 'Citation metadata fetched',
        'analysis_complete_text': 'Analysis complete',
        'start_analysis': 'Starting analysis...',
        'fetching_articles': 'Fetching articles from OpenAlex...',
        'parsing_articles': 'Parsing article data...',
        'total_articles_found': 'Total articles found',
        'total_citations_sum': 'Total citations sum',
        'parallel_citation_collection': 'Parallel citation collection',
        'processing_citations': 'Processing citations',
        'stage_1': 'Stage 1/5: Loading journal articles',
        'stage_2': 'Stage 2/5: Collecting citation DOIs',
        'stage_3': 'Stage 3/5: Fetching citation metadata',
        'stage_4': 'Stage 4/5: Analyzing data',
        'stage_5': 'Stage 5/5: Generating report',
        'analyzed_articles': 'Analyzed Articles',
        'citing_works': 'Citing Works',
        'overview': 'Overview',
        'analyzed_articles_section': 'Analyzed Articles',
        'citation_analysis_section': 'Citation Analysis',
        'citing_works_section': 'Citing Works Analysis',
        'topics_analysis_section': 'Topics Analysis',
        'detailed_citations_section': 'Detailed Citations',
        'all_publications_section': 'All Publications',
        'author_analysis_section': 'Author Analysis',
        'top_affiliations_section': 'Top Affiliations',
        'geographic_analysis_section': 'Geographic Analysis',
        'citation_dynamics_section': 'Citation Dynamics',
        'cumulative_citations_section': 'Cumulative Citations',
        'heatmap_section': 'Citation Heatmap',
        'most_cited_section': 'Most Cited Publications',
        'top_authors_section': 'Top Citing Authors',
        'top_affils_section': 'Top Citing Affiliations',
        'top_countries_section': 'Top Citing Countries',
        'top_journals_section': 'Top Citing Journals',
        'top_publishers_section': 'Top Citing Publishers',
        'top_10_cited': 'Top 10 Most Cited',
        'view_details': 'View Details',
        'hide_details': 'Hide Details',
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
        'analyze_journal': '📊 Анализ журнала',
        'reports': '📄 Отчеты',
        'issn_input': 'ISSN журнала',
        'issn_placeholder': '0028-0836 или 0028-0836',
        'issn_help': 'Введите ISSN журнала для анализа',
        'period_input': 'Период анализа',
        'period_placeholder': '2020-2023 или 2020,2021,2022 или 2020',
        'period_help': 'Формат: ГГГГ-ГГГГ (диапазон), ГГГГ,ГГГГ (список), или ГГГГ (один год)',
        'workers_label': 'Параллельных потоков',
        'workers_help': 'Количество параллельных потоков для сбора цитирований (4-12)',
        'upload_logo': 'Загрузить логотип журнала (опционально)',
        'logo_help': 'Логотип будет отображаться в отчетах',
        'analyze_button': '🚀 Запустить анализ',
        'no_issn': '⚠️ Введите ISSN',
        'no_period': '⚠️ Введите период анализа',
        'invalid_period': '⚠️ Неверный формат периода',
        'analysis_complete': '✅ Анализ завершен!',
        'error_occurred': '❌ Произошла ошибка',
        'no_data': '👈 Выполните анализ на вкладке "Анализ журнала"',
        'html_report': '📄 HTML отчет',
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
        'international_collaboration_rate': 'Доля международных коллабораций',
        'unique_citing_authors': 'Уникальных цитирующих авторов',
        'unique_citing_affiliations': 'Уникальных цитирующих аффилиаций',
        'unique_citing_countries': 'Уникальных цитирующих стран',
        'unique_citing_journals': 'Уникальных цитирующих журналов',
        'unique_citing_publishers': 'Уникальных цитирующих издательств',
        'gold': 'Золотой',
        'hybrid': 'Гибридный',
        'green': 'Зеленый',
        'bronze': 'Бронзовый',
        'closed': 'Закрытый',
        'unknown': 'Неизвестный',
        'author_analysis': 'Анализ авторов',
        'rank': 'Ранг',
        'authors': 'Авторы',
        'orcid': 'ORCID',
        'affiliations': 'Аффилиации',
        'countries': 'Страны',
        'publications_count': 'Публикаций',
        'citations_count': 'Цитирований',
        'top_affiliations': 'Топ аффилиаций',
        'geographic_analysis': 'Географический анализ',
        'unique_countries_per_publication': 'Уникальные страны на публикацию (уровень коллабораций)',
        'authors_per_country': 'Авторы по странам (индивидуальное распределение)',
        'collaboration_patterns': 'Модели коллабораций',
        'single_country': 'Однострановые',
        'international': 'Международные',
        'collaboration_couples': 'Пары стран-коллабораций',
        'country_pair': 'Пара стран',
        'frequency': 'Частота',
        'citation_analysis': 'Анализ цитирований',
        'citation_dynamics_by_year': 'Динамика цитирований по годам',
        'publication_year': 'Год публикации',
        'citation_year': 'Год цитирования',
        'citations_count': 'Количество цитирований',
        'cumulative_citations': 'Накопленные цитирования',
        'year': 'Год',
        'cumulative': 'Накопленные',
        'citation_network_heatmap': 'Тепловая карта сети цитирований',
        'most_cited_publications': 'Самые цитируемые публикации',
        'title': 'Название',
        'citations_per_year': 'Цитирований/год',
        'citing_works_analysis': 'Анализ цитирующих работ',
        'total_citing_works': 'Всего цитирующих работ',
        'top_citing_authors': 'Топ цитирующих авторов',
        'top_citing_affiliations': 'Топ цитирующих аффилиаций',
        'top_citing_countries': 'Топ цитирующих стран',
        'top_citing_journals': 'Топ цитирующих журналов',
        'top_citing_publishers': 'Топ цитирующих издательств',
        'topics_analysis': 'Тематический анализ',
        'topics': 'Темы',
        'analyzed_count': 'Анализируемых',
        'citing_count': 'Цитирующих',
        'analyzed_norm': 'Анализ. норма',
        'citing_norm': 'Цитир. норма',
        'total_norm': 'Общая норма',
        'first_year': 'Первый год',
        'peak_year': 'Пиковый год',
        'top_topics': 'Топ темы',
        'subtopics': 'Подтемы',
        'fields': 'Области',
        'domains': 'Домены',
        'concepts': 'Концепты',
        'detailed_citations': 'Детальные цитирования',
        'all_publications': 'Все публикации',
        'filter_by_year': 'Фильтр по году',
        'filter_by_title': 'Фильтр по словам в названии',
        'filter_by_author': 'Фильтр по автору',
        'filter_by_affiliation': 'Фильтр по аффилиации',
        'filter_by_citations': 'Фильтр по цитированиям (мин)',
        'show_citations': 'Показать цитирования',
        'all_years': 'Все годы',
        'citing_journal': 'Цитирующий журнал',
        'citing_year': 'Год цитирования',
        'citing_date': 'Дата цитирования',
        'citation_lag': 'Лаг цитирования',
        'search_publications': 'Поиск публикаций',
        'footer': '© Advanced Journal Analysis Tool / Created by daM / Chimica Techno Acta',
        'journal_url': 'https://chimicatechnoacta.ru',
        'no_profile_data': 'Нет данных',
        'enter_issn': 'Введите ISSN для анализа',
        'select_language': 'Выберите язык',
        'theme_presets_label': 'Пресеты тем',
        'primary_color_label': 'Основной цвет',
        'secondary_color_label': 'Дополнительный цвет',
        'analysis_progress': 'Прогресс анализа',
        'loading_articles': 'Загрузка статей журнала',
        'fetching_citations': 'Сбор DOI цитирований',
        'fetching_citation_metadata': 'Загрузка метаданных цитирований',
        'analyzing_data': 'Анализ данных',
        'generating_report_text': 'Генерация HTML отчета',
        'articles_loaded': 'Статей загружено',
        'citation_dois_collected': 'DOI цитирований собрано',
        'citation_metadata_fetched': 'Метаданных цитирований загружено',
        'analysis_complete_text': 'Анализ завершен',
        'start_analysis': 'Начинаем анализ...',
        'fetching_articles': 'Загрузка статей из OpenAlex...',
        'parsing_articles': 'Обработка данных статей...',
        'total_articles_found': 'Всего найдено статей',
        'total_citations_sum': 'Суммарное цитирование',
        'parallel_citation_collection': 'Параллельный сбор цитирований',
        'processing_citations': 'Обработка цитирований',
        'stage_1': 'Этап 1/5: Загрузка статей журнала',
        'stage_2': 'Этап 2/5: Сбор DOI цитирований',
        'stage_3': 'Этап 3/5: Загрузка метаданных цитирований',
        'stage_4': 'Этап 4/5: Анализ данных',
        'stage_5': 'Этап 5/5: Генерация отчета',
        'analyzed_articles': 'Анализируемые статьи',
        'citing_works': 'Цитирующие работы',
        'overview': 'Обзор',
        'analyzed_articles_section': 'Анализируемые статьи',
        'citation_analysis_section': 'Анализ цитирований',
        'citing_works_section': 'Анализ цитирующих работ',
        'topics_analysis_section': 'Тематический анализ',
        'detailed_citations_section': 'Детальные цитирования',
        'all_publications_section': 'Все публикации',
        'author_analysis_section': 'Анализ авторов',
        'top_affiliations_section': 'Топ аффилиаций',
        'geographic_analysis_section': 'Географический анализ',
        'citation_dynamics_section': 'Динамика цитирований',
        'cumulative_citations_section': 'Накопленные цитирования',
        'heatmap_section': 'Тепловая карта цитирований',
        'most_cited_section': 'Самые цитируемые публикации',
        'top_authors_section': 'Топ цитирующих авторов',
        'top_affils_section': 'Топ цитирующих аффилиаций',
        'top_countries_section': 'Топ цитирующих стран',
        'top_journals_section': 'Топ цитирующих журналов',
        'top_publishers_section': 'Топ цитирующих издательств',
        'top_10_cited': 'Топ 10 самых цитируемых',
        'view_details': 'Показать детали',
        'hide_details': 'Скрыть детали',
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
    """Нормализует ISSN к формату XXXX-XXXX"""
    cleaned = re.sub(r'[^0-9Xx]', '', str(issn_str).strip())
    if len(cleaned) == 8:
        return f"{cleaned[:4]}-{cleaned[4:]}".upper()
    return cleaned.upper()

def safe_get(data, *keys, default=None):
    """Безопасное получение значения из вложенного словаря"""
    for key in keys:
        if isinstance(data, dict):
            data = data.get(key, default)
        else:
            return default
    return data

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
    """Разбивает список на части по n элементов"""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def get_cache_path(issn: str) -> str:
    """Возвращает путь к файлу кэша для ISSN"""
    issn_clean = normalize_issn(issn)
    if not os.path.exists('cache'):
        os.makedirs('cache')
    return f"cache/{issn_clean}.json"

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

def parse_period(period_str: str) -> tuple:
    """Парсит строку периода и возвращает список годов или диапазон"""
    period_str = period_str.strip()
    
    if ',' in period_str:
        years = [int(y.strip()) for y in period_str.split(',') if y.strip().isdigit()]
        if years:
            return ('list', years)
    elif '-' in period_str:
        parts = period_str.split('-')
        if len(parts) == 2 and parts[0].strip().isdigit() and parts[1].strip().isdigit():
            start = int(parts[0].strip())
            end = int(parts[1].strip())
            if start <= end:
                return ('range', (start, end))
    elif period_str.isdigit():
        return ('single', int(period_str))
    
    return None

def build_year_filter(years) -> str:
    """Строит фильтр по годам для OpenAlex API"""
    if isinstance(years, list):
        return "|".join(f"publication_year:{y}" for y in years)
    elif isinstance(years, tuple) and len(years) == 2:
        return f"publication_year:{years[0]}-{years[1]}"
    elif isinstance(years, int):
        return f"publication_year:{years}"
    else:
        return ""

# ============================================
# КЛАСС ДЛЯ АНАЛИЗА ЖУРНАЛА
# ============================================

class JournalAnalyzer:
    """Анализирует журнал по ISSN с глубокой аналитикой цитирований"""
    
    def __init__(self, issn: str, years, max_workers: int = 8):
        self.issn = normalize_issn(issn)
        self.years = years
        self.max_workers = max_workers
        self.articles = []  # анализируемые статьи
        self.citations_map = {}  # {doi: [citing_dois]}
        self.citing_metadata = {}  # {doi: {metadata}}
        self.stats = {}
        self.articles_df = None
        self.citations_df = None
        self.citation_dynamics = defaultdict(lambda: defaultdict(int))
        self.cumulative_citations = defaultdict(int)
        self.heatmap_data = defaultdict(lambda: defaultdict(int))
        self.lock = Lock()
        
    def fetch_articles(self, progress_callback=None) -> int:
        """Загружает статьи журнала из OpenAlex"""
        base_url = "https://api.openalex.org/works"
        year_filter = build_year_filter(self.years)
        
        if not year_filter:
            return 0
        
        articles = []
        cursor = "*"
        page = 0
        
        if SHOW_DEBUG_LOGS:
            print(f"🔍 Загрузка статей для ISSN: {self.issn}, фильтр: {year_filter}")
        
        while True:
            page += 1
            params = {
                'filter': f"primary_location.source.issn:{self.issn},{year_filter}",
                'per_page': 200,
                'select': 'id,doi,publication_year,cited_by_count,primary_location,authorships,open_access,topics,concepts',
                'cursor': cursor
            }
            
            data = self._smart_get(base_url, params)
            
            if not data or not data.get('results'):
                break
            
            results = data['results']
            
            for item in results:
                doi = item.get('doi', '')
                if doi:
                    doi = doi.replace('https://doi.org/', '')
                
                # Парсим авторов
                authors = []
                author_orcids = []
                affiliations = []
                countries = []
                
                for auth in item.get('authorships', []):
                    author_data = auth.get('author', {})
                    author_name = author_data.get('display_name', '')
                    if author_name:
                        authors.append(author_name)
                        
                        orcid = author_data.get('orcid', '')
                        if orcid:
                            author_orcids.append(orcid.replace('https://orcid.org/', ''))
                    
                    # Аффилиации и страны
                    for inst in auth.get('institutions', []):
                        affil = inst.get('display_name', '')
                        if affil:
                            affiliations.append(affil)
                            country_code = inst.get('country_code', '')
                            if country_code:
                                countries.append(get_full_country_name(country_code))
                
                # Парсим primary_location для журнала
                journal_name = 'Unknown'
                publisher = 'Unknown'
                issn_list = []
                source_type = 'unknown'
                
                primary_loc = item.get('primary_location', {})
                if primary_loc:
                    source = primary_loc.get('source', {})
                    journal_name = source.get('display_name', 'Unknown')
                    publisher = source.get('host_organization_name') or source.get('publisher', 'Unknown')
                    issn_list = source.get('issn', [])
                    source_type = source.get('type', 'unknown')
                
                # Open Access
                oa = item.get('open_access', {})
                is_oa = oa.get('is_oa', False)
                oa_status = oa.get('oa_status', 'closed')
                oa_url = oa.get('oa_url', None)
                
                # Topics и Concepts
                topics = []
                subtopics = []
                fields = []
                domains = []
                concepts = []
                
                # Primary topic
                primary_topic = item.get('primary_topic', {})
                if primary_topic:
                    topic_name = primary_topic.get('display_name', '')
                    if topic_name:
                        topics.append(topic_name)
                    subfield = primary_topic.get('subfield', {}).get('display_name', '')
                    if subfield:
                        subtopics.append(subfield)
                    field = primary_topic.get('field', {}).get('display_name', '')
                    if field:
                        fields.append(field)
                    domain = primary_topic.get('domain', {}).get('display_name', '')
                    if domain:
                        domains.append(domain)
                
                # All topics
                for topic in item.get('topics', []):
                    topic_name = topic.get('display_name', '')
                    if topic_name and topic_name not in topics:
                        topics.append(topic_name)
                    subfield = topic.get('subfield', {}).get('display_name', '')
                    if subfield and subfield not in subtopics:
                        subtopics.append(subfield)
                    field = topic.get('field', {}).get('display_name', '')
                    if field and field not in fields:
                        fields.append(field)
                    domain = topic.get('domain', {}).get('display_name', '')
                    if domain and domain not in domains:
                        domains.append(domain)
                
                # Concepts
                for concept in item.get('concepts', []):
                    concept_name = concept.get('display_name', '')
                    if concept_name:
                        concepts.append(concept_name)
                
                article = {
                    'id': item.get('id', '').replace('https://openalex.org/', ''),
                    'doi': doi,
                    'title': item.get('title', 'No title'),
                    'publication_year': item.get('publication_year'),
                    'cited_by_count': item.get('cited_by_count', 0),
                    'journal_name': journal_name,
                    'publisher': publisher,
                    'issn': issn_list,
                    'source_type': source_type,
                    'is_oa': is_oa,
                    'oa_status': oa_status,
                    'oa_url': oa_url,
                    'authors': authors,
                    'author_orcids': author_orcids,
                    'author_count': len(authors),
                    'affiliations': list(set(affiliations)),
                    'affiliation_count': len(set(affiliations)),
                    'countries': list(set(countries)),
                    'country_count': len(set(countries)),
                    'topics': list(set(topics)),
                    'subtopics': list(set(subtopics)),
                    'fields': list(set(fields)),
                    'domains': list(set(domains)),
                    'concepts': list(set(concepts))
                }
                
                articles.append(article)
            
            if progress_callback:
                progress_callback(len(articles))
            
            cursor = data.get('meta', {}).get('next_cursor')
            if not cursor:
                break
        
        self.articles = articles
        self.articles_df = pd.DataFrame(articles)
        
        if SHOW_DEBUG_LOGS:
            print(f"✅ Загружено {len(articles)} статей")
        
        return len(articles)
    
    def _smart_get(self, url, params, retries=MAX_RETRIES):
        """Выполняет запрос с защитой от rate limit"""
        for attempt in range(retries):
            try:
                with self.lock:
                    time.sleep(random.uniform(0.1, BASE_DELAY))
                
                resp = requests.get(url, params=params, timeout=TIMEOUT)
                
                if resp.status_code == 429:
                    wait = int(resp.headers.get("Retry-After", 2 ** attempt + 1))
                    if SHOW_DEBUG_LOGS:
                        print(f"⚠️ Rate limit, ждем {wait} сек...")
                    time.sleep(wait + random.uniform(0.5, 1.5))
                    continue
                
                if resp.status_code == 200:
                    return resp.json()
                
                if SHOW_DEBUG_LOGS:
                    print(f"⚠️ Ошибка {resp.status_code} для {url}")
                time.sleep(1 * (2 ** attempt))
                
            except Exception as e:
                if SHOW_DEBUG_LOGS:
                    print(f"⚠️ Попытка {attempt+1}/{retries} ошибка: {str(e)[:100]}")
                time.sleep(1.5 * (2 ** attempt))
        
        return None
    
    def _get_citing_dois(self, oa_id: str) -> List[str]:
        """Получает список цитирующих DOI для одной статьи"""
        citing = []
        cursor = "*"
        base_url = "https://api.openalex.org/works"
        
        for _ in range(8):  # ограничение пагинации
            data = self._smart_get(base_url, {
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
    
    def fetch_citations_parallel(self, progress_callback=None) -> Dict:
        """Параллельно собирает цитирующие DOI для всех статей"""
        if not self.articles:
            return {}
        
        citing_map = {}
        futures = {}
        
        if SHOW_DEBUG_LOGS:
            print(f"⚡ Параллельный сбор цитирований ({self.max_workers} потоков)...")
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            total_articles = 0
            for article in self.articles:
                if article['cited_by_count'] > 0 and article['doi']:
                    future = executor.submit(self._get_citing_dois, article['id'])
                    futures[future] = article['doi']
                    total_articles += 1
            
            if SHOW_DEBUG_LOGS:
                print(f"📊 Обработка {total_articles} статей с цитированиями")
            
            completed = 0
            for future in as_completed(futures):
                doi = futures[future]
                try:
                    citing_map[doi] = future.result()
                    completed += 1
                    if progress_callback and completed % 5 == 0:
                        progress_callback(completed, total_articles)
                except Exception as e:
                    if SHOW_DEBUG_LOGS:
                        print(f"⚠️ Ошибка обработки {doi}: {e}")
                    citing_map[doi] = []
        
        self.citations_map = citing_map
        
        if SHOW_DEBUG_LOGS:
            total_citing = sum(len(v) for v in citing_map.values())
            print(f"✅ Собрано {total_citing} цитирующих DOI для {len(citing_map)} статей")
        
        return citing_map
    
    def fetch_citation_metadata(self, progress_callback=None) -> Dict:
        """Загружает полные метаданные для всех цитирующих статей"""
        if not self.citations_map:
            return {}
        
        all_citing_dois = set()
        for citing_list in self.citations_map.values():
            all_citing_dois.update(citing_list)
        
        if not all_citing_dois:
            return {}
        
        if SHOW_DEBUG_LOGS:
            print(f"📖 Загрузка метаданных для {len(all_citing_dois)} цитирующих статей")
        
        citing_metadata = {}
        doi_list = list(all_citing_dois)
        total = len(doi_list)
        processed = 0
        
        base_url = "https://api.openalex.org/works"
        
        for batch in chunks(doi_list, 50):
            doi_query = '|'.join(batch)
            
            params = {
                'filter': f'doi:{doi_query}',
                'per-page': len(batch),
                'select': 'id,doi,title,publication_year,publication_date,cited_by_count,primary_location,authorships,open_access,topics,concepts'
            }
            
            data = self._smart_get(base_url, params)
            
            if data and data.get('results'):
                for item in data['results']:
                    doi = item.get('doi', '')
                    if doi:
                        doi = doi.replace('https://doi.org/', '')
                    
                    # Парсим авторов
                    authors = []
                    author_orcids = []
                    affiliations = []
                    countries = []
                    
                    for auth in item.get('authorships', []):
                        author_data = auth.get('author', {})
                        author_name = author_data.get('display_name', '')
                        if author_name:
                            authors.append(author_name)
                            orcid = author_data.get('orcid', '')
                            if orcid:
                                author_orcids.append(orcid.replace('https://orcid.org/', ''))
                        
                        for inst in auth.get('institutions', []):
                            affil = inst.get('display_name', '')
                            if affil:
                                affiliations.append(affil)
                                country_code = inst.get('country_code', '')
                                if country_code:
                                    countries.append(get_full_country_name(country_code))
                    
                    journal_name = 'Unknown'
                    publisher = 'Unknown'
                    primary_loc = item.get('primary_location', {})
                    if primary_loc:
                        source = primary_loc.get('source', {})
                        journal_name = source.get('display_name', 'Unknown')
                        publisher = source.get('host_organization_name') or source.get('publisher', 'Unknown')
                    
                    oa = item.get('open_access', {})
                    is_oa = oa.get('is_oa', False)
                    oa_status = oa.get('oa_status', 'closed')
                    
                    # Topics
                    topics = []
                    subtopics = []
                    fields = []
                    domains = []
                    concepts = []
                    
                    primary_topic = item.get('primary_topic', {})
                    if primary_topic:
                        topic_name = primary_topic.get('display_name', '')
                        if topic_name:
                            topics.append(topic_name)
                        subfield = primary_topic.get('subfield', {}).get('display_name', '')
                        if subfield:
                            subtopics.append(subfield)
                        field = primary_topic.get('field', {}).get('display_name', '')
                        if field:
                            fields.append(field)
                        domain = primary_topic.get('domain', {}).get('display_name', '')
                        if domain:
                            domains.append(domain)
                    
                    for topic in item.get('topics', []):
                        topic_name = topic.get('display_name', '')
                        if topic_name and topic_name not in topics:
                            topics.append(topic_name)
                        subfield = topic.get('subfield', {}).get('display_name', '')
                        if subfield and subfield not in subtopics:
                            subtopics.append(subfield)
                        field = topic.get('field', {}).get('display_name', '')
                        if field and field not in fields:
                            fields.append(field)
                        domain = topic.get('domain', {}).get('display_name', '')
                        if domain and domain not in domains:
                            domains.append(domain)
                    
                    for concept in item.get('concepts', []):
                        concept_name = concept.get('display_name', '')
                        if concept_name:
                            concepts.append(concept_name)
                    
                    metadata = {
                        'id': item.get('id', '').replace('https://openalex.org/', ''),
                        'doi': doi,
                        'title': item.get('title', 'No title'),
                        'publication_year': item.get('publication_year'),
                        'publication_date': item.get('publication_date', ''),
                        'cited_by_count': item.get('cited_by_count', 0),
                        'journal_name': journal_name,
                        'publisher': publisher,
                        'is_oa': is_oa,
                        'oa_status': oa_status,
                        'authors': authors,
                        'author_orcids': author_orcids,
                        'author_count': len(authors),
                        'affiliations': list(set(affiliations)),
                        'affiliation_count': len(set(affiliations)),
                        'countries': list(set(countries)),
                        'country_count': len(set(countries)),
                        'topics': list(set(topics)),
                        'subtopics': list(set(subtopics)),
                        'fields': list(set(fields)),
                        'domains': list(set(domains)),
                        'concepts': list(set(concepts))
                    }
                    
                    citing_metadata[doi] = metadata
            
            processed += len(batch)
            if progress_callback:
                progress_callback(processed, total)
            
            time.sleep(DELAY_BETWEEN_BATCHES)
        
        self.citing_metadata = citing_metadata
        
        if SHOW_DEBUG_LOGS:
            print(f"✅ Загружено метаданных для {len(citing_metadata)} цитирующих статей")
        
        return citing_metadata
    
    def calculate_metrics(self):
        """Рассчитывает все метрики для журнала"""
        if not self.articles:
            return
        
        if SHOW_DEBUG_LOGS:
            print("📊 Расчет метрик...")
        
        # Основные метрики по анализируемым статьям
        df = self.articles_df
        
        # Total Publications
        total_pubs = len(df)
        
        # Total Citations
        total_citations = df['cited_by_count'].sum() if not df.empty else 0
        
        # h-index
        citations_sorted = sorted([c for c in df['cited_by_count'] if c > 0], reverse=True)
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
        
        # i10-index и i100-index
        i10_index = sum(1 for c in citations_sorted if c >= 10)
        i100_index = sum(1 for c in citations_sorted if c >= 100)
        
        # Avg Citations
        avg_citations = df['cited_by_count'].mean() if not df.empty else 0
        
        # Median Citations
        median_citations = df['cited_by_count'].median() if not df.empty else 0
        
        # Max Citations
        max_citations = df['cited_by_count'].max() if not df.empty else 0
        
        # Open Access
        oa_counts = df['oa_status'].value_counts().to_dict() if not df.empty else {}
        oa_breakdown = {
            'gold': oa_counts.get('gold', 0),
            'hybrid': oa_counts.get('hybrid', 0),
            'green': oa_counts.get('green', 0),
            'bronze': oa_counts.get('bronze', 0),
            'closed': oa_counts.get('closed', 0),
            'unknown': oa_counts.get('unknown', 0)
        }
        
        # Active Years
        active_years = len(df['publication_year'].unique()) if not df.empty else 0
        
        # Unique Authors
        all_authors = []
        for authors in df['authors']:
            all_authors.extend(authors)
        unique_authors = len(set(all_authors))
        
        # Unique Affiliations
        all_affiliations = []
        for affils in df['affiliations']:
            all_affiliations.extend(affils)
        unique_affiliations = len(set(all_affiliations))
        
        # Unique Countries
        all_countries = []
        for countries in df['countries']:
            all_countries.extend(countries)
        unique_countries = len(set(all_countries))
        
        # Avg Authors/Paper
        avg_authors_per_paper = df['author_count'].mean() if not df.empty else 0
        
        # Avg Affiliations/Paper
        avg_affiliations_per_paper = df['affiliation_count'].mean() if not df.empty else 0
        
        # Avg Countries/Paper
        avg_countries_per_paper = df['country_count'].mean() if not df.empty else 0
        
        # International Collaboration Rate
        international_count = 0
        total_pubs_with_countries = 0
        for countries in df['countries']:
            if countries:
                total_pubs_with_countries += 1
                if len(set(countries)) > 1:
                    international_count += 1
        international_collab_rate = international_count / total_pubs_with_countries if total_pubs_with_countries > 0 else 0
        
        # Unique Citing Authors
        citing_authors = []
        for metadata in self.citing_metadata.values():
            citing_authors.extend(metadata.get('authors', []))
        unique_citing_authors = len(set(citing_authors))
        
        # Unique Citing Affiliations
        citing_affiliations = []
        for metadata in self.citing_metadata.values():
            citing_affiliations.extend(metadata.get('affiliations', []))
        unique_citing_affiliations = len(set(citing_affiliations))
        
        # Unique Citing Countries
        citing_countries = []
        for metadata in self.citing_metadata.values():
            citing_countries.extend(metadata.get('countries', []))
        unique_citing_countries = len(set(citing_countries))
        
        # Unique Citing Journals
        citing_journals = []
        for metadata in self.citing_metadata.values():
            journal = metadata.get('journal_name', '')
            if journal:
                citing_journals.append(journal)
        unique_citing_journals = len(set(citing_journals))
        
        # Unique Citing Publishers
        citing_publishers = []
        for metadata in self.citing_metadata.values():
            publisher = metadata.get('publisher', '')
            if publisher:
                citing_publishers.append(publisher)
        unique_citing_publishers = len(set(citing_publishers))
        
        # Total Citing Works
        total_citing_works = len(self.citing_metadata)
        
        # Author Analysis
        author_stats = defaultdict(lambda: {'publications': 0, 'citations': 0, 'orcids': [], 'affiliations': set(), 'countries': set()})
        
        for idx, row in df.iterrows():
            for i, author in enumerate(row['authors']):
                author_stats[author]['publications'] += 1
                author_stats[author]['citations'] += row['cited_by_count']
                if i < len(row['author_orcids']):
                    author_stats[author]['orcids'].append(row['author_orcids'][i])
                author_stats[author]['affiliations'].update(row['affiliations'])
                author_stats[author]['countries'].update(row['countries'])
        
        # Сортируем авторов по убыванию цитирований
        sorted_authors = sorted(author_stats.items(), key=lambda x: x[1]['citations'], reverse=True)
        
        author_analysis = []
        for rank, (name, data) in enumerate(sorted_authors, 1):
            author_analysis.append({
                'rank': rank,
                'name': name,
                'orcid': data['orcids'][0] if data['orcids'] else '',
                'affiliations': ', '.join(list(data['affiliations'])[:3]),
                'countries': ', '.join(list(data['countries'])[:3]),
                'publications': data['publications'],
                'citations': data['citations']
            })
        
        # Top Affiliations
        affiliation_counts = Counter(all_affiliations)
        top_affiliations = dict(affiliation_counts.most_common(10))
        
        # Geographic Analysis
        # 5.3.1 Unique Countries per Publication (Collaboration Level)
        unique_countries_per_pub = []
        for countries in df['countries']:
            if countries:
                unique_countries_per_pub.append(len(set(countries)))
        avg_unique_countries = np.mean(unique_countries_per_pub) if unique_countries_per_pub else 0
        
        # 5.3.2 Authors per Country (Individual Distribution)
        author_country_counts = Counter()
        for idx, row in df.iterrows():
            for i, author in enumerate(row['authors']):
                if i < len(row['countries']):
                    # Берем первую страну автора (если есть)
                    if row['countries']:
                        author_country_counts[row['countries'][0]] += 1
        
        # 5.3.3 Collaboration Patterns
        single_country = 0
        international = 0
        for countries in df['countries']:
            if countries:
                if len(set(countries)) == 1:
                    single_country += 1
                else:
                    international += 1
        
        # 5.3.4 Collaboration Couples
        country_pairs = Counter()
        for countries in df['countries']:
            if len(set(countries)) >= 2:
                unique_countries = list(set(countries))
                for i in range(len(unique_countries)):
                    for j in range(i+1, len(unique_countries)):
                        pair = tuple(sorted([unique_countries[i], unique_countries[j]]))
                        country_pairs[pair] += 1
        
        top_country_pairs = dict(country_pairs.most_common(10))
        
        # Citation Dynamics by Year
        citation_dynamics = defaultdict(lambda: defaultdict(int))
        
        for article_doi, citing_dois in self.citations_map.items():
            article_year = None
            for article in self.articles:
                if article['doi'] == article_doi:
                    article_year = article['publication_year']
                    break
            
            if not article_year:
                continue
            
            for citing_doi in citing_dois:
                citing_meta = self.citing_metadata.get(citing_doi, {})
                citing_year = citing_meta.get('publication_year')
                if citing_year and citing_year >= article_year:
                    citation_dynamics[article_year][citing_year] += 1
        
        self.citation_dynamics = citation_dynamics
        
        # Cumulative Citations
        cumulative = defaultdict(int)
        all_years = sorted(set([y for years in citation_dynamics.values() for y in years.keys()]))
        running_total = 0
        for year in all_years:
            year_total = 0
            for pub_year, years_dict in citation_dynamics.items():
                year_total += years_dict.get(year, 0)
            running_total += year_total
            cumulative[year] = running_total
        
        self.cumulative_citations = dict(cumulative)
        
        # Heatmap Data
        heatmap_data = defaultdict(lambda: defaultdict(int))
        for pub_year, years_dict in citation_dynamics.items():
            for cite_year, count in years_dict.items():
                if cite_year >= pub_year:
                    heatmap_data[pub_year][cite_year] = count
        
        self.heatmap_data = heatmap_data
        
        # Most Cited Publications
        most_cited = df.nlargest(10, 'cited_by_count')[['doi', 'title', 'publication_year', 'cited_by_count', 'authors', 'journal_name']].to_dict('records')
        
        # Top Citing Authors
        citing_author_counts = Counter(citing_authors)
        top_citing_authors = dict(citing_author_counts.most_common(10))
        
        # Top Citing Affiliations
        citing_affiliation_counts = Counter(citing_affiliations)
        top_citing_affiliations = dict(citing_affiliation_counts.most_common(10))
        
        # Top Citing Countries
        citing_country_counts = Counter(citing_countries)
        top_citing_countries = dict(citing_country_counts.most_common(10))
        
        # Top Citing Journals
        citing_journal_counts = Counter(citing_journals)
        top_citing_journals = dict(citing_journal_counts.most_common(10))
        
        # Top Citing Publishers
        citing_publisher_counts = Counter(citing_publishers)
        top_citing_publishers = dict(citing_publisher_counts.most_common(10))
        
        # Topics Analysis
        # 8.1 Topics Table
        analyzed_topics = defaultdict(int)
        citing_topics = defaultdict(int)
        analyzed_topic_first_year = {}
        analyzed_topic_peak_year = {}
        citing_topic_first_year = {}
        citing_topic_peak_year = {}
        
        for article in self.articles:
            for topic in article.get('topics', []):
                analyzed_topics[topic] += 1
                year = article['publication_year']
                if topic not in analyzed_topic_first_year or year < analyzed_topic_first_year[topic]:
                    analyzed_topic_first_year[topic] = year
                if topic not in analyzed_topic_peak_year or analyzed_topics[topic] > analyzed_topics[analyzed_topic_peak_year[topic]]:
                    analyzed_topic_peak_year[topic] = year
        
        for metadata in self.citing_metadata.values():
            for topic in metadata.get('topics', []):
                citing_topics[topic] += 1
                year = metadata['publication_year']
                if year:
                    if topic not in citing_topic_first_year or year < citing_topic_first_year[topic]:
                        citing_topic_first_year[topic] = year
                    if topic not in citing_topic_peak_year or citing_topics[topic] > citing_topics[citing_topic_peak_year[topic]]:
                        citing_topic_peak_year[topic] = year
        
        total_analyzed = len(self.articles)
        total_citing = len(self.citing_metadata)
        
        topics_table = []
        all_topics = set(analyzed_topics.keys()) | set(citing_topics.keys())
        
        for topic in all_topics:
            analyzed_count = analyzed_topics.get(topic, 0)
            citing_count = citing_topics.get(topic, 0)
            analyzed_norm = analyzed_count / total_analyzed if total_analyzed > 0 else 0
            citing_norm = citing_count / total_citing if total_citing > 0 else 0
            total_norm = (analyzed_count + citing_count) / (total_analyzed + total_citing) if (total_analyzed + total_citing) > 0 else 0
            first_year = analyzed_topic_first_year.get(topic, citing_topic_first_year.get(topic, None))
            peak_year = analyzed_topic_peak_year.get(topic, citing_topic_peak_year.get(topic, None))
            
            topics_table.append({
                'topic': topic,
                'analyzed_count': analyzed_count,
                'citing_count': citing_count,
                'analyzed_norm': analyzed_norm,
                'citing_norm': citing_norm,
                'total_norm': total_norm,
                'first_year': first_year,
                'peak_year': peak_year
            })
        
        topics_table.sort(key=lambda x: x['total_norm'], reverse=True)
        
        # 8.2 Top Topics, Subtopics, Fields, Domains, Concepts
        all_analyzed_topics = []
        all_analyzed_subtopics = []
        all_analyzed_fields = []
        all_analyzed_domains = []
        all_analyzed_concepts = []
        all_citing_topics = []
        all_citing_subtopics = []
        all_citing_fields = []
        all_citing_domains = []
        all_citing_concepts = []
        
        for article in self.articles:
            all_analyzed_topics.extend(article.get('topics', []))
            all_analyzed_subtopics.extend(article.get('subtopics', []))
            all_analyzed_fields.extend(article.get('fields', []))
            all_analyzed_domains.extend(article.get('domains', []))
            all_analyzed_concepts.extend(article.get('concepts', []))
        
        for metadata in self.citing_metadata.values():
            all_citing_topics.extend(metadata.get('topics', []))
            all_citing_subtopics.extend(metadata.get('subtopics', []))
            all_citing_fields.extend(metadata.get('fields', []))
            all_citing_domains.extend(metadata.get('domains', []))
            all_citing_concepts.extend(metadata.get('concepts', []))
        
        top_topics = Counter(all_analyzed_topics + all_citing_topics).most_common(10)
        top_subtopics = Counter(all_analyzed_subtopics + all_citing_subtopics).most_common(10)
        top_fields = Counter(all_analyzed_fields + all_citing_fields).most_common(10)
        top_domains = Counter(all_analyzed_domains + all_citing_domains).most_common(10)
        top_concepts = Counter(all_analyzed_concepts + all_citing_concepts).most_common(10)
        
        # Detailed Citations
        detailed_citations = {}
        for article in self.articles:
            doi = article['doi']
            if doi in self.citations_map and self.citations_map[doi]:
                citations_list = []
                for citing_doi in self.citations_map[doi]:
                    citing_meta = self.citing_metadata.get(citing_doi, {})
                    if citing_meta:
                        citations_list.append({
                            'citing_title': citing_meta.get('title', 'No title'),
                            'citing_year': citing_meta.get('publication_year'),
                            'citing_date': citing_meta.get('publication_date', ''),
                            'citing_journal': citing_meta.get('journal_name', 'Unknown'),
                            'citing_publisher': citing_meta.get('publisher', 'Unknown'),
                            'citing_doi': citing_doi,
                            'citation_lag': citing_meta.get('publication_year', 0) - article['publication_year'] if citing_meta.get('publication_year') and article['publication_year'] else None,
                            'citing_authors': citing_meta.get('authors', []),
                            'citing_countries': citing_meta.get('countries', []),
                            'citing_topics': citing_meta.get('topics', [])
                        })
                
                detailed_citations[doi] = {
                    'title': article['title'],
                    'year': article['publication_year'],
                    'doi': doi,
                    'total_citations': len(citations_list),
                    'citations': citations_list
                }
        
        # Сохраняем все метрики
        self.stats = {
            'total_publications': total_pubs,
            'total_citations': total_citations,
            'h_index': h_index,
            'g_index': g_index,
            'i10_index': i10_index,
            'i100_index': i100_index,
            'avg_citations': avg_citations,
            'median_citations': median_citations,
            'max_citations': max_citations,
            'oa_breakdown': oa_breakdown,
            'active_years': active_years,
            'unique_authors': unique_authors,
            'unique_affiliations': unique_affiliations,
            'unique_countries': unique_countries,
            'avg_authors_per_paper': avg_authors_per_paper,
            'avg_affiliations_per_paper': avg_affiliations_per_paper,
            'avg_countries_per_paper': avg_countries_per_paper,
            'international_collab_rate': international_collab_rate,
            'unique_citing_authors': unique_citing_authors,
            'unique_citing_affiliations': unique_citing_affiliations,
            'unique_citing_countries': unique_citing_countries,
            'unique_citing_journals': unique_citing_journals,
            'unique_citing_publishers': unique_citing_publishers,
            'total_citing_works': total_citing_works,
            'author_analysis': author_analysis,
            'top_affiliations': top_affiliations,
            'avg_unique_countries': avg_unique_countries,
            'author_country_counts': dict(author_country_counts),
            'single_country': single_country,
            'international': international,
            'top_country_pairs': top_country_pairs,
            'citation_dynamics': dict(citation_dynamics),
            'cumulative_citations': self.cumulative_citations,
            'heatmap_data': dict(heatmap_data),
            'most_cited': most_cited,
            'top_citing_authors': top_citing_authors,
            'top_citing_affiliations': top_citing_affiliations,
            'top_citing_countries': top_citing_countries,
            'top_citing_journals': top_citing_journals,
            'top_citing_publishers': top_citing_publishers,
            'topics_table': topics_table,
            'top_topics': top_topics,
            'top_subtopics': top_subtopics,
            'top_fields': top_fields,
            'top_domains': top_domains,
            'top_concepts': top_concepts,
            'detailed_citations': detailed_citations
        }
        
        if SHOW_DEBUG_LOGS:
            print("✅ Расчет метрик завершен")
        
        return self.stats
    
    def get_stats(self) -> Dict:
        """Возвращает все рассчитанные метрики"""
        return self.stats
    
    def get_articles(self) -> List[Dict]:
        """Возвращает список статей"""
        return self.articles
    
    def get_citations_map(self) -> Dict:
        """Возвращает карту цитирований"""
        return self.citations_map
    
    def get_citing_metadata(self) -> Dict:
        """Возвращает метаданные цитирующих статей"""
        return self.citing_metadata

# ============================================
# ФУНКЦИЯ ДЛЯ ГЕНЕРАЦИИ HTML ОТЧЕТА
# ============================================

def generate_journal_html_report(analyzer: JournalAnalyzer, stats: Dict, logo_base64: Optional[str] = None, app_logo_base64: Optional[str] = None, theme_colors: Optional[Dict] = None, lang: str = 'en') -> str:
    """Генерирует HTML отчет для анализа журнала"""
    
    def t(key: str, **kwargs) -> str:
        return translate(key, lang, **kwargs)
    
    if theme_colors is None:
        theme_colors = {
            'primary': '#667eea',
            'secondary': '#f39c12'
        }
    
    primary = theme_colors.get('primary', '#667eea')
    secondary = theme_colors.get('secondary', '#f39c12')
    
    articles = analyzer.get_articles()
    citations_map = analyzer.get_citations_map()
    citing_metadata = analyzer.get_citing_metadata()
    
    # Подготовка данных для All Publications
    all_publications = []
    for article in sorted(articles, key=lambda x: x.get('publication_year', 0), reverse=True):
        all_publications.append({
            'id': article.get('id', ''),
            'title': article.get('title', 'No title'),
            'year': article.get('publication_year'),
            'authors': article.get('authors', []),
            'affiliations': article.get('affiliations', []),
            'countries': article.get('countries', []),
            'citations': article.get('cited_by_count', 0),
            'citations_per_year': article.get('cited_by_count', 0) / (2026 - article.get('publication_year', 2026) + 1) if article.get('publication_year') else 0,
            'doi': article.get('doi', ''),
            'journal_name': article.get('journal_name', 'Unknown'),
            'is_oa': article.get('is_oa', False),
            'oa_status': article.get('oa_status', 'closed')
        })
    
    # Year counts for filter
    year_counts = Counter([p['year'] for p in all_publications if p['year']])
    
    # OA Breakdown
    oa_breakdown = stats.get('oa_breakdown', {})
    oa_labels = {
        'gold': t('gold'),
        'hybrid': t('hybrid'),
        'green': t('green'),
        'bronze': t('bronze'),
        'closed': t('closed'),
        'unknown': t('unknown')
    }
    
    # Build HTML
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>{t('app_title')} - {analyzer.issn}</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{
                font-family: 'Times New Roman', 'DejaVu Serif', serif;
                margin: 0;
                padding: 0;
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
            }}
            .sidebar h3 {{
                margin-bottom: 15px;
                font-size: 18px;
                font-weight: 600;
                color: white;
                border-bottom: 2px solid rgba(255,255,255,0.3);
                padding-bottom: 10px;
            }}
            .sidebar a {{
                color: rgba(255,255,255,0.85);
                text-decoration: none;
                display: block;
                padding: 8px 12px;
                margin: 2px 0;
                border-radius: 6px;
                transition: all 0.3s;
                font-size: 14px;
            }}
            .sidebar a:hover {{
                background: rgba(255,255,255,0.2);
                transform: translateX(5px);
                color: white;
            }}
            .sidebar .level-1 {{
                font-weight: 600;
                padding-left: 8px;
            }}
            .sidebar .level-2 {{
                padding-left: 25px;
                font-size: 13px;
                font-weight: 400;
            }}
            .sidebar .level-2:hover {{
                padding-left: 30px;
            }}
            .sidebar .icon {{
                margin-right: 8px;
            }}
            .main-content {{
                margin-left: 280px;
                padding: 30px 40px;
            }}
            .header {{
                background: linear-gradient(135deg, {primary} 0%, {secondary} 100%);
                color: white;
                padding: 30px 40px;
                border-radius: 15px;
                margin-bottom: 30px;
                text-align: center;
            }}
            .header h1 {{
                color: white;
                border-bottom: none;
                margin: 0;
                font-size: 28px;
            }}
            .header .subtitle {{
                opacity: 0.9;
                margin-top: 8px;
                font-size: 16px;
            }}
            .header .date {{
                opacity: 0.8;
                margin-top: 5px;
                font-size: 14px;
            }}
            .header-logo {{
                max-height: 120px;
                max-width: 300px;
                margin-bottom: 15px;
            }}
            .header-logo-app {{
                max-height: 100px;
                max-width: 300px;
                margin-bottom: 10px;
            }}
            .section {{
                background: white;
                border-radius: 15px;
                padding: 25px;
                margin-bottom: 30px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                border: 1px solid #e8e8e8;
            }}
            .section-title {{
                font-size: 22px;
                font-weight: 600;
                margin-bottom: 20px;
                padding-bottom: 10px;
                border-bottom: 3px solid {primary};
                display: flex;
                align-items: center;
                gap: 10px;
            }}
            .section-title .icon {{
                font-size: 24px;
            }}
            .subsection-title {{
                font-size: 18px;
                font-weight: 600;
                margin: 20px 0 15px 0;
                color: {primary};
                padding-bottom: 8px;
                border-bottom: 2px solid {primary}30;
            }}
            .metrics-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
                gap: 15px;
                margin: 15px 0;
            }}
            .metric-card {{
                background: #f8f9fa;
                padding: 15px;
                border-radius: 8px;
                border-left: 4px solid {primary};
                text-align: center;
                transition: transform 0.2s, box-shadow 0.2s;
            }}
            .metric-card:hover {{
                transform: translateY(-3px);
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
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
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 15px 0;
                font-family: 'Times New Roman', serif;
                font-size: 14px;
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
                border-bottom: 1px solid #e0e0e0;
                vertical-align: middle;
            }}
            tr:hover {{
                background-color: #f5f5f5;
            }}
            .table-container {{
                overflow-x: auto;
                max-height: 600px;
                overflow-y: auto;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
            }}
            .filter-section {{
                background: #f8f9fa;
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 15px;
                border: 1px solid #e0e0e0;
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
            }}
            .filter-row label {{
                font-weight: 500;
                font-size: 13px;
                color: #555;
                white-space: nowrap;
            }}
            .filter-row select, .filter-row input {{
                padding: 5px 10px;
                border: 1px solid #ccc;
                border-radius: 4px;
                font-size: 13px;
                background: white;
            }}
            .filter-row input {{
                width: 130px;
            }}
            .filter-row select {{
                min-width: 100px;
            }}
            .badge {{
                display: inline-block;
                padding: 3px 10px;
                border-radius: 12px;
                font-size: 11px;
                font-weight: 600;
                margin: 2px;
            }}
            .badge-success {{ background: #d4edda; color: #155724; }}
            .badge-warning {{ background: #fff3cd; color: #856404; }}
            .badge-danger {{ background: #f8d7da; color: #721c24; }}
            .badge-info {{ background: #d1ecf1; color: #0c5460; }}
            .badge-gold {{ background: #ffd700; color: #8b6d00; }}
            .badge-hybrid {{ background: #9b59b6; color: white; }}
            .badge-green {{ background: #27ae60; color: white; }}
            .badge-bronze {{ background: #cd7f32; color: white; }}
            .badge-closed {{ background: #95a5a6; color: white; }}
            .badge-unknown {{ background: #bdc3c7; color: #333; }}
            .doi-link {{
                color: #2980B9;
                text-decoration: none;
                font-size: 12px;
                word-break: break-all;
            }}
            .doi-link:hover {{
                text-decoration: underline;
            }}
            .collapser {{
                cursor: pointer;
                padding: 12px 15px;
                background: #f8f9fa;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                margin-bottom: 8px;
                transition: all 0.3s;
                display: flex;
                flex-wrap: wrap;
                align-items: center;
                gap: 8px;
            }}
            .collapser:hover {{
                background: #e8f0fe;
                border-color: {primary};
                transform: translateX(3px);
            }}
            .collapser strong {{
                flex: 1;
                min-width: 200px;
            }}
            .citation-count {{
                background: {primary};
                color: white;
                padding: 2px 10px;
                border-radius: 12px;
                font-size: 12px;
                font-weight: 600;
            }}
            .citation-detail {{
                padding: 12px 15px;
                margin: 5px 0 5px 20px;
                background: #fafafa;
                border-left: 3px solid {secondary};
                border-radius: 4px;
                font-size: 13px;
            }}
            .citation-detail .cite-meta {{
                margin-top: 5px;
                color: #555;
                font-size: 12px;
            }}
            .citation-detail .cite-meta strong {{
                color: #333;
            }}
            .heatmap-cell {{
                padding: 4px 8px;
                text-align: center;
                font-size: 13px;
                border-radius: 3px;
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
            .collab-grid {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
                margin: 15px 0;
            }}
            .collab-box {{
                background: #f8f9fa;
                padding: 15px;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
            }}
            .collab-box h4 {{
                margin: 0 0 10px 0;
                color: #2C3E50;
            }}
            .collab-box .value {{
                font-size: 28px;
                font-weight: bold;
                color: {primary};
            }}
            .collab-box .label {{
                font-size: 13px;
                color: #666;
            }}
            .word-wrap {{
                word-wrap: break-word;
                max-width: 300px;
            }}
            @media print {{
                .sidebar {{ display: none; }}
                .main-content {{ margin-left: 0; }}
            }}
            @media (max-width: 768px) {{
                .sidebar {{ display: none; }}
                .main-content {{ margin-left: 0; padding: 20px; }}
                .filter-row {{
                    flex-direction: column;
                    align-items: stretch;
                }}
                .filter-row > div {{
                    flex-wrap: wrap;
                }}
                .collab-grid {{
                    grid-template-columns: 1fr;
                }}
                .metrics-grid {{
                    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
                }}
            }}
        </style>
    </head>
    <body>
        <div class="sidebar">
            <h3>📊 {t('app_title')}</h3>
            <a href="#overview" class="level-1"><span class="icon">📊</span> {t('overview')}</a>
            <a href="#analyzed_articles" class="level-1"><span class="icon">📄</span> {t('analyzed_articles_section')}</a>
            <a href="#author_analysis" class="level-2"><span class="icon">👤</span> {t('author_analysis_section')}</a>
            <a href="#top_affiliations" class="level-2"><span class="icon">🏛️</span> {t('top_affiliations_section')}</a>
            <a href="#geographic_analysis" class="level-2"><span class="icon">🌍</span> {t('geographic_analysis_section')}</a>
            <a href="#citation_analysis" class="level-1"><span class="icon">📈</span> {t('citation_analysis_section')}</a>
            <a href="#citation_dynamics" class="level-2"><span class="icon">📊</span> {t('citation_dynamics_section')}</a>
            <a href="#cumulative_citations" class="level-2"><span class="icon">📈</span> {t('cumulative_citations_section')}</a>
            <a href="#heatmap" class="level-2"><span class="icon">🔥</span> {t('heatmap_section')}</a>
            <a href="#most_cited" class="level-2"><span class="icon">🏆</span> {t('most_cited_section')}</a>
            <a href="#citing_works" class="level-1"><span class="icon">📚</span> {t('citing_works_section')}</a>
            <a href="#top_citing_authors" class="level-2"><span class="icon">👤</span> {t('top_authors_section')}</a>
            <a href="#top_citing_affiliations" class="level-2"><span class="icon">🏛️</span> {t('top_affils_section')}</a>
            <a href="#top_citing_countries" class="level-2"><span class="icon">🌍</span> {t('top_countries_section')}</a>
            <a href="#top_citing_journals" class="level-2"><span class="icon">📰</span> {t('top_journals_section')}</a>
            <a href="#top_citing_publishers" class="level-2"><span class="icon">📰</span> {t('top_publishers_section')}</a>
            <a href="#topics_analysis" class="level-1"><span class="icon">🏷️</span> {t('topics_analysis_section')}</a>
            <a href="#topics_table" class="level-2"><span class="icon">📊</span> {t('topics')}</a>
            <a href="#top_topics" class="level-2"><span class="icon">🏆</span> {t('top_topics')}</a>
            <a href="#detailed_citations" class="level-1"><span class="icon">📋</span> {t('detailed_citations_section')}</a>
            <a href="#all_publications" class="level-1"><span class="icon">📚</span> {t('all_publications_section')}</a>
        </div>
        
        <div class="main-content">
            <div class="header">
                {f'<img src="data:image/png;base64,{app_logo_base64}" class="header-logo-app" alt="App Logo">' if app_logo_base64 else ''}
                {f'<img src="data:image/png;base64,{logo_base64}" class="header-logo" alt="Journal Logo">' if logo_base64 else ''}
                <h1>📊 {t('app_title')}</h1>
                <div class="subtitle">ISSN: {analyzer.issn}</div>
                <div class="date">{t('report_preview')}: {datetime.now().strftime('%d.%m.%Y')}</div>
            </div>
            
            <!-- ============================================ -->
            <!-- OVERVIEW SECTION -->
            <!-- ============================================ -->
            <div id="overview" class="section">
                <div class="section-title"><span class="icon">📊</span> {t('overview')}</div>
                
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-value">{stats.get('total_publications', 0)}</div>
                        <div class="metric-label">{t('publications')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{stats.get('total_citations', 0):,}</div>
                        <div class="metric-label">{t('total_citations')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{stats.get('h_index', 0)}</div>
                        <div class="metric-label">{t('h_index')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{stats.get('g_index', 0)}</div>
                        <div class="metric-label">{t('g_index')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{stats.get('i10_index', 0)}</div>
                        <div class="metric-label">{t('i10_index')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{stats.get('i100_index', 0)}</div>
                        <div class="metric-label">{t('i100_index')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{stats.get('avg_citations', 0):.1f}</div>
                        <div class="metric-label">{t('avg_citations')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{stats.get('active_years', 0)}</div>
                        <div class="metric-label">{t('active_years')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{stats.get('unique_authors', 0)}</div>
                        <div class="metric-label">{t('unique_authors')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{stats.get('unique_affiliations', 0)}</div>
                        <div class="metric-label">{t('unique_affiliations')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{stats.get('unique_countries', 0)}</div>
                        <div class="metric-label">{t('unique_countries')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{stats.get('avg_authors_per_paper', 0):.1f}</div>
                        <div class="metric-label">{t('avg_authors_per_paper')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{stats.get('avg_affiliations_per_paper', 0):.1f}</div>
                        <div class="metric-label">{t('avg_affiliations_per_paper')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{stats.get('avg_countries_per_paper', 0):.1f}</div>
                        <div class="metric-label">{t('avg_countries_per_paper')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{stats.get('international_collab_rate', 0)*100:.1f}%</div>
                        <div class="metric-label">{t('international_collaboration_rate')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{stats.get('unique_citing_authors', 0)}</div>
                        <div class="metric-label">{t('unique_citing_authors')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{stats.get('unique_citing_affiliations', 0)}</div>
                        <div class="metric-label">{t('unique_citing_affiliations')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{stats.get('unique_citing_countries', 0)}</div>
                        <div class="metric-label">{t('unique_citing_countries')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{stats.get('unique_citing_journals', 0)}</div>
                        <div class="metric-label">{t('unique_citing_journals')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{stats.get('unique_citing_publishers', 0)}</div>
                        <div class="metric-label">{t('unique_citing_publishers')}</div>
                    </div>
                </div>
                
                <div class="subsection-title">📊 {t('open_access')}</div>
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-value">{oa_breakdown.get('gold', 0)}</div>
                        <div class="metric-label"><span class="badge badge-gold">{t('gold')}</span></div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{oa_breakdown.get('hybrid', 0)}</div>
                        <div class="metric-label"><span class="badge badge-hybrid">{t('hybrid')}</span></div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{oa_breakdown.get('green', 0)}</div>
                        <div class="metric-label"><span class="badge badge-green">{t('green')}</span></div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{oa_breakdown.get('bronze', 0)}</div>
                        <div class="metric-label"><span class="badge badge-bronze">{t('bronze')}</span></div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{oa_breakdown.get('closed', 0)}</div>
                        <div class="metric-label"><span class="badge badge-closed">{t('closed')}</span></div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{oa_breakdown.get('unknown', 0)}</div>
                        <div class="metric-label"><span class="badge badge-unknown">{t('unknown')}</span></div>
                    </div>
                </div>
            </div>
            
            <!-- ============================================ -->
            <!-- ANALYZED ARTICLES SECTION -->
            <!-- ============================================ -->
            <div id="analyzed_articles" class="section">
                <div class="section-title"><span class="icon">📄</span> {t('analyzed_articles_section')}</div>
                
                <!-- 5.1 Author Analysis -->
                <div id="author_analysis" class="subsection-title">👤 {t('author_analysis_section')}</div>
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
                                <th>{t('citations_count')}</th>
                            </tr>
                        </thead>
                        <tbody>
                            {''.join([
                                f"<tr>"
                                f"<td>{a['rank']}</td>"
                                f"<td>{html.escape(a['name'])}</td>"
                                f"<td>{a['orcid']}</td>"
                                f"<td>{html.escape(a['affiliations'])}</td>"
                                f"<td>{html.escape(a['countries'])}</td>"
                                f"<td>{a['publications']}</td>"
                                f"<td>{a['citations']}</td>"
                                f"</tr>"
                                for a in stats.get('author_analysis', [])[:50]
                            ])}
                        </tbody>
                    </table>
                </div>
                
                <!-- 5.2 Top Affiliations -->
                <div id="top_affiliations" class="subsection-title">🏛️ {t('top_affiliations_section')}</div>
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>{t('rank')}</th>
                                <th>{t('affiliations')}</th>
                                <th>{t('publications_count')}</th>
                            </tr>
                        </thead>
                        <tbody>
                            {''.join([
                                f"<tr><td>{i+1}</td><td>{html.escape(affil)}</td><td>{count}</td></tr>"
                                for i, (affil, count) in enumerate(stats.get('top_affiliations', {}).items())
                            ])}
                        </tbody>
                    </table>
                </div>
                
                <!-- 5.3 Geographic Analysis -->
                <div id="geographic_analysis" class="subsection-title">🌍 {t('geographic_analysis_section')}</div>
                
                <div class="subsection-title" style="font-size: 16px; margin-top: 10px;">{t('unique_countries_per_publication')}</div>
                <div style="margin-bottom: 15px;">
                    <span style="font-weight: bold;">{t('avg_countries_per_paper')}:</span> {stats.get('avg_countries_per_paper', 0):.2f}
                </div>
                
                <div class="subsection-title" style="font-size: 16px; margin-top: 10px;">{t('authors_per_country')}</div>
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
                                f"<tr><td>{i+1}</td><td>{html.escape(country)}</td><td>{count}</td></tr>"
                                for i, (country, count) in enumerate(stats.get('author_country_counts', {}).items())
                            ])}
                        </tbody>
                    </table>
                </div>
                
                <div class="subsection-title" style="font-size: 16px; margin-top: 10px;">{t('collaboration_patterns')}</div>
                <div class="collab-grid">
                    <div class="collab-box">
                        <h4>{t('single_country')}</h4>
                        <div class="value">{stats.get('single_country', 0)}</div>
                        <div class="label">{t('publications')}</div>
                    </div>
                    <div class="collab-box">
                        <h4>{t('international')}</h4>
                        <div class="value">{stats.get('international', 0)}</div>
                        <div class="label">{t('publications')}</div>
                    </div>
                </div>
                
                <div class="subsection-title" style="font-size: 16px; margin-top: 10px;">{t('collaboration_couples')}</div>
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>{t('rank')}</th>
                                <th>{t('country_pair')}</th>
                                <th>{t('frequency')}</th>
                            </tr>
                        </thead>
                        <tbody>
                            {''.join([
                                f"<tr><td>{i+1}</td><td>{' & '.join(pair)}</td><td>{count}</td></tr>"
                                for i, (pair, count) in enumerate(stats.get('top_country_pairs', {}).items())
                            ])}
                        </tbody>
                    </table>
                </div>
            </div>
            
            <!-- ============================================ -->
            <!-- CITATION ANALYSIS SECTION -->
            <!-- ============================================ -->
            <div id="citation_analysis" class="section">
                <div class="section-title"><span class="icon">📈</span> {t('citation_analysis_section')}</div>
                
                <!-- 6.1 Citation Dynamics by Year -->
                <div id="citation_dynamics" class="subsection-title">📊 {t('citation_dynamics_section')}</div>
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
                                f"<tr><td>{pub_year}</td><td>{cite_year}</td><td>{count}</td></tr>"
                                for pub_year, years_dict in sorted(stats.get('citation_dynamics', {}).items())
                                for cite_year, count in sorted(years_dict.items())
                            ])}
                        </tbody>
                    </table>
                </div>
                
                <!-- 6.2 Cumulative Citations -->
                <div id="cumulative_citations" class="subsection-title">📈 {t('cumulative_citations_section')}</div>
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>{t('year')}</th>
                                <th>{t('cumulative')}</th>
                            </tr>
                        </thead>
                        <tbody>
                            {''.join([
                                f"<tr><td>{year}</td><td>{cum}</td></tr>"
                                for year, cum in sorted(stats.get('cumulative_citations', {}).items())
                            ])}
                        </tbody>
                    </table>
                </div>
                
                <!-- 6.3 Citation Network Heatmap -->
                <div id="heatmap" class="subsection-title">🔥 {t('heatmap_section')}</div>
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>{t('publication_year')} \\ {t('citation_year')}</th>
                                {''.join([
                                    f"<th>{year}</th>"
                                    for year in sorted(set([y for years in stats.get('heatmap_data', {}).values() for y in years.keys()]))
                                ])}
                            </tr>
                        </thead>
                        <tbody>
                            {''.join([
                                f"<tr>"
                                f"<td><strong>{pub_year}</strong></td>"
                                f"{''.join([
                                    f"<td style=\"background: {get_heatmap_color(stats.get('heatmap_data', {{}}).get(pub_year, {{}}).get(year, 0), max_val)}\">"
                                    f"{stats.get('heatmap_data', {{}}).get(pub_year, {{}}).get(year, '-')}"
                                    f"</td>"
                                    for year in sorted(set([y for years in stats.get('heatmap_data', {{}}).values() for y in years.keys()]))
                                ])}"
                                f"</tr>"
                                for pub_year in sorted(stats.get('heatmap_data', {{}}).keys())
                            ])}
                                f"</tr>"
                                for pub_year in sorted(stats.get('heatmap_data', {}).keys())
                            ])}
                        </tbody>
                    </table>
                </div>
                
                <!-- 6.4 Most Cited Publications -->
                <div id="most_cited" class="subsection-title">🏆 {t('most_cited_section')}</div>
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
                                <th>DOI</th>
                            </tr>
                        </thead>
                        <tbody>
                            {''.join([
                                f"<tr>"
                                f"<td>{i+1}</td>"
                                f"<td class=\"word-wrap\">{html.escape(article.get('title', 'No title'))}</td>"
                                f"<td>{article.get('publication_year', '')}</td>"
                                f"<td>{article.get('cited_by_count', 0)}</td>"
                                f"<td>{article.get('cited_by_count', 0) / (2026 - article.get('publication_year', 2026) + 1):.1f}</td>"
                                f"<td>{', '.join(article.get('authors', [])[:3])}{' +' + str(len(article.get('authors', []))-3) + ' more' if len(article.get('authors', [])) > 3 else ''}</td>"
                                f"<td><a href=\"https://doi.org/{article.get('doi', '')}\" target=\"_blank\" class=\"doi-link\">{article.get('doi', '')}</a></td>"
                                f"</tr>"
                                for i, article in enumerate(stats.get('most_cited', []))
                            ])}
                        </tbody>
                    </table>
                </div>
            </div>
            
            <!-- ============================================ -->
            <!-- CITING WORKS ANALYSIS SECTION -->
            <!-- ============================================ -->
            <div id="citing_works" class="section">
                <div class="section-title"><span class="icon">📚</span> {t('citing_works_section')}</div>
                
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-value">{stats.get('total_citing_works', 0):,}</div>
                        <div class="metric-label">{t('total_citing_works')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{stats.get('unique_citing_authors', 0):,}</div>
                        <div class="metric-label">{t('unique_citing_authors')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{stats.get('unique_citing_affiliations', 0):,}</div>
                        <div class="metric-label">{t('unique_citing_affiliations')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{stats.get('unique_citing_countries', 0)}</div>
                        <div class="metric-label">{t('unique_citing_countries')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{stats.get('unique_citing_journals', 0)}</div>
                        <div class="metric-label">{t('unique_citing_journals')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{stats.get('unique_citing_publishers', 0)}</div>
                        <div class="metric-label">{t('unique_citing_publishers')}</div>
                    </div>
                </div>
                
                <!-- 7.1 Top Citing Authors -->
                <div id="top_citing_authors" class="subsection-title">👤 {t('top_authors_section')}</div>
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>{t('rank')}</th>
                                <th>{t('authors')}</th>
                                <th>{t('citations_count')}</th>
                            </tr>
                        </thead>
                        <tbody>
                            {''.join([
                                f"<tr><td>{i+1}</td><td>{html.escape(author)}</td><td>{count}</td></tr>"
                                for i, (author, count) in enumerate(stats.get('top_citing_authors', {}).items())
                            ])}
                        </tbody>
                    </table>
                </div>
                
                <!-- 7.2 Top Citing Affiliations -->
                <div id="top_citing_affiliations" class="subsection-title">🏛️ {t('top_affils_section')}</div>
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>{t('rank')}</th>
                                <th>{t('affiliations')}</th>
                                <th>{t('citations_count')}</th>
                            </tr>
                        </thead>
                        <tbody>
                            {''.join([
                                f"<tr><td>{i+1}</td><td>{html.escape(affil)}</td><td>{count}</td></tr>"
                                for i, (affil, count) in enumerate(stats.get('top_citing_affiliations', {}).items())
                            ])}
                        </tbody>
                    </table>
                </div>
                
                <!-- 7.3 Top Citing Countries -->
                <div id="top_citing_countries" class="subsection-title">🌍 {t('top_countries_section')}</div>
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>{t('rank')}</th>
                                <th>{t('countries')}</th>
                                <th>{t('citations_count')}</th>
                            </tr>
                        </thead>
                        <tbody>
                            {''.join([
                                f"<tr><td>{i+1}</td><td>{html.escape(country)}</td><td>{count}</td></tr>"
                                for i, (country, count) in enumerate(stats.get('top_citing_countries', {}).items())
                            ])}
                        </tbody>
                    </table>
                </div>
                
                <!-- 7.4 Top Citing Journals -->
                <div id="top_citing_journals" class="subsection-title">📰 {t('top_journals_section')}</div>
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>{t('rank')}</th>
                                <th>{t('title')}</th>
                                <th>{t('citations_count')}</th>
                            </tr>
                        </thead>
                        <tbody>
                            {''.join([
                                f"<tr><td>{i+1}</td><td>{html.escape(journal)}</td><td>{count}</td></tr>"
                                for i, (journal, count) in enumerate(stats.get('top_citing_journals', {}).items())
                            ])}
                        </tbody>
                    </table>
                </div>
                
                <!-- 7.5 Top Citing Publishers -->
                <div id="top_citing_publishers" class="subsection-title">📰 {t('top_publishers_section')}</div>
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>{t('rank')}</th>
                                <th>{t('title')}</th>
                                <th>{t('citations_count')}</th>
                            </tr>
                        </thead>
                        <tbody>
                            {''.join([
                                f"<tr><td>{i+1}</td><td>{html.escape(publisher)}</td><td>{count}</td></tr>"
                                for i, (publisher, count) in enumerate(stats.get('top_citing_publishers', {}).items())
                            ])}
                        </tbody>
                    </table>
                </div>
            </div>
            
            <!-- ============================================ -->
            <!-- TOPICS ANALYSIS SECTION -->
            <!-- ============================================ -->
            <div id="topics_analysis" class="section">
                <div class="section-title"><span class="icon">🏷️</span> {t('topics_analysis_section')}</div>
                
                <!-- 8.1 Topics Table -->
                <div id="topics_table" class="subsection-title">📊 {t('topics')}</div>
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>{t('topics')}</th>
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
                            {''.join([
                                f"<tr>"
                                f"<td>{html.escape(topic['topic'])}</td>"
                                f"<td>{topic['analyzed_count']}</td>"
                                f"<td>{topic['citing_count']}</td>"
                                f"<td>{topic['analyzed_norm']:.3f}</td>"
                                f"<td>{topic['citing_norm']:.3f}</td>"
                                f"<td>{topic['total_norm']:.3f}</td>"
                                f"<td>{topic['first_year'] or '-'}</td>"
                                f"<td>{topic['peak_year'] or '-'}</td>"
                                f"</tr>"
                                for topic in stats.get('topics_table', [])[:50]
                            ])}
                        </tbody>
                    </table>
                </div>
                
                <!-- 8.2 Top Topics, Subtopics, Fields, Domains, Concepts -->
                <div id="top_topics" class="subsection-title">🏆 {t('top_topics')}</div>
                
                <div style="margin-bottom: 20px;">
                    <h4 style="color: {primary}; margin: 10px 0;">{t('topics')}</h4>
                    <div class="table-container">
                        <table>
                            <thead>
                                <tr><th>{t('rank')}</th><th>{t('topics')}</th><th>{t('citations_count')}</th></tr>
                            </thead>
                            <tbody>
                                {''.join([
                                    f"<tr><td>{i+1}</td><td>{html.escape(topic)}</td><td>{count}</td></tr>"
                                    for i, (topic, count) in enumerate(stats.get('top_topics', []))
                                ])}
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <div style="margin-bottom: 20px;">
                    <h4 style="color: {primary}; margin: 10px 0;">{t('subtopics')}</h4>
                    <div class="table-container">
                        <table>
                            <thead>
                                <tr><th>{t('rank')}</th><th>{t('subtopics')}</th><th>{t('citations_count')}</th></tr>
                            </thead>
                            <tbody>
                                {''.join([
                                    f"<tr><td>{i+1}</td><td>{html.escape(subtopic)}</td><td>{count}</td></tr>"
                                    for i, (subtopic, count) in enumerate(stats.get('top_subtopics', []))
                                ])}
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <div style="margin-bottom: 20px;">
                    <h4 style="color: {primary}; margin: 10px 0;">{t('fields')}</h4>
                    <div class="table-container">
                        <table>
                            <thead>
                                <tr><th>{t('rank')}</th><th>{t('fields')}</th><th>{t('citations_count')}</th></tr>
                            </thead>
                            <tbody>
                                {''.join([
                                    f"<tr><td>{i+1}</td><td>{html.escape(field)}</td><td>{count}</td></tr>"
                                    for i, (field, count) in enumerate(stats.get('top_fields', []))
                                ])}
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <div style="margin-bottom: 20px;">
                    <h4 style="color: {primary}; margin: 10px 0;">{t('domains')}</h4>
                    <div class="table-container">
                        <table>
                            <thead>
                                <tr><th>{t('rank')}</th><th>{t('domains')}</th><th>{t('citations_count')}</th></tr>
                            </thead>
                            <tbody>
                                {''.join([
                                    f"<tr><td>{i+1}</td><td>{html.escape(domain)}</td><td>{count}</td></tr>"
                                    for i, (domain, count) in enumerate(stats.get('top_domains', []))
                                ])}
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <div>
                    <h4 style="color: {primary}; margin: 10px 0;">{t('concepts')}</h4>
                    <div class="table-container">
                        <table>
                            <thead>
                                <tr><th>{t('rank')}</th><th>{t('concepts')}</th><th>{t('citations_count')}</th></tr>
                            </thead>
                            <tbody>
                                {''.join([
                                    f"<tr><td>{i+1}</td><td>{html.escape(concept)}</td><td>{count}</td></tr>"
                                    for i, (concept, count) in enumerate(stats.get('top_concepts', []))
                                ])}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
            
            <!-- ============================================ -->
            <!-- DETAILED CITATIONS SECTION -->
            <!-- ============================================ """
    
    # Detailed Citations
    detailed_citations = stats.get('detailed_citations', {})
    if detailed_citations:
        html_content += f"""
            <div id="detailed_citations" class="section">
                <div class="section-title"><span class="icon">📋</span> {t('detailed_citations_section')}</div>
                
                {''.join([
                    f'''
                    <div class="collapser" onclick="toggleCitations('{doi.replace('/', '_')}')">
                        <strong>{html.escape(data['title'])}</strong>
                        <span class="badge badge-info">{data['year']}</span>
                        <span class="citation-count">{data['total_citations']} {t('citations')}</span>
                        <span style="font-size: 12px; color: #666; margin-left: 10px;">DOI: {html.escape(doi)}</span>
                        <span style="float: right; font-size: 12px; color: #666;">{t('view_details')}</span>
                    </div>
                    <div id="citations_{doi.replace('/', '_')}" style="display: none;">
                        {''.join([
                            f'''
                            <div class="citation-detail">
                                <div><strong>{html.escape(cite['citing_title'])}</strong></div>
                                <div class="cite-meta">
                                    <strong>{t('citing_journal')}:</strong> {html.escape(cite['citing_journal'])} | 
                                    <strong>{t('citing_year')}:</strong> {cite['citing_year']} | 
                                    <strong>{t('citing_date')}:</strong> {cite['citing_date']} |
                                    <strong>{t('citation_lag')}:</strong> {cite['citation_lag'] or '-'} years
                                </div>
                                <div class="cite-meta">
                                    <strong>{t('authors')}:</strong> {', '.join(cite['citing_authors'][:5])}{' +' + str(len(cite['citing_authors'])-5) + ' more' if len(cite['citing_authors']) > 5 else ''} |
                                    <strong>{t('countries')}:</strong> {', '.join(cite['citing_countries'][:5])}{' +' + str(len(cite['citing_countries'])-5) + ' more' if len(cite['citing_countries']) > 5 else ''} |
                                    <strong>{t('topics')}:</strong> {', '.join(cite['citing_topics'][:3])}{' +' + str(len(cite['citing_topics'])-3) + ' more' if len(cite['citing_topics']) > 3 else ''}
                                </div>
                                <div class="cite-meta">
                                    <a href="https://doi.org/{cite['citing_doi']}" target="_blank" class="doi-link">DOI: {cite['citing_doi']}</a>
                                </div>
                            </div>
                            ''' for cite in data['citations']
                        ])}
                    </div>
                    ''' for doi, data in detailed_citations.items()
                ])}
            </div>
        """
    
    # All Publications
    html_content += f"""
            <!-- ============================================ -->
            <!-- ALL PUBLICATIONS SECTION -->
            <!-- ============================================ -->
            <div id="all_publications" class="section">
                <div class="section-title"><span class="icon">📚</span> {t('all_publications_section')}</div>
                
                <div class="filter-section">
                    <div class="filter-row">
                        <div>
                            <label for="yearFilter">{t('filter_by_year')}:</label>
                            <select id="yearFilter" onchange="filterPublications()">
                                <option value="">{t('all_years')}</option>
                                {''.join([
                                    f'<option value="{year}">{year}</option>'
                                    for year in sorted(year_counts.keys(), reverse=True)
                                ])}
                            </select>
                        </div>
                        <div>
                            <label for="titleFilter">{t('filter_by_title')}:</label>
                            <input type="text" id="titleFilter" placeholder="Search title..." onkeyup="filterPublications()">
                        </div>
                        <div>
                            <label for="authorFilter">{t('filter_by_author')}:</label>
                            <input type="text" id="authorFilter" placeholder="Author name..." onkeyup="filterPublications()">
                        </div>
                        <div>
                            <label for="affilFilter">{t('filter_by_affiliation')}:</label>
                            <input type="text" id="affilFilter" placeholder="Affiliation..." onkeyup="filterPublications()">
                        </div>
                        <div>
                            <label for="citationFilter">{t('filter_by_citations')}:</label>
                            <input type="number" id="citationFilter" placeholder="Min..." min="0" onchange="filterPublications()">
                        </div>
                        <div>
                            <span id="visibleCount" style="font-weight: 500;">{len(all_publications)} {t('publications')}</span>
                        </div>
                    </div>
                </div>
                
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
                                <th>DOI</th>
                                <th>{t('show_citations')}</th>
                            </tr>
                        </thead>
                        <tbody>
                            {''.join([
                                f'<tr data-year="{p["year"]}" data-authors="{",".join(p["authors"])}" data-affils="{",".join(p["affiliations"])}" data-citations="{p["citations"]}" data-title="{p["title"].lower()}">'
                                f'<td>{i+1}</td>'
                                f'<td class="word-wrap">{html.escape(p["title"])}</td>'
                                f'<td>{p["year"]}</td>'
                                f'<td>{", ".join(p["authors"][:3])}{" +" + str(len(p["authors"])-3) + " more" if len(p["authors"]) > 3 else ""}</td>'
                                f'<td>{", ".join(p["affiliations"][:2])}{" +" + str(len(p["affiliations"])-2) + " more" if len(p["affiliations"]) > 2 else ""}</td>'
                                f'<td><span class="citation-count">{p["citations"]}</span></td>'
                                f'<td>{p["citations_per_year"]:.1f}</td>'
                                f'<td><a href="https://doi.org/{p["doi"]}" target="_blank" class="doi-link">{p["doi"]}</a></td>'
                                f'<td>'
                                f'<button onclick="toggleCitations(\'{p["id"]}\')" style="padding: 3px 8px; border: none; border-radius: 4px; background: {primary}; color: white; cursor: pointer; font-size: 11px;">{t("show_citations")}</button>'
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
    
    <script>
        function toggleCitations(id) {{
            var element = document.getElementById('citations_' + id);
            if (element) {{
                if (element.style.display === 'none' || element.style.display === '') {{
                    element.style.display = 'block';
                }} else {{
                    element.style.display = 'none';
                }}
            }}
        }}
        
        function filterPublications() {{
            var yearFilter = document.getElementById('yearFilter').value;
            var titleFilter = document.getElementById('titleFilter').value.toLowerCase();
            var authorFilter = document.getElementById('authorFilter').value.toLowerCase();
            var affilFilter = document.getElementById('affilFilter').value.toLowerCase();
            var citationFilter = parseInt(document.getElementById('citationFilter').value) || 0;
            
            var rows = document.querySelectorAll('#publicationsTable tbody tr');
            var visibleCount = 0;
            
            rows.forEach(function(row) {{
                var year = row.getAttribute('data-year');
                var authors = row.getAttribute('data-authors').toLowerCase();
                var affils = row.getAttribute('data-affils').toLowerCase();
                var citations = parseInt(row.getAttribute('data-citations'));
                var title = row.getAttribute('data-title');
                
                var show = true;
                
                if (yearFilter && year !== yearFilter) show = false;
                if (titleFilter && !title.includes(titleFilter)) show = false;
                if (authorFilter && !authors.includes(authorFilter)) show = false;
                if (affilFilter && !affils.includes(affilFilter)) show = false;
                if (citations < citationFilter) show = false;
                
                row.style.display = show ? '' : 'none';
                if (show) visibleCount++;
            }});
            
            document.getElementById('visibleCount').textContent = visibleCount + ' publications';
        }}
        
        function sortTable(colIndex) {{
            var table = document.getElementById('publicationsTable');
            var tbody = table.tBodies[0];
            var rows = Array.from(tbody.rows);
            
            var isAsc = table.getAttribute('data-sort-asc') === 'true';
            
            rows.sort(function(a, b) {{
                var aVal = a.cells[colIndex].textContent.trim();
                var bVal = b.cells[colIndex].textContent.trim();
                
                var aNum = parseFloat(aVal.replace(/,/g, ''));
                var bNum = parseFloat(bVal.replace(/,/g, ''));
                
                if (!isNaN(aNum) && !isNaN(bNum)) {{
                    return isAsc ? aNum - bNum : bNum - aNum;
                }}
                
                return isAsc ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
            }});
            
            rows.forEach(function(row) {{
                tbody.appendChild(row);
            }});
            
            table.setAttribute('data-sort-asc', !isAsc);
        }}
    </script>
    </body>
    </html>
    """
    
    return html_content

def get_heatmap_color(value: int, max_val: int) -> str:
    """Возвращает цвет для ячейки тепловой карты"""
    if value == 0:
        return '#f0f0f0'
    
    ratio = value / max_val if max_val > 0 else 0
    intensity = max(0.1, min(1.0, ratio))
    
    # Используем градиент от светло-голубого к темно-синему
    r = int(200 - 180 * intensity)
    g = int(230 - 200 * intensity)
    b = int(255 - 200 * intensity)
    
    return f'#{r:02x}{g:02x}{b:02x}'

# ============================================
# ОСНОВНАЯ ФУНКЦИЯ ЗАПУСКА ДЛЯ STREAMLIT
# ============================================

def run_journal_analysis(issn: str, period: str, max_workers: int = 8, journal_logo: Optional[Dict] = None):
    """Запускает полный анализ журнала"""
    
    current_lang = st.session_state.get('language', 'en')
    def t(key: str, **kwargs) -> str:
        return translate(key, current_lang, **kwargs)
    
    if not issn:
        st.error(t('no_issn'))
        return
    
    if not period:
        st.error(t('no_period'))
        return
    
    period_result = parse_period(period)
    if not period_result:
        st.error(t('invalid_period'))
        return
    
    period_type, years = period_result
    
    st.cache_data.clear()
    
    st.info(f"🔍 {t('start_analysis')} ISSN: {issn}")
    
    # Прогресс-бары
    progress_container = st.empty()
    status_container = st.empty()
    analysis_progress = st.progress(0, text=t('start_analysis'))
    
    try:
        # Загружаем логотип приложения
        app_logo_base64 = None
        if os.path.exists("icon.png"):
            try:
                with open("icon.png", "rb") as f:
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
                    st.success(f"✅ Логотип журнала загружен: {filename}")
                    break
            except Exception as e:
                st.warning(f"⚠️ Ошибка загрузки логотипа журнала: {e}")
        
        # Создаем анализатор
        analyzer = JournalAnalyzer(issn, years, max_workers)
        
        # Этап 1: Загрузка статей журнала
        status_container.info(f"📡 {t('stage_1')}...")
        analysis_progress.progress(0.05, text=f"📡 {t('stage_1')}...")
        
        articles_count = 0
        def articles_progress(count):
            nonlocal articles_count
            articles_count = count
            progress = 0.05 + (count / 2000) * 0.15  # Предполагаем до 2000 статей
            analysis_progress.progress(min(0.20, progress), text=f"📡 {t('stage_1')}: {t('articles_loaded')} {count}")
        
        analyzer.fetch_articles(articles_progress)
        
        if not analyzer.articles:
            st.error(f"❌ {t('no_data')}")
            analysis_progress.empty()
            return
        
        total_articles = len(analyzer.articles)
        status_container.info(f"✅ {t('articles_loaded')}: {total_articles}")
        analysis_progress.progress(0.20, text=f"✅ {t('articles_loaded')}: {total_articles}")
        
        # Этап 2: Сбор цитирующих DOI
        status_container.info(f"⚡ {t('stage_2')}...")
        analysis_progress.progress(0.20, text=f"⚡ {t('stage_2')}...")
        
        citation_map = {}
        def citations_progress(current, total):
            progress = 0.20 + (current / total) * 0.30
            analysis_progress.progress(min(0.50, progress), text=f"⚡ {t('stage_2')}: {current}/{total} {t('citation_dois_collected')}")
        
        citation_map = analyzer.fetch_citations_parallel(citations_progress)
        total_citing_dois = sum(len(v) for v in citation_map.values())
        status_container.info(f"✅ {t('citation_dois_collected')}: {total_citing_dois}")
        analysis_progress.progress(0.50, text=f"✅ {t('citation_dois_collected')}: {total_citing_dois}")
        
        # Этап 3: Загрузка метаданных цитирований
        status_container.info(f"📖 {t('stage_3')}...")
        analysis_progress.progress(0.50, text=f"📖 {t('stage_3')}...")
        
        citing_metadata = {}
        def metadata_progress(current, total):
            progress = 0.50 + (current / total) * 0.30
            analysis_progress.progress(min(0.80, progress), text=f"📖 {t('stage_3')}: {current}/{total} {t('citation_metadata_fetched')}")
        
        citing_metadata = analyzer.fetch_citation_metadata(metadata_progress)
        status_container.info(f"✅ {t('citation_metadata_fetched')}: {len(citing_metadata)}")
        analysis_progress.progress(0.80, text=f"✅ {t('citation_metadata_fetched')}: {len(citing_metadata)}")
        
        # Этап 4: Анализ данных
        status_container.info(f"📊 {t('stage_4')}...")
        analysis_progress.progress(0.80, text=f"📊 {t('stage_4')}...")
        
        stats = analyzer.calculate_metrics()
        analysis_progress.progress(0.90, text=f"📊 {t('analysis_complete_text')}")
        
        # Этап 5: Генерация отчета
        status_container.info(f"📄 {t('stage_5')}...")
        analysis_progress.progress(0.90, text=f"📄 {t('stage_5')}...")
        
        theme_colors = {
            'primary': st.session_state.primary_color,
            'secondary': st.session_state.secondary_color
        }
        
        html_report = generate_journal_html_report(
            analyzer,
            stats,
            journal_logo_base64,
            app_logo_base64,
            theme_colors,
            current_lang
        )
        
        analysis_progress.progress(1.0, text=f"✅ {t('analysis_complete_text')}!")
        
        # Сохраняем в сессию
        st.session_state['html_report'] = html_report
        st.session_state['analysis_complete'] = True
        st.session_state['stats'] = stats
        st.session_state['analyzer'] = analyzer
        st.session_state['issn'] = issn
        
        st.success(f"✅ {t('analysis_complete')}")
        
        # Отображаем отчет
        st.markdown("---")
        st.markdown(f"## 📄 {t('html_report')}")
        
        # Скачивание
        st.download_button(
            label=f"📥 {t('download_report')}",
            data=html_report.encode('utf-8'),
            file_name=f"journal_analysis_{issn}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
            mime="text/html",
            width='stretch'
        )
        
        # Предпросмотр
        with st.expander(f"📋 {t('report_preview')}"):
            st.components.v1.html(html_report, height=800, scrolling=True)
        
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
    if 'html_report' not in st.session_state:
        st.session_state.html_report = ''
    if 'analysis_complete' not in st.session_state:
        st.session_state.analysis_complete = False
    if 'stats' not in st.session_state:
        st.session_state.stats = {}
    if 'analyzer' not in st.session_state:
        st.session_state.analyzer = None
    if 'issn' not in st.session_state:
        st.session_state.issn = ''
    
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
        st.markdown(f"### {t('app_title')}")
    st.markdown("---")
    
    # Tabs
    tab1, tab2 = st.tabs([
        t('analyze_journal'),
        t('reports')
    ])
    
    with tab1:
        st.markdown('<div class="custom-tab fade-in">', unsafe_allow_html=True)
        st.header(t('analyze_journal'))
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            issn_input = st.text_input(
                t('issn_input'),
                placeholder=t('issn_placeholder'),
                help=t('issn_help'),
                key='issn_input'
            )
            
            period_input = st.text_input(
                t('period_input'),
                placeholder=t('period_placeholder'),
                help=t('period_help'),
                key='period_input'
            )
        
        with col2:
            workers_slider = st.slider(
                t('workers_label'),
                min_value=4,
                max_value=12,
                value=8,
                step=1,
                help=t('workers_help'),
                key='workers_slider'
            )
            
            journal_logo_upload = st.file_uploader(
                t('upload_logo'),
                type=['png', 'jpg', 'jpeg', 'svg'],
                help=t('logo_help'),
                key='journal_logo_upload'
            )
        
        if st.button(t('analyze_button'), type="primary", width='stretch'):
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
                workers_slider,
                journal_logo_data
            )
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        if st.session_state.analysis_complete and st.session_state.html_report:
            st.markdown(f"## 📄 {t('html_report')}")
            
            st.download_button(
                label=f"📥 {t('download_report')}",
                data=st.session_state.html_report.encode('utf-8'),
                file_name=f"journal_analysis_{st.session_state.issn}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                mime="text/html",
                width='stretch'
            )
            
            st.markdown("---")
            
            with st.expander(f"📋 {t('report_preview')}", expanded=True):
                st.components.v1.html(st.session_state.html_report, height=800, scrolling=True)
        else:
            st.info(t('no_data'))

if __name__ == "__main__":
    main()
