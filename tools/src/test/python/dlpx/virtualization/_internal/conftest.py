#
# Copyright (c) 2019 by Delphix. All rights reserved.
#

import copy
import json
import os

import pytest
import yaml
from dlpx.virtualization._internal import package_util

#
# conftest.py is used to share fixtures among multiple tests files. pytest will
# automatically get discovered in the test class if the figure name is used
# as the input variable. The idea of fixtures is to define certain object
# configs and allow them to get used in different tests but also being allowed
# to set certain parts definated in other fixtures. Read more at:
# https://docs.pytest.org/en/latest/fixture.html
#


@pytest.fixture
def plugin_config_file(tmpdir, plugin_config_filename, plugin_config_content):
    """
    This fixture creates a tempdir and writes the plugin_config_content to the
    file plugin_config_filename. Then it returns the full path of the file. If
    plugin_config_content is a dict we also want to create the full directory
    structure which includes the schema.json file and the src folder. Also
    it will do a yaml dump. If it's not a dict assume it's just a string and
     write that directly.
    """
    if isinstance(plugin_config_content, dict):
        plugin_config_content = yaml.dump(plugin_config_content,
                                          default_flow_style=False)

    f = tmpdir.join(plugin_config_filename)
    f.write(plugin_config_content)
    return f.strpath


@pytest.fixture
def plugin_config_filename():
    return 'plugin_config.yml'


@pytest.fixture
def src_dir(tmpdir, src_dirname):
    """
    This fixture creates a tempdir and makes a directory in it called
    src_dirname.
    """
    path = tmpdir.join(src_dirname).strpath
    os.mkdir(path)
    return path


@pytest.fixture
def src_dirname():
    return 'src'


@pytest.fixture
def schema_file(tmpdir, schema_filename, schema_content):
    """
    This fixture creates a tempdir and writes the schema.json file
    with the schema_content passed in via the fixture. Then it returns the
    path of the file. If artifact_content is a dict it will do a json dump,
    otherwise if it is just a string we'll write that directly.
    """
    if isinstance(schema_content, dict):
        schema_content = json.dumps(schema_content, indent=4)

    f = tmpdir.join(schema_filename)
    f.write(schema_content)
    return f.strpath


@pytest.fixture
def schema_filename():
    return 'schema.json'


@pytest.fixture
def artifact_file(tmpdir, artifact_content, artifact_filename,
                  artifact_file_created):
    """
    This fixture creates a tempdir and writes the artifact_filename file
    with the artifact_content passed in via the fixture. Then it returns the
    path of the file. If artifact_content is a dict it will do a json dump,
    otherwise if it is just a string we'll write that directly.
    """
    f = tmpdir.join(artifact_filename)
    if artifact_file_created:
        # Only write the artifact if we want to actually create it.
        if isinstance(artifact_content, dict):
            artifact_content = json.dumps(artifact_content, indent=4)
        f.write(artifact_content)
    return f.strpath


@pytest.fixture
def artifact_filename():
    return 'artifact.json'


@pytest.fixture
def artifact_file_created():
    return True


@pytest.fixture
def plugin_config_content(plugin_name, plugin_pretty_name, src_dir,
                          schema_file, language, manual_discovery):
    """
    This fixutre creates the dict expected in the properties yaml file the
    customer most provide for the build and compile commands.
    """
    config = {
        'version': '2.0.0',
        'hostTypes': 'UNIX',
        'entryPoint': 'python_vfiles:vfiles',
        'pluginType': 'DIRECT',
    }

    if plugin_name:
        config['name'] = plugin_name

    if plugin_pretty_name:
        config['prettyName'] = plugin_pretty_name

    if src_dir:
        config['srcDir'] = src_dir

    if schema_file:
        config['schemaFile'] = schema_file

    if language:
        config['language'] = language

    if manual_discovery:
        config['manualDiscovery'] = manual_discovery

    return config


@pytest.fixture
def plugin_name():
    return 'python_vfiles'


@pytest.fixture
def plugin_pretty_name():
    return 'Unstructured Files using Python'


@pytest.fixture
def language():
    return 'PYTHON27'


@pytest.fixture
def manual_discovery():
    return True


@pytest.fixture
def schema_content(repository_definition, source_config_definition,
                   virtual_source_definition, linked_source_definition,
                   snapshot_definition):

    schema = {}

    if repository_definition:
        schema['repositoryDefinition'] = repository_definition

    if source_config_definition:
        schema['sourceConfigDefinition'] = source_config_definition

    if virtual_source_definition:
        schema['virtualSourceDefinition'] = virtual_source_definition

    if linked_source_definition:
        schema['linkedSourceDefinition'] = linked_source_definition

    if snapshot_definition:
        schema['snapshotDefinition'] = snapshot_definition

    return schema


