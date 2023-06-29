import csv
from datetime import datetime
import pandas as pd
import numpy as np
import dash
import time
import base64
from dash import dcc
from dash import html
from dash_table import DataTable
import dash_bootstrap_components as dbc
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
from flask import Flask, request, session
import plotly.express as px
import io
import dash_auth

# fonts
title_size = 24
body_size = 16

# styles
button_style = {'margin': '20px 20px 20px 20px', 'fontSize': 18, 'font-family': 'sans-serif'}

# Global
# name_client_global='Unknown_client'

# AUTH

VALID_USERNAME_PASSWORD_PAIRS = {
    'tcc_internal_access': 'tccuser',
    'TEVA_supplier_selection': 'HDf8HJDp789m',
    'accessE18': 'csS4Mzen236r',
    'accessR17': 'GBHICZs564it',
    'accessT16': '5veIKEcd457d',
}


def clear_database():
    open('save_sup.csv', 'w')


def reset_weightage():
    with open('param_wt_init.csv', 'r') as input_file:
        reader = csv.reader(input_file)
        rows = list(reader)
    # Create a new CSV file with the same information
    with open('param_wt.csv', 'w', newline='') as output_file:
        writer = csv.writer(output_file)
        for row in rows:
            writer.writerow(row)


def DL_ranking(df):
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Sheet1', index=False)
    writer.save()
    return output.getvalue()


def check_duplicate(name):
    tag_ = False
    with open('save_sup.csv', 'r') as f:
        datareader = csv.reader(f)
        for row_test in datareader:
            if row_test != []:
                if row_test[0] == name:
                    tag_ = True
    return tag_


def test_length(name_file):
    length = 0
    with open(name_file, 'r') as f:
        datareader = csv.reader(f)
        for row_test in datareader:
            if row_test != []:
                length += 1
    if length >= 25:
        return False
    else:
        return True


def csv_to_df_live(name_file,
                   scf_wt,
                   VMI_wt,
                   critical_wt,
                   inventory_wt,
                   pay_term_wt,
                   lead_time_wt,
                   business_wt,
                   overdue_wt):
    data = []
    with open(name_file, 'r') as f:
        datareader = csv.reader(f)
        for row_test in datareader:
            if row_test != []:
                data.append(row_test)

    # LET'S HAVE A CREATED DATA WITH SCORE FROM DF_DATA
    data_score = []
    for row in data:
        row_nk = []
        row_nk.append(row[0])
        row_nk.append(weighted_total_live(row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], scf_wt,
                                          VMI_wt,
                                          critical_wt,
                                          inventory_wt,
                                          pay_term_wt,
                                          lead_time_wt,
                                          business_wt,
                                          overdue_wt))
        data_score.append(row_nk)

    df = pd.DataFrame(data_score, columns=['Supplier Name', 'Rating (out of 10)'])
    sorted_df = df
    sorted_df['Rating (out of 10)'] = sorted_df['Rating (out of 10)'].astype(float)
    sorted_df['ReverseRank'] = sorted_df['Rating (out of 10)'].rank(method='max')
    nrows = sorted_df.shape[0]
    max_rank = sorted_df['ReverseRank'].max()
    sorted_df['Rank'] = nrows + 1 - df['ReverseRank']
    sorted_df.pop('ReverseRank')
    sorted_df = sorted_df.sort_values('Rating (out of 10)', ascending=False)
    sorted_df.insert(0, 'Rank', sorted_df.pop('Rank'))

    return sorted_df


def csv_to_df(name_file):
    data = []
    with open(name_file, 'r') as f:
        datareader = csv.reader(f)
        for row_test in datareader:
            if row_test != []:
                data.append(row_test)

    # LET'S HAVE A CREATED DATA WITH SCORE FROM DF_DATA
    data_score = []
    for row in data:
        row_nk = []
        row_nk.append(row[0])
        row_nk.append(weighted_total(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9]))
        row_nk.append(row[1])
        data_score.append(row_nk)

    df = pd.DataFrame(data_score, columns=['Supplier Name', 'Rating (out of 10)', 'Amount'])
    sorted_df = df
    sorted_df['Rating (out of 10)'] = sorted_df['Rating (out of 10)'].astype(float)
    sorted_df['ReverseRank'] = sorted_df['Rating (out of 10)'].rank(method='max')
    nrows = sorted_df.shape[0]
    max_rank = sorted_df['ReverseRank'].max()
    sorted_df['Rank'] = nrows + 1 - df['ReverseRank']
    sorted_df.pop('ReverseRank')
    sorted_df = sorted_df.sort_values('Rating (out of 10)', ascending=False)
    sorted_df.insert(0, 'Rank', sorted_df.pop('Rank'))

    return sorted_df


def csv_to_df_2(name_file):
    data = []
    with open(name_file, 'r') as f:
        datareader = csv.reader(f)
        for row_test in datareader:
            if row_test != []:
                data.append(row_test)

    # LET'S HAVE A CREATED DATA WITH SCORE FROM DF_DATA
    data_score = []
    for row in data:
        row_nk = []
        row_nk.append(row[0])
        row_nk.append(weighted_total(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9]))
        row_nk.append(row[1])
        row_nk.append(row[2])
        row_nk.append(row[3])
        row_nk.append(row[4])
        row_nk.append(row[5])
        row_nk.append(row[6])
        row_nk.append(row[7])
        row_nk.append(row[8])
        row_nk.append(row[9])
        data_score.append(row_nk)

    df = pd.DataFrame(data_score,
                      columns=['Supplier Name', 'Rating (out of 10)', 'Amount ($M)', 'Criteria 1', 'Criteria 2',
                               'Criteria 3', 'Criteria 4', 'Criteria 5', 'Criteria 6', 'Criteria 7',
                               'Criteria 8']).set_index('Supplier Name')
    # df = pd.DataFrame(data_score, columns = ['Supplier Name','Rating (out of 10)'])
    sorted_df = df
    sorted_df['Rating (out of 10)'] = sorted_df['Rating (out of 10)'].astype(float)
    sorted_df['ReverseRank'] = sorted_df['Rating (out of 10)'].rank(method='max')
    nrows = sorted_df.shape[0]
    max_rank = sorted_df['ReverseRank'].max()
    sorted_df['Rank'] = nrows + 1 - df['ReverseRank']
    sorted_df['Rank'] = sorted_df['Rank'].astype(int)
    sorted_df.pop('ReverseRank')
    sorted_df.insert(1, 'Responses', ' ')
    sorted_df = sorted_df.sort_values('Rating (out of 10)', ascending=False)
    sorted_df.insert(0, 'Rank', sorted_df.pop('Rank'))
    sorted_df = sorted_df.T.reset_index()
    sorted_df.rename(columns={'index': 'Supplier'}, inplace=True)

    return sorted_df


def csv_to_df_3(name_file):
    data = []
    with open(name_file, 'r') as f:
        datareader = csv.reader(f)
        for row_test in datareader:
            if row_test != []:
                data.append(row_test)

    # LET'S HAVE A CREATED DATA WITH SCORE FROM DF_DATA
    data_score = []
    for row in data:
        row_nk = []
        row_nk.append(row[0])
        row_nk.append(weighted_total(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9]))
        row_nk.append(row[1])
        row_nk.append(row[2])
        row_nk.append(row[3])
        row_nk.append(row[4])
        row_nk.append(row[5])
        row_nk.append(row[6])
        row_nk.append(row[7])
        row_nk.append(row[8])
        row_nk.append(row[9])
        data_score.append(row_nk)

    df = pd.DataFrame(data_score,
                      columns=['Supplier Name', 'Rating (out of 10)', 'Criteria 1', 'Criteria 2', 'Criteria 3',
                               'Criteria 4', 'Criteria 5', 'Criteria 6', 'Criteria 7', 'Criteria 8'])
    sorted_df = df
    sorted_df['Rating (out of 10)'] = sorted_df['Rating (out of 10)'].astype(float)
    sorted_df['ReverseRank'] = sorted_df['Rating (out of 10)'].rank(method='max')
    nrows = sorted_df.shape[0]
    max_rank = sorted_df['ReverseRank'].max()
    sorted_df['Rank'] = nrows + 1 - df['ReverseRank']
    sorted_df['Rank'] = sorted_df['Rank'].astype(int)
    sorted_df.pop('ReverseRank')
    sorted_df = sorted_df.sort_values('Rating (out of 10)', ascending=False)
    sorted_df.insert(1, 'Rank', sorted_df.pop('Rank'))

    sorted_df['Rank'] = 'Rank: ' + sorted_df['Rank'].astype(str)
    sorted_df['Rating (out of 10)'] = 'Rating (out of 10): ' + sorted_df['Rating (out of 10)'].astype(str)
    sorted_df['Criteria 1'] = 'Criteria 1: ' + sorted_df['Criteria 1'].astype(str)
    sorted_df['Criteria 2'] = 'Criteria 2: ' + sorted_df['Criteria 2'].astype(str)
    sorted_df['Criteria 3'] = 'Criteria 3: ' + sorted_df['Criteria 3'].astype(str)
    sorted_df['Criteria 4'] = 'Criteria 4: ' + sorted_df['Criteria 4'].astype(str)
    sorted_df['Criteria 5'] = 'Criteria 5: ' + sorted_df['Criteria 5'].astype(str)
    sorted_df['Criteria 6'] = 'Criteria 6: ' + sorted_df['Criteria 6'].astype(str)
    sorted_df['Criteria 7'] = 'Criteria 7: ' + sorted_df['Criteria 7'].astype(str)
    sorted_df['Criteria 8'] = 'Criteria 8: ' + sorted_df['Criteria 8'].astype(str)

    return sorted_df


def csv_to_df_raw(name_file):
    data = []
    with open(name_file, 'r') as f:
        datareader = csv.reader(f)
        for row_test in datareader:
            if row_test != []:
                data.append(row_test)

    # LET'S HAVE A CREATED DATA WITH SCORE FROM DF_DATA
    data_score = []
    for row in data:
        row_nk = []
        row_nk.append(row[0])
        row_nk.append(weighted_total(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9]))
        data_score.append(row_nk)

    df = pd.DataFrame(data_score, columns=['Supplier Name', 'Rating (out of 10)'])
    '''sorted_df = df
    sorted_df['Rating (out of 10)'] = sorted_df['Rating (out of 10)'].astype(float)
    sorted_df['ReverseRank']=sorted_df['Rating (out of 10)'].rank(method='max')
    nrows = sorted_df.shape[0]
    max_rank = sorted_df['ReverseRank'].max()
    sorted_df['Rank'] = nrows + 1 - df['ReverseRank']
    sorted_df.pop('ReverseRank')
    sorted_df = sorted_df.sort_values('Rating (out of 10)', ascending=False)
    sorted_df.insert(0, 'Rank', sorted_df.pop('Rank'))'''

    return df


