#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
DASHBOARD VERVAL DATA KEMISKINAN KOTA BONTANG 2025
Dibuat oleh: Dinas Sosial dan Pemberdayaan Masyarakat Kota Bontang
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import os

# =============================================================================
# KONFIGURASI
# =============================================================================

FILE_CSV = "data_verval_kemiskinan.csv"
KOLOM_NOMOR_KK = "no_keluarga"
KOLOM_NIK = "nik"
KOLOM_INDIKATOR = ["ind_1", "ind_2", "ind_3", "ind_4", "ind_5", "ind_6", "ind_7", "ind_8"]

FONT_TITLE = 24
FONT_LABEL = 16
FONT_TICK = 14
FONT_LEGEND = 13
FONT_PIE_TEXT = 14

CHART_HEIGHT_PIE = 520
CHART_HEIGHT_BAR = 480
CHART_HEIGHT_RUMAH = 450

# =============================================================================
# FUNGSI FORMAT ANGKA INDONESIA
# =============================================================================

def format_angka_id(nilai, desimal=0):
    if pd.isna(nilai):
        return "-"
    if desimal > 0:
        formatted = f"{nilai:,.{desimal}f}"
    else:
        formatted = f"{int(nilai):,}"
    return formatted.replace(",", "TEMP").replace(".", ",").replace("TEMP", ".")

def format_persen_id(nilai, desimal=1):
    if pd.isna(nilai):
        return "-"
    formatted = f"{nilai:.{desimal}f}".replace(".", ",")
    return f"{formatted}%"

# =============================================================================
# LABEL MAPPING
# =============================================================================

LABEL_KECAMATAN = {
    'bontang_utara': 'BONTANG UTARA', 
    'bontang_selatan': 'BONTANG SELATAN', 
    'bontang_barat': 'BONTANG BARAT'
}

LABEL_KELURAHAN = {
    'api_api': 'API-API', 'belimbing': 'BELIMBING', 'berbas_pantai': 'BERBAS PANTAI',
    'berbas_tengah': 'BERBAS TENGAH', 'bontang_baru': 'BONTANG BARU', 'bontang_kuala': 'BONTANG KUALA',
    'bontang_lestari': 'BONTANG LESTARI', 'guntung': 'GUNTUNG', 'gunung_elai': 'GUNUNG ELAI',
    'gunung_telihan': 'GUNUNG TELIHAN', 'kanaan': 'KANAAN', 'lok tuan': 'LOK TUAN', 'lok_tuan': 'LOK TUAN',
    'satimpo': 'SATIMPO', 'tanjung_laut': 'TANJUNG LAUT', 'tanjung_laut_indah': 'TANJUNG LAUT INDAH',
    'Tanjung_laut': 'TANJUNG LAUT'
}

LABEL_INDIKATOR = {
    'ind_1': '1. KK Tidak Bekerja',
    'ind_2': '2. Khawatir Tidak Makan',
    'ind_3': '3. Peng. Makanan > Non-Makanan',
    'ind_4': '4. Tidak Beli Pakaian Setahun',
    'ind_5': '5. Lantai Tanah/Plester',
    'ind_6': '6. Dinding Non-Permanen',
    'ind_7': '7. Tidak Punya Jamban Sendiri',
    'ind_8': '8. Listrik 450W/Bukan Listrik'
}

LABEL_STATUS_KELUARGA = {
    1: 'Desil 1 (Sangat Miskin)', 2: 'Desil 2 (Miskin)', 3: 'Desil 3 (Hampir Miskin)',
    4: 'Desil 4 (Rentan Miskin)', 5: 'Lainnya',
    '1': 'Desil 1 (Sangat Miskin)', '2': 'Desil 2 (Miskin)', '3': 'Desil 3 (Hampir Miskin)',
    '4': 'Desil 4 (Rentan Miskin)', '5': 'Lainnya'
}

LABEL_LANTAI = {
    1: 'Marmer/Granit', 2: 'Keramik', 3: 'Parket/Vinil', 4: 'Ubin/Tegel',
    5: 'Kayu Kualitas Tinggi', 6: 'Semen/Bata Merah', 7: 'Bambu/Papan Rendah', 8: 'Tanah', 9: 'Lainnya',
    '1': 'Marmer/Granit', '2': 'Keramik', '3': 'Parket/Vinil', '4': 'Ubin/Tegel',
    '5': 'Kayu Kualitas Tinggi', '6': 'Semen/Bata Merah', '7': 'Bambu/Papan Rendah', '8': 'Tanah', '9': 'Lainnya'
}

LABEL_DINDING = {
    1: 'Tembok', 2: 'Plesteran Bambu', 3: 'Kayu/Gypsum',
    4: 'Anyaman Bambu', 5: 'Kayu Rendah', 6: 'Bambu', 7: 'Lainnya',
    '1': 'Tembok', '2': 'Plesteran Bambu', '3': 'Kayu/Gypsum',
    '4': 'Anyaman Bambu', '5': 'Kayu Rendah', '6': 'Bambu', '7': 'Lainnya'
}

