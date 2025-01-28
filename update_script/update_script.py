"""
An update script that pulls the latest versions
of Android apps bundled in this module "FOSS App Stores".

List of packages to update:
- Aurora Store
- F-Droid
- F-Droid Privileged Extenstion
- FFUpdater

REFERENCE(s):
- https://regex101.com/r/oK55Tu/1

- https://regex101.com/r/cSZcQe/1 (noveau)
- https://stackoverflow.com/questions/5319922/check-if-a-word-is-in-a-string-in-python
- https://beautiful-soup-4.readthedocs.io/en/latest/#parsing-only-part-of-a-document
- https://stackoverflow.com/questions/5815747/beautifulsoup-getting-href
- https://python-forum.io/thread-35482.html
- https://realpython.com/python-download-file-from-url/#using-the-third-party-requests-library
- https://docs.python.org/3/library/functions.html#open
- https://stackoverflow.com/questions/33333711/what-is-difference-between-root-and-base-directory
- https://stackoverflow.com/questions/1855095/how-to-create-a-zip-archive-of-a-directory#25650295
- https://stackoverflow.com/questions/17140886/how-to-search-and-replace-text-in-a-file#17141572
"""
# For Regular Expressions
import re as regex

# For file management
import os
import json
import shutil
from zipfile import ZipFile as ZPF

# For HTTP requests & web scraping
from bs4 import BeautifulSoup as b_soup
from bs4 import SoupStrainer as html_filter
import requests
import urllib.request as url_lib

# Misc
import time

# Dictionary of places to grab APK's in case web scraping is required
#
download_places: dict = {
    "f_droid": {
        "link_app_page": "https://f-droid.org/en/packages/*",
        "link_app_regex": "^https://f-droid.org/repo/*_[0-9]+.apk$"
    }
}
# List of files to only include in zipping
zip_file_list: list[str] = [
    "META-INF",
    "system",
    "changelog.md",
    "customize.sh",
    "module.prop",
    "update.json"
]

def zip_directory(zip_file, directory):
    # Walk through the directory
    for foldername, subfolders, filenames in os.walk(directory):
        for filename in filenames:
            # Create the full file path
            file_path = os.path.join(foldername, filename)
            # Write the file to the zip file, using arcname to avoid the directory structure
            arcname = os.path.relpath(file_path, os.path.dirname(directory))
            zip_file.write(file_path, arcname=arcname)


def web_scraping(pkg_name: str, where_to_get: str):
    # Get HTML contents of website
    #
    link_app_page = (download_places[where_to_get]["link_app_page"]).replace("*", pkg_name)
    site_contents = requests.get(link_app_page).content
    
    # Grab all links, and get the latest version
    #
    link_app_regex = regex.compile((download_places[where_to_get]["link_app_regex"]).replace("*", pkg_name))
    links_only = html_filter(name = "a", href = link_app_regex)

    list_of_link_tags = b_soup(
        markup=site_contents,
        features="html.parser",
        parse_only=links_only)
   
    link_download: str = ""

    for link in list_of_link_tags:
            link_download = (link["href"])
            break
    
    return(link_download)



