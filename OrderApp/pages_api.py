import shopify
import json
import requests

API_KEY = '8444dc202d58790ecb461d128a8a2b86'
SHARED_SECRET = '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'
API_VERSION = '2020-07'

# my_error_dict = dict()

class Assets:

    @staticmethod
    def get_theme_id(store, token):
        print(store, token, "theme data")
        url = 'https://%s/admin/api/%s/themes.json' % (store, API_VERSION)
        print(url, 'theme url')
        header = {
            'X-Shopify-Access-Token': token,
            'Content-Type': 'application/json',
            'client_id': API_KEY,
            'client_secret': SHARED_SECRET
        } 

        r = requests.get(url=url, headers=header)
        print(r.status_code)
        if r.status_code == 200:
            print('yes data')
            c = json.loads(r.text)
            for x in c['themes']:
                return x['id']
        else:
            print('no data')
            c = ''
            return c

    @staticmethod
    def create_request(theme_id, store, token):
        url = 'https://%s/admin/api/%s/themes/%s/assets.json' % (store, API_VERSION, theme_id)

        header = {
            'X-Shopify-Access-Token': token,
            'Content-Type': 'application/json',
            'client_id': API_KEY,
            'client_secret': SHARED_SECRET
        } 

        data = {
            'asset': {
                'key': 'templates/page.psar_return_request.liquid',
                'value': "<div id='psar_returnpage' class='psar_returnpage'><div class='psar_grid'><div class='psar_grid__item psar_large--five-sixths psar_push--large--one-twelfth psar-main'> <header class='psar_section-header psar_text-center'><h1>{{ page.title }}</h1> </header><div class='psar_rte psar_rte--nomargin rte--indented-images'>{% if customer %}<div class='psar_wrapper'><div id='psar_errors' class='psar_errors'></div><div id='psar_step1' class='psar_step1'><form name='psar_order_form_a' data-customer='{{ customer.id }}' id='psar_order_form_a'><span id='message' class='psar_message_error'></span><label for='order_number'><input type='text' name='order_number' placeholder='Order Number' class='psar-order' id='order_number' value='' /><span class='psar_iconbar num' tooltip='Order'> <?xml version='1.0' encoding='iso-8859-1'?><svg version='1.1' id='Capa_1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink' x='0px' y='0px' viewBox='0 0 512 512' style='enable-background:new 0 0 512 512;' xml:space='preserve'> <g> <g> <g> <circle cx='256' cy='378.5' r='25' /> <path d='M256,0C114.516,0,0,114.497,0,256c0,141.484,114.497,256,256,256c141.484,0,256-114.497,256-256,C512,114.516,397.503,0,256,0z M256,472c-119.377,0-216-96.607-216-216c0-119.377,96.607-216,216-216,c119.377,0,216,96.607,216,216C472,375.377,375.393,472,256,472z' /> <path d='M256,128.5c-44.112,0-80,35.888-80,80c0,11.046,8.954,20,20,20s20-8.954,20-20c0-22.056,17.944-40,40-40,c22.056,0,40,17.944,40,40c0,22.056-17.944,40-40,40c-11.046,0-20,8.954-20,20v50c0,11.046,8.954,20,20,20,c11.046,0,20-8.954,20-20v-32.531c34.466-8.903,60-40.26,60-77.469C336,164.388,300.112,128.5,256,128.5z' /> </g> </g> </g> </svg> </span></label><span id='messagebar' style='display:none'></span><label for='order_email'><input type='text' name='order_email' placeholder='Email' value='{{customer.email}}' id='order_email' class='psar-email' /><span class='psar_iconbar num' tooltip='Email'> <?xml version='1.0' encoding='iso-8859-1'?><svg version='1.1' id='Capa_1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink' x='0px' y='0px' viewBox='0 0 512 512' style='enable-background:new 0 0 512 512;' xml:space='preserve'> <g> <g> <g> <circle cx='256' cy='378.5' r='25' /> <path d='M256,0C114.516,0,0,114.497,0,256c0,141.484,114.497,256,256,256c141.484,0,256-114.497,256-256,C512,114.516,397.503,0,256,0z M256,472c-119.377,0-216-96.607-216-216c0-119.377,96.607-216,216-216,c119.377,0,216,96.607,216,216C472,375.377,375.393,472,256,472z' /> <path d='M256,128.5c-44.112,0-80,35.888-80,80c0,11.046,8.954,20,20,20s20-8.954,20-20c0-22.056,17.944-40,40-40,c22.056,0,40,17.944,40,40c0,22.056-17.944,40-40,40c-11.046,0-20,8.954-20,20v50c0,11.046,8.954,20,20,20,c11.046,0,20-8.954,20-20v-32.531c34.466-8.903,60-40.26,60-77.469C336,164.388,300.112,128.5,256,128.5z' /> </g> </g> </g> </svg> </span></label><button class='psar-button-login' id='psar-button-first' onclick='return order_operation_a()' style='margin-bottom:10px;'>Return Items</button></form></div><div id='psar_errors_step2'></div><div id='psar_step2' class='psar_step2' style=''><div class='psar_table-wrap psar_table-wrap--order'><form name='psar_order_form_b' id='psar_order_form_b'><table class='psar_order-table'><thead><tr><th scope='col' class='psar_text-left_th'>'#'</th><th scope='col' class='psar_text-left_th'>Product</th><th scope='col' class='psar_text-left_th'>SKU</th><th class='psar_text-right' scope='col'>Quantity</th><th class='psar_text-right' scope='col'>Price</th></tr></thead><tbody id='psar_line_items_wrapper'><tfoot><tr><td></td><td></td><td></td><td></td><td> <button class='psar-button-login' onclick='checkSelect()' style='margin-bottom:10px;'>Submit</button></td></tr></tfoot></table></form></div></div><div id='psar_step3' class='psar_step3' style='display:block !important'></div></div>{% else %}<div id='CustomerLoginForm' class='form-vertical'> {% form 'customer_login' %} {{ form.errors | default_errors }} <label for='CustomerEmail' class='hidden-label'>Email</label> <input type='email' name='customer[email]' id='CustomerEmail' class='input-full{% if form.errors contains 'email' %} error{% endif %}' placeholder='Email' autocorrect='off' autocapitalize='off' autofocus> {% if form.password_needed %} <label for='CustomerPassword' class='hidden-label'>Password</label> <input type='password' value="" name='customer[password]' id='CustomerPassword' class='input-full{% if form.errors contains 'password' %} error{% endif %}' placeholder='Password'> {% endif %} <input type='hidden' name='return_to' value='/pages/psar_return'><p> <input type='submit' class='btn btn--full' value='Sign In'></p> {% endform %}</div> {% endif %}</div></div></div></div>"
            }
        }

        r = requests.put(url=url, headers=header, json=data)
        
        if r.status_code == 200:
            c = json.loads(r.text)
            return c
        else:
            c = ''
            return c

    @staticmethod
    def create_status(theme_id, store, token):
        url = 'https://%s/admin/api/%s/themes/%s/assets.json' % (store, API_VERSION, theme_id)

        header = {
            'X-Shopify-Access-Token': token,
            'Content-Type': 'application/json',
            'client_id': API_KEY,
            'client_secret': SHARED_SECRET
        } 

        data = {
            'asset': {
                'key': 'templates/page.psar_return_status.liquid',
                'value': '<header class="section-header text-center"><h1>{{ page.title }}</h1> </header><div class="grid"><div class="grid__item large--four-fifths push--large--one-tenth"><div class="rte rte--nomargin rte--indented-images"> {% if customer %}<div class="table-wrap" style="display:block; width:50%;box-shadow:1px 5px 6px 4px #ccc;background: #f6f6f6; margin:0 auto;" id="psar_step"><form data-customer="{{ customer.id }}" name="psar_order_form_c" id="psar_order_form_c"><table class="full table--responsive"><thead><tr><th style="font-size:10px">Order</th><th style="font-size:10px">Requested Date</th><th style="font-size:10px">Updated Date</th><th style="font-size:10px">Fulfillment Status</th></tr></thead><tbody id="psar_table_view">&nbsp;</tbody></table></form></div> {% else %}<div id="CustomerLoginForm" class="form-vertical"> {% form "customer_login" %} {{ form.errors | default_errors }} <label for="CustomerEmail" class="hidden-label">Email</label> <input type="email" name="customer[email]" id="CustomerEmail" class="input-full{% if form.errors contains "email" %} error{% endif %}" placeholder="Email" autocorrect="off" autocapitalize="off" autofocus> {% if form.password_needed %} <label for="CustomerPassword" class="hidden-label">Password</label> <input type="password" value="" name="customer[password]" id="CustomerPassword" class="input-full{% if form.errors contains "password" %} error{% endif %}" placeholder="Password"> {% endif %} <input type="hidden" name="return_to" value="/pages/psar_return_request"><p> <input type="submit" class="btn btn--full" value="Sign In"></p> {% endform %}</div> {% endif %}</div></div></div>'
            }
        }

        r = requests.put(url=url, headers=header, json=data)
       
        if r.status_code == 200:
            c = json.loads(r.text)
            return c
        else:
            c = ''
            return c

    @staticmethod
    def create_css(theme_id, store, token):
        url = 'https://%s/admin/api/%s/themes/%s/assets.json' % (store, API_VERSION, theme_id)

        header = {
            'X-Shopify-Access-Token': token,
            'Content-Type': 'application/json',
            'client_id': API_KEY,
            'client_secret': SHARED_SECRET
        } 

        data = {
            'asset': {
                'key': 'assets/psar-style.css',
                "src": "https://python.penveel.com/static/css/psar-style.css"
            }
        }

        r = requests.put(url=url, headers=header, json=data)
       
        if r.status_code == 200:
            c = json.loads(r.text)
            return c
        else:
            c = ''
            return c

    @staticmethod
    def create_sjs(theme_id, store, token):
        url = 'https://%s/admin/api/%s/themes/%s/assets.json' % (store, API_VERSION, theme_id)

        header = {
            'X-Shopify-Access-Token': token,
            'Content-Type': 'application/json',
            'client_id': API_KEY,
            'client_secret': SHARED_SECRET
        } 

        data = {
            'asset': {
                'key': 'assets/psar_request.js',
                # "src": "https://python.penveel.com/static/js/psar_request.js"
                "src": "https://python.penveel.com/static/js/psar_request_local.js"
            }
        }

        r = requests.put(url=url, headers=header, json=data)
       
        if r.status_code == 200:
            c = json.loads(r.text)
            return c
        else:
            c = ''
            return c


