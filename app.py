# app.py

import pandas as pd
from dash import Dash, dcc, html, callback_context
import pandas as pd
import numpy as np
import plotly.express as px
import urllib
from dash.dependencies import Output, Input, State

from constants import (
    INSPECTION_DETAILS_FOLDER_NAME,
    MAPPING_FILES_FOLDER_NAME,
    ALL,
    STATE_NAMES,
    TWO_DIGIT_NAICS,
)
from helpers import get_naics_sector_numbers_by_names
from scrapping_inspection_details import (
    parse_inspection_file,
    Inspection,
    get_inspection_details_list,
)

FILE_NAMES_ENCODING = {
    #     'ITA Data CY 2016.zip': 'cp1252',
    #     'ITA Data CY 2017.zip': 'cp1252',
    #     'ITA Data CY 2018.zip': 'cp1252',
    #     'ITA Data CY 2019.zip': 'utf-8',
    "ITA Data CY 2020.zip": "utf-8",
    "ITA Data CY 2021 submitted thru 8-29-2022.zip": "utf-8",
}
OWNERSHIP_MAP = {
    "Not a government entity": 1.0,
    "State Government entity": 2.0,
    "Local Government entity": 3.0,
}
QUANTITATIVE_VALUES  = {
    "Days away from work": "total_dafw_days",
    "Total hours worked": "total_hours_worked",
    "Annual average employees": "annual_average_employees",
    "Days of job transfer or restriction": "total_djtr_days",
    "Total Deaths": "total_deaths",
    "Cases with days away from work": "total_dafw_cases",
    "Cases with job transfer or restriction": "total_djtr_cases",
    "Number of injuries": "total_injuries",
}
QUANTITATIVE_VALUES  = {
    "Days away from work": "total_dafw_days",
    "Total hours worked": "total_hours_worked",
    "Annual average employees": "annual_average_employees",
    "Days of job transfer or restriction": "total_djtr_days",
    "Total Deaths": "total_deaths",
    "Cases with days away from work": "total_dafw_cases",
    "Cases with job transfer or restriction": "total_djtr_cases",
    "Number of injuries": "total_injuries",
}

data = pd.concat(
    list(
        map(
            lambda name: pd.read_csv(
                name, encoding=FILE_NAMES_ENCODING[name], low_memory=False
            ),
            FILE_NAMES_ENCODING.keys(),
        )
    ),
    ignore_index=True,
)

data = data.drop(
    columns=[
        "id",  # Unique number for each record
        "street_address",
        "zip_code",
        "no_injuries_illnesses",  # Whether the establishment had any OSHA recordable work-related injuries or illnesses during the year
        "total_other_cases",
        "total_skin_disorders",
        "total_poisonings",
        "total_respiratory_conditions",
        "total_hearing_loss",
        "total_other_illnesses",
        "created_timestamp",  # The date and time a record was submitted to the ITA
        "change_reason",  # The reason why an establishment’s injury and illness summary was changed, if applicable
    ]
)

data = data[~data["year_filing_for"].isna()]
data = data[data["annual_average_employees"] < 1000000]
data = data[data["total_hours_worked"] >= 0]
data = data[data["total_dafw_days"] >= 0]
data = data[data["total_djtr_days"] >= 0]
data.index = list(range(len(data)))


external_stylesheets = [
    {
        "href": "https://fonts.googleapis.com/css2?"
        "family=Lato:wght@400;700&display=swap",
        "rel": "stylesheet",
    },
]
app = Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.title = "Avocado Analytics: Understand Your Avocados!"

