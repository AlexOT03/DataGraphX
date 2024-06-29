import flet as ft
from flet.matplotlib_chart import MatplotlibChart
import pyodbc as sql_server

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

import re

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


def bar_chart(headers:list, data:list, data_type:list) -> plt.Figure:

    fig, ax = plt.subplots()

    x = np.array(["A", "B", "C", "D"])
    y = np.array([3, 8, 1, 10])

    ax.bar(x, y)

    return fig


def pie_chart(headers:list, data:list, type:list) -> plt.Figure:

    fig, ax = plt.subplots()

    y = np.array([35, 25, 25, 15])

    ax.pie(y)

    return fig


def line_chart(headers:list, data:list, type:list) -> plt.Figure:

    fig, ax = plt.subplots()

    ypoints = np.array([3, 8, 1, 10])

    ax.plot(ypoints, linestyle='dotted')

    return fig


def calculate_mean(list:list):
    suma = 0
    for elemento in list:
        suma += elemento
    media = suma / len(list)

    return round(media, 2)


def calculate_median(list:list):
    
    lista_ordenada = sorted(list)
    n = len(lista_ordenada)
    if n % 2 == 0:
        mediana = (lista_ordenada[n // 2] + lista_ordenada[n // 2 - 1]) / 2
    else:
        mediana = lista_ordenada[n // 2]

    return round(mediana, 2)


def calculate_mode(list:list):

    frecuencia = {}
    for numero in list:
        if numero in frecuencia:
            frecuencia[numero] += 1
        else:
            frecuencia[numero] = 1

    moda = max(frecuencia, key=frecuencia.get)

    return round(moda, 2)


def get_data_type_headers(connection: sql_server.Connection, database: str, query: str) -> tuple[list, list, list]:

    with connection.cursor() as cursor:
        cursor.execute(f"USE {database}")
        cursor.execute(query)
        data = cursor.fetchall()
        headers = [columna[0] for columna in cursor.description]
        data_types = [columna[1] for columna in cursor.description]

    return headers, data, data_types


async def main(page: ft.Page):
    page.title = "DataGraphX"
    page.scroll = ft.ScrollMode.ADAPTIVE
    connection:sql_server.Connection = None
    query_list:list = []


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
        # on_click=open_dlg_modal
    )
    button_theme:ft.IconButton = ft.IconButton(
        icon=ft.icons.LIGHT_MODE,
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
                                ft.Image(src="./assets/icon.png", width=50, height=50, fit=ft.ImageFit.CONTAIN),
                            ],
                            expand=True,
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                        ft.Container(
                            ft.Column(
                                controls=[
                                    ft.Divider(),
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
                                alignment=ft.MainAxisAlignment.CENTER,
                            ),
                            padding=ft.padding.only(top=20, right=180, bottom=20, left=180),
                        ),
                    ],
                ),
            )

        if _page == "/details":

            _id = int(data['query_id'])-1
            query_text = query_list[_id]

            _heder_query, _data_query, _data_type = get_data_type_headers(connection, "airbus380_acad", query_text['query'])

            _columns:list = []
            for i in range(len(_heder_query)):
                _columns.append(ft.DataColumn(ft.Text(f"{_heder_query[i]}")))
            
            table_data = ft.DataTable(
                columns=_columns,
            )

            for element in _data_query:
                _cells:list = []
                for j in range(len(_heder_query)):
                    _cells.append(ft.DataCell(ft.Text(f"{element[j]}")))

                _row = ft.DataRow(
                    cells=_cells
                )

                table_data.rows.append(_row)
            
            mean:list = []
            median:list = []
            mode:list = []

            for element in _data_query:
                mean.append(element[-1])
                median.append(element[-1])
                mode.append(element[-1])
            
            _mean = calculate_mean(mean)
            _median = calculate_median(median)
            _mode = calculate_mode(mode)

            chart1 = bar_chart(_heder_query, _data_query, _data_type)
            chart2 = pie_chart(_heder_query, _data_query, _data_type)
            chart3 = line_chart(_heder_query, _data_query, _data_type)

            page.views.append(
                ft.View(
                    route="/details",
                    controls=[
                        ft.AppBar(
                            title=ft.Text("Details"), 
                            bgcolor=ft.colors.SURFACE_VARIANT,
                            actions=[
                                button_theme,
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
                                                    text="Line Chart",
                                                    icon=ft.icons.SSID_CHART,
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
                        ft.Divider(),
                        ft.Row(
                            controls=[
                                ft.Column(
                                    controls=[
                                        ft.Text(value="Data of the query", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
                                        ft.Row(
                                            controls=[
                                                ft.Text(value=f"Mean: {_mean}", style=ft.TextThemeStyle.BODY_MEDIUM),
                                                ft.Text(value=f"Median: {_median}", style=ft.TextThemeStyle.BODY_MEDIUM),
                                                ft.Text(value=f"Mode: {_mode}", style=ft.TextThemeStyle.BODY_MEDIUM),
                                            ],
                                        ),
                                        ft.Text(value=f"Total rows: {len(_data_query)}", style=ft.TextThemeStyle.BODY_MEDIUM),
                                        table_data,
                                    ],
                                    scroll=ft.ScrollMode.AUTO,
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
        if windows_auth:
            return sql_server.connect(driver=driver, server=server, trusted_connection="yes")
        else:
            return sql_server.connect(driver=driver, server=server, user=user, password=password)
    

    async def submit_connection(e: ft.ControlEvent) -> None:
        nonlocal connection
        connection = await connect_to_sql_server(dropdown_driver.value, text_server.value, checkbox_windows_auth.value, text_username.value, text_password.value)

        if connection and connection is not None:
            page.go("/")
        
        else:
            connection.close()


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
    ft.app(target=main)