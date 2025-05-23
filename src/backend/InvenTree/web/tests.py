"""Tests for web backend functionality."""

import json
import os
from pathlib import Path
from unittest import mock

from InvenTree.config import get_frontend_settings
from InvenTree.unit_test import InvenTreeTestCase

from .templatetags import spa_helper


class TemplateTagTest(InvenTreeTestCase):
    """Tests for the template tag code."""

    def assertSettings(self, settings_data):
        """Helper to test if needed args are in the settings."""
        self.assertIn('debug', settings_data)
        self.assertIn('server_list', settings_data)
        self.assertIn('show_server_selector', settings_data)
        self.assertIn('environment', settings_data)

    def test_spa_bundle(self):
        """Test the 'spa_bundle' template tag."""
        resp = spa_helper.spa_bundle()
        if resp == 'NOT_FOUND':
            # No Vite, no test
            return  # pragma: no cover

        shipped_js = resp.split('<script type="module" src="')[1:]
        self.assertGreater(len(shipped_js), 0)
        self.assertEqual(len(shipped_js), 3)

        manifest_file = Path(__file__).parent.joinpath('static/web/.vite/manifest.json')
        # Try with removed manifest file
        new_name = manifest_file.rename(
            manifest_file.with_suffix('.json.bak')
        )  # Rename
        resp = spa_helper.spa_bundle()
        self.assertEqual(resp, 'NOT_FOUND')

        # Try with differing name
        resp = spa_helper.spa_bundle(new_name)
        self.assertIsNotNone(resp)

        # Broken manifest file
        manifest_file.write_text('broken')
        resp = spa_helper.spa_bundle(manifest_file)
        self.assertEqual(resp, '')

        new_name.rename(manifest_file.with_suffix('.json'))  # Name back

    def test_spa_settings(self):
        """Test the 'spa_settings' template tag."""
        resp = spa_helper.spa_settings()
        self.assertTrue(resp.startswith('<script>window.INVENTREE_SETTINGS='))
        settings_data_string = resp.replace(
            '<script>window.INVENTREE_SETTINGS=', ''
        ).replace('</script>', '')
        settings_data = json.loads(settings_data_string)
        self.assertSettings(settings_data)

    def test_get_frontend_settings(self):
        """Test frontend settings retrieval."""
        # Normal run for priming
        rsp = get_frontend_settings()
        self.assertSettings(rsp)

        # No base_url
        envs = {'INVENTREE_FRONTEND_URL_BASE': ''}
        with mock.patch.dict(os.environ, envs):
            rsp = get_frontend_settings()
            self.assertSettings(rsp)

        # No debug, no serverlist -> selector
        rsp = get_frontend_settings(False)
        self.assertSettings(rsp)
        self.assertTrue(rsp['show_server_selector'])

        # No debug, serverlist -> no selector
        envs = {
            'INVENTREE_FRONTEND_SETTINGS': json.dumps({'server_list': ['aa', 'bb']})
        }
        with mock.patch.dict(os.environ, envs):
            rsp = get_frontend_settings(False)
            self.assertNotIn('show_server_selector', rsp)
            self.assertEqual(rsp['server_list'], ['aa', 'bb'])