LABEL_ATAP = {
    1: 'Beton', 2: 'Genteng', 3: 'Seng', 4: 'Asbes', 5: 'Bambu', 6: 'Kayu/Sirap',
    7: 'Jerami/Ijuk/Rumbia', 8: 'Lainnya',
    '1': 'Beton', '2': 'Genteng', '3': 'Seng', '4': 'Asbes', '5': 'Bambu', '6': 'Kayu/Sirap',
    '7': 'Jerami/Ijuk/Rumbia', '8': 'Lainnya'
}

LABEL_SUMBER_AIR = {
    '01': 'Air Kemasan Bermerk', '02': 'Air Isi Ulang', '03': 'Ledeng', '04': 'Sumur Bor/Pompa',
    '05': 'Sumur Terlindung', '06': 'Sumur Tak Terlindung', '07': 'Mata Air Terlindung',
    '08': 'Mata Air Tak Terlindung', '09': 'Air Permukaan', '10': 'Air Hujan', '11': 'Lainnya',
    '1': 'Air Kemasan Bermerk', '2': 'Air Isi Ulang', '3': 'Ledeng', '4': 'Sumur Bor/Pompa',
    '5': 'Sumur Terlindung', '6': 'Sumur Tak Terlindung', '7': 'Mata Air Terlindung',
    '8': 'Mata Air Tak Terlindung', '9': 'Air Permukaan',
    1: 'Air Kemasan Bermerk', 2: 'Air Isi Ulang', 3: 'Ledeng', 4: 'Sumur Bor/Pompa',
    5: 'Sumur Terlindung', 6: 'Sumur Tak Terlindung', 7: 'Mata Air Terlindung',
    8: 'Mata Air Tak Terlindung', 9: 'Air Permukaan', 10: 'Air Hujan', 11: 'Lainnya'
}

LABEL_PENERANGAN = {
    1: 'PLN Meteran', 2: 'PLN Non-Meteran', 3: 'Non-PLN', 4: 'Bukan Listrik',
    '1': 'PLN Meteran', '2': 'PLN Non-Meteran', '3': 'Non-PLN', '4': 'Bukan Listrik'
}

LABEL_DAYA_LISTRIK = {
    0: 'Bukan Listrik/Tanpa Meteran', 1: '450 Watt', 2: '900 Watt', 3: '1.300 Watt', 4: '2.200 Watt', 5: '> 2.200 Watt',
    '0': 'Bukan Listrik/Tanpa Meteran', '1': '450 Watt', '2': '900 Watt', '3': '1.300 Watt', '4': '2.200 Watt', '5': '> 2.200 Watt'
}

LABEL_BAHAN_BAKAR = {
    '00': 'Tidak Memasak di Rumah', '01': 'Listrik', '02': 'Gas Elpiji 5,5kg/Blue Gas',
    '03': 'Gas Elpiji 12 kg', '04': 'Gas Elpiji 3 kg', '05': 'Gas Kota/Meteran PGN',
    '06': 'Biogas', '07': 'Minyak Tanah', '08': 'Briket', '09': 'Arang', '10': 'Kayu Bakar', '11': 'Lainnya',
    '0': 'Tidak Memasak di Rumah', '1': 'Listrik', '2': 'Gas Elpiji 5,5kg/Blue Gas',
    '3': 'Gas Elpiji 12 kg', '4': 'Gas Elpiji 3 kg', '5': 'Gas Kota/Meteran PGN',
    '6': 'Biogas', '7': 'Minyak Tanah', '8': 'Briket', '9': 'Arang',
    0: 'Tidak Memasak di Rumah', 1: 'Listrik', 2: 'Gas Elpiji 5,5kg/Blue Gas',
    3: 'Gas Elpiji 12 kg', 4: 'Gas Elpiji 3 kg', 5: 'Gas Kota/Meteran PGN',
    6: 'Biogas', 7: 'Minyak Tanah', 8: 'Briket', 9: 'Arang', 10: 'Kayu Bakar', 11: 'Lainnya'
}

LABEL_FASILITAS_BAB = {
    1: 'Sendiri', 2: 'Bersama', 3: 'MCK Umum', 4: 'Tidak Ada',
    '1': 'Sendiri', '2': 'Bersama', '3': 'MCK Umum', '4': 'Tidak Ada'
}

LABEL_JENIS_DISABILITAS = {
    0: 'Tidak Disabilitas', 1: 'Fisik', 2: 'Sensorik', 3: 'Intelektual', 4: 'Mental', 5: 'Lainnya',
    '0': 'Tidak Disabilitas', '1': 'Fisik', '2': 'Sensorik', '3': 'Intelektual', '4': 'Mental', '5': 'Lainnya'
}

WARNA_FM = '#E74C3C'
WARNA_BFM = '#3498DB'
WARNA_POSITIF = '#2ECC71'
WARNA_NETRAL = '#3498DB'
WARNA_PALETTE = ['#2ECC71', '#3498DB', '#F39C12', '#9B59B6', '#1ABC9C', '#E67E22', '#34495E', '#E74C3C', '#C0392B', '#27AE60', '#2980B9', '#8E44AD']
WARNA_DESIL = ['#C0392B', '#E74C3C', '#F39C12', '#F1C40F', '#3498DB']

# =============================================================================
# FUNGSI HELPER
# =============================================================================

def apply_label(df, col, label_map):
    """Apply label mapping ke kolom"""
    df = df.copy()
    df[col] = df[col].map(label_map).fillna(df[col])
    return df

