from django.urls import path
from . import views


urlpatterns = [
    path("", views.ao_dash, name='ao_dash'),
    path("recharge/", views.add_recharge, name="add_recharge"),
    path("update_recharge/", views.update_recharge, name="update_recharge"),
    path("upload_trans/", views.upload_transactions, name="upload_trans"),
]
