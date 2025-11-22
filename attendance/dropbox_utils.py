import dropbox
import os
import json
from django.conf import settings
from django.core.cache import cache
import requests

# Dropbox OAuth configuration
DROPBOX_APP_KEY = os.environ.get('DROPBOX_APP_KEY', '9y25xay0giwemdu')
DROPBOX_APP_SECRET = os.environ.get('DROPBOX_APP_SECRET', 'ymiacrqpb6gi7on')
DROPBOX_REFRESH_TOKEN = os.environ.get('DROPBOX_REFRESH_TOKEN', 'bAR0RLQxWBYAAAAAAAAAAWVm6C7yNwkvhWkxzC5CAh8XmeG2xx6ArnJa-d4PyPl1')

# Current access token (will be auto-refreshed)
CURRENT_ACCESS_TOKEN = "sl.u.AGGwuzSo0L6_V0FQyWLKlgMEe72iHR2ZGJ1oSLjnKFtlvoqLL8ippmvzOHVl0QQGM4Zo5FJZVmtdOzacdfuWh013RBr7Elab21nqLtgJQjM_zb7C2rVEGo6t7dmvt1eELnjtUkZY3hHMLWNfTK6NKH3Bw8qCILpaVDspVfR1pMdjly3G3ioeHjHsZNwba7C1YEW8d0pwFFv6v9jfJYHaw0bThLh1UMK6KZhhLgiBsjXasZHu5brPOake-mfbThZmtcHgU57j4v28Z3ypZQcmQOAb2oMOEc083Ca1Z43sFE-V3S8hWMM9lGTPGgveDwJ4dGZ6ZVrYrhqfhVlYqNzix0gGPPg8_gUscLDzryvhV3fe9ZrNMDpUf3QPQyhUyQZXqV2gH_S8d0VAUTeQ0lY5X5qyEl0_nB0yqucFqLtZ6EVb-wBGxXogzhTo2S7O320W0h1S1iAveNFVZ1RJ1aM0awWRJlVYqZncVjtjO3au-FacuBC7LHGi3L4YSZ2JB4CsX5wdkayHiav_SmLheKwYwfoYGxxMGSdya5QsGQvZLWwtSaIHD-Z1jtLX66BMTM34YaHZS2Y_0dlo7-GL3L0oFxykpyk-V3659MR1dfI7RusZYgJOZCxOFeq3JUiOlzLjMlgHON13wMvrn4n2KteFDmBuuqeEVTWP5sgUZv0EwtSVJtHlNoMHlp6GsPdHPM4ttqC5y3Q-xsIu1XsGzs-tVVI_eMVWOjVfi15gs-I2oQ1cFCj2IodpNy08BDy8iCjeOPvweBp9Hznp78XMNRE5_1T-_HGFdFgdbyZtBc-2RaCzSKPCcaBI93Gy0lUWZCaeumvyXylk5T-DBzGdGCmRgLhFpFq1pi4wjD0ix2B1AbasQjnIqxN8xmBDNS_40VJU0bWUuunQ5QMQFl5kaX27GRcXK3IanAT5f1NZ7g9PC3Iuy5ExEVFlMpO2XUN5ermW2xF7tIx7ALQR7-9DHuIIHt9PRcVz13AORMiogcAxEm1gLAx5ntaCVu398T5DwayoZDB8kfVVVblAtwr41ME3EUrgDQ8nTj7N-qzXqiyKl-mYUDH_qipvJwNa50b9SD9cQ7edcJqDFlzFPeXTnkldtkNA3U6cvaGOFELuj99PZnqqaiEI3itoHb07Ajo6frVDpoy02i3ptVgvAAd-W3UZtUeI3AgSNSpWr10peYTJmnCOjQyhYVRAivKTUIm5wYlEcAGnnbjC163v1MqZdznV55mEjy7s-qeTtJWhOTvd7vwYzZOLUcEQ-Afp1ELnBmVxMHSPOpd7whBIyveySB589NHbNDVpskpszHMcFjgiArd_X-HEPceVgneBzN5IGZxW-9NhQZP8rmGu04dJ6HBzDQZkU47X8089mVAhsB_NLtIJAf_YQOBK356Zj0PaVUCUfcQfVUArdchGMLHRdN6ne1CYJ86kz7INIb8-9HTLyLGiRjlbrjTDOJJOD0VGybZc01DocwHdjxiI6_DAF_COepjV"


