#!/usr/bin/env python3

########################################################################
# A python script to retrieve compromised accounts in leclub api using #
#   sentinel api for scoring                                           #
########################################################################

import requests, json, time, argparse, simplejson
from datetime import datetime, timedelta
from pytz import timezone 

# some vars to configure script
tz = timezone('Europe/Paris')
api_url = 'http://sentinel.service.leclub'
dt_start = datetime.now().astimezone(tz)
dt_start = dt_start.replace(hour=0,minute=0,second=0,microsecond=0)

# command line parameters parsing
parser = argparse.ArgumentParser(description="Report aggreagation", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("--start", action="store", help="start date", default=dt_start, required=True)
parser.add_argument("--end", action="store", help="end date", default=dt_start, required=True)
parser.add_argument("--interval",action="store", help="analyse intervals in minutes", required=False, default=60)
parser.add_argument("--hit-count",action="store", help="minimum hits per ip during interval", default=100)
parser.add_argument("--success-ratio",action="store", help="maximum success ratio per ip", default=0.1)
parser.add_argument("--aggr-count",action="store", help="max number of ip addresses returned per interval", default=100)
parser.add_argument("--out",action="store", help="file do store the json result",required=True)
args = parser.parse_args()

# Sanitize inputs
def _init_dates(start: datetime, end: datetime) -> None:
    try: 
        dt_start = datetime.strptime(args.start, '%Y-%m-%d').astimezone(tz)
        dt_end = datetime.strptime(args.end, '%Y-%m-%d').astimezone(tz)
    except:
        print("\nERROR: Incorrect date format, date must be in the following format: '{}'".format(datetime.now().date()))
        exit(1)

    if dt_start > dt_end:
        print("\nERROR: Start date must be lower than end date")
        exit(1)

    dt_end = dt_end.replace(hour=23,minute=59,second=59)
    return dt_start,dt_end

# split start/end interval in days, one job for one day
def _create_jobs(start: datetime,end: datetime ) -> list[dict[str,str]]:
    
    jobs = []
    while start<= end:
        end_job = start.replace(hour=23,minute=59,second=59)
        jobs.append({'start': start, 'end': end_job})
        start = start + timedelta(days=1)
        if start.date()>end.date():
            break
    return jobs

# query sentinel api
def process_job( job: dict[str,datetime]) -> json:
    # forge api request with endpoint 'abuse'
    request = """{0}/abuse?
        interval_size_minutes={1}
        &top_count={2}
        &max_success_ratio={3}
        &hit_threshold={4}
        &start={5}
        &stop={6}
        """.format( api_url,
                args.interval,
                args.aggr_count,
                args.success_ratio,
                args.hit_count,
                int(round(datetime.timestamp(job['start']))),
                int(round(datetime.timestamp(job['end'])))
        )
    try:
        response = requests.get(request).text
        return True,json.loads(response)
    except:
        print("ERROR: Error encountered while making request to {}. Exiting.".format(api_url))
        exit(1)

# write json output to file
def write_output_file( outfile: str, data: json):
    output = open(outfile, "w")
    output.write(simplejson.dumps(simplejson.loads(json.dumps(data)), indent=4, sort_keys=False))
    output.close()

if __name__ == "__main__":
    print('Checking input...')
    start,stop = _init_dates(args.start, args.end)
    print('Creating search jobs...')
    jobs = _create_jobs(start, stop)
    # collect compromised accounts on a daily basis
    print('Collecting data...')
    report = {}
    report.update({'settings': 
                   {'start': start.strftime('%Y-%m-%d'),
                    'end': stop.strftime('%Y-%m-%d'),
                    'interval': args.interval , 
                    'min_hit_count': args.hit_count, 
                    'max_login_success_ratio': args.success_ratio,
                    'aggregation_size:': args.aggr_count}})
    emails = []
    run_start = time.time()
    for job in jobs:
        res, data = process_job(job)
        if res:
            emails = emails + data['email_summary']
    print( "Done. Elapsed time: {} seconds.".format(round(time.time()-run_start,2)))
    report.update({ 'summary': { 
        'elapsed_time_seconds': round(time.time()-run_start,2),
        'matched_email_addresses': len(emails)
        }})
    report.update({'emails': emails})
    # Save result to file 
    write_output_file( args.out, report)
