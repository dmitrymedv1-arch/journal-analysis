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

# Параметры для анализа журналов
MAX_WORKERS = 8  # Количество параллельных потоков для сбора цитирований
BASE_DELAY = 0.35  # Базовая задержка между запросами
MAX_CITING_PER_PAPER = 300  # Максимум цитирующих статей на одну публикацию

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
        'journal_analysis': '📊 Journal Analysis',
        'reports': '📄 Reports',
        'issn_input': 'Journal ISSN',
        'issn_placeholder': '0028-0836',
        'issn_help': 'Enter ISSN of the journal (format: XXXX-XXXX)',
        'period_input': 'Analysis Period',
        'period_placeholder': '2020-2023 or 2020,2021,2022 or 2020',
        'period_help': 'Format: YYYY-YYYY (range), YYYY,YYYY,YYYY (list), or YYYY (single year)',
        'workers_slider': 'Parallel Workers',
        'workers_help': 'Number of parallel threads for citation fetching (4-12)',
        'analyze_button': '🔍 Analyze Journal',
        'no_issn': '⚠️ Please enter ISSN',
        'no_period': '⚠️ Please enter analysis period',
        'analysis_complete': '✅ Analysis complete! Found {count} publications in {time:.1f} sec.',
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
        # Новые переводы для Journal Analysis
        'journal_analysis_title': 'Advanced Journal Analysis Tool',
        'journal_analysis_desc': 'Comprehensive analysis of journal publications and their citations',
        'stage_fetching_articles': '📚 Fetching journal articles...',
        'stage_fetching_citations': '🔗 Fetching citing articles...',
        'stage_analyzing': '📊 Analyzing data...',
        'stage_generating_report': '📄 Generating report...',
        'articles_found': 'Articles found: {count}',
        'citations_fetched': 'Citations fetched: {count}',
        'analyzed_publications': 'Analyzed Publications',
        'citing_publications': 'Citing Publications',
        'unique_authors': 'Unique Authors',
        'unique_affiliations': 'Unique Affiliations',
        'unique_countries': 'Unique Countries',
        'avg_authors': 'Avg Authors/Paper',
        'avg_affiliations': 'Avg Affiliations/Paper',
        'avg_countries': 'Avg Countries/Paper',
        'int_collab_rate': 'International Collaboration Rate',
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
        'author_analysis': 'Author Analysis',
        'rank': 'Rank',
        'authors': 'Authors',
        'publications_count': 'Publications',
        'top_affiliations': 'Top Affiliations',
        'geographic_analysis': 'Geographic Analysis',
        'unique_countries_per_publication': 'Unique Countries per Publication (Collaboration Level)',
        'each_publication_counted_once': 'Each publication counted once per unique country',
        'authors_per_country': 'Authors per Country (Individual Distribution)',
        'each_author_counted_separately': 'Each author counted separately',
        'collaboration_patterns': 'Collaboration Patterns',
        'distribution_of_single_country_vs_international': 'Distribution of single-country vs international collaborations',
        'collaboration_couples': 'Collaboration Couples',
        'frequency_of_country_pairs_collaborating': 'Frequency of country pairs collaborating',
        'citation_analysis': 'Citation Analysis',
        'citation_dynamics_by_year': 'Citation Dynamics by Year',
        'publication_year_col': 'Publication Year',
        'citation_year_col': 'Citation Year',
        'citations_count_col': 'Citations Count',
        'cumulative_citations': 'Cumulative Citations',
        'citation_network_heatmap': 'Citation Network Heatmap',
        'most_cited_publications': 'Most Cited Publications',
        'citations_per_year_col': 'Citations/Year',
        'citing_works_analysis': 'Citing Works Analysis',
        'total_citing_works': 'Total Citing Works',
        'top_citing_authors': 'Top Citing Authors',
        'top_citing_affiliations': 'Top Citing Affiliations',
        'top_citing_countries': 'Top Citing Countries',
        'top_citing_journals': 'Top Citing Journals',
        'top_citing_publishers': 'Top Citing Publishers',
        'topics_analysis': 'Topics Analysis',
        'analyzed_count': 'Analyzed Count',
        'citing_count': 'Citing Count',
        'analyzed_norm_count': 'Analyzed Norm Count',
        'citing_norm_count': 'Citing Norm Count',
        'total_norm_count': 'Total Norm Count',
        'first_year': 'First Year',
        'peak_year': 'Peak Year',
        'recent_5_years_count': 'Recent 5 Years Count',
        'detailed_citations': 'Detailed Citations',
        'show_citations': 'Show Citations',
        'citing_journal': 'Citing Journal',
        'citing_year': 'Citing Year',
        'citing_date': 'Citing Date',
        'citation_lag': 'Citation Lag',
        'all_publications': 'All Publications',
        'filter_by_year': 'Filter by Year',
        'filter_by_author': 'Filter by Author',
        'filter_by_citations': 'Filter by Citations (min)',
        'search_publications': 'Search Publications',
        'all_years': 'All Years',
        'filter_by_affiliation': 'Filter by Affiliation',
        'filter_by_title': 'Filter by Title Word(s)',
        'citing_works': 'Citing Works',
        'total_citing_publications': 'Total Citing Publications',
        'overview': 'Overview',
        'analyzed_articles': 'Analyzed Articles',
        'citing_works_analysis_title': 'Citing Works Analysis',
        'topics_analysis_title': 'Topics Analysis',
        'detailed_citations_title': 'Detailed Citations',
        'all_publications_title': 'All Publications',
        'publication': 'Publication',
        'citations_count': 'Citations',
        'citation_count': 'Citation Count',
        'analyzed_publications_count': 'Analyzed Publications',
        'citing_publications_count': 'Citing Publications',
        'unique_authors_count': 'Unique Authors',
        'unique_affiliations_count': 'Unique Affiliations',
        'unique_countries_count': 'Unique Countries',
        'avg_authors_per_paper_value': 'Avg Authors/Paper',
        'avg_affiliations_per_paper_value': 'Avg Affiliations/Paper',
        'avg_countries_per_paper_value': 'Avg Countries/Paper',
        'international_collaboration_rate_value': 'International Collaboration Rate',
        'unique_citing_authors_count': 'Unique Citing Authors',
        'unique_citing_affiliations_count': 'Unique Citing Affiliations',
        'unique_citing_countries_count': 'Unique Citing Countries',
        'unique_citing_journals_count': 'Unique Citing Journals',
        'unique_citing_publishers_count': 'Unique Citing Publishers',
        'gold_open_access': 'Gold',
        'hybrid_open_access': 'Hybrid',
        'green_open_access': 'Green',
        'bronze_open_access': 'Bronze',
        'closed_open_access': 'Closed',
        'unknown_open_access': 'Unknown',
        'top_authors': 'Top Authors',
        'top_affiliations_analyzed': 'Top Affiliations',
        'geographic_analysis_title': 'Geographic Analysis',
        'citation_dynamics_title': 'Citation Dynamics by Year',
        'cumulative_citations_title': 'Cumulative Citations',
        'citation_heatmap_title': 'Citation Network Heatmap',
        'most_cited_title': 'Most Cited Publications',
        'top_citing_authors_title': 'Top Citing Authors',
        'top_citing_affiliations_title': 'Top Citing Affiliations',
        'top_citing_countries_title': 'Top Citing Countries',
        'top_citing_journals_title': 'Top Citing Journals',
        'top_citing_publishers_title': 'Top Citing Publishers',
        'topics_analysis_table': 'Topics Analysis',
        'topic_name': 'Topic',
        'click_to_toggle': 'Click to toggle citations',
        'single_country': 'Single-Country',
        'international_collab': 'International',
        'citation_year': 'Citation Year',
        'publication_year_header': 'Publication Year',
        'title_header': 'Title',
        'year_header': 'Year',
        'citations_header': 'Citations',
        'citations_per_year_header': 'Citations/Year',
        'journal_header': 'Journal',
        'doi_header': 'DOI',
        'authors_header': 'Authors',
        'affiliations_header': 'Affiliations',
        'countries_header': 'Countries',
        'show': 'Show',
        'hide': 'Hide',
        'citing_works_count': 'Citing Works',
        'analyzed_works_count': 'Analyzed Works',
        'topic_advancements_solid_oxide_fuel_cells': 'Advancements in Solid Oxide Fuel Cells',
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
        'journal_analysis': '📊 Анализ журнала',
        'reports': '📄 Отчеты',
        'issn_input': 'ISSN журнала',
        'issn_placeholder': '0028-0836',
        'issn_help': 'Введите ISSN журнала (формат: XXXX-XXXX)',
        'period_input': 'Период анализа',
        'period_placeholder': '2020-2023 или 2020,2021,2022 или 2020',
        'period_help': 'Формат: ГГГГ-ГГГГ (диапазон), ГГГГ,ГГГГ,ГГГГ (список), или ГГГГ (один год)',
        'workers_slider': 'Параллельных потоков',
        'workers_help': 'Количество параллельных потоков для сбора цитирований (4-12)',
        'analyze_button': '🔍 Анализировать журнал',
        'no_issn': '⚠️ Введите ISSN',
        'no_period': '⚠️ Введите период анализа',
        'analysis_complete': '✅ Анализ завершен! Найдено {count} публикаций за {time:.1f} сек.',
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
        # Новые переводы для Journal Analysis
        'journal_analysis_title': 'Расширенный инструмент анализа журналов',
        'journal_analysis_desc': 'Комплексный анализ публикаций журнала и их цитирований',
        'stage_fetching_articles': '📚 Получение статей журнала...',
        'stage_fetching_citations': '🔗 Получение цитирующих статей...',
        'stage_analyzing': '📊 Анализ данных...',
        'stage_generating_report': '📄 Генерация отчета...',
        'articles_found': 'Найдено статей: {count}',
        'citations_fetched': 'Получено цитирований: {count}',
        'analyzed_publications': 'Анализируемых публикаций',
        'citing_publications': 'Цитирующих публикаций',
        'unique_authors': 'Уникальных авторов',
        'unique_affiliations': 'Уникальных аффилиаций',
        'unique_countries': 'Уникальных стран',
        'avg_authors': 'Среднее авторов/статью',
        'avg_affiliations': 'Среднее аффилиаций/статью',
        'avg_countries': 'Среднее стран/статью',
        'int_collab_rate': 'Доля международных коллабораций',
        'unique_citing_authors': 'Уникальных цитирующих авторов',
        'unique_citing_affiliations': 'Уникальных цитирующих аффилиаций',
        'unique_citing_countries': 'Уникальных цитирующих стран',
        'unique_citing_journals': 'Уникальных цитирующих журналов',
        'unique_citing_publishers': 'Уникальных цитирующих издателей',
        'open_access_breakdown': 'Разбивка по открытому доступу',
        'gold': 'Золотой',
        'hybrid': 'Гибридный',
        'green': 'Зеленый',
        'bronze': 'Бронзовый',
        'closed': 'Закрытый',
        'unknown': 'Неизвестно',
        'author_analysis': 'Анализ авторов',
        'rank': 'Ранг',
        'authors': 'Авторы',
        'publications_count': 'Публикаций',
        'top_affiliations': 'Топ аффилиаций',
        'geographic_analysis': 'Географический анализ',
        'unique_countries_per_publication': 'Уникальные страны на публикацию (Уровень коллаборации)',
        'each_publication_counted_once': 'Каждая публикация учтена один раз на уникальную страну',
        'authors_per_country': 'Авторы по странам (Индивидуальное распределение)',
        'each_author_counted_separately': 'Каждый автор учтен отдельно',
        'collaboration_patterns': 'Модели коллабораций',
        'distribution_of_single_country_vs_international': 'Распределение внутристрановых и международных коллабораций',
        'collaboration_couples': 'Пары коллабораций',
        'frequency_of_country_pairs_collaborating': 'Частота пар стран, сотрудничающих вместе',
        'citation_analysis': 'Цитационный анализ',
        'citation_dynamics_by_year': 'Динамика цитирований по годам',
        'publication_year_col': 'Год публикации',
        'citation_year_col': 'Год цитирования',
        'citations_count_col': 'Количество цитирований',
        'cumulative_citations': 'Накопленные цитирования',
        'citation_network_heatmap': 'Тепловая карта цитирований',
        'most_cited_publications': 'Самые цитируемые публикации',
        'citations_per_year_col': 'Цитирований/год',
        'citing_works_analysis': 'Анализ цитирующих работ',
        'total_citing_works': 'Всего цитирующих работ',
        'top_citing_authors': 'Топ цитирующих авторов',
        'top_citing_affiliations': 'Топ цитирующих аффилиаций',
        'top_citing_countries': 'Топ цитирующих стран',
        'top_citing_journals': 'Топ цитирующих журналов',
        'top_citing_publishers': 'Топ цитирующих издателей',
        'topics_analysis': 'Тематический анализ',
        'analyzed_count': 'Кол-во в анализируемых',
        'citing_count': 'Кол-во в цитирующих',
        'analyzed_norm_count': 'Норм. кол-во в анализируемых',
        'citing_norm_count': 'Норм. кол-во в цитирующих',
        'total_norm_count': 'Общее норм. кол-во',
        'first_year': 'Первый год',
        'peak_year': 'Пиковый год',
        'recent_5_years_count': 'Последние 5 лет',
        'detailed_citations': 'Детальные цитирования',
        'show_citations': 'Показать цитирования',
        'citing_journal': 'Цитирующий журнал',
        'citing_year': 'Год цитирования',
        'citing_date': 'Дата цитирования',
        'citation_lag': 'Задержка цитирования',
        'all_publications': 'Все публикации',
        'filter_by_year': 'Фильтр по году',
        'filter_by_author': 'Фильтр по автору',
        'filter_by_citations': 'Фильтр по цитированиям (мин)',
        'search_publications': 'Поиск публикаций',
        'all_years': 'Все годы',
        'filter_by_affiliation': 'Фильтр по аффилиации',
        'filter_by_title': 'Фильтр по словам в названии',
        'citing_works': 'Цитирующие работы',
        'total_citing_publications': 'Всего цитирующих публикаций',
        'overview': 'Обзор',
        'analyzed_articles': 'Анализируемые статьи',
        'citing_works_analysis_title': 'Анализ цитирующих работ',
        'topics_analysis_title': 'Тематический анализ',
        'detailed_citations_title': 'Детальные цитирования',
        'all_publications_title': 'Все публикации',
        'publication': 'Публикация',
        'citations_count': 'Цитирований',
        'citation_count': 'Количество цитирований',
        'analyzed_publications_count': 'Анализируемых публикаций',
        'citing_publications_count': 'Цитирующих публикаций',
        'unique_authors_count': 'Уникальных авторов',
        'unique_affiliations_count': 'Уникальных аффилиаций',
        'unique_countries_count': 'Уникальных стран',
        'avg_authors_per_paper_value': 'Среднее авторов/статью',
        'avg_affiliations_per_paper_value': 'Среднее аффилиаций/статью',
        'avg_countries_per_paper_value': 'Среднее стран/статью',
        'international_collaboration_rate_value': 'Доля международных коллабораций',
        'unique_citing_authors_count': 'Уникальных цитирующих авторов',
        'unique_citing_affiliations_count': 'Уникальных цитирующих аффилиаций',
        'unique_citing_countries_count': 'Уникальных цитирующих стран',
        'unique_citing_journals_count': 'Уникальных цитирующих журналов',
        'unique_citing_publishers_count': 'Уникальных цитирующих издателей',
        'gold_open_access': 'Золотой',
        'hybrid_open_access': 'Гибридный',
        'green_open_access': 'Зеленый',
        'bronze_open_access': 'Бронзовый',
        'closed_open_access': 'Закрытый',
        'unknown_open_access': 'Неизвестно',
        'top_authors': 'Топ авторы',
        'top_affiliations_analyzed': 'Топ аффилиации',
        'geographic_analysis_title': 'Географический анализ',
        'citation_dynamics_title': 'Динамика цитирований по годам',
        'cumulative_citations_title': 'Накопленные цитирования',
        'citation_heatmap_title': 'Тепловая карта цитирований',
        'most_cited_title': 'Самые цитируемые публикации',
        'top_citing_authors_title': 'Топ цитирующих авторов',
        'top_citing_affiliations_title': 'Топ цитирующих аффилиаций',
        'top_citing_countries_title': 'Топ цитирующих стран',
        'top_citing_journals_title': 'Топ цитирующих журналов',
        'top_citing_publishers_title': 'Топ цитирующих издателей',
        'topics_analysis_table': 'Тематический анализ',
        'topic_name': 'Тема',
        'click_to_toggle': 'Нажмите для показа цитирований',
        'single_country': 'Внутристрановые',
        'international_collab': 'Международные',
        'citation_year': 'Год цитирования',
        'publication_year_header': 'Год публикации',
        'title_header': 'Название',
        'year_header': 'Год',
        'citations_header': 'Цитирования',
        'citations_per_year_header': 'Цитирований/год',
        'journal_header': 'Журнал',
        'doi_header': 'DOI',
        'authors_header': 'Авторы',
        'affiliations_header': 'Аффилиации',
        'countries_header': 'Страны',
        'show': 'Показать',
        'hide': 'Скрыть',
        'citing_works_count': 'Цитирующих работ',
        'analyzed_works_count': 'Анализируемых работ',
        'topic_advancements_solid_oxide_fuel_cells': 'Достижения в твердооксидных топливных элементах',
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

