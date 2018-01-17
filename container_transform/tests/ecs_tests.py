from unittest import TestCase

from mock import patch
import uuid

from container_transform.ecs import ECSTransformer


class ECSTransformerTests(TestCase):
    """
    Tests for ECS Transformer
    """

    def setUp(self):
        self.file_name = './container_transform/tests/task.json'
        self.transformer = ECSTransformer(self.file_name)

    @patch.object(uuid, 'uuid4', return_value='2e9c3538-b9d3-4f47-8a23-2a19315b370b')
    def test_validate(self, mock_uuid):
        """
        Test .validate()
        """
        container = {
            'image': 'postgres:9.3',
            'cpu': 200,
            'memory': 40,
            'essential': True
        }

        validated = self.transformer.validate(container)
        self.assertEqual(
            validated['name'],
            mock_uuid.return_value
        )

    def test_ingest_cpu(self):
        cpu = 100
        self.assertEqual(
            self.transformer.ingest_cpu(cpu),
            cpu
        )

    def test_emit_cpu(self):
        cpu = 100
        self.assertEqual(
            self.transformer.emit_cpu(cpu),
            cpu
        )

    def test_command_list(self):
        """
        Test .ingest_command() should respect that list items are single command args
        Test .emit_command() should split correctly if an argument contains a space
        """
        command = [
            "/bin/echo",
            "Hello world"
        ]

        self.assertEqual(
            self.transformer.ingest_command(command),
            "/bin/echo 'Hello world'"
        )

        command = "/bin/echo 'Hello world'"

        self.assertEqual(
            self.transformer.emit_command(command),
            ["/bin/echo", "Hello world"]
        )

    def test_emit_essential(self):
        self.assertEqual(
            self.transformer.emit_essential('testing'),
            'testing')

    def test_emit_containers(self):
        """
        Test .emit_containers() output with and without a networkmode
        """
        containers = [{
            'image': 'postgres:9.3',
            'cpu': 200,
        }]

        # test with no networkmode
        output = self.transformer.emit_containers(containers)

        expected = (
            '{\n'
            '    "containerDefinitions": [\n'
            '        {\n'
            '            "cpu": 200,\n'
            '            "image": "postgres:9.3"\n'
            '        }\n'
            '    ],\n'
            '    "family": "pythonapp",\n'
            '    "volumes": []\n'
            '}'
        )
        self.assertEqual(
            expected,
            output
        )

        self.transformer.ecs_network_mode = 'awsvpc'
        output = self.transformer.emit_containers(containers)

        expected = (
            '{\n'
            '    "containerDefinitions": [\n'
            '        {\n'
            '            "cpu": 200,\n'
            '            "image": "postgres:9.3"\n'
            '        }\n'
            '    ],\n'
            '    "family": "pythonapp",\n'
            '    "networkMode": "awsvpc",\n'
            '    "volumes": []\n'
            '}'
        )

        self.assertEqual(
            expected,
            output
        )
