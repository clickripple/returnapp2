from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.views.decorators.clickjacking import xframe_options_exempt
import requests
import datetime
import shopify as shopifyapi
from .models import installer, about_data, Policy_data, Homedata
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
import json
# from django.conf.urls.static import settings
from django.db.models import Q
from django.shortcuts import redirect as redc

API_KEY = "8444dc202d58790ecb461d128a8a2b86"
SHARED_SECRET = "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"
API_VERSION = "2020-07"

shop = ""

# login page view functional code start (display template while go to main page) #
def login(request):
    return render(request, 'login.html')
# login page view functional code end #

# about page functional code start #
@xframe_options_exempt
def about(request):
    about_rec = about_data.objects.all()        # fetch all data from 'about_data' table #
    if len(about_rec)!=0:   # check the length of fetched data and extract title and description #
        title = about_rec[0].title
        des = about_rec[0].description
        return render(request, 'about.html', {'til': title, 'desc':des})    # return dictionary on about page #
    else:
        return render(request, 'about.html')
# about page functional code end #

# Home page functional code start #
@xframe_options_exempt
def home_page(request):
    home_rec = Homedata.objects.all()       # fetch all data from 'Homedata' table #
    if home_rec:        # fetch data from 'Homedata' table get description(data) #
        data = home_rec[0].Desctiption
        return render(request, 'home.html', {'home_data':data})     # return dictionary on home page #
    else:
        return render(request, 'home.html')
# Home page functional code end #

# privacy_policy functional code start #
@xframe_options_exempt
def policy(request):
    policy_rec = Policy_data.objects.all()      # fetch record from 'privacy_rec' table #
    if len(policy_rec)!=0:  # check the length of fetched data then get title and description from 'privacy_rec' table #
        pol_title = policy_rec[0].policy_title
        pol_desc = policy_rec[0].policy_description
        return render(request, 'privacy_policy.html', {'p_til': pol_title, 'p_desc': pol_desc})     # return dictionary to 'privacy_policy' template #
    else:
        return render(request, 'privacy_policy.html')
# privacy_policy functional code end #

# instruct page 'view' functional code start #
@xframe_options_exempt
def instruct(request):
    return render(request, 'instruction.html', {'instruct_data': 'pending'})
# instruct page 'view' functional code end #

# API for calculate refund functional code start (calculate refund by order_id and line_item's id) #
def refundwocurency(order_id, data_dict):
    main_dict = dict()
    if shop is not None and shop != '':
        data_installer = installer.objects.filter(shop=shop)    # filter data from 'installer' table by shop #
        if data_installer:      # fetch data from installer then get the token  #
            token = data_installer[0].access_token
        else:
            message = "shop data not found in database"
            main_dict['error_message'] = message
            return HttpResponse(json.dumps(main_dict), content_type="application/json")

        url = "https://%s:%s@%s/admin/api/%s/orders/%s/refunds/calculate.json" % (API_KEY, SHARED_SECRET, shop, API_VERSION, order_id)      # order_id is passed from returnapprove when the function is called #
        header = {
            "X-Shopify-Access-Token": token,
            "Content-Type": "application/json",
            "client_id": API_KEY,
            "client_secret": SHARED_SECRET
        }
        
        my_data = {
            "refund": {
                "shipping": {
                "full_refund": "false"
                },
                "refund_line_items": data_dict          # data_dict is passed from returnapprove when the function is called #
            }
        }

        r = requests.post(url=url, headers=header, json=my_data)
        c_data = json.loads(r.text)
        return c_data       # return json data in c_data #
# API for calculate refund functional code end #

# API for create_refund functional code start (create refund when refund is calculated) #
def create_refund(order_id, note, da):
    my_json = dict()
    
    if shop is not None and shop != '':
        data_installer = installer.objects.filter(shop=shop)    # filter data from 'installer' table by shop #
        if data_installer:          # fetch data from installer then get the token  #
            token = data_installer[0].access_token
        else:
            message = "shop data not found in database"
            main_dict['error_message'] = message
            return HttpResponse(json.dumps(main_dict), content_type="application/json")

    url = "https://%s:%s@%s/admin/api/%s/orders/%s/refunds.json" % (API_KEY, SHARED_SECRET, shop, API_VERSION, order_id)    # order_id is passed from returnapprove when the function is called #

    header = {
        "X-Shopify-Access-Token": token,
        "Content-Type": "application/json",
        "client_id": API_KEY,
        "client_secret": SHARED_SECRET
    }

    my_json["refund"] = da      # da is passed from returnapprove when the function is called #
    my_json["refund"]['transactions'][0]['kind'] = 'refund'
    my_json['refund']['notify'] = 'true'
    my_json['refund']['note'] = note        # note is passed from returnapprove when the function is called #
    r = requests.post(url=url, headers=header, json=my_json)
    c_json = json.loads(r.text)
    return c_json   # return json data in c_json #
