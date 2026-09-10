"""Convert explicit sampled SVG contours to cutting/plotting paths, running stitches and STL."""
import argparse
import json
import math
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
from shapely.geometry import Polygon, LineString
from shapely.geometry.polygon import orient
from shapely import constrained_delaunay_triangles

NS = 'http://www.w3.org/2000/svg'
ET.register_namespace('', NS)


def svg_paths(paths, width, height, title, color):
    root = ET.Element(f'{{{NS}}}svg', {'width':f'{width:g}mm','height':f'{height:g}mm','viewBox':f'0 0 {width:g} {height:g}'})
    ET.SubElement(root, f'{{{NS}}}title').text = title
    group = ET.SubElement(root, f'{{{NS}}}g', {'id':'tool-paths','fill':'none','stroke':color,'stroke-width':'0.15'})
    for path in paths:
        points = path['points']
        d = 'M'+' L'.join(f'{x:.5f},{y:.5f}' for x,y in points)
        if path['closed']:
            d += ' Z'
        ET.SubElement(group, f'{{{NS}}}path', {'id':path['id'],'d':d})
    return ET.tostring(root, encoding='utf-8', xml_declaration=True)


def extrude(points, thickness):
    polygon = orient(Polygon(points), sign=1)
    if not polygon.is_valid or polygon.area <= 0:
        raise ValueError('STL requires a valid simple closed contour')
    faces=[]
    for triangle in constrained_delaunay_triangles(polygon).geoms:
        xy=list(orient(triangle,sign=1).exterior.coords)[:3]
        faces.append([(x,y,thickness) for x,y in xy])
        faces.append([(x,y,0) for x,y in reversed(xy)])
    ring=list(polygon.exterior.coords)
    for a,b in zip(ring,ring[1:]):
        faces.append([(*a,0),(*b,0),(*b,thickness)])
        faces.append([(*a,0),(*b,thickness),(*a,thickness)])
    edges=Counter(tuple(sorted((tuple(a),tuple(b)))) for f in faces for a,b in zip(f,f[1:]+f[:1]))
    if not edges or any(count!=2 for count in edges.values()):
        raise ValueError('STL mesh must have exactly two faces per edge')
    volume=sum(a[0]*(b[1]*c[2]-b[2]*c[1])-a[1]*(b[0]*c[2]-b[2]*c[0])+a[2]*(b[0]*c[1]-b[1]*c[0]) for a,b,c in faces)/6
    if not math.isclose(volume,polygon.area*thickness,rel_tol=1e-6):
        raise ValueError('STL volume differs from profile area × thickness')
    lines=['solid svg_profile']
    for a,b,c in faces:
        u=[b[i]-a[i] for i in range(3)];v=[c[i]-a[i] for i in range(3)]
        normal=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
        length=math.hypot(*normal)
        if length==0:raise ValueError('Degenerate STL triangle')
        lines.append('facet normal '+' '.join(f'{x/length:.12g}' for x in normal))
        lines.append('outer loop')
        lines.extend('vertex '+' '.join(f'{x:.12g}' for x in vertex) for vertex in [a,b,c])
        lines.extend(['endloop','endfacet'])
    lines.append('endsolid svg_profile')
    return '\n'.join(lines), {'triangles':len(faces),'closed_mesh':True,'volume_mm3':volume,'thickness_mm':thickness}


