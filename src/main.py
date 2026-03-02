import asyncio
import sqlite3
from pathlib import Path



from pages.standort_one import PageOne
from pages.standort_two import PageTwo
from pages.standort_three import PageThree
from pages.login import PageLogin
import flet as ft


#Static Variables
_STANDORT_ONE:str = "Tettnang EST"
_STANDORT_TWO:str = "Aussichtspunkt Tettnang"
_STANDORT_THREE:str = "Aussichtspunkt Liebenau"
path_to_DB = Path(__file__).parent / ".auth"
if not path_to_DB.exists():
    path_to_DB.mkdir(parents=True)
path_to_DB_file = path_to_DB / "mqtt_metadata.db"
conn = sqlite3.connect(path_to_DB_file)
cursor = conn.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS mqtt_login
                  (
                      email       VARCHAR(255),
                      password          VARCHAR(255)
                  )""")



async def clear_and_add_control(page_content: ft.Container, control):
    """Replaces the content of the main container and updates the UI."""
    page_content.content = control
    page_content.update()




async def main(page: ft.Page):
    local_storage = ft.SharedPreferences()

    # Ensure login key exists
    if not await local_storage.contains_key("login"):
        await local_storage.set("login", "False")

    page.title = "Weather App"
    page.theme = ft.Theme(use_material3=True, color_scheme_seed=ft.Colors.CYAN)

    # Load theme mode
    theme_val = await local_storage.get("theme_mode")
    page.theme_mode = (
        ft.ThemeMode.LIGHT if theme_val == "light"
        else ft.ThemeMode.DARK if theme_val == "dark"
        else ft.ThemeMode.SYSTEM
    )

    page_content = ft.Container(expand=True)

    #routing
    async def route_to(control):
        page_content.content = control
        page_content.update()

    #Build NavigationRail
    async def build_rail():
        login_state = await local_storage.get("login")
        is_logged_in = login_state == "True"

        login_label = "Logout" if is_logged_in else "Login"
        selected_index = 0 if is_logged_in else 3

        return ft.NavigationRail(
            selected_index=selected_index,
            label_type=ft.NavigationRailLabelType.ALL,
            group_alignment=-0.9,
            destinations=[
                ft.NavigationRailDestination(
                    icon=ft.Icons.LOCATION_ON_OUTLINED,
                    selected_icon=ft.Icons.LOCATION_ON,
                    label=_STANDORT_ONE,
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.LOCATION_ON_OUTLINED,
                    selected_icon=ft.Icons.LOCATION_ON,
                    label=_STANDORT_TWO,
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.LOCATION_ON_OUTLINED,
                    selected_icon=ft.Icons.LOCATION_ON,
                    label=_STANDORT_THREE,
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.LOGOUT if is_logged_in else ft.Icons.LOGIN,
                    selected_icon=ft.Icons.LOGIN,
                    label=login_label,
                ),
            ],
            on_change=navigation_changed,
        )

    #NavigationRail changed (Cordinate the Change)
    async def navigation_changed(e):
        idx = e.control.selected_index
        login_state = await local_storage.get("login")

        # Block access if not logged in
        if login_state == "False" and idx != 3:
            rail.selected_index = 3
            rail.update()
            return

        if idx == 0:
            page.title = _STANDORT_ONE
            await route_to(PageOne(page, content_manager=refresh_ui, title=_STANDORT_ONE))

        elif idx == 1:
            page.title = _STANDORT_TWO
            await route_to(PageTwo(page, content_manager=refresh_ui, title=_STANDORT_TWO))

        elif idx == 2:
            page.title = _STANDORT_THREE
            await route_to(PageThree(page, content_manager=refresh_ui, title=_STANDORT_THREE))

        elif idx == 3:
            if login_state == "True":
                await local_storage.set("login", "False")
                await refresh_ui()
            else:
                page.title = "Login"
                await route_to(
                    PageLogin(
                        page,
                        content_manager=refresh_ui,
                        title="Login"
                    )
                )

        page.update()

    #Refresch UI for Lobin / Logout
    async def refresh_ui(*args):
        nonlocal rail

        # rebuild rail
        new_rail = await build_rail()
        rail.destinations = new_rail.destinations
        rail.selected_index = new_rail.selected_index
        rail.update()

        await navigation_changed(type("obj", (), {"control": rail}))


    # Initial UI build
    rail = await build_rail()

    page.add(
        ft.Row(
            [
                rail,
                ft.VerticalDivider(width=1),
                ft.Column(
                    [page_content],
                    expand=True,
                    alignment=ft.MainAxisAlignment.START,
                    scroll=ft.ScrollMode.ADAPTIVE,
                ),
            ],
            expand=True,
        )
    )

    await navigation_changed(type("obj", (), {"control": rail}))


if __name__ == "__main__":
    ft.run(main=main)