import csv,os,sys
import numpy as np
import pandas as pd
from pandas.core.algorithms import isin
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import datetime
from pykrige.rk import RegressionKriging
from sklearn.svm import SVR
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error
from scipy.spatial import distance
from math import cos, asin, sqrt

def dist(lat1, lon1, lat2, lon2):
    # unit km
    p = 0.017453292519943295
    hav = 0.5 - cos((lat2-lat1)*p)/2 + cos(lat1*p)*cos(lat2*p) * (1-cos((lon2-lon1)*p)) / 2
    return 12742 * asin(sqrt(hav))

def closest_node(node, nodes):
    closest_index = distance.cdist([node], nodes).argmin()
    return closest_index

def rk_interp(smap_sub9,smap_sub1,train_1km,date,test_size=0.2):
    svr_model = SVR(C=0.1)
    rf_model = RandomForestRegressor(n_estimators=100)
    lr_model = LinearRegression(normalize=True, copy_X=True, fit_intercept=False)
    training,testing = train_test_split(smap_sub9,test_size = test_size)
    x1_train_9km = training.iloc[:,:2]._values
    target1_train_9km = training.iloc[:,2]._values
    p1_train_9km = training.iloc[:,4:]._values
    # train against insitu data
    insitu_path = r'/fs/ess/scratch/PAS1961/sharpe/insitu_2016_5cm/'
    insitu_data = pd.read_csv(insitu_path+date+'.csv')
    insitu_data = insitu_data.dropna()
    # find the 1km grid where insitu station locates
    pos = []
    aux = []
    sm_point = []
    for p in range(len(insitu_data)):
        tar_point =(insitu_data['lat'].iloc[p],insitu_data['lon'].iloc[p])
        p_index = closest_node(tar_point,smap_sub1)
        d_p = dist(tar_point[0],tar_point[1],smap_sub1[p_index][0],smap_sub1[p_index][1])
        # less than 3 km
        if d_p < 3:
            pos.append(smap_sub1[p_index])
            aux.append(train_1km[p_index])
            sm_point.append(insitu_data['vwc_5cm'].iloc[p])
    # build RK model and train against insitu data
    mae_all = []
    for n in range(5,15):
        m_rk = RegressionKriging(regression_model=svr_model,method = 'ordinary', n_closest_points=n,nlags=n,weight=False)
        m_rk.fit(p1_train_9km, x1_train_9km, target1_train_9km)
        predict_point = m_rk.predict(np.array(aux), np.array(pos))
        mae = mean_absolute_error(np.array(sm_point),predict_point)
        mae_all.append([n,mae])
    mae_array = pd.DataFrame(mae_all)
    nlag = int(mae_array.loc[mae_array.iloc[:,1].idxmin()][0])
    # predict 1 km grids with optimal nlag
    m_rk = RegressionKriging(regression_model=svr_model,method = 'ordinary', n_closest_points=nlag,nlags=nlag,weight=False)
    m_rk.fit(p1_train_9km, x1_train_9km, target1_train_9km)
    predict = m_rk.predict(train_1km, smap_sub1)
    return predict

