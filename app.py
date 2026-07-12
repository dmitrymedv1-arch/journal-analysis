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

# Параметры для параллельного анализа журналов
MAX_WORKERS = 8  # Количество параллельных потоков
BASE_DELAY = 0.35  # Базовая задержка между запросами
MAX_CITING_PER_PAPER = 300  # Максимум цитирующих работ на статью

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
from threading import Lock
import random

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
        'issn_input': 'Journal ISSN(s)',
        'issn_placeholder': '0028-0836\nor: 0028-0836, 0036-8075',
        'issn_help': 'Enter one or more ISSNs. Separators: comma, space, new line',
        'period_input': 'Analysis Period',
        'period_placeholder': '2020-2023 or 2020,2021,2022',
        'period_help': 'Enter year range (e.g., 2020-2023) or list (e.g., 2020,2021,2022)',
        'upload_logo': 'Upload journal logo (optional)',
        'logo_help': 'Logo will be displayed in reports',
        'analyze_button': '🔍 Analyze Journal(s)',
        'no_issn': '⚠️ Enter at least one ISSN',
        'too_many_issns': '⚠️ Found {count} ISSNs. This may take a long time...',
        'analysis_complete': '✅ Analysis complete! Found {count} articles in {time:.1f} sec.',
        'best_journal': '🏆 Best journal: {name} (h-index: {h_index})',
        'single_journal': '📊 Journal: {name} (h-index: {h_index})',
        'showing_all': '📊 Showing all {count} journals (sorted by h-index)',
        'showing_single': '📊 Showing only the best journal',
        'showing_single_only': '📊 Showing single journal',
        'no_data': '👈 Load data in "Load Data" tab and click "Analyze Journal(s)"',
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
        'enter_issn': 'Enter ISSN to analyze',
        'analyze_multiple': 'Analyze multiple journals',
        'profile_analysis': 'Comprehensive journal analysis by ISSN',
        'select_language': 'Select language',
        'theme_presets_label': 'Theme presets',
        'primary_color_label': 'Primary color',
        'secondary_color_label': 'Secondary color',
        'analysis_progress': 'Analysis progress',
        'loading_data': 'Loading data',
        'analyzing_data': 'Analyzing data',
        'generating_viz': 'Generating visualizations',
        'issn_format_error': 'Invalid ISSN format',
        'data_not_found': 'Data not found. Check ISSN correctness.',
        'error_occurred': 'Error occurred',
        'analyzing_journals': 'Analyzing {count} journal(s)...',
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
        # Новые ключи для Journal Analysis
        'issn': 'ISSN',
        'period': 'Period',
        'analyze_journal': 'Analyze Journal',
        'journal_name': 'Journal Name',
        'publisher': 'Publisher',
        'total_publications': 'Total Publications',
        'total_citations': 'Total Citations',
        'avg_citations': 'Avg Citations',
        'open_access_breakdown': 'Open Access Breakdown',
        'gold': 'Gold',
        'hybrid': 'Hybrid',
        'green': 'Green',
        'bronze': 'Bronze',
        'closed': 'Closed',
        'unknown': 'Unknown',
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
        'overview': 'Overview',
        'analyzed_articles': 'Analyzed Articles',
        'author_analysis': 'Author Analysis',
        'top_affiliations': 'Top Affiliations',
        'geographic_analysis': 'Geographic Analysis',
        'countries_per_publication': 'Unique Countries per Publication',
        'authors_per_country': 'Authors per Country (Individual Distribution)',
        'collaboration_patterns': 'Collaboration Patterns',
        'collaboration_couples': 'Collaboration Couples',
        'citation_analysis': 'Citation Analysis',
        'citation_dynamics': 'Citation Dynamics by Year',
        'cumulative_citations': 'Cumulative Citations',
        'citation_heatmap': 'Citation Network Heatmap',
        'most_cited_publications': 'Most Cited Publications',
        'citing_works_analysis': 'Citing Works Analysis',
        'top_citing_authors': 'Top Citing Authors',
        'top_citing_affiliations': 'Top Citing Affiliations',
        'top_citing_countries': 'Top Citing Countries',
        'top_citing_journals': 'Top Citing Journals',
        'top_citing_publishers': 'Top Citing Publishers',
        'topics_analysis': 'Topics Analysis',
        'topics_overview': 'Topics Overview',
        'top_topics': 'Top Topics',
        'top_subtopics': 'Top Subtopics',
        'top_fields': 'Top Fields',
        'top_domains': 'Top Domains',
        'top_concepts': 'Top Concepts',
        'detailed_citations': 'Detailed Citations for Analyzed Works',
        'all_publications': 'All Publications',
        'rank': 'Rank',
        'authors': 'Authors',
        'citations_year': 'Citations/Year',
        'citation_count': 'Citations Count',
        'citing_journal': 'Citing Journal',
        'citing_year': 'Citing Year',
        'citing_date': 'Citing Date',
        'citation_lag': 'Citation Lag',
        'show_citations': 'Show Citations',
        'filter_by_year': 'Filter by Year',
        'filter_by_author': 'Filter by Author',
        'filter_by_citations': 'Filter by Citations (min)',
        'filter_by_title': 'Filter by Title Word(s)',
        'filter_by_affiliation': 'Filter by Affiliations',
        'search_publications': 'Search Publications',
        'all_years': 'All Years',
        'all_publications_count': 'All publications',
        'citing_works': 'Citing Works',
        'total_citing_works': 'Total Citing Works',
        'first_year': 'First Year',
        'peak_year': 'Peak Year',
        'analyzed_count': 'Analyzed Count',
        'citing_count': 'Citing Count',
        'analyzed_norm_count': 'Analyzed Norm Count',
        'citing_norm_count': 'Citing Norm Count',
        'total_norm_count': 'Total Norm Count',
        'single_country': 'Single Country',
        'international': 'International',
        'collaboration_couple': 'Collaboration Couple',
        'frequency': 'Frequency',
        'publication_year_vs_citation_year': 'Publication Year \\ Citation Year',
        'authors_per_article': 'Authors per Article',
        'affiliations_per_article': 'Affiliations per Article',
        'countries_per_article': 'Countries per Article',
        'publication_year': 'Publication Year',
        'citation_year': 'Citation Year',
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
        'journal_analysis': '📊 Анализ журнала',
        'reports': '📄 Отчеты',
        'issn_input': 'ISSN журнала(ов)',
        'issn_placeholder': '0028-0836\nили: 0028-0836, 0036-8075',
        'issn_help': 'Введите один или несколько ISSN. Разделители: запятая, пробел, новая строка',
        'period_input': 'Период анализа',
        'period_placeholder': '2020-2023 или 2020,2021,2022',
        'period_help': 'Введите диапазон лет (например, 2020-2023) или список (например, 2020,2021,2022)',
        'upload_logo': 'Загрузить логотип журнала (опционально)',
        'logo_help': 'Логотип будет отображаться в отчетах',
        'analyze_button': '🔍 Анализировать журнал(ы)',
        'no_issn': '⚠️ Введите хотя бы один ISSN',
        'too_many_issns': '⚠️ Найдено {count} ISSN. Это может занять много времени...',
        'analysis_complete': '✅ Анализ завершен! Найдено {count} статей за {time:.1f} сек.',
        'best_journal': '🏆 Лучший журнал: {name} (h-index: {h_index})',
        'single_journal': '📊 Журнал: {name} (h-index: {h_index})',
        'showing_all': '📊 Показаны все {count} журналов (сортировка по h-index)',
        'showing_single': '📊 Показан только лучший журнал',
        'showing_single_only': '📊 Показан единственный журнал',
        'no_data': '👈 Загрузите данные на вкладке "Загрузка данных" и нажмите "Анализировать журнал(ы)"',
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
        'enter_issn': 'Введите ISSN для анализа',
        'analyze_multiple': 'Анализировать несколько журналов',
        'profile_analysis': 'Комплексный анализ журнала по ISSN',
        'select_language': 'Выберите язык',
        'theme_presets_label': 'Пресеты тем',
        'primary_color_label': 'Основной цвет',
        'secondary_color_label': 'Дополнительный цвет',
        'analysis_progress': 'Прогресс анализа',
        'loading_data': 'Загрузка данных',
        'analyzing_data': 'Анализ данных',
        'generating_viz': 'Генерация визуализаций',
        'issn_format_error': 'Неверный формат ISSN',
        'data_not_found': 'Данные не найдены. Проверьте правильность ISSN.',
        'error_occurred': 'Произошла ошибка',
        'analyzing_journals': 'Анализирую {count} журналов...',
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
        # Новые ключи для Journal Analysis
        'issn': 'ISSN',
        'period': 'Период',
        'analyze_journal': 'Анализировать журнал',
        'journal_name': 'Название журнала',
        'publisher': 'Издатель',
        'total_publications': 'Всего публикаций',
        'total_citations': 'Всего цитирований',
        'avg_citations': 'Среднее цитирований',
        'open_access_breakdown': 'Разбивка открытого доступа',
        'gold': 'Gold',
        'hybrid': 'Hybrid',
        'green': 'Green',
        'bronze': 'Bronze',
        'closed': 'Closed',
        'unknown': 'Unknown',
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
        'unique_citing_publishers': 'Уникальных цитирующих издателей',
        'overview': 'Обзор',
        'analyzed_articles': 'Анализируемые статьи',
        'author_analysis': 'Анализ авторов',
        'top_affiliations': 'Топ аффилиаций',
        'geographic_analysis': 'Географический анализ',
        'countries_per_publication': 'Уникальные страны на публикацию',
        'authors_per_country': 'Авторы по странам (индивидуальное распределение)',
        'collaboration_patterns': 'Паттерны коллабораций',
        'collaboration_couples': 'Пары коллабораций',
        'citation_analysis': 'Цитационный анализ',
        'citation_dynamics': 'Динамика цитирований по годам',
        'cumulative_citations': 'Накопленные цитирования',
        'citation_heatmap': 'Тепловая карта цитирований',
        'most_cited_publications': 'Самые цитируемые публикации',
        'citing_works_analysis': 'Анализ цитирующих работ',
        'top_citing_authors': 'Топ цитирующих авторов',
        'top_citing_affiliations': 'Топ цитирующих аффилиаций',
        'top_citing_countries': 'Топ цитирующих стран',
        'top_citing_journals': 'Топ цитирующих журналов',
        'top_citing_publishers': 'Топ цитирующих издателей',
        'topics_analysis': 'Тематический анализ',
        'topics_overview': 'Обзор тем',
        'top_topics': 'Топ темы',
        'top_subtopics': 'Топ подтемы',
        'top_fields': 'Топ поля',
        'top_domains': 'Топ домены',
        'top_concepts': 'Топ концепты',
        'detailed_citations': 'Детальные цитирования для анализируемых работ',
        'all_publications': 'Все публикации',
        'rank': 'Ранг',
        'authors': 'Авторы',
        'citations_year': 'Цитирований/год',
        'citation_count': 'Количество цитирований',
        'citing_journal': 'Цитирующий журнал',
        'citing_year': 'Год цитирования',
        'citing_date': 'Дата цитирования',
        'citation_lag': 'Задержка цитирования',
        'show_citations': 'Показать цитирования',
        'filter_by_year': 'Фильтр по году',
        'filter_by_author': 'Фильтр по автору',
        'filter_by_citations': 'Фильтр по цитированиям (мин)',
        'filter_by_title': 'Фильтр по словам в названии',
        'filter_by_affiliation': 'Фильтр по аффилиации',
        'search_publications': 'Поиск публикаций',
        'all_years': 'Все годы',
        'all_publications_count': 'Все публикации',
        'citing_works': 'Цитирующие работы',
        'total_citing_works': 'Всего цитирующих работ',
        'first_year': 'Первый год',
        'peak_year': 'Пиковый год',
        'analyzed_count': 'Кол-во анализируемых',
        'citing_count': 'Кол-во цитирующих',
        'analyzed_norm_count': 'Норм. кол-во анализируемых',
        'citing_norm_count': 'Норм. кол-во цитирующих',
        'total_norm_count': 'Общее норм. кол-во',
        'single_country': 'Одна страна',
        'international': 'Международные',
        'collaboration_couple': 'Пара коллаборации',
        'frequency': 'Частота',
        'publication_year_vs_citation_year': 'Год публикации \\ Год цитирования',
        'authors_per_article': 'Авторов на статью',
        'affiliations_per_article': 'Аффилиаций на статью',
        'countries_per_article': 'Стран на статью',
        'publication_year': 'Год публикации',
        'citation_year': 'Год цитирования',
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
    """Нормализует имя автора для сравнения (инициал + фамилия) - задача 2"""
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

def normalize_issn(issn_str: str) -> str:
    """Нормализует ISSN для запросов к API"""
    cleaned = re.sub(r'[^0-9Xx]', '', str(issn_str).strip())
    if len(cleaned) == 8:
        return f"{cleaned[:4]}-{cleaned[4:]}".upper()
    return cleaned.upper()

def parse_issns(text: str) -> List[str]:
    """Парсит ISSN из текста. Поддерживает множественный ввод."""
    if not text or not text.strip():
        return []
    
    # Заменяем разделители на пробелы
    text = text.replace('\n', ' ').replace('\r', ' ')
    text = text.replace(',', ' ').replace(';', ' ')
    
    # Ищем все ISSN в тексте
    issn_pattern = r'\d{4}-\d{3}[\dX]'
    matches = re.findall(issn_pattern, text, re.IGNORECASE)
    
    # Также ищем без дефиса
    issn_pattern2 = r'\d{7}[\dX]'
    matches2 = re.findall(issn_pattern2, text, re.IGNORECASE)
    
    all_issns = matches + matches2
    
    # Нормализуем и возвращаем уникальные
    cleaned = [normalize_issn(o) for o in all_issns]
    return list(dict.fromkeys(cleaned))

def parse_period(period_text: str) -> Any:
    """Парсит период из текста"""
    period_text = period_text.strip()
    if not period_text:
        return None
    
    if ',' in period_text:
        years = [int(y.strip()) for y in period_text.split(',') if y.strip().isdigit()]
        return years
    elif '-' in period_text:
        parts = period_text.split('-')
        if len(parts) == 2:
            try:
                start = int(parts[0].strip())
                end = int(parts[1].strip())
                return (start, end)
            except:
                pass
    else:
        try:
            return int(period_text)
        except:
            pass
    
    return None

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
# ФУНКЦИЯ ДЛЯ ПОЛУЧЕНИЯ ЖУРНАЛЬНЫХ СТАТЕЙ ПО ISSN
# ============================================

