import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from sqlalchemy import create_engine
from library import  BarChart, DonutChart, LineChart, PieChart, HorizontalBarChart, GanttChart, ChatCard, DashboardCard
import folium
from streamlit_folium import st_folium

st.set_page_config(
    page_title="Dashboard Cipta Karya",
    page_icon="👨‍💼",
    layout='wide'
)

#judul
st.markdown(
    """<h1 style='text-align: center;'>Dashboard Data Layanan Kepegawaian</h1>""", 
    unsafe_allow_html=True
)

# KE HALAMAN CHATBOT
chatcard = ChatCard(
    link="https://your-link-here.com"
)

chatcard.render()  
#atur background color
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


def generate_years(start_year, end_year):
    return list(range(start_year, end_year + 1))
# Fetch data
def fetch_data(file_name):
    return pd.read_excel(file_name)

def filter_data_by_year(df, year_column, selected_year):
    df[year_column] = pd.to_datetime(df[year_column])
    df_filtered = df[df[year_column].dt.year == selected_year]
    return df_filtered
def format_number(value):
    """Format the value to a more readable string (e.g., 1000 -> 1K, 1000000 -> 1M, 1000000000 -> 1B)."""
    if value >= 1_000_000_000:
        formatted_value = value / 1_000_000_000
        return f"{int(formatted_value)}B" if formatted_value.is_integer() else f"{formatted_value:.1f}B"
    elif value >= 1_000_000:
        formatted_value = value / 1_000_000
        return f"{int(formatted_value)}M" if formatted_value.is_integer() else f"{formatted_value:.1f}M"
    elif value >= 1_000:
        formatted_value = value / 1_000
        return f"{int(formatted_value)}K" if formatted_value.is_integer() else f"{formatted_value:.1f}K"
    else:
        return str(value)


data_proyek = fetch_data("data_proyek.xlsx")
data_maintenance = fetch_data("data_maintenance.xlsx")
region = fetch_data("region.xlsx")

def preprocess_coordinates(data):
    coordinates = data['koordinat_lokasi'].str.split(',', expand=True)
    data['latitude'] = coordinates[0].astype(float)
    data['longitude'] = coordinates[1].astype(float)
    return data
data_proyek=preprocess_coordinates(data_proyek)



def filter_proyek_kecamatan(data_proyek,  region, selected_bidang):
    if selected_bidang != "Semua":
        selected_id_dept = region.loc[region["nama_region"] == selected_bidang, "id_region"].values[0]
        # filtered_data_proyek = data_proyek[data_proyek["id_proyek"].isin(
        #     region[region["id_region"] == selected_id_dept]["id_proyek"]
        # )]
        filtered_data_proyek= data_proyek[data_proyek["id_region"] == selected_id_dept]
    else:
        filtered_data_proyek = data_proyek
    return filtered_data_proyek
 

 ####################################################################################################################
####################################################################################################################
####################                                                                            ####################
####################                            VISUALISASI                                     ####################
####################                                                                            ####################
####################################################################################################################
####################################################################################################################

with st.container():
    row1col1, row1col2= st.columns([0.5,2])

    with row1col1:
                # Filter region untuk hanya mengambil tipe_region "kecamatan"
        filtered_regions = region[region['tipe_region'] == 'kecamatan']

        # Buat pilihan taman_choices
        taman_choices = ["Semua"] + filtered_regions['nama_region'].unique().tolist()
        st.subheader('Pilih Kecamatan', divider='blue')
        selected_taman = st.selectbox("Pilih Kecamatan", options=taman_choices)
        filtered_proyek=filter_proyek_kecamatan(data_proyek,region, selected_taman)
        st.info("Filter sesuai kecamatan menunjukkan dashboard yang akan ditampilkan disesuaikan dengan kecamatan yang dipilih")

    with row1col2:
        # st.write(filtered_proyek)
        filtered_proyek["tgl_mulai"] = pd.to_datetime(filtered_proyek["tgl_mulai"])
        filtered_proyek["tahun"] = filtered_proyek["tgl_mulai"].dt.year 
        data_maintenance["tgl_pelaksanaan"] = pd.to_datetime(data_maintenance["tgl_pelaksanaan"])
        data_maintenance["tahun_maintenance"] = data_maintenance["tgl_pelaksanaan"].dt.year 
        regionproyek=filtered_proyek.merge(region, on='id_region', how='left')
     
        jumlah_proyek = regionproyek.groupby(["tahun", "nama_region"])["id_proyek"].count().reset_index(name="total_proyek")

    
        jumlah_proyek_line= LineChart(
            jumlah_proyek, x_column='tahun', 
            y_column='total_proyek', category_column='nama_region', 
            title="",
            height=250)
        
        st.subheader('Jumlah Proyek Per Tahun', divider='blue')   
        
        jumlah_proyek_line.render()

