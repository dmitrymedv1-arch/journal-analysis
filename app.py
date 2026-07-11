"""
app.py - Journal Metrics Analyzer
Advanced analytics for scientific journals using OpenAlex API
"""

import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime
from collections import Counter, defaultdict
from typing import Dict, List, Tuple, Optional, Set
import hashlib
from tenacity import retry, stop_after_attempt, wait_exponential, wait_random
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import math
from collections import defaultdict
from itertools import combinations
import html
import threading
import re
from dataclasses import dataclass, field
import random
from io import StringIO


# ======================== COLOR UTILITIES FOR DYNAMIC THEMES ========================
import colorsys

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

def show_color_preview():
    """Display interactive color preview in sidebar"""
    primary = st.session_state.get('primary_color', '#667eea')
    secondary = st.session_state.get('secondary_color', get_complementary_color(primary))
    analogous = get_analogous_colors(primary, 2)
    
    st.markdown("### 🎨 Color Preview")
    
    palette_html = f"""
    <div style="display: flex; gap: 10px; margin: 15px 0; flex-wrap: wrap;">
        <div style="flex: 1; text-align: center;">
            <div style="background: {primary}; height: 60px; border-radius: 10px 10px 0 0;"></div>
            <div style="background: {secondary}; height: 60px; border-radius: 0 0 10px 10px;"></div>
            <div style="font-size: 11px; margin-top: 5px;">Primary → Complementary</div>
        </div>
        <div style="flex: 1; text-align: center;">
            <div style="background: {analogous[0] if analogous else primary}; height: 60px; border-radius: 10px;"></div>
            <div style="font-size: 11px; margin-top: 5px;">Analogous 1</div>
        </div>
        <div style="flex: 1; text-align: center;">
            <div style="background: {analogous[1] if len(analogous) > 1 else secondary}; height: 60px; border-radius: 10px;"></div>
            <div style="font-size: 11px; margin-top: 5px;">Analogous 2</div>
        </div>
    </div>
    
    <div style="display: flex; gap: 10px; margin: 10px 0;">
        <div style="flex: 1; background: linear-gradient(135deg, {primary}, {secondary}); height: 30px; border-radius: 15px;"></div>
        <div style="flex: 1; background: linear-gradient(90deg, {primary}, {secondary}); height: 30px; border-radius: 15px;"></div>
    </div>
    """
    st.markdown(palette_html, unsafe_allow_html=True)
    
    if st.button("Reset to Default Theme", use_container_width=True):
        st.session_state.primary_color = '#667eea'
        st.rerun()

def get_analogous_colors(hex_color: str, count: int = 2) -> List[str]:
    """
    Generate analogous colors (colors adjacent on color wheel)
    Useful for gradients and accents
    """
    rgb = hex_to_rgb(hex_color)
    h, s, v = colorsys.rgb_to_hsv(rgb[0]/255.0, rgb[1]/255.0, rgb[2]/255.0)
    
    colors = []
    step = 30 / 360.0
    
    for i in range(count):
        offset = (i + 1) * step
        new_hue = (h + offset) % 1.0
        new_rgb = colorsys.hsv_to_rgb(new_hue, s, v)
        colors.append(rgb_to_hex(tuple(int(c * 255) for c in new_rgb)))
    
    return colors

def get_gradient_colors(hex_color: str, steps: int = 5) -> List[str]:
    """
    Generate gradient colors from base color to lighter shades
    """
    rgb = hex_to_rgb(hex_color)
    colors = []
    
    for i in range(steps):
        factor = 0.3 + (i * 0.14)
        new_rgb = tuple(min(255, int(c * (1 + factor * 0.5))) for c in rgb)
        colors.append(rgb_to_hex(new_rgb))
    
    return colors

def get_contrast_color(hex_color: str) -> str:
    """
    Get contrasting color (black or white) for text on a colored background
    Uses luminance calculation for optimal readability
    """
    rgb = hex_to_rgb(hex_color)
    luminance = (0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]) / 255
    return '#FFFFFF' if luminance < 0.5 else '#000000'

