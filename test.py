import unittest

from searchads_api import SearchAdsAPI


class TestAPICalls(unittest.TestCase):
    def test_upper(self):
        api = SearchAdsAPI(2126300, "phiture.pem", "phiture.key", verbose=True)
        campaigns = api.get_campaigns_report_by_date(
            "2021-05-18",
            "2021-05-18",
            group_by="countryOrRegion",
            return_grand_totals=False,
        )
        print(campaigns)
        print()
        print(len(campaigns))

        print()
        for c in campaigns:
            if c["metadata"]["app"]["adamId"] == 1529233374:
                print(
                    c["total"]["localSpend"]["amount"]
                )  # , c["metadata"]["campaignName"])

        # # granularity api call
        # print()
        # for c in campaigns:
        #     for row in c["granularity"]:
        #         if c["metadata"]["app"]["adamId"] == 1529233374:
        #             if len(row) > 1:
        #                 #print(row)
        #                 print(row["localSpend"]["amount"])#, c["metadata"]["campaignName"])
        self.assertEqual("foo".upper(), "FOO")


if __name__ == "__main__":
    unittest.main()