st.subheader('Metrik', divider='blue') 
with st.container():
    row2col1, row2col2, row2col3, row2col4=st.columns([1,1,1,1])
    with row2col1:
        # Pastikan kolom 'tgl_mulai' memiliki format datetime
        regionproyek["tgl_mulai"] = pd.to_datetime(regionproyek["tgl_mulai"])

        # Mendapatkan bulan dan tahun saat ini
        current_date = datetime.now()
        current_month = current_date.month
        current_year = current_date.year

        # Filter data berdasarkan bulan dan tahun saat ini
        current_month_data = regionproyek[
            (regionproyek["tgl_mulai"].dt.year == current_year) & (regionproyek["tgl_mulai"].dt.month == current_month)
        ]
        last_month_data = regionproyek[
            (regionproyek["tgl_mulai"].dt.year == (current_year if current_month > 1 else current_year - 1)) & 
            (regionproyek["tgl_mulai"].dt.month == (current_month - 1 if current_month > 1 else 12))
        ]

        # Hitung total proyek bulan ini dan bulan lalu
        total_proyek_now = current_month_data["id_proyek"].count()
        total_proyek_last = last_month_data["id_proyek"].count()

        # Hitung pertumbuhan
        if total_proyek_last > 0:
            growth = ((total_proyek_now - total_proyek_last) / total_proyek_last) * 100
        elif total_proyek_last ==0:
            growth = +100 
        else:
            growth = -100 if total_proyek_now == 0 else 0  # Jika bulan ini 0 proyek, berarti turun 100%

        formatted_growth = f"{total_proyek_now:,}"  # Format angka
        growth_status = "up" if growth > 0 else "down"
        growth_formatted = f"{growth:.0f}% dibandingkan bulan lalu"

        # Tampilkan metrik
        if regionproyek.empty:
            st.warning("Tidak ada data proyek, periksa data!") 
        else:
            metrik1 = DashboardCard(
                title_1="Total Proyek",
                title_2=f"pada {current_date.strftime('%B %Y')}",
                total=formatted_growth,
                delta=growth_formatted,
                delta_status=growth_status
            )
            
            metrik1.render()


    with row2col2:
        # Hitung total proyek bulan ini dan bulan lalu
        anggaran_proyek_now = current_month_data["total_anggaran"].sum()
        anggaran_proyek_last = last_month_data["total_anggaran"].sum()

        # Hitung pertumbuhan
        if anggaran_proyek_last > 0:
            growth = ((anggaran_proyek_now - anggaran_proyek_last) / anggaran_proyek_last) * 100
        elif total_proyek_last ==0:
            growth = +100 
        else:
            growth = -100 if anggaran_proyek_now == 0 else 0  # Jika bulan ini 0 proyek, berarti turun 100%

        formatted_growth2 = f"{anggaran_proyek_now:,}"  # Format angka
        growth_status2 = "up" if growth > 0 else "down"
        growth_formatted2 = f"{growth:.0f}% dibandingkan bulan lalu"
        if regionproyek.empty:
            st.warning("Tidak ada data anggaran proyek, periksa data!") 
        else:
            metrik2 = DashboardCard(
                title_1="Total Anggaran",
                title_2=f"pada tahun {current_year}",
                total=formatted_growth2,
                delta=growth_formatted2,
                delta_status=growth_status2
            )

            metrik2.render() 
    with row2col3:
       # Hitung total proyek bulan ini dan bulan lalu
        total_luas_now = current_month_data["luas_area_proyek"].sum()
        total_luas_last = last_month_data["luas_area_proyek"].sum()

        # Hitung pertumbuhan
        if total_luas_last > 0:
            growth = ((total_luas_now - total_luas_last) / total_luas_last) * 100
        elif total_proyek_last ==0:
            growth = +100         
        else:
            growth = -100 if total_luas_now == 0 else 0  # Jika bulan ini 0 proyek, berarti turun 100%

        formatted_growth3 = f"{total_luas_now:,}"  # Format angka
        growth_status3 = "up" if growth > 0 else "down"
        growth_formatted3 = f"{growth:.0f}% dibandingkan bulan lalu"


        if regionproyek.empty:
            st.warning("Tidak ada luas proyek, periksa data!") 
        else:
            metrik3 = DashboardCard(
                title_1="Luas Proyek",
                title_2=f"pada tahun {current_year}",
                total=formatted_growth3,
                delta=growth_formatted3,
                delta_status=growth_status3
            )

            metrik3.render()
    with row2col4:
       # Hitung total proyek bulan ini dan bulan lalu
        panjang_proyek_now = current_month_data["panjang_proyek"].sum()
        panjang_proyek_last = last_month_data["panjang_proyek"].sum()

        # Hitung pertumbuhan
        if panjang_proyek_last > 0:
            growth = ((panjang_proyek_now - panjang_proyek_last) / panjang_proyek_last) * 100
        elif total_proyek_last ==0:
            growth = +100         
        else:
            growth = -100 if panjang_proyek_now == 0 else 0  # Jika bulan ini 0 proyek, berarti turun 100%

        formatted_growth4 = f"{panjang_proyek_now:,}"  # Format angka
        growth_status4 = "up" if growth > 0 else "down"
        growth_formatted4 = f"{growth:.0f}% dibandingkan bulan lalu"

        if regionproyek.empty:
            st.warning("Tidak ada data panjang proyek, periksa data!") 
        else:
            metrik4 = DashboardCard(
                title_1="Total Panjang Proyek",
                title_2=f"pada tahun {current_year}",
                total=formatted_growth4,
                delta=growth_formatted4,
                delta_status=growth_status4
            )

            metrik4.render()


