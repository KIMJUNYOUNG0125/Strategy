from mpl_finance import candlestick_ohlc
#from plotly import tools
#import plotly.offline as offline 
#import plotly.graph_objs as go


def drawing_chart(df):

    #----------------Initial candlestick chart -------------------------

    INCREASING_COLOR = 'rgb(255,0,0)'
    DECREASING_COLOR = 'rgb(0,0,255)'

    data = [ dict(
        type = 'candlestick',
        open = df.open,
        high = df.high,
        low = df.low,
        close = df.close,
        x = df.date,
        yaxis = 'y3',
        name = 'GS',
        increasing = dict( line = dict( color = INCREASING_COLOR ) ),
        decreasing = dict( line = dict( color = DECREASING_COLOR ) ),
    ) ]
    layout=dict()
    fig = dict( data=data, layout=layout )

    #----------------Create the layout object -------------------------
    #https://plot.ly/python/axes/

    fig['layout'] = dict()
    fig['layout']['plot_bgcolor'] = 'rgb(250, 250, 250)'
    fig['layout']['xaxis'] = dict( rangeselector = dict( visible = True ) )

    #y축1 위치 : volume
    fig['layout']['yaxis'] = dict( domain = [0, 0.15] , nticks = 3,
                                showline=True, linewidth=2, linecolor='black',
                                autorange =True, fixedrange = False)

    #y축2 위치 : macd
    fig['layout']['yaxis2'] = dict( domain = [0.15, 0.3], nticks = 5,
                                showline=True, linewidth=2, linecolor='black',
                                autorange =True, fixedrange = False)

    #y축3 위치 : candle, 볼린져, 이평등
    fig['layout']['yaxis3'] = dict( domain = [0.3, 0.8],nticks = 5,
                                showline=True, linewidth=2, linecolor='black',
                                autorange =True, fixedrange = False)

    fig['layout']['legend'] = dict( orientation = 'h', y=0.9, x=0.3, yanchor='bottom' )

    #위아래여백
    fig['layout']['margin'] = dict( t=40, b=40, r=40, l=40 )

    #----------------Add range buttons -------------------------

    rangeselector=dict(
        visible = True,
        x = 0, y = 0.9,
        bgcolor = 'rgba(150, 200, 250, 0.4)',
        font = dict( size = 13 ),
        buttons=list([
            dict(count=1,
                label='reset',
                step='all'),
            dict(count=5,
                label = '1w',
                step = 'day',
                stepmode = 'backward'),
            dict(count=10,
                label = '2w',
                step = 'day',
                stepmode = 'backward'), 
            dict(count=20,
                label = '1m',
                step = 'day',
                stepmode = 'backward'),         
            dict(step='all')
            
        ]))
        
    fig['layout']['xaxis']['rangeselector'] = rangeselector

    #----------------Add volume bar chart -------------------------
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
    fig['data'].append( dict( x=df.date, y=df.volume,                         
                            marker=dict( color=colors ),
                            type='bar', yaxis='y', name='Volume' ) )

    #----------------Add macd -------------------------
    #Add macd

    fig['data'].append( dict( x=df.date, y=df.macd, 
                            type = 'scatter', mode = 'lines',
                            line = dict(width = 1),
                            marker=dict(color= 'aquamarine'), 
                            yaxis='y2', name='macd' ) )

    fig['data'].append( dict( x=df.date, y=df.macdsignal, 
                            type = 'scatter', mode = 'lines',
                            line = dict(width = 1),
                            marker=dict(color= 'darkturquoise'), 
                            yaxis='y2', name='macdsignal' ) )

    #----------------Add moving_average -------------------------

    fig['data'].append( dict( x=df.date, y=df.close_ma5, 
                            type = 'scatter', mode = 'lines',
                            line = dict(width = 1),
                            marker=dict(color= 'olive'), 
                            yaxis='y3', name='ma5' ) )

    fig['data'].append( dict( x=df.date, y=df.close_ma10, 
                            type = 'scatter', mode = 'lines',
                            line = dict(width = 1),
                            marker=dict(color= 'forestgreen'),
                            yaxis='y3', name='ma10' ) )

    fig['data'].append( dict( x=df.date, y=df.close_ma20, 
                            type = 'scatter',  mode = 'lines',
                            line = dict(width = 1),
                            marker=dict(color= 'black'),
                            yaxis='y3', name='ma20' ) )


    return fig