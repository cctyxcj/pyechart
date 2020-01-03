from flask import Flask, render_template, request
import pandas as pd
from pyecharts import options as opts
from pyecharts.charts import Map, Line, Bar

app = Flask(__name__)

# 地图
df_map = pd.read_csv('./csv/map.csv', encoding='GBK', delimiter=",")
regions_available_map = list(df_map['region'].dropna().unique())

# 折线图
df_line = pd.read_csv('./csv/line.csv', encoding='GBK', delimiter=",")

# 柱状图
df_bar = pd.read_csv('./csv/bar.csv', encoding='GBK', delimiter=",")
regions_available_bar = list(df_bar['region'].dropna().unique())


@app.route('/', methods=['GET'])
def hu_run_2019():
    return render_template('pyecharts.html',
                           mark="index", )


@app.route('/toMap/oldMan', methods=['GET'])
def to_map_old_man():
    return render_template('pyecharts.html',
                           mark="map_oldMan",
                           the_select_year=["2018", "2017", "2016"],
                           )


@app.route('/toMap/citys', methods=['GET'])
def to_map_citys():
    return render_template('pyecharts.html',
                           mark="map_citys",
                           the_select_year=["2018", "2017", "2016"],
                           )


@app.route('/toLine', methods=['GET'])
def to_line():
    return render_template('pyecharts.html',
                           mark="line",
                           )


@app.route('/toBar', methods=['GET'])
def to_bar():
    return render_template('pyecharts.html',
                           mark="bar",
                           the_select_region=regions_available_bar,
                           )


# 柱状图
@app.route('/bar', methods=['POST'])
def bar_select() -> 'html':
    the_region = request.form["the_region_selected"]
    dfs_bar = df_bar.query("region=='{}'".format(the_region))

    c = (
        Bar()
            .add_xaxis(dfs_bar['年'].tolist())
            .add_yaxis(the_region, dfs_bar['count'].tolist())
            .set_global_opts(title_opts=opts.TitleOpts(title=the_region, subtitle=""))
    )

    c.render("./static/tmp/echarts_bar.html")
    with open("./static/tmp/echarts_bar.html", encoding="utf8", mode="r") as f:
        plot_all = "".join(f.readlines())

    data_str = dfs_bar.to_html()
    return render_template('pyecharts.html',
                           myechart=plot_all,
                           the_res=data_str,
                           the_select_region=regions_available_bar,
                           bottom_title="分析:柱状图",
                           mark="bar",
                           )


# 折线图
@app.route('/line', methods=['POST'])
def line_select() -> 'html':
    d = {"2016": "2016年老年人人口抚养比",
         "2017": "2017年老年人人口抚养比",
         "2018": "2018年老年人人口抚养比",
         "2018urual": "2018年农村老年人人口抚养比",
         "2018city": "2018年城市老年人人口抚养比",
         }
    the_region = request.form["the_region_selected"]
    c = (
        Line()
            .add_xaxis(df_line['地区'].tolist())
            .add_yaxis(the_region, df_line[the_region])
            .set_global_opts(title_opts=opts.TitleOpts(title=d[the_region]),
                             xaxis_opts=opts.AxisOpts(name="地区", axislabel_opts={"rotate": 45}))
    )
    c.render("./static/tmp/echarts_line.html")
    with open("./static/tmp/echarts_line.html", encoding="utf8", mode="r") as f:
        plot_all = "".join(f.readlines())
    data_str = df_line.to_html()
    return render_template('pyecharts.html',
                           myechart=plot_all,
                           the_res=data_str,
                           mark="line",
                           bottom_title="分析:折线图",
                           )


# 老年人口地图
@app.route('/map/oldMan', methods=['POST'])
def map_select() -> 'html':
    the_region = regions_available_map[0]
    dfs = df_map.query("region=='{}'".format(the_region))
    the_year = request.form["the_year_selected"]
    chart = (
        Map()
            .add(series_name=the_region, data_pair=[list(z) for z in zip(dfs["地区"], dfs[the_year])], maptype="china")
            .set_global_opts(
            title_opts=opts.TitleOpts(title=the_year + the_region),
            visualmap_opts=opts.VisualMapOpts(max_=10000),
        )
    )
    chart.render("./static/tmp/echarts_map.html")
    with open("./static/tmp/echarts_map.html", encoding="utf8", mode="r") as f:
        plot_all = "".join(f.readlines())
    data_str = dfs.to_html()
    return render_template('pyecharts.html',
                           myechart=plot_all,
                           mark="map_oldMan",
                           the_res=data_str,
                           the_select_year=["2018", "2017", "2016"],
                           bottom_title="分析:地图_老年人",
                           )


# 城市化地图
@app.route('/map/citys', methods=['POST'])
def map_select_citys() -> 'html':
    the_region = regions_available_map[1]
    dfs = df_map.query("region=='{}'".format(the_region))
    the_year = request.form["the_year_selected"]

    # 切掉百分号
    ndfs = dfs[the_year].apply(lambda x: x[0:5]).astype('float')

    chart = (
        Map()
            .add(series_name=the_region, data_pair=[list(z) for z in zip(dfs["地区"], ndfs)], maptype="china")
            .set_global_opts(
            title_opts=opts.TitleOpts(title=the_year + the_region),
            visualmap_opts=opts.VisualMapOpts(min_=28, max_=90),
        )
    )
    chart.render("./static/tmp/echarts_map.html")
    with open("./static/tmp/echarts_map.html", encoding="utf8", mode="r") as f:
        plot_all = "".join(f.readlines())
    data_str = dfs.to_html()
    return render_template('pyecharts.html',
                           myechart=plot_all,
                           mark="map_citys",
                           the_res=data_str,
                           the_select_year=["2018", "2017", "2016"],
                           bottom_title="分析:地图_城市化",
                           )


if __name__ == '__main__':
    app.run(debug=True, port=8000)
