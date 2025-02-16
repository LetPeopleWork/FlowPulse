from ..WorkItem import WorkItem
import requests
from datetime import datetime


class JiraWorkItemService:

    in_progress_status_categories = ["In Progress", "Done"]

    def __init__(
        self, jira_url, username, api_token, estimation_field, anonymize_label, jql_string
    ):
        self.jira_url = jira_url
        self.username = username
        self.api_token = api_token
        self.estimation_field = estimation_field
        self.anonymize_label = anonymize_label
        self.jql_string = jql_string

        # Set up auth based on token type
        if username:
            self.auth = (username, api_token)
            self.headers = {}
        else:
            # If no username, treat api_token as personal access token
            self.auth = None
            self.headers = {"Authorization": f"Bearer {api_token}"}

        self.status_category_map = self.get_status_categories()

    def fetch_issues(self, jql, fields, max_results=100, expand=None):
        start_at = 0
        all_issues = []

        query_url = f"{self.jira_url}/rest/api/latest/search"
        print(f"Fetching Issues from {query_url}")

        while True:
            params = {
                "jql": jql,
                "startAt": start_at,
                "maxResults": max_results,
                "fields": fields,
            }

            if expand:
                params["expand"] = expand

            response = requests.get(query_url, headers=self.headers, auth=self.auth, params=params)
            response.raise_for_status()
            data = response.json()

            issues = data.get("issues", [])
            all_issues.extend(issues)

            if start_at + max_results >= data["total"]:
                break

            start_at += max_results

        return all_issues

    def get_items(self, items_query=None):
        work_items = []
        if not items_query:
            items_query = self.jql_string

        jql = f"{items_query}"
        print(f"Executing following query: {jql}")

        fields = "id,key,summary,resolutiondate,created,status," + self.estimation_field
        issues = self.fetch_issues(jql, fields, expand="changelog")

        for issue in issues:
            work_item = self.convert_to_work_item(issue)

            work_items.append(work_item)

        return work_items

    def convert_to_work_item(self, issue):
        issue_key = issue["key"]

        if self.anonymize_label:
            issue_key = self.anonymize_issue_key(issue_key)

        fields = issue["fields"]

        title = fields.get("summary", "")
        closed_date = fields.get("resolutiondate", None)
        estimation = fields.get(self.estimation_field, 0)

        if estimation is None:
            estimation = 0

        if closed_date is not None:
            closed_date = self.parse_date(closed_date)

        activated_date = None
        status = fields.get("status", None)
        if status:
            status_name = status["statusCategory"]["name"]
            if status_name in self.in_progress_status_categories:
                activated_date = self.get_activated_date(issue)

                if activated_date:
                    activated_date = self.parse_date(activated_date)

        return WorkItem(issue_key, title, activated_date, closed_date, estimation)

    def get_activated_date(self, issue):
        # Iterate over changelog histories to find the first transition to 'In Progress' category
        for history in issue["changelog"]["histories"]:
            for item in history["items"]:
                if item["field"] == "status":
                    to_status = item["toString"]

                    if self.status_category_map.get(to_status) == "indeterminate":
                        activated_date = history["created"]
                        return activated_date

        return None

    def parse_date(self, date):
        try:
            # Strip the timezone offset and parse as naive datetime
            date_str = date[:-5]
            date_format = "%Y-%m-%dT%H:%M:%S.%f"
            return datetime.strptime(date_str, date_format)
        except ValueError:
            return None

    def get_status_categories(self):
        request_url = f"{self.jira_url}/rest/api/2/status"
        response = requests.get(request_url, auth=self.auth, headers=self.headers)
        response.raise_for_status()
        return {status["name"]: status["statusCategory"]["key"] for status in response.json()}

    def anonymize_issue_key(self, issue_key):
        parts = issue_key.split("-")
        return parts[-1] if len(parts) > 1 else issue_key