def generate_css_variables(base_color: str, accent_color: str = None) -> Dict[str, str]:
    """
    Generate complete CSS variable set for the theme
    """
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
    """
    Apply dynamic CSS theme based on selected colors
    """
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
    </style>
    """
    st.markdown(theme_css, unsafe_allow_html=True)

# ======================== DATA MODELS ========================

@dataclass
class Author:
    """Author data model"""
    display_name: str
    orcid: str = ""
    affiliations: List[str] = field(default_factory=list)
    countries: List[str] = field(default_factory=list)
    raw_data: Dict = field(default_factory=dict)

@dataclass
class Topic:
    """Topic/Concept data model"""
    display_name: str
    score: float = 0.0
    id: str = ""
    type: str = ""  # topic, field, subfield, domain, concept

@dataclass
class Publication:
    """Publication data model"""
    id: str
    doi: str
    title: str
    publication_year: int
    cited_by_count: int
    citations_per_year: float = 0.0
    authors: List[Author] = field(default_factory=list)
    journal_name: str = ""
    publisher: str = ""
    open_access_status: str = ""
    is_open_access: bool = False
    topics: List[Topic] = field(default_factory=list)
    concepts: List[Topic] = field(default_factory=list)
    raw_data: Dict = field(default_factory=dict)

@dataclass
class CitingWork:
    """Citing work data model"""
    citing_title: str
    citing_year: int
    citing_date: str
    citing_journal: str
    citing_publisher: str
    citing_doi: str
    citing_authors: List[Author] = field(default_factory=list)
    citing_countries: List[str] = field(default_factory=list)
    citing_affiliations: List[str] = field(default_factory=list)
    citing_topics: List[Topic] = field(default_factory=list)
    citing_open_access_status: str = ""
    citation_lag: int = 0

@dataclass
class JournalData:
    """Container for all collected data"""
    publications: List[Publication] = field(default_factory=list)
    citations: Dict[str, List[CitingWork]] = field(default_factory=dict)
    citing_works: List[CitingWork] = field(default_factory=list)

# ======================== LOCALIZATION DICTIONARY ========================
TEXTS = {
    'en': {
        # App
        'app_title': "Journal Metrics Analyzer",
        'app_subtitle': "Advanced analytics for scientific journals using OpenAlex API",
        
        # Sidebar
        'issn_label': "ISSN",
        'issn_placeholder': "0028-0836",
        'period_label': "Period",
        'period_placeholder': "2020-2023 or 2025 or 2020,2021,2022",
        'period_help': "Single year (2025), range (2020-2023), or list (2020,2021,2022)",
        'workers_label': "Parallel workers",
        'workers_help': "Number of parallel API requests (4-12 recommended)",
        'language_label': "Language",
        'language_english': "English",
        'language_russian': "Russian",
        'start_analysis': "🚀 Start Analysis",
        
        # Tabs
        'tab_collect': "📊 Data Collection",
        'tab_analytics': "📈 Analytics",
        'tab_report': "📄 Export",
        
        # Data Collection
        'collecting_data': "Collecting data from OpenAlex...",
        'step_publications': "Step 1: Getting journal publications...",
        'found_publications': "Found {0} publications",
        'step_citations': "Step 2: Collecting citing works for {0} publications...",
        'collecting_citations_for': "Collecting citations for publication {0}/{1}",
        'step_citing_metadata': "Step 3: Enriching citing works metadata...",
        'analysis_complete': "✅ Analysis complete!",
        'total_publications_found': "Total publications: {0}",
        'total_citations_found': "Total citations: {0}",
        'go_to_analytics': "👈 Go to 'Analytics' tab for detailed results",
        
        # Overview Section
        'overview': "Overview",
        'total_publications': "Total Publications",
        'total_citations': "Total Citations",
        'h_index': "h-index",
        'g_index': "g-index",
        'i10_index': "i10-index",
        'i100_index': "i100-index",
        'avg_citations': "Avg Citations",
        'open_access': "Open Access",
        'active_years': "Active Years",
        'unique_authors': "Unique Authors",
        'unique_countries': "Unique Countries",
        'total_citing_works': "Total Citing Works",
        'unique_citing_journals': "Unique Citing Journals",
        'avg_authors_per_paper': "Avg Authors per Paper",
        'avg_affiliations_per_paper': "Avg Affiliations per Paper",
        'avg_countries_per_paper': "Avg Countries per Paper",
        'international_collaboration_rate': "International Collaboration Rate",
        
        # Open Access Breakdown
        'open_access_breakdown': "Open Access Breakdown",
        'gold': "Gold",
        'hybrid': "Hybrid",
        'green': "Green",
        'bronze': "Bronze",
        'closed': "Closed",
        'unknown': "Unknown",
        
        # Most Cited
        'most_cited_publications': "Most Cited Publications (Top 30)",
        'rank': "Rank",
        'title': "Title",
        'year': "Year",
        'citations': "Citations",
        'citations_per_year': "Citations/Year",
        'authors': "Authors",
        'doi': "DOI",
        'show_citations': "Show Citations",
        'citing_journal': "Citing Journal",
        'citing_year': "Citing Year",
        'citing_date': "Citing Date",
        'citation_lag': "Citation Lag (years)",
        'countries': "Countries",
        'topics': "Topics",
        
        # Author Analysis
        'author_analysis': "Author Analysis",
        'top_authors': "Top Authors (with ORCID)",
        'orcid': "ORCID",
        'affiliations': "Affiliations",
        'publication_count': "Publications",
        'citation_count': "Citations",
        
        # Geographic Analysis
        'geographic_analysis': "Geographic Analysis",
        'geography_type_1': "Type 1: Unique Countries per Publication",
        'geography_type_1_desc': "Each publication counted once per unique country",
        'geography_type_2': "Type 2: Authors per Country",
        'geography_type_2_desc': "Each author counted separately",
        'geography_type_3': "Type 3: Collaboration Patterns",
        'geography_type_3_desc': "Distribution of single-country vs international collaborations",
        'single_country': "Single country",
        'international_collaboration': "International collaboration",
        'collaboration_couples': "Collaboration Couples (Country Pairs)",
        'collaboration_matrix': "Collaboration Matrix",
        'country1': "Country 1",
        'country2': "Country 2",
        'count': "Count",
        
        # Citation Analysis
        'citation_analysis': "Citation Analysis",
        'yearly_citation_dynamics': "Yearly Citation Dynamics",
        'cumulative_citation_dynamics': "Cumulative Citation Dynamics",
        'citation_network': "Citation Network (Heatmap)",
        'publication_year': "Publication Year",
        'citation_year': "Citation Year",
        'citations_count': "Citations Count",
        
        # Citing Works Analysis
        'citing_works_analysis': "Citing Works Analysis",
        'total_citing_works': "Total Citing Works",
        'unique_citing_authors': "Unique Citing Authors",
        'unique_citing_affiliations': "Unique Citing Affiliations",
        'unique_citing_countries': "Unique Citing Countries",
        'unique_citing_journals': "Unique Citing Journals",
        'unique_citing_publishers': "Unique Citing Publishers",
        'top_citing_authors': "Top Citing Authors",
        'top_citing_affiliations': "Top Citing Affiliations",
        'top_citing_countries': "Top Citing Countries",
        'top_citing_journals': "Top Citing Journals",
        'top_citing_publishers': "Top Citing Publishers",
        
        # Topics Analysis
        'topics_analysis': "Topics Analysis",
        'topic': "Topic",
        'analyzed_count': "Analyzed Count",
        'citing_count': "Citing Count",
        'analyzed_norm_count': "Analyzed Norm Count",
        'citing_norm_count': "Citing Norm Count",
        'total_norm_count': "Total Norm Count",
        'first_year': "First Year",
        'peak_year': "Peak Year",
        'recent_5_years_count': "Recent 5 Years Count",
        'top_topics': "Top Topics",
        'top_fields': "Top Fields",
        'top_subfields': "Top Subfields",
        'top_domains': "Top Domains",
        'top_concepts': "Top Concepts",
        
        # Detailed Citations
        'detailed_citations': "Detailed Citations",
        'click_to_toggle': "Click to toggle citations",
        
        # All Publications
        'all_publications': "All Publications",
        'filter_by_year': "Filter by Year",
        'filter_by_author': "Filter by Author",
        'filter_by_citations': "Filter by Citations (min)",
        'search_publications': "Search Publications",
        'showing_publications': "Showing {0} publications",
        'all_years': "All Years",
        'author_name_placeholder': "Author name...",
        'min_citations_placeholder': "Min citations...",
        'search_placeholder': "Search...",
        
        # Export
        'export_html_report': "📄 Export HTML Report",
        'download_html_report': "💾 Download HTML Report",
        'export_csv': "📋 Export CSV",
        'download_csv': "💾 Download CSV (Full Data)",
        'export_text': "📋 Text Export",
        'copy_to_clipboard': "📋 Copy to clipboard",
        'copied': "✅ Data copied!",
        'run_analysis_first': "👈 Please run analysis in 'Data Collection' tab first",
        
        # HTML Report
        'html_generated': "Generated",
        'html_footer': "",
        'html_copyright': "© Journal Metrics Analyzer / Created by daM",
        'html_not_found': "Not found",
        'html_citations_label': "citations",
        'html_percentage': "Percentage",
        'html_connections': "connections",
        'html_joint_works': "joint works",
        'html_authors_count': "authors",
        'html_frequency': "Frequency",
        'html_citations_count': "citations",
        'html_works': "works",
        'html_rank': "Rank",
        'html_count': "Count",
        'html_journal_label': "Journal",
        
        # Citation Velocity
        'citation_velocity': "Citation Velocity",
        'velocity': "Velocity (citations/year)",
        'velocity_category': "Velocity Category",
        'very_high': "Very High",
        'high': "High",
        'medium': "Medium",
        'low': "Low",
        'age': "Age (years)",
    },
    'ru': {
        # App
        'app_title': "Анализатор метрик журнала",
        'app_subtitle': "Расширенная аналитика для научных журналов с использованием OpenAlex API",
        
        # Sidebar
        'issn_label': "ISSN",
        'issn_placeholder': "0028-0836",
        'period_label': "Период",
        'period_placeholder': "2020-2023 или 2025 или 2020,2021,2022",
        'period_help': "Один год (2025), диапазон (2020-2023) или список (2020,2021,2022)",
        'workers_label': "Параллельных потоков",
        'workers_help': "Количество параллельных API запросов (рекомендуется 4-12)",
        'language_label': "Язык",
        'language_english': "Английский",
        'language_russian': "Русский",
        'start_analysis': "🚀 Запустить анализ",
        
        # Tabs
        'tab_collect': "📊 Сбор данных",
        'tab_analytics': "📈 Аналитика",
        'tab_report': "📄 Экспорт",
        
        # Data Collection
        'collecting_data': "Сбор данных из OpenAlex...",
        'step_publications': "Шаг 1: Получение публикаций журнала...",
        'found_publications': "Найдено {0} публикаций",
        'step_citations': "Шаг 2: Сбор цитирующих работ для {0} публикаций...",
        'collecting_citations_for': "Сбор цитирований для публикации {0}/{1}",
        'step_citing_metadata': "Шаг 3: Обогащение метаданных цитирующих работ...",
        'analysis_complete': "✅ Анализ завершен!",
        'total_publications_found': "Всего публикаций: {0}",
        'total_citations_found': "Всего цитирований: {0}",
        'go_to_analytics': "👈 Перейдите на вкладку 'Аналитика' для просмотра результатов",
        
        # Overview Section
        'overview': "Обзор",
        'total_publications': "Всего публикаций",
        'total_citations': "Всего цитирований",
        'h_index': "h-индекс",
        'g_index': "g-индекс",
        'i10_index': "i10-индекс",
        'i100_index': "i100-индекс",
        'avg_citations': "Среднее цитирований",
        'open_access': "Открытый доступ",
        'active_years': "Активные годы",
        'unique_authors': "Уникальных авторов",
        'unique_countries': "Уникальных стран",
        'total_citing_works': "Всего цитирующих работ",
        'unique_citing_journals': "Уникальных цитирующих журналов",
        'avg_authors_per_paper': "Среднее авторов на статью",
        'avg_affiliations_per_paper': "Среднее аффилиаций на статью",
        'avg_countries_per_paper': "Среднее стран на статью",
        'international_collaboration_rate': "Доля международных коллабораций",
        
        # Open Access Breakdown
        'open_access_breakdown': "Распределение по типам доступа",
        'gold': "Gold",
        'hybrid': "Hybrid",
        'green': "Green",
        'bronze': "Bronze",
        'closed': "Закрытый",
        'unknown': "Неизвестно",
        
        # Most Cited
        'most_cited_publications': "Самые цитируемые публикации (Топ-30)",
        'rank': "Ранг",
        'title': "Название",
        'year': "Год",
        'citations': "Цитирований",
        'citations_per_year': "Цитирований/год",
        'authors': "Авторы",
        'doi': "DOI",
        'show_citations': "Показать цитирования",
        'citing_journal': "Цитирующий журнал",
        'citing_year': "Год цитирования",
        'citing_date': "Дата цитирования",
        'citation_lag': "Задержка цитирования (лет)",
        'countries': "Страны",
        'topics': "Темы",
        
        # Author Analysis
        'author_analysis': "Анализ авторов",
        'top_authors': "Топ авторов (с ORCID)",
        'orcid': "ORCID",
        'affiliations': "Аффилиации",
        'publication_count': "Публикаций",
        'citation_count': "Цитирований",
        
        # Geographic Analysis
        'geographic_analysis': "Географический анализ",
        'geography_type_1': "Тип 1: Уникальные страны по публикации",
        'geography_type_1_desc': "Каждая публикация учитывается один раз на уникальную страну",
        'geography_type_2': "Тип 2: Авторы по странам",
        'geography_type_2_desc': "Каждый автор учитывается отдельно",
        'geography_type_3': "Тип 3: Паттерны коллабораций",
        'geography_type_3_desc': "Распределение внутристрановых и международных коллабораций",
        'single_country': "Одна страна",
        'international_collaboration': "Международная коллаборация",
        'collaboration_couples': "Пары стран (частота взаимодействия)",
        'collaboration_matrix': "Матрица коллабораций",
        'country1': "Страна 1",
        'country2': "Страна 2",
        'count': "Количество",
        
        # Citation Analysis
        'citation_analysis': "Анализ цитирований",
        'yearly_citation_dynamics': "Динамика цитирования по годам",
        'cumulative_citation_dynamics': "Кумулятивная динамика цитирования",
        'citation_network': "Сеть цитирования (тепловая карта)",
        'publication_year': "Год публикации",
        'citation_year': "Год цитирования",
        'citations_count': "Количество цитирований",
        
        # Citing Works Analysis
        'citing_works_analysis': "Анализ цитирующих работ",
        'total_citing_works': "Всего цитирующих работ",
        'unique_citing_authors': "Уникальных цитирующих авторов",
        'unique_citing_affiliations': "Уникальных цитирующих аффилиаций",
        'unique_citing_countries': "Уникальных цитирующих стран",
        'unique_citing_journals': "Уникальных цитирующих журналов",
        'unique_citing_publishers': "Уникальных цитирующих издательств",
        'top_citing_authors': "Топ цитирующих авторов",
        'top_citing_affiliations': "Топ цитирующих аффилиаций",
        'top_citing_countries': "Топ цитирующих стран",
        'top_citing_journals': "Топ цитирующих журналов",
        'top_citing_publishers': "Топ цитирующих издательств",
        
        # Topics Analysis
        'topics_analysis': "Анализ тем",
        'topic': "Тема",
        'analyzed_count': "Анализируемых",
        'citing_count': "Цитирующих",
        'analyzed_norm_count': "Норм. анализируемых",
        'citing_norm_count': "Норм. цитирующих",
        'total_norm_count': "Всего норм.",
        'first_year': "Первый год",
        'peak_year': "Пиковый год",
        'recent_5_years_count': "Последние 5 лет",
        'top_topics': "Топ тем",
        'top_fields': "Топ полей",
        'top_subfields': "Топ подполей",
        'top_domains': "Топ доменов",
        'top_concepts': "Топ концепций",
        
        # Detailed Citations
        'detailed_citations': "Детальные цитирования",
        'click_to_toggle': "Нажмите для показа цитирований",
        
        # All Publications
        'all_publications': "Все публикации",
        'filter_by_year': "Фильтр по году",
        'filter_by_author': "Фильтр по автору",
        'filter_by_citations': "Фильтр по цитированиям (мин)",
        'search_publications': "Поиск публикаций",
        'showing_publications': "Показано {0} публикаций",
        'all_years': "Все годы",
        'author_name_placeholder': "Имя автора...",
        'min_citations_placeholder': "Мин. цитирований...",
        'search_placeholder': "Поиск...",
        
        # Export
        'export_html_report': "📄 Экспорт HTML отчета",
        'download_html_report': "💾 Скачать HTML отчет",
        'export_csv': "📋 Экспорт CSV",
        'download_csv': "💾 Скачать CSV (полные данные)",
        'export_text': "📋 Текстовый экспорт",
        'copy_to_clipboard': "📋 Копировать в буфер",
        'copied': "✅ Данные скопированы!",
        'run_analysis_first': "👈 Сначала запустите анализ на вкладке 'Сбор данных'",
        
        # HTML Report
        'html_generated': "Сгенерирован",
        'html_footer': "",
        'html_copyright': "© Journal Metrics Analyzer / Created by daM",
        'html_not_found': "Не найден",
        'html_citations_label': "цитирований",
        'html_percentage': "Процент",
        'html_connections': "связей",
        'html_joint_works': "совместных работ",
        'html_authors_count': "авторов",
        'html_frequency': "Частота",
        'html_citations_count': "цитирований",
        'html_works': "работ",
        'html_rank': "Ранг",
        'html_count': "Количество",
        'html_journal_label': "Журнал",
        
        # Citation Velocity
        'citation_velocity': "Скорость цитирования",
        'velocity': "Скорость (цитирований/год)",
        'velocity_category': "Категория скорости",
        'very_high': "Очень высокая",
        'high': "Высокая",
        'medium': "Средняя",
        'low': "Низкая",
        'age': "Возраст (лет)",
    }
}

def get_text(key: str) -> str:
    """Get localized text by key"""
    lang = st.session_state.get('language', 'en')
    return TEXTS[lang].get(key, TEXTS['en'].get(key, key))

# ======================== PAGE CONFIGURATION ========================
st.set_page_config(
    page_title="Journal Metrics Analyzer",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'language' not in st.session_state:
    st.session_state.language = 'en'
if 'primary_color' not in st.session_state:
    st.session_state.primary_color = '#667eea'
if 'secondary_color' not in st.session_state:
    st.session_state.secondary_color = get_complementary_color('#667eea')
if 'journal_data' not in st.session_state:
    st.session_state.journal_data = None
if 'metrics' not in st.session_state:
    st.session_state.metrics = None
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False

# ======================== CSS STYLES ========================
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    .metric-card {
        background: white;
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: transform 0.3s;
        margin-bottom: 15px;
    }
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }
    .metric-number {
        font-size: 36px;
        font-weight: bold;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .metric-label {
        color: #666;
        font-size: 14px;
        margin-top: 8px;
    }
    
    .rank-item {
        background: white;
        border-radius: 10px;
        padding: 12px;
        margin-bottom: 8px;
        transition: all 0.3s;
        border-left: 3px solid #667eea;
    }
    .rank-item:hover {
        transform: translateX(5px);
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .rank-number {
        font-weight: bold;
        color: #667eea;
        font-size: 18px;
        display: inline-block;
        width: 40px;
    }
    .rank-name {
        display: inline-block;
        width: 200px;
        font-weight: 500;
    }
    .rank-count {
        float: right;
        color: #666;
    }
    .progress-bar-custom {
        background: #e0e0e0;
        border-radius: 10px;
        height: 8px;
        margin-top: 8px;
        overflow: hidden;
    }
    .progress-fill {
        background: linear-gradient(90deg, #667eea, #764ba2);
        height: 100%;
        border-radius: 10px;
        transition: width 0.5s;
    }
    
    .badge-success {
        background: #d4edda;
        color: #155724;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        display: inline-block;
    }
    .badge-warning {
        background: #fff3cd;
        color: #856404;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
    }
    .badge-info {
        background: #d1ecf1;
        color: #0c5460;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
    }
    
    .section-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 12px 20px;
        border-radius: 10px;
        margin: 20px 0 15px 0;
        font-weight: 600;
    }
    
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 20px;
        margin-bottom: 30px;
    }
    
    .custom-tab {
        background: white;
        border-radius: 10px;
        padding: 20px;
        margin-top: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .custom-tab-button {
        background: linear-gradient(135deg, #f5f7fa 0%, #e9ecef 100%);
        border: none;
        border-radius: 12px;
        padding: 15px 10px;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s;
        margin: 5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .custom-tab-button:hover {
        transform: translateY(-3px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        background: linear-gradient(135deg, #e9ecef 0%, #dee2e6 100%);
    }
    .custom-tab-button.active {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    .custom-tab-icon {
        font-size: 28px;
        margin-bottom: 8px;
    }
    .custom-tab-title {
        font-weight: 600;
        font-size: 14px;
    }
    .custom-tab-subtitle {
        font-size: 11px;
        opacity: 0.8;
        margin-top: 4px;
    }
    
    .clickable-link {
        color: #667eea;
        text-decoration: none;
        transition: all 0.3s;
    }
    .clickable-link:hover {
        color: #764ba2;
        text-decoration: underline;
    }
    
    .footer {
        text-align: center;
        padding: 20px;
        color: #666;
        font-size: 12px;
        margin-top: 40px;
    }
    
    .colored-progress-container {
        width: 100%;
        background-color: #f0f0f0;
        border-radius: 20px;
        overflow: hidden;
        box-shadow: inset 0 1px 3px rgba(0,0,0,0.2);
        margin: 10px 0;
    }
    
    .colored-progress-bar {
        height: 28px;
        border-radius: 20px;
        transition: width 0.5s ease-in-out;
        position: relative;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        font-size: 12px;
        text-shadow: 0 0 2px rgba(0,0,0,0.5);
    }
    
    .colored-progress-bar::after {
        position: absolute;
        left: 50%;
        transform: translateX(-50%);
        white-space: nowrap;
    }
    
    .progress-stats {
        display: flex;
        justify-content: space-between;
        font-size: 12px;
        color: #666;
        margin-top: 5px;
    }
    
    .filter-section {
        background: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .filter-row {
        display: flex;
        flex-wrap: wrap;
        gap: 15px;
        align-items: center;
    }
    .filter-row > div {
        flex: 1;
        min-width: 150px;
    }
    .filter-row label {
        display: block;
        font-size: 12px;
        color: #666;
        margin-bottom: 4px;
    }
    .filter-row select, .filter-row input {
        width: 100%;
        padding: 6px 10px;
        border: 1px solid #ddd;
        border-radius: 6px;
        font-size: 13px;
    }
    .filter-row select:focus, .filter-row input:focus {
        outline: none;
        border-color: #667eea;
        box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
    }
    
    .collapser {
        background: #f8f9fa;
        padding: 12px 15px;
        border-radius: 8px;
        cursor: pointer;
        margin-bottom: 8px;
        transition: background 0.2s;
        border-left: 3px solid #667eea;
    }
    .collapser:hover {
        background: #e9ecef;
    }
    .collapser .citation-count {
        background: #667eea;
        color: white;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 11px;
        margin-left: 10px;
    }
    
    .citation-detail {
        background: white;
        padding: 12px 15px;
        margin: 5px 0 5px 20px;
        border-radius: 6px;
        border-left: 2px solid #ddd;
        font-size: 13px;
    }
    .citation-detail .cite-meta {
        font-size: 12px;
        color: #666;
        margin-top: 4px;
    }
    .citation-detail .doi-link {
        color: #667eea;
        text-decoration: none;
        font-size: 12px;
    }
    .citation-detail .doi-link:hover {
        text-decoration: underline;
    }
    
    .word-wrap {
        word-break: break-word;
        max-width: 300px;
    }
    
    .dataframe-container {
        background: white;
        border-radius: 10px;
        padding: 15px;
        overflow-x: auto;
    }
    
    .footer-text {
        text-align: center;
        padding: 20px;
        color: #666;
        font-size: 12px;
        margin-top: 40px;
        border-top: 1px solid #e0e0e0;
    }
</style>
""", unsafe_allow_html=True)

