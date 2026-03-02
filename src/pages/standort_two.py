import asyncio
import flet as ft
import pages.functions as f


async def run_sync(page: ft.Page, page_content: ft.Container, color: str, location: int, column_name: str, unit: str):
    """
    Async worker that loads chart data into a container.
    """
    load_chart = f.loadChart(page, page_content, color, location, column_name, unit)
    await load_chart.load_data()


class PageTwo(ft.Column):
    """
    Defines the PageTwo class, which implements a dynamic UI component for managing
    and interacting with data visualizations across multiple tabs.

    The PageTwo class is designed to manage UI components, including charts for
    temperature, pressure, humidity, and altitude. It provides methods for mounting
    the UI, initializing asynchronous tasks, and dynamically switching between
    tabs with associated data visualizations.

    :ivar current_page: The current page instance to which this component belongs.
    :type current_page: ft.Page
    :ivar tabs_content_basic: Container for displaying tab-specific content.
    :type tabs_content_basic: ft.Column
    :ivar chart_container_temperature: Container for the temperature chart visualization.
    :type chart_container_temperature: ft.Container
    :ivar chart_container_pressure: Container for the pressure chart visualization.
    :type chart_container_pressure: ft.Container
    :ivar chart_container_humidity: Container for the humidity chart visualization.
    :type chart_container_humidity: ft.Container
    :ivar chart_container_altitude: Container for the altitude chart visualization.
    :type chart_container_altitude: ft.Container
    :ivar init_task: Task managing the initial asynchronous initialization.
    :type init_task: asyncio.Task or None
    :ivar worker_task_temperature: Background task managing updates for the temperature chart.
    :type worker_task_temperature: asyncio.Task or None
    :ivar worker_task_pressure: Background task managing updates for the pressure chart.
    :type worker_task_pressure: asyncio.Task or None
    :ivar worker_task_humidity: Background task managing updates for the humidity chart.
    :type worker_task_humidity: asyncio.Task or None
    :ivar worker_task_altitude: Background task managing updates for the altitude chart.
    :type worker_task_altitude: asyncio.Task or None
    """
    def __init__(self, page: ft.Page, content_manager, title: str):
        super().__init__(scroll=ft.ScrollMode.ADAPTIVE)
        self.current_page = page
        self._page_title = title
        self.init_task = None
        self.worker_task_temperature = None
        self.worker_task_pressure = None
        self.worker_task_altitude = None
        self.worker_task_humidity = None

        # Tabs content containers
        self.tabs_content_basic = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)
        self.chart_container_temperature = ft.Container(expand=True)
        self.chart_container_pressure = ft.Container(expand=True)
        self.chart_container_humidity = ft.Container(expand=True)
        self.chart_container_altitude = ft.Container(expand=True)

    def did_mount(self):
        # Start async init after component mounts
        self.init_task = self.page.run_task(self.async_init)

    async def async_init(self):

        await self._create_app_bar()

        #Initially the Tabs
        self.tabs_content_basic.controls = [
            self.chart_container_temperature,
            self.chart_container_pressure,
            self.chart_container_humidity,
            self.chart_container_altitude
        ]

        self.chart_container_pressure.visible = False
        self.chart_container_humidity.visible = False
        self.chart_container_altitude.visible = False
        self.update()


        tabs = await self.create_tabs()
        self.controls.append(tabs)


        self.update()
        await asyncio.sleep(0.1)

        #Start background tasks
        if self.worker_task_temperature is None:
            self.worker_task_temperature = self.page.run_task(
                run_sync,
                self.page,
                self.chart_container_temperature,
                'CYAN',
                2,
                'temperature',
                '°C'
            )

        if self.worker_task_pressure is None:
            self.worker_task_pressure = self.page.run_task(
                run_sync,
                self.page,
                self.chart_container_pressure,
                'RED',
                2,
                'pressure',
                'hPa'

            )
        if self.worker_task_humidity is None:
            self.worker_task_humidity = self.page.run_task(
                run_sync,
                self.page,
                self.chart_container_humidity,
                'GREEN',
                2,
                'humidity',
                '%'
            )
        if self.worker_task_altitude is None:
            self.worker_task_altitude = self.page.run_task(
                run_sync,
                self.page,
                self.chart_container_altitude,
                'YELLOW',
                2,
                'altitude',
                'm'
            )

    async def _create_app_bar(self):
        """Create the AppBar"""
        self.current_page.appbar = ft.AppBar(
            title=ft.Column(
                controls=[ft.Text(self._page_title)],
                alignment=ft.MainAxisAlignment.SPACE_AROUND,
            )
        )
        self.current_page.update()

    async def create_tabs(self):
        """Create tabs with a controller and switching logic"""

        async def handle_change(e):
            idx = int(e.control.selected_index)
            self.tabs_content_basic.controls.clear()

            # Switches chart visibility and launches worker tasks based on selected tab
            if idx == 0:
                self.tabs_content_basic.controls = [self.chart_container_temperature]
                if self.worker_task_temperature is None:
                    self.worker_task_temperature = self.page.run_task(
                        run_sync,
                        self.page,
                        self.chart_container_temperature,
                        'CYAN',
                        2,
                        'temperature',
                        '°C'
                    )
            elif idx == 1:
                self.chart_container_pressure.visible = True
                self.tabs_content_basic.controls = [self.chart_container_pressure]
                if self.worker_task_pressure is None:
                    self.worker_task_pressure = self.page.run_task(
                        run_sync,
                        self.page,
                        self.chart_container_pressure,
                        'RED',
                        2,
                        'pressure',
                        'hPa'

                    )

            elif idx == 2:
                self.chart_container_humidity.visible = True
                self.tabs_content_basic.controls = [self.chart_container_humidity]
                if self.worker_task_humidity is None:
                    self.worker_task_humidity = self.page.run_task(
                        run_sync,
                        self.page,
                        self.chart_container_humidity,
                        'GREEN',
                        2,
                        'humidity',
                        '%'
                    )
            elif idx == 3:
                self.chart_container_altitude.visible = True
                self.tabs_content_basic.controls = [self.chart_container_altitude]
                if self.worker_task_altitude is None:
                    self.worker_task_altitude = self.page.run_task(
                        run_sync,
                        self.page,
                        self.chart_container_altitude,
                        'YELLOW',
                        2,
                        'altitude',
                        'm'
                    )

            self.tabs_content_basic.update()


        tab_bar = ft.TabBar(
            tabs=[
                ft.Tab("Temperature"),
                ft.Tab("Pressure"),
                ft.Tab("Humidity"),
                ft.Tab("Altitude"),
            ],
            tab_alignment=ft.TabAlignment.FILL,
            scrollable=False
        )

        # Logic controller
        tabs_controller = ft.Tabs(
            length=4,
            selected_index=0,
            content=tab_bar,
            on_change=lambda e: self.current_page.run_task(handle_change, e),
        )

        # Full layout
        return ft.Column([
            tabs_controller,
            ft.Divider(color=ft.Colors.TRANSPARENT, height=10),
            ft.Container(
                content=self.tabs_content_basic,
                expand=True,
                padding=ft.padding.all(30),
            )
        ], expand=True)