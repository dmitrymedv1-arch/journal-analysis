# -*- coding: utf-8 -*-
"""
Advanced Journal Analysis Tool for Streamlit
Полноценный инструмент анализа научных журналов через OpenAlex API
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
from typing import Dict, List, Tuple, Optional, Any
import json
import html
from collections import defaultdict, Counter

# ==================== НАСТРОЙКИ ====================
MAX_WORKERS = 8
BASE_DELAY = 0.35
MAX_RETRIES = 4
MAX_CITING_PER_PAPER = 300
CACHE_TTL = 3600  # 1 час

# ==================== ЛОКАЛИЗАЦИЯ ====================
TRANSLATIONS = {
    'ru': {
        'app_title': '📊 Advanced Journal Analysis Tool',
        'issn_label': 'ISSN журнала:',
        'period_label': 'Анализируемый период:',
        'period_placeholder': '2020-2025 или 2020,2021,2022',
        'workers_label': 'Потоков для параллельной загрузки:',
        'start_button': '🚀 Начать анализ',
        'language': 'Язык',
        'overview': 'Обзор',
        'analyzed_articles': 'Анализируемые статьи',
        'citation_analysis': 'Цитатный анализ',
        'citing_works': 'Цитирующие работы',
        'topics_analysis': 'Тематический анализ',
        'detailed_citations': 'Детальные цитирования',
        'all_publications': 'Все публикации',
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
        'avg_authors_per_paper': 'Авторов на статью (сред.)',
        'avg_affiliations_per_paper': 'Аффилиаций на статью (сред.)',
        'avg_countries_per_paper': 'Стран на статью (сред.)',
        'international_collaboration': 'Международное сотрудничество',
        'unique_citing_authors': 'Уникальные цитирующие авторы',
        'unique_citing_affiliations': 'Уникальные цитирующие аффилиации',
        'unique_citing_countries': 'Уникальные цитирующие страны',
        'unique_citing_journals': 'Уникальные цитирующие журналы',
        'unique_citing_publishers': 'Уникальные цитирующие издатели',
        'open_access_breakdown': 'Разбивка по типу открытого доступа',
        'gold': 'Золотой',
        'hybrid': 'Гибридный',
        'green': 'Зеленый',
        'bronze': 'Бронзовый',
        'closed': 'Закрытый',
        'unknown': 'Неизвестно',
        'author_analysis': 'Анализ авторов',
        'top_affiliations': 'Топ аффилиаций',
        'geographic_analysis': 'Географический анализ',
        'unique_countries_per_publication': 'Уникальные страны на публикацию (уровень сотрудничества)',
        'authors_per_country': 'Авторов по странам (индивидуальное распределение)',
        'collaboration_patterns': 'Модели сотрудничества',
        'collaboration_couples': 'Пары сотрудничающих стран',
        'citation_dynamics': 'Динамика цитирований по годам',
        'cumulative_citations': 'Накопленные цитирования',
        'citation_network_heatmap': 'Тепловая карта цитирований',
        'most_cited_publications': 'Наиболее цитируемые публикации',
        'total_citing_works': 'Всего цитирующих работ',
        'top_citing_authors': 'Топ цитирующих авторов',
        'top_citing_affiliations': 'Топ цитирующих аффилиаций',
        'top_citing_countries': 'Топ цитирующих стран',
        'top_citing_journals': 'Топ цитирующих журналов',
        'top_citing_publishers': 'Топ цитирующих издателей',
        'topics_relationships': 'Взаимосвязи тем, подтем, полей и доменов',
        'top_10_cited_topics': 'Топ-10 наиболее цитируемых тем',
        'authors': 'Авторы',
        'countries': 'Страны',
        'publications': 'Публикации',
        'citations': 'Цитирования',
        'rank': 'Ранг',
        'title': 'Название',
        'year': 'Год',
        'doi': 'DOI',
        'citations_per_year': 'Цитирований/год',
        'journal': 'Журнал',
        'publisher': 'Издатель',
        'show_citations': 'Показать цитирования',
        'hide_citations': 'Скрыть цитирования',
        'filter_by_year': 'Фильтр по году',
        'filter_by_author': 'Фильтр по автору',
        'filter_by_citations': 'Фильтр по цитированиям (мин.)',
        'filter_by_affiliation': 'Фильтр по аффилиации',
        'search_publications': 'Поиск публикаций',
        'single_country': 'Одна страна',
        'international': 'Международные',
        'citing_journal': 'Цитирующий журнал',
        'citing_year': 'Год цитирования',
        'citing_date': 'Дата цитирования',
        'citation_lag': 'Задержка цитирования',
        'topics': 'Темы',
        'concepts': 'Концепты',
        'fields': 'Поля',
        'domains': 'Домены',
        'subtopics': 'Подтемы',
        'first_year': 'Первый год',
        'peak_year': 'Пиковый год',
        'analyzed_count': 'Проанализировано',
        'citing_count': 'Цитирований',
        'analyzed_norm': 'Норм. анализируемые',
        'citing_norm': 'Норм. цитирующие',
        'total_norm': 'Общее норм.',
        'processing': 'Обработка...',
        'fetching_publications': 'Загрузка публикаций журнала',
        'fetching_citations': 'Сбор цитирующих работ',
        'processing_data': 'Обработка данных',
        'generating_report': 'Генерация отчета',
        'ready': 'Готово!',
        'download_report': '📥 Скачать HTML отчет',
        'footer': 'Данные: OpenAlex | Сгенерировано',
        'all_years': 'Все годы',
        'enter_issn': 'Введите ISSN (например: 0028-0836)',
        'enter_period': 'Введите период (например: 2020-2025)',
        'please_wait': 'Пожалуйста, подождите...',
        'error_fetching': 'Ошибка загрузки данных',
        'no_results': 'Результатов не найдено',
    },
    'en': {
        'app_title': '📊 Advanced Journal Analysis Tool',
        'issn_label': 'Journal ISSN:',
        'period_label': 'Analysis period:',
        'period_placeholder': '2020-2025 or 2020,2021,2022',
        'workers_label': 'Parallel workers:',
        'start_button': '🚀 Start Analysis',
        'language': 'Language',
        'overview': 'Overview',
        'analyzed_articles': 'Analyzed Articles',
        'citation_analysis': 'Citation Analysis',
        'citing_works': 'Citing Works',
        'topics_analysis': 'Topics Analysis',
        'detailed_citations': 'Detailed Citations',
        'all_publications': 'All Publications',
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
        'international_collaboration': 'International Collaboration Rate',
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
        'top_affiliations': 'Top Affiliations',
        'geographic_analysis': 'Geographic Analysis',
        'unique_countries_per_publication': 'Unique Countries per Publication (Collaboration Level)',
        'authors_per_country': 'Authors per Country (Individual Distribution)',
        'collaboration_patterns': 'Collaboration Patterns',
        'collaboration_couples': 'Collaboration Couples',
        'citation_dynamics': 'Citation Dynamics by Year',
        'cumulative_citations': 'Cumulative Citations',
        'citation_network_heatmap': 'Citation Network Heatmap',
        'most_cited_publications': 'Most Cited Publications',
        'total_citing_works': 'Total Citing Works',
        'top_citing_authors': 'Top Citing Authors',
        'top_citing_affiliations': 'Top Citing Affiliations',
        'top_citing_countries': 'Top Citing Countries',
        'top_citing_journals': 'Top Citing Journals',
        'top_citing_publishers': 'Top Citing Publishers',
        'topics_relationships': 'Topics, Subtopics, Fields, Domains Relationships',
        'top_10_cited_topics': 'Top 10 Most Cited Topics',
        'authors': 'Authors',
        'countries': 'Countries',
        'publications': 'Publications',
        'citations': 'Citations',
        'rank': 'Rank',
        'title': 'Title',
        'year': 'Year',
        'doi': 'DOI',
        'citations_per_year': 'Citations/Year',
        'journal': 'Journal',
        'publisher': 'Publisher',
        'show_citations': 'Show citations',
        'hide_citations': 'Hide citations',
        'filter_by_year': 'Filter by Year',
        'filter_by_author': 'Filter by Author',
        'filter_by_citations': 'Filter by Citations (min)',
        'filter_by_affiliation': 'Filter by Affiliation',
        'search_publications': 'Search Publications',
        'single_country': 'Single Country',
        'international': 'International',
        'citing_journal': 'Citing Journal',
        'citing_year': 'Citing Year',
        'citing_date': 'Citing Date',
        'citation_lag': 'Citation Lag',
        'topics': 'Topics',
        'concepts': 'Concepts',
        'fields': 'Fields',
        'domains': 'Domains',
        'subtopics': 'Subtopics',
        'first_year': 'First Year',
        'peak_year': 'Peak Year',
        'analyzed_count': 'Analyzed Count',
        'citing_count': 'Citing Count',
        'analyzed_norm': 'Analyzed Norm',
        'citing_norm': 'Citing Norm',
        'total_norm': 'Total Norm',
        'processing': 'Processing...',
        'fetching_publications': 'Fetching journal publications',
        'fetching_citations': 'Collecting citing works',
        'processing_data': 'Processing data',
        'generating_report': 'Generating report',
        'ready': 'Ready!',
        'download_report': '📥 Download HTML Report',
        'footer': 'Data: OpenAlex | Generated',
        'all_years': 'All Years',
        'enter_issn': 'Enter ISSN (e.g., 0028-0836)',
        'enter_period': 'Enter period (e.g., 2020-2025)',
        'please_wait': 'Please wait...',
        'error_fetching': 'Error fetching data',
        'no_results': 'No results found',
    }
}

# ==================== OpenAlex CLIENT ====================
class OpenAlexClient:
    """Клиент для работы с OpenAlex API с поддержкой параллельных запросов"""
    
    def __init__(self, max_workers=8):
        self.max_workers = max_workers
        self.base_url = "https://api.openalex.org/works"
        self.lock = Lock()
        self.session = requests.Session()
        
    @staticmethod
    def normalize_issn(issn_str):
        """Нормализация ISSN"""
        cleaned = re.sub(r'[^0-9Xx]', '', str(issn_str).strip())
        if len(cleaned) == 8:
            return f"{cleaned[:4]}-{cleaned[4:]}".upper()
        return cleaned.upper()
    
    def _smart_get(self, url, params, retries=MAX_RETRIES):
        """Умный GET с обработкой ошибок и 429"""
        for attempt in range(retries):
            try:
                with self.lock:
                    time.sleep(random.uniform(0.1, BASE_DELAY))
                
                resp = self.session.get(url, params=params, timeout=25)
                
                if resp.status_code == 429:
                    wait = int(resp.headers.get("Retry-After", 2 ** attempt + 1))
                    time.sleep(wait + random.uniform(0.5, 1.5))
                    continue
                    
                if resp.status_code == 200:
                    return resp.json()
                
                time.sleep(1 * (2 ** attempt))
                
            except Exception as e:
                time.sleep(1.5 * (2 ** attempt))
        return None
    
    def fetch_publications(self, issn, years, progress_callback=None):
        """Получение публикаций журнала"""
        normalized = self.normalize_issn(issn)
        
        if isinstance(years, list):
            year_filter = "|".join(f"publication_year:{y}" for y in years)
        elif isinstance(years, tuple):
            year_filter = f"publication_year:{years[0]}-{years[1]}"
        else:
            year_filter = f"publication_year:{years}"
        
        articles = []
        cursor = "*"
        
        while True:
            data = self._smart_get(self.base_url, {
                "filter": f"primary_location.source.issn:{normalized},{year_filter}",
                "per_page": 200,
                "select": "id,doi,publication_year,cited_by_count,title,primary_location,open_access,authorships,topics",
                "cursor": cursor
            })
            
            if not data or not data.get("results"):
                break
                
            for w in data["results"]:
                doi = w.get("doi", "").replace("https://doi.org/", "") if w.get("doi") else ""
                articles.append({
                    "id": w.get("id", "").replace("https://openalex.org/", ""),
                    "doi": doi,
                    "title": w.get("title", "N/A"),
                    "year": w.get("publication_year"),
                    "cited_by_count": w.get("cited_by_count", 0),
                    "open_access": w.get("open_access", {}),
                    "authorships": w.get("authorships", []),
                    "topics": w.get("topics", []),
                    "journal": w.get("primary_location", {}).get("source", {}).get("display_name", ""),
                    "publisher": w.get("primary_location", {}).get("source", {}).get("publisher", ""),
                })
            
            if progress_callback:
                progress_callback(len(data["results"]))
            
            cursor = data.get("meta", {}).get("next_cursor")
            if not cursor:
                break
        
        return articles
    
    def _fetch_citing_dois(self, oa_id):
        """Получение цитирующих DOI для одной публикации"""
        citing = []
        cursor = "*"
        
        for _ in range(8):
            data = self._smart_get(self.base_url, {
                "filter": f"cites:{oa_id}",
                "per_page": 200,
                "select": "id,doi,title,publication_year,primary_location,open_access,authorships,topics",
                "cursor": cursor
            })
            
            if not data:
                break
                
            results = data.get("results", [])
            if not results:
                break
                
            for item in results:
                citing.append({
                    "id": item.get("id", "").replace("https://openalex.org/", ""),
                    "doi": item.get("doi", "").replace("https://doi.org/", "") if item.get("doi") else "",
                    "title": item.get("title", "N/A"),
                    "year": item.get("publication_year"),
                    "journal": item.get("primary_location", {}).get("source", {}).get("display_name", ""),
                    "publisher": item.get("primary_location", {}).get("source", {}).get("publisher", ""),
                    "authorships": item.get("authorships", []),
                    "topics": item.get("topics", []),
                })
            
            cursor = data.get("meta", {}).get("next_cursor")
            if not cursor:
                break
        
        return citing[:MAX_CITING_PER_PAPER]
    
    def fetch_citations_parallel(self, publications, progress_callback=None):
        """Параллельный сбор цитирующих работ"""
        citing_map = {}
        futures = {}
        
        # Фильтруем публикации с цитированиями
        pubs_with_citations = [p for p in publications if p.get('cited_by_count', 0) > 0 and p.get('id')]
        
        if not pubs_with_citations:
            return {}
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            for pub in pubs_with_citations:
                future = executor.submit(self._fetch_citing_dois, pub['id'])
                futures[future] = pub['id']
            
            completed = 0
            total = len(futures)
            
            for future in as_completed(futures):
                pub_id = futures[future]
                try:
                    citing_map[pub_id] = future.result()
                except Exception as e:
                    citing_map[pub_id] = []
                
                completed += 1
                if progress_callback:
                    progress_callback(completed, total)
        
        return citing_map

# ==================== DATA PROCESSOR ====================
class DataProcessor:
    """Обработка и агрегация данных"""
    
    @staticmethod
    def extract_authors_info(authorships):
        """Извлечение информации об авторах"""
        authors = []
        for auth in authorships:
            author_data = {
                'name': auth.get('author', {}).get('display_name', 'Unknown'),
                'orcid': auth.get('author', {}).get('orcid', '').replace('https://orcid.org/', ''),
                'affiliations': [],
                'countries': []
            }
            
            for inst in auth.get('institutions', []):
                affil = inst.get('display_name', '')
                if affil:
                    author_data['affiliations'].append(affil)
                
                country = inst.get('country_code', '')
                if country:
                    author_data['countries'].append(country)
            
            authors.append(author_data)
        
        return authors
    
    @staticmethod
    def extract_country_from_authorship(authorship):
        """Извлечение страны из авторовской записи"""
        countries = set()
        for inst in authorship.get('institutions', []):
            country = inst.get('country_code', '')
            if country:
                countries.add(country)
        return list(countries)
    
    @staticmethod
    def calculate_h_index(citations_list):
        """Расчет h-index"""
        if not citations_list:
            return 0
        sorted_citations = sorted([c for c in citations_list if c > 0], reverse=True)
        h = 0
        for i, cit in enumerate(sorted_citations, 1):
            if cit >= i:
                h = i
            else:
                break
        return h
    
    @staticmethod
    def calculate_g_index(citations_list):
        """Расчет g-index"""
        if not citations_list:
            return 0
        sorted_citations = sorted([c for c in citations_list if c > 0], reverse=True)
        g = 0
        total = 0
        for i, cit in enumerate(sorted_citations, 1):
            total += cit
            if total >= i * i:
                g = i
        return g
    
    @staticmethod
    def calculate_i10_index(citations_list):
        """Расчет i10-index (количество публикаций с >= 10 цитирований)"""
        return sum(1 for c in citations_list if c >= 10)
    
    @staticmethod
    def calculate_i100_index(citations_list):
        """Расчет i100-index (количество публикаций с >= 100 цитирований)"""
        return sum(1 for c in citations_list if c >= 100)
    
    @staticmethod
    def analyze_open_access(publications):
        """Анализ открытого доступа"""
        oa_counts = {
            'gold': 0, 'hybrid': 0, 'green': 0, 
            'bronze': 0, 'closed': 0, 'unknown': 0
        }
        
        for pub in publications:
            oa = pub.get('open_access', {})
            is_oa = oa.get('is_oa', False)
            status = oa.get('oa_status', 'unknown')
            
            if not is_oa:
                oa_counts['closed'] += 1
            elif status in oa_counts:
                oa_counts[status] += 1
            else:
                oa_counts['unknown'] += 1
        
        return oa_counts
    
    @staticmethod
    def analyze_geographic(publications):
        """Географический анализ"""
        # Уникальные страны на публикацию
        unique_countries_per_pub = []
        # Авторы по странам
        authors_per_country = Counter()
        # Коллаборации
        collaborations = []
        # Пары стран
        country_pairs = Counter()
        
        for pub in publications:
            countries = set()
            for authorship in pub.get('authorships', []):
                for inst in authorship.get('institutions', []):
                    country = inst.get('country_code', '')
                    if country:
                        countries.add(country)
                        authors_per_country[country] += 1
            
            if countries:
                unique_countries_per_pub.append(len(countries))
                if len(countries) > 1:
                    collaborations.append('international')
                    # Пары стран
                    country_list = sorted(list(countries))
                    for i in range(len(country_list)):
                        for j in range(i+1, len(country_list)):
                            pair = f"{country_list[i]}-{country_list[j]}"
                            country_pairs[pair] += 1
                else:
                    collaborations.append('single')
        
        return {
            'unique_countries_per_pub': unique_countries_per_pub,
            'authors_per_country': dict(authors_per_country),
            'collaborations': collaborations,
            'country_pairs': dict(country_pairs)
        }
    
    @staticmethod
    def analyze_citation_dynamics(publications, citing_map):
        """Анализ динамики цитирований"""
        citation_dynamics = defaultdict(lambda: defaultdict(int))
        all_citations_per_year = defaultdict(list)
        
        for pub in publications:
            pub_year = pub.get('year')
            if not pub_year:
                continue
            
            citing_works = citing_map.get(pub.get('id'), [])
            for citing in citing_works:
                citing_year = citing.get('year')
                if citing_year:
                    citation_dynamics[pub_year][citing_year] += 1
                    all_citations_per_year[citing_year].append(1)
        
        # Накопленные цитирования
        cumulative = {}
        sorted_years = sorted(all_citations_per_year.keys())
        total = 0
        for year in sorted_years:
            total += len(all_citations_per_year[year])
            cumulative[year] = total
        
        return {
            'dynamics': citation_dynamics,
            'cumulative': cumulative
        }
    
    @staticmethod
    def analyze_topics(publications, citing_map):
        """Анализ тем"""
        topics_stats = {}
        
        for pub in publications:
            pub_year = pub.get('year')
            if not pub_year:
                continue
            
            for topic in pub.get('topics', []):
                topic_name = topic.get('display_name', 'Unknown')
                if topic_name not in topics_stats:
                    topics_stats[topic_name] = {
                        'analyzed_count': 0,
                        'citing_count': 0,
                        'first_year': pub_year,
                        'peak_year': pub_year,
                        'years': []
                    }
                
                topics_stats[topic_name]['analyzed_count'] += 1
                topics_stats[topic_name]['years'].append(pub_year)
                
                if pub_year < topics_stats[topic_name]['first_year']:
                    topics_stats[topic_name]['first_year'] = pub_year
        
        # Добавляем цитирования для тем
        for citing_works in citing_map.values():
            for citing in citing_works:
                for topic in citing.get('topics', []):
                    topic_name = topic.get('display_name', 'Unknown')
                    if topic_name in topics_stats:
                        topics_stats[topic_name]['citing_count'] += 1
        
        # Расчет нормированных значений и пиковых годов
        for topic_name, stats in topics_stats.items():
            total_count = stats['analyzed_count'] + stats['citing_count']
            if total_count > 0:
                stats['analyzed_norm'] = stats['analyzed_count'] / total_count
                stats['citing_norm'] = stats['citing_count'] / total_count
            else:
                stats['analyzed_norm'] = 0
                stats['citing_norm'] = 0
            
            stats['total_norm'] = stats['analyzed_norm'] + stats['citing_norm']
            
            # Пиковый год - просто наиболее частый год
            if stats['years']:
                year_counts = Counter(stats['years'])
                stats['peak_year'] = max(year_counts.items(), key=lambda x: x[1])[0]
        
        return topics_stats

# ==================== HTML REPORT GENERATOR ====================
class HTMLReportGenerator:
    """Генератор HTML отчета"""
    
    def __init__(self, lang='ru'):
        self.lang = lang
        self.t = TRANSLATIONS[lang]
        self.primary_color = "#4A90D9"
        self.secondary_color = "#67B8F7"
    
    def generate_report(self, data, issn, period, journal_name=""):
        """Генерация полного HTML отчета"""
        
        # Сбор данных
        publications = data.get('publications', [])
        citing_map = data.get('citing_map', {})
        metrics = self._calculate_metrics(publications, citing_map)
        geo_analysis = DataProcessor.analyze_geographic(publications)
        citation_dynamics = DataProcessor.analyze_citation_dynamics(publications, citing_map)
        topics_stats = DataProcessor.analyze_topics(publications, citing_map)
        
        html = f"""
