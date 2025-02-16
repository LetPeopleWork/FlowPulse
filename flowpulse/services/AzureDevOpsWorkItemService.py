from ..WorkItem import WorkItem
from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication
from azure.devops.v7_1.work_item_tracking.models import Wiql

from datetime import datetime


class AzureDevOpsWorkItemService:

    def __init__(self, org_url, token, estimation_field, wiql_string):
        credentials = BasicAuthentication("", token)

        self.organization_url = org_url
        self.personal_access_token = token

        self.estimation_field = estimation_field

        self.header_patch = {"Content-Type": "application/json-patch+json"}

        self.connection = Connection(base_url=org_url, creds=credentials)
        self.wit_client = self.connection.clients.get_work_item_tracking_client()
        self.wiql_string = wiql_string

    def get_items(self, items_query=None):
        work_items = []
        if not items_query:
            items_query = self.wiql_string

        wiql = Wiql(
            query="""
                select [System.Id],
                    [System.Title],
                    [Microsoft.VSTS.Common.ClosedDate],
                    [Microsoft.VSTS.Common.ActivatedDate],
                    [{0}]
                from WorkItems
                where {1}""".format(
                self.estimation_field, items_query
            )
        )

        print("Executing following query: {0}".format(wiql.query))

        wiql_results = self.wit_client.query_by_wiql(wiql).work_items

        if wiql_results:
            query_results = (
                self.wit_client.get_work_item(int(res.id), expand="Relations")
                for res in wiql_results
            )
            for result in query_results:
                work_item = self.convert_to_work_item(result)
                work_items.append(work_item)

        return work_items

    def convert_to_work_item(self, wiql_result):
        title = ""
        if "System.Title" in wiql_result.fields:
            title = wiql_result.fields["System.Title"]

        closed_date = ""
        if "Microsoft.VSTS.Common.ClosedDate" in wiql_result.fields:
            closed_date = wiql_result.fields["Microsoft.VSTS.Common.ClosedDate"]

        activated_date = ""
        if "Microsoft.VSTS.Common.ActivatedDate" in wiql_result.fields:
            activated_date = wiql_result.fields["Microsoft.VSTS.Common.ActivatedDate"]

        estimation = 0
        if self.estimation_field in wiql_result.fields:
            estimation = wiql_result.fields[self.estimation_field]

        activated_date = self.parse_date(activated_date)
        closed_date = self.parse_date(closed_date)

        return WorkItem(wiql_result.id, title, activated_date, closed_date, estimation)

    def parse_date(self, date):
        if not date:
            return None

        try:
            return datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ")
        except ValueError:
            try:
                return datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ")
            except ValueError:
                return None
