import streamlit as st
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine
from library import  BarChart,  LineChart, PieChart, HorizontalBarChart, GanttChart,  DashboardCard,  ChatCard, DonutChart
import plotly.figure_factory as ff
import folium
from streamlit_folium import st_folium


st.set_page_config(
    page_title="Dashboard Pegawai",
    page_icon="👨‍💼",
    layout='wide'
)
#judul
st.markdown(
    """<h1 style='text-align: center;'>Dashboard Data Pertamanan</h1>""", 
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
 

engine = create_engine(
    "postgresql+psycopg2://postgres:intan271001@localhost:5432/db_pegawai"
)


def fetch_data(file_name):
    return pd.read_excel(file_name)

# Membaca data dari file Excel
data_taman = fetch_data("data_taman.xlsx")
aset_taman = fetch_data("aset_taman.xlsx")
maintanance = fetch_data("maintanance_taman.xlsx")
jumlah_pengunjung = fetch_data("jumlah_pengunjung.xlsx")
jenis_aset = fetch_data("jenis_aset.xlsx")
region = fetch_data("region.xlsx")

tree_icon_url = "https://upload.wikimedia.org/wikipedia/commons/5/50/Emojione_1F333.svg"

def format_number(value):
    if value >= 1_000_000_000:  
        return f"{value / 1_00_000_000}B"
    if value >= 1_000_000:  
        return f"{value / 1_000_000}M"
    elif value >= 1_000: 
        return f"{value / 1_000}K"
    else: 
        return str(value)
    
def preprocess_coordinates(data):
    coordinates = data['koordinat_lokasi'].str.split(',', expand=True)
    data['latitude'] = coordinates[0].astype(float)
    data['longitude'] = coordinates[1].astype(float)
    return data
data_taman=preprocess_coordinates(data_taman)

def clean_and_convert_cost(df, column_name):
    df[column_name] = pd.to_numeric(df[column_name], errors='coerce')  # Konversi menjadi numerik
    return df
data_taman = clean_and_convert_cost(data_taman, 'nilai_perolehan')
maintanance=clean_and_convert_cost(maintanance, 'cost')

def filter_data_by_year(df, year_column, selected_year):
    df[year_column] = pd.to_datetime(df[year_column])
    df_filtered = df[df[year_column].dt.year == selected_year]
    return df_filtered

def filter_taman(taman, maintanance, asettaman,jumlahpengunjung, selected_bidang):
    if selected_bidang != "Semua":
        selected_id= taman.loc[taman["nama_taman"] == selected_bidang, "id_taman"].values[0]
        filtered_taman = taman[taman["id_taman"] == selected_id]
        filtered_maintanance = maintanance[maintanance["id_taman"] == selected_id]
        filter_aset=asettaman[asettaman["id_taman"] == selected_id]
        filter_pengunjung=jumlahpengunjung[jumlahpengunjung["id_taman"] == selected_id]
    else:
        filtered_taman = taman
        filtered_maintanance = maintanance
        filter_aset=asettaman
        filter_pengunjung=jumlahpengunjung
    return filtered_taman, filtered_maintanance,filter_aset, filter_pengunjung

with st.container():

    map_gianyar = folium.Map(location=[-8.3405, 115.2583], zoom_start=11)

    tree_icon_url = "https://upload.wikimedia.org/wikipedia/commons/5/50/Emojione_1F333.svg"
    for index, row in data_taman.iterrows():
        icon = folium.CustomIcon(
            icon_image=tree_icon_url,  
            icon_size=(40, 40)  
        )
        popup_text = f"{row['nama_taman']}: {row['jenis_taman']}"
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=popup_text,
            tooltip=row['nama_taman'],
            icon=icon  
        ).add_to(map_gianyar)
    st.subheader('Persebaran Taman Kabupaten Gianyar', divider='blue')
    st_folium(map_gianyar, width=1400, height=300)
with st.container():
    row3col1, row3col2= st.columns([1,1])

    with row3col2:
        taman_merge_reg=data_taman.merge(region[region['tipe_region'] == 'kecamatan'], on="id_region", how="left") 
        totaltamanreg=(taman_merge_reg.groupby(['nama_region', 'jenis_taman']).size().reset_index(name="jumlah_taman"))
        kondisi_dan_rentang = HorizontalBarChart(
             totaltamanreg,
            x_column="jumlah_taman",
            y_column="nama_region",
            title="",
            height=250,
            color='jenis_taman',
            custom_labels={"jumlah_taman": "Jumlah", "nama_region": "Kecamatan"}
        )
        st.subheader('Persebaran Taman Per Kecamatan', divider='blue')
        kondisi_dan_rentang.render()
    with row3col1:
        nilaipertahun=data_taman.groupby(['tahun_perolehan', 'sumber_dana'])['nilai_perolehan'].sum().reset_index(name="jumlah_perolehan")

        nilai_perolehan_line = LineChart(
            data=nilaipertahun, x_column='tahun_perolehan', 
            y_column='jumlah_perolehan', category_column='sumber_dana',
            height=250, 
            title="")
        st.subheader('Nilai Perolehan per Sumber Dana', divider='blue')  
        nilai_perolehan_line.render()   

