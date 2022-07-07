import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import geoplot as gplt 
import geoplot.crs as gcrs 
import mapclassify as mc
import statistics as stats
import os
import docker
import a1c_states

def perform_geocoding(geo_path):

	os.system("docker run --rm -v " + '/'.join(os.getcwd().split('/')[:-1]) + ":/tmp " +  "degauss/geocoder:3.0.2 " + geo_path.split('/')[-1])

def load_data(fips_df, state=None, county=None, data_path=None):

	state_abbrev = a1c_states.state_abbrev_dict[state]
	fips = fips_df[(fips_df['name'] == county) & (fips_df['state'] == state_abbrev)]['fips'].values[0]
	if ' ' not in state:
		svi_path = '../svi/' + state + '/SVI2018_' + state.upper() + '_tract.shp'
	elif ' ' in state:
		svi_path = '../svi/' + state + '/SVI2018_' + state.split(' ')[0].upper() + state.split(' ')[1].upper() + '_tract.shp'

	tract_geodf = gpd.read_file(svi_path)
	tract_geodf['STCNTY'] = tract_geodf['STCNTY'].astype(int)
	tract_geodf_county = tract_geodf[tract_geodf['STCNTY'] == fips]

	if data_path != None:
		df_data = pd.read_csv(data_path)
		return(df_data, tract_geodf_county)
	else:
		return(tract_geodf_county)


## returns dataframe with census tract for each sample
def spatial_join(df_data, tract_geodf):
    
    gdf = gpd.GeoDataFrame(
    df_data, geometry=gpd.points_from_xy(df_data.lon, df_data.lat)
    )
    gdf.crs = 'epsg:4326'
    gdf = gdf.to_crs('epsg:4269')
    df_tracts_merged = gpd.sjoin(gdf, tract_geodf, how="inner", op="within")

    return(df_tracts_merged)

## returns dataframe of stats for each census tract 
def calc_stats(df_tracts_merged, tract_geodf, stat_num=None, stat_cat=None, comparator1=None, 
	comparator2=None, constraint1=None, constraint2=None, conditional=None, 
	cat=False, num=False, pos_cat=None, neg_cat=None):
    
	if num == True:
		df_tracts_merged.result = pd.to_numeric(df_tracts_merged.result, errors='coerce')
		df_tracts_merged = df_tracts_merged[df_tracts_merged['result'].notna()]
		tract_summary = pd.DataFrame(columns=['FIPS', 'result', 'count'])
		grouped = df_tracts_merged.groupby('FIPS')
		for name, group in grouped:
			count = len(group)
			if stat_num[0] == 'Median':
				median = stats.median(group['result'])
				tract_summary = tract_summary.append({'FIPS': name, 'result': median, 'count': count}, ignore_index=True)
			elif stat_num[0] == 'Mean':
				mean = stats.median(group['result'])
				tract_summary = tract_summary.append({'FIPS': name, 'result': mean, 'count': count}, ignore_index=True)
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

				tract_summary = tract_summary.append({'FIPS': name, 'result': percentage, 'count': count}, ignore_index=True)
		# tract_summary = pd.merge(tract_summary, tract_geodf, on='FIPS')

	elif cat == True:
		tract_summary = pd.DataFrame(columns=['FIPS', 'result', 'count'])
		grouped = df_tracts_merged.groupby('FIPS')
		for name, group in grouped:
			count = len(group)
			if stat_cat[0] == 'Count':
				pos_count = len(group[group['result'] == pos_cat])
				tract_summary = tract_summary.append({'FIPS': name, 'result': pos_count, 'count': count}, ignore_index=True)
			elif stat_cat[0] == 'Rate':
				rate = len(group[group['result'] == pos_cat])/(len(group[group['result'] == pos_cat])+len(group[group['result'] == neg_cat]))
				tract_summary = tract_summary.append({'FIPS': name, 'result': rate, 'count': count}, ignore_index=True)

		# tract_summary = pd.merge(tract_summary, tract_geodf, on='FIPS')
	return(tract_summary)


