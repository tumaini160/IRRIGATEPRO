from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from IRRIGATEPRO import views


urlpatterns = [
    path("", views.index, name="index"),
    # path('moisture/', views.receive_moisture_data, name='receive_moisture_data'),
    path('algorithm/', views.results, name='results'),
    path('historic_data/', views.historic_data, name='historic_data'),
    path('historic_data/weather_forecasting', views.weather_forecasting, name='weather_data'),
    path('result_data/1/', views.fetch_result_data1, name='fetch_result_data1'),
    path('result_data/2/', views.fetch_result_data2, name='fetch_result_data2'),
    path('charts/', views.graphs, name='graphs')
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)