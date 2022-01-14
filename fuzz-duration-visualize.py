import json

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

PREFIX = '/srv'

# /// Experiment runs of 6 durations x 5 iterations, with seed corpora. ///
RESULT_DIR = '../results/libxml2/artificial/'
DURATIONS = ['5m', '10m', '15m', '20m', '30m', '45m', '60m']
RUNS =  [x + 1 for x in range(len(DURATIONS))]
START = [x for x in range(60, 91, 5)]
STOP =  [x for x in range(64, 96, 5)]

# /// Original experiment runs from the thesis. ///
# RUNS = [8, 9, 10, 1, 2, 3, 4, 7, 12, 13, 6, 5, 11]
# DURATIONS = ['1m (run 8)', '1m (run 9)', '5m (run 10)', '10m (run 1)', '10m (run 2)', '15m (run 3)', '20m (run 4)',
#              '30m (run 7)', '1h (run 12)', '8h (run 13)', '12h (run 6)', '12h (run 5)', '48h (run 11)']
# START = [409, 423, 470, 74, 144, 226, 308, 369, 489, 502, 361, 350, 483]
# STOP = [413, 451, 477, 109, 224, 306, 346, 398, 500, 506, 367, 353, 484]

# /// Experiment runs of 8x5 iterations, without seed corpora. ///
# RUNS = [1, 2, 3, 4, 5, 6, 7, 8]
# DURATIONS = ['1m', '5m', '10m', '15m', '20m', '30m', '1h', '8h']
# START = [513, 518, 523, 528, 533, 538, 543, 548]
# STOP = [517, 522, 527, 532, 537, 542, 547, 552]

# /// Experiment runs of 8x5 iterations, with seed corpora. ///
# RUNS = [1, 2, 3, 4, 5, 6, 7, 8]
# DURATIONS = ['1m', '5m', '10m', '15m', '20m', '30m', '1h', '8h']
# START = [593, 598, 603, 608, 613, 618, 623, 628]
# STOP = [597, 602, 607, 612, 617, 622, 627, 632]


def coverage_results(start_dir, stop_dir):
    with open(f'{PREFIX}/results/example/coverage_results', 'r') as file:
        data = json.load(file)
        for fuzzer in data:
            for target in data[fuzzer]:
                for metric in data[fuzzer][target]:
                    if fuzzer == 'libfuzzer':
                        for submetric in data[fuzzer][target][metric]:
                            data[fuzzer][target][metric][submetric] = []
                    else:
                        data[fuzzer][target][metric] = []

    for i in range(start_dir, stop_dir + 1):
        with open(f'{RESULT_DIR}{i:04d}/coverage_results', 'r') as file:
            new = json.load(file)
            for fuzzer in data:
                for target in data[fuzzer]:
                    for metric in data[fuzzer][target]:
                        if fuzzer == 'libfuzzer':
                            for submetric in data[fuzzer][target][metric]:
                                try:
                                    data[fuzzer][target][metric][submetric].append(
                                        new[fuzzer][target][metric][submetric])
                                except:
                                    data[fuzzer][target][metric][submetric].append(None)
                        else:
                            try:
                                data[fuzzer][target][metric].append(new[fuzzer][target][metric])
                            except:
                                data[fuzzer][target][metric].append(None)

    for fuzzer in data:
        if fuzzer == 'libfuzzer':
            for metric in data['libfuzzer']['openssl-client']['stop']:
                res = {}
                for target in data[fuzzer]:
                    res[target] = data[fuzzer][target]['stop'][metric]
                df = pd.DataFrame.from_dict(res, dtype=float)
                fig = px.line(df, title=f'{fuzzer} - {metric} over time')
                fig.show()
        else:
            for metric in data[fuzzer]['openssl-client']:
                res = {}
                for target in data[fuzzer]:
                    res[target] = data[fuzzer][target][metric]
                df = pd.DataFrame.from_dict(res, dtype=float)
                fig = px.line(df, title=f'{fuzzer} - {metric} over time')
                fig.show()


