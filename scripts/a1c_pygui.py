import PySimpleGUI as sg 
import pandas as pd 
import a1c_mapping
import matplotlib.pyplot as plt
import a1c_states

vals = ['Select']

statistics_num = [
'Median',
'Mean',
'Percentage'
]

statistics_cat = [
'Count',
'Rate'
]

colors = [
'red',
'green',
'blue']

comparators = [
'>',
'<',
'>=',
'<='
]

conditionals = [
'AND',
'OR']

ses_variables = [
'Social Vulnerability Index',
'Socioeconomic composite',
'Household composition composite',
'Minority status/Language composite',
'Housing type/Transportation composite',
'Population (Total)',
'Age 65+ (%)',
'Age 17 and younger (%)',
'Non-white persons (%)',
'Per capita income ($)',
'Poverty rate (%)',
'Unemployment rate (%)',
'No high school diploma (%)',
'With a disability (%)',
'Single parent households (%)',
'Speak English "less than well" (%)',
'Housing in structures with 10+ units (%)',
'Mobile homes (%)',
'Occupied housing units with more people than rooms (%)',
'Households with no vehicle available (%)',
'Living in group quarters (%)',
'No health insurance (%)']

fips_df = pd.read_csv('../svi/fips-by-state.csv', encoding = "utf-8")

a1c_states_list = []

layout = [[sg.Frame('', 
	[[sg.Input(key='geo_browse', enable_events=True, visible=False), 
	sg.Text('Select File for Geocoding:'), 
	sg.FileBrowse(key='geo_file'),
	sg.Button(button_text='Perform Geocoding', key='geo_btn')]])],
[sg.Frame('Select Geography', [[
	sg.Listbox(a1c_states.states, key='state_select', enable_events=True, size=(20,8)),
	sg.Listbox(a1c_states_list, key='county', disabled=True, size=(20,10))]])], 
[sg.Frame('Choose Map Characteristics', [[
	sg.Checkbox('Include count map', key='count'), 
	sg.Combo(ses_variables, key='ses', enable_events=True, size=(45, 10), default_value='Select SES Variable')],
	[sg.Text('Select colormap:'), 
	sg.OptionMenu(colors, key='color_menu'), 
	sg.Text('Enter Title:'), 
	sg.Input(key='title', size=(5, 3))]])],
[sg.Frame('Choose Map Data', [[
	sg.Text('Map 1 data:'), 
	sg.Input(key='browse', enable_events=True, visible=False), 
	sg.FileBrowse(key='file1'),
	sg.Text('Select data type:'),
	sg.Radio('Quantitative', group_id=1, visible=True, key='num', enable_events=True, disabled=True),
	sg.Radio('Qualitative', group_id=1, visible=True, key='cat', enable_events=True, disabled=True)]])],
[sg.Frame('Choose Quantitative Statistics', [[ 
	sg.Listbox(statistics_num, visible=True, key='stat_menu_num', disabled=True, select_mode='LISTBOX_SELECT_MODE_SINGLE', enable_events=True, size=(10,3)), 
	sg.Listbox(comparators, visible=True, key='comparators1', disabled=True, select_mode='LISTBOX_SELECT_MODE_SINGLE', enable_events=True, size=(5,3)), 
	sg.Input(key='constraint1', enable_events=True, disabled=True, size=(5, 3)), 
	sg.Listbox(conditionals, key='conditional', enable_events=True, disabled=True, select_mode='LISTBOX_SELECT_MODE_SINGLE', size=(5,3)), 
	sg.Listbox(comparators, visible=True, key='comparators2', disabled=True, select_mode='LISTBOX_SELECT_MODE_SINGLE', enable_events=True, size=(5,3)), 
	sg.Input(key='constraint2', enable_events=True, disabled=True, size=(5, 3))],
	[sg.Text('Data type:', visible=True, key='choose_num'),
	sg.Radio('Continuous', group_id=2, enable_events=True, key='cont', visible=True, disabled=True), 
	sg.Radio('Groups', group_id=2, enable_events=True, key='grps', visible=True, disabled=True),
	sg.Text('Select # groups:', key='grp_text'), 
	sg.Input(key='num_grps', disabled=True, size=(5,3), enable_events=True)]])],
[sg.Frame('Choose Qualitative Attributes', [[
	sg.Listbox(statistics_cat, visible=True, key='stat_menu_cat', disabled=True, select_mode='LISTBOX_SELECT_MODE_SINGLE', enable_events=True, size=(12,3)),
	sg.Text('Positive category:', visible=True, key='select_pos'), 
	sg.OptionMenu(vals, key='pos_cat', visible=True, disabled=True), 
	sg.Text('Negative category:', visible=True, key='select_neg'), 
	sg.OptionMenu(vals, key='neg_cat', visible=True, disabled=True),
	sg.Text('Select # groups:', key='grp_text'), sg.Input(key='num_grps', disabled=True, size=(5,3), enable_events=True)
	]])],
[sg.Button(button_text='Perform analysis', key='gnrt_btn', enable_events=True)]
]

