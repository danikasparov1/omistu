from odoo import models, fields, api
import logging
import json

_logger = logging.getLogger(__name__)

class ProjectTaskGitlabEvent(models.Model):
    _name = 'project.task.gitlab'
    _rec_name = 'reference'
    reference = fields.Char(default=lambda self: self.env['ir.sequence'].next_by_code('project.task.gitlab.reference'))
    sub_task_id = fields.Many2one('project.task', string="Subtask")
    gitlab_event_id = fields.Char(string="GitLab Event ID", )
    gitlab_event_type = fields.Selection([
        ('push', 'Push'),
        ('pipeline', 'Pipeline'),
        ('merge_request', 'Merge Request'),
    ], string="Event Type", )
    commit_message = fields.Char(string="Commit Message")
    gitlab_event_data = fields.Text(string="Event Data", )
    gitlab_project = fields.Char(string="GitLab Repo Name")
    partner = fields.Many2one('res.partner', string="Developer")
    
class ProjectTask(models.Model):
    _inherit = 'project.task'
    # Many2one field to link back to the GitLab event
    code = fields.Char(string="Code",help="This is when you push the first commit message part must be and must be separated with space it is like .split()[0] from your commit message")
    gitlab_event_id = fields.One2many('project.task.gitlab', 'sub_task_id',string="GitLab Event", ondelete='set null')
    gitlab_event_count = fields.Integer(string="Number of GitLab Events", compute="get_gitlab_events_count", store=True)
    
    def get_gitlab_events_count(self):
        # This method will return the count of related GitLab events
        for record in self:
            record.gitlab_event_count = len(record.gitlab_event_id)
    def action_open_commits(self):
        # This function will be triggered when the button is clicked
        return {
            'type': 'ir.actions.act_window',
            'name': 'GitLab Events',
            'res_model': 'project.task.gitlab',
            'view_mode': 'tree',  # List view mode
            'domain': [('sub_task_id', '=', self.id)],  # Filter the records based on the sub_task_id
            'target': 'current',  # Opens in the current window
        }
