import os
import folium       # type: ignore
import pandas as pd # type: ignore


#
# Carga del archivo a un DataFrame
#
def load_affiliations():
    '''Carga el archivo scopus-papers.csv y retorna un dataframe con la
    columna "Affiliations"'''

    df= pd.read_csv(
        (
            'https://raw.githubusercontent.com/jdvelasq/datalabs/'
            'master/datasets/scopus-papers.csv'
        ),
        sep = ',',
        index_col = None,
    )[['Affiliations']]
    return df

#
# Eliminar valores NA
#
def remove_na_rows(affiliations):
    '''Elimina las filas con valores nulos en la columna "Affiliations"'''

    affiliations = affiliations.copy()
    affiliations = affiliations.dropna(subset=['Affiliations'])

    return affiliations

#
# Escoger los países y añadirlos a una columna
#
def add_countries_column(affiliations):
    '''Transforma la columna 'Affiliations' a una lista de paises.'''

    affiliations = affiliations.copy()
    affiliations['countries'] = affiliations['Affiliations'].copy()
    affiliations['countries'] = affiliations['countries'].str.split(';')
    affiliations['countries'] = affiliations['countries'].map(
        lambda x: [y.split(',') for y in x]
    )
    affiliations['countries'] = affiliations['countries'].map(
        lambda x: [y[-1].strip() for y in x]
    )
    affiliations['countries'] = affiliations['countries'].map(set)
    affiliations['countries'] = affiliations['countries'].str.join(', ')

    return affiliations

#
# Limpieza de nombres de países
#
def clean_countries(affiliations):

    affiliations = affiliations.copy()
    affiliations['countries'] = affiliations['countries'].str.replace(
        'United States', 'United States of America'
    )
    return affiliations

#
# Frecuencia de Países
#
def count_country_frequency(affiliations):
    '''Cuenta la frecuencia de cada país en la columna "countries"'''

    countries = affiliations['countries'].copy()
    countries = countries.str.split(', ')
    countries = countries.explode()
    countries = countries.value_counts()
    return countries

#
# Plot para cada país
#
def plot_world_map(countries):
    '''Grafica un mapa mundial con la frecuencia de cada país'''

    countries = countries.copy()
    countries = countries.to_frame()
    countries = countries.reset_index()

    m = folium.Map(location=[0, 0], zoom_start=2)

    folium.Choropleth(
        geo_data=(
            'https://raw.githubusercontent.com/python-visualization/'
            'folium/master/examples/data/world-countries.json'
        ),
        data=countries,
        columns=['countries', 'count'],
        key_on='feature.properties.name',
        fill_color='Greens',
    ).add_to(m)

    m.save('files/output/map.html')

#
# Main
#
def make_worldmap():
    '''Función principal'''

    if not os.path.exists('files'):
        os.makedirs('files')

    affiliations = load_affiliations()
    affiliations = remove_na_rows(affiliations)
    affiliations = add_countries_column(affiliations)
    affiliations = clean_countries(affiliations)
    countries = count_country_frequency(affiliations)
    countries.to_csv('files/output/countries.csv')
    plot_world_map(countries)

if __name__ == '__main__':
    make_worldmap()