# ======================== OPENALEX API CLIENT ========================

def normalize_issn(issn_str: str) -> str:
    """Normalize ISSN to format XXXX-XXXX"""
    cleaned = re.sub(r'[^0-9Xx]', '', str(issn_str).strip())
    if len(cleaned) == 8:
        return f"{cleaned[:4]}-{cleaned[4:]}".upper()
    return cleaned.upper()

@retry(stop=stop_after_attempt(4), wait=wait_exponential(multiplier=1, min=1, max=10))
def smart_get(url: str, params: Dict, retries: int = 4) -> Optional[Dict]:
    """
    Smart GET request with rate limiting and retry logic
    """
    for attempt in range(retries):
        try:
            time.sleep(random.uniform(0.1, 0.35))
            
            resp = requests.get(url, params=params, timeout=25)
            
            if resp.status_code == 429:
                wait = int(resp.headers.get("Retry-After", 2 ** attempt + 1))
                time.sleep(wait + random.uniform(0.5, 1.5))
                continue
                
            if resp.status_code == 200:
                return resp.json()
            
            time.sleep(1 * (2 ** attempt))
            
        except Exception:
            time.sleep(1.5 * (2 ** attempt))
    
    return None

def get_journal_publications(issn: str, years, progress_callback=None) -> List[Publication]:
    """
    Get all publications from a journal for the specified period
    """
    normalized = normalize_issn(issn)
    publications = []
    
    base_url = "https://api.openalex.org/works"
    
    if isinstance(years, list) and len(years) > 0:
        year_filter = "|".join(f"publication_year:{y}" for y in years)
    elif isinstance(years, tuple) and len(years) == 2:
        year_filter = f"publication_year:{years[0]}-{years[1]}"
    else:
        # Если years - это число (один год)
        year_filter = f"publication_year:{years}"
    
    cursor = "*"
    
    while True:
        params = {
            "filter": f"primary_location.source.issn:{normalized},{year_filter}",
            "per_page": 200,
            "select": "id,doi,publication_year,cited_by_count,title,authorships,primary_location,open_access,topics,concepts,type",
            "cursor": cursor
        }
        
        data = smart_get(base_url, params)
        if not data or not data.get("results"):
            break
        
        for w in data["results"]:
            # Extract authors
            authors = []
            for authorship in w.get("authorships", []):
                author_data = authorship.get("author", {})
                author = Author(
                    display_name=author_data.get("display_name", ""),
                    orcid=author_data.get("orcid", ""),
                    affiliations=[inst.get("display_name", "") for inst in authorship.get("institutions", [])],
                    countries=[inst.get("country_code", "") for inst in authorship.get("institutions", []) if inst.get("country_code")],
                    raw_data=authorship
                )
                authors.append(author)
            
            # Extract topics
            topics = []
            for topic_data in w.get("topics", []):
                topic = Topic(
                    display_name=topic_data.get("display_name", ""),
                    score=topic_data.get("score", 0.0),
                    id=topic_data.get("id", ""),
                    type="topic"
                )
                topics.append(topic)
            
            # Extract concepts
            concepts = []
            for concept_data in w.get("concepts", []):
                concept = Topic(
                    display_name=concept_data.get("display_name", ""),
                    score=concept_data.get("score", 0.0),
                    id=concept_data.get("id", ""),
                    type="concept"
                )
                concepts.append(concept)
            
            # Extract journal and publisher
            journal_name = ""
            publisher = ""
            primary_location = w.get("primary_location", {})
            if primary_location:
                source = primary_location.get("source", {})
                journal_name = source.get("display_name", "")
                publisher = source.get("publisher", "")
            
            # Extract open access
            open_access_data = w.get("open_access", {})
            is_open_access = open_access_data.get("is_open_access", False)
            open_access_status = open_access_data.get("oa_status", "")
            
            # Create publication
            doi = w.get("doi", "")
            if doi:
                doi = doi.replace("https://doi.org/", "")
            
            pub = Publication(
                id=w.get("id", ""),
                doi=doi,
                title=w.get("title", ""),
                publication_year=w.get("publication_year", 0),
                cited_by_count=w.get("cited_by_count", 0),
                citations_per_year=0.0,
                authors=authors,
                journal_name=journal_name,
                publisher=publisher,
                open_access_status=open_access_status,
                is_open_access=is_open_access,
                topics=topics,
                concepts=concepts,
                raw_data=w
            )
            
            publications.append(pub)
        
        if progress_callback:
            progress_callback(len(data["results"]))
        
        cursor = data.get("meta", {}).get("next_cursor")
        if not cursor:
            break
    
    # Calculate citations per year
    current_year = datetime.now().year
    for pub in publications:
        age = current_year - pub.publication_year
        if age > 0:
            pub.citations_per_year = pub.cited_by_count / age
        else:
            pub.citations_per_year = pub.cited_by_count
    
    return publications

def get_citing_works_for_publication(pub_id: str, progress_callback=None) -> List[CitingWork]:
    """
    Get ALL citing works for a publication (no limit)
    """
    citing_works = []
    base_url = "https://api.openalex.org/works"
    cursor = "*"
    
    while True:
        params = {
            "filter": f"cites:{pub_id}",
            "per_page": 200,
            "cursor": cursor
        }
        
        data = smart_get(base_url, params)
        if not data or not data.get("results"):
            break
        
        for w in data["results"]:
            # Extract authors
            authors = []
            for authorship in w.get("authorships", []):
                author_data = authorship.get("author", {})
                author = Author(
                    display_name=author_data.get("display_name", ""),
                    orcid=author_data.get("orcid", ""),
                    affiliations=[inst.get("display_name", "") for inst in authorship.get("institutions", [])],
                    countries=[inst.get("country_code", "") for inst in authorship.get("institutions", []) if inst.get("country_code")],
                    raw_data=authorship
                )
                authors.append(author)
            
            # Extract countries
            countries = set()
            for authorship in w.get("authorships", []):
                for inst in authorship.get("institutions", []):
                    if inst.get("country_code"):
                        countries.add(inst.get("country_code"))
            
            # Extract affiliations
            affiliations = set()
            for authorship in w.get("authorships", []):
                for inst in authorship.get("institutions", []):
                    if inst.get("display_name"):
                        affiliations.add(inst.get("display_name"))
            
            # Extract topics
            topics = []
            for topic_data in w.get("topics", []):
                topic = Topic(
                    display_name=topic_data.get("display_name", ""),
                    score=topic_data.get("score", 0.0),
                    id=topic_data.get("id", ""),
                    type="topic"
                )
                topics.append(topic)
            
            # Extract journal and publisher
            journal_name = ""
            publisher = ""
            primary_location = w.get("primary_location", {})
            if primary_location:
                source = primary_location.get("source", {})
                journal_name = source.get("display_name", "")
                publisher = source.get("publisher", "")
            
            # Extract open access
            open_access_data = w.get("open_access", {})
            open_access_status = open_access_data.get("oa_status", "")
            
            # Extract date
            publication_date = w.get("publication_date", "")
            citing_year = w.get("publication_year", 0)
            
            citing = CitingWork(
                citing_title=w.get("title", ""),
                citing_year=citing_year,
                citing_date=publication_date,
                citing_journal=journal_name,
                citing_publisher=publisher,
                citing_doi=w.get("doi", "").replace("https://doi.org/", ""),
                citing_authors=authors,
                citing_countries=list(countries),
                citing_affiliations=list(affiliations),
                citing_topics=topics,
                citing_open_access_status=open_access_status,
                citation_lag=0  # Will be calculated later
            )
            
            citing_works.append(citing)
        
        if progress_callback:
            progress_callback(len(data["results"]))
        
        cursor = data.get("meta", {}).get("next_cursor")
        if not cursor:
            break
    
    return citing_works

def collect_all_data(issn: str, years, max_workers: int = 8, progress_callback=None) -> JournalData:
    """
    Main method to collect all data with parallel processing
    """
    if progress_callback:
        progress_callback(get_text('step_publications'), 0)
    
    # Step 1: Get publications
    publications = get_journal_publications(issn, years)
    
    if progress_callback:
        progress_callback(get_text('found_publications').format(len(publications)), 10)
    
    if not publications:
        return JournalData()
    
    # Step 2: Get citing works for each publication (parallel)
    citations = {}
    citing_works_set = set()
    
    if progress_callback:
        progress_callback(get_text('step_citations').format(len(publications)), 20)
    
    total_pubs = len(publications)
    completed = 0
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {}
        for pub in publications:
            if pub.id:
                future = executor.submit(get_citing_works_for_publication, pub.id)
                futures[future] = pub.id
        
        for future in as_completed(futures):
            pub_id = futures[future]
            try:
                citing_works = future.result()
                citations[pub_id] = citing_works
                for citing in citing_works:
                    citing_works_set.add(citing.citing_doi)
            except Exception:
                citations[pub_id] = []
            
            completed += 1
            if progress_callback:
                progress_callback(
                    get_text('collecting_citations_for').format(completed, total_pubs),
                    20 + int((completed / total_pubs) * 50)
                )
    
    # Step 3: Calculate citation lag
    pub_years = {pub.id: pub.publication_year for pub in publications}
    for pub_id, citing_list in citations.items():
        pub_year = pub_years.get(pub_id, 0)
        for citing in citing_list:
            citing.citation_lag = citing.citing_year - pub_year if pub_year > 0 else 0
    
    if progress_callback:
        progress_callback(get_text('step_citing_metadata'), 90)
    
    # Step 4: Collect unique citing works
    citing_works_list = []
    for citing_list in citations.values():
        for citing in citing_list:
            if citing.citing_doi not in citing_works_set:
                citing_works_set.add(citing.citing_doi)
                citing_works_list.append(citing)
    
    data = JournalData(
        publications=publications,
        citations=citations,
        citing_works=citing_works_list
    )
    
    if progress_callback:
        progress_callback(get_text('analysis_complete'), 100)
    
    return data

# ======================== METRICS ENGINE ========================