app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.P(children="🥑", className="header-emoji"),
                html.H1(children="TEst Analytics", className="header-title"),
                html.P(
                    children="Analyze the behavio",
                    className="header-description",
                ),
            ],
            className="header",
        ),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(children="State", className="menu-title"),
                        dcc.Dropdown(
                            id="state-filter",
                            options=[
                                {"label": state, "value": state}
                                for state in np.append(ALL, data.state.unique())
                            ],
                            value=ALL,
                            multi=True,
                            clearable=True,
                            searchable=True,
                            className="dropdown",
                        ),
                    ],
                ),
                html.Div(
                    children=[
                        html.Div(children="Year", className="menu-title"),
                        dcc.Dropdown(
                            id="year-filter",
                            options=[
                                {"label": year, "value": year}
                                for year in np.append(
                                    ALL, data.year_filing_for.unique()
                                )
                            ],
                            value=ALL,
                            clearable=True,
                            searchable=True,
                            className="dropdown",
                        ),
                    ],
                ),
                html.Div(
                    children=[
                        html.Div(children="Ownership", className="menu-title"),
                        dcc.Dropdown(
                            id="ownership-filter",
                            options=[
                                {"label": state, "value": state}
                                for state in [ALL] + list(OWNERSHIP_MAP.keys())
                            ],
                            value=ALL,
                            clearable=True,
                            searchable=True,
                            className="dropdown",
                        ),
                    ],
                ),
                html.Div(
                    children=[
                        html.Div(children="Naics", className="menu-title"),
                        dcc.Dropdown(
                            id="naics-filter",
                            options=[
                                {"label": state, "value": state}
                                for state in [ALL] + list(set(TWO_DIGIT_NAICS.values()))
                            ],
                            value=ALL,
                            clearable=True,
                            searchable=True,
                            className="dropdown",
                        ),
                    ],
                ),
                html.Div(
                    children=[
                        html.Div(children="X label", className="menu-title"),
                        dcc.Dropdown(
                            id="x_label-filter",
                            options=[
                                {"label": state, "value": state}
                                for state in list(QUANTITATIVE_VALUES.keys())
                            ],
                            value=list(QUANTITATIVE_VALUES.keys())[0],
                            searchable=True,
                            className="dropdown",
                        ),
                    ],
                ),
            ],
            className="menu-row-1",
        ),  # children=[]
        html.Div(
            className="menu-row-2",
            children=[
                html.Div(  ## HERE
                    children=[
                        html.Div(
                            children="Days away from work", className="menu-title"
                        ),
                        dcc.RangeSlider(
                            id="days_away_from_work-filter",
                            min=data["total_dafw_days"].min(),
                            max=data["total_dafw_days"].max(),
                            value=[
                                data["total_dafw_days"].min(),
                                data["total_dafw_days"].max(),
                            ],
                        ),
                    ],
                ),
                html.Div(  ## HERE
                    children=[
                        html.Div(children="Total hours worked", className="menu-title"),
                        dcc.RangeSlider(
                            id="total_hours_worked-filter",
                            min=data["total_hours_worked"].min(),
                            max=data["total_hours_worked"].max(),
                            value=[
                                data["total_hours_worked"].min(),
                                data["total_hours_worked"].max(),
                            ],
                        ),
                    ],
                ),
                html.Div(  ## HERE
                    children=[
                        html.Div(
                            children="Annual average employees", className="menu-title"
                        ),
                        dcc.RangeSlider(
                            id="annual_average_employees-filter",
                            min=data["annual_average_employees"].min(),
                            max=data["annual_average_employees"].max(),
                            value=[
                                data["annual_average_employees"].min(),
                                data["annual_average_employees"].max(),
                            ],
                        ),
                    ],
                ),
                html.Div(  ## HERE
                    children=[
                        html.Div(
                            children="Days of job transfer or restriction",
                            className="menu-title",
                        ),
                        dcc.RangeSlider(
                            id="days_of_job_transfer_or_restriction-filter",
                            min=data["total_djtr_days"].min(),
                            max=data["total_djtr_days"].max(),
                            value=[
                                data["total_djtr_days"].min(),
                                data["total_djtr_days"].max(),
                            ],
                            tooltip={"placement": "bottom", "always_visible": True},
                        ),
                    ],
                ),
                html.Div(
                    children=[
                        html.Div(children="Y label", className="menu-title"),
                        dcc.Dropdown(
                            id="y_label-filter",
                            options=[
                                {"label": state, "value": state}
                                for state in list(QUANTITATIVE_VALUES.keys())
                            ],
                            value=list(QUANTITATIVE_VALUES.keys())[-1],
                            searchable=True,
                            className="dropdown",
                        ),
                    ],
                ),
            ],
        ),
        html.Div(
            className="menu-row-3",
            children=[
                html.Div(  ## HERE
                    children=[
                        html.Div(
                            children="Total Deaths",
                            className="menu-title",
                        ),
                        dcc.RangeSlider(
                            id="total_deaths-filter",
                            min=data["total_deaths"].min(),
                            max=data["total_deaths"].max(),
                            value=[
                                data["total_deaths"].min(),
                                data["total_deaths"].max(),
                            ],
                        ),
                    ],
                ),
                html.Div(  ## HERE
                    children=[
                        html.Div(
                            children="Cases with days away from work",
                            className="menu-title",
                        ),
                        dcc.RangeSlider(
                            id="total_dafw_cases-filter",
                            min=data["total_dafw_cases"].min(),
                            max=data["total_dafw_cases"].max(),
                            value=[
                                data["total_dafw_cases"].min(),
                                data["total_dafw_cases"].max(),
                            ],
                        ),
                    ],
                ),
                html.Div(  ## HERE
                    children=[
                        html.Div(
                            children="Cases with job transfer or restriction",
                            className="menu-title",
                        ),
                        dcc.RangeSlider(
                            id="total_djtr_cases-filter",
                            min=data["total_djtr_cases"].min(),
                            max=data["total_djtr_cases"].max(),
                            value=[
                                data["total_djtr_cases"].min(),
                                data["total_djtr_cases"].max(),
                            ],
                        ),
                    ],
                ),
                html.Div(  ## HERE
                    children=[
                        html.Div(
                            children="Number of injuries",
                            className="menu-title",
                        ),
                        dcc.RangeSlider(
                            id="total_injuries-filter",
                            min=data["total_injuries"].min(),
                            max=data["total_injuries"].max(),
                            value=[
                                data["total_injuries"].min(),
                                data["total_injuries"].max(),
                            ],
                        ),
                    ],
                ),
                html.Button("Download CSV", id="download-button", n_clicks=1),
                dcc.Download(id="download-dataframe-csv"),
                html.Div(
                    children=[
                        html.Div(children="Colors", className="menu-title"),
                        dcc.Dropdown(
                            id="colors-filter",
                            options=[
                                {"label": state, "value": state}
                                for state in list(QUANTITATIVE_VALUES.keys())
                            ],
                            value="State",
                            searchable=True,
                            className="dropdown",
                        ),
                    ],
                ),
            ],
        ),
        html.Div(
            children=[
                html.Div(
                    children=dcc.Graph(
                        id="price-chart",
                    ),
                    className="card",
                )
            ],
            className="wrapper",
        ),
    ]
)

