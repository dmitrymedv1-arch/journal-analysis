# -*- coding: utf-8 -*-
"""
Advanced Journal Analysis Tool
Единое приложение Streamlit для анализа журналов через OpenAlex API
"""

import streamlit as st
import pandas as pd
import requests
import re
import time
import random
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from tqdm import tqdm
import html
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass, field
from collections import defaultdict, Counter
import json

# ==================== НАСТРОЙКИ ====================
MAX_WORKERS = 8
BASE_DELAY = 0.35
MAX_RETRIES = 4
MAX_CITING_PER_PAPER = 300
CACHE_DURATION = 3600  # 1 час

lock = Lock()

# ==================== МУЛЬТИЯЗЫЧНАЯ ПОДДЕРЖКА ====================
LANGUAGES = {
    'ru': {
        'app_title': 'Advanced Journal Analysis Tool',
        'app_subtitle': 'Анализ журналов через OpenAlex API',
        'issn_label': 'ISSN журнала',
        'issn_placeholder': '0028-0836',
        'period_label': 'Период анализа',
        'period_placeholder': '2020-2023 или 2020,2021,2022 или 2020',
        'workers_label': 'Количество потоков',
        'analyze_button': '🚀 Запустить анализ',
        'language_label': 'Язык',
        'analyzing': 'Анализ...',
        'loading_articles': 'Загрузка статей журнала',
        'loading_citations': 'Сбор цитирований',
        'processing_data': 'Обработка данных',
        'generating_report': 'Генерация отчета',
        'complete': '✅ Анализ завершен!',
        'error': '❌ Ошибка',
        'fill_fields': 'Заполните все поля!',
        'invalid_issn': 'Неверный формат ISSN',
        'total_publications': 'Всего публикаций',
        'total_citations': 'Всего цитирований',
        'h_index': 'h-индекс',
        'g_index': 'g-индекс',
        'i10_index': 'i10-индекс',
        'i100_index': 'i100-индекс',
        'avg_citations': 'Среднее цитирование',
        'open_access': 'Открытый доступ',
        'active_years': 'Активные годы',
        'unique_authors': 'Уникальные авторы',
        'unique_affiliations': 'Уникальные аффилиации',
        'unique_countries': 'Уникальные страны',
        'avg_authors_per_paper': 'Авторов/статья',
        'avg_affiliations_per_paper': 'Аффилиаций/статья',
        'avg_countries_per_paper': 'Стран/статья',
        'international_collaboration_rate': 'Коэффициент международного сотрудничества',
        'unique_citing_authors': 'Уникальные цитирующие авторы',
        'unique_citing_affiliations': 'Уникальные цитирующие аффилиации',
        'unique_citing_countries': 'Уникальные цитирующие страны',
        'unique_citing_journals': 'Уникальные цитирующие журналы',
        'unique_citing_publishers': 'Уникальные цитирующие издатели',
        'gold': 'Gold',
        'hybrid': 'Hybrid',
        'green': 'Green',
        'bronze': 'Bronze',
        'closed': 'Closed',
        'unknown': 'Unknown',
        'overview': 'Обзор',
        'analyzed_articles': 'Анализируемые статьи',
        'author_analysis': 'Анализ авторов',
        'top_affiliations': 'Топ аффилиации',
        'geographic_analysis': 'Географический анализ',
        'unique_countries_per_publication': 'Уникальные страны на публикацию',
        'authors_per_country': 'Авторы по странам',
        'collaboration_patterns': 'Шаблоны сотрудничества',
        'collaboration_couples': 'Пары сотрудничества',
        'citation_analysis': 'Цитатный анализ',
        'citation_dynamics': 'Динамика цитирований по годам',
        'cumulative_citations': 'Накопленные цитирования',
        'citation_network_heatmap': 'Тепловая карта цитирований',
        'most_cited_publications': 'Наиболее цитируемые публикации',
        'citing_works_analysis': 'Анализ цитирующих работ',
        'total_citing_works': 'Всего цитирующих работ',
        'top_citing_authors': 'Топ цитирующих авторов',
        'top_citing_affiliations': 'Топ цитирующих аффилиаций',
        'top_citing_countries': 'Топ цитирующих стран',
        'top_citing_journals': 'Топ цитирующих журналов',
        'top_citing_publishers': 'Топ цитирующих издателей',
        'topics_analysis': 'Тематический анализ',
        'topics': 'Темы',
        'analyzed_count': 'Количество в анализируемых',
        'citing_count': 'Количество в цитирующих',
        'analyzed_norm_count': 'Норм. кол-во в анализируемых',
        'citing_norm_count': 'Норм. кол-во в цитирующих',
        'total_norm_count': 'Общее норм. кол-во',
        'first_year': 'Первый год',
        'peak_year': 'Пиковый год',
        'top_topics': 'Топ-10 тем',
        'top_subtopics': 'Топ-10 подтем',
        'top_fields': 'Топ-10 областей',
        'top_domains': 'Топ-10 доменов',
        'top_concepts': 'Топ-10 концепций',
        'detailed_citations': 'Детальные цитирования',
        'all_publications': 'Все публикации',
        'filter_by_year': 'Фильтр по году',
        'filter_by_title': 'Фильтр по названию',
        'filter_by_author': 'Фильтр по автору',
        'filter_by_affiliation': 'Фильтр по аффилиации',
        'filter_by_citations': 'Фильтр по цитированиям (мин)',
        'show_citations': 'Показать цитирования',
        'citing_journal': 'Цитирующий журнал',
        'citing_year': 'Год цитирования',
        'citing_date': 'Дата цитирования',
        'citation_lag': 'Лаг цитирования',
        'authors': 'Авторы',
        'countries': 'Страны',
        'rank': 'Ранг',
        'title': 'Название',
        'year': 'Год',
        'citations': 'Цитирования',
        'citations_per_year': 'Цитирований/год',
        'affiliations': 'Аффилиации',
        'journal': 'Журнал',
        'publisher': 'Издатель',
        'doi': 'DOI',
        'orcid': 'ORCID',
        'publications': 'Публикации',
        'collaboration_type': 'Тип сотрудничества',
        'single_country': 'Однострановые',
        'international': 'Международные',
        'country_pair': 'Пара стран',
        'frequency': 'Частота',
        'publication_year': 'Год публикации',
        'citation_year': 'Год цитирования',
        'citations_count': 'Количество цитирований',
        'cumulative': 'Накопленные',
        'heatmap': 'Тепловая карта',
        'footer': 'Данные получены через OpenAlex API',
        'journal_url': 'URL журнала',
        'download_report': '📥 Скачать HTML отчет',
        'download_csv': '📥 Скачать CSV',
        'search_publications': 'Поиск публикаций',
        'all_years': 'Все годы',
        'view_details': 'Подробнее'
    },
    'en': {
        'app_title': 'Advanced Journal Analysis Tool',
        'app_subtitle': 'Journal Analysis through OpenAlex API',
        'issn_label': 'Journal ISSN',
        'issn_placeholder': '0028-0836',
        'period_label': 'Analysis Period',
        'period_placeholder': '2020-2023 or 2020,2021,2022 or 2020',
        'workers_label': 'Number of threads',
        'analyze_button': '🚀 Start Analysis',
        'language_label': 'Language',
        'analyzing': 'Analyzing...',
        'loading_articles': 'Loading journal articles',
        'loading_citations': 'Collecting citations',
        'processing_data': 'Processing data',
        'generating_report': 'Generating report',
        'complete': '✅ Analysis complete!',
        'error': '❌ Error',
        'fill_fields': 'Please fill all fields!',
        'invalid_issn': 'Invalid ISSN format',
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
        'gold': 'Gold',
        'hybrid': 'Hybrid',
        'green': 'Green',
        'bronze': 'Bronze',
        'closed': 'Closed',
        'unknown': 'Unknown',
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
        'citation_dynamics': 'Citation Dynamics by Year',
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
        'topics': 'Topics',
        'analyzed_count': 'Analyzed Count',
        'citing_count': 'Citing Count',
        'analyzed_norm_count': 'Analyzed Norm Count',
        'citing_norm_count': 'Citing Norm Count',
        'total_norm_count': 'Total Norm Count',
        'first_year': 'First Year',
        'peak_year': 'Peak Year',
        'top_topics': 'Top-10 Topics',
        'top_subtopics': 'Top-10 Subtopics',
        'top_fields': 'Top-10 Fields',
        'top_domains': 'Top-10 Domains',
        'top_concepts': 'Top-10 Concepts',
        'detailed_citations': 'Detailed Citations',
        'all_publications': 'All Publications',
        'filter_by_year': 'Filter by Year',
        'filter_by_title': 'Filter by Title',
        'filter_by_author': 'Filter by Author',
        'filter_by_affiliation': 'Filter by Affiliation',
        'filter_by_citations': 'Filter by Citations (min)',
        'show_citations': 'Show Citations',
        'citing_journal': 'Citing Journal',
        'citing_year': 'Citing Year',
        'citing_date': 'Citing Date',
        'citation_lag': 'Citation Lag',
        'authors': 'Authors',
        'countries': 'Countries',
        'rank': 'Rank',
        'title': 'Title',
        'year': 'Year',
        'citations': 'Citations',
        'citations_per_year': 'Citations/Year',
        'affiliations': 'Affiliations',
        'journal': 'Journal',
        'publisher': 'Publisher',
        'doi': 'DOI',
        'orcid': 'ORCID',
        'publications': 'Publications',
        'collaboration_type': 'Collaboration Type',
        'single_country': 'Single-country',
        'international': 'International',
        'country_pair': 'Country Pair',
        'frequency': 'Frequency',
        'publication_year': 'Publication Year',
        'citation_year': 'Citation Year',
        'citations_count': 'Citations Count',
        'cumulative': 'Cumulative',
        'heatmap': 'Heatmap',
        'footer': 'Data sourced from OpenAlex API',
        'journal_url': 'Journal URL',
        'download_report': '📥 Download HTML Report',
        'download_csv': '📥 Download CSV',
        'search_publications': 'Search Publications',
        'all_years': 'All Years',
        'view_details': 'View Details'
    }
}

