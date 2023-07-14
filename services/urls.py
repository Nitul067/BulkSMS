from django.urls import path
from . import views


urlpatterns = [
    path("", views.ao_dash, name='ao_dash'),
    path("create_customer/", views.create_customer, name="create_customer"),
    path("recharge/", views.add_recharge, name="add_recharge"),
    path("recharge/<int:id>/update/", views.update_recharge, name="update_recharge"),
    path("upload_trans/", views.upload_transactions, name="upload_trans"),
    path("add_trans/", views.add_transaction, name="add_trans"),
    path("rollback/<int:id>/<int:save>/", views.rollback, name="rollback"),
    path("customer_trans/<int:id>/", views.customer_trans, name="customer_trans"),
    path("customer_recharge/<int:id>/", views.customer_recharge, name="customer_recharge"),
    path("pnl/<int:id>/", views.pnl, name="pnl"),
    
    path("rollback/<int:id>/pdf/", views.generate_pdf, name="generate_pdf"),
    path("ajax/get_sms", views.ajax_sms_data, name="ajax_sms_data"),
]
