import csv,os,sys
import numpy as np
import pandas as pd
from pandas.core.algorithms import isin
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import datetime
import pyproj
from pykrige.rk import RegressionKriging
from sklearn.svm import SVR
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error
from scipy.spatial import distance

def closest_node(node, nodes):
    closest_index = distance.cdist([node], nodes).argmin()
    return closest_index

def rk_interp(smap_sub9,smap_sub1,train_1km,date):
    svr_model = SVR(C=0.1)
    rf_model = RandomForestRegressor(n_estimators=100)
    lr_model = LinearRegression(normalize=True, copy_X=True, fit_intercept=False)
    training,testing = train_test_split(smap_sub9,test_size = 0.2)
    x1_train_9km = training.iloc[:,:2]._values
    target1_train_9km = training.iloc[:,2]._values
    p1_train_9km = training.iloc[:,4:]._values
    # train against insitu data
    insitu_path = r'C:\Users\zhaoc\Documents\chen_research\sharpe_seed_grant\insitu_2016_5cm/'
    insitu_data = pd.read_csv(insitu_path+date+'.csv')
    # subset insitu to region
    max_lat = np.max(smap_sub9['Latitude'])
    min_lat = np.min(smap_sub9['Latitude'])
    max_lon = np.max(smap_sub9['Longitude'])
    min_lon = np.min(smap_sub9['Longitude'])
    insitu_subset = insitu_data.loc[(insitu_data['lat']<= max_lat) & (insitu_data['lat']>= min_lat)&(insitu_data['lon']>= min_lon)&(insitu_data['lon']<= max_lon)]
    insitu_subset = insitu_subset.dropna()
    # find the 1km grid where insitu station locates
    pos = []
    aux = []
    for p in range(len(insitu_subset)):
        tar_point =(insitu_subset['lat'].iloc[p],insitu_subset['lon'].iloc[p])
        p_index = closest_node(tar_point,smap_sub1)
        pos.append(smap_sub1[p_index])
        aux.append(train_1km[p_index])
    # build RK model and train against insitu data
    mae_all = []
    for n in range(5,15):
        m_rk = RegressionKriging(regression_model=svr_model,method = 'ordinary', n_closest_points=n,nlags=n,weight=False)
        m_rk.fit(p1_train_9km, x1_train_9km, target1_train_9km)
        predict_point = m_rk.predict(np.array(aux), np.array(pos))
        mae = mean_absolute_error(insitu_subset['vwc_5cm']._values,predict_point)
        mae_all.append([n,mae])
    mae_array = pd.DataFrame(mae_all)
    nlag = int(mae_array.loc[mae_array.iloc[:,1].idxmin()][0])
    # predict 1 km grids with optimal nlag
    m_rk = RegressionKriging(regression_model=svr_model,method = 'ordinary', n_closest_points=nlag,nlags=nlag,weight=False)
    m_rk.fit(p1_train_9km, x1_train_9km, target1_train_9km)
    predict = m_rk.predict(train_1km, smap_sub1)
    return predict


#import date list
dates=open('C:/Users/zhaoc/OneDrive - The Ohio State University/Sharpe/PRISM/datelist.csv')
d_l=csv.reader(dates,delimiter=',',quotechar='|')
d=list(d_l)#366 days
dates.close()

path = r'C:\Users\zhaoc\Documents\chen_research\sharpe_seed_grant\Subregions'
files = os.listdir(path)
files_9km = [i for i in files if i.endswith('9km.csv')]
files_1km =  [i for i in files if not i.endswith('9km.csv')]

