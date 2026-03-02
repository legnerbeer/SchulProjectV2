import asyncio
import flet as ft
import pages.functions as f


async def run_sync(page: ft.Page, page_content: ft.Container, color: str, location: int, column_name: str, unit: str):
    """
    Async worker that loads chart data into a container.
    """
    load_chart = f.loadChart(page, page_content, color, location, column_name, unit)
    await load_chart.load_data()


class PageThree(ft.Column):
    """

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
        """
        Initializes the asynchronous elements of the UI and starts background tasks for
        data processing.

        This method performs several key actions. It prepares the app's UI components,
        ensures correct rendering of tab containers, and begins executing background
        tasks that collect and display data for temperature, pressure, humidity, and
        altitude. Each measurement type is displayed in a specific color-coded container
        and rendered only after the respective task is initialized.

        :return: None
        """
        await self._create_app_bar()

        # Initially attach the Temperature container to ensure it's in the page tree
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

        #Create the tabs layout
        tabs = await self.create_tabs()
        self.controls.append(tabs)


        self.update()
        await asyncio.sleep(0.1)  # allow UI to render

        # Start background tasks
        if self.worker_task_temperature is None:
            self.worker_task_temperature = self.page.run_task(
                run_sync,
                self.page,
                self.chart_container_temperature,
                'CYAN',
                3,
                'temperature',
                '°C'
            )

        if self.worker_task_pressure is None:
            self.worker_task_pressure = self.page.run_task(
                run_sync,
                self.page,
                self.chart_container_pressure,
                'RED',
                3,
                'pressure',
                'hPa'

            )
        if self.worker_task_humidity is None:
            self.worker_task_humidity = self.page.run_task(
                run_sync,
                self.page,
                self.chart_container_humidity,
                'GREEN',
                3,
                'humidity',
                '%'
            )
        if self.worker_task_altitude is None:
            self.worker_task_altitude = self.page.run_task(
                run_sync,
                self.page,
                self.chart_container_altitude,
                'YELLOW',
                3,
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
        """
        Creates a tabbed interface with different data displays, such as temperature, pressure,
        humidity, and altitude. Each tab dynamically updates its content upon selection and initiates
        a worker task to process and update the corresponding chart when required.

        The function constructs a set of interactive tabs using the `ft.TabBar` and `ft.Tabs`
        controls and assembles those into a flexible layout with dynamic content handling.

        :returns: A layout container (`ft.Column`) that includes the tab bar, a divider for spacing,
                  and the container for dynamic tab content.
        :rtype: ft.Column
        """
        async def handle_change(e):
            idx = int(e.control.selected_index)
            self.tabs_content_basic.controls.clear()

            if idx == 0:
                self.tabs_content_basic.controls = [self.chart_container_temperature]
                if self.worker_task_temperature is None:
                    self.worker_task_temperature = self.page.run_task(
                        run_sync,
                        self.page,
                        self.chart_container_temperature,
                        'CYAN',
                        3,
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
                        3,
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
                        3,
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
                        3,
                        'altitude',
                        'm'
                    )

            self.tabs_content_basic.update()

        # Visual tab bar
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