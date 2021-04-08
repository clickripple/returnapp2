import shopify
import json
import requests
import datetime
from .models import installer, detail_order, Relations_Plan_Shop, plan as p, Counter_Shop_Detail, plan_charges
from django.db.models import Q
from django.utils.html import strip_tags
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from .product_reason import product

# import BillingAPI #
from .billingapi import BillingAPI
# from .email import EmailNotifier
# END BillngAPI #

# count by month #
from django.db.models.functions import TruncMonth
from django.db.models import Count
# end count #

API_KEY = "1c86866d8c638b28da99bbdfe3cd5fce"
SHARED_SECRET = "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"
API_VERSION = "2021-01"
# fixed_count = settings.fix_counter

class App_api:
    # return functional code start (process return request from shopify page(return) )# detail_order
    @staticmethod
    def get_order_detail(request):               # if count == 20 #
        my_dict = dict()
        token = ''
        plan_date = ''
        shop_detail = strip_tags(request.GET.get('shop'))
        cus_email = strip_tags(request.GET.get('email'))
        cus_id = strip_tags(request.GET.get('customer'))
        ord_id = strip_tags(request.GET.get('order'))
        get_data = dict()
        
        # Order match functional code start (We have used for checking requested data from ajax call)
        if (shop_detail is not None and shop_detail!='') and (cus_email is not None and cus_email!='') and (cus_id is not None and cus_id!='') and (ord_id is not None and ord_id!=''):
            shop_domain = shop_detail + ".myshopify.com" 
            
            get_rec = installer.objects.filter(shop=shop_domain)        # filter the data from 'installer' table by shop domain #

            if get_rec:         # if shop data is match then get token and id from 'installer' table #
                token = get_rec[0].access_token
                sid = get_rec[0].id
            else:   
                message = "Invalid Store Data"
                my_dict['error_message'] = message
                return HttpResponse(json.dumps(my_dict), content_type="application/json") 

            check_plan = Relations_Plan_Shop.objects.get(shop_id_id=int(sid))
            if check_plan:
                plan_date = check_plan.entry_date
                plan_id = check_plan.plan_id_id
            else:
                message = "Invalid Store Data"
                my_dict['error_message'] = message
                return HttpResponse(json.dumps(my_dict), content_type="application/json")

            shop_plan = p.objects.get(id=int(plan_id)).plan_name
            if shop_plan == "Freemium":
                
                installation_data = installer.objects.get(shop=shop_domain)
                if installation_data:
                    insta_date = installation_data.install_date
                    shop_id = installation_data.id
                    checked_counter = Counter_Shop_Detail.objects.filter(store_id=shop_id)
                    if checked_counter:
                        pass
                    else:
                        db_count = 0
                        Counter_Shop_Detail.objects.create(store_id_id=int(shop_id), counter=db_count, reset_date=insta_date)
                else:
                    message = "No Store Data Found"
                    my_dict['error_message'] = message
                    return HttpResponse(json.dumps(my_dict), content_type="application/json")

                counter = Counter_Shop_Detail.objects.get(store_id=sid).counter            # request count #
                if counter < 3:
                    print(counter)                     # requested count <= fixed/free count #
                    print('freemium if')
                    db_count = 0
                    

                    installation_data = installer.objects.get(shop=shop_domain)
                    if installation_data:
                        insta_date = installation_data.install_date
                        shop_id = installation_data.id

                    # Enable Above # 
                        # Order API code start (API by Customer_id)  #
                        ur = "https://%s/admin/orders.json?customer_id=%s&financial_status=paid,partially_refunded,refunded&status=any" % (shop_domain, cus_id)
                    
                        headers = {
                            "X-Shopify-Access-Token": token,
                            "Content-Type": "application/json",
                            "client_id": API_KEY,
                            "client_secret": SHARED_SECRET
                        }
                        r = requests.get(url=ur, headers=headers)
                        c_data = json.loads(r.text)
                        data_vari_dict = dict()
                        # Order API code end (return json format data in c_data) #
                    
                        if c_data != "":        # check that above json is not none or blank #
                            for x in c_data["orders"]:
                                if x['financial_status'] == "refunded": # check that the order is refunded or not #
                                    message = "Order fully refunded"
                                    my_dict['error_message'] = message
                                    return HttpResponse(json.dumps(my_dict), content_type="application/json")
                                else:
                                    global data_dict_data
                                    data = x
                                    data_dict_data = data

                                    if data['email'] == cus_email and str(data['order_number']) == str(ord_id): # match the requested email and order number in order API json #
                                        or_id = data["id"]
                                        count = 0
                                        # from .models import detail_order
                                        data_detail_variant = detail_order.objects.filter(Q(shop_data=shop_domain), Q(ordid=str(or_id)), Q(order_id=str(ord_id)), Q(custom_id=str(cus_id)))
                                        # above line filter data from 'detail_order' table #
                                        if data_detail_variant:     # match data in 'detail_order' get variant and quantity data #

                                            # start code for get variant and quantity data and append the data in  the list #
                                            data_vari_dict['line_items'] = list()
                                            for data_detail in data_detail_variant:
                                                vda_variants = data_detail.variants
                                                vda_quant = data_detail.quantity
                                                

                                                if ',' in vda_variants:
                                                    count = 0
                                                    vdata_vari = vda_variants.split(',')
                        
                                                else:
                                                    count = 999
                                                    vdata_vari = vda_variants
                                                

                                                if ',' in vda_quant:
                                                    count = 0
                                                    vdata_quant = vda_quant.split(',')
                                                
                                                else:
                                                    count = 999
                                                    vdata_quant = vda_quant


                                                if count == 999: 
                                                    data = dict()
                                                    data_y = vdata_quant
                                                    data_x = vdata_vari
                                                    
                                                    update = "false"
                                                    if len(data_vari_dict['line_items']) != 0:
                                                        for d in data_vari_dict['line_items']:
                                                            if str(d['variants']) == str(data_x):
                                                                d['quant'] = int(data_y) + int(d['quant'])
                                                                update = "true"
                                                                break
                                                    if update == "false":
                                                        da = {
                                                            "variants":data_x,
                                                            "quant":data_y
                                                        }
                                                        data_vari_dict['line_items'].append(da)

                                                else:
                                                    if len(vdata_vari) == len(vdata_quant):
                                                        for x in range(len(vdata_vari)):
                                                            data = dict()
                                                            data_y = vdata_quant[x]
                                                            data_x = vdata_vari[x]

                                                            update = "false"
                                                            if len(data_vari_dict['line_items']) != 0:
                                                                for d in data_vari_dict['line_items']:
                                                                    
                                                                    if str(d['variants']) == str(data_x):
                                                                    
                                                                        d['quant'] = int(data_y) + int(d['quant'])
                                                                        
                                                                        update = "true"
                                                                        break
                                                            if update == "false":
                                                                da = {
                                                                    "variants":data_x,
                                                                    "quant":data_y
                                                                }
                                                                data_vari_dict['line_items'].append(da) 
                                            # end code for get variant and quantity data and append the data in  the list #


                                            if len(data_vari_dict['line_items']) > 0 and len(data_dict_data['line_items']) > 0: # check the length of json line_items and created line_items list #
                                                for l, data_line in enumerate(data_dict_data['line_items'], start=0):
                                                    for data_database in data_vari_dict['line_items']:
                                                    
                                                        if int(data_line['variant_id']) == int(data_database['variants']):  # match variant from json line_items and create line_items #
                                                            if int(data_line['quantity']) == int(data_database['quant']):   # match quantity from json line_items and create line_items #
                                                                
                                                                data_dict_data['line_items'][l] = ''
                                                                break
                                                            elif int(data_line['quantity']) > int(data_database['quant']):    # check that the quantity in json is greater than requested quantity then it's deduct requested quantity from json #
                                                                data_line['quantity'] = int(data_line['quantity']) - int(data_database['quant'])
                                                                break
                                                
                                            data_dict_data['line_items'] = list(filter(None, data_dict_data['line_items']))
                                            
                                        
                                        if (request.GET.get('variants') is not None) and (request.GET.get('quantity') is not None): # check the requested variant and quantity is not none or blank #
                                            db_count += 1
                                            # print(shop_id, insta_date)
                                            counter_data_checker = Counter_Shop_Detail.objects.filter(store_id=shop_id)
                                            # print(counter)
                                            if counter_data_checker:
                                                print('counter_data_checker if')
                                                get_counter_data = counter_data_checker[0].counter
                                                get_counter_data += db_count
                                                # Email sender here start #
                                                if get_counter_data == 3:
                                                    Shop_api_data = BillingAPI.Get_Shop_Data(shop_name=shop_domain, token=token)
                                                    if len(Shop_api_data) > 0:
                                                        if Shop_api_data['shop']['domain'] == shop_domain:
                                                            store_email = Shop_api_data['shop']['email']
                                                            from django.core.mail import EmailMultiAlternatives
                                                            from django.template.loader import render_to_string
                                                            from django.conf import settings
                                                            subject, from_email, to = 'Important Notice From Return Magic', settings.EMAIL_HOST_USER, store_email
                                                            text_content = 'This is an important message.'
                                                            print(shop_domain, "EMail")
                                                            plan_url = "https://"+ shop_domain +"/admin/apps/6devhome/price"
                                                            print(plan_url, "EMail")
                                                            # from .email import html   html(plan_link=plan_url)
                                                            
                                                            html_content = render_to_string("email.html", {'url': plan_url})
                                                            msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
                                                            msg.attach_alternative(html_content, "text/html")
                                                            msg.send()
                                                            pass
                                                        else:
                                                            message = "Store is not matched"
                                                            my_dict['error_message'] = message
                                                            return HttpResponse(json.dumps(my_dict), content_type="application/json")    
                                                else:
                                                    pass                                                
                                                # Email sender End #
                                                Counter_Shop_Detail.objects.filter(store_id=shop_id).update(counter=get_counter_data)
                                            else:
                                                print('counter_data_checker else')
                                                # print(shop_id)
                                                Counter_Shop_Detail.objects.create(store_id_id=int(shop_id), counter=db_count, reset_date=insta_date)
                                            
                                            total = 0
                                            quant = 0
                                            ful_stat = ''
                                            if (',' in request.GET.get('variants')) and (',' in request.GET.get('quantity')) and ('||' in request.GET.get('notes')):    # check that ',' in variant and quantity and '||' in notes  then separate it #
                                                count = 0
                                                variants = request.GET.get('variants').split(',')
                                                quantity = request.GET.get('quantity').split(',')
                                                reas_note = request.GET.get('notes').split('||')
                                            
                                                if len(data_dict_data) != 0:  # check the length of data_dict_data #
                                                    
                                                    for dk, dvdata in enumerate(data_dict_data['line_items'], start=0): 
                                                        for j, jdata in enumerate(variants, start=0):
                                                            dvvari = variants[j]
                                                            if str(dvvari) == str(dvdata['variant_id']):    # match json variant by requested variant #
                                                            
                                                                if int(dvdata['quantity']) < int(quantity[j]):  # check json quantity by requested quantity (requested quantity is max the show an error) #
                                                                    message = "wrong quantity error"
                                                                    my_dict['error_message'] = message
                                                                    return HttpResponse(json.dumps(my_dict), content_type="application/json")
                                                
                                                for xdata in data_dict_data['line_items']:  
                                                    for i in range(len(variants)): 
                                                        xvari = variants[i]
                                                        if str(xvari) == str(xdata['variant_id']):      # match json variant by requested variant #
                                                            if int(xdata['quantity']) >= int(quantity[i]):  # check the json variant quantity is greater than or equal to the requested quantity #
                                                                if xdata['fulfillment_status'] == "fulfilled":  # match json fulfillment_status is fulfilled or not #
                                                                    quant = int(quantity[i]) + int(quant)

                                                                    lintotal = float(float(xdata["price"]) * float(quantity[i]))
                                                                    total = lintotal + total                                                        
                                                                    ful_stat = xdata['fulfillment_status']
                                                            else:
                                                                message = "wrong quantity error"
                                                                my_dict['error_message'] = message
                                                                return HttpResponse(json.dumps(my_dict), content_type="application/json")
                                            else:
                                                count = 999
                                                variants = request.GET.get('variants')
                                                quantity = request.GET.get('quantity')
                                                reas_note = request.GET.get('notes')
                                            
                                                if len(data_vari_dict) != 0:
                                                    for dvdata in data_vari_dict['line_items']: 
                                                        dvvari = variants
                                                        if str(dvvari) == str(dvdata['variants']):      # match variant of data_vari_dict to requested variant if requested variant is single data #
                                                            if int(dvdata['quant']) < int(quantity):
                                                                message = "wrong quantity error"
                                                                my_dict['error_message'] = message
                                                                return HttpResponse(json.dumps(my_dict), content_type="application/json")

                                                
                                                for xdata in data_dict_data['line_items']:                                       
                                                    if str(variants) == str(xdata['variant_id']):       # match json variant by requested variant #                                        
                                                        if int(xdata['quantity']) >= int(quantity):             # check the json variant quantity is greater than or equal to the requested quantity #                                  
                                                            if xdata['fulfillment_status'] == "fulfilled":              # match json fulfillment_status is fulfilled or not #                                      
                                                                quant = int(quantity)                                                    
                                                                total = str(float(xdata["price"]) * float(quant))                                                   
                                                                ful_stat = xdata['fulfillment_status']
                                                        else:
                                                            message = "wrong quantity error"
                                                            my_dict['error_message'] = message
                                                            return HttpResponse(json.dumps(my_dict), content_type="application/json")
                                        
                                            if (',' in request.GET.get('variants')) and (',' in request.GET.get('quantity')):   # check that ',' in requested variant and quantity then separate it by ',' #
                                                count = 0
                                                if len(variants) == len(quantity) :
                                                    variant_da = ','.join(variants) 
                                                    qunt_da = ','.join(quantity) 
                                                else:
                                                    message = "something went wrong!"
                                                    my_dict['error_message'] = message
                                                    return HttpResponse(json.dumps(my_dict), content_type="application/json")
                                            else:
                                                count = 999
                                                variant_da = variants 
                                                qunt_da = quantity 

                                            # date = datetime.datetime.now().strftime("%d"+"/"+"%m"+"/"+"%Y")
                                            # from .models import detail_order
                                            get_rec_data_read = detail_order.objects.filter(Q(shop_data=shop_domain), Q(order_id=str(ord_id)), Q(variants=str(variant_da)), Q(quantity=str(qunt_da)), Q(custom_id=str(cus_id)))
                                            # above line filter data from 'detail_order' table #
                                            if get_rec_data_read:   # data is  match then return an error #
                                                message = "Already requested for return!"
                                                my_dict['error_message'] = message
                                                return HttpResponse(json.dumps(my_dict), content_type="application/json")
                                            else:
                                                # create new entry in 'detail_order' table #
                                                get_rec_data = detail_order.objects.create(order_total = total, order_fulfill_status = ful_stat, shop_data = shop_domain, variants = variant_da, quantity = qunt_da, tquant = quant, order_id = ord_id, ordid = or_id, order_reason = reas_note, order_note = "", status = "PENDING", custom_id = cus_id) # , crea_date = date, upda_date = date #
                                                # start to get id, shop_data and status from the new record #
                                                data_detail = get_rec_data.pk
                                                # print(data_detail)
                                                data_shop = get_rec_data.shop_data
                                                data_status = get_rec_data.status
                                                # end  to get data #

                                                
                                                if count == 999:    # for single data in request get variant, quantity and reason_note #
                                                    variant_data = variants
                                                    quant_data = quantity
                                                    reason_data = reas_note

                                                    # store the data by variants in 'requested_variant' table #
                                                    from .models import requested_variant
                                                    request_vari_data = requested_variant.objects.create(order_number=or_id, cust_id=cus_id, variants=variant_data, r_status=data_status, varaint_shop=data_shop, quantity=quant_data, status=get_rec_data.order_fulfill_status, order_reason=reason_data, order_note="", detail_order_id_id=data_detail)   # , crea_date=date_data, upda_date=date_data #
                                                else:   # multiple data in request get variant, quantity and reason_note #
                                                    
                                                    if len(variants) == len(quantity) == len(reas_note):    # check the length of requested variant, quantity and reason_note #
                                                        for j_vari, jdata_vari in enumerate(variants, start=0):
                                                            # start to get variant wise data #
                                                            variant_data = variants[j_vari]
                                                            quant_data = quantity[j_vari]
                                                            reason_data = reas_note[j_vari]
                                                            # end to get data #

                                                            # store the data by variants in 'requested_variant' table #
                                                            request_vari_data = requested_variant.objects.create(order_number=or_id, cust_id=cus_id, variants=variant_data, r_status=data_status, varaint_shop=data_shop, quantity=quant_data, status=get_rec_data.order_fulfill_status, order_reason=reason_data, order_note="", detail_order_id_id=data_detail) # , crea_date=date_data, upda_date=date_data #
                                                    else:   # execute when length of requested data is not match #
                                                        message = "some data are missing!"
                                                        my_dict['error_message'] = message
                                                        return HttpResponse(json.dumps(my_dict), content_type="application/json")
                                            
                                                get_data = my_dict
                                                from .models import data_admin, thank_you  # import data_admin and thank_you table from models.py #
                                                datadmin = data_admin.objects.all() # get the data from data_admin(SuperAdmin) table #
                                                if datadmin: # if SuperAdmin data get #
                                                    # start to get icon, email, address and description(html) of SuperAdmin #
                                                    get_data['html'] = datadmin[0].Desctiption_data
                                                    get_data['logo'] = "https://python.penveel.com/media/" + str(datadmin[0].Imageurl)
                                                    get_data['email'] = datadmin[0].emaildata
                                                    get_data['address'] = datadmin[0].address
                                                    # end to get data #
                                                    data_thanks = thank_you.objects.filter(shop_name=str(shop_domain))  # filter vendor thank_you page data by shop domain #
                                                    if data_thanks: # filter success #
                                                        # start to get icon, email, address and description(html) of Vendor #
                                                        logo = "https://python.penveel.com/media/" + data_thanks[0].logo_upload
                                                        email = data_thanks[0].email_id
                                                        address = data_thanks[0].ven_address
                                                        get_data['logo'] = logo
                                                        get_data['email'] = email
                                                        get_data['address'] = address 
                                                        # end to get data #
                                                        # return data in json of get_data #
                                                        return HttpResponse(json.dumps(get_data), content_type="application/json")
                                                    else:
                                                        return HttpResponse(json.dumps(get_data), content_type="application/json")           
                                        else:
                                            if(len(data_dict_data['line_items']) > 0):  # check the length of line_items in order json #
                                                
                                                data_dict_data['all_reasons'] = product.get_product_id(line_items=data_dict_data['line_items'], spname=shop_domain, Tooken=token, sh_id=sid)        # get the reson from 'ras.saara.io' return_reson API #
                                                get_data = data_dict_data
                                                return HttpResponse(json.dumps(get_data), content_type="application/json")
                                            else:
                                                message = "all items requested for return"
                                                my_dict['error_message'] = message
                                                return HttpResponse(json.dumps(my_dict), content_type="application/json") 
                                    else:
                                        message = "matching Order not found"
                                        my_dict['error_message'] = message
                                        return HttpResponse(json.dumps(my_dict), content_type="application/json") 

                        else:
                            message = "Order not found!"
                            my_dict['error_message'] = message
                            return HttpResponse(json.dumps(my_dict), content_type="application/json")
                    # Enable Above # 
                else:
                    db_count = 0
                    print('freemium else')                  # after free count #
                    installation_data = installer.objects.get(shop=shop_domain)
                    if installation_data:
                        insta_date = installation_data.install_date
                        shop_id = installation_data.id
                        
                    # pass     
                    # Order API code start (API by Customer_id)  #
                    # Enable Below #
                        ur = "https://%s/admin/orders.json?customer_id=%s&financial_status=paid,partially_refunded,refunded&status=any" % (shop_domain, cus_id)
                    
                        headers = {
                            "X-Shopify-Access-Token": token,
                            "Content-Type": "application/json",
                            "client_id": API_KEY,
                            "client_secret": SHARED_SECRET
                        }
                        r = requests.get(url=ur, headers=headers)
                        c_data = json.loads(r.text)
                        get_data = dict()
                        data_vari_dict = dict()
                        # Order API code end (return json format data in c_data) #
                    
                        if c_data != "":        # check that above json is not none or blank #
                            for x in c_data["orders"]:
                                if x['financial_status'] == "refunded": # check that the order is refunded or not #
                                    message = "Order fully refunded"
                                    my_dict['error_message'] = message
                                    return HttpResponse(json.dumps(my_dict), content_type="application/json")
                                else:
                                    # global data_dict_data
                                    data = x
                                    data_dict_data = data

                                    if data['email'] == cus_email and str(data['order_number']) == str(ord_id): # match the requested email and order number in order API json #
                                        or_id = data["id"]
                                        count = 0
                                        # from .models import detail_order
                                        data_detail_variant = detail_order.objects.filter(Q(shop_data=shop_domain), Q(ordid=str(or_id)), Q(order_id=str(ord_id)), Q(custom_id=str(cus_id)))
                                        # above line filter data from 'detail_order' table #
                                        if data_detail_variant:     # match data in 'detail_order' get variant and quantity data #

                                            # start code for get variant and quantity data and append the data in  the list #
                                            data_vari_dict['line_items'] = list()
                                            for data_detail in data_detail_variant:
                                                vda_variants = data_detail.variants
                                                vda_quant = data_detail.quantity
                                                

                                                if ',' in vda_variants:
                                                    count = 0
                                                    vdata_vari = vda_variants.split(',')
                        
                                                else:
                                                    count = 999
                                                    vdata_vari = vda_variants
                                                

                                                if ',' in vda_quant:
                                                    count = 0
                                                    vdata_quant = vda_quant.split(',')
                                                
                                                else:
                                                    count = 999
                                                    vdata_quant = vda_quant


                                                if count == 999: 
                                                    data = dict()
                                                    data_y = vdata_quant
                                                    data_x = vdata_vari
                                                    
                                                    update = "false"
                                                    if len(data_vari_dict['line_items']) != 0:
                                                        for d in data_vari_dict['line_items']:
                                                            if str(d['variants']) == str(data_x):
                                                                d['quant'] = int(data_y) + int(d['quant'])
                                                                update = "true"
                                                                break
                                                    if update == "false":
                                                        da = {
                                                            "variants":data_x,
                                                            "quant":data_y
                                                        }
                                                        data_vari_dict['line_items'].append(da)

                                                else:
                                                    if len(vdata_vari) == len(vdata_quant):
                                                        for x in range(len(vdata_vari)):
                                                            data = dict()
                                                            data_y = vdata_quant[x]
                                                            data_x = vdata_vari[x]

                                                            update = "false"
                                                            if len(data_vari_dict['line_items']) != 0:
                                                                for d in data_vari_dict['line_items']:
                                                                    
                                                                    if str(d['variants']) == str(data_x):
                                                                    
                                                                        d['quant'] = int(data_y) + int(d['quant'])
                                                                        
                                                                        update = "true"
                                                                        break
                                                            if update == "false":
                                                                da = {
                                                                    "variants":data_x,
                                                                    "quant":data_y
                                                                }
                                                                data_vari_dict['line_items'].append(da) 
                                            # end code for get variant and quantity data and append the data in  the list #


                                            if len(data_vari_dict['line_items']) > 0 and len(data_dict_data['line_items']) > 0: # check the length of json line_items and created line_items list #
                                                for l, data_line in enumerate(data_dict_data['line_items'], start=0):
                                                    for data_database in data_vari_dict['line_items']:
                                                    
                                                        if int(data_line['variant_id']) == int(data_database['variants']):  # match variant from json line_items and create line_items #
                                                            if int(data_line['quantity']) == int(data_database['quant']):   # match quantity from json line_items and create line_items #
                                                                
                                                                data_dict_data['line_items'][l] = ''
                                                                break
                                                            elif int(data_line['quantity']) > int(data_database['quant']):    # check that the quantity in json is greater than requested quantity then it's deduct requested quantity from json #
                                                                data_line['quantity'] = int(data_line['quantity']) - int(data_database['quant'])
                                                                break
                                                
                                            data_dict_data['line_items'] = list(filter(None, data_dict_data['line_items']))
                                            
                                        
                                        if (request.GET.get('variants') is not None) and (request.GET.get('quantity') is not None): # check the requested variant and quantity is not none or blank #
                                            db_count += 1
                                            # print(shop_id, insta_date)
                                            counter_data_checker = Counter_Shop_Detail.objects.filter(store_id=shop_id)
                                            # print(counter)
                                            if counter_data_checker:
                                                print('counter_data_checker if')
                                                get_counter_data = counter_data_checker[0].counter
                                                get_counter_data += db_count
                                                Counter_Shop_Detail.objects.filter(store_id=shop_id).update(counter=get_counter_data)
                                                rec_id = plan_charges.objects.get(shop_id=int(shop_id)).application_charge_id
                                                usage_price = float(float(db_count)*0.40)
                                                print(usage_price)
                                                usage = BillingAPI.usage_charges(shop_data=shop_domain, token=token, ruc_id=rec_id, price=usage_price)
                                                print(usage)

                                            else:
                                                print('counter_data_checker else')
                                                # print(shop_id)
                                                Counter_Shop_Detail.objects.create(store_id_id=int(shop_id), counter=db_count, reset_date=insta_date)
                                                rec_id = plan_charges.objects.get(shop_id=int(shop_id)).application_charge_id
                                                usage_price = float(float(db_count)*0.40)
                                                print(usage_price)
                                                usage = BillingAPI.usage_charges(shop_data=shop_domain, token=token, ruc_id=rec_id, price=usage_price)
                                                print(usage)

                                            total = 0
                                            quant = 0
                                            ful_stat = ''
                                            if (',' in request.GET.get('variants')) and (',' in request.GET.get('quantity')) and ('||' in request.GET.get('notes')):    # check that ',' in variant and quantity and '||' in notes  then separate it #
                                                count = 0
                                                variants = request.GET.get('variants').split(',')
                                                quantity = request.GET.get('quantity').split(',')
                                                reas_note = request.GET.get('notes').split('||')
                                            
                                                if len(data_dict_data) != 0:  # check the length of data_dict_data #
                                                    
                                                    for dk, dvdata in enumerate(data_dict_data['line_items'], start=0): 
                                                        for j, jdata in enumerate(variants, start=0):
                                                            dvvari = variants[j]
                                                            if str(dvvari) == str(dvdata['variant_id']):    # match json variant by requested variant #
                                                            
                                                                if int(dvdata['quantity']) < int(quantity[j]):  # check json quantity by requested quantity (requested quantity is max the show an error) #
                                                                    message = "wrong quantity error"
                                                                    my_dict['error_message'] = message
                                                                    return HttpResponse(json.dumps(my_dict), content_type="application/json")
                                                
                                                for xdata in data_dict_data['line_items']:  
                                                    for i in range(len(variants)): 
                                                        xvari = variants[i]
                                                        if str(xvari) == str(xdata['variant_id']):      # match json variant by requested variant #
                                                            if int(xdata['quantity']) >= int(quantity[i]):  # check the json variant quantity is greater than or equal to the requested quantity #
                                                                if xdata['fulfillment_status'] == "fulfilled":  # match json fulfillment_status is fulfilled or not #
                                                                    quant = int(quantity[i]) + int(quant)

                                                                    lintotal = float(float(xdata["price"]) * float(quantity[i]))
                                                                    total = lintotal + total                                                        
                                                                    ful_stat = xdata['fulfillment_status']
                                                            else:
                                                                message = "wrong quantity error"
                                                                my_dict['error_message'] = message
                                                                return HttpResponse(json.dumps(my_dict), content_type="application/json")
                                            else:
                                                count = 999
                                                variants = request.GET.get('variants')
                                                quantity = request.GET.get('quantity')
                                                reas_note = request.GET.get('notes')
                                            
                                                if len(data_vari_dict) != 0:
                                                    for dvdata in data_vari_dict['line_items']: 
                                                        dvvari = variants
                                                        if str(dvvari) == str(dvdata['variants']):      # match variant of data_vari_dict to requested variant if requested variant is single data #
                                                            if int(dvdata['quant']) < int(quantity):
                                                                message = "wrong quantity error"
                                                                my_dict['error_message'] = message
                                                                return HttpResponse(json.dumps(my_dict), content_type="application/json")

                                                
                                                for xdata in data_dict_data['line_items']:                                       
                                                    if str(variants) == str(xdata['variant_id']):       # match json variant by requested variant #                                        
                                                        if int(xdata['quantity']) >= int(quantity):             # check the json variant quantity is greater than or equal to the requested quantity #                                  
                                                            if xdata['fulfillment_status'] == "fulfilled":              # match json fulfillment_status is fulfilled or not #                                      
                                                                quant = int(quantity)                                                    
                                                                total = str(float(xdata["price"]) * float(quant))                                                   
                                                                ful_stat = xdata['fulfillment_status']
                                                        else:
                                                            message = "wrong quantity error"
                                                            my_dict['error_message'] = message
                                                            return HttpResponse(json.dumps(my_dict), content_type="application/json")
                                        
                                            if (',' in request.GET.get('variants')) and (',' in request.GET.get('quantity')):   # check that ',' in requested variant and quantity then separate it by ',' #
                                                count = 0
                                                if len(variants) == len(quantity) :
                                                    variant_da = ','.join(variants) 
                                                    qunt_da = ','.join(quantity) 
                                                else:
                                                    message = "something went wrong!"
                                                    my_dict['error_message'] = message
                                                    return HttpResponse(json.dumps(my_dict), content_type="application/json")
                                            else:
                                                count = 999
                                                variant_da = variants 
                                                qunt_da = quantity 

                                            # date = datetime.datetime.now().strftime("%d"+"/"+"%m"+"/"+"%Y")
                                            # from .models import detail_order
                                            get_rec_data_read = detail_order.objects.filter(Q(shop_data=shop_domain), Q(order_id=str(ord_id)), Q(variants=str(variant_da)), Q(quantity=str(qunt_da)), Q(custom_id=str(cus_id)))
                                            # above line filter data from 'detail_order' table #
                                            if get_rec_data_read:   # data is  match then return an error #
                                                message = "Already requested for return!"
                                                my_dict['error_message'] = message
                                                return HttpResponse(json.dumps(my_dict), content_type="application/json")
                                            else:
                                                # create new entry in 'detail_order' table #
                                                get_rec_data = detail_order.objects.create(order_total = total, order_fulfill_status = ful_stat, shop_data = shop_domain, variants = variant_da, quantity = qunt_da, tquant = quant, order_id = ord_id, ordid = or_id, order_reason = reas_note, order_note = "", status = "PENDING", custom_id = cus_id) # , crea_date = date, upda_date = date #
                                                # start to get id, shop_data and status from the new record #
                                                data_detail = get_rec_data.pk
                                                print(data_detail)
                                                data_shop = get_rec_data.shop_data
                                                data_status = get_rec_data.status
                                                # end  to get data #

                                                # Charges Table Entry #
                                                # from .models import PerMonth_Charges
                                                # PerMonth_Charges.objects.create(store_name=data_shop, reference_id=get_rec_data.id)
                                                # End Charges Table #
                                                
                                                if count == 999:    # for single data in request get variant, quantity and reason_note #
                                                    variant_data = variants
                                                    quant_data = quantity
                                                    reason_data = reas_note


                                                    from .models import requested_variant
                                                    # date_data = datetime.datetime.now()
                                                    # store the data by variants in 'requested_variant' table #
                                                    request_vari_data = requested_variant.objects.create(order_number=or_id, cust_id=cus_id, variants=variant_data, r_status=data_status, varaint_shop=data_shop, quantity=quant_data, status=get_rec_data.order_fulfill_status, order_reason=reason_data, order_note="", detail_order_id_id=data_detail)   # , crea_date=date_data, upda_date=date_data #
                                                else:   # multiple data in request get variant, quantity and reason_note #
                                                    
                                                    if len(variants) == len(quantity) == len(reas_note):    # check the length of requested variant, quantity and reason_note #
                                                        for j_vari, jdata_vari in enumerate(variants, start=0):
                                                            # start to get variant wise data #
                                                            variant_data = variants[j_vari]
                                                            quant_data = quantity[j_vari]
                                                            reason_data = reas_note[j_vari]
                                                            # end to get data #
                                                            
                                                            from .models import requested_variant
                                                            # date_data = datetime.datetime.now()
                                                            # store the data by variants in 'requested_variant' table #
                                                            request_vari_data = requested_variant.objects.create(order_number=or_id, cust_id=cus_id, variants=variant_data, r_status=data_status, varaint_shop=data_shop, quantity=quant_data, status=get_rec_data.order_fulfill_status, order_reason=reason_data, order_note="", detail_order_id_id=data_detail)   # , crea_date=date_data, upda_date=date_data #
                                                    else:   # execute when length of requested data is not match #
                                                        message = "some data are missing!"
                                                        my_dict['error_message'] = message
                                                        return HttpResponse(json.dumps(my_dict), content_type="application/json")
                                            
                                                get_data = my_dict
                                                from .models import data_admin, thank_you  # import data_admin and thank_you table from models.py #
                                                datadmin = data_admin.objects.all() # get the data from data_admin(SuperAdmin) table #
                                                if datadmin: # if SuperAdmin data get #
                                                    # start to get icon, email, address and description(html) of SuperAdmin #
                                                    get_data['html'] = datadmin[0].Desctiption_data
                                                    get_data['logo'] = "https://python.penveel.com/media/" + str(datadmin[0].Imageurl)
                                                    get_data['email'] = datadmin[0].emaildata
                                                    get_data['address'] = datadmin[0].address
                                                    # end to get data #
                                                    data_thanks = thank_you.objects.filter(shop_name=str(shop_domain))  # filter vendor thank_you page data by shop domain #
                                                    if data_thanks: # filter success #
                                                        # start to get icon, email, address and description(html) of Vendor #
                                                        logo = "https://python.penveel.com/media/" + data_thanks[0].logo_upload
                                                        email = data_thanks[0].email_id
                                                        address = data_thanks[0].ven_address
                                                        get_data['logo'] = logo
                                                        get_data['email'] = email
                                                        get_data['address'] = address 
                                                        # end to get data #
                                                        # return data in json of get_data #
                                                        return HttpResponse(json.dumps(get_data), content_type="application/json")
                                                    else:
                                                        return HttpResponse(json.dumps(get_data), content_type="application/json")           
                                        else:
                                            if(len(data_dict_data['line_items']) > 0):  # check the length of line_items in order json #
                                                
                                                data_dict_data['all_reasons'] = product.get_product_id(line_items=data_dict_data['line_items'], spname=shop_domain, Tooken=token, sh_id=sid)        # get the reson from 'ras.saara.io' return_reson API #
                                                get_data = data_dict_data
                                                return HttpResponse(json.dumps(get_data), content_type="application/json")
                                            else:
                                                message = "all items requested for return"
                                                my_dict['error_message'] = message
                                                return HttpResponse(json.dumps(my_dict), content_type="application/json") 
                                    else:
                                        message = "matching Order not found"
                                        my_dict['error_message'] = message
                                        return HttpResponse(json.dumps(my_dict), content_type="application/json") 
                        else:
                            message = "Order not found!"
                            my_dict['error_message'] = message
                            return HttpResponse(json.dumps(my_dict), content_type="application/json")
                    # Enable Above #   
            else:
                pass           
        else:
            message = "Some filed are missing"
            my_dict['error_message'] = message
            return HttpResponse(json.dumps(my_dict), content_type="application/json")
        # Order match functional code end
        return HttpResponse(json.dumps(get_data), content_type="application/json")    
        # return functional code end #

    # return_request functional code start (display return request in shopify page(return_request) ) #
    @staticmethod
    def get_customer(request):
        error_dict = dict()
        custome_id = request.GET.get('customer')
        shop = request.GET.get('shop')

        if (custome_id is not None and custome_id != '') and (shop is not None and shop != ''): # check the requested field is not none or blank #
            shop = shop +'.myshopify.com'
            # from .models import detail_order
            posts = detail_order.objects.filter(Q(custom_id=custome_id), Q(shop_data=shop))  # data filter from 'detail_order' table by shop and customer id  #
            
            if posts:   # fetch all data if filter successfully #
                ''' BELOW FUNCTION CALL FOR GET ORDER VARIANT BY IT'S ID '''
                main_dict = dict()
                main_sub_dict = dict()

                for x in posts:
                    o_id = x.id
                    o_page_id = x.ordid
                    c_order_id = x.order_id
                    c_order_fulfill_status = x.order_fulfill_status
                    c_crea_date = x.crea_date
                    c_status = x.status  
                    c_refund_date = x.upda_date
                    if (',' in x.variants): # multiple value separater from variants #
                        y =  x.variants.split(',')
                    else:    # single value variants #
                        y = x.variants

                    if (',' in x.quantity): # multiple value separater from quantity #
                        q =  x.quantity.split(',')
                    else:   # single value quantity #
                        q = x.quantity

                    
                    c_json_data = ''
                    if o_page_id is not None and o_page_id != '':       # check the fetched data is not none or blank #
                        
                        d_rec = installer.objects.filter(shop=shop)     # filter data from 'installer' table by shop domain(shop) #
                        from .models import requested_variant
                        if d_rec:   # if get data by filtering then get token from 'installer' table #
                            token = d_rec[0].access_token
                            
                            url = "https://%s/admin/api/%s/orders/%s.json" % (shop, API_VERSION, o_page_id) # OrderAPI GET ORDER detail from order id(o_page_id)  #

                            headers = {
                                "X-Shopify-Access-Token": token,
                                "Content-Type": "application/json",
                                "client_id": API_KEY,
                                "client_secret": SHARED_SECRET
                            }

                            r = requests.get(url=url, headers=headers)
                            c_json_data = json.loads(r.text)    # return json data c_json_data #

                            request_notes = dict()
                           
                            if ',' in x.variants:   # multiple variant separater by ',' #
                                
                                for data_y in y:
                                    
                                    variant = data_y
                                    data_request = requested_variant.objects.filter(Q(variants=str(variant)), Q(detail_order_id_id=str(o_id)), Q(varaint_shop=shop))    # filtering data form requested_variant #
                                    if data_request:    # get data(customer note, vendor note and status) from table #
                                        request_notes[variant] = {
                                            'cus_note': data_request[0].order_reason,
                                            'ven_note': data_request[0].order_note,
                                            'r_status': data_request[0].r_status
                                        }
                                       
                            else:    # single variant #
                                variant = y
                                data_request = requested_variant.objects.filter(Q(variants=str(variant)), Q(detail_order_id_id=str(o_id)), Q(varaint_shop=shop))    # filtering data form requested_variant #
                                if data_request:    # get data(customer note, vendor note and status) from table #
                                    request_notes[variant] = {
                                        'cus_note': data_request[0].order_reason,
                                        'ven_note': data_request[0].order_note,
                                        'r_status': data_request[0].r_status
                                    }
                            
                            main_sub_dict[o_id] = {'datavaritan':y, 'dataqnt':q, 'request_notes':request_notes, 'variants':c_json_data['order']['line_items'],'order_no':c_order_id,'order_status':c_order_fulfill_status,'create_date':c_crea_date,'refund_date':c_refund_date,'refund_status':c_status}   # create dictionary by order_id(ex. #1(database entry id)) #
                            main_dict = main_sub_dict.copy() # copy main_sub_dict to main_dict #
                variant_data = main_dict    # return main_dict #
                
                return JsonResponse(variant_data)
            else:
                message = "no data founds"
                error_dict['error_message'] = message
                return HttpResponse(json.dumps(error_dict), content_type="application/json")
        else:
            message = "Some filed are missing"
            error_dict['error_message'] = message
            return HttpResponse(json.dumps(error_dict), content_type="application/json")
        # return_request functional code end #