def get_text(key: str) -> str:
    """Получение текста на текущем языке"""
    lang = st.session_state.get('language', 'ru')
    return LANGUAGES.get(lang, LANGUAGES['ru']).get(key, key)

# ==================== DATA CLASSES ====================
@dataclass
class Author:
    display_name: str
    orcid: Optional[str] = None
    affiliations: List[str] = field(default_factory=list)
    countries: List[str] = field(default_factory=list)
    
@dataclass
class Topic:
    id: str
    display_name: str
    subtopic: Optional[str] = None
    topic_field: Optional[str] = None  # переименовали поле
    domain: Optional[str] = None
    concepts: List[str] = field(default_factory=list)

@dataclass
class Publication:
    id: str
    doi: str
    title: str
    publication_year: int
    cited_by_count: int
    authors: List[Author]
    affiliations: List[str]
    countries: List[str]
    open_access_status: str
    topics: List[Topic]
    journal_name: str
    publisher: str
    publication_date: Optional[str] = None
    citations_per_year: float = 0.0

@dataclass
class Citation:
    citing_doi: str
    citing_title: str
    citing_year: int
    citing_date: str
    citing_journal: str
    citing_publisher: str
    citing_authors: List[Author]
    citing_countries: List[str]
    citing_topics: List[Topic]
    citation_lag: int

# ==================== API CLIENT ====================
def normalize_issn(issn_str: str) -> str:
    """Нормализация ISSN"""
    cleaned = re.sub(r'[^0-9Xx]', '', str(issn_str).strip())
    if len(cleaned) == 8:
        return f"{cleaned[:4]}-{cleaned[4:]}".upper()
    return cleaned.upper()

def smart_get(url: str, params: Dict, retries: int = MAX_RETRIES) -> Optional[Dict]:
    """Умные запросы с защитой от 429 ошибок"""
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
            
        except:
            time.sleep(1.5 * (2 ** attempt))
    return None

def get_work_details(work_id: str) -> Optional[Dict]:
    """Получение детальной информации о работе"""
    url = f"https://api.openalex.org/works/{work_id}"
    data = smart_get(url, {})
    return data

def parse_author(author_data: Dict) -> Author:
    """Парсинг автора из данных API"""
    display_name = author_data.get('display_name', 'Unknown')
    orcid = None
    if 'orcid' in author_data and author_data['orcid']:
        orcid = author_data['orcid'].replace('https://orcid.org/', '')
    
    affiliations = []
    countries = []
    
    for aff in author_data.get('affiliations', []):
        institution = aff.get('institution', {})
        if institution.get('display_name'):
            affiliations.append(institution['display_name'])
        country_code = aff.get('country_code', '').upper()
        if country_code:
            countries.append(country_code)
    
    return Author(
        display_name=display_name,
        orcid=orcid,
        affiliations=affiliations,
        countries=countries
    )

def parse_topic(topic_data: Dict) -> Topic:
    return Topic(
        id=topic_data.get('id', ''),
        display_name=topic_data.get('display_name', 'Unknown'),
        subtopic=topic_data.get('subtopic', {}).get('display_name'),
        topic_field=topic_data.get('field', {}).get('display_name'),  # изменили
        domain=topic_data.get('domain', {}).get('display_name'),
        concepts=[c.get('display_name', '') for c in topic_data.get('concepts', [])]
    )

def get_publication_details(doi: str) -> Optional[Publication]:
    """Получение детальной информации о публикации по DOI"""
    work_id = f"https://openalex.org/works/doi:{doi}"
    data = get_work_details(work_id)
    
    if not data:
        return None
    
    # Парсинг авторов
    authors = []
    for author_data in data.get('authorships', []):
        author = parse_author(author_data)
        authors.append(author)
    
    # Сбор уникальных аффилиаций и стран
    affiliations = set()
    countries = set()
    for author in authors:
        affiliations.update(author.affiliations)
        countries.update(author.countries)
    
    # Парсинг тем
    topics = []
    for topic_data in data.get('topics', []):
        topics.append(parse_topic(topic_data))
    
    # Open Access статус
    oa_data = data.get('open_access', {})
    oa_status = oa_data.get('oa_status', 'unknown')
    if not oa_status:
        oa_status = 'unknown'
    
    # Название журнала
    journal_name = 'Unknown'
    if data.get('primary_location'):
        journal_name = data['primary_location'].get('source', {}).get('display_name', 'Unknown')
    
    # Издатель
    publisher = 'Unknown'
    if data.get('primary_location'):
        publisher = data['primary_location'].get('source', {}).get('publisher', 'Unknown')
    
    return Publication(
        id=data.get('id', ''),
        doi=doi,
        title=data.get('title', 'No title'),
        publication_year=data.get('publication_year', 0),
        cited_by_count=data.get('cited_by_count', 0),
        authors=authors,
        affiliations=list(affiliations),
        countries=list(countries),
        open_access_status=oa_status,
        topics=topics,
        journal_name=journal_name,
        publisher=publisher,
        publication_date=data.get('publication_date'),
        citations_per_year=0
    )

def get_journal_articles(issn: str, years: Any, progress_bar=None) -> List[Dict]:
    """Получение списка статей журнала"""
    normalized = normalize_issn(issn)
    base_url = "https://api.openalex.org/works"
    
    # Формирование фильтра по годам
    if isinstance(years, list):
        year_filter = "|".join(f"publication_year:{y}" for y in years)
    elif isinstance(years, tuple):
        year_filter = f"publication_year:{years[0]}-{years[1]}"
    else:
        year_filter = f"publication_year:{years}"
    
    articles = []
    cursor = "*"
    total_articles = 0
    
    while True:
        data = smart_get(base_url, {
            "filter": f"primary_location.source.issn:{normalized},{year_filter}",
            "per_page": 200,
            "select": "id,doi,publication_year,cited_by_count,title,authorships,primary_location,open_access,publication_date,topics",
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
                "year": w.get("publication_year"),
                "cited_by_count": w.get("cited_by_count", 0),
                "data": w
            })
        
        total_articles += len(data["results"])
        if progress_bar:
            progress_bar.progress(min(1.0, len(articles) / 500))
        
        cursor = data.get("meta", {}).get("next_cursor")
        if not cursor:
            break
    
    return articles

def get_citing_dois(oa_id: str) -> List[str]:
    """Получение списка цитирующих DOI"""
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
    
    return citing[:MAX_CITING_PER_PAPER]

def get_citation_details(citing_doi: str, source_year: int) -> Optional[Citation]:
    """Получение детальной информации о цитирующей работе"""
    pub = get_publication_details(citing_doi)
    if not pub:
        return None
    
    # Расчет лага цитирования
    citation_lag = pub.publication_year - source_year
    
    return Citation(
        citing_doi=pub.doi,
        citing_title=pub.title,
        citing_year=pub.publication_year,
        citing_date=pub.publication_date or '',
        citing_journal=pub.journal_name,
        citing_publisher=pub.publisher,
        citing_authors=pub.authors,
        citing_countries=pub.countries,
        citing_topics=pub.topics,
        citation_lag=citation_lag
    )

