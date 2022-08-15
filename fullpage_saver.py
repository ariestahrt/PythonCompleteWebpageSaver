from email.mime import base
from urllib.parse import urlparse, urljoin
import re
from pathlib import Path
import requests
import os
from urllib3.exceptions import InsecureRequestWarning
from urllib3 import disable_warnings
disable_warnings(InsecureRequestWarning)

def read_file(filename):
	try:
		with open(filename, 'r', encoding="utf8") as f:
			data = f.read()
		return data

	except Exception as ex:
		print("Error opening or reading input file: ", ex)
		exit()

def remove_dir(directory):
    try:
        directory = Path(directory)
        for item in directory.iterdir():
            if item.is_dir():
                remove_dir(item)
            else:
                item.unlink()
        directory.rmdir()
    except Exception as ex: # Ex always the exception
        print(f"[X] Failed to delete {directory}")

def create_dir(parrent_dir, new_dir):
    path = os.path.join(parrent_dir, new_dir)
    try:
        os.makedirs(path, exist_ok = True)
    except OSError as error:
        print("Failed creating dir")

def clean_backlash(url):
    while "//" in url: url=url.replace("//", "/")
    return url 

def download_local_asset(saved_path, base_url, file_path, asset_url, file_src, replace, assets_stats):
    if len(asset_url) <= 1: return

    if asset_url[0] == "/":
        asset_fullurl = urljoin(base_url, asset_url)
        asset_path = os.path.normpath(urlparse(asset_url).path).replace("\\", "/")
    else:
        asset_fullurl = urljoin(urljoin(base_url, file_path), asset_url)
        asset_path = os.path.normpath(urljoin(file_path, urlparse(asset_url).path)).replace("\\", "/")
    
    asset_dir = asset_path[:asset_path.rfind("/")]
    print("\t[!] asset_fullurl", asset_fullurl)
    print("\t[!] asset_path", asset_path)
    print("\t[!] asset_dir", asset_dir)

    # return
    # Fix path from current edited file_src
    old_content = read_file(file_src)
    new_content = old_content.replace(replace, replace.replace(asset_url, asset_path))
    with open(file_src, "w", encoding="utf-8") as f: f.write(new_content)

    assets_stats["total"] += 1
    print("\t[!] Downloading assets", asset_fullurl)
    req = requests.get(asset_fullurl, allow_redirects=False, verify=False)
    print(f"\t[!] RESP {req.status_code}")

    if req.status_code == 200:
        assets_stats["downloaded"] += 1
        create_dir(saved_path, asset_dir)
        with open(os.path.join(saved_path, asset_path), "wb") as f: f.write(req.content)

        # CHECK IF ASSET IS CSS AND HAS LOCAL URL
        parsed = urlparse(asset_fullurl)
        asset_filetype = parsed.path[parsed.path.rfind(".")+1:].lower()
        if asset_filetype == "css":
            pattern = r"(?<=url\().*?(?=\))"
            matches = re.finditer(pattern, req.text, re.MULTILINE)

            for match in matches:
                css_localcontent = match.group()
                css_localcontent_url = css_localcontent
                if css_localcontent[0]+css_localcontent[-1] in ['""', "''"]:
                    css_localcontent_url = css_localcontent[1:-1]

                if urlparse(css_localcontent_url).scheme == "":
                    print("\n\t[!] FOUND NEW ASSETS", css_localcontent_url)
                    css_parsed = urlparse(asset_fullurl)
                    css_file_path = os.path.normpath(css_parsed.path[:css_parsed.path.rfind("/")+1]).replace("\\", "/") + "/"

                    download_local_asset(asset_dir, base_url, css_file_path, css_localcontent_url, os.path.join(saved_path, asset_path), f"url({css_localcontent})", assets_stats)

def save_webpage(url, html_content="", saved_path="result"):
    print("[!] SAVING", url)
    remove_dir(saved_path)
    create_dir("", saved_path)

    parsed = urlparse(url)    
    base_url = parsed.scheme + "://" + parsed.netloc + "/"
    file_path = os.path.normpath(parsed.path[:parsed.path.rfind("/")+1]).replace("\\", "/") + "/"
    if len(file_path) > 0: file_path = file_path[1:]
        
    # Detect how many "../" needed to go to root folder
    count_parrentdir = file_path.count('/')
    index_path = os.path.join(saved_path, "index.html").replace("\\", "/")

    print("[!] base_url", base_url)
    print("[!] file_path", file_path)
    print("[!] count_parrentdir", count_parrentdir)

    if html_content == "":
        req = requests.get(url, verify=False, allow_redirects=False); req.encoding = "utf-8"; html_content=req.text
        # print(html_content)

    # Write HTML first
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    html_tag_cssjs = {
        "link" : "href",
        "script" : "src"
    }

    assets_stats = {"downloaded":0, "total":0}
    for tag in html_tag_cssjs.keys():
        pattern = fr"(?<=<{tag}).*?(?=>)"
        matches = re.finditer(pattern, html_content, re.MULTILINE)
        for match in matches:
            attr=html_tag_cssjs[tag]
            
            tag_attr = match.group()
            pattern2 = rf"(?<={attr}=(\"|')).*?(?=(\"|'))"
            matches2 = re.finditer(pattern2, tag_attr, re.MULTILINE)

            for match2 in matches2:
                asset_url = match2.group()
                lquote = match2.group(1)
                rquote = match2.group(2)

                replace = f"{lquote}{asset_url}{rquote}"
                print("\n[!] FOUND ASSET", replace)

                # DOWNLOAD ASSET IF LOCAL ASSET
                if urlparse(asset_url).scheme == "":
                    download_local_asset(saved_path, base_url, file_path, asset_url, index_path, replace, assets_stats)
    
    if assets_stats["total"] == 0: return 0.0
    return float(assets_stats["downloaded"]/assets_stats["total"])

# html_text = read_file("dom_sample.html")
url = "https://www.paypal.com/signin?"
# url = "https://www.amazon.com/ap/signin?openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.com%2F%3Fref_%3Dnav_custrec_signin&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=usflex&openid.mode=checkid_setup&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&"

asset_downloaded = save_webpage(url)
print("assets_downloaded", asset_downloaded)