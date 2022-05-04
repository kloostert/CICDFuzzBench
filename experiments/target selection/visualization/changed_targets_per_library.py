#!/usr/bin/python3

import plotly.graph_objects as go

prefix = './targsel/'
logfiles = ['libpng-01.log', 'libpng-03.log', 'libsndfile-01.log', 'libtiff-02.log', 'libxml2-01.log', 'openssl-01.log', 'openssl-03.log', 'php-02.log', 'poppler-02.log', 
        'sqlite3-02.log', 'libpng-02.log', 'libpng-04.log', 'libtiff-01.log', 'libtiff-03.log', 'lua-01.log', 'openssl-02.log', 'php-01.log', 'poppler-01.log', 'sqlite3-01.log']
results = {'php': [], 'openssl': [], 'sqlite3': [], 'poppler': [], 'lua': [], 'libxml2': [], 'libsndfile': [], 'libpng': [], 'libtiff': []}

for logfile in logfiles:
    lib = logfile.split('-')[0]
    prev_eq = 0
    prev_tot = 0
    with open(f'{prefix}{logfile}', 'r') as logs:
        for line in logs:
            if 'iteration=' in line:
                split = line.split()
                equal = int(split[2].split('=')[1]) 
                total = int(split[3].split('=')[1])
                if total == 0 or total == prev_tot:
                    continue
                results[lib].append((equal - prev_eq) * 100 / (total - prev_tot))
                # print(f'{equal}\t{total}\t{equal - prev_eq}\t{total - prev_tot}\t{((equal - prev_eq) * 100 / (total - prev_tot))}%')
                prev_eq = equal
                prev_tot = total

fig = go.Figure()
for library in results:
    fig.add_trace(go.Box(name=library, y=results[library], marker_color='#3D9970', boxpoints="all"))
fig.update_layout(title='Identical fuzz targets per commit per library', xaxis_title='Library', yaxis_title='Percentage of identical fuzz targets', showlegend=False)
fig.show()