class MetricsEngine:
    """Calculate all metrics from journal data"""
    
    def __init__(self, data: JournalData):
        self.data = data
        self.publications = data.publications
        self.citations = data.citations
        self.citing_works = data.citing_works
    
    def calculate_overview(self) -> Dict:
        """Calculate overview metrics"""
        total_pubs = len(self.publications)
        total_cites = sum(p.cited_by_count for p in self.publications)
        
        # h-index
        citations_sorted = sorted([p.cited_by_count for p in self.publications], reverse=True)
        h_index = 0
        for i, c in enumerate(citations_sorted, 1):
            if c >= i:
                h_index = i
            else:
                break
        
        # g-index
        g_index = 0
        total = 0
        for i, c in enumerate(citations_sorted, 1):
            total += c
            if total >= i * i:
                g_index = i
        
        # i10 and i100 indices
        i10_index = sum(1 for p in self.publications if p.cited_by_count >= 10)
        i100_index = sum(1 for p in self.publications if p.cited_by_count >= 100)
        
        # Average citations
        avg_citations = total_cites / total_pubs if total_pubs > 0 else 0
        
        # Open access
        open_access_count = sum(1 for p in self.publications if p.is_open_access)
        open_access_percent = (open_access_count / total_pubs * 100) if total_pubs > 0 else 0
        
        # Active years
        active_years = len(set(p.publication_year for p in self.publications if p.publication_year > 0))
        
        # Unique authors
        authors_set = set()
        for pub in self.publications:
            for author in pub.authors:
                if author.display_name:
                    authors_set.add(author.display_name)
        
        # Unique countries
        countries_set = set()
        for pub in self.publications:
            for author in pub.authors:
                for country in author.countries:
                    if country:
                        countries_set.add(country)
        
        # Citing works
        total_citing_works = len(self.citing_works)
        
        # Unique citing journals
        citing_journals_set = set()
        for citing in self.citing_works:
            if citing.citing_journal:
                citing_journals_set.add(citing.citing_journal)
        
        # Authors per paper stats
        total_authors = 0
        total_affiliations = 0
        total_countries = 0
        international_count = 0
        
        for pub in self.publications:
            pub_authors = set()
            pub_affiliations = set()
            pub_countries = set()
            
            for author in pub.authors:
                if author.display_name:
                    pub_authors.add(author.display_name)
                for aff in author.affiliations:
                    if aff:
                        pub_affiliations.add(aff)
                for country in author.countries:
                    if country:
                        pub_countries.add(country)
            
            total_authors += len(pub_authors)
            total_affiliations += len(pub_affiliations)
            total_countries += len(pub_countries)
            
            if len(pub_countries) > 1:
                international_count += 1
        
        avg_authors = total_authors / total_pubs if total_pubs > 0 else 0
        avg_affiliations = total_affiliations / total_pubs if total_pubs > 0 else 0
        avg_countries = total_countries / total_pubs if total_pubs > 0 else 0
        international_rate = (international_count / total_pubs * 100) if total_pubs > 0 else 0
        
        # Open access breakdown
        oa_breakdown = {
            'gold': 0,
            'hybrid': 0,
            'green': 0,
            'bronze': 0,
            'closed': 0,
            'unknown': 0
        }
        for pub in self.publications:
            status = pub.open_access_status.lower() if pub.open_access_status else 'unknown'
            if status in oa_breakdown:
                oa_breakdown[status] += 1
            else:
                oa_breakdown['unknown'] += 1
        
        return {
            'total_publications': total_pubs,
            'total_citations': total_cites,
            'h_index': h_index,
            'g_index': g_index,
            'i10_index': i10_index,
            'i100_index': i100_index,
            'avg_citations': avg_citations,
            'open_access_count': open_access_count,
            'open_access_percent': open_access_percent,
            'open_access_breakdown': oa_breakdown,
            'active_years': active_years,
            'unique_authors': len(authors_set),
            'unique_countries': len(countries_set),
            'total_citing_works': total_citing_works,
            'unique_citing_journals': len(citing_journals_set),
            'avg_authors_per_paper': avg_authors,
            'avg_affiliations_per_paper': avg_affiliations,
            'avg_countries_per_paper': avg_countries,
            'international_collaboration_rate': international_rate
        }
    
    def get_most_cited_publications(self, top_n: int = 30) -> List[Dict]:
        """Get most cited publications"""
        sorted_pubs = sorted(self.publications, key=lambda x: x.cited_by_count, reverse=True)
        result = []
        
        for i, pub in enumerate(sorted_pubs[:top_n], 1):
            author_names = [a.display_name for a in pub.authors if a.display_name]
            result.append({
                'rank': i,
                'title': pub.title,
                'year': pub.publication_year,
                'citations': pub.cited_by_count,
                'citations_per_year': pub.citations_per_year,
                'authors': ', '.join(author_names[:5]),
                'authors_full': author_names,
                'doi': pub.doi,
                'id': pub.id,
                'journal': pub.journal_name
            })
        
        return result
    
    def analyze_authors(self) -> Dict:
        """Analyze authors with ORCID and affiliations"""
        author_stats = defaultdict(lambda: {
            'display_name': '',
            'orcid': '',
            'affiliations': set(),
            'countries': set(),
            'publication_count': 0,
            'citation_count': 0,
            'papers': []
        })
        
        for pub in self.publications:
            for author in pub.authors:
                if not author.display_name:
                    continue
                
                key = author.display_name
                stats = author_stats[key]
                
                if not stats['display_name']:
                    stats['display_name'] = author.display_name
                if not stats['orcid'] and author.orcid:
                    stats['orcid'] = author.orcid
                
                stats['affiliations'].update(author.affiliations)
                stats['countries'].update(author.countries)
                stats['publication_count'] += 1
                stats['citation_count'] += pub.cited_by_count
                stats['papers'].append(pub.doi)
        
        # Convert to list and sort
        author_list = []
        for key, stats in author_stats.items():
            author_list.append({
                'display_name': stats['display_name'],
                'orcid': stats['orcid'],
                'affiliations': sorted(list(stats['affiliations'])),
                'countries': sorted(list(stats['countries'])),
                'publication_count': stats['publication_count'],
                'citation_count': stats['citation_count'],
                'papers': stats['papers']
            })
        
        author_list.sort(key=lambda x: x['publication_count'], reverse=True)
        
        return {
            'top_authors': author_list[:30],
            'total_authors': len(author_list)
        }
    
    def analyze_geography(self) -> Dict:
        """Three types of geographic analysis"""
        # Type 1: Unique countries per publication
        country_publication_counter = Counter()
        # Type 2: Authors per country
        country_author_counter = Counter()
        # Type 3: Collaboration patterns
        collaboration_patterns = Counter()
        # Collaboration couples
        country_pair_counter = Counter()
        
        for pub in self.publications:
            pub_countries = set()
            pub_authors_count = 0
            
            for author in pub.authors:
                if author.countries:
                    pub_authors_count += 1
                    for country in author.countries:
                        if country:
                            pub_countries.add(country)
                            country_author_counter[country] += 1
            
            for country in pub_countries:
                country_publication_counter[country] += 1
            
            if len(pub_countries) == 1:
                collaboration_patterns['single'] += 1
            elif len(pub_countries) > 1:
                collaboration_patterns['international'] += 1
                
                # Country pairs
                sorted_countries = sorted(pub_countries)
                for i in range(len(sorted_countries)):
                    for j in range(i + 1, len(sorted_countries)):
                        pair = tuple(sorted([sorted_countries[i], sorted_countries[j]]))
                        country_pair_counter[pair] += 1
        
        # Prepare collaboration couples
        collaboration_couples = []
        for (c1, c2), count in country_pair_counter.most_common(20):
            collaboration_couples.append({
                'country1': c1,
                'country2': c2,
                'count': count
            })
        
        return {
            'type1_unique_countries_per_publication': dict(country_publication_counter.most_common()),
            'type2_authors_per_country': dict(country_author_counter.most_common()),
            'type3_collaboration_patterns': dict(collaboration_patterns),
            'collaboration_couples': collaboration_couples,
            'single_country_count': collaboration_patterns.get('single', 0),
            'international_count': collaboration_patterns.get('international', 0)
        }
    
    def analyze_citation_dynamics(self) -> Dict:
        """Citation dynamics: yearly, cumulative, network"""
        # Yearly dynamics
        yearly_citations = defaultdict(lambda: defaultdict(int))
        # For cumulative
        pub_years = {pub.id: pub.publication_year for pub in self.publications}
        
        for pub_id, citing_list in self.citations.items():
            pub_year = pub_years.get(pub_id, 0)
            for citing in citing_list:
                citing_year = citing.citing_year
                if citing_year > 0 and pub_year > 0:
                    yearly_citations[pub_year][citing_year] += 1
        
        # Prepare network data for heatmap
        network_data = []
        pub_years_set = sorted(set(pub_years.values()))
        all_citation_years = set()
        
        for pub_year, cites in yearly_citations.items():
            for citing_year, count in cites.items():
                all_citation_years.add(citing_year)
                network_data.append({
                    'publication_year': pub_year,
                    'citation_year': citing_year,
                    'citations_count': count
                })
        
        all_years = sorted(pub_years_set | all_citation_years)
        
        # Cumulative dynamics
        cumulative = {}
        running_total = 0
        for year in all_years:
            year_total = sum(yearly_citations.get(y, {}).get(year, 0) for y in pub_years_set)
            running_total += year_total
            cumulative[year] = running_total
        
        return {
            'yearly_citations': yearly_citations,
            'cumulative_citations': cumulative,
            'network_data': network_data,
            'all_years': all_years
        }
    
    def analyze_citing_works(self) -> Dict:
        """Analyze citing works"""
        # Collect stats
        authors = Counter()
        affiliations = Counter()
        countries = Counter()
        journals = Counter()
        publishers = Counter()
        
        for citing in self.citing_works:
            for author in citing.citing_authors:
                if author.display_name:
                    authors[author.display_name] += 1
            
            for aff in citing.citing_affiliations:
                if aff:
                    affiliations[aff] += 1
            
            for country in citing.citing_countries:
                if country:
                    countries[country] += 1
            
            if citing.citing_journal:
                journals[citing.citing_journal] += 1
            
            if citing.citing_publisher:
                publishers[citing.citing_publisher] += 1
        
        return {
            'total_citing_works': len(self.citing_works),
            'unique_citing_authors': len(authors),
            'unique_citing_affiliations': len(affiliations),
            'unique_citing_countries': len(countries),
            'unique_citing_journals': len(journals),
            'unique_citing_publishers': len(publishers),
            'top_authors': [{'name': k, 'count': v} for k, v in authors.most_common(30)],
            'top_affiliations': [{'name': k, 'count': v} for k, v in affiliations.most_common(30)],
            'top_countries': [{'name': k, 'count': v} for k, v in countries.most_common(30)],
            'top_journals': [{'name': k, 'count': v} for k, v in journals.most_common(30)],
            'top_publishers': [{'name': k, 'count': v} for k, v in publishers.most_common(30)]
        }
    
    def analyze_topics(self) -> Dict:
        """Analyze topics, fields, subfields, domains, concepts"""
        # For analyzed publications
        analyzed_topics = defaultdict(lambda: {
            'count': 0,
            'first_year': float('inf'),
            'peak_year': 0,
            'peak_count': 0,
            'recent_5_count': 0,
            'years': []
        })
        
        current_year = datetime.now().year
        recent_5_years = set(range(current_year - 4, current_year + 1))
        
        # Process analyzed publications
        for pub in self.publications:
            year = pub.publication_year
            for topic in pub.topics:
                if topic.display_name:
                    stats = analyzed_topics[topic.display_name]
                    stats['count'] += 1
                    if year < stats['first_year']:
                        stats['first_year'] = year
                    stats['years'].append(year)
                    if year in recent_5_years:
                        stats['recent_5_count'] += 1
        
        # Process citing works
        citing_topics = defaultdict(lambda: {
            'count': 0,
            'first_year': float('inf'),
            'peak_year': 0,
            'peak_count': 0,
            'recent_5_count': 0,
            'years': []
        })
        
        for citing in self.citing_works:
            year = citing.citing_year
            for topic in citing.citing_topics:
                if topic.display_name:
                    stats = citing_topics[topic.display_name]
                    stats['count'] += 1
                    if year < stats['first_year']:
                        stats['first_year'] = year
                    stats['years'].append(year)
                    if year in recent_5_years:
                        stats['recent_5_count'] += 1
        
        # Combine and calculate peak years
        all_topics = set(analyzed_topics.keys()) | set(citing_topics.keys())
        combined_stats = []
        
        for topic_name in all_topics:
            a_stats = analyzed_topics.get(topic_name, {'count': 0, 'first_year': float('inf'), 'years': []})
            c_stats = citing_topics.get(topic_name, {'count': 0, 'first_year': float('inf'), 'years': []})
            
            # Calculate peak year
            all_years = a_stats.get('years', []) + c_stats.get('years', [])
            if all_years:
                year_counts = Counter(all_years)
                peak_year, peak_count = year_counts.most_common(1)[0]
            else:
                peak_year = 0
                peak_count = 0
            
            # Calculate total norm count (normalized by total publications/citing works)
            total_pubs = len(self.publications) or 1
            total_citing = len(self.citing_works) or 1
            
            combined_stats.append({
                'topic': topic_name,
                'analyzed_count': a_stats['count'],
                'citing_count': c_stats['count'],
                'analyzed_norm_count': a_stats['count'] / total_pubs,
                'citing_norm_count': c_stats['count'] / total_citing,
                'total_norm_count': (a_stats['count'] + c_stats['count']) / (total_pubs + total_citing),
                'first_year': a_stats['first_year'] if a_stats['first_year'] != float('inf') else 0,
                'peak_year': peak_year,
                'recent_5_years_count': a_stats.get('recent_5_count', 0) + c_stats.get('recent_5_count', 0)
            })
        
        # Sort by total norm count
        combined_stats.sort(key=lambda x: x['total_norm_count'], reverse=True)
        
        # Separate by type
        topics = [s for s in combined_stats[:20]]
        
        return {
            'top_topics': topics,
            'total_analyzed_topics': len(analyzed_topics),
            'total_citing_topics': len(citing_topics)
        }
    
    def get_detailed_citations(self) -> Dict:
        """Get detailed citations for each publication"""
        detailed = {}
        
        # Sort publications by year (newest first)
        sorted_pubs = sorted(self.publications, key=lambda x: x.publication_year, reverse=True)
        
        for pub in sorted_pubs:
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
                
                author_names = [a.display_name for a in pub.authors if a.display_name]
                detailed[pub.id] = {
                    'title': pub.title,
                    'year': pub.publication_year,
                    'doi': pub.doi,
                    'total_citations': len(citations_list),
                    'citations': citations_list,
                    'authors': author_names,
                    'journal': pub.journal_name
                }
        
        return detailed
    
    def get_all_publications(self) -> List[Dict]:
        """Get all publications for filtering"""
        result = []
        for pub in self.publications:
            author_names = [a.display_name for a in pub.authors if a.display_name]
            result.append({
                'id': pub.id,
                'title': pub.title,
                'year': pub.publication_year,
                'citations': pub.cited_by_count,
                'citations_per_year': pub.citations_per_year,
                'journal': pub.journal_name,
                'doi': pub.doi,
                'authors': author_names,
                'authors_str': ', '.join(author_names),
                'countries': list(set(c for a in pub.authors for c in a.countries if c)),
                'open_access': pub.is_open_access
            })
        
        return sorted(result, key=lambda x: x['year'], reverse=True)
    
    def calculate_citation_velocity(self) -> Dict:
        """Calculate citation velocity for each publication"""
        velocities = {}
        current_year = datetime.now().year
        
        for pub in self.publications:
            age = current_year - pub.publication_year
            if age > 0:
                velocity = pub.cited_by_count / age
            else:
                velocity = pub.cited_by_count  # Current year
            
            # Categories
            if velocity >= 10:
                category = get_text('very_high')
            elif velocity >= 5:
                category = get_text('high')
            elif velocity >= 1:
                category = get_text('medium')
            else:
                category = get_text('low')
            
            velocities[pub.id] = {
                'title': pub.title,
                'year': pub.publication_year,
                'citations': pub.cited_by_count,
                'velocity': velocity,
                'category': category,
                'age': age
            }
        
        return velocities

