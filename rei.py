"""
1. Choose a UI-based automation framework
    (such as Selenium, WebdriverIO, Cypress, Karate) as your test automation harness.
2. In a scripting language of your choice,
    automate the following user flow and its validation.
    BONUS: Use API requests when possible
    a. Navigate from https://www.rei.com/used to
        https://www.rei.com/used/shop/womens-footwear?category=Sandals%20%26%20Water%20Shoes
    b. Develop a means to land on a PDP
        (Product Description Page) such as https://www.rei.com/used/p/<product-name>/<parent_sku>?<color>
        BONUS POINTS for using a PDP where there are multiple color, size and item condition options.
    c. Add an item to cart
    d. Return to the Shop
    e. Select a different item
    f. Add an item to cart
    g. Visit the Cart page
    h. On the cart page, remove the lowest item from the list
    i. Click to checkout
    j. On the Shipping page, fill out the Email and Confirm Emails fields.
    k. END OF TEST

Deliverables
1. A written test plan identifying the use case(s) included in your automated test;
    use your preferred tool and format (eg, Google sheet, text file, etc).
2. Instructions for installing and setting up the testing harness framework.
3. Instructions to download your automation script.
4. Instructions to run your automation test.
"""
from playwright.sync_api import Playwright, sync_playwright
import requests
from random import choice
import json

