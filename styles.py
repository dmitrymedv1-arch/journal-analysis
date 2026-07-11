"""
styles.py - Complete styles module for Journal Metrics Analyzer
Contains all CSS, color utilities, and theme management functions
"""

import colorsys
from typing import Dict, List, Tuple, Optional, Set, Any
import streamlit as st

# ======================== COLOR UTILITIES ========================

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

def inject_color_placeholders(css_string: str, primary_color: str, secondary_color: str) -> str:
    """
    Inject color placeholders into CSS string
    Replaces {{primary}} and {{secondary}} with actual colors
    """
    css_string = css_string.replace('{{primary}}', primary_color)
    css_string = css_string.replace('{{secondary}}', secondary_color)
    return css_string

# ======================== THEME MANAGEMENT ========================

def get_available_themes() -> List[str]:
    """Get list of all available theme names"""
    return [
        'default',
        'glassmorphism',
        'neon_dark',
        'aurora',
        'brutalist',
        'minimalist_white',
        'ocean_deep',
        'cosmic',
        'terrazzo',
        'modern_cards',
        'duotone',
        'morphing'
    ]

def get_theme_display_name(theme_key: str) -> str:
    """Get display name for a theme"""
    theme_names = {
        'default': 'Gradient Classic',
        'glassmorphism': 'Glassmorphism',
        'neon_dark': 'Neon Dark',
        'aurora': 'Aurora Borealis',
        'brutalist': 'Brutalist',
        'minimalist_white': 'Minimalist White',
        'ocean_deep': 'Ocean Deep',
        'cosmic': 'Cosmic',
        'terrazzo': 'Terrazzo',
        'modern_cards': 'Modern Cards',
        'duotone': 'Duotone',
        'morphing': 'Morphing'
    }
    return theme_names.get(theme_key, theme_key)

def get_theme_info(theme_key: str) -> Dict[str, Any]:
    """Get information about a theme"""
    theme_info = {
        'default': {
            'name': 'Gradient Classic',
            'description': 'Clean gradient design with subtle shadows',
            'uses_primary': True,
            'uses_secondary': True
        },
        'glassmorphism': {
            'name': 'Glassmorphism',
            'description': 'Frosted glass effect with blur and transparency',
            'uses_primary': True,
            'uses_secondary': True
        },
        'neon_dark': {
            'name': 'Neon Dark',
            'description': 'Dark theme with neon glowing accents',
            'uses_primary': True,
            'uses_secondary': True
        },
        'aurora': {
            'name': 'Aurora Borealis',
            'description': 'Northern lights inspired gradient theme',
            'uses_primary': True,
            'uses_secondary': True
        },
        'brutalist': {
            'name': 'Brutalist',
            'description': 'Bold, raw, and minimal with sharp edges',
            'uses_primary': True,
            'uses_secondary': True
        },
        'minimalist_white': {
            'name': 'Minimalist White',
            'description': 'Clean white theme with subtle accents',
            'uses_primary': True,
            'uses_secondary': False
        },
        'ocean_deep': {
            'name': 'Ocean Deep',
            'description': 'Deep blue ocean inspired theme',
            'uses_primary': True,
            'uses_secondary': True
        },
        'cosmic': {
            'name': 'Cosmic',
            'description': 'Space and galaxy inspired theme',
            'uses_primary': True,
            'uses_secondary': True
        },
        'terrazzo': {
            'name': 'Terrazzo',
            'description': 'Colorful speckled terrazzo design',
            'uses_primary': True,
            'uses_secondary': True
        },
        'modern_cards': {
            'name': 'Modern Cards',
            'description': 'Card-based design with clean shadows',
            'uses_primary': True,
            'uses_secondary': True
        },
        'duotone': {
            'name': 'Duotone',
            'description': 'Two-tone color scheme with contrast',
            'uses_primary': True,
            'uses_secondary': True
        },
        'morphing': {
            'name': 'Morphing',
            'description': 'Smooth morphing gradient transitions',
            'uses_primary': True,
            'uses_secondary': True
        }
    }
    return theme_info.get(theme_key, theme_info['default'])

