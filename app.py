"""
app.py - Journal Metrics Analyzer
Comprehensive analysis of journal publications and their citations
Enhanced with OpenAlex API, parallel processing, and interactive HTML reports
"""

import streamlit as st
import pandas as pd
import requests
import json
import time
import random
import re
import math
import html
import base64
import os
from datetime import datetime
from collections import Counter, defaultdict
from typing import Dict, List, Tuple, Optional, Set, Any
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import hashlib
import difflib
from itertools import combinations
import colorsys


# ======================== COLOR UTILITIES FOR DYNAMIC THEMES ========================
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
        
        .publication-card {{
            background: white;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 15px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.08);
            border-left: 4px solid var(--primary);
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        
        .publication-card:hover {{
            transform: translateX(5px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.12);
        }}
        
        .publication-title {{
            font-size: 16px;
            font-weight: 600;
            color: var(--primary);
            margin-bottom: 8px;
        }}
        
        .publication-meta {{
            font-size: 13px;
            color: #555;
            margin-bottom: 5px;
        }}
        
        .publication-doi {{
            font-size: 12px;
            color: #666;
            font-family: monospace;
        }}
        
        .citation-detail {{
            background: #f8f9fa;
            border-radius: 8px;
            padding: 12px;
            margin: 8px 0 8px 20px;
            border-left: 3px solid #ddd;
            transition: background 0.2s;
        }}
        
        .citation-detail:hover {{
            background: #f0f0f0;
        }}
        
        .citation-title {{
            font-weight: 500;
            margin-bottom: 5px;
        }}
        
        .cite-meta {{
            font-size: 12px;
            color: #666;
            margin-top: 3px;
        }}
        
        .toggle-button {{
            display: inline-block;
            padding: 4px 12px;
            border: none;
            border-radius: 4px;
            background: var(--primary);
            color: white;
            cursor: pointer;
            font-size: 12px;
            transition: background 0.2s;
        }}
        
        .toggle-button:hover {{
            background: var(--secondary);
        }}
        
        .filter-section {{
            background: #f8f9fa;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 20px;
        }}
        
        .filter-row {{
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
            align-items: center;
        }}
        
        .filter-row label {{
            font-weight: 500;
            font-size: 13px;
            margin-right: 5px;
        }}
        
        .filter-row select, .filter-row input {{
            padding: 6px 10px;
            border: 1px solid #ddd;
            border-radius: 6px;
            font-size: 13px;
        }}
        
        .filter-row select:focus, .filter-row input:focus {{
            border-color: var(--primary);
            outline: none;
            box-shadow: 0 0 0 2px var(--hover-light);
        }}
        
        .citation-count {{
            font-weight: 600;
            color: var(--primary);
        }}
        
        .word-wrap {{
            word-wrap: break-word;
            max-width: 300px;
        }}
        
        .collapser {{
            cursor: pointer;
            padding: 10px 15px;
            background: #f8f9fa;
            border-radius: 8px;
            margin-bottom: 5px;
            transition: background 0.2s;
            border-left: 3px solid var(--primary);
        }}
        
        .collapser:hover {{
            background: #f0f0f0;
        }}
        
        .doi-link {{
            color: var(--primary);
            text-decoration: none;
            font-family: monospace;
            font-size: 12px;
        }}
        
        .doi-link:hover {{
            color: var(--secondary);
            text-decoration: underline;
        }}
        
        .badge-oa-gold {{
            background: #ffd700;
            color: #000;
            padding: 2px 10px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 600;
        }}
        
        .badge-oa-hybrid {{
            background: #ff8c00;
            color: #fff;
            padding: 2px 10px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 600;
        }}
        
        .badge-oa-green {{
            background: #2e8b57;
            color: #fff;
            padding: 2px 10px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 600;
        }}
        
        .badge-oa-bronze {{
            background: #cd7f32;
            color: #fff;
            padding: 2px 10px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 600;
        }}
        
        .badge-oa-closed {{
            background: #6c757d;
            color: #fff;
            padding: 2px 10px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 600;
        }}
    </style>
    """
    st.markdown(theme_css, unsafe_allow_html=True)

# ======================== ЛОКАЛИЗАЦИЯ ========================
TEXTS = {
    'en': {
        # App
        'app_title': "Journal Metrics Analyzer",
        'app_subtitle': "Comprehensive analysis of journal publications and their citations",
        'settings': "⚙️ Settings",
        'language': "🌐 Language",
        'language_english': "English",
        'language_russian': "Russian",
        
        # Input
        'issn_label': "📰 ISSN",
        'issn_placeholder': "0028-0836",
        'period_label': "📅 Period",
        'period_placeholder': "2020-2023 or 2025 or 2020,2021,2022",
        'period_help': "Single year (2025), range (2020-2023), or comma-separated (2020,2021,2022)",
        'workers_label': "⚡ Parallel Workers",
        'workers_help': "Number of parallel API requests (4-12 recommended)",
        'start_analysis': "🚀 Start Analysis",
        
        # Progress
        'collecting_publications': "📚 Collecting journal publications...",
        'found_publications': "✅ Found {0} publications",
        'collecting_citations': "🔍 Collecting citations for {0} publications...",
        'collecting_citation_metadata': "📊 Collecting citation metadata...",
        'analyzing_data': "📈 Analyzing data...",
        'analysis_complete': "✅ Analysis complete!",
        'generating_report': "📄 Generating HTML report...",
        
        # Overview
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
        'avg_authors_per_paper': "Avg Authors/Paper",
        'avg_affiliations_per_paper': "Avg Affiliations/Paper",
        'avg_countries_per_paper': "Avg Countries/Paper",
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
        'most_cited_publications': "Most Cited Publications",
        'rank': "Rank",
        'title': "Title",
        'year': "Year",
        'citations': "Citations",
        'citations_per_year': "Citations/Year",
        'authors': "Authors",
        'doi': "DOI",
        
        # Author Analysis
        'author_analysis': "Author Analysis",
        'top_authors': "Top Authors",
        'orcid': "ORCID",
        'affiliations': "Affiliations",
        'countries': "Countries",
        'publication_count': "Publications",
        'citation_count': "Citations",
        'affiliation_analysis': "Affiliation Analysis",
        'top_affiliations': "Top Affiliations",
        'geographic_analysis': "Geographic Analysis",
        'geography_type_1': "Unique Countries per Publication (Collaboration Level)",
        'geography_type_1_desc': "Each publication counted once per unique country",
        'geography_type_2': "Authors per Country (Individual Distribution)",
        'geography_type_2_desc': "Each author counted separately",
        'geography_type_3': "Collaboration Patterns",
        'geography_type_3_desc': "Distribution of single-country vs international collaborations",
        'single_country': "Single Country",
        'international_collab': "International Collaboration",
        'collaboration_couples': "Collaboration Couples",
        'collaboration_couples_desc': "Frequency of country pairs collaborating",
        'collaboration_by_year': "Collaboration Dynamics by Year",
        
        # Citation Analysis
        'citation_analysis': "Citation Analysis",
        'citation_dynamics': "Citation Dynamics by Year",
        'cumulative_citations': "Cumulative Citations",
        'citation_network': "Citation Network Heatmap",
        'publication_year': "Publication Year",
        'citation_year': "Citation Year",
        'citations_count': "Citations Count",
        
        # Citing Works
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
        'topics': "Topics",
        'fields': "Fields",
        'subfields': "Subfields",
        'domains': "Domains",
        'concepts': "Concepts",
        'analyzed_count': "Analyzed Count",
        'citing_count': "Citing Count",
        'analyzed_norm_count': "Analyzed Norm Count",
        'citing_norm_count': "Citing Norm Count",
        'total_norm_count': "Total Norm Count",
        'first_year': "First Year",
        'peak_year': "Peak Year",
        'recent_5_years_count': "Recent 5 Years Count",
        
        # Detailed Citations
        'detailed_citations': "Detailed Citations",
        'show_citations': "Show Citations",
        'citing_journal': "Citing Journal",
        'citing_year': "Citing Year",
        'citing_date': "Citing Date",
        'citation_lag': "Citation Lag (years)",
        'citing_authors': "Citing Authors",
        'citing_countries': "Citing Countries",
        'citing_topics': "Citing Topics",
        
        # All Publications
        'all_publications': "All Publications",
        'filter_by_year': "Filter by Year",
        'filter_by_author': "Filter by Author",
        'filter_by_citations': "Filter by Citations (min)",
        'search_publications': "Search Publications",
        'search_placeholder': "Search title or DOI...",
        'showing_publications': "Showing {0} publications",
        'all_years': "All Years",
        'show_citations_short': "Citations",
        
        # Citation Velocity
        'citation_velocity': "Citation Velocity",
        'velocity_very_high': "Very High (≥10 cit/year)",
        'velocity_high': "High (5-9 cit/year)",
        'velocity_medium': "Medium (1-4 cit/year)",
        'velocity_low': "Low (<1 cit/year)",
        
        # Export
        'export_report': "📄 Export Report",
        'download_html': "💾 Download HTML Report",
        'text_export': "📋 Text Export",
        'copy_to_clipboard': "📋 Copy to Clipboard",
        'copied': "✅ Data copied! (use Ctrl+C)",
        'run_analysis_first': "👈 Please run analysis first",
        
        # HTML Report
        'html_generated': "Generated",
        'html_copyright': "© Journal Metrics Analyzer / Created by daM / Chimica Techno Acta",
        'html_footer': "Journal Metrics Analyzer v2.0",
        'html_rank': "Rank",
        'html_count': "Count",
        'html_percentage': "Percentage",
        'html_frequency': "Frequency",
        'html_connections': "connections",
        'html_joint_works': "joint works",
        'html_citations_label': "citations",
        'html_not_found': "Not found",
        
        # Navigation
        'navigation': "Navigation",
        'nav_overview': "Overview",
        'nav_most_cited': "Most Cited",
        'nav_authors': "Authors",
        'nav_citation_analysis': "Citation Analysis",
        'nav_citing_works': "Citing Works",
        'nav_topics': "Topics",
        'nav_detailed_citations': "Detailed Citations",
        'nav_all_publications': "All Publications",
    },
    'ru': {
        # App
        'app_title': "Анализатор метрик журнала",
        'app_subtitle': "Комплексный анализ публикаций журнала и их цитирований",
        'settings': "⚙️ Настройки",
        'language': "🌐 Язык",
        'language_english': "Английский",
        'language_russian': "Русский",
        
        # Input
        'issn_label': "📰 ISSN",
        'issn_placeholder': "0028-0836",
        'period_label': "📅 Период",
        'period_placeholder': "2020-2023 или 2025 или 2020,2021,2022",
        'period_help': "Одиночный год (2025), диапазон (2020-2023) или список через запятую (2020,2021,2022)",
        'workers_label': "⚡ Параллельных потоков",
        'workers_help': "Количество параллельных API запросов (рекомендуется 4-12)",
        'start_analysis': "🚀 Запустить анализ",
        
        # Progress
        'collecting_publications': "📚 Сбор публикаций журнала...",
        'found_publications': "✅ Найдено {0} публикаций",
        'collecting_citations': "🔍 Сбор цитирований для {0} публикаций...",
        'collecting_citation_metadata': "📊 Сбор метаданных цитирований...",
        'analyzing_data': "📈 Анализ данных...",
        'analysis_complete': "✅ Анализ завершен!",
        'generating_report': "📄 Генерация HTML отчета...",
        
        # Overview
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
        'avg_authors_per_paper': "Среднее авторов/статья",
        'avg_affiliations_per_paper': "Среднее аффилиаций/статья",
        'avg_countries_per_paper': "Среднее стран/статья",
        'international_collaboration_rate': "Доля международных коллабораций",
        
        # Open Access Breakdown
        'open_access_breakdown': "Распределение по типам доступа",
        'gold': "Золотой",
        'hybrid': "Гибридный",
        'green': "Зеленый",
        'bronze': "Бронзовый",
        'closed': "Закрытый",
        'unknown': "Неизвестный",
        
        # Most Cited
        'most_cited_publications': "Самые цитируемые публикации",
        'rank': "Ранг",
        'title': "Название",
        'year': "Год",
        'citations': "Цитирований",
        'citations_per_year': "Цитирований/год",
        'authors': "Авторы",
        'doi': "DOI",
        
        # Author Analysis
        'author_analysis': "Анализ авторов",
        'top_authors': "Топ авторов",
        'orcid': "ORCID",
        'affiliations': "Аффилиации",
        'countries': "Страны",
        'publication_count': "Публикаций",
        'citation_count': "Цитирований",
        'affiliation_analysis': "Анализ аффилиаций",
        'top_affiliations': "Топ аффилиаций",
        'geographic_analysis': "Географический анализ",
        'geography_type_1': "Уникальные страны по публикации (уровень коллаборации)",
        'geography_type_1_desc': "Каждая публикация учитывается один раз на уникальную страну",
        'geography_type_2': "Авторы по странам (индивидуальное распределение)",
        'geography_type_2_desc': "Каждый автор учитывается отдельно",
        'geography_type_3': "Паттерны коллабораций",
        'geography_type_3_desc': "Распределение внутристрановых и международных коллабораций",
        'single_country': "Одна страна",
        'international_collab': "Международная коллаборация",
        'collaboration_couples': "Пары коллабораций",
        'collaboration_couples_desc': "Частота взаимодействия между парами стран",
        'collaboration_by_year': "Динамика коллабораций по годам",
        
        # Citation Analysis
        'citation_analysis': "Анализ цитирований",
        'citation_dynamics': "Динамика цитирований по годам",
        'cumulative_citations': "Кумулятивное цитирование",
        'citation_network': "Тепловая карта сети цитирований",
        'publication_year': "Год публикации",
        'citation_year': "Год цитирования",
        'citations_count': "Количество цитирований",
        
        # Citing Works
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
        'topics': "Темы",
        'fields': "Области",
        'subfields': "Подобласти",
        'domains': "Домены",
        'concepts': "Концепции",
        'analyzed_count': "Кол-во в анализируемых",
        'citing_count': "Кол-во в цитирующих",
        'analyzed_norm_count': "Норм. кол-во в анализируемых",
        'citing_norm_count': "Норм. кол-во в цитирующих",
        'total_norm_count': "Общее норм. кол-во",
        'first_year': "Первый год",
        'peak_year': "Пиковый год",
        'recent_5_years_count': "Кол-во за последние 5 лет",
        
        # Detailed Citations
        'detailed_citations': "Детальные цитирования",
        'show_citations': "Показать цитирования",
        'citing_journal': "Цитирующий журнал",
        'citing_year': "Год цитирования",
        'citing_date': "Дата цитирования",
        'citation_lag': "Задержка цитирования (лет)",
        'citing_authors': "Цитирующие авторы",
        'citing_countries': "Цитирующие страны",
        'citing_topics': "Цитирующие темы",
        
        # All Publications
        'all_publications': "Все публикации",
        'filter_by_year': "Фильтр по году",
        'filter_by_author': "Фильтр по автору",
        'filter_by_citations': "Фильтр по цитированиям (мин)",
        'search_publications': "Поиск публикаций",
        'search_placeholder': "Поиск по названию или DOI...",
        'showing_publications': "Показано {0} публикаций",
        'all_years': "Все годы",
        'show_citations_short': "Цитирования",
        
        # Citation Velocity
        'citation_velocity': "Скорость цитирования",
        'velocity_very_high': "Очень высокая (≥10 цит/год)",
        'velocity_high': "Высокая (5-9 цит/год)",
        'velocity_medium': "Средняя (1-4 цит/год)",
        'velocity_low': "Низкая (<1 цит/год)",
        
        # Export
        'export_report': "📄 Экспорт отчета",
        'download_html': "💾 Скачать HTML отчет",
        'text_export': "📋 Текстовый экспорт",
        'copy_to_clipboard': "📋 Копировать в буфер",
        'copied': "✅ Данные скопированы! (используйте Ctrl+C)",
        'run_analysis_first': "👈 Сначала запустите анализ",
        
        # HTML Report
        'html_generated': "Сгенерирован",
        'html_copyright': "© Journal Metrics Analyzer / Created by daM / Chimica Techno Acta",
        'html_footer': "Journal Metrics Analyzer v2.0",
        'html_rank': "Ранг",
        'html_count': "Количество",
        'html_percentage': "Процент",
        'html_frequency': "Частота",
        'html_connections': "связей",
        'html_joint_works': "совместных работ",
        'html_citations_label': "цитирований",
        'html_not_found': "Не найден",
        
        # Navigation
        'navigation': "Навигация",
        'nav_overview': "Обзор",
        'nav_most_cited': "Самые цитируемые",
        'nav_authors': "Авторы",
        'nav_citation_analysis': "Анализ цитирований",
        'nav_citing_works': "Цитирующие работы",
        'nav_topics': "Темы",
        'nav_detailed_citations': "Детальные цитирования",
        'nav_all_publications': "Все публикации",
    }
}

def get_text(key: str) -> str:
    """Get localized text by key"""
    lang = st.session_state.get('language', 'en')
    return TEXTS[lang].get(key, TEXTS['en'].get(key, key))

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

# ======================== API CLIENT ========================

class OpenAlexClient:
    """OpenAlex API client with parallel processing and rate limiting"""
    
    def __init__(self, max_workers: int = 8):
        self.max_workers = max_workers
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'JournalMetricsAnalyzer/2.0 (mailto:analyzer@example.com)',
            'Accept': 'application/json'
        })
        self.lock = Lock()
        self.base_delay = 0.35
        self.max_retries = 4
    
    def _normalize_issn(self, issn_str: str) -> str:
        """Normalize ISSN to OpenAlex format"""
        cleaned = re.sub(r'[^0-9Xx]', '', str(issn_str).strip())
        if len(cleaned) == 8:
            return f"{cleaned[:4]}-{cleaned[4:]}".upper()
        return cleaned.upper()
    
    @retry(stop=stop_after_attempt(4), wait=wait_exponential(multiplier=1, min=1, max=10), retry=retry_if_exception_type(Exception))
    def _smart_get(self, url: str, params: Dict) -> Optional[Dict]:
        """Smart GET with rate limiting and retry logic"""
        for attempt in range(self.max_retries):
            try:
                with self.lock:
                    time.sleep(random.uniform(0.1, self.base_delay))
                
                response = self.session.get(url, params=params, timeout=25)
                
                if response.status_code == 429:
                    wait = int(response.headers.get("Retry-After", 2 ** attempt + 1))
                    time.sleep(wait + random.uniform(0.5, 1.5))
                    continue
                
                if response.status_code == 200:
                    return response.json()
                
                if response.status_code >= 500:
                    time.sleep(1 * (2 ** attempt))
                    continue
                
                return None
                
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
                time.sleep(1.5 * (2 ** attempt))
                continue
            except Exception:
                time.sleep(1.5 * (2 ** attempt))
                continue
        
        return None
    
    def get_publications(self, issn: str, years, progress_callback=None) -> List[Publication]:
        """
        Get all publications from a journal for given years
        
        Args:
            issn: ISSN of the journal
            years: int (single year), list (multiple years), tuple (range)
            progress_callback: function to update progress
        
        Returns:
            List of Publication objects
        """
        normalized = self._normalize_issn(issn)
        
        # Parse years filter
        if isinstance(years, list):
            year_filter = "|".join(f"publication_year:{y}" for y in years)
        elif isinstance(years, tuple) and len(years) == 2:
            year_filter = f"publication_year:{years[0]}-{years[1]}"
        else:
            year_filter = f"publication_year:{years}"
        
        publications = []
        cursor = "*"
        base_url = "https://api.openalex.org/works"
        
        while True:
            data = self._smart_get(base_url, {
                "filter": f"primary_location.source.issn:{normalized},{year_filter}",
                "per_page": 200,
                "select": "id,doi,title,publication_year,cited_by_count,authorships,primary_location,open_access,topics,concepts",
                "cursor": cursor
            })
            
            if not data or not data.get("results"):
                break
            
            for work in data["results"]:
                pub = self._parse_publication(work)
                publications.append(pub)
            
            if progress_callback:
                progress_callback(len(publications))
            
            cursor = data.get("meta", {}).get("next_cursor")
            if not cursor:
                break
        
        return publications
    
    def _parse_publication(self, work: Dict) -> Publication:
        """Parse OpenAlex work data into Publication object"""
        # Extract DOI
        doi = work.get("doi", "")
        if doi:
            doi = doi.replace("https://doi.org/", "")
        
        # Extract title
        title = work.get("title", "")
        
        # Extract year
        year = work.get("publication_year")
        
        # Extract citations
        cited_by_count = work.get("cited_by_count", 0)
        
        # Extract authors
        authors = []
        for authorship in work.get("authorships", []):
            author_data = authorship.get("author", {})
            author_name = author_data.get("display_name", "")
            if not author_name:
                continue
            
            orcid = author_data.get("orcid", "")
            
            # Extract affiliations and countries
            affiliations = []
            countries = []
            for inst in authorship.get("institutions", []):
                aff_name = inst.get("display_name", "")
                if aff_name:
                    affiliations.append(aff_name)
                
                country_code = inst.get("country_code", "")
                if country_code and country_code != "XX":
                    country_names = {
                        'US': 'USA', 'GB': 'UK', 'CN': 'China', 'DE': 'Germany',
                        'FR': 'France', 'JP': 'Japan', 'CA': 'Canada', 'AU': 'Australia',
                        'RU': 'Russia', 'IN': 'India', 'BR': 'Brazil', 'IT': 'Italy',
                        'ES': 'Spain', 'KR': 'South Korea', 'NL': 'Netherlands',
                        'CH': 'Switzerland', 'SE': 'Sweden', 'BE': 'Belgium',
                        'NO': 'Norway', 'DK': 'Denmark', 'FI': 'Finland', 'PL': 'Poland',
                        'PT': 'Portugal', 'GR': 'Greece', 'TR': 'Turkey', 'IL': 'Israel',
                        'SG': 'Singapore', 'TW': 'Taiwan', 'HK': 'Hong Kong',
                        'MX': 'Mexico', 'AR': 'Argentina', 'BR': 'Brazil', 'CL': 'Chile',
                        'CO': 'Colombia', 'UA': 'Ukraine', 'CZ': 'Czech Republic',
                        'HU': 'Hungary', 'RO': 'Romania', 'BG': 'Bulgaria', 'RS': 'Serbia',
                        'HR': 'Croatia', 'SK': 'Slovakia', 'SI': 'Slovenia', 'LT': 'Lithuania',
                        'LV': 'Latvia', 'EE': 'Estonia', 'IE': 'Ireland', 'NZ': 'New Zealand',
                        'ZA': 'South Africa', 'EG': 'Egypt', 'SA': 'Saudi Arabia',
                        'AE': 'United Arab Emirates', 'QA': 'Qatar', 'IR': 'Iran',
                        'PK': 'Pakistan', 'BD': 'Bangladesh', 'VN': 'Vietnam',
                        'TH': 'Thailand', 'MY': 'Malaysia', 'ID': 'Indonesia',
                        'PH': 'Philippines', 'KZ': 'Kazakhstan', 'BY': 'Belarus',
                        'UZ': 'Uzbekistan', 'AZ': 'Azerbaijan', 'GE': 'Georgia',
                        'AM': 'Armenia', 'MD': 'Moldova', 'KG': 'Kyrgyzstan',
                        'TJ': 'Tajikistan', 'TM': 'Turkmenistan', 'MN': 'Mongolia'
                    }
                    country = country_names.get(country_code, country_code)
                    if country:
                        countries.append(country)
            
            author = Author(
                display_name=author_name,
                orcid=orcid,
                affiliations=affiliations,
                countries=countries,
                raw_data=authorship
            )
            authors.append(author)
        
        # Extract journal name
        journal_name = ""
        primary_location = work.get("primary_location", {})
        if primary_location:
            source = primary_location.get("source", {})
            if source:
                journal_name = source.get("display_name", "")
        
        # Extract publisher
        publisher = ""
        if primary_location:
            source = primary_location.get("source", {})
            if source:
                publisher = source.get("publisher", "")
        
        # Extract open access status
        open_access = work.get("open_access", {})
        open_access_status = open_access.get("oa_status", "")
        is_open_access = open_access.get("is_oa", False)
        
        # Extract topics
        topics = []
        for topic_data in work.get("topics", []):
            topic = Topic(
                display_name=topic_data.get("display_name", ""),
                score=topic_data.get("score", 0.0),
                id=topic_data.get("id", ""),
                type="topic"
            )
            topics.append(topic)
        
        # Extract concepts
        concepts = []
        for concept_data in work.get("concepts", []):
            concept = Topic(
                display_name=concept_data.get("display_name", ""),
                score=concept_data.get("score", 0.0),
                id=concept_data.get("id", ""),
                type="concept"
            )
            concepts.append(concept)
        
        # Calculate citations per year
        citations_per_year = 0
        if year and cited_by_count > 0:
            age = datetime.now().year - year
            if age > 0:
                citations_per_year = cited_by_count / age
            else:
                citations_per_year = cited_by_count
        
        return Publication(
            id=work.get("id", ""),
            doi=doi,
            title=title,
            publication_year=year or 0,
            cited_by_count=cited_by_count,
            citations_per_year=citations_per_year,
            authors=authors,
            journal_name=journal_name,
            publisher=publisher,
            open_access_status=open_access_status,
            is_open_access=is_open_access,
            topics=topics,
            concepts=concepts,
            raw_data=work
        )
    
    def get_citing_works(self, publication: Publication, progress_callback=None) -> List[CitingWork]:
        """
        Get all citing works for a publication
        
        Args:
            publication: Publication object
            progress_callback: function to update progress
        
        Returns:
            List of CitingWork objects
        """
        citing_works = []
        cursor = "*"
        base_url = "https://api.openalex.org/works"
        
        # Get OpenAlex ID
        oa_id = publication.id
        if not oa_id:
            return citing_works
        
        while True:
            data = self._smart_get(base_url, {
                "filter": f"cites:{oa_id}",
                "per_page": 200,
                "select": "id,doi,title,publication_year,publication_date,authorships,primary_location,open_access,topics,concepts",
                "cursor": cursor
            })
            
            if not data or not data.get("results"):
                break
            
            for work in data["results"]:
                citing = self._parse_citing_work(work, publication)
                citing_works.append(citing)
            
            if progress_callback:
                progress_callback(len(citing_works))
            
            cursor = data.get("meta", {}).get("next_cursor")
            if not cursor:
                break
        
        return citing_works
    
    def _parse_citing_work(self, work: Dict, original_pub: Publication) -> CitingWork:
        """Parse OpenAlex work data into CitingWork object"""
        # Extract DOI
        doi = work.get("doi", "")
        if doi:
            doi = doi.replace("https://doi.org/", "")
        
        # Extract title
        title = work.get("title", "")
        
        # Extract year
        year = work.get("publication_year", 0)
        
        # Extract date
        date = work.get("publication_date", "")
        
        # Extract authors
        authors = []
        countries = []
        affiliations = []
        
        for authorship in work.get("authorships", []):
            author_data = authorship.get("author", {})
            author_name = author_data.get("display_name", "")
            if not author_name:
                continue
            
            orcid = author_data.get("orcid", "")
            
            # Extract affiliations and countries
            affs = []
            cnts = []
            for inst in authorship.get("institutions", []):
                aff_name = inst.get("display_name", "")
                if aff_name:
                    affs.append(aff_name)
                    affiliations.append(aff_name)
                
                country_code = inst.get("country_code", "")
                if country_code and country_code != "XX":
                    country_names = {
                        'US': 'USA', 'GB': 'UK', 'CN': 'China', 'DE': 'Germany',
                        'FR': 'France', 'JP': 'Japan', 'CA': 'Canada', 'AU': 'Australia',
                        'RU': 'Russia', 'IN': 'India', 'BR': 'Brazil', 'IT': 'Italy',
                        'ES': 'Spain', 'KR': 'South Korea', 'NL': 'Netherlands',
                        'CH': 'Switzerland', 'SE': 'Sweden', 'BE': 'Belgium',
                        'NO': 'Norway', 'DK': 'Denmark', 'FI': 'Finland', 'PL': 'Poland',
                        'PT': 'Portugal', 'GR': 'Greece', 'TR': 'Turkey', 'IL': 'Israel',
                        'SG': 'Singapore', 'TW': 'Taiwan', 'HK': 'Hong Kong',
                        'MX': 'Mexico', 'AR': 'Argentina', 'BR': 'Brazil', 'CL': 'Chile',
                        'CO': 'Colombia', 'UA': 'Ukraine', 'CZ': 'Czech Republic',
                        'HU': 'Hungary', 'RO': 'Romania', 'BG': 'Bulgaria', 'RS': 'Serbia',
                        'HR': 'Croatia', 'SK': 'Slovakia', 'SI': 'Slovenia', 'LT': 'Lithuania',
                        'LV': 'Latvia', 'EE': 'Estonia', 'IE': 'Ireland', 'NZ': 'New Zealand',
                        'ZA': 'South Africa', 'EG': 'Egypt', 'SA': 'Saudi Arabia',
                        'AE': 'United Arab Emirates', 'QA': 'Qatar', 'IR': 'Iran',
                        'PK': 'Pakistan', 'BD': 'Bangladesh', 'VN': 'Vietnam',
                        'TH': 'Thailand', 'MY': 'Malaysia', 'ID': 'Indonesia',
                        'PH': 'Philippines', 'KZ': 'Kazakhstan', 'BY': 'Belarus',
                        'UZ': 'Uzbekistan', 'AZ': 'Azerbaijan', 'GE': 'Georgia',
                        'AM': 'Armenia', 'MD': 'Moldova', 'KG': 'Kyrgyzstan',
                        'TJ': 'Tajikistan', 'TM': 'Turkmenistan', 'MN': 'Mongolia'
                    }
                    country = country_names.get(country_code, country_code)
                    if country:
                        cnts.append(country)
                        countries.append(country)
            
            author = Author(
                display_name=author_name,
                orcid=orcid,
                affiliations=affs,
                countries=cnts,
                raw_data=authorship
            )
            authors.append(author)
        
        # Extract journal name
        journal_name = ""
        primary_location = work.get("primary_location", {})
        if primary_location:
            source = primary_location.get("source", {})
            if source:
                journal_name = source.get("display_name", "")
        
        # Extract publisher
        publisher = ""
        if primary_location:
            source = primary_location.get("source", {})
            if source:
                publisher = source.get("publisher", "")
        
        # Extract open access status
        open_access = work.get("open_access", {})
        open_access_status = open_access.get("oa_status", "")
        
        # Extract topics
        topics = []
        for topic_data in work.get("topics", []):
            topic = Topic(
                display_name=topic_data.get("display_name", ""),
                score=topic_data.get("score", 0.0),
                id=topic_data.get("id", ""),
                type="topic"
            )
            topics.append(topic)
        
        # Calculate citation lag
        citation_lag = 0
        if year and original_pub.publication_year:
            citation_lag = year - original_pub.publication_year
        
        return CitingWork(
            citing_title=title,
            citing_year=year,
            citing_date=date,
            citing_journal=journal_name,
            citing_publisher=publisher,
            citing_doi=doi,
            citing_authors=authors,
            citing_countries=list(set(countries)),
            citing_affiliations=list(set(affiliations)),
            citing_topics=topics,
            citing_open_access_status=open_access_status,
            citation_lag=citation_lag
        )

# ======================== METRICS ENGINE ========================

class MetricsEngine:
    """Calculate all metrics for journal analysis"""
    
    def __init__(self, data: JournalData):
        self.data = data
        self.publications = data.publications
        self.citations = data.citations
        self.citing_works = data.citing_works
    
    def calculate_overview(self) -> Dict:
        """Calculate overview metrics"""
        total_pubs = len(self.publications)
        total_cites = sum(p.cited_by_count for p in self.publications)
        
        # Calculate h-index
        citations_sorted = sorted([p.cited_by_count for p in self.publications], reverse=True)
        h_index = 0
        for i, c in enumerate(citations_sorted, 1):
            if c >= i:
                h_index = i
            else:
                break
        
        # Calculate g-index
        g_index = 0
        total = 0
        for i, c in enumerate(citations_sorted, 1):
            total += c
            if total >= i * i:
                g_index = i
        
        # Calculate i10 and i100 indices
        i10_index = sum(1 for p in self.publications if p.cited_by_count >= 10)
        i100_index = sum(1 for p in self.publications if p.cited_by_count >= 100)
        
        # Average citations
        avg_citations = total_cites / total_pubs if total_pubs > 0 else 0
        
        # Open access
        open_access_count = sum(1 for p in self.publications if p.is_open_access)
        open_access_percent = (open_access_count / total_pubs * 100) if total_pubs > 0 else 0
        
        # Open access breakdown
        oa_breakdown = defaultdict(int)
        for pub in self.publications:
            status = pub.open_access_status.lower() if pub.open_access_status else "unknown"
            oa_breakdown[status] += 1
        
        # Active years
        years = set(p.publication_year for p in self.publications if p.publication_year > 0)
        active_years = len(years)
        
        # Unique authors
        unique_authors = set()
        for pub in self.publications:
            for author in pub.authors:
                if author.display_name:
                    unique_authors.add(author.display_name)
        
        # Unique countries
        unique_countries = set()
        for pub in self.publications:
            for author in pub.authors:
                unique_countries.update(author.countries)
        
        # Citing works statistics
        total_citing_works = len(self.citing_works)
        
        # Unique citing journals
        unique_citing_journals = set()
        for cite in self.citing_works:
            if cite.citing_journal:
                unique_citing_journals.add(cite.citing_journal)
        
        # Collaboration metrics
        total_authors = 0
        total_affiliations = 0
        total_countries_per_pub = 0
        international_count = 0
        
        for pub in self.publications:
            pub_authors = set()
            pub_affiliations = set()
            pub_countries = set()
            
            for author in pub.authors:
                if author.display_name:
                    pub_authors.add(author.display_name)
                pub_affiliations.update(author.affiliations)
                pub_countries.update(author.countries)
            
            total_authors += len(pub_authors)
            total_affiliations += len(pub_affiliations)
            total_countries_per_pub += len(pub_countries)
            
            if len(pub_countries) > 1:
                international_count += 1
        
        avg_authors = total_authors / total_pubs if total_pubs > 0 else 0
        avg_affiliations = total_affiliations / total_pubs if total_pubs > 0 else 0
        avg_countries = total_countries_per_pub / total_pubs if total_pubs > 0 else 0
        international_rate = (international_count / total_pubs * 100) if total_pubs > 0 else 0
        
        # Collaboration by year
        collab_by_year = defaultdict(lambda: {'papers': 0, 'authors': 0, 'countries': 0, 'international': 0})
        for pub in self.publications:
            year = pub.publication_year
            if year > 0:
                pub_authors = set()
                pub_countries = set()
                for author in pub.authors:
                    if author.display_name:
                        pub_authors.add(author.display_name)
                    pub_countries.update(author.countries)
                
                collab_by_year[year]['papers'] += 1
                collab_by_year[year]['authors'] += len(pub_authors)
                collab_by_year[year]['countries'] += len(pub_countries)
                if len(pub_countries) > 1:
                    collab_by_year[year]['international'] += 1
        
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
            'open_access_breakdown': dict(oa_breakdown),
            'active_years': active_years,
            'unique_authors': len(unique_authors),
            'unique_countries': len(unique_countries),
            'total_citing_works': total_citing_works,
            'unique_citing_journals': len(unique_citing_journals),
            'avg_authors_per_paper': avg_authors,
            'avg_affiliations_per_paper': avg_affiliations,
            'avg_countries_per_paper': avg_countries,
            'international_collaboration_rate': international_rate,
            'collaboration_by_year': dict(collab_by_year)
        }
    
    def get_most_cited_publications(self, top_n: int = 30) -> List[Dict]:
        """Get most cited publications"""
        sorted_pubs = sorted(self.publications, key=lambda x: x.cited_by_count, reverse=True)
        
        result = []
        for i, pub in enumerate(sorted_pubs[:top_n], 1):
            result.append({
                'rank': i,
                'title': pub.title,
                'year': pub.publication_year,
                'citations': pub.cited_by_count,
                'citations_per_year': pub.citations_per_year,
                'authors': [a.display_name for a in pub.authors],
                'doi': pub.doi
            })
        
        return result
    
    def analyze_authors(self) -> Dict:
        """Analyze authors with ORCID, affiliations, and countries"""
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
                key = author.display_name
                if not key:
                    continue
                
                stats = author_stats[key]
                stats['display_name'] = author.display_name
                if author.orcid and not stats['orcid']:
                    stats['orcid'] = author.orcid
                stats['affiliations'].update(author.affiliations)
                stats['countries'].update(author.countries)
                stats['publication_count'] += 1
                stats['citation_count'] += pub.cited_by_count
                stats['papers'].append(pub.doi)
        
        # Sort by publication count
        sorted_authors = sorted(
            [{
                'display_name': v['display_name'],
                'orcid': v['orcid'],
                'affiliations': list(v['affiliations'])[:10],
                'countries': list(v['countries']),
                'publication_count': v['publication_count'],
                'citation_count': v['citation_count'],
                'papers': v['papers']
            } for v in author_stats.values()],
            key=lambda x: x['publication_count'],
            reverse=True
        )
        
        return {
            'top_authors': sorted_authors[:30],
            'total_authors': len(author_stats)
        }
    
    def analyze_affiliations(self) -> Dict:
        """Analyze affiliations frequency"""
        aff_counter = Counter()
        
        for pub in self.publications:
            for author in pub.authors:
                for aff in author.affiliations:
                    if aff:
                        aff_counter[aff] += 1
        
        return {
            'top_affiliations': aff_counter.most_common(30),
            'unique_affiliations': len(aff_counter)
        }
    
    def analyze_geography(self) -> Dict:
        """Analyze geographic distribution (3 types)"""
        # Type 1: Unique countries per publication
        country_per_pub = Counter()
        # Type 2: Authors per country
        authors_per_country = Counter()
        # Type 3: Collaboration patterns
        collab_patterns = Counter()
        # Collaboration couples
        collab_couples = Counter()
        
        for pub in self.publications:
            pub_countries = set()
            
            for author in pub.authors:
                for country in author.countries:
                    if country:
                        pub_countries.add(country)
                        authors_per_country[country] += 1
            
            # Type 1: Count each publication once per unique country
            for country in pub_countries:
                country_per_pub[country] += 1
            
            # Type 3: Collaboration patterns
            sorted_countries = sorted(pub_countries)
            if len(sorted_countries) == 1:
                collab_patterns[sorted_countries[0]] += 1
            elif len(sorted_countries) > 1:
                pattern = ' + '.join(sorted_countries)
                collab_patterns[pattern] += 1
                
                # Collaboration couples (all pairs)
                for i in range(len(sorted_countries)):
                    for j in range(i + 1, len(sorted_countries)):
                        pair = tuple(sorted([sorted_countries[i], sorted_countries[j]]))
                        collab_couples[pair] += 1
        
        # Collaboration by year
        collab_by_year = defaultdict(lambda: {'single': 0, 'international': 0})
        for pub in self.publications:
            year = pub.publication_year
            if year > 0:
                pub_countries = set()
                for author in pub.authors:
                    pub_countries.update(author.countries)
                
                if len(pub_countries) <= 1:
                    collab_by_year[year]['single'] += 1
                else:
                    collab_by_year[year]['international'] += 1
        
        return {
            'type1_unique_countries_per_pub': dict(country_per_pub.most_common()),
            'type2_authors_per_country': dict(authors_per_country.most_common()),
            'type3_collaboration_patterns': dict(collab_patterns.most_common()),
            'collaboration_couples': dict(collab_couples.most_common(30)),
            'collaboration_by_year': dict(collab_by_year),
            'single_country_count': sum(1 for p in collab_patterns.values() if len(str(p).split(' + ')) == 1),
            'international_count': sum(1 for p in collab_patterns.values() if len(str(p).split(' + ')) > 1),
            'total_pubs_with_country': len([p for p in self.publications if any(a.countries for a in p.authors)])
        }
    
    def analyze_citation_dynamics(self) -> Dict:
        """Analyze citation dynamics"""
        # Yearly dynamics: {publication_year: {citation_year: count}}
        yearly_matrix = defaultdict(lambda: defaultdict(int))
        
        for pub in self.publications:
            pub_year = pub.publication_year
            if pub_year > 0 and pub.id in self.citations:
                for cite in self.citations[pub.id]:
                    cite_year = cite.citing_year
                    if cite_year > 0:
                        yearly_matrix[pub_year][cite_year] += 1
        
        # Cumulative citations
        all_years = sorted(set(pub.publication_year for pub in self.publications if pub.publication_year > 0))
        cumulative = {}
        running_total = 0
        
        for year in all_years:
            year_total = sum(yearly_matrix.get(year, {}).values())
            running_total += year_total
            cumulative[year] = running_total
        
        # Prepare heatmap data
        heatmap_data = []
        for pub_year in sorted(yearly_matrix.keys()):
            for cite_year in sorted(yearly_matrix[pub_year].keys()):
                heatmap_data.append({
                    'publication_year': pub_year,
                    'citation_year': cite_year,
                    'citations_count': yearly_matrix[pub_year][cite_year]
                })
        
        return {
            'yearly_matrix': dict(yearly_matrix),
            'cumulative': cumulative,
            'heatmap_data': heatmap_data,
            'total_citations_by_year': {
                year: sum(yearly_matrix.get(year, {}).values())
                for year in yearly_matrix.keys()
            }
        }
    
    def analyze_citing_works(self) -> Dict:
        """Analyze citing works"""
        if not self.citing_works:
            return {
                'total_citing_works': 0,
                'unique_authors': 0,
                'unique_affiliations': 0,
                'unique_countries': 0,
                'unique_journals': 0,
                'unique_publishers': 0,
                'top_authors': [],
                'top_affiliations': [],
                'top_countries': [],
                'top_journals': [],
                'top_publishers': []
            }
        
        # Counters
        author_counter = Counter()
        aff_counter = Counter()
        country_counter = Counter()
        journal_counter = Counter()
        publisher_counter = Counter()
        
        for cite in self.citing_works:
            # Authors
            for author in cite.citing_authors:
                if author.display_name:
                    author_counter[author.display_name] += 1
            
            # Affiliations
            for aff in cite.citing_affiliations:
                if aff:
                    aff_counter[aff] += 1
            
            # Countries
            for country in cite.citing_countries:
                if country:
                    country_counter[country] += 1
            
            # Journals
            if cite.citing_journal:
                journal_counter[cite.citing_journal] += 1
            
            # Publishers
            if cite.citing_publisher:
                publisher_counter[cite.citing_publisher] += 1
        
        return {
            'total_citing_works': len(self.citing_works),
            'unique_authors': len(author_counter),
            'unique_affiliations': len(aff_counter),
            'unique_countries': len(country_counter),
            'unique_journals': len(journal_counter),
            'unique_publishers': len(publisher_counter),
            'top_authors': author_counter.most_common(30),
            'top_affiliations': aff_counter.most_common(30),
            'top_countries': country_counter.most_common(30),
            'top_journals': journal_counter.most_common(30),
            'top_publishers': publisher_counter.most_common(30)
        }
    
    def analyze_topics(self) -> Dict:
        """Analyze topics, fields, subfields, domains, concepts"""
        # Extract topics from publications and citing works
        pub_topics = defaultdict(lambda: {'count': 0, 'years': [], 'scores': []})
        cite_topics = defaultdict(lambda: {'count': 0, 'years': [], 'scores': []})
        
        # Also track fields, subfields, domains
        pub_fields = defaultdict(lambda: {'count': 0, 'years': []})
        cite_fields = defaultdict(lambda: {'count': 0, 'years': []})
        pub_subfields = defaultdict(lambda: {'count': 0, 'years': []})
        cite_subfields = defaultdict(lambda: {'count': 0, 'years': []})
        pub_domains = defaultdict(lambda: {'count': 0, 'years': []})
        cite_domains = defaultdict(lambda: {'count': 0, 'years': []})
        pub_concepts = defaultdict(lambda: {'count': 0, 'years': [], 'scores': []})
        cite_concepts = defaultdict(lambda: {'count': 0, 'years': [], 'scores': []})
        
        # Process publications
        for pub in self.publications:
            year = pub.publication_year
            
            # Topics
            for topic in pub.topics:
                if topic.display_name:
                    pub_topics[topic.display_name]['count'] += 1
                    pub_topics[topic.display_name]['years'].append(year)
                    pub_topics[topic.display_name]['scores'].append(topic.score)
            
            # Concepts
            for concept in pub.concepts:
                if concept.display_name:
                    pub_concepts[concept.display_name]['count'] += 1
                    pub_concepts[concept.display_name]['years'].append(year)
                    pub_concepts[concept.display_name]['scores'].append(concept.score)
        
        # Process citing works
        for cite in self.citing_works:
            year = cite.citing_year
            
            # Topics
            for topic in cite.citing_topics:
                if topic.display_name:
                    cite_topics[topic.display_name]['count'] += 1
                    cite_topics[topic.display_name]['years'].append(year)
                    cite_topics[topic.display_name]['scores'].append(topic.score)
        
        # Combine and calculate metrics
        combined_topics = {}
        all_topics = set(pub_topics.keys()) | set(cite_topics.keys())
        
        for topic in all_topics:
            pub_count = pub_topics.get(topic, {}).get('count', 0)
            cite_count = cite_topics.get(topic, {}).get('count', 0)
            pub_years = pub_topics.get(topic, {}).get('years', [])
            cite_years = cite_topics.get(topic, {}).get('years', [])
            pub_scores = pub_topics.get(topic, {}).get('scores', [])
            cite_scores = cite_topics.get(topic, {}).get('scores', [])
            
            # Normalized counts (by total publications/citations)
            pub_norm = pub_count / len(self.publications) if self.publications else 0
            cite_norm = cite_count / len(self.citing_works) if self.citing_works else 0
            total_norm = (pub_count + cite_count) / (len(self.publications) + len(self.citing_works)) if (self.publications or self.citing_works) else 0
            
            # First year and peak year
            all_years = pub_years + cite_years
            first_year = min(all_years) if all_years else 0
            peak_year = max(set(all_years), key=all_years.count) if all_years else 0
            
            # Recent 5 years
            current_year = datetime.now().year
            recent_5_years = sum(1 for y in all_years if y >= current_year - 5)
            
            combined_topics[topic] = {
                'analyzed_count': pub_count,
                'citing_count': cite_count,
                'analyzed_norm_count': pub_norm,
                'citing_norm_count': cite_norm,
                'total_norm_count': total_norm,
                'first_year': first_year,
                'peak_year': peak_year,
                'recent_5_years_count': recent_5_years
            }
        
        # Sort by total norm count
        sorted_topics = sorted(
            [{'topic': k, **v} for k, v in combined_topics.items()],
            key=lambda x: x['total_norm_count'],
            reverse=True
        )
        
        return {
            'topics': sorted_topics[:20],
            'total_topics': len(combined_topics),
            'pub_topics_count': len(pub_topics),
            'cite_topics_count': len(cite_topics)
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
                        'citing_topics': [t.display_name for t in cite.citing_topics],
                        'citing_open_access_status': cite.citing_open_access_status
                    })
                
                detailed[pub.id] = {
                    'title': pub.title,
                    'year': pub.publication_year,
                    'doi': pub.doi,
                    'total_citations': len(citations_list),
                    'citations': citations_list
                }
        
        return detailed
    
    def get_all_publications(self) -> List[Dict]:
        """Get all publications with metadata for filtering"""
        result = []
        for pub in self.publications:
            result.append({
                'id': pub.id,
                'title': pub.title,
                'year': pub.publication_year,
                'citations': pub.cited_by_count,
                'citations_per_year': pub.citations_per_year,
                'journal': pub.journal_name,
                'doi': pub.doi,
                'authors': [a.display_name for a in pub.authors],
                'countries': [c for a in pub.authors for c in a.countries],
                'affiliations': [a for author in pub.authors for a in author.affiliations],
                'open_access_status': pub.open_access_status,
                'is_open_access': pub.is_open_access
            })
        
        return sorted(result, key=lambda x: x['year'], reverse=True)
    
    def calculate_citation_velocity(self) -> Dict:
        """Calculate citation velocity for each publication"""
        velocities = {}
        current_year = datetime.now().year
        
        for pub in self.publications:
            if pub.cited_by_count > 0 and pub.publication_year > 0:
                age = current_year - pub.publication_year
                if age > 0:
                    velocity = pub.cited_by_count / age
                else:
                    velocity = pub.cited_by_count
                
                # Categorize velocity
                if velocity >= 10:
                    category = "Very High"
                elif velocity >= 5:
                    category = "High"
                elif velocity >= 1:
                    category = "Medium"
                else:
                    category = "Low"
                
                velocities[pub.id] = {
                    'velocity': velocity,
                    'category': category,
                    'age': age,
                    'citations': pub.cited_by_count,
                    'title': pub.title,
                    'year': pub.publication_year,
                    'doi': pub.doi
                }
        
        return velocities

# ======================== DATA COLLECTOR ========================

def collect_journal_data(issn: str, years, max_workers: int = 8, progress_callback=None) -> JournalData:
    """
    Collect all data for journal analysis
    
    Args:
        issn: ISSN of the journal
        years: int, list, or tuple of years
        max_workers: number of parallel workers
        progress_callback: function to update progress
    
    Returns:
        JournalData object with all collected data
    """
    client = OpenAlexClient(max_workers=max_workers)
    
    # Step 1: Get publications
    if progress_callback:
        progress_callback("publications", 0)
    
    publications = client.get_publications(issn, years)
    
    if progress_callback:
        progress_callback("publications", len(publications))
    
    # Step 2: Get citations for each publication
    citations = {}
    all_citing_works = []
    
    if progress_callback:
        progress_callback("citations_start", len(publications))
    
    total_processed = 0
    
    # Use ThreadPoolExecutor for parallel citation collection
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {}
        for pub in publications:
            if pub.cited_by_count > 0:
                future = executor.submit(client.get_citing_works, pub)
                futures[future] = pub.id
        
        for future in as_completed(futures):
            pub_id = futures[future]
            try:
                citing_works = future.result()
                citations[pub_id] = citing_works
                all_citing_works.extend(citing_works)
            except Exception:
                citations[pub_id] = []
            
            total_processed += 1
            if progress_callback:
                progress_callback("citations_progress", total_processed)
    
    # Step 3: Create JournalData object
    data = JournalData(
        publications=publications,
        citations=citations,
        citing_works=all_citing_works
    )
    
    return data

# ======================== HTML REPORT GENERATOR ========================

def generate_html_report(data: JournalData, metrics: Dict, lang: str = 'en', primary_color: str = '#667eea', secondary_color: str = '#f39c12') -> str:
    """Generate comprehensive HTML report"""
    
    # Добавьте эти строки
    BASE_CSS = """
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f7fa; color: #333; line-height: 1.6; }
        .main-content { max-width: 1400px; margin: 0 auto; padding: 20px; }
    """
    
    import base64
    
    # Load logo
    logo_base64 = ""
    try:
        with open("logo.png", "rb") as img_file:
            logo_base64 = base64.b64encode(img_file.read()).decode()
    except FileNotFoundError:
        pass
    
    # Get localized text
    def t(key: str) -> str:
        lang_dict = TEXTS.get(lang, TEXTS['en'])
        return lang_dict.get(key, TEXTS['en'].get(key, key))
    
    # Generate CSS variables for theme
    css_vars = generate_css_variables(primary_color, secondary_color)
    
    # Prepare data for template
    overview = metrics['overview']
    most_cited = metrics['most_cited']
    authors = metrics['authors']
    affiliations = metrics['affiliations']
    geography = metrics['geography']
    citation_dynamics = metrics['citation_dynamics']
    citing_works = metrics['citing_works']
    topics = metrics['topics']
    detailed_citations = metrics['detailed_citations']
    all_publications = metrics['all_publications']
    citation_velocity = metrics['citation_velocity']
    
    # Build HTML sections
    
    # 1. Overview section
    overview_html = f"""
    <div id="overview" class="section">
        <div class="section-title"><span class="icon">📊</span> {t('overview')}</div>
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">{overview['total_publications']}</div>
                <div class="stat-label">{t('total_publications')}</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{overview['total_citations']}</div>
                <div class="stat-label">{t('total_citations')}</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{overview['h_index']}</div>
                <div class="stat-label">{t('h_index')}</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{overview['g_index']}</div>
                <div class="stat-label">{t('g_index')}</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{overview['i10_index']}</div>
                <div class="stat-label">{t('i10_index')}</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{overview['i100_index']}</div>
                <div class="stat-label">{t('i100_index')}</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{overview['avg_citations']:.1f}</div>
                <div class="stat-label">{t('avg_citations')}</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{overview['open_access_percent']:.1f}%</div>
                <div class="stat-label">{t('open_access')}</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{overview['active_years']}</div>
                <div class="stat-label">{t('active_years')}</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{overview['unique_authors']}</div>
                <div class="stat-label">{t('unique_authors')}</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{overview['unique_countries']}</div>
                <div class="stat-label">{t('unique_countries')}</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{overview['total_citing_works']}</div>
                <div class="stat-label">{t('total_citing_works')}</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{overview['unique_citing_journals']}</div>
                <div class="stat-label">{t('unique_citing_journals')}</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{overview['avg_authors_per_paper']:.1f}</div>
                <div class="stat-label">{t('avg_authors_per_paper')}</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{overview['avg_affiliations_per_paper']:.1f}</div>
                <div class="stat-label">{t('avg_affiliations_per_paper')}</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{overview['avg_countries_per_paper']:.1f}</div>
                <div class="stat-label">{t('avg_countries_per_paper')}</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{overview['international_collaboration_rate']:.1f}%</div>
                <div class="stat-label">{t('international_collaboration_rate')}</div>
            </div>
        </div>
    </div>
    """
    
    # Open Access Breakdown
    oa_breakdown = overview.get('open_access_breakdown', {})
    oa_html = f"""
    <div style="margin-top: 20px;">
        <h4>{t('open_access_breakdown')}</h4>
        <div class="stats-grid" style="grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));">
            <div class="stat-card"><span class="badge-oa-gold">Gold</span><div class="stat-number">{oa_breakdown.get('gold', 0)}</div></div>
            <div class="stat-card"><span class="badge-oa-hybrid">Hybrid</span><div class="stat-number">{oa_breakdown.get('hybrid', 0)}</div></div>
            <div class="stat-card"><span class="badge-oa-green">Green</span><div class="stat-number">{oa_breakdown.get('green', 0)}</div></div>
            <div class="stat-card"><span class="badge-oa-bronze">Bronze</span><div class="stat-number">{oa_breakdown.get('bronze', 0)}</div></div>
            <div class="stat-card"><span class="badge-oa-closed">Closed</span><div class="stat-number">{oa_breakdown.get('closed', 0)}</div></div>
            <div class="stat-card"><span class="badge-oa-closed">Unknown</span><div class="stat-number">{oa_breakdown.get('unknown', 0)}</div></div>
        </div>
    </div>
    """
    overview_html += oa_html
    
    # 2. Most Cited Publications
    most_cited_html = f"""
    <div id="most_cited" class="section">
        <div class="section-title"><span class="icon">🏆</span> {t('most_cited_publications')}</div>
        <div style="overflow-x: auto;">
            <table>
                <thead>
                    <tr>
                        <th>{t('rank')}</th>
                        <th>{t('title')}</th>
                        <th>{t('year')}</th>
                        <th>{t('citations')}</th>
                        <th>{t('citations_per_year')}</th>
                        <th>{t('authors')}</th>
                        <th>{t('doi')}</th>
                    </tr>
                </thead>
                <tbody>
    """
    for pub in most_cited[:30]:
        authors_str = ', '.join(pub['authors'][:3])
        if len(pub['authors']) > 3:
            authors_str += f" +{len(pub['authors']) - 3} more"
        most_cited_html += f"""
                    <tr>
                        <td>{pub['rank']}</td>
                        <td class="word-wrap">{html.escape(pub['title'])}</td>
                        <td>{pub['year']}</td>
                        <td><span class="citation-count">{pub['citations']}</span></td>
                        <td>{pub['citations_per_year']:.1f}</td>
                        <td>{html.escape(authors_str)}</td>
                        <td><a href="https://doi.org/{pub['doi']}" target="_blank" class="doi-link">{pub['doi']}</a></td>
                    </tr>
        """
    most_cited_html += """
                </tbody>
            </table>
        </div>
    </div>
    """
    
    # 3. Author Analysis
    authors_html = f"""
    <div id="authors" class="section">
        <div class="section-title"><span class="icon">👨‍🎓</span> {t('author_analysis')}</div>
        <h4>{t('top_authors')}</h4>
        <div style="overflow-x: auto;">
            <table>
                <thead>
                    <tr>
                        <th>{t('rank')}</th>
                        <th>{t('authors')}</th>
                        <th>{t('orcid')}</th>
                        <th>{t('affiliations')}</th>
                        <th>{t('countries')}</th>
                        <th>{t('publication_count')}</th>
                        <th>{t('citation_count')}</th>
                    </tr>
                </thead>
                <tbody>
    """
    for i, author in enumerate(authors['top_authors'][:30], 1):
        orcid_display = f'<a href="{author["orcid"]}" target="_blank" class="doi-link">{author["orcid"][:20]}...</a>' if author['orcid'] else '-'
        aff_str = ', '.join(author['affiliations'][:2])
        if len(author['affiliations']) > 2:
            aff_str += f" +{len(author['affiliations']) - 2} more"
        country_str = ', '.join(author['countries'][:3])
        if len(author['countries']) > 3:
            country_str += f" +{len(author['countries']) - 3} more"
        authors_html += f"""
                    <tr>
                        <td>{i}</td>
                        <td>{html.escape(author['display_name'])}</td>
                        <td>{orcid_display}</td>
                        <td>{html.escape(aff_str)}</td>
                        <td>{html.escape(country_str)}</td>
                        <td>{author['publication_count']}</td>
                        <td>{author['citation_count']}</td>
                    </tr>
        """
    authors_html += """
                </tbody>
            </table>
        </div>
    """
    
    # Affiliations analysis
    aff_html = f"""
        <h4 style="margin-top: 25px;">{t('top_affiliations')}</h4>
        <div>
    """
    for aff, count in affiliations['top_affiliations'][:20]:
        aff_html += f"""
            <div class="rank-item">
                <span class="rank-name">{html.escape(aff)}</span>
                <span class="rank-count">{count} {t('html_frequency')}</span>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {count / affiliations['top_affiliations'][0][1] * 100 if affiliations['top_affiliations'] else 0}%;"></div>
                </div>
            </div>
        """
    aff_html += f"""
        </div>
        <div style="margin-top: 15px;">
            <span class="badge badge-info">{t('unique_affiliations')}: {affiliations['unique_affiliations']}</span>
        </div>
    </div>
    """
    authors_html += aff_html
    
    # 4. Geographic Analysis
    geo_html = f"""
    <div style="margin-top: 25px;">
        <h4>{t('geographic_analysis')}</h4>
        
        <h5>{t('geography_type_1')}</h5>
        <p style="font-size: 12px; color: #666; margin-bottom: 10px;">{t('geography_type_1_desc')}</p>
        <div>
    """
    for country, count in list(geography['type1_unique_countries_per_pub'].items())[:15]:
        max_count = max(geography['type1_unique_countries_per_pub'].values()) if geography['type1_unique_countries_per_pub'] else 1
        geo_html += f"""
            <div class="rank-item">
                <span class="rank-name">{html.escape(country)}</span>
                <span class="rank-count">{count} {t('html_citations_label')}</span>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {count / max_count * 100}%;"></div>
                </div>
            </div>
        """
    geo_html += f"""
        </div>
        
        <h5 style="margin-top: 20px;">{t('geography_type_2')}</h5>
        <p style="font-size: 12px; color: #666; margin-bottom: 10px;">{t('geography_type_2_desc')}</p>
        <div>
    """
    for country, count in list(geography['type2_authors_per_country'].items())[:15]:
        max_count = max(geography['type2_authors_per_country'].values()) if geography['type2_authors_per_country'] else 1
        geo_html += f"""
            <div class="rank-item">
                <span class="rank-name">{html.escape(country)}</span>
                <span class="rank-count">{count} {t('html_authors_count')}</span>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {count / max_count * 100}%;"></div>
                </div>
            </div>
        """
    geo_html += f"""
        </div>
        
        <h5 style="margin-top: 20px;">{t('geography_type_3')}</h5>
        <p style="font-size: 12px; color: #666; margin-bottom: 10px;">{t('geography_type_3_desc')}</p>
        <div class="stats-grid" style="grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));">
            <div class="stat-card">
                <div class="stat-number">{geography['single_country_count']}</div>
                <div class="stat-label">{t('single_country')}</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{geography['international_count']}</div>
                <div class="stat-label">{t('international_collab')}</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{geography['total_pubs_with_country']}</div>
                <div class="stat-label">{t('total_publications')}</div>
            </div>
        </div>
        
        <h5 style="margin-top: 20px;">{t('collaboration_couples')}</h5>
        <p style="font-size: 12px; color: #666; margin-bottom: 10px;">{t('collaboration_couples_desc')}</p>
        <div>
    """
    for (c1, c2), count in list(geography['collaboration_couples'].items())[:15]:
        max_couple = max(geography['collaboration_couples'].values()) if geography['collaboration_couples'] else 1
        geo_html += f"""
            <div class="rank-item">
                <span class="rank-name">{html.escape(c1)} + {html.escape(c2)}</span>
                <span class="rank-count">{count} {t('html_joint_works')}</span>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {count / max_couple * 100}%;"></div>
                </div>
            </div>
        """
    geo_html += f"""
        </div>
    </div>
    """
    authors_html += geo_html
    
    # 5. Citation Analysis
    citation_html = f"""
    <div id="citation_analysis" class="section">
        <div class="section-title"><span class="icon">📈</span> {t('citation_analysis')}</div>
        
        <h4>{t('citation_dynamics')}</h4>
        <div style="overflow-x: auto;">
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
    for item in citation_dynamics['heatmap_data'][:50]:
        citation_html += f"""
                    <tr>
                        <td>{item['publication_year']}</td>
                        <td>{item['citation_year']}</td>
                        <td>{item['citations_count']}</td>
                    </tr>
        """
    citation_html += f"""
                </tbody>
            </table>
        </div>
        
        <h4 style="margin-top: 25px;">{t('cumulative_citations')}</h4>
        <div>
    """
    for year, total in citation_dynamics['cumulative'].items():
        max_cum = max(citation_dynamics['cumulative'].values()) if citation_dynamics['cumulative'] else 1
        citation_html += f"""
            <div class="rank-item">
                <span class="rank-name">{year}</span>
                <span class="rank-count">{total} {t('html_citations_label')}</span>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {total / max_cum * 100}%;"></div>
                </div>
            </div>
        """
    citation_html += f"""
        </div>
        
        <h4 style="margin-top: 25px;">{t('citation_network')}</h4>
        <div style="overflow-x: auto; max-height: 400px; overflow-y: auto;">
            <table>
                <thead>
                    <tr>
                        <th>{t('publication_year')} \\ {t('citation_year')}</th>
    """
    # Get all citation years
    all_cite_years = sorted(set(item['citation_year'] for item in citation_dynamics['heatmap_data']))
    for year in all_cite_years[:20]:
        citation_html += f"<th>{year}</th>"
    citation_html += f"""
                    </tr>
                </thead>
                <tbody>
    """
    # Build heatmap matrix
    heatmap_dict = {}
    for item in citation_dynamics['heatmap_data']:
        key = (item['publication_year'], item['citation_year'])
        heatmap_dict[key] = item['citations_count']
    
    pub_years = sorted(set(item['publication_year'] for item in citation_dynamics['heatmap_data']))
    for pub_year in pub_years[:20]:
        citation_html += f"<tr><td><strong>{pub_year}</strong></td>"
        for cite_year in all_cite_years[:20]:
            count = heatmap_dict.get((pub_year, cite_year), 0)
            if count > 0:
                citation_html += f"<td style='background: rgba(102, 126, 234, {min(count / 10, 0.8)}); color: white;'>{count}</td>"
            else:
                citation_html += f"<td style='background: #f8f9fa;'>-</td>"
        citation_html += "</tr>"
    citation_html += f"""
                </tbody>
            </table>
        </div>
    </div>
    """
    
    # 6. Citing Works Analysis
    citing_html = f"""
    <div id="citing_works" class="section">
        <div class="section-title"><span class="icon">🔗</span> {t('citing_works_analysis')}</div>
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">{citing_works['total_citing_works']}</div>
                <div class="stat-label">{t('total_citing_works')}</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{citing_works['unique_authors']}</div>
                <div class="stat-label">{t('unique_citing_authors')}</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{citing_works['unique_affiliations']}</div>
                <div class="stat-label">{t('unique_citing_affiliations')}</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{citing_works['unique_countries']}</div>
                <div class="stat-label">{t('unique_citing_countries')}</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{citing_works['unique_journals']}</div>
                <div class="stat-label">{t('unique_citing_journals')}</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{citing_works['unique_publishers']}</div>
                <div class="stat-label">{t('unique_citing_publishers')}</div>
            </div>
        </div>
    """
    
    # Top citing authors
    if citing_works['top_authors']:
        citing_html += f"""
        <h4>{t('top_citing_authors')}</h4>
        <div>
        """
        for author, count in citing_works['top_authors'][:20]:
            max_author = citing_works['top_authors'][0][1] if citing_works['top_authors'] else 1
            citing_html += f"""
            <div class="rank-item">
                <span class="rank-name">{html.escape(author)}</span>
                <span class="rank-count">{count} {t('html_frequency')}</span>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {count / max_author * 100}%;"></div>
                </div>
            </div>
            """
        citing_html += "</div>"
    
    # Top citing journals
    if citing_works['top_journals']:
        citing_html += f"""
        <h4 style="margin-top: 25px;">{t('top_citing_journals')}</h4>
        <div>
        """
        for journal, count in citing_works['top_journals'][:20]:
            max_journal = citing_works['top_journals'][0][1] if citing_works['top_journals'] else 1
            citing_html += f"""
            <div class="rank-item">
                <span class="rank-name">{html.escape(journal)}</span>
                <span class="rank-count">{count} {t('html_frequency')}</span>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {count / max_journal * 100}%;"></div>
                </div>
            </div>
            """
        citing_html += "</div>"
    
    # Top citing countries
    if citing_works['top_countries']:
        citing_html += f"""
        <h4 style="margin-top: 25px;">{t('top_citing_countries')}</h4>
        <div>
        """
        for country, count in citing_works['top_countries'][:20]:
            max_country = citing_works['top_countries'][0][1] if citing_works['top_countries'] else 1
            citing_html += f"""
            <div class="rank-item">
                <span class="rank-name">{html.escape(country)}</span>
                <span class="rank-count">{count} {t('html_frequency')}</span>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {count / max_country * 100}%;"></div>
                </div>
            </div>
            """
        citing_html += "</div>"
    
    citing_html += "</div>"
    
    # 7. Topics Analysis
    topics_html = f"""
    <div id="topics" class="section">
        <div class="section-title"><span class="icon">🧠</span> {t('topics_analysis')}</div>
        <div style="overflow-x: auto;">
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
                        <th>{t('recent_5_years_count')}</th>
                    </tr>
                </thead>
                <tbody>
    """
    for item in topics['topics'][:20]:
        topics_html += f"""
                    <tr>
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
    topics_html += f"""
                </tbody>
            </table>
        </div>
        <div style="margin-top: 15px;">
            <span class="badge badge-info">{t('total_topics')}: {topics['total_topics']}</span>
            <span class="badge badge-info">{t('analyzed_count')}: {topics['pub_topics_count']}</span>
            <span class="badge badge-info">{t('citing_count')}: {topics['cite_topics_count']}</span>
        </div>
    </div>
    """
    
    # 8. Detailed Citations
    detailed_html = f"""
    <div id="detailed_citations" class="section">
        <div class="section-title"><span class="icon">📋</span> {t('detailed_citations')}</div>
    """
    
    if detailed_citations:
        for pub_id, data in detailed_citations.items():
            safe_id = pub_id.replace('https://openalex.org/', '').replace('/', '_')
            detailed_html += f"""
            <div class="collapser" onclick="toggleCitations('{safe_id}')">
                <strong>{html.escape(data['title'])}</strong>
                <span class="badge badge-info">{data['year']}</span>
                <span class="citation-count">{data['total_citations']} {t('citations')}</span>
                <span style="font-size: 12px; color: #666; margin-left: 10px;">DOI: {data['doi']}</span>
                <span style="float: right; font-size: 12px; color: #666;">{t('show_citations')}</span>
            </div>
            <div id="citations_{safe_id}" style="display: none;">
            """
            for cite in data['citations']:
                authors_str = ', '.join(cite['citing_authors'][:3])
                if len(cite['citing_authors']) > 3:
                    authors_str += f" +{len(cite['citing_authors']) - 3} more"
                countries_str = ', '.join(cite['citing_countries'][:3])
                if len(cite['citing_countries']) > 3:
                    countries_str += f" +{len(cite['citing_countries']) - 3} more"
                topics_str = ', '.join(cite['citing_topics'][:3])
                if len(cite['citing_topics']) > 3:
                    topics_str += f" +{len(cite['citing_topics']) - 3} more"
                
                detailed_html += f"""
                <div class="citation-detail">
                    <div class="citation-title"><strong>{html.escape(cite['citing_title'] or '')}</strong></div>
                    <div class="cite-meta">
                        <strong>{t('citing_journal')}:</strong> {html.escape(cite['citing_journal']) or ''} | 
                        <strong>{t('citing_year')}:</strong> {cite['citing_year'] or ''} | 
                        <strong>{t('citing_date')}:</strong> {cite['citing_date'] or ''} |
                        <strong>{t('citation_lag')}:</strong> {cite['citation_lag'] or ''} years
                    </div>
                    <div class="cite-meta">
                        <strong>{t('authors')}:</strong> {html.escape(authors_str) or ''} |
                        <strong>{t('countries')}:</strong> {html.escape(countries_str) or ''} |
                        <strong>{t('topics')}:</strong> {html.escape(topics_str)}
                    </div>
                    <div class="cite-meta">
                        <a href="https://doi.org/{cite['citing_doi']}" target="_blank" class="doi-link">DOI: {cite['citing_doi']}</a>
                    </div>
                </div>
                """
            detailed_html += """
            </div>
            """
    else:
        detailed_html += f"<p>{t('html_not_found')}</p>"
    
    detailed_html += "</div>"
    
    # 9. All Publications with filters
    pub_html = f"""
    <div id="all_publications" class="section">
        <div class="section-title"><span class="icon">📚</span> {t('all_publications')}</div>
        
        <div class="filter-section">
            <div class="filter-row">
                <div>
                    <label for="yearFilter">{t('filter_by_year')}:</label>
                    <select id="yearFilter" onchange="filterPublications()">
                        <option value="">{t('all_years')}</option>
    """
    years = sorted(set(p['year'] for p in all_publications if p['year'] > 0), reverse=True)
    for year in years:
        pub_html += f'<option value="{year}">{year}</option>'
    pub_html += f"""
                    </select>
                </div>
                <div>
                    <label for="authorFilter">{t('filter_by_author')}:</label>
                    <input type="text" id="authorFilter" placeholder="{t('filter_by_author')}" onkeyup="filterPublications()">
                </div>
                <div>
                    <label for="citationFilter">{t('filter_by_citations')}:</label>
                    <input type="number" id="citationFilter" placeholder="{t('filter_by_citations')}" min="0" onchange="filterPublications()">
                </div>
                <div>
                    <label for="searchInput">{t('search_publications')}:</label>
                    <input type="text" id="searchInput" placeholder="{t('search_placeholder')}" onkeyup="filterPublications()">
                </div>
                <div>
                    <span id="visibleCount" style="font-weight: 500;">{t('showing_publications').format(len(all_publications))}</span>
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
                        <th onclick="sortTable(4)" style="cursor: pointer;">{t('citations_per_year')}</th>
                        <th onclick="sortTable(5)" style="cursor: pointer;">{t('journal')}</th>
                        <th>{t('doi')}</th>
                        <th>{t('show_citations_short')}</th>
                    </tr>
                </thead>
                <tbody>
    """
    for i, pub in enumerate(all_publications, 1):
        authors_str = ', '.join(pub['authors'][:3])
        if len(pub['authors']) > 3:
            authors_str += f" +{len(pub['authors']) - 3} more"
        
        safe_id = pub['id'].replace('https://openalex.org/', '').replace('/', '_')
        pub_html += f"""
                    <tr data-year="{pub['year']}" data-authors="{', '.join(pub['authors']).lower()}" data-citations="{pub['citations']}" data-title="{pub['title'].lower()}" data-doi="{pub['doi'].lower()}">
                        <td>{i}</td>
                        <td class="word-wrap">{html.escape(pub['title'])}</td>
                        <td>{pub['year']}</td>
                        <td><span class="citation-count">{pub['citations']}</span></td>
                        <td>{pub['citations_per_year']:.1f}</td>
                        <td>{html.escape(pub['journal'])}</td>
                        <td><a href="https://doi.org/{pub['doi']}" target="_blank" class="doi-link">{pub['doi']}</a></td>
                        <td>
                            <button onclick="toggleCitations('{safe_id}')" class="toggle-button">{t('show_citations')}</button>
                        </td>
                    </tr>
        """
    pub_html += f"""
                </tbody>
            </table>
        </div>
    </div>
    """
    
    # JavaScript for interactivity
    js_code = """
    <script>
        function filterPublications() {
            const year = document.getElementById('yearFilter').value;
            const author = document.getElementById('authorFilter').value.toLowerCase();
            const minCitations = parseInt(document.getElementById('citationFilter').value) || 0;
            const search = document.getElementById('searchInput').value.toLowerCase();
            
            const rows = document.querySelectorAll('#publicationsTable tbody tr');
            let visible = 0;
            
            rows.forEach(row => {
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
            });
            
            document.getElementById('visibleCount').textContent = 'Showing ' + visible + ' publications';
        }
        
        function toggleCitations(pubId) {
            const element = document.getElementById('citations_' + pubId);
            if (element) {
                if (element.style.display === 'none') {
                    element.style.display = 'block';
                } else {
                    element.style.display = 'none';
                }
            }
        }
        
        function sortTable(column) {
            const table = document.getElementById('publicationsTable');
            const tbody = table.querySelector('tbody');
            const rows = Array.from(tbody.querySelectorAll('tr'));
            
            let sorted;
            if (column === 0) {
                sorted = rows.sort((a, b) => {
                    const aVal = parseInt(a.cells[0].textContent);
                    const bVal = parseInt(b.cells[0].textContent);
                    return aVal - bVal;
                });
            } else if (column === 2) {
                sorted = rows.sort((a, b) => {
                    const aVal = parseInt(a.cells[2].textContent);
                    const bVal = parseInt(b.cells[2].textContent);
                    return bVal - aVal;
                });
            } else if (column === 3) {
                sorted = rows.sort((a, b) => {
                    const aVal = parseInt(a.cells[3].textContent);
                    const bVal = parseInt(b.cells[3].textContent);
                    return bVal - aVal;
                });
            } else if (column === 4) {
                sorted = rows.sort((a, b) => {
                    const aVal = parseFloat(a.cells[4].textContent);
                    const bVal = parseFloat(b.cells[4].textContent);
                    return bVal - aVal;
                });
            } else {
                sorted = rows.sort((a, b) => {
                    const aVal = a.cells[column].textContent.toLowerCase();
                    const bVal = b.cells[column].textContent.toLowerCase();
                    return aVal.localeCompare(bVal);
                });
            }
            
            tbody.innerHTML = '';
            sorted.forEach(row => tbody.appendChild(row));
        }
    </script>
    """
    
    # Navigation sidebar
    sidebar_html = f"""
    <div class="sidebar">
        <h3>{t('navigation')}</h3>
        <a href="#overview">📊 {t('nav_overview')}</a>
        <a href="#most_cited">🏆 {t('nav_most_cited')}</a>
        <a href="#authors">👨‍🎓 {t('nav_authors')}</a>
        <a href="#citation_analysis">📈 {t('nav_citation_analysis')}</a>
        <a href="#citing_works">🔗 {t('nav_citing_works')}</a>
        <a href="#topics">🧠 {t('nav_topics')}</a>
        <a href="#detailed_citations">📋 {t('nav_detailed_citations')}</a>
        <a href="#all_publications">📚 {t('nav_all_publications')}</a>
    </div>
    """
    
    # Header with logo and date
    header_html = f"""
    <div class="header">
        <div style="display: flex; justify-content: center; margin-bottom: 15px;">
            <img src="data:image/png;base64,{logo_base64}" style="height: 150px; width: auto;" alt="Logo">
        </div>
        <div class="date">{t('html_generated')}: {datetime.now().strftime('%d.%m.%Y %H:%M')}</div>
    </div>
    """
    
    # Footer
    footer_html = f"""
    <div class="footer">
        {t('html_footer')}<br>
        {t('html_copyright')}
    </div>
    """
    
    # Combine all sections
    full_html = f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{t('app_title')}</title>
    <style>
        {BASE_CSS}
        {generate_theme_css('default', primary_color, secondary_color)}
        {get_reference_color_style('full')}
        
        .badge-oa-gold {{ background: #ffd700; color: #000; padding: 2px 10px; border-radius: 12px; font-size: 11px; font-weight: 600; }}
        .badge-oa-hybrid {{ background: #ff8c00; color: #fff; padding: 2px 10px; border-radius: 12px; font-size: 11px; font-weight: 600; }}
        .badge-oa-green {{ background: #2e8b57; color: #fff; padding: 2px 10px; border-radius: 12px; font-size: 11px; font-weight: 600; }}
        .badge-oa-bronze {{ background: #cd7f32; color: #fff; padding: 2px 10px; border-radius: 12px; font-size: 11px; font-weight: 600; }}
        .badge-oa-closed {{ background: #6c757d; color: #fff; padding: 2px 10px; border-radius: 12px; font-size: 11px; font-weight: 600; }}
        
        .filter-section {{ background: #f8f9fa; border-radius: 10px; padding: 15px; margin-bottom: 20px; }}
        .filter-row {{ display: flex; gap: 15px; flex-wrap: wrap; align-items: center; }}
        .filter-row label {{ font-weight: 500; font-size: 13px; margin-right: 5px; }}
        .filter-row select, .filter-row input {{ padding: 6px 10px; border: 1px solid #ddd; border-radius: 6px; font-size: 13px; }}
        .filter-row select:focus, .filter-row input:focus {{ border-color: var(--primary); outline: none; box-shadow: 0 0 0 2px var(--hover-light); }}
        
        .collapser {{ cursor: pointer; padding: 10px 15px; background: #f8f9fa; border-radius: 8px; margin-bottom: 5px; transition: background 0.2s; border-left: 3px solid var(--primary); }}
        .collapser:hover {{ background: #f0f0f0; }}
        .citation-detail {{ background: #f8f9fa; border-radius: 8px; padding: 12px; margin: 8px 0 8px 20px; border-left: 3px solid #ddd; transition: background 0.2s; }}
        .citation-detail:hover {{ background: #f0f0f0; }}
        .citation-title {{ font-weight: 500; margin-bottom: 5px; }}
        .cite-meta {{ font-size: 12px; color: #666; margin-top: 3px; }}
        .toggle-button {{ display: inline-block; padding: 4px 12px; border: none; border-radius: 4px; background: var(--primary); color: white; cursor: pointer; font-size: 12px; transition: background 0.2s; }}
        .toggle-button:hover {{ background: var(--secondary); }}
        
        .word-wrap {{ word-wrap: break-word; max-width: 300px; }}
        .citation-count {{ font-weight: 600; color: var(--primary); }}
        .doi-link {{ color: var(--primary); text-decoration: none; font-family: monospace; font-size: 12px; }}
        .doi-link:hover {{ color: var(--secondary); text-decoration: underline; }}
        
        .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 15px; margin-bottom: 20px; }}
        .stat-card {{ background: white; border-radius: 10px; padding: 15px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.08); }}
        .stat-number {{ font-size: 28px; font-weight: bold; background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }}
        .stat-label {{ font-size: 12px; color: #666; margin-top: 5px; }}
        
        .rank-item {{ background: white; border-radius: 8px; padding: 10px 15px; margin-bottom: 6px; border-left: 3px solid var(--primary); transition: all 0.2s; }}
        .rank-item:hover {{ transform: translateX(5px); box-shadow: 0 2px 8px rgba(0,0,0,0.08); }}
        .rank-name {{ font-weight: 500; }}
        .rank-count {{ float: right; color: #666; font-weight: 500; }}
        .progress-bar {{ background: #e0e0e0; border-radius: 10px; height: 6px; margin-top: 6px; overflow: hidden; }}
        .progress-fill {{ background: linear-gradient(90deg, var(--primary), var(--secondary)); height: 100%; border-radius: 10px; transition: width 0.5s; }}
        
        table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
        th {{ background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%); color: white; padding: 10px 12px; text-align: left; font-weight: 600; position: sticky; top: 0; z-index: 10; }}
        td {{ padding: 8px 12px; border-bottom: 1px solid #f0f0f0; }}
        tr:hover {{ background: #f8f9fa; }}
        
        .badge {{ display: inline-block; padding: 2px 10px; border-radius: 12px; font-size: 11px; font-weight: 600; }}
        .badge-info {{ background: #d1ecf1; color: #0c5460; }}
        .badge-success {{ background: #d4edda; color: #155724; }}
        .badge-warning {{ background: #fff3cd; color: #856404; }}
        .badge-danger {{ background: #f8d7da; color: #721c24; }}
        
        .section {{ margin-bottom: 40px; }}
        .section-title {{ font-size: 24px; font-weight: 700; padding-bottom: 10px; margin-bottom: 20px; border-bottom: 3px solid var(--primary); }}
        .icon {{ margin-right: 10px; }}
        .header {{ text-align: center; padding: 20px 0; margin-bottom: 30px; }}
        .date {{ font-size: 14px; color: #666; margin-top: 5px; }}
        .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; margin-top: 40px; border-top: 1px solid #e0e0e0; }}
        .sidebar {{ position: fixed; left: 0; top: 0; width: 200px; height: 100vh; background: linear-gradient(180deg, var(--primary) 0%, var(--secondary) 100%); padding: 20px 15px; overflow-y: auto; z-index: 1000; }}
        .sidebar h3 {{ color: white; font-size: 16px; margin-bottom: 15px; }}
        .sidebar a {{ display: block; color: rgba(255,255,255,0.85); text-decoration: none; padding: 8px 12px; border-radius: 6px; font-size: 13px; transition: all 0.2s; }}
        .sidebar a:hover {{ background: rgba(255,255,255,0.2); color: white; }}
        .main-content {{ margin-left: 220px; padding: 20px 30px; max-width: 1200px; }}
        
        @media (max-width: 768px) {{
            .sidebar {{ display: none; }}
            .main-content {{ margin-left: 0; padding: 15px; }}
            .stats-grid {{ grid-template-columns: repeat(auto-fit, minmax(100px, 1fr)); }}
            .filter-row {{ flex-direction: column; align-items: stretch; }}
            .filter-row div {{ width: 100%; }}
            .filter-row input, .filter-row select {{ width: 100%; }}
        }}
    </style>
</head>
<body>
    {sidebar_html}
    
    <div class="main-content">
        {header_html}
        {overview_html}
        {most_cited_html}
        {authors_html}
        {citation_html}
        {citing_html}
        {topics_html}
        {detailed_html}
        {pub_html}
        {footer_html}
    </div>
    
    {js_code}
</body>
</html>
    """
    
    return full_html

# ======================== STREAMLIT UI ========================

def main():
    # Page configuration
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
        st.session_state.secondary_color = '#f39c12'
    if 'analysis_complete' not in st.session_state:
        st.session_state.analysis_complete = False
    if 'data' not in st.session_state:
        st.session_state.data = None
    if 'metrics' not in st.session_state:
        st.session_state.metrics = None
    
    # Sidebar - Settings and inputs
    with st.sidebar:
        st.image("logo.png", width=150) if os.path.exists("logo.png") else st.markdown("### 📚 Journal Metrics")
        
        st.markdown(f"## {get_text('settings')}")
        
        # Language
        st.markdown(f"### {get_text('language')}")
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
        
        # Input parameters
        st.markdown(f"### {get_text('issn_label')}")
        issn = st.text_input(
            get_text('issn_label'),
            placeholder=get_text('issn_placeholder'),
            key="issn_input"
        )
        
        st.markdown(f"### {get_text('period_label')}")
        period = st.text_input(
            get_text('period_label'),
            placeholder=get_text('period_placeholder'),
            help=get_text('period_help'),
            key="period_input"
        )
        
        st.markdown(f"### {get_text('workers_label')}")
        max_workers = st.slider(
            get_text('workers_label'),
            min_value=4,
            max_value=12,
            value=8,
            step=1,
            help=get_text('workers_help')
        )
        
        st.markdown("---")
        
        # Color Theme (from original code)
        st.markdown(f"## 🎨 Color Theme")
        
        # Predefined theme options
        preset_themes = {
            "Default (Blue-Purple)": {"primary": "#667eea", "secondary": "#f39c12"},
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
                value=st.session_state.primary_color
            )
            st.session_state.primary_color = selected_color
            st.session_state.secondary_color = get_complementary_color(selected_color)
        
        # Color preview
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(
                f'<div style="text-align: center;"><div class="color-preview" style="background: {st.session_state.primary_color};"></div><div style="font-size: 11px;">Primary</div></div>',
                unsafe_allow_html=True
            )
        with col2:
            st.markdown(
                f'<div style="text-align: center;"><div class="color-preview" style="background: {st.session_state.secondary_color};"></div><div style="font-size: 11px;">Secondary</div></div>',
                unsafe_allow_html=True
            )
        
        st.markdown(
            f'<div class="complementary-preview" style="height: 8px; width: 100%; margin: 10px 0;"></div>',
            unsafe_allow_html=True
        )
        
        # Apply theme
        apply_theme_css(st.session_state.primary_color, st.session_state.secondary_color)
        
        st.markdown("---")
        
        # Start button
        if st.button(get_text('start_analysis'), type="primary", use_container_width=True):
            if not issn or not period:
                st.warning("Please fill in both ISSN and Period fields!")
            else:
                # Parse period
                period_clean = period.strip()
                if ',' in period_clean:
                    years = [int(y.strip()) for y in period_clean.split(',') if y.strip().isdigit()]
                elif '-' in period_clean:
                    parts = [p.strip() for p in period_clean.split('-')]
                    if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                        years = (int(parts[0]), int(parts[1]))
                    else:
                        st.error("Invalid period format! Use: 2020-2023")
                        years = None
                else:
                    try:
                        years = int(period_clean)
                    except ValueError:
                        st.error("Invalid period format! Use: 2025 or 2020-2023 or 2020,2021,2022")
                        years = None
                
                if years:
                    # Progress tracking
                    progress_status = st.status(get_text('collecting_publications'), expanded=True)
                    
                    # Define progress callback
                    progress_values = {}
                    
                    def progress_callback(stage, value):
                        if stage == "publications":
                            progress_status.update(label=get_text('found_publications').format(value))
                            st.session_state['pub_count'] = value
                        elif stage == "citations_start":
                            progress_status.update(label=get_text('collecting_citations').format(value))
                            st.session_state['total_pubs'] = value
                            st.session_state['processed_pubs'] = 0
                        elif stage == "citations_progress":
                            st.session_state['processed_pubs'] = value
                            progress_status.update(
                                label=get_text('collecting_citations').format(
                                    f"{value}/{st.session_state['total_pubs']}"
                                )
                            )
                            # Update progress bar
                            if 'progress_bar' in st.session_state:
                                st.session_state.progress_bar.progress(
                                    value / st.session_state['total_pubs']
                                )
                    
                    # Create progress bar
                    progress_bar = st.progress(0)
                    st.session_state.progress_bar = progress_bar
                    st.session_state['total_pubs'] = 0
                    st.session_state['processed_pubs'] = 0
                    
                    # Collect data
                    try:
                        data = collect_journal_data(
                            issn, 
                            years, 
                            max_workers=max_workers,
                            progress_callback=progress_callback
                        )
                        
                        progress_status.update(label=get_text('analyzing_data'), state="running")
                        
                        # Calculate metrics
                        engine = MetricsEngine(data)
                        metrics = {
                            'overview': engine.calculate_overview(),
                            'most_cited': engine.get_most_cited_publications(30),
                            'authors': engine.analyze_authors(),
                            'affiliations': engine.analyze_affiliations(),
                            'geography': engine.analyze_geography(),
                            'citation_dynamics': engine.analyze_citation_dynamics(),
                            'citing_works': engine.analyze_citing_works(),
                            'topics': engine.analyze_topics(),
                            'detailed_citations': engine.get_detailed_citations(),
                            'all_publications': engine.get_all_publications(),
                            'citation_velocity': engine.calculate_citation_velocity()
                        }
                        
                        # Store in session state
                        st.session_state.data = data
                        st.session_state.metrics = metrics
                        st.session_state.analysis_complete = True
                        
                        progress_status.update(label=get_text('analysis_complete'), state="complete")
                        st.balloons()
                        
                    except Exception as e:
                        progress_status.update(label=f"❌ Error: {str(e)}", state="error")
                        st.error(f"An error occurred during analysis: {str(e)}")
    
    # Main area
    st.image("logo.png", width=200) if os.path.exists("logo.png") else None
    st.markdown(f"# {get_text('app_title')}")
    st.markdown(f"### {get_text('app_subtitle')}")
    st.markdown("---")
    
    if st.session_state.analysis_complete and st.session_state.metrics:
        metrics = st.session_state.metrics
        data = st.session_state.data
        
        # Create tabs
        tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
            get_text('nav_overview'),
            get_text('nav_most_cited'),
            get_text('nav_authors'),
            get_text('nav_citation_analysis'),
            get_text('nav_citing_works'),
            get_text('nav_topics'),
            get_text('nav_detailed_citations'),
            get_text('nav_all_publications'),
            "📄 Export"
        ])
        
        with tab1:
            st.markdown(f"### {get_text('overview')}")
            
            # Metrics grid
            overview = metrics['overview']
            col1, col2, col3, col4, col5, col6 = st.columns(6)
            
            with col1:
                st.metric(get_text('total_publications'), overview['total_publications'])
            with col2:
                st.metric(get_text('total_citations'), overview['total_citations'])
            with col3:
                st.metric(get_text('h_index'), overview['h_index'])
            with col4:
                st.metric(get_text('g_index'), overview['g_index'])
            with col5:
                st.metric(get_text('i10_index'), overview['i10_index'])
            with col6:
                st.metric(get_text('i100_index'), overview['i100_index'])
            
            col7, col8, col9, col10, col11, col12 = st.columns(6)
            with col7:
                st.metric(get_text('avg_citations'), f"{overview['avg_citations']:.1f}")
            with col8:
                st.metric(get_text('open_access'), f"{overview['open_access_percent']:.1f}%")
            with col9:
                st.metric(get_text('active_years'), overview['active_years'])
            with col10:
                st.metric(get_text('unique_authors'), overview['unique_authors'])
            with col11:
                st.metric(get_text('unique_countries'), overview['unique_countries'])
            with col12:
                st.metric(get_text('total_citing_works'), overview['total_citing_works'])
            
            col13, col14, col15, col16, col17 = st.columns(5)
            with col13:
                st.metric(get_text('unique_citing_journals'), overview['unique_citing_journals'])
            with col14:
                st.metric(get_text('avg_authors_per_paper'), f"{overview['avg_authors_per_paper']:.1f}")
            with col15:
                st.metric(get_text('avg_affiliations_per_paper'), f"{overview['avg_affiliations_per_paper']:.1f}")
            with col16:
                st.metric(get_text('avg_countries_per_paper'), f"{overview['avg_countries_per_paper']:.1f}")
            with col17:
                st.metric(get_text('international_collaboration_rate'), f"{overview['international_collaboration_rate']:.1f}%")
            
            # Open Access Breakdown
            st.markdown(f"#### {get_text('open_access_breakdown')}")
            oa_breakdown = overview.get('open_access_breakdown', {})
            oa_cols = st.columns(6)
            oa_labels = ['gold', 'hybrid', 'green', 'bronze', 'closed', 'unknown']
            oa_display = [get_text('gold'), get_text('hybrid'), get_text('green'), get_text('bronze'), get_text('closed'), get_text('unknown')]
            for i, (key, label) in enumerate(zip(oa_labels, oa_display)):
                with oa_cols[i]:
                    st.metric(label, oa_breakdown.get(key, 0))
        
        with tab2:
            st.markdown(f"### {get_text('most_cited_publications')}")
            
            most_cited_df = pd.DataFrame(metrics['most_cited'])
            st.dataframe(most_cited_df, use_container_width=True, hide_index=True)
        
        with tab3:
            st.markdown(f"### {get_text('author_analysis')}")
            
            # Top Authors
            st.markdown(f"#### {get_text('top_authors')}")
            authors_df = pd.DataFrame(metrics['authors']['top_authors'])
            st.dataframe(authors_df, use_container_width=True, hide_index=True)
            
            # Top Affiliations
            st.markdown(f"#### {get_text('top_affiliations')}")
            aff_df = pd.DataFrame(metrics['affiliations']['top_affiliations'], columns=['Affiliation', 'Count'])
            st.dataframe(aff_df, use_container_width=True, hide_index=True)
            
            # Geographic Analysis
            st.markdown(f"#### {get_text('geographic_analysis')}")
            
            geo = metrics['geography']
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**{get_text('geography_type_1')}**")
                st.caption(get_text('geography_type_1_desc'))
                geo1_df = pd.DataFrame(list(geo['type1_unique_countries_per_pub'].items()), columns=['Country', 'Count'])
                st.dataframe(geo1_df, use_container_width=True, hide_index=True)
            
            with col2:
                st.markdown(f"**{get_text('geography_type_2')}**")
                st.caption(get_text('geography_type_2_desc'))
                geo2_df = pd.DataFrame(list(geo['type2_authors_per_country'].items()), columns=['Country', 'Count'])
                st.dataframe(geo2_df, use_container_width=True, hide_index=True)
            
            col3, col4 = st.columns(2)
            with col3:
                st.markdown(f"**{get_text('geography_type_3')}**")
                st.caption(get_text('geography_type_3_desc'))
                st.metric(get_text('single_country'), geo['single_country_count'])
                st.metric(get_text('international_collab'), geo['international_count'])
            
            with col4:
                st.markdown(f"**{get_text('collaboration_couples')}**")
                st.caption(get_text('collaboration_couples_desc'))
                couples_df = pd.DataFrame(
                    [(f"{c1} + {c2}", count) for (c1, c2), count in list(geo['collaboration_couples'].items())[:15]],
                    columns=['Country Pair', 'Count']
                )
                st.dataframe(couples_df, use_container_width=True, hide_index=True)
        
        with tab4:
            st.markdown(f"### {get_text('citation_analysis')}")
            
            # Citation dynamics
            st.markdown(f"#### {get_text('citation_dynamics')}")
            citation_data = metrics['citation_dynamics']
            
            # Yearly dynamics chart data
            yearly_data = []
            for pub_year, cite_years in citation_data['yearly_matrix'].items():
                for cite_year, count in cite_years.items():
                    yearly_data.append({'Publication Year': pub_year, 'Citation Year': cite_year, 'Count': count})
            
            if yearly_data:
                df_yearly = pd.DataFrame(yearly_data)
                st.dataframe(df_yearly, use_container_width=True)
            
            # Cumulative
            st.markdown(f"#### {get_text('cumulative_citations')}")
            cum_df = pd.DataFrame(list(citation_data['cumulative'].items()), columns=['Year', 'Cumulative Citations'])
            st.dataframe(cum_df, use_container_width=True, hide_index=True)
            
            # Heatmap
            st.markdown(f"#### {get_text('citation_network')}")
            heatmap_data = citation_data['heatmap_data']
            if heatmap_data:
                heatmap_df = pd.DataFrame(heatmap_data)
                # Pivot for heatmap
                heatmap_pivot = heatmap_df.pivot(index='publication_year', columns='citation_year', values='citations_count').fillna(0)
                st.dataframe(heatmap_pivot, use_container_width=True)
        
        with tab5:
            st.markdown(f"### {get_text('citing_works_analysis')}")
            
            citing = metrics['citing_works']
            
            col1, col2, col3, col4, col5, col6 = st.columns(6)
            with col1:
                st.metric(get_text('total_citing_works'), citing['total_citing_works'])
            with col2:
                st.metric(get_text('unique_citing_authors'), citing['unique_authors'])
            with col3:
                st.metric(get_text('unique_citing_affiliations'), citing['unique_affiliations'])
            with col4:
                st.metric(get_text('unique_citing_countries'), citing['unique_countries'])
            with col5:
                st.metric(get_text('unique_citing_journals'), citing['unique_journals'])
            with col6:
                st.metric(get_text('unique_citing_publishers'), citing['unique_publishers'])
            
            st.markdown(f"#### {get_text('top_citing_authors')}")
            citing_authors_df = pd.DataFrame(citing['top_authors'], columns=['Author', 'Count'])
            st.dataframe(citing_authors_df, use_container_width=True, hide_index=True)
            
            st.markdown(f"#### {get_text('top_citing_journals')}")
            citing_journals_df = pd.DataFrame(citing['top_journals'], columns=['Journal', 'Count'])
            st.dataframe(citing_journals_df, use_container_width=True, hide_index=True)
            
            st.markdown(f"#### {get_text('top_citing_countries')}")
            citing_countries_df = pd.DataFrame(citing['top_countries'], columns=['Country', 'Count'])
            st.dataframe(citing_countries_df, use_container_width=True, hide_index=True)
        
        with tab6:
            st.markdown(f"### {get_text('topics_analysis')}")
            
            topics = metrics['topics']
            
            st.markdown(f"**{get_text('total_topics')}:** {topics['total_topics']}")
            st.markdown(f"**{get_text('analyzed_count')}:** {topics['pub_topics_count']}")
            st.markdown(f"**{get_text('citing_count')}:** {topics['cite_topics_count']}")
            
            topics_df = pd.DataFrame(topics['topics'])
            st.dataframe(topics_df, use_container_width=True, hide_index=True)
        
        with tab7:
            st.markdown(f"### {get_text('detailed_citations')}")
            
            detailed = metrics['detailed_citations']
            if detailed:
                for pub_id, data in detailed.items():
                    with st.expander(f"{data['title']} ({data['year']}) - {data['total_citations']} citations"):
                        st.markdown(f"**DOI:** {data['doi']}")
                        st.markdown(f"**Total Citations:** {data['total_citations']}")
                        st.markdown("---")
                        for cite in data['citations']:
                            st.markdown(f"**{cite['citing_title']}**")
                            st.markdown(f"- Journal: {cite['citing_journal']} | Year: {cite['citing_year']} | Lag: {cite['citation_lag']} years")
                            st.markdown(f"- Authors: {', '.join(cite['citing_authors'][:3])}")
                            st.markdown(f"- Countries: {', '.join(cite['citing_countries'][:3])}")
                            st.markdown(f"- DOI: {cite['citing_doi']}")
                            st.markdown("---")
            else:
                st.info("No citations found")
        
        with tab8:
            st.markdown(f"### {get_text('all_publications')}")
            
            all_pubs = metrics['all_publications']
            all_pubs_df = pd.DataFrame(all_pubs)
            st.dataframe(all_pubs_df, use_container_width=True, hide_index=True)
        
        with tab9:
            st.markdown(f"### {get_text('export_report')}")
            
            # Generate HTML report
            if st.button(get_text('download_html'), type="primary"):
                with st.spinner(get_text('generating_report')):
                    html_report = generate_html_report(
                        data,
                        metrics,
                        st.session_state.language,
                        st.session_state.primary_color,
                        st.session_state.secondary_color
                    )
                    
                    # Generate filename
                    issn_clean = issn.replace('-', '')
                    file_name = f"journal_metrics_{issn_clean}_{datetime.now().strftime('%Y%m%d')}.html"
                    
                    st.download_button(
                        label="💾 Download HTML Report",
                        data=html_report.encode('utf-8'),
                        file_name=file_name,
                        mime="text/html"
                    )
            
            # Text export
            st.markdown(f"#### {get_text('text_export')}")
            
            # Build text export
            overview = metrics['overview']
            text_export = f"""
=== JOURNAL METRICS ANALYZER ===
Generated: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}

=== OVERVIEW ===
Total Publications: {overview['total_publications']}
Total Citations: {overview['total_citations']}
h-index: {overview['h_index']}
g-index: {overview['g_index']}
i10-index: {overview['i10_index']}
i100-index: {overview['i100_index']}
Avg Citations: {overview['avg_citations']:.1f}
Open Access: {overview['open_access_percent']:.1f}%
Active Years: {overview['active_years']}
Unique Authors: {overview['unique_authors']}
Unique Countries: {overview['unique_countries']}
Total Citing Works: {overview['total_citing_works']}
Unique Citing Journals: {overview['unique_citing_journals']}
Avg Authors/Paper: {overview['avg_authors_per_paper']:.1f}
Avg Affiliations/Paper: {overview['avg_affiliations_per_paper']:.1f}
Avg Countries/Paper: {overview['avg_countries_per_paper']:.1f}
International Collaboration Rate: {overview['international_collaboration_rate']:.1f}%

=== MOST CITED PUBLICATIONS (TOP 10) ===
"""
            for pub in metrics['most_cited'][:10]:
                text_export += f"{pub['rank']}. {pub['title']} ({pub['year']}) - {pub['citations']} citations\n"
            
            text_export += f"\n=== TOP AUTHORS (TOP 10) ===\n"
            for author in metrics['authors']['top_authors'][:10]:
                text_export += f"{author['display_name']} - {author['publication_count']} publications, {author['citation_count']} citations\n"
            
            text_export += f"\n=== TOTAL CITING WORKS ===\n{metrics['citing_works']['total_citing_works']}\n"
            text_export += f"Unique Citing Journals: {metrics['citing_works']['unique_journals']}\n"
            
            st.text_area(get_text('text_export'), text_export, height=400)
            
            if st.button(get_text('copy_to_clipboard')):
                st.success(get_text('copied'))
    
    else:
        st.info(get_text('run_analysis_first'))

if __name__ == "__main__":
    main()
