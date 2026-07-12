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
MAX_WORKERS = 8  # Количество параллельных потоков для сбора цитирований
MAX_CITING_PER_PAPER = 300  # Максимум цитирующих работ на статью

# Параметры вывода
SHOW_DEBUG_LOGS = True  # Показывать детальные логи
GENERATE_HTML_REPORT = True  # Генерировать HTML отчет
USE_CACHE = False  # Кэширование результатов
LOGO_PATH = None  # Путь к логотипу журнала (устанавливается через виджет)

# Лимиты для анализа
MAX_PUBLICATIONS_TO_ANALYZE = 1000  # Максимум статей для анализа
MIN_YEAR_FOR_TREND = 5  # Сколько лет для тренда

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
from threading import Lock
import random
from tqdm import tqdm
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set, Tuple, Any
from collections import defaultdict, Counter

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
        'analysis_params': '📊 Analysis Parameters',
        'use_cache': '💾 Use cache',
        'clear_cache': '🗑️ Clear cache',
        'cache_cleared': '✅ Cache cleared!',
        'load_data': '📥 Load Data',
        'journal_analysis': '📊 Journal Analysis',
        'reports': '📄 Reports',
        'issn_input': 'Journal ISSN',
        'issn_placeholder': '0028-0836',
        'period_input': 'Analysis Period',
        'period_placeholder': '2020-2023 or 2020,2021,2022 or 2020',
        'workers_label': 'Parallel Workers',
        'analyze_button': '🔍 Analyze Journal',
        'no_issn': '⚠️ Enter ISSN',
        'analysis_complete': '✅ Analysis complete! Found {count} articles in {time:.1f} sec.',
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
        'papers': 'Papers',
        'no_data_collab': 'No data',
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
        'data_not_found': 'Data not found. Check ISSN correctness.',
        'error_occurred': 'Error occurred',
        'analyzing_authors': 'Analyzing {count} author(s)...',
        'starting_analysis': 'Starting analysis...',
        'fetching_data': 'Fetching data',
        'analysis_complete_text': 'Analysis complete',
        'creating_charts': 'Creating charts',
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
        'overview': 'Overview',
        'analyzed_articles': 'Analyzed Articles',
        'author_analysis': 'Author Analysis',
        'top_affiliations': 'Top Affiliations',
        'geographic_analysis': 'Geographic Analysis',
        'unique_countries_per_publication': 'Unique Countries per Publication',
        'authors_per_country': 'Authors per Country',
        'collaboration_patterns': 'Collaboration Patterns',
        'collaboration_couples': 'Collaboration Couples',
        'citation_analysis': 'Citation Analysis',
        'citation_dynamics_by_year': 'Citation Dynamics by Year',
        'cumulative_citations': 'Cumulative Citations',
        'citation_network_heatmap': 'Citation Network Heatmap',
        'most_cited_publications': 'Most Cited Publications',
        'citing_works_analysis': 'Citing Works Analysis',
        'total_citing_works': 'Total Citing Works',
        'unique_citing_authors': 'Unique Citing Authors',
        'unique_citing_affiliations': 'Unique Citing Affiliations',
        'unique_citing_countries': 'Unique Citing Countries',
        'unique_citing_journals': 'Unique Citing Journals',
        'unique_citing_publishers': 'Unique Citing Publishers',
        'top_citing_authors': 'Top Citing Authors',
        'top_citing_affiliations': 'Top Citing Affiliations',
        'top_citing_countries': 'Top Citing Countries',
        'top_citing_journals': 'Top Citing Journals',
        'top_citing_publishers': 'Top Citing Publishers',
        'topics_analysis': 'Topics Analysis',
        'topics_table': 'Topics Table',
        'top_cited_topics': 'Top Cited Topics',
        'top_cited_subtopics': 'Top Cited Subtopics',
        'top_cited_fields': 'Top Cited Fields',
        'top_cited_domains': 'Top Cited Domains',
        'top_cited_concepts': 'Top Cited Concepts',
        'detailed_citations': 'Detailed Citations',
        'all_publications': 'All Publications',
        'analyzed_count': 'Analyzed Count',
        'citing_count': 'Citing Count',
        'analyzed_norm_count': 'Analyzed Norm Count',
        'citing_norm_count': 'Citing Norm Count',
        'total_norm_count': 'Total Norm Count',
        'first_year': 'First Year',
        'peak_year': 'Peak Year',
        'rank': 'Rank',
        'authors': 'Authors',
        'citations_per_year': 'Citations/Year',
        'citing_journal': 'Citing Journal',
        'citing_year': 'Citing Year',
        'citing_date': 'Citing Date',
        'citation_lag': 'Citation Lag',
        'show_citations': 'Show Citations',
        'filter_by_year': 'Filter by Year',
        'filter_by_author': 'Filter by Author',
        'filter_by_citations': 'Filter by Citations',
        'search_publications': 'Search Publications',
        'all_years': 'All Years',
        'single_country': 'Single Country',
        'international': 'International',
        'publication_year': 'Publication Year',
        'citation_year': 'Citation Year',
        'citations_count': 'Citations Count',
        'cumulative': 'Cumulative',
        'gold': 'Gold',
        'hybrid': 'Hybrid',
        'green': 'Green',
        'bronze': 'Bronze',
        'closed': 'Closed',
        'unknown': 'Unknown',
        'diamond': 'Diamond',
        'overview_metrics': 'Overview Metrics',
        'total_publications': 'Total Publications',
        'unique_authors': 'Unique Authors',
        'unique_affiliations': 'Unique Affiliations',
        'unique_countries': 'Unique Countries',
        'avg_affiliations_per_paper': 'Avg Affiliations/Paper',
        'avg_countries_per_paper': 'Avg Countries/Paper',
        'international_collaboration_rate': 'International Collaboration Rate',
        'unique_citing_authors': 'Unique Citing Authors',
        'publication_year': 'Publication Year',
        'citation_year': 'Citation Year',
        'citations_count': 'Citations Count',
        'cumulative': 'Cumulative',
        'gold': 'Gold',
        'hybrid': 'Hybrid',
        'green': 'Green',
        'bronze': 'Bronze',
        'closed': 'Closed',
        'unknown': 'Unknown',
        'diamond': 'Diamond',
        'analyzed_count': 'Analyzed Count',
        'citing_count': 'Citing Count',
        'analyzed_norm_count': 'Analyzed Norm Count',
        'citing_norm_count': 'Citing Norm Count',
        'total_norm_count': 'Total Norm Count',
        'first_year': 'First Year',
        'peak_year': 'Peak Year',
        'rank': 'Rank',
        'authors': 'Authors',
        'citations_per_year': 'Citations/Year',
        'citing_journal': 'Citing Journal',
        'citing_year': 'Citing Year',
        'citing_date': 'Citing Date',
        'citation_lag': 'Citation Lag',
        'show_citations': 'Show Citations',
        'filter_by_year': 'Filter by Year',
        'filter_by_author': 'Filter by Author',
        'filter_by_citations': 'Filter by Citations',
        'search_publications': 'Search Publications',
        'all_years': 'All Years',
        'single_country': 'Single Country',
        'international': 'International',
        'publication_year': 'Publication Year',
        'citation_year': 'Citation Year',
        'citations_count': 'Citations Count',
        'cumulative': 'Cumulative',
        'gold': 'Gold',
        'hybrid': 'Hybrid',
        'green': 'Green',
        'bronze': 'Bronze',
        'closed': 'Closed',
        'unknown': 'Unknown',
        'diamond': 'Diamond',
        'overview_metrics': 'Overview Metrics',
        'total_publications': 'Total Publications',
        'unique_authors': 'Unique Authors',
        'unique_affiliations': 'Unique Affiliations',
        'unique_countries': 'Unique Countries',
        'avg_affiliations_per_paper': 'Avg Affiliations/Paper',
        'avg_countries_per_paper': 'Avg Countries/Paper',
        'international_collaboration_rate': 'International Collaboration Rate',
        'unique_citing_authors': 'Unique Citing Authors',
        'stage_loading_articles': 'Loading articles',
        'stage_citing_works': 'Collecting citing works',
        'stage_generating_report': 'Generating report',
        'loading_articles_progress': 'Loading articles: {current}/{total} pages',
        'citing_works_progress': 'Processing citing works: {current}/{total}',
        'generating_report_progress': 'Generating HTML report...',
        'total_articles_found': 'Total articles found: {count}',
        'total_citations_found': 'Total citations found: {count}',
        'click_to_toggle': 'Click to toggle citations',
        'concepts': 'Concepts',
        'fields': 'Fields',
        'domains': 'Domains',
        'topics': 'Topics',
        'subtopics': 'Subtopics',
        'overview': 'Overview',
        'analyzed_articles': 'Analyzed Articles',
        'author_analysis': 'Author Analysis',
        'top_affiliations': 'Top Affiliations',
        'geographic_analysis': 'Geographic Analysis',
        'unique_countries_per_publication': 'Unique Countries per Publication',
        'authors_per_country': 'Authors per Country',
        'collaboration_patterns': 'Collaboration Patterns',
        'collaboration_couples': 'Collaboration Couples',
        'citation_analysis': 'Citation Analysis',
        'citation_dynamics_by_year': 'Citation Dynamics by Year',
        'cumulative_citations': 'Cumulative Citations',
        'citation_network_heatmap': 'Citation Network Heatmap',
        'most_cited_publications': 'Most Cited Publications',
        'citing_works_analysis': 'Citing Works Analysis',
        'total_citing_works': 'Total Citing Works',
        'unique_citing_authors': 'Unique Citing Authors',
        'unique_citing_affiliations': 'Unique Citing Affiliations',
        'unique_citing_countries': 'Unique Citing Countries',
        'unique_citing_journals': 'Unique Citing Journals',
        'unique_citing_publishers': 'Unique Citing Publishers',
        'top_citing_authors': 'Top Citing Authors',
        'top_citing_affiliations': 'Top Citing Affiliations',
        'top_citing_countries': 'Top Citing Countries',
        'top_citing_journals': 'Top Citing Journals',
        'top_citing_publishers': 'Top Citing Publishers',
        'topics_analysis': 'Topics Analysis',
        'topics_table': 'Topics Table',
        'top_cited_topics': 'Top Cited Topics',
        'top_cited_subtopics': 'Top Cited Subtopics',
        'top_cited_fields': 'Top Cited Fields',
        'top_cited_domains': 'Top Cited Domains',
        'top_cited_concepts': 'Top Cited Concepts',
        'detailed_citations': 'Detailed Citations',
        'all_publications': 'All Publications',
        'analyzed_count': 'Analyzed Count',
        'citing_count': 'Citing Count',
        'analyzed_norm_count': 'Analyzed Norm Count',
        'citing_norm_count': 'Citing Norm Count',
        'total_norm_count': 'Total Norm Count',
        'first_year': 'First Year',
        'peak_year': 'Peak Year',
        'rank': 'Rank',
        'authors': 'Authors',
        'citations_per_year': 'Citations/Year',
        'citing_journal': 'Citing Journal',
        'citing_year': 'Citing Year',
        'citing_date': 'Citing Date',
        'citation_lag': 'Citation Lag',
        'show_citations': 'Show Citations',
        'filter_by_year': 'Filter by Year',
        'filter_by_author': 'Filter by Author',
        'filter_by_citations': 'Filter by Citations',
        'search_publications': 'Search Publications',
        'all_years': 'All Years',
        'single_country': 'Single Country',
        'international': 'International',
        'publication_year': 'Publication Year',
        'citation_year': 'Citation Year',
        'citations_count': 'Citations Count',
        'cumulative': 'Cumulative',
        'gold': 'Gold',
        'hybrid': 'Hybrid',
        'green': 'Green',
        'bronze': 'Bronze',
        'closed': 'Closed',
        'unknown': 'Unknown',
        'diamond': 'Diamond',
        'overview_metrics': 'Overview Metrics',
        'total_publications': 'Total Publications',
        'unique_authors': 'Unique Authors',
        'unique_affiliations': 'Unique Affiliations',
        'unique_countries': 'Unique Countries',
        'avg_affiliations_per_paper': 'Avg Affiliations/Paper',
        'avg_countries_per_paper': 'Avg Countries/Paper',
        'international_collaboration_rate': 'International Collaboration Rate',
        'unique_citing_authors': 'Unique Citing Authors',
        'stage_loading_articles': 'Loading articles',
        'stage_citing_works': 'Collecting citing works',
        'stage_generating_report': 'Generating report',
        'loading_articles_progress': 'Loading articles: {current}/{total} pages',
        'citing_works_progress': 'Processing citing works: {current}/{total}',
        'generating_report_progress': 'Generating HTML report...',
        'total_articles_found': 'Total articles found: {count}',
        'total_citations_found': 'Total citations found: {count}',
        'click_to_toggle': 'Click to toggle citations',
        'concepts': 'Concepts',
        'fields': 'Fields',
        'domains': 'Domains',
        'topics': 'Topics',
        'subtopics': 'Subtopics',
        'filter_by_title': 'Filter by Title Word(s)',
        'filter_by_affiliations': 'Filter by Affiliations',
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
        'period_input': 'Период анализа',
        'period_placeholder': '2020-2023 или 2020,2021,2022 или 2020',
        'workers_label': 'Параллельных потоков',
        'analyze_button': '🔍 Анализировать журнал',
        'no_issn': '⚠️ Введите ISSN',
        'analysis_complete': '✅ Анализ завершен! Найдено {count} статей за {time:.1f} сек.',
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
        'papers': 'Статей',
        'no_data_collab': 'Нет данных',
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
        'footer': '© Advanced Journal Analysis Tool / Создано daM / Chimica Techno Acta',
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
        'data_not_found': 'Данные не найдены. Проверьте правильность ISSN.',
        'error_occurred': 'Произошла ошибка',
        'analyzing_authors': 'Анализирую {count} авторов...',
        'starting_analysis': 'Начинаем анализ...',
        'fetching_data': 'Получение данных',
        'analysis_complete_text': 'Анализ завершен',
        'creating_charts': 'Создание графиков',
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
        'overview': 'Обзор',
        'analyzed_articles': 'Анализируемые статьи',
        'author_analysis': 'Анализ авторов',
        'top_affiliations': 'Топ аффилиаций',
        'geographic_analysis': 'Географический анализ',
        'unique_countries_per_publication': 'Уникальные страны на публикацию',
        'authors_per_country': 'Авторы по странам',
        'collaboration_patterns': 'Паттерны коллабораций',
        'collaboration_couples': 'Пары коллабораций',
        'citation_analysis': 'Цитатный анализ',
        'citation_dynamics_by_year': 'Динамика цитирований по годам',
        'cumulative_citations': 'Накопленные цитирования',
        'citation_network_heatmap': 'Тепловая карта цитирований',
        'most_cited_publications': 'Самые цитируемые публикации',
        'citing_works_analysis': 'Анализ цитирующих работ',
        'total_citing_works': 'Всего цитирующих работ',
        'unique_citing_authors': 'Уникальных цитирующих авторов',
        'unique_citing_affiliations': 'Уникальных цитирующих аффилиаций',
        'unique_citing_countries': 'Уникальных цитирующих стран',
        'unique_citing_journals': 'Уникальных цитирующих журналов',
        'unique_citing_publishers': 'Уникальных цитирующих издательств',
        'top_citing_authors': 'Топ цитирующих авторов',
        'top_citing_affiliations': 'Топ цитирующих аффилиаций',
        'top_citing_countries': 'Топ цитирующих стран',
        'top_citing_journals': 'Топ цитирующих журналов',
        'top_citing_publishers': 'Топ цитирующих издательств',
        'topics_analysis': 'Тематический анализ',
        'topics_table': 'Таблица тем',
        'top_cited_topics': 'Топ цитируемых тем',
        'top_cited_subtopics': 'Топ цитируемых подтем',
        'top_cited_fields': 'Топ цитируемых полей',
        'top_cited_domains': 'Топ цитируемых доменов',
        'top_cited_concepts': 'Топ цитируемых концептов',
        'detailed_citations': 'Детальные цитирования',
        'all_publications': 'Все публикации',
        'analyzed_count': 'Кол-во в анализе',
        'citing_count': 'Кол-во цитирований',
        'analyzed_norm_count': 'Норм. кол-во в анализе',
        'citing_norm_count': 'Норм. кол-во цитирований',
        'total_norm_count': 'Общее норм. кол-во',
        'first_year': 'Первый год',
        'peak_year': 'Пиковый год',
        'rank': 'Ранг',
        'authors': 'Авторы',
        'citations_per_year': 'Цитирований/год',
        'citing_journal': 'Цитирующий журнал',
        'citing_year': 'Год цитирования',
        'citing_date': 'Дата цитирования',
        'citation_lag': 'Задержка цитирования',
        'show_citations': 'Показать цитирования',
        'filter_by_year': 'Фильтр по году',
        'filter_by_author': 'Фильтр по автору',
        'filter_by_citations': 'Фильтр по цитированиям',
        'search_publications': 'Поиск публикаций',
        'all_years': 'Все годы',
        'single_country': 'Одна страна',
        'international': 'Международные',
        'publication_year': 'Год публикации',
        'citation_year': 'Год цитирования',
        'citations_count': 'Кол-во цитирований',
        'cumulative': 'Накопленные',
        'gold': 'Золотой',
        'hybrid': 'Гибридный',
        'green': 'Зеленый',
        'bronze': 'Бронзовый',
        'closed': 'Закрытый',
        'unknown': 'Неизвестный',
        'diamond': 'Алмазный',
        'overview_metrics': 'Обзор метрик',
        'total_publications': 'Всего публикаций',
        'unique_authors': 'Уникальных авторов',
        'unique_affiliations': 'Уникальных аффилиаций',
        'unique_countries': 'Уникальных стран',
        'avg_affiliations_per_paper': 'Среднее аффилиаций на статью',
        'avg_countries_per_paper': 'Среднее стран на статью',
        'international_collaboration_rate': 'Уровень международных коллабораций',
        'unique_citing_authors': 'Уникальных цитирующих авторов',
        'stage_loading_articles': 'Загрузка статей',
        'stage_citing_works': 'Сбор цитирующих работ',
        'stage_generating_report': 'Генерация отчета',
        'loading_articles_progress': 'Загрузка статей: {current}/{total} страниц',
        'citing_works_progress': 'Обработка цитирующих работ: {current}/{total}',
        'generating_report_progress': 'Генерация HTML отчета...',
        'total_articles_found': 'Всего найдено статей: {count}',
        'total_citations_found': 'Всего найдено цитирований: {count}',
        'click_to_toggle': 'Нажмите для показа цитирований',
        'concepts': 'Концепты',
        'fields': 'Поля',
        'domains': 'Домены',
        'topics': 'Темы',
        'subtopics': 'Подтемы',
        'filter_by_title': 'Фильтр по словам в названии',
        'filter_by_affiliations': 'Фильтр по аффилиациям',
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
# СТРУКТУРЫ ДАННЫХ
# ============================================

