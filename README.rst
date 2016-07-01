===============
metricsandstuff
===============

Setting up a Dev Environment
============================
1. Clone deploymetrics:
""
    > git clone http://github.com/bucknerns/deploymetrics
    
2. Configure cloudfile in api_config.ini (optional for attachment support)
::
    > [auth]
    url=https://identity.api.rackspacecloud.com/v2.0
    username=<username>
    apikey=<api key>
    
    [files]
    url=<files endpoint> example: https://storage101.dfw1.clouddrive.com/v1/MossoCloudFS_<accountnum>
    temp_url_key=<tempurl key(just a random string)>
    prefix=<container prefix>
    
3. As root run install_all.sh
::
    > ./install_all.sh
    
Note: File attachment will still not work if the temp_url_key hasn't been set on the account and the containers have not been created.  Use files client to do this.(only do this once per container prefix, sharing the same account for different deployments can be done with different prefixes but the temp_url_key has to be the same)
::
    > In [1]: from myapp.files.client import FilesClient
    In [2]: from myapp.auth.client import AuthClient
    In [3]: ac = AuthClient("https://identity.api.rackspacecloud.com/v2.0", "<username>", "<apikey>")
    In [4]: c = FilesClient("https://storage101.dfw1.clouddrive.com/v1/MossoCloudFS_<accountnum>", ac, temp_url_key="<tempurl key>", container_prefix="<container prefix>")
    In [5]: c.init_files_account()