def create_summary_table(stacked_data, kategori_col, value_col, name_col):
    """Buat tabel summary dari data stacked bar"""
    summary = stacked_data.pivot_table(index=name_col, columns=kategori_col, values=value_col, aggfunc='sum', fill_value=0).reset_index()
    
    if 'Fakir Miskin' in summary.columns and 'Bukan Fakir Miskin' in summary.columns:
        summary['Total'] = summary['Fakir Miskin'] + summary['Bukan Fakir Miskin']
        summary = summary.sort_values('Total', ascending=False)
        total_all = summary['Total'].sum()
        summary['%'] = summary['Total'].apply(lambda x: format_persen_id(x/total_all*100, 2) if total_all > 0 else '0%')
        summary['FM'] = summary['Fakir Miskin'].apply(lambda x: format_angka_id(x))
        summary['Bukan FM'] = summary['Bukan Fakir Miskin'].apply(lambda x: format_angka_id(x))
        summary['Total'] = summary['Total'].apply(lambda x: format_angka_id(x))
        
        result = summary[[name_col, 'Total', 'FM', 'Bukan FM', '%']]
        return result
    return summary

# =============================================================================
# FUNGSI LOAD DATA
# =============================================================================

@st.cache_data
def load_data():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, FILE_CSV)
    
    if not os.path.exists(file_path):
        file_path = FILE_CSV
        if not os.path.exists(file_path):
            st.error(f"❌ File '{FILE_CSV}' tidak ditemukan!")
            return None
    
    df = pd.read_csv(file_path, dtype=str, low_memory=False)
    
    if KOLOM_NIK in df.columns:
        before_count = len(df)
        df = df.drop_duplicates(subset=[KOLOM_NIK], keep='first')
        after_count = len(df)
        if before_count != after_count:
            st.info(f"ℹ️ Ditemukan {before_count - after_count} data penduduk duplikat (berdasarkan NIK) yang telah dibersihkan.")
    
    for col in ['umur', 'jumlah_art_kk', 'jumlah_indikator']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    for col in KOLOM_INDIKATOR:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: 'Memenuhi Kriteria' if str(x).strip() == 'Memenuhi Kriteria' else 'Tidak')
    
    if 'jumlah_indikator' in df.columns:
        df['kategori_fm'] = df['jumlah_indikator'].apply(
            lambda x: 'Fakir Miskin' if pd.notna(x) and x >= 6 else 'Bukan Fakir Miskin'
        )
    
    return df

def get_keluarga_data(df):
    if df is None or len(df) == 0:
        return pd.DataFrame()
    
    df_kel = df.drop_duplicates(subset=KOLOM_NOMOR_KK).copy()
    
    keluarga_fm = df.groupby(KOLOM_NOMOR_KK)['kategori_fm'].apply(
        lambda x: 'Fakir Miskin' if (x == 'Fakir Miskin').any() else 'Bukan Fakir Miskin'
    ).reset_index()
    keluarga_fm.columns = [KOLOM_NOMOR_KK, 'kategori_fm_keluarga']
    df_kel = df_kel.merge(keluarga_fm, on=KOLOM_NOMOR_KK, how='left')
    
    return df_kel

# =============================================================================
# FUNGSI VISUALISASI
# =============================================================================

def apply_layout(fig, title, height=CHART_HEIGHT_PIE):
    fig.update_layout(
        title_text=title, title_font_size=FONT_TITLE, title_x=0.5,
        showlegend=True, legend_font_size=FONT_LEGEND,
        legend_orientation='h', legend_y=-0.15, legend_x=0.5, legend_xanchor='center',
        height=height, margin_l=40, margin_r=40, margin_t=80, margin_b=100
    )
    return fig

def create_pie_simple(labels, values, title, colors=None, show_percent_in_chart=True):
    if colors is None:
        colors = WARNA_PALETTE[:len(labels)]
    textinfo = 'label+percent' if show_percent_in_chart else 'label'
    fig = go.Figure(data=[go.Pie(
        labels=labels, values=values, hole=0.4, marker_colors=colors,
        textinfo=textinfo, textposition='outside',
        textfont_size=FONT_PIE_TEXT, outsidetextfont_size=FONT_PIE_TEXT,
        hovertemplate='<b>%{label}</b><br>Jumlah: %{value:,.0f}<br>Persentase: %{percent}<extra></extra>'
    )])
    return apply_layout(fig, title)

def create_stacked_bar(df, x_col, color_col, title, orientation='v', y_col='count'):
    color_map = {'Fakir Miskin': WARNA_FM, 'Bukan Fakir Miskin': WARNA_BFM}
    
    if orientation == 'v':
        fig = px.bar(df, x=x_col, y=y_col, color=color_col, title=title, 
                     color_discrete_map=color_map, barmode='stack')
    else:
        fig = px.bar(df, y=x_col, x=y_col, color=color_col, title=title, 
                     color_discrete_map=color_map, barmode='stack', orientation='h')
    
    fig.update_layout(
        title_font_size=FONT_TITLE, legend_title_text='Kategori', legend_font_size=FONT_LEGEND,
        font_size=FONT_TICK, margin_l=40, margin_r=40, margin_t=60, margin_b=60
    )
    fig.update_xaxes(tickfont_size=FONT_TICK, title_font_size=FONT_LABEL)
    fig.update_yaxes(tickfont_size=FONT_TICK, title_font_size=FONT_LABEL)
    return fig