@dataclass
class Author:
    """Класс для представления автора"""
    display_name: str
    orcid: Optional[str] = None
    affiliations: List[str] = field(default_factory=list)
    countries: List[str] = field(default_factory=list)
    
@dataclass
class Topic:
    """Класс для представления темы"""
    display_name: str
    subfield: str = ''
    field: str = ''
    domain: str = ''
    score: float = 0.0
    
@dataclass
class Concept:
    """Класс для представления концепта"""
    display_name: str
    level: int = 0
    score: float = 0.0

@dataclass
class Citation:
    """Класс для представления цитирования"""
    citing_work_id: str
    citing_doi: str
    citing_title: str
    citing_year: int
    citing_date: str
    citing_journal: str
    citing_publisher: str
    citing_authors: List[Author] = field(default_factory=list)
    citing_countries: List[str] = field(default_factory=list)
    citing_affiliations: List[str] = field(default_factory=list)
    citing_topics: List[Topic] = field(default_factory=list)
    citation_lag: int = 0

@dataclass
class Article:
    """Класс для представления анализируемой статьи"""
    id: str
    doi: str
    title: str
    publication_year: int
    cited_by_count: int
    journal_name: str
    publisher: str
    is_oa: bool = False
    oa_status: str = 'unknown'
    authors: List[Author] = field(default_factory=list)
    affiliations: List[str] = field(default_factory=list)
    countries: List[str] = field(default_factory=list)
    topics: List[Topic] = field(default_factory=list)
    concepts: List[Concept] = field(default_factory=list)
    fields: List[str] = field(default_factory=list)
    domains: List[str] = field(default_factory=list)
    citations: List[Citation] = field(default_factory=list)
    citations_per_year: float = 0.0

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

# ============================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================

def normalize_issn(issn_str: str) -> str:
    """Нормализует ISSN"""
    cleaned = re.sub(r'[^0-9Xx]', '', str(issn_str).strip())
    if len(cleaned) == 8:
        return f"{cleaned[:4]}-{cleaned[4:]}".upper()
    return cleaned.upper()

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

def get_cache_path_journal(issn: str, period_str: str) -> str:
    """Возвращает путь к файлу кэша для ISSN и периода"""
    issn_clean = normalize_issn(issn)
    if not os.path.exists('cache'):
        os.makedirs('cache')
    return f"cache/journal_{issn_clean}_{period_str}.json"

def load_from_cache_journal(issn: str, period_str: str) -> Optional[Dict]:
    """Загружает данные из кэша для журнала"""
    if not USE_CACHE:
        return None
    
    cache_path = get_cache_path_journal(issn, period_str)
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

def save_to_cache_journal(issn: str, period_str: str, data: Dict):
    """Сохраняет данные в кэш для журнала"""
    if not USE_CACHE:
        return
    
    cache_path = get_cache_path_journal(issn, period_str)
    try:
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✅ Данные сохранены в кэш: {cache_path}")
    except Exception as e:
        print(f"⚠️ Ошибка сохранения кэша: {e}")

# ============================================
# API КЛИЕНТ ДЛЯ OPENALEX
# ============================================

