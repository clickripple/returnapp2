from datetime import datetime, timedelta


class DateControl:
    @staticmethod
    def date_after_input(user_date):
        u_d = str(user_date)

        u_da = u_d.split('+')

        u_date = u_da[0]
        print(u_date, "datecontroller")
        date, time = u_date.split(' ')

        year, month, day = date.split('-')

        hour, minute, second_data = time.split(':')

        second, milisecond = second_data.split('.')
        
        return year, month, day, hour, minute, second, milisecond

    @staticmethod
    def get_before_date(year, month, day, hour, minute, second, milisecond):
        user_date_input = datetime(year, month, day, hour, minute, second, milisecond)

        print(user_date_input)

        before_date = (user_date_input + timedelta(days=30))

        return before_date

    @staticmethod
    def get_days(year, month, day, hour, minute, second, milisecond):
        user_date_input = datetime(year, month, day, hour, minute, second, milisecond)

        delta = datetime.now() - user_date_input

        return delta.days
