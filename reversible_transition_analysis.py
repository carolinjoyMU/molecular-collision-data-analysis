import pandas as pd
import matplotlib.pyplot as plt

# Read the data file and parse the contents
f = open('CS_op_J0_U170_alltrans_final.DAT', "r")
lines = f.readlines()
df_list = []
lineN = []

for line in lines:
    line_split = line.split()
    # Check if the line is a header
    if len(line_split) > 2 and line_split[0] == 'ilv' and line_split[1] == 'flv':
        # Determine the column names based on the header
        if 'sigma(U),ANG^2' in line:
            column_names = ['ilv', 'flv', 'sigma(U),ANG^2', 'E_coll(cm^-1)', 'sigma(E_coll),ANG^2']
        elif 'E_coll,cm^-1' in line and 'monte_carlo_error,%' in line:
            column_names = ['ilv', 'flv', 'E_coll(cm^-1)', 'sigma(E_coll),ANG^2', 'monte_carlo_error,%']
        elif 'E_coll(cm^-1)' in line:
            column_names = ['ilv', 'flv', 'E_coll(cm^-1)', 'sigma(E_coll),ANG^2']
        else:
            print("Header not found")
            continue

    elif len(line_split) > 0 and line_split[0].isdigit():
        lineN.append(list(map(float, line_split)))

    # If we reach the end of a section, create a new DataFrame and append it to the list
    if line.strip() == '':
        if lineN:
            df = pd.DataFrame(lineN, columns=column_names)
            df_list.append(df)
        lineN = []

# Find U value from the first line
U = float(lines[0].split()[1])
# print(U)

# Concatenate all DataFrames in the list to create a single DataFrame (df_raw)
if df_list:
    df_raw = pd.concat(df_list, ignore_index=True)
else:
    print("No data found in the file.")

# Read user input check file
def get_user_input_check(frm_state, to_state):
    f = open('UIP_op.DAT', 'r') 
    lines = f.readlines()

    frm_input = []
    to_input = []
    for line in lines:
        lineS = line.split()
        if len(lineS) > 0 and lineS[0].isdigit():
                if int(lineS[0]) == frm_state:
                    frm_input = list(map(float, lineS))
                if int(lineS[0]) == to_state:
                    to_input = list(map(float, lineS))
    return frm_input, to_input

# Create a desired DataFrame with states of H2O and H2 and the cross-sections
j1_f = []
ka_f = []
kc_f = []
j2_f = []
j1_t = [] 
ka_t = []
kc_t = []
j2_t = []
E_ilv = []
E_flv = []
diff = []
DelE = []
DelJ1 = []
DelJ2 = []
for index, row in df_raw.iterrows():
    frm_input, to_input = get_user_input_check(row['ilv'],row['flv'])
    j1_f.append(frm_input[1])
    ka_f.append(frm_input[2])
    kc_f.append(frm_input[3])
    j2_f.append(frm_input[4]) 
    E_ilv.append(frm_input[-1]) 
    j1_t.append(to_input[1])
    ka_t.append(to_input[2])
    kc_t.append(to_input[3])
    j2_t.append(to_input[4])
    E_flv.append(to_input[-1])  
    DelE.append(to_input[-1] - frm_input[-1])
    DelJ1.append(to_input[1] - frm_input[1])
    DelJ2.append(to_input[4] - frm_input[4])

# Write the data to the DataFrame
df_raw['j1_f'] = j1_f
df_raw['ka_f'] = ka_f
df_raw['kc_f'] = kc_f
df_raw['j2_f'] = j2_f
df_raw['DelJ1'] = DelJ1
df_raw['DelE'] = DelE
df_raw['DelJ2'] = DelJ2
df_raw['E_flv'] = E_flv 
df_raw['sigma(U),ANG^2'] = df_raw['sigma(E_coll),ANG^2']*(df_raw['E_coll(cm^-1)']/U)
df_raw['j1_t'] = j1_t
df_raw['ka_t'] = ka_t
df_raw['kc_t'] = kc_t
df_raw['j2_t'] = j2_t 
df_raw['E_ilv'] = E_ilv 

for f, t in zip(j2_f, j2_t):
    diff.append(abs(f - t)) 
df_raw['DelJ2'] = diff

# Remove rows where j1_f, ka_f, and kc_f are equal to j1_t, ka_t, and kc_t respectively; we don't need the elastic transitions
index =  df_raw[ ((df_raw['j1_f'] == df_raw['j1_t']) &
             (df_raw['ka_f'] == df_raw['ka_t']) &
              (df_raw['kc_f'] == df_raw['kc_t'])) ].index
df_raw.drop(index,inplace=True)

# Reset index after dropping rows
df_raw.reset_index(drop=True, inplace=True) 

# Find the reversible transitions
matched_idxs = set()
result_data = []