# API for create_refund functional code end #

# Approve functional code start (to approve return request) #
@csrf_exempt
def returnapprove(request):
    count = 0
    final_dict = {}
    my_dict = dict()
    if (request.GET.get('orderid') is not None and request.GET.get('orderid')!='') and (request.GET.get('vari') is not None and request.GET.get('vari')!='') and (request.GET.get('id') is not None and request.GET.get('id')!='') and (request.GET.get('quantity') is not None and request.GET.get('quantity')!=''):
        # above line check requested data is not none or blank except notes and note #
        note = request.GET.get('note')
        notes = request.GET.get('notes')
        orderid = request.GET.get('orderid')

        if ((',' in request.GET.get('id')) and (',' in request.GET.get('quantity')) and (',' in request.GET.get('vari')) and ('||' in request.GET.get('notes'))):       
            # above line check ',' in variant and quantity and '||' in notes for multiple variants then separate it #
            count = 0                       # multiple variant request #
            itemid = request.GET.get('id').split(',')
            quan = request.GET.get('quantity').split(',')
            itemvari = request.GET.get('vari').split(',')
            variant_note = request.GET.get('notes').split('||')
        else:
            count = 999     # single variant request #
            itemid = request.GET.get('id')
            quan = request.GET.get('quantity')
            itemvari = request.GET.get('vari')
            variant_note = request.GET.get('notes')

            
        if ((',' in request.GET.get('id')) and (',' in request.GET.get('quantity')) and (',' in request.GET.get('vari'))):  
            # above line check ',' in id, quantity and vari then separate it in below code #
            count = 0       # multiple variant request #
            if len(itemid) == len(quan) == len(itemvari):       # match the length of requested data(itemid. quan, itemvari) #
                item_da = ','.join(itemid)
                qunt_da = ','.join(quan)
                itemvari_da = ','.join(itemvari)
            else:
                message = "something went wrong!"
                my_dict['error_message'] = message
                return HttpResponse(json.dumps(my_dict), content_type="application/json")
        else:
            item_da = itemid
            count = 999      # single variant request #
            qunt_da = quan
            itemvari_da = itemvari


        data_list = list()
    
        if count == 999:        # single variant request #
            data = dict()
            data['line_item_id'] = item_da
            data['quantity'] = qunt_da
            data['restock_type'] = "return"
            data_list.append(data)          # append above data in data_list #
        else:           # multiple variant request #
            if len(itemid) == len(quan) == len(itemvari):               # match the length of requested data(itemid. quan, itemvari) #
                for j_item, jdata_item in enumerate(itemid, start=0):
                    data = dict()
                    data_y = quan[j_item]
                    data_x = itemid[j_item]

                    data['line_item_id'] = data_x
                    data['quantity'] = data_y
                    data['restock_type'] = "return"
                    data_list.append(data)               # append above data in data_list #
            else:
                message = "Invalid Item!"
                my_dict['error_message'] = message
                return HttpResponse(json.dumps(my_dict), content_type="application/json")
        main_dict = dict()
        final_dict = data_list          # store data_list in final_dict #

        calculate_refund = refundwocurency(order_id=orderid, data_dict=final_dict)          # refund calculate (refundwocurency) API call #
        main_dict['shipping'] = calculate_refund['refund']['shipping']                      # extract refund shipping data from calculate_refund #
        main_dict['refund_line_items'] = calculate_refund['refund']['refund_line_items']    # extract refund line_items data from calculate_refund #
        main_dict['transactions'] = calculate_refund['refund']['transactions']              # extract refund transactions data from calculate_refund #
        main_dict['currency'] = calculate_refund['refund']['currency']                      # extract refund currency data from calculate_refund #
        refund_process = create_refund(order_id=orderid, note=note, da=main_dict)           # call create_refund and put orderid, note and main_dict #

        ref_id = ''
        for refund_x in refund_process['refund']['transactions']:           # for loop on refund_process['refund']['transactions'] #
            if refund_x['status'] == "success":             # check refund status is "success" #
                if count == 999:    # single value #
                    from .models import requested_variant, detail_order
                    variant_get_data = requested_variant.objects.filter(Q(varaint_shop=shop), Q(variants=str(itemvari_da)), Q(quantity=str(qunt_da)), Q(order_number=str(orderid)))
                    # above code filter data from 'requested_variant' table #
                    if variant_get_data:    # fetch data from 'requested_variant' table #
                        ref_id = variant_get_data[0].detail_order_id_id
                        p_id = variant_get_data[0].id
                        o_id = variant_get_data[0].order_number
                    else:
                        message = "no data found in request_variant"
                        my_dict['error_message'] = message
                        return HttpResponse(json.dumps(my_dict), content_type="application/json")

                    if p_id:
                        variant_data_update = requested_variant.objects.filter(Q(varaint_shop=shop), Q(id=str(p_id)), Q(order_number=str(orderid))).update(order_note=notes, r_status="APPROVED")
                        # filter and update record of 'requested_variant' table #
                    else:
                        message = "no id match in requested_variant"
                        my_dict['error_message'] = message
                        return HttpResponse(json.dumps(my_dict), content_type="application/json")

                    if ref_id:
                        check_status = detail_order.objects.filter(Q(shop_data=shop), Q(id=str(ref_id)), Q(status="DONE"), Q(ordid=str(o_id)))
                        # filter data from 'detail_order' table if status is done it pass #
                        if check_status:
                            pass
                        else:
                            # filter and update record of 'detail_order' table #
                            get_data_rec = detail_order.objects.filter(Q(shop_data=shop), Q(id=str(ref_id)), Q(ordid=str(o_id))).update(status="DONE", order_note=note)
                    else:
                        message = "no data found in detail_order"
                        my_dict['error_message'] = message
                        return HttpResponse(json.dumps(my_dict), content_type="application/json")
                else:   # multiple data #
                    if len(itemid) == len(quan) == len(itemvari):           # check then length of itemid, quan and itemvari #
                        from .models import requested_variant, detail_order
                        for j_item, jdata_item in enumerate(itemid, start=0):
                            if variant_note[j_item] == '':          # check the note is none than pass #
                                pass
                            else:
                                data_qun = quan[j_item]
                                data_varia = itemvari[j_item]
                                data_note = variant_note[j_item]

                                variant_get_data = requested_variant.objects.filter(Q(varaint_shop=shop), Q(variants=str(data_varia)), Q(quantity=str(data_qun)), Q(order_number=str(orderid)))
                                # above code filter data from 'requested_variant' table #
                                if variant_get_data:
                                    ref_id = variant_get_data[0].detail_order_id_id
                                    p_id = variant_get_data[0].id
                                    o_id = variant_get_data[0].order_number
                                    n_note = variant_get_data[0].order_note
                                else:
                                    message = "no data found in request_variant"
                                    my_dict['error_message'] = message
                                    return HttpResponse(json.dumps(my_dict), content_type="application/json")


                                if p_id:
                                    # filter and update record of 'requested_variant' table #
                                    variant_data_update = requested_variant.objects.filter(Q(varaint_shop=shop), Q(id=str(p_id)), Q(order_number=str(orderid))).update(order_note=data_note, r_status="APPROVED")
                                else:
                                    message = "no id match in requested_variant"
                                    my_dict['error_message'] = message
                                    return HttpResponse(json.dumps(my_dict), content_type="application/json")

                                if ref_id:
                                    # filter data from 'detail_order' table if status is done it pass #
                                    check_status = detail_order.objects.filter(Q(shop_data=shop), Q(id=str(ref_id)), Q(status="DONE"), Q(ordid=str(o_id)))
                                    if check_status:
                                        pass
                                    else:
                                        # filter and update record of 'detail_order' table #
                                        get_data_rec = detail_order.objects.filter(Q(shop_data=shop), Q(id=str(ref_id)), Q(ordid=str(o_id))).update(status="DONE", order_note=note)
                                else:
                                    message = "no data found in detail_order"
                                    my_dict['error_message'] = message
                                    return HttpResponse(json.dumps(my_dict), content_type="application/json")

        my_dict['status'] = "APPROVED"
        return HttpResponse(json.dumps(my_dict), content_type="application/json")
    else:
        my_dict['status'] = "APPROVED"
        return HttpResponse(json.dumps(my_dict), content_type="application/json")
