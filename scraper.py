import datetime
import errno
import os
import requests
import sys


def scrape(catalog, year):
    """
    Scrape catalog data for a given year.

    :param catalog: Catalog name, as indexed on site.
    :param year: 4-digit year as integer.
    :return:
    """
    print("Scraping catalog \"" + str(catalog) + "\" {year}\n".format(year=year))

    """Default catalog starting page number"""
    page = 1

    """
    Maximum times we'll attempt to scrape a page. 
    
    Catalog start: 
    If the first page of a catalog isn't found, we assume the catalog doesn't exist.
    
    Catalog end: 
    Given there's no reasonable way to ascertain in advance how many pages are in a given catalog, we more  or less 
    assume we're at the end of a catalog and should stop processing when subsequent pages aren't found.
    """
    max_page_tries = 4

    page_try = 0
    while page_try <= max_page_tries:
        page_try += 1

        """Scrapge a page"""
        padded_page = str(page).zfill(4)  # Pad page number with zeros to match page image URL (i.e., "page0001.jpg")
        url = \
            "http://www.wishbookweb.com/FB/{year}_{catalog}/files/assets/common/page-substrates/page{page}.jpg".format(
                year=year, catalog=catalog, page=padded_page)

        """Optionally present an alternate user agent"""
        headers = {}
        # headers.update(
        #     {
        #         "User-Agent":
        #             "Mozilla/5.0 (Macintosh; "
        #             "Intel Mac OS X 10_14_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0.3 Safari/605.1.15"
        #     }
        # )

        r = requests.get(url, headers=headers)
        if r.status_code != 200 and page_try <= 1:
            """If we fail to scrape the first page, the catalog likely doesn't exist."""
            print("Couldn't find page 1. This catalog likely doesn't exist!\n")
            return
        elif r.status_code == 200:
            """Create catalog directory if new catalog, otherwise add page image to existing directory"""
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
                        page_try = 0
        else:
            print(str(url) + " failed to download! (HTTP response code: {}\n").format(r.status_code)

    print("Finished catalog \"" + str(catalog) + "\" {year}\n".format(year=year))
    return


def main():
    print("Starting scrape of Wishbookweb catalogs\n")

    """These catalog names reference the directory structure/folder of the catalog"""
    catalogs = ["Sears_Wishbook", "Sears_Wish_Book", "Sears_Christmas_Book", "Sears_Christmas",
                "JCPenney_ChristmasCatalog", "Mongomery_Ward_Christmas_Catalog", "Wards_Christmas_Catalog"]

    for catalog in catalogs:
        year_start = 1937
        year_end = int(datetime.datetime.now().year)
        for year in range(year_start, year_end):
            scrape(catalog, year)

    print("All done!\n")


if __name__ == "__main__":
    if sys.version_info[0] < 3:
        raise Exception("Python 3+ is required!")
    main()