st.write('''''')           
topleft, topright=st.columns([1,1])
with topleft:
    map_gianyar = folium.Map(location=[-8.3405, 115.2583], zoom_start=17)

    tree_icon_url = "https://upload.wikimedia.org/wikipedia/commons/a/a0/Ecuador_road_sign_T1-3.svg"
    for index, row in filtered_proyek.iterrows():
        icon = folium.CustomIcon(
            icon_image=tree_icon_url,  
            icon_size=(40, 40)  
        )
        popup_text = f"{row['nama_proyek']}, {row['panjang_proyek']}"
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=popup_text,
            tooltip=row['nama_proyek'],
            icon=icon  
        ).add_to(map_gianyar)
    st.subheader('Persebaran Aset', divider='blue') 
    st_folium(map_gianyar, width=700, height=380)
    if all(col in filtered_proyek.columns for col in ['panjang_proyek', 'total_anggaran', 'luas_area_proyek']):
        # Identifikasi proyek dengan panjang terbesar
        proyek_terbesar = filtered_proyek.loc[filtered_proyek['panjang_proyek'].idxmax()]
        
        # Identifikasi proyek dengan biaya tertinggi
        proyek_termahal = filtered_proyek.loc[filtered_proyek['total_anggaran'].idxmax()]
        
        # Identifikasi proyek dengan luas terbesar
        proyek_terluas = filtered_proyek.loc[filtered_proyek['luas_area_proyek'].idxmax()]
        
        # Tampilkan analisis gabungan
        st.info(
            f"Proyek dengan panjang terbesar adalah '{proyek_terbesar['nama_proyek']}' dengan panjang {proyek_terbesar['panjang_proyek']} meter. "
            f"Proyek dengan biaya tertinggi adalah '{proyek_termahal['nama_proyek']}' dengan total anggaran sebesar {proyek_termahal['total_anggaran']:,} rupiah. "
            f"Selain itu, proyek dengan luas terbesar adalah '{proyek_terluas['nama_proyek']}' dengan luas {proyek_terluas['luas_area_proyek']} meter persegi."
        )
    else:
        st.info("Data panjang, total anggaran, atau luas proyek tidak tersedia untuk analisis.")



