import hashlib
import sqlite3
from pathlib import Path

import flet as ft

from pages.standort_one import PageOne


class PageLogin(ft.Column):
    """
    Representation of a login and registration management page built using the Flet framework.

    This class handles the user interface for login and registration workflows in a Flet-based UI application.
    It includes features for handling user authentication, managing login state using local storage, and
    updating the navigation UI accordingly. The user interface is implemented using various Flet widgets such as
    containers, text fields, buttons, and tabs.

    :ivar current_page: The current application page this class is managing.
    :type current_page: ft.Page
    :ivar content_manager: A callable responsible for updating and managing page content.
    :type content_manager: callable
    :ivar local_storage: Instance of Shared Preferences for accessing persistent key-value storage.
    :type local_storage: ft.SharedPreferences
    :ivar login_button: The login button that triggers the login workflow.
    :type login_button: ft.Button or None
    :ivar register_button: The register button that triggers the registration workflow.
    :type register_button: ft.Button or None
    :ivar tabs_container_login: Container holding controls for the login tab.
    :type tabs_container_login: ft.Container
    :ivar tabs_container_register: Container holding controls for the register tab.
    :type tabs_container_register: ft.Container
    """
    def __init__(self, page: ft.Page, content_manager, title: str):
        super().__init__(expand=True)

        self.current_page = page
        self._page_title = title
        self.content_manager = content_manager
        self.local_storage = ft.SharedPreferences()
        self.login_button = None
        self.register_button = None

        self.tabs_container_login = ft.Container(
            expand=True,
        )

        self.tabs_container_register = ft.Container(
            expand=True,
        )


    def did_mount(self):
        """Lifesicle of Login Page"""
        self.current_page.run_task(self.async_init)

    async def async_init(self):
        """
        Initializes the asynchronous login and registration interface for the application.

        This method sets up two tab-based sections, one for login and another for registration. Each
        section includes corresponding input fields and buttons with event handlers for the respective
        actions. It also verifies the user's login state and conditionally redirects them. The
        appropriate layout is appended to the application's controls and updated to reflect the current
        state.

        :rtype: None
        :return: None
        """
        #Login Feed
        login_email = ft.TextField(
            label="Email",
            width=350,
            border_color=ft.Colors.PRIMARY,

        )
        login_password = ft.TextField(
            label="Password",
            password=True,
            width=350,
            can_reveal_password=True,
            border_color=ft.Colors.PRIMARY,
            on_click=lambda e: self.current_page.run_task(self.try_login, e, login_email.value, login_password.value),
        )
        self.login_button = self.register_button = ft.Button(
            content="login",
            on_click = lambda e: self.current_page.run_task(self.try_login, e, login_email.value, login_password.value),
        )
        self.tabs_container_login.content = ft.Column(
                spacing=15,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Text("Login", size=28, weight=ft.FontWeight.BOLD),
                    login_email,
                    login_password,
                    self.login_button
                ],
            )




        #Register Field
        email_register = ft.TextField(
            label="Email",
            width=350,
            border_color=ft.Colors.PRIMARY,
        )
        password_register = ft.TextField(
            label="Password",
            password=True,
            width=350,
            can_reveal_password=True,
            border_color=ft.Colors.PRIMARY,
        )
        password_repeat = ft.TextField(
            label="Repeat Password",
            password=True,
            width=350,
            can_reveal_password=True,
            border_color=ft.Colors.PRIMARY,
            on_submit= lambda e: self.current_page.run_task(self.try_register, e, email_register.value, password_register.value, password_repeat.value)
        )
        self.register_button = ft.Button(
            content="Register",
            on_click = lambda e: self.current_page.run_task(self.try_register, e, email_register.value, password_register.value, password_repeat.value)
        )




        self.tabs_container_register.content = ft.Column(
                spacing=15,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Text("Register", size=28, weight=ft.FontWeight.BOLD),
                    email_register,
                    password_register,
                    password_repeat,
                    self.register_button
                ],
            )

        # Check login state
        login_state = await self.local_storage.get("login")

        if login_state == "True":
            await self.content_manager(
                PageOne(
                    self.current_page,
                    content_manager=self.content_manager,
                    title="EST Tettnag",
                )
            )
            return

        await self._create_app_bar()

        tabs = await self.create_tabs()
        self.controls.append(tabs)

        self.update()


    async def _create_app_bar(self):
        """
        Creates and updates the app bar for the current page.

        This method sets up an app bar for the current page using the predefined
        title and updates the page to reflect the changes.

        :raises AttributeError: if `current_page` or its `appbar` attribute are
            not properly initialized.
        :return: None
        """
        self.current_page.appbar = ft.AppBar(
            title=ft.Text(self._page_title),
        )
        self.current_page.update()


    async def create_tabs(self):
        """
        Creates a `Tabs` component with a default selected index of 0, and containing
        two tabs for "Login" and "Register". The tabs are structured using a `TabBar`
        and a `TabBarView` with designated content containers for each tab.

        :return: An instantiated `Tabs` component with "Login" and "Register" tabs.
        :rtype: ft.Tabs
        """
        return ft.Tabs(
            selected_index=0,
            length=2,
            expand=True,
            content=ft.Column(
                expand=True,
                controls=[
                    ft.TabBar(
                        tabs=[
                            ft.Tab("Login"),
                            ft.Tab("Register"),
                        ],
                    ),
                    ft.TabBarView(
                        expand=True,
                        controls=[
                            self.tabs_container_login,
                            self.tabs_container_register,
                        ],
                    ),
                ],
            ),
        )
    async def try_register(self, e, email: str, password:str, password_repeat:str):
        """
        Attempts to register a user by validating the provided inputs, checking for the existence
        of the email in the database, and storing the new credentials if the user does not already
        exist. If registration is successful, it updates local storage and navigates to a specific
        page. Displays appropriate messages for input validation and database constraints.

        :param e: Event or handler invoked during the registration process.
        :param email: The email address of the user attempting to register. Must not be empty.
        :type email: str
        :param password: The password chosen by the user. Must not be empty.
        :type password: str
        :param password_repeat: The repeated password for confirmation. Must match the password.
        :type password_repeat: str
        :return: None
        :rtype: None
        :raises sqlite3.Error: If a database operation fails.
        """
        if email == "":
            self.current_page.show_dialog(ft.SnackBar("Please enter an email"))
            return
        if password == "":
            self.current_page.show_dialog(ft.SnackBar("Please enter a password"))
            return
        if password_repeat == "":
            self.current_page.show_dialog(ft.SnackBar("Please repeat your password"))
            return
        if password == password_repeat:

            path_to_DB = Path(__file__).parent.parent / ".auth"
            if not path_to_DB.exists():
                path_to_DB.mkdir(parents=True)
            path_to_DB_file = path_to_DB / "mqtt_metadata.db"
            conn = sqlite3.connect(path_to_DB_file)
            cursor = conn.cursor()
            sql_statement = f"SELECT COUNT(email) FROM mqtt_login WHERE email = (?)"
            cursor.execute(sql_statement, (email,))
            data = cursor.fetchone()
            conn.commit()
            if data[0] == 0:
                try:
                    sql_statement = f"insert into mqtt_login (email, password) values (?, ?)"
                    cursor.execute(sql_statement, (email, hashlib.sha256(password.encode('utf-8')).hexdigest()))
                    conn.commit()
                    conn.close()
                    await self.local_storage.set("login", "True")
                    await self.content_manager(
                        PageOne(
                            self.current_page,
                            content_manager=self.content_manager,
                            title="EST Tettnag",
                        )
                    )
                except Exception as e:
                    print(e)
            else:
                self.current_page.show_dialog(ft.SnackBar("Email already exists"))
        else:
            self.current_page.show_dialog(ft.SnackBar("Passwords do not match"))


    async def try_login(self, e, email: str, password:str):
        """
        Attempt to perform a login operation using the provided credentials. This function
        retrieves user data from an SQLite database, verifies the provided password against the
        stored hash using a secure hashing algorithm, and updates the application state
        accordingly upon success or failure.

        :param e: An event object triggered during the login operation.
        :param email: The email address of the user attempting to log in.
        :type email: str
        :param password: The plain text password of the user attempting to log in.
        :type password: str
        :return: None
        """
        def verify_hash(plain_text, stored_hash):
            """
            Verify if a given plain text matches a stored hash using HMAC-based comparison.

            This function computes the SHA-256 hash of the plain text, then checks if it
            matches the stored hash using a constant-time comparison method. This approach
            helps mitigate timing attacks by ensuring the comparison does not reveal
            information about partial matches.

            :param plain_text: The original plain text string to verify.
            :type plain_text: str
            :param stored_hash: The precomputed hash string to compare against.
            :type stored_hash: str
            :return: A boolean indicating whether the computed hash matches the stored hash.
            :rtype: bool
            """
            current_hash = hashlib.sha256(plain_text.encode()).hexdigest()

            import hmac
            return hmac.compare_digest(current_hash, stored_hash)

        if password == "":
            self.current_page.show_dialog(ft.SnackBar("Please enter a password"))
            return
        if email == "":
            self.current_page.show_dialog(ft.SnackBar("Please enter an email"))
            return


        path_to_DB = Path(__file__).parent.parent / ".auth"
        if not path_to_DB.exists():
            path_to_DB.mkdir(parents=True)
        path_to_DB_file = path_to_DB / "mqtt_metadata.db"
        conn = sqlite3.connect(path_to_DB_file)
        cursor = conn.cursor()
        sql_statement = f"SELECT * FROM mqtt_login WHERE email = (?) LIMIT 1"
        cursor.execute(sql_statement, (email,))
        data = cursor.fetchone()
        conn.commit()
        conn.close()

        if data is None:
            self.current_page.show_dialog(ft.SnackBar("Email not found"))
            return
        if verify_hash(password, data[1]):
            await self.local_storage.set("login", "True")
            await self.content_manager(
                PageOne(
                    self.current_page,
                    content_manager=self.content_manager,
                    title="EST Tettnag",
                )
            )
        else:
            self.current_page.show_dialog(ft.SnackBar("Wrong password"))
