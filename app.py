import streamlit as st
import pandas as pd
import folium
import json 

#Cabeçalho
st.title("Conjunto de dados sobre população global e migração")

st.markdown("""
    <style>
        .st-emotion-cache-yw8pof{
            width: 100%;
              padding: 6rem 1rem 10rem;
              max-width: 88rem;
        }
    </style>
""", unsafe_allow_html=True)


df = pd.read_csv('dataset.csv')

total_migration = df['netMigration'].sum()

def format_number(num):

    millions = int(num // 1_000_000)  
    thousands = int((num % 1_000_000) // 1_000) 

    formatted = f"{millions} M"
    if thousands > 0:
        formatted += f"  {thousands} mil"
    
    return formatted

paises_agrupados = df.groupby('country')['netMigration'].sum().reset_index()

saldo = paises_agrupados['netMigration'].values


menor_valor_saldo = saldo.min()
maior_valor_saldo = saldo.max()
media_valor_saldo = (saldo.min() + saldo.max())/ 2
media_menor_media_valor_saldo = (saldo.min() + media_valor_saldo)/ 2
media_maior_media_valor_saldo = (saldo.max() + media_valor_saldo)/ 2


def create_map(feature):

    linha = paises_agrupados[paises_agrupados['country'] == feature['properties']['name']]

    if linha.empty:
        return {'fillColor': 'gray', 'fillOpacity': 1}
    else :
        if menor_valor_saldo <= linha['netMigration'].values[0] < media_menor_media_valor_saldo:
            return {'fillColor': 'red', 'fillOpacity': 1}
        elif media_menor_media_valor_saldo < linha['netMigration'].values[0] <= media_valor_saldo:
            return {'fillColor': '#FF7F00', 'fillOpacity': 1}
        elif media_valor_saldo < linha['netMigration'].values[0] <= media_maior_media_valor_saldo:
            return {'fillColor': '#FFFF00', 'fillOpacity': 1}
        return {'fillColor': 'green', 'fillOpacity': 1}


def add_legend(map_object):
    legend_html = f"""
    <div style="
        position: fixed; 
        bottom: 20px; left: 20px; width: 240px; height: 170px; 
        background-color: white; z-index:9999; font-size:14px;
        border:2px solid grey; border-radius:5px; padding:10px; display: flex; flex-direction: column; gap: 8px">
        <b>Legenda:</b>
        <div style=" display: flex; flex-direction: column; gap: 4px;">
            <div>
                <i style="background:green; color:white; border: 1px solid black;">&nbsp;&nbsp;&nbsp;&nbsp;</i>
                <label style = "font-weight: bold;font-size: 12px;"> {media_maior_media_valor_saldo} < Saldo <= {maior_valor_saldo}</label>
            </div>
            <div>
                <i style="background:#FFFF00; color:white; border: 1px solid black;">&nbsp;&nbsp;&nbsp;&nbsp;</i>
                <label style = "font-weight: bold;font-size: 12px;"> {media_valor_saldo} <= Saldo < {media_maior_media_valor_saldo}</label>
            </div>
            <div>
                <i style="background:#FF7F00; color:white; border: 1px solid black;">&nbsp;&nbsp;&nbsp;&nbsp;</i>
                <label style = "font-weight: bold;font-size: 12px;">{media_menor_media_valor_saldo} <= Saldo < {media_valor_saldo} </label>
            </div>
            <div>
                <i style="background:red; color:white; border: 1px solid black;">&nbsp;&nbsp;&nbsp;&nbsp;</i>
                <label style = "font-weight: bold;font-size: 12px;"> {menor_valor_saldo} <= Saldo < {media_menor_media_valor_saldo} </label>
            </div>
            <div>
                <i style="background:gray; color:white; border: 1px solid black;">&nbsp;&nbsp;&nbsp;&nbsp;</i> 
                <label style = "font-weight: bold;font-size: 12px;"> Não consta no dataset </label>
            </div>
        </div>
    </div>
    """
    map_object.get_root().html.add_child(folium.Element(legend_html))


def style_df(val):
    color = 'green' if val > 0 else 'red'
    return f'color: {color}; font-weight: bold; font-size: 20px;'


main_col1, main_col2 = st.columns(2)

with main_col1:

    col1, col2, col3 = st.columns(3)

    with col1:
        container = st.container(border=True)
        with container:
            st.text('Total de migrações ')
            st.markdown(f'#### 🌍 {format_number(total_migration)}')

    with col2:
        year_with_most_migration = df.groupby('year')['netMigration'].sum().idxmax()
        container = st.container(border=True)
        with container:
            st.text('Ano com mais migrações')
            st.markdown(f'#### 📆 {year_with_most_migration}')

    with col3:
        country_with_most_migration = df.groupby('country')['netMigration'].sum().idxmax()
        container = st.container(border=True)
        with container:
            st.text('País com mais migração')
            st.markdown(f'#### {country_with_most_migration}')


    with open('paises.json') as f:
        paises = json.load(f)
        m = folium.Map(location=[20, 0], zoom_start=2)
        folium.GeoJson(paises, style_function=create_map).add_to(m)
        add_legend(m)
        st.components.v1.html(m._repr_html_(), height=400)

    st.markdown("### Saldo migratório agrupado por país")
    paises_agrupados_renomeado = paises_agrupados.rename(columns={'netMigration': 'Saldo Migratório', 'country': 'Nome do país'})
    paises_agrupados_renomeado = paises_agrupados_renomeado.reset_index(drop=True)
    st.dataframe(paises_agrupados_renomeado.style.applymap(style_df, subset=['Saldo Migratório']).format({"Saldo Migratório": "{:.1f}"}), height=350, width=600)



min_year = df['year'].min()
max_year = df['year'].max()


with main_col2:

    lista_paises = paises_agrupados['country'].to_list()

    container = st.container()

    sorter_order = ['Maiores', 'Menores']

    with container:
        
        st.markdown("### Top 10 saldos migratórios mundiais")
        
        dropdown = st.selectbox('Filtrar', sorter_order)
        selected_year = st.slider('Filtrar por um determinado ano', min_year, max_year)
        paises_filtrados_ano = df.filter(['country', 'year', 'netMigration']).loc[df['year'] == selected_year]
        top_10_filtrados_ano = paises_filtrados_ano.groupby('country')['netMigration'].sum().reset_index()
    
        if dropdown == 'Maiores':
            top_10_filtrados_ano = top_10_filtrados_ano.nlargest(10, 'netMigration')
        elif dropdown == 'Menores':
            top_10_filtrados_ano = top_10_filtrados_ano.nsmallest(10, 'netMigration')

        
        st.bar_chart(top_10_filtrados_ano.set_index('country').sort_values('netMigration', ascending=False), height=300)


        st.markdown("### Histórico migratório durante todo o período analisado")

        dropdown = st.selectbox('Escolha um país', lista_paises)

        pais_especifico_filtrado_ano = df.groupby(['country','year'])['netMigration'].sum().reset_index()
        pais_especifico_filtrado_ano = pais_especifico_filtrado_ano[pais_especifico_filtrado_ano['country'] == dropdown]

        pais_especifico_filtrado_ano['year'] = pd.to_datetime(pais_especifico_filtrado_ano['year'], format='%Y')

        st.line_chart(pais_especifico_filtrado_ano.set_index('year')['netMigration'],height=300)
