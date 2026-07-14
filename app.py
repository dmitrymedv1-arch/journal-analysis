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
import random
from threading import Lock
from dataclasses import dataclass, field
from typing import Optional

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
        'profile': 'Scholar Profile',
        'reports': '📄 Reports',
        'orcid_input': 'Author ORCID(s)',
        'orcid_placeholder': '0000-0002-1234-567X\n0000-0002-5678-9012\nor: 0000-0002-1234-567X, 0000-0002-5678-9012\nor: https://orcid.org/0000-0002-1234-567X',
        'orcid_help': 'Enter one or more ORCIDs. Separators: comma, space, new line',
        'upload_logo': 'Upload journal logo (optional)',
        'logo_help': 'Logo will be displayed in reports',
        'show_all_authors': '👥 Show data for all co-authors',
        'show_all_help': 'When enabled, shows information about all authors sorted by h-index',
        'analyze_button': '🔍 Analyze profile(s)',
        'no_orcid': '⚠️ Enter at least one ORCID',
        'too_many_orcids': '⚠️ Found {count} ORCIDs. This may take a long time...',
        'analysis_complete': '✅ Analysis complete! Found {count} authors in {time:.1f} sec.',
        'best_author': '🏆 Best author: {name} (h-index: {h_index})',
        'single_author': '👤 Author: {name} (h-index: {h_index})',
        'showing_all': '👥 Showing all {count} authors (sorted by h-index)',
        'showing_single': '👤 Showing only the best author',
        'showing_single_only': '👤 Showing single author',
        'no_data': '👈 Load data in "Load Data" tab and click "Analyze profile(s)"',
        'no_data_reports': '👈 First run analysis in "Load Data" tab',
        'retraction_warning': '⚠️ ATTENTION: This author has {count} retracted publication(s).',
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
        # NEW KEYS FOR JOURNAL ANALYSIS
        'journal_analysis': 'Journal Analysis',
        'issn': 'ISSN',
        'period': 'Period',
        'analyze_journal': '🔍 Analyze Journal',
        'stage_1': 'Collecting journal articles...',
        'stage_2': 'Collecting citing works...',
        'stage_3': 'Fetching article metadata...',
        'stage_4': 'Fetching citing works metadata...',
        'stage_5': 'Analyzing and generating report...',
        'processed': 'Processed',
        'citing_works': 'citing works',
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
        'unknown_oa': 'Unknown',
        'rank': 'Rank',
        'author': 'Author',
        'authors': 'Authors',
        'orcid': 'ORCID',
        'affiliations': 'Affiliations',
        'countries': 'Countries',
        'publications': 'Publications',
        'citations': 'Citations',
        'citations_per_year': 'Citations/Year',
        'publication_year': 'Publication Year',
        'citation_year': 'Citation Year',
        'citations_count': 'Citations Count',
        'collaboration_couples': 'Collaboration Couples',
        'single_country': 'Single-Country',
        'international_collab': 'International',
        'top_citing_authors': 'Top Citing Authors',
        'top_citing_affiliations': 'Top Citing Affiliations',
        'top_citing_countries': 'Top Citing Countries',
        'top_citing_journals': 'Top Citing Journals',
        'top_citing_publishers': 'Top Citing Publishers',
        'topic_analysis': 'Topic Analysis',
        'topics': 'Topics',
        'subtopics': 'Subtopics',
        'fields': 'Fields',
        'domains': 'Domains',
        'concepts': 'Concepts',
        'analyzed_count': 'Analyzed Count',
        'citing_count': 'Citing Count',
        'analyzed_norm_count': 'Analyzed Norm Count',
        'citing_norm_count': 'Citing Norm Count',
        'total_norm_count': 'Total Norm Count',
        'first_year': 'First Year',
        'peak_year': 'Peak Year',
        'first_citation_analysis': 'First Citation Analysis',
        'min_lag': 'Min Lag',
        'max_lag': 'Max Lag',
        'avg_lag': 'Avg Lag',
        'median_lag': 'Median Lag',
        'detailed_citations': 'Detailed Citations',
        'all_publications': 'All Publications',
        'filter_by_year': 'Filter by Year',
        'filter_by_author': 'Filter by Author',
        'filter_by_affiliations': 'Filter by Affiliations',
        'filter_by_citations_min': 'Filter by Citations (min)',
        'search_publications': 'Search Publications',
        'filter_by_title': 'Filter by Title Word(s)',
        'show_citations': 'Show Citations',
        'citing_journal': 'Citing Journal',
        'citing_year': 'Citing Year',
        'citing_date': 'Citing Date',
        'citation_lag': 'Citation Lag',
        'all_years': 'All Years',
        'download_html_report': 'Download HTML Report',
        'generating_report': 'Generating HTML report...',
        'report_preview': 'HTML Report Preview',
        'download_hint': 'Click "Download HTML Report" for full report',
        'journal_not_found': 'Journal not found or no articles in selected period',
        'invalid_issn': 'Invalid ISSN format. Use XXXX-XXXX',
        'invalid_period': 'Invalid period format. Use YYYY or YYYY-YYYY or YYYY,YYYY',
        'stage_1_desc': 'Fetching articles published in the journal during selected period',
        'stage_2_desc': 'Collecting all works that cite these articles',
        'stage_3_desc': 'Retrieving detailed metadata for analyzed articles',
        'stage_4_desc': 'Retrieving detailed metadata for citing works',
        'stage_5_desc': 'Calculating metrics and generating report',
        'overview': 'Overview',
        'analyzed_articles': 'Analyzed Articles',
        'citation_analysis': 'Citation Analysis',
        'citing_works_analysis': 'Citing Works Analysis',
        'topic_analysis_section': 'Topics Analysis',
        'detailed_citations_section': 'Detailed Citations',
        'all_publications_section': 'All Publications',
        'author_analysis': 'Author Analysis',
        'top_affiliations': 'Top Affiliations',
        'geographic_analysis': 'Geographic Analysis',
        'unique_countries_per_publication': 'Unique Countries per Publication',
        'authors_per_country': 'Authors per Country',
        'collaboration_patterns': 'Collaboration Patterns',
        'collaboration_couples_section': 'Collaboration Couples',
        'citation_dynamics_by_year': 'Citation Dynamics by Year',
        'cumulative_citations': 'Cumulative Citations',
        'citation_network_heatmap': 'Citation Network Heatmap',
        'most_cited_publications': 'Most Cited Publications',
        'total_citing_works': 'Total Citing Works',
        'stage': 'Stage',
        'articles_collected': 'articles collected',
        'citing_works_collected': 'citing works collected',
        'metadata_fetched': 'metadata entries fetched',
        'analysis_complete_label': 'Analysis Complete!',
        'generating_report_label': 'Generating HTML report...',
        'report_ready': 'Report is ready!',
        'click_to_download': 'Click "Download HTML Report" to save',
        'journal_analysis_title': 'Advanced Journal Analysis Tool',
        'enter_issn': 'Enter journal ISSN',
        'enter_period': 'Enter period (e.g., 2020-2023)',
        'total_publications_label': 'Total Publications',
        'total_citations_label': 'Total Citations',
        'h_index_label': 'h-index',
        'g_index_label': 'g-index',
        'i10_index_label': 'i10-index',
        'i100_index_label': 'i100-index',
        'avg_citations_label': 'Avg Citations',
        'open_access_label': 'Open Access',
        'active_years_label': 'Active Years',
        'unique_authors_label': 'Unique Authors',
        'unique_affiliations_label': 'Unique Affiliations',
        'unique_countries_label': 'Unique Countries',
        'avg_authors_per_paper_label': 'Avg Authors/Paper',
        'avg_affiliations_per_paper_label': 'Avg Affiliations/Paper',
        'avg_countries_per_paper_label': 'Avg Countries/Paper',
        'international_collaboration_rate_label': 'International Collaboration Rate',
        'unique_citing_authors_label': 'Unique Citing Authors',
        'unique_citing_affiliations_label': 'Unique Citing Affiliations',
        'unique_citing_countries_label': 'Unique Citing Countries',
        'unique_citing_journals_label': 'Unique Citing Journals',
        'unique_citing_publishers_label': 'Unique Citing Publishers',
        'open_access_breakdown': 'Open Access Breakdown',
        'top_30_authors': 'Top 30 Authors',
        'top_30_affiliations': 'Top 30 Affiliations',
        'collaboration_level': 'Collaboration Level',
        'individual_distribution': 'Individual Distribution',
        'country_pairs': 'Country Pairs',
        'frequency': 'Frequency',
        'publication_year_col': 'Publication Year',
        'citation_year_col': 'Citation Year',
        'citations_count_col': 'Citations Count',
        'first_citation_stats': 'First Citation Statistics',
        'min': 'Min',
        'max': 'Max',
        'average': 'Average',
        'median': 'Median',
        'years': 'years',
        'cumulative': 'Cumulative',
        'publication_title': 'Publication Title',
        'citing_works_total': 'Total Citing Works',
        'topic_trends': 'Topic Trends',
        'top_10_cited': 'Top 10 Most Cited',
        'analyzed_work': 'Analyzed Work',
        'citations_list': 'Citations List',
        'showing_all_publications': 'Showing all publications',
        'filtered_count': 'Filtered: {count} publications',
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
        'analysis_params': '📊 Параметры анализа',
        'use_cache': '💾 Использовать кэш',
        'clear_cache': '🗑️ Очистить кэш',
        'cache_cleared': '✅ Кэш очищен!',
        'load_data': '📥 Загрузка данных',
        'profile': 'Профиль ученого',
        'reports': '📄 Отчеты',
        'orcid_input': 'ORCID автора(ов)',
        'orcid_placeholder': '0000-0002-1234-567X\n0000-0002-5678-9012\nили: 0000-0002-1234-567X, 0000-0002-5678-9012\nили: https://orcid.org/0000-0002-1234-567X',
        'orcid_help': 'Введите один или несколько ORCID. Разделители: запятая, пробел, новая строка',
        'upload_logo': 'Загрузить логотип журнала (опционально)',
        'logo_help': 'Логотип будет отображаться в отчетах',
        'show_all_authors': '👥 Показать всех соавторов',
        'show_all_help': 'При включении показывает информацию о всех авторах, отсортированных по h-index',
        'analyze_button': '🔍 Анализировать профиль(и)',
        'no_orcid': '⚠️ Введите хотя бы один ORCID',
        'too_many_orcids': '⚠️ Найдено {count} ORCID. Это может занять много времени...',
        'analysis_complete': '✅ Анализ завершен! Найдено {count} авторов за {time:.1f} сек.',
        'best_author': '🏆 Лучший автор: {name} (h-index: {h_index})',
        'single_author': '👤 Автор: {name} (h-index: {h_index})',
        'showing_all': '👥 Показаны все {count} авторов (сортировка по h-index)',
        'showing_single': '👤 Показан только лучший автор',
        'showing_single_only': '👤 Показан единственный автор',
        'no_data': '👈 Загрузите данные на вкладке "Загрузка данных" и нажмите "Анализировать профиль(и)"',
        'no_data_reports': '👈 Сначала выполните анализ на вкладке "Загрузка данных"',
        'retraction_warning': '⚠️ ВНИМАНИЕ: У автора {count} ретрагированных публикаций.',
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
        # NEW KEYS FOR JOURNAL ANALYSIS
        'journal_analysis': 'Анализ журнала',
        'issn': 'ISSN',
        'period': 'Период',
        'analyze_journal': '🔍 Анализировать журнал',
        'stage_1': 'Сбор статей журнала...',
        'stage_2': 'Сбор цитирующих работ...',
        'stage_3': 'Получение метаданных статей...',
        'stage_4': 'Получение метаданных цитирующих работ...',
        'stage_5': 'Анализ и генерация отчета...',
        'processed': 'Обработано',
        'citing_works': 'цитирующих работ',
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
        'unique_citing_publishers': 'Уникальных цитирующих издателей',
        'gold': 'Золотой',
        'hybrid': 'Гибридный',
        'green': 'Зеленый',
        'bronze': 'Бронзовый',
        'closed': 'Закрытый',
        'unknown_oa': 'Неизвестно',
        'rank': 'Рейтинг',
        'author': 'Автор',
        'authors': 'Авторы',
        'orcid': 'ORCID',
        'affiliations': 'Аффилиации',
        'countries': 'Страны',
        'publications': 'Публикации',
        'citations': 'Цитирования',
        'citations_per_year': 'Цитирований/год',
        'publication_year': 'Год публикации',
        'citation_year': 'Год цитирования',
        'citations_count': 'Количество цитирований',
        'collaboration_couples': 'Пары стран-коллабораций',
        'single_country': 'Внутристрановые',
        'international_collab': 'Международные',
        'top_citing_authors': 'Топ цитирующих авторов',
        'top_citing_affiliations': 'Топ цитирующих аффилиаций',
        'top_citing_countries': 'Топ цитирующих стран',
        'top_citing_journals': 'Топ цитирующих журналов',
        'top_citing_publishers': 'Топ цитирующих издателей',
        'topic_analysis': 'Анализ тем',
        'topics': 'Темы',
        'subtopics': 'Подтемы',
        'fields': 'Области',
        'domains': 'Домены',
        'concepts': 'Концепты',
        'analyzed_count': 'Анализируемое кол-во',
        'citing_count': 'Цитирующее кол-во',
        'analyzed_norm_count': 'Норм. анализируемое',
        'citing_norm_count': 'Норм. цитирующее',
        'total_norm_count': 'Общее норм. кол-во',
        'first_year': 'Первый год',
        'peak_year': 'Пиковый год',
        'first_citation_analysis': 'Анализ первого цитирования',
        'min_lag': 'Мин. задержка',
        'max_lag': 'Макс. задержка',
        'avg_lag': 'Сред. задержка',
        'median_lag': 'Мед. задержка',
        'detailed_citations': 'Детальные цитирования',
        'all_publications': 'Все публикации',
        'filter_by_year': 'Фильтр по году',
        'filter_by_author': 'Фильтр по автору',
        'filter_by_affiliations': 'Фильтр по аффилиации',
        'filter_by_citations_min': 'Фильтр по цитированиям (мин)',
        'search_publications': 'Поиск публикаций',
        'filter_by_title': 'Фильтр по словам в названии',
        'show_citations': 'Показать цитирования',
        'citing_journal': 'Цитирующий журнал',
        'citing_year': 'Год цитирования',
        'citing_date': 'Дата цитирования',
        'citation_lag': 'Задержка цитирования',
        'all_years': 'Все годы',
        'download_html_report': 'Скачать HTML отчет',
        'generating_report': 'Генерация HTML отчета...',
        'report_preview': 'Предпросмотр HTML отчета',
        'download_hint': 'Нажмите "Скачать HTML отчет" для полного отчета',
        'journal_not_found': 'Журнал не найден или нет статей в выбранный период',
        'invalid_issn': 'Неверный формат ISSN. Используйте XXXX-XXXX',
        'invalid_period': 'Неверный формат периода. Используйте YYYY или YYYY-YYYY или YYYY,YYYY',
        'stage_1_desc': 'Получение статей, опубликованных в журнале за выбранный период',
        'stage_2_desc': 'Сбор всех работ, цитирующих эти статьи',
        'stage_3_desc': 'Получение детальной метаданных для анализируемых статей',
        'stage_4_desc': 'Получение детальной метаданных для цитирующих работ',
        'stage_5_desc': 'Расчет метрик и генерация отчета',
        'overview': 'Обзор',
        'analyzed_articles': 'Анализируемые статьи',
        'citation_analysis': 'Анализ цитирований',
        'citing_works_analysis': 'Анализ цитирующих работ',
        'topic_analysis_section': 'Анализ тем',
        'detailed_citations_section': 'Детальные цитирования',
        'all_publications_section': 'Все публикации',
        'author_analysis': 'Анализ авторов',
        'top_affiliations': 'Топ аффилиаций',
        'geographic_analysis': 'Географический анализ',
        'unique_countries_per_publication': 'Уникальные страны на публикацию',
        'authors_per_country': 'Авторы по странам',
        'collaboration_patterns': 'Модели коллабораций',
        'collaboration_couples_section': 'Пары стран-коллабораций',
        'citation_dynamics_by_year': 'Динамика цитирований по годам',
        'cumulative_citations': 'Накопленные цитирования',
        'citation_network_heatmap': 'Тепловая карта цитирований',
        'most_cited_publications': 'Самые цитируемые публикации',
        'total_citing_works': 'Всего цитирующих работ',
        'stage': 'Этап',
        'articles_collected': 'статей собрано',
        'citing_works_collected': 'цитирующих работ собрано',
        'metadata_fetched': 'записей метаданных получено',
        'analysis_complete_label': 'Анализ завершен!',
        'generating_report_label': 'Генерация HTML отчета...',
        'report_ready': 'Отчет готов!',
        'click_to_download': 'Нажмите "Скачать HTML отчет" для сохранения',
        'journal_analysis_title': 'Advanced Journal Analysis Tool',
        'enter_issn': 'Введите ISSN журнала',
        'enter_period': 'Введите период (например, 2020-2023)',
        'total_publications_label': 'Всего публикаций',
        'total_citations_label': 'Всего цитирований',
        'h_index_label': 'h-индекс',
        'g_index_label': 'g-индекс',
        'i10_index_label': 'i10-индекс',
        'i100_index_label': 'i100-индекс',
        'avg_citations_label': 'Среднее цитирований',
        'open_access_label': 'Открытый доступ',
        'active_years_label': 'Активных лет',
        'unique_authors_label': 'Уникальных авторов',
        'unique_affiliations_label': 'Уникальных аффилиаций',
        'unique_countries_label': 'Уникальных стран',
        'avg_authors_per_paper_label': 'Среднее авторов/статья',
        'avg_affiliations_per_paper_label': 'Среднее аффилиаций/статья',
        'avg_countries_per_paper_label': 'Среднее стран/статья',
        'international_collaboration_rate_label': 'Доля международных коллабораций',
        'unique_citing_authors_label': 'Уникальных цитирующих авторов',
        'unique_citing_affiliations_label': 'Уникальных цитирующих аффилиаций',
        'unique_citing_countries_label': 'Уникальных цитирующих стран',
        'unique_citing_journals_label': 'Уникальных цитирующих журналов',
        'unique_citing_publishers_label': 'Уникальных цитирующих издателей',
        'open_access_breakdown': 'Разбивка по открытому доступу',
        'top_30_authors': 'Топ 30 авторов',
        'top_30_affiliations': 'Топ 30 аффилиаций',
        'collaboration_level': 'Уровень коллабораций',
        'individual_distribution': 'Индивидуальное распределение',
        'country_pairs': 'Пары стран',
        'frequency': 'Частота',
        'publication_year_col': 'Год публикации',
        'citation_year_col': 'Год цитирования',
        'citations_count_col': 'Количество цитирований',
        'first_citation_stats': 'Статистика первого цитирования',
        'min': 'Мин',
        'max': 'Макс',
        'average': 'Среднее',
        'median': 'Медиана',
        'years': 'лет',
        'cumulative': 'Накопленные',
        'publication_title': 'Название публикации',
        'citing_works_total': 'Всего цитирующих работ',
        'topic_trends': 'Тренды тем',
        'top_10_cited': 'Топ 10 наиболее цитируемых',
        'analyzed_work': 'Анализируемая работа',
        'citations_list': 'Список цитирований',
        'showing_all_publications': 'Показаны все публикации',
        'filtered_count': 'Отфильтровано: {count} публикаций',
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
    """Normalize ISSN string to XXXX-XXXX format"""
    cleaned = re.sub(r'[^0-9Xx]', '', str(issn_str).strip())
    if len(cleaned) == 8:
        return f"{cleaned[:4]}-{cleaned[4:]}".upper()
    return cleaned.upper()

