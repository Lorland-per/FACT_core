from helperFunctions.data_conversion import make_bytes
from test.common_helper import TEST_FW, TEST_FW_2, TEST_TEXT_FILE  # pylint: disable=wrong-import-order
from test.unit.web_interface.base import WebInterfaceTest  # pylint: disable=wrong-import-order


class TestAppShowAnalysis(WebInterfaceTest):

    def test_app_show_analysis_get_valid_fw(self):
        result = self.test_client.get('/analysis/{}'.format(TEST_FW.uid)).data
        assert b'<strong>UID:</strong> ' + make_bytes(TEST_FW.uid) in result
        assert b'data-toggle="tooltip" title="mandatory plugin description"' in result
        assert b'data-toggle="tooltip" title="optional plugin description"' in result

        # check release date not available
        assert b'1970-01-01' not in result
        assert b'unknown' in result

        result = self.test_client.get('/analysis/{}'.format(TEST_FW_2.uid)).data
        assert b'unknown' not in result
        assert b'2000-01-01' in result

    def test_app_show_analysis_file_with_preview(self):
        result = self.test_client.get('/analysis/{}'.format(TEST_TEXT_FILE.uid)).data
        assert b'<strong>UID:</strong> ' + make_bytes(TEST_TEXT_FILE.uid) in result
        assert b'Preview' in result
        assert b'test file:\ncontent:'

    def test_app_single_file_analysis(self):
        result = self.test_client.get('/analysis/{}'.format(TEST_FW.uid))

        assert b'Add new analysis' in result.data
        assert b'Update analysis' in result.data

        assert not self.mocked_interface.tasks
        post_new = self.test_client.post('/analysis/{}'.format(TEST_FW.uid), content_type='multipart/form-data', data={'analysis_systems': ['plugin_a', 'plugin_b']})

        assert post_new.status_code == 302
        assert self.mocked_interface.tasks
        assert self.mocked_interface.tasks[0].scheduled_analysis == ['plugin_a', 'plugin_b']

    def test_app_dependency_graph(self):
        result = self.test_client.get('/dependency-graph/{}'.format('testgraph'))
        assert b'<strong>UID:</strong> testgraph' in result.data
        assert b'Error: Graph could not be rendered. The file chosen as root must contain a filesystem with binaries.' not in result.data
        assert b'Warning: Elf analysis plugin result is missing for 1 files' in result.data
        result_error = self.test_client.get('/dependency-graph/{}'.format('1234567'))
        assert b'Error: Graph could not be rendered. The file chosen as root must contain a filesystem with binaries.' in result_error.data
