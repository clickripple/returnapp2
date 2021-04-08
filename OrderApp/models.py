from django.db import models
from django.db.models import Q
from datetime import datetime


# Create your models here.
class installer(models.Model):  # installer table #
    hmac = models.CharField(max_length=2000)
    shop = models.CharField(max_length=2000)
    code = models.CharField(max_length=2000)
    access_token = models.CharField(max_length=2000)
    install_date = models.DateTimeField(default=datetime.now())

class Homedata(models.Model):   # Homedata table #
    Desctiption = models.CharField(max_length=5000)

class about_data(models.Model): # about_data table #
    title = models.CharField(max_length=1000)
    description = models.CharField(max_length=5000)

class Policy_data(models.Model):     # Policy_data table #
    policy_title = models.CharField(max_length=1000)
    policy_description = models.CharField(max_length=5000)

class detail_order(models.Model):       # detail_order table #
    shop_data = models.CharField(max_length=1000)
    variants = models.CharField(max_length=5000)
    quantity = models.CharField(max_length=1000)
    order_id = models.CharField(max_length=1000)
    ordid = models.CharField(max_length=100)
    order_fulfill_status = models.CharField(max_length=500)
    order_total = models.CharField(max_length=500)
    status = models.CharField(max_length=1000)
    order_reason = models.TextField(max_length=2500, blank=True)
    order_note = models.TextField(max_length=2500, blank=True)
    crea_date = models.DateTimeField(default=datetime.now())                          # change CharField to DateTimeFiled #
    upda_date = models.DateTimeField(default=datetime.now())                  # change CharField to DateTimeFiled #
    tquant = models.CharField(max_length=20)
    custom_id = models.CharField(max_length=20)

class requested_variant(models.Model):  # requested_variant table #
    variants = models.CharField(max_length=5000)
    quantity = models.CharField(max_length=1000)
    varaint_shop = models.CharField(max_length=5000)
    status = models.CharField(max_length=1000)
    order_number = models.CharField(max_length=100, default='')
    order_reason = models.TextField(max_length=2500, null=True)
    order_note = models.TextField(max_length=2500, null=True)
    crea_date = models.DateTimeField(default=datetime.now())                       # change CharField to DateTimeFiled #
    upda_date = models.DateTimeField(default=datetime.now())                 # change CharField to DateTimeFiled #
    cust_id = models.CharField(max_length=100, default='')
    r_status = models.CharField(max_length=500, null=True)
    detail_order_id = models.ForeignKey(detail_order, on_delete=models.CASCADE)

class uninstall_data(models.Model):     # uninstall_data table #
    uninstall_shop = models.CharField(max_length=500)
    uninstall_time = models.CharField(max_length=200)
    uninstall_log = models.CharField(max_length=3000)

class thank_you(models.Model):      # thank_you table #
    shop_name = models.CharField(max_length=500)
    logo_upload = models.CharField(max_length=1000)
    email_id = models.CharField(max_length=500)
    ven_address = models.CharField(max_length=700) 

class DataAdminQuerySet(models.QuerySet):       # DataAdminQuerySet queryset for DataAdminManager #
    def get_datas(self, emaildata, address, Imageurl, Desctiption_data):
        return self.filter(Q(emaildata=emaildata), Q(address=address), Q(Imageurl=Imageurl), Q(Desctiption_data=Desctiption_data))

class DataAdminManager(models.Manager):     # DataAdminManager for data_admin #
    def get_queryset(self):
        return DataAdminQuerySet(self.model, using=self._db)

    def datas(self, emaildata, address, Imageurl, Desctiption_data):
        return self.get_datas().datas(emaildata, address, Imageurl, Desctiption_data)

class data_admin(models.Model):     # data_admin table #
    Imageurl = models.FileField(upload_to='images')
    emaildata = models.CharField(max_length=1000)
    address = models.CharField(max_length=5000)
    Desctiption_data =  models.TextField() 

    objects = DataAdminManager()

    def __str__(self):
        return self.emaildata


# store shop requested data #
class PerMonth_Charges(models.Model):
    store_nanme = models.CharField(max_length=500)
    entry_date = models.DateTimeField(default=datetime.now())
    reference_id =  models.ForeignKey(detail_order, on_delete=models.CASCADE)

# store applications plan #
class plan(models.Model):           # plan detail #
    plan_name = models.CharField(max_length=350)
    month_Rent = models.FloatField()
    shipment_price = models.FloatField()
    descriptions = models.TextField()

class Relations_Plan_Shop(models.Model):    # plan shop relation table #
    shop_id = models.ForeignKey(installer, on_delete=models.CASCADE)
    plan_id = models.ForeignKey(plan, on_delete=models.CASCADE)
    entry_date = models.DateTimeField(default=datetime.now())

class plan_charges(models.Model):       # charges table #
    shop_id = models.ForeignKey(installer, on_delete=models.CASCADE)
    application_charge_id = models.CharField(max_length=50)
    price = models.FloatField()
    status = models.CharField(max_length=150)
    confirmation_url = models.CharField(max_length=2000)
    plan_id = models.ForeignKey(plan, on_delete=models.CASCADE)

class Relation_Store_Charges(models.Model):   # store charge relation table #
    shop_id = models.ForeignKey(installer, on_delete=models.CASCADE)
    plan_charges_id = models.ForeignKey(plan_charges, on_delete=models.CASCADE)

class Counter_Shop_Detail(models.Model):
    store_id = models.ForeignKey(installer, on_delete=models.CASCADE)
    counter = models.IntegerField()
    reset_date = models.DateTimeField()