# ======================== HTML REPORT GENERATOR ========================

def generate_html_report(data: JournalData, metrics: Dict, lang: str = 'en', primary_color: str = '#667eea', secondary_color: str = '#f39c12') -> str:
    """
    Generate comprehensive HTML report with all sections
    """
    
    def get_text_local(key: str) -> str:
        """Get localized text for HTML report"""
        if lang == 'ru' and key in TEXTS['ru']:
            return TEXTS['ru'][key]
        elif key in TEXTS['en']:
            return TEXTS['en'][key]
        else:
            return key
    
    # Prepare data
    overview = metrics['overview']
    most_cited = metrics['most_cited']
    authors_data = metrics['authors']
    geography = metrics['geography']
    citation_dynamics = metrics['citation_dynamics']
    citing_works = metrics['citing_works']
    topics_data = metrics['topics']
    detailed_citations = metrics['detailed_citations']
    all_publications = metrics['all_publications']
    citation_velocity = metrics.get('citation_velocity', {})
    
    # Current date
    current_date = datetime.now().strftime('%d.%m.%Y')
    
    # Build CSS with theme
    theme_css = f"""
    <style>
        :root {{
            --primary: {primary_color};
            --secondary: {secondary_color};
            --primary-light: {get_gradient_colors(primary_color, 1)[0]};
            --secondary-light: {get_gradient_colors(secondary_color, 1)[0]};
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            background: #f5f7fa;
            color: #333;
        }}
        
        .main-content {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .section {{
            background: white;
            border-radius: 12px;
            padding: 25px;
            margin-bottom: 30px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        
        .section-title {{
            font-size: 24px;
            font-weight: 600;
            color: var(--primary);
            border-bottom: 3px solid var(--primary);
            padding-bottom: 10px;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .section-title .icon {{
            font-size: 28px;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }}
        
        .stat-card {{
            background: #f8f9fa;
            border-radius: 10px;
            padding: 15px;
            text-align: center;
            border: 1px solid #e9ecef;
        }}
        
        .stat-number {{
            font-size: 32px;
            font-weight: bold;
            color: var(--primary);
        }}
        
        .stat-percent {{
            font-size: 14px;
            color: #666;
        }}
        
        .stat-label {{
            font-size: 12px;
            color: #666;
            margin-top: 5px;
        }}
        
        .rank-item {{
            background: #f8f9fa;
            border-radius: 8px;
            padding: 12px 15px;
            margin-bottom: 8px;
            border-left: 3px solid var(--primary);
        }}
        
        .rank-number {{
            font-weight: bold;
            color: var(--primary);
            margin-right: 10px;
        }}
        
        .rank-name {{
            font-weight: 500;
        }}
        
        .rank-count {{
            float: right;
            color: #666;
            font-size: 13px;
        }}
        
        .progress-bar {{
            background: #e9ecef;
            border-radius: 6px;
            height: 6px;
            margin-top: 6px;
            overflow: hidden;
        }}
        
        .progress-fill {{
            background: linear-gradient(90deg, var(--primary), var(--secondary));
            height: 100%;
            border-radius: 6px;
            transition: width 0.5s;
        }}
        
        .badge {{
            display: inline-block;
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 600;
            margin: 2px;
        }}
        
        .badge-success {{
            background: #d4edda;
            color: #155724;
        }}
        
        .badge-warning {{
            background: #fff3cd;
            color: #856404;
        }}
        
        .badge-info {{
            background: #d1ecf1;
            color: #0c5460;
        }}
        
        .badge-primary {{
            background: var(--primary);
            color: white;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
        }}
        
        thead {{
            background: var(--primary);
            color: white;
        }}
        
        th {{
            padding: 10px 12px;
            text-align: left;
            cursor: pointer;
            user-select: none;
        }}
        
        th:hover {{
            opacity: 0.8;
        }}
        
        td {{
            padding: 8px 12px;
            border-bottom: 1px solid #e9ecef;
        }}
        
        tr:hover {{
            background: #f8f9fa;
        }}
        
        .clickable-link {{
            color: var(--primary);
            text-decoration: none;
        }}
        
        .clickable-link:hover {{
            text-decoration: underline;
        }}
        
        .doi-link {{
            color: var(--primary);
            text-decoration: none;
            font-size: 12px;
        }}
        
        .doi-link:hover {{
            text-decoration: underline;
        }}
        
        .citation-count {{
            background: var(--primary);
            color: white;
            padding: 2px 10px;
            border-radius: 12px;
            font-size: 11px;
            margin-left: 8px;
        }}
        
        .collapser {{
            background: #f8f9fa;
            padding: 12px 15px;
            border-radius: 8px;
            cursor: pointer;
            margin-bottom: 8px;
            transition: background 0.2s;
            border-left: 3px solid var(--primary);
        }}
        
        .collapser:hover {{
            background: #e9ecef;
        }}
        
        .citation-detail {{
            background: white;
            padding: 12px 15px;
            margin: 5px 0 5px 20px;
            border-radius: 6px;
            border-left: 2px solid #ddd;
            font-size: 13px;
        }}
        
        .citation-detail .cite-meta {{
            font-size: 12px;
            color: #666;
            margin-top: 4px;
        }}
        
        .filter-section {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
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
            color: #666;
            margin-bottom: 4px;
        }}
        
        .filter-row select, .filter-row input {{
            width: 100%;
            padding: 6px 10px;
            border: 1px solid #ddd;
            border-radius: 6px;
            font-size: 13px;
        }}
        
        .filter-row select:focus, .filter-row input:focus {{
            outline: none;
            border-color: var(--primary);
            box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
        }}
        
        .footer-text {{
            text-align: center;
            padding: 20px;
            color: #666;
            font-size: 12px;
            margin-top: 40px;
            border-top: 1px solid #e0e0e0;
        }}
        
        .word-wrap {{
            word-break: break-word;
            max-width: 300px;
        }}
        
        .table-container {{
            overflow-x: auto;
            max-height: 800px;
            overflow-y: auto;
        }}
        
        .concepts-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 10px;
        }}
        
        .concept-card {{
            background: #f8f9fa;
            border-radius: 8px;
            padding: 12px;
            text-align: center;
            border: 1px solid #e9ecef;
        }}
        
        .concept-name {{
            font-weight: 600;
            color: var(--primary);
        }}
        
        .concept-score {{
            font-size: 12px;
            color: #666;
            margin-top: 4px;
        }}
        
        .header {{
            text-align: center;
            padding: 20px;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: white;
            border-radius: 12px;
            margin-bottom: 30px;
        }}
        
        .header h1 {{
            margin: 0;
            font-size: 28px;
        }}
        
        .header .subtitle {{
            font-size: 16px;
            opacity: 0.9;
        }}
        
        .header .meta {{
            font-size: 13px;
            opacity: 0.8;
            margin-top: 10px;
        }}
        
        .date {{
            font-size: 13px;
            color: #666;
            text-align: right;
            margin-top: 10px;
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
        
        .reviewer-card {{
            background: white;
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 16px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            border-left: 4px solid var(--primary);
        }}
        
        .reviewer-name {{
            font-size: 18px;
            font-weight: 600;
            color: var(--primary);
        }}
        
        .reviewer-orcid {{
            font-family: monospace;
            font-size: 12px;
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
        
        @media print {{
            .section {{
                box-shadow: none;
                border: 1px solid #ddd;
            }}
            .header {{
                -webkit-print-color-adjust: exact;
                print-color-adjust: exact;
            }}
            .progress-fill {{
                -webkit-print-color-adjust: exact;
                print-color-adjust: exact;
            }}
        }}
    </style>
    """
    
    # Build filter HTML
    year_options = sorted(set(p['year'] for p in all_publications if p['year']), reverse=True)
    year_filter_html = ''.join([f'<option value="{y}">{y}</option>' for y in year_options])
    
    # Build all publications table
    publications_table = ''
    for i, pub in enumerate(all_publications, 1):
        pub_id_escaped = pub['id'].replace('https://openalex.org/', '')
        publications_table += f"""
        <tr data-year="{pub['year']}" data-authors="{pub['authors_str'].lower()}" data-citations="{pub['citations']}" data-title="{pub['title'].lower()}" data-doi="{pub['doi'].lower()}">
            <td>{i}</td>
            <td class="word-wrap">{html.escape(pub['title'][:200])}</td>
            <td>{pub['year']}</td>
            <td><span class="citation-count">{pub['citations']}</span></td>
            <td>{pub['citations_per_year']:.1f}</td>
            <td>{html.escape(pub['journal'])}</td>
            <td><a href="https://doi.org/{pub['doi']}" target="_blank" class="doi-link">{pub['doi']}</a></td>
            <td>
                <button onclick="toggleCitations('{pub_id_escaped}')" style="padding: 3px 8px; border: none; border-radius: 4px; background: {primary_color}; color: white; cursor: pointer; font-size: 11px;">
                    {get_text_local('show_citations')}
                </button>
            </td>
        </tr>
        """
    
    # Build detailed citations
    detailed_citations_html = ''
    for pub_id, data in detailed_citations.items():
        pub_id_escaped = pub_id.replace('https://openalex.org/', '')
        author_names = ', '.join(data.get('authors', []))
        
        citations_content = ''
        for cite in data.get('citations', []):
            author_list = ', '.join(cite.get('citing_authors', []))
            country_list = ', '.join(cite.get('citing_countries', []))
            topic_list = ', '.join(cite.get('citing_topics', [])[:3])
            
            citations_content += f"""
            <div class="citation-detail">
                <div><strong>{html.escape(cite.get('citing_title', 'Unknown title'))}</strong></div>
                <div class="cite-meta">
                    <strong>{get_text_local('citing_journal')}:</strong> {html.escape(cite.get('citing_journal', 'Unknown'))} | 
                    <strong>{get_text_local('citing_year')}:</strong> {cite.get('citing_year', 'N/A')} | 
                    <strong>{get_text_local('citing_date')}:</strong> {cite.get('citing_date', 'N/A')} |
                    <strong>{get_text_local('citation_lag')}:</strong> {cite.get('citation_lag', 0)} years
                </div>
                <div class="cite-meta">
                    <strong>{get_text_local('authors')}:</strong> {author_list} |
                    <strong>{get_text_local('countries')}:</strong> {country_list} |
                    <strong>{get_text_local('topics')}:</strong> {topic_list}
                </div>
                <div class="cite-meta">
                    <a href="https://doi.org/{cite.get('citing_doi', '')}" target="_blank" class="doi-link">DOI: {cite.get('citing_doi', '')}</a>
                </div>
            </div>
            """
        
        if data.get('total_citations', 0) > 0:
            detailed_citations_html += f"""
            <div class="collapser" onclick="toggleCitations('{pub_id_escaped}')">
                <strong>{html.escape(data.get('title', 'Unknown title'))}</strong>
                <span class="badge badge-info">{data.get('year', 'N/A')}</span>
                <span class="citation-count">{data.get('total_citations', 0)} {get_text_local('citations')}</span>
                <span style="font-size: 12px; color: #666; margin-left: 10px;">{get_text_local('authors')}: {author_names[:100]}</span>
                <span style="float: right; font-size: 12px; color: #666;">{get_text_local('click_to_toggle')}</span>
            </div>
            <div id="citations_{pub_id_escaped}" style="display: none;">
                {citations_content}
            </div>
            """
    
    # Build most cited table
    most_cited_table = ''
    for pub in most_cited:
        most_cited_table += f"""
        <tr>
            <td>{pub['rank']}</td>
            <td class="word-wrap">{html.escape(pub['title'][:200])}</td>
            <td>{pub['year']}</td>
            <td><span class="citation-count">{pub['citations']}</span></td>
            <td>{pub['citations_per_year']:.1f}</td>
            <td>{html.escape(pub['authors'])}</td>
            <td><a href="https://doi.org/{pub['doi']}" target="_blank" class="doi-link">{pub['doi']}</a></td>
        </tr>
        """
    
    # Build author table
    author_table = ''
    for i, author in enumerate(authors_data['top_authors'][:30], 1):
        orcid_link = f'<a href="{author["orcid"]}" target="_blank" class="clickable-link">ORCID</a>' if author['orcid'] else ''
        aff_str = ', '.join(author['affiliations'][:3])
        if len(author['affiliations']) > 3:
            aff_str += f' +{len(author["affiliations"])-3} more'
        
        author_table += f"""
        <tr>
            <td>{i}</td>
            <td><strong>{html.escape(author['display_name'])}</strong> {orcid_link}</td>
            <td>{html.escape(aff_str)}</td>
            <td>{author['publication_count']}</td>
            <td>{author['citation_count']}</td>
        </tr>
        """
    
    # Build geography sections
    geo_type1 = ''
    for country, count in list(geography['type1_unique_countries_per_publication'].items())[:15]:
        geo_type1 += f"""
        <div class="rank-item">
            <span class="rank-name">{html.escape(country)}</span>
            <span class="rank-count">{count} {get_text_local('publications')}</span>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {count / max(geography['type1_unique_countries_per_publication'].values()) * 100 if geography['type1_unique_countries_per_publication'] else 0}%;"></div>
            </div>
        </div>
        """
    
    geo_type2 = ''
    for country, count in list(geography['type2_authors_per_country'].items())[:15]:
        geo_type2 += f"""
        <div class="rank-item">
            <span class="rank-name">{html.escape(country)}</span>
            <span class="rank-count">{count} {get_text_local('authors')}</span>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {count / max(geography['type2_authors_per_country'].values()) * 100 if geography['type2_authors_per_country'] else 0}%;"></div>
            </div>
        </div>
        """
    
    geo_couples = ''
    for couple in geography['collaboration_couples'][:15]:
        geo_couples += f"""
        <div class="rank-item">
            <span class="rank-name">{html.escape(couple['country1'])} + {html.escape(couple['country2'])}</span>
            <span class="rank-count">{couple['count']} {get_text_local('works')}</span>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {couple['count'] / max([c['count'] for c in geography['collaboration_couples']]) * 100 if geography['collaboration_couples'] else 0}%;"></div>
            </div>
        </div>
        """
    
    # Build citation network heatmap
    network_heatmap = ''
    all_years = citation_dynamics['all_years']
    if all_years:
        network_heatmap = '<table style="font-size: 11px; border-collapse: collapse;">'
        network_heatmap += '<thead><tr><th style="padding: 4px 8px;">Pub Year</th>'
        for cyear in all_years:
            network_heatmap += f'<th style="padding: 4px 8px;">{cyear}</th>'
        network_heatmap += '</tr></thead><tbody>'
        
        yearly_cites = citation_dynamics['yearly_citations']
        max_count = 0
        for pub_year, cites in yearly_cites.items():
            for count in cites.values():
                if count > max_count:
                    max_count = count
        
        for pyear in sorted(yearly_cites.keys()):
            network_heatmap += f'<tr><td style="padding: 4px 8px; font-weight: bold;">{pyear}</td>'
            for cyear in all_years:
                count = yearly_cites.get(pyear, {}).get(cyear, 0)
                if count > 0:
                    intensity = min(255, int(100 + (count / max_count) * 155)) if max_count > 0 else 100
                    network_heatmap += f'<td style="padding: 4px 8px; text-align: center; background: rgba({int(intensity*0.6)}, {int(intensity*0.4)}, 255, 0.6);">{count}</td>'
                else:
                    network_heatmap += '<td style="padding: 4px 8px; text-align: center; color: #ccc;">0</td>'
            network_heatmap += '</tr>'
        network_heatmap += '</tbody></table>'
    
    # Build citing works tables
    citing_authors_table = ''
    for i, item in enumerate(citing_works['top_authors'][:30], 1):
        citing_authors_table += f"""
        <tr><td>{i}</td><td>{html.escape(item['name'])}</td><td>{item['count']}</td></tr>
        """
    
    citing_affiliations_table = ''
    for i, item in enumerate(citing_works['top_affiliations'][:30], 1):
        citing_affiliations_table += f"""
        <tr><td>{i}</td><td>{html.escape(item['name'])}</td><td>{item['count']}</td></tr>
        """
    
    citing_countries_table = ''
    for i, item in enumerate(citing_works['top_countries'][:30], 1):
        citing_countries_table += f"""
        <tr><td>{i}</td><td>{html.escape(item['name'])}</td><td>{item['count']}</td></tr>
        """
    
    citing_journals_table = ''
    for i, item in enumerate(citing_works['top_journals'][:30], 1):
        citing_journals_table += f"""
        <tr><td>{i}</td><td>{html.escape(item['name'])}</td><td>{item['count']}</td></tr>
        """
    
    citing_publishers_table = ''
    for i, item in enumerate(citing_works['top_publishers'][:30], 1):
        citing_publishers_table += f"""
        <tr><td>{i}</td><td>{html.escape(item['name'])}</td><td>{item['count']}</td></tr>
        """
    
    # Build topics tables
    topics_table = ''
    for i, item in enumerate(topics_data['top_topics'][:20], 1):
        topics_table += f"""
        <tr>
            <td>{i}</td>
            <td>{html.escape(item['topic'])}</td>
            <td>{item['analyzed_count']}</td>
            <td>{item['citing_count']}</td>
            <td>{item['analyzed_norm_count']:.3f}</td>
            <td>{item['citing_norm_count']:.3f}</td>
            <td>{item['total_norm_count']:.3f}</td>
            <td>{item['first_year']}</td>
            <td>{item['peak_year']}</td>
            <td>{item['recent_5_years_count']}</td>
        </tr>
        """
    
    # Build citation velocity section
    velocity_table = ''
    sorted_velocity = sorted(citation_velocity.values(), key=lambda x: x['velocity'], reverse=True)
    for i, item in enumerate(sorted_velocity[:30], 1):
        velocity_table += f"""
        <tr>
            <td>{i}</td>
            <td class="word-wrap">{html.escape(item['title'][:150])}</td>
            <td>{item['year']}</td>
            <td>{item['citations']}</td>
            <td>{item['velocity']:.1f}</td>
            <td><span class="badge badge-{('success' if item['category'] == get_text_local('very_high') else 'warning' if item['category'] == get_text_local('high') else 'info' if item['category'] == get_text_local('medium') else '')}">{item['category']}</span></td>
            <td>{item['age']}</td>
        </tr>
        """
    
    # Build OA breakdown
    oa = overview['open_access_breakdown']
    oa_html = ''
    for oa_type, count in oa.items():
        if oa_type != 'unknown' or count > 0:
            label = get_text_local(oa_type)
            oa_html += f"""
            <div class="rank-item">
                <span class="rank-name">{label}</span>
                <span class="rank-count">{count} ({count/overview['total_publications']*100 if overview['total_publications'] > 0 else 0:.1f}%)</span>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {count/overview['total_publications']*100 if overview['total_publications'] > 0 else 0}%;"></div>
                </div>
            </div>
            """
    
    # Build full HTML
    html_content = f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{get_text_local('app_title')}</title>
    {theme_css}
    <script>
        function toggleCitations(id) {{
            const element = document.getElementById('citations_' + id);
            if (element) {{
                element.style.display = element.style.display === 'none' ? 'block' : 'none';
            }}
        }}
        
        function filterPublications() {{
            const year = document.getElementById('yearFilter').value;
            const author = document.getElementById('authorFilter').value.toLowerCase();
            const minCitations = parseInt(document.getElementById('citationFilter').value) || 0;
            const search = document.getElementById('searchInput').value.toLowerCase();
            
            const rows = document.querySelectorAll('#publicationsTable tbody tr');
            let visible = 0;
            
            rows.forEach(row => {{
                let show = true;
                const rowYear = row.dataset.year;
                const rowAuthors = row.dataset.authors;
                const rowCitations = parseInt(row.dataset.citations);
                const rowTitle = row.dataset.title;
                const rowDoi = row.dataset.doi;
                
                if (year && rowYear != year) show = false;
                if (author && !rowAuthors.includes(author)) show = false;
                if (rowCitations < minCitations) show = false;
                if (search && !rowTitle.includes(search) && !rowDoi.includes(search)) show = false;
                
                row.style.display = show ? '' : 'none';
                if (show) visible++;
            }});
            
            document.getElementById('visibleCount').textContent = '{get_text_local("showing_publications").replace("{0}", "")}' + visible + ' publications';
        }}
        
        function sortTable(column) {{
            const table = document.getElementById('publicationsTable');
            const tbody = table.querySelector('tbody');
            const rows = Array.from(tbody.querySelectorAll('tr'));
            
            const isNumeric = column === 2 || column === 3 || column === 4;
            
            rows.sort((a, b) => {{
                let aVal, bVal;
                if (column === 0) {{
                    aVal = parseInt(a.cells[0].textContent);
                    bVal = parseInt(b.cells[0].textContent);
                }} else if (column === 1) {{
                    aVal = a.cells[1].textContent.toLowerCase();
                    bVal = b.cells[1].textContent.toLowerCase();
                }} else if (column === 2) {{
                    aVal = parseInt(a.cells[2].textContent);
                    bVal = parseInt(b.cells[2].textContent);
                }} else if (column === 3) {{
                    aVal = parseInt(a.cells[3].textContent);
                    bVal = parseInt(b.cells[3].textContent);
                }} else if (column === 4) {{
                    aVal = parseFloat(a.cells[4].textContent);
                    bVal = parseFloat(b.cells[4].textContent);
                }} else if (column === 5) {{
                    aVal = a.cells[5].textContent.toLowerCase();
                    bVal = b.cells[5].textContent.toLowerCase();
                }} else {{
                    return 0;
                }}
                
                if (isNumeric) {{
                    return bVal - aVal;
                }} else {{
                    if (aVal < bVal) return -1;
                    if (aVal > bVal) return 1;
                    return 0;
                }}
            }});
            
            rows.forEach(row => tbody.appendChild(row));
            
            // Update ranks
            rows.forEach((row, index) => {{
                row.cells[0].textContent = index + 1;
            }});
        }}
    </script>
