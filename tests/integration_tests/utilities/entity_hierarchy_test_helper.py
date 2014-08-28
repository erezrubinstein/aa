from common.utilities.date_utilities import LAST_ECONOMICS_DATE, LAST_ANALYTICS_DATE
from tests.integration_tests.utilities.data_access_misc_queries import insert_test_industry, insert_test_company


__author__ = 'vgold'


def link_industry_to_company(instance, ind_id, co_id):

    return instance.mds_access.call_add_link("industry", ind_id, "primary_industry",
                                             "company", co_id, "primary_industry_classification",
                                             "industry_classification", instance.context)


def link_company_to_company(instance, cid1, cid2, rel_type="retailer_branding", branding_type="primary"):

    if rel_type == "retailer_branding":
        if branding_type == "secondary":
            role_from = "secondary_parent"
            role_to = "secondary_banner"
        else:
            role_from = "retail_parent"
            role_to = "retail_segment"

    elif rel_type == "retailer_cooperatives":
        role_from = "cooperative_parent_non_owner"
        role_to = "cooperative_member_non_owner"

    elif rel_type == "equity_investment":
        role_from = "investment_firm"
        role_to = "portfolio_company"

    elif rel_type == "private_investment":
        role_from = "investor"
        role_to = "investment"

    else:
        raise Exception("Invalid relation type for companies")

    return instance.mds_access.call_add_link("company", cid1, role_from,
                                             "company", cid2, role_to, rel_type, instance.context)


def create_companies_and_relationships(instance):

    make_ind_rec = lambda x, y, z: dict(industry_name=x, industry_code=y, source_vendor=z)

    instance.industry_id1 = insert_test_industry("a", make_ind_rec("a", "a", "a"))
    instance.industry_id2 = insert_test_industry("b", make_ind_rec("b", "b", "b"))
    instance.industry_id3 = insert_test_industry("c", make_ind_rec("c", "c", "c"))

    make_co_rec = lambda x, y, z: dict(exchange=x, status=y, description=z, workflow_status="published" ,
                                       analytics={"stores": {"monthly": {"store_counts": [{"date": LAST_ANALYTICS_DATE, "value":19}]}},
                                                  "dates": {"monthly": {"stores": {"end": LAST_ANALYTICS_DATE},
                                                                        "competition": {"end": LAST_ANALYTICS_DATE},
                                                                        "economics": {"end": LAST_ECONOMICS_DATE}}}},
                                       collection={"dates": {"stores": ["2013-08-15", "2012-07-25"]}})

    # Parents
    instance.company_id1 = insert_test_company("A", "A", "retail_parent", **make_co_rec("A", "A", "A"))
    instance.company_id2 = insert_test_company("B", "B", "retail_parent", **make_co_rec("B", "B", "B"))
    instance.company_id7 = insert_test_company("G", "G", "retail_parent", **make_co_rec("G", "G", "G"))

    # Secondary Parents
    instance.company_id100 = insert_test_company("AAA", "AAA", "retail_parent", **make_co_rec("AAA", "AAA", "AAA"))

    # Coops
    instance.company_id3 = insert_test_company("C", "C", "retailer_cooperative", **make_co_rec("C", "C", "C"))
    instance.company_id4 = insert_test_company("D", "D", "retailer_cooperative", **make_co_rec("D", "D", "D"))
    instance.company_id9 = insert_test_company("I", "I", "retailer_cooperative", **make_co_rec("I", "I", "I"))

    # Owners
    instance.company_id5 = insert_test_company("E", "E", "retail_owner", **make_co_rec("E", "E", "E"))
    instance.company_id6 = insert_test_company("F", "F", "retail_owner", **make_co_rec("F", "F", "F"))
    instance.company_id8 = insert_test_company("H", "H", "retail_owner", **make_co_rec("H", "H", "H"))

    # Banners
    instance.company_id01 = insert_test_company("AA", "AA", "retail_banner", **make_co_rec("AA", "AA", "AA"))
    instance.company_id12 = insert_test_company("AB", "AB", "retail_banner", **make_co_rec("AB", "AB", "AB"))
    instance.company_id23 = insert_test_company("BC", "BC", "retail_banner", **make_co_rec("BC", "BC", "BC"))
    instance.company_id34 = insert_test_company("CD", "CD", "retail_banner", **make_co_rec("CD", "CD", "CD"))
    instance.company_id40 = insert_test_company("DA", "DA", "retail_banner", **make_co_rec("DA", "DA", "DA"))
    instance.company_id41 = insert_test_company("DB", "DB", "retail_banner", **make_co_rec("DB", "DB", "DB"))
    instance.company_id42 = insert_test_company("DC", "DC", "retail_banner", **make_co_rec("DC", "DC", "DC"))
    instance.company_id60 = insert_test_company("FA", "FA", "retail_banner", **make_co_rec("FA", "FA", "FA"))
    instance.company_id61 = insert_test_company("FB", "FB", "retail_banner", **make_co_rec("FB", "FB", "FB"))

    # Industries
    link_industry_to_company(instance, instance.industry_id1, instance.company_id1)
    link_industry_to_company(instance, instance.industry_id2, instance.company_id2)
    link_industry_to_company(instance, instance.industry_id3, instance.company_id3)

    # Parent links
    link_company_to_company(instance, instance.company_id1, instance.company_id01, rel_type="retailer_branding")
    link_company_to_company(instance, instance.company_id1, instance.company_id12, rel_type="retailer_branding")
    link_company_to_company(instance, instance.company_id2, instance.company_id12, rel_type="retailer_branding")
    link_company_to_company(instance, instance.company_id2, instance.company_id23, rel_type="retailer_branding")
    link_company_to_company(instance, instance.company_id7, instance.company_id42, rel_type="retailer_branding")

    # Secondary parent links
    link_company_to_company(instance, instance.company_id100, instance.company_id23, rel_type="retailer_branding",
                            branding_type="secondary")

    # Coop links
    link_company_to_company(instance, instance.company_id3, instance.company_id23, rel_type="retailer_cooperatives")
    link_company_to_company(instance, instance.company_id3, instance.company_id34, rel_type="retailer_cooperatives")
    link_company_to_company(instance, instance.company_id4, instance.company_id34, rel_type="retailer_cooperatives")
    link_company_to_company(instance, instance.company_id4, instance.company_id40, rel_type="retailer_cooperatives")
    link_company_to_company(instance, instance.company_id4, instance.company_id41, rel_type="retailer_cooperatives")
    link_company_to_company(instance, instance.company_id4, instance.company_id42, rel_type="retailer_cooperatives")
    link_company_to_company(instance, instance.company_id9, instance.company_id61, rel_type="retailer_cooperatives")

    # Owner links
    link_company_to_company(instance, instance.company_id5, instance.company_id1, rel_type="equity_investment")
    link_company_to_company(instance, instance.company_id6, instance.company_id2, rel_type="equity_investment")
    link_company_to_company(instance, instance.company_id8, instance.company_id7, rel_type="equity_investment")



