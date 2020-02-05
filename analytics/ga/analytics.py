import httplib2
import json
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials as SC
from settings.models import StripeSetting
from Aartcy.utils import today,week,delta,percentage,DataNotImported,last_month

VERSION = 'v4'
DISCOVERY_URI = ('https://analyticsreporting.googleapis.com/$discovery/rest')
scopes = 'https://www.googleapis.com/auth/analytics.readonly'

try:
    secret_json = json.loads(StripeSetting.objects.get(name='SJ').value())
    viewId = StripeSetting.objects.get(name='VI').value()
except StripeSetting.DoesNotExist:
    print('Run : python manage.py importstripesettings')


class GoogleAnalytics:

    def connection(self):

        credentials = SC._from_parsed_json_keyfile(secret_json,scopes)
        return credentials

    def authorize(self):

        http = self.connection().authorize(httplib2.Http())
        analytics = build('analytics', VERSION, http=http, discoveryServiceUrl=DISCOVERY_URI)
        return analytics.reports()

    def _generate_report(self,body):
        if not body:
            return {}
        return self.authorize().batchGet(body=body).execute()

    def today_site_visits(self):

        yesterday = str(delta(today(),1))
        _week = str(week().date())
        _today = str(today().date())

        body =    {
            'reportRequests': [
                {
                    'viewId': viewId,

                    'dateRanges': [
                        {
                            'startDate': yesterday,
                            'endDate': _today,
                        },
                        {
                            'startDate': _week,
                            'endDate': yesterday,
                        },
                    ],

                    'metrics': [
                        {'expression': 'ga:newUsers'},
                        {'expression': 'ga:newUsers'}
                    ],
                }]
        }

        data = self._generate_report(body)
        today_visits = int(data['reports'][0]['data']['totals'][0]['values'][0])
        seven_days_visits = int(data['reports'][0]['data']['totals'][1]['values'][1])
        _p = percentage(today_visits,seven_days_visits)
        return {'today_site_visits':today_visits,'percentage':_p}

    def weekly_traffic(self):
        last_month_start = str(last_month(1).date())
        last_month_end = str(last_month().date())
        # last_month = str(delta(today(), 1))
        last_week = str(week().date())
        _today = str(today().date())

        monthly_body = {
            'reportRequests': [
                {
                    'viewId': viewId,

                    'dateRanges': [
                        {
                            'startDate': last_month_start,
                            'endDate': last_month_end,
                        },  # 0
                        {
                            'startDate': last_week,
                            'endDate': _today,
                        }, #1
                    ],

                    'metrics': [
                        {'expression': 'ga:Users'},
                        {'expression': 'ga:Users'},

                    ],
                }]
        }
        monthly_data = self._generate_report(monthly_body)
        monthly_visits = int(monthly_data['reports'][0]['data']['totals'][0]['values'][0])
        weekly_visits = int(monthly_data['reports'][0]['data']['totals'][1]['values'][1])

        ranges = self.make_range(today(), 7)
        ranged_data = self.ranged_data(ranges)
        ranged_data = self.cool_data(ranged_data)
        return {'monthly_visits':monthly_visits,'weekly_visits':weekly_visits,'weekly_data':ranged_data,'daily_avg':round(weekly_visits/7)}


    def cool_data(self,data):
        final_data = []
        for i in data:
            final_data.append({'label':list(i.keys())[0],'value':list(i.values())[0]})
        return final_data

    def make_range(self,date,_from):
        ranges = []
        for i in reversed(range(_from)):
            start = str(delta(date,i+1))
            end = str(delta(date,i))
            _range = { 'startDate': start, 'endDate': end,}
            ranges.append(_range)

        return ranges


    def ranged_data(self,ranges):
        data = []
        for i,d in zip(ranges,self.make_range(today(), 7)):
            body = {
                'reportRequests': [
                    {
                        'viewId': viewId,

                        'dateRanges': [
                            {
                                'startDate': i['startDate'],
                                'endDate': i['endDate'],
                            },
                        ],

                        'metrics': [
                            {'expression': 'ga:Users'},

                        ],
                    }]
            }

            body_data = self._generate_report(body)
            value = int(body_data['reports'][0]['data']['totals'][0]['values'][0])
            _dict = {d['endDate']:value}
            data.append(_dict)

        return data
