from django.urls import path
from django.contrib import admin
from infojobs import views
from rest_framework.documentation import include_docs_urls

urlpatterns = [
    path("get_offer_list/", views.InfojobsViewSet.as_view({"post": "get_offer_list"})),
    path("get_offer_detail/", views.InfojobsViewSet.as_view({"post": "get_offer_detail"})),
    path("extract_content/", views.InfojobsViewSet.as_view({"post": "extract_content"})),
]
