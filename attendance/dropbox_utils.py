import dropbox
import os
from django.conf import settings

# Dropbox configuration
DROPBOX_ACCESS_TOKEN = "sl.u.AGEaxf_eLensNUIeI0jmZAwysPl8AKrXYHkx_Bo7oPSiyEdTeHC5w38nEza80VSxlOdhHo51yx7bOcMIQ4UMHIz278ALigB217FbmG0r0F_CyxepEN-2mV1t69S6kva5zgaWuWpIVpaogIAKrs3JNpPn9e5FZgefnfgPv0h-jV90POWzCKGVv7Lan89SQZgaTSQE21790CSXcKrQRmRVnuF9pB9osrMRlPwbM7PKcULpeR9_tLqWlTpeBqJjTDwEQRQfv_wpq_xBS-atfRSpKie4Ls5GqekNjdZKVIt4unVuPtYCKMPEHWpAgwjv3yc_CyN9EsH6Y7Ac-6m3gP6wjDuu13A8zgrDoguoecPs3tekTTmLM1jMapmqiyByn2OZ4nEdiL9SXMiG0ttdYzC-s5EdrRRYUCKqWCYf8zaRSNDFm_KK9N_FCz3P0lCRnY94V4RPiShH2cFXmyuVGVZKUrfZM0Yy3JKZ1RjhDmPr93EeAjzF9jg3tgVOA5-Kb2ASB-c0UIE-Fw191yC8Xvq5Y_57ij37LM6HiGN0578ThJndSBKgnrVQaRWbYMcSCwH7jbzNMSR1nwPHE5XVT-smyQZnlR164lCPF-Jvfwm-sZlij694UkdI_z_a0zuv9-gYz45kvMhCOPlV8vZqkjNl7pM_Zl3ap4pTqgPjcQ_Dc39fewnM5jpF1_uKGyKplU67IbOJeJq1IOXKcR5HatR1ErX6CffNML9Ae7WDER4i1YL4sggE8IiQ2rbJ3DR_81KJdF-dEHSMc07XvkCRSURSX6v1kYoNBkg-RIFnp96_jUoyfXoGrwUru6t7RN5IKTFUsn906avripqqW0IxUt4V-FrLN1ODqzyAGE045xueMetvS6JKq5We9LWtU723zmw3ut-bvOo3us3EeOeeZdnPtvxGHcXrOZssF4q2FnELCE66m_-aFK7MoMCkU6BFSAy5oWsJYiO06bdGI3kBDaf3WSuOKuF0cgbEvkbJ95qpaxCjc8whONCZJGQGeiuF-c_F-Yy4rgYQqnhzqZPclfTd8Dq4FakLg7e2NXZMsF4VI6wNU5K39XvV7MdIjrfmsK2TnfEU7gppKfaUsLZXTwugCSmtvJ9ZVdukHufBA4W4xwbfxw8oo0mhVmiL0XuoTmNwBwbYTko4lTX8FMNDYrMAZqIenUURdrYVYB7BfCwYqq7_jXAPY6B_Lkw4sACaPZ7PrT0SwHbH_QnMufGW1YiD1ClQfwqTwEL5MFFsrMNe-CVD--lGah8DKHwrAOkehjLcxnzX2Wrd8fJ5Rf1Iuc6hqR7h"

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
        dbx = dropbox.Dropbox(DROPBOX_ACCESS_TOKEN)
        
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