import random


def select_random_element(array, numb):
    """Selects two random elements from an array.

    Args:
        array: The input array.

    Returns:
        A tuple containing the two selected elements.
    """

    if len(array) < 2:
        raise ValueError("Array must have at least two elements.")

    if numb == 1:
        random_index = random.randint(0, len(array) - 1)
        return array[random_index]
    else:
        random.shuffle(array)
        return array[:2]


def _pre_init_hook(env):
    livechat = env["ir.module.module"].sudo().search([("name", "=", "im_livechat")])
    livechat.button_install()


def _post_init_hook(env):
    # NOTE Example Website Configuration
    # ----------------------- Sample Data to get -----------------------
    features_id = ['feature_page_about_us', 'feature_page_our_services', 'feature_page_pricing', 'feature_page_privacy_policy', 'feature_module_news', 'feature_module_success_stories', 'feature_module_career',
                   'feature_module_shop', 'feature_module_event', 'feature_module_forum', 'feature_module_live_chat', 'feature_module_elearning', 'feature_module_stores_locator']
    website_purpose = ['develop_brand', 'get_leads', 'sell_more', 'inform_customers', 'schedule_appointments']
    website_type = ['business', 'online_store', 'blog', 'event', 'elearning']

    features_to_install = []
    for id_name in select_random_element(features_id, 2):
        features_to_install.append(env.ref(f"website.{id_name}").id)

    website_configuration = {
        'selected_features': [],
        'industry_id': env["res.partner.industry"].sudo().search([('name', '=', 'Wholesale/Retail')], limit=1).id or env.ref("base.res_partner_industry_S").id,
        'industry_name': 'Furniture Store',
        'selected_palette': ['#d51961', '#3222c4', '#EBE9F9', '#FF0000', '#1B030C'],
        'theme_name': 'theme_default',
        'website_purpose': select_random_element(website_purpose, 1),
        'website_type': select_random_element(website_type, 1)
    }

    print("\nTO FIX When Addis Systems Registration Form is fully functional\n")
    print(website_configuration)
    print("\n")
    # env['website'].configurator_apply(selected_features=website_configuration['selected_features'], industry_id=website_configuration['industry_id'], industry_name=website_configuration['industry_name'], selected_palette=website_configuration['selected_palette'],
    #                                   theme_name=website_configuration['theme_name'], website_purpose=website_configuration['website_purpose'], website_type=website_configuration['website_type'])