def bugs_found(start_dir, stop_dir):
    fuzzers = []
    res = {'active_bugs': []}
    overall_res = {'active': [], 'reached': [], 'triggered': [], 'detected': []}
    with open(f'{PREFIX}/results/example/coverage_results', 'r') as file:
        data = json.load(file)
        for fuzzer in data:
            fuzzers.append(fuzzer)
            res[fuzzer] = {}

    for i in range(start_dir, stop_dir + 1):
        bug_codes = {'reached': [], 'triggered': [], 'detected': []}
        with open(f'{RESULT_DIR}{i:04d}/bug_status', 'r') as file:
            bug_status = json.load(file)
            res['active_bugs'].append(bug_status['nr_active_bugs'])
            overall_res['active'].append(bug_status['nr_active_bugs'])

        with open(f'{RESULT_DIR}{i:04d}/final_results', 'r') as file:
            results = json.load(file)
            for status in results:
                for fuzzer in fuzzers:
                    if status not in res[fuzzer]:
                        res[fuzzer][status] = []
                    if fuzzer in results[status]:
                        res[fuzzer][status].append(len(results[status][fuzzer]))
                        for bug in results[status][fuzzer]:
                            bug_codes[status].append(bug)
                    else:
                        res[fuzzer][status].append(0)

        for status in bug_codes:
            overall_res[status].append(len(set(bug_codes[status])))

    for fuzzer in fuzzers:
        plot_data = res[fuzzer]
        plot_data['active'] = res['active_bugs']
        df = pd.DataFrame.from_dict(plot_data, dtype=float)
        fig = px.line(df, title=f'Bug status for {fuzzer} over time')
        fig.show()

    df = pd.DataFrame.from_dict(overall_res, dtype=float)
    fig = px.line(df, title=f'Bug status for all fuzzers over time')
    fig.show()

    new_overall = {'reached': [], 'triggered': [], 'detected': []}
    for i in range(start_dir, stop_dir + 1):
        for status in new_overall:
            new_overall[status].append(overall_res[status][i - start_dir] / overall_res['active'][i - start_dir] * 100)
    df = pd.DataFrame.from_dict(new_overall, dtype=float)
    fig = px.line(df, title=f'Percentage of bugs reached, triggered and detected for all fuzzers over time')
    fig.update_layout(xaxis_title='Time (commit number)', yaxis_title='Percentage of bugs (%)',
                      legend_title='Bug status')
    fig.show()


def nr_crashes(start_dir, stop_dir):
    plot_data = {'overall': []}
    for i in range(start_dir, stop_dir + 1):
        target_crashes = {}
        total_crashes = 0
        with open(f'{RESULT_DIR}{i:04d}/nr_crashes', 'r') as file:
            crashes = json.load(file)
            for fuzzer in crashes:
                for target in crashes[fuzzer]:
                    if target not in target_crashes:
                        target_crashes[target] = crashes[fuzzer][target]
                    else:
                        target_crashes[target] = target_crashes[target] + crashes[fuzzer][target]
        for target in crashes[fuzzer]:
            if target not in plot_data:
                plot_data[target] = []
            plot_data[target].append(target_crashes[target])
            total_crashes += target_crashes[target]
        plot_data['overall'].append(total_crashes)

    df = pd.DataFrame.from_dict(plot_data, dtype=float)
    fig = px.line(df, title=f'Number of crashes per fuzz target for all fuzzers over time')
    fig.update_layout(xaxis_title='Time (commit number)', yaxis_title='Number of crashes',
                      legend_title='Fuzz target')
    fig.show()


def box_fuzz_dur_crashes():
    fig = go.Figure()
    for i in range(len(START)):
        crashes = []
        for j in range(START[i], STOP[i] + 1):
            with open(f'{RESULT_DIR}{j:04d}/nr_crashes', 'r') as file:
                data = json.load(file)
            count = 0
            for fuzzer in data:
                for target in data[fuzzer]:
                    count += data[fuzzer][target]
            crashes.append(count)
        fig.add_trace(go.Box(name=f'Run {RUNS[i]}', y=crashes, x0=DURATIONS[i], marker_color='#3D9970'))
    fig.update_yaxes(type='log')
    fig.update_layout(xaxis_title='Fuzz duration', yaxis_title='Number of crashes')
    fig.show()