with topright:
    cost_proyek = regionproyek.groupby(["tahun", "nama_region"])["total_anggaran"].sum().reset_index(name="total_anggaran")
    cost_proyek_line= LineChart(
        cost_proyek, x_column='tahun', 
        y_column='total_anggaran', category_column='nama_region', 
        title=" ",
        height=250)
    st.subheader('Anggaran Proyek Per Tahun', divider='blue') 
    
    cost_proyek_line.render()

    data_maintenance["tgl_pelaksanaan"] = pd.to_datetime(data_maintenance["tgl_pelaksanaan"])
    data_maintenance["tahun_maintenance"] = data_maintenance["tgl_pelaksanaan"].dt.year 
    maintananceproyek=regionproyek.merge(data_maintenance, on='id_proyek', how='left') 


    cost_maintanance = maintananceproyek.groupby(["tahun_maintenance", "nama_region"])["biaya_pemeliharaan"].sum().reset_index(name="total_anggaran")
    cost_proyek_line= LineChart(
        cost_maintanance, x_column='tahun_maintenance', 
        y_column='total_anggaran', category_column='nama_region', 
        title="",
        height=250) 
    st.subheader('Anggaran Maintenance Per Tahun', divider='blue') 
    cost_proyek_line.render()


colrow1, colrow2=st.columns([0.5,1])
with colrow1:
        # Ambil daftar tahun unik dari kolom 'tahun' di dataset filtered_proyek
        tahun_list = sorted(filtered_proyek['tahun'].unique())

        # Buat dropdown untuk memilih tahun berdasarkan data yang tersedia
        st.subheader('Pilih Tahun', divider='blue')
        selected_year = st.selectbox('Pilih tahun', tahun_list)
        sumber_data = filtered_proyek['sumber_dana'].value_counts()
        # filtered_proyek['total_anggaran'] = pd.to_numeric(filtered_proyek['total_anggaran'], errors='coerce')
        total_dana=filtered_proyek['total_anggaran'].sum()

        labelsumber_data=sumber_data.index
        valuesumber_data=sumber_data.values

        donut_sumber_data = DonutChart(
            labels=labelsumber_data,
            values=valuesumber_data,
            title="",
            text='Dana',
            total=total_dana)
        st.subheader('Sumber Dana', divider='blue')
        donut_sumber_data.render()

with colrow2:
        nilaipertahun=filtered_proyek.groupby(['tahun', 'sumber_dana'])['total_anggaran'].sum().reset_index(name="jumlah_perolehan")

        nilai_perolehan_line = LineChart(
            data=nilaipertahun, x_column='tahun', 
            y_column='jumlah_perolehan', category_column='sumber_dana', 
            title="",
            height=280)
        st.subheader('Nilai Perolehan per Sumber Dana', divider='blue')   
        nilai_perolehan_line.render() 
        # Data untuk analisis
        tahun_terpilih = selected_year
        tahun_sebelumnya = tahun_terpilih - 1

        # Data tahun terpilih
        data_tahun_terpilih = filtered_proyek[filtered_proyek['tahun'] == tahun_terpilih]
        if not data_tahun_terpilih.empty:
            sumber_terbesar = data_tahun_terpilih.groupby('sumber_dana')['total_anggaran'].sum().idxmax()
            total_terbesar = data_tahun_terpilih.groupby('sumber_dana')['total_anggaran'].sum().max()
        else:
            sumber_terbesar = "Tidak ada data"
            total_terbesar = 0

        # Data tahun sebelumnya
        data_tahun_sebelumnya = filtered_proyek[filtered_proyek['tahun'] == tahun_sebelumnya]
        if not data_tahun_sebelumnya.empty:
            sumber_terbesar_sebelumnya = data_tahun_sebelumnya.groupby('sumber_dana')['total_anggaran'].sum().idxmax()
            total_sebelumnya = data_tahun_sebelumnya.groupby('sumber_dana')['total_anggaran'].sum().max()
        else:
            sumber_terbesar_sebelumnya = "Tidak ada data"
            total_sebelumnya = 0

        # Tampilkan analisis di st.info
        st.info(
            f"Pada tahun {tahun_terpilih}, sumber dana terbesar adalah '{sumber_terbesar}' dengan total anggaran sebesar Rp{total_terbesar:,}. "
            f"Dibandingkan dengan tahun {tahun_sebelumnya}, sumber dana terbesar {'tetap sama' if sumber_terbesar == sumber_terbesar_sebelumnya else 'berubah'} "
            f"menjadi '{sumber_terbesar_sebelumnya}' dengan total anggaran sebesar Rp{total_sebelumnya:,}."
        )