def fabricate(geometry, output, *, thickness=2, solid_id=None, embroidery=False, stitch_mm=2, hoop_mm=100):
    data=json.loads(Path(geometry).read_text(encoding='utf-8'))
    width,height=data['width_mm'],data['height_mm'];paths=data['paths']
    if not all(isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v) and v>0 for v in [width,height,thickness,stitch_mm,hoop_mm]):
        raise ValueError('Dimensions must be positive finite numbers')
    if not paths:raise ValueError('Select at least one geometry path')
    ids=set()
    for path in paths:
        if not isinstance(path['id'],str) or path['id'] in ids:raise ValueError('Unique path IDs required')
        ids.add(path['id'])
        points=path['points']
        if len(points)<2 or any(len(p)!=2 or not all(isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v) for v in p) for p in points):
            raise ValueError('Provide finite point pairs')
        if any(x<-.001 or x>width+.001 or y<-.001 or y>height+.001 for x,y in points):
            raise ValueError('Geometry exceeds declared design dimensions')
        if path['closed'] and (points[0]!=points[-1] or not Polygon(points).is_valid or Polygon(points).area<=0):
            raise ValueError('Closed paths need simple, nonzero contours with coincident endpoints')
    cut=[p for p in paths if p['closed']]
    # Drawing strokes are selected centerlines; filled silhouettes remain outlines.
    files={'plot.svg':svg_paths(paths,width,height,'Plotting centerlines · design units mm','#244c39')}
    if cut:files['cut.svg']=svg_paths(cut,width,height,'Nominal cutting contours · kerf compensation in CAM','#ff0000')
    report={'width_mm':width,'height_mm':height,'cut_contours':len(cut),'plot_paths':len(paths),'kerf_compensation_mm':0,'machine_tested':False}
    if solid_id:
        selected=next((p for p in cut if p['id']==solid_id),None)
        if not selected:raise ValueError('solid_id must select one closed contour')
        mesh,report['stl']=extrude(selected['points'],thickness);files['profile.stl']=mesh.encode()
    pattern=None
    if embroidery:
        from pyembroidery import EmbPattern
        if max(width,height)>hoop_mm or stitch_mm<.5 or stitch_mm>5:
            raise ValueError('Use stitch length .5–5 mm and a hoop containing the full design')
        pattern=EmbPattern();pattern.add_thread('#365f43');stitch_paths=[];count=0
        for path in paths:
            line=LineString(path['points']);n=max(1,math.ceil(line.length/stitch_mm))
            points=[list(line.interpolate(i/n*line.length).coords)[0] for i in range(n+1)]
            x,y=points[0];pattern.move_abs((x-width/2)*10,(y-height/2)*10)
            for x,y in points:pattern.stitch_abs((x-width/2)*10,(y-height/2)*10)
            pattern.trim();count+=len(points);stitch_paths.append({**path,'points':points})
        pattern.end()
        files['stitches.svg']=svg_paths(stitch_paths,width,height,'Running stitch plan · one thread color','#365f43')
        report['embroidery']={'type':'single-color running stitch','planned_stitches':count,'max_stitch_mm':stitch_mm,'hoop_mm':hoop_mm,'fabric_tested':False}
    output=Path(output);output.mkdir()
    for name,content in files.items():(output/name).write_bytes(content)
    if pattern:
        from pyembroidery import EmbPattern
        EmbPattern.write_dst(pattern,str(output/'running-stitch.dst'))
        EmbPattern.write_pes(pattern,str(output/'running-stitch.pes'))
        for ext,reader in [('dst',EmbPattern.read_dst),('pes',EmbPattern.read_pes)]:
            loaded=reader(str(output/f'running-stitch.{ext}'))
            if not loaded.stitches:raise ValueError('Embroidery read-back is empty')
            report['embroidery'][ext+'_commands']=len(loaded.stitches)
    (output/'fabrication.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('geometry');parser.add_argument('output')
    parser.add_argument('--solid-id');parser.add_argument('--thickness',type=float,default=2)
    parser.add_argument('--embroidery',action='store_true');parser.add_argument('--stitch-mm',type=float,default=2);parser.add_argument('--hoop-mm',type=float,default=100)
    args=parser.parse_args()
    try:
        print(json.dumps(fabricate(args.geometry,args.output,thickness=args.thickness,solid_id=args.solid_id,embroidery=args.embroidery,stitch_mm=args.stitch_mm,hoop_mm=args.hoop_mm),ensure_ascii=False,indent=2))
    except (ValueError,OSError,KeyError,TypeError,ImportError) as error:parser.exit(1,f'Fabrication failed: {error}\n')
