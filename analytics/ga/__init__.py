from .analytics import *

# body = {
#     'reportRequests': [
#         {
#             # The ID of your Analytics View. Cannot find it?
#             # Instructions below.
#             'viewId': '208498080',
#
#             'dateRanges': [
#                 {
#                     'startDate': yesterday,
#                     'endDate': _today,
#                 },
#             ],
#
#             'metrics': [
#                 # This is where you define the data you want
#                 # to receive. Link below. In this case I
#                 # want the sessions count and the conversion
#                 # rate
#                 # {'expression': 'ga:sessions'},
#                 # {'expression': 'ga:transactionsPerVisit'},
#
#                 {'expression': 'ga:newUsers'},
#                 # {'expression': 'ga:pageviews'},
#             ],
#             # 'dimensions': [
#             #     # Session attributes. We want to use our utm
#             #     # parameters, but you can also look for the
#             #     # user's country etc.
#             #     {'name': 'ga:medium'},
#             #     {'name': 'ga:source'},
#             # ],
#             # "dimensionFilterClauses": [
#             #     # Let's add some filters for the Facebook
#             #     # ad campaign
#             #     {
#             #         "filters": [
#             #             {
#             #                 "dimensionName": 'ga:medium',
#             #                 "operator": 'EXACT',
#             #                 "expressions": medium,
#             #             },
#             #             {
#             #                 "dimensionName": 'ga:source',
#             #                 "operator": 'EXACT',
#             #                 "expressions": source,
#             #             },
#             #         ],
#             #     }
#             # ],
#         }]
# }
