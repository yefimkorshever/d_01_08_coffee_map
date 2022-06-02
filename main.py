import json
import os
import requests
import folium
from geopy import distance
from flask import Flask


def hello_world():
    with open('index.html', 'r') as html_file:
        return html_file.read()


def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url,
                            params={
                                "geocode": address,
                                "apikey": apikey,
                                "format": "json",
                            })
    response.raise_for_status()
    found_response = response.json()['response']
    found_places = found_response['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lat, lon


def get_distance(coffee_house):
    return coffee_house['distance']


def main():
    location = input('Где вы находитесь? ')
    ya_api_key = os.environ['YA_API_KEY']
    current_coordinates = fetch_coordinates(ya_api_key, location)
    if current_coordinates is None:
        print('Не удалось определить местоположение')
        return

    local_map = folium.Map(location=current_coordinates, zoom_start=15)
    tooltip = "Вы здесь!"
    folium.Marker(
        current_coordinates,
        popup=tooltip,
        tooltip=tooltip,
        icon=folium.Icon(color="red", icon="info-sign"),
    ).add_to(local_map)

    with open('coffee.json', 'r', encoding='CP1251') as coffee_file:
        file_text = coffee_file.read()

    file_content = json.loads(file_text)
    coffee_houses = list()

    for file_item in file_content:
        coordinates = file_item['geoData']['coordinates']
        latitude = coordinates[1]
        longitude = coordinates[0]
        distance_km = distance.distance(current_coordinates,
                                        (latitude, longitude)).km

        coffee_house = {
            'title': file_item['Name'],
            'distance': distance_km,
            'latitude': latitude,
            'longitude': longitude,
        }

        coffee_houses.append(coffee_house)

    sorted_coffee_houses = sorted(coffee_houses, key=get_distance)
    number_of_nearest = 5
    nearest_coffee_houses = sorted_coffee_houses[:number_of_nearest]

    for coffee_house in nearest_coffee_houses:
        coffee_house_coordinates = (
            coffee_house['latitude'],
            coffee_house['longitude'],
        )

        title = coffee_house['title']

        folium.Marker(
            location=coffee_house_coordinates,
            popup=title,
            tooltip=title,
            icon=folium.Icon(color="green", icon="info-sign"),
        ).add_to(local_map)

    local_map.save('index.html')
    app = Flask(__name__)
    app.add_url_rule('/', 'hello', hello_world)
    app.run('0.0.0.0')


if __name__ == '__main__':
    main()