def box_fuzz_dur_bugs():
    fig = go.Figure()
    bugs = {'reached': [], 'triggered': [], 'detected': [], 'x': []}
    for i in range(len(START)):
        for j in range(START[i], STOP[i] + 1):
            count = {'reached': [], 'triggered': [], 'detected': []}
            with open(f'{RESULT_DIR}{j:04d}/final_results', 'r') as file:
                data = json.load(file)
            for metric in data:
                for fuzzer in data[metric]:
                    count[metric] = [*count[metric], *data[metric][fuzzer]]
                bugs[metric].append(len(set(count[metric])))
            bugs['x'].append(DURATIONS[i])
    fig.add_trace(go.Box(name='reached', y=bugs['reached'], x=bugs['x'], marker_color='#FF4136'))
    fig.add_trace(go.Box(name='triggered', y=bugs['triggered'], x=bugs['x'], marker_color='#FF851B'))
    fig.add_trace(go.Box(name='detected', y=bugs['detected'], x=bugs['x'], marker_color='#3D9970'))
    fig.update_layout(xaxis_title='Fuzz duration', yaxis_title='Number of bugs', boxmode='group')
    fig.show()


def box_fuzz_dur_bug_time():
    fig = go.Figure()
    bugs = {'reached': [], 'triggered': [], 'xreached': [], 'xtriggered': []}
    for i in range(len(START)):
        for j in range(START[i], STOP[i] + 1):
            with open(f'{RESULT_DIR}{j:04d}/benchd_results', 'r') as file:
                data = json.load(file)
            for fuzzer in data['results']:
                for program in data['results'][fuzzer]:
                    for target in data['results'][fuzzer][program]:
                        for run in data['results'][fuzzer][program][target]:
                            for metric in data['results'][fuzzer][program][target][run]:
                                for bug in data['results'][fuzzer][program][target][run][metric]:
                                    bugs[metric].append(data['results'][fuzzer][program][target][run][metric][bug])
                                    bugs[f'x{metric}'].append(DURATIONS[i])
    fig.add_trace(go.Box(name='reached', y=bugs['reached'], x=bugs['xreached'], marker_color='#FF4136'))
    fig.add_trace(go.Box(name='triggered', y=bugs['triggered'], x=bugs['xtriggered'], marker_color='#FF851B'))
    fig.update_yaxes(type='log')
    fig.update_layout(xaxis_title='Fuzz duration', yaxis_title='Time to bug (seconds)', boxmode='group')
    fig.show()


def box_fuzz_dur_coverage():
    fig = go.Figure()
    coverage = {'aflplusplus': [], 'honggfuzz': [], 'libfuzzer': [], 'xaflplusplus': [], 'xhonggfuzz': [],
                'xlibfuzzer': []}
    for i in range(len(START)):
        for j in range(START[i], STOP[i] + 1):
            with open(f'{RESULT_DIR}{j:04d}/coverage_results', 'r') as file:
                data = json.load(file)
            for fuzzer in data:
                for target in data[fuzzer]:
                    if fuzzer == 'libfuzzer':
                        try:
                            coverage[fuzzer].append(float(data[fuzzer][target]['stop']['coverage']))
                            coverage['xlibfuzzer'].append(DURATIONS[i])
                        except:
                            print(f'Coverage for result dir {j:04d} could not be retrieved.')
                    elif fuzzer == 'honggfuzz':
                        coverage[fuzzer].append(float(data[fuzzer][target]['coverage_percent']))
                        coverage['xhonggfuzz'].append(DURATIONS[i])
                    elif fuzzer == 'aflplusplus':
                        coverage[fuzzer].append(float(data[fuzzer][target]['coverage_percent']))
                        coverage['xaflplusplus'].append(DURATIONS[i])
    fig.add_trace(go.Box(name='AFL++', y=coverage['aflplusplus'], x=coverage['xaflplusplus'], marker_color='#FF4136'))
    fig.add_trace(go.Box(name='Honggfuzz', y=coverage['honggfuzz'], x=coverage['xhonggfuzz'], marker_color='#FF851B'))
    fig.add_trace(go.Box(name='libFuzzer', y=coverage['libfuzzer'], x=coverage['xlibfuzzer'], marker_color='#3D9970'))
    fig.update_yaxes(type='log')
    fig.update_layout(xaxis_title='Fuzz duration', yaxis_title='Coverage', boxmode='group')
    fig.show()


