![Phiture](logo.png)

### About Phiture

_[Phiture](http://phiture.com) is a Berlin-based mobile growth consultancy working with the teams behind leading apps. Using the company’s industry-acclaimed Mobile Growth Stack as a strategic framework, Phiture team offers 4 key services: App Store Optimization, Apple Search Ads, User Retention services and Growth Consulting._

### Apple Searchads API Library in Python

In order to facilitate the usage of the Apple Search Ads API Phiture's Engineers have built a library in Python which allows users to manage campaigns, ad groups, keywords and creative sets. This library only requires intermediate Python skills and therefore makes it possible not only for Engineers but also for Data Analysts and Apple Search Ads Consultants to work with it.  While the library is extensive it is not complete and users are encouraged to commit suggestions.
The official link to the searchads campaign management api is https://developer.apple.com/documentation/search_ads/

## Setup


### Using cert and key files
Create a certs directory inside of your project folder, or create a different certs directory and specify it using the certificates_dir_path argument.

```python
PEM_FILE_PATH = "cert.pem"
KEY_FILE_PATH = "cert.key"
CERTIFICATES_DIR_PATH = "certs/"

api = SearchAdsAPI(
    org_id=123456,
    pem=PEM_FILE_PATH,
    key=KEY_FILE_PATH,
    certificates_dir_path=CERTIFICATES_DIR_PATH,
    client_id="SEARCHADS.12345678-1234-1234-1234-123456789012",
    team_id="SEARCHADS.12345678-1234-1234-1234-123456789012",
    key_id="12345678-1234-1234-1234-123456789012",
)
```

### Using cert and key file strings
```python
PEM_FILE_CONTENT = """
-----BEGIN PUBLIC KEY-----
...
-----END PUBLIC KEY-----
"""

KEY_FILE_CONTENT = """
-----BEGIN EC PRIVATE KEY-----
...
-----END EC PRIVATE KEY-----
"""

api = SearchAdsAPI(
    org_id=123456,
    pem_content=PEM_FILE_CONTENT,
    key_content=KEY_FILE_CONTENT,
    client_id="SEARCHADS.12345678-1234-1234-1234-123456789012",
    team_id="SEARCHADS.12345678-1234-1234-1234-123456789012",
    key_id="12345678-1234-1234-1234-123456789012",
)
```

## Available Methods

### Campaign Methods

- Create a new campaign

         res = api.create_campaign(1433439534, ['AU'], "test", 1, 1, "EUR")

- Find campaigns using a conditions list

         res = api.find_campaigns(conditions=[{"field": "countriesOrRegions","operator": "CONTAINS_ALL","values": ["US", "CA"]}])

- Get a specific campaign

         res = api.get_campaign(283767149)

- Get all campaigns

         res = api.get_campaigns(limit=0)

- Update a campaign

         res = update_campaign(campaign_id, countries=None, campaign_name="Christmas Campaign 2019", budget=None, daily_budget=None, curruncy=None, status=None, adamId=None)

- Delete campaign

         res = api.delete_campaign(283767149)

### Adgroup Methods

- Create a new adGroup inside of a campaign

        res = api.create_adgroup(186370637, "test", "EUR",1, datetime.datetime.utcnow())
        
        res = api.create_adgroup(186370637, "test", "EUR",1, datetime.datetime.utcnow(), localities=["US|NY|New York"], adminAreas=["US|NY"])

         res = api.create_adgroup(campaign_id, adgroup_name, currency,
                       cpc_bid,  start_time, end_time=None, cpa_goal=None,  automated_keywords_opt_in=False, age=None, gender=None, device_class=None, day_part=None, adminArea=None, locality=None, appDownloaders=None)

- Fetch ad groups within a campaign.

         res = api.find_adgroups(campaign_id, limit=1000, offset=0, sort_field="id", sort_order="ASCENDING", conditions=[], fields=[])

- Get all adGroups

         res = api.get_adgroups(290916652)

- Get a specific adGroup

         res = api.get_adgroups(290916652, 21321323)

- Update an Adgroup

         res = update_adgroup(campaign_id, adgroup_id, adgroup_name=None,                             cpa_goal=None, currency=None,
                       cpc_bid=None, start_time=None, end_time=None, automated_keywords_opt_in=False, age=None, gender=None, device_class=None,
                       day_part=None, adminArea=None, locality=None, appDownloaders=None)

- Delete an Adgroup

         res = delete_adgroup(campaign_id, adgroup_id)


### Targeting Keyword Methods

- Add new targeting keywords to an AdGroup

         keywords = [{
                 "text": "keyword",
                 "matchType": "BROAD",
                 "status" : "PAUSED",
                 "bidAmount": {
                     "amount": "1",
                     "currency": "EUR"
                 }
             }, {
                 "text": "keyword 5",
                 "matchType": "EXACT",
                 "status" : "PAUSED",
                 "bidAmount": {
                     "amount": "1",
                     "currency": "EUR"
                 }
             }]
         res = api.add_targeting_keywords(290916652,291017295,keywords)

- Fetch keywords used in ad groups.

         res = find_targeting_keywords(campaign_id, adgroup_id, sort_field="id", sort_order="ASCENDING", conditions=[], offset=0, limit=1000)

- Get one targeting keyword

         res = api.get_targeting_keyword(290916652,291017295, 213213213)

- Get all targeting keywords

         res = api.get_targeting_keywords(290916652,291017295)

- Update targeting keywords in an adGroup

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
                     }
                     ]
         res = api.update_targeting_keywords(290916652, 291017295, keywords)

