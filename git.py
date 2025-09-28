import os
import json
import requests
import time
import shutil
import webbrowser
import sys
import subprocess
from datetime import datetime
from tabulate import tabulate
from tqdm import tqdm
import platform
from colorama import init, Fore, Style, Back

# مقداردهی اولیه colorama
init()

# تنظیمات اولیه
HISTORY_FILE = "github_downloader_history.json"
GITHUB_API_URL = "https://api.github.com/repos"
DOWNLOADS_DIR = "downloads"
REPO_URL = "https://github.com/cinaishere/git_downloader"
SCRIPT_NAME = "git.py"
UPDATE_SCRIPT_NAME = "git_update.py"

# پاک کردن کنسول
def clear_console():
    os.system('cls' if platform.system() == 'Windows' else 'clear')

# نمایش لوگوی ASCII با رنگ
def show_logo():
    logo = f"""
//                                                                                             
//    8 888888888o.      8 8888888888                 ,o888888o.     8 8888 8888888 8888888888 
//    8 8888    `^888.   8 8888                      8888     `88.   8 8888       8 8888       
//    8 8888        `88. 8 8888                   ,8 8888       `8.  8 8888       8 8888       
//    8 8888         `88 8 8888                   88 8888            8 8888       8 8888       
//    8 8888          88 8 888888888888           88 8888            8 8888       8 8888       
//    8 8888          88 8 8888                   88 8888            8 8888       8 8888       
//    8 8888         ,88 8 8888                   88 8888   8888888  8 8888       8 8888       
//    8 8888        ,88' 8 8888                   `8 8888       .8'  8 8888       8 8888       
//    8 8888    ,o88P'   8 8888                      8888     ,88'   8 8888       8 8888       
//    8 888888888P'      8 888888888888               `8888888P'     8 8888       8 8888       
          {Fore.YELLOW}GITHUB REPO DOWNLOADER v1.0 | Developed by Cina! De Co.{Style.RESET_ALL}
    """
    print(logo)

# تابع برای ایجاد باکس شماره‌دار
def create_numbered_box(number, title, width=45):
    box_top = f"{Fore.YELLOW}╔{'═' * (width-2)}╗{Style.RESET_ALL}"
    box_middle = f"{Fore.YELLOW}║{Style.RESET_ALL} {Fore.YELLOW}[{number}]{Style.RESET_ALL} {title.ljust(width-8)}{Fore.YELLOW}║{Style.RESET_ALL}"
    box_bottom = f"{Fore.YELLOW}╚{'═' * (width-2)}╝{Style.RESET_ALL}"
    
    return f"{box_top}\n{box_middle}\n{box_bottom}"

# نمایش منوی اصلی با رنگ و باکس‌های شماره‌دار
def show_menu():
    menu_title = f"\n{Fore.YELLOW}{'MAIN MENU'.center(50)}{Style.RESET_ALL}\n"
    
    menu_items = [
        ("1", "Download Repository"),
        ("2", "View Download History"),
        ("3", "Manage Downloads"),
        ("4", "Check for Updates"),
        ("5", "Update Announcement"),
        ("6", "Exit")
    ]
    
    menu_content = ""
    for number, title in menu_items:
        menu_content += create_numbered_box(number, title) + "\n"
    
    print(menu_title + menu_content)

# نمایش منوی اطلاعیه‌ها با رنگ و باکس‌های شماره‌دار
def show_announce_menu():
    menu_title = f"{Fore.YELLOW}{'=' * 50}{Style.RESET_ALL}"
    menu_title += f"\n{Fore.YELLOW}{'UPDATE ANNOUNCEMENT'.center(50)}{Style.RESET_ALL}"
    menu_title += f"\n{Fore.YELLOW}{'=' * 50}{Style.RESET_ALL}\n"
    
    menu_items = [
        ("1", "Visit Website"),
        ("2", "Join Telegram Channel"),
        ("3", "Back to Main Menu")
    ]
    
    menu_content = ""
    for number, title in menu_items:
        menu_content += create_numbered_box(number, title) + "\n"
    
    print(menu_title + menu_content)

# ایجاد فایل تاریخچه اگر وجود نداشته باشد
def init_history():
    if not os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'w') as f:
            json.dump({"history": []}, f)