def create_choropleth(tract_geodf, color, ses_var, count=False, grps=False, k_num=None, title=None, tract_summary=None):

	if tract_summary is not None:
		tract_summary = pd.merge(tract_summary, tract_geodf, on='FIPS')
		tract_summary = gpd.GeoDataFrame(tract_summary, geometry='geometry')
		tract_summary.result = pd.to_numeric(tract_summary.result, errors='ignore')
		tract_summary['count'] = pd.to_numeric(tract_summary['count'], errors='ignore')
	# print(tract_summary)

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
	'Poverty rate (%)': 'EP_POV',
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

	if ses_var != "Select SES Variable":
		tract_geodf.loc[tract_geodf[ses_var_dict[ses_var]] < 0, ses_var_dict[ses_var]] = tract_geodf[ses_var_dict[ses_var]].median()

	y = 0
	map_tracker = []
	if ses_var != "Select SES Variable":
		y += 1
		map_tracker.append('svi')
	if count:
		y += 1
		map_tracker.append('count')
	if tract_summary is not None:
		y += 1
		map_tracker.append('tract')
	longitude = tract_geodf.to_crs('+proj=cea').dissolve().centroid.to_crs(tract_geodf.crs).x[0]
	latitude = tract_geodf.to_crs('+proj=cea').dissolve().centroid.to_crs(tract_geodf.crs).y[0]

	proj = gcrs.AlbersEqualArea(central_longitude=longitude, central_latitude=latitude)

	fig, axarr = plt.subplots(1, y, figsize=(y*3, 5), subplot_kw={
	'projection': proj}, sharex=True, sharey=True)

	for i, j in enumerate(map_tracker):
		if len(map_tracker) > 1:
			axarr[i].format_coord = lambda x, y: ""
			if grps == False:
				if j =='svi':
					gplt.choropleth(tract_geodf,
					hue=ses_var_dict[ses_var],
					cmap=Color,
					legend=True,
					ax=axarr[i],
					projection=proj,
					legend_kwargs={'pad':0.03,
					'shrink':0.8,
                             'orientation':'horizontal'})
					axarr[i].set_title(ses_var.title(), pad=10)
				if j == 'count':
					gplt.choropleth(tract_summary,
					hue='count',
					cmap=Color,
					legend=True,
					ax=axarr[i],
					projection=proj,
					legend_kwargs={'pad':0.03,
					'shrink':0.8,
                             'orientation':'horizontal'})
					axarr[i].set_title('Sample size per tract', pad=10)
				if j == 'tract':
					gplt.choropleth(tract_summary,
					hue='result',
					cmap=Color,
					legend=True,
					ax=axarr[i],
					projection=proj,
					legend_kwargs={'pad':0.03,
					'shrink':0.8,
                             'orientation':'horizontal'})
					axarr[i].set_title(title, pad=10)
			elif grps == True:
				scheme = mc.Quantiles(tract_summary.result, k=int(k_num))
				cont_labels = []
				for s in scheme.get_legend_classes():
				    upper = s.split('.')[2].split(']')[0]
				    lower = s.split('.')[1].split(',')[0]
				    cont_labels.append(str(int(lower)) + '-' + str(int(upper)) +'%')
				if j =='svi':
					gplt.choropleth(tract_geodf,
					hue=ses_var_dict[ses_var],
					cmap=Color,
					legend=True,
					ax=axarr[i],
					projection=proj,
					legend_kwargs={'pad':0.03,
					'shrink':0.8,
                             'orientation':'horizontal'})
					axarr[i].set_title(ses_var.title(), pad=10)
				if j == 'count':
					gplt.choropleth(tract_summary,
					hue='count',
					cmap=Color,
					legend=True,
					ax=axarr[i],
					projection=proj)
					axarr[i].set_title('Sample size per tract', pad=10)
				if j == 'tract':
					gplt.choropleth(tract_summary,
					hue='result',
					cmap=Color,
					legend=True,
					ax=axarr[i],
					scheme=scheme,
					legend_kwargs={'loc': 'upper left'},
					legend_labels=cont_labels,
					projection=proj)
					axarr[i].set_title(title, pad=10)

		elif len(map_tracker) == 1:
			axarr.format_coord = lambda x, y: ""
			if grps == False:
				if j =='svi':
					gplt.choropleth(tract_geodf,
					hue=ses_var_dict[ses_var],
					cmap=Color,
					legend=True,
					ax=axarr,
					projection=proj,
					legend_kwargs={'pad':0.03,
					'shrink':0.8,
                             'orientation':'horizontal'})
					axarr.set_title(ses_var.title(), pad=10)
				if j == 'count':
					gplt.choropleth(tract_summary,
					hue='count',
					cmap=Color,
					legend=True,
					ax=axarr,
					projection=proj,
					legend_kwargs={'pad':0.03,
					'shrink':0.8,
                             'orientation':'horizontal'})
					axarr.set_title('Sample size per tract', pad=10)
				if j == 'tract':
					gplt.choropleth(tract_summary,
					hue='result',
					cmap=Color,
					legend=True,
					ax=axarr,
					projection=proj,
					legend_kwargs={'pad':0.03,
					'shrink':0.8,
                             'orientation':'horizontal'})
					axarr.set_title(title, pad=10)
			elif grps == True:
				scheme = mc.Quantiles(tract_summary.result, k=int(k_num))
				cont_labels = []
				for s in scheme.get_legend_classes():
				    upper = s.split('.')[2].split(']')[0]
				    lower = s.split('.')[1].split(',')[0]
				    cont_labels.append(str(int(lower)) + '-' + str(int(upper)) +'%')
				if j =='svi':
					gplt.choropleth(tract_geodf,
					hue=ses_var_dict[ses_var],
					cmap=Color,
					legend=True,
					ax=axarr,
					projection=proj,
					legend_kwargs={'pad':0.03,
					'shrink':0.8,
                             'orientation':'horizontal'})
					axarr.set_title(ses_var.title(), pad=10)
				if j == 'count':
					gplt.choropleth(tract_summary,
					hue='count',
					cmap=Color,
					legend=True,
					ax=axarr,
					projection=proj,
					legend_kwargs={'pad':0.03,
					'shrink':0.8,
                             'orientation':'horizontal'})
					axarr.set_title('Sample size per tract', pad=10)
				if j == 'tract':
					gplt.choropleth(tract_summary,
					hue='result',
					cmap=Color,
					legend=True,
					ax=axarr,
					scheme=scheme,
					legend_labels=cont_labels,
					projection=proj,
					legend_kwargs={'loc': 'upper left'})
					axarr.set_title(title, pad=10)				
	plt.show(block=False)





