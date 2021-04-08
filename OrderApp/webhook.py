import requests
import json
import hashlib
import base64
from .models import installer, uninstall_data, detail_order, requested_variant, thank_you
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
import hmac
import datetime
import os


API_KEY = "1c86866d8c638b28da99bbdfe3cd5fce"
SHARED_SECRET = "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"
API_VERSION = "2021-01"

# encrypt data functional start (uninstall app then save the uninstall time data in encrypted format)  #
def encrypt(data_json):
    data2 = json.dumps(data_json)
    sample_string_bytes = data2.encode("ascii") 
    base64_bytes = base64.b64encode(sample_string_bytes)
    return base64_bytes.decode('utf-8')
# encrypt data functional end #


def ras_uninstall_webhook(ras_shop, ras_json_data, ras_date):
    url = "https://ras.saara.io/api/shopify-uninstall-webhook?shop=%s&data=%s&date=%s" % (ras_shop, ras_json_data, ras_date)

    r_data = requests.get(url=url)

    if r_data.status_code == 200:
        c = json.loads(r_data.text)
        return HttpResponse(json.dumps(c), content_type="application/json")
    else:
        return HttpResponse('no data gether')
    return HttpResponse('hello')


class WebhookApi(object):
    # shopify Uninstalling app webhook  functional code start #
    @csrf_exempt
    def webhook_uninstall(request):
        if request.method == 'POST':        # check that the request method is POST or not #
            if ((request.body != "") and (request.headers.get('X-Shopify-Hmac-Sha256') != "")):     # check 'request.body' and  'request.headers.get('X-Shopify-Hmac-Sha256')' is not blank #
                data = request.body
                tkn = ''
                shop_url = ''
                hmac_header = request.headers.get('X-Shopify-Hmac-Sha256')
                digest = hmac.new(SHARED_SECRET.encode('utf-8'), data, hashlib.sha256).digest() # create new hmac from gethered data (data, hashlib.sha256 and shared_secret) #
                computed_hmac = base64.b64encode(digest)    # encoded hmac that create above #

                if computed_hmac == hmac_header.encode('utf-8'):    # match hmac_header and computed_hmac then get the topic and shop_url #
                    topic = request.headers.get('X-Shopify-Topic')
                    shop_url = request.headers.get('X-Shopify-Shop-Domain')
                    if shop_url != "":      # check the 'shop_url' is not blank #
                        uninstallap = installer.objects.filter(shop=str(shop_url))  # 'installer' table data filter by 'shop_url' #
                        if uninstallap: # get the record then #
                            tkn = uninstallap[0].access_token
                            encrypt_data = encrypt(data_json=data.decode('utf-8'))      # encrypt the data that gether while UninstallApp #
                            date = datetime.datetime.now()
                            
                            # call ras uninstall function start #
                            ras_data = ras_uninstall_webhook(ras_shop=shop_url, ras_json_data=data.decode('utf-8'), ras_date=date)
                            # end ras uninstall function #

                            # start call 'uninstall_data' table and store the data to it #
                            data = uninstall_data()     
                            data.uninstall_shop = uninstallap[0].shop
                            data.uninstall_time = date
                            data.uninstall_log = encrypt_data
                            data.save()
                            # end save data in uninstall_data #
                            uninstallap.delete()            # delete record from 'installer' table while 'shop_url' is match in data #

                            variant_tabel = requested_variant.objects.filter(varaint_shop=str(shop_url))    # filter 'requested_variant' table data by 'shop_url' #
                            if variant_tabel:   # fetch record from 'requested_variant' table #
                                variant_tabel.delete()  # delete that records from 'requested_variant' table #
                            else:
                                return HttpResponse("NO data found")

                            ordersallap = detail_order.objects.filter(shop_data=str(shop_url))      # filter 'detail_order' table data by 'shop_url' #
                            if ordersallap: # fetch record from 'detail_order' table #
                                ordersallap.delete()     # delete that records from 'detail_order' table #
                            else:
                                return HttpResponse("NO data found")

                            thanks_detail = thank_you.objects.filter(shop_name=str(shop_url))       # filter 'thank_you' table data by 'shop_url' #
                            if thanks_detail:       # fetch record from 'thank_you' table #
                                thanks_detail.delete()      # delete that records from 'thank_you' table #
                            else:
                                return HttpResponse("NO data found")    
                    else:
                        return HttpResponse("NO shop domain")
                else:
                    return HttpResponse("FALSE")
        return HttpResponse('Success')
        # shopify Uninstalling app webhook  functional code end #
    