def create_companies_and_relationships_just_parent(instance):

    # create a family with just 1 parent and no banners, etc.
    # parents are not usually in industries, so don't do that here either

    make_co_rec = lambda x, y, z: dict(exchange=x, status=y, description=z, workflow_status="published" ,
                                       analytics={"stores": {"monthly": {"store_counts": [{"date": LAST_ANALYTICS_DATE, "value":19}]}},
                                                  "dates": {"monthly": {"stores": {"end": LAST_ANALYTICS_DATE},
                                                                        "competition": {"end": LAST_ANALYTICS_DATE},
                                                                        "economics":{"end": LAST_ECONOMICS_DATE}}}})


    # Parents
    instance.company_id1 = insert_test_company("A", "A", "retail_parent", **make_co_rec("A", "A", "A"))


def create_companies_and_relationships_just_banner(instance):

    # create a family with just 1 banner and no parents, etc.
    # put the banner in a published-for-competition industry

    make_ind_rec = lambda x, y, z: dict(industry_name=x, industry_code=y, source_vendor=z, publish_competition_for_banners=True)

    instance.industry_id1 = insert_test_industry("a", make_ind_rec("a", "a", "a"))

    make_co_rec = lambda x, y, z: dict(exchange=x, status=y, description=z, workflow_status="published" ,
                                       analytics={"stores": {"monthly": {"store_counts": [{"date": LAST_ANALYTICS_DATE, "value":19}]}},
                                                  "dates": {"monthly": {"stores": {"end": LAST_ANALYTICS_DATE},
                                                                        "competition": {"end": LAST_ANALYTICS_DATE},
                                                                        "economics": {"end": LAST_ECONOMICS_DATE}}}},
                                       collection={"dates": {"stores": ["2013-08-15", "2012-07-25"]}})

    # Banners
    instance.company_id01 = insert_test_company("AA", "AA", "retail_banner", **make_co_rec("AA", "AA", "AA"))

    # Industries
    link_industry_to_company(instance, instance.industry_id1, instance.company_id01)