def theme_uses_primary(theme_key: str) -> bool:
    """Check if theme uses primary color"""
    info = get_theme_info(theme_key)
    return info.get('uses_primary', True)

def theme_uses_secondary(theme_key: str) -> bool:
    """Check if theme uses secondary color"""
    info = get_theme_info(theme_key)
    return info.get('uses_secondary', True)

# ======================== REFERENCE COLOR STYLES ========================

REFERENCE_COLORS_FULL = """
/* Full color coding - background + border */
.retracted-reference {
    background: #f8d7da !important;
    border-left: 4px solid #dc3545 !important;
}
.suspicious-reference {
    background: #fff3cd !important;
    border-left: 4px solid #ffc107 !important;
}
.duplicate-reference {
    background: #d1ecf1 !important;
    border-left: 4px solid #17a2b8 !important;
}
.ebook-reference {
    background: #d4f1e9 !important;
    border-left: 4px solid #0e6b5e !important;
}
.proceedings-reference {
    background: #fff2c9 !important;
    border-left: 4px solid #b26b00 !important;
}
.repository-reference {
    background: #e2d5f8 !important;
    border-left: 4px solid #5e2a9e !important;
}
.preprint-reference {
    background: #e2d5f8 !important;
    border-left: 4px solid #5e2a9e !important;
}
.normal-article {
    background: #ffffff !important;
    border-left: 4px solid #667eea !important;
}
.notfound-reference {
    background: #f5f5f5 !important;
    border-left: 4px solid #999 !important;
}
"""

REFERENCE_COLORS_BORDER_ONLY = """
/* Border only color coding */
.retracted-reference {
    border-left: 4px solid #dc3545 !important;
}
.suspicious-reference {
    border-left: 4px solid #ffc107 !important;
}
.duplicate-reference {
    border-left: 4px solid #17a2b8 !important;
}
.ebook-reference {
    border-left: 4px solid #0e6b5e !important;
}
.proceedings-reference {
    border-left: 4px solid #b26b00 !important;
}
.repository-reference {
    border-left: 4px solid #5e2a9e !important;
}
.preprint-reference {
    border-left: 4px solid #5e2a9e !important;
}
.normal-article {
    border-left: 4px solid #667eea !important;
}
.notfound-reference {
    border-left: 4px solid #999 !important;
}
"""

REFERENCE_COLORS_ICONS = """
/* Icon only color coding */
.retracted-reference .badge-danger { display: inline-block; }
.suspicious-reference .badge-warning { display: inline-block; }
.duplicate-reference .badge-info { display: inline-block; }
.ebook-reference .badge-book { display: inline-block; }
.proceedings-reference .badge-proceedings { display: inline-block; }
.repository-reference .badge-repository { display: inline-block; }
.preprint-reference .badge-repository { display: inline-block; }
"""

REFERENCE_COLORS_THEMED = """
/* Themed color coding - follows primary color */
.retracted-reference {
    border-left: 4px solid var(--primary) !important;
    background: var(--hover-light) !important;
}
.suspicious-reference {
    border-left: 4px solid var(--secondary) !important;
    background: var(--hover-light) !important;
}
.duplicate-reference {
    border-left: 4px solid var(--accent-1) !important;
}
.ebook-reference {
    border-left: 4px solid var(--accent-2) !important;
}
.proceedings-reference {
    border-left: 4px solid var(--secondary) !important;
}
.repository-reference {
    border-left: 4px solid var(--primary) !important;
}
.preprint-reference {
    border-left: 4px solid var(--primary) !important;
}
.normal-article {
    border-left: 4px solid var(--primary-light) !important;
}
.notfound-reference {
    border-left: 4px solid #999 !important;
}
"""