with st.container():
    row2col1, row2col2, row2col3=st.columns([2,1,1])
    with row2col3:
        taman_choices = ["Semua"] + data_taman['nama_taman'].unique().tolist()  # atau bisa pakai 'id_taman'
        st.subheader('Pilih Taman', divider='blue')
        selected_taman = st.selectbox("Pilih Taman", options=taman_choices)
        filtered_taman, filtered_maintanance,filter_aset, filter_pengunjung=filter_taman(data_taman,maintanance, aset_taman, jumlah_pengunjung, selected_taman)
        st.info("Filter sesuai taman menunjukkan dashboard yang akan ditampilkan disesuaikan dengan taman yang dipilih")
        # st.write(filtered_data)
    with row2col1:
        jenis_taman = filtered_taman.groupby('jenis_taman').size().reset_index(name="jumlah")
        jumlah_taman = HorizontalBarChart(
            jenis_taman,
            x_column="jumlah",
            y_column="jenis_taman",
            title="",
            height=250,
            custom_labels={"jenis_taman": "Jenis Taman", "jumlah": "Jumlah Taman"})
        st.subheader('Persebaran Jenis Taman', divider='blue')   
        jumlah_taman.render()

    with row2col2:
        sumber_data = filtered_taman['sumber_dana'].value_counts()
        total_dana=filtered_taman['nilai_perolehan'].sum()

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

 
with st.container():
    row4col1, row4col2=st.columns([1,2])
    with row4col1:
        data_koor=preprocess_coordinates(filtered_taman)
        if selected_taman== 'Semua':
            latitude = data_koor['latitude'][0]
            longitude = data_koor['longitude'][0]
        else:
            latitude = data_koor['latitude']
            longitude = data_koor['longitude']

        radius_area = 500 
        map_gianyar2 = folium.Map(location=[latitude, longitude], zoom_start=15)

        folium.Marker(
            location=[latitude, longitude],
            popup= f"{row['nama_taman']} Jenis {row['jenis_taman']} dengan Luas{row['luas']}",
            tooltip=row['nama_taman'],
            icon=icon  
        ).add_to(map_gianyar2)

        folium.Circle(
            location=[latitude, longitude],
            radius=radius_area,  
            color="blue",  
            fill=True,
            fill_color="blue",
            fill_opacity=0.2  
        ).add_to(map_gianyar2)

        st.subheader('Maps', divider='blue') 
        st_folium(map_gianyar2, width=500, height=300)

    with row4col2:
        aset_taman_fil=filtered_taman.merge(aset_taman, on='id_taman', how='left')
        jenis_taman_fil=aset_taman_fil.merge(jenis_aset, on='kode_jenis_aset', how='left')
        jenis_aset_taman = jenis_taman_fil.groupby('jenis_aset').size().reset_index(name="jumlah")
        jenis_taman_bar = HorizontalBarChart(
            jenis_aset_taman,
            x_column="jumlah",
            y_column="jenis_aset",
            title="",
            height=320,
            custom_labels={"jenis_aset": "Jenis Aset", "jumlah": "Jumlah Aset"})
        st.subheader('Jenis Aset Pada Taman', divider='blue')
            
        jenis_taman_bar.render()