def is_valid_issn(issn_str: str) -> bool:
    """Check if ISSN is valid"""
    normalized = normalize_issn(issn_str)
    return bool(re.match(r'^\d{4}-\d{3}[\dX]$', normalized))

def parse_period(period_str: str) -> tuple:
    """Parse period string to (start_year, end_year) or list of years"""
    period_str = period_str.strip()
    
    # Check for comma-separated years
    if ',' in period_str:
        years = [int(y.strip()) for y in period_str.split(',') if y.strip().isdigit()]
        if years:
            return tuple(sorted(years))
    
    # Check for range (YYYY-YYYY)
    if '-' in period_str:
        parts = period_str.split('-')
        if len(parts) == 2 and parts[0].strip().isdigit() and parts[1].strip().isdigit():
            start = int(parts[0].strip())
            end = int(parts[1].strip())
            if start <= end:
                return (start, end)
    
    # Single year
    if period_str.isdigit():
        year = int(period_str)
        return (year, year)
    
    raise ValueError("Invalid period format")

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
    if not os.path.exists('cache'):
        os.makedirs('cache')
    return f"cache/journal_{issn_clean}_{period_str}.json"

def load_from_cache(issn: str, period_str: str) -> Optional[Dict]:
    """Загружает данные из кэша"""
    if not USE_CACHE:
        return None
    
    cache_path = get_cache_path(issn, period_str)
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

def save_to_cache(issn: str, period_str: str, data: Dict):
    """Сохраняет данные в кэш"""
    if not USE_CACHE:
        return
    
    cache_path = get_cache_path(issn, period_str)
    try:
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        if SHOW_DEBUG_LOGS:
            print(f"✅ Данные сохранены в кэш: {cache_path}")
    except Exception as e:
        if SHOW_DEBUG_LOGS:
            print(f"⚠️ Ошибка сохранения кэша: {e}")

# ============================================
# DATA CLASSES FOR JOURNAL ANALYSIS
# ============================================

@dataclass
class Author:
    display_name: str
    orcid: Optional[str] = None
    affiliations: List[str] = field(default_factory=list)
    countries: List[str] = field(default_factory=list)

@dataclass
class Topic:
    display_name: str
    subfield: Optional[str] = None
    field: Optional[str] = None
    domain: Optional[str] = None
    score: float = 0.0

@dataclass
class Article:
    id: str
    doi: str
    title: str
    publication_year: int
    publication_date: Optional[str] = None
    cited_by_count: int = 0
    journal_name: str = ""
    publisher: str = ""
    is_oa: bool = False
    oa_status: str = "unknown"
    authors: List[Author] = field(default_factory=list)
    affiliations: List[str] = field(default_factory=list)
    countries: List[str] = field(default_factory=list)
    topics: List[Topic] = field(default_factory=list)
    concepts: List[str] = field(default_factory=list)
    citations_per_year: float = 0.0

@dataclass
class CitingWork:
    id: str
    doi: str
    title: str
    citing_year: int
    citing_date: Optional[str] = None
    journal_name: str = ""
    publisher: str = ""
    authors: List[Author] = field(default_factory=list)
    countries: List[str] = field(default_factory=list)
    topics: List[Topic] = field(default_factory=list)
    citation_lag: int = 0

@dataclass
class JournalMetrics:
    total_publications: int = 0
    total_citations: int = 0
    h_index: int = 0
    g_index: int = 0
    i10_index: int = 0
    i100_index: int = 0
    avg_citations: float = 0.0
    open_access_percentage: float = 0.0
    active_years: int = 0
    unique_authors: int = 0
    unique_affiliations: int = 0
    unique_countries: int = 0
    avg_authors_per_paper: float = 0.0
    avg_affiliations_per_paper: float = 0.0
    avg_countries_per_paper: float = 0.0
    international_collaboration_rate: float = 0.0
    unique_citing_authors: int = 0
    unique_citing_affiliations: int = 0
    unique_citing_countries: int = 0
    unique_citing_journals: int = 0
    unique_citing_publishers: int = 0

@dataclass
class JournalAnalysis:
    issn: str
    period: tuple
    articles: List[Article] = field(default_factory=list)
    citing_works: Dict[str, List[CitingWork]] = field(default_factory=dict)
    metrics: Optional[JournalMetrics] = None
    author_stats: Dict = field(default_factory=dict)
    affiliation_stats: Dict = field(default_factory=dict)
    country_stats: Dict = field(default_factory=dict)
    citation_dynamics: Dict = field(default_factory=dict)
    topic_analysis: Dict = field(default_factory=dict)
    detailed_citations: Dict = field(default_factory=dict)

# ============================================
# OPENALEX API CLIENT
# ============================================

class OpenAlexClient:
    def __init__(self, cache_dir: str = "cache/journals"):
        self.base_url = "https://api.openalex.org/works"
        self.cache_dir = cache_dir
        self.session = requests.Session()
        self.lock = Lock()
        
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
    
    def smart_request(self, params: Dict, retries: int = 5) -> Optional[Dict]:
        """Execute request with retries and rate limiting"""
        for attempt in range(retries):
            try:
                with self.lock:
                    time.sleep(random.uniform(0.2, 0.45))
                
                response = self.session.get(self.base_url, params=params, timeout=30)
                
                if response.status_code == 429:
                    wait = int(response.headers.get("Retry-After", 3))
                    time.sleep(wait + random.uniform(1, 2))
                    continue
                
                if response.status_code == 200:
                    return response.json()
                
                time.sleep(1.2 ** attempt)
                
            except Exception as e:
                if SHOW_DEBUG_LOGS:
                    print(f"⚠️ Request error: {e}")
                time.sleep(1.5 ** attempt)
        
        return None
    
    def get_works_metadata(self, work_ids: List[str]) -> Dict[str, Dict]:
        """Fetch full metadata for works by ID"""
        if not work_ids:
            return {}
        
        # Remove duplicates and ensure proper format
        clean_ids = []
        for w_id in work_ids:
            if w_id:
                clean_id = w_id.replace('https://openalex.org/', '').strip()
                if clean_id:
                    clean_ids.append(clean_id)
        
        clean_ids = list(set(clean_ids))
        
        result = {}
        
        for batch in chunks(clean_ids, 50):
            id_query = '|'.join([f"openalex:{id}" for id in batch])
            params = {
                'filter': f'openalex.id:{id_query}',
                'per_page': len(batch)
            }
            
            data = self.smart_request(params)
            
            if data and data.get('results'):
                for work in data['results']:
                    work_id = work.get('id', '').replace('https://openalex.org/', '')
                    if work_id:
                        result[work_id] = work
            
            time.sleep(DELAY_BETWEEN_BATCHES)
        
        return result
    
    def get_journal_articles(self, issn: str, years: tuple, progress_callback=None) -> List[Dict]:
        """Fetch articles from a journal for given period"""
        normalized = normalize_issn(issn)
        
        if not is_valid_issn(normalized):
            raise ValueError(f"Invalid ISSN: {issn}")
        
        # Build year filter
        if isinstance(years, tuple):
            if len(years) == 2:
                if years[0] == years[1]:
                    year_filter = f"publication_year:{years[0]}"
                else:
                    year_filter = f"publication_year:{years[0]}-{years[1]}"
            else:
                year_filter = '|'.join([f"publication_year:{y}" for y in years])
        else:
            year_filter = f"publication_year:{years}"
        
        articles = []
        cursor = "*"
        page = 0
        
        if SHOW_DEBUG_LOGS:
            print(f"🔍 Fetching articles for ISSN: {normalized}, period: {years}")
        
        while True:
            params = {
                "filter": f"primary_location.source.issn:{normalized},{year_filter}",
                "per_page": 200,
                "select": "id,doi,publication_year,publication_date,cited_by_count,title,primary_location",
                "cursor": cursor
            }
            
            data = self.smart_request(params)
            
            if not data or not data.get("results"):
                break
            
            for w in data["results"]:
                article = {
                    "id": w.get("id", "").replace("https://openalex.org/", ""),
                    "doi": w.get("doi", "").replace("https://doi.org/", "") if w.get("doi") else "",
                    "title": w.get("title", "No title"),
                    "publication_year": w.get("publication_year"),
                    "publication_date": w.get("publication_date"),
                    "cited_by_count": w.get("cited_by_count", 0),
                    "journal_name": "",
                    "publisher": "",
                    "is_oa": False,
                    "oa_status": "unknown"
                }
                
                # Extract journal info from primary_location
                primary_location = w.get("primary_location", {})
                source = primary_location.get("source", {})
                if source:
                    article["journal_name"] = source.get("display_name", "")
                    article["publisher"] = source.get("host_organization_name", "") or source.get("publisher", "")
                    article["is_oa"] = primary_location.get("is_oa", False)
                    article["oa_status"] = primary_location.get("oa_status", "unknown")
                
                articles.append(article)
            
            page += 1
            if progress_callback:
                progress_callback(len(articles), None)
            
            cursor = data.get("meta", {}).get("next_cursor")
            if not cursor:
                break
        
        if SHOW_DEBUG_LOGS:
            print(f"✅ Found {len(articles)} articles")
        
        return articles
    
    def get_citing_works(self, work_id: str, max_pages: int = 6) -> List[str]:
        """Get all works that cite a given work"""
        citing = []
        cursor = "*"
        page = 0
        
        while page < max_pages:
            params = {
                "filter": f"cites:{work_id}",
                "per_page": 200,
                "select": "doi,id,publication_year,publication_date,title,primary_location,cited_by_count",
                "cursor": cursor
            }
            
            data = self.smart_request(params)
            
            if not data or not data.get("results"):
                break
            
            for item in data["results"]:
                doi = item.get("doi", "").replace("https://doi.org/", "") if item.get("doi") else ""
                if doi:
                    citing.append({
                        "id": item.get("id", "").replace("https://openalex.org/", ""),
                        "doi": doi,
                        "title": item.get("title", "No title"),
                        "publication_year": item.get("publication_year"),
                        "publication_date": item.get("publication_date"),
                        "cited_by_count": item.get("cited_by_count", 0),
                        "journal_name": "",
                        "publisher": "",
                        "is_oa": False,
                        "oa_status": "unknown"
                    })
            
            page += 1
            cursor = data.get("meta", {}).get("next_cursor")
            if not cursor:
                break
        
        return citing

