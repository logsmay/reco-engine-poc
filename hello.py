#!/usr/bin/python
# -*- coding: utf-8 -*-
from flask import Flask, request, render_template, Markup
import configparser as ConfigParser
import pandas as pd
import time
import json
from CustomLogger import MyLogger

# read config file

config = ConfigParser.ConfigParser()
config.read('reco.cfg')
mylogger = MyLogger(config.get('logger-config', 'logger-name'),
                    config.get('logger-config', 'logger-dir'),
                    config.get('logger-config', 'logger-file'))
data_input = config.get('api-config', 'data_input')
reload_time = config.get('api-config', 'file-reload')
port = int(config.get('api-config', 'port'))


def get_df(input_json):
    start = time.time()
    mylogger.info('loading data from ' + data_input +
                  ' into pandas dataframe...')
    with open(input_json) as data_file:
        data = pd.read_json(data_file)
        data_file.close()
    end = time.time()
    mylogger.info('data load completed - took ' +
                  str('%.2f' % (end - start)) + ' sec(s)')
    return data


def get_geo_series_df(dataframe):

    # geometric series to assign alpha weight as it maintains the priority weight
    # between equal number of combinations between alphabets

    geo_series = {}
    for index in dataframe.index:
        data_calc = index.split('-')[1]
        geo_series[index] = 1.0 / 2 ** (ord(data_calc) - 97)
    geo_df = pd.Series(geo_series, name='geo_df')
    return geo_df


def get_sku_match(
    df,
    sku,
    reco_num,
    page_format,
):
    start = time.time()
    geo_df = get_geo_series_df(dataframe=df)
    sku_obj = df.get(sku)
    if sku_obj is not None:
        sku_match_df = df.isin(sku_obj)
        sku_match_series = pd.Series(sku_match_df.sum(),
                                     name='match_count')
        sku_match_df = df[df.isin(df.get(sku))]
        sku_geo_df = df.isin(df.get(sku)).T.astype('float64') * geo_df
        sku_geo_sum = pd.Series(sku_geo_df.T.sum(), name='alpha_weight')
        del sku_geo_df
        final_df = sku_match_df.T.join([sku_match_series, sku_geo_sum],
                                       how='inner', lsuffix='_l', rsuffix='_r'
                                       ).sort_values(by=['match_count', 'alpha_weight'],
                                                     ascending=False).head(n=reco_num + 1)
        del sku_match_df
        reco_count = len(final_df) - 1
        if page_format == 'html':
            sku_ = \
                final_df._slice(slice(1)).to_html(float_format=lambda x:
                                                  '%10.2f' % x)
            reco_skus = final_df._slice(slice(1, reco_num
                                              + 1)).to_html(float_format=lambda x: '%10.5f' % x,
                                                            na_rep='')
            if reco_count > 0:
                end = time.time()
                html_response = \
                    '<div><h2>Reco PoC Result</h2> <b>Selected sku & attributes</b><br/>' \
                    + sku_ \
                    + ' <br/><b>Recomended skus with alpha weight & attribute ' \
                    + 'match counts</b><br/>' + reco_skus \
                    + '<br/><small>data query took ' + str('%.3f'
                                                           % (end - start)) + ' sec(s) </small></div>'

                # cached_reco_df.ix[sku, "html"] = html_response

                return html_response
            return '{"sku":' + sku_ + ',"reco_sku_count":' \
                + str(reco_count) + '}'
        elif page_format == 'json':
            reco_sku = final_df.to_json(orient='index')
            if reco_count > 0:
                return reco_sku
            return '{"sku":' + sku_ + ',"reco_sku_count":' \
                + str(reco_count) + '}'
        else:
            return '{"error-code":401,"error-reason":"not a valid format' \
                + page_format + '"}'
    else:
        return '{"error-code":404,"error-reason":"sku not available"}'


application = Flask(__name__)


@application.route('/')
def index():
    return render_template('index.html')


@application.route('/reco-query', methods=['GET'])
def query_reco():
    sku = request.args.get('sku')
    recocount = int(request.args.get('recocount'))
    table_data = Markup(get_sku_match(df, sku, recocount, 'html'))
    return render_template('index.html', table_data=table_data)


@application.route('/<page_format>/<reco_num>/<sku>')
def display_reco(sku, reco_num, page_format):
    return get_sku_match(df, sku, int(reco_num), page_format)


if __name__ == '__main__':
    df = get_df(data_input)
    mylogger.info('sample url request in the browser: http://127.0.0.1:'
                  + str(port) + '/html/10/sku-1')
    mylogger.info('sample url request in the browser: http://127.0.0.1:'
                  + str(port) + '/json/15/sku-10231')
    mylogger.info('link to query sku: http://127.0.0.1:' + str(port))

    # cached_reco_df = pd.DataFrame(index=df.columns, columns=["json", "html"])

    application.run(port=port, debug=False, use_reloader=False,
                    threaded=True)
