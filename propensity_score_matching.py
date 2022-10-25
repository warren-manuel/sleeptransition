# pipeline for data from NSRR
import csv
import os

import numpy as np
import pandas as pd
import shutil
from psmpy import PsmPy
from psmpy.functions import cohenD
from psmpy.plotting import *

# TODO: Add function to get datafiles
data_files = ['/Users/wmanuel3/shhs/datasets/shhs1-dataset-0.18.0.csv',
              '/Users/wmanuel3/shhs/datasets/shhs2-dataset-0.18.0.csv',
              '/Users/wmanuel3/mros/datasets/mros-visit1-dataset-0.6.0.csv',
              '/Users/wmanuel3/mros/datasets/mros-visit2-dataset-0.6.0.csv']

# os.chdir('/Users/wmanuel3/shhs/datasets')

# 1. Identify target files (SHHS)
csvfile = open(data_files[1])
df = pd.read_csv(csvfile, usecols = ['nsrrid', 'alzh2'])
ad = df['nsrrid'].loc[df['alzh2']==1]
cn = df['nsrrid'].loc[df['alzh2']==0]

# Copying AD to destination folder (although SHHS2 is where the question is asked visit 1 is used to get max number of subjects)
for f in ad:
    print(f)
    src = os.path.join("/Users/wmanuel3/shhs/polysomnography/annotations-events-nsrr/shhs1",('shhs1-'+str(f)+'-nsrr.xml'))
    dst = os.path.join("/Users/wmanuel3/sleep/shhs_ad_1")
    try:
        shutil.copy(src,dst)
    except:
        print('fail')
        continue

# 1.    Identifying propensity score matched AD and CN subjects

csvfile = open(data_files[0])
csvfile1 = open(data_files[1])

# usage of demographics, hypertension, depression, stroke, diabetes
df = pd.read_csv(csvfile, usecols = ['nsrrid',
                                     'age_s1', 'ethnicity','gender','race',
                                     'ace1','aced1','alpha1','alphad1',
                                     'ntca1','tca1',
                                     # 'prev_hx_stroke', Cannot use as alzh2 = 1 are all blank for this field
                                     'insuln1','ohga1'])
df1 = pd.read_csv(csvfile1, usecols = ['nsrrid', 'alzh2',
                                     'age_s2','age_category_s2',
                                     'ntca2','tca2',
                                     'insuln2','ohga2'])
df_full = df.merge(df1, how='outer', on='nsrrid')

# Subsetting data to alzh2 has a value 1 or 0
df_alzh2 = df_full.loc[(df_full['alzh2']==1) | (df_full['alzh2']==0)].dropna()
df_alzh2['alzh2'].value_counts()

# 1.1   Propensity Score Matching

psm = PsmPy(df_alzh2, treatment='alzh2', indx='nsrrid', exclude = [])
psm.logistic_ps(balance = True)
psm.predicted_data
psm.knn_matched_12n(matcher='propensity_logit', how_many=4)
df_subjects = psm.df_matched

# Copying files to relevant
ad = df_subjects['nsrrid'].loc[df_subjects['alzh2']==1]
cn = df_subjects['nsrrid'].loc[df_subjects['alzh2']==0]

# Copying CN to destination folder
for f in cn:
    print(f)
    src = os.path.join("/Users/wmanuel3/shhs/polysomnography/annotations-events-nsrr/shhs1",('shhs1-'+str(f)+'-nsrr.xml'))
    dst = os.path.join("/Users/wmanuel3/sleep/shhs_cn")
    try:
        shutil.copy(src,dst)
    except:
        continue

for f in ad:
    print(f)
    src = os.path.join("/Users/wmanuel3/shhs/polysomnography/annotations-events-nsrr/shhs1",('shhs1-'+str(f)+'-nsrr.xml'))
    dst = os.path.join("/Users/wmanuel3/sleep/shhs_ad")
    try:
        shutil.copy(src,dst)
    except:
        continue


# 2. Identify target files (MrOS)
csvfile2 = open(data_files[2])
csvfile3 = open(data_files[3])

df = pd.read_csv(csvfile2, usecols = ['nsrrid', 'm1alzh'],low_memory=False)
df1 = pd.read_csv(csvfile3, usecols = ['nsrrid', 'm1alzh','mhalzh', 'mhalzht'],low_memory=False)

df_full = df.merge(df1, how='outer', on='nsrrid')
df_full['m1alzh_x'] = df_full['m1alzh_x'].fillna(0)
df_full['m1alzh_y'] = df_full['m1alzh_y'].fillna(0)
df_full['m1alzh_merged'] = df_full['m1alzh_x']+df_full['m1alzh_y']

# m1alzh 1 = AD 0 = NO
df['m1alzh'].value_counts()
df1['m1alzh'].value_counts()
df_full['m1alzh_merged'].value_counts()

# mhalzh	{A:Missing, D:Don't Know, K:DK/UN, M:Not Applicable, 0:No, 1:Yes}
df1['mhalzh'].value_counts()

# mhalzht   {A:Missing, D:Don't Know, K:DK/UN, M:Not Applicable, 0:No, 1:Yes}
df1['mhalzht'].value_counts()

ad = df_full['nsrrid'].loc[(df_full['m1alzh_x']==1) | (df_full['m1alzh_y']==1) | (df_full['mhalzh']==1) | (df_full['mhalzht']==1)]
cn = df_full['nsrrid'].loc[(df_full['m1alzh_x']==1) | (df_full['m1alzh_y']==1)]

# Copying AD to destination folder
for f in ad:
    print(f)
    src = os.path.join("/Users/wmanuel3/mros/polysomnography/annotations-events-nsrr/visit1",('mros-visit1-'+str(f).lower()+'-nsrr.xml'))
    dst = os.path.join("/Users/wmanuel3/sleep/mros_ad")
    open(src)
    try:
        shutil.copy(src,dst)
    except:
        print('fail')
        continue
# Copying CN to destination folder
for f in cn:
    print(f)
    src = os.path.join("/Users/wmanuel3/mros/polysomnography/annotations-events-nsrr/visit1",('mros-visit1-'+str(f).lower()+'-nsrr.xml'))
    dst = os.path.join("/Users/wmanuel3/sleep/mros_cn")
    try:
        shutil.copy(src,dst)
    except:
        continue