def create_indicator_chart(df, title):
    ind_data = []
    for col in KOLOM_INDIKATOR:
        if col in df.columns:
            memenuhi = (df[col] == 'Memenuhi Kriteria').sum()
            tidak = len(df) - memenuhi
            pct = memenuhi / len(df) * 100 if len(df) > 0 else 0
            ind_data.append({'Indikator': LABEL_INDIKATOR.get(col, col), 'Memenuhi': memenuhi, 'Tidak': tidak, 'Persen': pct})
    
    ind_df = pd.DataFrame(ind_data)
    fig = go.Figure()
    pct_labels = [format_persen_id(p, 1) for p in ind_df['Persen']]
    
    fig.add_trace(go.Bar(y=ind_df['Indikator'], x=ind_df['Memenuhi'], name='Memenuhi Kriteria',
                         orientation='h', marker_color=WARNA_FM,
                         text=pct_labels, textposition='auto', textfont_size=FONT_LABEL))
    fig.add_trace(go.Bar(y=ind_df['Indikator'], x=ind_df['Tidak'], name='Tidak Memenuhi',
                         orientation='h', marker_color=WARNA_BFM))
    
    fig.update_layout(
        barmode='stack', title_text=title, title_font_size=FONT_TITLE,
        xaxis_title='Jumlah Penduduk', height=CHART_HEIGHT_BAR, font_size=FONT_TICK, legend_font_size=FONT_LEGEND,
        margin_l=40, margin_r=40, margin_t=60, margin_b=60
    )
    fig.update_xaxes(tickfont_size=FONT_TICK, title_font_size=FONT_LABEL)
    fig.update_yaxes(tickfont_size=FONT_TICK)
    return fig

# =============================================================================
# MAIN APP
# =============================================================================