def smart_get(url: str, params: dict = None, retries: int = MAX_RETRIES) -> Optional[dict]:
    """Умный GET запрос с защитой от rate limiting (синхронная версия)"""
    lock = Lock()
    
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
                print(f"⚠️ Ошибка запроса: {e}")
            time.sleep(1.5 * (2 ** attempt))
    
    return None

def get_citing_dois(oa_id: str, max_citing: int = MAX_CITING_PER_PAPER) -> List[str]:
    """Получение цитирующих DOI для одной статьи"""
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
                if len(citing) >= max_citing:
                    return citing[:max_citing]
        
        cursor = data.get("meta", {}).get("next_cursor")
        if not cursor:
            break
    
    return citing[:max_citing]

def fetch_work_metadata(doi: str) -> Optional[Dict]:
    """Получение полных метаданных для одной работы по DOI"""
    if not doi:
        return None
    
    url = f"https://api.openalex.org/works/https://doi.org/{doi}"
    data = smart_get(url)
    
    if not data:
        return None
    
    return data

# ============================================
# ФУНКЦИЯ ПАРСИНГА ПУБЛИКАЦИИ ИЗ OPENALEX
# ============================================

def parse_openalex_publication(item: Dict) -> Dict:
    """Парсит публикацию из OpenAlex с расширенной информацией по темам и институтам"""
    try:
        pub = {}
        
        pub['id'] = item.get('id', '')
        pub['doi'] = item.get('doi', '').replace('https://doi.org/', '')
        pub['title'] = item.get('title', 'No title')
        pub['publication_year'] = item.get('publication_year')
        
        pub['type'] = item.get('type', 'unknown')
        pub['raw_type'] = item.get('raw_type', '')
        
        if item.get('primary_location'):
            source = item['primary_location'].get('source', {})
            pub['journal_name'] = source.get('display_name', 'Unknown')
            pub['publisher'] = source.get('host_organization_name') or source.get('publisher', 'Unknown')
            pub['issn'] = source.get('issn', [])
            pub['source_type'] = source.get('type', 'unknown')
        else:
            pub['journal_name'] = 'Unknown'
            pub['publisher'] = 'Unknown'
            pub['issn'] = []
            pub['source_type'] = 'unknown'
        
        oa = item.get('open_access', {})
        pub['is_oa'] = oa.get('is_oa', False)
        pub['open_access_status'] = oa.get('oa_status', 'closed')
        pub['oa_url'] = oa.get('oa_url', None)
        pub['any_repository_has_fulltext'] = oa.get('any_repository_has_fulltext', False)
        
        affiliations = []
        affiliation_countries = []
        institutions = []
        authors = []
        author_orcids = []
        authors_with_orcids = []
        
        for auth in item.get('authorships', []):
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
            
            if auth.get('institutions'):
                for inst in auth['institutions']:
                    affil = inst.get('display_name', '')
                    if affil:
                        affiliations.append(affil)
                        country = extract_country_from_affiliation(affil)
                        if country:
                            affiliation_countries.append(country)
                        
                        institutions.append({
                            'id': inst.get('id', ''),
                            'display_name': inst.get('display_name', ''),
                            'country_code': inst.get('country_code', ''),
                            'ror': inst.get('ror', ''),
                            'type': inst.get('type', ''),
                            'lineage': inst.get('lineage', [])
                        })
        
        pub['authors'] = authors
        pub['author_orcids'] = author_orcids
        pub['authors_with_orcids'] = authors_with_orcids
        pub['affiliations'] = affiliations
        pub['affiliation_countries'] = affiliation_countries
        pub['institutions'] = institutions
        
        pub['author_count'] = len(authors)
        pub['affiliation_count'] = len(set(affiliations))
        pub['country_count'] = len(set(affiliation_countries))
        
        if affiliations:
            pub['country'] = extract_country_from_affiliation(affiliations[0])
        else:
            pub['country'] = 'Unknown'
        
        primary_topic = item.get('primary_topic', {})
        if primary_topic:
            pub['primary_topic'] = {
                'display_name': primary_topic.get('display_name', ''),
                'subfield': primary_topic.get('subfield', {}).get('display_name', ''),
                'field': primary_topic.get('field', {}).get('display_name', ''),
                'domain': primary_topic.get('domain', {}).get('display_name', ''),
                'score': primary_topic.get('score', 0)
            }
        else:
            pub['primary_topic'] = None
        
        topics_list = item.get('topics', [])
        pub['topics'] = [
            {
                'display_name': t.get('display_name', ''),
                'subfield': t.get('subfield', {}).get('display_name', ''),
                'field': t.get('field', {}).get('display_name', ''),
                'domain': t.get('domain', {}).get('display_name', ''),
                'score': t.get('score', 0)
            }
            for t in topics_list
        ]
        
        keywords = item.get('keywords', [])
        pub['keywords'] = [k.get('display_name', '') for k in keywords if k.get('display_name')]
        
        concepts = []
        concept_levels = {}
        fields = []
        domains = []
        topics_old = []
        subtopics = []
        
        for concept in item.get('concepts', []):
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
        
        pub['concepts'] = concepts[:15]
        pub['concept_levels'] = concept_levels
        pub['fields'] = fields[:10]
        pub['domains'] = domains[:5]
        pub['topics_old'] = topics_old[:15]
        pub['subtopics'] = subtopics[:20]
        
        pub['cited_by_count'] = item.get('cited_by_count', 0)
        pub['cited_by_percentile'] = item.get('cited_by_percentile', {})
        
        pub['is_retracted'] = item.get('is_retracted', False)
        pub['is_correction'] = item.get('is_correction', False)
        pub['is_paratext'] = item.get('is_paratext', False)
        
        if pub['is_retracted']:
            pub['retraction_info'] = item.get('retraction_info', {})
        
        pub['publication_date'] = item.get('publication_date')
        pub['created_date'] = item.get('created_date')
        pub['updated_date'] = item.get('updated_date')
        
        # Определяем категорию источника
        pub['source_category'] = determine_source_category(pub)
        
        return pub
        
    except Exception as e:
        if SHOW_DEBUG_LOGS:
            print(f"⚠️ Ошибка парсинга публикации: {e}")
        return None

def determine_source_category(pub_data: Dict) -> str:
    """
    Определяет категорию источника публикации на основе полей OpenAlex.
    Возвращает одну из: 'articles', 'repositories', 'ebooks', 'proceedings', 'other'
    """
    source_type = pub_data.get('source_type', 'unknown')
    raw_type = pub_data.get('raw_type', '')
    pub_type = pub_data.get('type', '')
    
    # Приоритет: raw_type > source.type > type
    
    # Проверяем raw_type
    if raw_type:
        raw_lower = raw_type.lower()
        if 'journal-article' in raw_lower or 'journal article' in raw_lower:
            return 'articles'
        if 'posted-content' in raw_lower or 'preprint' in raw_lower:
            return 'repositories'
        if 'book-chapter' in raw_lower or 'book chapter' in raw_lower:
            return 'ebooks'
        if 'proceedings-article' in raw_lower or 'proceedings article' in raw_lower:
            return 'proceedings'
    
    # Проверяем source.type
    if source_type:
        source_lower = source_type.lower()
        if 'journal' in source_lower:
            return 'articles'
        if 'repository' in source_lower:
            return 'repositories'
        if 'ebook platform' in source_lower or 'ebook' in source_lower:
            return 'ebooks'
    
    # Проверяем pub_type
    if pub_type:
        pub_lower = pub_type.lower()
        if 'article' in pub_lower and 'journal' not in pub_lower:
            # Если просто article, но не journal-article - проверяем контекст
            pass
        if 'book-chapter' in pub_lower:
            return 'ebooks'
        if 'proceedings' in pub_lower:
            return 'proceedings'
    
    # Если ничего не подошло - определяем по наличию DOI
    if pub_data.get('doi'):
        # Есть DOI, но тип не определен - считаем статьей
        return 'articles'
    else:
        return 'other'

# ============================================
# НОВАЯ ФУНКЦИЯ: ОБНАРУЖЕНИЕ ВРЕМЕННЫХ РАЗРЫВОВ
# ============================================

def detect_temporal_gaps(publications: List[Dict], min_gap_years: int = 10) -> Dict:
    """
    Анализирует временные разрывы между публикациями.
    
    Args:
        publications: Список публикаций
        min_gap_years: Минимальный разрыв для обнаружения (по умолчанию 10 лет)
    
    Returns:
        Dict: {
            'has_gap': bool,
            'gap_years': int,
            'gap_start': int,  # год начала разрыва
            'gap_end': int,    # год окончания разрыва
            'clusters': List[List[int]],  # кластеры публикаций по годам
            'suggestion': str,  # предложение по отсечению
            'cut_off_year': int,  # рекомендуемый год отсечения
            'min_year': int,
            'max_year': int,
            'all_years': List[int]
        }
    """
    if not publications:
        return {'has_gap': False}
    
    # Получаем все годы публикаций
    years = sorted([p.get('publication_year') for p in publications if p.get('publication_year')])
    if len(years) < 2:
        return {'has_gap': False}
    
    unique_years = sorted(set(years))
    
    # Находим самый большой разрыв между соседними годами
    max_gap = 0
    gap_start = None
    gap_end = None
    
    for i in range(len(unique_years) - 1):
        current_gap = unique_years[i+1] - unique_years[i]
        if current_gap > max_gap:
            max_gap = current_gap
            gap_start = unique_years[i]
            gap_end = unique_years[i+1]
    
    if max_gap >= min_gap_years:
        # Определяем кластеры публикаций
        clusters = []
        current_cluster = [unique_years[0]]
        
        for i in range(1, len(unique_years)):
            if unique_years[i] - unique_years[i-1] >= min_gap_years:
                clusters.append(current_cluster)
                current_cluster = [unique_years[i]]
            else:
                current_cluster.append(unique_years[i])
        
        if current_cluster:
            clusters.append(current_cluster)
        
        # Определяем рекомендацию по отсечению
        # Обычно отсекаем старые публикации (первый кластер)
        if len(clusters) > 1:
            # Находим самый большой кластер (предположительно основной период активности)
            main_cluster = max(clusters, key=len)
            cut_off_year = min(main_cluster)
            
            return {
                'has_gap': True,
                'gap_years': max_gap,
                'gap_start': gap_start,
                'gap_end': gap_end,
                'clusters': clusters,
                'cut_off_year': cut_off_year,
                'suggestion': f"Рекомендуется отсечь публикации до {cut_off_year} года",
                'min_year': min(unique_years),
                'max_year': max(unique_years),
                'all_years': unique_years
            }
    
    return {
        'has_gap': False,
        'min_year': min(years) if years else None,
        'max_year': max(years) if years else None,
        'all_years': unique_years
    }

def get_filtered_publications(publications: List[Dict], start_year: Optional[int] = None, end_year: Optional[int] = None) -> List[Dict]:
    """Фильтрует публикации по диапазону лет"""
    if start_year is None and end_year is None:
        return publications
    
    filtered = []
    for p in publications:
        pub_year = p.get('publication_year')
        if pub_year is None:
            continue
        if start_year is not None and pub_year < start_year:
            continue
        if end_year is not None and pub_year > end_year:
            continue
        filtered.append(p)
    
    return filtered

# ============================================
# НОВЫЙ КЛАСС: JournalAnalyzer
# ============================================

