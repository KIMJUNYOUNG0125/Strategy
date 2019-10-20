from mpl_finance import candlestick_ohlc
import plotly.graph_objs as go
import copy

INCREASING_COLOR = 'rgb(255,0,0)'   #red
DECREASING_COLOR = 'rgb(0,0,255)'   #blue
gold = "rgb(255, 215, 0)"
purple = "rgb(128, 0, 128)"
lightblue = "rgb(173, 216, 230)"
grey = "rgb(128, 128, 128)"
black = "rgb(0, 0, 0)"

def drawing_chart(df):
    #----------------Create the layout object -------------------------

    # https://github.com/plotly/dash-technical-charting/blob/master/quantmod/chart.py
    _PLACEHOLDER = False
    layout = dict(
                # General
                title = '', width = 720, height = 480, autosize = True,
                margin = dict(t = 60, l = 40, b = 40, r = 40, pad = 0) , hovermode = 'x', barmode = "group",
                # Color theme
                plot_bgcolor = '#FFFFFF', paper_bgcolor = '#F3F3F3',
                # Gaps
                bargap = 0.3, bargroupgap = 0.0, boxgap = 0.3, boxgroupgap = 0.0,
                # Legend
                # showlegend = False,
                legend = dict(bgcolor = 'rgba(0, 0, 0, 0.00)', x = 0.01, y = 0.99, xanchor = 'left', yanchor = 'top', tracegroupgap = 10),
                font = dict(size = 10, color = '#222222'),
                #x축
                xaxis = dict(
                        # Range
                        #nticks = 10, #OR
                        #tick0 = , #AND
                        #dtick = ,
                        # Ticks
                        #tickfont = dict(size = 10),
                        showticklabels = True,
                        # Range slider
                        rangeslider = dict(visible = True, bordercolor = '#CCCCCC', bgcolor = '#CCCCCC', thickness = 0.1),
                        # Range selector
                        rangeselector = dict(visible = True, bordercolor = '#C9C9C9', bgcolor = '#C9C9C9', activecolor = '#888888',
                                            buttons = [
                                            #dict(count = 1, step = 'day', stepmode = 'backward', label = '1D'),
                                            dict(count = 5, step = 'day', stepmode = 'backward', label = '5D'),
                                            dict(count = 1, step = 'month', stepmode = 'backward', label = '1M'),
                                            dict(count = 3, step = 'month', stepmode = 'backward', label = '3M'),
                                            dict(count = 6, step = 'month', stepmode = 'backward', label = '6M'),
                                            dict(count = 1, step = 'year', stepmode = 'backward', label = '1Y'),
                                            #dict(count = 2, step = 'year', stepmode = 'backward', label = '2Y'),
                                            #dict(count = 5, step = 'year', stepmode = 'backward', label = '5Y'),
                                            dict(count = 1, step = 'all', stepmode = 'backward', label = 'MAX'),
                                            dict(count = 1, step = 'year', stepmode = 'todate', label = 'YTD'),
                                            dict(step='all')
                                            ],
                                            ),
                        # Other
                        type = 'date',
                        anchor = 'y',
                        side = 'bottom',
                        autorange = True,
                        showgrid = True,
                        gridwidth = 1,
                        gridcolor = '#F3F3F3',
                        zeroline = False,
                        showline = True,
                        linewidth = 1,
                        linecolor = grey,
                        mirror = True
                        #titlefont = dict(size = 10),
                        ),

                #y축
                yaxis = dict(
                        # Range
                        #rangemode = 'tozero',
                        #range = ,
                        #nticks = 5, #OR
                        #tick0 = , #AND
                        #dtick = ,
                        # Ticks
                        #tickfont = dict(size = 10),
                        showticklabels = True,
                        # Other
                        type = 'linear',
                        domain = [0.0, 1],
                        side = 'left',
                        # Additions
                        color = '#444444', tickfont = dict(color = '#222222'),
                        #fixedrange = False,
                        autorange = True,
                        showgrid = True,
                        gridwidth = 1,
                        gridcolor = '#F3F3F3',
                        zeroline = False,
                        showline = True,
                        linewidth = 1,
                        linecolor = grey,
                        mirror = True
                        #titlefont = dict(size = 10),
                        ),
                )


    # One main plot, n(4) gaps and sub plots
    n = 4
    main_height = 0.5 * layout['height']
    sub_height = 0.24 * layout['height']
    gap_height = 0.01 * layout['height']
    new_height = main_height + n * (gap_height + sub_height)

    main = main_height / new_height
    sub = sub_height / new_height
    gap = gap_height / new_height

    # Main plot
    upper = 1.0
    lower = upper - main
    layout['yaxis']['domain'] = [lower, upper]


    # Subplots
    for i in range(n):
        upper = lower - gap
        lower = upper - sub
        yaxisn = 'yaxis{0}'.format(i + 2)
        layout[yaxisn] = copy.deepcopy(layout['yaxis'])
        layout[yaxisn]['domain'] = [lower, upper]

    layout['xaxis']['anchor'] = 'y{0}'.format(n + 1)
    layout['height'] = new_height


    #---------------- Initial candlestick chart, moving_average on y -------------------------
    #----------------Add moving_average on y -------------------------

    # candlestick
    trace1_0 = dict(type = 'candlestick',
                    open = df.open,
                    high = df.high,
                    low = df.low,
                    close = df.close,
                    x = df.date,
                    yaxis = 'y',
                    name = 'stock',
                    showlegend = False,
                    increasing = dict( line = dict( color = INCREASING_COLOR ) ),
                    decreasing = dict( line = dict( color = DECREASING_COLOR ) )) 
    # moving_average_5
    trace1_1 = dict(x=df.date, y=df.close_ma5, 
                    type = 'scatter', mode = 'lines',
                    line = dict(width = 1),
                    marker=dict(color= INCREASING_COLOR), 
                    yaxis='y', name='ma5')
    # moving_average_10
    trace1_2 = dict(x=df.date, y=df.close_ma10, 
                    type = 'scatter', mode = 'lines',
                    line = dict(width = 1),
                    marker=dict(color= purple), 
                    yaxis='y', name='ma10') 
    # moving_average_20
    trace1_3 = dict(x=df.date, y=df.close_ma20, 
                    type = 'scatter', mode = 'lines',
                    line = dict(width = 1),
                    marker=dict(color= lightblue), 
                    yaxis='y', name='ma20' )
    # golden_cross_ma5 to 20
    trace1_4 = dict(x=df.date, y=df.ma_g_c, 
                    type = 'scatter', mode = 'markers',
                    showlegend = False,
                    marker=dict(color= gold,
                                size = 10,
                                symbol = 'triangle-up'), 
                    yaxis='y', name='ma_g_c' 
                    )
    # dead_cross_ma5 to 20
    trace1_5 = dict(x=df.date, y=df.ma_d_c, 
                    type = 'scatter', mode = 'markers',
                    showlegend = False,
                    marker=dict(color= grey,
                                size = 10,
                                symbol = 'triangle-down'), 
                    yaxis='y', name='ma_d_c' 
                    )


    #----------------Add volume bar chart on y2 -------------------------
    #Set volume bar chart colors

    colors = []

    for i in range(len(df.close)):
        if i != 0:
            if df.volume[i] > df.volume[i-1]:
                colors.append(INCREASING_COLOR)
            else:
                colors.append(DECREASING_COLOR)
        else:
            colors.append(DECREASING_COLOR)

    #Add volume bar chart

    trace2 = dict(x=df.date, y=df.volume,
                    marker=dict( color=colors ),
                    showlegend = False,
                    type='bar', yaxis='y2', name='Volume' )
            
    #----------------Add stocastic on y3 -------------------------


    trace3_1 =  dict(x=df.date, y=df.slowk,
                    type = 'scatter', mode = 'lines',
                    line = dict(width = 1),
                    marker=dict(color= INCREASING_COLOR),
                    yaxis='y3', name='slowk')
    trace3_2 = dict(x=df.date, y=df.slowd, 
                    type = 'scatter', mode = 'lines',
                    line = dict(width = 1),
                    marker=dict(color= DECREASING_COLOR),
                    yaxis='y3', name='slowd' )
    # golden_cross_stocastic
    trace3_3 = dict(x=df.date, y=df.stoc_g_c, 
                    type = 'scatter', mode = 'markers',
                    showlegend = False,
                    marker=dict(color= gold,
                                size = 10,
                                symbol = 'triangle-up'), 
                    yaxis='y3', name='stoc_g_c' 
                    )
    # dead_cross_stocastic
    trace3_4 = dict(x=df.date, y=df.stoc_d_c, 
                    type = 'scatter', mode = 'markers',
                    showlegend = False,
                    marker=dict(color= grey,
                                size = 10,
                                symbol = 'triangle-down'), 
                    yaxis='y3', name='stoc_d_c' 
                    )

    #----------------Add RSI on y4 -------------------------


    trace4_1 =  dict(x=df.date, y=df.rsi14,
                    type = 'scatter', mode = 'lines',
                    line = dict(width = 1),
                    marker=dict(color= INCREASING_COLOR),
                    yaxis='y4', name='rsi14' )
    trace4_2 =  dict(x=df.date, y=df.rsi14_signal,
                    type = 'scatter', mode = 'lines',
                    line = dict(width = 1),
                    marker=dict(color= DECREASING_COLOR),
                    yaxis='y4', name='rsi14_signal' )
    # golden_cross_rsi
    trace4_3 = dict(x=df.date, y=df.rsi_g_c, 
                    type = 'scatter', mode = 'markers',
                    showlegend = False,
                    marker=dict(color= gold,
                                size = 10,
                                symbol = 'triangle-up'), 
                    yaxis='y4', name='rsi_g_c' 
                    )
    # dead_cross_rsi
    trace4_4 = dict(x=df.date, y=df.rsi_d_c, 
                    type = 'scatter', mode = 'markers',
                    showlegend = False,
                    marker=dict(color= grey,
                                size = 10,
                                symbol = 'triangle-down'), 
                    yaxis='y4', name='rsi_d_c' 
                    )


    #----------------Add macd on y5 -------------------------
    #Add macd
    trace5_1 =  dict(x=df.date, y=df.macd,
                    type = 'scatter', mode = 'lines',
                    line = dict(width = 1),
                    marker=dict(color= INCREASING_COLOR), 
                    yaxis='y5', name='macd' )
    trace5_2 =  dict(x=df.date, y=df.macdsignal,
                    type = 'scatter', mode = 'lines',
                    line = dict(width = 1),
                    marker=dict(color= DECREASING_COLOR),
                    yaxis='y5', name='macdsignal' )
    # golden_cross_rsi
    trace5_3 = dict(x=df.date, y=df.macd_g_c, 
                    type = 'scatter', mode = 'markers',
                    showlegend = False,
                    marker=dict(color= gold,
                                size = 10,
                                symbol = 'triangle-up'), 
                    yaxis='y5', name='macd_g_c' 
                    )
    # dead_cross_rsi
    trace5_4 = dict(x=df.date, y=df.macd_d_c, 
                    type = 'scatter', mode = 'markers',
                    showlegend = False,
                    marker=dict(color= grey,
                                size = 10,
                                symbol = 'triangle-down'), 
                    yaxis='y5', name='macd_d_c' 
                    )



    data = [trace1_0, trace1_1, trace1_2, trace1_3, trace1_4, trace1_5,
            trace2,
            trace3_1, trace3_2, trace3_3, trace3_4,
            trace4_1, trace4_2, trace4_3, trace4_4,
            trace5_1, trace5_2, trace5_3, trace5_4, 
            ]

    fig = dict(data=data, layout=layout)
    fig_go = go.FigureWidget(data=data, layout=layout)

    #auto rescailing y-axis
    def zoom(layout, xrange):
        in_view = df.set_index('date')[fig_go.layout.xaxis.range[0].split(" ")[0]:fig_go.layout.xaxis.range[1].split(" ")[0]]
        fig_go.layout.yaxis.range = [in_view.low.min() - 100, in_view.high.max() + 100]

    fig_go.layout.on_change(zoom, 'xaxis.range')

    #fig -> not autoscale for saved file
    #fig_go -> autoscale for not saved file

    return fig, fig_go