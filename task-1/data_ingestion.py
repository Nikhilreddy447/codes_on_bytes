import requests
import csv
import gzip
import json
from io import BytesIO

#  OpenWeather API key
api_key = '93587c464e3105eb86518286f8fb69fa'

# URL for the OpenWeather API endpoint to get a list of cities
city_list_url = 'http://bulk.openweathermap.org/sample/city.list.json.gz'

# URL for the OpenWeather API endpoint to get weather information for a specific city
weather_url = 'http://api.openweathermap.org/data/2.5/weather'

# Create a CSV file to store the weather information
csv_file_path = 'task-1/weather_data.csv'

# Function to get the list of cities from the OpenWeather API
def get_city_list(api_key,limit=500):
    params = {'appid': api_key}
    response = requests.get(city_list_url, params=params)
    try:
        # Decompress the content
        decompressed_data = gzip.decompress(response.content)
        # Decode the decompressed content as UTF-8
        data = decompressed_data.decode('utf-8')
        # Parse the JSON data
        json_data = json.loads(data)
        return [city['name'] for city in json_data]
    except Exception as e:
        print(f"Error: {e}")
        return []

# Open the CSV file in write mode with explicit encoding
with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
    # Create a CSV writer object
    csv_writer = csv.writer(csv_file)

    # Write the header row
    csv_writer.writerow(['City', 'Temperature (Celsius)', 'Description', 'Humidity'])

    # Get the list of cities
    cities = get_city_list(api_key,limit=500)
    
    cities_processed = 0

    # Iterate through each city
    for city in cities:
        # Set up the parameters for the API request
        params = {'q': city, 'appid': api_key, 'units': 'metric'}  # 'units': 'metric' for Celsius

        # Make the API request
        response = requests.get(weather_url, params=params)
        try:
            data = response.json()
        except requests.exceptions.JSONDecodeError as e:
            print(f"Error decoding JSON for {city}: {e}")
            print(f"Response content: {response.content.decode('utf-8')}")
            continue

        # Check if the API request was successful
        if response.status_code == 200:
            # Extract relevant information from the API response
            city_name = data['name']
            temperature = data['main']['temp']
            description = data['weather'][0]['description']
            humidity = data['main']['humidity']

            # Write the data to the CSV file
            csv_writer.writerow([city_name, temperature, description, humidity])
            print(f"Data for {city_name} written to CSV.")
            
            cities_processed=cities_processed+1
            if cities_processed >= 500:
                print("Maximum number of cities processed. Exiting.")
                break
        else:
            print(f"Failed to retrieve data for {city}. Error code: {response.status_code}")

print(f"Weather data saved to {csv_file_path}")
