import flet as ft
from flet.matplotlib_chart import MatplotlibChart
import pyodbc as sql_server

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

import re

matplotlib.use("svg")

def extract_queries(sql_text) -> list:
    # Expresión regular para encontrar consultas que comienzan con SELECT y terminan con ;
    pattern = re.compile(r'(?i)(SELECT.*?;)', re.DOTALL)
    queries = pattern.findall(sql_text)
    return queries

def print_queries(doc:str) -> list:
    with open(doc, 'r') as myfile:
        data = myfile.read()

        # Extraer las consultas
        queries_list:list = extract_queries(data)

        return queries_list

def bar_chart(data_test):
    # make data:
    x2 = 0.5 + np.arange(8)
    y2 = [4.8, 5.5, 3.5, 4.6, 6.5, 6.6, 2.6, 3.0]
    bar_labels = ["red", "blue", "_red", "orange", "yellow", "orange", "yellow", "orange"]
    colors = ["tab:red", "tab:blue", "tab:red", "tab:orange", "tab:blue", "tab:orange", "tab:cyan", "tab:orange"]

    # plot
    figure, axles = plt.subplots()

    axles.bar(x2, y2, width=1, edgecolor="white", linewidth=0.7, label=bar_labels, color=colors)

    axles.set(xlim=(0, 8), xticks=np.arange(1, 8),
           ylim=(0, 8), yticks=np.arange(1, 8))
    
    axles.set_ylabel("fruit supply")
    axles.set_title("Fruit supply by kind and color")
    axles.legend(title="Fruit color")
    
    return figure


def pie_chart(data_test):
    def func(pct, allvals):
        absolute = int(np.round(pct/100.*np.sum(allvals)))
        return f"{pct:.1f}%\n({absolute:d} g)"

    figure, ax = plt.subplots()

    recipe = ["375 g flour",
              "75 g sugar",
              "250 g butter",
              "300 g berries"]

    data = [float(x.split()[0]) for x in recipe]
    ingredients = [x.split()[-1] for x in recipe]

    wedges, texts, autotexts = ax.pie(data, autopct=lambda pct: func(pct, data),
                                  textprops=dict(color="w"))

    ax.legend(wedges, ingredients,
              title="Ingredients",
              loc="center left",
              bbox_to_anchor=(1, 0, 0.5, 1))

    plt.setp(autotexts, size=8, weight="bold")

    ax.set_title("Matplotlib bakery: A pie")
    
    
    return figure


def area_chart(data_test):
    # make data
    year = [1950, 1960, 1970, 1980, 1990, 2000, 2010, 2018]
    population_by_continent = {
        'Africa': [.228, .284, .365, .477, .631, .814, 1.044, 1.275],
        'the Americas': [.340, .425, .519, .619, .727, .840, .943, 1.006],
        'Asia': [1.394, 1.686, 2.120, 2.625, 3.202, 3.714, 4.169, 4.560],
        'Europe': [.220, .253, .276, .295, .310, .303, .294, .293],
        'Oceania': [.012, .015, .019, .022, .026, .031, .036, .039],
    }
    
    # plot
    figure, axles = plt.subplots()
    
    axles.stackplot(year, population_by_continent.values(),
             labels=population_by_continent.keys(), alpha=0.8)
    axles.legend(loc='upper left', reverse=True)
    axles.set_title('World population')
    axles.set_xlabel('Year')
    axles.set_ylabel('Number of people (billions)')

    return figure