# [state-filter, year-filter, ownership-filter, naics-filter, days_away_from_work-filter, total_hours_worked-filter,
# annual_average_employees-filter, days_of_job_transfer_or_restriction-filter, total_deaths-filter, total_dafw_cases-filter,
# total_djtr_cases-filter, total_injuries-filter]
@app.callback(
    Output("price-chart", "figure"),
    [
        Input("state-filter", "value"),
        Input("year-filter", "value"),
        Input("ownership-filter", "value"),
        Input("naics-filter", "value"),
        Input("days_away_from_work-filter", "value"),
        Input("total_hours_worked-filter", "value"),
        Input("annual_average_employees-filter", "value"),
        Input(
            "days_of_job_transfer_or_restriction-filter", "value"
        ),
        Input("total_deaths-filter", "value"),
        Input("total_dafw_cases-filter", "value"),
        Input("total_djtr_cases-filter", "value"),
        Input("total_injuries-filter", "value"),# x_label-filter
        Input("x_label-filter", "value"),
        Input("y_label-filter", "value"),
    ],
)
def update_charts(
    state,
    year,
    ownership_type,
    naics,
    days_away_from_work,
    total_hours_worked_range,
    employee_number_range,
    days_of_job_transfer_or_restriction,
    total_deaths,
    total_dafw_cases,
    total_djtr_cases,
    total_injuries,
    x_label,
    y_label
):
    t = update_df(state,
    year,
    ownership_type,
    naics,
    days_away_from_work,
    total_hours_worked_range,
    employee_number_range,
    days_of_job_transfer_or_restriction,
    total_deaths,
    total_dafw_cases,
    total_djtr_cases,
    total_injuries,)

    price_chart_figure = px.scatter(
        t, x=QUANTITATIVE_VALUES[x_label], y=QUANTITATIVE_VALUES[y_label],
        color="state", log_x=True, size_max=100
    )

    return price_chart_figure