@pytest.fixture
def repository_definition():
    return {
        'type': 'object',
        'properties': {
            'name': {
                'type': 'string'
            }
        },
        'nameField': 'name',
        'identityFields': ['name']
    }


@pytest.fixture
def source_config_definition():
    return {
        'type': 'object',
        'required': ['name', 'path'],
        'additionalProperties': False,
        'properties': {
            'name': {
                'type': 'string'
            },
            'path': {
                'type': 'string'
            }
        },
        'nameField': 'name',
        'identityFields': ['path']
    }


@pytest.fixture
def virtual_source_definition():
    return {
        'type': 'object',
        'additionalProperties': False,
        'properties': {
            'path': {
                'type': 'string'
            }
        }
    }


@pytest.fixture
def linked_source_definition():
    return {'type': 'object', 'additionalProperties': False, 'properties': {}}


@pytest.fixture
def snapshot_definition():
    return {
        'type': 'object',
        'additionalProperties': False,
        'properties': {
            'snapshot_name': {
                'type': 'string'
            }
        }
    }


@pytest.fixture
def artifact_content(engine_api, virtual_source_definition,
                     linked_source_definition, discovery_definition,
                     snapshot_definition):
    """
    This fixture creates base artifact that was generated from build and
    used in upload. If any fields besides engine_api needs to be changed,
    add fixtures below and add the function name to be part of the input to
    this function.
    """
    artifact = {
        'type': 'Toolkit',
        'name': 'python_vfiles',
        'prettyName': 'Unstructured Files using Python',
        'version': '2.0.0',
        'defaultLocale': 'en-us',
        'language': 'PYTHON27',
        'hostTypes': 'UNIX',
        'entryPoint': 'python_vfiles:vfiles',
        'buildApi': package_util.get_build_api_version(),
        'sourceCode': 'UEsFBgAAAAAAAAAAAAAAAAAAAAAAAA==',
        'resources': {}
    }

    if engine_api:
        artifact['engineApi'] = engine_api

    if virtual_source_definition:
        artifact['virtualSourceDefinition'] = {
            'type': 'ToolkitVirtualSource',
            'parameters': virtual_source_definition,
            'configure': '',
            'unconfigure': '',
            'reconfigure': '',
            'initialize': '',
            'start': '',
            'stop': '',
            'preSnapshot': '',
            'postSnapshot': ''
        }

    if linked_source_definition:
        artifact['linkedSourceDefinition'] = {
            'type': 'ToolkitLinkedDirectSource',
            'parameters': linked_source_definition,
            'preSnapshot': '',
            'postSnapshot': '',
        }

    if discovery_definition:
        artifact['discoveryDefinition'] = discovery_definition

    if snapshot_definition:
        artifact['snapshotSchema'] = snapshot_definition

    return artifact


@pytest.fixture
def engine_api():
    return {'type': 'APIVersion', 'major': 1, 'minor': 10, 'micro': 4}


@pytest.fixture
def discovery_definition(repository_definition, source_config_definition,
                         manual_discovery):
    discovery_definition = {
        'type': 'ToolkitDiscoveryDefinition',
        'sourceConfigDiscovery': '',
        'repositoryDiscovery': ''
    }

    if manual_discovery:
        discovery_definition['manualSourceConfigDiscovery'] = manual_discovery

    if repository_definition:
        old_repository_def = copy.deepcopy(repository_definition)
        repo_id_fields = old_repository_def.pop('identityFields', None)
        repo_name_field = old_repository_def.pop('nameField', None)

        if repo_id_fields:
            discovery_definition['repositoryIdentityFields'] = repo_id_fields
        if repo_name_field:
            discovery_definition['repositoryNameField'] = repo_name_field
        discovery_definition['repositorySchema'] = old_repository_def

    if source_config_definition:
        old_source_config_def = copy.deepcopy(source_config_definition)
        scf_id_fields = old_source_config_def.pop('identityFields', None)
        scf_name_field = old_source_config_def.pop('nameField', None)

        if scf_id_fields:
            discovery_definition['sourceConfigIdentityFields'] = scf_id_fields
        if scf_name_field:
            discovery_definition['sourceConfigNameField'] = scf_name_field
        discovery_definition['sourceConfigSchema'] = old_source_config_def

    return discovery_definition


@pytest.fixture
def codegen_gen_py_inputs(plugin_config_file, plugin_pretty_name, src_dir,
                          tmpdir, schema_content):
    class CodegenInput:
        def __init__(self, name, source_dir, plugin_content_dir, schema_dict):
            self.name = name
            self.source_dir = source_dir
            self.plugin_content_dir = plugin_content_dir
            self.schema_dict = schema_dict

    return CodegenInput(plugin_pretty_name, src_dir, tmpdir.strpath,
                        schema_content)