# clip grids
os.chdir(path)
for q in range(182,183):
    for region in range(len(files_9km)):
        # process 9km
        region_9km = pd.read_csv(files_9km[region])
        elevation = pd.read_csv('C:/Users/zhaoc/OneDrive - The Ohio State University/Sharpe/DEM/DEM_9km_clipped_for_subregions.csv')
        gssurgo = pd.read_csv('C:/Users/zhaoc/OneDrive - The Ohio State University/Sharpe/gSSURGO/gSSURGO_d5_9km_clipped.csv')
        # elevation
        ele_sub9 = elevation.loc[elevation['pointid'].isin(list(region_9km['pointid']._values))]
        # gssurgo
        gssurgo['pointid'] = gssurgo.index +1
        gssurgo = gssurgo.loc[gssurgo['pointid'].isin(list(region_9km['pointid']._values))]
        # precip
        p_filename9='prep_'+d[q][0]+'nn_9km_clipped.csv'
        s_filename9='SMAP_L4_SM_aup_'+d[q][0]+'T150000_9km_clipped.csv'
        n_filename9='NDVI_'+d[q][0]+'nn_9km_clipped.csv'
        pt_filename9='tmean_'+d[q][0]+'nn_9km_clipped.csv'
        precip_9km = pd.read_csv('C:/Users/zhaoc/OneDrive - The Ohio State University/Sharpe/PRISM/PRISM_9km_clipped/'+p_filename9)
        precip_9km['pointid'] = precip_9km.index+1
        pt_9km = pd.read_csv('C:/Users/zhaoc/OneDrive - The Ohio State University/Sharpe/PRISM/PRISM_T_9km_clipped/'+pt_filename9)
        pt_9km['pointid'] = pt_9km.index +1
        smap_9km = pd.read_csv('C:/Users/zhaoc/OneDrive - The Ohio State University/Sharpe/SMAP/SMAP_extracted_clipped/'+s_filename9)
        smap_9km['pointid'] = smap_9km.index+1
        ndvi_9km = pd.read_csv('C:/Users/zhaoc/OneDrive - The Ohio State University/Sharpe/AVHRR_NDVI_9km/NDVI_clipped/'+n_filename9)
        ndvi_9km['pointid'] = ndvi_9km.index +1
        # subregion
        precip_sub9 = precip_9km.loc[precip_9km['pointid'].isin(list(region_9km['pointid']._values))]
        smap_sub9 = smap_9km.loc[smap_9km['pointid'].isin(list(region_9km['pointid']._values))]
        gs_sub9 = gssurgo.loc[gssurgo['pointid'].isin(list(region_9km['pointid']._values))]
        pt_sub9 = pt_9km.loc[pt_9km['pointid'].isin(list(region_9km['pointid']._values))]
        ndvi_sub9 = ndvi_9km.loc[ndvi_9km['pointid'].isin(list(region_9km['pointid']._values))]
        # add auxiliary variables to smap_sub9
        smap_sub9['prcp'] = precip_sub9['Pcp']
        smap_sub9['elevation'] = ele_sub9['Elevation']
        smap_sub9['clay'] = gs_sub9['Clay']
        smap_sub9['sand'] = gs_sub9['Sand']
        # smap_sub9['silt'] = gs_sub9['Silt']
        smap_sub9['tmean'] = pt_sub9['tmean']
        smap_sub9['ndvi'] = ndvi_sub9['NDVI']
        # process 1km
        region_1km = pd.read_csv(files_1km[region])
        ele_1km = pd.read_csv('C:/Users/zhaoc/OneDrive - The Ohio State University/Sharpe/DEM/DEM.csv')
        p_filename1='prep_'+d[q][0]+'nn_1km.csv'
        s_filename1='SMAP_L4_SM_RK_'+files_9km[region][:-7]+'_'+d[q][0]+'T150000_1km.csv'
        n_filename1='NDVI_'+d[q][0]+'nn_1km.csv'
        pt_filename1='tmean_'+d[q][0]+'nn_1km.csv'
        precip_1km = pd.read_csv('C:/Users/zhaoc/OneDrive - The Ohio State University/Sharpe/PRISM/PRISM_1km/'+p_filename1)
        precip_1km['pointid'] = precip_1km.index+1
        pt_1km = pd.read_csv('C:/Users/zhaoc/OneDrive - The Ohio State University/Sharpe/PRISM/PRISM_1km_T/'+pt_filename1)
        pt_1km['pointid'] = pt_1km.index+1
        ndvi_1km = pd.read_csv('C:/Users/zhaoc/OneDrive - The Ohio State University/Sharpe/AVHRR_NDVI_9km/NDVI_1km/'+n_filename1)
        ndvi_1km['pointid'] = ndvi_1km.index +1
        gssurgo_1km = pd.read_csv('C:/Users/zhaoc/OneDrive - The Ohio State University/Sharpe/gSSURGO/soil_texture_d5.csv')
        gssurgo_1km['pointid'] = gssurgo_1km.index +1
        # subregion
        precip_sub1 = precip_1km.loc[precip_1km['pointid'].isin(list(region_1km['pointid']._values))]
        ele_sub1 = ele_1km.loc[ele_1km['pointid'].isin(list(region_1km['pointid']._values))]
        gssurgo_sub1 = gssurgo_1km.loc[gssurgo_1km['pointid'].isin(list(region_1km['pointid']._values))]
        pt_sub1 = pt_1km.loc[pt_1km['pointid'].isin(list(region_1km['pointid']._values))]
        ndvi_sub1 = ndvi_1km[ndvi_1km['pointid'].isin(list(region_1km['pointid']._values))]
        train_1km = pd.DataFrame([precip_sub1['Pcp'],ele_sub1['grid_code'],gssurgo_sub1['sand'],gssurgo_sub1['clay'],pt_sub1['tmean'],ndvi_sub1['NDVI']]).T._values
        x1_1km = precip_sub1.iloc[:,:2]._values
        predict_1km = rk_interp(smap_sub9,x1_1km,train_1km,d[q][0])
        sm_1km = precip_sub1.iloc[:,:2]
        sm_1km['sm'] = predict_1km
        sm_1km.to_csv(s_filename1,index = False)