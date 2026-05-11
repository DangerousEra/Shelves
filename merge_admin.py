import os
import re

def get_body_content(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract everything inside <main class="main-content"> ... </main>
    main_match = re.search(r'<main class="main-content">(.*?)</main>', content, re.DOTALL)
    if not main_match:
        return ""
    main_content = main_match.group(1)
    
    # Remove top-bar because the SPA admin.html already has one dynamic top bar
    main_content = re.sub(r'<!-- ── TOP BAR ── -->\s*<div class="top-bar">.*?</div>', '', main_content, flags=re.DOTALL)
    return main_content.strip()

base_dir = r"f:\Shelves\Shelves"
admin_files = {
    'analytics': 'admin-analytics.html',
    'recurring': 'admin-recurring.html',
    'donors': 'admin-donors.html',
    'approved': 'admin-approved.html',
    'customers': 'admin-customers.html',
    'contacts': 'admin-contacts.html',
    'logs': 'admin-logs.html'
}

with open(os.path.join(base_dir, 'admin.html'), 'r', encoding='utf-8') as f:
    admin_spa = f.read()

# We will inject the new sections right before <!-- ── MODALS ── -->
new_sections = []
for section_id, filename in admin_files.items():
    filepath = os.path.join(base_dir, filename)
    if os.path.exists(filepath):
        content = get_body_content(filepath)
        section_html = f'\n    <section id="{section_id}-section" class="content-section" style="display: none;">\n      {content}\n    </section>\n'
        new_sections.append(section_html)

# Add all new sections
all_new_sections = "".join(new_sections)

# Insert the sections before closing </main>
admin_spa = admin_spa.replace('</main>', all_new_sections + '\n  </main>')

# Now we need to create the admin directory
admin_dir = os.path.join(base_dir, 'admin')
if not os.path.exists(admin_dir):
    os.makedirs(admin_dir)

# Update links inside the new admin/index.html
# The new admin/index.html needs to point href="favicon.png" to href="../favicon.png"
admin_spa = admin_spa.replace('href="favicon.png"', 'href="../favicon.png"')
admin_spa = admin_spa.replace('href="index.html"', 'href="../index.html"')
admin_spa = admin_spa.replace('href="admin-dashboard.html"', 'href="#dashboard"')

# Also fix the JS navigation to handle titles for all sections
titles_js = """    const titles = {
      dashboard: 'Dashboard Overview',
      analytics: 'Analytics Dashboard',
      donations: 'Donations Management',
      recurring: 'Recurring Donations',
      donors: 'Donors List',
      sellers: 'Seller Applications',
      approved: 'Approved Sellers',
      customers: 'Customers',
      contacts: 'Contact Messages',
      settings: 'Admin Settings',
      logs: 'System Logs'
    };"""

admin_spa = re.sub(r'const titles = \{.*?\};', titles_js, admin_spa, flags=re.DOTALL)

with open(os.path.join(admin_dir, 'index.html'), 'w', encoding='utf-8') as f:
    f.write(admin_spa)

print("Created admin/index.html successfully!")
