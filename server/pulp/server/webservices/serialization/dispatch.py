# -*- coding: utf-8 -*-
#
# Copyright © 2012 Red Hat, Inc.
#
# This software is licensed to you under the GNU General Public
# License as published by the Free Software Foundation; either version
# 2 of the License (GPLv2) or (at your option) any later version.
# There is NO WARRANTY for this software, express or implied,
# including the implied warranties of MERCHANTABILITY,
# NON-INFRINGEMENT, or FITNESS FOR A PARTICULAR PURPOSE. You should
# have received a copy of GPLv2 along with this software; if not, see
# http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt.


def task_result_href(task):
    if task.get('task_id'):
        return {'_href': '/pulp/api/v2/tasks/%s/' % task['task_id']}
    return {}


def task_href(call_report):
    if call_report.call_request_id is None:
        return {}
    return {'_href': '/pulp/api/v2/tasks/%s/' % call_report.call_request_id}


def task_group_href(call_report):
    if call_report.call_request_group_id is None:
        return {}
    return {'_href': '/pulp/api/v2/task_groups/%s/' % call_report.call_request_group_id}


def scheduled_unit_management_obj(scheduled_call):
    scheduled_call['options'] = scheduled_call['kwargs']['options']
    scheduled_call['units'] = scheduled_call['kwargs']['units']
    return scheduled_call