# افزودن به تاریخچه
def add_to_history(repo_url, downloaded_files, local_dir):
    init_history()
    with open(HISTORY_FILE, 'r+') as f:
        data = json.load(f)
        new_entry = {
            "repo_url": repo_url,
            "local_dir": local_dir,
            "downloaded_files": downloaded_files,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        data["history"].append(new_entry)
        f.seek(0)
        json.dump(data, f, indent=4)

# حذف از تاریخچه
def remove_from_history(local_dir, filename=None):
    init_history()
    with open(HISTORY_FILE, 'r+') as f:
        data = json.load(f)
        history = data.get('history', [])
        
        if filename is not None:
            # حذف فایل خاص از تاریخچه
            for entry in history:
                if entry.get('local_dir') == local_dir:
                    downloaded_files = entry.get('downloaded_files', [])
                    # حذف فایل با نام مشخص
                    entry['downloaded_files'] = [f for f in downloaded_files if f.get('name') != filename]
        else:
            # حذف کل پوشه از تاریخچه
            history = [entry for entry in history if entry.get('local_dir') != local_dir]
            data['history'] = history
        
        f.seek(0)
        json.dump(data, f, indent=4)
        f.truncate()

# دریافت اطلاعات ریپازیتوری از API
def get_repo_info(owner, repo):
    url = f"{GITHUB_API_URL}/{owner}/{repo}/contents"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"{Fore.RED}Error fetching repository info: {e}{Style.RESET_ALL}")
        return None

# نمایش انیمیشن لودینگ با رنگ
def show_loading():
    for _ in tqdm(range(100), desc=f"{Fore.YELLOW}Loading Repository{Style.RESET_ALL}", ncols=70, bar_format="{l_bar}%s{bar}%s{r_bar}" % (Fore.YELLOW, Style.RESET_ALL)):
        time.sleep(0.02)

# دانلود فایل
def download_file(url, filename, path):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        filepath = os.path.join(path, filename)
        os.makedirs(path, exist_ok=True)
        
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    except Exception as e:
        print(f"{Fore.RED}Error downloading {filename}: {e}{Style.RESET_ALL}")
        return False

# دانلود کل ریپازیتوری
def download_repo_contents(owner, repo, base_path):
    contents = get_repo_info(owner, repo)
    if not contents:
        return []
    
    downloaded_files = []
    
    for item in contents:
        name = item['name']
        item_type = item['type']
        
        if item_type == 'file':
            download_url = item['download_url']
            if download_file(download_url, name, base_path):
                downloaded_files.append({
                    "name": name,
                    "size": item.get('size', 0),
                    "type": "file"
                })
        elif item_type == 'dir':
            dir_path = os.path.join(base_path, name)
            sub_files = download_repo_contents(owner, repo + f"/contents/{name}", dir_path)
            downloaded_files.extend(sub_files)
    
    return downloaded_files

# نمایش فایل‌های ریپازیتوری با رنگ
def display_repo_files(contents):
    if not contents:
        print(f"{Fore.YELLOW}No files found in repository.{Style.RESET_ALL}")
        return
    
    headers = [f"{Fore.YELLOW}#{Style.RESET_ALL}", 
               f"{Fore.YELLOW}Name{Style.RESET_ALL}", 
               f"{Fore.YELLOW}Type{Style.RESET_ALL}", 
               f"{Fore.YELLOW}Size (KB){Style.RESET_ALL}"]
    table_data = []
    
    for idx, item in enumerate(contents, 1):
        name = item['name']
        item_type = item['type']
        size_kb = round(item.get('size', 0) / 1024, 2) if item_type == 'file' else 0
        table_data.append([idx, name, item_type, size_kb])
    
    print(f"\n{Fore.YELLOW}Repository Contents:{Style.RESET_ALL}")
    print(tabulate(table_data, headers=headers, tablefmt="grid"))

