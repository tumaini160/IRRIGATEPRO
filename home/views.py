from django.shortcuts import redirect, render
from django.http import HttpResponse
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import SensorData, Results
import json
from django.utils import timezone


# function to calculate ET0  using Penman-Monteith equation

def calculate_et0(temp, humidity, wind_speed, solar_radiation):
    # Constants
    delta = 0.409  # Slope of saturation vapor pressure curve (kPa/°C)
    gamma = 0.066  # Psychrometric constant (kPa/°C)

    # Calculate vapor pressure deficit (delta_e)
    es = 0.6108 * (10 ** ((7.5 * temp) / (237.3 + temp)))  # Saturation vapor pressure (kPa)
    ea = (humidity / 100) * es  # Actual vapor pressure (kPa)
    delta_e = es - ea

    # Calculate net radiation (Rn) and soil heat flux (G) if available
    # (You'll need additional data or estimates for these)

    # ET0   = (0.408 * delta * (solar_radiation - G) + gamma * 900 * wind_speed * delta_e) / (delta +    gamma * (1 + 0.34 * wind_speed))


    # Calculate reference evapotranspiration (ET0)
    ET0   = (0.408 * delta * (solar_radiation) + gamma * 900 * wind_speed * delta_e) / (delta +    gamma * (1 + 0.34 * wind_speed))

    return ET0  



def index(request):
    return render(request, 'home/index.html')
    
def results(request):
    if request.method == 'POST':
        city = request.POST['city']
        year_type = request.POST['yr']
        field_area = request.POST['Ai']
        crop_coefficient = request.POST['KC']
        
        api_key = '0ZK2c3TkJHFmt2TA6ZbRQ4HPSOx4itPo'
        url = f'https://api.tomorrow.io/v4/weather/forecast?location={city}&apikey={api_key}' #url used to fetch weather data from api
        headers={"accept":"application/json"}
        response = requests.get(url, headers=headers) # a request to fetch weather data from api using api url
        data = response.json() # weather data fetched
        rain_prob = data['timelines']['daily'][0]['values']['precipitationProbabilityAvg']
        Tmean = data['timelines']['daily'][0]['values']['temperatureAvg']
        rain_intensity = data['timelines']['daily'][0]['values']['rainIntensityAvg']
        Threshold_rain_prob = 50
        Sensor_data = 59.9
        Smin = 61.25
        GW = 0.00112486 #Groundwater Contribution, this users will input using ui (mm/day)
        SW = 0.002812148571 #Soil Water Depleted, this users will input using ui (mm/day)
        Ie = 50 #irrigation efficiency
        H = 15.24 #root depth(cm), this users will input using ui
        f = 50 #water availability in the soil, this users will input using ui
        Q = 40.5 #flow rate (mm3/s)

 
        # Check if temperature, humidity, wind speed, and UV index are available
        if 'timelines' in data and 'daily' in data['timelines'] and 'values' in data['timelines']['daily'][0]:
            current_data = data['timelines']['daily'][0]['values']
            if 'temperatureAvg' in current_data and 'humidityAvg' in current_data and 'windSpeedAvg' in current_data and 'uvIndexAvg' in current_data:
                # All required values are available
                temperature = current_data['temperatureAvg']
                humidity = current_data['humidityAvg']
                wind_speed = current_data['windSpeedAvg']
                uv_index = current_data['uvIndexAvg']
                k= 17.5
                solar_rad = k * uv_index
                    
                prep= rain_intensity*1 #precipitation in 1min of forecasting

                reference_ET0   = calculate_et0(temperature,humidity, wind_speed,   solar_rad) #call for function used to calculate ET0 using penman-monteith method

                ETc = int(crop_coefficient) * reference_ET0 


                if prep > 250:
                    EP = 125 + (0.1*prep)
                elif prep<=250:
                    EP= prep * ( 125 - (0.2*prep) )/125

                if rain_prob < Threshold_rain_prob:  
                    if Sensor_data <= Smin:
                        IRn = ETc - EP - GW - SW
                        IR = IRn/Ie
                    else:
                        IR = 0
                else:
                    IR = 0
                    
                if IR > 0: 
                    Dw = (H*(122.50)*f)/Ie
                    ID = (2.78 * Dw * int(field_area))/Q
                    
                    irr_data = Results(
                        ET0 = reference_ET0,
                        ETc = ETc,
                        IRn = IRn,
                        IR = IR,
                        Dw = Dw,
                        IDG = ID,
                        Wf = 1,
                        city = city
                        ) 
                    
                    irr_data.save()

                    return redirect('fetch_result_data')
                else:
                    return render(request, 'home/error.html')
            else:
                if year_type == 'leap year':
                    AHPD= (12.5 + 11.8)/2
                    TDHIY = AHPD *366
                    THIY = 24 * 366
                    PDTH=(TDHIY/THIY)*100

                    ET0=PDTH * ((0.46 * Tmean)+8.13)

                    ETc = int(crop_coefficient) * ET0

                    prep= rain_intensity * 1 #precipitation in 1min of forecasting

                    if prep > 250:
                        EP = 125 + (0.1 * prep)
                    elif prep<=250:
                        EP= prep * ( 125 - (0.2 * prep) )/125

                    if rain_prob > Threshold_rain_prob:  
                        if Sensor_data <= Smin:
                            IRn = ETc - EP - GW - SW
                            IR = IRn/Ie
                        else:
                            IR = 0
                    else:
                        IR = 0
                

                    if IR > 0: 
                        Dw = (H*(122.50)*f)/Ie
                        ID = (2.78 * Dw * int(field_area))/Q

                        irr_data = Results(
                            ET0 = reference_ET0,
                            ETc = ETc,
                            IRn = IRn,
                            IR = IR,
                            Dw = Dw,
                            IDG = ID,
                            Wf = 1,
                            city = city
                            ) 
                        
                        irr_data.save()

                        return redirect('fetch_result_data')
                    
                    else:
                        return render(request, 'home/error.html')
                elif year_type == "normal year":
                    AHPD= (12.5 + 11.8)/2
                    TDHIY = AHPD*365
                    THIY=24*365
                    PDTH=(TDHIY/THIY)*100

                    ET0=PDTH*((0.46*Tmean)+8.13)

                    ETc = int(crop_coefficient) * ET0

                    prep= rain_intensity*1 #precipitation in 1min of forecasting

                    if prep > 250:
                        EP = 125 + (0.1*prep)
                    elif prep<=250:
                        EP= prep * ( 125 - (0.2*prep) )/125

                    if rain_prob < Threshold_rain_prob:  
                        if Sensor_data <= Smin:
                            IRn = ETc - EP - GW - SW
                            IR = IRn/Ie
                        else:
                            IR = 0
                    else:
                        IR = 0
                

                    if IR > 0: 
                        Dw = (H*(122.5)*f)/Ie
                        ID = (2.78 * Dw * int(field_area))/Q
                        irr_data = Results(
                            ET0 = reference_ET0,
                            ETc = ETc,
                            IRn = IRn,
                            IR = IR,
                            Dw = Dw,
                            IDG = ID,
                            Wf = 1,
                            city = city
                            ) 
                        
                        irr_data.save()

                        return redirect('fetch_result_data')
                    else:
                        return render(request, 'home/error.html')
   