### Campaign Negative Keyword Methods

- Add new campaign negative keywords

         keywords = [{
                 "text": "keyword",
                 "matchType": "BROAD",
                 "status" : "PAUSED",
             }, {
                 "text": "keyword 5",
                 "matchType": "EXACT",
                 "status" : "PAUSED",
             }]
         res = api.add_campaign_negative_keywords(290916652, keywords)

- Get a specific campaign negative keyword

         res = api.get_campaign_negative_keyword(290916652, 291225104)

- Get all campaign negative keywords

         res = api.get_campaign_negative_keywords(290916652)

- Update campaign negative keywords

         keywords = [{
                 "id": "291225104",
                 "status" : "PAUSED",
             }]
         res = api.update_campaign_negative_keywords(290916652, keywords)

- Delete campaign negative keywords

         keywords = [291225104]
         res = api.delete_campaign_negative_keywords(290916652, keywords)

### Adgroup Negative Keyword Methods

- Add new adgroup negative keywords

         keywords = [{
                 "text": "keyword",
                 "matchType": "BROAD",
                 "status" : "PAUSED",
             }, {
                 "text": "keyword 5",
                 "matchType": "EXACT",
                 "status" : "PAUSED",
             }]
         res = api.add_adgroup_negative_keywords(290916652, 291017295, keywords)

- Get a specific adGroup negative keyword

         res = api.get_adgroup_negative_keyword(290916652, 291017295, 291227741)

- Get all adgroup negative keywords

         res = api.get_adgroup_negative_keywords(290916652,291017295)

- Update adGroup negative keywords

         keywords = [{
             "id": "123456789",
             "status": "PAUSED",
         }]
         res = api.update_adgroup_negative_keywords(123456789, 291017295, keywords)

- Update a list of adGroup negative Keywords

         keywords = [{
                     "id": 0000000,
                     "adGroupId": 291017295,
                     "text": "test",
                     "status": "PAUSED",
                     "matchType": "EXACT",
                     "bidAmount": {
                         "amount": "0.5",
                         "currency": "EUR"
                     },
                     "deleted": False
                 }]
         res = api.update_targeting_keywords(290916652,291017295,keywords)

- Delete a list of AdGroup negative keywords

         keyword_ids = [123456789]
         res = api.delete_adgroup_negative_keywords(290916652, 291017295, keyword_ids)

### Creativeset Methods (Some methods are Deprecated since ASA v4)

- DEPRECATED Fetch assets used with Creative Sets.

         res = api.get_creativesets_assets(adam_id, countries_or_regions, assets_gen_ids=[])

- Fetch supported app preview device size mappings.

         res = api.get_app_preview_device_sizes()

- Create a new creativeset

         res = api.create_creativeset(campaign_id, adgroup_id, adamId, name, languageCode, assetsGenIds)

- Get all Creativesets

         res = api.get_creativeset(campaign_id, adgroup_id=None, limit=1000, offset=0))

- Get a specific Creativesets

         res = api.get_creativeset(creativeset_id, include_deleted_creative_set_assets=False)

- DEPRECATED Update an Adgroup Creativeset

         res = api.update_creativeset(campaign_id, adgroup_id, creativeset_id, status)

- DEPRECATED Assign a Creativeset to an Adgroup

         res = api.assign_creativeset_to_adgroup(campaign_id, adgroup_id, creativeset_id)

