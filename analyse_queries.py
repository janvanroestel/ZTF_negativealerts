import pandas as pd
import numpy as np
import glob
import matplotlib.pyplot as plt


# load the files and combine
files = glob.glob("queries1/*.csv")
data = pd.concat([pd.read_csv(f) for f in files])

WDRDs = pd.read_csv("WDRD_IDs.txt",names=['ids','ra','dec'],delim_whitespace=True)

# sort by time
data.sort_values('jd',inplace=True)

data['WDRD'] = np.isin(data['objectId'],WDRDs['ids'])


# calculate some addition numbers
data['ratio'] = (10**(-0.4*data['magnr']) - 10**(-0.4*data['magpsf']) ) / (10**(-0.4*data['magnr']))
data['noflux_1s'] = ((data['magnr'] - data['magpsf'] + 1*data['sigmapsf'])>0) & ((data['magnr'] - data['magpsf'] - 1*data['sigmapsf'])<0)
data['noflux_3s'] = ((data['magnr'] - data['magpsf'] + 3*data['sigmapsf'])>0) & ((data['magnr'] - data['magpsf'] - 3*data['sigmapsf'])<0)



# combine by id
gb = data.groupby('objectId')

# use aggregation on the groupby to make a summary df
df_summary = gb.agg(
    ra=("ra", np.mean), 
    dec=("dec", np.mean), 
    fid1=("fid", lambda x: np.sum(x==1)), 
    fid2=("fid", lambda x: np.sum(x==2)), 
    fid3=("fid", lambda x: np.sum(x==3)), 
    jd_first=("jd", np.min),
    jd_last=("jd", np.max),
    classtar=("classtar", np.mean),
    sgmag1=("sgmag1", np.mean),
    srmag1=("srmag1", np.mean),
    simag1=("simag1", np.mean),
    szmag1=("szmag1", np.mean),
    ndethist=("ndethist", np.max),
    jdstarthist=("jdstarthist", np.min),
    jdendhist=("jdendhist", np.max),
)

# adding some additional columns that can't be done using agg (they depend on multiple columns)
df_summary['distnr_g'] = gb.apply(lambda x: np.nanmean(x['distnr'][x['fid']==1]))
df_summary['distnr_r'] = gb.apply(lambda x: np.nanmean(x['distnr'][x['fid']==2]))
df_summary['magnr_g'] = gb.apply(lambda x: np.nanmean(x['magnr'][x['fid']==1]))
df_summary['magnr_r'] = gb.apply(lambda x: np.nanmean(x['magnr'][x['fid']==2]))
df_summary['N_noflux_1s_g'] = gb.apply(lambda x: np.sum(x['noflux_1s'][x['fid']==1]))
df_summary['N_noflux_1s_r'] = gb.apply(lambda x: np.sum(x['noflux_1s'][x['fid']==2]))
df_summary['WDRD'] = np.isin(df_summary.index,WDRDs['ids'])


select = (df_summary['N_noflux_1s_r']>0) & (df_summary['N_noflux_1s_g']>0) & (df_summary['sgmag1']-df_summary['srmag1']<1)


for m in [~df_summary['WDRD'],df_summary['WDRD']]:
    plt.plot(df_summary['srmag1'][m]-df_summary['simag1'][m],
             df_summary['sgmag1'][m]-df_summary['srmag1'][m],'.')

for m in [~df_summary['WDRD'],df_summary['WDRD']]:
    plt.plot((df_summary['N_noflux_1s_r']+df_summary['N_noflux_1s_g'])[m],
             (df_summary['N_noflux_1s_g']/(df_summary['N_noflux_1s_r']+df_summary['N_noflux_1s_g']))[m],'.')
plt.show()

for m in [~df_summary['WDRD'],df_summary['WDRD']]:
    plt.plot(
    #(df_summary['N_noflux_1s_r']+df_summary['N_noflux_1s_g'])[m]/(df_summary['fid1']+df_summary['fid2'])[m],
    (df_summary['ndethist'])[m],
    (df_summary['fid1']+df_summary['fid2'])[m],
    '.')
plt.show()



for mask in [~data['noflux_1s'],data['noflux_1s']]:
    plt.plot(data['magnr'][mask],data['ratio'][mask],'.')
plt.show()