with st.container():
    row5col1, row5col2,row5col3= st.columns([1,0.7, 0.5])

    with row5col1:
        filtered_maintanance["datetime"] = pd.to_datetime(filtered_maintanance["datetime"])
        filtered_maintanance["tahun"] = filtered_maintanance["datetime"].dt.year 
        mergemain=filtered_taman.merge(filtered_maintanance, on='id_taman', how='left')
     
        total_biaya_per_tahun = mergemain.groupby(["tahun", "jenis_taman"])["cost"].sum().reset_index(name="total_biaya")
    
        total_biaya_line= LineChart(
            total_biaya_per_tahun, x_column='tahun', 
            y_column='total_biaya', category_column='jenis_taman', 
            height=250,
            title="")
        st.subheader('Biaya Maintanance Per Tahun',divider='blue')   
        total_biaya_line.render()

    with row5col2:
        aset_count = filter_aset['kondisi'].value_counts()

        labelproposi=aset_count.index
        valueproporsi=aset_count.values

        kondisi_aset = PieChart(
            labels=labelproposi,
            values=valueproporsi,
            title="")
        st.subheader('Kondisi Aset',divider='blue')
        kondisi_aset.render()
    with row5col3:
        # Tambahkan kolom year_month untuk mempermudah agregasi per bulan
        filtered_maintanance['year_month'] = filtered_maintanance['datetime'].dt.to_period('M')

        # Agregasi total biaya per bulan
        monthly_cost = filtered_maintanance.groupby('year_month')['cost'].sum().reset_index(name='total_cost')

        # Ambil data bulan ini dan bulan lalu
        current_month = monthly_cost['year_month'].max()
        last_month = current_month - 1
        current_year = current_month.year
        last_year = current_year - 1

        # Ambil total biaya untuk bulan ini dan bulan lalu
        current_cost = monthly_cost.loc[monthly_cost['year_month'] == current_month, 'total_cost'].sum()
        last_cost = monthly_cost.loc[monthly_cost['year_month'] == last_month, 'total_cost'].sum()

        # Hitung pertumbuhan untuk bulan ini vs bulan lalu
        if last_cost > 0:
            growth = ((current_cost - last_cost) / last_cost * 100)
            growth_status = "up" if growth > 0 else "down"
        elif current_cost > 0:
            growth = -100  # Jika ada biaya bulan ini tapi tidak ada di bulan lalu
            growth_status = "down"
        else:
            growth = 0  # Jika tidak ada biaya bulan ini dan bulan lalu
            growth_status = "down"

        # Format angka
        formatted_current_cost = format_number(current_cost)
        growth_formatted = f"{growth:.0f}% dibandingkan bulan lalu"

        # Tampilkan perbandingan bulan ini vs bulan lalu di dashboard
        if filtered_maintanance.empty:
            st.warning("Tidak ada biaya maintenance bulan ini, periksa data!") 
        else:
            metrik3 = DashboardCard(
                title_1="Total Biaya Maintenance",
                title_2=f"pada {current_month.strftime('%B %Y')}",
                total=formatted_current_cost,
                delta=growth_formatted,
                delta_status=growth_status
            )
            metrik3.render()

            # Tambahkan informasi di st.info tentang perbandingan dengan bulan yang sama tahun lalu
            # Ambil data bulan yang sama tahun lalu
            last_year_cost = monthly_cost.loc[monthly_cost['year_month'] == (current_month - 12), 'total_cost'].sum()

            # Hitung pertumbuhan dibandingkan dengan tahun lalu
            if last_year_cost > 0:
                year_growth = ((current_cost - last_year_cost) / last_year_cost * 100)
                year_growth_status = "up" if year_growth > 0 else "down"
            elif current_cost > 0:
                year_growth = -100  # Jika ada biaya bulan ini tapi tidak ada di bulan yang sama tahun lalu
                year_growth_status = "down"
            else:
                year_growth = 0  # Jika tidak ada biaya bulan ini dan tahun lalu
                year_growth_status = "down"

            # Menampilkan analisis di st.info
            st.info(
                #f"Total biaya maintenance bulan ini ({current_month.strftime('%B %Y')}) adalah {formatted_current_cost}. "
                f"Jumlah ini {year_growth_status} sebesar {abs(year_growth):.0f}% dibandingkan bulan yang sama pada tahun lalu ({current_month.strftime('%B')} {last_year})."
            )

with st.container():
    row6col1, row6col2= st.columns([1,1])
    
    with row6col1:
        st.subheader('Biaya Maintanance Per Bulan', divider='blue')
        years_available = filtered_maintanance['datetime'].dt.year.unique()
        selected_year = st.selectbox('pilih tahun', years_available)

        df_filtered_month = filter_data_by_year(filtered_maintanance, 'datetime', selected_year)
        df_filtered_month=filtered_taman.merge(df_filtered_month, on='id_taman', how='left')
        df_filtered_month["bulan"] = df_filtered_month["datetime"].dt.strftime('%B')

        total_biaya_per_bulan = df_filtered_month.groupby(["bulan", "jenis_taman"])["cost"].sum().reset_index(name="total_biaya")
        bulan_order = [
        "January", "February", "March", "April", "May", "June", 
        "July", "August", "September", "October", "November", "December"]
        total_biaya_per_bulan ["bulan"] = pd.Categorical(
        total_biaya_per_bulan ["bulan"], categories=bulan_order, ordered=True)
        total_biaya_per_bulan  = total_biaya_per_bulan .sort_values("bulan")

        total_biaya_bulan= LineChart(
            total_biaya_per_bulan, x_column='bulan', 
            y_column='total_biaya', category_column='jenis_taman', 
            height=250,
            title="")
            
        total_biaya_bulan.render()
    with row6col2:
        vendor_counts = filtered_maintanance["vendor"].value_counts().reset_index(name="jumlah_pemeliharaan") 
        vendor_counts.columns = ["vendor", "jumlah_pemeliharaan"]
        vendor_name = BarChart(
            vendor_counts,
            x_column="vendor",
            y_column="jumlah_pemeliharaan",
            title="",
            height=335,
            custom_labels={"vendor": "Vendor", "jumlah_pemeliharaan": "Jumlah Maintenance"})
        st.subheader('Vendir Maintenance', divider='blue')
        vendor_name.render()

