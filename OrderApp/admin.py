from django.contrib import admin
from .models import about_data, Policy_data, Homedata, thank_you, data_admin, plan
from django_dynamic_resource_admin.admin import DjangoDynamicResourceAdmin
from django.views.decorators.csrf import csrf_exempt
import django.contrib.admin.options as admin_opt


# plan #
admin.site.register(plan)
# end plan #

# SuperAdmin about page code start (To add data in about page) #
admin.site.register(about_data)
# SuperAdmin about page code end #

# SuperAdmin Privacy_policy page code start (To add data in privacy_policy page) #
admin.site.register(Policy_data)
# SuperAdmin Privacy_policy page code end #

# SuperAdmin Home page code start (To add data in Home page) #
admin.site.register(Homedata)
# SuperAdmin Home page code end #

# SuperAdmin ThankYou page code start (to add, update and delete data of superadmin thankyou page) #
class MyObjAdmin(admin.ModelAdmin):
    list_display = ('id', 'emaildata', 'address', 'Imageurl', 'Desctiption_data')
    list_filter = ('emaildata',)
    search_fields = ('emaildata',)
    ordering = ['id']    

admin.site.register(data_admin, MyObjAdmin)
# SuperAdmin ThankYou page code end #