# Approve functional code end #


# reject functional code start #        
@csrf_exempt
@xframe_options_exempt
def rejected(request):
    
    data_id = ''
    count = 0
    my_dict = dict()
    main_dict = dict()
    
    if (request.GET.get('orderid') is not None and request.GET.get('orderid')!='') and (request.GET.get('vari') is not None and request.GET.get('vari')!='') and (request.GET.get('id') is not None and request.GET.get('id')!='') and (request.GET.get('quantity') is not None and request.GET.get('quantity')!=''):
        # above code check the requested data is not none or blank except notes and note #
        note = request.GET.get('note')
        orderid = request.GET.get('orderid')
        notes = request.GET.get('notes') 

        if ((',' in request.GET.get('id')) and (',' in request.GET.get('quantity')) and (',' in request.GET.get('vari')) and ('||' in request.GET.get('notes'))):
            # check ',' in id, quantity and vari and '||' in notes then separate it #
            count = 0           # multiple data #
            itemid = request.GET.get('id').split(',')
            quan = request.GET.get('quantity').split(',')
            itemvari = request.GET.get('vari').split(',')
            variant_note = request.GET.get('notes').split('||')
        else:
            count = 999     # single data #
            itemid = request.GET.get('id')
            quan = request.GET.get('quantity')
            itemvari = request.GET.get('vari')
            variant_note = request.GET.get('notes')

            
        if ((',' in request.GET.get('id')) and (',' in request.GET.get('quantity')) and (',' in request.GET.get('vari'))):  # check ',' in id, vari and quantity #
            count = 0       # multiple data #
            if len(itemid) == len(quan) == len(itemvari):       # check length of requested data #
                item_da = ','.join(itemid)
                qunt_da = ','.join(quan)
                itemvari_da = ','.join(itemvari)
            else:
                message = "something went wrong!"
                my_dict['error_message'] = message
                return HttpResponse(json.dumps(my_dict), content_type="application/json")
        else:
            item_da = itemid
            count = 999     # single data #
            qunt_da = quan
            itemvari_da = itemvari
        
        ref_id = ''
        

        if count==999:      # single data #
            from .models import requested_variant, detail_order
            variant_get_data = requested_variant.objects.filter(Q(varaint_shop=shop), Q(variants=str(itemvari_da)), Q(quantity=str(qunt_da)), Q(order_number=str(orderid)))
            # above code filter data of requested_variant if data match extract re_ref_id, re_p_id and re_o_id #
            if variant_get_data:
                re_ref_id = variant_get_data[0].detail_order_id_id
                re_p_id = variant_get_data[0].id
                re_o_id = variant_get_data[0].order_number
            else:
                message = "no data found in request_variant"
                my_dict['error_message'] = message
                return HttpResponse(json.dumps(my_dict), content_type="application/json")
            

            if re_p_id:
                # filter and update record of 'requested_variant' table #
                variant_data_update = requested_variant.objects.filter(Q(varaint_shop=shop), Q(id=str(re_p_id)), Q(order_number=str(orderid))).update(order_note=notes, r_status="REJECTED")
            else:
                message = "no id match in requested_variant"
                my_dict['error_message'] = message
                return HttpResponse(json.dumps(my_dict), content_type="application/json")

            if re_ref_id:
                 # filter data from 'detail_order' table if status is done it pass #
                check_status = detail_order.objects.filter(Q(shop_data=shop), Q(id=str(re_ref_id)), Q(ordid=str(re_o_id)), Q(status="DONE"))
                if check_status:
                    pass
                else:
                     # filter and update record of 'detail_order' table #
                    get_data_rec = detail_order.objects.filter(Q(shop_data=shop), Q(id=str(re_ref_id)), Q(ordid=str(re_o_id))).update(status="DONE", order_note=note)
            else:
                message = "no data found in detail_order"
                my_dict['error_message'] = message
                return HttpResponse(json.dumps(my_dict), content_type="application/json")
        else:       # multiple data #
            if len(itemid) == len(quan) == len(itemvari):        # check length of requested data #
                
                from .models import requested_variant, detail_order
                for j_item, jdata_item in enumerate(itemid, start=0):
                    if variant_note[j_item] == '':      # check the note is none than pass #
                        pass
                    else:
                        re_data_qun = quan[j_item]
                        re_data_varia = itemvari[j_item]
                        re_data_note = variant_note[j_item]

                        

                        variant_get_data = requested_variant.objects.filter(Q(varaint_shop=shop), Q(variants=str(re_data_varia)), Q(quantity=str(re_data_qun)), Q(order_number=str(orderid)))
                        # above code filter data of requested_variant if data match extract re_ref_id, re_p_id and re_o_id, re_note #
                        if variant_get_data:
                            re_ref_id = variant_get_data[0].detail_order_id_id
                            re_p_id = variant_get_data[0].id
                            re_o_id = variant_get_data[0].order_number
                            re_note = variant_get_data[0].order_note
                        else:
                            message = "no data found in request_variant"
                            my_dict['error_message'] = message
                            return HttpResponse(json.dumps(my_dict), content_type="application/json")
                       

                        if re_p_id:
                            # filter and update record of 'requested_variant' table #
                            variant_data_update = requested_variant.objects.filter(Q(varaint_shop=shop), Q(id=str(re_p_id)), Q(order_number=str(orderid))).update(order_note=re_data_note, r_status="REJECTED")
                        else:
                            message = "no id match in requested_variant"
                            my_dict['error_message'] = message
                            return HttpResponse(json.dumps(my_dict), content_type="application/json")

                        if re_ref_id:
                             # filter data from 'detail_order' table if status is done it pass #
                            check_status = detail_order.objects.filter(Q(shop_data=shop), Q(id=str(re_ref_id)), Q(ordid=str(re_o_id)), Q(status="DONE"))
                            if check_status:
                                pass
                            else:
                                # filter and update record of 'detail_order' table #
                                get_data_rec = detail_order.objects.filter(Q(shop_data=shop), Q(id=str(re_ref_id)), Q(ordid=str(re_o_id))).update(status="DONE", order_note=note)
                        else:
                            message = "no data found in detail_order"
                            my_dict['error_message'] = message
                            return HttpResponse(json.dumps(my_dict), content_type="application/json")

        my_dict['status'] = "REJECTED"
        return HttpResponse(json.dumps(my_dict), content_type="application/json")

    else:
        my_dict['status'] = "REJECTED"
        return HttpResponse(json.dumps(my_dict), content_type="application/json")
