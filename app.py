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
        'unique_citing_affiliations': 'Unique Citing Affiliations',
        'avg_citation_lag': 'Avg Citation Lag (years)',
        'hot_topics': 'Hot Topics (Citation Impact)',
        'topic_overlap': 'Topic Overlap',
        
        # Report sections
        'executive_summary': '📊 Executive Summary',
        'publication_dynamics': '📈 Publication Dynamics',
        'most_cited_publications': '🏆 Most Cited Publications',
        'author_analysis': '👨‍🎓 Author Analysis',
        'affiliation_analysis': '🏛️ Affiliation & Country Analysis',
        'citation_analysis': '📊 Citation Analysis',
        'citation_matrix': '📊 Citation Matrix by Year',
        'citing_works_analysis': '📚 Citing Works Analysis',
        'citing_works_distribution': '📊 Citing Works Distribution',
        'topic_analysis': '🏷️ Topics Analysis',
        'topic_relationship': '🔄 Topic Relationship',
        'detailed_citations': '📋 Detailed Citations',
        'all_publications': '📚 All Publications',
        'publication_year': 'Publication Year',
        'citation_year': 'Citation Year',
        'citations_count': 'Citations Count',
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
        'unique_countries_per_citing_work': 'Unique Countries per Citing Work',
        'authors_per_country_citing': 'Authors per Country (Citing Works)',
        'collaboration_patterns_citing': 'Collaboration Patterns (Citing Works)',
        
        # Topics
        'topics': 'Topics',
        'fields': 'Fields',
        'domains': 'Domains',
        'concepts': 'Concepts',
        'publication_topics': 'Publication Topics',
        'citing_topics': 'Citing Topics',
        'topic_overlap_percentage': 'Topic Overlap Percentage',
        'hot_topic_index': 'Hot Topic Index',
        
        # Geography
        'geography_type_1': 'Type 1: Unique Countries per Reference',
        'geography_type_1_desc': 'Each reference counted once per unique country',
        'geography_type_2': 'Type 2: Authors per Country',
        'geography_type_2_desc': 'Each author counted separately',
        'geography_type_3': 'Type 3: Collaboration Patterns',
        'geography_type_3_desc': 'Distribution of single-country vs international collaborations',
        'single_country': 'Single country',
        'international_collaboration': 'International collaboration',
        'collaboration_matrix': 'Collaboration matrix (country pairs)',
        
        # Filters
        'filter_by_year': 'Filter by Year',
        'filter_by_author': 'Filter by Author',
        'filter_by_citations': 'Filter by Citations (min)',
        'search_publications': 'Search publications',
        'show_citations': 'Show Citations',
        'hide_citations': 'Hide Citations',
        
        # Navigation
        'nav_executive_summary': 'Executive Summary',
        'nav_publication_dynamics': 'Publication Dynamics',
        'nav_most_cited': 'Most Cited Publications',
        'nav_author_analysis': 'Author Analysis',
        'nav_affiliation_analysis': 'Affiliation Analysis',
        'nav_citation_analysis': 'Citation Analysis',
        'nav_citation_matrix': 'Citation Matrix',
        'nav_topic_analysis': 'Topics Analysis',
        'nav_citing_works': 'Citing Works Analysis',
        'nav_citing_distribution': 'Citing Works Distribution',
        'nav_topic_relationship': 'Topic Relationship',
        'nav_detailed_citations': 'Detailed Citations',
        'nav_all_publications': 'All Publications',
        
        # Footer
        'footer': '© Journal Analytics System / Created by daM / Chimica Techno Acta',
        'journal_url': 'https://chimicatechnoacta.ru',
        
        # Design Theme
        'design_theme': '🎨 Design Theme',
        'theme_default': 'Gradient Classic',
        'theme_glassmorphism': 'Glassmorphism',
        'theme_neon_dark': 'Neon Dark',
        'theme_aurora': 'Aurora Borealis',
        'theme_brutalist': 'Brutalist',
        'theme_minimalist_white': 'Minimalist White',
        'theme_ocean_deep': 'Ocean Deep',
        'theme_cosmic': 'Cosmic',
        'theme_terrazzo': 'Terrazzo',
        'theme_modern_cards': 'Modern Cards',
        'theme_duotone': 'Duotone',
        'theme_morphing': 'Morphing',
        'theme_current': 'Current: {}',
        'theme_color_warning': '⚠️ Color Theme is disabled for this design',
        'theme_color_partial': 'ℹ️ Color Theme uses only Primary color for accents',
        'reference_colors': '🎨 Reference Color Style',
        'ref_colors_full': 'Full (background + border)',
        'ref_colors_border': 'Border only',
        'ref_colors_icons': 'Icons only',
        'ref_colors_themed': 'Themed (follows primary color)',
        'ref_colors_text': 'Text only',
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
        'unique_citing_affiliations': 'Уникальных цитирующих аффилиаций',
        'avg_citation_lag': 'Средняя задержка цитирования (лет)',
        'hot_topics': 'Горячие темы',
        'topic_overlap': 'Пересечение тем',
        
        # Report sections
        'executive_summary': '📊 Сводка',
        'publication_dynamics': '📈 Динамика публикаций',
        'most_cited_publications': '🏆 Самые цитируемые публикации',
        'author_analysis': '👨‍🎓 Анализ авторов',
        'affiliation_analysis': '🏛️ Анализ аффилиаций и стран',
        'citation_analysis': '📊 Анализ цитирований',
        'citation_matrix': '📊 Матрица цитирований по годам',
        'citing_works_analysis': '📚 Анализ цитирующих работ',
        'citing_works_distribution': '📊 Распределение цитирующих работ',
        'topic_analysis': '🏷️ Тематический анализ',
        'topic_relationship': '🔄 Взаимосвязь тем',
        'detailed_citations': '📋 Детальные цитирования',
        'all_publications': '📚 Все публикации',
        'publication_year': 'Год публикации',
        'citation_year': 'Год цитирования',
        'citations_count': 'Количество цитирований',
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
        'unique_countries_per_citing_work': 'Уникальных стран на цитирующую работу',
        'authors_per_country_citing': 'Авторов по странам (цитирующие работы)',
        'collaboration_patterns_citing': 'Паттерны коллабораций (цитирующие работы)',
        
        # Topics
        'topics': 'Темы',
        'fields': 'Поля',
        'domains': 'Домены',
        'concepts': 'Концепты',
        'publication_topics': 'Темы публикаций',
        'citing_topics': 'Темы цитирующих работ',
        'topic_overlap_percentage': 'Процент пересечения тем',
        'hot_topic_index': 'Индекс горячих тем',
        
        # Geography
        'geography_type_1': 'Тип 1: Уникальные страны по ссылке',
        'geography_type_1_desc': 'Каждая ссылка учитывается один раз на уникальную страну',
        'geography_type_2': 'Тип 2: Авторы по странам',
        'geography_type_2_desc': 'Каждый автор учитывается отдельно',
        'geography_type_3': 'Тип 3: Паттерны коллабораций',
        'geography_type_3_desc': 'Распределение внутристрановых и международных коллабораций',
        'single_country': 'Одна страна',
        'international_collaboration': 'Международная коллаборация',
        'collaboration_matrix': 'Матрица коллабораций (пары стран)',
        
        # Filters
        'filter_by_year': 'Фильтр по году',
        'filter_by_author': 'Фильтр по автору',
        'filter_by_citations': 'Фильтр по цитированиям (мин)',
        'search_publications': 'Поиск публикаций',
        'show_citations': 'Показать цитирования',
        'hide_citations': 'Скрыть цитирования',
        
        # Navigation
        'nav_executive_summary': 'Сводка',
        'nav_publication_dynamics': 'Динамика публикаций',
        'nav_most_cited': 'Самые цитируемые',
        'nav_author_analysis': 'Анализ авторов',
        'nav_affiliation_analysis': 'Анализ аффилиаций',
        'nav_citation_analysis': 'Анализ цитирований',
        'nav_citation_matrix': 'Матрица цитирований',
        'nav_topic_analysis': 'Тематический анализ',
        'nav_citing_works': 'Цитирующие работы',
        'nav_citing_distribution': 'Распределение цитирующих',
        'nav_topic_relationship': 'Взаимосвязь тем',
        'nav_detailed_citations': 'Детальные цитирования',
        'nav_all_publications': 'Все публикации',
        
        # Footer
        'footer': '© Journal Analytics System / Created by daM / Chimica Techno Acta',
        'journal_url': 'https://chimicatechnoacta.ru',
        
        # Design Theme
        'design_theme': '🎨 Тема оформления',
        'theme_default': 'Gradient Classic',
        'theme_glassmorphism': 'Glassmorphism',
        'theme_neon_dark': 'Neon Dark',
        'theme_aurora': 'Aurora Borealis',
        'theme_brutalist': 'Brutalist',
        'theme_minimalist_white': 'Minimalist White',
        'theme_ocean_deep': 'Ocean Deep',
        'theme_cosmic': 'Cosmic',
        'theme_terrazzo': 'Terrazzo',
        'theme_modern_cards': 'Modern Cards',
        'theme_duotone': 'Duotone',
        'theme_morphing': 'Morphing',
        'theme_current': 'Текущая: {}',
        'theme_color_warning': '⚠️ Цветовая тема отключена для этого дизайна',
        'theme_color_partial': 'ℹ️ Цветовая тема использует только Primary цвет для акцентов',
        'reference_colors': '🎨 Стиль цветной кодировки',
        'ref_colors_full': 'Полный (фон + граница)',
        'ref_colors_border': 'Только граница',
        'ref_colors_icons': 'Только иконки',
        'ref_colors_themed': 'Тематический (следует primary цвету)',
        'ref_colors_text': 'Только текст',
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
# THEME UTILITIES (FROM OLD CODE)
# ============================================

