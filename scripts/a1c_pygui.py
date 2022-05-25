import PySimpleGUI as sg 
import pandas as pd 
import a1c_mapping
import matplotlib.pyplot as plt

vals = ['Select']

cities = [
"St. Louis", 
"Chicago", 
"New York",
"Custom"
]

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
'Poverty rate',
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

layout = [[sg.Text('Select city:'), sg.Combo(cities, key='city', enable_events=True),
sg.FolderBrowse(button_text='Select Folder', disabled=True, key='city_dir', target='city_dir', enable_events=True),
sg.Text('', key='city_dir_text')], 
[sg.Checkbox('Include count map', key='count')],
[sg.Checkbox('Include SES map', key='svi', enable_events=True), sg.Text('Select SES variable:', key='svi_text'),
sg.Combo(ses_variables, key='ses', enable_events=True, disabled=True, size=(45, 10))],
[sg.Text('Map 1 data:'), sg.Input(key='browse', enable_events=True, visible=False), sg.FileBrowse(key='file1'),
sg.Text('', key='data_dir_text')],
[sg.Text('Select data type:'), sg.Radio('Numerical', group_id=1, visible=True, key='num', enable_events=True, disabled=True), 
sg.Radio('Categorical', group_id=1, visible=True, key='cat', enable_events=True, disabled=True)],
[sg.Text('Select numerical statistic:', key='stat_text_num', visible=True), 
sg.Listbox(statistics_num, visible=True, key='stat_menu_num', disabled=True, select_mode='LISTBOX_SELECT_MODE_SINGLE', enable_events=True, size=(10,3)), 
sg.Text('Select numerical statistic:', key='stat_text_cat', visible=True), 
sg.Listbox(statistics_cat, visible=True, key='stat_menu_cat', disabled=True, select_mode='LISTBOX_SELECT_MODE_SINGLE', enable_events=True, size=(12,3))], 
[sg.Text('Select constraints:', key='constraint_text', visible=True), 
sg.Listbox(comparators, visible=True, key='comparators1', disabled=True, select_mode='LISTBOX_SELECT_MODE_SINGLE', enable_events=True, size=(5,3)), 
sg.Input(key='constraint1', enable_events=True, disabled=True, size=(5, 3)), 
sg.Listbox(conditionals, key='conditional', enable_events=True, disabled=True, select_mode='LISTBOX_SELECT_MODE_SINGLE', size=(5,3)), 
sg.Listbox(comparators, visible=True, key='comparators2', disabled=True, select_mode='LISTBOX_SELECT_MODE_SINGLE', enable_events=True, size=(5,3)), 
sg.Input(key='constraint2', enable_events=True, disabled=True, size=(5, 3))],
[sg.Text('Select positive category:', visible=True, key='select_pos'), 
sg.OptionMenu(vals, key='pos_cat', visible=True, disabled=True), 
sg.Text('Select negative category:', visible=True, key='select_neg'), 
sg.OptionMenu(vals, key='neg_cat', visible=True, disabled=True)],
[sg.Text('Select numerical data type:', visible=True, key='choose_num'), 
sg.Radio('Continuous', group_id=2, enable_events=True, key='cont', visible=True, disabled=True), 
sg.Radio('Groups', group_id=2, enable_events=True, key='grps', visible=True, disabled=True)],
[sg.Text('Select # groups:', key='grp_text'), sg.Input(key='num_grps', disabled=True, size=(5,3), enable_events=True)],
[sg.Text('Select colormap:'), sg.OptionMenu(colors, key='color_menu'), 
sg.Text('Enter Title:'), sg.Input(key='title', size=(5, 3))],
[sg.Button(button_text='Generate map', key='gnrt_btn', enable_events=True)]]

window = sg.Window('Lab Mapper', layout)

current_comparator1 = []
current_comparator2 = []
current_conditional = []
while True:
	event, values = window.read()
	print(event, values)
	if event in (None, 'Cancel'):
		break
	if (event == 'browse' or event == 'city') and (values['file1'] != '' and values['city'] != ''):
		window['num'].update(disabled=False)
		window['cat'].update(disabled=False)
	if event == 'city' and values['city'] == 'Custom':
		window['city_dir'].update(disabled=False)
	if event == 'city' and values['city'] != 'Custom':
		window['city_dir'].update(disabled=True)
	if event =='browse' and values['browse'] != '':
		window['data_dir_text'].update(values['browse'])
	if event == 'city_dir' and values['city_dir'] != '':
		window['city_dir_text'].update(values['city_dir'])
	if event == 'svi' and values['svi'] == True:
		window['ses'].update(disabled=False)
	if event == 'svi' and values['svi'] == False:
		window['ses'].update(disabled=True)
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
			current_conditional = []
	if event == 'comparators2' and len(values['comparators2']) > 0:
		window['constraint2'].update(disabled=False)
		current_comparator2.append(values['comparators2'][0])
	if event == 'comparators2' and len(current_comparator2) > 1:
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
		df_data, tract_geodf = a1c_mapping.load_data(values['file1'], values['city'], svi=values['svi'], city_dir=values['city_dir'])
		df_tracts_merged = a1c_mapping.spatial_join(df_data, tract_geodf)
		tract_summary = a1c_mapping.calc_stats(df_tracts_merged, tract_geodf, stat_num=values['stat_menu_num'], 
			stat_cat=values['stat_menu_cat'], comparator1=values['comparators1'], comparator2=values['comparators2'], 
			conditional=values['conditional'], constraint1=values['constraint1'], constraint2=values['constraint2'],
			cat=values['cat'], num=values['num'], pos_cat=values['pos_cat'], neg_cat=values['neg_cat'])
		choropleth = a1c_mapping.create_choropleth(tract_summary, tract_geodf, values['color_menu'], 
			svi=values['svi'], count=values['count'], scheme=values['grps'], k_num=values['num_grps'],
			ses_var=values['ses'], title=values['title'])
		plt.show()

window.close()