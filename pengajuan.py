import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from sqlalchemy import create_engine
from library import  BarChart, DonutChart2, LineChart, PieChart, HorizontalBarChart, GanttChart, ChatCard, DashboardCard, DashboardCardNoDelta, HorizontalBarChartWithLine
import folium
from streamlit_folium import st_folium
import plotly.graph_objects as go

st.set_page_config(
    page_title="Dashboard Pegawai",
    page_icon="👨‍💼",
    layout='wide'
)

st.markdown(
    """
    <style>
    /* Mengatur warna latar belakang aplikasi */
    .stApp {
        background-color: #f5f5f5; /* Light grey */
    }
    </style>
    """,
    unsafe_allow_html=True,
)
st.markdown("""<h1 style='text-align: center; margin-bottom:5%;'>Dashboard Data Layanan Penataan Ruang</h1>""", unsafe_allow_html=True)

def generate_years(start_year, end_year):
    return list(range(start_year, end_year + 1))
def fetch_data(file_name):
    return pd.read_excel(file_name)
def filter_data_by_year(df, year_column, selected_year):
    df[year_column] = pd.to_datetime(df[year_column])
    df_filtered = df[df[year_column].dt.year == selected_year]
    return df_filtered
def format_number(value):
    if value >= 1_000_000_000:  
        return f"{value / 1_00_000_000}B"
    if value >= 1_000_000:  
        return f"{value / 1_000_000}M"
    elif value >= 1_000: 
        return f"{value / 1_000}K"
    else: 
        return str(value)
tata_ruang = fetch_data("tata_ruang.xlsx")
data_node = fetch_data("data_node.xlsx")
flow_detail = fetch_data("flow_detail.xlsx")
kbli = fetch_data("kbli.xlsx")
region = fetch_data("region.xlsx")

def preprocess_coordinates(data):
    coordinates = data['koordinat_lokasi'].str.split(',', expand=True)
    data['latitude'] = coordinates[0].astype(float)
    data['longitude'] = coordinates[1].astype(float)
    return data



tata_merge= tata_ruang.merge(flow_detail, on="id_pengajuan", how="left")
tata_merge=tata_merge.merge(data_node, on="id_node", how="left")
tata_merge['timestamp_start'] = pd.to_datetime(tata_merge['timestamp_start'], errors='coerce')
tata_merge['year'] = tata_merge['timestamp_start'].dt.year
years = tata_merge['year'].dropna().unique()
years = sorted(years)
st.subheader('Pilih Tahun', divider='blue')
selected_year = st.selectbox("Tahun", options=years)
filtered_data = tata_merge[tata_merge['year'] == selected_year]
filtered_data=preprocess_coordinates(filtered_data)
filtered_data_reg=filtered_data.merge(region[region['tipe_region'] == 'kecamatan'], on="id_region", how="left") 

# st.subheader('Metrik', divider='blue')
with st.container():
    threshold = {
        "Permohonan Baru": 5,
        "Validasi": 10,
        "Pengkajian": 15,
        "Penerbitan Dokumen": 20,
    }

    status_summary = filtered_data.groupby("status").agg(
        total_time=("total_time", "sum"),
        avg_time=("total_time", "mean"),
        count=("id_pengajuan", "count"),  # Jumlah permohonan per status
    ).reset_index()
    def evaluate_status(row):
        if row["avg_time"] <= threshold[row["status"]]:
            return "Ideal", "Status sudah ideal.", "green"
        else:
            difference = (row["avg_time"] - threshold[row["status"]]) # dalam menit
            return "Tidak Ideal", f"Tingkatkan dengan mengurangi waktu {difference:.0f} hari lagi.", "red"

    status_summary[["is_ideal", "suggestion", "status_color"]] = status_summary.apply(
        evaluate_status, axis=1, result_type="expand"
    )

    desired_order = ["Permohonan Baru", "Validasi", "Pengkajian", "Penerbitan Dokumen"]
    status_summary["status"] = pd.Categorical(status_summary["status"], categories=desired_order, ordered=True)
    status_summary = status_summary.sort_values("status")
    columns = st.columns(4)
    for idx, row in status_summary.iterrows():
        # Buat card untuk setiap status
        card = DashboardCardNoDelta(
            title_1=row["status"],
            title_2=f"Rata-rata waktu: {row['avg_time']:.0f} hari",
            total=row["count"],  # Jumlah permohonan
            description=row["suggestion"],
            status_color=row["status_color"],
        )

        # Tentukan kolom tempat card akan ditampilkan
        with columns[idx]:
            card.render()