# reject functional code end # 


# order page functional code start #
@xframe_options_exempt
@csrf_exempt
def order_page(request):
    '''
    order.html data parsing
    '''
    from django.core.paginator import Paginator
    from .models import detail_order
    posts = detail_order.objects.all()
    paginator = Paginator(posts, 10)
    page = request.GET.get('page')
    posts = paginator.get_page(page)  
    
    ''' BELOW FUNCTION CALL FOR GET ORDER VARIANT BY IT'S ID '''
    main_dict = dict()
    main_sub_dict = dict()

    for x in posts:
        o_page_id = x.ordid
        
        if (',' in x.variants):
            y =  x.variants.split(',')
        else:
            y = x.variants
        
        if (',' in x.quantity):
            q_qunt = x.quantity.split(',')
        else:
            q_qunt = x.quantity

        c_json_data = ''
        if o_page_id is not None and o_page_id != '':
            if shop is not None and shop != '':
                d_rec = installer.objects.filter(shop=shop)
                if d_rec:
                    token = d_rec[0].access_token
                    
                    url = "https://%s/admin/api/%s/orders/%s.json" % (shop, API_VERSION, o_page_id)

                    headers = {
                        "X-Shopify-Access-Token": token,
                        "Content-Type": "application/json",
                        "client_id": API_KEY,
                        "client_secret": SHARED_SECRET
                    }

                    r = requests.get(url=url, headers=headers)
                    c_json_data = json.loads(r.text)

                    main_sub_dict[x.id] = {'datavaritan':y, 'dataqnt':q_qunt,'variants':c_json_data['order']['line_items']}
                    main_dict = main_sub_dict.copy() 
    variant_data = main_dict
    
    return render(request, 'order.html', {'order_requests': posts, 'line_items': variant_data})
