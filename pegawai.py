import streamlit as st
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine
from library import DashboardCardNoDelta, GenderAgeBarChart, GenderBarChart, BarChart, DonutChart, LineChart, PieChart, HorizontalBarChart, ChatCard, FunnelChart, DashboardCard, DonutChart2

st.set_page_config(
    page_title="Dashboard Pegawai",
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


def filter_pegawai_by_divisi(data_pegawai, struktur_organisasi, selected_bidang):
    if selected_bidang != "Semua":
        selected_id_dept = struktur_organisasi.loc[struktur_organisasi["name_of_dept"] == selected_bidang, "id_dept"].values[0]
        filtered_data_pegawai = data_pegawai[data_pegawai["id_pegawai"].isin(
            struktur_organisasi[struktur_organisasi["id_dept"] == selected_id_dept]["id_pegawai"])]
        # filtered_data_pegawai= data_pegawai[data_pegawai["id_dept"] == selected_id_dept]
    else:
        filtered_data_pegawai = data_pegawai
    return filtered_data_pegawai

def process_pegawai_data(data_pegawai):
    data_pegawai[["Tempat", "Tanggal_Lahir"]] = data_pegawai["tempat_tanggal_lahir"].str.split(", ", expand=True)
    data_pegawai["Tanggal_Lahir"] = pd.to_datetime(data_pegawai["Tanggal_Lahir"])
    today = datetime.today()
    data_pegawai["Usia"] = data_pegawai["Tanggal_Lahir"].apply(lambda x: today.year - x.year - ((today.month, today.day) < (x.month, x.day)))
    return data_pegawai

def fetch_data(file_name):
    return pd.read_excel(file_name)

data_pegawai = fetch_data("data_pegawai.xlsx")
struktur_organisasi = fetch_data("struktur_organisasi.xlsx")
data_pendidikan = fetch_data("data_pendidikan.xlsx")
data_golongan = fetch_data("data_golongan.xlsx")
def process_umur_bins(data):
    bins = [18, 27, 37, 47, 57, 67]  # Bins usia
    labels = ['18-27', '28-37', '38-47', '48-57', '58-67']  # Label untuk bins
    data['Usia_Bin'] = pd.cut(data['Usia'], bins=bins, labels=labels, right=True)
    return data
        # Klasifikasi berdasarkan kelompok usia
def klasifikasi_usia(usia):
    if usia < 15:
        return "Anak-anak"
    elif 15 <= usia <= 24:
        return "Usia Muda"
    elif 25 <= usia <= 34:
        return "Pekerja Awal"
    elif 35 <= usia <= 44:
        return "Paruh Baya"
    elif 45 <= usia <= 54:
        return "Pra-Pensiun"
    elif 55 <= usia <= 64:
        return "Pensiun"
    else:
        return "Usia Lanjut"

####################################################################################################################
####################################################################################################################
####################                                                                            ####################
####################                            VISUALISASI                                     ####################
####################                                                                            ####################
####################################################################################################################
####################################################################################################################
#ROW 1
with st.container():
    col1, col2=st.columns([1,3])
    with col1:
        all_divisions = ["Semua"] + struktur_organisasi["name_of_dept"].tolist()
        st.subheader('Pilih Bidang', divider='blue')
        selected_bidang = st.selectbox("Pilih Bidang", options=all_divisions)
        st.info("Filter sesuai bidang menunjukkan dashboard yang akan ditampilkan disesuaikan dengan bidang yang dipilih")
        filtered_data_pegawai = filter_pegawai_by_divisi(data_pegawai, struktur_organisasi, selected_bidang)
    with col2:
        pegawai_per_bidang = filtered_data_pegawai.merge(struktur_organisasi, on="id_pegawai", how="left")

        # Menambahkan kolom gender dan jumlah pegawai per divisi berdasarkan gender
        pegawai_per_bidang['jenis_kelamin'] = filtered_data_pegawai['jenis_kelamin']  # Kolom jenis_kelamin L/P
        jumlah_pegawai_gender = pegawai_per_bidang.groupby(["name_of_dept", "jenis_kelamin"])["id_pegawai"].count().reset_index(name="jumlah_pegawai")

        # Mengganti kode jenis_kelamin menjadi label lebih deskriptif (jika diperlukan)
        jumlah_pegawai_gender['jenis_kelamin'] = jumlah_pegawai_gender['jenis_kelamin'].map({'L': 'Laki-laki', 'P': 'Perempuan'})
        gender_chart = GenderBarChart(
            data=jumlah_pegawai_gender,
            x_column="name_of_dept",
            y_column="jumlah_pegawai",
            title="",
            custom_labels={"name_of_dept": "Bidang", "jumlah_pegawai": "Jumlah Pegawai"},
            height=250
        )
        st.subheader('Distribusi Pegawai per Divisi', divider='blue')

        gender_chart.render() 

#ROW 2          
with st.container():
    rowcol2, rowcol3, rowcol4=st.columns([2,1,1])

    with rowcol2:
        data_umur = process_pegawai_data(filtered_data_pegawai)
        data = pd.merge(data_umur, struktur_organisasi, on='id_pegawai')
        data = process_umur_bins(data)
        data2 = data.groupby(["Usia_Bin", "jenis_kelamin", "name_of_dept"])["id_pegawai"].count().reset_index(name="total_pegawai")
        data2['jenis_kelamin'] = data2['jenis_kelamin'].map({'L': 'Laki-laki', 'P': 'Perempuan'})
        gender_age_chart = GenderAgeBarChart(
            data=data2,
            x_column="Usia_Bin",
            y_column="total_pegawai",
            category_column="jenis_kelamin",
            title=" ",
            custom_labels={"Usia_Bin": "Rentang Usia", "total_pegawai": "Jumlah Pegawai", "jenis_kelamin": "Jenis Kelamin"},
            height=250
        )
        st.subheader('Distribusi Usia Pegawai', divider='blue')
        gender_age_chart.render()          
    with rowcol3:
        gender_counts = filtered_data_pegawai['jenis_kelamin'].value_counts()
        labels = gender_counts.index.map({'P': 'Perempuan', 'L': 'Laki-laki'})
        values = gender_counts.values
        total= filtered_data_pegawai['nama_lengkap'].count()
        
        donut_gender = PieChart(
            labels=labels,
            values=values,
            title=" ")
        st.subheader('Gender Pegawai', divider='blue')
        donut_gender.render()        
    with rowcol4:
        head_count = struktur_organisasi['head_of_dept'].value_counts()

        labelproposi=head_count.index
        valueproporsi=head_count.values
        donut_proporsipegawai = DonutChart2(
            labels=labelproposi,
            values=valueproporsi,
            total=filtered_data_pegawai['id_pegawai'].count(),
            text='Pegawai',
            title="")
        st.subheader('Proporsi Pegawai', divider='blue')
        donut_proporsipegawai.render()

#ROW 3
st.subheader('Metrik', divider='blue')
with st.container():
    col1, col2, col3, col4=st.columns([1,1,1,1])
    with col1:
        total_pegawai = filtered_data_pegawai.shape[0]
        jenis_kelamin_mayoritas = filtered_data_pegawai['jenis_kelamin'].mode()[0]  # 'L' atau 'P'
        jenis_kelamin_label = "Laki-laki" if jenis_kelamin_mayoritas == 'L' else "Perempuan"
          # 'Tetap' atau 'Kontrak'
        #status_color = 'green' if status_pegawai_mayoritas == 'Tetap' else 'red'
        description = f"Mayoritas pegawai adalah {jenis_kelamin_label}"

        dashboard_card = DashboardCardNoDelta(
            title_1="Total Pegawai",
            title_2=f"PUPR Gianyar {selected_bidang} adalah",
            total=total_pegawai,
            description=description,
            status_color='green'
        )
        dashboard_card.render()
    with col2:
        status_pegawai_mayoritas = filtered_data_pegawai['status_pegawai'].mode()[0]
        jumlah_status_mayoritas = data_pegawai[data_pegawai['status_pegawai'] == status_pegawai_mayoritas].shape[0]
        description2 = f"Mayoritas Pegawai berstatus {status_pegawai_mayoritas} dengan jumlah {jumlah_status_mayoritas}"
        dashboard_card2 = DashboardCardNoDelta(
            title_1="Mayoritas Pegawai",
            title_2=f"PUPR Gianyar {selected_bidang} berstatus",
            total=status_pegawai_mayoritas,
            description=description2,
            status_color='green'
        )
        dashboard_card2.render()
    with col3:
         # 1. Menambahkan kolom untuk usia tahun sebelumnya
        data_umur['Usia_tahun_sebelumnya'] = data_umur['Usia'] - 1

        # 2. Hitung pegawai yang akan pensiun tahun ini (Usia > 59 tahun saat ini)
        pegawai_pensiun_tahun_ini = data_umur[data_umur['Usia'] > 59]

        # 3. Hitung pegawai yang akan pensiun tahun sebelumnya (Usia > 59 tahun tahun lalu)
        pegawai_pensiun_tahun_sebelumnya = data_umur[data_umur['Usia_tahun_sebelumnya'] > 59]

        # 4. Hitung pegawai yang akan pensiun tahun ini tapi belum pensiun tahun lalu
        pegawai_pensiun_tahun_ini_valid = pegawai_pensiun_tahun_ini[~pegawai_pensiun_tahun_ini['id_pegawai'].isin(pegawai_pensiun_tahun_sebelumnya['id_pegawai'])]

        # Jumlah pegawai yang akan pensiun tahun ini dan tahun sebelumnya
        jumlah_pensiun_tahun_ini = pegawai_pensiun_tahun_ini_valid.shape[0]
        jumlah_pensiun_tahun_sebelumnya = pegawai_pensiun_tahun_sebelumnya.shape[0]

        # Deskripsi perbandingan jumlah pensiun tahun ini dan tahun sebelumnya
        if jumlah_pensiun_tahun_ini > jumlah_pensiun_tahun_sebelumnya:
            perbandingan = "Lebih banyak pegawai yang akan pensiun tahun ini dibandingkan tahun lalu."
        elif jumlah_pensiun_tahun_ini < jumlah_pensiun_tahun_sebelumnya:
            perbandingan = "Lebih sedikit pegawai yang akan pensiun tahun ini dibandingkan tahun lalu."
        else:
            perbandingan = "Jumlah pegawai yang akan pensiun tahun ini sama dengan tahun lalu."

        # Menyusun deskripsi
        description3 = f"{perbandingan}"
        dashboard_card3 = DashboardCardNoDelta(
            title_1="Pegawai yang Akan Pensiun",
            title_2="Informasi Pensiun Pegawai",
            total=jumlah_pensiun_tahun_ini,
            description=description3,
            status_color="green"  # Bisa diganti sesuai warna yang diinginkan
        )

        dashboard_card3.render()
    with col4:
        rata_rata_usia = data_umur['Usia'].mean()
        data_umur['Kategori Usia'] = data_umur['Usia'].apply(klasifikasi_usia)
        description4 = f"Mayoritas pegawai berada di kategori: {klasifikasi_usia(rata_rata_usia)}."
        dashboard_card4 = DashboardCardNoDelta(
            title_1="Rata-rata Usia Pegawai",
            title_2="Informasi Usia Pegawai",
            total=f"{rata_rata_usia:.0f} Tahun",  # Menampilkan rata-rata usia dengan 2 desimal
            description=description4,
            status_color="green"  # Bisa diganti sesuai warna yang diinginkan
        )

        dashboard_card4.render()
st.write('''''')          
#ROW 4
with st.container():
    row2col,  row2col2, row2col3= st.columns([1,1,1])  
    with row2col:
        data_umur['Pensiun'] = data_umur['Usia'] > 60
        pensiun_perempuan = data_umur[(data_umur['jenis_kelamin'] == 'P') & (data_umur['Pensiun'] == True)]
        pensiun_laki_laki = data_umur[(data_umur['jenis_kelamin'] == 'L') & (data_umur['Pensiun'] == True)]
        
        jumlah_pensiun_perempuan = pensiun_perempuan['Pensiun'].count()
        jumlah_pensiun_laki_laki = pensiun_laki_laki['Pensiun'].count()
        total_pensiun = jumlah_pensiun_perempuan + jumlah_pensiun_laki_laki

        labels = ['Perempuan', 'Laki-Laki']
        values = [jumlah_pensiun_perempuan, jumlah_pensiun_laki_laki]

        umur_pensiun = PieChart(
        labels=labels,
        values=values,
        title=" ")
        st.subheader('Pegawai Pensiun', divider='blue')
        umur_pensiun.render()     

    with row2col2:
        status_pegawai=filtered_data_pegawai["status_pegawai"].value_counts()
        most_frequent_status = status_pegawai.idxmax()
        labels = status_pegawai.index
        values = status_pegawai.values
        total= filtered_data_pegawai['nama_lengkap'].count()

        donut_status = DonutChart(
            labels=labels,
            values=values,
            title=" ",
            text='Pegawai',
            total=total)
        st.subheader('Status Pekerja', divider='blue')
        donut_status.render()
    with row2col3:
        status_perkawinan=filtered_data_pegawai["status_perkawinan"].value_counts()
        most_frequent_status = status_perkawinan.idxmax()
        labels = status_perkawinan.index
        values = status_perkawinan.values
        total= filtered_data_pegawai['nama_lengkap'].count()

        donut_perkawinan = PieChart(
        labels=labels,
        values=values,
        title="")
        st.subheader('Status Perkawinan', divider='blue')
        donut_perkawinan.render()
with st.container():
    row4col1, row4col2, row4col3= st.columns([ 1,1,1])

    with row4col1:
            education_counts = (data_pegawai.groupby("id_pegawai").size().reset_index(name="jumlah_pegawai").merge(data_pendidikan, left_on="id_pegawai", right_on="id_pegawai", how="left"))
            education_counts_formal = education_counts[education_counts['jenis_pendidikan'] == 'formal']
            
          
            education_chart = HorizontalBarChart(
            education_counts_formal,
            y_column="jenjang_pendidikan",
            x_column="jumlah_pegawai",
            title="",
            height=300,
            custom_labels={"jumlah_pegawai": "Jumlah Pegawai", "jenjang_pendidikan": "Pendidikan"})
            st.subheader('Distribusi  Pendidikan Terakhir', divider='blue')
            education_chart.render()
    with row4col2:
            education_counts_nonformal = education_counts[education_counts['jenis_pendidikan'] != 'formal']

            # Mengambil 6 jurusan teratas berdasarkan jumlah pegawai terbanyak
            top_6_jurusan = education_counts.nlargest(6, 'jumlah_pegawai')

            # Menghitung jumlah pegawai untuk kategori "Lainnya"
            jumlah_lainnya = education_counts.loc[~education_counts['bidang_pendidikan'].isin(top_6_jurusan['bidang_pendidikan'])]
            jumlah_lainnya = jumlah_lainnya['jumlah_pegawai'].sum()

            # Membuat DataFrame untuk kategori "Lainnya"
            lainnya = pd.DataFrame({'bidang_pendidikan': ['Lainnya'], 'jumlah_pegawai': [jumlah_lainnya]})

            # Menggabungkan 6 jurusan teratas dengan kategori "Lainnya"
            top_6_jurusan = pd.concat([top_6_jurusan, lainnya], ignore_index=True)
            top_6_jurusan = top_6_jurusan.sort_values(by="jumlah_pegawai", ascending=True)
            education_chart2 = HorizontalBarChart(
            top_6_jurusan,
            y_column="jenjang_pendidikan",
            x_column="jumlah_pegawai",
            title="",
            height=300,
            custom_labels={"jumlah_pegawai": "Jumlah Pegawai", "jenjang_pendidikan": "Pelatihan"})
            st.subheader('Distribusi Pelatihan Pegawai', divider='blue')
            education_chart2.render()
    with row4col3:
            #education_bidang_jurusan['bidang_pendidikan'] = education_bidang_jurusan.apply(lambda x: x['bidang_pendidikan'] if x['Values'] >= 5 else 'Others', axis=1)
            education_bidang_jurusan = education_counts[education_counts['bidang_pendidikan'] == 'formal']
            education_chart3 = HorizontalBarChart(
            education_counts_nonformal,
            y_column="bidang_pendidikan",
            x_column="jumlah_pegawai",
            title="",
            height=300,
            custom_labels={"jumlah_pegawai": "Jumlah Pegawai", "bidang_pendidikan": "Jurusan"})

            st.subheader('Jurusan Mayoritas Pegawai', divider='blue')
            education_chart3.render()
with st.container():
    rowleft, rowright=st.columns([1,2])

    with rowright:
        # Misalnya pegawai_golongan adalah hasil penggabungan data yang sudah ada
        pegawai_golongan = (
            data_pegawai
            .merge(struktur_organisasi, on="id_pegawai", how="left")
            .merge(data_golongan, on="id_golongan_pangkat", how="left")
        )
        jabatan_distribution = (
            pegawai_golongan.groupby("nama_pangkat")["id_pegawai"]
            .count()
            .reset_index(name="jumlah_pegawai")
        )
        pattern = r"(Ahli Pertama|Ahli Muda|Ahli Madya|Ahli Utama|Pemula|Terampil|Mahir|Penyelia)"

        # Mengekstrak jabatan fungsional dan membuat kolom baru 'jabatan_fungsional'
        pegawai_golongan['jabatan_fungsional'] = pegawai_golongan['nama_pangkat'].str.extract(pattern)

        # Visualisasi Distribusi Jabatan Fungsional
        jabatan_distribution = pegawai_golongan['jabatan_fungsional'].value_counts().reset_index()
        jabatan_distribution.columns = ['Jabatan Fungsional', 'Jumlah Pegawai']

        # Membuat Bar Chart
        jabatan_fungsional_chart = HorizontalBarChart(
            jabatan_distribution,
            x_column='Jumlah Pegawai',
            y_column='Jabatan Fungsional',
            title=" ",
            height=250,
            custom_labels={"Jumlah Pegawai": "Jumlah Pegawai", "Jabatan Fungsional": "Jabatan Fungsional"}
        )

        # Menampilkan chart di Streamlit
        st.subheader('Kelas Jabatan Fungsional', divider='blue')
        jabatan_fungsional_chart.render()

        # # Menghitung distribusi jabatan berdasarkan nama pangkat
        # jabatan_distribution = (
        #     pegawai_golongan.groupby("nama_pangkat")["id_pegawai"]
        #     .count()
        #     .reset_index(name="jumlah_pegawai")
        # )

        # # Mengurutkan dan memilih 5 jabatan fungsional teratas
        # top_5_jabatan = jabatan_distribution.nlargest(8, 'jumlah_pegawai')

        # # Menghitung jumlah pegawai untuk kategori "Lainnya"
        # jumlah_lainnya = jabatan_distribution.loc[~jabatan_distribution['nama_pangkat'].isin(top_5_jabatan['nama_pangkat'])]
        # jumlah_lainnya = jumlah_lainnya['jumlah_pegawai'].sum()

        # # Membuat DataFrame untuk kategori "Lainnya"
        # lainnya = pd.DataFrame({'nama_pangkat': ['Lainnya'], 'jumlah_pegawai': [jumlah_lainnya]})

        # # Menggabungkan 5 jabatan teratas dengan kategori "Lainnya"
        # top_5_jabatan = pd.concat([top_5_jabatan, lainnya], ignore_index=True)
        # top_5_jabatan = top_5_jabatan.sort_values(by="jumlah_pegawai", ascending=True)

        # # Membuat Horizontal Bar Chart
        # jabatan_fungsional = HorizontalBarChart(
        #     top_5_jabatan,
        #     x_column="jumlah_pegawai",
        #     y_column="nama_pangkat",
        #     title=" ",
        #     height=300,
        #     custom_labels={"jumlah_pegawai": "Jumlah Pegawai", "nama_pangkat": "Jabatan Fungsional"}
        # )
        # st.subheader('Distribusi Jabatan Fungsional', divider='blue')
        # jabatan_fungsional.render()

    with rowleft:
            golongan_distribution = (
                pegawai_golongan.groupby("nama_golongan")["id_pegawai"]
                .count()
                .reset_index(name="jumlah_pegawai"))   
            labels = golongan_distribution['nama_golongan']
            values = golongan_distribution['jumlah_pegawai']
            
            donut_gender = PieChart(
                labels=labels,
                values=values,
                title=" ")
            st.subheader('Distribusi Golongan', divider='blue')
            donut_gender.render() 
            # funnel_golongan = FunnelChart(
            # #     golongan_distribution,
            # #     x_column="nama_golongan",
            # #     y_column="jumlah_pegawai",
            # #     title=" ",
            # #     custom_labels={"jumlah_pegawai": "Jumlah Pegawai", "nama_golongan": "Golongan"})
            # # st.subheader('Distribusi Golongan', divider='blue')    
            # # funnel_golongan.render()




         

    


