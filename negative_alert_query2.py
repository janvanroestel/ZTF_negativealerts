'''
Query Kowalski for alerts that could be cataclysmic variables
'''

import os
import json
import time
import datetime
import pandas as pd
import numpy as np
from bson.json_util import dumps, loads 
from penquins import Kowalski
from astropy.time import Time




def make_queries(field,stepsize=100):
    """ make the queries"""
    
    # define the projection; the fields to get from the database
    projection = {"objectId": 1,
                  "candidate.rcid": 1,
                  "candidate.field": 1,
                  "candidate.ra": 1,
                  "candidate.dec": 1,
                  "candidate.jd": 1,
                  "candidate.ndethist": 1,
                  "candidate.jdstarthist": 1,
                  "candidate.jdendhist": 1,
                  "candidate.magpsf": 1,
                  "candidate.sigmapsf": 1,
                  "candidate.fid": 1,
                  "candidate.programid": 1,
                  "candidate.isdiffpos": 1,
                  "candidate.ssdistnr": 1,
                  "candidate.rb": 1,
                  "candidate.drb": 1,
                  "candidate.classtar": 1,
                  "candidate.distnr": 1,   
                  "candidate.nbad": 1,   
                  "candidate.magnr": 1,   
                  "candidate.distpsnr1": 1,   
                  "candidate.sgscore1": 1,
                  "candidate.sgmag1": 1,
                  "candidate.srmag1": 1,
                  "candidate.simag1": 1,
                  "candidate.szmag1": 1,
                  }

    # define the filters
    basefilter = {'candidate.field': int(field), 
                  #'$or': [{'classifications.braai': {'$gt': 0.9}}, {'candidate.drb': {'$gt': 0.9} }],
                  'candidate.drb': {'$gt': 0.9},
                  'candidate.distnr': {'$gt': 1.5},
                  'candidate.isdiffpos': {'$in': ['f','0']},
                  '$expr': { "$and" : [{'$not': [{'$and': [{'$lt': ['$candidate.distpsnr1',5]},
                                                 {'$lt': ['$candidate.srmag1',17]}] }]},
                                       {'$not': [{'$and': [{'$lt': ['$candidate.distpsnr2',5]},
                                                 {'$lt': ['$candidate.srmag2',17]}] }]},
                                       {'$not': [{'$and': [{'$lt': ['$candidate.distpsnr3',5]},
                                                 {'$lt': ['$candidate.srmag3',17]}] }]},
                                       {'$not': [{'$and': [{'$lt': ['$candidate.distpsnr1',60]},
                                                 {'$lt': ['$candidate.sgscore1',0.5]}] }]},
                                       {'$not': [{'$and': [{'$lt': ['$candidate.distpsnr2',60]},
                                                 {'$lt': ['$candidate.sgscore1',0.5]}] }]},
                                       {'$not': [{'$and': [{'$lt': ['$candidate.distpsnr3',60]},
                                                 {'$lt': ['$candidate.sgscore1',0.5]}] }]},]}

                 }


    # add the basefilter to 
    jdstart = 2458194.5 # official ZTF start jd
    jdend =   2459694.5+10 # current jd
    steps = int((jdend-jdstart)/stepsize)+1
    print("%d steps" %steps)
    
    alertfilters = [{**{'candidate.jd': {'$gte': jdstart+stepsize*n, '$lt': jdstart+stepsize*(n+1)}},**basefilter} for n in np.arange(steps)]


    
    #print(alertfilters)

    # actually make the queries
    qs = list([])
    for alertfilter in alertfilters:
        q = {"query_type": "find",
             "query": {
                 "catalog": "ZTF_alerts",
                 "filter": alertfilter,
                 "projection": projection,
                 },
                 "kwargs": {
                     "hint": "jd_field_rb_drb_braai_ndethhist_magpsf_isdiffpos",
                     "max_time_ms": 10000000
                 }
                 }

        # append the filter to list of filters
        qs.append(q)

    return qs



def get_alertdata(q,k):
    """ run an alertquery and put the result in a df
    """
    
    # get data
    print('starting query')
    print(q)
    r = k.query(query=q)
    print(r)
    data = r.get('data')

    # combine into a single dataframe
    output = pd.concat([
        pd.DataFrame([d['objectId'] for d in data],columns=['objectId',]),
        pd.DataFrame([d['candidate'] for d in data]) ],axis=1)
       
    return output



def run_CVqueries(k,field):
    """ run all queries, combine the results, and do some cleaning
    """

    # make the queries
    qs = make_queries(field)

    # run queries
    dfs = [get_alertdata(q,k) for q in qs]
    output = pd.concat(dfs,ignore_index=True)

    # clean
    output.replace(-999.0,np.nan,inplace=True)

    return output


if __name__ == "__main__":
    import argparse
    import os

    parser = argparse.ArgumentParser(description='Download candidates by field')
    parser.add_argument('-o', action='store_true')
    args = parser.parse_args()

    # savedir
    savedir = "./queries2"

    # make a directory to store the query results
    os.system("mkdir -p %s" %savedir)

    # login details
    with open('secrets.json', 'r') as f:
        secrets = json.load(f)

    # setup the connection to the kowalski database
    k = Kowalski(**secrets['kowalski'], verbose=False)

    # 
    fields = np.r_[np.arange(244,880)[::-1],np.arange(1240,1895)[::-1]]

    for f in fields:
        outname = "%s/query_fid%0.4d.csv" %(savedir,f)
        # skip if file is there and no overwrite
        if not args.o and os.path.exists(outname):
            print('Skipping field %d' %f)
            continue
        print('Query field %d' %f)

        output = run_CVqueries(k,f)
        output.to_csv(outname,index=False)