# order page functional code end #

# generate token functional code start #
def token(code, shop):
    ''' GENERATE ACCESS_TOKEN '''
    ur = "https://" + shop + "/admin/oauth/access_token"

    s = {
        "client_id": API_KEY,
        "client_secret": SHARED_SECRET,
        "code": code
    }
    r = requests.post(url=ur, json=s)
    x = json.loads(r.text)
    return x
# generate token functional code end #


# installation process functional code start #
def installation(request):
    if request.method == "POST":        # check request is post #
        url = request.POST['shop']      
        s_url = url.strip('/')
    
        api_key = API_KEY
        
        link = '%s/admin/oauth/authorize?client_id=%s&redirect_uri=https://6developer3i.pagekite.me/final&scope=read_products,write_products,read_customers,write_customers,read_orders,write_orders,read_themes,write_themes,write_content,read_content,write_script_tags,read_script_tags' % (s_url, api_key)
        
        li = link.strip("/")
       
        redirect = HttpResponseRedirect(f'{li}')
       
    return redirect
# installation process functional code end #

# redirect to app fucntional code start (while successfully installed redirect to app) #
def redirect(request):
    if request.GET.get('shop') is not None:     # check request data is not none #
        shop = request.GET.get('shop')
        redir = HttpResponseRedirect(redirect_to='https://' + shop + '/admin/apps/returnmagic-1')
    return redir