# ==================== DATA PROCESSING ====================
class JournalAnalyzer:
    """Класс для анализа журнала"""
    
    def __init__(self, issn: str, years: Any, max_workers: int = MAX_WORKERS):
        self.issn = issn
        self.years = years
        self.max_workers = max_workers
        self.publications: List[Publication] = []
        self.citations: Dict[str, List[Citation]] = {}
        self.article_data: List[Dict] = []
        self.citing_map: Dict[str, List[str]] = {}
        
    def run_analysis(self, progress_placeholder=None) -> bool:
        """Запуск полного анализа"""
        try:
            # 1. Загрузка статей журнала
            if progress_placeholder:
                progress_placeholder.progress(0, text=get_text('loading_articles'))
            
            articles = get_journal_articles(self.issn, self.years)
            self.article_data = articles
            
            if not articles:
                st.error("Не найдено статей для указанного ISSN и периода")
                return False
            
            # 2. Получение детальной информации о статьях
            if progress_placeholder:
                progress_placeholder.progress(10, text=get_text('processing_data'))
            
            for i, article in enumerate(articles):
                if article['doi'] != "N/A":
                    pub = get_publication_details(article['doi'])
                    if pub:
                        # Расчет цитирований в год
                        years_active = max(1, 2026 - pub.publication_year)
                        pub.citations_per_year = pub.cited_by_count / years_active
                        self.publications.append(pub)
                
                if progress_placeholder and i % 5 == 0:
                    progress = 10 + (i / len(articles)) * 30
                    progress_placeholder.progress(progress / 100, text=f"{get_text('processing_data')} ({i+1}/{len(articles)})")
            
            # 3. Параллельный сбор цитирующих работ
            if progress_placeholder:
                progress_placeholder.progress(40, text=get_text('loading_citations'))
            
            self.citing_map = {}
            futures = {}
            
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                for pub in self.publications:
                    if pub.cited_by_count > 0 and pub.doi != "N/A":
                        oa_id = pub.id.replace("https://openalex.org/", "")
                        future = executor.submit(get_citing_dois, oa_id)
                        futures[future] = pub.doi
                
                completed = 0
                for future in as_completed(futures):
                    doi = futures[future]
                    try:
                        self.citing_map[doi] = future.result()
                    except:
                        self.citing_map[doi] = []
                    
                    completed += 1
                    if progress_placeholder and completed % 5 == 0:
                        progress = 40 + (completed / len(futures)) * 40
                        progress_placeholder.progress(progress / 100, text=f"{get_text('loading_citations')} ({completed}/{len(futures)})")
            
            # 4. Получение детальной информации о цитирующих работах
            if progress_placeholder:
                progress_placeholder.progress(80, text=get_text('processing_data'))
            
            for pub in self.publications:
                if pub.doi in self.citing_map and self.citing_map[pub.doi]:
                    citations_list = []
                    citing_dois = self.citing_map[pub.doi]
                    
                    for i, citing_doi in enumerate(citing_dois[:100]):  # Ограничиваем для скорости
                        citation = get_citation_details(citing_doi, pub.publication_year)
                        if citation:
                            citations_list.append(citation)
                        
                        if progress_placeholder and i % 10 == 0:
                            progress = 80 + (i / len(citing_dois)) * 15
                            progress_placeholder.progress(progress / 100, text=f"{get_text('processing_data')}")
                    
                    self.citations[pub.id] = citations_list
            
            if progress_placeholder:
                progress_placeholder.progress(95, text=get_text('generating_report'))
            
            return True
            
        except Exception as e:
            st.error(f"{get_text('error')}: {str(e)}")
            return False
    
    # ============= МЕТРИКИ =============
    def calculate_metrics(self) -> Dict:
        """Расчет всех метрик"""
        metrics = {}
        
        # Основные метрики
        metrics['total_publications'] = len(self.publications)
        total_citations = sum(p.cited_by_count for p in self.publications)
        metrics['total_citations'] = total_citations
        metrics['avg_citations'] = total_citations / metrics['total_publications'] if metrics['total_publications'] > 0 else 0
        
        # h-index, g-index, i10-index, i100-index
        citations_list = sorted([p.cited_by_count for p in self.publications], reverse=True)
        
        # h-index
        h_index = 0
        for i, cites in enumerate(citations_list, 1):
            if cites >= i:
                h_index = i
            else:
                break
        metrics['h_index'] = h_index
        
        # g-index
        g_index = 0
        sum_citations = 0
        for i, cites in enumerate(citations_list, 1):
            sum_citations += cites
            if sum_citations >= i * i:
                g_index = i
        metrics['g_index'] = g_index
        
        # i10-index
        metrics['i10_index'] = sum(1 for c in citations_list if c >= 10)
        
        # i100-index
        metrics['i100_index'] = sum(1 for c in citations_list if c >= 100)
        
        # Open Access
        oa_statuses = [p.open_access_status for p in self.publications]
        metrics['open_access_breakdown'] = {
            'gold': oa_statuses.count('gold'),
            'hybrid': oa_statuses.count('hybrid'),
            'green': oa_statuses.count('green'),
            'bronze': oa_statuses.count('bronze'),
            'closed': oa_statuses.count('closed'),
            'unknown': oa_statuses.count('unknown')
        }
        metrics['open_access'] = sum(1 for s in oa_statuses if s not in ['closed', 'unknown'])
        
        # Активные годы
        years = [p.publication_year for p in self.publications if p.publication_year > 0]
        if years:
            metrics['active_years'] = f"{min(years)}-{max(years)}"
            metrics['year_counts'] = Counter(years)
        else:
            metrics['active_years'] = "N/A"
            metrics['year_counts'] = {}
        
        # Уникальные авторы, аффилиации, страны
        all_authors = set()
        all_affiliations = set()
        all_countries = set()
        total_authors = 0
        total_affiliations = 0
        total_countries = 0
        international_papers = 0
        
        for pub in self.publications:
            pub_authors = [a.display_name for a in pub.authors]
            all_authors.update(pub_authors)
            all_affiliations.update(pub.affiliations)
            all_countries.update(pub.countries)
            total_authors += len(pub_authors)
            total_affiliations += len(pub.affiliations)
            total_countries += len(pub.countries)
            
            if len(pub.countries) > 1:
                international_papers += 1
        
        metrics['unique_authors'] = len(all_authors)
        metrics['unique_affiliations'] = len(all_affiliations)
        metrics['unique_countries'] = len(all_countries)
        metrics['avg_authors_per_paper'] = total_authors / metrics['total_publications'] if metrics['total_publications'] > 0 else 0
        metrics['avg_affiliations_per_paper'] = total_affiliations / metrics['total_publications'] if metrics['total_publications'] > 0 else 0
        metrics['avg_countries_per_paper'] = total_countries / metrics['total_publications'] if metrics['total_publications'] > 0 else 0
        metrics['international_collaboration_rate'] = international_papers / metrics['total_publications'] if metrics['total_publications'] > 0 else 0
        
        # Авторская статистика
        author_stats = {}
        for pub in self.publications:
            for author in pub.authors:
                if author.display_name not in author_stats:
                    author_stats[author.display_name] = {
                        'name': author.display_name,
                        'orcid': author.orcid,
                        'affiliations': set(),
                        'countries': set(),
                        'publications': 0,
                        'citations': 0
                    }
                author_stats[author.display_name]['affiliations'].update(author.affiliations)
                author_stats[author.display_name]['countries'].update(author.countries)
                author_stats[author.display_name]['publications'] += 1
                author_stats[author.display_name]['citations'] += pub.cited_by_count
        
        metrics['author_stats'] = sorted(
            [v for v in author_stats.values()],
            key=lambda x: x['publications'],
            reverse=True
        )
        
        # Аффилиации
        aff_stats = {}
        for pub in self.publications:
            for aff in pub.affiliations:
                if aff not in aff_stats:
                    aff_stats[aff] = {'papers': 0, 'citations': 0}
                aff_stats[aff]['papers'] += 1
                aff_stats[aff]['citations'] += pub.cited_by_count
        
        metrics['affiliation_stats'] = sorted(
            [{'name': k, 'papers': v['papers'], 'citations': v['citations']} 
             for k, v in aff_stats.items()],
            key=lambda x: x['papers'],
            reverse=True
        )[:20]
        
        # Страны
        country_counts = Counter()
        for pub in self.publications:
            country_counts.update(pub.countries)
        metrics['country_counts'] = dict(country_counts)
        
        # Коллаборации
        collaboration_patterns = {
            'single_country': 0,
            'international': 0
        }
        
        collaboration_couples = Counter()
        for pub in self.publications:
            if len(pub.countries) <= 1:
                collaboration_patterns['single_country'] += 1
            else:
                collaboration_patterns['international'] += 1
                for i in range(len(pub.countries)):
                    for j in range(i+1, len(pub.countries)):
                        pair = tuple(sorted([pub.countries[i], pub.countries[j]]))
                        collaboration_couples[pair] += 1
        
        metrics['collaboration_patterns'] = collaboration_patterns
        metrics['collaboration_couples'] = dict(collaboration_couples.most_common(20))
        
        # Цитатная динамика
        citation_dynamics = defaultdict(lambda: defaultdict(int))
        for pub in self.publications:
            if pub.id in self.citations:
                for citation in self.citations[pub.id]:
                    citation_dynamics[pub.publication_year][citation.citing_year] += 1
        
        metrics['citation_dynamics'] = citation_dynamics
        
        # Накопленные цитирования
        cumulative_citations = defaultdict(int)
        all_years = sorted(set().union(*[set(d.keys()) for d in citation_dynamics.values()]))
        for pub in self.publications:
            if pub.id in self.citations:
                for citation in self.citations[pub.id]:
                    cumulative_citations[citation.citing_year] += 1
        
        metrics['cumulative_citations'] = dict(sorted(cumulative_citations.items()))
        
        # Most cited publications
        metrics['most_cited'] = sorted(
            self.publications,
            key=lambda x: x.cited_by_count,
            reverse=True
        )[:15]
        
        # Цитирующие работы
        all_citing_works = []
        for citations_list in self.citations.values():
            all_citing_works.extend(citations_list)
        
        metrics['total_citing_works'] = len(all_citing_works)
        
        citing_authors = set()
        citing_affiliations = set()
        citing_countries = set()
        citing_journals = set()
        citing_publishers = set()
        
        citing_author_stats = defaultdict(int)
        citing_aff_stats = defaultdict(int)
        citing_country_stats = defaultdict(int)
        citing_journal_stats = defaultdict(int)
        citing_publisher_stats = defaultdict(int)
        
        for citation in all_citing_works:
            for author in citation.citing_authors:
                citing_authors.add(author.display_name)
                citing_author_stats[author.display_name] += 1
            citing_affiliations.update(citation.citing_authors[0].affiliations if citation.citing_authors else [])
            for aff in citation.citing_authors[0].affiliations if citation.citing_authors else []:
                citing_aff_stats[aff] += 1
            citing_countries.update(citation.citing_countries)
            for country in citation.citing_countries:
                citing_country_stats[country] += 1
            citing_journals.add(citation.citing_journal)
            citing_journal_stats[citation.citing_journal] += 1
            citing_publishers.add(citation.citing_publisher)
            citing_publisher_stats[citation.citing_publisher] += 1
        
        metrics['unique_citing_authors'] = len(citing_authors)
        metrics['unique_citing_affiliations'] = len(citing_affiliations)
        metrics['unique_citing_countries'] = len(citing_countries)
        metrics['unique_citing_journals'] = len(citing_journals)
        metrics['unique_citing_publishers'] = len(citing_publishers)
        
        metrics['top_citing_authors'] = sorted(
            [{'name': k, 'count': v} for k, v in citing_author_stats.items()],
            key=lambda x: x['count'],
            reverse=True
        )[:20]
        
        metrics['top_citing_affiliations'] = sorted(
            [{'name': k, 'count': v} for k, v in citing_aff_stats.items()],
            key=lambda x: x['count'],
            reverse=True
        )[:20]
        
        metrics['top_citing_countries'] = sorted(
            [{'name': k, 'count': v} for k, v in citing_country_stats.items()],
            key=lambda x: x['count'],
            reverse=True
        )[:20]
        
        metrics['top_citing_journals'] = sorted(
            [{'name': k, 'count': v} for k, v in citing_journal_stats.items()],
            key=lambda x: x['count'],
            reverse=True
        )[:20]
        
        metrics['top_citing_publishers'] = sorted(
            [{'name': k, 'count': v} for k, v in citing_publisher_stats.items()],
            key=lambda x: x['count'],
            reverse=True
        )[:20]
        
        # Тематический анализ
        topic_analyzed = defaultdict(lambda: {'count': 0, 'citations': 0, 'years': []})
        for pub in self.publications:
            for topic in pub.topics:
                key = topic.display_name
                topic_analyzed[key]['count'] += 1
                topic_analyzed[key]['citations'] += pub.cited_by_count
                topic_analyzed[key]['years'].append(pub.publication_year)
        
        topic_citing = defaultdict(lambda: {'count': 0, 'citations': 0, 'years': []})
        for citation in all_citing_works:
            for topic in citation.citing_topics:
                key = topic.display_name
                topic_citing[key]['count'] += 1
                topic_citing[key]['years'].append(citation.citing_year)
        
        metrics['topics_analysis'] = []
        all_topics = set(topic_analyzed.keys()) | set(topic_citing.keys())
        
        for topic in all_topics:
            a_count = topic_analyzed[topic]['count']
            c_count = topic_citing[topic]['count']
            a_citations = topic_analyzed[topic]['citations']
            
            # Нормализация
            total_pubs = len(self.publications) or 1
            total_citing = metrics['total_citing_works'] or 1
            
            analyzed_norm = a_count / total_pubs
            citing_norm = c_count / total_citing
            total_norm = (a_count + c_count) / (total_pubs + total_citing)
            
            years_analyzed = topic_analyzed[topic]['years']
            years_citing = topic_citing[topic]['years']
            all_years_topic = years_analyzed + years_citing
            
            first_year = min(all_years_topic) if all_years_topic else 0
            peak_year = max(all_years_topic, key=lambda y: all_years_topic.count(y)) if all_years_topic else 0
            
            metrics['topics_analysis'].append({
                'topic': topic,
                'analyzed_count': a_count,
                'citing_count': c_count,
                'analyzed_norm': analyzed_norm,
                'citing_norm': citing_norm,
                'total_norm': total_norm,
                'first_year': first_year,
                'peak_year': peak_year
            })
        
        metrics['topics_analysis'] = sorted(
            metrics['topics_analysis'],
            key=lambda x: x['total_norm'],
            reverse=True
        )[:20]
        
        return metrics