</head>
<body>
    <div class="main-content">
        <!-- Header -->
        <div class="header">
            <h1>📚 {get_text_local('app_title')}</h1>
            <div class="subtitle">{get_text_local('app_subtitle')}</div>
            <div class="meta">
                ISSN: {html.escape(st.session_state.get('issn', 'N/A'))} | 
                Period: {html.escape(st.session_state.get('period', 'N/A'))} | 
                {get_text_local('html_generated')}: {current_date}
            </div>
        </div>
        
        <!-- 1. OVERVIEW SECTION -->
        <div id="overview" class="section">
            <div class="section-title"><span class="icon">📊</span> {get_text_local('overview')}</div>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">{overview['total_publications']}</div>
                    <div class="stat-label">{get_text_local('total_publications')}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{overview['total_citations']}</div>
                    <div class="stat-label">{get_text_local('total_citations')}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{overview['h_index']}</div>
                    <div class="stat-label">{get_text_local('h_index')}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{overview['g_index']}</div>
                    <div class="stat-label">{get_text_local('g_index')}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{overview['i10_index']}</div>
                    <div class="stat-label">{get_text_local('i10_index')}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{overview['i100_index']}</div>
                    <div class="stat-label">{get_text_local('i100_index')}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{overview['avg_citations']:.1f}</div>
                    <div class="stat-label">{get_text_local('avg_citations')}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{overview['open_access_percent']:.1f}%</div>
                    <div class="stat-label">{get_text_local('open_access')}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{overview['active_years']}</div>
                    <div class="stat-label">{get_text_local('active_years')}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{overview['unique_authors']}</div>
                    <div class="stat-label">{get_text_local('unique_authors')}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{overview['unique_countries']}</div>
                    <div class="stat-label">{get_text_local('unique_countries')}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{overview['total_citing_works']}</div>
                    <div class="stat-label">{get_text_local('total_citing_works')}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{overview['unique_citing_journals']}</div>
                    <div class="stat-label">{get_text_local('unique_citing_journals')}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{overview['avg_authors_per_paper']:.1f}</div>
                    <div class="stat-label">{get_text_local('avg_authors_per_paper')}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{overview['avg_affiliations_per_paper']:.1f}</div>
                    <div class="stat-label">{get_text_local('avg_affiliations_per_paper')}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{overview['avg_countries_per_paper']:.1f}</div>
                    <div class="stat-label">{get_text_local('avg_countries_per_paper')}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{overview['international_collaboration_rate']:.1f}%</div>
                    <div class="stat-label">{get_text_local('international_collaboration_rate')}</div>
                </div>
            </div>
            
            <!-- Open Access Breakdown -->
            <h4 style="margin-top: 20px;">{get_text_local('open_access_breakdown')}</h4>
            {oa_html}
        </div>
        
        <!-- 2. MOST CITED PUBLICATIONS -->
        <div id="most_cited" class="section">
            <div class="section-title"><span class="icon">🏆</span> {get_text_local('most_cited_publications')}</div>
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>{get_text_local('rank')}</th>
                            <th>{get_text_local('title')}</th>
                            <th>{get_text_local('year')}</th>
                            <th>{get_text_local('citations')}</th>
                            <th>{get_text_local('citations_per_year')}</th>
                            <th>{get_text_local('authors')}</th>
                            <th>DOI</th>
                        </tr>
                    </thead>
                    <tbody>
                        {most_cited_table}
                    </tbody>
                </table>
            </div>
        </div>
        
        <!-- 3. AUTHOR ANALYSIS -->
        <div id="authors" class="section">
            <div class="section-title"><span class="icon">👨‍🎓</span> {get_text_local('author_analysis')}</div>
            <h4>{get_text_local('top_authors')}</h4>
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>{get_text_local('rank')}</th>
                            <th>{get_text_local('author')}</th>
                            <th>{get_text_local('affiliations')}</th>
                            <th>{get_text_local('publication_count')}</th>
                            <th>{get_text_local('citation_count')}</th>
                        </tr>
                    </thead>
                    <tbody>
                        {author_table}
                    </tbody>
                </table>
            </div>
        </div>
        
        <!-- GEOGRAPHIC ANALYSIS -->
        <div id="geography" class="section">
            <div class="section-title"><span class="icon">🌍</span> {get_text_local('geographic_analysis')}</div>
            
            <h4>{get_text_local('geography_type_1')}</h4>
            <p style="font-size: 12px; color: #666; margin-bottom: 10px;">{get_text_local('geography_type_1_desc')}</p>
            {geo_type1}
            
            <h4 style="margin-top: 20px;">{get_text_local('geography_type_2')}</h4>
            <p style="font-size: 12px; color: #666; margin-bottom: 10px;">{get_text_local('geography_type_2_desc')}</p>
            {geo_type2}
            
            <h4 style="margin-top: 20px;">{get_text_local('geography_type_3')}</h4>
            <p style="font-size: 12px; color: #666; margin-bottom: 10px;">{get_text_local('geography_type_3_desc')}</p>
            <div style="display: flex; gap: 20px; margin-bottom: 15px;">
                <div><strong>{get_text_local('single_country')}:</strong> {geography.get('single_country_count', 0)}</div>
                <div><strong>{get_text_local('international_collaboration')}:</strong> {geography.get('international_count', 0)}</div>
            </div>
            
            <h4 style="margin-top: 20px;">{get_text_local('collaboration_couples')}</h4>
            {geo_couples}
        </div>
        
        <!-- 4. CITATION ANALYSIS -->
        <div id="citation_analysis" class="section">
            <div class="section-title"><span class="icon">📈</span> {get_text_local('citation_analysis')}</div>
            
            <h4>{get_text_local('yearly_citation_dynamics')}</h4>
            <div style="overflow-x: auto;">
                <table style="font-size: 12px;">
                    <thead>
                        <tr>
                            <th>{get_text_local('publication_year')}</th>
                            <th>{get_text_local('citation_year')}</th>
                            <th>{get_text_local('citations_count')}</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join([
                            f'<tr><td>{item["publication_year"]}</td><td>{item["citation_year"]}</td><td>{item["citations_count"]}</td></tr>'
                            for item in citation_dynamics['network_data'][:50]
                        ])}
                    </tbody>
                </table>
            </div>
            
            <h4 style="margin-top: 20px;">{get_text_local('citation_network')}</h4>
            {network_heatmap if network_heatmap else '<p>No citation network data available</p>'}
        </div>
        
        <!-- 5. CITING WORKS ANALYSIS -->
        <div id="citing_works" class="section">
            <div class="section-title"><span class="icon">🔗</span> {get_text_local('citing_works_analysis')}</div>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">{citing_works['total_citing_works']}</div>
                    <div class="stat-label">{get_text_local('total_citing_works')}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{citing_works['unique_citing_authors']}</div>
                    <div class="stat-label">{get_text_local('unique_citing_authors')}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{citing_works['unique_citing_affiliations']}</div>
                    <div class="stat-label">{get_text_local('unique_citing_affiliations')}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{citing_works['unique_citing_countries']}</div>
                    <div class="stat-label">{get_text_local('unique_citing_countries')}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{citing_works['unique_citing_journals']}</div>
                    <div class="stat-label">{get_text_local('unique_citing_journals')}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{citing_works['unique_citing_publishers']}</div>
                    <div class="stat-label">{get_text_local('unique_citing_publishers')}</div>
                </div>
            </div>
            
            <h4>{get_text_local('top_citing_authors')}</h4>
            <div class="table-container">
                <table>
                    <thead><tr><th>{get_text_local('rank')}</th><th>Author</th><th>{get_text_local('count')}</th></tr></thead>
                    <tbody>{citing_authors_table}</tbody>
                </table>
            </div>
            
            <h4 style="margin-top: 20px;">{get_text_local('top_citing_affiliations')}</h4>
            <div class="table-container">
                <table>
                    <thead><tr><th>{get_text_local('rank')}</th><th>Affiliation</th><th>{get_text_local('count')}</th></tr></thead>
                    <tbody>{citing_affiliations_table}</tbody>
                </table>
            </div>
            
            <h4 style="margin-top: 20px;">{get_text_local('top_citing_countries')}</h4>
            <div class="table-container">
                <table>
                    <thead><tr><th>{get_text_local('rank')}</th><th>Country</th><th>{get_text_local('count')}</th></tr></thead>
                    <tbody>{citing_countries_table}</tbody>
                </table>
            </div>
            
            <h4 style="margin-top: 20px;">{get_text_local('top_citing_journals')}</h4>
            <div class="table-container">
                <table>
                    <thead><tr><th>{get_text_local('rank')}</th><th>Journal</th><th>{get_text_local('count')}</th></tr></thead>
                    <tbody>{citing_journals_table}</tbody>
                </table>
            </div>
            
            <h4 style="margin-top: 20px;">{get_text_local('top_citing_publishers')}</h4>
            <div class="table-container">
                <table>
                    <thead><tr><th>{get_text_local('rank')}</th><th>Publisher</th><th>{get_text_local('count')}</th></tr></thead>
                    <tbody>{citing_publishers_table}</tbody>
                </table>
            </div>
        </div>
        
        <!-- 6. TOPICS ANALYSIS -->
        <div id="topics" class="section">
            <div class="section-title"><span class="icon">🧠</span> {get_text_local('topics_analysis')}</div>
            
            <h4>{get_text_local('top_topics')}</h4>
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>{get_text_local('rank')}</th>
                            <th>{get_text_local('topic')}</th>
                            <th>{get_text_local('analyzed_count')}</th>
                            <th>{get_text_local('citing_count')}</th>
                            <th>{get_text_local('analyzed_norm_count')}</th>
                            <th>{get_text_local('citing_norm_count')}</th>
                            <th>{get_text_local('total_norm_count')}</th>
                            <th>{get_text_local('first_year')}</th>
                            <th>{get_text_local('peak_year')}</th>
                            <th>{get_text_local('recent_5_years_count')}</th>
                        </tr>
                    </thead>
                    <tbody>
                        {topics_table}
                    </tbody>
                </table>
            </div>
        </div>
        
        <!-- CITATION VELOCITY -->
        <div id="citation_velocity" class="section">
            <div class="section-title"><span class="icon">⚡</span> {get_text_local('citation_velocity')}</div>
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>{get_text_local('rank')}</th>
                            <th>{get_text_local('title')}</th>
                            <th>{get_text_local('year')}</th>
                            <th>{get_text_local('citations')}</th>
                            <th>{get_text_local('velocity')}</th>
                            <th>{get_text_local('velocity_category')}</th>
                            <th>{get_text_local('age')}</th>
                        </tr>
                    </thead>
                    <tbody>
                        {velocity_table}
                    </tbody>
                </table>
            </div>
        </div>
        
        <!-- 7. DETAILED CITATIONS -->
        <div id="detailed_citations" class="section">
            <div class="section-title"><span class="icon">📋</span> {get_text_local('detailed_citations')}</div>
            {detailed_citations_html if detailed_citations_html else '<p>No detailed citations available</p>'}
        </div>
        
        <!-- 8. ALL PUBLICATIONS -->
        <div id="all_publications" class="section">
            <div class="section-title"><span class="icon">📚</span> {get_text_local('all_publications')}</div>
            
            <div class="filter-section">
                <div class="filter-row">
                    <div>
                        <label for="yearFilter">{get_text_local('filter_by_year')}</label>
                        <select id="yearFilter" onchange="filterPublications()">
                            <option value="">{get_text_local('all_years')}</option>
                            {year_filter_html}
                        </select>
                    </div>
                    <div>
                        <label for="authorFilter">{get_text_local('filter_by_author')}</label>
                        <input type="text" id="authorFilter" placeholder="{get_text_local('author_name_placeholder')}" onkeyup="filterPublications()">
                    </div>
                    <div>
                        <label for="citationFilter">{get_text_local('filter_by_citations')}</label>
                        <input type="number" id="citationFilter" placeholder="{get_text_local('min_citations_placeholder')}" min="0" onchange="filterPublications()">
                    </div>
                    <div>
                        <label for="searchInput">{get_text_local('search_publications')}</label>
                        <input type="text" id="searchInput" placeholder="{get_text_local('search_placeholder')}" onkeyup="filterPublications()">
                    </div>
                    <div>
                        <label>&nbsp;</label>
                        <span id="visibleCount" style="font-weight: 500;">{get_text_local('showing_publications').replace('{0}', str(len(all_publications)))}</span>
                    </div>
                </div>
            </div>
            
            <div class="table-container">
                <table id="publicationsTable">
                    <thead>
                        <tr>
                            <th onclick="sortTable(0)" style="cursor: pointer;">#</th>
                            <th onclick="sortTable(1)" style="cursor: pointer;">{get_text_local('title')}</th>
                            <th onclick="sortTable(2)" style="cursor: pointer;">{get_text_local('year')}</th>
                            <th onclick="sortTable(3)" style="cursor: pointer;">{get_text_local('citations')}</th>
                            <th onclick="sortTable(4)" style="cursor: pointer;">{get_text_local('citations_per_year')}</th>
                            <th onclick="sortTable(5)" style="cursor: pointer;">{get_text_local('journal')}</th>
                            <th>DOI</th>
                            <th>{get_text_local('show_citations')}</th>
                        </tr>
                    </thead>
                    <tbody>
                        {publications_table}
                    </tbody>
                </table>
            </div>
        </div>
        
        <div class="footer-text">
            {get_text_local('html_footer')}<br>
            {get_text_local('html_copyright')}
        </div>
    </div>
