# -*- coding: utf-8 -*-
"""
@author: leasor.4
Use random forest to downscale file from 9km to 1km
"""
import csv
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import pandas as pd
regions=['Central','EastNorthCentral','Northeast','Northwest',
         'South','Southeast','Southwest','West','WestNorthCentral']
feature_list=['Elevation','Sand','Precip','NDVI','Temp']  
#import date list
dates=open('D:/OneDrive - The Ohio State University/Sharpe/PRISM/datelist.csv')
d_l=csv.reader(dates,delimiter=',',quotechar='|')
d=list(d_l)#366 days
dates.close()
    
#1 km elevation
km_1_grid=open('D:/OneDrive - The Ohio State University/Sharpe/DEM/DEM.csv')
p_g=csv.reader(km_1_grid,delimiter=',',quotechar='|')
grid_dem=list(p_g)#7763333 grid cells
km_1_grid.close()

#1 km gSSURGO
km_1_grid3=open('D:/OneDrive - The Ohio State University/Sharpe/gSSURGO/soil_texture_d5.csv')
p_g3=csv.reader(km_1_grid3,delimiter=',',quotechar='|')
grid_gssurgo=list(p_g3)#7763333 grid cells
km_1_grid3.close()

#9 km elevation
km_9_grid=open('D:/OneDrive - The Ohio State University/Sharpe/DEM/DEM_9km_clipped.csv')
p_g4=csv.reader(km_9_grid,delimiter=',',quotechar='|')
grid2_dem=list(p_g4)#93906 grid cells
km_9_grid.close()

#9 km gSSURGO
km_9_grid3=open('D:/OneDrive - The Ohio State University/Sharpe/gSSURGO/gSSURGO_d5_9km_clipped.csv')
p_g6=csv.reader(km_9_grid3,delimiter=',',quotechar='|')
grid2_gssurgo=list(p_g6)#93906 grid cells
km_9_grid3.close()

annual_importances=[]#Store daily variable importances
#July is range(182,213)
for q in range(182,183):
    p_filename1='prep_'+d[q][0]+'nn_1km.csv'
    pt_filename1='tmean_'+d[q][0]+'nn_1km.csv'
    p_filename9='prep_'+d[q][0]+'nn_9km_clipped.csv'
    pt_filename9='tmean_'+d[q][0]+'nn_9km_clipped.csv'
    s_filename9='SMAP_L4_SM_aup_'+d[q][0]+'T150000_9km_clipped.csv'
    n_filename1='NDVI_'+d[q][0]+'nn_1km.csv'
    n_filename9='NDVI_'+d[q][0]+'nn_9km_clipped.csv'
    idata=d[q][0]+'.csv'

    #In situ data
    insitu_data=pd.read_csv('D:/OneDrive - The Ohio State University/Sharpe/insitu_2016_5cm/'+idata)
    
    #1 km PRISM precip
    km_1_grid2=open('D:/OneDrive - The Ohio State University/Sharpe/PRISM/PRISM_API_1km/'+p_filename1)
    p_g2=csv.reader(km_1_grid2,delimiter=',',quotechar='|')
    grid_prism=list(p_g2)#7763333 grid cells
    km_1_grid2.close()
        
#     #1 km PRISM API
#     km_1_grid2=open('D:/OneDrive - The Ohio State University/Sharpe/PRISM/PRISM_1km/'+p_filename1)
#     p_g2=csv.reader(km_1_grid2,delimiter=',',quotechar='|')
#     grid_prism=list(p_g2)#7763333 grid cells
#     km_1_grid2.close()
    
    #1 km PRISM temp
    km_1_grid5=open('D:/OneDrive - The Ohio State University/Sharpe/PRISM/PRISM_1km_T/'+pt_filename1)
    p_g9=csv.reader(km_1_grid5,delimiter=',',quotechar='|')
    grid_prismt=list(p_g9)#7763333 grid cells
    km_1_grid5.close()
    
    #1 km NDVI
    km_1_grid4=open('D:/OneDrive - The Ohio State University/Sharpe/AVHRR_NDVI_9km/NDVI_1km/'+n_filename1)
    p_g7=csv.reader(km_1_grid4,delimiter=',',quotechar='|')
    grid_ndvi=list(p_g7)#7763333 grid cells
    km_1_grid4.close()
    
    #9 km PRISM precip
    km_9_grid2=open('D:/OneDrive - The Ohio State University/Sharpe/PRISM/PRISM_9km_clipped/'+p_filename9)
    p_g5=csv.reader(km_9_grid2,delimiter=',',quotechar='|')
    grid2_prism=list(p_g5)#93906 grid cells
    km_9_grid2.close()
    
