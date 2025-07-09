import asyncio
from repo_tool.tui.app import RepoToolApp


def test_settings_screen_opens():
    """
    Test that triggering the settings action in RepoToolApp opens the SettingsScreen.
    
    This test mocks keyring password storage with an in-memory dictionary, ensures the app always has valid tokens, runs the app in test mode, triggers the settings action, and asserts that the settings screen is displayed.
    """
    async def run_app():
        import keyring
        storage = {}
        keyring.set_password = lambda s, u, p: storage.__setitem__((s, u), p)
        keyring.get_password = lambda s, u: storage.get((s, u))
        keyring.delete_password = lambda s, u: storage.pop((s, u), None)

        app = RepoToolApp()
        app.token_manager.has_valid_tokens = lambda: True
        async with app.run_test() as pilot:
            app.action_settings()
            await pilot.pause(0.1)
            assert app.screen_stack[-1].__class__.__name__ == 'SettingsScreen'

    asyncio.run(run_app())

