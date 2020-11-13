import csv, os
import xml.etree.ElementTree as ET

default_ns = {'ksj': 'http://nlftp.mlit.go.jp/ksj/schemas/ksj-app', 'jps': 'http://www.gsi.go.jp/GIS/jpgis/standardSchemas'}

# xmlファイルからバス停一覧と位置情報一覧のETオブジェクトを作る。
def load_xml(xml_path = "./xml/P11-10_13/P11-10_13-jgd.xml", ns = default_ns):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    dataset = root.find('dataset')
    ksj_object = dataset.find('ksj:object', ns)
    ksj_AA01 = ksj_object.find('ksj:AA01', ns)
    ksj_OBJ = ksj_AA01.find('ksj:OBJ', ns)
    ksj_ED01_list = ksj_OBJ.findall('ksj:ED01', ns) 
    jps_GM_Point_list = ksj_OBJ.findall('jps:GM_Point', ns)
    return ksj_ED01_list, jps_GM_Point_list

# バス停IDに対応する緯度経度のリストを返却する。
def get_latlng(jps_GM_Point_list, id, ns = default_ns):
    for jps_GM_Point in jps_GM_Point_list:
        if jps_GM_Point.attrib['id'] == id:
            jps_GM_Point_position = jps_GM_Point.find('jps:GM_Point.position', ns)
            jps_DirectPosition = jps_GM_Point_position.find('jps:DirectPosition', ns)
            DirectPosition_coordinate = jps_DirectPosition.find('DirectPosition.coordinate')
            return DirectPosition_coordinate.text.split()

# 路線に属するバス停のリストを返却する
def get_bus_stop_list(ksj_ED01_list, bus_operation_company, bus_line_name, ns = default_ns):
    bus_stop_list = []
    for ksj_ED01 in ksj_ED01_list:
        ksj_POS = ksj_ED01.find('ksj:POS', ns)
        ksj_BSN = ksj_ED01.find('ksj:BSN', ns)
        ksj_BRI_list = ksj_ED01.findall('ksj:BRI', ns)
        for ksj_BRI in ksj_BRI_list:
            ksj_BLN = ksj_BRI.find('ksj:BLN', ns)
            ksj_BOC = ksj_BRI.find('ksj:BOC', ns)
            if ksj_BLN.text == bus_line_name and ksj_BOC.text == bus_operation_company:
                bus_stop_list.append({'name':ksj_BSN.text, 'id': ksj_POS.attrib['idref']})
    return bus_stop_list

# バス事業者と路線の組のリストを返却する。
def get_boc_bln_list(ksj_ED01_list, ns = default_ns):
    bcn_bln_list = []
    for ksj_ED01 in ksj_ED01_list:
        ksj_POS = ksj_ED01.find('ksj:POS', ns)
        ksj_BSN = ksj_ED01.find('ksj:BSN', ns)
        ksj_BRI_list = ksj_ED01.findall('ksj:BRI', ns)
        for ksj_BRI in ksj_BRI_list:
            ksj_BLN = ksj_BRI.find('ksj:BLN', ns)
            ksj_BOC = ksj_BRI.find('ksj:BOC', ns)
            bcn_bln_list.append([ksj_BOC.text, ksj_BLN.text])
    seen = []
    return [x for x in bcn_bln_list if x not in seen and not seen.append(x)]

# CSVを作成する。
def create_csv(ksj_ED01_list, jps_GM_Point_list, bus_operation_company, bus_line_name):
    bus_stop_list = get_bus_stop_list(ksj_ED01_list, bus_operation_company, bus_line_name)
    for bus_stop in bus_stop_list:
        bus_stop['lat'], bus_stop['lng'] = get_latlng(jps_GM_Point_list, bus_stop['id'])
    bus_stops = [[d['id'], d['name'], d['lat'], d['lng']] for d in bus_stop_list]
    if len(bus_stops) > 0:
        bus_operation_company = bus_operation_company.replace("/", "-")
        bus_line_name = bus_line_name.replace("/", "-")
        boc_path = f"./csv/{bus_operation_company}"
        if not os.path.isdir(boc_path):
            os.makedirs(boc_path)
        with open(f'./csv/{bus_operation_company}/{bus_line_name}.csv', 'w') as f:
            writer = csv.writer(f, lineterminator="\n")
            writer.writerows(bus_stops)
        print(f'./csv/{bus_operation_company}/{bus_line_name}.csv')
    else:
        print("エラー")

if __name__ == "__main__":
    # バス停一覧と位置情報一覧のリストを取得
    ksj_ED01_list, jps_GM_Point_list = load_xml()
    # バス事業者と路線のすべての組でCSVを作成する。
    boc_bln_list = get_boc_bln_list(ksj_ED01_list)
    for boc_bln in boc_bln_list:
        print(boc_bln)
        bus_operation_company = boc_bln[0]
        bus_line_name = boc_bln[1]
        create_csv(ksj_ED01_list, jps_GM_Point_list, bus_operation_company, bus_line_name)

