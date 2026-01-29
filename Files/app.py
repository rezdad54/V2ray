import pybase64
import base64
import requests
import binascii
import os
import traceback
from telegram_utils import TelegramBot, analyze_config_stats
from telegram_scraper import scrape_telegram_channels_sync
from mtproto_scraper import scrape_all_mtproto_proxies
from mtproto_telegram_bot import MTProtoTelegramBot, analyze_mtproto_stats

# Define a fixed timeout for HTTP requests
TIMEOUT = 15  # seconds

# Define the fixed text for the initial configuration
fixed_text = """#profile-title: base64:8J+GkyBHaXRodWIgfCBCYXJyeS1mYXIg8J+ltw==
#profile-update-interval: 1
#subscription-userinfo: upload=29; download=12; total=10737418240000000; expire=2546249531
#support-url: https://github.com/rezdad54/V2ray
#profile-web-page-url: https://github.com/rezdad54/V2ray
"""

# Base64 decoding function
def decode_base64(encoded):
    decoded = ""
    for encoding in ["utf-8", "iso-8859-1"]:
        try:
            decoded = pybase64.b64decode(encoded + b"=" * (-len(encoded) % 4)).decode(encoding)
            break
        except (UnicodeDecodeError, binascii.Error):
            pass
    return decoded

# Function to decode base64-encoded links with a timeout
def decode_links(links):
    decoded_data = []
    for link in links:
        try:
            response = requests.get(link, timeout=TIMEOUT)
            encoded_bytes = response.content
            decoded_text = decode_base64(encoded_bytes)
            decoded_data.append(decoded_text)
        except requests.RequestException:
            pass  # If the request fails or times out, skip it
    return decoded_data

# Function to decode directory links with a timeout
def decode_dir_links(dir_links):
    decoded_dir_links = []
    for link in dir_links:
        try:
            response = requests.get(link, timeout=TIMEOUT)
            decoded_text = response.text
            decoded_dir_links.append(decoded_text)
        except requests.RequestException:
            pass  # If the request fails or times out, skip it
    return decoded_dir_links

# Filter function to select lines based on specified protocols and remove duplicates (only for config lines)
def filter_for_protocols(data, protocols):
    filtered_data = []
    seen_configs = set()
    
    # Process each decoded content
    for content in data:
        if content and content.strip():  # Skip empty content
            lines = content.strip().split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('#') or not line:
                    # Always keep comment/metadata/empty lines
                    filtered_data.append(line)
                elif any(protocol in line for protocol in protocols):
                    # Remove anything after "#" at the end of configs
                    if '#' in line:
                        # Split on the last "#" to remove comments
                        parts = line.rsplit('#', 1)
                        line = parts[0].strip()
                    
                    if line not in seen_configs:
                        filtered_data.append(line)
                        seen_configs.add(line)
    return filtered_data

# Function to add tracking information to configs (only if they have "#" at the end)
def add_tracking_info(configs, start_number=1):
    """Add tracking information to each config that already has '#' at the end"""
    tracked_configs = []
    for i, config in enumerate(configs):
        # Skip comment lines
        if config.startswith('#'):
            tracked_configs.append(config)
        else:
            # Only add tracking info if the config already has "#" at the end
            if '#' in config and not config.startswith('#'):
                # Add tracking info: #@V2rayshub: (config number)
                tracked_config = f"{config}#@V2rayshub: {start_number + i}"
                tracked_configs.append(tracked_config)
            else:
                # Keep config as-is if it doesn't have "#" at the end
                tracked_configs.append(config)
    return tracked_configs

# Function to get the next available config number
def get_next_config_number(output_folder):
    """Get the next available config number by reading existing configs"""
    config_number_file = os.path.join(output_folder, ".next_config_number")
    next_number = 1
    
    if os.path.exists(config_number_file):
        try:
            with open(config_number_file, "r") as f:
                next_number = int(f.read().strip())
        except:
            next_number = 1
    
    return next_number