def generate_new_access_token():
    """Generate new access token when current one expires."""
    try:
        # Try to refresh using refresh token if available
        if DROPBOX_REFRESH_TOKEN and DROPBOX_REFRESH_TOKEN != 'your_refresh_token_here':
            response = requests.post('https://api.dropbox.com/oauth2/token', data={
                'grant_type': 'refresh_token',
                'refresh_token': DROPBOX_REFRESH_TOKEN,
                'client_id': DROPBOX_APP_KEY,
                'client_secret': DROPBOX_APP_SECRET
            })
            
            if response.status_code == 200:
                token_data = response.json()
                new_token = token_data['access_token']
                cache.set('dropbox_access_token', new_token, timeout=14400)  # 4 hours
                print(f"SUCCESS: Generated new access token")
                return new_token
            else:
                print(f"ERROR: Token refresh failed: {response.status_code} - {response.text}")
        
        # Fallback: Use current token and hope it works
        print("WARNING: Using fallback access token")
        return CURRENT_ACCESS_TOKEN
        
    except Exception as e:
        print(f"ERROR: Token generation error: {e}")
        return CURRENT_ACCESS_TOKEN

def get_dropbox_client():
    """Get Dropbox client with auto-refreshed token."""
    # Try cached token first
    token = cache.get('dropbox_access_token')
    
    if not token:
        token = generate_new_access_token()
    
    try:
        dbx = dropbox.Dropbox(token)
        # Test the token by making a simple API call
        dbx.users_get_current_account()
        return dbx
    except (dropbox.exceptions.AuthError, dropbox.exceptions.BadInputError) as e:
        print(f"INFO: Token expired, generating new one: {e}")
        # Token expired or invalid, generate new one
        token = generate_new_access_token()
        return dropbox.Dropbox(token)
    except Exception as e:
        print(f"ERROR: Dropbox client error: {e}")
        # Return client with current token as fallback
        return dropbox.Dropbox(CURRENT_ACCESS_TOKEN)
def get_direct_dropbox_link(shared_url):
    """Convert Dropbox shared link to direct link."""
    if "dropbox.com" in shared_url:
        shared_url = shared_url.replace("?dl=0", "?raw=1")
        shared_url = shared_url.replace("?dl=1", "?raw=1")
        shared_url = shared_url.replace("www.dropbox.com", "dl.dropboxusercontent.com")
    return shared_url

def upload_devotee_photo(photo_file, devotee_data):
    """Upload devotee photo to Dropbox and return direct URL."""
    try:
        dbx = get_dropbox_client()
        
        # Create filename from devotee data: first_last_number
        name_parts = devotee_data['name'].strip().split()
        first_name = name_parts[0].lower() if name_parts else 'unknown'
        last_name = name_parts[-1].lower() if len(name_parts) > 1 else ''
        contact_number = devotee_data.get('contact_number', '0000000000')
        
        file_extension = os.path.splitext(photo_file.name)[1] or '.jpg'
        filename = f"{first_name}_{last_name}_{contact_number}{file_extension}" if last_name else f"{first_name}_{contact_number}{file_extension}"
        dropbox_path = f"/devotee_photos/{filename}"
        
        # print(f"Uploading photo as: {filename}")
        
        # Reset file pointer to beginning
        photo_file.seek(0)
        file_content = photo_file.read()
        
        # Upload file
        upload_result = dbx.files_upload(file_content, dropbox_path, mode=dropbox.files.WriteMode.overwrite)
        # print(f"Upload successful: {upload_result.name}")
        
        # Create shared link
        try:
            link = dbx.sharing_create_shared_link_with_settings(dropbox_path)
        except dropbox.exceptions.ApiError:
            # Link already exists
            links = dbx.sharing_list_shared_links(path=dropbox_path).links
            link = links[0] if links else None
        
        if link:
            direct_url = get_direct_dropbox_link(link.url)
            # print(f"Direct URL: {direct_url}")
            return direct_url
        
        return None
        
    except Exception as e:
        print(f"Dropbox upload error: {e}")
        return None