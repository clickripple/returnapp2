from django_cron import CronJobBase, Schedule
from django.conf.urls.static import settings

class MyCronJob(CronJobBase):
    RUN_EVERY_MINS = 1 if settings.DEBUG else 1   # 6 hours when not DEBUG

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'cron.MyCronJob'    # a unique code

    def do(self):
        installed_date = ''
        from .models import Counter_Shop_Detail
        from .datecontroller import DateControl

        counter_data_detail = Counter_Shop_Detail.objects.all()

        for x in counter_data_detail:
            installed_date = x.reset_date

            year, month, day, hour, minute, second, milisecond = DateControl.date_after_input(user_date=installed_date)

            days = DateControl.get_days(int(year), int(month), int(day), int(hour), int(minute), int(second), int(milisecond))

            expire_date = DateControl.get_before_date(int(year), int(month), int(day), int(hour), int(minute), int(second), int(milisecond))
            if days >= 30:
                shop_id = x.store_id_id
                Counter_Shop_Detail.objects.filter(store_id=shop_id).update(counter=0, reset_date=expire_date)
            else:
                pass