# redirect to app fucntional code end #

# Uninstall Webhook functional code start (to create webhook) #
def unistaller_second(request):
    if len(shop) != 0:              # check the length of shop #
        webrec = installer.objects.filter(shop=shop)        # filter installer data by shop#
        if webrec:
            token = webrec[0].access_token
            hmac_data = webrec[0].hmac
        else:
            HttpResponse("Invalid shop detail")

        url = "https://" + shop + "/admin/api/2020-07/webhooks.json"

        headers = {
            'X-Shopify-Access-Token': token,
            'X-Shopify-Topic': 'app/uninstalled',
            'X-Shopify-Hmac-Sha256': hmac_data,
            'X-Shopify-Shop-Domain': shop,
            'X-Shopify-API-Version': API_VERSION
        } 

        my = {
            "webhook": {
                "topic": "app/uninstalled",
                "address": 'https://6developer3i.pagekite.me/uninstall',  # uninstall process data send on the address #
                "format": "json"
            }
        }
    
        r = requests.post(url=url, json=my, headers=headers)
        c = json.loads(r.text)
        return HttpResponse(json.dumps(c), content_type="application/json")
# Uninstall Webhook functional code start

# app install final step functional code start (to add shop data into database) #
@xframe_options_exempt
def final(request):
    my_dict = dict()
    if request.GET.get('hmac') is not None:         # check hmac is not none #
        hmac = request.GET.get('hmac')
        global shop
        shop = request.GET.get('shop')
        if request.GET.get('code') is not None:     # check code is not none #
            code = request.GET.get('code')
            if len(code) != 0:              # check length of code #
                record = installer.objects.filter(shop=shop)    # filter installer data by shop #
                if record:
                    get_code = record[0].code
                    get_access_token = record[0].access_token
                    return redirect(request=request)
                else:
                    accesstoken = token(code=code, shop=shop)       # call token function to generate access_token #
                    rec = installer()           # call installer to add record #
                    rec.shop = shop
                    rec.code = code
                    rec.hmac = hmac
                    rec.access_token = accesstoken['access_token']
                    rec.save()      # save data in installer table #

                    tokn = accesstoken['access_token']
                    cr_date = datetime.datetime.now()

                    # ScriptTags.Create_ScriptTags_scss(store=shop, token=tokn)
                    from .pages_api import ScriptTags
                    ScriptTags.Create_ScriptTags_js(store=shop, token=tokn)
                    
                    unistaller_second(request=request)          # call 'unistaller_second' to create webhook #
                    return redirect(request=request)            # redirect to app #
                return redirect(request=request)
        else:
            record = installer.objects.filter(shop=shop)        # filter installer data by shop #    
            if record:
                getaccess = record[0].access_token
                getshop = record[0].shop
                return render(request, 'final.html')
            else:
                return HttpResponse("No Data Found")
    else:
        return render(request, 'login.html')
