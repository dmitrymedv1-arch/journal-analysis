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
MAX_CITING_PER_PAPER = 300  # Максимум цитирующих статей на одну статью

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
from threading import Lock
import math
from itertools import combinations
import difflib
from dataclasses import dataclass, field
from typing import List, Set, Dict, Optional, Any
import random
from IPython.display import display, HTML, clear_output
import ipywidgets as widgets
from tqdm import tqdm

# ============================================
# СЛОВАРЬ ПЕРЕВОДОВ (РАСШИРЕННЫЙ)
# ============================================

LANG = {
    'en': {
        # Существующие ключи из исходного кода
        'app_title': 'Author Profile Analysis',
        'app_icon': '🔬',
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
        'footer': '© Author Profile Analysis / Created by daM / Chimica Techno Acta',
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
        
        # ====== НОВЫЕ КЛЮЧИ ДЛЯ АНАЛИЗА ЖУРНАЛОВ ======
        'app_logo': 'Advanced Journal Analysis Tool',
        'journal_analysis': 'Journal Analysis',
        'issn_input': 'ISSN',
        'issn_placeholder': '0028-0836',
        'period_input': 'Period',
        'period_placeholder': '2020-2026 or 2020,2021,2022',
        'analyze_button': '🔍 Analyze Journal',
        'download_report': '💾 Download HTML Report',
        'stop_analysis': '⏹️ Stop Analysis',
        'analysis_stopped': '⏹️ Analysis stopped by user',
        'stage_1': '1. Collecting DOIs of journal articles',
        'stage_2': '2. Collecting citing DOIs (parallel)',
        'stage_3': '3. Enriching analyzed papers with metadata',
        'stage_4': '4. Enriching citing papers with metadata',
        'stage_5': '5. Analyzing data and generating HTML report',
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
        'diamond': 'Diamond',
        'author_analysis': 'Author Analysis',
        'rank': 'Rank',
        'authors': 'Authors',
        'publications_count': 'Publications',
        'citations_count': 'Citations',
        'top_affiliations': 'Top Affiliations',
        'geographic_analysis': 'Geographic Analysis',
        'unique_countries_per_publication': 'Unique Countries per Publication (Collaboration Level)',
        'authors_per_country': 'Authors per Country (Individual Distribution)',
        'collaboration_patterns': 'Collaboration Patterns',
        'collaboration_couples': 'Collaboration Couples',
        'country_pair': 'Country Pair',
        'frequency': 'Frequency',
        'citation_analysis': 'Citation Analysis',
        'citation_dynamics_by_year': 'Citation Dynamics by Year',
        'publication_year': 'Publication Year',
        'citation_year': 'Citation Year',
        'citations_count': 'Citations Count',
        'first_citation_analysis': 'First Citation Analysis',
        'min_days': 'Min (days)',
        'max_days': 'Max (days)',
        'avg_days': 'Avg (days)',
        'median_days': 'Median (days)',
        'cumulative_citations': 'Cumulative Citations',
        'citation_network_heatmap': 'Citation Network Heatmap',
        'most_cited_publications': 'Most Cited Publications',
        'title': 'Title',
        'year': 'Year',
        'citations': 'Citations',
        'citations_per_year': 'Citations/Year',
        'citing_works_analysis': 'Citing Works Analysis',
        'total_citing_works': 'Total Citing Works',
        'top_citing_authors': 'Top Citing Authors',
        'top_citing_affiliations': 'Top Citing Affiliations',
        'top_citing_countries': 'Top Citing Countries',
        'top_citing_journals': 'Top Citing Journals',
        'top_citing_publishers': 'Top Citing Publishers',
        'topics_analysis': 'Topics Analysis',
        'topics_overview': 'Topics Overview',
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
        'detailed_citations': 'Detailed Citations for Analyzed Works',
        'show_citations': 'Show Citations',
        'hide_citations': 'Hide Citations',
        'citing_journal': 'Citing Journal',
        'citing_year': 'Citing Year',
        'citing_date': 'Citing Date',
        'citation_lag': 'Citation Lag (years)',
        'authors': 'Authors',
        'countries': 'Countries',
        'topics': 'Topics',
        'all_publications': 'All Publications',
        'filter_by_title': 'Filter by Title Word(s)',
        'filter_by_year': 'Filter by Year',
        'filter_by_author': 'Filter by Author',
        'filter_by_affiliation': 'Filter by Affiliations',
        'filter_by_citations': 'Filter by Citations (min):',
        'search_publications': 'Search Publications',
        'show_all': 'Show All',
        'no_results': 'No results found',
        'apply_filter': 'Apply Filter',
        'clear_filters': 'Clear Filters',
        'single_country': 'Single-country',
        'international': 'International',
        'overview': 'Overview',
        'analyzed_articles': 'Analyzed Articles',
        'citing_works': 'Citing Works',
        'metrics_overview': 'Metrics Overview',
        'citation_dynamics': 'Citation Dynamics',
        'citation_network': 'Citation Network',
        'all_publications_table': 'All Publications',
        'data_source': 'Data source: OpenAlex',
        'generated': 'Generated',
        'journal_issn': 'Journal ISSN',
        'period': 'Period',
        'analysis_details': 'Analysis Details',
    },
    'ru': {
        # Существующие ключи из исходного кода (русские переводы)
        'app_title': 'Анализ профиля ученого',
        'app_icon': '🔬',
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
        'footer': '© Author Profile Analysis / Created by daM / Chimica Techno Acta',
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
        
        # ====== НОВЫЕ КЛЮЧИ ДЛЯ АНАЛИЗА ЖУРНАЛОВ (РУССКИЙ) ======
        'app_logo': 'Advanced Journal Analysis Tool',
        'journal_analysis': 'Анализ журнала',
        'issn_input': 'ISSN',
        'issn_placeholder': '0028-0836',
        'period_input': 'Период',
        'period_placeholder': '2020-2026 или 2020,2021,2022',
        'analyze_button': '🔍 Анализировать журнал',
        'download_report': '💾 Скачать HTML отчет',
        'stop_analysis': '⏹️ Остановить анализ',
        'analysis_stopped': '⏹️ Анализ остановлен пользователем',
        'stage_1': '1. Сбор DOI статей журнала',
        'stage_2': '2. Сбор цитирующих DOI (параллельно)',
        'stage_3': '3. Обогащение анализируемых статей метаданными',
        'stage_4': '4. Обогащение цитирующих статей метаданными',
        'stage_5': '5. Анализ данных и генерация HTML отчета',
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
        'gold': 'Золотой',
        'hybrid': 'Гибридный',
        'green': 'Зеленый',
        'bronze': 'Бронзовый',
        'closed': 'Закрытый',
        'unknown': 'Неизвестный',
        'diamond': 'Алмазный',
        'author_analysis': 'Анализ авторов',
        'rank': 'Ранг',
        'authors': 'Авторы',
        'publications_count': 'Публикаций',
        'citations_count': 'Цитирований',
        'top_affiliations': 'Топ аффилиаций',
        'geographic_analysis': 'Географический анализ',
        'unique_countries_per_publication': 'Уникальные страны на публикацию (уровень коллаборации)',
        'authors_per_country': 'Авторы по странам (индивидуальное распределение)',
        'collaboration_patterns': 'Паттерны коллабораций',
        'collaboration_couples': 'Пары стран-коллаборантов',
        'country_pair': 'Пара стран',
        'frequency': 'Частота',
        'citation_analysis': 'Анализ цитирований',
        'citation_dynamics_by_year': 'Динамика цитирований по годам',
        'publication_year': 'Год публикации',
        'citation_year': 'Год цитирования',
        'citations_count': 'Количество цитирований',
        'first_citation_analysis': 'Анализ первого цитирования',
        'min_days': 'Мин (дней)',
        'max_days': 'Макс (дней)',
        'avg_days': 'Среднее (дней)',
        'median_days': 'Медиана (дней)',
        'cumulative_citations': 'Накопленные цитирования',
        'citation_network_heatmap': 'Тепловая карта сети цитирований',
        'most_cited_publications': 'Самые цитируемые публикации',
        'citations_per_year': 'Цитирований/год',
        'citing_works_analysis': 'Анализ цитирующих работ',
        'total_citing_works': 'Всего цитирующих работ',
        'top_citing_authors': 'Топ цитирующих авторов',
        'top_citing_affiliations': 'Топ цитирующих аффилиаций',
        'top_citing_countries': 'Топ цитирующих стран',
        'top_citing_journals': 'Топ цитирующих журналов',
        'top_citing_publishers': 'Топ цитирующих издательств',
        'topics_analysis': 'Тематический анализ',
        'topics_overview': 'Обзор тем',
        'analyzed_count': 'Анализируемых',
        'citing_count': 'Цитирующих',
        'analyzed_norm_count': 'Норм. анализируемых',
        'citing_norm_count': 'Норм. цитирующих',
        'total_norm_count': 'Общий норм.',
        'first_year': 'Первый год',
        'peak_year': 'Пиковый год',
        'top_cited_topics': 'Топ цитируемых тем',
        'top_cited_subtopics': 'Топ цитируемых подтем',
        'top_cited_fields': 'Топ цитируемых областей',
        'top_cited_domains': 'Топ цитируемых доменов',
        'top_cited_concepts': 'Топ цитируемых концептов',
        'detailed_citations': 'Детальные цитирования для анализируемых работ',
        'show_citations': 'Показать цитирования',
        'hide_citations': 'Скрыть цитирования',
        'citing_journal': 'Цитирующий журнал',
        'citing_year': 'Год цитирования',
        'citing_date': 'Дата цитирования',
        'citation_lag': 'Задержка цитирования (лет)',
        'authors': 'Авторы',
        'countries': 'Страны',
        'topics': 'Темы',
        'all_publications': 'Все публикации',
        'filter_by_title': 'Фильтр по словам в названии',
        'filter_by_year': 'Фильтр по году',
        'filter_by_author': 'Фильтр по автору',
        'filter_by_affiliation': 'Фильтр по аффилиации',
        'filter_by_citations': 'Фильтр по цитированиям (мин):',
        'search_publications': 'Поиск публикаций',
        'show_all': 'Показать все',
        'no_results': 'Результатов не найдено',
        'apply_filter': 'Применить фильтр',
        'clear_filters': 'Очистить фильтры',
        'single_country': 'Однострановые',
        'international': 'Международные',
        'overview': 'Обзор',
        'analyzed_articles': 'Анализируемые статьи',
        'citing_works': 'Цитирующие работы',
        'metrics_overview': 'Обзор метрик',
        'citation_dynamics': 'Динамика цитирований',
        'citation_network': 'Сеть цитирований',
        'all_publications_table': 'Все публикации',
        'data_source': 'Источник данных: OpenAlex',
        'generated': 'Сгенерирован',
        'journal_issn': 'ISSN журнала',
        'period': 'Период',
        'analysis_details': 'Детали анализа',
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
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================

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

def get_cache_path(issn: str, period: str) -> str:
    """Возвращает путь к файлу кэша для ISSN и периода"""
    key = f"{issn}_{period}".replace('-', '_').replace(',', '_').replace(' ', '')
    if not os.path.exists('journal_cache'):
        os.makedirs('journal_cache')
    return f"journal_cache/{key}.json"

def load_from_cache(issn: str, period: str) -> Optional[Dict]:
    """Загружает данные из кэша"""
    if not USE_CACHE:
        return None
    
    cache_path = get_cache_path(issn, period)
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

def save_to_cache(issn: str, period: str, data: Dict):
    """Сохраняет данные в кэш"""
    if not USE_CACHE:
        return
    
    cache_path = get_cache_path(issn, period)
    try:
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        if SHOW_DEBUG_LOGS:
            print(f"✅ Данные сохранены в кэш: {cache_path}")
    except Exception as e:
        if SHOW_DEBUG_LOGS:
            print(f"⚠️ Ошибка сохранения кэша: {e}")

def normalize_issn(issn_str: str) -> str:
    """Нормализует ISSN к формату XXXX-XXXX"""
    cleaned = re.sub(r'[^0-9Xx]', '', str(issn_str).strip())
    if len(cleaned) == 8:
        return f"{cleaned[:4]}-{cleaned[4:]}".upper()
    return cleaned.upper()

def extract_country_from_affiliation(affiliation: str) -> str:
    """Извлекает страну из названия аффилиации"""
    countries = [
        'USA', 'UK', 'China', 'Germany', 'France', 'Japan', 'Russia', 'Italy', 
        'Canada', 'Australia', 'Spain', 'Brazil', 'India', 'Netherlands', 'Switzerland',
        'South Korea', 'Sweden', 'Belgium', 'Poland', 'Austria', 'Norway', 'Denmark',
        'Finland', 'Ireland', 'Portugal', 'Greece', 'Czech Republic', 'Hungary',
        'New Zealand', 'South Africa', 'Argentina', 'Mexico', 'Chile', 'Colombia',
        'United States', 'United Kingdom', 'England', 'Scotland', 'Wales',
        'Saudi Arabia', 'UAE', 'Turkey', 'Iran', 'Pakistan', 'Egypt', 'Nigeria',
        'Kenya', 'Singapore', 'Malaysia', 'Thailand', 'Vietnam', 'Indonesia',
        'Philippines', 'Taiwan', 'Hong Kong', 'Korea', 'Switzerland', 'Austria',
        'Czechia', 'Slovakia', 'Hungary', 'Romania', 'Bulgaria', 'Greece',
        'Cyprus', 'Malta', 'Luxembourg', 'Iceland', 'Estonia', 'Latvia', 'Lithuania',
        'Slovenia', 'Croatia', 'Bosnia', 'Serbia', 'Montenegro', 'North Macedonia',
        'Albania', 'Moldova', 'Ukraine', 'Belarus', 'Armenia', 'Azerbaijan',
        'Georgia', 'Kazakhstan', 'Uzbekistan', 'Turkmenistan', 'Kyrgyzstan',
        'Tajikistan', 'Mongolia', 'Nepal', 'Sri Lanka', 'Bangladesh', 'Myanmar',
        'Cambodia', 'Laos', 'Brunei', 'Papua New Guinea', 'New Zealand',
        'Fiji', 'Samoa', 'Tonga', 'Vanuatu', 'Solomon Islands'
    ]
    
    for country in countries:
        if country.lower() in affiliation.lower():
            return country
    return "Unknown"

def safe_get_text(data: Dict, *keys, default: str = "") -> str:
    """Безопасное получение текстового значения из вложенного словаря"""
    for key in keys:
        if isinstance(data, dict):
            data = data.get(key, default)
        else:
            return default
    if data is None:
        return default
    return str(data)

# ============================================
# КЛАССЫ ДАННЫХ
# ============================================

@dataclass
class Author:
    """Класс для хранения информации об авторе"""
    display_name: str
    orcid: Optional[str] = None
    affiliations: List[str] = field(default_factory=list)
    countries: List[str] = field(default_factory=list)
    institution_ids: List[str] = field(default_factory=list)

@dataclass
class Topic:
    """Класс для хранения информации о теме"""
    display_name: str
    subfield: Optional[str] = None
    field: Optional[str] = None
    domain: Optional[str] = None
    score: float = 0.0

@dataclass
class Concept:
    """Класс для хранения информации о концепте"""
    display_name: str
    level: int = 0
    score: float = 0.0

@dataclass
class AnalyzedPaper:
    """Класс для хранения информации об анализируемой статье"""
    id: str
    doi: str
    title: str
    year: int
    cited_by_count: int
    open_access_status: str
    is_oa: bool
    authors: List[Author] = field(default_factory=list)
    affiliations: List[str] = field(default_factory=list)
    countries: List[str] = field(default_factory=list)
    journal: str = ""
    publisher: str = ""
    topics: List[Topic] = field(default_factory=list)
    concepts: List[Concept] = field(default_factory=list)
    fields: List[str] = field(default_factory=list)
    domains: List[str] = field(default_factory=list)
    publication_date: str = ""
    citing_dois: List[str] = field(default_factory=list)
    citations: List['CitingPaper'] = field(default_factory=list)

@dataclass
class CitingPaper:
    """Класс для хранения информации о цитирующей статье"""
    id: str
    doi: str
    title: str
    year: int
    publication_date: str
    journal: str
    publisher: str
    authors: List[Author] = field(default_factory=list)
    affiliations: List[str] = field(default_factory=list)
    countries: List[str] = field(default_factory=list)
    topics: List[Topic] = field(default_factory=list)
    concepts: List[Concept] = field(default_factory=list)
    fields: List[str] = field(default_factory=list)
    domains: List[str] = field(default_factory=list)

# ============================================
# ФУНКЦИИ ДЛЯ РАБОТЫ С API (ПАРАЛЛЕЛЬНЫЕ)
# ============================================

# Глобальная блокировка для потокобезопасных запросов
lock = Lock()
stop_analysis_flag = False

def set_stop_flag(value: bool):
    """Устанавливает флаг остановки анализа"""
    global stop_analysis_flag
    stop_analysis_flag = value

def get_stop_flag() -> bool:
    """Возвращает состояние флага остановки"""
    global stop_analysis_flag
    return stop_analysis_flag

def smart_get(url: str, params: Dict = None, retries: int = MAX_RETRIES) -> Optional[Dict]:
    """Выполняет GET запрос с защитой от rate limiting и повторными попытками"""
    for attempt in range(retries):
        # Проверяем флаг остановки
        if get_stop_flag():
            if SHOW_DEBUG_LOGS:
                print("⏹️ Запрос прерван пользователем")
            return None
        
        try:
            with lock:
                time.sleep(random.uniform(0.1, BASE_DELAY))
            
            response = requests.get(url, params=params, timeout=TIMEOUT)
            
            if response.status_code == 429:
                wait = int(response.headers.get("Retry-After", 2 ** attempt + 1))
                if SHOW_DEBUG_LOGS:
                    print(f"⚠️ Rate limit, ждем {wait} сек...")
                time.sleep(wait + random.uniform(0.5, 1.5))
                continue
                
            if response.status_code == 200:
                return response.json()
            
            if SHOW_DEBUG_LOGS:
                print(f"⚠️ Ошибка {response.status_code} для {url}")
            time.sleep(1 * (2 ** attempt))
            
        except Exception as e:
            if SHOW_DEBUG_LOGS:
                print(f"⚠️ Попытка {attempt+1}/{retries} ошибка: {str(e)[:100]}")
            if attempt < retries - 1:
                time.sleep(1.5 * (2 ** attempt))
            else:
                return None
    
    return None

def get_citing_dois(oa_id: str, progress_callback: Optional[callable] = None) -> List[str]:
    """Параллельная функция получения цитирующих DOI для одной статьи"""
    if get_stop_flag():
        return []
    
    citing = []
    cursor = "*"
    base_url = "https://api.openalex.org/works"
    
    for _ in range(8):  # ограничение пагинации
        if get_stop_flag():
            break
            
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

ddef get_metadata_for_dois_parallel(dois: List[str], 
                                   progress_callback: Optional[callable] = None,
                                   stop_callback: Optional[callable] = None,
                                   max_workers: int = MAX_WORKERS) -> Dict[str, Dict]:
    """
    Параллельно получает метаданные для списка DOI из OpenAlex.
    """
    if not dois:
        return {}
    
    result = {}
    result_lock = Lock()
    total = len(dois)
    processed = 0
    
    if SHOW_DEBUG_LOGS:
        print(f"⚡ Параллельное получение метаданных для {total} DOI ({max_workers} потоков)...")
    
    def fetch_one(doi: str) -> Tuple[str, Optional[Dict]]:
        """Получает метаданные для одного DOI"""
        if stop_callback and stop_callback():
            return doi, None
        
        base_url = "https://api.openalex.org/works"
        
        # Пробуем найти по DOI
        params = {"filter": f"doi:{doi}", "per_page": 1}
        data = smart_get(base_url, params)
        
        if data and data.get("results"):
            return doi, data["results"][0]
        
        # Пробуем найти по ID
        params = {"filter": f"id:https://doi.org/{doi}", "per_page": 1}
        data = smart_get(base_url, params)
        
        if data and data.get("results"):
            return doi, data["results"][0]
        
        return doi, None
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Отправляем все задачи
        futures = {executor.submit(fetch_one, doi): doi for doi in dois}
        
        # Обрабатываем результаты по мере завершения
        for future in as_completed(futures):
            if stop_callback and stop_callback():
                break
            
            doi = futures[future]
            try:
                doi_result, work_data = future.result()
                with result_lock:
                    if work_data:
                        result[doi_result] = work_data
                    processed += 1
                    if progress_callback:
                        progress_callback(processed, total, doi_result)
            except Exception as e:
                if SHOW_DEBUG_LOGS:
                    print(f"⚠️ Ошибка получения метаданных для {doi}: {e}")
                with result_lock:
                    processed += 1
    
    if SHOW_DEBUG_LOGS:
        print(f"✅ Получено метаданных для {len(result)} из {total} DOI")
    
    return result

def get_metadata_for_ids(ids: List[str], progress_callback: Optional[callable] = None) -> Dict[str, Dict]:
    """Получает метаданные для списка OpenAlex ID"""
    if not ids:
        return {}
    
    result = {}
    base_url = "https://api.openalex.org/works"
    
    for i, oa_id in enumerate(ids):
        if get_stop_flag():
            break
        
        if progress_callback:
            progress_callback(i + 1, len(ids), oa_id)
        
        params = {
            "filter": f"id:https://openalex.org/{oa_id}",
            "per_page": 1
        }
        
        data = smart_get(base_url, params)
        if data and data.get("results"):
            result[oa_id] = data["results"][0]
        
        if i < len(ids) - 1:
            time.sleep(0.2)
    
    return result

def parse_author_data(author_data: Dict) -> Author:
    """Парсит данные автора из OpenAlex"""
    display_name = author_data.get("display_name", "Unknown")
    orcid = author_data.get("orcid", "")
    if orcid:
        orcid = orcid.replace("https://orcid.org/", "")
    
    affiliations = []
    countries = []
    institution_ids = []
    
    if "affiliations" in author_data:
        for aff in author_data.get("affiliations", []):
            inst = aff.get("institution", {})
            if inst.get("display_name"):
                affiliations.append(inst["display_name"])
                institution_ids.append(inst.get("id", ""))
            country = aff.get("country_code", "")
            if country:
                countries.append(country)
    
    return Author(
        display_name=display_name,
        orcid=orcid,
        affiliations=affiliations,
        countries=countries,
        institution_ids=institution_ids
    )

def parse_topic_data(topic_data: Dict) -> Topic:
    """Парсит данные темы из OpenAlex"""
    return Topic(
        display_name=topic_data.get("display_name", ""),
        subfield=topic_data.get("subfield", {}).get("display_name", ""),
        field=topic_data.get("field", {}).get("display_name", ""),
        domain=topic_data.get("domain", {}).get("display_name", ""),
        score=topic_data.get("score", 0.0)
    )

def parse_concept_data(concept_data: Dict) -> Concept:
    """Парсит данные концепта из OpenAlex"""
    return Concept(
        display_name=concept_data.get("display_name", ""),
        level=concept_data.get("level", 0),
        score=concept_data.get("score", 0.0)
    )

def parse_publication(work_data: Dict, is_analyzed: bool = True) -> Union[AnalyzedPaper, CitingPaper]:
    """Парсит публикацию из OpenAlex"""
    # Базовые поля
    oa_data = work_data.get("open_access", {})
    
    # Авторы
    authors = []
    affiliations_list = []
    countries_list = []
    
    for authorship in work_data.get("authorships", []):
        author_data = authorship.get("author", {})
        if author_data:
            author = parse_author_data(author_data)
            authors.append(author)
            
            for aff in authorship.get("institutions", []):
                aff_name = aff.get("display_name", "")
                if aff_name and aff_name not in affiliations_list:
                    affiliations_list.append(aff_name)
                country = aff.get("country_code", "")
                if country and country not in countries_list:
                    countries_list.append(country)
    
    # Темы
    topics = []
    for topic_data in work_data.get("topics", []):
        topics.append(parse_topic_data(topic_data))
    
    # Концепты
    concepts = []
    for concept_data in work_data.get("concepts", []):
        concepts.append(parse_concept_data(concept_data))
    
    # Поля и домены
    fields = []
    domains = []
    for topic in topics:
        if topic.field and topic.field not in fields:
            fields.append(topic.field)
        if topic.domain and topic.domain not in domains:
            domains.append(topic.domain)
    
    # ====== ИСПРАВЛЕНИЕ: обрабатываем None primary_location ======
    primary_location = work_data.get("primary_location")
    if primary_location and isinstance(primary_location, dict):
        source = primary_location.get("source", {})
        journal_name = source.get("display_name", "Unknown") if source else "Unknown"
        publisher = source.get("host_organization_name") or source.get("publisher", "Unknown") if source else "Unknown"
    else:
        journal_name = "Unknown"
        publisher = "Unknown"
    
    # Дата публикации
    publication_date = work_data.get("publication_date", "")
    
    if is_analyzed:
        return AnalyzedPaper(
            id=work_data.get("id", "").replace("https://openalex.org/", ""),
            doi=work_data.get("doi", "").replace("https://doi.org/", ""),
            title=work_data.get("title", "No title"),
            year=work_data.get("publication_year", 0),
            cited_by_count=work_data.get("cited_by_count", 0),
            open_access_status=oa_data.get("oa_status", "unknown"),
            is_oa=oa_data.get("is_oa", False),
            authors=authors,
            affiliations=affiliations_list,
            countries=countries_list,
            journal=journal_name,
            publisher=publisher,
            topics=topics,
            concepts=concepts,
            fields=fields,
            domains=domains,
            publication_date=publication_date
        )
    else:
        return CitingPaper(
            id=work_data.get("id", "").replace("https://openalex.org/", ""),
            doi=work_data.get("doi", "").replace("https://doi.org/", ""),
            title=work_data.get("title", "No title"),
            year=work_data.get("publication_year", 0),
            publication_date=publication_date,
            journal=journal_name,
            publisher=publisher,
            authors=authors,
            affiliations=affiliations_list,
            countries=countries_list,
            topics=topics,
            concepts=concepts,
            fields=fields,
            domains=domains
        )

def parse_publications_batch(works_data: List[Dict], is_analyzed: bool = True) -> List[Union[AnalyzedPaper, CitingPaper]]:
    """Парсит батч публикаций из OpenAlex"""
    results = []
    for work in works_data:
        try:
            pub = parse_publication(work, is_analyzed)
            results.append(pub)
        except Exception as e:
            if SHOW_DEBUG_LOGS:
                print(f"⚠️ Ошибка парсинга публикации: {e}")
            continue
    return results

# ============================================
# ОСНОВНАЯ ЛОГИКА АНАЛИЗА ЖУРНАЛА
# ============================================

def parse_period(period_str: str) -> Tuple[Optional[List[int]], Optional[Tuple[int, int]]]:
    """
    Парсит строку периода.
    Возвращает либо список годов, либо кортеж (start_year, end_year)
    """
    period_str = period_str.strip()
    
    if ',' in period_str:
        # Список годов: 2020,2021,2022
        years = []
        for y in period_str.split(','):
            y = y.strip()
            if y.isdigit():
                years.append(int(y))
        return years, None
    
    elif '-' in period_str:
        # Диапазон: 2020-2026
        parts = period_str.split('-')
        if len(parts) == 2:
            start = parts[0].strip()
            end = parts[1].strip()
            if start.isdigit() and end.isdigit():
                return None, (int(start), int(end))
    
    # Если ни один формат не подошел, пробуем как одиночный год
    if period_str.isdigit():
        return [int(period_str)], None
    
    return None, None

def collect_analyzed_papers(issn: str, period: Union[List[int], Tuple[int, int]], 
                            progress_callback: Optional[callable] = None,
                            stop_callback: Optional[callable] = None) -> List[Dict]:
    """
    Собирает статьи журнала за указанный период из OpenAlex.
    Возвращает список словарей с информацией о статьях.
    """
    normalized = normalize_issn(issn)
    if SHOW_DEBUG_LOGS:
        print(f"📚 Сбор статей для ISSN: {normalized}")
    
    # Формируем фильтр по годам
    if isinstance(period, list):
        year_filter = "|".join(f"publication_year:{y}" for y in period)
    elif isinstance(period, tuple):
        year_filter = f"publication_year:{period[0]}-{period[1]}"
    else:
        return []
    
    articles = []
    cursor = "*"
    base_url = "https://api.openalex.org/works"
    page = 0
    
    while True:
        if stop_callback and stop_callback():
            if SHOW_DEBUG_LOGS:
                print("⏹️ Сбор статей прерван пользователем")
            break
        
        data = smart_get(base_url, {
            "filter": f"primary_location.source.issn:{normalized},{year_filter}",
            "per_page": 200,
            "select": "id,doi,publication_year,cited_by_count",
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
                "OpenAlex_ID": w.get("id", "").replace("https://openalex.org/", "")
            })
        
        page += 1
        if progress_callback:
            progress_callback(page, len(articles), len(data["results"]))
        
        cursor = data.get("meta", {}).get("next_cursor")
        if not cursor:
            break
    
    if SHOW_DEBUG_LOGS:
        print(f"✅ Найдено статей: {len(articles)}")
    
    return articles

def collect_citing_dois_parallel(analyzed_papers: List[Dict], 
                                 progress_callback: Optional[callable] = None,
                                 stop_callback: Optional[callable] = None,
                                 max_workers: int = MAX_WORKERS) -> Dict[str, List[str]]:
    """
    Параллельно собирает цитирующие DOI для каждой анализируемой статьи.
    Возвращает словарь {DOI: [citing_DOIs]}.
    """
    citing_map = {}
    futures = {}
    total = len([p for p in analyzed_papers if p.get('Cited_by_count', 0) > 0 and p.get('DOI') != 'N/A'])
    processed = 0
    
    if SHOW_DEBUG_LOGS:
        print(f"⚡ Параллельный сбор цитирующих DOI ({max_workers} потоков)...")
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Отправляем задачи
        for paper in analyzed_papers:
            if stop_callback and stop_callback():
                break
            if paper.get('Cited_by_count', 0) > 0 and paper.get('DOI') != 'N/A':
                future = executor.submit(get_citing_dois, paper['OpenAlex_ID'])
                futures[future] = paper['DOI']
        
        # Обрабатываем результаты по мере завершения
        for future in as_completed(futures):
            if stop_callback and stop_callback():
                break
            doi = futures[future]
            try:
                citing_map[doi] = future.result()
            except Exception as e:
                if SHOW_DEBUG_LOGS:
                    print(f"⚠️ Ошибка получения цитирований для {doi}: {e}")
                citing_map[doi] = []
            
            processed += 1
            if progress_callback:
                progress_callback(processed, total, doi)
    
    if SHOW_DEBUG_LOGS:
        print(f"✅ Собрано цитирующих DOI для {len(citing_map)} статей")
    
    return citing_map

def enrich_analyzed_papers(analyzed_papers: List[Dict],
                           citing_map: Dict[str, List[str]],
                           progress_callback: Optional[callable] = None,
                           stop_callback: Optional[callable] = None) -> List[AnalyzedPaper]:
    """
    Обогащает анализируемые статьи метаданными из OpenAlex (параллельно).
    """
    if SHOW_DEBUG_LOGS:
        print("📊 Обогащение анализируемых статей метаданными...")
    
    # Собираем все DOI для запроса
    all_dois = [p['DOI'] for p in analyzed_papers if p['DOI'] != 'N/A']
    enriched = []
    
    # Параллельное получение метаданных
    metadata = get_metadata_for_dois_parallel(
        all_dois, 
        progress_callback=progress_callback,
        stop_callback=stop_callback,
        max_workers=MAX_WORKERS
    )
    
    for paper in analyzed_papers:
        if stop_callback and stop_callback():
            break
        
        doi = paper['DOI']
        work_data = metadata.get(doi)
        
        if work_data:
            analyzed_paper = parse_publication(work_data, is_analyzed=True)
            analyzed_paper.citing_dois = citing_map.get(doi, [])
            enriched.append(analyzed_paper)
        else:
            if SHOW_DEBUG_LOGS:
                print(f"⚠️ Не удалось получить метаданные для {doi}")
    
    if SHOW_DEBUG_LOGS:
        print(f"✅ Обогащено {len(enriched)} статей")
    
    return enriched

def enrich_citing_papers(analyzed_papers: List[AnalyzedPaper],
                         progress_callback: Optional[callable] = None,
                         stop_callback: Optional[callable] = None) -> Dict[str, List[CitingPaper]]:
    """
    Обогащает цитирующие статьи метаданными из OpenAlex (параллельно).
    """
    if SHOW_DEBUG_LOGS:
        print("📊 Обогащение цитирующих статей метаданными...")
    
    # Собираем все уникальные DOI цитирующих статей
    all_citing_dois = set()
    for paper in analyzed_papers:
        all_citing_dois.update(paper.citing_dois)
    
    all_citing_dois = list(all_citing_dois)
    if SHOW_DEBUG_LOGS:
        print(f"📝 Найдено уникальных цитирующих DOI: {len(all_citing_dois)}")
    
    # Параллельное получение метаданных
    metadata = get_metadata_for_dois_parallel(
        all_citing_dois,
        progress_callback=progress_callback,
        stop_callback=stop_callback,
        max_workers=MAX_WORKERS
    )
    
    # Собираем результат
    result = {}
    for paper in analyzed_papers:
        citing_papers = []
        for citing_doi in paper.citing_dois:
            work_data = metadata.get(citing_doi)
            if work_data:
                citing_paper = parse_publication(work_data, is_analyzed=False)
                citing_papers.append(citing_paper)
            else:
                if SHOW_DEBUG_LOGS:
                    print(f"⚠️ Не удалось получить метаданные для цитирующей статьи {citing_doi}")
        
        result[paper.doi] = citing_papers
        paper.citations = citing_papers
    
    if SHOW_DEBUG_LOGS:
        total_citations = sum(len(v) for v in result.values())
        print(f"✅ Обогащено цитирующих статей: {total_citations}")
    
    return result

# ============================================
# РАСЧЕТ МЕТРИК
# ============================================

def calculate_h_index(papers: List[AnalyzedPaper]) -> int:
    """Рассчитывает h-index для списка статей"""
    citations = sorted([p.cited_by_count for p in papers if p.cited_by_count > 0], reverse=True)
    h_index = 0
    for i, c in enumerate(citations, 1):
        if c >= i:
            h_index = i
        else:
            break
    return h_index

def calculate_g_index(papers: List[AnalyzedPaper]) -> int:
    """Рассчитывает g-index для списка статей"""
    citations = sorted([p.cited_by_count for p in papers if p.cited_by_count > 0], reverse=True)
    total_citations = 0
    g_index = 0
    for i, c in enumerate(citations, 1):
        total_citations += c
        if total_citations >= i ** 2:
            g_index = i
    return g_index

def calculate_overview_metrics(analyzed_papers: List[AnalyzedPaper], 
                               citing_papers_dict: Dict[str, List[CitingPaper]]) -> Dict:
    """
    Рассчитывает все метрики для Overview раздела.
    """
    if not analyzed_papers:
        return {}
    
    # Базовые метрики
    total_pubs = len(analyzed_papers)
    total_citations = sum(p.cited_by_count for p in analyzed_papers)
    h_index = calculate_h_index(analyzed_papers)
    g_index = calculate_g_index(analyzed_papers)
    i10_index = sum(1 for p in analyzed_papers if p.cited_by_count >= 10)
    i100_index = sum(1 for p in analyzed_papers if p.cited_by_count >= 100)
    avg_citations = total_citations / total_pubs if total_pubs > 0 else 0
    
    # Open Access Breakdown
    oa_statuses = {}
    for p in analyzed_papers:
        status = p.open_access_status or "unknown"
        oa_statuses[status] = oa_statuses.get(status, 0) + 1
    
    # Активные годы
    years = [p.year for p in analyzed_papers if p.year > 0]
    active_years = len(set(years))
    
    # Уникальные авторы, аффилиации, страны
    all_authors = set()
    all_affiliations = set()
    all_countries = set()
    authors_per_paper = []
    affiliations_per_paper = []
    countries_per_paper = []
    
    for p in analyzed_papers:
        all_authors.update([a.display_name for a in p.authors])
        all_affiliations.update(p.affiliations)
        all_countries.update(p.countries)
        authors_per_paper.append(len(p.authors))
        affiliations_per_paper.append(len(p.affiliations))
        countries_per_paper.append(len(p.countries))
    
    avg_authors = np.mean(authors_per_paper) if authors_per_paper else 0
    avg_affiliations = np.mean(affiliations_per_paper) if affiliations_per_paper else 0
    avg_countries = np.mean(countries_per_paper) if countries_per_paper else 0
    
    # Международные коллаборации
    international_papers = 0
    for p in analyzed_papers:
        if len(set(p.countries)) > 1:
            international_papers += 1
    international_rate = international_papers / total_pubs if total_pubs > 0 else 0
    
    # Цитирующие работы
    all_citing_papers = []
    for citing_list in citing_papers_dict.values():
        all_citing_papers.extend(citing_list)
    
    unique_citing_authors = set()
    unique_citing_affiliations = set()
    unique_citing_countries = set()
    unique_citing_journals = set()
    unique_citing_publishers = set()
    
    for cp in all_citing_papers:
        for author in cp.authors:
            unique_citing_authors.add(author.display_name)
        unique_citing_affiliations.update(cp.affiliations)
        unique_citing_countries.update(cp.countries)
        if cp.journal and cp.journal != "Unknown":
            unique_citing_journals.add(cp.journal)
        if cp.publisher and cp.publisher != "Unknown":
            unique_citing_publishers.add(cp.publisher)
    
    return {
        'total_publications': total_pubs,
        'total_citations': total_citations,
        'h_index': h_index,
        'g_index': g_index,
        'i10_index': i10_index,
        'i100_index': i100_index,
        'avg_citations': avg_citations,
        'open_access_breakdown': oa_statuses,
        'active_years': active_years,
        'unique_authors': len(all_authors),
        'unique_affiliations': len(all_affiliations),
        'unique_countries': len(all_countries),
        'avg_authors_per_paper': avg_authors,
        'avg_affiliations_per_paper': avg_affiliations,
        'avg_countries_per_paper': avg_countries,
        'international_collaboration_rate': international_rate,
        'unique_citing_authors': len(unique_citing_authors),
        'unique_citing_affiliations': len(unique_citing_affiliations),
        'unique_citing_countries': len(unique_citing_countries),
        'unique_citing_journals': len(unique_citing_journals),
        'unique_citing_publishers': len(unique_citing_publishers),
        'all_citing_papers': all_citing_papers,
        'years': years,
        'all_authors': all_authors,
        'all_affiliations': all_affiliations,
        'all_countries': all_countries
    }

def calculate_citation_dynamics(analyzed_papers: List[AnalyzedPaper],
                                citing_papers_dict: Dict[str, List[CitingPaper]],
                                period_start: int, period_end: int) -> Dict:
    """
    Рассчитывает динамику цитирований по годам.
    """
    # Создаем матрицу цитирований
    citation_matrix = {}
    citation_lags = []
    
    for paper in analyzed_papers:
        pub_year = paper.year
        if pub_year < period_start or pub_year > period_end:
            continue
        
        # Получаем цитирующие статьи
        citing_papers = citing_papers_dict.get(paper.doi, [])
        
        # Для каждого цитирования
        for citing in citing_papers:
            citing_year = citing.year
            if citing_year < period_start or citing_year > period_end:
                continue
            
            # Задержка цитирования
            lag = citing_year - pub_year
            if lag >= 0:
                citation_lags.append(lag)
            
            # Заполняем матрицу
            key = (pub_year, citing_year)
            citation_matrix[key] = citation_matrix.get(key, 0) + 1
    
    # Строим таблицу динамики
    dynamics_rows = []
    for pub_year in range(period_start, period_end + 1):
        for cit_year in range(period_start, period_end + 1):
            count = citation_matrix.get((pub_year, cit_year), 0)
            if count > 0 or pub_year == cit_year:  # Показываем все года, включая нулевые диагональные
                dynamics_rows.append({
                    'publication_year': pub_year,
                    'citation_year': cit_year,
                    'citations_count': count
                })
    
    # Сортируем по году публикации и году цитирования
    dynamics_rows.sort(key=lambda x: (x['publication_year'], x['citation_year']))
    
    # Первое цитирование анализ
    first_citation_data = []
    for paper in analyzed_papers:
        if paper.doi in citing_papers_dict and citing_papers_dict[paper.doi]:
            citing_years = [c.year for c in citing_papers_dict[paper.doi] if c.year >= period_start]
            if citing_years:
                first_citation_data.append(min(citing_years) - paper.year)
    
    first_citation_stats = {
        'min': min(first_citation_data) if first_citation_data else None,
        'max': max(first_citation_data) if first_citation_data else None,
        'avg': np.mean(first_citation_data) if first_citation_data else None,
        'median': np.median(first_citation_data) if first_citation_data else None,
        'count': len(first_citation_data)
    }
    
    # Накопленные цитирования
    cumulative = {}
    for year in range(period_start, period_end + 1):
        total = 0
        for (pub_year, cit_year), count in citation_matrix.items():
            if cit_year <= year:
                total += count
        cumulative[year] = total
    
    # Тепловая матрица для Heatmap
    heatmap_data = []
    for pub_year in range(period_start, period_end + 1):
        row = []
        for cit_year in range(period_start, period_end + 1):
            row.append(citation_matrix.get((pub_year, cit_year), 0))
        heatmap_data.append(row)
    
    return {
        'dynamics_rows': dynamics_rows,
        'citation_matrix': citation_matrix,
        'first_citation_stats': first_citation_stats,
        'cumulative': cumulative,
        'heatmap_data': heatmap_data,
        'citation_lags': citation_lags
    }

def calculate_author_analysis(analyzed_papers: List[AnalyzedPaper]) -> List[Dict]:
    """
    Анализирует авторов: топ по числу публикаций и цитирований.
    """
    author_stats = defaultdict(lambda: {'publications': 0, 'citations': 0, 'orcid': None, 'affiliations': [], 'countries': []})
    
    for paper in analyzed_papers:
        for author in paper.authors:
            author_stats[author.display_name]['publications'] += 1
            author_stats[author.display_name]['citations'] += paper.cited_by_count
            if author.orcid and not author_stats[author.display_name]['orcid']:
                author_stats[author.display_name]['orcid'] = author.orcid
            if author.affiliations:
                author_stats[author.display_name]['affiliations'].extend(author.affiliations)
            if author.countries:
                author_stats[author.display_name]['countries'].extend(author.countries)
    
    # Формируем список для таблицы
    result = []
    for name, stats in author_stats.items():
        result.append({
            'name': name,
            'publications': stats['publications'],
            'citations': stats['citations'],
            'orcid': stats['orcid'],
            'affiliations': list(set(stats['affiliations'])),
            'countries': list(set(stats['countries']))
        })
    
    # Сортируем по числу публикаций (по убыванию)
    result.sort(key=lambda x: x['publications'], reverse=True)
    return result[:30]  # Топ 30

def calculate_affiliation_analysis(analyzed_papers: List[AnalyzedPaper]) -> List[Dict]:
    """
    Анализирует аффилиации: топ по числу публикаций.
    """
    affiliation_stats = defaultdict(int)
    
    for paper in analyzed_papers:
        for aff in paper.affiliations:
            affiliation_stats[aff] += 1
    
    result = [{'name': name, 'count': count} for name, count in affiliation_stats.items()]
    result.sort(key=lambda x: x['count'], reverse=True)
    return result[:30]  # Топ 30

def calculate_geographic_analysis(analyzed_papers: List[AnalyzedPaper]) -> Dict:
    """
    Проводит географический анализ.
    """
    # 1. Уникальные страны на публикацию
    unique_countries_per_pub = []
    for paper in analyzed_papers:
        unique_countries_per_pub.append(len(set(paper.countries)))
    
    # 2. Авторы по странам (индивидуальное распределение)
    authors_per_country = defaultdict(int)
    for paper in analyzed_papers:
        for author in paper.authors:
            for country in author.countries:
                authors_per_country[country] += 1
    
    # 3. Паттерны коллабораций
    single_country = 0
    international = 0
    for paper in analyzed_papers:
        if len(set(paper.countries)) <= 1:
            single_country += 1
        else:
            international += 1
    
    # 4. Пары стран-коллаборантов
    country_pairs = defaultdict(int)
    for paper in analyzed_papers:
        countries = sorted(set(paper.countries))
        if len(countries) > 1:
            for i in range(len(countries)):
                for j in range(i + 1, len(countries)):
                    pair = f"{countries[i]} - {countries[j]}"
                    country_pairs[pair] += 1
    
    return {
        'unique_countries_per_pub': unique_countries_per_pub,
        'authors_per_country': dict(authors_per_country),
        'single_country': single_country,
        'international': international,
        'country_pairs': dict(sorted(country_pairs.items(), key=lambda x: x[1], reverse=True)[:20])
    }

def calculate_topics_analysis(analyzed_papers: List[AnalyzedPaper],
                              citing_papers_dict: Dict[str, List[CitingPaper]]) -> Dict:
    """
    Анализирует темы: частотность в анализируемых и цитирующих статьях.
    """
    # Собираем все темы из анализируемых статей
    analyzed_topic_count = defaultdict(int)
    analyzed_topic_years = defaultdict(list)
    
    for paper in analyzed_papers:
        for topic in paper.topics:
            if topic.display_name:
                analyzed_topic_count[topic.display_name] += 1
                analyzed_topic_years[topic.display_name].append(paper.year)
    
    # Собираем все темы из цитирующих статей
    citing_topic_count = defaultdict(int)
    citing_topic_years = defaultdict(list)
    
    for citing_list in citing_papers_dict.values():
        for citing in citing_list:
            for topic in citing.topics:
                if topic.display_name:
                    citing_topic_count[topic.display_name] += 1
                    citing_topic_years[topic.display_name].append(citing.year)
    
    # Объединяем
    all_topics = set(analyzed_topic_count.keys()) | set(citing_topic_count.keys())
    
    total_analyzed = len(analyzed_papers)
    total_citing = sum(len(v) for v in citing_papers_dict.values())
    
    result = []
    for topic in all_topics:
        analyzed_count = analyzed_topic_count.get(topic, 0)
        citing_count = citing_topic_count.get(topic, 0)
        
        analyzed_norm = analyzed_count / total_analyzed if total_analyzed > 0 else 0
        citing_norm = citing_count / total_citing if total_citing > 0 else 0
        total_norm = (analyzed_norm + citing_norm) / 2
        
        years = analyzed_topic_years.get(topic, []) + citing_topic_years.get(topic, [])
        first_year = min(years) if years else None
        peak_year = None
        if years:
            year_counts = Counter(years)
            peak_year = max(year_counts.items(), key=lambda x: x[1])[0]
        
        result.append({
            'topic': topic,
            'analyzed_count': analyzed_count,
            'citing_count': citing_count,
            'analyzed_norm': analyzed_norm,
            'citing_norm': citing_norm,
            'total_norm': total_norm,
            'first_year': first_year,
            'peak_year': peak_year
        })
    
    # Сортируем по общему нормированному значению
    result.sort(key=lambda x: x['total_norm'], reverse=True)
    
    return {
        'topics': result,
        'total_analyzed': total_analyzed,
        'total_citing': total_citing
    }

def calculate_most_cited_publications(analyzed_papers: List[AnalyzedPaper]) -> List[Dict]:
    """
    Возвращает топ самых цитируемых публикаций.
    """
    result = []
    for paper in sorted(analyzed_papers, key=lambda x: x.cited_by_count, reverse=True)[:20]:
        # Вычисляем citations per year
        if paper.year > 0:
            years_since = datetime.now().year - paper.year + 1
            citations_per_year = paper.cited_by_count / max(years_since, 1)
        else:
            citations_per_year = 0
        
        result.append({
            'title': paper.title,
            'year': paper.year,
            'citations': paper.cited_by_count,
            'citations_per_year': citations_per_year,
            'authors': ', '.join([a.display_name for a in paper.authors[:5]]) + (' + more' if len(paper.authors) > 5 else ''),
            'doi': paper.doi,
            'journal': paper.journal
        })
    
    return result

def calculate_top_citing_items(citing_papers: List[CitingPaper], item_type: str) -> List[Dict]:
    """
    Рассчитывает топ цитирующих элементов (авторы, аффилиации, страны, журналы, издательства).
    """
    if item_type == 'authors':
        counter = defaultdict(int)
        for paper in citing_papers:
            for author in paper.authors:
                counter[author.display_name] += 1
    elif item_type == 'affiliations':
        counter = defaultdict(int)
        for paper in citing_papers:
            for aff in paper.affiliations:
                counter[aff] += 1
    elif item_type == 'countries':
        counter = defaultdict(int)
        for paper in citing_papers:
            for country in paper.countries:
                counter[country] += 1
    elif item_type == 'journals':
        counter = defaultdict(int)
        for paper in citing_papers:
            if paper.journal and paper.journal != "Unknown":
                counter[paper.journal] += 1
    elif item_type == 'publishers':
        counter = defaultdict(int)
        for paper in citing_papers:
            if paper.publisher and paper.publisher != "Unknown":
                counter[paper.publisher] += 1
    else:
        return []
    
    result = [{'name': name, 'count': count} for name, count in counter.items()]
    result.sort(key=lambda x: x['count'], reverse=True)
    return result[:30]

def calculate_topic_relationships(analyzed_papers: List[AnalyzedPaper],
                                  citing_papers_dict: Dict[str, List[CitingPaper]]) -> Dict:
    """
    Рассчитывает взаимосвязи Topics, Subtopics, Fields, Domains, Concepts с цитированиями.
    Возвращает топ-10 для каждой категории.
    """
    # Собираем все цитирования для каждой категории
    topic_citations = defaultdict(int)
    subtopic_citations = defaultdict(int)
    field_citations = defaultdict(int)
    domain_citations = defaultdict(int)
    concept_citations = defaultdict(int)
    
    # Для анализируемых статей считаем цитирования
    for paper in analyzed_papers:
        if paper.cited_by_count == 0:
            continue
        
        for topic in paper.topics:
            if topic.display_name:
                topic_citations[topic.display_name] += paper.cited_by_count
            if topic.subfield:
                subtopic_citations[topic.subfield] += paper.cited_by_count
            if topic.field:
                field_citations[topic.field] += paper.cited_by_count
            if topic.domain:
                domain_citations[topic.domain] += paper.cited_by_count
        
        for concept in paper.concepts:
            if concept.display_name:
                concept_citations[concept.display_name] += paper.cited_by_count
    
    # Сортируем и берем топ-10
    return {
        'topics': dict(sorted(topic_citations.items(), key=lambda x: x[1], reverse=True)[:10]),
        'subtopics': dict(sorted(subtopic_citations.items(), key=lambda x: x[1], reverse=True)[:10]),
        'fields': dict(sorted(field_citations.items(), key=lambda x: x[1], reverse=True)[:10]),
        'domains': dict(sorted(domain_citations.items(), key=lambda x: x[1], reverse=True)[:10]),
        'concepts': dict(sorted(concept_citations.items(), key=lambda x: x[1], reverse=True)[:10])
    }

def get_detailed_citations(analyzed_papers: List[AnalyzedPaper],
                           citing_papers_dict: Dict[str, List[CitingPaper]]) -> Dict:
    """
    Возвращает детальные цитирования для каждой анализируемой статьи.
    """
    detailed = {}
    
    for paper in analyzed_papers:
        citations = citing_papers_dict.get(paper.doi, [])
        if citations:
            citations_list = []
            for cite in citations:
                # Собираем информацию о цитирующей статье
                citing_authors = [a.display_name for a in cite.authors]
                citing_countries = list(set([c for a in cite.authors for c in a.countries]))
                citing_topics = [t.display_name for t in cite.topics if t.display_name]
                
                citations_list.append({
                    'citing_title': cite.title,
                    'citing_year': cite.year,
                    'citing_date': cite.publication_date,
                    'citing_journal': cite.journal,
                    'citing_publisher': cite.publisher,
                    'citing_doi': cite.doi,
                    'citation_lag': cite.year - paper.year if cite.year >= paper.year else 0,
                    'citing_authors': citing_authors,
                    'citing_countries': citing_countries,
                    'citing_topics': citing_topics[:5]  # Топ 5 тем
                })
            
            detailed[paper.id] = {
                'title': paper.title,
                'year': paper.year,
                'doi': paper.doi,
                'total_citations': len(citations_list),
                'citations': citations_list
            }
    
    return detailed

# ============================================
# ГЕНЕРАЦИЯ HTML ОТЧЕТА (РАСШИРЕННАЯ)
# ============================================

def generate_html_report(issn: str, period: str, 
                         analyzed_papers: List[AnalyzedPaper],
                         citing_papers_dict: Dict[str, List[CitingPaper]],
                         overview_metrics: Dict,
                         citation_dynamics: Dict,
                         author_analysis: List[Dict],
                         affiliation_analysis: List[Dict],
                         geographic_analysis: Dict,
                         topics_analysis: Dict,
                         most_cited: List[Dict],
                         top_citing_authors: List[Dict],
                         top_citing_affiliations: List[Dict],
                         top_citing_countries: List[Dict],
                         top_citing_journals: List[Dict],
                         top_citing_publishers: List[Dict],
                         topic_relationships: Dict,
                         detailed_citations: Dict,
                         logo_base64: Optional[str] = None,
                         app_logo_base64: Optional[str] = None,
                         theme_colors: Optional[Dict] = None,
                         lang: str = 'en') -> str:
    """
    Генерирует полный HTML отчет с навигацией и всеми разделами.
    """
    
    # Функция перевода
    def t(key: str, **kwargs) -> str:
        return translate(key, lang, **kwargs)
    
    if theme_colors is None:
        theme_colors = {
            'primary': '#667eea',
            'secondary': '#f39c12'
        }
    
    primary = theme_colors.get('primary', '#667eea')
    secondary = theme_colors.get('secondary', '#f39c12')
    
    # Подготовка данных
    oa_breakdown = overview_metrics.get('open_access_breakdown', {})
    total_pubs = overview_metrics.get('total_publications', 0)
    total_citations = overview_metrics.get('total_citations', 0)
    h_index = overview_metrics.get('h_index', 0)
    g_index = overview_metrics.get('g_index', 0)
    i10_index = overview_metrics.get('i10_index', 0)
    i100_index = overview_metrics.get('i100_index', 0)
    avg_citations = overview_metrics.get('avg_citations', 0)
    active_years = overview_metrics.get('active_years', 0)
    unique_authors = overview_metrics.get('unique_authors', 0)
    unique_affiliations = overview_metrics.get('unique_affiliations', 0)
    unique_countries = overview_metrics.get('unique_countries', 0)
    avg_authors = overview_metrics.get('avg_authors_per_paper', 0)
    avg_affiliations = overview_metrics.get('avg_affiliations_per_paper', 0)
    avg_countries = overview_metrics.get('avg_countries_per_paper', 0)
    international_rate = overview_metrics.get('international_collaboration_rate', 0)
    unique_citing_authors = overview_metrics.get('unique_citing_authors', 0)
    unique_citing_affiliations = overview_metrics.get('unique_citing_affiliations', 0)
    unique_citing_countries = overview_metrics.get('unique_citing_countries', 0)
    unique_citing_journals = overview_metrics.get('unique_citing_journals', 0)
    unique_citing_publishers = overview_metrics.get('unique_citing_publishers', 0)
    
    # Определяем период для отображения
    period_display = period
    
    # Строим HTML
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>{t('journal_analysis')} - ISSN {issn}</title>
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
                max-width: 1600px;
                margin: 0 auto;
                background: white;
                box-shadow: 0 10px 40px rgba(0,0,0,0.1);
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
                padding: 20px;
                overflow-y: auto;
                z-index: 1000;
                box-shadow: 2px 0 10px rgba(0,0,0,0.1);
            }}
            .sidebar::-webkit-scrollbar {{
                width: 6px;
            }}
            .sidebar::-webkit-scrollbar-track {{
                background: rgba(255,255,255,0.1);
                border-radius: 3px;
            }}
            .sidebar::-webkit-scrollbar-thumb {{
                background: rgba(255,255,255,0.4);
                border-radius: 3px;
            }}
            .sidebar::-webkit-scrollbar-thumb:hover {{
                background: rgba(255,255,255,0.6);
            }}
            
            .sidebar-logo {{
                text-align: center;
                margin-bottom: 20px;
            }}
            .sidebar-logo img {{
                max-width: 200px;
                max-height: 80px;
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
                color: white;
                text-decoration: none;
                display: flex;
                align-items: center;
                gap: 10px;
                padding: 8px 12px;
                margin: 2px 0;
                border-radius: 6px;
                transition: all 0.3s;
                font-size: 14px;
            }}
            .sidebar a:hover {{
                background: rgba(255,255,255,0.2);
                transform: translateX(5px);
            }}
            .sidebar a .sub-link {{
                font-size: 12px;
                opacity: 0.8;
                margin-left: 20px;
            }}
            .sidebar a .icon {{
                font-size: 16px;
                width: 24px;
                text-align: center;
            }}
            .sidebar .level-1 {{
                padding-left: 8px;
            }}
            .sidebar .level-2 {{
                padding-left: 30px;
                font-size: 13px;
                opacity: 0.9;
            }}
            .sidebar .level-3 {{
                padding-left: 50px;
                font-size: 12px;
                opacity: 0.8;
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
                position: relative;
            }}
            .header .header-logo-container {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 15px;
            }}
            .header .header-logo-left {{
                max-height: 80px;
                max-width: 200px;
            }}
            .header .header-logo-right {{
                max-height: 80px;
                max-width: 200px;
            }}
            .header h1 {{
                color: white;
                border-bottom: none;
                margin: 10px 0;
                font-size: 32px;
            }}
            .header .subtitle {{
                opacity: 0.9;
                font-size: 16px;
            }}
            .header .date {{
                opacity: 0.8;
                margin-top: 10px;
                font-size: 14px;
            }}
            
            /* Sections */
            .section {{
                background: white;
                border-radius: 15px;
                padding: 25px;
                margin-bottom: 30px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                border: 1px solid #e8e8e8;
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
                font-size: 26px;
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
                padding: 18px;
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
            .metric-value .small {{
                font-size: 16px;
            }}
            
            /* Progress Bars */
            .progress-container {{
                width: 100%;
                background-color: #f0f0f0;
                border-radius: 20px;
                overflow: hidden;
                margin: 5px 0;
            }}
            .progress-bar {{
                height: 20px;
                background: linear-gradient(90deg, {primary}, {secondary});
                border-radius: 20px;
                transition: width 0.5s ease;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-size: 11px;
                font-weight: bold;
            }}
            
            /* Tables */
            .table-container {{
                overflow-x: auto;
                max-height: 600px;
                overflow-y: auto;
            }}
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
            
            table {{
                width: 100%;
                border-collapse: collapse;
                font-family: 'Times New Roman', serif;
                font-size: 14px;
            }}
            thead {{
                position: sticky;
                top: 0;
                z-index: 10;
            }}
            th {{
                background: linear-gradient(135deg, {primary} 0%, {secondary} 100%);
                color: white;
                padding: 12px;
                text-align: left;
                font-weight: 600;
                white-space: nowrap;
            }}
            td {{
                padding: 10px;
                border-bottom: 1px solid #e0e0e0;
                vertical-align: middle;
            }}
            tr:nth-child(even) {{
                background-color: #f8f9fa;
            }}
            tr:hover {{
                background-color: #e8f0fe;
            }}
            
            /* Heatmap */
            .heatmap-container {{
                overflow-x: auto;
                margin: 20px 0;
            }}
            .heatmap-grid {{
                display: inline-block;
                border-collapse: collapse;
            }}
            .heatmap-grid td {{
                padding: 8px 14px;
                text-align: center;
                border: 1px solid #ddd;
                font-size: 13px;
                min-width: 50px;
            }}
            .heatmap-grid .header-cell {{
                background: linear-gradient(135deg, {primary} 0%, {secondary} 100%);
                color: white;
                font-weight: bold;
                padding: 8px 12px;
            }}
            .heatmap-grid .row-header {{
                background: linear-gradient(135deg, {primary} 0%, {secondary} 100%);
                color: white;
                font-weight: bold;
                padding: 8px 12px;
                text-align: center;
            }}
            
            /* Collapsible */
            .collapser {{
                background: #f8f9fa;
                padding: 12px 16px;
                margin: 5px 0;
                border-radius: 8px;
                cursor: pointer;
                border: 1px solid #e0e0e0;
                transition: all 0.3s;
                display: flex;
                flex-wrap: wrap;
                align-items: center;
                gap: 10px;
            }}
            .collapser:hover {{
                background: #e8f0fe;
                border-color: {primary};
            }}
            .collapser .badge {{
                display: inline-block;
                padding: 2px 10px;
                border-radius: 12px;
                font-size: 11px;
                font-weight: 600;
            }}
            .collapser .badge-info {{
                background: #d1ecf1;
                color: #0c5460;
            }}
            .collapser .badge-success {{
                background: #d4edda;
                color: #155724;
            }}
            .collapser .badge-warning {{
                background: #fff3cd;
                color: #856404;
            }}
            .collapser .badge-danger {{
                background: #f8d7da;
                color: #721c24;
            }}
            .collapser .citation-count {{
                font-weight: bold;
                color: {primary};
            }}
            .collapser .toggle-icon {{
                margin-left: auto;
                font-size: 14px;
                color: #666;
            }}
            
            .citation-detail {{
                background: #f8f9fa;
                padding: 12px 16px;
                margin: 5px 0 5px 20px;
                border-radius: 6px;
                border-left: 3px solid {primary};
                font-size: 13px;
            }}
            .citation-detail .cite-meta {{
                font-size: 12px;
                color: #666;
                margin-top: 4px;
            }}
            .citation-detail .cite-meta strong {{
                color: #333;
            }}
            
            .word-wrap {{
                word-wrap: break-word;
                word-break: break-word;
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
            
            .country-badge {{
                display: inline-block;
                padding: 2px 8px;
                border-radius: 12px;
                font-size: 11px;
                background: #e8f0fe;
                margin: 2px;
            }}
            
            .filter-section {{
                background: #f8f9fa;
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 15px;
            }}
            .filter-row {{
                display: flex;
                flex-wrap: wrap;
                gap: 10px;
                align-items: center;
            }}
            .filter-row label {{
                font-size: 12px;
                font-weight: 600;
                color: #555;
            }}
            .filter-row select, .filter-row input {{
                padding: 5px 10px;
                border: 1px solid #ddd;
                border-radius: 5px;
                font-size: 12px;
                background: white;
            }}
            .filter-row select:focus, .filter-row input:focus {{
                outline: none;
                border-color: {primary};
                box-shadow: 0 0 5px rgba({primary}, 0.3);
            }}
            .filter-row .filter-group {{
                display: flex;
                align-items: center;
                gap: 5px;
            }}
            
            .footer {{
                margin-top: 40px;
                padding-top: 20px;
                border-top: 2px solid #e8e8e8;
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
            
            .badge-oa {{
                display: inline-block;
                padding: 2px 10px;
                border-radius: 12px;
                font-size: 11px;
                font-weight: 600;
            }}
            .badge-gold {{ background: #FFD700; color: #333; }}
            .badge-green {{ background: #2ECC71; color: white; }}
            .badge-hybrid {{ background: #F1C40F; color: #333; }}
            .badge-bronze {{ background: #CD7F32; color: white; }}
            .badge-closed {{ background: #95A5A6; color: white; }}
            .badge-diamond {{ background: #00BFFF; color: white; }}
            .badge-unknown {{ background: #BDC3C7; color: #333; }}
            
            .orcid-link {{
                color: #a6ce39;
                text-decoration: none;
                font-family: monospace;
                font-size: 12px;
            }}
            .orcid-link:hover {{
                text-decoration: underline;
            }}
            
            @media print {{
                .sidebar {{ display: none; }}
                .main-content {{ margin-left: 0; }}
            }}
            @media (max-width: 768px) {{
                .sidebar {{ display: none; }}
                .main-content {{ margin-left: 0; padding: 15px; }}
                .header .header-logo-container {{
                    flex-direction: column;
                    gap: 10px;
                }}
                .metrics-grid {{
                    grid-template-columns: repeat(2, 1fr);
                }}
                .filter-row {{
                    flex-direction: column;
                    align-items: stretch;
                }}
            }}
        </style>
    </head>
    <body>
        <!-- Sidebar Navigation -->
        <div class="sidebar">
            <div class="sidebar-logo">
                {f'<img src="data:image/png;base64,{app_logo_base64}" alt="App Logo">' if app_logo_base64 else f'<h3 style="font-size:16px;">{t("app_logo")}</h3>'}
            </div>
            <h3>📑 {t('journal_analysis')}</h3>
            
            <a href="#overview"><span class="icon">📊</span> {t('overview')}</a>
            <a href="#metrics-overview" class="level-2"><span class="icon">📈</span> {t('metrics_overview')}</a>
            <a href="#oa-breakdown" class="level-2"><span class="icon">📊</span> {t('open_access_breakdown')}</a>
            
            <a href="#analyzed-articles"><span class="icon">📄</span> {t('analyzed_articles')}</a>
            <a href="#author-analysis" class="level-2"><span class="icon">👤</span> {t('author_analysis')}</a>
            <a href="#affiliation-analysis" class="level-2"><span class="icon">🏛️</span> {t('top_affiliations')}</a>
            <a href="#geographic-analysis" class="level-2"><span class="icon">🌍</span> {t('geographic_analysis')}</a>
            <a href="#all-publications" class="level-2"><span class="icon">📚</span> {t('all_publications')}</a>
            <a href="#detailed-citations" class="level-2"><span class="icon">📋</span> {t('detailed_citations')}</a>
            
            <a href="#citation-analysis"><span class="icon">📊</span> {t('citation_analysis')}</a>
            <a href="#citation-dynamics" class="level-2"><span class="icon">📈</span> {t('citation_dynamics')}</a>
            <a href="#cumulative-citations" class="level-2"><span class="icon">📊</span> {t('cumulative_citations')}</a>
            <a href="#citation-heatmap" class="level-2"><span class="icon">🌡️</span> {t('citation_network_heatmap')}</a>
            <a href="#most-cited" class="level-2"><span class="icon">🏆</span> {t('most_cited_publications')}</a>
            
            <a href="#citing-works"><span class="icon">📄</span> {t('citing_works')}</a>
            <a href="#top-citing-authors" class="level-2"><span class="icon">👤</span> {t('top_citing_authors')}</a>
            <a href="#top-citing-affiliations" class="level-2"><span class="icon">🏛️</span> {t('top_citing_affiliations')}</a>
            <a href="#top-citing-countries" class="level-2"><span class="icon">🌍</span> {t('top_citing_countries')}</a>
            <a href="#top-citing-journals" class="level-2"><span class="icon">📚</span> {t('top_citing_journals')}</a>
            <a href="#top-citing-publishers" class="level-2"><span class="icon">🏛️</span> {t('top_citing_publishers')}</a>
            
            <a href="#topics-analysis"><span class="icon">🏷️</span> {t('topics_analysis')}</a>
            <a href="#topics-overview" class="level-2"><span class="icon">📊</span> {t('topics_overview')}</a>
            <a href="#topic-relationships" class="level-2"><span class="icon">🔗</span> {t('top_cited_topics')}</a>
        </div>
        
        <div class="main-content">
            <!-- Header -->
            <div class="header">
                <div class="header-logo-container">
                    {f'<img src="data:image/png;base64,{app_logo_base64}" class="header-logo-left" alt="App Logo">' if app_logo_base64 else ''}
                    <div>
                        <h1>🔬 {t('journal_analysis')}</h1>
                        <div class="subtitle">ISSN: {issn} | {t('period')}: {period_display}</div>
                    </div>
                    {f'<img src="data:image/png;base64,{logo_base64}" class="header-logo-right" alt="Journal Logo">' if logo_base64 else ''}
                </div>
                <div class="date">{t('generated')}: {datetime.now().strftime('%d.%m.%Y %H:%M')}</div>
            </div>
            
            <!-- ==================== OVERVIEW ==================== -->
            <div id="overview" class="section">
                <div class="section-title"><span class="icon">📊</span> {t('overview')}</div>
                
                <div id="metrics-overview">
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
                            <div class="metric-value">{avg_authors:.1f}</div>
                            <div class="metric-label">{t('avg_authors_per_paper')}</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{avg_affiliations:.1f}</div>
                            <div class="metric-label">{t('avg_affiliations_per_paper')}</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{avg_countries:.1f}</div>
                            <div class="metric-label">{t('avg_countries_per_paper')}</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{international_rate*100:.1f}%</div>
                            <div class="metric-label">{t('international_collaboration_rate')}</div>
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
                </div>
                
                <!-- Open Access Breakdown -->
                <div id="oa-breakdown" style="margin-top: 20px;">
                    <h3 style="color: {primary};">{t('open_access_breakdown')}</h3>
                    <div class="metrics-grid" style="grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));">
    """
    
    oa_labels = {
        'gold': t('gold'),
        'hybrid': t('hybrid'),
        'green': t('green'),
        'bronze': t('bronze'),
        'closed': t('closed'),
        'unknown': t('unknown'),
        'diamond': t('diamond')
    }
    oa_colors = {
        'gold': 'badge-gold',
        'hybrid': 'badge-hybrid',
        'green': 'badge-green',
        'bronze': 'badge-bronze',
        'closed': 'badge-closed',
        'unknown': 'badge-unknown',
        'diamond': 'badge-diamond'
    }
    
    for status, count in sorted(oa_breakdown.items(), key=lambda x: x[1], reverse=True):
        label = oa_labels.get(status, status)
        color_class = oa_colors.get(status, 'badge-unknown')
        percentage = (count / total_pubs * 100) if total_pubs > 0 else 0
        html_content += f"""
        <div class="metric-card">
            <div class="metric-value">{count}</div>
            <div class="metric-label"><span class="badge-oa {color_class}">{label}</span> ({percentage:.1f}%)</div>
        </div>
        """
    
    html_content += f"""
                    </div>
                </div>
            </div>
            
            <!-- ==================== ANALYZED ARTICLES ==================== -->
            <div id="analyzed-articles" class="section">
                <div class="section-title"><span class="icon">📄</span> {t('analyzed_articles')}</div>
                
                <!-- Author Analysis -->
                <div id="author-analysis">
                    <h3 style="color: {primary};">👤 {t('author_analysis')}</h3>
                    <div class="table-container">
                        <table>
                            <thead>
                                <tr>
                                    <th>{t('rank')}</th>
                                    <th>{t('authors')}</th>
                                    <th>ORCID</th>
                                    <th>{t('affiliations')}</th>
                                    <th>{t('countries')}</th>
                                    <th>{t('publications')}</th>
                                    <th>{t('citations')}</th>
                                </tr>
                            </thead>
                            <tbody>
    """
    
    for i, author in enumerate(author_analysis[:30], 1):
        orcid_link = f'<a href="https://orcid.org/{author["orcid"]}" target="_blank" class="orcid-link">🆔 {author["orcid"][:8]}...</a>' if author.get('orcid') else ''
        affiliations_text = ', '.join(author.get('affiliations', [])[:3])
        if len(author.get('affiliations', [])) > 3:
            affiliations_text += f' +{len(author["affiliations"])-3} more'
        countries_text = ', '.join(author.get('countries', [])[:3])
        if len(author.get('countries', [])) > 3:
            countries_text += f' +{len(author["countries"])-3} more'
        
        html_content += f"""
        <tr>
            <td>{i}</td>
            <td>{html.escape(author["name"])}</td>
            <td>{orcid_link}</td>
            <td>{html.escape(affiliations_text)}</td>
            <td>{countries_text}</td>
            <td>{author["publications"]}</td>
            <td>{author["citations"]}</td>
        </tr>
        """
    
    html_content += f"""
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <!-- Top Affiliations -->
                <div id="affiliation-analysis" style="margin-top: 25px;">
                    <h3 style="color: {primary};">🏛️ {t('top_affiliations')}</h3>
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
    """
    
    for i, aff in enumerate(affiliation_analysis[:30], 1):
        html_content += f"""
        <tr>
            <td>{i}</td>
            <td>{html.escape(aff["name"])}</td>
            <td>{aff["count"]}</td>
        </tr>
        """
    
    html_content += f"""
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <!-- Geographic Analysis -->
                <div id="geographic-analysis" style="margin-top: 25px;">
                    <h3 style="color: {primary};">🌍 {t('geographic_analysis')}</h3>
                    
                    <h4 style="margin-top: 15px; color: {primary};">{t('unique_countries_per_publication')}</h4>
                    <div style="display: flex; gap: 20px; flex-wrap: wrap; margin: 10px 0;">
                        <div class="metric-card" style="min-width: 120px;">
                            <div class="metric-value">{np.mean(geographic_analysis.get('unique_countries_per_pub', [0])):.2f}</div>
                            <div class="metric-label">Avg countries per paper</div>
                        </div>
                        <div class="metric-card" style="min-width: 120px;">
                            <div class="metric-value">{max(geographic_analysis.get('unique_countries_per_pub', [0]))}</div>
                            <div class="metric-label">Max countries per paper</div>
                        </div>
                    </div>
                    
                    <h4 style="margin-top: 15px; color: {primary};">{t('authors_per_country')}</h4>
                    <div class="table-container" style="max-height: 300px;">
                        <table>
                            <thead>
                                <tr>
                                    <th>{t('countries')}</th>
                                    <th>{t('authors')}</th>
                                </tr>
                            </thead>
                            <tbody>
    """
    
    authors_per_country = geographic_analysis.get('authors_per_country', {})
    for country, count in sorted(authors_per_country.items(), key=lambda x: x[1], reverse=True)[:30]:
        html_content += f"""
        <tr>
            <td><span class="country-badge">{html.escape(country)}</span></td>
            <td>{count}</td>
        </tr>
        """
    
    html_content += f"""
                            </tbody>
                        </table>
                    </div>
                    
                    <h4 style="margin-top: 15px; color: {primary};">{t('collaboration_patterns')}</h4>
                    <div style="display: flex; gap: 30px; flex-wrap: wrap; margin: 10px 0;">
                        <div class="metric-card" style="min-width: 150px;">
                            <div class="metric-value">{geographic_analysis.get('single_country', 0)}</div>
                            <div class="metric-label">{t('single_country')}</div>
                        </div>
                        <div class="metric-card" style="min-width: 150px; border-left-color: #2ECC71;">
                            <div class="metric-value">{geographic_analysis.get('international', 0)}</div>
                            <div class="metric-label">{t('international')}</div>
                        </div>
                        <div class="metric-card" style="min-width: 150px; border-left-color: #F39C12;">
                            <div class="metric-value">{(geographic_analysis.get('international', 0) / max(total_pubs, 1) * 100):.1f}%</div>
                            <div class="metric-label">International rate</div>
                        </div>
                    </div>
                    
                    <h4 style="margin-top: 15px; color: {primary};">{t('collaboration_couples')}</h4>
                    <div class="table-container" style="max-height: 300px;">
                        <table>
                            <thead>
                                <tr>
                                    <th>{t('country_pair')}</th>
                                    <th>{t('frequency')}</th>
                                </tr>
                            </thead>
                            <tbody>
    """
    
    country_pairs = geographic_analysis.get('country_pairs', {})
    for pair, count in list(country_pairs.items())[:20]:
        html_content += f"""
        <tr>
            <td>{html.escape(pair)}</td>
            <td>{count}</td>
        </tr>
        """
    
    html_content += f"""
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <!-- All Publications -->
                <div id="all-publications" style="margin-top: 25px;">
                    <h3 style="color: {primary};">📚 {t('all_publications')}</h3>
                    
                    <div class="filter-section">
                        <div class="filter-row">
                            <div class="filter-group">
                                <label>{t('filter_by_title')}:</label>
                                <input type="text" id="titleFilter" placeholder="Search title..." onkeyup="filterPublications()" style="width: 180px;">
                            </div>
                            <div class="filter-group">
                                <label>{t('filter_by_year')}:</label>
                                <select id="yearFilter" onchange="filterPublications()">
                                    <option value="">All</option>
    """
    
    years = sorted(set([p.year for p in analyzed_papers if p.year > 0]), reverse=True)
    for y in years:
        html_content += f'<option value="{y}">{y}</option>'
    
    html_content += f"""
                                </select>
                            </div>
                            <div class="filter-group">
                                <label>{t('filter_by_author')}:</label>
                                <input type="text" id="authorFilter" placeholder="Author..." onkeyup="filterPublications()" style="width: 150px;">
                            </div>
                            <div class="filter-group">
                                <label>{t('filter_by_affiliation')}:</label>
                                <input type="text" id="affiliationFilter" placeholder="Affiliation..." onkeyup="filterPublications()" style="width: 150px;">
                            </div>
                            <div class="filter-group">
                                <label>{t('filter_by_citations')}:</label>
                                <input type="number" id="citationFilter" placeholder="Min..." min="0" onchange="filterPublications()" style="width: 80px;">
                            </div>
                            <div>
                                <span id="visibleCount" style="font-weight: 500; font-size: 13px;">Showing all {total_pubs} publications</span>
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
                                    <th>DOI</th>
                                </tr>
                            </thead>
                            <tbody>
    """
    
    for i, paper in enumerate(analyzed_papers, 1):
        authors_text = ', '.join([a.display_name for a in paper.authors[:3]])
        if len(paper.authors) > 3:
            authors_text += f' +{len(paper.authors)-3} more'
        affiliations_text = ', '.join(paper.affiliations[:2])
        if len(paper.affiliations) > 2:
            affiliations_text += f' +{len(paper.affiliations)-2} more'
        
        citations_per_year = paper.cited_by_count / max(1, (datetime.now().year - paper.year + 1))
        
        html_content += f"""
        <tr data-year="{paper.year}" data-authors="{','.join([a.display_name for a in paper.authors])}" data-affiliations="{','.join(paper.affiliations)}" data-citations="{paper.cited_by_count}" data-title="{html.escape(paper.title.lower())}">
            <td>{i}</td>
            <td class="word-wrap">{html.escape(paper.title)}</td>
            <td>{paper.year}</td>
            <td>{html.escape(authors_text)}</td>
            <td>{html.escape(affiliations_text)}</td>
            <td>{paper.cited_by_count}</td>
            <td>{citations_per_year:.1f}</td>
            <td><a href="https://doi.org/{paper.doi}" target="_blank" class="doi-link">{paper.doi}</a></td>
        </tr>
        """
    
    html_content += f"""
                            </tbody>
                        </table>
                    </div>
                    <p style="margin-top: 10px; font-size: 13px; color: #666;">{t('total_publications')}: {total_pubs}</p>
                </div>
                
                <!-- Detailed Citations -->
                <div id="detailed-citations" style="margin-top: 25px;">
                    <h3 style="color: {primary};">📋 {t('detailed_citations')}</h3>
    """
    
    if detailed_citations:
        for pub_id, data in detailed_citations.items():
            pub_id_clean = pub_id.replace('https://openalex.org/', '').replace('/', '_')
            html_content += f"""
                    <div class="collapser" onclick="toggleCitations('{pub_id_clean}')">
                        <strong>{html.escape(data['title'][:80])}</strong>
                        <span class="badge badge-info">{data['year']}</span>
                        <span class="citation-count">{data['total_citations']} citations</span>
                        <span style="font-size: 12px; color: #666; margin-left: 5px;">DOI: {data['doi']}</span>
                        <span class="toggle-icon">▼</span>
                    </div>
                    <div id="citations_{pub_id_clean}" style="display: none;">
            """
            
            for cite in data['citations']:
                html_content += f"""
                        <div class="citation-detail">
                            <div><strong>{html.escape(cite['citing_title'][:100])}</strong></div>
                            <div class="cite-meta">
                                <strong>{t('citing_journal')}:</strong> {html.escape(cite['citing_journal'])} | 
                                <strong>{t('citing_year')}:</strong> {cite['citing_year']} | 
                                <strong>{t('citing_date')}:</strong> {cite['citing_date']} |
                                <strong>{t('citation_lag')}:</strong> {cite['citation_lag']} years
                            </div>
                            <div class="cite-meta">
                                <strong>{t('authors')}:</strong> {', '.join(cite['citing_authors'][:5])}{' +more' if len(cite['citing_authors']) > 5 else ''} |
                                <strong>{t('countries')}:</strong> {', '.join(cite['citing_countries'][:3])}{' +more' if len(cite['citing_countries']) > 3 else ''} |
                                <strong>{t('topics')}:</strong> {', '.join(cite['citing_topics'][:3])}{' +more' if len(cite['citing_topics']) > 3 else ''}
                            </div>
                            <div class="cite-meta">
                                <a href="https://doi.org/{cite['citing_doi']}" target="_blank" class="doi-link">DOI: {cite['citing_doi']}</a>
                            </div>
                        </div>
                """
            
            html_content += f"""
                    </div>
            """
    else:
        html_content += f"<p>{t('no_publications')}</p>"
    
    html_content += f"""
                </div>
            </div>
            
            <!-- ==================== CITATION ANALYSIS ==================== -->
            <div id="citation-analysis" class="section">
                <div class="section-title"><span class="icon">📊</span> {t('citation_analysis')}</div>
                
                <!-- Citation Dynamics -->
                <div id="citation-dynamics">
                    <h3 style="color: {primary};">📈 {t('citation_dynamics_by_year')}</h3>
                    <div class="table-container" style="max-height: 500px;">
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
    
    for row in citation_dynamics.get('dynamics_rows', []):
        html_content += f"""
        <tr>
            <td>{row['publication_year']}</td>
            <td>{row['citation_year']}</td>
            <td>{row['citations_count']}</td>
        </tr>
        """
    
    html_content += f"""
                            </tbody>
                        </table>
                    </div>
                    
                    <!-- First Citation Analysis -->
                    <div style="margin-top: 20px;">
                        <h4 style="color: {primary};">{t('first_citation_analysis')}</h4>
                        <div class="metrics-grid" style="grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));">
    """
    
    first_stats = citation_dynamics.get('first_citation_stats', {})
    html_content += f"""
                            <div class="metric-card"><div class="metric-value">{first_stats.get('count', 0)}</div><div class="metric-label">Papers with citations</div></div>
                            <div class="metric-card"><div class="metric-value">{first_stats.get('min', 'N/A')}</div><div class="metric-label">{t('min_days')}</div></div>
                            <div class="metric-card"><div class="metric-value">{first_stats.get('max', 'N/A')}</div><div class="metric-label">{t('max_days')}</div></div>
                            <div class="metric-card"><div class="metric-value">{first_stats.get('avg', 0):.1f}</div><div class="metric-label">{t('avg_days')}</div></div>
                            <div class="metric-card"><div class="metric-value">{first_stats.get('median', 0):.1f}</div><div class="metric-label">{t('median_days')}</div></div>
    """
    
    html_content += f"""
                        </div>
                    </div>
                </div>
                
                <!-- Cumulative Citations -->
                <div id="cumulative-citations" style="margin-top: 25px;">
                    <h3 style="color: {primary};">📊 {t('cumulative_citations')}</h3>
                    <div class="table-container" style="max-height: 300px;">
                        <table>
                            <thead>
                                <tr>
                                    <th>{t('year')}</th>
                                    <th>{t('cumulative_citations')}</th>
                                    <th style="width: 60%;">Progress</th>
                                </tr>
                            </thead>
                            <tbody>
    """
    
    cumulative = citation_dynamics.get('cumulative', {})
    max_cumulative = max(cumulative.values()) if cumulative else 1
    
    for year in sorted(cumulative.keys()):
        count = cumulative[year]
        percentage = (count / max_cumulative * 100) if max_cumulative > 0 else 0
        html_content += f"""
        <tr>
            <td>{year}</td>
            <td><strong>{count:,}</strong></td>
            <td>
                <div class="progress-container">
                    <div class="progress-bar" style="width: {percentage:.1f}%;">{percentage:.1f}%</div>
                </div>
            </td>
        </tr>
        """
    
    html_content += f"""
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <!-- Citation Network Heatmap -->
                <div id="citation-heatmap" style="margin-top: 25px;">
                    <h3 style="color: {primary};">🌡️ {t('citation_network_heatmap')}</h3>
                    <div class="heatmap-container">
                        <table class="heatmap-grid">
    """
    
    heatmap_data = citation_dynamics.get('heatmap_data', [])
    years_list = sorted(citation_dynamics.get('citation_matrix', {}).keys())
    unique_years = sorted(set([y for pair in years_list for y in pair]))
    
    if unique_years:
        # Заголовок
        html_content += "<tr><td class=\"row-header\">Pub \\ Cit</td>"
        for year in unique_years:
            html_content += f'<td class="header-cell">{year}</td>'
        html_content += "</tr>"
        
        # Данные
        max_val = max([max(row) for row in heatmap_data]) if heatmap_data and heatmap_data[0] else 1
        
        for i, row in enumerate(heatmap_data):
            if i < len(unique_years):
                pub_year = unique_years[i]
                html_content += f'<tr><td class="row-header">{pub_year}</td>'
                for j, val in enumerate(row[:len(unique_years)]):
                    if val > 0:
                        intensity = (val / max_val * 100) if max_val > 0 else 0
                        # Смешиваем primary и secondary для цвета
                        r1, g1, b1 = hex_to_rgb(primary)
                        r2, g2, b2 = hex_to_rgb(secondary)
                        r = int(r1 + (r2 - r1) * (intensity / 100))
                        g = int(g1 + (g2 - g1) * (intensity / 100))
                        b = int(b1 + (b2 - b1) * (intensity / 100))
                        color = rgb_to_hex((r, g, b))
                        text_color = get_contrast_color(color)
                        html_content += f'<td style="background: {color}; color: {text_color}; font-weight: bold;">{val}</td>'
                    else:
                        html_content += '<td style="background: #f5f5f5; color: #ccc;">-</td>'
                html_content += "</tr>"
    
    html_content += f"""
                        </table>
                    </div>
                </div>
                
                <!-- Most Cited Publications -->
                <div id="most-cited" style="margin-top: 25px;">
                    <h3 style="color: {primary};">🏆 {t('most_cited_publications')}</h3>
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
    """
    
    for i, pub in enumerate(most_cited[:20], 1):
        html_content += f"""
        <tr>
            <td>{i}</td>
            <td class="word-wrap">{html.escape(pub['title'][:120])}</td>
            <td>{pub['year']}</td>
            <td><strong>{pub['citations']}</strong></td>
            <td>{pub['citations_per_year']:.1f}</td>
            <td>{html.escape(pub['authors'])}</td>
            <td><a href="https://doi.org/{pub['doi']}" target="_blank" class="doi-link">{pub['doi']}</a></td>
        </tr>
        """
    
    html_content += f"""
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
            
            <!-- ==================== CITING WORKS ==================== -->
            <div id="citing-works" class="section">
                <div class="section-title"><span class="icon">📄</span> {t('citing_works_analysis')}</div>
                
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-value">{len(overview_metrics.get('all_citing_papers', []))}</div>
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
                
                <div id="top-citing-authors">
                    <h3 style="color: {primary};">👤 {t('top_citing_authors')}</h3>
                    <div class="table-container" style="max-height: 300px;">
                        <table>
                            <thead><tr><th>{t('rank')}</th><th>{t('authors')}</th><th>{t('publications')}</th></tr></thead>
                            <tbody>
    """
    
    for i, item in enumerate(top_citing_authors[:30], 1):
        html_content += f"""
        <tr><td>{i}</td><td>{html.escape(item['name'])}</td><td>{item['count']}</td></tr>
        """
    
    html_content += f"""
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <div id="top-citing-affiliations" style="margin-top: 20px;">
                    <h3 style="color: {primary};">🏛️ {t('top_citing_affiliations')}</h3>
                    <div class="table-container" style="max-height: 300px;">
                        <table>
                            <thead><tr><th>{t('rank')}</th><th>{t('affiliations')}</th><th>{t('publications')}</th></tr></thead>
                            <tbody>
    """
    
    for i, item in enumerate(top_citing_affiliations[:30], 1):
        html_content += f"""
        <tr><td>{i}</td><td>{html.escape(item['name'])}</td><td>{item['count']}</td></tr>
        """
    
    html_content += f"""
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <div id="top-citing-countries" style="margin-top: 20px;">
                    <h3 style="color: {primary};">🌍 {t('top_citing_countries')}</h3>
                    <div class="table-container" style="max-height: 300px;">
                        <table>
                            <thead><tr><th>{t('rank')}</th><th>{t('countries')}</th><th>{t('publications')}</th></tr></thead>
                            <tbody>
    """
    
    for i, item in enumerate(top_citing_countries[:30], 1):
        html_content += f"""
        <tr><td>{i}</td><td><span class="country-badge">{html.escape(item['name'])}</span></td><td>{item['count']}</td></tr>
        """
    
    html_content += f"""
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <div id="top-citing-journals" style="margin-top: 20px;">
                    <h3 style="color: {primary};">📚 {t('top_citing_journals')}</h3>
                    <div class="table-container" style="max-height: 300px;">
                        <table>
                            <thead><tr><th>{t('rank')}</th><th>{t('journal')}</th><th>{t('publications')}</th></tr></thead>
                            <tbody>
    """
    
    for i, item in enumerate(top_citing_journals[:30], 1):
        html_content += f"""
        <tr><td>{i}</td><td>{html.escape(item['name'])}</td><td>{item['count']}</td></tr>
        """
    
    html_content += f"""
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <div id="top-citing-publishers" style="margin-top: 20px;">
                    <h3 style="color: {primary};">🏛️ {t('top_citing_publishers')}</h3>
                    <div class="table-container" style="max-height: 300px;">
                        <table>
                            <thead><tr><th>{t('rank')}</th><th>{t('publishers')}</th><th>{t('publications')}</th></tr></thead>
                            <tbody>
    """
    
    for i, item in enumerate(top_citing_publishers[:30], 1):
        html_content += f"""
        <tr><td>{i}</td><td>{html.escape(item['name'])}</td><td>{item['count']}</td></tr>
        """
    
    html_content += f"""
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
            
            <!-- ==================== TOPICS ANALYSIS ==================== -->
            <div id="topics-analysis" class="section">
                <div class="section-title"><span class="icon">🏷️</span> {t('topics_analysis')}</div>
                
                <div id="topics-overview">
                    <h3 style="color: {primary};">📊 {t('topics_overview')}</h3>
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
    """
    
    for item in topics_analysis.get('topics', [])[:30]:
        html_content += f"""
        <tr>
            <td>{html.escape(item['topic'])}</td>
            <td>{item['analyzed_count']}</td>
            <td>{item['citing_count']}</td>
            <td>{item['analyzed_norm']:.3f}</td>
            <td>{item['citing_norm']:.3f}</td>
            <td><strong>{item['total_norm']:.3f}</strong></td>
            <td>{item['first_year'] or 'N/A'}</td>
            <td>{item['peak_year'] or 'N/A'}</td>
        </tr>
        """
    
    html_content += f"""
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <div id="topic-relationships" style="margin-top: 25px;">
                    <h3 style="color: {primary};">🔗 {t('top_cited_topics')}</h3>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
    """
    
    rel = topic_relationships
    categories = [
        ('topics', t('top_cited_topics')),
        ('subtopics', t('top_cited_subtopics')),
        ('fields', t('top_cited_fields')),
        ('domains', t('top_cited_domains')),
        ('concepts', t('top_cited_concepts'))
    ]
    
    for key, label in categories:
        data = rel.get(key, {})
        html_content += f"""
                        <div>
                            <h4 style="color: {primary};">{label}</h4>
                            <ul style="list-style: none; padding: 0;">
        """
        for name, count in list(data.items())[:10]:
            html_content += f"""
                                <li style="padding: 4px 8px; border-bottom: 1px solid #eee; display: flex; justify-content: space-between;">
                                    <span>{html.escape(name)}</span>
                                    <span style="font-weight: bold; color: {primary};">{count}</span>
                                </li>
            """
        html_content += """
                            </ul>
                        </div>
        """
    
    html_content += f"""
                    </div>
                </div>
            </div>
            
            <!-- Footer -->
            <div class="footer">
                <p>{t('footer')}</p>
                <p><a href="{t('journal_url')}" target="_blank">{t('journal_url')}</a></p>
                <p style="font-size: 11px; margin-top: 5px;">{t('data_source')} | {t('generated')}: {datetime.now().strftime('%d.%m.%Y %H:%M')}</p>
                <p style="font-size: 11px; color: #999;">ISSN: {issn} | {t('period')}: {period_display}</p>
            </div>
        </div>
        
        <!-- JavaScript for interactivity -->
        <script>
            function toggleCitations(id) {{
                var div = document.getElementById('citations_' + id);
                if (div) {{
                    if (div.style.display === 'none') {{
                        div.style.display = 'block';
                    }} else {{
                        div.style.display = 'none';
                    }}
                }}
            }}
            
            function filterPublications() {{
                var titleFilter = document.getElementById('titleFilter');
                var yearFilter = document.getElementById('yearFilter');
                var authorFilter = document.getElementById('authorFilter');
                var affiliationFilter = document.getElementById('affiliationFilter');
                var citationFilter = document.getElementById('citationFilter');
                var table = document.getElementById('publicationsTable');
                var rows = table.getElementsByTagName('tbody')[0].getElementsByTagName('tr');
                var visible = 0;
                
                var titleText = titleFilter ? titleFilter.value.toLowerCase() : '';
                var yearVal = yearFilter ? yearFilter.value : '';
                var authorText = authorFilter ? authorFilter.value.toLowerCase() : '';
                var affiliationText = affiliationFilter ? affiliationFilter.value.toLowerCase() : '';
                var citationMin = citationFilter ? parseInt(citationFilter.value) || 0 : 0;
                
                for (var i = 0; i < rows.length; i++) {{
                    var row = rows[i];
                    var year = row.getAttribute('data-year') || '';
                    var authors = row.getAttribute('data-authors') || '';
                    var affiliations = row.getAttribute('data-affiliations') || '';
                    var citations = parseInt(row.getAttribute('data-citations')) || 0;
                    var title = row.getAttribute('data-title') || '';
                    
                    var show = true;
                    
                    if (titleText && !title.includes(titleText)) show = false;
                    if (yearVal && year !== yearVal) show = false;
                    if (authorText && !authors.toLowerCase().includes(authorText)) show = false;
                    if (affiliationText && !affiliations.toLowerCase().includes(affiliationText)) show = false;
                    if (citations < citationMin) show = false;
                    
                    if (show) {{
                        row.style.display = '';
                        visible++;
                    }} else {{
                        row.style.display = 'none';
                    }}
                }}
                
                var countSpan = document.getElementById('visibleCount');
                if (countSpan) {{
                    countSpan.textContent = 'Showing ' + visible + ' of ' + rows.length + ' publications';
                }}
            }}
            
            function sortTable(column) {{
                var table = document.getElementById('publicationsTable');
                var tbody = table.getElementsByTagName('tbody')[0];
                var rows = tbody.getElementsByTagName('tr');
                var sorted = Array.from(rows);
                var ascending = table.getAttribute('data-sort-' + column) !== 'asc';
                
                sorted.sort(function(a, b) {{
                    var aVal = a.getElementsByTagName('td')[column].textContent.trim();
                    var bVal = b.getElementsByTagName('td')[column].textContent.trim();
                    
                    var aNum = parseFloat(aVal);
                    var bNum = parseFloat(bVal);
                    if (!isNaN(aNum) && !isNaN(bNum)) {{
                        return ascending ? aNum - bNum : bNum - aNum;
                    }}
                    return ascending ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
                }});
                
                for (var i = 0; i < sorted.length; i++) {{
                    tbody.appendChild(sorted[i]);
                }}
                
                table.setAttribute('data-sort-' + column, ascending ? 'asc' : 'desc');
            }}
        </script>
    </body>
    </html>
    """
    
    return html_content

# ============================================
# ОСНОВНАЯ ФУНКЦИЯ ЗАПУСКА ДЛЯ STREAMLIT
# ============================================

def run_journal_analysis(issn: str, period: str, journal_logo: Optional[Dict] = None):
    """
    Запускает полный анализ журнала с бар-прогрессом по этапам.
    """
    # Get current language for translations
    current_lang = st.session_state.get('language', 'en')
    def t(key: str, **kwargs) -> str:
        return translate(key, current_lang, **kwargs)
    
    if not issn or not period:
        st.error("⚠️ " + t('issn_input') + " и " + t('period_input') + " обязательны для заполнения")
        return
    
    # Сброс флага остановки
    set_stop_flag(False)
    
    # Парсим период
    period_result = parse_period(period)
    if period_result is None or (period_result[0] is None and period_result[1] is None):
        st.error(f"⚠️ Неверный формат периода: {period}. Используйте '2020-2026' или '2020,2021,2022'")
        return
    
    years_list, years_range = period_result
    period_data = years_list if years_list else years_range
    
    # Проверяем кэш
    cache_data = load_from_cache(issn, period) if USE_CACHE else None
    if cache_data:
        st.success(f"✅ Данные загружены из кэша для ISSN: {issn}")
        # Восстанавливаем данные из кэша
        analyzed_papers = [AnalyzedPaper(**p) for p in cache_data.get('analyzed_papers', [])]
        citing_papers_dict = cache_data.get('citing_papers_dict', {})
        # Преобразуем обратно в объекты CitingPaper
        citing_papers_obj = {}
        for doi, citing_list in citing_papers_dict.items():
            citing_papers_obj[doi] = [CitingPaper(**c) for c in citing_list]
        
        # Пересчитываем все метрики
        overview_metrics = calculate_overview_metrics(analyzed_papers, citing_papers_obj)
        citation_dynamics = calculate_citation_dynamics(analyzed_papers, citing_papers_obj, 
                                                       years_range[0] if years_range else min(years_list),
                                                       years_range[1] if years_range else max(years_list))
        author_analysis = calculate_author_analysis(analyzed_papers)
        affiliation_analysis = calculate_affiliation_analysis(analyzed_papers)
        geographic_analysis = calculate_geographic_analysis(analyzed_papers)
        topics_analysis = calculate_topics_analysis(analyzed_papers, citing_papers_obj)
        most_cited = calculate_most_cited_publications(analyzed_papers)
        
        all_citing_papers = overview_metrics.get('all_citing_papers', [])
        top_citing_authors = calculate_top_citing_items(all_citing_papers, 'authors')
        top_citing_affiliations = calculate_top_citing_items(all_citing_papers, 'affiliations')
        top_citing_countries = calculate_top_citing_items(all_citing_papers, 'countries')
        top_citing_journals = calculate_top_citing_items(all_citing_papers, 'journals')
        top_citing_publishers = calculate_top_citing_items(all_citing_papers, 'publishers')
        topic_relationships = calculate_topic_relationships(analyzed_papers, citing_papers_obj)
        detailed_citations = get_detailed_citations(analyzed_papers, citing_papers_obj)
        
        # Загружаем логотипы
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
                if SHOW_DEBUG_LOGS:
                    print(f"⚠️ Ошибка загрузки логотипа журнала: {e}")
        
        # Генерируем отчет
        theme_colors = {
            'primary': st.session_state.get('primary_color', '#667eea'),
            'secondary': st.session_state.get('secondary_color', '#f39c12')
        }
        
        html_report = generate_html_report(
            issn, period,
            analyzed_papers,
            citing_papers_obj,
            overview_metrics,
            citation_dynamics,
            author_analysis,
            affiliation_analysis,
            geographic_analysis,
            topics_analysis,
            most_cited,
            top_citing_authors,
            top_citing_affiliations,
            top_citing_countries,
            top_citing_journals,
            top_citing_publishers,
            topic_relationships,
            detailed_citations,
            journal_logo_base64,
            app_logo_base64,
            theme_colors,
            current_lang
        )
        
        st.session_state['html_report'] = html_report
        st.session_state['analysis_complete'] = True
        st.session_state['issn'] = issn
        st.session_state['period'] = period
        
        # Кнопка скачивания
        st.download_button(
            label="📥 " + t('download_report'),
            data=html_report.encode('utf-8'),
            file_name=f"journal_analysis_{issn}_{period}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
            mime="text/html",
            use_container_width=True
        )
        
        # Предпросмотр
        with st.expander("📋 " + t('report_preview'), expanded=True):
            st.components.v1.html(html_report, height=800, scrolling=True)
        
        return
    
    # Прогресс-бары для этапов
    st.info(f"🔍 " + t('journal_analysis') + f" для ISSN: {issn}, период: {period}")
    
    progress_container = st.empty()
    status_container = st.empty()
    stop_container = st.empty()
    
    # Кнопка остановки
    if stop_container.button(t('stop_analysis'), type="primary"):
        set_stop_flag(True)
        st.warning(t('analysis_stopped'))
        return
    
    # Этапы с весами
    stage_weights = {
        'stage1': 0.20,  # Сбор DOI статей журнала
        'stage2': 0.25,  # Сбор цитирующих DOI (параллельно)
        'stage3': 0.20,  # Обогащение анализируемых статей
        'stage4': 0.25,  # Обогащение цитирующих статей
        'stage5': 0.10   # Анализ и генерация отчета
    }
    
    progress_bar = st.progress(0, text=t('starting_analysis'))
    
    try:
        # ====== ЭТАП 1: Сбор DOI статей журнала ======
        status_container.info("📚 " + t('stage_1'))
        progress_bar.progress(0.01, text=t('stage_1'))
        
        def stage1_progress(page, total, new_count):
            progress = 0.01 + (page * 0.01) * stage_weights['stage1']
            progress_bar.progress(min(progress, stage_weights['stage1'] * 0.9), 
                                 text=f"📚 {t('stage_1')}: {total} статей найдено")
        
        def stop_check():
            return get_stop_flag()
        
        analyzed_papers_list = collect_analyzed_papers(
            issn, period_data, 
            progress_callback=stage1_progress,
            stop_callback=stop_check
        )
        
        if get_stop_flag():
            st.warning(t('analysis_stopped'))
            progress_bar.empty()
            return
        
        if not analyzed_papers_list:
            st.error(f"❌ Статей не найдено для ISSN: {issn}")
            progress_bar.empty()
            return
        
        st.success(f"✅ Найдено {len(analyzed_papers_list)} статей")
        progress_bar.progress(stage_weights['stage1'], text=f"✅ {t('stage_1')}: {len(analyzed_papers_list)} статей")
        
        # ====== ЭТАП 2: Сбор цитирующих DOI (параллельно) ======
        status_container.info("⚡ " + t('stage_2'))
        progress_bar.progress(stage_weights['stage1'] + 0.01, text=t('stage_2'))
        
        def stage2_progress(processed, total, doi):
            progress = stage_weights['stage1'] + (processed / max(total, 1)) * stage_weights['stage2'] * 0.9
            progress_bar.progress(min(progress, stage_weights['stage1'] + stage_weights['stage2'] * 0.9),
                                 text=f"⚡ {t('stage_2')}: {processed}/{total} DOI обработано")
        
        citing_map = collect_citing_dois_parallel(
            analyzed_papers_list,
            progress_callback=stage2_progress,
            stop_callback=stop_check,
            max_workers=MAX_WORKERS
        )
        
        if get_stop_flag():
            st.warning(t('analysis_stopped'))
            progress_bar.empty()
            return
        
        st.success(f"✅ Собрано цитирующих DOI для {len(citing_map)} статей")
        progress_bar.progress(stage_weights['stage1'] + stage_weights['stage2'], 
                             text=f"✅ {t('stage_2')}: {len(citing_map)} статей обработано")
        
        # ====== ЭТАП 3: Обогащение анализируемых статей ======
        status_container.info("📊 " + t('stage_3'))
        progress_bar.progress(stage_weights['stage1'] + stage_weights['stage2'] + 0.01, text=t('stage_3'))
        
        def stage3_progress(current, total, doi):
            progress = stage_weights['stage1'] + stage_weights['stage2'] + (current / max(total, 1)) * stage_weights['stage3'] * 0.9
            progress_bar.progress(min(progress, stage_weights['stage1'] + stage_weights['stage2'] + stage_weights['stage3'] * 0.9),
                                 text=f"📊 {t('stage_3')}: {current}/{total} DOI обработано")
        
        analyzed_papers = enrich_analyzed_papers(
            analyzed_papers_list,
            citing_map,
            progress_callback=stage3_progress,
            stop_callback=stop_check
        )
        
        if get_stop_flag():
            st.warning(t('analysis_stopped'))
            progress_bar.empty()
            return
        
        st.success(f"✅ Обогащено {len(analyzed_papers)} статей")
        progress_bar.progress(stage_weights['stage1'] + stage_weights['stage2'] + stage_weights['stage3'],
                             text=f"✅ {t('stage_3')}: {len(analyzed_papers)} статей")
        
        # ====== ЭТАП 4: Обогащение цитирующих статей ======
        status_container.info("📊 " + t('stage_4'))
        progress_bar.progress(stage_weights['stage1'] + stage_weights['stage2'] + stage_weights['stage3'] + 0.01, text=t('stage_4'))
        
        def stage4_progress(current, total, doi):
            progress = stage_weights['stage1'] + stage_weights['stage2'] + stage_weights['stage3'] + (current / max(total, 1)) * stage_weights['stage4'] * 0.9
            progress_bar.progress(min(progress, stage_weights['stage1'] + stage_weights['stage2'] + stage_weights['stage3'] + stage_weights['stage4'] * 0.9),
                                 text=f"📊 {t('stage_4')}: {current}/{total} DOI обработано")
        
        citing_papers_dict = enrich_citing_papers(
            analyzed_papers,
            progress_callback=stage4_progress,
            stop_callback=stop_check
        )
        
        if get_stop_flag():
            st.warning(t('analysis_stopped'))
            progress_bar.empty()
            return
        
        total_citations = sum(len(v) for v in citing_papers_dict.values())
        st.success(f"✅ Обогащено {total_citations} цитирующих статей")
        progress_bar.progress(stage_weights['stage1'] + stage_weights['stage2'] + stage_weights['stage3'] + stage_weights['stage4'],
                             text=f"✅ {t('stage_4')}: {total_citations} цитирующих статей")
        
        # ====== ЭТАП 5: Анализ и генерация отчета ======
        status_container.info("📊 " + t('stage_5'))
        progress_bar.progress(stage_weights['stage1'] + stage_weights['stage2'] + stage_weights['stage3'] + stage_weights['stage4'] + 0.01,
                             text=t('stage_5'))
        
        # Расчет всех метрик
        overview_metrics = calculate_overview_metrics(analyzed_papers, citing_papers_dict)
        
        start_year = years_range[0] if years_range else min(years_list)
        end_year = years_range[1] if years_range else max(years_list)
        citation_dynamics = calculate_citation_dynamics(analyzed_papers, citing_papers_dict, start_year, end_year)
        
        author_analysis = calculate_author_analysis(analyzed_papers)
        affiliation_analysis = calculate_affiliation_analysis(analyzed_papers)
        geographic_analysis = calculate_geographic_analysis(analyzed_papers)
        topics_analysis = calculate_topics_analysis(analyzed_papers, citing_papers_dict)
        most_cited = calculate_most_cited_publications(analyzed_papers)
        
        all_citing_papers = overview_metrics.get('all_citing_papers', [])
        top_citing_authors = calculate_top_citing_items(all_citing_papers, 'authors')
        top_citing_affiliations = calculate_top_citing_items(all_citing_papers, 'affiliations')
        top_citing_countries = calculate_top_citing_items(all_citing_papers, 'countries')
        top_citing_journals = calculate_top_citing_items(all_citing_papers, 'journals')
        top_citing_publishers = calculate_top_citing_items(all_citing_papers, 'publishers')
        topic_relationships = calculate_topic_relationships(analyzed_papers, citing_papers_dict)
        detailed_citations = get_detailed_citations(analyzed_papers, citing_papers_dict)
        
        progress_bar.progress(stage_weights['stage1'] + stage_weights['stage2'] + stage_weights['stage3'] + stage_weights['stage4'] + stage_weights['stage5'] * 0.5,
                             text=f"📊 {t('stage_5')}: формирование отчета...")
        
        # Сохраняем в кэш
        if USE_CACHE:
            cache_data = {
                'analyzed_papers': [vars(p) for p in analyzed_papers],
                'citing_papers_dict': {
                    doi: [vars(c) for c in citing_list] 
                    for doi, citing_list in citing_papers_dict.items()
                },
                'timestamp': datetime.now().isoformat()
            }
            save_to_cache(issn, period, cache_data)
        
        # Загружаем логотипы
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
                if SHOW_DEBUG_LOGS:
                    print(f"⚠️ Ошибка загрузки логотипа журнала: {e}")
        
        # Генерируем отчет
        theme_colors = {
            'primary': st.session_state.get('primary_color', '#667eea'),
            'secondary': st.session_state.get('secondary_color', '#f39c12')
        }
        
        html_report = generate_html_report(
            issn, period,
            analyzed_papers,
            citing_papers_dict,
            overview_metrics,
            citation_dynamics,
            author_analysis,
            affiliation_analysis,
            geographic_analysis,
            topics_analysis,
            most_cited,
            top_citing_authors,
            top_citing_affiliations,
            top_citing_countries,
            top_citing_journals,
            top_citing_publishers,
            topic_relationships,
            detailed_citations,
            journal_logo_base64,
            app_logo_base64,
            theme_colors,
            current_lang
        )
        
        progress_bar.progress(1.0, text="✅ " + t('analysis_complete_text') + "!")
        status_container.success("✅ " + t('analysis_complete_text'))
        
        st.session_state['html_report'] = html_report
        st.session_state['analysis_complete'] = True
        st.session_state['issn'] = issn
        st.session_state['period'] = period
        
        # Кнопка скачивания
        st.download_button(
            label="📥 " + t('download_report'),
            data=html_report.encode('utf-8'),
            file_name=f"journal_analysis_{issn}_{period}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
            mime="text/html",
            use_container_width=True
        )
        
        # Предпросмотр
        with st.expander("📋 " + t('report_preview'), expanded=True):
            st.components.v1.html(html_report, height=800, scrolling=True)
        
        st.balloons()
        
    except Exception as e:
        st.error(f"❌ {t('error_occurred')}: {str(e)}")
        import traceback
        st.code(traceback.format_exc())
    finally:
        progress_bar.empty()
        stop_container.empty()

# ============================================
# СОЗДАНИЕ WIDGET-ИНТЕРФЕЙСА STREAMLIT
# ============================================

def main():
    # Page configuration
    st.set_page_config(
        page_title="Advanced Journal Analysis Tool",
        page_icon="🔬",
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
    if 'html_report' not in st.session_state:
        st.session_state.html_report = None
    if 'issn' not in st.session_state:
        st.session_state.issn = None
    if 'period' not in st.session_state:
        st.session_state.period = None
    
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
            if os.path.exists('journal_cache'):
                shutil.rmtree('journal_cache')
            st.cache_data.clear()
            st.success(t('cache_cleared'))
        
        st.markdown("---")
        
        st.markdown(f"""
        <div style="font-size: 11px; color: #666; text-align: center;">
            © daM / Chimica Techno Acta \ https://chimicatechnoacta.ru
        </div>
        """, unsafe_allow_html=True)
    
    # Main interface
    st.markdown("---")
    
    # Logo
    col_logo, col_spacer, col_title = st.columns([1, 0.1, 3])
    with col_logo:
        if os.path.exists("logo.png"):
            st.image("logo.png", width=400)
        else:
            st.markdown(f"### 🔬 {t('app_logo')}")
    
    st.markdown("---")
    
    # Input section
    col1, col2 = st.columns([1, 1])
    
    with col1:
        issn_input = st.text_input(
            t('issn_input'),
            placeholder=t('issn_placeholder'),
            help="Enter the ISSN of the journal to analyze"
        )
    
    with col2:
        period_input = st.text_input(
            t('period_input'),
            placeholder=t('period_placeholder'),
            help="Enter period as '2020-2026' or '2020,2021,2022'"
        )
    
    # Logo upload
    journal_logo_upload = st.file_uploader(
        t('upload_logo'),
        type=['png', 'jpg', 'jpeg', 'svg'],
        help=t('logo_help')
    )
    
    # Analyze button
    if st.button(t('analyze_button'), type="primary", use_container_width=True):
        journal_logo_data = None
        if journal_logo_upload:
            journal_logo_data = {
                journal_logo_upload.name: {
                    'content': journal_logo_upload.read()
                }
            }
        
        run_journal_analysis(issn_input, period_input, journal_logo_data)
    
    st.markdown("---")
    
    # Display report if already generated
    if st.session_state.analysis_complete and st.session_state.html_report:
        st.success(f"✅ {t('analysis_complete_text')} для ISSN: {st.session_state.issn}, период: {st.session_state.period}")
        
        # Кнопка скачивания
        st.download_button(
            label="📥 " + t('download_report'),
            data=st.session_state.html_report.encode('utf-8'),
            file_name=f"journal_analysis_{st.session_state.issn}_{st.session_state.period}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
            mime="text/html",
            use_container_width=True
        )
        
        # Предпросмотр
        with st.expander("📋 " + t('report_preview'), expanded=True):
            st.components.v1.html(st.session_state.html_report, height=800, scrolling=True)

if __name__ == "__main__":
    main()