def rf_interp(smap_sub9,smap_sub1,train_1km,date,test_size=0.2):
    '''
    Interpolate soil moisture using random forest.
    '''
    # separate train, test data
    training,testing = train_test_split(smap_sub9,test_size = test_size)
    x1_train_9km = training.iloc[:,:2]._values
    target1_train_9km = training.iloc[:,2]._values
    p1_train_9km = training.iloc[:,4:]._values
    # remove -9999 from training data
    training = training[training['Data'] != -9999.0]
    # train against insitu data
    insitu_path = r'/fs/ess/scratch/PAS1961/sharpe/insitu_2016_5cm/'
    # insitu_path = r'C:\Users\zhaoc\Documents\chen_research\sharpe_seed_grant\insitu_2016_5cm/'
    insitu_data = pd.read_csv(insitu_path+date+'.csv')
    insitu_data = insitu_data.dropna()
    # find the 1km grid where insitu station locates
    pos = []
    aux = []
    cov_all = []
    sm_point = []
    for p in range(len(insitu_data)):
        tar_point =(insitu_data['lat'].iloc[p],insitu_data['lon'].iloc[p])
        p_index = closest_node(tar_point,smap_sub1)
        d_p = dist(tar_point[0],tar_point[1],smap_sub1[p_index][0],smap_sub1[p_index][1])
        # less than 3 km
        if d_p < 3:
            pos.append(smap_sub1[p_index])
            aux.append(train_1km[p_index])
            cov_all.append(list(train_1km[p_index])+list(smap_sub1[p_index]))
            sm_point.append(insitu_data['vwc_5cm'].iloc[p])
    # RF interp
    annual_importances = []
    rf = RandomForestRegressor(n_estimators = 100, random_state = 44)#random_state is a seed for reproducibility
    # build model with 9km data
    # matrix1:clay,silt, prep, etc; matrix2: lon,lat, and SM
    # train RF on each 9 km grid
    # coordinates should be covariates
    rf_aux_9km = training.iloc[:,[0,1,4,5,6,7,8,9]]._values
    # sm_train_9km = training.iloc[gr,:2]._values
    sm_train_9km = training.iloc[:,2]
    rf.fit(rf_aux_9km, sm_train_9km)
    importances = list(rf.feature_importances_)# List of tuples with variable and importance
    annual_importances.append([importances])
    # predict on 1km grid
    sm_1km = np.array(cov_all)
    # predict on in situ points
    predictions=rf.predict(sm_1km)
    # print 'RF Downscaling Complete'
    mae = mean_absolute_error(sm_point,predictions)
    print('Mean Absolute Error:', round(mae, 2))
    #https://towardsdatascience.com/random-forest-in-python-24d0893d51c0
    #https://towardsdatascience.com/hyperparameter-tuning-the-random-forest-in-python-using-scikit-learn-28d2aa77dd74
    # predict on all 1km grids, make sure the order of columns are the same
    aux_1km = np.hstack([train_1km,smap_sub1])
    predic_1km = rf.predict(aux_1km)
    output = pd.DataFrame(smap_sub1,columns=['Lat','Lon'])
    output['sm_prediction'] = predic_1km
    return output
    # # save it
    # out_path = r'/fs/ess/scratch/PAS1961/sharpe/Downscale_Regions/Result/'
    # output.to_csv(s_filename1,index = False)

    # with open(str('/fs/ess/scratch/PAS1961/sharpe/Downscale_Regions/Result/dailyimportancesRF8'+regions[i]+'.csv'), "wb") as f:
    #     writer = csv.writer(f)
    #     writer.writerows(annual_importances)


#import date list
dates=open('/fs/ess/scratch/PAS1961/sharpe/PRISM/datelist.csv')
d_l=csv.reader(dates,delimiter=',',quotechar='|')
d=list(d_l)#366 days
dates.close()