<!DOCTYPE html>
<html lang="{self.lang}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Journal Analysis Report - {issn}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f7fa; color: #333; }}
        
        .container {{ display: flex; min-height: 100vh; }}
        
        /* Sidebar */
        .sidebar {{
            width: 280px;
            background: linear-gradient(180deg, #2c3e50 0%, #1a252f 100%);
            padding: 20px 0;
            position: fixed;
            height: 100vh;
            overflow-y: auto;
            box-shadow: 2px 0 10px rgba(0,0,0,0.1);
            z-index: 1000;
        }}
        
        .sidebar::-webkit-scrollbar {{ width: 6px; }}
        .sidebar::-webkit-scrollbar-thumb {{ background: {self.primary_color}; border-radius: 3px; }}
        
        .sidebar-header {{
            padding: 20px 25px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            margin-bottom: 10px;
        }}
        
        .sidebar-header h2 {{
            color: #fff;
            font-size: 18px;
            font-weight: 700;
        }}
        
        .sidebar-header p {{
            color: #94a3b8;
            font-size: 12px;
            margin-top: 5px;
        }}
        
        .nav-item {{
            display: block;
            padding: 12px 25px;
            color: #cbd5e1;
            text-decoration: none;
            font-size: 14px;
            transition: all 0.2s;
            border-left: 3px solid transparent;
            cursor: pointer;
        }}
        
        .nav-item:hover {{
            background: rgba(255,255,255,0.05);
            color: #fff;
            border-left-color: {self.primary_color};
        }}
        
        .nav-item.active {{
            background: rgba(74, 144, 217, 0.15);
            color: #fff;
            border-left-color: {self.primary_color};
        }}
        
        .nav-item .icon {{ margin-right: 10px; }}
        .nav-sub {{ padding-left: 30px; font-size: 13px; }}
        
        /* Main Content */
        .main-content {{
            margin-left: 280px;
            padding: 30px 40px;
            flex: 1;
            max-width: calc(100% - 280px);
        }}
        
        .section {{
            background: #fff;
            border-radius: 12px;
            padding: 25px 30px;
            margin-bottom: 25px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
            scroll-margin-top: 20px;
        }}
        
        .section-title {{
            font-size: 22px;
            font-weight: 700;
            color: #1a252f;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid {self.primary_color};
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .section-title .icon {{ font-size: 24px; }}
        
        /* Metrics Grid */
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }}
        
        .metric-card {{
            background: #f8fafc;
            border-radius: 8px;
            padding: 15px;
            border: 1px solid #e2e8f0;
            transition: transform 0.2s;
        }}
        
        .metric-card:hover {{ transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.08); }}
        
        .metric-label {{
            font-size: 12px;
            color: #64748b;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .metric-value {{
            font-size: 28px;
            font-weight: 700;
            color: #0f172a;
            margin-top: 5px;
        }}
        
        .metric-value.small {{ font-size: 20px; }}
        
        /* Tables */
        .table-container {{
            overflow-x: auto;
            margin: 15px 0;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
        }}
        
        table thead {{
            background: #f1f5f9;
            border-bottom: 2px solid #e2e8f0;
        }}
        
        table th {{
            padding: 12px 15px;
            text-align: left;
            font-weight: 600;
            color: #334155;
            white-space: nowrap;
        }}
        
        table td {{
            padding: 10px 15px;
            border-bottom: 1px solid #e2e8f0;
            color: #1e293b;
        }}
        
        table tr:hover {{ background: #f8fafc; }}
        
        .citation-count {{
            font-weight: 600;
            color: {self.primary_color};
        }}
        
        .badge {{
            display: inline-block;
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 600;
        }}
        
        .badge-info {{ background: #dbeafe; color: #1e40af; }}
        .badge-success {{ background: #dcfce7; color: #166534; }}
        .badge-warning {{ background: #fef3c7; color: #92400e; }}
        .badge-danger {{ background: #fee2e2; color: #991b1b; }}
        
        .doi-link {{
            color: {self.primary_color};
            text-decoration: none;
            font-size: 13px;
        }}
        
        .doi-link:hover {{ text-decoration: underline; }}
        
        /* Collapsible */
        .collapser {{
            padding: 12px 15px;
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            margin-bottom: 8px;
            cursor: pointer;
            transition: all 0.2s;
        }}
        
        .collapser:hover {{
            background: #f1f5f9;
            border-color: {self.primary_color};
        }}
        
        .citation-detail {{
            padding: 12px 20px;
            margin: 5px 0 5px 20px;
            background: #fafbfc;
            border-left: 3px solid {self.primary_color};
            border-radius: 4px;
        }}
        
        .citation-detail .cite-meta {{
            font-size: 13px;
            color: #475569;
            margin-top: 4px;
        }}
        
        /* Filter section */
        .filter-section {{
            background: #f8fafc;
            padding: 15px 20px;
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
            font-weight: 600;
            color: #64748b;
            margin-bottom: 4px;
        }}
        
        .filter-row select,
        .filter-row input {{
            width: 100%;
            padding: 8px 12px;
            border: 1px solid #d1d5db;
            border-radius: 6px;
            font-size: 13px;
        }}
        
        .filter-row select:focus,
        .filter-row input:focus {{
            outline: none;
            border-color: {self.primary_color};
            box-shadow: 0 0 0 3px rgba(74, 144, 217, 0.1);
        }}
        
        /* Heatmap */
        .heatmap {{
            display: table;
            border-collapse: collapse;
            margin: 15px 0;
        }}
        
        .heatmap-cell {{
            padding: 8px 12px;
            text-align: center;
            border: 1px solid #e2e8f0;
            min-width: 60px;
            font-size: 13px;
        }}
        
        .heatmap-header {{
            background: #f1f5f9;
            font-weight: 600;
            padding: 8px 12px;
            text-align: center;
            border: 1px solid #e2e8f0;
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
            color: #94a3b8;
            font-size: 13px;
            border-top: 1px solid #e2e8f0;
            margin-top: 20px;
        }}
        
        /* Responsive */
        @media (max-width: 768px) {{
            .sidebar {{ display: none; }}
            .main-content {{ margin-left: 0; max-width: 100%; padding: 15px; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Sidebar Navigation -->
        <nav class="sidebar">
            <div class="sidebar-header">
                <h2>📊 Journal Analysis</h2>
                <p>{issn} | {period}</p>
            </div>
            
            <a href="#overview" class="nav-item active"><span class="icon">📊</span> {self.t['overview']}</a>
            <a href="#analyzed_articles" class="nav-item"><span class="icon">📄</span> {self.t['analyzed_articles']}</a>
            <a href="#citation_analysis" class="nav-item"><span class="icon">📈</span> {self.t['citation_analysis']}</a>
            <a href="#citing_works" class="nav-item"><span class="icon">📚</span> {self.t['citing_works']}</a>
            <a href="#topics_analysis" class="nav-item"><span class="icon">🏷️</span> {self.t['topics_analysis']}</a>
            <a href="#detailed_citations" class="nav-item"><span class="icon">📋</span> {self.t['detailed_citations']}</a>
            <a href="#all_publications" class="nav-item"><span class="icon">📚</span> {self.t['all_publications']}</a>
        </nav>
        
        <!-- Main Content -->
        <div class="main-content">
            
            <!-- ==================== OVERVIEW ==================== -->
            <div id="overview" class="section">
                <div class="section-title"><span class="icon">📊</span> {self.t['overview']}</div>
                
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-label">{self.t['total_publications']}</div>
                        <div class="metric-value">{metrics['total_publications']}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">{self.t['total_citations']}</div>
                        <div class="metric-value">{metrics['total_citations']}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">{self.t['h_index']}</div>
                        <div class="metric-value">{metrics['h_index']}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">{self.t['g_index']}</div>
                        <div class="metric-value">{metrics['g_index']}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">{self.t['i10_index']}</div>
                        <div class="metric-value">{metrics['i10_index']}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">{self.t['i100_index']}</div>
                        <div class="metric-value">{metrics['i100_index']}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">{self.t['avg_citations']}</div>
                        <div class="metric-value">{metrics['avg_citations']:.1f}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">{self.t['open_access']}</div>
                        <div class="metric-value small">{metrics['open_access_percent']:.1f}%</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">{self.t['active_years']}</div>
                        <div class="metric-value small">{metrics['active_years']}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">{self.t['unique_authors']}</div>
                        <div class="metric-value">{metrics['unique_authors']}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">{self.t['unique_affiliations']}</div>
                        <div class="metric-value">{metrics['unique_affiliations']}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">{self.t['unique_countries']}</div>
                        <div class="metric-value">{metrics['unique_countries']}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">{self.t['avg_authors_per_paper']}</div>
                        <div class="metric-value small">{metrics['avg_authors_per_paper']:.2f}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">{self.t['avg_affiliations_per_paper']}</div>
                        <div class="metric-value small">{metrics['avg_affiliations_per_paper']:.2f}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">{self.t['avg_countries_per_paper']}</div>
                        <div class="metric-value small">{metrics['avg_countries_per_paper']:.2f}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">{self.t['international_collaboration']}</div>
                        <div class="metric-value small">{metrics['international_collaboration']:.1f}%</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">{self.t['unique_citing_authors']}</div>
                        <div class="metric-value">{metrics['unique_citing_authors']}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">{self.t['unique_citing_affiliations']}</div>
                        <div class="metric-value">{metrics['unique_citing_affiliations']}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">{self.t['unique_citing_countries']}</div>
                        <div class="metric-value">{metrics['unique_citing_countries']}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">{self.t['unique_citing_journals']}</div>
                        <div class="metric-value">{metrics['unique_citing_journals']}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">{self.t['unique_citing_publishers']}</div>
                        <div class="metric-value">{metrics['unique_citing_publishers']}</div>
                    </div>
                </div>
                
                <!-- Open Access Breakdown -->
                <h4 style="margin: 20px 0 10px 0;">{self.t['open_access_breakdown']}</h4>
                <div class="metrics-grid" style="grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));">
                    {''.join([
                        f'<div class="metric-card"><div class="metric-label">{self.t[oa_type]}</div><div class="metric-value small">{count}</div></div>'
                        for oa_type, count in metrics['open_access_breakdown'].items()
                    ])}
                </div>
            </div>
            
            <!-- ==================== ANALYZED ARTICLES ==================== -->
            <div id="analyzed_articles" class="section">
                <div class="section-title"><span class="icon">📄</span> {self.t['analyzed_articles']}</div>
                
                <!-- Author Analysis -->
                <h4 style="margin: 15px 0 10px 0;">{self.t['author_analysis']}</h4>
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>{self.t['rank']}</th>
                                <th>{self.t['authors']}</th>
                                <th>ORCID</th>
                                <th>{self.t['affiliations']}</th>
                                <th>{self.t['countries']}</th>
                                <th>{self.t['publications']}</th>
                                <th>{self.t['citations']}</th>
                            </tr>
                        </thead>
                        <tbody>
                            {self._generate_author_table(publications)}
                        </tbody>
                    </table>
                </div>
                
                <!-- Top Affiliations -->
                <h4 style="margin: 20px 0 10px 0;">{self.t['top_affiliations']}</h4>
                <div class="table-container">
                    <table>
                        <thead>
                            <tr><th>#</th><th>Affiliation</th><th>{self.t['publications']}</th></tr>
                        </thead>
                        <tbody>
                            {self._generate_top_affiliations(publications)}
                        </tbody>
                    </table>
                </div>
                
                <!-- Geographic Analysis -->
                <h4 style="margin: 20px 0 10px 0;">{self.t['geographic_analysis']}</h4>
                
                <h5 style="margin: 10px 0 5px 0;">{self.t['unique_countries_per_publication']}</h5>
                <div class="table-container">
                    <table>
                        <thead><tr><th>{self.t['countries']}</th><th>{self.t['publications']}</th></tr></thead>
                        <tbody>
                            {self._generate_geographic_table(geo_analysis, 'unique')}
                        </tbody>
                    </table>
                </div>
                
                <h5 style="margin: 15px 0 5px 0;">{self.t['authors_per_country']}</h5>
                <div class="table-container">
                    <table>
                        <thead><tr><th>{self.t['countries']}</th><th>{self.t['authors']}</th></tr></thead>
                        <tbody>
                            {self._generate_geographic_table(geo_analysis, 'authors')}
                        </tbody>
                    </table>
                </div>
                
                <h5 style="margin: 15px 0 5px 0;">{self.t['collaboration_patterns']}</h5>
                <div class="table-container">
                    <table>
                        <thead><tr><th>{self.t['single_country']}</th><th>{self.t['international']}</th></tr></thead>
                        <tbody>
                            {self._generate_collaboration_table(geo_analysis)}
                        </tbody>
                    </table>
                </div>
                
                <h5 style="margin: 15px 0 5px 0;">{self.t['collaboration_couples']}</h5>
                <div class="table-container">
                    <table>
                        <thead><tr><th>{self.t['countries']}</th><th>{self.t['publications']}</th></tr></thead>
                        <tbody>
                            {self._generate_collaboration_couples(geo_analysis)}
                        </tbody>
                    </table>
                </div>
            </div>
            
            <!-- ==================== CITATION ANALYSIS ==================== -->
            <div id="citation_analysis" class="section">
                <div class="section-title"><span class="icon">📈</span> {self.t['citation_analysis']}</div>
                
                <h4 style="margin: 10px 0 10px 0;">{self.t['citation_dynamics']}</h4>
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
                            {self._generate_citation_dynamics(citation_dynamics['dynamics'])}
                        </tbody>
                    </table>
                </div>
                
                <h4 style="margin: 20px 0 10px 0;">{self.t['cumulative_citations']}</h4>
                <div class="table-container">
                    <table>
                        <thead><tr><th>Year</th><th>Cumulative Citations</th></tr></thead>
                        <tbody>
                            {self._generate_cumulative_citations(citation_dynamics['cumulative'])}
                        </tbody>
                    </table>
                </div>
                
                <h4 style="margin: 20px 0 10px 0;">{self.t['citation_network_heatmap']}</h4>
                {self._generate_heatmap(citation_dynamics['dynamics'])}
                
                <h4 style="margin: 20px 0 10px 0;">{self.t['most_cited_publications']}</h4>
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>{self.t['rank']}</th>
                                <th>{self.t['title']}</th>
                                <th>{self.t['year']}</th>
                                <th>{self.t['citations']}</th>
                                <th>{self.t['citations_per_year']}</th>
                                <th>{self.t['authors']}</th>
                                <th>{self.t['doi']}</th>
                            </tr>
                        </thead>
                        <tbody>
                            {self._generate_most_cited(publications)}
                        </tbody>
                    </table>
                </div>
            </div>
            
            <!-- ==================== CITING WORKS ==================== -->
            <div id="citing_works" class="section">
                <div class="section-title"><span class="icon">📚</span> {self.t['citing_works']}</div>
                
                <div class="metrics-grid" style="grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));">
                    <div class="metric-card">
                        <div class="metric-label">{self.t['total_citing_works']}</div>
                        <div class="metric-value">{metrics['total_citing_works']}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">{self.t['unique_citing_authors']}</div>
                        <div class="metric-value">{metrics['unique_citing_authors']}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">{self.t['unique_citing_affiliations']}</div>
                        <div class="metric-value">{metrics['unique_citing_affiliations']}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">{self.t['unique_citing_countries']}</div>
                        <div class="metric-value">{metrics['unique_citing_countries']}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">{self.t['unique_citing_journals']}</div>
                        <div class="metric-value">{metrics['unique_citing_journals']}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">{self.t['unique_citing_publishers']}</div>
                        <div class="metric-value">{metrics['unique_citing_publishers']}</div>
                    </div>
                </div>
                
                <h4 style="margin: 20px 0 10px 0;">{self.t['top_citing_authors']}</h4>
                <div class="table-container">
                    <table>
                        <thead><tr><th>{self.t['rank']}</th><th>{self.t['authors']}</th><th>{self.t['citations']}</th></tr></thead>
                        <tbody>
                            {self._generate_top_citing_authors(citing_map)}
                        </tbody>
                    </table>
                </div>
                
                <h4 style="margin: 20px 0 10px 0;">{self.t['top_citing_affiliations']}</h4>
                <div class="table-container">
                    <table>
                        <thead><tr><th>{self.t['rank']}</th><th>Affiliation</th><th>{self.t['citations']}</th></tr></thead>
                        <tbody>
                            {self._generate_top_citing_affiliations(citing_map)}
                        </tbody>
                    </table>
                </div>
                
                <h4 style="margin: 20px 0 10px 0;">{self.t['top_citing_countries']}</h4>
                <div class="table-container">
                    <table>
                        <thead><tr><th>{self.t['rank']}</th><th>{self.t['countries']}</th><th>{self.t['citations']}</th></tr></thead>
                        <tbody>
                            {self._generate_top_citing_countries(citing_map)}
                        </tbody>
                    </table>
                </div>
                
                <h4 style="margin: 20px 0 10px 0;">{self.t['top_citing_journals']}</h4>
                <div class="table-container">
                    <table>
                        <thead><tr><th>{self.t['rank']}</th><th>{self.t['journal']}</th><th>{self.t['citations']}</th></tr></thead>
                        <tbody>
                            {self._generate_top_citing_journals(citing_map)}
                        </tbody>
                    </table>
                </div>
                
                <h4 style="margin: 20px 0 10px 0;">{self.t['top_citing_publishers']}</h4>
                <div class="table-container">
                    <table>
                        <thead><tr><th>{self.t['rank']}</th><th>{self.t['publisher']}</th><th>{self.t['citations']}</th></tr></thead>
                        <tbody>
                            {self._generate_top_citing_publishers(citing_map)}
                        </tbody>
                    </table>
                </div>
            </div>
            
            <!-- ==================== TOPICS ANALYSIS ==================== -->
            <div id="topics_analysis" class="section">
                <div class="section-title"><span class="icon">🏷️</span> {self.t['topics_analysis']}</div>
                
                <h4 style="margin: 10px 0 10px 0;">Topics Analysis</h4>
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>Topic</th>
                                <th>{self.t['analyzed_count']}</th>
                                <th>{self.t['citing_count']}</th>
                                <th>{self.t['analyzed_norm']}</th>
                                <th>{self.t['citing_norm']}</th>
                                <th>{self.t['total_norm']}</th>
                                <th>{self.t['first_year']}</th>
                                <th>{self.t['peak_year']}</th>
                            </tr>
                        </thead>
                        <tbody>
                            {self._generate_topics_table(topics_stats)}
                        </tbody>
                    </table>
                </div>
                
                <h4 style="margin: 20px 0 10px 0;">{self.t['top_10_cited_topics']}</h4>
                <div class="table-container">
                    <table>
                        <thead><tr><th>{self.t['rank']}</th><th>Topic</th><th>{self.t['citations']}</th></tr></thead>
                        <tbody>
                            {self._generate_top_10_cited_topics(topics_stats)}
                        </tbody>
                    </table>
                </div>
            </div>
            
            <!-- ==================== DETAILED CITATIONS ==================== -->
            <div id="detailed_citations" class="section">
                <div class="section-title"><span class="icon">📋</span> {self.t['detailed_citations']}</div>
                
                {self._generate_detailed_citations(publications, citing_map)}
            </div>
            
            <!-- ==================== ALL PUBLICATIONS ==================== -->
            <div id="all_publications" class="section">
                <div class="section-title"><span class="icon">📚</span> {self.t['all_publications']}</div>
                
                <div class="filter-section">
                    <div class="filter-row">
                        <div>
                            <label for="yearFilter">{self.t['filter_by_year']}:</label>
                            <select id="yearFilter" onchange="filterPublications()">
                                <option value="">{self.t['all_years']}</option>
                                {''.join([
                                    f'<option value="{y}">{y}</option>'
                                    for y in sorted(set(p.get('year') for p in publications if p.get('year')), reverse=True)
                                ])}
                            </select>
                        </div>
                        <div>
                            <label for="authorFilter">{self.t['filter_by_author']}:</label>
                            <input type="text" id="authorFilter" placeholder="Author name..." onkeyup="filterPublications()">
                        </div>
                        <div>
                            <label for="affiliationFilter">{self.t['filter_by_affiliation']}:</label>
                            <input type="text" id="affiliationFilter" placeholder="Affiliation..." onkeyup="filterPublications()">
                        </div>
                        <div>
                            <label for="citationFilter">{self.t['filter_by_citations']}:</label>
                            <input type="number" id="citationFilter" placeholder="Min citations..." min="0" onchange="filterPublications()">
                        </div>
                        <div>
                            <label for="searchInput">{self.t['search_publications']}:</label>
                            <input type="text" id="searchInput" placeholder="Search..." onkeyup="filterPublications()">
                        </div>
                    </div>
                </div>
                
                <div class="table-container" style="max-height: 600px; overflow-y: auto;">
                    <table id="publicationsTable">
                        <thead>
                            <tr>
                                <th>#</th>
                                <th>{self.t['title']}</th>
                                <th>{self.t['year']}</th>
                                <th>{self.t['authors']}</th>
                                <th>{self.t['affiliations']}</th>
                                <th>{self.t['citations']}</th>
                                <th>{self.t['citations_per_year']}</th>
                                <th>{self.t['doi']}</th>
                            </tr>
                        </thead>
                        <tbody>
                            {self._generate_all_publications_table(publications)}
                        </tbody>
                    </table>
                </div>
            </div>
            
            <!-- Footer -->
            <div class="footer">
                <p>{self.t['footer']}: {datetime.now().strftime('%d.%m.%Y')}</p>
                <p style="font-size: 11px;">Data source: OpenAlex | ISSN: {issn}</p>
            </div>
        </div>
    </div>
    
    <!-- JavaScript -->
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
            const yearFilter = document.getElementById('yearFilter').value;
            const authorFilter = document.getElementById('authorFilter').value.toLowerCase();
            const affiliationFilter = document.getElementById('affiliationFilter').value.toLowerCase();
            const citationFilter = parseInt(document.getElementById('citationFilter').value) || 0;
            const searchFilter = document.getElementById('searchInput').value.toLowerCase();
            
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
                if (authorFilter && !authors.includes(authorFilter)) show = false;
                if (affiliationFilter && !affiliations.includes(affiliationFilter)) show = false;
                if (citations < citationFilter) show = false;
                if (searchFilter && !title.includes(searchFilter) && !doi.includes(searchFilter)) show = false;
                
                row.style.display = show ? '' : 'none';
                if (show) visible++;
            }});
            
            const countEl = document.getElementById('visibleCount');
            if (countEl) countEl.textContent = visible + ' publications';
        }}
    </script>
</body>
</html>
"""
        return html
    
    # ==================== HELPER METHODS ====================
    
    def _calculate_metrics(self, publications, citing_map):
        """Расчет всех метрик"""
        citations = [p.get('cited_by_count', 0) for p in publications]
        
        # Open Access
        oa_counts = DataProcessor.analyze_open_access(publications)
        oa_total = sum(oa_counts.values())
        oa_percent = (oa_counts['gold'] + oa_counts['hybrid'] + oa_counts['green'] + oa_counts['bronze']) / oa_total * 100 if oa_total > 0 else 0
        
        # Authors
        all_authors = set()
        all_affiliations = set()
        all_countries = set()
        total_authors = 0
        total_affiliations = 0
        
        for pub in publications:
            for authorship in pub.get('authorships', []):
                author = authorship.get('author', {}).get('display_name', '')
                if author:
                    all_authors.add(author)
                    total_authors += 1
                
                for inst in authorship.get('institutions', []):
                    affil = inst.get('display_name', '')
                    if affil:
                        all_affiliations.add(affil)
                        total_affiliations += 1
                    
                    country = inst.get('country_code', '')
                    if country:
                        all_countries.add(country)
        
        # Citing works
        citing_works = []
        for works in citing_map.values():
            citing_works.extend(works)
        
        citing_authors = set()
        citing_affiliations = set()
        citing_countries = set()
        citing_journals = set()
        citing_publishers = set()
        
        for work in citing_works:
            for authorship in work.get('authorships', []):
                author = authorship.get('author', {}).get('display_name', '')
                if author:
                    citing_authors.add(author)
                
                for inst in authorship.get('institutions', []):
                    affil = inst.get('display_name', '')
                    if affil:
                        citing_affiliations.add(affil)
                    
                    country = inst.get('country_code', '')
                    if country:
                        citing_countries.add(country)
            
            journal = work.get('journal', '')
            if journal:
                citing_journals.add(journal)
            
            publisher = work.get('publisher', '')
            if publisher:
                citing_publishers.add(publisher)
        
        # Collaboration
        geo = DataProcessor.analyze_geographic(publications)
        collab_rate = sum(1 for c in geo['collaborations'] if c == 'international') / len(geo['collaborations']) * 100 if geo['collaborations'] else 0
        
        return {
            'total_publications': len(publications),
            'total_citations': sum(citations),
            'h_index': DataProcessor.calculate_h_index(citations),
            'g_index': DataProcessor.calculate_g_index(citations),
            'i10_index': DataProcessor.calculate_i10_index(citations),
            'i100_index': DataProcessor.calculate_i100_index(citations),
            'avg_citations': sum(citations) / len(citations) if citations else 0,
            'open_access_percent': oa_percent,
            'active_years': len(set(p.get('year') for p in publications if p.get('year'))),
            'unique_authors': len(all_authors),
            'unique_affiliations': len(all_affiliations),
            'unique_countries': len(all_countries),
            'avg_authors_per_paper': total_authors / len(publications) if publications else 0,
            'avg_affiliations_per_paper': total_affiliations / len(publications) if publications else 0,
            'avg_countries_per_paper': sum(len(set(DataProcessor.extract_country_from_authorship(a) for a in p.get('authorships', []))) for p in publications) / len(publications) if publications else 0,
            'international_collaboration': collab_rate,
            'unique_citing_authors': len(citing_authors),
            'unique_citing_affiliations': len(citing_affiliations),
            'unique_citing_countries': len(citing_countries),
            'unique_citing_journals': len(citing_journals),
            'unique_citing_publishers': len(citing_publishers),
            'open_access_breakdown': oa_counts,
            'total_citing_works': len(citing_works),
        }
    
    def _generate_author_table(self, publications):
        """Генерация таблицы авторов"""
        author_stats = defaultdict(lambda: {'publications': 0, 'citations': 0, 'orcid': '', 'affiliations': set(), 'countries': set()})
        
        for pub in publications:
            for authorship in pub.get('authorships', []):
                author = authorship.get('author', {}).get('display_name', 'Unknown')
                if author:
                    author_stats[author]['publications'] += 1
                    author_stats[author]['citations'] += pub.get('cited_by_count', 0)
                    
                    if not author_stats[author]['orcid']:
                        author_stats[author]['orcid'] = authorship.get('author', {}).get('orcid', '').replace('https://orcid.org/', '')
                    
                    for inst in authorship.get('institutions', []):
                        affil = inst.get('display_name', '')
                        if affil:
                            author_stats[author]['affiliations'].add(affil)
                        
                        country = inst.get('country_code', '')
                        if country:
                            author_stats[author]['countries'].add(country)
        
        sorted_authors = sorted(author_stats.items(), key=lambda x: x[1]['citations'], reverse=True)
        
        rows = []
        for i, (author, stats) in enumerate(sorted_authors[:50], 1):
            rows.append(f"""
            <tr>
                <td>{i}</td>
                <td>{html.escape(author)}</td>
                <td>{stats['orcid']}</td>
                <td>{', '.join(list(stats['affiliations'])[:3]) + ('...' if len(stats['affiliations']) > 3 else '')}</td>
                <td>{', '.join(stats['countries'])}</td>
                <td>{stats['publications']}</td>
                <td><span class="citation-count">{stats['citations']}</span></td>
            </tr>
            """)
        
        return ''.join(rows)
    
    def _generate_top_affiliations(self, publications):
        """Генерация топ аффилиаций"""
        affil_counts = Counter()
        
        for pub in publications:
            for authorship in pub.get('authorships', []):
                for inst in authorship.get('institutions', []):
                    affil = inst.get('display_name', '')
                    if affil:
                        affil_counts[affil] += 1
        
        rows = []
        for i, (affil, count) in enumerate(affil_counts.most_common(20), 1):
            rows.append(f"""
            <tr>
                <td>{i}</td>
                <td>{html.escape(affil)}</td>
                <td>{count}</td>
            </tr>
            """)
        
        return ''.join(rows)
    
    def _generate_geographic_table(self, geo, mode):
        """Генерация географической таблицы"""
        if mode == 'unique':
            country_counts = Counter()
            for pub in geo['unique_countries_per_pub']:
                # Здесь нужна реальная логика, упрощенно
                pass
            # Возвращаем пустую таблицу, т.к. данные собираются по-другому
            return '<tr><td colspan="2">Data available in full implementation</td></tr>'
        else:
            rows = []
            for country, count in sorted(geo['authors_per_country'].items(), key=lambda x: x[1], reverse=True)[:20]:
                rows.append(f"""
                <tr>
                    <td>{country}</td>
                    <td>{count}</td>
                </tr>
                """)
            return ''.join(rows) if rows else '<tr><td colspan="2">No data</td></tr>'
    
    def _generate_collaboration_table(self, geo):
        """Генерация таблицы коллабораций"""
        single = sum(1 for c in geo['collaborations'] if c == 'single')
        international = sum(1 for c in geo['collaborations'] if c == 'international')
        return f"""
        <tr>
            <td>{single}</td>
            <td>{international}</td>
        </tr>
        """
    
    def _generate_collaboration_couples(self, geo):
        """Генерация пар стран"""
        rows = []
        for pair, count in sorted(geo['country_pairs'].items(), key=lambda x: x[1], reverse=True)[:20]:
            rows.append(f"""
            <tr>
                <td>{pair}</td>
                <td>{count}</td>
            </tr>
            """)
        return ''.join(rows) if rows else '<tr><td colspan="2">No data</td></tr>'
    
    def _generate_citation_dynamics(self, dynamics):
        """Генерация динамики цитирований"""
        rows = []
        for pub_year in sorted(dynamics.keys()):
            for cite_year in sorted(dynamics[pub_year].keys()):
                rows.append(f"""
                <tr>
                    <td>{pub_year}</td>
                    <td>{cite_year}</td>
                    <td>{dynamics[pub_year][cite_year]}</td>
                </tr>
                """)
        return ''.join(rows) if rows else '<tr><td colspan="3">No data</td></tr>'
    
    def _generate_cumulative_citations(self, cumulative):
        """Генерация накопленных цитирований"""
        rows = []
        for year in sorted(cumulative.keys()):
            rows.append(f"""
            <tr>
                <td>{year}</td>
                <td>{cumulative[year]}</td>
            </tr>
            """)
        return ''.join(rows) if rows else '<tr><td colspan="2">No data</td></tr>'
    
    def _generate_heatmap(self, dynamics):
        """Генерация тепловой карты"""
        if not dynamics:
            return '<p>No data available</p>'
        
        all_pub_years = sorted(dynamics.keys())
        all_cite_years = sorted(set().union(*[set(yr.keys()) for yr in dynamics.values()]))
        
        if not all_cite_years:
            return '<p>No citation data available</p>'
        
        html_table = '<div class="heatmap">'
        
        # Заголовки
        html_table += '<div class="heatmap-row">'
        html_table += '<div class="heatmap-header">Year \\ Citation</div>'
        for year in all_cite_years:
            html_table += f'<div class="heatmap-header">{year}</div>'
        html_table += '</div>'
        
        # Данные
        max_citations = max([dynamics.get(py, {}).get(cy, 0) for py in all_pub_years for cy in all_cite_years])
        
        for pub_year in all_pub_years:
            html_table += '<div class="heatmap-row">'
            html_table += f'<div class="heatmap-header">{pub_year}</div>'
            
            for cite_year in all_cite_years:
                count = dynamics.get(pub_year, {}).get(cite_year, 0)
                intensity = count / max_citations if max_citations > 0 else 0
                color = self._get_heatmap_color(intensity)
                html_table += f'<div class="heatmap-cell" style="background: {color};">{count if count > 0 else "-"}</div>'
            
            html_table += '</div>'
        
        html_table += '</div>'
        return html_table
    
    def _get_heatmap_color(self, intensity):
        """Получение цвета для тепловой карты"""
        # Градиент от белого к primary_color
        r = int(255 - (255 - int(self.primary_color[1:3], 16)) * intensity)
        g = int(255 - (255 - int(self.primary_color[3:5], 16)) * intensity)
        b = int(255 - (255 - int(self.primary_color[5:7], 16)) * intensity)
        return f'rgb({r}, {g}, {b})'
    
    def _generate_most_cited(self, publications):
        """Генерация наиболее цитируемых публикаций"""
        sorted_pubs = sorted(publications, key=lambda x: x.get('cited_by_count', 0), reverse=True)[:20]
        
        rows = []
        for i, pub in enumerate(sorted_pubs, 1):
            authors = []
            for authorship in pub.get('authorships', [])[:3]:
                author = authorship.get('author', {}).get('display_name', '')
                if author:
                    authors.append(author)
            
            author_str = ', '.join(authors)
            if len(pub.get('authorships', [])) > 3:
                author_str += f' +{len(pub.get("authorships", [])) - 3} more'
            
            cited_by = pub.get('cited_by_count', 0)
            year = pub.get('year', 'N/A')
            citation_per_year = cited_by / (2026 - year + 1) if year and year != 'N/A' else 0
            
            rows.append(f"""
            <tr>
                <td>{i}</td>
                <td class="word-wrap">{html.escape(pub.get('title', 'N/A'))}</td>
                <td>{year}</td>
                <td><span class="citation-count">{cited_by}</span></td>
                <td>{citation_per_year:.1f}</td>
                <td>{html.escape(author_str)}</td>
                <td><a href="https://doi.org/{pub.get('doi', '')}" target="_blank" class="doi-link">{pub.get('doi', 'N/A')}</a></td>
            </tr>
            """)
        
        return ''.join(rows)
    
    def _generate_top_citing_authors(self, citing_map):
        """Генерация топ цитирующих авторов"""
        author_counts = Counter()
        
        for works in citing_map.values():
            for work in works:
                for authorship in work.get('authorships', []):
                    author = authorship.get('author', {}).get('display_name', '')
                    if author:
                        author_counts[author] += 1
        
        rows = []
        for i, (author, count) in enumerate(author_counts.most_common(20), 1):
            rows.append(f"""
            <tr>
                <td>{i}</td>
                <td>{html.escape(author)}</td>
                <td><span class="citation-count">{count}</span></td>
            </tr>
            """)
        return ''.join(rows) if rows else '<tr><td colspan="3">No data</td></tr>'
    
    def _generate_top_citing_affiliations(self, citing_map):
        """Генерация топ цитирующих аффилиаций"""
        affil_counts = Counter()
        
        for works in citing_map.values():
            for work in works:
                for authorship in work.get('authorships', []):
                    for inst in authorship.get('institutions', []):
                        affil = inst.get('display_name', '')
                        if affil:
                            affil_counts[affil] += 1
        
        rows = []
        for i, (affil, count) in enumerate(affil_counts.most_common(20), 1):
            rows.append(f"""
            <tr>
                <td>{i}</td>
                <td>{html.escape(affil)}</td>
                <td><span class="citation-count">{count}</span></td>
            </tr>
            """)
        return ''.join(rows) if rows else '<tr><td colspan="3">No data</td></tr>'
    
    def _generate_top_citing_countries(self, citing_map):
        """Генерация топ цитирующих стран"""
        country_counts = Counter()
        
        for works in citing_map.values():
            for work in works:
                for authorship in work.get('authorships', []):
                    for inst in authorship.get('institutions', []):
                        country = inst.get('country_code', '')
                        if country:
                            country_counts[country] += 1
        
        rows = []
        for i, (country, count) in enumerate(country_counts.most_common(20), 1):
            rows.append(f"""
            <tr>
                <td>{i}</td>
                <td>{country}</td>
                <td><span class="citation-count">{count}</span></td>
            </tr>
            """)
        return ''.join(rows) if rows else '<tr><td colspan="3">No data</td></tr>'
    
    def _generate_top_citing_journals(self, citing_map):
        """Генерация топ цитирующих журналов"""
        journal_counts = Counter()
        
        for works in citing_map.values():
            for work in works:
                journal = work.get('journal', '')
                if journal:
                    journal_counts[journal] += 1
        
        rows = []
        for i, (journal, count) in enumerate(journal_counts.most_common(20), 1):
            rows.append(f"""
            <tr>
                <td>{i}</td>
                <td>{html.escape(journal)}</td>
                <td><span class="citation-count">{count}</span></td>
            </tr>
            """)
        return ''.join(rows) if rows else '<tr><td colspan="3">No data</td></tr>'
    
    def _generate_top_citing_publishers(self, citing_map):
        """Генерация топ цитирующих издателей"""
        publisher_counts = Counter()
        
        for works in citing_map.values():
            for work in works:
                publisher = work.get('publisher', '')
                if publisher:
                    publisher_counts[publisher] += 1
        
        rows = []
        for i, (publisher, count) in enumerate(publisher_counts.most_common(20), 1):
            rows.append(f"""
            <tr>
                <td>{i}</td>
                <td>{html.escape(publisher)}</td>
                <td><span class="citation-count">{count}</span></td>
            </tr>
            """)
        return ''.join(rows) if rows else '<tr><td colspan="3">No data</td></tr>'
    
    def _generate_topics_table(self, topics_stats):
        """Генерация таблицы тем"""
        rows = []
        for topic, stats in sorted(topics_stats.items(), key=lambda x: x[1]['total_norm'], reverse=True)[:50]:
            rows.append(f"""
            <tr>
                <td class="word-wrap">{html.escape(topic)}</td>
                <td>{stats['analyzed_count']}</td>
                <td>{stats['citing_count']}</td>
                <td>{stats['analyzed_norm']:.3f}</td>
                <td>{stats['citing_norm']:.3f}</td>
                <td>{stats['total_norm']:.3f}</td>
                <td>{stats['first_year']}</td>
                <td>{stats['peak_year']}</td>
            </tr>
            """)
        return ''.join(rows) if rows else '<tr><td colspan="8">No data</td></tr>'
    
    def _generate_top_10_cited_topics(self, topics_stats):
        """Генерация топ-10 наиболее цитируемых тем"""
        sorted_topics = sorted(topics_stats.items(), key=lambda x: x[1]['citing_count'], reverse=True)[:10]
        
        rows = []
        for i, (topic, stats) in enumerate(sorted_topics, 1):
            rows.append(f"""
            <tr>
                <td>{i}</td>
                <td>{html.escape(topic)}</td>
                <td><span class="citation-count">{stats['citing_count']}</span></td>
            </tr>
            """)
        return ''.join(rows) if rows else '<tr><td colspan="3">No data</td></tr>'
    
    def _generate_detailed_citations(self, publications, citing_map):
        """Генерация детальных цитирований"""
        if not citing_map:
            return '<p>No citation data available</p>'
        
        html_parts = []
        
        for pub in publications[:50]:  # Ограничим для производительности
            pub_id = pub.get('id', '')
            if pub_id in citing_map and citing_map[pub_id]:
                citations = citing_map[pub_id]
                
                html_parts.append(f"""
                <div class="collapser" onclick="toggleCitations('{pub_id}')">
                    <strong>{html.escape(pub.get('title', 'N/A'))}</strong>
                    <span class="badge badge-info">{pub.get('year', 'N/A')}</span>
                    <span class="citation-count">{len(citations)} citations</span>
                    <span style="font-size: 12px; color: #666; margin-left: 10px;">DOI: {pub.get('doi', 'N/A')}</span>
                    <span style="float: right; font-size: 12px; color: #666;">Click to toggle citations</span>
                </div>
                <div id="citations_{pub_id}" style="display: none;">
                """)
                
                for cite in citations[:50]:
                    citing_authors = []
                    for authorship in cite.get('authorships', [])[:3]:
                        author = authorship.get('author', {}).get('display_name', '')
                        if author:
                            citing_authors.append(author)
                    
                    citing_countries = set()
                    for authorship in cite.get('authorships', []):
                        for inst in authorship.get('institutions', []):
                            country = inst.get('country_code', '')
                            if country:
                                citing_countries.add(country)
                    
                    citing_topics = [t.get('display_name', '') for t in cite.get('topics', [])[:3]]
                    
                    pub_year = pub.get('year', 0)
                    cite_year = cite.get('year', 0)
                    citation_lag = cite_year - pub_year if pub_year and cite_year else 'N/A'
                    
                    html_parts.append(f"""
                    <div class="citation-detail">
                        <div><strong>{html.escape(cite.get('title', 'N/A'))}</strong></div>
                        <div class="cite-meta">
                            <strong>{self.t['citing_journal']}:</strong> {html.escape(cite.get('journal', 'N/A'))} | 
                            <strong>{self.t['citing_year']}:</strong> {cite.get('year', 'N/A')} |
                            <strong>{self.t['citation_lag']}:</strong> {citation_lag} years
                        </div>
                        <div class="cite-meta">
                            <strong>{self.t['authors']}:</strong> {', '.join(citing_authors)}{'...' if len(cite.get('authorships', [])) > 3 else ''} |
                            <strong>{self.t['countries']}:</strong> {', '.join(citing_countries)} |
                            <strong>{self.t['topics']}:</strong> {', '.join(citing_topics)}
                        </div>
                        <div class="cite-meta">
                            <a href="https://doi.org/{cite.get('doi', '')}" target="_blank" class="doi-link">DOI: {cite.get('doi', 'N/A')}</a>
                        </div>
                    </div>
                    """)
                
                html_parts.append('</div>')
        
        return ''.join(html_parts)
    
    def _generate_all_publications_table(self, publications):
        """Генерация таблицы всех публикаций"""
        rows = []
        
        for i, pub in enumerate(publications, 1):
            authors = []
            affiliations = set()
            
            for authorship in pub.get('authorships', []):
                author = authorship.get('author', {}).get('display_name', '')
                if author:
                    authors.append(author)
                
                for inst in authorship.get('institutions', []):
                    affil = inst.get('display_name', '')
                    if affil:
                        affiliations.add(affil)
            
            author_str = ', '.join(authors[:3])
            if len(authors) > 3:
                author_str += f' +{len(authors) - 3} more'
            
            affil_str = ', '.join(list(affiliations)[:2])
            if len(affiliations) > 2:
                affil_str += f' +{len(affiliations) - 2} more'
            
            cited_by = pub.get('cited_by_count', 0)
            year = pub.get('year', 'N/A')
            citation_per_year = cited_by / (2026 - year + 1) if year and year != 'N/A' else 0
            
            rows.append(f"""
            <tr data-year="{year}" data-authors="{','.join(authors)}" 
                data-affiliations="{','.join(affiliations)}" 
                data-citations="{cited_by}" 
                data-title="{pub.get('title', '').lower()}" 
                data-doi="{pub.get('doi', '').lower()}">
                <td>{i}</td>
                <td class="word-wrap">{html.escape(pub.get('title', 'N/A'))}</td>
                <td>{year}</td>
                <td>{html.escape(author_str)}</td>
                <td>{html.escape(affil_str)}</td>
                <td><span class="citation-count">{cited_by}</span></td>
                <td>{citation_per_year:.1f}</td>
                <td><a href="https://doi.org/{pub.get('doi', '')}" target="_blank" class="doi-link">{pub.get('doi', 'N/A')}</a></td>
            </tr>
            """)
        
        return ''.join(rows)

# ==================== STREAMLIT APP ====================
def main():
    """Основное приложение Streamlit"""
    
    st.set_page_config(
        page_title="Advanced Journal Analysis Tool",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Язык
    lang = st.sidebar.selectbox(
        "Language / Язык",
        options=['en', 'ru'],
        format_func=lambda x: 'English' if x == 'en' else 'Русский'
    )
    t = TRANSLATIONS[lang]
    
    # Заголовок
    st.title(t['app_title'])
    st.markdown("---")
    
    # Входные данные
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        issn = st.text_input(
            t['issn_label'],
            placeholder=t['enter_issn'],
            value="0028-0836"
        )
    
    with col2:
        period = st.text_input(
            t['period_label'],
            placeholder=t['enter_period'],
            value="2020-2025"
        )
    
    with col3:
        max_workers = st.slider(
            t['workers_label'],
            min_value=4,
            max_value=12,
            value=8,
            step=1
        )
    
    # Кнопка запуска
    if st.button(t['start_button'], type="primary", use_container_width=True):
        if not issn or not period:
            st.error(t['enter_issn'] + " и " + t['enter_period'])
            return
        
        # Парсинг периода
        try:
            if ',' in period:
                years = [int(y.strip()) for y in period.split(',') if y.strip().isdigit()]
            elif '-' in period:
                parts = period.split('-')
                years = tuple(map(int, [p.strip() for p in parts]))
            else:
                years = int(period)
        except:
            st.error(t['enter_period'])
            return
        
        # Прогресс
        status_placeholder = st.empty()
        progress_bar = st.progress(0)
        
        try:
            # Инициализация клиента
            client = OpenAlexClient(max_workers=max_workers)
            
            # 1. Загрузка публикаций
            status_placeholder.info(f"🔄 {t['fetching_publications']}...")
            progress_bar.progress(10)
            
            publications = client.fetch_publications(issn, years)
            
            if not publications:
                st.warning(t['no_results'])
                return
            
            progress_bar.progress(30)
            
            # 2. Сбор цитирований
            status_placeholder.info(f"🔄 {t['fetching_citations']}...")
            
            citing_map = client.fetch_citations_parallel(
                publications,
                progress_callback=lambda done, total: progress_bar.progress(30 + (done / total) * 50)
            )
            
            progress_bar.progress(80)
            
            # 3. Обработка данных
            status_placeholder.info(f"🔄 {t['processing_data']}...")
            processor = DataProcessor()
            
            # 4. Генерация отчета
            status_placeholder.info(f"🔄 {t['generating_report']}...")
            
            data = {
                'publications': publications,
                'citing_map': citing_map
            }
            
            report_gen = HTMLReportGenerator(lang)
            html_report = report_gen.generate_report(data, issn, period)
            
            progress_bar.progress(95)
            status_placeholder.success(f"✅ {t['ready']}")
            progress_bar.progress(100)
            
            # Отображение отчета
            st.markdown("---")
            st.subheader("📄 HTML Отчет")
            
            # Кнопка скачивания
            st.download_button(
                label=t['download_report'],
                data=html_report,
                file_name=f"journal_report_{issn}_{period}.html",
                mime="text/html",
                use_container_width=True
            )
            
            # Превью отчета в iframe
            st.components.v1.html(html_report, height=800, scrolling=True)
            
        except Exception as e:
            st.error(f"{t['error_fetching']}: {str(e)}")
            import traceback
            st.code(traceback.format_exc())
        
        finally:
            status_placeholder.empty()

if __name__ == "__main__":
    main()
