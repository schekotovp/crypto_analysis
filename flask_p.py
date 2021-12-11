from flask import Flask, render_template, send_file, request
import time
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

app = Flask(__name__)

links = {"Download": "/download",
         "Statistics": "/stats",
         "Data explanations": "/expl",
         "Market dominance of top-100 cryptos": "/domin",
         "Correlation of 60 days change and market cap": "/mc_change_corr",
         "Correlation of market pairs quantity and market cap": "/mc_pairs_corr",
         "Distribution of 60 days change depending on type": "/type_change_dist",
         "MC Distribution of Tokens SC": "/sc_mc_dist",
         "Chart description": "/describe",
         "View Raw Data": "/view_data",
         "Market Pairs": "/pairs",
         "Market Cap": "/mc",
         "Smart Contracts": "/sc"}


def render_index(image=None, html_string=None, filters=None, errors=None, current_filter_value=""):
    return render_template("index.html", links=links, image=image, code=time.time(), html_string=html_string,
                           filters=filters, errors=errors, current_filter_value=current_filter_value)


@app.route('/', methods=['GET'])
def main_page():
    return render_index()


@app.route(links["Download"], methods=['GET'])
def download_data():
    return send_file("data.csv", as_attachment=True)


@app.route(links["Data explanations"], methods=['GET'])
def expl():
    df_expl = pd.DataFrame({'name': ['Name of a cryptocurrency'],
                            'market_pairs': ['Amount of currencies paired'],
                            'circulating': ['Circulating supply (millions of tokens)'],
                            'max supply': ['Is there a maximum supply for this currency?'],
                            'MC': ['Market Cap (millions $)'],
                            'MC_dominance': ['Dominance on the general market (%)'],
                            'sixty_days_change': ['60 days change (%)'],
                            'SC': ['Does provide a platform for smart contracts?']
                            })
    html_string_exp = df_expl.to_html()
    return render_index(html_string=html_string_exp, filters=True)



@app.route(links["Correlation of 60 days change and market cap"], methods=['GET'])
def mc_change_corr():
    df = pd.read_csv("data.csv")
    fig, ax = plt.subplots(figsize=(12, 7))

    ax.set_xlim(-1000, 40000)
    ax.set_ylim(-150, 250)

    ax.set_title("Correlation of 60 days change and market cap", size=17, pad=10)
    ax.set_xlabel("MC")
    ax.set_ylabel("60 days change")
    ax.grid(True)
    ax.tick_params(left=False, bottom=False)
    ax.scatter(df[3:505].MC, df[3:505].sixty_days_change, s=20.6)
    plt.savefig('static/tmp/mc_change_corr.png')
    return render_index(image=("mc_change_corr.png", "Correlation of 60 days change and market cap"))


@app.route(links["Market dominance of top-100 cryptos"], methods=['GET'])
def domin():
    df = pd.read_csv('data.csv')
    x = df[3:100].MC_dominance.dropna()

    fig, ax = plt.subplots(figsize=(12, 7))

    ax.set_xlim(0, 3)
    ax.set_ylim(0, 5)

    ax.set_xlabel("MC dominance")
    ax.set_ylabel("Frequency")

    ax.set_yticklabels([None, 1, 2, 3, 4, 5])

    ax.grid(True)
    ax.set_title("MC dominance of top-100 cryptos", size=17, pad=10)

    ax.tick_params(left=False, bottom=False)
    ax.hist(x, density=True, alpha=0.65, bins=29)
    x.plot(kind="kde")
    plt.style.use("bmh")
    plt.savefig('static/tmp/mc_dominance.png')

    return render_index(image=("mc_dominance.png", "Market dominance of top-100 cryptos"))


@app.route(links["Correlation of market pairs quantity and market cap"], methods=['GET'])
def mc_pairs_corr():
    df = pd.read_csv("data.csv")
    fig, ax = plt.subplots(figsize=(12, 7))

    ax.scatter(df.MC, df.market_pairs, s=25.6)

    ax.set_xlim(-1000, 40000)
    ax.set_ylim(0, 2000)
    ax.set_yticklabels([None] + list(range(250, 2250, 250)))
    ax.set_title("MC and amount of market pairs correlation", size=17, pad=10)
    ax.set_xlabel("MC")
    ax.set_ylabel("market pairs")
    ax.tick_params(left=False, bottom=False)

    plt.savefig('static/tmp/mc_pairs_corr.png')
    return render_index(image=("mc_pairs_corr.png", "Correlation of market pairs quantity and market cap"))


@app.route(links["MC Distribution of Tokens SC"], methods=['GET'])
def sc_mc_dist():
    import matplotlib.pyplot as plt
    df = pd.read_csv("data.csv")
    data = pd.DataFrame(data=df, columns=['MC'])
    target = pd.DataFrame(data=df, columns=['SC'])
    new_df = pd.concat([data, target], axis=1)
    n_type = new_df.groupby('SC').agg('sum')['MC']
    label = ['No SC', 'SC']
    explode = [0, 0.1]

    plt.style.use('ggplot')
    plt.rcParams.update({'font.size': 12})

    size = (9, 5)

    plt.figure(figsize=size, dpi=100)

    plt.pie(n_type, explode=explode, shadow=True,
            startangle=90, autopct='%1.1f%%',
            wedgeprops={'edgecolor': 'black'})
    plt.legend(label, fancybox=True, loc='center left', bbox_to_anchor=(0.9, 0.5))
    plt.axis('equal')
    plt.title("MC Distribution of Tokens with and without Smart Contracts")
    plt.tight_layout()

    plt.savefig('static/tmp/sc_mc_dist.png', bbox_inches='tight', pad_inches=0.05)
    return render_index(image=("sc_mc_dist.png", "MC Distribution of Tokens SC"))


