from setuptools import find_packages, setup

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="plone_cookiesregtech",
    version="1.0.0",
    description="CookiesRegTech cookie consent for Plone: one-click connect, automatic banner injection, cookie scanner and consent log.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: Addon",
        "Framework :: Plone :: 6.0",
        "Framework :: Plone :: 6.1",
        "Framework :: Plone :: 6.2",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
    ],
    keywords="Plone cookie consent GDPR CCPA banner Google Consent Mode",
    author="CookiesRegTech",
    url="https://www.cookiesregtech.com",
    project_urls={
        "Homepage": "https://www.cookiesregtech.com",
        "Privacy Policy": "https://www.cookiesregtech.com/privacy-policy",
    },
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.10",
    install_requires=[
        "Products.CMFPlone>=6.0",
        "plone.api",
    ],
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
