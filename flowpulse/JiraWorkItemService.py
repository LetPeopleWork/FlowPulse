from .WorkItem import WorkItem
import requests
from datetime import datetime, timedelta
import pytz

class JiraWorkItemService:    
    
    in_progress_status_categories = ["In Progress", "Done"]
    
    def __init__(self, jira_url, username, api_token, estimation_field, backlog_history):
        self.jira_url = jira_url
        self.username = username
        self.api_token = api_token
        self.estimation_field = estimation_field
        self.backlog_history = backlog_history
        self.auth = (username, api_token)
        
        starting_date = (datetime.now(pytz.utc) - timedelta(backlog_history)).strftime("%Y-%m-%d")
        self.starting_date_statement = f'AND updated >= "{starting_date}"'
        
        self.status_category_map = self.get_status_categories()

    def fetch_issues(self, jql, fields, max_results=100, expand=None):
        start_at = 0
        all_issues = []
        
        query_url = f'{self.jira_url}/rest/api/2/search'
        print(f"Fetching Issues from {query_url}")

        while True:
            params = {
                'jql': jql,
                'startAt': start_at,
                'maxResults': max_results,
                'fields': fields,
            }
            
            if expand:
                params['expand'] = expand
            
            response = requests.get(
                query_url,
                auth=self.auth,
                params=params
            )
            response.raise_for_status()
            data = response.json()
            
            issues = data.get('issues', [])
            all_issues.extend(issues)

            if start_at + max_results >= data['total']:
                break
            
            start_at += max_results

        return all_issues
    
    def get_items_via_query(self, jql_string):
        work_items = []
        
        jql = f'{jql_string} {self.starting_date_statement} AND statusCategory in ("In Progress", "Done")'
        print(f'Executing following query: {jql}')
        
        fields = 'id,key,summary,resolutiondate,created,status,' + self.estimation_field
        issues = self.fetch_issues(jql, fields, expand="changelog")
        
        for issue in issues:
            work_item = self.convert_to_work_item(issue)
            work_items.append(work_item)
        
        return work_items

    def convert_to_work_item(self, issue):        
        issue_key = issue['key']
        fields = issue['fields']        
        
        title = fields.get('summary', '')
        closed_date = fields.get('resolutiondate', None)
        estimation = fields.get(self.estimation_field, 0)
        
        if estimation is None:
            estimation = 0
            
        if closed_date is not None:
            closed_date = self.parse_date(closed_date)
        
        activated_date = None
        status = fields.get('status', None)
        if status:
            status_name = status['statusCategory']['name']
            if status_name in self.in_progress_status_categories:
                activated_date = self.get_activated_date(issue)
        
                if activated_date:
                    activated_date = self.parse_date(activated_date)
        
        return WorkItem(issue_key, title, activated_date, closed_date, estimation)
    
    def get_activated_date(self, issue):
        # Iterate over changelog histories to find the first transition to 'In Progress' category
        for history in issue['changelog']['histories']:
            for item in history['items']:
                if item['field'] == 'status':
                    to_status = item['toString']
                    
                    if self.status_category_map.get(to_status) == 'indeterminate':
                        activated_date = history['created']
                        return activated_date
        
        return None
        
    def parse_date(self, date):
        try:
            # Strip the timezone offset and parse as naive datetime
            date_str = date[:-5]
            date_format = '%Y-%m-%dT%H:%M:%S.%f'
            return datetime.strptime(date_str, date_format)
        except ValueError:
            return None
        
    def get_status_categories(self):
        request_url = f'{self.jira_url}/rest/api/3/status'
        response = requests.get(request_url, auth=self.auth)
        response.raise_for_status()
        return {status['name']: status['statusCategory']['key'] for status in response.json()}