import falcon
import json
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Document, Date, Integer, Keyword, Text, GeoPoint, Ip, aggs, Q, A, Search
from datetime import datetime, timedelta
from pytz import timezone
import os


class Abuse_report:

    _tz = timezone('Europe/Paris')
    _params = {
            'scan_interval_minutes': 60,
            'aggr_size': 100,
            'max_success_ratio':  0.1,
            'min_calls': 100,
            'dt_start': None,   
            'dt_end': None,
            'es_scheme': 'https',
            'es_host': os.environ.get('ES_HOST'),
            'es_port': os.environ.get('ES_PORT'),
            'es_user': os.environ.get('ES_USER'),
            'es_pwd': os.environ.get('ES_PASSWORD'),
            'es_index': os.environ.get('ES_INDEX')
        }
    
    __es_client: None
    __query_jobs: None

    def __init__(self) -> None:
        pass

    def init_time_frame(self) -> None:
        if self._params['dt_end'] is None:
                self._params['dt_end'] = datetime.now().astimezone(self._tz)

        if self._params['dt_start'] == None:
            dt = self._params['dt_end'].astimezone(self._tz)
            self._params['dt_start'] = dt.replace(minute=0, hour=0, second=0)

    def create_jobs(self):
        job_start = job_end = self._params['dt_start']
        jobs = []
        job_id = 0
        while job_end != self._params['dt_end']:
            job_end = job_start + timedelta(minutes=self._params['scan_interval_minutes'])
            if job_end > self._params['dt_end']:
                job_end = self._params['dt_end']
            job_id = job_id + 1
            jobs.append({'job_id': job_id, 'start': job_start, 'end': job_end})
            job_start = job_end
        self.__query_jobs = jobs

    
    def connect_es(self):
        client = Elasticsearch(
        hosts=['{0}://{1}:{2}@{3}:{4}'.format(self._params['es_scheme'], self._params['es_user'], self._params['es_pwd'], self._params['es_host'], self._params['es_port'])],
        verify_certs=None,
        basic_auth=(self._params['es_user'], self._params['es_pwd'])
        )
        self.__es_client = client

    def disconnect_es(self):
        self.__es_client.close()

    def get_top_talkers( self, method: str, start: datetime, end: datetime ):
        query = Search(using=self.__es_client,index=self._params['es_index'])\
            .filter('range', **{'@timestamp': {'gte': round(start.timestamp()*1000) , 'lt': round(end.timestamp()*1000) ,'format' : 'epoch_millis'}} ) \
            .query('match', event__api_method=method)

        tot_by_ip = A('terms', field='event.webedia_x_forwarded_for.keyword', size=self._params['aggr_size'])
        query.aggs.bucket('tot_by_ip', tot_by_ip)

        sub_by_exit_code = A('terms', field='event.exit_code', size=5)
        query.aggs['tot_by_ip'].bucket('exit_code', sub_by_exit_code)

        # print(json.dumps(query.to_dict(), indent=2, default=str))
        res = query.execute()
        # print(json.dumps(res.aggregations.tot_by_ip.buckets, indent=2, default=str))
        ans = []
        for i in res.aggregations.tot_by_ip.buckets:
            success = 0
            fails =0
            for x in i.exit_code:
                if x.key == 0:
                    success = x.doc_count
                else:
                    fails += x.doc_count
            success_ratio = round(success/i.doc_count,3)
            if i.doc_count>= self._params['min_calls'] and success_ratio <= self._params['max_success_ratio'] and success>0 :
                ans.append({'client_ip': i.key, 'total': i.doc_count, 'success': success, 'fails': fails, 'success_ratio': success_ratio})
        return ans
    
    def get_hacked_emails(self, start: datetime, end: datetime, offending_ip):
        query = Search(using=self.__es_client,index=self._params['es_index'])\
        .filter('range', **{'@timestamp': {'gte': round(start.timestamp()*1000) , 'lt': round(end.timestamp()*1000) ,'format' : 'epoch_millis'}} )\
        .query('match', event__api_method="GetMember")\
        .query('match', event__webedia_x_forwarded_for=offending_ip)
        res = query.execute()
        emails = []
        for x in res:
            try: # in case email field is missing from document
                if x.event.email not in emails: 
                    emails.append( x.event.email)
            except:
                pass
        return(emails)


    def on_get(self, req, resp):
        
        try:
            self._params['scan_interval_minutes'] = int(req.params['interval_size_minutes'])
        except:
            pass

        try:
            self._params['aggr_size'] = int(req.params['top_count'])
        except:
            pass

        try:
            self._params['max_success_ratio'] = float(req.params['max_success_ratio'])
        except:
            pass

        try:
            self._params['min_calls'] = int(req.params['hit_threshold'])
        except:
            pass

        try:
            self._params['dt_start'] = datetime.fromtimestamp(int(req.params['start'])).astimezone(self._tz)
        except:
            pass

        try:
            self._params['dt_end'] = datetime.fromtimestamp(int(req.params['stop'])).astimezone(self._tz)
        except:
            pass

        # self._params['dt_start'] = datetime.fromisoformat('2023-04-17 00:00:00')
        self.init_time_frame()
        self.create_jobs()

        self.connect_es()
        compromised_accounts = []
        ip_adresses = []
        for j in self.__query_jobs:
            ans = self.get_top_talkers('Login',j['start'], j['end'])
            for x in ans:
                emails = self.get_hacked_emails(j['start'], j['end'],x['client_ip'])
                x.update({ 'accounts_email': emails})
                compromised_accounts += emails
                ip_adresses.append(x['client_ip'])
            j.update( { 'result': ans})
        self.disconnect_es()

        # dedup account emails
        compromised_accounts = list( dict.fromkeys(compromised_accounts) )

        # build report
        report = {}
        report_params = {
            'hit_count_treshold': self._params['min_calls'],
            'max_success_ratio': self._params['max_success_ratio'],
            'top_count': self._params['aggr_size'],
            'interval_size_minutes': self._params['scan_interval_minutes']
        }
        report.update({ 'search_start': self._params['dt_start']})
        report.update({ 'search_end': self._params['dt_end']})
        report.update({ 'search_params': report_params})
        report.update({ 'email_summary': compromised_accounts})
        report.update({ 'ip_addresses_summary': ip_adresses})
        report.update({ 'intervals': self.__query_jobs})


        # make answer
        resp.text = json.dumps( report, indent=2, default=str)
        resp.status = falcon.HTTP_200
        resp.content_type = falcon.MEDIA_JSON