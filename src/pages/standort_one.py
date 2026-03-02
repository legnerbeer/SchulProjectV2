import asyncio
import flet as ft
import pages.functions as f


async def run_sync(page: ft.Page, page_content: ft.Container, color: str, location: int, column_name: str, unit: str):
    """
    Async worker that loads chart data into a container.
    The container MUST be already attached to the page before calling update().
    """
    load_chart = f.loadChart(page, page_content, color, location, column_name, unit)
    await load_chart.load_data()


class PageOne(ft.Column):
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
        Asynchronously initializes the application's UI and starts background tasks.

        This method performs the following operations:
        - Creates and configures the application bar.
        - Initializes and attaches the temperature chart container to ensure it is part
          of the page tree initially. Configures visibility of other chart containers
          (pressure, humidity, altitude) to `False`.
        - Updates the UI after initializing the containers.
        - Creates and appends the tab layout to the main application controls.
        - Starts background tasks for processing and updating temperature, pressure,
          humidity, and altitude data. Each task is bound to a specific chart container
          and renders its data in the specified color, frequency, and units.

        :param self: Instance of the class accessing this method.
        :type self: object
        :return: None
        :rtype: None
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

        # Create the tabs layout
        tabs = await self.create_tabs()
        self.controls.append(tabs)


        self.update()
        await asyncio.sleep(0.1)  # allow UI to render

        # starting the background tasks
        if self.worker_task_temperature is None:
            self.worker_task_temperature = self.page.run_task(
                run_sync,
                self.page,
                self.chart_container_temperature,
                'CYAN',
                1,
                'temperature',
                '°C'
            )

        if self.worker_task_pressure is None:
            self.worker_task_pressure = self.page.run_task(
                run_sync,
                self.page,
                self.chart_container_pressure,
                'RED',
                1,
                'pressure',
                'hPa'

            )
        if self.worker_task_humidity is None:
            self.worker_task_humidity = self.page.run_task(
                run_sync,
                self.page,
                self.chart_container_humidity,
                'GREEN',
                1,
                'humidity',
                '%'
            )
        if self.worker_task_altitude is None:
            self.worker_task_altitude = self.page.run_task(
                run_sync,
                self.page,
                self.chart_container_altitude,
                'YELLOW',
                1,
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
        Creates and initializes tabbed navigation with controls for displaying different sensor
        charts and launching corresponding background tasks if needed. Each tab represents a
        specific sensor type: Temperature, Pressure, Humidity, and Altitude. Upon tab selection,
        the tab content updates dynamically, and tasks for sensor data processing are started
        if not already active.

        :raises: None
        :parameters: None
        :return: A fully constructed `ft.Column` containing tab navigation controls and a
            dynamically updating content container.
        :rtype: ft.Column
        """
        async def handle_change(e):
            idx = int(e.control.selected_index)
            self.tabs_content_basic.controls.clear()

            # Switches tab content to selected sensor chart and launches worker task if needed
            if idx == 0:
                self.tabs_content_basic.controls = [self.chart_container_temperature]
                if self.worker_task_temperature is None:
                    self.worker_task_temperature = self.page.run_task(
                        run_sync,
                        self.page,
                        self.chart_container_temperature,
                        'CYAN',
                        1,
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
                        1,
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
                        1,
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
                        1,
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