# ============================================
# СЕКЦИЯ ПАРАМЕТРОВ (настройка запросов)
# ============================================

# Параметры API запросов
BATCH_SIZE = 50 
MAX_RETRIES = 3 
TIMEOUT = 30 
DELAY_BETWEEN_BATCHES = 0.5 
MAX_CONCURRENT_REQUESTS = 3
RETRY_DELAY = 2 
ORCID_REQUEST_DELAY = 0.2 

# Параметры вывода
SHOW_DEBUG_LOGS = True  # Показывать детальные логи
GENERATE_HTML_REPORT = True  # Генерировать HTML отчет
USE_CACHE = True  # Кэширование результатов
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
from datetime import datetime, date, timedelta
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
import random
from dateutil.relativedelta import relativedelta

# ============================================
# OPENALEX API KEY (from Streamlit secrets)
# ============================================

def get_openalex_api_key() -> Optional[str]:
    """Read OpenAlex API key from st.secrets. Returns None if not configured."""
    try:
        return st.secrets["OPENALEX_API_KEY"]
    except (KeyError, FileNotFoundError):
        return None

OPENALEX_API_KEY = get_openalex_api_key()

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
        'select_secondary_color': '🎨 Select secondary color',
        'primary': 'Primary',
        'secondary': 'Secondary',
        'analysis_params': '📊 Analysis Parameters',
        'use_cache': '💾 Use cache',
        'clear_cache': '🗑️ Clear cache',
        'cache_cleared': '✅ Cache cleared!',
        'load_data': '📥 Load Data',
        'profile': 'Scholar Profile',
        'reports': '📄 Reports',
        'journal_issn': 'Journal ISSN',
        'issn_placeholder': '0028-0836 or 00280836',
        'issn_help': 'Enter the ISSN of the journal to analyze',
        'period_input': 'Analysis Period',
        'period_placeholder': '2020-2025 or 2020,2021,2022 or 2024',
        'period_help': 'Enter period: YYYY-YYYY (range), YYYY,YYYY (specific years), or YYYY (single year)',
        'workers': 'Parallel Workers',
        'workers_help': 'Number of parallel threads for API requests',
        'upload_logo': 'Upload journal logo (optional)',
        'logo_help': 'Logo will be displayed in reports',
        'analyze_button': '🔍 Analyze Journal',
        'no_issn': '⚠️ Enter a valid ISSN',
        'no_period': '⚠️ Enter analysis period',
        'analysis_complete': '✅ Analysis complete! Found {count} publications in {time:.1f} sec.',
        'no_data': '👈 Load data and click "Analyze Journal"',
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
        'total_citations': 'Total citations',
        'avg_citations': 'Average citations',
        'median_citations': 'Median citations',
        'max_citations': 'Max citations',
        'open_access': 'Open Access',
        'active_years': 'Active years',
        'risk_flags': 'Risk flags',
        'collaborations': 'Collaboration Analysis',
        'domestic': '🇷🇺 Domestic collaborations',
        'international': '🌐 International collaborations',
        'papers': 'Papers',
        'no_data_collab': 'No data',
        'collab_index': 'Collaboration index: {index:.2f}',
        'country_diversity': 'Country diversity: {count} countries',
        'most_collaborative': 'Most collaborative country: {country}',
        'top_coauthors': 'Top co-authors',
        'joint_works': 'joint works',
        'publications_list': '📚 Publication list',
        'showing_limited': 'Showing {shown} of {total} publications',
        'title': 'Title',
        'year': 'Year',
        'journal': 'Journal',
        'doi': 'DOI',
        'no_publications': 'No publications',
        'orcid': 'ORCID',
        'affiliations': 'Affiliations',
        'countries': 'Countries',
        'total_analyzed': 'Total analyzed publications',
        'retractions': 'Retractions',
        'corrections': 'Corrections',
        'first_publication': 'First publication',
        'last_publication': 'Last publication',
        'papers_per_year': 'Papers per year',
        'trend': 'Trend',
        'unique_coauthors': 'Unique co-authors',
        'avg_authors_per_paper': 'Average authors per paper',
        'thematic_diversity': 'Thematic diversity (Shannon)',
        'domestic_ratio': 'Domestic collaboration ratio',
        'international_ratio': 'International collaboration ratio',
        'years_chart_title': 'Publication activity dynamics',
        'journals_chart_title': 'Top journals by publications',
        'oa_chart_title': 'Open access status',
        'publishers_chart_title': 'Distribution by publishers',
        'affiliations_chart_title': 'Top affiliations',
        'citations_chart_title': 'Most cited articles',
        'citation_distribution_title': 'Citation distribution',
        'thematic_structure_title': 'Thematic structure of research',
        'wordcloud_title': 'Key research concepts',
        'radar_title': 'Thematic profile (Radar Chart)',
        'concepts': 'Concepts',
        'fields': 'Fields',
        'domains': 'Domains',
        'topics': 'Topics',
        'subtopics': 'Subtopics',
        'year': 'Year',
        'publication_year': 'Publication year',
        'number': 'Number',
        'citation_range': 'Citation range',
        'articles': 'Articles',
        'x_label_pubs': 'Number of publications',
        'y_label_pubs': 'Number of publications',
        'trend_label': 'Trend',
        'confidence_interval': 'Confidence interval',
        'footer': '© Advanced Journal Analysis Tool / Created by daM / Chimica Techno Acta',
        'journal_url': 'https://chimicatechnoacta.ru',
        'no_profile_data': 'No profile data available',
        'enter_orcid': 'Enter ORCID to analyze',
        'analyze_multiple': 'Analyze multiple authors',
        'profile_analysis': 'Comprehensive scholar profile analysis by ORCID',
        'select_language': 'Select language',
        'theme_presets_label': 'Theme presets',
        'primary_color_label': 'Primary color',
        'secondary_color_label': 'Secondary color',
        'analysis_progress': 'Analysis progress',
        'loading_data': 'Loading data',
        'analyzing_data': 'Analyzing data',
        'generating_viz': 'Generating visualizations',
        'orcid_format_error': 'Invalid ORCID format',
        'data_not_found': 'Data not found. Check ORCID correctness.',
        'error_occurred': 'Error occurred',
        'retracted_publications': 'retracted publications',
        'possible_unethical': 'Possible unethical practices detected!',
        'analyzing_authors': 'Analyzing {count} author(s)...',
        'starting_analysis': 'Starting analysis...',
        'fetching_data': 'Fetching data',
        'analysis_complete_text': 'Analysis complete',
        'creating_charts': 'Creating charts',
        'retractions_in_profile': 'retractions in profile',
        'source_types': 'Sources by Type',
        'source_journal_articles': 'Journal articles',
        'source_repositories': 'Preprints/Repositories',
        'source_ebooks': 'Electronic books',
        'source_proceedings': 'Proceedings',
        'source_other': 'Other items (non-DOI)',
        'source_count': 'Count',
        'source_examples': 'Examples',
        'source_no_doi': 'No DOI available',
        'source_view_link': 'View',
        'source_doi_available': 'DOI available',
        'source_no_link': 'No link available',
        'coauthor_orcid': 'ORCID',
        'coauthor_scopus': 'Scopus',
        'coauthor_researcherid': 'ResearcherID',
        'coauthor_website': 'Personal website',
        'coauthor_other': 'Other profiles',
        'no_orcid_found': 'No ORCID found',
        'coauthor_info': 'Co-author information',
        'coauthor_profiles': 'External profiles',
        'main_metrics': 'Main Metrics',
        'citations_per_year': 'Citations/year',
        'fetching_orcid_profiles': '🆔 Fetching ORCID profiles...',
        'orcid_profiles_fetched': '✅ ORCID profiles fetched: {count}',
        'no_orcid_profiles_found': 'No ORCID profiles found',
        'analysis_source': '📊 Data source for analysis:',
        'analysis_source_orcid_only': '🔒 ORCID only (safe)',
        'analysis_source_orcid_openalex': '🔓 ORCID + OpenAlex (max. completeness)',
        'analysis_source_help': 'Select data source for publication analysis',
        'temporal_gap_warning': '⚠️ Significant temporal gap detected in publications!',
        'temporal_gap_detected': 'Gap of {gap_years} years between {gap_start} and {gap_end}',
        'temporal_gap_suggestion': 'This may indicate: - Wrongly attributed publications from another scientist with the same name - Long break in scientific activity',
        'temporal_gap_recommendation': 'Recommended to cut off publications before {cut_off_year}',
        'temporal_gap_apply_filter': '📅 Apply year filter for report',
        'temporal_gap_select_period': 'Select analysis period:',
        'temporal_gap_publications_total': 'Total publications',
        'temporal_gap_after_filter': 'After filtering',
        'temporal_gap_filter_info': '📅 Period: {start_year} - {end_year}',
        'temporal_gap_original_count': 'Original: {count} publications',
        'temporal_gap_filtered_count': 'Filtered: {count} publications',
        'show_filtered_report': 'Show report with filtering',
        'show_original_report': 'Show original report (no filtering)',
        'temporal_gap_use_filter': 'Use year filter for report',
        # ====== НОВЫЕ КЛЮЧИ ДЛЯ JOURNAL ANALYSIS ======
        'journal_analysis_title': 'Journal Analysis Report',
        'stage_fetch_publications': 'Stage 1: Fetching journal publications',
        'stage_fetch_citing': 'Stage 2: Fetching citing works',
        'stage_fetch_pub_metadata': 'Stage 3: Fetching publication metadata',
        'stage_fetch_cite_metadata': 'Stage 4: Fetching citing works metadata',
        'stage_analyze_report': 'Stage 5: Analyzing data and generating report',
        'stage_publications_found': 'Found {count} publications',
        'stage_citing_found': 'Found {count} citing works',
        'stage_metadata_fetched': 'Fetched metadata for {count} works',
        'stage_processing': 'Processing {current}/{total}...',
        'overview': 'Overview',
        'total_publications': 'Total Publications',
        'total_citations': 'Total Citations',
        'avg_citations': 'Avg Citations',
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
        'analyzed_articles': 'Analyzed Articles',
        'author_analysis': 'Author Analysis',
        'rank': 'Rank',
        'authors': 'Authors',
        'publications_count': 'Publications',
        'citations_count': 'Citations',
        'top_affiliations': 'Top Affiliations',
        'geographic_analysis': 'Geographic Analysis',
        'unique_countries_per_publication': 'Unique Countries per Publication',
        'authors_per_country': 'Authors per Country',
        'collaboration_patterns': 'Collaboration Patterns',
        'single_country': 'Single-Country',
        'multi_country': 'Multi-Country',
        'collaboration_couples': 'Collaboration Couples',
        'country_pair': 'Country Pair',
        'frequency': 'Frequency',
        'citation_analysis': 'Citation Analysis',
        'citation_dynamics_by_year': 'Citation Dynamics by Year',
        'publication_year': 'Publication Year',
        'citation_year': 'Citation Year',
        'citations_count': 'Citations Count',
        'first_citation_analysis': 'First Citation Analysis',
        'min_lag': 'Min lag (days)',
        'max_lag': 'Max lag (days)',
        'avg_lag': 'Avg lag (days)',
        'median_lag': 'Median lag (days)',
        'cumulative_citations': 'Cumulative Citations',
        'citation_network_heatmap': 'Citation Network Heatmap',
        'most_cited_publications': 'Most Cited Publications',
        'citing_works_analysis': 'Citing Works Analysis',
        'total_citing_works': 'Total Citing Works',
        'top_citing_authors': 'Top Citing Authors',
        'top_citing_affiliations': 'Top Citing Affiliations',
        'top_citing_countries': 'Top Citing Countries',
        'top_citing_journals': 'Top Citing Journals',
        'top_citing_publishers': 'Top Citing Publishers',
        'topics_analysis': 'Topics Analysis',
        'analyzed_count': 'Count in Analyzed',
        'citing_count': 'Count in Citing',
        'analyzed_norm_count': 'Norm. Count in Analyzed',
        'citing_norm_count': 'Norm. Count in Citing',
        'total_norm_count': 'Total Norm. Count',
        'first_year': 'First Year',
        'peak_year': 'Peak Year',
        'top_cited_topics': 'Top Cited Topics',
        'top_cited_subtopics': 'Top Cited Subtopics',
        'top_cited_fields': 'Top Cited Fields',
        'top_cited_domains': 'Top Cited Domains',
        'top_cited_concepts': 'Top Cited Concepts',
        'detailed_citations': 'Detailed Citations',
        'show_citations': 'Show Citations',
        'hide_citations': 'Hide Citations',
        'citing_journal': 'Citing Journal',
        'citing_year': 'Citing Year',
        'citing_date': 'Citing Date',
        'citation_lag': 'Citation Lag (days)',
        'all_publications': 'All Publications',
        'filter_by_year': 'Filter by Year',
        'filter_by_author': 'Filter by Author',
        'filter_by_affiliation': 'Filter by Affiliation',
        'filter_by_citations': 'Filter by Citations (min)',
        'filter_by_title': 'Filter by Title Word(s)',
        'search_publications': 'Search Publications',
        'all_years': 'All Years',
        'visible_count': 'Showing {shown} of {total} publications',
        'data_source': 'Data source: OpenAlex',
        'generated_on': 'Generated',
        'click_to_toggle': 'Click to toggle citations',
        'no_citations_found': 'No citations found for this publication',
        'citations_per_year_label': 'Citations/Year',
        'journal_issn_label': 'ISSN: {issn}',
        'analysis_period_label': 'Period: {period}',
        'reset_analysis': 'Reset Analysis',
        'days': 'days',
        'analysis_data_from_cache': 'Using cached data from previous analysis',
        'regenerate_report': 'Regenerate Report',
        # ====== НОВЫЕ КЛЮЧИ ДЛЯ AUTHOR DISTRIBUTION ======
        'author_distribution': 'Author Distribution',
        'author_distribution_analyzed': 'Distribution of Analyzed Publications by Author Count',
        'author_distribution_citing': 'Distribution of Citing Publications by Author Count',
        'authors_per_paper': 'Authors per paper',
        'num_papers': 'Number of papers',
        'num_citing_papers': 'Number of citing papers',
        'one_author': '1 author',
        'two_authors': '2 authors',
        'three_authors': '3 authors',
        'four_plus_authors': '4+ authors',
        # ====== НОВЫЕ КЛЮЧИ ДЛЯ ORCID IN CITING AUTHORS ======
        'citing_author_orcid': 'ORCID',
        # ====== НОВЫЕ КЛЮЧИ ДЛЯ IMPACT FACTOR И CITESCORE ======
        'impact_factor': 'Impact Factor (3-year)',
        'impact_factor_full': 'IF ({pub_years} → {cite_year})',
        'impact_factor_description': 'Citations in {cite_year} to articles published in {pub_years} / Number of articles published in {pub_years}',
        'impact_factor_calculation': 'Impact Factor calculation for 3-year window',
        'impact_factor_not_applicable': 'Impact Factor not applicable (period does not cover target years {years})',
        'citescore': 'CiteScore (4-year)',
        'citescore_full': 'SC ({years})',
        'citescore_description': 'Citations within {years} to articles published in {years} / Number of articles published in {years}',
        'citescore_calculation': 'CiteScore calculation for 4-year window',
        'citescore_not_applicable': 'CiteScore not applicable (period does not cover target years {years})',
        'if_sc_note': 'Calculated for the analysis period covering target years',
        # ====== НОВЫЕ КЛЮЧИ ДЛЯ ДИНАМИЧЕСКИХ IF И CITESCORE ======
        'dynamic_metrics_title': 'Dynamic Metrics',
        'if_dynamic': 'Dynamic Impact Factor (3-year)',
        'citescore_dynamic': 'Dynamic CiteScore (4-year)',
        'if_dynamic_full': 'Dynamic IF ({cite_start} → {cite_end})',
        'citescore_dynamic_full': 'Dynamic SC ({start} → {end})',
        'dynamic_window_label': 'Window: {start} → {end}',
        'dynamic_publications_window': 'Publications window: {start} → {end}',
        'dynamic_citations_window': 'Citations window: {start} → {end}',
        'dynamic_not_applicable': 'Not applicable (period does not cover window)',
        'if_dynamic_description': 'Dynamic IF: citations in (now-1y, now] to articles published in (now-3y, now-1y] / number of articles published in (now-3y, now-1y]',
        'citescore_dynamic_description': 'Dynamic SC: citations in (now-4y, now] to articles published in (now-4y, now] / number of articles published in (now-4y, now]',
        'dynamic_as_of': 'as of {date}',
        'dynamic_citations_publications': '{citations} Citations / {publications} Publications',
        # ====== NEW: GRANTS & FUNDING ======
        'grants_analysis': 'Grants & Funding',
        'grants_and_funding': 'Grants & Funding',
        'top_funders': 'Top Funders',
        'top_awards': 'Top Awards',
        'top_funders_analyzed': 'Top Funders (Analyzed)',
        'top_funders_citing': 'Top Funders (Citing)',
        'top_awards_analyzed': 'Top Awards (Analyzed)',
        'top_awards_citing': 'Top Awards (Citing)',
        'funder': 'Funder',
        'award_id': 'Award ID',
        'unique_funders': 'Unique Funders',
        'unique_awards': 'Unique Awards',
        'unique_funders_analyzed': 'Unique Funders (Analyzed)',
        'unique_funders_citing': 'Unique Funders (Citing)',
        'unique_awards_analyzed': 'Unique Awards (Analyzed)',
        'unique_awards_citing': 'Unique Awards (Citing)',
        'no_grants_data': 'No grants data available',
        'works_count': 'Works',
        'citing_publications': 'Citing Publications',
        'filter_by_journal': 'Filter by Journal',
        'filter_by_publisher': 'Filter by Publisher',
        'grants_funding': 'Grants & Funding',
        'grant': 'Grant',
        'ror': 'ROR',
        'analyzed_publications_grants': 'Analyzed Publications — Grants & Funding',
        'citing_publications_grants': 'Citing Publications — Grants & Funding',
        'no_cited_publications': 'No cited publications',
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
        'select_secondary_color': '🎨 Выберите дополнительный цвет',
        'primary': 'Основной',
        'secondary': 'Дополнительный',
        'analysis_params': '📊 Параметры анализа',
        'use_cache': '💾 Использовать кэш',
        'clear_cache': '🗑️ Очистить кэш',
        'cache_cleared': '✅ Кэш очищен!',
        'load_data': '📥 Загрузка данных',
        'profile': 'Профиль ученого',
        'reports': '📄 Отчеты',
        'journal_issn': 'ISSN журнала',
        'issn_placeholder': '0028-0836 или 00280836',
        'issn_help': 'Введите ISSN журнала для анализа',
        'period_input': 'Период анализа',
        'period_placeholder': '2020-2025 или 2020,2021,2022 или 2024',
        'period_help': 'Введите период: ГГГГ-ГГГГ (диапазон), ГГГГ,ГГГГ (конкретные годы), или ГГГГ (один год)',
        'workers': 'Параллельных потоков',
        'workers_help': 'Количество параллельных потоков для API запросов',
        'upload_logo': 'Загрузить логотип журнала (опционально)',
        'logo_help': 'Логотип будет отображаться в отчетах',
        'analyze_button': '🔍 Анализировать журнал',
        'no_issn': '⚠️ Введите корректный ISSN',
        'no_period': '⚠️ Введите период анализа',
        'analysis_complete': '✅ Анализ завершен! Найдено {count} публикаций за {time:.1f} сек.',
        'no_data': '👈 Загрузите данные и нажмите "Анализировать журнал"',
        'no_data_reports': '👈 Сначала выполните анализ на вкладке "Загрузка данных"',
        'html_report': '📄 Генерация HTML отчета',
        'download_report': '💾 Скачать HTML отчет',
        'report_preview': '📋 Предпросмотр HTML отчета',
        'download_hint': 'Нажмите "Скачать HTML отчет" для полного отчета',
        'generating_report': 'Генерация HTML отчета...',
        'publications': 'Публикаций',
        'citations': 'Цитирований',
        'h_index': 'h-index',
        'g_index': 'g-index',
        'i10_index': 'i10-index',
        'i100_index': 'i100-index',
        'total_citations': 'Всего цитирований',
        'avg_citations': 'Среднее цитирований',
        'median_citations': 'Медиана цитирований',
        'max_citations': 'Максимум цитирований',
        'open_access': 'Открытый доступ',
        'active_years': 'Активных лет',
        'risk_flags': 'Флаги риска',
        'collaborations': 'Анализ коллабораций',
        'domestic': '🇷🇺 Внутристрановые коллаборации',
        'international': '🌐 Международные коллаборации',
        'papers': 'Статей',
        'no_data_collab': 'Нет данных',
        'collab_index': 'Индекс коллабораций: {index:.2f}',
        'country_diversity': 'Страновое разнообразие: {count} стран',
        'most_collaborative': 'Самая коллаборативная страна: {country}',
        'top_coauthors': 'Топ соавторы',
        'joint_works': 'совместных работ',
        'publications_list': '📚 Список публикаций',
        'showing_limited': 'Показано {shown} из {total} публикаций',
        'title': 'Название',
        'year': 'Год',
        'journal': 'Журнал',
        'doi': 'DOI',
        'no_publications': 'Нет публикаций',
        'orcid': 'ORCID',
        'affiliations': 'Аффилиации',
        'countries': 'Страны',
        'total_analyzed': 'Всего проанализировано публикаций',
        'retractions': 'Ретракций',
        'corrections': 'Коррекций',
        'first_publication': 'Первая публикация',
        'last_publication': 'Последняя публикация',
        'papers_per_year': 'Статей в год',
        'trend': 'Тренд',
        'unique_coauthors': 'Уникальных соавторов',
        'avg_authors_per_paper': 'Среднее авторов на статью',
        'thematic_diversity': 'Тематическое разнообразие (Shannon)',
        'domestic_ratio': 'Доля внутристрановых коллабораций',
        'international_ratio': 'Доля международных коллабораций',
        'years_chart_title': 'Динамика публикационной активности',
        'journals_chart_title': 'Топ журналов по числу публикаций',
        'oa_chart_title': 'Статус открытого доступа',
        'publishers_chart_title': 'Распределение по издательствам',
        'affiliations_chart_title': 'Топ аффилиаций',
        'citations_chart_title': 'Самые цитируемые статьи',
        'citation_distribution_title': 'Распределение статей по числу цитирований',
        'thematic_structure_title': 'Тематическая структура исследований',
        'wordcloud_title': 'Ключевые концепты исследований',
        'radar_title': 'Тематический профиль (Radar Chart)',
        'concepts': 'Концепты',
        'fields': 'Fields',
        'domains': 'Domains',
        'topics': 'Topics',
        'subtopics': 'Subtopics',
        'year': 'Год',
        'publication_year': 'Год публикации',
        'number': 'Число',
        'citation_range': 'Диапазон цитирований',
        'articles': 'Статей',
        'x_label_pubs': 'Число публикаций',
        'y_label_pubs': 'Число публикаций',
        'trend_label': 'Тренд',
        'confidence_interval': 'Доверительный интервал',
        'footer': '© Advanced Journal Analysis Tool / Created by daM / Chimica Techno Acta',
        'journal_url': 'https://chimicatechnoacta.ru',
        'no_profile_data': 'Нет данных профиля',
        'enter_orcid': 'Введите ORCID для анализа',
        'analyze_multiple': 'Анализировать нескольких авторов',
        'profile_analysis': 'Комплексный анализ профиля ученого по ORCID',
        'select_language': 'Выберите язык',
        'theme_presets_label': 'Пресеты тем',
        'primary_color_label': 'Основной цвет',
        'secondary_color_label': 'Дополнительный цвет',
        'analysis_progress': 'Прогресс анализа',
        'loading_data': 'Загрузка данных',
        'analyzing_data': 'Анализ данных',
        'generating_viz': 'Генерация визуализаций',
        'orcid_format_error': 'Неверный формат ORCID',
        'data_not_found': 'Данные не найдены. Проверьте правильность ORCID.',
        'error_occurred': 'Произошла ошибка',
        'retracted_publications': 'ретрагированных публикаций',
        'possible_unethical': 'Обнаружены возможные неэтичные практики!',
        'analyzing_authors': 'Анализирую {count} авторов...',
        'starting_analysis': 'Начинаем анализ...',
        'fetching_data': 'Получение данных',
        'analysis_complete_text': 'Анализ завершен',
        'creating_charts': 'Создание графиков',
        'retractions_in_profile': 'ретракций в профиле',
        'source_types': 'Типы источников',
        'source_journal_articles': 'Статьи в журналах',
        'source_repositories': 'Препринты/Репозитории',
        'source_ebooks': 'Электронные книги',
        'source_proceedings': 'Материалы конференций',
        'source_other': 'Другие материалы (без DOI)',
        'source_count': 'Количество',
        'source_examples': 'Примеры',
        'source_no_doi': 'Нет DOI',
        'source_view_link': 'Смотреть',
        'source_doi_available': 'DOI доступен',
        'source_no_link': 'Нет ссылки',
        'coauthor_orcid': 'ORCID',
        'coauthor_scopus': 'Scopus',
        'coauthor_researcherid': 'ResearcherID',
        'coauthor_website': 'Персональный сайт',
        'coauthor_other': 'Другие профили',
        'no_orcid_found': 'ORCID не найден',
        'coauthor_info': 'Информация о соавторе',
        'coauthor_profiles': 'Внешние профили',
        'main_metrics': 'Основные метрики',
        'citations_per_year': 'Цитирований/год',
        'fetching_orcid_profiles': '🆔 Получение профилей ORCID...',
        'orcid_profiles_fetched': '✅ Получено профилей ORCID: {count}',
        'no_orcid_profiles_found': 'Профили ORCID не найдены',
        'analysis_source': '📊 Источник данных для анализа:',
        'analysis_source_orcid_only': '🔒 Только ORCID (безопасный)',
        'analysis_source_orcid_openalex': '🔓 ORCID + OpenAlex (макс. полнота)',
        'analysis_source_help': 'Выберите источник данных для анализа публикаций',
        'temporal_gap_warning': '⚠️ Обнаружен значительный временной разрыв в публикациях!',
        'temporal_gap_detected': 'Разрыв в {gap_years} лет между {gap_start} и {gap_end} годами',
        'temporal_gap_suggestion': 'Это может указывать на: - Ошибочную привязку публикаций другого ученого с таким же именем - Длительный перерыв в научной деятельности',
        'temporal_gap_recommendation': 'Рекомендуется отсечь публикации до {cut_off_year} года',
        'temporal_gap_apply_filter': '📅 Применить фильтр по годам для отчета',
        'temporal_gap_select_period': 'Выберите период анализа:',
        'temporal_gap_publications_total': 'Всего публикаций',
        'temporal_gap_after_filter': 'После фильтрации',
        'temporal_gap_filter_info': '📅 Период: {start_year} - {end_year}',
        'temporal_gap_original_count': 'Исходно: {count} публикаций',
        'temporal_gap_filtered_count': 'Отфильтровано: {count} публикаций',
        'show_filtered_report': 'Показать отчет с фильтрацией',
        'show_original_report': 'Показать исходный отчет (без фильтрации)',
        'temporal_gap_use_filter': 'Использовать фильтр по годам для отчета',
        # ====== НОВЫЕ КЛЮЧИ ДЛЯ JOURNAL ANALYSIS (РУССКИЙ) ======
        'journal_analysis_title': 'Отчет анализа журнала',
        'stage_fetch_publications': 'Этап 1: Получение публикаций журнала',
        'stage_fetch_citing': 'Этап 2: Получение цитирующих работ',
        'stage_fetch_pub_metadata': 'Этап 3: Получение метаданных публикаций',
        'stage_fetch_cite_metadata': 'Этап 4: Получение метаданных цитирующих работ',
        'stage_analyze_report': 'Этап 5: Анализ данных и генерация отчета',
        'stage_publications_found': 'Найдено {count} публикаций',
        'stage_citing_found': 'Найдено {count} цитирующих работ',
        'stage_metadata_fetched': 'Получены метаданные для {count} работ',
        'stage_processing': 'Обработка {current}/{total}...',
        'overview': 'Обзор',
        'total_publications': 'Всего публикаций',
        'total_citations': 'Всего цитирований',
        'avg_citations': 'Среднее цитирований',
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
        'open_access_breakdown': 'Разбивка по открытому доступу',
        'gold': 'Gold',
        'hybrid': 'Hybrid',
        'green': 'Green',
        'bronze': 'Bronze',
        'closed': 'Closed',
        'unknown': 'Unknown',
        'analyzed_articles': 'Анализируемые статьи',
        'author_analysis': 'Анализ авторов',
        'rank': 'Ранг',
        'authors': 'Авторы',
        'publications_count': 'Публикаций',
        'citations_count': 'Цитирований',
        'top_affiliations': 'Топ аффилиаций',
        'geographic_analysis': 'Географический анализ',
        'unique_countries_per_publication': 'Уникальные страны на публикацию',
        'authors_per_country': 'Авторы по странам',
        'collaboration_patterns': 'Паттерны коллабораций',
        'single_country': 'Однострановые',
        'multi_country': 'Международные',
        'collaboration_couples': 'Пары стран в коллаборациях',
        'country_pair': 'Пара стран',
        'frequency': 'Частота',
        'citation_analysis': 'Анализ цитирований',
        'citation_dynamics_by_year': 'Динамика цитирований по годам',
        'publication_year': 'Год публикации',
        'citation_year': 'Год цитирования',
        'citations_count': 'Количество цитирований',
        'first_citation_analysis': 'Анализ первого цитирования',
        'min_lag': 'Мин. задержка (дней)',
        'max_lag': 'Макс. задержка (дней)',
        'avg_lag': 'Сред. задержка (дней)',
        'median_lag': 'Мед. задержка (дней)',
        'cumulative_citations': 'Накопленные цитирования',
        'citation_network_heatmap': 'Тепловая карта сети цитирований',
        'most_cited_publications': 'Наиболее цитируемые публикации',
        'citing_works_analysis': 'Анализ цитирующих работ',
        'total_citing_works': 'Всего цитирующих работ',
        'top_citing_authors': 'Топ цитирующих авторов',
        'top_citing_affiliations': 'Топ цитирующих аффилиаций',
        'top_citing_countries': 'Топ цитирующих стран',
        'top_citing_journals': 'Топ цитирующих журналов',
        'top_citing_publishers': 'Топ цитирующих издательств',
        'topics_analysis': 'Тематический анализ',
        'analyzed_count': 'Кол-во в анализируемых',
        'citing_count': 'Кол-во в цитирующих',
        'analyzed_norm_count': 'Норм. кол-во в анализируемых',
        'citing_norm_count': 'Норм. кол-во в цитирующих',
        'total_norm_count': 'Общее норм. кол-во',
        'first_year': 'Первый год',
        'peak_year': 'Пиковый год',
        'top_cited_topics': 'Топ цитируемых тем',
        'top_cited_subtopics': 'Топ цитируемых подтем',
        'top_cited_fields': 'Топ цитируемых полей',
        'top_cited_domains': 'Топ цитируемых доменов',
        'top_cited_concepts': 'Топ цитируемых концептов',
        'detailed_citations': 'Детальные цитирования',
        'show_citations': 'Показать цитирования',
        'hide_citations': 'Скрыть цитирования',
        'citing_journal': 'Цитирующий журнал',
        'citing_year': 'Год цитирования',
        'citing_date': 'Дата цитирования',
        'citation_lag': 'Задержка цитирования (дней)',
        'all_publications': 'Все публикации',
        'filter_by_year': 'Фильтр по году',
        'filter_by_author': 'Фильтр по автору',
        'filter_by_affiliation': 'Фильтр по аффилиации',
        'filter_by_citations': 'Фильтр по цитированиям (мин)',
        'filter_by_title': 'Фильтр по словам в названии',
        'search_publications': 'Поиск публикаций',
        'all_years': 'Все годы',
        'visible_count': 'Показано {shown} из {total} публикаций',
        'data_source': 'Источник данных: OpenAlex',
        'generated_on': 'Сгенерировано',
        'click_to_toggle': 'Нажмите, чтобы показать/скрыть цитирования',
        'no_citations_found': 'Цитирования не найдены для этой публикации',
        'citations_per_year_label': 'Цитирований/год',
        'journal_issn_label': 'ISSN: {issn}',
        'analysis_period_label': 'Период: {period}',
        'reset_analysis': 'Сбросить анализ',
        'days': 'дней',
        'analysis_data_from_cache': '📦 Использованы данные из предыдущего анализа',
        'regenerate_report': '🔄 Перегенерировать отчет',
        # ====== НОВЫЕ КЛЮЧИ ДЛЯ IMPACT FACTOR (РУССКИЙ) ======
        'impact_factor': 'Импакт-фактор (3-летний)',
        'impact_factor_full': 'IF ({pub_years} → {cite_year})',
        'impact_factor_description': 'Цитирования в {cite_year} статей, опубликованных в {pub_years} / Число статей, опубликованных в {pub_years}',
        'impact_factor_calculation': 'Расчет импакт-фактора для 3-летнего окна',
        'impact_factor_not_applicable': 'Импакт-фактор не применим (период не покрывает целевые годы {years})',
        'citescore': 'CiteScore (4-летний)',
        'citescore_full': 'SC ({years})',
        'citescore_description': 'Цитирования в {years} статей, опубликованных в {years} / Число статей, опубликованных в {years}',
        'citescore_calculation': 'Расчет CiteScore для 4-летнего окна',
        'citescore_not_applicable': 'CiteScore не применим (период не покрывает целевые годы {years})',
        'if_sc_note': 'Рассчитано для периода анализа, покрывающего целевые годы',
        # ====== НОВЫЕ КЛЮЧИ ДЛЯ AUTHOR DISTRIBUTION (РУССКИЙ) ======
        'author_distribution': 'Распределение по числу авторов',
        'author_distribution_analyzed': 'Распределение анализируемых публикаций по числу авторов',
        'author_distribution_citing': 'Распределение цитирующих публикаций по числу авторов',
        'authors_per_paper': 'Авторов на статью',
        'num_papers': 'Количество статей',
        'num_citing_papers': 'Количество цитирующих статей',
        'one_author': '1 автор',
        'two_authors': '2 автора',
        'three_authors': '3 автора',
        'four_plus_authors': '4+ авторов',
        # ====== НОВЫЕ КЛЮЧИ ДЛЯ ORCID IN CITING AUTHORS (РУССКИЙ) ======
        'citing_author_orcid': 'ORCID',
        # ====== НОВЫЕ КЛЮЧИ ДЛЯ ДИНАМИЧЕСКИХ IF И CITESCORE (РУССКИЙ) ======
        'dynamic_metrics_title': 'Динамические метрики',
        'if_dynamic': 'Динамический импакт-фактор (3-летний)',
        'citescore_dynamic': 'Динамический CiteScore (4-летний)',
        'if_dynamic_full': 'Динамический IF ({cite_start} → {cite_end})',
        'citescore_dynamic_full': 'Динамический SC ({start} → {end})',
        'dynamic_window_label': 'Окно: {start} → {end}',
        'dynamic_publications_window': 'Окно публикаций: {start} → {end}',
        'dynamic_citations_window': 'Окно цитирований: {start} → {end}',
        'dynamic_not_applicable': 'Не применимо (период не покрывает окно)',
        'if_dynamic_description': 'Динамический IF: цитирования в (now-1y, now] статей, опубликованных в (now-3y, now-1y] / число статей, опубликованных в (now-3y, now-1y]',
        'citescore_dynamic_description': 'Динамический SC: цитирования в (now-4y, now] статей, опубликованных в (now-4y, now] / число статей, опубликованных в (now-4y, now]',
        'dynamic_as_of': 'на {date}',
        'dynamic_citations_publications': '{citations} цитирований / {publications} публикаций',
        # ====== NEW: GRANTS & FUNDING (РУССКИЙ) ======
        'grants_analysis': 'Гранты и финансирование',
        'grants_and_funding': 'Гранты и финансирование',
        'top_funders': 'Топ фондов',
        'top_awards': 'Топ грантов',
        'top_funders_analyzed': 'Топ фондов (анализируемые)',
        'top_funders_citing': 'Топ фондов (цитирующие)',
        'top_awards_analyzed': 'Топ грантов (анализируемые)',
        'top_awards_citing': 'Топ грантов (цитирующие)',
        'funder': 'Фонд',
        'award_id': 'ID гранта',
        'unique_funders': 'Уникальных фондов',
        'unique_awards': 'Уникальных грантов',
        'unique_funders_analyzed': 'Уникальных фондов (анализируемые)',
        'unique_funders_citing': 'Уникальных фондов (цитирующие)',
        'unique_awards_analyzed': 'Уникальных грантов (анализируемые)',
        'unique_awards_citing': 'Уникальных грантов (цитирующие)',
        'no_grants_data': 'Нет данных о грантах',
        'works_count': 'Работ',
        'citing_publications': 'Цитирующие публикации',
        'filter_by_journal': 'Фильтр по журналу',
        'filter_by_publisher': 'Фильтр по издателю',
        'grants_funding': 'Гранты и финансирование',
        'grant': 'Грант',
        'ror': 'ROR',
        'analyzed_publications_grants': 'Анализируемые публикации — гранты и финансирование',
        'citing_publications_grants': 'Цитирующие публикации — гранты и финансирование',
        'no_cited_publications': 'Нет цитирующих публикаций',
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
        
        /* ===== COLOR SCALE FOR NUMERIC VALUES ===== */
        .color-scale-value {{
            display: inline-block;
            padding: 2px 10px;
            border-radius: 8px;
            font-weight: 600;
            text-align: center;
            min-width: 30px;
            transition: all 0.2s;
        }}
        .color-scale-value:hover {{
            transform: scale(1.05);
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        
        /* ===== HEATMAP CELL COLORS ===== */
        .heatmap-cell {{
            text-align: center;
            padding: 6px 10px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 600;
            transition: all 0.3s;
            min-width: 40px;
        }}
        .heatmap-cell:hover {{
            transform: scale(1.05);
            box-shadow: 0 2px 8px rgba(0,0,0,0.15);
            z-index: 5;
        }}
        
        /* ===== SORTABLE HEADERS ===== */
        th.sortable {{
            cursor: pointer;
            user-select: none;
            position: relative;
        }}
        th.sortable:hover {{
            opacity: 0.85;
        }}
        th.sortable::after {{
            content: ' ↕';
            opacity: 0.4;
            font-size: 10px;
        }}
        th.sortable.asc::after {{
            content: ' ↑';
            opacity: 0.8;
        }}
        th.sortable.desc::after {{
            content: ' ↓';
            opacity: 0.8;
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
# НОВЫЕ ФУНКЦИИ ДЛЯ РАБОТЫ С НАЗВАНИЯМИ ЖУРНАЛОВ
# ============================================

def get_journal_by_issn(issn: str) -> Dict:
    """
    Get journal information by ISSN through OpenAlex API
    Returns dict with journal name and metadata
    """
    # Clean ISSN
    issn = issn.strip().replace("-", "").replace(" ", "")
    if len(issn) == 8:
        issn = f"{issn[:4]}-{issn[4:]}"
    
    url = f"https://api.openalex.org/sources/issn:{issn}"
    params = {"api_key": OPENALEX_API_KEY} if OPENALEX_API_KEY else {}
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        return {
            "success": True,
            "display_name": data.get("display_name"),
            "issn_l": data.get("issn_l"),
            "issn": data.get("issn"),
            "type": data.get("type"),
            "works_count": data.get("works_count"),
            "openalex_id": data.get("id"),
            "homepage_url": data.get("homepage_url"),
            "abbreviation": data.get("abbreviation"),
            "raw_data": data
        }
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return {"success": False, "error": "Journal with this ISSN not found in OpenAlex"}
        else:
            return {"success": False, "error": f"HTTP error: {e}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def generate_journal_abbreviation(full_name: str) -> str:
    """
    Generate abbreviation from full journal name
    - If 1 word: return as is
    - If 2+ words: take first letters of each significant word
    """
    if not full_name:
        return "Journal"
    
    # Clean up the name
    name = full_name.strip()
    
    # Split into words
    words = name.split()
    
    # If only one word, return as is
    if len(words) == 1:
        return name
    
    # Stop words to skip
    stop_words = {'of', 'and', 'the', 'for', 'on', 'at', 'to', 'in', 'with', 'without', 'by', 'from', 'as', 'an', 'a'}
    
    # Take first letters of significant words
    abbreviation_parts = []
    for word in words:
        # Skip stop words
        if word.lower() in stop_words:
            continue
        # Take first letter, uppercase
        if word:
            abbreviation_parts.append(word[0].upper())
    
    # If all words were stop words, use first letters of all words
    if not abbreviation_parts:
        abbreviation_parts = [w[0].upper() for w in words if w]
    
    # If abbreviation is too short (1 letter), use first 2 letters of first word
    if len(abbreviation_parts) == 1:
        first_word = words[0]
        if len(first_word) >= 2:
            return first_word[:2].upper()
        return first_word.upper()
    
    return ''.join(abbreviation_parts)

def get_color_for_value(value: float, max_value: float, min_value: float = 0) -> str:
    """
    Get color from green-yellow-red scale based on value relative to max
    Green = highest value, Yellow = middle, Red = lowest
    """
    if max_value == min_value:
        return "rgba(46, 204, 113, 0.15)"
    
    # Normalize value to 0-1 range
    normalized = (value - min_value) / (max_value - min_value)
    
    # Clamp to 0-1
    normalized = max(0, min(1, normalized))
    
    # Define colors: Red (0) -> Yellow (0.5) -> Green (1)
    if normalized < 0.5:
        # Red to Yellow: (255,0,0) to (255,255,0)
        ratio = normalized / 0.5
        r = 255
        g = int(255 * ratio)
        b = 0
    else:
        # Yellow to Green: (255,255,0) to (0,255,0)
        ratio = (normalized - 0.5) / 0.5
        r = int(255 * (1 - ratio))
        g = 255
        b = 0
    
    # Return with semi-transparent alpha
    return f"rgba({r}, {g}, {b}, 0.25)"

def get_color_for_value_text(value: float, max_value: float, min_value: float = 0) -> str:
    """
    Get color from green-yellow-red scale for text (more opaque for readability)
    """
    if max_value == min_value:
        return "rgba(46, 204, 113, 0.3)"
    
    normalized = (value - min_value) / (max_value - min_value)
    normalized = max(0, min(1, normalized))
    
    if normalized < 0.5:
        ratio = normalized / 0.5
        r = 200
        g = int(200 * ratio)
        b = 50
    else:
        ratio = (normalized - 0.5) / 0.5
        r = int(200 * (1 - ratio))
        g = 200
        b = 50
    
    return f"rgba({r}, {g}, {b}, 0.35)"

def get_heatmap_cell_color(value: float, max_value: float) -> str:
    """
    Get color for heatmap cells using green-yellow-red scale
    Returns transparent for None or 0 values
    """
    if value is None or value == 0 or max_value == 0:
        return "transparent"
    
    normalized = value / max_value
    normalized = max(0, min(1, normalized))
    
    if normalized < 0.5:
        ratio = normalized / 0.5
        r = 200
        g = int(200 * ratio)
        b = 50
    else:
        ratio = (normalized - 0.5) / 0.5
        r = int(200 * (1 - ratio))
        g = 200
        b = 50
    
    return f"rgba({r}, {g}, {b}, 0.45)"

def get_color_scale_html_with_format(value: float, max_value: float, min_value: float = 0, decimals: int = 3) -> str:
    """
    Get color scale HTML with formatted number (for Topics table with 3 decimal places)
    """
    if max_value == min_value:
        return f'<span class="color-scale-value" style="background: rgba(200,200,200,0.15); color: #1a1a1a;">{value:.{decimals}f}</span>'
    
    # Normalize value to 0-1 range
    normalized = (value - min_value) / (max_value - min_value)
    normalized = max(0, min(1, normalized))
    
    # Define colors: Red (0) -> Yellow (0.5) -> Green (1)
    if normalized < 0.5:
        ratio = normalized / 0.5
        r = 200
        g = int(200 * ratio)
        b = 50
    else:
        ratio = (normalized - 0.5) / 0.5
        r = int(200 * (1 - ratio))
        g = 200
        b = 50
    
    bg_color = f"rgba({r}, {g}, {b}, 0.35)"
    
    # Форматируем число с нужным количеством знаков
    formatted_value = f"{value:.{decimals}f}"
    
    return f'<span class="color-scale-value" style="background: {bg_color}; color: #1a1a1a;">{formatted_value}</span>'

def format_ror_link(ror_short: str) -> str:
    """
    Format ROR ID for display in HTML
    
    Args:
        ror_short: ROR ID without https://ror.org/ prefix
        
    Returns:
        str: HTML link to colab.ws
    """
    if not ror_short:
        return '-'
    # Показываем только первые 8 символов для компактности
    display_id = ror_short[:8] + '...' if len(ror_short) > 8 else ror_short
    return f'<a href="https://colab.ws/organizations/{ror_short}" target="_blank" class="doi-link" style="font-family: monospace; font-size: 11px;">{display_id}</a>'

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

def is_author_affiliation(affiliation_name: str, author_affiliations: List[str]) -> bool:
    """Проверяет, является ли аффилиация аффилиацией самого ученого"""
    if not affiliation_name or not author_affiliations:
        return False
    
    aff_normalized = affiliation_name.strip().lower()
    
    for author_aff in author_affiliations:
        if not author_aff:
            continue
        author_aff_normalized = author_aff.strip().lower()
        if aff_normalized == author_aff_normalized:
            return True
        if aff_normalized in author_aff_normalized or author_aff_normalized in aff_normalized:
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

def normalize_author_name_for_grouping(name: str) -> str:
    """
    Нормализует имя автора для группировки (фамилия + первая буква имени)
    
    Примеры:
    - "D.A. Osinkin" → "Osinkin D"
    - "Denis Osinkin" → "Osinkin D"
    - "Dmitry A. Medvedev" → "Medvedev D"
    - "D. Medvedev" → "Medvedev D"
    - "Osinkin D.A." → "Osinkin D"
    """
    if not name:
        return name
    
    name = name.strip()
    
    # Удаляем точки и лишние пробелы
    name = name.replace('.', ' ')
    name = ' '.join(name.split())
    
    parts = name.split()
    
    if len(parts) == 0:
        return name
    
    # Определяем фамилию и инициалы
    # Если имя в формате "Фамилия И.О." или "Фамилия И"
    if len(parts) == 2:
        # Проверяем, является ли первый элемент фамилией (не содержит коротких инициалов)
        first_part = parts[0]
        second_part = parts[1]
        
        # Если первый элемент короткий (1-2 символа) - это инициал, значит фамилия в конце
        if len(first_part) <= 2:
            last_name = second_part
            first_initial = first_part[0]
        else:
            # Иначе фамилия в начале
            last_name = first_part
            first_initial = second_part[0]
        
        return f"{last_name} {first_initial}"
    
    # Если имя в формате "И.О. Фамилия"
    elif len(parts) >= 3:
        # Проверяем, есть ли короткие инициалы в начале
        first_part = parts[0]
        last_part = parts[-1]
        
        if len(first_part) <= 2:
            # Инициалы в начале, фамилия в конце
            last_name = last_part
            first_initial = first_part[0]
        else:
            # Имя в начале, фамилия в конце (обычный порядок)
            last_name = last_part
            first_initial = parts[0][0]
        
        return f"{last_name} {first_initial}"
    
    # Если имя в формате "Фамилия И.О." с точками
    elif len(parts) == 1:
        # Одиночное имя - пробуем разделить по точке
        if '.' in name:
            subparts = name.split('.')
            if len(subparts) >= 2:
                last_name = subparts[0].strip()
                first_initial = subparts[1].strip() if subparts[1] else ''
                if first_initial:
                    return f"{last_name} {first_initial[0]}"
        return name
    
    # Если имя в формате "Фамилия, И."
    elif ',' in name:
        parts_comma = name.split(',')
        if len(parts_comma) == 2:
            last_name = parts_comma[0].strip()
            first_part = parts_comma[1].strip()
            first_initial = first_part[0] if first_part else ''
            return f"{last_name} {first_initial}"
    
    # Fallback: берем последнее слово как фамилию, первое как инициал
    elif len(parts) >= 2:
        last_name = parts[-1]
        first_initial = parts[0][0]
        return f"{last_name} {first_initial}"
    
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
    
    text = text.replace('\n', ' ').replace('\r', ' ')
    text = text.replace(',', ' ').replace(';', ' ')
    
    orcid_pattern = r'\d{4}-\d{4}-\d{4}-\d{3}[\dX]'
    matches = re.findall(orcid_pattern, text, re.IGNORECASE)
    
    url_pattern = r'orcid\.org/(\d{4}-\d{4}-\d{4}-\d{3}[\dX])'
    url_matches = re.findall(url_pattern, text, re.IGNORECASE)
    
    all_orcids = matches + url_matches
    
    cleaned = [clean_orcid(o) for o in all_orcids]
    return list(dict.fromkeys(cleaned))

async def fetch_with_retry(session, url, params=None, headers=None, method='GET'):
    """Выполняет запрос с повторными попытками при ошибке"""
    # ===== NEW: добавляем OpenAlex API key в заголовок для OpenAlex-запросов
    if OPENALEX_API_KEY and "api.openalex.org" in url:
        headers = {**(headers or {}), "Authorization": f"Bearer {OPENALEX_API_KEY}"}
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

def get_cache_path(identifier: str, cache_type: str = "journal") -> str:
    """Возвращает путь к файлу кэша"""
    if not os.path.exists('cache_journal'):
        os.makedirs('cache_journal')
    return f"cache_journal/{identifier}_{cache_type}.json"

def load_from_cache(identifier: str, cache_type: str = "journal") -> Optional[Dict]:
    """Загружает данные из кэша"""
    if not USE_CACHE:
        return None
    
    cache_path = get_cache_path(identifier, cache_type)
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

def save_to_cache(identifier: str, data: Dict, cache_type: str = "journal"):
    """Сохраняет данные в кэш"""
    if not USE_CACHE:
        return
    
    cache_path = get_cache_path(identifier, cache_type)
    try:
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        if SHOW_DEBUG_LOGS:
            print(f"✅ Данные сохранены в кэш: {cache_path}")
    except Exception as e:
        if SHOW_DEBUG_LOGS:
            print(f"⚠️ Ошибка сохранения кэша: {e}")

def normalize_issn(issn_str):
    """Normalize ISSN string to standard format"""
    cleaned = re.sub(r'[^0-9Xx]', '', str(issn_str).strip())
    if len(cleaned) == 8:
        return f"{cleaned[:4]}-{cleaned[4:]}".upper()
    return cleaned.upper()

def smart_request(params, retries=5):
    """Smart request to OpenAlex API with rate limiting and retries"""
    base_url = "https://api.openalex.org/works"
    lock = Lock()
    
    # ===== NEW: добавляем API-ключ, если он есть (не мутируем исходный dict)
    if OPENALEX_API_KEY:
        params = {**params, "api_key": OPENALEX_API_KEY}
    
    for attempt in range(retries):
        try:
            with lock:
                time.sleep(random.uniform(0.2, 0.45))
            
            resp = requests.get(base_url, params=params, timeout=30)
            
            if resp.status_code == 429:
                wait = int(resp.headers.get("Retry-After", 3))
                time.sleep(wait + random.uniform(1, 2))
                continue
                
            if resp.status_code == 200:
                return resp.json()
            
            time.sleep(1.2 ** attempt)
        except:
            time.sleep(1.5 ** attempt)
    return None

def get_work_metadata_batch(work_ids: List[str]) -> List[Dict]:
    """Get metadata for a batch of works by OpenAlex IDs"""
    if not work_ids:
        return []
    
    results = []
    
    for batch in chunks(work_ids, 50):
        id_query = '|'.join(batch)
        params = {
            'filter': f'openalex:{id_query}',
            'per_page': min(len(batch), 100) 
        }
        
        data = smart_request(params)
        if data and data.get('results'):
            results.extend(data['results'])
        
        time.sleep(random.uniform(0.1, 0.3))
    
    return results

def parse_work_metadata(work: Dict) -> Dict:
    """Parse work metadata from OpenAlex API response with ROR information"""
    try:
        parsed = {}
        
        parsed['id'] = work.get('id', '').replace('https://openalex.org/', '')
        parsed['doi'] = work.get('doi', '').replace('https://doi.org/', '')
        parsed['title'] = work.get('title', 'No title')
        parsed['publication_year'] = work.get('publication_year')
        parsed['publication_date'] = work.get('publication_date')
        parsed['cited_by_count'] = work.get('cited_by_count', 0)
        parsed['type'] = work.get('type', 'unknown')
        parsed['raw_type'] = work.get('raw_type', '')
        
        # Open Access
        oa = work.get('open_access', {})
        parsed['is_oa'] = oa.get('is_oa', False)
        parsed['oa_status'] = oa.get('oa_status', 'unknown')
        
        # Primary location (source/journal)
        if work.get('primary_location'):
            source = work['primary_location'].get('source', {})
            parsed['journal_name'] = source.get('display_name', 'Unknown')
            parsed['publisher'] = source.get('host_organization_name') or source.get('publisher', 'Unknown')
            parsed['source_type'] = source.get('type', 'unknown')
            parsed['issn'] = source.get('issn', [])
        else:
            parsed['journal_name'] = 'Unknown'
            parsed['publisher'] = 'Unknown'
            parsed['source_type'] = 'unknown'
            parsed['issn'] = []
        
        # Authors
        authors = []
        author_orcids = []
        authors_with_orcids = []
        authorships_raw = []  # Сохраняем сырые данные об авторах с их аффилиациями
        
        for auth in work.get('authorships', []):
            raw_author_name = auth.get('raw_author_name', '')
            if not raw_author_name:
                author_data = auth.get('author', {})
                raw_author_name = author_data.get('display_name', '')
            
            author_orcid = ''
            author_data = auth.get('author', {})
            if author_data:
                author_orcid = author_data.get('orcid', '')
            
            if raw_author_name:
                authors.append(raw_author_name)
                if author_orcid:
                    author_orcids.append(author_orcid)
                authors_with_orcids.append({
                    'name': raw_author_name,
                    'orcid': author_orcid.replace('https://orcid.org/', '') if author_orcid else None
                })
                
                # Сохраняем сырые данные об авторах с их аффилиациями
                authorships_raw.append({
                    'author': raw_author_name,
                    'orcid': author_orcid,
                    'institutions': auth.get('institutions', []),
                    'countries': auth.get('countries', []),
                    'raw_affiliation_strings': auth.get('raw_affiliation_strings', [])
                })
        
        # Сохраняем authorships_raw для детального анализа стран
        parsed['authorships_raw'] = authorships_raw
        
        # ===== СОБИРАЕМ АФФИЛИАЦИИ ТОЛЬКО ИЗ institutions (С ROR) =====
        affiliations = []
        affiliation_countries = []
        institutions = []
        
        for auth in work.get('authorships', []):
            if auth.get('institutions'):
                for inst in auth['institutions']:
                    inst_name = inst.get('display_name', '')
                    country_code = inst.get('country_code', '')
                    ror = inst.get('ror', '')
                    inst_type = inst.get('type', '')
                    
                    if inst_name and inst_name not in affiliations:
                        affiliations.append(inst_name)
                    
                    if country_code:
                        country_name = get_full_country_name(country_code)
                        if country_name and country_name not in affiliation_countries:
                            affiliation_countries.append(country_name)
                    
                    institutions.append({
                        'id': inst.get('id', ''),
                        'display_name': inst.get('display_name', ''),
                        'country_code': inst.get('country_code', ''),
                        'ror': ror,
                        'type': inst_type
                    })
        
        parsed['authors'] = authors
        parsed['author_orcids'] = author_orcids
        parsed['authors_with_orcids'] = authors_with_orcids
        parsed['author_count'] = len(authors)
        parsed['affiliations'] = affiliations
        parsed['affiliation_countries'] = affiliation_countries
        parsed['institutions'] = institutions
        
        # Определяем основную страну из первой аффилиации
        if affiliation_countries:
            parsed['country'] = affiliation_countries[0]
        elif affiliations:
            parsed['country'] = extract_country_from_affiliation(affiliations[0])
        else:
            parsed['country'] = 'Unknown'
        
        # Topics
        topics_from_field = []
        for topic in work.get('topics', []):
            topic_name = topic.get('display_name', '')
            if topic_name:
                topics_from_field.append(topic_name)
        parsed['topics'] = topics_from_field[:15]
        
        # Concepts
        concepts = []
        concept_levels = {}
        fields = []
        domains = []
        subtopics = []
        subfields = []
        
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
                subfields.append(concept_name)
            elif concept_level == 0:
                subtopics.append(concept_name)
        
        parsed['concepts'] = concepts[:15]
        parsed['concept_levels'] = concept_levels
        parsed['fields'] = fields[:10]
        parsed['domains'] = domains[:5]
        parsed['subtopics'] = subtopics[:20]
        parsed['subfields'] = subfields[:15]
        parsed['topics_old'] = subfields[:15]
        
        # ===== NEW: AWARDS & FUNDERS =====
        awards_raw = work.get('awards', []) or []
        funders_raw = work.get('funders', []) or []
        
        parsed_awards = []
        for aw in awards_raw:
            funder_id = aw.get('funder_id', '') or ''
            funder_id_short = funder_id.replace('https://openalex.org/', '') if funder_id else ''
            funder_award_id = aw.get('funder_award_id', '') or ''
            award_display_name = aw.get('display_name', '') or ''
            funder_display_name = aw.get('funder_display_name', '') or ''
            
            parsed_awards.append({
                'id': aw.get('id', ''),
                'display_name': award_display_name,
                'funder_award_id': funder_award_id,
                'funder_id': funder_id,
                'funder_id_short': funder_id_short,
                'funder_display_name': funder_display_name
            })
        
        parsed_funders = []
        for fd in funders_raw:
            ror = fd.get('ror', '') or ''
            ror_short = ror.replace('https://ror.org/', '') if ror else ''
            fd_id = fd.get('id', '') or ''
            parsed_funders.append({
                'id': fd_id,
                'id_short': fd_id.replace('https://openalex.org/', '') if fd_id else '',
                'display_name': fd.get('display_name', '') or '',
                'ror': ror,
                'ror_short': ror_short
            })
        
        # Build map funder_id -> ror_short for cross-referencing
        funder_id_to_ror_short = {}
        for fd in parsed_funders:
            if fd['id']:
                funder_id_to_ror_short[fd['id']] = fd['ror_short']
        
        # Build map funder_id -> display_name (для fallback если нет display_name в award)
        funder_id_to_display = {}
        for fd in parsed_funders:
            if fd['id']:
                funder_id_to_display[fd['id']] = fd['display_name']
        
        # Enrich awards with ror_short (if available)
        for aw in parsed_awards:
            if not aw.get('funder_display_name'):
                aw['funder_display_name'] = funder_id_to_display.get(aw.get('funder_id', ''), '')
            aw['funder_ror_short'] = funder_id_to_ror_short.get(aw.get('funder_id', ''), '')
        
        # Build display strings list (for tables)
        grants_display = []
        for aw in parsed_awards:
            funder_name = aw.get('funder_display_name') or ''
            award_id = aw.get('funder_award_id') or ''
            award_name = aw.get('display_name') or ''
            
            # Приоритет: display_name + award_id, если display_name есть
            # Иначе: funder_name — award_id
            if award_name and award_id:
                item_str = f"{award_name} [{award_id}]"
                if funder_name:
                    item_str = f"{funder_name} — {item_str}"
            elif award_id and funder_name:
                item_str = f"{funder_name} — {award_id}"
            elif award_id:
                item_str = award_id
            elif award_name:
                item_str = award_name
            elif funder_name:
                item_str = funder_name
            else:
                continue
            grants_display.append(item_str)
        
        parsed['awards'] = parsed_awards
        parsed['funders'] = parsed_funders
        parsed['grants_display'] = grants_display
        
        return parsed
        
    except Exception as e:
        if SHOW_DEBUG_LOGS:
            print(f"⚠️ Ошибка парсинга метаданных работы: {e}")
        return None

# ============================================
# КЛАСС АНАЛИЗАТОРА ЖУРНАЛА
# ============================================

class JournalAnalyzer:
    def __init__(self, issn: str, period, max_workers: int = 6):
        self.issn = normalize_issn(issn)
        self.period = period
        self.max_workers = max_workers
        self.publications = []  # анализируемые статьи
        self.citing_works = {}  # {doi: [citing_dois]}
        self.publications_metadata = {}  # расширенные данные по статьям
        self.citations_metadata = {}  # расширенные данные по цитирующим
        self.analysis_results = {}
        self.lock = Lock()
        self.journal_name = None
        self.journal_abbreviation = None
        
    def parse_period(self):
        """Parse period string to years list or range"""
        if isinstance(self.period, (int, str)):
            if isinstance(self.period, str) and self.period.isdigit():
                return int(self.period)
            return self.period
        
        period_str = str(self.period).strip()
        
        if ',' in period_str:
            return [int(y.strip()) for y in period_str.split(',') if y.strip().isdigit()]
        elif '-' in period_str:
            parts = period_str.split('-')
            if len(parts) == 2:
                return tuple(map(int, [x.strip() for x in parts]))
        
        try:
            return int(period_str)
        except:
            return None
    
    def get_journal_info(self):
        """Get journal information from OpenAlex"""
        result = get_journal_by_issn(self.issn)
        if result.get('success'):
            self.journal_name = result.get('display_name')
            self.journal_abbreviation = generate_journal_abbreviation(self.journal_name)
            if SHOW_DEBUG_LOGS:
                print(f"📖 Журнал: {self.journal_name} ({self.journal_abbreviation})")
        else:
            self.journal_name = f"Journal {self.issn}"
            self.journal_abbreviation = f"J-{self.issn[:4]}"
            if SHOW_DEBUG_LOGS:
                print(f"⚠️ Не удалось получить название журнала: {result.get('error', 'Unknown error')}")
        
        return self.journal_name, self.journal_abbreviation
    
    def get_year_filter(self):
        """Get year filter for OpenAlex API"""
        period = self.parse_period()
        
        if isinstance(period, list):
            return "|".join(f"publication_year:{y}" for y in period)
        elif isinstance(period, tuple):
            return f"publication_year:{period[0]}-{period[1]}"
        else:
            return f"publication_year:{period}"
    
    def fetch_journal_publications(self, progress_callback=None):
        """Stage 1: Fetch all publications from the journal (page-based pagination)"""
        year_filter = self.get_year_filter()
        normalized = self.issn
        
        if SHOW_DEBUG_LOGS:
            print(f"🚀 Запуск сбора публикаций для {normalized}")
        
        publications = []
        page = 1
        per_page = 100  # OpenAlex: максимум 100 для page-based
        total_fetched = 0
        
        while True:
            data = smart_request({
                "filter": f"primary_location.source.issn:{normalized},{year_filter}",
                "per_page": per_page,
                "page": page,
                "select": "id,doi,publication_year,cited_by_count,publication_date"
            })
            
            if not data or not data.get("results"):
                break
            
            for w in data["results"]:
                doi = w.get("doi")
                if doi:
                    doi = doi.replace("https://doi.org/", "")
                publications.append({
                    "DOI": doi,
                    "Year": w.get("publication_year"),
                    "Cited_by_count": w.get("cited_by_count", 0),
                    "Publication_Date": w.get("publication_date"),
                    "OpenAlex_ID": w.get("id", "").replace("https://openalex.org/", "")
                })
            
            total_fetched += len(data["results"])
            if progress_callback:
                total_count = data.get("meta", {}).get("count", total_fetched)
                progress_callback(total_fetched, total_count)
            
            # Проверяем, есть ли следующая страница
            results_count = len(data["results"])
            meta = data.get("meta", {})
            total_count = meta.get("count", 0)
            
            # Прекращаем, если получили меньше per_page или достигли общего количества
            if results_count < per_page or total_fetched >= total_count:
                break
            
            page += 1
            
            # Защита: page * per_page не должен превышать 10 000
            if page * per_page > 10000:
                if SHOW_DEBUG_LOGS:
                    print(f"⚠️ Достигнут лимит page-based пагинации (10 000). Собрано {len(publications)} публикаций.")
                break
        
        self.publications = publications
        
        if SHOW_DEBUG_LOGS:
            print(f"✅ Загружено публикаций: {len(self.publications)}")
                   
        return publications
    
    def fetch_citing_works(self, progress_callback=None):
        """Stage 2: Fetch citing works for all publications in parallel"""
        if not self.publications:
            return {}
        
        citing_map = {}
        to_process = [row for row in self.publications if row.get('Cited_by_count', 0) > 0 and row.get('DOI')]
        
        if SHOW_DEBUG_LOGS:
            print(f"⚡ Запуск параллельного сбора цитирующих...")
        
        citing_workers = max(1, self.max_workers // 5) # скорость обработки
        if SHOW_DEBUG_LOGS:
            print(f"   Используется {citing_workers} потоков (было {self.max_workers})")
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_doi = {}
            for row in to_process:
                oa_id = row.get('OpenAlex_ID')
                doi = row.get('DOI')
                if oa_id:
                    future = executor.submit(self._get_citing_dois_batch, oa_id)
                    future_to_doi[future] = doi
            
            total = len(future_to_doi)
            completed = 0
            
            for future in as_completed(future_to_doi):
                doi = future_to_doi[future]
                try:
                    citing_map[doi] = future.result()
                except:
                    citing_map[doi] = []
                
                completed += 1
                if progress_callback:
                    progress_callback(completed, total)
        
        self.citing_works = citing_map
        
        if SHOW_DEBUG_LOGS:
            total_citing = sum(len(v) for v in citing_map.values())
            print(f"✅ Собрано цитирующих работ: {total_citing}")
        
        return citing_map
    
    def _get_citing_dois_batch(self, oa_id: str) -> List[str]:
        """Get citing DOIs for a single work (page-based pagination)"""
        citing = []
        page = 1
        per_page = 100  # OpenAlex: максимум 100 для page-based
        
        for _ in range(6):  # ограничение на количество страниц
            data = smart_request({
                "filter": f"cites:{oa_id}",
                "per_page": per_page,
                "page": page,
                "select": "doi,publication_date"
            })
            
            if not data or not data.get("results"):
                break
            
            for item in data["results"]:
                d = item.get("doi")
                if d:
                    citing.append({
                        'doi': d.replace("https://doi.org/", ""),
                        'publication_date': item.get('publication_date')
                    })
            
            # Проверяем, есть ли следующая страница
            results_count = len(data["results"])
            meta = data.get("meta", {})
            total_count = meta.get("count", 0)
            
            if results_count < per_page:
                break
            
            page += 1
            
            # Защита: лимит page-based пагинации
            if page * per_page > 10000:
                break
            
            time.sleep(25)  # замедление на 2 этапе
        
        return citing
    
    def fetch_publications_metadata(self, progress_callback=None):
        """Stage 3: Fetch extended metadata for all publications"""
        if not self.publications:
            return {}
        
        work_ids = [p.get('OpenAlex_ID') for p in self.publications if p.get('OpenAlex_ID')]
        
        if not work_ids:
            return {}
        
        if SHOW_DEBUG_LOGS:
            print(f"📖 Получение метаданных для {len(work_ids)} публикаций...")
        
        all_metadata = []
        total = len(work_ids)
        
        for batch in chunks(work_ids, 50):
            batch_metadata = get_work_metadata_batch(batch)
            all_metadata.extend(batch_metadata)
            
            if progress_callback:
                progress_callback(len(all_metadata), total)
        
        # Создаем словарь для быстрого доступа
        metadata_dict = {}
        for meta in all_metadata:
            parsed = parse_work_metadata(meta)
            if parsed and parsed.get('doi'):
                metadata_dict[parsed['doi']] = parsed
        
        self.publications_metadata = metadata_dict
        
        if SHOW_DEBUG_LOGS:
            print(f"✅ Получено метаданных для {len(metadata_dict)} публикаций")
        
        return metadata_dict
    
    def fetch_citations_metadata(self, progress_callback=None):
        """Stage 4: Fetch extended metadata for all citing works (page-based pagination)"""
        if not self.citing_works:
            return {}
        
        # Собираем все уникальные DOI цитирующих работ
        all_citing_dois = set()
        for citing_list in self.citing_works.values():
            for cite in citing_list:
                if isinstance(cite, dict) and cite.get('doi'):
                    all_citing_dois.add(cite['doi'])
                elif isinstance(cite, str):
                    all_citing_dois.add(cite)
        
        if not all_citing_dois:
            return {}
        
        citing_dois_list = list(all_citing_dois)
        
        if SHOW_DEBUG_LOGS:
            print(f"📖 Получение метаданных для {len(citing_dois_list)} цитирующих работ...")
        
        all_metadata = []
        total = len(citing_dois_list)
        
        for batch in chunks(citing_dois_list, 50):
            doi_query = '|'.join(batch)
            page = 1
            per_page = min(len(batch), 100)
            
            while True:
                params = {
                    'filter': f'doi:{doi_query}',
                    'per_page': per_page,
                    'page': page
                }
                data = smart_request(params)
                if data and data.get('results'):
                    all_metadata.extend(data['results'])
                    results_count = len(data['results'])
                    if results_count < per_page:
                        break
                    page += 1
                    if page * per_page > 10000:
                        break
                else:
                    break
            
            if progress_callback:
                progress_callback(len(all_metadata), total)
            
            time.sleep(random.uniform(0.1, 0.3))
        
        # Создаем словарь для быстрого доступа
        metadata_dict = {}
        for meta in all_metadata:
            parsed = parse_work_metadata(meta)
            if parsed and parsed.get('doi'):
                metadata_dict[parsed['doi']] = parsed
        
        self.citations_metadata = metadata_dict
        
        if SHOW_DEBUG_LOGS:
            print(f"✅ Получено метаданных для {len(metadata_dict)} цитирующих работ")
        
        return metadata_dict
    
    def analyze_data(self, progress_callback=None):
        """Stage 5: Analyze all collected data"""
        if SHOW_DEBUG_LOGS:
            print("📊 Анализ собранных данных...")
        
        results = {}
        
        # 1. Basic metrics
        results['basic_metrics'] = self._analyze_basic_metrics()
        
        # 2. Author analysis
        results['author_analysis'] = self._analyze_authors()
        
        # 3. Affiliation analysis
        results['affiliation_analysis'] = self._analyze_affiliations()
        
        # 4. Geographic analysis
        results['geographic_analysis'] = self._analyze_geographic()
        
        # 5. Citation analysis
        results['citation_analysis'] = self._analyze_citations()
        
        # 6. Citing works analysis
        results['citing_analysis'] = self._analyze_citing_works()
        
        # 7. Topics analysis
        results['topics_analysis'] = self._analyze_topics()
        
        # 8. Detailed citations
        results['detailed_citations'] = self._get_detailed_citations()
        
        # 9. Author distribution (analyzed and citing)
        results['author_distribution'] = self._analyze_author_distribution()
        
        # 10. Impact Factor (3-year)
        results['impact_factor'] = self._calculate_impact_factor()
        
        # 11. CiteScore (4-year)
        results['citescore'] = self._calculate_citescore()
        
        # 12. Dynamic Impact Factor (3-year) — привязан к текущей дате
        results['impact_factor_dynamic'] = self._calculate_impact_factor_dynamic()
        
        # 13. Dynamic CiteScore (4-year) — привязан к текущей дате
        results['citescore_dynamic'] = self._calculate_citescore_dynamic()
        
        # ===== NEW: 14. Grants & Funding analysis
        results['grants_analysis'] = self._analyze_grants()
        
        self.analysis_results = results
        
        if progress_callback:
            progress_callback(100, 100)
        
        return results
    
    # ===== NEW: метод анализа грантов и фондов
    def _analyze_grants(self) -> Dict:
        """
        Analyze grants (awards) and funders separately for analyzed and citing publications.
        Aggregation is per-work (unique works), not per-author.
        
        Returns:
            Dict with 'analyzed' and 'citing' sections, each containing:
                - top_funders: [{funder_id, name, ror_short, count}]  (top-30 by unique works)
                - top_awards: [{funder_id, funder_name, award_id, display_name, count}] (top-30 by unique works)
                - unique_funders_count: int
                - unique_awards_count: int
        """
        def _aggregate(metadata_dict: Dict[str, Dict]) -> Dict:
            funders_by_id = defaultdict(lambda: {
                'name': '',
                'ror_short': '',
                'count': 0
            })
            awards_by_key = defaultdict(lambda: {
                'funder_id': '',
                'funder_name': '',
                'award_id': '',
                'display_name': '',
                'count': 0
            })
            
            for doi, meta in metadata_dict.items():
                if not meta:
                    continue
                
                # ---- Funders: агрегируем по funder_id, считаем уникальные работы ----
                seen_funder_ids = set()
                for fd in meta.get('funders', []) or []:
                    fid = fd.get('id', '')
                    if not fid:
                        continue
                    if fid in seen_funder_ids:
                        continue
                    seen_funder_ids.add(fid)
                    
                    funders_by_id[fid]['count'] += 1
                    if not funders_by_id[fid]['name']:
                        funders_by_id[fid]['name'] = fd.get('display_name', '') or ''
                    if not funders_by_id[fid]['ror_short']:
                        funders_by_id[fid]['ror_short'] = fd.get('ror_short', '') or ''
                
                # Также включим фонды, у которых есть только awards (без funders[])
                for aw in meta.get('awards', []) or []:
                    fid = aw.get('funder_id', '')
                    if not fid:
                        continue
                    if fid in seen_funder_ids:
                        continue
                    seen_funder_ids.add(fid)
                    
                    funders_by_id[fid]['count'] += 1
                    if not funders_by_id[fid]['name']:
                        funders_by_id[fid]['name'] = aw.get('funder_display_name', '') or ''
                    if not funders_by_id[fid]['ror_short']:
                        funders_by_id[fid]['ror_short'] = aw.get('funder_ror_short', '') or ''
                
                # ---- Awards: агрегируем по паре (funder_id, funder_award_id) ----
                seen_award_keys = set()
                for aw in meta.get('awards', []) or []:
                    fid = aw.get('funder_id', '') or ''
                    award_id = aw.get('funder_award_id', '') or ''
                    display_name = aw.get('display_name', '') or ''
                    funder_name = aw.get('funder_display_name', '') or ''
                    
                    # Если нет ни funder_id, ни award_id — пропускаем
                    if not fid and not award_id:
                        continue
                    
                    key = (fid, award_id)
                    if key in seen_award_keys:
                        continue
                    seen_award_keys.add(key)
                    
                    entry = awards_by_key[key]
                    entry['count'] += 1
                    entry['funder_id'] = fid
                    entry['award_id'] = award_id
                    if not entry['display_name'] and display_name:
                        entry['display_name'] = display_name
                    if not entry['funder_name'] and funder_name:
                        entry['funder_name'] = funder_name
            
            # All funders (no limit)
            sorted_funders = sorted(
                [
                    {
                        'funder_id': fid,
                        'name': data['name'],
                        'ror_short': data['ror_short'],
                        'count': data['count']
                    }
                    for fid, data in funders_by_id.items()
                    if data['count'] > 0
                ],
                key=lambda x: x['count'],
                reverse=True
            )
            
            # All awards (no limit)
            sorted_awards = sorted(
                [
                    {
                        'funder_id': data['funder_id'],
                        'funder_name': data['funder_name'],
                        'award_id': data['award_id'],
                        'display_name': data['display_name'],
                        'count': data['count']
                    }
                    for data in awards_by_key.values()
                    if data['count'] > 0
                ],
                key=lambda x: x['count'],
                reverse=True
            )
            
            # Unique counters (across all data, not only top-30)
            unique_funders_count = sum(1 for d in funders_by_id.values() if d['count'] > 0)
            unique_awards_count = sum(1 for d in awards_by_key.values() if d['count'] > 0)
            
            return {
                'top_funders': sorted_funders,
                'top_awards': sorted_awards,
                'unique_funders_count': unique_funders_count,
                'unique_awards_count': unique_awards_count
            }
        
        analyzed = _aggregate(self.publications_metadata)
        citing = _aggregate(self.citations_metadata)
        
        if SHOW_DEBUG_LOGS:
            print(f"📊 Grants (analyzed): {analyzed['unique_funders_count']} funders, {analyzed['unique_awards_count']} awards")
            print(f"📊 Grants (citing): {citing['unique_funders_count']} funders, {citing['unique_awards_count']} awards")
        
        return {
            'analyzed': analyzed,
            'citing': citing
        }
    
    def _calculate_impact_factor(self) -> Optional[Dict]:
        """
        Calculate 3-year Impact Factor (IF)
        
        IF = (Citations in YEAR-1 to articles published in YEAR-3 and YEAR-2) / 
             (Number of articles published in YEAR-3 and YEAR-2)
        
        For analysis year 2026:
        - Publications window: 2023-2024
        - Citation window: 2025
        
        Returns dict with IF value and metadata, or None if period doesn't cover required years
        """
        current_year = datetime.now().year
        
        # Target years for IF
        pub_years = [current_year - 3, current_year - 2]  # e.g., [2023, 2024]
        cite_year = current_year - 1  # e.g., 2025
        
        # Get period years
        period_years = self._get_period_years_set()
        
        # Check if all required years are covered by the analysis period
        required_years = set(pub_years + [cite_year])
        if not required_years.issubset(period_years):
            if SHOW_DEBUG_LOGS:
                print(f"⚠️ IF не применим: период не покрывает целевые годы {sorted(required_years)}")
            return None
        
        # Get publications in pub_years
        pub_dois = []
        for p in self.publications:
            year = p.get('Year')
            if year in pub_years:
                doi = p.get('DOI')
                if doi:
                    pub_dois.append(doi)
        
        if not pub_dois:
            if SHOW_DEBUG_LOGS:
                print(f"⚠️ IF = 0: нет публикаций за {pub_years}")
            return {
                'value': 0.0,
                'citations': 0,
                'publications': 0,
                'pub_years': pub_years,
                'cite_year': cite_year,
                'years_covered': sorted(required_years),
                'period_covers': True
            }
        
        # Count citations in cite_year to publications in pub_years
        citation_count = 0
        for doi in pub_dois:
            citing_list = self.citing_works.get(doi, [])
            for cite in citing_list:
                cite_doi = cite.get('doi') if isinstance(cite, dict) else cite
                cite_meta = self.citations_metadata.get(cite_doi, {})
                cite_pub_year = cite_meta.get('publication_year')
                if cite_pub_year == cite_year:
                    citation_count += 1
        
        if SHOW_DEBUG_LOGS:
            print(f"📊 IF: цитирований {citation_count} за {cite_year} на {len(pub_dois)} статей за {pub_years}")
        
        if len(pub_dois) == 0:
            return {
                'value': 0.0,
                'citations': citation_count,
                'publications': 0,
                'pub_years': pub_years,
                'cite_year': cite_year,
                'years_covered': sorted(required_years),
                'period_covers': True
            }
        
        if_value = citation_count / len(pub_dois)
        
        return {
            'value': if_value,
            'citations': citation_count,
            'publications': len(pub_dois),
            'pub_years': pub_years,
            'cite_year': cite_year,
            'years_covered': sorted(required_years),
            'period_covers': True
        }
    
    def _calculate_citescore(self) -> Optional[Dict]:
        """
        Calculate 4-year CiteScore (SC)
        
        SC = (Citations within YEAR-4 to YEAR-1 to articles published in YEAR-4 to YEAR-1) /
             (Number of articles published in YEAR-4 to YEAR-1)
        
        For analysis year 2026:
        - Window: 2022-2025
        
        Returns dict with SC value and metadata, or None if period doesn't cover required years
        """
        current_year = datetime.now().year
        
        # Target years for SC (4-year window)
        window_years = list(range(current_year - 4, current_year))  # e.g., [2022, 2023, 2024, 2025]
        
        # Get period years
        period_years = self._get_period_years_set()
        
        # Check if all required years are covered by the analysis period
        required_years = set(window_years)
        if not required_years.issubset(period_years):
            if SHOW_DEBUG_LOGS:
                print(f"⚠️ SC не применим: период не покрывает целевые годы {sorted(required_years)}")
            return None
        
        # Get publications in window_years
        pub_dois = []
        for p in self.publications:
            year = p.get('Year')
            if year in window_years:
                doi = p.get('DOI')
                if doi:
                    pub_dois.append(doi)
        
        if not pub_dois:
            if SHOW_DEBUG_LOGS:
                print(f"⚠️ SC = 0: нет публикаций за {window_years}")
            return {
                'value': 0.0,
                'citations': 0,
                'publications': 0,
                'window_years': window_years,
                'years_covered': sorted(required_years),
                'period_covers': True
            }
        
        # Count citations within window_years to publications in window_years
        citation_count = 0
        for doi in pub_dois:
            citing_list = self.citing_works.get(doi, [])
            for cite in citing_list:
                cite_doi = cite.get('doi') if isinstance(cite, dict) else cite
                cite_meta = self.citations_metadata.get(cite_doi, {})
                cite_pub_year = cite_meta.get('publication_year')
                if cite_pub_year in window_years:
                    citation_count += 1
        
        if SHOW_DEBUG_LOGS:
            print(f"📊 SC: цитирований {citation_count} за {window_years} на {len(pub_dois)} статей за {window_years}")
        
        if len(pub_dois) == 0:
            return {
                'value': 0.0,
                'citations': citation_count,
                'publications': 0,
                'window_years': window_years,
                'years_covered': sorted(required_years),
                'period_covers': True
            }
        
        sc_value = citation_count / len(pub_dois)
        
        return {
            'value': sc_value,
            'citations': citation_count,
            'publications': len(pub_dois),
            'window_years': window_years,
            'years_covered': sorted(required_years),
            'period_covers': True
        }
    
    def _calculate_impact_factor_dynamic(self) -> Optional[Dict]:
        """
        Calculate dynamic 3-year Impact Factor (IF) anchored to the current date.
        
        Definition:
            Publications window: (now - 3y, now - 1y]
            Citations window:    (now - 1y, now]
            IF_dyn = citations in citations window to articles from publications window
                     / number of articles in publications window
        
        Left bound is exclusive, right bound is inclusive.
        
        Returns dict with value and metadata, or None if period doesn't cover the window.
        """
        now = datetime.now()
        
        pub_window_start = now - relativedelta(years=3)
        pub_window_end = now - relativedelta(years=1)
        cite_window_start = pub_window_end
        cite_window_end = now
        
        period_years = self._get_period_years_set()
        
        # Check that all years touched by the windows are covered by the analysis period
        def years_touched(start_dt: datetime, end_dt: datetime) -> Set[int]:
            """Return set of calendar years touched by the interval (start, end]."""
            years = set()
            y = start_dt.year
            while y <= end_dt.year:
                years.add(y)
                y += 1
            return years
        
        required_years = years_touched(pub_window_start, pub_window_end) | \
                         years_touched(cite_window_start, cite_window_end)
        
        if not required_years.issubset(period_years):
            if SHOW_DEBUG_LOGS:
                print(f"⚠️ Dynamic IF не применим: период не покрывает окно {sorted(required_years)}")
            return {
                'value': None,
                'citations': 0,
                'publications': 0,
                'pub_window_start': pub_window_start.strftime('%Y-%m-%d'),
                'pub_window_end': pub_window_end.strftime('%Y-%m-%d'),
                'cite_window_start': cite_window_start.strftime('%Y-%m-%d'),
                'cite_window_end': cite_window_end.strftime('%Y-%m-%d'),
                'period_covers': False,
                'not_applicable_reason': 'period_does_not_cover_window'
            }
        
        # Collect publications within publications window using publication_date
        pub_dois = []
        for p in self.publications:
            doi = p.get('DOI')
            if not doi:
                continue
            # publication_date is preferred; fallback to year-based midpoint
            pub_date_str = p.get('Publication_Date')
            pub_date = None
            if pub_date_str:
                try:
                    pub_date = datetime.fromisoformat(pub_date_str[:10])
                except Exception:
                    pub_date = None
            if pub_date is None:
                # Fallback: try to use metadata
                meta = self.publications_metadata.get(doi, {})
                meta_date_str = meta.get('publication_date')
                if meta_date_str:
                    try:
                        pub_date = datetime.fromisoformat(meta_date_str[:10])
                    except Exception:
                        pub_date = None
            if pub_date is None:
                # If we cannot determine the date, skip this publication
                continue
            # Interval is (start, end]
            if pub_window_start < pub_date <= pub_window_end:
                pub_dois.append(doi)
        
        # Count citations in citations window to publications from publications window
        citation_count = 0
        for pub_doi in pub_dois:
            citing_list = self.citing_works.get(pub_doi, [])
            for cite in citing_list:
                cite_doi = cite.get('doi') if isinstance(cite, dict) else cite
                cite_date_str = cite.get('publication_date') if isinstance(cite, dict) else None
                cite_date = None
                if cite_date_str:
                    try:
                        cite_date = datetime.fromisoformat(cite_date_str[:10])
                    except Exception:
                        cite_date = None
                if cite_date is None:
                    # Fallback: use metadata
                    cite_meta = self.citations_metadata.get(cite_doi, {})
                    meta_date_str = cite_meta.get('publication_date')
                    if meta_date_str:
                        try:
                            cite_date = datetime.fromisoformat(meta_date_str[:10])
                        except Exception:
                            cite_date = None
                if cite_date is None:
                    continue
                # Interval is (start, end]
                if cite_window_start < cite_date <= cite_window_end:
                    citation_count += 1
        
        publications_count = len(pub_dois)
        
        if publications_count == 0:
            if SHOW_DEBUG_LOGS:
                print(f"⚠️ Dynamic IF = 0: нет публикаций в окне ({pub_window_start.date()}, {pub_window_end.date()}]")
            return {
                'value': 0.0,
                'citations': citation_count,
                'publications': 0,
                'pub_window_start': pub_window_start.strftime('%Y-%m-%d'),
                'pub_window_end': pub_window_end.strftime('%Y-%m-%d'),
                'cite_window_start': cite_window_start.strftime('%Y-%m-%d'),
                'cite_window_end': cite_window_end.strftime('%Y-%m-%d'),
                'period_covers': True,
                'not_applicable_reason': None
            }
        
        if_value = citation_count / publications_count
        
        if SHOW_DEBUG_LOGS:
            print(f"📊 Dynamic IF: {citation_count} / {publications_count} = {if_value:.3f} "
                  f"(pub window: {pub_window_start.date()} → {pub_window_end.date()}, "
                  f"cite window: {cite_window_start.date()} → {cite_window_end.date()})")
        
        return {
            'value': if_value,
            'citations': citation_count,
            'publications': publications_count,
            'pub_window_start': pub_window_start.strftime('%Y-%m-%d'),
            'pub_window_end': pub_window_end.strftime('%Y-%m-%d'),
            'cite_window_start': cite_window_start.strftime('%Y-%m-%d'),
            'cite_window_end': cite_window_end.strftime('%Y-%m-%d'),
            'period_covers': True,
            'not_applicable_reason': None
        }
    
    def _calculate_citescore_dynamic(self) -> Optional[Dict]:
        """
        Calculate dynamic 4-year CiteScore (SC) anchored to the current date.
        
        Definition (variant A — всё окно скользит к now()):
            Window: (now - 4y, now]
            SC_dyn = citations in (now - 4y, now] to articles published in (now - 4y, now]
                     / number of articles published in (now - 4y, now]
        
        Left bound is exclusive, right bound is inclusive.
        
        Returns dict with value and metadata, or None if period doesn't cover the window.
        """
        now = datetime.now()
        
        window_start = now - relativedelta(years=4)
        window_end = now
        
        period_years = self._get_period_years_set()
        
        def years_touched(start_dt: datetime, end_dt: datetime) -> Set[int]:
            """Return set of calendar years touched by the interval (start, end]."""
            years = set()
            y = start_dt.year
            while y <= end_dt.year:
                years.add(y)
                y += 1
            return years
        
        required_years = years_touched(window_start, window_end)
        
        if not required_years.issubset(period_years):
            if SHOW_DEBUG_LOGS:
                print(f"⚠️ Dynamic SC не применим: период не покрывает окно {sorted(required_years)}")
            return {
                'value': None,
                'citations': 0,
                'publications': 0,
                'window_start': window_start.strftime('%Y-%m-%d'),
                'window_end': window_end.strftime('%Y-%m-%d'),
                'period_covers': False,
                'not_applicable_reason': 'period_does_not_cover_window'
            }
        
        # Collect publications within window
        pub_dois = []
        for p in self.publications:
            doi = p.get('DOI')
            if not doi:
                continue
            pub_date_str = p.get('Publication_Date')
            pub_date = None
            if pub_date_str:
                try:
                    pub_date = datetime.fromisoformat(pub_date_str[:10])
                except Exception:
                    pub_date = None
            if pub_date is None:
                meta = self.publications_metadata.get(doi, {})
                meta_date_str = meta.get('publication_date')
                if meta_date_str:
                    try:
                        pub_date = datetime.fromisoformat(meta_date_str[:10])
                    except Exception:
                        pub_date = None
            if pub_date is None:
                continue
            if window_start < pub_date <= window_end:
                pub_dois.append(doi)
        
        # Count citations within the same window to publications from the window
        citation_count = 0
        for pub_doi in pub_dois:
            citing_list = self.citing_works.get(pub_doi, [])
            for cite in citing_list:
                cite_doi = cite.get('doi') if isinstance(cite, dict) else cite
                cite_date_str = cite.get('publication_date') if isinstance(cite, dict) else None
                cite_date = None
                if cite_date_str:
                    try:
                        cite_date = datetime.fromisoformat(cite_date_str[:10])
                    except Exception:
                        cite_date = None
                if cite_date is None:
                    cite_meta = self.citations_metadata.get(cite_doi, {})
                    meta_date_str = cite_meta.get('publication_date')
                    if meta_date_str:
                        try:
                            cite_date = datetime.fromisoformat(meta_date_str[:10])
                        except Exception:
                            cite_date = None
                if cite_date is None:
                    continue
                if window_start < cite_date <= window_end:
                    citation_count += 1
        
        publications_count = len(pub_dois)
        
        if publications_count == 0:
            if SHOW_DEBUG_LOGS:
                print(f"⚠️ Dynamic SC = 0: нет публикаций в окне ({window_start.date()}, {window_end.date()}]")
            return {
                'value': 0.0,
                'citations': citation_count,
                'publications': 0,
                'window_start': window_start.strftime('%Y-%m-%d'),
                'window_end': window_end.strftime('%Y-%m-%d'),
                'period_covers': True,
                'not_applicable_reason': None
            }
        
        sc_value = citation_count / publications_count
        
        if SHOW_DEBUG_LOGS:
            print(f"📊 Dynamic SC: {citation_count} / {publications_count} = {sc_value:.3f} "
                  f"(window: {window_start.date()} → {window_end.date()})")
        
        return {
            'value': sc_value,
            'citations': citation_count,
            'publications': publications_count,
            'window_start': window_start.strftime('%Y-%m-%d'),
            'window_end': window_end.strftime('%Y-%m-%d'),
            'period_covers': True,
            'not_applicable_reason': None
        }
    
    def _get_period_years_set(self) -> Set[int]:
        """Get set of years covered by the analysis period"""
        period = self.parse_period()
        
        if isinstance(period, int):
            return {period}
        elif isinstance(period, list):
            return set(period)
        elif isinstance(period, tuple) and len(period) == 2:
            start, end = period
            return set(range(start, end + 1))
        else:
            # Fallback: extract years from publications
            years = [p.get('Year') for p in self.publications if p.get('Year')]
            if years:
                return set(years)
            return set()
    
    def _analyze_basic_metrics(self) -> Dict:
        """Analyze basic metrics"""
        pubs = self.publications
        
        total_pubs = len(pubs)
        total_citations = sum(p.get('Cited_by_count', 0) for p in pubs)
        citations = [p.get('Cited_by_count', 0) for p in pubs]
        
        # h-index
        citations_sorted = sorted([c for c in citations if c > 0], reverse=True)
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
        i10_index = sum(1 for c in citations if c >= 10)
        i100_index = sum(1 for c in citations if c >= 100)
        
        # Years
        years = [p.get('Year') for p in pubs if p.get('Year')]
        active_years = len(set(years)) if years else 0
        
        # Open Access
        oa_statuses = []
        for p in pubs:
            doi = p.get('DOI')
            if doi and doi in self.publications_metadata:
                meta = self.publications_metadata[doi]
                oa_statuses.append(meta.get('oa_status', 'unknown'))
            else:
                oa_statuses.append('unknown')
        
        oa_breakdown = dict(Counter(oa_statuses))
        oa_count = sum(1 for s in oa_statuses if s not in ['closed', 'unknown'])
        oa_percentage = (oa_count / total_pubs * 100) if total_pubs > 0 else 0
        
        # Unique authors, affiliations, countries
        all_authors = set()
        all_affiliations = set()
        all_countries = set()
        total_authors = 0
        total_affiliations = 0
        total_countries = 0
        
        for p in pubs:
            doi = p.get('DOI')
            if doi and doi in self.publications_metadata:
                meta = self.publications_metadata[doi]
                authors = meta.get('authors', [])
                affiliations = meta.get('affiliations', [])
                countries = meta.get('affiliation_countries', [])
                
                all_authors.update(authors)
                all_affiliations.update(affiliations)
                all_countries.update(countries)
                total_authors += len(authors)
                total_affiliations += len(affiliations)
                total_countries += len(set(countries))
        
        avg_authors = total_authors / total_pubs if total_pubs > 0 else 0
        avg_affiliations = total_affiliations / total_pubs if total_pubs > 0 else 0
        avg_countries = total_countries / total_pubs if total_pubs > 0 else 0
        
        # International collaboration rate
        international_papers = 0
        for p in pubs:
            doi = p.get('DOI')
            if doi and doi in self.publications_metadata:
                meta = self.publications_metadata[doi]
                countries = set(meta.get('affiliation_countries', []))
                if len(countries) > 1:
                    international_papers += 1
        
        international_rate = (international_papers / total_pubs * 100) if total_pubs > 0 else 0
        
        # Citing works metrics
        all_citing_authors = set()
        all_citing_affiliations = set()
        all_citing_countries = set()
        all_citing_journals = set()
        all_citing_publishers = set()
        
        for citing_list in self.citing_works.values():
            for cite in citing_list:
                doi = cite.get('doi') if isinstance(cite, dict) else cite
                if doi and doi in self.citations_metadata:
                    meta = self.citations_metadata[doi]
                    all_citing_authors.update(meta.get('authors', []))
                    all_citing_affiliations.update(meta.get('affiliations', []))
                    all_citing_countries.update(meta.get('affiliation_countries', []))
                    all_citing_journals.add(meta.get('journal_name', 'Unknown'))
                    all_citing_publishers.add(meta.get('publisher', 'Unknown'))
        
        # Topics distribution - используем настоящие Topics
        all_topics_analyzed = set()
        all_topics_citing = set()
        
        for p in pubs:
            doi = p.get('DOI')
            if doi and doi in self.publications_metadata:
                meta = self.publications_metadata[doi]
                all_topics_analyzed.update(meta.get('topics', []))
        
        for citing_list in self.citing_works.values():
            for cite in citing_list:
                doi = cite.get('doi') if isinstance(cite, dict) else cite
                if doi and doi in self.citations_metadata:
                    meta = self.citations_metadata[doi]
                    all_topics_citing.update(meta.get('topics', []))
        
        return {
            'total_publications': total_pubs,
            'total_citations': total_citations,
            'h_index': h_index,
            'g_index': g_index,
            'i10_index': i10_index,
            'i100_index': i100_index,
            'avg_citations': total_citations / total_pubs if total_pubs > 0 else 0,
            'median_citations': np.median(citations) if citations else 0,
            'max_citations': max(citations) if citations else 0,
            'oa_percentage': oa_percentage,
            'oa_breakdown': oa_breakdown,
            'active_years': active_years,
            'unique_authors': len(all_authors),
            'unique_affiliations': len(all_affiliations),
            'unique_countries': len(all_countries),
            'avg_authors_per_paper': avg_authors,
            'avg_affiliations_per_paper': avg_affiliations,
            'avg_countries_per_paper': avg_countries,
            'international_collaboration_rate': international_rate,
            'unique_citing_authors': len(all_citing_authors),
            'unique_citing_affiliations': len(all_citing_affiliations),
            'unique_citing_countries': len(all_citing_countries),
            'unique_citing_journals': len(all_citing_journals),
            'unique_citing_publishers': len(all_citing_publishers),
            'unique_topics_analyzed': len(all_topics_analyzed),
            'unique_topics_citing': len(all_topics_citing)
        }
    
    def _analyze_authors(self) -> Dict:
        """Analyze authors with ORCID-based deduplication and name merging
        
        Логика объединения авторов:
        1. Если у автора есть ORCID — группируем строго по ORCID.
           Разные варианты имени (например, "Aleksander N. Volkov" и 
           "Alexander N. Volkov") объединяются в одну запись.
        2. Если ORCID нет — группируем по нормализованному имени.
        3. Для отображения имени используем "умное" слияние:
           - различающиеся части имени объединяются через скобки:
             "Aleksander (Alexander) N. Volkov"
             "Yuri (Yuriy) P. Zaikov"
           - если варианты имени идентичны — используется как есть.
        """
        
        def merge_names(names: Set[str]) -> str:
            """Объединяет варианты имени в одну строку формата 'A (B) C Surname'."""
            names = [n.strip() for n in names if n and n.strip()]
            if not names:
                return ''
            if len(names) == 1:
                return names[0]
            
            # Разбиваем каждое имя на токены
            tokenized = [n.split() for n in names]
            
            # Проверяем, одинаковая ли длина у всех вариантов
            lengths = {len(t) for t in tokenized}
            if len(lengths) != 1:
                # Разная структура (разное число слов) — просто берём самое длинное
                return max(names, key=len)
            
            n_tokens = tokenized[0].__len__()
            merged_tokens = []
            
            for i in range(n_tokens):
                variants_at_pos = {t[i] for t in tokenized}
                if len(variants_at_pos) == 1:
                    # Все варианты совпадают на этой позиции
                    merged_tokens.append(variants_at_pos.pop())
                else:
                    # Различаются — объединяем через скобки
                    # Сортируем для стабильного порядка (первым — более длинный/частый)
                    sorted_variants = sorted(variants_at_pos, key=lambda x: (-len(x), x))
                    primary = sorted_variants[0]
                    others = sorted_variants[1:]
                    merged_tokens.append(f"{primary} ({', '.join(others)})")
            
            return ' '.join(merged_tokens)
        
        # Структура: key -> {'names': set, 'publications', 'citations',
        #                     'orcid', 'affiliations': set, 'countries': set}
        author_stats: Dict[str, Dict] = {}
        orcid_to_key: Dict[str, str] = {}
        normalized_to_keys: Dict[str, List[str]] = defaultdict(list)
        
        for p in self.publications:
            doi = p.get('DOI')
            if not doi or doi not in self.publications_metadata:
                continue
            
            meta = self.publications_metadata[doi]
            authors_with_orcids = meta.get('authors_with_orcids', [])
            citations = p.get('Cited_by_count', 0)
            
            # Дедупликация внутри одной публикации: 
            # один и тот же автор может встретиться в разных authorships
            seen_keys_in_work = set()
            
            for auth in authors_with_orcids:
                name = (auth.get('name') or '').strip()
                orcid = auth.get('orcid')
                
                if not name:
                    continue
                
                normalized = normalize_author_name_for_grouping(name)
                
                # --- Определяем ключ группировки ---
                key = None
                
                if orcid:
                    # Приоритет — ORCID
                    if orcid in orcid_to_key:
                        key = orcid_to_key[orcid]
                    else:
                        # ORCID новый; проверяем, нет ли уже записи
                        # с таким же нормализованным именем и без ORCID
                        for existing_key in normalized_to_keys.get(normalized, []):
                            if existing_key in author_stats and not author_stats[existing_key]['orcid']:
                                key = existing_key
                                author_stats[key]['orcid'] = orcid
                                orcid_to_key[orcid] = key
                                break
                        
                        if key is None:
                            key = f"orcid:{orcid}"
                            author_stats[key] = {
                                'names': set(),
                                'publications': 0,
                                'citations': 0,
                                'orcid': orcid,
                                'affiliations': set(),
                                'countries': set()
                            }
                            orcid_to_key[orcid] = key
                            normalized_to_keys[normalized].append(key)
                else:
                    # Нет ORCID — группируем по нормализованному имени
                    for existing_key in normalized_to_keys.get(normalized, []):
                        if existing_key in author_stats and not author_stats[existing_key]['orcid']:
                            key = existing_key
                            break
                    
                    if key is None:
                        key = f"name:{normalized}:{len(author_stats)}"
                        author_stats[key] = {
                            'names': set(),
                            'publications': 0,
                            'citations': 0,
                            'orcid': None,
                            'affiliations': set(),
                            'countries': set()
                        }
                        normalized_to_keys[normalized].append(key)
                
                # --- Обновляем запись автора ---
                entry = author_stats[key]
                entry['names'].add(name)
                
                # Публикации и цитирования учитываем один раз на работу
                if key not in seen_keys_in_work:
                    seen_keys_in_work.add(key)
                    entry['publications'] += 1
                    entry['citations'] += citations
                    
                    for aff in meta.get('affiliations', []):
                        if aff:
                            entry['affiliations'].add(aff)
                    for country in meta.get('affiliation_countries', []):
                        if country:
                            entry['countries'].add(country)
        
        # --- Формируем итоговый список ---
        author_list = []
        for key, data in author_stats.items():
            merged_name = merge_names(data['names'])
            author_list.append({
                'name': merged_name,
                'publications': data['publications'],
                'citations': data['citations'],
                'orcid': data['orcid'],
                'affiliations': sorted(data['affiliations'])[:5],
                'countries': sorted(data['countries'])[:5]
            })
        
        author_list.sort(key=lambda x: (x['publications'], x['citations']), reverse=True)
        
        return {'top_authors': author_list}
    
    def _analyze_affiliations(self) -> Dict:
        """Analyze affiliations with ROR-based aggregation (per work, not per author)"""
        # Используем ROR ID для группировки аффилиаций
        affiliations_by_ror = defaultdict(lambda: {
            'name': '',
            'count': 0,
            'ror': '',
            'ror_short': ''
        })
        
        for p in self.publications:
            doi = p.get('DOI')
            if doi and doi in self.publications_metadata:
                meta = self.publications_metadata[doi]
                
                # Собираем уникальные ROR ID для этой работы
                work_ror_ids = set()
                
                for inst in meta.get('institutions', []):
                    ror = inst.get('ror', '')
                    inst_name = inst.get('display_name', '')
                    
                    if ror:
                        work_ror_ids.add(ror)
                    elif inst_name:
                        # Если нет ROR, используем название как ключ
                        key = f"no_ror_{inst_name}"
                        work_ror_ids.add(key)
                
                # Теперь увеличиваем счетчики для каждого уникального ROR в этой работе
                for ror_id in work_ror_ids:
                    if ror_id.startswith('no_ror_'):
                        # Это запись без ROR
                        inst_name = ror_id.replace('no_ror_', '')
                        if not affiliations_by_ror.get(ror_id):
                            affiliations_by_ror[ror_id] = {
                                'name': inst_name,
                                'count': 0,
                                'ror': '',
                                'ror_short': ''
                            }
                        affiliations_by_ror[ror_id]['count'] += 1
                    else:
                        # Это ROR ID
                        # Находим название института для этого ROR
                        inst_name = ''
                        for inst in meta.get('institutions', []):
                            if inst.get('ror', '') == ror_id:
                                inst_name = inst.get('display_name', '')
                                break
                        
                        if not affiliations_by_ror[ror_id]['name']:
                            ror_short = ror_id.replace('https://ror.org/', '') if ror_id else ''
                            affiliations_by_ror[ror_id] = {
                                'name': inst_name,
                                'count': 0,
                                'ror': ror_id,
                                'ror_short': ror_short
                            }
                        affiliations_by_ror[ror_id]['count'] += 1
        
        # Сортируем по частоте
        sorted_affs = sorted(
            [{
                'name': data['name'],
                'count': data['count'],
                'ror': data['ror'],
                'ror_short': data['ror_short']
            } for data in affiliations_by_ror.values() if data['count'] > 0],
            key=lambda x: x['count'],
            reverse=True
        )
        
        return {
            'top_affiliations': sorted_affs
        }
    
    def _analyze_geographic(self) -> Dict:
        """Analyze geographic data with two metrics: Unique (per work) and Author-based (per author)"""
        
        # ---- METRIC 1: UNIQUE COUNTRIES PER WORK (сколько стран в каждой публикации) ----
        countries_per_work = []  # список количества стран для каждой работы
        work_country_details = []  # детали по каждой работе: список стран
        
        # ---- METRIC 2: AUTHOR-BASED COUNTRIES (Individual Distribution) ----
        authors_per_country = defaultdict(int)
        
        # Collaboration Patterns
        single_country_papers = 0
        multi_country_papers = 0
        
        # Collaboration Couples
        country_pairs = defaultdict(int)
        
        # ---- Собираем данные по странам для каждой работы ----
        for p in self.publications:
            doi = p.get('DOI')
            if doi and doi in self.publications_metadata:
                meta = self.publications_metadata[doi]
                
                # Собираем уникальные страны для этой работы
                work_countries = set()
                
                # Используем authorships_raw для получения стран каждого автора
                authorships = meta.get('authorships_raw', [])
                
                if authorships:
                    for auth in authorships:
                        for inst in auth.get('institutions', []):
                            country_code = inst.get('country_code', '')
                            if country_code:
                                country_name = get_full_country_name(country_code)
                                if country_name and country_name != 'Unknown':
                                    work_countries.add(country_name)
                                    authors_per_country[country_name] += 1
                else:
                    # Fallback: используем institutions
                    for inst in meta.get('institutions', []):
                        country_code = inst.get('country_code', '')
                        if country_code:
                            country_name = get_full_country_name(country_code)
                            if country_name and country_name != 'Unknown':
                                work_countries.add(country_name)
                                # Приблизительно: каждый автор из этой страны
                                for _ in meta.get('authors', []):
                                    authors_per_country[country_name] += 1
                
                # Если нет данных по странам, используем affiliation_countries
                if not work_countries:
                    work_countries = set(meta.get('affiliation_countries', []))
                    work_countries = {c for c in work_countries if c and c != 'Unknown'}
                
                # Сохраняем данные по этой работе
                if work_countries:
                    countries_per_work.append({
                        'work_doi': doi,
                        'countries': list(work_countries),
                        'count': len(work_countries)
                    })
                    
                    # Collaboration Patterns
                    if len(work_countries) == 1:
                        single_country_papers += 1
                    else:
                        multi_country_papers += 1
                    
                    # Collaboration Couples
                    country_list = list(work_countries)
                    for i in range(len(country_list)):
                        for j in range(i+1, len(country_list)):
                            pair = tuple(sorted([country_list[i], country_list[j]]))
                            country_pairs[pair] += 1
        
        # ---- ВЫЧИСЛЯЕМ СТАТИСТИКУ ПО UNIQUE COUNTRIES PER PUBLICATION ----
        country_counts = [item['count'] for item in countries_per_work]
        
        unique_countries_stats = {
            'avg': np.mean(country_counts) if country_counts else 0,
            'min': min(country_counts) if country_counts else 0,
            'max': max(country_counts) if country_counts else 0,
            'total_works': len(country_counts)
        }
        
        # ---- АГРЕГИРУЕМ ДАННЫЕ ПО СТРАНАМ ----
        # Для каждой страны считаем:
        # 1. Уникальные публикации (в скольких работах встречается страна)
        # 2. Количество авторов из этой страны
        
        country_stats = defaultdict(lambda: {
            'unique_works': 0,
            'authors_count': 0,
            'work_dois': set()
        })
        
        for work_data in countries_per_work:
            for country in work_data['countries']:
                country_stats[country]['unique_works'] += 1
                country_stats[country]['work_dois'].add(work_data['work_doi'])
        
        # Добавляем данные по авторам из authors_per_country
        for country, author_count in authors_per_country.items():
            country_stats[country]['authors_count'] = author_count
        
        # Преобразуем в список для сортировки
        country_stats_list = []
        for country, stats in country_stats.items():
            country_stats_list.append({
                'country': country,
                'unique_works': stats['unique_works'],
                'authors_count': stats['authors_count'],
                'work_dois': list(stats['work_dois'])
            })
        
        # Сортируем по уникальным публикациям (по убыванию)
        country_stats_list.sort(key=lambda x: x['unique_works'], reverse=True)
        
        # Сортируем пары стран по частоте
        sorted_pairs = sorted(country_pairs.items(), key=lambda x: x[1], reverse=True)[:20]
        
        return {
            'country_stats': country_stats_list,  # Страны с двумя метриками
            'unique_countries_per_publication': unique_countries_stats,  # Статистика по уникальным странам
            'collaboration_patterns': {
                'single_country': single_country_papers,
                'multi_country': multi_country_papers,
                'total': single_country_papers + multi_country_papers,
                'single_country_ratio': single_country_papers / (single_country_papers + multi_country_papers) if (single_country_papers + multi_country_papers) > 0 else 0
            },
            'collaboration_couples': [{'country1': pair[0], 'country2': pair[1], 'frequency': freq} for pair, freq in sorted_pairs]
        }
    
    def _analyze_citations(self) -> Dict:
        """Analyze citations with proper year filtering for heatmap"""
        
        # Get analysis period bounds
        period = self.parse_period()
        if isinstance(period, tuple):
            min_year = period[0]
            max_year = period[1]
        elif isinstance(period, list):
            min_year = min(period) if period else None
            max_year = max(period) if period else None
        else:
            min_year = period if isinstance(period, int) else None
            max_year = datetime.now().year
        
        # If min_year is None, use earliest publication year
        if min_year is None:
            years = [p.get('Year') for p in self.publications if p.get('Year')]
            min_year = min(years) if years else datetime.now().year - 5
        
        current_year = datetime.now().year
        
        # Citation Dynamics by Year
        dynamics = defaultdict(lambda: defaultdict(int))
        
        # First Citation Analysis
        first_citation_lags = []
        
        # Cumulative Citations
        cumulative = defaultdict(int)
        
        # Citation Network Heatmap - will be filtered
        heatmap = defaultdict(lambda: defaultdict(int))
        
        # Get publication dates
        pub_dates = {}
        for p in self.publications:
            doi = p.get('DOI')
            if doi and doi in self.publications_metadata:
                meta = self.publications_metadata[doi]
                pub_dates[doi] = {
                    'year': meta.get('publication_year'),
                    'date': meta.get('publication_date')
                }
        
        # Process citations
        for pub_doi, citing_list in self.citing_works.items():
            pub_year = pub_dates.get(pub_doi, {}).get('year')
            pub_date = pub_dates.get(pub_doi, {}).get('date')
            
            if not pub_year:
                continue
            
            # Skip if publication year is before analysis period
            if pub_year < min_year:
                continue
            
            for cite in citing_list:
                cite_doi = cite.get('doi') if isinstance(cite, dict) else cite
                cite_date = cite.get('publication_date') if isinstance(cite, dict) else None
                
                # Get citing work metadata
                cite_meta = self.citations_metadata.get(cite_doi, {})
                cite_year = cite_meta.get('publication_year')
                
                if not cite_year:
                    continue
                
                # Skip if citation year is before analysis period or before publication year
                if cite_year < min_year or cite_year < pub_year:
                    continue
                
                # Skip if citation year is in the future
                if cite_year > current_year:
                    continue
                
                # Citation Dynamics
                dynamics[pub_year][cite_year] += 1
                
                # Heatmap - only for valid years
                heatmap[pub_year][cite_year] += 1
                
                # Cumulative Citations
                cumulative[cite_year] += 1
                
                # First Citation Analysis (in days)
                if pub_date and cite_date:
                    try:
                        pub_dt = datetime.fromisoformat(pub_date[:10])
                        cite_dt = datetime.fromisoformat(cite_date[:10])
                        lag = (cite_dt - pub_dt).days
                        if lag >= 0:
                            first_citation_lags.append(lag)
                    except:
                        pass
        
        # Build complete dynamics matrix with zeros for all year combinations
        all_pub_years = sorted([y for y in dynamics.keys() if y >= min_year])
        all_cite_years = sorted([y for y in set([y for sub in dynamics.values() for y in sub.keys()]) if y >= min_year])
        
        # If no citation years, use publication years within period
        if not all_cite_years:
            all_cite_years = all_pub_years
        
        # Create complete dynamics matrix with zeros
        complete_dynamics = []
        for pub_year in all_pub_years:
            for cite_year in all_cite_years:
                if cite_year < pub_year:
                    # Skip impossible citations (from future to past)
                    continue
                value = dynamics[pub_year].get(cite_year, 0)
                complete_dynamics.append({
                    'publication_year': pub_year,
                    'citation_year': cite_year,
                    'citations_count': value
                })
        
        # Sort dynamics by publication year and citation year
        sorted_dynamics = sorted(complete_dynamics, key=lambda x: (x['publication_year'], x['citation_year']))
        
        # Cumulative sorted by year
        sorted_cumulative = sorted(cumulative.items())
        cumulative_list = []
        running_total = 0
        for year, count in sorted_cumulative:
            if year >= min_year and year <= current_year:
                running_total += count
                cumulative_list.append({
                    'year': year,
                    'citations': running_total
                })
        
        # First citation stats
        first_citation_stats = {}
        if first_citation_lags:
            first_citation_stats = {
                'min': min([lag for lag in first_citation_lags if lag > 0]) if any(lag > 0 for lag in first_citation_lags) else 0,
                'max': max(first_citation_lags),
                'avg': np.mean(first_citation_lags),
                'median': np.median(first_citation_lags),
                'count': len(first_citation_lags)
            }
        
        # ===== HEATMAP DATA WITH PROPER FILTERING =====
        # Get all years from min_year to current_year
        all_years = list(range(min_year, current_year + 1))
        
        heatmap_data = []
        for pub_year in all_years:
            row = {'publication_year': pub_year}
            has_data = False
            
            for cite_year in all_years:
                # Skip impossible citations (citation year < publication year)
                if cite_year < pub_year:
                    row[cite_year] = None  # Use None for empty cells
                    continue
                
                # Check if we have data for this combination
                value = heatmap[pub_year].get(cite_year, 0)
                if value > 0:
                    has_data = True
                    row[cite_year] = value
                else:
                    row[cite_year] = 0
            
            # Only include rows that have at least one citation
            if has_data or pub_year in dynamics:
                heatmap_data.append(row)
        
        # Also include publication years that have citations but might not be in all_years
        # (e.g., if min_year was adjusted)
        for pub_year in dynamics.keys():
            if pub_year < min_year or pub_year > current_year:
                continue
            if not any(row.get('publication_year') == pub_year for row in heatmap_data):
                row = {'publication_year': pub_year}
                for cite_year in all_years:
                    if cite_year < pub_year:
                        row[cite_year] = None
                    else:
                        value = heatmap[pub_year].get(cite_year, 0)
                        row[cite_year] = value if value > 0 else 0
                heatmap_data.append(row)
        
        # Sort heatmap data by publication year
        heatmap_data.sort(key=lambda x: x['publication_year'])
        
        # Most Cited Publications
        most_cited = []
        for p in sorted(self.publications, key=lambda x: x.get('Cited_by_count', 0), reverse=True)[:20]:
            doi = p.get('DOI')
            meta = self.publications_metadata.get(doi, {})
            citations = p.get('Cited_by_count', 0)
            year = p.get('Year')
            
            # Skip if publication year is before min_year
            if year and year < min_year:
                continue
            
            # Calculate citations per year
            if year:
                years_since = datetime.now().year - year + 1
                citations_per_year = citations / max(years_since, 1)
            else:
                citations_per_year = 0
            
            authors = meta.get('authors', [])
            authors_str = ', '.join(authors[:3])
            if len(authors) > 3:
                authors_str += f' +{len(authors)-3} more'
            
            most_cited.append({
                'title': meta.get('title', 'No title'),
                'year': year,
                'citations': citations,
                'citations_per_year': citations_per_year,
                'authors': authors_str,
                'doi': doi,
                'journal': meta.get('journal_name', 'Unknown')
            })
        
        return {
            'dynamics': sorted_dynamics,
            'first_citation_stats': first_citation_stats,
            'cumulative': cumulative_list,
            'heatmap': heatmap_data,
            'heatmap_years': all_years,  # Добавляем список всех лет для HTML
            'most_cited': most_cited[:10]
        }
    
    def _analyze_citing_works(self) -> Dict:
        """Analyze citing works with ROR-based affiliation aggregation (per work, not per author)
        and author aggregation with ORCID deduplication and name normalization"""
        
        total_citing = sum(len(v) for v in self.citing_works.values())
        
        # Используем ROR ID для группировки аффилиаций
        affiliations_by_ror = defaultdict(lambda: {
            'name': '',
            'count': 0,
            'ror': '',
            'ror_short': ''
        })
        
        # Также собираем статистику по авторам, странам, журналам, издателям
        # Используем словарь для агрегации авторов с дедупликацией
        # Структура: key -> {'name': best_name, 'orcid': orcid, 'count': count, 'names_seen': set()}
        authors_aggregated = {}
        
        # Для быстрого поиска по ORCID
        orcid_to_key = {}
        # Для быстрого поиска по нормализованному имени
        normalized_to_keys = defaultdict(list)
        
        countries = defaultdict(int)
        journals = defaultdict(int)
        publishers = defaultdict(int)
        
        for citing_list in self.citing_works.values():
            for cite in citing_list:
                doi = cite.get('doi') if isinstance(cite, dict) else cite
                if doi and doi in self.citations_metadata:
                    meta = self.citations_metadata[doi]
                    
                    # --- АВТОРЫ (считаем каждого автора, группируем по ORCID и нормализованному имени) ---
                    authors_with_orcids = meta.get('authors_with_orcids', [])
                    for auth in authors_with_orcids:
                        name = auth.get('name', '')
                        orcid = auth.get('orcid')
                        
                        if not name:
                            continue
                        
                        # Нормализуем имя для группировки
                        normalized_name = normalize_author_name_for_grouping(name)
                        
                        # Определяем ключ для группировки
                        # Приоритет: ORCID > нормализованное имя
                        key = None
                        
                        # 1. Если есть ORCID, ищем по ORCID
                        if orcid:
                            if orcid in orcid_to_key:
                                key = orcid_to_key[orcid]
                            else:
                                # Проверяем, есть ли уже автор с таким нормализованным именем
                                for existing_key in normalized_to_keys.get(normalized_name, []):
                                    if existing_key in authors_aggregated:
                                        # Нашли автора с таким же нормализованным именем
                                        # Проверяем, есть ли у него ORCID
                                        existing_orcid = authors_aggregated[existing_key].get('orcid')
                                        if not existing_orcid:
                                            # У существующего нет ORCID, перепривязываем к нему
                                            key = existing_key
                                            # Обновляем ORCID у существующего
                                            authors_aggregated[key]['orcid'] = orcid
                                            # Обновляем маппинг ORCID
                                            orcid_to_key[orcid] = key
                                            break
                                
                                if key is None:
                                    # Создаем новую запись
                                    key = f"orcid_{orcid}"
                                    authors_aggregated[key] = {
                                        'name': name,
                                        'orcid': orcid,
                                        'count': 0,
                                        'names_seen': set([name])
                                    }
                                    orcid_to_key[orcid] = key
                                    normalized_to_keys[normalized_name].append(key)
                        
                        # 2. Если нет ORCID, используем нормализованное имя
                        else:
                            # Ищем по нормализованному имени
                            found = False
                            for existing_key in normalized_to_keys.get(normalized_name, []):
                                if existing_key in authors_aggregated:
                                    # Проверяем, не привязан ли уже этот автор к другому ORCID
                                    # Если у найденного есть ORCID, мы не можем объединить без ORCID
                                    existing_orcid = authors_aggregated[existing_key].get('orcid')
                                    if not existing_orcid:
                                        key = existing_key
                                        found = True
                                        break
                            
                            if not found:
                                # Создаем новую запись
                                key = f"name_{normalized_name}_{len(authors_aggregated)}"
                                authors_aggregated[key] = {
                                    'name': name,
                                    'orcid': None,
                                    'count': 0,
                                    'names_seen': set([name])
                                }
                                normalized_to_keys[normalized_name].append(key)
                        
                        # Увеличиваем счетчик для автора
                        if key:
                            authors_aggregated[key]['count'] += 1
                            # Сохраняем все варианты имени для выбора лучшего
                            authors_aggregated[key]['names_seen'].add(name)
                            
                            # Если у нас есть более полное имя, обновляем
                            current_name = authors_aggregated[key]['name']
                            # Предпочитаем имена с ORCID или более длинные
                            if orcid and (not current_name or len(name) > len(current_name)):
                                authors_aggregated[key]['name'] = name
                            elif not orcid and len(name) > len(current_name):
                                authors_aggregated[key]['name'] = name
                    
                    # --- СТРАНЫ (уникальные страны на работу) ---
                    work_countries = set(meta.get('affiliation_countries', []))
                    for country in work_countries:
                        countries[country] += 1
                    
                    # --- ЖУРНАЛЫ ---
                    journal = meta.get('journal_name', 'Unknown')
                    journals[journal] += 1
                    
                    # --- ИЗДАТЕЛИ ---
                    publisher = meta.get('publisher', 'Unknown')
                    publishers[publisher] += 1
                    
                    # --- АФФИЛИАЦИИ (УНИКАЛЬНЫЕ НА РАБОТУ, а не на автора) ---
                    # Собираем уникальные ROR ID для этой работы
                    work_ror_ids = set()
                    
                    for inst in meta.get('institutions', []):
                        ror = inst.get('ror', '')
                        inst_name = inst.get('display_name', '')
                        
                        if ror:
                            work_ror_ids.add(ror)
                        elif inst_name:
                            # Если нет ROR, используем название как ключ
                            key = f"no_ror_{inst_name}"
                            work_ror_ids.add(key)
                    
                    # Теперь увеличиваем счетчики для каждого уникального ROR в этой работе
                    for ror_id in work_ror_ids:
                        if ror_id.startswith('no_ror_'):
                            # Это запись без ROR
                            inst_name = ror_id.replace('no_ror_', '')
                            if not affiliations_by_ror.get(ror_id):
                                affiliations_by_ror[ror_id] = {
                                    'name': inst_name,
                                    'count': 0,
                                    'ror': '',
                                    'ror_short': ''
                                }
                            affiliations_by_ror[ror_id]['count'] += 1
                        else:
                            # Это ROR ID
                            # Находим название института для этого ROR
                            inst_name = ''
                            for inst in meta.get('institutions', []):
                                if inst.get('ror', '') == ror_id:
                                    inst_name = inst.get('display_name', '')
                                    break
                            
                            if not affiliations_by_ror[ror_id]['name']:
                                ror_short = ror_id.replace('https://ror.org/', '') if ror_id else ''
                                affiliations_by_ror[ror_id] = {
                                    'name': inst_name,
                                    'count': 0,
                                    'ror': ror_id,
                                    'ror_short': ror_short
                                }
                            affiliations_by_ror[ror_id]['count'] += 1
        
        # Сортируем аффилиации по частоте
        top_affiliations = sorted(
            [{
                'name': data['name'],
                'count': data['count'],
                'ror': data['ror'],
                'ror_short': data['ror_short']
            } for data in affiliations_by_ror.values() if data['count'] > 0],
            key=lambda x: x['count'],
            reverse=True
        )[:30]
        
        # Сортируем авторов по частоте
        top_authors = sorted(
            [{
                'name': data['name'],
                'orcid': data['orcid'],
                'count': data['count']
            } for data in authors_aggregated.values() if data['count'] > 0],
            key=lambda x: x['count'],
            reverse=True
        )[:30]
        
        top_countries = sorted(countries.items(), key=lambda x: x[1], reverse=True)[:30]
        top_journals = sorted(journals.items(), key=lambda x: x[1], reverse=True)[:30]
        top_publishers = sorted(publishers.items(), key=lambda x: x[1], reverse=True)[:30]
        
        return {
            'total_citing_works': total_citing,
            'top_authors': [{'name': item['name'], 'orcid': item['orcid'], 'count': item['count']} for item in top_authors],
            'top_affiliations': top_affiliations,
            'top_countries': [{'name': name, 'count': count} for name, count in top_countries],
            'top_journals': [{'name': name, 'count': count} for name, count in top_journals],
            'top_publishers': [{'name': name, 'count': count} for name, count in top_publishers]
        }
    
    def _analyze_topics(self) -> Dict:
        """Analyze topics using real Topics from OpenAlex topics field"""
        # Collect topics from analyzed publications - считаем КОЛИЧЕСТВО ПУБЛИКАЦИЙ
        analyzed_topics = defaultdict(lambda: {
            'count': 0,
            'years': [],
            'citations': []  # оставляем для статистики, но для top_cited используем count
        })
        
        # Collect topics from citing works - считаем КОЛИЧЕСТВО ЦИТИРУЮЩИХ РАБОТ
        citing_topics = defaultdict(lambda: {
            'count': 0,
            'years': [],
            'citations': []
        })
        
        # Process analyzed publications
        for p in self.publications:
            doi = p.get('DOI')
            if doi and doi in self.publications_metadata:
                meta = self.publications_metadata[doi]
                year = p.get('Year')
                citations = p.get('Cited_by_count', 0)
                
                for topic in meta.get('topics', []):
                    analyzed_topics[topic]['count'] += 1  # ← СЧИТАЕМ КОЛИЧЕСТВО
                    if year:
                        analyzed_topics[topic]['years'].append(year)
                    analyzed_topics[topic]['citations'].append(citations)
        
        # Process citing works - считаем КОЛИЧЕСТВО ЦИТИРУЮЩИХ РАБОТ
        for citing_list in self.citing_works.values():
            for cite in citing_list:
                doi = cite.get('doi') if isinstance(cite, dict) else cite
                if doi and doi in self.citations_metadata:
                    meta = self.citations_metadata[doi]
                    year = meta.get('publication_year')
                    citations = meta.get('cited_by_count', 0)
                    
                    for topic in meta.get('topics', []):
                        citing_topics[topic]['count'] += 1  # ← СЧИТАЕМ КОЛИЧЕСТВО
                        if year:
                            citing_topics[topic]['years'].append(year)
                        citing_topics[topic]['citations'].append(citations)
        
        # Combine topics
        all_topics = set(analyzed_topics.keys()) | set(citing_topics.keys())
        
        topic_results = []
        total_analyzed = len(self.publications)
        total_citing = sum(len(v) for v in self.citing_works.values())
        
        for topic in all_topics:
            a_count = analyzed_topics[topic]['count']
            c_count = citing_topics[topic]['count']
            
            a_norm = a_count / total_analyzed if total_analyzed > 0 else 0
            c_norm = c_count / total_citing if total_citing > 0 else 0
            total_norm = (a_count + c_count) / (total_analyzed + total_citing) if (total_analyzed + total_citing) > 0 else 0
            
            years = analyzed_topics[topic]['years'] + citing_topics[topic]['years']
            first_year = min(years) if years else None
            
            if years:
                year_counts = Counter(years)
                peak_year = max(year_counts.items(), key=lambda x: x[1])[0]
            else:
                peak_year = None
            
            topic_results.append({
                'topic': topic,
                'analyzed_count': a_count,
                'citing_count': c_count,
                'analyzed_norm_count': a_norm,
                'citing_norm_count': c_norm,
                'total_norm_count': total_norm,
                'first_year': first_year,
                'peak_year': peak_year
            })
        
        # Sort by total normalized count
        topic_results.sort(key=lambda x: x['total_norm_count'], reverse=True)
        
        # ===== ИСПРАВЛЕННЫЕ ФУНКЦИИ ДЛЯ TOP CITED =====
        # Теперь считаем КОЛИЧЕСТВО ПУБЛИКАЦИЙ, а не сумму цитирований
        
        def get_top_cited_count(items_key):
            """Считает количество публикаций по каждому топику/концепту"""
            counter = defaultdict(int)
            
            # Анализируемые публикации
            for p in self.publications:
                doi = p.get('DOI')
                if doi and doi in self.publications_metadata:
                    meta = self.publications_metadata[doi]
                    for item in meta.get(items_key, []):
                        counter[item] += 1  # ← СЧИТАЕМ ПУБЛИКАЦИИ
            
            # Цитирующие работы
            for citing_list in self.citing_works.values():
                for cite in citing_list:
                    doi = cite.get('doi') if isinstance(cite, dict) else cite
                    if doi and doi in self.citations_metadata:
                        meta = self.citations_metadata[doi]
                        for item in meta.get(items_key, []):
                            counter[item] += 1  # ← СЧИТАЕМ ЦИТИРУЮЩИЕ РАБОТЫ
            
            return sorted(counter.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            'topics': topic_results[:30],
            'top_cited_topics': get_top_cited_count('topics'),  # ← ИСПРАВЛЕНО
            'top_cited_subtopics': get_top_cited_count('subtopics'),  # ← ИСПРАВЛЕНО
            'top_cited_fields': get_top_cited_count('fields'),  # ← ИСПРАВЛЕНО
            'top_cited_domains': get_top_cited_count('domains'),  # ← ИСПРАВЛЕНО
            'top_cited_concepts': get_top_cited_count('concepts')  # ← ИСПРАВЛЕНО
        }
    
    def _get_detailed_citations(self) -> Dict:
        """Get detailed citations for each publication"""
        detailed = {}
        
        for p in self.publications:
            doi = p.get('DOI')
            if not doi:
                continue
            
            citing_list = self.citing_works.get(doi, [])
            if not citing_list:
                continue
            
            citations_list = []
            for cite in citing_list:
                cite_doi = cite.get('doi') if isinstance(cite, dict) else cite
                cite_date = cite.get('publication_date') if isinstance(cite, dict) else None
                
                meta = self.citations_metadata.get(cite_doi, {})
                
                # Calculate citation lag in days
                citation_lag = None
                pub_date = self.publications_metadata.get(doi, {}).get('publication_date')
                if pub_date and cite_date:
                    try:
                        pub_dt = datetime.fromisoformat(pub_date[:10])
                        cite_dt = datetime.fromisoformat(cite_date[:10])
                        citation_lag = (cite_dt - pub_dt).days
                    except:
                        pass
                
                citations_list.append({
                    'citing_title': meta.get('title', 'No title'),
                    'citing_year': meta.get('publication_year'),
                    'citing_date': cite_date,
                    'citing_journal': meta.get('journal_name', 'Unknown'),
                    'citing_publisher': meta.get('publisher', 'Unknown'),
                    'citing_doi': cite_doi,
                    'citation_lag': citation_lag,
                    'citing_authors': meta.get('authors', []),
                    'citing_countries': meta.get('affiliation_countries', []),
                    'citing_topics': meta.get('topics', [])  # Используем настоящие Topics
                })
            
            pub_meta = self.publications_metadata.get(doi, {})
            detailed[doi] = {
                'title': pub_meta.get('title', 'No title'),
                'year': p.get('Year'),
                'doi': doi,
                'total_citations': len(citations_list),
                'citations': citations_list
            }
        
        return detailed

    def _analyze_author_distribution(self) -> Dict:
        """Analyze distribution of publications by number of authors
        
        Groups: 1, 2, 3-5, 6-7, 8-10, 11-15, 15+
        
        Returns:
            Dict with two keys:
            - 'analyzed': distribution for analyzed publications
            - 'citing': distribution for citing publications
        """
        # --- ANALYZED PUBLICATIONS ---
        analyzed_distribution = defaultdict(int)
        analyzed_total = 0
        
        for p in self.publications:
            doi = p.get('DOI')
            if doi and doi in self.publications_metadata:
                meta = self.publications_metadata[doi]
                author_count = meta.get('author_count', 0)
                if author_count > 0:
                    # Группируем по новым категориям
                    if author_count == 1:
                        analyzed_distribution['1'] += 1
                    elif author_count == 2:
                        analyzed_distribution['2'] += 1
                    elif 3 <= author_count <= 5:
                        analyzed_distribution['3-5'] += 1
                    elif 6 <= author_count <= 7:
                        analyzed_distribution['6-7'] += 1
                    elif 8 <= author_count <= 10:
                        analyzed_distribution['8-10'] += 1
                    elif 11 <= author_count <= 15:
                        analyzed_distribution['11-15'] += 1
                    else:  # > 15
                        analyzed_distribution['15+'] += 1
                    analyzed_total += 1
        
        # --- CITING PUBLICATIONS ---
        citing_distribution = defaultdict(int)
        citing_total = 0
        
        for citing_list in self.citing_works.values():
            for cite in citing_list:
                doi = cite.get('doi') if isinstance(cite, dict) else cite
                if doi and doi in self.citations_metadata:
                    meta = self.citations_metadata[doi]
                    author_count = meta.get('author_count', 0)
                    if author_count > 0:
                        # Группируем по новым категориям
                        if author_count == 1:
                            citing_distribution['1'] += 1
                        elif author_count == 2:
                            citing_distribution['2'] += 1
                        elif 3 <= author_count <= 5:
                            citing_distribution['3-5'] += 1
                        elif 6 <= author_count <= 7:
                            citing_distribution['6-7'] += 1
                        elif 8 <= author_count <= 10:
                            citing_distribution['8-10'] += 1
                        elif 11 <= author_count <= 15:
                            citing_distribution['11-15'] += 1
                        else:  # > 15
                            citing_distribution['15+'] += 1
                        citing_total += 1
        
        # --- СОРТИРОВКА: определяем правильный порядок категорий ---
        category_order = ['1', '2', '3-5', '6-7', '8-10', '11-15', '15+']
        
        # Сортируем словари в правильном порядке
        sorted_analyzed = {}
        for cat in category_order:
            if cat in analyzed_distribution:
                sorted_analyzed[cat] = analyzed_distribution[cat]
        
        sorted_citing = {}
        for cat in category_order:
            if cat in citing_distribution:
                sorted_citing[cat] = citing_distribution[cat]
        
        return {
            'analyzed': {
                'distribution': sorted_analyzed,
                'total': analyzed_total
            },
            'citing': {
                'distribution': sorted_citing,
                'total': citing_total
            }
        }

# ============================================
# ФУНКЦИИ ДЛЯ ГЕНЕРАЦИИ ОТЧЕТОВ
# ============================================

def generate_journal_html_report(analyzer: JournalAnalyzer, logo_base64: Optional[str] = None, 
                                 app_logo_base64: Optional[str] = None, 
                                 theme_colors: Optional[Dict] = None, 
                                 lang: str = 'en') -> str:
    """Generate HTML report for journal analysis with rich visual elements"""
    
    results = analyzer.analysis_results
    publications = analyzer.publications
    citing_works = analyzer.citing_works
                                     
    # Get journal name and abbreviation
    journal_name = analyzer.journal_name or f"Journal {analyzer.issn}"
    journal_abbr = analyzer.journal_abbreviation or generate_journal_abbreviation(journal_name)
    
    if theme_colors is None:
        theme_colors = {
            'primary': '#667eea',
            'secondary': '#f39c12'
        }
    
    primary = theme_colors.get('primary', '#667eea')
    secondary = theme_colors.get('secondary', '#f39c12')
    
    # Получаем цвета для OA статусов
    oa_colors = {
        'gold': '#FFD700',
        'hybrid': '#F1C40F',
        'green': '#2ECC71',
        'bronze': '#CD7F32',
        'closed': '#95A5A6',
        'unknown': '#BDC3C7'
    }
    
    def t(key: str, **kwargs) -> str:
        return translate(key, lang, **kwargs)
    
    # Basic metrics
    basic = results.get('basic_metrics', {})
    author_analysis = results.get('author_analysis', {})
    affiliation_analysis = results.get('affiliation_analysis', {})
    geographic = results.get('geographic_analysis', {})
    citation = results.get('citation_analysis', {})
    citing = results.get('citing_analysis', {})
    topics = results.get('topics_analysis', {})
    detailed_citations = results.get('detailed_citations', {})
    author_distribution = results.get('author_distribution', {})
    
    # Impact Factor and CiteScore (static)
    impact_factor_data = results.get('impact_factor', {})
    citescore_data = results.get('citescore', {})
    
    # Dynamic Impact Factor and CiteScore (anchored to now())
    impact_factor_dynamic_data = results.get('impact_factor_dynamic', {}) or {}
    citescore_dynamic_data = results.get('citescore_dynamic', {}) or {}
    
    # ===== NEW: Grants & Funding data
    grants_analysis = results.get('grants_analysis', {}) or {}
    grants_analyzed = grants_analysis.get('analyzed', {}) or {}
    grants_citing = grants_analysis.get('citing', {}) or {}
    grants_analyzed_funders = grants_analyzed.get('top_funders', []) or []
    grants_analyzed_awards = grants_analyzed.get('top_awards', []) or []
    grants_citing_funders = grants_citing.get('top_funders', []) or []
    grants_citing_awards = grants_citing.get('top_awards', []) or []
    
    grants_analyzed_unique_funders = grants_analyzed.get('unique_funders_count', 0)
    grants_analyzed_unique_awards = grants_analyzed.get('unique_awards_count', 0)
    grants_citing_unique_funders = grants_citing.get('unique_funders_count', 0)
    grants_citing_unique_awards = grants_citing.get('unique_awards_count', 0)
    
    # ===== NEW: max values for grants tables
    max_grants_analyzed_funder_count = max([x.get('count', 0) for x in grants_analyzed_funders]) if grants_analyzed_funders else 1
    max_grants_analyzed_award_count = max([x.get('count', 0) for x in grants_analyzed_awards]) if grants_analyzed_awards else 1
    max_grants_citing_funder_count = max([x.get('count', 0) for x in grants_citing_funders]) if grants_citing_funders else 1
    max_grants_citing_award_count = max([x.get('count', 0) for x in grants_citing_awards]) if grants_citing_awards else 1
    
    # Все публикации для таблицы
    all_publications = []
    for p in publications:
        doi = p.get('DOI')
        meta = analyzer.publications_metadata.get(doi, {})
        all_publications.append({
            'doi': doi,
            'title': meta.get('title', 'No title'),
            'year': p.get('Year'),
            'authors': meta.get('authors', []),
            'affiliations': list(set(meta.get('affiliations', []))),
            'citations': p.get('Cited_by_count', 0),
            'citations_per_year': p.get('Cited_by_count', 0) / (datetime.now().year - p.get('Year') + 1) if p.get('Year') else 0,
            'journal': meta.get('journal_name', 'Unknown'),
            'id': meta.get('id', ''),
            'grants_display': meta.get('grants_display', [])  # ===== NEW
        })
    
    all_publications.sort(key=lambda x: x.get('year', 0), reverse=True)
    
    # ===== NEW: Build flat list of unique citing works for "Cited Publications" section
    # Дедуплицируем по DOI цитирующей работы (вариант A — одна строка на уникальную цитирующую работу)
    citing_by_doi = {}
    for our_doi, citing_list in (analyzer.citing_works or {}).items():
        for cite in citing_list:
            cite_doi = cite.get('doi') if isinstance(cite, dict) else cite
            if not cite_doi:
                continue
            if cite_doi not in citing_by_doi:
                meta = analyzer.citations_metadata.get(cite_doi, {})
                citing_by_doi[cite_doi] = {
                    'doi': cite_doi,
                    'title': meta.get('title', 'No title'),
                    'year': meta.get('publication_year'),
                    'date': meta.get('publication_date'),
                    'authors': meta.get('authors', []),
                    'affiliations': list(set(meta.get('affiliations', []))),
                    'journal': meta.get('journal_name', 'Unknown'),
                    'publisher': meta.get('publisher', 'Unknown'),
                    'cited_by_count': meta.get('cited_by_count', 0),
                    'countries': meta.get('affiliation_countries', []),
                    'grants_display': meta.get('grants_display', []),
                    'cites_our_count': 0
                }
            citing_by_doi[cite_doi]['cites_our_count'] += 1
    
    all_citing_works = list(citing_by_doi.values())
    all_citing_works.sort(key=lambda x: x.get('year') or 0, reverse=True)
    
    # Max values for citing works
    max_citing_cites_our = max([w.get('cites_our_count', 0) for w in all_citing_works]) if all_citing_works else 1
    
    # Helper function for color scale values in HTML
    def get_color_scale_html(value, max_val, min_val=0, unit=''):
        color = get_color_for_value(value, max_val, min_val)
        bg_color = get_color_for_value_text(value, max_val, min_val)
        return f'<span class="color-scale-value" style="background: {bg_color}; color: #1a1a1a;">{value}{unit}</span>'

    # ===== ВЫЧИСЛЯЕМ МАКСИМАЛЬНЫЕ ЗНАЧЕНИЯ ДЛЯ ТАБЛИЦЫ TOPICS =====
    topics_data = topics.get('topics', [])
    max_analyzed = max([t['analyzed_count'] for t in topics_data]) if topics_data else 1
    max_citing = max([t['citing_count'] for t in topics_data]) if topics_data else 1
    max_analyzed_norm = max([t['analyzed_norm_count'] for t in topics_data]) if topics_data else 1
    max_citing_norm = max([t['citing_norm_count'] for t in topics_data]) if topics_data else 1
    max_total_norm = max([t['total_norm_count'] for t in topics_data]) if topics_data else 1

    # ===== ВЫЧИСЛЯЕМ МАКСИМУМЫ ДЛЯ СТРАН =====
    country_stats = geographic.get('country_stats', [])
    max_unique_works = max([c['unique_works'] for c in country_stats]) if country_stats else 1
    max_authors_count = max([c['authors_count'] for c in country_stats]) if country_stats else 1
    
    # Max values for color scales
    max_publications = max([a.get('publications', 0) for a in author_analysis.get('top_authors', [])]) if author_analysis.get('top_authors') else 1
    max_citations_auth = max([a.get('citations', 0) for a in author_analysis.get('top_authors', [])]) if author_analysis.get('top_authors') else 1
    max_aff_count = max([a.get('count', 0) for a in affiliation_analysis.get('top_affiliations', [])]) if affiliation_analysis.get('top_affiliations') else 1
    max_country_count = max([c for c in geographic.get('authors_per_country', {}).values()]) if geographic.get('authors_per_country') else 1
    max_citation_count = max([r.get('citations_count', 0) for r in citation.get('dynamics', [])]) if citation.get('dynamics') else 1
    max_citing_auth = max([a.get('count', 0) for a in citing.get('top_authors', [])]) if citing.get('top_authors') else 1
    max_citing_aff = max([a.get('count', 0) for a in citing.get('top_affiliations', [])]) if citing.get('top_affiliations') else 1
    max_citing_country = max([a.get('count', 0) for a in citing.get('top_countries', [])]) if citing.get('top_countries') else 1
    max_citing_journal = max([a.get('count', 0) for a in citing.get('top_journals', [])]) if citing.get('top_journals') else 1
    max_citing_pub = max([a.get('count', 0) for a in citing.get('top_publishers', [])]) if citing.get('top_publishers') else 1
    max_most_cited = max([p.get('citations', 0) for p in citation.get('most_cited', [])]) if citation.get('most_cited') else 1
    max_most_cited_py = max([p.get('citations_per_year', 0) for p in citation.get('most_cited', [])]) if citation.get('most_cited') else 1
    
    # Heatmap max
    heatmap_max = 0
    for row in citation.get('heatmap', []):
        for year, val in row.items():
            if year != 'publication_year' and isinstance(val, (int, float)):
                heatmap_max = max(heatmap_max, val)
    
    # Собираем все годы для heatmap
    heatmap_years = sorted(set(
        [y for row in citation.get('heatmap', []) for y in row.keys() if y != 'publication_year']
    ))
    
    # ===== AUTHOR DISTRIBUTION DATA =====
    analyzed_dist = author_distribution.get('analyzed', {}).get('distribution', {})
    analyzed_total = author_distribution.get('analyzed', {}).get('total', 0)
    citing_dist = author_distribution.get('citing', {}).get('distribution', {})
    citing_total = author_distribution.get('citing', {}).get('total', 0)
    
    # Ensure all categories exist with default 0
    category_order = ['1', '2', '3-5', '6-7', '8-10', '11-15', '15+']
    for cat in category_order:
        if cat not in analyzed_dist:
            analyzed_dist[cat] = 0
        if cat not in citing_dist:
            citing_dist[cat] = 0
    
    # Labels for display
    category_labels = {
        '1': '1 author',
        '2': '2 authors',
        '3-5': '3-5 authors',
        '6-7': '6-7 authors',
        '8-10': '8-10 authors',
        '11-15': '11-15 authors',
        '15+': '15+ authors'
    }
    
    # Max values for author distribution color scales
    max_analyzed_dist = max(analyzed_dist.values()) if analyzed_dist else 1
    max_citing_dist = max(citing_dist.values()) if citing_dist else 1
    
    # ===== ПОДГОТОВКА ДАННЫХ ДЛЯ ДИНАМИЧЕСКИХ IF/SC =====
    dynamic_now = datetime.now()
    dynamic_now_str = dynamic_now.strftime('%Y-%m-%d')
    
    if impact_factor_dynamic_data.get('period_covers', False) and impact_factor_dynamic_data.get('value') is not None:
        if_dyn_value = f"{impact_factor_dynamic_data.get('value', 0):.1f}"
        if_dyn_cite_window = f"{impact_factor_dynamic_data.get('cite_window_start', '')} → {impact_factor_dynamic_data.get('cite_window_end', '')}"
        if_dyn_pub_window = f"{impact_factor_dynamic_data.get('pub_window_start', '')} → {impact_factor_dynamic_data.get('pub_window_end', '')}"
        if_dyn_citations = impact_factor_dynamic_data.get('citations', 0)
        if_dyn_publications = impact_factor_dynamic_data.get('publications', 0)
        if_dyn_calc_line = t('dynamic_citations_publications', citations=if_dyn_citations, publications=if_dyn_publications)
        if_dyn_label = t('if_dynamic_full', cite_start=impact_factor_dynamic_data.get('cite_window_start', ''), cite_end=impact_factor_dynamic_data.get('cite_window_end', ''))
        if_dyn_not_applicable = ''
    else:
        if_dyn_value = 'N/A'
        if_dyn_cite_window = ''
        if_dyn_pub_window = ''
        if_dyn_calc_line = ''
        if_dyn_label = t('if_dynamic')
        if_dyn_not_applicable = t('dynamic_not_applicable')
    
    if citescore_dynamic_data.get('period_covers', False) and citescore_dynamic_data.get('value') is not None:
        sc_dyn_value = f"{citescore_dynamic_data.get('value', 0):.1f}"
        sc_dyn_window = f"{citescore_dynamic_data.get('window_start', '')} → {citescore_dynamic_data.get('window_end', '')}"
        sc_dyn_citations = citescore_dynamic_data.get('citations', 0)
        sc_dyn_publications = citescore_dynamic_data.get('publications', 0)
        sc_dyn_calc_line = t('dynamic_citations_publications', citations=sc_dyn_citations, publications=sc_dyn_publications)
        sc_dyn_label = t('citescore_dynamic_full', start=citescore_dynamic_data.get('window_start', ''), end=citescore_dynamic_data.get('window_end', ''))
        sc_dyn_not_applicable = ''
    else:
        sc_dyn_value = 'N/A'
        sc_dyn_window = ''
        sc_dyn_calc_line = ''
        sc_dyn_label = t('citescore_dynamic')
        sc_dyn_not_applicable = t('dynamic_not_applicable')
    
    # ===== ГОТОВИМ HTML ДЛЯ СТАТИЧЕСКИХ IF/SC =====
    static_if_sc_block = ''
    if impact_factor_data and citescore_data:
        static_if_sc_block = f'''
                    <h3 style="margin-top: 20px; color: {primary}; font-size: 16px;">{t('impact_factor')} & {t('citescore')}</h3>
                    <div class="if-sc-grid">
                        <div class="if-sc-card">
                            <div class="if-sc-value">{impact_factor_data.get('value', 0):.1f}</div>
                            <div class="if-sc-label">{t('impact_factor_full', pub_years='-'.join(map(str, impact_factor_data.get('pub_years', []))), cite_year=impact_factor_data.get('cite_year', ''))}</div>
                            <div class="if-sc-detail">
                                {impact_factor_data.get('citations', 0)} {t('citations')} / {impact_factor_data.get('publications', 0)} {t('publications')}
                            </div>
                        </div>
                        <div class="if-sc-card">
                            <div class="if-sc-value">{citescore_data.get('value', 0):.1f}</div>
                            <div class="if-sc-label">{t('citescore_full', years='-'.join(map(str, citescore_data.get('window_years', []))))}</div>
                            <div class="if-sc-detail">
                                {citescore_data.get('citations', 0)} {t('citations')} / {citescore_data.get('publications', 0)} {t('publications')}
                            </div>
                        </div>
                    </div>
                    '''
    
    # ===== ГОТОВИМ HTML ДЛЯ ДИНАМИЧЕСКИХ IF/SC =====
    dynamic_if_sc_block = f'''
                    <h3 style="margin-top: 20px; color: {primary}; font-size: 16px;">{t('dynamic_metrics_title')} <span style="font-weight: 400; font-size: 12px; color: #7F8C8D;">{t('dynamic_as_of', date=dynamic_now_str)}</span></h3>
                    <div class="if-sc-grid">
                        <div class="if-sc-card">
                            <div class="if-sc-value">{if_dyn_value}</div>
                            <div class="if-sc-label">{if_dyn_label}</div>
                            <div class="if-sc-detail">
                                {if_dyn_calc_line}
                            </div>
                            {f'<div class="if-sc-detail" style="color: #95A5A6;">{t("dynamic_publications_window", start=impact_factor_dynamic_data.get("pub_window_start", ""), end=impact_factor_dynamic_data.get("pub_window_end", ""))}</div>' if if_dyn_pub_window else ''}
                            {f'<div class="if-sc-detail" style="color: #95A5A6;">{t("dynamic_citations_window", start=impact_factor_dynamic_data.get("cite_window_start", ""), end=impact_factor_dynamic_data.get("cite_window_end", ""))}</div>' if if_dyn_cite_window else ''}
                            {f'<div class="if-sc-detail" style="color: #E74C3C;">{if_dyn_not_applicable}</div>' if if_dyn_not_applicable else ''}
                        </div>
                        <div class="if-sc-card">
                            <div class="if-sc-value">{sc_dyn_value}</div>
                            <div class="if-sc-label">{sc_dyn_label}</div>
                            <div class="if-sc-detail">
                                {sc_dyn_calc_line}
                            </div>
                            {f'<div class="if-sc-detail" style="color: #95A5A6;">{t("dynamic_window_label", start=citescore_dynamic_data.get("window_start", ""), end=citescore_dynamic_data.get("window_end", ""))}</div>' if sc_dyn_window else ''}
                            {f'<div class="if-sc-detail" style="color: #E74C3C;">{sc_dyn_not_applicable}</div>' if sc_dyn_not_applicable else ''}
                        </div>
                    </div>
                    '''
    
    # ===== NEW: HTML for Grants section (safe building of rows) =====
    def _funder_ror_link(ror_short: str) -> str:
        if not ror_short:
            return '-'
        display_id = ror_short[:8] + '...' if len(ror_short) > 8 else ror_short
        return f'<a href="https://colab.ws/organizations/{ror_short}" target="_blank" class="doi-link" style="font-family: monospace; font-size: 11px;">{display_id}</a>'
    
    grants_analyzed_funders_rows = ''.join([
        f'''
        <tr>
            <td>{i+1}</td>
            <td>{html.escape(fd.get('name', '') or 'Unknown')}</td>
            <td>{_funder_ror_link(fd.get('ror_short', ''))}</td>
            <td>{get_color_scale_html(fd.get('count', 0), max_grants_analyzed_funder_count)}</td>
        </tr>
        '''
        for i, fd in enumerate(grants_analyzed_funders)
    ])
    
    grants_analyzed_awards_rows = ''.join([
        f'''
        <tr>
            <td>{i+1}</td>
            <td>{html.escape(aw.get('funder_name', '') or 'Unknown')}</td>
            <td>{html.escape(aw.get('award_id', '') or '-')}</td>
            <td>{html.escape(aw.get('display_name', '') or '')}</td>
            <td>{get_color_scale_html(aw.get('count', 0), max_grants_analyzed_award_count)}</td>
        </tr>
        '''
        for i, aw in enumerate(grants_analyzed_awards)
    ])
    
    grants_citing_funders_rows = ''.join([
        f'''
        <tr>
            <td>{i+1}</td>
            <td>{html.escape(fd.get('name', '') or 'Unknown')}</td>
            <td>{_funder_ror_link(fd.get('ror_short', ''))}</td>
            <td>{get_color_scale_html(fd.get('count', 0), max_grants_citing_funder_count)}</td>
        </tr>
        '''
        for i, fd in enumerate(grants_citing_funders)
    ])
    
    grants_citing_awards_rows = ''.join([
        f'''
        <tr>
            <td>{i+1}</td>
            <td>{html.escape(aw.get('funder_name', '') or 'Unknown')}</td>
            <td>{html.escape(aw.get('award_id', '') or '-')}</td>
            <td>{html.escape(aw.get('display_name', '') or '')}</td>
            <td>{get_color_scale_html(aw.get('count', 0), max_grants_citing_award_count)}</td>
        </tr>
        '''
        for i, aw in enumerate(grants_citing_awards)
    ])
    
    # ===== NEW: HTML for All Publications rows (with Grants & Funding column) =====
    max_all_pubs_citations = max([pub.get('citations', 0) for pub in all_publications]) if all_publications else 1
    max_all_pubs_cpy = max([pub.get('citations_per_year', 0) for pub in all_publications]) if all_publications else 1
    
    all_publications_rows = ''.join([
        f'''
        <tr 
            data-year="{p.get('year', '')}" 
            data-authors="{','.join([html.escape(a) for a in p.get('authors', [])])}" 
            data-affiliations="{','.join([html.escape(a) for a in p.get('affiliations', [])])}"
            data-citations="{p.get('citations', 0)}" 
            data-title="{html.escape((p.get('title') or '').lower())}"
            data-doi="{html.escape((p.get('doi') or '').lower())}"
        >
            <td>{i+1}</td>
            <td class="word-wrap">{html.escape((p.get('title') or 'No title')[:120])}{'...' if len(p.get('title') or '') > 120 else ''}</td>
            <td>{p.get('year', 'N/A')}</td>
            <td>{', '.join([html.escape(a) for a in p.get('authors', [])[:3]])}{' +' + str(len(p.get('authors', []))-3) if len(p.get('authors', [])) > 3 else ''}</td>
            <td>{', '.join([html.escape(a) for a in list(dict.fromkeys(p.get('affiliations', [])))[:3]])}{' +' + str(len(list(dict.fromkeys(p.get('affiliations', []))))-3) if len(list(dict.fromkeys(p.get('affiliations', [])))) > 3 else ''}</td>
            <td>{get_color_scale_html(p.get('citations', 0), max_all_pubs_citations)}</td>
            <td>{get_color_scale_html(round(p.get('citations_per_year', 0), 1), max_all_pubs_cpy)}</td>
            <td class="word-wrap" style="max-width: 220px;">{'<br>'.join([html.escape(g) for g in p.get('grants_display', [])]) if p.get('grants_display') else '-'}</td>
            <td>{f'<a href="https://doi.org/{html.escape(p.get("doi") or "")}" target="_blank" class="doi-link">{html.escape((p.get("doi") or "")[:20])}...</a>' if p.get('doi') else '-'}</td>
        </tr>
        '''
        for i, p in enumerate(all_publications)
    ])
    
    # ===== NEW: HTML for Cited Publications rows (with filters, journal, publisher, grants) =====
    all_citing_works_rows = ''.join([
        f'''
        <tr
            data-year="{w.get('year', '')}"
            data-authors="{','.join([html.escape(a) for a in w.get('authors', [])])}"
            data-affiliations="{','.join([html.escape(a) for a in w.get('affiliations', [])])}"
            data-journal="{html.escape((w.get('journal') or '').lower())}"
            data-publisher="{html.escape((w.get('publisher') or '').lower())}"
            data-citations="{w.get('cited_by_count', 0)}"
            data-cites-our="{w.get('cites_our_count', 0)}"
            data-title="{html.escape((w.get('title') or '').lower())}"
            data-doi="{html.escape((w.get('doi') or '').lower())}"
        >
            <td>{i+1}</td>
            <td class="word-wrap">{html.escape((w.get('title') or 'No title')[:120])}{'...' if len(w.get('title') or '') > 120 else ''}</td>
            <td>{w.get('year', 'N/A')}</td>
            <td>{', '.join([html.escape(a) for a in w.get('authors', [])[:3]])}{' +' + str(len(w.get('authors', []))-3) if len(w.get('authors', [])) > 3 else ''}</td>
            <td>{', '.join([html.escape(a) for a in list(dict.fromkeys(w.get('affiliations', [])))[:3]])}{' +' + str(len(list(dict.fromkeys(w.get('affiliations', []))))-3) if len(list(dict.fromkeys(w.get('affiliations', [])))) > 3 else ''}</td>
            <td>{html.escape(w.get('journal', 'Unknown') or 'Unknown')}</td>
            <td>{html.escape(w.get('publisher', 'Unknown') or 'Unknown')}</td>
            <td>{get_color_scale_html(w.get('cited_by_count', 0), max([x.get('cited_by_count', 0) for x in all_citing_works]) if all_citing_works else 1)}</td>
            <td>{get_color_scale_html(w.get('cites_our_count', 0), max_citing_cites_our)}</td>
            <td class="word-wrap" style="max-width: 220px;">{'<br>'.join([html.escape(g) for g in w.get('grants_display', [])]) if w.get('grants_display') else '-'}</td>
            <td>{f'<a href="https://doi.org/{html.escape(w.get("doi") or "")}" target="_blank" class="doi-link">{html.escape((w.get("doi") or "")[:20])}...</a>' if w.get('doi') else '-'}</td>
        </tr>
        '''
        for i, w in enumerate(all_citing_works)
    ])
    
    # HTML generation
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>{journal_name}</title>
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
                max-width: 1600px;
                margin: 0 auto;
                background: white;
                box-shadow: 0 10px 40px rgba(0,0,0,0.1);
                border-radius: 10px;
                overflow: hidden;
            }}
            
            /* ===== SIDEBAR NAVIGATION ===== */
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
                box-shadow: 2px 0 20px rgba(0,0,0,0.15);
            }}
            .sidebar::-webkit-scrollbar {{ width: 4px; }}
            .sidebar::-webkit-scrollbar-thumb {{ background: rgba(255,255,255,0.3); border-radius: 4px; }}
            
            .sidebar h3 {{
                margin-bottom: 20px;
                font-size: 18px;
                font-weight: 700;
                color: white;
                border-bottom: 2px solid rgba(255,255,255,0.3);
                padding-bottom: 15px;
                letter-spacing: 0.5px;
                word-wrap: break-word;
            }}
            .sidebar .nav-section {{
                margin-top: 5px;
            }}
            .sidebar .nav-section-title {{
                font-size: 11px;
                text-transform: uppercase;
                letter-spacing: 1px;
                opacity: 0.7;
                padding: 8px 12px 4px 12px;
                font-weight: 600;
                display: none;
            }}
            .sidebar a {{
                color: white;
                text-decoration: none;
                display: flex;
                align-items: center;
                gap: 10px;
                padding: 8px 14px;
                margin: 2px 0;
                border-radius: 8px;
                transition: all 0.3s;
                font-size: 13px;
            }}
            .sidebar a:hover {{
                background: rgba(255,255,255,0.2);
                transform: translateX(5px);
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            .sidebar a .nav-icon {{
                font-size: 16px;
                width: 24px;
                text-align: center;
            }}
            
            /* ===== MAIN CONTENT ===== */
            .main-content {{
                margin-left: 280px;
                padding: 30px 40px;
            }}
            
            /* ===== HEADER ===== */
            .header {{
                background: linear-gradient(135deg, {primary} 0%, {secondary} 100%);
                color: white;
                padding: 30px 40px;
                border-radius: 15px;
                margin-bottom: 30px;
                display: flex;
                align-items: center;
                justify-content: space-between;
                box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            }}
            .header-left {{
                display: flex;
                align-items: center;
                gap: 20px;
            }}
            .header-left img {{
                max-height: 130px;
                filter: drop-shadow(0 2px 4px rgba(0,0,0,0.2));
            }}
            .header h1 {{
                color: white;
                border-bottom: none;
                margin: 0;
                font-size: 28px;
                font-weight: 700;
                text-shadow: 0 2px 4px rgba(0,0,0,0.2);
                word-wrap: break-word;
            }}
            .header .subtitle {{
                opacity: 0.9;
                margin-top: 5px;
                font-size: 14px;
                text-shadow: 0 1px 2px rgba(0,0,0,0.15);
            }}
            .header-right img {{
                max-height: 120px;
                max-width: 250px;
                filter: drop-shadow(0 2px 8px rgba(0,0,0,0.2));
                background: rgba(255,255,255,0.1);
                border-radius: 8px;
                padding: 5px;
            }}
            
            /* ===== SECTIONS ===== */
            .section {{
                background: white;
                border-radius: 15px;
                padding: 25px 30px;
                margin-bottom: 25px;
                box-shadow: 0 2px 12px rgba(0,0,0,0.08);
                border: 1px solid #f0f0f0;
                transition: all 0.3s;
            }}
            .section:hover {{
                box-shadow: 0 4px 20px rgba(0,0,0,0.12);
            }}
            
            .section-header {{
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: space-between;
                user-select: none;
                padding: 5px 0;
            }}
            .section-header:hover .section-title {{
                color: {primary};
            }}
            .section-title {{
                font-size: 22px;
                font-weight: 700;
                margin-bottom: 0;
                padding-bottom: 0;
                border-bottom: none;
                display: flex;
                align-items: center;
                gap: 12px;
                color: #2C3E50;
                transition: color 0.3s;
            }}
            .section-title .icon {{
                font-size: 24px;
            }}
            .section-title .section-badge {{
                background: linear-gradient(135deg, {primary}, {secondary});
                color: white;
                padding: 2px 12px;
                border-radius: 20px;
                font-size: 13px;
                font-weight: 600;
                margin-left: 8px;
            }}
            .section-divider {{
                height: 3px;
                background: linear-gradient(90deg, {primary}, {secondary}, transparent);
                margin: 15px 0 20px 0;
                border-radius: 3px;
            }}
            .toggle-indicator {{
                font-size: 18px;
                transition: transform 0.3s;
                color: {primary};
                font-weight: 300;
            }}
            .toggle-indicator.collapsed {{
                transform: rotate(-90deg);
            }}
            .section-content {{
                display: block;
                transition: all 0.4s ease;
            }}
            .section-content.collapsed {{
                display: none;
            }}
            
            /* ===== METRICS GRID ===== */
            .metrics-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
                gap: 12px;
                margin: 15px 0;
            }}
            .metrics-grid-4 {{
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            }}
            .metric-card {{
                background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
                padding: 14px 18px;
                border-radius: 12px;
                border-left: 4px solid {primary};
                text-align: center;
                transition: all 0.3s;
                box-shadow: 0 2px 6px rgba(0,0,0,0.04);
                position: relative;
                overflow: hidden;
            }}
            .metric-card::after {{
                content: '';
                position: absolute;
                top: 0;
                right: 0;
                width: 60px;
                height: 60px;
                background: linear-gradient(135deg, transparent 50%, {primary}08 100%);
                border-radius: 0 12px 0 60px;
            }}
            .metric-card:hover {{
                transform: translateY(-4px);
                box-shadow: 0 6px 20px rgba(0,0,0,0.1);
                border-left-color: {secondary};
            }}
            .metric-card .metric-icon {{
                font-size: 20px;
                display: block;
                margin-bottom: 4px;
            }}
            .metric-value {{
                font-size: 26px;
                font-weight: 700;
                color: #2C3E50;
                font-family: 'Times New Roman', serif;
                background: linear-gradient(135deg, {primary}, {secondary});
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }}
            .metric-label {{
                font-size: 11px;
                color: #7F8C8D;
                margin-top: 4px;
                font-family: 'Times New Roman', serif;
                font-weight: 500;
                text-transform: uppercase;
                letter-spacing: 0.3px;
            }}
            
            /* ===== PROGRESS BARS ===== */
            .progress-bar-container {{
                width: 100%;
                background-color: #f0f0f0;
                border-radius: 8px;
                overflow: hidden;
                margin: 4px 0;
                height: 22px;
                position: relative;
                box-shadow: inset 0 1px 3px rgba(0,0,0,0.1);
            }}
            .progress-bar-fill {{
                height: 100%;
                border-radius: 8px;
                transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1);
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-size: 11px;
                font-weight: 700;
                text-shadow: 0 1px 2px rgba(0,0,0,0.3);
                position: relative;
                overflow: hidden;
                min-width: 30px;
            }}
            .progress-bar-fill.animate {{
                animation: shimmer 2s infinite linear;
                background-size: 200% 100%;
            }}
            @keyframes shimmer {{
                0% {{ background-position: -200% 0; }}
                100% {{ background-position: 200% 0; }}
            }}
            
            .progress-bar-label {{
                display: flex;
                justify-content: space-between;
                font-size: 12px;
                margin: 2px 0 1px 0;
                color: #555;
                font-weight: 500;
            }}
            .progress-bar-label .label-value {{
                font-weight: 700;
                color: #2C3E50;
            }}
            
            /* ===== OA BREAKDOWN ===== */
            .oa-breakdown {{
                display: flex;
                flex-wrap: wrap;
                gap: 12px;
                margin: 12px 0;
            }}
            .oa-item {{
                display: flex;
                align-items: center;
                gap: 10px;
                background: #f8f9fa;
                padding: 8px 16px 8px 12px;
                border-radius: 10px;
                border: 1px solid #e9ecef;
                flex: 1;
                min-width: 120px;
                transition: all 0.3s;
            }}
            .oa-item:hover {{
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            }}
            .oa-item .color-dot {{
                width: 16px;
                height: 16px;
                border-radius: 50%;
                display: inline-block;
                flex-shrink: 0;
                border: 1px solid rgba(0,0,0,0.05);
            }}
            .oa-item .oa-info {{
                flex: 1;
            }}
            .oa-item .oa-name {{
                font-weight: 600;
                font-size: 13px;
            }}
            .oa-item .oa-count {{
                font-size: 12px;
                color: #666;
            }}
            .oa-item .oa-percent {{
                font-size: 14px;
                font-weight: 700;
                color: #2C3E50;
                margin-left: auto;
            }}
            
            /* ===== TABLES ===== */
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 12px 0;
                font-family: 'Times New Roman', serif;
                font-size: 13px;
            }}
            th {{
                background: linear-gradient(135deg, {primary} 0%, {secondary} 100%);
                color: white;
                padding: 10px 14px;
                text-align: left;
                font-weight: 600;
                position: sticky;
                top: 0;
                z-index: 10;
                white-space: nowrap;
            }}
            th.sortable {{
                cursor: pointer;
                user-select: none;
                position: relative;
            }}
            th.sortable:hover {{
                opacity: 0.9;
            }}
            th.sortable::after {{
                content: ' ↕';
                opacity: 0.5;
                font-size: 10px;
            }}
            th.sortable.asc::after {{
                content: ' ↑';
                opacity: 0.8;
            }}
            th.sortable.desc::after {{
                content: ' ↓';
                opacity: 0.8;
            }}
            td {{
                padding: 8px 14px;
                border-bottom: 1px solid #e9ecef;
                vertical-align: middle;
                transition: background 0.2s;
            }}
            tr:hover td {{
                background-color: #f8f9fa;
            }}
            .scrollable-table {{
                max-height: 500px;
                overflow-y: auto;
                border-radius: 8px;
                border: 1px solid #e9ecef;
            }}
            .scrollable-table thead {{
                position: sticky;
                top: 0;
                z-index: 10;
            }}
            
            .citation-count {{
                background: linear-gradient(135deg, {primary}15, {secondary}15);
                padding: 2px 10px;
                border-radius: 12px;
                font-weight: 700;
                color: {primary};
            }}
            
            .doi-link {{
                color: #2980B9;
                text-decoration: none;
                font-size: 11px;
                word-break: break-all;
                transition: color 0.2s;
            }}
            .doi-link:hover {{
                color: {primary};
                text-decoration: underline;
            }}
            
            .badge {{
                display: inline-block;
                padding: 2px 10px;
                border-radius: 12px;
                font-size: 11px;
                font-weight: 600;
                margin: 1px 2px;
            }}
            .badge-gold {{ background: #FFD700; color: #333; }}
            .badge-hybrid {{ background: #F1C40F; color: #333; }}
            .badge-green {{ background: #2ECC71; color: white; }}
            .badge-bronze {{ background: #CD7F32; color: white; }}
            .badge-closed {{ background: #95A5A6; color: white; }}
            .badge-unknown {{ background: #BDC3C7; color: #333; }}
            .badge-info {{ background: #3498DB; color: white; }}
            .badge-success {{ background: #2ECC71; color: white; }}
            .badge-warning {{ background: #F39C12; color: white; }}
            .badge-danger {{ background: #E74C3C; color: white; }}
            .badge-primary {{ background: {primary}; color: white; }}
            
            /* ===== HEATMAP ===== */
            .heatmap-cell {{
                text-align: center;
                padding: 6px 10px;
                border-radius: 4px;
                font-size: 12px;
                font-weight: 600;
                transition: all 0.3s;
                min-width: 40px;
            }}
            .heatmap-cell:hover {{
                transform: scale(1.05);
                box-shadow: 0 2px 8px rgba(0,0,0,0.15);
                z-index: 5;
            }}
            
            /* ===== COLLAPSER (Detailed Citations) ===== */
            .collapser {{
                background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
                padding: 12px 18px;
                margin: 5px 0;
                border-radius: 10px;
                cursor: pointer;
                border-left: 4px solid {primary};
                transition: all 0.3s;
                display: flex;
                align-items: center;
                flex-wrap: wrap;
                gap: 8px;
                box-shadow: 0 1px 4px rgba(0,0,0,0.04);
            }}
            .collapser:hover {{
                background: #e9ecef;
                transform: translateX(5px);
                box-shadow: 0 2px 12px rgba(0,0,0,0.08);
            }}
            .collapser .citation-count-badge {{
                background: linear-gradient(135deg, {primary}, {secondary});
                color: white;
                padding: 2px 12px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: 700;
            }}
            .collapser .toggle-hint {{
                font-size: 11px;
                color: #999;
                margin-left: auto;
                font-weight: 400;
            }}
            .citation-detail {{
                background: #f8f9fa;
                padding: 12px 18px;
                margin: 4px 0 4px 24px;
                border-radius: 8px;
                border-left: 3px solid {secondary};
                font-size: 13px;
                transition: all 0.3s;
            }}
            .citation-detail:hover {{
                background: #f0f1f2;
                transform: translateX(3px);
            }}
            .citation-detail .cite-meta {{
                color: #555;
                font-size: 12px;
                margin-top: 4px;
                line-height: 1.6;
            }}
            .citation-detail .cite-title {{
                font-weight: 600;
                color: #2C3E50;
            }}
            
            /* ===== FILTER SECTION ===== */
            .filter-section {{
                background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
                padding: 15px 20px;
                border-radius: 10px;
                margin-bottom: 15px;
                border: 1px solid #e9ecef;
            }}
            .filter-row {{
                display: flex;
                flex-wrap: wrap;
                gap: 12px;
                align-items: center;
            }}
            .filter-row .filter-group {{
                display: flex;
                align-items: center;
                gap: 6px;
                background: white;
                padding: 4px 10px 4px 12px;
                border-radius: 8px;
                border: 1px solid #e9ecef;
            }}
            .filter-row label {{
                font-size: 11px;
                font-weight: 600;
                color: #555;
                white-space: nowrap;
                text-transform: uppercase;
                letter-spacing: 0.3px;
            }}
            .filter-row select, .filter-row input {{
                padding: 4px 8px;
                border: none;
                border-radius: 4px;
                font-size: 12px;
                font-family: 'Times New Roman', serif;
                background: transparent;
                outline: none;
            }}
            .filter-row select:focus, .filter-row input:focus {{
                box-shadow: 0 0 0 2px {primary}40;
            }}
            .filter-row input[type="text"] {{
                width: 130px;
            }}
            .filter-row input[type="number"] {{
                width: 70px;
            }}
            .filter-stats {{
                margin-top: 10px;
                font-size: 13px;
                color: #555;
                padding: 6px 12px;
                background: white;
                border-radius: 8px;
                border: 1px solid #e9ecef;
                display: inline-block;
            }}
            .filter-stats strong {{
                color: #2C3E50;
            }}
            
            /* ===== GEO GRID ===== */
            .geo-grid {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
                margin: 15px 0;
            }}
            .geo-card {{
                background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
                padding: 16px 20px;
                border-radius: 10px;
                border: 1px solid #e9ecef;
                transition: all 0.3s;
            }}
            .geo-card:hover {{
                box-shadow: 0 4px 16px rgba(0,0,0,0.06);
            }}
            .geo-card h4 {{
                color: {primary};
                margin-bottom: 8px;
                font-size: 14px;
            }}
            .geo-card .geo-value {{
                font-size: 18px;
                font-weight: 700;
                color: #2C3E50;
            }}
            .geo-card .geo-label {{
                font-size: 12px;
                color: #7F8C8D;
            }}
            
            /* ===== COLOR SCALE FOR NUMERIC VALUES ===== */
            .color-scale-value {{
                display: inline-block;
                padding: 2px 10px;
                border-radius: 8px;
                font-weight: 600;
                text-align: center;
                min-width: 30px;
                transition: all 0.2s;
            }}
            .color-scale-value:hover {{
                transform: scale(1.05);
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }}
            
            /* ===== RESPONSIVE ===== */
            @media print {{
                .sidebar {{ display: none; }}
                .main-content {{ margin-left: 0; }}
                .section {{ box-shadow: none; border: 1px solid #ddd; }}
                .metric-card {{ box-shadow: none; }}
            }}
            @media (max-width: 768px) {{
                .sidebar {{ display: none; }}
                .main-content {{ margin-left: 0; padding: 15px; }}
                .header {{ flex-direction: column; text-align: center; padding: 20px; }}
                .header-left {{ flex-direction: column; }}
                .geo-grid {{ grid-template-columns: 1fr; }}
                .filter-row {{ flex-direction: column; align-items: stretch; }}
                .filter-row .filter-group {{ flex-wrap: wrap; }}
                .metrics-grid {{ grid-template-columns: repeat(2, 1fr); }}
                .metrics-grid-4 {{ grid-template-columns: 1fr 1fr; }}
                .oa-breakdown {{ flex-direction: column; }}
            }}
            
            /* ===== ANIMATIONS ===== */
            @keyframes fadeInUp {{
                from {{ opacity: 0; transform: translateY(20px); }}
                to {{ opacity: 1; transform: translateY(0); }}
            }}
            .section {{
                animation: fadeInUp 0.6s ease forwards;
            }}
            .section:nth-child(2) {{ animation-delay: 0.1s; }}
            .section:nth-child(3) {{ animation-delay: 0.2s; }}
            .section:nth-child(4) {{ animation-delay: 0.3s; }}
            .section:nth-child(5) {{ animation-delay: 0.4s; }}
            .section:nth-child(6) {{ animation-delay: 0.5s; }}
            .section:nth-child(7) {{ animation-delay: 0.6s; }}
            
            .word-wrap {{
                word-wrap: break-word;
                max-width: 300px;
            }}
            
            .footer {{
                margin-top: 40px;
                padding-top: 20px;
                border-top: 2px solid #e9ecef;
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
            
            .orcid-full {{
                font-family: monospace;
                font-size: 12px;
                color: #1a1a1a;
            }}
            
            .dist-grid {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
                margin: 15px 0;
            }}
            .dist-card {{
                background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
                padding: 16px 20px;
                border-radius: 10px;
                border: 1px solid #e9ecef;
                transition: all 0.3s;
            }}
            .dist-card:hover {{
                box-shadow: 0 4px 16px rgba(0,0,0,0.06);
            }}
            .dist-card h4 {{
                color: {primary};
                margin-bottom: 12px;
                font-size: 14px;
                text-align: center;
            }}
            .dist-card .total-label {{
                text-align: center;
                font-size: 12px;
                color: #7F8C8D;
                margin-top: 10px;
                padding-top: 8px;
                border-top: 1px solid #e9ecef;
            }}
            
            /* ===== IF/SC CARDS ===== */
            .if-sc-grid {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 12px;
                margin: 12px 0;
            }}
            .if-sc-card {{
                background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
                padding: 14px 18px;
                border-radius: 12px;
                border-left: 4px solid {primary};
                text-align: center;
                transition: all 0.3s;
                box-shadow: 0 2px 6px rgba(0,0,0,0.04);
                position: relative;
                overflow: hidden;
            }}
            .if-sc-card:hover {{
                transform: translateY(-4px);
                box-shadow: 0 6px 20px rgba(0,0,0,0.1);
                border-left-color: {secondary};
            }}
            .if-sc-card .if-sc-value {{
                font-size: 28px;
                font-weight: 700;
                color: #2C3E50;
                font-family: 'Times New Roman', serif;
                background: linear-gradient(135deg, {primary}, {secondary});
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }}
            .if-sc-card .if-sc-label {{
                font-size: 11px;
                color: #7F8C8D;
                margin-top: 4px;
                font-family: 'Times New Roman', serif;
                font-weight: 500;
                letter-spacing: 0.3px;
            }}
            .if-sc-card .if-sc-detail {{
                font-size: 10px;
                color: #95A5A6;
                margin-top: 2px;
                font-family: 'Times New Roman', serif;
            }}
        </style>
    </head>
    <body>
        <div class="sidebar">
            <h3>{journal_abbr}</h3>
            
            <div class="nav-section">
                <a href="#overview"><span class="nav-icon">📋</span> {t('overview')}</a>
                <a href="#analyzed_articles"><span class="nav-icon">📄</span> {t('analyzed_articles')}</a>
                <a href="#citation_analysis"><span class="nav-icon">📈</span> {t('citation_analysis')}</a>
                <a href="#citing_publications"><span class="nav-icon">📄</span> {t('citing_publications')}</a>
                <a href="#citing_works"><span class="nav-icon">📚</span> {t('citing_works_analysis')}</a>
                <a href="#topics_analysis"><span class="nav-icon">🏷️</span> {t('topics_analysis')}</a>
                <a href="#grants_analysis"><span class="nav-icon">💰</span> {t('grants_and_funding')}</a>
                <a href="#detailed_citations"><span class="nav-icon">📋</span> {t('detailed_citations')}</a>
                <a href="#all_publications"><span class="nav-icon">📚</span> {t('all_publications')}</a>
            </div>
            
            <div style="margin-top: 20px; padding-top: 15px; border-top: 1px solid rgba(255,255,255,0.2); font-size: 11px; opacity: 0.8; line-height: 1.6;">
                <div>{t('journal_issn_label', issn=analyzer.issn)}</div>
                <div>{t('analysis_period_label', period=str(analyzer.period))}</div>
                <div style="margin-top: 4px; font-size: 10px; opacity: 0.6;">{t('generated_on')}: {datetime.now().strftime('%d.%m.%Y %H:%M')}</div>
            </div>
        </div>
        
        <div class="main-content">
            <!-- HEADER -->
            <div class="header">
                <div class="header-left">
                    {f'<img src="data:image/png;base64,{app_logo_base64}" alt="App Logo" style="max-height:105px;">' if app_logo_base64 else ''}
                    <div>
                        <h1>{journal_name}</h1>
                        <div class="subtitle">
                            {t('journal_issn_label', issn=analyzer.issn)} | 
                            {t('analysis_period_label', period=str(analyzer.period))}
                        </div>
                    </div>
                </div>
                {f'<div class="header-right"><img src="data:image/png;base64,{logo_base64}" alt="Journal Logo"></div>' if logo_base64 else ''}
            </div>
            
            <!-- ============================================================ -->
            <!-- SECTION 1: OVERVIEW -->
            <!-- ============================================================ -->
            <div id="overview" class="section">
                <div class="section-header" onclick="toggleSection('overview_content')">
                    <div class="section-title">
                        <span class="icon">📋</span> {t('overview')}
                        <span class="section-badge">{basic.get('total_publications', 0)} {t('publications')}</span>
                    </div>
                    <span class="toggle-indicator" id="overview_indicator">▼</span>
                </div>
                <div class="section-divider"></div>
                <div id="overview_content" class="section-content">
                    
                    <!-- Metrics Grid -->
                    <div class="metrics-grid">
                        <div class="metric-card">
                            <div class="metric-value">{basic.get('total_publications', 0)}</div>
                            <div class="metric-label">{t('total_publications')}</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{basic.get('total_citations', 0):,}</div>
                            <div class="metric-label">{t('total_citations')}</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{basic.get('h_index', 0)}</div>
                            <div class="metric-label">{t('h_index')}</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{basic.get('g_index', 0)}</div>
                            <div class="metric-label">{t('g_index')}</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{basic.get('i10_index', 0)}</div>
                            <div class="metric-label">{t('i10_index')}</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{basic.get('i100_index', 0)}</div>
                            <div class="metric-label">{t('i100_index')}</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{basic.get('avg_citations', 0):.1f}</div>
                            <div class="metric-label">{t('avg_citations')}</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{basic.get('oa_percentage', 0):.1f}%</div>
                            <div class="metric-label">{t('open_access')}</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{basic.get('active_years', 0)}</div>
                            <div class="metric-label">{t('active_years')}</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{basic.get('unique_authors', 0):,}</div>
                            <div class="metric-label">{t('unique_authors')}</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{basic.get('unique_affiliations', 0):,}</div>
                            <div class="metric-label">{t('unique_affiliations')}</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{basic.get('unique_countries', 0)}</div>
                            <div class="metric-label">{t('unique_countries')}</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{basic.get('avg_authors_per_paper', 0):.1f}</div>
                            <div class="metric-label">{t('avg_authors_per_paper')}</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{basic.get('avg_affiliations_per_paper', 0):.1f}</div>
                            <div class="metric-label">{t('avg_affiliations_per_paper')}</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{basic.get('avg_countries_per_paper', 0):.1f}</div>
                            <div class="metric-label">{t('avg_countries_per_paper')}</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{basic.get('international_collaboration_rate', 0):.1f}%</div>
                            <div class="metric-label">{t('international_collaboration_rate')}</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{basic.get('unique_citing_authors', 0):,}</div>
                            <div class="metric-label">{t('unique_citing_authors')}</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{basic.get('unique_citing_affiliations', 0):,}</div>
                            <div class="metric-label">{t('unique_citing_affiliations')}</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{basic.get('unique_citing_countries', 0)}</div>
                            <div class="metric-label">{t('unique_citing_countries')}</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{basic.get('unique_citing_journals', 0):,}</div>
                            <div class="metric-label">{t('unique_citing_journals')}</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{basic.get('unique_citing_publishers', 0):,}</div>
                            <div class="metric-label">{t('unique_citing_publishers')}</div>
                        </div>
                        <!-- ===== NEW: Grants metrics ===== -->
                        <div class="metric-card">
                            <div class="metric-value">{grants_analyzed_unique_funders}</div>
                            <div class="metric-label">{t('unique_funders_analyzed')}</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{grants_analyzed_unique_awards}</div>
                            <div class="metric-label">{t('unique_awards_analyzed')}</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{grants_citing_unique_funders}</div>
                            <div class="metric-label">{t('unique_funders_citing')}</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{grants_citing_unique_awards}</div>
                            <div class="metric-label">{t('unique_awards_citing')}</div>
                        </div>
                    </div>
                    
                    <!-- Impact Factor and CiteScore Cards (static) -->
                    {static_if_sc_block}
                    
                    <!-- Dynamic Impact Factor and CiteScore Cards (anchored to now()) -->
                    {dynamic_if_sc_block}
                    
                    <!-- Open Access Breakdown with Progress Bars -->
                    <h3 style="margin-top: 20px; color: {primary}; font-size: 16px;">{t('open_access_breakdown')}</h3>
                    
                    {''.join([
                        f'''
                        <div style="margin: 6px 0;">
                            <div class="progress-bar-label">
                                <span><span class="color-dot" style="display:inline-block;width:12px;height:12px;border-radius:50%;background:{oa_colors.get(status, '#BDC3C7')};vertical-align:middle;margin-right:6px;"></span> 
                                <strong>{t(status)}</strong></span>
                                <span class="label-value">{count} ({count/basic.get('total_publications', 1)*100:.1f}%)</span>
                            </div>
                            <div class="progress-bar-container">
                                <div class="progress-bar-fill animate" style="width: {count/basic.get('total_publications', 1)*100:.1f}%; background: {oa_colors.get(status, '#BDC3C7')};">
                                    {count/basic.get('total_publications', 1)*100:.1f}%
                                </div>
                            </div>
                        </div>
                        '''
                        for status, count in basic.get('oa_breakdown', {}).items()
                        if count > 0 and status not in ['unknown']
                    ])}
                    
                    {f'''
                    <div style="margin: 6px 0;">
                        <div class="progress-bar-label">
                            <span><span class="color-dot" style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#BDC3C7;vertical-align:middle;margin-right:6px;"></span> 
                            <strong>{t('unknown')}</strong></span>
                            <span class="label-value">{basic.get('oa_breakdown', {}).get('unknown', 0)} ({basic.get('oa_breakdown', {}).get('unknown', 0)/basic.get('total_publications', 1)*100:.1f}%)</span>
                        </div>
                        <div class="progress-bar-container">
                            <div class="progress-bar-fill animate" style="width: {basic.get('oa_breakdown', {}).get('unknown', 0)/basic.get('total_publications', 1)*100:.1f}%; background: #BDC3C7;">
                                {basic.get('oa_breakdown', {}).get('unknown', 0)/basic.get('total_publications', 1)*100:.1f}%
                            </div>
                        </div>
                    </div>
                    ''' if basic.get('oa_breakdown', {}).get('unknown', 0) > 0 else ''}
                    
                </div>
            </div>
            
            <!-- ============================================================ -->
            <!-- SECTION 2: ANALYZED ARTICLES -->
            <!-- ============================================================ -->
            <div id="analyzed_articles" class="section">
                <div class="section-header" onclick="toggleSection('analyzed_content')">
                    <div class="section-title">
                        <span class="icon">📄</span> {t('analyzed_articles')}
                        <span class="section-badge">{len(publications)} {t('articles')}</span>
                    </div>
                    <span class="toggle-indicator" id="analyzed_indicator">▼</span>
                </div>
                <div class="section-divider"></div>
                <div id="analyzed_content" class="section-content">
                    
                    <!-- ===== AUTHOR DISTRIBUTION ===== -->
                    <h3 style="color: {primary}; font-size: 16px;">{t('author_distribution')}</h3>
                    
                    <div class="dist-grid">
                        <div class="dist-card">
                            <h4>{t('author_distribution_analyzed')}</h4>
                            <div style="margin: 6px 0;">
                                <div class="progress-bar-label">
                                    <span>1 author</span>
                                    <span class="label-value">{analyzed_dist.get('1', 0)}</span>
                                </div>
                                <div class="progress-bar-container">
                                    <div class="progress-bar-fill animate" style="width: {analyzed_dist.get('1', 0)/max(analyzed_total, 1)*100:.1f}%; background: #667eea;">
                                        {analyzed_dist.get('1', 0)/max(analyzed_total, 1)*100:.1f}%
                                    </div>
                                </div>
                            </div>
                            <div style="margin: 6px 0;">
                                <div class="progress-bar-label">
                                    <span>2 authors</span>
                                    <span class="label-value">{analyzed_dist.get('2', 0)}</span>
                                </div>
                                <div class="progress-bar-container">
                                    <div class="progress-bar-fill animate" style="width: {analyzed_dist.get('2', 0)/max(analyzed_total, 1)*100:.1f}%; background: #f39c12;">
                                        {analyzed_dist.get('2', 0)/max(analyzed_total, 1)*100:.1f}%
                                    </div>
                                </div>
                            </div>
                            <div style="margin: 6px 0;">
                                <div class="progress-bar-label">
                                    <span>3-5 authors</span>
                                    <span class="label-value">{analyzed_dist.get('3-5', 0)}</span>
                                </div>
                                <div class="progress-bar-container">
                                    <div class="progress-bar-fill animate" style="width: {analyzed_dist.get('3-5', 0)/max(analyzed_total, 1)*100:.1f}%; background: #e74c3c;">
                                        {analyzed_dist.get('3-5', 0)/max(analyzed_total, 1)*100:.1f}%
                                    </div>
                                </div>
                            </div>
                            <div style="margin: 6px 0;">
                                <div class="progress-bar-label">
                                    <span>6-7 authors</span>
                                    <span class="label-value">{analyzed_dist.get('6-7', 0)}</span>
                                </div>
                                <div class="progress-bar-container">
                                    <div class="progress-bar-fill animate" style="width: {analyzed_dist.get('6-7', 0)/max(analyzed_total, 1)*100:.1f}%; background: #2ecc71;">
                                        {analyzed_dist.get('6-7', 0)/max(analyzed_total, 1)*100:.1f}%
                                    </div>
                                </div>
                            </div>
                            <div style="margin: 6px 0;">
                                <div class="progress-bar-label">
                                    <span>8-10 authors</span>
                                    <span class="label-value">{analyzed_dist.get('8-10', 0)}</span>
                                </div>
                                <div class="progress-bar-container">
                                    <div class="progress-bar-fill animate" style="width: {analyzed_dist.get('8-10', 0)/max(analyzed_total, 1)*100:.1f}%; background: #3498db;">
                                        {analyzed_dist.get('8-10', 0)/max(analyzed_total, 1)*100:.1f}%
                                    </div>
                                </div>
                            </div>
                            <div style="margin: 6px 0;">
                                <div class="progress-bar-label">
                                    <span>11-15 authors</span>
                                    <span class="label-value">{analyzed_dist.get('11-15', 0)}</span>
                                </div>
                                <div class="progress-bar-container">
                                    <div class="progress-bar-fill animate" style="width: {analyzed_dist.get('11-15', 0)/max(analyzed_total, 1)*100:.1f}%; background: #9b59b6;">
                                        {analyzed_dist.get('11-15', 0)/max(analyzed_total, 1)*100:.1f}%
                                    </div>
                                </div>
                            </div>
                            <div style="margin: 6px 0;">
                                <div class="progress-bar-label">
                                    <span>15+ authors</span>
                                    <span class="label-value">{analyzed_dist.get('15+', 0)}</span>
                                </div>
                                <div class="progress-bar-container">
                                    <div class="progress-bar-fill animate" style="width: {analyzed_dist.get('15+', 0)/max(analyzed_total, 1)*100:.1f}%; background: #1abc9c;">
                                        {analyzed_dist.get('15+', 0)/max(analyzed_total, 1)*100:.1f}%
                                    </div>
                                </div>
                            </div>
                            <div class="total-label">Total: {analyzed_total} {t('publications')}</div>
                        </div>
                        
                        <div class="dist-card">
                            <h4>{t('author_distribution_citing')}</h4>
                            <div style="margin: 6px 0;">
                                <div class="progress-bar-label">
                                    <span>1 author</span>
                                    <span class="label-value">{citing_dist.get('1', 0)}</span>
                                </div>
                                <div class="progress-bar-container">
                                    <div class="progress-bar-fill animate" style="width: {citing_dist.get('1', 0)/max(citing_total, 1)*100:.1f}%; background: #667eea;">
                                        {citing_dist.get('1', 0)/max(citing_total, 1)*100:.1f}%
                                    </div>
                                </div>
                            </div>
                            <div style="margin: 6px 0;">
                                <div class="progress-bar-label">
                                    <span>2 authors</span>
                                    <span class="label-value">{citing_dist.get('2', 0)}</span>
                                </div>
                                <div class="progress-bar-container">
                                    <div class="progress-bar-fill animate" style="width: {citing_dist.get('2', 0)/max(citing_total, 1)*100:.1f}%; background: #f39c12;">
                                        {citing_dist.get('2', 0)/max(citing_total, 1)*100:.1f}%
                                    </div>
                                </div>
                            </div>
                            <div style="margin: 6px 0;">
                                <div class="progress-bar-label">
                                    <span>3-5 authors</span>
                                    <span class="label-value">{citing_dist.get('3-5', 0)}</span>
                                </div>
                                <div class="progress-bar-container">
                                    <div class="progress-bar-fill animate" style="width: {citing_dist.get('3-5', 0)/max(citing_total, 1)*100:.1f}%; background: #e74c3c;">
                                        {citing_dist.get('3-5', 0)/max(citing_total, 1)*100:.1f}%
                                    </div>
                                </div>
                            </div>
                            <div style="margin: 6px 0;">
                                <div class="progress-bar-label">
                                    <span>6-7 authors</span>
                                    <span class="label-value">{citing_dist.get('6-7', 0)}</span>
                                </div>
                                <div class="progress-bar-container">
                                    <div class="progress-bar-fill animate" style="width: {citing_dist.get('6-7', 0)/max(citing_total, 1)*100:.1f}%; background: #2ecc71;">
                                        {citing_dist.get('6-7', 0)/max(citing_total, 1)*100:.1f}%
                                    </div>
                                </div>
                            </div>
                            <div style="margin: 6px 0;">
                                <div class="progress-bar-label">
                                    <span>8-10 authors</span>
                                    <span class="label-value">{citing_dist.get('8-10', 0)}</span>
                                </div>
                                <div class="progress-bar-container">
                                    <div class="progress-bar-fill animate" style="width: {citing_dist.get('8-10', 0)/max(citing_total, 1)*100:.1f}%; background: #3498db;">
                                        {citing_dist.get('8-10', 0)/max(citing_total, 1)*100:.1f}%
                                    </div>
                                </div>
                            </div>
                            <div style="margin: 6px 0;">
                                <div class="progress-bar-label">
                                    <span>11-15 authors</span>
                                    <span class="label-value">{citing_dist.get('11-15', 0)}</span>
                                </div>
                                <div class="progress-bar-container">
                                    <div class="progress-bar-fill animate" style="width: {citing_dist.get('11-15', 0)/max(citing_total, 1)*100:.1f}%; background: #9b59b6;">
                                        {citing_dist.get('11-15', 0)/max(citing_total, 1)*100:.1f}%
                                    </div>
                                </div>
                            </div>
                            <div style="margin: 6px 0;">
                                <div class="progress-bar-label">
                                    <span>15+ authors</span>
                                    <span class="label-value">{citing_dist.get('15+', 0)}</span>
                                </div>
                                <div class="progress-bar-container">
                                    <div class="progress-bar-fill animate" style="width: {citing_dist.get('15+', 0)/max(citing_total, 1)*100:.1f}%; background: #1abc9c;">
                                        {citing_dist.get('15+', 0)/max(citing_total, 1)*100:.1f}%
                                    </div>
                                </div>
                            </div>
                            <div class="total-label">Total: {citing_total} {t('citations')}</div>
                        </div>
                    </div>
                    
                    <!-- Author Analysis -->
                    <h3 style="color: {primary}; font-size: 16px; margin-top: 20px;">{t('author_analysis')}</h3>
                    <div class="scrollable-table">
                        <table id="author_table">
                            <thead>
                                <tr>
                                    <th class="sortable" onclick="sortTable('author_table', 0)">{t('rank')}</th>
                                    <th class="sortable" onclick="sortTable('author_table', 1)">{t('authors')}</th>
                                    <th class="sortable" onclick="sortTable('author_table', 2)">ORCID</th>
                                    <th>{t('affiliations')}</th>
                                    <th>{t('countries')}</th>
                                    <th class="sortable" onclick="sortTable('author_table', 5)">{t('publications_count')}</th>
                                    <th class="sortable" onclick="sortTable('author_table', 6)">{t('citations_count')}</th>
                                </tr>
                            </thead>
                            <tbody>
                                {''.join([
                                    f'''
                                    <tr>
                                        <td>{i+1}</td>
                                        <td><strong>{html.escape(author['name'])}</strong></td>
                                        <td>{f'<a href="https://orcid.org/{author["orcid"]}" target="_blank" class="doi-link orcid-full">{author["orcid"]}</a>' if author.get('orcid') else '-'}</td>
                                        <td>{', '.join([html.escape(a) for a in author.get('affiliations', [])[:3]])}{' +' + str(len(author.get('affiliations', []))-3) if len(author.get('affiliations', [])) > 3 else ''}</td>
                                        <td>{', '.join(author.get('countries', [])[:3])}</td>
                                        <td>{get_color_scale_html(author.get('publications', 0), max_publications)}</td>
                                        <td>{get_color_scale_html(author.get('citations', 0), max_citations_auth)}</td>
                                    </tr>
                                    '''
                                    for i, author in enumerate(author_analysis.get('top_authors', [])[:30])
                                ])}
                            </tbody>
                        </table>
                    </div>
                    
                    <!-- Top Affiliations -->
                    <h3 style="color: {primary}; font-size: 16px; margin-top: 20px;">{t('top_affiliations')}</h3>
                    <div class="scrollable-table" style="max-height: 300px;">
                        <table id="aff_table">
                            <thead>
                                <tr>
                                    <th class="sortable" onclick="sortTable('aff_table', 0)">{t('rank')}</th>
                                    <th class="sortable" onclick="sortTable('aff_table', 1)">{t('affiliations')}</th>
                                    <th class="sortable" onclick="sortTable('aff_table', 2)">{t('publications_count')}</th>
                                    <th>ROR ID</th>
                                </tr>
                            </thead>
                            <tbody>
                                {''.join([
                                    f'''
                                    <tr>
                                        <td>{i+1}</td>
                                        <td>{html.escape(aff['name'])}</td>
                                        <td>{get_color_scale_html(aff['count'], max_aff_count)}</td>
                                        <td>
                                            {f'<a href="https://colab.ws/organizations/{aff["ror_short"]}" target="_blank" class="doi-link" style="font-family: monospace; font-size: 11px;">{aff["ror_short"][:8]}...</a>' 
                                             if aff.get('ror_short') and aff['ror_short'] else '-'}
                                        </td>
                                    </tr>
                                    '''
                                    for i, aff in enumerate(affiliation_analysis.get('top_affiliations', [])[:30])
                                ])}
                            </tbody>
                        </table>
                    </div>
                    
                    <!-- Geographic Analysis -->
                    <h3 style="color: {primary}; font-size: 16px; margin-top: 20px;">{t('geographic_analysis')}</h3>
                    
                    <div class="geo-grid">
                        <div class="geo-card">
                            <h4>{t('unique_countries_per_publication')}</h4>
                            <div>
                                <div><span class="geo-value">{geographic.get('unique_countries_per_publication', {}).get('avg', 0):.2f}</span> <span class="geo-label">Avg</span></div>
                                <div><span class="geo-value">{geographic.get('unique_countries_per_publication', {}).get('min', 0)}</span> <span class="geo-label">Min</span></div>
                                <div><span class="geo-value">{geographic.get('unique_countries_per_publication', {}).get('max', 0)}</span> <span class="geo-label">Max</span></div>
                                <div style="margin-top: 8px; font-size: 12px; color: #7F8C8D;">Based on {geographic.get('unique_countries_per_publication', {}).get('total_works', 0)} publications with country data</div>
                            </div>
                        </div>
                        <div class="geo-card">
                            <h4>{t('collaboration_patterns')}</h4>
                            <div>
                                <div><span class="geo-value">{geographic.get('collaboration_patterns', {}).get('single_country', 0)}</span> <span class="geo-label">{t('single_country')} ({geographic.get('collaboration_patterns', {}).get('single_country_ratio', 0)*100:.1f}%)</span></div>
                                <div><span class="geo-value">{geographic.get('collaboration_patterns', {}).get('multi_country', 0)}</span> <span class="geo-label">{t('multi_country')} ({(1-geographic.get('collaboration_patterns', {}).get('single_country_ratio', 0))*100:.1f}%)</span></div>
                                <div style="margin-top: 8px; font-size: 12px; color: #7F8C8D;">Total: {geographic.get('collaboration_patterns', {}).get('total', 0)} publications</div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Collaboration Patterns Progress Bars -->
                    <div style="margin: 10px 0 20px 0;">
                        <div style="display: flex; gap: 20px;">
                            <div style="flex: 1;">
                                <div class="progress-bar-label">
                                    <span>{t('single_country')}</span>
                                    <span class="label-value">{geographic.get('collaboration_patterns', {}).get('single_country', 0)} ({geographic.get('collaboration_patterns', {}).get('single_country_ratio', 0)*100:.1f}%)</span>
                                </div>
                                <div class="progress-bar-container">
                                    <div class="progress-bar-fill animate" style="width: {geographic.get('collaboration_patterns', {}).get('single_country_ratio', 0)*100:.1f}%; background: {primary};">
                                        {geographic.get('collaboration_patterns', {}).get('single_country_ratio', 0)*100:.1f}%
                                    </div>
                                </div>
                            </div>
                            <div style="flex: 1;">
                                <div class="progress-bar-label">
                                    <span>{t('multi_country')}</span>
                                    <span class="label-value">{geographic.get('collaboration_patterns', {}).get('multi_country', 0)} ({(1-geographic.get('collaboration_patterns', {}).get('single_country_ratio', 0))*100:.1f}%)</span>
                                </div>
                                <div class="progress-bar-container">
                                    <div class="progress-bar-fill animate" style="width: {(1-geographic.get('collaboration_patterns', {}).get('single_country_ratio', 0))*100:.1f}%; background: {secondary};">
                                        {(1-geographic.get('collaboration_patterns', {}).get('single_country_ratio', 0))*100:.1f}%
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Countries -->
                    <h4 style="color: {primary}; margin-top: 15px; font-size: 14px;">{t('countries')}</h4>
                    <div class="scrollable-table" style="max-height: 400px;">
                        <table id="country_table">
                            <thead>
                                <tr>
                                    <th class="sortable" onclick="sortTable('country_table', 0)">{t('rank')}</th>
                                    <th class="sortable" onclick="sortTable('country_table', 1)">{t('countries')}</th>
                                    <th class="sortable" onclick="sortTable('country_table', 2)">{t('unique_works')}</th>
                                    <th class="sortable" onclick="sortTable('country_table', 3)">{t('authors_count')}</th>
                                </tr>
                            </thead>
                            <tbody>
                                {''.join([
                                    f'''
                                    <tr>
                                        <td>{i+1}</td>
                                        <td><strong>{html.escape(country['country'])}</strong></td>
                                        <td>{get_color_scale_html(country['unique_works'], max_unique_works)}</td>
                                        <td>{get_color_scale_html(country['authors_count'], max_authors_count)}</td>
                                    </tr>
                                    '''
                                    for i, country in enumerate(geographic.get('country_stats', [])[:30])
                                ])}
                            </tbody>
                        </table>
                    </div>
                    
                    <!-- Collaboration Couples -->
                    <h4 style="color: {primary}; margin-top: 15px; font-size: 14px;">{t('collaboration_couples')}</h4>
                    <div class="scrollable-table" style="max-height: 300px;">
                        <table id="couple_table">
                            <thead>
                                <tr>
                                    <th class="sortable" onclick="sortTable('couple_table', 0)">{t('country_pair')}</th>
                                    <th class="sortable" onclick="sortTable('couple_table', 1)">{t('frequency')}</th>
                                </tr>
                            </thead>
                            <tbody>
                                {''.join([
                                    f'<tr><td>{html.escape(couple["country1"])} — {html.escape(couple["country2"])}</td><td>{get_color_scale_html(couple["frequency"], geographic.get("collaboration_couples", [{}])[0].get("frequency", 1) if geographic.get("collaboration_couples") else 1)}</td></tr>'
                                    for couple in geographic.get('collaboration_couples', [])[:30]
                                ])}
                            </tbody>
                        </table>
                    </div>
                    
                </div>
            </div>
            
            <!-- ============================================================ -->
            <!-- SECTION 3: CITATION ANALYSIS -->
            <!-- ============================================================ -->
            <div id="citation_analysis" class="section">
                <div class="section-header" onclick="toggleSection('citation_content')">
                    <div class="section-title">
                        <span class="icon">📈</span> {t('citation_analysis')}
                        <span class="section-badge">{basic.get('total_citations', 0):,} {t('citations')}</span>
                    </div>
                    <span class="toggle-indicator" id="citation_indicator">▼</span>
                </div>
                <div class="section-divider"></div>
                <div id="citation_content" class="section-content">
                    
                    <!-- Citation Dynamics by Year -->
                    <h3 style="color: {primary}; font-size: 16px;">{t('citation_dynamics_by_year')}</h3>
                    <div class="scrollable-table" style="max-height: 400px;">
                        <table id="dynamics_table">
                            <thead>
                                <tr>
                                    <th class="sortable" onclick="sortTable('dynamics_table', 0)">{t('publication_year')}</th>
                                    <th class="sortable" onclick="sortTable('dynamics_table', 1)">{t('citation_year')}</th>
                                    <th class="sortable" onclick="sortTable('dynamics_table', 2)">{t('citations_count')}</th>
                                </tr>
                            </thead>
                            <tbody>
                                {''.join([
                                    f'<tr><td>{row["publication_year"]}</td><td>{row["citation_year"]}</td><td>{get_color_scale_html(row["citations_count"], max_citation_count)}</td></tr>'
                                    for row in citation.get('dynamics', [])
                                ])}
                            </tbody>
                        </table>
                    </div>
                    
                    <!-- First Citation Analysis -->
                    <h3 style="color: {primary}; font-size: 16px; margin-top: 20px;">{t('first_citation_analysis')}</h3>
                    <div class="metrics-grid metrics-grid-4" style="grid-template-columns: repeat(4, 1fr);">
                        <div class="metric-card">
                            <span class="metric-icon">⏱️</span>
                            <div class="metric-value">{citation.get('first_citation_stats', {}).get('min', 'N/A')}</div>
                            <div class="metric-label">{t('min_lag')}</div>
                        </div>
                        <div class="metric-card">
                            <span class="metric-icon">⏱️</span>
                            <div class="metric-value">{citation.get('first_citation_stats', {}).get('max', 'N/A')}</div>
                            <div class="metric-label">{t('max_lag')}</div>
                        </div>
                        <div class="metric-card">
                            <span class="metric-icon">⏱️</span>
                            <div class="metric-value">{citation.get('first_citation_stats', {}).get('avg', 0):.1f}</div>
                            <div class="metric-label">{t('avg_lag')}</div>
                        </div>
                        <div class="metric-card">
                            <span class="metric-icon">⏱️</span>
                            <div class="metric-value">{citation.get('first_citation_stats', {}).get('median', 0):.1f}</div>
                            <div class="metric-label">{t('median_lag')}</div>
                        </div>
                    </div>
                    
                    <!-- Cumulative Citations -->
                    <h3 style="color: {primary}; font-size: 16px; margin-top: 20px;">{t('cumulative_citations')}</h3>
                    <div class="scrollable-table" style="max-height: 300px;">
                        <table id="cum_table">
                            <thead>
                                <tr>
                                    <th class="sortable" onclick="sortTable('cum_table', 0)">{t('year')}</th>
                                    <th class="sortable" onclick="sortTable('cum_table', 1)">{t('citations')}</th>
                                </tr>
                            </thead>
                            <tbody>
                                {''.join([
                                    f'<tr><td>{row["year"]}</td><td>{get_color_scale_html(row["citations"], citation.get("cumulative", [{}])[-1].get("citations", 1) if citation.get("cumulative") else 1)}</td></tr>'
                                    for row in citation.get('cumulative', [])
                                ])}
                            </tbody>
                        </table>
                    </div>
                    
                    <!-- Citation Network Heatmap -->
                    <h3 style="color: {primary}; font-size: 16px; margin-top: 20px;">{t('citation_network_heatmap')}</h3>
                    <div class="scrollable-table" style="max-height: 500px;">
                        <table id="heatmap_table">
                            <thead>
                                <tr>
                                    <th>{t('publication_year')} \ {t('citation_year')}</th>
                                    {''.join([
                                        f'<th>{year}</th>'
                                        for year in citation.get('heatmap_years', [])
                                    ])}
                                </tr>
                            </thead>
                            <tbody>
                                {''.join([
                                    f'''
                                    <tr>
                                        <td><strong>{row.get("publication_year", "N/A")}</strong></td>
                                        {''.join([
                                            f'''
                                            <td class="heatmap-cell" style="
                                                {f'background: {get_heatmap_cell_color(row.get(year, 0), heatmap_max)};' if row.get(year) is not None and row.get(year) > 0 else 'background: transparent;'}
                                                color: {'#1a1a1a' if row.get(year) is not None and row.get(year) > 0 and row.get(year) / max(heatmap_max, 1) > 0.6 else '#333' if row.get(year) is not None and row.get(year) > 0 else 'transparent'};
                                                {'' if row.get(year) is not None else 'cursor: default;'}
                                            ">
                                                {row.get(year) if row.get(year) is not None and row.get(year) > 0 else ''}
                                            </td>
                                            '''
                                            for year in citation.get('heatmap_years', [])
                                        ])}
                                    </tr>
                                    '''
                                    for row in citation.get('heatmap', [])
                                ])}
                            </tbody>
                        </table>
                    </div>
                    
                </div>
            </div>
            
            <!-- ============================================================ -->
            <!-- SECTION 4: CITING PUBLICATIONS (was Most Cited Publications) -->
            <!-- ============================================================ -->
            <div id="citing_publications" class="section">
                <div class="section-header" onclick="toggleSection('cited_content')">
                    <div class="section-title">
                        <span class="icon">📄</span> {t('citing_publications')}
                        <span class="section-badge">{len(all_citing_works)} {t('citations')}</span>
                    </div>
                    <span class="toggle-indicator" id="cited_indicator">▼</span>
                </div>
                <div class="section-divider"></div>
                <div id="cited_content" class="section-content">
                    
                    <div class="filter-section">
                        <div class="filter-row">
                            <div class="filter-group">
                                <label>🔍</label>
                                <input type="text" id="citedTitleFilter" placeholder="{t('filter_by_title')}..." onkeyup="filterCited()">
                            </div>
                            <div class="filter-group">
                                <label>📅</label>
                                <select id="citedYearFilter" onchange="filterCited()">
                                    <option value="">{t('all_years')}</option>
                                    {''.join([
                                        f'<option value="{year}">{year}</option>'
                                        for year in sorted(set([w.get('year') for w in all_citing_works if w.get('year')]), reverse=True)
                                    ])}
                                </select>
                            </div>
                            <div class="filter-group">
                                <label>👤</label>
                                <input type="text" id="citedAuthorFilter" placeholder="{t('filter_by_author')}..." onkeyup="filterCited()">
                            </div>
                            <div class="filter-group">
                                <label>🏛️</label>
                                <input type="text" id="citedAffiliationFilter" placeholder="{t('filter_by_affiliation')}..." onkeyup="filterCited()">
                            </div>
                            <div class="filter-group">
                                <label>📚</label>
                                <input type="text" id="citedJournalFilter" placeholder="{t('filter_by_journal')}..." onkeyup="filterCited()">
                            </div>
                            <div class="filter-group">
                                <label>🏢</label>
                                <input type="text" id="citedPublisherFilter" placeholder="{t('filter_by_publisher')}..." onkeyup="filterCited()">
                            </div>
                            <div class="filter-group">
                                <label>📊</label>
                                <input type="number" id="citedCitationFilter" placeholder="{t('filter_by_citations')}..." min="0" onchange="filterCited()">
                            </div>
                        </div>
                        <div class="filter-stats">
                            <span id="citedVisibleCount">{t('visible_count', shown=len(all_citing_works), total=len(all_citing_works))}</span>
                        </div>
                    </div>
                    
                    <div class="scrollable-table" style="max-height: 600px;">
                        <table id="citedTable">
                            <thead>
                                <tr>
                                    <th class="sortable" onclick="sortTable('citedTable', 0)">#</th>
                                    <th class="sortable" onclick="sortTable('citedTable', 1)">{t('title')}</th>
                                    <th class="sortable" onclick="sortTable('citedTable', 2)">{t('year')}</th>
                                    <th class="sortable" onclick="sortTable('citedTable', 3)">{t('authors')}</th>
                                    <th class="sortable" onclick="sortTable('citedTable', 4)">{t('affiliations')}</th>
                                    <th class="sortable" onclick="sortTable('citedTable', 5)">{t('journal')}</th>
                                    <th class="sortable" onclick="sortTable('citedTable', 6)">{t('publishers')}</th>
                                    <th class="sortable" onclick="sortTable('citedTable', 7)">{t('citations')}</th>
                                    <th class="sortable" onclick="sortTable('citedTable', 8)">{t('citations')} (ours)</th>
                                    <th>{t('grants_funding')}</th>
                                    <th>DOI</th>
                                </tr>
                            </thead>
                            <tbody>
                                {all_citing_works_rows if all_citing_works_rows else f'<tr><td colspan="11" style="text-align: center; color: #999; font-style: italic;">{t("no_cited_publications")}</td></tr>'}
                            </tbody>
                        </table>
                    </div>
                    
                </div>
            </div>
            
            <!-- ============================================================ -->
            <!-- SECTION 5: CITING WORKS ANALYSIS -->
            <!-- ============================================================ -->
            <div id="citing_works" class="section">
                <div class="section-header" onclick="toggleSection('citing_content')">
                    <div class="section-title">
                        <span class="icon">📚</span> {t('citing_works_analysis')}
                        <span class="section-badge">{citing.get('total_citing_works', 0):,} {t('citations')}</span>
                    </div>
                    <span class="toggle-indicator" id="citing_indicator">▼</span>
                </div>
                <div class="section-divider"></div>
                <div id="citing_content" class="section-content">
                    
                    <div class="metrics-grid" style="grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));">
                        <div class="metric-card">
                            <span class="metric-icon">📚</span>
                            <div class="metric-value">{citing.get('total_citing_works', 0):,}</div>
                            <div class="metric-label">{t('total_citing_works')}</div>
                        </div>
                    </div>
                    
                    <!-- Top Citing Authors -->
                    <h3 style="color: {primary}; font-size: 16px;">{t('top_citing_authors')}</h3>
                    <div class="scrollable-table" style="max-height: 300px;">
                        <table id="citing_auth_table">
                            <thead>
                                <tr>
                                    <th class="sortable" onclick="sortTable('citing_auth_table', 0)">{t('rank')}</th>
                                    <th class="sortable" onclick="sortTable('citing_auth_table', 1)">{t('authors')}</th>
                                    <th class="sortable" onclick="sortTable('citing_auth_table', 2)">{t('citing_author_orcid')}</th>
                                    <th class="sortable" onclick="sortTable('citing_auth_table', 3)">{t('citations_count')}</th>
                                </tr>
                            </thead>
                            <tbody>
                                {''.join([
                                    f'''
                                    <tr>
                                        <td>{i+1}</td>
                                        <td>{html.escape(author['name'])}</td>
                                        <td>{f'<a href="https://orcid.org/{author["orcid"]}" target="_blank" class="doi-link orcid-full">{author["orcid"]}</a>' if author.get('orcid') else '-'}</td>
                                        <td>{get_color_scale_html(author['count'], max_citing_auth)}</td>
                                    </tr>
                                    '''
                                    for i, author in enumerate(citing.get('top_authors', [])[:30])
                                ])}
                            </tbody>
                        </table>
                    </div>
                    
                    <!-- Top Citing Affiliations -->
                    <h3 style="color: {primary}; font-size: 16px; margin-top: 20px;">{t('top_citing_affiliations')}</h3>
                    <div class="scrollable-table" style="max-height: 300px;">
                        <table id="citing_aff_table">
                            <thead>
                                <tr>
                                    <th class="sortable" onclick="sortTable('citing_aff_table', 0)">{t('rank')}</th>
                                    <th class="sortable" onclick="sortTable('citing_aff_table', 1)">{t('affiliations')}</th>
                                    <th class="sortable" onclick="sortTable('citing_aff_table', 2)">{t('citations_count')}</th>
                                    <th>ROR ID</th>
                                </tr>
                            </thead>
                            <tbody>
                                {''.join([
                                    f'''
                                    <tr>
                                        <td>{i+1}</td>
                                        <td>{html.escape(aff['name'])}</td>
                                        <td>{get_color_scale_html(aff['count'], max_citing_aff)}</td>
                                        <td>
                                            {f'<a href="https://colab.ws/organizations/{aff["ror_short"]}" target="_blank" class="doi-link" style="font-family: monospace; font-size: 11px;">{aff["ror_short"][:8]}...</a>' 
                                             if aff.get('ror_short') and aff['ror_short'] else '-'}
                                        </td>
                                    </tr>
                                    '''
                                    for i, aff in enumerate(citing.get('top_affiliations', [])[:30])
                                ])}
                            </tbody>
                        </table>
                    </div>
                    
                    <!-- Top Citing Countries -->
                    <h3 style="color: {primary}; font-size: 16px; margin-top: 20px;">{t('top_citing_countries')}</h3>
                    <div class="scrollable-table" style="max-height: 300px;">
                        <table id="citing_country_table">
                            <thead>
                                <tr>
                                    <th class="sortable" onclick="sortTable('citing_country_table', 0)">{t('rank')}</th>
                                    <th class="sortable" onclick="sortTable('citing_country_table', 1)">{t('countries')}</th>
                                    <th class="sortable" onclick="sortTable('citing_country_table', 2)">{t('citations_count')}</th>
                                </tr>
                            </thead>
                            <tbody>
                                {''.join([
                                    f'<tr><td>{i+1}</td><td>{html.escape(country["name"])}</td><td>{get_color_scale_html(country["count"], max_citing_country)}</td></tr>'
                                    for i, country in enumerate(citing.get('top_countries', [])[:30])
                                ])}
                            </tbody>
                        </table>
                    </div>
                    
                    <!-- Top Citing Journals -->
                    <h3 style="color: {primary}; font-size: 16px; margin-top: 20px;">{t('top_citing_journals')}</h3>
                    <div class="scrollable-table" style="max-height: 300px;">
                        <table id="citing_journal_table">
                            <thead>
                                <tr>
                                    <th class="sortable" onclick="sortTable('citing_journal_table', 0)">{t('rank')}</th>
                                    <th class="sortable" onclick="sortTable('citing_journal_table', 1)">{t('journal')}</th>
                                    <th class="sortable" onclick="sortTable('citing_journal_table', 2)">{t('citations_count')}</th>
                                </tr>
                            </thead>
                            <tbody>
                                {''.join([
                                    f'<tr><td>{i+1}</td><td>{html.escape(journal["name"])}</td><td>{get_color_scale_html(journal["count"], max_citing_journal)}</td></tr>'
                                    for i, journal in enumerate(citing.get('top_journals', [])[:30])
                                ])}
                            </tbody>
                        </table>
                    </div>
                    
                    <!-- Top Citing Publishers -->
                    <h3 style="color: {primary}; font-size: 16px; margin-top: 20px;">{t('top_citing_publishers')}</h3>
                    <div class="scrollable-table" style="max-height: 300px;">
                        <table id="citing_pub_table">
                            <thead>
                                <tr>
                                    <th class="sortable" onclick="sortTable('citing_pub_table', 0)">{t('rank')}</th>
                                    <th class="sortable" onclick="sortTable('citing_pub_table', 1)">{t('publishers')}</th>
                                    <th class="sortable" onclick="sortTable('citing_pub_table', 2)">{t('citations_count')}</th>
                                </tr>
                            </thead>
                            <tbody>
                                {''.join([
                                    f'<tr><td>{i+1}</td><td>{html.escape(pub["name"])}</td><td>{get_color_scale_html(pub["count"], max_citing_pub)}</td></tr>'
                                    for i, pub in enumerate(citing.get('top_publishers', [])[:30])
                                ])}
                            </tbody>
                        </table>
                    </div>
                    
                </div>
            </div>
            
            <!-- ============================================================ -->
            <!-- SECTION 6: TOPICS ANALYSIS -->
            <!-- ============================================================ -->
            <div id="topics_analysis" class="section">
                <div class="section-header" onclick="toggleSection('topics_content')">
                    <div class="section-title">
                        <span class="icon">🏷️</span> {t('topics_analysis')}
                        <span class="section-badge">{len(topics.get('topics', []))} {t('topics')}</span>
                    </div>
                    <span class="toggle-indicator" id="topics_indicator">▼</span>
                </div>
                <div class="section-divider"></div>
                <div id="topics_content" class="section-content">
                    
                    <h3 style="color: {primary}; font-size: 16px;">Topics</h3>
                    <div class="scrollable-table" style="max-height: 400px;">
                        <table id="topics_table">
                            <thead>
                                <tr>
                                    <th class="sortable" onclick="sortTable('topics_table', 0)">Topic</th>
                                    <th class="sortable" onclick="sortTable('topics_table', 1)">{t('analyzed_count')}</th>
                                    <th class="sortable" onclick="sortTable('topics_table', 2)">{t('citing_count')}</th>
                                    <th class="sortable" onclick="sortTable('topics_table', 3)">{t('analyzed_norm_count')}</th>
                                    <th class="sortable" onclick="sortTable('topics_table', 4)">{t('citing_norm_count')}</th>
                                    <th class="sortable" onclick="sortTable('topics_table', 5)">{t('total_norm_count')}</th>
                                    <th>{t('first_year')}</th>
                                    <th>{t('peak_year')}</th>
                                </tr>
                            </thead>
                            <tbody>
                                {''.join([
                                    f'''
                                    <tr>
                                        <td class="word-wrap">{html.escape(topic['topic'][:50])}{'...' if len(topic['topic']) > 50 else ''}</td>
                                        <td>{get_color_scale_html(topic['analyzed_count'], max_analyzed)}</td>
                                        <td>{get_color_scale_html(topic['citing_count'], max_citing)}</td>
                                        <td>{get_color_scale_html_with_format(topic['analyzed_norm_count'], max_analyzed_norm, decimals=3)}</td>
                                        <td>{get_color_scale_html_with_format(topic['citing_norm_count'], max_citing_norm, decimals=3)}</td>
                                        <td>{get_color_scale_html_with_format(topic['total_norm_count'], max_total_norm, decimals=3)}</td>
                                        <td>{topic['first_year'] or 'N/A'}</td>
                                        <td>{topic['peak_year'] or 'N/A'}</td>
                                    </tr>
                                    '''
                                    for topic in topics.get('topics', [])[:30]
                                ])}
                            </tbody>
                        </table>
                    </div>
                    
                    <!-- Top Cited Topics with Progress Bars -->
                    <h3 style="color: {primary}; font-size: 16px; margin-top: 20px;">{t('top_cited_topics')}</h3>
                    {''.join([
                        f'''
                        <div style="margin: 4px 0;">
                            <div class="progress-bar-label">
                                <span>{i+1}. {html.escape(topic[0][:50])}{'...' if len(topic[0]) > 50 else ''}</span>
                                <span class="label-value">{topic[1]} {t('publications')}</span>
                            </div>
                            <div class="progress-bar-container">
                                <div class="progress-bar-fill animate" style="width: {topic[1]/topics.get('top_cited_topics', [{}])[0][1]*100 if topics.get('top_cited_topics') and topics.get('top_cited_topics')[0][1] > 0 else 0:.1f}%; background: linear-gradient(90deg, {primary}, {secondary});">
                                    {topic[1]}
                                </div>
                            </div>
                        </div>
                        '''
                        for i, topic in enumerate(topics.get('top_cited_topics', [])[:10])
                    ])}
                    
                    <!-- Top Cited Subtopics -->
                    <h3 style="color: {primary}; font-size: 16px; margin-top: 20px;">{t('top_cited_subtopics')}</h3>
                    {''.join([
                        f'''
                        <div style="margin: 4px 0;">
                            <div class="progress-bar-label">
                                <span>{i+1}. {html.escape(subtopic[0][:50])}{'...' if len(subtopic[0]) > 50 else ''}</span>
                                <span class="label-value">{subtopic[1]} {t('publications')}</span>
                            </div>
                            <div class="progress-bar-container">
                                <div class="progress-bar-fill animate" style="width: {subtopic[1]/topics.get('top_cited_subtopics', [{}])[0][1]*100 if topics.get('top_cited_subtopics') and topics.get('top_cited_subtopics')[0][1] > 0 else 0:.1f}%; background: linear-gradient(90deg, {primary}, {secondary});">
                                    {subtopic[1]}
                                </div>
                            </div>
                        </div>
                        '''
                        for i, subtopic in enumerate(topics.get('top_cited_subtopics', [])[:10])
                    ])}
                    
                    <!-- Top Cited Fields -->
                    <h3 style="color: {primary}; font-size: 16px; margin-top: 20px;">{t('top_cited_fields')}</h3>
                    {''.join([
                        f'''
                        <div style="margin: 4px 0;">
                            <div class="progress-bar-label">
                                <span>{i+1}. {html.escape(field[0][:50])}{'...' if len(field[0]) > 50 else ''}</span>
                                <span class="label-value">{field[1]} {t('publications')}</span>
                            </div>
                            <div class="progress-bar-container">
                                <div class="progress-bar-fill animate" style="width: {field[1]/topics.get('top_cited_fields', [{}])[0][1]*100 if topics.get('top_cited_fields') and topics.get('top_cited_fields')[0][1] > 0 else 0:.1f}%; background: linear-gradient(90deg, {primary}, {secondary});">
                                    {field[1]}
                                </div>
                            </div>
                        </div>
                        '''
                        for i, field in enumerate(topics.get('top_cited_fields', [])[:10])
                    ])}
                    
                    <!-- Top Cited Domains -->
                    <h3 style="color: {primary}; font-size: 16px; margin-top: 20px;">{t('top_cited_domains')}</h3>
                    {''.join([
                        f'''
                        <div style="margin: 4px 0;">
                            <div class="progress-bar-label">
                                <span>{i+1}. {html.escape(domain[0][:50])}{'...' if len(domain[0]) > 50 else ''}</span>
                                <span class="label-value">{domain[1]} {t('publications')}</span>
                            </div>
                            <div class="progress-bar-container">
                                <div class="progress-bar-fill animate" style="width: {domain[1]/topics.get('top_cited_domains', [{}])[0][1]*100 if topics.get('top_cited_domains') and topics.get('top_cited_domains')[0][1] > 0 else 0:.1f}%; background: linear-gradient(90deg, {primary}, {secondary});">
                                    {domain[1]}
                                </div>
                            </div>
                        </div>
                        '''
                        for i, domain in enumerate(topics.get('top_cited_domains', [])[:10])
                    ])}
                    
                    <!-- Top Cited Concepts -->
                    <h3 style="color: {primary}; font-size: 16px; margin-top: 20px;">{t('top_cited_concepts')}</h3>
                    {''.join([
                        f'''
                        <div style="margin: 4px 0;">
                            <div class="progress-bar-label">
                                <span>{i+1}. {html.escape(concept[0][:50])}{'...' if len(concept[0]) > 50 else ''}</span>
                                <span class="label-value">{concept[1]} {t('publications')}</span>
                            </div>
                            <div class="progress-bar-container">
                                <div class="progress-bar-fill animate" style="width: {concept[1]/topics.get('top_cited_concepts', [{}])[0][1]*100 if topics.get('top_cited_concepts') and topics.get('top_cited_concepts')[0][1] > 0 else 0:.1f}%; background: linear-gradient(90deg, {primary}, {secondary});">
                                    {concept[1]}
                                </div>
                            </div>
                        </div>
                        '''
                        for i, concept in enumerate(topics.get('top_cited_concepts', [])[:10])
                    ])}
                    
                </div>
            </div>
            
            <!-- ============================================================ -->
            <!-- SECTION 7: GRANTS & FUNDING (NEW) -->
            <!-- ============================================================ -->
            <div id="grants_analysis" class="section">
                <div class="section-header" onclick="toggleSection('grants_content')">
                    <div class="section-title">
                        <span class="icon">💰</span> {t('grants_and_funding')}
                        <span class="section-badge">{grants_analyzed_unique_funders + grants_citing_unique_funders} {t('funder')}</span>
                    </div>
                    <span class="toggle-indicator" id="grants_indicator">▼</span>
                </div>
                <div class="section-divider"></div>
                <div id="grants_content" class="section-content">
                    
                    <!-- ============ ANALYZED PUBLICATIONS ============ -->
                    <h3 style="color: {primary}; font-size: 16px;">{t('analyzed_publications_grants')}</h3>
                    
                    <div class="metrics-grid" style="grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));">
                        <div class="metric-card">
                            <span class="metric-icon">💰</span>
                            <div class="metric-value">{grants_analyzed_unique_funders}</div>
                            <div class="metric-label">{t('unique_funders_analyzed')}</div>
                        </div>
                        <div class="metric-card">
                            <span class="metric-icon">🎫</span>
                            <div class="metric-value">{grants_analyzed_unique_awards}</div>
                            <div class="metric-label">{t('unique_awards_analyzed')}</div>
                        </div>
                    </div>
                    
                    <h4 style="color: {primary}; margin-top: 15px; font-size: 14px;">{t('top_funders_analyzed')} <span style="font-weight: 400; font-size: 12px; color: #7F8C8D;">({len(grants_analyzed_funders)} total)</span></h4>
                    {f'''
                    <div class="scrollable-table" style="max-height: 800px;">
                        <table id="grants_analyzed_funders_table">
                            <thead>
                                <tr>
                                    <th class="sortable" onclick="sortTable('grants_analyzed_funders_table', 0)">{t('rank')}</th>
                                    <th class="sortable" onclick="sortTable('grants_analyzed_funders_table', 1)">{t('funder')}</th>
                                    <th>{t('ror')}</th>
                                    <th class="sortable" onclick="sortTable('grants_analyzed_funders_table', 3)">{t('works_count')}</th>
                                </tr>
                            </thead>
                            <tbody>
                                {grants_analyzed_funders_rows}
                            </tbody>
                        </table>
                    </div>
                    ''' if grants_analyzed_funders else f'<p style="color: #7F8C8D; font-style: italic;">{t("no_grants_data")}</p>'}
                    
                    <h4 style="color: {primary}; margin-top: 15px; font-size: 14px;">{t('top_awards_analyzed')} <span style="font-weight: 400; font-size: 12px; color: #7F8C8D;">({len(grants_analyzed_awards)} total)</span></h4>
                    {f'''
                    <div class="scrollable-table" style="max-height: 800px;">
                        <table id="grants_analyzed_awards_table">
                            <thead>
                                <tr>
                                    <th class="sortable" onclick="sortTable('grants_analyzed_awards_table', 0)">{t('rank')}</th>
                                    <th class="sortable" onclick="sortTable('grants_analyzed_awards_table', 1)">{t('funder')}</th>
                                    <th class="sortable" onclick="sortTable('grants_analyzed_awards_table', 2)">{t('award_id')}</th>
                                    <th>{t('grant')}</th>
                                    <th class="sortable" onclick="sortTable('grants_analyzed_awards_table', 4)">{t('works_count')}</th>
                                </tr>
                            </thead>
                            <tbody>
                                {grants_analyzed_awards_rows}
                            </tbody>
                        </table>
                    </div>
                    ''' if grants_analyzed_awards else f'<p style="color: #7F8C8D; font-style: italic;">{t("no_grants_data")}</p>'}
                    
                    <hr style="border: none; border-top: 2px solid #e9ecef; margin: 25px 0;">
                    
                    <!-- ============ CITING PUBLICATIONS ============ -->
                    <h3 style="color: {primary}; font-size: 16px;">{t('citing_publications_grants')}</h3>
                    
                    <div class="metrics-grid" style="grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));">
                        <div class="metric-card">
                            <span class="metric-icon">💰</span>
                            <div class="metric-value">{grants_citing_unique_funders}</div>
                            <div class="metric-label">{t('unique_funders_citing')}</div>
                        </div>
                        <div class="metric-card">
                            <span class="metric-icon">🎫</span>
                            <div class="metric-value">{grants_citing_unique_awards}</div>
                            <div class="metric-label">{t('unique_awards_citing')}</div>
                        </div>
                    </div>
                    
                    <h4 style="color: {primary}; margin-top: 15px; font-size: 14px;">{t('top_funders_citing')} <span style="font-weight: 400; font-size: 12px; color: #7F8C8D;">({len(grants_citing_funders)} total)</span></h4>
                    {f'''
                    <div class="scrollable-table" style="max-height: 800px;">
                        <table id="grants_citing_funders_table">
                            <thead>
                                <tr>
                                    <th class="sortable" onclick="sortTable('grants_citing_funders_table', 0)">{t('rank')}</th>
                                    <th class="sortable" onclick="sortTable('grants_citing_funders_table', 1)">{t('funder')}</th>
                                    <th>{t('ror')}</th>
                                    <th class="sortable" onclick="sortTable('grants_citing_funders_table', 3)">{t('works_count')}</th>
                                </tr>
                            </thead>
                            <tbody>
                                {grants_citing_funders_rows}
                            </tbody>
                        </table>
                    </div>
                    ''' if grants_citing_funders else f'<p style="color: #7F8C8D; font-style: italic;">{t("no_grants_data")}</p>'}
                    
                    <h4 style="color: {primary}; margin-top: 15px; font-size: 14px;">{t('top_awards_citing')} <span style="font-weight: 400; font-size: 12px; color: #7F8C8D;">({len(grants_citing_awards)} total)</span></h4>
                    {f'''
                    <div class="scrollable-table" style="max-height: 800px;">
                        <table id="grants_citing_awards_table">
                            <thead>
                                <tr>
                                    <th class="sortable" onclick="sortTable('grants_citing_awards_table', 0)">{t('rank')}</th>
                                    <th class="sortable" onclick="sortTable('grants_citing_awards_table', 1)">{t('funder')}</th>
                                    <th class="sortable" onclick="sortTable('grants_citing_awards_table', 2)">{t('award_id')}</th>
                                    <th>{t('grant')}</th>
                                    <th class="sortable" onclick="sortTable('grants_citing_awards_table', 4)">{t('works_count')}</th>
                                </tr>
                            </thead>
                            <tbody>
                                {grants_citing_awards_rows}
                            </tbody>
                        </table>
                    </div>
                    ''' if grants_citing_awards else f'<p style="color: #7F8C8D; font-style: italic;">{t("no_grants_data")}</p>'}
                    
                </div>
            </div>
            
            <!-- ============================================================ -->
            <!-- SECTION 8: DETAILED CITATIONS -->
            <!-- ============================================================ -->
            <div id="detailed_citations" class="section">
                <div class="section-header" onclick="toggleSection('detailed_content')">
                    <div class="section-title">
                        <span class="icon">📋</span> {t('detailed_citations')}
                        <span class="section-badge">{len(detailed_citations)} {t('publications')}</span>
                    </div>
                    <span class="toggle-indicator" id="detailed_indicator">▼</span>
                </div>
                <div class="section-divider"></div>
                <div id="detailed_content" class="section-content">
                    
                    {''.join([
                        f'''
                        <div class="collapser" onclick="toggleCitations('{html.escape(doi)}')">
                            <strong class="cite-title">{html.escape((data['title'] or 'No title')[:100])}{'...' if len(data['title'] or '') > 100 else ''}</strong>
                            <span class="badge badge-info">{data['year'] or 'N/A'}</span>
                            <span class="citation-count-badge">{data['total_citations']} {t('citations')}</span>
                            <span style="font-size: 12px; color: #999;">DOI: {data['doi'][:20] if data['doi'] else 'N/A'}...</span>
                            <span class="toggle-hint">{t('click_to_toggle')}</span>
                        </div>
                        <div id="citations_{html.escape(doi)}" style="display: none; margin-bottom: 8px;">
                            {''.join([
                                f'''
                                <div class="citation-detail">
                                    <div class="cite-title">{html.escape((cite['citing_title'] or 'No title')[:120])}{'...' if len(cite['citing_title'] or '') > 120 else ''}</div>
                                    <div class="cite-meta">
                                        <strong>{t('citing_journal')}:</strong> {html.escape(cite['citing_journal'] or 'Unknown')} | 
                                        <strong>{t('citing_year')}:</strong> {cite['citing_year'] or 'N/A'} | 
                                        <strong>{t('citing_date')}:</strong> {cite['citing_date'][:10] if cite['citing_date'] else 'N/A'} |
                                        <strong>{t('citation_lag')}:</strong> {cite['citation_lag'] or 'N/A'} {t('days') if cite['citation_lag'] else ''}
                                    </div>
                                    <div class="cite-meta">
                                        <strong>{t('authors')}:</strong> {', '.join([html.escape(a) for a in cite['citing_authors'][:5]]) if cite.get('citing_authors') else 'N/A'}{' +' + str(len(cite['citing_authors'])-5) if cite.get('citing_authors') and len(cite['citing_authors']) > 5 else ''} |
                                        <strong>{t('countries')}:</strong> {', '.join(cite['citing_countries'][:3]) if cite.get('citing_countries') else 'N/A'}
                                    </div>
                                    <div class="cite-meta">
                                        <a href="https://doi.org/{html.escape(cite['citing_doi'] or '')}" target="_blank" class="doi-link">DOI: {html.escape(cite['citing_doi'] or 'N/A')}</a>
                                    </div>
                                </div>
                                ''' for cite in sorted(data['citations'], key=lambda x: x.get('citation_lag') or 0, reverse=True)
                            ])}
                            {f'<div style="padding: 10px 18px; color: #999; font-style: italic;">{t("no_citations_found")}</div>' if not data['citations'] else ''}
                        </div>
                        ''' for doi, data in sorted(
                            detailed_citations.items(),
                            key=lambda kv: (-kv[1].get('total_citations', 0), kv[1].get('year') or 0)
                        )
                    ])}
                    
                </div>
            </div>
            
            <!-- ============================================================ -->
            <!-- SECTION 9: ALL PUBLICATIONS -->
            <!-- ============================================================ -->
            <div id="all_publications" class="section">
                <div class="section-header" onclick="toggleSection('all_content')">
                    <div class="section-title">
                        <span class="icon">📚</span> {t('all_publications')}
                        <span class="section-badge">{len(all_publications)} {t('articles')}</span>
                    </div>
                    <span class="toggle-indicator" id="all_indicator">▼</span>
                </div>
                <div class="section-divider"></div>
                <div id="all_content" class="section-content">
                    
                    <div class="filter-section">
                        <div class="filter-row">
                            <div class="filter-group">
                                <label>🔍</label>
                                <input type="text" id="titleFilter" placeholder="{t('filter_by_title')}..." onkeyup="filterPublications()">
                            </div>
                            <div class="filter-group">
                                <label>📅</label>
                                <select id="yearFilter" onchange="filterPublications()">
                                    <option value="">{t('all_years')}</option>
                                    {''.join([
                                        f'<option value="{year}">{year}</option>'
                                        for year in sorted(set([p.get('year') for p in all_publications if p.get('year')]), reverse=True)
                                    ])}
                                </select>
                            </div>
                            <div class="filter-group">
                                <label>👤</label>
                                <input type="text" id="authorFilter" placeholder="{t('filter_by_author')}..." onkeyup="filterPublications()">
                            </div>
                            <div class="filter-group">
                                <label>🏛️</label>
                                <input type="text" id="affiliationFilter" placeholder="{t('filter_by_affiliation')}..." onkeyup="filterPublications()">
                            </div>
                            <div class="filter-group">
                                <label>📊</label>
                                <input type="number" id="citationFilter" placeholder="{t('filter_by_citations')}..." min="0" onchange="filterPublications()">
                            </div>
                        </div>
                        <div class="filter-stats">
                            <span id="visibleCount">{t('visible_count', shown=len(all_publications), total=len(all_publications))}</span>
                        </div>
                    </div>
                    
                    <div class="scrollable-table" style="max-height: 600px;">
                        <table id="publicationsTable">
                            <thead>
                                <tr>
                                    <th class="sortable" onclick="sortTable('publicationsTable', 0)">#</th>
                                    <th class="sortable" onclick="sortTable('publicationsTable', 1)">{t('title')}</th>
                                    <th class="sortable" onclick="sortTable('publicationsTable', 2)">{t('year')}</th>
                                    <th class="sortable" onclick="sortTable('publicationsTable', 3)">{t('authors')}</th>
                                    <th class="sortable" onclick="sortTable('publicationsTable', 4)">{t('affiliations')}</th>
                                    <th class="sortable" onclick="sortTable('publicationsTable', 5)">{t('citations')}</th>
                                    <th class="sortable" onclick="sortTable('publicationsTable', 6)">{t('citations_per_year_label')}</th>
                                    <th>{t('grants_funding')}</th>
                                    <th>DOI</th>
                                </tr>
                            </thead>
                            <tbody>
                                {all_publications_rows}
                            </tbody>
                        </table>
                    </div>
                    
                </div>
            </div>
            
            <!-- ============================================================ -->
            <!-- FOOTER -->
            <!-- ============================================================ -->
            <div class="footer">
                <p>{t('footer')}</p>
                <p> {t('generated_on')}: {datetime.now().strftime('%d.%m.%Y %H:%M')}</p>
                <p><a href="{t('journal_url')}" target="_blank">{t('journal_url')}</a></p>
            </div>
            
        </div>
    </div>
    
    <script>
        // ===== TOGGLE SECTIONS =====
        function toggleSection(sectionId) {{
            var content = document.getElementById(sectionId);
            var indicator = document.getElementById(sectionId.replace('_content', '_indicator'));
            if (content) {{
                if (content.style.display === 'none' || content.style.display === '') {{
                    content.style.display = 'block';
                    if (indicator) indicator.textContent = '▼';
                    content.style.animation = 'fadeInUp 0.4s ease forwards';
                }} else {{
                    content.style.display = 'none';
                    if (indicator) indicator.textContent = '▶';
                }}
            }}
        }}
        
        // ===== TOGGLE CITATIONS =====
        function toggleCitations(id) {{
            var el = document.getElementById('citations_' + id);
            if (el) {{
                if (el.style.display === 'none' || el.style.display === '') {{
                    el.style.display = 'block';
                    el.scrollIntoView({{ behavior: 'smooth', block: 'nearest' }});
                }} else {{
                    el.style.display = 'none';
                }}
            }}
        }}
        
        // ===== FILTER PUBLICATIONS =====
        function filterPublications() {{
            var titleFilter = document.getElementById('titleFilter').value.toLowerCase();
            var yearFilter = document.getElementById('yearFilter').value;
            var authorFilter = document.getElementById('authorFilter').value.toLowerCase();
            var affiliationFilter = document.getElementById('affiliationFilter').value.toLowerCase();
            var citationFilter = parseInt(document.getElementById('citationFilter').value) || 0;
            
            var rows = document.querySelectorAll('#publicationsTable tbody tr');
            var visible = 0;
            
            rows.forEach(function(row) {{
                var title = row.getAttribute('data-title') || '';
                var year = row.getAttribute('data-year') || '';
                var authors = row.getAttribute('data-authors') || '';
                var affiliations = row.getAttribute('data-affiliations') || '';
                var citations = parseInt(row.getAttribute('data-citations')) || 0;
                
                var show = true;
                
                if (titleFilter && !title.includes(titleFilter)) show = false;
                if (yearFilter && year !== yearFilter) show = false;
                if (authorFilter && !authors.toLowerCase().includes(authorFilter)) show = false;
                if (affiliationFilter && !affiliations.toLowerCase().includes(affiliationFilter)) show = false;
                if (citationFilter > 0 && citations < citationFilter) show = false;
                
                row.style.display = show ? '' : 'none';
                if (show) visible++;
            }});
            
            document.getElementById('visibleCount').textContent = 
                'Showing ' + visible + ' of ' + rows.length + ' publications';
        }}
        
        // ===== FILTER CITED PUBLICATIONS =====
        function filterCited() {{
            var titleFilter = (document.getElementById('citedTitleFilter').value || '').toLowerCase();
            var yearFilter = document.getElementById('citedYearFilter').value;
            var authorFilter = (document.getElementById('citedAuthorFilter').value || '').toLowerCase();
            var affiliationFilter = (document.getElementById('citedAffiliationFilter').value || '').toLowerCase();
            var journalFilter = (document.getElementById('citedJournalFilter').value || '').toLowerCase();
            var publisherFilter = (document.getElementById('citedPublisherFilter').value || '').toLowerCase();
            var citationFilter = parseInt(document.getElementById('citedCitationFilter').value) || 0;
            
            var rows = document.querySelectorAll('#citedTable tbody tr');
            var visible = 0;
            
            rows.forEach(function(row) {{
                var title = row.getAttribute('data-title') || '';
                var year = row.getAttribute('data-year') || '';
                var authors = row.getAttribute('data-authors') || '';
                var affiliations = row.getAttribute('data-affiliations') || '';
                var journal = row.getAttribute('data-journal') || '';
                var publisher = row.getAttribute('data-publisher') || '';
                var citations = parseInt(row.getAttribute('data-citations')) || 0;
                
                var show = true;
                
                if (titleFilter && !title.includes(titleFilter)) show = false;
                if (yearFilter && year !== yearFilter) show = false;
                if (authorFilter && !authors.toLowerCase().includes(authorFilter)) show = false;
                if (affiliationFilter && !affiliations.toLowerCase().includes(affiliationFilter)) show = false;
                if (journalFilter && !journal.includes(journalFilter)) show = false;
                if (publisherFilter && !publisher.includes(publisherFilter)) show = false;
                if (citationFilter > 0 && citations < citationFilter) show = false;
                
                row.style.display = show ? '' : 'none';
                if (show) visible++;
            }});
            
            document.getElementById('citedVisibleCount').textContent = 
                'Showing ' + visible + ' of ' + rows.length + ' publications';
        }}
        
        // ===== UNIVERSAL SORT FUNCTION =====
        function sortTable(tableId, colIndex) {{
            var table = document.getElementById(tableId);
            if (!table) return;
            var tbody = table.querySelector('tbody');
            if (!tbody) return;
            var rows = Array.from(tbody.querySelectorAll('tr'));
            
            // Determine sort direction
            var key = tableId + '_col_' + colIndex;
            if (!window.sortState) window.sortState = {{}};
            if (!window.sortState[key]) window.sortState[key] = 1;
            else window.sortState[key] *= -1;
            var direction = window.sortState[key];
            
            // Update header indicators
            var headers = table.querySelectorAll('thead th');
            headers.forEach(function(th, idx) {{
                th.classList.remove('asc', 'desc');
                if (idx === colIndex) {{
                    th.classList.add(direction > 0 ? 'asc' : 'desc');
                }}
            }});
            
            rows.sort(function(a, b) {{
                var valA = a.cells[colIndex] ? a.cells[colIndex].textContent.trim() : '';
                var valB = b.cells[colIndex] ? b.cells[colIndex].textContent.trim() : '';
                
                // Try parsing as number
                var numA = parseFloat(valA.replace(/,/g, ''));
                var numB = parseFloat(valB.replace(/,/g, ''));
                if (!isNaN(numA) && !isNaN(numB)) {{
                    return (numA - numB) * direction;
                }}
                
                // Try parsing as date
                var dateA = new Date(valA);
                var dateB = new Date(valB);
                if (!isNaN(dateA) && !isNaN(dateB)) {{
                    return (dateA - dateB) * direction;
                }}
                
                // String comparison
                return valA.localeCompare(valB) * direction;
            }});
            
            // Re-append rows
            rows.forEach(function(row) {{
                tbody.appendChild(row);
            }});
        }}
        
        // ===== AUTO-OPEN FIRST SECTION =====
        document.addEventListener('DOMContentLoaded', function() {{
            // Overview section is open by default, others closed
            var sections = ['analyzed_content', 'citation_content', 'cited_content', 'citing_content', 'topics_content', 'grants_content', 'detailed_content', 'all_content'];
            sections.forEach(function(id) {{
                var el = document.getElementById(id);
                if (el) {{
                    el.style.display = 'none';
                }}
            }});
            var indicators = ['analyzed_indicator', 'citation_indicator', 'cited_indicator', 'citing_indicator', 'topics_indicator', 'grants_indicator', 'detailed_indicator', 'all_indicator'];
            indicators.forEach(function(id) {{
                var el = document.getElementById(id);
                if (el) {{
                    el.textContent = '▶';
                }}
            }});
        }});
    </script>
    
    </body>
    </html>
    """
    
    return html_content

# ============================================
# ОСНОВНАЯ ФУНКЦИЯ ЗАПУСКА ДЛЯ STREAMLIT
# ============================================

def run_journal_analysis(issn: str, period: str, max_workers: int = 6, journal_logo: Optional[Dict] = None):
    """Run complete journal analysis and save results to session state"""
    
    current_lang = st.session_state.get('language', 'en')
    def t(key: str, **kwargs) -> str:
        return translate(key, current_lang, **kwargs)
    
    if not issn or not period:
        st.error(t('no_issn') if not issn else t('no_period'))
        return
    
    st.cache_data.clear()
    
    st.info(f"🔍 {t('stage_fetch_publications')}")
    
    progress_container = st.empty()
    status_container = st.empty()
    analysis_progress = st.progress(0, text=t('starting_analysis'))
    
    try:
        # Load app logo
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
                    break
            except Exception as e:
                st.warning(f"⚠️ Ошибка загрузки логотипа журнала: {e}")
        
        # Stage weights
        stage_weights = {
            'fetch_publications': 0.15,
            'fetch_citing': 0.20,
            'fetch_pub_metadata': 0.20,
            'fetch_cite_metadata': 0.25,
            'analyze_report': 0.20
        }
        
        # Initialize analyzer
        analyzer = JournalAnalyzer(issn, period, max_workers)
        
        # Get journal info
        journal_name, journal_abbr = analyzer.get_journal_info()
        
        # Stage 1: Fetch publications
        status_container.info(f"📡 {t('stage_fetch_publications')}")
        analysis_progress.progress(0.01, text=t('stage_fetch_publications'))
        
        def pub_progress(current, total):
            progress = 0.01 + (current / total) * stage_weights['fetch_publications']
            analysis_progress.progress(progress, text=f"{t('stage_fetch_publications')} - {t('stage_processing', current=current, total=total)}")
            status_container.info(f"📡 {t('stage_fetch_publications')} - {t('stage_processing', current=current, total=total)}")
        
        publications = analyzer.fetch_journal_publications(pub_progress)
        
        if not publications:
            st.error(f"❌ {t('data_not_found')}")
            analysis_progress.empty()
            return
        
        st.success(f"✅ {t('stage_publications_found', count=len(publications))}")
        
        # Stage 2: Fetch citing works
        status_container.info(f"📡 {t('stage_fetch_citing')}")
        progress_base = stage_weights['fetch_publications']
        analysis_progress.progress(progress_base, text=t('stage_fetch_citing'))
        
        def cite_progress(current, total):
            progress = progress_base + (current / total) * stage_weights['fetch_citing']
            analysis_progress.progress(progress, text=f"{t('stage_fetch_citing')} - {t('stage_processing', current=current, total=total)}")
            status_container.info(f"📡 {t('stage_fetch_citing')} - {t('stage_processing', current=current, total=total)}")
        
        citing_works = analyzer.fetch_citing_works(cite_progress)
        total_citing = sum(len(v) for v in citing_works.values())
        st.success(f"✅ {t('stage_citing_found', count=total_citing)}")
        
        # Stage 3: Fetch publication metadata
        status_container.info(f"📡 {t('stage_fetch_pub_metadata')}")
        progress_base += stage_weights['fetch_citing']
        analysis_progress.progress(progress_base, text=t('stage_fetch_pub_metadata'))
        
        def pub_meta_progress(current, total):
            progress = progress_base + (current / total) * stage_weights['fetch_pub_metadata']
            analysis_progress.progress(progress, text=f"{t('stage_fetch_pub_metadata')} - {t('stage_processing', current=current, total=total)}")
            status_container.info(f"📡 {t('stage_fetch_pub_metadata')} - {t('stage_processing', current=current, total=total)}")
        
        pub_metadata = analyzer.fetch_publications_metadata(pub_meta_progress)
        st.success(f"✅ {t('stage_metadata_fetched', count=len(pub_metadata))}")
        
        # Stage 4: Fetch citations metadata
        status_container.info(f"📡 {t('stage_fetch_cite_metadata')}")
        progress_base += stage_weights['fetch_pub_metadata']
        analysis_progress.progress(progress_base, text=t('stage_fetch_cite_metadata'))
        
        def cite_meta_progress(current, total):
            progress = progress_base + (current / total) * stage_weights['fetch_cite_metadata']
            analysis_progress.progress(progress, text=f"{t('stage_fetch_cite_metadata')} - {t('stage_processing', current=current, total=total)}")
            status_container.info(f"📡 {t('stage_fetch_cite_metadata')} - {t('stage_processing', current=current, total=total)}")
        
        cite_metadata = analyzer.fetch_citations_metadata(cite_meta_progress)
        st.success(f"✅ {t('stage_metadata_fetched', count=len(cite_metadata))}")
        
        # Stage 5: Analyze and generate report
        status_container.info(f"📡 {t('stage_analyze_report')}")
        progress_base += stage_weights['fetch_cite_metadata']
        analysis_progress.progress(progress_base, text=t('stage_analyze_report'))
        
        def analyze_progress(current, total):
            progress = progress_base + (current / total) * stage_weights['analyze_report']
            analysis_progress.progress(progress, text=f"{t('stage_analyze_report')} - {t('stage_processing', current=current, total=total)}")
            status_container.info(f"📡 {t('stage_analyze_report')} - {t('stage_processing', current=current, total=total)}")
        
        results = analyzer.analyze_data(analyze_progress)
        
        # ====== СОХРАНЯЕМ ВСЕ ДАННЫЕ В SESSION_STATE ======
        st.session_state['analyzer'] = analyzer
        st.session_state['results'] = results
        st.session_state['publications'] = publications
        st.session_state['citing_works'] = citing_works
        st.session_state['journal_logo_base64'] = journal_logo_base64
        st.session_state['app_logo_base64'] = app_logo_base64
        st.session_state['analysis_complete'] = True
        st.session_state['issn'] = issn
        st.session_state['period'] = period
        st.session_state['max_workers'] = max_workers
        st.session_state['journal_name'] = journal_name
        st.session_state['journal_abbreviation'] = journal_abbr
        
        analysis_progress.progress(1.0, text=f"✅ {t('analysis_complete_text')}!")
        
        st.success(t('analysis_complete', count=len(publications), time=0))
        st.balloons()
        
        # ====== ПОКАЗЫВАЕМ ОТЧЕТ ИЗ SESSION_STATE ======
        st.markdown("---")
        st.markdown(f"## {t('html_report')}")
        
        theme_colors = {
            'primary': st.session_state.primary_color,
            'secondary': st.session_state.secondary_color
        }
        
        # Генерируем отчет из session_state (без повторного анализа)
        with st.spinner(t('generating_report')):
            html_report = generate_journal_html_report(
                st.session_state.analyzer,
                st.session_state.journal_logo_base64,
                st.session_state.app_logo_base64,
                theme_colors,
                current_lang
            )
        
        # Кнопка скачивания
        filename = f"journal_analysis_{st.session_state.journal_abbreviation or st.session_state.issn}_{datetime.now().strftime('%Y%m%d')}.html"
        st.download_button(
            label="📥 " + t('download_report'),
            data=html_report.encode('utf-8'),
            file_name=filename,
            mime="text/html",
            type="primary",
            width='stretch'
        )
        
        # Предпросмотр
        st.markdown("---")
        st.markdown(f"### {t('report_preview')}")
        st.info(t('download_hint'))
        st.components.v1.html(html_report, height=800, scrolling=True)
        
        # Кнопка сброса
        if st.button("🔄 " + t('reset_analysis'), type="secondary"):
            for key in ['analyzer', 'results', 'publications', 'citing_works', 'analysis_complete', 'issn', 'period', 'max_workers', 'journal_name', 'journal_abbreviation']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
        
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
    if 'analyzer' not in st.session_state:
        st.session_state.analyzer = None
    if 'results' not in st.session_state:
        st.session_state.results = None
    if 'publications' not in st.session_state:
        st.session_state.publications = []
    if 'citing_works' not in st.session_state:
        st.session_state.citing_works = {}
    if 'journal_logo_base64' not in st.session_state:
        st.session_state.journal_logo_base64 = None
    if 'app_logo_base64' not in st.session_state:
        st.session_state.app_logo_base64 = None
    if 'issn' not in st.session_state:
        st.session_state.issn = ''
    if 'period' not in st.session_state:
        st.session_state.period = ''
    if 'max_workers' not in st.session_state:
        st.session_state.max_workers = 6
    if 'journal_name' not in st.session_state:
        st.session_state.journal_name = ''
    if 'journal_abbreviation' not in st.session_state:
        st.session_state.journal_abbreviation = ''
    
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
        
        # ==== OpenAlex API key status ====
        if OPENALEX_API_KEY:
            st.success("🔑 OpenAlex API key loaded")
        else:
            st.warning("🔑 OpenAlex API key not configured (using free tier)")
        # =================================
        
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
        
        use_preset = st.checkbox(t('use_preset'), value=False)
        
        if use_preset:
            selected_theme = preset_themes[theme_option]
            st.session_state.primary_color = selected_theme["primary"]
            st.session_state.secondary_color = selected_theme["secondary"]
        else:
            col_p1, col_p2 = st.columns(2)
            with col_p1:
                st.session_state.primary_color = st.color_picker(
                    t('select_color'),
                    value=st.session_state.primary_color
                )
            with col_p2:
                st.session_state.secondary_color = st.color_picker(
                    t('select_secondary_color'),
                    value=st.session_state.secondary_color
                )
        
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
            if os.path.exists('cache_journal'):
                shutil.rmtree('cache_journal')
                st.cache_data.clear()
                st.success(t('cache_cleared'))
        
        st.markdown("---")
        
        st.markdown(f"""
        <div style="font-size: 11px; color: #666; text-align: center;">
            © daM / Chimica Techno Acta / {t('journal_url')}
        </div>
        """, unsafe_allow_html=True)
    
    # Main area - only logo
    if os.path.exists("logo.png"):
        col_logo, col_spacer = st.columns([1, 3])
        with col_logo:
            st.image("logo.png", width=400)
    st.markdown("---")
    
    # ====== ПРОВЕРКА: ЕСТЬ ЛИ ДАННЫЕ В SESSION_STATE ======
    if st.session_state.analysis_complete and st.session_state.analyzer:
        st.info(f"📦 {t('analysis_data_from_cache')}")
        st.markdown(f"**{t('journal_issn_label', issn=st.session_state.issn)}** | **{t('analysis_period_label', period=st.session_state.period)}**")
        if st.session_state.journal_name:
            st.markdown(f"**Journal:** {st.session_state.journal_name} ({st.session_state.journal_abbreviation})")
        
        # Кнопка для сброса
        col1, col2 = st.columns([4, 1])
        with col2:
            if st.button("🗑️ " + t('reset_analysis'), type="secondary"):
                for key in ['analyzer', 'results', 'publications', 'citing_works', 'analysis_complete', 'issn', 'period', 'max_workers', 'journal_name', 'journal_abbreviation']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()
        
        st.markdown("---")
        
        # Показываем отчет из session_state
        st.markdown(f"## {t('html_report')}")
        
        theme_colors = {
            'primary': st.session_state.primary_color,
            'secondary': st.session_state.secondary_color
        }
        
        with st.spinner(t('generating_report')):
            html_report = generate_journal_html_report(
                st.session_state.analyzer,
                st.session_state.journal_logo_base64,
                st.session_state.app_logo_base64,
                theme_colors,
                current_lang
            )
        
        filename = f"journal_analysis_{st.session_state.journal_abbreviation or st.session_state.issn}_{datetime.now().strftime('%Y%m%d')}.html"
        st.download_button(
            label="📥 " + t('download_report'),
            data=html_report.encode('utf-8'),
            file_name=filename,
            mime="text/html",
            type="primary",
            width='stretch'
        )
        
        st.markdown("---")
        st.markdown(f"### {t('report_preview')}")
        st.info(t('download_hint'))
        st.components.v1.html(html_report, height=800, scrolling=True)
        
    else:
        # Input section for new analysis
        st.markdown(f"## {t('load_data')}")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            issn_input = st.text_input(
                t('journal_issn'),
                placeholder=t('issn_placeholder'),
                help=t('issn_help')
            )
        
        with col2:
            period_input = st.text_input(
                t('period_input'),
                placeholder=t('period_placeholder'),
                help=t('period_help')
            )
        
        col3, col4, col5 = st.columns([1, 1, 1])
        
        with col3:
            workers = st.slider(
                t('workers'),
                min_value=4,
                max_value=10,
                value=6,
                step=1,
                help=t('workers_help')
            )
        
        with col4:
            journal_logo_upload = st.file_uploader(
                t('upload_logo'),
                type=['png', 'jpg', 'jpeg', 'svg'],
                help=t('logo_help')
            )
        
        with col5:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button(t('analyze_button'), type="primary", width='stretch'):
                journal_logo_data = None
                if journal_logo_upload:
                    journal_logo_data = {
                        journal_logo_upload.name: {
                            'content': journal_logo_upload.read()
                        }
                    }
                
                run_journal_analysis(issn_input, period_input, workers, journal_logo_data)

if __name__ == "__main__":
    main()