# دانلود ریپازیتوری
def download_repository():
    repo_url = input(f"{Fore.YELLOW}Enter GitHub repository URL (e.g., https://github.com/owner/repo): {Style.RESET_ALL}").strip()
    
    # استخراج نام کاربر و ریپازیتوری
    parts = repo_url.split('/')
    if len(parts) < 5 or 'github.com' not in parts:
        print(f"{Fore.RED}Invalid GitHub URL!{Style.RESET_ALL}")
        return
    
    owner = parts[-2]
    repo = parts[-1]
    
    # نمایش لودینگ
    show_loading()
    
    # دریافت اطلاعات ریپازیتوری
    contents = get_repo_info(owner, repo)
    if not contents:
        return
    
    # نمایش فایل‌ها
    display_repo_files(contents)
    
    # دریافت انتخاب کاربر
    while True:
        choice = input(f"\n{Fore.YELLOW}Enter file number to download (0 for all files, 'b' to back): {Style.RESET_ALL}").strip()
        
        if choice.lower() == 'b':
            return
        elif choice == '0':
            # دانلود کل ریپازیتوری
            repo_name = repo.split('/')[-1]
            base_path = os.path.join(DOWNLOADS_DIR, repo_name)
            print(f"\n{Fore.YELLOW}Downloading entire repository to: {base_path}{Style.RESET_ALL}")
            
            downloaded_files = download_repo_contents(owner, repo, base_path)
            if downloaded_files:
                print(f"\n{Fore.GREEN}Successfully downloaded {len(downloaded_files)} files!{Style.RESET_ALL}")
                add_to_history(repo_url, downloaded_files, repo_name)
            else:
                print(f"{Fore.RED}Download failed!{Style.RESET_ALL}")
            return
        else:
            try:
                file_idx = int(choice) - 1
                if 0 <= file_idx < len(contents):
                    selected_file = contents[file_idx]
                    
                    if selected_file['type'] != 'file':
                        print(f"{Fore.RED}'{selected_file['name']}' is a directory. Only files can be downloaded individually. Use '0' for directories.{Style.RESET_ALL}")
                        continue
                    
                    # دانلود فایل
                    filename = selected_file['name']
                    download_url = selected_file['download_url']
                    size_kb = round(selected_file.get('size', 0) / 1024, 2)
                    
                    print(f"\n{Fore.YELLOW}Downloading: {filename} ({size_kb} KB){Style.RESET_ALL}")
                    repo_name = repo.split('/')[-1]
                    save_path = os.path.join(DOWNLOADS_DIR, repo_name)
                    
                    if download_file(download_url, filename, save_path):
                        print(f"{Fore.GREEN}Successfully downloaded: {filename}{Style.RESET_ALL}")
                        add_to_history(repo_url, [{
                            "name": filename,
                            "size": selected_file.get('size', 0),
                            "type": "file"
                        }], repo_name)
                    else:
                        print(f"{Fore.RED}Download failed!{Style.RESET_ALL}")
                    return
                else:
                    print(f"{Fore.RED}Invalid selection! Please enter a number between 1 and {len(contents)}.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED}Please enter a valid number!{Style.RESET_ALL}")

# نمایش تاریخچه دانلودها
def show_history():
    init_history()
    
    with open(HISTORY_FILE, 'r') as f:
        data = json.load(f)
        history = data.get('history', [])
    
    if not history:
        print(f"\n{Fore.YELLOW}No download history found!{Style.RESET_ALL}")
        return
    
    # نمایش تاریخچه
    headers = [f"{Fore.YELLOW}#{Style.RESET_ALL}", 
               f"{Fore.YELLOW}Repository{Style.RESET_ALL}", 
               f"{Fore.YELLOW}Files Count{Style.RESET_ALL}", 
               f"{Fore.YELLOW}Date{Style.RESET_ALL}"]
    table_data = []
    
    for idx, entry in enumerate(history, 1):
        repo_url = entry['repo_url']
        repo_name = repo_url.split('/')[-1]
        files_count = len(entry['downloaded_files'])
        date = entry['timestamp']
        table_data.append([idx, repo_name, files_count, date])
    
    print(f"\n{Fore.YELLOW}Download History:{Style.RESET_ALL}")
    print(tabulate(table_data, headers=headers, tablefmt="grid"))
    
    # انتخاب ریپازیتوری برای نمایش جزئیات
    while True:
        choice = input(f"\n{Fore.YELLOW}Enter repository number to view details (0 to back): {Style.RESET_ALL}").strip()
        
        if choice == '0':
            return
        
        try:
            repo_idx = int(choice) - 1
            if 0 <= repo_idx < len(history):
                selected_entry = history[repo_idx]
                repo_url = selected_entry['repo_url']
                files = selected_entry['downloaded_files']
                
                # نمایش جزئیات فایل‌ها
                print(f"\n{Fore.YELLOW}Files from: {repo_url}{Style.RESET_ALL}")
                headers = [f"{Fore.YELLOW}#{Style.RESET_ALL}", 
                           f"{Fore.YELLOW}File Name{Style.RESET_ALL}", 
                           f"{Fore.YELLOW}Type{Style.RESET_ALL}", 
                           f"{Fore.YELLOW}Size (KB){Style.RESET_ALL}"]
                table_data = []
                
                for idx, file in enumerate(files, 1):
                    name = file['name']
                    file_type = file.get('type', 'file')
                    size_kb = round(file.get('size', 0) / 1024, 2)
                    table_data.append([idx, name, file_type, size_kb])
                
                print(tabulate(table_data, headers=headers, tablefmt="grid"))
                return
            else:
                print(f"{Fore.RED}Invalid selection! Please enter a number between 1 and {len(history)}.{Style.RESET_ALL}")
        except ValueError:
            print(f"{Fore.RED}Please enter a valid number!{Style.RESET_ALL}")