REFERENCE_COLORS_TEXT = """
/* Text only color coding */
.retracted-reference .rank-name { color: #dc3545 !important; }
.suspicious-reference .rank-name { color: #ffc107 !important; }
.duplicate-reference .rank-name { color: #17a2b8 !important; }
.ebook-reference .rank-name { color: #0e6b5e !important; }
.proceedings-reference .rank-name { color: #b26b00 !important; }
.repository-reference .rank-name { color: #5e2a9e !important; }
.preprint-reference .rank-name { color: #5e2a9e !important; }
"""

def get_reference_color_style(style_name: str = 'full') -> str:
    """
    Get CSS for reference color coding style
    
    Args:
        style_name: 'full', 'border_only', 'icons', 'themed', 'text'
    
    Returns:
        CSS string for the selected style
    """
    styles = {
        'full': REFERENCE_COLORS_FULL,
        'border_only': REFERENCE_COLORS_BORDER_ONLY,
        'icons': REFERENCE_COLORS_ICONS,
        'themed': REFERENCE_COLORS_THEMED,
        'text': REFERENCE_COLORS_TEXT
    }
    return styles.get(style_name, REFERENCE_COLORS_FULL)

# ======================== THEME CSS GENERATORS ========================

def generate_theme_css(theme_name: str, primary_color: str, secondary_color: str) -> str:
    """
    Generate complete CSS for a theme
    
    Args:
        theme_name: Name of the theme
        primary_color: Primary color hex
        secondary_color: Secondary color hex
    
    Returns:
        CSS string for the theme
    """
    
    # Base CSS variables
    css_vars = generate_css_variables(primary_color, secondary_color)
    
    # Common styles applied to all themes
    base_theme_css = """
    :root {
        --primary: {primary};
        --secondary: {secondary};
        --primary-light: {primary_light};
        --secondary-light: {secondary_light};
        --primary-contrast: {primary_contrast};
        --secondary-contrast: {secondary_contrast};
        --gradient-start: {gradient_start};
        --gradient-end: {gradient_end};
        --accent-1: {accent_1};
        --accent-2: {accent_2};
        --hover-light: {hover_light};
    }
    """.format(
        primary=css_vars['--primary-color'],
        secondary=css_vars['--secondary-color'],
        primary_light=css_vars['--primary-light'],
        secondary_light=css_vars['--secondary-light'],
        primary_contrast=css_vars['--primary-contrast'],
        secondary_contrast=css_vars['--secondary-contrast'],
        gradient_start=css_vars['--gradient-start'],
        gradient_end=css_vars['--gradient-end'],
        accent_1=css_vars['--accent-1'],
        accent_2=css_vars['--accent-2'],
        hover_light=css_vars['--hover-light']
    )
    
    # Theme-specific CSS
    theme_css = {
        'default': """
        .stApp {
            background: linear-gradient(135deg, 
                rgba({r1}, {g1}, {b1}, 0.05) 0%,
                rgba({r2}, {g2}, {b2}, 0.08) 100%);
        }
        .section {
            background: rgba(255,255,255,0.95);
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }
        .stat-card {
            background: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.06);
        }
        """.format(
            r1=hex_to_rgb(primary_color)[0],
            g1=hex_to_rgb(primary_color)[1],
            b1=hex_to_rgb(primary_color)[2],
            r2=hex_to_rgb(secondary_color)[0],
            g2=hex_to_rgb(secondary_color)[1],
            b2=hex_to_rgb(secondary_color)[2]
        ),
        
        'glassmorphism': """
        .stApp {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        .section {
            background: rgba(255,255,255,0.15);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid rgba(255,255,255,0.2);
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        }
        .section-title {
            border-bottom-color: rgba(255,255,255,0.3);
            color: white;
        }
        .stat-card {
            background: rgba(255,255,255,0.12);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.15);
        }
        .stat-label {
            color: rgba(255,255,255,0.8);
        }
        .stat-number {
            background: linear-gradient(135deg, #ffffff 0%, rgba(255,255,255,0.7) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .rank-item {
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(5px);
            border-left-color: rgba(255,255,255,0.3);
        }
        .rank-name, .rank-count {
            color: white;
        }
        table {
            background: rgba(255,255,255,0.05);
        }
        th {
            background: rgba(255,255,255,0.2);
            backdrop-filter: blur(5px);
            color: white;
        }
        td {
            color: rgba(255,255,255,0.9);
            border-bottom-color: rgba(255,255,255,0.1);
        }
        tr:hover {
            background: rgba(255,255,255,0.08);
        }
        .footer {
            color: rgba(255,255,255,0.6);
            border-top-color: rgba(255,255,255,0.1);
        }
        """,
        
        'neon_dark': """
        .stApp {
            background: #0a0a0f;
        }
        .section {
            background: rgba(20,20,30,0.9);
            border: 1px solid rgba(102,126,234,0.2);
            box-shadow: 0 0 30px rgba(102,126,234,0.05);
        }
        .section-title {
            border-bottom-color: var(--primary);
            color: #fff;
            text-shadow: 0 0 20px rgba(102,126,234,0.3);
        }
        .stat-card {
            background: rgba(30,30,50,0.8);
            border: 1px solid rgba(102,126,234,0.15);
            box-shadow: 0 0 20px rgba(102,126,234,0.05);
        }
        .stat-label {
            color: rgba(255,255,255,0.7);
        }
        .stat-number {
            text-shadow: 0 0 30px rgba(102,126,234,0.3);
        }
        .rank-item {
            background: rgba(30,30,50,0.6);
            border-left-color: var(--primary);
        }
        .rank-name, .rank-count {
            color: rgba(255,255,255,0.9);
        }
        .rank-name {
            color: #fff;
        }
        table {
            background: rgba(20,20,30,0.5);
        }
        th {
            background: rgba(102,126,234,0.2);
            color: #fff;
        }
        td {
            color: rgba(255,255,255,0.8);
            border-bottom-color: rgba(255,255,255,0.05);
        }
        tr:hover {
            background: rgba(102,126,234,0.05);
        }
        .footer {
            color: rgba(255,255,255,0.4);
            border-top-color: rgba(255,255,255,0.05);
        }
        .badge-info {
            background: rgba(102,126,234,0.2);
            color: #a8b5f0;
        }
        .badge-success {
            background: rgba(0,255,100,0.15);
            color: #66ff99;
        }
        .badge-warning {
            background: rgba(255,200,0,0.15);
            color: #ffdd44;
        }
        .badge-danger {
            background: rgba(255,50,50,0.15);
            color: #ff6666;
        }
        .concept-card {
            background: rgba(30,30,50,0.6);
            border-color: rgba(102,126,234,0.2);
        }
        .concept-name {
            color: #a8b5f0;
        }
        .progress-bar {
            background: rgba(255,255,255,0.05);
        }
        .progress-fill {
            background: linear-gradient(90deg, var(--primary), var(--secondary));
            box-shadow: 0 0 20px rgba(102,126,234,0.3);
        }
        .rank-item .rank-number {
            color: var(--primary);
            text-shadow: 0 0 20px rgba(102,126,234,0.3);
        }
        """,
        
        'aurora': """
        .stApp {
            background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
        }
        .section {
            background: rgba(255,255,255,0.05);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.08);
        }
        .section-title {
            border-bottom-color: rgba(255,255,255,0.15);
            color: #e0d7ff;
        }
        .stat-card {
            background: rgba(255,255,255,0.04);
            border: 1px solid rgba(255,255,255,0.06);
        }
        .stat-label {
            color: rgba(224,215,255,0.7);
        }
        .stat-number {
            background: linear-gradient(135deg, #a78bfa 0%, #7c3aed 50%, #4f46e5 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .rank-item {
            background: rgba(255,255,255,0.03);
            border-left-color: #7c3aed;
        }
        .rank-name {
            color: #e0d7ff;
        }
        .rank-count {
            color: rgba(224,215,255,0.7);
        }
        th {
            background: linear-gradient(135deg, rgba(167,139,250,0.2), rgba(124,58,237,0.2));
            color: #e0d7ff;
        }
        td {
            color: rgba(224,215,255,0.8);
            border-bottom-color: rgba(255,255,255,0.05);
        }
        tr:hover {
            background: rgba(167,139,250,0.05);
        }
        .footer {
            color: rgba(224,215,255,0.4);
            border-top-color: rgba(255,255,255,0.05);
        }
        .progress-bar {
            background: rgba(255,255,255,0.05);
        }
        .progress-fill {
            background: linear-gradient(90deg, #a78bfa, #7c3aed, #4f46e5);
        }
        """,
        
        'brutalist': """
        .stApp {
            background: #ffffff;
        }
        .section {
            background: #ffffff;
            border: 3px solid #000000;
            border-radius: 0px;
            box-shadow: 8px 8px 0px rgba(0,0,0,0.15);
        }
        .section-title {
            border-bottom: 4px solid #000000;
            color: #000000;
            font-weight: 900;
            text-transform: uppercase;
            letter-spacing: -0.5px;
        }
        .stat-card {
            background: #ffffff;
            border: 2px solid #000000;
            border-radius: 0px;
            box-shadow: 4px 4px 0px rgba(0,0,0,0.1);
        }
        .stat-number {
            font-weight: 900;
            color: #000000;
            background: none;
            -webkit-text-fill-color: #000000;
        }
        .stat-label {
            color: #333333;
            font-weight: 700;
            text-transform: uppercase;
            font-size: 11px;
        }
        .rank-item {
            border-left: 6px solid #000000;
            border-radius: 0px;
            background: #ffffff;
        }
        .rank-name {
            font-weight: 700;
        }
        th {
            background: #000000;
            color: #ffffff;
            text-transform: uppercase;
            font-weight: 900;
            border-radius: 0px;
        }
        td {
            border-bottom: 2px solid #e0e0e0;
        }
        tr:hover {
            background: #f0f0f0;
        }
        .footer {
            border-top: 4px solid #000000;
            color: #333333;
            font-weight: 700;
        }
        .badge-info {
            background: #000000;
            color: #ffffff;
            border-radius: 0px;
        }
        .badge-success {
            background: #00aa00;
            color: #ffffff;
            border-radius: 0px;
        }
        .badge-warning {
            background: #ffaa00;
            color: #000000;
            border-radius: 0px;
        }
        .badge-danger {
            background: #ff0000;
            color: #ffffff;
            border-radius: 0px;
        }
        .progress-bar {
            background: #e0e0e0;
            border-radius: 0px;
            height: 8px;
        }
        .progress-fill {
            background: #000000;
            border-radius: 0px;
        }
        .concept-card {
            border: 2px solid #000000;
            border-radius: 0px;
            background: #ffffff;
        }
        .concept-name {
            color: #000000;
            font-weight: 900;
        }
        """,
        
        'minimalist_white': """
        .stApp {
            background: #ffffff;
        }
        .section {
            background: #ffffff;
            border: none;
            box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        }
        .section-title {
            border-bottom: 2px solid #e0e0e0;
            color: #1a1a1a;
            font-weight: 600;
        }
        .stat-card {
            background: #fafafa;
            border: none;
            box-shadow: 0 1px 2px rgba(0,0,0,0.02);
        }
        .stat-number {
            color: #1a1a1a;
            background: none;
            -webkit-text-fill-color: #1a1a1a;
            font-weight: 300;
        }
        .stat-label {
            color: #888888;
            font-weight: 400;
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .rank-item {
            border-left: 2px solid #e0e0e0;
            background: #ffffff;
            box-shadow: none;
        }
        .rank-item:hover {
            background: #fafafa;
            transform: none;
        }
        .rank-name {
            color: #1a1a1a;
            font-weight: 400;
        }
        .rank-count {
            color: #888888;
        }
        th {
            background: #f5f5f5;
            color: #1a1a1a;
            font-weight: 600;
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        td {
            border-bottom: 1px solid #f0f0f0;
            color: #333333;
        }
        tr:hover {
            background: #fafafa;
        }
        .footer {
            border-top: 1px solid #f0f0f0;
            color: #999999;
        }
        .progress-bar {
            background: #f0f0f0;
            height: 4px;
        }
        .progress-fill {
            background: #333333;
        }
        .badge-info {
            background: #f0f0f0;
            color: #333333;
        }
        .badge-success {
            background: #e8f5e9;
            color: #2e7d32;
        }
        .badge-warning {
            background: #fff3e0;
            color: #e65100;
        }
        .badge-danger {
            background: #fce4ec;
            color: #c62828;
        }
        """,
        
        'ocean_deep': """
        .stApp {
            background: linear-gradient(135deg, #0c2340 0%, #1a4a7a 50%, #0c2340 100%);
        }
        .section {
            background: rgba(255,255,255,0.06);
            backdrop-filter: blur(8px);
            border: 1px solid rgba(255,255,255,0.06);
        }
        .section-title {
            border-bottom-color: rgba(100,180,255,0.2);
            color: #b8d8f0;
        }
        .stat-card {
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.05);
        }
        .stat-label {
            color: rgba(184,216,240,0.7);
        }
        .stat-number {
            background: linear-gradient(135deg, #64b5f6 0%, #1a8cff 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .rank-item {
            background: rgba(255,255,255,0.03);
            border-left-color: #1a8cff;
        }
        .rank-name {
            color: #b8d8f0;
        }
        .rank-count {
            color: rgba(184,216,240,0.7);
        }
        th {
            background: rgba(26,140,255,0.15);
            color: #b8d8f0;
        }
        td {
            color: rgba(184,216,240,0.8);
            border-bottom-color: rgba(255,255,255,0.05);
        }
        tr:hover {
            background: rgba(26,140,255,0.05);
        }
        .footer {
            color: rgba(184,216,240,0.4);
            border-top-color: rgba(255,255,255,0.05);
        }
        .progress-bar {
            background: rgba(255,255,255,0.05);
        }
        .progress-fill {
            background: linear-gradient(90deg, #1a8cff, #64b5f6);
        }
        """,
        
        'cosmic': """
        .stApp {
            background: radial-gradient(ellipse at center, #1a0a2e 0%, #0d0d2b 50%, #000000 100%);
        }
        .section {
            background: rgba(20,10,40,0.8);
            border: 1px solid rgba(100,50,200,0.15);
            box-shadow: 0 0 40px rgba(100,50,200,0.05);
        }
        .section-title {
            border-bottom-color: rgba(150,100,255,0.2);
            color: #c8b8f0;
        }
        .stat-card {
            background: rgba(30,15,50,0.6);
            border: 1px solid rgba(150,100,255,0.08);
        }
        .stat-label {
            color: rgba(200,184,240,0.7);
        }
        .stat-number {
            background: linear-gradient(135deg, #a78bfa 0%, #7c3aed 40%, #6d28d9 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            text-shadow: 0 0 40px rgba(124,58,237,0.2);
        }
        .rank-item {
            background: rgba(30,15,50,0.4);
            border-left-color: #7c3aed;
        }
        .rank-name {
            color: #c8b8f0;
        }
        .rank-count {
            color: rgba(200,184,240,0.7);
        }
        th {
            background: rgba(124,58,237,0.15);
            color: #c8b8f0;
        }
        td {
            color: rgba(200,184,240,0.8);
            border-bottom-color: rgba(255,255,255,0.03);
        }
        tr:hover {
            background: rgba(124,58,237,0.05);
        }
        .footer {
            color: rgba(200,184,240,0.3);
            border-top-color: rgba(255,255,255,0.03);
        }
        .progress-bar {
            background: rgba(255,255,255,0.03);
        }
        .progress-fill {
            background: linear-gradient(90deg, #7c3aed, #a78bfa);
            box-shadow: 0 0 20px rgba(124,58,237,0.3);
        }
        .badge-info {
            background: rgba(124,58,237,0.2);
            color: #a78bfa;
        }
        """,
        
        'terrazzo': """
        .stApp {
            background: #f5f0eb;
            background-image: 
                radial-gradient(circle at 10% 20%, rgba(230,200,180,0.3) 0%, transparent 50%),
                radial-gradient(circle at 80% 80%, rgba(200,180,160,0.3) 0%, transparent 50%),
                radial-gradient(circle at 40% 60%, rgba(220,190,170,0.2) 0%, transparent 40%);
        }
        .section {
            background: rgba(255,252,248,0.9);
            border: none;
            box-shadow: 0 4px 16px rgba(0,0,0,0.04);
        }
        .section-title {
            border-bottom-color: #d4c5b5;
            color: #4a3728;
        }
        .stat-card {
            background: rgba(255,252,248,0.8);
            border: 1px solid rgba(200,180,160,0.15);
        }
        .stat-label {
            color: #8a7a6a;
        }
        .stat-number {
            color: #4a3728;
            background: none;
            -webkit-text-fill-color: #4a3728;
        }
        .rank-item {
            background: rgba(255,252,248,0.7);
            border-left-color: #b8a090;
        }
        .rank-name {
            color: #4a3728;
        }
        .rank-count {
            color: #8a7a6a;
        }
        th {
            background: #e8ddd0;
            color: #4a3728;
        }
        td {
            border-bottom-color: #ece5dc;
            color: #5a4a3a;
        }
        tr:hover {
            background: #f5efe8;
        }
        .footer {
            color: #b8a8a0;
            border-top-color: #ece5dc;
        }
        .progress-bar {
            background: #ece5dc;
        }
        .progress-fill {
            background: linear-gradient(90deg, #b8a090, #8a7a6a);
        }
        """,
        
        'modern_cards': """
        .stApp {
            background: #f0f2f5;
        }
        .section {
            background: #ffffff;
            border: none;
            box-shadow: 0 4px 20px rgba(0,0,0,0.04);
            border-radius: 16px;
        }
        .section-title {
            border-bottom: none;
            color: #1a1a2e;
            font-weight: 700;
        }
        .stat-card {
            background: #f8f9fc;
            border: none;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.02);
        }
        .stat-number {
            font-weight: 700;
        }
        .stat-label {
            color: #6c757d;
            font-weight: 500;
        }
        .rank-item {
            background: #f8f9fc;
            border-left-color: var(--primary);
            border-radius: 8px;
            box-shadow: 0 1px 4px rgba(0,0,0,0.02);
        }
        th {
            background: #f8f9fc;
            color: #1a1a2e;
            font-weight: 600;
            border-bottom: 2px solid #e9ecef;
        }
        td {
            border-bottom-color: #f0f0f0;
        }
        tr:hover {
            background: #f8f9fc;
        }
        .progress-bar {
            background: #e9ecef;
            border-radius: 8px;
        }
        .progress-fill {
            border-radius: 8px;
        }
        .footer {
            border-top-color: #e9ecef;
            color: #6c757d;
        }
        """,
        
        'duotone': """
        .stApp {
            background: linear-gradient(135deg, 
                rgba({r1}, {g1}, {b1}, 0.05) 0%,
                rgba({r2}, {g2}, {b2}, 0.10) 100%);
        }
        .section {
            background: rgba(255,255,255,0.92);
            border: 2px solid rgba({r2}, {g2}, {b2}, 0.08);
        }
        .section-title {
            border-bottom-color: var(--secondary);
            color: var(--primary);
        }
        .stat-card {
            background: rgba({r1}, {g1}, {b1}, 0.04);
            border: 1px solid rgba({r2}, {g2}, {b2}, 0.06);
        }
        .stat-number {
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .stat-label {
            color: #555;
        }
        .rank-item {
            border-left-color: var(--secondary);
            background: rgba(255,255,255,0.8);
        }
        .rank-name {
            color: var(--primary);
        }
        .rank-count {
            color: #777;
        }
        th {
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
            color: white;
        }
        td {
            border-bottom-color: rgba({r2}, {g2}, {b2}, 0.08);
        }
        tr:hover {
            background: rgba({r1}, {g1}, {b1}, 0.04);
        }
        .footer {
            border-top-color: rgba({r2}, {g2}, {b2}, 0.1);
            color: #888;
        }
        .progress-bar {
            background: rgba({r2}, {g2}, {b2}, 0.1);
        }
        .progress-fill {
            background: linear-gradient(90deg, var(--primary), var(--secondary));
        }
        .badge-info {
            background: rgba({r1}, {g1}, {b1}, 0.1);
            color: var(--primary);
        }
        .badge-success {
            background: rgba(0,200,100,0.1);
            color: #2e7d32;
        }
        .badge-warning {
            background: rgba(255,180,0,0.1);
            color: #e65100;
        }
        .badge-danger {
            background: rgba(255,50,50,0.1);
            color: #c62828;
        }
        """.format(
            r1=hex_to_rgb(primary_color)[0],
            g1=hex_to_rgb(primary_color)[1],
            b1=hex_to_rgb(primary_color)[2],
            r2=hex_to_rgb(secondary_color)[0],
            g2=hex_to_rgb(secondary_color)[1],
            b2=hex_to_rgb(secondary_color)[2]
        ),
        
        'morphing': """
        .stApp {
            background: linear-gradient(135deg, 
                rgba({r1}, {g1}, {b1}, 0.03) 0%,
                rgba({r2}, {g2}, {b2}, 0.05) 25%,
                rgba({r1}, {g1}, {b1}, 0.03) 50%,
                rgba({r2}, {g2}, {b2}, 0.05) 75%,
                rgba({r1}, {g1}, {b1}, 0.03) 100%);
            background-size: 400% 400%;
            animation: morphGradient 15s ease infinite;
        }
        @keyframes morphGradient {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        .section {
            background: rgba(255,255,255,0.85);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
            box-shadow: 0 8px 32px rgba(0,0,0,0.04);
        }
        .section-title {
            border-bottom-color: rgba({r2}, {g2}, {b2}, 0.2);
            color: var(--primary);
        }
        .stat-card {
            background: rgba(255,255,255,0.5);
            backdrop-filter: blur(5px);
            border: 1px solid rgba(255,255,255,0.2);
        }
        .stat-number {
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 50%, var(--primary) 100%);
            background-size: 200% 200%;
            animation: shimmerText 4s ease infinite;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        @keyframes shimmerText {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        .stat-label {
            color: #666;
        }
        .rank-item {
            background: rgba(255,255,255,0.6);
            backdrop-filter: blur(3px);
            border-left-color: var(--secondary);
            transition: all 0.3s ease;
        }
        .rank-item:hover {
            transform: translateX(8px) scale(1.01);
            box-shadow: 0 4px 20px rgba(0,0,0,0.06);
        }
        th {
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
            background-size: 200% 200%;
            animation: shimmerText 4s ease infinite;
            color: white;
        }
        td {
            border-bottom-color: rgba(0,0,0,0.04);
        }
        tr:hover {
            background: rgba({r1}, {g1}, {b1}, 0.04);
        }
        .footer {
            border-top-color: rgba(0,0,0,0.06);
            color: #888;
        }
        .progress-bar {
            background: rgba(0,0,0,0.06);
            border-radius: 8px;
        }
        .progress-fill {
            background: linear-gradient(90deg, var(--primary), var(--secondary), var(--primary));
            background-size: 200% 100%;
            animation: shimmerText 3s ease infinite;
            border-radius: 8px;
        }
        """.format(
            r1=hex_to_rgb(primary_color)[0],
            g1=hex_to_rgb(primary_color)[1],
            b1=hex_to_rgb(primary_color)[2],
            r2=hex_to_rgb(secondary_color)[0],
            g2=hex_to_rgb(secondary_color)[1],
            b2=hex_to_rgb(secondary_color)[2]
        )
    }
    
    # Get theme-specific CSS or use default
    theme_css_str = theme_css.get(theme_name, theme_css['default'])
    
    # Combine base and theme CSS
    return base_theme_css + "\n" + theme_css_str

# ======================== STREAMLIT COLOR PREVIEW ========================

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

# ======================== APPLY THEME CSS ========================

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
    </style>
    """
    st.markdown(theme_css, unsafe_allow_html=True)