st.write('''''')
with st.container():
    rowcol1, rowcol2, rowcol3=st.columns([1.5,1,0.5])
    with rowcol1:
        map_gianyar = folium.Map(location=[-8.489568, 115.319184], zoom_start=15)

        tree_icon_url = "https://upload.wikimedia.org/wikipedia/commons/e/ed/Map_pin_icon.svg"
        for index, row in filtered_data.iterrows():
            icon = folium.CustomIcon(
                icon_image=tree_icon_url,  
                icon_size=(20, 20)  
            )
            popup_text = f"{row['status']}"
            folium.Marker(
                location=[row['latitude'], row['longitude']],
                popup=popup_text,
                tooltip=row['nama_pengaju'],
                icon=icon  
            ).add_to(map_gianyar)
        st.subheader("Distribusi Titik Lokasi Pengajuan", divider="blue")
        jumlah_pengajuan_per_kecamatan = filtered_data_reg.groupby('nama_region')['id_pengajuan'].count().reset_index(name="jumlah_pengajuan")
        kecamatan_terbanyak = jumlah_pengajuan_per_kecamatan.sort_values('jumlah_pengajuan', ascending=False).iloc[0]
        st.info('Visualisasi peta ini menunjukkan distribusi koordinat lokasi pengajuan.'
                f" Kecamatan {kecamatan_terbanyak['nama_region']} memiliki jumlah pengajuan terbanyak dengan total {kecamatan_terbanyak['jumlah_pengajuan']} pengajuan. ")
        st_folium(map_gianyar, width=700, height=255)

    with rowcol2:
        filtered_data_node = filtered_data_reg[filtered_data["p_node"].isnull()]
        labels = filtered_data_node["node_name"].tolist()
        values = [1] * len(labels) 
        total = filtered_data["id_node"].count()
        donut_jenis_layanan = DonutChart2(
            labels=labels,
            values=values,
            title="",
            text='Pengajuan',
            total=total)
        st.subheader("Jenis Layanan", divider="blue")
        donut_jenis_layanan.render()
        st.info(
            "Diagram menunjukkan persentase pengajuan berdasarkan jenis layanan yang telah dilakukan."
            f" Total pengajuan yang tercatat adalah {total} pengajuan. "
        )
    with rowcol3:
        status_node = data_node['node_status'].value_counts()
        labelproposi=status_node.index
        valueproporsi=status_node.values

        kondisi_aset = PieChart(
            labels=labelproposi,
            values=valueproporsi,
            title=" ")
        st.subheader("Status Proses", divider="blue")
      
        kondisi_aset.render() 
        st.info(
            "Aktif menunjukkan proses yang sedang berjalan"
        ) 

