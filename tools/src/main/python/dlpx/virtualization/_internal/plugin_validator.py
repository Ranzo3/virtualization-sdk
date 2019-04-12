#
# Copyright (c) 2019 by Delphix. All rights reserved.
#

import enum
import importlib
import json
import logging
import os
import sys

import jsonschema
import yaml
from dlpx.virtualization._internal import exceptions, file_util
from jsonschema.exceptions import ValidationError

logger = logging.getLogger(__name__)


class ValidationMode(enum.Enum):
    info = logging.info
    warning = logging.warn
    error = logging.error


class PluginValidator:
    def __init__(self,
                 plugin_config,
                 plugin_config_schema,
                 validation_mode,
                 plugin_config_content=None):
        self.__plugin_config = plugin_config
        self.__plugin_config_schema = plugin_config_schema
        self.__validation_mode = validation_mode
        self.__plugin_config_content = plugin_config_content
        self.__plugin_module_content = None
        self.__plugin_entry_point = None

    @property
    def plugin_config_content(self):
        return self.__plugin_config_content

    @property
    def plugin_module_content(self):
        return self.__plugin_module_content

    @property
    def plugin_entry_point(self):
        return self.__plugin_entry_point

    @classmethod
    def from_config_content(cls, plugin_config_file, plugin_config_content,
                            plugin_config_schema):
        return cls(plugin_config_file, plugin_config_schema,
                   ValidationMode.error, plugin_config_content)

    def validate(self):
        try:
            logger.debug("Run config validations")
            self.__run_validations()
        except Exception as e:
            if self.__validation_mode is ValidationMode.info:
                logger.info('Validation failed on plugin config file : %s', e)
            elif self.__validation_mode is ValidationMode.warning:
                logger.warning('Validation failed on plugin config file : %s',
                               e)
            else:
                raise e

    def __run_validations(self):
        logger.info('Reading plugin config file %s', self.__plugin_config)

        if self.__plugin_config_content is None:
            self.__plugin_config_content = self.__read_plugin_config_file()

        logger.debug('Validating plugin config file content : %s',
                     self.__plugin_config_content)
        self.__validate_plugin_config_content()

        src_dir = file_util.get_src_dir_path(
            self.__plugin_config, self.__plugin_config_content['srcDir'])

        logger.debug('Validating plugin entry point : %s',
                     self.__plugin_config_content['entryPoint'])
        self.__validate_plugin_entry_point(src_dir)

    def __read_plugin_config_file(self):
        try:
            with open(self.__plugin_config, 'rb') as f:
                try:
                    return yaml.safe_load(f)
                except yaml.YAMLError as err:
                    if hasattr(err, 'problem_mark'):
                        mark = err.problem_mark
                        raise exceptions.UserError(
                            'Command failed because the plugin config file '
                            'provided as input {!r} was not valid yaml. '
                            'Verify the file contents. '
                            'Error position: {}:{}'.format(
                                self.__plugin_config, mark.line + 1,
                                mark.column + 1))
        except IOError as err:
            raise exceptions.UserError(
                'Unable to read plugin config file {!r}'
                '\nError code: {}. Error message: {}'.format(
                    self.__plugin_config, err.errno, os.strerror(err.errno)))

    def __validate_plugin_config_content(self):
        """
        Validates the given plugin configuration is valid.

        The plugin configuration should include:
        name            the plugin name
        prettyName      the plugin's displayed name
        version         the plugin version
        hostTypes       the list of supported hostTypes (UNIX and/or WINDOWS)
        entryPoint      the entry point of the plugin defined by the decorator
        srcDir          the directory that the source code is writen in
        schemaFile:     the file containing defined schemas in the plugin
        manualDiscovery whether or not manual discovery is supported
        pluginType      whether the plugin is DIRECT or STAGED
        language        language of the source code(ex: PYTHON27 for python2.7)

        Args:
            plugin_config_content (dict): A dictionary representing a plugin
              configuration file.
        Raises:
            UserError: If the configuration is not valid.
            PathNotAbsoluteError: If the src and schema paths are not absolute.
        """
        # First validate that all the expected keys are in the plugin config.
        plugin_schema = {}
        try:
            with open(self.__plugin_config_schema, 'r') as f:
                try:
                    plugin_schema = json.load(f)
                except Exception as err:
                    raise exceptions.UserError(
                        'Failed to load schemas because {!r} is not a '
                        'valid json file. Error: {}'.format(
                            self.__plugin_config_schema, err))

        except IOError as err:
            raise exceptions.UserError(
                'Unable to read plugin config schema file {!r}'
                '\nError code: {}. Error message: {}'.format(
                    self.__plugin_config_schema, err.errno,
                    os.strerror(err.errno)))

        # Convert plugin config content to json
        plugin_config_json = json.loads(
            json.dumps(self.__plugin_config_content))

        # Validate the plugin config against the schema
        try:
            jsonschema.validate(instance=plugin_config_json,
                                schema=plugin_schema)
        except ValidationError as err:
            raise exceptions.UserError(
                'Validation failed on {}, Error message: {}'.format(
                    self.__plugin_config, err.message))

    def __validate_plugin_entry_point(self, src_dir):
        """
        Validates the plugin entry point by parsing the entry
        point to get module and entry point. Imports the module
        to check for errors or issues. Also does an eval on the
        entry point.
        """
        entry_point_field = self.__plugin_config_content['entryPoint']
        entry_point_strings = entry_point_field.split(':')

        # Get the module and entry point name to import
        module = entry_point_strings[0]
        self.__plugin_entry_point = entry_point_strings[1]

        if 'pytest' not in sys.modules:
            # Import the module to check if its good.
            self.__plugin_module_content = PluginValidator.__import_plugin(
                src_dir, module)

            # Check for the plugin entry point in the module.
            objects = dir(self.__plugin_module_content)

            if self.__plugin_entry_point not in objects:
                raise exceptions.UserError(
                    'Entry point \'{}\' provided in the plugin config '
                    'file is not found in module \'{}\'.'.format(
                        self.__plugin_entry_point, module))

    @staticmethod
    def __import_plugin(src_dir, module):
        sys.path.append(src_dir)
        module_content = importlib.import_module(module)
        return module_content
