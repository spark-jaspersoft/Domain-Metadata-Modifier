# Domain-Metadata-Modifier

This project is for commercial users of TIBCO JasperReports Server who wish to make domain changes. A major drawback of using domains is that making changes to a domain that contains dependent repository objects (such as Ad Hoc views, reports and dashboards) would often cause those objects to break. Users would then need to recreate the Ad Hoc views, dashboards, etc. This tool is aimed at two specific use cases:

* Removing one or more existing fields from a domain and its dependent Ad Hoc views, reports and dashboards
* Rename one or more field ids, labels and optionally database columns in the domain definition

It's possible to add fields to an existing domain as long as domain validation is turned off first, therefore adding fields is beyond the scope of this tool. 

The tool is written in Python 3. It calls the REST API to export the entire repository. It downloads the export zip archive to a temporary folder. It extracts the zip archive, iterates over each file looking for matching conditions, and changes the file according to the requested action. It then re-zips the temporary folder and calls the REST API to import the modified archive. Since the REST API requires that the export and import actions require the superuser account, you will need to know the superuser password.

# Usage on Windows

Since Python is not installed on Windows by default, I recommend using Cygwin with Python 3 and PIP installed (64 and 32 bit installers available at http://cygwin.org). This project contains a requirements.txt file that you can use with the pip command to download all of the project dependencies. Once Cygwin has been installed and configured, launch the Cygwin command line window, browse to the folder where the tool is installed. The command line syntax to remove one or more fields from a domain is:

python3 DomainMetadataMod.py \<server-url\> \<superuser-password\> \<domain-id\> \<comma-separated-list-of-field-ids-to-remove\>

If you are renaming one or more field ids and labels, the syntax is:

python3 DomainMetadataMod \<server-url\> \<superuser-password\> \<domain-id\> \<comma-separated-list-of-old-field-ids\> \<comma-separated-list-of-new-field-ids\>

The default behavior also changes the database column names in the domain schema.xml file to match the new field ids. If you wish to keep the database column names the same or change them to something besides the new field ids, add an additional comma separated list parameter at the end:

python3 DomainMetadataMod \<server-url\> \<superuser-password\> \<domain-id\> \<comma-separated-list-of-old-field-ids\> \<comma-separated-list-of-new-field-ids\> <\comma-separated-list-of-new-db-column-names\>

The server-url parameter is the URL you would use to access your JasperReports Server instance from a browser (i.e. http://localhost:8080/jasperserver-pro) without a forward slash on the end. The domain-id parameter is the resource ID for the domain, which you may obtain by right-clicking on the domain in the repository explorer and selecting "Properties". The field ids are available on the display tab of the domain designer. Select a field and use its ID property.

For example, to rename the store_country and product_name fields to country_2 and product_2 respectively from the supermartDomain domain as well as any associated Ad Hoc Views, reports and dashboards from a JasperReports Server instance running on the same machine while preserving the existing database column names, use the following command:

python3 DomainMetadataMod.py http://localhost:8080/jasperserver-pro superuser supermartDomain store_country,product_name country_2, product_2 store_country,product_name

# Usage on Linux or Mac OSX

Mac OSX and most flavors of Linux come with Python pre-installed. Since many come with both Python 2 and 3, you'll need to ensure you're using the correct version. This tool has some dependencies that are available as wheels from PyPI but aren't included in most standard distributions. To get these dependencies, browse to the folder where you downloaded the tool and execute the following in a command line window:

pip3 install -r requirements.txt

Then execute the tool using the following syntax:

To remove one or more fields:

python3 DomainMetadataMod.py \<server-url\> \<superuser-password\> \<domain-id\> \<comma-separated-list-of-field-ids-to-remove\>

To rename one or more field ids and labels in the domain definition:

python3 DomainMetadataMod.py \<server-url\> \<superuser-password\> \<domain-id\> \<comma-separated-list-of-old-field-ids\> \<comma-separated-list-of-new-field-ids\>

To rename one or more field ids and labels in the domain definition and either keep the database column names the same or change them to something other than the new field ids:

python3 DomainMetadataMod.py \<server-url\> \<superuser-password\> \<domain-id\> \<comma-separated-list-of-old-field-ids\> \<comma-separated-list-of-new-field-ids\> \<comma-separated-list-of-db-column-names\>

# Caveats and Cautions

This tool is designed to be aggressive. A common use case for SaaS providers is to have multi-tenancy enabled with separate domains in each tenant. Assuming the domains all have the same domain ids, this tool will remove the same field from all of them in one pass. This tool also accepts partial ID matches. For example, using store_c as the field id will cause both the store_country and store_city fields to be removed.

BE SURE TO EXPORT THE REPOSITORY TO A ZIP ARCHIVE BEFORE USING THIS TOOL!!!

Also, if you have either changed the field labels or are implementing I18N using resource bundles, the field labels will not change. I will probably add support for changing field labels separately from ids in the next release.

Please reach out to me if you have any questions or have additional use cases you would like this tool to support. I'm also hoping to receive feedback on how the tool works for your use case. Thanks for your interest in this tool. I hope it helps make working with domains easier.

Steve Park
email: stpark@tibco.com