def update_json():
    # Variables
    #
    update_json: dict = ()
    module_prop: list = []
    json_name: str = "update.json"
    prop_name: str = "module.prop"

    # Import "update.json"
    #
    with open(file = ("../" + json_name), encoding='utf-8') as json_file:
        update_json = json.load(json_file)
    json_file.close()
    #
    ## Split ' update_json["version"] ' for correct version formatting
    #
    version_number_list: list[str] = (update_json["version"]).replace("v", "").split(".")
    version_number_pick: list[str] = [
         "v" + str(int(version_number_list[0]) + 1) + ".0.0",
         "v" + version_number_list[0] + "." + str(int(version_number_list[1]) + 1) + ".0",
         "v" + version_number_list[0] + "." + version_number_list[1] + "." + str(int(version_number_list[len(version_number_list) - 1]) + 1)
         ]
    #
    ## Inquire next version number
    #
    print("FOSS App Stores Magisk Module\n")
    print("Current Version: " + update_json["version"])
    time.sleep(1)
    print("\nHow should we update this package?")
    print("\t Option 1 — " + version_number_pick[0] + " — a MAJOR update")
    print("\t Option 2 — " + version_number_pick[1] + " — a MINOR update")
    print("\t Option 3 — " + version_number_pick[2] + " — a SUB-MINOR update")

    answer_raw: str = input("\nPlease enter your answer [1, 2, 3]: ")

    while (not answer_raw.isdigit() or (int(answer_raw) - 1) not in range (0, (len(version_number_list)))):
         answer_raw = input("\nPlease enter your answer [1, 2, 3]: ")
    time.sleep(1)

    answer: int = int(answer_raw) - 1
    print(answer)
    #
    ## Update Version Number
    #
    print("Updating version number . . .")
    version_number_list[answer] = str(int(version_number_list[answer]) + 1)
    match(answer):
        # Case 01: MAJOR Update
        case 0:
              for index, number in enumerate(version_number_list):
                if (index != 0): version_number_list[index] = "0"
        # Case 02: MINOR Update
        case 1:
              version_number_list[len(version_number_list) - 1] = "0"
        # Case 03: SUB-MINOR Update
        # Nothing to do
    #
    ## Update "version" property
    #
    update_json["version"] = version_number_pick[answer]
    #
    ## Update "versionCode" property
    #
    versionCode_new: str = ""

    for num in version_number_list:
         if int(num) in range (0, 10):
              versionCode_new += "0" + num
         else:
              versionCode_new += num
    
    update_json["versionCode"] = versionCode_new
    #
    ## Push new changes into the "update.json" file
    #
    with open(file = ("../" + json_name), mode = "w", encoding='utf-8') as json_file:
         json.dump(update_json, json_file, ensure_ascii=False)
    json_file.close()

    # Do the same in "module.prop" file
    #
    with open(file = ("../" + prop_name), mode="r") as file:
        module_prop = file.readlines()
    file.close()

    for i, line in enumerate(module_prop):
        if "version=" in line:
              module_prop[i] = "version=" + update_json["version"] + "\n"
        if "versionCode=" in line:
              module_prop[i] = "versionCode=" + update_json["versionCode"] + "\n"
    
    with open(file = ("../" + prop_name), mode="w") as file:
         file.writelines(module_prop)
    file.close()
    

    
    
    
         


def update_apps():
    app_infos : dict = ()
    download_link: str = ""
    with open("app_infos.json") as json_file:
         app_infos = json.load(json_file)

    for app in app_infos:
        # Check if the app's APK can be downloaded directly
        # Otherwise, perform web scraping to get the latest APK
        #
        

        if (app_infos[app]["download_directly"] is True):
             download_link = app_infos[app]["link"]
        else:
             download_link = web_scraping(
                  pkg_name = app_infos[app]["pkg_name"],
                  where_to_get = app_infos[app]["where_to_get"]
                  )
        # Then download the APK & place it to the correct location
        apk_file = requests.get(download_link)
        file_name: str = app_infos[app]["app_name"]+".apk"

        with open(file = file_name, mode="wb") as file:
             file.write(apk_file.content)

        # Next is to move file to appropriate location
        #

        """
        This will generate the following address:
        - "../system/product/[app or priv-app]/[app_name]/[app_name].apk"
        """
        file_destination: str = "../system/product/" + app_infos[app]["location"] + "/" + app_infos[app]["app_name"] + "/" + file_name
        os.replace(src = file_name, dst = file_destination)
        

def make_zip_file():
    file_name: str = "foss-app-stores"

    # Check if ZIP file already exists; then delete if it exists
    if os.path.exists("./" + file_name + ".zip"): os.remove("./" + file_name + ".zip")
    time.sleep(3)
    # Finally, make the ZIP file
    # shutil.make_archive(base_name = ("../" + file_name), format = "zip", root_dir="../")
    
    with ZPF(file_name + ".zip", mode="w") as zip:
        for file in zip_file_list:
            file_name = "../" + file

            if os.path.isdir(file_name):  # Check if it's a directory
                zip_directory(zip, file_name)  # Zip the entire directory
            else:
                zip.write(filename=("../" + file), arcname=file)  # Write the individual file
         
     


def main():
    delay: float = 2.0 
    # # Update "update.json" file
    # update_json()
    # time.sleep(delay)
    # print("\nUpdated 'update.json' successfully!\n")
    # time.sleep(delay)

    # # Update APK's
    # #
    # print("Updating APK's shortly...")
    # time.sleep(delay)
    # print("Updating APK's starts...")
    # update_apps()
    # print("\nUpdated APK's successfully!\n")
    # time.sleep(delay)
  
    # Finally, make a ZIP file compressing all changes
    print("Compiling changes into ZIP file shortly...")
    time.sleep(delay)
    print("Compiling changes into ZIP file starts...")
    make_zip_file()
    time.sleep(delay)
    print("\nCompiled changes into ZIP file successfully!")

main()