window = sg.Window('LabMapper', layout)

current_comparator1 = []
current_comparator2 = []
current_conditional = []
while True:
	event, values = window.read()
	print(event, values)
	if event in (None, 'Cancel'):
		break
	if event == 'geo_btn':
		geo_file = a1c_mapping.perform_geocoding(values['geo_file'])
	if (event == 'browse' or event == 'county') and (values['file1'] != '' and values['county'] != ''):
		window['num'].update(disabled=False)
		window['cat'].update(disabled=False)
	if event == 'state_select':
		state_abbrev = a1c_states.state_abbrev_dict[values['state_select'][0]]
		county_list = fips_df[fips_df['state'] == state_abbrev]['name'].to_list()
		window['county'].update(county_list, disabled=False)
	if values['num'] == True and values['cat'] == False:
		window['stat_menu_num'].update(disabled=False)
		window['cont'].update(disabled=False)
		window['grps'].update(disabled=False)
		window['pos_cat'].update(disabled=True)
		window['neg_cat'].update(disabled=True)
		window['stat_menu_cat'].update(disabled=True)
	if event == 'stat_menu_num' and values['stat_menu_num'][0] == 'Percentage':
		window['comparators1'].update(disabled=False)
	if event == 'comparators1' and len(values['comparators1']) > 0:
		window['constraint1'].update(disabled=False)
		current_comparator1.append(values['comparators1'][0])
	if event == 'constraint1' and values['constraint1'].isdigit() == True:
		window['conditional'].update(disabled=False)
	if event == 'comparators1' and len(current_comparator1) > 1:
		if values['comparators1'][0] == current_comparator1[-2]:
			window['comparators1'].update(set_to_index=[])
			values['comparators1'] = []
			current_comparator1 = []
	if event == 'conditional':
		window['comparators2'].update(disabled=False)
		current_conditional.append(values['conditional'])
	if event == 'conditional' and len(current_conditional) > 1:
		if values['conditional'] == current_conditional[-2]:
			window['conditional'].update(set_to_index=[])
			values['conditional'] = []
			values['comparators2'] = []
			window['comparators2'].update(set_to_index=[])
			current_conditional = []
			current_comparator2 = []
	if event == 'comparators2' and len(values['comparators2']) > 0:
		window['constraint2'].update(disabled=False)
		current_comparator2.append(values['comparators2'][0])
	if event == 'comparators2' and len(current_comparator2) > 1:
		print(current_comparator2)
		if values['comparators2'][0] == current_comparator2[-2]:
			window['comparators2'].update(set_to_index=[])
			values['comparators2'] = []
			current_comparator2 = []
	if event == 'cat' and values['cat'] == True and values['num'] == False:
		df = pd.read_csv(values['file1'])
		vals = df.result.unique()
		window['pos_cat'].update(values=vals, disabled=False)
		window['neg_cat'].update(values=vals, disabled=False)
		window['stat_menu_cat'].update(disabled=False)

		window['cont'].update(False, disabled=True)
		window['grps'].update(False, disabled=True)
		window['stat_menu_num'].update(disabled=True)
		window['comparators1'].update(set_to_index=[])
		window['comparators2'].update(set_to_index=[])
		window['conditional'].update(set_to_index=[])
	if values['cont'] == True:
		# window['stat_text'].update(disabled=False)
		window['stat_menu_num'].update(disabled=False)
		window['num_grps'].update(disabled=True)
	if values['grps'] == True:
		window['num_grps'].update(disabled=False)
	if event == 'gnrt_btn':
		if values['browse'] != '':
			df_data, tract_geodf = a1c_mapping.load_data(fips_df, state=values['state_select'][0], county=values['county'][0], data_path=values['file1'])
			df_tracts_merged = a1c_mapping.spatial_join(df_data, tract_geodf)
			tract_summary = a1c_mapping.calc_stats(df_tracts_merged, tract_geodf, stat_num=values['stat_menu_num'], 
				stat_cat=values['stat_menu_cat'], comparator1=values['comparators1'], comparator2=values['comparators2'], 
				conditional=values['conditional'], constraint1=values['constraint1'], constraint2=values['constraint2'],
				cat=values['cat'], num=values['num'], pos_cat=values['pos_cat'], neg_cat=values['neg_cat'])
			choropleth = a1c_mapping.create_choropleth(tract_geodf, values['color_menu'], values['ses'],
				count=values['count'], grps=values['grps'], k_num=values['num_grps'],
				title=values['title'], tract_summary=tract_summary)
		elif values['browse'] == '':
			tract_geodf = a1c_mapping.load_data(fips_df, state=values['state_select'][0], county=values['county'][0], data_path=None)
			choropleth = a1c_mapping.create_choropleth(tract_geodf, values['color_menu'], values['ses'],
			count=values['count'], grps=values['grps'], k_num=values['num_grps'],
			title=values['title'], tract_summary=None)
		plt.show()

window.close()