class OpenAlexClient:
    """Клиент для работы с OpenAlex API с параллельными запросами"""
    
    def __init__(self, max_workers: int = 8, max_citing: int = 300):
        self.max_workers = max_workers
        self.max_citing = max_citing
        self.lock = Lock()
        self.base_delay = 0.35
        self.max_retries = 4
        
    def smart_get(self, url: str, params: Dict, retries: int = None) -> Optional[Dict]:
        """Умный GET запрос с защитой от 429"""
        if retries is None:
            retries = self.max_retries
            
        for attempt in range(retries):
            try:
                with self.lock:
                    time.sleep(random.uniform(0.1, self.base_delay))
                
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
                    print(f"⚠️ Ошибка запроса: {e}")
                time.sleep(1.5 * (2 ** attempt))
                
        return None
    
    def get_citing_dois(self, oa_id: str) -> List[str]:
        """Получает цитирующие DOI для работы"""
        citing = []
        cursor = "*"
        base_url = "https://api.openalex.org/works"
        
        for _ in range(8):  # ограничение пагинации
            data = self.smart_get(base_url, {
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
        
        return citing[:self.max_citing]
    
    def get_journal_articles(self, issn: str, years, progress_callback=None) -> List[Dict]:
        """Получает все статьи журнала за указанный период"""
        normalized = normalize_issn(issn)
        
        # Формируем фильтр по годам
        if isinstance(years, list):
            year_filter = "|".join(f"publication_year:{y}" for y in years)
        elif isinstance(years, tuple):
            year_filter = f"publication_year:{years[0]}-{years[1]}"
        else:
            year_filter = f"publication_year:{years}"
        
        articles = []
        cursor = "*"
        base_url = "https://api.openalex.org/works"
        page_count = 0
        
        while True:
            page_count += 1
            data = self.smart_get(base_url, {
                "filter": f"primary_location.source.issn:{normalized},{year_filter}",
                "per_page": 200,
                "select": "id,doi,publication_year,cited_by_count,title,primary_location,type,open_access,authorships,topics,concepts",
                "cursor": cursor
            })
            
            if not data or not data.get("results"):
                break
                
            for w in data["results"]:
                doi = w.get("doi")
                if doi:
                    doi = doi.replace("https://doi.org/", "")
                articles.append({
                    "id": w.get("id", ""),
                    "doi": doi or "N/A",
                    "title": w.get("title", "No title"),
                    "publication_year": w.get("publication_year"),
                    "cited_by_count": w.get("cited_by_count", 0),
                    "openalex_id": w.get("id", "").replace("https://openalex.org/", ""),
                    "raw_data": w  # Сохраняем для дальнейшей обработки
                })
            
            if progress_callback:
                progress_callback(page_count, articles)
            
            cursor = data.get("meta", {}).get("next_cursor")
            if not cursor:
                break
        
        return articles
    
    def get_citing_works_batch(self, articles: List[Dict], progress_callback=None) -> Dict[str, List[str]]:
        """Параллельно получает цитирующие работы для списка статей"""
        citing_map = {}
        futures = {}
        
        # Фильтруем статьи с цитированиями
        citing_articles = [a for a in articles if a.get('cited_by_count', 0) > 0 and a.get('doi') != "N/A"]
        
        if not citing_articles:
            return {}
        
        if SHOW_DEBUG_LOGS:
            print(f"⚡ Запуск параллельного сбора цитирований для {len(citing_articles)} статей ({self.max_workers} потоков)")
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            for article in citing_articles:
                oa_id = article.get('openalex_id', '')
                doi = article.get('doi', '')
                if oa_id:
                    future = executor.submit(self.get_citing_dois, oa_id)
                    futures[future] = doi
            
            total = len(futures)
            processed = 0
            
            for future in as_completed(futures):
                doi = futures[future]
                try:
                    citing_map[doi] = future.result()
                except Exception as e:
                    if SHOW_DEBUG_LOGS:
                        print(f"⚠️ Ошибка получения цитирований для {doi}: {e}")
                    citing_map[doi] = []
                
                processed += 1
                if progress_callback:
                    progress_callback(processed, total)
        
        return citing_map
    
    def get_work_details(self, oa_id: str) -> Optional[Dict]:
        """Получает детальную информацию о работе по OpenAlex ID"""
        url = f"https://api.openalex.org/works/{oa_id}"
        data = self.smart_get(url, {})
        return data

# ============================================
# ОБРАБОТЧИК ДАННЫХ
# ============================================

class JournalDataProcessor:
    """Обработчик данных для анализа журнала"""
    
    def __init__(self, articles: List[Dict], citing_map: Dict[str, List[str]]):
        self.articles = articles
        self.citing_map = citing_map
        self.processed_articles = []
        self.metrics = {}
        self.topics_data = {}
        self.citation_dynamics = {}
        self.cumulative_citations = {}
        self.citation_heatmap = {}
        self.most_cited = []
        self.citing_works_stats = {}
        self.detailed_citations = {}
        self.author_analysis = []
        self.top_affiliations = []
        self.geographic_data = {}
        self.all_publications_data = []
        
    def process(self) -> Dict:
        """Полный процесс обработки данных"""
        self._parse_articles()
        self._calculate_metrics()
        self._analyze_authors()
        self._analyze_affiliations()
        self._analyze_geographic()
        self._analyze_citations()
        self._analyze_citing_works()
        self._analyze_topics()
        self._prepare_detailed_citations()
        self._prepare_all_publications()
        
        return {
            'articles': self.processed_articles,
            'metrics': self.metrics,
            'topics_data': self.topics_data,
            'citation_dynamics': self.citation_dynamics,
            'cumulative_citations': self.cumulative_citations,
            'citation_heatmap': self.citation_heatmap,
            'most_cited': self.most_cited,
            'citing_works_stats': self.citing_works_stats,
            'detailed_citations': self.detailed_citations,
            'author_analysis': self.author_analysis,
            'top_affiliations': self.top_affiliations,
            'geographic_data': self.geographic_data,
            'all_publications_data': self.all_publications_data
        }
    
    def _parse_articles(self):
        """Парсит сырые данные в структурированные объекты"""
        for article_data in self.articles:
            raw = article_data.get('raw_data', {})
            
            # Парсим авторов
            authors = []
            affiliations = []
            countries = []
            
            for authorship in raw.get('authorships', []):
                author_data = authorship.get('author', {})
                author = Author(
                    display_name=author_data.get('display_name', 'Unknown'),
                    orcid=author_data.get('orcid', '').replace('https://orcid.org/', '') if author_data.get('orcid') else None
                )
                
                # Аффилиации автора
                for inst in authorship.get('institutions', []):
                    affil_name = inst.get('display_name', '')
                    if affil_name:
                        affiliations.append(affil_name)
                        author.affiliations.append(affil_name)
                        country = extract_country_from_affiliation(affil_name)
                        if country and country != 'Unknown':
                            countries.append(country)
                            author.countries.append(country)
                
                authors.append(author)
            
            # Парсим темы
            topics = []
            for topic in raw.get('topics', []):
                topics.append(Topic(
                    display_name=topic.get('display_name', ''),
                    subfield=topic.get('subfield', {}).get('display_name', ''),
                    field=topic.get('field', {}).get('display_name', ''),
                    domain=topic.get('domain', {}).get('display_name', ''),
                    score=topic.get('score', 0.0)
                ))
            
            # Парсим концепты
            concepts = []
            for concept in raw.get('concepts', []):
                concepts.append(Concept(
                    display_name=concept.get('display_name', ''),
                    level=concept.get('level', 0),
                    score=concept.get('score', 0.0)
                ))
            
            # Поля и домены из концептов
            fields = []
            domains = []
            for concept in concepts:
                if concept.level == 2:
                    fields.append(concept.display_name)
                elif concept.level == 3:
                    domains.append(concept.display_name)
            
            # Open Access
            oa_data = raw.get('open_access', {})
            is_oa = oa_data.get('is_oa', False)
            oa_status = oa_data.get('oa_status', 'unknown')
            
            # Информация о журнале
            primary_location = raw.get('primary_location', {})
            source = primary_location.get('source', {})
            journal_name = source.get('display_name', 'Unknown')
            publisher = source.get('host_organization_name') or source.get('publisher', 'Unknown')
            
            article = Article(
                id=raw.get('id', ''),
                doi=article_data.get('doi', ''),
                title=article_data.get('title', 'No title'),
                publication_year=article_data.get('publication_year', 0),
                cited_by_count=article_data.get('cited_by_count', 0),
                journal_name=journal_name,
                publisher=publisher,
                is_oa=is_oa,
                oa_status=oa_status,
                authors=authors,
                affiliations=list(set(affiliations)),
                countries=list(set(countries)),
                topics=topics,
                concepts=concepts,
                fields=list(set(fields)),
                domains=list(set(domains))
            )
            
            # Добавляем цитирования
            doi = article_data.get('doi')
            if doi in self.citing_map:
                citing_dois = self.citing_map[doi]
                # Здесь будут загружены детальные цитирования позже
                # Пока сохраняем только список DOI
                article.citations = []  # Будет заполнено позже
            
            # Цитирования в год
            if article.publication_year:
                current_year = datetime.now().year
                years_since = current_year - article.publication_year + 1
                article.citations_per_year = article.cited_by_count / max(years_since, 1)
            
            self.processed_articles.append(article)
    
    def _calculate_metrics(self):
        """Вычисляет все метрики"""
        articles = self.processed_articles
        n = len(articles)
        
        if n == 0:
            self.metrics = {
                'total_publications': 0,
                'total_citations': 0,
                'avg_citations': 0,
                'median_citations': 0,
                'max_citations': 0,
                'h_index': 0,
                'g_index': 0,
                'i10_index': 0,
                'i100_index': 0,
                'oa_percentage': 0,
                'active_years': 0,
                'papers_per_year': 0,
                'unique_authors': 0,
                'unique_affiliations': 0,
                'unique_countries': 0,
                'avg_authors_per_paper': 0,
                'avg_affiliations_per_paper': 0,
                'avg_countries_per_paper': 0,
                'international_collaboration_rate': 0,
                'oa_breakdown': {'gold': 0, 'hybrid': 0, 'green': 0, 'bronze': 0, 'closed': 0, 'unknown': 0}
            }
            return
        
        # Цитирования
        citations = [a.cited_by_count for a in articles]
        total_citations = sum(citations)
        avg_citations = total_citations / n if n > 0 else 0
        median_citations = np.median(citations) if citations else 0
        max_citations = max(citations) if citations else 0
        
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
        
        # i10 и i100
        i10_index = sum(1 for c in citations if c >= 10)
        i100_index = sum(1 for c in citations if c >= 100)
        
        # Open Access
        oa_articles = [a for a in articles if a.is_oa]
        oa_percentage = (len(oa_articles) / n * 100) if n > 0 else 0
        
        # OA Breakdown
        oa_breakdown = {'gold': 0, 'hybrid': 0, 'green': 0, 'bronze': 0, 'closed': 0, 'unknown': 0}
        for a in articles:
            status = a.oa_status if a.oa_status in oa_breakdown else 'unknown'
            oa_breakdown[status] += 1
        
        # Годы
        years = [a.publication_year for a in articles if a.publication_year]
        active_years = len(set(years)) if years else 0
        papers_per_year = n / active_years if active_years > 0 else 0
        
        # Авторы
        all_authors = []
        all_affiliations = []
        all_countries = []
        total_authors = 0
        
        for a in articles:
            all_authors.extend([author.display_name for author in a.authors])
            all_affiliations.extend(a.affiliations)
            all_countries.extend(a.countries)
            total_authors += len(a.authors)
        
        unique_authors = len(set(all_authors))
        unique_affiliations = len(set(all_affiliations))
        unique_countries = len(set(all_countries))
        
        avg_authors_per_paper = total_authors / n if n > 0 else 0
        avg_affiliations_per_paper = len(all_affiliations) / n if n > 0 else 0
        avg_countries_per_paper = len(all_countries) / n if n > 0 else 0
        
        # International collaboration rate
        international_papers = 0
        for a in articles:
            if len(set(a.countries)) > 1:
                international_papers += 1
        international_collaboration_rate = (international_papers / n * 100) if n > 0 else 0
        
        self.metrics = {
            'total_publications': n,
            'total_citations': total_citations,
            'avg_citations': avg_citations,
            'median_citations': median_citations,
            'max_citations': max_citations,
            'h_index': h_index,
            'g_index': g_index,
            'i10_index': i10_index,
            'i100_index': i100_index,
            'oa_percentage': oa_percentage,
            'active_years': active_years,
            'papers_per_year': papers_per_year,
            'unique_authors': unique_authors,
            'unique_affiliations': unique_affiliations,
            'unique_countries': unique_countries,
            'avg_authors_per_paper': avg_authors_per_paper,
            'avg_affiliations_per_paper': avg_affiliations_per_paper,
            'avg_countries_per_paper': avg_countries_per_paper,
            'international_collaboration_rate': international_collaboration_rate,
            'oa_breakdown': oa_breakdown
        }
    
    def _analyze_authors(self):
        """Анализирует авторов"""
        author_stats = defaultdict(lambda: {
            'name': '',
            'orcid': None,
            'affiliations': set(),
            'countries': set(),
            'publications': 0,
            'citations': 0
        })
        
        for article in self.processed_articles:
            for author in article.authors:
                if author.display_name not in author_stats:
                    author_stats[author.display_name]['name'] = author.display_name
                    author_stats[author.display_name]['orcid'] = author.orcid
                
                author_stats[author.display_name]['affiliations'].update(author.affiliations)
                author_stats[author.display_name]['countries'].update(author.countries)
                author_stats[author.display_name]['publications'] += 1
                author_stats[author.display_name]['citations'] += article.cited_by_count
        
        # Сортируем по цитированиям
        sorted_authors = sorted(
            author_stats.values(),
            key=lambda x: x['citations'],
            reverse=True
        )
        
        self.author_analysis = sorted_authors
    
    def _analyze_affiliations(self):
        """Анализирует аффилиации"""
        affil_stats = defaultdict(lambda: {
            'name': '',
            'country': None,
            'publications': 0,
            'citations': 0,
            'authors': set()
        })
        
        for article in self.processed_articles:
            for affil in article.affiliations:
                if affil not in affil_stats:
                    affil_stats[affil]['name'] = affil
                    affil_stats[affil]['country'] = extract_country_from_affiliation(affil)
                
                affil_stats[affil]['publications'] += 1
                affil_stats[affil]['citations'] += article.cited_by_count
                for author in article.authors:
                    if affil in author.affiliations:
                        affil_stats[affil]['authors'].add(author.display_name)
        
        # Сортируем по публикациям
        sorted_affils = sorted(
            affil_stats.values(),
            key=lambda x: x['publications'],
            reverse=True
        )
        
        self.top_affiliations = sorted_affils[:20]
    
    def _analyze_geographic(self):
        """Географический анализ"""
        # 5.3.1 Unique Countries per Publication
        unique_countries_per_pub = []
        for article in self.processed_articles:
            unique_countries_per_pub.append({
                'doi': article.doi,
                'title': article.title,
                'year': article.publication_year,
                'countries': list(set(article.countries)),
                'count': len(set(article.countries))
            })
        
        # 5.3.2 Authors per Country (Individual Distribution)
        authors_per_country = defaultdict(int)
        for article in self.processed_articles:
            for author in article.authors:
                for country in set(author.countries):
                    authors_per_country[country] += 1
        
        # 5.3.3 Collaboration Patterns
        single_country = 0
        international = 0
        for article in self.processed_articles:
            if len(set(article.countries)) <= 1:
                single_country += 1
            else:
                international += 1
        
        # 5.3.4 Collaboration Couples
        country_pairs = defaultdict(int)
        for article in self.processed_articles:
            countries = list(set(article.countries))
            if len(countries) >= 2:
                for i in range(len(countries)):
                    for j in range(i+1, len(countries)):
                        pair = tuple(sorted([countries[i], countries[j]]))
                        country_pairs[pair] += 1
        
        sorted_pairs = sorted(country_pairs.items(), key=lambda x: x[1], reverse=True)
        
        self.geographic_data = {
            'unique_countries_per_pub': unique_countries_per_pub,
            'authors_per_country': dict(authors_per_country),
            'collaboration_patterns': {
                'single_country': single_country,
                'international': international,
                'total': len(self.processed_articles)
            },
            'collaboration_couples': sorted_pairs[:20]
        }
    
    def _analyze_citations(self):
        """Цитатный анализ"""
        # 6.1 Citation Dynamics by Year
        dynamics = defaultdict(lambda: defaultdict(int))
        all_years = sorted(set([a.publication_year for a in self.processed_articles if a.publication_year]))
        citing_years = set()
        
        # Загружаем детальные цитирования для динамики
        for article in self.processed_articles:
            if article.doi in self.citing_map:
                citing_dois = self.citing_map[article.doi]
                # Здесь нужно получить годы цитирований
                # В реальном коде здесь будет запрос к API для получения годов
                # Пока используем заглушку
                for citing_doi in citing_dois[:10]:  # Ограничиваем для примера
                    citing_year = article.publication_year + 1  # Заглушка
                    dynamics[article.publication_year][citing_year] += 1
                    citing_years.add(citing_year)
        
        self.citation_dynamics = dict(dynamics)
        
        # 6.2 Cumulative Citations
        cumulative = defaultdict(int)
        for pub_year, years_data in dynamics.items():
            for cite_year, count in years_data.items():
                for y in range(pub_year, cite_year + 1):
                    cumulative[y] += count
        
        self.cumulative_citations = dict(cumulative)
        
        # 6.3 Citation Network Heatmap
        all_cite_years = sorted(citing_years)
        heatmap_data = []
        for pub_year in sorted(all_years):
            row = []
            for cite_year in all_cite_years:
                row.append(dynamics.get(pub_year, {}).get(cite_year, 0))
            heatmap_data.append(row)
        
        self.citation_heatmap = {
            'publication_years': sorted(all_years),
            'citation_years': all_cite_years,
            'data': heatmap_data
        }
        
        # 6.4 Most Cited Publications
        sorted_articles = sorted(
            self.processed_articles,
            key=lambda x: x.cited_by_count,
            reverse=True
        )
        
        self.most_cited = []
        for i, article in enumerate(sorted_articles[:15], 1):
            author_names = [a.display_name for a in article.authors[:3]]
            author_str = ', '.join(author_names)
            if len(article.authors) > 3:
                author_str += f' +{len(article.authors)-3} more'
            
            self.most_cited.append({
                'rank': i,
                'title': article.title,
                'year': article.publication_year,
                'citations': article.cited_by_count,
                'citations_per_year': article.citations_per_year,
                'authors': author_str,
                'doi': article.doi
            })
    
    def _analyze_citing_works(self):
        """Анализ цитирующих работ"""
        # Собираем все цитирующие работы
        all_citing_dois = []
        for doi, citing_list in self.citing_map.items():
            all_citing_dois.extend(citing_list)
        
        total_citing = len(all_citing_dois)
        unique_citing = len(set(all_citing_dois))
        
        # Статистика будет заполнена при загрузке детальных данных
        self.citing_works_stats = {
            'total_citing_works': total_citing,
            'unique_citing_authors': 0,  # Будет заполнено позже
            'unique_citing_affiliations': 0,
            'unique_citing_countries': 0,
            'unique_citing_journals': 0,
            'unique_citing_publishers': 0,
            'top_citing_authors': [],
            'top_citing_affiliations': [],
            'top_citing_countries': [],
            'top_citing_journals': [],
            'top_citing_publishers': []
        }
    
    def _analyze_topics(self):
        """Тематический анализ"""
        # 8.1 Topics Table
        topics_stats = defaultdict(lambda: {
            'analyzed_count': 0,
            'citing_count': 0,
            'analyzed_norm_count': 0,
            'citing_norm_count': 0,
            'total_norm_count': 0,
            'first_year': 9999,
            'peak_year': 0,
            'peak_citations': 0
        })
        
        for article in self.processed_articles:
            for topic in article.topics:
                if topic.display_name:
                    topics_stats[topic.display_name]['analyzed_count'] += 1
                    topics_stats[topic.display_name]['citing_count'] += article.cited_by_count
                    if article.publication_year < topics_stats[topic.display_name]['first_year']:
                        topics_stats[topic.display_name]['first_year'] = article.publication_year
                    if article.cited_by_count > topics_stats[topic.display_name]['peak_citations']:
                        topics_stats[topic.display_name]['peak_citations'] = article.cited_by_count
                        topics_stats[topic.display_name]['peak_year'] = article.publication_year
        
        # Нормализация
        total_articles = len(self.processed_articles)
        total_citations = sum([a.cited_by_count for a in self.processed_articles])
        
        for topic, stats in topics_stats.items():
            stats['analyzed_norm_count'] = stats['analyzed_count'] / total_articles if total_articles > 0 else 0
            stats['citing_norm_count'] = stats['citing_count'] / total_citations if total_citations > 0 else 0
            stats['total_norm_count'] = (stats['analyzed_norm_count'] + stats['citing_norm_count']) / 2
        
        # 8.2 Top-10
        top_topics = sorted(
            topics_stats.items(),
            key=lambda x: x[1]['citing_count'],
            reverse=True
        )[:10]
        
        # Собираем топы для Subtopics, Fields, Domains, Concepts
        subtopics_stats = defaultdict(int)
        fields_stats = defaultdict(int)
        domains_stats = defaultdict(int)
        concepts_stats = defaultdict(int)
        
        for article in self.processed_articles:
            for topic in article.topics:
                if topic.subfield:
                    subtopics_stats[topic.subfield] += article.cited_by_count
                if topic.field:
                    fields_stats[topic.field] += article.cited_by_count
                if topic.domain:
                    domains_stats[topic.domain] += article.cited_by_count
            
            for concept in article.concepts:
                concepts_stats[concept.display_name] += article.cited_by_count
        
        self.topics_data = {
            'topics_table': topics_stats,
            'top_topics': top_topics,
            'top_subtopics': sorted(subtopics_stats.items(), key=lambda x: x[1], reverse=True)[:10],
            'top_fields': sorted(fields_stats.items(), key=lambda x: x[1], reverse=True)[:10],
            'top_domains': sorted(domains_stats.items(), key=lambda x: x[1], reverse=True)[:10],
            'top_concepts': sorted(concepts_stats.items(), key=lambda x: x[1], reverse=True)[:10]
        }
    
    def _prepare_detailed_citations(self):
        """Подготавливает детальные цитирования для каждой статьи"""
        # В реальном коде здесь будет загрузка деталей цитирующих работ
        # Пока создаем структуру
        self.detailed_citations = {}
        
        for article in self.processed_articles:
            if article.doi in self.citing_map:
                citing_dois = self.citing_map[article.doi]
                if citing_dois:
                    self.detailed_citations[article.doi] = {
                        'title': article.title,
                        'year': article.publication_year,
                        'doi': article.doi,
                        'total_citations': len(citing_dois),
                        'citations': citing_dois[:10]  # Пока только список DOI
                    }
    
    def _prepare_all_publications(self):
        """Подготавливает данные для таблицы всех публикаций"""
        self.all_publications_data = []
        for i, article in enumerate(self.processed_articles, 1):
            author_names = [a.display_name for a in article.authors]
            self.all_publications_data.append({
                'rank': i,
                'title': article.title,
                'year': article.publication_year,
                'authors': ', '.join(author_names[:5]) + (' +' + str(len(author_names)-5) + ' more' if len(author_names) > 5 else ''),
                'affiliations': ', '.join(article.affiliations[:3]) + (' +' + str(len(article.affiliations)-3) + ' more' if len(article.affiliations) > 3 else ''),
                'citations': article.cited_by_count,
                'citations_per_year': article.citations_per_year,
                'doi': article.doi,
                'journal': article.journal_name
            })

# ============================================
# ГЕНЕРАТОР HTML ОТЧЕТА ДЛЯ ЖУРНАЛОВ
# ============================================

def generate_journal_html_report(
    data: Dict,
    issn: str,
    period_str: str,
    journal_logo_base64: Optional[str] = None,
    app_logo_base64: Optional[str] = None,
    theme_colors: Optional[Dict] = None,
    lang: str = 'en'
) -> str:
    """Генерирует HTML отчет для журнала"""
    
    if theme_colors is None:
        theme_colors = {
            'primary': '#667eea',
            'secondary': '#f39c12'
        }
    
    primary = theme_colors.get('primary', '#667eea')
    secondary = theme_colors.get('secondary', '#f39c12')
    
    metrics = data.get('metrics', {})
    articles = data.get('articles', [])
    topics_data = data.get('topics_data', {})
    citation_dynamics = data.get('citation_dynamics', {})
    cumulative_citations = data.get('cumulative_citations', {})
    citation_heatmap = data.get('citation_heatmap', {})
    most_cited = data.get('most_cited', [])
    citing_works_stats = data.get('citing_works_stats', {})
    detailed_citations = data.get('detailed_citations', {})
    author_analysis = data.get('author_analysis', [])
    top_affiliations = data.get('top_affiliations', [])
    geographic_data = data.get('geographic_data', {})
    all_publications_data = data.get('all_publications_data', [])
    
    def t(key: str, **kwargs) -> str:
        return translate(key, lang, **kwargs)
    
    # Генерируем таблицу Author Analysis
    author_rows = ""
    for i, author in enumerate(author_analysis[:20], 1):
        author_rows += f"""
        <tr>
            <td>{i}</td>
            <td>{html.escape(author['name'])}</td>
            <td>{author.get('orcid', 'N/A')}</td>
            <td>{', '.join(list(author['affiliations'])[:3])}</td>
            <td>{', '.join(list(author['countries'])[:3])}</td>
            <td>{author['publications']}</td>
            <td>{author['citations']}</td>
        </tr>
        """
    
    # Генерируем таблицу Top Affiliations
    affil_rows = ""
    for i, affil in enumerate(top_affiliations[:15], 1):
        affil_rows += f"""
        <tr>
            <td>{i}</td>
            <td>{html.escape(affil['name'])}</td>
            <td>{affil.get('country', 'N/A')}</td>
            <td>{len(affil['authors'])}</td>
            <td>{affil['publications']}</td>
            <td>{affil['citations']}</td>
        </tr>
        """
    
    # Генерируем таблицу Geographic Analysis - Unique Countries per Publication
    geo_rows = ""
    for item in geographic_data.get('unique_countries_per_pub', [])[:20]:
        geo_rows += f"""
        <tr>
            <td>{html.escape(item['title'][:60])}...</td>
            <td>{item['year']}</td>
            <td>{item['count']}</td>
            <td>{', '.join(item['countries'])}</td>
            <td><a href="https://doi.org/{item['doi']}" target="_blank">{item['doi']}</a></td>
        </tr>
        """
    
    # Authors per Country
    authors_per_country_rows = ""
    for country, count in sorted(geographic_data.get('authors_per_country', {}).items(), key=lambda x: x[1], reverse=True)[:15]:
        authors_per_country_rows += f"""
        <tr>
            <td>{country}</td>
            <td>{count}</td>
        </tr>
        """
    
    # Collaboration Patterns
    collab = geographic_data.get('collaboration_patterns', {})
    total = collab.get('total', 0)
    single = collab.get('single_country', 0)
    inter = collab.get('international', 0)
    single_pct = (single / total * 100) if total > 0 else 0
    inter_pct = (inter / total * 100) if total > 0 else 0
    
    # Collaboration Couples
    couples_rows = ""
    for (country1, country2), count in geographic_data.get('collaboration_couples', [])[:20]:
        couples_rows += f"""
        <tr>
            <td>{country1}</td>
            <td>{country2}</td>
            <td>{count}</td>
        </tr>
        """
    
    # Citation Dynamics by Year
    dynamics_rows = ""
    for pub_year, years_data in sorted(citation_dynamics.items()):
        for cite_year, count in sorted(years_data.items()):
            dynamics_rows += f"""
            <tr>
                <td>{pub_year}</td>
                <td>{cite_year}</td>
                <td>{count}</td>
            </tr>
            """
    
    # Cumulative Citations
    cumul_rows = ""
    for year, count in sorted(cumulative_citations.items()):
        cumul_rows += f"""
        <tr>
            <td>{year}</td>
            <td>{count}</td>
        </tr>
        """
    
    # Citation Network Heatmap
    heatmap_years = citation_heatmap.get('publication_years', [])
    cite_years = citation_heatmap.get('citation_years', [])
    heatmap_data = citation_heatmap.get('data', [])
    
    heatmap_rows = ""
    for i, pub_year in enumerate(heatmap_years):
        heatmap_rows += "<tr>"
        heatmap_rows += f"<td><strong>{pub_year}</strong></td>"
        if i < len(heatmap_data):
            row = heatmap_data[i]
            for j, cite_year in enumerate(cite_years):
                val = row[j] if j < len(row) else 0
                # Определяем цвет ячейки на основе значения
                if val == 0:
                    bg_color = "#f5f5f5"
                    text_color = "#999"
                else:
                    # Градиент от primary к secondary
                    max_val = max([max(row) for row in heatmap_data if row]) if heatmap_data else 1
                    intensity = min(val / max_val, 1.0) if max_val > 0 else 0
                    # Смешиваем primary и secondary
                    rgb1 = hex_to_rgb(primary)
                    rgb2 = hex_to_rgb(secondary)
                    r = int(rgb1[0] + (rgb2[0] - rgb1[0]) * intensity)
                    g = int(rgb1[1] + (rgb2[1] - rgb1[1]) * intensity)
                    b = int(rgb1[2] + (rgb2[2] - rgb1[2]) * intensity)
                    bg_color = f"rgb({r},{g},{b})"
                    text_color = "white" if intensity > 0.5 else "black"
                heatmap_rows += f'<td style="background-color:{bg_color}; color:{text_color}; text-align:center;">{val if val > 0 else "-"}</td>'
        heatmap_rows += "</tr>"
    
    # Most Cited Publications
    most_cited_rows = ""
    for item in most_cited[:15]:
        most_cited_rows += f"""
        <tr>
            <td>{item['rank']}</td>
            <td>{html.escape(item['title'])}</td>
            <td>{item['year']}</td>
            <td><span class="citation-count">{item['citations']}</span></td>
            <td>{item['citations_per_year']:.1f}</td>
            <td>{html.escape(item['authors'])}</td>
            <td><a href="https://doi.org/{item['doi']}" target="_blank" class="doi-link">{item['doi']}</a></td>
        </tr>
        """
    
    # Citing Works Statistics
    citing_stats_rows = f"""
    <tr><td>{t('total_citing_works')}</td><td><strong>{citing_works_stats.get('total_citing_works', 0)}</strong></td></tr>
    <tr><td>{t('unique_citing_authors')}</td><td><strong>{citing_works_stats.get('unique_citing_authors', 0)}</strong></td></tr>
    <tr><td>{t('unique_citing_affiliations')}</td><td><strong>{citing_works_stats.get('unique_citing_affiliations', 0)}</strong></td></tr>
    <tr><td>{t('unique_citing_countries')}</td><td><strong>{citing_works_stats.get('unique_citing_countries', 0)}</strong></td></tr>
    <tr><td>{t('unique_citing_journals')}</td><td><strong>{citing_works_stats.get('unique_citing_journals', 0)}</strong></td></tr>
    <tr><td>{t('unique_citing_publishers')}</td><td><strong>{citing_works_stats.get('unique_citing_publishers', 0)}</strong></td></tr>
    """
    
    # Top Citing Authors
    top_citing_rows = ""
    for author in citing_works_stats.get('top_citing_authors', [])[:15]:
        top_citing_rows += f"""
        <tr>
            <td>{author.get('rank', 0)}</td>
            <td>{html.escape(author.get('name', 'Unknown'))}</td>
            <td>{author.get('count', 0)}</td>
        </tr>
        """
    
    # Topics Table
    topics_rows = ""
    for topic, stats in sorted(topics_data.get('topics_table', {}).items(), key=lambda x: x[1]['citing_count'], reverse=True)[:20]:
        topics_rows += f"""
        <tr>
            <td>{html.escape(topic)}</td>
            <td>{stats['analyzed_count']}</td>
            <td>{stats['citing_count']}</td>
            <td>{stats['analyzed_norm_count']:.3f}</td>
            <td>{stats['citing_norm_count']:.3f}</td>
            <td>{stats['total_norm_count']:.3f}</td>
            <td>{stats['first_year']}</td>
            <td>{stats['peak_year']}</td>
        </tr>
        """
    
    # Top Cited Topics, Subtopics, Fields, Domains, Concepts
    top_topics_rows = ""
    for topic, count in topics_data.get('top_topics', []):
        top_topics_rows += f"""
        <tr>
            <td>{html.escape(topic)}</td>
            <td>{count}</td>
        </tr>
        """
    
    top_subtopics_rows = ""
    for subtopic, count in topics_data.get('top_subtopics', []):
        top_subtopics_rows += f"""
        <tr>
            <td>{html.escape(subtopic)}</td>
            <td>{count}</td>
        </tr>
        """
    
    top_fields_rows = ""
    for field, count in topics_data.get('top_fields', []):
        top_fields_rows += f"""
        <tr>
            <td>{html.escape(field)}</td>
            <td>{count}</td>
        </tr>
        """
    
    top_domains_rows = ""
    for domain, count in topics_data.get('top_domains', []):
        top_domains_rows += f"""
        <tr>
            <td>{html.escape(domain)}</td>
            <td>{count}</td>
        </tr>
        """
    
    top_concepts_rows = ""
    for concept, count in topics_data.get('top_concepts', []):
        top_concepts_rows += f"""
        <tr>
            <td>{html.escape(concept)}</td>
            <td>{count}</td>
        </tr>
        """
    
    # Detailed Citations
    detailed_citations_html = ""
    for doi, data in detailed_citations.items():
        pub_id = doi.replace('/', '_')
        citations_html = ""
        for cite in data.get('citations', [])[:10]:
            if isinstance(cite, str):
                # Если это просто строка DOI
                citations_html += f"""
                <div class="citation-detail">
                    <div><strong>Citing work:</strong> <a href="https://doi.org/{cite}" target="_blank">{cite}</a></div>
                </div>
                """
            else:
                # Если это структурированные данные
                citations_html += f"""
                <div class="citation-detail">
                    <div><strong>{html.escape(cite.get('citing_title', 'No title'))}</strong></div>
                    <div class="cite-meta">
                        <strong>{t('citing_journal')}:</strong> {html.escape(cite.get('citing_journal', 'Unknown'))} | 
                        <strong>{t('citing_year')}:</strong> {cite.get('citing_year', 'N/A')} | 
                        <strong>{t('citation_lag')}:</strong> {cite.get('citation_lag', 0)} years
                    </div>
                    <div class="cite-meta">
                        <a href="https://doi.org/{cite.get('citing_doi', '')}" target="_blank" class="doi-link">DOI: {cite.get('citing_doi', '')}</a>
                    </div>
                </div>
                """
        
        if citations_html:
            detailed_citations_html += f"""
            <div class="collapser" onclick="toggleCitations('{pub_id}')">
                <strong>{html.escape(data['title'][:80])}...</strong>
                <span class="badge badge-info">{data['year']}</span>
                <span class="citation-count">{data['total_citations']} {t('citations')}</span>
                <span style="font-size: 12px; color: #666; margin-left: 10px;">DOI: {data['doi']}</span>
                <span style="float: right; font-size: 12px; color: #666;">{t('click_to_toggle')}</span>
            </div>
            <div id="citations_{pub_id}" style="display: none;">
                {citations_html}
            </div>
            """
    
    # All Publications
    all_pubs_rows = ""
    for item in all_publications_data[:50]:
        all_pubs_rows += f"""
        <tr data-year="{item['year']}" data-authors="{item['authors'].lower()}" data-citations="{item['citations']}" data-title="{item['title'].lower()}" data-doi="{item['doi'].lower()}" data-affiliations="{item['affiliations'].lower()}">
            <td>{item['rank']}</td>
            <td class="word-wrap">{html.escape(item['title'])}</td>
            <td>{item['year']}</td>
            <td>{html.escape(item['authors'])}</td>
            <td>{html.escape(item['affiliations'])}</td>
            <td><span class="citation-count">{item['citations']}</span></td>
            <td>{item['citations_per_year']:.1f}</td>
            <td><a href="https://doi.org/{item['doi']}" target="_blank" class="doi-link">{item['doi']}</a></td>
        </tr>
        """
    
    # Year filter options
    years_options = sorted(set([a.publication_year for a in articles if a.publication_year]), reverse=True)
    year_options_html = '<option value="">All Years</option>'
    for year in years_options:
        year_options_html += f'<option value="{year}">{year}</option>'
    
    # Open Access Breakdown
    oa_breakdown = metrics.get('oa_breakdown', {})
    oa_rows = ""
    for status in ['gold', 'hybrid', 'green', 'bronze', 'closed', 'unknown']:
        count = oa_breakdown.get(status, 0)
        if count > 0:
            pct = (count / metrics.get('total_publications', 1) * 100) if metrics.get('total_publications', 0) > 0 else 0
            oa_rows += f"""
            <tr>
                <td>{t(status)}</td>
                <td>{count}</td>
                <td>{pct:.1f}%</td>
            </tr>
            """
    
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
                padding: 25px 18px;
                overflow-y: auto;
                z-index: 1000;
            }}
            .sidebar h3 {{
                margin-bottom: 15px;
                font-size: 18px;
                font-weight: 600;
                color: white;
                border-bottom: 1px solid rgba(255,255,255,0.2);
                padding-bottom: 10px;
            }}
            .sidebar a {{
                color: white;
                text-decoration: none;
                display: flex;
                align-items: center;
                gap: 10px;
                padding: 8px 12px;
                margin: 3px 0;
                border-radius: 6px;
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
            .sidebar .level2-icon {{
                font-size: 12px;
            }}
            .main-content {{
                margin-left: 280px;
                padding: 30px 40px;
            }}
            .header {{
                background: linear-gradient(135deg, {primary} 0%, {secondary} 100%);
                color: white;
                padding: 35px;
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
                margin-top: 8px;
                font-size: 14px;
            }}
            .header-logo {{
                max-height: 150px;
                max-width: 300px;
                margin-bottom: 15px;
            }}
            .header-logo-app {{
                max-height: 120px;
                max-width: 360px;
                margin-bottom: 10px;
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
            .subsection-title {{
                font-size: 18px;
                font-weight: 600;
                margin: 20px 0 15px 0;
                padding-bottom: 8px;
                border-bottom: 2px solid {secondary};
                color: {primary};
            }}
            .metrics-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
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
                position: sticky;
                top: 0;
                z-index: 10;
            }}
            td {{
                padding: 8px 12px;
                border-bottom: 1px solid #e0e0e0;
            }}
            tr:hover {{
                background-color: #f5f5f5;
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
            .citation-count {{
                font-weight: bold;
                color: {primary};
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
            .collapser {{
                background: #f8f9fa;
                padding: 12px 15px;
                margin: 8px 0;
                border-radius: 8px;
                cursor: pointer;
                border-left: 4px solid {primary};
                transition: background 0.3s;
            }}
            .collapser:hover {{
                background: #e9ecef;
            }}
            .collapser .citation-count {{
                float: right;
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
                margin-top: 4px;
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
                gap: 6px;
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
                border-radius: 4px;
                font-size: 13px;
                font-family: 'Times New Roman', serif;
            }}
            .filter-row input[type="text"] {{
                min-width: 120px;
            }}
            .filter-row input[type="number"] {{
                width: 80px;
            }}
            .word-wrap {{
                word-wrap: break-word;
                max-width: 300px;
            }}
            .table-container {{
                overflow-x: auto;
                max-height: 600px;
                overflow-y: auto;
            }}
            .table-container table {{
                font-size: 13px;
            }}
            .table-container th {{
                position: sticky;
                top: 0;
                z-index: 10;
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
            #visibleCount {{
                font-weight: 500;
                font-size: 14px;
                color: #555;
            }}
            .status-badge {{
                display: inline-block;
                padding: 2px 8px;
                border-radius: 10px;
                font-size: 10px;
                font-weight: 600;
            }}
            .status-badge.gold {{ background: #ffd700; color: #333; }}
            .status-badge.hybrid {{ background: #ff8c00; color: white; }}
            .status-badge.green {{ background: #2ecc71; color: white; }}
            .status-badge.bronze {{ background: #cd7f32; color: white; }}
            .status-badge.closed {{ background: #95a5a6; color: white; }}
            .status-badge.unknown {{ background: #bdc3c7; color: #333; }}
            .status-badge.diamond {{ background: #00bcd4; color: white; }}
            @media (max-width: 768px) {{
                .sidebar {{ display: none; }}
                .main-content {{ margin-left: 0; padding: 15px; }}
                .filter-row {{
                    flex-direction: column;
                    align-items: stretch;
                }}
                .filter-row > div {{
                    flex-wrap: wrap;
                }}
                .metrics-grid {{
                    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
                }}
            }}
            @media print {{
                .sidebar {{ display: none; }}
                .main-content {{ margin-left: 0; }}
                .section {{ page-break-inside: avoid; }}
            }}
        </style>
        <script>
            function toggleCitations(id) {{
                var elem = document.getElementById('citations_' + id);
                if (elem) {{
                    if (elem.style.display === 'none') {{
                        elem.style.display = 'block';
                    }} else {{
                        elem.style.display = 'none';
                    }}
                }}
            }}
            
            function filterPublications() {{
                var yearFilter = document.getElementById('yearFilter');
                var authorFilter = document.getElementById('authorFilter');
                var citationFilter = document.getElementById('citationFilter');
                var searchInput = document.getElementById('searchInput');
                var affilFilter = document.getElementById('affilFilter');
                
                var yearVal = yearFilter ? yearFilter.value : '';
                var authorVal = authorFilter ? authorFilter.value.toLowerCase() : '';
                var citationVal = citationFilter ? parseInt(citationFilter.value) || 0 : 0;
                var searchVal = searchInput ? searchInput.value.toLowerCase() : '';
                var affilVal = affilFilter ? affilFilter.value.toLowerCase() : '';
                
                var rows = document.querySelectorAll('#publicationsTable tbody tr');
                var visible = 0;
                
                rows.forEach(function(row) {{
                    var year = row.getAttribute('data-year') || '';
                    var authors = row.getAttribute('data-authors') || '';
                    var citations = parseInt(row.getAttribute('data-citations')) || 0;
                    var title = row.getAttribute('data-title') || '';
                    var doi = row.getAttribute('data-doi') || '';
                    var affiliations = row.getAttribute('data-affiliations') || '';
                    
                    var show = true;
                    
                    if (yearVal && year !== yearVal) show = false;
                    if (authorVal && !authors.includes(authorVal)) show = false;
                    if (citationVal > 0 && citations < citationVal) show = false;
                    if (searchVal && !title.includes(searchVal) && !doi.includes(searchVal)) show = false;
                    if (affilVal && !affiliations.includes(affilVal)) show = false;
                    
                    if (show) {{
                        row.style.display = '';
                        visible++;
                    }} else {{
                        row.style.display = 'none';
                    }}
                }});
                
                var countSpan = document.getElementById('visibleCount');
                if (countSpan) {{
                    countSpan.textContent = 'Showing ' + visible + ' publications';
                }}
            }}
            
            function sortTable(column) {{
                var table = document.getElementById('publicationsTable');
                var tbody = table.querySelector('tbody');
                var rows = Array.from(tbody.querySelectorAll('tr'));
                var ascending = table.getAttribute('data-sort-' + column) === 'asc';
                
                rows.sort(function(a, b) {{
                    var aVal = a.cells[column].textContent.trim();
                    var bVal = b.cells[column].textContent.trim();
                    
                    var aNum = parseFloat(aVal);
                    var bNum = parseFloat(bVal);
                    if (!isNaN(aNum) && !isNaN(bNum)) {{
                        return ascending ? aNum - bNum : bNum - aNum;
                    }}
                    
                    return ascending ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
                }});
                
                rows.forEach(function(row) {{
                    tbody.appendChild(row);
                }});
                
                table.setAttribute('data-sort-' + column, ascending ? 'desc' : 'asc');
            }}
            
            document.addEventListener('DOMContentLoaded', function() {{
                filterPublications();
            }});
        </script>
    </head>
    <body>
        <div class="sidebar">
            <h3>📑 {t('app_title')}</h3>
            <a href="#overview"><span>📊 {t('overview')}</span></a>
            <a href="#analyzed_articles" class="level2"><span class="level2-icon">└─</span> {t('analyzed_articles')}</a>
            <a href="#author_analysis" class="level2"><span class="level2-icon">  └─</span> {t('author_analysis')}</a>
            <a href="#top_affiliations" class="level2"><span class="level2-icon">  └─</span> {t('top_affiliations')}</a>
            <a href="#geographic_analysis" class="level2"><span class="level2-icon">  └─</span> {t('geographic_analysis')}</a>
            <a href="#citation_analysis"><span>📈 {t('citation_analysis')}</span></a>
            <a href="#citing_works"><span>📚 {t('citing_works_analysis')}</span></a>
            <a href="#topics_analysis"><span>🏷️ {t('topics_analysis')}</span></a>
            <a href="#detailed_citations"><span>📋 {t('detailed_citations')}</span></a>
            <a href="#all_publications"><span>📄 {t('all_publications')}</span></a>
        </div>
        
        <div class="main-content">
            <div class="header">
                {f'<img src="data:image/png;base64,{app_logo_base64}" class="header-logo-app" alt="App Logo">' if app_logo_base64 else ''}
                {f'<img src="data:image/png;base64,{journal_logo_base64}" class="header-logo" alt="Journal Logo">' if journal_logo_base64 else ''}
                <h1>📊 {t('app_title')}</h1>
                <div class="subtitle">ISSN: {issn} | Period: {period_str}</div>
                <div class="date">{t('report_preview')}: {datetime.now().strftime('%d.%m.%Y')}</div>
            </div>
            
            <!-- Overview -->
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
                        <div class="metric-value">{metrics.get('oa_percentage', 0):.1f}%</div>
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
                </div>
                
                <div class="subsection-title">Open Access Breakdown</div>
                <table>
                    <thead>
                        <tr>
                            <th>Status</th>
                            <th>Count</th>
                            <th>Percentage</th>
                        </tr>
                    </thead>
                    <tbody>
                        {oa_rows}
                    </tbody>
                </table>
            </div>
            
            <!-- Analyzed Articles -->
            <div id="analyzed_articles" class="section">
                <div class="section-title"><span class="icon">📄</span> {t('analyzed_articles')}</div>
                
                <div id="author_analysis" class="subsection-title">Author Analysis</div>
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th onclick="sortTable(0)" style="cursor: pointer;">Rank</th>
                                <th onclick="sortTable(1)" style="cursor: pointer;">Authors</th>
                                <th onclick="sortTable(2)" style="cursor: pointer;">ORCID</th>
                                <th onclick="sortTable(3)" style="cursor: pointer;">Affiliations</th>
                                <th onclick="sortTable(4)" style="cursor: pointer;">Countries</th>
                                <th onclick="sortTable(5)" style="cursor: pointer;">Publications</th>
                                <th onclick="sortTable(6)" style="cursor: pointer;">Citations</th>
                            </tr>
                        </thead>
                        <tbody>
                            {author_rows}
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
                                <th>Rank</th>
                                <th>Affiliation</th>
                                <th>Country</th>
                                <th>Unique Authors</th>
                                <th>Publications</th>
                                <th>Citations</th>
                            </tr>
                        </thead>
                        <tbody>
                            {affil_rows}
                        </tbody>
                    </table>
                </div>
            </div>
            
            <!-- Geographic Analysis -->
            <div id="geographic_analysis" class="section">
                <div class="section-title"><span class="icon">🌍</span> {t('geographic_analysis')}</div>
                
                <div class="subsection-title">{t('unique_countries_per_publication')}</div>
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>Title</th>
                                <th>Year</th>
                                <th>Countries Count</th>
                                <th>Countries</th>
                                <th>DOI</th>
                            </tr>
                        </thead>
                        <tbody>
                            {geo_rows}
                        </tbody>
                    </table>
                </div>
                
                <div class="subsection-title">{t('authors_per_country')}</div>
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>Country</th>
                                <th>Authors Count</th>
                            </tr>
                        </thead>
                        <tbody>
                            {authors_per_country_rows}
                        </tbody>
                    </table>
                </div>
                
                <div class="subsection-title">{t('collaboration_patterns')}</div>
                <div style="display: flex; gap: 30px; flex-wrap: wrap; margin: 15px 0;">
                    <div style="background: #f8f9fa; padding: 15px 25px; border-radius: 8px; text-align: center; border-left: 4px solid {primary};">
                        <div style="font-size: 24px; font-weight: bold;">{single}</div>
                        <div style="font-size: 13px; color: #555;">{t('single_country')} ({single_pct:.1f}%)</div>
                    </div>
                    <div style="background: #f8f9fa; padding: 15px 25px; border-radius: 8px; text-align: center; border-left: 4px solid {secondary};">
                        <div style="font-size: 24px; font-weight: bold;">{inter}</div>
                        <div style="font-size: 13px; color: #555;">{t('international')} ({inter_pct:.1f}%)</div>
                    </div>
                    <div style="background: #f8f9fa; padding: 15px 25px; border-radius: 8px; text-align: center; border-left: 4px solid #95a5a6;">
                        <div style="font-size: 24px; font-weight: bold;">{total}</div>
                        <div style="font-size: 13px; color: #555;">Total Publications</div>
                    </div>
                </div>
                
                <div class="subsection-title">{t('collaboration_couples')}</div>
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>Country 1</th>
                                <th>Country 2</th>
                                <th>Collaborations</th>
                            </tr>
                        </thead>
                        <tbody>
                            {couples_rows}
                        </tbody>
                    </table>
                </div>
            </div>
            
            <!-- Citation Analysis -->
            <div id="citation_analysis" class="section">
                <div class="section-title"><span class="icon">📈</span> {t('citation_analysis')}</div>
                
                <div class="subsection-title">{t('citation_dynamics_by_year')}</div>
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>Publication Year</th>
                                <th>Citation Year</th>
                                <th>Citations Count</th>
                            </tr>
                        </thead>
                        <tbody>
                            {dynamics_rows}
                        </tbody>
                    </table>
                </div>
                
                <div class="subsection-title">{t('cumulative_citations')}</div>
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>Year</th>
                                <th>Cumulative Citations</th>
                            </tr>
                        </thead>
                        <tbody>
                            {cumul_rows}
                        </tbody>
                    </table>
                </div>
                
                <div class="subsection-title">{t('citation_network_heatmap')}</div>
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>Publication Year \ Citation Year</th>
                                {''.join([f'<th>{y}</th>' for y in cite_years])}
                            </tr>
                        </thead>
                        <tbody>
                            {heatmap_rows}
                        </tbody>
                    </table>
                </div>
                
                <div class="subsection-title">{t('most_cited_publications')}</div>
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>Rank</th>
                                <th>Title</th>
                                <th>Year</th>
                                <th>Citations</th>
                                <th>Citations/Year</th>
                                <th>Authors</th>
                                <th>DOI</th>
                            </tr>
                        </thead>
                        <tbody>
                            {most_cited_rows}
                        </tbody>
                    </table>
                </div>
            </div>
            
            <!-- Citing Works Analysis -->
            <div id="citing_works" class="section">
                <div class="section-title"><span class="icon">📚</span> {t('citing_works_analysis')}</div>
                
                <div class="subsection-title">{t('citing_works_analysis')}</div>
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>Metric</th>
                                <th>Value</th>
                            </tr>
                        </thead>
                        <tbody>
                            {citing_stats_rows}
                        </tbody>
                    </table>
                </div>
                
                <div class="subsection-title">{t('top_citing_authors')}</div>
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>Rank</th>
                                <th>Author</th>
                                <th>Citations</th>
                            </tr>
                        </thead>
                        <tbody>
                            {top_citing_rows}
                        </tbody>
                    </table>
                </div>
                
                <div class="subsection-title">{t('top_citing_affiliations')}</div>
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>Rank</th>
                                <th>Affiliation</th>
                                <th>Citations</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr><td colspan="3">Data loading...</td></tr>
                        </tbody>
                    </table>
                </div>
                
                <div class="subsection-title">{t('top_citing_countries')}</div>
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>Rank</th>
                                <th>Country</th>
                                <th>Citations</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr><td colspan="3">Data loading...</td></tr>
                        </tbody>
                    </table>
                </div>
                
                <div class="subsection-title">{t('top_citing_journals')}</div>
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>Rank</th>
                                <th>Journal</th>
                                <th>Citations</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr><td colspan="3">Data loading...</td></tr>
                        </tbody>
                    </table>
                </div>
                
                <div class="subsection-title">{t('top_citing_publishers')}</div>
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>Rank</th>
                                <th>Publisher</th>
                                <th>Citations</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr><td colspan="3">Data loading...</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
            
            <!-- Topics Analysis -->
            <div id="topics_analysis" class="section">
                <div class="section-title"><span class="icon">🏷️</span> {t('topics_analysis')}</div>
                
                <div class="subsection-title">{t('topics_table')}</div>
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>Topic</th>
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
                            {topics_rows}
                        </tbody>
                    </table>
                </div>
                
                <div class="subsection-title">{t('top_cited_topics')}</div>
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>Topic</th>
                                <th>Citations</th>
                            </tr>
                        </thead>
                        <tbody>
                            {top_topics_rows}
                        </tbody>
                    </table>
                </div>
                
                <div class="subsection-title">{t('top_cited_subtopics')}</div>
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>Subtopic</th>
                                <th>Citations</th>
                            </tr>
                        </thead>
                        <tbody>
                            {top_subtopics_rows}
                        </tbody>
                    </table>
                </div>
                
                <div class="subsection-title">{t('top_cited_fields')}</div>
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>Field</th>
                                <th>Citations</th>
                            </tr>
                        </thead>
                        <tbody>
                            {top_fields_rows}
                        </tbody>
                    </table>
                </div>
                
                <div class="subsection-title">{t('top_cited_domains')}</div>
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>Domain</th>
                                <th>Citations</th>
                            </tr>
                        </thead>
                        <tbody>
                            {top_domains_rows}
                        </tbody>
                    </table>
                </div>
                
                <div class="subsection-title">{t('top_cited_concepts')}</div>
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>Concept</th>
                                <th>Citations</th>
                            </tr>
                        </thead>
                        <tbody>
                            {top_concepts_rows}
                        </tbody>
                    </table>
                </div>
            </div>
            
            <!-- Detailed Citations -->
            <div id="detailed_citations" class="section">
                <div class="section-title"><span class="icon">📋</span> {t('detailed_citations')}</div>
                {detailed_citations_html if detailed_citations_html else '<p>No detailed citations available</p>'}
            </div>
            
            <!-- All Publications -->
            <div id="all_publications" class="section">
                <div class="section-title"><span class="icon">📄</span> {t('all_publications')}</div>
                
                <div class="filter-section">
                    <div class="filter-row">
                        <div>
                            <label for="yearFilter">{t('filter_by_year')}:</label>
                            <select id="yearFilter" onchange="filterPublications()">
                                {year_options_html}
                            </select>
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
                            <label for="citationFilter">{t('filter_by_citations')}:</label>
                            <input type="number" id="citationFilter" placeholder="Min citations..." min="0" onchange="filterPublications()">
                        </div>
                        <div>
                            <label for="searchInput">{t('search_publications')}:</label>
                            <input type="text" id="searchInput" placeholder="Search..." onkeyup="filterPublications()">
                        </div>
                        <div>
                            <span id="visibleCount" style="font-weight: 500;">All publications</span>
                        </div>
                    </div>
                </div>
                
                <div class="table-container">
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
                            {all_pubs_rows}
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
    </body>
    </html>
    """
    
    return html_content

# ============================================
# ОСНОВНАЯ ФУНКЦИЯ АНАЛИЗА ЖУРНАЛА
# ============================================

def analyze_journal(issn: str, period_input: str, max_workers: int = 8, progress_callback=None) -> Dict:
    """Основная функция анализа журнала"""
    
    issn_clean = normalize_issn(issn)
    period_str = period_input.strip()
    
    # Парсим период
    if ',' in period_str:
        years = [int(y.strip()) for y in period_str.split(',') if y.strip().isdigit()]
    elif '-' in period_str:
        years = tuple(map(int, [x.strip() for x in period_str.split('-')]))
    else:
        years = int(period_str)
    
    # Проверяем кэш
    cache_data = load_from_cache_journal(issn_clean, period_str)
    if cache_data:
        return cache_data
    
    # Создаем клиент
    client = OpenAlexClient(max_workers=max_workers, max_citing=MAX_CITING_PER_PAPER)
    
    # Этап 1: Загрузка статей
    if progress_callback:
        progress_callback(0, 100, 'loading_articles')
    
    articles = []
    page_count = 0
    
    def article_progress(current, data):
        nonlocal page_count
        page_count = current
        if progress_callback:
            progress_callback(min(40, current * 2), 100, 'loading_articles')
    
    raw_articles = client.get_journal_articles(issn_clean, years, article_progress)
    
    if not raw_articles:
        return {'error': 'No articles found'}
    
    if progress_callback:
        progress_callback(40, 100, 'citing_works')
    
    # Этап 2: Сбор цитирующих работ
    citing_map = {}
    
    def citing_progress(current, total):
        if progress_callback:
            pct = 40 + (current / total) * 40
            progress_callback(min(80, pct), 100, 'citing_works')
    
    citing_map = client.get_citing_works_batch(raw_articles, citing_progress)
    
    if progress_callback:
        progress_callback(80, 100, 'generating_report')
    
    # Этап 3: Обработка данных
    processor = JournalDataProcessor(raw_articles, citing_map)
    processed_data = processor.process()
    
    # Добавляем метаданные
    processed_data['issn'] = issn_clean
    processed_data['period'] = period_str
    processed_data['total_articles'] = len(raw_articles)
    processed_data['total_citations'] = sum([a.get('cited_by_count', 0) for a in raw_articles])
    
    # Сохраняем в кэш
    save_to_cache_journal(issn_clean, period_str, processed_data)
    
    if progress_callback:
        progress_callback(100, 100, 'generating_report')
    
    return processed_data

# ============================================
# STREAMLIT ИНТЕРФЕЙС
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
    if 'journal_data' not in st.session_state:
        st.session_state.journal_data = None
    if 'journal_logo_base64' not in st.session_state:
        st.session_state.journal_logo_base64 = None
    if 'app_logo_base64' not in st.session_state:
        st.session_state.app_logo_base64 = None
    
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
    tab1, tab2, tab3 = st.tabs([
        t('load_data'),
        t('journal_analysis'),
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
                help="Enter ISSN in format 0028-0836"
            )
        
        with col2:
            period_input = st.text_input(
                t('period_input'),
                placeholder=t('period_placeholder'),
                help="Enter year range (2020-2023) or list (2020,2021,2022) or single year (2020)"
            )
        
        workers_slider = st.slider(
            t('workers_label'),
            min_value=4,
            max_value=12,
            value=8,
            step=1
        )
        
        journal_logo_upload = st.file_uploader(
            t('upload_logo'),
            type=['png', 'jpg', 'jpeg', 'svg'],
            help=t('logo_help')
        )
        
        if st.button(t('analyze_button'), type="primary", width='stretch'):
            if not issn_input:
                st.error(t('no_issn'))
            elif not period_input:
                st.error("⚠️ Enter analysis period")
            else:
                journal_logo_data = None
                if journal_logo_upload:
                    journal_logo_data = {
                        journal_logo_upload.name: {
                            'content': journal_logo_upload.read()
                        }
                    }
                    st.session_state.journal_logo_base64 = base64.b64encode(
                        journal_logo_upload.read()
                    ).decode()
                
                # Загружаем логотип приложения
                app_logo_base64 = None
                if os.path.exists("icon.png"):
                    try:
                        with open("icon.png", "rb") as f:
                            app_logo_base64 = base64.b64encode(f.read()).decode()
                            st.session_state.app_logo_base64 = app_logo_base64
                    except Exception as e:
                        print(f"⚠️ Ошибка загрузки логотипа приложения: {e}")
                
                # Прогресс-бар
                progress_bar = st.progress(0, text=t('starting_analysis'))
                status_text = st.empty()
                
                def progress_callback(current, total, stage):
                    pct = (current / total * 100) if total > 0 else 0
                    if stage == 'loading_articles':
                        progress_bar.progress(pct / 100, text=t('stage_loading_articles'))
                        status_text.info(t('loading_articles_progress', current=current, total=total))
                    elif stage == 'citing_works':
                        progress_bar.progress(pct / 100, text=t('stage_citing_works'))
                        status_text.info(t('citing_works_progress', current=current, total=total))
                    elif stage == 'generating_report':
                        progress_bar.progress(pct / 100, text=t('stage_generating_report'))
                        status_text.info(t('generating_report_progress'))
                
                try:
                    start_time = time.time()
                    
                    data = analyze_journal(
                        issn_input,
                        period_input,
                        max_workers=workers_slider,
                        progress_callback=progress_callback
                    )
                    
                    if 'error' in data:
                        st.error(f"❌ {data['error']}")
                        progress_bar.empty()
                        return
                    
                    elapsed = time.time() - start_time
                    
                    st.session_state.journal_data = data
                    st.session_state.analysis_complete = True
                    st.session_state.issn = issn_input
                    st.session_state.period = period_input
                    
                    progress_bar.progress(1.0, text="✅ " + t('analysis_complete_text'))
                    
                    st.success(t('analysis_complete', 
                                count=data.get('total_articles', 0), 
                                time=elapsed))
                    
                    st.balloons()
                    
                except Exception as e:
                    st.error(f"❌ {t('error_occurred')}: {str(e)}")
                    import traceback
                    st.code(traceback.format_exc())
                finally:
                    progress_bar.empty()
                    status_text.empty()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        if st.session_state.analysis_complete and st.session_state.journal_data:
            data = st.session_state.journal_data
            metrics = data.get('metrics', {})
            
            st.markdown(f"## {t('journal_analysis')}")
            st.markdown(f"**ISSN:** {st.session_state.issn} | **Period:** {st.session_state.period}")
            
            # Metrics display
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.metric(t('total_publications'), metrics.get('total_publications', 0))
            with col2:
                st.metric(t('total_citations'), f"{metrics.get('total_citations', 0):,}")
            with col3:
                st.metric(t('h_index'), metrics.get('h_index', 0))
            with col4:
                st.metric(t('g_index'), metrics.get('g_index', 0))
            with col5:
                st.metric(t('open_access'), f"{metrics.get('oa_percentage', 0):.1f}%")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric(t('i10_index'), metrics.get('i10_index', 0))
            with col2:
                st.metric(t('i100_index'), metrics.get('i100_index', 0))
            with col3:
                st.metric(t('avg_citations'), f"{metrics.get('avg_citations', 0):.1f}")
            with col4:
                st.metric(t('active_years'), metrics.get('active_years', 0))
            
            # Open Access Breakdown
            oa_breakdown = metrics.get('oa_breakdown', {})
            if oa_breakdown:
                st.markdown("### Open Access Breakdown")
                oa_df = pd.DataFrame([
                    {'Status': status, 'Count': count}
                    for status, count in oa_breakdown.items() if count > 0
                ])
                st.dataframe(oa_df, width='stretch')
            
            # Articles preview
            with st.expander(f"{t('publications')} ({metrics.get('total_publications', 0)})"):
                articles = data.get('articles', [])
                if articles:
                    preview_data = []
                    for a in articles[:20]:
                        preview_data.append({
                            'Title': a.title[:60] + '...' if len(a.title) > 60 else a.title,
                            'Year': a.publication_year,
                            'Citations': a.cited_by_count,
                            'Journal': a.journal_name,
                            'DOI': a.doi
                        })
                    st.dataframe(pd.DataFrame(preview_data), width='stretch')
                    if len(articles) > 20:
                        st.caption(f"Showing 20 of {len(articles)} publications")
            
            # Top Authors
            author_analysis = data.get('author_analysis', [])
            if author_analysis:
                with st.expander(f"Top Authors"):
                    author_df = pd.DataFrame([
                        {
                            'Author': a['name'],
                            'Publications': a['publications'],
                            'Citations': a['citations'],
                            'ORCID': a.get('orcid', 'N/A'),
                            'Countries': ', '.join(list(a['countries'])[:3])
                        }
                        for a in author_analysis[:20]
                    ])
                    st.dataframe(author_df, width='stretch')
            
            # Top Affiliations
            top_affiliations = data.get('top_affiliations', [])
            if top_affiliations:
                with st.expander(f"Top Affiliations"):
                    affil_df = pd.DataFrame([
                        {
                            'Affiliation': a['name'],
                            'Country': a.get('country', 'N/A'),
                            'Publications': a['publications'],
                            'Citations': a['citations'],
                            'Unique Authors': len(a['authors'])
                        }
                        for a in top_affiliations[:15]
                    ])
                    st.dataframe(affil_df, width='stretch')
            
            # Most Cited
            most_cited = data.get('most_cited', [])
            if most_cited:
                with st.expander("Most Cited Publications"):
                    cited_df = pd.DataFrame([
                        {
                            'Rank': a['rank'],
                            'Title': a['title'][:60] + '...' if len(a['title']) > 60 else a['title'],
                            'Year': a['year'],
                            'Citations': a['citations'],
                            'Citations/Year': a['citations_per_year'],
                            'Authors': a['authors'],
                            'DOI': a['doi']
                        }
                        for a in most_cited[:15]
                    ])
                    st.dataframe(cited_df, width='stretch')
            
        else:
            st.info(t('no_data'))
    
    with tab3:
        if st.session_state.analysis_complete and st.session_state.journal_data:
            data = st.session_state.journal_data
            theme_colors = {
                'primary': st.session_state.primary_color,
                'secondary': st.session_state.secondary_color
            }
            
            st.markdown(f"## {t('html_report')}")
            
            if st.button(t('download_report'), type="primary", width='stretch'):
                with st.spinner(t('generating_report')):
                    html_report = generate_journal_html_report(
                        data,
                        st.session_state.issn,
                        st.session_state.period,
                        st.session_state.journal_logo_base64,
                        st.session_state.app_logo_base64,
                        theme_colors,
                        current_lang
                    )
                    
                    filename = f"journal_{st.session_state.issn}_{st.session_state.period}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
                    
                    st.download_button(
                        label="📥 " + t('download_report'),
                        data=html_report.encode('utf-8'),
                        file_name=filename,
                        mime="text/html",
                        width='stretch'
                    )
            
            st.markdown("---")
            st.markdown(f"### {t('report_preview')}")
            st.info(t('download_hint'))
        else:
            st.info(t('no_data_reports'))

if __name__ == "__main__":
    main()