def csv_to_df_data(name_file):
    data = []
    with open(name_file, 'r') as f:
        datareader = csv.reader(f)
        for row_test in datareader:
            if row_test != []:
                data.append(row_test)

    df = pd.DataFrame(data, columns=['Supplier Name', 'amount', 'scf', 'VMI', 'critical', 'inventory', 'pay_term',
                                     'lead_time', 'business', 'overdue'])

    return df


def del_sup(name, file_name='save_sup.csv'):
    data = []
    data_new = []

    with open(file_name, 'r') as f:
        datareader = csv.reader(f)
        for row_test in datareader:
            if row_test != []:
                data.append(row_test)

    open(file_name, 'w')

    for row_b in data:
        if row_b[0] != name:
            data_new.append(row_b)

    for row_a in data_new:
        with open('save_sup.csv', 'a') as f:
            writer = csv.writer(f)
            writer.writerow(row_a)


def edit_sup(name,
             amount_,
             scf_,
             VMI_,
             critical_,
             inventory_,
             pay_term_,
             lead_time_,
             business_,
             overdue_, file_name='save_sup.csv'):
    data = []
    data_new = []

    with open(file_name, 'r') as f:
        datareader = csv.reader(f)
        for row_test in datareader:
            if row_test != []:
                data.append(row_test)

    open(file_name, 'w')

    for row_b in data:
        if row_b[0] == name:
            data_new.append([name,
                             amount_,
                             scf_,
                             VMI_,
                             critical_,
                             inventory_,
                             pay_term_,
                             lead_time_,
                             business_,
                             overdue_])
        else:
            data_new.append(row_b)

    for row_a in data_new:
        with open('save_sup.csv', 'a') as f:
            writer = csv.writer(f)
            writer.writerow(row_a)


class Supplier:
    def __init__(self, name_, amount_, scf_,
                 VMI_,
                 critical_,
                 inventory_,
                 pay_term_,
                 lead_time_,
                 business_,
                 overdue_):
        self.name_ = name_
        self.amount_ = amount_
        self.scf_ = scf_
        self.VMI_ = VMI_
        self.critical_ = critical_
        self.inventory_ = inventory_
        self.pay_term_ = pay_term_
        self.lead_time_ = lead_time_
        self.business_ = business_
        self.overdue_ = overdue_

    def add_supplier(self):
        test_length = False
        with open('save_sup.csv', 'r') as f:
            datareader = csv.reader(f)
            for row_test in datareader:
                if row_test != []:
                    if row_test[0] == self.name_:
                        test_id = True

        if test_length == False:
            row = [self.name_, self.amount_, self.scf_, self.VMI_, self.critical_, self.inventory_, self.pay_term_,
                   self.lead_time_, self.business_, self.overdue_]
            with open('save_sup.csv', 'a') as f:
                writer = csv.writer(f)
                writer.writerow(row)
                # print('Supplier : '+self.name_+'  Added')

    def save_add_tcc(self, name_client_):
        row = [name_client_, datetime.now(), self.name_, self.amount_, self.scf_, self.VMI_, self.critical_,
               self.inventory_, self.pay_term_, self.lead_time_, self.business_, self.overdue_]
        with open('historic_save.csv', 'a') as f:
            writer = csv.writer(f)
            writer.writerow(row)


def generate_color_code(value):
    max_ = 10
    percent = (value - 1) / (max_ - 1) * 100
    # calculate the red and green values based on the percentage
    red = int(255 * (100 - percent) / 100)
    green = int(255 * percent / 100)
    # format the color code as a hex string
    color_code = '#{:02x}{:02x}00'.format(red, green)
    return color_code


def weighted_total(name_,
                   amount_,
                   scf_,
                   VMI_,
                   critical_,
                   inventory_,
                   pay_term_,
                   lead_time_,
                   business_,
                   overdue_, ):
    if any([arg is None for arg in [name_,
                                    amount_,
                                    scf_,
                                    VMI_,
                                    critical_,
                                    inventory_,
                                    pay_term_,
                                    lead_time_,
                                    business_,
                                    overdue_, ]]) or name_ == '':
        # print('there is none')
        return -1

    else:

        df_wt = pd.read_csv('param_wt.csv', header=0)
        scf_wt = df_wt['scf'][0]
        VMI_wt = df_wt['VMI'][0]
        critical_wt = df_wt['critical'][0]
        inventory_wt = df_wt['inventory'][0]
        pay_term_wt = df_wt['pay_term'][0]
        lead_time_wt = df_wt['lead_time'][0]
        business_wt = df_wt['business'][0]
        overdue_wt = df_wt['overdue'][0]

        # print(scf_wt+VMI_wt+critical_wt+inventory_wt+pay_term_wt+lead_time_wt+business_wt+overdue_wt)

        if scf_wt + VMI_wt + critical_wt + inventory_wt + pay_term_wt + lead_time_wt + business_wt + overdue_wt > 1:
            # print('>1')
            return -1

        else:
            # ----------------------------------------scf
            if scf_ == 'No':
                scf = 10 * scf_wt
            else:
                scf = 0

            # ----------------------------------------VMI
            if VMI_ == 'No':
                VMI = 10 * VMI_wt
            else:
                VMI = 0

            # ----------------------------------------critical
            if critical_ == 'Yes':
                critical = 10 * critical_wt
            else:
                critical = 0

            # ----------------------------------------inventory
            if inventory_ == 'Yes':
                inventory = 10 * inventory_wt
            else:
                inventory = 0

            # ----------------------------------------pay_term
            if pay_term_ == 'No':
                pay_term = 10 * pay_term_wt
            else:
                pay_term = 0

            # ----------------------------------------lead_time
            if lead_time_ == 'Yes':
                lead_time = 10 * lead_time_wt
            else:
                lead_time = 0

            # ----------------------------------------business
            if business_ == 'Yes':
                business = 10 * business_wt
            else:
                business = 0

            # ----------------------------------------overdue
            if overdue_ == 'No':
                overdue = 10 * overdue_wt
            else:
                overdue = 0

            return (scf + VMI + critical + inventory + pay_term + lead_time + business + overdue)


def weighted_total_live(name_,
                        scf_,
                        VMI_,
                        critical_,
                        inventory_,
                        pay_term_,
                        lead_time_,
                        business_,
                        overdue_,
                        scf_wt,
                        VMI_wt,
                        critical_wt,
                        inventory_wt,
                        pay_term_wt,
                        lead_time_wt,
                        business_wt,
                        overdue_wt):
    if any([arg is None for arg in [name_,
                                    scf_,
                                    VMI_,
                                    critical_,
                                    inventory_,
                                    pay_term_,
                                    lead_time_,
                                    business_,
                                    overdue_, ]]):
        return -1

    else:
        totall = scf_wt + VMI_wt + critical_wt + inventory_wt + pay_term_wt + lead_time_wt + business_wt + overdue_wt
        if totall != 100:
            return -1

        else:
            # ----------------------------------------scf
            if scf_ == 'No':
                scf = 10 * scf_wt / 100
            else:
                scf = 0

            # ----------------------------------------VMI
            if VMI_ == 'No':
                VMI = 10 * VMI_wt / 100
            else:
                VMI = 0

            # ----------------------------------------critical
            if critical_ == 'Yes':
                critical = 10 * critical_wt / 100
            else:
                critical = 0

            # ----------------------------------------inventory
            if inventory_ == 'Yes':
                inventory = 10 * inventory_wt / 100
            else:
                inventory = 0

            # ----------------------------------------pay_term
            if pay_term_ == 'No':
                pay_term = 10 * pay_term_wt / 100
            else:
                pay_term = 0

            # ----------------------------------------lead_time
            if lead_time_ == 'Yes':
                lead_time = 10 * lead_time_wt / 100
            else:
                lead_time = 0

            # ----------------------------------------business
            if business_ == 'Yes':
                business = 10 * business_wt / 100
            else:
                business = 0

            # ----------------------------------------overdue
            if overdue_ == 'Yes':
                overdue = 10 * overdue_wt / 100
            else:
                overdue = 0

            return (scf + VMI + critical + inventory + pay_term + lead_time + business + overdue)


def bar_sup():
    df = csv_to_df('save_sup.csv')

    nb_sup = df.shape[0]

    col11 = px.bar(df, x='Rating (out of 10)', y='Supplier Name', barmode='group', text_auto=True, orientation='h',
                   height=150 + nb_sup * 150,
                   color_discrete_sequence=['#FFA41B'])

    # col11.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    col11.update_annotations(font_size=22)

    col11.update_layout(legend=dict(
        orientation="h",
        title=None,
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1,
        font=dict(
            size=18,
            color="black"
        ),
    ))

    col11.update_traces(textangle=0)

    col11.update_traces(width=0.3)

    col11.update_layout({"bargap": 0.3, 'bargroupgap': 0.12})

    col11.update_layout(xaxis=dict(tickfont=dict(size=18)))

    col11.update_layout(font=dict(size=18))

    col11.update_layout(yaxis=dict(autorange="reversed"))

    return col11


def quadrant():
    df = csv_to_df('save_sup.csv')

    df['Amount'] = df['Amount'].astype(int)
    df['color'] = 'red'

    # Create scatter plot
    fig = px.scatter(df, x='Amount', y='Rating (out of 10)', size='Amount', color_discrete_sequence=['#FFA41B'],
                     text="Supplier Name",
                     labels={"Amount": "Amount ($M)", "Rating (out of 10)": "TCC Supplier Rating"},
                     template="simple_white", height=1000, size_max=40)

    # Set quadrant boundaries
    hline_value = (int(max(df['Amount'])) + int(min(df['Amount']))) / 2
    vline_value = 5
    fig.update_layout(
        shapes=[
            dict(
                type='line',
                yref='paper', y0=0, y1=1,
                xref='x', x0=hline_value, x1=hline_value,
                line=dict(color='black', width=2)
            ),
            dict(
                type='line',
                xref='paper', x0=0, x1=1,
                yref='y', y0=vline_value, y1=vline_value,
                line=dict(color='black', width=2)
            )
        ]
    )

    fig.update_yaxes(range=[0, 10])

    # Add annotations
    annotations = []

    annotations.append(
        dict(
            x=0.15,
            y=0.25,
            xref='paper',
            yref='paper',
            text='Low priority',
            showarrow=False,
            font=dict(size=32, color='red'),
            opacity=0.12
        )
    )

    annotations.append(
        dict(
            x=0.10,
            y=0.85,
            xref='paper',
            yref='paper',
            text='Medium priority',
            showarrow=False,
            font=dict(size=32, color='blue'),
            opacity=0.12
        )
    )

    annotations.append(
        dict(
            x=0.90,
            y=0.25,
            xref='paper',
            yref='paper',
            text='Medium priority',
            showarrow=False,
            font=dict(size=32, color='blue'),
            opacity=0.12
        )
    )

    annotations.append(
        dict(
            x=0.85,
            y=0.85,
            xref='paper',
            yref='paper',
            text='High priority',
            showarrow=False,
            font=dict(size=32, color='green'),
            opacity=0.12
        )
    )

    fig.update_layout(
        coloraxis_colorbar=dict(showticklabels=False),
        annotations=annotations
    )

    # Format text above the bubbles
    fig.update_traces(
        texttemplate='%{text}',
        textposition='top center',
        textfont=dict(size=18),
        hovertemplate='Supplier: %{text}<br>Amount: $%{x}M<br>TCC Supplier Rating: %{y}<br>'
    )

    return fig