</body>
</html>
"""
    
    return html_content

# ======================== STREAMLIT UI ========================

def main():
    """Main Streamlit application"""
    
    # Sidebar
    with st.sidebar:
        st.image("logo.png", width=150)
        
        st.markdown(f"## {get_text('language_label')}")
        lang_option = st.selectbox(
            "",
            options=['en', 'ru'],
            format_func=lambda x: get_text('language_english') if x == 'en' else get_text('language_russian'),
            index=0 if st.session_state.language == 'en' else 1
        )
        if lang_option != st.session_state.language:
            st.session_state.language = lang_option
            st.rerun()
        st.markdown("---")
        
        st.markdown(f"## {get_text('issn_label')}")
        issn = st.text_input(
            get_text('issn_label'),
            placeholder=get_text('issn_placeholder'),
            key="issn_input"
        )
        
        st.markdown(f"## {get_text('period_label')}")
        period = st.text_input(
            get_text('period_label'),
            placeholder=get_text('period_placeholder'),
            help=get_text('period_help'),
            key="period_input"
        )
        
        st.markdown(f"## {get_text('workers_label')}")
        max_workers = st.slider(
            get_text('workers_label'),
            4, 12, 8,
            help=get_text('workers_help'),
            key="workers_slider"
        )
        
        st.markdown("---")
        
        # Color Theme
        st.markdown(f"## 🎨 Color Theme")
        
        if 'primary_color' not in st.session_state:
            st.session_state.primary_color = '#667eea'
        if 'secondary_color' not in st.session_state:
            st.session_state.secondary_color = get_complementary_color('#667eea')
        
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
                value=st.session_state.primary_color,
                help="Choose any color. Complementary color will be auto-generated!"
            )
            st.session_state.primary_color = selected_color
            st.session_state.secondary_color = get_complementary_color(selected_color)
        
        complementary = st.session_state.secondary_color
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(
                f'<div style="text-align: center;">'
                f'<div class="color-preview" style="background: {st.session_state.primary_color};"></div>'
                f'<div style="font-size: 11px; margin-top: 5px;">Primary</div>'
                f'</div>',
                unsafe_allow_html=True
            )
        with col2:
            st.markdown(
                f'<div style="text-align: center;">'
                f'<div class="color-preview" style="background: {complementary};"></div>'
                f'<div style="font-size: 11px; margin-top: 5px;">Complementary</div>'
                f'</div>',
                unsafe_allow_html=True
            )
        
        st.markdown(
            f'<div class="complementary-preview" style="height: 8px; width: 100%; margin: 10px 0;"></div>',
            unsafe_allow_html=True
        )
        
        secondary = st.session_state.get('secondary_color', get_complementary_color(st.session_state.primary_color))
        apply_theme_css(st.session_state.primary_color, secondary)
        
        st.markdown("---")
        
        # Start button
        if st.button(get_text('start_analysis'), type="primary", use_container_width=True):
            if not issn or not period:
                st.error("Please fill in ISSN and Period fields!")
            else:
                # Parse period
                period_str = period.strip()
                if ',' in period_str:
                    years = [int(y.strip()) for y in period_str.split(',') if y.strip().isdigit()]
                elif '-' in period_str:
                    parts = period_str.split('-')
                    if len(parts) == 2:
                        try:
                            start_year = int(parts[0].strip())
                            end_year = int(parts[1].strip())
                            years = (start_year, end_year)
                        except ValueError:
                            st.error("Invalid period format. Use YYYY-YYYY")
                            years = None
                    else:
                        years = None
                else:
                    try:
                        years = int(period_str)
                    except ValueError:
                        st.error("Invalid period format. Use YYYY, YYYY-YYYY, or YYYY,YYYY,YYYY")
                        years = None
                
                if years is None:
                    st.error("Please fix period format!")
                else:
                    st.session_state.issn = issn
                    st.session_state.period = period
                    
                    # Progress tracking
                    progress_placeholder = st.empty()
                    status_placeholder = st.empty()
                    
                    def update_progress(message, percent):
                        status_placeholder.text(message)
                        progress_placeholder.progress(percent / 100)
                    
                    with st.spinner(get_text('collecting_data')):
                        try:
                            data = collect_all_data(
                                issn, 
                                years, 
                                max_workers=max_workers,
                                progress_callback=update_progress
                            )
                            
                            if data.publications:
                                st.session_state.journal_data = data
                                
                                # Calculate metrics
                                engine = MetricsEngine(data)
                                metrics = {
                                    'overview': engine.calculate_overview(),
                                    'most_cited': engine.get_most_cited_publications(30),
                                    'authors': engine.analyze_authors(),
                                    'geography': engine.analyze_geography(),
                                    'citation_dynamics': engine.analyze_citation_dynamics(),
                                    'citing_works': engine.analyze_citing_works(),
                                    'topics': engine.analyze_topics(),
                                    'detailed_citations': engine.get_detailed_citations(),
                                    'all_publications': engine.get_all_publications(),
                                    'citation_velocity': engine.calculate_citation_velocity()
                                }
                                
                                st.session_state.metrics = metrics
                                st.session_state.analysis_complete = True
                                
                                progress_placeholder.progress(1.0)
                                status_placeholder.success(
                                    get_text('analysis_complete') + 
                                    f" {get_text('total_publications_found').format(len(data.publications))} " +
                                    f"{get_text('total_citations_found').format(sum(p.cited_by_count for p in data.publications))}"
                                )
                                st.balloons()
                                st.info(get_text('go_to_analytics'))
                            else:
                                st.error("No publications found for this ISSN and period.")
                                
                        except Exception as e:
                            st.error(f"Error during analysis: {str(e)}")
    
    # Main area
    st.markdown(f"# 📚 {get_text('app_title')}")
    st.markdown(f"### {get_text('app_subtitle')}")
    st.markdown("---")
    
    tab1, tab2, tab3 = st.tabs([get_text('tab_collect'), get_text('tab_analytics'), get_text('tab_report')])
    
    with tab1:
        st.markdown('<div class="custom-tab fade-in">', unsafe_allow_html=True)
        st.markdown(f"### {get_text('tab_collect')}")
        
        if st.session_state.analysis_complete:
            data = st.session_state.journal_data
            if data:
                st.success(f"✅ {get_text('analysis_complete')}")
                st.metric(get_text('total_publications'), len(data.publications))
                st.metric(get_text('total_citations'), sum(p.cited_by_count for p in data.publications))
                
                # Show sample of publications
                with st.expander("📋 Sample Publications"):
                    for i, pub in enumerate(data.publications[:10]):
                        st.markdown(f"**{i+1}. {pub.title[:150]}...**")
                        st.markdown(f"Year: {pub.publication_year} | Citations: {pub.cited_by_count} | DOI: {pub.doi}")
                        st.markdown("---")
        else:
            st.info(get_text('run_analysis_first'))
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        if st.session_state.analysis_complete and st.session_state.metrics:
            metrics = st.session_state.metrics
            data = st.session_state.journal_data
            
            # Display metrics
            overview = metrics['overview']
            
            # Overview metrics
            st.markdown(f"### {get_text('overview')}")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric(get_text('total_publications'), overview['total_publications'])
            with col2:
                st.metric(get_text('total_citations'), overview['total_citations'])
            with col3:
                st.metric(get_text('h_index'), overview['h_index'])
            with col4:
                st.metric(get_text('avg_citations'), f"{overview['avg_citations']:.1f}")
            
            col5, col6, col7, col8 = st.columns(4)
            with col5:
                st.metric(get_text('open_access'), f"{overview['open_access_percent']:.1f}%")
            with col6:
                st.metric(get_text('unique_authors'), overview['unique_authors'])
            with col7:
                st.metric(get_text('unique_countries'), overview['unique_countries'])
            with col8:
                st.metric(get_text('unique_citing_journals'), overview['unique_citing_journals'])
            
            st.markdown("---")
            
            # Open Access Breakdown
            with st.expander(f"📊 {get_text('open_access_breakdown')}"):
                oa = overview['open_access_breakdown']
                for oa_type, count in oa.items():
                    if oa_type != 'unknown' or count > 0:
                        label = get_text(oa_type)
                        st.markdown(f"**{label}:** {count} ({count/overview['total_publications']*100 if overview['total_publications'] > 0 else 0:.1f}%)")
                        st.progress(count/overview['total_publications'] if overview['total_publications'] > 0 else 0)
            
            # Most Cited
            st.markdown(f"### {get_text('most_cited_publications')}")
            most_cited_df = pd.DataFrame(metrics['most_cited'])
            st.dataframe(most_cited_df, use_container_width=True)
            
            # Author Analysis
            st.markdown(f"### {get_text('author_analysis')}")
            authors_df = pd.DataFrame(metrics['authors']['top_authors'])
            st.dataframe(authors_df, use_container_width=True)
            
            # Geographic Analysis
            st.markdown(f"### {get_text('geographic_analysis')}")
            
            geo = metrics['geography']
            
            # Type 1
            st.markdown(f"#### {get_text('geography_type_1')}")
            st.caption(get_text('geography_type_1_desc'))
            if geo['type1_unique_countries_per_publication']:
                geo1_df = pd.DataFrame(list(geo['type1_unique_countries_per_publication'].items()), columns=["Country", "Publications"])
                st.dataframe(geo1_df, use_container_width=True)
            
            # Type 2
            st.markdown(f"#### {get_text('geography_type_2')}")
            st.caption(get_text('geography_type_2_desc'))
            if geo['type2_authors_per_country']:
                geo2_df = pd.DataFrame(list(geo['type2_authors_per_country'].items()), columns=["Country", "Authors"])
                st.dataframe(geo2_df, use_container_width=True)
            
            # Type 3
            st.markdown(f"#### {get_text('geography_type_3')}")
            st.caption(get_text('geography_type_3_desc'))
            col1, col2 = st.columns(2)
            with col1:
                st.metric(get_text('single_country'), geo.get('single_country_count', 0))
            with col2:
                st.metric(get_text('international_collaboration'), geo.get('international_count', 0))
            
            if geo['collaboration_couples']:
                st.markdown(f"#### {get_text('collaboration_couples')}")
                couples_df = pd.DataFrame(geo['collaboration_couples'])
                st.dataframe(couples_df, use_container_width=True)
            
            # Citation Dynamics
            st.markdown(f"### {get_text('citation_analysis')}")
            
            cd = metrics['citation_dynamics']
            
            st.markdown(f"#### {get_text('yearly_citation_dynamics')}")
            if cd['network_data']:
                network_df = pd.DataFrame(cd['network_data'])
                st.dataframe(network_df, use_container_width=True)
            
            st.markdown(f"#### {get_text('citation_network')}")
            if cd['all_years']:
                st.caption("Heatmap: Publication Year → Citation Year")
                all_years = cd['all_years']
                yearly_cites = cd['yearly_citations']
                
                heatmap_data = []
                for pyear in sorted(yearly_cites.keys()):
                    row = {'Publication Year': pyear}
                    for cyear in all_years:
                        row[str(cyear)] = yearly_cites.get(pyear, {}).get(cyear, 0)
                    heatmap_data.append(row)
                
                if heatmap_data:
                    heatmap_df = pd.DataFrame(heatmap_data)
                    st.dataframe(heatmap_df, use_container_width=True)
            
            # Citing Works
            st.markdown(f"### {get_text('citing_works_analysis')}")
            cw = metrics['citing_works']
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(get_text('total_citing_works'), cw['total_citing_works'])
            with col2:
                st.metric(get_text('unique_citing_authors'), cw['unique_citing_authors'])
            with col3:
                st.metric(get_text('unique_citing_journals'), cw['unique_citing_journals'])
            
            with st.expander(f"📊 {get_text('top_citing_authors')}"):
                authors_df = pd.DataFrame(cw['top_authors'])
                st.dataframe(authors_df, use_container_width=True)
            
            with st.expander(f"📊 {get_text('top_citing_countries')}"):
                countries_df = pd.DataFrame(cw['top_countries'])
                st.dataframe(countries_df, use_container_width=True)
            
            with st.expander(f"📊 {get_text('top_citing_journals')}"):
                journals_df = pd.DataFrame(cw['top_journals'])
                st.dataframe(journals_df, use_container_width=True)
            
            # Topics
            st.markdown(f"### {get_text('topics_analysis')}")
            topics_df = pd.DataFrame(metrics['topics']['top_topics'])
            st.dataframe(topics_df, use_container_width=True)
            
            # Citation Velocity
            st.markdown(f"### {get_text('citation_velocity')}")
            velocity_df = pd.DataFrame(metrics['citation_velocity'].values())
            st.dataframe(velocity_df, use_container_width=True)
            
            # Detailed Citations
            st.markdown(f"### {get_text('detailed_citations')}")
            if metrics['detailed_citations']:
                for pub_id, data in list(metrics['detailed_citations'].items())[:20]:
                    with st.expander(f"📄 {data['title'][:150]}... ({data['year']}) - {data['total_citations']} citations"):
                        st.markdown(f"**DOI:** {data['doi']}")
                        st.markdown(f"**Total Citations:** {data['total_citations']}")
                        
                        for cite in data['citations'][:10]:
                            st.markdown(f"""
                            <div style="background: #f8f9fa; padding: 10px; border-radius: 6px; margin: 5px 0;">
                                <strong>{cite['citing_title'][:150]}...</strong><br>
                                {get_text('citing_journal')}: {cite['citing_journal']} | 
                                {get_text('citing_year')}: {cite['citing_year']} | 
                                {get_text('citation_lag')}: {cite['citation_lag']} years<br>
                                <a href="https://doi.org/{cite['citing_doi']}" target="_blank">DOI: {cite['citing_doi']}</a>
                            </div>
                            """, unsafe_allow_html=True)
            else:
                st.info("No detailed citations available")
            
            # All Publications
            st.markdown(f"### {get_text('all_publications')}")
            all_pubs_df = pd.DataFrame(metrics['all_publications'])
            st.dataframe(all_pubs_df, use_container_width=True)
            
        else:
            st.info(get_text('run_analysis_first'))
    
    with tab3:
        if st.session_state.analysis_complete and st.session_state.metrics:
            data = st.session_state.journal_data
            metrics = st.session_state.metrics
            lang = st.session_state.language
            primary = st.session_state.primary_color
            secondary = st.session_state.secondary_color
            
            st.markdown(f"### {get_text('export_html_report')}")
            
            html_report = generate_html_report(data, metrics, lang, primary, secondary)
            
            # Generate filename
            issn_clean = st.session_state.get('issn', 'journal').replace('-', '')
            period_clean = st.session_state.get('period', 'period').replace(',', '_').replace('-', '_')
            filename = f"journal_metrics_{issn_clean}_{period_clean}.html"
            
            st.download_button(
                label=get_text('download_html_report'),
                data=html_report.encode('utf-8'),
                file_name=filename,
                mime="text/html"
            )
            
            st.markdown("---")
            
            # CSV Export
            st.markdown(f"### {get_text('export_csv')}")
            
            # Prepare CSV data
            csv_data = []
            for pub in data.publications:
                author_names = ', '.join([a.display_name for a in pub.authors if a.display_name])
                countries = ', '.join(set(c for a in pub.authors for c in a.countries if c))
                
                citing_dois = []
                if pub.id in data.citations:
                    citing_dois = [c.citing_doi for c in data.citations[pub.id]]
                
                csv_data.append({
                    'DOI': pub.doi,
                    'Title': pub.title,
                    'Year': pub.publication_year,
                    'Citations': pub.cited_by_count,
                    'Citations_Per_Year': pub.citations_per_year,
                    'Journal': pub.journal_name,
                    'Publisher': pub.publisher,
                    'Authors': author_names,
                    'Countries': countries,
                    'Open_Access': pub.is_open_access,
                    'Open_Access_Status': pub.open_access_status,
                    'Citing_Works_Count': len(citing_dois),
                    'Citing_Works': '|'.join(citing_dois)
                })
            
            csv_df = pd.DataFrame(csv_data)
            csv_str = csv_df.to_csv(index=False)
            
            csv_filename = f"journal_data_{issn_clean}_{period_clean}.csv"
            
            st.download_button(
                label=get_text('download_csv'),
                data=csv_str,
                file_name=csv_filename,
                mime="text/csv"
            )
            
            st.markdown("---")
            
            # Text Export
            st.markdown(f"### {get_text('export_text')}")
            
            export_text = f"""
