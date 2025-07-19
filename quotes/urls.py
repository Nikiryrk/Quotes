from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('top-quotes/', views.top_quotes, name='top_quotes'),
    path('quotes/<int:quote_id>/rate/', views.rate_quote, name='rate_quote'),
    path('new-quote/',views.new_quote,name='new_quote')
]