def normalize_issn(issn_str: str) -> str:
    """Нормализует ISSN к формату XXXX-XXXX"""
    if not issn_str:
        return ""
    cleaned = re.sub(r'[^0-9Xx]', '', str(issn_str).strip())
    if len(cleaned) == 8:
        return f"{cleaned[:4]}-{cleaned[4:]}".upper()
    return cleaned.upper()

def parse_period(period_str: str) -> Any:
    """Парсит строку периода в формат для OpenAlex"""
    if not period_str:
        return None
    
    period_str = period_str.strip()
    
    # Диапазон: 2020-2023
    if '-' in period_str and ',' not in period_str:
        parts = period_str.split('-')
        if len(parts) == 2:
            try:
                start = int(parts[0].strip())
                end = int(parts[1].strip())
                return (start, end)
            except:
                pass
    
    # Список: 2020,2021,2022
    if ',' in period_str:
        try:
            years = [int(y.strip()) for y in period_str.split(',') if y.strip().isdigit()]
            if years:
                return years
        except:
            pass
    
    # Одиночный год
    try:
        year = int(period_str)
        return year
    except:
        pass
    
    return None

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
# СИНХРОННЫЕ ФУНКЦИИ ДЛЯ РАБОТЫ С API (ДЛЯ ЖУРНАЛЬНОГО АНАЛИЗА)
# ============================================

lock = Lock()

def smart_get(url: str, params: Dict, retries: int = MAX_RETRIES) -> Optional[Dict]:
    """Выполняет GET запрос с защитой от rate limiting"""
    for attempt in range(retries):
        try:
            with lock:
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

