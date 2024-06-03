from django.shortcuts import redirect, render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Table1, Table2
import requests
import json
from firebase_admin import db


# Function to calculate ET0 using the Penman-Monteith equation
def calculate_et0(temp, humidity, wind_speed, solar_radiation):
    delta = 0.409  # Slope of saturation vapor pressure curve (kPa/°C)
    gamma = 0.066  # Psychrometric constant (kPa/°C)

    es = 0.611 * (2.7183 ** ((17.3 * temp) / (237.3 + temp)))  # Saturation vapor pressure (kPa)
    ea = (humidity / 100) * es  # Actual vapor pressure (kPa)
    delta_e = es - ea

    ET0 = (0.408 * delta * solar_radiation + gamma * (900 / (temp + 273)) * wind_speed * delta_e) / (delta + gamma * (1 + 0.34 * wind_speed))
    return ET0  


def get_latest_soil_moisture():
    ref = db.reference('/soilMoisture')
    snapshot = ref.order_by_key().limit_to_last(1).get()
    for key, value in snapshot.items():
        return value.get('value')


def index(request):
    return render(request, 'home/index.html')


def results(request):
    if request.method == 'POST':
        try:
            city = request.POST['city']
            year_type = request.POST['yr']
            field_area = request.POST['Ai']
            crop_coefficient = request.POST['KC']
            crop_type = request.POST['crop']
            api_key = "e1945ce89b7b434b92b10f8ec8625f97"
            
            url1 = f"https://api.opencagedata.com/geocode/v1/json?q={city}&key={api_key}"
            response1 = requests.get(url1)
            data1 = response1.json()
            
            lat = data1['results'][0]['geometry']['lat']
            lon = data1['results'][0]['geometry']['lng']
            
            Api_key = '0ZK2c3TkJHFmt2TA6ZbRQ4HPSOx4itPo'
            url = f'https://api.tomorrow.io/v4/weather/forecast?location={lat},{lon}&apikey={Api_key}'
            headers = {"accept": "application/json"}
            response = requests.get(url, headers=headers)
            data = response.json()
            rain_prob = data['timelines']['daily'][0]['values']['precipitationProbabilityAvg']
            tmean = data['timelines']['daily'][0]['values']['temperatureAvg']
            rain_intensity = data['timelines']['daily'][0]['values']['rainIntensityAvg']
            threshold_rain_prob = 50
            sensor_data = get_latest_soil_moisture()
            smin = 50
            gw = 0.00112486  # Groundwater Contribution (mm/day)
            sw = 0.002812148571  # Soil Water Depleted (mm/day)
            ie = 80  # Irrigation efficiency
            h = 0.045  # Root depth (m)
            f = 50  # Water availability in the soil
            q = 40.5  # Flow rate (mm3/s)
            dnet = 2.76 #in (mm)

            if 'timelines' in data and 'daily' in data['timelines'] and 'values' in data['timelines']['daily'][0]:
                current_data = data['timelines']['daily'][0]['values']
                if 'temperatureAvg' in current_data and 'humidityAvg' in current_data and 'windSpeedAvg' in current_data and 'uvIndexAvg' in current_data:
                    temperature = current_data['temperatureAvg']
                    humidity = current_data['humidityAvg']
                    wind_speed = current_data['windSpeedAvg']
                    uv_index = current_data['uvIndexAvg']
                    k = 17.5
                    solar_rad = k * uv_index
                    prep = rain_intensity * 1

                    reference_et0 = calculate_et0(temperature, humidity, wind_speed, solar_rad)
                    etc = int(float(crop_coefficient)) * reference_et0
                    print(etc)
                    ifr = int(dnet / etc)

                    if prep > 250:
                        ep = 125 + (0.1 * prep)
                    else:
                        ep = prep * (125 - (0.2 * prep)) / 125

                    if rain_prob < threshold_rain_prob:
                        if sensor_data >= smin:
                            irn = etc - ep - gw - sw
                            ir = irn / ie
                        else:
                            ir = 0
                    else:
                        ir = 0

                    if ir > 0:
                        dw = h * 122.50 * f / ie
                        id = 2.78 * dw * int(field_area) / q
                        irr_data = Table1(
                            CropType=crop_type,
                            SoilMoistureValue=sensor_data,
                            ET0=reference_et0,
                            ETc=etc,
                            IRn=irn,
                            IR=ir,
                            Dw=dw,
                            IDG=id,
                            Wf=ifr,
                            city=city
                        )
                        irr_data.save()
                        return redirect('fetch_result_data1')
                    else:
                        return render(request, 'home/noirrigation.html')
                else:
                    return handle_missing_weather_data(year_type, tmean, crop_coefficient, dnet, rain_intensity, rain_prob, threshold_rain_prob, sensor_data, smin, gw, sw, ie, h, f, q, field_area, crop_type, city)
        except Exception as e:
            print(f"Error: {e}")
            return render(request, 'home/error.html', {'error': str(e)})