def get_available_themes() -> List[str]:
    """Get list of available design themes"""
    return [
        'default',
        'glassmorphism',
        'neon_dark',
        'aurora',
        'brutalist',
        'minimalist_white',
        'ocean_deep',
        'cosmic',
        'terrazzo',
        'modern_cards',
        'duotone',
        'morphing'
    ]

def get_theme_display_name(theme_id: str) -> str:
    """Get display name for a theme"""
    theme_names = {
        'default': '🎨 Gradient Classic',
        'glassmorphism': '🪟 Glassmorphism',
        'neon_dark': '🌙 Neon Dark',
        'aurora': '🌌 Aurora Borealis',
        'brutalist': '🏛 Brutalist',
        'minimalist_white': '⬜ Minimalist White',
        'ocean_deep': '🌊 Ocean Deep',
        'cosmic': '🚀 Cosmic',
        'terrazzo': '🎨 Terrazzo',
        'modern_cards': '📐 Modern Cards',
        'duotone': '🌈 Duotone',
        'morphing': '🌀 Morphing'
    }
    return theme_names.get(theme_id, theme_id)

def get_theme_info(theme_id: str) -> Dict:
    """Get information about a theme"""
    theme_info = {
        'default': {'name': 'Gradient Classic', 'uses_primary': True, 'uses_secondary': True},
        'glassmorphism': {'name': 'Glassmorphism', 'uses_primary': True, 'uses_secondary': True},
        'neon_dark': {'name': 'Neon Dark', 'uses_primary': True, 'uses_secondary': True},
        'aurora': {'name': 'Aurora Borealis', 'uses_primary': True, 'uses_secondary': True},
        'brutalist': {'name': 'Brutalist', 'uses_primary': True, 'uses_secondary': False},
        'minimalist_white': {'name': 'Minimalist White', 'uses_primary': True, 'uses_secondary': False},
        'ocean_deep': {'name': 'Ocean Deep', 'uses_primary': True, 'uses_secondary': True},
        'cosmic': {'name': 'Cosmic', 'uses_primary': True, 'uses_secondary': True},
        'terrazzo': {'name': 'Terrazzo', 'uses_primary': True, 'uses_secondary': True},
        'modern_cards': {'name': 'Modern Cards', 'uses_primary': True, 'uses_secondary': True},
        'duotone': {'name': 'Duotone', 'uses_primary': True, 'uses_secondary': True},
        'morphing': {'name': 'Morphing', 'uses_primary': True, 'uses_secondary': True}
    }
    return theme_info.get(theme_id, {'name': theme_id, 'uses_primary': True, 'uses_secondary': True})

def generate_theme_css(theme_id: str, primary_color: str = '#667eea', secondary_color: str = '#f39c12') -> str:
    """Generate CSS for a specific theme"""
    # This is a simplified version - in production this would generate full theme CSS
    css_vars = generate_css_variables(primary_color, secondary_color)
    
    base_css = f"""
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
    """
    
    # Theme-specific additions
    theme_specific = {
        'default': """
        .stApp { background: linear-gradient(135deg, rgba(102,126,234,0.05) 0%, rgba(243,156,18,0.08) 100%); }
        """,
        'glassmorphism': """
        .stApp { background: rgba(255,255,255,0.1); backdrop-filter: blur(10px); }
        .metric-card { background: rgba(255,255,255,0.15) !important; backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.2); }
        """,
        'neon_dark': """
        .stApp { background: #0a0a0a; }
        .metric-card { background: #1a1a2e !important; border: 1px solid var(--primary); box-shadow: 0 0 20px rgba(102,126,234,0.1); }
        .metric-number { background: linear-gradient(135deg, #00ff87 0%, #60efff 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        """,
        'minimalist_white': """
        .stApp { background: #ffffff; }
        .metric-card { background: #f8f9fa !important; border: 1px solid #e9ecef; }
        """
    }
    
    return base_css + theme_specific.get(theme_id, '')

def get_reference_color_style(style: str) -> str:
    """Get CSS for reference color coding style"""
    styles = {
        'full': """
        .retracted-reference { background: #f8d7da !important; border-left: 4px solid #dc3545 !important; }
        .suspicious-reference { background: #fff3cd !important; border-left: 4px solid #ffc107 !important; }
        .duplicate-reference { background: #d1ecf1 !important; border-left: 4px solid #17a2b8 !important; }
        .ebook-reference { background: #d4f1e9 !important; border-left: 4px solid #0e6b5e !important; }
        .repository-reference { background: #e2d5f8 !important; border-left: 4px solid #5e2a9e !important; }
        .proceedings-reference { background: #fff2c9 !important; border-left: 4px solid #b26b00 !important; }
        .preprint-reference { background: #e8f4fd !important; border-left: 4px solid #2196f3 !important; }
        .notfound-reference { background: #f5f5f5 !important; border-left: 4px solid #999 !important; }
        .normal-article { background: #ffffff !important; border-left: 4px solid #28a745 !important; }
        """,
        'border_only': """
        .retracted-reference { border-left: 4px solid #dc3545 !important; }
        .suspicious-reference { border-left: 4px solid #ffc107 !important; }
        .duplicate-reference { border-left: 4px solid #17a2b8 !important; }
        .ebook-reference { border-left: 4px solid #0e6b5e !important; }
        .repository-reference { border-left: 4px solid #5e2a9e !important; }
        .proceedings-reference { border-left: 4px solid #b26b00 !important; }
        .preprint-reference { border-left: 4px solid #2196f3 !important; }
        .notfound-reference { border-left: 4px solid #999 !important; }
        .normal-article { border-left: 4px solid #28a745 !important; }
        """,
        'icons': """
        .retracted-reference::before { content: "⚠️ "; }
        .suspicious-reference::before { content: "❓ "; }
        .duplicate-reference::before { content: "🔄 "; }
        .ebook-reference::before { content: "📖 "; }
        .repository-reference::before { content: "📚 "; }
        .proceedings-reference::before { content: "📊 "; }
        .preprint-reference::before { content: "📄 "; }
        .notfound-reference::before { content: "❌ "; }
        .normal-article::before { content: "✅ "; }
        """,
        'themed': """
        .retracted-reference { border-left: 4px solid var(--primary) !important; }
        .suspicious-reference { border-left: 4px solid var(--secondary) !important; }
        .duplicate-reference { border-left: 4px solid var(--accent-1) !important; }
        .ebook-reference { border-left: 4px solid var(--accent-2) !important; }
        .repository-reference { border-left: 4px solid var(--primary) !important; }
        .proceedings-reference { border-left: 4px solid var(--secondary) !important; }
        .preprint-reference { border-left: 4px solid var(--accent-1) !important; }
        .notfound-reference { border-left: 4px solid #999 !important; }
        .normal-article { border-left: 4px solid var(--primary) !important; }
        """,
        'text': """
        .retracted-reference { color: #dc3545 !important; }
        .suspicious-reference { color: #856404 !important; }
        .duplicate-reference { color: #0c5460 !important; }
        .ebook-reference { color: #0e6b5e !important; }
        .repository-reference { color: #5e2a9e !important; }
        .proceedings-reference { color: #b26b00 !important; }
        .preprint-reference { color: #2196f3 !important; }
        .notfound-reference { color: #999 !important; }
        .normal-article { color: #28a745 !important; }
        """
    }
    return styles.get(style, styles['full'])

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