with st.container():
    row3col1, row3col2= st.columns([1,1])
    with row3col1:
        df_proyek_month = filter_data_by_year(regionproyek, 'tgl_mulai', selected_year)
        df_proyek_month["bulan"] = df_proyek_month["tgl_mulai"].dt.strftime('%B')
        proyek_biaya_per_bulan = df_proyek_month.groupby(["bulan", "nama_region"])["total_anggaran"].sum().reset_index(name="total_biaya")
        bulan_order = [
        "January", "February", "March", "April", "May", "June", 
        "July", "August", "September", "October", "November", "December"]
        proyek_biaya_per_bulan ["bulan"] = pd.Categorical(proyek_biaya_per_bulan["bulan"], categories=bulan_order, ordered=True)
        total_biaya_per_bulan  = proyek_biaya_per_bulan .sort_values("bulan")

        total_biaya_bulan= LineChart(
            total_biaya_per_bulan, x_column='bulan', 
            y_column='total_biaya', category_column='nama_region', 
            title="",
            height=250)
        st.subheader('Biaya Anggaran Per Bulan', divider='blue')  
        total_biaya_bulan.render()
    with row3col2:
        df_filtered_month = filter_data_by_year(maintananceproyek, 'tgl_pelaksanaan', selected_year)
        # df_filtered_month=regionproyek.merge(df_filtered_month, on='id_proyek', how='left')
        df_filtered_month["bulan"] = df_filtered_month["tgl_pelaksanaan"].dt.strftime('%B')
        total_biaya_per_bulan = df_filtered_month.groupby(["bulan", "nama_region"])["biaya_pemeliharaan"].sum().reset_index(name="total_biaya")

        total_biaya_per_bulan ["bulan"] = pd.Categorical(
        total_biaya_per_bulan ["bulan"], categories=bulan_order, ordered=True)
        total_biaya_per_bulan  = total_biaya_per_bulan .sort_values("bulan")

        total_biaya_bulan= LineChart(
            total_biaya_per_bulan, x_column='bulan', 
            y_column='total_biaya', category_column='nama_region', 
            title="",
            height=250)
        st.subheader('Biaya Maintanance Per Bulan', divider='blue')     
        total_biaya_bulan.render()



col1, col2=st.columns([0.5,2])
with col1:
            jumlah_pekerja = maintananceproyek[maintananceproyek["tahun_maintenance"] == current_year]["id_maintenance"].count()
            jumlah_pekerja_last = maintananceproyek[maintananceproyek["tahun_maintenance"] == current_year-1]["id_maintenance"].count()
            growth = ((jumlah_pekerja - jumlah_pekerja_last) / jumlah_pekerja_last * 100) if jumlah_pekerja_last > 0 else 0
            formatted_growth = format_number(jumlah_pekerja)
            growth_status = "up" if growth > 0 else "down"
            growth_formatted = f"{growth:.0f}% dibandingkan bulan lalu"

            if jumlah_proyek.empty:
                st.warning("Tidak ada pekerja, periksa data!") 
            else:
                metrik1 = DashboardCard(
                    title_1="Total Pemeliharaan",
                    title_2=f"pada {current_year}",
                    total=formatted_growth,
                    delta=growth_formatted,
                    delta_status=growth_status
                )

                metrik1.render() 
            jumlah_pekerja = maintananceproyek[maintananceproyek["tahun_maintenance"] == current_year]["biaya_pemeliharaan"].sum()
            jumlah_pekerja_last = maintananceproyek[maintananceproyek["tahun_maintenance"] == current_year-1]["biaya_pemeliharaan"].sum()
            growth = ((jumlah_pekerja - jumlah_pekerja_last) / jumlah_pekerja_last * 100) if jumlah_pekerja_last > 0 else 0
            formatted_growth = format_number(jumlah_pekerja)
            growth_status = "up" if growth > 0 else "down"
            growth_formatted = f"{growth:.0f}% dibandingkan bulan lalu"

            if jumlah_proyek.empty:
                st.warning("Tidak ada biaya maintanance bulan ini, periksa data!") 
            else:
                metrik1 = DashboardCard(
                    title_1="Biaya Maintenance",
                    title_2=f"pada {current_year}",
                    total=formatted_growth,
                    delta=growth_formatted,
                    delta_status=growth_status
                )

                metrik1.render()             