class JournalAnalyzer:
    """Класс для анализа журнала по ISSN"""
    
    def __init__(self, issn: str, period: Any):
        self.issn = normalize_issn(issn)
        self.period = period
        self.articles = []  # Список статей журнала
        self.citing_map = {}  # {doi: [список цитирующих DOI]}
        self.citing_metadata = {}  # {doi: метаданные цитирующей работы}
        self.journal_info = {}
        self.profile = {}
        self.citation_dynamics = []  # [{pub_year, cite_year, count}]
        self.cumulative_citations = []  # [{year, total}]
        self.heatmap_data = {}  # {pub_year: {cite_year: count}}
        self.topic_analysis = {}  # Тематический анализ
        self.detailed_citations = {}  # Детальные цитирования для каждой статьи
        
    def add_article(self, article_data: Dict):
        """Добавляет статью журнала"""
        self.articles.append(article_data)
    
    def set_citing_map(self, citing_map: Dict):
        """Устанавливает карту цитирований"""
        self.citing_map = citing_map
    
    def set_citing_metadata(self, metadata: Dict):
        """Устанавливает метаданные цитирующих работ"""
        self.citing_metadata = metadata
    
    def set_journal_info(self, info: Dict):
        """Устанавливает информацию о журнале"""
        self.journal_info = info
    
    def analyze_publications(self):
        """Анализирует все публикации и строит профиль"""
        if not self.articles:
            print("⚠️ Нет статей для анализа")
            return
        
        print(f"📊 Анализирую {len(self.articles)} статей...")
        
        self.profile['total_publications'] = len(self.articles)
        self.profile['issn'] = self.issn
        
        # Информация о журнале
        self.profile['journal_name'] = self.journal_info.get('display_name', 'Unknown')
        self.profile['publisher'] = self.journal_info.get('publisher', 'Unknown')
        
        # Годы
        years = [p.get('publication_year') for p in self.articles if p.get('publication_year')]
        self.profile['years_distribution'] = dict(Counter(years))
        self.profile['first_publication'] = min(years) if years else None
        self.profile['last_publication'] = max(years) if years else None
        self.profile['active_years'] = len(set(years)) if years else 0
        
        # Цитирования
        citations = [p.get('cited_by_count', 0) for p in self.articles]
        self.profile['total_citations'] = sum(citations)
        self.profile['average_citations'] = sum(citations) / len(citations) if citations else 0
        self.profile['median_citations'] = np.median(citations) if citations else 0
        self.profile['max_citations'] = max(citations) if citations else 0
        
        # h-index
        citations_sorted = sorted([c for c in citations if c > 0], reverse=True)
        h_index = 0
        for i, c in enumerate(citations_sorted, 1):
            if c >= i:
                h_index = i
            else:
                break
        self.profile['h_index'] = h_index
        
        # i10-index
        self.profile['i10_index'] = sum(1 for c in citations if c >= 10)
        
        # i100-index
        self.profile['i100_index'] = sum(1 for c in citations if c >= 100)
        
        # g-index
        total_citations_sorted = 0
        g_index = 0
        for i, c in enumerate(citations_sorted, 1):
            total_citations_sorted += c
            if total_citations_sorted >= i**2:
                g_index = i
        self.profile['g_index'] = g_index
        
        # Open Access
        oa_statuses = [p.get('open_access_status') for p in self.articles if p.get('open_access_status')]
        self.profile['open_access'] = dict(Counter(oa_statuses))
        self.profile['total_oa'] = sum(1 for p in self.articles if p.get('is_oa', False))
        self.profile['oa_percentage'] = (self.profile['total_oa'] / len(self.articles) * 100) if self.articles else 0
        
        # Open Access Breakdown
        oa_types = {'gold': 0, 'hybrid': 0, 'green': 0, 'bronze': 0, 'closed': 0, 'unknown': 0}
        for p in self.articles:
            status = p.get('open_access_status', 'unknown')
            if status in oa_types:
                oa_types[status] += 1
            else:
                oa_types['unknown'] += 1
        self.profile['oa_types'] = oa_types
        
        # Авторы
        all_authors = []
        author_affiliations = []
        author_countries = []
        author_orcids = []
        
        for p in self.articles:
            if p.get('authors'):
                all_authors.extend(p['authors'])
            if p.get('affiliations'):
                author_affiliations.extend(p['affiliations'])
            if p.get('affiliation_countries'):
                author_countries.extend(p['affiliation_countries'])
            if p.get('author_orcids'):
                author_orcids.extend(p['author_orcids'])
        
        self.profile['unique_authors'] = len(set(all_authors))
        self.profile['unique_affiliations'] = len(set(author_affiliations))
        self.profile['unique_countries'] = len(set(author_countries))
        
        # Средние значения
        author_counts = [p.get('author_count', 0) for p in self.articles if p.get('author_count', 0) > 0]
        aff_counts = [p.get('affiliation_count', 0) for p in self.articles if p.get('affiliation_count', 0) > 0]
        country_counts = [p.get('country_count', 0) for p in self.articles if p.get('country_count', 0) > 0]
        
        self.profile['avg_authors_per_paper'] = np.mean(author_counts) if author_counts else 0
        self.profile['avg_affiliations_per_paper'] = np.mean(aff_counts) if aff_counts else 0
        self.profile['avg_countries_per_paper'] = np.mean(country_counts) if country_counts else 0
        
        # Топ авторы
        self.profile['top_authors'] = dict(Counter(all_authors).most_common(20))
        
        # Топ аффилиации
        self.profile['top_affiliations'] = dict(Counter(author_affiliations).most_common(20))
        
        # Топ страны
        self.profile['top_countries'] = dict(Counter(author_countries).most_common(20))
        
        # Самые цитируемые статьи
        sorted_pubs = sorted(self.articles, key=lambda x: x.get('cited_by_count', 0), reverse=True)
        self.profile['most_cited'] = [
            {
                'title': p.get('title', 'No title'),
                'citations': p.get('cited_by_count', 0),
                'year': p.get('publication_year', 'Unknown'),
                'journal': p.get('journal_name', 'Unknown'),
                'doi': p.get('doi', ''),
                'authors': p.get('authors', [])
            }
            for p in sorted_pubs[:10]
        ]
        
        # International Collaboration Rate
        international_papers = 0
        for p in self.articles:
            countries = set(p.get('affiliation_countries', []))
            if len(countries) > 1:
                international_papers += 1
        self.profile['international_collaboration_rate'] = international_papers / len(self.articles) if self.articles else 0
        
        # ====== Анализ коллабораций ======
        self._analyze_collaborations()
        
        # ====== Тематический анализ ======
        self._analyze_topics()
        
        # ====== Цитационный анализ ======
        self._analyze_citations()
        
        # ====== Детальные цитирования ======
        self._build_detailed_citations()
        
        print("✅ Анализ завершен!")
    
    def _analyze_collaborations(self):
        """Анализирует коллаборации"""
        collaborations = {
            'single_country': 0,
            'international': 0,
            'country_pairs': defaultdict(int)
        }
        
        # Countries per publication (уникальные страны на публикацию)
        countries_per_pub = []
        # Authors per country (индивидуальное распределение)
        authors_per_country = defaultdict(int)
        
        for p in self.articles:
            countries = set(p.get('affiliation_countries', []))
            countries_per_pub.append(len(countries))
            
            # Authors per country
            for auth in p.get('authors_with_orcids', []):
                # Пытаемся определить страну автора
                author_country = 'Unknown'
                # Ищем аффилиации автора
                for inst in p.get('institutions', []):
                    if inst.get('display_name') in p.get('affiliations', []):
                        country_code = inst.get('country_code', '')
                        if country_code:
                            author_country = get_full_country_name(country_code)
                            break
                authors_per_country[author_country] += 1
            
            if len(countries) <= 1:
                collaborations['single_country'] += 1
            else:
                collaborations['international'] += 1
                
                # Пары стран
                country_list = sorted(list(countries))
                for i in range(len(country_list)):
                    for j in range(i+1, len(country_list)):
                        pair = f"{country_list[i]}-{country_list[j]}"
                        collaborations['country_pairs'][pair] += 1
        
        self.profile['collaborations'] = collaborations
        self.profile['countries_per_pub_avg'] = np.mean(countries_per_pub) if countries_per_pub else 0
        self.profile['authors_per_country'] = dict(authors_per_country)
    
    def _analyze_topics(self):
        """Анализирует тематическую структуру"""
        topics_data = defaultdict(lambda: {
            'analyzed_count': 0,
            'citing_count': 0,
            'first_year': None,
            'peak_year': None,
            'year_counts': defaultdict(int),
            'citing_year_counts': defaultdict(int)
        })
        
        # Анализируемые статьи
        for p in self.articles:
            year = p.get('publication_year')
            if not year:
                continue
            
            # Topics
            for t in p.get('topics', []):
                topic_name = t.get('display_name', '')
                if topic_name:
                    topics_data[topic_name]['analyzed_count'] += 1
                    if topics_data[topic_name]['first_year'] is None or year < topics_data[topic_name]['first_year']:
                        topics_data[topic_name]['first_year'] = year
                    topics_data[topic_name]['year_counts'][year] += 1
        
        # Цитирующие работы
        for doi, citing_dois in self.citing_map.items():
            # Находим анализируемую статью по DOI
            citing_metadata = self.citing_metadata.get(doi, {})
            citing_year = citing_metadata.get('publication_year')
            if not citing_year:
                continue
            
            # Находим темы анализируемой статьи
            for p in self.articles:
                if p.get('doi') == doi:
                    for t in p.get('topics', []):
                        topic_name = t.get('display_name', '')
                        if topic_name:
                            topics_data[topic_name]['citing_count'] += 1
                            topics_data[topic_name]['citing_year_counts'][citing_year] += 1
                    break
        
        # Расчет нормализованных значений
        total_analyzed = len(self.articles)
        total_citing = sum(len(c) for c in self.citing_map.values())
        
        for topic, data in topics_data.items():
            data['analyzed_norm'] = data['analyzed_count'] / total_analyzed if total_analyzed > 0 else 0
            data['citing_norm'] = data['citing_count'] / total_citing if total_citing > 0 else 0
            data['total_norm'] = data['analyzed_norm'] + data['citing_norm']
            
            # Peak year
            if data['year_counts']:
                data['peak_year'] = max(data['year_counts'].items(), key=lambda x: x[1])[0]
            elif data['citing_year_counts']:
                data['peak_year'] = max(data['citing_year_counts'].items(), key=lambda x: x[1])[0]
        
        self.profile['topics_data'] = dict(topics_data)
        
        # Топ темы
        sorted_topics = sorted(
            topics_data.items(),
            key=lambda x: x[1]['total_norm'],
            reverse=True
        )
        self.profile['top_topics'] = sorted_topics[:10]
        
        # Сбор Subtopics, Fields, Domains, Concepts
        subtopics_data = defaultdict(lambda: {'analyzed': 0, 'citing': 0})
        fields_data = defaultdict(lambda: {'analyzed': 0, 'citing': 0})
        domains_data = defaultdict(lambda: {'analyzed': 0, 'citing': 0})
        concepts_data = defaultdict(lambda: {'analyzed': 0, 'citing': 0})
        
        for p in self.articles:
            for subtopic in p.get('subtopics', []):
                subtopics_data[subtopic]['analyzed'] += 1
            for field in p.get('fields', []):
                fields_data[field]['analyzed'] += 1
            for domain in p.get('domains', []):
                domains_data[domain]['analyzed'] += 1
            for concept in p.get('concepts', []):
                concepts_data[concept]['analyzed'] += 1
        
        # Цитирующие
        for doi, citing_dois in self.citing_map.items():
            citing_metadata = self.citing_metadata.get(doi, {})
            for subtopic in citing_metadata.get('subtopics', []):
                subtopics_data[subtopic]['citing'] += 1
            for field in citing_metadata.get('fields', []):
                fields_data[field]['citing'] += 1
            for domain in citing_metadata.get('domains', []):
                domains_data[domain]['citing'] += 1
            for concept in citing_metadata.get('concepts', []):
                concepts_data[concept]['citing'] += 1
        
        self.profile['subtopics_data'] = dict(subtopics_data)
        self.profile['fields_data'] = dict(fields_data)
        self.profile['domains_data'] = dict(domains_data)
        self.profile['concepts_data'] = dict(concepts_data)
        
        # Топ списки
        self.profile['top_subtopics'] = sorted(
            subtopics_data.items(),
            key=lambda x: x[1]['analyzed'] + x[1]['citing'],
            reverse=True
        )[:10]
        self.profile['top_fields'] = sorted(
            fields_data.items(),
            key=lambda x: x[1]['analyzed'] + x[1]['citing'],
            reverse=True
        )[:10]
        self.profile['top_domains'] = sorted(
            domains_data.items(),
            key=lambda x: x[1]['analyzed'] + x[1]['citing'],
            reverse=True
        )[:10]
        self.profile['top_concepts'] = sorted(
            concepts_data.items(),
            key=lambda x: x[1]['analyzed'] + x[1]['citing'],
            reverse=True
        )[:10]
    
    def _analyze_citations(self):
        """Анализирует цитирования"""
        # Citation Dynamics by Year
        dynamics = defaultdict(lambda: defaultdict(int))
        
        for doi, citing_dois in self.citing_map.items():
            # Находим год публикации анализируемой статьи
            pub_year = None
            for p in self.articles:
                if p.get('doi') == doi:
                    pub_year = p.get('publication_year')
                    break
            
            if not pub_year:
                continue
            
            for citing_doi in citing_dois:
                citing_metadata = self.citing_metadata.get(citing_doi, {})
                citing_year = citing_metadata.get('publication_year')
                if citing_year:
                    dynamics[pub_year][citing_year] += 1
        
        self.citation_dynamics = []
        for pub_year, cite_years in dynamics.items():
            for cite_year, count in cite_years.items():
                self.citation_dynamics.append({
                    'publication_year': pub_year,
                    'citation_year': cite_year,
                    'citations_count': count
                })
        
        self.heatmap_data = dict(dynamics)
        
        # Cumulative Citations
        cumulative = defaultdict(int)
        all_years = sorted(set(
            [d['citation_year'] for d in self.citation_dynamics] +
            [d['publication_year'] for d in self.citation_dynamics]
        ))
        
        running_total = 0
        for year in all_years:
            year_total = sum(d['citations_count'] for d in self.citation_dynamics if d['citation_year'] == year)
            running_total += year_total
            cumulative[year] = running_total
        
        self.cumulative_citations = [
            {'year': year, 'total': total}
            for year, total in sorted(cumulative.items())
        ]
    
    def _build_detailed_citations(self):
        """Строит детальные цитирования для каждой анализируемой статьи"""
        for p in self.articles:
            doi = p.get('doi')
            if not doi:
                continue
            
            citing_dois = self.citing_map.get(doi, [])
            if not citing_dois:
                continue
            
            citations_list = []
            for citing_doi in citing_dois:
                cite = self.citing_metadata.get(citing_doi, {})
                if not cite:
                    continue
                
                citation_lag = cite.get('publication_year') - p.get('publication_year') if cite.get('publication_year') and p.get('publication_year') else None
                
                citations_list.append({
                    'citing_title': cite.get('title', 'No title'),
                    'citing_year': cite.get('publication_year'),
                    'citing_date': cite.get('publication_date'),
                    'citing_journal': cite.get('journal_name', 'Unknown'),
                    'citing_publisher': cite.get('publisher', 'Unknown'),
                    'citing_doi': citing_doi,
                    'citation_lag': citation_lag,
                    'citing_authors': cite.get('authors', []),
                    'citing_countries': cite.get('affiliation_countries', []),
                    'citing_topics': [t.get('display_name', '') for t in cite.get('topics', []) if t.get('display_name')]
                })
            
            self.detailed_citations[doi] = {
                'title': p.get('title', 'No title'),
                'year': p.get('publication_year'),
                'doi': doi,
                'total_citations': len(citations_list),
                'citations': citations_list
            }
    
    def get_profile_data(self) -> Dict:
        """Возвращает полный профиль"""
        return self.profile
    
    def get_articles(self) -> List[Dict]:
        """Возвращает список статей"""
        return self.articles
    
    def get_citing_map(self) -> Dict:
        """Возвращает карту цитирований"""
        return self.citing_map
    
    def get_citing_metadata(self) -> Dict:
        """Возвращает метаданные цитирующих работ"""
        return self.citing_metadata
    
    def get_citation_dynamics(self) -> List[Dict]:
        """Возвращает динамику цитирований"""
        return self.citation_dynamics
    
    def get_cumulative_citations(self) -> List[Dict]:
        """Возвращает накопленные цитирования"""
        return self.cumulative_citations
    
    def get_heatmap_data(self) -> Dict:
        """Возвращает данные для тепловой карты"""
        return self.heatmap_data
    
    def get_detailed_citations(self) -> Dict:
        """Возвращает детальные цитирования"""
        return self.detailed_citations

# ============================================
# ФУНКЦИИ ДЛЯ ПОЛУЧЕНИЯ ДАННЫХ ИЗ API (ЖУРНАЛЫ)
# ============================================

