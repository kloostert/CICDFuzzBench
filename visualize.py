import json

import pandas as pd
import plotly.express as px


def coverage_results(start_dir, stop_dir):
    with open(f'/srv/results/example/coverage_results', 'r') as file:
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
        with open(f'/srv/results/artificial/{i:04d}/coverage_results', 'r') as file:
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
                fig.write_html(f'/var/www/html/plotly/{fuzzer}-{metric.replace("/", "_")}.html')
        else:
            for metric in data[fuzzer]['openssl-client']:
                res = {}
                for target in data[fuzzer]:
                    res[target] = data[fuzzer][target][metric]
                df = pd.DataFrame.from_dict(res, dtype=float)
                fig = px.line(df, title=f'{fuzzer} - {metric} over time')
                fig.write_html(f'/var/www/html/plotly/{fuzzer}-{metric.replace("/", "_")}.html')


def bugs_found(start_dir, stop_dir):
    fuzzers = []
    res = {'active_bugs': []}
    overall_res = {'active': [], 'reached': [], 'triggered': [], 'detected': []}
    with open(f'/srv/results/example/coverage_results', 'r') as file:
        data = json.load(file)
        for fuzzer in data:
            fuzzers.append(fuzzer)
            res[fuzzer] = {}

    for i in range(start_dir, stop_dir + 1):
        bug_codes = {'reached': [], 'triggered': [], 'detected': []}
        with open(f'/srv/results/artificial/{i:04d}/bug_status', 'r') as file:
            bug_status = json.load(file)
            res['active_bugs'].append(bug_status['nr_active_bugs'])
            overall_res['active'].append(bug_status['nr_active_bugs'])

        with open(f'/srv/results/artificial/{i:04d}/final_results', 'r') as file:
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
        fig.write_html(f'/var/www/html/plotly/{fuzzer}-bug_status.html')

    df = pd.DataFrame.from_dict(overall_res, dtype=float)
    fig = px.line(df, title=f'Bug status for all fuzzers over time')
    fig.write_html(f'/var/www/html/plotly/combined-bug_status.html')

    new_overall = {'reached': [], 'triggered': [], 'detected': []}
    for i in range(start_dir, stop_dir + 1):
        for status in new_overall:
            new_overall[status].append(overall_res[status][i - start_dir] / overall_res['active'][i - start_dir] * 100)
    df = pd.DataFrame.from_dict(new_overall, dtype=float)
    fig = px.line(df, title=f'Percentage of bugs reached, triggered and detected for all fuzzers over time')
    fig.update_layout(xaxis_title='Time (commit number)', yaxis_title='Percentage of bugs (%)',
                      legend_title='Bug status')
    fig.write_html(f'/var/www/html/plotly/percent-bug_status.html')


def nr_crashes(start_dir, stop_dir):
    plot_data = {}
    for i in range(start_dir, stop_dir + 1):
        target_crashes = {}
        with open(f'/srv/results/artificial/{i:04d}/nr_crashes', 'r') as file:
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

    df = pd.DataFrame.from_dict(plot_data, dtype=float)
    fig = px.line(df, title=f'Number of crashes per fuzz target for all fuzzers over time')
    fig.update_layout(xaxis_title='Time (commit number)', yaxis_title='Number of crashes',
                      legend_title='Fuzz target')
    fig.write_html(f'/var/www/html/plotly/overall-nr_crashes.html')


if __name__ == '__main__':
    coverage_results(226, 306)
    bugs_found(226, 306)
    nr_crashes(226, 306)