with col2:
            vendor_counts = filtered_proyek["nama_kontraktor"].value_counts().reset_index(name="jumlah_proyek") 
            vendor_counts.columns = ["nama_kontraktor", "jumlah_proyek"]
            vendor_name = BarChart(
                vendor_counts,
                x_column="nama_kontraktor",
                y_column="jumlah_proyek",
                title="",
                height=350,
                custom_labels={"nama_kontraktor": "Nama Kontraktor", "jumlah_proyek": "Jumlah Proyek"})
            st.subheader('Kontraktor Proyek', divider='blue') 
            vendor_name.render()

with st.container():
    row5col1, row5col2, row5col3=st.columns([2,0.7, 0.7])
    with row5col1:
        jenis_maint_cost=data_maintenance.groupby(['tahun_maintenance', 'jenis_pemeliharaan'])['biaya_pemeliharaan'].sum().reset_index(name="jumlah_perolehan")
        jenis_maint_cost_line = LineChart(
            data=jenis_maint_cost, x_column='tahun_maintenance', 
            y_column='jumlah_perolehan', category_column='jenis_pemeliharaan', 
            title="",
            height=250)
        st.subheader('Biaya Per Jenis Maintenance', divider='blue')    
        jenis_maint_cost_line.render() 
    with row5col2:
        aset_count = data_maintenance['jenis_pemeliharaan'].value_counts()
        labelproposi=aset_count.index
        valueproporsi=aset_count.values

        kondisi_aset = PieChart(
            labels=labelproposi,
            values=valueproporsi,
            title="")
        st.subheader('Kondisi Aset', divider='blue') 
        kondisi_aset.render() 
    with row5col3:
            jumlah_pekerja = maintananceproyek[maintananceproyek["tahun_maintenance"] == current_year]["jml_tenaga_kerja"].sum()
            jumlah_pekerja_last = maintananceproyek[maintananceproyek["tahun_maintenance"] == current_year-1]["jml_tenaga_kerja"].sum()
            growth = ((jumlah_pekerja - jumlah_pekerja_last) / jumlah_pekerja_last * 100) if jumlah_pekerja_last > 0 else 0
            formatted_growth = format_number(jumlah_pekerja)
            growth_status = "up" if growth > 0 else "down"
            growth_formatted = f"{growth:.0f}% dibandingkan bulan lalu"

            if jumlah_proyek.empty:
                st.warning("Tidak ada biaya maintanance bulan ini, periksa data!") 
            else:
                metrik1 = DashboardCard(
                    title_1="Total Tenaga Kerja",
                    title_2=f"pada {current_year}",
                    total=formatted_growth,
                    delta=growth_formatted,
                    delta_status=growth_status
                )

                metrik1.render() 
            # Hitung jumlah pekerja untuk tahun ini dan tahun lalu
            jumlah_pekerja = maintananceproyek[maintananceproyek["tahun_maintenance"] == current_year]["jml_tenaga_kerja"].sum()
            jumlah_pekerja_last = maintananceproyek[maintananceproyek["tahun_maintenance"] == current_year - 1]["jml_tenaga_kerja"].sum()

            # Hitung pertumbuhan (growth)
            growth = ((jumlah_pekerja - jumlah_pekerja_last) / jumlah_pekerja_last * 100) if jumlah_pekerja_last > 0 else 0

            # Format informasi
            if jumlah_pekerja > 0:
                growth_direction = "meningkat" if growth > 0 else "menurun"
                st.info(
                    f"Jumlah ini {growth_direction} sebesar {abs(growth):.0f}% dibandingkan tahun lalu ({current_year - 1}) "
                    f"dengan total {jumlah_pekerja_last} orang."
                )
            else:
                st.info("Tidak ada data tenaga kerja untuk tahun ini.")
 
with st.container():
        gantt_chart = GanttChart(filtered_proyek, task_column='nama_proyek', 
                                 start_column='tgl_mulai', end_column='tgl_selesai', 
                                 resource_column='nama_kontraktor', title=' ')
        st.subheader('Kegiatan Proyek', divider='blue') 
        gantt_chart.render()
  
