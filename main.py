import flet as ft
from flet.matplotlib_chart import MatplotlibChart
import pyodbc as sql_server

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

import re
import time

matplotlib.use("svg")

async def extract_queries(sql_text) -> list:
    pattern = re.compile(r'(?i)(SELECT.*?;)', re.DOTALL)
    queries = pattern.findall(sql_text)
    
    queries_list = [{'id': i + 1, 'query': query} for i, query in enumerate(queries)]
    return queries_list

async def print_queries(src:str) -> list:
    with open(src, 'r') as myfile:
        data = myfile.read()

        # Extraer las consultas
        queries_list:list = await extract_queries(data)

        return queries_list


def bar_chart(headers:list, data:list, data_type:list) -> tuple[plt.Figure, float]:

    start_time = time.time()

    fig, ax = plt.subplots()
    bar_colors = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple', 'tab:brown', 'tab:pink', 'tab:gray', 'tab:olive', 'tab:cyan']

    index:int = 0
    if len(headers) == 3:
        if data_type[0] == data_type[1]:
            if data[0][0] == data[1][0]:
                index = 1
            else:
                index = 0

    x_header = np.array([element[index] for element in data])
    y_data = np.array([element[-1] for element in data])

    ax.bar(x_header, y_data, color=bar_colors[:len(headers)])

    ax.set_xlabel(f'{headers[0]}')
    ax.set_ylabel(f'{headers[-1]}')
    ax.set_title(f'{headers[-1]} by {headers[0]}')

    end_time = time.time()
    elapsed_time = end_time - start_time

    return fig, elapsed_time


def pie_chart(headers:list, data:list) -> tuple[plt.Figure, float]:

    start_time = time.time()

    fig, ax = plt.subplots()

    labels = [element[0] for element in data]
    y_data = np.array([element[-1] for element in data])

    total = sum(y_data)
    percentages = [round((value / total) * 100, 1) for value in y_data]

    wedge_patches, texts, autotexts = ax.pie(
        y_data, labels=labels, autopct=lambda pct: f"{pct:.1f}%"
    )
    
    ax.set_title(f"{headers[-1]} by {headers[0]}")
    plt.setp(autotexts, size=8, weight="bold")

    end_time = time.time()
    elapsed_time = end_time - start_time

    return fig, elapsed_time


def line_chart(headers:list, data:list, data_type:list) -> tuple[plt.Figure, float]:

    start_time = time.time()

    fig, ax = plt.subplots()

    index:int = 0
    if len(headers) == 3:
        if data_type[0] == data_type[1]:
            if data[0][0] == data[1][0]:
                index = 1
            else:
                index = 0

    x_header = np.array([element[index] for element in data])
    y_data = np.array([element[-1] for element in data])

    ax.plot(x_header, y_data)

    ax.set_xlabel(f'{headers[0]}')
    ax.set_ylabel(f'{headers[-1]}')
    ax.set_title(f'{headers[-1]} by {headers[0]}')

    end_time = time.time()
    elapsed_time = end_time - start_time

    return fig, elapsed_time


def calculate_mean(list:list):
    suma = 0
    for elemento in list:
        suma += elemento
    media = suma / len(list)

    return media