async def main(page: ft.Page):
    page.title = "DataGraphX"
    page.scroll = ft.ScrollMode.ADAPTIVE
    connection:sql_server.Connection = None
    query_list:list = []


    panel_list = ft.ExpansionPanelList(
        elevation=8,
    )
    dropdown_driver:ft.Dropdown = ft.Dropdown(
        label="Driver", 
        value="{SQL Server}", 
        options=[
            ft.dropdown.Option("{SQL Server}"), 
            ft.dropdown.Option("{ODBC Driver 13 for SQL Server}")
        ]
    )
    text_server:ft.TextField = ft.TextField(
        label="Server",
        text_align=ft.TextAlign.LEFT
    )
    checkbox_windows_auth:ft.Checkbox = ft.Checkbox(
        label="Windows Auth",
        value=False
    )
    text_username:ft.TextField = ft.TextField(
        label="Username",
        text_align=ft.TextAlign.LEFT,
        disabled=False
    )
    text_password:ft.TextField = ft.TextField(
        label="Password",
        text_align=ft.TextAlign.LEFT,
        password=True,
        disabled=False
    )
    button_connect:ft.ElevatedButton = ft.ElevatedButton(
        text="Connect",
        icon=ft.icons.CLOUD_UPLOAD,
        disabled=True,
    )
    button_help:ft.ElevatedButton = ft.ElevatedButton(
        text="Help",
        icon=ft.icons.HELP,
        # on_click=open_dlg_modal
    )
    button_theme:ft.ElevatedButton = ft.ElevatedButton(
        text="Theme",
        icon=ft.icons.LIGHT_MODE,
    )


    def route_change(e: ft.RouteChangeEvent) -> None:
        page.views.clear()
        page.views.append(
            ft.View(
                route="/",
                controls=[
                    ft.AppBar(title=ft.Text("Home"), bgcolor=ft.colors.SURFACE_VARIANT),
                    ft.Row(
                        controls=[
                            ft.Column(
                                controls=[
                                    ft.Text("Database selected"),
                                    ft.Text(f"Connetion: {connection}"),
                                    button_theme,
                                ],
                                expand=True,
                            ),
                            ft.Column(
                                controls=[
                                    ft.Text("List of query to view data"),
                                    ft.Container(
                                        content=ft.Column(
                                            controls=[
                                                panel_list,
                                            ],
                                        ),
                                    ),
                                ],
                                expand=True,
                            ),
                        ],
                    ),
                ],
            ),
        )

        if page.route == "/login":
            page.views.append(
                ft.View(
                    route="/login",
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Text(value="DataGraphX", size=40),
                                ft.Image(src="./assets/icon.png", width=50, height=50, fit=ft.ImageFit.CONTAIN),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                        ft.Container(
                            ft.Column(
                                controls=[
                                    dropdown_driver,
                                    text_server,
                                    checkbox_windows_auth,
                                    text_username,
                                    text_password,
                                    ft.Divider(),
                                    ft.Row(
                                        controls=[
                                            button_connect,
                                            button_help,
                                            button_theme
                                        ],
                                        alignment=ft.MainAxisAlignment.END,
                                    ),
                                ],
                                
                            ),
                            padding=20,
                            margin=20,
                            border_radius=10,
                        ),
                    ],
                ),
            )

        if page.route == "/details":
            chart1 = bar_chart("test")
            chart2 = pie_chart("test")
            chart3 = area_chart("test")

            query = query_list[0]

            page.views.append(
                ft.View(
                    route="/details",
                    controls=[
                        ft.AppBar(title=ft.Text("Details"), bgcolor=ft.colors.SURFACE_VARIANT),
                        ft.Row(
                            controls=[
                                ft.Column(
                                    controls=[
                                        ft.Text(value="Query structure"),
                                        ft.Markdown(
                                            value=f"```console\n {query} \n```",
                                            selectable=True,
                                            extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
                                            on_tap_link=lambda e: page.launch_url(e.data),
                                        )
                                    ],
                                    expand=True
                                ),
                                ft.Column(
                                    controls=[
                                        ft.Tabs(
                                            selected_index=0,
                                            animation_duration=300,
                                            tabs=[
                                                ft.Tab(
                                                    text="BarChart",
                                                    icon=ft.icons.BAR_CHART,
                                                    content=ft.Column(
                                                        controls=[
                                                            MatplotlibChart(chart1, expand=True)
                                                        ]
                                                    ),
                                                ),
                                                ft.Tab(
                                                    text="Pie Chart",
                                                    icon=ft.icons.PIE_CHART,
                                                    content=ft.Column(
                                                        controls=[
                                                            MatplotlibChart(chart2, expand=True)
                                                        ]
                                                    ),
                                                ),
                                                ft.Tab(
                                                    text="Area Chart",
                                                    icon=ft.icons.AREA_CHART,
                                                    content=ft.Column(
                                                        controls=[
                                                            MatplotlibChart(chart3, expand=True)
                                                        ]
                                                    ),
                                                ),
                                            ],
                                            expand=True
                                        )
                                    ],
                                    expand=True
                                ),
                            ],
                            expand=True,
                        ),
                        ft.Row(
                            controls=[
                                ft.Column(
                                    controls=[
                                        ft.Text(value="Data of the query"),
                                        ft.DataTable(
                                            columns=[
                                                ft.DataColumn(ft.Text("First name")),
                                                ft.DataColumn(ft.Text("Last name")),
                                                ft.DataColumn(ft.Text("Age"), numeric=True),
                                            ],
                                            rows=[
                                                ft.DataRow(
                                                    cells=[
                                                        ft.DataCell(ft.Text("John")),
                                                        ft.DataCell(ft.Text("Smith")),
                                                        ft.DataCell(ft.Text("43")),
                                                    ],
                                                ),
                                                ft.DataRow(
                                                    cells=[
                                                        ft.DataCell(ft.Text("Jack")),
                                                        ft.DataCell(ft.Text("Brown")),
                                                        ft.DataCell(ft.Text("19")),
                                                    ],
                                                ),
                                                ft.DataRow(
                                                    cells=[
                                                        ft.DataCell(ft.Text("Alice")),
                                                        ft.DataCell(ft.Text("Wong")),
                                                        ft.DataCell(ft.Text("25")),
                                                    ],
                                                ),
                                            ],
                                        ),
                                    ]
                                )
                            ],
                            expand=True,
                        ),
                    ],
                ),
            )
        
        page.update()
    

    def change_theme(e: ft.ControlEvent) -> None:
        page.theme_mode = ft.ThemeMode.DARK if page.theme_mode == ft.ThemeMode.LIGHT else ft.ThemeMode.LIGHT
        button_theme.icon = ft.icons.LIGHT_MODE if page.theme_mode == ft.ThemeMode.DARK else ft.icons.DARK_MODE
        page.update()

    async def validate_inputs(e: ft.ControlEvent) -> None:
        if checkbox_windows_auth.value:
            text_username.disabled = True
            text_password.disabled = True

            if all([dropdown_driver.value, text_server.value]):
                button_connect.disabled = False
            else:
                button_connect.disabled = True

        else:
            text_username.disabled = False
            text_password.disabled = False

            if all([text_server.value, text_username.value, text_password.value]):
                button_connect.disabled = False
            else:
                button_connect.disabled = True
        
        page.update()


    async def connect_to_sql_server(driver: str, server: str, windows_auth:bool, user: str, password: str) -> sql_server.Connection:
        if windows_auth:
            return sql_server.connect(driver=driver, server=server, trusted_connection="yes")
        else:
            return sql_server.connect(driver=driver, server=server, user=user, password=password)
    

    async def submit_connection(e: ft.ControlEvent) -> None:
        # nonlocal connection
        # connection = await connect_to_sql_server(dropdown_driver.value, text_server.value, checkbox_windows_auth.value, text_username.value, text_password.value)

        # if connection and connection is not None:
        #     page.go("/")
        
        # else:
        #     connection.close()
        page.go("/")


    def view_pop(view) -> None:
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)
    
    query_list = print_queries('assets/test.sql')

    for id in range(len(query_list)):
        exp = ft.ExpansionPanel(
            header=ft.ListTile(title=ft.Text(f"Query {id+1}")),
            expand=True if id == 0 else False,
        )

        exp.content = ft.ListTile(
            title=ft.Text(f"This is in Panel {id+1}"),
            subtitle=ft.Text(f"Press the icon to go to full view of the query {id+1}, the real id is {id}"),
            trailing=ft.IconButton(ft.icons.QUERY_STATS, on_click=lambda _: page.go("/details")),
        )

        panel_list.controls.append(exp)


    dropdown_driver.on_change = validate_inputs
    text_server.on_change = validate_inputs
    checkbox_windows_auth.on_change = validate_inputs
    text_username.on_change = validate_inputs
    text_password.on_change = validate_inputs

    button_connect.on_click = submit_connection
    button_theme.on_click = change_theme


    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go("/login")


if __name__ == "__main__":
    ft.app(target=main)