
for fs in df['filt_slope'].unique():
    idx = (df['filt_slope'] == fs)
    plt.plot(df.loc[idx]['freq'], df.loc[idx]['disp_val'],
        marker = '*',
        label = 'Filt. slope = {}'.format(fs))
plt.legend()
# metadata
header['start']
header['stop']

# view the baseline data (i.e. configuration values)
h = db[-1]
h.table('baseline')