#    #9 km PRISM API
#    km_9_grid2=open('D:/OneDrive - The Ohio State University/Sharpe/PRISM/PRISM_API_9km_clipped/'+p_filename9)
#    p_g5=csv.reader(km_9_grid2,delimiter=',',quotechar='|')
#    grid2_prism=list(p_g5)#93906 grid cells
#    km_9_grid2.close()
    
    #9 km PRISM temp
    km_9_grid5=open('D:/OneDrive - The Ohio State University/Sharpe/PRISM/PRISM_T_9km_clipped/'+pt_filename9)
    p_g10=csv.reader(km_9_grid5,delimiter=',',quotechar='|')
    grid2_prismt=list(p_g10)#93906 grid cells
    km_9_grid5.close()
    
    #9 km SMAP
    smap_grid=open('D:/OneDrive - The Ohio State University/Sharpe/SMAP/SMAP_extracted_clipped/'+s_filename9)
    s_g=csv.reader(smap_grid,delimiter=',',quotechar='|')
    sgrid=list(s_g)#93906 grid cells
    smap_grid.close()
    print s_filename9
    
    #9 km NDVI
    km_9_grid4=open('D:/OneDrive - The Ohio State University/Sharpe/AVHRR_NDVI_9km/NDVI_clipped/'+n_filename9)
    p_g8=csv.reader(km_9_grid4,delimiter=',',quotechar='|')
    grid2_ndvi=list(p_g8)#93906 grid cells
    km_9_grid4.close()
    #del(p_filename1, pt_filename1, p_filename9, pt_filename9, s_filename9, n_filename1, n_filename9, idata)

    #Organize 1km data (Check the lat/lon order on these files)
    xg,yg,eg,sandg,pg,pgt,ng=([]for h in range(7))#define the data
    for g in range(1,len(grid_dem)):
        xg.append(float(grid_dem[g][4]))# 1km grid longitude
        yg.append(float(grid_dem[g][3]))# 1km grid latitude
        eg.append(float(grid_dem[g][2])) #elevation (m)
#        clayg.append(float(grid_gssurgo[g][3]))#clay (%)
        sandg.append(float(grid_gssurgo[g][4]))#sand (%)
#        siltg.append(float(grid_gssurgo[g][5]))#silt (%)
        pg.append(float(grid_prism[g][2])) #pcp (mm)
        pgt.append(float(grid_prismt[g][2])) #tmean (C)
        ng.append(float(grid_ndvi[g][2])) #ndvi (-0.1 to 1)
    del(grid_prism,grid_prismt,grid_ndvi,grid_dem,grid_gssurgo,g)
    xg2,yg2,sg2,eg2,sand2g,pg2,pgt2,ng2,master,masteri=([]for h in range(10))#define the data
    count=0
    for k in range(1,len(sgrid)):#This loop removes the missing data from smap grid cells
        if sgrid[k][2]!='-9999.000000':
            xg2.append(float(sgrid[k][1]))# SMAP 9km longitude
            yg2.append(float(sgrid[k][0]))# SMAP 9km latitude
            sg2.append(float(sgrid[k][2]))#SM Anomaly with no data coded as -9999
            eg2.append(float(grid2_dem[k][2])) #elevation (m)
            master.append(int(grid2_dem[k][3])) #climate region identifier
            masteri.append(count)
            #clay2g.append(float(grid2_gssurgo[k][2])) #clay (%)
            sand2g.append(float(grid2_gssurgo[k][3])) #sand (%)
            #silt2g.append(float(grid2_gssurgo[k][4])) #silt (%)
            pg2.append(float(grid2_prism[k][2])) #pcp (mm)
            pgt2.append(float(grid2_prismt[k][2])) #tmean (C)
            ng2.append(float(grid2_ndvi[k][2])) #ndvi (-0.1 to 1)
            count=count+1
                
    del(sgrid,grid2_dem,grid2_gssurgo,grid2_prism,grid2_prismt,grid2_ndvi,k)
    smap=np.array([xg2,yg2,sg2])#SMAP lon,lat, and SM 3x93812
    km_1=np.array([eg,sandg,pg,pgt,ng])# (5x7763332)
    km_9=np.array([eg2,sand2g,pg2,pgt2,ng2])# (5x93812)
    xgr=np.array(xg)
    ygr=np.array(yg)
    del(xg,yg)
    del(eg,pg,pgt,ng,xg2,yg2,eg2,pg2,pgt2,sg2,ng2)
    del(sandg,sand2g)
    print 'Data Prep Complete'    
    for i in range(0,len(regions)):
        rows1,rows9=([]for v in range(2))
        s_filename1='SMAP_L4_SM_RF8_'+d[q][0]+regions[i]+'T150000_1km.csv'

        c1=open('D:/OneDrive - The Ohio State University/Sharpe/Subregions/'+regions[i]+'_grids.csv')
        c_1=csv.reader(c1,delimiter=',',quotechar='|')
        cells1=list(c_1)
        c1.close()
        for v in range(1,len(cells1)):
            rows1.append((int(cells1[v][2])-1))#subtract 1 for zero indexing
            
        for b in range(0,len(master)):
            if int(master[b])-1==i:
                rows9.append((int(masteri[b])))#subtract 1 for zero indexing
        
        region_9km = pd.read_csv('D:/OneDrive - The Ohio State University/Sharpe/Subregions/'+regions[i]+'_9km.csv')    
        smap_9km = pd.read_csv('D:/OneDrive - The Ohio State University/Sharpe/SMAP/SMAP_extracted_clipped/'+s_filename9)          
        smap_9km['pointid'] = smap_9km.index+1
        smap_sub9 = smap_9km.loc[smap_9km['pointid'].isin(list(region_9km['pointid']._values))]
        region1=km_1[:,np.array(rows1)]
        region9=km_9[:,np.array(rows9)]
        regionsmap9=smap[:,np.array(rows9)]
        regionxg=xgr[np.array(rows1)]
        regionyg=ygr[np.array(rows1)]
        #Split data into training and test sets
        #Train by building a relationship from original 9km grid
        #Instantiate model with 1000 decision trees
        rf = RandomForestRegressor(n_estimators = 100, random_state = 42)#random_state is a seed for reproducibility
        rf.fit(region9.transpose(),regionsmap9[2])
        importances = list(rf.feature_importances_)# List of tuples with variable and importance
        annual_importances.append([importances])
        predictions=rf.predict(region1.transpose())
        print 'RF Downscaling Complete'