def handle_missing_weather_data(request, year_type, tmean, crop_coefficient, dnet, rain_intensity, rain_prob, threshold_rain_prob, sensor_data, smin, gw, sw, ie, h, f, q, field_area, crop_type, city):
    if year_type == 'leap year':
        ahpd = (12.5 + 11.8) / 2
        tdhi_y = ahpd * 366
        thiy = 24 * 366
        pdth = (tdhi_y / thiy) * 100
        et0 = pdth * ((0.46 * tmean) + 8.13)
    else:  # Normal year
        ahpd = (12.5 + 11.8) / 2
        tdhi_y = ahpd * 365
        thiy = 24 * 365
        pdth = (tdhi_y / thiy) * 100
        et0 = pdth * ((0.46 * tmean) + 8.13)

    etc = int(float(crop_coefficient)) * et0
    ifr = int(dnet / etc)
    prep = rain_intensity * 1

    if prep > 250:
        ep = 125 + (0.1 * prep)
    else:
        ep = prep * (125 - (0.2 * prep)) / 125

    if rain_prob < threshold_rain_prob:
        if sensor_data <= smin:
            irn = etc - ep - gw - sw
            ir = irn / ie
        else:
            ir = 0
    else:
        ir = 0

    if ir > 0:
        dw = h * 122.5 * f / ie
        id = 2.78 * dw * int(field_area) / q
        irr_data = Table2(
            CropType=crop_type,
            SoilMoistureValue=sensor_data,
            ET0=et0,
            ETc=etc,
            IRn=irn,
            IR=ir,
            Dw=dw,
            IDG=id,
            Wf=ifr,
            city=city
        )
        irr_data.save()
        return redirect('fetch_result_data2')
    else:
        return render(request, 'home/noirrigation.html')


def weather_forecasting(request):
    if request.method == 'POST':
        try:
            city = request.POST['city']
            api_key = "0ZK2c3TkJHFmt2TA6ZbRQ4HPSOx4itPo"
            url = f"https://api.tomorrow.io/v4/weather/forecast?location={city}&timesteps=1d&apikey={api_key}"
            headers = {"accept": "application/json"}
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                data = response.json()
                weather = data['timelines']['daily']
                weather_forecast = [{
                    "time": daily["time"],
                    "temperature": daily["values"].get("temperatureAvg", 0),
                    "humidity": daily["values"].get("humidityAvg", 0),
                    "wind_speed": daily["values"].get("windSpeedAvg", 0),
                    "prep_prob": daily["values"].get("precipitationProbabilityAvg", 0),
                    "rain_intensity": daily["values"].get("rainIntensityAvg", 0),
                    "uvIndex": daily["values"].get("uvIndexAvg", 0),
                    "sunrise": daily["values"].get("sunriseTime", ""),
                    "sunset": daily["values"].get("sunsetTime", "")
                } for daily in weather]
                return render(request, 'home/weather.html', {'weather': weather_forecast})
            else:
                return render(request, 'home/error.html', {'error': 'Failed to fetch weather data'})

        except Exception as e:
            print(f"Error: {e}")
            return render(request, 'home/error.html', {'error': str(e)})
    else:
        return render(request, 'home/error.html', {'error': 'Invalid request method'})


def historic_data(request):
    results_data1 = Table1.objects.all()
    results_data2 = Table2.objects.all()
    return render(request, 'home/data.html', {'result_data1': results_data1, 'result_data2': results_data2})


def fetch_result_data1(request):
    result_data = Table1.objects.order_by('-Date').first()
    return render(request, 'home/results.html', {'result_data': result_data})


def fetch_result_data2(request):
    result_data = Table2.objects.order_by('-Date').first()
    return render(request, 'home/results.html', {'result_data': result_data})


def graphs(request):
    ref = db.reference('/soilMoisture')
    snapshot = ref.order_by_child('timestamp').get()

    timestamps = []
    moisture_values = []

    for key, value in snapshot.items():
        timestamps.append(value['timestamp'])
        moisture_values.append(value['value'])

    results_data1 = Table1.objects.all()
    results_data2 = Table2.objects.all()

    labels = [entry.Date.strftime('%Y-%m-%d') for entry in results_data1]
    data = [float(entry.ET0) for entry in results_data1]
    labels2 = [entry.Date.strftime('%Y-%m-%d') for entry in results_data2]
    data2 = [float(entry.ETc) for entry in results_data2]

    return render(request, 'home/charts.html', {
        'timestamps': json.dumps(timestamps),
        'moisture_values': json.dumps(moisture_values),
        'labels': labels,
        'data': data,
        'labels2': labels2,
        'data2': data2,
    })