# مدیریت دانلودها
def manage_downloads():
    while True:
        clear_console()
        show_logo()
        
        menu_title = f"{Fore.YELLOW}{'=' * 50}{Style.RESET_ALL}"
        menu_title += f"\n{Fore.YELLOW}{'MANAGE DOWNLOADS'.center(50)}{Style.RESET_ALL}"
        menu_title += f"\n{Fore.YELLOW}{'=' * 50}{Style.RESET_ALL}\n"
        
        menu_items = [
            ("1", "View Downloaded Files"),
            ("2", "Delete Downloaded Files"),
            ("3", "Back to Main Menu")
        ]
        
        menu_content = ""
        for number, title in menu_items:
            menu_content += create_numbered_box(number, title) + "\n"
        
        print(menu_title + menu_content)
        
        choice = input(f"\n{Fore.YELLOW}Enter your choice: {Style.RESET_ALL}").strip()
        
        if choice == '1':
            view_downloaded_files()
        elif choice == '2':
            delete_downloaded_files()
        elif choice == '3':
            return
        else:
            print(f"{Fore.RED}Invalid choice! Please try again.{Style.RESET_ALL}")
        
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

# نمایش فایل‌های دانلود شده
def view_downloaded_files():
    if not os.path.exists(DOWNLOADS_DIR):
        print(f"\n{Fore.YELLOW}No downloaded files found.{Style.RESET_ALL}")
        return
    
    print(f"\n{Fore.YELLOW}Downloaded Files:{Style.RESET_ALL}")
    
    # دریافت لیست پوشه‌ها و فایل‌ها
    repos = []
    for item in os.listdir(DOWNLOADS_DIR):
        item_path = os.path.join(DOWNLOADS_DIR, item)
        if os.path.isdir(item_path):
            repos.append((item, 'directory', 0))
        else:
            size = os.path.getsize(item_path) / 1024  # KB
            repos.append((item, 'file', size))
    
    if not repos:
        print(f"{Fore.YELLOW}No downloaded files found.{Style.RESET_ALL}")
        return
    
    # نمایش در جدول
    headers = [f"{Fore.YELLOW}#{Style.RESET_ALL}", 
               f"{Fore.YELLOW}Name{Style.RESET_ALL}", 
               f"{Fore.YELLOW}Type{Style.RESET_ALL}", 
               f"{Fore.YELLOW}Size (KB){Style.RESET_ALL}"]
    table_data = []
    
    for idx, (name, item_type, size) in enumerate(repos, 1):
        table_data.append([idx, name, item_type, round(size, 2)])
    
    print(tabulate(table_data, headers=headers, tablefmt="grid"))