def get_journal_articles(issn: str, period: Any, max_articles: int = MAX_PUBLICATIONS_TO_ANALYZE, progress_callback=None) -> List[Dict]:
    """
    Получает все статьи журнала за указанный период
    
    Args:
        issn: ISSN журнала
        period: Период (int, list или tuple)
        max_articles: Максимальное количество статей
        progress_callback: Функция обратного вызова для прогресса
    
    Returns:
        List[Dict]: Список статей
    """
    normalized = normalize_issn(issn)
    
    if SHOW_DEBUG_LOGS:
        print(f"🔍 Получение статей для ISSN: {normalized}")
    
    base_url = "https://api.openalex.org/works"
    
    # Формируем фильтр по году
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
        
        params = {
            'filter': f"primary_location.source.issn:{normalized},{year_filter}",
            'per_page': 200,
            'select': "id,doi,publication_year,cited_by_count,title,type,raw_type,primary_location,authorships,open_access,topics,concepts,keywords",
            'cursor': cursor
        }
        
        data = smart_get(base_url, params)
        
        if not data or not data.get('results'):
            break
        
        for work in data['results']:
            parsed = parse_openalex_publication(work)
            if parsed:
                articles.append(parsed)
                if len(articles) >= max_articles:
                    if SHOW_DEBUG_LOGS:
                        print(f"⚠️ Достигнут лимит {max_articles} статей")
                    return articles
        
        if progress_callback:
            progress_callback(page_count, len(articles))
        
        cursor = data.get('meta', {}).get('next_cursor')
        if not cursor:
            break
    
    if SHOW_DEBUG_LOGS:
        print(f"✅ Получено {len(articles)} статей")
    
    return articles

def get_citing_works_parallel(articles: List[Dict], max_workers: int = MAX_WORKERS, progress_callback=None) -> Dict:
    """
    Параллельный сбор цитирующих работ для списка статей
    
    Args:
        articles: Список статей
        max_workers: Количество потоков
        progress_callback: Функция обратного вызова для прогресса
    
    Returns:
        Dict: {doi: [список цитирующих DOI]}
    """
    if not articles:
        return {}
    
    if SHOW_DEBUG_LOGS:
        print(f"⚡ Параллельный сбор цитирующих DOI ({max_workers} потоков)...")
    
    citing_map = {}
    futures = {}
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for article in articles:
            doi = article.get('doi')
            oa_id = article.get('id', '').replace('https://openalex.org/', '')
            if doi and doi != 'N/A' and oa_id:
                future = executor.submit(get_citing_dois, oa_id, MAX_CITING_PER_PAPER)
                futures[future] = doi
        
        total = len(futures)
        completed = 0
        
        for future in as_completed(futures):
            doi = futures[future]
            try:
                citing_map[doi] = future.result()
            except Exception as e:
                if SHOW_DEBUG_LOGS:
                    print(f"⚠️ Ошибка для {doi}: {e}")
                citing_map[doi] = []
            
            completed += 1
            if progress_callback:
                progress_callback(completed, total)
    
    if SHOW_DEBUG_LOGS:
        total_citing = sum(len(v) for v in citing_map.values())
        print(f"✅ Собрано {total_citing} цитирующих работ")
    
    return citing_map

def fetch_citing_metadata_parallel(citing_map: Dict, max_workers: int = MAX_WORKERS, progress_callback=None) -> Dict:
    """
    Параллельный сбор метаданных для цитирующих работ
    
    Args:
        citing_map: {doi: [список цитирующих DOI]}
        max_workers: Количество потоков
        progress_callback: Функция обратного вызова для прогресса
    
    Returns:
        Dict: {doi: метаданные}
    """
    # Собираем все уникальные цитирующие DOI
    all_citing_dois = set()
    for citing_list in citing_map.values():
        all_citing_dois.update(citing_list)
    
    if not all_citing_dois:
        return {}
    
    if SHOW_DEBUG_LOGS:
        print(f"📖 Получение метаданных для {len(all_citing_dois)} цитирующих работ...")
    
    metadata = {}
    futures = {}
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for doi in all_citing_dois:
            future = executor.submit(fetch_work_metadata, doi)
            futures[future] = doi
        
        total = len(futures)
        completed = 0
        
        for future in as_completed(futures):
            doi = futures[future]
            try:
                data = future.result()
                if data:
                    parsed = parse_openalex_publication(data)
                    if parsed:
                        metadata[doi] = parsed
            except Exception as e:
                if SHOW_DEBUG_LOGS:
                    print(f"⚠️ Ошибка для {doi}: {e}")
            
            completed += 1
            if progress_callback:
                progress_callback(completed, total)
    
    if SHOW_DEBUG_LOGS:
        print(f"✅ Получено метаданных для {len(metadata)} цитирующих работ")
    
    return metadata

# ============================================
# ОСНОВНАЯ ФУНКЦИЯ СБОРА ДАННЫХ (ЖУРНАЛ)
# ============================================

def collect_journal_data(issn: str, period: Any, max_workers: int = MAX_WORKERS, progress_callback=None) -> Tuple[JournalAnalyzer, Dict, List[Dict]]:
    """
    Собирает все данные для анализа журнала
    
    Args:
        issn: ISSN журнала
        period: Период (int, list или tuple)
        max_workers: Количество потоков
        progress_callback: Функция обратного вызова для прогресса
    
    Returns:
        Tuple[JournalAnalyzer, Dict, List[Dict]]
    """
    normalized = normalize_issn(issn)
    
    if not normalized:
        print(f"❌ Неверный формат ISSN: {issn}")
        return None, {}, []
    
    print(f"🚀 Начинаем сбор данных для ISSN: {normalized}")
    
    # Создаем анализатор
    analyzer = JournalAnalyzer(normalized, period)
    
    # Этап 1: Получение статей журнала
    if progress_callback:
        progress_callback('articles', 0, 100)
    
    articles = get_journal_articles(normalized, period, MAX_PUBLICATIONS_TO_ANALYZE)
    
    if not articles:
        print("❌ Не найдено статей для журнала")
        return analyzer, {}, []
    
    for article in articles:
        analyzer.add_article(article)
    
    if progress_callback:
        progress_callback('articles', 100, 100)
    
    # Этап 2: Параллельный сбор цитирующих DOI
    if progress_callback:
        progress_callback('citing', 0, 100)
    
    citing_map = get_citing_works_parallel(articles, max_workers)
    analyzer.set_citing_map(citing_map)
    
    if progress_callback:
        progress_callback('citing', 100, 100)
    
    # Этап 3: Получение метаданных цитирующих работ
    if progress_callback:
        progress_callback('metadata', 0, 100)
    
    citing_metadata = fetch_citing_metadata_parallel(citing_map, max_workers)
    analyzer.set_citing_metadata(citing_metadata)
    
    if progress_callback:
        progress_callback('metadata', 100, 100)
    
    # Этап 4: Анализ
    if progress_callback:
        progress_callback('analysis', 0, 100)
    
    analyzer.analyze_publications()
    
    if progress_callback:
        progress_callback('analysis', 100, 100)
    
    print(f"✅ Сбор данных завершен для {normalized}")
    
    return analyzer, analyzer.get_profile_data(), analyzer.get_articles()

# ============================================
# ФУНКЦИИ ДЛЯ АНАЛИЗА МНОЖЕСТВЕННЫХ ЖУРНАЛОВ
# ============================================

def analyze_multiple_journals(issn_list: List[str], period: Any, progress_callback=None, max_workers: int = MAX_WORKERS) -> List[Dict]:
    """Анализирует несколько журналов"""
    results = []
    total = len(issn_list)
    
    for idx, issn in enumerate(issn_list):
        if progress_callback:
            progress_callback(idx + 1, total, issn)
        
        analyzer, profile, articles = collect_journal_data(issn, period, max_workers)
        if profile:
            results.append({
                'issn': issn,
                'analyzer': analyzer,
                'profile': profile,
                'articles': articles,
                'journal_name': profile.get('journal_name', 'Unknown'),
                'h_index': profile.get('h_index', 0),
                'total_publications': profile.get('total_publications', 0),
                'total_citations': profile.get('total_citations', 0)
            })
    
    return results

def sort_journals_by_h_index(journals: List[Dict]) -> List[Dict]:
    """Сортирует журналы по убыванию h-index"""
    return sorted(journals, key=lambda x: x.get('h_index', 0), reverse=True)

# ============================================
# ФУНКЦИИ ДЛЯ ГЕНЕРАЦИИ ОТЧЕТОВ (ЖУРНАЛ)
# ============================================