# app = dash.Dash(__name__,external_stylesheets=[dbc.themes.MINTY,dbc.icons.FONT_AWESOME, dbc.icons.BOOTSTRAP])

def create_app():
    # clear_database()
    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.MINTY, dbc.icons.FONT_AWESOME, dbc.icons.BOOTSTRAP])

    add_icon = html.I(className="fa-regular fa-floppy-disk me-2")
    clear_icon = html.I(className="fa-solid fa-trash me-2")
    change_icon = html.I(className="fa-solid fa-wrench me-2")
    warning_icon = html.I(className="fa-solid fa-circle-exclamation me-2")
    ok_icon = html.I(className="fa-solid fa-circle-check me-2")
    edit_icon = html.I(className="fa-solid fa-floppy-disk me-2")
    enter_icon = html.I(className="fa-solid fa-right-to-bracket me-2")
    dl_icon = html.I(className="fa-solid fa-download me-2")

    image_filename = 'logo.png'
    encoded_image = base64.b64encode(open(image_filename, 'rb').read())

    # Define the callback function for the page content
    @app.callback(Output('page-content', 'children'),
                  Input('url', 'pathname'))
    def display_page(pathname):
        if pathname == '/Dashboard':
            # Display the success page if the user has successfully logged in
            return app_layout
        elif pathname == '/login':
            # Display the failed login page if the user has entered an invalid username or password
            return landing_layout
        else:
            # Display the login page by default
            return landing_layout

    # Define the layout for the landing page
    landing_layout = html.Div(children=[

        html.Div(
            children=[
                html.Br(),
                html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()), style={
                    "display": "block",
                    "margin-left": "auto",
                    "margin-right": "auto",
                }),
                html.Br(),
                html.H1('Supplier selection tool - 1TCC © 2023',
                        style={'color': 'white',  # 'pading':'50px 0px 50px 0px',
                               'textAlign': 'center', 'font-family': 'sans-serif', 'fontSize': title_size, }),
                html.Br(),
            ]
            , style={'background-color': 'rgb(52, 56, 52)'}
        ),

        html.Br(),
        html.Div(children=[

            html.H1(children='App level Login'),
            html.Br(),
            html.Div(children=[
                html.Label('Username:'),
                dbc.Input(id='username-input', placeholder='Enter your username', type='text'),
            ]),
            html.Br(),
            html.Div(children=[
                html.Label('Password:'),
                dbc.Input(id='password-input', placeholder='Enter your password', type='password'),
            ]),
            html.Br(),
            dbc.Button('Enter', id='login-button', n_clicks=0, style=button_style),
            html.Div(id='login-status'),
            # html.Div(id='login-display'),

            html.Br(),

            html.Div(children=["Don't have access? ",
                               html.A("Contact 1TCC to get access", href="https://1tcc.com/tcc-contact/",
                                      target="_blank")]),

            # dbc.Button([enter_icon,"ENTER"], id='dashboard-button',
            #           color="primary", className="me-1",n_clicks=0,style=button_style)

        ], style={

            "display": "flex",
            "flex-direction": "column",
            "justify-content": "center",
            "align-items": "center",
        })

    ], style={'background-color': 'rgb(52, 56, 52)', "height": "100vh", 'width': '100%',
              'display': 'inline-block', 'align-items': 'center', 'horizontalAlign': 'center'})

    app_layout = html.Div([

        html.Div(children=[
            html.Div(children=[
                dbc.Row(
                    html.H3('Supplier Selection Tool', style={'color': 'white', 'font-family': 'sans-serif',
                                                              'fontSize': 45, 'verticalAlign': 'top',
                                                              'display': 'inline-block',
                                                              'margin': '10px 60px 10px 60px', 'width': '90',
                                                              'align-items': 'center', 'justify-content': 'left'}),
                ),

            ], style={'verticalAlign': 'top',
                      'margin': '10px', 'width': '5%',
                      'align-items': 'center', 'flex': 1,
                      'display': 'flex', 'justify-content': 'left'}),

            html.Div(children=[
                html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode())),
            ], style={'verticalAlign': 'top',
                      'margin': '10px', 'width': '5%',
                      'align-items': 'center', 'flex': 1,
                      'display': 'flex', 'justify-content': 'right'}),

        ], style={'background-color': 'rgb(52, 56, 52)', 'display': 'flex',
                  'flex': 'row', 'horizontalAlign': 'center', 'height': '120px'}, ),

        # Overall Summary
        dcc.Tabs(
            id="tabs_common_summary",
            className='custom-tabs', vertical=False,
            children=[
                dcc.Tab(label='➲ Criteria responses', value='tab_1', className='custom-tab',
                        selected_className='custom-tab--selected',
                        style={'color': 'white', 'background-color': 'rgb(117, 125, 120)',
                               'font-family': 'sans-serif'}),
                dcc.Tab(label='☷ Ranking', value='tab_3', className='custom-tab',
                        selected_className='custom-tab--selected',
                        style={'color': 'white', 'background-color': 'rgb(117, 125, 120)',
                               'font-family': 'sans-serif'}),
                dcc.Tab(label='✎ Edit or remove Supplier', value='tab_4', className='custom-tab',
                        selected_className='custom-tab--selected',
                        style={'color': 'white', 'background-color': 'rgb(117, 125, 120)',
                               'font-family': 'sans-serif'}),
                # dcc.Tab(label='⚙ Criteria weightage', value='tab_2', className='custom-tab',
                #        selected_className='custom-tab--selected',style={'color': 'white','background-color':'rgb(117, 125, 120)','font-family':'sans-serif'}),
            ], style={'font-family': 'sans-serif', 'fontSize': 25, 'color': 'red', 'height': '75px',
                      'align-items': 'center'}),

        html.Div(children=[

            html.Div(id='tab_display'),

            # FOOTER
            html.Footer(
                children=[
                    html.Br(),
                    html.H1('1TCC © 2023', style={'color': 'white',  # 'pading':'50px 0px 50px 0px',
                                                  'textAlign': 'center', 'font-family': 'sans-serif',
                                                  'fontSize': 20, }),
                    html.Br(),

                ]
                , style={'background-color': 'rgb(52, 56, 52)', "width": "100%"}

            ),

            # Closing
        ],
            style={'text-align': 'center', 'display': 'inline-block', 'width': '100%',
                   'background-color': 'rgb(245, 245, 245)', 'color': 'rgb(79, 79, 79)'})
    ])

    # Define the callback function for the button click
    # @app.callback(Output('url', 'pathname'),
    #              #Output('login-display','children'),
    #              [Input('dashboard-button', 'n_clicks'),
    #               #Input('username', 'value'),
    #               #Input('password', 'value'),
    #              ])
    # def navigate_to_dashboard(n_clicks):#,username,password):
    #    if n_clicks:
    #        reset_weightage()
    #        #clear_database()
    #        return '/Dashboard'

    # Define the callback function for the submit button
    @app.callback(Output('login-status', 'children'),
                  Output('url', 'pathname'),
                  Input('login-button', 'n_clicks'),
                  State('username-input', 'value'),
                  State('password-input', 'value'))
    def login(n_clicks, username, password):
        # Check if the username and password are valid
        if username in VALID_USERNAME_PASSWORD_PAIRS and password == VALID_USERNAME_PASSWORD_PAIRS[username]:
            # If the login is successful, redirect the user to the success page
            return '', '/Dashboard'
        else:
            # If the login fails, display a message on the login page
            return ' ', '/login'

    # Define the app's layout
    app.layout = html.Div([
        dcc.Location(id='url', refresh=False),
        html.Div(id='page-content')
    ])

    @app.callback(
        Output('tab_display', 'children'),
        Input('tabs_common_summary', 'value'),
        # Input(df_timeline_CF)
    )
    def update_styles(tab):
        if tab == 'tab_1':

            return html.Div(children=[

                html.Div(children=[

                    html.H3('Criteria response form',
                            style={'color': 'black', 'font-family': 'sans-serif', 'width': '100%',
                                   'fontSize': title_size, 'verticalAlign': 'top', 'margin': '20px 20px 20px 20px',
                                   'display': 'inline-block', 'horizontalAlign': 'center'}),

                    html.Br(),  # ---------Name

                    html.Div(children=[

                        html.H3('Supplier name:', style={'color': 'black', 'font-family': 'sans-serif',
                                                         'fontSize': body_size, 'verticalAlign': 'top', 'width': '40%',
                                                         'margin': '10px',
                                                         'align-items': 'center', 'flex': 1,
                                                         'display': 'flex', 'justify-content': 'right'}),

                        dbc.Input(id="name", placeholder="Enter supplier name", type='text',
                                  style={'color': 'blue', 'width': '20%', 'font-family': 'sans-serif',
                                         'fontSize': body_size, 'margin': '10px', 'width': '250px',
                                         'align-items': 'center', 'flex': 1,
                                         'display': 'flex', 'justify-content': 'left'}
                                  ),
                    ], style={'border': 'px solid orange', 'background-color': 'white', 'display': 'flex',
                              'border-radius': 20, 'margin': '30px', 'flex': 'row', 'horizontalAlign': 'center'}, ),

                    html.Br(),

                    html.Br(),  # ---------AMOUNT

                    html.Div(children=[
                        html.H3('Amount dealt with the supplier:', style={'color': 'black', 'font-family': 'sans-serif',
                                                                          'fontSize': body_size, 'verticalAlign': 'top',
                                                                          'margin': '10px',
                                                                          'align-items': 'center', 'flex': 1,
                                                                          'flex-direction': 'row',
                                                                          'width': '50%',
                                                                          'display': 'flex',
                                                                          'justify-content': 'right'}),

                        dbc.Input(id="amount", placeholder="Amount in $M", type='number', min=0,
                                  style={'color': 'blue', 'width': '20%', 'font-family': 'sans-serif',
                                         'fontSize': body_size, 'margin': '10px', 'width': '250px',
                                         'align-items': 'center', 'flex': 1,
                                         'display': 'flex', 'justify-content': 'left'}
                                  ),

                        html.H3(' ', style={'color': '#737373', 'font-family': 'sans-serif',
                                            'fontSize': body_size, 'verticalAlign': 'top',
                                            'margin': '10px 30px 10px 30px',
                                            'align-items': 'center', 'flex': 1, 'width': '100px',
                                            'display': 'flex', 'justify-content': 'right'}),

                    ], style={'border': 'px solid orange', 'background-color': '#f2f2f2', 'display': 'flex',
                              'border-radius': 20, 'margin': '5px 20px 5px 20px', 'flex': 'row',
                              'horizontalAlign': 'center'}, ),

                    html.Br(),  # ---------SCF

                    html.Div(children=[
                        html.H3('Criteria 1 - Supplier has access to SCF programs',
                                style={'color': 'black', 'font-family': 'sans-serif',
                                       'fontSize': body_size, 'verticalAlign': 'top',
                                       'margin': '10px',
                                       'align-items': 'center', 'flex': 1,
                                       'flex-direction': 'row',
                                       'width': '50%',
                                       'display': 'flex', 'justify-content': 'right'}),

                        dcc.RadioItems(id='scf', options={'Yes': ' Yes', 'No': ' No'}
                                       , labelStyle={'margin': "10px 20px 10px 20px"},
                                       style={'color': '#3384BA', 'font-family': 'sans-serif', 'width': '25%',
                                              'fontSize': body_size, 'margin': '10px',
                                              'align-items': 'center', 'flex': 1,
                                              'display': 'flex', 'justify-content': 'center'}),

                        html.H3('(Optimal: No)', style={'color': '#737373', 'font-family': 'sans-serif',
                                                        'fontSize': body_size, 'verticalAlign': 'top',
                                                        'margin': '10px 30px 10px 30px',
                                                        'align-items': 'center', 'flex': 1, 'width': '100px',
                                                        'display': 'flex', 'justify-content': 'right'}),

                    ], style={'border': 'px solid orange', 'background-color': '#f2f2f2', 'display': 'flex',
                              'border-radius': 20, 'margin': '5px 20px 5px 20px', 'flex': 'row',
                              'horizontalAlign': 'center'}, ),

                    html.Br(),  # ---------VMI

                    html.Div(children=[
                        html.H3('Criteria 2 - Supplier offers VMI to clients',
                                style={'color': 'black', 'font-family': 'sans-serif',
                                       'fontSize': body_size, 'verticalAlign': 'top',
                                       'margin': '10px',
                                       'align-items': 'center', 'flex': 1,
                                       'display': 'flex', 'justify-content': 'right'}),

                        dcc.RadioItems(id='VMI', options={'Yes': ' Yes', 'No': ' No'}
                                       , labelStyle={'margin': "10px 20px 10px 20px"},
                                       style={'color': '#3384BA', 'font-family': 'sans-serif', 'width': '20%',
                                              'fontSize': body_size, 'margin': '10px',
                                              'align-items': 'center', 'flex': 1,
                                              'display': 'flex', 'justify-content': 'center'}),
                        html.H3('(Optimal: No)', style={'color': '#737373', 'font-family': 'sans-serif',
                                                        'fontSize': body_size, 'verticalAlign': 'top',
                                                        'margin': '10px 30px 10px 30px',
                                                        'align-items': 'center', 'flex': 1, 'width': '25%',
                                                        'display': 'flex', 'justify-content': 'right'}),

                    ], style={'border': 'px solid orange', 'background-color': '#f2f2f2', 'display': 'flex',
                              'border-radius': 20, 'margin': '5px 20px 5px 20px', 'flex': 'row',
                              'horizontalAlign': 'center'}, ),

                    html.Br(),  # ---------Critical

                    html.Div(children=[
                        html.H3('Criteria 3 - Supplier is critical for client',
                                style={'color': 'black', 'font-family': 'sans-serif',
                                       'fontSize': body_size, 'verticalAlign': 'top',
                                       'margin': '10px',
                                       'align-items': 'center', 'flex': 1,
                                       'display': 'flex', 'justify-content': 'right'}),

                        dcc.RadioItems(id='critical', options={'Yes': ' Yes', 'No': ' No'}
                                       , labelStyle={'margin': "10px 20px 10px 20px"},
                                       style={'color': '#3384BA', 'font-family': 'sans-serif', 'width': '20%',
                                              'fontSize': body_size, 'margin': '10px',
                                              'align-items': 'center', 'flex': 1,
                                              'display': 'flex', 'justify-content': 'center'}),
                        html.H3('(Optimal: Yes)', style={'color': '#737373', 'font-family': 'sans-serif',
                                                         'fontSize': body_size, 'verticalAlign': 'top',
                                                         'margin': '10px 30px 10px 30px',
                                                         'align-items': 'center', 'flex': 1, 'width': '25%',
                                                         'display': 'flex', 'justify-content': 'right'}),

                    ], style={'border': 'px solid orange', 'background-color': '#f2f2f2', 'display': 'flex',
                              'border-radius': 20, 'margin': '5px 20px 5px 20px', 'flex': 'row',
                              'horizontalAlign': 'center'}, ),

                    html.Br(),  # ---------inventory

                    html.Div(children=[
                        html.H3('Criteria 4 - Supplier inventory is within top 25 of total Client inventory',
                                style={'color': 'black', 'font-family': 'sans-serif',
                                       'fontSize': body_size, 'verticalAlign': 'top',
                                       'margin': '10px',
                                       'align-items': 'center', 'flex': 1,
                                       'display': 'flex', 'justify-content': 'right'}),

                        dcc.RadioItems(id='inventory', options={'Yes': ' Yes', 'No': ' No'}
                                       , labelStyle={'margin': "10px 20px 10px 20px"},
                                       style={'color': '#3384BA', 'font-family': 'sans-serif', 'width': '20%',
                                              'fontSize': body_size, 'margin': '10px',
                                              'align-items': 'center', 'flex': 1,
                                              'display': 'flex', 'justify-content': 'center'}),
                        html.H3('(Optimal: Yes)', style={'color': '#737373', 'font-family': 'sans-serif',
                                                         'fontSize': body_size, 'verticalAlign': 'top',
                                                         'margin': '10px 30px 10px 30px',
                                                         'align-items': 'center', 'flex': 1, 'width': '25%',
                                                         'display': 'flex', 'justify-content': 'right'}),

                    ], style={'border': 'px solid orange', 'background-color': '#f2f2f2', 'display': 'flex',
                              'border-radius': 20, 'margin': '5px 20px 5px 20px', 'flex': 'row',
                              'horizontalAlign': 'center'}, ),

                    html.Br(),  # -----------------------------------------------pay_term

                    html.Div(children=[
                        html.H3('Criteria 5 - Payment terms are below 45 days',
                                style={'color': 'black', 'font-family': 'sans-serif',
                                       'fontSize': body_size, 'verticalAlign': 'top',
                                       'margin': '10px',
                                       'align-items': 'center', 'flex': 1,
                                       'display': 'flex', 'justify-content': 'right'}),

                        dcc.RadioItems(id='pay_term', options={'Yes': ' Yes', 'No': ' No'}
                                       , labelStyle={'margin': "10px 20px 10px 20px"},
                                       style={'color': '#3384BA', 'font-family': 'sans-serif', 'width': '20%',
                                              'fontSize': body_size, 'margin': '10px',
                                              'align-items': 'center', 'flex': 1,
                                              'display': 'flex', 'justify-content': 'center'}),
                        html.H3('(Optimal: No)', style={'color': '#737373', 'font-family': 'sans-serif',
                                                        'fontSize': body_size, 'verticalAlign': 'top',
                                                        'margin': '10px 30px 10px 30px',
                                                        'align-items': 'center', 'flex': 1, 'width': '25%',
                                                        'display': 'flex', 'justify-content': 'right'}),

                    ], style={'border': 'px solid orange', 'background-color': '#f2f2f2', 'display': 'flex',
                              'border-radius': 20, 'margin': '5px 20px 5px 20px', 'flex': 'row',
                              'horizontalAlign': 'center'}, ),

                    html.Br(),  # -----------------------------------------------lead_time

                    html.Div(children=[
                        html.H3('Criteria 6 - Lead times are 90+ days',
                                style={'color': 'black', 'font-family': 'sans-serif',
                                       'fontSize': body_size, 'verticalAlign': 'top',
                                       'margin': '10px',
                                       'align-items': 'center', 'flex': 1,
                                       'display': 'flex', 'justify-content': 'right'}),

                        dcc.RadioItems(id='lead_time', options={'Yes': ' Yes', 'No': ' No'}
                                       , labelStyle={'margin': "10px 20px 10px 20px"},
                                       style={'color': '#3384BA', 'font-family': 'sans-serif', 'width': '20%',
                                              'fontSize': body_size, 'margin': '10px',
                                              'align-items': 'center', 'flex': 1,
                                              'display': 'flex', 'justify-content': 'center'}),
                        html.H3('(Optimal: Yes)', style={'color': '#737373', 'font-family': 'sans-serif',
                                                         'fontSize': body_size, 'verticalAlign': 'top',
                                                         'margin': '10px 30px 10px 30px',
                                                         'align-items': 'center', 'flex': 1, 'width': '25%',
                                                         'display': 'flex', 'justify-content': 'right'}),

                    ], style={'border': 'px solid orange', 'background-color': '#f2f2f2', 'display': 'flex',
                              'border-radius': 20, 'margin': '5px 20px 5px 20px', 'flex': 'row',
                              'horizontalAlign': 'center'}, ),

                    html.Br(),  # -----------------------------------------------business

                    html.Div(children=[
                        html.H3('Criteria 7 - Client business is  within top 10 of supplier business',
                                style={'color': 'black', 'font-family': 'sans-serif',
                                       'fontSize': body_size, 'verticalAlign': 'top',
                                       'margin': '10px',
                                       'align-items': 'center', 'flex': 1,
                                       'display': 'flex', 'justify-content': 'right'}),

                        dcc.RadioItems(id='business', options={'Yes': ' Yes', 'No': ' No'}
                                       , labelStyle={'margin': "10px 20px 10px 20px"},
                                       style={'color': '#3384BA', 'font-family': 'sans-serif', 'width': '20%',
                                              'fontSize': body_size, 'margin': '10px',
                                              'align-items': 'center', 'flex': 1,
                                              'display': 'flex', 'justify-content': 'center'}),
                        html.H3('(Optimal: Yes)', style={'color': '#737373', 'font-family': 'sans-serif',
                                                         'fontSize': body_size, 'verticalAlign': 'top',
                                                         'margin': '10px 30px 10px 30px',
                                                         'align-items': 'center', 'flex': 1, 'width': '25%',
                                                         'display': 'flex', 'justify-content': 'right'}),

                    ], style={'border': 'px solid orange', 'background-color': '#f2f2f2', 'display': 'flex',
                              'border-radius': 20, 'margin': '5px 20px 5px 20px', 'flex': 'row',
                              'horizontalAlign': 'center'}, ),

                    html.Br(),  # -----------------------------------------------overdue

                    html.Div(children=[
                        html.H3('Criteria 8 - Supplier Invoices overdue 30+ days',
                                style={'color': 'black', 'font-family': 'sans-serif',
                                       'fontSize': body_size, 'verticalAlign': 'top',
                                       'margin': '10px',
                                       'align-items': 'center', 'flex': 1,
                                       'display': 'flex', 'justify-content': 'right'}),

                        dcc.RadioItems(id='overdue', options={'Yes': ' Yes', 'No': ' No'}
                                       , labelStyle={'margin': "10px 20px 10px 20px"},
                                       style={'color': '#3384BA', 'font-family': 'sans-serif', 'width': '20%',
                                              'fontSize': body_size, 'margin': '10px',
                                              'align-items': 'center', 'flex': 1,
                                              'display': 'flex', 'justify-content': 'center'}),
                        html.H3('(Optimal: No)', style={'color': '#737373', 'font-family': 'sans-serif',
                                                        'fontSize': body_size, 'verticalAlign': 'top',
                                                        'margin': '10px 30px 10px 30px',
                                                        'align-items': 'center', 'flex': 1, 'width': '25%',
                                                        'display': 'flex', 'justify-content': 'right'}),

                    ], style={'border': 'px solid orange', 'background-color': '#f2f2f2', 'display': 'flex',
                              'border-radius': 20, 'margin': '5px 20px 5px 20px', 'flex': 'row',
                              'horizontalAlign': 'center'}, ),

                    html.Br(),

                    html.Br(),

                    html.Div(id='supplier_score'),

                ], style={'width': '95%', 'border': 'px solid orange', 'box-shadow': '5px 5px 15px 8px lightgrey',
                          'background-color': 'white', 'display': 'inline-block',
                          'border-radius': 20, 'margin': '50px', 'padding': '50px'}),

                html.Br(), ])

        # --------------------------------------------DECISION REMOVE WEIGHTAGE TAB
        # elif tab=='tab_2':
        #    return html.Div(id='change_param')

        elif tab == 'tab_3':
            return html.Div(dcc.Loading(
                id="supplier_table",
                type="dot",
                className="loading-component",
            ), )

        elif tab == 'tab_4':
            df_ = csv_to_df_raw('save_sup.csv')
            if df_.shape[0] == 0:
                return html.H3('No supplier is currently ranked, go to -- Criteria responses tab and enter responses',
                               style={'color': '#383838', 'font-family': 'sans-serif',
                                      'fontSize': 22, 'verticalAlign': 'top', 'margin': '50px',
                                      'display': 'inline-block', 'horizontalAlign': 'center',
                                      'border': '0px solid orange', 'background-color': 'white',
                                      'display': 'inline-block',
                                      'border-radius': 20, 'horizontalAlign': 'center', 'padding': '50px'}),
            else:
                return html.Div(children=[
                    html.H3('Supplier List', style={'color': 'black', 'font-family': 'sans-serif', 'width': '300px',
                                                    'fontSize': title_size, 'verticalAlign': 'top', 'margin': '50px',
                                                    'display': 'inline-block', 'horizontalAlign': 'center'}),

                    html.Br(),

                    DataTable(
                        id='datatable-modify',
                        columns=[
                            {"name": i, "id": i, "selectable": True} for i in df_.columns
                        ],
                        data=df_.to_dict('records'),
                        editable=True,
                        style_cell={'padding': '10px', 'font-family': 'sans-serif', 'fontSize': 24},
                        sort_action="native",
                        sort_mode="multi",
                        # style_table={'maxWidth':'500px','overflowX': 'scroll'},
                        row_selectable="single",
                        page_action="native",
                        page_current=0,
                        page_size=50,
                    ),

                    dbc.Button([clear_icon, "Remove all"], id='button_clear_table_2',
                               color="secondary", className="me-1", n_clicks=0,
                               style={'margin': '30px', 'fontSize': 16, 'font-family': 'sans-serif', }),

                    html.Div(id='clear_table_click_2'),
                    html.Br(),

                    html.Div(id='modify_render')
                ], style={'margin': '50px'})

    @app.callback(
        Output('modify_render', 'children'),
        Input('datatable-modify', 'selected_rows')
    )
    def clicks(datatable_modify):
        df_ = csv_to_df_data('save_sup.csv')
        if datatable_modify == None:
            return html.Label([warning_icon, 'Select to modify'],
                              style={'font-family': 'sans-serif', 'fontSize': 22, 'color': 'red',
                                     'width': '500px', 'display': 'inline-block', 'verticalAlign': 'middle',
                                     'margin': '50px'  # 'height':'40px'
                                     }),
        else:
            selection_name = list(df_.loc[datatable_modify, 'Supplier Name'])
            selection_amount = list(df_.loc[datatable_modify, 'amount'])
            selection_scf = list(df_.loc[datatable_modify, 'scf'])
            selection_VMI = list(df_.loc[datatable_modify, 'VMI'])
            selection_inventory = list(df_.loc[datatable_modify, 'inventory'])
            selection_overdue = list(df_.loc[datatable_modify, 'overdue'])
            selection_pay_term = list(df_.loc[datatable_modify, 'pay_term'])
            selection_business = list(df_.loc[datatable_modify, 'business'])
            selection_lead_time = list(df_.loc[datatable_modify, 'lead_time'])
            selection_critical = list(df_.loc[datatable_modify, 'critical'])

            return html.Div(children=[

                html.Br(),
                html.Div(children=[

                    html.H3('Edit: ' + selection_name[0],
                            style={'color': 'black', 'font-family': 'sans-serif', 'width': '500px',
                                   'fontSize': 28, 'verticalAlign': 'top', 'margin': '20px 20px 20px 20px',
                                   'display': 'inline-block', 'horizontalAlign': 'center'}),

                    html.Br(),

                    dbc.Input(id='name_edit', value=selection_name[0], disabled=True
                              , style={'color': 'black', 'fontSize': 0, 'margin': '0px', 'width': '0px',
                                       'display': 'inline-block', 'horizontalAlign': 'center'}),

                    html.Br(),  # ---------AMOUNT

                    html.Div(children=[
                        html.H3('Amount dealt', style={'color': 'black', 'font-family': 'sans-serif',
                                                       'fontSize': body_size, 'verticalAlign': 'top',
                                                       'margin': '10px',
                                                       'align-items': 'center', 'flex': 1,
                                                       'display': 'flex', 'justify-content': 'right'}),

                        dbc.Input(id="amount_edit", placeholder="Amount in $M", type='number', min=0,
                                  value=selection_amount[0],
                                  style={'color': 'blue', 'width': '20%', 'font-family': 'sans-serif',
                                         'fontSize': body_size, 'margin': '10px', 'width': '250px',
                                         'align-items': 'center', 'flex': 1,
                                         'display': 'flex', 'justify-content': 'left'}
                                  ),

                    ], style={'border': 'px solid orange', 'background-color': '#f2f2f2', 'display': 'flex',
                              'border-radius': 20, 'margin': '5px 20px 5px 20px', 'flex': 'row',
                              'horizontalAlign': 'center'}, ),

                    html.Br(),  # ---------SCF

                    html.Div(children=[
                        html.H3('Does supplier have SCF now via banks?',
                                style={'color': 'black', 'font-family': 'sans-serif',
                                       'fontSize': body_size, 'verticalAlign': 'top',
                                       'margin': '10px',
                                       'align-items': 'center', 'flex': 1,
                                       'display': 'flex', 'justify-content': 'right'}),

                        dcc.Dropdown(id='scf_edit', value=selection_scf[0], options={'Yes': 'Yes', 'No': 'No'},
                                     searchable=False
                                     , style={'color': 'black', 'font-family': 'sans-serif',
                                              'fontSize': body_size, 'margin': '10px', 'width': '250px',
                                              'align-items': 'center', 'flex': 1,
                                              'display': 'flex', 'justify-content': 'left'}),

                    ], style={'border': 'px solid orange', 'background-color': '#f2f2f2', 'display': 'flex',
                              'border-radius': 20, 'margin': '5px 20px 5px 20px', 'flex': 'row',
                              'horizontalAlign': 'center'}, ),

                    html.Br(),  # ---------VMI

                    html.Div(children=[
                        html.H3('Does Supplier currently have VMI agreement with Customer?',
                                style={'color': 'black', 'font-family': 'sans-serif',
                                       'fontSize': body_size, 'verticalAlign': 'top',
                                       'margin': '10px',
                                       'align-items': 'center', 'flex': 1,
                                       'display': 'flex', 'justify-content': 'right'}),

                        dcc.Dropdown(id='VMI_edit', value=selection_VMI[0], options={'Yes': 'Yes', 'No': 'No'},
                                     searchable=False
                                     , style={'color': 'black', 'font-family': 'sans-serif',
                                              'fontSize': body_size, 'margin': '10px', 'width': '250px',
                                              'align-items': 'center', 'flex': 1,
                                              'display': 'flex', 'justify-content': 'left'}),

                    ], style={'border': 'px solid orange', 'background-color': '#f2f2f2', 'display': 'flex',
                              'border-radius': 20, 'margin': '5px 20px 5px 20px', 'flex': 'row',
                              'horizontalAlign': 'center'}, ),

                    html.Br(),  # ---------Critical

                    html.Div(children=[
                        html.H3('Is Supplier  a critical supplier  in Client view?',
                                style={'color': 'black', 'font-family': 'sans-serif',
                                       'fontSize': body_size, 'verticalAlign': 'top',
                                       'margin': '10px',
                                       'align-items': 'center', 'flex': 1,
                                       'display': 'flex', 'justify-content': 'right'}),

                        dcc.Dropdown(id='critical_edit', value=selection_critical[0],
                                     options={'Yes': 'Yes', 'No': 'No'}, searchable=False
                                     , style={'color': 'black', 'font-family': 'sans-serif',
                                              'fontSize': body_size, 'margin': '10px', 'width': '250px',
                                              'align-items': 'center', 'flex': 1,
                                              'display': 'flex', 'justify-content': 'left'}),

                    ], style={'border': 'px solid orange', 'background-color': '#f2f2f2', 'display': 'flex',
                              'border-radius': 20, 'margin': '5px 20px 5px 20px', 'flex': 'row',
                              'horizontalAlign': 'center'}, ),

                    html.Br(),  # ---------inventory

                    html.Div(children=[
                        html.H3('Is Supplier inventory  greater than  20% of Client  total inventory?',
                                style={'color': 'black', 'font-family': 'sans-serif',
                                       'fontSize': body_size, 'verticalAlign': 'top',
                                       'margin': '10px',
                                       'align-items': 'center', 'flex': 1,
                                       'display': 'flex', 'justify-content': 'right'}),

                        dcc.Dropdown(id='inventory_edit', value=selection_inventory[0],
                                     options={'Yes': 'Yes', 'No': 'No'}, searchable=False
                                     , style={'color': 'black', 'font-family': 'sans-serif',
                                              'fontSize': body_size, 'margin': '10px', 'width': '250px',
                                              'align-items': 'center', 'flex': 1,
                                              'display': 'flex', 'justify-content': 'left'}),

                    ], style={'border': 'px solid orange', 'background-color': '#f2f2f2', 'display': 'flex',
                              'border-radius': 20, 'margin': '5px 20px 5px 20px', 'flex': 'row',
                              'horizontalAlign': 'center'}, ),

                    html.Br(),  # -----------------------------------------------pay_term

                    html.Div(children=[
                        html.H3('Is payment terms to supplier 45 days or less?',
                                style={'color': 'black', 'font-family': 'sans-serif',
                                       'fontSize': body_size, 'verticalAlign': 'top',
                                       'margin': '10px',
                                       'align-items': 'center', 'flex': 1,
                                       'display': 'flex', 'justify-content': 'right'}),

                        dcc.Dropdown(id='pay_term_edit', value=selection_pay_term[0],
                                     options={'Yes': 'Yes', 'No': 'No'}, searchable=False
                                     , style={'color': 'black', 'font-family': 'sans-serif',
                                              'fontSize': body_size, 'margin': '10px', 'width': '250px',
                                              'align-items': 'center', 'flex': 1,
                                              'display': 'flex', 'justify-content': 'left'}),

                    ], style={'border': 'px solid orange', 'background-color': '#f2f2f2', 'display': 'flex',
                              'border-radius': 20, 'margin': '5px 20px 5px 20px', 'flex': 'row',
                              'horizontalAlign': 'center'}, ),

                    html.Br(),  # -----------------------------------------------lead_time

                    html.Div(children=[
                        html.H3('Is Supplier Lead time  > 90 days?',
                                style={'color': 'black', 'font-family': 'sans-serif',
                                       'fontSize': body_size, 'verticalAlign': 'top',
                                       'margin': '10px',
                                       'align-items': 'center', 'flex': 1,
                                       'display': 'flex', 'justify-content': 'right'}),

                        dcc.Dropdown(id='lead_time_edit', value=selection_lead_time[0],
                                     options={'Yes': 'Yes', 'No': 'No'}, searchable=False
                                     , style={'color': 'black', 'font-family': 'sans-serif',
                                              'fontSize': body_size, 'margin': '10px', 'width': '250px',
                                              'align-items': 'center', 'flex': 1,
                                              'display': 'flex', 'justify-content': 'left'}),

                    ], style={'border': 'px solid orange', 'background-color': '#f2f2f2', 'display': 'flex',
                              'border-radius': 20, 'margin': '5px 20px 5px 20px', 'flex': 'row',
                              'horizontalAlign': 'center'}, ),

                    html.Br(),  # -----------------------------------------------business

                    html.Div(children=[
                        html.H3('Is Client business  greater than  20%  of Supplier total business?',
                                style={'color': 'black', 'font-family': 'sans-serif',
                                       'fontSize': body_size, 'verticalAlign': 'top',
                                       'margin': '10px',
                                       'align-items': 'center', 'flex': 1,
                                       'display': 'flex', 'justify-content': 'right'}),

                        dcc.Dropdown(id='business_edit', value=selection_business[0],
                                     options={'Yes': 'Yes', 'No': 'No'}, searchable=False
                                     , style={'color': 'black', 'font-family': 'sans-serif',
                                              'fontSize': body_size, 'margin': '10px', 'width': '250px',
                                              'align-items': 'center', 'flex': 1,
                                              'display': 'flex', 'justify-content': 'left'}),

                    ], style={'border': 'px solid orange', 'background-color': '#f2f2f2', 'display': 'flex',
                              'border-radius': 20, 'margin': '5px 20px 5px 20px', 'flex': 'row',
                              'horizontalAlign': 'center'}, ),

                    html.Br(),  # -----------------------------------------------overdue

                    html.Div(children=[
                        html.H3('Are supplier Invoices overdue by 30 days or greater?',
                                style={'color': 'black', 'font-family': 'sans-serif',
                                       'fontSize': body_size, 'verticalAlign': 'top',
                                       'margin': '10px',
                                       'align-items': 'center', 'flex': 1,
                                       'display': 'flex', 'justify-content': 'right'}),

                        dcc.Dropdown(id='overdue_edit', value=selection_overdue[0], options={'Yes': 'Yes', 'No': 'No'},
                                     searchable=False
                                     , style={'color': 'black', 'font-family': 'sans-serif',
                                              'fontSize': body_size, 'margin': '10px', 'width': '250px',
                                              'align-items': 'center', 'flex': 1,
                                              'display': 'flex', 'justify-content': 'left'}),

                    ], style={'border': 'px solid orange', 'background-color': '#f2f2f2', 'display': 'flex',
                              'border-radius': 20, 'margin': '5px 20px 5px 20px', 'flex': 'row',
                              'horizontalAlign': 'center'}, ),

                    html.Br(),

                    dbc.Button([edit_icon, "Save"], id='button_edit_sup', color="primary", className="me-1", n_clicks=0,
                               style={'margin': '20px 20px 20px 20px'}),
                    dbc.Button([clear_icon, "Remove"], id='button_del_sup', color="secondary", className="me-1",
                               n_clicks=0,
                               style={'margin': '20px 20px 20px 20px'}),
                    html.Div(id='button-clicks-edit'),
                    html.Div(id='button-clicks-del'),

                ], style={'width': '95%', 'border': 'px solid orange', 'box-shadow': '5px 5px 15px 8px lightgrey',
                          'background-color': 'white', 'display': 'inline-block',
                          'border-radius': 20, 'margin': '50px', 'padding': '50px'},

                )
            ])

    @app.callback(
        Output('supplier_score', 'children'),
        Input('name', 'value'),
        Input('amount', 'value'),
        Input('scf', 'value'),
        Input('VMI', 'value'),
        Input('critical', 'value'),
        Input('inventory', 'value'),
        Input('pay_term', 'value'),
        Input('lead_time', 'value'),
        Input('business', 'value'),
        Input('overdue', 'value')
    )
    def sup_score(name_,
                  amount_,
                  scf_,
                  VMI_,
                  critical_,
                  inventory_,
                  pay_term_,
                  lead_time_,
                  business_,
                  overdue_, ):
        # process score:
        score = weighted_total(name_,
                               amount_,
                               scf_,
                               VMI_,
                               critical_,
                               inventory_,
                               pay_term_,
                               lead_time_,
                               business_,
                               overdue_, )
        color = generate_color_code(score)

        nb_sup = test_length('save_sup.csv')
        if nb_sup == False:
            return html.Div(children=[html.Div(children=[
                html.Label([warning_icon,
                            'You reached the maximum of 10 suppliers in the ranking -- Clear the table or remove some to rank other ones'],
                           style={'font-family': 'sans-serif', 'fontSize': 22, 'color': 'red',
                                  'width': '80%', 'display': 'inline-block', 'verticalAlign': 'middle',
                                  'margin': '15px 15px 15px 15px'  # 'height':'40px'
                                  })
            ], style={'border': '0px solid orange', 'background-color': '#ffebeb', 'display': 'inline-block',
                      'border-radius': 20, 'horizontalAlign': 'center', 'margin': '15px 15px 15px 15px'}), ])

        else:

            if score < 0:
                return html.Div(children=[html.Div(children=[
                    html.Label([warning_icon, 'Please answer all the fields'],
                               style={'font-family': 'sans-serif', 'fontSize': 22, 'color': 'red',
                                      'width': '500px', 'display': 'inline-block', 'verticalAlign': 'middle',
                                      'margin': '15px 15px 15px 15px'  # 'height':'40px'
                                      }),
                ], style={'border': '0px solid orange', 'background-color': '#ffebeb', 'display': 'inline-block',
                          'border-radius': 20, 'horizontalAlign': 'center', 'margin': '15px 15px 15px 15px'}), ])
            else:
                if check_duplicate(name_) == True:
                    return html.Div(children=[html.Div(children=[
                        html.Label([warning_icon, 'This supplier already exist in the ranking'],
                                   style={'font-family': 'sans-serif', 'fontSize': 22, 'color': 'orange',
                                          'width': '500px', 'display': 'inline-block', 'verticalAlign': 'middle',
                                          'margin': '15px 15px 15px 15px'  # 'height':'40px'
                                          }),
                    ], style={'border': '0px solid orange', 'background-color': '#ffecd9', 'display': 'inline-block',
                              'border-radius': 20, 'horizontalAlign': 'center', 'margin': '15px 15px 15px 15px'}), ])

                else:
                    return html.Div(children=[html.Div(children=[
                        html.Label('Supplier score:',
                                   style={'font-family': 'sans-serif', 'fontSize': 20, 'color': 'black',
                                          'width': '500px', 'display': 'inline-block', 'verticalAlign': 'middle',
                                          # 'height':'40px'
                                          }),
                        html.Div(children=[
                            html.Label(str(score) + '/10',
                                       style={'font-family': 'sans-serif', 'fontSize': 20, 'color': 'blue',
                                              'display': 'inline-block', 'verticalAlign': 'middle',  # 'height':'40px'
                                              }),
                            html.Div(children=[html.H3('.', style={'fontSize': 0}), ],
                                     style={'width': '30px', 'height': '30px', 'display': 'inline-block',
                                            'margin': '0px 5px 0px 5px',
                                            'color': 'blue', 'horizontalAlign': 'right', 'verticalAlign': 'middle',
                                            'border': '0px solid orange', 'border-radius': 30,
                                            'font-family': 'sans-serif', 'fontSize': 20, 'background-color': color}),
                        ], style={'margin': '10px 10px 10px 10px'}),

                        # dcc.Location(id='button-clicks', refresh=False),

                        dbc.Button([add_icon, "Save & Rank supplier"], id='button_rank_supplier',
                                   color="primary", className="me-1", n_clicks=0,
                                   style={'margin': '20px 20px 20px 20px', 'fontSize': 16,
                                          'font-family': 'sans-serif', }),
                        # html.Div(id='button-clicks'),
                        html.Div(id='add_sup_click'),
                    ]),
                    ], style={'border': '0px solid orange', 'background-color': '#dff7e5', 'display': 'inline-block',
                              'border-radius': 20, 'horizontalAlign': 'center', 'margin': '15px 15px 15px 15px',
                              'padding': '15px 15px 15px 15px'})

    @app.callback(
        [Output('add_sup_click', 'children'),
         Output('tabs_common_summary', 'value')],
        [Input('button_rank_supplier', 'n_clicks'),
         Input('name', 'value'),
         Input('amount', 'value'),
         Input('scf', 'value'),
         Input('VMI', 'value'),
         Input('critical', 'value'),
         Input('inventory', 'value'),
         Input('pay_term', 'value'),
         Input('lead_time', 'value'),
         Input('business', 'value'),
         Input('overdue', 'value')])
    def clicks(n_clicks,
               name,
               amount,
               scf_,
               VMI_,
               critical_,
               inventory_,
               pay_term_,
               lead_time_,
               business_,
               overdue_):

        if n_clicks > 0:
            sup = Supplier(name, amount, scf_, VMI_, critical_, inventory_, pay_term_, lead_time_, business_, overdue_)
            sup.add_supplier()
            sup.save_add_tcc('unknown_user')
            return html.H3([ok_icon, 'added -- RELOAD the page to update the ranking or add another supplier'],
                           style={'color': 'green', 'font-family': 'sans-serif',
                                  'fontSize': 18, 'verticalAlign': 'top', 'margin': '10px',
                                  'display': 'inline-block', 'horizontalAlign': 'center'}), 'tab_1'

    @app.callback(
        Output('supplier_table', 'children'),
        Input('tabs_common_summary', 'value'),
    )
    def sup_score(tab):
        df_sup = csv_to_df_2('save_sup.csv')
        if df_sup.shape[1] == 1:
            return html.H3('No supplier is currently ranked, go to -- Criteria responses tab and enter responses',
                           style={'color': '#383838', 'font-family': 'sans-serif',
                                  'fontSize': 22, 'verticalAlign': 'top', 'margin': '50px',
                                  'display': 'inline-block', 'horizontalAlign': 'center',
                                  'border': '0px solid orange', 'background-color': 'white', 'display': 'inline-block',
                                  'border-radius': 20, 'horizontalAlign': 'center', 'padding': '50px'}),
        else:
            return html.Div([
                html.H3('Supplier Ranking', style={'color': 'black', 'font-family': 'sans-serif', 'width': '300px',
                                                   'fontSize': title_size, 'verticalAlign': 'top',
                                                   'margin': '0px 50px 50px 50px',
                                                   'display': 'inline-block', 'horizontalAlign': 'center'}),

                html.Br(),
                DataTable(
                    id='datatable_1',
                    columns=[
                        {"name": str(i), "id": str(i), "deletable": True, "selectable": True} for i in df_sup.columns
                    ],
                    data=df_sup.reset_index().to_dict('records'),

                    sort_action="native",
                    sort_mode="multi",
                    style_header={
                        'backgroundColor': 'rgb(117, 125, 120)',
                        'fontWeight': 'bold',
                        'color': 'white'
                    },
                    style_data_conditional=[
                        {
                            'if': {
                                'filter_query': '{Supplier} contains "Responses"'
                            },
                            'backgroundColor': 'rgb(117, 125, 120)',
                            'fontWeight': 'bold',
                            'color': 'white'
                        },
                        {
                            'if': {
                                'filter_query': '{Supplier} contains "Rank"'
                            },
                            'backgroundColor': '#c7c7c7',
                            'color': 'black'
                        },
                        {
                            'if': {
                                'filter_query': '{Supplier} contains "Rating (out of 10)"'
                            },
                            'backgroundColor': '#c7c7c7',
                            'color': 'black'
                        }
                    ],
                    style_cell={'padding': '10px', 'font-family': 'sans-serif', 'fontSize': 24},
                    style_table={'maxWidth': '100%', 'overflowX': 'scroll'},
                    selected_columns=[],
                    selected_rows=[],
                    page_action="native",
                    page_current=0,
                    page_size=50,
                ),

                html.Br(),
                dcc.Graph(
                    id='rank-graph',
                    figure=quadrant()
                ),

                html.Br(),
                # html.A(, id='download-link', download="ranking_supplier_TCC.csv", href="", target="_blank"),
                html.A([dl_icon, 'Download ranking'], id='download-link', download="ranking_supplier_TCC.xlsx", href="",
                       target="_blank"),
                # html.Br(),
                dbc.Button([clear_icon, "Clear ranking"], id='button_clear_table',
                           color="secondary", className="me-1", n_clicks=0,
                           style={'margin': '20px 20px 20px 20px', 'fontSize': 16, 'font-family': 'sans-serif', }),

                html.Div(id='clear_table_click'),

            ], style={'border': 'px solid orange', 'background-color': 'white',
                      'display': 'inline-block', 'width': '95%', 'box-shadow': '5px 5px 15px 8px lightgrey',
                      'border-radius': 20, 'margin': '50px', 'horizontalAlign': 'center', 'padding': '50px'}),

    @app.callback(
        Output('supplier_table_2', 'children'),
        [Input('scf_wt', 'value'),
         Input('VMI_wt', 'value'),
         Input('critical_wt', 'value'),
         Input('inventory_wt', 'value'),
         Input('pay_term_wt', 'value'),
         Input('lead_time_wt', 'value'),
         Input('business_wt', 'value'),
         Input('overdue_wt', 'value')],
    )
    def sup_score_2(scf_wt,
                    VMI_wt,
                    critical_wt,
                    inventory_wt,
                    pay_term_wt,
                    lead_time_wt,
                    business_wt,
                    overdue_wt):

        df_sup = csv_to_df_live('save_sup.csv',
                                scf_wt,
                                VMI_wt,
                                critical_wt,
                                inventory_wt,
                                pay_term_wt,
                                lead_time_wt,
                                business_wt,
                                overdue_wt)

        if df_sup.empty:
            pass
        else:
            return html.Div([
                html.H3('Supplier Ranking', style={'color': 'black', 'font-family': 'sans-serif', 'width': '300px',
                                                   'fontSize': title_size, 'verticalAlign': 'top', 'margin': '50px',
                                                   'display': 'inline-block', 'horizontalAlign': 'center'}),

                html.Br(),
                DataTable(
                    id='datatable_2',
                    columns=[
                        {"name": i, "id": i, "deletable": True, "selectable": True} for i in df_sup.columns
                    ],
                    data=df_sup.to_dict('records'),
                    # editable=True,
                    # filter_action="disable",
                    sort_action="native",
                    sort_mode="multi",
                    # column_selectable="single",
                    # row_selectable="single",
                    # row_deletable=True,
                    style_cell={'padding': '10px', 'font-family': 'sans-serif', 'fontSize': 24},
                    selected_columns=[],
                    selected_rows=[],
                    page_action="native",
                    page_current=0,
                    page_size=50,
                ),

            ], style={'margin': '50px'}),

    @app.callback(Output('clear_table_click', 'children'), [Input('button_clear_table', 'n_clicks')])
    def clicks(n_clicks):

        if n_clicks > 0:
            clear_database()
            return html.H3([ok_icon, 'Ranking cleared -- RELOAD the page'],
                           style={'color': 'grey', 'font-family': 'sans-serif',
                                  'fontSize': 18, 'verticalAlign': 'top', 'margin': '10px',
                                  'display': 'inline-block', 'horizontalAlign': 'center'}),

    @app.callback(Output('clear_table_click_2', 'children'), [Input('button_clear_table_2', 'n_clicks')])
    def clicks(n_clicks):

        if n_clicks > 0:
            clear_database()
            return html.H3([ok_icon, 'Ranking cleared -- RELOAD the page'],
                           style={'color': 'grey', 'font-family': 'sans-serif',
                                  'fontSize': 18, 'verticalAlign': 'top', 'margin': '10px',
                                  'display': 'inline-block', 'horizontalAlign': 'center'}),

    @app.callback(Output('change_param', 'children'), [Input('tabs_common_summary', 'value')])
    def clicks(tab):
        df = pd.read_csv('param_wt.csv', header=0)
        return html.Div(children=[

            html.Div(children=[

                html.H3('Edit criteria weightage (Total must be equal to 100):',
                        style={'color': 'black', 'font-family': 'sans-serif',
                               'fontSize': title_size, 'verticalAlign': 'top', 'width': '100%',
                               'margin': '22px',
                               'align-items': 'center', 'flex': 1,
                               'display': 'flex', 'justify-content': 'center'}),

                html.Div(children=[

                    html.H3('Criteria 1 (Supplier has access to SCF programs) %:',
                            style={'color': 'black', 'font-family': 'sans-serif',
                                   'fontSize': 18, 'verticalAlign': 'top', 'width': '40%',
                                   'margin': '10px',
                                   'align-items': 'center', 'flex': 1,
                                   'display': 'flex', 'justify-content': 'right'}),

                    dbc.Input(id="scf_wt", type='number', min=0, max=100, value=df['scf'][0] * 100, step=1,
                              style={'color': 'black', 'font-family': 'sans-serif',
                                     'fontSize': 18, 'verticalAlign': 'top', 'width': '40%',
                                     'margin': '10px',
                                     'align-items': 'center', 'flex': 1,
                                     'display': 'flex', 'justify-content': 'right'}),
                ], style={'display': 'flex', 'margin': '12px', 'flex': 'row', 'horizontalAlign': 'center'}),

                html.Div(children=[

                    html.H3('Criteria 2 (Supplier offers VMI to clients) %:',
                            style={'color': 'black', 'font-family': 'sans-serif',
                                   'fontSize': 18, 'verticalAlign': 'top', 'width': '40%',
                                   'margin': '10px',
                                   'align-items': 'center', 'flex': 1,
                                   'display': 'flex', 'justify-content': 'right'}),

                    dbc.Input(id="VMI_wt", type='number', min=0, max=100, value=df['VMI'][0] * 100, step=1,
                              style={'color': 'black', 'font-family': 'sans-serif',
                                     'fontSize': 18, 'verticalAlign': 'top', 'width': '40%',
                                     'margin': '10px',
                                     'align-items': 'center', 'flex': 1,
                                     'display': 'flex', 'justify-content': 'right'}),
                ], style={'display': 'flex', 'margin': '12px', 'flex': 'row', 'horizontalAlign': 'center'}),

                html.Div(children=[

                    html.H3("Criteria 3 (Supplier is a critical for client) %:",
                            style={'color': 'black', 'font-family': 'sans-serif',
                                   'fontSize': 18, 'verticalAlign': 'top', 'width': '40%',
                                   'margin': '10px',
                                   'align-items': 'center', 'flex': 1,
                                   'display': 'flex', 'justify-content': 'right'}),

                    dbc.Input(id="critical_wt", type='number', min=0, max=100, value=df['critical'][0] * 100, step=1,
                              style={'color': 'black', 'font-family': 'sans-serif',
                                     'fontSize': 18, 'verticalAlign': 'top', 'width': '20px',
                                     'margin': '10px',
                                     'align-items': 'center', 'flex': 1,
                                     'display': 'flex', 'justify-content': 'right'}),
                ], style={'display': 'flex', 'margin': '12px', 'flex': 'row', 'horizontalAlign': 'center'}),

                html.Div(children=[

                    html.H3("Criteria 4 (Supplier inventory is 20%+ for client ) %:",
                            style={'color': 'black', 'font-family': 'sans-serif',
                                   'fontSize': 18, 'verticalAlign': 'top', 'width': '40%',
                                   'margin': '10px',
                                   'align-items': 'center', 'flex': 1,
                                   'display': 'flex', 'justify-content': 'right'}),

                    dbc.Input(id="inventory_wt", type='number', min=0, max=100, value=df['inventory'][0] * 100, step=1,
                              style={'color': 'black', 'font-family': 'sans-serif',
                                     'fontSize': 18, 'verticalAlign': 'top', 'width': '40%',
                                     'margin': '10px',
                                     'align-items': 'center', 'flex': 1,
                                     'display': 'flex', 'justify-content': 'right'}),
                ], style={'display': 'flex', 'margin': '12px', 'flex': 'row', 'horizontalAlign': 'center'}),

                html.Div(children=[

                    html.H3('Criteria 5 (Payment terms are below 45 days) %:',
                            style={'color': 'black', 'font-family': 'sans-serif',
                                   'fontSize': 18, 'verticalAlign': 'top', 'width': '40%',
                                   'margin': '10px',
                                   'align-items': 'center', 'flex': 1,
                                   'display': 'flex', 'justify-content': 'right'}),

                    dbc.Input(id="pay_term_wt", type='number', min=0, max=100, value=df['pay_term'][0] * 100, step=1,
                              style={'color': 'black', 'font-family': 'sans-serif',
                                     'fontSize': 18, 'verticalAlign': 'top', 'width': '40%',
                                     'margin': '10px',
                                     'align-items': 'center', 'flex': 1,
                                     'display': 'flex', 'justify-content': 'right'}),
                ], style={'display': 'flex', 'margin': '12px', 'flex': 'row', 'horizontalAlign': 'center'}),

                html.Div(children=[

                    html.H3("Criteria 6 (Lead times are 90+ days) %:",
                            style={'color': 'black', 'font-family': 'sans-serif',
                                   'fontSize': 18, 'verticalAlign': 'top', 'width': '40%',
                                   'margin': '10px',
                                   'align-items': 'center', 'flex': 1,
                                   'display': 'flex', 'justify-content': 'right'}),

                    dbc.Input(id="lead_time_wt", type='number', min=0, max=100, value=df['lead_time'][0] * 100, step=1,
                              style={'color': 'black', 'font-family': 'sans-serif',
                                     'fontSize': 18, 'verticalAlign': 'top', 'width': '40%',
                                     'margin': '10px',
                                     'align-items': 'center', 'flex': 1,
                                     'display': 'flex', 'justify-content': 'right'}),
                ], style={'display': 'flex', 'margin': '12px', 'flex': 'row', 'horizontalAlign': 'center'}),

                html.Div(children=[

                    html.H3("Criteria 7 (Client business is 20%+ of supplier business) %:",
                            style={'color': 'black', 'font-family': 'sans-serif',
                                   'fontSize': 18, 'verticalAlign': 'top', 'width': '40%',
                                   'margin': '10px',
                                   'align-items': 'center', 'flex': 1,
                                   'display': 'flex', 'justify-content': 'right'}),

                    dbc.Input(id="business_wt", type='number', min=0, max=100, value=df['business'][0] * 100, step=1,
                              style={'color': 'black', 'font-family': 'sans-serif',
                                     'fontSize': 18, 'verticalAlign': 'top', 'width': '20px',
                                     'margin': '10px',
                                     'align-items': 'center', 'flex': 1,
                                     'display': 'flex', 'justify-content': 'right'}),
                ], style={'display': 'flex', 'margin': '12px', 'flex': 'row', 'horizontalAlign': 'center'}),

                html.Div(children=[

                    html.H3("Criteria 8 (Supplier Invoices overdue 30+ days) %:",
                            style={'color': 'black', 'font-family': 'sans-serif',
                                   'fontSize': 18, 'verticalAlign': 'top', 'width': '40%',
                                   'margin': '10px',
                                   'align-items': 'center', 'flex': 1,
                                   'display': 'flex', 'justify-content': 'right'}),

                    dbc.Input(id="overdue_wt", type='number', min=0, max=100, value=df['overdue'][0] * 100, step=1,
                              style={'color': 'black', 'font-family': 'sans-serif',
                                     'fontSize': 18, 'verticalAlign': 'top', 'width': '40%',
                                     'margin': '10px',
                                     'align-items': 'center', 'flex': 1,
                                     'display': 'flex', 'justify-content': 'right'}),
                ], style={'display': 'flex', 'margin': '12px', 'flex': 'row', 'horizontalAlign': 'center'}),

                html.Div(id='wt_engine'),

            ], style={'border': 'px solid orange', 'background-color': 'white', 'width': '75%',
                      'horizontalAlign': 'center',
                      'border-radius': 20, 'margin': '0px', 'padding': '20px', 'display': 'inline-block'}),

            # html.Div(children=[html.Div(id='supplier_table_2')],style={'width':'30%','display':'inline-block','verticalAlign': 'top',}),

        ], style={'border': 'px solid orange', 'width': '100%', 'display': 'inline-block',
                  'border-radius': 20, 'margin': '50px', 'horizontalAlign': 'center'})

    @app.callback(
        Output('wt_engine', 'children'),
        [Input('scf_wt', 'value'),
         Input('VMI_wt', 'value'),
         Input('critical_wt', 'value'),
         Input('inventory_wt', 'value'),
         Input('pay_term_wt', 'value'),
         Input('lead_time_wt', 'value'),
         Input('business_wt', 'value'),
         Input('overdue_wt', 'value')])
    def wt_engine(scf_wt,
                  VMI_wt,
                  critical_wt,
                  inventory_wt,
                  pay_term_wt,
                  lead_time_wt,
                  business_wt,
                  overdue_wt):
        if any([arg is None for arg in [scf_wt,
                                        VMI_wt,
                                        critical_wt,
                                        inventory_wt,
                                        pay_term_wt,
                                        lead_time_wt,
                                        business_wt,
                                        overdue_wt, ]]):
            return html.Label([warning_icon, '/!\ One param is <Null> - Please change it to <0>'],
                              style={'font-family': 'sans-serif', 'fontSize': 22, 'color': 'red',
                                     'width': '500px', 'display': 'inline-block', 'verticalAlign': 'middle',
                                     'margin': '15px 15px 15px 15px'  # 'height':'40px'
                                     }),

        else:

            rslt = scf_wt + VMI_wt + critical_wt + inventory_wt + pay_term_wt + lead_time_wt + business_wt + overdue_wt

            if (rslt / 100) == 1:
                return html.Div(children=[
                    dbc.Button([change_icon, "Edit weightage"], id='button_change_param',
                               color="primary", className="me-1", n_clicks=0,
                               style={'margin': '20px 20px 20px 20px', 'fontSize': 16, 'font-family': 'sans-serif', }),
                    html.Div(id='change_param_click'),
                ])
            else:
                return html.Label([warning_icon, 'The total should be 100% -- Total is now: ' + str(rslt) + '%'],
                                  style={'font-family': 'sans-serif', 'fontSize': 22, 'color': 'red',
                                         'width': '500px', 'display': 'inline-block', 'verticalAlign': 'middle',
                                         'margin': '15px 15px 15px 15px'  # 'height':'40px'
                                         }),

    @app.callback(
        Output('change_param_click', 'children'),
        [Input('button_change_param', 'n_clicks'),
         Input('scf_wt', 'value'),
         Input('VMI_wt', 'value'),
         Input('critical_wt', 'value'),
         Input('inventory_wt', 'value'),
         Input('pay_term_wt', 'value'),
         Input('lead_time_wt', 'value'),
         Input('business_wt', 'value'),
         Input('overdue_wt', 'value')])
    def clicks_param(n_clicks,
                     scf_wt,
                     VMI_wt,
                     critical_wt,
                     inventory_wt,
                     pay_term_wt,
                     lead_time_wt,
                     business_wt,
                     overdue_wt):

        if n_clicks > 0:
            data = {'scf': [scf_wt / 100],
                    'VMI': [VMI_wt / 100],
                    'critical': [critical_wt / 100],
                    'inventory': [inventory_wt / 100],
                    'pay_term': [pay_term_wt / 100],
                    'lead_time': [lead_time_wt / 100],
                    'business': [business_wt / 100],
                    'overdue': [overdue_wt / 100]}

            df = pd.DataFrame(data)

            df.to_csv('param_wt.csv', index=False)
            return html.H3([ok_icon, 'Weightage updated'], style={'color': 'green', 'font-family': 'sans-serif',
                                                                  'fontSize': 18, 'verticalAlign': 'top',
                                                                  'margin': '10px',
                                                                  'display': 'inline-block',
                                                                  'horizontalAlign': 'center'}),

    @app.callback(
        Output('button-clicks-del', 'children'),
        [Input('button_del_sup', 'n_clicks'),
         Input('name_edit', 'value'),
         ])
    def clicks(n_clicks, name):
        if n_clicks > 0:
            del_sup(name)
            return html.H3([ok_icon, 'Supplier removed from the list /!\ reload the page to update'],
                           style={'color': 'green', 'font-family': 'sans-serif',
                                  'fontSize': 18, 'verticalAlign': 'top', 'margin': '10px',
                                  'display': 'inline-block', 'horizontalAlign': 'center'}),

    @app.callback(Output('download-link', 'href'),
                  Input('download-link', 'n_clicks'))
    def download_xlsx(n_clicks):

        df = csv_to_df_2('save_sup.csv')

        xlsx_data = DL_ranking(df)
        b64_data = base64.b64encode(xlsx_data).decode('utf-8')
        href_data = f"data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;charset=utf-8;base64,{b64_data}"
        return href_data

    @app.callback(
        Output('button-clicks-edit', 'children'),
        [Input('button_edit_sup', 'n_clicks'),
         Input('name_edit', 'value'),
         Input('amount_edit', 'value'),
         Input('scf_edit', 'value'),
         Input('VMI_edit', 'value'),
         Input('critical_edit', 'value'),
         Input('inventory_edit', 'value'),
         Input('pay_term_edit', 'value'),
         Input('lead_time_edit', 'value'),
         Input('business_edit', 'value'),
         Input('overdue_edit', 'value')])
    def clicks(n_clicks, name, amount_, scf_, VMI_, critical_, inventory_, pay_term_, lead_time_, business_, overdue_):
        if n_clicks > 0:
            if any([arg is None for arg in [name,
                                            amount_,
                                            scf_,
                                            VMI_,
                                            critical_,
                                            inventory_,
                                            pay_term_,
                                            lead_time_,
                                            business_,
                                            overdue_, ]]) or name == '':
                return html.H3([warning_icon, 'Please provide an answer for all criterias'],
                               style={'color': 'red', 'font-family': 'sans-serif',
                                      'fontSize': 18, 'verticalAlign': 'top', 'margin': '10px',
                                      'display': 'inline-block', 'horizontalAlign': 'center'}),
            else:
                edit_sup(name, amount_, scf_, VMI_, critical_, inventory_, pay_term_, lead_time_, business_, overdue_)
                return html.H3([ok_icon, 'Edited /!\ reload the page to update'],
                               style={'color': 'green', 'font-family': 'sans-serif',
                                      'fontSize': 18, 'verticalAlign': 'top', 'margin': '10px',
                                      'display': 'inline-block', 'horizontalAlign': 'center'}),

    return app


app = create_app()

if __name__ == '__main__':
    app.run_server(port=8000, debug=True, use_reloader=False)
