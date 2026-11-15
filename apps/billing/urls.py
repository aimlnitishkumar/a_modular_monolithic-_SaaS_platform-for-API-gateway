from django.urls import path

from .views import InvoiceGenerateAPIView, InvoiceListAPIView

urlpatterns = [
    path("invoices/", InvoiceListAPIView.as_view(), name="invoice-list"),
    path("invoices/generate/", InvoiceGenerateAPIView.as_view(), name="invoice-generate"),
]
