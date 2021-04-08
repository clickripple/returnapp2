import shopify
import json
import requests
from .models import installer
from django.http import HttpResponse
from django.db.models import Q

API_KEY = "1c86866d8c638b28da99bbdfe3cd5fce"
SHARED_SECRET = "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"
API_VERSION = "2021-01"


class BillingAPI:
    @staticmethod
    def recurring_application_charges(shop_data, token):
        url = "https://%s/admin/api/%s/recurring_application_charges.json" % (shop_data, API_VERSION)

        header = {
            'X-Shopify-Access-Token': token,
            'Content-Type': 'application/json',
            'client_id': API_KEY,
            'client_secret': SHARED_SECRET
        }

        return_url = "https://%s/admin/apps/productreturn" % (shop_data)

        my = {
            "recurring_application_charge": 
            {
                "name": "Return Magic",
                "price": "0.0",
                "return_url": return_url,
                "capped_amount": "100",
                "terms": "0.4 USD after 20 entries",
                "test": "true"
            }
        }
        r = requests.post(url=url, headers=header, json=my)
        if r.status_code == 201:
            c = json.loads(r.text)
            return c
        else:
            c = ''
            return c
    
    @staticmethod
    def usage_charges(shop_data, token, ruc_id, price):
        url = "https://%s/admin/api/%s/recurring_application_charges/%s/usage_charges.json" % (shop_data, API_VERSION, ruc_id)

        header = {
            'X-Shopify-Access-Token': token,
            'Content-Type': 'application/json',
            'client_id': API_KEY,
            'client_secret': SHARED_SECRET
        }

        usage_my = {
            "usage_charge": {
                "description": "Return Magic the Order Return App",
                "price": price,
                "test": "true"
            }
        }

        r = requests.post(url=url, headers=header, json=usage_my)
        # print(r)
        # print(r.status_code)
        if r.status_code == 201:
            c = json.loads(r.text)
            return c
        else:
            c = ''
            return c
    
    @staticmethod
    def application_charges(shop_data, token):
        url = "https://%s/admin/api/%s/application_charges.json" % (shop_data, API_VERSION)
        # print(url)

        header = {
            'X-Shopify-Access-Token': token,
            'Content-Type': 'application/json',
            'client_id': API_KEY,
            'client_secret': SHARED_SECRET
        }

        my = {
            "application_credit": {
                "description": "Return Magic",
                "amount": "0.40",
                "test": "true"
            }
        }
        # print(my)
        r = requests.post(url=url, headers=header, json=my)
        # print(r)
        # print(r.status_code)
        if r.status_code == 201:
            c = json.loads(r.text)
            return c
        else:
            c = ''
            return c

    @staticmethod
    def get_usages_charges(shop_data, token, ruc_id):
        url = "https://%s/admin/api/%s/recurring_application_charges/%s/usage_charges.json" % (shop_data, API_VERSION, ruc_id)

        header = {
            'X-Shopify-Access-Token': token,
            'Content-Type': 'application/json',
            'client_id': API_KEY,
            'client_secret': SHARED_SECRET
        }

        r = requests.get(url=url, headers=header)
      
        if r.status_code == 200:
            c = json.loads(r.text)
            return c
        else:
            c = ''
            return c
    
    @staticmethod
    def Get_Shop_Data(shop_name, token):
        url = "https://%s/admin/api/%s/shop.json" % (shop_name, API_VERSION)

        header = {
            'X-Shopify-Access-Token': token,
            'Content-Type': 'application/json',
            'client_id': API_KEY,
            'client_secret': SHARED_SECRET
        }

        r = requests.get(url=url, headers=header)
      
        if r.status_code == 200:
            c = json.loads(r.text)
            data_dict = dict()
            data_dict['shop'] = {
                'id': c['shop']['id'],
                'email': c['shop']['email'],
                'domain': c['shop']['domain']
            }
            c = data_dict
            return c
        else:
            c = ''
            return c