#        #Independent (X) data should be reshaped right now because they only contain one feature (column)
#        #https://towardsdatascience.com/random-forest-in-python-24d0893d51c0
        #km_1=np.transpose(km_1)#match predictions
        p2=np.transpose(np.array([predictions]))
        coor=np.transpose(np.array([regionxg,regionyg]))
        output=np.concatenate((coor,p2),axis=1)
        np.savetxt(s_filename1,output,fmt='%1.3f',delimiter=",",
               header='Lon,Lat,SM',comments='')
    
        with open(str('dailyimportancesRF8'+regions[i]+'.csv'), "wb") as f:
            writer = csv.writer(f)
            writer.writerows(annual_importances)
            
        del(v,b,region1,region9,regionsmap9,regionxg,regionyg,predictions,p2,coor,output)

#View decision trees, takes too long (> 4 hours)
#from sklearn.tree import export_graphviz
#import pydot
#feature_list=['Elevation','Clay','Sand','Silt','Precip','NDVI']
##Pull out one tree from the forest
#tree=rf.estimators_[1]
## Export the image to a dot file
#export_graphviz(tree, out_file = 'tree.dot', feature_names = feature_list, rounded = True, precision = 1)# Use dot file to create a graph
#(graph, ) = pydot.graph_from_dot_file('tree.dot')# Write graph to a png file
#graph.write_png('tree.png')
#    
#Variable importance
# Get numerical feature importances
#importances = list(rf.feature_importances_)# List of tuples with variable and importance
#feature_importances = [(feature, round(importance, 2)) for feature, importance in zip(feature_list, importances)]# Sort the feature importances by most important first
#feature_importances = sorted(feature_importances, key = lambda x: x[1], reverse = True)# Print out the feature and importances 
##for pair in feature_importances:
##    print('Variable: {:20} Importance: {}'.format(*pair))
#
##Make a plot of the variable importances
#import matplotlib.pyplot as plt
##%matplotlib inline
## Set the style
#plt.style.use('fivethirtyeight')
## list of x locations for plotting
#x_values = list(range(len(importances)))
## Make a bar chart
#plt.bar(x_values, importances, orientation = 'vertical')
## Tick labels for x axis
#plt.xticks(x_values, feature_list, rotation='vertical')
## Axis labels and title
#plt.ylabel('Importance'); plt.xlabel('Variable'); plt.title('Variable Importances');