- DEPRECATED Fetch all Creative Sets assigned to ad groups.

         conditions = [{
            "field": "id",
            "operator": "EQUALS",
            "values": [
            "11111111"
                ]
            }]
         res = api.find_adgroup_creativesets(campaign_id,conditions=conditions,         sort_field="id", sort_order="ASCENDING")

- DEPRECATED Fetch all Creative Sets assigned to an organization.

         res = api.find_creativesets(conditions=[], limit=1000, offset=0)

- Fetch asset details of a Creative Set.

         res = api.get_creativeset(creativeset_id, include_deleted_creative_set_assets=False)

- DEPRECATED Update a creativeset name

         res = api.update_adgroup_creativeset_name(creativeset_id, name)

- DEPRECATED Delete creative sets from a specified Adgroup
         res = api.delete_creativesets(campaign_id, adgroup_id, ids)

### Reporting Methods

- Get reports on campaigns within a specific org.

         res = api.get_campaigns_report_by_date("2019-04-01", "2019-04-10", 123456789, limit=5)

- Get reports on adgroups within a specific org.

         row, grandTotals = api.get_adgroups_report_by_date(123456789, "2019-02-20", "2019-02-28",limit=0)

- Get reports on keywords level. limit 0 gets all results instead of just 1000

         row, grandTotals = api.get_keywords_report_by_date(123456789, "2019-02-20", "2019-02-28",limit=0)

- Fetches reports for targeting keywords within an ad group. limit 0 gets all results instead of just 1000

         row, grandTotals = api.get_keyword_level_within_adgroup_report_by_date(123456789, 123456789, "2019-02-20", "2019-02-28",limit=0)

- DEPRECATED Get reports on creativeset level. limit 0 gets all results instead of just 1000

         row, grandTotals= api.get_creativesets_report_by_date(123456789, "2019-06-01", "2019-06-10")

- Fetches ad performance data within a campaign. limit 0 gets all results instead of just 1000

         row, grandTotals= api.get_ad_level_report_by_date(123456789, "2019-06-01", "2019-06-10")

- Get reports on searchterms level

         row, grandTotals = api.get_searcherms_report_by_date(123456789,"2019-05-01", "2019-05-07",limit=0)

- Fetches reports for search terms within an ad group.

         row, grandTotals = api.get_searchterm_level_within_an_adgroup_report_by_date(123456789, 123456789,"2019-05-01", "2019-05-07",limit=0)

### Geo Search

- Search Adminareas

         res = api.geo_search("New York", entity="AdminArea", country_code="US")

- Search Localities 

         res = api.geo_search("New York", entity="Locality", country_code="US")

- Returns a list of admin areas in a country.

         res = api.get_admin_areas(country_code="US")

- Returns a list of localities in a country.

         res = api.get_localities(country_code)

- Gets geo location details based on geo identifier.

         res = api.get_geo_locations_list(geo_id,
                               entity,
                               limit=1000, offset=0)

# Ad Endpoints

# Product Pages methods


# Impression share reports
- Create an impression share report example
         
         conditions = [
         {
             "field": "countryOrRegion",
             "operator": "IN",
             "values": [
             "US",
             "IN"
             ]
         }
         ]
         
         #res = api.impression_share_reports(start_date="2023-01-01", end_date="2023-01-20", conditions=conditions)

- Get a list of all impression share reports

         res = api.get_all_impression_share_reports()

- Get a single impression share report using report ID

         res = api.get_single_impression_share_report(12345)


## Changelog

* version 1.7.11 added support for use cert and key as strings
* version 1.7.10 always use the latest cryptography package
* version 1.7.9 always use the latest requests package
* version 1.7.7 fixed an issue update_campaign
* version 1.7.6 fixed an issue with token update
* version 1.7.1 added impression share reports and new find methods along product pages to match Searchads API version 4.7
* version 1.6.3 New bug fixes
* version 1.6.1 added new product page, reporting, and Ad endpoints. Deprecated creatives endpoints
* version 1.5.3 fixed token update issue
* version 1.5.3 deprecated creativesets methods from Apple Search Ads API v4
* version 1.5.2 fixed a bug in token refresh due to wrong status code
* version 1.5.1 handles API error with Exception
* version 1.2.1 refresh access_tokn only when needed
* version 1.1.1 added support for the v4 of the Apple Search Ads API
* version 0.7.1 fixed some issues with granularity
* version 0.1.1 Added granularity level reports