def box_fuzz_dur_coverage_targets():
    fig = go.Figure()
    # coverage = {'openssl-bignum': [], 'openssl-asn1parse': [], 'openssl-server': [], 'openssl-client': [],
    #             'openssl-x509': [],
    #             'xopenssl-bignum': [], 'xopenssl-asn1parse': [], 'xopenssl-server': [], 'xopenssl-client': [],
    #             'xopenssl-x509': []}
    coverage = {'libxml2-xmllint': [], 'libxml2-libxml2_xml_read_memory_fuzzer': [],
                'xlibxml2-xmllint': [], 'xlibxml2-libxml2_xml_read_memory_fuzzer': []}
    for i in range(len(START)):
        for j in range(START[i], STOP[i] + 1):
            with open(f'{RESULT_DIR}{j:04d}/coverage_results', 'r') as file:
                data = json.load(file)
            for fuzzer in data:
                for target in data[fuzzer]:
                    if fuzzer == 'libfuzzer':
                        try:
                            coverage[target].append(float(data[fuzzer][target]['stop']['coverage']))
                            coverage[f'x{target}'].append(DURATIONS[i])
                        except:
                            print(f'Coverage for result dir {j:04d} could not be retrieved.')
                    else:
                        coverage[target].append(100 * float(data[fuzzer][target]['coverage_percent']))
                        coverage[f'x{target}'].append(DURATIONS[i])
    # fig.add_trace(go.Box(name='bignum', y=coverage['openssl-bignum'], x=coverage['xopenssl-bignum']))
    # fig.add_trace(go.Box(name='asn1parse', y=coverage['openssl-asn1parse'], x=coverage['xopenssl-asn1parse']))
    # fig.add_trace(go.Box(name='server', y=coverage['openssl-server'], x=coverage['xopenssl-server']))
    # fig.add_trace(go.Box(name='client', y=coverage['openssl-client'], x=coverage['xopenssl-client']))
    # fig.add_trace(go.Box(name='x509', y=coverage['openssl-x509'], x=coverage['xopenssl-x509']))
    fig.add_trace(go.Box(name='xmllint', y=coverage['libxml2-xmllint'], x=coverage['xlibxml2-xmllint']))
    fig.add_trace(go.Box(name='libxml2_xml_read_memory_fuzzer', y=coverage['libxml2-libxml2_xml_read_memory_fuzzer'], x=coverage['xlibxml2-libxml2_xml_read_memory_fuzzer']))
    fig.update_layout(xaxis_title='Fuzz duration', yaxis_title='Coverage', boxmode='group')
    fig.show()


def box_fuzz_dur_cov_seeds():
    fig = go.Figure()
    coverage = {'aflplusplus': [], 'honggfuzz': [], 'libfuzzer': [], 'xaflplusplus': [], 'xhonggfuzz': [],
                'xlibfuzzer': []}
    for i in range(len(START)):
        for j in range(START[i], STOP[i] + 1):
            with open(f'{RESULT_DIR}{j:04d}/coverage_results', 'r') as file:
                data = json.load(file)
            for fuzzer in data:
                for target in data[fuzzer]:
                    if fuzzer == 'libfuzzer':
                        coverage[fuzzer].append(float(data[fuzzer][target]['stop']['coverage']) / float(
                            data[fuzzer][target]['stop']['corpus']))
                        coverage['xlibfuzzer'].append(DURATIONS[i])
                    elif fuzzer == 'honggfuzz':
                        coverage[fuzzer].append(float(data[fuzzer][target]['coverage_percent']) / float(
                            float(data[fuzzer][target]['stop_corp'])))
                        coverage['xhonggfuzz'].append(DURATIONS[i])
                    elif fuzzer == 'aflplusplus':
                        coverage[fuzzer].append(float(data[fuzzer][target]['coverage_percent']) / float(
                            float(data[fuzzer][target]['stop_corp'])))
                        coverage['xaflplusplus'].append(DURATIONS[i])
    fig.add_trace(go.Box(name='AFL++', y=coverage['aflplusplus'], x=coverage['xaflplusplus'], marker_color='#FF4136'))
    fig.add_trace(go.Box(name='Honggfuzz', y=coverage['honggfuzz'], x=coverage['xhonggfuzz'], marker_color='#FF851B'))
    fig.add_trace(go.Box(name='libFuzzer', y=coverage['libfuzzer'], x=coverage['xlibfuzzer'], marker_color='#3D9970'))
    fig.update_yaxes(type='log')
    fig.update_layout(xaxis_title='Fuzz duration', yaxis_title='Coverage', boxmode='group')
    fig.show()


if __name__ == '__main__':
    # box_fuzz_dur_cov_seeds()

    box_fuzz_dur_coverage_targets()
    box_fuzz_dur_coverage()
    box_fuzz_dur_bug_time()
    box_fuzz_dur_bugs()
    box_fuzz_dur_crashes()

    # start = 226
    # stop = 306
    # coverage_results(start, stop)
    # bugs_found(start, stop)
    # nr_crashes(start, stop)
