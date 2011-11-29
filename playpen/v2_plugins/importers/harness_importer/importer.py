# -*- coding: utf-8 -*-
#
# Copyright © 2011 Red Hat, Inc.
#
# This software is licensed to you under the GNU General Public
# License as published by the Free Software Foundation; either version
# 2 of the License (GPLv2) or (at your option) any later version.
# There is NO WARRANTY for this software, express or implied,
# including the implied warranties of MERCHANTABILITY,
# NON-INFRINGEMENT, or FITNESS FOR A PARTICULAR PURPOSE. You should
# have received a copy of GPLv2 along with this software; if not, see
# http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt.

"""
Contains importer plugins and functionality for the Pulp plugin testing harness.
"""

import datetime
import logging
import os
import time

from pulp.server.content.plugins.importer import Importer
from pulp.server.content.plugins.model import SyncReport

# -- constants ----------------------------------------------------------------

# Until Pulp injects the logger, grab one from the Pulp namespace to use its
# file location
_LOG = logging.getLogger(__name__)
_LOG.addHandler(logging.FileHandler('/var/log/pulp/harness-importer.log'))

ACCEPTABLE_CONFIG_KEYS = ['num_units', 'write_files']

# -- plugins ------------------------------------------------------------------

class HarnessImporter(Importer):

    @classmethod
    def metadata(cls):
        return {
            'id'           : 'harness_importer',
            'display_name' : 'Test Harness Importer',
            'types'        : ['harness_type_one', 'harness_type_two']
        }

    def validate_config(self, repo, config):

        # Simply make sure that everything passed in the config is expected.
        # This lets the user simulate an invalid config by passing any other
        # key into the config.
        for key in config.repo_plugin_config:
            if key not in ACCEPTABLE_CONFIG_KEYS:
                return False
            if config.repo_plugin_config.get(key) is None:
                return False
        return True

    def importer_removed(self, repo, config):
        _LOG.info('Importer removed from repository [%s]' % repo.id)

        init_file = os.path.join(repo.working_dir, 'repo-initialized')
        os.remove(init_file)

    def importer_added(self, repo, config):
        _LOG.info('Importer added to repository [%s] with working directory [%s]' % (repo.id, repo.working_dir))

        init_file = os.path.join(repo.working_dir, 'repo-initialized')
        f = open(init_file, 'w')
        f.write('Repository ID: %s' % repo.id)
        f.close()

    def sync_repo(self, repo, sync_conduit, config):

        start = datetime.datetime.now()

        # Retrieve units already associated with the repository
        existing_units = sync_conduit.get_units()
        _LOG.info('Retrieved [%d] units from the server for repository [%s]' % (len(existing_units), repo.id))

        units_by_name = dict([(unit.unit_key['name'], unit) for unit in existing_units])

        # Add type 1 units
        num_units = int(config.get('num_units'))
        write_files = bool(config.get('write_files'))

        _LOG.info('Saving [%d] units of type "harness_type_one"' % num_units)
        if write_files:
            _LOG.info('Unit files will be written as part of the sync')
        else:
            _LOG.info('Importer configuration indicates to skip writing files')

        added_count = 0
        for i in range(0, num_units):
            # Collect unit metadata
            unit_key = {'name' : 'harness_unit_%d' % i}
            metadata = {'field_1' : 'value_%d' % i}
            relative_path = 'chunk_%d/%s.unit' % (i % 5, unit_key['name'])

            # Initialize the unit
            unit = sync_conduit.init_unit('harness_type_one', unit_key, metadata, relative_path)

            # Write the bits if configured to do so
            if write_files:
                f = open(unit.storage_path, 'w')
                f.write(unit_key['name'])
                f.close()

            # Save the unit in Pulp
            sync_conduit.save_unit(unit)

            # Update the counters for a fancy report
            if unit_key['name'] not in units_by_name:
                added_count += 1

        # Fake a slow sync if one is requested
        sync_delay_in_seconds = config.get('sync_delay', None)
        if sync_delay_in_seconds is not None:
            _LOG.info('Faking a long sync with delay of [%s] seconds' % sync_delay_in_seconds)
            time.sleep(int(sync_delay_in_seconds))

        end = datetime.datetime.now()
        ellapsed_in_seconds = (end - start).seconds

        return SyncReport(added_count, 0, 'Ellapsed time in seconds: %d' % ellapsed_in_seconds)
