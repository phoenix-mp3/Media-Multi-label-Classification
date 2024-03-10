from django.urls import path
from . import views

urlpatterns = [
    path('input-output/', views.input_output, name='input_output'),
    path('summarizer/', views.summarizer, name='summarizer'),
    path('web_scraper/', views.url_tagging, name='url_tagging'),
    path('image/', views.extract_text_view, name='extract_text_view'),
    path('url_summary/', views.URL_summarizer, name='URL_summarizer'),
    path('img_summary/', views.Image_summarizer, name='Image_summarizer'),
]