# ==================== HTML REPORT GENERATOR ====================
class HTMLReportGenerator:
    """Генератор HTML отчета"""
    
    def __init__(self, analyzer: JournalAnalyzer, metrics: Dict, language: str = 'ru'):
        self.analyzer = analyzer
        self.metrics = metrics
        self.language = language
        self.primary_color = '#4A90E2'
        self.secondary_color = '#50C878'
    
    def generate(self) -> str:
        """Генерация полного HTML отчета"""
        lang = self.language
        
        # Якоря для навигации
        anchors = [
            ('overview', get_text('overview')),
            ('analyzed_articles', get_text('analyzed_articles')),
            ('author_analysis', get_text('author_analysis')),
            ('top_affiliations', get_text('top_affiliations')),
            ('geographic_analysis', get_text('geographic_analysis')),
            ('citation_analysis', get_text('citation_analysis')),
            ('citing_works_analysis', get_text('citing_works_analysis')),
            ('topics_analysis', get_text('topics_analysis')),
            ('detailed_citations', get_text('detailed_citations')),
            ('all_publications', get_text('all_publications'))
        ]
        
        html_content = f"""
<!DOCTYPE html>
<html lang="{lang}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{get_text('app_title')} - {self.analyzer.issn}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: #f5f7fa;
            color: #2d3748;
            line-height: 1.6;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }}
        /* Header */
        .header {{
            background: linear-gradient(135deg, {self.primary_color}, {self.secondary_color});
            color: white;
            padding: 30px;
            border-radius: 12px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .header h1 {{ font-size: 28px; margin-bottom: 5px; }}
        .header p {{ opacity: 0.9; font-size: 14px; }}
        
        /* Navigation */
        .nav-container {{
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            background: white;
            padding: 15px 20px;
            border-radius: 12px;
            margin-bottom: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            position: sticky;
            top: 0;
            z-index: 100;
            border: 1px solid #e2e8f0;
        }}
        .nav-container a {{
            color: #4a5568;
            text-decoration: none;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 13px;
            transition: all 0.2s;
            white-space: nowrap;
        }}
        .nav-container a:hover {{
            background: {self.primary_color};
            color: white;
        }}
        .nav-container .nav-level2 {{
            margin-left: 10px;
            font-size: 12px;
            opacity: 0.8;
        }}
        
        /* Sections */
        .section {{
            background: white;
            border-radius: 12px;
            padding: 25px;
            margin-bottom: 25px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            border: 1px solid #e2e8f0;
        }}
        .section-title {{
            font-size: 22px;
            font-weight: 600;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid {self.primary_color};
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .section-title .icon {{ font-size: 24px; }}
        
        .subsection-title {{
            font-size: 18px;
            font-weight: 500;
            margin: 20px 0 15px 0;
            color: #2d3748;
        }}
        
        /* Cards */
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }}
        .metric-card {{
            background: #f7fafc;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid {self.primary_color};
            transition: transform 0.2s;
        }}
        .metric-card:hover {{ transform: translateY(-2px); }}
        .metric-value {{
            font-size: 24px;
            font-weight: 700;
            color: #2d3748;
        }}
        .metric-label {{
            font-size: 13px;
            color: #718096;
            margin-top: 4px;
        }}
        
        /* Tables */
        .table-container {{
            overflow-x: auto;
            margin: 15px 0;
            border-radius: 8px;
            border: 1px solid #e2e8f0;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
        }}
        thead {{
            background: #f7fafc;
            border-bottom: 2px solid #e2e8f0;
        }}
        th {{
            padding: 12px 15px;
            text-align: left;
            font-weight: 600;
            color: #4a5568;
            white-space: nowrap;
        }}
        td {{
            padding: 10px 15px;
            border-bottom: 1px solid #f0f0f0;
        }}
        tr:hover {{
            background: #f7fafc;
        }}
        
        /* Badges */
        .badge {{
            display: inline-block;
            padding: 2px 10px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 500;
        }}
        .badge-primary {{ background: {self.primary_color}; color: white; }}
        .badge-success {{ background: {self.secondary_color}; color: white; }}
        .badge-warning {{ background: #f6ad55; color: white; }}
        .badge-danger {{ background: #fc8181; color: white; }}
        
        /* Progress bars */
        .progress-container {{
            width: 100%;
            height: 8px;
            background: #edf2f7;
            border-radius: 4px;
            overflow: hidden;
            margin: 5px 0;
        }}
        .progress-bar {{
            height: 100%;
            border-radius: 4px;
            transition: width 0.3s;
            background: linear-gradient(90deg, {self.primary_color}, {self.secondary_color});
        }}
        
        /* Collapsible */
        .collapser {{
            cursor: pointer;
            padding: 12px 15px;
            background: #f7fafc;
            border-radius: 6px;
            margin: 8px 0;
            border: 1px solid #e2e8f0;
            transition: all 0.2s;
        }}
        .collapser:hover {{
            background: #edf2f7;
        }}
        .collapser .citation-count {{
            float: right;
            color: {self.primary_color};
            font-weight: 500;
        }}
        .collapser .badge {{
            margin: 0 8px;
        }}
        .citation-detail {{
            padding: 12px 15px;
            margin: 5px 0 5px 20px;
            background: #fafafa;
            border-radius: 6px;
            border-left: 3px solid {self.secondary_color};
        }}
        .citation-detail .cite-meta {{
            font-size: 13px;
            color: #4a5568;
            margin-top: 5px;
        }}
        .citation-detail .doi-link {{
            color: {self.primary_color};
            text-decoration: none;
            font-size: 13px;
        }}
        .citation-detail .doi-link:hover {{
            text-decoration: underline;
        }}
        
        /* Filters */
        .filter-section {{
            background: #f7fafc;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
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
            font-weight: 500;
            color: #4a5568;
            margin-bottom: 4px;
        }}
        .filter-row select, .filter-row input {{
            width: 100%;
            padding: 6px 10px;
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            font-size: 13px;
        }}
        
        /* Word wrap */
        .word-wrap {{
            word-wrap: break-word;
            max-width: 300px;
        }}
        
        /* Footer */
        .footer {{
            text-align: center;
            padding: 20px;
            color: #718096;
            font-size: 13px;
            border-top: 1px solid #e2e8f0;
            margin-top: 30px;
        }}
        
        /* Heatmap */
        .heatmap-cell {{
            text-align: center;
            padding: 6px 10px;
            border-radius: 4px;
            font-weight: 500;
        }}
        
        @media (max-width: 768px) {{
            .metrics-grid {{
                grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
            }}
            .filter-row {{
                flex-direction: column;
            }}
            .filter-row > div {{
                min-width: 100%;
            }}
            .nav-container {{
                flex-direction: column;
            }}
            .nav-container .nav-level2 {{
                margin-left: 20px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>{get_text('app_title')}</h1>
            <p>{get_text('app_subtitle')} | ISSN: {self.analyzer.issn} | {get_text('period_label')}: {self._format_years()}</p>
            <p style="margin-top: 5px; font-size: 13px;">{get_text('total_publications')}: {len(self.analyzer.publications)} | {get_text('total_citations')}: {self.metrics['total_citations']}</p>
        </div>
        
        <!-- Navigation -->
        <nav class="nav-container">
            {''.join([f'<a href="#{anchor}">{label}</a>' for anchor, label in anchors[:2]])}
            <span class="nav-level2">
                {''.join([f'<a href="#{anchor}">{label}</a>' for anchor, label in anchors[2:5]])}
            </span>
            <span class="nav-level2">
                {''.join([f'<a href="#{anchor}">{label}</a>' for anchor, label in anchors[5:8]])}
            </span>
            <span class="nav-level2">
                {''.join([f'<a href="#{anchor}">{label}</a>' for anchor, label in anchors[8:10]])}
            </span>
        </nav>
        
        {self._generate_overview_section()}
        {self._generate_analyzed_articles_section()}
        {self._generate_citation_analysis_section()}
        {self._generate_citing_works_section()}
        {self._generate_topics_section()}
        {self._generate_detailed_citations_section()}
        {self._generate_all_publications_section()}
        
        <!-- Footer -->
        <div class="footer">
            <p>{get_text('footer')}</p>
            <p style="font-size: 11px; margin-top: 5px;">Generated: {datetime.now().strftime('%d.%m.%Y %H:%M')}</p>
        </div>
    </div>
    
    <script>
        function toggleCitations(id) {{
            const el = document.getElementById('citations_' + id);
            if (el) {{
                if (el.style.display === 'none' || el.style.display === '') {{
                    el.style.display = 'block';
                }} else {{
                    el.style.display = 'none';
                }}
            }}
        }}
        
        function filterPublications() {{
            const yearFilter = document.getElementById('yearFilter')?.value || '';
            const titleFilter = document.getElementById('titleFilter')?.value?.toLowerCase() || '';
            const authorFilter = document.getElementById('authorFilter')?.value?.toLowerCase() || '';
            const affFilter = document.getElementById('affFilter')?.value?.toLowerCase() || '';
            const citationFilter = parseInt(document.getElementById('citationFilter')?.value) || 0;
            const searchFilter = document.getElementById('searchInput')?.value?.toLowerCase() || '';
            
            const rows = document.querySelectorAll('#publicationsTable tbody tr');
            let visible = 0;
            
            rows.forEach(row => {{
                const year = row.dataset.year || '';
                const authors = (row.dataset.authors || '').toLowerCase();
                const affiliations = (row.dataset.affiliations || '').toLowerCase();
                const citations = parseInt(row.dataset.citations) || 0;
                const title = (row.dataset.title || '').toLowerCase();
                const doi = (row.dataset.doi || '').toLowerCase();
                
                let show = true;
                
                if (yearFilter && year !== yearFilter) show = false;
                if (titleFilter && !title.includes(titleFilter)) show = false;
                if (authorFilter && !authors.includes(authorFilter)) show = false;
                if (affFilter && !affiliations.includes(affFilter)) show = false;
                if (citationFilter && citations < citationFilter) show = false;
                if (searchFilter && !title.includes(searchFilter) && !authors.includes(searchFilter) && !doi.includes(searchFilter)) show = false;
                
                row.style.display = show ? '' : 'none';
                if (show) visible++;
            }});
            
            const countEl = document.getElementById('visibleCount');
            if (countEl) countEl.textContent = visible + ' publications';
        }}
        
        function sortTable(n) {{
            const table = document.getElementById('publicationsTable');
            const tbody = table.querySelector('tbody');
            const rows = Array.from(tbody.querySelectorAll('tr'));
            const isNumeric = n === 0 || n === 2 || n === 3 || n === 4;
            
            rows.sort((a, b) => {{
                let aVal = a.children[n]?.textContent?.trim() || '';
                let bVal = b.children[n]?.textContent?.trim() || '';
                
                if (isNumeric) {{
                    aVal = parseFloat(aVal) || 0;
                    bVal = parseFloat(bVal) || 0;
                    return aVal - bVal;
                }}
                return aVal.localeCompare(bVal);
            }});
            
            rows.forEach(row => tbody.appendChild(row));
        }}
        
        // Подсветка навигации при скролле
        const sections = document.querySelectorAll('.section');
        const navLinks = document.querySelectorAll('.nav-container a');
        
        window.addEventListener('scroll', () => {{
            let current = '';
            sections.forEach(section => {{
                const sectionTop = section.offsetTop - 120;
                if (window.pageYOffset >= sectionTop) {{
                    current = section.getAttribute('id');
                }}
            }});
            
            navLinks.forEach(link => {{
                link.style.background = '';
                link.style.color = '';
                if (link.getAttribute('href') === '#' + current) {{
                    link.style.background = '{self.primary_color}';
                    link.style.color = 'white';
                }}
            }});
        }});
    </script>
</body>
</html>
"""
        return html_content
    
    def _format_years(self) -> str:
        """Форматирование периода для отображения"""
        years = self.analyzer.years
        if isinstance(years, list):
            return ', '.join(map(str, years))
        elif isinstance(years, tuple):
            return f"{years[0]}-{years[1]}"
        else:
            return str(years)
    
    def _generate_overview_section(self) -> str:
        """Генерация секции Overview"""
        m = self.metrics
        
        # Open Access Breakdown
        oa = m['open_access_breakdown']
        total_oa = sum(oa.values())
        
        oa_rows = ''
        for status, label in [('gold', get_text('gold')), ('hybrid', get_text('hybrid')), 
                             ('green', get_text('green')), ('bronze', get_text('bronze')),
                             ('closed', get_text('closed')), ('unknown', get_text('unknown'))]:
            count = oa.get(status, 0)
            pct = (count / total_oa * 100) if total_oa > 0 else 0
            oa_rows += f'''
            <tr>
                <td>{label}</td>
                <td>{count}</td>
                <td>
                    <div class="progress-container">
                        <div class="progress-bar" style="width: {pct}%;"></div>
                    </div>
                </td>
                <td>{pct:.1f}%</td>
            </tr>
            '''
        
        return f'''
        <div id="overview" class="section">
            <div class="section-title"><span class="icon">📊</span> {get_text('overview')}</div>
            
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-value">{m['total_publications']}</div>
                    <div class="metric-label">{get_text('total_publications')}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{m['total_citations']}</div>
                    <div class="metric-label">{get_text('total_citations')}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{m['h_index']}</div>
                    <div class="metric-label">{get_text('h_index')}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{m['g_index']}</div>
                    <div class="metric-label">{get_text('g_index')}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{m['i10_index']}</div>
                    <div class="metric-label">{get_text('i10_index')}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{m['i100_index']}</div>
                    <div class="metric-label">{get_text('i100_index')}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{m['avg_citations']:.1f}</div>
                    <div class="metric-label">{get_text('avg_citations')}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{m['open_access']}</div>
                    <div class="metric-label">{get_text('open_access')}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{m['active_years']}</div>
                    <div class="metric-label">{get_text('active_years')}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{m['unique_authors']}</div>
                    <div class="metric-label">{get_text('unique_authors')}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{m['unique_affiliations']}</div>
                    <div class="metric-label">{get_text('unique_affiliations')}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{m['unique_countries']}</div>
                    <div class="metric-label">{get_text('unique_countries')}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{m['avg_authors_per_paper']:.2f}</div>
                    <div class="metric-label">{get_text('avg_authors_per_paper')}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{m['avg_affiliations_per_paper']:.2f}</div>
                    <div class="metric-label">{get_text('avg_affiliations_per_paper')}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{m['avg_countries_per_paper']:.2f}</div>
                    <div class="metric-label">{get_text('avg_countries_per_paper')}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{(m['international_collaboration_rate'] * 100):.1f}%</div>
                    <div class="metric-label">{get_text('international_collaboration_rate')}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{m['unique_citing_authors']}</div>
                    <div class="metric-label">{get_text('unique_citing_authors')}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{m['unique_citing_affiliations']}</div>
                    <div class="metric-label">{get_text('unique_citing_affiliations')}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{m['unique_citing_countries']}</div>
                    <div class="metric-label">{get_text('unique_citing_countries')}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{m['unique_citing_journals']}</div>
                    <div class="metric-label">{get_text('unique_citing_journals')}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{m['unique_citing_publishers']}</div>
                    <div class="metric-label">{get_text('unique_citing_publishers')}</div>
                </div>
            </div>
            
            <div class="subsection-title">Open Access Breakdown</div>
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>{get_text('open_access')}</th>
                            <th>{get_text('publications')}</th>
                            <th>%</th>
                            <th></th>
                        </tr>
                    </thead>
                    <tbody>
                        {oa_rows}
                    </tbody>
                </table>
            </div>
        </div>
        '''
    
    def _generate_analyzed_articles_section(self) -> str:
        """Генерация секции Analyzed Articles"""
        m = self.metrics
        
        # 5.1 Author Analysis
        author_rows = ''
        for i, author in enumerate(m['author_stats'][:20], 1):
            author_rows += f'''
            <tr>
                <td>{i}</td>
                <td><strong>{html.escape(author['name'])}</strong></td>
                <td>{author['orcid'] or '-'}</td>
                <td class="word-wrap">{', '.join(list(author['affiliations'])[:3])}</td>
                <td>{', '.join(list(author['countries'])[:3])}</td>
                <td>{author['publications']}</td>
                <td>{author['citations']}</td>
            </tr>
            '''
        
        # 5.2 Top Affiliations
        aff_rows = ''
        for i, aff in enumerate(m['affiliation_stats'][:15], 1):
            aff_rows += f'''
            <tr>
                <td>{i}</td>
                <td>{html.escape(aff['name'])}</td>
                <td>{aff['papers']}</td>
                <td>{aff['citations']}</td>
            </tr>
            '''
        
        # 5.3 Geographic Analysis
        country_rows_unique = ''
        for country, count in sorted(m['country_counts'].items(), key=lambda x: x[1], reverse=True):
            country_rows_unique += f'''
            <tr>
                <td>{country}</td>
                <td>{count}</td>
            </tr>
            '''
        
        # Collaboration patterns
        collab = m['collaboration_patterns']
        total_collab = collab['single_country'] + collab['international']
        single_pct = (collab['single_country'] / total_collab * 100) if total_collab > 0 else 0
        int_pct = (collab['international'] / total_collab * 100) if total_collab > 0 else 0
        
        # Collaboration couples
        couple_rows = ''
        for (c1, c2), count in sorted(m['collaboration_couples'].items(), key=lambda x: x[1], reverse=True)[:20]:
            couple_rows += f'''
            <tr>
                <td>{c1} - {c2}</td>
                <td>{count}</td>
            </tr>
            '''
        
        return f'''
        <div id="analyzed_articles" class="section">
            <div class="section-title"><span class="icon">📄</span> {get_text('analyzed_articles')}</div>
            
            <div id="author_analysis" class="subsection-title">{get_text('author_analysis')}</div>
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>{get_text('rank')}</th>
                            <th>{get_text('authors')}</th>
                            <th>{get_text('orcid')}</th>
                            <th>{get_text('affiliations')}</th>
                            <th>{get_text('countries')}</th>
                            <th>{get_text('publications')}</th>
                            <th>{get_text('citations')}</th>
                        </tr>
                    </thead>
                    <tbody>
                        {author_rows}
                    </tbody>
                </table>
            </div>
            
            <div id="top_affiliations" class="subsection-title">{get_text('top_affiliations')}</div>
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>{get_text('rank')}</th>
                            <th>{get_text('affiliations')}</th>
                            <th>{get_text('publications')}</th>
                            <th>{get_text('citations')}</th>
                        </tr>
                    </thead>
                    <tbody>
                        {aff_rows}
                    </tbody>
                </table>
            </div>
            
            <div id="geographic_analysis" class="subsection-title">{get_text('geographic_analysis')}</div>
            
            <div style="margin: 15px 0;">
                <strong>{get_text('unique_countries_per_publication')}</strong>
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>{get_text('countries')}</th>
                                <th>{get_text('publications')}</th>
                            </tr>
                        </thead>
                        <tbody>
                            {country_rows_unique}
                        </tbody>
                    </table>
                </div>
            </div>
            
            <div style="margin: 15px 0;">
                <strong>{get_text('collaboration_patterns')}</strong>
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>{get_text('collaboration_type')}</th>
                                <th>{get_text('publications')}</th>
                                <th>%</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>{get_text('single_country')}</td>
                                <td>{collab['single_country']}</td>
                                <td>{single_pct:.1f}%</td>
                            </tr>
                            <tr>
                                <td>{get_text('international')}</td>
                                <td>{collab['international']}</td>
                                <td>{int_pct:.1f}%</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
            
            <div style="margin: 15px 0;">
                <strong>{get_text('collaboration_couples')}</strong>
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>{get_text('country_pair')}</th>
                                <th>{get_text('frequency')}</th>
                            </tr>
                        </thead>
                        <tbody>
                            {couple_rows}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        '''
    
    def _generate_citation_analysis_section(self) -> str:
        """Генерация секции Citation Analysis"""
        m = self.metrics
        cd = m['citation_dynamics']
        
        # 6.1 Citation Dynamics by Year
        all_pub_years = sorted(cd.keys())
        all_cit_years = sorted(set().union(*[set(cy.keys()) for cy in cd.values()]))
        
        dynamics_rows = ''
        for pub_year in all_pub_years:
            for cit_year in all_cit_years:
                count = cd.get(pub_year, {}).get(cit_year, 0)
                if count > 0:
                    dynamics_rows += f'''
                    <tr>
                        <td>{pub_year}</td>
                        <td>{cit_year}</td>
                        <td>{count}</td>
                    </tr>
                    '''
        
        # 6.2 Cumulative Citations
        cum = m['cumulative_citations']
        cum_rows = ''
        running = 0
        for year, count in sorted(cum.items()):
            running += count
            cum_rows += f'''
            <tr>
                <td>{year}</td>
                <td>{running}</td>
            </tr>
            '''
        
        # 6.3 Citation Network Heatmap
        heatmap_rows = ''
        for pub_year in all_pub_years:
            heatmap_rows += '<tr>'
            heatmap_rows += f'<td><strong>{pub_year}</strong></td>'
            for cit_year in all_cit_years:
                count = cd.get(pub_year, {}).get(cit_year, 0)
                # Цветовая шкала
                max_val = max([cd.get(py, {}).get(cy, 0) for py in all_pub_years for cy in all_cit_years]) or 1
                intensity = count / max_val
                r = int(74 + (181 * intensity))
                g = int(144 + (111 * intensity))
                b = int(226 - (226 * intensity))
                color = f'rgb({r}, {g}, {b})'
                heatmap_rows += f'<td class="heatmap-cell" style="background: {color};">{count if count > 0 else "-"}</td>'
            heatmap_rows += '</tr>'
        
        # 6.4 Most Cited Publications
        most_cited_rows = ''
        for i, pub in enumerate(m['most_cited'][:15], 1):
            authors = ', '.join([a.display_name for a in pub.authors[:3]])
            if len(pub.authors) > 3:
                authors += ' +' + str(len(pub.authors) - 3) + ' more'
            most_cited_rows += f'''
            <tr>
                <td>{i}</td>
                <td class="word-wrap">{html.escape(pub.title)}</td>
                <td>{pub.publication_year}</td>
                <td>{pub.cited_by_count}</td>
                <td>{pub.citations_per_year:.1f}</td>
                <td class="word-wrap">{html.escape(authors)}</td>
                <td><a href="https://doi.org/{pub.doi}" target="_blank">{pub.doi}</a></td>
            </tr>
            '''
        
        return f'''
        <div id="citation_analysis" class="section">
            <div class="section-title"><span class="icon">📈</span> {get_text('citation_analysis')}</div>
            
            <div class="subsection-title">{get_text('citation_dynamics')}</div>
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>{get_text('publication_year')}</th>
                            <th>{get_text('citation_year')}</th>
                            <th>{get_text('citations_count')}</th>
                        </tr>
                    </thead>
                    <tbody>
                        {dynamics_rows}
                    </tbody>
                </table>
            </div>
            
            <div class="subsection-title">{get_text('cumulative_citations')}</div>
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>{get_text('citation_year')}</th>
                            <th>{get_text('cumulative')}</th>
                        </tr>
                    </thead>
                    <tbody>
                        {cum_rows}
                    </tbody>
                </table>
            </div>
            
            <div class="subsection-title">{get_text('citation_network_heatmap')}</div>
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>{get_text('publication_year')} \\ {get_text('citation_year')}</th>
                            {''.join([f'<th>{y}</th>' for y in all_cit_years])}
                        </tr>
                    </thead>
                    <tbody>
                        {heatmap_rows}
                    </tbody>
                </table>
            </div>
            
            <div class="subsection-title">{get_text('most_cited_publications')}</div>
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>{get_text('rank')}</th>
                            <th>{get_text('title')}</th>
                            <th>{get_text('year')}</th>
                            <th>{get_text('citations')}</th>
                            <th>{get_text('citations_per_year')}</th>
                            <th>{get_text('authors')}</th>
                            <th>{get_text('doi')}</th>
                        </tr>
                    </thead>
                    <tbody>
                        {most_cited_rows}
                    </tbody>
                </table>
            </div>
        </div>
        '''
    
    def _generate_citing_works_section(self) -> str:
        """Генерация секции Citing Works Analysis"""
        m = self.metrics
        
        def generate_top_table(items, title, col1, col2):
            if not items:
                return '<p>No data available</p>'
            rows = ''
            for i, item in enumerate(items[:20], 1):
                rows += f'''
                <tr>
                    <td>{i}</td>
                    <td>{html.escape(item['name'])}</td>
                    <td>{item['count']}</td>
                </tr>
                '''
            return f'''
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>{get_text('rank')}</th>
                            <th>{col1}</th>
                            <th>{col2}</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows}
                    </tbody>
                </table>
            </div>
            '''
        
        return f'''
        <div id="citing_works_analysis" class="section">
            <div class="section-title"><span class="icon">🔗</span> {get_text('citing_works_analysis')}</div>
            
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-value">{m['total_citing_works']}</div>
                    <div class="metric-label">{get_text('total_citing_works')}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{m['unique_citing_authors']}</div>
                    <div class="metric-label">{get_text('unique_citing_authors')}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{m['unique_citing_affiliations']}</div>
                    <div class="metric-label">{get_text('unique_citing_affiliations')}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{m['unique_citing_countries']}</div>
                    <div class="metric-label">{get_text('unique_citing_countries')}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{m['unique_citing_journals']}</div>
                    <div class="metric-label">{get_text('unique_citing_journals')}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{m['unique_citing_publishers']}</div>
                    <div class="metric-label">{get_text('unique_citing_publishers')}</div>
                </div>
            </div>
            
            <div class="subsection-title">{get_text('top_citing_authors')}</div>
            {generate_top_table(m['top_citing_authors'], get_text('top_citing_authors'), get_text('authors'), get_text('citations'))}
            
            <div class="subsection-title">{get_text('top_citing_affiliations')}</div>
            {generate_top_table(m['top_citing_affiliations'], get_text('top_citing_affiliations'), get_text('affiliations'), get_text('citations'))}
            
            <div class="subsection-title">{get_text('top_citing_countries')}</div>
            {generate_top_table(m['top_citing_countries'], get_text('top_citing_countries'), get_text('countries'), get_text('citations'))}
            
            <div class="subsection-title">{get_text('top_citing_journals')}</div>
            {generate_top_table(m['top_citing_journals'], get_text('top_citing_journals'), get_text('journal'), get_text('citations'))}
            
            <div class="subsection-title">{get_text('top_citing_publishers')}</div>
            {generate_top_table(m['top_citing_publishers'], get_text('top_citing_publishers'), get_text('publisher'), get_text('citations'))}
        </div>
        '''
    
    def _generate_topics_section(self) -> str:
        """Генерация секции Topics Analysis"""
        topics = self.metrics.get('topics_analysis', [])
        
        topics_rows = ''
        for t in topics[:20]:
            topics_rows += f'''
            <tr>
                <td class="word-wrap">{html.escape(t['topic'])}</td>
                <td>{t['analyzed_count']}</td>
                <td>{t['citing_count']}</td>
                <td>{t['analyzed_norm']:.3f}</td>
                <td>{t['citing_norm']:.3f}</td>
                <td>{t['total_norm']:.3f}</td>
                <td>{t['first_year']}</td>
                <td>{t['peak_year']}</td>
            </tr>
            '''
        
        # Топ-10 по категориям
        def get_top_concepts(category: str, limit: int = 10) -> List:
            """Получение топ-концепций по категории"""
            concept_counts = defaultdict(int)
            concept_citations = defaultdict(int)
            
            for pub in self.analyzer.publications:
                for topic in pub.topics:
                    if category == 'topic':
                        name = topic.display_name
                    elif category == 'subtopic':
                        name = topic.subtopic or topic.display_name
                    elif category == 'field':
                        name = topic.topic_field or topic.display_name  # исправлено
                    elif category == 'domain':
                        name = topic.domain or topic.display_name
                    elif category == 'concept':
                        for concept in topic.concepts[:3]:
                            concept_counts[concept] += 1
                            concept_citations[concept] += pub.cited_by_count
                        continue
                    else:
                        name = topic.display_name
                    
                    concept_counts[name] += 1
                    concept_citations[name] += pub.cited_by_count
            
            if category == 'concept':
                return sorted(
                    [{'name': k, 'count': v, 'citations': concept_citations[k]} 
                     for k, v in concept_counts.items()],
                    key=lambda x: x['count'],
                    reverse=True
                )[:limit]
            
            return sorted(
                [{'name': k, 'count': v, 'citations': concept_citations[k]} 
                 for k, v in concept_counts.items()],
                key=lambda x: x['citations'],
                reverse=True
            )[:limit]
        
        def generate_concept_table(items, title):
            if not items:
                return '<p>No data available</p>'
            rows = ''
            for i, item in enumerate(items[:10], 1):
                rows += f'''
                <tr>
                    <td>{i}</td>
                    <td>{html.escape(item['name'])}</td>
                    <td>{item['count']}</td>
                    <td>{item['citations']}</td>
                </tr>
                '''
            return f'''
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>{get_text('rank')}</th>
                            <th>{title}</th>
                            <th>{get_text('publications')}</th>
                            <th>{get_text('citations')}</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows}
                    </tbody>
                </table>
            </div>
            '''
        
        top_topics = get_top_concepts('topic')
        top_subtopics = get_top_concepts('subtopic')
        top_fields = get_top_concepts('field')
        top_domains = get_top_concepts('domain')
        top_concepts = get_top_concepts('concept')
        
        return f'''
        <div id="topics_analysis" class="section">
            <div class="section-title"><span class="icon">🏷️</span> {get_text('topics_analysis')}</div>
            
            <div class="subsection-title">{get_text('topics')}</div>
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>{get_text('topics')}</th>
                            <th>{get_text('analyzed_count')}</th>
                            <th>{get_text('citing_count')}</th>
                            <th>{get_text('analyzed_norm_count')}</th>
                            <th>{get_text('citing_norm_count')}</th>
                            <th>{get_text('total_norm_count')}</th>
                            <th>{get_text('first_year')}</th>
                            <th>{get_text('peak_year')}</th>
                        </tr>
                    </thead>
                    <tbody>
                        {topics_rows}
                    </tbody>
                </table>
            </div>
            
            <div class="subsection-title">{get_text('top_topics')}</div>
            {generate_concept_table(top_topics, get_text('topics'))}
            
            <div class="subsection-title">{get_text('top_subtopics')}</div>
            {generate_concept_table(top_subtopics, get_text('topics'))}
            
            <div class="subsection-title">{get_text('top_fields')}</div>
            {generate_concept_table(top_fields, get_text('topics'))}
            
            <div class="subsection-title">{get_text('top_domains')}</div>
            {generate_concept_table(top_domains, get_text('topics'))}
            
            <div class="subsection-title">{get_text('top_concepts')}</div>
            {generate_concept_table(top_concepts, get_text('topics'))}
        </div>
        '''
    
    def _generate_detailed_citations_section(self) -> str:
        """Генерация секции Detailed Citations"""
        detailed_sections = ''
        
        for pub in self.analyzer.publications[:50]:  # Ограничиваем для производительности
            if pub.id in self.analyzer.citations and self.analyzer.citations[pub.id]:
                citations_list = self.analyzer.citations[pub.id]
                pub_id = pub.id.replace('https://openalex.org/', '')
                
                citation_items = ''
                for cite in citations_list[:20]:  # Ограничиваем
                    citation_items += f'''
                    <div class="citation-detail">
                        <div><strong>{html.escape(cite.citing_title)}</strong></div>
                        <div class="cite-meta">
                            <strong>{get_text('citing_journal')}:</strong> {html.escape(cite.citing_journal)} | 
                            <strong>{get_text('citing_year')}:</strong> {cite.citing_year} | 
                            <strong>{get_text('citing_date')}:</strong> {cite.citing_date} |
                            <strong>{get_text('citation_lag')}:</strong> {cite.citation_lag} years
                        </div>
                        <div class="cite-meta">
                            <strong>{get_text('authors')}:</strong> {', '.join([a.display_name for a in cite.citing_authors[:5]])}
                            {', +' + str(len(cite.citing_authors) - 5) + ' more' if len(cite.citing_authors) > 5 else ''} |
                            <strong>{get_text('countries')}:</strong> {', '.join(cite.citing_countries[:3])}
                        </div>
                        <div class="cite-meta">
                            <a href="https://doi.org/{cite.citing_doi}" target="_blank" class="doi-link">DOI: {cite.citing_doi}</a>
                        </div>
                    </div>
                    '''
                
                detailed_sections += f'''
                <div class="collapser" onclick="toggleCitations('{pub_id}')">
                    <strong>{html.escape(pub.title[:100])}{'...' if len(pub.title) > 100 else ''}</strong>
                    <span class="badge badge-primary">{pub.publication_year}</span>
                    <span class="citation-count">{len(citations_list)} {get_text('citations')}</span>
                    <span style="font-size: 12px; color: #666; margin-left: 10px;">DOI: {pub.doi}</span>
                    <span style="float: right; font-size: 12px; color: #666;">Click to toggle</span>
                </div>
                <div id="citations_{pub_id}" style="display: none; margin: 5px 0 15px 0;">
                    {citation_items}
                </div>
                '''
        
        return f'''
        <div id="detailed_citations" class="section">
            <div class="section-title"><span class="icon">📋</span> {get_text('detailed_citations')}</div>
            {detailed_sections if detailed_sections else '<p>No citation data available</p>'}
        </div>
        '''
    
    def _generate_all_publications_section(self) -> str:
        """Генерация секции All Publications"""
        pubs = self.analyzer.publications
        
        # Получаем все года для фильтра
        years = sorted(set(p.publication_year for p in pubs if p.publication_year > 0), reverse=True)
        
        pub_rows = ''
        for i, pub in enumerate(pubs, 1):
            authors = ', '.join([a.display_name for a in pub.authors[:3]])
            if len(pub.authors) > 3:
                authors += ' +' + str(len(pub.authors) - 3) + ' more'
            
            affiliations = ', '.join(pub.affiliations[:2])
            if len(pub.affiliations) > 2:
                affiliations += ' +' + str(len(pub.affiliations) - 2) + ' more'
            
            pub_rows += f'''
            <tr data-year="{pub.publication_year}" 
                data-authors="{','.join([a.display_name for a in pub.authors])}" 
                data-affiliations="{','.join(pub.affiliations)}"
                data-citations="{pub.cited_by_count}" 
                data-title="{pub.title.lower()}" 
                data-doi="{pub.doi.lower()}">
                <td>{i}</td>
                <td class="word-wrap">{html.escape(pub.title)}</td>
                <td>{pub.publication_year}</td>
                <td class="word-wrap">{html.escape(authors)}</td>
                <td class="word-wrap">{html.escape(affiliations)}</td>
                <td><span class="badge badge-primary">{pub.cited_by_count}</span></td>
                <td>{pub.citations_per_year:.1f}</td>
                <td><a href="https://doi.org/{pub.doi}" target="_blank" class="doi-link">{pub.doi}</a></td>
                <td>
                    <button onclick="toggleCitations('{pub.id.replace('https://openalex.org/', '')}')" 
                            style="padding: 3px 8px; border: none; border-radius: 4px; 
                                   background: {self.primary_color}; color: white; 
                                   cursor: pointer; font-size: 11px;">
                        {get_text('show_citations')}
                    </button>
                </td>
            </tr>
            '''
        
        year_options = ''.join([f'<option value="{y}">{y}</option>' for y in years])
        
        return f'''
        <div id="all_publications" class="section">
            <div class="section-title"><span class="icon">📚</span> {get_text('all_publications')}</div>
            
            <div class="filter-section">
                <div class="filter-row">
                    <div>
                        <label for="yearFilter">{get_text('filter_by_year')}</label>
                        <select id="yearFilter" onchange="filterPublications()">
                            <option value="">{get_text('all_years')}</option>
                            {year_options}
                        </select>
                    </div>
                    <div>
                        <label for="titleFilter">{get_text('filter_by_title')}</label>
                        <input type="text" id="titleFilter" placeholder="Search title..." onkeyup="filterPublications()">
                    </div>
                    <div>
                        <label for="authorFilter">{get_text('filter_by_author')}</label>
                        <input type="text" id="authorFilter" placeholder="Author name..." onkeyup="filterPublications()">
                    </div>
                    <div>
                        <label for="affFilter">{get_text('filter_by_affiliation')}</label>
                        <input type="text" id="affFilter" placeholder="Affiliation..." onkeyup="filterPublications()">
                    </div>
                    <div>
                        <label for="citationFilter">{get_text('filter_by_citations')}</label>
                        <input type="number" id="citationFilter" placeholder="Min citations..." min="0" onchange="filterPublications()">
                    </div>
                    <div>
                        <label for="searchInput">{get_text('search_publications')}</label>
                        <input type="text" id="searchInput" placeholder="Search..." onkeyup="filterPublications()">
                    </div>
                    <div>
                        <span id="visibleCount" style="font-weight: 500;">{len(pubs)} {get_text('publications')}</span>
                    </div>
                </div>
            </div>
            
            <div class="table-container" style="max-height: 800px; overflow-y: auto;">
                <table id="publicationsTable">
                    <thead>
                        <tr>
                            <th onclick="sortTable(0)" style="cursor: pointer;">#</th>
                            <th onclick="sortTable(1)" style="cursor: pointer;">{get_text('title')}</th>
                            <th onclick="sortTable(2)" style="cursor: pointer;">{get_text('year')}</th>
                            <th onclick="sortTable(3)" style="cursor: pointer;">{get_text('authors')}</th>
                            <th onclick="sortTable(4)" style="cursor: pointer;">{get_text('affiliations')}</th>
                            <th onclick="sortTable(5)" style="cursor: pointer;">{get_text('citations')}</th>
                            <th onclick="sortTable(6)" style="cursor: pointer;">{get_text('citations_per_year')}</th>
                            <th>{get_text('doi')}</th>
                            <th>{get_text('show_citations')}</th>
                        </tr>
                    </thead>
                    <tbody>
                        {pub_rows}
                    </tbody>
                </table>
            </div>
        </div>
        '''