ENTRY_URL = "https://www.rei.com/used"
CATEGORY_URL = "https://www.rei.com/used/shop/womens-footwear?category=Sandals%20%26%20Water%20Shoes"


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()

    page = context.new_page()  # open new page
    page.goto(ENTRY_URL)  # go to https://www.rei.com/used

    # with page.expect_request("https://reware-production.yerdlesite.com/v4/graphql?q=query-initApp") as expected:
    #     page.goto(ENTRY_URL)  # go to https://www.rei.com/used
    # print("a", expected.value.all_headers())
    # TRIED TO GET THE ORDER UUID FROM THE REQUEST HEADERS AS CREATED BY THE WEB APP, BUT IT ALWAYS RETURNED NULL,
    # SO I WOULD GUESS IT'S A SECURITY THING

    # def handle_route(route):
    #     print("a", route.request)
    #     route.continue_()
    # page.route("https://reware-production.yerdlesite.com/v4/graphql?q=query-initApp", handle_route)
    # ALSO TRIED TO ROUTE THE APP INIT REQUEST AND PULL THE POST DATA, BUT STILL DIDN'T GET ME WHAT I WANTED

    menu = page.locator("div.wrap >> div#menu-wrap.menu-wrap >> menu.navigation >> li:has-text(\"Women's\")")
    menu.first.click()

    category = page.locator("text=Sandals & Water Shoes")
    category.first.click()

    assert page.url == CATEGORY_URL

    num = page.locator("div.count").nth(0).text_content().strip(" matches")

    init_shop_ending = "query-initShop"
    init_shop_query = {"query": "query initShop($partner: String!, $slug: String!, $filters: [FacetLimitPublic], "
                                "$offset: Int, $limit: Int, $sort: String, $source: String, "
                                "$metadata: ShopMetadataInputTypePublic) {partner(uuid: $partner) {shop(slug: $slug, "
                                "filters: $filters, metadata: $metadata) {canonical(filters: $filters), headline, "
                                "subheadline, metaDescription, slug, title, facets(filters: $filters) {tag, title, "
                                "entries {name, count}, visibleLimit}, browse(filters: $filters, offset: $offset, "
                                "limit: $limit, sort: $sort, source: $source) {count, indexName, queryId, items , "
                                "{availableSizes, brand, brandDisplay, cmsData, color, displayColor, imageUrls, "
                                "originalPrice, parentSKU, price, priceRange, title, stackId, displayTitle, "
                                "objectType, pdpLink {path, url}}}}}}",
                       "variables": {"partner": "7d32ad83-330e-4ccc-ba03-3bb32ac113ae",
                                     "slug": "womens-footwear",
                                     "filters": [{"tag": "category", "name": "Sandals & Water Shoes"}],
                                     "offset": 0,
                                     "limit": num,
                                     "sort": "",
                                     "metadata": {}}}

    item_page_stack_ending = "query-itemPageStack"
    item_page_stack_query = {"query": "query itemPageStack($partner: String!, $parentSKU: String, "
                                      "$color: String, $shouldGetAllColors: Boolean, "
                                      "$shouldGetAllConditions: Boolean, $shouldCheckUnavailableSizes: Boolean) "
                                      "{partner(uuid: $partner) {itemPageStack(color: $color, parentSKU: $parentSKU) "
                                      "{allSizes, brand, brandDisplay, brandSlug, collection, color, "
                                      "configuredNewPrice, data, description, displayColor, displayTitle, imageUrls, "
                                      "parentSKU, pdpStyle, prevPrice, priceRange, prop65Code, prop65Message, "
                                      "redirectTo, stackId, title, fabric {code, name, content} facets {tag, "
                                      "name} wishColors {name, url, type} breadcrumbs {name, url, urlPath} offers "
                                      "{sku, price, image} pdpLink {canonical, path, url} "
                                      "availableSizes(shouldCheckUnavailableSizes: $shouldCheckUnavailableSizes, "
                                      "shouldGetAllColors: $shouldGetAllColors, "
                                      "shouldGetAllConditions: $shouldGetAllConditions) {color, condition, "
                                      "displayColor, imageUrls, itemStatus, notes, notesByNewLine, originalPrice, "
                                      "price, seasonDisplay, size, sku, surchargeAmount, uuid} breadcrumbs {name, "
                                      "url, urlPath}}}}",
                             "variables": {"color": None,
                                           "parentSKU": None,
                                           "partner": "7d32ad83-330e-4ccc-ba03-3bb32ac113ae",
                                           "shouldCheckUnavailableSizes": True,
                                           "shouldGetAllColors": True,
                                           "shouldGetAllConditions": True}}

    # should probably find a graphql client, but don't know enough about graphql, and too lazy. and this works

    url = "https://reware-production.yerdlesite.com/v4/graphql?q={}"

    get_all_items = requests.post(url=url.format(init_shop_ending), json=init_shop_query).json()

    items = get_all_items['data']['partner']['shop']['browse']['items']  # get list of all items

    items_with_multiple_sizes_and_or_colors = []
    for i in items:
        if len(i['availableSizes']) > 1:
            if any("EU" in x for x in i['availableSizes']):
                pass
            else:
                items_with_multiple_sizes_and_or_colors.append(i)

    # random_items = sample(items_with_multiple_sizes_and_or_colors, 2)  # get 2 random items
    cart = page.locator("text=Cart")  # find the cart element for later

    while cart.inner_text() != 2:
        random_item = choice(items_with_multiple_sizes_and_or_colors)  # get a random item

        item_brand = random_item['brand']  # get brand here because it's not stored in individual item size data
        # I didn't know there was a manufacturer named ALFWEAR and it pleases me deeply to know

        item_page_stack_query['variables']['color'] = random_item['color']
        item_page_stack_query['variables']['parentSKU'] = random_item['parentSKU']

        # get specific item data
        get_chosen_item = requests.post(url=url.format(item_page_stack_ending), json=item_page_stack_query)

        random_size = get_chosen_item.json()['data']['partner']['itemPageStack']['availableSizes']  # get list of sizes

        chosen_item = choice(random_size)
        chosen_item_image = json.loads(chosen_item["imageUrls"])["main"][0]  # stored as a string dict for some reason
        # get the main img file location so you can "compare visually" like a real boi

        filters = page.locator("div.all-filters")

        # filter for brand like a humanman (but really it's to reduce what's in results later)
        brand_section = filters.locator("section.Filter:has-text(\"Brand\")")
        brand_section.scroll_into_view_if_needed()
        if page.query_selector("div.all-filters >> section.Filter:has-text(\"Brand\") >> button"):  # if more options
            expand = brand_section.locator("button")
            expand.click()
        brand_filter = brand_section.locator(f"label:has-text(\"{item_brand}\")")
        brand_filter.scroll_into_view_if_needed()
        brand_filter.check()

        # filter for size
        size_section = filters.locator("section.Filter:has-text(\"Size\")")
        size_section.scroll_into_view_if_needed()
        if page.query_selector("div.all-filters >> section.Filter:has-text(\"Size\") >> button"):  # if more options
            expand = size_section.locator("button")
            expand.click()
        size_filter = size_section.locator(f"label:has-text(\"{chosen_item['size']}\")")
        size_filter.first.check()

        page.wait_for_selector("article.Results >> div.List >> ol")  # wait for the overlay to load
        items = page.query_selector_all("article.Results >> div.List >> ol >> li.TileItem")
        for i in items:
            # i.scroll_into_view_if_needed()  # occasionally errors with "element is not in DOM" so... yeah
            if chosen_item_image in i.inner_html():
                i.click()

        # select color, condition, size
        page.wait_for_selector("div.Item >> div.wrap >> article >> section")
        selections = page.locator("div.Item >> div.wrap >> article >> section")
        # colors = selections.locator("div.colors.is-left-scrolled.is-right-scrolled")

        # check for if there are multiple colors to choose from
        # multi_color = page.query_selector_all("div.colors.is-left-scrolled.is-right-scrolled >> article >> label")
        # if len(multi_color) > 1:
        #     all_colors = colors.locator("article")

        # CHOOSING A SIZE ALONE SHOULD GET ME CLOSE TO FEWER SELECTIONS NEEDED, PLUS I ALREADY FILTERED FOR IT
        sizes = page.query_selector_all("div.sizes >> article >> label")
        for size in sizes:
            print(size.get_attribute("aria-label"))

        # conditions = page.query_selector_all("div.conditions >> article >> label")
        # print("e", conditions)
        # condition = selections.locator("div.conditions")
        # print("e", condition.inner_text())

        add_to_cart_button = selections.locator("button.add-to-cart")

        if add_to_cart_button.is_enabled():    # tricksy hobbitses...the item could be in someone else's cart!
            add_to_cart_button.click()  # add it
            print("CART", cart.inner_text())

        page.go_back()
        continue
        # cycle through again

    # AS OF WEDNESDAY MORNING (11/17) REI IS GIVING ME A 403 SO I GUESS I'M DONE
    # MAYBE THEY THOUGHT I WAS HACKING WITH MY BAD GRAPHQL QUERIES AND BLOCKED MY IP

    # page.click("text=View your cart")
    # assert page.url == "https://www.rei.com/used/cart"
    # page.click(":nth-match(:text(\"Remove\"), 2)")  remove the later

    # page.click("text=Checkout")  # start checkout
    # assert page.url == "https://www.rei.com/used/checkout/shipping"
    # page.click("input[name=\"email\"]")
    # page.fill("input[name=\"email\"]", "reitest@reitest.com")
    # page.press("input[name=\"email\"]", "Tab")
    # page.fill("input[name=\"emailConfirm\"]", "reitest@reitest.com")

    context.close()  # you're done, rub your hands together as if you are clever
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