class Page:

    @staticmethod
    def create_return_request_page(store, token):
        url = "https://%s/admin/api/%s/pages.json" % (store, API_VERSION)

        header = {
            'X-Shopify-Access-Token': token,
            'Content-Type': 'application/json',
            'client_id': API_KEY,
            'client_secret': SHARED_SECRET
        } 

        my_data = {
            "page": {
                "title": "Return requests",
                "template_suffix": "psar_return_request",
                "published": True
            }
        }

        r = requests.post(url=url, headers=header, json=my_data)
        print(r.status_code)
        if r.status_code == 201:
            c = json.loads(r.text)
            return c
        else:
            c = ''
            return c

    @staticmethod
    def create_return_status_page(store, token):
        url = "https://%s/admin/api/%s/pages.json" % (store, API_VERSION)

        header = {
            'X-Shopify-Access-Token': token,
            'Content-Type': 'application/json',
            'client_id': API_KEY,
            'client_secret': SHARED_SECRET
        } 

        my_data = {
            "page": {
                "title": "Return status",
                "template_suffix": "psar_return_status",
                "published": True
            }
        }

        r = requests.post(url=url, headers=header, json=my_data)
        print(r.status_code)
        if r.status_code == 201:
            c = json.loads(r.text)
            return c
        else:
            c = ''
            return c

