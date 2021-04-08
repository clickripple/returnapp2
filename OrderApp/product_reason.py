import requests
import json

API_KEY = "1c86866d8c638b28da99bbdfe3cd5fce"
SHARED_SECRET = "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"
API_VERSION = "2021-01"

class product:
    # return_reason functional code start (get return_reason by product category) #
    @staticmethod
    def get_product_id(line_items, spname, Tooken, sh_id):
        my_dict = dict()
        all_reasons = dict()
        for c_id in line_items: # get line_items from get_order_detail in api.py #
            url = "https://" + spname + "/admin/api/%s/products/%s.json" %  (API_VERSION, c_id['product_id'])   # PRODUCT API to get product detail using product id #

            headers = {
                "X-Shopify-Access-Token": Tooken,
                "Content-Type": "application/json",
                "client_id": API_KEY,
                "client_secret": SHARED_SECRET
            }

            r = requests.get(url=url, headers=headers)
            if r.status_code == 200:        # check the status code is 200 then go ahead and return product category from json c #
                c = json.loads(r.text)
                my_dict[c_id['variant_id']] = c['product']['product_type']
            else:
                my_dict[c_id['variant_id']] = ''    
        all_reasons = product.product_check_ras(my_dict,shp_id=sh_id)   # product_check_ras fuction called here and return reasons for return product #
        return all_reasons # product type
    # return_reason functional code end #

    # return_reason API by ras.saara.io start #
    @staticmethod
    def product_check_ras(category, shp_id):
        data_reason_list = dict()
        for i, x_category in enumerate(category, start=0):
            url = "https://ras.saara.io/api/return-reasons?product_category=%s&seller_id=%s" %(category[x_category], shp_id)
            r = requests.get(url=url)
            if r.status_code == 200:    # check '200' status code to proccess further and return reason list of get data # 
                c = json.loads(r.text)
                data_reason_list[x_category] = c
            else:
                data_reason_list[x_category] = ''
        return data_reason_list
    # return_reason API by ras.saara.io end #