# ==================== STREAMLIT APP ====================
def init_session_state():
    """Инициализация состояния сессии"""
    if 'language' not in st.session_state:
        st.session_state.language = 'ru'
    if 'analyzer' not in st.session_state:
        st.session_state.analyzer = None
    if 'metrics' not in st.session_state:
        st.session_state.metrics = None
    if 'report_html' not in st.session_state:
        st.session_state.report_html = None
    if 'analysis_complete' not in st.session_state:
        st.session_state.analysis_complete = False

def main():
    """Главная функция приложения"""
    st.set_page_config(
        page_title="Advanced Journal Analysis Tool",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    init_session_state()
    
    # Заголовок
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #4A90E2, #50C878); 
                padding: 20px; border-radius: 12px; color: white; margin-bottom: 20px;">
        <h1 style="margin: 0;">📊 {get_text('app_title')}</h1>
        <p style="margin: 5px 0 0 0; opacity: 0.9;">{get_text('app_subtitle')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Боковая панель с настройками
    with st.sidebar:
        st.markdown("### ⚙️ Настройки")
        
        # Язык
        language = st.selectbox(
            get_text('language_label'),
            options=['ru', 'en'],
            format_func=lambda x: 'Русский' if x == 'ru' else 'English',
            index=0 if st.session_state.language == 'ru' else 1
        )
        if language != st.session_state.language:
            st.session_state.language = language
            st.rerun()
        
        st.markdown("---")
        
        # Входные данные
        issn = st.text_input(
            get_text('issn_label'),
            placeholder=get_text('issn_placeholder'),
            value='0028-0836'
        )
        
        period = st.text_input(
            get_text('period_label'),
            placeholder=get_text('period_placeholder'),
            value='2020-2023'
        )
        
        max_workers = st.slider(
            get_text('workers_label'),
            min_value=4,
            max_value=12,
            value=8,
            step=1
        )
        
        st.markdown("---")
        
        # Кнопка анализа
        analyze_button = st.button(
            get_text('analyze_button'),
            type="primary",
            use_container_width=True
        )
        
        # Кнопка скачивания отчета (если анализ завершен)
        if st.session_state.analysis_complete and st.session_state.report_html:
            st.markdown("---")
            st.download_button(
                label=get_text('download_report'),
                data=st.session_state.report_html,
                file_name=f"journal_analysis_{issn.replace('-', '')}_{datetime.now().strftime('%Y%m%d')}.html",
                mime="text/html",
                use_container_width=True
            )
    
    # Основная область
    if analyze_button:
        if not issn or not period:
            st.error(get_text('fill_fields'))
            return
        
        # Парсинг периода
        try:
            if ',' in period:
                years = [int(y.strip()) for y in period.split(',') if y.strip().isdigit()]
            elif '-' in period:
                parts = period.split('-')
                years = (int(parts[0].strip()), int(parts[1].strip()))
            else:
                years = int(period)
        except:
            st.error(get_text('invalid_issn'))
            return
        
        # Запуск анализа
        with st.status(get_text('analyzing'), expanded=True) as status:
            # Прогресс-бар
            progress = st.progress(0, text=get_text('loading_articles'))
            
            # Создание анализатора
            analyzer = JournalAnalyzer(issn, years, max_workers)
            
            # Выполнение анализа
            success = analyzer.run_analysis(progress)
            
            if success:
                status.update(label=get_text('complete'), state="complete")
                
                # Расчет метрик
                progress.progress(95, text=get_text('generating_report'))
                metrics = analyzer.calculate_metrics()
                
                # Генерация отчета
                report_gen = HTMLReportGenerator(analyzer, metrics, st.session_state.language)
                report_html = report_gen.generate()
                
                # Сохранение в сессию
                st.session_state.analyzer = analyzer
                st.session_state.metrics = metrics
                st.session_state.report_html = report_html
                st.session_state.analysis_complete = True
                
                progress.progress(100, text=get_text('complete'))
                
                # Отображение отчета
                st.components.v1.html(report_html, height=800, scrolling=True)
                
            else:
                status.update(label=get_text('error'), state="error")
                st.error("Анализ не удался. Проверьте ISSN и период.")
    
    # Показ сохраненного отчета
    elif st.session_state.analysis_complete and st.session_state.report_html:
        st.components.v1.html(st.session_state.report_html, height=800, scrolling=True)
    
    # Информация о приложении
    else:
        st.info("""
        ### 📋 Инструкция
        
        1. Введите **ISSN** журнала (например, 0028-0836 для Nature)
        2. Укажите **период** анализа:
           - Одиночный год: `2022`
           - Диапазон: `2020-2023`
           - Список: `2020,2022,2023`
        3. Настройте **количество потоков** (оптимально 6-10)
        4. Нажмите **"Запустить анализ"**
        
        После завершения анализа будет сгенерирован HTML-отчет со всеми метриками и таблицами.
        """)
        
        # Примеры
        st.markdown("### 📚 Примеры ISSN")
        examples = [
            ("0028-0836", "Nature"),
            ("0036-8075", "Science"),
            ("1095-9203", "Science (online)"),
            ("1476-4687", "Nature (online)"),
            ("0140-6736", "The Lancet")
        ]
        for code, name in examples:
            st.markdown(f"- `{code}` - {name}")

if __name__ == "__main__":
    main()