# ============================================
# JOURNAL ANALYZER
# ============================================

class JournalAnalyzer:
    def __init__(self, issn: str, period: tuple):
        self.issn = normalize_issn(issn)
        self.period = period
        self.client = OpenAlexClient()
        self.articles: List[Article] = []
        self.citing_works: Dict[str, List[CitingWork]] = {}
        self.metrics: Optional[JournalMetrics] = None
        self.author_stats = {}
        self.affiliation_stats = {}
        self.country_stats = {}
        self.citation_dynamics = {}
        self.topic_analysis = {}
        self.detailed_citations = {}
        self.raw_articles_data = []
        self.raw_citing_data = {}
        self.citing_work_ids = set()
    
    def parse_article_from_dict(self, data: Dict, citing_works: List[Dict] = None) -> Article:
        """Parse article data from OpenAlex response"""
        authors = []
        for auth_data in data.get("authorships", []):
            author = auth_data.get("author", {})
            insts = auth_data.get("institutions", [])
            affiliations = [inst.get("display_name", "") for inst in insts]
            countries = [inst.get("country_code", "") for inst in insts if inst.get("country_code")]
            
            authors.append(Author(
                display_name=author.get("display_name", "Unknown"),
                orcid=author.get("orcid", "").replace("https://orcid.org/", "") if author.get("orcid") else None,
                affiliations=affiliations,
                countries=countries
            ))
        
        affiliations = []
        countries = []
        for auth in authors:
            affiliations.extend(auth.affiliations)
            countries.extend(auth.countries)
        
        topics = []
        for topic_data in data.get("topics", []):
            topics.append(Topic(
                display_name=topic_data.get("display_name", ""),
                subfield=topic_data.get("subfield", {}).get("display_name", ""),
                field=topic_data.get("field", {}).get("display_name", ""),
                domain=topic_data.get("domain", {}).get("display_name", ""),
                score=topic_data.get("score", 0)
            ))
        
        # Primary topic
        primary_topic = data.get("primary_topic", {})
        if primary_topic:
            topics.append(Topic(
                display_name=primary_topic.get("display_name", ""),
                subfield=primary_topic.get("subfield", {}).get("display_name", ""),
                field=primary_topic.get("field", {}).get("display_name", ""),
                domain=primary_topic.get("domain", {}).get("display_name", ""),
                score=primary_topic.get("score", 0)
            ))
        
        concepts = [c.get("display_name", "") for c in data.get("concepts", []) if c.get("display_name")]
        
        oa = data.get("open_access", {})
        
        return Article(
            id=data.get("id", "").replace("https://openalex.org/", ""),
            doi=data.get("doi", "").replace("https://doi.org/", "") if data.get("doi") else "",
            title=data.get("title", "No title"),
            publication_year=data.get("publication_year", 0),
            publication_date=data.get("publication_date"),
            cited_by_count=data.get("cited_by_count", 0),
            journal_name=data.get("primary_location", {}).get("source", {}).get("display_name", ""),
            publisher=data.get("primary_location", {}).get("source", {}).get("host_organization_name", ""),
            is_oa=oa.get("is_oa", False),
            oa_status=oa.get("oa_status", "unknown"),
            authors=authors,
            affiliations=list(set(affiliations)),
            countries=list(set(countries)),
            topics=topics,
            concepts=concepts,
            citations_per_year=0
        )
    
    def parse_citing_from_dict(self, data: Dict, article_id: str) -> List[CitingWork]:
        """Parse citing works from OpenAlex response"""
        citing_list = []
        
        authors = []
        for auth_data in data.get("authorships", []):
            author = auth_data.get("author", {})
            insts = auth_data.get("institutions", [])
            affiliations = [inst.get("display_name", "") for inst in insts]
            countries = [inst.get("country_code", "") for inst in insts if inst.get("country_code")]
            
            authors.append(Author(
                display_name=author.get("display_name", "Unknown"),
                orcid=author.get("orcid", "").replace("https://orcid.org/", "") if author.get("orcid") else None,
                affiliations=affiliations,
                countries=countries
            ))
        
        topics = []
        for topic_data in data.get("topics", []):
            topics.append(Topic(
                display_name=topic_data.get("display_name", ""),
                subfield=topic_data.get("subfield", {}).get("display_name", ""),
                field=topic_data.get("field", {}).get("display_name", ""),
                domain=topic_data.get("domain", {}).get("display_name", ""),
                score=topic_data.get("score", 0)
            ))
        
        citing_list.append(CitingWork(
            id=data.get("id", "").replace("https://openalex.org/", ""),
            doi=data.get("doi", "").replace("https://doi.org/", "") if data.get("doi") else "",
            title=data.get("title", "No title"),
            citing_year=data.get("publication_year", 0),
            citing_date=data.get("publication_date"),
            journal_name=data.get("primary_location", {}).get("source", {}).get("display_name", ""),
            publisher=data.get("primary_location", {}).get("source", {}).get("host_organization_name", ""),
            authors=authors,
            countries=list(set([c for a in authors for c in a.countries])),
            topics=topics,
            citation_lag=0
        ))
        
        return citing_list
    
    def calculate_metrics(self) -> JournalMetrics:
        """Calculate all journal metrics"""
        if not self.articles:
            return JournalMetrics()
        
        metrics = JournalMetrics()
        
        # Total publications
        metrics.total_publications = len(self.articles)
        
        # Citations
        citations = [a.cited_by_count for a in self.articles]
        metrics.total_citations = sum(citations)
        metrics.avg_citations = sum(citations) / len(citations) if citations else 0
        
        # h-index
        citations_sorted = sorted([c for c in citations if c > 0], reverse=True)
        h_idx = 0
        for i, c in enumerate(citations_sorted, 1):
            if c >= i:
                h_idx = i
            else:
                break
        metrics.h_index = h_idx
        
        # g-index
        total_sorted = 0
        g_idx = 0
        for i, c in enumerate(citations_sorted, 1):
            total_sorted += c
            if total_sorted >= i**2:
                g_idx = i
        metrics.g_index = g_idx
        
        # i10-index and i100-index
        metrics.i10_index = sum(1 for c in citations if c >= 10)
        metrics.i100_index = sum(1 for c in citations if c >= 100)
        
        # Open Access
        oa_count = sum(1 for a in self.articles if a.is_oa)
        metrics.open_access_percentage = (oa_count / len(self.articles) * 100) if self.articles else 0
        
        # Active years
        years = [a.publication_year for a in self.articles if a.publication_year]
        metrics.active_years = len(set(years))
        
        # Unique authors, affiliations, countries
        all_authors = []
        all_affiliations = []
        all_countries = []
        
        for article in self.articles:
            for author in article.authors:
                if author.display_name:
                    all_authors.append(author.display_name)
            all_affiliations.extend(article.affiliations)
            all_countries.extend(article.countries)
        
        metrics.unique_authors = len(set(all_authors))
        metrics.unique_affiliations = len(set(all_affiliations))
        metrics.unique_countries = len(set(all_countries))
        
        # Avg authors/paper
        author_counts = [len(a.authors) for a in self.articles]
        metrics.avg_authors_per_paper = sum(author_counts) / len(author_counts) if author_counts else 0
        
        # Avg affiliations/paper
        affil_counts = [len(a.affiliations) for a in self.articles]
        metrics.avg_affiliations_per_paper = sum(affil_counts) / len(affil_counts) if affil_counts else 0
        
        # Avg countries/paper
        country_counts = [len(a.countries) for a in self.articles]
        metrics.avg_countries_per_paper = sum(country_counts) / len(country_counts) if country_counts else 0
        
        # International collaboration rate
        international_count = sum(1 for a in self.articles if len(set(a.countries)) > 1)
        metrics.international_collaboration_rate = (international_count / len(self.articles) * 100) if self.articles else 0
        
        # Citing works metrics
        all_citing_authors = []
        all_citing_affiliations = []
        all_citing_countries = []
        all_citing_journals = []
        all_citing_publishers = []
        
        for citing_list in self.citing_works.values():
            for citing in citing_list:
                for author in citing.authors:
                    if author.display_name:
                        all_citing_authors.append(author.display_name)
                all_citing_affiliations.extend([a for a in citing.authors for aff in a.affiliations if aff])
                all_citing_countries.extend(citing.countries)
                if citing.journal_name:
                    all_citing_journals.append(citing.journal_name)
                if citing.publisher:
                    all_citing_publishers.append(citing.publisher)
        
        metrics.unique_citing_authors = len(set(all_citing_authors))
        metrics.unique_citing_affiliations = len(set(all_citing_affiliations))
        metrics.unique_citing_countries = len(set(all_citing_countries))
        metrics.unique_citing_journals = len(set(all_citing_journals))
        metrics.unique_citing_publishers = len(set(all_citing_publishers))
        
        self.metrics = metrics
        return metrics
    
    def analyze_authors(self) -> Dict:
        """Analyze author statistics"""
        author_data = defaultdict(lambda: {
            'count': 0,
            'citations': 0,
            'orcid': None,
            'affiliations': set(),
            'countries': set()
        })
        
        for article in self.articles:
            for author in article.authors:
                if author.display_name:
                    key = author.display_name
                    author_data[key]['count'] += 1
                    author_data[key]['citations'] += article.cited_by_count
                    if author.orcid and not author_data[key]['orcid']:
                        author_data[key]['orcid'] = author.orcid
                    author_data[key]['affiliations'].update(author.affiliations)
                    author_data[key]['countries'].update(author.countries)
        
        # Sort by count (number of publications)
        sorted_authors = sorted(
            author_data.items(),
            key=lambda x: (x[1]['count'], x[1]['citations']),
            reverse=True
        )
        
        self.author_stats = {
            'top_30': [
                {
                    'name': name,
                    'count': data['count'],
                    'citations': data['citations'],
                    'orcid': data['orcid'],
                    'affiliations': list(data['affiliations'])[:5],
                    'countries': list(data['countries'])
                }
                for name, data in sorted_authors[:30]
            ],
            'total': len(author_data)
        }
        
        return self.author_stats
    
    def analyze_affiliations(self) -> Dict:
        """Analyze affiliation statistics"""
        affil_data = defaultdict(lambda: {
            'count': 0,
            'citations': 0,
            'countries': set()
        })
        
        for article in self.articles:
            for affil in article.affiliations:
                if affil:
                    affil_data[affil]['count'] += 1
                    affil_data[affil]['citations'] += article.cited_by_count
                    for country in article.countries:
                        affil_data[affil]['countries'].add(country)
        
        sorted_affils = sorted(
            affil_data.items(),
            key=lambda x: x[1]['count'],
            reverse=True
        )
        
        self.affiliation_stats = {
            'top_30': [
                {
                    'name': name,
                    'count': data['count'],
                    'citations': data['citations'],
                    'countries': list(data['countries'])
                }
                for name, data in sorted_affils[:30]
            ],
            'total': len(affil_data)
        }
        
        return self.affiliation_stats
    
    def analyze_countries(self) -> Dict:
        """Analyze country statistics"""
        # 5.3.1 Unique Countries per Publication
        unique_countries_per_pub = []
        for article in self.articles:
            unique_countries_per_pub.append(len(set(article.countries)))
        
        # 5.3.2 Authors per Country
        authors_per_country = defaultdict(int)
        for article in self.articles:
            for author in article.authors:
                for country in author.countries:
                    authors_per_country[country] += 1
        
        # 5.3.3 Collaboration Patterns
        single_country = 0
        international = 0
        for article in self.articles:
            if len(set(article.countries)) <= 1:
                single_country += 1
            else:
                international += 1
        
        # 5.3.4 Collaboration Couples
        country_pairs = defaultdict(int)
        for article in self.articles:
            countries = list(set(article.countries))
            if len(countries) >= 2:
                for i in range(len(countries)):
                    for j in range(i+1, len(countries)):
                        pair = tuple(sorted([countries[i], countries[j]]))
                        country_pairs[pair] += 1
        
        sorted_pairs = sorted(
            country_pairs.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        self.country_stats = {
            'unique_countries_per_pub': {
                'counts': unique_countries_per_pub,
                'avg': sum(unique_countries_per_pub) / len(unique_countries_per_pub) if unique_countries_per_pub else 0,
                'max': max(unique_countries_per_pub) if unique_countries_per_pub else 0
            },
            'authors_per_country': dict(authors_per_country),
            'collaboration_patterns': {
                'single_country': single_country,
                'international': international,
                'total': len(self.articles)
            },
            'collaboration_couples': sorted_pairs[:20]
        }
        
        return self.country_stats
    
    def analyze_citation_dynamics(self) -> Dict:
        """Analyze citation dynamics"""
        # Build citation matrix: publication_year -> citation_year -> count
        citation_matrix = defaultdict(lambda: defaultdict(int))
        first_citation_lags = []
        
        for article in self.articles:
            pub_year = article.publication_year
            if pub_year not in citation_matrix:
                citation_matrix[pub_year] = defaultdict(int)
            
            citing_list = self.citing_works.get(article.id, [])
            first_lag = None
            
            for citing in citing_list:
                citing_year = citing.citing_year
                if citing_year:
                    citation_matrix[pub_year][citing_year] += 1
                    
                    lag = citing_year - pub_year
                    if first_lag is None or lag < first_lag:
                        first_lag = lag
            
            if first_lag is not None:
                first_citation_lags.append(first_lag)
        
        # 6.1 Citation Dynamics by Year (table)
        dynamics_table = []
        for pub_year in sorted(citation_matrix.keys()):
            for cit_year in sorted(citation_matrix[pub_year].keys()):
                dynamics_table.append({
                    'publication_year': pub_year,
                    'citation_year': cit_year,
                    'citations_count': citation_matrix[pub_year][cit_year]
                })
        
        # 6.2 Cumulative Citations
        cumulative = defaultdict(int)
        all_citation_years = []
        for pub_year, cit_years in citation_matrix.items():
            for cit_year, count in cit_years.items():
                cumulative[cit_year] += count
                all_citation_years.append(cit_year)
        
        cumulative_sorted = sorted(cumulative.items())
        # Running total
        running_total = 0
        cumulative_with_total = []
        for year, count in cumulative_sorted:
            running_total += count
            cumulative_with_total.append({
                'year': year,
                'yearly_count': count,
                'cumulative_total': running_total
            })
        
        # First citation stats
        first_citation_stats = {
            'min': min(first_citation_lags) if first_citation_lags else None,
            'max': max(first_citation_lags) if first_citation_lags else None,
            'avg': sum(first_citation_lags) / len(first_citation_lags) if first_citation_lags else None,
            'median': sorted(first_citation_lags)[len(first_citation_lags)//2] if first_citation_lags else None,
            'count': len(first_citation_lags)
        }
        
        self.citation_dynamics = {
            'matrix': citation_matrix,
            'table': dynamics_table,
            'cumulative': cumulative_with_total,
            'first_citation_stats': first_citation_stats
        }
        
        return self.citation_dynamics
    
    def analyze_topics(self) -> Dict:
        """Analyze topics, subtopics, fields, domains, concepts"""
        # Count topics in analyzed articles
        topic_count = defaultdict(int)
        subtopic_count = defaultdict(int)
        field_count = defaultdict(int)
        domain_count = defaultdict(int)
        concept_count = defaultdict(int)
        
        for article in self.articles:
            for topic in article.topics:
                if topic.display_name:
                    topic_count[topic.display_name] += 1
                if topic.subfield:
                    subtopic_count[topic.subfield] += 1
                if topic.field:
                    field_count[topic.field] += 1
                if topic.domain:
                    domain_count[topic.domain] += 1
            for concept in article.concepts:
                if concept:
                    concept_count[concept] += 1
        
        # Count topics in citing works
        citing_topic_count = defaultdict(int)
        citing_subtopic_count = defaultdict(int)
        citing_field_count = defaultdict(int)
        citing_domain_count = defaultdict(int)
        citing_concept_count = defaultdict(int)
        
        for citing_list in self.citing_works.values():
            for citing in citing_list:
                for topic in citing.topics:
                    if topic.display_name:
                        citing_topic_count[topic.display_name] += 1
                    if topic.subfield:
                        citing_subtopic_count[topic.subfield] += 1
                    if topic.field:
                        citing_field_count[topic.field] += 1
                    if topic.domain:
                        citing_domain_count[topic.domain] += 1
        
        # Normalize counts
        total_articles = len(self.articles) if self.articles else 1
        total_citing = sum(len(c) for c in self.citing_works.values()) if self.citing_works else 1
        total_combined = total_articles + total_citing
        
        # Build combined topic data
        all_topics = set(topic_count.keys()) | set(citing_topic_count.keys())
        topic_analysis = {}
        
        for topic in all_topics:
            analyzed = topic_count.get(topic, 0)
            citing = citing_topic_count.get(topic, 0)
            
            # First and peak years for this topic in analyzed articles
            years = []
            for article in self.articles:
                for t in article.topics:
                    if t.display_name == topic and article.publication_year:
                        years.append(article.publication_year)
            
            first_year = min(years) if years else None
            peak_year = max(set(years), key=years.count) if years else None
            
            topic_analysis[topic] = {
                'analyzed_count': analyzed,
                'citing_count': citing,
                'analyzed_norm_count': analyzed / total_articles,
                'citing_norm_count': citing / total_citing,
                'total_norm_count': (analyzed + citing) / total_combined,
                'first_year': first_year,
                'peak_year': peak_year,
                'total': analyzed + citing
            }
        
        # Sort by total norm count
        sorted_topics = sorted(
            topic_analysis.items(),
            key=lambda x: x[1]['total_norm_count'],
            reverse=True
        )
        
        # 8.2 Top 10 most cited topics, subtopics, fields, domains, concepts
        # Combine analyzed and citing counts for each category
        combined_subtopics = defaultdict(int)
        for k, v in subtopic_count.items():
            combined_subtopics[k] += v
        for k, v in citing_subtopic_count.items():
            combined_subtopics[k] += v
        
        combined_fields = defaultdict(int)
        for k, v in field_count.items():
            combined_fields[k] += v
        for k, v in citing_field_count.items():
            combined_fields[k] += v
        
        combined_domains = defaultdict(int)
        for k, v in domain_count.items():
            combined_domains[k] += v
        for k, v in citing_domain_count.items():
            combined_domains[k] += v
        
        combined_concepts = defaultdict(int)
        for k, v in concept_count.items():
            combined_concepts[k] += v
        # No concepts from citing works (not available in simple query)
        
        self.topic_analysis = {
            'top_topics': sorted_topics[:20],
            'top_subtopics': sorted(combined_subtopics.items(), key=lambda x: x[1], reverse=True)[:10],
            'top_fields': sorted(combined_fields.items(), key=lambda x: x[1], reverse=True)[:10],
            'top_domains': sorted(combined_domains.items(), key=lambda x: x[1], reverse=True)[:10],
            'top_concepts': sorted(combined_concepts.items(), key=lambda x: x[1], reverse=True)[:10],
            'all_topics': dict(sorted_topics)
        }
        
        return self.topic_analysis
    
    def build_detailed_citations(self) -> Dict:
        """Build detailed citations for each article"""
        detailed = {}
        
        for article in self.articles:
            citing_list = self.citing_works.get(article.id, [])
            if citing_list:
                citations_data = []
                for citing in citing_list:
                    citations_data.append({
                        'citing_title': citing.title,
                        'citing_year': citing.citing_year,
                        'citing_date': citing.citing_date,
                        'citing_journal': citing.journal_name,
                        'citing_publisher': citing.publisher,
                        'citing_doi': citing.doi,
                        'citation_lag': citing.citation_lag,
                        'citing_authors': [a.display_name for a in citing.authors],
                        'citing_countries': citing.countries,
                        'citing_topics': [t.display_name for t in citing.topics[:5]]
                    })
                
                detailed[article.id] = {
                    'title': article.title,
                    'year': article.publication_year,
                    'doi': article.doi,
                    'total_citations': len(citations_data),
                    'citations': citations_data
                }
        
        self.detailed_citations = detailed
        return detailed
    
    def run_analysis(self, progress_callback=None) -> 'JournalAnalysis':
        """Run full analysis pipeline"""
        total_stages = 5
        
        # Stage 1: Collect journal articles
        if progress_callback:
            progress_callback(1, total_stages, 0, 0, "stage_1", "Collecting articles...")
        
        raw_articles = self.client.get_journal_articles(
            self.issn,
            self.period,
            lambda count, total: progress_callback(1, total_stages, count, None, "stage_1", f"Collected {count} articles") if progress_callback else None
        )
        self.raw_articles_data = raw_articles
        
        if progress_callback:
            progress_callback(1, total_stages, len(raw_articles), len(raw_articles), "stage_1", f"Collected {len(raw_articles)} articles")
        
        if not raw_articles:
            return JournalAnalysis(self.issn, self.period)
        
        # Stage 2: Collect citing works
        if progress_callback:
            progress_callback(2, total_stages, 0, 0, "stage_2", "Collecting citing works...")
        
        # Get IDs of articles with citations
        article_ids = [a['id'] for a in raw_articles if a['cited_by_count'] > 0]
        total_articles_with_citations = len(article_ids)
        
        citing_map = {}
        citing_work_ids = set()
        
        for idx, article_id in enumerate(article_ids, 1):
            citing = self.client.get_citing_works(article_id)
            citing_map[article_id] = citing
            for c in citing:
                if c.get('id'):
                    citing_work_ids.add(c['id'])
            
            if progress_callback:
                progress_callback(2, total_stages, idx, total_articles_with_citations, "stage_2", f"Processed {idx}/{total_articles_with_citations} articles")
        
        self.raw_citing_data = citing_map
        self.citing_work_ids = citing_work_ids
        
        if progress_callback:
            progress_callback(2, total_stages, len(citing_work_ids), len(citing_work_ids), "stage_2", f"Collected {len(citing_work_ids)} citing works")
        
        # Stage 3: Fetch metadata for analyzed articles
        if progress_callback:
            progress_callback(3, total_stages, 0, 0, "stage_3", "Fetching article metadata...")
        
        all_work_ids = [a['id'] for a in raw_articles if a['id']]
        all_work_ids = list(set(all_work_ids))
        
        metadata = self.client.get_works_metadata(all_work_ids)
        
        # Parse articles
        parsed_articles = []
        for raw in raw_articles:
            work_id = raw.get('id')
            meta = metadata.get(work_id, {})
            if meta:
                article = self.parse_article_from_dict(meta)
                parsed_articles.append(article)
            else:
                # Use raw data as fallback
                article = Article(
                    id=raw.get('id', ''),
                    doi=raw.get('doi', ''),
                    title=raw.get('title', 'No title'),
                    publication_year=raw.get('publication_year', 0),
                    publication_date=raw.get('publication_date'),
                    cited_by_count=raw.get('cited_by_count', 0),
                    journal_name=raw.get('journal_name', ''),
                    publisher=raw.get('publisher', ''),
                    is_oa=raw.get('is_oa', False),
                    oa_status=raw.get('oa_status', 'unknown'),
                    authors=[],
                    affiliations=[],
                    countries=[],
                    topics=[],
                    concepts=[]
                )
                parsed_articles.append(article)
        
        self.articles = parsed_articles
        
        if progress_callback:
            progress_callback(3, total_stages, len(parsed_articles), len(all_work_ids), "stage_3", f"Fetched metadata for {len(parsed_articles)} articles")
        
        # Stage 4: Fetch metadata for citing works
        if progress_callback:
            progress_callback(4, total_stages, 0, 0, "stage_4", "Fetching citing works metadata...")
        
        citing_work_ids_list = list(self.citing_work_ids)
        citing_metadata = {}
        
        if citing_work_ids_list:
            # Process in batches to avoid overwhelming the API
            batch_size = 50
            total_batches = (len(citing_work_ids_list) + batch_size - 1) // batch_size
            
            for batch_idx in range(total_batches):
                start_idx = batch_idx * batch_size
                end_idx = min(start_idx + batch_size, len(citing_work_ids_list))
                batch_ids = citing_work_ids_list[start_idx:end_idx]
                
                batch_meta = self.client.get_works_metadata(batch_ids)
                citing_metadata.update(batch_meta)
                
                if progress_callback:
                    progress_callback(4, total_stages, min(end_idx, len(citing_work_ids_list)), len(citing_work_ids_list), "stage_4", f"Fetched metadata for {end_idx}/{len(citing_work_ids_list)} works")
        
        # Parse citing works
        parsed_citing = {}
        for article_id, citing_list in citing_map.items():
            parsed_citing[article_id] = []
            for citing_raw in citing_list:
                work_id = citing_raw.get('id')
                meta = citing_metadata.get(work_id, {})
                if meta:
                    citing_works = self.parse_citing_from_dict(meta, article_id)
                    if citing_works:
                        citing_work = citing_works[0]
                        # Calculate citation lag
                        if citing_work.citing_year and self.articles:
                            # Find the original article
                            for article in self.articles:
                                if article.id == article_id:
                                    citing_work.citation_lag = citing_work.citing_year - article.publication_year
                                    break
                        parsed_citing[article_id].append(citing_work)
                else:
                    # Use raw data as fallback
                    citing_work = CitingWork(
                        id=citing_raw.get('id', ''),
                        doi=citing_raw.get('doi', ''),
                        title=citing_raw.get('title', 'No title'),
                        citing_year=citing_raw.get('publication_year', 0),
                        citing_date=citing_raw.get('publication_date'),
                        journal_name=citing_raw.get('journal_name', ''),
                        publisher=citing_raw.get('publisher', ''),
                        authors=[],
                        countries=[],
                        topics=[],
                        citation_lag=0
                    )
                    parsed_citing[article_id].append(citing_work)
        
        self.citing_works = parsed_citing
        
        if progress_callback:
            total_citing_works = sum(len(c) for c in parsed_citing.values())
            progress_callback(4, total_stages, total_citing_works, total_citing_works, "stage_4", f"Fetched {total_citing_works} citing works")
        
        # Stage 5: Analyze data
        if progress_callback:
            progress_callback(5, total_stages, 0, 0, "stage_5", "Analyzing data...")
        
        # Calculate all metrics
        self.calculate_metrics()
        self.analyze_authors()
        self.analyze_affiliations()
        self.analyze_countries()
        self.analyze_citation_dynamics()
        self.analyze_topics()
        self.build_detailed_citations()
        
        if progress_callback:
            progress_callback(5, total_stages, 100, 100, "stage_5", "Analysis complete!")
        
        return JournalAnalysis(
            issn=self.issn,
            period=self.period,
            articles=self.articles,
            citing_works=self.citing_works,
            metrics=self.metrics,
            author_stats=self.author_stats,
            affiliation_stats=self.affiliation_stats,
            country_stats=self.country_stats,
            citation_dynamics=self.citation_dynamics,
            topic_analysis=self.topic_analysis,
            detailed_citations=self.detailed_citations
        )

# ============================================
# HTML REPORT GENERATION
# ============================================

def generate_html_report_journal(analysis: JournalAnalysis, logo_base64: Optional[str] = None, 
                                  app_logo_base64: Optional[str] = None, 
                                  theme_colors: Optional[Dict] = None, lang: str = 'en') -> str:
    """Generate HTML report for journal analysis"""
    
    if theme_colors is None:
        theme_colors = {
            'primary': '#667eea',
            'secondary': '#f39c12'
        }
    
    primary = theme_colors.get('primary', '#667eea')
    secondary = theme_colors.get('secondary', '#f39c12')
    
    metrics = analysis.metrics or JournalMetrics()
    articles = analysis.articles
    citing_works = analysis.citing_works
    author_stats = analysis.author_stats or {}
    affiliation_stats = analysis.affiliation_stats or {}
    country_stats = analysis.country_stats or {}
    citation_dynamics = analysis.citation_dynamics or {}
    topic_analysis = analysis.topic_analysis or {}
    detailed_citations = analysis.detailed_citations or {}
    
    def t(key: str, **kwargs) -> str:
        return translate(key, lang, **kwargs)
    
    # Build Open Access breakdown
    oa_breakdown = defaultdict(int)
    for article in articles:
        status = article.oa_status if article.oa_status else "unknown"
        oa_breakdown[status] += 1
    
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
    for status, label in oa_labels.items():
        if status in oa_breakdown:
            count = oa_breakdown[status]
            pct = (count / len(articles) * 100) if articles else 0
            oa_html += f"""
            <div style="margin: 5px 0;">
                <span>{label}:</span>
                <span style="font-weight: 600;">{count}</span>
                <span style="color: #666; font-size: 12px;">({pct:.1f}%)</span>
            </div>
            """
    
    # Build author analysis table
    author_html = ""
    for i, author in enumerate(author_stats.get('top_30', []), 1):
        author_html += f"""
        <tr>
            <td>{i}</td>
            <td>{html.escape(author.get('name', 'Unknown'))}</td>
            <td>{author.get('orcid', '')}</td>
            <td>{'; '.join(author.get('affiliations', [])[:3])}</td>
            <td>{'; '.join(author.get('countries', []))}</td>
            <td>{author.get('count', 0)}</td>
            <td>{author.get('citations', 0)}</td>
        </tr>
        """
    
    # Build affiliations table
    affil_html = ""
    for i, affil in enumerate(affiliation_stats.get('top_30', []), 1):
        affil_html += f"""
        <tr>
            <td>{i}</td>
            <td>{html.escape(affil.get('name', 'Unknown'))}</td>
            <td>{affil.get('count', 0)}</td>
            <td>{affil.get('citations', 0)}</td>
            <td>{'; '.join(affil.get('countries', []))}</td>
        </tr>
        """
    
    # Build country stats
    # 5.3.1 Unique Countries per Publication
    countries_per_pub = country_stats.get('unique_countries_per_pub', {})
    avg_countries = countries_per_pub.get('avg', 0)
    
    # 5.3.2 Authors per Country
    authors_per_country = country_stats.get('authors_per_country', {})
    authors_per_country_html = ""
    for country, count in sorted(authors_per_country.items(), key=lambda x: x[1], reverse=True)[:20]:
        authors_per_country_html += f"""
        <tr>
            <td>{country}</td>
            <td>{count}</td>
        </tr>
        """
    
    # 5.3.3 Collaboration Patterns
    collab_patterns = country_stats.get('collaboration_patterns', {})
    single_country = collab_patterns.get('single_country', 0)
    international = collab_patterns.get('international', 0)
    total_pubs = collab_patterns.get('total', 1)
    
    # 5.3.4 Collaboration Couples
    collab_couples = country_stats.get('collaboration_couples', [])
    collab_couples_html = ""
    for pair, count in collab_couples[:15]:
        collab_couples_html += f"""
        <tr>
            <td>{pair[0]} ↔ {pair[1]}</td>
            <td>{count}</td>
        </tr>
        """
    
    # 6.1 Citation Dynamics by Year (table)
    dynamics_table = citation_dynamics.get('table', [])
    dynamics_html = ""
    for row in dynamics_table:
        dynamics_html += f"""
        <tr>
            <td>{row.get('publication_year', '')}</td>
            <td>{row.get('citation_year', '')}</td>
            <td>{row.get('citations_count', 0)}</td>
        </tr>
        """
    
    # 6.2 Cumulative Citations
    cumulative = citation_dynamics.get('cumulative', [])
    cumulative_html = ""
    for row in cumulative:
        cumulative_html += f"""
        <tr>
            <td>{row.get('year', '')}</td>
            <td>{row.get('cumulative_total', 0)}</td>
        </tr>
        """
    
    # 6.3 Heatmap (build matrix)
    matrix = citation_dynamics.get('matrix', {})
    heatmap_html = ""
    if matrix:
        pub_years = sorted(matrix.keys())
        all_cit_years = set()
        for pub_year, cit_years in matrix.items():
            all_cit_years.update(cit_years.keys())
        cit_years = sorted(all_cit_years)
        
        # Build header
        heatmap_html = "<table style='border-collapse: collapse; width: 100%;'>"
        heatmap_html += "<tr><th style='padding: 8px; background: #f0f0f0; border: 1px solid #ddd;'>Publication \\ Citation</th>"
        for cit_year in cit_years:
            heatmap_html += f"<th style='padding: 8px; background: #f0f0f0; border: 1px solid #ddd;'>{cit_year}</th>"
        heatmap_html += "</tr>"
        
        max_val = 0
        for pub_year, cit_years_dict in matrix.items():
            for cit_year, count in cit_years_dict.items():
                if count > max_val:
                    max_val = count
        
        for pub_year in pub_years:
            heatmap_html += f"<tr><td style='padding: 8px; border: 1px solid #ddd; font-weight: bold;'>{pub_year}</td>"
            for cit_year in cit_years:
                count = matrix.get(pub_year, {}).get(cit_year, 0)
                # Color intensity based on count
                if count > 0:
                    intensity = count / max_val if max_val > 0 else 0
                    # Use primary color with varying opacity
                    r, g, b = hex_to_rgb(primary)
                    opacity = 0.2 + intensity * 0.7
                    color = f"rgba({r}, {g}, {b}, {opacity})"
                    text_color = "#fff" if intensity > 0.5 else "#333"
                    heatmap_html += f"<td style='padding: 8px; border: 1px solid #ddd; text-align: center; background: {color}; color: {text_color};'>{count if count > 0 else ''}</td>"
                else:
                    heatmap_html += f"<td style='padding: 8px; border: 1px solid #ddd; text-align: center;'>&nbsp;</td>"
            heatmap_html += "</tr>"
        heatmap_html += "</table>"
    
    # 6.4 Most Cited Publications
    most_cited = sorted(articles, key=lambda x: x.cited_by_count, reverse=True)[:10]
    most_cited_html = ""
    for i, article in enumerate(most_cited, 1):
        authors_str = ', '.join([a.display_name for a in article.authors[:3]])
        if len(article.authors) > 3:
            authors_str += f" +{len(article.authors) - 3} more"
        citations_per_year = article.cited_by_count / (2026 - article.publication_year + 1) if article.publication_year else 0
        
        most_cited_html += f"""
        <tr>
            <td>{i}</td>
            <td>{html.escape(article.title)}</td>
            <td>{article.publication_year}</td>
            <td>{article.cited_by_count}</td>
            <td>{citations_per_year:.1f}</td>
            <td>{authors_str}</td>
            <td><a href="https://doi.org/{article.doi}" target="_blank" style="color: {primary};">{article.doi}</a></td>
        </tr>
        """
    
    # 7. Citing Works Analysis - Top citing authors
    citing_authors = defaultdict(int)
    citing_affiliations = defaultdict(int)
    citing_countries = defaultdict(int)
    citing_journals = defaultdict(int)
    citing_publishers = defaultdict(int)
    
    for citing_list in citing_works.values():
        for citing in citing_list:
            for author in citing.authors:
                if author.display_name:
                    citing_authors[author.display_name] += 1
            for aff in citing.authors:
                for a in aff.affiliations:
                    if a:
                        citing_affiliations[a] += 1
            for country in citing.countries:
                if country:
                    citing_countries[country] += 1
            if citing.journal_name:
                citing_journals[citing.journal_name] += 1
            if citing.publisher:
                citing_publishers[citing.publisher] += 1
    
    top_citing_authors_html = ""
    for i, (name, count) in enumerate(sorted(citing_authors.items(), key=lambda x: x[1], reverse=True)[:20], 1):
        top_citing_authors_html += f"""
        <tr>
            <td>{i}</td>
            <td>{html.escape(name)}</td>
            <td>{count}</td>
        </tr>
        """
    
    top_citing_affils_html = ""
    for i, (name, count) in enumerate(sorted(citing_affiliations.items(), key=lambda x: x[1], reverse=True)[:20], 1):
        top_citing_affils_html += f"""
        <tr>
            <td>{i}</td>
            <td>{html.escape(name)}</td>
            <td>{count}</td>
        </tr>
        """
    
    top_citing_countries_html = ""
    for i, (name, count) in enumerate(sorted(citing_countries.items(), key=lambda x: x[1], reverse=True)[:20], 1):
        top_citing_countries_html += f"""
        <tr>
            <td>{i}</td>
            <td>{name}</td>
            <td>{count}</td>
        </tr>
        """
    
    top_citing_journals_html = ""
    for i, (name, count) in enumerate(sorted(citing_journals.items(), key=lambda x: x[1], reverse=True)[:20], 1):
        top_citing_journals_html += f"""
        <tr>
            <td>{i}</td>
            <td>{html.escape(name)}</td>
            <td>{count}</td>
        </tr>
        """
    
    top_citing_publishers_html = ""
    for i, (name, count) in enumerate(sorted(citing_publishers.items(), key=lambda x: x[1], reverse=True)[:20], 1):
        top_citing_publishers_html += f"""
        <tr>
            <td>{i}</td>
            <td>{html.escape(name)}</td>
            <td>{count}</td>
        </tr>
        """
    
    # 8. Topic Analysis
    top_topics = topic_analysis.get('top_topics', [])
    topics_html = ""
    for topic, data in top_topics[:20]:
        topics_html += f"""
        <tr>
            <td>{html.escape(topic)}</td>
            <td>{data.get('analyzed_count', 0)}</td>
            <td>{data.get('citing_count', 0)}</td>
            <td>{data.get('analyzed_norm_count', 0):.3f}</td>
            <td>{data.get('citing_norm_count', 0):.3f}</td>
            <td>{data.get('total_norm_count', 0):.3f}</td>
            <td>{data.get('first_year', '')}</td>
            <td>{data.get('peak_year', '')}</td>
        </tr>
        """
    
    # 8.2 Top 10 most cited categories
    top_subtopics = topic_analysis.get('top_subtopics', [])
    top_fields = topic_analysis.get('top_fields', [])
    top_domains = topic_analysis.get('top_domains', [])
    top_concepts = topic_analysis.get('top_concepts', [])
    
    top_subtopics_html = ""
    for name, count in top_subtopics[:10]:
        top_subtopics_html += f"""
        <tr>
            <td>{html.escape(name)}</td>
            <td>{count}</td>
        </tr>
        """
    
    top_fields_html = ""
    for name, count in top_fields[:10]:
        top_fields_html += f"""
        <tr>
            <td>{html.escape(name)}</td>
            <td>{count}</td>
        </tr>
        """
    
    top_domains_html = ""
    for name, count in top_domains[:10]:
        top_domains_html += f"""
        <tr>
            <td>{html.escape(name)}</td>
            <td>{count}</td>
        </tr>
        """
    
    top_concepts_html = ""
    for name, count in top_concepts[:10]:
        top_concepts_html += f"""
        <tr>
            <td>{html.escape(name)}</td>
            <td>{count}</td>
        </tr>
        """
    
    # 9. Detailed Citations (collapsible)
    detailed_citations_html = ""
    for article_id, data in detailed_citations.items():
        safe_id = article_id.replace('https://openalex.org/', '').replace('/', '_')
        detailed_citations_html += f"""
        <div class="collapser" onclick="toggleCitations('{safe_id}')" style="cursor: pointer; padding: 12px 15px; margin: 8px 0; background: #f8f9fa; border-radius: 8px; border-left: 4px solid {primary};">
            <strong>{html.escape(data.get('title', 'No title')[:80])}</strong>
            <span style="background: {primary}; color: white; padding: 2px 10px; border-radius: 12px; font-size: 12px; margin-left: 10px;">{data.get('year', '')}</span>
            <span style="font-weight: 600; color: {primary}; margin-left: 10px;">{data.get('total_citations', 0)} {t('citations')}</span>
            <span style="font-size: 12px; color: #666; margin-left: 10px;">DOI: {data.get('doi', '')}</span>
            <span style="float: right; font-size: 12px; color: #666;">▼ {t('show_citations')}</span>
        </div>
        <div id="citations_{safe_id}" style="display: none; padding: 10px 20px; margin-bottom: 10px; background: #f0f2f5; border-radius: 8px;">
        """
        
        for cite in data.get('citations', []):
            authors_str = ', '.join(cite.get('citing_authors', [])[:3])
            if len(cite.get('citing_authors', [])) > 3:
                authors_str += f" +{len(cite.get('citing_authors', [])) - 3} more"
            
            topics_str = ', '.join(cite.get('citing_topics', [])[:3])
            if len(cite.get('citing_topics', [])) > 3:
                topics_str += f" +{len(cite.get('citing_topics', [])) - 3} more"
            
            detailed_citations_html += f"""
            <div style="padding: 10px; margin: 5px 0; background: white; border-radius: 6px; border-left: 3px solid {secondary};">
                <div><strong>{html.escape(cite.get('citing_title', 'No title'))}</strong></div>
                <div style="font-size: 13px; color: #555; margin-top: 4px;">
                    <strong>{t('citing_journal')}:</strong> {html.escape(cite.get('citing_journal', ''))} | 
                    <strong>{t('citing_year')}:</strong> {cite.get('citing_year', '')} | 
                    <strong>{t('citation_lag')}:</strong> {cite.get('citation_lag', 0)} {t('years')}
                </div>
                <div style="font-size: 13px; color: #555;">
                    <strong>{t('authors')}:</strong> {authors_str} |
                    <strong>{t('countries')}:</strong> {', '.join(cite.get('citing_countries', [])[:3])} |
                    <strong>{t('topics')}:</strong> {topics_str}
                </div>
                <div style="font-size: 13px; color: #555;">
                    <a href="https://doi.org/{cite.get('citing_doi', '')}" target="_blank" style="color: {primary};">DOI: {cite.get('citing_doi', '')}</a>
                </div>
            </div>
            """
        
        detailed_citations_html += """
        </div>
        """
    
    # 10. All Publications (filterable table)
    all_publications_html = ""
    for i, article in enumerate(sorted(articles, key=lambda x: x.publication_year, reverse=True), 1):
        authors_str = ', '.join([a.display_name for a in article.authors[:3]])
        if len(article.authors) > 3:
            authors_str += f" +{len(article.authors) - 3} more"
        
        affils_str = ', '.join(article.affiliations[:3])
        if len(article.affiliations) > 3:
            affils_str += f" +{len(article.affiliations) - 3} more"
        
        citations_per_year = article.cited_by_count / (2026 - article.publication_year + 1) if article.publication_year else 0
        
        all_publications_html += f"""
        <tr data-year="{article.publication_year}" data-authors="{', '.join([a.display_name for a in article.authors])}" data-affiliations="{', '.join(article.affiliations)}" data-citations="{article.cited_by_count}" data-title="{article.title.lower()}">
            <td>{i}</td>
            <td class="word-wrap">{html.escape(article.title)}</td>
            <td>{article.publication_year}</td>
            <td>{authors_str}</td>
            <td>{affils_str}</td>
            <td><span class="citation-count">{article.cited_by_count}</span></td>
            <td>{citations_per_year:.1f}</td>
            <td><a href="https://doi.org/{article.doi}" target="_blank" style="color: {primary};">{article.doi}</a></td>
        </tr>
        """
    
    # Build year filter options
    year_options = sorted(set(a.publication_year for a in articles if a.publication_year), reverse=True)
    year_filter_options = '<option value="">All Years</option>'
    for year in year_options:
        year_filter_options += f'<option value="{year}">{year}</option>'
    
    # Full HTML template
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{t('journal_analysis_title')} - {analysis.issn}</title>
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
            
            /* Sidebar Navigation */
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
                box-shadow: 2px 0 10px rgba(0,0,0,0.1);
            }}
            .sidebar h3 {{
                margin-bottom: 20px;
                font-size: 18px;
                font-weight: 600;
                color: white;
                border-bottom: 2px solid rgba(255,255,255,0.3);
                padding-bottom: 15px;
            }}
            .sidebar a {{
                color: white;
                text-decoration: none;
                display: flex;
                align-items: center;
                gap: 12px;
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
            .sidebar .level-2 {{
                padding-left: 35px;
                font-size: 13px;
                opacity: 0.9;
            }}
            .sidebar .level-2:hover {{
                opacity: 1;
            }}
            
            .main-content {{
                margin-left: 280px;
                padding: 30px 40px;
            }}
            
            /* Header */
            .header {{
                background: linear-gradient(135deg, {primary} 0%, {secondary} 100%);
                color: white;
                padding: 40px;
                border-radius: 15px;
                margin-bottom: 30px;
                display: flex;
                align-items: center;
                justify-content: space-between;
            }}
            .header-left {{
                display: flex;
                align-items: center;
                gap: 20px;
            }}
            .header-logo {{
                max-height: 80px;
                max-width: 120px;
            }}
            .header-title h1 {{
                color: white;
                margin: 0;
                font-size: 28px;
            }}
            .header-title .subtitle {{
                opacity: 0.9;
                font-size: 14px;
                margin-top: 5px;
            }}
            .header-right {{
                display: flex;
                align-items: center;
                gap: 15px;
            }}
            .header-logo-journal {{
                max-height: 80px;
                max-width: 150px;
            }}
            
            /* Sections */
            .section {{
                background: white;
                border-radius: 15px;
                padding: 25px;
                margin-bottom: 30px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                scroll-margin-top: 20px;
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
            
            /* Metrics Grid */
            .metrics-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
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
            
            /* Tables */
            .table-container {{
                overflow-x: auto;
                max-height: 600px;
                overflow-y: auto;
                margin: 15px 0;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                font-family: 'Times New Roman', serif;
                font-size: 14px;
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
                vertical-align: middle;
            }}
            tr:hover {{
                background-color: #f5f5f5;
            }}
            
            /* Badges */
            .badge {{
                display: inline-block;
                padding: 3px 12px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: 600;
                margin: 2px;
            }}
            .badge-info {{ background: #d1ecf1; color: #0c5460; }}
            .badge-success {{ background: #d4edda; color: #155724; }}
            .badge-warning {{ background: #fff3cd; color: #856404; }}
            .badge-danger {{ background: #f8d7da; color: #721c24; }}
            
            /* Citation count */
            .citation-count {{
                font-weight: 600;
                color: {primary};
            }}
            
            /* Progress bars in metrics */
            .progress-bar-container {{
                width: 100%;
                background-color: #f0f0f0;
                border-radius: 10px;
                overflow: hidden;
                height: 8px;
                margin: 5px 0;
            }}
            .progress-bar-fill {{
                height: 100%;
                background: linear-gradient(90deg, {primary}, {secondary});
                border-radius: 10px;
                transition: width 0.5s ease;
            }}
            
            /* Word wrap */
            .word-wrap {{
                word-wrap: break-word;
                max-width: 300px;
            }}
            
            /* Filter section */
            .filter-section {{
                background: #f8f9fa;
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 20px;
            }}
            .filter-row {{
                display: flex;
                flex-wrap: wrap;
                gap: 15px;
                align-items: center;
            }}
            .filter-row label {{
                font-weight: 600;
                font-size: 13px;
                margin-right: 5px;
            }}
            .filter-row select, .filter-row input {{
                padding: 5px 10px;
                border-radius: 5px;
                border: 1px solid #ddd;
                font-size: 13px;
            }}
            
            /* Collapsible */
            .collapser {{
                cursor: pointer;
                transition: background 0.2s;
            }}
            .collapser:hover {{
                background: #e8e8e8 !important;
            }}
            
            /* Footer */
            .footer {{
                margin-top: 40px;
                padding-top: 20px;
                border-top: 1px solid #BDC3C7;
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
            
            /* Scroll bar styling */
            .table-container::-webkit-scrollbar {{
                width: 8px;
                height: 8px;
            }}
            .table-container::-webkit-scrollbar-track {{
                background: #f1f1f1;
                border-radius: 4px;
            }}
            .table-container::-webkit-scrollbar-thumb {{
                background: {primary};
                border-radius: 4px;
            }}
            .table-container::-webkit-scrollbar-thumb:hover {{
                background: {secondary};
            }}
            
            @media (max-width: 768px) {{
                .sidebar {{ display: none; }}
                .main-content {{ margin-left: 0; padding: 20px; }}
                .header {{ flex-direction: column; text-align: center; }}
                .metrics-grid {{ grid-template-columns: 1fr 1fr; }}
            }}
            @media print {{
                .sidebar {{ display: none; }}
                .main-content {{ margin-left: 0; }}
            }}
        </style>
    </head>
    <body>
        <div class="sidebar">
            <h3>📊 {t('journal_analysis_title')}</h3>
            <a href="#overview">📈 {t('overview')}</a>
            <a href="#analyzed_articles" class="level-2">📄 {t('analyzed_articles')}</a>
            <a href="#author_analysis" class="level-2">👤 {t('author_analysis')}</a>
            <a href="#top_affiliations" class="level-2">🏛️ {t('top_affiliations')}</a>
            <a href="#geographic_analysis" class="level-2">🌍 {t('geographic_analysis')}</a>
            <a href="#citation_analysis">📊 {t('citation_analysis')}</a>
            <a href="#citation_dynamics" class="level-2">📈 {t('citation_dynamics_by_year')}</a>
            <a href="#cumulative_citations" class="level-2">📊 {t('cumulative_citations')}</a>
            <a href="#heatmap" class="level-2">🔥 {t('citation_network_heatmap')}</a>
            <a href="#most_cited" class="level-2">⭐ {t('most_cited_publications')}</a>
            <a href="#citing_works">📚 {t('citing_works_analysis')}</a>
            <a href="#top_citing_authors" class="level-2">👤 {t('top_citing_authors')}</a>
            <a href="#top_citing_affiliations" class="level-2">🏛️ {t('top_citing_affiliations')}</a>
            <a href="#top_citing_countries" class="level-2">🌍 {t('top_citing_countries')}</a>
            <a href="#top_citing_journals" class="level-2">📰 {t('top_citing_journals')}</a>
            <a href="#top_citing_publishers" class="level-2">🏢 {t('top_citing_publishers')}</a>
            <a href="#topic_analysis">🏷️ {t('topic_analysis_section')}</a>
            <a href="#topic_trends" class="level-2">📊 {t('topic_trends')}</a>
            <a href="#top_cited_categories" class="level-2">⭐ {t('top_10_cited')}</a>
            <a href="#detailed_citations">📋 {t('detailed_citations_section')}</a>
            <a href="#all_publications">📚 {t('all_publications_section')}</a>
        </div>
        
        <div class="main-content">
            <!-- Header -->
            <div class="header">
                <div class="header-left">
                    {f'<img src="data:image/png;base64,{app_logo_base64}" class="header-logo" alt="App Logo">' if app_logo_base64 else ''}
                    <div class="header-title">
                        <h1>{t('journal_analysis_title')}</h1>
                        <div class="subtitle">ISSN: {analysis.issn} | {t('period')}: {analysis.period[0]} - {analysis.period[1]}</div>
                    </div>
                </div>
                <div class="header-right">
                    {f'<img src="data:image/png;base64,{logo_base64}" class="header-logo-journal" alt="Journal Logo">' if logo_base64 else ''}
                    <div style="text-align: right; font-size: 12px; opacity: 0.9;">
                        {datetime.now().strftime('%d.%m.%Y')}
                    </div>
                </div>
            </div>
            
            <!-- ============================================================ -->
            <!-- SECTION 1: OVERVIEW -->
            <!-- ============================================================ -->
            <div id="overview" class="section">
                <div class="section-title"><span class="icon">📈</span> {t('overview')}</div>
                
                <!-- Key Metrics -->
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-value">{metrics.total_publications}</div>
                        <div class="metric-label">{t('total_publications_label')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{metrics.total_citations:,}</div>
                        <div class="metric-label">{t('total_citations_label')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{metrics.h_index}</div>
                        <div class="metric-label">{t('h_index_label')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{metrics.g_index}</div>
                        <div class="metric-label">{t('g_index_label')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{metrics.i10_index}</div>
                        <div class="metric-label">{t('i10_index_label')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{metrics.i100_index}</div>
                        <div class="metric-label">{t('i100_index_label')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{metrics.avg_citations:.1f}</div>
                        <div class="metric-label">{t('avg_citations_label')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{metrics.open_access_percentage:.1f}%</div>
                        <div class="metric-label">{t('open_access_label')}</div>
                        <div class="progress-bar-container">
                            <div class="progress-bar-fill" style="width: {metrics.open_access_percentage}%;"></div>
                        </div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{metrics.active_years}</div>
                        <div class="metric-label">{t('active_years_label')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{metrics.unique_authors}</div>
                        <div class="metric-label">{t('unique_authors_label')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{metrics.unique_affiliations}</div>
                        <div class="metric-label">{t('unique_affiliations_label')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{metrics.unique_countries}</div>
                        <div class="metric-label">{t('unique_countries_label')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{metrics.avg_authors_per_paper:.1f}</div>
                        <div class="metric-label">{t('avg_authors_per_paper_label')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{metrics.avg_affiliations_per_paper:.1f}</div>
                        <div class="metric-label">{t('avg_affiliations_per_paper_label')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{metrics.avg_countries_per_paper:.1f}</div>
                        <div class="metric-label">{t('avg_countries_per_paper_label')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{metrics.international_collaboration_rate:.1f}%</div>
                        <div class="metric-label">{t('international_collaboration_rate_label')}</div>
                        <div class="progress-bar-container">
                            <div class="progress-bar-fill" style="width: {metrics.international_collaboration_rate}%;"></div>
                        </div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{metrics.unique_citing_authors}</div>
                        <div class="metric-label">{t('unique_citing_authors_label')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{metrics.unique_citing_affiliations}</div>
                        <div class="metric-label">{t('unique_citing_affiliations_label')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{metrics.unique_citing_countries}</div>
                        <div class="metric-label">{t('unique_citing_countries_label')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{metrics.unique_citing_journals}</div>
                        <div class="metric-label">{t('unique_citing_journals_label')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{metrics.unique_citing_publishers}</div>
                        <div class="metric-label">{t('unique_citing_publishers_label')}</div>
                    </div>
                </div>
                
                <!-- Open Access Breakdown -->
                <h3 style="color: {primary}; margin-top: 20px;">{t('open_access_breakdown')}</h3>
                <div style="display: flex; flex-wrap: wrap; gap: 20px; padding: 15px; background: #f8f9fa; border-radius: 8px;">
                    {oa_html}
                </div>
            </div>
            
            <!-- ============================================================ -->
            <!-- SECTION 2: ANALYZED ARTICLES -->
            <!-- ============================================================ -->
            <div id="analyzed_articles" class="section">
                <div class="section-title"><span class="icon">📄</span> {t('analyzed_articles')}</div>
                
                <!-- 5.1 Author Analysis -->
                <div id="author_analysis">
                    <h3 style="color: {primary};">{t('author_analysis')}</h3>
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
                                {author_html if author_html else '<tr><td colspan="7" style="text-align: center;">No data</td></tr>'}
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <!-- 5.2 Top Affiliations -->
                <div id="top_affiliations">
                    <h3 style="color: {primary}; margin-top: 25px;">{t('top_affiliations')}</h3>
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
                                {affil_html if affil_html else '<tr><td colspan="5" style="text-align: center;">No data</td></tr>'}
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <!-- 5.3 Geographic Analysis -->
                <div id="geographic_analysis">
                    <h3 style="color: {primary}; margin-top: 25px;">{t('geographic_analysis')}</h3>
                    
                    <!-- 5.3.1 Unique Countries per Publication -->
                    <h4 style="color: #555; margin-top: 15px;">{t('unique_countries_per_publication')}</h4>
                    <div style="display: flex; gap: 20px; flex-wrap: wrap; padding: 10px; background: #f8f9fa; border-radius: 8px;">
                        <div><strong>{t('average')}:</strong> {avg_countries:.2f}</div>
                        <div><strong>{t('max')}:</strong> {countries_per_pub.get('max', 0)}</div>
                        <div><strong>{t('total_publications_label')}:</strong> {len(articles)}</div>
                    </div>
                    
                    <!-- 5.3.2 Authors per Country -->
                    <h4 style="color: #555; margin-top: 15px;">{t('authors_per_country')}</h4>
                    <div class="table-container" style="max-height: 300px;">
                        <table>
                            <thead>
                                <tr>
                                    <th>{t('countries')}</th>
                                    <th>{t('authors')}</th>
                                </tr>
                            </thead>
                            <tbody>
                                {authors_per_country_html if authors_per_country_html else '<tr><td colspan="2" style="text-align: center;">No data</td></tr>'}
                            </tbody>
                        </table>
                    </div>
                    
                    <!-- 5.3.3 Collaboration Patterns -->
                    <h4 style="color: #555; margin-top: 15px;">{t('collaboration_patterns')}</h4>
                    <div style="display: flex; gap: 30px; flex-wrap: wrap; padding: 10px; background: #f8f9fa; border-radius: 8px;">
                        <div><strong>{t('single_country')}:</strong> {single_country} ({single_country/total_pubs*100:.1f}%)</div>
                        <div><strong>{t('international_collab')}:</strong> {international} ({international/total_pubs*100:.1f}%)</div>
                        <div><strong>{t('total_publications_label')}:</strong> {total_pubs}</div>
                    </div>
                    
                    <!-- 5.3.4 Collaboration Couples -->
                    <h4 style="color: #555; margin-top: 15px;">{t('collaboration_couples_section')}</h4>
                    <div class="table-container" style="max-height: 300px;">
                        <table>
                            <thead>
                                <tr>
                                    <th>{t('country_pairs')}</th>
                                    <th>{t('frequency')}</th>
                                </tr>
                            </thead>
                            <tbody>
                                {collab_couples_html if collab_couples_html else '<tr><td colspan="2" style="text-align: center;">No data</td></tr>'}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
            
            <!-- ============================================================ -->
            <!-- SECTION 3: CITATION ANALYSIS -->
            <!-- ============================================================ -->
            <div id="citation_analysis" class="section">
                <div class="section-title"><span class="icon">📊</span> {t('citation_analysis')}</div>
                
                <!-- 6.1 Citation Dynamics by Year -->
                <div id="citation_dynamics">
                    <h3 style="color: {primary};">{t('citation_dynamics_by_year')}</h3>
                    
                    <!-- First Citation Statistics -->
                    <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                        <h4 style="color: #555;">{t('first_citation_analysis')}</h4>
                        <div style="display: flex; gap: 20px; flex-wrap: wrap;">
                            <div><strong>{t('min_lag')}:</strong> {citation_dynamics.get('first_citation_stats', {}).get('min', 'N/A')} {t('years')}</div>
                            <div><strong>{t('max_lag')}:</strong> {citation_dynamics.get('first_citation_stats', {}).get('max', 'N/A')} {t('years')}</div>
                            <div><strong>{t('avg_lag')}:</strong> {citation_dynamics.get('first_citation_stats', {}).get('avg', 'N/A'):.1f} {t('years')}</div>
                            <div><strong>{t('median_lag')}:</strong> {citation_dynamics.get('first_citation_stats', {}).get('median', 'N/A')} {t('years')}</div>
                            <div><strong>{t('total_publications_label')}:</strong> {citation_dynamics.get('first_citation_stats', {}).get('count', 0)}</div>
                        </div>
                    </div>
                    
                    <div class="table-container" style="max-height: 400px;">
                        <table>
                            <thead>
                                <tr>
                                    <th>{t('publication_year_col')}</th>
                                    <th>{t('citation_year_col')}</th>
                                    <th>{t('citations_count_col')}</th>
                                </tr>
                            </thead>
                            <tbody>
                                {dynamics_html if dynamics_html else '<tr><td colspan="3" style="text-align: center;">No data</td></tr>'}
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <!-- 6.2 Cumulative Citations -->
                <div id="cumulative_citations">
                    <h3 style="color: {primary}; margin-top: 25px;">{t('cumulative_citations')}</h3>
                    <div class="table-container" style="max-height: 300px;">
                        <table>
                            <thead>
                                <tr>
                                    <th>{t('year')}</th>
                                    <th>{t('cumulative')}</th>
                                </tr>
                            </thead>
                            <tbody>
                                {cumulative_html if cumulative_html else '<tr><td colspan="2" style="text-align: center;">No data</td></tr>'}
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <!-- 6.3 Citation Network Heatmap -->
                <div id="heatmap">
                    <h3 style="color: {primary}; margin-top: 25px;">{t('citation_network_heatmap')}</h3>
                    <div style="overflow-x: auto;">
                        {heatmap_html if heatmap_html else '<p style="text-align: center; color: #666;">No data for heatmap</p>'}
                    </div>
                </div>
                
                <!-- 6.4 Most Cited Publications -->
                <div id="most_cited">
                    <h3 style="color: {primary}; margin-top: 25px;">{t('most_cited_publications')}</h3>
                    <div class="table-container" style="max-height: 400px;">
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
                                {most_cited_html if most_cited_html else '<tr><td colspan="7" style="text-align: center;">No data</td></tr>'}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
            
            <!-- ============================================================ -->
            <!-- SECTION 4: CITING WORKS ANALYSIS -->
            <!-- ============================================================ -->
            <div id="citing_works" class="section">
                <div class="section-title"><span class="icon">📚</span> {t('citing_works_analysis')}</div>
                
                <div style="display: flex; gap: 20px; flex-wrap: wrap; padding: 15px; background: #f8f9fa; border-radius: 8px; margin-bottom: 20px;">
                    <div><strong>{t('total_citing_works')}:</strong> {sum(len(c) for c in citing_works.values())}</div>
                    <div><strong>{t('unique_citing_authors_label')}:</strong> {metrics.unique_citing_authors}</div>
                    <div><strong>{t('unique_citing_affiliations_label')}:</strong> {metrics.unique_citing_affiliations}</div>
                    <div><strong>{t('unique_citing_countries_label')}:</strong> {metrics.unique_citing_countries}</div>
                    <div><strong>{t('unique_citing_journals_label')}:</strong> {metrics.unique_citing_journals}</div>
                    <div><strong>{t('unique_citing_publishers_label')}:</strong> {metrics.unique_citing_publishers}</div>
                </div>
                
                <!-- 7.1 Top Citing Authors -->
                <div id="top_citing_authors">
                    <h3 style="color: {primary};">{t('top_citing_authors')}</h3>
                    <div class="table-container" style="max-height: 300px;">
                        <table>
                            <thead>
                                <tr>
                                    <th>{t('rank')}</th>
                                    <th>{t('authors')}</th>
                                    <th>{t('citing_works')}</th>
                                </tr>
                            </thead>
                            <tbody>
                                {top_citing_authors_html if top_citing_authors_html else '<tr><td colspan="3" style="text-align: center;">No data</td></tr>'}
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <!-- 7.2 Top Citing Affiliations -->
                <div id="top_citing_affiliations">
                    <h3 style="color: {primary}; margin-top: 25px;">{t('top_citing_affiliations')}</h3>
                    <div class="table-container" style="max-height: 300px;">
                        <table>
                            <thead>
                                <tr>
                                    <th>{t('rank')}</th>
                                    <th>{t('affiliations')}</th>
                                    <th>{t('citing_works')}</th>
                                </tr>
                            </thead>
                            <tbody>
                                {top_citing_affils_html if top_citing_affils_html else '<tr><td colspan="3" style="text-align: center;">No data</td></tr>'}
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <!-- 7.3 Top Citing Countries -->
                <div id="top_citing_countries">
                    <h3 style="color: {primary}; margin-top: 25px;">{t('top_citing_countries')}</h3>
                    <div class="table-container" style="max-height: 300px;">
                        <table>
                            <thead>
                                <tr>
                                    <th>{t('rank')}</th>
                                    <th>{t('countries')}</th>
                                    <th>{t('citing_works')}</th>
                                </tr>
                            </thead>
                            <tbody>
                                {top_citing_countries_html if top_citing_countries_html else '<tr><td colspan="3" style="text-align: center;">No data</td></tr>'}
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <!-- 7.4 Top Citing Journals -->
                <div id="top_citing_journals">
                    <h3 style="color: {primary}; margin-top: 25px;">{t('top_citing_journals')}</h3>
                    <div class="table-container" style="max-height: 300px;">
                        <table>
                            <thead>
                                <tr>
                                    <th>{t('rank')}</th>
                                    <th>{t('journal')}</th>
                                    <th>{t('citing_works')}</th>
                                </tr>
                            </thead>
                            <tbody>
                                {top_citing_journals_html if top_citing_journals_html else '<tr><td colspan="3" style="text-align: center;">No data</td></tr>'}
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <!-- 7.5 Top Citing Publishers -->
                <div id="top_citing_publishers">
                    <h3 style="color: {primary}; margin-top: 25px;">{t('top_citing_publishers')}</h3>
                    <div class="table-container" style="max-height: 300px;">
                        <table>
                            <thead>
                                <tr>
                                    <th>{t('rank')}</th>
                                    <th>{t('publishers')}</th>
                                    <th>{t('citing_works')}</th>
                                </tr>
                            </thead>
                            <tbody>
                                {top_citing_publishers_html if top_citing_publishers_html else '<tr><td colspan="3" style="text-align: center;">No data</td></tr>'}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
            
            <!-- ============================================================ -->
            <!-- SECTION 5: TOPICS ANALYSIS -->
            <!-- ============================================================ -->
            <div id="topic_analysis" class="section">
                <div class="section-title"><span class="icon">🏷️</span> {t('topic_analysis_section')}</div>
                
                <!-- 8.1 Topics -->
                <div id="topic_trends">
                    <h3 style="color: {primary};">{t('topic_trends')}</h3>
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
                                {topics_html if topics_html else '<tr><td colspan="8" style="text-align: center;">No data</td></tr>'}
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <!-- 8.2 Top 10 most cited -->
                <div id="top_cited_categories">
                    <h3 style="color: {primary}; margin-top: 25px;">{t('top_10_cited')}</h3>
                    
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                        <div>
                            <h4 style="color: #555;">{t('subtopics')}</h4>
                            <div class="table-container" style="max-height: 300px;">
                                <table>
                                    <thead><tr><th>{t('subtopics')}</th><th>{t('citations')}</th></tr></thead>
                                    <tbody>{top_subtopics_html if top_subtopics_html else '<tr><td colspan="2" style="text-align: center;">No data</td></tr>'}</tbody>
                                </table>
                            </div>
                        </div>
                        <div>
                            <h4 style="color: #555;">{t('fields')}</h4>
                            <div class="table-container" style="max-height: 300px;">
                                <table>
                                    <thead><tr><th>{t('fields')}</th><th>{t('citations')}</th></tr></thead>
                                    <tbody>{top_fields_html if top_fields_html else '<tr><td colspan="2" style="text-align: center;">No data</td></tr>'}</tbody>
                                </table>
                            </div>
                        </div>
                        <div>
                            <h4 style="color: #555;">{t('domains')}</h4>
                            <div class="table-container" style="max-height: 300px;">
                                <table>
                                    <thead><tr><th>{t('domains')}</th><th>{t('citations')}</th></tr></thead>
                                    <tbody>{top_domains_html if top_domains_html else '<tr><td colspan="2" style="text-align: center;">No data</td></tr>'}</tbody>
                                </table>
                            </div>
                        </div>
                        <div>
                            <h4 style="color: #555;">{t('concepts')}</h4>
                            <div class="table-container" style="max-height: 300px;">
                                <table>
                                    <thead><tr><th>{t('concepts')}</th><th>{t('citations')}</th></tr></thead>
                                    <tbody>{top_concepts_html if top_concepts_html else '<tr><td colspan="2" style="text-align: center;">No data</td></tr>'}</tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- ============================================================ -->
            <!-- SECTION 6: DETAILED CITATIONS -->
            <!-- ============================================================ -->
            <div id="detailed_citations" class="section">
                <div class="section-title"><span class="icon">📋</span> {t('detailed_citations_section')}</div>
                {detailed_citations_html if detailed_citations_html else '<p style="text-align: center; color: #666;">No citations data available</p>'}
            </div>
            
            <!-- ============================================================ -->
            <!-- SECTION 7: ALL PUBLICATIONS -->
            <!-- ============================================================ -->
            <div id="all_publications" class="section">
                <div class="section-title"><span class="icon">📚</span> {t('all_publications_section')}</div>
                
                <!-- Filters -->
                <div class="filter-section">
                    <div class="filter-row">
                        <div>
                            <label for="yearFilter">{t('filter_by_year')}:</label>
                            <select id="yearFilter" onchange="filterPublications()">
                                {year_filter_options}
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
                            <label for="affilFilter">{t('filter_by_affiliations')}:</label>
                            <input type="text" id="affilFilter" placeholder="Affiliation..." onkeyup="filterPublications()">
                        </div>
                        <div>
                            <label for="citationFilter">{t('filter_by_citations_min')}:</label>
                            <input type="number" id="citationFilter" placeholder="Min citations..." min="0" onchange="filterPublications()">
                        </div>
                        <div>
                            <span id="visibleCount" style="font-weight: 500; color: {primary};">Showing all {len(articles)} publications</span>
                        </div>
                    </div>
                </div>
                
                <!-- Table -->
                <div class="table-container" style="max-height: 600px;">
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
                            </tr>
                        </thead>
                        <tbody>
                            {all_publications_html if all_publications_html else '<tr><td colspan="8" style="text-align: center;">No publications found</td></tr>'}
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
        
        <script>
            // Toggle citations function
            function toggleCitations(id) {{
                var elem = document.getElementById('citations_' + id);
                if (elem) {{
                    if (elem.style.display === 'none' || elem.style.display === '') {{
                        elem.style.display = 'block';
                        // Change arrow
                        var parent = elem.previousElementSibling;
                        if (parent) {{
                            var arrow = parent.querySelector('span:last-child');
                            if (arrow) arrow.innerHTML = '▲ {t("show_citations")}';
                        }}
                    }} else {{
                        elem.style.display = 'none';
                        var parent = elem.previousElementSibling;
                        if (parent) {{
                            var arrow = parent.querySelector('span:last-child');
                            if (arrow) arrow.innerHTML = '▼ {t("show_citations")}';
                        }}
                    }}
                }}
            }}
            
            // Filter publications
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
                    var authors = row.getAttribute('data-authors').toLowerCase();
                    var affiliations = row.getAttribute('data-affiliations').toLowerCase();
                    var citations = parseInt(row.getAttribute('data-citations')) || 0;
                    var title = row.getAttribute('data-title').toLowerCase();
                    
                    var show = true;
                    
                    if (yearFilter && year != yearFilter) show = false;
                    if (titleFilter && !title.includes(titleFilter)) show = false;
                    if (authorFilter && !authors.includes(authorFilter)) show = false;
                    if (affilFilter && !affiliations.includes(affilFilter)) show = false;
                    if (citations < citationFilter) show = false;
                    
                    if (show) {{
                        row.style.display = '';
                        visible++;
                    }} else {{
                        row.style.display = 'none';
                    }}
                }});
                
                var countElem = document.getElementById('visibleCount');
                if (countElem) {{
                    var total = rows.length;
                    countElem.textContent = '{t("filtered_count", count="")}'.replace('{count}', visible) + ' / ' + total + ' {t("publications")}';
                }}
            }}
            
            // Sort table
            var sortDirection = [true, true, true, true, true, true, true];
            
            function sortTable(col) {{
                var table = document.getElementById('publicationsTable');
                var tbody = table.querySelector('tbody');
                var rows = Array.from(tbody.querySelectorAll('tr'));
                
                sortDirection[col] = !sortDirection[col];
                var direction = sortDirection[col] ? 1 : -1;
                
                rows.sort(function(a, b) {{
                    var valA = a.cells[col].textContent.trim();
                    var valB = b.cells[col].textContent.trim();
                    
                    // Check if numeric
                    if (!isNaN(valA) && !isNaN(valB)) {{
                        return direction * (parseFloat(valA) - parseFloat(valB));
                    }}
                    return direction * valA.localeCompare(valB);
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

# ============================================
# MAIN STREAMLIT APPLICATION
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
    if 'journal_logo_base64' not in st.session_state:
        st.session_state.journal_logo_base64 = None
    if 'app_logo_base64' not in st.session_state:
        st.session_state.app_logo_base64 = None
    if 'analysis_result' not in st.session_state:
        st.session_state.analysis_result = None
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
    # Load app logo
    app_logo_base64 = None
    if os.path.exists("logo.png"):
        try:
            with open("logo.png", "rb") as f:
                app_logo_base64 = base64.b64encode(f.read()).decode()
                st.session_state.app_logo_base64 = app_logo_base64
        except Exception as e:
            if SHOW_DEBUG_LOGS:
                print(f"⚠️ Error loading app logo: {e}")
    
    # Header with logo
    col_logo, col_title = st.columns([1, 5])
    with col_logo:
        if app_logo_base64:
            st.image(f"data:image/png;base64,{app_logo_base64}", width=150)
        else:
            st.markdown("📊")
    with col_title:
        st.markdown(f"# {t('journal_analysis_title')}")
    
    st.markdown("---")
    
    # Input section
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        issn_input = st.text_input(
            t('issn'),
            placeholder="0028-0836",
            help=t('enter_issn')
        )
    
    with col2:
        period_input = st.text_input(
            t('period'),
            placeholder="2020-2023",
            help=t('enter_period')
        )
    
    with col3:
        journal_logo_upload = st.file_uploader(
            t('upload_logo'),
            type=['png', 'jpg', 'jpeg', 'svg'],
            help=t('logo_help')
        )
        
        if journal_logo_upload:
            try:
                logo_bytes = journal_logo_upload.read()
                st.session_state.journal_logo_base64 = base64.b64encode(logo_bytes).decode()
                st.success("✅ " + t('logo_help').split(':')[0])
            except Exception as e:
                st.warning(f"⚠️ Error loading logo: {e}")
    
    # Analyze button
    if st.button(t('analyze_journal'), type="primary", use_container_width=True):
        issn = issn_input.strip()
        period_str = period_input.strip()
        
        if not issn:
            st.error(t('invalid_issn'))
        elif not is_valid_issn(issn):
            st.error(t('invalid_issn'))
        elif not period_str:
            st.error(t('invalid_period'))
        else:
            try:
                period = parse_period(period_str)
                if isinstance(period, tuple) and len(period) == 2:
                    period_tuple = period
                else:
                    # If years list, use min and max
                    if isinstance(period, tuple) and len(period) > 2:
                        period_tuple = (min(period), max(period))
                    else:
                        period_tuple = (period, period) if isinstance(period, int) else (2020, 2023)
            except:
                st.error(t('invalid_period'))
                st.stop()
            
            # Check cache
            cached_data = load_from_cache(issn, period_str)
            if cached_data:
                st.info("📦 " + t('use_cache') + " - " + t('loading_data'))
                # For now, we'll re-run analysis but in production we'd load from cache
                # This is simplified - in real implementation we'd store the full analysis object
            
            # Progress tracking
            progress_container = st.empty()
            status_container = st.empty()
            progress_bar = st.progress(0, text=t('starting_analysis'))
            
            def progress_callback(stage: int, total_stages: int, current: int, total: int, stage_key: str, message: str):
                """Update progress bar during analysis"""
                stage_names = {
                    'stage_1': t('stage_1'),
                    'stage_2': t('stage_2'),
                    'stage_3': t('stage_3'),
                    'stage_4': t('stage_4'),
                    'stage_5': t('stage_5')
                }
                
                stage_name = stage_names.get(stage_key, f"{t('stage')} {stage}/{total_stages}")
                
                # Calculate overall progress
                base_progress = (stage - 1) / total_stages * 100
                stage_progress = (current / total) if total > 0 else 0
                overall_progress = base_progress + (stage_progress / total_stages * 100)
                
                progress_bar.progress(min(overall_progress / 100, 0.99))
                
                if total and total > 0:
                    status_container.info(f"**{stage_name}** ({current}/{total}) - {message}")
                else:
                    status_container.info(f"**{stage_name}** - {message}")
            
            # Run analysis
            try:
                st.info("🚀 " + t('starting_analysis'))
                
                analyzer = JournalAnalyzer(issn, period_tuple)
                
                # Check cache again after analysis
                analysis_result = analyzer.run_analysis(progress_callback)
                
                if not analysis_result.articles:
                    st.error(t('journal_not_found'))
                    progress_bar.empty()
                    st.stop()
                
                # Store result
                st.session_state.analysis_result = analysis_result
                st.session_state.analysis_complete = True
                
                # Generate HTML report
                progress_bar.progress(0.99, text=t('generating_report_label'))
                status_container.info("📄 " + t('generating_report'))
                
                theme_colors = {
                    'primary': st.session_state.primary_color,
                    'secondary': st.session_state.secondary_color
                }
                
                html_report = generate_html_report_journal(
                    analysis_result,
                    st.session_state.journal_logo_base64,
                    st.session_state.app_logo_base64,
                    theme_colors,
                    current_lang
                )
                
                st.session_state.html_report = html_report
                
                progress_bar.progress(1.0, text=t('analysis_complete_label'))
                status_container.success("✅ " + t('analysis_complete_label'))
                
                st.success(f"✅ {t('analysis_complete_label')} {len(analysis_result.articles)} {t('articles')}, {sum(len(c) for c in analysis_result.citing_works.values())} {t('citing_works')}")
                
                # Save to cache
                # In production, we would save the full analysis object
                # For now, we save the metrics
                cache_data = {
                    'issn': issn,
                    'period': period_str,
                    'total_publications': analysis_result.metrics.total_publications if analysis_result.metrics else 0,
                    'total_citations': analysis_result.metrics.total_citations if analysis_result.metrics else 0,
                    'h_index': analysis_result.metrics.h_index if analysis_result.metrics else 0,
                    'timestamp': datetime.now().isoformat()
                }
                save_to_cache(issn, period_str, cache_data)
                
                # Update session state for reports
                st.session_state['analysis_result'] = analysis_result
                
            except Exception as e:
                st.error(f"❌ {t('error_occurred')}: {str(e)}")
                import traceback
                st.code(traceback.format_exc())
            finally:
                progress_bar.empty()
                status_container.empty()
    
    # Display results if analysis is complete
    if st.session_state.analysis_complete and st.session_state.analysis_result:
        analysis_result = st.session_state.analysis_result
        html_report = st.session_state.html_report
        
        st.markdown("---")
        st.markdown(f"## {t('html_report')}")
        
        # Download button
        filename = f"journal_analysis_{analysis_result.issn}_{analysis_result.period[0]}-{analysis_result.period[1]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        
        if html_report:
            st.download_button(
                label="💾 " + t('download_html_report'),
                data=html_report.encode('utf-8'),
                file_name=filename,
                mime="text/html",
                use_container_width=True
            )
        
        # Preview
        st.markdown(f"### {t('report_preview')}")
        st.info(t('download_hint'))
        
        if html_report:
            # Show preview in iframe
            st.components.v1.html(html_report, height=800, scrolling=True)
        else:
            st.warning(t('generating_report'))

if __name__ == "__main__":
    main()
