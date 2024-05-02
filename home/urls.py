from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path('moisture/', views.receive_moisture_data, name='receive_moisture_data'),
    path('algorithm/', views.results, name='results'),
    path('historic_data/', views.historic_data, name='historic_data'),
    path('result_data/', views.fetch_result_data, name='fetch_result_data'),
    path('charts/', views.graphs, name='graphs')
]