with st.container():
     col1, col2=st.columns([1,1])   
     with col1:
        filtered_taman["next_maint_date"] = pd.to_datetime(filtered_taman["next_maint_date"])
        df_combined = filtered_taman.merge(filtered_maintanance, on="id_taman", how="left") 
        df_combined = filter_data_by_year(df_combined, 'next_maint_date', selected_year)

        gantt_chart = GanttChart(df_combined, task_column='action', 
                                 start_column='next_maint_date', end_column='datetime', 
                                 resource_column='vendor', title='')
        st.subheader('Kegiatan Maintanance', divider='blue')
        gantt_chart.render()

     with col2:
        st.subheader('Jadwal Maintanance', divider='blue')
        filtered_taman["last_maint_date"] = pd.to_datetime(filtered_taman["last_maint_date"])
        today = pd.Timestamp.now()
        filtered_data = filtered_taman[filtered_taman["next_maint_date"] >= today]
        filtered_data = filtered_data[["nama_taman",  "last_maint_date", "next_maint_date"]]
        filtered_data = filtered_data.head(8)
        filtered_data.rename(
            columns={
                "nama_taman": "Nama Taman",
                "last_maint_date": "Tanggal Maintanance Terakhir",
                "next_maint_date": "Tanggal Maintanance Berikutnya",
            },
            inplace=True,
        )
        st.markdown("**Jadwal Maintenance Berikutnya**")
        if filtered_data.empty:
            st.warning("Tidak ada jadwal pemeliharaan aset sejauh ini.")
        else:
            table_data = filtered_data.values.tolist()
            header = filtered_data.columns.tolist()
            table_data.insert(0, header)
            fig = ff.create_table(table_data, height_constant=10)
            st.plotly_chart(fig)
with st.container():
    row7col1, row7col2=st.columns([0.5, 1])
    with row7col1:
        filter_pengunjung["start_record"] = pd.to_datetime(filter_pengunjung["start_record"])
        current_year = datetime.now().year
        last_year = current_year - 1
        current_year_data = filter_pengunjung[filter_pengunjung["start_record"].dt.year == current_year]
        last_year_data = filter_pengunjung[filter_pengunjung["start_record"].dt.year == last_year]

        total_current_year = current_year_data["jumlah_pengunjung"].sum()
        total_last_year = last_year_data["jumlah_pengunjung"].sum()
        growth = 0
        if total_last_year > 0:
            growth = (total_current_year - total_last_year) / total_last_year * 100

        formatted_current = f"{total_current_year:,}"  # Format angka
        growth_formatted = f"{growth:.0f}%"  # Format pertumbuhan
        growth_status = "up" if growth > 0 else "down"

        metrik3 = DashboardCard(
            title_1="Jumlah Pengunjung",
            title_2=f"per {datetime.now().strftime('%B %Y')}",
            total=formatted_current,
            delta=growth_formatted,
            delta_status=growth_status
        )

        metrik3.render()

        # Menampilkan analisis di st.info mengenai perbandingan jumlah pengunjung tahun ini dan tahun lalu
        st.info(
            #f"Jumlah pengunjung pada tahun {current_year} mencapai {formatted_current} orang. "
            f"Jumlah ini {growth_status} sebesar {abs(growth):.0f}% dibandingkan dengan jumlah pengunjung pada tahun {last_year}."
        )
    with row7col2:
        st.subheader('Pengunjung Per Tahun', divider='blue')
        jumlah_pengunjung["start_record"] = pd.to_datetime(jumlah_pengunjung["start_record"])
        jumlah_pengunjung["tahun"] = jumlah_pengunjung["start_record"].dt.year 
        mergemain2=filtered_taman.merge(jumlah_pengunjung, on='id_taman', how='left')
     
        pengunjung_pertahun = mergemain2.groupby(["tahun", "jenis_taman"])["jumlah_pengunjung"].sum().reset_index(name="total_biaya")
        if filtered_data.empty:
            st.warning("Tidak ada jadwal pemeliharaan aset sejauh ini.")
        else:    
            total_pengunjung= LineChart(
                pengunjung_pertahun, x_column='tahun', 
                y_column='total_biaya', category_column='jenis_taman', 
                height=250,
                title="")
                
            total_pengunjung.render()
