import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import geoplot as gplt 
import geoplot.crs as gcrs 
import mapclassify as mc
import statistics as stats
import os

def load_data(data_path, city, svi=False, city_dir=None):
    
	if city == 'St. Louis':
		tract_path = '../maps/stlouis/tl_2020_29510_tract10.shp'
		if svi:
			df_svi = gpd.read_file('../svi/Missouri/SVI2018_MISSOURI_tract.shp')
			df_svi['NAME10'] = (df_svi['LOCATION'].str.split(',').str[0].str.split('Tract ').str[1]).astype('float')
	elif city == 'Chicago':
		tract_path = '../maps/chicago/geo_export_a4ec3105-9b79-40d8-81b0-c8b865cbc38f.shp'
	elif city == 'New York City':
		tract_path = '../maps/newyork/nyct2010.shp'
	elif city == 'Custom':
		for file in os.listdir(city_dir):
			if file.endswith('.shp'):
				tract_path = city_dir + '/' + file

	df_data = pd.read_csv(data_path)
	tract_geodf = gpd.read_file(tract_path)
	tract_geodf['NAME10'] = tract_geodf['NAME10'].astype(float)
	if svi:
		tract_geodf = pd.merge(tract_geodf, df_svi.rename(columns={'NAME20':'NAME10'})[['RPL_THEMES', 
			'E_TOTPOP','E_PCI', 'EP_POV', 'EP_UNEMP', 'EP_PCI', 'EP_NOHSDP', 'EP_AGE65',
			'EP_AGE17', 'EP_DISABL', 'EP_SNGPNT', 'EP_MINRTY', 'EP_LIMENG', 'EP_MUNIT', 
			'EP_MOBILE', 'EP_CROWD', 'EP_NOVEH', 'EP_GROUPQ', 'RPL_THEME1',
			'RPL_THEME2', 'RPL_THEME3', 'RPL_THEME4', 'EP_UNINSUR', 'NAME10']], on='NAME10')
    
	return(df_data, tract_geodf)

## returns dataframe with census tract for each sample
def spatial_join(df_data, tract_geodf):
    
    gdf = gpd.GeoDataFrame(
    df_data, geometry=gpd.points_from_xy(df_data.x, df_data.y)
    )
    gdf.crs = 'epsg:4326'
    gdf = gdf.to_crs('epsg:4269')
    df_tracts_merged = gpd.sjoin(gdf, tract_geodf, how="inner", op="within")
    
    return(df_tracts_merged)

