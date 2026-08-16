"""
m3uScan v21.5 - Kivy GUI Edition
Main Application Entry Point
Cross-platform für Android + Desktop
"""

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.progressbar import ProgressBar
from kivy.uix.switch import Switch
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.clock import Clock
import asyncio

from .utils import (
    platform,
    theme,
    responsive,
    APP_NAME,
    APP_VERSION,
    STATUS_EMOJIS,
)
from .services import LinkLedgerAdapter, OfflineManager


class M3uScanApp(App):
    """
    m3uScan v21.5 Kivy Application
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = f"{APP_NAME} - {APP_VERSION}"

        # Platform & Theme Detection
        self.is_mobile = platform.is_mobile()
        self.is_qpython = platform.is_qpython()
        theme.set_dark_mode(True)  # Default: Dark Mode

        # Services
        try:
            self.ledger_adapter = LinkLedgerAdapter()
        except Exception as e:
            print(f"[ERROR] LinkLedger Adapter failed: {e}")
            self.ledger_adapter = None

        self.offline_manager = OfflineManager()

        # Async Loop
        self.async_loop = None

    def build(self):
        """Baue Kivy UI"""

        # Window Setup
        if self.is_mobile:
            Window.size = (1080, 1920)  # Phone Portrait
        else:
            Window.size = (1200, 700)  # Desktop

        # Main Screen Manager
        self.screen_manager = ScreenManager()

        # Add Screens
        self.screen_manager.add_widget(MainScreen(name="main", app=self))
        self.screen_manager.add_widget(AccountsScreen(name="accounts", app=self))
        self.screen_manager.add_widget(StatusScreen(name="status", app=self))
        self.screen_manager.add_widget(SettingsScreen(name="settings", app=self))

        return self.screen_manager

    def on_start(self):
        """Wird bei App-Start aufgerufen"""

        # Setup Async Loop
        self._setup_async_loop()

        # Startup Checks
        if not self.ledger_adapter:
            self._show_error("m3uScan Fehler", "LinkLedger konnte nicht geladen werden")

    def _setup_async_loop(self):
        """Integriere asyncio mit Kivy Event Loop"""
        try:
            self.async_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.async_loop)

            # Schedule asyncio pulse in Kivy
            Clock.schedule_interval(self._pump_async_loop, 0.001)
        except Exception as e:
            print(f"[ERROR] Async loop setup failed: {e}")

    def _pump_async_loop(self, dt):
        """Pumpe asyncio Event Loop"""
        try:
            self.async_loop.run_until_complete(asyncio.sleep(0))
        except Exception as e:
            print(f"[ERROR] Async pump failed: {e}")

    def _show_error(self, title: str, message: str):
        """Zeige Error-Dialog"""
        content = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(10))
        content.add_widget(Label(text=message, size_hint_y=0.8))
        content.add_widget(
            Button(text="OK", size_hint_y=0.2, on_press=lambda x: error_popup.dismiss())
        )

        error_popup = Popup(title=title, content=content, size_hint=(0.8, 0.3))
        error_popup.open()


class MainScreen(Screen):
    """Startbildschirm mit Navigation"""

    def __init__(self, app=None, **kwargs):
        super().__init__(**kwargs)
        self.app = app

        layout = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(10))

        # Header
        header = BoxLayout(size_hint_y=0.15, orientation="vertical")
        header.add_widget(Label(text=APP_NAME, font_size=dp(24)))
        header.add_widget(Label(text=f"v{APP_VERSION}", font_size=dp(12)))
        layout.add_widget(header)

        # Main Menu Buttons
        menu_layout = GridLayout(cols=1, spacing=dp(10), size_hint_y=0.7)

        buttons = [
            ("📋 Konten-Manager", "accounts"),
            ("📊 Status-Überwachung", "status"),
            ("⚙️ Einstellungen", "settings"),
        ]

        for label, screen in buttons:
            btn = Button(text=label, size_hint_y=0.3)
            btn.bind(on_press=lambda x, s=screen: self.go_to_screen(s))
            menu_layout.add_widget(btn)

        layout.add_widget(menu_layout)

        # Offline Indicator
        if self.app.offline_manager:
            layout.add_widget(self.app.offline_manager.create_status_widget())

        self.add_widget(layout)

    def go_to_screen(self, screen_name: str):
        """Wechsle zu anderem Screen"""
        self.app.screen_manager.current = screen_name


class AccountsScreen(Screen):
    """Account-Manager Screen"""

    def __init__(self, app=None, **kwargs):
        super().__init__(**kwargs)
        self.app = app

        layout = BoxLayout(orientation="vertical", spacing=dp(10), padding=dp(10))

        # Toolbar
        toolbar = BoxLayout(size_hint_y=0.08, spacing=dp(5))
        toolbar.add_widget(Button(text="➕ Add", on_press=self.show_add_dialog))
        toolbar.add_widget(Button(text="🔄 Refresh", on_press=self.refresh_list))
        toolbar.add_widget(Button(text="← Back", on_press=lambda x: self.go_back()))
        layout.add_widget(toolbar)

        # Account List
        self.account_list = RecycleView()
        self.refresh_list(None)
        layout.add_widget(self.account_list)

        self.add_widget(layout)

    def refresh_list(self, instance):
        """Aktualisiere Account-Liste"""
        if not self.app.ledger_adapter:
            return

        accounts = self.app.ledger_adapter.get_all_accounts()

        # Prepare data for RecycleView
        data = []
        for account in accounts:
            data.append(
                {
                    "text": f"{account['username']} | {account['assignment_count']} Zuweisungen",
                    "key": account["key"],
                    "size_hint_y": None,
                    "height": dp(50),
                }
            )

        self.account_list.data = data

    def show_add_dialog(self, instance):
        """Zeige Add-Account Dialog"""

        content = BoxLayout(orientation="vertical", spacing=dp(10), padding=dp(10))

        content.add_widget(Label(text="Host:Port", size_hint_y=0.1))
        host_input = TextInput(multiline=False, size_hint_y=0.1)
        content.add_widget(host_input)

        content.add_widget(Label(text="Username", size_hint_y=0.1))
        user_input = TextInput(multiline=False, size_hint_y=0.1)
        content.add_widget(user_input)

        content.add_widget(Label(text="Password", size_hint_y=0.1))
        pass_input = TextInput(multiline=False, password=True, size_hint_y=0.1)
        content.add_widget(pass_input)

        content.add_widget(Label(text="Person/Device", size_hint_y=0.1))
        person_input = TextInput(multiline=False, size_hint_y=0.1)
        content.add_widget(person_input)

        button_layout = BoxLayout(size_hint_y=0.2, spacing=dp(5))
        button_layout.add_widget(Button(text="Cancel", on_press=lambda x: dialog.dismiss()))
        button_layout.add_widget(
            Button(
                text="Add",
                on_press=lambda x: self.on_account_added(
                    host_input, user_input, pass_input, person_input, dialog
                ),
            )
        )
        content.add_widget(button_layout)

        dialog = Popup(title="Add Account", content=content, size_hint=(0.8, 0.7))
        dialog.open()

    def on_account_added(self, host_input, user_input, pass_input, person_input, dialog):
        """Callback für Account hinzufügen"""
        if not (host_input.text and user_input.text and pass_input.text and person_input.text):
            return

        key = f"{user_input.text}:{pass_input.text}"

        if self.app.ledger_adapter.add_assignment(key, person_input.text, device=host_input.text):
            dialog.dismiss()
            self.refresh_list(None)

    def go_back(self):
        """Gehe zurück zum Hauptmenü"""
        self.app.screen_manager.current = "main"


class StatusScreen(Screen):
    """Status-Monitor Screen"""

    def __init__(self, app=None, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.check_in_progress = False

        layout = BoxLayout(orientation="vertical", spacing=dp(10), padding=dp(10))

        # Toolbar
        toolbar = BoxLayout(size_hint_y=0.08, spacing=dp(5))
        toolbar.add_widget(Button(text="✓ Check All", on_press=self.start_batch_check))
        toolbar.add_widget(Button(text="← Back", on_press=lambda x: self.go_back()))
        layout.add_widget(toolbar)

        # Progress Bar
        self.progress_bar = ProgressBar(size_hint_y=0.05, max=100)
        layout.add_widget(self.progress_bar)

        # Status List
        self.status_list = RecycleView()
        layout.add_widget(self.status_list)

        self.add_widget(layout)

    def start_batch_check(self, instance):
        """Starte Batch-Status-Check"""
        if not self.app.ledger_adapter or self.check_in_progress:
            return

        self.check_in_progress = True

        # Run async check
        if self.app.async_loop:
            asyncio.ensure_future(self._do_batch_check(), loop=self.app.async_loop)

    async def _do_batch_check(self):
        """Asynchrone Batch-Check"""

        def on_progress(current, total):
            self.progress_bar.value = (current / total * 100) if total > 0 else 0

        try:
            results = await self.app.ledger_adapter.check_all_async(on_progress=on_progress)

            # Format results for display
            data = []
            for key, result in results.items():
                if "success" in result:
                    status_icon = STATUS_EMOJIS.get("ok", "✓")
                    text = f"{status_icon} {key[:30]} | {result.get('exp', '?')}"
                else:
                    status_icon = STATUS_EMOJIS.get("error", "✗")
                    text = f"{status_icon} {key[:30]} | ERROR"

                data.append(
                    {
                        "text": text,
                        "size_hint_y": None,
                        "height": dp(50),
                    }
                )

            self.status_list.data = data
        finally:
            self.check_in_progress = False

    def go_back(self):
        """Gehe zurück zum Hauptmenü"""
        self.app.screen_manager.current = "main"


class SettingsScreen(Screen):
    """Einstellungen Screen"""

    def __init__(self, app=None, **kwargs):
        super().__init__(**kwargs)
        self.app = app

        layout = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(10))

        # Dark Mode Toggle
        dark_mode_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        dark_mode_layout.add_widget(Label(text="🌙 Dark Mode", size_hint_x=0.7))
        dark_mode_switch = Switch(active=True, size_hint_x=0.3, size_hint_y=1)
        dark_mode_switch.bind(active=self.on_dark_mode_toggle)
        dark_mode_layout.add_widget(dark_mode_switch)
        layout.add_widget(dark_mode_layout)

        # About Section
        about_layout = BoxLayout(size_hint_y=0.3, orientation="vertical")
        about_layout.add_widget(Label(text="ℹ️ About", font_size=dp(16)))
        about_layout.add_widget(
            Label(
                text=f"{APP_NAME}\nv{APP_VERSION}\n\n© TheGermanGuy™\n\nAndroid + Desktop GUI",
                font_size=dp(12),
            )
        )
        layout.add_widget(about_layout)

        # Back Button
        layout.add_widget(Label(size_hint_y=0.4))
        layout.add_widget(Button(text="← Back", size_hint_y=0.1, on_press=lambda x: self.go_back()))

        self.add_widget(layout)

    def on_dark_mode_toggle(self, instance, value):
        """Dark Mode Toggle Callback"""
        theme.set_dark_mode(value)

    def go_back(self):
        """Gehe zurück zum Hauptmenü"""
        self.app.screen_manager.current = "main"


if __name__ == "__main__":
    app = M3uScanApp()
    app.run()
