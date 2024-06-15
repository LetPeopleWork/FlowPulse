from .WorkItem import WorkItem
import requests
from datetime import datetime, timedelta
import pytz

class JiraWorkItemService:    
    
    def __init__(self, jira_url, username, api_token, estimation_field, backlog_history):
        self.jira_url = jira_url
        self.username = username
        self.api_token = api_token
        self.estimation_field = estimation_field
        self.backlog_history = backlog_history
        self.auth = (username, api_token)
        
        starting_date = (datetime.now(pytz.utc) - timedelta(backlog_history)).strftime("%Y-%m-%d")
        self.starting_date_statement = f'AND updated >= "{starting_date}"'
    
    def get_items_via_query(self, jql_string):
        work_items = []
        
        jql = f'{jql_string} {self.starting_date_statement}'
        print(f'Executing following query: {jql}')
        
        query_url = f'{self.jira_url}/rest/api/2/search'
        params = {
            'jql': jql,
            'fields': 'id,key,summary,updated,created,' + self.estimation_field
        }
        
        response = requests.get(query_url, params=params, auth=self.auth)
        response.raise_for_status()
        
        issues = response.json().get('issues', [])
        
        for issue in issues:
            work_item = self.convert_to_work_item(issue)
            work_items.append(work_item)
        
        return work_items    

    def convert_to_work_item(self, issue):
        fields = issue['fields']
        
        title = fields.get('summary', '')
        closed_date = fields.get('updated', '')
        activated_date = fields.get('created', '')
        estimation = fields.get(self.estimation_field, 0)
        
        return WorkItem(issue['id'], title, activated_date, closed_date, estimation)