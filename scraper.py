"""
Simple script to scrape http://www.wishbookweb.com catalogs. Defaults to 1min and 1sec delays between catalog and page
scrapes, respectively. No performance considerations have been made. The combination of these serves to impact the site
as minimally as possible.
"""

import errno
import os
import requests
import sys
from time import sleep


def scrape_catalog(store_name, catalog, year):
    """
    Scrape catalog data for a given year.

    :param store_name: Name of store.
    :param catalog: Catalog name, as indexed on site.
    :param year: 4-digit year as integer.
    :return:
    """

    print("Scraping catalog \"" + str(catalog) + "\" {}\n".format(year))

    """
    Maximum times we'll attempt to scrape a page. 
    
    Catalog start: 
    If the first page of a catalog isn't found, we assume the catalog doesn't exist.
    
    Catalog end: 
    Given there's no reasonable way to ascertain in advance how many pages are in a given catalog, we more  or less 
    assume we're at the end of a catalog and should stop processing when subsequent pages aren't found.
    """

    max_page_tries = 4
    page = 1  # Default catalog starting page number

    page_try = 0
    while page_try <= max_page_tries:
        page_try += 1
        padded_page = str(page).zfill(4)  # Pad page number with zeros to match page image URL (i.e., "page0001.jpg")
        url = \
            "http://www.wishbookweb.com/FB/{}_{}/files/assets/common/page-substrates/page{}.jpg"\
            .format(year, catalog, padded_page)
        r = requests.get(url)
        if r.status_code != 200 and page_try <= 1:
            """If we fail to scrape the first page, the catalog likely doesn't exist."""
            print("Couldn't find page {}. This catalog likely doesn't exist!\n".format(page))
            return
        elif r.status_code == 200:
            """Create catalog directory if new catalog, otherwise add page image to existing directory"""
            if page <= 1:
                try:
                    os.makedirs(store_name)
                except OSError as e:
                    if e.errno != errno.EEXIST:
                        raise
                page += 1
            if page >= 1:
                if r.status_code == 200:
                    filename = "./{}/{}_{}_page{}.jpg".format(store_name, catalog, year, page)
                    with open(filename, 'wb') as file:
                        file.write(r.content)
                        print(str(url) + " saved as " + str(filename) + "\n")
                        page += 1
                        page_try = 0
        else:
            print(str(url) + " failed to download! (HTTP response code: {}\n").format(r.status_code)
        sleep(1)  # Default sleep for 1sec between pages

    print("Finished {} catalog {} {}\n".format(store_name, catalog, year))
    return


if __name__ == "__main__":

    if sys.version_info[0] < 3:
        raise Exception("Python 3+ is required!")

    print("Starting scrape of Wishbookweb catalogs\n")

    """
    These catalog names reference the directory structure/folder of the catalog, and where they include spelling errors
    reflect catalog directory errors on the site itself. Year ranges reflect year ranges as available on the site.
    """
    catalogs = \
        {
            'sears': {
                'store_name': "Sears",
                'years': "1937-1991",
                'catalog_names': [
                    "Sears_Wishbook",
                    "Sears_Wish_Book",
                    "Sears_Christmas_Book",
                    "Sears_Christmas"
                ]
            },
            'jc_penny': {
                'store_name': "JC Penny",
                'years': "1967-1996",
                'catalog_names': [
                    "JCPenney_ChristmasCatalog",
                ]
            },
            'montgomery_ward': {
                'store_name': "Montgomery Ward",
                'years': "1944-1984",
                'catalog_names': [
                    "Mongomery_Ward_Christmas_Catalog",
                    "Wards_Christmas_Catalog"
                ]
            }
        }

    for k, v in catalogs.items():
        years = str(v['years'])
        year_start, year_end = years.split('-', 1)
        for year in range(int(year_start), int(year_end)):
            for catalog in v['catalog_names']:
                scrape_catalog(v['store_name'], catalog, year)
                sleep(60)  # Default sleep for 1min between catalogs

    print("All done!\n")
