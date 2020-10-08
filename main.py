import io
import xml.etree.ElementTree as ElTree
import zipfile
import webbrowser
import re
from urllib.request import urlopen


def download(url):
    try:
        urlopen(url)
    except:
        return
    with urlopen(url) as f:
        inf = f.read()
    return inf


def getPackageURL(name):
    inf = download("https://pypi.org/simple/%s/" %name)
    if inf == None:
        return
    root = ElTree.fromstring(inf)
    package_url = None
    for el in root[1]:
        if el.tag == "a":
            url = el.attrib["href"]
            if ".whl#" in url:
                package_url = url
    return package_url


def getPackageSec(url):
    sec = []
    inf = download(url)
    obj = io.BytesIO(inf)
    zipf = zipfile.ZipFile(obj)
    meta_path = [s for s in zipf.namelist() if "METADATA" in s][0]
    with zipf.open(meta_path) as f:
        meta = f.read().decode("utf-8")
    for line in meta.split("\n"):
        line = line.replace(";", " ").split()
        if not line:
            break
        if line[0] == "Requires-Dist:" and "extra" not in line:
            sec.append(line[1])
        elif line[0] == "Provides-Extra:":
            sec.append(re.sub(r"[^A-Za-z]", "", line[1]))
    return sec


def getPypiGraph(name):
    graph = {}

    def rec(name):
        print(name)
        graph[name] = set()
        url = getPackageURL(name)
        if not url:
            return
        sec = getPackageSec(url)
        for d in sec:
            graph[name].add(d)
            if d not in graph:
                rec(d)
    rec(name)
    return graph


def gv(graph):
    str = "digraph{"
    for v1 in graph:
        for v2 in graph[v1]:
            if not v1 == v2:
                v1 = v1.replace('-', '_').replace('.', ',')
                v2 = v2.replace('-', '_').replace('.', ',')
                str += '%s->%s;' % (v1, v2)
    str += "}"
    return str


def getGraph(name):
    graph = getPypiGraph(name)
    print(gvText(graph))
    digraph = gv(graph)
    if len(graph) > 1:
        url = "https://quickchart.io/graphviz?graph=" +digraph
        webbrowser.open(url, new=2)


def gvText(graph):
    str = ["digraph{"]
    for v1 in graph:
        for v2 in graph[v1]:
            if not v1 == v2:
                v1 = v1.replace('-', '_').replace('.', ',')
                v2 = v2.replace('-', '_').replace('.', ',')
                str.append('%s->%s;' % (v1, v2))
    str.append("}")
    return ("\n").join(str)


getGraph(input())