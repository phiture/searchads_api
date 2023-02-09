import datetime
import time

import jwt
import requests


class SearchAdsAPI:
    def __init__(
        self,
        org_id,
        pem,
        key,
        client_id=None,
        team_id=None,
        key_id=None,
        certificates_dir_path="certs/",
        api_version="v4",
        session=None,
        verbose=False,
    ):
        """
        Init API instance
        """
        self.org_id = org_id
        self.pem = pem
        self.key = key
        self.session = session
        self.path = certificates_dir_path
        self.verbose = verbose
        if key_id is None:
            self.api_version = "v3"
        else:
            self.api_version = api_version
        self.client_id = client_id
        self.team_id = team_id
        self.key_id = key_id
        self.access_token = None

    def get_access_token_from_client_secret(self, key):
        if self.access_token is None:
            audience = "https://appleid.apple.com"
            alg = "ES256"
            # Define issue timestamp.
            issued_at_timestamp = int(datetime.datetime.utcnow().timestamp())
            # Define expiration timestamp. May not exceed 180 days from issue timestamp.
            expiration_timestamp = issued_at_timestamp + 86400 * 180

            # Define JWT headers.
            headers = dict()
            headers["alg"] = alg
            headers["kid"] = self.key_id

            # Define JWT payload.
            payload = dict()
            payload["sub"] = self.client_id
            payload["aud"] = audience
            payload["iat"] = issued_at_timestamp
            payload["exp"] = expiration_timestamp
            payload["iss"] = self.team_id

            # Path to signed private key.
            KEY_FILE = key

            with open(KEY_FILE, "r") as key_file:
                key = "".join(key_file.readlines())

            client_secret = jwt.encode(
                payload=payload, headers=headers, algorithm=alg, key=key
            )
            # with open(f'{KEY_FILE}.txt', 'w') as output:
            #     output.write(client_secret.decode("utf-8"))
            result = requests.post(
                "https://appleid.apple.com/auth/oauth2/token",
                data={
                    "grant_type": "client_credentials",
                    "client_id": self.client_id,
                    "client_secret": client_secret,
                    "scope": "searchadsorg",
                },
                headers={
                    "Host": "appleid.apple.com",
                    "Content-Type": "application/x-www-form-urlencoded",
                },
            )

            # return client_secret
            result_json = result.json()
            if self.verbose:
                print(result_json)
            access_token = result_json["access_token"]
            # set global access token
            self.access_token = access_token
        else:
            # get global access_token
            access_token = self.access_token
        if self.verbose:
            print(access_token)
        return access_token

    # API Function

    def api_call(
        self,
        api_endpoint="",
        headers={},
        json_data={},
        params={},
        method="GET",
        limit=1000,
        offset=0,
    ):
        """
        Generic API call function
        """
        url = "https://api.searchads.apple.com/api/{}"
        # choose between using a proxy or the public ip
        if self.session is None:
            caller = requests
        else:
            caller = self.session
        # find the certicates path
        pem = self.path + self.pem
        key = self.path + self.key

        kwargs = {
            "headers": headers,
        }
        # if v3 is being used
        if self.client_id is None:
            kwargs["cert"] = (pem, key)
        if json_data:
            kwargs["json"] = json_data
        kwargs["params"] = dict()
        # add the limit if it applies
        if limit:
            kwargs["params"]["limit"] = limit
        # add the offset
        if offset:
            kwargs["params"]["offset"] = offset
        # add the org_id header in v3
        if self.org_id:
            kwargs["headers"]["Authorization"] = f"orgId={self.org_id}"
        # only if using Search Ads API v4
        if self.key_id is not None and self.api_version == "v4":
            access_token = self.get_access_token_from_client_secret(key)
            kwargs["headers"]["Authorization"] = f"Bearer {access_token}"
            kwargs["headers"]["X-AP-Context"] = f"orgId={self.org_id}"
        kwargs["params"].update(params)
        api_endpoint = "{}/{}".format(self.api_version, api_endpoint)
        url = url.format(api_endpoint)
        if method == "get" or method == "GET":
            req = caller.get(url, **kwargs)
        elif method == "post" or method == "POST":
            req = caller.post(url, **kwargs)
        elif method == "put" or method == "PUT":
            req = caller.put(url, **kwargs)
        elif method == "delete" or method == "DELETE":
            req = caller.delete(url, **kwargs)
        if (
            req.status_code == 401 or "Expired Token:" in req.text
        ) and self.api_version == "v4":
            print("Update the token due to expiration")
            # make it none
            self.access_token = None
            # Get a new token
            access_token = self.get_access_token_from_client_secret(key)
            # echo new token
            print(access_token)

        if self.verbose:
            print(req.status_code)
            print(req.url)
            print(req.text)
        resp = req.json()
        # raise an error 
        if resp.get("error") is not None:
            raise Exception(resp["error"])
        return resp

    # Campaign Methods

    def create_campaign(
        self, app_id, countries, campaign_name, budget, daily_budget, curruncy
    ):
        """
        Creates a campaign to promote an app.
        """
        data = {
            "orgId": self.org_id,
            "name": campaign_name,
            "budgetAmount": {"amount": "{}".format(budget), "currency": curruncy},
            "dailyBudgetAmount": {
                "amount": "{}".format(daily_budget),
                "currency": curruncy,
            },
            "adamId": app_id,
            "countriesOrRegions": countries,
        }
        res = self.api_call("campaigns", json_data=data, method="POST")
        return res

    def find_campaigns(
        self,
        sort_field="id",
        sort_order="ASCENDING",
        conditions=[],
        limit=1000,
        offset=0,
    ):
        """
        Finds campaigns.
        Example condition:
        {"field": "countriesOrRegions","operator": "CONTAINS_ALL","values": ["US", "CA"]}
        """
        data = {
            "pagination": {"offset": offset, "limit": limit},
            "orderBy": [{"field": sort_field, "sortOrder": sort_order}],
            "conditions": conditions,
        }
        res = self.api_call("campaigns/find", json_data=data, method="POST")
        return res

    def get_campaign(self, campaign_id):
        """
        Returns a campaign according to a campaignId .
        """
        res = self.api_call("campaigns/{}".format(campaign_id), method="GET")["data"]
        return res

    def get_campaigns(self, limit=0, offset=0):
        """
        Returns all campaigns for an org. Use limit 0 to get all campaigns.
        {
            "orgId": 0000000,
            "name": "name",
            "budgetAmount": {
            "amount": "2000",
            "currency": "USD"
        },
            "dailyBudgetAmount": {
            "amount": "300",
            "currency": "USD"
        },
            "adamId": 00000000,
            "countriesOrRegions": ["US","AU"]
        }
        """
        res = []
        result = None
        retries = 0
        if limit == 0:
            li = 1000
        else:
            li = limit
        while True:
            result = self.api_call("campaigns", method="GET", offset=offset, limit=li)
            if result is None or result["data"] is None:
                retries += 1
                if retries > 3:
                    break
                else:
                    time.sleep(0.5)
                    continue
            res.extend(result["data"])
            res_len = len(res)
            if res_len == limit or result["pagination"]["totalResults"] == res_len:
                break
            # print(result["pagination"], len(result["data"]))
            offset += result["pagination"]["itemsPerPage"]
        return res

    def update_campaign(
        self,
        campaign_id,
        countries=None,
        campaign_name=None,
        budget=None,
        daily_budget=None,
        curruncy=None,
        status=None,
        adamId=None,
    ):
        """
        Updates a campaign by campaign identifier.
        {
            "campaign": {
                "countriesOrRegions": [
                                        "US",
                                        "CA",
                                        "UK",
                                        "AU",
                                        ]
            }
        }
        """
        edit = {}
        if countries:
            edit["countriesOrRegions"] = countries
        if campaign_name:
            edit["name"] = campaign_name
        if budget:
            edit["budgetAmount"] = {"amount": "{}".format(budget), "currency": curruncy}
        if daily_budget:
            edit["dailyBudgetAmount"] = {
                "amount": "{}".format(daily_budget),
                "currency": curruncy,
            }
        if campaign_name:
            edit["name"] = campaign_name
        if campaign_name:
            edit["status"] = campaign_name
        if edit["adamId"]:
            edit["adamId"] = adamId
        if edit["status"]:
            edit["status"] = status
        data = {"campaign": edit}
        res = self.api_call(
            api_endpoint="campaigns/{}".format(campaign_id),
            json_data=data,
            method="PUT",
        )
        return res

    def delete_campaign(self, campaign_id):
        """
        Deletes a specific campaign using the campaign identifier.
        """
        res = self.api_call("campaigns/{}".format(campaign_id), method="DELETE")
        return res

    # Budget order methods

    def get_budget_order(self, boId):
        """
        Fetches a specific budget order using a budget order identifier.
        """
        res = self.api_call(f"budgetorders/{boId}", method="GET")["data"]
        return res

    def get_all_budget_orders(self):
        """
        Fetches all assigned budget orders for an organization.
        """
        res = self.api_call(f"budgetorders", method="GET")["data"]
        return res

    # Adgroup Methods

    def create_adgroup(
        self,
        campaign_id,
        adgroup_name,
        currency,
        cpc_bid,
        start_time,
        end_time=None,
        cpa_goal=None,
        automated_keywords_opt_in=False,
        age=None,
        gender=None,
        device_class=None,
        day_part=None,
        adminArea=None,
        locality=None,
        appDownloaders=None,
    ):
        """
         Creates an ad group as part of a campaign.
         {
        "id": <id>,
         "campaignId": <campaignId>,
         "name": "<name>",
         "cpaGoal": {
             "amount": "100",
             "currency": "USD"
         },
         "startTime": "2019-05-28T10:33:31.650",
         "endTime": "2019-05-31T10:33:31.650",
         "automatedKeywordsOptIn": true,
         "defaultCpcBid": {
             "amount": "100",
             "currency": "USD"
         },
         "targetingDimensions": {
             "age": {
                 "included": [
                     {
                         "minAge": 20,
                         "maxAge": 25
                     }
                 ]
             },
             "gender": {
                 "included": [
                     "M"
                 ]
             },

             "deviceClass": {
                 "included": [
                     "IPAD",
                     "IPHONE"
                 ]
             },
             "daypart": {
                 "userTime": {
                     "included": [
                         1,
                         3,
                         22,
                         24
                     ]
                 }
             },
             "appDownloaders": {
                 "included": [],
                 "excluded": ["<adamid>"]
             }
         },
         "orgId": <orgId>,
         "modificationTime": "2019-05-23T23:26:09.824",
         "status": "ENABLED",
         "servingStatus": "NOT_RUNNING",
         "servingStateReasons": [
             "START_DATE_IN_THE_FUTURE",
             "PENDING_AUDIENCE_VERIFICATION"
                 ],
                 "displayStatus": "ON_HOLD",
                 "deleted": false
             },
             "pagination": null,
             "error": null
         }
        """
        dimensions = {}
        if (
            gender is not None
            or device_class is not None
            or day_part is not None
            or adminArea is not None
            or locality is not None
            or appDownloaders is not None
        ):
            dimensions = {
                "age": {"included": age},
                "gender": {"included": gender},
                "deviceClass": {"included": device_class},
                "daypart": {"userTime": {"included": day_part}},
                "adminArea": {"included": adminArea},
                "locality": {"included": locality},
                "appDownloaders": appDownloaders,
            }

        data = {
            "campaignId": campaign_id,
            "name": adgroup_name,
            "automatedKeywordsOptIn": automated_keywords_opt_in,
            "defaultCpcBid": {"amount": "{}".format(cpc_bid), "currency": currency},
            "targetingDimensions": dimensions,
            "orgId": self.org_id,
        }
        if cpa_goal is not None:
            data["cpaGoal"] = {"amount": "{}".format(cpa_goal), "currency": currency}
        if start_time is not None:
            data["startTime"] = start_time.strftime("%Y-%m-%dT%H:%M:%S.%f")
        if end_time is not None:
            data["endTime"] = end_time.strftime("%Y-%m-%dT%H:%M:%S.%f")
        res = self.api_call(
            "campaigns/{}/adgroups".format(campaign_id), json_data=data, method="POST"
        )
        return res

    def find_adgroups(
        self,
        campaign_id,
        conditions=[],
        fields=[],
        sort_field="id",
        sort_order="ASCENDING",
        limit=1000,
        offset=0,
    ):
        """
        Fetches ad groups within a campaign.

        """
        data = {
            "fields": fields,
            "pagination": {"offset": offset, "limit": limit},
            "orderBy": [{"field": sort_field, "sortOrder": sort_order}],
            "conditions": conditions,
        }
        res = self.api_call(
            "campaigns/{}/adgroups/find".format(campaign_id),
            json_data=data,
            method="POST",
        )
        return res

    def get_adgroups(self, campaign_id, limit=0, offset=0):
        """
        Returns all adGroups for a specified campaign.
        Optional pagination specifies how many records to return
        per page (the default is 20).
        """
        res = []
        result = None
        if limit == 0:
            li = 1000
        else:
            li = limit
        while True:
            result = self.api_call(
                "campaigns/{}/adgroups".format(campaign_id),
                method="GET",
                offset=offset,
                limit=li,
            )
            res.extend(result["data"])
            res_len = len(res)
            if res_len == limit or result["pagination"]["totalResults"] == res_len:
                break
            print(result["pagination"], len(result["data"]))
            offset += result["pagination"]["itemsPerPage"]
        return res

    def get_adgroup(self, campaign_id, adgroup_id):
        """
        Returns a specific adgroup.
        {
            "orgId": 0000000,
            "name": "name",
            "budgetAmount": {
                "amount": "2000",
                "currency": "USD"
            },
            "dailyBudgetAmount": {
                "amount": "300",
                "currency": "USD"
            },
            "adamId": 00000000,
            "countriesOrRegions": ["US", "AU"]
        }
        """
        res = self.api_call(
            "campaigns/{}/adgroups/{}".format(campaign_id, adgroup_id), method="GET"
        )
        return res

    def update_adgroup(
        self,
        campaign_id,
        adgroup_id,
        adgroup_name=None,
        cpa_goal=None,
        currency=None,
        cpc_bid=None,
        start_time=None,
        end_time=None,
        automated_keywords_opt_in=False,
        age=None,
        gender=None,
        device_class=None,
        day_part=None,
        adminArea=None,
        locality=None,
        appDownloaders=None,
    ):
        """
        Allows edits to adGroups according to campaignId.
        For PUT, on adGroup update, if updating targetingDimensions
        then all dimensions must be specified.
        {
        "name": "<name>",
        "cpaGoal": {
            "amount": "100",
            "currency": "USD"
        },
        "startTime": "2019-08-20T16:20:31.650",
        "endTime": "2019-08-20T19:33:31.650",
        "automatedKeywordsOptIn": false,
        "defaultCpcBid": {
            "amount": "100",
            "currency": "USD"
        },
        "targetingDimensions": {
            "age": {
                "included": [
                    {
                        "minAge": 20,
                        "maxAge": 25
                    }
                ]
            },
            "gender": {
                "included": [
                    "M"
                ]
            },
            "country": null,
            "adminArea": null,
            "locality": null,
            "deviceClass": {
                "included": [
                    "IPAD",
                    "IPHONE"
                ]
            },
            "daypart": {
                "userTime": {
                    "included": [
                        1,
                        3,
                        22,
                        24
                    ]
                }
            },
                        "appDownloaders": null
                    }
            }
        """
        dimensions = None
        if (
            gender is not None
            or device_class is not None
            or day_part is not None
            or adminArea is not None
            or locality is not None
            or appDownloaders is not None
        ):
            dimensions = {
                "age": {"included": age},
                "gender": {"included": gender},
                "deviceClass": {"included": device_class},
                "daypart": {"userTime": {"included": day_part}},
                "adminArea": {"included": adminArea},
                "locality": {"included": locality},
                "appDownloaders": appDownloaders,
            }
        data = {
            "automatedKeywordsOptIn": automated_keywords_opt_in,
        }
        if adgroup_name is not None:
            data["name"] = adgroup_name
        if dimensions is not None:
            data["targetingDimensions"] = dimensions
        if cpa_goal is not None:
            data["cpaGoal"] = {"amount": "{}".format(cpa_goal), "currency": currency}
        if cpc_bid is not None:
            data["defaultCpcBid"] = {
                "amount": "{}".format(cpc_bid),
                "currency": currency,
            }
        if start_time is not None:
            data["startTime"] = start_time.strftime("%Y-%m-%dT%H:%M:%S.%f")
        if end_time is not None:
            data["endTime"] = end_time.strftime("%Y-%m-%dT%H:%M:%S.%f")
        # print(data)
        res = self.api_call(
            "campaigns/{}/adgroups/{}".format(campaign_id, adgroup_id),
            json_data=data,
            method="PUT",
        )
        if res["error"] is not None:
            print(res["error"])
            print("Make sure to provide all targeting dimesions")
        return res

    def delete_adgroup(self, campaign_id, adgroup_id):
        """
        Deletes an ad group by using a campaign and ad group identifier.
        """
        res = self.api_call(
            "campaigns/{}/adgroups/{}".format(campaign_id, adgroup_id), method="DELETE"
        )
        return res

    # Targeting Keyword Methods

    def add_targeting_keywords(self, campaign_id, adgroup_id, keywords):
        """
        Creates targeting keywords to use in ad groups.
        [{
            "text": "keyword 4",
            "matchType": "BROAD",
            "bidAmount": {
                "amount": "1.50",
                "currency": "USD"
            }
        }, {
            "text": "keyword 5",
            "matchType": "EXACT",
            "bidAmount": {
                "amount": "2",
                "currency": "USD"
            }
        }]
        """
        res = self.api_call(
            "campaigns/{}/adgroups/{}/targetingkeywords/bulk".format(
                campaign_id, adgroup_id
            ),
            json_data=keywords,
            method="POST",
        )
        return res

    def find_targeting_keywords(
        self,
        campaign_id,
        adgroup_id,
        sort_field="id",
        sort_order="ASCENDING",
        conditions=[],
        limit=1000,
        offset=0,
    ):
        """
        Fetches keywords used in ad groups.
        {
            "pagination": {
                "offset": 0,
                "limit": 1000
            },
            "orderBy": [{
                "field": "id",
                "sortOrder": "ASCENDING"
            }],
            "conditions": [{
                "field": "matchType",
                "operator": "EQUALS",
                "values": [
                    "BROAD"
                ]
            }]
        }
        Conditions Example:
        {"field": "matchType","operator": "EQUALS","values": ["BROAD"]}
        """
        data = {
            "pagination": {"offset": offset, "limit": limit},
            "orderBy": [{"field": sort_field, "sortOrder": sort_order}],
            "conditions": conditions,
        }
        res = self.api_call(
            "campaigns/{}/adgroups/targetingkeywords/find".format(campaign_id),
            json_data=data,
            method="POST",
        )
        return res

    def get_targeting_keyword(self, campaign_id, adgroup_id, keyword_id):
        """
        Fetches a specific targeting keyword used in an ad group.
        """
        res = self.api_call(
            "campaigns/{}/adgroup/{}/targetingkeywords/{}".format(
                campaign_id, adgroup_id, keyword_id
            ),
            method="GET",
        )
        return res

    def get_targeting_keywords(self, campaign_id, adgroup_id, limit=1000, offset=0):
        """
        Fetches all targeting keywords used in ad groups.
        """
        res = []
        result = None
        if limit == 0:
            li = 1000
        else:
            li = limit
        while True:
            result = self.api_call(
                "campaigns/{}/adgroups/{}/targetingkeywords/".format(
                    campaign_id, adgroup_id
                ),
                method="GET",
                limit=li,
                offset=offset,
            )
            res.extend(result["data"])
            res_len = len(res)
            if res_len == limit or result["pagination"]["totalResults"] == res_len:
                break
            print(result["pagination"], len(result["data"]))
            offset += result["pagination"]["itemsPerPage"]
        return res

    def update_targeting_keywords(self, campaign_id, adgroup_id, keywords):
        """
        Updates targeting keywords used in ad groups.
        Here is an example keywords list
        keywords = [{
            "id": 291202529,
            "status": "PAUSED",
            "bidAmount": {
                "amount": "0.5",
                "currency": "EUR"
            }
        },
        {
            "id": 291202530,
            "status": "PAUSED",
            "bidAmount": {
                "amount": "0.5",
                "currency": "EUR"
            }
        }]
        """
        res = self.api_call(
            f"campaigns/{campaign_id}/adgroups/{adgroup_id}/targetingkeywords/bulk",
            json_data=keywords,
            method="PUT",
        )
        return res

    def delete_targeting_keyword(self, campaign_id, adgroup_id, keyword_id):
        """
        Deletes a targeting keyword in an ad group.
        """
        res = self.api_call(
            f"campaigns/{campaign_id}/adgroups/{adgroup_id}/targetingkeywords/{keyword_id}",
            method="DELETE",
        )
        return res

    def delete_targeting_keywords(self, campaign_id, adgroup_id):
        """
        Deletes targeting keywords from ad groups.
        """
        res = self.api_call(
            f"campaigns/{campaign_id}/adgroups/{adgroup_id}/targetingkeywords/delete/bulk",
            method="POST",
        )
        return res   
     
    # Campaign Negative Keyword Methods

    def add_campaign_negative_keywords(self, campaign_id, keywords):
        """
        Creates negative keywords to use in a specific ad group.
        [{
            "text": "keyword 4",
            "matchType": "BROAD",
            "Status": "PAUSED"
        }, {
            "text": "keyword 5",
            "matchType": "EXACT",
            "Status": "PAUSED"
        }]
        """
        res = self.api_call(
            "campaigns/{}/negativekeywords/bulk".format(campaign_id),
            json_data=keywords,
            method="POST",
        )
        return res

    def find_campaign_negative_keywords(
        self,
        campaign_id,
        sort_field="id",
        sort_order="ASCENDING",
        conditions=[],
        limit=1000,
        offset=0,
    ):
        """
        Fetches negative keywords for campaigns.
        {
            "pagination": {
                "offset": 0,
                "limit": 1000
            },
            "orderBy": [{
                "field": "id",
                "sortOrder": "ASCENDING"
            }],
            "conditions": [{
                "field": "matchType",
                "operator": "EQUALS",
                "values": [
                    "BROAD"
                ]
            }]
        }
        Conditions Example:
        {"field": "matchType","operator": "EQUALS","values": ["BROAD"]}
        """
        data = {
            "pagination": {"offset": offset, "limit": limit},
            "orderBy": [{"field": sort_field, "sortOrder": sort_order}],
            "conditions": conditions,
        }
        res = self.api_call(
            f"campaigns/{campaign_id}/negativekeywords/find",
            json_data=data,
            method="POST",
        )
        return res
    
    def get_campaign_negative_keyword(self, campaign_id, negative_keyword_id):
        """
        Gets a campaign negative keyword.
        """
        res = self.api_call(
            "campaigns/{}/negativekeywords/{}".format(campaign_id, negative_keyword_id),
            method="GET",
        )
        return res

    def get_campaign_negative_keywords(self, campaign_id, limit=1000, offset=0):
        """
        Gets all campaign negative keywords.
        """
        res = []
        result = None
        if limit == 0:
            li = 1000
        else:
            li = limit
        while True:
            result = self.api_call(
                "campaigns/{}/negativekeywords".format(campaign_id),
                method="GET",
                limit=li,
                offset=offset,
            )
            res.extend(result["data"])
            res_len = len(res)
            if res_len == limit or result["pagination"]["totalResults"] == res_len:
                break
            print(result["pagination"], len(result["data"]))
            offset += result["pagination"]["itemsPerPage"]
        return res

    def update_campaign_negative_keywords(self, campaign_id, keywords):
        """
        Updates multiple campaign negative keywords.
        [{
            "id": "291225104",
            "status" : "PAUSED",
        }]
        """
        res = self.api_call(
            "campaigns/{}/negativekeywords/bulk".format(campaign_id),
            json_data=keywords,
            method="PUT",
        )
        return res

    def delete_campaign_negative_keywords(self, campaign_id, keyword_ids):
        """
        Deletes multiple campaign negative keywords.
        [
            <keywordId>,
            0000000,
            0000000
        ]
        """
        res = self.api_call(
            "campaigns/{}/negativekeywords/delete/bulk".format(campaign_id),
            json_data=keyword_ids,
            method="POST",
        )
        return res

    # Adgroup Negative Keyword Methods

    def add_adgroup_negative_keywords(self, campaign_id, adgroup_id, keywords):
        """
        Adds multiple adGroup negative keywords.
        [{
            "text": "keyword 4",
            "matchType": "BROAD",
            "Status": "PAUSED"
        }, {
            "text": "keyword 5",
            "matchType": "EXACT",
            "Status": "PAUSED"
        }]
        """
        res = self.api_call(
            "campaigns/{}/adgroups/{}/negativekeywords/bulk".format(
                campaign_id, adgroup_id
            ),
            json_data=keywords,
            method="POST",
        )
        return res

    def find_adgroup_negative_keywords(
        self,
        campaign_id,
        sort_field="id",
        sort_order="ASCENDING",
        conditions=[],
        limit=1000,
        offset=0,
    ):
        """
        Fetches negative keywords in a campaign’s ad groups.
        {
            "pagination": {
                "offset": 0,
                "limit": 1000
            },
            "orderBy": [{
                "field": "id",
                "sortOrder": "ASCENDING"
            }],
            "conditions": [{
                "field": "matchType",
                "operator": "EQUALS",
                "values": [
                    "BROAD"
                ]
            }]
        }
        Conditions Example:
        {"field": "matchType","operator": "EQUALS","values": ["BROAD"]}
        """
        data = {
            "pagination": {"offset": offset, "limit": limit},
            "orderBy": [{"field": sort_field, "sortOrder": sort_order}],
            "conditions": conditions,
        }
        res = self.api_call(
            f"campaigns/{campaign_id}/adgroups/negativekeywords/find",
            json_data=data,
            method="POST",
        )
        return res
    
    def get_adgroup_negative_keyword(
        self, campaign_id, adgroup_id, negative_keyword_id
    ):
        """
        Fetches a specific negative keyword used in an ad group.
        """
        res = self.api_call(
            "campaigns/{}/adgroups/{}/negativekeywords/{}".format(
                campaign_id, adgroup_id, negative_keyword_id
            ),
            method="GET",
        )
        return res

    def get_adgroup_negative_keywords(self, campaign_id, adgroup_id):
        """
        Fetches all ad group negative keywords used in ad groups.
        """
        res = self.api_call(
            "campaigns/{}/adgroups/{}/negativekeywords".format(campaign_id, adgroup_id),
            method="GET",
        )
        return res

    def update_adgroup_negative_keywords(self, campaign_id, adgroup_id, keywords):
        """
        Updates negative keywords in an ad group.
        [{
            "text": "negative keyword 1",
            "matchType": "EXACT"
         },
         {
            "text": "negative keyword 2",
            "matchType": "BROAD"
         }
        ]
        """
        res = self.api_call(
            "campaigns/{}/adgroups/{}/negativekeywords/bulk".format(
                campaign_id, adgroup_id
            ),
            json_data=keywords,
            method="PUT",
        )
        return res

    def delete_adgroup_negative_keywords(self, campaign_id, adgroup_id, keyword_ids):
        """
        Deletes negative keywords from an ad group.
        [
            <keywordId>,
            0000000,
            0000000
        ]
        """
        res = self.api_call(
            "campaigns/{}/adgroups/{}/negativekeywords/delete/bulk".format(
                campaign_id, adgroup_id
            ),
            json_data=keyword_ids,
            method="POST",
        )
        return res

    ## Creativeset Methods ##

    def get_creativesets_assets(self, adam_id, countries_or_regions, assets_gen_ids=[]):
        """
        Fetches assets used with Creative Sets.
        Deprecated
        """
        data = {
            "countryOrRegions": countries_or_regions,
            "assetsGenIds": assets_gen_ids,
        }
        res = self.api_call(
            "creativeappassets/{}".format(adam_id), json_data=data, method="POST"
        )
        return res

    def create_creativeset(
        self, campaign_id, adgroup_id, adamId, name, languageCode, assetsGenIds
    ):
        """
        Deprecated
        Creates a creative set experiment
        {
            "creativeSet": {
                "adamId": <adamId>,
                "name": "<name>",
                "languageCode": "en-US",
                "assetsGenIds": [
                "<assetsGenId>",
                "<assetsGenId>",
                "<assetsGenId>",
                "<assetsGenId>"
                ]
            }
        }
        """
        data = {}
        data["creativeSet"] = {
            "adamId": adamId,
            "name": name,
            "languageCode": languageCode,
            "assetsGenIds": assetsGenIds,
        }
        res = self.api_call(
            "campaigns/{}/adgroups/{}/adgroupcreativesets/creativesets".format(
                campaign_id, adgroup_id
            ),
            json_data=data,
            method="POST",
        )
        return res

    def update_adgroup_creativeset(
        self, campaign_id, adgroup_id, creativeset_id, status
    ):
        """
        Deprecated
        Updates the status of a CreativeSet in the specified campaign and
        adgroup. ENABLED or PAUSED
        {"status":"PAUSED"}
        """
        data = {}
        if status is not None:
            data["status"] = status
        res = self.api_call(
            "campaigns/{}/adgroup/{}/adgroupcreativeset/{}".format(
                campaign_id, adgroup_id, creativeset_id
            ),
            json_data=data,
            method="PUT",
        )
        return res

    def assign_creativeset_to_adgroup(self, campaign_id, adgroup_id, creativeset_id):
        """
        Deprecated
        Creates a Creative Set assignment to an ad group.
        """
        print("Please don't use this method as it's deprecated since v4")
        data = {"creativeSetId": creativeset_id}
        res = self.api_call(
            "campaigns/{}/adgroups/{}/adgroupcreativesets".format(
                campaign_id, adgroup_id
            ),
            json_data=data,
            method="POST",
        )
        return res

    def find_adgroup_creativesets(
        self,
        campaign_id,
        conditions=[],
        sort_field="id",
        sort_order="ASCENDING",
        limit=1000,
        offset=0,
    ):
        """
        Deprecated
        Fetches all Creative Sets assigned to ad groups.
        Use this endpoint to find all Creative Sets assigned to an ad group.
        Use the corresponding campaignId of the ad group in the URI.
        Use the id field with its corresponding ad group as a value
        in the request payload.
        conditions example:
        conditions = [{
        "field": "id",
        "operator": "EQUALS",
        "values": [
          "11111111"
            ]
        }]
        """
        print("Please don't use this method as it's deprecated since v4")
        data = {
            "selector": {
                "conditions": conditions,
                "pagination": {"offset": offset, "limit": limit},
                "orderBy": [{"field": sort_field, "sortOrder": sort_order}],
            }
        }
        res = self.api_call(
            "campaigns/{}/adgroupcreativesets/find".format(campaign_id),
            json_data=data,
            method="POST",
        )
        return res

    def find_creativesets(self, conditions=[], limit=1000, offset=0):
        """
        Deprecated
        Fetches all Creative Sets assigned to an organization.
        Use this endpoint to find all Creative Sets assigned to an organization.
        Use the name or id field with its corresponding campaignID as a value in
        the request payload.
        conditions={
                    "field": "id",
                    "operator": "EQUALS",
                    "values": [
                    "11111111"
                    ]
                }
        """
        print("Please don't use this method as it's deprecated since v4")
        data = {
            "selector": {
                "pagination": {"offset": offset, "limit": limit},
                "conditions": conditions,
            }
        }
        res = self.api_call("creativesets/find", json_data=data, method="POST")
        return res

    def get_creativeset(
        self, creativeset_id, include_deleted_creative_set_assets=False
    ):
        """
        Deprecated
        Fetches asset details of a Creative Set.
        """
        params = {
            "includeDeletedCreativeSetAssets": include_deleted_creative_set_assets
        }
        res = self.api_call("creativesets/{}".format(creativeset_id), params=params)
        return res

    def update_adgroup_creativeset_name(self, creativeset_id, name):
        """
        Deprecated
        Updates a Creative Set name using an identifier.
        {"name":"Campaign 2019"}
        """
        print("Please don't use this method as it's deprecated since v4")
        data = {"name": name}
        res = self.api_call(
            "creativesets/{}".format(creativeset_id), json_data=data, method="PUT"
        )
        return res

    def delete_creativesets(self, campaign_id, adgroup_id, ids):
        """
        Deprecated
        Delete Creative Sets from a specified ad group.
        you could specify either one id or a list of ids
        [11111111,22222222,33333333,4444444]
        """
        print("Please don't use this method as it's deprecated since v4")
        if type(ids) == int:
            ids = [ids]
        res = self.api_call(
            "campaigns/{}/adgroups/{}/adgroupcreativesets/delete/bulk".format(
                campaign_id, adgroup_id
            ),
            json_data=ids,
            method="POST",
        )
        return res

    # Product Pages methods

    def get_product_pages(self, adamId, name=None, states=None):
        """
        Fetches metadata of all your custom product pages.
        adamId: int, App Adam ID
        name: str, Filters by name field. For example, the name of your custom product page on App Store Connect.
        states: str, Possible values: VISIBLE, HIDDEN. Filters by states, which indicates whether the product page is visible or not.
        """
        data = {}
        if name is not None:
            data["name"] = name
        if states is not None:
            data["states"] = states
        res = self.api_call(f"apps/{adamId}/product-pages", params=data, method="GET")
        return res

    def get_product_page_by_identifier(self, adamId, productPageId):
        """
        Fetches metadata for a specific product page.

        adamId: int, (Required) Your adamId in the resource path must match the adamId in your campaign. Use Get a Campaign or Get All Campaigns to obtain your adamId and correlate it to the correct campaign.
        productPageId: int,  (Required) A unique string to identify a product page on App Store Connect. For example, 45812c9b-c296-43d3-c6a0-c5a02f74bf6e.
        """
        res = self.api_call(
            f"apps/{adamId}/product-pages/{productPageId}", method="GET"
        )
        return res

    def get_product_page_locales(
        self, adamId, productPageId, expand, languages, languageCodes, deviceClasses
    ):
        """
        Fetches product page locales by identifier.

        adamId: int, (Required) Your adamId in the resource path must match the adamId in your campaign. Use Get a Campaign or Get All Campaigns to obtain your adamId and correlate it to the correct campaign.
        productPageId: int,  (Required) A unique string to identify a product page on App Store Connect. For example, 45812c9b-c296-43d3-c6a0-c5a02f74bf6e.
        expand: Detailed app asset details of a device. Default: false
        languages: Filters by ISO alpha-2 country code, such as US.
        languageCodes: string Filters by ISO 639-1 language code appended to the ISO alpha-2 country code, such as en-US. The languageCodes paramater can have multiple values such as en-US, fr-CA.
        deviceClasses: string Filters by device type. Possible values: IPHONE, IPAD
        """
        data = {
            "expand": expand,
            "languages": languages,
            "languageCodes": languageCodes,
            "deviceClasses": deviceClasses,
        }
        res = self.api_call(
            f"apps/{adamId}/product-pages/{productPageId}/locale-details",
            params=data,
            method="GET",
        )
        return res

    def get_supported_languages(self, countriesOrRegions):
        """
        Fetches supported languages and language codes.

        countriesOrRegions: string, Filters by ISO alpha-2 country codes using one or more comma-separated values.
        For example: https://api.searchads.apple.com/api/v4/countries-or-regions?countriesOrRegions=US,GB,AU,CA.
        """
        data = {"countriesOrRegions": countriesOrRegions}
        res = self.api_call("countries-or-regions", params=data, method="GET")
        return res

    def get_app_preview_device_sizes(self):
        """
        Fetches supported app preview device size mappings.
        """
        return self.api_call("creativeappmappings/devices")

    # Ad Endpoints

    def create_an_ad(self, campaignId, adgroupId, name, creativeId, status):
        data = {"name": name, "creativeId": creativeId, "status": status}

        res = self.api_call(
            f"campaigns/{campaignId}/adgroups/{adgroupId}/ads",
            json_data=data,
            method="POST",
        )
        return res

    def find_ads(
        self,
        campaignId,
        fields=None,
        sort_field="creativeType",
        sort_order="ASCENDING",
        conditions=[],
        limit=1000,
        offset=0,
    ):
        """
        Finds ads within a campaign by selector criteria.
        {
            "fields": null,
            "pagination": {
                "offset": 0,
                "limit": 1000
            },
            "orderBy": [{
                "field": "creativeType",
                "sortOrder": "ASCENDING"
            }],
            "conditions": [{
                "field": "matchType",
                "operator": "EQUALS",
                "values": [
                    "BROAD"
                ]
            }]
        }
        Conditions Example:
            "conditions": [
                {
                "field": "creativeType",
                "operator": "EQUALS",
                "values": [
                    "CUSTOM_PRODUCT_PAGE"
                ]
                },
                {
                "field": "status",
                "operator": "EQUALS",
                "values": [
                    "PAUSED"
                ]
                }
            ],
        """
        data = {
            "fields": fields,
            "pagination": {"offset": offset, "limit": limit},
            "orderBy": [{"field": sort_field, "sortOrder": sort_order}],
            "conditions": conditions,
        }
        res = self.api_call(
            f"campaigns/{campaignId}/ads/find", json_data=data, method="POST"
        )
        return res

    def get_an_ad(self, campaignId, adgroupId, adId):
        """
        Fetches an ad assigned to an ad group by identifier.

        campaignId: int, (Required) Your Campaign Id Use Get a Campaign or Get All Campaigns to obtain your adamId and correlate it to the correct campaign.
        adgroupId: int,  (Required) A unique string to identify an adgroup
        adId: int,  (Required) A unique string to identify an ad
        """
        res = self.api_call(
            f"campaigns/{campaignId}/adgroups/{adgroupId}/ads/{adId}", method="GET"
        )
        return res

    def get_all_ads(self, campaignId, adgroupId):
        """
        Fetches all ads assigned to an ad group.

        campaignId: int, (Required) Your Campaign Id Use Get a Campaign or Get All Campaigns to obtain your adamId and correlate it to the correct campaign.
        adgroupId: int,  (Required) A unique string to identify an adgroup
        """
        res = self.api_call(f"campaigns/{campaignId}/adgroups/{adgroupId}/ads",
                            method="GET")
        return res

    def update_an_ad(self, campaignId, adgroupId, adId, name, status):
        """
        Updates an ad in an ad group.

        campaignId: int, (Required) Your Campaign Id Use Get a Campaign or Get All Campaigns to obtain your adamId and correlate it to the correct campaign.
        adgroupId: int,  (Required) A unique string to identify an adgroup
        adId: int,  (Required) A unique string to identify an Ad
        name: str, new name
        status: str, new status
        """
        data = {"name": name, "status": status}
        res = self.api_call(
            f"campaigns/{campaignId}/adgroups/{adgroupId}/ads/{adId}",
            json_data=data,
            method="PUT",
        )
        return res

    def delete_an_ad(self, campaignId, adgroupId, adId):
        """
        Deletes an ad from an ad group.

        campaignId: int, (Required) Your Campaign Id Use Get a Campaign or Get All Campaigns to obtain your adamId and correlate it to the correct campaign.
        adgroupId: int,  (Required) A unique string to identify an adgroup
        adId: int,  (Required) A unique string to identify an Ad
        """
        res = self.api_call(
            f"campaigns/{campaignId}/adgroups/{adgroupId}/ads/{adId}", method="DELETE"
        )
        return res

    # Reporting Methods

    def get_campaigns_report_by_date(
        self,
        start_date,
        end_date,
        sort_field="countryOrRegion",
        sort_order="ASCENDING",
        conditions=[],
        group_by="countryOrRegion",
        return_records_with_no_metrics=True,
        return_row_totals=True,
        return_grand_totals=True,
        granularity=None,
        offset=0,
        limit=1000,
    ):
        """
        Get reports on campaigns within a specific org.
        {
        "startTime": "2019-02-20",
        "endTime": "2019-02-28",
        "selector": {
            "orderBy": [
                {
                    "field": "countryOrRegion",
                    "sortOrder": "ASCENDING"
                }
            ],
            "conditions": [
                {
                    "field": "countriesOrRegions",
                    "operator": "CONTAINS_ANY",
                    "values": [
                        "US",
                        "GB"
                    ]
                },
                {
                    "field": "countryOrRegion",
                    "operator": "IN",
                    "values": [
                        "US"
                    ]
                }
            ],
            "pagination": {
                "offset": 0,
                "limit": 1000
            }
        },
        "groupBy": [
            "countryOrRegion"
        ],
        "timeZone": "UTC",
        "returnRecordsWithNoMetrics": true,
        "returnRowTotals": true,
        "returnGrandTotals": true
        }

        example conditions
        conditions = [{"field": "countriesOrRegions",
        "operator": "CONTAINS_ANY",
        "values": ["US","GB"]}]
        """
        return self._get_data(
            data_type="campaigns",
            start_date=start_date,
            end_date=end_date,
            sort_field=sort_field,
            sort_order=sort_order,
            conditions=conditions,
            group_by=group_by,
            no_metrics=return_records_with_no_metrics,
            return_row_totals=return_row_totals,
            return_grand_totals=return_grand_totals,
            granularity=granularity,
            offset=offset,
            limit=limit,
        )

    def get_adgroups_report_by_date(
        self,
        campaignId,
        start_date,
        end_date,
        sort_field="adGroupId",
        sort_order="ASCENDING",
        conditions=[],
        return_records_with_no_metrics=True,
        return_row_totals=True,
        return_grand_totals=True,
        granularity=None,
        group_by=None,
        offset=0,
        limit=1000,
    ):
        """
        Get reports on adGroups within a specific campaign.
        {
            "startTime": "2019-02-20",
            "endTime": "2019-02-28",
            "selector": {
                "orderBy": [{
                    "field": "adGroupId",
                    "sortOrder": "ASCENDING"
                }],
                "conditions": [{
                    "field": "deleted",
                    "operator": "EQUALS",
                    "values": [
                        "false"
                    ]
                }],
                "pagination": {
                    "offset": 0,
                    "limit": 1000
                }
            },
            "timeZone": "UTC",
            "returnRecordsWithNoMetrics": true,
            "returnRowTotals": true,
            "returnGrandTotals": true
        }
        conditions example
        {"field": "deleted","operator": "EQUALS","values": ["false"]}
        """
        return self._get_data(
            data_type="adgroups",
            campaignId=campaignId,
            start_date=start_date,
            end_date=end_date,
            sort_field=sort_field,
            sort_order=sort_order,
            conditions=conditions,
            no_metrics=return_records_with_no_metrics,
            return_row_totals=return_row_totals,
            return_grand_totals=return_grand_totals,
            granularity=granularity,
            group_by=group_by,
            offset=offset,
            limit=limit,
        )

    def get_keywords_report_by_date(
        self,
        campaignId,
        start_date,
        end_date,
        sort_field="adGroupId",
        sort_order="ASCENDING",
        conditions=[],
        return_records_with_no_metrics=True,
        return_row_totals=True,
        return_grand_totals=True,
        granularity=None,
        group_by=None,
        offset=0,
        limit=1000,
    ):
        """
        Get reports on targeting keywords within a specific campaign.
        """
        return self._get_data(
            data_type="keywords",
            campaignId=campaignId,
            start_date=start_date,
            end_date=end_date,
            sort_field=sort_field,
            sort_order=sort_order,
            conditions=conditions,
            no_metrics=return_records_with_no_metrics,
            return_row_totals=return_row_totals,
            return_grand_totals=return_grand_totals,
            granularity=granularity,
            group_by=group_by,
            offset=offset,
            limit=limit,
        )

    def get_keyword_level_within_adgroup_report_by_date(
        self,
        campaignId,
        adgroupId,
        start_date,
        end_date,
        sort_field="adGroupId",
        sort_order="ASCENDING",
        conditions=[],
        return_records_with_no_metrics=True,
        return_row_totals=True,
        return_grand_totals=True,
        granularity=None,
        group_by=None,
        offset=0,
        limit=1000,
    ):
        """
        Fetches reports for targeting keywords within an ad group.

        Use this endpoint to fetch reports for a high volume of targeting keywords in your campaigns.
        The orderBy Selector specifies fields to sort the records list by ASCENDING or DESCENDING.
        All ReportingKeyword fields are available to the orderBy Selector.
        """
        return self._get_data(
            data_type="keywords_adgroup",
            campaignId=campaignId,
            adgroupId=adgroupId,
            start_date=start_date,
            end_date=end_date,
            sort_field=sort_field,
            sort_order=sort_order,
            conditions=conditions,
            no_metrics=return_records_with_no_metrics,
            return_row_totals=return_row_totals,
            return_grand_totals=return_grand_totals,
            granularity=granularity,
            group_by=group_by,
            offset=offset,
            limit=limit,
        )

    def get_searchterms_report_by_date(
        self,
        campaignId,
        start_date,
        end_date,
        sort_field="adGroupId",
        sort_order="ASCENDING",
        conditions=[],
        return_records_with_no_metrics=False,
        return_row_totals=True,
        return_grand_totals=True,
        granularity=None,
        group_by=None,
        offset=0,
        limit=1000,
    ):
        """
        Get reports on targeting keywords within a specific campaign.
        """
        return self._get_data(
            data_type="searchterms",
            campaignId=campaignId,
            start_date=start_date,
            end_date=end_date,
            sort_field=sort_field,
            sort_order=sort_order,
            conditions=conditions,
            no_metrics=return_records_with_no_metrics,
            return_row_totals=return_row_totals,
            return_grand_totals=return_grand_totals,
            granularity=granularity,
            group_by=group_by,
            offset=offset,
            limit=limit,
        )

    def get_searchterm_level_within_an_adgroup_report_by_date(
        self,
        campaignId,
        adgroupId,
        start_date,
        end_date,
        sort_field="adGroupId",
        sort_order="ASCENDING",
        conditions=[],
        return_records_with_no_metrics=False,
        return_row_totals=True,
        return_grand_totals=True,
        granularity=None,
        group_by=None,
        offset=0,
        limit=1000,
    ):
        """
        Fetches reports for search terms within an ad group.
        Use this endpoint to fetch reports with a high volume of search terms in your campaign.
        See ReportingSearchTerm for Condition operators and field values to filter results with a Selector.
        The limit for search term-level reports is 10 impressions. Search term-level reports only support
        a timeZone value of ORTZ. The orderBy Selector specifies fields to sort the records list by ASCENDING
        or DESCENDING. All ReportingSearchTerm fields are available to the orderBy Selector.
        """
        return self._get_data(
            data_type="searchterms_adgroup",
            campaignId=campaignId,
            adgroupId=adgroupId,
            start_date=start_date,
            end_date=end_date,
            sort_field=sort_field,
            sort_order=sort_order,
            conditions=conditions,
            no_metrics=return_records_with_no_metrics,
            return_row_totals=return_row_totals,
            return_grand_totals=return_grand_totals,
            granularity=granularity,
            group_by=group_by,
            offset=offset,
            limit=limit,
        )

    def get_creativesets_report_by_date(
        self,
        campaignId,
        start_date,
        end_date,
        sort_field="adGroupId",
        sort_order="ASCENDING",
        conditions=[],
        return_records_with_no_metrics=True,
        return_row_totals=True,
        return_grand_totals=True,
        granularity=None,
        group_by=None,
        offset=0,
        limit=1000,
    ):
        """
        DEPRECATED and no longer to be used since ASA API v4
        Fetches reports on Creative Sets used within a campaign.
        conditions example
        {"field": "deleted","operator": "EQUALS","values": ["false"]}
        """
        return self._get_data(
            data_type="creativesets",
            campaignId=campaignId,
            start_date=start_date,
            end_date=end_date,
            sort_field=sort_field,
            sort_order=sort_order,
            conditions=conditions,
            no_metrics=return_records_with_no_metrics,
            return_row_totals=return_row_totals,
            return_grand_totals=return_grand_totals,
            granularity=granularity,
            group_by=group_by,
            offset=offset,
            limit=limit,
        )

    def get_ad_level_report_by_date(
        self,
        campaignId,
        start_date,
        end_date,
        sort_field="adGroupId",
        sort_order="ASCENDING",
        conditions=[],
        return_records_with_no_metrics=True,
        return_row_totals=True,
        return_grand_totals=True,
        granularity=None,
        group_by=None,
        offset=0,
        limit=1000,
    ):
        """
        Fetches ad performance data within a campaign.
        conditions example
        {"field": "deleted","operator": "EQUALS","values": ["false"]}
        """
        return self._get_data(
            data_type="ads",
            campaignId=campaignId,
            start_date=start_date,
            end_date=end_date,
            sort_field=sort_field,
            sort_order=sort_order,
            conditions=conditions,
            no_metrics=return_records_with_no_metrics,
            return_row_totals=return_row_totals,
            return_grand_totals=return_grand_totals,
            granularity=granularity,
            group_by=group_by,
            offset=offset,
            limit=limit,
        )

    def impression_share_reports(
        self,
        start_date,
        end_date,
        date_range=None,
        name="impression_share_API_report_example_1",
        sort_field="adamId",
        sort_order="ASCENDING",
        conditions=[],
        return_records_with_no_metrics=True,
        return_row_totals=False,
        return_grand_totals=False,
        granularity="DAILY",
        group_by=None,
        offset=0,
        limit=1000,
    ):
        """
        Obtain a report ID.
        
        The date range of the report request. A date range is required only when using WEEKLY granularity.
        dateRange Possible values: LAST_WEEK, LAST_2_WEEKS, LAST_4_WEEKS
        granularity Possible values: DAILY, WEEKLY
        conditions example
        {
            "field": "countryOrRegion",
            "operator": "IN",
            "values": [
            "US",
            "IN"
            ]
        }
        """
        return self._get_data(
            data_type="impression_share_report",
            name=name,
            date_range=date_range,
            start_date=start_date,
            end_date=end_date,
            sort_field=sort_field,
            sort_order=sort_order,
            conditions=conditions,
            no_metrics=return_records_with_no_metrics,
            return_row_totals=return_row_totals,
            return_grand_totals=return_grand_totals,
            granularity=granularity,
            group_by=group_by,
            offset=offset,
            limit=limit,
        )

    def get_single_impression_share_report(self, report_id):
        """
        Returns a single Impression Share report containing metrics and metadata.
        """
        res = self.api_call(
            f"custom-reports/{report_id}/", method="GET"
        )
        return res
    
    def get_all_impression_share_reports(self, field="creationTime", limit=20, offset=0, sort_order="DESCENDING"):
        """
        Returns all Impression Share reports containing metrics and metadata.
        """
        data = {
            "offset": offset, "limit": limit, "field": field, "sortOrder": sort_order 
        }
        res = self.api_call(
            f"custom-reports", params=data, method="GET"
        )
        return res

    def _get_data(
        self,
        data_type,
        start_date,
        end_date,
        sort_field,
        sort_order,
        conditions,
        no_metrics,
        return_row_totals,
        return_grand_totals,
        offset,
        limit,
        date_range = None, # only for the impression share report
        name = None, # only for the impression share report
        granularity=None,
        campaignId=None,
        adgroupId=None,
        group_by=None,
    ):
        """
        This is a helper function
        Request driver
        granularity Possible values: MONTHLY, WEEKLY, DAILY, HOURLY
        """
        row = []
        grandTotals = []
        if limit == 0:
            li = 1000
        else:
            li = limit
        if granularity is not None:
            if return_grand_totals is True or return_row_totals is True:
                print("return_grand_totals and return_row_totals must be False")
                return None
        while True:
            # Use this data schema for all reports except of impression share
            data = {
                "startTime": start_date,
                "endTime": end_date,
                "selector": {
                    "orderBy": [{"field": sort_field, "sortOrder": sort_order}],
                    "conditions": conditions,
                    "pagination": {"offset": offset, "limit": li},
                },
                "timeZone": "UTC",
                "returnRecordsWithNoMetrics": no_metrics,
                "returnRowTotals": return_row_totals,
                "returnGrandTotals": return_grand_totals,
            }
            if granularity is not None:
                data["granularity"] = granularity
            if group_by is not None:
                data["groupBy"] = [group_by]
            
            if data_type == "campaigns":
                res = self.api_call("reports/campaigns", json_data=data, method="POST")
            elif data_type == "adgroups":
                res = self.api_call(
                    f"reports/campaigns/{campaignId}/adgroups",
                    json_data=data,
                    method="POST",
                )
            elif data_type == "creativesets":
                res = self.api_call(
                    f"reports/campaigns/{campaignId}/creativesets",
                    json_data=data,
                    method="POST",
                )
            elif data_type == "ads":
                res = self.api_call(
                    f"reports/campaigns/{campaignId}/ads", json_data=data, method="POST"
                )
            elif data_type == "keywords":
                res = self.api_call(
                    f"reports/campaigns/{campaignId}/keywords",
                    json_data=data,
                    method="POST",
                )
            elif data_type == "keywords_adgroup":
                res = self.api_call(
                    f"reports/campaigns/{campaignId}/adgroups/{adgroupId}/keywords",
                    json_data=data,
                    method="POST",
                )
            elif data_type == "searchterms":
                res = self.api_call(
                    f"reports/campaigns/{campaignId}/searchterms",
                    json_data=data,
                    method="POST",
                )
            elif data_type == "searchterms_adgroup":
                res = self.api_call(
                    f"reports/campaigns/{campaignId}/adgroups/{adgroupId}/searchterms",
                    json_data=data,
                    method="POST",
                )
            elif data_type == "impression_share_report":
                data = {
                    "name": name,
                    "startTime": start_date,
                    "endTime": end_date,
                    "granularity": granularity,
                    "selector": {
                        "conditions": conditions,
                    }, 
                }
                if date_range is not None:
                    data["dateRange"] = date_range

                res = self.api_call(
                    f"custom-reports",
                    json_data=data,
                    method="POST",
                )
                if res is None:
                    return None
                return res["data"]
            else:
                print("Unknown request type", data_type)
            if res is None:
                return None
            if res["data"] is None:
                return None
            if res["data"]["reportingDataResponse"] is None:
                return None
            row.extend(res["data"]["reportingDataResponse"]["row"])
            if return_grand_totals:
                grandTotals.extend(res["data"]["reportingDataResponse"]["grandTotals"])
            res_len = len(row)

            offset = len(row)
            # print(limit)
            if res_len == limit or res_len >= res["pagination"]["totalResults"]:
                break
        if return_grand_totals:
            return row, grandTotals
        return row

    # Geosearch Methods
    def geo_search(
        self, word, entity="Country", country_code="GB", limit=100, offset=0
    ):
        """
        Returns a list of geo locations according to the entity type and the country code.
        entity: The country, adminArea, or Locality locations available for targeting.
        """
        params = {
            "query": word,
            "countrycode": country_code,
            "entity": entity,
            "offset": offset,
            "limit": limit,
        }
        res = self.api_call("search/geo", params=params, method="GET")
        return res

    def get_admin_areas(self, country_code):
        """
        Returns a list of admin areas in a country.
        """
        res = self.api_call(
            "search/geo",
            params={"entity": "AdminArea", "countrycode": country_code},
            method="GET",
        )["data"]
        return res

    def get_localities(self, country_code):
        """
        Returns a list of localities .
        """
        res = self.api_call(
            "search/geo?countrycode={}&entity=Locality".format(country_code),
            method="GET",
        )["data"]
        return res

    def get_geo_locations_list(self, geo_id, entity, limit=1000, offset=0):
        """
        Gets geo location details based on geo identifier.
        geo_id: string
            (Required) The parameter used to specify the geographic
            location formatted as CountryCode|AdminArea|Locality.
            CountryCode is a ISO-ALPHA2-COUNTRYCODE string.
            AdminArea is state or the equivalent according
            to its associated Country.
            Locality is city or the equivalent
            according to its associated adminArea.
        """
        res = self.api_call(
            "search/geo",
            params={"limit": limit, "offset": offset},
            json_data={"id": geo_id, "entity": entity},
            method="POST",
        )["data"]
        return res