# حذف فایل‌های دانلود شده
def delete_downloaded_files():
    if not os.path.exists(DOWNLOADS_DIR):
        print(f"\n{Fore.YELLOW}No downloaded files found.{Style.RESET_ALL}")
        return
    
    print(f"\n{Fore.YELLOW}Downloaded Files:{Style.RESET_ALL}")
    
    # دریافت لیست پوشه‌ها و فایل‌ها
    repos = []
    for item in os.listdir(DOWNLOADS_DIR):
        item_path = os.path.join(DOWNLOADS_DIR, item)
        if os.path.isdir(item_path):
            repos.append((item, 'directory', 0))
        else:
            size = os.path.getsize(item_path) / 1024  # KB
            repos.append((item, 'file', size))
    
    if not repos:
        print(f"{Fore.YELLOW}No downloaded files found.{Style.RESET_ALL}")
        return
    
    # نمایش در جدول
    headers = [f"{Fore.YELLOW}#{Style.RESET_ALL}", 
               f"{Fore.YELLOW}Name{Style.RESET_ALL}", 
               f"{Fore.YELLOW}Type{Style.RESET_ALL}", 
               f"{Fore.YELLOW}Size (KB){Style.RESET_ALL}"]
    table_data = []
    
    for idx, (name, item_type, size) in enumerate(repos, 1):
        table_data.append([idx, name, item_type, round(size, 2)])
    
    print(tabulate(table_data, headers=headers, tablefmt="grid"))
    
    # دریافت انتخاب کاربر
    while True:
        choice = input(f"\n{Fore.YELLOW}Enter file number to delete (0 for all files, 'b' to back): {Style.RESET_ALL}").strip()
        
        if choice.lower() == 'b':
            return
        elif choice == '0':
            # حذف کل فایل‌ها
            confirm = input(f"{Fore.YELLOW}Are you sure you want to delete all downloaded files? (y/n): {Style.RESET_ALL}").strip().lower()
            if confirm == 'y':
                try:
                    shutil.rmtree(DOWNLOADS_DIR)
                    os.makedirs(DOWNLOADS_DIR, exist_ok=True)
                    # حذف کل تاریخچه
                    init_history()
                    with open(HISTORY_FILE, 'w') as f:
                        json.dump({"history": []}, f)
                    print(f"\n{Fore.GREEN}All downloaded files and history deleted successfully!{Style.RESET_ALL}")
                except Exception as e:
                    print(f"\n{Fore.RED}Error deleting files: {e}{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}Operation cancelled.{Style.RESET_ALL}")
            return
        else:
            try:
                file_idx = int(choice) - 1
                if 0 <= file_idx < len(repos):
                    selected_file = repos[file_idx][0]
                    file_path = os.path.join(DOWNLOADS_DIR, selected_file)
                    
                    confirm = input(f"{Fore.YELLOW}Are you sure you want to delete '{selected_file}'? (y/n): {Style.RESET_ALL}").strip().lower()
                    if confirm == 'y':
                        try:
                            if os.path.isdir(file_path):
                                shutil.rmtree(file_path)
                                # حذف کل پوشه از تاریخچه
                                remove_from_history(selected_file)
                            else:
                                os.remove(file_path)
                                # حذف فایل از تاریخچه
                                # برای فایل‌های سطح بالا، نیاز به بررسی داریم
                                # در اینجا فرض می‌کنیم فایل‌های سطح بالا متعلق به هیچ ریپازیتوری خاصی نیستند
                                # بنابراین فقط از دیسک حذف می‌شوند
                            print(f"\n{Fore.GREEN}'{selected_file}' deleted successfully!{Style.RESET_ALL}")
                        except Exception as e:
                            print(f"\n{Fore.RED}Error deleting file: {e}{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.YELLOW}Operation cancelled.{Style.RESET_ALL}")
                    return
                else:
                    print(f"{Fore.RED}Invalid selection! Please enter a number between 1 and {len(repos)}.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED}Please enter a valid number!{Style.RESET_ALL}")

# مدیریت منوی اطلاعیه‌ها
def announce_menu():
    while True:
        clear_console()
        show_logo()
        show_announce_menu()
        
        choice = input(f"\n{Fore.YELLOW}Enter your choice: {Style.RESET_ALL}").strip()
        
        if choice == '1':
            print(f"\n{Fore.YELLOW}Opening website...{Style.RESET_ALL}")
            webbrowser.open('https://supdechatnone.liara.run/user')
        elif choice == '2':
            print(f"\n{Fore.YELLOW}Opening Telegram channel...{Style.RESET_ALL}")
            webbrowser.open('https://t.me/Hidenchatnone')
        elif choice == '3':
            return
        else:
            print(f"{Fore.RED}Invalid choice! Please try again.{Style.RESET_ALL}")
        
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

