import streamlit as st
import pandas as pd
from datetime import datetime
from library import  BarChart,  LineChart, PieChart, HorizontalBarChart, GanttChart,  DashboardCard, HorizontalBarChartWithLine, ChatCard, format_number
import plotly.figure_factory as ff

st.set_page_config(
    page_title="Dashboard Pegawai",
    page_icon="👨‍💼",
    layout='wide'
)
#judul
st.markdown(
    """<h1 style='text-align: center;'>Dashboard Data Layanan Manajemen Aset</h1>""", 
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
 


def fetch_data(file_name):
    return pd.read_excel(file_name)
   
data_aset = fetch_data("data_aset.xlsx")
jenis_aset = fetch_data("jenis_aset2.xlsx")  
maintanance= fetch_data("maintanance.xlsx")
struktur_organisasi = fetch_data("struktur_organisasi.xlsx")
####fetch data dari database



#######filter divisi
def filter_aset_per_divisi(data_aset, struktur_organisasi, selected_bidang):
    # Jika selected_bidang bukan "Semua", filter berdasarkan bidang yang dipilih
    if selected_bidang != "Semua":
        # Cek apakah ada matching bidang di struktur organisasi
        matching_dept = struktur_organisasi.loc[struktur_organisasi["name_of_dept"] == selected_bidang, "id_dept"]
        
        if not matching_dept.empty:
            selected_id_dept = matching_dept.values[0]
            
            # Filter data aset dan maintenance berdasarkan id_dept
            filtered_data_aset = data_aset[data_aset["id_dept"] == selected_id_dept]
        else:
            # Jika tidak ada matching bidang, kembalikan DataFrame kosong
            filtered_data_aset = data_aset.iloc[0:0]
    else:
        # Jika "Semua", gunakan seluruh data
        filtered_data_aset = data_aset
    
    return filtered_data_aset

####### filter tahun
def filter_data_by_year(df, year_column, selected_year):
    df[year_column] = pd.to_datetime(df[year_column])
    df_filtered = df[df[year_column].dt.year == selected_year]
    return df_filtered

def clean_and_convert_cost(df, column_name):
    #df[column_name] = df[column_name].str.replace(r'[^\d.]', '', regex=True)  # Hapus karakter non-numerik
    df[column_name] = pd.to_numeric(df[column_name], errors='coerce')  # Konversi menjadi numerik
    return df

data_aset['tahun_perolehan'] = pd.to_numeric(data_aset['tahun_perolehan'], errors='coerce')

####################################################################################################################
####################################################################################################################
####################                                                                            ####################
####################                            VISUALISASI                                     ####################
####################                                                                            ####################
####################################################################################################################
####################################################################################################################


topleft, topright=st.columns([1, 3])
with topleft:
    #FILTER DATA BY DIVISI

    all_divisions = ["Semua"] + struktur_organisasi["name_of_dept"].tolist()

    st.subheader('Pilih Bidang', divider='blue')
    selected_bidang = st.selectbox("Bidang PUPR Gianyar", options=all_divisions)
    st.info("Filter sesuai bidang menunjukkan dashboard yang akan ditampilkan disesuaikan dengan bidang yang dipilih")
    #APLIKASIKAN FUNCTION FILTER
    filtered_data_aset= filter_aset_per_divisi(data_aset, struktur_organisasi, selected_bidang)

    #CLEAN NILAI UANG
    filtered_maintanance = clean_and_convert_cost(maintanance, 'cost')
    filtered_data_aset = clean_and_convert_cost(filtered_data_aset, 'nilai_perolehan')
    filtered_data_aset=filtered_data_aset.merge(filtered_maintanance, on='id_aset', how='left')


with topright:
    row1col1, row1col2=st.columns([2,1])
    with row1col1:
        #DISTRIBUSI ASET PER DIVISI 
        aset_per_bidang = (filtered_data_aset.groupby("id_dept").size().reset_index(name="jumlah_aset")) 
        aset_per_bidang = aset_per_bidang.merge(struktur_organisasi, on="id_dept", how="left")
        
        bidang_chart = HorizontalBarChart(
            aset_per_bidang,
            x_column="jumlah_aset",
            y_column="name_of_dept",
            title=" ",
            height=250,
            custom_labels={"name_of_dept": "Bidang", "jumlah_aset": "Jumlah Aset"})
        st.subheader('Jumlah Aset per Bidang', divider='blue')
        bidang_chart.render()


    with row1col2:
        #sumber dana
        total_nilai_per_sumber_dana = filtered_data_aset.groupby("sumber_dana")["nilai_perolehan"].sum().reset_index(name="total_nilai")
        sumber_dana = PieChart(
            labels=total_nilai_per_sumber_dana["sumber_dana"],
            values=total_nilai_per_sumber_dana["total_nilai"],
            title="")
        st.subheader('Sumber Dana', divider='blue')
        sumber_dana.render()
with st.container():
    row2col1, row2col2=st.columns([1, 3])
    with row2col1:
        # METRIK TOTAL JUMLAH ASET
        current_year = datetime.now().year
        
        current_year_aset = filtered_data_aset[filtered_data_aset["tahun_perolehan"] == current_year]["id_aset"].count()

        previous_year_aset = filtered_data_aset[filtered_data_aset["tahun_perolehan"] == current_year - 1]["id_aset"].count()

        
        growth_percentage = ((current_year_aset - previous_year_aset) / previous_year_aset) * 100

        # Format pertumbuhan
        growth_formatted = f"perolehan aset {growth_percentage:.0f}% dari tahun lalu" if growth_percentage != None else "N/A"

        # Status pertumbuhan (periksa None sebelum perbandingan)
        if growth_percentage > 0:
            growth_status = "up"
        elif growth_percentage < 0:
            growth_status = "down"
        else:
            growth_status = "neutral"

        # Jumlah aset tahun ini
        
        aset_value = filtered_data_aset["id_aset"].count()
        total_aset_saat_ini = filtered_data_aset["id_aset"].count()


        # Tampilkan metrik
        metrik1 = DashboardCard(
            title_1="Jumlah  Aset",
            title_2=f"sampai tahun {current_year}",
            total=aset_value,
            delta=growth_formatted,
            delta_status=growth_status
        )
        metrik1.render()
        st.info(f"Perolehan aset saat tahun ini adalah {current_year_aset} dan tahun lalu adalah {previous_year_aset}."
                " Lebih lengkap, lihat pada diagram disamping")
    with row2col2:
  
        #jumlah_aset_per_tahun = filtered_data_aset.groupby("tahun_perolehan").size().reset_index(name="jumlah_aset")
        filtered_data_aset=filtered_data_aset.merge(struktur_organisasi, on="id_dept", how="left")
        #st.write(asetbidang)
        jumlah_aset_per_tahun = filtered_data_aset.groupby(["tahun_perolehan", "name_of_dept"])["id_aset"].count().reset_index(name="total_anggaran")
        aset_per_tahun = LineChart(
                jumlah_aset_per_tahun ,
                x_column="tahun_perolehan",
                y_column="total_anggaran",
                title="",
                height=250,
                category_column="name_of_dept",
                custom_labels={"tahun_perolehan": "Tahun Perolehan", "jumlah_aset": "Jumlah Aset"}) 
        st.subheader("Jumlah Aset Berdasarkan Tahun Perolehan", divider='blue')            
        aset_per_tahun.render()

with st.container():
    rowcol1, rowcol2=st.columns([1, 3])
    with rowcol1:

        current_year_nilai= filtered_data_aset[filtered_data_aset["tahun_perolehan"] == current_year]["nilai_perolehan"].sum()

        previous_year_nilai = filtered_data_aset[filtered_data_aset["tahun_perolehan"] == current_year - 1]["nilai_perolehan"].sum()
        growth_percentage = ((current_year_nilai - previous_year_nilai) / previous_year_nilai) * 100
        # Format pertumbuhan
        growth_formatted = f"{growth_percentage:.0f}% dari tahun lalu" if growth_percentage != None else "N/A"

        # Status pertumbuhan (periksa None sebelum perbandingan)
        if growth_percentage > 0:
            growth_status = "up"
        elif growth_percentage < 0:
            growth_status = "down"
        else:
            growth_status = "neutral"
        # previous_year_nilai=format_number(previous_year_nilai)
        # current_year_nilai=format_number(current_year_nilai)
        previous_year_nilai=format_number(previous_year_nilai)
        current_year_nilai=format_number(current_year_nilai)
        if filtered_data_aset.empty:
            st.warning("Tidak ada nilai perolehan saat ini, periksa data!") 
        else:
            metrik3 = DashboardCard(
                title_1="Total Nilai Perolehan",
                title_2=f"pada tahun {current_year}",
                total=f"Rp{current_year_nilai}",
                delta=growth_formatted,
                delta_status=growth_status
            )
            metrik3.render()      
            st.info(f"Nilai perolehan tahun ini adalah Rp{current_year_nilai} dan tahun lalu adalah Rp{previous_year_nilai}."
                " Lebih lengkap, lihat pada diagram disamping")      
    with rowcol2:
        total_nilai_per_tahun = filtered_data_aset.groupby(["tahun_perolehan", "name_of_dept"])["nilai_perolehan"].sum().reset_index(name="total_nilai")
        nilai_per_tahun = LineChart(
                total_nilai_per_tahun ,
                x_column="tahun_perolehan",
                y_column="total_nilai",
                title="",
                height=250,
                category_column="name_of_dept",
                custom_labels={"tahun_perolehan": "Tahun Perolehan", "total_nilai": "Total Nilai"})
        st.subheader('Nilai Perolehan Per Tahun', divider='blue')    
        nilai_per_tahun.render()

with st.container():
    row5col1, row5col2= st.columns([1,1])

    with row5col1:
        tahun_sekarang = datetime.now().year 
        filtered_data_aset["tahun_perolehan"] = pd.to_numeric(filtered_data_aset["tahun_perolehan"], errors="coerce")
        filtered_data_aset["usia_aset"] = tahun_sekarang - filtered_data_aset["tahun_perolehan"]
        aset_usia=(filtered_data_aset.groupby(["usia_aset", "kondisi_aset"])["id_aset"].count().reset_index(name="total_aset"))

        # Sesuaikan x_column dan y_column
        kondisi_dan_rentang = HorizontalBarChart(
             aset_usia,
            x_column="total_aset",
            y_column="usia_aset",
            title="",
            height=250,
            color='kondisi_aset',
            custom_labels={"usia_aset": "Usia Aset", "total_aset": "Jumlah Aset", "kondisi_aset": "Kondisi Aset",}
        )
        st.subheader('Kondisi Aset Berdasarkan Usia', divider='blue')
        kondisi_dan_rentang.render()
    with row5col2:
        # Merging the data with 'jenis_aset'
        filtered_data_aset_merge_jenis = filtered_data_aset.merge(jenis_aset, on="kode_jenis_aset", how="left")

        # Group by 'jenis_aset' and 'kondisi_aset', then count the assets
        total_nilai_per_tahun = filtered_data_aset_merge_jenis.groupby(["jenis_aset", "kondisi_aset"])["id_aset"].count().reset_index(name="total_aset")

        # Take the top 8 based on 'total_aset'
        top_10_jenis_aset = total_nilai_per_tahun.nlargest(8, 'total_aset')

        # Calculate the 'Lainnya' category (sum of the rest)
        lainnya_data = total_nilai_per_tahun.loc[~total_nilai_per_tahun['jenis_aset'].isin(top_10_jenis_aset['jenis_aset'])]
        lainnya_data = lainnya_data.groupby("kondisi_aset")["total_aset"].sum().reset_index(name="total_aset")

        # If there's no 'Lainnya' data, set a default value
        if len(lainnya_data) == 0:
            # Adding default condition for 'Lainnya' when no other data exists
            lainnya_data = pd.DataFrame({
                'jenis_aset': ['Lainnya'],
                'kondisi_aset': ['Tidak Diketahui'],  # Default condition
                'total_aset': [0]  # Set the total as 0 for now
            })

        # Assign the majority 'kondisi_aset' to 'Lainnya' if there is any valid data for 'Lainnya'
        else:
            # Find the majority 'kondisi_aset' in the rest of the data
            majority_condition = lainnya_data.loc[lainnya_data['total_aset'].idxmax(), 'kondisi_aset']
            lainnya_data['jenis_aset'] = 'Lainnya'
            lainnya_data['kondisi_aset'] = majority_condition  # Assign the majority condition to 'Lainnya'

        # Now merge 'Lainnya' with the top 8
        top_10_and_lainnya = pd.concat([top_10_jenis_aset, lainnya_data], ignore_index=True)

        # Sort the values by 'total_aset' in descending order
        top_10_and_lainnya = top_10_and_lainnya.sort_values(by="total_aset", ascending=True)

        # Render the chart
        kondisi_dan_rentang = HorizontalBarChart(
            top_10_and_lainnya,
            x_column="total_aset",
            y_column="jenis_aset",
            title="",
            color="kondisi_aset",
            height=250,
            custom_labels={
                "total_aset": "Total Aset",
                "jenis_aset": "Jenis Aset",
                "kondisi_aset": "Kondisi Aset",
            },
        )

        # Display in Streamlit
        st.subheader('Kondisi Aset Berdasarkan Jenis', divider='blue')
        kondisi_dan_rentang.render()




with st.container():
    row4col1,row4col2, row4col3=st.columns([0.5,1,0.5])
    with row4col1:
        filtered_data_aset["datetime"] = pd.to_datetime(filtered_data_aset["datetime"])
        filtered_data_aset['year_month'] = filtered_data_aset['datetime'].dt.to_period('M')
        # monthly_cost = filtered_maintanance.groupby('year_month')['cost'].sum().reset_index(name='total_cost')
        
        current_month = pd.to_datetime("today").to_period('M')  # Mendapatkan periode bulan ini
        last_month = current_month - 1

        # Memastikan 'year_month' adalah dalam format Period untuk perbandingan
        filtered_data_aset['year_month'] = filtered_data_aset['year_month'].astype('period[M]')

        current_cost = filtered_data_aset.loc[filtered_data_aset['year_month'] == current_month, 'cost'].sum()
        last_cost = filtered_data_aset.loc[filtered_data_aset['year_month'] == last_month, 'cost'].sum()

        growth = ((current_cost - last_cost) / last_cost * 100) if last_cost > 0 else 0
        
        formatted_current_cost = format_number(current_cost)
        formatted_last_cost = format_number(last_cost)
        growth_status = "up" if growth > 0 else "down"
        growth_formatted = f"{growth:.2f}% dibandingkan bulan lalu"

        if filtered_data_aset.empty:
            st.warning("Tidak ada nilai perolehan saat ini, periksa data!") 
        else:
            metrik3 = DashboardCard(
                title_1="Total Biaya Maintenance",
                title_2=f"pada {current_month.strftime('%B %Y')}",
                total=f"Rp{formatted_current_cost}",
                delta=growth_formatted,
                delta_status=growth_status
            )
            
            metrik3.render()   
            st.info(f"Total Biaya Maintanance bulan ini Rp{current_cost} dibandingkan bulan lalu total mencapai Rp{formatted_last_cost}")       
    with row4col2:
        filtered_data_aset['freq_main'] = pd.to_numeric(filtered_data_aset['freq_main'], errors='coerce')
        freq_maint_per_jenis = filtered_data_aset_merge_jenis.groupby("jenis_aset")["freq_main"].sum().reset_index(name="total_freq_maint")

        kondisi_dan_freq = HorizontalBarChart(
            freq_maint_per_jenis,
            x_column="total_freq_maint",
            y_column="jenis_aset",
            title=" ",
            height=250,
            custom_labels={"total_freq_maint": "Frekuensi Maintanance", "jenis_aset": "Jenis Aset"})
        st.subheader('Frequensi Maintanance', divider='blue')
        kondisi_dan_freq.render()

    with row4col3:
        aset_count = filtered_data_aset['kondisi_aset'].value_counts()

        labelproposi=aset_count.index
        valueproporsi=aset_count.values

        kondisi_aset = PieChart(
            labels=labelproposi,
            values=valueproporsi,
            title="")
        st.subheader('Kondisi Aset', divider='blue')
        kondisi_aset.render()


with st.container():
    row6col1, row6col2= st.columns([1,1])
    with row6col1:
        filtered_data_aset["tahun"] = filtered_data_aset["datetime"].dt.year # Mengelompokkan data berdasarkan tahun dan menghitung total biaya pemeliharaan per tahun
        total_biaya_per_tahun = filtered_data_aset.groupby(["tahun", "name_of_dept"])["cost"].sum().reset_index(name="total_biaya")
        total_biaya= LineChart(
            total_biaya_per_tahun,
            x_column="tahun",
            y_column="total_biaya",
            title=" ",
            category_column="name_of_dept",
            height=250,
            custom_labels={"tahun": "Tahun", "total_biaya": "Total Biaya"})
        st.subheader('Nilai Maintenance Per Tahun', divider='blue')
        total_biaya.render()
    with row6col2:
        data = filtered_data_aset_merge_jenis.merge(jenis_aset, on="kode_jenis_aset")
      

        chart = HorizontalBarChartWithLine(
            data,
            x_bar="nilai_perolehan",
            y_bar="jenis_aset_y",
            x_line="cost",
            y_line="jenis_aset_x",
            bar_label="Nilai Perolehan",
            line_label="Biaya Maintenance",
            title=""
        )
        st.subheader('Perolehan dan Biaya Maintenance Aset', divider='blue')
        chart.render()
with st.container():
    row7col1, row7col2= st.columns([1,1])
    with row7col1:
        filtered_data_aset["next_maint_date"] = pd.to_datetime(filtered_data_aset["next_maint_date"]) 
        filtered_data_aset["datetime"] = pd.to_datetime(filtered_data_aset["datetime"]) 

        years_available = filtered_data_aset['next_maint_date'].dt.year.unique()
        st.subheader('Nilai Maintenance Per Bulan', divider='blue') 
        selected_year = st.selectbox('pilih tahun',years_available)

        df_filtered_month = filter_data_by_year(filtered_data_aset, 'datetime', selected_year)
        bulan_dict = {
            "January": "Januari",
            "February": "Februari",
            "March": "Maret",
            "April": "April",
            "May": "Mei",
            "June": "Juni",
            "July": "Juli",
            "August": "Agustus",
            "September": "September",
            "October": "Oktober",
            "November": "November",
            "December": "Desember",
        }

        # Tambahkan kolom nama bulan
        df_filtered_month["bulan"] = (
            df_filtered_month["datetime"].dt.strftime("%B").map(bulan_dict)
        )
        total_biaya_per_tahun = df_filtered_month.groupby(["bulan", "name_of_dept"])["cost"].sum().reset_index(name="total_biaya")
        total_biaya= BarChart(
            total_biaya_per_tahun,
            x_column="bulan",
            y_column="total_biaya",
            title=" ",
            height=250,
            custom_labels={"bulan": "Bulan", "total_biaya": "Total Biaya"})
          
        total_biaya.render()
    with row7col2:
        vendor_counts = filtered_data_aset["vendor"].value_counts().reset_index(name="jumlah_pemeliharaan") 
        vendor_counts.columns = ["vendor", "jumlah_pemeliharaan"]
        vendor_name = BarChart(
            vendor_counts,
            x_column="vendor",
            y_column="jumlah_pemeliharaan",
            title="",
            height=335,
            custom_labels={"vendor": "Vendor", "jumlah_pemeliharaan": "Jumlah Maintenance"})
        st.subheader('Vendor Maintanance', divider='blue')  
        vendor_name.render()        
with st.container():
     col1, col2=st.columns([1,1])   
     with col1:
        # df_combined = filtered_data_aset.merge(filtered_data_aset, on="id_aset", how="left") 
        df_combined = filter_data_by_year(filtered_data_aset, 'next_maint_date', selected_year)

        gantt_chart = GanttChart(df_combined, task_column='action', 
                                 start_column='next_maint_date', end_column='datetime', 
                                 resource_column='vendor', title='')
        st.subheader('Kegiatan Maintanance', divider='blue')
        gantt_chart.render()

     with col2:
        #data_org = filtered_data_aset.merge(struktur_organisasi, on="id_dept", how="left")
        # st.write(filtered_data_aset)
        st.subheader('Jadwal Maintenance', divider='blue')
        columns_needed = ['nama_aset', 'kondisi_aset', 'next_maint_date', 'name_of_dept']
        filtered_data = filtered_data_aset[columns_needed]
        today = pd.Timestamp.now()
        filtered_data = filtered_data[filtered_data['next_maint_date'] >= today]
        if filtered_data.empty:
            st.warning("Tidak ada jadwal pemeliharaan aset sejauh ini.")
        else:
            table_data = filtered_data.values.tolist()
            header = filtered_data.columns.tolist()
            table_data.insert(0, header)
            fig = ff.create_table(table_data, height_constant=60)
            st.subheader('Jadwal Pemeliharaan', divider='blue')
            st.plotly_chart(fig)