class ScriptTags:

    # @staticmethod
    # def Create_ScriptTags_scss(store, token):
    #     url = "https://%s/admin/api/%s/script_tags.json" %(store, API_VERSION)
    
    #     header = {
    #         'X-Shopify-Access-Token': token,
    #         'Content-Type': 'application/json',
    #         'client_id': API_KEY,
    #         'client_secret': SHARED_SECRET
    #     } 

    #     script_data = {
    #         "script_tag": {
    #             "event": "onload",
    #             "src": "https://python.penveel.com/static/css/psar-style.css"
    #         }
    #     }

    #     r = requests.post(url=url, headers=header, json=script_data)
        
    #     if r.status_code == 201:
    #         c = json.loads(r.text)
    #         return c
    #     else:
    #         c = ''
    #         return c

    @staticmethod
    def Create_ScriptTags_js(store, token):
        url = "https://%s/admin/api/%s/script_tags.json" %(store, API_VERSION)

        header = {
            'X-Shopify-Access-Token': token,
            'Content-Type': 'application/json',
            'client_id': API_KEY,
            'client_secret': SHARED_SECRET
        } 

        script_data = {
            "script_tag": {
                "event": "onload",
                # "src": "https://python.penveel.com/static/js/psar_request.js"
                "src": "https://python.penveel.com/static/js/psar_request_local.js"
            }
        }

        r = requests.post(url=url, headers=header, json=script_data)
        if r.status_code == 201:
            c = json.loads(r.text)
            return c
        else:
            c = ''
            return c

