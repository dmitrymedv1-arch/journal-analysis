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
USE_CACHE = False  # Кэширование результатов (отключено в интерфейсе)
LOGO_PATH = None  # Путь к логотипу журнала (устанавливается через виджет)

# Лимиты для анализа
MAX_PUBLICATIONS_TO_ANALYZE = 1000  # Максимум статей для анализа
MIN_YEAR_FOR_TREND = 5  # Сколько лет для тренда

# Режим анализа источников данных
ANALYSIS_MODE = "journal_analysis"  # Режим анализа журналов

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
        'load_data': '📥 Load Data',
        'analysis_results': '📊 Analysis Results',
        'issn_input': 'Journal ISSN',
        'issn_placeholder': '0028-0836',
        'issn_help': 'Enter the journal ISSN (format: XXXX-XXXX)',
        'period_input': 'Analysis Period',
        'period_placeholder': '2020-2023 or 2020,2021,2022',
        'period_help': 'Enter year range (2020-2023) or comma-separated years (2020,2021,2022)',
        'max_workers': 'Parallel Threads',
        'max_workers_help': 'Number of parallel API requests (4-12 recommended)',
        'upload_logo': 'Upload journal logo (optional)',
        'logo_help': 'Logo will be displayed in reports',
        'analyze_button': '🚀 Run Journal Analysis',
        'no_issn': '⚠️ Enter a valid ISSN',
        'no_period': '⚠️ Enter analysis period',
        'invalid_issn': '⚠️ Invalid ISSN format. Use XXXX-XXXX',
        'invalid_period': '⚠️ Invalid period format',
        'analysis_complete': '✅ Analysis complete! Processed {count} articles in {time:.1f} sec.',
        'no_data': '👈 Enter ISSN and period, then click "Run Journal Analysis"',
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
        'analysis_source': '📊 Data source for analysis:',
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
        # Новые ключи для журнального анализа
        'journal_analysis_title': 'Advanced Journal Analysis Tool',
        'journal_analysis_subtitle': 'Comprehensive journal analysis by ISSN',
        'stage_1': 'Collecting journal publications',
        'stage_2': 'Collecting citing works',
        'stage_3': 'Fetching metadata for analyzed works',
        'stage_4': 'Fetching metadata for citing works',
        'stage_5': 'Generating HTML report',
        'stage_1_desc': 'Retrieving all articles from the journal for the specified period',
        'stage_2_desc': 'Collecting all citing works for each article',
        'stage_3_desc': 'Fetching detailed metadata for analyzed articles',
        'stage_4_desc': 'Fetching detailed metadata for citing works',
        'stage_5_desc': 'Calculating statistics and generating report',
        'processing_articles': 'Processing articles: {processed}/{total}',
        'processing_citations': 'Processing citations: {processed}/{total}',
        'fetching_metadata': 'Fetching metadata: {processed}/{total}',
        'total_publications': 'Total Publications',
        'total_citations': 'Total Citations',
        'avg_citations': 'Avg Citations',
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
        'diamond': 'Diamond',
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
        'single_country': 'Single Country',
        'international_collaboration': 'International Collaboration',
        'collaboration_couples': 'Collaboration Couples',
        'country_pair': 'Country Pair',
        'frequency': 'Frequency',
        'citation_analysis': 'Citation Analysis',
        'citation_dynamics_by_year': 'Citation Dynamics by Year',
        'publication_year_col': 'Publication Year',
        'citation_year_col': 'Citation Year',
        'citations_count_col': 'Citations Count',
        'first_citation_analysis': 'First Citation Analysis',
        'min': 'Min',
        'max': 'Max',
        'avg': 'Avg',
        'median': 'Median',
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
        'topic_overview': 'Topic Overview',
        'analyzed_count': 'Analyzed Count',
        'citing_count': 'Citing Count',
        'analyzed_norm_count': 'Analyzed Norm Count',
        'citing_norm_count': 'Citing Norm Count',
        'total_norm_count': 'Total Norm Count',
        'first_year': 'First Year',
        'peak_year': 'Peak Year',
        'top_topics_by_citations': 'Top Topics by Citations',
        'detailed_citations': 'Detailed Citations',
        'show_citations': 'Show Citations',
        'hide_citations': 'Hide Citations',
        'citing_title': 'Citing Title',
        'citing_journal': 'Citing Journal',
        'citing_year': 'Citing Year',
        'citing_date': 'Citing Date',
        'citation_lag': 'Citation Lag',
        'all_publications': 'All Publications',
        'filter_by_year': 'Filter by Year',
        'filter_by_author': 'Filter by Author',
        'filter_by_affiliation': 'Filter by Affiliation',
        'filter_by_citations': 'Filter by Citations (min)',
        'filter_by_title': 'Filter by Title Word(s)',
        'search_publications': 'Search Publications',
        'all_years': 'All Years',
        'show_all_publications': 'Show All Publications',
        'showing_all_publications': 'Showing all {count} publications',
        'no_matching_publications': 'No matching publications found',
        'citation_network': 'Citation Network',
        'overview': 'Overview',
        'key_metrics': 'Key Metrics',
        'citing_works': 'Citing Works',
        'summary': 'Summary',
        'topics_analysis_title': 'Topics Analysis',
        'topic_relationships': 'Topic Relationships',
        'subtopics': 'Subtopics',
        'fields_analysis': 'Fields',
        'domains_analysis': 'Domains',
        'concepts_analysis': 'Concepts',
        'top_10_topics': 'Top 10 Most Cited Topics',
        'top_10_subtopics': 'Top 10 Most Cited Subtopics',
        'top_10_fields': 'Top 10 Most Cited Fields',
        'top_10_domains': 'Top 10 Most Cited Domains',
        'top_10_concepts': 'Top 10 Most Cited Concepts',
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
        'load_data': '📥 Загрузка данных',
        'analysis_results': '📊 Результаты анализа',
        'issn_input': 'ISSN журнала',
        'issn_placeholder': '0028-0836',
        'issn_help': 'Введите ISSN журнала (формат: XXXX-XXXX)',
        'period_input': 'Период анализа',
        'period_placeholder': '2020-2023 или 2020,2021,2022',
        'period_help': 'Введите диапазон лет (2020-2023) или годы через запятую (2020,2021,2022)',
        'max_workers': 'Параллельных потоков',
        'max_workers_help': 'Количество параллельных запросов к API (рекомендуется 4-12)',
        'upload_logo': 'Загрузить логотип журнала (опционально)',
        'logo_help': 'Логотип будет отображаться в отчетах',
        'analyze_button': '🚀 Запустить анализ журнала',
        'no_issn': '⚠️ Введите корректный ISSN',
        'no_period': '⚠️ Введите период анализа',
        'invalid_issn': '⚠️ Неверный формат ISSN. Используйте XXXX-XXXX',
        'invalid_period': '⚠️ Неверный формат периода',
        'analysis_complete': '✅ Анализ завершен! Обработано {count} статей за {time:.1f} сек.',
        'no_data': '👈 Введите ISSN и период, затем нажмите "Запустить анализ журнала"',
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
        'analysis_source': '📊 Источник данных для анализа:',
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
        # Новые ключи для журнального анализа
        'journal_analysis_title': 'Расширенный инструмент анализа журналов',
        'journal_analysis_subtitle': 'Комплексный анализ журнала по ISSN',
        'stage_1': 'Сбор публикаций журнала',
        'stage_2': 'Сбор цитирующих работ',
        'stage_3': 'Получение метаданных анализируемых работ',
        'stage_4': 'Получение метаданных цитирующих работ',
        'stage_5': 'Генерация HTML отчета',
        'stage_1_desc': 'Получение всех статей из журнала за указанный период',
        'stage_2_desc': 'Сбор всех цитирующих работ для каждой статьи',
        'stage_3_desc': 'Получение детальных метаданных анализируемых статей',
        'stage_4_desc': 'Получение детальных метаданных цитирующих работ',
        'stage_5_desc': 'Расчет статистики и формирование отчета',
        'processing_articles': 'Обработка статей: {processed}/{total}',
        'processing_citations': 'Обработка цитирований: {processed}/{total}',
        'fetching_metadata': 'Получение метаданных: {processed}/{total}',
        'total_publications': 'Всего публикаций',
        'total_citations': 'Всего цитирований',
        'avg_citations': 'Среднее цитирований',
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
        'open_access_breakdown': 'Разбивка по открытому доступу',
        'gold': 'Gold',
        'hybrid': 'Hybrid',
        'green': 'Green',
        'bronze': 'Bronze',
        'closed': 'Closed',
        'diamond': 'Diamond',
        'unknown': 'Неизвестно',
        'analyzed_articles': 'Анализируемые статьи',
        'author_analysis': 'Анализ авторов',
        'rank': 'Место',
        'authors': 'Авторы',
        'publications_count': 'Публикаций',
        'citations_count': 'Цитирований',
        'top_affiliations': 'Топ аффилиаций',
        'geographic_analysis': 'Географический анализ',
        'unique_countries_per_publication': 'Уникальные страны на публикацию',
        'authors_per_country': 'Авторы по странам',
        'collaboration_patterns': 'Модели коллабораций',
        'single_country': 'Одна страна',
        'international_collaboration': 'Международная коллаборация',
        'collaboration_couples': 'Пары стран-коллабораций',
        'country_pair': 'Пара стран',
        'frequency': 'Частота',
        'citation_analysis': 'Цитируемость',
        'citation_dynamics_by_year': 'Динамика цитирований по годам',
        'publication_year_col': 'Год публикации',
        'citation_year_col': 'Год цитирования',
        'citations_count_col': 'Количество цитирований',
        'first_citation_analysis': 'Анализ первого цитирования',
        'min': 'Мин',
        'max': 'Макс',
        'avg': 'Сред',
        'median': 'Медиана',
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
        'topic_overview': 'Обзор тем',
        'analyzed_count': 'Количество в анализе',
        'citing_count': 'Количество цитирований',
        'analyzed_norm_count': 'Норм. кол-во в анализе',
        'citing_norm_count': 'Норм. кол-во цитирований',
        'total_norm_count': 'Общее норм. кол-во',
        'first_year': 'Первый год',
        'peak_year': 'Пиковый год',
        'top_topics_by_citations': 'Топ тем по цитированиям',
        'detailed_citations': 'Детальные цитирования',
        'show_citations': 'Показать цитирования',
        'hide_citations': 'Скрыть цитирования',
        'citing_title': 'Название цитирующей работы',
        'citing_journal': 'Цитирующий журнал',
        'citing_year': 'Год цитирования',
        'citing_date': 'Дата цитирования',
        'citation_lag': 'Задержка цитирования',
        'all_publications': 'Все публикации',
        'filter_by_year': 'Фильтр по году',
        'filter_by_author': 'Фильтр по автору',
        'filter_by_affiliation': 'Фильтр по аффилиации',
        'filter_by_citations': 'Фильтр по цитированиям (мин)',
        'filter_by_title': 'Фильтр по словам в названии',
        'search_publications': 'Поиск публикаций',
        'all_years': 'Все годы',
        'show_all_publications': 'Показать все публикации',
        'showing_all_publications': 'Показаны все {count} публикаций',
        'no_matching_publications': 'Нет подходящих публикаций',
        'citation_network': 'Сеть цитирований',
        'overview': 'Обзор',
        'key_metrics': 'Ключевые метрики',
        'citing_works': 'Цитирующие работы',
        'summary': 'Сводка',
        'topics_analysis_title': 'Тематический анализ',
        'topic_relationships': 'Взаимосвязи тем',
        'subtopics': 'Подтемы',
        'fields_analysis': 'Области',
        'domains_analysis': 'Домены',
        'concepts_analysis': 'Концепты',
        'top_10_topics': 'Топ-10 наиболее цитируемых тем',
        'top_10_subtopics': 'Топ-10 наиболее цитируемых подтем',
        'top_10_fields': 'Топ-10 наиболее цитируемых областей',
        'top_10_domains': 'Топ-10 наиболее цитируемых доменов',
        'top_10_concepts': 'Топ-10 наиболее цитируемых концептов',
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
        
        .filter-section {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            border: 1px solid #e0e0e0;
        }}
        
        .filter-row {{
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            align-items: end;
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
            margin-bottom: 4px;
        }}
        
        .filter-row select, .filter-row input {{
            width: 100%;
            padding: 6px 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 13px;
        }}
        
        .collapser {{
            background: #f8f9fa;
            padding: 12px 15px;
            margin: 8px 0;
            border-radius: 6px;
            cursor: pointer;
            border: 1px solid #e0e0e0;
            transition: all 0.2s;
        }}
        
        .collapser:hover {{
            background: #e9ecef;
            border-color: var(--primary);
        }}
        
        .collapser .citation-count {{
            background: var(--primary);
            color: white;
            padding: 2px 10px;
            border-radius: 12px;
            font-size: 12px;
            margin-left: 10px;
        }}
        
        .citation-detail {{
            background: white;
            padding: 12px 15px;
            margin: 4px 0 4px 20px;
            border-left: 3px solid var(--primary);
            border-radius: 4px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }}
        
        .citation-detail .cite-meta {{
            font-size: 13px;
            color: #555;
            margin-top: 4px;
        }}
        
        .citation-detail .cite-meta strong {{
            color: #333;
        }}
        
        .word-wrap {{
            word-wrap: break-word;
            max-width: 300px;
        }}
        
        .heatmap-cell {{
            text-align: center;
            padding: 6px 10px;
            border-radius: 4px;
            font-weight: 500;
        }}
        
        .table-container {{
            overflow-x: auto;
            max-height: 600px;
            overflow-y: auto;
        }}
        
        .table-container table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
        }}
        
        .table-container th {{
            position: sticky;
            top: 0;
            z-index: 10;
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
            color: white;
            padding: 10px 12px;
            text-align: left;
        }}
        
        .table-container td {{
            padding: 8px 12px;
            border-bottom: 1px solid #eee;
        }}
        
        .table-container tr:hover {{
            background: var(--hover-light);
        }}
        
        .topic-card {{
            background: white;
            border-radius: 8px;
            padding: 12px 15px;
            margin-bottom: 8px;
            border-left: 4px solid var(--primary);
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }}
        
        .topic-card .topic-name {{
            font-weight: 600;
            color: var(--primary);
        }}
        
        .topic-card .topic-stats {{
            font-size: 12px;
            color: #666;
            margin-top: 4px;
        }}
        
        .topic-card .topic-stats span {{
            margin-right: 15px;
        }}
        
        .progress-bar-container {{
            background: #f0f0f0;
            border-radius: 10px;
            overflow: hidden;
            height: 20px;
            margin: 4px 0;
        }}
        
        .progress-bar-fill {{
            height: 100%;
            background: linear-gradient(90deg, var(--primary), var(--secondary));
            border-radius: 10px;
            transition: width 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 11px;
            font-weight: 600;
        }}
        
        .badge {{
            display: inline-block;
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 600;
            margin: 2px;
        }}
        
        .badge-gold {{
            background: #ffd700;
            color: #333;
        }}
        
        .badge-hybrid {{
            background: #ff6b35;
            color: white;
        }}
        
        .badge-green {{
            background: #2ecc71;
            color: white;
        }}
        
        .badge-bronze {{
            background: #cd7f32;
            color: white;
        }}
        
        .badge-closed {{
            background: #95a5a6;
            color: white;
        }}
        
        .badge-diamond {{
            background: #3498db;
            color: white;
        }}
        
        .badge-unknown {{
            background: #bdc3c7;
            color: #333;
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
# ФУНКЦИИ ДЛЯ АНАЛИЗА ЖУРНАЛОВ (НОВЫЙ КОД)
# ============================================

# Глобальная блокировка для потокобезопасных запросов
_api_lock = Lock()

def normalize_issn(issn_str: str) -> str:
    """Нормализует ISSN к формату XXXX-XXXX"""
    cleaned = re.sub(r'[^0-9Xx]', '', str(issn_str).strip())
    if len(cleaned) == 8:
        return f"{cleaned[:4]}-{cleaned[4:]}".upper()
    return cleaned.upper()

def smart_get(url: str, params: Dict, retries: int = MAX_RETRIES) -> Optional[Dict]:
    """Умный GET запрос с защитой от 429 ошибок"""
    for attempt in range(retries):
        try:
            with _api_lock:
                time.sleep(random.uniform(0.1, 0.35))
            
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
                print(f"⚠️ smart_get attempt {attempt+1} failed: {str(e)[:100]}")
            time.sleep(1.5 * (2 ** attempt))
    
    return None

def get_citing_dois(oa_id: str, max_citing: int = 300) -> List[str]:
    """Получает список DOI цитирующих работ для указанной работы"""
    citing = []
    cursor = "*"
    base_url = "https://api.openalex.org/works"
    
    for _ in range(8):
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
    
    return citing[:max_citing]

def fetch_article_metadata(doi: str) -> Optional[Dict]:
    """Получает полные метаданные статьи по DOI из OpenAlex"""
    url = "https://api.openalex.org/works"
    params = {
        "filter": f"doi:{doi}",
        "per_page": 1
    }
    
    data = smart_get(url, params)
    if not data or not data.get("results"):
        return None
    
    work = data["results"][0]
    return parse_openalex_publication(work)

def parse_openalex_publication(item: Dict) -> Dict:
    """Парсит публикацию из OpenAlex с полной информацией"""
    try:
        pub = {}
        
        pub['id'] = item.get('id', '')
        pub['doi'] = item.get('doi', '').replace('https://doi.org/', '')
        pub['title'] = item.get('title', 'No title')
        pub['publication_year'] = item.get('publication_year')
        pub['publication_date'] = item.get('publication_date')
        
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
            author_name = auth.get('author', {}).get('display_name', '')
            author_orcid = auth.get('author', {}).get('orcid', '')
            
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
        
        pub['created_date'] = item.get('created_date')
        pub['updated_date'] = item.get('updated_date')
        
        pub['source_category'] = 'articles'
        
        return pub
        
    except Exception as e:
        if SHOW_DEBUG_LOGS:
            print(f"⚠️ Ошибка парсинга публикации: {e}")
        return None

class JournalAnalyzer:
    """Класс для анализа журнала по ISSN"""
    
    def __init__(self, issn: str, period, max_workers: int = 8):
        self.issn = normalize_issn(issn)
        self.period = period
        self.max_workers = max_workers
        self.articles = []  # Список статей журнала
        self.citing_dois = {}  # {doi: [citing_dois]}
        self.articles_metadata = {}  # {doi: metadata}
        self.citing_metadata = {}  # {doi: metadata}
        self.stats = {}
        self.detailed_citations = {}
        self.citation_dynamics = {}
        self.cumulative_citations = {}
        self.heatmap_data = {}
        self.topics_analysis = {}
        self._cache = {}
        
    def _parse_period(self):
        """Парсит период в формат для OpenAlex API"""
        if isinstance(self.period, list):
            return "|".join(f"publication_year:{y}" for y in self.period)
        elif isinstance(self.period, tuple):
            return f"publication_year:{self.period[0]}-{self.period[1]}"
        else:
            return f"publication_year:{self.period}"
    
    def _collect_articles(self, progress_callback=None):
        """Этап 1: Сбор всех статей журнала за период"""
        if progress_callback:
            progress_callback(0, 1, "stage_1", 0, 0, "")
        
        base_url = "https://api.openalex.org/works"
        period_filter = self._parse_period()
        
        articles = []
        cursor = "*"
        page = 0
        
        while True:
            page += 1
            data = smart_get(base_url, {
                "filter": f"primary_location.source.issn:{self.issn},{period_filter}",
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
                    "OpenAlex_ID": w.get("id", "").replace("https://openalex.org/", ""),
                    "Year": w.get("publication_year"),
                    "Cited_by_count": w.get("cited_by_count", 0),
                    "Publication_Date": w.get("publication_date")
                })
            
            if progress_callback:
                progress_callback(len(articles), None, "stage_1", len(articles), None, "")
            
            cursor = data.get("meta", {}).get("next_cursor")
            if not cursor:
                break
        
        self.articles = articles
        return articles
    
    def _collect_citing_dois(self, progress_callback=None):
        """Этап 2: Сбор цитирующих DOI для каждой статьи"""
        if not self.articles:
            return {}
        
        total = len([a for a in self.articles if a['Cited_by_count'] > 0 and a['DOI'] != "N/A"])
        processed = 0
        
        citing_map = {}
        futures = {}
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            for _, article in enumerate(self.articles):
                if article['Cited_by_count'] > 0 and article['DOI'] != "N/A":
                    future = executor.submit(get_citing_dois, article['OpenAlex_ID'])
                    futures[future] = article['DOI']
            
            for future in futures:
                doi = futures[future]
                try:
                    citing_map[doi] = future.result()
                    processed += 1
                    if progress_callback:
                        progress_callback(processed, total, "stage_2", processed, total, "")
                except Exception as e:
                    if SHOW_DEBUG_LOGS:
                        print(f"⚠️ Ошибка получения цитирований для {doi}: {e}")
                    citing_map[doi] = []
        
        self.citing_dois = citing_map
        return citing_map
    
    def _fetch_articles_metadata(self, progress_callback=None):
        """Этап 3: Получение расширенных метаданных для анализируемых статей"""
        if not self.articles:
            return {}
        
        all_dois = [a['DOI'] for a in self.articles if a['DOI'] != "N/A"]
        total = len(all_dois)
        processed = 0
        
        metadata = {}
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(fetch_article_metadata, doi): doi for doi in all_dois}
            
            for future in futures:
                doi = futures[future]
                try:
                    result = future.result()
                    if result:
                        metadata[doi] = result
                    processed += 1
                    if progress_callback:
                        progress_callback(processed, total, "stage_3", processed, total, doi)
                except Exception as e:
                    if SHOW_DEBUG_LOGS:
                        print(f"⚠️ Ошибка получения метаданных для {doi}: {e}")
                    processed += 1
        
        self.articles_metadata = metadata
        return metadata
    
    def _fetch_citing_metadata(self, progress_callback=None):
        """Этап 4: Получение расширенных метаданных для цитирующих работ"""
        all_citing_dois = set()
        for citing_list in self.citing_dois.values():
            all_citing_dois.update(citing_list)
        
        all_citing_dois = list(all_citing_dois)
        total = len(all_citing_dois)
        processed = 0
        
        metadata = {}
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(fetch_article_metadata, doi): doi for doi in all_citing_dois}
            
            for future in futures:
                doi = futures[future]
                try:
                    result = future.result()
                    if result:
                        metadata[doi] = result
                    processed += 1
                    if progress_callback:
                        progress_callback(processed, total, "stage_4", processed, total, doi)
                except Exception as e:
                    if SHOW_DEBUG_LOGS:
                        print(f"⚠️ Ошибка получения метаданных для цитирующей {doi}: {e}")
                    processed += 1
        
        self.citing_metadata = metadata
        return metadata
    
    def _calculate_stats(self):
        """Этап 5: Расчет всех статистик"""
        stats = {}
        
        # Базовые метрики
        total_pubs = len(self.articles)
        total_citations = sum(a['Cited_by_count'] for a in self.articles)
        avg_citations = total_citations / total_pubs if total_pubs > 0 else 0
        
        # h-index, g-index, i10-index, i100-index
        citations_list = [a['Cited_by_count'] for a in self.articles]
        citations_sorted = sorted([c for c in citations_list if c > 0], reverse=True)
        
        h_index = 0
        for i, c in enumerate(citations_sorted, 1):
            if c >= i:
                h_index = i
            else:
                break
        
        g_index = 0
        total_citations_sorted = 0
        for i, c in enumerate(citations_sorted, 1):
            total_citations_sorted += c
            if total_citations_sorted >= i**2:
                g_index = i
        
        i10_index = sum(1 for c in citations_list if c >= 10)
        i100_index = sum(1 for c in citations_list if c >= 100)
        
        # Open Access
        oa_statuses = {'gold': 0, 'hybrid': 0, 'green': 0, 'bronze': 0, 'closed': 0, 'diamond': 0, 'unknown': 0}
        oa_pubs = 0
        
        for article in self.articles:
            doi = article['DOI']
            if doi in self.articles_metadata:
                meta = self.articles_metadata[doi]
                status = meta.get('open_access_status', 'unknown')
                if status in oa_statuses:
                    oa_statuses[status] += 1
                else:
                    oa_statuses['unknown'] += 1
                if meta.get('is_oa', False):
                    oa_pubs += 1
            else:
                oa_statuses['unknown'] += 1
        
        # Уникальные авторы, аффилиации, страны
        unique_authors = set()
        unique_affiliations = set()
        unique_countries = set()
        author_count_per_paper = []
        affiliation_count_per_paper = []
        country_count_per_paper = []
        international_collab_count = 0
        
        for article in self.articles:
            doi = article['DOI']
            if doi in self.articles_metadata:
                meta = self.articles_metadata[doi]
                authors = meta.get('authors', [])
                affiliations = meta.get('affiliations', [])
                countries = meta.get('affiliation_countries', [])
                
                unique_authors.update(authors)
                unique_affiliations.update(affiliations)
                unique_countries.update(countries)
                
                author_count_per_paper.append(len(authors))
                affiliation_count_per_paper.append(len(set(affiliations)))
                country_count_per_paper.append(len(set(countries)))
                
                # Международные коллаборации
                country_codes = set()
                for inst in meta.get('institutions', []):
                    cc = inst.get('country_code', '')
                    if cc:
                        country_codes.add(cc)
                if len(country_codes) > 1:
                    international_collab_count += 1
        
        avg_authors_per_paper = np.mean(author_count_per_paper) if author_count_per_paper else 0
        avg_affiliations_per_paper = np.mean(affiliation_count_per_paper) if affiliation_count_per_paper else 0
        avg_countries_per_paper = np.mean(country_count_per_paper) if country_count_per_paper else 0
        international_collab_rate = international_collab_count / total_pubs if total_pubs > 0 else 0
        
        # Цитирующие работы
        all_citing_authors = set()
        all_citing_affiliations = set()
        all_citing_countries = set()
        all_citing_journals = set()
        all_citing_publishers = set()
        
        for citing_list in self.citing_dois.values():
            for citing_doi in citing_list:
                if citing_doi in self.citing_metadata:
                    meta = self.citing_metadata[citing_doi]
                    all_citing_authors.update(meta.get('authors', []))
                    all_citing_affiliations.update(meta.get('affiliations', []))
                    all_citing_countries.update(meta.get('affiliation_countries', []))
                    all_citing_journals.add(meta.get('journal_name', ''))
                    all_citing_publishers.add(meta.get('publisher', ''))
        
        total_citing_works = sum(len(c) for c in self.citing_dois.values())
        
        stats = {
            'total_publications': total_pubs,
            'total_citations': total_citations,
            'avg_citations': avg_citations,
            'h_index': h_index,
            'g_index': g_index,
            'i10_index': i10_index,
            'i100_index': i100_index,
            'oa_statuses': oa_statuses,
            'oa_pubs': oa_pubs,
            'unique_authors': len(unique_authors),
            'unique_affiliations': len(unique_affiliations),
            'unique_countries': len(unique_countries),
            'avg_authors_per_paper': avg_authors_per_paper,
            'avg_affiliations_per_paper': avg_affiliations_per_paper,
            'avg_countries_per_paper': avg_countries_per_paper,
            'international_collab_rate': international_collab_rate,
            'total_citing_works': total_citing_works,
            'unique_citing_authors': len(all_citing_authors),
            'unique_citing_affiliations': len(all_citing_affiliations),
            'unique_citing_countries': len(all_citing_countries),
            'unique_citing_journals': len(all_citing_journals),
            'unique_citing_publishers': len(all_citing_publishers),
            'active_years': len(set(a['Year'] for a in self.articles if a['Year']))
        }
        
        self.stats = stats
        
        # Расчет дополнительных метрик
        self._calculate_author_analysis()
        self._calculate_affiliation_analysis()
        self._calculate_geographic_analysis()
        self._calculate_citation_dynamics()
        self._calculate_cumulative_citations()
        self._calculate_heatmap()
        self._calculate_most_cited()
        self._calculate_citing_analysis()
        self._calculate_topics_analysis()
        self._calculate_detailed_citations()
        
        return stats
    
    def _calculate_author_analysis(self):
        """Анализ авторов (топ 30)"""
        author_stats = defaultdict(lambda: {'count': 0, 'citations': 0, 'orcids': [], 'affiliations': [], 'countries': []})
        
        for article in self.articles:
            doi = article['DOI']
            if doi in self.articles_metadata:
                meta = self.articles_metadata[doi]
                authors = meta.get('authors_with_orcids', [])
                citations = article['Cited_by_count']
                affils = meta.get('affiliations', [])
                countries = meta.get('affiliation_countries', [])
                
                for auth in authors:
                    name = auth.get('name', '')
                    orcid = auth.get('orcid', '')
                    if name:
                        author_stats[name]['count'] += 1
                        author_stats[name]['citations'] += citations
                        if orcid:
                            author_stats[name]['orcids'].append(orcid)
                        author_stats[name]['affiliations'].extend(affils)
                        author_stats[name]['countries'].extend(countries)
        
        # Сортируем по количеству публикаций
        sorted_authors = sorted(
            author_stats.items(),
            key=lambda x: x[1]['count'],
            reverse=True
        )[:30]
        
        self.author_analysis = [
            {
                'name': name,
                'count': data['count'],
                'citations': data['citations'],
                'orcid': list(set(data['orcids']))[0] if data['orcids'] else '',
                'affiliations': list(set(data['affiliations']))[:3],
                'countries': list(set(data['countries']))[:3]
            }
            for name, data in sorted_authors
        ]
    
    def _calculate_affiliation_analysis(self):
        """Анализ аффилиаций (топ 30)"""
        affil_stats = defaultdict(lambda: {'count': 0, 'citations': 0})
        
        for article in self.articles:
            doi = article['DOI']
            if doi in self.articles_metadata:
                meta = self.articles_metadata[doi]
                affils = meta.get('affiliations', [])
                citations = article['Cited_by_count']
                
                for affil in set(affils):
                    if affil:
                        affil_stats[affil]['count'] += 1
                        affil_stats[affil]['citations'] += citations
        
        sorted_affils = sorted(
            affil_stats.items(),
            key=lambda x: x[1]['count'],
            reverse=True
        )[:30]
        
        self.affiliation_analysis = [
            {
                'name': name,
                'count': data['count'],
                'citations': data['citations']
            }
            for name, data in sorted_affils
        ]
    
    def _calculate_geographic_analysis(self):
        """Географический анализ"""
        # 5.3.1 Unique Countries per Publication
        country_per_pub = []
        for article in self.articles:
            doi = article['DOI']
            if doi in self.articles_metadata:
                meta = self.articles_metadata[doi]
                countries = set()
                for inst in meta.get('institutions', []):
                    cc = inst.get('country_code', '')
                    if cc:
                        countries.add(cc)
                country_per_pub.append(list(countries))
        
        self.geo_countries_per_pub = country_per_pub
        
        # 5.3.2 Authors per Country
        author_country_counts = defaultdict(int)
        for article in self.articles:
            doi = article['DOI']
            if doi in self.articles_metadata:
                meta = self.articles_metadata[doi]
                for inst in meta.get('institutions', []):
                    cc = inst.get('country_code', '')
                    if cc:
                        author_country_counts[cc] += 1
        
        self.geo_authors_per_country = dict(author_country_counts)
        
        # 5.3.3 Collaboration Patterns
        single_country = 0
        multi_country = 0
        for countries in country_per_pub:
            if len(set(countries)) <= 1:
                single_country += 1
            else:
                multi_country += 1
        
        total_pubs = len(self.articles)
        self.geo_collab_patterns = {
            'single_country': single_country,
            'single_country_pct': single_country / total_pubs * 100 if total_pubs > 0 else 0,
            'multi_country': multi_country,
            'multi_country_pct': multi_country / total_pubs * 100 if total_pubs > 0 else 0
        }
        
        # 5.3.4 Collaboration Couples
        country_pairs = defaultdict(int)
        for countries in country_per_pub:
            if len(set(countries)) > 1:
                unique_countries = list(set(countries))
                for i in range(len(unique_countries)):
                    for j in range(i + 1, len(unique_countries)):
                        pair = tuple(sorted([unique_countries[i], unique_countries[j]]))
                        country_pairs[pair] += 1
        
        self.geo_collab_couples = dict(sorted(
            country_pairs.items(),
            key=lambda x: x[1],
            reverse=True
        )[:20])
    
    def _calculate_citation_dynamics(self):
        """6.1 Citation Dynamics by Year"""
        dynamics = defaultdict(lambda: defaultdict(int))
        first_citation_lags = []
        
        # Собираем все цитирования
        for article in self.articles:
            pub_year = article['Year']
            pub_date = article.get('Publication_Date')
            pub_doi = article['DOI']
            
            if pub_doi in self.citing_dois:
                for citing_doi in self.citing_dois[pub_doi]:
                    if citing_doi in self.citing_metadata:
                        citing_meta = self.citing_metadata[citing_doi]
                        citing_year = citing_meta.get('publication_year')
                        citing_date = citing_meta.get('publication_date')
                        
                        if citing_year:
                            dynamics[pub_year][citing_year] += 1
                            
                            # First citation analysis
                            if pub_date and citing_date:
                                try:
                                    pub_dt = datetime.fromisoformat(pub_date.replace('Z', '+00:00'))
                                    citing_dt = datetime.fromisoformat(citing_date.replace('Z', '+00:00'))
                                    lag_days = (citing_dt - pub_dt).days
                                    if lag_days > 0:
                                        first_citation_lags.append(lag_days / 365.25)
                                except:
                                    pass
        
        self.citation_dynamics = dict(dynamics)
        
        # First citation statistics
        if first_citation_lags:
            self.first_citation_stats = {
                'min': min(first_citation_lags),
                'max': max(first_citation_lags),
                'avg': np.mean(first_citation_lags),
                'median': np.median(first_citation_lags)
            }
        else:
            self.first_citation_stats = {'min': 0, 'max': 0, 'avg': 0, 'median': 0}
    
    def _calculate_cumulative_citations(self):
        """6.2 Cumulative Citations"""
        all_years = sorted(set(
            [a['Year'] for a in self.articles if a['Year']] +
            [y for dynamics in self.citation_dynamics.values() for y in dynamics.keys()]
        ))
        
        cumulative = {}
        running_total = 0
        
        for year in all_years:
            year_total = 0
            for pub_year, cit_years in self.citation_dynamics.items():
                if pub_year <= year:
                    year_total += cit_years.get(year, 0)
            running_total += year_total
            cumulative[year] = running_total
        
        self.cumulative_citations = cumulative
    
    def _calculate_heatmap(self):
        """6.3 Citation Network Heatmap"""
        pub_years = sorted(set(a['Year'] for a in self.articles if a['Year']))
        cit_years = sorted(set(
            y for dynamics in self.citation_dynamics.values() 
            for y in dynamics.keys()
        ))
        
        heatmap = {}
        for pub_year in pub_years:
            heatmap[pub_year] = {}
            for cit_year in cit_years:
                heatmap[pub_year][cit_year] = self.citation_dynamics.get(pub_year, {}).get(cit_year, 0)
        
        self.heatmap_data = heatmap
    
    def _calculate_most_cited(self):
        """6.4 Most Cited Publications"""
        sorted_articles = sorted(
            self.articles,
            key=lambda x: x['Cited_by_count'],
            reverse=True
        )[:20]
        
        self.most_cited = []
        for idx, article in enumerate(sorted_articles, 1):
            doi = article['DOI']
            meta = self.articles_metadata.get(doi, {})
            
            authors = meta.get('authors', [])
            author_display = ', '.join(authors[:3])
            if len(authors) > 3:
                author_display += f' +{len(authors) - 3} more'
            
            citations_per_year = article['Cited_by_count'] / max(1, 2026 - article['Year'])
            
            self.most_cited.append({
                'rank': idx,
                'title': meta.get('title', 'No title'),
                'year': article['Year'],
                'citations': article['Cited_by_count'],
                'citations_per_year': citations_per_year,
                'authors': author_display,
                'doi': doi
            })
    
    def _calculate_citing_analysis(self):
        """7. Citing Works Analysis"""
        citing_authors = defaultdict(int)
        citing_affiliations = defaultdict(int)
        citing_countries = defaultdict(int)
        citing_journals = defaultdict(int)
        citing_publishers = defaultdict(int)
        
        for citing_list in self.citing_dois.values():
            for citing_doi in citing_list:
                if citing_doi in self.citing_metadata:
                    meta = self.citing_metadata[citing_doi]
                    
                    for author in meta.get('authors', []):
                        if author:
                            citing_authors[author] += 1
                    
                    for affil in meta.get('affiliations', []):
                        if affil:
                            citing_affiliations[affil] += 1
                    
                    for country in meta.get('affiliation_countries', []):
                        if country:
                            citing_countries[country] += 1
                    
                    journal = meta.get('journal_name', '')
                    if journal:
                        citing_journals[journal] += 1
                    
                    publisher = meta.get('publisher', '')
                    if publisher:
                        citing_publishers[publisher] += 1
        
        self.citing_analysis = {
            'authors': dict(sorted(citing_authors.items(), key=lambda x: x[1], reverse=True)[:30]),
            'affiliations': dict(sorted(citing_affiliations.items(), key=lambda x: x[1], reverse=True)[:30]),
            'countries': dict(sorted(citing_countries.items(), key=lambda x: x[1], reverse=True)[:30]),
            'journals': dict(sorted(citing_journals.items(), key=lambda x: x[1], reverse=True)[:30]),
            'publishers': dict(sorted(citing_publishers.items(), key=lambda x: x[1], reverse=True)[:30])
        }
    
    def _calculate_topics_analysis(self):
        """8. Topics Analysis"""
        topic_stats = defaultdict(lambda: {
            'analyzed_count': 0,
            'citing_count': 0,
            'first_year': None,
            'peak_year': None,
            'years': defaultdict(int)
        })
        
        # Анализируемые статьи
        for article in self.articles:
            doi = article['DOI']
            year = article['Year']
            if doi in self.articles_metadata:
                meta = self.articles_metadata[doi]
                topics = meta.get('topics', [])
                
                for topic in topics:
                    name = topic.get('display_name', '')
                    if name:
                        topic_stats[name]['analyzed_count'] += 1
                        if topic_stats[name]['first_year'] is None or year < topic_stats[name]['first_year']:
                            topic_stats[name]['first_year'] = year
                        topic_stats[name]['years'][year] += 1
        
        # Цитирующие статьи
        for citing_list in self.citing_dois.values():
            for citing_doi in citing_list:
                if citing_doi in self.citing_metadata:
                    meta = self.citing_metadata[citing_doi]
                    topics = meta.get('topics', [])
                    citing_year = meta.get('publication_year', 0)
                    
                    for topic in topics:
                        name = topic.get('display_name', '')
                        if name:
                            topic_stats[name]['citing_count'] += 1
                            if topic_stats[name]['first_year'] is None or citing_year < topic_stats[name]['first_year']:
                                topic_stats[name]['first_year'] = citing_year
                            if citing_year:
                                topic_stats[name]['years'][citing_year] += 1
        
        # Расчет нормированных значений и пиковых годов
        total_analyzed = len(self.articles)
        total_citing = sum(len(c) for c in self.citing_dois.values())
        
        for name, data in topic_stats.items():
            data['analyzed_norm'] = data['analyzed_count'] / total_analyzed if total_analyzed > 0 else 0
            data['citing_norm'] = data['citing_count'] / total_citing if total_citing > 0 else 0
            data['total_norm'] = data['analyzed_norm'] + data['citing_norm']
            
            if data['years']:
                data['peak_year'] = max(data['years'].items(), key=lambda x: x[1])[0]
            else:
                data['peak_year'] = data['first_year']
        
        # Сортируем по total_norm
        self.topics_analysis = dict(sorted(
            topic_stats.items(),
            key=lambda x: x[1]['total_norm'],
            reverse=True
        )[:30])
        
        # Топ-10 по цитированиям для каждой категории
        self.top_cited_topics = self._get_top_cited_by_category('topics')
        self.top_cited_subtopics = self._get_top_cited_by_category('subtopics')
        self.top_cited_fields = self._get_top_cited_by_category('fields')
        self.top_cited_domains = self._get_top_cited_by_category('domains')
        self.top_cited_concepts = self._get_top_cited_by_category('concepts')
    
    def _get_top_cited_by_category(self, category: str) -> Dict:
        """Получает топ-10 по цитированиям для указанной категории"""
        category_counts = defaultdict(int)
        
        for article in self.articles:
            doi = article['DOI']
            if doi in self.articles_metadata:
                meta = self.articles_metadata[doi]
                items = meta.get(category, [])
                for item in items:
                    if item:
                        category_counts[item] += article['Cited_by_count']
        
        return dict(sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:10])
    
    def _calculate_detailed_citations(self):
        """9. Detailed Citations for Analyzed Works"""
        detailed = {}
        
        for article in self.articles:
            doi = article['DOI']
            if doi in self.citing_dois and self.citing_dois[doi]:
                citations_list = []
                for citing_doi in self.citing_dois[doi]:
                    if citing_doi in self.citing_metadata:
                        meta = self.citing_metadata[citing_doi]
                        
                        # Расчет задержки цитирования
                        citation_lag = 0
                        pub_date = article.get('Publication_Date')
                        citing_date = meta.get('publication_date')
                        if pub_date and citing_date:
                            try:
                                pub_dt = datetime.fromisoformat(pub_date.replace('Z', '+00:00'))
                                citing_dt = datetime.fromisoformat(citing_date.replace('Z', '+00:00'))
                                citation_lag = (citing_dt - pub_dt).days / 365.25
                            except:
                                pass
                        
                        citations_list.append({
                            'citing_title': meta.get('title', 'No title'),
                            'citing_year': meta.get('publication_year', 'Unknown'),
                            'citing_date': meta.get('publication_date', ''),
                            'citing_journal': meta.get('journal_name', 'Unknown'),
                            'citing_publisher': meta.get('publisher', 'Unknown'),
                            'citing_doi': citing_doi,
                            'citation_lag': citation_lag,
                            'citing_authors': meta.get('authors', []),
                            'citing_countries': meta.get('affiliation_countries', []),
                            'citing_topics': [t.get('display_name', '') for t in meta.get('topics', [])[:5]]
                        })
                
                meta = self.articles_metadata.get(doi, {})
                detailed[doi] = {
                    'title': meta.get('title', 'No title'),
                    'year': article['Year'],
                    'doi': doi,
                    'total_citations': len(citations_list),
                    'citations': citations_list
                }
        
        self.detailed_citations = detailed
    
    def run_analysis(self, progress_callback=None):
        """Запускает полный анализ с обратными вызовами прогресса"""
        # Этап 1: Сбор статей журнала
        if progress_callback:
            progress_callback(0, 1, "stage_1", 0, 0, "")
        
        self._collect_articles(progress_callback)
        
        # Этап 2: Сбор цитирующих DOI
        if progress_callback:
            progress_callback(0, 1, "stage_2", 0, 0, "")
        
        self._collect_citing_dois(progress_callback)
        
        # Этап 3: Метаданные анализируемых статей
        if progress_callback:
            progress_callback(0, 1, "stage_3", 0, 0, "")
        
        self._fetch_articles_metadata(progress_callback)
        
        # Этап 4: Метаданные цитирующих работ
        if progress_callback:
            progress_callback(0, 1, "stage_4", 0, 0, "")
        
        self._fetch_citing_metadata(progress_callback)
        
        # Этап 5: Расчет статистики
        if progress_callback:
            progress_callback(0, 1, "stage_5", 0, 0, "")
        
        self._calculate_stats()
        
        if progress_callback:
            progress_callback(1, 1, "stage_5", 1, 1, "complete")
        
        return self.stats
    
    def get_results(self):
        """Возвращает все результаты анализа"""
        return {
            'articles': self.articles,
            'citing_dois': self.citing_dois,
            'articles_metadata': self.articles_metadata,
            'citing_metadata': self.citing_metadata,
            'stats': self.stats,
            'author_analysis': self.author_analysis,
            'affiliation_analysis': self.affiliation_analysis,
            'geo_countries_per_pub': self.geo_countries_per_pub,
            'geo_authors_per_country': self.geo_authors_per_country,
            'geo_collab_patterns': self.geo_collab_patterns,
            'geo_collab_couples': self.geo_collab_couples,
            'citation_dynamics': self.citation_dynamics,
            'first_citation_stats': self.first_citation_stats,
            'cumulative_citations': self.cumulative_citations,
            'heatmap_data': self.heatmap_data,
            'most_cited': self.most_cited,
            'citing_analysis': self.citing_analysis,
            'topics_analysis': self.topics_analysis,
            'top_cited_topics': self.top_cited_topics,
            'top_cited_subtopics': self.top_cited_subtopics,
            'top_cited_fields': self.top_cited_fields,
            'top_cited_domains': self.top_cited_domains,
            'top_cited_concepts': self.top_cited_concepts,
            'detailed_citations': self.detailed_citations
        }

