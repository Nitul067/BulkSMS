from django.urls import path
from . import views


urlpatterns = [
    path("", views.ao_dash, name='ao_dash'),
    path("create_customer/", views.create_customer, name="create_customer"),
    path("recharge/", views.add_recharge, name="add_recharge"),
    path("recharge/<int:id>/update/", views.update_recharge, name="update_recharge"),
    path("upload_trans/", views.upload_transactions, name="upload_trans"),
    path("add_trans/", views.add_transaction, name="add_trans"),
]