for idx, row in df_raw.iterrows():
    if idx in matched_idxs:
        continue
    
    data = df_raw.loc[(df_raw['ilv'] == row['flv']) & (df_raw['flv'] == row['ilv'])]
    if not data.empty:
        matched_idxs.add(data.index[0])

        x = ((2 * row['j1_f']) + 1) * ((2 * row['j2_f']) + 1) * row['sigma(U),ANG^2']
        y = ((2 * row['j1_t']) + 1) * ((2 * row['j2_t']) + 1) * data['sigma(U),ANG^2'].iloc[0]

        Sigma_tilda = (x + y) / 2
        sig_til_ex = Sigma_tilda / ((2 * row['j1_f']) + 1) * ((2 * row['j2_f']) + 1)
        sig_qu_til = Sigma_tilda / ((2 * row['j1_t']) + 1) * ((2 * row['j2_t']) + 1)

        result_data.append({
            'R_j1_f': row['j1_f'],
            'R_Ka_f': row['ka_f'],
            'R_Kc_f': row['kc_f'],
            'R_j2_f': row['j2_f'],
            'R_j1_t': row['j1_t'],
            'R_Ka_t': row['ka_t'],
            'R_Kc_t': row['kc_t'],
            'R_j2_t': row['j2_t'],
            'E_ini_R': row['E_ilv'],
            'E_fin_R': row['E_flv'],
            'DelE_R': row['DelE'],
            'DelJ1_R': row['DelJ1'],
            'DelJ2_R': row['DelJ2'],
            'X': x,
            'Y': y,
            'sig_ex': sig_til_ex,
            'sig_qu': sig_qu_til,
        })

# Create a DataFrame from the result_data list
result_df = pd.DataFrame(result_data)      

# Get the unique DelJ2 values
DelJ2_range = result_df['DelJ2_R'].drop_duplicates()
# print(DelJ2_range) 

# Find reversible transitions and save to an Excel file
matched_idxs = []
rows = []
df_match = pd.DataFrame(columns=df_raw.columns) 

for idx, row in df_raw.iterrows():
    if idx in matched_idxs:
        continue 
    data = df_raw.loc[(
        (df_raw['ilv'] == row['flv']) & 
        (df_raw['flv'] == row['ilv'])
        )]
    rows.append(data)

df_data = pd.concat(rows)
df_data.to_excel(fr'Rev_trans_excel/rev_transitions.xlsx', index=False)

# Plot reversible transitions for each DelJ2 value
# User can input the desired DelJ2 value to plot
unique_delJ2_values = [0, 2, 4] 
plt.figure(figsize=(5, 5), dpi=300) 
ax = plt.gca()
matched_idxs = []

# Create a dictionary to store data for each DelJ2 value
data_dict = {delj2: {'X': [], 'Y': []} for delj2 in unique_delJ2_values}

for idx, row in df_raw.iterrows():
    delj2 = row['DelJ2']

    # Skip if there is no matching data
    if delj2 not in data_dict:
        continue

    if idx in matched_idxs: 
        continue 

    data = df_raw.loc[(
        (df_raw['ilv'] == row['flv']) & 
        (df_raw['flv'] == row['ilv'])
        )]
    if data.size != 0:
        matched_idxs.append(data.index[0])
        x = ((2 * row['j1_f']) + 1) * ((2 * row['j2_f']) + 1) * row['sigma(U),ANG^2']
        y = ((2 * row['j1_t']) + 1) * ((2 * row['j2_t']) + 1) * data['sigma(U),ANG^2'].values[0]
        data_dict[delj2]['X'].append(x)
        data_dict[delj2]['Y'].append(y)

marker_styles = ['o', 'o', 'o']
marker_sizes = [10, 10, 10]
face_colors = ['darkblue', 'none', 'none']
lws = [0.5, 0.5, 0.5]
colors = ['darkblue', 'r', 'g']

# Iterate through unique DelJ2 values and plot data
for i, delj2 in enumerate(unique_delJ2_values):
    X = data_dict[delj2]['X']
    Y = data_dict[delj2]['Y']

    color = colors[i]
    marker = marker_styles[i]
    marker_size = marker_sizes[i]
    face_color = face_colors[i]
    lw = lws[i]
    ax.scatter(X, Y, edgecolors=color, facecolors=face_color, marker=marker, linewidths=lw, s=marker_size, label=f'$\Delta\ J_2 = \pm{delj2}$')  

    # Add reference lines, set scales, and axis limits
    ax.plot([1E-12, 1000], [1E-12, 1000], color='r', linestyle='--',linewidth=0.70)
    ax.plot([1E-12, 1000], [5E-13, 500],  color='r', linestyle='--',linewidth=0.70)
    ax.plot([1E-12, 1000], [2E-12, 2000], color='r', linestyle='--',linewidth=0.70)    
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.xaxis.set_minor_locator(plt.LogLocator(base=10.0, subs=(0.2, 0.4, 0.6, 0.8), numticks=20))
    ax.yaxis.set_minor_locator(plt.LogLocator(base=10.0, subs=(0.2, 0.4, 0.6, 0.8), numticks=20))
    ax.tick_params(which='both', axis='both', direction='in')  
    ax.set_xlim([1E-10, 1000])
    ax.set_ylim([1E-10, 1000])

    # Add a legend to label the different DelJ2 values
    ax.legend()
    ax.legend(frameon=False)
    ax.set_aspect('equal')

plt.show() 
