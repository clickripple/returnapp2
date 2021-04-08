from django.urls import path, re_path
from . import views                         # import views from views.py #
from .api import App_api                    # import Ap_api class from api.py #
from .webhook import WebhookApi as wb       # import WebhookApi class from webhook.py #
# from .sub_api import get_month_data
# from .sample import Count

urlpatterns = [
    # '''views.py'''                                            "Whitelisted urls" that must be mensioned in "public app" whilist url in "shopify". 
    path('', views.login, name='index'),                        # https://python.penveel.com/login
    path('installation', views.installation),
    path('final', views.final),                                 # https://python.penveel.com/final
    path('about', views.about),                                 # https://python.penveel.com/about
    path('privacy_policy', views.policy),                       # https://python.penveel.com/privacy_policy
    path('price', views.pricing),                               # https://python.penveel.com/price
    path('instruct', views.instruct),                           # https://python.penveel.com/instruct
    path('home', views.home_page),                              # https://python.penveel.com/home
    path('order', views.order_page),                            # https://python.penveel.com/order
    path('return_approved', views.returnapprove),               # https://python.penveel.com/return_approved
    path('return_reject', views.rejected),                      # https://python.penveel.com/return_reject
    path('settings', views.settings),                           # https://python.penveel.com/settings
    path('upload_data', views.data_upload),                     # https://python.penveel.com/upload_data
    path('install_page', views.install_page),                   # https://python.penveel.com/install_page

    # '''api.py'''
    path('oid', App_api.get_order_detail),                      # https://python.penveel.com/oid
    path('c_order', App_api.get_customer),                      # https://python.penveel.com/c_order

    # '''webhook.py'''
    path('uninstall', wb.webhook_uninstall),                    # https://python.penveel.com/uninstall
    path('Transactions', views.Transactions),                   # https://python.penveel.com/Transactions
]