async def fetch_with_retry(session, url, params=None, headers=None, method='GET'):
    """Execute request with retries on error"""
    for attempt in range(MAX_RETRIES):
        try:
            async with session.request(method, url, params=params, headers=headers, timeout=TIMEOUT) as response:
                if response.status == 429:
                    retry_after = int(response.headers.get('Retry-After', RETRY_DELAY * (attempt + 1)))
                    if SHOW_DEBUG_LOGS:
                        print(f"⚠️ Rate limit, waiting {retry_after} sec...")
                    await asyncio.sleep(retry_after)
                    continue
                
                if response.status == 200:
                    return await response.json()
                else:
                    if SHOW_DEBUG_LOGS:
                        print(f"⚠️ Error {response.status} for {url}")
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
    """Get journal information from OpenAlex by ISSN"""
    issn_clean = parse_issn(issn)
    if not issn_clean:
        return None
    
    url = "https://api.openalex.org/sources"
    params = {
        'filter': f'issn:{issn_clean}',
        'per-page': 1
    }
    
    data = await fetch_with_retry(session, url, params=params)
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
    
    while True:
        data = await fetch_with_retry(session, url, params=params)
        
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
    """Get all citing works for a publication"""
    if not work_id:
        return []
    
    all_citations = []
    url = "https://api.openalex.org/works"
    params = {
        'filter': f'cites:{work_id}',
        'per-page': 200
    }
    
    page_count = 0
    
    while True:
        page_count += 1
        data = await fetch_with_retry(session, url, params=params)
        
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
    """Parse citation from OpenAlex data with publisher extraction"""
    try:
        citing_id = item.get('id', '')
        citing_doi = item.get('doi', '').replace('https://doi.org/', '')
        citing_title = item.get('title', 'No title')
        citing_year = item.get('publication_year', 0)
        citing_date = item.get('publication_date', '')
        
        citing_journal = ''
        citing_publisher = ''
        primary_location = item.get('primary_location', {})
        if primary_location:
            source = primary_location.get('source', {})
            citing_journal = source.get('display_name', '')
            # Extract publisher from host_organization_name or publisher field
            citing_publisher = source.get('host_organization_name', '') or source.get('publisher', '')
            
            # If not found in primary_location, try locations
            if not citing_publisher:
                for loc in item.get('locations', []):
                    src = loc.get('source', {})
                    if src.get('host_organization_name'):
                        citing_publisher = src['host_organization_name']
                        break
                    elif src.get('publisher'):
                        citing_publisher = src['publisher']
                        break
        
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
            citing_domains=list(set(citing_domains))
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
        """Get author statistics with collaboration patterns"""
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
        
        # Get top affiliations
        affiliation_counter = Counter()
        for pub in self.publications:
            for aff in pub.affiliations:
                if aff.get('name'):
                    affiliation_counter[aff['name']] += 1
        
        top_affiliations = [{'name': name, 'count': count} for name, count in affiliation_counter.most_common(20)]
        
        # Get country collaboration patterns
        country_patterns = defaultdict(int)
        for pub in self.publications:
            if pub.countries:
                unique_countries = sorted(set(pub.countries))
                if len(unique_countries) == 1:
                    pattern = unique_countries[0]
                    country_patterns[f"{pattern} - single"] += 1
                else:
                    pattern = '+'.join(unique_countries)
                    country_patterns[pattern] += 1
        
        collaboration_patterns = [{'pattern': k, 'count': v} for k, v in sorted(country_patterns.items(), key=lambda x: x[1], reverse=True)]
        
        # Get unique countries per reference (Type 1)
        unique_countries_per_ref = Counter()
        for pub in self.publications:
            for country in set(pub.countries):
                if country:
                    unique_countries_per_ref[country] += 1
        
        # Get authors per country (Type 2)
        authors_per_country = Counter()
        for pub in self.publications:
            for author in pub.authors:
                for country in author.countries:
                    if country:
                        authors_per_country[country] += 1
        
        # Get collaboration patterns (Type 3)
        single_country = 0
        international = 0
        for pub in self.publications:
            if pub.countries:
                if len(set(pub.countries)) == 1:
                    single_country += 1
                else:
                    international += 1
        
        # Get collaboration matrix
        country_pairs = Counter()
        for pub in self.publications:
            if len(pub.countries) > 1:
                sorted_countries = sorted(set(pub.countries))
                for i in range(len(sorted_countries)):
                    for j in range(i + 1, len(sorted_countries)):
                        pair = tuple(sorted([sorted_countries[i], sorted_countries[j]]))
                        country_pairs[pair] += 1
        
        collaboration_matrix = [{'country1': c1, 'country2': c2, 'count': v} for (c1, c2), v in country_pairs.most_common(20)]
        
        return {
            'total_authors': len(author_list),
            'top_authors': author_list[:20],
            'all_authors': author_list,
            'top_affiliations': top_affiliations,
            'collaboration_patterns': collaboration_patterns,
            'unique_countries_per_reference': dict(unique_countries_per_ref.most_common()),
            'authors_per_country': dict(authors_per_country.most_common()),
            'single_country_count': single_country,
            'international_count': international,
            'collaboration_matrix': collaboration_matrix
        }
    
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
            'domains': domain_list[:20],
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
        """Get detailed statistics about citing works with full analytics"""
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
                'citation_years': {},
                'unique_journals': 0,
                'unique_publishers': 0,
                'unique_authors': 0,
                'unique_countries': 0,
                'unique_affiliations': 0,
                'top_citing_affiliations': [],
                'unique_countries_per_citing_work': {},
                'authors_per_country_citing': {},
                'single_country_citing': 0,
                'international_citing': 0,
                'collaboration_matrix_citing': []
            }
        
        journal_counts = Counter()
        publisher_counts = Counter()
        author_counts = Counter()
        country_counts = Counter()
        aff_counts = Counter()
        
        # Track collaboration patterns for citing works
        citing_country_patterns = defaultdict(int)
        citing_country_pairs = Counter()
        citing_single_country = 0
        citing_international = 0
        
        # Track unique countries per citing work
        unique_countries_per_citing = Counter()
        authors_per_country_citing = Counter()
        
        for cite in all_citations:
            if cite.citing_journal:
                journal_counts[cite.citing_journal] += 1
            if cite.citing_publisher:
                publisher_counts[cite.citing_publisher] += 1
            
            for author in cite.citing_authors:
                if author.display_name:
                    author_counts[author.display_name] += 1
            
            for country in cite.citing_countries:
                if country:
                    country_counts[country] += 1
                    authors_per_country_citing[country] += 1
            
            for aff in cite.citing_affiliations:
                if aff.get('name'):
                    aff_counts[aff['name']] += 1
            
            # Collaboration patterns for citing works
            citing_countries_list = list(set(cite.citing_countries))
            if citing_countries_list:
                for country in citing_countries_list:
                    unique_countries_per_citing[country] += 1
                
                if len(citing_countries_list) == 1:
                    citing_single_country += 1
                    pattern = citing_countries_list[0]
                    citing_country_patterns[f"{pattern} - single"] += 1
                else:
                    citing_international += 1
                    sorted_countries = sorted(citing_countries_list)
                    pattern = '+'.join(sorted_countries)
                    citing_country_patterns[pattern] += 1
                    
                    for i in range(len(sorted_countries)):
                        for j in range(i + 1, len(sorted_countries)):
                            pair = tuple(sorted([sorted_countries[i], sorted_countries[j]]))
                            citing_country_pairs[pair] += 1
        
        citation_years = Counter()
        for c in all_citations:
            if c.citing_year > 0:
                citation_years[c.citing_year] += 1
        
        collaboration_matrix_citing = [{'country1': c1, 'country2': c2, 'count': v} for (c1, c2), v in citing_country_pairs.most_common(20)]
        
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
            'top_citing_affiliations': [{'name': k, 'count': v} for k, v in aff_counts.most_common(20)],
            'citation_years': dict(citation_years),
            'all_citations': all_citations,
            'unique_countries_per_citing_work': dict(unique_countries_per_citing.most_common()),
            'authors_per_country_citing': dict(authors_per_country_citing.most_common()),
            'single_country_citing': citing_single_country,
            'international_citing': citing_international,
            'collaboration_matrix_citing': collaboration_matrix_citing,
            'citing_country_patterns': dict(citing_country_patterns)
        }
    
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
    
    def _get_citation_matrix(self) -> Dict:
        """Get citation matrix: publication_year vs citation_year"""
        matrix = defaultdict(lambda: defaultdict(int))
        
        for pub in self.publications:
            pub_year = pub.publication_year
            if pub_year == 0:
                continue
            
            for cite in self.citations.get(pub.id, []):
                if cite.citing_year > 0:
                    matrix[pub_year][cite.citing_year] += 1
        
        # Convert to sorted dict
        result = {}
        for pub_year in sorted(matrix.keys()):
            result[pub_year] = dict(sorted(matrix[pub_year].items()))
        
        return result
    
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
                        'ratio': ratio
                    }
        
        # Sort by ratio descending
        sorted_hot_topics = dict(sorted(hot_topics.items(), key=lambda x: x[1]['ratio'], reverse=True))
        
        return {
            'publication_topics': dict(pub_topics.most_common(30)),
            'citing_topics': dict(citing_topics.most_common(30)),
            'overlap_topics': list(overlap),
            'overlap_percentage': (len(overlap) / max(len(pub_topic_set), 1) * 100) if pub_topic_set else 0,
            'hot_topics': sorted_hot_topics,
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
                        'citing_authors': [a.display_name for a in cite.citing_authors],
                        'citing_countries': cite.citing_countries,
                        'citing_topics': [t.display_name for t in cite.citing_topics[:3]]
                    })
                
                detailed[pub.id] = {
                    'title': pub.title,
                    'year': pub.publication_year,
                    'doi': pub.doi,
                    'total_citations': len(citations_list),
                    'authors': [a.display_name for a in pub.authors],
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
    
    author_stats = analytics.get('author_stats', {})
    top_authors = author_stats.get('top_authors', [])
    if top_authors:
        fig, ax = plt.subplots(figsize=(10, 5))
        
        names = [a['display_name'][:20] for a in top_authors[:10]]
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
    
    hot_topics = analytics.get('topic_relationship', {}).get('hot_topics', {})
    if hot_topics:
        fig, ax = plt.subplots(figsize=(10, 6))
        
        names = []
        sizes = []
        ratios = []
        
        for topic, data in list(hot_topics.items())[:10]:
            names.append(topic[:20])
            sizes.append(data['citations'])
            ratios.append(data['ratio'])
        
        if names:
            max_ratio = max(ratios) if ratios else 1
            colors = plt.cm.RdYlGn(np.array(ratios) / max_ratio)
            
            scatter = ax.scatter(range(len(names)), sizes, s=[s * 2 for s in sizes], 
                               c=colors, alpha=0.6, edgecolors='black', linewidth=1)
            
            ax.set_xticks(range(len(names)))
            ax.set_xticklabels(names, rotation=45, ha='right', fontsize=9)
            ax.set_ylabel('Citations', fontsize=11, fontweight='bold')
            ax.set_xlabel('Topics', fontsize=11, fontweight='bold')
            ax.set_title('Hot Topics (Citation Impact)', fontsize=12, fontweight='bold')
            ax.grid(True, alpha=0.3, linestyle='--')
            
            plt.tight_layout()
            
            buf = BytesIO()
            plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
            buf.seek(0)
            images['hot_topics'] = base64.b64encode(buf.getvalue()).decode()
            plt.close()
    
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
    
    top_citing_countries = citing_stats.get('top_countries', [])
    if top_citing_countries:
        fig, ax = plt.subplots(figsize=(10, 5))
        
        names = [c['name'][:20] for c in top_citing_countries[:10]]
        counts = [c['count'] for c in top_citing_countries[:10]]
        
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
    
    return images

# ============================================
# ENHANCED HTML REPORT GENERATOR
# ============================================

def generate_enhanced_html_report(journal: Journal, analytics: Dict, periods: List[Tuple[int, int]], 
                                   images: Dict[str, str], theme_colors: Dict, lang: str = 'en',
                                   all_publications: List[Publication] = None, design_theme: str = 'default',
                                   reference_color_style: str = 'full') -> str:
    """Generate enhanced HTML report with all features and navigation"""
    
    def t(key: str, **kwargs) -> str:
        return translate(key, lang, **kwargs)
    
    primary = theme_colors.get('primary', '#667eea')
    secondary = theme_colors.get('secondary', '#f39c12')
    
    # Generate theme CSS
    theme_css = generate_theme_css(design_theme, primary, secondary)
    ref_colors_css = get_reference_color_style(reference_color_style)
    
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
    citation_matrix = analytics.get('citation_matrix', {})
    
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Journal Analytics - {journal.title}</title>
    <style>
        {theme_css}
        {ref_colors_css}
        
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Times New Roman', 'DejaVu Serif', serif;
            margin: 0;
            padding: 0;
            background: #f5f7fa;
            color: #333;
        }}
        .report-wrapper {{
            display: flex;
            min-height: 100vh;
        }}
        
        /* ===== SIDEBAR NAVIGATION ===== */
        .sidebar {{
            width: 280px;
            min-width: 280px;
            background: linear-gradient(180deg, var(--primary) 0%, var(--secondary) 100%);
            color: white;
            padding: 20px 15px;
            position: sticky;
            top: 0;
            height: 100vh;
            overflow-y: auto;
            flex-shrink: 0;
            z-index: 100;
        }}
        .sidebar::-webkit-scrollbar {{ width: 5px; }}
        .sidebar::-webkit-scrollbar-thumb {{ background: rgba(255,255,255,0.3); border-radius: 10px; }}
        .sidebar::-webkit-scrollbar-track {{ background: transparent; }}
        
        .sidebar-brand {{
            text-align: center;
            padding-bottom: 20px;
            border-bottom: 1px solid rgba(255,255,255,0.2);
            margin-bottom: 20px;
        }}
        .sidebar-brand h2 {{
            font-size: 18px;
            font-weight: 600;
            color: white;
            margin: 0;
        }}
        .sidebar-brand .sub {{
            font-size: 11px;
            opacity: 0.8;
            margin-top: 5px;
        }}
        
        .sidebar-nav {{
            display: flex;
            flex-direction: column;
            gap: 3px;
        }}
        .sidebar-nav a {{
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 8px 12px;
            border-radius: 8px;
            color: rgba(255,255,255,0.85);
            text-decoration: none;
            font-size: 13px;
            transition: all 0.3s;
            border-left: 2px solid transparent;
        }}
        .sidebar-nav a:hover {{
            background: rgba(255,255,255,0.15);
            color: white;
            border-left-color: white;
        }}
        .sidebar-nav a.active {{
            background: rgba(255,255,255,0.2);
            color: white;
            border-left-color: white;
        }}
        .sidebar-nav .nav-icon {{
            font-size: 16px;
            width: 24px;
            text-align: center;
            flex-shrink: 0;
        }}
        .sidebar-nav .nav-label {{
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
        .sidebar-nav .nav-section {{
            font-size: 10px;
            text-transform: uppercase;
            letter-spacing: 1px;
            opacity: 0.5;
            padding: 12px 12px 4px;
            font-weight: 600;
        }}
        
        /* ===== MAIN CONTENT ===== */
        .main-content {{
            flex: 1;
            padding: 30px 40px 40px;
            max-width: calc(100% - 280px);
            background: white;
            min-height: 100vh;
        }}
        
        .header {{
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
            color: white;
            padding: 30px 40px;
            border-radius: 12px;
            margin-bottom: 30px;
        }}
        .header h1 {{
            color: white;
            font-size: 28px;
            margin: 0;
        }}
        .header .subtitle {{
            opacity: 0.9;
            margin-top: 8px;
            font-size: 15px;
        }}
        .header .meta {{
            opacity: 0.8;
            margin-top: 6px;
            font-size: 13px;
        }}
        
        .section {{
            background: white;
            border-radius: 12px;
            padding: 25px;
            margin-bottom: 25px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            border: 1px solid #eef2f7;
            scroll-margin-top: 20px;
        }}
        .section-title {{
            font-size: 22px;
            font-weight: 600;
            margin-bottom: 20px;
            padding-bottom: 12px;
            border-bottom: 3px solid var(--primary);
            color: var(--primary);
        }}
        .section-title .icon {{
            margin-right: 10px;
        }}
        
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
            gap: 12px;
            margin: 15px 0;
        }}
        .metric-card {{
            background: #f8f9fa;
            padding: 14px 12px;
            border-radius: 8px;
            border-left: 4px solid var(--primary);
            text-align: center;
            transition: transform 0.3s;
        }}
        .metric-card:hover {{
            transform: translateY(-3px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.08);
        }}
        .metric-value {{
            font-size: 26px;
            font-weight: bold;
            color: var(--primary);
        }}
        .metric-label {{
            font-size: 11px;
            color: #7F8C8D;
            margin-top: 4px;
        }}
        
        .chart-container {{
            margin: 15px 0;
            text-align: center;
        }}
        .chart-container img {{
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }}
        
        .two-column {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
        .three-column {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px; }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 12px 0;
            font-size: 13px;
        }}
        th {{
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
            color: white;
            padding: 10px 12px;
            text-align: left;
            font-weight: 600;
        }}
        td {{
            padding: 8px 12px;
            border-bottom: 1px solid #eef2f7;
        }}
        tr:hover {{ background-color: #f8f9fa; }}
        
        .doi-link {{
            color: var(--primary);
            text-decoration: none;
            font-size: 12px;
        }}
        .doi-link:hover {{ text-decoration: underline; }}
        
        .rank-item {{
            border-radius: 8px;
            padding: 10px 14px;
            margin-bottom: 6px;
            transition: all 0.3s;
            background: #f8f9fa;
            border-left: 3px solid var(--primary);
        }}
        .rank-item:hover {{
            transform: translateX(4px);
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        }}
        .rank-number {{
            font-weight: bold;
            color: var(--primary);
            font-size: 16px;
            display: inline-block;
            width: 36px;
        }}
        .rank-name {{
            display: inline-block;
            font-weight: 500;
        }}
        .rank-count {{
            float: right;
            color: #666;
            font-size: 13px;
        }}
        
        .progress-bar {{
            background: #e9ecef;
            border-radius: 10px;
            height: 6px;
            margin-top: 6px;
            overflow: hidden;
        }}
        .progress-fill {{
            background: linear-gradient(90deg, var(--primary), var(--secondary));
            height: 100%;
            border-radius: 10px;
            transition: width 0.5s;
        }}
        
        .badge {{
            display: inline-block;
            padding: 2px 10px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 600;
            margin: 2px;
        }}
        .badge-success {{ background: #d4edda; color: #155724; }}
        .badge-warning {{ background: #fff3cd; color: #856404; }}
        .badge-info {{ background: #d1ecf1; color: #0c5460; }}
        .badge-danger {{ background: #f8d7da; color: #721c24; }}
        
        .collapser {{
            cursor: pointer;
            padding: 10px 15px;
            background: #f8f9fa;
            border: 1px solid #ddd;
            border-radius: 8px;
            margin: 5px 0;
            transition: background 0.3s;
        }}
        .collapser:hover {{ background: #e9ecef; }}
        .collapser-content {{
            padding: 10px 15px;
            border: 1px solid #ddd;
            border-top: none;
            border-radius: 0 0 8px 8px;
            margin-bottom: 10px;
        }}
        
        .citation-detail {{
            background: #f8f9fa;
            padding: 10px 14px;
            margin: 4px 0;
            border-radius: 5px;
            border-left: 3px solid var(--primary);
        }}
        .citation-detail .cite-meta {{
            font-size: 12px;
            color: #666;
            margin-top: 3px;
        }}
        
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #eef2f7;
            text-align: center;
            color: #7F8C8D;
            font-size: 12px;
        }}
        .footer a {{
            color: var(--primary);
            text-decoration: none;
        }}
        .footer a:hover {{ text-decoration: underline; }}
        
        @media (max-width: 768px) {{
            .report-wrapper {{ flex-direction: column; }}
            .sidebar {{
                width: 100%;
                min-width: unset;
                height: auto;
                position: relative;
                padding: 15px;
            }}
            .main-content {{
                max-width: 100%;
                padding: 20px;
            }}
            .two-column, .three-column {{ grid-template-columns: 1fr; }}
            .metrics-grid {{ grid-template-columns: repeat(auto-fit, minmax(100px, 1fr)); }}
            .header {{ padding: 20px; }}
        }}
        
        .citation-count {{
            display: inline-block;
            padding: 1px 10px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            background: var(--primary)20;
            color: var(--primary);
        }}
        
        .full-text {{
            word-wrap: break-word;
            overflow-wrap: break-word;
            white-space: normal;
        }}
        
        .matrix-table td, .matrix-table th {{
            text-align: center;
            padding: 6px 10px;
            font-size: 12px;
        }}
        .matrix-table .highlight {{
            background: var(--primary)15;
            font-weight: 600;
        }}
    </style>
</head>
<body>
<div class="report-wrapper">
    
    <!-- ===== SIDEBAR NAVIGATION ===== -->
    <nav class="sidebar">
        <div class="sidebar-brand">
            <h2>📊 Journal Analytics</h2>
            <div class="sub">{journal.title}</div>
        </div>
        <div class="sidebar-nav">
            <div class="nav-section">Overview</div>
            <a href="#executive-summary"><span class="nav-icon">📊</span><span class="nav-label">{t('nav_executive_summary')}</span></a>
            
            <div class="nav-section">Journal Publications</div>
            <a href="#publication-dynamics"><span class="nav-icon">📈</span><span class="nav-label">{t('nav_publication_dynamics')}</span></a>
            <a href="#most-cited"><span class="nav-icon">🏆</span><span class="nav-label">{t('nav_most_cited')}</span></a>
            <a href="#author-analysis"><span class="nav-icon">👨‍🎓</span><span class="nav-label">{t('nav_author_analysis')}</span></a>
            <a href="#affiliation-analysis"><span class="nav-icon">🏛️</span><span class="nav-label">{t('nav_affiliation_analysis')}</span></a>
            <a href="#citation-analysis"><span class="nav-icon">📊</span><span class="nav-label">{t('nav_citation_analysis')}</span></a>
            <a href="#citation-matrix"><span class="nav-icon">📊</span><span class="nav-label">{t('nav_citation_matrix')}</span></a>
            <a href="#topic-analysis"><span class="nav-icon">🏷️</span><span class="nav-label">{t('nav_topic_analysis')}</span></a>
            
            <div class="nav-section">Citing Works</div>
            <a href="#citing-works"><span class="nav-icon">📚</span><span class="nav-label">{t('nav_citing_works')}</span></a>
            <a href="#citing-distribution"><span class="nav-icon">📊</span><span class="nav-label">{t('nav_citing_distribution')}</span></a>
            
            <div class="nav-section">Relationships</div>
            <a href="#topic-relationship"><span class="nav-icon">🔄</span><span class="nav-label">{t('nav_topic_relationship')}</span></a>
            
            <div class="nav-section">Details</div>
            <a href="#detailed-citations"><span class="nav-icon">📋</span><span class="nav-label">{t('nav_detailed_citations')}</span></a>
            <a href="#all-publications"><span class="nav-icon">📚</span><span class="nav-label">{t('nav_all_publications')}</span></a>
        </div>
    </nav>
    
    <!-- ===== MAIN CONTENT ===== -->
    <div class="main-content">
        
        <!-- HEADER -->
        <div class="header">
            <h1>📊 Journal Analytics Report</h1>
            <div class="subtitle">{journal.title}</div>
            <div class="meta">ISSN: {journal.issn} | Publisher: {journal.publisher} | Period: {period_display}</div>
            <div class="meta">Generated: {datetime.now().strftime('%d.%m.%Y')}</div>
        </div>
        
        <!-- ===== EXECUTIVE SUMMARY ===== -->
        <div id="executive-summary" class="section">
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
                    <div class="metric-value">{citing_stats.get('unique_publishers', 0)}</div>
                    <div class="metric-label">{t('unique_citing_publishers')}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{citing_stats.get('unique_countries', 0)}</div>
                    <div class="metric-label">{t('unique_citing_countries')}</div>
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
        
        <!-- ===== PUBLICATION DYNAMICS ===== -->
        <div id="publication-dynamics" class="section">
            <div class="section-title"><span class="icon">📈</span> {t('publication_dynamics')}</div>
            <div class="chart-container">
                <img src="data:image/png;base64,{images.get('publication_dynamics', '')}" alt="{t('publication_dynamics')}">
            </div>
        </div>
        
        <!-- ===== MOST CITED PUBLICATIONS ===== -->
        <div id="most-cited" class="section">
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
                        f'<td class="full-text">{html.escape(pub["title"])}</td>'
                        f'<td>{pub["year"]}</td>'
                        f'<td><span class="citation-count">{pub["citations"]}</span></td>'
                        f'<td>{pub.get("citations_per_year", 0):.1f}</td>'
                        f'<td>{", ".join(pub["authors"])}</td>'
                        f'<td><a href="https://doi.org/{pub["doi"]}" target="_blank" class="doi-link">{pub["doi"]}</a></td>'
                        f'</tr>'
                        for i, pub in enumerate(most_cited)
                    ])}
                </tbody>
            </table>
        </div>
        
        <!-- ===== AUTHOR ANALYSIS ===== -->
        <div id="author-analysis" class="section">
            <div class="section-title"><span class="icon">👨‍🎓</span> {t('author_analysis')}</div>
            
            <div class="two-column">
                <div>
                    <h4>Top Authors by Publications</h4>
                    {''.join([
                        f'<div class="rank-item">'
                        f'<span class="rank-number">{i+1}</span>'
                        f'<span class="rank-name">{html.escape(a["display_name"])}</span>'
                        f'<span class="rank-count">{a["publications"]} pubs</span>'
                        f'<div class="progress-bar"><div class="progress-fill" style="width: {a["publications"]/max([a["publications"] for a in author_stats.get("top_authors", [])])*100 if author_stats.get("top_authors") else 0}%;"></div></div>'
                        f'<div style="font-size: 11px; color: #666;">h-index: {a["h_index"]} | Citations: {a["citations"]}</div>'
                        f'</div>'
                        for i, a in enumerate(author_stats.get("top_authors", [])[:10])
                    ])}
                </div>
                <div>
                    <h4>Top Countries</h4>
                    {''.join([
                        f'<div class="rank-item">'
                        f'<span class="rank-number">{i+1}</span>'
                        f'<span class="rank-name">{html.escape(c["country"])}</span>'
                        f'<span class="rank-count">{c["publications"]} pubs</span>'
                        f'<div class="progress-bar"><div class="progress-fill" style="width: {c["publications"]/max([c["publications"] for c in country_stats.get("top_countries", [])])*100 if country_stats.get("top_countries") else 0}%;"></div></div>'
                        f'</div>'
                        for i, c in enumerate(country_stats.get("top_countries", [])[:10])
                    ])}
                </div>
            </div>
            
            <div style="margin-top: 20px;">
                <h4>Top Affiliations</h4>
                {''.join([
                    f'<div class="rank-item">'
                    f'<span class="rank-number">{i+1}</span>'
                    f'<span class="rank-name">{html.escape(a["name"][:60])}</span>'
                    f'<span class="rank-count">{a["count"]} pubs</span>'
                    f'<div class="progress-bar"><div class="progress-fill" style="width: {a["count"]/max([a["count"] for a in author_stats.get("top_affiliations", [])])*100 if author_stats.get("top_affiliations") else 0}%;"></div></div>'
                    f'</div>'
                    for i, a in enumerate(author_stats.get("top_affiliations", [])[:10])
                ])}
            </div>
            
            <div style="margin-top: 20px;">
                <h4>Collaboration Patterns</h4>
                <div class="two-column">
                    <div>
                        <h5>Unique Countries per Reference</h5>
                        {''.join([
                            f'<div class="rank-item">'
                            f'<span class="rank-name">{html.escape(c)}</span>'
                            f'<span class="rank-count">{count} refs</span>'
                            f'<div class="progress-bar"><div class="progress-fill" style="width: {count/max(author_stats.get("unique_countries_per_reference", {}).values())*100 if author_stats.get("unique_countries_per_reference") else 0}%;"></div></div>'
                            f'</div>'
                            for c, count in list(author_stats.get("unique_countries_per_reference", {}).items())[:10]
                        ])}
                    </div>
                    <div>
                        <h5>Authors per Country</h5>
                        {''.join([
                            f'<div class="rank-item">'
                            f'<span class="rank-name">{html.escape(c)}</span>'
                            f'<span class="rank-count">{count} authors</span>'
                            f'<div class="progress-bar"><div class="progress-fill" style="width: {count/max(author_stats.get("authors_per_country", {}).values())*100 if author_stats.get("authors_per_country") else 0}%;"></div></div>'
                            f'</div>'
                            for c, count in list(author_stats.get("authors_per_country", {}).items())[:10]
                        ])}
                    </div>
                </div>
                
                <div style="margin-top: 15px;">
                    <h5>Collaboration Matrix</h5>
                    <div class="two-column">
                        <div>
                            <span class="badge badge-info">Single country: {author_stats.get("single_country_count", 0)}</span>
                            <span class="badge badge-success">International: {author_stats.get("international_count", 0)}</span>
                        </div>
                    </div>
                    {''.join([
                        f'<div class="rank-item">'
                        f'<span class="rank-name">{html.escape(m["country1"])} + {html.escape(m["country2"])}</span>'
                        f'<span class="rank-count">{m["count"]} refs</span>'
                        f'<div class="progress-bar"><div class="progress-fill" style="width: {m["count"]/max([m["count"] for m in author_stats.get("collaboration_matrix", [])])*100 if author_stats.get("collaboration_matrix") else 0}%;"></div></div>'
                        f'</div>'
                        for m in author_stats.get("collaboration_matrix", [])[:10]
                    ])}
                </div>
            </div>
        </div>
        
        <!-- ===== AFFILIATION ANALYSIS ===== -->
        <div id="affiliation-analysis" class="section">
            <div class="section-title"><span class="icon">🏛️</span> {t('affiliation_analysis')}</div>
            <table>
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Affiliation</th>
                        <th>Country</th>
                        <th>Publications</th>
                        <th>Citations</th>
                        <th>Unique Authors</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join([
                        f'<tr>'
                        f'<td>{i+1}</td>'
                        f'<td class="full-text">{html.escape(a["name"])}</td>'
                        f'<td>{html.escape(a.get("country", ""))}</td>'
                        f'<td>{a["publications"]}</td>'
                        f'<td>{a["citations"]}</td>'
                        f'<td>{a["authors_count"]}</td>'
                        f'</tr>'
                        for i, a in enumerate(analytics.get("affiliation_stats", {}).get("top_affiliations", [])[:20])
                    ])}
                </tbody>
            </table>
        </div>
        
        <!-- ===== CITATION ANALYSIS ===== -->
        <div id="citation-analysis" class="section">
            <div class="section-title"><span class="icon">📊</span> {t('citation_analysis')}</div>
            <div class="metrics-grid" style="grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));">
                <div class="metric-card">
                    <div class="metric-value">{cit_stats.get('total', 0):,}</div>
                    <div class="metric-label">{t('total_citations')}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{cit_stats.get('avg', 0):.1f}</div>
                    <div class="metric-label">{t('avg_citations')}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{cit_stats.get('median', 0):.1f}</div>
                    <div class="metric-label">{t('median_citations')}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{cit_stats.get('max', 0)}</div>
                    <div class="metric-label">{t('max_citations')}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{cit_stats.get('h_index', 0)}</div>
                    <div class="metric-label">{t('h_index')}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{cit_stats.get('g_index', 0)}</div>
                    <div class="metric-label">{t('g_index')}</div>
                </div>
            </div>
            <div class="chart-container">
                <img src="data:image/png;base64,{images.get('citation_distribution', '')}" alt="{t('citation_analysis')}">
            </div>
        </div>
        
        <!-- ===== CITATION MATRIX ===== -->
        <div id="citation-matrix" class="section">
            <div class="section-title"><span class="icon">📊</span> {t('citation_matrix')}</div>
            <p style="margin-bottom: 12px; color: #666; font-size: 13px;">
                Matrix showing how many articles published in each year (rows) were cited in subsequent years (columns).
            </p>
            
            {f'''
            <div style="overflow-x: auto;">
                <table class="matrix-table">
                    <thead>
                        <tr>
                            <th>{t('publication_year')} ↓ / {t('citation_year')} →</th>
                            {''.join([f'<th>{year}</th>' for year in sorted(citation_matrix.keys())])}
                            <th>Total</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join([
                            f'<tr>'
                            f'<td><strong>{pub_year}</strong></td>'
                            + ''.join([
                                f'<td>{citation_matrix.get(pub_year, {}).get(cite_year, 0)}</td>'
                                for cite_year in sorted(citation_matrix.keys())
                            ])
                            + f'<td><strong>{sum(citation_matrix.get(pub_year, {}).values())}</strong></td>'
                            f'</tr>'
                            for pub_year in sorted(citation_matrix.keys())
                        ])}
                    </tbody>
                </table>
            </div>
            ''' if citation_matrix else '<p>No citation matrix data available.</p>'}
        </div>
        
        <!-- ===== TOPIC ANALYSIS ===== -->
        <div id="topic-analysis" class="section">
            <div class="section-title"><span class="icon">🏷️</span> {t('topic_analysis')}</div>
            
            <div class="two-column">
                <div>
                    <h4>Top Topics</h4>
                    {''.join([
                        f'<div class="rank-item">'
                        f'<span class="rank-number">{i+1}</span>'
                        f'<span class="rank-name">{html.escape(t["name"][:40])}</span>'
                        f'<span class="rank-count">{t["publications"]} pubs</span>'
                        f'<div class="progress-bar"><div class="progress-fill" style="width: {t["publications"]/max([t["publications"] for t in topic_stats.get("topics", [])])*100 if topic_stats.get("topics") else 0}%;"></div></div>'
                        f'</div>'
                        for i, t in enumerate(topic_stats.get("topics", [])[:10])
                    ])}
                </div>
                <div>
                    <h4>Top Fields</h4>
                    {''.join([
                        f'<div class="rank-item">'
                        f'<span class="rank-number">{i+1}</span>'
                        f'<span class="rank-name">{html.escape(f["name"][:40])}</span>'
                        f'<span class="rank-count">{f["publications"]} pubs</span>'
                        f'<div class="progress-bar"><div class="progress-fill" style="width: {f["publications"]/max([f["publications"] for f in topic_stats.get("fields", [])])*100 if topic_stats.get("fields") else 0}%;"></div></div>'
                        f'</div>'
                        for i, f in enumerate(topic_stats.get("fields", [])[:10])
                    ])}
                </div>
            </div>
            
            <div style="margin-top: 20px;">
                <h4>Top Domains</h4>
                {''.join([
                    f'<div class="rank-item">'
                    f'<span class="rank-number">{i+1}</span>'
                    f'<span class="rank-name">{html.escape(d["name"][:40])}</span>'
                    f'<span class="rank-count">{d["publications"]} pubs</span>'
                    f'<div class="progress-bar"><div class="progress-fill" style="width: {d["publications"]/max([d["publications"] for d in topic_stats.get("domains", [])])*100 if topic_stats.get("domains") else 0}%;"></div></div>'
                    f'</div>'
                    for i, d in enumerate(topic_stats.get("domains", [])[:10])
                ])}
            </div>
            
            <div style="margin-top: 20px;">
                <h4>Top Concepts</h4>
                {''.join([
                    f'<div class="rank-item">'
                    f'<span class="rank-number">{i+1}</span>'
                    f'<span class="rank-name">{html.escape(c["name"][:40])}</span>'
                    f'<span class="rank-count">{c["publications"]} pubs</span>'
                    f'<div class="progress-bar"><div class="progress-fill" style="width: {c["publications"]/max([c["publications"] for c in topic_stats.get("concepts", [])])*100 if topic_stats.get("concepts") else 0}%;"></div></div>'
                    f'</div>'
                    for i, c in enumerate(topic_stats.get("concepts", [])[:15])
                ])}
            </div>
        </div>
        
        <!-- ===== CITING WORKS ANALYSIS ===== -->
        <div id="citing-works" class="section">
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
                    <div class="metric-value">{citing_stats.get("unique_authors", 0)}</div>
                    <div class="metric-label">{t('unique_citing_authors')}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{citing_stats.get("unique_countries", 0)}</div>
                    <div class="metric-label">{t('unique_citing_countries')}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{citing_stats.get("unique_affiliations", 0)}</div>
                    <div class="metric-label">{t('unique_citing_affiliations')}</div>
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
                        for i, j in enumerate(citing_stats.get("top_journals", [])[:10])
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
                        for i, p in enumerate(citing_stats.get("top_publishers", [])[:10])
                    ])}
                </div>
            </div>
            
            <div class="two-column">
                <div>
                    <h4>{t('top_citing_authors')}</h4>
                    {''.join([
                        f'<div class="rank-item">'
                        f'<span class="rank-number">{i+1}</span>'
                        f'<span class="rank-name">{html.escape(a["name"][:40])}</span>'
                        f'<span class="rank-count">{a["count"]}</span>'
                        f'<div class="progress-bar"><div class="progress-fill" style="width: {a["count"]/max([a["count"] for a in citing_stats.get("top_authors", [])])*100 if citing_stats.get("top_authors") else 0}%;"></div></div>'
                        f'</div>'
                        for i, a in enumerate(citing_stats.get("top_authors", [])[:10])
                    ])}
                </div>
                <div>
                    <h4>{t('top_citing_affiliations')}</h4>
                    {''.join([
                        f'<div class="rank-item">'
                        f'<span class="rank-number">{i+1}</span>'
                        f'<span class="rank-name">{html.escape(a["name"][:40])}</span>'
                        f'<span class="rank-count">{a["count"]}</span>'
                        f'<div class="progress-bar"><div class="progress-fill" style="width: {a["count"]/max([a["count"] for a in citing_stats.get("top_citing_affiliations", [])])*100 if citing_stats.get("top_citing_affiliations") else 0}%;"></div></div>'
                        f'</div>'
                        for i, a in enumerate(citing_stats.get("top_citing_affiliations", [])[:10])
                    ])}
                </div>
            </div>
            
            <div style="margin-top: 20px;">
                <h4>{t('top_citing_countries')}</h4>
                <div class="two-column">
                    <div>
                        <h5>{t('unique_countries_per_citing_work')}</h5>
                        {''.join([
                            f'<div class="rank-item">'
                            f'<span class="rank-name">{html.escape(c)}</span>'
                            f'<span class="rank-count">{count}</span>'
                            f'<div class="progress-bar"><div class="progress-fill" style="width: {count/max(citing_stats.get("unique_countries_per_citing_work", {}).values())*100 if citing_stats.get("unique_countries_per_citing_work") else 0}%;"></div></div>'
                            f'</div>'
                            for c, count in list(citing_stats.get("unique_countries_per_citing_work", {}).items())[:10]
                        ])}
                    </div>
                    <div>
                        <h5>{t('authors_per_country_citing')}</h5>
                        {''.join([
                            f'<div class="rank-item">'
                            f'<span class="rank-name">{html.escape(c)}</span>'
                            f'<span class="rank-count">{count}</span>'
                            f'<div class="progress-bar"><div class="progress-fill" style="width: {count/max(citing_stats.get("authors_per_country_citing", {}).values())*100 if citing_stats.get("authors_per_country_citing") else 0}%;"></div></div>'
                            f'</div>'
                            for c, count in list(citing_stats.get("authors_per_country_citing", {}).items())[:10]
                        ])}
                    </div>
                </div>
                
                <div style="margin-top: 15px;">
                    <h5>{t('collaboration_patterns_citing')}</h5>
                    <div>
                        <span class="badge badge-info">Single country: {citing_stats.get("single_country_citing", 0)}</span>
                        <span class="badge badge-success">International: {citing_stats.get("international_citing", 0)}</span>
                    </div>
                    {''.join([
                        f'<div class="rank-item">'
                        f'<span class="rank-name">{html.escape(m["country1"])} + {html.escape(m["country2"])}</span>'
                        f'<span class="rank-count">{m["count"]}</span>'
                        f'<div class="progress-bar"><div class="progress-fill" style="width: {m["count"]/max([m["count"] for m in citing_stats.get("collaboration_matrix_citing", [])])*100 if citing_stats.get("collaboration_matrix_citing") else 0}%;"></div></div>'
                        f'</div>'
                        for m in citing_stats.get("collaboration_matrix_citing", [])[:10]
                    ])}
                </div>
            </div>
        </div>
        
        <!-- ===== CITING WORKS DISTRIBUTION ===== -->
        <div id="citing-distribution" class="section">
            <div class="section-title"><span class="icon">📊</span> {t('citing_works_distribution')}</div>
            <div class="two-column">
                <div class="chart-container">
                    <img src="data:image/png;base64,{images.get('top_citing_journals', '')}" alt="{t('top_citing_journals')}">
                </div>
                <div class="chart-container">
                    <img src="data:image/png;base64,{images.get('top_citing_countries', '')}" alt="{t('top_citing_countries')}">
                </div>
            </div>
        </div>
        
        <!-- ===== TOPIC RELATIONSHIP ===== -->
        <div id="topic-relationship" class="section">
            <div class="section-title"><span class="icon">🔄</span> {t('topic_relationship')}</div>
            
            <div class="metrics-grid" style="grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));">
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
                    <h4>Publication Topics</h4>
                    {''.join([
                        f'<div class="rank-item">'
                        f'<span class="rank-name">{html.escape(topic[:40])}</span>'
                        f'<span class="rank-count">{count}</span>'
                        f'<div class="progress-bar"><div class="progress-fill" style="width: {count/max(topic_rel.get("publication_topics", {}).values())*100 if topic_rel.get("publication_topics") else 0}%;"></div></div>'
                        f'</div>'
                        for topic, count in list(topic_rel.get("publication_topics", {}).items())[:10]
                    ])}
                </div>
                <div>
                    <h4>Citing Topics</h4>
                    {''.join([
                        f'<div class="rank-item">'
                        f'<span class="rank-name">{html.escape(topic[:40])}</span>'
                        f'<span class="rank-count">{count}</span>'
                        f'<div class="progress-bar"><div class="progress-fill" style="width: {count/max(topic_rel.get("citing_topics", {}).values())*100 if topic_rel.get("citing_topics") else 0}%;"></div></div>'
                        f'</div>'
                        for topic, count in list(topic_rel.get("citing_topics", {}).items())[:10]
                    ])}
                </div>
            </div>
            
            <div style="margin-top: 20px;">
                <h4>Hot Topics (Citation Impact)</h4>
                {''.join([
                    f'<div class="rank-item" style="border-left-color: #ff6b6b;">'
                    f'<span class="rank-name">{html.escape(topic[:40])}</span>'
                    f'<span class="rank-count">Citations: {data["citations"]} | Ratio: {data["ratio"]:.2f}</span>'
                    f'<div class="progress-bar"><div class="progress-fill" style="width: {data["ratio"]/max([d["ratio"] for d in topic_rel.get("hot_topics", {}).values()])*100 if topic_rel.get("hot_topics") else 0}%;"></div></div>'
                    f'<div style="font-size: 11px; color: #666;">Publications: {data["publications"]}</div>'
                    f'</div>'
                    for topic, data in list(topic_rel.get("hot_topics", {}).items())[:10]
                ])}
            </div>
        </div>
        
        <!-- ===== DETAILED CITATIONS ===== -->
        <div id="detailed-citations" class="section">
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
                    <div style="font-size: 13px; margin-bottom: 8px; color: #666;">
                        <strong>Authors:</strong> {', '.join(data['authors'])}
                    </div>
                    {''.join([
                        f'''
                        <div class="citation-detail">
                            <div><strong>{html.escape(cite['citing_title'])}</strong></div>
                            <div class="cite-meta">
                                <strong>{t('citing_journal')}:</strong> {html.escape(cite['citing_journal'])} | 
                                <strong>{t('citing_year')}:</strong> {cite['citing_year']} | 
                                <strong>{t('citing_date')}:</strong> {cite['citing_date']}
                            </div>
                            <div class="cite-meta">
                                <strong>{t('authors')}:</strong> {', '.join(cite['citing_authors'])} |
                                <strong>{t('countries')}:</strong> {', '.join(cite['citing_countries'])}
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
        
        <!-- ===== ALL PUBLICATIONS ===== -->
        <div id="all-publications" class="section">
            <div class="section-title"><span class="icon">📚</span> {t('all_publications')}</div>
            
            <div style="overflow-x: auto;">
                <table id="publicationsTable">
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Title</th>
                            <th>Year</th>
                            <th>Citations</th>
                            <th>Citations/Year</th>
                            <th>Journal</th>
                            <th>Authors</th>
                            <th>DOI</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join([
                            f'<tr>'
                            f'<td>{i+1}</td>'
                            f'<td class="full-text">{html.escape(p.title)}</td>'
                            f'<td>{p.publication_year}</td>'
                            f'<td><span class="citation-count">{p.cited_by_count}</span></td>'
                            f'<td>{p.citations_per_year:.1f}</td>'
                            f'<td>{html.escape(p.journal_name)}</td>'
                            f'<td>{", ".join([a.display_name for a in p.authors])}</td>'
                            f'<td><a href="https://doi.org/{p.doi}" target="_blank" class="doi-link">{p.doi}</a></td>'
                            f'</tr>'
                            for i, p in enumerate(all_publications)
                        ])}
                    </tbody>
                </table>
            </div>
            <p style="margin-top: 10px; color: #666; font-size: 13px;">Total: {len(all_publications)} publications</p>
        </div>
        
        <!-- ===== FOOTER ===== -->
        <div class="footer">
            <p>{t('footer')}</p>
            <p><a href="{t('journal_url')}" target="_blank">{t('journal_url')}</a></p>
            <p style="font-size: 11px; margin-top: 5px;">Data source: OpenAlex | Generated: {datetime.now().strftime('%d.%m.%Y')}</p>
        </div>
        
    </div>
</div>

<script>
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
    
    // Smooth scroll for sidebar links
    document.querySelectorAll('.sidebar-nav a').forEach(link => {{
        link.addEventListener('click', function(e) {{
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            const target = document.getElementById(targetId);
            if (target) {{
                target.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
            }}
        }});
    }});
</script>

</body>
</html>"""
    
    return html_content

# ============================================
# MAIN ANALYSIS FUNCTION
# ============================================

async def analyze_journal(issn: str, periods: List[Tuple[int, int]], progress_callback=None) -> Tuple[Journal, List[Publication], Dict[str, List[Citation]], Dict]:
    """Main journal analysis function"""
    
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
    
    async with aiohttp.ClientSession() as session:
        if progress_callback:
            progress_callback('journal', 0, 100)
        
        journal_data = await get_journal_by_issn(issn_clean, session)
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
        
        works = await get_journal_publications(journal.id, session, periods, pub_progress, issn_clean)
        
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
        
        for idx, pub in enumerate(publications):
            if progress_callback:
                progress_callback('citations', idx + 1, len(publications))
            
            if pub.cited_by_count > 0:
                citing_works = await get_work_citations(pub.id, session)
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
    if 'design_theme' not in st.session_state:
        st.session_state.design_theme = 'default'
    if 'reference_color_style' not in st.session_state:
        st.session_state.reference_color_style = 'full'
    
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
        
        # Design Theme
        st.markdown(f"## {t('design_theme')}")
        available_themes = get_available_themes()
        theme_options = {theme: get_theme_display_name(theme) for theme in available_themes}
        current_theme = st.session_state.get('design_theme', 'default')
        
        theme_cols = st.columns(3)
        for i, key in enumerate(available_themes):
            col_idx = i % 3
            with theme_cols[col_idx]:
                if st.button(
                    theme_options[key],
                    key=f"theme_{key}",
                    use_container_width=True,
                    type="primary" if current_theme == key else "secondary"
                ):
                    st.session_state.design_theme = key
                    st.rerun()
        
        theme_info = get_theme_info(current_theme)
        st.info(t('theme_current').format(theme_info['name']))
        
        if not theme_info['uses_primary'] and not theme_info['uses_secondary']:
            st.warning(t('theme_color_warning'))
        elif theme_info['uses_primary'] and not theme_info['uses_secondary']:
            st.info(t('theme_color_partial'))
        
        st.markdown("---")
        
        # Reference Color Style
        st.markdown(f"## {t('reference_colors')}")
        color_style_options = {
            'full': t('ref_colors_full'),
            'border_only': t('ref_colors_border'),
            'icons': t('ref_colors_icons'),
            'themed': t('ref_colors_themed'),
            'text': t('ref_colors_text')
        }
        current_color_style = st.session_state.get('reference_color_style', 'full')
        color_style = st.selectbox(
            "",
            options=list(color_style_options.keys()),
            format_func=lambda x: color_style_options[x],
            index=list(color_style_options.keys()).index(current_color_style)
        )
        if color_style != current_color_style:
            st.session_state.reference_color_style = color_style
            st.rerun()
        
        st.markdown("---")
        
        # Color Theme
        st.markdown(f"## 🎨 Color Theme")
        
        preset_themes = {
            "Default (Blue-Purple)": {"primary": "#667eea", "secondary": "#9b59b6"},
            "Emerald (Green-Teal)": {"primary": "#2ecc71", "secondary": "#27ae60"},
            "Sunset (Orange-Coral)": {"primary": "#e74c3c", "secondary": "#c0392b"},
            "Ocean (Deep Blue)": {"primary": "#3498db", "secondary": "#2980b9"},
            "Royal (Purple-Pink)": {"primary": "#9b59b6", "secondary": "#e84393"},
            "Forest (Dark Green)": {"primary": "#27ae60", "secondary": "#2ecc71"},
            "Cherry (Red-Pink)": {"primary": "#e84393", "secondary": "#9b59b6"},
            "Amber (Yellow-Orange)": {"primary": "#f39c12", "secondary": "#e67e22"},
        }
        
        theme_option = st.selectbox(
            "🎨 Preset themes",
            options=list(preset_themes.keys()),
            index=0
        )
        
        use_preset = st.checkbox("Use preset theme", value=True)
        
        if use_preset:
            selected_theme = preset_themes[theme_option]
            st.session_state.primary_color = selected_theme["primary"]
            st.session_state.secondary_color = selected_theme["secondary"]
        else:
            selected_color = st.color_picker(
                "🎨 Pick your primary color",
                value=st.session_state.primary_color
            )
            st.session_state.primary_color = selected_color
            st.session_state.secondary_color = get_complementary_color(selected_color)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(
                f'<div style="text-align: center;"><div style="background: {st.session_state.primary_color}; height: 40px; border-radius: 8px;"></div><div style="font-size: 10px; margin-top: 3px;">Primary</div></div>',
                unsafe_allow_html=True
            )
        with col2:
            st.markdown(
                f'<div style="text-align: center;"><div style="background: {st.session_state.secondary_color}; height: 40px; border-radius: 8px;"></div><div style="font-size: 10px; margin-top: 3px;">Complementary</div></div>',
                unsafe_allow_html=True
            )
        
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
            
            journal, publications, citations, analytics = asyncio.run(
                analyze_journal(issn_clean, periods, progress_callback)
            )
            
            if not journal:
                st.error(t('journal_not_found'))
                progress_placeholder.empty()
                status_placeholder.empty()
                return
            
            st.session_state.journal = journal
            st.session_state.publications = publications
            st.session_state.citations = citations
            st.session_state.analytics = analytics
            st.session_state.periods = periods
            st.session_state.analysis_done = True
            
            elapsed = time.time() - start_time
            
            progress_placeholder.progress(1.0)
            status_placeholder.empty()
            
            st.success(t('analysis_complete', count=len(publications), time=elapsed))
            st.balloons()
            
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
            st.metric(t('hot_topics'), len(topic_rel.get('hot_topics', {})))
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(t('topic_overlap_percentage'), f"{topic_rel.get('overlap_percentage', 0):.1f}%")
        with col2:
            st.metric(t('unique_citing_journals'), citing_stats.get('unique_journals', 0))
        with col3:
            st.metric(t('unique_citing_publishers'), citing_stats.get('unique_publishers', 0))
        
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
                journal, analytics, periods, images, theme_colors, current_lang, 
                publications, st.session_state.design_theme, st.session_state.reference_color_style
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