def generate_journal_html_report(analyzer: JournalAnalyzer, profile: Dict, articles: List[Dict], 
                                 logo_base64: Optional[str] = None, app_logo_base64: Optional[str] = None,
                                 theme_colors: Optional[Dict] = None, lang: str = 'en') -> str:
    """Генерирует HTML отчет для журнала"""
    
    if theme_colors is None:
        theme_colors = {
            'primary': '#667eea',
            'secondary': '#f39c12'
        }
    
    primary = theme_colors.get('primary', '#667eea')
    secondary = theme_colors.get('secondary', '#f39c12')
    
    def t(key: str, **kwargs) -> str:
        return translate(key, lang, **kwargs)
    
    # Получаем данные для отчета
    total_pubs = profile.get('total_publications', 0)
    total_citations = profile.get('total_citations', 0)
    h_index = profile.get('h_index', 0)
    g_index = profile.get('g_index', 0)
    i10_index = profile.get('i10_index', 0)
    i100_index = profile.get('i100_index', 0)
    avg_citations = profile.get('average_citations', 0)
    oa_percentage = profile.get('oa_percentage', 0)
    active_years = profile.get('active_years', 0)
    
    unique_authors = profile.get('unique_authors', 0)
    unique_affiliations = profile.get('unique_affiliations', 0)
    unique_countries = profile.get('unique_countries', 0)
    
    avg_authors = profile.get('avg_authors_per_paper', 0)
    avg_affiliations = profile.get('avg_affiliations_per_paper', 0)
    avg_countries = profile.get('avg_countries_per_paper', 0)
    international_rate = profile.get('international_collaboration_rate', 0) * 100
    
    # Open Access Breakdown
    oa_types = profile.get('oa_types', {})
    oa_labels = {
        'gold': t('gold'),
        'hybrid': t('hybrid'),
        'green': t('green'),
        'bronze': t('bronze'),
        'closed': t('closed'),
        'unknown': t('unknown')
    }
    
    # Top authors
    top_authors = profile.get('top_authors', {})
    top_affiliations = profile.get('top_affiliations', {})
    
    # Geographic analysis
    collaborations = profile.get('collaborations', {})
    countries_per_pub_avg = profile.get('countries_per_pub_avg', 0)
    authors_per_country = profile.get('authors_per_country', {})
    country_pairs = collaborations.get('country_pairs', {})
    
    # Citation dynamics
    citation_dynamics = analyzer.get_citation_dynamics()
    cumulative_citations = analyzer.get_cumulative_citations()
    heatmap_data = analyzer.get_heatmap_data()
    
    # Most cited
    most_cited = profile.get('most_cited', [])
    
    # Citing works stats
    citing_map = analyzer.get_citing_map()
    citing_metadata = analyzer.get_citing_metadata()
    
    total_citing_works = sum(len(v) for v in citing_map.values())
    
    # Unique citing authors, affiliations, countries, journals, publishers
    citing_authors = set()
    citing_affiliations = set()
    citing_countries = set()
    citing_journals = set()
    citing_publishers = set()
    
    for metadata in citing_metadata.values():
        for author in metadata.get('authors', []):
            citing_authors.add(author)
        for aff in metadata.get('affiliations', []):
            citing_affiliations.add(aff)
        for country in metadata.get('affiliation_countries', []):
            citing_countries.add(country)
        if metadata.get('journal_name'):
            citing_journals.add(metadata['journal_name'])
        if metadata.get('publisher'):
            citing_publishers.add(metadata['publisher'])
    
    unique_citing_authors = len(citing_authors)
    unique_citing_affiliations = len(citing_affiliations)
    unique_citing_countries = len(citing_countries)
    unique_citing_journals = len(citing_journals)
    unique_citing_publishers = len(citing_publishers)
    
    # Top citing authors
    citing_authors_counter = Counter()
    for metadata in citing_metadata.values():
        for author in metadata.get('authors', []):
            citing_authors_counter[author] += 1
    
    top_citing_authors = dict(citing_authors_counter.most_common(20))
    
    # Top citing affiliations
    citing_affiliations_counter = Counter()
    for metadata in citing_metadata.values():
        for aff in metadata.get('affiliations', []):
            citing_affiliations_counter[aff] += 1
    
    top_citing_affiliations = dict(citing_affiliations_counter.most_common(20))
    
    # Top citing countries
    citing_countries_counter = Counter()
    for metadata in citing_metadata.values():
        for country in metadata.get('affiliation_countries', []):
            citing_countries_counter[country] += 1
    
    top_citing_countries = dict(citing_countries_counter.most_common(20))
    
    # Top citing journals
    citing_journals_counter = Counter()
    for metadata in citing_metadata.values():
        if metadata.get('journal_name'):
            citing_journals_counter[metadata['journal_name']] += 1
    
    top_citing_journals = dict(citing_journals_counter.most_common(20))
    
    # Top citing publishers
    citing_publishers_counter = Counter()
    for metadata in citing_metadata.values():
        if metadata.get('publisher'):
            citing_publishers_counter[metadata['publisher']] += 1
    
    top_citing_publishers = dict(citing_publishers_counter.most_common(20))
    
    # Topics data
    topics_data = profile.get('topics_data', {})
    top_topics = profile.get('top_topics', [])
    top_subtopics = profile.get('top_subtopics', [])
    top_fields = profile.get('top_fields', [])
    top_domains = profile.get('top_domains', [])
    top_concepts = profile.get('top_concepts', [])
    
    # Detailed citations
    detailed_citations = analyzer.get_detailed_citations()
    
    # All publications for table
    all_publications = sorted(articles, key=lambda x: x.get('publication_year', 0), reverse=True)
    
    # Генерация таблицы авторов
    authors_html = ""
    if top_authors:
        author_rows = []
        for rank, (name, count) in enumerate(top_authors.items(), 1):
            # Находим ORCID для автора
            orcid = ""
            for p in articles:
                for auth in p.get('authors_with_orcids', []):
                    if auth.get('name') == name and auth.get('orcid'):
                        orcid = auth['orcid']
                        break
                if orcid:
                    break
            
            # Находим аффилиации и страны автора
            author_affs = set()
            author_countries_set = set()
            for p in articles:
                for auth in p.get('authors_with_orcids', []):
                    if auth.get('name') == name:
                        for inst in p.get('institutions', []):
                            if inst.get('display_name') in p.get('affiliations', []):
                                author_affs.add(inst.get('display_name', ''))
                                country_code = inst.get('country_code', '')
                                if country_code:
                                    author_countries_set.add(get_full_country_name(country_code))
            
            # Подсчет публикаций и цитирований автора
            pub_count = 0
            cite_count = 0
            for p in articles:
                if name in p.get('authors', []):
                    pub_count += 1
                    cite_count += p.get('cited_by_count', 0)
            
            author_rows.append({
                'rank': rank,
                'name': name,
                'orcid': orcid,
                'affiliations': ', '.join(list(author_affs)[:3]) + ('...' if len(author_affs) > 3 else ''),
                'countries': ', '.join(list(author_countries_set)[:3]) + ('...' if len(author_countries_set) > 3 else ''),
                'publications': pub_count,
                'citations': cite_count
            })
        
        for row in author_rows[:20]:
            orcid_link = f'<a href="https://orcid.org/{row["orcid"]}" target="_blank">{row["orcid"]}</a>' if row['orcid'] else ''
            authors_html += f"""
            <tr>
                <td>{row['rank']}</td>
                <td>{html.escape(row['name'])}</td>
                <td>{orcid_link}</td>
                <td>{html.escape(row['affiliations'])}</td>
                <td>{html.escape(row['countries'])}</td>
                <td>{row['publications']}</td>
                <td>{row['citations']}</td>
            </tr>
            """
    
    # Генерация таблицы топ аффилиаций
    affiliations_html = ""
    if top_affiliations:
        for rank, (aff, count) in enumerate(top_affiliations.items(), 1):
            affiliations_html += f"""
            <tr>
                <td>{rank}</td>
                <td>{html.escape(aff)}</td>
                <td>{count}</td>
            </tr>
            """
    
    # Географический анализ
    countries_per_pub_html = ""
    if authors_per_country:
        for country, count in sorted(authors_per_country.items(), key=lambda x: x[1], reverse=True)[:20]:
            countries_per_pub_html += f"""
            <tr>
                <td>{html.escape(country)}</td>
                <td>{count}</td>
            </tr>
            """
    
    # Паттерны коллабораций
    single_country = collaborations.get('single_country', 0)
    international = collaborations.get('international', 0)
    total_collab = single_country + international
    
    # Пары стран
    country_pairs_html = ""
    if country_pairs:
        for pair, count in sorted(country_pairs.items(), key=lambda x: x[1], reverse=True)[:20]:
            country1, country2 = pair.split('-')
            country1_full = get_full_country_name(country1)
            country2_full = get_full_country_name(country2)
            country_pairs_html += f"""
            <tr>
                <td>{html.escape(country1_full)}</td>
                <td>{html.escape(country2_full)}</td>
                <td>{count}</td>
            </tr>
            """
    
    # Динамика цитирований
    dynamics_html = ""
    for d in sorted(citation_dynamics, key=lambda x: (x['publication_year'], x['citation_year'])):
        dynamics_html += f"""
        <tr>
            <td>{d['publication_year']}</td>
            <td>{d['citation_year']}</td>
            <td>{d['citations_count']}</td>
        </tr>
        """
    
    # Накопленные цитирования
    cumulative_html = ""
    for c in cumulative_citations:
        cumulative_html += f"""
        <tr>
            <td>{c['year']}</td>
            <td>{c['total']}</td>
        </tr>
        """
    
    # Тепловая карта
    heatmap_html = ""
    if heatmap_data:
        all_pub_years = sorted(heatmap_data.keys())
        all_cite_years = sorted(set().union(*[set(v.keys()) for v in heatmap_data.values()]))
        
        heatmap_html += "<table class='heatmap-table'><thead><tr><th>Publication Year \\ Citation Year</th>"
        for cite_year in all_cite_years:
            heatmap_html += f"<th>{cite_year}</th>"
        heatmap_html += "</tr></thead><tbody>"
        
        for pub_year in all_pub_years:
            heatmap_html += f"<tr><td><strong>{pub_year}</strong></td>"
            cite_data = heatmap_data.get(pub_year, {})
            for cite_year in all_cite_years:
                count = cite_data.get(cite_year, 0)
                # Определяем цвет ячейки на основе количества
                max_count = max([max(v.values()) for v in heatmap_data.values()] + [1])
                intensity = count / max_count if max_count > 0 else 0
                if intensity > 0:
                    r, g, b = hex_to_rgb(primary)
                    color = f"rgba({r}, {g}, {b}, {0.2 + intensity * 0.7})"
                else:
                    color = "rgba(200, 200, 200, 0.3)"
                heatmap_html += f"<td style='background-color: {color}; text-align: center;'>{count if count > 0 else '-'}</td>"
            heatmap_html += "</tr>"
        
        heatmap_html += "</tbody></table>"
    
    # Самые цитируемые публикации
    most_cited_html = ""
    for rank, pub in enumerate(most_cited[:10], 1):
        authors_str = ', '.join(pub.get('authors', [])[:4])
        if len(pub.get('authors', [])) > 4:
            authors_str += ' +' + str(len(pub.get('authors', [])) - 4) + ' more'
        citations_per_year = pub.get('citations') / (2026 - pub.get('year') + 1) if pub.get('year') else 0
        
        most_cited_html += f"""
        <tr>
            <td>{rank}</td>
            <td>{html.escape(pub.get('title', 'No title'))}</td>
            <td>{pub.get('year', 'N/A')}</td>
            <td>{pub.get('citations', 0)}</td>
            <td>{citations_per_year:.1f}</td>
            <td>{html.escape(authors_str)}</td>
            <td><a href="https://doi.org/{pub.get('doi', '')}" target="_blank" class="doi-link">{pub.get('doi', '')}</a></td>
        </tr>
        """
    
    # Топ цитирующие авторы
    top_citing_authors_html = ""
    for rank, (name, count) in enumerate(top_citing_authors.items(), 1):
        top_citing_authors_html += f"""
        <tr>
            <td>{rank}</td>
            <td>{html.escape(name)}</td>
            <td>{count}</td>
        </tr>
        """
    
    # Топ цитирующие аффилиации
    top_citing_affiliations_html = ""
    for rank, (aff, count) in enumerate(top_citing_affiliations.items(), 1):
        top_citing_affiliations_html += f"""
        <tr>
            <td>{rank}</td>
            <td>{html.escape(aff)}</td>
            <td>{count}</td>
        </tr>
        """
    
    # Топ цитирующие страны
    top_citing_countries_html = ""
    for rank, (country, count) in enumerate(top_citing_countries.items(), 1):
        top_citing_countries_html += f"""
        <tr>
            <td>{rank}</td>
            <td>{html.escape(get_full_country_name(country))}</td>
            <td>{count}</td>
        </tr>
        """
    
    # Топ цитирующие журналы
    top_citing_journals_html = ""
    for rank, (journal, count) in enumerate(top_citing_journals.items(), 1):
        top_citing_journals_html += f"""
        <tr>
            <td>{rank}</td>
            <td>{html.escape(journal)}</td>
            <td>{count}</td>
        </tr>
        """
    
    # Топ цитирующие издатели
    top_citing_publishers_html = ""
    for rank, (publisher, count) in enumerate(top_citing_publishers.items(), 1):
        top_citing_publishers_html += f"""
        <tr>
            <td>{rank}</td>
            <td>{html.escape(publisher)}</td>
            <td>{count}</td>
        </tr>
        """
    
    # Тематический анализ
    topics_overview_html = ""
    for topic, data in top_topics:
        topics_overview_html += f"""
        <tr>
            <td>{html.escape(topic)}</td>
            <td>{data['analyzed_count']}</td>
            <td>{data['citing_count']}</td>
            <td>{data['analyzed_norm']:.3f}</td>
            <td>{data['citing_norm']:.3f}</td>
            <td>{data['total_norm']:.3f}</td>
            <td>{data['first_year'] or 'N/A'}</td>
            <td>{data['peak_year'] or 'N/A'}</td>
        </tr>
        """
    
    # Топ Subtopics, Fields, Domains, Concepts
    top_subtopics_html = ""
    for item in top_subtopics[:10]:
        name, data = item
        total = data.get('analyzed', 0) + data.get('citing', 0)
        top_subtopics_html += f"""
        <tr>
            <td>{html.escape(name)}</td>
            <td>{data.get('analyzed', 0)}</td>
            <td>{data.get('citing', 0)}</td>
            <td>{total}</td>
        </tr>
        """
    
    top_fields_html = ""
    for item in top_fields[:10]:
        name, data = item
        total = data.get('analyzed', 0) + data.get('citing', 0)
        top_fields_html += f"""
        <tr>
            <td>{html.escape(name)}</td>
            <td>{data.get('analyzed', 0)}</td>
            <td>{data.get('citing', 0)}</td>
            <td>{total}</td>
        </tr>
        """
    
    top_domains_html = ""
    for item in top_domains[:10]:
        name, data = item
        total = data.get('analyzed', 0) + data.get('citing', 0)
        top_domains_html += f"""
        <tr>
            <td>{html.escape(name)}</td>
            <td>{data.get('analyzed', 0)}</td>
            <td>{data.get('citing', 0)}</td>
            <td>{total}</td>
        </tr>
        """
    
    top_concepts_html = ""
    for item in top_concepts[:10]:
        name, data = item
        total = data.get('analyzed', 0) + data.get('citing', 0)
        top_concepts_html += f"""
        <tr>
            <td>{html.escape(name)}</td>
            <td>{data.get('analyzed', 0)}</td>
            <td>{data.get('citing', 0)}</td>
            <td>{total}</td>
        </tr>
        """
    
    # Детальные цитирования
    detailed_citations_html = ""
    for pub_id, data in detailed_citations.items():
        pub_id_clean = pub_id.replace('https://doi.org/', '').replace('/', '_')
        detailed_citations_html += f"""
        <div class="collapser" onclick="toggleCitations('{pub_id_clean}')">
            <strong>{html.escape(data['title'][:100])}</strong>
            <span class="badge badge-info">{data['year']}</span>
            <span class="citation-count">{data['total_citations']} citations</span>
            <span style="font-size: 12px; color: #666; margin-left: 10px;">DOI: {data['doi']}</span>
            <span style="float: right; font-size: 12px; color: #666;">Click to toggle citations</span>
        </div>
        <div id="citations_{pub_id_clean}" style="display: none;">
        """
        
        for cite in data['citations']:
            detailed_citations_html += f"""
            <div class="citation-detail">
                <div><strong>{html.escape(cite['citing_title'][:100])}</strong></div>
                <div class="cite-meta">
                    <strong>{t('citing_journal')}:</strong> {html.escape(cite['citing_journal'])} | 
                    <strong>{t('citing_year')}:</strong> {cite['citing_year'] or 'N/A'} | 
                    <strong>{t('citing_date')}:</strong> {cite['citing_date'] or 'N/A'} |
                    <strong>{t('citation_lag')}:</strong> {cite['citation_lag'] or 'N/A'} years
                </div>
                <div class="cite-meta">
                    <strong>{t('authors')}:</strong> {', '.join(cite['citing_authors'][:5])}{'...' if len(cite['citing_authors']) > 5 else ''} |
                    <strong>{t('countries')}:</strong> {', '.join(cite['citing_countries'][:5])}{'...' if len(cite['citing_countries']) > 5 else ''} |
                    <strong>{t('topics')}:</strong> {', '.join(cite['citing_topics'][:5])}{'...' if len(cite['citing_topics']) > 5 else ''}
                </div>
                <div class="cite-meta">
                    <a href="https://doi.org/{cite['citing_doi']}" target="_blank" class="doi-link">DOI: {cite['citing_doi']}</a>
                </div>
            </div>
            """
        
        detailed_citations_html += "</div>"
    
    # Все публикации
    all_publications_html = ""
    for idx, p in enumerate(all_publications[:50], 1):
        authors_str = ', '.join(p.get('authors', [])[:3])
        if len(p.get('authors', [])) > 3:
            authors_str += f' +{len(p.get("authors", [])) - 3} more'
        
        all_publications_html += f"""
        <tr data-year="{p.get('publication_year', '')}" 
            data-authors="{','.join(p.get('authors', []))}" 
            data-citations="{p.get('cited_by_count', 0)}" 
            data-title="{p.get('title', '').lower()}" 
            data-doi="{p.get('doi', '').lower()}"
            data-affiliations="{','.join(p.get('affiliations', []))}">
            <td>{idx}</td>
            <td class="word-wrap">{html.escape(p.get('title', 'No title'))}</td>
            <td>{p.get('publication_year', 'N/A')}</td>
            <td>{', '.join(p.get('authors', [])[:5])}{'...' if len(p.get('authors', [])) > 5 else ''}</td>
            <td>{', '.join(p.get('affiliations', [])[:5])}{'...' if len(p.get('affiliations', [])) > 5 else ''}</td>
            <td><span class="citation-count">{p.get('cited_by_count', 0)}</span></td>
            <td>{p.get('citations_per_year', 0):.1f}</td>
            <td><a href="https://doi.org/{p.get('doi', '')}" target="_blank" class="doi-link">{p.get('doi', '')}</a></td>
        </tr>
        """
    
    # Формируем полный HTML отчет
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>{t('app_title')} - {profile.get('journal_name', 'Journal')}</title>
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
            .sidebar h2 {{
                color: white;
                margin-bottom: 25px;
                font-size: 20px;
                border-bottom: 2px solid rgba(255,255,255,0.3);
                padding-bottom: 15px;
            }}
            .sidebar h3 {{
                color: rgba(255,255,255,0.7);
                font-size: 13px;
                text-transform: uppercase;
                letter-spacing: 1px;
                margin: 20px 0 10px 0;
                padding-left: 10px;
                border-left: 3px solid rgba(255,255,255,0.3);
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
                opacity: 0.8;
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
                grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
                gap: 12px;
                margin: 15px 0;
            }}
            .metric-card {{
                background: #f8f9fa;
                padding: 15px;
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
                margin-top: 5px;
                font-family: 'Times New Roman', serif;
            }}
            .oa-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
                gap: 10px;
                margin: 15px 0;
            }}
            .oa-card {{
                background: #f8f9fa;
                padding: 12px;
                border-radius: 8px;
                text-align: center;
                border: 1px solid #e0e0e0;
            }}
            .oa-card .value {{
                font-size: 22px;
                font-weight: bold;
                color: #2C3E50;
            }}
            .oa-card .label {{
                font-size: 11px;
                color: #7F8C8D;
                margin-top: 3px;
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
                padding: 12px;
                text-align: left;
                position: sticky;
                top: 0;
                z-index: 10;
            }}
            td {{
                padding: 10px;
                border-bottom: 1px solid #BDC3C7;
            }}
            tr:hover {{
                background-color: #f5f5f5;
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
            .badge {{
                display: inline-block;
                padding: 3px 10px;
                border-radius: 15px;
                font-size: 11px;
                font-weight: 600;
                margin: 2px;
            }}
            .badge-info {{
                background: #d1ecf1;
                color: #0c5460;
            }}
            .citation-count {{
                background: {primary}20;
                padding: 2px 10px;
                border-radius: 12px;
                font-weight: 600;
                font-size: 13px;
                color: {primary};
            }}
            .collapser {{
                background: #f8f9fa;
                padding: 12px 15px;
                border-radius: 8px;
                margin-bottom: 8px;
                cursor: pointer;
                border-left: 4px solid {primary};
                transition: background 0.2s;
            }}
            .collapser:hover {{
                background: #e9ecef;
            }}
            .citation-detail {{
                background: #f8f9fa;
                padding: 12px 15px;
                margin: 5px 0 5px 20px;
                border-radius: 6px;
                border-left: 3px solid #6c757d;
            }}
            .cite-meta {{
                font-size: 12px;
                color: #555;
                margin-top: 4px;
            }}
            .heatmap-table {{
                width: 100%;
                border-collapse: collapse;
                font-size: 13px;
            }}
            .heatmap-table th {{
                background: linear-gradient(135deg, {primary} 0%, {secondary} 100%);
                color: white;
                padding: 8px;
                text-align: center;
            }}
            .heatmap-table td {{
                padding: 6px 10px;
                border: 1px solid #ddd;
                text-align: center;
                min-width: 40px;
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
                gap: 15px;
                align-items: center;
            }}
            .filter-row div {{
                display: flex;
                align-items: center;
                gap: 5px;
            }}
            .filter-row label {{
                font-size: 12px;
                font-weight: 600;
                color: #555;
            }}
            .filter-row select, .filter-row input {{
                padding: 5px 10px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 12px;
                font-family: 'Times New Roman', serif;
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
            }}
            .table-container table {{
                font-size: 13px;
            }}
            
            @media print {{
                .sidebar {{ display: none; }}
                .main-content {{ margin-left: 0; }}
            }}
            @media (max-width: 768px) {{
                .sidebar {{ display: none; }}
                .main-content {{ margin-left: 0; padding: 15px; }}
                .filter-row {{ flex-direction: column; align-items: stretch; }}
                .metrics-grid {{ grid-template-columns: repeat(2, 1fr); }}
            }}
        </style>
        <script>
            function toggleCitations(id) {{
                var el = document.getElementById('citations_' + id);
                if (el) {{
                    if (el.style.display === 'none' || el.style.display === '') {{
                        el.style.display = 'block';
                    }} else {{
                        el.style.display = 'none';
                    }}
                }}
            }}
            
            function filterPublications() {{
                var yearFilter = document.getElementById('yearFilter');
                var authorFilter = document.getElementById('authorFilter');
                var citationFilter = document.getElementById('citationFilter');
                var titleFilter = document.getElementById('titleFilter');
                var affiliationFilter = document.getElementById('affiliationFilter');
                var table = document.getElementById('publicationsTable');
                var rows = table.getElementsByTagName('tbody')[0].getElementsByTagName('tr');
                var visibleCount = 0;
                
                var yearVal = yearFilter ? yearFilter.value : '';
                var authorVal = authorFilter ? authorFilter.value.toLowerCase() : '';
                var citationVal = citationFilter ? parseInt(citationFilter.value) || 0 : 0;
                var titleVal = titleFilter ? titleFilter.value.toLowerCase() : '';
                var affiliationVal = affiliationFilter ? affiliationFilter.value.toLowerCase() : '';
                
                for (var i = 0; i < rows.length; i++) {{
                    var row = rows[i];
                    var year = row.getAttribute('data-year') || '';
                    var authors = row.getAttribute('data-authors') || '';
                    var citations = parseInt(row.getAttribute('data-citations')) || 0;
                    var title = row.getAttribute('data-title') || '';
                    var affiliations = row.getAttribute('data-affiliations') || '';
                    var show = true;
                    
                    if (yearVal && year != yearVal) show = false;
                    if (authorVal && authors.toLowerCase().indexOf(authorVal) === -1) show = false;
                    if (citationVal > 0 && citations < citationVal) show = false;
                    if (titleVal && title.indexOf(titleVal) === -1) show = false;
                    if (affiliationVal && affiliations.toLowerCase().indexOf(affiliationVal) === -1) show = false;
                    
                    row.style.display = show ? '' : 'none';
                    if (show) visibleCount++;
                }}
                
                var countEl = document.getElementById('visibleCount');
                if (countEl) {{
                    countEl.textContent = 'Showing ' + visibleCount + ' publications';
                }}
            }}
        </script>
    </head>
    <body>
        <!-- Sidebar Navigation -->
        <div class="sidebar">
            <h2>📊 {t('app_title')}</h2>
            <a href="#overview">📊 {t('overview')}</a>
            
            <h3>{t('analyzed_articles')}</h3>
            <a href="#author_analysis" class="level2">👤 {t('author_analysis')}</a>
            <a href="#top_affiliations" class="level2">🏛️ {t('top_affiliations')}</a>
            <a href="#geographic_analysis" class="level2">🌍 {t('geographic_analysis')}</a>
            <a href="#countries_per_pub" class="level2" style="padding-left: 45px; font-size: 12px;">└ {t('countries_per_publication')}</a>
            <a href="#authors_per_country" class="level2" style="padding-left: 45px; font-size: 12px;">└ {t('authors_per_country')}</a>
            <a href="#collaboration_patterns" class="level2" style="padding-left: 45px; font-size: 12px;">└ {t('collaboration_patterns')}</a>
            <a href="#collaboration_couples" class="level2" style="padding-left: 45px; font-size: 12px;">└ {t('collaboration_couples')}</a>
            
            <h3>{t('citation_analysis')}</h3>
            <a href="#citation_dynamics" class="level2">📈 {t('citation_dynamics')}</a>
            <a href="#cumulative_citations" class="level2">📊 {t('cumulative_citations')}</a>
            <a href="#citation_heatmap" class="level2">🔥 {t('citation_heatmap')}</a>
            <a href="#most_cited" class="level2">⭐ {t('most_cited_publications')}</a>
            
            <h3>{t('citing_works_analysis')}</h3>
            <a href="#top_citing_authors" class="level2">👤 {t('top_citing_authors')}</a>
            <a href="#top_citing_affiliations" class="level2">🏛️ {t('top_citing_affiliations')}</a>
            <a href="#top_citing_countries" class="level2">🌍 {t('top_citing_countries')}</a>
            <a href="#top_citing_journals" class="level2">📰 {t('top_citing_journals')}</a>
            <a href="#top_citing_publishers" class="level2">📚 {t('top_citing_publishers')}</a>
            
            <h3>{t('topics_analysis')}</h3>
            <a href="#topics_overview" class="level2">🏷️ {t('topics_overview')}</a>
            <a href="#top_subtopics" class="level2">📋 {t('top_subtopics')}</a>
            <a href="#top_fields" class="level2">📋 {t('top_fields')}</a>
            <a href="#top_domains" class="level2">📋 {t('top_domains')}</a>
            <a href="#top_concepts" class="level2">📋 {t('top_concepts')}</a>
            
            <a href="#detailed_citations">📋 {t('detailed_citations')}</a>
            <a href="#all_publications">📚 {t('all_publications')}</a>
        </div>
        
        <div class="main-content">
            <!-- Header -->
            <div class="header">
                {f'<img src="data:image/png;base64,{app_logo_base64}" class="header-logo-app" alt="App Logo">' if app_logo_base64 else ''}
                {f'<img src="data:image/png;base64,{logo_base64}" class="header-logo" alt="Journal Logo">' if logo_base64 else ''}
                <h1>{t('app_title')}</h1>
                <div class="subtitle">{html.escape(profile.get('journal_name', 'Unknown Journal'))} — {t('issn')}: {profile.get('issn', 'N/A')}</div>
                <div class="subtitle" style="font-size: 14px; opacity: 0.8;">{t('period')}: {period if isinstance(period, str) else f'{period[0]}-{period[1]}' if isinstance(period, tuple) else period}</div>
                <div style="margin-top: 10px; font-size: 13px; opacity: 0.8;">{t('report_preview')}: {datetime.now().strftime('%d.%m.%Y')}</div>
            </div>
            
            <!-- ============================================ -->
            <!-- OVERVIEW -->
            <!-- ============================================ -->
            <div id="overview" class="section">
                <div class="section-title"><span class="icon">📊</span> {t('overview')}</div>
                
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
                        <div class="metric-value">{oa_percentage:.1f}%</div>
                        <div class="metric-label">{t('open_access')}</div>
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
                        <div class="metric-value">{international_rate:.1f}%</div>
                        <div class="metric-label">{t('international_collaboration_rate')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{total_citing_works}</div>
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
                
                <!-- Open Access Breakdown -->
                <h3 style="margin-top: 20px;">{t('open_access_breakdown')}</h3>
                <div class="oa-grid">
                    {''.join([
                        f'''
                        <div class="oa-card">
                            <div class="value">{oa_types.get(oa_type, 0)}</div>
                            <div class="label">{oa_labels.get(oa_type, oa_type)}</div>
                        </div>
                        '''
                        for oa_type in ['gold', 'hybrid', 'green', 'bronze', 'closed', 'unknown']
                        if oa_types.get(oa_type, 0) > 0
                    ])}
                </div>
            </div>
            
            <!-- ============================================ -->
            <!-- AUTHOR ANALYSIS -->
            <!-- ============================================ -->
            <div id="author_analysis" class="section">
                <div class="section-title"><span class="icon">👤</span> {t('author_analysis')}</div>
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
                            {authors_html if authors_html else '<tr><td colspan="7" style="text-align: center;">No data</td></tr>'}
                        </tbody>
                    </table>
                </div>
            </div>
            
            <!-- ============================================ -->
            <!-- TOP AFFILIATIONS -->
            <!-- ============================================ -->
            <div id="top_affiliations" class="section">
                <div class="section-title"><span class="icon">🏛️</span> {t('top_affiliations')}</div>
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
                            {affiliations_html if affiliations_html else '<tr><td colspan="3" style="text-align: center;">No data</td></tr>'}
                        </tbody>
                    </table>
                </div>
            </div>
            
            <!-- ============================================ -->
            <!-- GEOGRAPHIC ANALYSIS -->
            <!-- ============================================ -->
            <div id="geographic_analysis" class="section">
                <div class="section-title"><span class="icon">🌍</span> {t('geographic_analysis')}</div>
                
                <!-- Countries per Publication -->
                <div id="countries_per_pub">
                    <h3>{t('countries_per_publication')}</h3>
                    <p style="margin-bottom: 10px; color: #666; font-size: 14px;">{t('avg_countries_per_paper')}: {countries_per_pub_avg:.2f}</p>
                    <div class="table-container">
                        <table>
                            <thead>
                                <tr>
                                    <th>{t('countries')}</th>
                                    <th>{t('articles')}</th>
                                </tr>
                            </thead>
                            <tbody>
                                {countries_per_pub_html if countries_per_pub_html else '<tr><td colspan="2" style="text-align: center;">No data</td></tr>'}
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <!-- Authors per Country -->
                <div id="authors_per_country" style="margin-top: 30px;">
                    <h3>{t('authors_per_country')}</h3>
                    <div class="table-container">
                        <table>
                            <thead>
                                <tr>
                                    <th>{t('countries')}</th>
                                    <th>{t('authors')}</th>
                                </tr>
                            </thead>
                            <tbody>
                                {''.join([
                                    f'<tr><td>{html.escape(country)}</td><td>{count}</td></tr>'
                                    for country, count in sorted(authors_per_country.items(), key=lambda x: x[1], reverse=True)[:20]
                                ]) if authors_per_country else '<tr><td colspan="2" style="text-align: center;">No data</td></tr>'}
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <!-- Collaboration Patterns -->
                <div id="collaboration_patterns" style="margin-top: 30px;">
                    <h3>{t('collaboration_patterns')}</h3>
                    <div style="display: flex; gap: 30px; flex-wrap: wrap; margin: 15px 0;">
                        <div style="background: #f8f9fa; padding: 15px 25px; border-radius: 10px; text-align: center; border-left: 4px solid {primary};">
                            <div style="font-size: 28px; font-weight: bold; color: #2C3E50;">{single_country}</div>
                            <div style="font-size: 13px; color: #7F8C8D;">{t('single_country')}</div>
                            <div style="font-size: 12px; color: #555;">{single_country/total_collab*100:.1f}%</div>
                        </div>
                        <div style="background: #f8f9fa; padding: 15px 25px; border-radius: 10px; text-align: center; border-left: 4px solid {secondary};">
                            <div style="font-size: 28px; font-weight: bold; color: #2C3E50;">{international}</div>
                            <div style="font-size: 13px; color: #7F8C8D;">{t('international')}</div>
                            <div style="font-size: 12px; color: #555;">{international/total_collab*100:.1f}%</div>
                        </div>
                        <div style="background: #f8f9fa; padding: 15px 25px; border-radius: 10px; text-align: center; border-left: 4px solid #6c757d;">
                            <div style="font-size: 28px; font-weight: bold; color: #2C3E50;">{total_collab}</div>
                            <div style="font-size: 13px; color: #7F8C8D;">{t('papers')} Total</div>
                        </div>
                    </div>
                </div>
                
                <!-- Collaboration Couples -->
                <div id="collaboration_couples" style="margin-top: 30px;">
                    <h3>{t('collaboration_couples')}</h3>
                    <div class="table-container">
                        <table>
                            <thead>
                                <tr>
                                    <th>{t('country_1')}</th>
                                    <th>{t('country_2')}</th>
                                    <th>{t('frequency')}</th>
                                </tr>
                            </thead>
                            <tbody>
                                {country_pairs_html if country_pairs_html else '<tr><td colspan="3" style="text-align: center;">No data</td></tr>'}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
            
            <!-- ============================================ -->
            <!-- CITATION ANALYSIS -->
            <!-- ============================================ -->
            <div id="citation_analysis" class="section">
                <div class="section-title"><span class="icon">📈</span> {t('citation_analysis')}</div>
                
                <!-- Citation Dynamics -->
                <div id="citation_dynamics">
                    <h3>{t('citation_dynamics')}</h3>
                    <div class="table-container">
                        <table>
                            <thead>
                                <tr>
                                    <th>{t('publication_year')}</th>
                                    <th>{t('citation_year')}</th>
                                    <th>{t('citation_count')}</th>
                                </tr>
                            </thead>
                            <tbody>
                                {dynamics_html if dynamics_html else '<tr><td colspan="3" style="text-align: center;">No data</td></tr>'}
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <!-- Cumulative Citations -->
                <div id="cumulative_citations" style="margin-top: 30px;">
                    <h3>{t('cumulative_citations')}</h3>
                    <div class="table-container">
                        <table>
                            <thead>
                                <tr>
                                    <th>{t('year')}</th>
                                    <th>{t('total_citations')}</th>
                                </tr>
                            </thead>
                            <tbody>
                                {cumulative_html if cumulative_html else '<tr><td colspan="2" style="text-align: center;">No data</td></tr>'}
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <!-- Citation Heatmap -->
                <div id="citation_heatmap" style="margin-top: 30px;">
                    <h3>{t('citation_heatmap')}</h3>
                    {heatmap_html if heatmap_html else '<p style="text-align: center; color: #666;">No data</p>'}
                </div>
                
                <!-- Most Cited Publications -->
                <div id="most_cited" style="margin-top: 30px;">
                    <h3>{t('most_cited_publications')}</h3>
                    <div class="table-container">
                        <table>
                            <thead>
                                <tr>
                                    <th>{t('rank')}</th>
                                    <th>{t('title')}</th>
                                    <th>{t('year')}</th>
                                    <th>{t('citations')}</th>
                                    <th>{t('citations_year')}</th>
                                    <th>{t('authors')}</th>
                                    <th>{t('doi')}</th>
                                </tr>
                            </thead>
                            <tbody>
                                {most_cited_html if most_cited_html else '<tr><td colspan="7" style="text-align: center;">No data</td></tr>'}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
            
            <!-- ============================================ -->
            <!-- CITING WORKS ANALYSIS -->
            <!-- ============================================ -->
            <div id="citing_works_analysis" class="section">
                <div class="section-title"><span class="icon">📚</span> {t('citing_works_analysis')}</div>
                
                <!-- Top Citing Authors -->
                <div id="top_citing_authors">
                    <h3>{t('top_citing_authors')}</h3>
                    <div class="table-container">
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
                
                <!-- Top Citing Affiliations -->
                <div id="top_citing_affiliations" style="margin-top: 30px;">
                    <h3>{t('top_citing_affiliations')}</h3>
                    <div class="table-container">
                        <table>
                            <thead>
                                <tr>
                                    <th>{t('rank')}</th>
                                    <th>{t('affiliations')}</th>
                                    <th>{t('citing_works')}</th>
                                </tr>
                            </thead>
                            <tbody>
                                {top_citing_affiliations_html if top_citing_affiliations_html else '<tr><td colspan="3" style="text-align: center;">No data</td></tr>'}
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <!-- Top Citing Countries -->
                <div id="top_citing_countries" style="margin-top: 30px;">
                    <h3>{t('top_citing_countries')}</h3>
                    <div class="table-container">
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
                
                <!-- Top Citing Journals -->
                <div id="top_citing_journals" style="margin-top: 30px;">
                    <h3>{t('top_citing_journals')}</h3>
                    <div class="table-container">
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
                
                <!-- Top Citing Publishers -->
                <div id="top_citing_publishers" style="margin-top: 30px;">
                    <h3>{t('top_citing_publishers')}</h3>
                    <div class="table-container">
                        <table>
                            <thead>
                                <tr>
                                    <th>{t('rank')}</th>
                                    <th>{t('publisher')}</th>
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
            
            <!-- ============================================ -->
            <!-- TOPICS ANALYSIS -->
            <!-- ============================================ -->
            <div id="topics_analysis" class="section">
                <div class="section-title"><span class="icon">🏷️</span> {t('topics_analysis')}</div>
                
                <!-- Topics Overview -->
                <div id="topics_overview">
                    <h3>{t('topics_overview')}</h3>
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
                                </tr>
                            </thead>
                            <tbody>
                                {topics_overview_html if topics_overview_html else '<tr><td colspan="8" style="text-align: center;">No data</td></tr>'}
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <!-- Top Subtopics -->
                <div id="top_subtopics" style="margin-top: 30px;">
                    <h3>{t('top_subtopics')}</h3>
                    <div class="table-container">
                        <table>
                            <thead>
                                <tr>
                                    <th>{t('subtopics')}</th>
                                    <th>{t('analyzed_count')}</th>
                                    <th>{t('citing_count')}</th>
                                    <th>{t('total_citations')}</th>
                                </tr>
                            </thead>
                            <tbody>
                                {top_subtopics_html if top_subtopics_html else '<tr><td colspan="4" style="text-align: center;">No data</td></tr>'}
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <!-- Top Fields -->
                <div id="top_fields" style="margin-top: 30px;">
                    <h3>{t('top_fields')}</h3>
                    <div class="table-container">
                        <table>
                            <thead>
                                <tr>
                                    <th>{t('fields')}</th>
                                    <th>{t('analyzed_count')}</th>
                                    <th>{t('citing_count')}</th>
                                    <th>{t('total_citations')}</th>
                                </tr>
                            </thead>
                            <tbody>
                                {top_fields_html if top_fields_html else '<tr><td colspan="4" style="text-align: center;">No data</td></tr>'}
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <!-- Top Domains -->
                <div id="top_domains" style="margin-top: 30px;">
                    <h3>{t('top_domains')}</h3>
                    <div class="table-container">
                        <table>
                            <thead>
                                <tr>
                                    <th>{t('domains')}</th>
                                    <th>{t('analyzed_count')}</th>
                                    <th>{t('citing_count')}</th>
                                    <th>{t('total_citations')}</th>
                                </tr>
                            </thead>
                            <tbody>
                                {top_domains_html if top_domains_html else '<tr><td colspan="4" style="text-align: center;">No data</td></tr>'}
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <!-- Top Concepts -->
                <div id="top_concepts" style="margin-top: 30px;">
                    <h3>{t('top_concepts')}</h3>
                    <div class="table-container">
                        <table>
                            <thead>
                                <tr>
                                    <th>{t('concepts')}</th>
                                    <th>{t('analyzed_count')}</th>
                                    <th>{t('citing_count')}</th>
                                    <th>{t('total_citations')}</th>
                                </tr>
                            </thead>
                            <tbody>
                                {top_concepts_html if top_concepts_html else '<tr><td colspan="4" style="text-align: center;">No data</td></tr>'}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
            
            <!-- ============================================ -->
            <!-- DETAILED CITATIONS -->
            <!-- ============================================ -->
            <div id="detailed_citations" class="section">
                <div class="section-title"><span class="icon">📋</span> {t('detailed_citations')}</div>
                {detailed_citations_html if detailed_citations_html else '<p style="text-align: center; color: #666;">No detailed citations available</p>'}
            </div>
            
            <!-- ============================================ -->
            <!-- ALL PUBLICATIONS -->
            <!-- ============================================ -->
            <div id="all_publications" class="section">
                <div class="section-title"><span class="icon">📚</span> {t('all_publications')}</div>
                
                <div class="filter-section">
                    <div class="filter-row">
                        <div>
                            <label for="yearFilter">{t('filter_by_year')}:</label>
                            <select id="yearFilter" onchange="filterPublications()">
                                <option value="">{t('all_years')}</option>
                                {''.join([
                                    f'<option value="{year}">{year}</option>'
                                    for year in sorted(set(p.get('publication_year') for p in all_publications if p.get('publication_year')), reverse=True)
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
                            <label for="affiliationFilter">{t('filter_by_affiliation')}:</label>
                            <input type="text" id="affiliationFilter" placeholder="Affiliation..." onkeyup="filterPublications()">
                        </div>
                        <div>
                            <label for="citationFilter">{t('filter_by_citations')}:</label>
                            <input type="number" id="citationFilter" placeholder="Min citations..." min="0" onchange="filterPublications()">
                        </div>
                        <div>
                            <span id="visibleCount" style="font-weight: 500;">{t('all_publications_count')}</span>
                        </div>
                    </div>
                </div>
                
                <div class="table-container">
                    <table id="publicationsTable">
                        <thead>
                            <tr>
                                <th>#</th>
                                <th>{t('title')}</th>
                                <th>{t('year')}</th>
                                <th>{t('authors')}</th>
                                <th>{t('affiliations')}</th>
                                <th>{t('citations')}</th>
                                <th>{t('citations_year')}</th>
                                <th>{t('doi')}</th>
                            </tr>
                        </thead>
                        <tbody>
                            {all_publications_html if all_publications_html else '<tr><td colspan="8" style="text-align: center;">No publications</td></tr>'}
                        </tbody>
                    </table>
                </div>
                <p style="margin-top: 10px; font-size: 13px; color: #666;">Showing up to 50 publications</p>
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
# ФУНКЦИИ ДЛЯ МНОЖЕСТВЕННЫХ ЖУРНАЛОВ (ОТЧЕТЫ)
# ============================================

def generate_journal_html_report_multiple(all_journals: List[Dict], show_all: bool, 
                                         journal_logo_base64: Optional[str] = None, 
                                         app_logo_base64: Optional[str] = None,
                                         theme_colors: Optional[Dict] = None, 
                                         lang: str = 'en') -> str:
    """Генерирует HTML отчет для множественных журналов"""
    
    if theme_colors is None:
        theme_colors = {
            'primary': '#667eea',
            'secondary': '#f39c12'
        }
    
    primary = theme_colors.get('primary', '#667eea')
    secondary = theme_colors.get('secondary', '#f39c12')
    
    def t(key: str, **kwargs) -> str:
        return translate(key, lang, **kwargs)
    
    if not all_journals:
        return "<html><body><h1>Нет данных для отображения</h1></body></html>"
    
    best_journal = all_journals[0]
    
    if show_all:
        journals_to_show = all_journals
    else:
        journals_to_show = [best_journal]
    
    if len(journals_to_show) == 1:
        journal_data = journals_to_show[0]
        analyzer = journal_data.get('analyzer')
        profile = journal_data.get('profile', {})
        articles = journal_data.get('articles', [])
        
        return generate_journal_html_report(
            analyzer, profile, articles,
            journal_logo_base64, app_logo_base64,
            theme_colors, lang
        )
    
    # Множественные журналы
    html_parts = []
    
    html_parts.append(f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>{t('app_title')} - {t('analyze_multiple')}</title>
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
            .sidebar h2 {{
                color: white;
                margin-bottom: 25px;
                font-size: 20px;
                border-bottom: 2px solid rgba(255,255,255,0.3);
                padding-bottom: 15px;
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
            .journal-card {{
                background: white;
                border-radius: 15px;
                padding: 25px;
                margin-bottom: 30px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                border-left: 5px solid {primary};
                transition: transform 0.2s;
            }}
            .journal-card.best {{
                border-left-color: #FFD700;
                background: linear-gradient(135deg, #fff9e6 0%, #ffffff 100%);
            }}
            .journal-rank {{
                font-size: 20px;
                font-weight: bold;
                color: {primary};
                display: inline-block;
                margin-right: 10px;
            }}
            .journal-name-main {{
                font-size: 22px;
                font-weight: 600;
                color: {primary};
                display: inline-block;
            }}
            .journal-hindex {{
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
            .metrics-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
                gap: 10px;
                margin: 15px 0;
            }}
            .metric-card {{
                background: #f8f9fa;
                padding: 12px;
                border-radius: 8px;
                border-left: 4px solid {primary};
                text-align: center;
            }}
            .metric-value {{
                font-size: 22px;
                font-weight: bold;
                color: #2C3E50;
            }}
            .metric-label {{
                font-size: 11px;
                color: #7F8C8D;
                margin-top: 3px;
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
            @media print {{
                .sidebar {{ display: none; }}
                .main-content {{ margin-left: 0; }}
            }}
            @media (max-width: 768px) {{
                .sidebar {{ display: none; }}
                .main-content {{ margin-left: 0; padding: 15px; }}
                .metrics-grid {{ grid-template-columns: repeat(2, 1fr); }}
            }}
        </style>
    </head>
    <body>
        <div class="sidebar">
            <h2>📊 {t('app_title')}</h2>
    """)
    
    for i, journal in enumerate(journals_to_show):
        journal_name = journal.get('journal_name', f'Journal {i+1}')
        h_index = journal.get('h_index', 0)
        html_parts.append(f'<a href="#journal_{i}">📊 {html.escape(journal_name)} (h-index: {h_index})</a>')
    
    html_parts.append("""
        </div>
        <div class="main-content">
            <div class="header">
    """)
    
    if app_logo_base64:
        html_parts.append(f'<img src="data:image/png;base64,{app_logo_base64}" class="header-logo-app" alt="App Logo">')
    
    if journal_logo_base64:
        html_parts.append(f'<img src="data:image/png;base64,{journal_logo_base64}" class="header-logo" alt="Journal Logo">')
    
    html_parts.append(f"""
                <h1>📊 {t('app_title')}</h1>
                <div style="margin-top: 10px; font-size: 16px;">
                    {t('analyzing_journals', count=len(journals_to_show))}
                </div>
                <div style="margin-top: 10px;">
                    <span class="badge badge-info">{t('publications')}: {len(journals_to_show)}</span>
                    {'<span class="badge badge-success">' + t('best_journal', name=best_journal.get("journal_name", "Unknown"), h_index=best_journal.get("h_index", 0)) + '</span>' if len(journals_to_show) > 1 else ''}
                    {'<span class="badge badge-info">' + t('showing_all', count=len(journals_to_show)) + '</span>' if show_all else ''}
                </div>
                <div class="subtitle" style="font-size: 14px; opacity: 0.8; margin-top: 10px;">{t('report_preview')}: {datetime.now().strftime('%d.%m.%Y')}</div>
            </div>
    """)
    
    for i, journal_data in enumerate(journals_to_show):
        is_best = (i == 0 and len(journals_to_show) > 1)
        journal_name = journal_data.get('journal_name', f'Journal {i+1}')
        profile = journal_data.get('profile', {})
        articles = journal_data.get('articles', [])
        analyzer = journal_data.get('analyzer')
        
        # Создаем мини-отчет для каждого журнала
        mini_report = generate_journal_html_report(
            analyzer, profile, articles,
            None, None,
            theme_colors, lang
        )
        
        # Извлекаем только содержимое между main-content
        import re
        content_match = re.search(r'<div class="main-content">(.*?)</body>', mini_report, re.DOTALL)
        if content_match:
            content = content_match.group(1)
            # Удаляем дублирующий header
            content = re.sub(r'<div class="header">.*?</div>', '', content, flags=re.DOTALL)
        else:
            content = "<p>Error generating report</p>"
        
        html_parts.append(f"""
        <div id="journal_{i}" class="journal-card {'best' if is_best else ''}">
            <div>
                <span class="journal-rank">{i+1}.</span>
                <span class="journal-name-main">{html.escape(journal_name)}</span>
                <span class="journal-hindex">(h-index: {profile.get('h_index', 0)})</span>
                {f'<span class="best-badge">🏆 {t("best_journal", name="", h_index="")}</span>' if is_best else ''}
            </div>
            
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-value">{profile.get('total_publications', 0)}</div>
                    <div class="metric-label">{t('publications')}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{profile.get('total_citations', 0):,}</div>
                    <div class="metric-label">{t('total_citations')}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{profile.get('h_index', 0)}</div>
                    <div class="metric-label">{t('h_index')}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{profile.get('avg_citations', 0):.1f}</div>
                    <div class="metric-label">{t('avg_citations')}</div>
                </div>
            </div>
            
            {content}
        </div>
        """)
    
    html_parts.append("""
            <div class="footer">
                <p>© Advanced Journal Analysis Tool / Created by daM / Chimica Techno Acta</p>
                <p><a href="https://chimicatechnoacta.ru" target="_blank">https://chimicatechnoacta.ru</a></p>
                <p style="font-size: 11px; margin-top: 5px;">Data source: OpenAlex | Generated: {datetime.now().strftime('%d.%m.%Y')}</p>
            </div>
        </div>
    </body>
    </html>
    """)
    
    return '\n'.join(html_parts)

# ============================================
# ОСНОВНАЯ ФУНКЦИЯ ЗАПУСКА ДЛЯ STREAMLIT (ЖУРНАЛЫ)
# ============================================

def run_journal_analysis(issn_list: List[str], period: Any, show_all_journals: bool, 
                         journal_logo: Optional[Dict] = None, max_workers: int = MAX_WORKERS):
    """Запускает полный анализ журнала для одного или нескольких ISSN"""
    
    # Get current language for translations
    current_lang = st.session_state.get('language', 'en')
    def t(key: str, **kwargs) -> str:
        return translate(key, current_lang, **kwargs)
    
    if not issn_list:
        st.error("⚠️ " + t('no_issn'))
        return
    
    st.cache_data.clear()
    
    st.info(f"🔍 " + t('analyzing_journals', count=len(issn_list)))
    
    progress_container = st.empty()
    status_container = st.empty()
    analysis_progress = st.progress(0, text=t('starting_analysis'))
    
    try:
        # Загружаем логотип приложения
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
        
        total_journals = len(issn_list)
        
        def progress_callback(stage: str, current: int, total: int):
            """Обработчик прогресса"""
            if stage == 'articles':
                progress = (current / total) * 0.3
                analysis_progress.progress(progress, text=f"📡 {t('loading_data')}... ({current} статей)")
                status_container.info(f"📡 {t('fetching_data')}: {current} статей")
            elif stage == 'citing':
                progress = 0.3 + (current / total) * 0.35
                analysis_progress.progress(progress, text=f"⚡ {t('analyzing_data')}... ({current}/{total} цитирований)")
                status_container.info(f"⚡ Сбор цитирований: {current}/{total}")
            elif stage == 'metadata':
                progress = 0.65 + (current / total) * 0.2
                analysis_progress.progress(progress, text=f"📖 Получение метаданных... ({current}/{total})")
                status_container.info(f"📖 Метаданные цитирующих работ: {current}/{total}")
            elif stage == 'analysis':
                progress = 0.85 + (current / total) * 0.1
                analysis_progress.progress(progress, text=f"📊 {t('analyzing_data')}...")
                status_container.info(f"📊 Анализ данных...")
        
        def journal_progress_callback(current: int, total: int, issn: str):
            """Прогресс для множественных журналов"""
            progress = (current / total) * 0.9
            analysis_progress.progress(progress, text=f"🔍 {t('analyzing_journals', count=total)}: {issn} ({current}/{total})")
            status_container.info(f"🔍 Анализ журнала: {issn} ({current}/{total})")
        
        start_time = time.time()
        
        # Сбор данных
        all_journals_data = []
        
        for idx, issn in enumerate(issn_list):
            journal_progress_callback(idx + 1, total_journals, issn)
            
            analyzer, profile, articles = collect_journal_data(
                issn, period, max_workers, progress_callback
            )
            
            if profile:
                all_journals_data.append({
                    'issn': issn,
                    'analyzer': analyzer,
                    'profile': profile,
                    'articles': articles,
                    'journal_name': profile.get('journal_name', 'Unknown'),
                    'h_index': profile.get('h_index', 0),
                    'total_publications': profile.get('total_publications', 0),
                    'total_citations': profile.get('total_citations', 0)
                })
        
        elapsed = time.time() - start_time
        
        if not all_journals_data:
            st.error(f"❌ {t('data_not_found')}")
            analysis_progress.empty()
            return
        
        sorted_journals = sort_journals_by_h_index(all_journals_data)
        
        st.session_state['all_journals'] = sorted_journals
        st.session_state['show_all_journals'] = show_all_journals
        st.session_state['journal_logo_base64'] = journal_logo_base64
        st.session_state['app_logo_base64'] = app_logo_base64
        st.session_state['analysis_complete'] = True
        st.session_state['analysis_mode'] = 'journal'
        st.session_state['period'] = period
        
        analysis_progress.progress(1.0, text=f"✅ {t('analysis_complete_text')}!")
        
        st.success(t('analysis_complete', count=sum(j.get('total_publications', 0) for j in sorted_journals), time=elapsed))
        
        if len(sorted_journals) > 1:
            best_journal = sorted_journals[0]
            st.info(t('best_journal', name=best_journal.get('journal_name', 'Unknown'), h_index=best_journal.get('h_index', 0)))
        else:
            st.info(t('single_journal', name=sorted_journals[0].get('journal_name', 'Unknown'), h_index=sorted_journals[0].get('h_index', 0)))
        
        if show_all_journals and len(sorted_journals) > 1:
            st.info(t('showing_all', count=len(sorted_journals)))
        elif len(sorted_journals) == 1:
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
    if 'show_all_journals' not in st.session_state:
        st.session_state.show_all_journals = False
    if 'all_journals' not in st.session_state:
        st.session_state.all_journals = []
    if 'analysis_complete' not in st.session_state:
        st.session_state.analysis_complete = False
    if 'journal_logo_base64' not in st.session_state:
        st.session_state.journal_logo_base64 = None
    if 'app_logo_base64' not in st.session_state:
        st.session_state.app_logo_base64 = None
    if 'language' not in st.session_state:
        st.session_state.language = 'en'
    if 'analysis_mode' not in st.session_state:
        st.session_state.analysis_mode = 'journal'
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
        st.markdown(f"### {t('profile_analysis')}")
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
        
        issn_text = st.text_area(
            t('issn_input'),
            placeholder=t('issn_placeholder'),
            help=t('issn_help'),
            height=80
        )
        
        period_text = st.text_input(
            t('period_input'),
            placeholder=t('period_placeholder'),
            help=t('period_help')
        )
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            journal_logo_upload = st.file_uploader(
                t('upload_logo'),
                type=['png', 'jpg', 'jpeg', 'svg'],
                help=t('logo_help')
            )
        
        with col2:
            show_all_journals = st.checkbox(
                t('show_all_authors'),
                value=st.session_state.show_all_journals,
                help=t('show_all_help')
            )
            st.session_state.show_all_journals = show_all_journals
        
        # Параметры параллельной обработки
        max_workers = st.slider(
            "⚡ Parallel Workers",
            min_value=4,
            max_value=12,
            value=MAX_WORKERS,
            step=1,
            help="Number of parallel threads for API requests"
        )
        
        if st.button(t('analyze_button'), type="primary", width='stretch'):
            issns = parse_issns(issn_text)
            
            if not issns:
                st.error(t('no_issn'))
            elif len(issns) > 20:
                st.warning(t('too_many_issns', count=len(issns)))
            else:
                period = parse_period(period_text)
                if not period:
                    st.error("⚠️ Invalid period format. Use e.g., 2020-2023 or 2020,2021,2022")
                else:
                    journal_logo_data = None
                    if journal_logo_upload:
                        journal_logo_data = {
                            journal_logo_upload.name: {
                                'content': journal_logo_upload.read()
                            }
                        }
                    
                    run_journal_analysis(issns, period, show_all_journals, journal_logo_data, max_workers)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        if st.session_state.analysis_complete and st.session_state.all_journals:
            journals = st.session_state.all_journals
            show_all = st.session_state.show_all_journals
            journal_logo_base64 = st.session_state.journal_logo_base64
            period = st.session_state.period
            
            st.markdown(f"## {t('journal_analysis')}")
            
            if show_all and len(journals) > 1:
                st.info(t('showing_all', count=len(journals)))
            elif len(journals) == 1:
                st.info(t('showing_single_only'))
            
            st.markdown("---")
            
            for idx, journal_data in enumerate(journals, 1):
                if not show_all and idx > 1:
                    break
                
                is_best = (idx == 1 and len(journals) > 1)
                journal_name = journal_data.get('journal_name', f'Journal {idx}')
                profile = journal_data.get('profile', {})
                articles = journal_data.get('articles', [])
                analyzer = journal_data.get('analyzer')
                
                h_index = profile.get('h_index', 0)
                total_pubs = profile.get('total_publications', 0)
                total_citations = profile.get('total_citations', 0)
                avg_citations = profile.get('average_citations', 0)
                oa_percentage = profile.get('oa_percentage', 0)
                
                journal_class = "author-card best" if is_best else "author-card"
                st.markdown(f"""
                <div class="{journal_class}">
                    <div>
                        <span class="author-rank">{idx}.</span>
                        <span class="author-name-main">{journal_name}</span>
                        <span class="author-hindex">(h-index: {h_index})</span>
                        {'<span class="best-badge">🏆 ' + t("best_journal", name="", h_index="") + '</span>' if is_best and len(journals) > 1 else ''}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    st.metric(t('publications'), total_pubs)
                with col2:
                    st.metric(t('h_index'), h_index)
                with col3:
                    st.metric(t('total_citations'), f"{total_citations:,}")
                with col4:
                    st.metric(t('avg_citations'), f"{avg_citations:.1f}")
                with col5:
                    st.metric(t('open_access'), f"{oa_percentage:.1f}%")
                
                # Open Access Breakdown
                oa_types = profile.get('oa_types', {})
                oa_labels = {
                    'gold': t('gold'),
                    'hybrid': t('hybrid'),
                    'green': t('green'),
                    'bronze': t('bronze'),
                    'closed': t('closed'),
                    'unknown': t('unknown')
                }
                
                st.markdown("**Open Access Breakdown:**")
                oa_cols = st.columns(len([k for k in oa_types.keys() if oa_types[k] > 0]) or 1)
                for i, (oa_type, label) in enumerate(oa_labels.items()):
                    if oa_types.get(oa_type, 0) > 0:
                        with oa_cols[i % len(oa_cols)]:
                            st.metric(label, oa_types[oa_type])
                
                # Top Authors
                top_authors = profile.get('top_authors', {})
                if top_authors:
                    st.markdown("**Top Authors:**")
                    author_data = []
                    for name, count in list(top_authors.items())[:10]:
                        author_data.append({'Author': name, 'Publications': count})
                    st.dataframe(pd.DataFrame(author_data), width='stretch')
                
                # Top Affiliations
                top_affiliations = profile.get('top_affiliations', {})
                if top_affiliations:
                    st.markdown("**Top Affiliations:**")
                    aff_data = []
                    for aff, count in list(top_affiliations.items())[:10]:
                        aff_data.append({'Affiliation': aff, 'Publications': count})
                    st.dataframe(pd.DataFrame(aff_data), width='stretch')
                
                # Most Cited
                most_cited = profile.get('most_cited', [])
                if most_cited:
                    st.markdown("**Most Cited Publications:**")
                    cited_data = []
                    for pub in most_cited[:5]:
                        cited_data.append({
                            'Title': pub.get('title', 'No title')[:60] + '...' if len(pub.get('title', 'No title')) > 60 else pub.get('title', 'No title'),
                            'Year': pub.get('year', 'N/A'),
                            'Citations': pub.get('citations', 0),
                            'DOI': pub.get('doi', '')
                        })
                    st.dataframe(pd.DataFrame(cited_data), width='stretch')
                
                with st.expander(f"📚 {t('publications_list')} ({len(articles)})"):
                    if articles:
                        pub_data = []
                        for pub in sorted(articles, key=lambda x: x.get('publication_year', 0), reverse=True)[:20]:
                            pub_data.append({
                                t('title'): (pub.get('title') or 'No title')[:80] + '...' if len(pub.get('title') or 'No title') > 80 else (pub.get('title') or 'No title'),
                                t('year'): pub.get('publication_year', 'N/A'),
                                t('citations'): pub.get('cited_by_count', 0),
                                'DOI': pub.get('doi', ''),
                                'OA': '✅' if pub.get('is_oa', False) else '❌'
                            })
                        st.dataframe(pd.DataFrame(pub_data), width='stretch')
                        if len(articles) > 20:
                            st.caption(t('showing_limited', shown=20, total=len(articles)))
                
                st.markdown("---")
        else:
            st.info(t('no_data'))
    
    with tab3:
        if st.session_state.analysis_complete and st.session_state.all_journals:
            journals = st.session_state.all_journals
            show_all = st.session_state.show_all_journals
            journal_logo_base64 = st.session_state.journal_logo_base64
            app_logo_base64 = st.session_state.app_logo_base64
            period = st.session_state.period
            
            theme_colors = {
                'primary': st.session_state.primary_color,
                'secondary': st.session_state.secondary_color
            }
            
            st.markdown(f"## {t('html_report')}")
            
            best_journal = journals[0]
            
            if len(journals) > 1:
                st.info(t('best_journal', name=best_journal.get('journal_name', 'Unknown'), h_index=best_journal.get('h_index', 0)))
            else:
                st.info(t('single_journal', name=best_journal.get('journal_name', 'Unknown'), h_index=best_journal.get('h_index', 0)))
            
            if show_all and len(journals) > 1:
                st.info(t('showing_all', count=len(journals)))
            else:
                st.info(t('showing_single'))
            
            if st.button(t('download_report'), type="primary", width='stretch'):
                with st.spinner(t('generating_report')):
                    if len(journals) == 1 or not show_all:
                        journal_data = journals[0]
                        analyzer = journal_data.get('analyzer')
                        profile = journal_data.get('profile', {})
                        articles = journal_data.get('articles', [])
                        
                        html_report = generate_journal_html_report(
                            analyzer, profile, articles,
                            journal_logo_base64, app_logo_base64,
                            theme_colors, current_lang
                        )
                    else:
                        html_report = generate_journal_html_report_multiple(
                            journals, show_all,
                            journal_logo_base64, app_logo_base64,
                            theme_colors, current_lang
                        )
                    
                    if show_all and len(journals) > 1:
                        filename = f"journals_{len(journals)}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
                    else:
                        filename = f"journal_{best_journal.get('journal_name', 'unknown').replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
                    
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