with st.container():
    row1col1, row1col2= st.columns([1,1])

    with row1col1:
        grouped_data = filtered_data_node.groupby(["nama_region", "node_name"]).size().reset_index(name="jumlah_pengajuan")
        kondisi_dan_rentang = HorizontalBarChart(
            grouped_data,
            x_column="jumlah_pengajuan",
            y_column="nama_region",
            title=" ",
            height=250,
            color='node_name',
            custom_labels={"jumlah_pengajuan": "Jumlah", "nama_region": "Kecamatan"}
        )
        st.subheader('Persebaran Pengajuan Per Kecamatan', divider='blue')        #
        kondisi_dan_rentang.render()
    with row1col2:
        tata_merge_kbli = filtered_data_reg.merge(kbli, on="id_KBLI", how="left")
        totaltata_merge_kbli = (
            tata_merge_kbli.groupby(["nama"])
            .size()
            .reset_index(name="jumlah")
            .sort_values(by="jumlah", ascending=False)
        )
        
        top_categories = totaltata_merge_kbli.head(5)
        other_categories = totaltata_merge_kbli.iloc[5:]  # Sisanya sebagai "Lainnya"
        if not other_categories.empty:
            other_total = other_categories["jumlah"].sum()
            top_categories = pd.concat(
                [
                    top_categories,
                    pd.DataFrame({"nama": ["Lainnya"], "jumlah": [other_total]}),
                ]
            )
        
        kondisi_dan_rentang = HorizontalBarChart(
            top_categories,
            x_column="jumlah",
            y_column="nama",
            title=" ",
            height=250,
            custom_labels={"jumlah": "Jumlah", "nama": "Kategori"}
        )
        st.subheader("Distribusi Unit Usaha", divider="blue")
        kondisi_dan_rentang.render()

with st.container():

    filtered_data_reg["timestamp_end"] = pd.to_datetime(filtered_data_reg["timestamp_end"])
    filtered_data_reg["estimasi_waktu_jam"] = (filtered_data_reg["timestamp_end"] - flow_detail["timestamp_start"]).dt.total_seconds() / 3600  # dalam jam
    filtered_data_reg["estimasi_waktu_hari"] = filtered_data_reg["estimasi_waktu_jam"] / 24  
    filtered_data_reg["standard_time"] = pd.to_numeric(filtered_data_reg["standard_time"], errors="coerce")

    parent_nodes = filtered_data_reg[filtered_data_reg["p_node"].isnull()] 
    with st.container():
        col1,col2=st.columns([1,1])
        with col1:
            parent_options = parent_nodes["node_name"].tolist()
            st.subheader("Pilih Jenis Layanan", divider='blue')
            selected_parent = st.selectbox ("jenis layanan", options=parent_options)

    selected_parent_id = parent_nodes[parent_nodes["node_name"] == selected_parent]["id_node"].values[0]
    child_data = filtered_data_reg[filtered_data_reg["p_node"] == selected_parent_id]

    if child_data.empty:
        st.write(f"Tidak ada data untuk {selected_parent}.")
    else:
        # Persiapkan data untuk HorizontalBarChartWithLine
        chart_data = child_data.copy()
        chart_data["Node Name"] = chart_data["node_name"]
        chart_data["Duration (Hours)"] = chart_data["estimasi_waktu_jam"]
        chart_data["Standard Time"] = chart_data["standard_time"]

        # Buat objek chart menggunakan class
        chart = HorizontalBarChartWithLine(
            data=chart_data,
            x_bar="Duration (Hours)",
            y_bar="Node Name",
            x_line="Standard Time",
            y_line="Node Name",
            bar_label="Durasi Pengajuan",
            line_label="Standar Waktu",
            title=f" ",
        )

        # Tampilkan chart dan analisis
        with st.container():
            col1, col2 = st.columns([2, 1])

            # Kolom 1: Chart
            with col1:
                st.subheader(selected_parent, divider='blue')
                chart.render()

            # Kolom 2: Analisis
            with col2:
                mean_duration = chart_data["Duration (Hours)"].mean()
                mean_standard = chart_data["Standard Time"].mean()

                # Analisis menggunakan st.info, st.warning, atau st.error
                st.subheader(f"Analisis {selected_parent}", divider='green')

                st.info(f"""
                    Durasi rata-rata pengajuan: {mean_duration:.0f} jam
                    dengan standar waktu rata-rata: {mean_standard:.0f} jam
                """)

                if mean_duration > mean_standard:
                    st.warning("""
                        Durasi rata-rata lebih tinggi dari standar waktu. 
                        Disarankan untuk meningkatkan efisiensi proses.
                    """)
                else:
                    st.success("""
                        Durasi rata-rata berada di bawah standar waktu. 
                        Proses sudah berjalan sesuai standar.
                    """)