def main():
    st.set_page_config(page_title="Dashboard Verval Kemiskinan - Kota Bontang 2025",
                       page_icon="📊", layout="wide", initial_sidebar_state="expanded")
    
    # Custom CSS
    st.markdown("""
    <style>
    .stMetricValue { font-size: 28px !important; }
    .stMetricDelta { font-size: 16px !important; }
    .stTabs [data-baseweb="tab"] { font-size: 18px !important; }
    div[data-testid="stDataFrame"] { font-size: 14px !important; }
    .stMarkdown h1 { font-size: 36px !important; }
    .stMarkdown h2 { font-size: 28px !important; }
    .stMarkdown h3 { font-size: 22px !important; }
    .stSelectbox label { font-size: 16px !important; font-weight: bold !important; }
    .stSelectbox div { font-size: 14px !important; }
    </style>
    """, unsafe_allow_html=True)
    
    st.title("📊 Dashboard Verval Data Kemiskinan")
    st.subheader("Kota Bontang Tahun 2025")
    
    df = load_data()
    if df is None:
        st.stop()
    
    # Tampilkan informasi data
    with st.expander("ℹ️ Informasi Data", expanded=False):
        col1, col2 = st.columns(2)
        col1.metric("Total Data Penduduk (Unique NIK)", format_angka_id(len(df)))
        col2.metric("Total Data Keluarga (Unique KK)", format_angka_id(df[KOLOM_NOMOR_KK].nunique()))
    
    # SIDEBAR FILTER
    st.sidebar.header("🔍 Filter Data")
    
    kecamatan_list = ['Semua'] + sorted(df['kecamatan'].dropna().unique().tolist())
    kecamatan_display = ['Semua'] + [LABEL_KECAMATAN.get(k, k) for k in kecamatan_list[1:]]
    selected_kec_idx = st.sidebar.selectbox("Kecamatan", range(len(kecamatan_display)), format_func=lambda x: kecamatan_display[x])
    selected_kec = kecamatan_list[selected_kec_idx]
    
    if selected_kec == 'Semua':
        kelurahan_list = ['Semua'] + sorted(df['kelurahan'].dropna().unique().tolist())
    else:
        kelurahan_list = ['Semua'] + sorted(df[df['kecamatan'] == selected_kec]['kelurahan'].dropna().unique().tolist())
    
    kelurahan_display = ['Semua'] + [LABEL_KELURAHAN.get(k, k) for k in kelurahan_list[1:]]
    selected_kel_idx = st.sidebar.selectbox("Kelurahan", range(len(kelurahan_display)), format_func=lambda x: kelurahan_display[x])
    selected_kel = kelurahan_list[selected_kel_idx]
    
    kategori_list = ['Semua', 'Fakir Miskin', 'Bukan Fakir Miskin']
    selected_kategori = st.sidebar.selectbox("Kategori FM", kategori_list)
    
    # Filter data
    df_filtered = df.copy()
    if selected_kec != 'Semua':
        df_filtered = df_filtered[df_filtered['kecamatan'] == selected_kec]
    if selected_kel != 'Semua':
        df_filtered = df_filtered[df_filtered['kelurahan'] == selected_kel]
    if selected_kategori != 'Semua':
        df_filtered = df_filtered[df_filtered['kategori_fm'] == selected_kategori]
    
    df_keluarga = get_keluarga_data(df_filtered)
    
    # Hitung metrik untuk filtered data
    total_penduduk = len(df_filtered)
    total_keluarga = df_filtered[KOLOM_NOMOR_KK].nunique()
    fm_penduduk = len(df_filtered[df_filtered['kategori_fm'] == 'Fakir Miskin']) if total_penduduk > 0 else 0
    fm_keluarga = len(df_keluarga[df_keluarga['kategori_fm_keluarga'] == 'Fakir Miskin']) if len(df_keluarga) > 0 else 0
    
    st.sidebar.markdown("---")
    st.sidebar.info(f"**Penduduk:** {format_angka_id(total_penduduk)}\n\n**Keluarga:** {format_angka_id(total_keluarga)}")
    
    # METRICS
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Keluarga", format_angka_id(total_keluarga))
    col2.metric("Keluarga FM", format_angka_id(fm_keluarga), 
                format_persen_id(fm_keluarga/total_keluarga*100, 1) if total_keluarga > 0 else "0%")
    col3.metric("Total Penduduk", format_angka_id(total_penduduk))
    col4.metric("Penduduk FM", format_angka_id(fm_penduduk), 
                format_persen_id(fm_penduduk/total_penduduk*100, 1) if total_penduduk > 0 else "0%")
    
    # TABS (Demografi dihapus)
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Ringkasan", "🗺️ Wilayah", "📋 Indikator", 
        "🏠 Kondisi Rumah", "💰 Bantuan Sosial", "📝 Kebutuhan Layanan"
    ])
    
    # =========================================================================
    # TAB 1: RINGKASAN
    # =========================================================================
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            fig = create_pie_simple(['Fakir Miskin', 'Bukan Fakir Miskin'], 
                                   [fm_keluarga, total_keluarga - fm_keluarga], 'Distribusi Keluarga', [WARNA_FM, WARNA_BFM])
            st.plotly_chart(fig, use_container_width=True)
            tbl = pd.DataFrame({'Kategori': ['Fakir Miskin', 'Bukan Fakir Miskin'], 
                               'Jumlah': [format_angka_id(fm_keluarga), format_angka_id(total_keluarga - fm_keluarga)],
                               'Persentase': [format_persen_id(fm_keluarga/total_keluarga*100, 2) if total_keluarga > 0 else '0%', 
                                             format_persen_id((total_keluarga-fm_keluarga)/total_keluarga*100, 2) if total_keluarga > 0 else '0%']})
            st.dataframe(tbl, use_container_width=True, hide_index=True)
        
        with col2:
            fig = create_pie_simple(['Fakir Miskin', 'Bukan Fakir Miskin'],
                                   [fm_penduduk, total_penduduk - fm_penduduk], 'Distribusi Penduduk', [WARNA_FM, WARNA_BFM])
            st.plotly_chart(fig, use_container_width=True)
            tbl = pd.DataFrame({'Kategori': ['Fakir Miskin', 'Bukan Fakir Miskin'], 
                               'Jumlah': [format_angka_id(fm_penduduk), format_angka_id(total_penduduk - fm_penduduk)],
                               'Persentase': [format_persen_id(fm_penduduk/total_penduduk*100, 2) if total_penduduk > 0 else '0%', 
                                             format_persen_id((total_penduduk-fm_penduduk)/total_penduduk*100, 2) if total_penduduk > 0 else '0%']})
            st.dataframe(tbl, use_container_width=True, hide_index=True)
        
        if 'status_keluarga' in df_keluarga.columns:
            st.subheader("Status Keluarga (Desil Kemiskinan)")
            desil_data = df_keluarga['status_keluarga'].value_counts().reset_index()
            desil_data.columns = ['Status', 'Jumlah']
            desil_data['Status'] = desil_data['Status'].map(LABEL_STATUS_KELUARGA).fillna(desil_data['Status'])
            desil_data['Persentase'] = desil_data['Jumlah'] / total_keluarga * 100
            
            col1, col2 = st.columns([2, 1])
            with col1:
                fig = create_pie_simple(desil_data['Status'].tolist(), desil_data['Jumlah'].tolist(), 
                                       'Distribusi Desil Keluarga', WARNA_DESIL[:len(desil_data)])
                st.plotly_chart(fig, use_container_width=True)
            with col2:
                tbl = desil_data.copy()
                tbl['Jumlah'] = tbl['Jumlah'].apply(lambda x: format_angka_id(x))
                tbl['Persentase'] = tbl['Persentase'].apply(lambda x: format_persen_id(x, 2))
                st.dataframe(tbl, use_container_width=True, hide_index=True)
        
        if 'jumlah_indikator' in df_filtered.columns:
            st.subheader("Distribusi Jumlah Indikator Terpenuhi")
            hist_data = df_filtered['jumlah_indikator'].value_counts().sort_index().reset_index()
            hist_data.columns = ['Jumlah Indikator', 'Jumlah Penduduk']
            hist_data['Kategori'] = hist_data['Jumlah Indikator'].apply(lambda x: 'Fakir Miskin' if x >= 6 else 'Bukan Fakir Miskin')
            
            fig = px.bar(hist_data, x='Jumlah Indikator', y='Jumlah Penduduk', color='Kategori',
                        color_discrete_map={'Fakir Miskin': WARNA_FM, 'Bukan Fakir Miskin': WARNA_BFM})
            fig.add_vline(x=5.5, line_dash="dash", line_color="red", annotation_text="Batas FM (≥6)")
            fig.update_layout(title_text='', font_size=FONT_TICK, legend_font_size=FONT_LEGEND,
                             xaxis_title='Jumlah Indikator', yaxis_title='Jumlah Penduduk')
            st.plotly_chart(fig, use_container_width=True)
            
            tbl = hist_data.copy()
            tbl['Jumlah Penduduk'] = tbl['Jumlah Penduduk'].apply(lambda x: format_angka_id(x))
            st.dataframe(tbl, use_container_width=True, hide_index=True)
    
    # =========================================================================
    # TAB 2: WILAYAH
    # =========================================================================
    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            kec_data = df_keluarga.groupby(['kecamatan', 'kategori_fm_keluarga']).size().reset_index(name='count')
            kec_data = apply_label(kec_data, 'kecamatan', LABEL_KECAMATAN)
            fig = create_stacked_bar(kec_data, 'kecamatan', 'kategori_fm_keluarga', 'Keluarga per Kecamatan')
            st.plotly_chart(fig, use_container_width=True)
            tbl = create_summary_table(kec_data, 'kategori_fm_keluarga', 'count', 'kecamatan')
            st.dataframe(tbl, use_container_width=True, hide_index=True)
        with col2:
            kec_data_pend = df_filtered.groupby(['kecamatan', 'kategori_fm']).size().reset_index(name='count')
            kec_data_pend = apply_label(kec_data_pend, 'kecamatan', LABEL_KECAMATAN)
            fig = create_stacked_bar(kec_data_pend, 'kecamatan', 'kategori_fm', 'Penduduk per Kecamatan')
            st.plotly_chart(fig, use_container_width=True)
            tbl = create_summary_table(kec_data_pend, 'kategori_fm', 'count', 'kecamatan')
            st.dataframe(tbl, use_container_width=True, hide_index=True)
        
        st.subheader("Distribusi per Kelurahan")
        
        st.markdown("#### Keluarga per Kelurahan")
        kel_data = df_keluarga.groupby(['kelurahan', 'kategori_fm_keluarga']).size().reset_index(name='count')
        kel_data = apply_label(kel_data, 'kelurahan', LABEL_KELURAHAN)
        
        col1, col2 = st.columns([2, 1])
        with col1:
            fig = create_stacked_bar(kel_data, 'kelurahan', 'kategori_fm_keluarga', 'Keluarga per Kelurahan', orientation='h')
            fig.update_layout(height=550)
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            tbl = create_summary_table(kel_data, 'kategori_fm_keluarga', 'count', 'kelurahan')
            st.dataframe(tbl, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        
        st.markdown("#### Penduduk per Kelurahan")
        kel_data_pend = df_filtered.groupby(['kelurahan', 'kategori_fm']).size().reset_index(name='count')
        kel_data_pend = apply_label(kel_data_pend, 'kelurahan', LABEL_KELURAHAN)
        
        col1, col2 = st.columns([2, 1])
        with col1:
            fig = create_stacked_bar(kel_data_pend, 'kelurahan', 'kategori_fm', 'Penduduk per Kelurahan', orientation='h')
            fig.update_layout(height=550)
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            tbl = create_summary_table(kel_data_pend, 'kategori_fm', 'count', 'kelurahan')
            st.dataframe(tbl, use_container_width=True, hide_index=True)
    
    # =========================================================================
    # TAB 3: INDIKATOR (Tanpa Total)
    # =========================================================================
    with tab3:
        st.markdown("### 📌 Logika Klasifikasi\n**Penduduk FM:** ≥ 6 dari 8 indikator | **Keluarga FM:** Min. 1 anggota FM")
        fig = create_indicator_chart(df_filtered, "Distribusi 8 Indikator Kemiskinan")
        st.plotly_chart(fig, use_container_width=True)
        
        ind_summary = []
        for col in KOLOM_INDIKATOR:
            if col in df_filtered.columns:
                m = (df_filtered[col] == 'Memenuhi Kriteria').sum()
                t = len(df_filtered) - m
                p = m / len(df_filtered) * 100 if len(df_filtered) > 0 else 0
                ind_summary.append({
                    'Indikator': LABEL_INDIKATOR.get(col, col), 
                    'Memenuhi': format_angka_id(m), 
                    'Tidak': format_angka_id(t), 
                    'Persentase': format_persen_id(p, 2)
                })
        ind_df = pd.DataFrame(ind_summary)
        st.dataframe(ind_df, use_container_width=True, hide_index=True)
        st.caption(f"✅ **Total penduduk yang dianalisis:** {format_angka_id(len(df_filtered))}")
    
    # =========================================================================
    # TAB 4: KONDISI RUMAH - DENGAN DROPDOWN
    # =========================================================================
    with tab4:
        st.info(f"🏠 **Total Keluarga:** {format_angka_id(total_keluarga)} | **Fakir Miskin:** {format_angka_id(fm_keluarga)} | **Bukan Fakir Miskin:** {format_angka_id(total_keluarga - fm_keluarga)}")
        
        # Dropdown untuk memilih kondisi rumah
        rumah_options = {
            "Jenis Lantai": "jenis_lantai",
            "Jenis Dinding": "jenis_dinding",
            "Jenis Atap": "jenis_atap",
            "Sumber Penerangan": "sumber_penerangan",
            "Daya Listrik": "daya_listrik",
            "Fasilitas BAB": "fasilitas_bab",
            "Sumber Air Minum": "sumber_air",
            "Bahan Bakar Memasak": "bahan_bakar"
        }
        
        selected_rumah = st.selectbox(
            "🏚️ Pilih Kondisi Rumah",
            list(rumah_options.keys()),
            format_func=lambda x: f"🏠 {x}"
        )
        
        kolom_rumah = rumah_options[selected_rumah]
        
        st.markdown("---")
        
        # Label map untuk kondisi rumah
        label_map_rumah = None
        if kolom_rumah == "jenis_lantai":
            label_map_rumah = LABEL_LANTAI
        elif kolom_rumah == "jenis_dinding":
            label_map_rumah = LABEL_DINDING
        elif kolom_rumah == "jenis_atap":
            label_map_rumah = LABEL_ATAP
        elif kolom_rumah == "sumber_penerangan":
            label_map_rumah = LABEL_PENERANGAN
        elif kolom_rumah == "daya_listrik":
            label_map_rumah = LABEL_DAYA_LISTRIK
        elif kolom_rumah == "fasilitas_bab":
            label_map_rumah = LABEL_FASILITAS_BAB
        elif kolom_rumah == "sumber_air":
            label_map_rumah = LABEL_SUMBER_AIR
        elif kolom_rumah == "bahan_bakar":
            label_map_rumah = LABEL_BAHAN_BAKAR
        
        if kolom_rumah in df_keluarga.columns:
            data_valid = df_keluarga[df_keluarga[kolom_rumah].notna()]
            
            if len(data_valid) > 0:
                data = data_valid.groupby([kolom_rumah, 'kategori_fm_keluarga']).size().reset_index(name='count')
                data = apply_label(data, kolom_rumah, label_map_rumah)
                
                fig = create_stacked_bar(data, kolom_rumah, 'kategori_fm_keluarga', f'{selected_rumah}', orientation='h')
                fig.update_layout(height=CHART_HEIGHT_RUMAH)
                st.plotly_chart(fig, use_container_width=True)
                
                summary = data.pivot_table(index=kolom_rumah, columns='kategori_fm_keluarga', values='count', aggfunc='sum', fill_value=0).reset_index()
                if 'Fakir Miskin' in summary.columns and 'Bukan Fakir Miskin' in summary.columns:
                    summary['Total'] = summary['Fakir Miskin'] + summary['Bukan Fakir Miskin']
                    summary = summary.sort_values('Total', ascending=False)
                    total_all = summary['Total'].sum()
                    summary['%'] = summary['Total'].apply(lambda x: format_persen_id(x/total_all*100, 2) if total_all > 0 else '0%')
                    summary['FM'] = summary['Fakir Miskin'].apply(lambda x: format_angka_id(x))
                    summary['Bukan FM'] = summary['Bukan Fakir Miskin'].apply(lambda x: format_angka_id(x))
                    summary['Total'] = summary['Total'].apply(lambda x: format_angka_id(x))
                    st.dataframe(summary[[kolom_rumah, 'Total', 'FM', 'Bukan FM', '%']], use_container_width=True, hide_index=True)
                
                st.caption(f"ℹ️ Berdasarkan data valid: {format_angka_id(len(data_valid))} dari {format_angka_id(total_keluarga)} keluarga")
            else:
                st.warning(f"Tidak ada data valid untuk {selected_rumah}")
        else:
            st.warning(f"Kolom '{kolom_rumah}' tidak ditemukan dalam data")
    
    # =========================================================================
    # TAB 5: BANTUAN SOSIAL (Tanpa Total)
    # =========================================================================
    with tab5:
        st.subheader("Cakupan Penerimaan Bantuan Sosial")
        bansos_cols = [
            ('bantuan_sembako', 'Sembako/BPNT'), ('bantuan_pkh', 'PKH'),
            ('bantuan_blt', 'BLT'), ('subsidi_listrik', 'Subsidi Listrik'),
            ('subsidi_lpg', 'Subsidi LPG'), ('bantuan_pemda', 'Bantuan Pemda'),
            ('bantuan_non_pemerintah', 'Non-Pemerintah')
        ]
        
        bansos_stacked = []
        bansos_summary = []
        
        for col, label in bansos_cols:
            if col in df_keluarga.columns:
                for kategori in ['Fakir Miskin', 'Bukan Fakir Miskin']:
                    mask = (df_keluarga['kategori_fm_keluarga'] == kategori) & ((df_keluarga[col] == 1) | (df_keluarga[col] == '1'))
                    count = mask.sum()
                    bansos_stacked.append({'Jenis Bantuan': label, 'kategori_fm_keluarga': kategori, 'count': count})
                
                total_penerima = ((df_keluarga[col] == 1) | (df_keluarga[col] == '1')).sum()
                fm_penerima = ((df_keluarga['kategori_fm_keluarga'] == 'Fakir Miskin') & ((df_keluarga[col] == 1) | (df_keluarga[col] == '1'))).sum()
                bfm_penerima = total_penerima - fm_penerima
                pct = total_penerima / len(df_keluarga) * 100 if len(df_keluarga) > 0 else 0
                bansos_summary.append({
                    'Jenis Bantuan': label, 
                    'Total': format_angka_id(total_penerima),
                    'FM': format_angka_id(fm_penerima),
                    'Bukan FM': format_angka_id(bfm_penerima),
                    '%': format_persen_id(pct, 2)
                })
        
        if bansos_stacked:
            bansos_df = pd.DataFrame(bansos_stacked)
            summary_df = pd.DataFrame(bansos_summary)
            
            col1, col2 = st.columns([2, 1])
            with col1:
                fig = create_stacked_bar(bansos_df, 'Jenis Bantuan', 'kategori_fm_keluarga', 'Penerima Bantuan Sosial', orientation='h')
                st.plotly_chart(fig, use_container_width=True)
            with col2:
                st.markdown("**Tabel Distribusi:**")
                st.dataframe(summary_df, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        
        st.subheader("Data Penyandang Disabilitas")
        
        if 'jenis_disabilitas' in df_filtered.columns:
            df_temp = df_filtered.copy()
            df_temp['status_disabilitas'] = df_temp['jenis_disabilitas'].apply(
                lambda x: 'Disabilitas' if str(x) in ['1','2','3','4','5'] else 'Tidak Disabilitas'
            )
            
            data = df_temp.groupby(['status_disabilitas', 'kategori_fm']).size().reset_index(name='count')
            
            col1, col2 = st.columns([2, 1])
            with col1:
                fig = create_stacked_bar(data, 'status_disabilitas', 'kategori_fm', 'Status Disabilitas')
                st.plotly_chart(fig, use_container_width=True)
            with col2:
                tbl = create_summary_table(data, 'kategori_fm', 'count', 'status_disabilitas')
                st.dataframe(tbl, use_container_width=True, hide_index=True)
            
            disabilitas_mask = df_filtered['jenis_disabilitas'].isin(['1','2','3','4','5'])
            if disabilitas_mask.sum() > 0:
                st.subheader("Jenis Disabilitas")
                df_disabilitas = df_filtered[disabilitas_mask].copy()
                data = df_disabilitas.groupby(['jenis_disabilitas', 'kategori_fm']).size().reset_index(name='count')
                data = apply_label(data, 'jenis_disabilitas', LABEL_JENIS_DISABILITAS)
                
                col1, col2 = st.columns([2, 1])
                with col1:
                    fig = create_stacked_bar(data, 'jenis_disabilitas', 'kategori_fm', 'Jenis Disabilitas', orientation='h')
                    st.plotly_chart(fig, use_container_width=True)
                with col2:
                    tbl = create_summary_table(data, 'kategori_fm', 'count', 'jenis_disabilitas')
                    st.dataframe(tbl, use_container_width=True, hide_index=True)
    
    # =========================================================================
    # TAB 6: KEBUTUHAN LAYANAN (Tanpa Total)
    # =========================================================================
    with tab6:
        st.subheader("Kebutuhan Layanan")
        
        kebutuhan_cols = [('butuh_pangan', '🍚 Pangan'), ('butuh_sandang', '👕 Sandang'), 
                         ('butuh_kesehatan', '🏥 Kesehatan'), ('butuh_pendidikan', '📚 Pendidikan'), 
                         ('butuh_dokumen', '📄 Dokumen')]
        
        cols = st.columns(3)
        kebutuhan_data = []
        for i, (col, label) in enumerate(kebutuhan_cols):
            if col in df_filtered.columns:
                butuh = ((df_filtered[col] == 1) | (df_filtered[col] == '1')).sum()
                pct = butuh/len(df_filtered)*100 if len(df_filtered) > 0 else 0
                with cols[i % 3]:
                    st.markdown(f"#### {label}")
                    st.metric(f"Butuh {label.split()[1]}", format_angka_id(butuh), format_persen_id(pct, 1))
                kebutuhan_data.append({'Kebutuhan': label.split()[1], 'Jumlah': butuh, 'Persentase': pct})
        
        if kebutuhan_data:
            st.markdown("---")
            keb_df = pd.DataFrame(kebutuhan_data)
            fig = px.bar(keb_df, x='Kebutuhan', y='Jumlah', title='Distribusi Kebutuhan Layanan',
                        color_discrete_sequence=[WARNA_FM])
            fig.update_layout(title_font_size=FONT_TITLE, font_size=FONT_TICK)
            st.plotly_chart(fig, use_container_width=True)
            
            tbl = keb_df.copy()
            tbl['Jumlah'] = tbl['Jumlah'].apply(lambda x: format_angka_id(x))
            tbl['Persentase'] = tbl['Persentase'].apply(lambda x: format_persen_id(x, 2))
            st.dataframe(tbl, use_container_width=True, hide_index=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align:center; padding: 25px; background: linear-gradient(135deg, #1a365d 0%, #2c5282 100%); border-radius: 10px;'>
        <h3 style='color: white; font-size: 24px;'>Dashboard Verval Data Kemiskinan Kota Bontang 2025</h3>
        <p style='color: #e2e8f0; font-size: 18px;'>Dinas Sosial dan Pemberdayaan Masyarakat Kota Bontang</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()