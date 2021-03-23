from django import template
from django.contrib.auth.models import Group

register = template.Library()

# Template variable create code start (templatetag for create variable) #
@register.simple_tag
def setvar(val=None):   
  return val
# Template variable create code end #

# Template indexing code start (templatetag for indexing) #
@register.filter
def get_at_index(list, index):
  if len(list) > index:
      gotdata = list[index]
  else: 
      gotdata = 0
  return gotdata
# Template indexing code end #

# Template customer reason code start (templatetag for gether customer return reason by variant) #
@register.filter
def get_product_by_variant(variant, oid):
  from django.db.models import Q
  from OrderApp.models import requested_variant
  variant_reason = ''
  data_request = requested_variant.objects.filter(Q(variants=str(variant)), Q(detail_order_id_id=str(oid)))
  if data_request:
    variant_reason = data_request[0].order_reason
  return variant_reason
# Template customer reason code end #

# Template vendor reason code start (templatetag for gether vendor reason of return request by variant) #
@register.filter
def get_note_by_variant(variant, oid):
  from django.db.models import Q
  from OrderApp.models import requested_variant
  variant_reason = ''
  data_request = requested_variant.objects.filter(Q(variants=str(variant)), Q(detail_order_id_id=str(oid)))
  if data_request:
    variant_reason = data_request[0].order_note
  return variant_reason
# Template vendor reason code end #

# Template status code start (templatetag for gether each variant status) #
@register.filter
def get_status_by_variant(variant, oid):
  from django.db.models import Q
  from OrderApp.models import requested_variant
  variant_reason = ''
  data_request = requested_variant.objects.filter(Q(variants=str(variant)), Q(detail_order_id_id=str(oid)))
  if data_request:
    variant_status = data_request[0].r_status
  return variant_status
# Template status code start #