path = r'/fs/ess/scratch/PAS1961/sharpe/Subregions'
files = os.listdir(path)
files_9km = [i for i in files if i.endswith('9km.csv')]
files_1km =  [i for i in files if i.endswith('grids.csv')]
files_1km.sort()
files_9km.sort()
# clip grids
for q in range(182,192):
    for region in range(len(files_9km)):
        os.chdir(path)
        # process 9km
        region_9km = pd.read_csv(files_9km[region])
        elevation = pd.read_csv('/fs/ess/scratch/PAS1961/sharpe/DEM/DEM_9km_clipped_for_subregions.csv')
        gssurgo = pd.read_csv('/fs/ess/scratch/PAS1961/sharpe/gSSURGO/gSSURGO_d5_9km_clipped.csv')
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
        precip_9km = pd.read_csv('/fs/ess/scratch/PAS1961/sharpe/PRISM/PRISM_9km_clipped/'+p_filename9)
        precip_9km['pointid'] = precip_9km.index+1
        pt_9km = pd.read_csv('/fs/ess/scratch/PAS1961/sharpe/PRISM/PRISM_T_9km_clipped/'+pt_filename9)
        pt_9km['pointid'] = pt_9km.index +1
        smap_9km = pd.read_csv('/fs/ess/scratch/PAS1961/sharpe/SMAP/SMAP_extracted_clipped/'+s_filename9)
        smap_9km['pointid'] = smap_9km.index+1
        ndvi_9km = pd.read_csv('/fs/ess/scratch/PAS1961/sharpe/AVHRR_NDVI_9km/NDVI_clipped/'+n_filename9)
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
        region_1km = pd.read_csv(files_1km[region],header=0)
        ele_1km = pd.read_csv('/fs/ess/scratch/PAS1961/sharpe/DEM/DEM.csv')
        p_filename1='prep_'+d[q][0]+'nn_1km.csv'
        s_fn1_rk='SMAP_L4_SM_RK_'+files_1km[region][:-7]+'_'+d[q][0]+'T150000_1km.csv'
        s_fn1_rf = 'SMAP_L4_SM_RF_'+files_1km[region][:-7]+'_'+d[q][0]+'T150000_1km.csv'
        print(s_fn1_rf)
        n_filename1='NDVI_'+d[q][0]+'nn_1km.csv'
        pt_filename1='tmean_'+d[q][0]+'nn_1km.csv'
        precip_1km = pd.read_csv('/fs/ess/scratch/PAS1961/sharpe/PRISM/PRISM_1km/'+p_filename1)
        precip_1km['pointid'] = precip_1km.index+1
        pt_1km = pd.read_csv('/fs/ess/scratch/PAS1961/sharpe/PRISM/PRISM_1km_T/'+pt_filename1)
        pt_1km['pointid'] = pt_1km.index+1
        ndvi_1km = pd.read_csv('/fs/ess/scratch/PAS1961/sharpe/AVHRR_NDVI_9km/NDVI_1km/'+n_filename1)
        ndvi_1km['pointid'] = ndvi_1km.index +1
        gssurgo_1km = pd.read_csv('/fs/ess/scratch/PAS1961/sharpe/gSSURGO/soil_texture_d5.csv')
        gssurgo_1km['pointid'] = gssurgo_1km.index +1
        # subregion
        precip_sub1 = precip_1km.loc[precip_1km['pointid'].isin(list(region_1km['pointid']._values))]
        ele_sub1 = ele_1km.loc[ele_1km['pointid'].isin(list(region_1km['pointid']._values))]
        gssurgo_sub1 = gssurgo_1km.loc[gssurgo_1km['pointid'].isin(list(region_1km['pointid']._values))]
        pt_sub1 = pt_1km.loc[pt_1km['pointid'].isin(list(region_1km['pointid']._values))]
        ndvi_sub1 = ndvi_1km[ndvi_1km['pointid'].isin(list(region_1km['pointid']._values))]
        train_1km = pd.DataFrame([precip_sub1['Pcp'],ele_sub1['grid_code'],gssurgo_sub1['sand'],gssurgo_sub1['clay'],pt_sub1['tmean'],ndvi_sub1['NDVI']]).T._values
        x1_1km = precip_sub1.iloc[:,:2]._values
        # predict_1km = rk_interp(smap_sub9,x1_1km,train_1km,d[q][0])
        rf_pred_1km = rf_interp(smap_sub9,x1_1km,train_1km,d[q][0])
        # sm_1km = precip_sub1.iloc[:,:2]
        # sm_1km['sm'] = predict_1km
        out_path = r'/fs/ess/scratch/PAS1961/sharpe/RK_regions/'
        # if sm_1km['sm'].any()>0 and sm_1km['sm'].any() < 3:
        #     # save
        #     os.chdir(out_path)
        #     sm_1km.to_csv(s_filename1,index = False)
        # else:
        #     while sm_1km['sm'].any()>0 and sm_1km['sm'].any() < 3:
        #         print('do it again')
        #         predict_1km = rk_interp(smap_sub9,x1_1km,train_1km,d[q][0],0.1)
        #         sm_1km = precip_sub1.iloc[:,:2]
        #         sm_1km['sm'] = predict_1km
        os.chdir(out_path)
        # sm_1km.to_csv(s_fn1_rk,index = False)
        rf_pred_1km.to_csv(s_fn1_rf,index = False)
        