# Function to save the next config number
def save_next_config_number(output_folder, next_number):
    """Save the next config number for future runs"""
    config_number_file = os.path.join(output_folder, ".next_config_number")
    with open(config_number_file, "w") as f:
        f.write(str(next_number))



# Create necessary directories if they don't exist
def ensure_directories_exist():
    output_folder = os.path.join(os.path.dirname(__file__), "..")
    base64_folder = os.path.join(output_folder, "Base64")

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    if not os.path.exists(base64_folder):
        os.makedirs(base64_folder)

    return output_folder, base64_folder

# Main function to process links and write output files
def main():
    telegram_bot = TelegramBot()
    success = False
    error_message = ""
    
    try:
        output_folder, base64_folder = ensure_directories_exist()  # Ensure directories are created

        # Read existing configs FIRST before processing
        print("Reading existing configs...")
        output_filename = os.path.join(output_folder, "All_Configs_Sub.txt")
        main_base64_filename = os.path.join(output_folder, "All_Configs_base64_Sub.txt")
        
        existing_configs = set()
        existing_config_lines = []
        
        if os.path.exists(output_filename):
            with open(output_filename, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # Remove tracking info for comparison
                        clean_line = line
                        if '#@V2rayshub:' in line:
                            clean_line = line.split('#@V2rayshub:')[0].strip()
                        existing_configs.add(clean_line)
                        existing_config_lines.append(line)
            print(f"Found {len(existing_configs)} existing configs")
        else:
            print("No existing config file found, starting fresh")

        print("Starting to fetch and process configs...")
    
        protocols = ["vmess", "vless", "trojan", "ss", "ssr", "hy2", "tuic", "warp://"]
        links = [
            "https://raw.githubusercontent.com/ALIILAPRO/v2rayNG-Config/main/sub.txt",
            "https://raw.githubusercontent.com/mfuu/v2ray/master/v2ray",
            "https://raw.githubusercontent.com/ts-sf/fly/main/v2",
            "https://raw.githubusercontent.com/aiboboxx/v2rayfree/main/v2",
            "https://raw.githubusercontent.com/mahsanet/MahsaFreeConfig/refs/heads/main/app/sub.txt",
            "https://raw.githubusercontent.com/mahsanet/MahsaFreeConfig/refs/heads/main/mtn/sub_1.txt",
            "https://raw.githubusercontent.com/mahsanet/MahsaFreeConfig/refs/heads/main/mtn/sub_2.txt",
            "https://raw.githubusercontent.com/mahsanet/MahsaFreeConfig/refs/heads/main/mtn/sub_3.txt",
            "https://raw.githubusercontent.com/mahsanet/MahsaFreeConfig/refs/heads/main/mtn/sub_4.txt",
            "https://raw.githubusercontent.com/yebekhe/vpn-fail/refs/heads/main/sub-link",
            "https://raw.githubusercontent.com/Surfboardv2ray/TGParse/main/splitted/mixed"
        ]
        dir_links = [
            "https://raw.githubusercontent.com/itsyebekhe/PSG/main/lite/subscriptions/xray/normal/mix",
            "https://raw.githubusercontent.com/HosseinKoofi/GO_V2rayCollector/main/mixed_iran.txt",
            "https://raw.githubusercontent.com/arshiacomplus/v2rayExtractor/refs/heads/main/mix/sub.html",
            "https://raw.githubusercontent.com/IranianCypherpunks/sub/main/config",
            "https://raw.githubusercontent.com/Rayan-Config/C-Sub/refs/heads/main/configs/proxy.txt",
            "https://raw.githubusercontent.com/sashalsk/V2Ray/main/V2Config",
            "https://raw.githubusercontent.com/mahdibland/ShadowsocksAggregator/master/Eternity.txt",
            "https://raw.githubusercontent.com/itsyebekhe/HiN-VPN/main/subscription/normal/mix",
            "https://raw.githubusercontent.com/sarinaesmailzadeh/V2Hub/main/merged",
            "https://raw.githubusercontent.com/freev2rayconfig/V2RAY_SUBSCRIPTION_LINK/main/v2rayconfigs.txt",
            "https://raw.githubusercontent.com/Everyday-VPN/Everyday-VPN/main/subscription/main.txt",
            "https://raw.githubusercontent.com/C4ssif3r/V2ray-sub/main/all.txt",
            "https://raw.githubusercontent.com/MahsaNetConfigTopic/config/refs/heads/main/xray_final.txt",
        ]

        print("Fetching base64 encoded configs...")
        decoded_links = decode_links(links)
        print(f"Decoded {len(decoded_links)} base64 sources")
        
        print("Fetching direct text configs...")
        decoded_dir_links = decode_dir_links(dir_links)
        print(f"Decoded {len(decoded_dir_links)} direct text sources")

        # Scrape configs from Telegram channels
        print("Scraping configs from Telegram channels...")
        telegram_channels = [
            "NetAccount",  # Channel to scrape configs from
            # Add more Telegram channels here
        ]
        
        telegram_configs = scrape_telegram_channels_sync(telegram_channels, limit_per_channel=20)
        telegram_config_lines = []
        
        for config in telegram_configs:
            telegram_config_lines.append(config)
        
        print(f"Scraped {len(telegram_configs)} configs from Telegram channels")

        print("Combining and filtering configs...")
        combined_data = decoded_links + decoded_dir_links + telegram_config_lines
        merged_configs = filter_for_protocols(combined_data, protocols)
        print(f"Found {len(merged_configs)} unique configs after filtering")

        # Identify new configs that aren't in existing files
        new_configs = []
        for config in merged_configs:
            # Skip comment lines
            if config.startswith('#'):
                continue
            # Remove tracking info for comparison
            clean_config = config
            if '#@V2rayshub:' in config:
                clean_config = config.split('#@V2rayshub:')[0].strip()
            
            if clean_config not in existing_configs:
                new_configs.append(config)
        
        print(f"Found {len(new_configs)} new configs out of {len(merged_configs)} total configs")

        # Write configs to output file (preserve existing + add new)
        print("Writing main config file...")
        output_filename = os.path.join(output_folder, "All_Configs_Sub.txt")
        
        # Get the next config number for tracking
        next_config_number = get_next_config_number(output_folder)
        
        # Add tracking info to new configs
        tracked_new_configs = add_tracking_info(new_configs, next_config_number)
        
        # Save the updated config number
        save_next_config_number(output_folder, next_config_number + len(new_configs))
        
        # Write all configs (existing + new with tracking)
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(fixed_text)
            
            # Write existing configs first (preserve their order and tracking)
            for line in existing_config_lines:
                f.write(line + "\n")
            
            # Write new configs with tracking
            for config in tracked_new_configs:
                f.write(config + "\n")
        
        print(f"Main config file updated: {output_filename}")

        # Create base64 version of the main file
        print("Creating base64 version...")
        with open(output_filename, "r", encoding="utf-8") as f:
            main_config_data = f.read()
        
        main_base64_filename = os.path.join(output_folder, "All_Configs_base64_Sub.txt")
        with open(main_base64_filename, "w", encoding="utf-8") as f:
            encoded_main_config = base64.b64encode(main_config_data.encode()).decode()
            f.write(encoded_main_config)
        print(f"Base64 config file created: {main_base64_filename}")

        # Split merged configs into smaller files (no more than 500 configs per file)
        print("Creating split files...")
        with open(output_filename, "r", encoding="utf-8") as f:
            lines = f.readlines()

        num_lines = len(lines)
        max_lines_per_file = 500
        num_files = (num_lines + max_lines_per_file - 1) // max_lines_per_file
        print(f"Splitting into {num_files} files with max {max_lines_per_file} lines each")

        for i in range(num_files):
            profile_title = f"🆓 Git:rezdad54 | Sub{i+1} 🔥"
            encoded_title = base64.b64encode(profile_title.encode()).decode()
            custom_fixed_text = f"""#profile-title: base64:{encoded_title}
#profile-update-interval: 1
#subscription-userinfo: upload=29; download=12; total=10737418240000000; expire=2546249531
#support-url: https://github.com/rezdad54/V2ray
#profile-web-page-url: https://github.com/rezdad54/V2ray
"""

            input_filename = os.path.join(output_folder, f"Sub{i + 1}.txt")
            with open(input_filename, "w", encoding="utf-8") as f:
                f.write(custom_fixed_text)
                start_index = i * max_lines_per_file
                end_index = min((i + 1) * max_lines_per_file, num_lines)
                for line in lines[start_index:end_index]:
                    f.write(line)
            print(f"Created: Sub{i + 1}.txt")

            with open(input_filename, "r", encoding="utf-8") as input_file:
                config_data = input_file.read()
            
            base64_output_filename = os.path.join(base64_folder, f"Sub{i + 1}_base64.txt")
            with open(base64_output_filename, "w", encoding="utf-8") as output_file:
                encoded_config = base64.b64encode(config_data.encode()).decode()
                output_file.write(encoded_config)
            print(f"Created: Sub{i + 1}_base64.txt")

        print(f"\nProcess completed successfully!")
        print(f"Total configs processed: {len(merged_configs)}")
        print(f"Files created:")
        print(f"  - All_Configs_Sub.txt")
        print(f"  - All_Configs_base64_Sub.txt") 
        print(f"  - {num_files} split files (Sub1.txt to Sub{num_files}.txt)")
        print(f"  - {num_files} base64 split files (Sub1_base64.txt to Sub{num_files}_base64.txt)")
        
        # Check if there are new configs by comparing with previous run
        previous_config_count = 0
        config_count_file = os.path.join(output_folder, ".previous_config_count")
        previous_configs_file = os.path.join(output_folder, ".previous_configs.txt")
        
        # Read previous config count and configs if exists
        previous_configs = set()
        if os.path.exists(config_count_file):
            try:
                with open(config_count_file, "r") as f:
                    previous_config_count = int(f.read().strip())
            except:
                previous_config_count = 0
        
        if os.path.exists(previous_configs_file):
            try:
                with open(previous_configs_file, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            # Remove tracking info for comparison
                            if '#@V2rayshub:' in line:
                                line = line.split('#@V2rayshub:')[0].strip()
                            previous_configs.add(line)
            except:
                previous_configs = set()
        
        current_config_count = len(merged_configs)
        
        # Only send Telegram message if there are new configs or significant change
        if current_config_count > previous_config_count or abs(current_config_count - previous_config_count) > 1:
            # Post individual configs to Telegram
            print("Posting individual configs to Telegram...")
            
            # Extract config lines (non-comment lines) and filter for new ones
            config_lines = []
            new_configs = []
            with open(output_filename, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # Remove tracking info for comparison
                        clean_line = line
                        if '#@V2rayshub:' in line:
                            clean_line = line.split('#@V2rayshub:')[0].strip()
                        
                        if clean_line not in previous_configs:
                            new_configs.append(line)
                        config_lines.append(line)
            
            print(f"Found {len(new_configs)} new configs out of {len(config_lines)} total configs")
            
            if new_configs:
                # Get next config number for unique numbering across runs
                next_config_number = get_next_config_number(output_folder)
                
                # Add tracking information to new configs with unique numbering
                tracked_configs = add_tracking_info(new_configs, next_config_number)
                
                # Post only new configs
                telegram_bot.post_individual_configs(tracked_configs)
                
                # Save the next config number for future runs
                save_next_config_number(output_folder, next_config_number + len(new_configs))
            else:
                print("No new configs to post")
            
            # Also post a summary message
            print("Analyzing config statistics...")
            stats = analyze_config_stats(output_filename)
            print(f"Config analysis: {stats}")
            
            print("Posting summary to Telegram...")
            telegram_bot.post_success_update(stats)
            
            # Save current config count and configs for next comparison
            with open(config_count_file, "w") as f:
                f.write(str(current_config_count))
            
            with open(previous_configs_file, "w", encoding="utf-8") as f:
                for config in config_lines:
                    f.write(config + "\n")
            
            print(f"Saved config count: {current_config_count}")
        else:
            print(f"No significant config changes detected. Current: {current_config_count}, Previous: {previous_config_count}")
            print("Skipping Telegram notification.")
        
        # Process MTProto proxies
        print("\n🔄 Starting MTProto proxy processing...")
        mtproto_bot = MTProtoTelegramBot()
        
        try:
            # Scrape MTProto proxies
            mtproto_results = scrape_all_mtproto_proxies(output_folder)
            
            # Check if there are new MTProto proxies by comparing with previous run
            mtproto_previous_count = 0
            mtproto_count_file = os.path.join(output_folder, ".previous_mtproto_count")
            mtproto_previous_proxies_file = os.path.join(output_folder, ".previous_mtproto_proxies.txt")
            
            # Read previous MTProto proxy count and proxies if exists
            mtproto_previous_proxies = set()
            if os.path.exists(mtproto_count_file):
                try:
                    with open(mtproto_count_file, "r") as f:
                        mtproto_previous_count = int(f.read().strip())
                except:
                    mtproto_previous_count = 0
            
            if os.path.exists(mtproto_previous_proxies_file):
                try:
                    with open(mtproto_previous_proxies_file, "r", encoding="utf-8") as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith('#'):
                                mtproto_previous_proxies.add(line)
                except:
                    mtproto_previous_proxies = set()
            
            mtproto_current_count = mtproto_results["total_proxies"]
            
            # Only send MTProto Telegram message if there are new proxies or significant change
            if mtproto_current_count > mtproto_previous_count or abs(mtproto_current_count - mtproto_previous_count) > 1:
                print("Posting MTProto proxies to Telegram...")
                
                # Filter for new MTProto proxies
                new_mtproto_proxies = []
                for proxy in mtproto_results["proxies"]:
                    if proxy not in mtproto_previous_proxies:
                        new_mtproto_proxies.append(proxy)
                
                print(f"Found {len(new_mtproto_proxies)} new MTProto proxies out of {mtproto_current_count} total proxies")
                
                if new_mtproto_proxies:
                    # Post new MTProto proxies
                    mtproto_bot.post_individual_proxies(new_mtproto_proxies)
                else:
                    print("No new MTProto proxies to post")
                
                # Also post a summary message
                print("Analyzing MTProto statistics...")
                mtproto_stats = analyze_mtproto_stats(mtproto_results["output_file"])
                print(f"MTProto analysis: {mtproto_stats}")
                
                print("Posting MTProto summary to Telegram...")
                mtproto_bot.post_success_update(mtproto_stats)
                
                # Save current MTProto proxy count and proxies for next comparison
                with open(mtproto_count_file, "w") as f:
                    f.write(str(mtproto_current_count))
                
                with open(mtproto_previous_proxies_file, "w", encoding="utf-8") as f:
                    for proxy in mtproto_results["proxies"]:
                        f.write(proxy + "\n")
                
                print(f"Saved MTProto proxy count: {mtproto_current_count}")
            else:
                print(f"No significant MTProto proxy changes detected. Current: {mtproto_current_count}, Previous: {mtproto_previous_count}")
                print("Skipping MTProto Telegram notification.")
        
        except Exception as e:
            print(f"❌ MTProto processing error: {e}")
            mtproto_bot.post_error_update(str(e))
        
        success = True
        
    except Exception as e:
        error_message = f"{str(e)}\n\n{traceback.format_exc()}"
        print(f"❌ Error occurred: {error_message}")
        
        # Post error message to Telegram
        print("Posting error to Telegram...")
        telegram_bot.post_error_update(str(e))
        
    finally:
        if success:
            print("✅ Process completed successfully with Telegram notification")
        else:
            print("❌ Process failed with Telegram error notification")

if __name__ == "__main__":
    main()
