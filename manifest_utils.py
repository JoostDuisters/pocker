import requests

REGISTRYBASE = 'https://registry-1.docker.io'
AUTHBASE = 'https://auth.docker.io'
AUTHSERVICE = 'registry.docker.io'
MANIFEST_ACCEPTS = ','.join(['application/vnd.docker.distribution.manifest.v2+json',
                             'application/vnd.docker.distribution.manifest.list.v2+json',
                             'application/vnd.docker.distribution.manifest.v1+json'])


class DockerRegistry:

    def __init__(self, image):
        self._image = 'library/' + image if not '/' in image else image

    def _get_token(self):
        token_url = f"{AUTHBASE}/token?service={AUTHSERVICE}&scope=repository:{self._image}:pull"
        data = requests.get(url=token_url)
        return data.json()['token']

    def get_manifest_json(self, tag):
        manifest_url = f"{REGISTRYBASE}/v2/{self._image}/manifests/{tag}"
        manifest_headers = {
            'Authorization': f'Bearer {self._get_token()}',
            'Accept': MANIFEST_ACCEPTS
        }
        data = requests.get(url=manifest_url, headers=manifest_headers)
        return data.json()

    def fetch_blob(self, tag, destination):
        blob_url = f"{REGISTRYBASE}/v2/{self._image}/blobs/{tag}"
        blob_headers = {'Authorization': f'Bearer {self._get_token()}'}
        data = requests.get(url=blob_url, headers=blob_headers)
        open(destination, 'wb').write(data.content)