def calculate_median(list:list):
    
    lista_ordenada = sorted(list)
    n = len(lista_ordenada)
    if n % 2 == 0:
        mediana = (lista_ordenada[n // 2] + lista_ordenada[n // 2 - 1]) / 2
    else:
        mediana = lista_ordenada[n // 2]

    return mediana


def calculate_mode(list:list):

    frecuencia = {}
    for numero in list:
        if numero in frecuencia:
            frecuencia[numero] += 1
        else:
            frecuencia[numero] = 1

    moda = max(frecuencia, key=frecuencia.get)

    return moda


def get_data_type_headers(connection: sql_server.Connection, database: str, query: str) -> tuple[list, list, list, float]:

    start_time = time.time()
    with connection.cursor() as cursor:
        cursor.execute(f"USE {database}")
        cursor.execute(query)
        data = cursor.fetchall()
        headers = [columna[0] for columna in cursor.description]
        data_types = [columna[1] for columna in cursor.description]
    
    end_time = time.time()
    elapsed_time = end_time - start_time

    return headers, data, data_types, elapsed_time


async def main(page: ft.Page):
    page.title = "DataGraphX"
    page.scroll = ft.ScrollMode.ADAPTIVE

    connection:sql_server.Connection = None
    query_list:list = []

    dlg_modal_error = ft.AlertDialog(
        modal=True,
        title=ft.Text("Something went wrong"),
        content=ft.Text("The connection failed. Please check the credentials and try again."),
        actions=[
            ft.TextButton("Ok", on_click=lambda e: page.close(dlg_modal_error)),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    dlg_modal_info = ft.AlertDialog(
        modal=True,
        title=ft.Text("How to use this app"),
        content=ft.Column(
            controls=[
                ft.Text(value="Hi!, Welcome to DataGraphX. This app is a tool to visualize the data of a SQL query. \nIn this secction you can see how to use this app. Dont worry, this app is very simple, \nyou only need check the content of this page and follow the instructions."),
                ft.Text(value="The first step is to connect to the database. For this, you have 2 options: \n- Using the drivers available in the dropdown menu and typing the server name."),
                ft.Image(src="assets/login1.png", width=300, height=200, fit=ft.ImageFit.CONTAIN),
                ft.Text(value="- Typing the all data without check the windows auth option."),
                ft.Image(src="assets/login2.png", width=300, height=200, fit=ft.ImageFit.CONTAIN),
                ft.Divider(),
                ft.Text(value="Now, You are in the Home page. In this you can see the status of the connection \nand the list of the queries."),
                ft.Image(src="assets/home.png", width=300, height=200, fit=ft.ImageFit.CONTAIN),
                ft.Text(value="The first panel show you the general status of the connection. If the connection \nis established, the status will be green and said 'Success', otherwise it will be \nred and said 'Error'."),
                ft.Image(src="assets/panel-info.png", width=300, height=200, fit=ft.ImageFit.CONTAIN),
                ft.Text(value="The second panel show you the list of the queries. You can click on the row icon \nto open the details of the query and after that you can click on the chart icon to \ngo to the details of the query."),
                ft.Image(src="assets/panel-list.png", width=300, height=200, fit=ft.ImageFit.CONTAIN),
                ft.Divider(),
                ft.Text(value="In the details page, you can see the data of the query. You can see the mean, \nmedian and mode of the data. You can also see the creation time of the chart."),
                ft.Image(src="assets/details.png", width=300, height=200, fit=ft.ImageFit.CONTAIN),
                ft.Text(value="This page is divided in 3 parts. The first part is the general information of the query."),
                ft.Image(src="assets/details-general.png", width=300, height=200, fit=ft.ImageFit.CONTAIN),
                ft.Text(value="The second part is the data of the query in three diferente types of charts."),
                ft.Image(src="assets/chart.png", width=300, height=200, fit=ft.ImageFit.CONTAIN),
                ft.Text(value="The third part is a table with the data of the query and the aditional information \n(mean, median and mode)."),
                ft.Image(src="assets/table.png", width=300, height=200, fit=ft.ImageFit.CONTAIN),

            ],
            scroll=ft.ScrollMode.AUTO,
        ),
        actions=[
            ft.TextButton("Ok", on_click=lambda e: page.close(dlg_modal_info)),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    panel_list = ft.ExpansionPanelList(
        elevation=5,
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
        on_click=lambda e: page.open(dlg_modal_info),
    )
    button_theme:ft.IconButton = ft.IconButton(
        icon=ft.icons.LIGHT_MODE,
    )
    button_info:ft.IconButton = ft.IconButton(
        icon=ft.icons.INFO,
        on_click=lambda e: page.open(dlg_modal_info),
    )


    def route_change(e: ft.RouteChangeEvent) -> None:
        page.views.clear()

        _page = e.route.split("?")[0]
        queries = e.route.split("?")[1:]

        data:dict = {}

        for item in queries:
            key = item.split("=")[0]
            value = item.split("=")[1]
            data[key] = value.replace("+", " ")


        page.views.append(
            ft.View(
                route="/",
                controls=[
                    ft.AppBar(
                        title=ft.Text("Home"), 
                        bgcolor=ft.colors.SURFACE_VARIANT, 
                        actions=[
                            button_theme,
                            button_info,
                            ft.PopupMenuButton(
                                items=[
                                    ft.PopupMenuItem(text="Help"),
                                    ft.PopupMenuItem(),
                                    ft.PopupMenuItem(text="Info"),
                                ]
                            )
                        ]
                    ),
                    ft.Row(
                        controls=[
                            ft.Column(
                                controls=[
                                    ft.Text("General info", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
                                    ft.Row(
                                        controls=[
                                            ft.Text(f"Connetion status"), 
                                            ft.Tooltip(
                                                message="When the connection is established, \nthe status will be green and said 'Success', \notherwise it will be red and said 'Error'",
                                                content=ft.Container(
                                                    content=ft.Text("Success" if connection else "Error", style=ft.TextThemeStyle.LABEL_SMALL,),
                                                    bgcolor=ft.colors.GREEN if connection else ft.colors.RED,
                                                    padding=ft.padding.only(top=1, right=5, bottom=1, left=5),
                                                    border_radius=ft.border_radius.all(50)
                                                ),
                                            )
                                        ]
                                    )
                                ],
                                expand=True,
                            ),
                            ft.VerticalDivider(),
                            ft.Column(
                                controls=[
                                    ft.Text("List of query's", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
                                    ft.Container(
                                        content=panel_list,
                                        padding=ft.padding.only(top=5, right=5, bottom=10, left=5),
                                    ),
                                    # panel_list,
                                ],
                                scroll=ft.ScrollMode.AUTO,
                                expand=True,
                            ),
                        ],
                        expand=True,
                    ),
                ],
            ),
        )

        if _page == "/login":
            page.views.append(
                ft.View(
                    route="/login",
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Text(value="DataGraphX", theme_style=ft.TextThemeStyle.DISPLAY_LARGE),
                                ft.Image(src="assets/icon.png", width=50, height=50, fit=ft.ImageFit.CONTAIN),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            vertical_alignment=ft.VerticalAlignment.CENTER,
                            expand=True
                        ),
                        ft.Container(
                            ft.Column(
                                controls=[
                                    dropdown_driver,
                                    text_server,
                                    checkbox_windows_auth,
                                    text_username,
                                    text_password,
                                    ft.Row(
                                        controls=[
                                            button_connect,
                                            button_help,
                                            button_theme
                                        ],
                                        alignment=ft.MainAxisAlignment.END,
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                            ),
                            padding=ft.padding.only(top=20, right=180, bottom=50, left=180),
                        ),
                    ],
                ),
            )

        if _page == "/details":

            _id = int(data['query_id'])-1
            query_text = query_list[_id]

            mean:list = []
            median:list = []
            mode:list = []

            _heder_query, _data_query, _data_type, _query_time = get_data_type_headers(connection, "airbus380_acad", query_text['query'])

            _columns:list = []
            for i in range(len(_heder_query)):
                _columns.append(ft.DataColumn(ft.Text(f"{_heder_query[i]}")))
            
            table_data = ft.DataTable(
                columns=_columns,
            )

            for element in _data_query:
                mean.append(element[-1])
                median.append(element[-1])
                mode.append(element[-1])

                _cells:list = []
                for j in range(len(_heder_query)):
                    _cells.append(ft.DataCell(ft.Text(f"{element[j]}")))

                _row = ft.DataRow(
                    cells=_cells
                )

                table_data.rows.append(_row)


            _mean = calculate_mean(mean)
            _median = calculate_median(median)
            _mode = calculate_mode(mode)

            chart1, chart1_time = bar_chart(_heder_query, _data_query, _data_type)
            plt.close(chart1)
            chart2, chart2_time = pie_chart(_heder_query, _data_query)
            plt.close(chart2)
            chart3, chart3_time = line_chart(_heder_query, _data_query, _data_type)
            plt.close(chart3)

            total_chart_time = chart1_time + chart2_time + chart3_time

            page.views.append(
                ft.View(
                    route="/details",
                    controls=[
                        ft.AppBar(
                            title=ft.Text("Details"), 
                            bgcolor=ft.colors.SURFACE_VARIANT,
                            actions=[
                                button_theme,
                                button_info,
                                ft.PopupMenuButton(
                                    items=[
                                        ft.PopupMenuItem(text="Help"),
                                        ft.PopupMenuItem(),
                                        ft.PopupMenuItem(text="Info"),
                                    ]
                                )
                            ]
                        ),
                        ft.Row(
                            controls=[
                                ft.Column(
                                    controls=[
                                        ft.Text(value=f"Query structure Num {query_text['id']}", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
                                        ft.Container(
                                            content=ft.Column(
                                                controls=[
                                                    ft.Markdown(
                                                        value=f"```console\n {query_text['query']} \n```",
                                                        selectable=True,
                                                        extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
                                                        on_tap_link=lambda e: page.launch_url(e.data),
                                                    )
                                                ],
                                                scroll=ft.ScrollMode.AUTO,
                                            ),
                                            expand=True
                                        )
                                    ],
                                    expand=True
                                ),
                                ft.VerticalDivider(),
                                ft.Column(
                                    controls=[
                                        ft.Tabs(
                                            selected_index=0,
                                            animation_duration=300,
                                            tabs=[
                                                ft.Tab(
                                                    text="Bar Chart",
                                                    icon=ft.icons.BAR_CHART,
                                                    content=ft.Column(
                                                        controls=[
                                                            MatplotlibChart(chart1, expand=True)
                                                        ],
                                                        expand=True
                                                    ),
                                                ),
                                                ft.Tab(
                                                    text="Pie Chart",
                                                    icon=ft.icons.PIE_CHART,
                                                    content=ft.Column(
                                                        controls=[
                                                            MatplotlibChart(chart2, expand=True)
                                                        ],
                                                        expand=True
                                                    ),
                                                ),
                                                ft.Tab(
                                                    text="Line Chart",
                                                    icon=ft.icons.SSID_CHART,
                                                    content=ft.Column(
                                                        controls=[
                                                            MatplotlibChart(chart3, expand=True)
                                                        ],
                                                        expand=True
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
                        ft.Divider(),
                        ft.Row(
                            controls=[
                                ft.Column(
                                    controls=[
                                        ft.Text(value="Data of the query", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
                                        ft.Row(
                                            controls=[
                                                ft.Text(value=f"Mean: {_mean:.2f}", style=ft.TextThemeStyle.BODY_MEDIUM),
                                                ft.Text(value=f"Median: {_median:.2f}", style=ft.TextThemeStyle.BODY_MEDIUM),
                                                ft.Text(value=f"Mode: {_mode:.2f}", style=ft.TextThemeStyle.BODY_MEDIUM),
                                            ],
                                        ),
                                        ft.Container(
                                            content=ft.Column(
                                                controls=[
                                                    table_data,
                                                ],
                                                scroll=ft.ScrollMode.AUTO,
                                            ),
                                            expand=True,
                                            padding=ft.padding.only(left=5, right=5),
                                        ),
                                        ft.Divider(),
                                        ft.Row(
                                            controls=[
                                                ft.Text(value=f"Total rows: {len(_data_query)}", style=ft.TextThemeStyle.BODY_MEDIUM),
                                                ft.Text(value=f"Query execution time: {_query_time:.2f}", style=ft.TextThemeStyle.BODY_MEDIUM),
                                                ft.Text(value=f"Chart's creation time: {total_chart_time:.2f}", style=ft.TextThemeStyle.BODY_MEDIUM),
                                            ]
                                        )
                                    ],
                                    expand=True
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
        try:
            if windows_auth:
                return sql_server.connect(driver=driver, server=server, trusted_connection="yes")
            else:
                return sql_server.connect(driver=driver, server=server, user=user, password=password)
            
        except Exception as e:
            return None
    

    async def submit_connection(e: ft.ControlEvent) -> None:
        nonlocal connection

        if connection is not None:
            connection.close()

        connection = await connect_to_sql_server(dropdown_driver.value, text_server.value, checkbox_windows_auth.value, text_username.value, text_password.value)

        if connection and connection is not None:
            page.go("/")
        
        else:
            if connection is not None:
                connection.close()

            page.open(dlg_modal_error)


    def view_pop(view) -> None:
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)
    
    query_list:list = await print_queries(src='assets/test.sql')

    for query in query_list:
        exp = ft.ExpansionPanel(
            header=ft.ListTile(title=ft.Text(f"SQL query number {query['id']}")),
        )

        exp.content = ft.ListTile(
            title=ft.Text(f"This is in Panel {query['id']}"),
            subtitle=ft.Text(f"Press the icon to go to full view of the query {query['id']}"),
            trailing=ft.IconButton(ft.icons.QUERY_STATS, on_click=lambda _, q_id=query['id']: page.go("/details", query_id=q_id)),
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
    ft.app(target=main, view=ft.WEB_BROWSER)