=== JOURNAL METRICS ANALYSIS ===
ISSN: {st.session_state.get('issn', 'N/A')}
Period: {st.session_state.get('period', 'N/A')}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

=== OVERVIEW ===
Total Publications: {metrics['overview']['total_publications']}
Total Citations: {metrics['overview']['total_citations']}
h-index: {metrics['overview']['h_index']}
g-index: {metrics['overview']['g_index']}
i10-index: {metrics['overview']['i10_index']}
i100-index: {metrics['overview']['i100_index']}
Average Citations: {metrics['overview']['avg_citations']:.1f}
Open Access: {metrics['overview']['open_access_percent']:.1f}%
Active Years: {metrics['overview']['active_years']}
Unique Authors: {metrics['overview']['unique_authors']}
Unique Countries: {metrics['overview']['unique_countries']}
Total Citing Works: {metrics['overview']['total_citing_works']}
Unique Citing Journals: {metrics['overview']['unique_citing_journals']}

=== MOST CITED PUBLICATIONS (TOP 10) ===
{chr(10).join([f"{i+1}. {pub['title'][:100]}... ({pub['year']}) - {pub['citations']} citations" for i, pub in enumerate(metrics['most_cited'][:10])])}

=== TOP AUTHORS ===
{chr(10).join([f"{i+1}. {author['display_name']}: {author['publication_count']} publications, {author['citation_count']} citations" for i, author in enumerate(metrics['authors']['top_authors'][:10])])}

=== TOP COUNTRIES (by publications) ===
{chr(10).join([f"{country}: {count}" for country, count in list(metrics['geography']['type1_unique_countries_per_publication'].items())[:10]])}

=== TOP CITING JOURNALS ===
{chr(10).join([f"{journal['name']}: {journal['count']}" for journal in metrics['citing_works']['top_journals'][:10]])}
"""
            
            st.text_area(get_text('export_text'), export_text, height=300)
            
            if st.button(get_text('copy_to_clipboard')):
                st.success(get_text('copied'))
        else:
            st.info(get_text('run_analysis_first'))

if __name__ == "__main__":
    main()