@app.route(links["Distribution of 60 days change depending on type"], methods=['GET'])
def type_change_dist():
    df = pd.read_csv("data.csv")
    data = pd.DataFrame(data=df, columns=['MC', 'sixty_days_change'])
    target = pd.DataFrame(data=df, columns=['max supply'])
    new_df = pd.concat([data, target], axis=1)

    new_df['Type'] = np.where(new_df['max supply'] == 0, 'Without max supply', None)
    new_df['Type'] = np.where(new_df['max supply'] == 1, 'With max supply', new_df['Type'])

    without_max_supply = new_df[new_df['Type'] == 'Without max supply']['sixty_days_change']
    with_max_supply = new_df[new_df['Type'] == 'With max supply']['sixty_days_change']
    with_max_supply = (pd.DataFrame(sorted(with_max_supply, reverse=True)).iloc[30:])[0]
    without_max_supply = (pd.DataFrame(sorted(without_max_supply, reverse=True)).iloc[30:])[0]

    fig, ax = plt.subplots(figsize=(12, 7))

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)

    ax.yaxis.set_ticks_position('none')

    ax.grid(color='grey', axis='y', linestyle='-', linewidth=0.25, alpha=0.5)

    ax.set_title('Distribution of 60 days change depending on type')

    dataset = [with_max_supply, without_max_supply]
    labels = new_df['Type'].unique()
    ax.boxplot(dataset, labels=labels)

    plt.savefig('static/tmp/type_change_dist.png')
    return render_index(image=("type_change_dist.png", "Distribution of 60 days change depending on type"))


@app.route(links["Chart description"], methods=['GET', 'POST'])
def describe():
    with open('description.txt', 'r') as f:
        text = f.read()
    text = text.replace('\n', '<br>')
    return render_index(html_string=text, filters=True)


@app.route(links["View Raw Data"], methods=['GET', 'POST'])
def view_data():
    df = pd.read_csv("data.csv")
    errors = []
    current_filter_value = ""
    if request.method == "POST":
        current_filter = request.form.get('filters')
        current_filter_value = current_filter
        if current_filter:
            try:
                df = df.loc[[df[df['name'] == current_filter].index[0]]]
            except Exception as e:
                errors.append('<font color="red">Incorrect filter</font>')
                print(e)

    html_string = df.to_html()
    return render_index(html_string=html_string, filters=True, errors=errors, current_filter_value=current_filter_value)


@app.route(links["Market Cap"], methods=['GET', 'POST'])
def mc():
    df = pd.read_csv("data.csv")
    errors = []
    current_filter_value = ""
    if request.method == "POST":
        current_filter = request.form.get('filters')
        current_filter_value = current_filter
        if current_filter:
            try:
                df = df.loc[[df[df['name'] == current_filter].index[0]]]
            except Exception as e:
                errors.append('<font color="red">Incorrect filter</font>')
                print(e)

    html_string_3 = df[["name", "MC"]].to_html()
    return render_index(html_string=html_string_3, filters=True, errors=errors, current_filter_value=current_filter_value)


@app.route(links["Market Pairs"], methods=['GET', 'POST'])
def pairs():
    df = pd.read_csv("data.csv")
    errors = []
    current_filter_value = ""
    if request.method == "POST":
        current_filter = request.form.get('filters')
        current_filter_value = current_filter
        if current_filter:
            try:
                df = df.loc[[df[df['name'] == current_filter].index[0]]]
            except Exception as e:
                errors.append('<font color="red">Incorrect filter</font>')
                print(e)

    html_string_2 = df[["name", "market_pairs"]].to_html()
    return render_index(html_string=html_string_2, filters=True, errors=errors, current_filter_value=current_filter_value)


@app.route(links["Smart Contracts"], methods=['GET', 'POST'])
def sc():
    df = pd.read_csv("data.csv")
    errors = []
    current_filter_value = ""
    if request.method == "POST":
        current_filter = request.form.get('filters')
        current_filter_value = current_filter
        if current_filter:
            try:
                df = df.loc[[df[df['name'] == current_filter].index[0]]]
            except Exception as e:
                errors.append('<font color="red">Incorrect filter</font>')
                print(e)

    html_string_1 = df[["name", "SC"]].to_html()
    return render_index(html_string=html_string_1, filters=True, errors=errors, current_filter_value=current_filter_value)


@app.route(links["Statistics"], methods=['GET', 'POST'])
def stats():
    df = pd.read_csv("data.csv")

    errors = []
    current_filter_value = ""
    if request.method == "POST":
        current_filter = request.form.get('filters')
        current_filter_value = current_filter
        if current_filter:
            try:
                df = df.loc[[df[df['name'] == current_filter].index[0]]]
            except Exception as e:
                errors.append('<font color="red">Incorrect filter</font>')
                print(e)
    df1 = pd.concat([df[['market_pairs', 'MC', 'sixty_days_change']].describe()[1:3], pd.DataFrame(dict(
        zip(['market_pairs', 'MC', 'sixty_days_change'], df[['market_pairs', 'MC', 'sixty_days_change']].median())),
        columns=[
            'market_pairs',
            'MC',
            'sixty_days_change'],
        index=['median'])], axis=0)
    html_string = df1.to_html()
    return render_index(html_string=html_string, filters=True, errors=errors, current_filter_value=current_filter_value)


if __name__ == '__main__':
    app.run()