## returns dataframe of stats for each census tract 
def calc_stats(df_tracts_merged, tract_geodf, stat_num=None, stat_cat=None, comparator1=None, 
	comparator2=None, constraint1=None, constraint2=None, conditional=None, 
	cat=False, num=False, pos_cat=None, neg_cat=None):
    
	if num:
		df_tracts_merged.result = pd.to_numeric(df_tracts_merged.result, errors='coerce')
		df_tracts_merged = df_tracts_merged[df_tracts_merged['result'].notna()]
		tract_summary = pd.DataFrame(columns=['NAME10', 'result', 'count'])
		grouped = df_tracts_merged.groupby('NAME10')
		for name, group in grouped:
			count = len(group)
			if stat_num[0] == 'Median':
				median = stats.median(group['result'])
				tract_summary = tract_summary.append({'NAME10': name, 'result': median, 'count': count}, ignore_index=True)
			elif stat_num[0] == 'Mean':
				mean = stats.median(group['result'])
				tract_summary = tract_summary.append({'NAME10': name, 'result': mean, 'count': count}, ignore_index=True)
			elif stat_num[0] == 'Percentage':
				if len(comparator2) == 0:
					if comparator1[0] == '>':
						percentage = len(group[group['result'] > float(constraint1)])/len(group)
					elif comparator1[0] == '>=':
						percentage = len(group[group['result'] >= float(constraint1)])/len(group)
					elif comparator1[0] == '<':
						percentage = len(group[group['result'] < float(constraint1)])/len(group)
					elif comparator1[0] == '<=':
						percentage = len(group[group['result'] <= float(constraint1)])/len(group)
				elif len(comparator2) > 0:
					if conditional[0] == 'AND':
						if comparator1[0] == '>' and comparator2[0] == '>':
							percentage = len(group[(group['result'] > float(constraint1)) & (group['result'] > float(constraint2))])/len(group)
						if comparator1[0] == '>' and comparator2[0] == '>=':
							percentage = len(group[(group['result'] > float(constraint1)) & (group['result'] >= float(constraint2))])/len(group)
						if comparator1[0] == '>' and comparator2[0] == '<':
							percentage = len(group[(group['result'] > float(constraint1)) & (group['result'] < float(constraint2))])/len(group)
						if comparator1[0] == '>' and comparator2[0] == '<=':
							percentage = len(group[(group['result'] > float(constraint1)) & (group['result'] <= float(constraint2))])/len(group)

						elif comparator1[0] == '>=' and comparator2[0] == '>':
							percentage = len(group[(group['result'] >= float(constraint1)) & (group['result'] > float(constraint2))])/len(group)
						elif comparator1[0] == '>=' and comparator2[0] == '>=':
							percentage = len(group[(group['result'] >= float(constraint1)) & (group['result'] >= float(constraint2))])/len(group)
						elif comparator1[0] == '>=' and comparator2[0] == '<':
							percentage = len(group[(group['result'] >= float(constraint1)) & (group['result'] < float(constraint2))])/len(group)
						elif comparator1[0] == '>=' and comparator2[0] == '<=':
							percentage = len(group[(group['result'] >= float(constraint1)) & (group['result'] <= float(constraint2))])/len(group)

						elif comparator1[0] == '<' and comparator2[0] == '>':
							percentage = len(group[(group['result'] < float(constraint1)) & (group['result'] > float(constraint2))])/len(group)
						elif comparator1[0] == '<' and comparator2[0] == '>=':
							percentage = len(group[(group['result'] < float(constraint1)) & (group['result'] >= float(constraint2))])/len(group)	
						elif comparator1[0] == '<' and comparator2[0] == '<':
							percentage = len(group[(group['result'] < float(constraint1)) & (group['result'] < float(constraint2))])/len(group)	
						elif comparator1[0] == '<' and comparator2[0] == '<=':
							percentage = len(group[(group['result'] < float(constraint1)) & (group['result'] <= float(constraint2))])/len(group)			

						elif comparator1[0] == '<=' and comparator2[0] == '>':
							percentage = len(group[(group['result'] <= float(constraint1)) & (group['result'] > float(constraint2))])/len(group)
						elif comparator1[0] == '<=' and comparator2[0] == '>=':
							percentage = len(group[(group['result'] <= float(constraint1)) & (group['result'] >= float(constraint2))])/len(group)
						elif comparator1[0] == '<=' and comparator2[0] == '<':
							percentage = len(group[(group['result'] <= float(constraint1)) & (group['result'] < float(constraint2))])/len(group)
						elif comparator1[0] == '<=' and comparator2[0] == '<=':
							percentage = len(group[(group['result'] <= float(constraint1)) & (group['result'] <= float(constraint2))])/len(group)

					elif conditional[0] == 'OR':
						if comparator1[0] == '>' and comparator2[0] == '>':
							percentage = len(group[(group['result'] > float(constraint1)) | (group['result'] > float(constraint2))])/len(group)
						if comparator1[0] == '>' and comparator2[0] == '>=':
							percentage = len(group[(group['result'] > float(constraint1)) | (group['result'] >= float(constraint2))])/len(group)
						if comparator1[0] == '>' and comparator2[0] == '<':
							percentage = len(group[(group['result'] > float(constraint1)) | (group['result'] < float(constraint2))])/len(group)
						if comparator1[0] == '>' and comparator2[0] == '<=':
							percentage = len(group[(group['result'] > float(constraint1)) | (group['result'] <= float(constraint2))])/len(group)

						elif comparator1[0] == '>=' and comparator2[0] == '>':
							percentage = len(group[(group['result'] >= float(constraint1)) | (group['result'] > float(constraint2))])/len(group)
						elif comparator1[0] == '>=' and comparator2[0] == '>=':
							percentage = len(group[(group['result'] >= float(constraint1)) | (group['result'] >= float(constraint2))])/len(group)
						elif comparator1[0] == '>=' and comparator2[0] == '<':
							percentage = len(group[(group['result'] >= float(constraint1)) | (group['result'] < float(constraint2))])/len(group)
						elif comparator1[0] == '>=' and comparator2[0] == '<=':
							percentage = len(group[(group['result'] >= float(constraint1)) | (group['result'] <= float(constraint2))])/len(group)

						elif comparator1[0] == '<' and comparator2[0] == '>':
							percentage = len(group[(group['result'] < float(constraint1)) | (group['result'] > float(constraint2))])/len(group)
						elif comparator1[0] == '<' and comparator2[0] == '>=':
							percentage = len(group[(group['result'] < float(constraint1)) | (group['result'] >= float(constraint2))])/len(group)	
						elif comparator1[0] == '<' and comparator2[0] == '<':
							percentage = len(group[(group['result'] < float(constraint1)) | (group['result'] < float(constraint2))])/len(group)	
						elif comparator1[0] == '<' and comparator2[0] == '<=':
							percentage = len(group[(group['result'] < float(constraint1)) | (group['result'] <= float(constraint2))])/len(group)			

						elif comparator1[0] == '<=' and comparator2[0] == '>':
							percentage = len(group[(group['result'] <= float(constraint1)) | (group['result'] > float(constraint2))])/len(group)
						elif comparator1[0] == '<=' and comparator2[0] == '>=':
							percentage = len(group[(group['result'] <= float(constraint1)) | (group['result'] >= float(constraint2))])/len(group)
						elif comparator1[0] == '<=' and comparator2[0] == '<':
							percentage = len(group[(group['result'] <= float(constraint1)) | (group['result'] < float(constraint2))])/len(group)
						elif comparator1[0] == '<=' and comparator2[0] == '<=':
							percentage = len(group[(group['result'] <= float(constraint1)) | (group['result'] <= float(constraint2))])/len(group)

				tract_summary = tract_summary.append({'NAME10': name, 'result': percentage, 'count': count}, ignore_index=True)
			
	elif cat:
		tract_summary = pd.DataFrame(columns=['NAME10', 'result', 'count'])
		grouped = df_tracts_merged.groupby('NAME10')
		for name, group in grouped:
			count = len(group)
			if stat_cat[0] == 'Count':
				pos_count = len(group[group['result'] == pos_cat])
				tract_summary = tract_summary.append({'NAME10': name, 'result': pos_count, 'count': count}, ignore_index=True)
			elif stat_cat[0] == 'Rate':
				rate = len(group[group['result'] == pos_cat])/(len(group[group['result'] == pos_cat])+len(group[group['result'] == neg_cat]))
				tract_summary = tract_summary.append({'NAME10': name, 'result': rate, 'count': count}, ignore_index=True)

	tract_summary = pd.merge(tract_summary, tract_geodf, on='NAME10')
	return(tract_summary)