# ============================================
# ФУНКЦИИ ДЛЯ ГЕНЕРАЦИИ HTML ОТЧЕТА (АДАПТИРОВАННЫЕ)
# ============================================

def generate_html_report_journal(results: Dict, images: Dict[str, str], 
                                 logo_base64: Optional[str] = None, 
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
    
    stats = results.get('stats', {})
    articles = results.get('articles', [])
    citing_dois = results.get('citing_dois', {})
    articles_metadata = results.get('articles_metadata', {})
    citing_metadata = results.get('citing_metadata', {})
    author_analysis = results.get('author_analysis', [])
    affiliation_analysis = results.get('affiliation_analysis', [])
    geo_countries_per_pub = results.get('geo_countries_per_pub', [])
    geo_authors_per_country = results.get('geo_authors_per_country', {})
    geo_collab_patterns = results.get('geo_collab_patterns', {})
    geo_collab_couples = results.get('geo_collab_couples', {})
    citation_dynamics = results.get('citation_dynamics', {})
    first_citation_stats = results.get('first_citation_stats', {})
    cumulative_citations = results.get('cumulative_citations', {})
    heatmap_data = results.get('heatmap_data', {})
    most_cited = results.get('most_cited', [])
    citing_analysis = results.get('citing_analysis', {})
    topics_analysis = results.get('topics_analysis', {})
    top_cited_topics = results.get('top_cited_topics', {})
    top_cited_subtopics = results.get('top_cited_subtopics', {})
    top_cited_fields = results.get('top_cited_fields', {})
    top_cited_domains = results.get('top_cited_domains', {})
    top_cited_concepts = results.get('top_cited_concepts', {})
    detailed_citations = results.get('detailed_citations', {})
    
    total_pubs = stats.get('total_publications', 0)
    total_citations = stats.get('total_citations', 0)
    avg_citations = stats.get('avg_citations', 0)
    h_index = stats.get('h_index', 0)
    g_index = stats.get('g_index', 0)
    i10_index = stats.get('i10_index', 0)
    i100_index = stats.get('i100_index', 0)
    oa_statuses = stats.get('oa_statuses', {})
    unique_authors = stats.get('unique_authors', 0)
    unique_affiliations = stats.get('unique_affiliations', 0)
    unique_countries = stats.get('unique_countries', 0)
    avg_authors_per_paper = stats.get('avg_authors_per_paper', 0)
    avg_affiliations_per_paper = stats.get('avg_affiliations_per_paper', 0)
    avg_countries_per_paper = stats.get('avg_countries_per_paper', 0)
    international_collab_rate = stats.get('international_collab_rate', 0)
    total_citing_works = stats.get('total_citing_works', 0)
    unique_citing_authors = stats.get('unique_citing_authors', 0)
    unique_citing_affiliations = stats.get('unique_citing_affiliations', 0)
    unique_citing_countries = stats.get('unique_citing_countries', 0)
    unique_citing_journals = stats.get('unique_citing_journals', 0)
    unique_citing_publishers = stats.get('unique_citing_publishers', 0)
    
    # Подготовка данных для таблиц
    pub_years = sorted(set(a['Year'] for a in articles if a['Year']))
    cit_years = sorted(set(
        y for dynamics in citation_dynamics.values() 
        for y in dynamics.keys()
    ))
    
    # Citation Dynamics Table
    dyn_rows = []
    for pub_year in sorted(citation_dynamics.keys()):
        for cit_year in sorted(citation_dynamics[pub_year].keys()):
            dyn_rows.append({
                'pub_year': pub_year,
                'cit_year': cit_year,
                'count': citation_dynamics[pub_year][cit_year]
            })
    
    # Cumulative Citations Table
    cum_rows = []
    for year in sorted(cumulative_citations.keys()):
        cum_rows.append({
            'year': year,
            'citations': cumulative_citations[year]
        })
    
    # Heatmap Table
    heatmap_rows = []
    for pub_year in pub_years:
        row = {'pub_year': pub_year}
        for cit_year in cit_years:
            row[str(cit_year)] = heatmap_data.get(pub_year, {}).get(cit_year, 0)
        heatmap_rows.append(row)
    
    # Topics Table
    topic_rows = []
    for name, data in list(topics_analysis.items())[:20]:
        topic_rows.append({
            'name': name,
            'analyzed_count': data['analyzed_count'],
            'citing_count': data['citing_count'],
            'analyzed_norm': data.get('analyzed_norm', 0),
            'citing_norm': data.get('citing_norm', 0),
            'total_norm': data.get('total_norm', 0),
            'first_year': data.get('first_year', ''),
            'peak_year': data.get('peak_year', '')
        })
    
    # Max color for heatmap
    max_heatmap_val = 0
    for pub_year in heatmap_data:
        for cit_year in heatmap_data[pub_year]:
            max_heatmap_val = max(max_heatmap_val, heatmap_data[pub_year][cit_year])
    
    # Build HTML
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>{t('app_title')} - {t('journal_analysis_title')}</title>
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
                padding: 25px 20px;
                overflow-y: auto;
                z-index: 1000;
            }}
            .sidebar::-webkit-scrollbar {{
                width: 4px;
            }}
            .sidebar::-webkit-scrollbar-track {{
                background: rgba(255,255,255,0.1);
            }}
            .sidebar::-webkit-scrollbar-thumb {{
                background: rgba(255,255,255,0.3);
                border-radius: 2px;
            }}
            .sidebar h3 {{
                margin-bottom: 20px;
                font-size: 18px;
                font-weight: 600;
                color: white;
                border-bottom: 2px solid rgba(255,255,255,0.2);
                padding-bottom: 12px;
            }}
            .sidebar .nav-section {{
                margin-bottom: 15px;
            }}
            .sidebar .nav-section-title {{
                font-size: 12px;
                font-weight: 600;
                color: rgba(255,255,255,0.7);
                text-transform: uppercase;
                letter-spacing: 1px;
                margin: 12px 0 6px 0;
                padding-left: 8px;
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
                transform: translateX(4px);
            }}
            .sidebar a .nav-icon {{
                font-size: 16px;
                width: 24px;
            }}
            .sidebar a.sub {{
                padding-left: 32px;
                font-size: 13px;
                opacity: 0.85;
            }}
            .sidebar a.sub:hover {{
                opacity: 1;
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
            .header h1 {{
                color: white;
                border-bottom: none;
                margin: 0;
                font-size: 28px;
            }}
            .header .subtitle {{
                opacity: 0.9;
                font-size: 14px;
                margin-top: 4px;
            }}
            .header .date {{
                opacity: 0.9;
                font-size: 13px;
            }}
            .header-logo {{
                max-height: 80px;
                max-width: 200px;
            }}
            .header-logo-app {{
                max-height: 70px;
                max-width: 200px;
            }}
            .section {{
                background: white;
                border-radius: 12px;
                padding: 25px;
                margin-bottom: 25px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);
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
                gap: 12px;
            }}
            .section-title .icon {{
                font-size: 24px;
            }}
            .metrics-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
                gap: 12px;
                margin: 15px 0;
            }}
            .metric-card {{
                background: #f8f9fa;
                padding: 14px;
                border-radius: 8px;
                border-left: 4px solid {primary};
                text-align: center;
                transition: transform 0.2s;
            }}
            .metric-card:hover {{
                transform: translateY(-3px);
                box-shadow: 0 4px 12px rgba(0,0,0,0.08);
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
            .metric-value.small {{
                font-size: 20px;
            }}
            .oa-badges {{
                display: flex;
                flex-wrap: wrap;
                gap: 10px;
                margin: 10px 0;
            }}
            .badge {{
                display: inline-block;
                padding: 4px 14px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: 600;
            }}
            .badge-gold {{ background: #ffd700; color: #333; }}
            .badge-hybrid {{ background: #ff6b35; color: white; }}
            .badge-green {{ background: #2ecc71; color: white; }}
            .badge-bronze {{ background: #cd7f32; color: white; }}
            .badge-closed {{ background: #95a5a6; color: white; }}
            .badge-diamond {{ background: #3498db; color: white; }}
            .badge-unknown {{ background: #bdc3c7; color: #333; }}
            
            .table-container {{
                overflow-x: auto;
                max-height: 600px;
                overflow-y: auto;
                margin: 15px 0;
                border-radius: 8px;
                border: 1px solid #e8e8e8;
            }}
            .table-container table {{
                width: 100%;
                border-collapse: collapse;
                font-size: 13px;
            }}
            .table-container th {{
                position: sticky;
                top: 0;
                z-index: 10;
                background: linear-gradient(135deg, {primary} 0%, {secondary} 100%);
                color: white;
                padding: 10px 12px;
                text-align: left;
                font-weight: 600;
            }}
            .table-container td {{
                padding: 8px 12px;
                border-bottom: 1px solid #eee;
            }}
            .table-container tr:hover {{
                background: rgba({int(hex_to_rgb(primary)[0])}, {int(hex_to_rgb(primary)[1])}, {int(hex_to_rgb(primary)[2])}, 0.05);
            }}
            .table-container tr:nth-child(even) {{
                background: #fafafa;
            }}
            .table-container tr:nth-child(even):hover {{
                background: rgba({int(hex_to_rgb(primary)[0])}, {int(hex_to_rgb(primary)[1])}, {int(hex_to_rgb(primary)[2])}, 0.08);
            }}
            
            .heatmap-cell {{
                text-align: center;
                padding: 6px 8px;
                border-radius: 4px;
                font-weight: 500;
                font-size: 12px;
                min-width: 40px;
            }}
            
            .collapser {{
                background: #f8f9fa;
                padding: 12px 15px;
                margin: 6px 0;
                border-radius: 6px;
                cursor: pointer;
                border: 1px solid #e0e0e0;
                transition: all 0.2s;
                display: flex;
                flex-wrap: wrap;
                align-items: center;
                gap: 10px;
            }}
            .collapser:hover {{
                background: #e9ecef;
                border-color: {primary};
            }}
            .collapser .citation-count {{
                background: {primary};
                color: white;
                padding: 2px 12px;
                border-radius: 12px;
                font-size: 12px;
                font-weight: 600;
            }}
            .collapser .toggle-hint {{
                font-size: 11px;
                color: #999;
                margin-left: auto;
            }}
            .citation-detail {{
                background: white;
                padding: 12px 15px;
                margin: 3px 0 3px 20px;
                border-left: 3px solid {primary};
                border-radius: 4px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            }}
            .citation-detail .cite-meta {{
                font-size: 12px;
                color: #555;
                margin-top: 4px;
            }}
            .citation-detail .cite-meta strong {{
                color: #333;
            }}
            
            .filter-section {{
                background: #f8f9fa;
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 20px;
                border: 1px solid #e0e0e0;
            }}
            .filter-row {{
                display: flex;
                flex-wrap: wrap;
                gap: 15px;
                align-items: end;
            }}
            .filter-row > div {{
                flex: 1;
                min-width: 140px;
            }}
            .filter-row label {{
                display: block;
                font-size: 11px;
                font-weight: 600;
                color: #555;
                margin-bottom: 3px;
            }}
            .filter-row select, .filter-row input {{
                width: 100%;
                padding: 5px 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 12px;
            }}
            
            .topic-card {{
                background: white;
                border-radius: 8px;
                padding: 12px 15px;
                margin-bottom: 8px;
                border-left: 4px solid {primary};
                box-shadow: 0 1px 3px rgba(0,0,0,0.05);
                display: flex;
                flex-wrap: wrap;
                justify-content: space-between;
                align-items: center;
            }}
            .topic-card .topic-name {{
                font-weight: 600;
                color: {primary};
                font-size: 14px;
            }}
            .topic-card .topic-stats {{
                font-size: 12px;
                color: #666;
                display: flex;
                flex-wrap: wrap;
                gap: 12px;
            }}
            .topic-card .topic-stats span {{
                background: #f0f0f0;
                padding: 2px 10px;
                border-radius: 12px;
            }}
            
            .progress-bar-container {{
                background: #f0f0f0;
                border-radius: 8px;
                overflow: hidden;
                height: 18px;
                margin: 2px 0;
                width: 100%;
                max-width: 150px;
            }}
            .progress-bar-fill {{
                height: 100%;
                background: linear-gradient(90deg, {primary}, {secondary});
                border-radius: 8px;
                transition: width 0.5s ease;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-size: 10px;
                font-weight: 600;
            }}
            
            .word-wrap {{
                word-wrap: break-word;
                max-width: 250px;
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
                gap: 15px;
                margin: 10px 0;
            }}
            .collab-box {{
                background: #f8f9fa;
                padding: 12px 15px;
                border-radius: 6px;
                border: 1px solid #ddd;
            }}
            .collab-box h4 {{
                margin: 0 0 6px 0;
                color: #2C3E50;
                font-size: 14px;
            }}
            
            @media print {{
                .sidebar {{ display: none; }}
                .main-content {{ margin-left: 0; }}
            }}
            @media (max-width: 768px) {{
                .sidebar {{ display: none; }}
                .main-content {{ margin-left: 0; padding: 15px; }}
                .filter-row > div {{ min-width: 100px; }}
                .collab-grid {{ grid-template-columns: 1fr; }}
            }}
            
            .sub-section-title {{
                font-size: 17px;
                font-weight: 600;
                color: {primary};
                margin: 20px 0 12px 0;
                padding-left: 10px;
                border-left: 3px solid {primary};
            }}
            .sub-section-title .sub-icon {{
                margin-right: 8px;
            }}
        </style>
    </head>
    <body>
        <div class="sidebar">
            <h3>📊 {t('app_title')}</h3>
            <div class="nav-section">
                <div class="nav-section-title">{t('overview')}</div>
                <a href="#overview"><span class="nav-icon">📊</span> {t('key_metrics')}</a>
                <a href="#oa_breakdown" class="sub"><span class="nav-icon">📖</span> {t('open_access_breakdown')}</a>
                <a href="#citation_dynamics" class="sub"><span class="nav-icon">📈</span> {t('citation_dynamics_by_year')}</a>
                <a href="#cumulative" class="sub"><span class="nav-icon">📊</span> {t('cumulative_citations')}</a>
                <a href="#heatmap" class="sub"><span class="nav-icon">🌐</span> {t('citation_network_heatmap')}</a>
                <a href="#most_cited" class="sub"><span class="nav-icon">⭐</span> {t('most_cited_publications')}</a>
            </div>
            <div class="nav-section">
                <div class="nav-section-title">{t('analyzed_articles')}</div>
                <a href="#author_analysis"><span class="nav-icon">👥</span> {t('author_analysis')}</a>
                <a href="#top_affiliations" class="sub"><span class="nav-icon">🏛️</span> {t('top_affiliations')}</a>
                <a href="#geographic" class="sub"><span class="nav-icon">🌍</span> {t('geographic_analysis')}</a>
            </div>
            <div class="nav-section">
                <div class="nav-section-title">{t('citing_works')}</div>
                <a href="#citing_summary"><span class="nav-icon">📚</span> {t('summary')}</a>
                <a href="#top_citing_authors" class="sub"><span class="nav-icon">👥</span> {t('top_citing_authors')}</a>
                <a href="#top_citing_affiliations" class="sub"><span class="nav-icon">🏛️</span> {t('top_citing_affiliations')}</a>
                <a href="#top_citing_countries" class="sub"><span class="nav-icon">🌍</span> {t('top_citing_countries')}</a>
                <a href="#top_citing_journals" class="sub"><span class="nav-icon">📰</span> {t('top_citing_journals')}</a>
            </div>
            <div class="nav-section">
                <div class="nav-section-title">{t('topics_analysis_title')}</div>
                <a href="#topics_overview"><span class="nav-icon">🏷️</span> {t('topic_overview')}</a>
                <a href="#top_cited_topics" class="sub"><span class="nav-icon">📈</span> {t('top_10_topics')}</a>
                <a href="#top_cited_subtopics" class="sub"><span class="nav-icon">📈</span> {t('top_10_subtopics')}</a>
                <a href="#top_cited_fields" class="sub"><span class="nav-icon">📈</span> {t('top_10_fields')}</a>
                <a href="#top_cited_domains" class="sub"><span class="nav-icon">📈</span> {t('top_10_domains')}</a>
                <a href="#top_cited_concepts" class="sub"><span class="nav-icon">📈</span> {t('top_10_concepts')}</a>
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
        
        <div class="main-content">
            <div class="header">
                <div class="header-left">
                    {f'<img src="data:image/png;base64,{app_logo_base64}" class="header-logo-app" alt="App Logo">' if app_logo_base64 else ''}
                    <div>
                        <h1>{t('journal_analysis_title')}</h1>
                        <div class="subtitle">{t('journal_analysis_subtitle')}</div>
                        <div class="date">ISSN: {results.get('issn', '')} | {t('report_preview')}: {datetime.now().strftime('%d.%m.%Y')}</div>
                    </div>
                </div>
                {f'<img src="data:image/png;base64,{logo_base64}" class="header-logo" alt="Journal Logo">' if logo_base64 else ''}
            </div>
            
            <!-- ==================== OVERVIEW ==================== -->
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
                        <div class="metric-value">{stats.get('oa_pubs', 0)}</div>
                        <div class="metric-label">{t('open_access')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{stats.get('active_years', 0)}</div>
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
                        <div class="metric-value">{avg_authors_per_paper:.1f}</div>
                        <div class="metric-label">{t('avg_authors_per_paper')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{avg_affiliations_per_paper:.1f}</div>
                        <div class="metric-label">{t('avg_affiliations_per_paper')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{avg_countries_per_paper:.1f}</div>
                        <div class="metric-label">{t('avg_countries_per_paper')}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{international_collab_rate*100:.1f}%</div>
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
            </div>
            
            <!-- ==================== OPEN ACCESS BREAKDOWN ==================== -->
            <div id="oa_breakdown" class="section">
                <div class="section-title"><span class="icon">📖</span> {t('open_access_breakdown')}</div>
                <div class="oa-badges">
                    {''.join([
                        f'<span class="badge badge-{status}">{t(status)}: {count}</span>'
                        for status, count in oa_statuses.items() if count > 0
                    ])}
                </div>
                <div style="margin-top: 10px;">
                    {''.join([
                        f'<div style="display:flex;align-items:center;gap:10px;margin:4px 0;">'
                        f'<span style="width:120px;font-size:13px;">{t(status)}</span>'
                        f'<div class="progress-bar-container" style="max-width:300px;">'
                        f'<div class="progress-bar-fill" style="width:{count/total_pubs*100 if total_pubs>0 else 0:.1f}%;">{count}</div>'
                        f'</div>'
                        f'<span style="font-size:12px;color:#666;">{count/total_pubs*100 if total_pubs>0 else 0:.1f}%</span>'
                        f'</div>'
                        for status, count in oa_statuses.items() if count > 0
                    ])}
                </div>
            </div>
            
            <!-- ==================== CITATION DYNAMICS ==================== -->
            <div id="citation_dynamics" class="section">
                <div class="section-title"><span class="icon">📈</span> {t('citation_dynamics_by_year')}</div>
                
                <div class="sub-section-title"><span class="sub-icon">📊</span> {t('citation_dynamics_by_year')}</div>
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>{t('publication_year_col')}</th>
                                <th>{t('citation_year_col')}</th>
                                <th>{t('citations_count_col')}</th>
                            </tr>
                        </thead>
                        <tbody>
                            {''.join([
                                f'<tr><td>{row["pub_year"]}</td><td>{row["cit_year"]}</td><td>{row["count"]}</td></tr>'
                                for row in sorted(dyn_rows, key=lambda x: (x['pub_year'], x['cit_year']))
                            ])}
                        </tbody>
                    </table>
                </div>
                
                <div class="sub-section-title" style="margin-top:20px;"><span class="sub-icon">⏱️</span> {t('first_citation_analysis')}</div>
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-value">{first_citation_stats.get('min', 0):.2f}</div>
                        <div class="metric-label">{t('min')} (years)</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{first_citation_stats.get('max', 0):.2f}</div>
                        <div class="metric-label">{t('max')} (years)</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{first_citation_stats.get('avg', 0):.2f}</div>
                        <div class="metric-label">{t('avg')} (years)</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{first_citation_stats.get('median', 0):.2f}</div>
                        <div class="metric-label">{t('median')} (years)</div>
                    </div>
                </div>
            </div>
            
            <!-- ==================== CUMULATIVE CITATIONS ==================== -->
            <div id="cumulative" class="section">
                <div class="section-title"><span class="icon">📊</span> {t('cumulative_citations')}</div>
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>{t('year')}</th>
                                <th>{t('citations')}</th>
                            </tr>
                        </thead>
                        <tbody>
                            {''.join([
                                f'<tr><td>{row["year"]}</td><td>{row["citations"]:,}</td></tr>'
                                for row in sorted(cum_rows, key=lambda x: x['year'])
                            ])}
                        </tbody>
                    </table>
                </div>
            </div>
            
            <!-- ==================== HEATMAP ==================== -->
            <div id="heatmap" class="section">
                <div class="section-title"><span class="icon">🌐</span> {t('citation_network_heatmap')}</div>
                <div class="table-container" style="max-height:500px;">
                    <table>
                        <thead>
                            <tr>
                                <th>{t('publication_year_col')}</th>
                                {''.join([f'<th>{y}</th>' for y in cit_years])}
                            </tr>
                        </thead>
                        <tbody>
                            {''.join([
                                '<tr>'
                                + f'<td><strong>{row["pub_year"]}</strong></td>'
                                + ''.join([
                                    (lambda val, cit_year_val: 
                                        f'<td class="heatmap-cell" style="background:rgba({int(hex_to_rgb(primary)[0])}, {int(hex_to_rgb(primary)[1])}, {int(hex_to_rgb(primary)[2])}, {val/max_heatmap_val if max_heatmap_val > 0 else 0:.2f}); color:{("white" if val/max_heatmap_val > 0.5 else "#333")};">{val if val > 0 else "-"}</td>'
                                    )(row[str(cit_year)], cit_year)
                                    for cit_year in cit_years
                                ])
                                + '</tr>'
                                for row in heatmap_rows
                            ])}
                        </tbody>
                    </table>
                </div>
                <div style="font-size:12px;color:#666;margin-top:8px;">
                    Color intensity: <span style="background:{primary};padding:2px 10px;border-radius:4px;color:white;">Higher</span> 
                    → <span style="background:{primary}30;padding:2px 10px;border-radius:4px;">Lower</span>
                </div>
            </div>
            
            <!-- ==================== MOST CITED ==================== -->
            <div id="most_cited" class="section">
                <div class="section-title"><span class="icon">⭐</span> {t('most_cited_publications')}</div>
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>{t('rank')}</th>
                                <th>{t('title')}</th>
                                <th>{t('year')}</th>
                                <th>{t('citations')}</th>
                                <th>{t('citations_per_year_col')}</th>
                                <th>{t('authors')}</th>
                                <th>{t('doi')}</th>
                            </tr>
                        </thead>
                        <tbody>
                            {''.join([
                                f'<tr>'
                                f'<td>{row["rank"]}</td>'
                                f'<td class="word-wrap">{html.escape(row["title"])}</td>'
                                f'<td>{row["year"]}</td>'
                                f'<td>{row["citations"]}</td>'
                                f'<td>{row["citations_per_year"]:.1f}</td>'
                                f'<td>{html.escape(row["authors"])}</td>'
                                f'<td><a href="https://doi.org/{row["doi"]}" target="_blank" class="doi-link">{row["doi"][:30]}{"..." if len(row["doi"])>30 else ""}</a></td>'
                                f'</tr>'
                                for row in most_cited
                            ])}
                        </tbody>
                    </table>
                </div>
            </div>
            
            <!-- ==================== AUTHOR ANALYSIS ==================== -->
            <div id="author_analysis" class="section">
                <div class="section-title"><span class="icon">👥</span> {t('author_analysis')}</div>
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
                                f'<tr>'
                                f'<td>{i+1}</td>'
                                f'<td>{html.escape(row["name"])}</td>'
                                f'<td>{row["orcid"][:20] if row["orcid"] else "-"}</td>'
                                f'<td>{", ".join([html.escape(a) for a in row["affiliations"][:2]])}{"..." if len(row["affiliations"])>2 else ""}</td>'
                                f'<td>{", ".join(row["countries"][:2])}{"..." if len(row["countries"])>2 else ""}</td>'
                                f'<td>{row["count"]}</td>'
                                f'<td>{row["citations"]}</td>'
                                f'</tr>'
                                for i, row in enumerate(author_analysis[:30])
                            ])}
                        </tbody>
                    </table>
                </div>
            </div>
            
            <!-- ==================== TOP AFFILIATIONS ==================== -->
            <div id="top_affiliations" class="section">
                <div class="section-title"><span class="icon">🏛️</span> {t('top_affiliations')}</div>
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>{t('rank')}</th>
                                <th>{t('affiliations')}</th>
                                <th>{t('publications_count')}</th>
                                <th>{t('citations_count')}</th>
                            </tr>
                        </thead>
                        <tbody>
                            {''.join([
                                f'<tr>'
                                f'<td>{i+1}</td>'
                                f'<td class="word-wrap">{html.escape(row["name"])}</td>'
                                f'<td>{row["count"]}</td>'
                                f'<td>{row["citations"]}</td>'
                                f'</tr>'
                                for i, row in enumerate(affiliation_analysis[:30])
                            ])}
                        </tbody>
                    </table>
                </div>
            </div>
            
            <!-- ==================== GEOGRAPHIC ANALYSIS ==================== -->
            <div id="geographic" class="section">
                <div class="section-title"><span class="icon">🌍</span> {t('geographic_analysis')}</div>
                
                <div class="sub-section-title"><span class="sub-icon">🌐</span> {t('unique_countries_per_publication')}</div>
                <div style="font-size:13px;color:#666;margin-bottom:10px;">
                    Each publication counted once per unique country
                </div>
                <div class="table-container" style="max-height:300px;">
                    <table>
                        <thead>
                            <tr>
                                <th>#</th>
                                <th>{t('countries')}</th>
                            </tr>
                        </thead>
                        <tbody>
                            {''.join([
                                f'<tr><td>{i+1}</td><td>{", ".join([get_full_country_name(c) for c in countries]) if countries else "-"}</td></tr>'
                                for i, countries in enumerate(geo_countries_per_pub[:50])
                            ])}
                        </tbody>
                    </table>
                </div>
                
                <div class="sub-section-title" style="margin-top:20px;"><span class="sub-icon">👤</span> {t('authors_per_country')}</div>
                <div class="table-container" style="max-height:300px;">
                    <table>
                        <thead>
                            <tr>
                                <th>{t('countries')}</th>
                                <th>{t('authors')}</th>
                            </tr>
                        </thead>
                        <tbody>
                            {''.join([
                                f'<tr><td>{get_full_country_name(country)}</td><td>{count}</td></tr>'
                                for country, count in sorted(geo_authors_per_country.items(), key=lambda x: x[1], reverse=True)
                            ])}
                        </tbody>
                    </table>
                </div>
                
                <div class="sub-section-title" style="margin-top:20px;"><span class="sub-icon">🤝</span> {t('collaboration_patterns')}</div>
                <div class="collab-grid">
                    <div class="collab-box">
                        <h4>{t('single_country')}</h4>
                        <p><strong>{geo_collab_patterns.get('single_country', 0)}</strong> publications</p>
                        <p style="font-size:13px;color:#666;">{geo_collab_patterns.get('single_country_pct', 0):.1f}% of total</p>
                    </div>
                    <div class="collab-box">
                        <h4>{t('international_collaboration')}</h4>
                        <p><strong>{geo_collab_patterns.get('multi_country', 0)}</strong> publications</p>
                        <p style="font-size:13px;color:#666;">{geo_collab_patterns.get('multi_country_pct', 0):.1f}% of total</p>
                    </div>
                </div>
                
                <div class="sub-section-title" style="margin-top:20px;"><span class="sub-icon">🔗</span> {t('collaboration_couples')}</div>
                <div class="table-container" style="max-height:300px;">
                    <table>
                        <thead>
                            <tr>
                                <th>{t('country_pair')}</th>
                                <th>{t('frequency')}</th>
                            </tr>
                        </thead>
                        <tbody>
                            {''.join([
                                f'<tr><td>{get_full_country_name(pair[0])} ↔ {get_full_country_name(pair[1])}</td><td>{count}</td></tr>'
                                for pair, count in list(geo_collab_couples.items())[:20]
                            ])}
                        </tbody>
                    </table>
                </div>
            </div>
            
            <!-- ==================== CITING WORKS SUMMARY ==================== -->
            <div id="citing_summary" class="section">
                <div class="section-title"><span class="icon">📚</span> {t('citing_works_analysis')}</div>
                <div class="metrics-grid">
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
            </div>
            
            <!-- ==================== TOP CITING AUTHORS ==================== -->
            <div id="top_citing_authors" class="section">
                <div class="section-title"><span class="icon">👥</span> {t('top_citing_authors')}</div>
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
                                f'<tr><td>{i+1}</td><td>{html.escape(name)}</td><td>{count}</td></tr>'
                                for i, (name, count) in enumerate(list(citing_analysis.get('authors', {}).items())[:30])
                            ])}
                        </tbody>
                    </table>
                </div>
            </div>
            
            <!-- ==================== TOP CITING AFFILIATIONS ==================== -->
            <div id="top_citing_affiliations" class="section">
                <div class="section-title"><span class="icon">🏛️</span> {t('top_citing_affiliations')}</div>
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
                                f'<tr><td>{i+1}</td><td class="word-wrap">{html.escape(name)}</td><td>{count}</td></tr>'
                                for i, (name, count) in enumerate(list(citing_analysis.get('affiliations', {}).items())[:30])
                            ])}
                        </tbody>
                    </table>
                </div>
            </div>
            
            <!-- ==================== TOP CITING COUNTRIES ==================== -->
            <div id="top_citing_countries" class="section">
                <div class="section-title"><span class="icon">🌍</span> {t('top_citing_countries')}</div>
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
                                f'<tr><td>{i+1}</td><td>{get_full_country_name(name)}</td><td>{count}</td></tr>'
                                for i, (name, count) in enumerate(list(citing_analysis.get('countries', {}).items())[:30])
                            ])}
                        </tbody>
                    </table>
                </div>
            </div>
            
            <!-- ==================== TOP CITING JOURNALS ==================== -->
            <div id="top_citing_journals" class="section">
                <div class="section-title"><span class="icon">📰</span> {t('top_citing_journals')}</div>
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>{t('rank')}</th>
                                <th>{t('journal')}</th>
                                <th>{t('citations_count')}</th>
                            </tr>
                        </thead>
                        <tbody>
                            {''.join([
                                f'<tr><td>{i+1}</td><td class="word-wrap">{html.escape(name)}</td><td>{count}</td></tr>'
                                for i, (name, count) in enumerate(list(citing_analysis.get('journals', {}).items())[:30])
                            ])}
                        </tbody>
                    </table>
                </div>
            </div>
            
            <!-- ==================== TOP CITING PUBLISHERS ==================== -->
            <div id="top_citing_publishers" class="section">
                <div class="section-title"><span class="icon">🏢</span> {t('top_citing_publishers')}</div>
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>{t('rank')}</th>
                                <th>{t('publishers')}</th>
                                <th>{t('citations_count')}</th>
                            </tr>
                        </thead>
                        <tbody>
                            {''.join([
                                f'<tr><td>{i+1}</td><td class="word-wrap">{html.escape(name)}</td><td>{count}</td></tr>'
                                for i, (name, count) in enumerate(list(citing_analysis.get('publishers', {}).items())[:30])
                            ])}
                        </tbody>
                    </table>
                </div>
            </div>
            
            <!-- ==================== TOPICS OVERVIEW ==================== -->
            <div id="topics_overview" class="section">
                <div class="section-title"><span class="icon">🏷️</span> {t('topic_overview')}</div>
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
                            {''.join([
                                f'<tr>'
                                f'<td class="word-wrap">{html.escape(row["name"])}</td>'
                                f'<td>{row["analyzed_count"]}</td>'
                                f'<td>{row["citing_count"]}</td>'
                                f'<td>{row["analyzed_norm"]:.3f}</td>'
                                f'<td>{row["citing_norm"]:.3f}</td>'
                                f'<td>{row["total_norm"]:.3f}</td>'
                                f'<td>{row["first_year"]}</td>'
                                f'<td>{row["peak_year"]}</td>'
                                f'</tr>'
                                for row in topic_rows
                            ])}
                        </tbody>
                    </table>
                </div>
            </div>
            
            <!-- ==================== TOP CITED TOPICS ==================== -->
            <div id="top_cited_topics" class="section">
                <div class="section-title"><span class="icon">📈</span> {t('top_10_topics')}</div>
                {''.join([
                    f'<div class="topic-card">'
                    f'<span class="topic-name">{html.escape(name)}</span>'
                    f'<div class="topic-stats">'
                    f'<span>📄 {count} {t("citations")}</span>'
                    f'</div>'
                    f'</div>'
                    for name, count in list(top_cited_topics.items())[:10]
                ])}
            </div>
            
            <!-- ==================== TOP CITED SUBTOPICS ==================== -->
            <div id="top_cited_subtopics" class="section">
                <div class="section-title"><span class="icon">📈</span> {t('top_10_subtopics')}</div>
                {''.join([
                    f'<div class="topic-card">'
                    f'<span class="topic-name">{html.escape(name)}</span>'
                    f'<div class="topic-stats">'
                    f'<span>📄 {count} {t("citations")}</span>'
                    f'</div>'
                    f'</div>'
                    for name, count in list(top_cited_subtopics.items())[:10]
                ])}
            </div>
            
            <!-- ==================== TOP CITED FIELDS ==================== -->
            <div id="top_cited_fields" class="section">
                <div class="section-title"><span class="icon">📈</span> {t('top_10_fields')}</div>
                {''.join([
                    f'<div class="topic-card">'
                    f'<span class="topic-name">{html.escape(name)}</span>'
                    f'<div class="topic-stats">'
                    f'<span>📄 {count} {t("citations")}</span>'
                    f'</div>'
                    f'</div>'
                    for name, count in list(top_cited_fields.items())[:10]
                ])}
            </div>
            
            <!-- ==================== TOP CITED DOMAINS ==================== -->
            <div id="top_cited_domains" class="section">
                <div class="section-title"><span class="icon">📈</span> {t('top_10_domains')}</div>
                {''.join([
                    f'<div class="topic-card">'
                    f'<span class="topic-name">{html.escape(name)}</span>'
                    f'<div class="topic-stats">'
                    f'<span>📄 {count} {t("citations")}</span>'
                    f'</div>'
                    f'</div>'
                    for name, count in list(top_cited_domains.items())[:10]
                ])}
            </div>
            
            <!-- ==================== TOP CITED CONCEPTS ==================== -->
            <div id="top_cited_concepts" class="section">
                <div class="section-title"><span class="icon">📈</span> {t('top_10_concepts')}</div>
                {''.join([
                    f'<div class="topic-card">'
                    f'<span class="topic-name">{html.escape(name)}</span>'
                    f'<div class="topic-stats">'
                    f'<span>📄 {count} {t("citations")}</span>'
                    f'</div>'
                    f'</div>'
                    for name, count in list(top_cited_concepts.items())[:10]
                ])}
            </div>
            
            <!-- ==================== DETAILED CITATIONS ==================== -->
            <div id="detailed_citations" class="section">
                <div class="section-title"><span class="icon">📋</span> {t('detailed_citations')}</div>
                
                <script>
                    function toggleCitations(id) {{
                        var element = document.getElementById('citations_' + id);
                        if (element.style.display === 'none' || element.style.display === '') {{
                            element.style.display = 'block';
                        }} else {{
                            element.style.display = 'none';
                        }}
                    }}
                </script>

                {''.join([
                    f'''
                    <div class="collapser" onclick="toggleCitations('{doi.replace('/', '_')}')">
                        <strong>{html.escape(data["title"][:80])}{"..." if len(data["title"])>80 else ""}</strong>
                        <span class="badge badge-info">{data["year"]}</span>
                        <span class="citation-count">{data["total_citations"]} citations</span>
                        <span style="font-size:11px;color:#999;margin-left:10px;">DOI: {data["doi"][:25]}{"..." if len(data["doi"])>25 else ""}</span>
                        <span class="toggle-hint">Click to toggle citations</span>
                    </div>
                    <div id="citations_{doi.replace('/', '_')}" style="display: none; margin-bottom: 10px;">
                        {''.join([
                            f'''
                            <div class="citation-detail">
                                <div><strong>{html.escape(cite["citing_title"][:100])}{"..." if len(cite["citing_title"])>100 else ""}</strong></div>
                                <div class="cite-meta">
                                    <strong>{t("citing_journal")}:</strong> {html.escape(cite["citing_journal"])} | 
                                    <strong>{t("citing_year")}:</strong> {cite["citing_year"]} | 
                                    <strong>{t("citing_date")}:</strong> {cite["citing_date"][:10] if cite["citing_date"] else "N/A"} |
                                    <strong>{t("citation_lag")}:</strong> {cite["citation_lag"]:.2f} years
                                </div>
                                <div class="cite-meta">
                                    <strong>{t("authors")}:</strong> {', '.join([html.escape(a) for a in cite["citing_authors"][:5]])}{"..." if len(cite["citing_authors"])>5 else ""} |
                                    <strong>{t("countries")}:</strong> {', '.join([get_full_country_name(c) for c in cite["citing_countries"][:3]])}{"..." if len(cite["citing_countries"])>3 else ""} |
                                    <strong>{t("topics")}:</strong> {', '.join([html.escape(t) for t in cite["citing_topics"][:3]])}{"..." if len(cite["citing_topics"])>3 else ""}
                                </div>
                                <div class="cite-meta">
                                    <a href="https://doi.org/{cite["citing_doi"]}" target="_blank" class="doi-link">DOI: {cite["citing_doi"][:40]}{"..." if len(cite["citing_doi"])>40 else ""}</a>
                                </div>
                            </div>
                            ''' for cite in data["citations"]
                        ])}
                    </div>
                    ''' for doi, data in list(detailed_citations.items())[:50]
                ]}
                
                {f'<p style="font-size:13px;color:#666;margin-top:10px;">Showing {min(50, len(detailed_citations))} of {len(detailed_citations)} publications with citations</p>' if len(detailed_citations) > 50 else ''}
            </div>
            
            <!-- ==================== ALL PUBLICATIONS ==================== -->
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
                                    for year in sorted(set(a["Year"] for a in articles if a["Year"]), reverse=True)
                                ])}
                            </select>
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
                            <label for="titleFilter">{t('filter_by_title')}:</label>
                            <input type="text" id="titleFilter" placeholder="Title words..." onkeyup="filterPublications()">
                        </div>
                        <div>
                            <span id="visibleCount" style="font-weight:500;font-size:13px;">{t('showing_all_publications', count=total_pubs)}</span>
                        </div>
                    </div>
                </div>
                
                <script>
                    function filterPublications() {{
                        var yearFilter = document.getElementById('yearFilter').value;
                        var authorFilter = document.getElementById('authorFilter').value.toLowerCase();
                        var affilFilter = document.getElementById('affilFilter').value.toLowerCase();
                        var citationFilter = parseInt(document.getElementById('citationFilter').value) || 0;
                        var titleFilter = document.getElementById('titleFilter').value.toLowerCase();
                        var rows = document.querySelectorAll('#publicationsTable tbody tr');
                        var visible = 0;
                        
                        rows.forEach(function(row) {{
                            var year = row.getAttribute('data-year');
                            var authors = row.getAttribute('data-authors').toLowerCase();
                            var affiliations = row.getAttribute('data-affiliations').toLowerCase();
                            var citations = parseInt(row.getAttribute('data-citations')) || 0;
                            var title = row.getAttribute('data-title').toLowerCase();
                            
                            var show = true;
                            if (yearFilter && year !== yearFilter) show = false;
                            if (authorFilter && !authors.includes(authorFilter)) show = false;
                            if (affilFilter && !affiliations.includes(affilFilter)) show = false;
                            if (citationFilter > 0 && citations < citationFilter) show = false;
                            if (titleFilter && !title.includes(titleFilter)) show = false;
                            
                            if (show) {{
                                row.style.display = '';
                                visible++;
                            }} else {{
                                row.style.display = 'none';
                            }}
                        }});
                        
                        document.getElementById('visibleCount').textContent = 'Showing ' + visible + ' of ' + {total_pubs} + ' publications';
                    }}
                </script>
                
                <div class="table-container" style="max-height:600px;">
                    <table id="publicationsTable">
                        <thead>
                            <tr>
                                <th onclick="sortTable(0)" style="cursor:pointer;">#</th>
                                <th onclick="sortTable(1)" style="cursor:pointer;">{t('title')}</th>
                                <th onclick="sortTable(2)" style="cursor:pointer;">{t('year')}</th>
                                <th onclick="sortTable(3)" style="cursor:pointer;">{t('authors')}</th>
                                <th onclick="sortTable(4)" style="cursor:pointer;">{t('affiliations')}</th>
                                <th onclick="sortTable(5)" style="cursor:pointer;">{t('citations')}</th>
                                <th onclick="sortTable(6)" style="cursor:pointer;">{t('citations_per_year_col')}</th>
                                <th>{t('doi')}</th>
                            </tr>
                        </thead>
                        <tbody>
                            {''.join([
                                f'''
                                <tr data-year="{article.get('Year', '')}" 
                                    data-authors="{','.join(articles_metadata.get(article['DOI'], {}).get('authors', []))}" 
                                    data-affiliations="{','.join(articles_metadata.get(article['DOI'], {}).get('affiliations', []))}" 
                                    data-citations="{article.get('Cited_by_count', 0)}" 
                                    data-title="{articles_metadata.get(article['DOI'], {}).get('title', 'No title').lower()}">
                                    <td>{i+1}</td>
                                    <td class="word-wrap">{html.escape(articles_metadata.get(article['DOI'], {}).get('title', 'No title')[:80])}{"..." if len(articles_metadata.get(article['DOI'], {}).get('title', 'No title'))>80 else ""}</td>
                                    <td>{article.get('Year', 'N/A')}</td>
                                    <td>{', '.join([html.escape(a) for a in articles_metadata.get(article['DOI'], {}).get('authors', [])[:3]])}{"..." if len(articles_metadata.get(article['DOI'], {}).get('authors', []))>3 else ""}</td>
                                    <td>{', '.join([html.escape(a) for a in articles_metadata.get(article['DOI'], {}).get('affiliations', [])[:2]])}{"..." if len(articles_metadata.get(article['DOI'], {}).get('affiliations', []))>2 else ""}</td>
                                    <td>{article.get('Cited_by_count', 0)}</td>
                                    <td>{(article.get('Cited_by_count', 0) / max(1, 2026 - article.get('Year', 2026))):.1f}</td>
                                    <td><a href="https://doi.org/{article['DOI']}" target="_blank" class="doi-link">{article['DOI'][:25]}{"..." if len(article['DOI'])>25 else ""}</a></td>
                                </tr>
                                ''' for i, article in enumerate(articles)
                            ])}
                        </tbody>
                    </table>
                </div>
                
                <script>
                    function sortTable(n) {{
                        var table = document.getElementById('publicationsTable');
                        var rows = table.getElementsByTagName('tbody')[0].getElementsByTagName('tr');
                        var switching = true;
                        var dir = 'asc';
                        
                        while (switching) {{
                            switching = false;
                            var shouldSwitch = false;
                            
                            for (var i = 0; i < rows.length - 1; i++) {{
                                var x = rows[i].getElementsByTagName('td')[n];
                                var y = rows[i+1].getElementsByTagName('td')[n];
                                
                                if (dir === 'asc') {{
                                    if (x.innerHTML.toLowerCase() > y.innerHTML.toLowerCase()) {{
                                        shouldSwitch = true;
                                        break;
                                    }}
                                }} else if (dir === 'desc') {{
                                    if (x.innerHTML.toLowerCase() < y.innerHTML.toLowerCase()) {{
                                        shouldSwitch = true;
                                        break;
                                    }}
                                }}
                            }}
                            
                            if (shouldSwitch) {{
                                rows[i].parentNode.insertBefore(rows[i+1], rows[i]);
                                switching = true;
                            }} else {{
                                if (dir === 'asc') {{
                                    dir = 'desc';
                                    switching = true;
                                }}
                            }}
                        }}
                    }}
                </script>
            </div>
            
            <!-- ==================== FOOTER ==================== -->
            <div class="footer">
                <p>{t('footer')}</p>
                <p><a href="{t('journal_url')}" target="_blank">{t('journal_url')}</a></p>
                <p style="font-size:11px;margin-top:5px;">Data source: OpenAlex | Generated: {datetime.now().strftime('%d.%m.%Y %H:%M')}</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html_content

# ============================================
# ОСНОВНАЯ ФУНКЦИЯ ЗАПУСКА ДЛЯ STREAMLIT
# ============================================

def run_journal_analysis(issn: str, period, max_workers: int = 8, journal_logo: Optional[Dict] = None):
    """Запускает полный анализ журнала"""
    
    current_lang = st.session_state.get('language', 'en')
    def t(key: str, **kwargs) -> str:
        return translate(key, current_lang, **kwargs)
    
    if not issn or not period:
        st.error(t('no_issn') if not issn else t('no_period'))
        return
    
    # Проверка формата ISSN
    issn_clean = normalize_issn(issn)
    if len(issn_clean) != 9 or issn_clean[4] != '-':
        st.error(t('invalid_issn'))
        return
    
    # Парсинг периода
    period_str = str(period).strip()
    if ',' in period_str:
        years = [int(y.strip()) for y in period_str.split(',') if y.strip().isdigit()]
        if not years:
            st.error(t('invalid_period'))
            return
        period_parsed = years
    elif '-' in period_str:
        parts = period_str.split('-')
        if len(parts) != 2 or not parts[0].strip().isdigit() or not parts[1].strip().isdigit():
            st.error(t('invalid_period'))
            return
        period_parsed = (int(parts[0].strip()), int(parts[1].strip()))
    else:
        if period_str.isdigit():
            period_parsed = int(period_str)
        else:
            st.error(t('invalid_period'))
            return
    
    # Кэширование в сессии
    cache_key = f"{issn_clean}_{period_str}_{max_workers}"
    if cache_key in st.session_state.get('journal_analysis_cache', {}):
        st.info("✅ Using cached results from this session")
        results = st.session_state.journal_analysis_cache[cache_key]
        st.session_state.journal_analysis_results = results
        st.session_state.analysis_complete = True
        return
    
    st.info(f"🔍 {t('analyzing_authors', count=1)} (ISSN: {issn_clean}, Period: {period_str})")
    
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
                    st.success(f"✅ {t('logo_help')}: {filename}")
                    break
            except Exception as e:
                st.warning(f"⚠️ {t('error_occurred')}: {e}")
        
        # Функция обратного вызова для прогресса
        stage_names = {
            'stage_1': t('stage_1'),
            'stage_2': t('stage_2'),
            'stage_3': t('stage_3'),
            'stage_4': t('stage_4'),
            'stage_5': t('stage_5')
        }
        
        stage_descs = {
            'stage_1': t('stage_1_desc'),
            'stage_2': t('stage_2_desc'),
            'stage_3': t('stage_3_desc'),
            'stage_4': t('stage_4_desc'),
            'stage_5': t('stage_5_desc')
        }
        
        stage_weights = {'stage_1': 0.15, 'stage_2': 0.25, 'stage_3': 0.20, 'stage_4': 0.25, 'stage_5': 0.15}
        stage_progress = {'stage_1': 0, 'stage_2': 0, 'stage_3': 0, 'stage_4': 0, 'stage_5': 0}
        
        def progress_callback(processed, total, stage, sub_processed=0, sub_total=0, sub_item=""):
            if stage in stage_weights:
                if total and total > 0:
                    stage_progress[stage] = processed / total
                else:
                    stage_progress[stage] = 0.5
                
                total_progress = sum(stage_progress[s] * stage_weights[s] for s in stage_weights)
                total_percent = total_progress * 100
                
                stage_name = stage_names.get(stage, stage)
                if sub_total and sub_total > 0:
                    sub_text = f" ({sub_processed}/{sub_total})"
                else:
                    sub_text = ""
                
                if sub_item:
                    item_text = f" - {sub_item[:40]}"
                else:
                    item_text = ""
                
                status_text = f"{stage_name}{sub_text}{item_text}"
                analysis_progress.progress(min(total_progress, 0.99), text=status_text)
                status_container.info(f"📊 {stage_name} - {stage_descs.get(stage, '')}{sub_text}")
        
        start_time = time.time()
        
        # Создаем и запускаем анализатор
        analyzer = JournalAnalyzer(issn_clean, period_parsed, max_workers)
        stats = analyzer.run_analysis(progress_callback)
        results = analyzer.get_results()
        results['issn'] = issn_clean
        results['period'] = period_str
        
        elapsed = time.time() - start_time
        
        # Сохраняем в сессию
        if 'journal_analysis_cache' not in st.session_state:
            st.session_state.journal_analysis_cache = {}
        st.session_state.journal_analysis_cache[cache_key] = results
        st.session_state.journal_analysis_results = results
        st.session_state.analysis_complete = True
        st.session_state.journal_logo_base64 = journal_logo_base64
        st.session_state.app_logo_base64 = app_logo_base64
        st.session_state.current_issn = issn_clean
        st.session_state.current_period = period_str
        
        analysis_progress.progress(1.0, text=f"✅ {t('analysis_complete_text')}!")
        
        st.success(t('analysis_complete', count=stats.get('total_publications', 0), time=elapsed))
        st.balloons()
        
    except Exception as e:
        st.error(f"❌ {t('error_occurred')}: {str(e)}")
        import traceback
        st.code(traceback.format_exc())
    finally:
        analysis_progress.empty()
        status_container.empty()

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
        st.session_state.analysis_mode = 'journal_analysis'
    if 'filter_params' not in st.session_state:
        st.session_state.filter_params = {}
    if 'journal_analysis_cache' not in st.session_state:
        st.session_state.journal_analysis_cache = {}
    if 'journal_analysis_results' not in st.session_state:
        st.session_state.journal_analysis_results = None
    if 'current_issn' not in st.session_state:
        st.session_state.current_issn = ''
    if 'current_period' not in st.session_state:
        st.session_state.current_period = ''
    
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
    tab1, tab2 = st.tabs([
        t('load_data'),
        t('analysis_results')
    ])
    
    with tab1:
        st.markdown('<div class="custom-tab fade-in">', unsafe_allow_html=True)
        st.header(t('load_data'))
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
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
                t('max_workers'),
                min_value=4,
                max_value=12,
                value=8,
                step=1,
                help=t('max_workers_help')
            )
        
        with col2:
            journal_logo_upload = st.file_uploader(
                t('upload_logo'),
                type=['png', 'jpg', 'jpeg', 'svg'],
                help=t('logo_help')
            )
        
        if st.button(t('analyze_button'), type="primary", width='stretch'):
            if not issn_input.strip():
                st.error(t('no_issn'))
            elif not period_input.strip():
                st.error(t('no_period'))
            else:
                journal_logo_data = None
                if journal_logo_upload:
                    journal_logo_data = {
                        journal_logo_upload.name: {
                            'content': journal_logo_upload.read()
                        }
                    }
                
                run_journal_analysis(
                    issn_input.strip(),
                    period_input.strip(),
                    max_workers,
                    journal_logo_data
                )
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        if st.session_state.analysis_complete and st.session_state.journal_analysis_results:
            results = st.session_state.journal_analysis_results
            journal_logo_base64 = st.session_state.journal_logo_base64
            app_logo_base64 = st.session_state.app_logo_base64
            
            st.markdown(f"## {t('html_report')}")
            
            stats = results.get('stats', {})
            total_pubs = stats.get('total_publications', 0)
            
            st.info(f"📊 {t('total_publications')}: {total_pubs} | {t('total_citations')}: {stats.get('total_citations', 0):,} | {t('h_index')}: {stats.get('h_index', 0)}")
            
            theme_colors = {
                'primary': st.session_state.primary_color,
                'secondary': st.session_state.secondary_color
            }
            
            if st.button(t('download_report'), type="primary", width='stretch'):
                with st.spinner(t('generating_report')):
                    html_report = generate_html_report_journal(
                        results,
                        {},
                        journal_logo_base64,
                        app_logo_base64,
                        theme_colors,
                        current_lang
                    )
                    
                    filename = f"journal_analysis_{st.session_state.current_issn}_{st.session_state.current_period}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
                    
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
            
            # Предпросмотр отчета
            with st.spinner(t('generating_report')):
                html_preview = generate_html_report_journal(
                    results,
                    {},
                    journal_logo_base64,
                    app_logo_base64,
                    theme_colors,
                    current_lang
                )
                st.components.v1.html(html_preview, height=800, scrolling=True)
                
        else:
            st.info(t('no_data'))
    
    if st.session_state.analysis_complete and st.session_state.journal_analysis_results:
        pass

if __name__ == "__main__":
    main()