@app.callback(
    Output("download-dataframe-csv", "data"),
    Input("download-button", "n_clicks"),
    [
        State("state-filter", "value"),
        State("year-filter", "value"),
        State("ownership-filter", "value"),
        State("naics-filter", "value"),
        State("days_away_from_work-filter", "value"),
        State("total_hours_worked-filter", "value"),
        State("annual_average_employees-filter", "value"),
        State("days_of_job_transfer_or_restriction-filter", "value"),
        State("total_deaths-filter", "value"),
        State("total_dafw_cases-filter", "value"),
        State("total_djtr_cases-filter", "value"),
        State("total_injuries-filter", "value"),
    ],
    prevent_initial_call=True,
)
def download_csv(
    n_clicks,
    state,
    year,
    ownership_type,
    naics,
    days_away_from_work,
    total_hours_worked_range,
    employee_number_range,
    days_of_job_transfer_or_restriction,
    total_deaths,
    total_dafw_cases,
    total_djtr_cases,
    total_injuries,
):
    t = update_df(state,
    year,
    ownership_type,
    naics,
    days_away_from_work,
    total_hours_worked_range,
    employee_number_range,
    days_of_job_transfer_or_restriction,
    total_deaths,
    total_dafw_cases,
    total_djtr_cases,
    total_injuries,)

    return dcc.send_data_frame(t.to_csv, filename="some_name.csv")


def update_df(
    state,
    year,
    ownership_type,
    naics,
    days_away_from_work,
    total_hours_worked_range,
    employee_number_range,
    days_of_job_transfer_or_restriction,
    total_deaths,
    total_dafw_cases,
    total_djtr_cases,
    total_injuries,
):
    t = data if ALL in state else data[data["state"].isin(state)]
    t = (
        t
        if ALL in naics
        else t[
            t["naics_code"]
            .astype(str)
            .str.startswith(tuple(get_naics_sector_numbers_by_names([naics])))
        ]
    )
    t = (
        t
        if (not year or ALL in year)
        else t[t["year_filing_for"].isin([np.float64(year)])]
    )
    t = (
        t
        if ALL in ownership_type
        else t[t["establishment_type"].isin([OWNERSHIP_MAP[ownership_type]])]
    )
    t = t[
        t["annual_average_employees"].between(
            employee_number_range[0], employee_number_range[1]
        )
    ]
    t = t[
        t["total_hours_worked"].between(
            total_hours_worked_range[0], total_hours_worked_range[1]
        )
    ]
    t = t[t["total_dafw_days"].between(days_away_from_work[0], days_away_from_work[1])]
    t = t[
        t["total_djtr_days"].between(
            days_of_job_transfer_or_restriction[0],
            days_of_job_transfer_or_restriction[1],
        )
    ]
    t = t[t["total_deaths"].between(total_deaths[0], total_deaths[1])]
    t = t[t["total_dafw_cases"].between(total_dafw_cases[0], total_dafw_cases[1])]
    t = t[t["total_djtr_cases"].between(total_djtr_cases[0], total_djtr_cases[1])]
    t = t[t["total_injuries"].between(total_injuries[0], total_injuries[1])]

    return t

if __name__ == "__main__":
    app.run_server(debug=True, port=8060)