# app install final step functional code end #

# settings page 'view' functional code start #
@xframe_options_exempt
def settings(request):
    return render(request, 'settings.html')
# settings page 'view' functional code end #

# settings page functional code to upload data code start (upload vendor data into database) #
@csrf_exempt
def data_upload(request):
    my_dict = dict()
    from django.core.files.storage import FileSystemStorage
    if request.method == "POST":        # check request is post #
        thank_id = ''
        myfil = request.FILES['myfile']     
        sh = shop
        dta_installer = installer.objects.filter(shop=sh)        # filter installer data by shop #   
        if dta_installer:
            vendor_id = dta_installer[0].id
            fs = FileSystemStorage('var/www/html/media/' + str(vendor_id))      # filesystemstorage path to upload image #
            filename = fs.save(myfil.name, myfil)
            uploaded_file_url = fs.url(str(vendor_id) +"/"+ filename)
            address = request.POST['store_address']
            email = request.POST['store_email']
            from .models import thank_you
            data_thanks = thank_you.objects.filter(shop_name=str(sh))   # filter thank_you data by shop #   
            if data_thanks:
                thank_id = data_thanks[0].id
                imagedata = data_thanks[0].logo_upload
                image_list = imagedata.split('/')
                imagename = image_list[1]
                if thank_id:
                    data_image = uploaded_file_url.strip('var/www/html/media/') 
                    fs.delete(imagename)        # delete old image from folder #
                    # update record with new image file and data in 'thank_you' table #
                    data_thanks2 = thank_you.objects.filter(Q(id=str(thank_id))).update(shop_name=sh, logo_upload=data_image, email_id=email, ven_address=address)
            else:
                data_image = uploaded_file_url.strip('var/www/html/media/')
                # create new record in 'thank_you' table # 
                thank_data = thank_you.objects.create(shop_name=sh, logo_upload=data_image, email_id=email, ven_address=address)
        else:
            message = "no vendor found"
            my_dict['error_message'] = message
            return HttpResponse(json.dumps(my_dict), content_type="application/json")
    else:
        message = "Request is not posted"
        my_dict['error_message'] = message
        return HttpResponse(json.dumps(my_dict), content_type="application/json")
    return render(request, 'home.html')
# settings page functional code to upload data code end #

# ScriptTag API Functional Code start # 
@csrf_exempt
def install_page(request):
    my_dict = dict()
    store = shop
    data_script = installer.objects.filter(shop=store)
    if data_script:
        store_data = data_script[0].shop
        token = data_script[0].access_token
        c_date_data = datetime.datetime.now()

        from .pages_api import Assets, Page
        
        data_theme_id = Assets.get_theme_id(store=store_data, token=token)
        if len(str(data_theme_id)) > 0:
            
            data_assets_request = Assets.create_request(theme_id=data_theme_id, store=store_data, token=token)
            if len(data_assets_request) > 0:
                request_page = Page.create_return_request_page(store=store_data, token=token)
            else:
                message = "the data_assets_request is not successfully created"
                my_dict['error_message'] = message
                return HttpResponse(json.dumps(my_dict), content_type="application/json")

            data_assets_status = Assets.create_status(theme_id=data_theme_id, store=store_data, token=token)
            if len(data_assets_status) > 0:
                status_page = Page.create_return_status_page(store=store_data, token=token)
            else:
                message = "the data_assets_status is not successfully created"
                my_dict['error_message'] = message
                return HttpResponse(json.dumps(my_dict), content_type="application/json")

            Assets.create_css(theme_id=data_theme_id, store=store_data, token=token)
            Assets.create_sjs(theme_id=data_theme_id, store=store_data, token=token)
        else:
            message = "No theme found in store"
            my_dict['error_message'] = message
            return HttpResponse(json.dumps(my_dict), content_type="application/json")
        return render(request, 'instruction.html', {'instruct_data': "success"})
    else:
        message = "No store data found"
        my_dict['error_message'] = message
        return HttpResponse(json.dumps(my_dict), content_type="application/json")
# ScriptTag API Functional Code end #