# بررسی وجود به‌روزرسانی
def check_for_updates():
    clear_console()
    show_logo()
    
    print(f"\n{Fore.YELLOW}Checking for updates...{Style.RESET_ALL}")
    
    try:
        # دریافت اطلاعات ریپازیتوری
        repo_owner = "cinaishere"
        repo_name = "git_downloader"
        
        # دریافت اطلاعات فایل git.py از ریپازیتوری
        api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{SCRIPT_NAME}"
        response = requests.get(api_url)
        response.raise_for_status()
        file_info = response.json()
        
        # دریافت تاریخ آخرین تغییر فایل در گیت‌هاب
        github_date_str = file_info.get('commit', {}).get('committer', {}).get('date', '')
        github_date = datetime.strptime(github_date_str, "%Y-%m-%dT%H:%M:%SZ")
        
        # دریافت تاریخ تغییر فایل محلی
        local_file_path = os.path.abspath(__file__)
        local_mtime = os.path.getmtime(local_file_path)
        local_date = datetime.fromtimestamp(local_mtime)
        
        print(f"\n{Fore.YELLOW}GitHub version: {github_date.strftime('%Y-%m-%d %H:%M:%S')}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Local version: {local_date.strftime('%Y-%m-%d %H:%M:%S')}{Style.RESET_ALL}")
        
        if github_date > local_date:
            print(f"\n{Fore.GREEN}A new version is available!{Style.RESET_ALL}")
            
            choice = input(f"\n{Fore.YELLOW}Do you want to download the latest version? (y/n): {Style.RESET_ALL}").strip().lower()
            if choice == 'y':
                # دانلود فایل جدید
                download_url = file_info.get('download_url', '')
                print(f"\n{Fore.YELLOW}Downloading update...{Style.RESET_ALL}")
                
                try:
                    response = requests.get(download_url)
                    response.raise_for_status()
                    
                    # ذخیره فایل جدید با نام موقت
                    with open(UPDATE_SCRIPT_NAME, 'wb') as f:
                        f.write(response.content)
                    
                    print(f"\n{Fore.GREEN}Update downloaded successfully!{Style.RESET_ALL}")
                    
                    # ایجاد اسکریپت به‌روزرسانی
                    create_update_script()
                    
                    print(f"\n{Fore.YELLOW}The application will restart after the update.{Style.RESET_ALL}")
                    print(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
                    input()
                    
                    # اجرای اسکریپت به‌روزرسانی و خروج از برنامه
                    if platform.system() == 'Windows':
                        subprocess.Popen(['update_script.bat'])
                    else:
                        subprocess.Popen(['bash', 'update_script.sh'])
                    
                    sys.exit(0)
                except Exception as e:
                    print(f"\n{Fore.RED}Error downloading update: {e}{Style.RESET_ALL}")
            else:
                print(f"\n{Fore.YELLOW}Update cancelled.{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.GREEN}You are using the latest version!{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}Error checking for updates: {e}{Style.RESET_ALL}")
    
    input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

# ایجاد اسکریپت به‌روزرسانی
def create_update_script():
    if platform.system() == 'Windows':
        # ایجاد فایل بچ برای ویندوز
        with open('update_script.bat', 'w') as f:
            f.write('@echo off\n')
            f.write('timeout /t 2 /nobreak > nul\n')
            f.write(f'del "{SCRIPT_NAME}"\n')
            f.write(f'ren "{UPDATE_SCRIPT_NAME}" "{SCRIPT_NAME}"\n')
            f.write(f'start "" "{sys.executable}" "{SCRIPT_NAME}"\n')
            f.write('del update_script.bat\n')
    else:
        # ایجاد فایل شل برای لینوکس/مک
        with open('update_script.sh', 'w') as f:
            f.write('#!/bin/bash\n')
            f.write('sleep 2\n')
            f.write(f'rm -f "{SCRIPT_NAME}"\n')
            f.write(f'mv "{UPDATE_SCRIPT_NAME}" "{SCRIPT_NAME}"\n')
            f.write(f'exec "{sys.executable}" "{SCRIPT_NAME}"\n')
            f.write('rm -f update_script.sh\n')
        os.chmod('update_script.sh', 0o755)

# تابع اصلی
def main():
    # ایجاد پوشه دانلودها اگر وجود ندارد
    os.makedirs(DOWNLOADS_DIR, exist_ok=True)
    
    while True:
        clear_console()
        show_logo()
        show_menu()
        
        choice = input(f"\n{Fore.YELLOW}Enter your choice: {Style.RESET_ALL}").strip()
        
        if choice == '1':
            download_repository()
        elif choice == '2':
            show_history()
        elif choice == '3':
            manage_downloads()
        elif choice == '4':
            check_for_updates()
        elif choice == '5':
            announce_menu()
        elif choice == '6':
            print(f"\n{Fore.YELLOW}Goodbye!{Style.RESET_ALL}")
            break
        else:
            print(f"\n{Fore.RED}Invalid choice! Please try again.{Style.RESET_ALL}")
        
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