def get_citing_dois(oa_id: str) -> List[str]:
    """Получает список цитирующих DOI для одной публикации"""
    citing = []
    cursor = "*"
    base_url = "https://api.openalex.org/works"
    
    for _ in range(8):  # ограничение пагинации
        data = smart_get(base_url, {
            "filter": f"cites:{oa_id}",
            "per_page": 200,
            "select": "id,doi,publication_year,publication_date,title,primary_location,type,cited_by_count,authorships,topics,concepts,open_access",
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
                citing.append({
                    'id': item.get('id', ''),
                    'doi': doi.replace("https://doi.org/", ""),
                    'publication_year': item.get('publication_year'),
                    'publication_date': item.get('publication_date'),
                    'title': item.get('title', 'No title'),
                    'cited_by_count': item.get('cited_by_count', 0),
                    'journal_name': item.get('primary_location', {}).get('source', {}).get('display_name', 'Unknown'),
                    'publisher': item.get('primary_location', {}).get('source', {}).get('host_organization_name', 'Unknown'),
                    'type': item.get('type', 'unknown'),
                    'authors': [auth.get('author', {}).get('display_name', '') for auth in item.get('authorships', [])],
                    'author_orcids': [auth.get('author', {}).get('orcid', '').replace('https://orcid.org/', '') for auth in item.get('authorships', [])],
                    'affiliations': [
                        {
                            'name': inst.get('display_name', ''),
                            'country': inst.get('country_code', ''),
                            'ror': inst.get('ror', '')
                        }
                        for auth in item.get('authorships', [])
                        for inst in auth.get('institutions', [])
                    ],
                    'topics': [
                        {
                            'display_name': t.get('display_name', ''),
                            'subfield': t.get('subfield', {}).get('display_name', ''),
                            'field': t.get('field', {}).get('display_name', ''),
                            'domain': t.get('domain', {}).get('display_name', '')
                        }
                        for t in item.get('topics', [])
                    ],
                    'concepts': [c.get('display_name', '') for c in item.get('concepts', [])],
                    'open_access': item.get('open_access', {}).get('oa_status', 'closed'),
                    'is_oa': item.get('open_access', {}).get('is_oa', False)
                })
        
        cursor = data.get("meta", {}).get("next_cursor")
        if not cursor:
            break
    
    return citing[:MAX_CITING_PER_PAPER]

# ============================================
# КЛАСС ДЛЯ АНАЛИЗА ЖУРНАЛА
# ============================================

class JournalAnalyzer:
    """Класс для анализа журнала по ISSN"""
    
    def __init__(self, issn: str, period: Any, max_workers: int = MAX_WORKERS):
        self.issn = normalize_issn(issn)
        self.period = period
        self.max_workers = max_workers
        self.publications = []
        self.citations = {}  # {pub_id: [citing_works]}
        self.metrics = {}
        self.author_data = []
        self.top_affiliations = {}
        self.geographic_data = {}
        self.citation_dynamics = []
        self.cumulative_citations = {}
        self.heatmap_data = {}
        self.most_cited = []
        self.citing_works_metrics = {}
        self.top_citing_authors = {}
        self.top_citing_affiliations = {}
        self.top_citing_countries = {}
        self.top_citing_journals = {}
        self.top_citing_publishers = {}
        self.topic_analysis = {}
        self.detailed_citations = {}
        self.all_publications = []
        
    def _build_year_filter(self) -> str:
        """Строит фильтр по году для OpenAlex"""
        if isinstance(self.period, tuple):
            return f"publication_year:{self.period[0]}-{self.period[1]}"
        elif isinstance(self.period, list):
            return "|".join(f"publication_year:{y}" for y in self.period)
        else:
            return f"publication_year:{self.period}"
    
    def fetch_publications(self, progress_callback=None) -> int:
        """Сбор всех статей журнала за указанный период"""
        base_url = "https://api.openalex.org/works"
        year_filter = self._build_year_filter()
        
        articles = []
        cursor = "*"
        
        if SHOW_DEBUG_LOGS:
            print(f"📚 Начинаем сбор статей для {self.issn} за период {self.period}")
        
        while True:
            data = smart_get(base_url, {
                "filter": f"primary_location.source.issn:{self.issn},{year_filter}",
                "per_page": 200,
                "select": "id,doi,publication_year,publication_date,title,primary_location,type,cited_by_count,authorships,topics,concepts,open_access",
                "cursor": cursor
            })
            
            if not data or not data.get("results"):
                break
                
            for w in data["results"]:
                doi = w.get("doi")
                if doi:
                    doi = doi.replace("https://doi.org/", "")
                
                # Парсим авторов
                authors = []
                author_orcids = []
                for auth in w.get("authorships", []):
                    author_name = auth.get("author", {}).get("display_name", "")
                    orcid = auth.get("author", {}).get("orcid", "").replace("https://orcid.org/", "")
                    if author_name:
                        authors.append(author_name)
                        if orcid:
                            author_orcids.append(orcid)
                
                # Парсим аффилиации
                affiliations = []
                affiliation_countries = []
                for auth in w.get("authorships", []):
                    for inst in auth.get("institutions", []):
                        affil_name = inst.get("display_name", "")
                        if affil_name:
                            affiliations.append(affil_name)
                            country = extract_country_from_affiliation(affil_name)
                            if country:
                                affiliation_countries.append(country)
                
                # Парсим темы
                topics = []
                for t in w.get("topics", []):
                    topics.append({
                        'display_name': t.get('display_name', ''),
                        'subfield': t.get('subfield', {}).get('display_name', ''),
                        'field': t.get('field', {}).get('display_name', ''),
                        'domain': t.get('domain', {}).get('display_name', '')
                    })
                
                # Парсим концепты
                concepts = [c.get('display_name', '') for c in w.get('concepts', [])]
                
                # Open Access
                oa_data = w.get('open_access', {})
                
                articles.append({
                    'id': w.get('id', '').replace('https://openalex.org/', ''),
                    'doi': doi or "N/A",
                    'title': w.get('title', 'No title'),
                    'publication_year': w.get('publication_year'),
                    'publication_date': w.get('publication_date'),
                    'journal_name': w.get('primary_location', {}).get('source', {}).get('display_name', 'Unknown'),
                    'publisher': w.get('primary_location', {}).get('source', {}).get('host_organization_name', 'Unknown'),
                    'type': w.get('type', 'unknown'),
                    'cited_by_count': w.get('cited_by_count', 0),
                    'authors': authors,
                    'author_orcids': author_orcids,
                    'author_count': len(authors),
                    'affiliations': affiliations,
                    'affiliation_countries': affiliation_countries,
                    'topics': topics,
                    'concepts': concepts,
                    'open_access_status': oa_data.get('oa_status', 'closed'),
                    'is_oa': oa_data.get('is_oa', False),
                    'oa_url': oa_data.get('oa_url')
                })
            
            if progress_callback:
                progress_callback(len(articles), len(data["results"]))
            
            cursor = data.get("meta", {}).get("next_cursor")
            if not cursor:
                break
        
        self.publications = articles
        self.all_publications = articles
        
        if SHOW_DEBUG_LOGS:
            print(f"✅ Найдено {len(articles)} статей")
        
        return len(articles)
    
    def fetch_citations_parallel(self, progress_callback=None) -> int:
        """Параллельный сбор цитирующих статей для всех публикаций"""
        if not self.publications:
            return 0
        
        if SHOW_DEBUG_LOGS:
            print(f"🔗 Начинаем параллельный сбор цитирований для {len(self.publications)} статей")
        
        citing_map = {}
        futures = {}
        
        # Фильтруем только публикации с цитированиями
        pubs_to_fetch = [p for p in self.publications if p.get('cited_by_count', 0) > 0 and p.get('id')]
        
        if not pubs_to_fetch:
            if SHOW_DEBUG_LOGS:
                print("ℹ️ Нет публикаций с цитированиями для сбора")
            return 0
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            for pub in pubs_to_fetch:
                future = executor.submit(get_citing_dois, pub['id'])
                futures[future] = pub['id']
            
            total = len(futures)
            completed = 0
            
            for future in as_completed(futures):
                pub_id = futures[future]
                try:
                    citing_map[pub_id] = future.result()
                except Exception as e:
                    if SHOW_DEBUG_LOGS:
                        print(f"⚠️ Ошибка получения цитирований для {pub_id}: {e}")
                    citing_map[pub_id] = []
                
                completed += 1
                if progress_callback:
                    progress_callback(completed, total)
        
        self.citations = citing_map
        
        total_citations = sum(len(c) for c in citing_map.values())
        if SHOW_DEBUG_LOGS:
            print(f"✅ Собрано {total_citations} цитирующих статей")
        
        return total_citations
    
    def _calculate_h_index(self, citations: List[int]) -> int:
        """Рассчитывает h-index"""
        citations_sorted = sorted([c for c in citations if c > 0], reverse=True)
        h_index = 0
        for i, c in enumerate(citations_sorted, 1):
            if c >= i:
                h_index = i
            else:
                break
        return h_index
    
    def _calculate_g_index(self, citations: List[int]) -> int:
        """Рассчитывает g-index"""
        citations_sorted = sorted([c for c in citations if c > 0], reverse=True)
        total_citations_sorted = 0
        g_index = 0
        for i, c in enumerate(citations_sorted, 1):
            total_citations_sorted += c
            if total_citations_sorted >= i**2:
                g_index = i
        return g_index
    
    def analyze(self) -> Dict:
        """Анализирует все собранные данные и рассчитывает метрики"""
        if not self.publications:
            return {}
        
        if SHOW_DEBUG_LOGS:
            print("📊 Начинаем анализ данных...")
        
        # ============================================================
        # 1. ОСНОВНЫЕ МЕТРИКИ
        # ============================================================
        
        total_pubs = len(self.publications)
        citations = [p.get('cited_by_count', 0) for p in self.publications]
        total_citations = sum(citations)
        avg_citations = total_citations / total_pubs if total_pubs > 0 else 0
        median_citations = np.median(citations) if citations else 0
        max_citations = max(citations) if citations else 0
        
        h_index = self._calculate_h_index(citations)
        g_index = self._calculate_g_index(citations)
        i10_index = sum(1 for c in citations if c >= 10)
        i100_index = sum(1 for c in citations if c >= 100)
        
        # Open Access Breakdown
        oa_statuses = [p.get('open_access_status', 'closed') for p in self.publications]
        oa_breakdown = dict(Counter(oa_statuses))
        
        # Активные годы
        years = [p.get('publication_year') for p in self.publications if p.get('publication_year')]
        active_years = len(set(years)) if years else 0
        
        # Уникальные авторы, аффилиации, страны
        all_authors = []
        all_affiliations = []
        all_countries = []
        
        for p in self.publications:
            all_authors.extend(p.get('authors', []))
            all_affiliations.extend(p.get('affiliations', []))
            all_countries.extend(p.get('affiliation_countries', []))
        
        unique_authors = len(set(all_authors))
        unique_affiliations = len(set(all_affiliations))
        unique_countries = len(set([c for c in all_countries if c and c != 'Unknown']))
        
        # Средние значения
        author_counts = [p.get('author_count', 0) for p in self.publications]
        avg_authors = np.mean(author_counts) if author_counts else 0
        avg_affiliations = np.mean([len(p.get('affiliations', [])) for p in self.publications]) if self.publications else 0
        avg_countries = np.mean([len(set(p.get('affiliation_countries', []))) for p in self.publications]) if self.publications else 0
        
        # Международные коллаборации
        international_count = 0
        for p in self.publications:
            countries = set(p.get('affiliation_countries', []))
            countries = [c for c in countries if c and c != 'Unknown']
            if len(countries) > 1:
                international_count += 1
        
        int_collab_rate = international_count / total_pubs if total_pubs > 0 else 0
        
        # ============================================================
        # 2. АНАЛИЗ ЦИТИРУЮЩИХ РАБОТ
        # ============================================================
        
        all_citing_authors = []
        all_citing_affiliations = []
        all_citing_countries = []
        all_citing_journals = []
        all_citing_publishers = []
        citing_works_count = 0
        
        for pub_id, citing_list in self.citations.items():
            citing_works_count += len(citing_list)
            for cite in citing_list:
                all_citing_authors.extend(cite.get('authors', []))
                for affil in cite.get('affiliations', []):
                    affil_name = affil.get('name', '')
                    if affil_name:
                        all_citing_affiliations.append(affil_name)
                    country = affil.get('country', '')
                    if country and country != 'Unknown':
                        all_citing_countries.append(country)
                
                journal = cite.get('journal_name', '')
                if journal and journal != 'Unknown':
                    all_citing_journals.append(journal)
                
                publisher = cite.get('publisher', '')
                if publisher and publisher != 'Unknown':
                    all_citing_publishers.append(publisher)
        
        unique_citing_authors = len(set(all_citing_authors))
        unique_citing_affiliations = len(set(all_citing_affiliations))
        unique_citing_countries = len(set(all_citing_countries))
        unique_citing_journals = len(set(all_citing_journals))
        unique_citing_publishers = len(set(all_citing_publishers))
        
        # ============================================================
        # 3. АНАЛИЗ АВТОРОВ
        # ============================================================
        
        author_stats = defaultdict(lambda: {
            'publications': 0,
            'citations': 0,
            'orcid': None,
            'affiliations': set(),
            'countries': set()
        })
        
        for p in self.publications:
            authors = p.get('authors', [])
            orcids = p.get('author_orcids', [])
            citations_count = p.get('cited_by_count', 0)
            affiliations = p.get('affiliations', [])
            countries = p.get('affiliation_countries', [])
            
            for idx, author in enumerate(authors):
                if author:
                    author_stats[author]['publications'] += 1
                    author_stats[author]['citations'] += citations_count
                    if idx < len(orcids) and orcids[idx]:
                        if not author_stats[author]['orcid']:
                            author_stats[author]['orcid'] = orcids[idx]
                    for aff in affiliations:
                        if aff:
                            author_stats[author]['affiliations'].add(aff)
                    for country in countries:
                        if country and country != 'Unknown':
                            author_stats[author]['countries'].add(country)
        
        # Сортируем авторов по количеству публикаций
        sorted_authors = sorted(
            author_stats.items(),
            key=lambda x: (x[1]['publications'], x[1]['citations']),
            reverse=True
        )
        
        self.author_data = []
        for rank, (name, stats) in enumerate(sorted_authors, 1):
            self.author_data.append({
                'rank': rank,
                'name': name,
                'orcid': stats['orcid'],
                'affiliations': list(stats['affiliations']),
                'countries': list(stats['countries']),
                'publications': stats['publications'],
                'citations': stats['citations']
            })
        
        # ============================================================
        # 4. ТОП АФФИЛИАЦИЙ
        # ============================================================
        
        affil_counter = Counter()
        for p in self.publications:
            for aff in p.get('affiliations', []):
                if aff:
                    affil_counter[aff] += 1
        
        self.top_affiliations = dict(affil_counter.most_common(20))
        
        # ============================================================
        # 5. ГЕОГРАФИЧЕСКИЙ АНАЛИЗ
        # ============================================================
        
        # 5.1 Уникальные страны на публикацию
        country_per_pub = []
        for p in self.publications:
            countries = set([c for c in p.get('affiliation_countries', []) if c and c != 'Unknown'])
            country_per_pub.append(len(countries))
        
        self.geographic_data['unique_countries_per_publication'] = {
            'distribution': dict(Counter(country_per_pub)),
            'average': np.mean(country_per_pub) if country_per_pub else 0,
            'max': max(country_per_pub) if country_per_pub else 0
        }
        
        # 5.2 Авторы по странам
        author_country_counter = Counter()
        for p in self.publications:
            for country in p.get('affiliation_countries', []):
                if country and country != 'Unknown':
                    author_country_counter[country] += 1
        
        self.geographic_data['authors_per_country'] = dict(author_country_counter.most_common())
        
        # 5.3 Модели коллабораций
        single_country = 0
        international = 0
        for p in self.publications:
            countries = set([c for c in p.get('affiliation_countries', []) if c and c != 'Unknown'])
            if len(countries) <= 1:
                single_country += 1
            elif len(countries) > 1:
                international += 1
        
        self.geographic_data['collaboration_patterns'] = {
            'single_country': single_country,
            'international': international,
            'single_country_percent': single_country / total_pubs * 100 if total_pubs > 0 else 0,
            'international_percent': international / total_pubs * 100 if total_pubs > 0 else 0
        }
        
        # 5.4 Пары стран
        country_pairs = Counter()
        for p in self.publications:
            countries = sorted(set([c for c in p.get('affiliation_countries', []) if c and c != 'Unknown']))
            if len(countries) >= 2:
                for i in range(len(countries)):
                    for j in range(i+1, len(countries)):
                        pair = f"{countries[i]}-{countries[j]}"
                        country_pairs[pair] += 1
        
        self.geographic_data['country_pairs'] = dict(country_pairs.most_common(30))
        
        # ============================================================
        # 6. ЦИТАЦИОННЫЙ АНАЛИЗ
        # ============================================================
        
        # 6.1 Динамика цитирований по годам
        citation_dynamics = []
        for pub in self.publications:
            pub_year = pub.get('publication_year')
            if not pub_year:
                continue
            
            pub_id = pub.get('id')
            if pub_id in self.citations:
                for cite in self.citations[pub_id]:
                    cite_year = cite.get('publication_year')
                    if cite_year:
                        citation_dynamics.append({
                            'publication_year': pub_year,
                            'citation_year': cite_year,
                            'citations_count': 1
                        })
        
        # Группируем
        dynamics_grouped = defaultdict(int)
        for item in citation_dynamics:
            key = (item['publication_year'], item['citation_year'])
            dynamics_grouped[key] += 1
        
        self.citation_dynamics = [
            {
                'publication_year': k[0],
                'citation_year': k[1],
                'citations_count': v
            }
            for k, v in sorted(dynamics_grouped.items())
        ]
        
        # 6.2 Накопленные цитирования
        cumulative = defaultdict(int)
        all_years = sorted(set([d['citation_year'] for d in self.citation_dynamics]))
        running_total = 0
        
        for year in all_years:
            year_citations = sum(d['citations_count'] for d in self.citation_dynamics if d['citation_year'] == year)
            running_total += year_citations
            cumulative[year] = running_total
        
        self.cumulative_citations = dict(sorted(cumulative.items()))
        
        # 6.3 Тепловая карта
        heatmap_data = defaultdict(lambda: defaultdict(int))
        for d in self.citation_dynamics:
            heatmap_data[d['publication_year']][d['citation_year']] += d['citations_count']
        
        self.heatmap_data = {
            'pub_years': sorted(set(d['publication_year'] for d in self.citation_dynamics)),
            'cite_years': sorted(set(d['citation_year'] for d in self.citation_dynamics)),
            'data': heatmap_data
        }
        
        # 6.4 Самые цитируемые публикации
        sorted_pubs = sorted(self.publications, key=lambda x: x.get('cited_by_count', 0), reverse=True)
        self.most_cited = [
            {
                'rank': i+1,
                'title': p.get('title', 'No title'),
                'year': p.get('publication_year', 'N/A'),
                'citations': p.get('cited_by_count', 0),
                'citations_per_year': p.get('cited_by_count', 0) / (datetime.now().year - p.get('publication_year', datetime.now().year) + 1) if p.get('publication_year') else 0,
                'authors': p.get('authors', [])[:5],
                'doi': p.get('doi', '')
            }
            for i, p in enumerate(sorted_pubs[:20])
        ]
        
        # ============================================================
        # 7. АНАЛИЗ ЦИТИРУЮЩИХ РАБОТ
        # ============================================================
        
        self.citing_works_metrics = {
            'total_citing_works': citing_works_count,
            'unique_citing_authors': unique_citing_authors,
            'unique_citing_affiliations': unique_citing_affiliations,
            'unique_citing_countries': unique_citing_countries,
            'unique_citing_journals': unique_citing_journals,
            'unique_citing_publishers': unique_citing_publishers
        }
        
        # Топ цитирующих авторов
        citing_author_counter = Counter(all_citing_authors)
        self.top_citing_authors = dict(citing_author_counter.most_common(20))
        
        # Топ цитирующих аффилиаций
        citing_affil_counter = Counter(all_citing_affiliations)
        self.top_citing_affiliations = dict(citing_affil_counter.most_common(20))
        
        # Топ цитирующих стран
        citing_country_counter = Counter(all_citing_countries)
        self.top_citing_countries = dict(citing_country_counter.most_common(20))
        
        # Топ цитирующих журналов
        citing_journal_counter = Counter(all_citing_journals)
        self.top_citing_journals = dict(citing_journal_counter.most_common(20))
        
        # Топ цитирующих издателей
        citing_publisher_counter = Counter(all_citing_publishers)
        self.top_citing_publishers = dict(citing_publisher_counter.most_common(20))
        
        # ============================================================
        # 8. ТЕМАТИЧЕСКИЙ АНАЛИЗ
        # ============================================================
        
        # Собираем все темы из анализируемых и цитирующих статей
        analyzed_topics = defaultdict(lambda: {
            'count': 0,
            'years': [],
            'recent_5_years': 0
        })
        
        citing_topics = defaultdict(lambda: {
            'count': 0,
            'years': [],
            'recent_5_years': 0
        })
        
        current_year = datetime.now().year
        
        # Анализируемые статьи
        for p in self.publications:
            pub_year = p.get('publication_year')
            for topic in p.get('topics', []):
                topic_name = topic.get('display_name', '')
                if topic_name:
                    analyzed_topics[topic_name]['count'] += 1
                    if pub_year:
                        analyzed_topics[topic_name]['years'].append(pub_year)
                        if pub_year >= current_year - 4:
                            analyzed_topics[topic_name]['recent_5_years'] += 1
        
        # Цитирующие статьи
        for pub_id, citing_list in self.citations.items():
            for cite in citing_list:
                cite_year = cite.get('publication_year')
                for topic in cite.get('topics', []):
                    topic_name = topic.get('display_name', '')
                    if topic_name:
                        citing_topics[topic_name]['count'] += 1
                        if cite_year:
                            citing_topics[topic_name]['years'].append(cite_year)
                            if cite_year >= current_year - 4:
                                citing_topics[topic_name]['recent_5_years'] += 1
        
        # Объединяем темы
        all_topic_names = set(analyzed_topics.keys()) | set(citing_topics.keys())
        
        total_analyzed = len(self.publications)
        total_citing = citing_works_count
        
        for topic_name in all_topic_names:
            a_count = analyzed_topics[topic_name]['count']
            c_count = citing_topics[topic_name]['count']
            
            a_norm = a_count / total_analyzed if total_analyzed > 0 else 0
            c_norm = c_count / total_citing if total_citing > 0 else 0
            total_norm = (a_count + c_count) / (total_analyzed + total_citing) if (total_analyzed + total_citing) > 0 else 0
            
            all_years = analyzed_topics[topic_name]['years'] + citing_topics[topic_name]['years']
            first_year = min(all_years) if all_years else None
            peak_year = max(set(all_years), key=all_years.count) if all_years else None
            
            recent_5 = analyzed_topics[topic_name]['recent_5_years'] + citing_topics[topic_name]['recent_5_years']
            
            self.topic_analysis[topic_name] = {
                'analyzed_count': a_count,
                'citing_count': c_count,
                'analyzed_norm': a_norm,
                'citing_norm': c_norm,
                'total_norm': total_norm,
                'first_year': first_year,
                'peak_year': peak_year,
                'recent_5_years': recent_5
            }
        
        # Сортируем темы по общему нормализованному значению
        self.topic_analysis = dict(sorted(
            self.topic_analysis.items(),
            key=lambda x: x[1]['total_norm'],
            reverse=True
        ))
        
        # ============================================================
        # 9. ДЕТАЛЬНЫЕ ЦИТИРОВАНИЯ
        # ============================================================
        
        for pub in self.publications:
            pub_id = pub.get('id')
            if pub_id in self.citations and self.citations[pub_id]:
                citations_list = []
                for cite in self.citations[pub_id]:
                    # Вычисляем задержку цитирования
                    pub_year = pub.get('publication_year')
                    cite_year = cite.get('publication_year')
                    citation_lag = cite_year - pub_year if pub_year and cite_year else None
                    
                    # Собираем страны
                    cite_countries = []
                    for aff in cite.get('affiliations', []):
                        country = aff.get('country', '')
                        if country and country != 'Unknown':
                            cite_countries.append(country)
                    
                    citations_list.append({
                        'citing_title': cite.get('title', 'No title'),
                        'citing_year': cite_year,
                        'citing_date': cite.get('publication_date', ''),
                        'citing_journal': cite.get('journal_name', 'Unknown'),
                        'citing_publisher': cite.get('publisher', 'Unknown'),
                        'citing_doi': cite.get('doi', ''),
                        'citation_lag': citation_lag,
                        'citing_authors': cite.get('authors', []),
                        'citing_countries': cite_countries,
                        'citing_topics': [t.get('display_name', '') for t in cite.get('topics', [])]
                    })
                
                self.detailed_citations[pub_id] = {
                    'title': pub.get('title', 'No title'),
                    'year': pub.get('publication_year'),
                    'doi': pub.get('doi', ''),
                    'total_citations': len(citations_list),
                    'citations': citations_list
                }
        
        # ============================================================
        # 10. СОХРАНЯЕМ МЕТРИКИ
        # ============================================================
        
        self.metrics = {
            'total_publications': total_pubs,
            'total_citations': total_citations,
            'h_index': h_index,
            'g_index': g_index,
            'i10_index': i10_index,
            'i100_index': i100_index,
            'avg_citations': avg_citations,
            'median_citations': median_citations,
            'max_citations': max_citations,
            'open_access_breakdown': oa_breakdown,
            'active_years': active_years,
            'unique_authors': unique_authors,
            'unique_affiliations': unique_affiliations,
            'unique_countries': unique_countries,
            'avg_authors_per_paper': avg_authors,
            'avg_affiliations_per_paper': avg_affiliations,
            'avg_countries_per_paper': avg_countries,
            'international_collaboration_rate': int_collab_rate,
            'total_citing_works': citing_works_count,
            'unique_citing_authors': unique_citing_authors,
            'unique_citing_affiliations': unique_citing_affiliations,
            'unique_citing_countries': unique_citing_countries,
            'unique_citing_journals': unique_citing_journals,
            'unique_citing_publishers': unique_citing_publishers
        }
        
        if SHOW_DEBUG_LOGS:
            print("✅ Анализ завершен!")
        
        return self.metrics
    
    def get_metrics(self) -> Dict:
        """Возвращает все метрики"""
        return self.metrics
    
    def get_publications(self) -> List[Dict]:
        """Возвращает список публикаций"""
        return self.publications
    
    def get_citations(self) -> Dict:
        """Возвращает словарь цитирований"""
        return self.citations
    
    def generate_html_report(self, lang: str = 'en', theme_colors: Dict = None) -> str:
        """Генерирует HTML отчет на основе собранных данных"""
        
        def t(key: str, **kwargs) -> str:
            return translate(key, lang, **kwargs)
        
        if theme_colors is None:
            theme_colors = {
                'primary': '#667eea',
                'secondary': '#f39c12'
            }
        
        primary = theme_colors.get('primary', '#667eea')
        secondary = theme_colors.get('secondary', '#f39c12')
        
        metrics = self.metrics
        oa_breakdown = metrics.get('open_access_breakdown', {})
        
        # Формируем HTML
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>{t('journal_analysis_title')} - {self.issn}</title>
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
                    padding: 30px 20px;
                    overflow-y: auto;
                    z-index: 1000;
                }}
                .sidebar h3 {{
                    margin-bottom: 20px;
                    font-size: 18px;
                    font-weight: 600;
                    color: white;
                    border-bottom: 2px solid rgba(255,255,255,0.3);
                    padding-bottom: 10px;
                }}
                .sidebar a {{
                    color: white;
                    text-decoration: none;
                    display: block;
                    padding: 8px 15px;
                    margin: 3px 0;
                    border-radius: 8px;
                    transition: all 0.3s;
                    font-size: 14px;
                }}
                .sidebar a:hover {{
                    background: rgba(255,255,255,0.2);
                    transform: translateX(5px);
                }}
                .sidebar .level2 {{
                    padding-left: 30px;
                    font-size: 13px;
                    opacity: 0.9;
                }}
                .sidebar .level2:hover {{
                    opacity: 1;
                }}
                .main-content {{
                    margin-left: 280px;
                    padding: 30px 40px;
                }}
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
                    margin-top: 10px;
                    font-size: 16px;
                }}
                .header .date {{
                    opacity: 0.8;
                    margin-top: 5px;
                    font-size: 14px;
                }}
                .section {{
                    background: white;
                    border-radius: 15px;
                    padding: 25px;
                    margin-bottom: 30px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
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
                .metrics-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
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
                .oa-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
                    gap: 10px;
                    margin: 15px 0;
                }}
                .oa-item {{
                    background: #f8f9fa;
                    padding: 12px;
                    border-radius: 8px;
                    text-align: center;
                    border: 1px solid #e0e0e0;
                }}
                .oa-label {{
                    font-weight: 600;
                    font-size: 14px;
                    color: #555;
                }}
                .oa-value {{
                    font-size: 20px;
                    font-weight: bold;
                    color: #2C3E50;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                    font-family: 'Times New Roman', serif;
                }}
                th {{
                    background: linear-gradient(135deg, {primary} 0%, {secondary} 100%);
                    color: white;
                    padding: 12px;
                    text-align: left;
                }}
                td {{
                    padding: 10px;
                    border-bottom: 1px solid #BDC3C7;
                }}
                tr:hover {{
                    background-color: #f5f5f5;
                }}
                .doi-link {{
                    color: #2980B9;
                    text-decoration: none;
                    font-size: 12px;
                }}
                .doi-link:hover {{
                    text-decoration: underline;
                }}
                .badge {{
                    display: inline-block;
                    padding: 4px 12px;
                    border-radius: 20px;
                    font-size: 12px;
                    font-weight: 600;
                    margin: 2px;
                }}
                .badge-success {{ background: #d4edda; color: #155724; }}
                .badge-warning {{ background: #fff3cd; color: #856404; }}
                .badge-danger {{ background: #f8d7da; color: #721c24; }}
                .badge-info {{ background: #d1ecf1; color: #0c5460; }}
                .badge-primary {{ background: {primary}25; color: {primary}; }}
                .collapser {{
                    background: #f8f9fa;
                    padding: 12px 15px;
                    margin: 5px 0;
                    border-radius: 8px;
                    cursor: pointer;
                    border-left: 4px solid {primary};
                    transition: all 0.3s;
                }}
                .collapser:hover {{
                    background: #e9ecef;
                    transform: translateX(3px);
                }}
                .citation-detail {{
                    background: #f8f9fa;
                    padding: 12px 15px;
                    margin: 5px 0 5px 20px;
                    border-radius: 6px;
                    border-left: 3px solid #6c757d;
                }}
                .citation-detail .cite-meta {{
                    font-size: 13px;
                    color: #555;
                    margin-top: 3px;
                }}
                .citation-count {{
                    color: {primary};
                    font-weight: bold;
                }}
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
                .filter-row select, .filter-row input {{
                    padding: 6px 10px;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    font-family: 'Times New Roman', serif;
                }}
                .filter-row label {{
                    font-size: 13px;
                    font-weight: 500;
                    margin-right: 5px;
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
                .heatmap-cell {{
                    text-align: center;
                    padding: 8px;
                    border-radius: 4px;
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
                    .metrics-grid {{ grid-template-columns: repeat(2, 1fr); }}
                    .filter-row {{ flex-direction: column; align-items: stretch; }}
                }}
            </style>
        </head>
        <body>
            <div class="sidebar">
                <h3>📊 {t('journal_analysis_title')}</h3>
                <a href="#overview">📊 {t('overview')}</a>
                <a href="#analyzed_articles" class="level2">📄 {t('analyzed_articles')}</a>
                <a href="#citation_analysis" class="level2">📈 {t('citation_analysis')}</a>
                <a href="#citing_works" class="level2">🔗 {t('citing_works')}</a>
                <a href="#topics_analysis" class="level2">🏷️ {t('topics_analysis')}</a>
                <a href="#detailed_citations" class="level2">📋 {t('detailed_citations')}</a>
                <a href="#all_publications" class="level2">📚 {t('all_publications')}</a>
            </div>
            
            <div class="main-content">
                <div class="header">
                    <h1>📊 {t('journal_analysis_title')}</h1>
                    <div class="subtitle">{t('journal_analysis_desc')}</div>
                    <div class="subtitle">ISSN: {self.issn}</div>
                    <div class="date">{t('report_preview')}: {datetime.now().strftime('%d.%m.%Y')}</div>
                </div>
        """
        
        # ============================================================
        # РАЗДЕЛ 1: OVERVIEW
        # ============================================================
        
        html_content += f"""
                <div id="overview" class="section">
                    <div class="section-title"><span class="icon">📊</span> {t('overview')}</div>
                    
                    <div class="metrics-grid">
                        <div class="metric-card">
                            <div class="metric-value">{metrics.get('total_publications', 0)}</div>
                            <div class="metric-label">{t('publications')}</div>
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
                            <div class="metric-value">{metrics.get('open_access_breakdown', {}).get('gold', 0) + metrics.get('open_access_breakdown', {}).get('hybrid', 0) + metrics.get('open_access_breakdown', {}).get('green', 0) + metrics.get('open_access_breakdown', {}).get('bronze', 0)}</div>
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
                            <div class="metric-label">{t('avg_affiliations')}</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{metrics.get('avg_countries_per_paper', 0):.1f}</div>
                            <div class="metric-label">{t('avg_countries')}</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{metrics.get('international_collaboration_rate', 0)*100:.1f}%</div>
                            <div class="metric-label">{t('int_collab_rate')}</div>
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
                    
                    <h4 style="margin-top: 20px;">{t('open_access_breakdown')}</h4>
                    <div class="oa-grid">
        """
        
        oa_labels = {
            'gold': t('gold'),
            'hybrid': t('hybrid'),
            'green': t('green'),
            'bronze': t('bronze'),
            'closed': t('closed'),
            'unknown': t('unknown')
        }
        
        for status, label in oa_labels.items():
            count = oa_breakdown.get(status, 0)
            html_content += f"""
                        <div class="oa-item">
                            <div class="oa-label">{label}</div>
                            <div class="oa-value">{count}</div>
                        </div>
            """
        
        html_content += """
                    </div>
                </div>
        """
        
        # ============================================================
        # РАЗДЕЛ 2: ANALYZED ARTICLES
        # ============================================================
        
        html_content += f"""
                <div id="analyzed_articles" class="section">
                    <div class="section-title"><span class="icon">📄</span> {t('analyzed_articles')}</div>
                    
                    <h4>{t('author_analysis')}</h4>
                    <div style="overflow-x: auto; max-height: 500px; overflow-y: auto;">
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
        
        for author in self.author_data[:50]:
            html_content += f"""
                                <tr>
                                    <td>{author['rank']}</td>
                                    <td>{html.escape(author['name'])}</td>
                                    <td>{f'<a href="https://orcid.org/{author["orcid"]}" target="_blank">{author["orcid"]}</a>' if author['orcid'] else 'N/A'}</td>
                                    <td>{', '.join([html.escape(a) for a in author['affiliations'][:3]])}</td>
                                    <td>{', '.join([html.escape(c) for c in author['countries'][:3]])}</td>
                                    <td>{author['publications']}</td>
                                    <td>{author['citations']}</td>
                                </tr>
            """
        
        html_content += """
                            </tbody>
                        </table>
                    </div>
                    
                    <h4 style="margin-top: 20px;">{t('top_affiliations')}</h4>
                    <div style="overflow-x: auto;">
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
        
        for rank, (affil, count) in enumerate(list(self.top_affiliations.items())[:20], 1):
            html_content += f"""
                                <tr>
                                    <td>{rank}</td>
                                    <td>{html.escape(affil)}</td>
                                    <td>{count}</td>
                                </tr>
            """
        
        html_content += """
                            </tbody>
                        </table>
                    </div>
                    
                    <h4 style="margin-top: 20px;">{t('geographic_analysis')}</h4>
                    
                    <h5>{t('unique_countries_per_publication')}</h5>
                    <p style="font-size: 13px; color: #666; margin-bottom: 10px;">{t('each_publication_counted_once')}</p>
                    <div style="overflow-x: auto;">
                        <table>
                            <thead>
                                <tr>
                                    <th>{t('countries_count')}</th>
                                    <th>{t('publications')}</th>
                                </tr>
                            </thead>
                            <tbody>
        """
        
        geo_dist = self.geographic_data.get('unique_countries_per_publication', {}).get('distribution', {})
        for country_count, pub_count in sorted(geo_dist.items()):
            html_content += f"""
                                <tr>
                                    <td>{country_count}</td>
                                    <td>{pub_count}</td>
                                </tr>
            """
        
        html_content += """
                            </tbody>
                        </table>
                    </div>
                    
                    <h5 style="margin-top: 15px;">{t('authors_per_country')}</h5>
                    <p style="font-size: 13px; color: #666; margin-bottom: 10px;">{t('each_author_counted_separately')}</p>
                    <div style="overflow-x: auto;">
                        <table>
                            <thead>
                                <tr>
                                    <th>{t('countries')}</th>
                                    <th>{t('authors')}</th>
                                </tr>
                            </thead>
                            <tbody>
        """
        
        for country, count in list(self.geographic_data.get('authors_per_country', {}).items())[:30]:
            html_content += f"""
                                <tr>
                                    <td>{html.escape(country)}</td>
                                    <td>{count}</td>
                                </tr>
            """
        
        html_content += """
                            </tbody>
                        </table>
                    </div>
                    
                    <h5 style="margin-top: 15px;">{t('collaboration_patterns')}</h5>
                    <p style="font-size: 13px; color: #666; margin-bottom: 10px;">{t('distribution_of_single_country_vs_international')}</p>
                    <div style="overflow-x: auto;">
                        <table>
                            <thead>
                                <tr>
                                    <th>{t('collaboration_type')}</th>
                                    <th>{t('publications')}</th>
                                    <th>{t('percent')}</th>
                                </tr>
                            </thead>
                            <tbody>
        """
        
        collab = self.geographic_data.get('collaboration_patterns', {})
        html_content += f"""
                                <tr>
                                    <td>{t('single_country')}</td>
                                    <td>{collab.get('single_country', 0)}</td>
                                    <td>{collab.get('single_country_percent', 0):.1f}%</td>
                                </tr>
                                <tr>
                                    <td>{t('international_collab')}</td>
                                    <td>{collab.get('international', 0)}</td>
                                    <td>{collab.get('international_percent', 0):.1f}%</td>
                                </tr>
        """
        
        html_content += """
                            </tbody>
                        </table>
                    </div>
                    
                    <h5 style="margin-top: 15px;">{t('collaboration_couples')}</h5>
                    <p style="font-size: 13px; color: #666; margin-bottom: 10px;">{t('frequency_of_country_pairs_collaborating')}</p>
                    <div style="overflow-x: auto;">
                        <table>
                            <thead>
                                <tr>
                                    <th>{t('country_pair')}</th>
                                    <th>{t('publications')}</th>
                                </tr>
                            </thead>
                            <tbody>
        """
        
        for pair, count in list(self.geographic_data.get('country_pairs', {}).items())[:30]:
            html_content += f"""
                                <tr>
                                    <td>{html.escape(pair)}</td>
                                    <td>{count}</td>
                                </tr>
            """
        
        html_content += """
                            </tbody>
                        </table>
                    </div>
                </div>
        """
        
        # ============================================================
        # РАЗДЕЛ 3: CITATION ANALYSIS
        # ============================================================
        
        html_content += f"""
                <div id="citation_analysis" class="section">
                    <div class="section-title"><span class="icon">📈</span> {t('citation_analysis')}</div>
                    
                    <h4>{t('citation_dynamics_by_year')}</h4>
                    <div style="overflow-x: auto; max-height: 400px; overflow-y: auto;">
                        <table>
                            <thead>
                                <tr>
                                    <th>{t('publication_year_col')}</th>
                                    <th>{t('citation_year_col')}</th>
                                    <th>{t('citations_count_col')}</th>
                                </tr>
                            </thead>
                            <tbody>
        """
        
        for d in self.citation_dynamics:
            html_content += f"""
                                <tr>
                                    <td>{d['publication_year']}</td>
                                    <td>{d['citation_year']}</td>
                                    <td>{d['citations_count']}</td>
                                </tr>
            """
        
        html_content += """
                            </tbody>
                        </table>
                    </div>
                    
                    <h4 style="margin-top: 20px;">{t('cumulative_citations')}</h4>
                    <div style="overflow-x: auto;">
                        <table>
                            <thead>
                                <tr>
                                    <th>{t('citation_year_col')}</th>
                                    <th>{t('cumulative_citations')}</th>
                                </tr>
                            </thead>
                            <tbody>
        """
        
        for year, count in self.cumulative_citations.items():
            html_content += f"""
                                <tr>
                                    <td>{year}</td>
                                    <td>{count}</td>
                                </tr>
            """
        
        html_content += """
                            </tbody>
                        </table>
                    </div>
                    
                    <h4 style="margin-top: 20px;">{t('citation_network_heatmap')}</h4>
                    <div style="overflow-x: auto;">
                        <table>
                            <thead>
                                <tr>
                                    <th>{t('publication_year_col')}</th>
        """
        
        for cite_year in self.heatmap_data.get('cite_years', []):
            html_content += f"<th>{cite_year}</th>"
        
        html_content += """
                                </tr>
                            </thead>
                            <tbody>
        """
        
        # Находим максимальное значение для нормализации цветов
        max_val = 1
        heatmap_data = self.heatmap_data.get('data', {})
        for pub_year, cite_years in heatmap_data.items():
            for cite_year, count in cite_years.items():
                if count > max_val:
                    max_val = count
        
        for pub_year in self.heatmap_data.get('pub_years', []):
            html_content += f"""
                                <tr>
                                    <td><strong>{pub_year}</strong></td>
            """
            for cite_year in self.heatmap_data.get('cite_years', []):
                count = heatmap_data.get(pub_year, {}).get(cite_year, 0)
                if count == 0:
                    html_content += f'<td style="text-align: center; color: #ccc;">-</td>'
                else:
                    # Нормализуем цвет от светло-желтого до темно-красного
                    intensity = count / max_val if max_val > 0 else 0
                    r = int(255 * intensity)
                    g = int(255 * (1 - intensity * 0.7))
                    b = int(200 * (1 - intensity * 0.8))
                    html_content += f'<td style="text-align: center; background: rgb({r},{g},{b}); color: {"white" if intensity > 0.6 else "black"};">{count}</td>'
            html_content += """
                                </tr>
            """
        
        html_content += """
                            </tbody>
                        </table>
                    </div>
                    
                    <h4 style="margin-top: 20px;">{t('most_cited_publications')}</h4>
                    <div style="overflow-x: auto;">
                        <table>
                            <thead>
                                <tr>
                                    <th>{t('rank')}</th>
                                    <th>{t('title')}</th>
                                    <th>{t('year')}</th>
                                    <th>{t('citations')}</th>
                                    <th>{t('citations_per_year_col')}</th>
                                    <th>{t('authors')}</th>
                                    <th>DOI</th>
                                </tr>
                            </thead>
                            <tbody>
        """
        
        for item in self.most_cited:
            authors_str = ', '.join(item.get('authors', [])[:3])
            if len(item.get('authors', [])) > 3:
                authors_str += f' +{len(item.get("authors", [])) - 3} more'
            
            html_content += f"""
                                <tr>
                                    <td>{item['rank']}</td>
                                    <td class="word-wrap">{html.escape(item['title'])}</td>
                                    <td>{item['year']}</td>
                                    <td>{item['citations']}</td>
                                    <td>{item['citations_per_year']:.1f}</td>
                                    <td>{html.escape(authors_str)}</td>
                                    <td><a href="https://doi.org/{item['doi']}" target="_blank" class="doi-link">{item['doi']}</a></td>
                                </tr>
            """
        
        html_content += """
                            </tbody>
                        </table>
                    </div>
                </div>
        """
        
        # ============================================================
        # РАЗДЕЛ 4: CITING WORKS ANALYSIS
        # ============================================================
        
        html_content += f"""
                <div id="citing_works" class="section">
                    <div class="section-title"><span class="icon">🔗</span> {t('citing_works_analysis')}</div>
                    
                    <div class="metrics-grid">
                        <div class="metric-card">
                            <div class="metric-value">{metrics.get('total_citing_works', 0)}</div>
                            <div class="metric-label">{t('total_citing_works')}</div>
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
                    
                    <h4>{t('top_citing_authors')}</h4>
                    <div style="overflow-x: auto; max-height: 300px; overflow-y: auto;">
                        <table>
                            <thead>
                                <tr>
                                    <th>{t('rank')}</th>
                                    <th>{t('authors')}</th>
                                    <th>{t('citations_count')}</th>
                                </tr>
                            </thead>
                            <tbody>
        """
        
        for rank, (author, count) in enumerate(list(self.top_citing_authors.items())[:20], 1):
            html_content += f"""
                                <tr>
                                    <td>{rank}</td>
                                    <td>{html.escape(author)}</td>
                                    <td>{count}</td>
                                </tr>
            """
        
        html_content += """
                            </tbody>
                        </table>
                    </div>
                    
                    <h4 style="margin-top: 15px;">{t('top_citing_affiliations')}</h4>
                    <div style="overflow-x: auto; max-height: 300px; overflow-y: auto;">
                        <table>
                            <thead>
                                <tr>
                                    <th>{t('rank')}</th>
                                    <th>{t('affiliations')}</th>
                                    <th>{t('citations_count')}</th>
                                </tr>
                            </thead>
                            <tbody>
        """
        
        for rank, (affil, count) in enumerate(list(self.top_citing_affiliations.items())[:20], 1):
            html_content += f"""
                                <tr>
                                    <td>{rank}</td>
                                    <td>{html.escape(affil)}</td>
                                    <td>{count}</td>
                                </tr>
            """
        
        html_content += """
                            </tbody>
                        </table>
                    </div>
                    
                    <h4 style="margin-top: 15px;">{t('top_citing_countries')}</h4>
                    <div style="overflow-x: auto; max-height: 300px; overflow-y: auto;">
                        <table>
                            <thead>
                                <tr>
                                    <th>{t('rank')}</th>
                                    <th>{t('countries')}</th>
                                    <th>{t('citations_count')}</th>
                                </tr>
                            </thead>
                            <tbody>
        """
        
        for rank, (country, count) in enumerate(list(self.top_citing_countries.items())[:20], 1):
            html_content += f"""
                                <tr>
                                    <td>{rank}</td>
                                    <td>{html.escape(country)}</td>
                                    <td>{count}</td>
                                </tr>
            """
        
        html_content += """
                            </tbody>
                        </table>
                    </div>
                    
                    <h4 style="margin-top: 15px;">{t('top_citing_journals')}</h4>
                    <div style="overflow-x: auto; max-height: 300px; overflow-y: auto;">
                        <table>
                            <thead>
                                <tr>
                                    <th>{t('rank')}</th>
                                    <th>{t('journal')}</th>
                                    <th>{t('citations_count')}</th>
                                </tr>
                            </thead>
                            <tbody>
        """
        
        for rank, (journal, count) in enumerate(list(self.top_citing_journals.items())[:20], 1):
            html_content += f"""
                                <tr>
                                    <td>{rank}</td>
                                    <td>{html.escape(journal)}</td>
                                    <td>{count}</td>
                                </tr>
            """
        
        html_content += """
                            </tbody>
                        </table>
                    </div>
                    
                    <h4 style="margin-top: 15px;">{t('top_citing_publishers')}</h4>
                    <div style="overflow-x: auto; max-height: 300px; overflow-y: auto;">
                        <table>
                            <thead>
                                <tr>
                                    <th>{t('rank')}</th>
                                    <th>{t('publisher')}</th>
                                    <th>{t('citations_count')}</th>
                                </tr>
                            </thead>
                            <tbody>
        """
        
        for rank, (publisher, count) in enumerate(list(self.top_citing_publishers.items())[:20], 1):
            html_content += f"""
                                <tr>
                                    <td>{rank}</td>
                                    <td>{html.escape(publisher)}</td>
                                    <td>{count}</td>
                                </tr>
            """
        
        html_content += """
                            </tbody>
                        </table>
                    </div>
                </div>
        """
        
        # ============================================================
        # РАЗДЕЛ 5: TOPICS ANALYSIS
        # ============================================================
        
        html_content += f"""
                <div id="topics_analysis" class="section">
                    <div class="section-title"><span class="icon">🏷️</span> {t('topics_analysis')}</div>
                    
                    <div style="overflow-x: auto; max-height: 600px; overflow-y: auto;">
                        <table>
                            <thead>
                                <tr>
                                    <th>{t('topic_name')}</th>
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
        """
        
        for topic_name, data in list(self.topic_analysis.items())[:50]:
            html_content += f"""
                                <tr>
                                    <td>{html.escape(topic_name)}</td>
                                    <td>{data['analyzed_count']}</td>
                                    <td>{data['citing_count']}</td>
                                    <td>{data['analyzed_norm']:.3f}</td>
                                    <td>{data['citing_norm']:.3f}</td>
                                    <td>{data['total_norm']:.3f}</td>
                                    <td>{data['first_year'] or 'N/A'}</td>
                                    <td>{data['peak_year'] or 'N/A'}</td>
                                    <td>{data['recent_5_years']}</td>
                                </tr>
            """
        
        html_content += """
                            </tbody>
                        </table>
                    </div>
                </div>
        """
        
        # ============================================================
        # РАЗДЕЛ 6: DETAILED CITATIONS
        # ============================================================
        
        html_content += f"""
                <div id="detailed_citations" class="section">
                    <div class="section-title"><span class="icon">📋</span> {t('detailed_citations')}</div>
        """
        
        for pub_id, data in self.detailed_citations.items():
            # Генерируем безопасный ID для JavaScript
            safe_id = pub_id.replace('https://openalex.org/', '').replace('/', '_')
            
            html_content += f"""
                    <div class="collapser" onclick="toggleCitations('{safe_id}')">
                        <strong>{html.escape(data['title'][:100])}{'...' if len(data['title']) > 100 else ''}</strong>
                        <span class="badge badge-info">{data['year']}</span>
                        <span class="citation-count">{data['total_citations']} {t('citations')}</span>
                        <span style="font-size: 12px; color: #666; margin-left: 10px;">DOI: {data['doi']}</span>
                        <span style="float: right; font-size: 12px; color: #666;">{t('click_to_toggle')}</span>
                    </div>
                    <div id="citations_{safe_id}" style="display: none;">
            """
            
            for cite in data['citations']:
                html_content += f"""
                        <div class="citation-detail">
                            <div><strong>{html.escape(cite['citing_title'])}</strong></div>
                            <div class="cite-meta">
                                <strong>{t('citing_journal')}:</strong> {html.escape(cite['citing_journal'])} | 
                                <strong>{t('citing_year')}:</strong> {cite['citing_year'] or 'N/A'} | 
                                <strong>{t('citing_date')}:</strong> {cite['citing_date'] or 'N/A'} |
                                <strong>{t('citation_lag')}:</strong> {cite['citation_lag'] if cite['citation_lag'] is not None else 'N/A'} {t('years') if cite['citation_lag'] else ''}
                            </div>
                            <div class="cite-meta">
                                <strong>{t('authors')}:</strong> {', '.join([html.escape(a) for a in cite['citing_authors'][:5]])}{' +' + str(len(cite['citing_authors']) - 5) + ' more' if len(cite['citing_authors']) > 5 else ''} |
                                <strong>{t('countries')}:</strong> {', '.join([html.escape(c) for c in cite['citing_countries'][:3]])}{' +' + str(len(cite['citing_countries']) - 3) + ' more' if len(cite['citing_countries']) > 3 else ''} |
                                <strong>{t('topics')}:</strong> {', '.join([html.escape(t) for t in cite['citing_topics'][:3]])}{' +' + str(len(cite['citing_topics']) - 3) + ' more' if len(cite['citing_topics']) > 3 else ''}
                            </div>
                            <div class="cite-meta">
                                <a href="https://doi.org/{cite['citing_doi']}" target="_blank" class="doi-link">DOI: {cite['citing_doi']}</a>
                            </div>
                        </div>
                """
            
            html_content += """
                    </div>
            """
        
        html_content += """
                </div>
        """
        
        # ============================================================
        # РАЗДЕЛ 7: ALL PUBLICATIONS
        # ============================================================
        
        # Собираем все года для фильтра
        all_years = sorted(set([p.get('publication_year') for p in self.publications if p.get('publication_year')]), reverse=True)
        year_options = ''.join([f'<option value="{year}">{year}</option>' for year in all_years])
        
        html_content += f"""
                <div id="all_publications" class="section">
                    <div class="section-title"><span class="icon">📚</span> {t('all_publications')}</div>
                    
                    <div class="filter-section">
                        <div class="filter-row">
                            <div>
                                <label for="yearFilter">{t('filter_by_year')}:</label>
                                <select id="yearFilter" onchange="filterPublications()">
                                    <option value="">{t('all_years')}</option>
                                    {year_options}
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
                                <input type="number" id="citationFilter" placeholder="Min citations..." min="0" onchange="filterPublications()">
                            </div>
                            <div>
                                <span id="visibleCount" style="font-weight: 500;">{t('publications')}: {len(self.publications)}</span>
                            </div>
                        </div>
                    </div>
                    
                    <div style="overflow-x: auto; max-height: 800px; overflow-y: auto;">
                        <table id="publicationsTable">
                            <thead>
                                <tr>
                                    <th onclick="sortTable(0)" style="cursor: pointer;">#</th>
                                    <th onclick="sortTable(1)" style="cursor: pointer;">{t('title')}</th>
                                    <th onclick="sortTable(2)" style="cursor: pointer;">{t('year')}</th>
                                    <th onclick="sortTable(3)" style="cursor: pointer;">{t('citations')}</th>
                                    <th onclick="sortTable(4)" style="cursor: pointer;">{t('citations_per_year_col')}</th>
                                    <th onclick="sortTable(5)" style="cursor: pointer;">{t('journal')}</th>
                                    <th>{t('authors')}</th>
                                    <th>{t('affiliations')}</th>
                                    <th>DOI</th>
                                    <th>{t('show_citations')}</th>
                                </tr>
                            </thead>
                            <tbody>
        """
        
        for i, p in enumerate(self.publications):
            pub_id = p.get('id', '')
            safe_id = pub_id.replace('https://openalex.org/', '').replace('/', '_')
            authors_str = ', '.join(p.get('authors', [])[:3])
            if len(p.get('authors', [])) > 3:
                authors_str += f' +{len(p.get("authors", [])) - 3} more'
            
            affils_str = ', '.join(p.get('affiliations', [])[:3])
            if len(p.get('affiliations', [])) > 3:
                affils_str += f' +{len(p.get("affiliations", [])) - 3} more'
            
            pub_year = p.get('publication_year', 0)
            citations = p.get('cited_by_count', 0)
            citations_per_year = citations / (datetime.now().year - pub_year + 1) if pub_year else 0
            
            html_content += f"""
                                <tr data-year="{pub_year}" data-authors="{', '.join(p.get('authors', []))}" data-citations="{citations}" data-title="{p.get('title', '').lower()}" data-doi="{p.get('doi', '').lower()}" data-affils="{', '.join(p.get('affiliations', []))}">
                                    <td>{i+1}</td>
                                    <td class="word-wrap">{html.escape(p.get('title', 'No title'))}</td>
                                    <td>{pub_year}</td>
                                    <td><span class="citation-count">{citations}</span></td>
                                    <td>{citations_per_year:.1f}</td>
                                    <td>{html.escape(p.get('journal_name', 'Unknown'))}</td>
                                    <td>{html.escape(authors_str)}</td>
                                    <td>{html.escape(affils_str)}</td>
                                    <td><a href="https://doi.org/{p.get('doi', '')}" target="_blank" class="doi-link">{p.get('doi', '')}</a></td>
                                    <td>
                                        <button onclick="toggleCitations('{safe_id}')" style="padding: 3px 8px; border: none; border-radius: 4px; background: {primary}; color: white; cursor: pointer; font-size: 11px;">{t('show_citations')}</button>
                                    </td>
                                </tr>
            """
        
        html_content += """
                            </tbody>
                        </table>
                    </div>
                </div>
        """
        
        # ============================================================
        # FOOTER И СКРИПТЫ
        # ============================================================
        
        html_content += f"""
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
                    if (element.style.display === 'none') {{
                        element.style.display = 'block';
                    }} else {{
                        element.style.display = 'none';
                    }}
                }}
            }}
            
            function filterPublications() {{
                var yearFilter = document.getElementById('yearFilter');
                var titleFilter = document.getElementById('titleFilter');
                var authorFilter = document.getElementById('authorFilter');
                var affilFilter = document.getElementById('affilFilter');
                var citationFilter = document.getElementById('citationFilter');
                
                var year = yearFilter ? yearFilter.value : '';
                var title = titleFilter ? titleFilter.value.toLowerCase() : '';
                var author = authorFilter ? authorFilter.value.toLowerCase() : '';
                var affil = affilFilter ? affilFilter.value.toLowerCase() : '';
                var minCitations = citationFilter ? parseInt(citationFilter.value) || 0 : 0;
                
                var rows = document.querySelectorAll('#publicationsTable tbody tr');
                var visibleCount = 0;
                
                rows.forEach(function(row) {{
                    var show = true;
                    
                    if (year && row.getAttribute('data-year') !== year) {{
                        show = false;
                    }}
                    
                    if (title && !row.getAttribute('data-title').includes(title)) {{
                        show = false;
                    }}
                    
                    if (author && !row.getAttribute('data-authors').toLowerCase().includes(author)) {{
                        show = false;
                    }}
                    
                    if (affil && !row.getAttribute('data-affils').toLowerCase().includes(affil)) {{
                        show = false;
                    }}
                    
                    if (parseInt(row.getAttribute('data-citations')) < minCitations) {{
                        show = false;
                    }}
                    
                    row.style.display = show ? '' : 'none';
                    if (show) visibleCount++;
                }});
                
                var countSpan = document.getElementById('visibleCount');
                if (countSpan) {{
                    countSpan.textContent = 'Visible publications: ' + visibleCount;
                }}
            }}
            
            function sortTable(column) {{
                var table = document.getElementById('publicationsTable');
                var tbody = table.querySelector('tbody');
                var rows = Array.from(tbody.querySelectorAll('tr'));
                var ascending = table.getAttribute('data-sort-dir') !== 'asc';
                
                rows.sort(function(a, b) {{
                    var aVal, bVal;
                    var cells = a.querySelectorAll('td');
                    var cellsB = b.querySelectorAll('td');
                    
                    if (column === 0) {{
                        aVal = parseInt(cells[0].textContent);
                        bVal = parseInt(cellsB[0].textContent);
                    }} else if (column === 1) {{
                        aVal = cells[1].textContent;
                        bVal = cellsB[1].textContent;
                    }} else if (column === 2) {{
                        aVal = parseInt(cells[2].textContent) || 0;
                        bVal = parseInt(cellsB[2].textContent) || 0;
                    }} else if (column === 3) {{
                        aVal = parseInt(cells[3].textContent) || 0;
                        bVal = parseInt(cellsB[3].textContent) || 0;
                    }} else if (column === 4) {{
                        aVal = parseFloat(cells[4].textContent) || 0;
                        bVal = parseFloat(cellsB[4].textContent) || 0;
                    }} else if (column === 5) {{
                        aVal = cells[5].textContent;
                        bVal = cellsB[5].textContent;
                    }}
                    
                    if (typeof aVal === 'string') {{
                        aVal = aVal.toLowerCase();
                        bVal = bVal.toLowerCase();
                        return ascending ? (aVal > bVal ? 1 : -1) : (aVal < bVal ? 1 : -1);
                    }} else {{
                        return ascending ? (aVal - bVal) : (bVal - aVal);
                    }}
                }});
                
                rows.forEach(function(row) {{
                    tbody.appendChild(row);
                }});
                
                table.setAttribute('data-sort-dir', ascending ? 'asc' : 'desc');
            }}
        </script>
        </body>
        </html>
        """
        
        return html_content

# ============================================
# ОСНОВНАЯ ФУНКЦИЯ ЗАПУСКА ДЛЯ STREAMLIT
# ============================================

def run_journal_analysis(issn: str, period: Any, max_workers: int = MAX_WORKERS, progress_callback=None) -> Tuple[JournalAnalyzer, Dict]:
    """Запускает полный анализ журнала"""
    
    if not issn or not period:
        return None, {}
    
    analyzer = JournalAnalyzer(issn, period, max_workers)
    
    # Этап 1: Сбор статей
    if progress_callback:
        progress_callback(0, 0, 'fetching_articles')
    
    total_pubs = analyzer.fetch_publications()
    
    if progress_callback:
        progress_callback(1, 1, 'fetching_articles', total_pubs)
    
    if total_pubs == 0:
        return analyzer, {}
    
    # Этап 2: Сбор цитирований
    if progress_callback:
        progress_callback(0, 0, 'fetching_citations')
    
    total_citations = analyzer.fetch_citations_parallel()
    
    if progress_callback:
        progress_callback(1, 1, 'fetching_citations', total_citations)
    
    # Этап 3: Анализ
    if progress_callback:
        progress_callback(0, 0, 'analyzing')
    
    metrics = analyzer.analyze()
    
    if progress_callback:
        progress_callback(1, 1, 'analyzing')
    
    return analyzer, metrics

def run_profile_analysis(orcid_list: List[str], show_all_authors: bool, journal_logo: Optional[Dict] = None, analysis_mode: str = "orcid_openalex"):
    """Запускает полный анализ профиля ученого для одного или нескольких ORCID с учетом режима анализа"""
    
    current_lang = st.session_state.get('language', 'en')
    def t(key: str, **kwargs) -> str:
        return translate(key, current_lang, **kwargs)
    
    if not orcid_list:
        st.error("⚠️ " + t('no_orcid'))
        return
        
    st.cache_data.clear()
    
    st.info(f"🔍 " + t('analyzing_authors', count=len(orcid_list)) + f" (режим: {'ORCID+OpenAlex' if analysis_mode == 'orcid_openalex' else 'ORCID only'})")
    
    progress_container = st.empty()
    status_container = st.empty()
    analysis_progress = st.progress(0, text=t('starting_analysis'))
    
    try:
        app_logo_base64 = None
        if os.path.exists("icon.png"):
            try:
                with open("icon.png", "rb") as f:
                    app_logo_base64 = base64.b64encode(f.read()).decode()
            except Exception as e:
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
        
        total_authors = len(orcid_list)
        
        stage_weights = {
            'api': 0.60,
            'analysis': 0.25,
            'orcid_profiles': 0.10,
            'visualization': 0.05
        }
        
        def progress_callback(current, total, orcid):
            api_progress = (current / total) * stage_weights['api'] * 100
            analysis_progress.progress(api_progress / 100, text=f"📡 {t('loading_data')}: {orcid} ({current}/{total})")
            status_container.info(f"📡 {t('fetching_data')} {current}/{total}: {orcid}")
        
        def orcid_profiles_callback(current, total):
            base_progress = (stage_weights['api'] + stage_weights['analysis']) * 100
            orcid_progress = (current / total) * stage_weights['orcid_profiles'] * 100
            total_progress = (base_progress + orcid_progress) / 100
            analysis_progress.progress(total_progress, text=f"🆔 {t('fetching_orcid_profiles')} ({current}/{total})")
            status_container.info(f"🆔 {t('fetching_orcid_profiles')} ({current}/{total})")
        
        start_time = time.time()
        
        all_authors_data = asyncio.run(
            analyze_multiple_authors(orcid_list, progress_callback, analysis_mode=analysis_mode)
        )
        
        analysis_progress.progress(stage_weights['api'], text=f"📊 {t('analyzing_data')}...")
        
        all_coauthor_orcids = set()
        for author_data in all_authors_data:
            profile = author_data.get('profile', {})
            top_coauthors = profile.get('top_coauthors_with_orcids', {})
            for name, data in top_coauthors.items():
                if data.get('orcid'):
                    orcid_clean = data['orcid'].replace('https://orcid.org/', '').strip()
                    if orcid_clean:
                        all_coauthor_orcids.add(orcid_clean)
        
        if all_coauthor_orcids:
            coauthor_orcids_list = list(all_coauthor_orcids)[:50]
            
            if SHOW_DEBUG_LOGS:
                print(f"🆔 Получение профилей для {len(coauthor_orcids_list)} уникальных соавторов")
            
            async def fetch_all_profiles():
                async with aiohttp.ClientSession() as session:
                    profiles = await fetch_coauthor_profiles_sequentially(
                        coauthor_orcids_list,
                        session,
                        delay=ORCID_REQUEST_DELAY,
                        max_retries=3
                    )
                    return profiles
            
            coauthor_profiles = asyncio.run(fetch_all_profiles())
            
            orcid_progress = (stage_weights['api'] + stage_weights['analysis'] + stage_weights['orcid_profiles']) * 100
            analysis_progress.progress(orcid_progress / 100, text=f"🆔 {t('orcid_profiles_fetched', count=len(coauthor_profiles))}")
            status_container.info(f"🆔 {t('orcid_profiles_fetched', count=len(coauthor_profiles))}")
            
            for author_data in all_authors_data:
                analyzer = author_data.get('analyzer')
                if analyzer:
                    for orcid, profile_data in coauthor_profiles.items():
                        if orcid not in analyzer.coauthor_profiles:
                            analyzer.coauthor_profiles[orcid] = profile_data
                    
                    if 'profile' in author_data:
                        author_data['profile']['coauthor_profiles'] = analyzer.coauthor_profiles
                    
                    analyzer.analyze_publications()
                    author_data['profile'] = analyzer.profile
                    
                    if USE_CACHE:
                        cache_data = {
                            'publications': analyzer.publications,
                            'author_info': analyzer.author_info,
                            'profile': analyzer.profile,
                            'institution_homepages': analyzer.institution_homepages,
                            'coauthors_with_orcids': analyzer.coauthors_with_orcids,
                            'coauthor_profiles': analyzer.coauthor_profiles,
                            'analysis_mode': analysis_mode,
                            'timestamp': datetime.now().isoformat()
                        }
                        save_to_cache(analyzer.orcid, cache_data)
        
        elapsed = time.time() - start_time
        
        if not all_authors_data:
            st.error(f"❌ {t('data_not_found')}")
            analysis_progress.empty()
            return
        
        sorted_authors = sort_authors_by_h_index(all_authors_data)
        
        viz_start_progress = (stage_weights['api'] + stage_weights['analysis'] + stage_weights['orcid_profiles']) * 100
        analysis_progress.progress(viz_start_progress / 100, text=f"🎨 {t('generating_viz')}...")
        
        for idx, author_data in enumerate(sorted_authors):
            profile = author_data.get('profile', {})
            if profile:
                images = create_visualizations(profile, current_lang)
                author_data['images'] = images
                
                viz_progress = (idx + 1) / len(sorted_authors) * stage_weights['visualization'] * 100
                total_progress = (viz_start_progress + viz_progress) / 100
                analysis_progress.progress(min(total_progress, 0.99), text=f"🎨 {t('creating_charts')} {idx+1}/{len(sorted_authors)}...")
        
        for author_data in sorted_authors:
            profile = author_data.get('profile', {})
            publications = author_data.get('publications', [])
            gap_analysis = detect_temporal_gaps(publications, MIN_GAP_YEARS_FOR_WARNING)
            author_data['gap_analysis'] = gap_analysis
        
        st.session_state['all_authors'] = sorted_authors
        st.session_state['show_all_authors'] = show_all_authors
        st.session_state['journal_logo_base64'] = journal_logo_base64
        st.session_state['app_logo_base64'] = app_logo_base64
        st.session_state['analysis_complete'] = True
        st.session_state['analysis_mode'] = analysis_mode
        
        analysis_progress.progress(1.0, text=f"✅ {t('analysis_complete_text')}!")
        
        st.success(t('analysis_complete', count=len(sorted_authors), time=elapsed))
        
        if len(sorted_authors) > 1:
            best_author = sorted_authors[0]
            st.info(t('best_author', name=best_author.get('author_name', 'Unknown'), h_index=best_author.get('h_index', 0)))
        else:
            st.info(t('single_author', name=sorted_authors[0].get('author_name', 'Unknown'), h_index=sorted_authors[0].get('h_index', 0)))
        
        if show_all_authors and len(sorted_authors) > 1:
            st.info(t('showing_all', count=len(sorted_authors)))
        elif len(sorted_authors) == 1:
            st.info(t('showing_single_only'))
        else:
            st.info(t('showing_single'))
        
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
    if 'show_all_authors' not in st.session_state:
        st.session_state.show_all_authors = False
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
    if 'analysis_mode' not in st.session_state:
        st.session_state.analysis_mode = 'orcid_openalex'
    if 'filter_params' not in st.session_state:
        st.session_state.filter_params = {}
    if 'journal_analyzer' not in st.session_state:
        st.session_state.journal_analyzer = None
    if 'journal_metrics' not in st.session_state:
        st.session_state.journal_metrics = {}
    if 'journal_report' not in st.session_state:
        st.session_state.journal_report = None
    if 'journal_analysis_complete' not in st.session_state:
        st.session_state.journal_analysis_complete = False
    
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
    
    st.markdown("---")
    if os.path.exists("icon.png"):
        col_logo, col_text = st.columns([1, 3])
        with col_logo:
            st.image("icon.png", width=400)
    else:
        st.markdown(f"### {t('journal_analysis_title')}")
    st.markdown("---")
    
    # Tabs
    tab1, tab2, tab3 = st.tabs([
        t('load_data'),
        t('journal_analysis'),
        t('reports')
    ])
    
    with tab1:
        st.markdown('<div class="custom-tab fade-in">', unsafe_allow_html=True)
        st.header(t('load_data'))
        
        issn_input = st.text_input(
            t('issn_input'),
            placeholder=t('issn_placeholder'),
            help=t('issn_help')
        )
        
        period_input = st.text_input(
            t('period_input'),
            placeholder=t('period_placeholder'),
            help=t('period_help')
        )
        
        max_workers = st.slider(
            t('workers_slider'),
            min_value=4,
            max_value=12,
            value=MAX_WORKERS,
            step=1,
            help=t('workers_help')
        )
        
        if st.button(t('analyze_button'), type="primary", width='stretch'):
            if not issn_input:
                st.error(t('no_issn'))
            elif not period_input:
                st.error(t('no_period'))
            else:
                period = parse_period(period_input)
                if period is None:
                    st.error("⚠️ Неверный формат периода. Используйте: 2020-2023, 2020,2021,2022, или 2020")
                else:
                    with st.spinner(t('starting_analysis')):
                        # Создаем контейнеры для прогресса
                        progress_col1, progress_col2, progress_col3 = st.columns(3)
                        
                        with progress_col1:
                            st.write("📚 " + t('stage_fetching_articles'))
                            bar1 = st.progress(0)
                            status1 = st.empty()
                        
                        with progress_col2:
                            st.write("🔗 " + t('stage_fetching_citations'))
                            bar2 = st.progress(0)
                            status2 = st.empty()
                        
                        with progress_col3:
                            st.write("📊 " + t('stage_analyzing'))
                            bar3 = st.progress(0)
                            status3 = st.empty()
                        
                        def progress_callback(stage, total, stage_name, count=0):
                            if stage_name == 'fetching_articles':
                                if total > 0:
                                    progress = stage / total if stage < total else 1.0
                                    bar1.progress(progress)
                                    status1.text(t('articles_found', count=stage))
                            elif stage_name == 'fetching_citations':
                                if total > 0:
                                    progress = stage / total if stage < total else 1.0
                                    bar2.progress(progress)
                                    status2.text(t('citations_fetched', count=stage))
                            elif stage_name == 'analyzing':
                                bar3.progress(stage)
                                if stage == 0:
                                    status3.text(t('analyzing_data'))
                                elif stage == 1:
                                    status3.text("✅ " + t('analysis_complete_text'))
                        
                        start_time = time.time()
                        
                        analyzer, metrics = run_journal_analysis(
                            issn_input,
                            period,
                            max_workers,
                            progress_callback
                        )
                        
                        elapsed = time.time() - start_time
                        
                        if analyzer and metrics:
                            st.session_state.journal_analyzer = analyzer
                            st.session_state.journal_metrics = metrics
                            st.session_state.journal_analysis_complete = True
                            
                            # Генерируем отчет
                            theme_colors = {
                                'primary': st.session_state.primary_color,
                                'secondary': st.session_state.secondary_color
                            }
                            st.session_state.journal_report = analyzer.generate_html_report(
                                current_lang,
                                theme_colors
                            )
                            
                            st.success(t('analysis_complete', count=metrics.get('total_publications', 0), time=elapsed))
                            
                            # Показываем основные метрики
                            col1, col2, col3, col4, col5 = st.columns(5)
                            with col1:
                                st.metric(t('publications'), metrics.get('total_publications', 0))
                            with col2:
                                st.metric(t('total_citations'), f"{metrics.get('total_citations', 0):,}")
                            with col3:
                                st.metric(t('h_index'), metrics.get('h_index', 0))
                            with col4:
                                st.metric(t('unique_authors'), metrics.get('unique_authors', 0))
                            with col5:
                                st.metric(t('unique_countries'), metrics.get('unique_countries', 0))
                            
                            st.balloons()
                        else:
                            st.error("❌ " + t('data_not_found'))
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        if st.session_state.journal_analysis_complete and st.session_state.journal_analyzer:
            metrics = st.session_state.journal_metrics
            analyzer = st.session_state.journal_analyzer
            
            st.markdown(f"## {t('journal_analysis')}")
            
            # Показываем основные метрики
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.metric(t('publications'), metrics.get('total_publications', 0))
            with col2:
                st.metric(t('total_citations'), f"{metrics.get('total_citations', 0):,}")
            with col3:
                st.metric(t('h_index'), metrics.get('h_index', 0))
            with col4:
                st.metric(t('i10_index'), metrics.get('i10_index', 0))
            with col5:
                st.metric(t('unique_authors'), metrics.get('unique_authors', 0))
            
            # Open Access Breakdown
            oa_breakdown = metrics.get('open_access_breakdown', {})
            if oa_breakdown:
                st.markdown(f"### {t('open_access_breakdown')}")
                oa_cols = st.columns(len(oa_breakdown))
                for idx, (status, count) in enumerate(oa_breakdown.items()):
                    label_map = {
                        'gold': t('gold'),
                        'hybrid': t('hybrid'),
                        'green': t('green'),
                        'bronze': t('bronze'),
                        'closed': t('closed'),
                        'unknown': t('unknown')
                    }
                    with oa_cols[idx % len(oa_cols)]:
                        st.metric(label_map.get(status, status), count)
            
            # Топ авторы
            if analyzer.author_data:
                st.markdown(f"### {t('top_authors')}")
                author_df = pd.DataFrame(analyzer.author_data[:10])
                st.dataframe(author_df[['rank', 'name', 'publications', 'citations']], width='stretch')
            
            # Топ аффилиации
            if analyzer.top_affiliations:
                st.markdown(f"### {t('top_affiliations_analyzed')}")
                affil_df = pd.DataFrame(list(analyzer.top_affiliations.items())[:10], columns=['Affiliation', 'Publications'])
                st.dataframe(affil_df, width='stretch')
            
            # Топ цитирующие авторы
            if analyzer.top_citing_authors:
                st.markdown(f"### {t('top_citing_authors')}")
                citing_author_df = pd.DataFrame(list(analyzer.top_citing_authors.items())[:10], columns=['Author', 'Citations'])
                st.dataframe(citing_author_df, width='stretch')
            
            # Топ цитирующие журналы
            if analyzer.top_citing_journals:
                st.markdown(f"### {t('top_citing_journals')}")
                citing_journal_df = pd.DataFrame(list(analyzer.top_citing_journals.items())[:10], columns=['Journal', 'Citations'])
                st.dataframe(citing_journal_df, width='stretch')
            
            # Топ темы
            if analyzer.topic_analysis:
                st.markdown(f"### {t('topics_analysis')}")
                topic_df = pd.DataFrame(list(analyzer.topic_analysis.items())[:10], columns=['Topic', 'Data'])
                topic_df['Analyzed'] = topic_df['Data'].apply(lambda x: x['analyzed_count'])
                topic_df['Citing'] = topic_df['Data'].apply(lambda x: x['citing_count'])
                topic_df['Total Norm'] = topic_df['Data'].apply(lambda x: f"{x['total_norm']:.3f}")
                topic_df = topic_df[['Topic', 'Analyzed', 'Citing', 'Total Norm']]
                st.dataframe(topic_df, width='stretch')
            
            # Самые цитируемые
            if analyzer.most_cited:
                st.markdown(f"### {t('most_cited_publications')}")
                most_cited_df = pd.DataFrame(analyzer.most_cited[:10])
                most_cited_df = most_cited_df[['rank', 'title', 'year', 'citations', 'citations_per_year', 'doi']]
                st.dataframe(most_cited_df, width='stretch')
            
        else:
            st.info(t('no_data'))
    
    with tab3:
        if st.session_state.journal_analysis_complete and st.session_state.journal_report:
            st.markdown(f"## {t('html_report')}")
            
            if st.button(t('download_report'), type="primary", width='stretch'):
                issn_clean = st.session_state.journal_analyzer.issn.replace('-', '')
                filename = f"journal_analysis_{issn_clean}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
                
                st.download_button(
                    label="📥 " + t('download_report'),
                    data=st.session_state.journal_report.encode('utf-8'),
                    file_name=filename,
                    mime="text/html",
                    width='stretch'
                )
            
            st.markdown("---")
            st.markdown(f"### {t('report_preview')}")
            st.info(t('download_hint'))
            
            # Отображаем HTML отчет
            st.components.v1.html(st.session_state.journal_report, height=800, scrolling=True)
        else:
            st.info(t('no_data_reports'))

if __name__ == "__main__":
    main()
