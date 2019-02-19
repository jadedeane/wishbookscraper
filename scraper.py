import errno
import os
import requests


def scrape(catalog, year):
    print("Scraping catalog \"" + str(catalog) + "\" {year}\n".format(year=year))

    page = 1
    tries = 0

    while tries <= 4:
        tries += 1

        padded_page = str(page).zfill(4)
        url = \
            "http://www.wishbookweb.com/FB/{year}_{catalog}/files/assets/common/page-substrates/page{page}.jpg" \
            .format(year=year, catalog=catalog, page=padded_page)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0.3 Safari/605.1.15'
        }

        r = requests.get(url, headers=headers)
        if r.status_code != 200 and tries <= 1:
            print("This catalog likely wasn't found!\n")
            return
        elif r.status_code == 200:
            if page <= 1:
                try:
                    catalog_dir = str(catalog) + "_" + str(year)
                    os.makedirs(catalog_dir)
                except OSError as e:
                    if e.errno != errno.EEXIST:
                        raise
                page += 1
            if page >= 1:
                if r.status_code == 200:
                    filename = "./{catalog}_{year}/page{page}.jpg".format(catalog=catalog, year=year, page=page)
                    with open(filename, 'wb') as file:
                        file.write(r.content)
                        print(str(url) + " saved as " + str(filename) + "\n")
                        page += 1
                        tries = 0
        else:
            print(str(url) + " failed to download!\n")

    print("Finished catalog \"" + str(catalog) + "\" {year}\n".format(year=year))
    return


def main():
    os.chdir("./scrape")

    print("Starting fetch of Wishbookweb catalogs\n")

    catalogs = ["Sears_Wishbook", "Sears_Wish_Book", "Sears_Christmas_Book", "Sears_Christmas",
                "JCPenney_ChristmasCatalog",
                "Mongomery_Ward_Christmas_Catalog", "Wards_Christmas_Catalog"]

    for catalog in catalogs:
        year = 1937
        while year <= 2019:
            scrape(catalog, year)
            year += 1

    print("All done!\n")


if __name__ == "__main__":
    main()
