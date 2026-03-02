import asyncio
import zoneinfo
from pathlib import Path
import datetime
import flet_charts as fch
import flet as ft
import sqlite3
import math


class loadChart():
    """
    Handles the loading and real-time display of chart data in a responsive UI.

    The `loadChart` class is responsible for rendering charts with real-time
    statistical data and dynamically updating the chart with time-varying data
    streams over a specific column. The chart includes supportive UI components
    like average statistics (arithmetic mean, max, and min values) and axes labels.

    :ivar page: Represents the main page where the chart will be displayed.
    :type page: ft.Page
    :ivar page_content: Container object used to embed dynamic chart updates.
    :type page_content: ft.Container
    :ivar color: Color scheme for the chart lines.
    :type color: str
    :ivar location: Location identifier for data filtering.
    :type location: Any
    :ivar column_name: The column selected from which chart data is derived.
    :type column_name: str
    :ivar unit: Unit of measurement for displayed data.
    :type unit: str
    :ivar chart_container: Dynamic container that holds the generated chart.
    :type chart_container: ft.Column
    """
    def __init__(self, page: ft.Page, page_content: ft.Container, *args):
        self.page = page
        self.page_content = page_content
        self.color = ft.Colors.upper(args[0])
        self.location = args[1]
        self.column_name = args[2]
        self.unit = args[3]
        self.chart_container =ft.Column()
        self.page.appbar.actions = [ft.IconButton(ft.Icons.WIFI, style=ft.ButtonStyle(color=ft.Colors.GREEN))]

    async def load_data(self):
        """
        Asynchronously processes and visualizes real-time data by integrating a dynamic chart,
        statistical tables, and labels. The method continually fetches data from an MQTT loop
        or a database connection, processes it for display, and updates UI elements in an
        event-driven architecture. The visualization includes configurable options for the Y-axis,
        timestamp formatting for the X-axis, and statistical calculations such as arithmetic mean,
        maximum, and minimum values.

        :rtype: None

        :raises sqlite3.Error: If there's a database-related error during the data fetching process.
        :raises asyncio.CancelledError: If the asynchronous task is cancelled while running.
        :raises Exception: For any unhandled errors occurring during the task execution.

        :return: None
        """
        chart_points = []
        bottom_axis = fch.ChartAxis(label_size=32)
        left_badge = fch.ChartAxis(label_size=70, labels=[

        ])

        #definning the data series
        data_series = [
            fch.LineChartData(
                color=self.color,
                points=chart_points,
                stroke_width=4,
                curved=True,
                point=True,
                below_line_bgcolor=ft.Colors.with_opacity(
                    0.2, self.color
                ),
            )
        ]
        #defining the LineChart
        chart = fch.LineChart(
            interactive=True,
            height=500,
            data_series=data_series,
            min_y=0,
            min_x=0,
            max_x=20,
            expand=True,
            bottom_axis=bottom_axis,
            left_axis=left_badge
        )
        #create Labels for the X-axis
        unit_label = ft.Text(
            f"{self.unit}",
            size=16,
            weight=ft.FontWeight.BOLD
        )
        #create the Table for the averages
        average_table = ft.Column()


        #create the init of the chart Container
        self.chart_container = ft.Column(
            expand=True,
            controls=[
                chart,
                ft.Divider(color=ft.Colors.TRANSPARENT, height=50),
                average_table
            ]
        )
        self.page_content.content = ft.Column([
            unit_label,
            self.chart_container

        ])
        self.page_content.update()
        try:
            # Loops; fetches data; updates chart with statistics
            while True:
                await self._loop_for_mqtt()
                try:
                    data = self._connection()

                except sqlite3.Error as db_error:
                    print(f"Database error: {db_error}")
                    await asyncio.sleep(2)
                    continue

                if len(data) >= 11:
                    # Processes database data into timezone-adjusted chart with statistics and auto-scaling
                    try:
                        data.reverse()
                        average_table.controls.clear()
                        chart_points.clear()
                        bottom_axis.labels.clear()

                        for i in range(11):
                            value = float(data[i][0])
                            dt_utc = datetime.datetime.strptime(data[i][1], "%Y-%m-%d %H:%M:%S")


                            dt_utc = dt_utc.replace(tzinfo=zoneinfo.ZoneInfo("UTC"))
                            dt_german = dt_utc.astimezone(zoneinfo.ZoneInfo("Europe/Berlin"))


                            timestamp = dt_german.strftime("%H:%M:%S")
                            if self.column_name == "pressure":
                                value = int(value)
                            chart_points.append(
                                fch.LineChartDataPoint(i * 2, value)
                            )

                            bottom_axis.labels.append(
                                fch.ChartAxisLabel(
                                    value=i * 2,
                                    label=ft.Text(timestamp, size=12)
                                )
                            )

                        # Auto-scale Y axis
                        max_val = max(float(row[0]) for row in data)
                        min_val = min(float(row[0]) for row in data)

                        #Calculate and Display Statics (Arithetic Mean, min and max)
                        arithmetic_mean = 0
                        for i in range(11):
                            arithmetic_mean += float(data[i][0])
                        arithmetic_mean /= 11
                        average_table.controls.extend([
                            ft.DataTable(
                                width=3000,
                                columns=[
                                    ft.DataColumn(label=ft.Text(f"Max. {self.column_name.capitalize()}")),
                                    ft.DataColumn(label=ft.Text(f"{max_val:.2f} {self.unit}")),
                                ],
                                rows=[
                                    ft.DataRow(
                                        cells=[
                                            ft.DataCell(ft.Text(f"Min. {self.column_name.capitalize()}")),
                                            ft.DataCell(ft.Text(f"{min_val:.2f} {self.unit}")),
                                        ]
                                    ),
                                    ft.DataRow(
                                        cells=[
                                            ft.DataCell(ft.Text(f"Arithmetic mean of {self.column_name.capitalize()}")),
                                            ft.DataCell(ft.Text(f"{arithmetic_mean:.2f} {self.unit}")),
                                        ]
                                    ),
                                ],
                            )
                            ]
                        )
                        max_y = math.ceil(max_val)

                        # Add breathing room
                        range_raw = max_y - 0
                        padding = max(1, math.ceil(range_raw * 0.5))


                        chart.max_y = max_y + padding

                        # Keep min_y >= 0 if you don't want negatives
                        chart.min_y = max(0, chart.min_y-10)

                        # Calculate clean interval (about 5 grid lines)
                        range_y = chart.max_y - chart.min_y
                        interval = max(1, math.ceil(range_y / 5))

                        chart.horizontal_grid_lines = fch.ChartGridLines(
                            interval=interval,
                            color=ft.Colors.with_opacity(0.2, ft.Colors.ON_SURFACE),
                            width=1
                        )

                        chart.update()

                    except (ValueError, TypeError) as data_error:
                        print(f"Data processing error: {data_error}")

                self.page_content.update()
                await asyncio.sleep(2)

        except asyncio.CancelledError:
            print("Chart task cancelled properly")

        except Exception as e:
            print(f"Unexpected error: {e}")

        finally:
            print("Worker stopped cleanly")



    def _connection(self) -> list:
        """
        Connects to the database and returns the last 11 values of the selected column
        :return:
        """
        path_to_DB = Path(__file__).parent.parent / ".auth"
        path_to_DB.mkdir(parents=True, exist_ok=True)
        path_to_DB_file = path_to_DB / "mqtt_metadata.db"

        conn = sqlite3.connect(path_to_DB_file)
        cursor = conn.cursor()

        data = cursor.execute(
            f"""
                                SELECT {self.column_name}, capture_timestamp, location_id
                                FROM mqtt_metadata
                                WHERE location_id = ?
                                ORDER BY capture_timestamp DESC
                                LIMIT 11
                                """,
            (self.location,)
        ).fetchall()

        conn.close()
        return data

    async def _loop_for_mqtt(self) -> None:
        """
        Continuously monitors the MQTT connection status and updates the UI
        accordingly. This method checks the status stored in a database file
        and sets the application bar icon to signify the connection state.

        :return: None
        """
        path_to_DB = Path(__file__).parent.parent / ".auth"
        path_to_DB.mkdir(parents=True, exist_ok=True)
        path_to_DB_file = path_to_DB / "mqtt_metadata.db"

        conn = sqlite3.connect(path_to_DB_file)
        cursor = conn.cursor()

        data = cursor.execute(
            f"SELECT status FROM mqtt_lastwill"
        ).fetchone()
        conn.close()
        status = data[0]
        if data is None or status != "online":
            self.page.appbar.actions = [ft.IconButton(ft.Icons.WIFI_OFF, style=ft.ButtonStyle(color=ft.Colors.RED))]
            self.page.update()
        else:
            self.page.appbar.actions = [ft.IconButton(ft.Icons.WIFI, style=ft.ButtonStyle(color=ft.Colors.GREEN))]
            self.page.update()

