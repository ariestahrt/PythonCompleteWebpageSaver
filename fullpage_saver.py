from urllib.parse import urlparse, urljoin
import re
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

def create_dir(parrent_dir, new_dir):
    path = os.path.join(parrent_dir, new_dir)
    try:
        os.makedirs(path, exist_ok = True)
    except OSError as error:
        print("Failed creating dir")

def download_local_asset(saved_path, url_root, url_file_path, asset_url, file_src, replace):
    if asset_url[0] == "/": asset_fullurl = urljoin(url_root, asset_url)
    else: asset_fullurl = urljoin(url_file_path, asset_url)
    
    # Clean Asset URL from unwanted char like anchor in url
    asset_url = urlparse(asset_url).path

    if asset_url[0] == "/": asset_path = os.path.join(saved_path, asset_url[1:]).replace("\\", "/")
    else: asset_path = os.path.join(saved_path, asset_url).replace("\\", "/")

    # Fix root path
    if asset_url[0] == "/":
        old_content = read_file(file_src)
        new_content = old_content.replace(replace, replace.replace(asset_url, asset_url[1:]))
        with open(file_src, "w", encoding="utf-8") as f:
            f.write(new_content)

    print("Downloading assets", asset_fullurl, ":", end="")
    req = requests.get(asset_fullurl, allow_redirects=False, verify=False)
    print(req.status_code)

    if req.status_code == 200:
        asset_dir = asset_path[:asset_path.rfind("/")]
        
        print("ASSET_PATH", asset_path)
        print("ASSET_DIR", asset_dir)
        create_dir("", asset_dir)

        with open(asset_path, "wb") as f:
            f.write(req.content)

        # CHECK IF ASSET IS CSS AND HAS LOCAL URL
        parsed = urlparse(asset_fullurl)
        asset_filetype = parsed.path[parsed.path.rfind(".")+1:]
        if asset_filetype == "css":
            pattern = r"(?<=url\().*?(?=\))"
            matches = re.finditer(pattern, req.text, re.MULTILINE)

            for match in matches:
                css_localcontent = match.group()
                css_localcontent_url = css_localcontent
                if css_localcontent[0]+css_localcontent[-1] in ['""', "''"]:
                    css_localcontent_url = css_localcontent[1:-1]

                if urlparse(css_localcontent_url).scheme == "":
                    download_local_asset(asset_dir, url_root, url_file_path, css_localcontent_url, asset_path, f"url({css_localcontent})")

def save_webpage(url, html_content="", saved_path="result"):
    print("SAVING", url)
    parsed = urlparse(url)
    url_root = parsed.scheme + "://" + parsed.netloc + "/"
    url_file_path = parsed.scheme + "://" + parsed.netloc + "/" + parsed.path[:parsed.path.rfind("/")]

    if html_content == "":
        req = requests.get(url, verify=False, allow_redirects=False)
        req.encoding = "utf-8"
        html_content=req.text
        print(html_content)
    
    # Write HTML first
    with open(os.path.join(saved_path, "index.html").replace("\\", "/"), "w", encoding="utf-8") as f:
        f.write(html_content)

    html_tag_cssjs = {
        "link" : "href",
        "script" : "src"
    }

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
                print("\nFOUND", replace)

                # DOWNLOAD ASSET IF LOCAL ASSET
                if urlparse(asset_url).scheme == "":
                    download_local_asset(saved_path, url_root, url_file_path, asset_url, os.path.join(saved_path, "index.html"), replace)
                    

url = "https://openphish.com/"
save_webpage(url)