@csrf_exempt
def receive_moisture_data(request):
    if request.method == 'GET':
        soil_moisture = request.POST.get('soil_moisture', None)
        if soil_moisture is not None:
        # Do something with the received soil moisture data
            print("Received soil moisture:", soil_moisture)
            return HttpResponse("Data received successfully")
        # data = json.loads(request.body)
        # moisture_percentage = data.get('moisture_percentage')
        # if moisture_percentage is not None:
        #     SensorData.objects.create(SoilMoistureValue = moisture_percentage)
        #     return JsonResponse({'message': 'Data received successfully'}, status=200)
    return JsonResponse({'error': 'Invalid request'}, status=400)
        
def historic_data(request):
    api_key = "0ZK2c3TkJHFmt2TA6ZbRQ4HPSOx4itPo"  # Replace with your Tomorrow.io API key
    city = "Dar es salaam"
    url = f"https://api.tomorrow.io/v4/weather/forecast?location={city}&timesteps=1d&apikey={api_key}"
    headers = {"accept": "application/json"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        weather= data['timelines']['daily']
        weather_forecast = [{
            "time": daily["time"],
            "temperature": daily["values"]["temperatureAvg"],
            "humidity": daily["values"]["humidityAvg"],
            "wind_speed": daily["values"]["windSpeedAvg"],
            "prep_prob": daily["values"]["precipitationProbabilityAvg"],
            "rain_intensity": daily["values"]["rainIntensityAvg"],
            "uvIndex": daily["values"]["uvIndexAvg"],
            "sunrise": daily["values"]["sunriseTime"],
            "sunset": daily["values"]["sunsetTime"]
            }
             for daily in weather]
        soil_moisture_data = SensorData.objects.all()
        results_data = Results.objects.all()
        return render(request, 'home/data.html', {'weather_forecast': weather_forecast, 'soil_moisture_data': soil_moisture_data, 'result_data':results_data})
    else:
        return render(request, 'home/error.html')
    
def fetch_result_data(request):
    # Fetch the most recently posted data (latest first)
    result_data = Results.objects.order_by('-Date').first()
    return render(request, 'home/results.html', {'result_data': result_data})
    
def graphs(request): # Fetch data from the SalesData model
    results_data = Results.objects.all()
    
    # Extract labels and data from the queryset
    labels = [entry.Date.strftime('%Y-%m-%d') for entry in results_data]
    data = [float(entry.ET0) for entry in results_data]
    
    labels2 = [entry.Date.strftime('%Y-%m-%d') for entry in results_data]
    data2 = [float(entry.ETc) for entry in results_data]
    
    return render(request, 'home/charts.html', {'labels': labels, 'data': data, 'labels2': labels, 'data2': data})