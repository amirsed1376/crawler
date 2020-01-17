from django.urls import path , include
from . import views

urlpatterns = [
    # path("", views.crawler , name="crawler"),
    path("",views.crawler)
]
