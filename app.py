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
USE_CACHE = False  # Кэширование результатов (отключено, используется сессионное кэширование)
LOGO_PATH = None  # Путь к логотипу журнала (устанавливается через виджет)

# Лимиты для анализа
MAX_PUBLICATIONS_TO_ANALYZE = 1000  # Максимум статей для анализа
MIN_YEAR_FOR_TREND = 5  # Сколько лет для тренда

# Режим анализа источников данных
ANALYSIS_MODE = "journal_analysis"  # Новый режим для анализа журналов

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
        
        # Анализ журнала
        'journal_analysis': '📊 Journal Analysis',
        'issn_label': 'ISSN',
        'issn_placeholder': '0028-0836 or 0028-0836',
        'period_label': 'Analysis Period',
        'period_placeholder': '2020-2023 or 2020,2021,2022',
        'period_help': 'Enter as: 2020-2023 (range) or 2020,2021,2022 (list)',
        'workers_label': 'Parallel Threads',
        'workers_help': 'Number of parallel API requests (4-12 recommended)',
        'run_analysis': '🚀 Run Analysis',
        'no_issn': '⚠️ Please enter ISSN',
        'no_period': '⚠️ Please enter analysis period',
        'analysis_complete': '✅ Analysis complete!',
        'analysis_error': '❌ Analysis error: {error}',
        'cache_hit': '✅ Using cached results for {issn} ({period})',
        'cache_miss': '🔄 Running new analysis for {issn} ({period})',
        
        # Этапы анализа
        'stage1': '📚 Stage 1: Fetching journal articles...',
        'stage1_complete': '✅ Found {count} articles',
        'stage2': '🔄 Stage 2: Collecting citing DOIs...',
        'stage2_complete': '✅ Collected {count} citing DOIs',
        'stage3': '📊 Stage 3: Enriching analyzed articles...',
        'stage3_complete': '✅ Enriched {count} articles',
        'stage4': '📊 Stage 4: Enriching citing works...',
        'stage4_complete': '✅ Enriched {count} citing works',
        'stage5': '📄 Stage 5: Generating HTML report...',
        'stage5_complete': '✅ Report ready!',
        'stage_processing': 'Processing {current}/{total}',
        'stage_found': 'Found {count} items',
        
        # Метрики Overview
        'overview': 'Overview',
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
        
        # Open Access Breakdown
        'open_access_breakdown': 'Open Access Breakdown',
        'gold': 'Gold',
        'hybrid': 'Hybrid',
        'green': 'Green',
        'bronze': 'Bronze',
        'closed': 'Closed',
        'diamond': 'Diamond',
        'unknown': 'Unknown',
        
        # Analyzed Articles
        'analyzed_articles': 'Analyzed Articles',
        'author_analysis': 'Author Analysis',
        'top_affiliations': 'Top Affiliations',
        'geographic_analysis': 'Geographic Analysis',
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
        
        # Geographic Analysis
        'countries_per_publication': 'Countries per Publication (Collaboration Level)',
        'authors_per_country': 'Authors per Country (Individual Distribution)',
        'collaboration_patterns': 'Collaboration Patterns',
        'collaboration_couples': 'Collaboration Couples',
        'single_country': 'Single Country',
        'international': 'International',
        'country_pairs': 'Country Pairs',
        'frequency': 'Frequency',
        
        # Citation Analysis
        'citation_analysis': 'Citation Analysis',
        'citation_dynamics': 'Citation Dynamics by Year',
        'publication_year': 'Publication Year',
        'citation_year': 'Citation Year',
        'citations_count': 'Citations Count',
        'first_citation_analysis': 'First Citation Analysis',
        'min_days': 'Min Days',
        'max_days': 'Max Days',
        'avg_days': 'Avg Days',
        'median_days': 'Median Days',
        'cumulative_citations': 'Cumulative Citations',
        'citation_network_heatmap': 'Citation Network Heatmap',
        'most_cited_publications': 'Most Cited Publications',
        'cited_by_count': 'Cited by',
        
        # Citing Works
        'citing_works_analysis': 'Citing Works Analysis',
        'total_citing_works': 'Total Citing Works',
        'top_citing_authors': 'Top Citing Authors',
        'top_citing_affiliations': 'Top Citing Affiliations',
        'top_citing_countries': 'Top Citing Countries',
        'top_citing_journals': 'Top Citing Journals',
        'top_citing_publishers': 'Top Citing Publishers',
        
        # Topics Analysis
        'topics_analysis': 'Topics Analysis',
        'topics': 'Topics',
        'analyzed_count': 'Analyzed Count',
        'citing_count': 'Citing Count',
        'analyzed_norm_count': 'Analyzed Norm Count',
        'citing_norm_count': 'Citing Norm Count',
        'total_norm_count': 'Total Norm Count',
        'first_year': 'First Year',
        'peak_year': 'Peak Year',
        'top_10_cited_topics': 'Top 10 Most Cited Topics',
        'subtopics': 'Subtopics',
        'fields': 'Fields',
        'domains': 'Domains',
        'concepts': 'Concepts',
        
        # Detailed Citations
        'detailed_citations': 'Detailed Citations',
        'citing_journal': 'Citing Journal',
        'citing_year': 'Citing Year',
        'citing_date': 'Citing Date',
        'citation_lag': 'Citation Lag',
        'click_to_toggle': 'Click to toggle citations',
        'show_citations': 'Show Citations',
        'hide_citations': 'Hide Citations',
        
        # All Publications
        'all_publications': 'All Publications',
        'filter_by_title': 'Filter by Title Word(s)',
        'filter_by_year': 'Filter by Year',
        'filter_by_author': 'Filter by Author',
        'filter_by_affiliation': 'Filter by Affiliation',
        'filter_by_citations_min': 'Filter by Citations (min)',
        'filter_placeholder_title': 'Enter title keywords...',
        'filter_placeholder_author': 'Enter author name...',
        'filter_placeholder_affiliation': 'Enter affiliation...',
        'no_results': 'No results found',
        'showing_results': 'Showing {shown} of {total} publications',
        
        # Общее
        'footer': '© Advanced Journal Analysis Tool / Created by daM / Chimica Techno Acta',
        'journal_url': 'https://chimicatechnoacta.ru',
        'download_report': '💾 Download HTML Report',
        'report_preview': '📋 HTML Report Preview',
        'generating_report': 'Generating HTML report...',
        'no_data': '👈 Enter ISSN and period, then click "Run Analysis"',
        'data_source': 'Data source: OpenAlex',
        'generated': 'Generated',
        
        # Цветовые настройки
        'theme_info': 'Theme colors will be applied to the HTML report',
        'primary_color_label': 'Primary color',
        'secondary_color_label': 'Secondary color',
        
        # Новые для journal analysis
        'article': 'article',
        'articles': 'articles',
        'citation': 'citation',
        'citations': 'citations',
        'author': 'author',
        'coauthors': 'co-authors',
        'affiliation': 'affiliation',
        'country': 'country',
        'journal_name': 'Journal',
        'publisher_name': 'Publisher',
        'oa_status': 'OA Status',
        'is_oa': 'Open Access',
        'publication_date': 'Publication Date',
        'citing_work': 'Citing Work',
        'citing_works': 'Citing Works',
        'analyzed_work': 'Analyzed Work',
        'analyzed_works': 'Analyzed Works',
        'first_citation': 'First Citation',
        'citation_lag_years': 'Citation Lag (years)',
    },
    'ru': {
        'app_title': 'Advanced Journal Analysis Tool',
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
        
        # Анализ журнала
        'journal_analysis': '📊 Анализ журнала',
        'issn_label': 'ISSN',
        'issn_placeholder': '0028-0836 или 0028-0836',
        'period_label': 'Период анализа',
        'period_placeholder': '2020-2023 или 2020,2021,2022',
        'period_help': 'Введите как: 2020-2023 (диапазон) или 2020,2021,2022 (список)',
        'workers_label': 'Параллельных потоков',
        'workers_help': 'Количество параллельных API запросов (рекомендуется 4-12)',
        'run_analysis': '🚀 Запустить анализ',
        'no_issn': '⚠️ Введите ISSN',
        'no_period': '⚠️ Введите период анализа',
        'analysis_complete': '✅ Анализ завершен!',
        'analysis_error': '❌ Ошибка анализа: {error}',
        'cache_hit': '✅ Использованы кэшированные результаты для {issn} ({period})',
        'cache_miss': '🔄 Запуск нового анализа для {issn} ({period})',
        
        # Этапы анализа
        'stage1': '📚 Этап 1: Загрузка статей журнала...',
        'stage1_complete': '✅ Найдено {count} статей',
        'stage2': '🔄 Этап 2: Сбор цитирующих DOI...',
        'stage2_complete': '✅ Собрано {count} цитирующих DOI',
        'stage3': '📊 Этап 3: Обогащение анализируемых статей...',
        'stage3_complete': '✅ Обогащено {count} статей',
        'stage4': '📊 Этап 4: Обогащение цитирующих работ...',
        'stage4_complete': '✅ Обогащено {count} цитирующих работ',
        'stage5': '📄 Этап 5: Генерация HTML отчета...',
        'stage5_complete': '✅ Отчет готов!',
        'stage_processing': 'Обработка {current}/{total}',
        'stage_found': 'Найдено {count} элементов',
        
        # Метрики Overview
        'overview': 'Обзор',
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
        
        # Open Access Breakdown
        'open_access_breakdown': 'Распределение открытого доступа',
        'gold': 'Золотой',
        'hybrid': 'Гибридный',
        'green': 'Зеленый',
        'bronze': 'Бронзовый',
        'closed': 'Закрытый',
        'diamond': 'Алмазный',
        'unknown': 'Неизвестный',
        
        # Analyzed Articles
        'analyzed_articles': 'Анализируемые статьи',
        'author_analysis': 'Анализ авторов',
        'top_affiliations': 'Топ аффилиаций',
        'geographic_analysis': 'Географический анализ',
        'rank': 'Ранг',
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
        
        # Geographic Analysis
        'countries_per_publication': 'Стран на публикацию (уровень коллаборации)',
        'authors_per_country': 'Авторов по странам (индивидуальное распределение)',
        'collaboration_patterns': 'Паттерны коллабораций',
        'collaboration_couples': 'Пары стран в коллаборациях',
        'single_country': 'Одна страна',
        'international': 'Международные',
        'country_pairs': 'Пары стран',
        'frequency': 'Частота',
        
        # Citation Analysis
        'citation_analysis': 'Анализ цитирований',
        'citation_dynamics': 'Динамика цитирований по годам',
        'publication_year': 'Год публикации',
        'citation_year': 'Год цитирования',
        'citations_count': 'Количество цитирований',
        'first_citation_analysis': 'Анализ первого цитирования',
        'min_days': 'Мин. дней',
        'max_days': 'Макс. дней',
        'avg_days': 'Сред. дней',
        'median_days': 'Мед. дней',
        'cumulative_citations': 'Накопленные цитирования',
        'citation_network_heatmap': 'Тепловая карта цитирований',
        'most_cited_publications': 'Самые цитируемые публикации',
        'cited_by_count': 'Цитирований',
        
        # Citing Works
        'citing_works_analysis': 'Анализ цитирующих работ',
        'total_citing_works': 'Всего цитирующих работ',
        'top_citing_authors': 'Топ цитирующих авторов',
        'top_citing_affiliations': 'Топ цитирующих аффилиаций',
        'top_citing_countries': 'Топ цитирующих стран',
        'top_citing_journals': 'Топ цитирующих журналов',
        'top_citing_publishers': 'Топ цитирующих издательств',
        
        # Topics Analysis
        'topics_analysis': 'Тематический анализ',
        'topics': 'Темы',
        'analyzed_count': 'Анализ. кол-во',
        'citing_count': 'Цитир. кол-во',
        'analyzed_norm_count': 'Анализ. норм.',
        'citing_norm_count': 'Цитир. норм.',
        'total_norm_count': 'Общ. норм.',
        'first_year': 'Первый год',
        'peak_year': 'Пиковый год',
        'top_10_cited_topics': 'Топ-10 наиболее цитируемых тем',
        'subtopics': 'Подтемы',
        'fields': 'Области',
        'domains': 'Домены',
        'concepts': 'Концепты',
        
        # Detailed Citations
        'detailed_citations': 'Детальные цитирования',
        'citing_journal': 'Цитирующий журнал',
        'citing_year': 'Год цитирования',
        'citing_date': 'Дата цитирования',
        'citation_lag': 'Задержка цитирования',
        'click_to_toggle': 'Нажмите для показа цитирований',
        'show_citations': 'Показать цитирования',
        'hide_citations': 'Скрыть цитирования',
        
        # All Publications
        'all_publications': 'Все публикации',
        'filter_by_title': 'Фильтр по названию',
        'filter_by_year': 'Фильтр по году',
        'filter_by_author': 'Фильтр по автору',
        'filter_by_affiliation': 'Фильтр по аффилиации',
        'filter_by_citations_min': 'Фильтр по цитированиям (мин)',
        'filter_placeholder_title': 'Введите ключевые слова...',
        'filter_placeholder_author': 'Введите имя автора...',
        'filter_placeholder_affiliation': 'Введите аффилиацию...',
        'no_results': 'Результатов не найдено',
        'showing_results': 'Показано {shown} из {total} публикаций',
        
        # Общее
        'footer': '© Advanced Journal Analysis Tool / Created by daM / Chimica Techno Acta',
        'journal_url': 'https://chimicatechnoacta.ru',
        'download_report': '💾 Скачать HTML отчет',
        'report_preview': '📋 Предпросмотр HTML отчета',
        'generating_report': 'Генерация HTML отчета...',
        'no_data': '👈 Введите ISSN и период, затем нажмите "Запустить анализ"',
        'data_source': 'Источник данных: OpenAlex',
        'generated': 'Сгенерировано',
        
        # Цветовые настройки
        'theme_info': 'Цвета темы будут применены к HTML отчету',
        'primary_color_label': 'Основной цвет',
        'secondary_color_label': 'Дополнительный цвет',
        
        # Новые для journal analysis
        'article': 'статья',
        'articles': 'статей',
        'citation': 'цитирование',
        'citations': 'цитирований',
        'author': 'автор',
        'coauthors': 'соавторы',
        'affiliation': 'аффилиация',
        'country': 'страна',
        'journal_name': 'Журнал',
        'publisher_name': 'Издательство',
        'oa_status': 'Статус OA',
        'is_oa': 'Открытый доступ',
        'publication_date': 'Дата публикации',
        'citing_work': 'Цитирующая работа',
        'citing_works': 'Цитирующие работы',
        'analyzed_work': 'Анализируемая работа',
        'analyzed_works': 'Анализируемые работы',
        'first_citation': 'Первое цитирование',
        'citation_lag_years': 'Задержка цитирования (лет)',
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
            margin: 2px;
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
        
        .no-links {{
            color: #999;
            font-style: italic;
            margin: 5px 0;
            font-size: 12px;
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
    
    # Если уже полное название (длиннее 2 символов), возвращаем как есть
    if len(country_code) > 3:
        return country_code
    
    return COUNTRY_CODE_TO_NAME.get(country_code.upper(), country_code)

def is_author_affiliation(affiliation_name: str, author_affiliations: List[str]) -> bool:
    """Проверяет, является ли аффилиация аффилиацией самого ученого"""
    if not affiliation_name or not author_affiliations:
        return False
    
    # Нормализуем для сравнения (убираем лишние пробелы, приводим к нижнему регистру)
    aff_normalized = affiliation_name.strip().lower()
    
    for author_aff in author_affiliations:
        if not author_aff:
            continue
        author_aff_normalized = author_aff.strip().lower()
        # Проверяем полное совпадение или вхождение (если одна аффилиация является частью другой)
        if aff_normalized == author_aff_normalized:
            return True
        # Проверяем, не является ли аффилиация подразделением основной аффилиации
        if aff_normalized in author_aff_normalized or author_aff_normalized in aff_normalized:
            # Если одно название полностью содержит другое, считаем что это та же организация
            # но только если длина разницы не слишком большая (чтобы не перепутать разные организации)
            if len(aff_normalized) > 10 and len(author_aff_normalized) > 10:
                return True
    
    return False

# ============================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================

def clean_orcid(orcid_input: str) -> str:
    """Очищает ORCID от лишних символов и приводит к стандартному формату"""
    orcid = orcid_input.strip().upper()
    
    if 'orcid.org/' in orcid:
        orcid = orcid.split('orcid.org/')[-1]
    
    orcid = re.sub(r'[^0-9X-]', '', orcid)
    
    if re.match(r'^\d{4}-\d{4}-\d{4}-\d{3}[\dX]$', orcid):
        return orcid
    
    if len(orcid) == 16 and orcid.isdigit():
        return f"{orcid[:4]}-{orcid[4:8]}-{orcid[8:12]}-{orcid[12:]}"
    
    return orcid

def format_boolean(value: bool) -> str:
    return "✅" if value else "❌"

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

def normalize_author_name(name: str) -> str:
    """Нормализует имя автора для сравнения (инициал + фамилия)"""
    if not name:
        return name
    
    name = name.strip()
    parts = name.split()
    
    if len(parts) >= 2:
        first_initial = parts[0][0].upper()
        last_name = parts[-1]
        return f"{first_initial} {last_name}"
    elif len(parts) == 1:
        return parts[0]
    else:
        return name

def format_orcid_id(orcid: str) -> str:
    """Format ORCID ID to full URL"""
    if not orcid or not isinstance(orcid, str):
        return ""
    
    if orcid.startswith('https://orcid.org/'):
        return orcid
    
    clean_id = re.sub(r'[^\dXx-]', '', orcid.strip())
    
    if '-' in clean_id:
        if re.match(r'^\d{4}-\d{4}-\d{4}-\d{3}[\dX]$', clean_id, re.IGNORECASE):
            return f"https://orcid.org/{clean_id}"
    
    if len(clean_id) == 16:
        formatted = f"{clean_id[:4]}-{clean_id[4:8]}-{clean_id[8:12]}-{clean_id[12:]}"
        return f"https://orcid.org/{formatted}"
    elif len(clean_id) == 15 and clean_id[15] in ['X', 'x']:
        formatted = f"{clean_id[:4]}-{clean_id[4:8]}-{clean_id[8:12]}-{clean_id[12:15]}X"
        return f"https://orcid.org/{formatted}"
    else:
        return f"https://orcid.org/{clean_id}"

def parse_orcids(text: str) -> List[str]:
    """Парсит ORCID из текста. Поддерживает множественный ввод."""
    if not text or not text.strip():
        return []
    
    # Заменяем разделители на пробелы
    text = text.replace('\n', ' ').replace('\r', ' ')
    text = text.replace(',', ' ').replace(';', ' ')
    
    # Ищем все ORCID в тексте
    orcid_pattern = r'\d{4}-\d{4}-\d{4}-\d{3}[\dX]'
    matches = re.findall(orcid_pattern, text, re.IGNORECASE)
    
    # Также ищем URL с ORCID
    url_pattern = r'orcid\.org/(\d{4}-\d{4}-\d{4}-\d{3}[\dX])'
    url_matches = re.findall(url_pattern, text, re.IGNORECASE)
    
    all_orcids = matches + url_matches
    
    # Очищаем и возвращаем уникальные
    cleaned = [clean_orcid(o) for o in all_orcids]
    return list(dict.fromkeys(cleaned))

async def fetch_with_retry(session, url, params=None, headers=None, method='GET'):
    """Выполняет запрос с повторными попытками при ошибке"""
    for attempt in range(MAX_RETRIES):
        try:
            async with session.request(method, url, params=params, headers=headers, timeout=TIMEOUT) as response:
                if response.status == 429:
                    retry_after = int(response.headers.get('Retry-After', RETRY_DELAY * (attempt + 1)))
                    if SHOW_DEBUG_LOGS:
                        print(f"⚠️ Rate limit, ждем {retry_after} сек...")
                    await asyncio.sleep(retry_after)
                    continue
                
                if response.status == 200:
                    return await response.json()
                else:
                    if SHOW_DEBUG_LOGS:
                        print(f"⚠️ Ошибка {response.status} для {url}")
                    return None
        except Exception as e:
            if SHOW_DEBUG_LOGS:
                print(f"⚠️ Попытка {attempt+1}/{MAX_RETRIES} ошибка: {str(e)[:100]}")
            if attempt < MAX_RETRIES - 1:
                await asyncio.sleep(RETRY_DELAY * (attempt + 1))
            else:
                return None
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

def get_cache_path(orcid: str, mode: str = "orcid_openalex") -> str:
    """Возвращает путь к файлу кэша для ORCID с учетом режима анализа"""
    orcid_clean = clean_orcid(orcid)
    if not os.path.exists('cache'):
        os.makedirs('cache')
    return f"cache/{orcid_clean}_{mode}.json"

def load_from_cache(orcid: str) -> Optional[Dict]:
    """Загружает данные из кэша"""
    if not USE_CACHE:
        return None
    
    cache_path = get_cache_path(orcid, ANALYSIS_MODE)
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

def save_to_cache(orcid: str, data: Dict):
    """Сохраняет данные в кэш"""
    if not USE_CACHE:
        return
    
    cache_path = get_cache_path(orcid, ANALYSIS_MODE)
    try:
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✅ Данные сохранены в кэш: {cache_path}")
    except Exception as e:
        print(f"⚠️ Ошибка сохранения кэша: {e}")

# ============================================
# ФУНКЦИИ ДЛЯ АНАЛИЗА ЖУРНАЛОВ (НОВЫЙ КОД)
# ============================================

# Глобальные настройки для анализа журналов
MAX_WORKERS = 8
BASE_DELAY = 0.35
MAX_RETRIES = 4
MAX_CITING_PER_PAPER = 300
lock = Lock()

def normalize_issn(issn_str: str) -> str:
    """Нормализует ISSN к формату XXXX-XXXX"""
    cleaned = re.sub(r'[^0-9Xx]', '', str(issn_str).strip())
    if len(cleaned) == 8:
        return f"{cleaned[:4]}-{cleaned[4:]}".upper()
    return cleaned.upper()

def smart_get(url: str, params: dict, retries: int = MAX_RETRIES) -> Optional[dict]:
    """Выполняет GET запрос с защитой от rate limiting"""
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
                print(f"⚠️ smart_get attempt {attempt+1} error: {e}")
            time.sleep(1.5 * (2 ** attempt))
    return None

def get_citing_dois(oa_id: str) -> List[str]:
    """Параллельная функция получения цитирующих DOI"""
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

def enrich_article_with_details(doi: str, session=None) -> Dict:
    """Получает детальную информацию о статье по DOI"""
    if not doi or doi == "N/A":
        return {}
    
    try:
        url = "https://api.openalex.org/works"
        params = {"filter": f"doi:{doi}"}
        
        data = smart_get(url, params)
        if not data:
            return {}
        
        results = data.get("results", [])
        if not results:
            return {}
        
        work = results[0]
        
        # Извлекаем все необходимые поля
        enriched = {
            'doi': doi,
            'title': work.get('title', 'No title'),
            'publication_year': work.get('publication_year'),
            'publication_date': work.get('publication_date'),
            'cited_by_count': work.get('cited_by_count', 0),
            'is_retracted': work.get('is_retracted', False),
            'is_correction': work.get('is_correction', False),
            'type': work.get('type', 'unknown'),
        }
        
        # Информация о журнале
        if work.get('primary_location'):
            source = work['primary_location'].get('source', {})
            enriched['journal_name'] = source.get('display_name', 'Unknown')
            enriched['publisher'] = source.get('host_organization_name') or source.get('publisher', 'Unknown')
            enriched['issn'] = source.get('issn', [])
            enriched['source_type'] = source.get('type', 'unknown')
        else:
            enriched['journal_name'] = 'Unknown'
            enriched['publisher'] = 'Unknown'
            enriched['issn'] = []
            enriched['source_type'] = 'unknown'
        
        # Open Access
        oa = work.get('open_access', {})
        enriched['is_oa'] = oa.get('is_oa', False)
        enriched['oa_status'] = oa.get('oa_status', 'unknown')
        enriched['oa_url'] = oa.get('oa_url', None)
        enriched['any_repository_has_fulltext'] = oa.get('any_repository_has_fulltext', False)
        
        # Авторы
        authors = []
        author_orcids = []
        authors_with_orcids = []
        
        for auth in work.get('authorships', []):
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
        
        enriched['authors'] = authors
        enriched['author_orcids'] = author_orcids
        enriched['authors_with_orcids'] = authors_with_orcids
        enriched['author_count'] = len(authors)
        
        # Аффилиации и страны
        affiliations = []
        affiliation_countries = []
        institutions = []
        countries_set = set()
        
        for auth in work.get('authorships', []):
            if auth.get('institutions'):
                for inst in auth['institutions']:
                    affil = inst.get('display_name', '')
                    if affil:
                        affiliations.append(affil)
                        country_code = inst.get('country_code', '')
                        if country_code:
                            country_name = get_full_country_name(country_code)
                            affiliation_countries.append(country_name)
                            countries_set.add(country_name)
                        
                        institutions.append({
                            'id': inst.get('id', ''),
                            'display_name': inst.get('display_name', ''),
                            'country_code': inst.get('country_code', ''),
                            'ror': inst.get('ror', ''),
                            'type': inst.get('type', ''),
                            'lineage': inst.get('lineage', [])
                        })
        
        enriched['affiliations'] = affiliations
        enriched['affiliation_countries'] = affiliation_countries
        enriched['institutions'] = institutions
        enriched['countries'] = list(countries_set)
        enriched['unique_countries'] = len(countries_set)
        
        # Темы и концепты
        primary_topic = work.get('primary_topic', {})
        if primary_topic:
            enriched['primary_topic'] = {
                'display_name': primary_topic.get('display_name', ''),
                'subfield': primary_topic.get('subfield', {}).get('display_name', ''),
                'field': primary_topic.get('field', {}).get('display_name', ''),
                'domain': primary_topic.get('domain', {}).get('display_name', ''),
                'score': primary_topic.get('score', 0)
            }
        else:
            enriched['primary_topic'] = None
        
        topics_list = work.get('topics', [])
        enriched['topics'] = [
            {
                'display_name': t.get('display_name', ''),
                'subfield': t.get('subfield', {}).get('display_name', ''),
                'field': t.get('field', {}).get('display_name', ''),
                'domain': t.get('domain', {}).get('display_name', ''),
                'score': t.get('score', 0)
            }
            for t in topics_list
        ]
        
        # Концепты
        concepts = []
        concept_levels = {}
        fields = []
        domains = []
        topics_old = []
        subtopics = []
        
        for concept in work.get('concepts', []):
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
        
        enriched['concepts'] = list(set(concepts))[:15]
        enriched['concept_levels'] = concept_levels
        enriched['fields'] = list(set(fields))[:10]
        enriched['domains'] = list(set(domains))[:5]
        enriched['topics_old'] = list(set(topics_old))[:15]
        enriched['subtopics'] = list(set(subtopics))[:20]
        
        enriched['cited_by_percentile'] = work.get('cited_by_percentile', {})
        
        return enriched
        
    except Exception as e:
        if SHOW_DEBUG_LOGS:
            print(f"⚠️ Ошибка обогащения статьи {doi}: {e}")
        return {}

def enrich_articles_batch(dois: List[str], progress_callback=None) -> List[Dict]:
    """Обогащает список DOI детальной информацией"""
    if not dois:
        return []
    
    enriched = []
    total = len(dois)
    
    for idx, doi in enumerate(dois):
        if progress_callback:
            progress_callback(idx + 1, total)
        
        article = enrich_article_with_details(doi)
        if article:
            enriched.append(article)
        
        # Небольшая задержка между запросами
        if idx < total - 1:
            time.sleep(0.1)
    
    return enriched

def run_journal_analysis(issn: str, period, max_workers: int = 8, progress_callbacks: Dict = None) -> Dict:
    """
    Основная функция анализа журнала
    
    Args:
        issn: ISSN журнала
        period: период в формате int (год), list (список годов) или tuple (диапазон)
        max_workers: количество параллельных потоков
        progress_callbacks: словарь с callback-функциями для этапов
    
    Returns:
        Dict: словарь с результатами анализа
    """
    if progress_callbacks is None:
        progress_callbacks = {}
    
    normalized = normalize_issn(issn)
    
    if SHOW_DEBUG_LOGS:
        print(f"🚀 Запуск анализа для {normalized}")
    
    # Этап 1: Получение статей журнала
    if 'stage1' in progress_callbacks:
        progress_callbacks['stage1'](0, 1)
    
    base_url = "https://api.openalex.org/works"
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
            "select": "id,doi,publication_year,cited_by_count,publication_date",
            "cursor": cursor
        })
        
        if not data or not data.get("results"):
            break
        
        for w in data["results"]:
            doi = w.get("doi")
            if doi:
                doi = doi.replace("https://doi.org/", "")
            articles.append({
                "DOI": doi or "N/A",
                "Year": w.get("publication_year"),
                "Cited_by_count": w.get("cited_by_count", 0),
                "OpenAlex_ID": w.get("id", "").replace("https://openalex.org/", ""),
                "Publication_Date": w.get("publication_date", "")
            })
        
        if 'stage1' in progress_callbacks:
            progress_callbacks['stage1'](len(articles), None)
        
        cursor = data.get("meta", {}).get("next_cursor")
        if not cursor:
            break
    
    if 'stage1' in progress_callbacks:
        progress_callbacks['stage1'](len(articles), len(articles))
    
    if SHOW_DEBUG_LOGS:
        print(f"✅ Найдено статей: {len(articles)} | Суммарное цитирование: {sum(a['Cited_by_count'] for a in articles)}")
    
    # Этап 2: Сбор цитирующих DOI
    if 'stage2' in progress_callbacks:
        progress_callbacks['stage2'](0, len(articles))
    
    citing_map = {}
    futures = {}
    
    # Фильтруем статьи с цитированиями
    articles_with_citations = [a for a in articles if a['Cited_by_count'] > 0 and a['DOI'] != "N/A"]
    
    if SHOW_DEBUG_LOGS:
        print(f"⚡ Параллельный сбор цитирующих DOI ({max_workers} потоков)...")
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for idx, row in enumerate(articles_with_citations):
            future = executor.submit(get_citing_dois, row['OpenAlex_ID'])
            futures[future] = (idx, row['DOI'])
        
        completed = 0
        total = len(futures)
        
        for future in as_completed(futures):
            idx, doi = futures[future]
            try:
                citing_map[doi] = future.result()
            except Exception as e:
                if SHOW_DEBUG_LOGS:
                    print(f"⚠️ Ошибка получения цитирований для {doi}: {e}")
                citing_map[doi] = []
            
            completed += 1
            if 'stage2' in progress_callbacks:
                progress_callbacks['stage2'](completed, total)
    
    # Этап 3: Обогащение анализируемых статей
    if 'stage3' in progress_callbacks:
        progress_callbacks['stage3'](0, len(articles))
    
    analyzed_articles = []
    article_dois = [a['DOI'] for a in articles if a['DOI'] != "N/A"]
    
    # Обогащаем статьи детальной информацией
    enriched_articles = enrich_articles_batch(article_dois, lambda current, total: progress_callbacks['stage3'](current, total) if 'stage3' in progress_callbacks else None)
    
    # Создаем словарь для быстрого доступа по DOI
    enriched_map = {a['doi']: a for a in enriched_articles}
    
    # Объединяем с исходными данными
    for article in articles:
        doi = article['DOI']
        if doi != "N/A" and doi in enriched_map:
            enriched = enriched_map[doi]
            # Добавляем цитирующие DOI
            citing_dois = citing_map.get(doi, [])
            enriched['citing_dois'] = citing_dois
            enriched['citing_count'] = len(citing_dois)
            analyzed_articles.append(enriched)
        elif doi != "N/A":
            # Создаем базовую запись
            analyzed_articles.append({
                'doi': doi,
                'title': 'No title',
                'publication_year': article['Year'],
                'publication_date': article.get('Publication_Date', ''),
                'cited_by_count': article['Cited_by_count'],
                'journal_name': 'Unknown',
                'publisher': 'Unknown',
                'is_oa': False,
                'oa_status': 'unknown',
                'authors': [],
                'authors_with_orcids': [],
                'affiliations': [],
                'affiliation_countries': [],
                'countries': [],
                'institutions': [],
                'concepts': [],
                'fields': [],
                'domains': [],
                'topics': [],
                'topics_old': [],
                'subtopics': [],
                'citing_dois': citing_map.get(doi, []),
                'citing_count': len(citing_map.get(doi, [])),
                'author_count': 0,
                'unique_countries': 0
            })
    
    if 'stage3' in progress_callbacks:
        progress_callbacks['stage3'](len(analyzed_articles), len(analyzed_articles))
    
    # Этап 4: Обогащение цитирующих статей
    if 'stage4' in progress_callbacks:
        progress_callbacks['stage4'](0, 1)
    
    # Собираем все цитирующие DOI
    all_citing_dois = set()
    for article in analyzed_articles:
        for citing_doi in article.get('citing_dois', []):
            if citing_doi and citing_doi != "N/A":
                all_citing_dois.add(citing_doi)
    
    citing_dois_list = list(all_citing_dois)
    
    if SHOW_DEBUG_LOGS:
        print(f"📊 Найдено {len(citing_dois_list)} уникальных цитирующих DOI")
    
    # Обогащаем цитирующие статьи
    if 'stage4' in progress_callbacks:
        progress_callbacks['stage4'](0, len(citing_dois_list))
    
    citing_articles = enrich_articles_batch(
        citing_dois_list, 
        lambda current, total: progress_callbacks['stage4'](current, total) if 'stage4' in progress_callbacks else None
    )
    
    # Создаем словарь для быстрого доступа к цитирующим статьям
    citing_map_enriched = {a['doi']: a for a in citing_articles}
    
    # Добавляем обогащенные цитирующие статьи к анализируемым
    for article in analyzed_articles:
        enriched_citing = []
        for citing_doi in article.get('citing_dois', []):
            if citing_doi in citing_map_enriched:
                enriched_citing.append(citing_map_enriched[citing_doi])
        article['citing_articles'] = enriched_citing
    
    if 'stage4' in progress_callbacks:
        progress_callbacks['stage4'](len(citing_articles), len(citing_articles))
    
    # Этап 5: Подготовка результата
    if 'stage5' in progress_callbacks:
        progress_callbacks['stage5'](0, 1)
    
    result = {
        'issn': normalized,
        'period': period,
        'total_articles': len(analyzed_articles),
        'analyzed_articles': analyzed_articles,
        'citing_articles': citing_articles,
        'all_citing_dois': list(all_citing_dois),
        'analysis_date': datetime.now().isoformat()
    }
    
    if 'stage5' in progress_callbacks:
        progress_callbacks['stage5'](1, 1)
    
    return result

# ============================================
# КЛАСС ДЛЯ АНАЛИЗА ЖУРНАЛА
# ============================================

class JournalAnalyzer:
    """Класс для анализа журнала и расчета всех метрик"""
    
    def __init__(self, result: Dict):
        self.result = result
        self.analyzed_articles = result.get('analyzed_articles', [])
        self.citing_articles = result.get('citing_articles', [])
        self.metrics = {}
        self._calculate_metrics()
    
    def _calculate_metrics(self):
        """Рассчитывает все метрики для журнала"""
        
        # Основные метрики
        total_publications = len(self.analyzed_articles)
        total_citations = sum(a.get('cited_by_count', 0) for a in self.analyzed_articles)
        citations_list = [a.get('cited_by_count', 0) for a in self.analyzed_articles]
        
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
        
        # i10 и i100
        i10_index = sum(1 for c in citations_list if c >= 10)
        i100_index = sum(1 for c in citations_list if c >= 100)
        
        # Среднее цитирований
        avg_citations = sum(citations_list) / len(citations_list) if citations_list else 0
        
        # Open Access
        oa_count = sum(1 for a in self.analyzed_articles if a.get('is_oa', False))
        oa_percentage = (oa_count / total_publications * 100) if total_publications > 0 else 0
        
        # Активные годы
        years = [a.get('publication_year') for a in self.analyzed_articles if a.get('publication_year')]
        active_years = len(set(years)) if years else 0
        
        # Уникальные авторы
        all_authors = set()
        for a in self.analyzed_articles:
            for author in a.get('authors', []):
                all_authors.add(author)
        unique_authors = len(all_authors)
        
        # Уникальные аффилиации
        all_affiliations = set()
        for a in self.analyzed_articles:
            for aff in a.get('affiliations', []):
                if aff:
                    all_affiliations.add(aff)
        unique_affiliations = len(all_affiliations)
        
        # Уникальные страны
        all_countries = set()
        for a in self.analyzed_articles:
            for country in a.get('countries', []):
                if country:
                    all_countries.add(country)
        unique_countries = len(all_countries)
        
        # Среднее авторов/статью
        author_counts = [a.get('author_count', 0) for a in self.analyzed_articles]
        avg_authors_per_paper = sum(author_counts) / len(author_counts) if author_counts else 0
        
        # Среднее аффилиаций/статью
        aff_counts = [len(a.get('affiliations', [])) for a in self.analyzed_articles]
        avg_affiliations_per_paper = sum(aff_counts) / len(aff_counts) if aff_counts else 0
        
        # Среднее стран/статью
        country_counts = [len(a.get('countries', [])) for a in self.analyzed_articles]
        avg_countries_per_paper = sum(country_counts) / len(country_counts) if country_counts else 0
        
        # Международные коллаборации
        international_papers = sum(1 for a in self.analyzed_articles if len(a.get('countries', [])) >= 2)
        international_collab_rate = (international_papers / total_publications * 100) if total_publications > 0 else 0
        
        # Уникальные цитирующие авторы
        all_citing_authors = set()
        for a in self.citing_articles:
            for author in a.get('authors', []):
                all_citing_authors.add(author)
        unique_citing_authors = len(all_citing_authors)
        
        # Уникальные цитирующие аффилиации
        all_citing_affiliations = set()
        for a in self.citing_articles:
            for aff in a.get('affiliations', []):
                if aff:
                    all_citing_affiliations.add(aff)
        unique_citing_affiliations = len(all_citing_affiliations)
        
        # Уникальные цитирующие страны
        all_citing_countries = set()
        for a in self.citing_articles:
            for country in a.get('countries', []):
                if country:
                    all_citing_countries.add(country)
        unique_citing_countries = len(all_citing_countries)
        
        # Уникальные цитирующие журналы
        all_citing_journals = set()
        for a in self.citing_articles:
            journal = a.get('journal_name', '')
            if journal and journal != 'Unknown':
                all_citing_journals.add(journal)
        unique_citing_journals = len(all_citing_journals)
        
        # Уникальные цитирующие издательства
        all_citing_publishers = set()
        for a in self.citing_articles:
            publisher = a.get('publisher', '')
            if publisher and publisher != 'Unknown':
                all_citing_publishers.add(publisher)
        unique_citing_publishers = len(all_citing_publishers)
        
        # Open Access Breakdown
        oa_breakdown = {
            'gold': 0,
            'hybrid': 0,
            'green': 0,
            'bronze': 0,
            'closed': 0,
            'diamond': 0,
            'unknown': 0
        }
        for a in self.analyzed_articles:
            status = a.get('oa_status', 'unknown')
            if status in oa_breakdown:
                oa_breakdown[status] += 1
            else:
                oa_breakdown['unknown'] += 1
        
        # Сохраняем все метрики
        self.metrics = {
            'total_publications': total_publications,
            'total_citations': total_citations,
            'h_index': h_index,
            'g_index': g_index,
            'i10_index': i10_index,
            'i100_index': i100_index,
            'avg_citations': avg_citations,
            'open_access': oa_percentage,
            'active_years': active_years,
            'unique_authors': unique_authors,
            'unique_affiliations': unique_affiliations,
            'unique_countries': unique_countries,
            'avg_authors_per_paper': avg_authors_per_paper,
            'avg_affiliations_per_paper': avg_affiliations_per_paper,
            'avg_countries_per_paper': avg_countries_per_paper,
            'international_collaboration_rate': international_collab_rate,
            'unique_citing_authors': unique_citing_authors,
            'unique_citing_affiliations': unique_citing_affiliations,
            'unique_citing_countries': unique_citing_countries,
            'unique_citing_journals': unique_citing_journals,
            'unique_citing_publishers': unique_citing_publishers,
            'oa_breakdown': oa_breakdown,
            'years': sorted(set(years)) if years else [],
            'citations_list': citations_list,
            'citations_sorted': citations_sorted,
        }
    
    def get_author_analysis(self, top_n: int = 30) -> List[Dict]:
        """Анализ авторов"""
        author_stats = defaultdict(lambda: {
            'count': 0,
            'citations': 0,
            'orcid': None,
            'affiliations': set(),
            'countries': set(),
            'papers': []
        })
        
        for article in self.analyzed_articles:
            authors_with_orcids = article.get('authors_with_orcids', [])
            citations = article.get('cited_by_count', 0)
            
            for author_data in authors_with_orcids:
                name = author_data.get('name', '')
                if not name:
                    continue
                
                author_stats[name]['count'] += 1
                author_stats[name]['citations'] += citations
                
                if not author_stats[name]['orcid']:
                    author_stats[name]['orcid'] = author_data.get('orcid')
                
                # Добавляем аффилиации и страны из статьи
                for aff in article.get('affiliations', []):
                    if aff:
                        author_stats[name]['affiliations'].add(aff)
                
                for country in article.get('countries', []):
                    if country:
                        author_stats[name]['countries'].add(country)
                
                author_stats[name]['papers'].append(article.get('doi', ''))
        
        # Сортируем по количеству публикаций
        sorted_authors = sorted(
            author_stats.items(),
            key=lambda x: (x[1]['count'], x[1]['citations']),
            reverse=True
        )
        
        result = []
        for idx, (name, stats) in enumerate(sorted_authors[:top_n], 1):
            result.append({
                'rank': idx,
                'name': name,
                'orcid': stats['orcid'],
                'affiliations': list(stats['affiliations'])[:3],
                'countries': list(stats['countries']),
                'publications': stats['count'],
                'citations': stats['citations']
            })
        
        return result
    
    def get_top_affiliations(self, top_n: int = 30) -> List[Dict]:
        """Топ аффилиаций"""
        aff_stats = defaultdict(lambda: {
            'count': 0,
            'citations': 0,
            'countries': set()
        })
        
        for article in self.analyzed_articles:
            citations = article.get('cited_by_count', 0)
            for aff in article.get('affiliations', []):
                if aff:
                    aff_stats[aff]['count'] += 1
                    aff_stats[aff]['citations'] += citations
                    for country in article.get('countries', []):
                        if country:
                            aff_stats[aff]['countries'].add(country)
        
        sorted_affs = sorted(
            aff_stats.items(),
            key=lambda x: (x[1]['count'], x[1]['citations']),
            reverse=True
        )
        
        result = []
        for idx, (name, stats) in enumerate(sorted_affs[:top_n], 1):
            result.append({
                'rank': idx,
                'name': name,
                'count': stats['count'],
                'citations': stats['citations'],
                'countries': list(stats['countries'])
            })
        
        return result
    
    def get_geographic_analysis(self) -> Dict:
        """Географический анализ"""
        # Countries per Publication (Collaboration Level)
        countries_per_pub = []
        for article in self.analyzed_articles:
            countries = article.get('countries', [])
            if countries:
                countries_per_pub.append(len(countries))
        
        # Authors per Country (Individual Distribution)
        authors_per_country = defaultdict(int)
        for article in self.analyzed_articles:
            for author in article.get('authors', []):
                # Пытаемся определить страну автора по аффилиациям
                # Упрощенный подход: берем страны из статьи
                for country in article.get('countries', []):
                    if country:
                        authors_per_country[country] += 1
        
        # Collaboration Patterns
        single_country = 0
        international = 0
        for article in self.analyzed_articles:
            countries = article.get('countries', [])
            if len(countries) <= 1:
                single_country += 1
            else:
                international += 1
        
        # Collaboration Couples
        country_pairs = defaultdict(int)
        for article in self.analyzed_articles:
            countries = article.get('countries', [])
            if len(countries) >= 2:
                for i in range(len(countries)):
                    for j in range(i + 1, len(countries)):
                        pair = tuple(sorted([countries[i], countries[j]]))
                        country_pairs[pair] += 1
        
        sorted_pairs = sorted(country_pairs.items(), key=lambda x: x[1], reverse=True)
        
        return {
            'countries_per_pub': countries_per_pub,
            'authors_per_country': dict(authors_per_country),
            'single_country': single_country,
            'international': international,
            'country_pairs': sorted_pairs[:20]
        }
    
    def get_citation_dynamics(self) -> Dict:
        """Динамика цитирований по годам"""
        dynamics = defaultdict(lambda: defaultdict(int))
        
        # Для каждой анализируемой статьи
        for article in self.analyzed_articles:
            pub_year = article.get('publication_year')
            if not pub_year:
                continue
            
            # Для каждой цитирующей статьи
            for citing in article.get('citing_articles', []):
                citing_year = citing.get('publication_year')
                if not citing_year:
                    continue
                
                dynamics[pub_year][citing_year] += 1
        
        # Преобразуем в список для таблицы
        result = []
        for pub_year in sorted(dynamics.keys()):
            for citing_year in sorted(dynamics[pub_year].keys()):
                result.append({
                    'publication_year': pub_year,
                    'citation_year': citing_year,
                    'count': dynamics[pub_year][citing_year]
                })
        
        # Расчет первого цитирования
        first_citation_lags = []
        for article in self.analyzed_articles:
            pub_year = article.get('publication_year')
            if not pub_year:
                continue
            
            citing_years = []
            for citing in article.get('citing_articles', []):
                citing_year = citing.get('publication_year')
                if citing_year:
                    citing_years.append(citing_year)
            
            if citing_years:
                min_year = min(citing_years)
                lag = min_year - pub_year
                first_citation_lags.append(lag)
        
        first_citation_stats = {}
        if first_citation_lags:
            first_citation_stats = {
                'min': min(first_citation_lags),
                'max': max(first_citation_lags),
                'avg': sum(first_citation_lags) / len(first_citation_lags),
                'median': sorted(first_citation_lags)[len(first_citation_lags) // 2]
            }
        
        # Cumulative Citations
        cumulative = defaultdict(int)
        year_citations = defaultdict(int)
        
        for article in self.analyzed_articles:
            pub_year = article.get('publication_year')
            if not pub_year:
                continue
            
            citations = article.get('cited_by_count', 0)
            year_citations[pub_year] += citations
        
        running_total = 0
        for year in sorted(year_citations.keys()):
            running_total += year_citations[year]
            cumulative[year] = running_total
        
        return {
            'dynamics': result,
            'first_citation_stats': first_citation_stats,
            'cumulative': dict(cumulative)
        }
    
    def get_most_cited_publications(self, top_n: int = 20) -> List[Dict]:
        """Самые цитируемые публикации"""
        sorted_articles = sorted(
            self.analyzed_articles,
            key=lambda x: x.get('cited_by_count', 0),
            reverse=True
        )
        
        result = []
        for idx, article in enumerate(sorted_articles[:top_n], 1):
            pub_year = article.get('publication_year')
            citations = article.get('cited_by_count', 0)
            citations_per_year = citations / (2026 - pub_year + 1) if pub_year else 0
            
            authors = article.get('authors', [])
            authors_str = ', '.join(authors[:3])
            if len(authors) > 3:
                authors_str += f' +{len(authors) - 3} more'
            
            result.append({
                'rank': idx,
                'title': article.get('title', 'No title'),
                'year': pub_year,
                'citations': citations,
                'citations_per_year': round(citations_per_year, 1),
                'authors': authors_str,
                'doi': article.get('doi', '')
            })
        
        return result
    
    def get_topic_analysis(self) -> Dict:
        """Тематический анализ"""
        # Собираем все темы из анализируемых и цитирующих статей
        topics_analyzed = defaultdict(lambda: {
            'count': 0,
            'citations': 0,
            'years': []
        })
        
        topics_citing = defaultdict(lambda: {
            'count': 0,
            'citations': 0,
            'years': []
        })
        
        # Анализируемые статьи
        for article in self.analyzed_articles:
            topics = article.get('topics', [])
            citations = article.get('cited_by_count', 0)
            year = article.get('publication_year')
            
            for topic in topics:
                name = topic.get('display_name', '')
                if name:
                    topics_analyzed[name]['count'] += 1
                    topics_analyzed[name]['citations'] += citations
                    if year:
                        topics_analyzed[name]['years'].append(year)
        
        # Цитирующие статьи
        for article in self.citing_articles:
            topics = article.get('topics', [])
            citations = article.get('cited_by_count', 0)
            year = article.get('publication_year')
            
            for topic in topics:
                name = topic.get('display_name', '')
                if name:
                    topics_citing[name]['count'] += 1
                    topics_citing[name]['citations'] += citations
                    if year:
                        topics_citing[name]['years'].append(year)
        
        # Объединяем
        all_topics = set(topics_analyzed.keys()) | set(topics_citing.keys())
        
        total_analyzed = len(self.analyzed_articles)
        total_citing = len(self.citing_articles)
        total_all = total_analyzed + total_citing
        
        topic_results = []
        for topic in all_topics:
            analyzed_count = topics_analyzed.get(topic, {}).get('count', 0)
            citing_count = topics_citing.get(topic, {}).get('count', 0)
            
            analyzed_norm = analyzed_count / total_analyzed if total_analyzed > 0 else 0
            citing_norm = citing_count / total_citing if total_citing > 0 else 0
            total_norm = (analyzed_count + citing_count) / total_all if total_all > 0 else 0
            
            years = topics_analyzed.get(topic, {}).get('years', [])
            first_year = min(years) if years else None
            
            # Пиковый год (по количеству цитирований)
            peak_year = None
            if years:
                year_counts = Counter(years)
                peak_year = max(year_counts.items(), key=lambda x: x[1])[0]
            
            topic_results.append({
                'topic': topic,
                'analyzed_count': analyzed_count,
                'citing_count': citing_count,
                'analyzed_norm_count': round(analyzed_norm, 3),
                'citing_norm_count': round(citing_norm, 3),
                'total_norm_count': round(total_norm, 3),
                'first_year': first_year,
                'peak_year': peak_year
            })
        
        # Сортируем по общему нормированному количеству
        topic_results.sort(key=lambda x: x['total_norm_count'], reverse=True)
        
        # Топ-10 по цитированиям
        citing_by_topic = defaultdict(int)
        for article in self.citing_articles:
            citations = article.get('cited_by_count', 0)
            for topic in article.get('topics', []):
                name = topic.get('display_name', '')
                if name:
                    citing_by_topic[name] += citations
        
        top_cited_topics = sorted(citing_by_topic.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            'topics': topic_results[:50],
            'top_cited_topics': top_cited_topics
        }
    
    def get_detailed_citations(self) -> Dict:
        """Детальные цитирования для каждой статьи"""
        result = {}
        
        for article in self.analyzed_articles:
            doi = article.get('doi', '')
            if not doi or doi == 'N/A':
                continue
            
            citing_articles = article.get('citing_articles', [])
            citations_list = []
            
            for citing in citing_articles:
                citations_list.append({
                    'citing_title': citing.get('title', 'No title'),
                    'citing_year': citing.get('publication_year'),
                    'citing_date': citing.get('publication_date', ''),
                    'citing_journal': citing.get('journal_name', 'Unknown'),
                    'citing_publisher': citing.get('publisher', 'Unknown'),
                    'citing_doi': citing.get('doi', ''),
                    'citation_lag': citing.get('publication_year') - article.get('publication_year') if citing.get('publication_year') and article.get('publication_year') else None,
                    'citing_authors': citing.get('authors', []),
                    'citing_countries': citing.get('countries', []),
                    'citing_topics': [t.get('display_name', '') for t in citing.get('topics', [])]
                })
            
            if citations_list:
                result[doi] = {
                    'title': article.get('title', 'No title'),
                    'year': article.get('publication_year'),
                    'doi': doi,
                    'total_citations': len(citations_list),
                    'citations': citations_list
                }
        
        return result
    
    def get_metrics(self) -> Dict:
        """Возвращает все метрики"""
        return self.metrics

# ============================================
# ФУНКЦИИ ДЛЯ ГЕНЕРАЦИИ ОТЧЕТОВ (ОБНОВЛЕННЫЕ)
# ============================================

def generate_journal_html_report(result: Dict, logo_base64: Optional[str] = None, 
                                 app_logo_base64: Optional[str] = None,
                                 theme_colors: Optional[Dict] = None,
                                 lang: str = 'en') -> str:
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
    
    # Создаем анализатор
    analyzer = JournalAnalyzer(result)
    metrics = analyzer.get_metrics()
    analyzed_articles = result.get('analyzed_articles', [])
    citing_articles = result.get('citing_articles', [])
    
    # Получаем данные для отчета
    author_analysis = analyzer.get_author_analysis(30)
    top_affiliations = analyzer.get_top_affiliations(30)
    geographic = analyzer.get_geographic_analysis()
    citation_dynamics = analyzer.get_citation_dynamics()
    most_cited = analyzer.get_most_cited_publications(20)
    topic_analysis = analyzer.get_topic_analysis()
    detailed_citations = analyzer.get_detailed_citations()
    
    # Подготовка данных для таблиц
    all_publications_data = analyzed_articles
    
    # Формируем HTML
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>{t('app_title')} - {result.get('issn', '')}</title>
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
                max-width: 1600px;
                margin: 0 auto;
                background: white;
                box-shadow: 0 10px 40px rgba(0,0,0,0.1);
                border-radius: 10px;
                overflow: hidden;
            }}
            
            /* Sidebar Navigation */
            .sidebar {{
                position: fixed;
                left: 0;
                top: 0;
                width: 280px;
                height: 100vh;
                background: linear-gradient(180deg, {primary} 0%, {secondary} 100%);
                color: white;
                padding: 20px 15px;
                overflow-y: auto;
                z-index: 1000;
                box-shadow: 2px 0 10px rgba(0,0,0,0.2);
            }}
            
            .sidebar::-webkit-scrollbar {{
                width: 5px;
            }}
            
            .sidebar::-webkit-scrollbar-thumb {{
                background: rgba(255,255,255,0.3);
                border-radius: 10px;
            }}
            
            .sidebar h3 {{
                margin-bottom: 20px;
                font-size: 18px;
                font-weight: 600;
                color: white;
                padding-bottom: 10px;
                border-bottom: 2px solid rgba(255,255,255,0.2);
                text-align: center;
            }}
            
            .sidebar .logo-mini {{
                max-width: 100px;
                display: block;
                margin: 0 auto 15px auto;
            }}
            
            .sidebar .nav-section {{
                margin-bottom: 5px;
            }}
            
            .sidebar .nav-section-title {{
                font-size: 12px;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 1px;
                color: rgba(255,255,255,0.6);
                padding: 8px 15px;
                margin-top: 10px;
            }}
            
            .sidebar a {{
                color: rgba(255,255,255,0.85);
                text-decoration: none;
                display: flex;
                align-items: center;
                gap: 12px;
                padding: 8px 15px;
                margin: 2px 0;
                border-radius: 8px;
                transition: all 0.3s;
                font-size: 14px;
            }}
            
            .sidebar a:hover {{
                background: rgba(255,255,255,0.2);
                transform: translateX(5px);
                color: white;
            }}
            
            .sidebar a.active {{
                background: rgba(255,255,255,0.15);
                color: white;
            }}
            
            .sidebar .nav-sub {{
                padding-left: 20px;
                font-size: 13px;
            }}
            
            .sidebar .nav-sub a {{
                font-size: 13px;
                padding: 5px 15px;
            }}
            
            .sidebar .nav-icon {{
                width: 20px;
                text-align: center;
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
                padding: 30px 40px;
                border-radius: 15px;
                margin-bottom: 30px;
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
            
            .header-logo {{
                max-height: 80px;
                max-width: 150px;
            }}
            
            .header-logo-app {{
                max-height: 70px;
                max-width: 200px;
            }}
            
            .header-title h1 {{
                color: white;
                border: none;
                margin: 0;
                font-size: 28px;
            }}
            
            .header-title .subtitle {{
                opacity: 0.9;
                font-size: 14px;
                margin-top: 5px;
            }}
            
            .header-right {{
                text-align: right;
            }}
            
            .header-right .date {{
                opacity: 0.9;
                font-size: 13px;
            }}
            
            /* Sections */
            .section {{
                background: white;
                border-radius: 15px;
                padding: 25px;
                margin-bottom: 30px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.08);
                border: 1px solid #e8ecf1;
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
            
            /* Metrics Grid */
            .metrics-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
                gap: 12px;
                margin: 15px 0;
            }}
            
            .metric-card {{
                background: #f8f9fa;
                padding: 14px 12px;
                border-radius: 10px;
                border-left: 4px solid {primary};
                text-align: center;
                transition: transform 0.3s, box-shadow 0.3s;
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
                font-size: 11px;
                color: #7F8C8D;
                margin-top: 4px;
                font-family: 'Times New Roman', serif;
            }}
            
            /* Progress bars */
            .progress-container {{
                margin: 8px 0;
            }}
            
            .progress-label {{
                display: flex;
                justify-content: space-between;
                font-size: 13px;
                margin-bottom: 3px;
            }}
            
            .progress-bar {{
                width: 100%;
                height: 22px;
                background: #f0f0f0;
                border-radius: 12px;
                overflow: hidden;
                position: relative;
                box-shadow: inset 0 1px 3px rgba(0,0,0,0.1);
            }}
            
            .progress-fill {{
                height: 100%;
                border-radius: 12px;
                transition: width 1s ease;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 11px;
                font-weight: 600;
                color: white;
                text-shadow: 0 1px 2px rgba(0,0,0,0.2);
                background: linear-gradient(90deg, {primary}, {secondary});
            }}
            
            /* Tables */
            .table-container {{
                overflow-x: auto;
                max-height: 600px;
                overflow-y: auto;
                border-radius: 10px;
                border: 1px solid #e8ecf1;
            }}
            
            .table-container::-webkit-scrollbar {{
                width: 8px;
                height: 8px;
            }}
            
            .table-container::-webkit-scrollbar-thumb {{
                background: {primary};
                border-radius: 4px;
            }}
            
            .table-container::-webkit-scrollbar-track {{
                background: #f0f0f0;
                border-radius: 4px;
            }}
            
            table {{
                width: 100%;
                border-collapse: collapse;
                font-family: 'Times New Roman', serif;
                font-size: 13px;
            }}
            
            thead {{
                position: sticky;
                top: 0;
                z-index: 10;
            }}
            
            th {{
                background: linear-gradient(135deg, {primary} 0%, {secondary} 100%);
                color: white;
                padding: 10px 12px;
                text-align: left;
                font-weight: 600;
                white-space: nowrap;
            }}
            
            td {{
                padding: 8px 12px;
                border-bottom: 1px solid #e8ecf1;
                vertical-align: middle;
            }}
            
            tr:hover {{
                background-color: #f8f9fa;
            }}
            
            .word-wrap {{
                word-wrap: break-word;
                max-width: 300px;
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
            
            /* Badges */
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
            .badge-primary {{ background: {primary}30; color: {primary}; }}
            .badge-secondary {{ background: {secondary}30; color: {secondary}; }}
            
            /* Heatmap */
            .heatmap-container {{
                overflow-x: auto;
                margin: 15px 0;
            }}
            
            .heatmap-table td {{
                text-align: center;
                padding: 8px 12px;
                min-width: 50px;
                font-weight: 500;
            }}
            
            .heatmap-table .year-label {{
                font-weight: 600;
                background: #f8f9fa;
                position: sticky;
                left: 0;
                z-index: 5;
            }}
            
            /* Collapsible Cards */
            .collapsible-card {{
                border: 1px solid #e8ecf1;
                border-radius: 10px;
                margin-bottom: 10px;
                overflow: hidden;
                transition: all 0.3s;
            }}
            
            .collapsible-card:hover {{
                border-color: {primary};
            }}
            
            .card-header {{
                padding: 12px 18px;
                background: #f8f9fa;
                cursor: pointer;
                display: flex;
                justify-content: space-between;
                align-items: center;
                transition: background 0.3s;
                user-select: none;
            }}
            
            .card-header:hover {{
                background: #e8ecf1;
            }}
            
            .card-header .card-title {{
                font-weight: 600;
                font-size: 14px;
                flex: 1;
            }}
            
            .card-header .card-meta {{
                display: flex;
                gap: 12px;
                align-items: center;
                font-size: 13px;
                color: #666;
            }}
            
            .card-header .card-toggle {{
                font-size: 18px;
                transition: transform 0.3s;
                color: {primary};
            }}
            
            .card-header .card-toggle.open {{
                transform: rotate(180deg);
            }}
            
            .card-body {{
                padding: 15px 18px;
                background: white;
            }}
            
            .citation-detail {{
                padding: 10px 15px;
                margin-bottom: 8px;
                background: #f8f9fa;
                border-radius: 8px;
                border-left: 3px solid {primary};
            }}
            
            .citation-detail:hover {{
                background: #f0f1f3;
            }}
            
            .citation-detail .cite-meta {{
                font-size: 12px;
                color: #666;
                margin-top: 4px;
            }}
            
            /* Filters */
            .filter-section {{
                background: #f8f9fa;
                padding: 15px 20px;
                border-radius: 10px;
                margin-bottom: 20px;
                border: 1px solid #e8ecf1;
            }}
            
            .filter-row {{
                display: flex;
                flex-wrap: wrap;
                gap: 15px;
                align-items: center;
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
            
            .filter-row select,
            .filter-row input {{
                width: 100%;
                padding: 6px 10px;
                border: 1px solid #ced4da;
                border-radius: 6px;
                font-size: 13px;
                font-family: inherit;
                transition: border-color 0.3s;
            }}
            
            .filter-row select:focus,
            .filter-row input:focus {{
                outline: none;
                border-color: {primary};
                box-shadow: 0 0 0 3px {primary}20;
            }}
            
            .filter-stats {{
                font-weight: 500;
                font-size: 14px;
                color: #333;
                padding: 5px 10px;
                background: white;
                border-radius: 6px;
                border: 1px solid #e8ecf1;
            }}
            
            /* Geo Analysis */
            .geo-grid {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
                margin: 15px 0;
            }}
            
            .geo-box {{
                background: #f8f9fa;
                padding: 15px 18px;
                border-radius: 10px;
                border: 1px solid #e8ecf1;
            }}
            
            .geo-box h4 {{
                margin: 0 0 10px 0;
                color: #2C3E50;
                font-size: 15px;
            }}
            
            .geo-box .geo-item {{
                display: flex;
                justify-content: space-between;
                padding: 4px 0;
                border-bottom: 1px solid #e8ecf1;
                font-size: 13px;
            }}
            
            .geo-box .geo-item:last-child {{
                border-bottom: none;
            }}
            
            .geo-box .geo-count {{
                font-weight: 600;
                color: {primary};
            }}
            
            /* Footer */
            .footer {{
                margin-top: 40px;
                padding-top: 20px;
                border-top: 2px solid #e8ecf1;
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
            
            /* Responsive */
            @media (max-width: 1024px) {{
                .sidebar {{
                    width: 220px;
                }}
                .main-content {{
                    margin-left: 220px;
                    padding: 20px;
                }}
                .geo-grid {{
                    grid-template-columns: 1fr;
                }}
            }}
            
            @media (max-width: 768px) {{
                .sidebar {{
                    display: none;
                }}
                .main-content {{
                    margin-left: 0;
                    padding: 15px;
                }}
                .header {{
                    flex-direction: column;
                    text-align: center;
                    padding: 20px;
                }}
                .header-left {{
                    flex-direction: column;
                }}
                .metrics-grid {{
                    grid-template-columns: repeat(2, 1fr);
                }}
                .filter-row {{
                    flex-direction: column;
                }}
                .filter-row > div {{
                    min-width: 100%;
                }}
            }}
            
            @media print {{
                .sidebar {{
                    display: none;
                }}
                .main-content {{
                    margin-left: 0;
                }}
                .section {{
                    page-break-inside: avoid;
                }}
            }}
        </style>
    </head>
    <body>
        <!-- Sidebar Navigation -->
        <div class="sidebar">
            {f'<img src="data:image/png;base64,{app_logo_base64}" class="logo-mini" alt="Logo">' if app_logo_base64 else ''}
            <h3>{t('app_title')}</h3>
            
            <div class="nav-section">
                <div class="nav-section-title">{t('overview')}</div>
                <a href="#overview"><span class="nav-icon">📊</span> {t('overview')}</a>
            </div>
            
            <div class="nav-section">
                <div class="nav-section-title">{t('analyzed_articles')}</div>
                <a href="#author_analysis"><span class="nav-icon">👤</span> {t('author_analysis')}</a>
                <a href="#top_affiliations"><span class="nav-icon">🏛️</span> {t('top_affiliations')}</a>
                <a href="#geographic"><span class="nav-icon">🌍</span> {t('geographic_analysis')}</a>
            </div>
            
            <div class="nav-section">
                <div class="nav-section-title">{t('citation_analysis')}</div>
                <a href="#citation_dynamics"><span class="nav-icon">📈</span> {t('citation_dynamics')}</a>
                <a href="#cumulative"><span class="nav-icon">📊</span> {t('cumulative_citations')}</a>
                <a href="#heatmap"><span class="nav-icon">🔥</span> {t('citation_network_heatmap')}</a>
                <a href="#most_cited"><span class="nav-icon">⭐</span> {t('most_cited_publications')}</a>
            </div>
            
            <div class="nav-section">
                <div class="nav-section-title">{t('citing_works_analysis')}</div>
                <a href="#citing_authors"><span class="nav-icon">👤</span> {t('top_citing_authors')}</a>
                <a href="#citing_affiliations"><span class="nav-icon">🏛️</span> {t('top_citing_affiliations')}</a>
                <a href="#citing_countries"><span class="nav-icon">🌍</span> {t('top_citing_countries')}</a>
                <a href="#citing_journals"><span class="nav-icon">📰</span> {t('top_citing_journals')}</a>
                <a href="#citing_publishers"><span class="nav-icon">🏢</span> {t('top_citing_publishers')}</a>
            </div>
            
            <div class="nav-section">
                <div class="nav-section-title">{t('topics_analysis')}</div>
                <a href="#topics"><span class="nav-icon">🏷️</span> {t('topics')}</a>
            </div>
            
            <div class="nav-section">
                <div class="nav-section-title">{t('detailed_citations')}</div>
                <a href="#detailed_citations"><span class="nav-icon">📋</span> {t('detailed_citations')}</a>
            </div>
            
            <div class="nav-section">
                <div class="nav-section-title">{t('all_publications')}</div>
                <a href="#all_publications"><span class="nav-icon">📚</span> {t('all_publications')}</a>
            </div>
        </div>
        
        <!-- Main Content -->
        <div class="main-content">
            <!-- Header -->
            <div class="header">
                <div class="header-left">
                    {f'<img src="data:image/png;base64,{app_logo_base64}" class="header-logo-app" alt="App Logo">' if app_logo_base64 else ''}
                    {f'<img src="data:image/png;base64,{logo_base64}" class="header-logo" alt="Journal Logo">' if logo_base64 else ''}
                    <div class="header-title">
                        <h1>{t('app_title')}</h1>
                        <div class="subtitle">ISSN: {result.get('issn', '')} | {t('period_label')}: {result.get('period', '')}</div>
                    </div>
                </div>
                <div class="header-right">
                    <div class="date">{t('generated')}: {datetime.now().strftime('%d.%m.%Y %H:%M')}</div>
                    <div style="font-size:12px; opacity:0.8;">{t('data_source')}</div>
                </div>
            </div>
            
            <!-- Overview Section -->
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
                        <div class="metric-value">{metrics.get('open_access', 0):.1f}%</div>
                        <div class="metric-label">{t('open_access')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{metrics.get('active_years', 0)}</div>
                        <div class="metric-label">{t('active_years')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{metrics.get('unique_authors', 0)}</div>
                        <div class="metric-label">{t('unique_authors')}</div>
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
                        <div class="metric-value">{metrics.get('international_collaboration_rate', 0):.1f}%</div>
                        <div class="metric-label">{t('international_collaboration_rate')}</div>
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
                
                <!-- Open Access Breakdown -->
                <h4 style="margin-top: 20px; color: {primary};">{t('open_access_breakdown')}</h4>
                <div class="metrics-grid" style="grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));">
                    {''.join([
                        f'<div class="metric-card" style="border-left-color: {oa_colors.get(status, "#95A5A6")};">'
                        f'<div class="metric-value">{count}</div>'
                        f'<div class="metric-label">{t(status)}</div>'
                        f'</div>'
                        for status, count in metrics.get('oa_breakdown', {}).items() if count > 0
                    ])}
                </div>
            </div>
            
            <!-- Author Analysis -->
            <div id="author_analysis" class="section">
                <div class="section-title"><span class="icon">👤</span> {t('author_analysis')}</div>
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
                                f'<tr>'
                                f'<td>{a["rank"]}</td>'
                                f'<td>{html.escape(a["name"])}</td>'
                                f'<td>{f\'<a href="https://orcid.org/{a["orcid"]}" target="_blank">{a["orcid"]}</a>\' if a["orcid"] else "-"}</td>'
                                f'<td>{", ".join([html.escape(aff) for aff in a["affiliations"]])}</td>'
                                f'<td>{", ".join(a["countries"])}</td>'
                                f'<td>{a["publications"]}</td>'
                                f'<td>{a["citations"]}</td>'
                                f'</tr>'
                                for a in author_analysis
                            ])}
                        </tbody>
                    </table>
                </div>
            </div>
            
            <!-- Top Affiliations -->
            <div id="top_affiliations" class="section">
                <div class="section-title"><span class="icon">🏛️</span> {t('top_affiliations')}</div>
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>{t('rank')}</th>
                                <th>{t('affiliations')}</th>
                                <th>{t('publications')}</th>
                                <th>{t('citations')}</th>
                                <th>{t('countries')}</th>
                            </tr>
                        </thead>
                        <tbody>
                            {''.join([
                                f'<tr>'
                                f'<td>{a["rank"]}</td>'
                                f'<td>{html.escape(a["name"])}</td>'
                                f'<td>' + (f'<a href="https://orcid.org/{a["orcid"]}" target="_blank">{a["orcid"]}</a>' if a["orcid"] else "-") + '</td>'
                                f'<td>{", ".join([html.escape(aff) for aff in a["affiliations"]])}</td>'
                                f'<td>{", ".join(a["countries"])}</td>'
                                f'<td>{a["publications"]}</td>'
                                f'<td>{a["citations"]}</td>'
                                f'</tr>'
                                for a in author_analysis
                            ])}
                        </tbody>
                    </table>
                </div>
            </div>
            
            <!-- Geographic Analysis -->
            <div id="geographic" class="section">
                <div class="section-title"><span class="icon">🌍</span> {t('geographic_analysis')}</div>
                
                <div class="geo-grid">
                    <div class="geo-box">
                        <h4>{t('countries_per_publication')}</h4>
                        <div><strong>{t('avg_countries_per_paper')}:</strong> {metrics.get('avg_countries_per_paper', 0):.2f}</div>
                        <div style="margin-top: 8px;">
                            <div class="geo-item"><span>{t('single_country')}</span> <span class="geo-count">{geographic.get('single_country', 0)}</span></div>
                            <div class="geo-item"><span>{t('international')}</span> <span class="geo-count">{geographic.get('international', 0)}</span></div>
                        </div>
                    </div>
                    
                    <div class="geo-box">
                        <h4>{t('authors_per_country')}</h4>
                        {''.join([
                            f'<div class="geo-item"><span>{html.escape(country)}</span> <span class="geo-count">{count}</span></div>'
                            for country, count in list(geographic.get('authors_per_country', {}).items())[:15]
                        ])}
                    </div>
                </div>
                
                <div style="margin-top: 15px;">
                    <h4 style="color: {primary};">{t('collaboration_couples')}</h4>
                    <div class="table-container" style="max-height: 300px;">
                        <table>
                            <thead>
                                <tr>
                                    <th>{t('country_pairs')}</th>
                                    <th>{t('frequency')}</th>
                                </tr>
                            </thead>
                            <tbody>
                                {''.join([
                                    f'<tr><td>{pair[0]} ↔ {pair[1]}</td><td>{count}</td></tr>'
                                    for (pair, count) in geographic.get('country_pairs', [])[:20]
                                ])}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
            
            <!-- Citation Dynamics -->
            <div id="citation_dynamics" class="section">
                <div class="section-title"><span class="icon">📈</span> {t('citation_dynamics')}</div>
                
                <div class="table-container" style="max-height: 400px;">
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
                                f'<tr><td>{d["publication_year"]}</td><td>{d["citation_year"]}</td><td>{d["count"]}</td></tr>'
                                for d in citation_dynamics.get('dynamics', [])
                            ])}
                        </tbody>
                    </table>
                </div>
                
                <!-- First Citation Analysis -->
                {f'''
                <div style="margin-top: 20px;">
                    <h4 style="color: {primary};">{t('first_citation_analysis')}</h4>
                    <div class="metrics-grid" style="grid-template-columns: repeat(4, 1fr);">
                        <div class="metric-card"><div class="metric-value">{citation_dynamics.get('first_citation_stats', {}).get('min', '-')}</div><div class="metric-label">{t('min_days')}</div></div>
                        <div class="metric-card"><div class="metric-value">{citation_dynamics.get('first_citation_stats', {}).get('max', '-')}</div><div class="metric-label">{t('max_days')}</div></div>
                        <div class="metric-card"><div class="metric-value">{citation_dynamics.get('first_citation_stats', {}).get('avg', 0):.1f}</div><div class="metric-label">{t('avg_days')}</div></div>
                        <div class="metric-card"><div class="metric-value">{citation_dynamics.get('first_citation_stats', {}).get('median', '-')}</div><div class="metric-label">{t('median_days')}</div></div>
                    </div>
                </div>
                ''' if citation_dynamics.get('first_citation_stats') else ''}
            </div>
            
            <!-- Cumulative Citations -->
            <div id="cumulative" class="section">
                <div class="section-title"><span class="icon">📊</span> {t('cumulative_citations')}</div>
                <div class="table-container" style="max-height: 300px;">
                    <table>
                        <thead>
                            <tr>
                                <th>{t('year')}</th>
                                <th>{t('cumulative_citations')}</th>
                            </tr>
                        </thead>
                        <tbody>
                            {''.join([
                                f'<tr><td>{year}</td><td>{count:,}</td></tr>'
                                for year, count in sorted(citation_dynamics.get('cumulative', {}).items())
                            ])}
                        </tbody>
                    </table>
                </div>
            </div>
            
            <!-- Citation Network Heatmap -->
            <div id="heatmap" class="section">
                <div class="section-title"><span class="icon">🔥</span> {t('citation_network_heatmap')}</div>
                <div class="heatmap-container">
                    <table class="heatmap-table">
                        <thead>
                            <tr>
                                <th style="background: {primary}; color: white; position: sticky; left: 0; z-index: 10;">{t('publication_year')} \\ {t('citation_year')}</th>
                                {''.join([
                                    f'<th style="background: {primary}; color: white;">{year}</th>'
                                    for year in sorted(set(d["citation_year"] for d in citation_dynamics.get('dynamics', [])))
                                ])}
                            </tr>
                        </thead>
                        <tbody>
                            {''.join([
                                f'<tr>'
                                f'<td class="year-label" style="background: #f8f9fa; font-weight: 600;">{pub_year}</td>'
                                + ''.join([
                                    f'<td style="background: {get_heatmap_color(count, max_count)}; color: {get_contrast_color(get_heatmap_color(count, max_count))};">{count if count > 0 else "-"}</td>'
                                    for citing_year in sorted(set(d["citation_year"] for d in citation_dynamics.get('dynamics', [])))
                                    for count in [next((d["count"] for d in citation_dynamics.get('dynamics', []) if d["publication_year"] == pub_year and d["citation_year"] == citing_year), 0)]
                                ])
                                f'</tr>'
                                for pub_year in sorted(set(d["publication_year"] for d in citation_dynamics.get('dynamics', [])))
                            ])}
                        </tbody>
                    </table>
                </div>
            </div>
            
            <!-- Most Cited Publications -->
            <div id="most_cited" class="section">
                <div class="section-title"><span class="icon">⭐</span> {t('most_cited_publications')}</div>
                <div class="table-container" style="max-height: 500px;">
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
                                f'<tr>'
                                f'<td>{p["rank"]}</td>'
                                f'<td class="word-wrap">{html.escape(p["title"])}</td>'
                                f'<td>{p["year"]}</td>'
                                f'<td><span class="badge badge-primary">{p["citations"]}</span></td>'
                                f'<td>{p["citations_per_year"]}</td>'
                                f'<td>{html.escape(p["authors"])}</td>'
                                f'<td><a href="https://doi.org/{p["doi"]}" target="_blank" class="doi-link">{p["doi"]}</a></td>'
                                f'</tr>'
                                for p in most_cited
                            ])}
                        </tbody>
                    </table>
                </div>
            </div>
            
            <!-- Citing Works Analysis -->
            <div id="citing_works" class="section">
                <div class="section-title"><span class="icon">📚</span> {t('citing_works_analysis')}</div>
                
                <div class="metrics-grid" style="grid-template-columns: repeat(3, 1fr);">
                    <div class="metric-card"><div class="metric-value">{len(citing_articles)}</div><div class="metric-label">{t('total_citing_works')}</div></div>
                    <div class="metric-card"><div class="metric-value">{metrics.get('unique_citing_authors', 0)}</div><div class="metric-label">{t('unique_citing_authors')}</div></div>
                    <div class="metric-card"><div class="metric-value">{metrics.get('unique_citing_affiliations', 0)}</div><div class="metric-label">{t('unique_citing_affiliations')}</div></div>
                    <div class="metric-card"><div class="metric-value">{metrics.get('unique_citing_countries', 0)}</div><div class="metric-label">{t('unique_citing_countries')}</div></div>
                    <div class="metric-card"><div class="metric-value">{metrics.get('unique_citing_journals', 0)}</div><div class="metric-label">{t('unique_citing_journals')}</div></div>
                    <div class="metric-card"><div class="metric-value">{metrics.get('unique_citing_publishers', 0)}</div><div class="metric-label">{t('unique_citing_publishers')}</div></div>
                </div>
                
                <!-- Top Citing Authors -->
                <div id="citing_authors" style="margin-top: 20px;">
                    <h4 style="color: {primary};">{t('top_citing_authors')}</h4>
                    {''.join([
                        f'<div class="geo-item"><span>{html.escape(author)}</span> <span class="geo-count">{count}</span></div>'
                        for author, count in list(Counter([a for article in citing_articles for a in article.get('authors', [])]).most_common(20))
                    ]) if citing_articles else '<p>No data</p>'}
                </div>
                
                <!-- Top Citing Affiliations -->
                <div id="citing_affiliations" style="margin-top: 15px;">
                    <h4 style="color: {primary};">{t('top_citing_affiliations')}</h4>
                    {''.join([
                        f'<div class="geo-item"><span>{html.escape(aff)}</span> <span class="geo-count">{count}</span></div>'
                        for aff, count in list(Counter([aff for article in citing_articles for aff in article.get('affiliations', []) if aff]).most_common(20))
                    ]) if citing_articles else '<p>No data</p>'}
                </div>
                
                <!-- Top Citing Countries -->
                <div id="citing_countries" style="margin-top: 15px;">
                    <h4 style="color: {primary};">{t('top_citing_countries')}</h4>
                    {''.join([
                        f'<div class="geo-item"><span>{html.escape(country)}</span> <span class="geo-count">{count}</span></div>'
                        for country, count in list(Counter([country for article in citing_articles for country in article.get('countries', []) if country]).most_common(20))
                    ]) if citing_articles else '<p>No data</p>'}
                </div>
                
                <!-- Top Citing Journals -->
                <div id="citing_journals" style="margin-top: 15px;">
                    <h4 style="color: {primary};">{t('top_citing_journals')}</h4>
                    {''.join([
                        f'<div class="geo-item"><span>{html.escape(journal)}</span> <span class="geo-count">{count}</span></div>'
                        for journal, count in list(Counter([article.get('journal_name', '') for article in citing_articles if article.get('journal_name') and article.get('journal_name') != 'Unknown']).most_common(20))
                    ]) if citing_articles else '<p>No data</p>'}
                </div>
                
                <!-- Top Citing Publishers -->
                <div id="citing_publishers" style="margin-top: 15px;">
                    <h4 style="color: {primary};">{t('top_citing_publishers')}</h4>
                    {''.join([
                        f'<div class="geo-item"><span>{html.escape(publisher)}</span> <span class="geo-count">{count}</span></div>'
                        for publisher, count in list(Counter([article.get('publisher', '') for article in citing_articles if article.get('publisher') and article.get('publisher') != 'Unknown']).most_common(20))
                    ]) if citing_articles else '<p>No data</p>'}
                </div>
            </div>
            
            <!-- Topics Analysis -->
            <div id="topics" class="section">
                <div class="section-title"><span class="icon">🏷️</span> {t('topics_analysis')}</div>
                
                <div class="table-container" style="max-height: 500px;">
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
                                f'<tr>'
                                f'<td class="word-wrap">{html.escape(t["topic"])}</td>'
                                f'<td>{t["analyzed_count"]}</td>'
                                f'<td>{t["citing_count"]}</td>'
                                f'<td>{t["analyzed_norm_count"]}</td>'
                                f'<td>{t["citing_norm_count"]}</td>'
                                f'<td><span class="badge badge-primary">{t["total_norm_count"]}</span></td>'
                                f'<td>{t["first_year"] or "-"}</td>'
                                f'<td>{t["peak_year"] or "-"}</td>'
                                f'</tr>'
                                for t in topic_analysis.get('topics', [])[:30]
                            ])}
                        </tbody>
                    </table>
                </div>
                
                <!-- Top 10 Most Cited Topics -->
                <div style="margin-top: 20px;">
                    <h4 style="color: {primary};">{t('top_10_cited_topics')}</h4>
                    {''.join([
                        f'<div class="geo-item"><span>{html.escape(topic)}</span> <span class="geo-count">{citations}</span></div>'
                        for topic, citations in topic_analysis.get('top_cited_topics', [])[:10]
                    ]) if topic_analysis.get('top_cited_topics') else '<p>No data</p>'}
                </div>
            </div>
            
            <!-- Detailed Citations -->
            {f'''
            <div id="detailed_citations" class="section">
                <div class="section-title"><span class="icon">📋</span> {t('detailed_citations')}</div>
                
                {''.join([
                    f'''
                    <div class="collapsible-card">
                        <div class="card-header" onclick="toggleCard(this)">
                            <span class="card-title">{html.escape(data['title'])}</span>
                            <span class="card-meta">
                                <span class="badge badge-info">{data['year']}</span>
                                <span class="badge badge-primary">{data['total_citations']} {t('citations')}</span>
                                <span style="font-size: 12px; color: #666;">DOI: {data['doi']}</span>
                                <span class="card-toggle">▼</span>
                            </span>
                        </div>
                        <div class="card-body" style="display: none;">
                            {''.join([
                                f'''
                                <div class="citation-detail">
                                    <div><strong>{html.escape(cite['citing_title'])}</strong></div>
                                    <div class="cite-meta">
                                        <strong>{t('citing_journal')}:</strong> {html.escape(cite['citing_journal'])} | 
                                        <strong>{t('citing_year')}:</strong> {cite['citing_year']} | 
                                        <strong>{t('citing_date')}:</strong> {cite['citing_date']} |
                                        <strong>{t('citation_lag')}:</strong> {cite['citation_lag']} {t('years') if cite['citation_lag'] else '-'}
                                    </div>
                                    <div class="cite-meta">
                                        <strong>{t('authors')}:</strong> {', '.join(cite['citing_authors'][:5])}{' +' + str(len(cite['citing_authors']) - 5) + ' more' if len(cite['citing_authors']) > 5 else ''} |
                                        <strong>{t('countries')}:</strong> {', '.join(cite['citing_countries'][:5])} |
                                        <strong>{t('topics')}:</strong> {', '.join(cite['citing_topics'][:3])}
                                    </div>
                                    <div class="cite-meta">
                                        <a href="https://doi.org/{cite['citing_doi']}" target="_blank" class="doi-link">DOI: {cite['citing_doi']}</a>
                                    </div>
                                </div>
                                ''' for cite in data['citations'][:20]
                            ])}
                            {f'<p style="margin-top: 8px; font-style: italic; color: #666;">... and {len(data["citations"]) - 20} more citations</p>' if len(data['citations']) > 20 else ''}
                        </div>
                    </div>
                    ''' for doi, data in list(detailed_citations.items())[:30]
                ])}
            </div>
            ''' if detailed_citations else ''}
            
            <!-- All Publications -->
            <div id="all_publications" class="section">
                <div class="section-title"><span class="icon">📚</span> {t('all_publications')}</div>
                
                <div class="filter-section">
                    <div class="filter-row">
                        <div>
                            <label for="titleFilter">{t('filter_by_title')}:</label>
                            <input type="text" id="titleFilter" placeholder="{t('filter_placeholder_title')}" oninput="filterTable()">
                        </div>
                        <div>
                            <label for="yearFilter">{t('filter_by_year')}:</label>
                            <select id="yearFilter" onchange="filterTable()">
                                <option value="">All Years</option>
                                {''.join([
                                    f'<option value="{year}">{year}</option>'
                                    for year in sorted(set(a.get('publication_year') for a in all_publications_data if a.get('publication_year')), reverse=True)
                                ])}
                            </select>
                        </div>
                        <div>
                            <label for="authorFilter">{t('filter_by_author')}:</label>
                            <input type="text" id="authorFilter" placeholder="{t('filter_placeholder_author')}" oninput="filterTable()">
                        </div>
                        <div>
                            <label for="affiliationFilter">{t('filter_by_affiliation')}:</label>
                            <input type="text" id="affiliationFilter" placeholder="{t('filter_placeholder_affiliation')}" oninput="filterTable()">
                        </div>
                        <div>
                            <label for="citationFilter">{t('filter_by_citations_min')}:</label>
                            <input type="number" id="citationFilter" placeholder="0" min="0" oninput="filterTable()">
                        </div>
                        <div>
                            <span id="filterStats" class="filter-stats">{t('showing_results', shown=len(all_publications_data), total=len(all_publications_data))}</span>
                        </div>
                    </div>
                </div>
                
                <div class="table-container" style="max-height: 700px;">
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
                                f'<tr data-year="{a.get("publication_year", "")}" data-authors="{",".join(a.get("authors", []))}" data-affiliations="{",".join(a.get("affiliations", []))}" data-citations="{a.get("cited_by_count", 0)}" data-title="{html.escape(a.get("title", "")).lower()}">'
                                f'<td>{i+1}</td>'
                                f'<td class="word-wrap">{html.escape(a.get("title", "No title"))}</td>'
                                f'<td>{a.get("publication_year", "-")}</td>'
                                f'<td>{", ".join(a.get("authors", [])[:3])}{" +" + str(len(a.get("authors", [])) - 3) + " more" if len(a.get("authors", [])) > 3 else ""}</td>'
                                f'<td>{", ".join(a.get("affiliations", [])[:2])}{" +" + str(len(a.get("affiliations", [])) - 2) + " more" if len(a.get("affiliations", [])) > 2 else ""}</td>'
                                f'<td><span class="badge badge-primary">{a.get("cited_by_count", 0)}</span></td>'
                                f'<td>{(a.get("cited_by_count", 0) / (2026 - a.get("publication_year", 2026) + 1)):.1f if a.get("publication_year") else "-"}</td>'
                                f'<td><a href="https://doi.org/{a.get("doi", "")}" target="_blank" class="doi-link">{a.get("doi", "")}</a></td>'
                                f'</tr>'
                                for i, a in enumerate(all_publications_data)
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
            // Toggle collapsible cards
            function toggleCard(header) {{
                const body = header.nextElementSibling;
                const toggle = header.querySelector('.card-toggle');
                if (body.style.display === 'none' || body.style.display === '') {{
                    body.style.display = 'block';
                    if (toggle) toggle.classList.add('open');
                }} else {{
                    body.style.display = 'none';
                    if (toggle) toggle.classList.remove('open');
                }}
            }}
            
            // Filter publications table
            function filterTable() {{
                const titleFilter = document.getElementById('titleFilter').value.toLowerCase();
                const yearFilter = document.getElementById('yearFilter').value;
                const authorFilter = document.getElementById('authorFilter').value.toLowerCase();
                const affiliationFilter = document.getElementById('affiliationFilter').value.toLowerCase();
                const citationFilter = parseInt(document.getElementById('citationFilter').value) || 0;
                
                const rows = document.querySelectorAll('#publicationsTable tbody tr');
                let visible = 0;
                
                rows.forEach(row => {{
                    const title = row.getAttribute('data-title') || '';
                    const year = row.getAttribute('data-year') || '';
                    const authors = row.getAttribute('data-authors') || '';
                    const affiliations = row.getAttribute('data-affiliations') || '';
                    const citations = parseInt(row.getAttribute('data-citations')) || 0;
                    
                    let show = true;
                    
                    if (titleFilter && !title.includes(titleFilter)) show = false;
                    if (yearFilter && year !== yearFilter) show = false;
                    if (authorFilter && !authors.toLowerCase().includes(authorFilter)) show = false;
                    if (affiliationFilter && !affiliations.toLowerCase().includes(affiliationFilter)) show = false;
                    if (citations < citationFilter) show = false;
                    
                    row.style.display = show ? '' : 'none';
                    if (show) visible++;
                }});
                
                document.getElementById('filterStats').textContent = 
                    'Showing ' + visible + ' of ' + rows.length + ' publications';
            }}
            
            // Sort table
            let sortDirection = {{}};
            function sortTable(col) {{
                const table = document.getElementById('publicationsTable');
                const tbody = table.querySelector('tbody');
                const rows = Array.from(tbody.querySelectorAll('tr'));
                
                if (!sortDirection[col]) sortDirection[col] = 1;
                else sortDirection[col] *= -1;
                
                rows.sort((a, b) => {{
                    let aVal = a.cells[col].textContent.trim();
                    let bVal = b.cells[col].textContent.trim();
                    
                    // Try numeric comparison
                    const aNum = parseFloat(aVal);
                    const bNum = parseFloat(bVal);
                    if (!isNaN(aNum) && !isNaN(bNum)) {{
                        return (aNum - bNum) * sortDirection[col];
                    }}
                    
                    return aVal.localeCompare(bVal) * sortDirection[col];
                }});
                
                rows.forEach(row => tbody.appendChild(row));
                
                // Update header arrows
                const headers = table.querySelectorAll('thead th');
                headers.forEach((th, i) => {{
                    th.textContent = th.textContent.replace(/ [▲▼]/, '');
                    if (i === col) {{
                        th.textContent += sortDirection[col] === 1 ? ' ▲' : ' ▼';
                    }}
                }});
            }}
            
            // Initialize filter stats
            document.addEventListener('DOMContentLoaded', function() {{
                const rows = document.querySelectorAll('#publicationsTable tbody tr');
                document.getElementById('filterStats').textContent = 
                    'Showing ' + rows.length + ' of ' + rows.length + ' publications';
            }});
        </script>
    </body>
    </html>
    """
    
    return html_content

def get_heatmap_color(value: int, max_value: int) -> str:
    """Возвращает цвет для тепловой карты на основе значения"""
    if max_value == 0:
        return '#f8f9fa'
    
    ratio = value / max_value if max_value > 0 else 0
    
    # Получаем цвета темы из сессии
    primary = st.session_state.get('primary_color', '#667eea')
    secondary = st.session_state.get('secondary_color', '#f39c12')
    
    # Преобразуем в RGB
    p_rgb = hex_to_rgb(primary)
    s_rgb = hex_to_rgb(secondary)
    
    # Интерполяция между secondary и primary в зависимости от ratio
    r = int(s_rgb[0] + (p_rgb[0] - s_rgb[0]) * ratio)
    g = int(s_rgb[1] + (p_rgb[1] - s_rgb[1]) * ratio)
    b = int(s_rgb[2] + (p_rgb[2] - s_rgb[2]) * ratio)
    
    return f'rgb({r}, {g}, {b})'

def generate_journal_report_with_caching(issn: str, period, max_workers: int = 8,
                                         progress_callback=None) -> Tuple[Dict, str]:
    """
    Запускает анализ журнала с кэшированием в сессии
    
    Returns:
        Tuple[Dict, str]: (результат анализа, HTML отчет)
    """
    # Проверяем кэш
    cache_key = f"{issn}_{str(period)}_{max_workers}"
    
    if 'journal_cache' in st.session_state:
        cached = st.session_state.journal_cache.get(cache_key)
        if cached:
            if SHOW_DEBUG_LOGS:
                print(f"✅ Использован кэш для {issn}")
            return cached['result'], cached['html']
    
    # Прогресс-коллбэки
    progress_data = {
        'stage1': {'current': 0, 'total': 0},
        'stage2': {'current': 0, 'total': 0},
        'stage3': {'current': 0, 'total': 0},
        'stage4': {'current': 0, 'total': 0},
        'stage5': {'current': 0, 'total': 0}
    }
    
    def stage1_callback(current, total):
        progress_data['stage1']['current'] = current
        progress_data['stage1']['total'] = total if total else current
        if progress_callback:
            progress_callback('stage1', current, total)
    
    def stage2_callback(current, total):
        progress_data['stage2']['current'] = current
        progress_data['stage2']['total'] = total if total else current
        if progress_callback:
            progress_callback('stage2', current, total)
    
    def stage3_callback(current, total):
        progress_data['stage3']['current'] = current
        progress_data['stage3']['total'] = total if total else current
        if progress_callback:
            progress_callback('stage3', current, total)
    
    def stage4_callback(current, total):
        progress_data['stage4']['current'] = current
        progress_data['stage4']['total'] = total if total else current
        if progress_callback:
            progress_callback('stage4', current, total)
    
    def stage5_callback(current, total):
        progress_data['stage5']['current'] = current
        progress_data['stage5']['total'] = total if total else current
        if progress_callback:
            progress_callback('stage5', current, total)
    
    callbacks = {
        'stage1': stage1_callback,
        'stage2': stage2_callback,
        'stage3': stage3_callback,
        'stage4': stage4_callback,
        'stage5': stage5_callback
    }
    
    # Запускаем анализ
    result = run_journal_analysis(issn, period, max_workers, callbacks)
    
    # Генерируем HTML отчет
    theme_colors = {
        'primary': st.session_state.get('primary_color', '#667eea'),
        'secondary': st.session_state.get('secondary_color', '#f39c12')
    }
    
    app_logo_base64 = None
    if os.path.exists("logo.png"):
        try:
            with open("logo.png", "rb") as f:
                app_logo_base64 = base64.b64encode(f.read()).decode()
        except Exception as e:
            if SHOW_DEBUG_LOGS:
                print(f"⚠️ Ошибка загрузки логотипа: {e}")
    
    journal_logo_base64 = st.session_state.get('journal_logo_base64', None)
    
    html_report = generate_journal_html_report(
        result,
        journal_logo_base64,
        app_logo_base64,
        theme_colors,
        st.session_state.get('language', 'en')
    )
    
    # Сохраняем в кэш
    if 'journal_cache' not in st.session_state:
        st.session_state.journal_cache = {}
    
    st.session_state.journal_cache[cache_key] = {
        'result': result,
        'html': html_report,
        'timestamp': datetime.now().isoformat()
    }
    
    return result, html_report

# ============================================
# ОСНОВНАЯ ФУНКЦИЯ ЗАПУСКА ДЛЯ STREAMLIT
# ============================================

def run_journal_analysis_ui(issn: str, period, max_workers: int, journal_logo: Optional[Dict] = None):
    """Запускает анализ журнала с UI прогрессом"""
    
    current_lang = st.session_state.get('language', 'en')
    def t(key: str, **kwargs) -> str:
        return translate(key, current_lang, **kwargs)
    
    if not issn:
        st.error(t('no_issn'))
        return
    
    if not period:
        st.error(t('no_period'))
        return
    
    # Парсим период
    period_str = str(period).strip()
    if ',' in period_str:
        period_parsed = [int(y.strip()) for y in period_str.split(',') if y.strip().isdigit()]
    elif '-' in period_str:
        parts = period_str.split('-')
        if len(parts) == 2:
            period_parsed = (int(parts[0].strip()), int(parts[1].strip()))
        else:
            period_parsed = int(period_str)
    else:
        try:
            period_parsed = int(period_str)
        except:
            st.error(f"⚠️ Invalid period format: {period_str}")
            return
    
    # Проверяем кэш
    cache_key = f"{issn}_{str(period_parsed)}_{max_workers}"
    
    if 'journal_cache' in st.session_state and cache_key in st.session_state.journal_cache:
        cached = st.session_state.journal_cache[cache_key]
        st.success(t('cache_hit', issn=issn, period=period_str))
        
        # Показываем отчет
        st.markdown("---")
        st.markdown(f"## {t('report_preview')}")
        
        html_report = cached['html']
        st.download_button(
            label=t('download_report'),
            data=html_report.encode('utf-8'),
            file_name=f"journal_analysis_{issn}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
            mime="text/html",
            width='stretch'
        )
        
        with st.expander("📋 " + t('report_preview'), expanded=True):
            st.components.v1.html(html_report, height=800, scrolling=True)
        
        return
    
    # Прогресс-бар
    progress_container = st.empty()
    status_container = st.empty()
    progress_bar = st.progress(0)
    
    # Статусы этапов
    stage_status = {
        'stage1': {'label': t('stage1'), 'completed': False},
        'stage2': {'label': t('stage2'), 'completed': False},
        'stage3': {'label': t('stage3'), 'completed': False},
        'stage4': {'label': t('stage4'), 'completed': False},
        'stage5': {'label': t('stage5'), 'completed': False}
    }
    
    stage_weights = {
        'stage1': 0.15,
        'stage2': 0.25,
        'stage3': 0.20,
        'stage4': 0.25,
        'stage5': 0.15
    }
    
    stage_progress = {
        'stage1': {'current': 0, 'total': 0},
        'stage2': {'current': 0, 'total': 0},
        'stage3': {'current': 0, 'total': 0},
        'stage4': {'current': 0, 'total': 0},
        'stage5': {'current': 0, 'total': 0}
    }
    
    def progress_callback(stage: str, current: int, total: Optional[int]):
        """Обработчик прогресса"""
        if total is not None:
            stage_progress[stage]['total'] = total
        stage_progress[stage]['current'] = current
        
        # Вычисляем общий прогресс
        total_progress = 0
        for s, weight in stage_weights.items():
            if stage_progress[s]['total'] > 0:
                p = stage_progress[s]['current'] / stage_progress[s]['total']
            else:
                p = 0
            total_progress += p * weight
        
        # Обновляем UI
        progress_bar.progress(min(total_progress, 1.0))
        
        # Обновляем статус
        if stage in stage_status:
            stage_status[stage]['completed'] = (current == total) if total else False
        
        # Формируем сообщение
        if total:
            status_text = f"{stage_status[stage]['label']} {t('stage_processing', current=current, total=total)}"
        else:
            status_text = stage_status[stage]['label']
        
        status_container.info(status_text)
    
    try:
        # Загружаем логотип приложения
        app_logo_base64 = None
        if os.path.exists("logo.png"):
            try:
                with open("logo.png", "rb") as f:
                    app_logo_base64 = base64.b64encode(f.read()).decode()
            except Exception as e:
                if SHOW_DEBUG_LOGS:
                    print(f"⚠️ Ошибка загрузки логотипа: {e}")
        
        # Загружаем логотип журнала
        journal_logo_base64 = None
        if journal_logo:
            try:
                for filename, file_info in journal_logo.items():
                    content = file_info['content'] if hasattr(file_info, 'get') else file_info
                    if hasattr(content, 'read'):
                        content = content.read()
                    journal_logo_base64 = base64.b64encode(content).decode()
                    st.session_state.journal_logo_base64 = journal_logo_base64
                    break
            except Exception as e:
                st.warning(f"⚠️ Ошибка загрузки логотипа журнала: {e}")
        
        # Запускаем анализ
        result, html_report = generate_journal_report_with_caching(
            issn,
            period_parsed,
            max_workers,
            progress_callback
        )
        
        # Завершаем прогресс
        progress_bar.progress(1.0)
        status_container.success(t('stage5_complete'))
        
        st.success(t('analysis_complete'))
        
        # Показываем отчет
        st.markdown("---")
        st.markdown(f"## {t('report_preview')}")
        
        st.download_button(
            label=t('download_report'),
            data=html_report.encode('utf-8'),
            file_name=f"journal_analysis_{issn}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
            mime="text/html",
            width='stretch'
        )
        
        with st.expander("📋 " + t('report_preview'), expanded=True):
            st.components.v1.html(html_report, height=800, scrolling=True)
        
    except Exception as e:
        st.error(t('analysis_error', error=str(e)))
        import traceback
        st.code(traceback.format_exc())

# ============================================
# СОЗДАНИЕ WIDGET-ИНТЕРФЕЙСА STREAMLIT (ОБНОВЛЕННЫЙ)
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
    if 'journal_cache' not in st.session_state:
        st.session_state.journal_cache = {}
    if 'journal_logo_base64' not in st.session_state:
        st.session_state.journal_logo_base64 = None
    
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
        
        # Upload journal logo
        st.markdown(f"## {t('upload_logo')}")
        journal_logo_upload = st.file_uploader(
            t('upload_logo'),
            type=['png', 'jpg', 'jpeg', 'svg'],
            help=t('logo_help')
        )
        
        if journal_logo_upload:
            try:
                content = journal_logo_upload.read()
                st.session_state.journal_logo_base64 = base64.b64encode(content).decode()
                st.success("✅ Logo uploaded")
            except Exception as e:
                st.warning(f"⚠️ Error: {e}")
        
        st.markdown("---")
        
        st.markdown(f"""
        <div style="font-size: 11px; color: #666; text-align: center;">
            {t('theme_info')}<br><br>
            © daM / Chimica Techno Acta<br>
            <a href="{t('journal_url')}" target="_blank">{t('journal_url')}</a>
        </div>
        """, unsafe_allow_html=True)
    
    # Main content
    st.markdown("---")
    
    # Logo and title
    col_logo, col_text = st.columns([1, 3])
    with col_logo:
        if os.path.exists("logo.png"):
            st.image("logo.png", width=200)
    with col_text:
        st.markdown(f"## {t('app_title')}")
        st.markdown(f"### {t('journal_analysis')}")
    
    st.markdown("---")
    
    # Input fields
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        issn_input = st.text_input(
            t('issn_label'),
            placeholder=t('issn_placeholder'),
            help="Enter ISSN in format XXXX-XXXX"
        )
    
    with col2:
        period_input = st.text_input(
            t('period_label'),
            placeholder=t('period_placeholder'),
            help=t('period_help')
        )
    
    with col3:
        workers_input = st.slider(
            t('workers_label'),
            min_value=4,
            max_value=12,
            value=8,
            step=1,
            help=t('workers_help')
        )
    
    # Analyze button
    if st.button(t('run_analysis'), type="primary", width='stretch'):
        journal_logo_data = None
        if st.session_state.journal_logo_base64:
            journal_logo_data = {'logo': {'content': base64.b64decode(st.session_state.journal_logo_base64)}}
        
        run_journal_analysis_ui(
            issn_input.strip(),
            period_input.strip(),
            workers_input,
            journal_logo_data
        )
    
    # Show info if no analysis
    if not st.session_state.journal_cache:
        st.info(t('no_data'))

if __name__ == "__main__":
    main()
