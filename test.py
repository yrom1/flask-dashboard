project_names = [
    'cloud-dictionary',
    'mypandas',
    'ty',
    'exception-logging',
    'postgrespy',
]
projects = {
    name: {
        'readme': f"https://raw.githubusercontent.com/yrom1/{name}/main/README.md",
        'tagline': name,
    }
 for name in project_names}
