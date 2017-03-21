# -*- coding: utf-8 -*-
##############################################################################
#
#    open2bizz
#    Copyright (C) 2016 open2bizz (open2bizz.nl).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

##############################################################################
from odoo import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)

class ProjectProjectTypeOrbeon(models.Model):
    _inherit = "project.type"
    
    orbeon_builder_form_ids = fields.Many2many(
        "orbeon.builder",
        string="Orbeon Builder Forms",
    )

class ProjectOrbeonProject(models.Model):
    _inherit = "project.project"

    orbeon_runner_form_ids = fields.One2many(
        "orbeon.runner",
        "project_id",
        string="Orbeon Runner Forms",
    )

    orbeon_runner_forms_count = fields.Integer(
        "Number of Orbeon Runner Forms",
        compute="_get_orbeon_runner_forms_count",
    )

    @api.one
    def _get_orbeon_runner_forms_count(self):
        self.orbeon_runner_forms_count = self.env["orbeon.runner"]\
                                             .search_count([("project_id","=",self.id)])

    @api.model
    def create(self, vals):
        res = super(ProjectOrbeonProject, self).create(vals)
        runner = self.env["orbeon.runner"]

        for builder in res.type_id.orbeon_builder_form_ids:
            runner_obj = runner.create({
                'builder_id': builder.id,
                'name': builder.name,
                'project_id': res.id,
            })
        
        return res

    @api.multi
    def action_project_orbeon_runner_forms(self, context=None, *args, **kwargs):
        tree_view = self.env["ir.ui.view"]\
                        .search([("name","=","orbeon.runner_form.tree")])[0]

        kanban_view = self.env["ir.ui.view"]\
                       .search([("name","=","orbeon.runner_form.kanban")])[0]

        runner_form_ids = [runner_form.id for runner_form in self.orbeon_runner_form_ids]
        name = self.name
        
        return {
            "name": _("Forms"),
            "type": "ir.actions.act_window",
            "res_model": "orbeon.runner",
            "view_type": "kanban",
            "view_mode": "kanban, tree",
            "views": [
                [kanban_view.id,"kanban"],
                [tree_view.id,"tree"],
            ],
            "target": "current",
            "domain": [("id","in",runner_form_ids)],
        }

class ProjectOrbeonOrbeonRunner(models.Model):
    _inherit = "orbeon.runner"

    project_id = fields.Many2one(
        "project.project",
        #string="Orbeon Runner Forms",
    )

# class project_orbeon_orbeon_builder(models.Model):
#     _inherit = "orbeon.builder"

#     # TODO update project-type linked builder-forms (state=current,obsolete
#     @api.multi
#     def write(self, vals):
#         if 'state' in vals and vals['state'] == 'current':
#             project_type = self.env["project.type"]