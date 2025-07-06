import requests
import csv
import bs4
import concurrent.futures

THREAD_NUMBER = 10
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"
HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept-Language": "en-US,en;q=0.9",
}


def get_html_page(url):
    res = requests.get(url=url, headers=HEADERS)
    return res.content


def get_product_price(soup):
    price = (
        soup.find("span", attrs={"class": "a-price-whole"})
        .text.strip()
        .replace(",", "")
        .replace(".", "")
    )

    try:
        return float(price)
    except ValueError:
        print("could not parse the price")
        exit()


def get_product_title(soup):
    title = soup.find(
        "h1", attrs={"id": "title", "class": "a-size-large a-spacing-none"}
    )
    try:
        t = title.text.strip()
    except ValueError:
        print("Could not parse the price")
        exit()
    return t


def get_product_rating(soup):
    rating = soup.find(
        "span", attrs={"class": "a-size-base a-color-base", "aria-hidden": "true"}
    ).text.strip()
    try:
        return float(rating)
    except ValueError:
        print("could not parse the price")
        exit()


def get_product_details(soup):
    details = {}
    div = soup.find("div", attrs={"id": "detailBullets_feature_div"})

    spans = div.find_all("span", class_="a-list-item")
    for span in spans:
        key_span = span.find("span", class_="a-text-bold")
        if key_span != None:
            value_span = key_span.find_next_sibling("span")
        if value_span != None:
            key = (
                key_span.text.replace("\u200f", "")
                .replace("\u200e", "")
                .replace(":", "")
                .strip()
            )
            value = (
                value_span.text.strip().replace("\u200f\n", "").replace("\u200e", "")
            )
            details[key] = value

    return details


def get_info(url, output):
    product_info = {}
    html = get_html_page(url)
    soup = bs4.BeautifulSoup(html, "lxml")

    product_info["price"] = get_product_price(soup)
    product_info["title"] = get_product_title(soup)
    product_info["rating"] = get_product_rating(soup)
    product_info.update(get_product_details(soup))
    output.append(product_info)


if __name__ == "__main__":
    output_data = []
    with open("amazon_products_url.csv", newline="") as csvfile:
        reader = list(csv.reader(csvfile, delimiter=","))

    with concurrent.futures.ThreadPoolExecutor(max_workers=THREAD_NUMBER) as executor:
        for row in reader:
            url = row[0]
            executor.submit(get_info, url, output_data)
    filename = "output.csv"
    with open(filename, "w") as output_file:
        writer = csv.writer(output_file)
        writer.writerow(output_data[0].keys())
        for product in output_data:
            writer.writerow(product.values())