def create_choropleth(tract_summary, tract_geodf, color, svi=False, count=False, scheme=False, k_num=None, ses_var=None, title=None):

	tract_summary = gpd.GeoDataFrame(tract_summary, geometry='geometry')
	tract_summary.result = pd.to_numeric(tract_summary.result, errors='ignore')
	tract_summary['count'] = pd.to_numeric(tract_summary['count'], errors='ignore')

	if color == 'red':
		Color = 'Reds'
	if color == 'blue':
		Color = 'Blues'
	if color == 'green':
		Color = 'Greens'

	ses_var_dict = {'Social Vulnerability Index': 'RPL_THEMES', 
	'Socioeconomic composite': 'RPL_THEME1',
	'Household composition composite': 'RPL_THEME2',
	'Minority status/Language composite': 'RPL_THEME3',
	'Housing type/Transportation composite': 'RPL_THEME4',
	'Population (Total)': 'E_TOTPOP',
	'Age 65+ (%)': 'EP_AGE65',
	'Age 17 and younger (%)': 'EP_AGE17',
	'Non-white persons (%)': 'EP_MINRTY',
	'Per capita income ($)': 'EP_PCI',
	'Poverty rate': 'EP_POV',
	'Unemployment rate (%)': 'EP_UNEMP',
	'No high school diploma (%)': 'EP_NOHSDP',
	'With a disability (%)': 'EP_DISABL',
	'Single parent households (%)': 'EP_SNGPNT',
	'Speak English "less than well" (%)': 'EP_LIMENG',
	'Housing in structures with 10+ units (%)': 'EP_MUNIT',
	'Mobile homes (%)': 'EP_MOBILE',
	'Occupied housing units with more people than rooms (%)': 'EP_CROWD',
	'Households with no vehicle available (%)': 'EP_NOVEH',
	'Living in group quarters (%)': 'EP_GROUPQ',
	'No health insurance (%)': 'EP_UNINSUR'}

	y = 1
	map_list = []
	if svi:
		map_list.append('svi')
		y += 1
	if count:
		map_list.append('count')
		y += 1

	proj = gcrs.AlbersEqualArea(central_longitude=-90.199402, central_latitude=38.627003)

	fig, axarr = plt.subplots(1, y, figsize=(y*3, 5), subplot_kw={
	'projection': proj})

	if len(map_list) >= 1:
		for i, j in enumerate(map_list):
			if j == 'svi':
				gplt.choropleth(tract_geodf,
				hue=ses_var_dict[ses_var],
				cmap=Color,
				legend=True,
				ax=axarr[i],
				projection=proj)
				axarr[i].set_title(ses_var.title(), pad=20)
			if j == 'count':
				gplt.choropleth(tract_summary,
				hue='count',
				cmap=Color,
				legend=True,
				ax=axarr[i],
				projection=proj)
				axarr[i].set_title('Sample size per tract', pad=20)
		if scheme:
			scheme = mc.Quantiles(tract_summary.result, k=int(k_num))
			gplt.choropleth(tract_summary,
			hue='result',
			cmap=Color,
			legend=True,
			ax=axarr[y-1],
			scheme=scheme,
			projection=proj)	
			if title != None:
				axarr[y-1].set_title(title, pad=20)
		else:
			gplt.choropleth(tract_summary,
			hue='result',
			cmap=Color,
			legend=True,
			ax=axarr[y-1],
			projection=proj)	
			if title != None:
				axarr[y-1].set_title(title, pad=20)
	else:
		if scheme:
			scheme = mc.Quantiles(tract_summary.result, k=int(k_num))
			gplt.choropleth(tract_summary,
			hue='result',
			cmap=Color,
			legend=True,
			scheme=scheme,
			ax=axarr,
			projection=proj)	
			if title != None:
				axarr.set_title(title, pad=20)		
		else:
			gplt.choropleth(tract_summary,
			hue='result',
			cmap=Color,
			legend=True,
			ax=axarr,
			projection=proj)
			if title != None:
				axarr.set_title(title, pad=20)





